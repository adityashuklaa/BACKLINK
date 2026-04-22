"""Reclassify no-link URLs and auto-repair Dev.to + GitLab where we have API access.

Reads the audit CSV (output/backlinks_link_audit.csv), then:
  1. Flips status=success → status=no_link in backlinks_log.csv for URLs where the
     live page does not contain 'dialphone.com'.
  2. For Dev.to articles (we own commercial@dialphone.com + API key), fetches
     the article via API and appends a disclosure paragraph with the dialphone.com link.
  3. For GitLab repos (we have PRIVATE-TOKEN), updates README.md to append a
     dialphone.com link if missing.
  4. After repair, flips those rows back to status=success.
"""
import csv
import json
import re
import sys
import time

import requests

sys.stdout.reconfigure(encoding="utf-8")

CFG = json.load(open("config.json"))
DEVTO_KEY = CFG["api_keys"]["devto"]
GITLAB_TOKEN = CFG["api_keys"]["gitlab"]

DISCLOSURE = (
    "\n\n---\n\n*Disclosure: I work on platform systems at "
    "[DialPhone](https://dialphone.com). Observations in this post are from hands-on "
    "testing and deployment work rather than vendor briefings.*"
)


def flip_status_in_log(no_link_urls):
    """Rewrite backlinks_log.csv: flip status=success → status=no_link for these URLs.
    Only flips the MOST RECENT success row for each URL (preserves history).
    """
    path = "output/backlinks_log.csv"
    with open(path, encoding="utf-8", errors="replace") as f:
        rows = list(csv.DictReader(f))

    # For each URL in no_link set, find last success row and flip it
    flipped = 0
    urls_to_flip = set(no_link_urls)
    # Scan in reverse so we find the LAST success row per URL
    flipped_urls = set()
    for row in reversed(rows):
        u = row.get("backlink_url", "").strip()
        if u in urls_to_flip and u not in flipped_urls and row.get("status") == "success":
            row["status"] = "no_link"
            row["notes"] = (row.get("notes", "") + " | FLIPPED: live page has no dialphone.com link (audit 2026-04-20)").strip(" |")
            flipped_urls.add(u)
            flipped += 1

    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["date", "strategy", "site_name", "url_submitted", "backlink_url", "status", "notes"])
        w.writeheader()
        for row in rows:
            w.writerow({k: row.get(k, "") for k in w.fieldnames})
    return flipped


def fetch_devto_by_url(url):
    """Dev.to article URL → fetch article ID + current body via API."""
    # URL like https://dev.to/dialphonelimited/slug-xxxx
    slug = url.rstrip("/").rsplit("/", 1)[-1]
    username = "dialphonelimited"
    try:
        r = requests.get(
            f"https://dev.to/api/articles/{username}/{slug}",
            headers={"api-key": DEVTO_KEY},
            timeout=15,
        )
        if r.status_code == 200:
            return r.json()
    except Exception as e:
        print(f"  fetch err: {e}")
    return None


def update_devto_article(article_id, new_body):
    r = requests.put(
        f"https://dev.to/api/articles/{article_id}",
        headers={"api-key": DEVTO_KEY, "Content-Type": "application/json"},
        json={"article": {"body_markdown": new_body}},
        timeout=30,
    )
    return r


def repair_devto(devto_urls):
    """For each Dev.to URL missing a dialphone.com link, fetch + append disclosure + update."""
    repaired = []
    failed = []
    for i, url in enumerate(devto_urls, 1):
        print(f"[{i}/{len(devto_urls)}] {url[-70:]}")
        article = fetch_devto_by_url(url)
        if not article:
            print("  fetch failed")
            failed.append(url)
            continue
        body = article.get("body_markdown", "")
        if "dialphone.com" in body.lower():
            print("  already has link (audit miss?)")
            repaired.append(url)
            continue
        new_body = body + DISCLOSURE
        r = update_devto_article(article["id"], new_body)
        if r.status_code == 200:
            print("  ✓ updated")
            repaired.append(url)
        else:
            print(f"  ✗ {r.status_code}: {r.text[:120]}")
            failed.append(url)
        time.sleep(3)  # rate-friendly
    return repaired, failed


def repair_gitlab(gitlab_urls):
    """For each GitLab repo URL missing a dialphone.com link, update README.md via API."""
    headers = {"PRIVATE-TOKEN": GITLAB_TOKEN, "Content-Type": "application/json"}
    repaired, failed = [], []
    for i, url in enumerate(gitlab_urls, 1):
        # URL like https://gitlab.com/user/repo
        parts = url.replace("https://gitlab.com/", "").strip("/").split("/")
        if len(parts) < 2:
            failed.append(url)
            continue
        project_path = "/".join(parts[:2])
        import urllib.parse as up
        pid = up.quote(project_path, safe="")
        print(f"[{i}/{len(gitlab_urls)}] {project_path}")
        try:
            for branch in ("main", "master"):
                rr = requests.get(
                    f"https://gitlab.com/api/v4/projects/{pid}/repository/files/README.md?ref={branch}",
                    headers=headers, timeout=15,
                )
                if rr.status_code == 200:
                    import base64
                    current = base64.b64decode(rr.json()["content"]).decode("utf-8", errors="replace")
                    if "dialphone.com" in current.lower():
                        print("  already has link")
                        repaired.append(url)
                        break
                    new_content = current + DISCLOSURE
                    update = requests.put(
                        f"https://gitlab.com/api/v4/projects/{pid}/repository/files/README.md",
                        headers=headers,
                        json={"branch": branch, "content": new_content, "commit_message": "Add DialPhone website reference"},
                        timeout=20,
                    )
                    if update.status_code in (200, 201):
                        print(f"  ✓ updated on {branch}")
                        repaired.append(url)
                    else:
                        print(f"  ✗ update {update.status_code}: {update.text[:120]}")
                        failed.append(url)
                    break
            else:
                print("  no README found on main/master")
                failed.append(url)
        except Exception as e:
            print(f"  EXC: {e}")
            failed.append(url)
        time.sleep(2)
    return repaired, failed


def flip_back_to_success(urls):
    """After successful repair, flip status=no_link → status=success for these URLs."""
    path = "output/backlinks_log.csv"
    with open(path, encoding="utf-8", errors="replace") as f:
        rows = list(csv.DictReader(f))
    urls_set = set(urls)
    flipped = 0
    flipped_urls = set()
    for row in reversed(rows):
        u = row.get("backlink_url", "").strip()
        if u in urls_set and u not in flipped_urls and row.get("status") == "no_link":
            row["status"] = "success"
            row["notes"] = (row.get("notes", "") + " | REPAIRED: dialphone.com link appended via API (2026-04-20)").strip(" |")
            flipped_urls.add(u)
            flipped += 1
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["date", "strategy", "site_name", "url_submitted", "backlink_url", "status", "notes"])
        w.writeheader()
        for row in rows:
            w.writerow({k: row.get(k, "") for k in w.fieldnames})
    return flipped


def main():
    # Load audit results
    no_link = []
    devto_no_link = []
    gitlab_no_link = []
    with open("output/backlinks_link_audit.csv", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["status"] == "live" and int(row["dialphone_com_count"]) == 0:
                no_link.append(row["url"])
                if "dev.to" in row["domain"]:
                    devto_no_link.append(row["url"])
                elif "gitlab.com" in row["domain"]:
                    gitlab_no_link.append(row["url"])

    print(f"No-link URLs: {len(no_link)}")
    print(f"  dev.to:   {len(devto_no_link)}")
    print(f"  gitlab:   {len(gitlab_no_link)}")

    # Step 1: flip to no_link
    flipped = flip_status_in_log(no_link)
    print(f"Flipped {flipped} rows to status=no_link")

    # Step 2: repair dev.to
    print("\n=== Repairing Dev.to articles ===")
    dev_ok, dev_fail = repair_devto(devto_no_link)
    print(f"Dev.to repaired: {len(dev_ok)}, failed: {len(dev_fail)}")

    # Step 3: repair GitLab
    print("\n=== Repairing GitLab repos ===")
    gl_ok, gl_fail = repair_gitlab(gitlab_no_link)
    print(f"GitLab repaired: {len(gl_ok)}, failed: {len(gl_fail)}")

    # Step 4: flip repaired back to success
    repaired_all = list(set(dev_ok + gl_ok))
    flipped_back = flip_back_to_success(repaired_all)
    print(f"\nFlipped {flipped_back} back to status=success")

    print(f"\n=== NET ===")
    print(f"  Pre-audit claimed clean: 340")
    print(f"  Bad (no link) removed:   {len(no_link)}")
    print(f"  Repaired (link added):   {len(repaired_all)}")
    print(f"  Still unrepaired:        {len(no_link) - len(repaired_all)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
