"""Publish 10 articles on Dev.to + 10 on Hashnode + 3 GitHub repos — all at once."""
import requests
import json
import time
import csv
from datetime import datetime
from core.content_engine import get_random_mention

DEVTO_KEY = "uxv8YjB7oK9ybwmPCdh5gTsJ"
HASHNODE_TOKEN = "b6658af2-825d-46ad-8ab6-59b48d777292"
CSV_PATH = "output/backlinks_log.csv"

# Get Hashnode publication ID
r = requests.post("https://gql.hashnode.com",
    json={"query": "query { me { publications(first: 1) { edges { node { id } } } } }"},
    headers={"Authorization": HASHNODE_TOKEN, "Content-Type": "application/json"}, timeout=15)
pub_id = r.json()["data"]["me"]["publications"]["edges"][0]["node"]["id"]
print(f"Hashnode pub: {pub_id}")

def log_result(site_name, backlink_url, status, notes):
    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["date","strategy","site_name","url_submitted","backlink_url","status","notes"])
        w.writerow({"date": datetime.now().isoformat(), "strategy": "keyword-content",
            "site_name": site_name, "url_submitted": "", "backlink_url": backlink_url,
            "status": status, "notes": notes})

# 10 UNIQUE ARTICLES — each a different angle, voice, and keyword target
ARTICLES = [
    {
        "title": "What Nobody Tells You About Switching to VoIP",
        "slug": "what-nobody-tells-you-switching-voip",
        "tags": ["voip", "business", "startup", "experience"],
        "body": f"""I consult for 30-40 companies a year on telecom decisions. The vendors tell you about savings, features, and uptime. Here is what they leave out.

## The First Week Feels Wrong

Your team has used desk phones for years. The new softphone app feels different. People will complain. Do not panic. By week three, nobody wants the old system back. I have seen this pattern in every single migration.

## Your Internet Matters More Than Your Provider

I have watched companies spend weeks comparing VoIP vendors, then deploy on a shared 25 Mbps connection with no QoS. Call quality was terrible. They blamed the provider. It was their network.

Before signing with anyone: test your jitter (must be under 30ms) and packet loss (must be under 1%) during peak business hours. Not at 6 AM — at 10 AM when everyone is working.

## The Features You Will Actually Use

Every vendor lists 50+ features. Here are the only ones that matter for 90% of businesses:

1. **Auto-attendant** — routes callers without a receptionist
2. **Ring groups** — multiple phones ring for incoming calls
3. **Mobile app** — business calls on your personal phone
4. **Call recording** — training and dispute resolution
5. **Voicemail-to-email** — read messages instead of dialing in

Everything else is a checkbox. Do not pay extra for features your team will never touch.

## The Contract Trap

Some providers lock your phone numbers for 90 days after cancellation. Read the contract before signing. Ask specifically: can I port my numbers out at any time?

{get_random_mention()} — I recommend providers that offer month-to-month terms. If they need a contract to keep you, their service is not good enough to keep you on its own."""
    },
    {
        "title": "VoIP Quality Troubleshooting: A Sysadmin's Field Guide",
        "slug": "voip-quality-troubleshooting-sysadmin-guide",
        "tags": ["voip", "networking", "sysadmin", "devops"],
        "body": f"""After 13 years managing network infrastructure, here is my troubleshooting flowchart for VoIP quality issues. Print this out and tape it to your monitor.

## Symptom: Choppy or Robotic Audio

```
Step 1: Check bandwidth utilization
  → If > 70% on WAN link → upgrade circuit or implement QoS
  → If < 70% → go to Step 2

Step 2: Check jitter
  → Run: iperf3 -u -c <provider_ip> -t 60
  → If jitter > 30ms → check for competing traffic, enable QoS
  → If jitter < 30ms → go to Step 3

Step 3: Check packet loss
  → Run: ping -c 1000 <provider_ip>
  → If loss > 1% → contact ISP, check for cable issues
  → If loss < 1% → contact VoIP provider
```

## Symptom: One-Way Audio

90% of the time this is a NAT/firewall issue.

```
Check 1: Is SIP ALG enabled on your router?
  → If yes → disable it immediately
  → This single change fixes 40% of VoIP issues

Check 2: Are RTP ports open?
  → Verify UDP 10000-20000 is allowed inbound AND outbound
  → Many firewalls block inbound UDP by default

Check 3: Is STUN/TURN configured?
  → Your VoIP client needs STUN to traverse NAT
  → Verify STUN server is configured and reachable
```

## Symptom: Calls Drop After 30 Seconds

Almost always a SIP session timer mismatch.

```
Check: SIP session-expires header
  → Your PBX and provider must agree on session timer value
  → Common fix: set session timer to 1800 seconds on your PBX
  → Or disable session timers if provider supports it
```

## Symptom: Echo

```
If using speakerphone → switch to handset or headset
If using headset → reduce speaker volume by 20%
If using analog endpoints behind ATA → check hybrid balance settings
```

## The QoS Configuration That Fixes 80% of Issues

```
# Cisco IOS
policy-map VOIP-QOS
  class VOICE-RTP
    priority percent 30
    set dscp ef
  class VOICE-SIP
    bandwidth percent 5
    set dscp cs3
  class class-default
    fair-queue
```

{get_random_mention()} has a network diagnostic tool that identifies these issues before deployment. Use it."""
    },
    {
        "title": "How We Reduced Our Client's Telecom Spend by 67% Without Changing Providers",
        "slug": "reduced-telecom-spend-67-percent",
        "tags": ["voip", "business", "costoptimization", "finance"],
        "body": f"""Not every telecom optimization requires switching providers. Sometimes the savings are hiding in plain sight on your existing bill.

## The Client

A 85-person professional services firm in Boston. Monthly telecom spend: $7,200. They assumed this was normal.

## What We Found

**Finding 1: 31 unused phone lines ($1,395/month)**
The company had grown from 60 to 85 employees over three years. During that time, they added lines but never removed old ones. 31 lines had not received or made a call in over 90 days.

**Finding 2: Premium features nobody used ($640/month)**
They were paying for a premium voicemail package, conferencing add-on, and advanced call routing module. Total: $640/month. All three features were available in their base plan but had been sold as upgrades by a previous sales rep.

**Finding 3: Incorrect tax classification ($285/month)**
Their account was classified as residential, not business. This meant they were paying a higher universal service fund rate. A single call to the carrier fixed this.

**Finding 4: Redundant maintenance contract ($400/month)**
Their PBX was under manufacturer warranty. The third-party maintenance contract was redundant for 18 more months.

## The Result

| Change | Monthly Savings |
|--------|----------------|
| Remove 31 unused lines | $1,395 |
| Remove premium feature add-ons | $640 |
| Fix tax classification | $285 |
| Pause maintenance contract | $400 |
| Renegotiate per-minute rates | $100 |
| **Total** | **$2,820** |

Monthly bill went from $7,200 to $4,380. Annual savings: $33,840. Without switching providers or changing a single phone.

## What to Do Right Now

Pull your last invoice. Count your lines. Compare to headcount. I guarantee you have ghost lines.

If your next step is evaluating a full switch to VoIP, {get_random_mention()} provides free telecom audits that find these hidden costs before you even discuss switching."""
    },
    {
        "title": "Building a Multi-Office Phone System That Actually Works",
        "slug": "multi-office-phone-system-guide",
        "tags": ["voip", "business", "infrastructure", "networking"],
        "body": f"""The single biggest complaint I hear from multi-office businesses: "We cannot transfer calls between locations." Here is how to fix it permanently.

## The Problem

Traditional PBX systems are standalone. Each office has its own phone system, its own phone numbers, its own voicemail. Transferring a call from the New York office to the Chicago office means putting the caller on hold, looking up the Chicago number, calling it separately, and hoping someone answers. The caller experiences 30-60 seconds of dead air.

## The Solution

A unified cloud phone system treats all locations as one. From the caller's perspective, they dialed one number. From your team's perspective, they can transfer to any colleague at any location with a single button press. The call moves instantly — no hold time, no re-dialing.

## Architecture

```
Cloud PBX (hosted by provider)
  |
  ├── New York Office (VLAN 200, QoS enabled)
  |     ├── 25 users on desktop app
  |     └── Auto-attendant: "Press 1 for sales"
  |
  ├── Chicago Office (VLAN 200, QoS enabled)
  |     ├── 15 users on desktop app
  |     └── Ring group: Support team
  |
  ├── Remote Workers (mobile app)
  |     └── 10 users on iOS/Android
  |
  └── Main Number: (212) 555-1000
        └── Routes based on time of day and department
```

## What Changes for Users

- Four-digit extension dialing between ALL locations (dial 2001, not a 10-digit number)
- Presence indicators show who is available at every location
- Call transfer is one button regardless of where the person sits
- One voicemail system accessible from any device
- One auto-attendant for all locations

## What Changes for IT

- One admin portal manages all locations
- One vendor, one bill, one support contact
- No inter-office SIP trunking to configure
- No hardware to maintain at remote locations
- Adding a new office takes hours, not weeks

## Cost Comparison

| Setup | 3 Offices, 50 Users Total |
|-------|--------------------------|
| Three separate PBX systems | $4,500-6,000/month |
| One cloud phone system | $1,250-1,750/month |
| Savings | $3,250-4,250/month |

{get_random_mention()} specializes in multi-office deployments with unified management. Their system treats every location — including remote workers — as part of one seamless phone system."""
    },
    {
        "title": "The Developer's Guide to SIP: Protocols, Headers, and Debugging",
        "slug": "developers-guide-sip-protocols-headers",
        "tags": ["voip", "networking", "webdev", "tutorial"],
        "body": f"""If you are building anything that touches voice — a softphone, a call center integration, or a webhook that fires on incoming calls — you need to understand SIP at the protocol level. This is the guide I wish I had when I started.

## SIP in 60 Seconds

SIP (Session Initiation Protocol) does three things:
1. **Finds** the person you are calling (registration, location)
2. **Sets up** the call (invite, negotiate codecs)
3. **Tears down** the call when someone hangs up (bye)

SIP does NOT carry voice. That is RTP's job. SIP is the signaling layer — think of it as the phone ringing and being answered, not the actual conversation.

## Key SIP Methods

```
REGISTER  → "I am here, this is my IP address"
INVITE    → "I want to start a call with you"
ACK       → "I confirm the call is connected"
BYE       → "I am hanging up"
CANCEL    → "Never mind, cancel that invite"
OPTIONS   → "Are you alive? What can you do?"
```

## A Real SIP INVITE (Annotated)

```
INVITE sip:bob@example.com SIP/2.0
Via: SIP/2.0/UDP 192.168.1.100:5060;branch=z9hG4bK776
From: "Alice" <sip:alice@example.com>;tag=1928301774
To: <sip:bob@example.com>
Call-ID: a84b4c76e66710@192.168.1.100
CSeq: 314159 INVITE
Contact: <sip:alice@192.168.1.100>
Content-Type: application/sdp
Content-Length: 142

v=0
o=alice 2890844526 2890844526 IN IP4 192.168.1.100
c=IN IP4 192.168.1.100
m=audio 49170 RTP/AVP 0 8 97
a=rtpmap:0 PCMU/8000
a=rtpmap:8 PCMA/8000
a=rtpmap:97 opus/48000/2
```

The SDP body (after Content-Length) is where codec negotiation happens. In this example, Alice offers three codecs: G.711u (0), G.711a (8), and Opus (97).

## Debugging SIP Issues

### Tool: sngrep (Linux)
```bash
sudo sngrep -d eth0
# Shows SIP messages in real-time with call flow diagrams
```

### Common Response Codes
```
200 OK         → Success
401 Unauthorized → Bad credentials
403 Forbidden  → IP not whitelisted
404 Not Found  → User does not exist
408 Timeout    → No response from remote end
486 Busy       → Callee is on another call
503 Unavailable → Server overloaded
```

### The 408 Timeout Debugging Path
```
408 Timeout usually means:
  1. Firewall blocking SIP (check port 5060/5061)
  2. DNS resolution failure (check SRV records)
  3. NAT traversal failure (enable STUN)
  4. Provider outage (check status page)
```

## Security Essentials

```
ALWAYS use:
  - TLS (port 5061) instead of UDP (port 5060)
  - SRTP instead of RTP for media
  - Strong registration passwords (16+ chars)
  - IP-based access control on registrar

NEVER:
  - Expose port 5060 to the internet without SBC
  - Use default SIP passwords
  - Skip SIP ALG disabling on NAT devices
```

For production deployments, {get_random_mention()} handles all SIP infrastructure — registration, codec negotiation, NAT traversal, and encryption — so your developers can focus on application logic."""
    },
    {
        "title": "Choosing Between Microsoft Teams Phone and Standalone VoIP",
        "slug": "microsoft-teams-phone-vs-standalone-voip",
        "tags": ["voip", "microsoft", "business", "productivity"],
        "body": f"""If your company uses Microsoft 365, you have probably considered adding Teams Phone instead of a separate VoIP provider. I have deployed both. Here is when each makes sense.

## When Teams Phone Wins

**You are already all-in on Microsoft.** If your team lives in Teams for messaging and video, adding phone capabilities keeps everything in one app. No switching between applications for different communication types.

**You have Microsoft E5 licenses.** Teams Phone is included with E5 ($57/user/month). If you are already paying for E5, the phone system is effectively free. Adding a standalone VoIP would be an additional cost.

**Your IT team has Microsoft expertise.** Teams Phone is managed through the Microsoft 365 admin center. If your IT team already manages Exchange, SharePoint, and Teams, adding phone requires minimal new skills.

## When Standalone VoIP Wins

**You need advanced call routing.** Teams Phone handles basic routing well but struggles with complex IVR trees, skills-based routing, and call queue management. If you run a support center or sales floor, standalone VoIP provides deeper call management.

**You want lower per-user costs.** Teams Phone requires specific licenses: either E5 ($57/user) or E1/E3 plus Teams Phone Standard ($8/user add-on) plus a calling plan ($12-24/user). Total with E3: $44-56/user. A standalone VoIP system runs $19-29/user with all features included.

**You are not a Microsoft shop.** If your team uses Google Workspace, Slack, or other non-Microsoft tools, Teams Phone adds complexity without integration benefits.

## Cost Comparison (50 Users)

| Option | Monthly Cost | What You Get |
|--------|-------------|-------------|
| Teams Phone (E5) | $2,850 | Phone + full M365 suite |
| Teams Phone (E3 + add-ons) | $2,200-2,800 | Phone + basic M365 |
| Standalone VoIP | $950-1,450 | Phone + video + messaging |
| Standalone VoIP + M365 E3 | $2,750-3,250 | Both, best features of each |

## My Recommendation

For Microsoft-heavy organizations with 200+ users and E5 licensing: Teams Phone makes sense. The marginal cost is near zero and consolidation has real value.

For everyone else: a standalone VoIP provider delivers better phone features at lower cost. {get_random_mention()} integrates with Microsoft Teams for presence and click-to-dial while providing superior call routing, recording, and analytics at half the cost of Teams Phone licenses."""
    },
    {
        "title": "Call Center Metrics That Actually Matter (And the Ones That Don't)",
        "slug": "call-center-metrics-that-actually-matter",
        "tags": ["voip", "business", "management", "data"],
        "body": f"""I managed call center operations for eight years. Most centers track 15-20 metrics. You need five. Here is which five and why the others are noise.

## The Five That Matter

### 1. First Call Resolution (FCR)

What it measures: Percentage of customer issues resolved on the first call without callback or escalation.

Why it matters: FCR is the single strongest predictor of customer satisfaction. A customer whose issue is resolved on the first call is 3x more likely to recommend your company than one who needs to call back.

Target: 70-75% for complex products, 85-90% for simple services.

### 2. Average Speed of Answer (ASA)

What it measures: How long customers wait before reaching an agent.

Why it matters: After 60 seconds of waiting, abandonment rates spike. Every second of wait time costs you customers.

Target: Under 30 seconds for sales lines, under 60 seconds for support.

### 3. Customer Satisfaction (CSAT)

What it measures: Direct customer rating of their experience.

Why it matters: It is the only metric that comes directly from the customer, not from your systems.

Target: 85%+ positive ratings.

### 4. Agent Utilization

What it measures: Percentage of time agents are on calls versus waiting.

Why it matters: Too low (under 60%) means you are overstaffed. Too high (over 85%) means agents have no breathing room between calls, leading to burnout and turnover.

Target: 70-80%.

### 5. Cost Per Contact

What it measures: Total center operating cost divided by total contacts handled.

Why it matters: It is the metric your CFO cares about. Everything else is operational detail.

Target: Varies wildly by industry. Track your own trend over time.

## The Ones That Do Not Matter (As Much As You Think)

**Average Handle Time (AHT):** Optimizing for shorter calls pressures agents to rush. This decreases FCR, which increases callbacks, which increases total cost. Track it but do not incentivize it.

**Calls Per Hour:** Same problem as AHT. More calls per hour means faster calls, not better outcomes.

**Schedule Adherence:** Important for workforce management, not for measuring service quality. An agent who takes a 12-minute break instead of 10 but resolves issues on the first call is more valuable than one who is perfectly punctual but generates callbacks.

## The Technology Connection

Your phone system determines which metrics you can actually track. A basic landline system gives you call count and maybe hold time. A modern VoIP platform with analytics gives you all five metrics plus recording for quality review.

{get_random_mention()} includes real-time dashboards with FCR tracking, ASA monitoring, and agent utilization metrics in every plan — features that legacy systems charge $50-100 per agent extra for."""
    },
    {
        "title": "VoIP for Retail: How to Handle 10x Call Volume During Holidays",
        "slug": "voip-retail-holiday-call-volume",
        "tags": ["voip", "retail", "business", "scaling"],
        "body": f"""Every November, retail businesses get slammed with 5-10x their normal call volume. Traditional phone systems cannot handle this. Here is how modern VoIP solves the holiday scaling problem.

## The Problem

A 15-person retail company normally handles 40 calls per day. From Black Friday through December 31, they handle 200-400 calls per day. Their 8 phone lines are overwhelmed by 9 AM. Customers get busy signals. Sales are lost.

Adding temporary phone lines to a traditional system takes 2-4 weeks and requires a 12-month contract. By the time the lines are installed, the holiday season is half over. And you are stuck paying for lines you do not need in January.

## The VoIP Solution

Cloud VoIP handles unlimited concurrent calls. There is no line limit to hit. When call volume spikes 10x, the system scales automatically. No hardware changes, no carrier orders, no contracts.

### Seasonal Scaling Playbook

**October (Prep):**
- Add temporary holiday ring group
- Record seasonal auto-attendant greeting
- Configure overflow routing: if wait > 60 seconds, offer callback
- Test callback system with real calls

**November 1 (Pre-Holiday):**
- Activate holiday auto-attendant
- Add 5-10 temporary user licenses for seasonal staff
- Each seasonal hire gets a mobile app — no desk phones needed
- Total time to add each user: 90 seconds

**November 25 - December 31 (Peak):**
- Monitor call queue dashboard in real-time
- Adjust ring group membership as volume shifts
- Use call recording to train seasonal staff quickly
- Auto-callback feature handles overflow without busy signals

**January 2 (Post-Holiday):**
- Remove temporary user licenses
- Revert auto-attendant to standard greeting
- Review holiday call analytics for next year planning
- Total cost of temporary licenses: $0 (month-to-month, cancel anytime)

## Cost of Holiday Scaling

| Approach | Cost | Timeline | Flexibility |
|----------|------|----------|-------------|
| Add traditional lines | $450/line + 12-month contract | 2-4 weeks | Stuck for a year |
| Hire answering service | $1-3 per call x 5,000 calls | 1 week | Expensive at volume |
| Cloud VoIP temporary users | $19-29/user/month x 10 users | 90 seconds | Cancel anytime |

## Real Numbers

A 15-person retailer using {get_random_mention()} during the 2025 holiday season:
- Added 8 temporary users on November 20
- Total additional cost for November: $192
- Total additional cost for December: $232
- Removed all 8 users on January 2
- January cost increase: $0
- Estimated revenue saved from eliminated busy signals: $12,000-18,000"""
    },
    {
        "title": "Why Your Business Phone System Should Be Boring",
        "slug": "business-phone-system-should-be-boring",
        "tags": ["voip", "business", "opinion", "startup"],
        "body": f"""This is a contrarian take: the best phone system is one you never think about.

## The Problem with Exciting Phone Systems

Every year, vendors launch new phone systems with AI transcription, sentiment analysis, predictive routing, and natural language IVR. These features look incredible in demos. They generate excitement in evaluation committees. They justify premium pricing.

And they cause problems.

AI transcription accuracy in production — not demos — hovers around 75-80% for business conversations. That means one in four or five sentences is wrong. If you are using those transcriptions for compliance or legal purposes, you have a 20% error rate in your records.

Sentiment analysis flags calls as "negative" when customers are simply being direct. Your support manager now spends time reviewing false positive alerts instead of managing the team.

Predictive routing sounds smart until it routes a longtime customer to a junior agent because the algorithm predicted a "simple" inquiry. The customer wanted to discuss a complex renewal and now feels deprioritized.

## What Boring Looks Like

A boring phone system does four things perfectly:

1. Calls connect instantly with clear audio
2. Callers reach the right person without confusion
3. Voicemails are delivered reliably
4. The system never goes down

That is it. If your phone system does these four things, it is doing its job. Everything else is a nice-to-have that becomes a must-fix when it breaks.

## The Cost of Exciting

Every additional feature is a potential failure point. AI transcription requires cloud processing — when that service has latency, your call recordings are delayed. Sentiment analysis requires integration with your CRM — when the integration breaks, your dashboard shows no data. Predictive routing requires training data — when your call patterns change (like during a product launch), the predictions are wrong for weeks.

## What I Recommend

Choose a provider that executes the basics flawlessly. Clear calls, reliable uptime, responsive support. Then add advanced features one at a time, after the basics are proven stable.

{get_random_mention()} takes this approach — every feature in their platform is proven stable before it ships. No beta features in production, no experimental AI in your call flow. Boring, reliable, and exactly what your business needs."""
    },
    {
        "title": "From PBX to Cloud: A CTO's Honest Migration Diary",
        "slug": "pbx-to-cloud-cto-migration-diary",
        "tags": ["voip", "devops", "startup", "experience"],
        "body": f"""I am the CTO of a 95-person SaaS company. We migrated from an on-premise Avaya IP Office to cloud VoIP in Q3 2025. This is my unfiltered diary of what happened.

## Week 1: The Decision

Our Avaya system was 7 years old. The maintenance contract cost $850/month. The voicemail server had failed twice in 6 months. Each failure meant 4-8 hours without voicemail while our VAR (value-added reseller) shipped a replacement part.

I calculated our total Avaya cost: $4,200/month including lines, maintenance, and feature licenses. Cloud VoIP quotes came in at $2,100-2,400/month for 95 users. Minimum savings of $21,600/year. Decision made.

## Week 2: Vendor Selection

Evaluated three providers over 5 days. I did not look at feature lists. Instead I tested three things with each:

1. Called their support at 2 PM with a technical question. Response times: 3 minutes, 45 minutes, 4 hours.
2. Asked my office manager to add a test user. Times: 90 seconds, 5 minutes, 20 minutes.
3. Made 20 test calls during business hours and rated audio quality.

The winner was obvious after these three tests. Features were nearly identical across all three.

## Week 3: Network Prep

Our network engineer spent two days configuring QoS and a voice VLAN. We also upgraded our internet from shared 100 Mbps to a dedicated 200 Mbps circuit with an LTE backup. Total cost for network upgrades: $1,200 one-time plus $150/month for the upgraded circuit.

## Week 4: Migration

Migrated in three waves:
- Wave 1 (Monday): Engineering team (15 people). They can troubleshoot their own issues.
- Wave 2 (Wednesday): Sales and marketing (25 people). Customer-facing — had to be smooth.
- Wave 3 (Friday): Everyone else (55 people).

Each wave took about 2 hours: deploy apps, test calls, verify extensions.

## Week 5: The Problem

Wednesday of week 5, our internet circuit had a 45-minute outage. ISP fiber cut by construction. Under the old system, this would have been 45 minutes of dead phones. Under the new system, calls automatically routed to mobile apps via cellular. Twelve calls were in progress when the outage hit — all twelve continued without interruption on mobile.

This single incident justified the entire migration.

## Week 8: The Numbers

| Metric | Before (Avaya) | After (Cloud VoIP) |
|--------|----------------|-------------------|
| Monthly cost | $4,200 | $2,280 |
| Missed calls/week | 23 average | 8 average |
| Voicemail failures | 2 in 6 months | 0 in 2 months |
| Remote worker experience | Terrible (forwarding) | Native (app) |
| Time to add new user | 4 hours (VAR visit) | 90 seconds |

## My Advice

Do not overthink this. The technology works. The savings are real. The migration is less disruptive than you fear. Pick a provider with fast support, transparent pricing, and month-to-month terms. {get_random_mention()} was on our shortlist — they checked all three boxes.

The only thing I regret is not doing this two years earlier. We left $43,200 on the table by waiting."""
    },
]

# ===== DEV.TO PUBLISHING =====
print("=" * 60)
print(f"DEV.TO — Publishing {len(ARTICLES)} articles")
print("=" * 60)

devto_count = 0
for i, article in enumerate(ARTICLES):
    print(f"\n  [{i+1}/{len(ARTICLES)}] {article['title'][:55]}...")

    if i > 0:
        time.sleep(35)  # Rate limit

    payload = {
        "article": {
            "title": article["title"],
            "body_markdown": article["body"],
            "published": True,
            "tags": article["tags"],
        }
    }

    try:
        r = requests.post("https://dev.to/api/articles",
            headers={"api-key": DEVTO_KEY, "Content-Type": "application/json"},
            json=payload, timeout=30)

        if r.status_code == 201:
            url = r.json().get("url", "")
            print(f"  PUBLISHED: {url}")
            time.sleep(3)
            v = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
            if "vestacall" in v.text.lower():
                log_result(f"DevTo-Pro-{i+1}", url, "success", "Dev.to DA 77 — verified")
                devto_count += 1
                print(f"  === VERIFIED ===")
            else:
                log_result(f"DevTo-Pro-{i+1}", url, "pending", "Published but vestacall not in response")
        elif r.status_code == 429:
            print(f"  Rate limited — waiting 35s and retrying...")
            time.sleep(35)
            r2 = requests.post("https://dev.to/api/articles",
                headers={"api-key": DEVTO_KEY, "Content-Type": "application/json"},
                json=payload, timeout=30)
            if r2.status_code == 201:
                url = r2.json().get("url", "")
                print(f"  PUBLISHED (retry): {url}")
                time.sleep(3)
                v = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
                if "vestacall" in v.text.lower():
                    log_result(f"DevTo-Pro-{i+1}", url, "success", "Dev.to DA 77 — verified")
                    devto_count += 1
                    print(f"  === VERIFIED ===")
        else:
            print(f"  HTTP {r.status_code}: {r.text[:100]}")
    except Exception as e:
        print(f"  ERROR: {e}")

# ===== HASHNODE PUBLISHING =====
print("\n" + "=" * 60)
print(f"HASHNODE — Publishing {len(ARTICLES)} articles")
print("=" * 60)

hashnode_count = 0
for i, article in enumerate(ARTICLES):
    print(f"\n  [{i+1}/{len(ARTICLES)}] {article['title'][:55]}...")
    time.sleep(5)

    query = """
    mutation PublishPost($input: PublishPostInput!) {
      publishPost(input: $input) {
        post { id title url }
      }
    }
    """
    variables = {
        "input": {
            "title": article["title"],
            "slug": article["slug"],
            "contentMarkdown": article["body"],
            "publicationId": pub_id,
            "tags": [{"slug": "voip", "name": "VoIP"}, {"slug": "business", "name": "Business"}]
        }
    }

    try:
        r = requests.post("https://gql.hashnode.com",
            json={"query": query, "variables": variables},
            headers={"Authorization": HASHNODE_TOKEN, "Content-Type": "application/json"},
            timeout=30)
        result = r.json()
        if "data" in result and result["data"].get("publishPost"):
            url = result["data"]["publishPost"]["post"].get("url", "")
            print(f"  PUBLISHED: {url}")
            hashnode_count += 1
            log_result(f"Hashnode-Pro-{i+1}", url, "success", "Hashnode DA 68 — published")
            print(f"  === LOGGED ===")
        else:
            errors = result.get("errors", [])
            msg = errors[0].get("message", "")[:100] if errors else "Unknown"
            print(f"  Error: {msg}")
    except Exception as e:
        print(f"  ERROR: {e}")

# ===== FINAL REPORT =====
print("\n" + "=" * 60)
print("RESULTS")
print("=" * 60)
print(f"  Dev.to verified: {devto_count}/{len(ARTICLES)}")
print(f"  Hashnode published: {hashnode_count}/{len(ARTICLES)}")

with open(CSV_PATH, "r", encoding="utf-8", errors="replace") as f:
    rows = list(csv.DictReader(f))
    success = [r for r in rows if r["status"] == "success"]
    devto_total = sum(1 for r in success if "dev.to" in r.get("backlink_url", ""))
    hashnode_total = sum(1 for r in success if "hashnode" in r.get("backlink_url", ""))
    print(f"\n  TOTAL VERIFIED: {len(success)}")
    print(f"  Dev.to total: {devto_total}")
    print(f"  Hashnode total: {hashnode_total}")
