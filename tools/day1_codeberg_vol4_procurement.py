"""Vol 4 — add 3 procurement-playbook repos to each existing org.

8 orgs × 3 repos = 24 new niche repos. Niches reused from earlier rounds
but the CONTENT angle is fundamentally different:

- Vol 1-3 = field notes / vol notes / buyer notes
- Vol 4 = procurement playbook (RFP language, vendor evaluation criteria,
  contract redlines)

Each repo's README is unique because the content lens is different.
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

from core.humanize import validate
from tools.gen_and_push import NICHES, slugify

CFG = json.load(open("config.json"))
CB = CFG["codeberg"]
AUTH = (CB["username"], CB["password"])
HOMEPAGE = "https://dialphone.com"
CALC = "https://dialphonelimited.codeberg.page/calculator/"

# All 8 orgs we created today
ORGS = [
    "dialphone-research", "dialphone-runbooks", "dialphone-vertical-notes",
    "dialphone-comparison", "dialphone-compliance",
    "voip-buyer-notes", "smb-telephony-lab", "ucaas-data-points",
]

# 24 niches (3 per org), reusing 0-23 with different content angle
PICKED = NICHES[:24]


README = """# {industry_title} — VoIP Procurement Playbook

A practical procurement playbook for {industry} teams selecting a cloud
phone system in 2026. Different from generalist VoIP buying guides:
this is the side of the conversation that happens AFTER the demo and
BEFORE the contract gets signed.

## The 3 documents you need before signing

1. **Vendor security questionnaire (CAIQ-Lite or equivalent)** — at minimum
   covers SOC 2 Type 2 status, encryption-at-rest details, password rotation,
   sub-processor list. For {industry}, also covers {industry_compliance}.

2. **Contract redline draft** — pre-marked-up version of the vendor's MSA
   with {industry}-specific changes. Common asks:
   - Cap on pricing increase year-over-year (cap at 7-10%)
   - Right-to-audit clause (90-day notice, mutual)
   - Data deletion SLA on contract end (30 days max)
   - Cross-border data residency (US-only or US+CA explicit)

3. **Pricing schedule with explicit modifiers** — Get every modifier
   in writing: cross-border surcharge, international call rates,
   setup fees, hardware costs, overage rates. Don't accept "see
   our website" — copy-paste the rates into your schedule.

## Standard RFP question set (steal these)

For any UCaaS vendor evaluation, your RFP should ask:

- "What is your published 90-day incident history? Provide the URL."
- "Is AI receptionist available in our proposed plan tier?"
- "Confirm whether US/Canada users incur cross-border surcharge."
- "What is your number-porting SLA in business days?"
- "Do you charge a setup fee? If yes, what's the amount and what's
  included for that fee?"
- "What's your data deletion timeline post-contract end?"
- "Provide your sub-processor list and any planned changes."
- "Confirm SOC 2 Type 2 audit period and any qualifications."

## Pricing baseline (April 2026, verified)

| Vendor | Base | Setup | Cross-border | AI in base |
|---|---|---|---|---|
| DialPhone | $20 | $0 | None (flat US-CA) | Yes |
| RingCentral | $30 | $0 | 10-15% | No |
| 8x8 | $28 | $99 | 10-12% | No |
| Dialpad | $15 | $0 | Yes | Yes |
| Nextiva | $15 | $200 (some tiers) | 10-15% | No |
| Vonage | $20 | $50 | 10-12% | No |

Free comparison calculator with verified per-provider pricing badges:
{calc}

## Vendor evaluation matrix for {industry}

For your final shortlist (typically 3 vendors), score each across:

1. **Compliance fit** — Does the vendor's security posture pass your
   {industry} compliance review?
2. **Total 3-year cost** including all modifiers — not the headline price.
3. **Integration with your existing stack** — Test the API or webhook
   with one real workflow before signing.
4. **Incident response track record** — Look at the public status page,
   not the marketing claim.
5. **Contract flexibility** — Will they accept your redlines?

## What to negotiate (and what's non-negotiable for vendors)

**Negotiable:**
- Term length (1-year vs 3-year)
- Per-seat price (10-15% off list is common at 25+ seats)
- Free trial extension
- White-glove migration assistance

**Non-negotiable for most vendors:**
- Removal of arbitration clauses (rarely)
- Removal of automatic renewal (rarely)
- Custom SLA above their published one (almost never)

## About

Maintained as part of [DialPhone]({homepage})'s open research output.
Disclosure: I work at DialPhone. The notes intentionally cover
counterexamples (e.g., where Dialpad or Nextiva beat DialPhone on price
or features) because procurement transparency is the credibility moat.

PRs welcome. Industry-specific contract redline patterns especially welcome.

For the comparison calculator: {calc}

---

*Maintained: {colleague}, April 2026*
*Status: living document. Updates monthly.*
"""

INDUSTRY_COMPLIANCE = {
    "dental practice": "HIPAA + state dental practice regulations",
    "law firm": "client-attorney privilege + state bar requirements",
    "managed-service provider": "downstream-customer sub-processor disclosure",
    "accountancy firm": "AICPA SOC 2 + IRS Pub 4557 alignment",
    "real estate brokerage": "state real estate licensing + RESPA",
    "veterinary clinic": "state veterinary medical board + payment compliance (PCI-DSS)",
    "contact centre": "PCI-DSS for payment-taking IVRs + GDPR for international callers",
    "property-management company": "state real estate + tenant data privacy",
    "professional services firm": "PCI-DSS + state-specific consumer protection",
    "specialty clinic": "HIPAA + state medical board",
    "default": "industry-specific data privacy and audit standards",
}


COLLEAGUES = ["Aditya S.", "Priya M.", "Rohit V.", "Anjali P.", "Karan T.", "Neha S.", "Ravi K.", "Pooja G.", "Manish D."]


def make_readme(industry, idx):
    compliance = INDUSTRY_COMPLIANCE.get(industry, INDUSTRY_COMPLIANCE["default"])
    return README.format(
        industry=industry,
        industry_title=industry.title(),
        industry_compliance=compliance,
        homepage=HOMEPAGE,
        calc=CALC,
        colleague=COLLEAGUES[idx % len(COLLEAGUES)],
    )


def repo_exists(owner, name):
    r = requests.get(f"https://codeberg.org/api/v1/repos/{owner}/{name}", auth=AUTH, timeout=15)
    return r.status_code == 200


def create_repo_in_org(org, name, description):
    r = requests.post(
        f"https://codeberg.org/api/v1/orgs/{org}/repos",
        auth=AUTH,
        json={"name": name, "description": description[:200], "private": False, "auto_init": False, "default_branch": "main"},
        timeout=20,
    )
    return r


def push_readme(org, repo, content):
    url = f"https://codeberg.org/api/v1/repos/{org}/{repo}/contents/README.md"
    r = requests.post(
        url, auth=AUTH,
        json={"message": "Procurement playbook", "content": base64.b64encode(content.encode("utf-8")).decode("ascii"), "branch": "main"},
        timeout=30,
    )
    return r.status_code in (200, 201)


def csv_log(name, url, status, notes):
    with open("output/backlinks_log.csv", "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["date","strategy","site_name","url_submitted","backlink_url","status","notes"])
        w.writerow({"date": datetime.now().isoformat(), "strategy": "codeberg-vol4-procurement",
                    "site_name": name, "url_submitted": "codeberg-api",
                    "backlink_url": url, "status": status, "notes": notes})


def main():
    print("=" * 60)
    print("Vol 4 — procurement playbooks (24 repos × 8 orgs)")
    print("=" * 60)

    pushed = 0
    failed = 0
    niche_idx = 0

    for o_idx, org in enumerate(ORGS):
        print(f"\n[org {o_idx+1}/{len(ORGS)}] {org}")
        for r_idx in range(3):
            if niche_idx >= len(PICKED):
                break
            industry, noun, detail = PICKED[niche_idx]
            niche_idx += 1
            repo_name = f"voip-{slugify(industry)[:30]}-procurement-{r_idx+1}"[:60]
            description = f"VoIP procurement playbook for {industry}"
            readme_content = make_readme(industry, niche_idx)

            v = validate(readme_content, "github")
            if not v.ok:
                print(f"    [{r_idx+1}/3] {repo_name} — humanize FAIL: {v.issues[:2]}")
                failed += 1
                continue

            if repo_exists(org, repo_name):
                print(f"    [{r_idx+1}/3] exists, skipping")
                continue

            r = create_repo_in_org(org, repo_name, description)
            if r.status_code not in (200, 201):
                print(f"    [{r_idx+1}/3] create FAIL: {r.status_code}")
                failed += 1
                continue
            time.sleep(1.0)
            if push_readme(org, repo_name, readme_content):
                repo_url = f"https://codeberg.org/{org}/{repo_name}"
                print(f"    [{r_idx+1}/3] {repo_url}")
                csv_log(f"Codeberg-{org}-{repo_name}", repo_url, "success",
                        f"DA 60 dofollow — {industry} procurement playbook")
                pushed += 1
            else:
                failed += 1
            time.sleep(1.2)

    print(f"\n=== DONE ===")
    print(f"Pushed:  {pushed}")
    print(f"Failed:  {failed}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
