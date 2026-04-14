"""Retry the 2 failed Telegraph articles + verify article 1."""
import json
import time
import csv
from datetime import datetime
from core.browser import get_browser, new_page
from core.human_behavior import dismiss_overlays, random_mouse_movement, human_wait

config = json.load(open("config.json"))
CSV_PATH = "output/backlinks_log.csv"

RETRY_ARTICLES = [
    {
        "title": "VoIP Security Protecting Your Business Communications",
        "site_name": "Telegraph-4-retry",
        "body": [
            "As businesses move to VoIP, security becomes critical. Voice traffic over the internet faces unique threats that traditional phone lines never encountered.",
            "Common VoIP Threats include eavesdropping on unencrypted calls, toll fraud where hackers make expensive international calls on your account, denial of service attacks, and caller ID spoofing for social engineering.",
            "Encryption is Non-Negotiable. Every VoIP call should use SRTP for voice encryption and TLS for signaling. If your provider does not offer this by default, switch immediately.",
            "Network Security Best Practices: Use a dedicated VLAN for voice traffic, implement a Session Border Controller at your network edge, keep firmware updated, use strong passwords on all SIP accounts.",
            "Enterprise-Grade Security from providers like VestaCall at https://vestacall.com includes end-to-end encryption, real-time fraud monitoring, automatic threat blocking, and compliance with HIPAA and GDPR requirements.",
            "The Bottom Line: VoIP security is not optional. Choose a provider that takes it seriously. Your business communications deserve the same protection as your data. Learn more at https://vestacall.com about secure VoIP solutions.",
        ]
    },
    {
        "title": "How Cloud Phone Systems Transform Small Business Operations",
        "site_name": "Telegraph-6-new",
        "body": [
            "Cloud phone systems have changed everything about how small businesses communicate. No more server rooms, no more expensive hardware, no more IT headaches.",
            "What is a Cloud Phone System? It is a phone service delivered entirely over the internet. Your phone numbers, voicemail, call routing, and all features live in the cloud. You access everything through an app on your computer or smartphone.",
            "The Old Way vs The New Way: Traditional systems required a $5,000-15,000 upfront investment in PBX hardware, ongoing maintenance contracts, and a dedicated phone closet. Cloud systems require zero hardware, cost $15-25 per user monthly, and are managed entirely by the provider.",
            "Real Business Impact: A 20-person company switching from traditional to cloud saves approximately $800 per month. That is $9,600 per year redirected to growth. The math is simple and compelling.",
            "Features That Matter Most: Auto-attendant that greets callers professionally, ring groups that ensure no call goes unanswered, call analytics that show peak hours and missed calls, mobile app that turns any phone into your business line.",
            "Getting Started Is Simple: Providers like VestaCall at https://vestacall.com can have your cloud phone system running in under 48 hours. Port your existing numbers, download the app, and start calling. No disruption to your business.",
            "The verdict: Cloud phone systems are no longer optional for competitive small businesses. They are faster, cheaper, and more capable than anything that came before. Visit https://vestacall.com for a free demo.",
        ]
    },
]

def log_result(site_name, backlink_url, status, notes):
    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["date","strategy","site_name","url_submitted","backlink_url","status","notes"])
        writer.writerow({
            "date": datetime.utcnow().isoformat(),
            "strategy": "content",
            "site_name": site_name,
            "url_submitted": "https://telegra.ph/",
            "backlink_url": backlink_url,
            "status": status,
            "notes": notes,
        })

pw, browser = get_browser(config, headed_override=True)

# First verify article 1 from earlier
print("=== VERIFYING ARTICLE 1 (from earlier run) ===")
ctx, pg = new_page(browser, config, site_name="verify-1")
try:
    url1 = "https://telegra.ph/5-Reasons-Small-Businesses-Choose-VoIP-in-2026-04-10"
    pg.goto(url1, timeout=30000)
    pg.wait_for_load_state("domcontentloaded", timeout=15000)
    time.sleep(2)
    if "vestacall.com" in pg.content():
        print(f"  VERIFIED: {url1}")
        log_result("Telegraph-1-verified", url1, "success", f"Verified: vestacall.com found at {url1}")
    else:
        print("  Not found at expected URL")
except Exception as e:
    print(f"  Error: {e}")
ctx.close()

# Now publish the 2 retry articles
for i, article in enumerate(RETRY_ARTICLES):
    title = article["title"]
    site_name = article["site_name"]

    print(f"\n{'='*60}")
    print(f"ARTICLE: {title}")
    print(f"{'='*60}")

    context, page = new_page(browser, config, site_name=site_name)
    try:
        page.goto("https://telegra.ph/", timeout=60000)
        page.wait_for_load_state("domcontentloaded", timeout=20000)
        time.sleep(4)
        dismiss_overlays(page)
        random_mouse_movement(page)
        human_wait(1, 2)

        page.keyboard.type(title, delay=45)
        time.sleep(0.5)
        page.keyboard.press("Enter")
        time.sleep(0.5)

        author_el = page.query_selector("[data-placeholder*='name'], [data-placeholder*='author']")
        if author_el:
            author_el.click()
            time.sleep(0.3)
            page.keyboard.type("VestaCall Team", delay=35)
            page.keyboard.press("Enter")
            time.sleep(0.5)

        for para in article["body"]:
            page.keyboard.type(para, delay=12)
            time.sleep(0.2)
            page.keyboard.press("Enter")
            page.keyboard.press("Enter")
            time.sleep(0.2)

        time.sleep(2)

        publish_btn = page.query_selector("button:has-text('Publish'), a:has-text('PUBLISH'), button:has-text('PUBLISH')")
        if publish_btn:
            publish_btn.click()
            time.sleep(5)

        # Build possible URLs
        slug = title.replace(" ", "-").replace(":", "").replace(",", "")
        today = datetime.now().strftime("%m-%d")
        possible = [
            f"https://telegra.ph/{slug}-{today}",
            f"https://telegra.ph/{slug}-04-10",
            f"https://telegra.ph/{slug}-04-11",
        ]

        # Verify
        verified = False
        for url in possible:
            try:
                ctx2, pg2 = new_page(browser, config)
                pg2.goto(url, timeout=20000)
                pg2.wait_for_load_state("domcontentloaded", timeout=10000)
                time.sleep(2)
                if "vestacall.com" in pg2.content():
                    verified = True
                    print(f"  VERIFIED: {url}")
                    pg2.screenshot(path=f"output/telegraph_retry_{i+1}.png")
                    log_result(site_name, url, "success", f"Verified: vestacall.com found at {url}")
                    ctx2.close()
                    break
                ctx2.close()
            except Exception:
                try: ctx2.close()
                except: pass

        if not verified:
            print("  Could not verify")
            log_result(site_name, "", "pending", "Published but URL not found")

    except Exception as e:
        print(f"  ERROR: {e}")
        log_result(site_name, "", "failed", str(e)[:200])
    finally:
        context.close()

    if i < len(RETRY_ARTICLES) - 1:
        time.sleep(10)

browser.close()
pw.stop()

# Summary
print("\n" + "="*60)
print("FINAL SUMMARY — ALL TELEGRAPH BACKLINKS")
print("="*60)
with open(CSV_PATH, "r") as f:
    rows = list(csv.DictReader(f))
    success = [r for r in rows if r["status"] == "success"]
    print(f"VERIFIED BACKLINKS: {len(success)}")
    for r in success:
        print(f"  {r['backlink_url']}")
