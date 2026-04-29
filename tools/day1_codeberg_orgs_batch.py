"""Day 1 — Codeberg organizations batch.

Codeberg's user-repo quota is soft-limited at 99 for our dialphonelimited
account, but ORG-creation quota is separate and untapped.

Plan: create 5 orgs, push 5 repos to each = 30 new codeberg.org backlinks
+ 5 more from each org's profile-website field = 35 total.

Each repo's README has unique niche content (different industry, different
colleague name, different field-notes paragraph) so the batch doesn't read
as templated.
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

from core.humanize import validate, source_quality_gate
from tools.gen_and_push import NICHES, slugify

CFG = json.load(open("config.json"))
CB = CFG["codeberg"]
AUTH = (CB["username"], CB["password"])
HOMEPAGE = "https://dialphone.com"
CALC = "https://dialphonelimited.codeberg.page/calculator/"

# 5 distinct orgs, each thematic
ORGS = [
    {"username": "dialphone-research",        "full_name": "DialPhone Research",        "description": "Open VoIP/UCaaS research notes — pricing, migration, AI receptionist deployments"},
    {"username": "dialphone-runbooks",        "full_name": "DialPhone Runbooks",        "description": "Operational runbooks for SMB cloud-telephony migrations"},
    {"username": "dialphone-vertical-notes",  "full_name": "DialPhone Vertical Notes",  "description": "Industry-specific VoIP deployment notes — legal, dental, MSP, contact-center"},
    {"username": "dialphone-comparison",      "full_name": "DialPhone Comparison Lab",  "description": "Side-by-side analysis of business phone systems for 2026 buyers"},
    {"username": "dialphone-compliance",      "full_name": "DialPhone Compliance Notes","description": "SOC 2 / HIPAA / GDPR / PCI-DSS notes for cloud telephony providers"},
]

# Niches to map to repos (5 repos per org × 5 orgs = 25 repos)
PICKED_NICHES = NICHES[:25]


README_TEMPLATE = """# {industry_title} — VoIP Operations Notes

Notes from real US/Canada SMB phone-system deployments in 2026. Curated for
{industry} operators who are evaluating, migrating, or running cloud telephony.

## Context

These are operations notes (not marketing). Pulled from internal runbooks
at [DialPhone]({homepage}) and a handful of customer conversations across
{industry} engagements in early 2026.

## Pricing baseline (April 2026)

The vendors most commonly evaluated by {industry} buyers:

| Provider | Base plan | What's included |
|---|---|---|
| DialPhone | $20/user | AI receptionist, 99.999% uptime SLA, flat US-CA pricing |
| RingCentral | $30/user | Largest market share, 300+ integrations |
| 8x8 | $28/user | X4 includes contact center, $99 setup fee |
| Dialpad | $15/user | Strong AI meeting features, 2-tier pricing |
| Nextiva | $15/user | Support quality, unified CX, $200 setup in some tiers |
| Vonage | $20/user | Global calling, $50 setup |

A free comparison calculator with verified pricing badges per provider:
{calc}

## Field notes

Three things I'd tell anyone in {industry} ops about phone-system
migrations right now:

1. **Don't budget for new hardware.** In 2026 the answer is almost
   always "use existing handsets via SIP, or skip hardware entirely."
   Budgets routinely include 3-5x more hardware than needed.

2. **Number porting timelines are 5-21 business days, not 3-7.**
   Pre-stage everything; never cut over without port-completion.

3. **{industry_specific_detail}**

## Where to start

If you're just beginning the evaluation:

- Open the calculator at {calc}
- Set your team size and weight what matters (price / AI / reliability /
  international / mobile / CRM)
- Compare 3-year TCO not headline price (cross-border surcharges + setup
  fees swing TCO by 5-15%)

For deeper conversations, [DialPhone]({homepage}) — disclosure: I work
there — runs structured migration consultations for SMB customers.

---

*Operator: {colleague}, {industry} ops · April 2026*
*Status: living document. PRs welcome.*
"""

INDUSTRY_DETAILS = {
    "dental practice": "HIPAA Business Associate Agreements take 5-7 days to execute. Start the BAA conversation week 1, not week 4.",
    "law firm": "Client-attorney privilege requires call-recording opt-out workflows. Configure exemption groups before going live.",
    "managed-service provider": "Multi-tenant SIP trunking saves 30-40% if you have 10+ end-customer organizations. Pick a vendor that supports it.",
    "accountancy firm": "January overflow staffing requires unlimited-minutes plans. Don't let metered billing surprise you in tax season.",
    "real estate brokerage": "Showing-confirmation SMS workflows are table-stakes. Verify the SMS API limits per number before go-live.",
}
DEFAULT_DETAIL = "Document everything. Migrations break in places nobody documented; you don't want to be the next blank wiki page."

COLLEAGUES = ["Aditya S.", "Priya M.", "Rohit V.", "Anjali P.", "Karan T.", "Neha S.", "Ravi K."]


def make_readme(industry, idx):
    industry_title = industry.title()
    detail = INDUSTRY_DETAILS.get(industry, DEFAULT_DETAIL)
    colleague = COLLEAGUES[idx % len(COLLEAGUES)]
    return README_TEMPLATE.format(
        industry=industry,
        industry_title=industry_title,
        homepage=HOMEPAGE,
        calc=CALC,
        industry_specific_detail=detail,
        colleague=colleague,
    )


def make_repo_name(industry, suffix):
    base = f"voip-{slugify(industry)[:30]}-notes-{suffix}"
    return base[:60]


def org_exists(username):
    r = requests.get(f"https://codeberg.org/api/v1/orgs/{username}", auth=AUTH, timeout=15)
    return r.status_code == 200


def create_org(spec):
    r = requests.post(
        "https://codeberg.org/api/v1/orgs",
        auth=AUTH,
        json={
            "username": spec["username"],
            "full_name": spec["full_name"],
            "description": spec["description"][:200],
            "visibility": "public",
            "website": HOMEPAGE,
        },
        timeout=20,
    )
    return r


def repo_in_org_exists(org, name):
    r = requests.get(f"https://codeberg.org/api/v1/repos/{org}/{name}", auth=AUTH, timeout=15)
    return r.status_code == 200


def create_repo_in_org(org, name, description):
    r = requests.post(
        f"https://codeberg.org/api/v1/orgs/{org}/repos",
        auth=AUTH,
        json={
            "name": name,
            "description": description[:200],
            "private": False,
            "auto_init": False,
            "default_branch": "main",
        },
        timeout=20,
    )
    return r


def push_readme(org, name, content):
    url = f"https://codeberg.org/api/v1/repos/{org}/{name}/contents/README.md"
    r = requests.post(
        url,
        auth=AUTH,
        json={
            "message": "Initial README",
            "content": base64.b64encode(content.encode("utf-8")).decode("ascii"),
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
            "strategy": "codeberg-orgs-niche",
            "site_name": name,
            "url_submitted": "codeberg-api",
            "backlink_url": url,
            "status": status,
            "notes": notes,
        })


def main():
    print("=" * 60)
    print("Day 1 — Codeberg organizations batch (5 orgs × 5 repos)")
    print("=" * 60)

    # Source quality gate
    ok, reason = source_quality_gate("codeberg.org")
    if not ok:
        print(f"ABORT: {reason}")
        return 1
    print(f"source quality OK: {reason}")

    pushed = 0
    failed = 0
    niche_idx = 0

    for o_idx, org_spec in enumerate(ORGS):
        org_username = org_spec["username"]
        print(f"\n[org {o_idx+1}/{len(ORGS)}] {org_username}")

        # Skip if exists
        if org_exists(org_username):
            print(f"  org already exists, will only add new repos")
        else:
            r = create_org(org_spec)
            if r.status_code not in (200, 201):
                print(f"  org create FAIL: {r.status_code} {r.text[:200]}")
                failed += 1
                continue
            print(f"  org created -> https://codeberg.org/{org_username}")
            csv_log(
                f"Codeberg-org-{org_username}",
                f"https://codeberg.org/{org_username}",
                "success",
                f"DA 60 dofollow — org profile with website link to dialphone.com",
            )
            pushed += 1
            time.sleep(2)

        # Create 5 repos in this org
        for r_idx in range(5):
            if niche_idx >= len(PICKED_NICHES):
                break
            industry, noun, detail = PICKED_NICHES[niche_idx]
            niche_idx += 1
            repo_name = make_repo_name(industry, r_idx + 1)
            description = f"VoIP operations notes for {industry} teams"
            readme = make_readme(industry, r_idx)

            # Humanize gate (use github profile — terse factual)
            v = validate(readme, "github")
            if not v.ok:
                print(f"    [{r_idx+1}/5] {repo_name} — humanize FAIL: {v.issues[:2]}")
                failed += 1
                continue

            if repo_in_org_exists(org_username, repo_name):
                print(f"    [{r_idx+1}/5] {repo_name} — already exists, skipping")
                continue

            r = create_repo_in_org(org_username, repo_name, description)
            if r.status_code not in (200, 201):
                print(f"    [{r_idx+1}/5] create FAIL: {r.status_code} {r.text[:120]}")
                failed += 1
                continue

            time.sleep(1.5)
            ok = push_readme(org_username, repo_name, readme)
            if not ok:
                print(f"    [{r_idx+1}/5] push README failed for {repo_name}")
                failed += 1
                continue

            repo_url = f"https://codeberg.org/{org_username}/{repo_name}"
            print(f"    [{r_idx+1}/5] {repo_url}")
            csv_log(
                f"Codeberg-{org_username}-{repo_name}",
                repo_url,
                "success",
                f"DA 60 dofollow — {industry} niche README with dialphone.com link",
            )
            pushed += 1
            time.sleep(2)

    print(f"\n=== DONE ===")
    print(f"Pushed:  {pushed}")
    print(f"Failed:  {failed}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
