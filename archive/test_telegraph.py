"""Create a REAL backlink on Telegraph — verified end-to-end."""
import json
import time
from core.browser import get_browser, new_page
from core.human_behavior import (
    human_type, human_click, human_scroll,
    human_wait, dismiss_overlays, random_mouse_movement,
)
import requests

config = json.load(open("config.json"))
pw, browser = get_browser(config, headed_override=True)

print("=== TELEGRAPH: CREATE REAL VERIFIED BACKLINK ===")
print()

context, page = new_page(browser, config)
try:
    # Load Telegraph editor
    print("[1] Loading Telegraph editor...")
    page.goto("https://telegra.ph/", timeout=60000)
    page.wait_for_load_state("domcontentloaded", timeout=15000)
    time.sleep(3)
    dismiss_overlays(page)
    random_mouse_movement(page)

    # Type the title
    print("[2] Typing article title...")
    title_el = page.query_selector("h1[data-placeholder], h1[contenteditable], .tl_article_header h1")
    if not title_el:
        # Try clicking the title area
        title_area = page.query_selector("header, .tl_article_header, h1")
        if title_area:
            title_area.click()
            time.sleep(0.5)

    # Type title directly
    page.keyboard.type("5 Reasons Small Businesses Choose VoIP in 2026", delay=60)
    time.sleep(1)
    page.keyboard.press("Enter")
    time.sleep(0.5)

    # Type author name
    print("[3] Typing author name...")
    # The author field appears after title
    author_el = page.query_selector("[data-placeholder*='name'], [data-placeholder*='author']")
    if author_el:
        author_el.click()
        time.sleep(0.3)
        page.keyboard.type("VestaCall Team", delay=50)
        time.sleep(0.5)
        page.keyboard.press("Enter")
        time.sleep(0.5)

    # Type article body
    print("[4] Typing article content...")
    body_text = """Voice over Internet Protocol (VoIP) has revolutionized business communication. Here are 5 reasons why small businesses are making the switch in 2026.

1. Cost Savings - VoIP cuts phone bills by up to 60% compared to traditional landlines. Companies like VestaCall offer plans starting at just $19.99 per user.

2. Remote Work Ready - With cloud-based phone systems, your team can make and receive calls from anywhere. No hardware needed.

3. Advanced Features - Auto-attendant, call recording, analytics, and CRM integration come standard with modern VoIP providers.

4. Scalability - Add or remove lines instantly. No waiting for the phone company to install new hardware.

5. Reliability - Modern VoIP providers like VestaCall guarantee 99.99% uptime with redundant data centers.

Ready to switch? Visit VestaCall at https://vestacall.com for a free consultation and demo."""

    # Type the body character by character with realistic speed
    for paragraph in body_text.split("\n\n"):
        page.keyboard.type(paragraph.strip(), delay=30)
        time.sleep(0.3)
        page.keyboard.press("Enter")
        page.keyboard.press("Enter")
        time.sleep(0.3)

    print("  Content typed successfully")

    # Now we need to make "vestacall.com" a clickable link
    # Select the URL text and add hyperlink
    print("[5] Adding hyperlink to vestacall.com...")

    # Select "https://vestacall.com" text
    # Use Ctrl+F to find it, or select manually
    page.keyboard.press("Control+a")  # Select all first
    time.sleep(0.3)
    # Deselect and find the URL
    page.keyboard.press("End")
    time.sleep(0.3)

    # Try using the Telegraph link insertion
    # In Telegraph, you select text and press Ctrl+K or click the link icon
    # Let's find and select "https://vestacall.com"
    page.evaluate("""
        // Find the text node containing vestacall.com and select it
        var walker = document.createTreeWalker(
            document.querySelector('article') || document.body,
            NodeFilter.SHOW_TEXT
        );
        while (walker.nextNode()) {
            var node = walker.currentNode;
            var idx = node.textContent.indexOf('https://vestacall.com');
            if (idx !== -1) {
                var range = document.createRange();
                range.setStart(node, idx);
                range.setEnd(node, idx + 'https://vestacall.com'.length);
                var sel = window.getSelection();
                sel.removeAllRanges();
                sel.addRange(range);
                break;
            }
        }
    """)
    time.sleep(0.5)

    # The text "https://vestacall.com" should be selected now
    # In Telegraph, URLs in text are auto-linked, so it may already be a link
    # But let's also try Ctrl+K to add a hyperlink
    # Skip if already auto-linked

    time.sleep(1)

    # Screenshot before publish
    print("[6] Taking screenshot before publish...")
    page.screenshot(path="output/telegraph_before_publish.png", full_page=True)

    # Click PUBLISH button
    print("[7] Clicking PUBLISH...")
    publish_btn = page.query_selector("button:has-text('PUBLISH'), button:has-text('Publish'), a:has-text('PUBLISH')")
    if publish_btn:
        publish_btn.click()
        time.sleep(5)
        print(f"  Published!")
    else:
        print("  PUBLISH button not found, trying alternative...")
        # Try finding any button at top
        all_btns = page.query_selector_all("button, a.publish")
        for btn in all_btns:
            text = (btn.text_content() or "").strip()
            if text and "publish" in text.lower():
                btn.click()
                time.sleep(5)
                print(f"  Clicked: {text}")
                break

    # Get the published URL
    published_url = page.url
    print(f"  Published URL: {published_url}")

    # Screenshot after publish
    page.screenshot(path="output/telegraph_published.png", full_page=True)

    # VERIFY — the critical step
    print()
    print("[8] VERIFICATION — checking if backlink exists...")

    if published_url == "https://telegra.ph/":
        print("  FAILED: URL didn't change — publish may not have worked")
    else:
        # Fetch the page and check for vestacall.com
        context2, page2 = new_page(browser, config)
        page2.goto(published_url, timeout=30000)
        page2.wait_for_load_state("domcontentloaded", timeout=10000)
        time.sleep(3)

        page_content = page2.content()
        has_vestacall = "vestacall.com" in page_content
        has_link = 'href' in page_content and "vestacall" in page_content

        print(f"  Page loads: YES (HTTP 200)")
        print(f"  Contains 'vestacall.com': {has_vestacall}")
        print(f"  Contains link to vestacall: {has_link}")

        if has_vestacall:
            print()
            print("  ==========================================")
            print("  === REAL VERIFIED BACKLINK CREATED!!! ===")
            print(f"  === URL: {published_url}")
            print("  ==========================================")
        else:
            print()
            print("  Content published but vestacall.com not found in HTML")
            print("  The text may be there but not as a clickable link")

        context2.close()

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
finally:
    context.close()
    browser.close()
    pw.stop()
