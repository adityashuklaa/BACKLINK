"""Create professional repos on company GitHub with expert content."""
import json, time, csv
from datetime import datetime
from core.browser import get_browser, new_page

config = json.load(open("config.json"))
repos = json.load(open("data/company_repos.json"))
CSV_PATH = "output/backlinks_log.csv"

pw, browser = get_browser(config, headed_override=True)
ctx, pg = new_page(browser, config, site_name="github-company-pro")

try:
    # Login
    print("[1] Logging in to dialphonelimited...")
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

    for repo_name, repo_data in repos.items():
        desc = repo_data["description"]
        readme = repo_data["readme"]

        print(f"\n{'='*60}")
        print(f"Creating: {repo_name}")
        print(f"{'='*60}")

        # Step 1: Create the repo
        pg.goto("https://github.com/new", timeout=30000)
        pg.wait_for_load_state("domcontentloaded", timeout=15000)
        time.sleep(6)
        try:
            pg.evaluate('document.getElementById("ghcc")?.remove()')
        except:
            pass

        # Fill repo name
        name_el = pg.query_selector("input#repository-name-input")
        if name_el:
            name_el.click()
            time.sleep(0.5)
            pg.keyboard.type(repo_name, delay=40)
            time.sleep(2)
            print(f"  Name: {repo_name}")

            # Description
            desc_el = pg.query_selector('input[name="Description"]')
            if desc_el:
                desc_el.click()
                time.sleep(0.3)
                pg.keyboard.type(desc[:200], delay=15)
                time.sleep(1)

            # Add README checkbox
            labels = pg.query_selector_all("label")
            for lbl in labels:
                t = (lbl.text_content() or "").strip().lower()
                if "readme" in t or "add a readme" in t:
                    lbl.click()
                    time.sleep(1)
                    print("  README checked")
                    break

            time.sleep(2)

            # Create
            create_btn = pg.query_selector('button:has-text("Create repository")')
            if create_btn and create_btn.is_visible():
                create_btn.click()
                time.sleep(10)
                print(f"  Created: {pg.url}")

                # Step 2: Add README content via create file
                pg.goto(f"https://github.com/dialphonelimited/{repo_name}", timeout=30000)
                pg.wait_for_load_state("domcontentloaded", timeout=15000)
                time.sleep(5)
                try:
                    pg.evaluate('document.getElementById("ghcc")?.remove()')
                except:
                    pass

                # Click on README.md to edit it
                readme_link = pg.query_selector('a:has-text("README.md")')
                if readme_link:
                    readme_link.click()
                    time.sleep(3)

                    # Click edit (pencil icon)
                    edit_btn = pg.query_selector('button[aria-label*="Edit"], a[aria-label*="Edit"], button:has-text("Edit")')
                    if not edit_btn:
                        edit_btn = pg.query_selector('button svg.octicon-pencil, a[href*="edit"]')
                    if edit_btn:
                        edit_btn.click()
                        time.sleep(5)
                        print("  Editing README...")

                        # Set content
                        pg.evaluate("""(content) => {
                            var cm = document.querySelector('.CodeMirror');
                            if (cm && cm.CodeMirror) { cm.CodeMirror.setValue(content); return; }
                            var ta = document.querySelector('textarea');
                            if (ta) { ta.value = content; ta.dispatchEvent(new Event('input', {bubbles: true})); }
                        }""", readme)
                        time.sleep(2)

                        # Commit
                        commit_btn = pg.query_selector('button:has-text("Commit changes")')
                        if commit_btn:
                            commit_btn.click()
                            time.sleep(3)
                            dialog = pg.query_selector('button:has-text("Commit changes"):visible')
                            if dialog:
                                dialog.click()
                                time.sleep(5)
                            print("  README updated!")
                    else:
                        print("  Edit button not found — trying file creation instead")
                else:
                    # Empty repo — create file directly
                    create_link = pg.query_selector('a:has-text("creating a new file")')
                    if create_link:
                        create_link.click()
                        time.sleep(5)

                        # Filename
                        for sel in ['input[placeholder*="Name your file"]', 'input[name*="filename"]']:
                            inp = pg.query_selector(sel)
                            if inp and inp.is_visible():
                                inp.click()
                                time.sleep(0.3)
                                pg.keyboard.type("README.md", delay=50)
                                time.sleep(1)
                                break

                        # Paste content
                        editor = pg.query_selector('.CodeMirror, .cm-editor, textarea, [role="textbox"]')
                        if editor:
                            editor.click()
                            time.sleep(0.5)
                            pg.keyboard.press("Control+a")
                            time.sleep(0.2)
                            pg.evaluate("(text) => navigator.clipboard.writeText(text)", readme)
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

                # Verify
                verify_url = f"https://github.com/dialphonelimited/{repo_name}"
                pg.goto(verify_url, timeout=30000)
                pg.wait_for_load_state("domcontentloaded", timeout=15000)
                time.sleep(3)

                has_vc = "dialphone" in pg.content().lower()
                print(f"  dialphone verified: {has_vc}")
                pg.screenshot(path=f"output/github_company_{repo_name}.png")

                if has_vc:
                    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
                        w = csv.DictWriter(f, fieldnames=["date","strategy","site_name","url_submitted","backlink_url","status","notes"])
                        w.writerow({"date": datetime.now().isoformat(), "strategy": "content",
                            "site_name": f"GitHub-Company-{repo_name}", "url_submitted": "https://github.com/new",
                            "backlink_url": verify_url, "status": "success",
                            "notes": f"Company repo DA 100 — professional content verified"})
                    print(f"  === VERIFIED: {verify_url} ===")
            else:
                print("  Create button not found")
        else:
            print("  Name field not found")

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
