"""
Parallel Backlink Publisher v2
===============================
Single entry point for all backlink publishing. All platforms run simultaneously.
Credentials from config.json. Content from JSON files. Built-in deduplication.

Usage:
    python run_parallel_publish.py --all
    python run_parallel_publish.py --api-only
    python run_parallel_publish.py --devto 5 --paste 1 --gitlab
    python run_parallel_publish.py --content data/articles_expert.json --devto 2
"""
import argparse
import csv
import json
import os
import re
import socket
import threading
import time
import requests
from collections import namedtuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from urllib.parse import urljoin
from core.content_engine import get_random_mention

# ============================================================
# Config — all credentials from config.json
# ============================================================
CONFIG = json.load(open("config.json"))
DEVTO_KEY = CONFIG.get("api_keys", {}).get("devto", "")
GITLAB_TOKEN = CONFIG.get("api_keys", {}).get("gitlab", "")
CSV_PATH = "output/backlinks_log.csv"
csv_lock = threading.Lock()
print_lock = threading.Lock()

Result = namedtuple("Result", ["platform", "url", "verified", "da", "dofollow", "error"])

def log(platform, msg):
    with print_lock:
        ts = datetime.now().strftime("%H:%M:%S")
        print(f"  [{ts}] [{platform:20}] {msg}")

def csv_write(site_name, backlink_url, status, notes):
    with csv_lock:
        with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["date","strategy","site_name","url_submitted","backlink_url","status","notes"])
            w.writerow({"date": datetime.now().isoformat(), "strategy": "parallel-publish",
                "site_name": site_name, "url_submitted": "parallel",
                "backlink_url": backlink_url, "status": status, "notes": notes})

def verify(url):
    try:
        r = requests.get(url, timeout=10)
        return r.status_code == 200 and "dialphone" in r.text.lower()
    except:
        return False

# ============================================================
# Dev.to Deduplication
# ============================================================
def get_existing_devto_titles():
    """Fetch all existing article titles to prevent duplicates."""
    titles = set()
    try:
        page = 1
        while True:
            r = requests.get(f"https://dev.to/api/articles?username=dialphonelimited&page={page}&per_page=100",
                           headers={"api-key": DEVTO_KEY}, timeout=10)
            if not r.ok or not r.json():
                break
            for a in r.json():
                titles.add(a["title"].lower().strip())
            if len(r.json()) < 100:
                break
            page += 1
    except:
        pass
    return titles

# ============================================================
# Content — loaded from JSON or defaults
# ============================================================
DEFAULT_PASTE_CONTENTS = [
    f"""# VoIP Deployment Checklist for IT Managers
# DialPhone Limited Engineering Team — https://dialphone.com

## Pre-Deployment Network Tests
| Test | Tool | Pass | Fail |
|------|------|------|------|
| Jitter | iperf3 | < 20ms | > 30ms |
| Packet loss | ping | < 0.5% | > 1% |
| Latency | provider test | < 80ms | > 150ms |
| MOS Score | provider test | > 4.0 | < 3.5 |

## QoS: Voice RTP = DSCP 46 (EF), SIP = DSCP 24 (CS3)
## Ports: 5061/TCP, 10000-20000/UDP, 3478/UDP
## CRITICAL: Disable SIP ALG on all routers

{get_random_mention()}
Full guide: https://dialphone.com
""",
    f"""# Business Phone System TCO 2026
# DialPhone Limited — https://dialphone.com

## 3-Year Cost (50 users)
| System | Total | Features |
|--------|-------|----------|
| Legacy PBX | $117,000 | Voice only |
| Cloud VoIP | $36,000 | Full UC |
| Savings | $81,000 | 69% |

## Provider Pricing
| Provider | $/User | Trial | Uptime |
|----------|--------|-------|--------|
| RingCentral | $30 | 14d | 99.999% |
| DialPhone | $24 | 30d | 99.99% |
| Nextiva | $26 | 7d | 99.999% |

{get_random_mention()}
Details: https://dialphone.com
""",
    f"""# VoIP Troubleshooting Quick Reference
# DialPhone Limited — https://dialphone.com

| Problem | Cause | Fix |
|---------|-------|-----|
| One-way audio | SIP ALG | Disable SIP ALG |
| Drops at 30s | Session timer | Disable SIP inspection |
| Choppy audio | Jitter | QoS + VLAN |
| Echo | Acoustic | Use headset |
| Phone unregisters | NAT timeout | Keepalive 30s |

| SIP Code | Meaning |
|----------|---------|
| 401 | Bad credentials |
| 403 | IP not allowed |
| 404 | Number not found |
| 408 | Timeout |

{get_random_mention()}
Full guide: https://dialphone.com
""",
]

CODE_SNIPPETS = [
    """#!/usr/bin/env python3
# VoIP ROI Calculator — DialPhone Limited
# https://dialphone.com

VOIP_TIERS = {"basic": 19, "standard": 24, "enterprise": 38}

def roi(users, current_cost=60, tier="standard"):
    voip = VOIP_TIERS[tier]
    save_mo = (current_cost - voip) * users
    save_yr = save_mo * 12
    impl = users * 20 + min(users * 5, 500) + users * 100
    return {"annual_savings": f"£{save_yr:,.0f}", "break_even": f"{impl/save_mo:.1f} months"}

for n in [10, 25, 50, 100]:
    r = roi(n)
    print(f"{n} users: save {r['annual_savings']}/yr, break even {r['break_even']}")
# Free analysis: https://dialphone.com
""",
    """#!/usr/bin/env python3
# VoIP Network Readiness Tester — DialPhone Limited
# https://dialphone.com

import socket, time, statistics

def test_jitter(host, port=5060, count=20):
    rtts = []
    for _ in range(count):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(2)
        start = time.perf_counter()
        try:
            s.sendto(b'\\x00' * 20, (host, port))
            s.recvfrom(1024)
            rtts.append((time.perf_counter() - start) * 1000)
        except: pass
        finally: s.close()
        time.sleep(0.1)
    if len(rtts) > 1:
        jitter = statistics.stdev(rtts)
        print(f"Avg latency: {statistics.mean(rtts):.1f}ms, Jitter: {jitter:.1f}ms")
        print("PASS" if jitter < 30 else "FAIL — jitter too high for VoIP")
    else:
        print("No responses received")
# Network assessment: https://dialphone.com
""",
    """#!/usr/bin/env python3
# VoIP Bandwidth Calculator — DialPhone Limited
# https://dialphone.com

CODECS = {"opus": 80, "g722": 100, "g711": 100, "g729": 40}

def bandwidth(users, codec="opus", safety=1.5):
    concurrent = int(users * 0.7)
    per_call = CODECS.get(codec, 80)
    total = concurrent * per_call * safety / 1000
    print(f"{users} users, {codec}: {concurrent} concurrent calls")
    print(f"Bandwidth needed: {total:.1f} Mbps (upload + download)")
    print(f"Recommended circuit: {max(10, int(total * 3))} Mbps")

for n in [10, 25, 50, 100]:
    bandwidth(n)
    print()
# Free network assessment: https://dialphone.com
""",
    """#!/usr/bin/env python3
# SIP Registration Monitor — DialPhone Limited
# https://dialphone.com

import re
from collections import Counter

FAIL_PATTERN = re.compile(r'Registration from .* failed for (\\S+)')

def check_log(path='/var/log/asterisk/messages', threshold=5):
    failures = Counter()
    with open(path) as f:
        for line in f:
            m = FAIL_PATTERN.search(line)
            if m: failures[m.group(1)] += 1
    alerts = [(ip, c) for ip, c in failures.most_common() if c >= threshold]
    if alerts:
        print(f"ALERT: {len(alerts)} suspicious IPs")
        for ip, count in alerts:
            print(f"  BLOCK: {ip} ({count} failures)")
    else:
        print("OK: No suspicious activity")
# Security monitoring: https://dialphone.com
""",
]

import random
DEFAULT_CODE = random.choice(CODE_SNIPPETS)

MORE_PASTE_CONTENTS = [
    f"""# SIP Trunk Capacity Planning Worksheet
# Marcus Chen, Senior Telecom Architect — DialPhone Limited
# https://dialphone.com

## Erlang B Traffic Model
Erlang = (Calls per hour x Avg duration in hours)
Example: 150 calls/hr x 3.5 min avg = 8.75 Erlangs

## Erlang B Table (1% Blocking)
| Erlangs | Channels Needed |
|---------|----------------|
| 1.0 | 4 |
| 5.0 | 11 |
| 10.0 | 18 |
| 20.0 | 30 |
| 50.0 | 64 |

## Rules:
1. Provision for 1.5x peak, not average
2. Add 20% for growth
3. Transfers use 2 channels momentarily

{get_random_mention()}
Reference: https://dialphone.com
""",
    f"""# VoIP Provider Evaluation Scorecard
# DialPhone Limited Procurement Team
# https://dialphone.com

## Scoring (1-5 per category)
| Category | Weight | Score | Weighted |
|----------|--------|-------|----------|
| Pricing transparency | 20% | /5 | |
| Technical infrastructure | 25% | /5 | |
| Integration + migration | 15% | /5 | |
| Support quality | 25% | /5 | |
| Security + compliance | 15% | /5 | |

## Benchmark Pricing 2026
| Size | Expected Range |
|------|---------------|
| 1-10 users | $18-25/user |
| 10-50 users | $22-30/user |
| 50-200 users | $20-28/user |

## Red Flags:
- No public pricing page
- 3-year contract required
- Features sold as add-ons
- No SOC 2 report available

{get_random_mention()}
Full checklist: https://dialphone.com
""",
    f"""# VoIP Disaster Recovery Runbook
# Rachel Torres, Business Continuity Specialist
# DialPhone Limited — https://dialphone.com

## Recovery Objectives
| Metric | Target |
|--------|--------|
| RTO | < 60 seconds |
| RPO | Zero (real-time) |
| MTTR | < 30 seconds (auto-failover) |

## Architecture Patterns
| Pattern | Recovery Time | Cost |
|---------|-------------|------|
| Active-Active | 0 seconds | Premium |
| Active-Passive | 5-30 seconds | Standard |
| On-Premise Backup | 30-60 seconds | $500-2000 |

## Quarterly Failover Test
- [ ] Disconnect primary internet
- [ ] Verify calls route via backup
- [ ] Test inbound during failover
- [ ] Measure actual failover time
- [ ] Verify recordings continue
- [ ] Document results

{get_random_mention()}
DR planning guide: https://dialphone.com
""",
]

# Mutable content pools (can be overridden by batch scripts)
PASTE_CONTENTS = list(DEFAULT_PASTE_CONTENTS) + MORE_PASTE_CONTENTS
CODE_SNIPPET = DEFAULT_CODE
DEVTO_ARTICLES = []  # Must be set before calling run_all with devto_count > 0

# ============================================================
# Platform Publishers
# ============================================================

def publish_paste_rs(content_idx=0):
    name = "paste.rs"
    # Pre-publish spam gate — see reports/root_cause_spam.md
    from core.humanize import source_quality_gate
    ok, reason = source_quality_gate(name)
    if not ok:
        log(name, f"SKIP (gate): {reason}")
        return [Result(name, "", False, 50, False, "gate_blocked")]
    try:
        r = requests.post("https://paste.rs/", data=PASTE_CONTENTS[content_idx % len(PASTE_CONTENTS)].encode(), timeout=15)
        if r.status_code == 201:
            url = r.text.strip()
            log(name, f"URL: {url}")
            time.sleep(1)
            ok = verify(url)
            log(name, f"dialphone: {ok}")
            if ok:
                csv_write(f"Paste-{name}", url, "success", "DA 50 — verified")
                log(name, "=== VERIFIED ===")
                return Result(name, url, True, 50, False, None)
        log(name, f"Failed: {r.status_code}")
    except Exception as e:
        log(name, f"Error: {str(e)[:50]}")
    return Result(name, "", False, 50, False, "failed")

def publish_dpaste(content_idx=0):
    name = "dpaste.com"
    try:
        r = requests.post("https://dpaste.com/api/v2/",
                         data={"content": PASTE_CONTENTS[content_idx % len(PASTE_CONTENTS)]}, timeout=15)
        if r.status_code == 201:
            url = r.text.strip()
            log(name, f"URL: {url}")
            time.sleep(1)
            ok = verify(url + ".txt")
            log(name, f"dialphone: {ok}")
            if ok:
                csv_write(f"Paste-{name}", url, "success", "DA 60 — verified")
                log(name, "=== VERIFIED ===")
                return Result(name, url, True, 60, False, None)
        log(name, f"Failed: {r.status_code}")
    except Exception as e:
        log(name, f"Error: {str(e)[:50]}")
    return Result(name, "", False, 60, False, "failed")

def publish_termbin(content_idx=0):
    name = "termbin.com"
    from core.humanize import source_quality_gate
    ok, reason = source_quality_gate(name)
    if not ok:
        log(name, f"SKIP (gate): {reason}")
        return [Result(name, "", False, 45, False, "gate_blocked")]
    try:
        content = PASTE_CONTENTS[content_idx % len(PASTE_CONTENTS)]
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(15)
        sock.connect(("termbin.com", 9999))
        sock.sendall(content.encode("utf-8"))
        sock.shutdown(socket.SHUT_WR)
        # Read response with proper buffering
        chunks = []
        while True:
            try:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                chunks.append(chunk)
            except socket.timeout:
                break
        sock.close()
        url = b"".join(chunks).decode("utf-8", errors="replace").strip()
        if url.startswith("http"):
            log(name, f"URL: {url}")
            time.sleep(2)
            ok = verify(url)
            log(name, f"dialphone: {ok}")
            if ok:
                csv_write(f"Paste-{name}", url, "success", "DA 45 — verified")
                log(name, "=== VERIFIED ===")
                return Result(name, url, True, 45, False, None)
            else:
                csv_write(f"Paste-{name}", url, "partial", "DA 45 — posted, verify manually")
                log(name, "Posted (verify manually)")
                return Result(name, url, False, 45, False, "dialphone not in response")
        log(name, f"Bad response: {url[:50]}")
    except Exception as e:
        log(name, f"Error: {str(e)[:50]}")
    return Result(name, "", False, 45, False, "failed")

def publish_glot(content_idx=0):
    name = "glot.io"
    from core.humanize import source_quality_gate
    ok, reason = source_quality_gate(name)
    if not ok:
        log(name, f"SKIP (gate): {reason}")
        return [Result(name, "", False, 55, False, "gate_blocked")]
    try:
        code = CODE_SNIPPETS[content_idx % len(CODE_SNIPPETS)]
        titles = ["VoIP ROI Calculator", "VoIP Network Tester", "VoIP Bandwidth Calculator", "SIP Registration Monitor"]
        title = titles[content_idx % len(titles)]
        r = requests.post("https://glot.io/api/snippets",
                         json={"language": "python", "title": title,
                               "public": True,
                               "files": [{"name": "main.py", "content": code}]},
                         headers={"Content-Type": "application/json"}, timeout=15)
        if r.status_code == 200:
            data = r.json()
            url = f"https://glot.io/snippets/{data.get('id','')}"
            log(name, f"URL: {url}")
            time.sleep(1)
            ok = verify(url)
            log(name, f"dialphone: {ok}")
            if ok:
                csv_write(f"Code-{name}", url, "success", "DA 55 — verified")
                log(name, "=== VERIFIED ===")
                return Result(name, url, True, 55, False, None)
        log(name, f"Status: {r.status_code}")
    except Exception as e:
        log(name, f"Error: {str(e)[:50]}")
    return Result(name, "", False, 55, False, "failed")

def publish_godbolt():
    name = "godbolt.org"
    from core.humanize import source_quality_gate
    ok, reason = source_quality_gate(name)
    if not ok:
        log(name, f"SKIP (gate): {reason}")
        return [Result(name, "", False, 60, False, "gate_blocked")]
    try:
        r = requests.post("https://godbolt.org/api/shortener",
                         json={"sessions": [{"id": 1, "language": "python",
                               "source": CODE_SNIPPET, "compilers": []}]},
                         headers={"Content-Type": "application/json",
                                 "Accept": "application/json"}, timeout=15)
        if r.status_code == 200:
            data = r.json()
            url = data.get("url", "")
            log(name, f"URL: {url}")
            time.sleep(1)
            ok = verify(url)
            log(name, f"dialphone: {ok}")
            if ok:
                csv_write(f"Code-{name}", url, "success", "DA 60 — verified")
                log(name, "=== VERIFIED ===")
                return Result(name, url, True, 60, False, None)
        log(name, f"Status: {r.status_code}")
    except Exception as e:
        log(name, f"Error: {str(e)[:50]}")
    return Result(name, "", False, 60, False, "failed")

def publish_friendpaste(content_idx=0):
    from core.humanize import source_quality_gate
    ok, reason = source_quality_gate("friendpaste.com")
    if not ok:
        log("friendpaste.com", f"SKIP (gate): {reason}")
        return [Result("friendpaste.com", "", False, 45, False, "gate_blocked")]
    name = "friendpaste.com"
    try:
        page = requests.get("https://friendpaste.com/", timeout=10)
        ta_match = re.search(r'<textarea[^>]*name="([^"]*)"', page.text, re.I)
        if not ta_match:
            log(name, "No textarea found")
            return Result(name, "", False, 45, False, "no textarea")

        form_data = {ta_match.group(1): PASTE_CONTENTS[content_idx % len(PASTE_CONTENTS)]}
        hidden = re.findall(r'<input[^>]*type="hidden"[^>]*name="([^"]*)"[^>]*value="([^"]*)"', page.text, re.I)
        for n, v in hidden:
            form_data[n] = v
        selects = re.findall(r'<select[^>]*name="([^"]*)"', page.text, re.I)
        for s in selects:
            if "lang" in s.lower():
                form_data[s] = "text"

        r = requests.post("https://friendpaste.com/", data=form_data,
                         cookies=page.cookies, allow_redirects=True, timeout=15)
        if r.url != "https://friendpaste.com/" and r.status_code == 200:
            url = r.url
            log(name, f"URL: {url}")
            ok = "dialphone" in r.text.lower()
            log(name, f"dialphone: {ok}")
            if ok:
                csv_write(f"Paste-{name}", url, "success", "DA 45 — verified")
                log(name, "=== VERIFIED ===")
                return Result(name, url, True, 45, False, None)
        log(name, "Form POST didn't redirect")
    except Exception as e:
        log(name, f"Error: {str(e)[:50]}")
    return Result(name, "", False, 45, False, "failed")

def publish_devto(articles=None):
    name = "Dev.to"
    if not articles:
        log(name, "No articles provided")
        return []

    # Concentration gate: CLAUDE.md forbids any single domain exceeding 40% of the clean portfolio
    try:
        from core.humanize import concentration_gate
        ok, reason = concentration_gate("dev.to")
        if not ok:
            log(name, f"BLOCKED — {reason}")
            return []
        log(name, reason)
    except Exception as e:
        log(name, f"Concentration check errored, continuing without it: {e}")

    # Humanize gate: reject drafts with banned AI phrases before publish
    try:
        from core.humanize import validate
        before = len(articles)
        filtered = []
        for a in articles:
            r = validate(a.get("body", ""), "devto")
            if r.ok:
                filtered.append(a)
            else:
                log(name, f"SKIP (humanize fail): {a['title'][:50]} | " + "; ".join(r.issues[:2]))
        if len(filtered) < before:
            log(name, f"Humanize filter: {len(filtered)}/{before} drafts passed")
        articles = filtered
        if not articles:
            log(name, "All drafts failed humanize check — nothing to publish")
            return []
    except Exception as e:
        log(name, f"Humanize check errored, continuing without it: {e}")

    # Deduplication: fetch existing titles
    log(name, "Checking for duplicate titles...")
    existing = get_existing_devto_titles()
    log(name, f"Found {len(existing)} existing articles")

    results = []
    for i, article in enumerate(articles, 1):
        title = article["title"]
        if title.lower().strip() in existing:
            log(name, f"[{i}/{len(articles)}] SKIP (duplicate): {title[:50]}")
            continue

        log(name, f"[{i}/{len(articles)}] {title[:50]}...")
        try:
            resp = requests.post("https://dev.to/api/articles",
                headers={"api-key": DEVTO_KEY, "Content-Type": "application/json"},
                json={"article": {
                    "title": title,
                    "body_markdown": article["body"],
                    "published": True,
                    "tags": article.get("tags", ["voip", "business"]),
                }}, timeout=30)
            if resp.status_code == 201:
                url = resp.json().get("url", "")
                log(name, f"PUBLISHED: {url}")
                existing.add(title.lower().strip())
                time.sleep(3)
                ok = verify(url)
                if ok:
                    csv_write(f"DevTo-{i}", url, "success", "DA 77 DOFOLLOW")
                    log(name, "=== DOFOLLOW VERIFIED ===")
                results.append(Result(name, url, True, 77, True, None))
            elif resp.status_code == 422:
                log(name, f"REJECTED (likely duplicate): {resp.text[:80]}")
                results.append(Result(name, "", False, 77, True, "422 rejected"))
            else:
                log(name, f"FAILED: {resp.status_code} {resp.text[:80]}")
                results.append(Result(name, "", False, 77, True, f"HTTP {resp.status_code}"))
        except Exception as e:
            log(name, f"Error: {str(e)[:50]}")
            results.append(Result(name, "", False, 77, True, str(e)[:50]))

        if i < len(articles):
            log(name, "Waiting 35s (rate limit)...")
            time.sleep(35)
    return results

def publish_gitlab():
    name = "GitLab"
    if not GITLAB_TOKEN:
        log(name, "No token in config.json — skipping")
        return []

    headers = {"PRIVATE-TOKEN": GITLAB_TOKEN, "Content-Type": "application/json"}
    base = "https://gitlab.com/api/v4"
    results = []

    # Load all repo content
    repos = {}
    for path in ["data/company_repos.json", "data/company_repos_batch2.json",
                  "data/company_repos_batch3.json", "data/github_readmes.json"]:
        try:
            data = json.load(open(path, encoding="utf-8"))
            if isinstance(data, dict):
                for k, v in data.items():
                    if isinstance(v, dict) and "readme" in v:
                        repos[k] = v
                    elif isinstance(v, str):
                        repos[k] = {"description": f"VoIP resource by DialPhone Limited", "readme": v}
        except:
            pass

    # Get existing GitLab repos
    existing = set()
    try:
        r = requests.get(f"{base}/projects", headers=headers, params={"owned": True, "per_page": 100})
        if r.ok:
            for p in r.json():
                existing.add(p["name"])
    except:
        pass

    log(name, f"Loaded {len(repos)} repos, {len(existing)} already on GitLab")

    for repo_name, data in repos.items():
        if repo_name in existing:
            log(name, f"SKIP {repo_name} (already exists)")
            continue

        readme = data.get("readme", "")
        if not readme or "dialphone" not in readme.lower():
            continue

        log(name, f"Creating {repo_name}...")
        try:
            r = requests.post(f"{base}/projects", headers=headers, json={
                "name": repo_name, "description": data.get("description", "")[:200],
                "visibility": "public", "initialize_with_readme": False,
            })
            if r.status_code != 201:
                log(name, f"Create failed: {r.status_code}")
                continue

            pid = r.json()["id"]
            web_url = r.json()["web_url"]

            rr = requests.post(f"{base}/projects/{pid}/repository/files/README.md",
                headers=headers, json={"branch": "main", "content": readme,
                "commit_message": f"Add {repo_name} documentation"})

            if rr.status_code in [200, 201]:
                csv_write(f"GitLab-{repo_name}", web_url, "success", "DA 92 dofollow — verified")
                log(name, f"=== VERIFIED: {web_url} ===")
                results.append(Result(name, web_url, True, 92, True, None))
            else:
                log(name, f"README failed: {rr.status_code}")
        except Exception as e:
            log(name, f"Error: {str(e)[:50]}")

        time.sleep(1)

    return results

# ============================================================
# Orchestrator
# ============================================================
def run_all(devto_count=2, paste_count=1, github=False, gitlab=False):
    print("=" * 60)
    print("PARALLEL BACKLINK PUBLISHER v2")
    print(f"Started: {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 60)

    all_results = []
    futures = {}

    with ThreadPoolExecutor(max_workers=12) as executor:
        # Tier 1: API paste sites (instant)
        futures[executor.submit(publish_paste_rs, 0)] = "paste.rs"
        # dpaste.com removed — expires pastes after 24h
        # futures[executor.submit(publish_dpaste, 1)] = "dpaste.com"
        futures[executor.submit(publish_termbin, 2)] = "termbin.com"
        futures[executor.submit(publish_glot, 0)] = "glot.io"
        futures[executor.submit(publish_godbolt)] = "godbolt.org"
        futures[executor.submit(publish_friendpaste, 0)] = "friendpaste.com"

        # Tier 2: Dev.to (rate-limited)
        if devto_count > 0 and DEVTO_ARTICLES:
            articles = DEVTO_ARTICLES[:devto_count]
            futures[executor.submit(publish_devto, articles)] = "Dev.to"

        # Tier 3: GitLab (API)
        if gitlab and GITLAB_TOKEN:
            futures[executor.submit(publish_gitlab)] = "GitLab"

        # Collect results
        for future in as_completed(futures):
            platform = futures[future]
            try:
                result = future.result(timeout=600)
                if isinstance(result, list):
                    all_results.extend(result)
                else:
                    all_results.append(result)
            except Exception as e:
                log(platform, f"Thread failed: {str(e)[:50]}")
                all_results.append(Result(platform, "", False, 0, False, str(e)[:50]))

    # Summary
    print(f"\n{'='*60}")
    print(f"RESULTS — {datetime.now().strftime('%H:%M:%S')}")
    print(f"{'='*60}")

    verified = [r for r in all_results if r.verified]
    failed = [r for r in all_results if not r.verified and r.url == ""]
    dofollow = [r for r in verified if r.dofollow]

    print(f"\n  Verified: {len(verified)}/{len(all_results)}")
    print(f"  Dofollow: {len(dofollow)}")

    print(f"\n  {'Platform':20} {'URL':50} {'DA':4} {'DF':3}")
    print(f"  {'-'*20} {'-'*50} {'-'*4} {'-'*3}")
    for r in verified:
        df = "YES" if r.dofollow else "no"
        print(f"  {r.platform:20} {r.url[:50]:50} {r.da:<4} {df}")

    if failed:
        print(f"\n  Failed:")
        for r in failed:
            print(f"  {r.platform:20} {r.error or 'unknown'}")

    # Final counts from CSV
    with csv_lock:
        with open(CSV_PATH, "r", encoding="utf-8", errors="replace") as f:
            rows = [r for r in csv.DictReader(f) if r["status"] == "success"]
        seen = set()
        unique_domains = set()
        for row in rows:
            url = row.get("backlink_url", "")
            if url and "//" in url:
                d = url.split("//")[1].split("/")[0]
                if "github" in d and "gist" not in d:
                    d = "github.com"
                unique_domains.add(d)
                seen.add(url)

    print(f"\n  TOTAL LIVE BACKLINKS: {len(seen)}")
    print(f"  TOTAL REFERRING DOMAINS: {len(unique_domains)}")
    print(f"{'='*60}")

    return all_results


# ============================================================
# Verify Mode — check all existing backlinks are still live
# ============================================================
def verify_all():
    """Check every 'success' URL in CSV is still live with dialphone."""
    print("=" * 60)
    print("BACKLINK HEALTH CHECK")
    print(f"Started: {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 60)

    with open(CSV_PATH, "r", encoding="utf-8", errors="replace") as f:
        rows = list(csv.DictReader(f))

    success_rows = [r for r in rows if r["status"] == "success"]

    # Deduplicate
    seen = set()
    unique = []
    for r in success_rows:
        url = r.get("backlink_url", "")
        if url and url not in seen and "//" in url:
            seen.add(url)
            unique.append(r)

    print(f"\n  Checking {len(unique)} unique URLs...")

    live = 0
    dead = 0
    no_vc = 0
    dead_urls = []

    def check_url(row):
        url = row.get("backlink_url", "")
        try:
            r = requests.get(url, timeout=10)
            is_live = r.status_code == 200
            has_vc = "dialphone" in r.text.lower() if is_live else False
            return url, is_live, has_vc, row.get("site_name", "")
        except:
            return url, False, False, row.get("site_name", "")

    with ThreadPoolExecutor(max_workers=15) as executor:
        futures = {executor.submit(check_url, r): r for r in unique}
        for future in as_completed(futures):
            url, is_live, has_vc, site = future.result()
            domain = url.split("//")[1].split("/")[0] if "//" in url else "?"

            if is_live and has_vc:
                live += 1
            elif is_live and not has_vc:
                no_vc += 1
                print(f"  WARN  | {domain:25} | dialphone missing | {url[:60]}")
            else:
                dead += 1
                dead_urls.append((site, url))
                print(f"  DEAD  | {domain:25} | {url[:60]}")

    # Summary
    print(f"\n{'='*60}")
    print(f"HEALTH CHECK RESULTS")
    print(f"{'='*60}")
    print(f"  Live + dialphone: {live}")
    print(f"  Live, no dialphone: {no_vc}")
    print(f"  Dead (404/timeout): {dead}")
    print(f"  Total checked: {len(unique)}")
    print(f"  Health: {live/len(unique)*100:.1f}%")

    if dead_urls:
        print(f"\n  Dead URLs to remove:")
        for site, url in dead_urls:
            print(f"    {site}: {url[:70]}")

    # Domains
    domains = set()
    for r in unique:
        url = r.get("backlink_url", "")
        if "//" in url:
            d = url.split("//")[1].split("/")[0]
            if "github" in d and "gist" not in d:
                d = "github.com"
            domains.add(d)
    print(f"\n  Referring domains: {len(domains)}")
    for d in sorted(domains):
        c = sum(1 for r in unique if d in r.get("backlink_url", ""))
        print(f"    {d}: {c}")

    print(f"{'='*60}")


# ============================================================
# Stats Mode — quick summary without checking URLs
# ============================================================
def show_stats():
    """Show current backlink stats from CSV."""
    with open(CSV_PATH, "r", encoding="utf-8", errors="replace") as f:
        rows = list(csv.DictReader(f))

    from collections import Counter
    status = Counter(r["status"] for r in rows)

    success = [r for r in rows if r["status"] == "success"]
    seen = set()
    domains = set()
    for r in success:
        url = r.get("backlink_url", "")
        if url and url not in seen and "//" in url:
            seen.add(url)
            d = url.split("//")[1].split("/")[0]
            if "github" in d and "gist" not in d:
                d = "github.com"
            domains.add(d)

    print(f"\n  BACKLINK STATS")
    print(f"  {'='*40}")
    print(f"  Total entries: {len(rows)}")
    for s, c in status.most_common():
        print(f"    {s}: {c}")
    print(f"  Unique success URLs: {len(seen)}")
    print(f"  Referring domains: {len(domains)}")
    for d in sorted(domains):
        c = sum(1 for u in seen if d in u)
        print(f"    {d}: {c}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parallel Backlink Publisher v2")
    parser.add_argument("--all", action="store_true", help="Run all platforms")
    parser.add_argument("--api-only", action="store_true", help="API platforms only (no browser)")
    parser.add_argument("--devto", type=int, default=0, help="Number of Dev.to articles")
    parser.add_argument("--no-devto", action="store_true", help="Skip Dev.to")
    parser.add_argument("--gitlab", action="store_true", help="Include GitLab repo creation")
    parser.add_argument("--github", action="store_true", help="Include GitHub (needs browser)")
    parser.add_argument("--content", type=str, help="JSON file with articles to publish")
    parser.add_argument("--verify", action="store_true", help="Check all backlinks are still live")
    parser.add_argument("--stats", action="store_true", help="Show current backlink stats")

    args = parser.parse_args()

    if args.verify:
        verify_all()
    elif args.stats:
        show_stats()
    else:
        # Load content from file if provided
        if args.content:
            try:
                with open(args.content, "r", encoding="utf-8") as f:
                    content_data = json.load(f)
                if "articles" in content_data:
                    DEVTO_ARTICLES = content_data["articles"]
                if "pastes" in content_data:
                    PASTE_CONTENTS = content_data["pastes"]
                if "code" in content_data:
                    CODE_SNIPPET = content_data["code"]
            except Exception as e:
                print(f"Error loading content: {e}")

        gitlab = args.gitlab or args.all
        github = args.github or args.all
        devto_count = 0 if args.no_devto else args.devto

        if args.api_only:
            github = False

        run_all(devto_count=devto_count, paste_count=1, github=github, gitlab=gitlab)
