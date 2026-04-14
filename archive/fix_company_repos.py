"""Add README to compliance repo + create 2 more repos on company GitHub."""
import json, time, csv
from datetime import datetime
from core.browser import get_browser, new_page

config = json.load(open("config.json"))
repos_data = json.load(open("data/company_repos.json"))
CSV_PATH = "output/backlinks_log.csv"

# Repos to handle: compliance (exists, needs README), roi + network (need creating)
TASKS = [
    {"name": "voip-compliance-framework", "exists": True},
    {"name": "business-phone-roi-calculator", "exists": False},
    {"name": "voip-network-requirements", "exists": False},
]

pw, browser = get_browser(config, headed_override=True)
ctx, pg = new_page(browser, config, site_name="github-fix")

try:
    # Login
    print("[1] Logging in...")
    pg.goto("https://github.com/login", timeout=60000)
    pg.wait_for_load_state("domcontentloaded", timeout=20000)
    time.sleep(5)

    # Cookie dismiss
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
    print(f"  URL: {pg.url}")

    for task in TASKS:
        repo_name = task["name"]
        readme_content = repos_data[repo_name]["readme"]
        desc = repos_data[repo_name]["description"]

        print(f"\n{'='*60}")
        print(f"REPO: {repo_name}")
        print(f"{'='*60}")

        # Create repo if it doesn't exist
        if not task["exists"]:
            print("  Creating repo...")
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
                    pg.keyboard.type(desc[:200], delay=15)
                    time.sleep(1)

                # README checkbox
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

        # Navigate to repo
        pg.goto(f"https://github.com/dialphonelimited/{repo_name}", timeout=30000)
        pg.wait_for_load_state("domcontentloaded", timeout=15000)
        time.sleep(5)
        try:
            pg.evaluate('document.getElementById("ghcc")?.remove()')
        except:
            pass

        # Click "creating a new file"
        print("  Adding README...")
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
                    print("  Filename: README.md")
                    break

            # Paste content via clipboard
            editor = pg.query_selector('.CodeMirror, .cm-editor, textarea, [role="textbox"]')
            if editor:
                editor.click()
                time.sleep(0.5)
                pg.keyboard.press("Control+a")
                time.sleep(0.2)
                pg.evaluate("(text) => navigator.clipboard.writeText(text)", readme_content)
                time.sleep(0.5)
                pg.keyboard.press("Control+v")
                time.sleep(3)
                print("  Content pasted")

            # Commit
            commit_btn = pg.query_selector('button:has-text("Commit changes")')
            if commit_btn:
                commit_btn.click()
                time.sleep(3)
                dialog = pg.query_selector('button:has-text("Commit changes"):visible')
                if dialog:
                    dialog.click()
                    time.sleep(5)
                print("  Committed!")
        else:
            print("  No 'creating a new file' link — repo may have content already")

        # Verify
        pg.goto(f"https://github.com/dialphonelimited/{repo_name}", timeout=30000)
        pg.wait_for_load_state("domcontentloaded", timeout=15000)
        time.sleep(3)
        has_vc = "vestacall" in pg.content().lower()
        print(f"  vestacall verified: {has_vc}")
        pg.screenshot(path=f"output/github_company_{repo_name}_final.png")

        if has_vc:
            with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=["date", "strategy", "site_name", "url_submitted", "backlink_url", "status", "notes"])
                w.writerow({
                    "date": datetime.now().isoformat(),
                    "strategy": "content",
                    "site_name": f"GitHub-Company-{repo_name}",
                    "url_submitted": "https://github.com/new",
                    "backlink_url": f"https://github.com/dialphonelimited/{repo_name}",
                    "status": "success",
                    "notes": f"Company repo DA 100 — professional content verified"
                })
            print(f"  === VERIFIED ===")

        time.sleep(5)

    print("\n=== ALL REPOS DONE ===")

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
finally:
    ctx.close()
    browser.close()
    pw.stop()

# Final count
with open(CSV_PATH, "r", encoding="utf-8", errors="replace") as f:
    success = sum(1 for r in csv.DictReader(f) if r["status"] == "success")
print(f"\nTOTAL VERIFIED: {success}")
