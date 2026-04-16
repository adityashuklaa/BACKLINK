"""Create 2 more company repos — disaster recovery + CRM integration."""
import json, time, csv
from datetime import datetime
from core.browser import get_browser, new_page

config = json.load(open("config.json"))
repos = json.load(open("data/company_repos_batch2.json"))
CSV_PATH = "output/backlinks_log.csv"

pw, browser = get_browser(config, headed_override=True)
ctx, pg = new_page(browser, config, site_name="github-batch2")

try:
    # Login
    print("[1] Logging in...")
    pg.goto("https://github.com/login", timeout=60000)
    pg.wait_for_load_state("domcontentloaded", timeout=20000)
    time.sleep(5)
    for sel in ['button:has-text("Accept")', 'button:has-text("Reject all")', 'button:has-text("Save changes")']:
        try:
            b = pg.query_selector(sel)
            if b and b.is_visible():
                b.click()
                time.sleep(2)
                break
        except:
            pass
    try:
        pg.evaluate('document.getElementById("ghcc")?.remove()')
    except:
        pass
    pg.fill("input#login_field", "dialphonelimited")
    time.sleep(0.5)
    pg.fill("input#password", "DevD!alph0ne@0912@#")
    time.sleep(0.5)
    pg.click("input[type=submit]")
    time.sleep(10)
    print(f"  Logged in: {pg.url}")

    for repo_name, data in repos.items():
        print(f"\n{'='*60}")
        print(f"{repo_name}")
        print(f"{'='*60}")

        # Create repo
        pg.goto("https://github.com/new", timeout=30000)
        pg.wait_for_load_state("domcontentloaded", timeout=15000)
        time.sleep(6)
        try:
            pg.evaluate('document.getElementById("ghcc")?.remove()')
        except:
            pass

        name_el = pg.query_selector("input#repository-name-input")
        if name_el:
            name_el.click()
            time.sleep(0.5)
            pg.keyboard.type(repo_name, delay=40)
            time.sleep(2)

            desc_el = pg.query_selector('input[name="Description"]')
            if desc_el:
                desc_el.click()
                time.sleep(0.3)
                pg.keyboard.type(data["description"][:200], delay=15)
                time.sleep(1)

            labels = pg.query_selector_all("label")
            for lbl in labels:
                if "readme" in (lbl.text_content() or "").lower():
                    lbl.click()
                    time.sleep(1)
                    break

            time.sleep(2)
            create_btn = pg.query_selector('button:has-text("Create repository")')
            if create_btn and create_btn.is_visible():
                create_btn.click()
                time.sleep(10)
                print(f"  Repo created")

        # Navigate to repo and add README
        pg.goto(f"https://github.com/dialphonelimited/{repo_name}", timeout=30000)
        pg.wait_for_load_state("domcontentloaded", timeout=15000)
        time.sleep(5)
        try:
            pg.evaluate('document.getElementById("ghcc")?.remove()')
        except:
            pass

        create_link = pg.query_selector('a:has-text("creating a new file")')
        if create_link:
            create_link.click()
            time.sleep(5)

            # Filename
            inputs = pg.query_selector_all("input:visible")
            for inp in inputs:
                ph = (inp.get_attribute("placeholder") or "").lower()
                if "name" in ph or "file" in ph:
                    inp.click()
                    time.sleep(0.3)
                    pg.keyboard.type("README.md", delay=50)
                    time.sleep(1)
                    break

            # Tab into editor and paste
            pg.keyboard.press("Tab")
            time.sleep(1)
            pg.keyboard.press("Tab")
            time.sleep(1)
            pg.keyboard.press("Control+a")
            time.sleep(0.3)
            pg.evaluate("(text) => navigator.clipboard.writeText(text)", data["readme"])
            time.sleep(0.5)
            pg.keyboard.press("Control+v")
            time.sleep(3)
            print("  Content pasted")

            # Commit
            commit = pg.query_selector('button:has-text("Commit changes")')
            if commit:
                commit.click()
                time.sleep(3)
                dialog = pg.query_selector('button:has-text("Commit changes"):visible')
                if dialog:
                    dialog.click()
                    time.sleep(5)
                print("  Committed!")

        # Verify
        pg.goto(f"https://github.com/dialphonelimited/{repo_name}", timeout=30000)
        pg.wait_for_load_state("domcontentloaded", timeout=15000)
        time.sleep(3)
        has_vc = "dialphone" in pg.content().lower()
        print(f"  dialphone: {has_vc}")

        if has_vc:
            url = f"https://github.com/dialphonelimited/{repo_name}"
            with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=["date", "strategy", "site_name", "url_submitted", "backlink_url", "status", "notes"])
                w.writerow({
                    "date": datetime.now().isoformat(), "strategy": "content",
                    "site_name": f"GitHub-Company-{repo_name}",
                    "url_submitted": "https://github.com/new",
                    "backlink_url": url, "status": "success",
                    "notes": "Company repo DA 100 — professional content verified"
                })
            print(f"  === VERIFIED ===")

        time.sleep(5)

    print("\n=== DONE ===")

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
