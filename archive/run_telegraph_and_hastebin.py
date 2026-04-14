"""Telegraph is back + fix Hastebin — humanized content on both."""
import json, time, csv, requests
from datetime import datetime
from core.browser import get_browser, new_page
from core.human_behavior import dismiss_overlays, random_mouse_movement, human_wait
from core.content_engine import get_content_piece

config = json.load(open("config.json"))
CSV_PATH = "output/backlinks_log.csv"

def log_result(site_name, backlink_url, status, notes):
    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["date","strategy","site_name","url_submitted","backlink_url","status","notes"])
        w.writerow({"date": datetime.now().isoformat(), "strategy": "content",
            "site_name": site_name, "url_submitted": "", "backlink_url": backlink_url,
            "status": status, "notes": notes})

# Get humanized content pieces
pieces = [get_content_piece(i) for i in range(5)]

pw, browser = get_browser(config, headed_override=True)

# ===== TELEGRAPH — 5 humanized expert articles =====
print("=" * 60)
print("TELEGRAPH — 5 HUMANIZED ARTICLES")
print("=" * 60)

for i, piece in enumerate(pieces):
    site_name = f"Telegraph-Human-{i+1}"
    print(f"\n  Article {i+1}/5: {piece['title'][:50]}... [{piece['style']}]")

    ctx, pg = new_page(browser, config, site_name=site_name)
    try:
        pg.goto("https://telegra.ph/", timeout=60000)
        pg.wait_for_load_state("domcontentloaded", timeout=20000)
        time.sleep(4)
        dismiss_overlays(pg)
        random_mouse_movement(pg)
        human_wait(1, 2)

        # Title
        pg.keyboard.type(piece["title"], delay=35)
        time.sleep(0.5)
        pg.keyboard.press("Enter")
        time.sleep(0.5)

        # Author — use the voice from content engine
        author_el = pg.query_selector("[data-placeholder*='name'], [data-placeholder*='author']")
        if author_el:
            author_el.click()
            time.sleep(0.3)
            pg.keyboard.type("Industry Analysis", delay=30)
            pg.keyboard.press("Enter")
            time.sleep(0.5)

        # Body — type naturally
        for para in piece["content"].split("\n\n"):
            para = para.strip()
            if not para:
                continue
            pg.keyboard.type(para, delay=8)
            time.sleep(0.2)
            pg.keyboard.press("Enter")
            pg.keyboard.press("Enter")
            time.sleep(0.15)

        time.sleep(2)

        # Publish
        pub = pg.query_selector("button:has-text('Publish'), a:has-text('PUBLISH'), button:has-text('PUBLISH')")
        if pub:
            pub.click()
            time.sleep(6)

        # Verify
        current = pg.url
        verified = False

        # Try current URL first
        if current != "https://telegra.ph/" and "telegra.ph" in current:
            if "vestacall" in pg.content().lower():
                verified = True
                print(f"  VERIFIED: {current}")
                log_result(site_name, current, "success", f"Telegraph humanized [{piece['style']}] verified")

        # Try constructed slug
        if not verified:
            slug = piece["title"].replace(" ", "-").replace("'", "").replace(",", "").replace(":", "")
            slug = slug.replace("\u2014", "-").replace("\u2019", "")
            slug = "".join(c for c in slug if c.isalnum() or c == "-")
            while "--" in slug:
                slug = slug.replace("--", "-")
            today = datetime.now().strftime("%m-%d")
            url = f"https://telegra.ph/{slug}-{today}"

            try:
                ctx2, pg2 = new_page(browser, config)
                pg2.goto(url, timeout=15000)
                pg2.wait_for_load_state("domcontentloaded", timeout=10000)
                time.sleep(2)
                if "vestacall" in pg2.content().lower():
                    verified = True
                    print(f"  VERIFIED: {url}")
                    log_result(site_name, url, "success", f"Telegraph humanized [{piece['style']}] verified")
                ctx2.close()
            except:
                try:
                    ctx2.close()
                except:
                    pass

        if not verified:
            print("  Published but URL not verified")
            log_result(site_name, "", "pending", f"Telegraph humanized [{piece['style']}] — published, URL unclear")

    except Exception as e:
        print(f"  ERROR: {str(e)[:60]}")
        log_result(site_name, "", "failed", str(e)[:200])
    finally:
        ctx.close()

    if i < len(pieces) - 1:
        time.sleep(8)

# ===== HASTEBIN (DA 88) — fix URL capture =====
print("\n" + "=" * 60)
print("HASTEBIN (DA 88) — FIX URL CAPTURE")
print("=" * 60)

hastebin_content = get_content_piece(3)  # Opinion piece

ctx, pg = new_page(browser, config, site_name="hastebin")
try:
    pg.goto("https://www.toptal.com/developers/hastebin", timeout=30000)
    pg.wait_for_load_state("domcontentloaded", timeout=15000)
    time.sleep(4)
    dismiss_overlays(pg)

    # Hastebin auto-focuses the editor — just start typing
    full_text = hastebin_content["title"] + "\n\n" + hastebin_content["content"]
    pg.keyboard.type(full_text, delay=2)
    time.sleep(2)
    print("  Content typed")

    # Save with Ctrl+S (hastebin keyboard shortcut)
    pg.keyboard.press("Control+s")
    time.sleep(5)

    url = pg.url
    print(f"  URL after save: {url}")

    if url != "https://www.toptal.com/developers/hastebin" and "hastebin" in url:
        # Verify
        try:
            r = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0 Chrome/125.0.0.0"})
            if "vestacall" in r.text.lower():
                print(f"  VERIFIED: {url}")
                log_result("Hastebin", url, "success", "Hastebin DA 88 — new domain verified")
            else:
                # Try raw URL
                raw_url = url.replace("/share/", "/raw/") if "/share/" in url else url + "/raw"
                r2 = requests.get(raw_url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
                if "vestacall" in r2.text.lower():
                    print(f"  VERIFIED (raw): {url}")
                    log_result("Hastebin", url, "success", "Hastebin DA 88 — verified via raw content")
                else:
                    print("  Published but vestacall not in response")
        except Exception as e:
            print(f"  Verify error: {e}")

        # Also check browser content
        if "vestacall" in pg.content().lower():
            print(f"  Browser confirms vestacall present")
    else:
        print("  URL didn't change — trying click Save button instead")
        save_btn = pg.query_selector('button:has-text("Save"), button[title="Save"]')
        if save_btn:
            save_btn.click()
            time.sleep(5)
            url = pg.url
            print(f"  After button click: {url}")

except Exception as e:
    print(f"  ERROR: {e}")
finally:
    ctx.close()

browser.close()
pw.stop()

# Final
with open(CSV_PATH, "r", encoding="utf-8", errors="replace") as f:
    rows = list(csv.DictReader(f))
    success = [r for r in rows if r["status"] == "success"]
    domains = {}
    for r in success:
        u = r["backlink_url"]
        if "github.com" in u: d = "github.com/dialphonelimited"
        elif "telegra.ph" in u: d = "telegra.ph"
        else:
            d = u.replace("https://", "").replace("http://", "").split("/")[0]
        domains[d] = domains.get(d, 0) + 1

    print(f"\n{'='*60}")
    print(f"TOTAL VERIFIED: {len(success)}")
    print(f"REFERRING DOMAINS: {len(domains)}")
    for d, c in sorted(domains.items(), key=lambda x: -x[1]):
        print(f"  {d}: {c}")
