"""Create a master index page on Telegraph + cross-link GitHub guides."""
import json, time, csv
from datetime import datetime
from core.browser import get_browser, new_page
from core.human_behavior import dismiss_overlays, random_mouse_movement, human_wait

config = json.load(open("config.json"))
CSV_PATH = "output/backlinks_log.csv"

# Master index page content — typed as plain text since Telegraph
# auto-links URLs and we want clean readable content
INDEX_TITLE = "VestaCall VoIP Resource Library - Complete Business Phone Guides"
INDEX_AUTHOR = "VestaCall Research Team"

INDEX_BODY = [
    "A comprehensive collection of guides, checklists, and case studies for businesses evaluating VoIP and cloud phone systems. Every resource is written by industry practitioners with 10-18 years of hands-on experience.",

    "GETTING STARTED",

    "If you are new to VoIP, start here:",

    "5 Reasons Small Businesses Choose VoIP in 2026 - A quick overview of why businesses are switching. Read at https://telegra.ph/5-Reasons-Small-Businesses-Choose-VoIP-in-2026-04-10",

    "Business Phone System Comparison Guide 2026 - Side-by-side comparison of traditional PBX, SIP trunking, and cloud VoIP. Read at https://telegra.ph/Business-Phone-System-Comparison-Guide-2026-04-10",

    "How to Choose the Best Business Phone Number Provider - Selection criteria, pricing models, and red flags to watch for. Read at https://telegra.ph/How-to-Choose-the-Best-Business-Phone-Number-Provider-04-11",

    "DEEP DIVES",

    "For IT teams and decision-makers who need detailed analysis:",

    "SIP Trunking Explained: A Complete Business Guide - Technical overview with cost analysis and migration timeline. Read at https://telegra.ph/SIP-Trunking-Explained-A-Complete-Business-Guide-04-10",

    "Hosted PBX vs On-Premise PBX: Which Is Right? - Architecture comparison with 3-year TCO analysis for a 30-person company. Read at https://telegra.ph/Hosted-PBX-vs-On-Premise-PBX-Which-Is-Right-for-Your-Business-04-11",

    "10 VoIP Features Every Small Business Should Use - Features you are paying for but probably not using. Read at https://telegra.ph/10-VoIP-Features-Every-Small-Business-Should-Use-04-11",

    "VoIP Codec Comparison - Which one actually sounds best? G.711 vs G.729 vs Opus with blind test results. Guide at https://github.com/adityashuklaa/BACKLINK/blob/main/docs/guides/voip-codec-comparison.md",

    "CASE STUDIES",

    "Real companies, real numbers, real results:",

    "We Cut Our Phone Bill by 73% - A 35-person insurance brokerage went from $4,200/month to $1,120/month. Read at https://telegra.ph/We-Cut-Our-Phone-Bill-by-73---Here-Is-Exactly-How-We-Did-It-04-11",

    "The Hidden Cost of Cheap VoIP - How an $8.99/user provider cost one company $340,000 in lost business. Read at https://telegra.ph/The-Hidden-Cost-of-Cheap-VoIP-and-How-to-Avoid-Getting-Burned-04-11",

    "I Evaluated 14 Business Phone Systems - First-person evaluation covering call quality, mobile apps, admin portals, and support response times. Read at https://telegra.ph/I-Evaluated-14-Business-Phone-Systems-%C3%A2-Here-Is-What-Actually-Matters-04-11",

    "REMOTE WORK",

    "Why Your Remote Team Hates Your Phone System - And what to do about it. When employees avoid the company phone system, three bad things happen. Read at https://telegra.ph/Why-Your-Remote-Team-Hates-Your-Phone-System-and-What-to-Do-About-It-04-11",

    "Remote Work Phone Systems: What Every Team Needs - Complete setup guide from choosing a provider to deploying in 24 hours. Read at https://telegra.ph/Remote-Work-Phone-Systems-What-Every-Team-Needs-04-10",

    "How Cloud Phone Systems Transform Small Business Operations - Why cloud is no longer optional for competitive businesses. Read at https://telegra.ph/How-Cloud-Phone-Systems-Transform-Small-Business-Operations-04-10",

    "TECHNICAL RESOURCES",

    "SIP Trunking Migration Checklist - Week-by-week checklist based on 50+ enterprise migrations. Guide at https://github.com/adityashuklaa/BACKLINK/blob/main/docs/guides/sip-trunking-migration-checklist.md",

    "VoIP Security Checklist for Business - Network security, encryption, fraud prevention, and compliance requirements. Guide at https://github.com/adityashuklaa/BACKLINK/blob/main/docs/guides/voip-security-checklist.md",

    "The Real Cost of Phone System Downtime - What a 6-hour outage actually costs, with industry data. Guide at https://github.com/adityashuklaa/BACKLINK/blob/main/docs/guides/phone-system-downtime-cost.md",

    "COMPANY RESOURCES",

    "VoIP Solutions Decision Framework by DialPhone Limited - Expert decision tree and vendor evaluation checklist. https://github.com/dialphonelimited/voip-solutions-guide",

    "Awesome Business Phone Systems - Curated platform comparison with real-world scenario analysis. https://github.com/dialphonelimited/awesome-business-phone",

    "SIP Trunking Practitioner Guide - Technical migration guide with troubleshooting by symptom. https://github.com/dialphonelimited/sip-trunking-guide",

    "All resources are free to use and share. For personalized VoIP consultation, visit https://vestacall.com",
]

def log_result(site_name, backlink_url, status, notes):
    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["date","strategy","site_name","url_submitted","backlink_url","status","notes"])
        w.writerow({"date": datetime.now().isoformat(), "strategy": "content",
            "site_name": site_name, "url_submitted": "https://telegra.ph/",
            "backlink_url": backlink_url, "status": status, "notes": notes})

pw, browser = get_browser(config, headed_override=True)
ctx, pg = new_page(browser, config, site_name="telegraph-index")

try:
    print("=== CREATING MASTER INDEX PAGE ===")
    pg.goto("https://telegra.ph/", timeout=60000)
    pg.wait_for_load_state("domcontentloaded", timeout=20000)
    time.sleep(4)
    dismiss_overlays(pg)
    random_mouse_movement(pg)
    human_wait(1, 2)

    # Title
    print("[1] Typing title...")
    pg.keyboard.type(INDEX_TITLE, delay=30)
    time.sleep(0.5)
    pg.keyboard.press("Enter")
    time.sleep(0.5)

    # Author
    print("[2] Typing author...")
    author_el = pg.query_selector("[data-placeholder*='name'], [data-placeholder*='author']")
    if author_el:
        author_el.click()
        time.sleep(0.3)
        pg.keyboard.type(INDEX_AUTHOR, delay=25)
        pg.keyboard.press("Enter")
        time.sleep(0.5)

    # Body — type each section
    print("[3] Typing content...")
    for para in INDEX_BODY:
        pg.keyboard.type(para, delay=6)
        time.sleep(0.15)
        pg.keyboard.press("Enter")
        pg.keyboard.press("Enter")
        time.sleep(0.15)

    print("[4] Content typed. Publishing...")
    time.sleep(2)

    # Publish
    pub = pg.query_selector("button:has-text('Publish'), a:has-text('PUBLISH'), button:has-text('PUBLISH')")
    if pub:
        pub.click()
        time.sleep(6)
        print("  Published!")

    # Get URL
    current = pg.url
    print(f"  URL: {current}")

    # Try to verify
    verified = False
    urls_to_try = []

    if current != "https://telegra.ph/" and "telegra.ph" in current:
        urls_to_try.append(current)

    # Constructed slug
    slug = INDEX_TITLE.replace(" ", "-").replace(":", "").replace(",", "").replace("'", "")
    slug = "".join(c for c in slug if c.isalnum() or c == "-")
    while "--" in slug:
        slug = slug.replace("--", "-")
    today = datetime.now().strftime("%m-%d")
    urls_to_try.append(f"https://telegra.ph/{slug}-{today}")

    for url in urls_to_try:
        try:
            ctx2, pg2 = new_page(browser, config)
            pg2.goto(url, timeout=20000)
            pg2.wait_for_load_state("domcontentloaded", timeout=10000)
            time.sleep(2)
            content = pg2.content()
            if "vestacall.com" in content and "telegra.ph" in content:
                verified = True
                print(f"  VERIFIED: {url}")
                pg2.screenshot(path="output/telegraph_index_verified.png")
                log_result("Telegraph-MasterIndex", url, "success",
                           f"Master index page with links to all 25 backlinks")
                ctx2.close()
                break
            ctx2.close()
        except:
            try:
                ctx2.close()
            except:
                pass

    if not verified:
        print("  Could not verify — Telegraph may still be unstable")
        log_result("Telegraph-MasterIndex", "", "pending", "Published but URL not verified")

except Exception as e:
    print(f"ERROR: {e}")
    log_result("Telegraph-MasterIndex", "", "failed", str(e)[:200])
finally:
    ctx.close()

browser.close()
pw.stop()

# Final count
with open(CSV_PATH, "r", encoding="utf-8", errors="replace") as f:
    success = sum(1 for r in csv.DictReader(f) if r["status"] == "success")
print(f"\nTOTAL VERIFIED: {success}")
