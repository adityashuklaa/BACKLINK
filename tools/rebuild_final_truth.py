"""Rebuild output/backlinks_final_truth.csv from output/backlinks_log.csv.

Deduplicates by URL (keeping highest-priority status), applies spam_quarantined
for any success row pointing to a blocked paste-site domain, and writes the
clean + quarantined rows to the final truth CSV.

Run after any batch publish or manual CSV edits so the concentration gate reads
accurate counts.
"""
import csv
import sys
from collections import Counter
from urllib.parse import urlparse

sys.stdout.reconfigure(encoding="utf-8")

BLOCKED_HIGH_SPAM_DOMAINS = {
    "paste.rs", "friendpaste.com", "godbolt.org", "termbin.com", "ideone.com",
    "bpa.st", "paste2.org", "snippet.host", "pastebin.fi", "dpaste.com", "glot.io",
}

# Manual overrides (no_link, spam_quarantined) beat success if both exist for same URL.
STATUS_PRIORITY = {
    "no_link": 7,             # audit-confirmed page has no dialphone.com link — not a real backlink
    "spam_quarantined": 6,    # domain is in blocked spam list
    "success": 5,
    "unverified": 4,
    "pending": 3,
    "dead": 2,
    "failed": 1,
}

LOG_PATH = "output/backlinks_log.csv"
OUT_PATH = "output/backlinks_final_truth.csv"
FIELDS = ["date", "strategy", "site_name", "url_submitted", "backlink_url", "status", "notes"]


def main():
    url_best = {}
    with open(LOG_PATH, encoding="utf-8", errors="replace") as f:
        for row in csv.DictReader(f):
            url = row.get("backlink_url", "").strip()
            if not url or "//" not in url:
                continue
            s = (row.get("status") or "").lower()
            pr = STATUS_PRIORITY.get(s, 0)
            cur = url_best.get(url)
            cur_pr = STATUS_PRIORITY.get((cur.get("status") or "").lower(), -1) if cur else -1
            if pr > cur_pr:
                url_best[url] = row

    success_rows, quarantined_rows = [], []
    for url, row in url_best.items():
        status = (row.get("status") or "").lower()
        d = urlparse(url).netloc.lower().replace("www.", "")
        if status == "spam_quarantined":
            quarantined_rows.append((url, row))
        elif status == "success":
            if d in BLOCKED_HIGH_SPAM_DOMAINS:
                row["status"] = "spam_quarantined"
                quarantined_rows.append((url, row))
            else:
                success_rows.append((url, row))

    # Write
    with open(OUT_PATH, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        for _, row in success_rows:
            w.writerow({k: row.get(k, "") for k in FIELDS})
        for _, row in quarantined_rows:
            w.writerow({k: row.get(k, "") for k in FIELDS})

    # Report
    dom = Counter()
    for url, _ in success_rows:
        d = urlparse(url).netloc.lower().replace("www.", "")
        dom[d] += 1
    total = sum(dom.values())

    print(f"Wrote {OUT_PATH}: {len(success_rows)} success + {len(quarantined_rows)} quarantined")
    print(f"Referring domains: {len(dom)}")
    print()
    for d, c in dom.most_common():
        print(f"  {d:35s} {c:4d}  {100*c/total:5.1f}%")
    return 0


if __name__ == "__main__":
    sys.exit(main())
