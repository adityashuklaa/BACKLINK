"""Safety / anti-detection module.

Centralizes velocity gates, pattern detection, jitter, and audit logging
so every publishing script has a uniform safety net.

The whole point: prevent the 8-orgs-90-repos-in-one-day pattern that
risks Codeberg flagging us, the 37-Dev.to-articles-in-one-day pattern
that risks shadowban, and the cross-platform burst pattern that risks
loss of an entire campaign.

Usage:
    from core.safety import (
        velocity_gate,           # decision gate before publish
        log_publish,             # record after successful publish
        jitter_sleep,            # randomized inter-publish delay
        content_similarity_check, # detect template-spam pattern
        velocity_status,          # inspect current 24h state
        DAILY_CAPS,
    )
"""
from __future__ import annotations

import json
import os
import random
import re
import time
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# ============================================================
# CAPS — per-platform daily / weekly / 7-day-window limits
# ============================================================
# Tuned from real-world ban thresholds + our own incident history (74-article
# Hashnode deletion). Values reflect the upper-safe pace per platform.
DAILY_CAPS = {
    # Platform: (per-24h, per-week, per-30d-rolling)
    # If any window is exceeded, gate refuses publish.
    "dev.to":              (5,   25,  80),
    "hashnode.dev":        (1,    4,  15),  # tightest cap — 74-article incident
    "codeberg.org":        (5,   30, 100),  # repos
    "codeberg-orgs":       (1,    3,   8),  # org creation specifically
    "codeberg.page":       (1,    3,   8),  # Pages subdomains
    "gitlab.com":          (3,   18,  60),
    "github.com":          (3,   18,  60),
    "tumblr.com":          (1,    5,  15),
    "medium.com":          (1,    5,  15),
    "substack.com":        (1,    5,  15),
    "indiehackers.com":    (1,    3,   8),
    "stackoverflow.com":   (3,   12,  35),  # answers; profile is one-shot
    "quora.com":           (3,   12,  35),
    "diigo.com":           (5,   25,  60),  # bookmarks
    "spiceworks.com":      (2,    8,  20),
    "default":             (2,    8,  25),
}


# ============================================================
# VELOCITY LOG — JSON-file tracker of every publish
# ============================================================
LOG_PATH = Path("output/daily_publish_velocity.json")


def _load_log() -> List[Dict]:
    if not LOG_PATH.exists():
        return []
    try:
        with open(LOG_PATH, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def _save_log(entries: List[Dict]) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2, default=str)


def log_publish(platform: str, url: str, content_excerpt: str = "", strategy: str = "") -> None:
    """Record a successful publish. Call AFTER the publish succeeds."""
    entries = _load_log()
    entries.append({
        "ts": datetime.now().isoformat(),
        "platform": _normalize_platform(platform),
        "url": url,
        "strategy": strategy,
        "content_excerpt": content_excerpt[:200],  # for similarity checks later
    })
    # Keep last 60 days only — auto-prune
    cutoff = datetime.now() - timedelta(days=60)
    entries = [e for e in entries if datetime.fromisoformat(e["ts"]) >= cutoff]
    _save_log(entries)


# ============================================================
# VELOCITY GATE — decision before publish
# ============================================================
@dataclass
class VelocityResult:
    ok: bool
    reason: str
    counts_24h: int = 0
    counts_7d: int = 0
    counts_30d: int = 0
    next_allowed_at: Optional[str] = None


def _normalize_platform(p: str) -> str:
    """Map various platform identifiers to our cap keys."""
    p = p.lower().strip().replace("https://", "").replace("http://", "")
    # strip path
    p = p.split("/")[0]
    p = p.replace("www.", "")
    if "hashnode" in p:
        return "hashnode.dev"
    if p.endswith(".codeberg.page"):
        return "codeberg.page"
    return p


def velocity_gate(platform: str, special_kind: Optional[str] = None) -> VelocityResult:
    """Decision gate: can we publish to this platform RIGHT NOW?

    `special_kind` lets you specify a sub-category like "codeberg-orgs"
    when creating an org (vs a regular repo).
    """
    cap_key = special_kind if special_kind else _normalize_platform(platform)
    caps = DAILY_CAPS.get(cap_key, DAILY_CAPS["default"])
    cap_24h, cap_7d, cap_30d = caps

    entries = _load_log()
    now = datetime.now()
    cutoff_24h = now - timedelta(hours=24)
    cutoff_7d = now - timedelta(days=7)
    cutoff_30d = now - timedelta(days=30)

    target_platform = cap_key if special_kind else _normalize_platform(platform)
    # When checking codeberg-orgs, only count entries with strategy hinting orgs
    if special_kind == "codeberg-orgs":
        relevant = [e for e in entries if "org" in e.get("strategy", "").lower() and "codeberg" in e.get("platform", "").lower()]
    elif special_kind == "codeberg.page":
        relevant = [e for e in entries if "pages" in e.get("strategy", "").lower() or e.get("platform", "").endswith(".codeberg.page")]
    else:
        relevant = [e for e in entries if e.get("platform") == target_platform]

    c24 = sum(1 for e in relevant if datetime.fromisoformat(e["ts"]) >= cutoff_24h)
    c7d = sum(1 for e in relevant if datetime.fromisoformat(e["ts"]) >= cutoff_7d)
    c30d = sum(1 for e in relevant if datetime.fromisoformat(e["ts"]) >= cutoff_30d)

    # Hard caps
    if c24 >= cap_24h:
        oldest_in_24h = min((datetime.fromisoformat(e["ts"]) for e in relevant
                             if datetime.fromisoformat(e["ts"]) >= cutoff_24h), default=now)
        next_allowed = (oldest_in_24h + timedelta(hours=24)).isoformat()
        return VelocityResult(False, f"velocity: {target_platform} {cap_key} hit 24h cap ({c24}/{cap_24h}). Next allowed at {next_allowed}",
                              c24, c7d, c30d, next_allowed)
    if c7d >= cap_7d:
        return VelocityResult(False, f"velocity: {target_platform} hit 7d cap ({c7d}/{cap_7d})",
                              c24, c7d, c30d)
    if c30d >= cap_30d:
        return VelocityResult(False, f"velocity: {target_platform} hit 30d cap ({c30d}/{cap_30d})",
                              c24, c7d, c30d)

    return VelocityResult(True, f"velocity OK: {target_platform} 24h={c24}/{cap_24h} 7d={c7d}/{cap_7d} 30d={c30d}/{cap_30d}",
                          c24, c7d, c30d)


# ============================================================
# CONTENT SIMILARITY — detect template-spam pattern
# ============================================================
def _word_set(text: str) -> set:
    return set(re.findall(r"\w{4,}", text.lower()))


def content_similarity_check(content: str, platform: str, threshold: float = 0.55) -> Tuple[bool, float, str]:
    """Block publish if similar content was published recently on the platform.

    Returns (ok, max_similarity, message).

    Uses Jaccard on 4+ char words. Threshold 0.55 = 55% word overlap.
    Anything above that is template-spam pattern.
    """
    entries = _load_log()
    target = _normalize_platform(platform)
    cutoff = datetime.now() - timedelta(days=14)

    fresh = _word_set(content[:4000])  # first 4k chars
    max_sim = 0.0
    closest_url = ""
    for e in entries:
        if e.get("platform") != target:
            continue
        if datetime.fromisoformat(e["ts"]) < cutoff:
            continue
        existing = _word_set(e.get("content_excerpt", ""))
        if not existing or not fresh:
            continue
        union = fresh | existing
        if not union:
            continue
        sim = len(fresh & existing) / len(union)
        if sim > max_sim:
            max_sim = sim
            closest_url = e.get("url", "")

    if max_sim >= threshold:
        return False, max_sim, f"content_similarity: {max_sim:.2f} overlap with recent {target} post {closest_url[:80]}"
    return True, max_sim, f"content_similarity OK ({max_sim:.2f} max)"


# ============================================================
# JITTER — randomized delays, not robot-clean intervals
# ============================================================
def jitter_sleep(base_seconds: int, variance_pct: float = 0.4) -> float:
    """Sleep for base±variance%. Returns actual sleep duration.

    Why: humans don't post on a 35.0s metronome. Random delays look
    natural to rate limiters watching for bot patterns.
    """
    spread = base_seconds * variance_pct
    actual = base_seconds + random.uniform(-spread, spread)
    actual = max(5, actual)  # never less than 5s
    time.sleep(actual)
    return actual


# ============================================================
# ACCOUNT AGE GATE — prevent posting from fresh accounts
# ============================================================
def account_age_gate(account_created_iso: str, min_days: int = 7) -> Tuple[bool, str]:
    """Returns (ok, reason). Block posting from accounts younger than min_days."""
    try:
        created = datetime.fromisoformat(account_created_iso)
    except Exception:
        return False, f"account_age_gate: invalid date {account_created_iso}"
    age_days = (datetime.now() - created).days
    if age_days < min_days:
        return False, f"account_age_gate: account is {age_days}d old, need {min_days}d minimum"
    return True, f"account_age OK: {age_days}d old"


# ============================================================
# DESTINATION-URL ROTATION — don't always link the same URL
# ============================================================
DESTINATION_URLS = [
    "https://dialphone.com",
    "https://dialphone.com/pricing-overview/",
    "https://dialphonelimited.codeberg.page/calculator/",
    "https://dialphonelimited.codeberg.page/calculator/#methodology",
]


def rotate_destination(idx: int) -> str:
    """Pick a destination URL based on index — rotates through 4 URLs.

    Distribution we want over a batch of N publishes:
    - 50% to dialphone.com homepage
    - 20% to /pricing-overview/
    - 20% to /calculator/
    - 10% to /calculator/#methodology
    """
    weights = [50, 20, 20, 10]
    seed = idx % sum(weights)
    cum = 0
    for i, w in enumerate(weights):
        cum += w
        if seed < cum:
            return DESTINATION_URLS[i]
    return DESTINATION_URLS[0]


# ============================================================
# REST DAYS — designate days where we deliberately don't publish
# ============================================================
def is_rest_day(d: Optional[datetime] = None) -> bool:
    """Designate Sundays as "rest days" — no batch publishing.

    Helps the velocity profile look more human (humans don't usually
    blast 30 articles on Sunday).
    """
    if d is None:
        d = datetime.now()
    return d.weekday() == 6  # Sunday


# ============================================================
# VELOCITY STATUS — inspector for dashboards/CLIs
# ============================================================
def velocity_status() -> Dict:
    """Snapshot of current velocity across all platforms in our log."""
    entries = _load_log()
    now = datetime.now()
    cutoff_24h = now - timedelta(hours=24)
    cutoff_7d = now - timedelta(days=7)
    cutoff_30d = now - timedelta(days=30)

    plats = Counter(e["platform"] for e in entries if datetime.fromisoformat(e["ts"]) >= cutoff_30d)
    out = {
        "as_of": now.isoformat(),
        "platforms": {},
        "is_rest_day": is_rest_day(),
    }
    for plat in plats:
        rel = [e for e in entries if e["platform"] == plat]
        c24 = sum(1 for e in rel if datetime.fromisoformat(e["ts"]) >= cutoff_24h)
        c7d = sum(1 for e in rel if datetime.fromisoformat(e["ts"]) >= cutoff_7d)
        c30d = sum(1 for e in rel if datetime.fromisoformat(e["ts"]) >= cutoff_30d)
        cap = DAILY_CAPS.get(plat, DAILY_CAPS["default"])
        out["platforms"][plat] = {
            "count_24h": c24, "cap_24h": cap[0],
            "count_7d": c7d, "cap_7d": cap[1],
            "count_30d": c30d, "cap_30d": cap[2],
            "headroom_24h": cap[0] - c24,
            "status": "BLOCKED" if c24 >= cap[0] else ("WARN" if c24 >= cap[0] * 0.8 else "OK"),
        }
    return out


# ============================================================
# COMBINED PRE-PUBLISH CHECK
# ============================================================
@dataclass
class SafetyCheckResult:
    ok: bool
    velocity: VelocityResult
    similarity_ok: bool
    similarity_score: float
    similarity_msg: str
    rest_day: bool
    issues: List[str]


def pre_publish_check(platform: str, content: str, special_kind: Optional[str] = None,
                       respect_rest_day: bool = True) -> SafetyCheckResult:
    """The single function every publishing script should call before
    publishing. Returns a SafetyCheckResult with go/no-go decision.

    Usage:
        from core.safety import pre_publish_check, log_publish, jitter_sleep
        result = pre_publish_check("dev.to", article_body)
        if not result.ok:
            print(f"BLOCKED: {result.issues}")
            return
        publish(...)
        log_publish("dev.to", url, article_body[:200], strategy="devto-niche")
        jitter_sleep(35)
    """
    issues = []
    vel = velocity_gate(platform, special_kind=special_kind)
    if not vel.ok:
        issues.append(vel.reason)

    sim_ok, sim_score, sim_msg = content_similarity_check(content, platform)
    if not sim_ok:
        issues.append(sim_msg)

    rest = is_rest_day() if respect_rest_day else False
    if rest:
        issues.append("today is rest day (Sunday) — skipping for natural pacing")

    return SafetyCheckResult(
        ok=(len(issues) == 0),
        velocity=vel,
        similarity_ok=sim_ok,
        similarity_score=sim_score,
        similarity_msg=sim_msg,
        rest_day=rest,
        issues=issues,
    )
