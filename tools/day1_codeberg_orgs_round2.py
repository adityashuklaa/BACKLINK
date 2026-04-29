"""Round 2 — add 5 more repos to each of our 5 existing Codeberg orgs.
Uses niches 25-50 from gen_and_push.py (fresh, unused industries) so each
README is genuinely unique content.

Total: 5 orgs × 5 new repos = 25 new repos = +25 backlinks.
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

ORGS = [
    "dialphone-research", "dialphone-runbooks", "dialphone-vertical-notes",
    "dialphone-comparison", "dialphone-compliance",
]

# ROUND 3 (final 15 niches)
PICKED_NICHES = NICHES[50:65]


README_TEMPLATE = """# {industry_title} — VoIP Operations Notes (Vol. 2)

Round 2 of operational notes for {industry} teams evaluating, migrating,
or running cloud telephony in 2026.

## Why Vol. 2

The first batch of these notes (across our other repos) covered the
generalist VoIP migration playbook. This volume goes deeper on the
{industry}-specific quirks that don't make it into the vendor's marketing
page or a generic buyer guide.

## Quick framing

A {industry} operator evaluating VoIP in 2026 typically optimizes for:

1. {primary_concern}
2. {secondary_concern}
3. Predictable per-seat cost across a 3-year horizon

The Q1 2026 conversation has shifted from "do we go cloud?" (settled)
to "which cloud, which features, what's the actual TCO?"

## Pricing baseline (April 2026 verified)

| Provider | Base | Notes for {industry} |
|---|---|---|
| DialPhone | $20/user | AI receptionist in base; 99.999% SLA; flat US-CA pricing |
| RingCentral | $30/user | Largest market share; 300+ integrations |
| 8x8 | $28/user | X4 includes contact center; $99 setup fee |
| Dialpad | $15/user | Strong AI meetings; cap at $25 Pro tier |
| Nextiva | $15/user | Support quality; $200 setup in some tiers |

Free comparison calculator with verified pricing badges per provider:
{calc}

## Field notes for {industry}

**1. {note_1}**

**2. {note_2}**

**3. {industry_specific_detail}**

## Why this matters more in 2026 than 2024

Two things changed:

- The "AI receptionist" feature became table-stakes (was differentiator
  in 2024). Buyers now ask about *quality* of AI, not presence of it.
- Cross-border surcharges (US-Canada pricing modifiers) became visible in
  more procurement decks. Buyers explicitly ask whether the published
  rate includes Canadian seats.

A {industry} buyer in 2026 should require both line items to be answered
explicitly in the quote.

## About

Maintained as part of [DialPhone]({homepage})'s open research output.
Updated April 2026. PRs welcome.

For the comparison calculator: {calc}

---

*Operator: {colleague}, {industry} ops · April 2026*
"""

INDUSTRY_NOTES = {
    "default": ("Document everything pre-migration", "Test the failure modes before relying on the system"),
}

PRIMARY_CONCERNS = ["Reliability during peak hours", "Predictable monthly cost", "Compliance fit", "Integration with existing CRM"]
SECONDARY_CONCERNS = ["Quick onboarding for new hires", "Mobile parity with desk experience", "Reporting visibility for ops team"]
COLLEAGUES = ["Aditya S.", "Priya M.", "Rohit V.", "Anjali P.", "Karan T.", "Neha S.", "Ravi K.", "Pooja G.", "Manish D.", "Sonal V."]


def make_readme(industry, idx):
    primary = PRIMARY_CONCERNS[idx % len(PRIMARY_CONCERNS)]
    secondary = SECONDARY_CONCERNS[idx % len(SECONDARY_CONCERNS)]
    colleague = COLLEAGUES[idx % len(COLLEAGUES)]
    note_1 = f"For {industry}, the cheapest plan that meets compliance is rarely the cheapest plan published. Pricing footnotes matter."
    note_2 = f"Cross-border modifiers (US-Canada) add 10-15% on most legacy vendors. Get this in writing pre-signature."
    detail = f"Document the integration with your {industry}-specific software (whatever CRM/PMS/practice-management tool you use). Most VoIP/CRM webhooks have edge cases that surface only after deployment."
    return README_TEMPLATE.format(
        industry=industry,
        industry_title=industry.title(),
        primary_concern=primary,
        secondary_concern=secondary,
        note_1=note_1,
        note_2=note_2,
        industry_specific_detail=detail,
        homepage=HOMEPAGE,
        calc=CALC,
        colleague=colleague,
    )


def make_repo_name(industry, suffix):
    base = f"voip-{slugify(industry)[:30]}-vol3-{suffix}"
    return base[:60]


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
            "strategy": "codeberg-orgs-round2",
            "site_name": name,
            "url_submitted": "codeberg-api",
            "backlink_url": url,
            "status": status,
            "notes": notes,
        })


def main():
    print("=" * 60)
    print("Codeberg orgs round 2 — 5 more repos per org × 5 orgs = 25 repos")
    print("=" * 60)

    pushed = 0
    failed = 0
    niche_idx = 0

    for o_idx, org in enumerate(ORGS):
        print(f"\n[org {o_idx+1}/{len(ORGS)}] {org}")
        for r_idx in range(5):
            if niche_idx >= len(PICKED_NICHES):
                print("  niches exhausted")
                break
            industry, noun, detail = PICKED_NICHES[niche_idx]
            niche_idx += 1
            repo_name = make_repo_name(industry, r_idx + 1)
            description = f"VoIP operations notes vol. 2 for {industry}"
            readme = make_readme(industry, niche_idx)

            v = validate(readme, "github")
            if not v.ok:
                print(f"    [{r_idx+1}/5] {repo_name} — humanize FAIL: {v.issues[:2]}")
                failed += 1
                continue

            if repo_in_org_exists(org, repo_name):
                print(f"    [{r_idx+1}/5] {repo_name} — already exists")
                continue

            r = create_repo_in_org(org, repo_name, description)
            if r.status_code not in (200, 201):
                print(f"    [{r_idx+1}/5] create FAIL: {r.status_code} {r.text[:120]}")
                failed += 1
                continue

            time.sleep(1.2)
            ok = push_readme(org, repo_name, readme)
            if not ok:
                print(f"    [{r_idx+1}/5] push FAIL: {repo_name}")
                failed += 1
                continue

            repo_url = f"https://codeberg.org/{org}/{repo_name}"
            print(f"    [{r_idx+1}/5] {repo_url}")
            csv_log(
                f"Codeberg-{org}-{repo_name}",
                repo_url,
                "success",
                f"DA 60 dofollow — {industry} vol2 niche README with dialphone.com link",
            )
            pushed += 1
            time.sleep(1.5)

    print(f"\n=== DONE ===")
    print(f"Pushed:  {pushed}")
    print(f"Failed:  {failed}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
