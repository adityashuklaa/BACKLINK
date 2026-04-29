"""Quick login probe — for each credential, attempt login and report whether
the account actually exists. Doesn't post anything. Just verifies which
credentials are usable so we know where to invest Playwright effort.
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

# Credentials from chat-shared sheet (sample)
TARGETS = [
    {
        "platform": "stackoverflow",
        "url": "https://stackoverflow.com/users/login",
        "email_sel": "input[type='email']",
        "pwd_sel": "input[type='password']",
        "submit_sel": "button#submit-button, button[type='submit']",
        "email": "commercial@dialphone.com",
        "password": "4Ght2g@aQmCeb6t",
    },
    {
        "platform": "diigo",
        "url": "https://www.diigo.com/sign-in",
        "email_sel": "input[name='Username'], input[name='username'], input[type='email']",
        "pwd_sel": "input[name='Password'], input[name='password'], input[type='password']",
        "submit_sel": "button[type='submit'], input[type='submit']",
        "email": "commercial@dialphone.com",
        "password": "g@a%.X4Ght2bDdn3",
    },
    {
        "platform": "indiehackers",
        "url": "https://www.indiehackers.com/login",
        "email_sel": "input[type='email']",
        "pwd_sel": "input[type='password']",
        "submit_sel": "button[type='submit']",
        "email": "commercial@dialphone.com",
        "password": "@Rt4^Ght2g@Ddn3eW",
    },
    {
        "platform": "spiceworks",
        "url": "https://community.spiceworks.com/login",
        "email_sel": "input[type='email']",
        "pwd_sel": "input[type='password']",
        "submit_sel": "button[type='submit']",
        "email": "commercial@dialphone.com",
        "password": "Vf#~Kzqq&5sX3-T",
    },
    {
        "platform": "tumblr",
        "url": "https://www.tumblr.com/login",
        "email_sel": "input[name='email'], input[type='email']",
        "pwd_sel": "input[name='password'], input[type='password']",
        "submit_sel": "button[type='submit']",
        "email": "commercial@dialphone.com",
        "password": "g@a%.X4Ght2bDdn3",
    },
    {
        "platform": "gitea",
        "url": "https://gitea.com/user/login",
        "email_sel": "input[name='user_name'], input[type='text']",
        "pwd_sel": "input[name='password']",
        "submit_sel": "button[type='submit']",
        "email": "dialphone",  # gitea uses username not email
        "password": "KSzbqiEBm&$G3JZC10j1",
    },
    {
        "platform": "notabug",
        "url": "https://notabug.org/user/login",
        "email_sel": "input[name='user_name'], input[type='text']",
        "pwd_sel": "input[name='password']",
        "submit_sel": "button[type='submit']",
        "email": "dialphone",
        "password": "PEXd$6qEQ1S1M*0NH*g3",
    },
]


def detect_state(page, body, url, platform):
    """Read post-submit state to classify outcome."""
    body_lower = body.lower()
    if any(x in body_lower for x in ["captcha", "recaptcha", "hcaptcha", "are you a robot"]):
        return "captcha_required"
    if "cloudflare" in body_lower[:500] or "just a moment" in body_lower[:500]:
        return "cloudflare_challenge"
    if any(x in body_lower for x in [
        "incorrect password", "wrong password", "invalid credentials",
        "incorrect email", "wrong email", "invalid email",
        "no account", "doesn't exist", "not found",
        "password is incorrect", "couldn't sign you in",
    ]):
        return "auth_failed_or_no_account"
    if "/login" in url or "/sign-in" in url or "/sign_in" in url:
        return "still_on_login_page"
    return "appears_logged_in"


def main():
    pw, browser = get_browser(CFG, headed_override=False)
    ctx, page = new_page(browser, CFG, "verify-accounts")
    results = []

    for t in TARGETS:
        plat = t["platform"]
        print(f"\n--- {plat} ---")
        try:
            page.goto(t["url"], wait_until="domcontentloaded", timeout=20000)
            page.wait_for_timeout(3000)
            title = page.title()
            print(f"  page title: {title[:80]}")

            # Body sample
            body_pre = page.evaluate("document.body.innerText")[:500].lower()
            if "captcha" in body_pre or "cloudflare" in body_pre[:500]:
                results.append({"platform": plat, "status": "blocked_pre_login", "notes": "CAPTCHA or Cloudflare on login page"})
                print(f"  BLOCKED: {body_pre[:120]}")
                continue

            # Try filling the form
            email_field = page.query_selector(t["email_sel"])
            pwd_field = page.query_selector(t["pwd_sel"])
            if not email_field:
                print(f"  email field not found ({t['email_sel']})")
                results.append({"platform": plat, "status": "form_layout_unknown", "notes": "email field selector miss"})
                continue
            if not pwd_field:
                print(f"  password field not found ({t['pwd_sel']})")
                results.append({"platform": plat, "status": "form_layout_unknown", "notes": "password field selector miss"})
                continue

            # On Diigo and similar, the email field comes first then a 'Continue' button before password
            # If password field is hidden, try filling email first and clicking continue
            try:
                email_field.fill(t["email"])
                print(f"  filled email")
            except Exception as e:
                print(f"  fill email failed: {e}")

            try:
                if pwd_field.is_visible():
                    pwd_field.fill(t["password"])
                    print(f"  filled password")
                else:
                    # Click any "Continue" / "Next" button
                    cont = page.query_selector("button:has-text('Continue'), button:has-text('Next'), button[type='submit']")
                    if cont:
                        cont.click()
                        page.wait_for_timeout(2500)
                        # Now password field should be visible
                        pwd2 = page.query_selector(t["pwd_sel"])
                        if pwd2 and pwd2.is_visible():
                            pwd2.fill(t["password"])
                            print(f"  filled password (after Continue)")
            except Exception as e:
                print(f"  password fill issue: {e}")

            # Submit
            submit = page.query_selector(t["submit_sel"])
            if submit:
                try:
                    submit.click(timeout=8000)
                    print(f"  clicked submit")
                except Exception as e:
                    page.keyboard.press("Enter")
                    print(f"  click failed, pressed Enter")
            else:
                page.keyboard.press("Enter")
                print(f"  no submit button, pressed Enter")

            page.wait_for_timeout(6000)
            post_url = page.url
            post_body = page.evaluate("document.body.innerText")[:1500]
            state = detect_state(page, post_body, post_url, plat)
            print(f"  post_url: {post_url[:90]}")
            print(f"  state: {state}")
            results.append({"platform": plat, "status": state, "notes": post_body[:200]})

        except Exception as e:
            print(f"  EXC: {str(e)[:120]}")
            results.append({"platform": plat, "status": "exception", "notes": str(e)[:200]})

    print("\n" + "=" * 70)
    print("VERIFICATION SUMMARY")
    print("=" * 70)
    for r in results:
        print(f"  {r['status']:30s}  {r['platform']}")

    with open("output/account_verification.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved: output/account_verification.json")

    try: ctx.close(); browser.close(); pw.stop()
    except: pass


if __name__ == "__main__":
    main()
