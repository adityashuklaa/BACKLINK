"""Brownbook end-to-end test — proper submission + verification."""
import json
import time
from core.browser import get_browser, new_page
from core.human_behavior import (
    human_type, human_click, human_scroll,
    human_wait, dismiss_overlays, random_mouse_movement,
)
from core.rate_limiter import inter_field_delay

config = json.load(open("config.json"))
pw, browser = get_browser(config, headed_override=True)
b = config.get("business", {})
addr = b.get("address", {})

print("=== BROWNBOOK: FULL END-TO-END TEST ===")
print()

context, page = new_page(browser, config)
try:
    # Load form
    print("[1] Loading form...")
    page.goto("https://www.brownbook.net/add-business/", timeout=60000)
    page.wait_for_load_state("domcontentloaded", timeout=20000)
    time.sleep(4)
    dismiss_overlays(page)
    random_mouse_movement(page)
    human_wait(2, 3)

    # Select country
    print("[2] Selecting country...")
    country_input = page.query_selector("input#react-select-country_select-input")
    if country_input:
        country_input.click()
        time.sleep(0.5)
        page.keyboard.type("United States", delay=80)
        time.sleep(1.5)
        page.keyboard.press("Enter")
        time.sleep(1)
        print("  Country: United States selected")
    inter_field_delay(config)

    # Business name
    print("[3] Business name...")
    human_type(page, 'input[name="name"]', b.get("name", "VestaCall"))
    inter_field_delay(config)

    # Category
    print("[4] Category...")
    cat_input = page.query_selector('input[placeholder="Select category"]')
    if cat_input:
        cat_input.click()
        time.sleep(0.5)
        page.keyboard.type("Telecommunications", delay=80)
        time.sleep(1.5)
        page.keyboard.press("Enter")
        time.sleep(0.5)
        print("  Category: Telecommunications")
    inter_field_delay(config)

    # Address
    print("[5] Address...")
    if isinstance(addr, dict):
        human_type(page, 'textarea[name="address"]', addr.get("street", "1234 Tech Avenue"))
        inter_field_delay(config)
        human_type(page, 'input[name="city"]', addr.get("city", "San Francisco"))
        inter_field_delay(config)
        human_type(page, 'input[name="zip_code"]', addr.get("zip", "94105"))
        inter_field_delay(config)

    # Contact
    print("[6] Contact info...")
    human_type(page, 'input[name="phone"]', b.get("phone", "+1-800-555-0192"))
    inter_field_delay(config)
    human_type(page, 'input[name="email"]', b.get("email", "vestacall.testing@gmail.com"))
    inter_field_delay(config)

    # Website — THE BACKLINK
    print("[7] Website URL (THE BACKLINK)...")
    human_type(page, 'input[name="website"]', b.get("website", "https://vestacall.com"))
    inter_field_delay(config)
    human_type(page, 'input[name="display_website"]', b.get("website", "https://vestacall.com"))
    inter_field_delay(config)

    # Scroll down to see all fields
    print("[8] Scrolling to bottom...")
    human_scroll(page, "down", 500)
    time.sleep(1)

    # Screenshot before submit
    page.screenshot(path="output/brownbook_filled.png", full_page=True)
    print("  Screenshot: output/brownbook_filled.png")

    # Find submit button
    print("[9] Finding submit button...")
    all_btns = page.query_selector_all("button")
    for btn in all_btns:
        try:
            text = (btn.text_content() or "").strip()
            visible = btn.is_visible()
            btn_type = btn.get_attribute("type") or ""
            if visible and text:
                print(f"  Button: '{text}' type={btn_type} visible={visible}")
        except Exception:
            pass

    # Click submit — find the FORM submit, not nav buttons
    print("[10] Clicking submit...")
    before_url = page.url

    # First try: form submit button (inside the form, not header nav)
    clicked = False
    form_submit = page.query_selector('form button[type="submit"]')
    if form_submit and form_submit.is_visible():
        text = (form_submit.text_content() or "").strip()
        print(f"  Found form submit: '{text}'")
        form_submit.click()
        clicked = True

    if not clicked:
        # Try input submit inside form
        input_submit = page.query_selector('form input[type="submit"]')
        if input_submit and input_submit.is_visible():
            print(f"  Found form input submit")
            input_submit.click()
            clicked = True

    if not clicked:
        # Try any button with submit-like text that's NOT in the header
        for sel in [
            'main button:has-text("Submit")',
            'main button:has-text("Add Business")',
            '.form button', '#form button',
            'button:has-text("Submit")',
            'button:has-text("Save")',
        ]:
            try:
                btn = page.query_selector(sel)
                if btn and btn.is_visible():
                    text = (btn.text_content() or "").strip()
                    # Skip navigation buttons
                    if "sign in" in text.lower() or "register" in text.lower() or "search" in text.lower():
                        continue
                    print(f"  Clicking: '{text}'")
                    btn.click()
                    clicked = True
                    break
            except Exception:
                pass

    if not clicked:
        print("  WARNING: No submit button found — trying Enter key on last field")
        page.keyboard.press("Enter")
        clicked = True

    time.sleep(5)
    after_url = page.url

    # Screenshot after submit
    page.screenshot(path="output/brownbook_submitted.png", full_page=True)
    print(f"  URL: {before_url[:50]} -> {after_url[:50]}")

    # Check result
    print("[11] Analyzing result...")
    result_text = page.evaluate("document.body ? document.body.innerText.substring(0, 600) : ''")
    print(f"  Page text: {result_text[:300].encode('ascii', 'replace').decode()}")

    # Handle step 2 if present
    if "step 2" in result_text.lower():
        print("[12] Step 2 found — handling...")
        # Look for description textarea or other fields
        step2_inputs = page.query_selector_all("input:visible, textarea:visible")
        print(f"  Step 2 inputs: {len(step2_inputs)}")
        for inp in step2_inputs[:10]:
            name = inp.get_attribute("name") or ""
            ph = inp.get_attribute("placeholder") or ""
            print(f"    name={name} placeholder={ph[:30]}")

        # Fill description if available
        desc = b.get("description", "")
        if desc:
            for sel in ['textarea[name="description"]', 'textarea[name="about"]', "textarea"]:
                if human_type(page, sel, desc[:300]):
                    print(f"  Filled description")
                    break

        # Submit step 2
        time.sleep(2)
        for sel in ['button[type="submit"]', 'button:has-text("Submit")', 'button:has-text("Finish")']:
            try:
                btn = page.query_selector(sel)
                if btn and btn.is_visible():
                    btn.click()
                    print(f"  Step 2 submitted")
                    time.sleep(5)
                    break
            except Exception:
                pass

        page.screenshot(path="output/brownbook_step2_done.png", full_page=True)
        final_text = page.evaluate("document.body ? document.body.innerText.substring(0, 500) : ''")
        print(f"  Final page: {final_text[:200].encode('ascii', 'replace').decode()}")

    # VERIFY
    print()
    print("[13] VERIFICATION...")
    context2, page2 = new_page(browser, config)

    # Search Brownbook
    page2.goto("https://www.brownbook.net/?q=vestacall", timeout=30000)
    page2.wait_for_load_state("domcontentloaded", timeout=15000)
    time.sleep(3)
    bb_text = page2.evaluate("document.body ? document.body.innerText.substring(0, 500) : ''")
    bb_found = "vestacall" in bb_text.lower()
    print(f"  Brownbook search: {'FOUND' if bb_found else 'NOT FOUND'}")
    print(f"  Text: {bb_text[:150].encode('ascii', 'replace').decode()}")

    context2.close()

    print()
    if bb_found:
        print("=== REAL VERIFIED BACKLINK ===")
    else:
        print("=== HONEST: submitted but listing not found yet ===")
        print("  May need admin approval — this is the truth")

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
finally:
    context.close()
    browser.close()
    pw.stop()
