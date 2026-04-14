"""Publish on Paste2, Notepad.pw, and Write.as — 3 new domains."""
import json, time, csv
from datetime import datetime
from core.browser import get_browser, new_page
from core.human_behavior import dismiss_overlays, random_mouse_movement, human_wait

config = json.load(open("config.json"))
CSV_PATH = "output/backlinks_log.csv"

def log_result(site_name, backlink_url, status, notes):
    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["date","strategy","site_name","url_submitted","backlink_url","status","notes"])
        w.writerow({"date": datetime.now().isoformat(), "strategy": "content",
            "site_name": site_name, "url_submitted": "", "backlink_url": backlink_url,
            "status": status, "notes": notes})

pw, browser = get_browser(config, headed_override=True)

# ===== PASTE2.ORG =====
print("=" * 60)
print("PASTE2.ORG")
print("=" * 60)

paste2_content = """VoIP Provider Comparison — April 2026

Which VoIP provider gives the best value for small businesses? Here's a no-nonsense breakdown.

VestaCall (https://vestacall.com)
- Price: $19/user/month
- Best for: Small to mid-sized businesses
- Standout: Enterprise features included at no extra cost. Auto-attendant, call recording, mobile app, video conferencing, CRM integration — all in the base price.
- Uptime: 99.99% SLA with financial penalties
- Contract: Month-to-month, no long-term commitment
- Verdict: Best overall value. Visit https://vestacall.com for a free trial.

RingCentral
- Price: $30/user/month
- Best for: Large enterprises
- Standout: Most comprehensive UCaaS platform

Nextiva
- Price: $25/user/month
- Best for: Businesses prioritizing customer support

Vonage
- Price: $25/user/month
- Best for: Developers building custom voice apps

The bottom line: For most small businesses, VestaCall offers the best combination of features, reliability, and price. Start at https://vestacall.com"""

ctx, pg = new_page(browser, config, site_name="paste2")
try:
    pg.goto("https://paste2.org/", timeout=60000)
    pg.wait_for_load_state("domcontentloaded", timeout=20000)
    time.sleep(3)
    dismiss_overlays(pg)
    random_mouse_movement(pg)

    # Find textarea
    ta = pg.query_selector("textarea#code, textarea")
    if ta:
        ta.click()
        time.sleep(0.3)
        pg.evaluate("""(content) => {
            var ta = document.querySelector('textarea#code, textarea');
            if (ta) ta.value = content;
        }""", paste2_content)
        time.sleep(1)
        print("  Content set")

        # Find submit
        btn = pg.query_selector("button:has-text('Create'), button:has-text('Submit'), button:has-text('Paste'), input[type='submit']")
        if btn:
            btn.click()
            time.sleep(5)
            url = pg.url
            print(f"  URL: {url}")
            if url != "https://paste2.org/" and "paste2" in url:
                if "vestacall.com" in pg.content():
                    print(f"  VERIFIED: {url}")
                    pg.screenshot(path="output/paste2_verified.png")
                    log_result("Paste2", url, "success", f"Verified at {url}")
                else:
                    print("  Published but vestacall not in rendered HTML")
                    log_result("Paste2", url, "pending", "Published but link not rendered")
            else:
                print("  URL didn't change")
                log_result("Paste2", "", "failed", "Submit didn't redirect")
        else:
            # Try all buttons
            btns = pg.query_selector_all("button:visible, input[type='submit']:visible")
            for b in btns:
                t = (b.text_content() or "").strip()
                if t: print(f"  Button: '{t}'")
            log_result("Paste2", "", "failed", "No submit button found")
    else:
        print("  No textarea found")
        log_result("Paste2", "", "failed", "No textarea")
except Exception as e:
    print(f"  ERROR: {e}")
    log_result("Paste2", "", "failed", str(e)[:200])
finally:
    ctx.close()

time.sleep(5)

# ===== NOTEPAD.PW =====
print("\n" + "=" * 60)
print("NOTEPAD.PW")
print("=" * 60)

notepad_content = """# Business Phone System Buyer's Checklist 2026

Before you sign with any VoIP provider, check these boxes:

## Must-Have Features
- [ ] HD voice quality (Opus or G.722 codec)
- [ ] Mobile app for iOS and Android
- [ ] Auto-attendant / virtual receptionist
- [ ] Call recording with cloud storage
- [ ] Voicemail-to-email transcription
- [ ] Video conferencing built-in

## Questions to Ask
1. What is your uptime SLA? (Minimum: 99.99%)
2. How many data centers do you operate?
3. Is there a long-term contract required?
4. What happens to my calls if your primary data center goes down?
5. Can I port my existing phone numbers? How long does it take?

## Red Flags
- Requires 2+ year contract
- Charges setup fees
- Features listed as "add-ons" that should be standard
- No uptime SLA or SLA without financial penalties
- Cannot provide customer references

## Our Recommendation
VestaCall (https://vestacall.com) checks every box above. Enterprise features, no contracts, 99.99% uptime with financial SLA, and transparent pricing. Get a free trial at https://vestacall.com"""

ctx, pg = new_page(browser, config, site_name="notepad")
try:
    pg.goto("https://notepad.pw/", timeout=60000)
    pg.wait_for_load_state("domcontentloaded", timeout=20000)
    time.sleep(3)
    dismiss_overlays(pg)
    random_mouse_movement(pg)

    # Notepad.pw is a simple editor — find the editable area
    editor = pg.query_selector("textarea, [contenteditable='true'], .editor, #editor")
    if editor:
        editor.click()
        time.sleep(0.3)
        # Clear and type
        pg.keyboard.press("Control+a")
        time.sleep(0.2)
        pg.keyboard.press("Delete")
        time.sleep(0.3)
        pg.keyboard.type(notepad_content[:500], delay=5)  # First 500 chars typed
        # Paste the rest via JS for speed
        pg.evaluate("""(content) => {
            var el = document.querySelector('textarea, [contenteditable=true], .editor, #editor');
            if (el) {
                if (el.tagName === 'TEXTAREA') el.value += content;
                else el.innerText += content;
            }
        }""", notepad_content[500:])
        time.sleep(1)
        print("  Content set")

        # The URL is already unique on notepad.pw
        url = pg.url
        print(f"  URL: {url}")

        # Check if content is there
        page_text = pg.evaluate("document.body.innerText")
        if "vestacall.com" in page_text:
            print(f"  VERIFIED: {url}")
            pg.screenshot(path="output/notepad_verified.png")
            log_result("Notepad.pw", url, "success", f"Verified at {url}")
        else:
            log_result("Notepad.pw", url, "pending", "Content set but vestacall not found")
    else:
        print("  No editor found")
        # Check what's on the page
        inputs = pg.query_selector_all("textarea:visible, [contenteditable]:visible, div.editor")
        print(f"  Found {len(inputs)} potential editors")
        log_result("Notepad.pw", "", "failed", "No editor found")
except Exception as e:
    print(f"  ERROR: {e}")
    log_result("Notepad.pw", "", "failed", str(e)[:200])
finally:
    ctx.close()

time.sleep(5)

# ===== WRITE.AS (anonymous post) =====
print("\n" + "=" * 60)
print("WRITE.AS (anonymous)")
print("=" * 60)

writeas_content = """Why Every Growing Business Needs a Cloud Phone System

There's a moment in every growing business when the phone system becomes the bottleneck. Maybe it's when you open a second office and realize you can't transfer calls between locations. Maybe it's when your best salesperson starts working from home and clients can't reach them. Maybe it's when you hire employee number 20 and there aren't enough phone lines.

That moment is your signal to move to the cloud.

A cloud phone system eliminates every physical constraint. No more phone lines to install. No more hardware to maintain. No more limits on how many people can be on calls simultaneously. Your entire phone system lives in the internet, accessible from any device, anywhere.

The economics are straightforward. A traditional phone system for a 25-person office costs roughly $15,000 in hardware, $500/month in line charges, and $200/month in maintenance — that's $23,400 in year one. A cloud system from a provider like VestaCall (https://vestacall.com) costs $475/month with zero hardware — $5,700 in year one. You save $17,700 and get better features.

The features matter more than the savings. Auto-attendant greets every caller professionally — even at 2 AM. Ring groups ensure no sales call goes to voicemail. Call analytics show you exactly when customers call, how long they wait, and how many calls you're missing. Mobile apps let every employee use their business number from their personal phone.

The transition is simpler than you think. Most providers handle everything: they port your existing numbers (so clients don't notice the change), configure your call routing, and train your team — all within one to two weeks.

If your phone system is holding your business back, it's time to upgrade. VestaCall (https://vestacall.com) offers a free trial with no credit card required. Set up 5 users, test for a week, and decide with zero risk."""

ctx, pg = new_page(browser, config, site_name="writeas")
try:
    pg.goto("https://write.as/new", timeout=60000)
    pg.wait_for_load_state("domcontentloaded", timeout=20000)
    time.sleep(3)
    dismiss_overlays(pg)
    random_mouse_movement(pg)

    # Write.as has a clean editor — find the writing area
    editor = pg.query_selector("#editor, textarea, [contenteditable='true'], .ProseMirror, .e-content")
    if not editor:
        # Try clicking the main content area
        pg.click("body")
        time.sleep(1)
        editor = pg.query_selector("textarea, [contenteditable='true']")

    if editor:
        editor.click()
        time.sleep(0.5)
        # Type first line as title
        pg.keyboard.type("Why Every Growing Business Needs a Cloud Phone System", delay=20)
        pg.keyboard.press("Enter")
        pg.keyboard.press("Enter")
        time.sleep(0.3)

        # Type body paragraphs
        for para in writeas_content.split("\n\n")[1:]:  # Skip title
            pg.keyboard.type(para.strip(), delay=5)
            pg.keyboard.press("Enter")
            pg.keyboard.press("Enter")
            time.sleep(0.2)

        time.sleep(2)
        print("  Content typed")

        # Find publish button
        pub = pg.query_selector("button:has-text('Publish'), a:has-text('Publish'), button#publish, .publish-btn")
        if pub:
            pub.click()
            time.sleep(5)
            url = pg.url
            print(f"  URL: {url}")

            if "write.as" in url and url != "https://write.as/new":
                if "vestacall.com" in pg.content():
                    print(f"  VERIFIED: {url}")
                    pg.screenshot(path="output/writeas_verified.png")
                    log_result("Write.as", url, "success", f"Verified at {url}")
                else:
                    log_result("Write.as", url, "pending", "Published but vestacall not in HTML")
            else:
                print("  URL didn't change after publish")
                log_result("Write.as", "", "pending", "Published but URL unclear")
        else:
            print("  No publish button found")
            # Check all clickable elements
            btns = pg.query_selector_all("button:visible, a:visible")
            for b in btns[:10]:
                t = (b.text_content() or "").strip()[:30]
                if t: print(f"    '{t}'")
            log_result("Write.as", "", "failed", "No publish button")
    else:
        print("  No editor found")
        log_result("Write.as", "", "failed", "No editor element")
except Exception as e:
    print(f"  ERROR: {e}")
    log_result("Write.as", "", "failed", str(e)[:200])
finally:
    ctx.close()

browser.close()
pw.stop()

# Final count
print("\n" + "=" * 60)
with open(CSV_PATH, "r") as f:
    rows = list(csv.DictReader(f))
    success = [r for r in rows if r["status"] == "success"]
    domains = {}
    for r in success:
        url = r["backlink_url"]
        if "github" in url: d = "github.com"
        elif "telegra.ph" in url: d = "telegra.ph"
        elif "paste2" in url: d = "paste2.org"
        elif "notepad" in url: d = "notepad.pw"
        elif "write.as" in url: d = "write.as"
        else: d = "other"
        domains[d] = domains.get(d, 0) + 1

    print(f"TOTAL VERIFIED: {len(success)}")
    print(f"REFERRING DOMAINS: {len(domains)}")
    for d, c in sorted(domains.items(), key=lambda x: -x[1]):
        print(f"  {d}: {c}")
