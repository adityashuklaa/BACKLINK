"""Find web pages that mention 'DialPhone' but don't link to dialphone.com.

For each found mention, draft an outreach email the user can send to the author
asking them to add a link to dialphone.com.

Uses Google search operator via a stealth browser, scrapes the top 50-100 results
for the brand term, checks each for an unlinked mention.
"""
import csv
import json
import re
import sys
import time
from urllib.parse import urlparse

import requests

sys.path.insert(0, ".")
sys.stdout.reconfigure(encoding="utf-8")

from core.browser import get_browser, new_page

CFG = json.load(open("config.json"))

# Sites we already own or publish on — skip these in unlinked-mention hunt
OWN_DOMAINS = {
    "dialphone.com", "dialphone.ai",
    "dev.to", "hashnode.dev", "dialphonevoip.hashnode.dev",
    "gitlab.com", "github.com", "codeberg.org",
    "gitlab.io", "github.io", "codeberg.page",
    "quora.com",
}


def search_google_for_mentions():
    """Run a few Google queries looking for DialPhone mentions not on our own domains."""
    queries = [
        '"DialPhone" voip',
        '"DialPhone" business phone',
        '"DialPhone" review',
        '"DialPhone Limited"',
        '"DialPhone" vs RingCentral',
        '"DialPhone" customer',
        '"DialPhone AI Pro"',
        '"dialphone.com"',
        'DialPhone business phone system',
    ]
    pw, browser = get_browser(CFG, headed_override=False)
    ctx, page = new_page(browser, CFG, "mention-search")

    all_results = set()
    try:
        for q in queries:
            try:
                url = f"https://www.google.com/search?q={requests.utils.quote(q)}&num=50&hl=en&gl=us"
                page.goto(url, wait_until="networkidle", timeout=20000)
                page.wait_for_timeout(2000)
                # Extract all organic result URLs
                hrefs = page.eval_on_selector_all("a", "els => els.map(e => e.href)")
                for h in hrefs:
                    if not h.startswith("http"):
                        continue
                    if "google.com" in h or "googleusercontent.com" in h:
                        continue
                    domain = urlparse(h).netloc.lower().replace("www.", "")
                    # Filter out our own domains
                    if any(od in domain for od in OWN_DOMAINS):
                        continue
                    # Ignore generic content platforms that always show up
                    if domain in ("youtube.com", "facebook.com", "twitter.com", "x.com", "linkedin.com", "reddit.com"):
                        continue
                    all_results.add(h.split("#")[0])  # strip fragments
                print(f"[search] '{q}' -> {len(all_results)} unique urls so far")
            except Exception as e:
                print(f"[search err] {q}: {e}")
    finally:
        ctx.close()
        browser.close()
        pw.stop()

    return sorted(all_results)


def check_mention(url):
    """Fetch URL; return (has_dialphone_text, has_dialphone_com_link, page_title, snippet)."""
    try:
        r = requests.get(url, timeout=12, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36"})
        if r.status_code != 200:
            return None
        html = r.text.lower()
        if "dialphone" not in html:
            return None
        has_link = "dialphone.com" in html
        # Extract <title>
        m = re.search(r"<title[^>]*>([^<]+)</title>", r.text, re.I)
        title = m.group(1).strip()[:120] if m else ""
        # Find a snippet around the first dialphone mention
        idx = html.find("dialphone")
        start = max(0, idx - 80)
        end = min(len(html), idx + 120)
        snippet = re.sub(r"\s+", " ", r.text[start:end]).strip()[:250]
        return has_link, title, snippet
    except Exception:
        return None


def main():
    print("[1/3] Searching Google for brand mentions...")
    urls = search_google_for_mentions()
    print(f"[info] {len(urls)} unique candidate URLs to check")

    print("\n[2/3] Checking each for existing dialphone.com link...")
    unlinked = []
    already_linked = []
    errored = []
    for i, url in enumerate(urls):
        if i % 10 == 0:
            print(f"  {i}/{len(urls)}")
        result = check_mention(url)
        if result is None:
            errored.append(url)
            continue
        has_link, title, snippet = result
        if has_link:
            already_linked.append((url, title))
        else:
            unlinked.append((url, title, snippet))

    print(f"\n[3/3] Results:")
    print(f"  Total pages checked:   {len(urls)}")
    print(f"  Mention DialPhone (any form): {len(already_linked) + len(unlinked)}")
    print(f"  Already link to dialphone.com: {len(already_linked)}")
    print(f"  UNLINKED (our targets): {len(unlinked)}")

    # Write output CSV
    with open("output/unlinked_mentions.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["url", "domain", "title", "snippet", "email_template"])
        for url, title, snippet in unlinked:
            domain = urlparse(url).netloc.lower().replace("www.", "")
            template = build_email(url, title, domain)
            w.writerow([url, domain, title, snippet, template])

    # Write already-linked list for reference
    with open("output/already_linked_mentions.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["url", "title"])
        for url, title in already_linked:
            w.writerow([url, title])

    print(f"\nWritten to:")
    print(f"  output/unlinked_mentions.csv  — targets to email")
    print(f"  output/already_linked_mentions.csv — reference")

    print(f"\n=== FIRST 10 UNLINKED TARGETS ===")
    for url, title, _ in unlinked[:10]:
        print(f"  {urlparse(url).netloc:30s} — {title[:70]}")
        print(f"    {url}")

    return 0


def build_email(url, title, domain):
    """Generate an outreach email draft asking the author to add a link."""
    return f"""Subject: Small thing about your DialPhone mention on {domain}

Hi there,

I was reading your piece "{title[:80]}..." and noticed you mentioned DialPhone — thank you for that, much appreciated.

One small thing: the mention doesn't currently link to https://dialphone.com/. Readers who want to learn more hit a dead end. Would you be open to adding the link when you're next updating the page? It's a tiny edit but really helps us (and your readers) connect the dots.

The direct URL for reference is: https://dialphone.com/
Pricing and product info: https://dialphone.com/pricing-overview/

No worries at all if you'd rather not — just thought I'd flag it.

Thanks for the mention either way.
commercial@dialphone.com"""


if __name__ == "__main__":
    sys.exit(main())
