"""Mass Publisher — discover new platforms, publish humanized content at scale."""
import json, time, csv, requests
from datetime import datetime
from core.browser import get_browser, new_page
from core.human_behavior import dismiss_overlays, random_mouse_movement
from core.content_engine import get_content_piece, get_all_content
from core.platform_discovery import get_untested_platforms, get_working_platforms, PASTE_PLATFORMS

config = json.load(open("config.json"))
CSV_PATH = "output/backlinks_log.csv"

def log_result(site_name, backlink_url, status, notes):
    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["date","strategy","site_name","url_submitted","backlink_url","status","notes"])
        w.writerow({"date": datetime.now().isoformat(), "strategy": "content",
            "site_name": site_name, "url_submitted": "", "backlink_url": backlink_url,
            "status": status, "notes": notes})

pw, browser = get_browser(config, headed_override=True)

# PHASE 1: Test untested platforms
print("=" * 60)
print("PHASE 1: DISCOVERING NEW PLATFORMS")
print("=" * 60)

untested = get_untested_platforms()
new_working = []

for platform in untested:
    name = platform["name"]
    url = platform["url"]
    da = platform["da"]

    ctx, pg = new_page(browser, config, site_name=name)
    try:
        pg.goto(url, timeout=15000)
        pg.wait_for_load_state("domcontentloaded", timeout=10000)
        time.sleep(2)
        dismiss_overlays(pg)

        has_editor = pg.query_selector("textarea:visible, [contenteditable]:visible, .CodeMirror") is not None
        has_captcha = any(x in pg.content().lower() for x in ["recaptcha", "captcha", "turnstile"])
        login_req = "log in" in pg.evaluate("document.body.innerText.substring(0, 150)").lower()

        if has_editor and not has_captcha and not login_req:
            platform["tested"] = True
            platform["works"] = True
            new_working.append(platform)
            print(f"  NEW!  DA:{da:3} | {name}")
        elif has_captcha:
            platform["tested"] = True
            platform["works"] = False
            print(f"  CAPTCHA DA:{da:3} | {name}")
        elif login_req:
            platform["tested"] = True
            platform["works"] = False
            print(f"  LOGIN  DA:{da:3} | {name}")
        else:
            platform["tested"] = True
            platform["works"] = False
            print(f"  FAIL   DA:{da:3} | {name}")
    except Exception:
        print(f"  ERROR  DA:{da:3} | {name}")
        platform["tested"] = True
        platform["works"] = False
    finally:
        ctx.close()

print(f"\nDiscovered {len(new_working)} new working platforms")

# PHASE 2: Publish content on ALL working platforms
print("\n" + "=" * 60)
print("PHASE 2: PUBLISHING CONTENT")
print("=" * 60)

all_working = get_working_platforms() + new_working
content_pieces = get_all_content()
content_index = 0

for platform in all_working:
    # Skip platforms we already published on (check CSV)
    name = platform["name"]

    # Get existing entries for this platform
    existing = set()
    try:
        with open(CSV_PATH, "r", encoding="utf-8", errors="replace") as f:
            for row in csv.DictReader(f):
                if row["status"] == "success" and name.split(".")[0] in row.get("backlink_url", ""):
                    existing.add(row["site_name"])
    except:
        pass

    # Determine how many new pieces to publish on this platform
    # High DA = more pieces, Low DA = fewer
    if platform["da"] >= 60:
        target = 3  # Up to 3 pieces per high-DA platform
    elif platform["da"] >= 40:
        target = 2
    else:
        target = 1

    already_have = len(existing)
    to_publish = max(0, target - already_have)

    if to_publish == 0:
        print(f"\n  SKIP {name} — already have {already_have} pieces")
        continue

    for j in range(to_publish):
        if content_index >= len(content_pieces):
            content_index = 0  # Wrap around

        piece = content_pieces[content_index]
        content_index += 1

        site_label = f"{name}-{piece['id']}"
        print(f"\n  Publishing '{piece['title'][:40]}...' on {name} (DA {platform['da']})...")

        ctx, pg = new_page(browser, config, site_name=site_label)
        try:
            pg.goto(platform["url"], timeout=30000)
            pg.wait_for_load_state("domcontentloaded", timeout=15000)
            time.sleep(3)
            dismiss_overlays(pg)
            random_mouse_movement(pg)

            # Find editor
            editor = pg.query_selector("textarea:visible, [contenteditable]:visible, .CodeMirror")
            if editor:
                editor.click()
                time.sleep(0.5)
                pg.keyboard.press("Control+a")
                time.sleep(0.2)
                pg.keyboard.press("Delete")
                time.sleep(0.3)

                # Type title + content
                full_text = piece["title"] + "\n\n" + piece["content"]
                for line in full_text.split("\n"):
                    pg.keyboard.type(line, delay=2)
                    pg.keyboard.press("Enter")
                time.sleep(1)

                # Submit
                for sel in ['button:has-text("Create")', 'button:has-text("Submit")',
                            'button:has-text("Paste")', 'button:has-text("Send")',
                            'button:has-text("Save")', 'input[type=submit]', 'button[type=submit]']:
                    btn = pg.query_selector(sel)
                    if btn and btn.is_visible():
                        btn.click()
                        time.sleep(5)
                        break

                url = pg.url
                if url != platform["url"] and platform["name"].split(".")[0] in url:
                    # Verify
                    has_vc = "dialphone" in pg.content().lower()
                    if not has_vc:
                        try:
                            r = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
                            has_vc = "dialphone" in r.text.lower()
                        except:
                            pass

                    if has_vc:
                        print(f"  VERIFIED: {url}")
                        log_result(site_label, url, "success",
                                   f"{name} DA {platform['da']} — {piece['style']} content verified")
                    else:
                        print(f"  Published but dialphone not found")
                        log_result(site_label, url, "pending", "Published but dialphone not in page")
                else:
                    print(f"  URL didn't change")
            else:
                print(f"  No editor found")
        except Exception as e:
            print(f"  ERROR: {str(e)[:60]}")
        finally:
            ctx.close()

        time.sleep(3)

browser.close()
pw.stop()

# Final report
print("\n" + "=" * 60)
print("FINAL RESULTS")
print("=" * 60)
with open(CSV_PATH, "r", encoding="utf-8", errors="replace") as f:
    rows = list(csv.DictReader(f))
    success = [r for r in rows if r["status"] == "success"]

    domains = {}
    for r in success:
        u = r["backlink_url"]
        # Extract domain
        if "github.com" in u:
            d = "github.com/dialphonelimited"
        elif "/" in u.replace("https://", "").replace("http://", ""):
            d = u.replace("https://", "").replace("http://", "").split("/")[0]
        else:
            d = u
        domains[d] = domains.get(d, 0) + 1

    print(f"TOTAL VERIFIED: {len(success)}")
    print(f"REFERRING DOMAINS: {len(domains)}")
    for d, c in sorted(domains.items(), key=lambda x: -x[1]):
        print(f"  {d}: {c}")
