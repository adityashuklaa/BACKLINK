"""Retry 2 failed expert articles."""
import json, time, csv
from datetime import datetime
from core.browser import get_browser, new_page
from core.human_behavior import dismiss_overlays, random_mouse_movement, human_wait

config = json.load(open("config.json"))
CSV_PATH = "output/backlinks_log.csv"

with open("data/expert_articles.json", "r") as f:
    ALL = json.load(f)

RETRY = [ALL[0], ALL[4]]  # Article 1 and 5 that failed

def log_result(site_name, backlink_url, status, notes):
    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["date","strategy","site_name","url_submitted","backlink_url","status","notes"])
        writer.writerow({"date": datetime.now().isoformat(), "strategy": "content",
            "site_name": site_name, "url_submitted": "https://telegra.ph/",
            "backlink_url": backlink_url, "status": status, "notes": notes})

pw, browser = get_browser(config, headed_override=True)

for i, article in enumerate(RETRY):
    title = article["title"]
    site_name = f"Telegraph-Expert-Retry-{i+1}"
    print(f"\n{'='*60}")
    print(f"RETRY: {title}")
    print(f"{'='*60}")

    context, page = new_page(browser, config, site_name=site_name)
    try:
        page.goto("https://telegra.ph/", timeout=90000)
        page.wait_for_load_state("domcontentloaded", timeout=30000)
        time.sleep(5)
        dismiss_overlays(page)
        random_mouse_movement(page)
        human_wait(1, 2)

        page.keyboard.type(title, delay=40)
        time.sleep(0.5)
        page.keyboard.press("Enter")
        time.sleep(0.5)

        author_el = page.query_selector("[data-placeholder*='name'], [data-placeholder*='author']")
        if author_el:
            author_el.click()
            time.sleep(0.3)
            page.keyboard.type("VestaCall Insights", delay=30)
            page.keyboard.press("Enter")
            time.sleep(0.5)

        for para in article["body"]:
            page.keyboard.type(para, delay=10)
            time.sleep(0.3)
            page.keyboard.press("Enter")
            page.keyboard.press("Enter")
            time.sleep(0.2)

        time.sleep(2)
        publish_btn = page.query_selector("button:has-text('Publish'), a:has-text('PUBLISH'), button:has-text('PUBLISH')")
        if publish_btn:
            publish_btn.click()
            time.sleep(6)

        # Try page URL first (most reliable)
        current = page.url
        verified = False

        if current != "https://telegra.ph/" and "telegra.ph" in current:
            ctx2, pg2 = new_page(browser, config)
            try:
                pg2.goto(current, timeout=20000)
                pg2.wait_for_load_state("domcontentloaded", timeout=10000)
                time.sleep(2)
                if "vestacall.com" in pg2.content():
                    verified = True
                    print(f"  VERIFIED: {current}")
                    pg2.screenshot(path=f"output/telegraph_expert_retry_{i+1}.png")
                    log_result(site_name, current, "success", f"Expert article verified at {current}")
            except: pass
            try: ctx2.close()
            except: pass

        if not verified:
            # Try constructed slug
            slug = title.replace(" ", "-").replace("'", "").replace(",", "").replace(".", "")
            slug = slug.replace("\u2014", "").replace("\u2019", "").replace("$", "")
            slug = "".join(c for c in slug if c.isalnum() or c == "-")
            while "--" in slug: slug = slug.replace("--", "-")
            today = datetime.now().strftime("%m-%d")
            url = f"https://telegra.ph/{slug}-{today}"
            try:
                ctx3, pg3 = new_page(browser, config)
                pg3.goto(url, timeout=20000)
                pg3.wait_for_load_state("domcontentloaded", timeout=10000)
                time.sleep(2)
                if "vestacall.com" in pg3.content():
                    verified = True
                    print(f"  VERIFIED: {url}")
                    log_result(site_name, url, "success", f"Expert article verified at {url}")
                ctx3.close()
            except:
                try: ctx3.close()
                except: pass

        if not verified:
            print("  Could not verify")
            log_result(site_name, "", "pending", "Published but URL not found")

    except Exception as e:
        print(f"  ERROR: {e}")
        log_result(site_name, "", "failed", str(e)[:200])
    finally:
        context.close()

    if i < len(RETRY) - 1:
        time.sleep(10)

browser.close()
pw.stop()

# Count
with open(CSV_PATH, "r") as f:
    success = sum(1 for r in csv.DictReader(f) if r["status"] == "success")
print(f"\nTOTAL VERIFIED BACKLINKS: {success}")
