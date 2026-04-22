"""Scrape DialPhone homepage for social URLs + addresses via Playwright element query."""
import sys
import re
import json
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, ".")

from core.browser import get_browser, new_page

cfg = json.load(open("config.json"))
pw, browser = get_browser(cfg, headed_override=False)
ctx, page = new_page(browser, cfg, "dialphone-footer-scrape")

try:
    for url in ["https://dialphone.com", "https://dialphone.com/contact-us/"]:
        try:
            page.goto(url, wait_until="networkidle", timeout=25000)
            page.wait_for_timeout(4000)
            print(f"\n=== {url} ===")
            # Query every anchor element
            hrefs = page.eval_on_selector_all("a", "els => els.map(e => e.href)")
            social_roots = ("linkedin.com", "twitter.com", "x.com", "facebook.com", "youtube.com", "github.com")
            seen = set()
            for h in hrefs:
                for root in social_roots:
                    if root in h and h not in seen:
                        seen.add(h)
                        print(f"  social: {h}")
                        break
            # text addresses
            text = page.inner_text("body")
            for m in re.finditer(r"[A-Z][a-zA-Z ]+,\s+[A-Z]{2}\s+\d{5}", text):
                print(f"  addr:   {m.group(0)}")
            # phones
            for m in re.finditer(r"\+?1?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", text):
                print(f"  phone:  {m.group(0)}")
        except Exception as e:
            print(f"  FAIL {url}: {e}")
finally:
    ctx.close()
    browser.close()
    pw.stop()
