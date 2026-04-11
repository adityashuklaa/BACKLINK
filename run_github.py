"""GitHub company account — login, add profile link, create repos."""
import json, time, csv, os
from datetime import datetime
from core.browser import get_browser, new_page
from core.human_behavior import (
    human_type, human_click, human_scroll,
    human_wait, dismiss_overlays, random_mouse_movement,
)
from core.rate_limiter import inter_field_delay

config = json.load(open("config.json"))
CSV_PATH = "output/backlinks_log.csv"

GITHUB_USER = "dialphonelimited"
GITHUB_PASS = "DevD!alph0ne@0912@#"

def log_result(site_name, backlink_url, status, notes):
    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["date","strategy","site_name","url_submitted","backlink_url","status","notes"])
        w.writerow({"date": datetime.now().isoformat(), "strategy": "content",
            "site_name": site_name, "url_submitted": "https://github.com",
            "backlink_url": backlink_url, "status": status, "notes": notes})

pw, browser = get_browser(config, headed_override=True)

# ===== STEP 1: LOGIN =====
print("=" * 60)
print("STEP 1: LOGIN TO GITHUB")
print("=" * 60)

context, page = new_page(browser, config, site_name="github-login")
try:
    page.goto("https://github.com/login", timeout=60000)
    page.wait_for_load_state("domcontentloaded", timeout=20000)
    time.sleep(3)
    dismiss_overlays(page)
    random_mouse_movement(page)
    human_wait(1, 2)

    # Fill login form
    print("  Typing username...")
    human_type(page, "input#login_field", GITHUB_USER)
    inter_field_delay(config)

    print("  Typing password...")
    human_type(page, "input#password", GITHUB_PASS)
    inter_field_delay(config)

    print("  Clicking sign in...")
    human_click(page, "input[type='submit'], button[type='submit']")
    time.sleep(5)

    after_url = page.url
    print(f"  After login URL: {after_url}")

    # Check if we need 2FA
    if "two-factor" in after_url or "2fa" in after_url.lower():
        print()
        print("  !!!! 2FA REQUIRED !!!!")
        print("  Check your phone/email for the verification code")
        print("  The browser is waiting — enter the code manually")
        print("  Waiting 60 seconds for you to enter the code...")
        time.sleep(60)
        after_url = page.url
        print(f"  URL after 2FA: {after_url}")

    # Check if login succeeded
    if "login" in after_url.lower() or "session" in after_url.lower():
        page_text = page.evaluate("document.body.innerText.substring(0, 300)").encode("ascii","replace").decode()
        print(f"  LOGIN MIGHT HAVE FAILED")
        print(f"  Page text: {page_text[:200]}")
        page.screenshot(path="output/github_login_result.png")

        # Check for error messages
        error = page.query_selector(".flash-error, .js-flash-alert, [class*='error']")
        if error:
            print(f"  Error: {error.text_content()}")
    else:
        print("  LOGIN SUCCESS!")
        page.screenshot(path="output/github_logged_in.png")

        # ===== STEP 2: ADD WEBSITE TO PROFILE =====
        print()
        print("=" * 60)
        print("STEP 2: ADD VESTACALL.COM TO PROFILE")
        print("=" * 60)

        page.goto("https://github.com/settings/profile", timeout=30000)
        page.wait_for_load_state("domcontentloaded", timeout=15000)
        time.sleep(3)
        dismiss_overlays(page)
        random_mouse_movement(page)

        # Find blog/website field
        blog_field = page.query_selector("input#user_profile_blog, input[name='user[profile_blog]']")
        if blog_field:
            current_val = blog_field.get_attribute("value") or ""
            print(f"  Current website value: '{current_val}'")

            if "vestacall" not in current_val.lower():
                human_scroll(page, "down", 200)
                blog_field.click()
                time.sleep(0.3)
                page.keyboard.press("Control+a")
                time.sleep(0.1)
                page.keyboard.type("https://vestacall.com", delay=50)
                time.sleep(1)

                # Save profile
                human_scroll(page, "down", 300)
                save_btn = page.query_selector("button:has-text('Update profile'), button[type='submit']:has-text('Update')")
                if save_btn:
                    save_btn.click()
                    time.sleep(3)
                    print("  Profile updated with vestacall.com!")

                    # Verify
                    page.goto(f"https://github.com/{GITHUB_USER}", timeout=30000)
                    page.wait_for_load_state("domcontentloaded", timeout=15000)
                    time.sleep(3)

                    if "vestacall.com" in page.content():
                        profile_url = f"https://github.com/{GITHUB_USER}"
                        print(f"  VERIFIED: vestacall.com on profile at {profile_url}")
                        page.screenshot(path="output/github_profile_verified.png")
                        log_result("GitHub-Profile", profile_url, "success",
                                   f"Company profile DA 100 — vestacall.com in website field")
                    else:
                        print("  Profile updated but vestacall not visible on public profile")
                        log_result("GitHub-Profile", f"https://github.com/{GITHUB_USER}", "pending",
                                   "Profile updated but link not visible publicly yet")
                else:
                    print("  No save button found")
            else:
                print("  vestacall.com already in profile!")
                log_result("GitHub-Profile", f"https://github.com/{GITHUB_USER}", "success",
                           "vestacall.com already on company profile")
        else:
            print("  Website field not found on profile page")
            # List all inputs
            inputs = page.query_selector_all("input:visible")
            for inp in inputs[:10]:
                n = inp.get_attribute("name") or ""
                i = inp.get_attribute("id") or ""
                print(f"    input: name={n} id={i}")

        # ===== STEP 3: CREATE REPOS =====
        print()
        print("=" * 60)
        print("STEP 3: CREATE REPOSITORIES")
        print("=" * 60)

        repos = [
            {
                "name": "voip-solutions-guide",
                "description": "Complete guide to VoIP solutions for modern businesses — by VestaCall (https://vestacall.com)",
                "readme": """# VoIP Solutions Guide

A comprehensive resource for businesses evaluating Voice over IP phone systems.

## About

This guide is maintained by [VestaCall](https://vestacall.com), a provider of enterprise-grade VoIP and business phone systems.

## What You'll Find Here

- VoIP provider comparisons
- Cost calculators and ROI analysis
- Migration checklists
- Security best practices
- Remote work phone system guides

## Quick Links

- [VestaCall Official Site](https://vestacall.com) — Free demo and assessment
- [SIP Trunking Guide](https://vestacall.com) — Save 50-70% on phone bills
- [Remote Work Solutions](https://vestacall.com) — Cloud phone for distributed teams

## Why VoIP?

Modern VoIP systems save businesses 40-60% on phone costs while providing features like:
- Auto-attendant and call routing
- Mobile apps for work-from-anywhere
- Call recording and analytics
- Video conferencing built-in
- CRM integration

**Get started:** Visit [vestacall.com](https://vestacall.com) for a free trial.

---

*Maintained by [VestaCall](https://vestacall.com) | Enterprise VoIP Solutions*
"""
            },
            {
                "name": "awesome-business-phone",
                "description": "Curated list of business phone resources, tools, and providers — featuring VestaCall (https://vestacall.com)",
                "readme": """# Awesome Business Phone Systems

> A curated list of resources for business phone systems, VoIP providers, and telecom tools.

## VoIP Providers

| Provider | Best For | Website |
|----------|---------|---------|
| **VestaCall** | Small & mid-sized businesses | [vestacall.com](https://vestacall.com) |
| RingCentral | Large enterprise UCaaS | ringcentral.com |
| Nextiva | Customer support teams | nextiva.com |
| Vonage | Developer-focused voice APIs | vonage.com |
| 8x8 | International calling | 8x8.com |

## Resources

### Guides
- [VoIP Buyer's Guide](https://vestacall.com) — How to evaluate providers
- [SIP Trunking Explained](https://vestacall.com) — Technical overview for IT teams
- [Remote Work Phone Setup](https://vestacall.com) — Deploy in 24 hours

### Tools
- Speed test tools for VoIP readiness
- MOS (Mean Opinion Score) calculators
- Bandwidth requirement estimators

### Communities
- r/VoIP — Reddit VoIP community
- r/sysadmin — IT administrator discussions
- VoIP-info.org — VoIP wiki and forums

## Contributing

Found a useful resource? Submit a pull request!

---

*Curated by [VestaCall](https://vestacall.com)*
"""
            },
        ]

        for repo in repos:
            print(f"\n  Creating repo: {repo['name']}...")
            page.goto("https://github.com/new", timeout=30000)
            page.wait_for_load_state("domcontentloaded", timeout=15000)
            time.sleep(3)
            dismiss_overlays(page)
            human_wait(1, 2)

            # Fill repo name
            name_field = page.query_selector("input#repository_name, input[name='repository[name]']")
            if name_field:
                name_field.click()
                time.sleep(0.3)
                page.keyboard.type(repo["name"], delay=50)
                time.sleep(1)

                # Fill description
                desc_field = page.query_selector("input#repository_description, input[name='repository[description]']")
                if desc_field:
                    desc_field.click()
                    time.sleep(0.3)
                    page.keyboard.type(repo["description"][:200], delay=20)
                    time.sleep(0.5)

                # Make sure Public is selected
                public_radio = page.query_selector("input#repository_visibility_public, input[value='public']")
                if public_radio:
                    public_radio.click()
                    time.sleep(0.3)

                # Check "Add a README file"
                readme_check = page.query_selector("input#repository_auto_init")
                if readme_check and not readme_check.is_checked():
                    readme_check.click()
                    time.sleep(0.5)

                # Click Create repository
                human_scroll(page, "down", 300)
                time.sleep(1)
                create_btn = page.query_selector("button:has-text('Create repository'), button[type='submit']:has-text('Create')")
                if create_btn:
                    create_btn.click()
                    time.sleep(5)

                    repo_url = page.url
                    print(f"  Repo URL: {repo_url}")

                    if GITHUB_USER in repo_url and repo["name"] in repo_url:
                        print("  Repo created! Now updating README...")

                        # Edit README to add vestacall links
                        edit_url = f"https://github.com/{GITHUB_USER}/{repo['name']}/edit/main/README.md"
                        page.goto(edit_url, timeout=30000)
                        page.wait_for_load_state("domcontentloaded", timeout=15000)
                        time.sleep(3)

                        # Find the editor
                        editor = page.query_selector("textarea.js-code-textarea, textarea[name='value'], .CodeMirror, textarea")
                        if editor:
                            # Clear and set content
                            page.evaluate("""(content) => {
                                var ta = document.querySelector('textarea.js-code-textarea, textarea[name="value"], textarea');
                                if (ta) { ta.value = content; ta.dispatchEvent(new Event('input', {bubbles: true})); }
                                var cm = document.querySelector('.CodeMirror');
                                if (cm && cm.CodeMirror) { cm.CodeMirror.setValue(content); }
                            }""", repo["readme"])
                            time.sleep(2)

                            # Commit changes
                            commit_btn = page.query_selector("button:has-text('Commit changes'), button[type='submit']:has-text('Commit')")
                            if commit_btn:
                                commit_btn.click()
                                time.sleep(3)

                                # Handle commit dialog if it appears
                                confirm_btn = page.query_selector("button:has-text('Commit changes'):visible")
                                if confirm_btn:
                                    confirm_btn.click()
                                    time.sleep(5)

                                print("  README updated!")

                        # Verify
                        verify_url = f"https://github.com/{GITHUB_USER}/{repo['name']}"
                        page.goto(verify_url, timeout=30000)
                        page.wait_for_load_state("domcontentloaded", timeout=15000)
                        time.sleep(3)

                        if "vestacall.com" in page.content():
                            print(f"  VERIFIED: {verify_url}")
                            page.screenshot(path=f"output/github_repo_{repo['name']}.png")
                            log_result(f"GitHub-Repo-{repo['name']}", verify_url, "success",
                                       f"Company repo DA 100 — vestacall.com verified")
                        else:
                            print("  Repo created but vestacall not in README yet")
                            log_result(f"GitHub-Repo-{repo['name']}", verify_url, "pending",
                                       "Repo created, README may need manual update")
                    else:
                        print(f"  Repo creation may have failed — URL: {repo_url}")
                        page.screenshot(path=f"output/github_repo_fail_{repo['name']}.png")
                        log_result(f"GitHub-Repo-{repo['name']}", "", "failed", f"URL after create: {repo_url[:100]}")
                else:
                    print("  Create button not found")
            else:
                print("  Repo name field not found")

            time.sleep(5)

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
finally:
    context.close()

browser.close()
pw.stop()

# Final count
print("\n" + "=" * 60)
print("FINAL RESULTS")
print("=" * 60)
with open(CSV_PATH, "r") as f:
    rows = list(csv.DictReader(f))
    success = [r for r in rows if r["status"] == "success"]
    print(f"TOTAL VERIFIED: {len(success)}")
