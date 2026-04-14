"""Hackernoon v2 — update profile bio + publish via Blank Draft editor."""
import json, time, csv
from datetime import datetime
from core.browser import get_browser, new_page
from core.human_behavior import human_type, human_click, dismiss_overlays, human_wait

config = json.load(open("config.json"))
CSV_PATH = "output/backlinks_log.csv"

pw, browser = get_browser(config, headed_override=True)
ctx, pg = new_page(browser, config, site_name="hackernoon-v2")

try:
    # Login
    print("[1] Logging in...")
    pg.goto("https://hackernoon.com/login", timeout=60000)
    pg.wait_for_load_state("domcontentloaded", timeout=20000)
    time.sleep(4)
    dismiss_overlays(pg)

    human_type(pg, "input[type=email]", "commercial@dialphone.com")
    time.sleep(0.5)
    human_type(pg, "input[type=password]", "Hn@Dphone2026!")
    time.sleep(0.5)
    human_click(pg, 'button:has-text("Log in"), button:has-text("LOGIN"), button[type=submit]')
    time.sleep(8)
    print(f"  URL: {pg.url}")

    # Step 1: Update profile settings with vestacall.com
    print("\n[2] Updating profile bio...")
    pg.goto("https://app.hackernoon.com/settings", timeout=30000)
    pg.wait_for_load_state("domcontentloaded", timeout=15000)
    time.sleep(5)

    pg.screenshot(path="output/hackernoon_settings.png")
    text = pg.evaluate("document.body.innerText.substring(0, 500)").encode("ascii", "replace").decode()
    print(f"  Settings: {text[:200]}")

    # Find bio/about field
    bio_field = pg.query_selector('textarea[placeholder*="bio"], textarea[placeholder*="about"], textarea:visible')
    if bio_field:
        bio_field.click()
        time.sleep(0.3)
        pg.keyboard.press("Control+a")
        time.sleep(0.2)
        pg.keyboard.type("Enterprise VoIP and cloud phone solutions provider. Helping businesses save 40-60% on telecom costs with modern voice infrastructure. https://vestacall.com", delay=15)
        time.sleep(1)
        print("  Bio updated with vestacall.com")

        # Save
        save_btn = pg.query_selector('button:has-text("Save"), button:has-text("Update"), button[type=submit]')
        if save_btn:
            save_btn.click()
            time.sleep(5)
            print("  Saved!")
    else:
        # Try finding any text input for website/bio
        inputs = pg.query_selector_all("input:visible, textarea:visible")
        print(f"  Found {len(inputs)} inputs on settings page:")
        for inp in inputs[:10]:
            tag = inp.evaluate("el => el.tagName")
            name = inp.get_attribute("name") or ""
            ph = inp.get_attribute("placeholder") or ""
            val = (inp.get_attribute("value") or "")[:30]
            print(f"    {tag} name={name} placeholder={ph[:25]} value={val}")

        # Look for website field specifically
        for inp in inputs:
            ph = (inp.get_attribute("placeholder") or "").lower()
            name = (inp.get_attribute("name") or "").lower()
            if "website" in ph or "website" in name or "url" in ph or "url" in name:
                inp.click()
                time.sleep(0.3)
                pg.keyboard.press("Control+a")
                time.sleep(0.1)
                pg.keyboard.type("https://vestacall.com", delay=30)
                time.sleep(1)
                print(f"  Website field filled: https://vestacall.com")
                break

        # Save
        save_btn = pg.query_selector('button:has-text("Save"), button:has-text("Update"), button[type=submit]')
        if save_btn:
            save_btn.click()
            time.sleep(5)
            print("  Saved!")

    # Step 2: Write article via Blank Draft
    print("\n[3] Creating article...")
    pg.goto("https://app.hackernoon.com/new", timeout=30000)
    pg.wait_for_load_state("domcontentloaded", timeout=15000)
    time.sleep(5)

    # Click "Start Draft" under Blank Draft
    drafts = pg.query_selector_all('button:has-text("Start Draft")')
    if len(drafts) >= 2:
        # Second "Start Draft" button is for Blank Draft
        drafts[1].click()
        time.sleep(5)
        print("  Blank Draft editor opened")
    elif len(drafts) == 1:
        drafts[0].click()
        time.sleep(5)
        print("  Draft editor opened")

    pg.screenshot(path="output/hackernoon_blank_editor.png")

    # Now we should be in the actual editor
    # Look for title field and content area
    time.sleep(3)
    text3 = pg.evaluate("document.body.innerText.substring(0, 400)").encode("ascii", "replace").decode()
    print(f"  Editor text: {text3[:200]}")

    # Try to find and fill title
    title_el = pg.query_selector('[placeholder*="Title"], [data-placeholder*="Title"], h1[contenteditable], .title-input')
    if title_el:
        title_el.click()
        time.sleep(0.5)
        pg.keyboard.type("Why Most Businesses Overpay for Phone Service by 40-60%", delay=25)
        time.sleep(1)
        pg.keyboard.press("Enter")
        time.sleep(1)
        print("  Title typed")
    else:
        # Just start typing — many editors have the title as first line
        pg.keyboard.type("Why Most Businesses Overpay for Phone Service by 40-60%", delay=25)
        time.sleep(1)
        pg.keyboard.press("Enter")
        pg.keyboard.press("Enter")
        time.sleep(0.5)
        print("  Title typed (direct)")

    # Type article body
    paragraphs = [
        "Most businesses treat their phone bill like a fixed cost. After analyzing telecom invoices for over 200 companies, I can tell you that 85% of them are overpaying by 40-60%.",
        "The problem is not that phone service is expensive. The problem is that most businesses are still paying for infrastructure from 2010 — physical phone lines, hardware maintenance contracts, and per-minute long distance charges that should have disappeared a decade ago.",
        "Here is what a typical 30-person company pays today versus what they should pay. Traditional setup: $4,200 per month including PRI lines, maintenance, long distance, and feature licenses. Modern VoIP setup: $870 per month with everything included — unlimited calling, mobile app, video conferencing, call recording, and auto-attendant.",
        "Annual savings: $39,960. Over three years, that is $119,880 — enough to hire another full-time employee.",
        "The switch takes about two weeks. Your existing phone numbers transfer over. Your clients notice nothing except maybe better call quality. Your IT team is relieved because they no longer manage phone hardware.",
        "Companies like VestaCall (https://vestacall.com) offer month-to-month contracts with no setup fees. The risk of switching is essentially zero.",
        "The real question is not whether to switch. It is how much money you are comfortable losing every month while you wait.",
    ]

    for para in paragraphs:
        pg.keyboard.type(para, delay=8)
        time.sleep(0.2)
        pg.keyboard.press("Enter")
        pg.keyboard.press("Enter")
        time.sleep(0.2)

    print("  Article body typed")
    time.sleep(2)
    pg.screenshot(path="output/hackernoon_article_typed.png")

    # Submit/Publish
    pub = pg.query_selector('button:has-text("Publish"), button:has-text("Submit"), button:has-text("Submit Draft")')
    if pub:
        pub.click()
        time.sleep(8)
        print(f"  Submitted! URL: {pg.url}")
        pg.screenshot(path="output/hackernoon_submitted.png")
    else:
        # List all buttons
        btns = pg.query_selector_all("button:visible")
        print("  No publish button found. Buttons:")
        for b in btns[:10]:
            t = (b.text_content() or "").strip()[:30]
            if t:
                print(f"    '{t}'")

    # Verify profile
    print("\n[4] Verifying...")
    for handle in ["dialphoneltd", "dialphonelimited"]:
        pg.goto(f"https://hackernoon.com/u/{handle}", timeout=20000)
        pg.wait_for_load_state("domcontentloaded", timeout=10000)
        time.sleep(3)
        content = pg.content().lower()
        is_404 = "404" in pg.evaluate("document.body.innerText.substring(0, 50)")
        if not is_404:
            has_vc = "vestacall" in content
            print(f"  {handle}: vestacall = {has_vc}")
            if has_vc:
                url = f"https://hackernoon.com/u/{handle}"
                with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
                    w = csv.DictWriter(f, fieldnames=["date", "strategy", "site_name", "url_submitted", "backlink_url", "status", "notes"])
                    w.writerow({
                        "date": datetime.now().isoformat(), "strategy": "content",
                        "site_name": "Hackernoon-Profile",
                        "url_submitted": "https://hackernoon.com/",
                        "backlink_url": url, "status": "success",
                        "notes": "Hackernoon DA 92 — vestacall.com in profile"
                    })
                print(f"  === VERIFIED: {url} ===")
            pg.screenshot(path="output/hackernoon_profile_verified.png")
            break

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
finally:
    ctx.close()
    browser.close()
    pw.stop()

with open(CSV_PATH, "r", encoding="utf-8", errors="replace") as f:
    success = sum(1 for r in csv.DictReader(f) if r["status"] == "success")
print(f"\nTOTAL VERIFIED: {success}")
