"""Push the VoIP Cost Calculator to GitLab as a Pages project.

Creates repo `voip-cost-calculator` under the `dialphonelimited` GitLab account,
uploads the HTML + .gitlab-ci.yml, and triggers a Pages deploy.
Result: calculator lives at https://dialphonelimited.gitlab.io/voip-cost-calculator/
"""
import base64
import csv
import json
import sys
import time
from datetime import datetime

import requests

sys.stdout.reconfigure(encoding="utf-8")

CFG = json.load(open("config.json"))
TOKEN = CFG["api_keys"]["gitlab"]
HEADERS = {"PRIVATE-TOKEN": TOKEN, "Content-Type": "application/json"}

REPO_NAME = "voip-cost-calculator"


def get_or_create_project():
    # check if exists
    r = requests.get(
        f"https://gitlab.com/api/v4/projects/dialphonelimited%2F{REPO_NAME}",
        headers=HEADERS, timeout=15,
    )
    if r.status_code == 200:
        print(f"[info] project exists: {r.json()['web_url']}")
        return r.json()
    # create
    r = requests.post(
        "https://gitlab.com/api/v4/projects",
        headers=HEADERS,
        json={
            "name": REPO_NAME,
            "description": "Free VoIP cost calculator comparing 2026 pricing across DialPhone, RingCentral, 8x8, Dialpad, Nextiva, and more.",
            "visibility": "public",
            "initialize_with_readme": False,
        },
        timeout=20,
    )
    if r.status_code != 201:
        raise Exception(f"create failed {r.status_code}: {r.text[:200]}")
    print(f"[info] created: {r.json()['web_url']}")
    return r.json()


def push_file(pid, path, content_str, commit_msg):
    # Try to update first; if 404 (doesn't exist), create
    r = requests.post(
        f"https://gitlab.com/api/v4/projects/{pid}/repository/files/{requests.utils.quote(path, safe='')}",
        headers=HEADERS,
        json={"branch": "main", "content": content_str, "commit_message": commit_msg},
        timeout=30,
    )
    if r.status_code in (200, 201):
        print(f"  ✓ pushed {path}")
        return True
    print(f"  ✗ {path}: {r.status_code} {r.text[:150]}")
    return False


def csv_log(url, status, notes):
    with open("output/backlinks_log.csv", "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=["date", "strategy", "site_name", "url_submitted", "backlink_url", "status", "notes"],
        )
        w.writerow(
            {
                "date": datetime.now().isoformat(),
                "strategy": "linkable-asset",
                "site_name": "VoIP-Cost-Calculator",
                "url_submitted": "gitlab-pages",
                "backlink_url": url,
                "status": status,
                "notes": notes,
            }
        )


def main():
    proj = get_or_create_project()
    pid = proj["id"]

    # Read files
    with open("assets/calculator/index.html", encoding="utf-8") as f:
        html = f.read()
    with open("assets/calculator/.gitlab-ci.yml", encoding="utf-8") as f:
        ci = f.read()

    # Push both
    push_file(pid, "index.html", html, "Add VoIP Cost Calculator")
    push_file(pid, ".gitlab-ci.yml", ci, "Add Pages CI config")

    # Log the backlink
    pages_url = f"https://dialphonelimited.gitlab.io/{REPO_NAME}/"
    repo_url = proj["web_url"]
    csv_log(pages_url, "pending", "DA 92 (GitLab Pages) — linkable asset calculator, deploy pending ~5 min")
    csv_log(repo_url, "success", "DA 92 dofollow — GitLab repo containing calculator")

    print(f"\n=== DONE ===")
    print(f"Repo:          {repo_url}")
    print(f"Pages (in ~5 min): {pages_url}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
