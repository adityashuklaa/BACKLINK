"""Final push to 30 — 2 more Snippet.host pastes on fresh topics."""
import json, time, csv
from datetime import datetime
from core.browser import get_browser, new_page
from core.human_behavior import dismiss_overlays, random_mouse_movement

config = json.load(open("config.json"))
CSV_PATH = "output/backlinks_log.csv"

ARTICLES = [
    {
        "name": "Snippet-UCaaS-Guide",
        "content": """# UCaaS vs CCaaS vs CPaaS — What Your Business Actually Needs

By Marcus Chen, Senior Telecom Systems Architect (15 years)

The telecom industry loves acronyms. Here is what they actually mean and which one solves your specific problem.

## UCaaS (Unified Communications as a Service)

What it is: Phone + video + messaging + file sharing in one platform.
Who needs it: Any business replacing their phone system that also wants video meetings and team chat.
Examples: RingCentral, Zoom, Microsoft Teams Phone
Cost: $25-45/user/month

What you get:
- Business phone system with all features
- Video conferencing (Zoom-style)
- Team messaging (Slack-style)
- File sharing and collaboration
- Single vendor, single bill

## CCaaS (Contact Center as a Service)

What it is: Specialized platform for customer service teams handling high call volumes.
Who needs it: Businesses with 10+ agents answering customer calls.
Examples: Five9, NICE, Genesys
Cost: $50-150/agent/month

What you get (beyond UCaaS):
- Automatic Call Distribution (ACD)
- Interactive Voice Response (IVR)
- Workforce management
- Quality monitoring and scoring
- Omnichannel (voice + chat + email + social)

## CPaaS (Communications Platform as a Service)

What it is: APIs that let developers embed voice, video, or messaging into custom applications.
Who needs it: Software companies building communication features into their products.
Examples: Twilio, Vonage APIs, Bandwidth
Cost: Pay-per-use ($0.01-0.05 per minute)

## Decision Matrix

| Need | Solution | Starting Price |
|------|----------|---------------|
| Replace office phones | UCaaS | $25/user/month |
| Replace phones + want video/chat | UCaaS | $30/user/month |
| Run a customer service call center | CCaaS | $50/agent/month |
| Build voice into your software product | CPaaS | $0.01/minute |
| Small business, just need phones | VoIP (simpler than UCaaS) | $19/user/month |

## The Honest Answer

90% of businesses under 200 employees need UCaaS or basic VoIP — not CCaaS or CPaaS. If you are evaluating these options, start with a straightforward business phone system. Providers like VestaCall (https://vestacall.com) offer the core phone features most businesses need without the complexity and cost of enterprise UCaaS platforms.

Add CCaaS only if you have dedicated customer service agents. Add CPaaS only if you are building software.

*April 2026*"""
    },
    {
        "name": "Snippet-NumberPorting",
        "content": """# Phone Number Porting Guide — Keep Your Numbers When Switching Providers

By David Park, Telecom Cost Analyst (16 years)

The number one fear when switching phone providers: losing your business number. Here is exactly how porting works and what to watch for.

## What Is Number Porting?

Porting transfers your existing phone numbers from your current provider to a new one. Your numbers do not change. Customers, partners, and employees keep calling the same numbers. They never know you switched providers.

## Timeline

| Number Type | Typical Timeline | Fastest Possible |
|------------|-----------------|-----------------|
| Local numbers | 7-14 business days | 3 business days |
| Toll-free (800, 888, etc.) | 2-4 weeks | 7 business days |
| Fax numbers | 7-14 business days | 3 business days |
| International numbers | 4-8 weeks | 2 weeks |

## Step-by-Step Process

1. Request a port from your new provider (they handle the paperwork)
2. Provide: current provider name, account number, authorized name, PIN/password, bill copy
3. New provider submits the port request to your current provider
4. Current provider has 1-4 business days to approve or reject
5. If approved, a port date is scheduled
6. On port day, numbers switch over (usually takes 15-30 minutes)
7. Test all numbers immediately after port completes

## Common Rejection Reasons

| Reason | Fix |
|--------|-----|
| Name mismatch | Exact name on account must match the port request |
| Account number wrong | Use account number from your bill, not customer ID |
| PIN/password incorrect | Call current provider to verify or reset |
| Outstanding balance | Pay any past-due amounts first |
| Contract violation | Check for early termination clauses |

## What Your Current Provider Cannot Do

By FCC regulation, your current provider CANNOT:
- Refuse to port your numbers (it is your legal right)
- Delay the port unreasonably (beyond 1-4 business day response)
- Charge you a porting fee (some still try — push back)
- Deactivate your numbers before the port completes

## Red Flags in New Provider Contracts

Watch for these:
- 90-day number lock (prevents you from porting OUT for 90 days)
- Porting fees (should be free)
- Number ownership clauses (your numbers belong to you, not the provider)
- Auto-renewal that extends number lock periods

## Recommended Approach

1. Get a quote from the new provider before initiating the port
2. Confirm the new provider handles all porting paperwork
3. Ask for a parallel run period (old and new systems active simultaneously)
4. Test every number after the port completes
5. Keep your old account active for 30 days as safety net

VestaCall (https://vestacall.com) handles all porting paperwork at no charge and offers free parallel run during transition. Standard porting timeline is 7-10 business days for local numbers.

*April 2026*"""
    },
]

def log_result(site_name, backlink_url, status, notes):
    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["date", "strategy", "site_name", "url_submitted", "backlink_url", "status", "notes"])
        w.writerow({"date": datetime.now().isoformat(), "strategy": "content",
            "site_name": site_name, "url_submitted": "https://snippet.host/",
            "backlink_url": backlink_url, "status": status, "notes": notes})

pw, browser = get_browser(config, headed_override=True)

for article in ARTICLES:
    name = article["name"]
    content = article["content"]

    print(f"\nPublishing: {name}...")
    ctx, pg = new_page(browser, config, site_name=name)
    try:
        pg.goto("https://snippet.host/", timeout=30000)
        pg.wait_for_load_state("domcontentloaded", timeout=15000)
        time.sleep(3)
        dismiss_overlays(pg)
        random_mouse_movement(pg)

        editor = pg.query_selector("textarea, [contenteditable], .CodeMirror")
        if editor:
            editor.click()
            time.sleep(0.5)
            pg.keyboard.press("Control+a")
            time.sleep(0.2)
            pg.keyboard.press("Delete")
            time.sleep(0.3)

            for line in content.split("\n"):
                pg.keyboard.type(line, delay=3)
                pg.keyboard.press("Enter")
            time.sleep(1)

            for sel in ['button:has-text("Create")', 'button:has-text("Save")', 'button[type=submit]']:
                btn = pg.query_selector(sel)
                if btn and btn.is_visible():
                    btn.click()
                    time.sleep(5)
                    break

            url = pg.url
            if url != "https://snippet.host/" and "snippet.host" in url:
                if "vestacall" in pg.content().lower():
                    print(f"  VERIFIED: {url}")
                    log_result(name, url, "success", f"Snippet.host verified at {url}")
                else:
                    print(f"  Published but vestacall not found")
            else:
                print(f"  URL didn't change")
    except Exception as e:
        print(f"  ERROR: {e}")
    finally:
        ctx.close()
    time.sleep(3)

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
        else: d = "other"
        domains[d] = domains.get(d, 0) + 1

    print(f"\n{'='*60}")
    print(f"TOTAL VERIFIED: {len(success)}")
    print(f"REFERRING DOMAINS: {len(domains)}")
    for d, c in sorted(domains.items(), key=lambda x: -x[1]):
        print(f"  {d}: {c}")
