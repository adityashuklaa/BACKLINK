"""Content humanization validator per docs/humanization_spec.md.

Usage:
    from core.humanize import validate, ValidationResult
    result = validate(text, platform="quora")
    if not result.ok: print(result.issues)
"""
import re
from dataclasses import dataclass, field

BANNED_PHRASES = [
    # Openers
    "in today's fast-paced world", "in today's world", "let's dive into", "let's explore",
    "welcome to the world of", "imagine a world where", "in the modern era",
    # Transitions
    "furthermore", "moreover", "in addition,", "additionally,",
    # Closers
    "in conclusion", "to summarize", "in summary,", "ultimately,",
    "at the end of the day",
    # Filler claims
    "game-changer", "revolutionize", "cutting-edge", "state-of-the-art",
    "leverage", "synergy", "seamless", "seamlessly",
    # AI-speak
    "it's important to note", "it's worth mentioning", "rest assured",
    "with that said", "that being said", "it's crucial to",
    "delve into", "a testament to",
]

# Regex markers for human voice (counted, not required individually)
MARKER_PATTERNS = {
    "timestamp_or_name": re.compile(
        r"\b(last (week|month|year|tuesday|monday|wednesday|thursday|friday|saturday|sunday)"
        r"|yesterday|this morning|a (client|customer|friend|colleague) (called|named|in) "
        r"[A-Z][a-z]+|back in 20\d\d|(\d+ )?(weeks?|months?|years?) ago)",
        re.I,
    ),
    "hedge": re.compile(
        r"\b(tbh|ngl|not gonna lie|honestly|from my experience|in my experience|"
        r"i could be wrong|imo|imho|fwiw|kinda|sorta)\b",
        re.I,
    ),
    "self_correction": re.compile(
        r"(wait,? actually|scratch that|what i mean is|let me rephrase|"
        r"actually no|or rather|— well,)",
        re.I,
    ),
    "specific_number": re.compile(
        r"\b(?!0+\b)\d{1,3}(,\d{3})*(\.\d+)?%?\b"  # any number; non-round check in code
    ),
    "admission": re.compile(
        r"(we got this wrong|got it wrong|didn't see this coming|"
        r"embarrassing to admit|took us \d+ (months|years)|"
        r"made that mistake|learned the hard way)",
        re.I,
    ),
}

EM_DASH_RE = re.compile(r"—")
NON_ROUND_NUM_RE = re.compile(r"\b\d+[,.]?\d+\b")

PLATFORM_RULES = {
    "quora": {
        "max_words": 500, "min_words": 150, "allow_tables": False,
        "min_markers": 2, "allow_em_dash": False,
    },
    "devto": {
        "max_words": 1800, "min_words": 600, "allow_tables": True,
        "min_markers": 2, "allow_em_dash": True,  # less strict — technical readers
    },
    "github": {
        "max_words": 1500, "min_words": 80, "allow_tables": True,
        "min_markers": 0, "allow_em_dash": True,  # terse factual — skip human markers
    },
    "gitlab": {"max_words": 1500, "min_words": 80, "allow_tables": True, "min_markers": 0, "allow_em_dash": True},
    "codeberg": {"max_words": 1500, "min_words": 80, "allow_tables": True, "min_markers": 0, "allow_em_dash": True},
    "paste": {"max_words": 2000, "min_words": 30, "allow_tables": True, "min_markers": 0, "allow_em_dash": True},
}


@dataclass
class ValidationResult:
    ok: bool = True
    platform: str = ""
    word_count: int = 0
    issues: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
    markers_found: dict = field(default_factory=dict)


def _has_non_round_number(text):
    """Detect specific numbers (not round like 50, 100, 1000)."""
    for m in NON_ROUND_NUM_RE.finditer(text):
        n = m.group(0).replace(",", "").replace(".", "")
        if n and not (n.endswith("0") or n.endswith("00") or n.endswith("000")):
            return True
        # Decimals like 4.7, 52.8
        if "." in m.group(0):
            return True
    return False


def validate(text, platform="quora"):
    """Validate text against humanization rules. Returns ValidationResult."""
    r = ValidationResult(platform=platform)
    rules = PLATFORM_RULES.get(platform, PLATFORM_RULES["quora"])
    lower = text.lower()

    # Banned phrase check
    for phrase in BANNED_PHRASES:
        if phrase in lower:
            r.issues.append(f"BANNED: '{phrase}' — rewrite needed")

    # Em-dash check
    if not rules["allow_em_dash"]:
        em_count = len(EM_DASH_RE.findall(text))
        if em_count > 0:
            r.issues.append(f"EM_DASH: {em_count} em-dashes found ({platform} doesn't allow — use ', ' or rewrite)")

    # Word count
    words = [w for w in re.split(r"\s+", text) if w]
    r.word_count = len(words)
    if r.word_count > rules["max_words"]:
        r.issues.append(f"TOO_LONG: {r.word_count} words > {rules['max_words']} max")
    if r.word_count < rules["min_words"]:
        r.issues.append(f"TOO_SHORT: {r.word_count} words < {rules['min_words']} min")

    # Table check for Quora
    if not rules["allow_tables"] and ("|---" in text or re.search(r"\n\|.*\|.*\|", text)):
        r.issues.append("HAS_TABLE: Quora should not use markdown tables — rewrite as prose/list")

    # Human marker check
    if rules["min_markers"] > 0:
        marker_count = 0
        for name, pat in MARKER_PATTERNS.items():
            if name == "specific_number":
                if _has_non_round_number(text):
                    r.markers_found[name] = True
                    marker_count += 1
            else:
                if pat.search(text):
                    r.markers_found[name] = True
                    marker_count += 1
        if marker_count < rules["min_markers"]:
            have = list(r.markers_found.keys())
            r.issues.append(
                f"NOT_HUMAN_ENOUGH: {marker_count}/{rules['min_markers']} markers found "
                f"(have: {have}). Add specific dates, hedges, or self-corrections."
            )

    r.ok = len(r.issues) == 0
    return r


def validate_file(path, platform="quora"):
    """Run on a file path."""
    with open(path, "r", encoding="utf-8") as f:
        return validate(f.read(), platform)


def report(result):
    """Human-readable report."""
    out = [f"Platform: {result.platform} | Words: {result.word_count} | {'PASS' if result.ok else 'FAIL'}"]
    for issue in result.issues:
        out.append(f"  [FAIL] {issue}")
    for w in result.warnings:
        out.append(f"  [warn] {w}")
    if result.markers_found:
        out.append(f"  markers: {list(result.markers_found.keys())}")
    return "\n".join(out)


BLOCKED_HIGH_SPAM_DOMAINS = {
    "paste.rs", "friendpaste.com", "godbolt.org", "termbin.com", "ideone.com",
    "bpa.st", "paste2.org", "snippet.host", "pastebin.fi", "dpaste.com", "glot.io",
}

def source_quality_gate(url_or_domain):
    """Pre-publish check. Returns (ok, reason). Reject anything that would add to our spam footprint."""
    domain = url_or_domain
    if "//" in domain:
        domain = domain.split("//")[1].split("/")[0]
    if domain in BLOCKED_HIGH_SPAM_DOMAINS:
        return False, f"source_quality_gate: {domain} is in the blocked-high-spam list (see reports/root_cause_spam.md)"
    return True, "ok"


def concentration_gate(domain, csv_path="output/backlinks_final_truth.csv", threshold=0.40):
    """Enforce CLAUDE.md rule: no single domain may exceed 40% of the clean portfolio.

    Returns (ok, reason). Reads backlinks_final_truth.csv (status=success only) and blocks
    publishing to `domain` if it's already at or above `threshold`.
    """
    import csv as _csv
    import os as _os
    from urllib.parse import urlparse as _urlparse

    target = domain.lower().replace("www.", "")
    if "//" in target:
        target = _urlparse(target).netloc.lower().replace("www.", "")

    if not _os.path.exists(csv_path):
        return True, "concentration_gate: no truth CSV yet, allowing"

    total = 0
    domain_count = 0
    try:
        with open(csv_path, encoding="utf-8", errors="replace") as f:
            for row in _csv.DictReader(f):
                if row.get("status") != "success":
                    continue
                url = row.get("backlink_url", "")
                if not url:
                    continue
                d = _urlparse(url).netloc.lower().replace("www.", "")
                if not d:
                    continue
                total += 1
                if d == target:
                    domain_count += 1
    except Exception as e:
        return True, f"concentration_gate: read error ({e}), allowing"

    if total == 0:
        return True, "concentration_gate: empty portfolio, allowing"

    pct = domain_count / total
    if pct >= threshold:
        return False, (
            f"concentration_gate: {target} is already at {pct:.1%} of the clean portfolio "
            f"({domain_count}/{total}), at/above {threshold:.0%} cap — "
            f"publish to other domains to dilute (see CLAUDE.md section 4, reports/double_down_plan.md)"
        )
    return True, f"concentration_gate: {target} at {pct:.1%} ({domain_count}/{total}), under {threshold:.0%} cap"


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python humanize.py <file> <platform>")
        sys.exit(1)
    r = validate_file(sys.argv[1], sys.argv[2])
    print(report(r))
    sys.exit(0 if r.ok else 1)
