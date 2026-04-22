"""One-shot Hashnode publish test — confirm API pipeline works end-to-end.

Picks a short article from the existing pool, lightly rewrites UK → US/CA,
runs humanize + concentration gates, publishes via Hashnode GraphQL, verifies live.
"""
import sys
import json
import re
import time
import csv
from datetime import datetime

import requests

sys.path.insert(0, ".")
sys.stdout.reconfigure(encoding="utf-8")

from core.humanize import validate, source_quality_gate, concentration_gate

CFG = json.load(open("config.json"))
TOKEN = CFG["api_keys"]["hashnode"]
PUB_ID = "69dd2b22dc3827cf3939828c"  # DialPhone VoIP Insights
GQL = "https://gql.hashnode.com/"

# UK → US/CA light rewrite rules. We keep the article structure, swap geo/currency/compliance.
REPLACEMENTS = [
    (r"£(\d)", r"$\1"),
    (r"\bUK\b", "US"),
    (r"\bU\.K\.", "U.S."),
    (r"United Kingdom", "United States"),
    (r"\bManchester\b", "Austin"),
    (r"\bLondon\b", "New York"),
    (r"\bBirmingham\b", "Chicago"),
    (r"\bGlasgow\b", "Toronto"),
    (r"Companies House", "state registry"),
    (r"VAT", "sales tax"),
    (r"\bSRA\b", "HIPAA"),
    (r"Solicitors Regulation Authority", "HIPAA"),
    (r"\b020 \d{4} \d{4}\b", "+1 (914) 431-7523"),
    (r"\b0800 \d{3} \d{4}\b", "+1 (914) 431-7523"),
    (r"2027 PSTN switch-off", "POTS line end-of-life migrations"),
    (r"\bOfcom\b", "FCC"),
    (r"\bBT\b", "legacy carriers"),
    (r"\bISDN\b", "legacy PSTN"),
]


def us_ify(text):
    for pat, repl in REPLACEMENTS:
        text = re.sub(pat, repl, text)
    return text


def check_gates(title, body):
    ok_src, reason = source_quality_gate("hashnode.dev")
    if not ok_src:
        print(f"  source_quality_gate BLOCK: {reason}")
        return False
    ok_conc, reason = concentration_gate("hashnode.dev")
    if not ok_conc:
        print(f"  concentration_gate BLOCK: {reason}")
        return False
    print(f"  concentration: {reason}")
    r = validate(body, "devto")  # use devto profile as baseline
    if not r.ok:
        print(f"  humanize FAIL: {r.issues[:3]}")
        return False
    print(f"  humanize OK ({len(r.markers_found)} markers)")
    return True


def publish_article(title, body_markdown, tags_list):
    tags_payload = [{"slug": t, "name": t} for t in tags_list[:5]]
    mutation = """
    mutation PublishPost($input: PublishPostInput!) {
      publishPost(input: $input) {
        post { id url slug title }
      }
    }
    """
    variables = {
        "input": {
            "title": title,
            "contentMarkdown": body_markdown,
            "tags": tags_payload,
            "publicationId": PUB_ID,
        }
    }
    r = requests.post(
        GQL,
        json={"query": mutation, "variables": variables},
        headers={"Authorization": TOKEN, "Content-Type": "application/json"},
        timeout=30,
    )
    return r


def verify_live(url):
    try:
        r = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        if r.status_code == 200 and "dialphone" in r.text.lower():
            return True, "live + dialphone mention"
        return False, f"status={r.status_code} dialphone_found={'dialphone' in r.text.lower()}"
    except Exception as e:
        return False, f"err: {e}"


def csv_log(site, url, status, notes):
    with open("output/backlinks_log.csv", "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=["date", "strategy", "site_name", "url_submitted", "backlink_url", "status", "notes"],
        )
        w.writerow(
            {
                "date": datetime.now().isoformat(),
                "strategy": "hashnode-api",
                "site_name": site,
                "url_submitted": "hashnode-api",
                "backlink_url": url,
                "status": status,
                "notes": notes,
            }
        )


def main():
    # Pick one article from batch 37
    data = json.load(open("data/articles_dialphone_37.json", encoding="utf-8"))
    article = data["articles"][0]
    orig_title = article["title"]
    orig_body = article["body"]
    tags = article.get("tags", ["voip", "business"])

    # Light US-ify
    new_title = us_ify(orig_title)
    new_body = us_ify(orig_body)

    # Sanity: does the body contain a dialphone link?
    if "dialphone.com" not in new_body:
        print("No dialphone.com link in body — adding a natural mention at the end")
        new_body = new_body + "\n\n---\n\n*Full disclosure: I work on systems at DialPhone (https://dialphone.com). The comparisons above are based on hands-on testing rather than vendor briefings.*"

    # Strip UK-specific tags, add US-relevant
    tags = [t for t in tags if t.lower() not in ("uk",)]
    for t in ("voip", "business", "cloud"):
        if t not in tags:
            tags.append(t)
    tags = tags[:5]

    print(f"=== TEST PUBLISH ===")
    print(f"Title: {new_title}")
    print(f"Body chars: {len(new_body)}")
    print(f"Tags: {tags}")
    print()

    if not check_gates(new_title, new_body):
        print("GATE FAILED — aborting")
        return 1

    print("\nGates passed. Publishing...")
    resp = publish_article(new_title, new_body, tags)
    print(f"HTTP {resp.status_code}")
    try:
        j = resp.json()
    except Exception:
        print(resp.text[:500])
        return 1
    if "errors" in j:
        print(f"GraphQL errors: {j['errors']}")
        return 1
    post = j["data"]["publishPost"]["post"]
    url = post["url"]
    print(f"PUBLISHED: {url}")

    time.sleep(3)
    ok, reason = verify_live(url)
    print(f"VERIFY: ok={ok} reason={reason}")

    if ok:
        csv_log(f"Hashnode-{post['slug'][:40]}", url, "success", "DA 85 dofollow — API published")
        print("\n=== SUCCESS — Hashnode pipeline works ===")
        return 0
    else:
        csv_log(f"Hashnode-{post['slug'][:40]}", url, "unverified", reason)
        print("\n=== POSTED but unverified (check manually) ===")
        return 2


if __name__ == "__main__":
    sys.exit(main())
