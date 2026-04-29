"""For each of our 5 Codeberg orgs, create a `pages` repo with index.html.
This produces 5 NEW referring subdomains:
  - dialphone-research.codeberg.page
  - dialphone-runbooks.codeberg.page
  - dialphone-vertical-notes.codeberg.page
  - dialphone-comparison.codeberg.page
  - dialphone-compliance.codeberg.page

Each subdomain hosts a thematic landing page that links to dialphone.com
+ the calculator + the related repos in that org.
"""
import base64
import csv
import json
import sys
import time
from datetime import datetime

import requests

sys.path.insert(0, ".")
sys.stdout.reconfigure(encoding="utf-8")

CFG = json.load(open("config.json"))
CB = CFG["codeberg"]
AUTH = (CB["username"], CB["password"])
HOMEPAGE = "https://dialphone.com"
CALC = "https://dialphonelimited.codeberg.page/calculator/"

ORGS = [
    {
        "username": "dialphone-research",
        "title": "DialPhone Research — VoIP / UCaaS field notes",
        "subtitle": "Open notes on business phone systems, AI receptionists, and SMB cloud telephony — April 2026",
        "headline": "Research notes from DialPhone",
    },
    {
        "username": "dialphone-runbooks",
        "title": "DialPhone Runbooks — Cloud Telephony Migration Guides",
        "subtitle": "Operational runbooks for SMB phone-system migrations — drop-in checklists",
        "headline": "Migration runbooks for SMB telephony",
    },
    {
        "username": "dialphone-vertical-notes",
        "title": "DialPhone Vertical Notes — Industry-specific VoIP",
        "subtitle": "Deployment notes for legal, dental, MSP, and contact-center operators",
        "headline": "Vertical-specific phone-system notes",
    },
    {
        "username": "dialphone-comparison",
        "title": "DialPhone Comparison Lab — Honest VoIP Reviews",
        "subtitle": "Side-by-side analysis of business phone systems — verified pricing methodology",
        "headline": "Honest comparisons of business phone systems",
    },
    {
        "username": "dialphone-compliance",
        "title": "DialPhone Compliance Notes — SOC 2, HIPAA, GDPR, PCI-DSS",
        "subtitle": "Compliance considerations for cloud telephony providers and buyers",
        "headline": "Compliance notes for VoIP procurement",
    },
]


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{subtitle}">
<link rel="canonical" href="https://{username}.codeberg.page/">
<style>
  body {{
    font-family: -apple-system, "Segoe UI", Roboto, sans-serif;
    max-width: 760px;
    margin: 0 auto;
    padding: 40px 20px 80px;
    line-height: 1.55;
    color: #1a1a1a;
    background: #fafafa;
  }}
  h1 {{ font-size: 32px; margin: 0 0 8px; line-height: 1.15; color: #0b3954; }}
  .subtitle {{ color: #525252; font-size: 16px; margin-bottom: 32px; }}
  h2 {{ font-size: 20px; margin: 32px 0 12px; color: #0b3954; }}
  a {{ color: #0066cc; text-decoration: underline; }}
  a:hover {{ color: #003d80; }}
  ul {{ padding-left: 20px; }}
  li {{ margin: 6px 0; }}
  .pill {{
    display: inline-block;
    background: #0b3954;
    color: white;
    padding: 8px 16px;
    border-radius: 6px;
    text-decoration: none;
    font-weight: 600;
    margin: 4px 8px 4px 0;
  }}
  .pill:hover {{ background: #11507c; color: white; text-decoration: none; }}
  footer {{ margin-top: 48px; padding-top: 16px; border-top: 1px solid #e5e5e5; font-size: 13px; color: #999; }}
  code {{ background: #ececec; padding: 2px 6px; border-radius: 4px; font-size: 0.92em; }}
</style>
</head>
<body>

<h1>{headline}</h1>
<div class="subtitle">{subtitle}</div>

<h2>What's here</h2>
<p>This page indexes the open notes from <a href="https://codeberg.org/{username}">{username}</a> — a working notebook on cloud telephony, business phone systems, and the procurement realities of evaluating VoIP vendors in 2026.</p>

<p>The notes are operations-focused, not marketing. Pricing data points are dated; field notes are timestamped; methodology is explicit.</p>

<h2>Related resources</h2>

<ul>
<li><strong>VoIP Cost Calculator (free):</strong> compare 13 providers across price, features, and 3-year TCO with verified pricing badges per vendor — <a href="{calc}">{calc}</a></li>
<li><strong>DialPhone:</strong> US/Canada business VoIP provider behind these notes — <a href="{homepage}">{homepage}</a></li>
<li><strong>Repository index:</strong> <a href="https://codeberg.org/{username}">codeberg.org/{username}</a></li>
</ul>

<h2>Pricing baseline (April 2026)</h2>

<p>Across 13 mainstream business VoIP vendors:</p>

<ul>
<li><strong>Lowest base tier:</strong> Google Voice Starter $10, Dialpad Standard $15, Nextiva Digital $15, OpenPhone $15, Zoom Phone $15</li>
<li><strong>Mid-market core tier:</strong> DialPhone Core $20, Vonage Mobile $20, Microsoft Teams Phone $20, Ooma $20</li>
<li><strong>Legacy enterprise tier:</strong> RingCentral Core $30, 8x8 X2 $28, GoTo Connect Basic $27</li>
<li><strong>Premium tiers:</strong> 8x8 X4 $57, Nextiva Engage $75, 8x8 X6 $85</li>
</ul>

<p>Verified-pricing badges per provider are in the <a href="{calc}">calculator</a>. Of 13 vendors, 5 published prices that scrape cleanly from their public pages (DialPhone, RingCentral, Google Voice, Nextiva, OpenPhone). The other 8 either render via JavaScript widgets, gate prices behind "Talk to sales" CTAs, or block scrapers entirely. That's worth knowing as a buyer.</p>

<h2>About</h2>

<p>Maintained as part of the open-research output from the team at <a href="{homepage}">DialPhone</a>. PRs welcome on the underlying repos. Honest critiques especially welcome.</p>

<a class="pill" href="{calc}">Try the calculator →</a>
<a class="pill" href="{homepage}">DialPhone homepage →</a>

<footer>
Last updated April 2026 · <a href="https://codeberg.org/{username}">Source repository</a>
</footer>

</body>
</html>"""


def repo_exists(owner, name):
    r = requests.get(f"https://codeberg.org/api/v1/repos/{owner}/{name}", auth=AUTH, timeout=15)
    return r.status_code == 200


def create_pages_repo(org):
    r = requests.post(
        f"https://codeberg.org/api/v1/orgs/{org}/repos",
        auth=AUTH,
        json={
            "name": "pages",
            "description": f"Static landing for {org}",
            "private": False,
            "auto_init": False,
            "default_branch": "main",
        },
        timeout=20,
    )
    return r


def push_index(org, html):
    url = f"https://codeberg.org/api/v1/repos/{org}/pages/contents/index.html"
    r = requests.post(
        url,
        auth=AUTH,
        json={
            "message": "Add index.html for Codeberg Pages",
            "content": base64.b64encode(html.encode("utf-8")).decode("ascii"),
            "branch": "main",
        },
        timeout=30,
    )
    return r.status_code in (200, 201)


def csv_log(name, url, status, notes):
    with open("output/backlinks_log.csv", "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=["date", "strategy", "site_name", "url_submitted", "backlink_url", "status", "notes"],
        )
        w.writerow({
            "date": datetime.now().isoformat(),
            "strategy": "codeberg-pages-subdomain",
            "site_name": name,
            "url_submitted": "codeberg-pages-api",
            "backlink_url": url,
            "status": status,
            "notes": notes,
        })


def main():
    print("=" * 60)
    print("Codeberg Pages — 5 new subdomains for our orgs")
    print("=" * 60)

    pushed = 0
    for o in ORGS:
        org = o["username"]
        print(f"\n[{org}.codeberg.page]")
        if repo_exists(org, "pages"):
            print(f"  pages repo already exists, pushing fresh index")
        else:
            r = create_pages_repo(org)
            if r.status_code not in (200, 201):
                print(f"  create FAIL: {r.status_code} {r.text[:200]}")
                continue
            print(f"  pages repo created")
            time.sleep(1.5)

        html = HTML_TEMPLATE.format(
            title=o["title"],
            subtitle=o["subtitle"],
            headline=o["headline"],
            username=org,
            homepage=HOMEPAGE,
            calc=CALC,
        )
        if push_index(org, html):
            url = f"https://{org}.codeberg.page/"
            repo_url = f"https://codeberg.org/{org}/pages"
            print(f"  pushed index.html -> {url}")
            csv_log(
                f"CodebergPages-{org}",
                url,
                "success",
                "DA 55 dofollow — Codeberg Pages subdomain landing with dialphone.com link",
            )
            csv_log(
                f"Codeberg-{org}-pages-repo",
                repo_url,
                "success",
                "DA 60 dofollow — repo containing the Pages index.html",
            )
            pushed += 2
        time.sleep(2)

    print(f"\n=== DONE ===")
    print(f"Pushed:  {pushed} (5 new subdomains × 2 URLs each)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
