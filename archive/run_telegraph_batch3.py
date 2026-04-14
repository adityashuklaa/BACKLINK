"""Batch 3: Expert-level Telegraph articles — 20-year content writer quality."""
import json
import time
import csv
from datetime import datetime
from core.browser import get_browser, new_page
from core.human_behavior import dismiss_overlays, random_mouse_movement, human_wait

config = json.load(open("config.json"))
CSV_PATH = "output/backlinks_log.csv"

with open("data/expert_articles.json", "r") as f:
    ARTICLES = json.load(f)

def log_result(site_name, backlink_url, status, notes):
    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["date","strategy","site_name","url_submitted","backlink_url","status","notes"])
        writer.writerow({
            "date": datetime.now().isoformat(),
            "strategy": "content",
            "site_name": site_name,
            "url_submitted": "https://telegra.ph/",
            "backlink_url": backlink_url,
            "status": status,
            "notes": notes,
        })

pw, browser = get_browser(config, headed_override=True)

for i, article in enumerate(ARTICLES):
    title = article["title"]
    site_name = f"Telegraph-Expert-{i+1}"

    print(f"\n{'='*60}")
    print(f"EXPERT ARTICLE {i+1}/5: {title}")
    print(f"{'='*60}")

    context, page = new_page(browser, config, site_name=site_name)
    try:
        page.goto("https://telegra.ph/", timeout=60000)
        page.wait_for_load_state("domcontentloaded", timeout=20000)
        time.sleep(4)
        dismiss_overlays(page)
        random_mouse_movement(page)
        human_wait(1, 2)

        # Type title
        page.keyboard.type(title, delay=40)
        time.sleep(0.5)
        page.keyboard.press("Enter")
        time.sleep(0.5)

        # Author
        author_el = page.query_selector("[data-placeholder*='name'], [data-placeholder*='author']")
        if author_el:
            author_el.click()
            time.sleep(0.3)
            page.keyboard.type("VestaCall Insights", delay=30)
            page.keyboard.press("Enter")
            time.sleep(0.5)

        # Type body — slightly slower for expert content (more natural)
        for para in article["body"]:
            page.keyboard.type(para, delay=10)
            time.sleep(0.3)
            page.keyboard.press("Enter")
            page.keyboard.press("Enter")
            time.sleep(0.2)

        time.sleep(2)

        # Publish
        publish_btn = page.query_selector("button:has-text('Publish'), a:has-text('PUBLISH'), button:has-text('PUBLISH')")
        if publish_btn:
            publish_btn.click()
            time.sleep(5)
            print("  Published!")

        # Build possible URLs
        slug = title.replace(" ", "-").replace("'", "").replace(",", "").replace(".", "")
        # Remove special chars that Telegraph strips
        slug = "".join(c for c in slug if c.isalnum() or c == "-")
        # Remove double dashes
        while "--" in slug:
            slug = slug.replace("--", "-")
        today = datetime.now().strftime("%m-%d")
        possible = [
            f"https://telegra.ph/{slug}-{today}",
            f"https://telegra.ph/{title.replace(' ', '-')}-{today}",
        ]

        # Verify
        verified = False
        for url in possible:
            try:
                ctx2, pg2 = new_page(browser, config)
                pg2.goto(url, timeout=20000)
                pg2.wait_for_load_state("domcontentloaded", timeout=10000)
                time.sleep(2)
                if "vestacall.com" in pg2.content():
                    verified = True
                    print(f"  VERIFIED: {url}")
                    pg2.screenshot(path=f"output/telegraph_expert_{i+1}.png")
                    log_result(site_name, url, "success", f"Expert article verified at {url}")
                    ctx2.close()
                    break
                ctx2.close()
            except Exception:
                try: ctx2.close()
                except: pass

        if not verified:
            print("  Could not verify slug — trying page URL directly")
            # Try getting URL from the current page after publish
            current = page.url
            if current != "https://telegra.ph/" and "telegra.ph" in current:
                try:
                    ctx3, pg3 = new_page(browser, config)
                    pg3.goto(current, timeout=20000)
                    pg3.wait_for_load_state("domcontentloaded", timeout=10000)
                    time.sleep(2)
                    if "vestacall.com" in pg3.content():
                        verified = True
                        print(f"  VERIFIED via page URL: {current}")
                        log_result(site_name, current, "success", f"Expert article verified at {current}")
                    ctx3.close()
                except:
                    try: ctx3.close()
                    except: pass

            if not verified:
                log_result(site_name, "", "pending", "Published but slug not found")

    except Exception as e:
        print(f"  ERROR: {e}")
        log_result(site_name, "", "failed", str(e)[:200])
    finally:
        context.close()

    if i < len(ARTICLES) - 1:
        time.sleep(10)

browser.close()
pw.stop()

# Final summary
print("\n" + "="*60)
print("ALL VERIFIED BACKLINKS (Batches 1+2+3)")
print("="*60)
with open(CSV_PATH, "r") as f:
    rows = list(csv.DictReader(f))
    success = [r for r in rows if r["status"] == "success"]
    print(f"TOTAL VERIFIED: {len(success)}")
    for r in success:
        print(f"  {r['backlink_url']}")
