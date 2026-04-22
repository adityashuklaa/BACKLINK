"""Hard-verify each success URL actually contains a dialphone.com link (not just brand mention).

Writes output/backlinks_link_audit.csv with columns:
  url, domain, status (live|dead|err), dialphone_com_count, note

Use this to classify rows accurately and prune false-positive "clean" backlinks.
"""
import csv
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse

import requests

sys.stdout.reconfigure(encoding="utf-8")

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/131.0 Safari/537.36"}
TIMEOUT = 15

# Quora + Hashnode + some others get 403 to headless requests but still have links via API.
# We skip them here and trust the separate API-based check.
KNOWN_BOT_BLOCKED = {"quora.com", "hashnode.dev"}


def check(url):
    domain = urlparse(url).netloc.lower().replace("www.", "")
    if any(b in domain for b in KNOWN_BOT_BLOCKED):
        return url, domain, "skip_bot_blocked", 0, "checked via API elsewhere"
    try:
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT, allow_redirects=True)
        if r.status_code != 200:
            return url, domain, f"http_{r.status_code}", 0, ""
        html = r.text
        count = len(re.findall(r"dialphone\.com", html, re.I))
        return url, domain, "live", count, "has_link" if count > 0 else "no_link"
    except Exception as e:
        return url, domain, "err", 0, f"{type(e).__name__}"


def main():
    rows = []
    with open("output/backlinks_final_truth.csv", encoding="utf-8", errors="replace") as f:
        for r in csv.DictReader(f):
            if r.get("status") == "success":
                rows.append(r["backlink_url"])

    print(f"Auditing {len(rows)} URLs...")
    results = []
    done = 0
    with ThreadPoolExecutor(max_workers=20) as ex:
        futures = {ex.submit(check, u): u for u in rows}
        for f in as_completed(futures):
            results.append(f.result())
            done += 1
            if done % 25 == 0:
                print(f"  {done}/{len(rows)}")

    with open("output/backlinks_link_audit.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["url", "domain", "status", "dialphone_com_count", "note"])
        w.writerows(results)

    from collections import Counter
    by_status = Counter(r[2] for r in results)
    by_has_link = Counter()
    for _, d, s, c, _n in results:
        if s == "live":
            by_has_link[d + (" [link]" if c > 0 else " [no link]")] += 1
        elif s == "skip_bot_blocked":
            by_has_link[d + " [bot-blocked]"] += 1

    print(f"\n=== STATUS SUMMARY ===")
    for s, c in by_status.most_common():
        print(f"  {s:25s} {c}")

    print(f"\n=== DOMAIN × LINK PRESENCE ===")
    for k, c in sorted(by_has_link.items()):
        print(f"  {k:45s} {c}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
