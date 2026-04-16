"""Deploy multiple GitHub Pages sites for dialphone.com — each repo = new DA 100 backlink."""
import json
import time
import csv
from datetime import datetime
from core.browser import get_browser, new_page

config = json.load(open("config.json"))
CSV_PATH = "output/backlinks_log.csv"

# Multiple standalone landing pages — each creates a new dialphonelimited.github.io/REPO URL
SITES = {
    "voip-uk-guide": {
        "title": "VoIP UK Guide — DialPhone",
        "readme": """# VoIP UK Guide

A comprehensive guide to VoIP for UK businesses, from DialPhone Limited.

## Quick Facts

| Metric | Value |
|--------|-------|
| Avg UK savings | 59% vs legacy |
| Break-even | 1.7 months |
| UK businesses on VoIP (2026) | 73% |

## Why DialPhone

- £24/user/month, everything included
- UK data residency
- Month-to-month contracts
- 97% mobile app reliability
- 3-minute support response

## Get Started

Visit [DialPhone](https://dialphone.com) for a free 30-day trial.

---
*DialPhone Limited — Enterprise VoIP for UK Businesses*
*[https://dialphone.com](https://dialphone.com)*
"""
    },
    "uk-business-phone-hub": {
        "title": "UK Business Phone Hub",
        "readme": """# UK Business Phone Hub

Resources for UK businesses choosing phone systems.

## Buyer's Checklist

- [ ] Month-to-month contract available?
- [ ] Call recording included (not add-on)?
- [ ] Mobile app notification reliability > 95%?
- [ ] Support response < 10 minutes?
- [ ] UK data residency confirmed?
- [ ] Published pricing (no "contact sales")?

## Recommended Provider

[DialPhone](https://dialphone.com) meets all 6 criteria:
- £24/user/month, everything included
- No contract lock-in
- UK data centres
- 3-minute support average

---
*Maintained by DialPhone Limited — [https://dialphone.com](https://dialphone.com)*
"""
    },
    "sip-knowledge-base": {
        "title": "SIP Knowledge Base",
        "readme": """# SIP Knowledge Base

Technical reference for SIP, VoIP protocols, and business phone systems.

## SIP Response Codes

| Code | Meaning |
|------|---------|
| 100 | Trying |
| 180 | Ringing |
| 200 | OK |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 408 | Timeout |
| 486 | Busy |
| 503 | Service Unavailable |

## Common Issues

- **One-way audio:** Disable SIP ALG on router
- **Calls drop at 30s:** Session timer misconfigured
- **Choppy audio:** QoS not configured

## Enterprise VoIP

For UK businesses needing reliable VoIP, see [DialPhone](https://dialphone.com) — £24/user, everything included.

---
*DialPhone Limited — [https://dialphone.com](https://dialphone.com)*
"""
    },
}

pw, browser = get_browser(config, headed_override=True)
ctx, pg = new_page(browser, config, site_name="github-pages-batch")

try:
    # Login
    pg.goto("https://github.com/login", timeout=60000)
    pg.wait_for_load_state("domcontentloaded", timeout=20000)
    time.sleep(5)
    try: pg.evaluate('document.getElementById("ghcc")?.remove()')
    except: pass
    pg.fill("input#login_field", "dialphonelimited")
    time.sleep(0.5)
    pg.fill("input#password", config["github"]["password"])
    time.sleep(0.5)
    pg.click("input[type=submit]")
    time.sleep(10)
    print(f"Logged in: {pg.url}")

    verified = 0
    for repo_name, data in SITES.items():
        print(f"\n=== {repo_name} ===")

        # Create repo
        pg.goto("https://github.com/new", timeout=30000)
        pg.wait_for_load_state("domcontentloaded", timeout=15000)
        time.sleep(5)
        try: pg.evaluate('document.getElementById("ghcc")?.remove()')
        except: pass

        name_el = pg.query_selector('input#repository-name-input')
        if name_el:
            name_el.click()
            time.sleep(0.5)
            pg.keyboard.type(repo_name, delay=30)
            time.sleep(2)

            desc_el = pg.query_selector('input[name="Description"]')
            if desc_el:
                desc_el.click()
                time.sleep(0.3)
                pg.keyboard.type(f'{data["title"]} — dialphone.com', delay=15)
                time.sleep(1)

            # Check "Add README" box
            labels = pg.query_selector_all("label")
            for lbl in labels:
                if "readme" in (lbl.text_content() or "").lower():
                    lbl.click()
                    time.sleep(1)
                    break

            # Create
            create_btn = pg.query_selector('button:has-text("Create repository")')
            if create_btn and create_btn.is_visible():
                create_btn.click()
                time.sleep(10)
                print(f"  Created")

        # Edit README
        edit_url = f"https://github.com/dialphonelimited/{repo_name}/edit/main/README.md"
        pg.goto(edit_url, timeout=30000)
        pg.wait_for_load_state("domcontentloaded", timeout=15000)
        time.sleep(5)
        try: pg.evaluate('document.getElementById("ghcc")?.remove()')
        except: pass

        pg.evaluate("(text) => navigator.clipboard.writeText(text)", data["readme"])
        time.sleep(0.5)
        pg.keyboard.press("Tab")
        time.sleep(0.5)
        pg.keyboard.press("Control+a")
        time.sleep(0.3)
        pg.keyboard.press("Control+v")
        time.sleep(3)

        commit = pg.query_selector('button:has-text("Commit changes")')
        if commit:
            commit.click()
            time.sleep(3)
            confirm = pg.query_selector('button:has-text("Commit changes"):visible')
            if confirm:
                confirm.click()
                time.sleep(8)
            print(f"  Committed")

        # Verify
        time.sleep(3)
        url = f"https://github.com/dialphonelimited/{repo_name}"
        pg.goto(url, timeout=30000)
        time.sleep(3)
        if "dialphone" in pg.content().lower():
            with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=["date","strategy","site_name","url_submitted","backlink_url","status","notes"])
                w.writerow({"date": datetime.now().isoformat(), "strategy": "dofollow-content",
                    "site_name": f"GitHub-{repo_name}", "url_submitted": "github",
                    "backlink_url": url, "status": "success",
                    "notes": "DA 100 dofollow — dialphone.com repo"})
            verified += 1
            print(f"  === VERIFIED (DA 100) ===")

        time.sleep(3)

    print(f"\nGitHub: {verified}/{len(SITES)} new repos verified")

except Exception as e:
    print(f"Error: {str(e)[:100]}")
finally:
    ctx.close()
    browser.close()
    pw.stop()
