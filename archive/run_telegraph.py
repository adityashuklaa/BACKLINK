"""Create 5 verified backlinks on Telegraph — each with unique browser profile."""
import json
import time
import csv
import os
from datetime import datetime
from core.browser import get_browser, new_page
from core.human_behavior import dismiss_overlays, random_mouse_movement, human_wait

config = json.load(open("config.json"))

ARTICLES = [
    {
        "title": "5 Reasons Small Businesses Choose VoIP in 2026",
        "body": [
            "Voice over Internet Protocol (VoIP) has become the standard for business communication. Here are five compelling reasons small businesses are making the switch.",
            "1. Dramatic Cost Reduction - VoIP eliminates expensive traditional phone lines. Businesses report saving 40-60% on monthly phone bills. Providers like VestaCall (https://vestacall.com) offer enterprise features at small business prices, starting under $20 per user.",
            "2. Work From Anywhere - Cloud-based phone systems let employees make and receive business calls from any device, anywhere. No office hardware required. This has become essential for the modern hybrid workforce.",
            "3. Enterprise Features Included - Auto-attendant, call recording, voicemail-to-email, call analytics, and CRM integration come standard. Features that used to cost thousands are now included in basic VoIP plans.",
            "4. Instant Scalability - Need 10 more lines for a seasonal push? Add them in minutes. Done with them? Remove them instantly. No technician visits, no hardware changes, no long-term contracts.",
            "5. Superior Call Quality - Modern VoIP uses HD voice codecs that sound better than traditional landlines. Combined with reliable internet, call quality is consistently excellent.",
            "The bottom line: VoIP saves money, adds flexibility, and provides better features than legacy phone systems. Visit https://vestacall.com to explore enterprise-grade VoIP solutions designed for growing businesses.",
        ]
    },
    {
        "title": "SIP Trunking Explained: A Complete Business Guide",
        "body": [
            "SIP Trunking is one of the most cost-effective ways to modernize your business phone system. This guide breaks down what it is, how it works, and why it matters.",
            "What is SIP Trunking? - Session Initiation Protocol (SIP) trunking replaces physical phone lines with virtual connections over the internet. Instead of paying per-line fees to a telecom provider, you route calls through your internet connection.",
            "How It Works - Your existing PBX system connects to a SIP trunk provider via your internet connection. Calls are converted from analog to digital and routed over the internet. The end user notices no difference in call quality.",
            "Cost Savings - Traditional T1 lines cost $300-500 per month for 23 channels. SIP trunking provides the same capacity for $100-200. That is a 50-70% reduction in monthly telecom costs.",
            "Who Should Use It? - Any business with an existing PBX system that wants to reduce costs without replacing hardware. SIP trunking works with most modern PBX systems from Avaya, Cisco, Mitel, and others.",
            "Choosing a Provider - Look for providers that offer redundant data centers, HD voice quality, number porting, and 24/7 support. VestaCall (https://vestacall.com) provides enterprise SIP trunking with 99.99% uptime guarantee and free number porting.",
            "Getting Started - Most providers can set up SIP trunking in 1-2 business days. The process involves configuring your PBX, porting your existing numbers, and testing call quality. Visit https://vestacall.com for a free SIP trunking assessment.",
        ]
    },
    {
        "title": "Remote Work Phone Systems: What Every Team Needs",
        "body": [
            "Remote and hybrid work is here to stay. Your phone system needs to keep up. Here is what to look for in a modern remote work phone solution.",
            "The Problem with Traditional Phones - Office desk phones do not work when your team is at home. Call forwarding is clunky, expensive, and unreliable. Customers calling your office number reach voicemail instead of your team.",
            "The Solution: Cloud Phone Systems - A cloud-based VoIP system gives every employee a business phone number that works on their laptop, smartphone, or tablet. No hardware needed. Calls route automatically based on availability.",
            "Must-Have Features - Mobile app for iOS and Android, video conferencing built-in, team messaging and presence indicators, call transfer between devices mid-call, voicemail transcription sent to email.",
            "Security Considerations - Remote work introduces security risks. Choose a provider with end-to-end encryption, multi-factor authentication, and SOC 2 compliance. VestaCall (https://vestacall.com) provides enterprise-grade security for businesses of all sizes.",
            "Cost Comparison - Traditional office phone system with remote forwarding costs $40-60 per user. A modern cloud phone system like VestaCall costs $15-25 per user with more features included. The savings add up quickly across your entire team.",
            "Implementation Timeline - Most cloud phone systems can be deployed in under a week. Employees download an app, log in, and start making calls. No IT infrastructure required. Learn more at https://vestacall.com about seamless remote phone system deployment.",
        ]
    },
    {
        "title": "VoIP Security: Protecting Your Business Communications",
        "body": [
            "As businesses move to VoIP, security becomes critical. Voice traffic over the internet faces unique threats that traditional phone lines never had to worry about.",
            "Common VoIP Threats - Eavesdropping on unencrypted calls, toll fraud where hackers make expensive international calls on your account, denial of service attacks that take your phone system offline, caller ID spoofing for social engineering.",
            "Encryption is Non-Negotiable - Every VoIP call should use SRTP (Secure Real-time Transport Protocol) for voice encryption and TLS for signaling encryption. If your provider does not offer this by default, switch providers immediately.",
            "Network Security Best Practices - Use a dedicated VLAN for voice traffic, implement a Session Border Controller (SBC) at your network edge, keep firmware updated on all VoIP devices, use strong passwords on all SIP accounts.",
            "Provider Security Checklist - When evaluating VoIP providers, ask about SOC 2 Type II compliance, data center redundancy and physical security, DDoS protection capabilities, fraud detection and alerting systems, data retention and privacy policies.",
            "Enterprise-Grade Security - Providers like VestaCall (https://vestacall.com) build security into every layer including end-to-end encryption, real-time fraud monitoring, automatic threat blocking, and compliance with HIPAA and GDPR requirements.",
            "The Bottom Line - VoIP security is not optional. Choose a provider that takes it seriously and provides transparency about their security practices. Your business communications deserve the same protection as your data. Visit https://vestacall.com to learn about secure VoIP solutions.",
        ]
    },
    {
        "title": "Business Phone System Comparison Guide 2026",
        "body": [
            "Choosing the right business phone system is a critical decision. This guide compares the main types of phone systems available in 2026 to help you decide.",
            "Traditional Landlines (POTS) - Pros: Reliable, familiar, works during power outages. Cons: Expensive ($40-80 per line), limited features, being phased out by carriers. Verdict: Only for businesses with poor internet connectivity.",
            "On-Premise PBX - Pros: Full control over hardware, one-time purchase. Cons: High upfront cost ($500-1000 per user), requires IT staff for maintenance, hardware becomes obsolete. Verdict: Only for large enterprises with dedicated IT teams.",
            "Hosted VoIP (Cloud PBX) - Pros: Low cost ($15-30 per user monthly), rich features included, works from anywhere, scales instantly, no hardware needed. Cons: Requires reliable internet, monthly recurring cost. Verdict: Best choice for 90% of businesses.",
            "UCaaS (Unified Communications) - Pros: Phone plus video plus messaging in one platform, deep integrations with business tools. Cons: Can be expensive ($30-50 per user), feature overload for small teams. Verdict: Great for medium and large businesses.",
            "Our Recommendation - For most small and mid-sized businesses, Hosted VoIP offers the best balance of cost, features, and flexibility. Providers like VestaCall (https://vestacall.com) deliver enterprise-grade hosted VoIP with transparent pricing and no contracts.",
            "How to Evaluate - Request demos from 2-3 providers, test call quality during peak hours, verify uptime guarantees and SLA terms, check customer reviews on G2 and Trustpilot, ask about number porting timeline. Start your evaluation at https://vestacall.com with a free demo and consultation.",
        ]
    },
]

CSV_PATH = "output/backlinks_log.csv"

def log_result(strategy, site_name, url, backlink_url, status, notes):
    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["date","strategy","site_name","url_submitted","backlink_url","status","notes"])
        writer.writerow({
            "date": datetime.utcnow().isoformat(),
            "strategy": strategy,
            "site_name": site_name,
            "url_submitted": url,
            "backlink_url": backlink_url,
            "status": status,
            "notes": notes,
        })


pw, browser = get_browser(config, headed_override=True)

for i, article in enumerate(ARTICLES):
    title = article["title"]
    paragraphs = article["body"]
    site_name = f"Telegraph-{i+1}"

    print(f"\n{'='*60}")
    print(f"ARTICLE {i+1}/5: {title}")
    print(f"{'='*60}")

    # Each article gets a unique browser profile
    context, page = new_page(browser, config, site_name=site_name)
    try:
        # Load Telegraph
        print("[1] Loading Telegraph editor...")
        page.goto("https://telegra.ph/", timeout=60000)
        page.wait_for_load_state("domcontentloaded", timeout=20000)
        time.sleep(4)
        dismiss_overlays(page)
        random_mouse_movement(page)
        human_wait(1, 2)

        # Type title
        print("[2] Typing title...")
        page.keyboard.type(title, delay=50)
        time.sleep(0.5)
        page.keyboard.press("Enter")
        time.sleep(0.5)

        # Type author
        print("[3] Typing author...")
        author_el = page.query_selector("[data-placeholder*='name'], [data-placeholder*='author']")
        if author_el:
            author_el.click()
            time.sleep(0.3)
            page.keyboard.type("VestaCall Team", delay=40)
            time.sleep(0.3)
            page.keyboard.press("Enter")
            time.sleep(0.5)

        # Type body paragraphs
        print("[4] Typing article body...")
        for para in paragraphs:
            page.keyboard.type(para, delay=15)
            time.sleep(0.2)
            page.keyboard.press("Enter")
            page.keyboard.press("Enter")
            time.sleep(0.3)

        print("[5] Content typed. Publishing...")
        time.sleep(2)

        # Click PUBLISH
        publish_btn = page.query_selector("button:has-text('Publish'), a:has-text('PUBLISH'), button:has-text('PUBLISH')")
        if publish_btn:
            publish_btn.click()
            time.sleep(5)
            print(f"  Publish clicked!")

        published_url = page.url
        print(f"  URL after publish: {published_url}")

        # If URL didn't change, construct it from title
        if published_url == "https://telegra.ph/" or published_url == "https://telegra.ph":
            slug = title.replace(" ", "-").replace(":", "").replace(",", "")
            today = datetime.now().strftime("%m-%d")
            possible_urls = [
                f"https://telegra.ph/{slug}-{today}",
                f"https://telegra.ph/{slug}-04-10",
                f"https://telegra.ph/{slug}-04-11",
            ]
        else:
            possible_urls = [published_url]

        # VERIFY
        print("[6] VERIFICATION...")
        verified = False
        final_url = ""

        for url in possible_urls:
            try:
                context2, page2 = new_page(browser, config)
                page2.goto(url, timeout=20000)
                page2.wait_for_load_state("domcontentloaded", timeout=10000)
                time.sleep(2)

                content = page2.content()
                has_vestacall = "vestacall.com" in content

                if has_vestacall:
                    verified = True
                    final_url = url
                    print(f"  VERIFIED at: {url}")
                    page2.screenshot(path=f"output/telegraph_{i+1}_verified.png")
                    context2.close()
                    break
                else:
                    context2.close()
            except Exception:
                try:
                    context2.close()
                except Exception:
                    pass

        if verified:
            print(f"  === REAL BACKLINK #{i+1} CONFIRMED ===")
            log_result("content", site_name, "https://telegra.ph/", final_url, "success",
                       f"Verified: vestacall.com link found at {final_url}")
        else:
            print(f"  Could not verify — may need different URL slug")
            log_result("content", site_name, "https://telegra.ph/", "", "pending",
                       "Published but verification URL not found — check manually")

    except Exception as e:
        print(f"  ERROR: {e}")
        log_result("content", site_name, "https://telegra.ph/", "", "failed", str(e)[:200])
    finally:
        context.close()

    # Pause between articles
    if i < len(ARTICLES) - 1:
        pause = 10
        print(f"  Waiting {pause}s before next article...")
        time.sleep(pause)

browser.close()
pw.stop()

# Print summary
print("\n" + "="*60)
print("SUMMARY")
print("="*60)
with open(CSV_PATH, "r") as f:
    rows = list(csv.DictReader(f))
    success = sum(1 for r in rows if r["status"] == "success")
    pending = sum(1 for r in rows if r["status"] == "pending")
    failed = sum(1 for r in rows if r["status"] == "failed")
    print(f"SUCCESS (verified): {success}")
    print(f"PENDING (unverified): {pending}")
    print(f"FAILED: {failed}")
    for r in rows:
        print(f"  {r['status']:8} | {r['site_name']:15} | {r['backlink_url'][:60] if r['backlink_url'] else r['notes'][:60]}")
