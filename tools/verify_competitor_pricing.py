"""Scrape every competitor's public pricing page with Playwright stealth.

For each provider, records: rendered price mentions, visible plan names, timestamp.
Saves to output/pricing_audit_2026.json for the calculator to ingest.

Providers that block scrapers get flagged 'unverified' — at least then we know.
"""
import json
import re
import sys
import time
from datetime import datetime

sys.path.insert(0, ".")
sys.stdout.reconfigure(encoding="utf-8")

from core.browser import get_browser, new_page

CFG = json.load(open("config.json"))

TARGETS = [
    ("DialPhone",            "https://dialphone.com/pricing-overview/",                     [20, 30, 40, 55]),
    ("RingCentral",          "https://www.ringcentral.com/office/plansandpricing.html",     [30, 35, 45]),
    ("8x8",                  "https://www.8x8.com/products/all-products/8x8-work-pricing",  [28, 57, 85]),
    ("Dialpad",              "https://www.dialpad.com/pricing/",                            [15, 25]),
    ("Nextiva",              "https://www.nextiva.com/pricing",                             [21, 26, 37]),
    ("Vonage",               "https://www.vonage.com/unified-communications/pricing/",       [20, 30, 40]),
    ("GoTo Connect",         "https://www.goto.com/connect/pricing",                        [27, 32]),
    ("Zoom Phone",           "https://zoom.us/en/pricing/phone-plans.html",                 [10, 15, 20]),
    ("Ooma",                 "https://www.ooma.com/business-phone-service/",                [20, 25]),
    ("Grasshopper",          "https://grasshopper.com/pricing/",                            [29, 49, 89]),
    ("OpenPhone / Quo",      "https://www.quo.com/pricing",                                 [19, 33]),
    ("Microsoft Teams Phone","https://www.microsoft.com/en-us/microsoft-teams/voice",       [20, 36]),
    ("Google Voice",         "https://workspace.google.com/products/voice/",                [10, 20, 30]),
]

PRICE_RE = re.compile(r"\$\s?(\d{1,3}(?:\.\d{2})?)\s*(?:/|per|\s+per)", re.I)
PRICE_RE_BROAD = re.compile(r"\$\s?(\d{1,3}(?:\.\d{2})?)")


def scrape_one(name, url, expected):
    pw, browser = get_browser(CFG, headed_override=False)
    ctx, page = new_page(browser, CFG, f"pricing-{name.lower().replace(' ','-')}")
    result = {
        "provider": name,
        "url": url,
        "expected_prices_in_calculator": expected,
        "scraped_at": datetime.now().isoformat(),
        "status": "unknown",
        "prices_found_precise": [],
        "prices_found_broad": [],
        "text_length": 0,
        "notes": "",
    }
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=25000)
        page.wait_for_timeout(6000)
        text = page.inner_text("body")
        result["text_length"] = len(text)

        if "403" in text[:200] or "forbidden" in text.lower()[:300] or len(text) < 500:
            result["status"] = "blocked_or_empty"
            result["notes"] = text[:200]
            return result

        precise = sorted({float(m.group(1)) for m in PRICE_RE.finditer(text) if 5 <= float(m.group(1)) <= 200})
        broad = sorted({float(m.group(1)) for m in PRICE_RE_BROAD.finditer(text) if 5 <= float(m.group(1)) <= 200})
        result["prices_found_precise"] = precise
        result["prices_found_broad"] = broad

        # Check if any expected price shows up
        matched = [p for p in expected if p in precise or p in broad]
        result["matched_expected"] = matched
        result["match_ratio"] = len(matched) / len(expected) if expected else 0

        if result["match_ratio"] >= 0.5:
            result["status"] = "verified"
        elif precise or broad:
            result["status"] = "rendered_but_prices_differ"
        else:
            result["status"] = "no_prices_found"
    except Exception as e:
        result["status"] = "error"
        result["notes"] = str(e)[:200]
    finally:
        try: ctx.close(); browser.close(); pw.stop()
        except: pass
    return result


def main():
    results = []
    for i, (name, url, expected) in enumerate(TARGETS):
        print(f"[{i+1}/{len(TARGETS)}] {name}")
        r = scrape_one(name, url, expected)
        print(f"  status={r['status']} len={r.get('text_length',0)} precise={r.get('prices_found_precise',[])[:8]} match_ratio={r.get('match_ratio',0):.1f}")
        results.append(r)
        time.sleep(3)

    with open("output/pricing_audit_2026.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved: output/pricing_audit_2026.json")

    # Summary
    statuses = {}
    for r in results:
        statuses.setdefault(r["status"], []).append(r["provider"])
    print("\n=== SUMMARY ===")
    for s, names in statuses.items():
        print(f"  {s}: {', '.join(names)}")


if __name__ == "__main__":
    sys.exit(main())
