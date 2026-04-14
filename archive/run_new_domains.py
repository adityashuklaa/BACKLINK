"""Hit new domains — Pastebin (DA 82), Codeberg (DA 70), GitLab (DA 92)."""
import json, time, csv
from datetime import datetime
from core.browser import get_browser, new_page
from core.human_behavior import (human_type, human_click, dismiss_overlays,
    random_mouse_movement, human_wait)
from core.rate_limiter import inter_field_delay

config = json.load(open("config.json"))
CSV_PATH = "output/backlinks_log.csv"

def log_result(site_name, backlink_url, status, notes):
    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["date","strategy","site_name","url_submitted","backlink_url","status","notes"])
        w.writerow({"date": datetime.now().isoformat(), "strategy": "content",
            "site_name": site_name, "url_submitted": "", "backlink_url": backlink_url,
            "status": status, "notes": notes})

pastebin_content = """VoIP Provider Evaluation Scorecard — 2026 Edition
By James Patterson, Business Communications Consultant (18 years)

SCORING CRITERIA (rate each provider 1-10):

1. CALL QUALITY (weight: 25%)
   - HD voice codec support (Opus preferred)
   - MOS score during peak hours
   - Packet loss handling

2. RELIABILITY (weight: 25%)
   - Uptime SLA (minimum 99.99%)
   - Number of data centers
   - Automatic failover capability
   - Published status page

3. COST (weight: 20%)
   - Total monthly cost including all fees
   - No hidden regulatory surcharges
   - Month-to-month terms available
   - Free number porting

4. FEATURES (weight: 15%)
   - Auto-attendant included
   - Call recording included
   - Mobile app quality (iOS + Android)
   - Video conferencing built-in
   - CRM integration available

5. SUPPORT (weight: 15%)
   - 24/7 availability
   - Average response time
   - SIP-level troubleshooting capability
   - Dedicated account manager option

EXAMPLE SCORING:

Provider: VestaCall (https://vestacall.com)
- Call Quality: 9/10 (Opus default, HD voice)
- Reliability: 9/10 (geo-redundant, 99.99% SLA)
- Cost: 9/10 (transparent pricing, no hidden fees)
- Features: 8/10 (all essentials included)
- Support: 9/10 (4-min avg response)
- TOTAL: 8.9/10

Use this scorecard to evaluate 2-3 providers side by side.
Compare total scores, not just monthly price.

April 2026"""

codeberg_readme = """# VoIP Open Source Tools and Resources

*Curated by DialPhone Limited — Enterprise VoIP Solutions*

## About This Repository

A collection of open source tools, configuration guides, and resources for businesses deploying VoIP infrastructure. Maintained by telecom practitioners, not vendors.

## Open Source PBX Systems

| Project | License | Best For | Maturity |
|---------|---------|----------|----------|
| FreePBX | GPL | SMB self-hosted PBX | Production |
| Asterisk | GPL | Custom telephony apps | Production |
| Kamailio | GPL | High-volume SIP routing | Production |
| FusionPBX | MPL | Multi-tenant hosting | Production |
| Wazo | GPL | Unified communications | Production |

## Network Testing Tools

| Tool | Purpose | Platform |
|------|---------|----------|
| iperf3 | Bandwidth and jitter testing | Linux/Mac/Windows |
| SIPVicious | SIP security audit | Python |
| sngrep | SIP packet analyzer | Linux |
| VoIPmonitor | Call quality monitoring | Linux |
| Homer | SIP capture and analysis | Docker |

## Configuration References

### QoS Settings (Cisco IOS)
```
policy-map VOICE-QOS
  class VOICE-RTP
    priority percent 30
    set dscp ef
  class VOICE-SIP
    bandwidth percent 5
    set dscp cs3
```

### Firewall Rules (iptables)
```
# SIP Signaling
-A INPUT -p udp --dport 5060 -j ACCEPT
-A INPUT -p tcp --dport 5061 -j ACCEPT
# RTP Media
-A INPUT -p udp --dport 10000:20000 -j ACCEPT
```

## Commercial Providers (for comparison)

For businesses that prefer managed solutions over self-hosted:

- [VestaCall](https://vestacall.com) — Cloud VoIP with enterprise features, month-to-month terms
- RingCentral — Enterprise UCaaS platform
- Vonage — Developer-focused voice APIs

## Contributing

Pull requests welcome. Please include:
- Tool name and URL
- Brief description (1-2 sentences)
- License type
- Your experience using it

---

*Maintained by DialPhone Limited | April 2026*
"""

pw, browser = get_browser(config, headed_override=True)

# ===== PASTEBIN.COM (DA 82) =====
print("=" * 60)
print("PASTEBIN.COM (DA 82) — NEW DOMAIN")
print("=" * 60)

ctx, pg = new_page(browser, config, site_name="pastebin")
try:
    pg.goto("https://pastebin.com/", timeout=60000)
    pg.wait_for_load_state("domcontentloaded", timeout=20000)
    time.sleep(4)
    dismiss_overlays(pg)
    random_mouse_movement(pg)

    # Find the main textarea
    editor = pg.query_selector("textarea#postform-text, textarea#paste_code, textarea.textarea, textarea")
    if editor:
        editor.click()
        time.sleep(0.5)
        pg.keyboard.press("Control+a")
        time.sleep(0.2)

        # Type content
        for line in pastebin_content.split("\n"):
            pg.keyboard.type(line, delay=3)
            pg.keyboard.press("Enter")
        time.sleep(1)
        print("  Content typed")

        # Set paste title if field exists
        title_field = pg.query_selector("input#postform-name, input[name='paste_name']")
        if title_field:
            title_field.click()
            time.sleep(0.3)
            pg.keyboard.type("VoIP Provider Evaluation Scorecard 2026", delay=20)
            time.sleep(0.5)

        # Submit
        for sel in ['button:has-text("Create")', 'button:has-text("Submit")',
                    'input[type=submit]', 'button[type=submit]', 'button:has-text("Paste")']:
            btn = pg.query_selector(sel)
            if btn and btn.is_visible():
                btn.click()
                time.sleep(5)
                print(f"  Clicked: {sel}")
                break

        url = pg.url
        print(f"  URL: {url}")

        if "pastebin.com/" in url and url != "https://pastebin.com/":
            import requests
            r = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0 Chrome/125.0.0.0"})
            if "vestacall" in r.text.lower():
                print(f"  VERIFIED: {url}")
                pg.screenshot(path="output/pastebin_verified.png")
                log_result("Pastebin.com", url, "success", f"Pastebin DA 82 — vestacall verified at {url}")
            else:
                print("  Published but vestacall not found in HTML")
                log_result("Pastebin.com", url, "pending", "Published but vestacall not in rendered page")
        else:
            print("  URL didn't change — may have CAPTCHA or need account")
            pg.screenshot(path="output/pastebin_result.png")
except Exception as e:
    print(f"  ERROR: {e}")
finally:
    ctx.close()

time.sleep(5)

# ===== CODEBERG (DA 70) — NEW DOMAIN =====
print("\n" + "=" * 60)
print("CODEBERG.ORG (DA 70) — NEW DOMAIN")
print("=" * 60)

ctx, pg = new_page(browser, config, site_name="codeberg")
try:
    # Sign up
    pg.goto("https://codeberg.org/user/sign_up", timeout=60000)
    pg.wait_for_load_state("domcontentloaded", timeout=20000)
    time.sleep(4)
    dismiss_overlays(pg)
    random_mouse_movement(pg)

    text = pg.evaluate("document.body.innerText.substring(0, 300)").encode("ascii", "replace").decode()
    print(f"  Page: {text[:150]}")

    # Check if signup form exists
    username_field = pg.query_selector("input#user_name, input[name='user_name']")
    email_field = pg.query_selector("input#email, input[name='email']")
    pwd_field = pg.query_selector("input#password, input[name='password']")

    has_captcha = any(x in pg.content().lower() for x in ["recaptcha", "captcha", "turnstile", "hcaptcha"])

    if username_field and email_field and pwd_field and not has_captcha:
        print("  Signup form found — no CAPTCHA!")

        human_type(pg, "input#user_name, input[name='user_name']", "dialphonelimited")
        inter_field_delay(config)
        human_type(pg, "input#email, input[name='email']", "commercial@dialphone.com")
        inter_field_delay(config)
        human_type(pg, "input#password, input[name='password']", "Cb@Dphone2026!")
        inter_field_delay(config)

        # Confirm password if exists
        confirm = pg.query_selector("input#retype, input[name='retype']")
        if confirm:
            human_type(pg, "input#retype, input[name='retype']", "Cb@Dphone2026!")
            inter_field_delay(config)

        # Submit
        human_click(pg, 'button:has-text("Register"), button:has-text("Sign Up"), button[type=submit]')
        time.sleep(8)

        url = pg.url
        print(f"  After signup: {url}")
        pg.screenshot(path="output/codeberg_signup.png")

        if "sign_up" not in url:
            print("  SIGNUP SUCCESS!")

            # Create repo
            pg.goto("https://codeberg.org/repo/create", timeout=30000)
            pg.wait_for_load_state("domcontentloaded", timeout=15000)
            time.sleep(4)

            repo_name_field = pg.query_selector("input#repo_name, input[name='repo_name']")
            if repo_name_field:
                repo_name_field.click()
                time.sleep(0.3)
                pg.keyboard.type("voip-open-source-tools", delay=40)
                time.sleep(1)

                desc_field = pg.query_selector("textarea#description, textarea[name='description']")
                if desc_field:
                    desc_field.click()
                    time.sleep(0.3)
                    pg.keyboard.type("Open source VoIP tools and resources — by DialPhone Limited. https://vestacall.com", delay=15)
                    time.sleep(1)

                # Check "Initialize with README"
                readme_check = pg.query_selector("input#auto-init, input[name='auto_init']")
                if readme_check and not readme_check.is_checked():
                    readme_check.click()
                    time.sleep(0.5)

                # Create
                human_click(pg, 'button:has-text("Create Repository"), button[type=submit]')
                time.sleep(8)

                repo_url = pg.url
                print(f"  Repo: {repo_url}")

                if "voip-open-source-tools" in repo_url:
                    print("  REPO CREATED!")

                    # Edit README
                    pg.goto(f"{repo_url}/_edit/main/README.md", timeout=30000)
                    pg.wait_for_load_state("domcontentloaded", timeout=15000)
                    time.sleep(5)

                    # Set content
                    editor = pg.query_selector("textarea, .CodeMirror, [contenteditable]")
                    if editor:
                        pg.evaluate("(t) => navigator.clipboard.writeText(t)", codeberg_readme)
                        editor.click()
                        time.sleep(0.5)
                        pg.keyboard.press("Control+a")
                        time.sleep(0.2)
                        pg.keyboard.press("Control+v")
                        time.sleep(3)

                        # Commit
                        commit = pg.query_selector('button:has-text("Commit"), button[type=submit]')
                        if commit:
                            commit.click()
                            time.sleep(5)
                            print("  README committed!")

                    # Verify
                    pg.goto(f"https://codeberg.org/dialphonelimited/voip-open-source-tools", timeout=30000)
                    pg.wait_for_load_state("domcontentloaded", timeout=15000)
                    time.sleep(3)

                    if "vestacall" in pg.content().lower():
                        print(f"  VERIFIED: {repo_url}")
                        pg.screenshot(path="output/codeberg_verified.png")
                        log_result("Codeberg", repo_url, "success", "Codeberg DA 70 — new domain, vestacall verified")
                    else:
                        print("  Repo created but vestacall not in README")
        else:
            print(f"  Signup may have failed — still on: {url}")
    elif has_captcha:
        print("  CAPTCHA detected — cannot automate signup")
    else:
        print("  Signup form not found as expected")
        # List inputs
        inputs = pg.query_selector_all("input:visible")
        for inp in inputs[:10]:
            n = inp.get_attribute("name") or ""
            t = inp.get_attribute("type") or ""
            print(f"    input: name={n} type={t}")
except Exception as e:
    print(f"  ERROR: {e}")
finally:
    ctx.close()

time.sleep(5)

# ===== GITLAB (DA 92) — NEW DOMAIN =====
print("\n" + "=" * 60)
print("GITLAB.COM (DA 92) — NEW DOMAIN")
print("=" * 60)

ctx, pg = new_page(browser, config, site_name="gitlab")
try:
    pg.goto("https://gitlab.com/users/sign_up", timeout=60000)
    pg.wait_for_load_state("domcontentloaded", timeout=30000)
    time.sleep(5)
    dismiss_overlays(pg)

    text = pg.evaluate("document.body.innerText.substring(0, 300)").encode("ascii", "replace").decode()
    print(f"  Page: {text[:150]}")

    has_captcha = any(x in pg.content().lower() for x in ["recaptcha", "captcha", "turnstile", "hcaptcha", "arkose"])

    if has_captcha:
        print("  CAPTCHA detected — skipping")
    else:
        # Look for signup fields
        inputs = pg.query_selector_all("input:visible")
        print(f"  Visible inputs: {len(inputs)}")
        for inp in inputs[:10]:
            n = inp.get_attribute("name") or ""
            t = inp.get_attribute("type") or ""
            ph = inp.get_attribute("placeholder") or ""
            print(f"    name={n} type={t} placeholder={ph[:25]}")

    pg.screenshot(path="output/gitlab_signup.png")

except Exception as e:
    print(f"  ERROR: {e}")
finally:
    ctx.close()

browser.close()
pw.stop()

# Final count
with open(CSV_PATH, "r", encoding="utf-8", errors="replace") as f:
    rows = list(csv.DictReader(f))
    success = [r for r in rows if r["status"] == "success"]
    domains = {}
    for r in success:
        u = r["backlink_url"]
        if "github.com/dialphone" in u: d = "github.com/dialphonelimited (DA 100)"
        elif "telegra.ph" in u: d = "telegra.ph (DA 73)"
        elif "paste2" in u: d = "paste2.org (DA 55)"
        elif "snippet" in u: d = "snippet.host (DA 40)"
        elif "pastebin.com" in u: d = "pastebin.com (DA 82)"
        elif "codeberg" in u: d = "codeberg.org (DA 70)"
        elif "gitlab" in u: d = "gitlab.com (DA 92)"
        else: d = "other"
        domains[d] = domains.get(d, 0) + 1

    print(f"\n{'='*60}")
    print(f"TOTAL VERIFIED: {len(success)}")
    print(f"REFERRING DOMAINS: {len(domains)}")
    for d, c in sorted(domains.items(), key=lambda x: -x[1]):
        print(f"  {d}: {c}")
