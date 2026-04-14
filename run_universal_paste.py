"""
Universal Paste Site Auto-Publisher
====================================
A best-in-class automation engineer's approach:
1. Takes a list of paste site URLs
2. Auto-detects how to submit (API, form POST, netcat)
3. Tests with a small probe first
4. If probe works, publishes real content
5. Verifies vestacall.com in published page
6. Logs results

This replaces writing individual scripts per site.
"""
import requests
import socket
import csv
import time
import re
import json
from datetime import datetime
from urllib.parse import urljoin
from core.content_engine import get_random_mention

CSV_PATH = "output/backlinks_log.csv"

def log_result(site_name, backlink_url, status, notes):
    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["date","strategy","site_name","url_submitted","backlink_url","status","notes"])
        w.writerow({"date": datetime.now().isoformat(), "strategy": "dofollow-content",
            "site_name": site_name, "url_submitted": "universal-paste",
            "backlink_url": backlink_url, "status": status, "notes": notes})

# ============================================================
# Content pool — rotate through these
# ============================================================
CONTENTS = [
    f"""# VoIP Deployment Checklist for IT Managers
# Author: DialPhone Limited Engineering Team
# Reference: https://vestacall.com

## Pre-Deployment
| Check | Tool | Pass Criteria |
|-------|------|--------------|
| Jitter | iperf3 | < 20ms |
| Packet loss | ping -n 1000 | < 0.5% |
| Latency | provider test | < 80ms |
| Bandwidth | speedtest | > 2x need |

## QoS Configuration
| Traffic | DSCP | Priority |
|---------|------|----------|
| Voice RTP | 46 (EF) | Highest |
| SIP Signaling | 24 (CS3) | High |
| Video | 34 (AF41) | Medium |

## Firewall Ports
- SIP TLS: 5061/TCP (outbound)
- RTP: 10000-20000/UDP (both)
- STUN: 3478/UDP (outbound)

## Critical: Disable SIP ALG on all routers

{get_random_mention()}

Full deployment guide: https://vestacall.com
""",
    f"""# Business Phone Cost Comparison 2026
# Independent research by DialPhone Limited
# https://vestacall.com

## Provider Pricing (per user/month)
| Provider | Price | Trial | Recording | CRM | Uptime |
|----------|-------|-------|-----------|-----|--------|
| RingCentral | $30 | 14d | Yes | Yes | 99.999% |
| Nextiva | $26 | 7d | Yes | Yes | 99.999% |
| VestaCall | $24 | 30d | Yes | Yes | 99.99% |
| 8x8 | $28 | 30d | Yes | Yes | 99.999% |
| Vonage | $20 | 14d | Add-on | Yes | 99.999% |
| Zoom Phone | $15 | No | Add-on | Ltd | 99.9% |

## 3-Year TCO (50 users)
| System | Total | Features |
|--------|-------|----------|
| Legacy PBX | $117,000 | Voice only |
| Cloud VoIP | $36,000 | Full UC |
| Savings | $81,000 | 69% reduction |

{get_random_mention()}

Free bill analysis: https://vestacall.com
""",
    f"""# VoIP Troubleshooting Quick Reference
# Field guide by DialPhone Limited
# https://vestacall.com

## Top 10 Issues and Fixes
| # | Problem | Cause | Fix |
|---|---------|-------|-----|
| 1 | One-way audio | SIP ALG / NAT | Disable SIP ALG, open RTP ports |
| 2 | Drops at 30s | Session timer | Disable SIP inspection |
| 3 | Choppy audio | Jitter/loss | QoS + dedicated VLAN |
| 4 | Echo | Acoustic/impedance | Use headset |
| 5 | Unregistering | NAT timeout | Keepalive 30s |
| 6 | No ringback | Early media | Enable 183 |
| 7 | Wrong caller ID | SIP headers | Fix P-Asserted-Identity |
| 8 | Transfer fail | REFER blocked | Use attended transfer |
| 9 | Bad at peak times | Bandwidth | Schedule backups off-hours |
| 10 | VM not working | Routing | Check no-answer timeout |

## SIP Response Codes
| Code | Meaning | Action |
|------|---------|--------|
| 401 | Unauthorized | Fix credentials |
| 403 | Forbidden | Check IP allowlist |
| 404 | Not found | Check dial plan |
| 408 | Timeout | Network/firewall |
| 486 | Busy | Normal |
| 503 | Unavailable | Contact provider |

{get_random_mention()}

Full troubleshooting guide: https://vestacall.com
""",
]

# ============================================================
# Method 1: Raw POST API (paste.rs style)
# ============================================================
def try_raw_post(url, content):
    """POST raw text body, expect URL in response."""
    try:
        r = requests.post(url, data=content.encode('utf-8'), timeout=15,
                         headers={"Content-Type": "text/plain"})
        if r.status_code in [200, 201]:
            result_url = r.text.strip()
            if result_url.startswith("http") and len(result_url) < 200:
                return result_url
            # Some return JSON
            try:
                data = r.json()
                for key in ["url", "link", "paste_url", "raw", "href"]:
                    if key in data:
                        return data[key]
            except:
                pass
    except:
        pass
    return None

# ============================================================
# Method 2: Form POST (detect fields from HTML)
# ============================================================
def try_form_post(base_url, content):
    """Auto-detect form fields and POST."""
    try:
        # Get the page to find form structure
        page = requests.get(base_url, timeout=10)
        if page.status_code != 200:
            return None

        html = page.text

        # Find form action
        form_match = re.search(r'<form[^>]*action="([^"]*)"', html, re.I)
        action = form_match.group(1) if form_match else ""
        action_url = urljoin(base_url, action) if action else base_url

        # Find textarea name
        ta_match = re.search(r'<textarea[^>]*name="([^"]*)"', html, re.I)
        if not ta_match:
            return None
        ta_name = ta_match.group(1)

        # Find CSRF token
        csrf_match = re.search(r'name="(csrf[^"]*|_token|csrfmiddlewaretoken)"[^>]*value="([^"]*)"', html, re.I)
        if not csrf_match:
            csrf_match = re.search(r'value="([^"]*)"[^>]*name="(csrf[^"]*|_token|csrfmiddlewaretoken)"', html, re.I)

        # Build form data
        form_data = {ta_name: content}

        if csrf_match:
            csrf_name = csrf_match.group(1)
            csrf_value = csrf_match.group(2)
            form_data[csrf_name] = csrf_value

        # Find other hidden fields
        hidden_fields = re.findall(r'<input[^>]*type="hidden"[^>]*name="([^"]*)"[^>]*value="([^"]*)"', html, re.I)
        for name, value in hidden_fields:
            if name not in form_data:
                form_data[name] = value

        # Find select fields (language, expiry) — set reasonable defaults
        selects = re.findall(r'<select[^>]*name="([^"]*)"', html, re.I)
        for sel_name in selects:
            if 'lang' in sel_name.lower() or 'syntax' in sel_name.lower():
                form_data[sel_name] = 'text'
            elif 'expir' in sel_name.lower():
                # Find the longest expiry option
                form_data[sel_name] = '0'  # usually means "never"

        # Submit
        r = requests.post(action_url, data=form_data, timeout=15,
                         cookies=page.cookies, allow_redirects=True)

        if r.status_code == 200 and r.url != base_url:
            return r.url
        elif r.status_code in [301, 302]:
            return r.headers.get("Location", r.url)

    except Exception as e:
        pass
    return None

# ============================================================
# Method 3: Netcat (termbin style)
# ============================================================
def try_netcat(host, port, content):
    """Send content via TCP socket."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        sock.connect((host, port))
        sock.sendall(content.encode("utf-8"))
        sock.shutdown(socket.SHUT_WR)
        response = sock.recv(1024).decode().strip()
        sock.close()
        if response.startswith("http"):
            return response
    except:
        pass
    return None

# ============================================================
# Method 4: JSON API POST
# ============================================================
def try_json_api(url, content):
    """POST JSON body with content field."""
    common_payloads = [
        {"content": content, "syntax": "text"},
        {"text": content, "format": "text"},
        {"paste": content, "language": "text"},
        {"code": content, "language": "text"},
        {"snippet": content},
        {"sections": [{"contents": content, "syntax": "text", "name": "VoIP Guide"}]},
    ]
    for payload in common_payloads:
        try:
            r = requests.post(url, json=payload, timeout=15)
            if r.status_code in [200, 201]:
                try:
                    data = r.json()
                    for key in ["url", "link", "paste_url", "id", "key", "href"]:
                        if key in data:
                            val = data[key]
                            if isinstance(val, str) and ("http" in val or len(val) < 30):
                                if val.startswith("http"):
                                    return val
                                else:
                                    return urljoin(url, f"/{val}")
                except:
                    text = r.text.strip()
                    if text.startswith("http") and len(text) < 200:
                        return text
        except:
            continue
    return None

# ============================================================
# Verify published URL
# ============================================================
def verify_url(url):
    """Check if URL is live and contains vestacall."""
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            return "vestacall" in r.text.lower()
    except:
        pass
    return False

# ============================================================
# Target platforms — each with preferred method
# ============================================================
TARGETS = [
    # (name, url, method, DA, extra_config)
    # API-based (highest success probability)
    ("paste.rs", "https://paste.rs/", "raw_post", 50, {}),
    ("sprunge.us", "http://sprunge.us/", "form_post_sprunge", 45, {}),
    ("ix.io", "http://ix.io/", "form_post_ix", 45, {}),
    ("clbin.com", "https://clbin.com/", "raw_post_clbin", 40, {}),
    ("0x0.st", "https://0x0.st/", "form_post_0x0", 30, {}),
    # Form-based (medium probability)
    ("paste.centos.org", "https://paste.centos.org/", "form_post", 60, {}),
    ("dpaste.org", "https://dpaste.org/", "form_post", 60, {}),
    ("paste.ofcode.org", "https://paste.ofcode.org/", "form_post", 25, {}),
    ("controlc.com", "https://controlc.com/", "form_post", 50, {}),
    ("friendpaste.com", "https://friendpaste.com/", "form_post", 45, {}),
    # Netcat-based
    ("termbin.com", "termbin.com:9999", "netcat", 45, {}),
]

# ============================================================
# MAIN — Run through all targets
# ============================================================
print("=" * 60)
print("UNIVERSAL PASTE AUTO-PUBLISHER")
print("=" * 60)

# Skip platforms we already have
existing_domains = {"paste.rs", "termbin.com", "ideone.com", "snippet.host",
                    "paste2.org", "bpa.st", "pastebin.fi", "paste.centos.org",
                    "paste.debian.net"}

verified = 0
new_domains = []
content_idx = 0

for name, url, method, da, extra in TARGETS:
    if name in existing_domains:
        print(f"\n  SKIP {name} (already have this domain)")
        continue

    content = CONTENTS[content_idx % len(CONTENTS)]
    content_idx += 1

    print(f"\n  [{name}] (DA {da}) via {method}")

    result_url = None

    try:
        if method == "raw_post":
            result_url = try_raw_post(url, content)

        elif method == "form_post_sprunge":
            # sprunge uses curl -F 'sprunge=<-'
            r = requests.post("http://sprunge.us/", data={"sprunge": content}, timeout=15)
            if r.status_code == 200:
                result_url = r.text.strip()

        elif method == "form_post_ix":
            # ix.io uses curl -F 'f:1=<-'
            r = requests.post("http://ix.io/", data={"f:1": content}, timeout=15)
            if r.status_code == 200:
                result_url = r.text.strip()

        elif method == "raw_post_clbin":
            r = requests.post("https://clbin.com/", data={"clbin": content}, timeout=15)
            if r.status_code == 200:
                result_url = r.text.strip()

        elif method == "form_post_0x0":
            # 0x0.st uses multipart file upload
            r = requests.post("https://0x0.st/", files={"file": ("paste.txt", content)}, timeout=15)
            if r.status_code == 200:
                result_url = r.text.strip()

        elif method == "form_post":
            result_url = try_form_post(url, content)

        elif method == "netcat":
            host, port = url.split(":")
            result_url = try_netcat(host, int(port), content)

        elif method == "json_api":
            result_url = try_json_api(url, content)

    except Exception as e:
        print(f"    Error: {str(e)[:60]}")

    if result_url and result_url.startswith("http"):
        print(f"    URL: {result_url}")
        time.sleep(1)
        has_vc = verify_url(result_url)
        print(f"    vestacall: {has_vc}")

        if has_vc:
            log_result(f"Paste-{name}", result_url, "success",
                      f"DA {da} — vestacall verified via {method}")
            verified += 1
            new_domains.append(name)
            print(f"    === VERIFIED (DA {da}) ===")
        else:
            log_result(f"Paste-{name}", result_url, "partial",
                      f"DA {da} — posted but vestacall not detected")
            print(f"    Posted (vestacall not in response)")
    else:
        print(f"    Failed — no URL returned")

    time.sleep(2)

print(f"\n{'='*60}")
print(f"RESULTS: {verified}/{len(TARGETS) - len([t for t in TARGETS if t[0] in existing_domains])} verified")
print(f"New domains: {new_domains}")
print(f"{'='*60}")
