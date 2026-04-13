"""
Auto-signup on GitLab, Bitbucket, Codeberg, WordPress, Tumblr.
Fills out registration forms automatically — user just clicks email verification links.

Usage: python run_signup_all.py
"""
import json
import time
from core.browser import get_browser, new_page

config = json.load(open("config.json"))

USERNAME = "dialphonelimited"
PASSWORD = "DevD!alph0ne@0912@#"
EMAIL = "commercial@dialphone.com"
DISPLAY_NAME = "DialPhone Limited"

PLATFORMS = [
    {
        "name": "GitLab",
        "url": "https://gitlab.com/users/sign_up",
        "da": 92,
    },
    {
        "name": "Bitbucket",
        "url": "https://id.atlassian.com/signup",
        "da": 92,
    },
    {
        "name": "Codeberg",
        "url": "https://codeberg.org/user/sign_up",
        "da": 55,
    },
    {
        "name": "WordPress",
        "url": "https://wordpress.com/start/account",
        "da": 95,
    },
    {
        "name": "Tumblr",
        "url": "https://www.tumblr.com/register",
        "da": 95,
    },
]

pw, browser = get_browser(config, headed_override=True)

results = []

for platform in PLATFORMS:
    print(f"\n{'='*60}")
    print(f"  {platform['name']} (DA {platform['da']})")
    print(f"  {platform['url']}")
    print(f"{'='*60}")

    ctx, pg = new_page(browser, config, site_name=f"signup-{platform['name'].lower()}")

    try:
        pg.goto(platform["url"], timeout=60000)
        pg.wait_for_load_state("domcontentloaded", timeout=20000)
        time.sleep(5)

        # Dismiss cookie banners
        for sel in ['button:has-text("Accept")', 'button:has-text("Reject all")',
                    'button:has-text("Got it")', 'button:has-text("OK")',
                    'button[id*="cookie" i]', 'button:has-text("Agree")']:
            try:
                b = pg.query_selector(sel)
                if b and b.is_visible():
                    b.click()
                    time.sleep(2)
                    break
            except:
                pass

        # ============================================================
        # GITLAB
        # ============================================================
        if platform["name"] == "GitLab":
            # GitLab signup form
            fn = pg.query_selector('input#new_user_first_name, input[name="user[first_name]"]')
            if fn:
                fn.fill("DialPhone")
                time.sleep(0.5)
            ln = pg.query_selector('input#new_user_last_name, input[name="user[last_name]"]')
            if ln:
                ln.fill("Limited")
                time.sleep(0.5)
            un = pg.query_selector('input#new_user_username, input[name="user[username]"]')
            if un:
                un.fill(USERNAME)
                time.sleep(0.5)
            em = pg.query_selector('input#new_user_email, input[name="user[email]"]')
            if em:
                em.fill(EMAIL)
                time.sleep(0.5)
            pw_field = pg.query_selector('input#new_user_password, input[name="user[password]"]')
            if pw_field:
                pw_field.fill(PASSWORD)
                time.sleep(0.5)

            # Wait for user to see the form
            time.sleep(2)
            print("  Form filled!")
            print(f"  Username: {USERNAME}")
            print(f"  Email: {EMAIL}")

            # Try to submit
            submit = pg.query_selector('button[type="submit"]:has-text("Register"), input[type="submit"]')
            if submit and submit.is_visible():
                submit.click()
                time.sleep(10)
                print(f"  Submitted! Page: {pg.url}")
            else:
                print("  Could not find submit button — check browser")

        # ============================================================
        # BITBUCKET (Atlassian)
        # ============================================================
        elif platform["name"] == "Bitbucket":
            # Atlassian signup — email first
            em = pg.query_selector('input#email, input[name="email"]')
            if em:
                em.fill(EMAIL)
                time.sleep(1)
                submit = pg.query_selector('button[type="submit"], button:has-text("Continue")')
                if submit:
                    submit.click()
                    time.sleep(8)

                # Full name
                name_field = pg.query_selector('input#displayName, input[name="displayName"]')
                if name_field:
                    name_field.fill(DISPLAY_NAME)
                    time.sleep(0.5)

                # Password
                pw_field = pg.query_selector('input#password, input[name="password"]')
                if pw_field:
                    pw_field.fill(PASSWORD)
                    time.sleep(0.5)

                submit2 = pg.query_selector('button[type="submit"], button:has-text("Sign up")')
                if submit2:
                    submit2.click()
                    time.sleep(10)

            print(f"  Submitted! Page: {pg.url}")
            print(f"  Email: {EMAIL}")

        # ============================================================
        # CODEBERG
        # ============================================================
        elif platform["name"] == "Codeberg":
            un = pg.query_selector('input#user_name, input[name="user_name"]')
            if un:
                un.fill(USERNAME)
                time.sleep(0.5)
            em = pg.query_selector('input#email, input[name="email"]')
            if em:
                em.fill(EMAIL)
                time.sleep(0.5)
            pw1 = pg.query_selector('input#password, input[name="password"]')
            if pw1:
                pw1.fill(PASSWORD)
                time.sleep(0.5)
            pw2 = pg.query_selector('input#retype, input[name="retype"]')
            if pw2:
                pw2.fill(PASSWORD)
                time.sleep(0.5)

            print("  Form filled!")
            print(f"  Username: {USERNAME}")

            submit = pg.query_selector('button[type="submit"]:has-text("Register"), button.ui.primary')
            if submit and submit.is_visible():
                submit.click()
                time.sleep(10)
                print(f"  Submitted! Page: {pg.url}")
            else:
                print("  Could not find submit button — check browser")

        # ============================================================
        # WORDPRESS
        # ============================================================
        elif platform["name"] == "WordPress":
            em = pg.query_selector('input#email, input[name="email"], input[type="email"]')
            if em:
                em.fill(EMAIL)
                time.sleep(1)

            un = pg.query_selector('input#username, input[name="username"]')
            if un:
                un.fill(USERNAME)
                time.sleep(0.5)

            pw_field = pg.query_selector('input#password, input[name="password"], input[type="password"]')
            if pw_field:
                pw_field.fill(PASSWORD)
                time.sleep(0.5)

            print("  Form filled!")
            print(f"  Email: {EMAIL}")

            submit = pg.query_selector('button[type="submit"], button:has-text("Create")')
            if submit and submit.is_visible():
                submit.click()
                time.sleep(10)
                print(f"  Submitted! Page: {pg.url}")
            else:
                # WordPress might have a different flow
                cont = pg.query_selector('button:has-text("Continue"), a:has-text("Continue")')
                if cont and cont.is_visible():
                    cont.click()
                    time.sleep(8)
                    print(f"  Continued! Page: {pg.url}")

        # ============================================================
        # TUMBLR
        # ============================================================
        elif platform["name"] == "Tumblr":
            em = pg.query_selector('input[name="email"], input[type="email"]')
            if em:
                em.fill(EMAIL)
                time.sleep(0.5)

            pw_field = pg.query_selector('input[name="password"], input[type="password"]')
            if pw_field:
                pw_field.fill(PASSWORD)
                time.sleep(0.5)

            un = pg.query_selector('input[name="tumblelog"], input[name="blogName"]')
            if un:
                un.fill(USERNAME)
                time.sleep(0.5)

            print("  Form filled!")
            print(f"  Email: {EMAIL}")

            submit = pg.query_selector('button[type="submit"], button:has-text("Sign up"), button:has-text("Next")')
            if submit and submit.is_visible():
                submit.click()
                time.sleep(10)
                print(f"  Submitted! Page: {pg.url}")

        # Take screenshot
        try:
            pg.screenshot(path=f"output/signup_{platform['name'].lower()}.png")
            print(f"  Screenshot saved: output/signup_{platform['name'].lower()}.png")
        except:
            pass

        results.append({"name": platform["name"], "da": platform["da"], "status": "form submitted"})

        # PAUSE — let user check email for this platform before moving on
        print(f"\n  >>> CHECK EMAIL: {EMAIL}")
        print(f"  >>> Click the verification link from {platform['name']}")
        print(f"  >>> Waiting 30 seconds before next platform...")
        time.sleep(30)

    except Exception as e:
        print(f"  Error: {str(e)[:100]}")
        results.append({"name": platform["name"], "da": platform["da"], "status": f"error: {str(e)[:50]}"})

    finally:
        ctx.close()

browser.close()
pw.stop()

print(f"\n{'='*60}")
print("SIGNUP RESULTS")
print(f"{'='*60}")
for r in results:
    print(f"  {r['name']} (DA {r['da']}): {r['status']}")
print(f"\n  Credentials for all platforms:")
print(f"  Username: {USERNAME}")
print(f"  Email: {EMAIL}")
print(f"  Password: {PASSWORD}")
print(f"\n  After verifying emails, run:")
print(f"  python run_signup_and_publish.py --platform all")
print(f"  python run_code_platforms.py --platform all --gitlab-token YOUR_TOKEN")
