"""Scrape competitor backlink sources via Ahrefs free Backlink Checker.

For each competitor (RingCentral, 8x8, Dialpad, Nextiva, Vonage), fetches the
top referring domains and saves them as targets for outreach. Each competitor
backlink source is a pre-qualified site that already writes about VoIP and
already links to a major VoIP vendor — so they're likely to consider linking to us.
"""
import csv
import json
import re
import sys
import time
from urllib.parse import urlparse, quote

sys.path.insert(0, ".")
sys.stdout.reconfigure(encoding="utf-8")

from core.browser import get_browser, new_page

CFG = json.load(open("config.json"))

COMPETITORS = [
    "ringcentral.com",
    "8x8.com",
    "dialpad.com",
    "nextiva.com",
    "vonage.com",
    "goto.com",
    "zoom.us",
    "ooma.com",
    "grasshopper.com",
    "mitel.com",
]


def scrape_ahrefs_free(domain):
    """Use Ahrefs' free Backlink Checker. Returns list of top referring domains."""
    pw, browser = get_browser(CFG, headed_override=False)
    ctx, page = new_page(browser, CFG, f"ahrefs-{domain}")
    results = []
    try:
        url = f"https://ahrefs.com/backlink-checker/?input={quote(domain)}&mode=subdomains"
        page.goto(url, wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(5000)
        # Try to click "I'm not a robot" or similar if present (skip — not automatable reliably)
        html = page.content()

        # Ahrefs free tool shows top 100 backlinks. Extract the "Referring page" URLs.
        # Look for anchors pointing to external sites (not ahrefs, not the target)
        hrefs = page.eval_on_selector_all("a", "els => els.map(e => e.href)")
        for h in hrefs:
            if not h.startswith("http"):
                continue
            d = urlparse(h).netloc.lower().replace("www.", "")
            if not d or d == domain or "ahrefs" in d or "google" in d:
                continue
            if d.endswith(("cdn.com", "cloudfront.net", "akamai.net")):
                continue
            results.append(h)

        # Also extract from text if tool renders them as text
        texts = re.findall(r'https?://[^\s"\'<>]+', html)
        for t in texts:
            d = urlparse(t).netloc.lower().replace("www.", "")
            if not d or d == domain or "ahrefs" in d or "google" in d:
                continue
            results.append(t)
    except Exception as e:
        print(f"  [err] ahrefs for {domain}: {e}")
    finally:
        ctx.close()
        browser.close()
        pw.stop()

    return list(set(results))


def scrape_serp_who_links(domain):
    """Fallback: Google search for sites linking to competitor."""
    queries = [
        f'"{domain}" VoIP review',
        f'"{domain}" vs',
        f'"{domain}" comparison',
        f'best voip providers "{domain}"',
    ]
    pw, browser = get_browser(CFG, headed_override=False)
    ctx, page = new_page(browser, CFG, f"serp-{domain}")
    results = set()
    try:
        for q in queries:
            try:
                page.goto(f"https://www.google.com/search?q={quote(q)}&num=30", wait_until="networkidle", timeout=15000)
                page.wait_for_timeout(2000)
                hrefs = page.eval_on_selector_all("a", "els => els.map(e => e.href)")
                for h in hrefs:
                    if not h.startswith("http"):
                        continue
                    d = urlparse(h).netloc.lower().replace("www.", "")
                    if not d or d == domain or "google" in d:
                        continue
                    if d in ("youtube.com", "facebook.com", "twitter.com", "x.com", "reddit.com", "pinterest.com"):
                        continue
                    results.add(h.split("#")[0])
            except Exception:
                pass
    finally:
        ctx.close()
        browser.close()
        pw.stop()
    return sorted(results)


def main():
    print(f"Scraping backlink sources for {len(COMPETITORS)} competitors via SERP analysis...")
    domain_to_linkers = {}  # competitor -> set of linking domains
    all_linkers = {}  # linking_domain -> list of competitors it links to

    for i, comp in enumerate(COMPETITORS):
        print(f"\n[{i+1}/{len(COMPETITORS)}] {comp}")
        urls = scrape_serp_who_links(comp)
        print(f"  found {len(urls)} SERP results mentioning '{comp}'")
        domains = set()
        for u in urls:
            d = urlparse(u).netloc.lower().replace("www.", "")
            if d and not d.endswith((".gov", ".edu", ".mil")):
                domains.add(d)
                all_linkers.setdefault(d, set()).add(comp)
        domain_to_linkers[comp] = domains

    # Find domains that link to 2+ competitors (these are industry publications)
    gold = [d for d, comps in all_linkers.items() if len(comps) >= 3]
    silver = [d for d, comps in all_linkers.items() if len(comps) == 2]
    bronze = [d for d, comps in all_linkers.items() if len(comps) == 1]

    print(f"\n=== RESULTS ===")
    print(f"Total unique linking domains: {len(all_linkers)}")
    print(f"  GOLD (link to 3+ competitors — likely industry pubs): {len(gold)}")
    print(f"  SILVER (link to 2 competitors): {len(silver)}")
    print(f"  BRONZE (link to 1): {len(bronze)}")

    # Write results
    with open("output/competitor_backlink_targets.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["tier", "domain", "linked_competitors", "suggested_outreach"])
        for d in sorted(gold):
            w.writerow(["gold", d, ", ".join(sorted(all_linkers[d])), suggest_pitch(d, all_linkers[d])])
        for d in sorted(silver):
            w.writerow(["silver", d, ", ".join(sorted(all_linkers[d])), suggest_pitch(d, all_linkers[d])])
        # Limit bronze to avoid spam — only top 100
        for d in sorted(bronze)[:100]:
            w.writerow(["bronze", d, ", ".join(sorted(all_linkers[d])), suggest_pitch(d, all_linkers[d])])

    print(f"\nOutput: output/competitor_backlink_targets.csv")
    print(f"\n=== TOP 20 GOLD TARGETS ===")
    for d in sorted(gold)[:20]:
        comps = ", ".join(sorted(all_linkers[d]))
        print(f"  {d:40s} -> {comps}")

    return 0


def suggest_pitch(domain, competitors):
    comps = sorted(competitors)
    return f"Email author: 'I noticed you covered {', '.join(list(comps)[:3])} — have you considered DialPhone? Newer entrant, $20/user starting, 99.999% SLA. Happy to provide a demo account if useful.'"


if __name__ == "__main__":
    sys.exit(main())
