"""Generate Google Search Console disavow.txt for high-spam-score backlinks.

Google Search Console accepts a text file listing URLs or whole domains to ignore
when evaluating our site's backlink profile. This is the standard remediation for
legacy spam links we can't delete at the source.

Format: https://support.google.com/webmasters/answer/2648487
- Comments start with #
- One URL per line, OR
- domain:example.com to disavow everything from a domain
"""
import csv
import sys
from collections import Counter

sys.path.insert(0, ".")
from dashboard.dialphone_dashboard import SPAM_SCORES, _spam_tier

MASTER = "output/backlinks_log.csv"
OUT = "output/disavow.txt"

# Domains where we want to disavow the whole domain (not URL-by-URL)
# because EVERY link we have there is garbage
WHOLE_DOMAIN_DISAVOW = {
    "paste.rs",        # all 107 links are high-spam, no way to remove individually
    "friendpaste.com", # same, anonymous pastes, permanent
    "godbolt.org",     # URL shortener, permanent, only 3 but all junk
    "termbin.com",     # netcat paste, permanent
    "ideone.com",      # low quality UGC
    "bpa.st",          # anonymous paste
    "paste2.org",      # anonymous paste
    "snippet.host",    # UGC, thin
    "pastebin.fi",     # anonymous paste
    "dpaste.com",      # pastes expire in 24h anyway
}

# Domains where we want URL-level disavow (keep some, drop the rest)
URL_LEVEL_DISAVOW = {
    "glot.io",          # we have an account, 40+ duplicate posts damaged the whole class
}


def main():
    rows = list(csv.DictReader(open(MASTER, encoding="utf-8", errors="replace")))
    succ = [r for r in rows if r.get("status") == "success"]

    by_domain = Counter()
    per_url_to_disavow = []
    seen = set()

    for r in succ:
        url = r.get("backlink_url", "")
        if not url or url in seen or "//" not in url:
            continue
        seen.add(url)
        domain = url.split("//")[1].split("/")[0]
        if "github" in domain and "gist" not in domain:
            domain = "github.com"
        by_domain[domain] += 1

        if domain in URL_LEVEL_DISAVOW:
            per_url_to_disavow.append(url)

    # Build the output
    lines = [
        "# Disavow file for dialphone.com",
        "# Generated 2026-04-18",
        "# Upload at: https://search.google.com/search-console/disavow-links",
        "#",
        "# RATIONALE — see reports/backlink_seo_audit.md and reports/root_cause_spam.md",
        "# We built automation on paste/code-dump sites before realising Google devalues them.",
        "# Total links to disavow: {} domains + {} individual URLs".format(
            len([d for d in WHOLE_DOMAIN_DISAVOW if by_domain.get(d, 0) > 0]),
            len(per_url_to_disavow),
        ),
        "",
        "# === WHOLE-DOMAIN DISAVOWS (anonymous pastes, link-farm-pattern UGC) ===",
    ]

    total_whole_domain_links = 0
    for d in sorted(WHOLE_DOMAIN_DISAVOW):
        count = by_domain.get(d, 0)
        if count > 0:
            lines.append(f"# {d} — {count} links, all high-spam-score per internal audit")
            lines.append(f"domain:{d}")
            total_whole_domain_links += count

    lines.extend([
        "",
        f"# === URL-LEVEL DISAVOWS ({len(per_url_to_disavow)} URLs) ===",
        "# These come from domains that ARE legitimate in other contexts but our specific",
        "# posts damaged the link profile (duplicate content, velocity abuse).",
    ])
    for u in sorted(per_url_to_disavow):
        lines.append(u)

    lines.extend([
        "",
        f"# Total links disavowed: {total_whole_domain_links + len(per_url_to_disavow)}",
        f"# Total backlinks in CSV: {sum(by_domain.values())}",
        f"# Disavow share: {(total_whole_domain_links + len(per_url_to_disavow)) / sum(by_domain.values()) * 100:.1f}%",
    ])

    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines))

    print(f"Wrote {OUT}")
    print(f"Whole-domain disavows: {sum(1 for d in WHOLE_DOMAIN_DISAVOW if by_domain.get(d, 0) > 0)}")
    print(f"URL-level disavows: {len(per_url_to_disavow)}")
    print(f"Total links covered: {total_whole_domain_links + len(per_url_to_disavow)}")
    print(f"Upload at: https://search.google.com/search-console/disavow-links")


if __name__ == "__main__":
    main()
