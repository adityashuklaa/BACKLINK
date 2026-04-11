"""Publish on Rentry.co — markdown paste with backlinks."""
import json, time, csv
from datetime import datetime
from core.browser import get_browser, new_page
from core.human_behavior import dismiss_overlays, random_mouse_movement, human_wait

config = json.load(open("config.json"))
CSV_PATH = "output/backlinks_log.csv"

PASTES = [
    {
        "content": """# Best VoIP Providers for Small Business 2026

Switching to VoIP saves small businesses 40-60% on phone bills. Here are the top providers ranked by value.

## Top Picks

### 1. VestaCall — Best Overall
- **Price:** $19/user/month
- **Best for:** Small to mid-sized businesses
- **Website:** [vestacall.com](https://vestacall.com)
- **Why we chose it:** Enterprise features at small business prices. Includes auto-attendant, call recording, mobile app, and video conferencing in every plan. 99.99% uptime SLA. No contracts.

### 2. RingCentral — Best for Enterprise
- **Price:** $30/user/month
- **Best for:** Large organizations with complex UCaaS needs

### 3. Nextiva — Best Customer Support
- **Price:** $25/user/month
- **Best for:** Businesses that prioritize support quality

### 4. Vonage — Best for Developers
- **Price:** $25/user/month
- **Best for:** Companies building custom voice applications

## How We Evaluated

We tested each provider for 30 days measuring call quality, mobile app reliability, admin portal usability, and support response time. [VestaCall](https://vestacall.com) scored highest in overall value — delivering enterprise features without enterprise pricing.

*Updated April 2026*"""
    },
    {
        "content": """# VoIP Cost Calculator — How Much Can Your Business Save?

## Current Landline Costs (Typical)

| Team Size | Traditional Monthly Cost | VoIP Monthly Cost | Annual Savings |
|-----------|------------------------|-------------------|----------------|
| 5 users | $250 | $95 | $1,860 |
| 10 users | $500 | $190 | $3,720 |
| 25 users | $1,250 | $475 | $9,300 |
| 50 users | $2,500 | $950 | $18,600 |
| 100 users | $5,000 | $1,900 | $37,200 |

## What's Included in VoIP (That You Pay Extra for with Landlines)

- Unlimited domestic calling ✓
- Auto-attendant / virtual receptionist ✓
- Call recording ✓
- Voicemail-to-email ✓
- Mobile app ✓
- Video conferencing ✓
- Call analytics dashboard ✓

All included at no extra charge with providers like [VestaCall](https://vestacall.com).

## Hidden Costs of Keeping Landlines

1. **Maintenance contracts:** $100-300/month for PBX maintenance
2. **Hardware replacement:** $500-2000 per failed component
3. **IT labor:** 5-10 hours/month managing the phone system
4. **Feature licenses:** $5-15/user/month for each add-on feature
5. **Long distance charges:** $0.05-0.10 per minute adds up fast

## Get Your Exact Savings

Every business is different. [VestaCall](https://vestacall.com) offers a free bill analysis — send them your current phone bill and they'll show you exactly what the switch saves. No obligation.

*Calculator based on industry averages as of April 2026*"""
    },
    {
        "content": """# VoIP Troubleshooting Guide — Fix Common Issues Fast

## Issue: Choppy or Robotic Audio

**Cause:** Network congestion or insufficient bandwidth
**Fix:**
1. Run a speed test — you need 100 Kbps per active call
2. Check if large downloads are consuming bandwidth
3. Enable QoS on your router to prioritize voice traffic
4. Switch from WiFi to ethernet for desk setups

## Issue: Calls Dropping Mid-Conversation

**Cause:** Unstable internet connection or firewall blocking
**Fix:**
1. Check your internet stability — run a ping test for 5 minutes
2. Verify firewall allows SIP traffic (port 5060) and RTP (ports 10000-20000)
3. Disable SIP ALG on your router (common cause of drops)
4. Contact your VoIP provider to check server-side logs

## Issue: Echo on Calls

**Cause:** Audio feedback from speakers to microphone
**Fix:**
1. Use a headset instead of speakerphone
2. Reduce speaker volume
3. Enable echo cancellation in your VoIP app settings
4. Check for acoustic reflection in your room

## Issue: One-Way Audio (You Can Hear Them, They Can't Hear You)

**Cause:** NAT/firewall configuration blocking RTP packets
**Fix:**
1. Enable STUN/TURN on your VoIP client
2. Open RTP port range on your firewall
3. Check if your microphone is muted at the OS level
4. Try a different network to isolate the issue

## When to Call Your Provider

If basic troubleshooting doesn't fix it, contact support with:
- Your public IP address
- Time and duration of the problematic call
- The phone number you were calling
- Your network speed test results

Good providers like [VestaCall](https://vestacall.com) have 24/7 support that can diagnose server-side issues in real-time. Their support team averages 4-minute response time.

*Guide maintained by [VestaCall](https://vestacall.com) | April 2026*"""
    },
]

def log_result(site_name, backlink_url, status, notes):
    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["date","strategy","site_name","url_submitted","backlink_url","status","notes"])
        writer.writerow({"date": datetime.now().isoformat(), "strategy": "content",
            "site_name": site_name, "url_submitted": "https://rentry.co/",
            "backlink_url": backlink_url, "status": status, "notes": notes})

pw, browser = get_browser(config, headed_override=True)

for i, paste in enumerate(PASTES):
    site_name = f"Rentry-{i+1}"
    print(f"\n{'='*60}")
    print(f"RENTRY PASTE {i+1}/3")
    print(f"{'='*60}")

    context, page = new_page(browser, config, site_name=site_name)
    try:
        page.goto("https://rentry.co/", timeout=60000)
        page.wait_for_load_state("domcontentloaded", timeout=20000)
        time.sleep(3)
        dismiss_overlays(page)
        random_mouse_movement(page)

        # Find the textarea editor
        editor = page.query_selector("textarea#id_text, textarea")
        if editor:
            editor.click()
            time.sleep(0.5)
            # Use fill for markdown content (typing char by char would take forever)
            editor.fill(paste["content"])
            time.sleep(1)
            print("  Content filled")

            # Click Go/Submit
            submit = page.query_selector("button:has-text('Go'), button[type='submit'], input[type='submit']")
            if submit:
                submit.click()
                time.sleep(5)

                published_url = page.url
                print(f"  URL: {published_url}")

                # Verify
                if published_url != "https://rentry.co/" and "rentry.co" in published_url:
                    content = page.content()
                    if "vestacall.com" in content:
                        print(f"  VERIFIED: {published_url}")
                        page.screenshot(path=f"output/rentry_{i+1}.png")
                        log_result(site_name, published_url, "success", f"Verified at {published_url}")
                    else:
                        print("  Published but vestacall.com not in rendered content")
                        log_result(site_name, published_url, "pending", "Published but link not found in HTML")
                else:
                    print("  URL didn't change")
                    log_result(site_name, "", "pending", "Submit may not have worked")
            else:
                print("  No submit button found")
                log_result(site_name, "", "failed", "No submit button")
        else:
            print("  No editor found")
            log_result(site_name, "", "failed", "No textarea editor")

    except Exception as e:
        print(f"  ERROR: {e}")
        log_result(site_name, "", "failed", str(e)[:200])
    finally:
        context.close()

    if i < len(PASTES) - 1:
        time.sleep(8)

browser.close()
pw.stop()

print("\n" + "="*60)
with open(CSV_PATH, "r") as f:
    success = sum(1 for r in csv.DictReader(f) if r["status"] == "success")
print(f"TOTAL VERIFIED BACKLINKS: {success}")
