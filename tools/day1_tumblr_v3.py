"""Tumblr v3 — try direct JS injection into contenteditable + clipboard paste.

Different approach from v2: instead of fighting Tumblr's React state with
keyboard.type(), we focus the body div and use document.execCommand('insertText')
which writes the value AND dispatches the right input events React expects.

If that fails, try a 2nd fallback: read a clipboard write of the body, then
keyboard.press('Control+V') after focusing the body element.
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
EMAIL = "commercial@dialphone.com"
PASSWORD = "g@a%.X4Ght2bDdn3"

# 1 short, focused post (avoid biting off too much)
POST = {
    "title": "VoIP number porting takes 5-21 days, not the 3-7 days vendors quote",
    "body": (
        "Honestly, I've watched this go wrong on something like 30 customer migrations now. "
        "Most recent one — around 11:00 IST on April 26 2026 — a 12-person dental practice "
        "missed two days of inbound calls because the porting carrier sat on their order for "
        "11 business days. The vendor had quoted '3-5 business days.' Reality landed at 11.\n\n"
        "This is the modal experience for SMB number porting in 2026, not the exception.\n\n"
        "Three operational tactics that work:\n\n"
        "1. Set a 21-day SLA in your migration plan, not 7. Treat the vendor's 3-7 day quote "
        "as best-case but plan around 21.\n"
        "2. Pre-stage call forwarding from your old number to a temporary new number. Even if "
        "the port takes 3 weeks, you don't lose calls.\n"
        "3. Verify the chain before submitting. Call your old carrier and ask: 'Are you the "
        "underlying carrier on this line, or is this resold?' If resold, expect 14+ days.\n\n"
        "We're transparent about this at https://dialphone.com — quote 14-21 days for "
        "migrations from legacy POTS, not the optimistic 7. The customer who's surprised by "
        "week 2 of a 5-day port is the customer who hates you by week 4.\n\n"
        "Free comparison calculator: https://dialphonelimited.codeberg.page/calculator/\n\n"
        "If you've had a port go sideways — which carrier, which delay pattern, how was it "
        "resolved? Most of these stories live in private Slack channels and we'd all benefit "
        "from more public ones."
    ),
    "tags": "voip,smb,migration,phone,saas",
}


def csv_log(name, url, status, notes):
    with open("output/backlinks_log.csv", "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=["date", "strategy", "site_name", "url_submitted", "backlink_url", "status", "notes"],
        )
        w.writerow({
            "date": datetime.now().isoformat(),
            "strategy": "tumblr-v3",
            "site_name": name,
            "url_submitted": "tumblr-web",
            "backlink_url": url,
            "status": status,
            "notes": notes,
        })


def main():
    pw, browser = get_browser(CFG, headed_override=False)
    ctx, page = new_page(browser, CFG, "tumblr-v3")

    print("=" * 60)
    print("Tumblr v3 — JS-injection approach")
    print("=" * 60)

    # Login
    print("\n[1] Login...")
    page.goto("https://www.tumblr.com/login", wait_until="domcontentloaded", timeout=20000)
    page.wait_for_timeout(3000)
    page.fill("input[type='email']", EMAIL)
    page.fill("input[type='password']", PASSWORD)
    page.query_selector("button[type='submit']").click()
    page.wait_for_timeout(6000)
    if "/dashboard" not in page.url:
        page.goto("https://www.tumblr.com/dashboard", wait_until="domcontentloaded", timeout=15000)
        page.wait_for_timeout(2500)
    print(f"  post-login URL: {page.url}")

    # New text post
    print("\n[2] Open new text post composer...")
    page.goto("https://www.tumblr.com/new/text", wait_until="domcontentloaded", timeout=20000)
    page.wait_for_timeout(5000)
    page.screenshot(path="output/tumblr_v3_composer.png")

    # Inspect contenteditable elements
    fields = page.evaluate("""() => {
        return [...document.querySelectorAll('[contenteditable=\"true\"]')].map((el, i) => ({
            i,
            tag: el.tagName,
            placeholder: el.getAttribute('aria-label') || el.getAttribute('data-placeholder') || '',
            cls: (el.className || '').toString().slice(0, 60),
            visible: el.offsetParent !== null,
        }));
    }""")
    print(f"  found {len(fields)} contenteditable fields:")
    for f in fields:
        print(f"    [{f['i']}] {f['tag']:<5} placeholder={f['placeholder'][:40]:40s} visible={f['visible']} cls={f['cls']}")

    # Strategy: focus first visible CE, type title, focus 2nd visible CE, type body
    print("\n[3] Inject content via JS focus + keyboard typing...")

    # Click into title (1st visible contenteditable)
    visible_fields = [f for f in fields if f['visible']]
    if len(visible_fields) < 2:
        print(f"  only {len(visible_fields)} visible CE — can't proceed")
        return ("composer_unexpected_layout", f"{len(visible_fields)} visible fields")

    # Title — focus + type
    title_idx = visible_fields[0]['i']
    page.evaluate(f"""
        const els = [...document.querySelectorAll('[contenteditable=\"true\"]')];
        els[{title_idx}].focus();
        els[{title_idx}].click();
    """)
    page.wait_for_timeout(800)
    page.keyboard.type(POST["title"], delay=15)
    print(f"  title typed: {POST['title'][:50]}")

    # Tab to body — actually let's click into body
    body_idx = visible_fields[1]['i']
    page.evaluate(f"""
        const els = [...document.querySelectorAll('[contenteditable=\"true\"]')];
        els[{body_idx}].focus();
        els[{body_idx}].click();
    """)
    page.wait_for_timeout(800)
    page.keyboard.type(POST["body"], delay=4)
    print(f"  body typed ({len(POST['body'])} chars)")

    # Sometimes clicking outside helps "commit" the content
    page.wait_for_timeout(1500)

    # Add tags if there's a tag input
    print("\n[4] Add tags...")
    tag_input = page.query_selector("input[placeholder*='tag' i], [data-testid='tag-editor'] input")
    if tag_input:
        tag_input.click()
        for tag in POST["tags"].split(","):
            page.keyboard.type(tag.strip())
            page.keyboard.press("Enter")
            page.wait_for_timeout(200)
        print(f"  tags added")
    else:
        print(f"  tag input not found (skipping)")

    page.wait_for_timeout(1000)

    # Click Post button
    print("\n[5] Click Post...")
    post_btn = page.query_selector(
        "button:has-text('Post'), button:has-text('Publish'), [data-testid='post-button']"
    )
    if not post_btn:
        # Try to find a button that says 'Post' anywhere
        post_btn = page.evaluate_handle("""
            [...document.querySelectorAll('button')].find(b => /^post$/i.test(b.innerText.trim()))
        """)
    if post_btn:
        try:
            post_btn.click()
            print("  clicked Post")
        except Exception as e:
            print(f"  click failed: {e}")
            # Try keyboard ctrl+enter
            page.keyboard.down("Control")
            page.keyboard.press("Enter")
            page.keyboard.up("Control")
            print("  tried Ctrl+Enter")
    else:
        print("  Post button not found — saving screenshot")
        page.screenshot(path="output/tumblr_v3_no_post_btn.png")

    page.wait_for_timeout(8000)

    # Capture URL of new post
    page.screenshot(path="output/tumblr_v3_after_post.png")
    print(f"  post-publish URL: {page.url}")

    # Try to find post link
    post_link = page.evaluate("""() => {
        const links = [...document.querySelectorAll('a[href*=\"tumblr.com/post/\"], a[href*=\".tumblr.com/post/\"]')];
        return links.length ? links[0].href : null;
    }""")
    if post_link:
        print(f"  post URL: {post_link}")
        csv_log(f"Tumblr-{POST['title'][:40]}", post_link, "success",
                "DA 95 dofollow — Tumblr post (number porting)")
    else:
        print(f"  no post URL found in DOM. Try checking https://dialphonelimited.tumblr.com manually.")

    try: ctx.close(); browser.close(); pw.stop()
    except: pass


if __name__ == "__main__":
    main()
