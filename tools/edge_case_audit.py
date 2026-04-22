"""Edge-case audit: extreme inputs, save/load round-trip, growth projection math."""
import json, sys
sys.path.insert(0, ".")
sys.stdout.reconfigure(encoding="utf-8")
from core.browser import get_browser, new_page

CFG = json.load(open("config.json"))
URL = "https://dialphonelimited.codeberg.page/calculator/"


def main():
    pw, browser = get_browser(CFG, headed_override=False)
    ctx, page = new_page(browser, CFG, "edge-audit")
    page.goto(URL, wait_until="networkidle")
    page.wait_for_timeout(1500)

    issues = []

    def set_users(n):
        page.fill("#users", str(n))
        page.evaluate("document.getElementById('users').dispatchEvent(new Event('input'))")
        page.wait_for_timeout(400)

    def top_row():
        return page.evaluate("""() => {
            const rows = [...document.querySelectorAll('#resultsBody tr')];
            if (!rows.length) return null;
            return rows.map(r => ({
                provider: r.querySelector('td:nth-child(1)')?.innerText?.split('\\n')[0]?.trim() || '',
                plan: r.querySelector('td:nth-child(2)')?.innerText?.trim() || '',
                monthly: r.querySelector('td:nth-child(3)')?.innerText?.trim() || '',
                annual: r.querySelector('td:nth-child(4)')?.innerText?.trim() || '',
                tco: r.querySelector('td:nth-child(5)')?.innerText?.trim() || '',
                fit: r.querySelector('td:nth-child(6)')?.innerText?.trim() || '',
            }));
        }""")

    # 1 user (minimum)
    print("=" * 60 + "\n1. EDGE: 1 user\n" + "=" * 60)
    set_users(1)
    rows = top_row()
    if rows:
        dp = next((r for r in rows if "DialPhone" in r["provider"]), None)
        print(f"  DialPhone at 1 user: plan={dp['plan']} monthly={dp['monthly']}")
        # Expected: Core @ $20/user = $20/mo + hidden costs
        mv = dp["monthly"].split("\n")[0].replace("$","").replace(",","")
        try:
            mv_int = int(mv)
            if mv_int < 15 or mv_int > 50:
                issues.append(f"EDGE: DialPhone at 1 user = ${mv_int}/mo — outside sane range (15-50)")
        except: pass

    # 500 users (max common SMB)
    print("\n" + "=" * 60 + "\n2. EDGE: 500 users\n" + "=" * 60)
    set_users(500)
    rows = top_row()
    if rows:
        dp = next((r for r in rows if "DialPhone" in r["provider"]), None)
        print(f"  DialPhone at 500 users: plan={dp['plan']} monthly={dp['monthly']} annual={dp['annual']} tco={dp['tco']}")
        # Sanity: 500 × $55 = $27,500/mo base; 3-year should be roughly 36x that + growth
        # $27500 × 36 = $990k if flat; with growth could be $1.5M
        tco_raw = dp["tco"].split("\n")[0].replace("$","").replace(",","")
        try:
            tco_int = int(tco_raw)
            if tco_int < 500000 or tco_int > 5000000:
                issues.append(f"EDGE: DialPhone at 500 users 3-year TCO ${tco_int} outside sane range")
        except: pass

    # 0 users (invalid, what does it do?)
    print("\n" + "=" * 60 + "\n3. EDGE: 0 users (should handle gracefully)\n" + "=" * 60)
    set_users(0)
    rows = top_row()
    if rows:
        nan_rows = [r for r in rows if "NaN" in str(r) or "Infinity" in str(r) or "undefined" in str(r)]
        if nan_rows:
            issues.append(f"EDGE: 0 users produces NaN/Infinity in {len(nan_rows)} rows")
            print(f"  BROKEN: {nan_rows[0]}")
        else:
            dp = next((r for r in rows if "DialPhone" in r["provider"]), None)
            print(f"  DialPhone at 0 users: {dp}")

    # Growth projection check
    print("\n" + "=" * 60 + "\n4. GROWTH PROJECTION math\n" + "=" * 60)
    set_users(50)
    growth_select = page.query_selector("#growth")
    if growth_select:
        # 0% growth
        page.select_option("#growth", value="flat")
        page.wait_for_timeout(400)
        rows = top_row()
        dp_flat = next((r for r in rows if "DialPhone" in r["provider"]), None)
        tco_flat = int(dp_flat["tco"].split("\n")[0].replace("$","").replace(",",""))
        # 200% growth
        try:
            page.select_option("#growth", value="aggressive")
        except:
            # Try other values
            opts = page.evaluate("[...document.querySelectorAll('#growth option')].map(o=>o.value)")
            print(f"  growth options: {opts}")
            if opts and len(opts) > 2:
                page.select_option("#growth", value=opts[-1])
        page.wait_for_timeout(400)
        rows = top_row()
        dp_aggr = next((r for r in rows if "DialPhone" in r["provider"]), None)
        tco_aggr = int(dp_aggr["tco"].split("\n")[0].replace("$","").replace(",",""))
        print(f"  50 users × flat:       TCO ${tco_flat:,}")
        print(f"  50 users × aggressive: TCO ${tco_aggr:,}")
        if tco_aggr <= tco_flat:
            issues.append(f"GROWTH: aggressive TCO ({tco_aggr}) should be > flat TCO ({tco_flat})")

    # Billing cycle toggle
    print("\n" + "=" * 60 + "\n5. BILLING cycle toggle\n" + "=" * 60)
    page.select_option("#growth", value="flat")
    page.select_option("#billing", value="monthly")
    page.wait_for_timeout(400)
    rows = top_row()
    dp_mo = next((r for r in rows if "DialPhone" in r["provider"]), None)
    mo_price = int(dp_mo["monthly"].split("\n")[0].replace("$","").replace(",",""))
    page.select_option("#billing", value="annual")
    page.wait_for_timeout(400)
    rows = top_row()
    dp_an = next((r for r in rows if "DialPhone" in r["provider"]), None)
    an_price = int(dp_an["monthly"].split("\n")[0].replace("$","").replace(",",""))
    print(f"  DialPhone @ 50 users monthly billing: ${mo_price}/mo")
    print(f"  DialPhone @ 50 users annual billing:  ${an_price}/mo")
    if mo_price == an_price:
        issues.append("BILLING: monthly vs annual billing produce same price — toggle is broken/no-op")
    else:
        print(f"  Annual discount: {100*(mo_price-an_price)/mo_price:.1f}%")

    # Scenario save/load round-trip
    print("\n" + "=" * 60 + "\n6. SCENARIO save/load round-trip\n" + "=" * 60)
    set_users(77)
    # Open save dialog
    save_btn = page.query_selector("#saveScenario")
    if save_btn:
        # Use a page.evaluate to fake the prompt response
        page.evaluate("window.prompt = () => 'edge-test-scenario-xyz';")
        save_btn.click()
        page.wait_for_timeout(500)
        # Check localStorage
        stored = page.evaluate("JSON.parse(localStorage.getItem('voip_scenarios') || '[]').length")
        print(f"  Scenarios in localStorage after save: {stored}")
        # Change users, then load back
        set_users(10)
        # Click on the saved scenario — find it by text
        # Simpler: call loadScenario directly via exposed global
        page.evaluate("loadScenario(0)")
        page.wait_for_timeout(500)
        restored = page.evaluate("document.getElementById('users').value")
        print(f"  users after load: {restored} (expected 77)")
        if str(restored) != "77":
            issues.append(f"SCENARIO: save/load roundtrip failed — expected 77, got {restored}")
        # Clean up
        page.evaluate("localStorage.removeItem('voip_scenarios')")

    # Chart.js CDN check (what if it fails?)
    print("\n" + "=" * 60 + "\n7. CHART.JS availability\n" + "=" * 60)
    chart_ok = page.evaluate("typeof Chart !== 'undefined' && typeof Chart.register === 'function'")
    print(f"  Chart.js loaded: {chart_ok}")
    if not chart_ok:
        issues.append("CDN: Chart.js CDN not loading — charts will be broken")

    # FINAL
    print("\n" + "=" * 60)
    print(f"TOTAL EDGE-CASE ISSUES: {len(issues)}")
    print("=" * 60)
    for i, x in enumerate(issues, 1):
        print(f"{i:2}. {x}")
    if not issues:
        print("ALL EDGE CASES PASS")
    ctx.close(); browser.close(); pw.stop()


if __name__ == "__main__":
    main()
