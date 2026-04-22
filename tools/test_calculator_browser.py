"""Load the live calculator in a real browser, check for JS errors + validate UX."""
import json
import sys

sys.path.insert(0, ".")
sys.stdout.reconfigure(encoding="utf-8")

from core.browser import get_browser, new_page

CFG = json.load(open("config.json"))

URL = "https://dialphonelimited.codeberg.page/calculator/"


def main():
    pw, browser = get_browser(CFG, headed_override=False)
    ctx, page = new_page(browser, CFG, "calc-browser-test")

    console_msgs = []
    page_errors = []
    page.on("console", lambda msg: console_msgs.append(f"[{msg.type}] {msg.text}"))
    page.on("pageerror", lambda err: page_errors.append(str(err)))

    try:
        print(f"[1] Loading {URL}")
        page.goto(URL, wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(4000)

        print(f"[2] Page loaded, checking state...")
        title = page.title()
        print(f"  Title: {title}")

        # Check key elements rendered
        checks = [
            ("Top picks rendered",     "#topPicks .pick-card",         True),
            ("Results table rendered", "#resultsBody tr",              True),
            ("Bar chart canvas",       "#barChart",                    True),
            ("Line chart canvas",      "#lineChart",                   True),
            ("Pie chart canvas",       "#pieChart",                    True),
            ("Radar chart canvas",     "#radarChart",                  True),
            ("Feature weights",        "#features .importance-item",   True),
            ("Scenarios section",      "#scenariosList",               True),
        ]
        failures = []
        for name, selector, should_exist in checks:
            els = page.query_selector_all(selector)
            ok = (len(els) > 0) == should_exist
            mark = "✓" if ok else "✗"
            print(f"  {mark} {name}: {len(els)} element(s)")
            if not ok: failures.append(name)

        # Measure top picks count
        picks = page.query_selector_all("#topPicks .pick-card")
        print(f"\n[3] Top picks: {len(picks)}")

        # Measure rows
        rows = page.query_selector_all("#resultsBody tr")
        print(f"[4] Result rows: {len(rows)} (expected 13 providers)")

        # Measure chart dimensions
        for id_ in ("barChart", "lineChart", "pieChart", "radarChart"):
            chart = page.query_selector(f"#{id_}")
            if chart:
                box = chart.bounding_box()
                if box:
                    print(f"  {id_} size: {box['width']:.0f} x {box['height']:.0f}")

        # Test interaction: change user count
        print(f"\n[5] Interaction test: change user count to 100")
        page.fill("#users", "100")
        page.evaluate("document.getElementById('users').dispatchEvent(new Event('input'))")
        page.wait_for_timeout(500)
        label = page.inner_text("#usersLabel")
        print(f"  users label now: {label}")

        # Test theme toggle
        print(f"\n[6] Theme toggle test")
        page.click("#themeToggle")
        page.wait_for_timeout(500)
        theme = page.evaluate("document.body.dataset.theme")
        print(f"  theme: {theme}")

        # Test a weight click
        print(f"\n[7] Weight pill click test")
        first_pill = page.query_selector("[data-weight='3']")
        if first_pill:
            first_pill.click()
            page.wait_for_timeout(300)
            print("  ✓ weight pill clicked")

        # Screenshot
        page.screenshot(path="output/calculator_screenshot.png", full_page=True)
        print(f"\n[8] Screenshot saved to output/calculator_screenshot.png")

        # Final report
        print(f"\n=== RESULTS ===")
        print(f"Element checks failed: {len(failures)} ({', '.join(failures) if failures else 'none'})")
        print(f"\nConsole messages ({len(console_msgs)}):")
        for m in console_msgs[:20]:
            print(f"  {m}")
        print(f"\nJS page errors ({len(page_errors)}):")
        for e in page_errors:
            print(f"  ERROR: {e}")

        # Exit code summary
        if page_errors:
            print("\n❌ HAS PAGE ERRORS")
            return 2
        if failures:
            print("\n⚠️ HAS MISSING ELEMENTS")
            return 1
        print("\n✅ ALL CHECKS PASSED")
        return 0

    except Exception as e:
        print(f"\nEXC: {e}")
        return 3
    finally:
        try: ctx.close(); browser.close(); pw.stop()
        except: pass


if __name__ == "__main__":
    sys.exit(main())
