"""Scrape each outreach target publication's recent VoIP/UCaaS articles.

Goal: pre-fill the [SPECIFIC RECENT ARTICLE] placeholder in outreach_emails_ready_to_send.md
so the user doesn't have to do the 20-min research task before sending.
"""
import json
import re
import sys
import time

sys.path.insert(0, ".")
sys.stdout.reconfigure(encoding="utf-8")

from core.browser import get_browser, new_page

CFG = json.load(open("config.json"))

TARGETS = [
    {
        "name": "UC Today",
        "urls": ["https://www.uctoday.com/unified-communications/", "https://www.uctoday.com/"],
        "keywords": ["voip", "ucaas", "ringcentral", "8x8", "nextiva", "dialpad", "business phone", "cloud phone"],
    },
    {
        "name": "No Jitter",
        "urls": ["https://www.nojitter.com/", "https://www.nojitter.com/ucaas"],
        "keywords": ["voip", "ucaas", "smb", "cloud", "phone", "ringcentral", "8x8"],
    },
    {
        "name": "GetVoIP",
        "urls": ["https://getvoip.com/blog/", "https://getvoip.com/"],
        "keywords": ["best", "compar", "review", "ringcentral", "dialpad", "smb"],
    },
    {
        "name": "WhichVoIP",
        "urls": ["https://whichvoip.com/blog/", "https://whichvoip.com/"],
        "keywords": ["review", "best", "compar", "voip", "business phone"],
    },
    {
        "name": "Forbes Advisor",
        "urls": ["https://www.forbes.com/advisor/business/software/best-voip/", "https://www.forbes.com/advisor/business/software/"],
        "keywords": ["voip", "business phone", "best", "small business"],
    },
    {
        "name": "BusinessNewsDaily",
        "urls": ["https://www.businessnewsdaily.com/business-phone-systems.html", "https://www.businessnewsdaily.com/"],
        "keywords": ["voip", "business phone", "ringcentral", "8x8", "nextiva"],
    },
    {
        "name": "TechRadar Pro",
        "urls": ["https://www.techradar.com/pro/unified-communications", "https://www.techradar.com/pro/best-voip"],
        "keywords": ["voip", "ucaas", "business phone", "unified communication"],
    },
    {
        "name": "PCMag",
        "urls": ["https://www.pcmag.com/categories/voip", "https://www.pcmag.com/picks/the-best-business-voip-services"],
        "keywords": ["voip", "business phone", "ringcentral", "8x8", "dialpad"],
    },
]


def extract_candidate_articles(page_html, keywords):
    """Find article titles/links on the page that mention VoIP/UCaaS topics."""
    # naive approach: find all <a> hrefs with link text, filter by keyword
    pattern = re.compile(r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>([^<]{15,180})</a>', re.I)
    found = []
    for m in pattern.finditer(page_html):
        href, text = m.group(1), re.sub(r"\s+", " ", m.group(2)).strip()
        lower = text.lower()
        if any(k in lower for k in keywords) and "?" not in href and "#" not in href[-20:]:
            found.append({"title": text, "url": href})
    # Dedup by title
    seen = set()
    unique = []
    for f in found:
        if f["title"] not in seen:
            seen.add(f["title"])
            unique.append(f)
    return unique[:8]


def main():
    pw, browser = get_browser(CFG, headed_override=False)
    ctx, page = new_page(browser, CFG, "article-research")
    results = {}

    for t in TARGETS:
        print(f"\n=== {t['name']} ===")
        articles = []
        for u in t["urls"]:
            try:
                page.goto(u, wait_until="domcontentloaded", timeout=25000)
                page.wait_for_timeout(3000)
                html = page.content()
                candidates = extract_candidate_articles(html, t["keywords"])
                print(f"  {u} -> {len(candidates)} candidates")
                articles.extend(candidates)
                if len(articles) >= 5:
                    break
            except Exception as e:
                print(f"  {u} -> ERROR {str(e)[:100]}")
        # Dedup
        seen = set()
        unique = []
        for a in articles:
            if a["title"] not in seen:
                seen.add(a["title"])
                unique.append(a)
        results[t["name"]] = unique[:5]
        time.sleep(2)

    print("\n" + "=" * 70)
    print("TOP CANDIDATES PER PUBLICATION")
    print("=" * 70)
    for name, arts in results.items():
        print(f"\n{name}:")
        if not arts:
            print("  (none found — use generic pitch)")
        for a in arts:
            print(f"  - {a['title'][:120]}")

    with open("output/publication_recent_articles.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved: output/publication_recent_articles.json")

    try: ctx.close(); browser.close(); pw.stop()
    except: pass


if __name__ == "__main__":
    main()
