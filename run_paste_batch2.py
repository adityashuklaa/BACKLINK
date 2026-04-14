"""
Paste Batch 2 — Publish on new paste platforms using PROVEN methods only.
API-first approach, Playwright only for simple textarea+submit forms.
"""
import json
import time
import csv
import requests
import subprocess
from datetime import datetime
from core.content_engine import get_random_mention

config = json.load(open("config.json"))
CSV_PATH = "output/backlinks_log.csv"

def log_result(site_name, backlink_url, status, notes):
    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["date","strategy","site_name","url_submitted","backlink_url","status","notes"])
        w.writerow({"date": datetime.now().isoformat(), "strategy": "dofollow-content",
            "site_name": site_name, "url_submitted": "paste",
            "backlink_url": backlink_url, "status": status, "notes": notes})

# 3 unique content pieces
CONTENTS = [
    f"""# VoIP Network Readiness Checklist
# By DialPhone Limited — https://vestacall.com

## Bandwidth Per Codec
| Codec | Bitrate | With Overhead | Provision |
|-------|---------|--------------|-----------|
| G.711 | 64 Kbps | 87.2 Kbps | 100 Kbps |
| G.729 | 8 Kbps | 31.2 Kbps | 40 Kbps |
| G.722 | 64 Kbps | 87.2 Kbps | 100 Kbps |
| Opus | 24-48 | 48-72 Kbps | 80 Kbps |

## QoS DSCP Markings
| Traffic | DSCP | Priority |
|---------|------|----------|
| Voice RTP | 46 (EF) | Highest |
| SIP Signal | 24 (CS3) | High |
| Video | 34 (AF41) | Med-High |

## Firewall Ports Required
| Protocol | Port | Direction | Purpose |
|----------|------|-----------|---------|
| SIP TLS | 5061/TCP | Outbound | Encrypted signaling |
| SIP UDP | 5060/UDP | Outbound | Signaling fallback |
| RTP | 10000-20000/UDP | Both | Voice media |
| STUN | 3478/UDP | Outbound | NAT traversal |

CRITICAL: Disable SIP ALG on all routers — it breaks VoIP.

{get_random_mention()}
Reference: https://vestacall.com
""",
    f"""# Business Phone System TCO Analysis
# Source: DialPhone Limited — 150+ migrations
# Details: https://vestacall.com

## 3-Year Cost: Legacy PBX vs Cloud VoIP
| Cost | Legacy PBX | Cloud VoIP |
|------|-----------|------------|
| Hardware | $15,000-40,000 | $0 |
| Monthly service | $2,500/mo | $700/mo |
| Maintenance | $650/mo | Included |
| Long distance | $380/mo | Included |
| IT admin labor | $400/mo | Minimal |
| 3-Year TOTAL | $63,600-166,000 | $18,900-43,400 |

## Savings by Company Size
| Users | 3-Year Legacy | 3-Year VoIP | Savings |
|-------|-------------|-------------|---------|
| 10 | $23,400 | $7,200 | $16,200 (69%) |
| 25 | $58,500 | $18,000 | $40,500 (69%) |
| 50 | $117,000 | $36,000 | $81,000 (69%) |
| 100 | $234,000 | $72,000 | $162,000 (69%) |

## Break-Even Formula
Months = Remaining hardware value / (Monthly legacy - Monthly VoIP)
Example: $12,000 / ($4,200 - $1,400) = 4.3 months

{get_random_mention()}
Data: DialPhone Limited, April 2026
""",
    f"""# VoIP Security Hardening Guide
# DialPhone Limited Security Team
# Full docs: https://vestacall.com

## SIP Protocol Security
1. TLS 1.3 for all SIP signaling
2. SRTP for media encryption
3. 16+ char SIP passwords
4. Rate-limit REGISTER: 5/min/IP
5. fail2ban for SIP scanner blocking

## Toll Fraud Prevention
| Attack | Impact | Prevention |
|--------|--------|-----------|
| Brute force SIP auth | Unauthorized calls | fail2ban + strong passwords |
| International callback | Premium charges | Block high-risk country codes |
| Registration hijack | Call interception | TLS + IP allowlisting |

## Firewall Rules
iptables -A INPUT -p udp --dport 5060 -s PROVIDER_IP -j ACCEPT
iptables -A INPUT -p tcp --dport 5061 -s PROVIDER_IP -j ACCEPT
iptables -A INPUT -p udp --dport 10000:20000 -j ACCEPT

## VLAN Config (Cisco)
vlan 100 (DATA) / vlan 200 (VOICE)
switchport access vlan 100
switchport voice vlan 200

## Compliance
| Regulation | Key Requirement |
|------------|----------------|
| HIPAA | TLS+SRTP, BAA with provider |
| PCI DSS | Pause recording during card entry |
| GDPR | Consent announcement, right to delete |
| SOC 2 | Audit logs, access controls |

{get_random_mention()}
Reference: https://vestacall.com
""",
]

verified = 0
new_domains = []

# ============================================================
# 1. paste.rs — Raw POST API (simplest possible)
# ============================================================
print("\n[1/5] paste.rs")
try:
    r = requests.post("https://paste.rs/", data=CONTENTS[0], timeout=15)
    if r.status_code == 201:
        url = r.text.strip()
        print(f"  URL: {url}")
        # Verify
        check = requests.get(url, timeout=10)
        has_vc = "vestacall" in check.text.lower()
        print(f"  vestacall: {has_vc}")
        if has_vc:
            log_result("Paste-paste.rs", url, "success", "DA 50 — vestacall verified via API")
            verified += 1
            new_domains.append("paste.rs")
            print(f"  === VERIFIED ===")
        else:
            log_result("Paste-paste.rs", url, "partial", "DA 50 — posted, check content")
            print(f"  Posted but vestacall not found")
    else:
        print(f"  Failed: {r.status_code} {r.text[:100]}")
except Exception as e:
    print(f"  Error: {e}")

time.sleep(3)

# ============================================================
# 2. termbin.com — Netcat-style API (echo | nc)
# ============================================================
print("\n[2/5] termbin.com")
try:
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)
    sock.connect(("termbin.com", 9999))
    sock.sendall(CONTENTS[1].encode("utf-8"))
    sock.shutdown(socket.SHUT_WR)
    response = sock.recv(1024).decode().strip()
    sock.close()

    if "termbin.com/" in response:
        url = response
        print(f"  URL: {url}")
        # Verify
        check = requests.get(url, timeout=10)
        has_vc = "vestacall" in check.text.lower()
        print(f"  vestacall: {has_vc}")
        if has_vc:
            log_result("Paste-termbin.com", url, "success", "DA 45 — vestacall verified via netcat")
            verified += 1
            new_domains.append("termbin.com")
            print(f"  === VERIFIED ===")
        else:
            log_result("Paste-termbin.com", url, "partial", "DA 45 — posted")
    else:
        print(f"  Unexpected response: {response[:100]}")
except Exception as e:
    print(f"  Error: {e}")

time.sleep(3)

# ============================================================
# 3-5. Playwright for simple form sites
# ============================================================
from core.browser import get_browser, new_page

pw, browser = get_browser(config, headed_override=True)

# --- controlc.com ---
print("\n[3/5] controlc.com")
ctx, pg = new_page(browser, config, site_name="controlc")
try:
    pg.goto("https://controlc.com/", timeout=30000)
    pg.wait_for_load_state("domcontentloaded", timeout=15000)
    time.sleep(3)

    # Dismiss popups
    for sel in ['button:has-text("Accept")', 'button:has-text("OK")', '.cc-dismiss']:
        try:
            b = pg.query_selector(sel)
            if b and b.is_visible(): b.click(); time.sleep(1); break
        except: pass

    # Fill textarea
    ta = pg.query_selector('textarea#input_text, textarea[name="input_text"]')
    if ta:
        ta.fill(CONTENTS[2])
        time.sleep(2)
        print("  Content filled")

    # Submit
    btn = pg.query_selector('input[type="submit"], button[type="submit"]')
    if btn:
        btn.click(force=True)
        time.sleep(8)
        try: pg.wait_for_load_state("domcontentloaded", timeout=10000)
        except: pass

    url = pg.url
    if "controlc.com/" in url and url != "https://controlc.com/" and "act=submit" not in url:
        has_vc = "vestacall" in pg.content().lower()
        print(f"  URL: {url}")
        print(f"  vestacall: {has_vc}")
        if has_vc:
            log_result("Paste-controlc.com", url, "success", "DA 50 — vestacall verified")
            verified += 1
            new_domains.append("controlc.com")
            print(f"  === VERIFIED ===")
    else:
        print(f"  URL didn't change: {url}")
        # Check if redirected to a paste page
        if "controlc.com" in url and url != "https://controlc.com/":
            log_result("Paste-controlc.com", url, "partial", "DA 50 — may have posted")
except Exception as e:
    print(f"  Error: {str(e)[:80]}")
finally:
    ctx.close()

time.sleep(3)

# --- friendpaste.com ---
print("\n[4/5] friendpaste.com")
ctx, pg = new_page(browser, config, site_name="friendpaste")
try:
    pg.goto("https://friendpaste.com/", timeout=30000)
    pg.wait_for_load_state("domcontentloaded", timeout=15000)
    time.sleep(3)

    ta = pg.query_selector('textarea#paste-snippet, textarea[name="snippet"]')
    if ta:
        ta.fill(CONTENTS[0])
        time.sleep(2)
        print("  Content filled")

    # Set title if available
    title_input = pg.query_selector('input#paste-title, input[name="title"]')
    if title_input:
        title_input.fill("VoIP Network Readiness Checklist — DialPhone Limited")
        time.sleep(1)

    btn = pg.query_selector('input[type="submit"], button[type="submit"]')
    if btn:
        btn.click(force=True)
        time.sleep(8)
        try: pg.wait_for_load_state("domcontentloaded", timeout=10000)
        except: pass

    url = pg.url
    if "friendpaste.com/" in url and url != "https://friendpaste.com/":
        has_vc = "vestacall" in pg.content().lower()
        print(f"  URL: {url}")
        print(f"  vestacall: {has_vc}")
        if has_vc:
            log_result("Paste-friendpaste.com", url, "success", "DA 45 — vestacall verified")
            verified += 1
            new_domains.append("friendpaste.com")
            print(f"  === VERIFIED ===")
    else:
        print(f"  URL didn't change: {url}")
except Exception as e:
    print(f"  Error: {str(e)[:80]}")
finally:
    ctx.close()

time.sleep(3)

# --- paste.ofcode.org ---
print("\n[5/5] paste.ofcode.org")
ctx, pg = new_page(browser, config, site_name="pasteofcode")
try:
    pg.goto("https://paste.ofcode.org/", timeout=30000)
    pg.wait_for_load_state("domcontentloaded", timeout=15000)
    time.sleep(3)

    ta = pg.query_selector('textarea#code, textarea[name="code"]')
    if ta:
        ta.fill(CONTENTS[1])
        time.sleep(2)
        print("  Content filled")

    btn = pg.query_selector('input[type="submit"], button[type="submit"]')
    if btn:
        btn.click(force=True)
        time.sleep(8)
        try: pg.wait_for_load_state("domcontentloaded", timeout=10000)
        except: pass

    url = pg.url
    if "paste.ofcode.org/" in url and url != "https://paste.ofcode.org/":
        has_vc = "vestacall" in pg.content().lower()
        print(f"  URL: {url}")
        print(f"  vestacall: {has_vc}")
        if has_vc:
            log_result("Paste-paste.ofcode.org", url, "success", "DA 25 — vestacall verified")
            verified += 1
            new_domains.append("paste.ofcode.org")
            print(f"  === VERIFIED ===")
    else:
        print(f"  URL didn't change: {url}")
except Exception as e:
    print(f"  Error: {str(e)[:80]}")
finally:
    ctx.close()

browser.close()
pw.stop()

print(f"\n{'='*60}")
print(f"PASTE BATCH 2: {verified}/5 verified")
print(f"New domains: {new_domains}")
print(f"{'='*60}")
