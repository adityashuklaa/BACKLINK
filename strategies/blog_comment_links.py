"""
Strategy 5: Blog Comment Links — humanized comment posting.
"""
import json
import os
import random
from datetime import datetime

from core.browser import get_browser, new_page
from core.http_client import get_session
from core.rate_limiter import delay, inter_field_delay, reading_pause
from core.human_behavior import (
    human_type, human_click, human_scroll,
    human_wait, dismiss_overlays, random_mouse_movement,
)

DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "voip_blogs.json")
TEMPLATE_FILE = os.path.join(os.path.dirname(__file__), "..", "templates", "blog_comment.txt")

VOIP_KEYWORDS = ["voip", "sip", "pbx", "business phone", "hosted phone", "cloud phone",
                 "trunking", "virtual phone", "call center", "unified communications"]


def _render_comment(config: dict, post_title: str = "") -> str:
    with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    b = config.get("business", {})
    replacements = {
        "{{business_name}}": b.get("name", ""),
        "{{website}}": b.get("website", ""),
        "{{tagline}}": b.get("tagline", ""),
        "{{post_title}}": post_title,
    }
    for k, v in replacements.items():
        content = content.replace(k, v)
    return content


def _is_relevant(title: str, url: str) -> bool:
    text = (title + " " + url).lower()
    return any(kw in text for kw in VOIP_KEYWORDS)


def find_posts(config: dict, session) -> list:
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        blogs = json.load(f)

    posts = []
    comment_friendly = [b for b in blogs if b.get("comment_friendly")]

    for blog in comment_friendly:
        rss_url = blog.get("rss")
        if rss_url:
            try:
                import feedparser
                feed = feedparser.parse(rss_url)
                for entry in feed.entries[:5]:
                    title = entry.get("title", "")
                    link = entry.get("link", "")
                    if link and _is_relevant(title, link):
                        posts.append({"url": link, "title": title, "blog": blog["name"]})
            except Exception:
                pass
        else:
            try:
                resp = session.get(blog["url"], timeout=10)
                if resp.status_code == 200:
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(resp.text, "lxml")
                    for a in soup.find_all("a", href=True)[:30]:
                        href = a["href"]
                        text = a.get_text()
                        if _is_relevant(text, href) and href.startswith("http"):
                            posts.append({"url": href, "title": text.strip(), "blog": blog["name"]})
            except Exception:
                pass

    # Deduplicate
    seen = set()
    unique = []
    for p in posts:
        if p["url"] not in seen:
            seen.add(p["url"])
            unique.append(p)
    return unique


def _detect_comment_form(page) -> bool:
    selectors = [
        "#respond", "#comment-form", "form[id*='comment']",
        "textarea[name='comment']", "textarea[id*='comment']",
        "textarea[placeholder*='comment']",
    ]
    for s in selectors:
        el = page.query_selector(s)
        if el:
            return True
    return False


def post_comment(browser, post: dict, config: dict, logger, dry_run: bool = False):
    url = post["url"]
    title = post["title"]
    blog_name = post["blog"]
    site_name = f"comment:{blog_name}:{url[-30:]}"
    b = config.get("business", {})

    if dry_run:
        print(f"[comments/{blog_name}] DRY RUN: would comment on '{title}'")
        logger.log({
            "date": datetime.utcnow().isoformat(), "strategy": "comments",
            "site_name": site_name, "url_submitted": url,
            "backlink_url": "", "status": "skipped", "notes": "dry-run mode",
        })
        return

    context, page = new_page(browser, config)
    try:
        page.goto(url, timeout=60000)
        page.wait_for_load_state("domcontentloaded", timeout=20000)
        dismiss_overlays(page)

        # Simulate reading the blog post
        reading_pause(config)
        random_mouse_movement(page)
        human_scroll(page, "down", random.randint(400, 800))
        human_wait(2.0, 4.0)

        if not _detect_comment_form(page):
            # Scroll further to find comment form
            human_scroll(page, "down", random.randint(500, 1000))
            human_wait(1.0, 2.0)

        if not _detect_comment_form(page):
            logger.log({
                "date": datetime.utcnow().isoformat(), "strategy": "comments",
                "site_name": site_name, "url_submitted": url,
                "backlink_url": "", "status": "failed",
                "notes": "No comment form found or comments closed",
            })
            return

        comment_text = _render_comment(config, title)

        # Fill comment form fields with human behavior
        name_selectors = "input[name='author'], input[name='name'], input[placeholder*='name']"
        email_selectors = "input[name='email'], input[type='email']"
        website_selectors = "input[name='url'], input[name='website'], input[placeholder*='website']"
        comment_selectors = "textarea[name='comment'], textarea[id*='comment'], textarea[placeholder*='comment']"

        human_type(page, name_selectors, b.get("name", ""))
        inter_field_delay(config)
        human_type(page, email_selectors, b.get("email", ""))
        inter_field_delay(config)
        human_type(page, website_selectors, b.get("website", ""))
        inter_field_delay(config)
        human_type(page, comment_selectors, comment_text)
        inter_field_delay(config)

        # Submit
        human_scroll(page, "down", 150)
        before_url = page.url
        human_click(page, "#submit, input[type='submit'], button[type='submit']")

        try:
            page.wait_for_load_state("domcontentloaded", timeout=15000)
        except Exception:
            pass
        human_wait(1.5, 3.0)

        from core.success_detector import analyze_page
        result = analyze_page(page, before_url, site_name)

        logger.log({
            "date": datetime.utcnow().isoformat(), "strategy": "comments",
            "site_name": site_name, "url_submitted": url,
            "backlink_url": page.url if result.status == "success" else "",
            "status": result.status, "notes": result.notes[:200],
        })
        print(f"[comments/{blog_name}] Commented on: {title}")

    except Exception as e:
        logger.log({
            "date": datetime.utcnow().isoformat(), "strategy": "comments",
            "site_name": site_name, "url_submitted": url,
            "backlink_url": "", "status": "failed", "notes": str(e)[:200],
        })
    finally:
        context.close()


def run(config: dict, logger, dry_run: bool = False, headed: bool = False):
    session = get_session(config)
    print("[comments] Phase 1: Discovering VoIP blog posts...")
    posts = find_posts(config, session)
    print(f"[comments] Found {len(posts)} relevant posts")

    if not posts:
        print("[comments] No comment-friendly posts found.")
        return

    done = logger.get_done_sites()

    pw, browser = get_browser(config, headed_override=headed)
    try:
        for post in posts:
            site_name = f"comment:{post['blog']}:{post['url'][-30:]}"
            if site_name in done:
                continue
            post_comment(browser, post, config, logger, dry_run=dry_run)
            delay(config)
    finally:
        browser.close()
        pw.stop()
