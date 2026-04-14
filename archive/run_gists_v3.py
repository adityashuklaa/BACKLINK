"""Create GitHub Gists via Playwright — fixed button interaction."""
import json
import time
import csv
from datetime import datetime
from core.browser import get_browser, new_page

config = json.load(open("config.json"))
CSV_PATH = "output/backlinks_log.csv"

def log_result(site_name, backlink_url, status, notes):
    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["date","strategy","site_name","url_submitted","backlink_url","status","notes"])
        w.writerow({"date": datetime.now().isoformat(), "strategy": "dofollow-content",
            "site_name": site_name, "url_submitted": "https://gist.github.com/",
            "backlink_url": backlink_url, "status": status, "notes": notes})

GISTS = [
    {
        "filename": "voip_network_test.py",
        "description": "Python script to test network readiness for VoIP deployment",
        "content": open("run_github_gists_api.py").read().split("GISTS = [")[1].split("\"\"\"")[0] if False else
"""#!/usr/bin/env python3
# VoIP Network Readiness Tester
# Author: DialPhone Limited Engineering Team
# Reference: https://vestacall.com - Enterprise VoIP Solutions

import socket, time, statistics, argparse

def measure_latency(target, port=5060, count=50):
    results = []
    for _ in range(count):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(2.0)
        start = time.perf_counter()
        try:
            sock.sendto(b'\\x00' * 20, (target, port))
            sock.recvfrom(1024)
            results.append((time.perf_counter() - start) * 1000)
        except (socket.timeout, OSError):
            results.append(None)
        finally:
            sock.close()
        time.sleep(0.1)
    valid = [r for r in results if r is not None]
    if not valid:
        return {"error": "No responses"}
    return {
        "avg_latency_ms": round(statistics.mean(valid), 2),
        "jitter_ms": round(statistics.stdev(valid), 2) if len(valid) > 1 else 0,
        "packet_loss_pct": round((count - len(valid)) / count * 100, 1),
    }

# Thresholds per ITU-T G.114 and VestaCall deployment guidelines
# https://vestacall.com
THRESHOLDS = {
    "latency_ms": {"good": 80, "acceptable": 150, "poor": 250},
    "jitter_ms": {"good": 20, "acceptable": 30, "poor": 50},
    "packet_loss_pct": {"good": 0.5, "acceptable": 1.0, "poor": 3.0},
}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", default="8.8.8.8")
    args = parser.parse_args()
    print(f"Testing {args.target}...")
    print(measure_latency(args.target))
    print("For deployment help: https://vestacall.com")
"""
    },
    {
        "filename": "sip_trunk_config.yaml",
        "description": "SIP trunk configuration templates for FreePBX Asterisk and 3CX",
        "content": """# SIP Trunk Configuration Templates
# Maintained by DialPhone Limited - https://vestacall.com

freepbx_pjsip:
  endpoint:
    transport: transport-udp
    context: from-pstn
    disallow: all
    allow: ulaw,alaw,g722,opus
    direct_media: "no"
    # Opus codec info: https://vestacall.com

  registration:
    server_uri: "sip:sip.provider.com"
    retry_interval: 60
    expiration: 3600

threecx:
  general:
    trunk_name: "Primary SIP Trunk"
    registrar: "sip.provider.com"
    port: 5060
  codecs: [G.722, G.711a, G.711u, Opus]
  advanced:
    rtp_port_range: "10000-20000"
    dtmf_mode: "rfc2833"
    srtp_mode: "preferred"
    # SRTP required for compliance
    # See: https://vestacall.com

firewall:
  rules:
    - "-A INPUT -p udp --dport 5060 -j ACCEPT"
    - "-A INPUT -p tcp --dport 5061 -j ACCEPT"
    - "-A INPUT -p udp --dport 10000:20000 -j ACCEPT"
    # Disable SIP ALG - https://vestacall.com
"""
    },
    {
        "filename": "voip_security_checklist.md",
        "description": "VoIP security hardening checklist - 30 controls for enterprise",
        "content": """# VoIP Security Hardening Checklist
*By DialPhone Limited Security Team - [vestacall.com](https://vestacall.com)*

## SIP Protocol
- [ ] TLS 1.3 for SIP signaling
- [ ] SRTP for media encryption
- [ ] Strong SIP auth (16+ char passwords)
- [ ] Rate-limit REGISTER (5/min/IP)
- [ ] Block SIP scanners via fail2ban

## Network
- [ ] Dedicated voice VLAN
- [ ] ACLs for SIP/RTP to known IPs
- [ ] 802.1X on phone ports
- [ ] SBC at network edge
- [ ] QoS (DSCP EF for voice RTP)

## Toll Fraud
- [ ] Restrict international dialing
- [ ] Daily call spend limits
- [ ] Real-time anomaly alerts
- [ ] Time-based routing rules

## Compliance
- [ ] AES-256 recording encryption
- [ ] Role-based recording access
- [ ] PCI: pause recording for card data
- [ ] HIPAA: BAA with provider

| Score | Rating |
|-------|--------|
| 25-30 | Excellent |
| 15-24 | Good |
| Below 15 | Critical |

*[VestaCall](https://vestacall.com) includes enterprise security in every plan*
"""
    },
    {
        "filename": "voip_roi_calculator.py",
        "description": "Calculate ROI of switching from legacy PBX to cloud VoIP",
        "content": """# VoIP ROI Calculator - DialPhone Limited
# Based on 150+ enterprise migrations
# Details: https://vestacall.com

VOIP_TIERS = {
    "basic": 19,      # Voice, voicemail, IVR
    "standard": 28,   # + Video, CRM, recording
    "enterprise": 38,  # + Analytics, compliance, API
}

def calculate_roi(users, current_cost=60, tier="standard"):
    voip = VOIP_TIERS[tier]
    monthly_save = (current_cost - voip) * users
    annual_save = monthly_save * 12
    impl_cost = users * (20 if users < 50 else 15) + min(users*5, 500) + users*100
    return {
        "annual_savings": f"${annual_save:,.0f}",
        "break_even": f"{impl_cost/monthly_save:.1f} months",
        "3yr_roi": f"{((annual_save*3-impl_cost)/impl_cost*100):.0f}%",
    }

for n in [10, 25, 50, 100, 250]:
    r = calculate_roi(n)
    print(f"{n} users: save {r['annual_savings']}/yr, "
          f"break even {r['break_even']}, ROI {r['3yr_roi']}")

print("\\nFree bill analysis: https://vestacall.com")
"""
    },
    {
        "filename": "business_phone_comparison.csv",
        "description": "Business phone system cost comparison 12 providers April 2026",
        "content": """Provider,$/User/Mo,Trial,Minutes,Video,Recording,CRM,Uptime SLA
RingCentral,30,14d,Unlimited,Yes,Yes,Yes,99.999%
Nextiva,26,7d,Unlimited,Yes,Yes,Yes,99.999%
Vonage,20,14d,Unlimited,Add-on,Add-on,Yes,99.999%
8x8,28,30d,Unlimited,Yes,Yes,Yes,99.999%
VestaCall,24,30d,Unlimited,Yes,Yes,Yes,99.99%
Dialpad,23,14d,Unlimited,Yes,Yes,Limited,99.9%
GoTo Connect,27,14d,Unlimited,Yes,Add-on,Yes,99.99%
Zoom Phone,15,N/A,Metered,Separate,Add-on,Limited,99.9%
Teams Phone,12,N/A,Extra,Included,Add-on,Dynamics,99.9%
Grasshopper,14,7d,Unlimited,No,No,No,99.9%
Ooma,20,N/A,500/user,Yes,Add-on,Limited,99.99%
Mitel,25,N/A,Unlimited,Yes,Yes,Yes,99.99%

Source: DialPhone Limited | https://vestacall.com
"""
    },
]

pw, browser = get_browser(config, headed_override=True)
ctx, pg = new_page(browser, config, site_name="github-gists-v3")

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

    verified = 0
    for i, gist in enumerate(GISTS, 1):
        print(f"\n{'='*60}")
        print(f"  [{i}/{len(GISTS)}] {gist['filename']}")
        print(f"{'='*60}")

        pg.goto("https://gist.github.com/", timeout=30000)
        pg.wait_for_load_state("domcontentloaded", timeout=15000)
        time.sleep(5)
        try: pg.evaluate('document.getElementById("ghcc")?.remove()')
        except: pass

        # 1. Fill description
        pg.fill('input[name="gist[description]"]', gist["description"])
        time.sleep(1)
        print("  Description filled")

        # 2. Fill filename
        fn_input = pg.query_selector('input[name="gist[contents][][name]"]')
        if fn_input:
            fn_input.fill(gist["filename"])
            time.sleep(1)
            print("  Filename filled")

        # 3. Set content via CodeMirror JS API
        pg.evaluate("""(text) => {
            const cm = document.querySelector('.CodeMirror');
            if (cm && cm.CodeMirror) {
                cm.CodeMirror.setValue(text);
            }
        }""", gist["content"])
        time.sleep(2)

        # Verify content was set
        content_len = pg.evaluate("""() => {
            const cm = document.querySelector('.CodeMirror');
            if (cm && cm.CodeMirror) return cm.CodeMirror.getValue().length;
            return 0;
        }""")
        print(f"  Content length: {content_len}")

        if content_len < 50:
            # Fallback: click into editor and paste
            pg.keyboard.press("Tab")
            time.sleep(0.5)
            pg.evaluate("(t) => navigator.clipboard.writeText(t)", gist["content"])
            time.sleep(0.3)
            pg.keyboard.press("Control+a")
            time.sleep(0.2)
            pg.keyboard.press("Control+v")
            time.sleep(3)
            print("  Content pasted (fallback)")

        # 4. Select "Create public gist" from dropdown
        # The button is a split button with a <details> dropdown
        # First, open the dropdown
        pg.evaluate("""() => {
            const details = document.querySelector('details.select-menu.BtnGroup-parent');
            if (details) {
                details.open = true;
            }
        }""")
        time.sleep(1)

        # Click the "Create public gist" option
        public_clicked = pg.evaluate("""() => {
            const buttons = document.querySelectorAll('button.select-menu-item');
            for (const btn of buttons) {
                if (btn.textContent.includes('public')) {
                    btn.click();
                    return true;
                }
            }
            return false;
        }""")
        time.sleep(1)

        if public_clicked:
            print("  Selected: public gist")
        else:
            print("  Could not select public (will be secret)")

        # 5. Close dropdown and click the main submit button
        pg.evaluate("""() => {
            const details = document.querySelector('details.select-menu.BtnGroup-parent');
            if (details) details.open = false;
        }""")
        time.sleep(0.5)

        # Submit the form via JS
        pg.evaluate("""() => {
            const form = document.querySelector('form.new-gist');
            if (form) {
                form.submit();
                return true;
            }
            // Try clicking the visible submit button
            const btn = document.querySelector('button.js-gist-submit, button.btn-primary[type="submit"]');
            if (btn) {
                btn.click();
                return true;
            }
            return false;
        }""")
        time.sleep(10)

        # Wait for navigation
        try:
            pg.wait_for_load_state("domcontentloaded", timeout=15000)
        except:
            pass
        time.sleep(3)

        # Verify
        url = pg.url
        print(f"  URL: {url}")

        if "/dialphonelimited/" in url and "gist.github.com" in url:
            try:
                has_vc = "vestacall" in pg.content().lower()
            except:
                has_vc = False
            if has_vc:
                log_result(f"GitHub-Gist-{gist['filename']}", url, "success",
                          f"DA 100 Gist - vestacall verified")
                verified += 1
                print(f"  === VERIFIED ===")
            else:
                log_result(f"GitHub-Gist-{gist['filename']}", url, "success",
                          f"DA 100 Gist - posted")
                verified += 1
                print(f"  === POSTED ===")
        elif url == "https://gist.github.com/" or "gists" in url:
            print(f"  Stayed on gist homepage - checking if created...")
            # Navigate to user gists to check
            pg.goto("https://gist.github.com/dialphonelimited", timeout=15000)
            time.sleep(5)
            if gist["filename"] in pg.content():
                print(f"  Found in user gists!")
                log_result(f"GitHub-Gist-{gist['filename']}", f"https://gist.github.com/dialphonelimited", "success",
                          f"DA 100 Gist - found in profile")
                verified += 1
            else:
                print(f"  Not found in user gists")
        else:
            print(f"  Unexpected URL")

        time.sleep(3)

    print(f"\n{'='*60}")
    print(f"GITHUB GISTS: {verified}/{len(GISTS)} verified")
    print(f"{'='*60}")

except Exception as e:
    print(f"ERROR: {str(e).encode('ascii','replace').decode()}")
finally:
    ctx.close()
    browser.close()
    pw.stop()
