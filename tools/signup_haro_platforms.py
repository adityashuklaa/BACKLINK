"""Attempt to sign up `social@dialphone.com` to the 4 HARO replacement platforms.

Email verification still requires user action (click link in inbox) — this only
gets the account *created*. After user clicks 4 verify links, accounts are live.

Saves all credentials to .credentials/accounts_sheet.csv after successful submit.
"""
import csv
import json
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, ".")
sys.stdout.reconfigure(encoding="utf-8")

from core.browser import get_browser, new_page

CFG = json.load(open("config.json"))

# Single shared password for all 4 (different from prod accounts)
HARO_PASSWORD = "Nw@fq773FaBMHw%V"
EMAIL = "social@dialphone.com"
FIRST_NAME = "Aditya"
LAST_NAME = "Shukla"
COMPANY = "DialPhone"
TITLE = "Growth Operations"


def append_creds(platform, username, password, email, status, signup_url, notes):
    p = Path(".credentials/accounts_sheet.csv")
    p.parent.mkdir(parents=True, exist_ok=True)
    new = not p.exists() or p.stat().st_size == 0
    with open(p, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["platform", "username", "password", "email", "status", "signup_url", "created", "notes"])
        w.writerow([platform, username, password, email, status, signup_url, datetime.now().isoformat(), notes])


def signup_featured(page):
    """Featured.com — simplest signup, no captcha."""
    print("\n--- Featured.com ---")
    try:
        page.goto("https://featured.com/sign-up", wait_until="domcontentloaded", timeout=25000)
        page.wait_for_timeout(3000)
        page.fill("#firstName", FIRST_NAME)
        page.fill("#lastName", LAST_NAME)
        page.fill("#email", EMAIL)
        page.fill("#password", HARO_PASSWORD)
        # Find submit
        submit = page.query_selector("button[type='submit'], button:has-text('Sign Up'), button:has-text('Create')")
        if not submit:
            print("  no submit button found")
            return ("error", "submit button missing")
        submit.click()
        page.wait_for_timeout(5000)
        # Check for success indicators
        body = page.inner_text("body").lower()
        url = page.url
        print(f"  post-submit URL: {url}")
        if "verify" in body or "check your email" in body or "confirmation" in body or "/dashboard" in url or "/onboard" in url:
            print("  SUCCESS — email verification pending")
            return ("pending_verify", "click verify link in social@ inbox")
        if "already" in body or "exists" in body:
            print("  account already exists")
            return ("exists", "account already registered")
        print(f"  unclear state, body excerpt: {body[:300]}")
        return ("unknown", body[:200])
    except Exception as e:
        print(f"  err: {str(e)[:200]}")
        return ("error", str(e)[:200])


def signup_qwoted(page):
    """Qwoted — moved to app.qwoted.com."""
    print("\n--- Qwoted ---")
    try:
        # Try the sources signup page
        for url in ["https://app.qwoted.com/users/sign_up", "https://app.qwoted.com/signup",
                    "https://www.qwoted.com/users/sign_up"]:
            page.goto(url, wait_until="domcontentloaded", timeout=20000)
            page.wait_for_timeout(2500)
            inputs = page.evaluate("[...document.querySelectorAll('input')].map(i=>i.type)")
            if "email" in inputs and "password" in inputs:
                print(f"  signup form found at {url}")
                break
        else:
            print("  could not find Qwoted signup form")
            return ("error", "signup URL not found")

        # Fill what's possible
        for sel, val in [
            ("input[type='email']", EMAIL),
            ("input[name='user[email]']", EMAIL),
            ("input[type='password']", HARO_PASSWORD),
            ("input[name='user[password]']", HARO_PASSWORD),
        ]:
            try:
                el = page.query_selector(sel)
                if el and el.is_visible():
                    el.fill(val)
            except: pass
        # Try first/last name fields
        for sel, val in [
            ("input[name='user[first_name]']", FIRST_NAME),
            ("input[id*='first']", FIRST_NAME),
            ("input[name='user[last_name]']", LAST_NAME),
            ("input[id*='last']", LAST_NAME),
        ]:
            try:
                el = page.query_selector(sel)
                if el and el.is_visible(): el.fill(val)
            except: pass

        # Detect captcha before submit
        captcha = page.query_selector("[class*=recaptcha] iframe, iframe[src*=recaptcha]")
        if captcha:
            print("  reCAPTCHA visible — cannot submit autonomously")
            return ("blocked_captcha", "reCAPTCHA on Qwoted signup; user needs to do it manually")

        submit = page.query_selector("button[type='submit'], input[type='submit']")
        if submit:
            submit.click()
            page.wait_for_timeout(5000)
            body = page.inner_text("body").lower()
            if "verify" in body or "confirm" in body or "sent" in body:
                return ("pending_verify", "click verify link in social@ inbox")
            return ("unknown", body[:200])
        return ("error", "no submit button")
    except Exception as e:
        print(f"  err: {str(e)[:200]}")
        return ("error", str(e)[:200])


def signup_connectively(page):
    """Connectively — official HARO successor."""
    print("\n--- Connectively ---")
    candidates = ["https://connectively.us/sign-up", "https://connectively.us/signup",
                  "https://app.connectively.us/sign-up", "https://www.connectively.us/sign-up"]
    try:
        for url in candidates:
            page.goto(url, wait_until="domcontentloaded", timeout=20000)
            page.wait_for_timeout(3000)
            inputs = page.evaluate("[...document.querySelectorAll('input')].map(i=>i.type)")
            if "email" in inputs and "password" in inputs:
                print(f"  signup form at {url}")
                break
        else:
            print("  signup form not found at known URLs")
            return ("error", "signup URL not found")

        # Detect captcha
        captcha = page.query_selector("iframe[src*=hcaptcha], iframe[src*=recaptcha], [class*=hcaptcha], [class*=turnstile]")
        if captcha:
            print("  CAPTCHA detected — cannot proceed autonomously")
            return ("blocked_captcha", "CAPTCHA on Connectively signup")

        # Try to fill
        for sel, val in [
            ("input[type='email']", EMAIL),
            ("input[type='password']", HARO_PASSWORD),
        ]:
            try:
                el = page.query_selector(sel)
                if el and el.is_visible(): el.fill(val)
            except: pass

        submit = page.query_selector("button[type='submit']")
        if submit:
            submit.click()
            page.wait_for_timeout(6000)
            body = page.inner_text("body").lower()
            if "verify" in body or "confirm" in body or "check your email" in body:
                return ("pending_verify", "click verify link in social@ inbox")
            return ("unknown", body[:200])
        return ("error", "no submit button")
    except Exception as e:
        return ("error", str(e)[:200])


def signup_mentionmatch(page):
    """MentionMatch (formerly Help A B2B Writer)."""
    print("\n--- MentionMatch / Help A B2B Writer ---")
    candidates = ["https://mentionmatch.com/source/sign-up", "https://mentionmatch.com/signup",
                  "https://helpab2bwriter.com/source/sign-up", "https://helpab2bwriter.com/signup",
                  "https://helpab2bwriter.com/register"]
    try:
        for url in candidates:
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=20000)
                page.wait_for_timeout(2500)
                inputs = page.evaluate("[...document.querySelectorAll('input')].map(i=>i.type)")
                if "email" in inputs and "password" in inputs:
                    print(f"  signup form at {url}")
                    break
            except: continue
        else:
            print("  no working signup URL found across all candidates")
            return ("error", "signup URL not found")

        # Quick attempt
        for sel, val in [
            ("input[type='email']", EMAIL),
            ("input[type='password']", HARO_PASSWORD),
        ]:
            try:
                el = page.query_selector(sel)
                if el and el.is_visible(): el.fill(val)
            except: pass

        submit = page.query_selector("button[type='submit']")
        if submit:
            submit.click()
            page.wait_for_timeout(5000)
            body = page.inner_text("body").lower()
            if "verify" in body or "confirm" in body:
                return ("pending_verify", "click verify link in social@ inbox")
            return ("unknown", body[:200])
        return ("error", "no submit button")
    except Exception as e:
        return ("error", str(e)[:200])


def main():
    pw, browser = get_browser(CFG, headed_override=False)
    ctx, page = new_page(browser, CFG, "haro-signup")

    runs = [
        ("Featured.com",   "https://featured.com/sign-up",    signup_featured),
        ("Qwoted",         "https://app.qwoted.com",          signup_qwoted),
        ("Connectively",   "https://connectively.us",         signup_connectively),
        ("MentionMatch",   "https://mentionmatch.com",        signup_mentionmatch),
    ]

    results = []
    for name, url, fn in runs:
        status, notes = fn(page)
        append_creds(name, EMAIL, HARO_PASSWORD, EMAIL, status, url, notes)
        results.append((name, status, notes))
        time.sleep(2)

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for name, status, notes in results:
        print(f"  {status:20s}  {name}  — {notes[:80]}")

    pending = [r for r in results if r[1] == "pending_verify"]
    print(f"\nNeed user action: click {len(pending)} verify links in social@dialphone.com inbox")

    try: ctx.close(); browser.close(); pw.stop()
    except: pass


if __name__ == "__main__":
    main()
