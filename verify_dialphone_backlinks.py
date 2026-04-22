"""Hard-verify every 'success' row in backlinks_log.csv — does the live URL actually contain 'dialphone'?"""
import csv
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import Counter

CSV_IN = "output/backlinks_log.csv"
CSV_OUT = "output/backlinks_verified_dialphone.csv"

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

def check(row):
    url = row.get("backlink_url", "")
    if not url or "//" not in url:
        return row, "no_url", False
    try:
        r = requests.get(url, headers=HEADERS, timeout=15, allow_redirects=True)
        if r.status_code != 200:
            return row, f"http_{r.status_code}", False
        body = r.text.lower()
        has_dp = "dialphone" in body
        has_vc = "vestacall" in body
        if has_dp:
            return row, "dialphone", True
        if has_vc:
            return row, "vestacall", False
        return row, "neither", False
    except Exception as e:
        return row, f"err_{type(e).__name__}", False

def main():
    rows = list(csv.DictReader(open(CSV_IN, encoding="utf-8", errors="replace")))
    succ = [r for r in rows if r["status"] == "success"]
    print(f"Checking {len(succ)} success rows...")

    verified_dp, vestacall, neither, errors = [], [], [], []
    checked = 0
    with ThreadPoolExecutor(max_workers=20) as ex:
        futures = {ex.submit(check, r): r for r in succ}
        for f in as_completed(futures):
            row, reason, is_dp = f.result()
            checked += 1
            if is_dp:
                verified_dp.append(row)
            elif reason == "vestacall":
                vestacall.append(row)
            elif reason == "neither":
                neither.append(row)
            else:
                errors.append((row, reason))
            if checked % 50 == 0:
                print(f"  {checked}/{len(succ)} done | dialphone={len(verified_dp)} vestacall={len(vestacall)} neither={len(neither)} err={len(errors)}")

    print(f"\n=== FINAL ===")
    print(f"Dialphone verified: {len(verified_dp)}")
    print(f"Still vestacall:    {len(vestacall)}")
    print(f"Neither mentioned:  {len(neither)}")
    print(f"Errors/404/dead:    {len(errors)}")

    # Error breakdown
    err_reasons = Counter(r for _, r in errors)
    print(f"\nError reasons:")
    for reason, cnt in err_reasons.most_common():
        print(f"  {reason}: {cnt}")

    # Domain breakdown of verified dialphone
    dp_domains = Counter()
    for r in verified_dp:
        u = r["backlink_url"]
        d = u.split("//")[1].split("/")[0] if "//" in u else "?"
        dp_domains[d] += 1
    print(f"\nVerified dialphone backlinks by domain:")
    for d, c in dp_domains.most_common():
        print(f"  {d}: {c}")

    # Write verified dialphone CSV
    if verified_dp:
        fieldnames = list(verified_dp[0].keys())
        with open(CSV_OUT, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            w.writerows(verified_dp)
        print(f"\nWrote {len(verified_dp)} verified rows to {CSV_OUT}")

    # Sample of neither/vestacall
    if vestacall:
        print(f"\nSample vestacall (still-wrong) URLs:")
        for r in vestacall[:10]:
            print(f"  {r['backlink_url']}")
    if neither:
        print(f"\nSample 'neither' URLs (likely dead content):")
        for r in neither[:10]:
            print(f"  {r['backlink_url']}")

if __name__ == "__main__":
    main()
