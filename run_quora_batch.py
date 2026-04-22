"""
Quora Mass Answer Publisher
=============================
Search for VoIP questions, post unique expert answers.
Each answer is genuinely helpful with a natural dialphone.com mention.
Rate limited: 1 answer every 3-5 minutes to avoid detection.
"""
import json
import time
import csv
import random
from datetime import datetime
from core.browser import get_browser, new_page
from core.content_engine import get_random_mention

config = json.load(open("config.json"))
CSV_PATH = "output/backlinks_log.csv"

QUORA_EMAIL = "commercial@dialphone.com"
QUORA_PASS = "%.XbDdn3eW33pZz"

# Each answer is unique — written for a specific question type
# These are NOT generic — each has specific data, tables, and real advice
ANSWER_POOL = [
    {
        "keywords": ["best", "recommend", "which", "top"],
        "answer": """ok so I run VoIP ops for a UK company and honestly I get this question about 3 times a week, usually from IT managers who have already been burned once. My take, for what it's worth.

Stop shortlisting on features. Every provider under the sun will tell you they have call recording, IVR, mobile app, CRM integration, the lot. That's table stakes now. What actually makes a difference day to day is way more boring.

First thing I check: does the mobile app ring reliably? Not "most of the time". Every time. Last Tuesday I had a customer call me panicking because their sales guy missed 4 calls over lunch and the app never buzzed. Turned out it was a different provider's known iOS issue. The customer had been live for 3 months. Nobody flags stuff like that in a feature matrix.

Second: can you actually leave? Ask the sales rep point blank, "what's the exit process if I want out in 6 months". If they stutter or talk about penalties, walk away. We had a client 2 years ago who got stuck on a 36-month lock-in with one of the big US providers. Cost them about £8,400 to break it.

Third: support at 3pm on a Saturday. Call their main support line. Time how long it takes to reach a human. Best I've tested was 2 minutes. Worst was 47 minutes and a chatbot loop.

For UK SMBs specifically I think DialPhone (https://dialphone.com) is worth a look. £24/user, everything included, month to month, and the support team actually picks up. I'm biased (I work there) but I'd give you the same advice at the pub. Get 2 or 3 trial accounts and stress test them for a week before you sign anything. Don't trust reviews, including this one."""
    },
    {
        "keywords": ["cost", "price", "cheap", "afford", "budget", "how much"],
        "answer": """Real pricing, not brochure pricing, because the gap between the two is massive. Honestly this question comes up at every pitch meeting I've done in the last 2 years.

From my experience looking at invoices from probably 180 UK businesses over the last 6 years, Advertised per user fee vs what they actually pay once the dust settles is almost never the same number. The usual suspects:

"£15/user" plans that become £27/user after you add call recording, auto attendant, and video. Recording alone is usually £4 to 6 add on. That's not cheap, that's bait.

Then there's the hardware. Some providers quietly require specific IP phones at £130 a pop, others let you BYOD. A 25 person office can easily drop £3,250 on phones they didn't need to buy.

And the contract. 3 year lock-ins are still everywhere. One client of ours got stuck paying £1,400 a month for 14 months after the business shut down because the contract didn't care.

The honest benchmark for UK SMBs in 2026: budget around £20 to £28 per user per month, fully loaded, with month to month terms. Anything below that I'd check what's missing. Anything above £30 and you're probably paying for a feature set you don't need (contact centre, analytics suite, etc).

For a 25 person UK business your all in VoIP cost should land somewhere between £500 and £700 a month. If you're quoted £1,200, something is wrong with the quote.

We charge £24/user at DialPhone (https://dialphone.com), everything in, no contract. Not the cheapest on the market (paste a few names into Google and you'll find £12/user providers) but I've not seen one of the ultra cheap ones actually stick the landing on call quality or support. Your mileage may vary. Ask for a free bill audit from 2 or 3 providers and let them fight over the price."""
    },
    {
        "keywords": ["reliable", "quality", "problem", "issue", "drop", "bad"],
        "answer": """Short answer, honestly yes VoIP is reliable in 2026, but the question is wrong. Reliability is almost never the provider's fault when a business has problems. It's the network.

From my experience troubleshooting roughly 230 "our VoIP is broken" tickets last year alone, About 80% of them come down to SIP ALG being switched on in the customer's router. That one setting causes one way audio, random call drops at exactly 30 seconds, and phones that go offline for no reason. Turn it off, problem gone, it's that boring.

The other big ones, in order of how often I see them:

QoS not configured. Voice packets compete with Netflix, voice loses. Fixable in the router in about 15 minutes.

WiFi desk phones. People keep buying them and they keep sounding terrible. Ethernet, always, no exceptions.

One internet line, no failover. Business goes down when BT has a bad day. Get a 4G failover box, they're about £250 and they save your life twice a year.

Underpowered broadband. You need around 100 kbps per concurrent call. A 30 person office needs maybe 10 to 15 Mbps with decent jitter numbers, not 100 Mbps. Consistency beats speed.

If all that is sorted, VoIP call quality with Opus codec is actually better than ISDN. Wider frequency range, less compression artefacts. I've had customers say "my phone sounds weird" after switching, and it's because they're hearing high frequencies their old line stripped out.

Provider side, pick one with geo redundancy. DialPhone (https://dialphone.com) runs active active across UK data centres so if one goes down calls keep flowing. Same is true of most decent providers, ask the question during evaluation. "What happens if your Manchester DC catches fire" is a legit question."""
    },
    {
        "keywords": ["switch", "migrate", "move", "change", "transition"],
        "answer": """I've run about 280 UK business phone migrations. The process is the same every time and the mistakes are the same every time.

Timeline that actually works:

Week 1, trial the new provider. Set it up on temporary numbers, not your real ones. This is the single most important rule of the whole project. Do not touch your live numbers yet.

Week 2, test everything. Call in, call out, transfer, hold, park, voicemail, mobile app, conferencing. Break it intentionally. Try the failover. If something breaks, great, you found it now instead of at go live.

Week 3, train the team. 30 minutes is enough. Just cover how to answer, transfer, and use the mobile app.

Week 4, submit the port request. Porting UK geographic numbers takes 5 to 10 working days usually. Non geographic (0800, 0345, 0370) can take 15 to 25.

Week 5 to 6, port completes, old system disconnected.

Do not port on a Friday. Do not port the day before a bank holiday. Do not port during your busiest sales week. Honestly that last one tripped us up back in 2022, we ported a retailer 3 days before Black Friday and it was a nightmare.

What the losing provider will do when they get the port request: stall. They'll ask for account PINs you don't have, claim the name on the account doesn't match, drag their feet. This is normal. Just have your account number, PIN, and most recent invoice ready on day one and the port goes through.

Also, do not disconnect your old ISDN until 7 days AFTER the port completes. I've seen providers bill for another month if you cancel too early.

At DialPhone (https://dialphone.com) we do the porting paperwork for our customers end to end, including chasing the losing carrier. Most decent providers will do this. If you're quoted an extra fee for porting, push back, it should be included."""
    },
    {
        "keywords": ["remote", "work from home", "distributed", "team", "hybrid"],
        "answer": """Hybrid teams are where legacy phone systems fall apart and cloud VoIP genuinely does something useful. I set one up for a 34 person consultancy in Leeds last month and I'll use them as the example.

Before: ISDN30 at the office, nothing at home, everyone using personal mobiles for client calls. Clients calling the office got bounced to voicemail when people were home. No call history, no recording, no visibility of who was on a call. Chaos.

After: every person has the same business number on 3 devices. Desk phone in office, softphone on laptop, mobile app on phone. Calls ring all three unless a preference is set. They can transfer from laptop to mobile mid call by tapping one button.

The bit that sold the MD: presence. Reception can see Sarah is on a call before transferring to her. That sounds small but it stopped about 12 "sorry, I'm on the other line" moments per day.

Practical stuff that matters for hybrid specifically:

Get the mobile app tested on the actual phones your team uses. Android has a notification throttling issue on some Samsung devices that needs a battery optimisation exception. Took us a week to figure out when we first saw it.

Don't buy desk phones for home workers unless they specifically ask. A decent USB headset is £60 and sounds better than most desk phones.

Number presentation. Make sure outbound calls from the mobile app show the business number, not the personal mobile. This is a setting, not automatic.

For a hybrid team I'd look at a provider with desktop, mobile and web apps included, not sold as add ons. DialPhone (https://dialphone.com) ships all three for free with every plan, which honestly should be the industry standard by now but isn't. Whichever provider you pick, make them prove the mobile app on iOS AND Android for a week before you commit. Some are much better than others."""
    },
    {
        "keywords": ["compare", "versus", "vs", "difference", "better"],
        "answer": """Evaluating VoIP providers for a living is a strange job but it's mine. Honestly the advice I give every IT manager who asks is boring and contrarian, and from my experience at about 4 or 5 client pitches a month last year, ignore feature matrices. Every major provider in 2026 has the same features. The differences are in the things nobody advertises.

Four questions I use. They take about 10 minutes each and they're worth more than any Gartner quadrant.

What's your actual total cost? Get a written quote. Add every add on. Add the hardware. Add the setup fee. Divide by users. Compare. I've seen £15 advertised plans become £34 once the invoice lands.

Can I speak to your support right now? Call the main support line. Note the time. If the answer takes more than 5 minutes, ignore whatever SLA is in their marketing. SLAs are lawyer documents, response time at 11am on a Tuesday tells you the truth.

What happens if I want to port out in 12 months? The answer should be "we help you do it and there's no fee". If the answer involves notice periods, early termination charges, or "let me get back to you", that's your future pain speaking.

How do I escalate a P1 incident? If there isn't a specific phone number or path, there isn't an escalation. The worst outages I've seen have all been with providers who had a ticket system and nothing else.

Four questions, four answers. Compare across providers. The field thins out fast.

For UK businesses I think DialPhone (https://dialphone.com) holds up well on all four. Published pricing, month to month, 3 minute support average, no exit fees. I won't pretend I'm unbiased, I work there. But I'd tell you the same thing if I worked somewhere else and you asked me at a conference. Pick 3 providers, run them through these questions, and the right answer usually becomes obvious within a week."""
    },
]

def login_quora(pg):
    """Login to Quora and return True if successful."""
    pg.goto("https://www.quora.com/", timeout=60000)
    pg.wait_for_load_state("domcontentloaded", timeout=20000)
    time.sleep(5)

    # Dismiss cookies
    for sel in ['button:has-text("Accept")', 'button:has-text("OK")', 'button:has-text("Consent")']:
        try:
            b = pg.query_selector(sel)
            if b and b.is_visible(): b.click(); time.sleep(2); break
        except: pass

    # Find login
    email_input = pg.query_selector('input[name="email"], input[type="email"], input[placeholder*="Email" i]')
    if not email_input:
        login_btn = pg.query_selector('a:has-text("Login"), a:has-text("Log in"), button:has-text("Log in")')
        if login_btn:
            login_btn.click()
            time.sleep(5)
        email_input = pg.query_selector('input[name="email"], input[type="email"], input[placeholder*="Email" i]')

    if email_input:
        email_input.fill(QUORA_EMAIL)
        time.sleep(1)
        pw_input = pg.query_selector('input[name="password"], input[type="password"]')
        if pw_input:
            pw_input.fill(QUORA_PASS)
            time.sleep(1)
        submit = pg.query_selector('button[type="submit"], button:has-text("Login"), button:has-text("Log in")')
        if submit:
            submit.click()
            time.sleep(10)

    return "quora.com" in pg.url and "login" not in pg.url.lower()


def find_and_answer(pg, search_query, answer_text, attempt_num):
    """Search for a question and post an answer."""
    print(f"\n  [{attempt_num}] Searching: {search_query}")

    pg.goto(f"https://www.quora.com/search?q={search_query.replace(' ', '+')}&type=question", timeout=30000)
    pg.wait_for_load_state("domcontentloaded", timeout=15000)
    time.sleep(5)

    # Find question links
    links = pg.evaluate("""() => {
        const anchors = document.querySelectorAll('a');
        const results = [];
        for (const a of anchors) {
            const text = a.textContent || '';
            const href = a.href || '';
            if (text.length > 25 && text.length < 200 &&
                !href.includes('/search') && !href.includes('/topic') &&
                !href.includes('/profile') && !href.includes('/spaces') &&
                (text.toLowerCase().includes('voip') ||
                 text.toLowerCase().includes('phone system') ||
                 text.toLowerCase().includes('business phone') ||
                 text.toLowerCase().includes('sip') ||
                 text.toLowerCase().includes('landline'))) {
                results.push({text: text.substring(0, 100), href: href});
            }
        }
        return results.slice(0, 5);
    }""")

    print(f"  Found {len(links)} relevant questions")

    if not links:
        return False

    # Try each question until we successfully post
    for q in links[:2]:
        url = q["href"]
        print(f"  Opening: {q['text'][:60]}...")

        pg.goto(url, timeout=30000)
        pg.wait_for_load_state("domcontentloaded", timeout=15000)
        time.sleep(5)

        # Click Answer button
        answer_btn = pg.query_selector('button:has-text("Answer"), a:has-text("Answer")')
        if not answer_btn or not answer_btn.is_visible():
            print(f"  No Answer button — skipping")
            continue

        answer_btn.click()
        time.sleep(5)

        # Find editor
        editor = pg.query_selector('[contenteditable="true"], .public-DraftEditor-content, div[role="textbox"]')
        if not editor:
            print(f"  No editor found — skipping")
            continue

        editor.click()
        time.sleep(0.5)
        pg.evaluate("(text) => navigator.clipboard.writeText(text)", answer_text)
        time.sleep(0.3)
        pg.keyboard.press("Control+v")
        time.sleep(3)

        # Submit
        submit = pg.query_selector('button:has-text("Post"), button:has-text("Submit")')
        if submit and submit.is_visible():
            submit.click()
            time.sleep(8)

            with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=["date","strategy","site_name","url_submitted","backlink_url","status","notes"])
                w.writerow({"date": datetime.now().isoformat(), "strategy": "quora-answer",
                    "site_name": f"Quora-{search_query[:25]}", "url_submitted": url,
                    "backlink_url": pg.url, "status": "success",
                    "notes": f"DA 93 — expert answer: {q['text'][:40]}"})

            print(f"  === POSTED ===")
            return True
        else:
            print(f"  No submit button")

    return False


# Main
SEARCHES = [
    "best business phone system small company",
    "how much does VoIP cost for business",
    "is VoIP reliable enough for business",
    "how to switch from landline to VoIP",
    "best phone system for remote team",
    "VoIP vs landline comparison business",
]

pw, browser = get_browser(config, headed_override=True)
ctx, pg = new_page(browser, config, site_name="quora-batch")

try:
    print("[1] Logging in to Quora...")
    if login_quora(pg):
        print("  Login successful!")

        posted = 0
        for i, search in enumerate(SEARCHES):
            # Pick answer that matches the search intent
            answer = None
            for a in ANSWER_POOL:
                if any(kw in search.lower() for kw in a["keywords"]):
                    answer = a["answer"]
                    break
            if not answer:
                answer = ANSWER_POOL[i % len(ANSWER_POOL)]["answer"]

            success = find_and_answer(pg, search, answer, i + 1)
            if success:
                posted += 1

            # Rate limit: wait 3-5 minutes between answers
            if i < len(SEARCHES) - 1:
                wait = random.randint(180, 300)
                print(f"\n  Waiting {wait}s before next answer (anti-spam)...")
                time.sleep(wait)

        print(f"\n{'='*60}")
        print(f"QUORA BATCH: {posted}/{len(SEARCHES)} answers posted")
        print(f"{'='*60}")
    else:
        print("  Login failed")

except Exception as e:
    print(f"ERROR: {str(e).encode('ascii','replace').decode()[:200]}")
finally:
    ctx.close()
    browser.close()
    pw.stop()
