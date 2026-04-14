"""Publish repos on GitLab (DA 92) — login via Playwright, create repos with README content."""
import json
import time
import csv
from datetime import datetime
from core.browser import get_browser, new_page

config = json.load(open("config.json"))
CSV_PATH = "output/backlinks_log.csv"

GL_USER = "commercial@dialphone.com"
GL_PASS = "6b@YcNDm!Aw"

# Load all repo content
repos = {}
for path in ["data/company_repos.json", "data/company_repos_batch2.json", "data/company_repos_batch3.json"]:
    try:
        repos.update(json.load(open(path, encoding="utf-8")))
    except:
        pass

print(f"Loaded {len(repos)} repos to publish on GitLab")
print("=" * 60)

pw, browser = get_browser(config, headed_override=True)
ctx, pg = new_page(browser, config, site_name="gitlab-publish")

try:
    # Login
    print("[1] Logging in to GitLab...")
    pg.goto("https://gitlab.com/users/sign_in", timeout=60000)
    pg.wait_for_load_state("domcontentloaded", timeout=20000)
    time.sleep(5)

    # Dismiss cookies
    for sel in ['button:has-text("Accept")', 'button:has-text("Reject")', 'button[id*="cookie" i]',
                'button:has-text("OK")', 'button:has-text("Got it")']:
        try:
            b = pg.query_selector(sel)
            if b and b.is_visible():
                b.click()
                time.sleep(2)
                break
        except:
            pass

    # Fill login
    login_input = pg.query_selector('input#user_login, input[name="user[login]"]')
    if login_input:
        login_input.fill(GL_USER)
        time.sleep(0.5)

    pw_input = pg.query_selector('input#user_password, input[name="user[password]"]')
    if pw_input:
        pw_input.fill(GL_PASS)
        time.sleep(0.5)

    submit = pg.query_selector('button[type="submit"], input[type="submit"]')
    if submit:
        submit.click()
        time.sleep(10)

    print(f"  After login: {pg.url}")
    pg.screenshot(path="output/gitlab_login_result.png")

    if "sign_in" in pg.url:
        print("  Login failed — check credentials or 2FA")
        # Try to see error message
        error = pg.query_selector('.flash-alert, .alert-danger, [data-testid="alert"]')
        if error:
            print(f"  Error: {error.text_content()[:100]}")
        ctx.close()
        browser.close()
        pw.stop()
        exit(1)

    print("  Login successful!")

    # Get username from profile
    pg.goto("https://gitlab.com/-/user_settings/profile", timeout=30000)
    time.sleep(5)
    username_input = pg.query_selector('input#user_username, input[name="user[username]"]')
    gl_username = username_input.get_attribute("value") if username_input else "unknown"
    print(f"  GitLab username: {gl_username}")

    verified = 0

    for repo_name, data in repos.items():
        print(f"\n{'='*60}")
        print(f"  {repo_name}")
        print(f"{'='*60}")

        # Check if repo already exists
        pg.goto(f"https://gitlab.com/{gl_username}/{repo_name}", timeout=15000)
        time.sleep(3)
        if pg.url == f"https://gitlab.com/{gl_username}/{repo_name}" and "404" not in pg.content():
            if "vestacall" in pg.content().lower():
                print(f"  Already exists with vestacall — skipping")
                continue
            else:
                print(f"  Exists but no vestacall — will update README")

        # Create new project
        pg.goto("https://gitlab.com/projects/new#blank_project", timeout=30000)
        pg.wait_for_load_state("domcontentloaded", timeout=15000)
        time.sleep(5)

        # Dismiss any popups
        for sel in ['button:has-text("Accept")', 'button:has-text("OK")', 'button:has-text("Got it")']:
            try:
                b = pg.query_selector(sel)
                if b and b.is_visible(): b.click(); time.sleep(1); break
            except: pass

        # Project name
        name_input = pg.query_selector('input#project_name, input[data-testid="project-name-field"]')
        if name_input:
            name_input.click()
            time.sleep(0.3)
            name_input.fill(repo_name)
            time.sleep(2)
            print(f"  Name: {repo_name}")

        # Wait for slug to auto-fill
        time.sleep(2)

        # Description
        desc_input = pg.query_selector('textarea#project_description, textarea[data-testid="project-description"]')
        if desc_input:
            desc_input.fill(data["description"][:200])
            time.sleep(1)

        # Set to public visibility
        public_radio = pg.query_selector('input#project_visibility_level_20, input[value="20"]')
        if not public_radio:
            # Try clicking the public option label
            public_label = pg.query_selector('label:has-text("Public")')
            if public_label:
                public_label.click()
                time.sleep(1)
        else:
            try:
                public_radio.click()
                time.sleep(1)
            except:
                pg.evaluate("""() => {
                    const radio = document.querySelector('input[value="20"]');
                    if (radio) { radio.checked = true; radio.dispatchEvent(new Event('change')); }
                }""")
                time.sleep(1)

        # Initialize with README
        readme_check = pg.query_selector('input#project_initialize_with_readme')
        if readme_check:
            if not readme_check.is_checked():
                try:
                    readme_check.click()
                except:
                    pg.evaluate("""() => {
                        const cb = document.querySelector('#project_initialize_with_readme');
                        if (cb) { cb.checked = true; cb.dispatchEvent(new Event('change')); }
                    }""")
            time.sleep(1)

        # Create project
        create_btn = pg.query_selector('button:has-text("Create project"), input[value="Create project"]')
        if create_btn:
            create_btn.click()
            time.sleep(10)
            print(f"  Repo created: {pg.url}")
        else:
            # Try submit form
            pg.evaluate("""() => {
                const form = document.querySelector('form#new_project, form[action*="projects"]');
                if (form) form.submit();
            }""")
            time.sleep(10)
            print(f"  Repo submitted: {pg.url}")

        pg.screenshot(path=f"output/gitlab_{repo_name}.png")

        # Now edit the README with our content
        time.sleep(3)

        # Navigate to edit README
        edit_url = f"https://gitlab.com/{gl_username}/{repo_name}/-/edit/main/README.md"
        pg.goto(edit_url, timeout=30000)
        pg.wait_for_load_state("domcontentloaded", timeout=15000)
        time.sleep(5)

        # Try to paste content
        # GitLab uses Monaco editor or simple textarea
        pg.evaluate("(text) => navigator.clipboard.writeText(text)", data["readme"])
        time.sleep(0.5)

        # Try clicking into the editor
        editor = pg.query_selector('.monaco-editor, .CodeMirror, [role="textbox"], textarea')
        if editor:
            editor.click()
            time.sleep(0.5)
        else:
            pg.keyboard.press("Tab")
            time.sleep(0.5)

        pg.keyboard.press("Control+a")
        time.sleep(0.3)
        pg.keyboard.press("Control+v")
        time.sleep(3)
        print(f"  README content pasted")

        # Commit
        commit_btn = pg.query_selector('button:has-text("Commit changes")')
        if commit_btn:
            commit_btn.click()
            time.sleep(3)
            # Confirm dialog if it appears
            confirm = pg.query_selector('button:has-text("Commit changes"):visible')
            if confirm and confirm != commit_btn:
                confirm.click()
                time.sleep(5)
            print(f"  Committed")

        # Verify
        time.sleep(3)
        repo_url = f"https://gitlab.com/{gl_username}/{repo_name}"
        pg.goto(repo_url, timeout=30000)
        pg.wait_for_load_state("domcontentloaded", timeout=15000)
        time.sleep(3)

        has_vc = "vestacall" in pg.content().lower()
        print(f"  vestacall: {has_vc}")

        if has_vc:
            with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=["date","strategy","site_name","url_submitted","backlink_url","status","notes"])
                w.writerow({
                    "date": datetime.now().isoformat(), "strategy": "dofollow-content",
                    "site_name": f"GitLab-{repo_name}",
                    "url_submitted": "https://gitlab.com/projects/new",
                    "backlink_url": repo_url, "status": "success",
                    "notes": "DA 92 dofollow — README with vestacall.com verified"
                })
            verified += 1
            print(f"  === VERIFIED (DA 92 DOFOLLOW) ===")
        else:
            # Check if README was actually saved
            raw_url = f"https://gitlab.com/{gl_username}/{repo_name}/-/raw/main/README.md"
            try:
                raw = pg.evaluate(f"() => fetch('{raw_url}').then(r => r.text())")
                if raw and "vestacall" in raw.lower():
                    print(f"  vestacall found in raw README")
                    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
                        w = csv.DictWriter(f, fieldnames=["date","strategy","site_name","url_submitted","backlink_url","status","notes"])
                        w.writerow({
                            "date": datetime.now().isoformat(), "strategy": "dofollow-content",
                            "site_name": f"GitLab-{repo_name}",
                            "url_submitted": "https://gitlab.com/projects/new",
                            "backlink_url": repo_url, "status": "success",
                            "notes": "DA 92 dofollow — verified in raw README"
                        })
                    verified += 1
                    print(f"  === VERIFIED (DA 92 DOFOLLOW) ===")
                else:
                    print(f"  Content not saved — README may be empty")
            except:
                print(f"  Could not check raw README")

        time.sleep(3)

    print(f"\n{'='*60}")
    print(f"GITLAB: {verified}/{len(repos)} verified")
    print(f"{'='*60}")

except Exception as e:
    print(f"ERROR: {str(e).encode('ascii','replace').decode()}")
    import traceback
    try: traceback.print_exc()
    except: pass
finally:
    ctx.close()
    browser.close()
    pw.stop()
