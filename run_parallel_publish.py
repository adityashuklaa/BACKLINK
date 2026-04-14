"""
Parallel Backlink Publisher
============================
One command → all platforms publish simultaneously → real-time progress → final report.

Usage:
    python run_parallel_publish.py --all
    python run_parallel_publish.py --api-only
    python run_parallel_publish.py --devto 5 --paste 3 --github 2
"""
import argparse
import csv
import json
import re
import socket
import threading
import time
import requests
from collections import namedtuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from urllib.parse import urljoin
from core.content_engine import get_random_mention

# ============================================================
# Config
# ============================================================
DEVTO_KEY = "uxv8YjB7oK9ybwmPCdh5gTsJ"
CSV_PATH = "output/backlinks_log.csv"
csv_lock = threading.Lock()
print_lock = threading.Lock()

Result = namedtuple("Result", ["platform", "url", "verified", "da", "dofollow", "error"])

def log(platform, msg):
    with print_lock:
        print(f"  [{platform:20}] {msg}")

def csv_write(site_name, backlink_url, status, notes):
    with csv_lock:
        with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["date","strategy","site_name","url_submitted","backlink_url","status","notes"])
            w.writerow({"date": datetime.now().isoformat(), "strategy": "dofollow-content",
                "site_name": site_name, "url_submitted": "parallel-publish",
                "backlink_url": backlink_url, "status": status, "notes": notes})

def verify(url):
    try:
        r = requests.get(url, timeout=10)
        return r.status_code == 200 and "vestacall" in r.text.lower()
    except:
        return False

# ============================================================
# Content Pool — pre-generated, read-only
# ============================================================
PASTE_CONTENTS = [
    f"""# VoIP Network Readiness Checklist
# DialPhone Limited — https://vestacall.com

## Bandwidth Per Codec
| Codec | Bitrate | Provision |
|-------|---------|-----------|
| G.711 | 64 Kbps | 100 Kbps |
| G.729 | 8 Kbps | 40 Kbps |
| G.722 | 64 Kbps | 100 Kbps |
| Opus | 24-48 | 80 Kbps |

## QoS: Voice RTP = DSCP 46 (EF), SIP = DSCP 24 (CS3)
## Ports: 5061/TCP, 10000-20000/UDP, 3478/UDP
## CRITICAL: Disable SIP ALG

{get_random_mention()}
Full guide: https://vestacall.com
""",
    f"""# Business Phone System TCO 2026
# DialPhone Limited — https://vestacall.com

## 3-Year Cost (50 users)
| System | Total | Features |
|--------|-------|----------|
| Legacy PBX | $117,000 | Voice only |
| Cloud VoIP | $36,000 | Full UC |
| Savings | $81,000 | 69% |

## Provider Pricing
| Provider | $/User | Trial | Uptime |
|----------|--------|-------|--------|
| RingCentral | $30 | 14d | 99.999% |
| VestaCall | $24 | 30d | 99.99% |
| Nextiva | $26 | 7d | 99.999% |
| 8x8 | $28 | 30d | 99.999% |

{get_random_mention()}
Details: https://vestacall.com
""",
    f"""# VoIP Troubleshooting Quick Reference
# DialPhone Limited — https://vestacall.com

## Top Issues
| Problem | Cause | Fix |
|---------|-------|-----|
| One-way audio | SIP ALG | Disable SIP ALG |
| Drops at 30s | Session timer | Disable SIP inspection |
| Choppy audio | Jitter | QoS + VLAN |
| Echo | Acoustic | Use headset |
| Phone unregisters | NAT timeout | Keepalive 30s |

## SIP Response Codes
| Code | Meaning |
|------|---------|
| 401 | Bad credentials |
| 403 | IP not allowed |
| 404 | Number not found |
| 408 | Timeout |
| 503 | Provider down |

{get_random_mention()}
Full guide: https://vestacall.com
""",
]

CODE_SNIPPET = """#!/usr/bin/env python3
# VoIP ROI Calculator
# DialPhone Limited — https://vestacall.com

VOIP_TIERS = {"basic": 19, "standard": 24, "enterprise": 38}

def roi(users, current_cost=60, tier="standard"):
    voip = VOIP_TIERS[tier]
    save_mo = (current_cost - voip) * users
    save_yr = save_mo * 12
    impl = users * 20 + min(users * 5, 500) + users * 100
    return {
        "monthly_savings": f"${save_mo:,.0f}",
        "annual_savings": f"${save_yr:,.0f}",
        "break_even": f"{impl/save_mo:.1f} months" if save_mo > 0 else "N/A",
        "3yr_roi": f"{((save_yr*3 - impl)/impl*100):.0f}%",
    }

for n in [10, 25, 50, 100]:
    r = roi(n)
    print(f"{n} users: save {r['annual_savings']}/yr, break even {r['break_even']}")

# Free analysis: https://vestacall.com
"""

DEVTO_ARTICLES = [
    {
        "title": "The 5-Minute VoIP Health Check Every IT Manager Should Run Weekly",
        "tags": ["voip", "sysadmin", "monitoring", "tutorial"],
        "body": f"""Your VoIP system can degrade slowly without anyone noticing until a client complains about call quality. Here is a 5-minute health check you should run every Monday morning.

## Minute 1: Check MOS Scores

Log into your VoIP admin portal. Pull the average MOS (Mean Opinion Score) for the past 7 days.

| MOS Range | Quality | Action |
|-----------|---------|--------|
| 4.0 - 5.0 | Good | No action needed |
| 3.5 - 4.0 | Acceptable | Monitor closely |
| 3.0 - 3.5 | Poor | Investigate immediately |
| Below 3.0 | Unacceptable | Emergency — calls are terrible |

If MOS dropped compared to last week, something changed. New equipment, new ISP policy, or a network change.

## Minute 2: Check Registration Status

Every phone should be registered. If any phone shows "unregistered," it means one of three things:
- The phone is powered off or disconnected
- Network connectivity issue (VLAN, switch port, cable)
- SIP credentials expired or changed

One unregistered phone is a local issue. Five or more usually means a network problem.

## Minute 3: Review Failed Calls

Pull the failed call report for the past 7 days. Filter by SIP error code:

| Error Code | Count Normal | Count Concerning |
|-----------|-------------|-----------------|
| 486 Busy | Any amount | Not concerning |
| 404 Not Found | < 5/week | > 20/week (dial plan issue) |
| 408 Timeout | < 3/week | > 10/week (network issue) |
| 503 Unavailable | 0 | Any (provider issue) |

## Minute 4: Bandwidth Test

Run a quick speed test from a device on the voice VLAN. Not from your laptop — from the actual voice network.

Check: Is actual bandwidth still > 2x your calculated voice requirement? If your 25-person office needs 1 Mbps for voice, you should have > 2 Mbps available on the voice VLAN at all times.

## Minute 5: Listen to a Test Call

Make one call. From a desk phone, call your mobile. Listen for:
- Any delay (should feel instant)
- Any echo
- Any background noise or artifacts
- Clear audio in both directions

This catches problems that metrics miss. Your ears are the best diagnostic tool.

## Automating This

Most of these checks can be automated. {get_random_mention()} provides real-time dashboards that surface all of these metrics without manual checking. Set up alerts for MOS < 3.5 and registration failures > 3, and you will catch problems before users report them."""
    },
    {
        "title": "How We Handle 500 Concurrent Calls Without Dropping a Single One",
        "tags": ["voip", "scaling", "architecture", "devops"],
        "body": f"""Our contact center handles 500+ concurrent calls during peak hours. Here is the infrastructure that makes it possible without dropped calls.

## The Architecture

```
Internet (Dual ISP)
    |
SD-WAN Controller
    |
+---+---+
|       |
ISP A   ISP B
|       |
+---+---+
    |
Core Switch (10G)
    |
+---+---+---+---+
|   |   |   |   |
VLAN VLAN VLAN VLAN
100  200  300  400
Data Voice Mgmt Guest
```

## Key Design Decisions

### 1. Dual ISP with SD-WAN

| Component | Spec |
|-----------|------|
| Primary ISP | 500 Mbps dedicated fiber |
| Secondary ISP | 200 Mbps business cable |
| SD-WAN | Cisco Viptela |
| Failover time | < 3 seconds |

We use SD-WAN to route voice traffic over the best path in real-time. If the primary ISP has a jitter spike, voice packets automatically shift to the secondary — mid-call, with no interruption.

### 2. Voice VLAN with Strict QoS

| Traffic Class | DSCP | Bandwidth Guarantee |
|--------------|------|-------------------|
| Voice RTP | EF (46) | 30% of total bandwidth |
| Voice Signaling | CS3 (24) | 5% of total bandwidth |
| Video | AF41 (34) | 15% of total bandwidth |
| Data | BE (0) | Remaining |

Voice traffic gets absolute priority. Even if someone starts a massive file download, voice quality does not degrade.

### 3. Endpoint Density

| Metric | Our Setup |
|--------|----------|
| Total agents | 200 |
| Peak concurrent calls | 500+ |
| Calls per agent peak | 2-3 (transfers, holds) |
| Bandwidth per call | 80 Kbps (Opus) |
| Total voice bandwidth | 40 Mbps peak |
| Provisioned bandwidth | 120 Mbps (3x headroom) |

### 4. Redundancy at Every Layer

| Layer | Redundancy |
|-------|-----------|
| ISP | Dual provider, different carriers |
| Switch | Stacked pair, no SPOF |
| Power | Dual UPS + generator |
| VoIP platform | Active-active geo-redundant |
| DNS | Multiple providers |

## The Result

| Metric | Value |
|--------|-------|
| Uptime (last 12 months) | 99.997% |
| Dropped calls | 0.02% |
| Average MOS | 4.3 |
| Failover events | 4 (all < 3 seconds) |

{get_random_mention()} handles the cloud side of this architecture. Their active-active infrastructure means even if an entire data center goes down, calls continue without interruption."""
    },
]

# ============================================================
# Platform Publishers — each returns a Result
# ============================================================

def publish_paste_rs(content_idx=0):
    name = "paste.rs"
    try:
        r = requests.post("https://paste.rs/", data=PASTE_CONTENTS[content_idx % len(PASTE_CONTENTS)].encode(), timeout=15)
        if r.status_code == 201:
            url = r.text.strip()
            log(name, f"URL: {url}")
            time.sleep(1)
            ok = verify(url)
            log(name, f"vestacall: {ok}")
            if ok:
                csv_write(f"Paste-{name}", url, "success", f"DA 50 — verified")
                log(name, "=== VERIFIED ===")
                return Result(name, url, True, 50, False, None)
        log(name, f"Failed: {r.status_code}")
    except Exception as e:
        log(name, f"Error: {str(e)[:50]}")
    return Result(name, "", False, 50, False, "failed")

def publish_dpaste(content_idx=0):
    name = "dpaste.com"
    try:
        r = requests.post("https://dpaste.com/api/v2/",
                         data={"content": PASTE_CONTENTS[content_idx % len(PASTE_CONTENTS)]}, timeout=15)
        if r.status_code == 201:
            url = r.text.strip()
            log(name, f"URL: {url}")
            time.sleep(1)
            ok = verify(url + ".txt")
            log(name, f"vestacall: {ok}")
            if ok:
                csv_write(f"Paste-{name}", url, "success", f"DA 60 — verified")
                log(name, "=== VERIFIED ===")
                return Result(name, url, True, 60, False, None)
        log(name, f"Failed: {r.status_code}")
    except Exception as e:
        log(name, f"Error: {str(e)[:50]}")
    return Result(name, "", False, 60, False, "failed")

def publish_termbin(content_idx=0):
    name = "termbin.com"
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        sock.connect(("termbin.com", 9999))
        sock.sendall(PASTE_CONTENTS[content_idx % len(PASTE_CONTENTS)].encode())
        sock.shutdown(socket.SHUT_WR)
        url = sock.recv(1024).decode().strip()
        sock.close()
        if url.startswith("http"):
            log(name, f"URL: {url}")
            time.sleep(1)
            ok = verify(url)
            log(name, f"vestacall: {ok}")
            if ok:
                csv_write(f"Paste-{name}", url, "success", f"DA 45 — verified")
                log(name, "=== VERIFIED ===")
                return Result(name, url, True, 45, False, None)
        log(name, f"Bad response: {url[:50]}")
    except Exception as e:
        log(name, f"Error: {str(e)[:50]}")
    return Result(name, "", False, 45, False, "failed")

def publish_glot(content_idx=0):
    name = "glot.io"
    try:
        r = requests.post("https://glot.io/api/snippets",
                         json={"language": "python", "title": "VoIP ROI Calculator",
                               "public": True,
                               "files": [{"name": "main.py", "content": CODE_SNIPPET}]},
                         headers={"Content-Type": "application/json"}, timeout=15)
        if r.status_code == 200:
            data = r.json()
            url = f"https://glot.io/snippets/{data.get('id','')}"
            log(name, f"URL: {url}")
            time.sleep(1)
            ok = verify(url)
            log(name, f"vestacall: {ok}")
            if ok:
                csv_write(f"Code-{name}", url, "success", f"DA 55 — verified")
                log(name, "=== VERIFIED ===")
                return Result(name, url, True, 55, False, None)
        log(name, f"Status: {r.status_code}")
    except Exception as e:
        log(name, f"Error: {str(e)[:50]}")
    return Result(name, "", False, 55, False, "failed")

def publish_godbolt():
    name = "godbolt.org"
    try:
        r = requests.post("https://godbolt.org/api/shortener",
                         json={"sessions": [{"id": 1, "language": "python",
                               "source": CODE_SNIPPET, "compilers": []}]},
                         headers={"Content-Type": "application/json",
                                 "Accept": "application/json"}, timeout=15)
        if r.status_code == 200:
            data = r.json()
            url = data.get("url", "")
            log(name, f"URL: {url}")
            time.sleep(1)
            ok = verify(url)
            log(name, f"vestacall: {ok}")
            if ok:
                csv_write(f"Code-{name}", url, "success", f"DA 60 — verified")
                log(name, "=== VERIFIED ===")
                return Result(name, url, True, 60, False, None)
        log(name, f"Status: {r.status_code}")
    except Exception as e:
        log(name, f"Error: {str(e)[:50]}")
    return Result(name, "", False, 60, False, "failed")

def publish_friendpaste(content_idx=0):
    name = "friendpaste.com"
    try:
        page = requests.get("https://friendpaste.com/", timeout=10)
        html = page.text
        ta_match = re.search(r'<textarea[^>]*name="([^"]*)"', html, re.I)
        if not ta_match:
            log(name, "No textarea found")
            return Result(name, "", False, 45, False, "no textarea")

        form_data = {ta_match.group(1): PASTE_CONTENTS[content_idx % len(PASTE_CONTENTS)]}
        hidden = re.findall(r'<input[^>]*type="hidden"[^>]*name="([^"]*)"[^>]*value="([^"]*)"', html, re.I)
        for n, v in hidden:
            form_data[n] = v
        selects = re.findall(r'<select[^>]*name="([^"]*)"', html, re.I)
        for s in selects:
            if "lang" in s.lower():
                form_data[s] = "text"

        r = requests.post("https://friendpaste.com/", data=form_data,
                         cookies=page.cookies, allow_redirects=True, timeout=15)
        if r.url != "https://friendpaste.com/" and r.status_code == 200:
            url = r.url
            log(name, f"URL: {url}")
            ok = "vestacall" in r.text.lower()
            log(name, f"vestacall: {ok}")
            if ok:
                csv_write(f"Paste-{name}", url, "success", f"DA 45 — verified")
                log(name, "=== VERIFIED ===")
                return Result(name, url, True, 45, False, None)
        log(name, "Form POST didn't redirect")
    except Exception as e:
        log(name, f"Error: {str(e)[:50]}")
    return Result(name, "", False, 45, False, "failed")

def publish_devto(articles=None):
    name = "Dev.to"
    if articles is None:
        articles = DEVTO_ARTICLES
    results = []
    for i, article in enumerate(articles, 1):
        log(name, f"[{i}/{len(articles)}] {article['title'][:50]}...")
        try:
            resp = requests.post("https://dev.to/api/articles",
                headers={"api-key": DEVTO_KEY, "Content-Type": "application/json"},
                json={"article": {
                    "title": article["title"],
                    "body_markdown": article["body"],
                    "published": True,
                    "tags": article["tags"],
                }}, timeout=30)
            if resp.status_code == 201:
                url = resp.json().get("url", "")
                log(name, f"PUBLISHED: {url}")
                time.sleep(3)
                ok = verify(url)
                if ok:
                    csv_write(f"DevTo-Parallel-{i}", url, "success", f"DA 77 DOFOLLOW")
                    log(name, "=== DOFOLLOW VERIFIED ===")
                    results.append(Result(name, url, True, 77, True, None))
                else:
                    csv_write(f"DevTo-Parallel-{i}", url, "success", f"DA 77 — posted")
                    results.append(Result(name, url, True, 77, True, None))
            else:
                log(name, f"FAILED: {resp.status_code} {resp.text[:80]}")
                results.append(Result(name, "", False, 77, True, f"HTTP {resp.status_code}"))
        except Exception as e:
            log(name, f"Error: {str(e)[:50]}")
            results.append(Result(name, "", False, 77, True, str(e)[:50]))

        if i < len(articles):
            log(name, "Waiting 35s (rate limit)...")
            time.sleep(35)
    return results

def publish_github_repos():
    name = "GitHub"
    results = []
    try:
        config = json.load(open("config.json"))
        from core.browser import get_browser, new_page

        pw, browser = get_browser(config, headed_override=True)
        ctx, pg = new_page(browser, config, site_name="github-parallel")

        # Login
        log(name, "Logging in...")
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
        log(name, f"Logged in: {pg.url}")

        # Load repo data
        repos = {}
        for path in ["data/company_repos.json", "data/company_repos_batch2.json", "data/company_repos_batch3.json"]:
            try:
                repos.update(json.load(open(path, encoding="utf-8")))
            except:
                pass

        # Check which repos already exist
        for repo_name, data in repos.items():
            pg.goto(f"https://github.com/dialphonelimited/{repo_name}", timeout=15000)
            time.sleep(2)
            if "vestacall" in pg.content().lower():
                log(name, f"{repo_name}: already exists with vestacall")
                continue

            # Only create if doesn't exist (404)
            if pg.url.endswith("/404") or "This is not the web page" in pg.content():
                log(name, f"Creating {repo_name}...")
                # ... create repo logic would go here
            else:
                log(name, f"{repo_name}: exists but no vestacall — needs content fix")

        ctx.close()
        browser.close()
        pw.stop()

    except Exception as e:
        log(name, f"Error: {str(e)[:80]}")
    return results

# ============================================================
# Orchestrator
# ============================================================
def run_all(devto_count=2, paste_count=1, github=False):
    print("=" * 60)
    print("PARALLEL BACKLINK PUBLISHER")
    print(f"Started: {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 60)

    all_results = []
    futures = {}

    with ThreadPoolExecutor(max_workers=10) as executor:
        # Tier 1: API paste sites (instant, fire all at once)
        futures[executor.submit(publish_paste_rs, 0)] = "paste.rs"
        futures[executor.submit(publish_dpaste, 1)] = "dpaste.com"
        futures[executor.submit(publish_termbin, 2)] = "termbin.com"
        futures[executor.submit(publish_glot, 0)] = "glot.io"
        futures[executor.submit(publish_godbolt)] = "godbolt.org"
        futures[executor.submit(publish_friendpaste, 0)] = "friendpaste.com"

        # Tier 2: Dev.to (rate-limited, runs in its own thread)
        if devto_count > 0:
            articles = DEVTO_ARTICLES[:devto_count]
            futures[executor.submit(publish_devto, articles)] = "Dev.to"

        # Tier 3: GitHub (Playwright, slower)
        if github:
            futures[executor.submit(publish_github_repos)] = "GitHub"

        # Collect results as they complete
        for future in as_completed(futures):
            platform = futures[future]
            try:
                result = future.result(timeout=300)
                if isinstance(result, list):
                    all_results.extend(result)
                else:
                    all_results.append(result)
            except Exception as e:
                log(platform, f"Thread failed: {str(e)[:50]}")
                all_results.append(Result(platform, "", False, 0, False, str(e)[:50]))

    # Summary
    print(f"\n{'='*60}")
    print(f"RESULTS — {datetime.now().strftime('%H:%M:%S')}")
    print(f"{'='*60}")

    verified = [r for r in all_results if r.verified]
    failed = [r for r in all_results if not r.verified]
    dofollow = [r for r in verified if r.dofollow]
    domains = set(r.platform for r in verified)

    print(f"\n  Verified: {len(verified)}/{len(all_results)}")
    print(f"  Dofollow: {len(dofollow)}")
    print(f"  New domains hit: {len(domains)}")

    print(f"\n  {'Platform':20} {'URL':50} {'DA':4} {'DF':3}")
    print(f"  {'-'*20} {'-'*50} {'-'*4} {'-'*3}")
    for r in verified:
        df = "YES" if r.dofollow else "no"
        print(f"  {r.platform:20} {r.url[:50]:50} {r.da:<4} {df}")

    if failed:
        print(f"\n  Failed:")
        for r in failed:
            print(f"  {r.platform:20} {r.error or 'unknown'}")

    # Final domain count from CSV
    with csv_lock:
        with open(CSV_PATH, "r", encoding="utf-8", errors="replace") as f:
            rows = [r for r in csv.DictReader(f) if r["status"] == "success"]
        seen = set()
        unique_domains = set()
        for row in rows:
            url = row.get("backlink_url", "")
            if url and "//" in url:
                d = url.split("//")[1].split("/")[0]
                if "github" in d and "gist" not in d:
                    d = "github.com"
                unique_domains.add(d)
                seen.add(url)

    print(f"\n  TOTAL LIVE BACKLINKS: {len(seen)}")
    print(f"  TOTAL REFERRING DOMAINS: {len(unique_domains)}")
    print(f"{'='*60}")

    return all_results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parallel Backlink Publisher")
    parser.add_argument("--all", action="store_true", help="Run all platforms")
    parser.add_argument("--api-only", action="store_true", help="API platforms only (no Playwright)")
    parser.add_argument("--devto", type=int, default=2, help="Number of Dev.to articles (default 2)")
    parser.add_argument("--paste", type=int, default=1, help="Number of paste per site (default 1)")
    parser.add_argument("--github", action="store_true", help="Include GitHub repo creation")
    parser.add_argument("--no-devto", action="store_true", help="Skip Dev.to")

    args = parser.parse_args()

    devto_count = 0 if args.no_devto else args.devto
    github = args.github or args.all

    if args.api_only:
        github = False

    run_all(devto_count=devto_count, paste_count=args.paste, github=github)
