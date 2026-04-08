"""
Strategy 1: Directory Submissions — humanized browser behavior.
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

DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "directories.json")


def _detect_captcha(page) -> bool:
    content = page.content().lower()
    return any(x in content for x in ["recaptcha", "captcha", "g-recaptcha", "hcaptcha"])


def submit(browser, site: dict, config: dict, logger, dry_run: bool = False):
    site_name = site["name"]
    signup_url = site["signup_url"]

    if dry_run:
        logger.log({
            "date": datetime.utcnow().isoformat(),
            "strategy": "directories",
            "site_name": site_name,
            "url_submitted": signup_url,
            "backlink_url": "",
            "status": "skipped",
            "notes": "dry-run mode",
        })
        return

    context, page = new_page(browser, config)
    try:
        page.goto(signup_url, timeout=60000)
        page.wait_for_load_state("domcontentloaded", timeout=20000)

        # Human behavior: dismiss popups, read the page, move mouse
        dismiss_overlays(page)
        reading_pause(config)
        random_mouse_movement(page)
        human_scroll(page, "down", random.randint(150, 400))

        if _detect_captcha(page):
            from core.captcha_solver import solve_captcha_if_present
            solved = solve_captcha_if_present(page, signup_url, config)
            if not solved:
                captcha_cfg = config.get("captcha", {})
                reason = "disabled" if not captcha_cfg.get("enabled") else "failed"
                logger.log({
                    "date": datetime.utcnow().isoformat(),
                    "strategy": "directories",
                    "site_name": site_name,
                    "url_submitted": signup_url,
                    "backlink_url": "",
                    "status": "pending",
                    "notes": f"CAPTCHA detected, auto-solve {reason} — complete manually at {signup_url}",
                })
                return

        # Human-like form fill
        b = config.get("business", {})
        fields = [
            ("input[name*='business_name'], input[name*='company'], input[placeholder*='business name'], input[name*='name']", b.get("name", "")),
            ("input[name*='website'], input[type='url'], input[placeholder*='website']", b.get("website", "")),
            ("input[name*='email'], input[type='email']", b.get("email", "")),
            ("input[name*='phone'], input[type='tel']", b.get("phone", "")),
        ]

        for selector, value in fields:
            if value:
                human_type(page, selector, value)
                inter_field_delay(config)

        # Description in textarea
        desc = b.get("description", "")
        if desc:
            human_type(page, "textarea[name*='description'], textarea[placeholder*='description']", desc)
            inter_field_delay(config)

        # Scroll to submit and click
        human_scroll(page, "down", random.randint(100, 300))
        human_wait(0.5, 1.5)
        before_url = page.url

        # Try submit — with retry on retryable failures
        from core.success_detector import analyze_page, should_retry

        for attempt in range(3):
            human_click(page, "button[type='submit'], input[type='submit']")

            try:
                page.wait_for_load_state("domcontentloaded", timeout=15000)
            except Exception:
                pass
            human_wait(1.5, 3.0)

            result = analyze_page(page, before_url, site_name)

            if result.status == "success" or not should_retry(result, attempt):
                break

            # Retry: scroll up, re-check form, try again
            print(f"[directories] Retry {attempt+1} for {site_name}: {result.retry_reason}")
            human_scroll(page, "up", 200)
            human_wait(1.0, 2.0)

        logger.log({
            "date": datetime.utcnow().isoformat(),
            "strategy": "directories",
            "site_name": site_name,
            "url_submitted": signup_url,
            "backlink_url": page.url if result.status == "success" else "",
            "status": result.status,
            "notes": result.notes[:200],
        })

    except Exception as e:
        logger.log({
            "date": datetime.utcnow().isoformat(),
            "strategy": "directories",
            "site_name": site_name,
            "url_submitted": signup_url,
            "backlink_url": "",
            "status": "failed",
            "notes": str(e)[:200],
        })
    finally:
        context.close()


def run(config: dict, logger, dry_run: bool = False, headed: bool = False):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        sites = json.load(f)

    done = logger.get_done_sites()
    sites_to_do = [s for s in sites if s["name"] not in done]

    if not sites_to_do:
        print("[directories] All sites already processed.")
        return

    pw, browser = get_browser(config, headed_override=headed)
    try:
        for site in sites_to_do:
            print(f"[directories] Submitting to {site['name']}...")
            submit(browser, site, config, logger, dry_run=dry_run)
            delay(config)
    finally:
        browser.close()
        pw.stop()
