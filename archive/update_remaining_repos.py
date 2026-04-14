"""Update remaining 2 company GitHub repos with expert READMEs."""
import json, time
from core.browser import get_browser, new_page

config = json.load(open("config.json"))
readmes = json.load(open("data/github_readmes.json"))

pw, browser = get_browser(config, headed_override=True)
ctx, pg = new_page(browser, config, site_name="github-remaining")

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

    repos_to_update = ["awesome-business-phone", "sip-trunking-guide"]

    for repo in repos_to_update:
        content = readmes[repo]
        print(f"\n[*] Updating {repo}...")

        pg.goto(f"https://github.com/dialphonelimited/{repo}", timeout=30000)
        pg.wait_for_load_state("domcontentloaded", timeout=15000)
        time.sleep(5)
        try:
            pg.evaluate('document.getElementById("ghcc")?.remove()')
        except:
            pass

        # Click create file link
        create_link = pg.query_selector('a:has-text("creating a new file")')
        if not create_link:
            create_link = pg.query_selector('a:has-text("Create new file")')
        if not create_link:
            # Try Add file button
            add_btn = pg.query_selector('button:has-text("Add file")')
            if add_btn:
                add_btn.click()
                time.sleep(2)
                create_link = pg.query_selector('a:has-text("Create new file")')

        if create_link:
            create_link.click()
            time.sleep(5)
            print("  On create file page")

            # Check for dropdown "Create new file" option
            new_file = pg.query_selector('a:has-text("Create new file"):visible')
            if new_file and new_file != create_link:
                new_file.click()
                time.sleep(5)

            # Fill filename
            name_filled = False
            for sel in ['input[placeholder*="Name your file"]', 'input[name*="filename"]', 'input#file-name-id']:
                try:
                    inp = pg.query_selector(sel)
                    if inp and inp.is_visible():
                        inp.click()
                        time.sleep(0.3)
                        pg.keyboard.type("README.md", delay=50)
                        time.sleep(1)
                        name_filled = True
                        print("  Filename: README.md")
                        break
                except:
                    pass

            if not name_filled:
                inputs = pg.query_selector_all("input:visible")
                for inp in inputs:
                    ph = (inp.get_attribute("placeholder") or "").lower()
                    if "name" in ph or "file" in ph:
                        inp.click()
                        time.sleep(0.3)
                        pg.keyboard.type("README.md", delay=50)
                        time.sleep(1)
                        name_filled = True
                        print("  Filename set via fallback")
                        break

            if name_filled:
                # Click editor and paste content
                editor = pg.query_selector('.CodeMirror, .cm-editor, textarea.js-code-textarea, [role="textbox"]')
                if editor:
                    editor.click()
                    time.sleep(0.5)
                    pg.keyboard.press("Control+a")
                    time.sleep(0.2)
                    pg.evaluate("(text) => navigator.clipboard.writeText(text)", content)
                    time.sleep(0.5)
                    pg.keyboard.press("Control+v")
                    time.sleep(3)
                    print("  Content pasted")
                else:
                    ta = pg.query_selector("textarea")
                    if ta:
                        ta.fill(content)
                        time.sleep(2)
                        print("  Content filled via textarea")

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
                pg.goto(f"https://github.com/dialphonelimited/{repo}", timeout=30000)
                pg.wait_for_load_state("domcontentloaded", timeout=15000)
                time.sleep(3)
                has_vc = "vestacall" in pg.content().lower()
                authors = {"awesome-business-phone": "sarah mitchell", "sip-trunking-guide": "david park"}
                has_author = authors.get(repo, "") in pg.content().lower()
                print(f"  vestacall: {has_vc} | Author: {has_author}")
                pg.screenshot(path=f"output/github_{repo}_final.png")

                if has_vc and has_author:
                    print(f"  === VERIFIED: Expert README live ===")
            else:
                print("  Could not find filename input")
        else:
            print("  No create file link found")

    print("\n=== ALL REPOS DONE ===")

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
finally:
    ctx.close()
    browser.close()
    pw.stop()
