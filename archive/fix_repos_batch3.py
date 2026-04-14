"""Fix batch 3 repos — push README content via GitHub web editor."""
import json, time, csv
from datetime import datetime
from core.browser import get_browser, new_page

config = json.load(open("config.json"))
repos = json.load(open("data/company_repos_batch3.json"))
CSV_PATH = "output/backlinks_log.csv"

pw, browser = get_browser(config, headed_override=True)
ctx, pg = new_page(browser, config, site_name="github-fix-batch3")

try:
    # Login
    print("[1] Logging in...")
    pg.goto("https://github.com/login", timeout=60000)
    pg.wait_for_load_state("domcontentloaded", timeout=20000)
    time.sleep(5)
    try: pg.evaluate('document.getElementById("ghcc")?.remove()')
    except: pass

    pg.fill("input#login_field", "dialphonelimited")
    time.sleep(0.5)
    pg.fill("input#password", "DevD!alph0ne@0912@#")
    time.sleep(0.5)
    pg.click("input[type=submit]")
    time.sleep(10)
    print(f"  Logged in: {pg.url}")

    for repo_name, data in repos.items():
        print(f"\n{'='*60}")
        print(f"  {repo_name}")
        print(f"{'='*60}")

        # Navigate to edit README
        edit_url = f"https://github.com/dialphonelimited/{repo_name}/edit/main/README.md"
        pg.goto(edit_url, timeout=30000)
        pg.wait_for_load_state("domcontentloaded", timeout=15000)
        time.sleep(5)
        try: pg.evaluate('document.getElementById("ghcc")?.remove()')
        except: pass

        # Clear and set content via CodeMirror
        content_set = pg.evaluate("""(text) => {
            // Try CodeMirror
            const cm = document.querySelector('.CodeMirror');
            if (cm && cm.CodeMirror) {
                cm.CodeMirror.setValue(text);
                return 'codemirror';
            }
            // Try Monaco
            const monaco = window.monaco;
            if (monaco) {
                const editors = monaco.editor.getEditors();
                if (editors.length > 0) {
                    editors[0].setValue(text);
                    return 'monaco';
                }
            }
            // Try textarea
            const ta = document.querySelector('textarea[name="value"], textarea.file-editor-textarea');
            if (ta) {
                ta.value = text;
                ta.dispatchEvent(new Event('input', {bubbles: true}));
                return 'textarea';
            }
            return false;
        }""", data["readme"])
        print(f"  Content set via: {content_set}")

        if not content_set:
            # Fallback: click into editor and paste
            print("  Trying clipboard paste...")
            editor_area = pg.query_selector('.CodeMirror-code, .CodeMirror-lines, [role="textbox"]')
            if editor_area:
                editor_area.click()
                time.sleep(0.5)
            else:
                pg.keyboard.press("Tab")
                time.sleep(0.5)

            pg.keyboard.press("Control+a")
            time.sleep(0.3)
            pg.evaluate("(t) => navigator.clipboard.writeText(t)", data["readme"])
            time.sleep(0.5)
            pg.keyboard.press("Control+v")
            time.sleep(3)
            print("  Content pasted via clipboard")

        time.sleep(2)

        # Commit changes
        commit_btn = pg.query_selector('button:has-text("Commit changes")')
        if commit_btn:
            commit_btn.click()
            time.sleep(3)
            # Confirm dialog
            confirm = pg.query_selector('button:has-text("Commit changes"):visible')
            if confirm:
                confirm.click()
                time.sleep(8)
            print("  Committed!")

        # Verify
        time.sleep(3)
        pg.goto(f"https://github.com/dialphonelimited/{repo_name}", timeout=30000)
        pg.wait_for_load_state("domcontentloaded", timeout=15000)
        time.sleep(3)

        has_vc = "vestacall" in pg.content().lower()
        print(f"  vestacall: {has_vc}")

        if has_vc:
            url = f"https://github.com/dialphonelimited/{repo_name}"
            with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=["date","strategy","site_name","url_submitted","backlink_url","status","notes"])
                w.writerow({
                    "date": datetime.now().isoformat(), "strategy": "dofollow-content",
                    "site_name": f"GitHub-{repo_name}",
                    "url_submitted": "https://github.com/new",
                    "backlink_url": url, "status": "success",
                    "notes": "DA 100 dofollow — professional README verified"
                })
            print(f"  === VERIFIED ===")

        time.sleep(3)

    print("\n=== DONE ===")

except Exception as e:
    print(f"ERROR: {str(e).encode('ascii','replace').decode()}")
finally:
    ctx.close()
    browser.close()
    pw.stop()
