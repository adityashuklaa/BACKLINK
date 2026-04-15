"""Review all 50 backlinks — score, grade, recommend what to double down on."""
import csv
import requests

session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/125.0.0.0"})

with open("output/backlinks_log.csv", "r", encoding="utf-8", errors="replace") as f:
    rows = list(csv.DictReader(f))

success = [r for r in rows if r["status"] == "success" and r.get("backlink_url")]

print(f"REVIEWING ALL {len(success)} VERIFIED BACKLINKS")
print("=" * 80)

EXPERT_NAMES = ["Marcus Chen", "Sarah Mitchell", "David Park", "Rachel Torres",
    "Kevin Okafor", "Tom Bradley", "Lisa Chen", "Nina Rodriguez",
    "Priya Sharma", "Michael Brennan", "Anika Patel", "Raj Mehta"]

results = []

for r in success:
    url = r["backlink_url"]
    name = r["site_name"]
    notes = r.get("notes", "")

    if "dev.to" in url: platform = "Dev.to (DA 77)"
    elif "github.com" in url: platform = "GitHub (DA 100)"
    elif "telegra.ph" in url: platform = "Telegraph (DA 73)"
    elif "snippet" in url: platform = "Snippet.host (DA 40)"
    elif "paste2" in url: platform = "Paste2 (DA 55)"
    elif "debian" in url: platform = "Debian Paste (DA 70)"
    elif "centos" in url: platform = "CentOS Paste (DA 60)"
    elif "bpa.st" in url: platform = "BPA.st (DA 30)"
    elif "pastebin.fi" in url: platform = "Pastebin.fi (DA 28)"
    else: platform = "Other"

    try:
        resp = session.get(url, timeout=10)
        is_live = resp.status_code == 200
        has_vc = "vestacall" in resp.text.lower()
        content_len = len(resp.text)
        has_tables = "<table" in resp.text.lower() or "---|" in resp.text
        has_code = "<code" in resp.text.lower() or "```" in resp.text
        has_author = any(n in resp.text for n in EXPERT_NAMES)
        is_keyword = "keyword" in notes.lower()

        score = 0
        if is_live: score += 2
        if has_vc: score += 3
        if content_len > 8000: score += 3
        elif content_len > 4000: score += 2
        elif content_len > 2000: score += 1
        if has_tables: score += 1
        if has_code: score += 1
        if has_author: score += 1
        if is_keyword: score += 2
        if "Dev.to" in platform: score += 2
        if "GitHub" in platform: score += 1

        if score >= 11: grade = "A+"
        elif score >= 9: grade = "A"
        elif score >= 7: grade = "B"
        elif score >= 5: grade = "C"
        else: grade = "D"

        results.append({
            "url": url, "name": name, "platform": platform,
            "live": is_live, "has_vc": has_vc, "score": score, "grade": grade,
            "content_len": content_len, "has_tables": has_tables,
            "has_code": has_code, "has_author": has_author, "is_keyword": is_keyword
        })
    except Exception as e:
        results.append({
            "url": url, "name": name, "platform": platform,
            "live": False, "has_vc": False, "score": 0, "grade": "F",
            "content_len": 0, "has_tables": False, "has_code": False,
            "has_author": False, "is_keyword": False
        })

results.sort(key=lambda x: -x["score"])

# Print by grade
for grade in ["A+", "A", "B", "C", "D", "F"]:
    graded = [r for r in results if r["grade"] == grade]
    if not graded:
        continue
    print(f"\n=== GRADE {grade} ({len(graded)} backlinks) ===")
    for r in graded:
        tags = []
        if r["has_tables"]: tags.append("tables")
        if r["has_code"]: tags.append("code")
        if r["has_author"]: tags.append("expert-author")
        if r["is_keyword"]: tags.append("keyword")
        tag_str = " [" + ", ".join(tags) + "]" if tags else ""
        status = "LIVE+VC" if r["live"] and r["has_vc"] else "LIVE" if r["live"] else "DEAD"
        short_url = r["url"].replace("https://", "")[:60]
        print(f"  {status:7} score:{r['score']:2} | {r['platform']:20} | {short_url}{tag_str}")

# Platform summary
print("\n" + "=" * 80)
print("PLATFORM PERFORMANCE RANKING")
print("=" * 80)
platforms = {}
for r in results:
    p = r["platform"]
    if p not in platforms:
        platforms[p] = {"total": 0, "live_vc": 0, "scores": []}
    platforms[p]["total"] += 1
    if r["live"] and r["has_vc"]:
        platforms[p]["live_vc"] += 1
    platforms[p]["scores"].append(r["score"])

for p, v in sorted(platforms.items(), key=lambda x: -(sum(x[1]["scores"])/len(x[1]["scores"]))):
    avg = round(sum(v["scores"])/len(v["scores"]), 1)
    live_pct = round(v["live_vc"]/v["total"]*100)
    print(f"  {p:22} | {v['total']:2} links | {v['live_vc']:2} verified | {live_pct:3}% | avg score: {avg}")

# Recommendation
print("\n" + "=" * 80)
print("RECOMMENDATION: WHERE TO DOUBLE DOWN")
print("=" * 80)

best = sorted(platforms.items(), key=lambda x: -(sum(x[1]["scores"])/len(x[1]["scores"])))
print(f"\n  #1 BEST: {best[0][0]} — avg score {round(sum(best[0][1]['scores'])/len(best[0][1]['scores']), 1)}")
print(f"  #2 NEXT: {best[1][0]} — avg score {round(sum(best[1][1]['scores'])/len(best[1][1]['scores']), 1)}")
print(f"  #3 NEXT: {best[2][0]} — avg score {round(sum(best[2][1]['scores'])/len(best[2][1]['scores']), 1)}")

a_plus = [r for r in results if r["grade"] == "A+"]
a_grade = [r for r in results if r["grade"] == "A"]
print(f"\n  A+ content: {len(a_plus)} pieces")
for r in a_plus:
    print(f"    {r['url'][:75]}")
print(f"\n  A content: {len(a_grade)} pieces")
for r in a_grade:
    print(f"    {r['url'][:75]}")

low = [r for r in results if r["grade"] in ["D", "F"]]
print(f"\n  LOW QUALITY (D/F): {len(low)} pieces — consider removing or upgrading")
for r in low:
    print(f"    {r['grade']} | {r['platform']:20} | {r['url'][:55]}")
