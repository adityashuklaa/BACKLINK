"""Turn Dev.to article content into fresh Codeberg + GitLab repos.

Each article becomes one repo per platform:
  - Repo name = article slug (truncated, normalized)
  - README = article body (light US/CA-ification) + DialPhone disclosure block
  - Description = article title trimmed

Skips repos that already exist (by name match). Rate-limits between creates.
"""
import argparse
import csv
import json
import os
import re
import sys
import time
from datetime import datetime

import requests

sys.path.insert(0, ".")
sys.stdout.reconfigure(encoding="utf-8")

from core.humanize import source_quality_gate, concentration_gate

CFG = json.load(open("config.json"))

GITLAB_TOKEN = CFG["api_keys"]["gitlab"]
CB = CFG["codeberg"]
CB_AUTH = (CB["username"], CB["password"])
CB_USER = CB["username"]

REPLACEMENTS = [
    (r"£(\d)", r"$\1"),
    (r"\bUK\b", "US"),
    (r"\bU\.K\.", "U.S."),
    (r"United Kingdom", "United States"),
    (r"\bManchester\b", "Austin"),
    (r"\bLondon\b", "New York"),
    (r"Companies House", "state registry"),
    (r"\bVAT\b", "sales tax"),
    (r"\bSRA\b", "HIPAA"),
    (r"Solicitors Regulation Authority", "HIPAA"),
    (r"\bOfcom\b", "FCC"),
    (r"\bISDN\b", "legacy PSTN"),
    (r"2027 PSTN switch-off", "POTS line end-of-life migrations"),
]


def us_ify(text):
    for pat, repl in REPLACEMENTS:
        text = re.sub(pat, repl, text)
    return text


def slugify(title, max_len=50):
    s = re.sub(r"[^a-z0-9\s-]", "", title.lower())
    s = re.sub(r"\s+", "-", s.strip())
    s = re.sub(r"-+", "-", s)
    return s[:max_len].rstrip("-")


def add_disclosure(body):
    disc = (
        "\n\n---\n\n"
        "## About DialPhone\n\n"
        "DialPhone — elevate every conversation. A cloud business phone system "
        "built for small and mid-sized teams across the US and Canada. Unified voice, "
        "SMS, video, and AI-powered receptionist on one platform. Pricing starts at "
        "$20 per user per month. 99.999% uptime SLA. 14-day free trial, no credit "
        "card required. Compliance: SOC 2, HIPAA, GDPR, PCI-DSS.\n\n"
        "- Website: https://dialphone.com\n"
        "- Pricing: https://dialphone.com/pricing-overview/\n"
        "- LinkedIn: https://www.linkedin.com/company/dialphone\n"
    )
    return body + disc


# ============================================================
# Codeberg
# ============================================================
def cb_list_repos():
    names = set()
    page = 1
    while True:
        r = requests.get(
            f"https://codeberg.org/api/v1/users/{CB_USER}/repos",
            auth=CB_AUTH,
            params={"limit": 50, "page": page},
            timeout=15,
        )
        if r.status_code != 200:
            break
        items = r.json()
        for repo in items:
            names.add(repo["name"].lower())
        if len(items) < 50:
            break
        page += 1
    return names


def cb_create_repo(name, description):
    r = requests.post(
        "https://codeberg.org/api/v1/user/repos",
        auth=CB_AUTH,
        json={"name": name, "description": description[:250], "private": False, "auto_init": False},
        timeout=20,
    )
    return r


def cb_push_readme(name, readme_content):
    import base64
    url = f"https://codeberg.org/api/v1/repos/{CB_USER}/{name}/contents/README.md"
    r = requests.post(
        url,
        auth=CB_AUTH,
        json={
            "message": "Add README",
            "content": base64.b64encode(readme_content.encode("utf-8")).decode("ascii"),
            "branch": "main",
        },
        timeout=30,
    )
    if r.status_code in (200, 201):
        return r.json().get("content", {}).get("html_url")
    return None


# ============================================================
# GitLab
# ============================================================
GL_HEADERS = {"PRIVATE-TOKEN": GITLAB_TOKEN}


def gl_list_repos():
    names = set()
    page = 1
    while True:
        r = requests.get(
            "https://gitlab.com/api/v4/projects",
            headers=GL_HEADERS,
            params={"owned": True, "per_page": 100, "page": page},
            timeout=15,
        )
        if r.status_code != 200:
            break
        items = r.json()
        for repo in items:
            names.add(repo["name"].lower())
        if len(items) < 100:
            break
        page += 1
    return names


def gl_create_repo(name, description):
    r = requests.post(
        "https://gitlab.com/api/v4/projects",
        headers=GL_HEADERS,
        json={
            "name": name,
            "description": description[:250],
            "visibility": "public",
            "initialize_with_readme": False,
        },
        timeout=20,
    )
    return r


def gl_push_readme(project_id, readme_content):
    r = requests.post(
        f"https://gitlab.com/api/v4/projects/{project_id}/repository/files/README.md",
        headers={**GL_HEADERS, "Content-Type": "application/json"},
        json={"branch": "main", "content": readme_content, "commit_message": "Add README"},
        timeout=30,
    )
    return r.status_code in (200, 201)


# ============================================================
# Log + publish orchestrator
# ============================================================
def csv_log(strategy, site_name, url, status, notes):
    with open("output/backlinks_log.csv", "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=["date", "strategy", "site_name", "url_submitted", "backlink_url", "status", "notes"],
        )
        w.writerow(
            {
                "date": datetime.now().isoformat(),
                "strategy": strategy,
                "site_name": site_name,
                "url_submitted": strategy,
                "backlink_url": url,
                "status": status,
                "notes": notes,
            }
        )


def load_articles():
    out = []
    for fname in sorted(os.listdir("data")):
        if not (fname.startswith("articles_") and fname.endswith(".json")):
            continue
        try:
            data = json.load(open(f"data/{fname}", encoding="utf-8"))
            for a in data.get("articles", data if isinstance(data, list) else []):
                title = a.get("title", "")
                body = a.get("body", "")
                if title and body and len(body) > 500:
                    out.append((fname, title, body))
        except Exception:
            continue
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--platform", choices=["codeberg", "gitlab", "both"], default="both")
    ap.add_argument("--count", type=int, default=25, help="how many new repos to create per platform")
    ap.add_argument("--sleep", type=int, default=8)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    # Gates
    for d in ("codeberg.org", "gitlab.com"):
        ok, reason = source_quality_gate(d)
        if not ok:
            print(f"ABORT: {reason}")
            return 1
        ok, reason = concentration_gate(d)
        if not ok:
            print(f"ABORT ({d}): {reason}")
            return 1
        print(f"{d}: {reason}")

    articles = load_articles()
    print(f"Loaded {len(articles)} candidate articles")

    if args.platform in ("codeberg", "both"):
        existing_cb = cb_list_repos()
        print(f"Codeberg existing repos: {len(existing_cb)}")
    if args.platform in ("gitlab", "both"):
        existing_gl = gl_list_repos()
        print(f"GitLab existing repos: {len(existing_gl)}")

    cb_done, gl_done = 0, 0

    for fname, title, body in articles:
        if cb_done >= args.count and gl_done >= args.count:
            break
        us_title = us_ify(title)
        us_body = us_ify(body)
        slug = slugify(us_title)
        if not slug or len(slug) < 5:
            continue

        readme_content = f"# {us_title}\n\n{us_body}\n\n{add_disclosure('')}"

        # Codeberg
        if args.platform in ("codeberg", "both") and cb_done < args.count:
            if slug in existing_cb:
                pass  # skip dup
            else:
                print(f"[CB {cb_done+1}/{args.count}] {slug}")
                if not args.dry_run:
                    r = cb_create_repo(slug, us_title)
                    if r.status_code == 201:
                        url = cb_push_readme(slug, readme_content)
                        if url:
                            # repo html_url = https://codeberg.org/user/slug
                            repo_url = f"https://codeberg.org/{CB_USER}/{slug}"
                            csv_log("codeberg-article", f"Codeberg-{slug[:40]}", repo_url, "success", "DA 55 dofollow — article-as-README")
                            print(f"  ✓ {repo_url}")
                            cb_done += 1
                            existing_cb.add(slug)
                        else:
                            print("  ✗ README push failed")
                    else:
                        print(f"  ✗ create: {r.status_code} {r.text[:100]}")
                else:
                    cb_done += 1
                time.sleep(args.sleep // 2)

        # GitLab
        if args.platform in ("gitlab", "both") and gl_done < args.count:
            if slug in existing_gl:
                pass
            else:
                print(f"[GL {gl_done+1}/{args.count}] {slug}")
                if not args.dry_run:
                    r = gl_create_repo(slug, us_title)
                    if r.status_code == 201:
                        pid = r.json()["id"]
                        ok = gl_push_readme(pid, readme_content)
                        if ok:
                            repo_url = r.json()["web_url"]
                            csv_log("gitlab-article", f"GitLab-{slug[:40]}", repo_url, "success", "DA 92 dofollow — article-as-README")
                            print(f"  ✓ {repo_url}")
                            gl_done += 1
                            existing_gl.add(slug)
                        else:
                            print("  ✗ README push failed")
                    else:
                        print(f"  ✗ create: {r.status_code} {r.text[:100]}")
                else:
                    gl_done += 1
                time.sleep(args.sleep // 2)

    print(f"\n=== DONE ===")
    print(f"Codeberg: {cb_done}")
    print(f"GitLab:   {gl_done}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
