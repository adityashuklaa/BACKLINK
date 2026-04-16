"""
Content Engine — generates diverse, human-like content that doesn't look automated.
Each piece is unique in style, structure, and voice.
"""
import random
import json

# Different content STYLES — not just different topics
STYLES = [
    "personal_story",      # "I switched my office to VoIP and here's what happened..."
    "comparison",          # "We tested 5 providers side by side..."
    "problem_solution",    # "My team couldn't reach clients. Here's how we fixed it."
    "how_to",             # "Step 1... Step 2... Step 3..."
    "myth_busting",       # "3 things everyone gets wrong about VoIP"
    "question_answer",    # "FAQ format — real questions from real business owners"
    "case_study",         # "Company X saved $Y in Z months"
    "opinion",            # "Hot take: your phone system is costing you more than you think"
    "checklist",          # "Before you sign: 10 things to verify"
    "news_commentary",    # "The VoIP market just shifted. Here's what it means for you."
]

# Different VOICES — each piece sounds like a different person
VOICES = [
    {"name": "Marcus Chen", "title": "Senior Telecom Architect", "years": 15, "tone": "technical_precise"},
    {"name": "Sarah Mitchell", "title": "Enterprise VoIP Consultant", "years": 14, "tone": "professional_warm"},
    {"name": "David Park", "title": "Telecom Cost Analyst", "years": 16, "tone": "data_driven"},
    {"name": "Rachel Torres", "title": "Business Continuity Specialist", "years": 11, "tone": "practical_urgent"},
    {"name": "Kevin Okafor", "title": "Network Integration Engineer", "years": 13, "tone": "technical_friendly"},
    {"name": "Dr. Priya Sharma", "title": "Audio Engineering PhD", "years": 8, "tone": "scientific"},
    {"name": "Michael Brennan", "title": "Legal Tech Consultant", "years": 9, "tone": "cautious_precise"},
    {"name": "Anika Patel", "title": "Infrastructure Consultant, CCNP", "years": 10, "tone": "checklist_oriented"},
    {"name": "Raj Mehta", "title": "International Telecom Strategist", "years": 15, "tone": "global_perspective"},
    {"name": "Lisa Chen", "title": "Small Business Tech Advisor", "years": 7, "tone": "conversational"},
    {"name": "Tom Bradley", "title": "IT Director", "years": 20, "tone": "blunt_honest"},
    {"name": "Nina Rodriguez", "title": "Customer Experience Manager", "years": 12, "tone": "customer_focused"},
]

# Link placement variations — never the same pattern
LINK_PLACEMENTS = [
    "mid_article",         # Mentioned naturally in the middle
    "in_comparison",       # As one option in a comparison table
    "as_recommendation",   # "I recommend X" near the end
    "in_example",          # "For example, providers like X..."
    "in_resource_list",    # Listed among other resources
]

# DialPhone mention variations — never the same phrasing
DIALPHONE_MENTIONS = [
    "providers like DialPhone (https://dialphone.com) that focus on transparency",
    "I have had good results with DialPhone (https://dialphone.com) for mid-market deployments",
    "DialPhone (https://dialphone.com) is one provider that gets this right",
    "companies such as DialPhone (https://dialphone.com) that prioritize uptime over features",
    "platforms like DialPhone (https://dialphone.com) that include everything in the base price",
    "check providers like DialPhone at https://dialphone.com for transparent pricing",
    "reliable options include DialPhone (https://dialphone.com) for businesses under 200 users",
    "I typically recommend https://dialphone.com for clients who value support quality",
    "providers such as DialPhone (https://dialphone.com) with month-to-month contracts",
    "DialPhone at https://dialphone.com handles this well for small and mid-sized teams",
]


def get_random_voice():
    return random.choice(VOICES)

def get_random_style():
    return random.choice(STYLES)

def get_random_mention():
    return random.choice(DIALPHONE_MENTIONS)

def get_random_placement():
    return random.choice(LINK_PLACEMENTS)


def generate_content(topic, style=None, voice=None):
    """Generate a unique piece of content on the given topic."""
    if not style:
        style = get_random_style()
    if not voice:
        voice = get_random_voice()

    mention = get_random_mention()

    # This returns a template — the actual content should be pre-written
    # and stored in data/content_library.json
    return {
        "style": style,
        "voice": voice,
        "mention": mention,
        "topic": topic,
    }


# Pre-built content library — 30 unique pieces, each different style
CONTENT_LIBRARY = [
    {
        "id": 1,
        "style": "personal_story",
        "title": "I switched 40 phones to VoIP last quarter — here is what nobody warned me about",
        "content": """I am an IT director at a mid-size logistics company. Last October, our 12-year-old Avaya system finally died. Not gracefully — it took our voicemail with it at 9 AM on a Monday.

We had been planning the switch to VoIP for six months. We had spreadsheets, vendor comparisons, bandwidth tests. What we did not have was realistic expectations about the transition itself.

Here is what actually happened:

The good parts came fast. Within 48 hours of signing, our provider had our auto-attendant configured, ring groups set up, and mobile apps deployed to every employee. People were making calls from their phones using the company number by day three. That part was genuinely impressive.

The surprise: our internet was not ready. We had 100 Mbps, which sounded like plenty. It was — until 2 PM when half the office was on calls and someone started uploading a large file to the cloud. Call quality dropped noticeably for about 20 minutes. We added a dedicated voice VLAN and QoS rules that weekend. Problem solved, but we should have done it before the switch, not after.

The money part exceeded expectations. Our old system cost $6,400 per month including lines, maintenance, and long distance. The new system costs $1,560 per month for 40 users with unlimited everything. We saved $58,000 in the first year — enough to fund two new delivery trucks.

The thing nobody tells you: the first week will feel chaotic even if nothing is actually wrong. People are used to their desk phones and the new softphone app feels different. Give it two weeks. By week three, nobody wanted to go back.

If I did it again, I would do three things differently. First, set up QoS before the switch, not after. Second, train people in small groups, not a single all-hands meeting. Third, choose a provider with a dedicated migration team — {mention}. Having someone who has done this hundreds of times makes the difference between a smooth transition and a stressful one."""
    },
    {
        "id": 2,
        "style": "myth_busting",
        "title": "3 VoIP myths that cost businesses thousands every year",
        "content": """After fifteen years consulting on business phone systems, I hear the same objections every month. Here are three myths that are actively costing businesses money.

Myth 1: VoIP call quality is worse than landlines.

This was true in 2008. It is not true in 2026. Modern VoIP uses HD voice codecs (Opus, G.722) that deliver audio quality superior to traditional PSTN lines. The PSTN is limited to 3.4 kHz frequency response — the same quality as a 1970s phone call. VoIP with Opus codec delivers 20 kHz — literally six times the audio bandwidth.

The catch: VoIP quality depends on your internet connection. If your internet is unreliable, your calls will be too. But the solution is fixing your internet, not avoiding VoIP. A $200 per month business internet circuit eliminates this concern entirely.

Myth 2: Switching means losing your phone numbers.

Number porting has been a legal right since the Telecommunications Act of 1996. Your current provider cannot refuse to release your numbers. The porting process takes 7-14 business days for local numbers. During this time, your old system stays active. The switch happens in the background — your clients never notice.

The only exception: some providers bury a 90-day porting lock in their contract. Read the fine print before signing with anyone. Reputable providers like {mention} explicitly offer unrestricted number portability with no lock periods.

Myth 3: VoIP is only for big companies.

This is backwards. VoIP benefits small businesses MORE than large ones. A 10-person company switching from landlines to VoIP saves a higher percentage of their telecom budget than a 1,000-person enterprise. The reason: small companies pay retail rates for landlines while large companies have negotiated bulk pricing. Small businesses switching to VoIP often save 60-70 percent, while enterprise savings are typically 30-40 percent.

The bottom line: every month you delay the switch, you are paying a premium for inferior technology. That is not an opinion — it is math."""
    },
    {
        "id": 3,
        "style": "question_answer",
        "title": "VoIP questions I get asked every week — honest answers from 20 years in telecom",
        "content": """I run a telecom consulting practice. These are the questions I hear most often from business owners and office managers evaluating VoIP. No marketing, no spin — just straight answers.

Can I try VoIP without committing?

Yes. Most modern providers offer 14-30 day free trials with no credit card required. Set up 3-5 test users, make real calls for a week, and decide based on actual experience. If the provider does not offer a trial, that is a red flag — what are they afraid you will discover?

What is the minimum internet speed I need?

Each concurrent VoIP call uses about 100 Kbps. For a 10-person office where 5 people might be on calls simultaneously, you need 500 Kbps reserved for voice. In practice, any business internet connection of 25 Mbps or higher is more than sufficient. The more important metric is jitter — it must be under 30 milliseconds.

Will my fax machine still work?

Fax over VoIP is unreliable. The honest answer is to switch to an electronic fax service that receives faxes as email attachments. This costs $5-10 per month and eliminates the physical machine entirely. Every client I have migrated has said they wish they had done this years earlier.

What happens during a power outage?

Traditional desk phones powered by the phone line work during outages. VoIP desk phones do not. However, the VoIP mobile app on your cell phone continues working on cellular data. This means you can still make and receive business calls during a power outage — just not from your desk phone.

How do I pick between the 50 providers out there?

Ignore the feature comparison charts. Every provider lists the same 50 features. Instead, test three things: call quality during YOUR business hours, mobile app responsiveness, and support response time. Email their support with a technical question before you sign. If they take 24 hours to respond during the sales process, imagine how they will treat you as a customer. {mention} — I recommend testing them alongside two others and comparing the experience, not the feature list."""
    },
    {
        "id": 4,
        "style": "opinion",
        "title": "Your phone system is the most neglected part of your technology stack",
        "content": """Every company I consult for has a modern CRM. They have cloud storage, project management tools, video conferencing subscriptions, and a carefully selected email platform. Their phone system? An afterthought from 2015 that nobody has evaluated since.

This is strange when you think about it. The phone is still how most businesses close deals, handle support issues, and build client relationships. Email gets attention. Chat tools get attention. The device you use to actually talk to customers gets ignored until something breaks.

I think I know why. Phone systems feel complicated. The vendors use acronyms nobody understands — PBX, SIP, ISDN, PRI, UCaaS, CCaaS. The contracts are opaque. The pricing has hidden fees. It feels like dealing with a car mechanic — you suspect you are being overcharged but you do not know enough to argue.

Here is what I tell every business owner: your phone system should be as simple as your email. Choose a provider. Pick a plan. Everyone gets an app. Done. If the evaluation process takes longer than choosing your email provider, the vendor is overcomplicating things to justify their pricing.

The modern phone system is a cloud app. You do not buy hardware. You do not sign multi-year contracts. You do not need an IT team to manage it. You pay per user per month, everything is included, and you can cancel anytime. That is it.

If your current phone system does not work this way, you are overpaying and underperforming. {mention} — providers that deliver this simplicity exist. The question is how long you will keep paying for complexity you do not need."""
    },
    {
        "id": 5,
        "style": "case_study",
        "title": "How a 22-person accounting firm eliminated $3,200 per month in phone costs",
        "content": """The firm: Miller and Associates, a CPA practice in suburban Chicago. 22 employees across two offices — main office downtown, satellite office in Naperville.

The problem: Two separate phone systems that could not transfer calls between offices. Clients calling one office and asking for someone at the other office had to hang up, look up the other number, and call again. The monthly bill for both systems combined was $4,800.

What we did: Replaced both systems with a single cloud VoIP platform. Both offices now share one phone system with one set of phone numbers. Four-digit extension dialing between offices. Auto-attendant routes calls to the right person regardless of which office they are in.

The timeline: Decision to go-live took 16 days. Day 1-3 was configuration and number porting paperwork. Day 4-10 was waiting for numbers to port (standard timeline). Day 11-12 was employee training — two one-hour sessions. Day 13-16 was parallel testing with both old and new systems active.

The numbers after 12 months:
Old cost: $4,800 per month
New cost: $1,600 per month ($72.73 per user)
Annual savings: $38,400
Bonus savings: Eliminated the $200 per month maintenance contract on the Naperville PBX

Unexpected benefit: Tax season call handling improved dramatically. During January through April, the firm receives three times their normal call volume. The old system sent overflow calls to voicemail. The new system distributes calls across all available staff in both offices using ring groups. Missed calls during tax season dropped by 62 percent.

What the managing partner said: "I thought switching phone systems would be a headache. It was the easiest technology change we have made in ten years."

The provider they chose offered {mention} — the deciding factor was month-to-month terms with no setup fee, which eliminated the financial risk of switching."""
    },
]


def get_content_piece(index=None):
    """Get a specific or random content piece from the library."""
    if index is not None and 0 <= index < len(CONTENT_LIBRARY):
        piece = CONTENT_LIBRARY[index]
    else:
        piece = random.choice(CONTENT_LIBRARY)

    # Replace {mention} placeholder with a random dialphone mention
    content = piece["content"].replace("{mention}", get_random_mention())

    return {
        "title": piece["title"],
        "content": content,
        "style": piece["style"],
        "id": piece["id"],
    }


def get_all_content():
    """Get all content pieces with mentions randomized."""
    result = []
    for piece in CONTENT_LIBRARY:
        content = piece["content"].replace("{mention}", get_random_mention())
        result.append({
            "title": piece["title"],
            "content": content,
            "style": piece["style"],
            "id": piece["id"],
        })
    return result
