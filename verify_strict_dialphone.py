"""Stricter verification: does the page contain an ACTUAL link to dialphone.com?"""
import csv
import re
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import Counter

CSV_IN = "output/backlinks_verified_dialphone.csv"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

# Patterns that prove an actual backlink exists
LINK_PATTERNS = [
    re.compile(r'https?://(?:www\.)?dialphone\.com', re.I),
    re.compile(r'href=["\'][^"\']*dialphone\.com', re.I),
]

def check(row):
    url = row["backlink_url"]
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        if r.status_code != 200:
            return url, f"http_{r.status_code}", 0
        body = r.text
        # Count actual link occurrences
        link_count = len(LINK_PATTERNS[0].findall(body))
        has_href = bool(LINK_PATTERNS[1].search(body))
        mere_mention = "dialphone" in body.lower() and link_count == 0
        if has_href or link_count > 0:
            return url, "real_link", link_count
        if mere_mention:
            return url, "word_only_no_link", 0
        return url, "nothing", 0
    except Exception as e:
        return url, f"err_{type(e).__name__}", 0

def main():
    rows = list(csv.DictReader(open(CSV_IN, encoding="utf-8", errors="replace")))
    # Dedupe by URL
    seen = {}
    for r in rows:
        seen[r["backlink_url"]] = r
    unique_rows = list(seen.values())
    print(f"Checking {len(unique_rows)} unique verified URLs for REAL dialphone.com links...")

    results = {"real_link": [], "word_only_no_link": [], "nothing": [], "error": []}
    checked = 0
    with ThreadPoolExecutor(max_workers=20) as ex:
        futs = {ex.submit(check, r): r for r in unique_rows}
        for f in as_completed(futs):
            url, reason, cnt = f.result()
            checked += 1
            if reason == "real_link":
                results["real_link"].append((url, cnt))
            elif reason == "word_only_no_link":
                results["word_only_no_link"].append(url)
            elif reason == "nothing":
                results["nothing"].append(url)
            else:
                results["error"].append((url, reason))
            if checked % 100 == 0:
                print(f"  {checked}/{len(unique_rows)}")

    print(f"\n=== STRICT VERIFICATION ===")
    print(f"Real link to dialphone.com:       {len(results['real_link'])}")
    print(f"Word 'dialphone' only, no link:   {len(results['word_only_no_link'])}")
    print(f"Nothing (shouldn't happen):       {len(results['nothing'])}")
    print(f"Errors/404:                       {len(results['error'])}")

    # Breakdown by domain for real links
    real_domains = Counter()
    for u, _ in results["real_link"]:
        d = u.split("//")[1].split("/")[0]
        if "github" in d and "gist" not in d: d = "github.com"
        real_domains[d] += 1
    print(f"\nReal dialphone.com backlinks by domain:")
    for d, c in real_domains.most_common():
        print(f"  {d}: {c}")

    # Errors breakdown
    if results["error"]:
        err_counts = Counter(r for _, r in results["error"])
        print(f"\nError types:")
        for r, c in err_counts.most_common():
            print(f"  {r}: {c}")

    # Write final truth CSV
    real_url_set = set(u for u, _ in results["real_link"])
    final = [r for r in unique_rows if r["backlink_url"] in real_url_set]
    with open("output/backlinks_final_truth.csv", "w", newline="", encoding="utf-8") as f:
        if final:
            w = csv.DictWriter(f, fieldnames=list(final[0].keys()))
            w.writeheader()
            w.writerows(final)
    print(f"\nFinal truth file: {len(final)} real dialphone.com backlinks written to output/backlinks_final_truth.csv")

if __name__ == "__main__":
    main()
