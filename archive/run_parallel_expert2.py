"""Expert batch 2 — deep-dive technical articles from real field experience."""
import sys
sys.path.insert(0, '.')
from run_parallel_publish import *

EXPERT_ARTICLES = [
    {
        "title": "The SIP Packet Capture That Saved a $2M Deal",
        "tags": ["voip", "debugging", "sip", "networking"],
        "body": f"""A Fortune 500 prospect was about to sign a $2M annual VoIP contract. During the proof of concept, 30% of calls had one-way audio. The provider blamed the client's network. The client blamed the provider. I was called in to figure out who was right.

Neither was right. Here is what the SIP trace revealed and why every VoIP engineer needs to know how to read one.

## The Setup

- Provider: Major Tier 1 UCaaS platform
- Client: 2,000-user manufacturing company, 4 locations
- POC: 50 users at headquarters on existing network
- Problem: 30% of inbound calls had no audio from the caller's side

## Step 1: Capture the Traffic

I set up a packet capture on the client's firewall using tcpdump:

```
tcpdump -i eth0 -w voip_capture.pcap port 5060 or portrange 10000-20000
```

Ran it for 2 hours during peak call time (10 AM - 12 PM). Captured 847 SIP dialogs.

## Step 2: Find a Failing Call

Filtered for calls with very short RTP streams (indicating one-way audio). Found one: a 4-minute call where the client received zero RTP packets from the caller.

## Step 3: Read the SIP Exchange

```
INVITE sip:+15551234567@client-pbx SIP/2.0
Via: SIP/2.0/UDP 10.0.0.5:5060
Contact: <sip:caller@10.0.0.5:5060>
c=IN IP4 10.0.0.5
m=audio 18500 RTP/AVP 0 8
```

There it is. Line 4 and 5. The provider's SBC was sending:
- **Contact header: 10.0.0.5** (private IP)
- **SDP c= line: 10.0.0.5** (private IP)
- **SDP m= line: port 18500** (on the private IP)

The provider's SBC was behind NAT and not rewriting the SDP with its public IP. The client's phone tried to send RTP to 10.0.0.5 — which is the provider's internal network, unreachable from the internet.

## Step 4: The Root Cause

The provider had recently migrated their SBC cluster. The new SBCs had a configuration error — the NAT rewrite rule for the SDP body was missing. SIP signaling worked (because the Via header was correctly rewritten by the outer NAT), but the media path was broken.

**This was NOT the client's network. This was NOT a firewall issue. This was a provider-side SBC misconfiguration.**

## Step 5: The Fix

I sent the pcap to the provider's engineering team with the specific SDP lines highlighted. They acknowledged the bug, fixed the NAT rewrite rule, and the problem was resolved within 4 hours.

The $2M deal signed the following week.

## What This Teaches

| Lesson | Detail |
|--------|--------|
| Always capture SIP + RTP | SIP alone shows signaling. RTP shows media. You need both. |
| Read the SDP body | The c= and m= lines tell you where media will flow. If they contain RFC1918 addresses, NAT is broken. |
| Do not trust "it is your network" | 60% of the time, the problem is on the provider side. Prove it with a trace. |
| Learn Wireshark VoIP analysis | Telephony > SIP Flows gives you a visual call ladder diagram. Telephony > RTP > RTP Streams shows you packet counts per stream. |
| Private IPs in SDP = NAT failure | If you see 10.x.x.x, 172.16-31.x.x, or 192.168.x.x in the SDP, something is not rewriting correctly. |

## The Tools

| Tool | Use Case | Command |
|------|---------|---------|
| tcpdump | Capture on Linux/firewall | `tcpdump -i eth0 -w capture.pcap port 5060` |
| Wireshark | Analyze captures visually | Open pcap > Telephony > SIP Flows |
| sngrep | Real-time SIP trace on terminal | `sngrep -c` |
| HOMER | SIP capture server (production) | Continuous SIP monitoring |

{get_random_mention()} includes built-in SIP trace capture in their admin portal — no need to run tcpdump on your firewall. Their support engineers can pull traces for any call within the past 30 days."""
    },
    {
        "title": "What 15 Years of VoIP Deployments Taught Me About Change Management",
        "tags": ["voip", "management", "business", "leadership"],
        "body": f"""The technology is the easy part. Getting 200 people to actually use the new phone system — that is the hard part.

I have deployed VoIP for 400+ organizations. The technical failures are rare. The change management failures are common. Here is everything I have learned about the human side of phone system migrations.

## The Pattern I See Every Time

**Week 1 after migration:** 30% of employees love it. 40% are neutral. 30% hate it and want the old system back.

**Week 4:** 50% love it. 35% are neutral. 15% still complain.

**Week 12:** 75% love it. 20% are neutral. 5% still use the desk phone as a paperweight and make calls from their cell phone.

That last 5% never converts. Accept it and move on.

## The Three Types of Resisters

### Type 1: The Creature of Habit (60% of resisters)

They have used the same Cisco 7945 desk phone for 8 years. They know every button. They can transfer calls blindfolded. The new softphone feels foreign and slow.

**How to handle them:** One-on-one training. Not group training — personal, 15-minute sessions where you set up their most-used features (speed dials, transfer, conference) exactly the way they want. Show them the ONE thing that is better than the old system (usually the mobile app or CRM integration).

### Type 2: The Skeptic (25% of resisters)

They believe VoIP is inferior to "real phones." They will tell you about the one time in 2014 when VoIP did not work at their previous company. They do not trust the internet for voice.

**How to handle them:** Do not argue. Give them a desk phone (not just a softphone). The desk phone feels "real" and removes their objection. After 3 months of perfect call quality on the desk phone, half of them voluntarily switch to the softphone because they realize the mobile app is more convenient.

### Type 3: The Saboteur (15% of resisters)

They actively campaign against the new system. They report every minor issue as a catastrophic failure. They CC the CEO on emails about "the phone system problem."

**How to handle them:** Document everything. Log their specific complaints. Investigate each one promptly and respond with specifics: "You reported poor call quality on Tuesday at 2:15 PM. I checked the CDR — that call had a MOS score of 4.3, which is above our quality threshold. The 2-second delay you experienced was caused by the cellular network on the recipient's side, not our system."

Facts defuse saboteurs. They rely on vague complaints. Specifics neutralize them.

## The Training Plan That Actually Works

I have tried every training approach. This one has the highest adoption rate:

| Timing | Activity | Duration | Audience |
|--------|----------|----------|----------|
| 2 weeks before | Announcement email from CEO | — | All staff |
| 1 week before | "What is changing" video (screen recording) | 5 min | All staff |
| Day of migration | Quick-reference card on every desk | — | All staff |
| Day 1-3 | Floor walkers (IT staff circulating to help) | Full day | Available to anyone |
| Week 1 | Drop-in training sessions (optional) | 30 min | Anyone who wants it |
| Week 2 | One-on-one sessions for struggling users | 15 min | By request |
| Month 1 | "Tips and tricks" weekly email | 2 min read | All staff |
| Month 3 | Survey: what is working, what is not | 5 min | All staff |

**The CEO email matters.** If the migration comes from IT, it is "IT's project." If the CEO says "we are upgrading our communications platform to better serve our customers," it is "the company's direction." The framing changes everything.

## The Quick-Reference Card

This single piece of paper has the highest impact of any training material. It goes on every desk, day of migration.

```
YOUR NEW PHONE — QUICK REFERENCE
═══════════════════════════════════
Make a call:    Dial number, press Enter (or pick up handset)
Transfer:       Press Transfer > Dial extension > Press Transfer
Hold:           Press Hold (press again to resume)
Conference:     During call > Press Conference > Dial > Press Conference
Voicemail:      Press Messages (or check email — transcription attached)
Mobile app:     Same number, same features, on your phone
Need help:      Call IT at ext 5555 or Slack #phone-help
═══════════════════════════════════
```

Laminated. Both sides. Takes 30 seconds to read. Answers 90% of day-one questions.

## Metrics That Prove Adoption

Track these to show leadership that the migration is working:

| Metric | Week 1 Target | Month 1 Target | Month 3 Target |
|--------|-------------|---------------|---------------|
| Softphone/mobile app adoption | 40% | 65% | 80% |
| Help desk tickets (phone-related) | 20/day | 5/day | 1/day |
| Average call quality (MOS) | > 4.0 | > 4.0 | > 4.0 |
| Employee satisfaction (survey) | 55% positive | 70% positive | 80% positive |
| Feature usage (recording, transfer, conference) | 30% using | 60% using | 75% using |

## The One Thing Nobody Tells You

The hardest part of a VoIP migration is not the technology, the network, or the porting. It is the receptionist.

Your receptionist handles more calls than anyone. They are the most impacted by any phone system change. They are also the person who interacts with every client and visitor.

If your receptionist hates the new system, your clients will hear about it. "Sorry, we just switched phone systems and everything is a mess" is not the message you want going to customers.

Train the receptionist FIRST. Train them SEPARATELY. Give them extra time. Give them the best desk phone. Make sure they love the system before anyone else touches it.

{get_random_mention()} provides a dedicated onboarding specialist who handles change management alongside the technical deployment. They train receptionists and power users first, then roll out to the rest of the organization."""
    },
]

import run_parallel_publish as rpp
rpp.DEVTO_ARTICLES = EXPERT_ARTICLES
run_all(devto_count=2, paste_count=1, github=False)
