"""
Strategy 3: Profile / Forum Links — humanized with fallback selectors.
"""
import json
import os
import random
from datetime import datetime

from core.browser import get_browser, new_page
from core.rate_limiter import delay, inter_field_delay, reading_pause
from core.human_behavior import (
    human_type, human_click, human_scroll,
    human_wait, dismiss_overlays, random_mouse_movement,
)

DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "forums.json")

# Fallback selectors for website field (tried in order)
WEBSITE_FALLBACK_SELECTORS = [
    "input[name='url']", "input[name='website']", "input[name='blog']",
    "input[name='homepage']", "input[name='web']", "input[name='site']",
    "input[placeholder*='website']", "input[placeholder*='site']",
    "input[placeholder*='url']", "input[placeholder*='http']",
    "input[type='url']",
    "input#user_profile_blog", "input#website-url", "input#WebsiteUrl",
    "input#user-website", "input[id*='website']", "input[id*='url']",
]


def fill_profile(browser, site: dict, config: dict, logger, dry_run: bool = False):
    site_name = site["name"]
    profile_url = site.get("profile_url", "")
    login_url = site.get("login_url", "")
    website_selector = site.get("website_field_selector", "")
    website = config.get("business", {}).get("website", "")

    # Normalize name for config lookup
    config_key = site_name.lower().replace(" ", "").replace(".", "").replace("-", "")
    creds = config.get("accounts", {}).get(config_key, {})
    if not creds:
        creds = config.get("accounts", {}).get(site_name.lower(), {})

    if dry_run:
        print(f"[profiles/{site_name}] DRY RUN: would fill website={website} at {profile_url}")
        logger.log({
            "date": datetime.utcnow().isoformat(), "strategy": "profiles",
            "site_name": site_name, "url_submitted": profile_url,
            "backlink_url": "", "status": "skipped", "notes": "dry-run mode",
        })
        return

    if not creds.get("email") and not creds.get("username"):
        logger.log({
            "date": datetime.utcnow().isoformat(), "strategy": "profiles",
            "site_name": site_name, "url_submitted": profile_url,
            "backlink_url": "", "status": "failed",
            "notes": f"No credentials for {site_name} in config.json",
        })
        return

    context, page = new_page(browser, config)
    try:
        # Login
        if login_url:
            page.goto(login_url, timeout=60000)
            page.wait_for_load_state("domcontentloaded", timeout=20000)
            dismiss_overlays(page)
            reading_pause(config)
            random_mouse_movement(page)

            username_val = creds.get("email", creds.get("username", ""))
            password_val = creds.get("password", "")

            human_type(page, "input[type='email'], input[name*='email'], input[name*='username'], input[name*='login']", username_val)
            inter_field_delay(config)
            human_type(page, "input[type='password']", password_val)
            inter_field_delay(config)
            human_click(page, "button[type='submit'], input[type='submit']")

            try:
                page.wait_for_load_state("domcontentloaded", timeout=20000)
            except Exception:
                pass
            human_wait(1.0, 2.0)

        # Navigate to profile
        page.goto(profile_url, timeout=60000)
        page.wait_for_load_state("domcontentloaded", timeout=20000)
        dismiss_overlays(page)
        reading_pause(config)
        random_mouse_movement(page)

        # Check for CAPTCHA
        content_lower = page.content().lower()
        if any(x in content_lower for x in ["recaptcha", "captcha", "g-recaptcha", "hcaptcha"]):
            from core.captcha_solver import solve_captcha_if_present
            solve_captcha_if_present(page, profile_url, config)

        # Find website field — try data file selector first, then fallbacks
        filled = False
        selectors_to_try = []
        if website_selector:
            selectors_to_try.extend([s.strip() for s in website_selector.split(",")])
        selectors_to_try.extend(WEBSITE_FALLBACK_SELECTORS)

        # Deduplicate while preserving order
        seen = set()
        unique_selectors = []
        for s in selectors_to_try:
            if s not in seen:
                seen.add(s)
                unique_selectors.append(s)

        for sel in unique_selectors:
            try:
                el = page.query_selector(sel)
                if el and el.is_visible():
                    human_scroll(page, "down", random.randint(100, 250))
                    filled = human_type(page, sel, website)
                    if filled:
                        break
            except Exception:
                continue

        if not filled:
            raise Exception(f"Website field not found after trying {len(unique_selectors)} selectors")

        inter_field_delay(config)

        # Save profile
        human_scroll(page, "down", random.randint(100, 200))
        save_selectors = [
            "button[type='submit']", "input[type='submit']",
            "button:has-text('Save')", "button:has-text('Update')",
            "button:has-text('Submit')", "button:has-text('save')",
        ]
        before_url = page.url
        for save_sel in save_selectors:
            if human_click(page, save_sel):
                break

        try:
            page.wait_for_load_state("domcontentloaded", timeout=15000)
        except Exception:
            pass
        human_wait(1.5, 3.0)

        from core.success_detector import analyze_page
        result = analyze_page(page, before_url, site_name)

        # Profile saves are often silent (no redirect, no message)
        # If we successfully filled the field and clicked save without error, that's success
        if result.status == "pending" and filled:
            result.status = "success"
            result.notes = f"Website field set to {website} — save clicked"

        logger.log({
            "date": datetime.utcnow().isoformat(), "strategy": "profiles",
            "site_name": site_name, "url_submitted": profile_url,
            "backlink_url": "", "status": result.status,
            "notes": result.notes[:200],
        })

    except Exception as e:
        logger.log({
            "date": datetime.utcnow().isoformat(), "strategy": "profiles",
            "site_name": site_name, "url_submitted": profile_url,
            "backlink_url": "", "status": "failed", "notes": str(e)[:200],
        })
    finally:
        context.close()


def run(config: dict, logger, dry_run: bool = False, headed: bool = False):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        sites = json.load(f)

    done = logger.get_done_sites()
    sites_to_do = [s for s in sites if s["name"] not in done]

    if not sites_to_do:
        print("[profiles] All forum profiles already done.")
        return

    pw, browser = get_browser(config, headed_override=headed)
    try:
        for site in sites_to_do:
            print(f"[profiles] Filling profile on {site['name']}...")
            fill_profile(browser, site, config, logger, dry_run=dry_run)
            delay(config)
    finally:
        browser.close()
        pw.stop()
