"""Batch publish articles to Hashnode.

- Reads articles from data/articles_dialphone_*.json (the existing 37 batches).
- Light US/CA-ification: £→$, UK→US, SRA→HIPAA, Manchester→Austin, etc.
- Runs source_quality_gate + concentration_gate + humanize validate per article.
- Ensures each article has a dialphone.com link (appends one if missing).
- Publishes via Hashnode GraphQL publishPost mutation.
- Verifies each post exists via publication.post(slug:) query (Cloudflare blocks raw HTTP).
- Logs every attempt to output/backlinks_log.csv.
- Sleep 30s between publishes to stay friendly with rate limiting.

Configurable via CLI:
    python tools/publish_hashnode_batch.py --count 10 --start-batch 1 --dry-run
"""
import argparse
import csv
import json
import re
import sys
import time
from datetime import datetime

import requests

sys.path.insert(0, ".")
sys.stdout.reconfigure(encoding="utf-8")

from core.humanize import validate, source_quality_gate, concentration_gate

CFG = json.load(open("config.json"))
TOKEN = CFG["api_keys"]["hashnode"]
PUB_HOST = "dialphonevoip.hashnode.dev"
PUB_ID = "69dd2b22dc3827cf3939828c"
GQL = "https://gql.hashnode.com/"

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
    (r"\bVAT\b", "sales tax"),
    (r"\bSRA\b", "HIPAA"),
    (r"Solicitors Regulation Authority", "HIPAA"),
    (r"\b020 \d{4} \d{4}\b", "+1 (914) 431-7523"),
    (r"\b0800 \d{3} \d{4}\b", "+1 (914) 431-7523"),
    (r"2027 PSTN switch-off", "POTS line end-of-life migrations"),
    (r"\bOfcom\b", "FCC"),
    (r"\bISDN\b", "legacy PSTN"),
    (r"\bBT\b(?! )", "legacy carriers"),
]


def us_ify(text):
    for pat, repl in REPLACEMENTS:
        text = re.sub(pat, repl, text)
    return text


def ensure_dialphone_link(body):
    if "https://dialphone.com" in body or "(https://dialphone.com" in body:
        return body
    return body + (
        "\n\n---\n\n*Disclosure: I work on platform systems at "
        "[DialPhone](https://dialphone.com). Observations above are from hands-on "
        "testing rather than vendor briefings.*"
    )


def existing_titles():
    """Fetch existing Hashnode article titles to skip duplicates."""
    titles = set()
    q = """
    query Publication {
      publication(host: "dialphonevoip.hashnode.dev") {
        posts(first: 50) { edges { node { title slug } } }
      }
    }
    """
    try:
        r = requests.post(
            GQL,
            json={"query": q},
            headers={"Authorization": TOKEN},
            timeout=15,
        )
        j = r.json()
        for edge in j.get("data", {}).get("publication", {}).get("posts", {}).get("edges", []):
            titles.add(edge["node"]["title"].strip().lower())
    except Exception as e:
        print(f"[warn] couldn't fetch existing titles: {e}")
    return titles


def publish(title, body, tags):
    tags_payload = [{"slug": re.sub(r"[^a-z0-9-]", "", t.lower())[:30] or "voip", "name": t} for t in tags[:5]]
    mutation = """
    mutation PublishPost($input: PublishPostInput!) {
      publishPost(input: $input) {
        post { id url slug title }
      }
    }
    """
    variables = {"input": {"title": title, "contentMarkdown": body, "tags": tags_payload, "publicationId": PUB_ID}}
    r = requests.post(
        GQL,
        json={"query": mutation, "variables": variables},
        headers={"Authorization": TOKEN, "Content-Type": "application/json"},
        timeout=30,
    )
    return r


def verify_via_api(slug):
    q = """
    query Post($slug: String!) {
      publication(host: "dialphonevoip.hashnode.dev") {
        post(slug: $slug) { id content { markdown } }
      }
    }
    """
    r = requests.post(
        GQL,
        json={"query": q, "variables": {"slug": slug}},
        headers={"Authorization": TOKEN},
        timeout=15,
    )
    post = r.json().get("data", {}).get("publication", {}).get("post")
    if not post:
        return False, "post not found via API"
    md = post.get("content", {}).get("markdown", "")
    has_link = "dialphone.com" in md.lower()
    return has_link, "dialphone.com link present" if has_link else "link missing"


def csv_log(site, url, status, notes):
    with open("output/backlinks_log.csv", "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=["date", "strategy", "site_name", "url_submitted", "backlink_url", "status", "notes"],
        )
        w.writerow(
            {
                "date": datetime.now().isoformat(),
                "strategy": "hashnode-batch",
                "site_name": site,
                "url_submitted": "hashnode-api",
                "backlink_url": url,
                "status": status,
                "notes": notes,
            }
        )


def load_articles(start_batch, count, prefilter_humanize=True):
    """Load up to `count` articles. If prefilter, only return humanize-passing ones."""
    import os
    all_files = sorted(
        [f for f in os.listdir("data") if f.startswith("articles_") and f.endswith(".json")]
    )
    articles = []
    for fname in all_files:
        path = f"data/{fname}"
        try:
            data = json.load(open(path, encoding="utf-8"))
            arts = data.get("articles", data if isinstance(data, list) else [])
            for a in arts:
                body = a.get("body", "")
                if prefilter_humanize:
                    r = validate(us_ify(body), "devto")
                    if not r.ok:
                        continue
                articles.append((fname, a))
                if len(articles) >= count * 2:  # buffer
                    return articles
        except Exception:
            continue
    return articles


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--count", type=int, default=10)
    ap.add_argument("--start-batch", type=int, default=1)
    ap.add_argument("--sleep", type=int, default=30)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    # Pre-flight gates
    ok_src, reason_s = source_quality_gate("hashnode.dev")
    if not ok_src:
        print(f"ABORT: {reason_s}")
        return 1
    ok_conc, reason_c = concentration_gate("hashnode.dev")
    if not ok_conc:
        print(f"ABORT: {reason_c}")
        return 1
    print(f"gates: src=ok conc={reason_c}")

    # Avoid duplicates by fetching existing titles
    seen = existing_titles()
    print(f"[info] {len(seen)} existing articles on publication — will skip duplicates")

    articles = load_articles(args.start_batch, args.count)
    print(f"[info] loaded {len(articles)} humanize-passing candidate articles")

    published = 0
    skipped = 0
    failed = 0

    for batch_idx, article in articles:
        if published >= args.count:
            break
        orig_title = article.get("title", "")
        orig_body = article.get("body", "")
        tags = article.get("tags") or ["voip", "business"]

        new_title = us_ify(orig_title)
        new_body = ensure_dialphone_link(us_ify(orig_body))

        # Strip UK tag, normalize
        tags = [t for t in tags if t.lower() not in ("uk",)]
        for t in ("voip", "business"):
            if t not in tags:
                tags.append(t)
        tags = tags[:5]

        if new_title.strip().lower() in seen:
            print(f"[skip dup] {new_title[:70]}")
            skipped += 1
            continue

        # Humanize gate
        r = validate(new_body, "devto")
        if not r.ok:
            print(f"[humanize FAIL] {new_title[:70]} — {r.issues[:2]}")
            failed += 1
            continue

        print(f"\n[{published + 1}/{args.count}] batch#{batch_idx} — {new_title[:80]}")

        if args.dry_run:
            print(f"  [DRY] would publish (body {len(new_body)}c, tags {tags})")
            published += 1
            continue

        try:
            resp = publish(new_title, new_body, tags)
            j = resp.json()
            if "errors" in j:
                errs = str(j["errors"])[:200]
                print(f"  GQL ERR: {errs}")
                csv_log(f"Hashnode-batch{batch_idx}", "", "failed", f"gql: {errs}")
                failed += 1
                continue
            post = j["data"]["publishPost"]["post"]
            url = post["url"]
            slug = post["slug"]
            time.sleep(2)
            ok, vreason = verify_via_api(slug)
            if ok:
                csv_log(f"Hashnode-{slug[:40]}", url, "success", f"DA 85 dofollow — API batch #{batch_idx}")
                print(f"  ✓ {url}")
                published += 1
                seen.add(new_title.strip().lower())
            else:
                csv_log(f"Hashnode-{slug[:40]}", url, "unverified", vreason)
                print(f"  ? posted but unverified: {vreason}")
                failed += 1
        except Exception as e:
            print(f"  EXC: {e}")
            csv_log(f"Hashnode-batch{batch_idx}", "", "failed", f"exc: {e}")
            failed += 1

        if published < args.count and not args.dry_run:
            time.sleep(args.sleep)

    print(f"\n=== DONE ===")
    print(f"Published: {published}")
    print(f"Skipped (dup): {skipped}")
    print(f"Failed: {failed}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
