"""v2 strict verification — handles GitLab/Codeberg (fetch raw README) and Dev.to (use /feed or raw page)."""
import csv
import re
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import Counter

CSV_IN = "output/backlinks_verified_dialphone.csv"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

LINK_RE = re.compile(r'https?://(?:www\.)?dialphone\.com', re.I)

def fetch_url_for_verification(url):
    """Return the URL we should actually fetch to see the real content."""
    # GitLab: fetch raw README instead of rendered landing page
    if "gitlab.com/" in url and "/-/" not in url and "-/blob" not in url:
        parts = url.rstrip("/").split("gitlab.com/")
        if len(parts) == 2:
            return f"https://gitlab.com/{parts[1]}/-/raw/main/README.md"
    # Codeberg: same pattern
    if "codeberg.org/" in url and "/raw/" not in url and "src/" not in url:
        parts = url.rstrip("/").split("codeberg.org/")
        if len(parts) == 2:
            return f"https://codeberg.org/{parts[1]}/raw/branch/main/README.md"
    # GitHub: raw readme
    if "github.com/" in url and "/blob/" not in url and "raw.githubusercontent" not in url:
        parts = url.rstrip("/").split("github.com/")
        if len(parts) == 2 and "/" in parts[1]:
            return f"https://raw.githubusercontent.com/{parts[1]}/main/README.md"
    return url

def check(row):
    url = row["backlink_url"]
    fetch_url = fetch_url_for_verification(url)
    try:
        r = requests.get(fetch_url, headers=HEADERS, timeout=15)
        if r.status_code != 200:
            # try master branch instead of main
            if "/main/" in fetch_url or "/branch/main/" in fetch_url:
                fetch_url2 = fetch_url.replace("/main/", "/master/").replace("/branch/main/", "/branch/master/")
                r2 = requests.get(fetch_url2, headers=HEADERS, timeout=10)
                if r2.status_code == 200:
                    r = r2
                else:
                    return url, f"http_{r.status_code}", 0
            else:
                return url, f"http_{r.status_code}", 0
        body = r.text
        links = LINK_RE.findall(body)
        if links:
            return url, "real_link", len(links)
        if "dialphone" in body.lower():
            return url, "word_only_no_link", 0
        return url, "nothing", 0
    except Exception as e:
        return url, f"err_{type(e).__name__}", 0

def main():
    rows = list(csv.DictReader(open(CSV_IN, encoding="utf-8", errors="replace")))
    seen = {}
    for r in rows:
        seen[r["backlink_url"]] = r
    unique_rows = list(seen.values())
    print(f"v2 strict checking {len(unique_rows)} unique URLs...")

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

    print(f"\n=== FINAL TRUTH ===")
    print(f"Real clickable link to dialphone.com:  {len(results['real_link'])}")
    print(f"Word only (no real link):              {len(results['word_only_no_link'])}")
    print(f"Nothing:                               {len(results['nothing'])}")
    print(f"Errors:                                {len(results['error'])}")

    real_domains = Counter()
    for u, _ in results["real_link"]:
        d = u.split("//")[1].split("/")[0]
        if "github" in d and "gist" not in d: d = "github.com"
        real_domains[d] += 1
    print(f"\nReal dialphone.com backlinks by domain:")
    for d, c in real_domains.most_common():
        print(f"  {d}: {c}")

    if results["word_only_no_link"]:
        by_domain = Counter()
        for u in results["word_only_no_link"]:
            d = u.split("//")[1].split("/")[0]
            by_domain[d] += 1
        print(f"\nWord-only (no link) by domain:")
        for d, c in by_domain.most_common():
            print(f"  {d}: {c}")

    if results["error"]:
        err_counts = Counter(r for _, r in results["error"])
        print(f"\nErrors:")
        for r, c in err_counts.most_common():
            print(f"  {r}: {c}")

    # Final truth CSV
    real_urls = set(u for u, _ in results["real_link"])
    final = [r for r in unique_rows if r["backlink_url"] in real_urls]
    with open("output/backlinks_final_truth.csv", "w", newline="", encoding="utf-8") as f:
        if final:
            w = csv.DictWriter(f, fieldnames=list(final[0].keys()))
            w.writeheader()
            w.writerows(final)
    print(f"\n{len(final)} real backlinks written to output/backlinks_final_truth.csv")

if __name__ == "__main__":
    main()
