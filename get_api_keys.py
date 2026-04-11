"""Log into Dev.to and Hashnode, get API keys."""
import json
import time
from core.browser import get_browser, new_page
from core.human_behavior import (
    human_type, human_click, human_scroll,
    human_wait, dismiss_overlays, random_mouse_movement,
)

config = json.load(open("config.json"))
pw, browser = get_browser(config, headed_override=True)

# ===== DEV.TO =====
print("=" * 60)
print("DEV.TO: Login + Get API Key")
print("=" * 60)

context, page = new_page(browser, config, site_name="devto-login")
try:
    # Dev.to uses OAuth buttons BUT also has email login via Forem
    # Try the direct email login URL
    page.goto("https://dev.to/enter?state=new-user", timeout=60000)
    page.wait_for_load_state("domcontentloaded", timeout=20000)
    time.sleep(4)
    dismiss_overlays(page)
    random_mouse_movement(page)

    # Check what login options are available
    text = page.evaluate("document.body.innerText.substring(0, 500)").encode("ascii", "replace").decode()
    print(f"Page text: {text[:200]}")

    # Look for email login option
    email_link = page.query_selector("a:has-text('Email'), button:has-text('Email'), a:has-text('Continue with email')")
    if email_link:
        print("Found email login option, clicking...")
        email_link.click()
        time.sleep(3)

    # Check for email/password fields
    email_field = page.query_selector("input[type='email'], input[name='user[email]'], input[id*='email']")
    pwd_field = page.query_selector("input[type='password'], input[name='user[password]']")

    if email_field and pwd_field:
        print("Email + password fields found! Logging in...")
        human_type(page, "input[type='email'], input[name='user[email]'], input[id*='email']", "commercial@dialphone.com")
        time.sleep(0.5)
        human_type(page, "input[type='password'], input[name='user[password]']", "D4qJ%@Rt4^q5f3(")
        time.sleep(0.5)
        human_click(page, "button[type='submit'], input[type='submit']")
        time.sleep(5)

        after_url = page.url
        print(f"After login URL: {after_url}")

        if "enter" not in after_url.lower() and "login" not in after_url.lower():
            print("LOGIN SUCCESS!")

            # Navigate to API settings
            page.goto("https://dev.to/settings/extensions", timeout=30000)
            page.wait_for_load_state("domcontentloaded", timeout=15000)
            time.sleep(3)

            page_text = page.evaluate("document.body.innerText.substring(0, 1000)").encode("ascii", "replace").decode()
            print(f"Settings page: {page_text[:300]}")

            # Look for API key generation
            desc_input = page.query_selector("input[name='description'], input[placeholder*='description'], input[placeholder*='name']")
            if desc_input:
                human_type(page, "input[name='description'], input[placeholder*='description'], input[placeholder*='name']", "backlink-bot")
                time.sleep(0.5)
                human_click(page, "button:has-text('Generate'), button:has-text('Create')")
                time.sleep(3)

                # Try to find the generated key
                key_text = page.evaluate("document.body.innerText").encode("ascii", "replace").decode()
                # Look for long alphanumeric strings
                import re
                keys = re.findall(r'[a-zA-Z0-9]{20,}', key_text)
                if keys:
                    print(f"POSSIBLE API KEY FOUND: {keys[0][:30]}...")
                else:
                    print("No API key found in page text")

            page.screenshot(path="output/devto_settings.png")
        else:
            print("LOGIN FAILED — still on login page")
            page.screenshot(path="output/devto_login_failed.png")
    else:
        print("No email/password fields found")
        # List all visible inputs
        inputs = page.query_selector_all("input:visible")
        for inp in inputs[:10]:
            t = inp.get_attribute("type") or ""
            n = inp.get_attribute("name") or ""
            p = inp.get_attribute("placeholder") or ""
            print(f"  input: type={t} name={n} placeholder={p[:30]}")
        page.screenshot(path="output/devto_login_page.png")

except Exception as e:
    print(f"ERROR: {e}")
finally:
    context.close()

print()

# ===== HASHNODE =====
print("=" * 60)
print("HASHNODE: Login + Get API Key")
print("=" * 60)

context, page = new_page(browser, config, site_name="hashnode-login")
try:
    page.goto("https://hashnode.com/login", timeout=60000)
    page.wait_for_load_state("domcontentloaded", timeout=20000)
    time.sleep(4)
    dismiss_overlays(page)
    random_mouse_movement(page)

    text = page.evaluate("document.body.innerText.substring(0, 500)").encode("ascii", "replace").decode()
    print(f"Page text: {text[:200]}")

    # Check for email login
    email_field = page.query_selector("input[type='email'], input[name='email'], input[placeholder*='email']")
    pwd_field = page.query_selector("input[type='password']")

    if email_field:
        print("Email field found!")
        human_type(page, "input[type='email'], input[name='email'], input[placeholder*='email']", "commercial@dialphone.com")
        time.sleep(1)

        if pwd_field:
            print("Password field found!")
            human_type(page, "input[type='password']", "@Rt4^Kzqq&5sXdn3eW")
            time.sleep(0.5)
            human_click(page, "button[type='submit'], input[type='submit'], button:has-text('Log in'), button:has-text('Sign in')")
        else:
            # Hashnode might use magic link (email-only login)
            print("No password field — might be magic link login")
            human_click(page, "button[type='submit'], button:has-text('Continue'), button:has-text('Send')")

        time.sleep(5)
        after_url = page.url
        print(f"After login URL: {after_url}")

        if "login" not in after_url.lower():
            print("LOGIN SUCCESS!")
            page.goto("https://hashnode.com/settings/developer", timeout=30000)
            page.wait_for_load_state("domcontentloaded", timeout=15000)
            time.sleep(3)
            page.screenshot(path="output/hashnode_settings.png")
            settings_text = page.evaluate("document.body.innerText.substring(0, 500)").encode("ascii", "replace").decode()
            print(f"Settings: {settings_text[:200]}")
        else:
            print("LOGIN FAILED or magic link sent (check email)")
            page.screenshot(path="output/hashnode_login_result.png")
    else:
        print("No email field — login page uses OAuth only")
        inputs = page.query_selector_all("input:visible, button:visible")
        for el in inputs[:10]:
            tag = el.evaluate("el => el.tagName")
            text = (el.text_content() or "").strip()[:30]
            t = el.get_attribute("type") or ""
            print(f"  {tag}: type={t} text={text}")
        page.screenshot(path="output/hashnode_login_page.png")

except Exception as e:
    print(f"ERROR: {e}")
finally:
    context.close()

browser.close()
pw.stop()
print("\nDone. Check output/ folder for screenshots.")
