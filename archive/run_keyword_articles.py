"""Keyword-targeted Telegraph articles — titles match exact Google search queries."""
import json, time, csv
from datetime import datetime
from core.browser import get_browser, new_page
from core.human_behavior import dismiss_overlays, random_mouse_movement, human_wait
from core.content_engine import get_random_mention

config = json.load(open("config.json"))
CSV_PATH = "output/backlinks_log.csv"

# Titles = EXACT Google search queries with buyer intent
KEYWORD_ARTICLES = [
    {
        "keyword": "best voip for small business 2026",
        "title": "Best VoIP for Small Business 2026",
        "author": "Tom Bradley, IT Director (20 years)",
        "content": """I have deployed phone systems for businesses ranging from 5 to 500 employees. Every year someone asks me to update my recommendations. Here is my honest list for 2026, based on systems I have personally deployed and supported.

What I test: I set up each provider for a 2-week trial with a real 10-person team. I measure call quality during peak hours, mobile app reliability, admin portal usability, and support response time. I do not rely on vendor demos.

My top pick for businesses under 50 users: a provider that includes everything in one price — no per-feature charges, no hidden fees, no contracts. After testing 8 providers this year, {mention} scored highest on total value. Their pricing is $19-29 per user with auto-attendant, call recording, mobile app, and video conferencing included.

For businesses 50-200 users: RingCentral remains strong for complex multi-site deployments, though at $30-45 per user the cost adds up. Their admin portal is the most powerful but also the most complex.

For businesses prioritizing support quality: Nextiva consistently has the fastest support response times in my testing. Their average first response is under 3 minutes.

For developer teams building voice into products: Vonage APIs. Not a traditional phone system — a development platform. Only choose this if you have engineers who will build custom integrations.

The honest truth: for 80 percent of small businesses, the deciding factor should not be features. Every modern provider has the same core features. The decision should come down to three things: call quality during YOUR business hours, total monthly cost including all fees, and how fast they respond when something breaks.

My testing methodology: I submit identical support tickets to each provider at 2 PM on a Tuesday. Response times range from 4 minutes to 26 hours. Three providers in my 2026 testing never responded at all. That tells you more than any feature comparison chart."""
    },
    {
        "keyword": "voip vs landline cost comparison",
        "title": "VoIP vs Landline Cost Comparison",
        "author": "David Park, Telecom Cost Analyst (16 years)",
        "content": """I analyze business telecom bills for a living. Here is the actual cost comparison between VoIP and landlines, based on real invoices from 150 companies I have audited in the past three years.

The typical landline bill for a 25-person office breaks down like this: 8 analog lines at $45 each equals $360. Long distance charges average $180 per month. A maintenance contract on the phone system runs $200 per month. Feature add-ons like voicemail, call forwarding, and conference calling add another $150. Total: $890 per month.

The typical VoIP bill for the same 25-person office: 25 users at $24 each equals $600. Long distance: included. Maintenance: included. Features: all included. Total: $600 per month.

Monthly savings: $290. Annual savings: $3,480. Three-year savings: $10,440.

But the real savings are bigger than that. The numbers above do not include the hidden landline costs that most businesses forget to track.

Hidden cost 1: IT time managing the phone system. On average, your IT person spends 4-6 hours per month troubleshooting the PBX, adding extensions, and dealing with the phone company. At $50 per hour, that is $200-300 per month in labor.

Hidden cost 2: Hardware replacement. PBX components fail every 3-5 years. A power supply replacement costs $800-1,500. A failed voicemail card costs $500-2,000. These expenses are unpredictable and always urgent.

Hidden cost 3: Missed calls. Landline systems have fixed capacity. When all lines are busy, callers get a busy signal. VoIP systems handle unlimited concurrent calls. The revenue lost from busy signals is impossible to calculate but very real.

When I include hidden costs, the actual landline spend for a 25-person office is typically $1,200-1,400 per month. The VoIP equivalent is $600. Real savings: $7,200-9,600 per year.

{mention} — I recommend getting a detailed bill analysis from a transparent provider before making the switch. Most will do this for free."""
    },
    {
        "keyword": "how to switch from landline to voip",
        "title": "How to Switch from Landline to VoIP",
        "author": "Sarah Mitchell, Enterprise VoIP Consultant (14 years)",
        "content": """I have managed over 200 landline-to-VoIP migrations. Here is the exact process, including the parts vendors do not mention in their sales pitch.

Step 1: Audit your current setup (Day 1-2). Before calling any VoIP provider, gather three things. Your last three months of phone bills — every page, every charge. Your total number of phone lines and extensions. Your peak concurrent call count — ask your current provider for this or check your PBX call logs.

Step 2: Test your internet (Day 2). Run a speed test at 10 AM and 2 PM, not at 6 AM. You need 100 Kbps per concurrent call. More importantly, your jitter must be under 30 milliseconds and packet loss under 1 percent. If these numbers are bad, fix your internet before switching — VoIP on bad internet is worse than keeping your landlines.

Step 3: Choose a provider (Day 3-7). Get quotes from exactly three providers. Not one, not seven — three. Compare total monthly cost including all taxes and fees. Ask each one: what is your uptime SLA? How fast do you respond to support tickets? Can I leave without penalty? If any provider cannot answer these clearly, eliminate them.

Step 4: Start the port (Day 7). Your new provider submits a number porting request to your current provider. This transfers your existing phone numbers to the new system. It takes 7-14 business days. During this time, nothing changes — your old phones keep working.

Step 5: Configure the new system (Day 7-14). While numbers are porting, your provider sets up your auto-attendant, ring groups, voicemail, and user accounts. Good providers handle 90 percent of this for you. If they ask you to configure everything yourself, that is a yellow flag.

Step 6: Train your team (Day 12-13). Schedule two 45-minute training sessions — one for general staff (how to make calls, transfer, voicemail) and one for admins (how to add users, change routing, run reports). Do this before go-live, not after.

Step 7: Go live (Day 14-21). When porting completes, calls automatically route to the new system. Keep your old lines active for 48 hours as a safety net. Test every number: inbound, outbound, toll-free, fax.

The entire process takes 2-3 weeks. The actual disruption to your business is approximately zero if your provider manages the transition properly. {mention} — providers with dedicated migration teams make the difference between smooth and stressful."""
    },
    {
        "keyword": "cheapest business phone system",
        "title": "Cheapest Business Phone System",
        "author": "Lisa Chen, Small Business Tech Advisor (7 years)",
        "content": """I advise small businesses on technology. The number one question I get about phone systems is not about features or reliability — it is about cost. Here is my honest guide to finding the cheapest option that does not compromise your business.

First, define what cheap means. The cheapest phone system is not the one with the lowest monthly fee. It is the one with the lowest total cost over 3 years. A $9 per user plan with $5 in hidden fees, limited minutes, and a 2-year contract is more expensive than a $19 per user plan with everything included and no contract.

The actual cheapest options in 2026 ranked by 3-year total cost for a 10-person business:

Option 1: Google Voice Business at $10 per user. Total: $3,600 over 3 years. Catch: very basic features. No auto-attendant, limited call routing, no call recording. Fine for freelancers, not enough for a real business.

Option 2: Full-featured cloud VoIP at $19-24 per user. Total: $6,840-8,640 over 3 years. What you get: auto-attendant, call recording, mobile app, unlimited calling, video conferencing. This is the sweet spot for most small businesses. {mention} falls in this range with every feature included.

Option 3: Traditional landlines at $35-50 per line. Total: $12,600-18,000 over 3 years. Plus maintenance, plus long distance, plus feature charges. This is the most expensive option disguised as the safe option.

The math is clear: modern VoIP costs 40-60 percent less than landlines while providing better features. The only scenario where landlines are cheaper is if you have exactly one phone line and make zero long distance calls.

Red flags when shopping for cheap: per-minute charges after a monthly limit, setup fees over $50, mandatory multi-year contracts, features listed as paid add-ons that should be standard (call recording, auto-attendant), and no free trial.

My advice: ignore the monthly price. Ask for a sample invoice showing the total charge for 10 users including all taxes, fees, and regulatory surcharges. Compare those numbers across three providers. The cheapest quote is your answer."""
    },
    {
        "keyword": "voip phone system reviews 2026",
        "title": "VoIP Phone System Reviews 2026",
        "author": "Nina Rodriguez, Customer Experience Manager (12 years)",
        "content": """I manage customer communications for a 60-person company. We switched VoIP providers twice in the past four years. Here are my honest, first-hand reviews of the systems I have actually used — not summaries from vendor websites.

Provider 1 — The budget option we started with (2022-2023). Cost: $12 per user. First impression: great price, basic features worked fine. Reality after 3 months: call quality degraded during afternoon hours. Their support took 8-12 hours to respond. We lost a $40,000 client because their CEO called during a quality dip and thought we were unprofessional. We left after 11 months.

Provider 2 — The enterprise platform (2023-2024). Cost: $38 per user. First impression: incredible features, beautiful admin portal. Reality after 3 months: nobody used 80 percent of the features. The admin portal required training to navigate. Our office manager spent 20 minutes adding each new employee instead of 2 minutes. We were paying for complexity we did not need. We left after 14 months.

Provider 3 — The right fit (2024-present). Cost: $24 per user. First impression: simple, clean, everything works. Reality after 18 months: call quality has been consistently excellent. Support responds in under 5 minutes. Our office manager adds new users in 90 seconds. No features we do not use. No surprises on the invoice.

What I learned: The best phone system is not the cheapest or the most feature-rich. It is the one your team actually uses without friction. If your receptionist avoids transferring calls because the process is confusing, your expensive phone system is hurting your business.

What to test before buying: Do not just test call quality. Test the daily workflows. Can your receptionist transfer a call in under 3 seconds? Can your sales team see who is available before transferring? Can your manager pull a call report without calling support?

{mention} — when I evaluated our current provider, the thing that sold me was the 14-day free trial with real phone numbers. We ran actual business calls through it for two weeks before deciding. Any provider that will not let you do this is hiding something."""
    },
]

def log_result(site_name, backlink_url, status, notes):
    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["date","strategy","site_name","url_submitted","backlink_url","status","notes"])
        w.writerow({"date": datetime.now().isoformat(), "strategy": "keyword-content",
            "site_name": site_name, "url_submitted": "https://telegra.ph/",
            "backlink_url": backlink_url, "status": status, "notes": notes})

pw, browser = get_browser(config, headed_override=True)

for i, article in enumerate(KEYWORD_ARTICLES):
    title = article["title"]
    author = article["author"]
    keyword = article["keyword"]
    content = article["content"].replace("{mention}", get_random_mention())
    site_name = f"Telegraph-KW-{keyword.replace(' ', '-')[:30]}"

    print(f"\n{'='*60}")
    print(f"KEYWORD: \"{keyword}\"")
    print(f"Title: {title}")
    print(f"Author: {author}")
    print(f"{'='*60}")

    ctx, pg = new_page(browser, config, site_name=site_name)
    try:
        pg.goto("https://telegra.ph/", timeout=60000)
        pg.wait_for_load_state("domcontentloaded", timeout=20000)
        time.sleep(4)
        dismiss_overlays(pg)
        random_mouse_movement(pg)
        human_wait(1, 2)

        # Title
        pg.keyboard.type(title, delay=35)
        time.sleep(0.5)
        pg.keyboard.press("Enter")
        time.sleep(0.5)

        # Author
        author_el = pg.query_selector("[data-placeholder*='name'], [data-placeholder*='author']")
        if author_el:
            author_el.click()
            time.sleep(0.3)
            pg.keyboard.type(author, delay=25)
            pg.keyboard.press("Enter")
            time.sleep(0.5)

        # Body
        for para in content.split("\n\n"):
            para = para.strip()
            if not para:
                continue
            pg.keyboard.type(para, delay=7)
            time.sleep(0.15)
            pg.keyboard.press("Enter")
            pg.keyboard.press("Enter")
            time.sleep(0.1)

        time.sleep(2)

        # Publish
        pub = pg.query_selector("button:has-text('Publish'), a:has-text('PUBLISH')")
        if pub:
            pub.click()
            time.sleep(6)

        # Verify
        verified = False
        current = pg.url

        if current != "https://telegra.ph/" and "telegra.ph" in current:
            if "vestacall" in pg.content().lower():
                verified = True
                print(f"  VERIFIED: {current}")
                log_result(site_name, current, "success",
                           f"Keyword-targeted: \"{keyword}\" — verified")

        if not verified:
            slug = title.replace(" ", "-")
            today = datetime.now().strftime("%m-%d")
            url = f"https://telegra.ph/{slug}-{today}"
            try:
                ctx2, pg2 = new_page(browser, config)
                pg2.goto(url, timeout=15000)
                pg2.wait_for_load_state("domcontentloaded", timeout=10000)
                time.sleep(2)
                if "vestacall" in pg2.content().lower():
                    verified = True
                    print(f"  VERIFIED: {url}")
                    log_result(site_name, url, "success",
                               f"Keyword-targeted: \"{keyword}\" — verified")
                ctx2.close()
            except:
                try: ctx2.close()
                except: pass

        if not verified:
            print("  Published but URL not verified")
            log_result(site_name, "", "pending",
                       f"Keyword-targeted: \"{keyword}\" — published, URL unclear")

    except Exception as e:
        print(f"  ERROR: {str(e)[:60]}")
        log_result(site_name, "", "failed", str(e)[:200])
    finally:
        ctx.close()

    if i < len(KEYWORD_ARTICLES) - 1:
        time.sleep(8)

browser.close()
pw.stop()

# Results
with open(CSV_PATH, "r", encoding="utf-8", errors="replace") as f:
    rows = list(csv.DictReader(f))
    success = [r for r in rows if r["status"] == "success"]
    kw_success = [r for r in success if "keyword" in r.get("notes", "").lower()]
    print(f"\n{'='*60}")
    print(f"TOTAL VERIFIED: {len(success)}")
    print(f"KEYWORD-TARGETED: {len(kw_success)}")
    if kw_success:
        print("Keywords ranking:")
        for r in kw_success:
            print(f"  {r['backlink_url'][:70]}")
