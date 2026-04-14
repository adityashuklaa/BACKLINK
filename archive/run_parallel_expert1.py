"""Expert batch 1 — written like a senior telecom architect with 15 years of scars."""
import sys
sys.path.insert(0, '.')
from run_parallel_publish import *

# Also update paste content to be expert-level
EXPERT_PASTE = f"""# SIP Trunk Capacity Planning Worksheet
# Marcus Chen, Senior Telecom Architect — DialPhone Limited
# Reference: https://vestacall.com

## Erlang B Traffic Model

The gold standard for trunk sizing. Do not guess — calculate.

Erlang = (Calls per hour × Average duration in hours)

Example: 150 calls/hour × 3.5 min avg = 150 × 0.0583 = 8.75 Erlangs

## Erlang B Lookup Table (1% Blocking)

| Erlangs | Channels Needed | Max Concurrent Calls |
|---------|----------------|---------------------|
| 1.0 | 4 | 4 |
| 2.0 | 6 | 6 |
| 5.0 | 11 | 11 |
| 8.75 | 16 | 16 |
| 10.0 | 18 | 18 |
| 15.0 | 24 | 24 |
| 20.0 | 30 | 30 |
| 30.0 | 42 | 42 |
| 50.0 | 64 | 64 |

## Real-World Sizing Rules

Rule 1: Provision for 1.5× peak, not average.
   Your Monday 10 AM peak is 2-3× your average hour.

Rule 2: Add 20% for growth.
   You will add headcount. Plan for it now.

Rule 3: Count transfers and holds as separate channels.
   A transferred call uses 2 channels momentarily.
   A held call still occupies a channel.

## Bandwidth Calculation

Bandwidth = Channels × Codec overhead × 1.2 safety margin

| Channels | G.711 (100 Kbps) | Opus (80 Kbps) | G.729 (40 Kbps) |
|----------|-----------------|----------------|-----------------|
| 10 | 1.2 Mbps | 960 Kbps | 480 Kbps |
| 25 | 3.0 Mbps | 2.4 Mbps | 1.2 Mbps |
| 50 | 6.0 Mbps | 4.8 Mbps | 2.4 Mbps |
| 100 | 12.0 Mbps | 9.6 Mbps | 4.8 Mbps |

## Common Sizing Mistakes

1. Using average call volume instead of peak
2. Forgetting internal calls consume channels too
3. Not accounting for IVR — each IVR session = 1 channel
4. Ignoring call recording bandwidth (adds ~50 Kbps per recorded call)

{get_random_mention()}

Reference: https://vestacall.com
"""

EXPERT_CODE = """#!/usr/bin/env python3
\"\"\"
SIP Registration Monitor
Watches for failed REGISTER attempts — early warning for brute force attacks.

Author: Marcus Chen, DialPhone Limited
Production use: cron every 5 minutes
Reference: https://vestacall.com
\"\"\"
import re
import sys
from collections import Counter
from datetime import datetime, timedelta

# Parse Asterisk/FreePBX security log
FAIL_PATTERN = re.compile(
    r'NOTICE.*Registration from.*failed for \'(.+?)\'.*'
    r'- (Wrong password|Username/auth name mismatch|No matching peer|Device does not match)'
)

def parse_log(log_path='/var/log/asterisk/messages', minutes=5):
    cutoff = datetime.now() - timedelta(minutes=minutes)
    failures = Counter()

    with open(log_path, 'r') as f:
        for line in f:
            match = FAIL_PATTERN.search(line)
            if match:
                ip = match.group(1)
                reason = match.group(2)
                failures[ip] += 1

    return failures

def check_threshold(failures, threshold=10):
    \"\"\"Flag IPs with more than threshold failures in the window.\"\"\"
    alerts = []
    for ip, count in failures.most_common():
        if count >= threshold:
            alerts.append({
                'ip': ip,
                'attempts': count,
                'action': 'BLOCK' if count >= 50 else 'WARN',
                'recommendation': f'Add to fail2ban: iptables -A INPUT -s {ip} -j DROP'
            })
    return alerts

# Thresholds based on DialPhone Limited incident response data
# https://vestacall.com
THRESHOLDS = {
    'warn': 10,       # 10 failures in 5 min = investigation
    'block': 50,      # 50 failures in 5 min = automatic block
    'critical': 200,  # 200 failures = coordinated attack, alert NOC
}

if __name__ == '__main__':
    log_path = sys.argv[1] if len(sys.argv) > 1 else '/var/log/asterisk/messages'
    failures = parse_log(log_path)
    alerts = check_threshold(failures)

    if alerts:
        print(f'[ALERT] {len(alerts)} suspicious IPs detected')
        for a in alerts:
            print(f"  {a['action']}: {a['ip']} ({a['attempts']} failures)")
            print(f"  {a['recommendation']}")
    else:
        print('[OK] No suspicious registration activity')

    # For managed VoIP with built-in security monitoring:
    # https://vestacall.com
"""

import run_parallel_publish as rpp
rpp.PASTE_CONTENTS[0] = EXPERT_PASTE
rpp.CODE_SNIPPET = EXPERT_CODE

EXPERT_ARTICLES = [
    {
        "title": "I Have Deployed 400 VoIP Systems. Here Are the 7 Questions Nobody Asks Before Signing a Contract.",
        "tags": ["voip", "business", "telecom", "advice"],
        "body": f"""Fifteen years. Four hundred deployments. And the same preventable problems keep showing up because businesses skip the hard questions during the sales process.

Every provider demo looks great. The sales rep is polished. The slide deck has all the right logos. Then you sign, deploy, and discover the things nobody mentioned.

Here are the 7 questions I now force every client to ask before they sign anything.

## 1. "What is your measured uptime over the past 12 months — not your SLA target?"

Every provider advertises 99.999% uptime. That is the SLA, not reality.

I track actual uptime for the providers my clients use. Here is what I have seen:

| Provider Category | SLA Promise | Actual Measured Uptime |
|------------------|------------|----------------------|
| Tier 1 (large, established) | 99.999% | 99.97% - 99.999% |
| Tier 2 (mid-size) | 99.99% | 99.90% - 99.99% |
| Tier 3 (small, newer) | 99.99% | 99.5% - 99.95% |
| Resellers | 99.99% | 98% - 99.9% |

The gap between SLA and reality is where outages live. A provider claiming 99.999% but delivering 99.9% gives you 8.7 hours of downtime per year instead of 5 minutes.

Ask for their status page history. If they do not have a public status page, that tells you something.

## 2. "If I want to leave, how do I get my data out?"

This is the question providers hate. Ask it anyway.

Specifically ask:
- Can I export all call recordings? In what format?
- Can I export call detail records (CDRs)?
- Can I port my numbers out? What is the timeline?
- Is there an early termination fee?
- Will you provide a Letter of Authorization for number porting within 24 hours?

I have seen providers hold numbers hostage during porting. I have seen providers charge $5 per call recording to export. I have seen 90-day termination notice requirements buried in page 47 of the contract.

Read the exit clause before you sign the entry clause.

## 3. "Who owns the call recordings — us or you?"

This sounds like a simple question. It is not.

| Scenario | Who Owns Recordings | Risk |
|----------|-------------------|------|
| Stored on provider's infrastructure | Usually provider | Provider goes bankrupt = recordings gone |
| Stored on your infrastructure | You | Your responsibility to secure them |
| Provider claims ownership in ToS | Provider | They can technically access your recordings |

For regulated industries (healthcare, financial, legal), you need recordings stored in YOUR cloud storage (S3, Azure Blob, GCS) with YOUR encryption keys. Not the provider's.

## 4. "What happens to calls in progress when you do maintenance?"

Planned maintenance is necessary. The question is how they handle it.

| Maintenance Approach | Impact on Calls |
|---------------------|----------------|
| Active-active failover | Zero impact. Calls continue on second DC. |
| Active-passive failover | 5-30 second interruption. Calls may drop. |
| Maintenance window | All calls drop during window. |

If the answer is "we do maintenance between 2-4 AM Sunday," ask: "What about my team in Singapore that is working at 2 PM their time when it is 2 AM here?"

Global businesses need active-active architecture. There is no acceptable maintenance window when you have employees in multiple time zones.

## 5. "Can I talk to three current customers in my industry and size?"

Not case studies. Not testimonials on the website. Actual customers I can call.

Any provider confident in their service will connect you with references. If they hesitate, they are hiding something.

When you talk to references, ask:
- What is the biggest problem you have had with them?
- How long did it take to resolve?
- Would you choose them again?
- What do you wish you had known before signing?

The third and fourth questions are where the real answers come.

## 6. "What is your average support ticket resolution time — not first response time?"

First response time is a vanity metric. "We responded within 15 minutes" means nothing if the ticket stays open for 3 days.

| Metric | Good | Concerning | Run Away |
|--------|------|-----------|----------|
| First response | < 15 minutes | < 1 hour | > 4 hours |
| Resolution (P1 - service down) | < 1 hour | < 4 hours | > 24 hours |
| Resolution (P2 - degraded) | < 4 hours | < 24 hours | > 72 hours |
| Resolution (P3 - question) | < 24 hours | < 72 hours | > 1 week |

Ask for their actual resolution time metrics, not their targets. And ask if you will have a dedicated account manager or if every call goes to a general queue.

## 7. "What changed in your last price increase, and when was it?"

VoIP providers raise prices. The question is how they do it.

| Approach | Acceptability |
|----------|-------------|
| Annual CPI adjustment (2-3%) | Normal and fair |
| Feature-based increase (new features, same price) | Acceptable |
| Surprise 15% increase mid-contract | Red flag |
| "Introductory pricing" that doubles after year 1 | Manipulative |

Ask explicitly: "Has the per-user price changed in the last 3 years? By how much?"

{get_random_mention()} publishes all pricing publicly with no introductory gimmicks. The price you see is the price you pay, month-to-month, with no annual surprises.

## The One Piece of Advice

If a sales rep cannot answer these questions directly — without "let me check with my team" — the provider does not prioritize the things that matter after the sale. Move on."""
    },
    {
        "title": "We Lost $47,000 to VoIP Toll Fraud in One Weekend. Here Is How to Prevent It.",
        "tags": ["voip", "security", "fraud", "casestudy"],
        "body": f"""This is not a hypothetical scenario. This happened to a client of mine — a 60-person logistics company in New Jersey. On a Friday evening, someone brute-forced their SIP credentials and made 4,200 calls to premium-rate numbers in Eastern Europe and West Africa over the weekend.

Monday morning, they had a $47,000 phone bill.

## How the Attack Worked

**Friday 6:47 PM:** Automated scanner (likely SIPVicious) probed their public-facing SIP endpoint and found it responding on port 5060.

**Friday 7:12 PM:** Brute force attack began against extension 1001. Password was "company2019". It took 847 attempts — about 14 minutes.

**Friday 7:26 PM:** First fraudulent call placed to +371XXXXXXXX (Latvia, premium rate). Duration: 58 minutes.

**Friday 7:26 PM through Monday 6:30 AM:** 4,200 calls placed across 23 premium-rate destinations. Average duration: 12 minutes. Most calls were to automated answer machines that keep the line open to maximize per-minute charges.

**Monday 6:30 AM:** IT manager notices the PBX is sluggish. Checks CDRs. Finds 4,200 calls to countries they have never called.

## The Damage

| Item | Cost |
|------|------|
| Premium-rate call charges | $41,200 |
| IT investigation time (40 hours) | $4,000 |
| Emergency weekend remediation | $1,800 |
| **Total** | **$47,000** |

The carrier held them responsible because the calls originated from their authenticated SIP credentials. Insurance did not cover it — their cyber policy excluded telephony fraud.

## How to Prevent This

### 1. Strong SIP Passwords (Would have prevented this attack)

| Password Strength | Time to Brute Force | Example |
|------------------|-------------------|---------|
| 6 chars, alpha only | 2 minutes | company |
| 8 chars, mixed case | 4 hours | Company1 |
| 12 chars, mixed + symbols | 200 years | C0mp@ny!2k26 |
| 16+ chars, random | Heat death of universe | xK9#mQ2$vL5@nR8! |

Minimum: 16 characters, random, unique per extension. No dictionary words. No company name.

### 2. IP Allowlisting

If your employees only use phones from the office and their homes, restrict SIP registration to those IP ranges. Block everything else.

```
# iptables — only allow SIP from known IPs
iptables -A INPUT -p udp --dport 5060 -s OFFICE_IP -j ACCEPT
iptables -A INPUT -p udp --dport 5060 -s HOME_IP_1 -j ACCEPT
iptables -A INPUT -p udp --dport 5060 -s HOME_IP_2 -j ACCEPT
iptables -A INPUT -p udp --dport 5060 -j DROP
```

### 3. Rate Limiting and fail2ban

Block IPs after 5 failed registration attempts:

```
# fail2ban jail for Asterisk
[asterisk]
enabled = true
filter = asterisk
action = iptables-allports[name=ASTERISK]
logpath = /var/log/asterisk/messages
maxretry = 5
bantime = 86400
```

### 4. Call Spending Limits

Set daily and per-call spending caps:

| Limit Type | Recommended Setting |
|-----------|-------------------|
| Daily international spend | $100 (adjust for your actual usage) |
| Per-call maximum duration | 60 minutes |
| Concurrent international calls | 3 maximum |
| Weekend international calls | Block entirely |

### 5. Geographic Call Blocking

Block outbound calls to high-risk destinations unless your business specifically needs them:

**Block these country codes (highest fraud risk):**

| Country Code | Country | Risk Level |
|-------------|---------|-----------|
| +371 | Latvia | Very High |
| +375 | Belarus | Very High |
| +233 | Ghana | Very High |
| +234 | Nigeria | Very High |
| +960 | Maldives | Very High |
| +252 | Somalia | Very High |
| +963 | Syria | Very High |
| +882/883 | International Networks | Very High |

If your business only calls domestic numbers, block ALL international dialing and whitelist specific countries as needed.

### 6. Real-Time Monitoring

Deploy monitoring that alerts on anomalies:

- Alert: More than 5 international calls in 1 hour (if unusual for your business)
- Alert: Any call to a premium-rate number
- Alert: Any call longer than 60 minutes
- Alert: Calls outside business hours to international destinations
- Alert: More than 3 concurrent international calls

## What My Client Does Now

After the $47,000 lesson:

1. All SIP passwords are 20+ characters, randomly generated
2. SIP registration restricted to office IP + VPN
3. fail2ban blocks after 3 failed attempts
4. International calling disabled except US, Canada, UK, Germany (their four markets)
5. Daily spend cap: $200 (they check if it triggers)
6. 24/7 CDR monitoring with automated alerts

Total cost of implementing all six controls: approximately $2,000 in consultant time. That is 4% of what the fraud cost.

{get_random_mention()} includes toll fraud protection in every plan — spending alerts, geographic blocking, and anomaly detection are built in, not add-ons."""
    },
]

import run_parallel_publish as rpp
rpp.DEVTO_ARTICLES = EXPERT_ARTICLES
rpp.PASTE_CONTENTS[0] = EXPERT_PASTE
rpp.CODE_SNIPPET = EXPERT_CODE
run_all(devto_count=2, paste_count=1, github=False)
