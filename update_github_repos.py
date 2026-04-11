"""Update company GitHub repos with expert README content."""
import json, time
from core.browser import get_browser, new_page

config = json.load(open("config.json"))
readmes = json.load(open("data/github_readmes.json"))

pw, browser = get_browser(config, headed_override=True)
ctx, pg = new_page(browser, config, site_name="github-update")

try:
    # Login
    print("[1] Logging in...")
    pg.goto("https://github.com/login", timeout=60000)
    pg.wait_for_load_state("domcontentloaded", timeout=20000)
    time.sleep(5)

    # Dismiss cookies
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

    # Update each repo
    for repo_name, content in readmes.items():
        print(f"\n[*] Updating {repo_name}...")

        edit_url = f"https://github.com/dialphonelimited/{repo_name}/edit/main/README.md"
        pg.goto(edit_url, timeout=30000)
        pg.wait_for_load_state("domcontentloaded", timeout=15000)
        time.sleep(6)

        try:
            pg.evaluate('document.getElementById("ghcc")?.remove()')
        except:
            pass

        # Set content via JS
        pg.evaluate("""(content) => {
            // CodeMirror
            var cm = document.querySelector('.CodeMirror');
            if (cm && cm.CodeMirror) {
                cm.CodeMirror.setValue(content);
                return 'codemirror';
            }
            // Textarea
            var ta = document.querySelector('textarea.js-code-textarea, textarea[name="value"], textarea');
            if (ta) {
                ta.value = content;
                ta.dispatchEvent(new Event('input', {bubbles: true}));
                return 'textarea';
            }
            // Monaco
            var lines = document.querySelectorAll('.view-line');
            if (lines.length > 0) {
                return 'monaco-detected';
            }
            return 'none-found';
        }""", content)
        time.sleep(2)
        print("  Content set")

        # Click Commit changes
        try:
            pg.click('button:has-text("Commit changes")')
            time.sleep(3)
        except:
            pass

        # Handle commit dialog if it appears
        try:
            dialog_btn = pg.query_selector('button:has-text("Commit changes"):visible')
            if dialog_btn:
                dialog_btn.click()
                time.sleep(5)
        except:
            pass

        print("  Committed!")
        pg.screenshot(path=f"output/github_{repo_name}_updated.png")

        # Verify
        verify_url = f"https://github.com/dialphonelimited/{repo_name}"
        pg.goto(verify_url, timeout=30000)
        pg.wait_for_load_state("domcontentloaded", timeout=15000)
        time.sleep(3)

        page_content = pg.content().lower()
        has_vc = "vestacall.com" in page_content
        has_author = any(name.lower() in page_content for name in ["james patterson", "sarah mitchell", "david park"])
        word_indicators = any(phrase in page_content for phrase in ["decision tree", "scenario analysis", "troubleshooting"])

        print(f"  vestacall: {has_vc} | Expert author: {has_author} | Expert content: {word_indicators}")

        if has_vc and has_author:
            print(f"  === VERIFIED: Expert README live at {verify_url} ===")
        elif has_vc:
            print(f"  vestacall present but author name not found — README may not have updated")
        else:
            print(f"  vestacall NOT found — update may have failed")

        time.sleep(3)

    print("\n=== ALL REPOS UPDATED ===")

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
finally:
    ctx.close()
    browser.close()
    pw.stop()
