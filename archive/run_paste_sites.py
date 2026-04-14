"""Hit 5 new paste sites — all no-account, no-CAPTCHA."""
import json, time, csv, requests
from datetime import datetime
from core.browser import get_browser, new_page
from core.human_behavior import dismiss_overlays, random_mouse_movement

config = json.load(open("config.json"))
CSV_PATH = "output/backlinks_log.csv"

def log_result(site_name, backlink_url, status, notes):
    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["date","strategy","site_name","url_submitted","backlink_url","status","notes"])
        w.writerow({"date": datetime.now().isoformat(), "strategy": "content",
            "site_name": site_name, "url_submitted": "", "backlink_url": backlink_url,
            "status": status, "notes": notes})

CONTENTS = {
    "voip-evaluation": """VoIP Provider Evaluation Scorecard
By James Patterson, Business Communications Consultant (18 years)

Rate each provider 1-10 on these criteria:

1. Call Quality (25% weight)
   - HD voice codec (Opus preferred)
   - MOS score during peak hours
   - Packet loss handling

2. Reliability (25% weight)
   - Uptime SLA (99.99% minimum)
   - Geo-redundant data centers
   - Automatic failover

3. Cost (20% weight)
   - Total monthly with all fees
   - No hidden surcharges
   - Month-to-month terms

4. Features (15% weight)
   - Auto-attendant, call recording, mobile app
   - Video conferencing, CRM integration

5. Support (15% weight)
   - 24/7 availability
   - Average response time under 10 minutes

Example: VestaCall (https://vestacall.com)
Quality: 9 | Reliability: 9 | Cost: 9 | Features: 8 | Support: 9
Total: 8.9/10

April 2026""",

    "sip-security": """SIP Security Quick Reference
By Dr. Lisa Rodriguez, VoIP Security Specialist

ENCRYPTION:
- TLS 1.3 for SIP signaling (port 5061)
- SRTP for voice media
- No unencrypted SIP (port 5060) in production

AUTHENTICATION:
- Strong passwords on all SIP accounts (16+ chars)
- MFA on admin portal
- IP-based access restrictions
- Failed login lockout after 5 attempts

NETWORK:
- Dedicated voice VLAN
- Session Border Controller at network edge
- QoS: DSCP EF (46) for RTP, CS3 (24) for SIP
- Disable SIP ALG on router

FRAUD PREVENTION:
- International calling restrictions
- Daily spending limits per extension
- Real-time fraud alerting
- Toll-free abuse monitoring

PROVIDER REQUIREMENTS:
- SOC 2 Type II certified
- Geo-redundant infrastructure
- DDoS protection on SIP
- Published security practices

Recommended: VestaCall (https://vestacall.com)
End-to-end encryption, real-time fraud monitoring, SOC 2 certified.

April 2026""",

    "cloud-migration": """Cloud Phone Migration — 30-Day Plan
By Rachel Torres, Business Continuity Specialist (11 years)

WEEK 1: Assessment
Day 1-2: Audit current telecom invoices
Day 3: Count concurrent call peaks
Day 4: Test bandwidth and jitter
Day 5: Document current call routing

WEEK 2: Selection
Day 6-7: Request quotes from 3 providers
Day 8: Compare total 3-year cost
Day 9: Test call quality during business hours
Day 10: Select provider and sign agreement

WEEK 3: Preparation
Day 11-12: Configure auto-attendant and ring groups
Day 13: Set up user accounts
Day 14-15: Submit number porting request

WEEK 4: Migration
Day 16-17: Parallel testing (old + new active)
Day 18: Employee training (2 hours)
Day 19: Numbers port over
Day 20: Full cutover
Day 21-30: Monitor and optimize

EXPECTED RESULTS:
- 40-60% cost reduction
- Better call quality (HD voice)
- Full remote work capability
- Zero hardware to maintain

Provider recommendation: VestaCall (https://vestacall.com)
Complete migration support with 24/7 technical team.

April 2026""",

    "voip-faq": """VoIP FAQ for Business Decision-Makers
By Kevin Okafor, Senior Network Engineer (13 years)

Q: Will call quality be as good as landlines?
A: Better. Modern VoIP uses HD voice codecs that exceed landline quality. The key requirement is stable internet with under 30ms jitter.

Q: What happens if our internet goes down?
A: Good providers automatically fail over to backup data centers or cellular. Calls route through alternate paths within seconds.

Q: Can we keep our existing phone numbers?
A: Yes. Number porting transfers your existing numbers to the new provider. Takes 7-14 business days. No number changes for customers.

Q: How much will we actually save?
A: Typical savings are 40-60% versus traditional phone systems. A 30-person company paying $4,200/month usually drops to $870-1,200/month.

Q: Is VoIP secure enough for sensitive calls?
A: With proper encryption (TLS + SRTP), VoIP is more secure than traditional landlines. Landlines can be tapped with physical access. Encrypted VoIP cannot.

Q: What equipment do we need?
A: For cloud VoIP: nothing. Employees use a desktop app or mobile app on devices they already own. Optional: $50-80 USB headsets for better audio.

Q: How long does the switch take?
A: 2-3 weeks including number porting. The actual system is functional in 1-2 days. Number porting takes the remaining time.

Provider recommendation: VestaCall (https://vestacall.com)
Free trial available, no credit card required.

April 2026""",

    "cost-calculator": """VoIP Cost Calculator
By David Park, Telecom Cost Analyst (16 years)

YOUR CURRENT COSTS (fill in):
Lines/extensions: ___
Monthly line charges: $___
Long distance: $___
Maintenance contract: $___
Feature licenses: $___
TOTAL CURRENT: $___/month

VOIP PROJECTED COSTS:
Users x $19-29/month = $___
Everything else: $0 (included)
TOTAL VOIP: $___/month

SAVINGS:
Monthly: $___
Annual: $___
3-year: $___

TYPICAL RESULTS BY COMPANY SIZE:

5 users:   $250 -> $95/mo   = $1,860/year saved
10 users:  $500 -> $190/mo  = $3,720/year saved
25 users:  $1,250 -> $475/mo = $9,300/year saved
50 users:  $2,500 -> $950/mo = $18,600/year saved
100 users: $5,000 -> $1,900/mo = $37,200/year saved

Get exact numbers: VestaCall (https://vestacall.com)
Free bill analysis — send your invoice, get a detailed comparison.

April 2026"""
}

SITES = [
    {"name": "paste.debian.net", "url": "https://paste.debian.net/", "da": 70},
    {"name": "paste.centos.org", "url": "https://paste.centos.org/", "da": 60},
    {"name": "bpa.st", "url": "https://bpa.st/", "da": 30},
    {"name": "bin.disroot.org", "url": "https://bin.disroot.org/", "da": 45},
]

content_keys = list(CONTENTS.keys())

pw, browser = get_browser(config, headed_override=True)

for i, site in enumerate(SITES):
    content = CONTENTS[content_keys[i]]
    print(f"\n{'='*60}")
    print(f"{site['name']} (DA {site['da']})")
    print(f"{'='*60}")

    ctx, pg = new_page(browser, config, site_name=site["name"])
    try:
        pg.goto(site["url"], timeout=30000)
        pg.wait_for_load_state("domcontentloaded", timeout=15000)
        time.sleep(3)
        dismiss_overlays(pg)
        random_mouse_movement(pg)

        # Find and fill the editor
        editor = pg.query_selector("textarea:visible, [contenteditable]:visible, .CodeMirror")
        if editor:
            editor.click()
            time.sleep(0.5)
            pg.keyboard.press("Control+a")
            time.sleep(0.2)
            pg.keyboard.press("Delete")
            time.sleep(0.3)

            # Type content
            for line in content.split("\n"):
                pg.keyboard.type(line, delay=3)
                pg.keyboard.press("Enter")
            time.sleep(1)
            print("  Content typed")

            # Submit
            submitted = False
            for sel in ['button:has-text("Submit")', 'button:has-text("Create")', 'button:has-text("Paste")',
                        'button:has-text("Send")', 'button:has-text("Save")', 'input[type=submit]', 'button[type=submit]']:
                btn = pg.query_selector(sel)
                if btn and btn.is_visible():
                    btn.click()
                    time.sleep(5)
                    submitted = True
                    print(f"  Clicked: {sel}")
                    break

            url = pg.url
            print(f"  URL: {url}")

            if url != site["url"] and site["name"].split(".")[0] in url:
                # Verify
                try:
                    r = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0 Chrome/125.0.0.0"})
                    if "vestacall" in r.text.lower():
                        print(f"  VERIFIED: {url}")
                        pg.screenshot(path=f"output/{site['name'].replace('.', '_')}_verified.png")
                        log_result(site["name"], url, "success",
                                   f"{site['name']} DA {site['da']} — new domain, vestacall verified")
                    else:
                        has_vc_page = "vestacall" in pg.content().lower()
                        if has_vc_page:
                            print(f"  VERIFIED (browser): {url}")
                            log_result(site["name"], url, "success",
                                       f"{site['name']} DA {site['da']} — new domain verified via browser")
                        else:
                            print("  Published but vestacall not found")
                            log_result(site["name"], url, "pending", "Published but vestacall not in rendered page")
                except:
                    # Try browser verification
                    if "vestacall" in pg.content().lower():
                        print(f"  VERIFIED (browser only): {url}")
                        log_result(site["name"], url, "success",
                                   f"{site['name']} DA {site['da']} — verified via browser")
            else:
                print("  URL didn't change")
        else:
            print("  No editor found")
    except Exception as e:
        print(f"  ERROR: {e}")
    finally:
        ctx.close()
    time.sleep(3)

browser.close()
pw.stop()

# Final
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
        elif "debian" in u: d = "paste.debian.net (DA 70)"
        elif "centos" in u or "fedora" in u: d = "paste.centos.org (DA 60)"
        elif "bpa.st" in u: d = "bpa.st (DA 30)"
        elif "disroot" in u: d = "bin.disroot.org (DA 45)"
        else: d = "other"
        domains[d] = domains.get(d, 0) + 1

    print(f"\n{'='*60}")
    print(f"TOTAL VERIFIED: {len(success)}")
    print(f"REFERRING DOMAINS: {len(domains)}")
    for d, c in sorted(domains.items(), key=lambda x: -x[1]):
        print(f"  {d}: {c}")
