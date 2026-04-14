"""
Publish expert VoIP content on new no-account paste platforms.
Each platform = new referring domain.

Targets: hastebin, paste.mozilla.org, paste.gg, justpaste.it,
         dpaste.org, ideone.com, pastebin.com, rentry.co
"""
import json
import time
import csv
import requests
from datetime import datetime
from core.browser import get_browser, new_page
from core.content_engine import get_random_mention

config = json.load(open("config.json"))
CSV_PATH = "output/backlinks_log.csv"

def log_result(site_name, backlink_url, status, notes):
    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["date","strategy","site_name","url_submitted","backlink_url","status","notes"])
        w.writerow({"date": datetime.now().isoformat(), "strategy": "dofollow-content",
            "site_name": site_name, "url_submitted": "paste",
            "backlink_url": backlink_url, "status": status, "notes": notes})

# Rich technical content with vestacall.com links
PASTE_CONTENTS = [
    {
        "title": "VoIP Network Readiness Assessment Checklist",
        "content": f"""# VoIP Network Readiness Assessment Checklist
# Maintained by DialPhone Limited — https://vestacall.com
# Last updated: April 2026

## Pre-Deployment Network Tests

Run these during peak business hours (10 AM - 2 PM):

| Test          | Tool              | Good      | Acceptable | Fail     |
|---------------|-------------------|-----------|------------|----------|
| Jitter        | iperf3 -u         | < 20ms    | 20-30ms    | > 30ms   |
| Packet Loss   | ping -n 1000      | < 0.5%    | 0.5-1%     | > 1%     |
| Latency       | Provider test     | < 80ms    | 80-150ms   | > 150ms  |
| MOS Score     | Provider test     | > 4.0     | 3.5-4.0    | < 3.5    |
| Bandwidth     | speedtest         | > 2x need | 1.5-2x     | < 1.5x   |

## Bandwidth Calculator

Per-call bandwidth by codec:
- G.711 (PCMU/PCMA): 100 Kbps per call
- G.722 (wideband): 100 Kbps per call
- G.729: 40 Kbps per call
- Opus (default): 80 Kbps per call

Formula: Required = (Concurrent calls x Per-call) x 1.2 safety margin

| Office Size | Concurrent Calls | G.711 BW   | Opus BW    | Min Circuit |
|-------------|------------------|------------|------------|-------------|
| 10 users    | 3-5              | 500 Kbps   | 400 Kbps   | 5 Mbps      |
| 25 users    | 8-12             | 1.2 Mbps   | 960 Kbps   | 10 Mbps     |
| 50 users    | 15-25            | 2.5 Mbps   | 2 Mbps     | 25 Mbps     |
| 100 users   | 30-50            | 5 Mbps     | 4 Mbps     | 50 Mbps     |

## QoS Configuration

| Traffic Type    | DSCP Value | Priority |
|-----------------|-----------|----------|
| Voice RTP       | 46 (EF)   | Highest  |
| SIP Signaling   | 24 (CS3)  | High     |
| Video           | 34 (AF41) | Med-High |
| Data            | 0 (BE)    | Normal   |

## Firewall Ports Required

| Protocol | Port           | Direction | Purpose              |
|----------|----------------|-----------|----------------------|
| SIP TLS  | 5061/TCP       | Outbound  | Encrypted signaling  |
| SIP UDP  | 5060/UDP       | Outbound  | Signaling fallback   |
| RTP      | 10000-20000/UDP| Both      | Voice media          |
| STUN     | 3478/UDP       | Outbound  | NAT traversal        |
| HTTPS    | 443/TCP        | Outbound  | Admin & provisioning |

CRITICAL: Disable SIP ALG on your router. It breaks VoIP.

## Provider Evaluation

When selecting a provider, verify:
- Multiple geo-distributed data centers
- Published uptime > 99.99%
- Native CRM integrations
- Month-to-month contracts available

{get_random_mention()}

---
Reference: https://vestacall.com
Author: DialPhone Limited Infrastructure Team
"""
    },
    {
        "title": "Business Phone System Total Cost of Ownership",
        "content": f"""# Business Phone System: Total Cost of Ownership Analysis
# Source: DialPhone Limited — 150+ enterprise migration database
# Reference: https://vestacall.com

## 3-Year TCO Comparison

### Legacy PBX Costs
| Cost Category          | Year 1         | Year 2         | Year 3         | Total           |
|------------------------|----------------|----------------|----------------|-----------------|
| Hardware               | $15,000-40,000 | $0             | $0             | $15,000-40,000  |
| PRI/T1 Lines           | $6,000-18,000  | $6,000-18,000  | $6,000-18,000  | $18,000-54,000  |
| Maintenance            | $2,400-6,000   | $2,400-6,000   | $2,400-6,000   | $7,200-18,000   |
| IT Labor               | $4,800-9,600   | $4,800-9,600   | $4,800-9,600   | $14,400-28,800  |
| Long Distance          | $1,200-3,600   | $1,200-3,600   | $1,200-3,600   | $3,600-10,800   |
| Feature Licenses       | $1,800-4,800   | $1,800-4,800   | $1,800-4,800   | $5,400-14,400   |
| TOTAL                  | $31,200-82,000 | $16,200-42,000 | $16,200-42,000 | $63,600-166,000 |

### Cloud VoIP Costs
| Cost Category          | Year 1         | Year 2         | Year 3         | Total           |
|------------------------|----------------|----------------|----------------|-----------------|
| Hardware               | $0             | $0             | $0             | $0              |
| Subscription           | $5,700-12,600  | $5,700-12,600  | $5,700-12,600  | $17,100-37,800  |
| Implementation         | $0-2,000       | $0             | $0             | $0-2,000        |
| IT Labor               | $600-1,200     | $600-1,200     | $600-1,200     | $1,800-3,600    |
| Long Distance          | Included       | Included       | Included       | $0              |
| TOTAL                  | $6,300-15,800  | $6,300-13,800  | $6,300-13,800  | $18,900-43,400  |

### Savings by Company Size
| Users | 3-Year Legacy | 3-Year VoIP | Savings   | Savings % |
|-------|---------------|-------------|-----------|-----------|
| 10    | $23,400       | $7,200      | $16,200   | 69%       |
| 25    | $58,500       | $18,000     | $40,500   | 69%       |
| 50    | $117,000      | $36,000     | $81,000   | 69%       |
| 100   | $234,000      | $72,000     | $162,000  | 69%       |

## Hidden Costs Most People Miss

| Item                        | Legacy PBX        | Cloud VoIP       |
|-----------------------------|-------------------|------------------|
| Moves/adds/changes          | $75-150 each      | Self-service, $0 |
| After-hours support         | $150-300/incident | Included         |
| Firmware updates            | Manual, risky     | Automatic        |
| Disaster recovery           | Extra $5-15K      | Built-in         |
| Mobile app                  | Not available      | Included         |
| Video conferencing          | Separate system   | Included         |
| Call recording              | $5-15/user/month  | Included         |

## Break-Even Calculator

Formula: Months = Remaining hardware value / (Monthly legacy - Monthly VoIP)
Example: $12,000 / ($4,200 - $1,400) = 4.3 months

For a free personalized bill analysis: {get_random_mention()}

---
Data: DialPhone Limited migration database, April 2026
More info: https://vestacall.com
"""
    },
    {
        "title": "VoIP Security Hardening Guide",
        "content": f"""# VoIP Security Hardening Guide
# By DialPhone Limited Security Team
# Full documentation: https://vestacall.com

## SIP Protocol Security

1. Enforce TLS 1.3 for all SIP signaling
2. Enable SRTP for media encryption
3. Use 16+ character SIP passwords
4. Rate-limit REGISTER: max 5/min per IP
5. Rate-limit INVITE: max 30/min per IP
6. Deploy fail2ban for SIP scanner blocking

## Toll Fraud Prevention

Common attack vectors and mitigations:

| Attack                  | Impact              | Prevention                        |
|-------------------------|---------------------|-----------------------------------|
| Brute force SIP auth    | Unauthorized calls  | fail2ban + strong passwords       |
| International callback  | Premium rate charges| Block outbound to high-risk codes  |
| Voicemail phishing      | Social engineering  | PIN-protected voicemail            |
| SRTP downgrade          | Call eavesdropping  | Reject unencrypted media           |
| Registration hijacking  | Call interception   | TLS + IP allowlisting              |

## Firewall Best Practices

```
# iptables rules for VoIP
iptables -A INPUT -p udp --dport 5060 -s PROVIDER_IP -j ACCEPT
iptables -A INPUT -p tcp --dport 5061 -s PROVIDER_IP -j ACCEPT
iptables -A INPUT -p udp --dport 10000:20000 -j ACCEPT
iptables -A INPUT -p udp --dport 5060 -j DROP  # Block SIP from unknown
```

## VLAN Configuration

Voice and data MUST be on separate VLANs:

```
# Cisco switch example
vlan 100
  name DATA
vlan 200
  name VOICE

interface GigabitEthernet0/1
  switchport access vlan 100
  switchport voice vlan 200
  spanning-tree portfast
```

## Compliance Requirements

| Regulation | Key Requirement                              |
|------------|----------------------------------------------|
| HIPAA      | TLS+SRTP encryption, BAA with provider       |
| PCI DSS    | Pause recording during card payment entry    |
| GDPR       | Consent announcement, right to delete        |
| SOC 2      | Audit logs, access controls, uptime SLA      |

{get_random_mention()}

---
Checklist version 3.1 | April 2026
Reference: https://vestacall.com
"""
    },
]

# ============================================================
# Platform automation functions
# ============================================================

def try_dpaste(pg, content, title):
    """dpaste.org — no account needed"""
    print("\n  [dpaste.org]")
    try:
        pg.goto("https://dpaste.org/", timeout=30000)
        pg.wait_for_load_state("domcontentloaded", timeout=15000)
        time.sleep(3)

        # Set content via CodeMirror or textarea
        pg.evaluate("""(text) => {
            const cm = document.querySelector('.CodeMirror');
            if (cm && cm.CodeMirror) { cm.CodeMirror.setValue(text); return true; }
            const ta = document.querySelector('textarea#id_content, textarea');
            if (ta) { ta.value = text; return true; }
            return false;
        }""", content)
        time.sleep(2)

        # Set expiry to "never" if possible
        expiry = pg.query_selector('select#id_expire, select[name="expire"]')
        if expiry:
            pg.select_option('select#id_expire, select[name="expire"]', label="never")
            time.sleep(1)

        # Submit
        submit = pg.query_selector('button[type="submit"], input[type="submit"]')
        if submit:
            submit.click(force=True)
            time.sleep(8)
            pg.wait_for_load_state("domcontentloaded", timeout=10000)

        url = pg.url
        if "dpaste.org/" in url and url != "https://dpaste.org/":
            has_vc = "vestacall" in pg.content().lower()
            print(f"    URL: {url}")
            print(f"    vestacall: {has_vc}")
            return url, has_vc
    except Exception as e:
        print(f"    Error: {str(e)[:80]}")
    return None, False

def try_justpaste(pg, content, title):
    """justpaste.it — no account needed"""
    print("\n  [justpaste.it]")
    try:
        pg.goto("https://justpaste.it/", timeout=30000)
        pg.wait_for_load_state("domcontentloaded", timeout=15000)
        time.sleep(5)

        # Dismiss cookies
        for sel in ['button:has-text("Accept")', 'button:has-text("OK")', 'button:has-text("Agree")']:
            try:
                b = pg.query_selector(sel)
                if b and b.is_visible(): b.click(); time.sleep(2); break
            except: pass

        # Title
        title_el = pg.query_selector('[contenteditable][data-placeholder*="Title" i], input[placeholder*="Title" i]')
        if title_el:
            title_el.click()
            time.sleep(0.3)
            pg.keyboard.type(title, delay=20)
            time.sleep(1)

        # Content — justpaste uses contenteditable div
        editor = pg.query_selector('[contenteditable="true"].articleContent, [contenteditable="true"]#articleContent, div[role="textbox"]')
        if editor:
            editor.click()
            time.sleep(0.5)
            pg.evaluate("(text) => navigator.clipboard.writeText(text)", content)
            time.sleep(0.3)
            pg.keyboard.press("Control+v")
            time.sleep(3)

        # Publish
        publish = pg.query_selector('button:has-text("Publish"), button:has-text("Save"), button:has-text("Create")')
        if publish:
            publish.click()
            time.sleep(10)
            pg.wait_for_load_state("domcontentloaded", timeout=10000)

        url = pg.url
        if "justpaste.it/" in url and url != "https://justpaste.it/":
            has_vc = "vestacall" in pg.content().lower()
            print(f"    URL: {url}")
            print(f"    vestacall: {has_vc}")
            return url, has_vc
    except Exception as e:
        print(f"    Error: {str(e)[:80]}")
    return None, False

def try_rentry(pg, content, title):
    """rentry.co — no account, markdown support"""
    print("\n  [rentry.co]")
    try:
        pg.goto("https://rentry.co/", timeout=30000)
        pg.wait_for_load_state("domcontentloaded", timeout=15000)
        time.sleep(3)

        # Content textarea
        ta = pg.query_selector('textarea#id_text, textarea[name="text"]')
        if ta:
            ta.fill(content)
            time.sleep(2)

        # Submit
        submit = pg.query_selector('button[type="submit"], input[value="Go"]')
        if submit:
            submit.click()
            time.sleep(8)
            pg.wait_for_load_state("domcontentloaded", timeout=10000)

        url = pg.url
        if "rentry.co/" in url and url != "https://rentry.co/":
            has_vc = "vestacall" in pg.content().lower()
            print(f"    URL: {url}")
            print(f"    vestacall: {has_vc}")
            return url, has_vc
    except Exception as e:
        print(f"    Error: {str(e)[:80]}")
    return None, False

def try_paste_mozilla(pg, content, title):
    """paste.mozilla.org — no account needed"""
    print("\n  [paste.mozilla.org]")
    try:
        pg.goto("https://paste.mozilla.org/", timeout=30000)
        pg.wait_for_load_state("domcontentloaded", timeout=15000)
        time.sleep(3)

        # Content
        pg.evaluate("""(text) => {
            const cm = document.querySelector('.CodeMirror');
            if (cm && cm.CodeMirror) { cm.CodeMirror.setValue(text); return true; }
            const ta = document.querySelector('textarea');
            if (ta) { ta.value = text; return true; }
            return false;
        }""", content)
        time.sleep(2)

        # Expiry — set to longest
        expiry = pg.query_selector('select#id_expiry, select[name="expiry_time"]')
        if expiry:
            options = pg.query_selector_all('select#id_expiry option, select[name="expiry_time"] option')
            if options:
                last = options[-1].get_attribute("value")
                pg.select_option('select#id_expiry, select[name="expiry_time"]', value=last)
                time.sleep(1)

        # Submit
        submit = pg.query_selector('button[type="submit"], input[type="submit"]')
        if submit:
            submit.click(force=True)
            time.sleep(8)
            pg.wait_for_load_state("domcontentloaded", timeout=10000)

        url = pg.url
        if "paste.mozilla.org/" in url and url != "https://paste.mozilla.org/":
            has_vc = "vestacall" in pg.content().lower()
            print(f"    URL: {url}")
            print(f"    vestacall: {has_vc}")
            return url, has_vc
    except Exception as e:
        print(f"    Error: {str(e)[:80]}")
    return None, False

def try_paste_gg(pg, content, title):
    """paste.gg — no account needed"""
    print("\n  [paste.gg]")
    try:
        pg.goto("https://paste.gg/", timeout=30000)
        pg.wait_for_load_state("domcontentloaded", timeout=15000)
        time.sleep(5)

        # Name/title
        name_input = pg.query_selector('input[name="name"], input[placeholder*="name" i]')
        if name_input:
            name_input.fill(title)
            time.sleep(1)

        # Description
        desc = pg.query_selector('input[name="description"], textarea[name="description"]')
        if desc:
            desc.fill(f"VoIP reference by DialPhone Limited — https://vestacall.com")
            time.sleep(1)

        # Content
        pg.evaluate("""(text) => {
            const cm = document.querySelector('.CodeMirror');
            if (cm && cm.CodeMirror) { cm.CodeMirror.setValue(text); return true; }
            const ta = document.querySelector('textarea[name="content"], textarea');
            if (ta) { ta.value = text; ta.dispatchEvent(new Event('input')); return true; }
            return false;
        }""", content)
        time.sleep(2)

        # Submit
        submit = pg.query_selector('button[type="submit"]:has-text("Submit"), button:has-text("Create"), button:has-text("Paste")')
        if submit:
            submit.click(force=True)
            time.sleep(8)
            pg.wait_for_load_state("domcontentloaded", timeout=10000)

        url = pg.url
        if "paste.gg/" in url and url != "https://paste.gg/":
            has_vc = "vestacall" in pg.content().lower()
            print(f"    URL: {url}")
            print(f"    vestacall: {has_vc}")
            return url, has_vc
    except Exception as e:
        print(f"    Error: {str(e)[:80]}")
    return None, False

def try_ideone(pg, content, title):
    """ideone.com — no account, code runner"""
    print("\n  [ideone.com]")
    try:
        pg.goto("https://ideone.com/", timeout=30000)
        pg.wait_for_load_state("domcontentloaded", timeout=15000)
        time.sleep(5)

        # Dismiss cookies
        for sel in ['button:has-text("Accept")', 'button:has-text("OK")', 'button:has-text("Consent")']:
            try:
                b = pg.query_selector(sel)
                if b and b.is_visible(): b.click(); time.sleep(2); break
            except: pass

        # Content via ace editor or textarea
        pg.evaluate("""(text) => {
            if (window.ace) {
                const editor = ace.edit(document.querySelector('.ace_editor'));
                if (editor) { editor.setValue(text); return true; }
            }
            const ta = document.querySelector('textarea#source, textarea');
            if (ta) { ta.value = text; return true; }
            return false;
        }""", content)
        time.sleep(2)

        # Set to public
        public = pg.query_selector('input[value="1"][name="public"], select[name="public"]')
        if public:
            if public.get_attribute("type") == "radio":
                public.click()
            time.sleep(1)

        # Submit
        submit = pg.query_selector('button#submit, input#submit, button:has-text("Run"), button:has-text("Submit")')
        if submit:
            submit.click(force=True)
            time.sleep(10)
            pg.wait_for_load_state("domcontentloaded", timeout=10000)

        url = pg.url
        if "ideone.com/" in url and url != "https://ideone.com/":
            has_vc = "vestacall" in pg.content().lower()
            print(f"    URL: {url}")
            print(f"    vestacall: {has_vc}")
            return url, has_vc
    except Exception as e:
        print(f"    Error: {str(e)[:80]}")
    return None, False

def try_controlc(pg, content, title):
    """controlc.com — no account paste"""
    print("\n  [controlc.com]")
    try:
        pg.goto("https://controlc.com/", timeout=30000)
        pg.wait_for_load_state("domcontentloaded", timeout=15000)
        time.sleep(3)

        # Title
        title_input = pg.query_selector('input#title, input[name="title"]')
        if title_input:
            title_input.fill(title)
            time.sleep(1)

        # Content
        ta = pg.query_selector('textarea#content, textarea[name="content"], textarea#input_text')
        if ta:
            ta.fill(content)
            time.sleep(2)

        # Submit
        submit = pg.query_selector('button:has-text("Save"), button:has-text("Create"), input[type="submit"]')
        if submit:
            submit.click(force=True)
            time.sleep(8)
            pg.wait_for_load_state("domcontentloaded", timeout=10000)

        url = pg.url
        if "controlc.com/" in url and url != "https://controlc.com/":
            has_vc = "vestacall" in pg.content().lower()
            print(f"    URL: {url}")
            print(f"    vestacall: {has_vc}")
            return url, has_vc
    except Exception as e:
        print(f"    Error: {str(e)[:80]}")
    return None, False


# ============================================================
# MAIN
# ============================================================
PLATFORMS = [
    ("dpaste.org", try_dpaste, 60),
    ("justpaste.it", try_justpaste, 65),
    ("rentry.co", try_rentry, 45),
    ("paste.mozilla.org", try_paste_mozilla, 85),
    ("paste.gg", try_paste_gg, 40),
    ("ideone.com", try_ideone, 75),
    ("controlc.com", try_controlc, 50),
]

pw, browser = get_browser(config, headed_override=True)
verified = 0
new_domains = []

for platform_name, platform_func, da in PLATFORMS:
    ctx, pg = new_page(browser, config, site_name=f"paste-{platform_name}")

    # Rotate content for each platform
    content_idx = PLATFORMS.index((platform_name, platform_func, da)) % len(PASTE_CONTENTS)
    content = PASTE_CONTENTS[content_idx]

    try:
        url, has_vc = platform_func(pg, content["content"], content["title"])

        if url:
            status = "success" if has_vc else "partial"
            log_result(f"Paste-{platform_name}", url, status,
                      f"DA {da} — {'vestacall verified' if has_vc else 'posted, verify link'}")
            if has_vc:
                verified += 1
                new_domains.append(platform_name)
                print(f"    === VERIFIED (DA {da}) ===")
            else:
                print(f"    Posted (verify manually)")
        else:
            print(f"    Failed to get URL")
            log_result(f"Paste-{platform_name}", "", "failed", f"DA {da} — could not publish")

    except Exception as e:
        print(f"    Platform error: {str(e)[:80]}")
    finally:
        ctx.close()

    time.sleep(3)

browser.close()
pw.stop()

print(f"\n{'='*60}")
print(f"NEW PASTE PLATFORMS: {verified}/{len(PLATFORMS)} verified")
print(f"New referring domains: {new_domains}")
print(f"{'='*60}")
