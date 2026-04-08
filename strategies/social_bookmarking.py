"""
Strategy 2: Social Bookmarking — humanized browser behavior.
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

DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "social_bookmarks.json")
TEMPLATE_FILE = os.path.join(os.path.dirname(__file__), "..", "templates", "social_post.txt")


def _render_template(config: dict) -> str:
    with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    b = config.get("business", {})
    replacements = {
        "{{business_name}}": b.get("name", ""),
        "{{website}}": b.get("website", ""),
        "{{tagline}}": b.get("tagline", ""),
        "{{description}}": b.get("description", ""),
        "{{keywords}}": ", ".join(b.get("keywords", [])),
    }
    for k, v in replacements.items():
        content = content.replace(k, v)
    return content


def post_reddit(site: dict, config: dict, logger, dry_run: bool = False):
    try:
        import praw
    except ImportError:
        logger.log({
            "date": datetime.utcnow().isoformat(), "strategy": "social",
            "site_name": "Reddit", "url_submitted": "https://reddit.com",
            "backlink_url": "", "status": "failed",
            "notes": "praw not installed",
        })
        return

    creds = config.get("accounts", {}).get("reddit", {})
    if not creds.get("client_id") or "demo" in creds.get("client_id", ""):
        logger.log({
            "date": datetime.utcnow().isoformat(), "strategy": "social",
            "site_name": "Reddit", "url_submitted": "https://reddit.com",
            "backlink_url": "", "status": "skipped",
            "notes": "Reddit credentials not configured — skipping",
        })
        return

    b = config.get("business", {})
    website = b.get("website", "")
    title = b.get("tagline", b.get("name", ""))

    if dry_run:
        for subreddit in site.get("subreddits", []):
            print(f"[social/reddit] DRY RUN: would post to {subreddit}")
        return

    reddit = praw.Reddit(
        client_id=creds["client_id"],
        client_secret=creds["client_secret"],
        username=creds["username"],
        password=creds["password"],
        user_agent=f"backlink-bot:v1.0 (by /u/{creds['username']})",
    )

    for subreddit_name in site.get("subreddits", []):
        sub_name = subreddit_name.lstrip("r/")
        try:
            subreddit = reddit.subreddit(sub_name)
            submission = subreddit.submit_link(title=title, url=website)
            logger.log({
                "date": datetime.utcnow().isoformat(), "strategy": "social",
                "site_name": f"Reddit/{sub_name}",
                "url_submitted": f"https://reddit.com/r/{sub_name}",
                "backlink_url": f"https://reddit.com{submission.permalink}",
                "status": "success", "notes": "",
            })
        except Exception as e:
            logger.log({
                "date": datetime.utcnow().isoformat(), "strategy": "social",
                "site_name": f"Reddit/{sub_name}",
                "url_submitted": f"https://reddit.com/r/{sub_name}",
                "backlink_url": "", "status": "failed", "notes": str(e)[:200],
            })
        delay(config)


def post_playwright(browser, site: dict, config: dict, logger, dry_run: bool = False):
    site_name = site["name"]
    submit_url = site.get("submit_url", "")
    login_url = site.get("login_url", "")
    config_key = site_name.lower().replace(" ", "").replace(".", "").replace("-", "")
    creds = config.get("accounts", {}).get(config_key, {})

    if dry_run:
        print(f"[social/{site_name}] DRY RUN: would post to {submit_url}")
        logger.log({
            "date": datetime.utcnow().isoformat(), "strategy": "social",
            "site_name": site_name, "url_submitted": submit_url,
            "backlink_url": "", "status": "skipped", "notes": "dry-run mode",
        })
        return

    context, page = new_page(browser, config)
    try:
        b = config.get("business", {})
        description = _render_template(config)

        # Login if credentials provided
        if login_url and creds.get("username"):
            page.goto(login_url, timeout=60000)
            page.wait_for_load_state("domcontentloaded", timeout=20000)
            dismiss_overlays(page)
            reading_pause(config)

            human_type(page, "input[type='email'], input[name*='email'], input[name*='username']", creds.get("username", ""))
            inter_field_delay(config)
            human_type(page, "input[type='password']", creds.get("password", ""))
            inter_field_delay(config)
            human_click(page, "button[type='submit'], input[type='submit']")

            try:
                page.wait_for_load_state("domcontentloaded", timeout=15000)
            except Exception:
                pass

        page.goto(submit_url, timeout=60000)
        page.wait_for_load_state("domcontentloaded", timeout=20000)
        dismiss_overlays(page)
        reading_pause(config)
        random_mouse_movement(page)

        # Check for CAPTCHA
        content_lower = page.content().lower()
        if any(x in content_lower for x in ["recaptcha", "captcha", "g-recaptcha", "hcaptcha"]):
            from core.captcha_solver import solve_captcha_if_present
            solve_captcha_if_present(page, submit_url, config)

        # Fill submission form
        human_type(page, "input[name*='url'], input[type='url'], input[placeholder*='url']", b.get("website", ""))
        inter_field_delay(config)
        human_type(page, "input[name*='title'], input[placeholder*='title']", b.get("tagline", b.get("name", "")))
        inter_field_delay(config)
        human_type(page, "textarea[name*='description'], textarea[placeholder*='description']", description[:500])
        inter_field_delay(config)

        human_scroll(page, "down", 200)
        before_url = page.url

        from core.success_detector import analyze_page
        human_click(page, "button[type='submit'], input[type='submit']")

        try:
            page.wait_for_load_state("domcontentloaded", timeout=15000)
        except Exception:
            pass
        human_wait(1.5, 3.0)

        result = analyze_page(page, before_url, site_name)

        logger.log({
            "date": datetime.utcnow().isoformat(), "strategy": "social",
            "site_name": site_name, "url_submitted": submit_url,
            "backlink_url": page.url if result.status == "success" else "",
            "status": result.status, "notes": result.notes[:200],
        })
    except Exception as e:
        logger.log({
            "date": datetime.utcnow().isoformat(), "strategy": "social",
            "site_name": site_name, "url_submitted": submit_url,
            "backlink_url": "", "status": "failed", "notes": str(e)[:200],
        })
    finally:
        context.close()


def run(config: dict, logger, dry_run: bool = False, headed: bool = False):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        sites = json.load(f)

    done = logger.get_done_sites()

    pw, browser = get_browser(config, headed_override=headed)
    try:
        for site in sites:
            site_name = site["name"]
            if site_name in done and not site_name.startswith("Reddit"):
                print(f"[social] Skipping {site_name} — already done")
                continue
            print(f"[social] Posting to {site_name}...")
            if site.get("method") == "api" and site_name == "Reddit":
                post_reddit(site, config, logger, dry_run=dry_run)
            else:
                post_playwright(browser, site, config, logger, dry_run=dry_run)
            delay(config)
    finally:
        browser.close()
        pw.stop()
