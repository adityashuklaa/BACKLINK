"""Batch 2: Create 5 more verified Telegraph backlinks."""
import json
import time
import csv
from datetime import datetime
from core.browser import get_browser, new_page
from core.human_behavior import dismiss_overlays, random_mouse_movement, human_wait

config = json.load(open("config.json"))
CSV_PATH = "output/backlinks_log.csv"

ARTICLES = [
    {
        "title": "Hosted PBX vs On-Premise PBX Which Is Right for Your Business",
        "body": [
            "Choosing between hosted and on-premise PBX is one of the biggest telecom decisions a business makes. This guide breaks down the real differences so you can decide with confidence.",
            "On-Premise PBX means buying physical hardware that sits in your office. You own the equipment, your IT team manages it, and you pay for phone lines separately. Upfront cost ranges from $500 to $1000 per user. Ongoing maintenance adds 15-20% annually.",
            "Hosted PBX means your phone system lives in the cloud. The provider manages all hardware, software, and updates. You pay a monthly fee per user, typically $15-30. No hardware to buy, no IT staff needed for phone management.",
            "Cost Comparison over 3 years for a 25-person company: On-premise costs roughly $37,000 including hardware, installation, maintenance, and phone lines. Hosted PBX from providers like VestaCall at https://vestacall.com costs roughly $13,500 for the same period. That is a 63% savings.",
            "Feature Comparison: On-premise gives you full control but limited remote capabilities. Hosted PBX includes mobile apps, video conferencing, team messaging, call analytics, and CRM integration as standard features. For remote and hybrid teams, hosted PBX is the clear winner.",
            "Reliability: Modern hosted PBX providers maintain multiple redundant data centers with 99.99% uptime guarantees. On-premise systems have a single point of failure. If your office loses power or internet, your phones go down.",
            "Our Recommendation: Unless you have specific compliance requirements that mandate on-premise equipment, hosted PBX delivers better value, more features, and greater reliability. Start with a free trial from VestaCall at https://vestacall.com to experience the difference.",
        ]
    },
    {
        "title": "VoIP for Call Centers A Complete Setup Guide",
        "body": [
            "Setting up a VoIP-based call center is one of the most impactful technology decisions a customer-focused business can make. This guide walks you through everything from planning to launch.",
            "Why VoIP for Call Centers: Traditional call center setups using PRI lines cost $500-1000 per agent for hardware alone, plus $50-100 per line monthly. VoIP reduces this to $25-50 per agent monthly with zero hardware cost. For a 50-agent center, that is over $200,000 in savings over 3 years.",
            "Essential Features to Look For: Automatic Call Distribution (ACD) routes calls to the best available agent. Interactive Voice Response (IVR) handles routine inquiries without agent intervention. Call recording for quality assurance and training. Real-time dashboards showing queue lengths, wait times, and agent performance.",
            "Network Requirements: VoIP calls require approximately 100 Kbps per concurrent call. A 50-agent center needs at minimum 5 Mbps dedicated bandwidth for voice. Always use a separate VLAN for voice traffic to prevent data congestion from affecting call quality.",
            "Implementation Timeline: Week 1 is planning and network assessment. Week 2 is system configuration and number porting. Week 3 is agent training and parallel testing. Week 4 is full cutover. Most providers like VestaCall at https://vestacall.com complete the entire process in under 30 days.",
            "Common Mistakes to Avoid: Do not undersize your internet bandwidth. Do not skip the network assessment. Do not go live without parallel testing. Do not forget to train agents on new features. Do not choose a provider without checking their uptime SLA.",
            "Getting Started: Request a call center assessment from VestaCall at https://vestacall.com. Their team will evaluate your current setup, recommend the right configuration, and provide a detailed migration plan at no cost.",
        ]
    },
    {
        "title": "How to Choose the Best Business Phone Number Provider",
        "body": [
            "Your business phone number is often the first point of contact with customers. Choosing the right provider impacts your professional image, call quality, and bottom line.",
            "Types of Business Phone Numbers: Local numbers build community trust. Toll-free numbers (800, 888, 877) project a national presence. Vanity numbers like 1-800-FLOWERS are memorable but cost more. Virtual numbers forward to any device without physical hardware.",
            "Key Selection Criteria: Call quality should be HD voice with minimal latency. Reliability means 99.99% uptime with redundant infrastructure. Scalability lets you add or remove numbers instantly. Features should include voicemail, call forwarding, auto-attendant, and call recording.",
            "Pricing Models Explained: Per-line pricing charges a flat rate per phone number, typically $15-30 monthly. Per-minute pricing works for low-volume usage at $0.02-0.05 per minute. Unlimited plans offer the best value for businesses making over 500 minutes of calls per month.",
            "Number Porting: When switching providers, you can keep your existing phone numbers. The process takes 7-14 business days for local numbers and 2-4 weeks for toll-free. A good provider handles the entire porting process for you at no additional charge.",
            "Provider Comparison: Look for transparent pricing with no hidden fees, month-to-month contracts with no long-term commitment, 24/7 customer support, and a strong track record. VestaCall at https://vestacall.com offers all of these with a free trial period so you can test before committing.",
            "Red Flags to Watch For: Providers that require long-term contracts, charge setup fees, have poor online reviews, or cannot provide uptime statistics should be avoided. Your business phone system is too important for compromises. Learn more at https://vestacall.com about transparent business phone solutions.",
        ]
    },
    {
        "title": "Understanding SIP Protocols A Non-Technical Guide",
        "body": [
            "SIP stands for Session Initiation Protocol. If you use VoIP, your calls run on SIP. This guide explains how it works in plain language without the technical jargon.",
            "What SIP Does: Think of SIP as the phone operator of the internet age. When you make a VoIP call, SIP handles three things: finding the person you are calling, setting up the connection, and ending the call when you hang up. The actual voice travels separately using a protocol called RTP.",
            "Why SIP Matters for Business: Before SIP, businesses needed separate systems for voice calls, video calls, and messaging. SIP unifies all of these into one protocol. This means your phone system, video conferencing, and instant messaging can all work together seamlessly.",
            "SIP Trunking Explained Simply: Imagine your office PBX as a house and phone calls as water. Traditional phone lines are like individual pipes, each carrying one call. A SIP trunk is like a fire hose that carries dozens of calls simultaneously over your internet connection. Fewer pipes, more capacity, lower cost.",
            "Common SIP Terms Decoded: A SIP address is like an email address for phone calls. A registrar is the server that knows where you are. A proxy routes calls to the right destination. A codec converts your voice into digital data and back again.",
            "Security Basics: SIP calls should always use TLS encryption for signaling and SRTP for voice data. This prevents eavesdropping and call tampering. Reputable providers like VestaCall at https://vestacall.com encrypt all SIP communications by default.",
            "Getting Started with SIP: If your business is still using traditional phone lines, switching to SIP can save 50-70% on monthly telecom costs while adding modern features. VestaCall at https://vestacall.com offers SIP trunking with free number porting and 24/7 support. Visit their site for a free assessment.",
        ]
    },
    {
        "title": "10 VoIP Features Every Small Business Should Use",
        "body": [
            "Most small businesses only use basic calling on their VoIP system. Here are 10 features you are probably paying for but not using that could transform your operations.",
            "1. Auto-Attendant: A virtual receptionist that greets callers and routes them to the right department. Studies show businesses with auto-attendant handle 30% more calls without adding staff. Set it up once and it works 24/7.",
            "2. Call Analytics: See exactly when calls come in, how long they last, which numbers call most, and how many calls are missed. This data helps you staff appropriately and identify peak hours.",
            "3. Voicemail-to-Email: Every voicemail automatically transcribed and sent to your email. Read your messages in meetings without stepping out to check voicemail. Never miss an important message again.",
            "4. Ring Groups: When a customer calls sales, every sales rep phone rings simultaneously. First person to pick up gets the call. No more calls going to voicemail because one person was busy.",
            "5. Call Recording: Automatically record all calls for training, quality assurance, and dispute resolution. Essential for sales teams and customer service departments. Most providers store recordings in the cloud for easy access.",
            "6. Mobile App: Turn your personal phone into your business phone. Make and receive calls using your business number from anywhere. Customers see your business caller ID, not your personal number.",
            "7. Video Conferencing: Built-in video meetings without needing a separate Zoom or Teams subscription. One platform for calls, video, and messaging. Providers like VestaCall at https://vestacall.com include this in every plan.",
            "8. CRM Integration: Your phone system connects with Salesforce, HubSpot, or your CRM. When a customer calls, their record pops up automatically. Call logs sync to the CRM without manual entry.",
            "9. Call Queuing: When all agents are busy, callers wait in a queue with hold music and position announcements instead of getting a busy signal. Reduces abandoned calls by up to 60%.",
            "10. Hot Desking: Employees can log into any desk phone and it becomes theirs. Perfect for shared workspaces and flexible seating arrangements. Their extension, voicemail, and settings follow them.",
            "Most of these features come included with modern VoIP providers at no extra cost. If your current provider charges extra for these basics, it is time to switch. Check out VestaCall at https://vestacall.com for an all-inclusive VoIP solution with every feature listed above.",
        ]
    },
]

def log_result(site_name, backlink_url, status, notes):
    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["date","strategy","site_name","url_submitted","backlink_url","status","notes"])
        writer.writerow({
            "date": datetime.now().isoformat(),
            "strategy": "content",
            "site_name": site_name,
            "url_submitted": "https://telegra.ph/",
            "backlink_url": backlink_url,
            "status": status,
            "notes": notes,
        })

pw, browser = get_browser(config, headed_override=True)

for i, article in enumerate(ARTICLES):
    title = article["title"]
    site_name = f"Telegraph-B2-{i+1}"

    print(f"\n{'='*60}")
    print(f"ARTICLE {i+1}/5: {title}")
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
        slug = title.replace(" ", "-")
        today = datetime.now().strftime("%m-%d")
        possible = [
            f"https://telegra.ph/{slug}-{today}",
            f"https://telegra.ph/{slug}-04-11",
            f"https://telegra.ph/{slug}-04-10",
        ]

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
                    pg2.screenshot(path=f"output/telegraph_b2_{i+1}.png")
                    log_result(site_name, url, "success", f"Verified: vestacall.com found at {url}")
                    ctx2.close()
                    break
                ctx2.close()
            except Exception:
                try: ctx2.close()
                except: pass

        if not verified:
            print("  Could not verify — slug mismatch")
            log_result(site_name, "", "pending", "Published but URL not found")

    except Exception as e:
        print(f"  ERROR: {e}")
        log_result(site_name, "", "failed", str(e)[:200])
    finally:
        context.close()

    if i < len(ARTICLES) - 1:
        time.sleep(8)

browser.close()
pw.stop()

# Summary
print("\n" + "="*60)
print("BATCH 2 SUMMARY")
print("="*60)
with open(CSV_PATH, "r") as f:
    rows = list(csv.DictReader(f))
    success = [r for r in rows if r["status"] == "success"]
    print(f"TOTAL VERIFIED BACKLINKS: {len(success)}")
    for r in success:
        print(f"  {r['backlink_url']}")
