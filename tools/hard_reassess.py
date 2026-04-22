"""Hard reassessment of every 'success' URL in final_truth.csv.

For each URL:
  - HTTP GET (browser UA)
  - 404 → mark status=dead
  - 403 → use API verification if available (Hashnode, Codeberg)
  - 200 without dialphone.com in body → mark no_link
  - 200 with dialphone.com → keep as success

Special handling per platform:
  - Hashnode: use GraphQL API to confirm article exists + has dialphone.com markdown
  - Codeberg: use API to confirm repo exists + fetch README
  - GitLab: same (with PRIVATE-TOKEN)
  - Dev.to: /api/articles/:id — confirm not deleted
  - Quora: already flipped to no_link; skip
"""
import base64
import csv
import json
import re
import sys
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import quote, urlparse

import requests

sys.stdout.reconfigure(encoding="utf-8")

CFG = json.load(open("config.json"))
HN_TOKEN = CFG["api_keys"]["hashnode"]
DEVTO_KEY = CFG["api_keys"]["devto"]
GITLAB_TOKEN = CFG["api_keys"]["gitlab"]
CB = CFG["codeberg"]
CB_AUTH = (CB["username"], CB["password"])

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/131.0 Safari/537.36"}


def hn_verify(url):
    """Hashnode: fetch post via API, check alive + dialphone.com in body."""
    slug = url.rstrip("/").rsplit("/", 1)[-1]
    q = """
    query Post($slug: String!) {
      publication(host: "dialphonevoip.hashnode.dev") {
        post(slug: $slug) { id content { markdown } }
      }
    }
    """
    try:
        r = requests.post(
            "https://gql.hashnode.com/",
            json={"query": q, "variables": {"slug": slug}},
            headers={"Authorization": HN_TOKEN},
            timeout=15,
        )
        post = r.json().get("data", {}).get("publication", {}).get("post")
        if not post:
            return "dead", "hashnode post missing (slug not found)"
        md = post.get("content", {}).get("markdown", "")
        return ("success" if "dialphone.com" in md.lower() else "no_link", "hashnode api-verified")
    except Exception as e:
        return "err", f"hashnode api err: {e}"


def cb_verify(url):
    """Codeberg: check repo exists + README contains dialphone.com."""
    parts = url.replace("https://codeberg.org/", "").strip("/").split("/")
    if len(parts) < 2:
        return "err", "bad url"
    owner, repo = parts[0], parts[1]
    try:
        r = requests.get(
            f"https://codeberg.org/api/v1/repos/{owner}/{repo}",
            auth=CB_AUTH,
            timeout=12,
        )
        if r.status_code == 404:
            return "dead", "codeberg repo missing"
        if r.status_code != 200:
            return "err", f"cb repo http_{r.status_code}"
        for branch in ("main", "master"):
            rr = requests.get(
                f"https://codeberg.org/api/v1/repos/{owner}/{repo}/contents/README.md",
                auth=CB_AUTH,
                params={"ref": branch},
                timeout=12,
            )
            if rr.status_code == 200:
                content = rr.json().get("content", "")
                try:
                    body = base64.b64decode(content).decode("utf-8", errors="replace")
                    return ("success" if "dialphone.com" in body.lower() else "no_link", "cb readme check")
                except Exception:
                    return "err", "cb b64 decode"
        return "no_link", "cb repo exists but no README"
    except Exception as e:
        return "err", f"cb: {e}"


def gl_verify(url):
    """GitLab: check project exists + README has dialphone.com."""
    path = url.replace("https://gitlab.com/", "").strip("/")
    pid = quote(path, safe="")
    try:
        r = requests.get(
            f"https://gitlab.com/api/v4/projects/{pid}",
            headers={"PRIVATE-TOKEN": GITLAB_TOKEN},
            timeout=12,
        )
        if r.status_code == 404:
            return "dead", "gl project missing"
        if r.status_code != 200:
            return "err", f"gl proj http_{r.status_code}"
        for branch in ("main", "master"):
            rr = requests.get(
                f"https://gitlab.com/api/v4/projects/{pid}/repository/files/README.md",
                headers={"PRIVATE-TOKEN": GITLAB_TOKEN},
                params={"ref": branch},
                timeout=12,
            )
            if rr.status_code == 200:
                try:
                    body = base64.b64decode(rr.json()["content"]).decode("utf-8", errors="replace")
                    return ("success" if "dialphone.com" in body.lower() else "no_link", "gl readme check")
                except Exception:
                    return "err", "gl b64 decode"
        return "no_link", "gl project exists but no README"
    except Exception as e:
        return "err", f"gl: {e}"


def devto_verify(url):
    """Dev.to: fetch article via API."""
    # url like https://dev.to/username/slug
    parts = url.rstrip("/").split("/")
    if len(parts) < 5:
        return "err", "bad url"
    username, slug = parts[-2], parts[-1]
    try:
        r = requests.get(
            f"https://dev.to/api/articles/{username}/{slug}",
            headers={"api-key": DEVTO_KEY},
            timeout=15,
        )
        if r.status_code == 404:
            return "dead", "devto article deleted"
        if r.status_code != 200:
            return "err", f"devto http_{r.status_code}"
        body = r.json().get("body_markdown", "")
        return ("success" if "dialphone.com" in body.lower() else "no_link", "devto api check")
    except Exception as e:
        return "err", f"devto: {e}"


def http_verify(url):
    """Generic HTTP check (for domains without API verification)."""
    try:
        r = requests.get(url, headers=HEADERS, timeout=15, allow_redirects=True)
        if r.status_code == 404:
            return "dead", "http 404"
        if r.status_code != 200:
            return "err", f"http_{r.status_code}"
        has_link = "dialphone.com" in r.text.lower()
        return ("success" if has_link else "no_link", "http check")
    except Exception as e:
        return "err", f"http: {type(e).__name__}"


def verify_row(row):
    url = row["backlink_url"]
    domain = urlparse(url).netloc.lower().replace("www.", "")
    if "hashnode.dev" in domain:
        status, note = hn_verify(url)
    elif "codeberg.org" in domain:
        status, note = cb_verify(url)
    elif "gitlab.com" in domain:
        status, note = gl_verify(url)
    elif "dev.to" in domain:
        status, note = devto_verify(url)
    else:
        status, note = http_verify(url)
    return url, domain, status, note


def main():
    rows = []
    with open("output/backlinks_final_truth.csv", encoding="utf-8", errors="replace") as f:
        for r in csv.DictReader(f):
            if r.get("status") == "success":
                rows.append(r)

    print(f"Re-verifying {len(rows)} success URLs...")

    results = []
    done = 0
    with ThreadPoolExecutor(max_workers=15) as ex:
        futures = {ex.submit(verify_row, r): r for r in rows}
        for f in as_completed(futures):
            results.append(f.result())
            done += 1
            if done % 30 == 0:
                print(f"  {done}/{len(rows)}")

    # Flip statuses in log.csv for URLs that need correction
    log_path = "output/backlinks_log.csv"
    with open(log_path, encoding="utf-8", errors="replace") as f:
        log_rows = list(csv.DictReader(f))

    flip_map = {}  # url -> new_status
    for url, domain, status, note in results:
        if status in ("dead", "no_link"):
            flip_map[url] = (status, note)

    flipped = 0
    flipped_urls = set()
    for row in reversed(log_rows):
        u = row.get("backlink_url", "").strip()
        if u in flip_map and u not in flipped_urls and row.get("status") == "success":
            new_status, note = flip_map[u]
            row["status"] = new_status
            row["notes"] = (row.get("notes", "") + f" | REASSESS 2026-04-21: {note}").strip(" |")
            flipped_urls.add(u)
            flipped += 1

    with open(log_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["date", "strategy", "site_name", "url_submitted", "backlink_url", "status", "notes"])
        w.writeheader()
        for row in log_rows:
            w.writerow({k: row.get(k, "") for k in w.fieldnames})

    # Summary
    by_status = Counter(r[2] for r in results)
    by_domain_status = Counter((r[1], r[2]) for r in results)

    print(f"\n=== STATUS ===")
    for s, c in by_status.most_common():
        print(f"  {s:15s} {c}")

    print(f"\n=== BY DOMAIN ===")
    for (d, s), c in sorted(by_domain_status.items()):
        print(f"  {d:35s} {s:15s} {c}")

    print(f"\nFlipped {flipped} rows in log.csv to dead/no_link")
    return 0


if __name__ == "__main__":
    sys.exit(main())
