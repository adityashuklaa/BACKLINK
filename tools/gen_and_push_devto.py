"""Generate niche content and push to Dev.to (paced for Dev.to rate limits)."""
import csv
import json
import sys
import time
from datetime import datetime

import requests

sys.path.insert(0, ".")
sys.stdout.reconfigure(encoding="utf-8")

from core.humanize import validate, concentration_gate
from tools.gen_and_push import NICHES, make_article, slugify

CFG = json.load(open("config.json"))
DEVTO_KEY = CFG["api_keys"]["devto"]


def existing_devto_titles():
    titles = set()
    page = 1
    while True:
        r = requests.get(
            f"https://dev.to/api/articles?username=dialphonelimited&page={page}&per_page=100",
            headers={"api-key": DEVTO_KEY},
            timeout=15,
        )
        if not r.ok or not r.json():
            break
        for a in r.json():
            titles.add(a["title"].lower().strip())
        if len(r.json()) < 100:
            break
        page += 1
    return titles


def publish(title, body_md):
    r = requests.post(
        "https://dev.to/api/articles",
        headers={"api-key": DEVTO_KEY, "Content-Type": "application/json"},
        json={
            "article": {
                "title": title,
                "body_markdown": body_md,
                "published": True,
                "tags": ["voip", "business", "productivity", "smallbusiness"],
            }
        },
        timeout=30,
    )
    return r


def csv_log(site, url, status, notes):
    with open("output/backlinks_log.csv", "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=["date", "strategy", "site_name", "url_submitted", "backlink_url", "status", "notes"],
        )
        w.writerow(
            {
                "date": datetime.now().isoformat(),
                "strategy": "devto-niche",
                "site_name": site,
                "url_submitted": "devto-api",
                "backlink_url": url,
                "status": status,
                "notes": notes,
            }
        )


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--count", type=int, default=10)
    ap.add_argument("--sleep", type=int, default=35, help="Dev.to rate limit is ~30s; keep >=35 to be safe")
    args = ap.parse_args()

    ok, reason = concentration_gate("dev.to")
    if not ok:
        print(f"ABORT: {reason}")
        return 1
    print(f"dev.to: {reason}")

    seen = existing_devto_titles()
    print(f"[info] {len(seen)} existing Dev.to articles")

    pushed = 0
    skipped = 0
    failed = 0

    for industry, noun, detail in NICHES:
        if pushed >= args.count:
            break
        title, body = make_article(industry, noun, detail)
        if title.lower().strip() in seen:
            skipped += 1
            continue
        # Humanize check — niche content should pass
        r = validate(body, "devto")
        if not r.ok:
            print(f"  [humanize fail] {title[:60]} — {r.issues[:2]}")
            failed += 1
            continue

        print(f"\n[{pushed+1}/{args.count}] {title[:75]}")
        try:
            resp = publish(title, body)
            if resp.status_code == 201:
                url = resp.json().get("url", "")
                print(f"  ✓ {url}")
                csv_log(f"DevTo-niche-{slugify(title)[:40]}", url, "success", "DA 77 DOFOLLOW — niche content")
                pushed += 1
                seen.add(title.lower().strip())
            elif resp.status_code == 429:
                print(f"  rate-limited, waiting 60s")
                time.sleep(60)
                failed += 1
            else:
                print(f"  ✗ {resp.status_code}: {resp.text[:150]}")
                failed += 1
        except Exception as e:
            print(f"  EXC: {e}")
            failed += 1

        if pushed < args.count:
            time.sleep(args.sleep)

    print(f"\n=== DONE ===")
    print(f"Pushed:  {pushed}")
    print(f"Skipped: {skipped}")
    print(f"Failed:  {failed}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
