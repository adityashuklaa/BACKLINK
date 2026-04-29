"""Day 1 Stack Overflow profile setup.

Logs into Stack Overflow using the creds we have, edits the profile to add
website link (dialphone.com) + a real-sounding bio. The profile-page link
is dofollow on Stack Overflow Network sites = 1 DA-93 backlink.

Steps:
1. Navigate to stackoverflow.com/users/login
2. Fill email + password
3. Solve any captcha (we'll fail and report)
4. Navigate to /users/edit/<id>
5. Fill: Display Name, Location, Title, About Me (with dialphone.com link),
   Website URL = https://dialphone.com
6. Save
"""
import csv
import json
import sys
import time
from datetime import datetime

sys.path.insert(0, ".")
sys.stdout.reconfigure(encoding="utf-8")

from core.browser import get_browser, new_page

CFG = json.load(open("config.json"))

# Credentials
EMAIL = "commercial@dialphone.com"
PASSWORD = "4Ght2g@aQmCeb6t"

# Profile content
DISPLAY_NAME = "Aditya Shukla"
LOCATION = "United States"
TITLE_TAG = "Growth Operations @ DialPhone"
ABOUT_ME = """Growth Operations at [DialPhone](https://dialphone.com), a US/Canada business VoIP provider founded in 2024.

I work mostly on the operations side of cloud telephony — SIP trunking, number porting, AI receptionist deployments, CRM integrations for SMB customers. Happy to answer questions on:

- VoIP / UCaaS migration patterns
- Business phone APIs (RingCentral, Twilio, Vonage)
- AI in customer service (receptionist routing, voice triage)
- US/Canada compliance (SOC 2, HIPAA, PCI-DSS for telecom)

Free comparison tool we built for buyers evaluating 13 VoIP providers: https://dialphonelimited.codeberg.page/calculator/"""
WEBSITE = "https://dialphone.com"


def csv_log(url, status, notes):
    with open("output/backlinks_log.csv", "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=["date", "strategy", "site_name", "url_submitted", "backlink_url", "status", "notes"],
        )
        w.writerow({
            "date": datetime.now().isoformat(),
            "strategy": "stackoverflow-profile",
            "site_name": "StackOverflow-Aditya-Profile",
            "url_submitted": "stackoverflow.com",
            "backlink_url": url,
            "status": status,
            "notes": notes,
        })


def main():
    pw, browser = get_browser(CFG, headed_override=False)
    ctx, page = new_page(browser, CFG, "stackoverflow-profile")

    print("=" * 60)
    print("Day 1 — Stack Overflow profile setup")
    print("=" * 60)

    try:
        # Step 1: log in
        print("\n[1] Navigating to Stack Overflow login...")
        page.goto("https://stackoverflow.com/users/login", wait_until="domcontentloaded", timeout=25000)
        page.wait_for_timeout(3500)

        # Detect anti-bot
        title = page.title()
        body = page.inner_text("body").lower()[:500]
        print(f"  page title: {title[:80]}")

        if "just a moment" in body or "cloudflare" in body:
            print("  CLOUDFLARE CHALLENGE — cannot proceed autonomously")
            return ("cloudflare_blocked", "Stack Overflow login behind Cloudflare challenge")

        # Find email/password fields
        email_field = page.query_selector("#email") or page.query_selector("input[type='email'], input[name='email']")
        if not email_field:
            print("  no email field found — login form layout may have changed")
            page.screenshot(path="output/stackoverflow_login_page.png")
            return ("login_form_missing", "couldn't find email field")
        email_field.fill(EMAIL)
        print(f"  filled email: {EMAIL}")

        password_field = page.query_selector("#password") or page.query_selector("input[type='password']")
        if not password_field:
            print("  no password field found")
            return ("login_form_missing", "couldn't find password field")
        password_field.fill(PASSWORD)
        print(f"  filled password (16 chars)")

        # Submit
        submit_btn = page.query_selector("button#submit-button, button[type='submit'], button:has-text('Log in')")
        if submit_btn:
            submit_btn.click()
            print("  clicked submit")
        else:
            # Try keyboard Enter
            page.keyboard.press("Enter")
            print("  pressed Enter")

        page.wait_for_timeout(6000)
        post_login_url = page.url
        post_login_body = page.inner_text("body").lower()[:1000]
        print(f"  post-login URL: {post_login_url}")

        # Detect captcha after submit
        if "captcha" in post_login_body or "recaptcha" in post_login_body or "verify" in post_login_body[:300]:
            print("  CAPTCHA appeared after submit — manual solve needed")
            page.screenshot(path="output/stackoverflow_captcha.png")
            return ("captcha_blocked", "reCAPTCHA on login")

        # Detect login failure
        if "/users/login" in post_login_url and ("error" in post_login_body or "incorrect" in post_login_body):
            print("  LOGIN FAILED — bad credentials")
            page.screenshot(path="output/stackoverflow_login_fail.png")
            return ("auth_failed", "credentials rejected")

        # Detect login success — should redirect to home or user page
        if "/users/login" in post_login_url:
            print(f"  Still on login page — checking form state")
            page.screenshot(path="output/stackoverflow_post_submit.png")
            return ("login_unclear", "stayed on login page after submit")

        print(f"\n[2] Login appears successful")

        # Find our user ID
        # Stack Overflow stores user info in the global site nav
        user_id = page.evaluate("""() => {
            // The user-card link in the top nav contains '/users/<id>/<name>'
            const a = document.querySelector('a.s-user-card--link, a[href*=\"/users/\"][href*=\"/edit\"]');
            if (a) {
                const m = a.href.match(/\\/users\\/(\\d+)/);
                return m ? m[1] : null;
            }
            // Fallback: any /users/ link in nav
            const nav = document.querySelector('header, .top-bar');
            if (!nav) return null;
            const links = [...nav.querySelectorAll('a[href*=\"/users/\"]')];
            for (const l of links) {
                const m = l.href.match(/\\/users\\/(\\d+)/);
                if (m) return m[1];
            }
            return null;
        }""")
        print(f"  user_id: {user_id}")
        if not user_id:
            print("  couldn't find user ID — login may not have completed")
            return ("no_user_id", "login flow ambiguous")

        # Step 3: edit profile
        edit_url = f"https://stackoverflow.com/users/edit/{user_id}"
        print(f"\n[3] Going to {edit_url}")
        page.goto(edit_url, wait_until="domcontentloaded", timeout=20000)
        page.wait_for_timeout(3000)

        # Fill profile fields
        for sel, val, label in [
            ("input[name='DisplayName'], #displayNameInput", DISPLAY_NAME, "display name"),
            ("input[name='Location'], #locationInput", LOCATION, "location"),
            ("input[name='Title'], #titleInput", TITLE_TAG, "title tagline"),
            ("input[name='WebsiteUrl'], #websiteUrlInput", WEBSITE, "website URL"),
            ("textarea[name='AboutMe'], #aboutMeInput", ABOUT_ME, "about me"),
        ]:
            try:
                el = page.query_selector(sel)
                if el and el.is_visible():
                    el.fill("")  # clear
                    el.fill(val)
                    print(f"    filled {label}")
                else:
                    print(f"    {label} field not found ({sel})")
            except Exception as e:
                print(f"    {label} failed: {e}")

        # Save
        save_btn = page.query_selector("button:has-text('Save'), button[type='submit']")
        if save_btn:
            save_btn.click()
            print("  clicked save")
            page.wait_for_timeout(4000)
        else:
            print("  no save button found")
            return ("save_button_missing", "couldn't save profile")

        profile_url = f"https://stackoverflow.com/users/{user_id}"
        print(f"\n[4] Profile URL: {profile_url}")

        # Verify website link is on profile
        page.goto(profile_url, wait_until="domcontentloaded", timeout=15000)
        page.wait_for_timeout(2500)
        body_now = page.inner_text("body")
        has_dialphone = "dialphone.com" in body_now.lower()
        print(f"  dialphone.com on profile: {has_dialphone}")
        page.screenshot(path="output/stackoverflow_profile_after.png")

        if has_dialphone:
            csv_log(profile_url, "success",
                    "DA 93 dofollow profile backlink — bio + website link to dialphone.com")
            print(f"\nSUCCESS — backlink logged")
            return ("success", profile_url)
        else:
            return ("save_did_not_persist", "profile saved but dialphone.com not on rendered profile")

    except Exception as e:
        print(f"\nEXCEPTION: {e}")
        return ("exception", str(e)[:200])
    finally:
        try: ctx.close(); browser.close(); pw.stop()
        except: pass


if __name__ == "__main__":
    status, info = main()
    print(f"\nResult: {status} | {info}")
