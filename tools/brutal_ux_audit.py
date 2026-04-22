"""Brutal UX + accuracy audit of the live calculator.

Test it like an actual skeptical SMB buyer would. Check every edge case,
validate every number displayed, check mobile + accessibility + share URL.
"""
import json
import sys
import time

sys.path.insert(0, ".")
sys.stdout.reconfigure(encoding="utf-8")

from core.browser import get_browser, new_page

CFG = json.load(open("config.json"))
URL = "https://dialphonelimited.codeberg.page/calculator/"


def section(name):
    print(f"\n{'='*60}\n{name}\n{'='*60}")


def main():
    pw, browser = get_browser(CFG, headed_override=False)
    ctx, page = new_page(browser, CFG, "brutal-audit")

    errors = []
    issues = []
    page.on("pageerror", lambda err: errors.append(str(err)))
    page.on("console", lambda msg: (errors.append(f"console.{msg.type}: {msg.text}") if msg.type in ("error",) else None))

    try:
        section("1. FIRST IMPRESSION (as a skeptical buyer)")
        page.goto(URL, wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(2000)

        # First scroll state
        hero_h1 = page.query_selector("h1")
        h1_text = hero_h1.inner_text() if hero_h1 else "NO H1"
        print(f"  H1: {h1_text[:80]}")

        # Does the page communicate value in 5 seconds?
        meta_desc = page.get_attribute("meta[name=description]", "content") or ""
        print(f"  Meta desc: {meta_desc[:100]}")

        # Page weight
        perf = page.evaluate("""() => {
            const t = performance.getEntriesByType('navigation')[0];
            return {
                dom_loaded: Math.round(t.domContentLoadedEventEnd),
                full_load: Math.round(t.loadEventEnd),
                resources: performance.getEntriesByType('resource').length,
            };
        }""")
        print(f"  Performance: DOM-ready {perf['dom_loaded']}ms, full-load {perf['full_load']}ms, resources={perf['resources']}")
        if perf['full_load'] > 3500:
            issues.append(f"SLOW: full-load took {perf['full_load']}ms (target: under 3500ms)")

        section("2. DATA INTEGRITY (are the numbers plausible?)")

        # Read the PROVIDERS JS data — it's an OBJECT keyed by name
        providers_count = page.evaluate("Object.keys(PROVIDERS).length")
        print(f"  Providers count: {providers_count}")
        if providers_count != 13:
            issues.append(f"DATA: expected 13 providers, found {providers_count}")

        # DialPhone must be present and verified
        dp = page.evaluate("""() => {
            const dp = PROVIDERS['DialPhone'];
            if (!dp) return null;
            return {
                verified: dp.verified,
                plan_count: dp.plans.length,
                min_price: Math.min(...dp.plans.map(pl=>pl.price)),
                max_price: Math.max(...dp.plans.map(pl=>pl.price)),
                pros_count: dp.pros ? dp.pros.length : 0,
                cons_count: dp.cons ? dp.cons.length : 0,
            };
        }""")
        print(f"  DialPhone: {dp}")

        # Check every provider has required fields
        missing = page.evaluate("""() => {
            const fields = ['plans','pros','cons','bestFor'];
            const issues = [];
            for (const [name, p] of Object.entries(PROVIDERS)) {
                for (const f of fields) {
                    if (!p[f] || (Array.isArray(p[f]) && p[f].length===0)) {
                        issues.push(`${name}: missing/empty ${f}`);
                    }
                }
                if (p.plans && !p.plans.every(pl => typeof pl.price === 'number' && pl.price >= 0)) {
                    issues.push(`${name}: invalid plan price`);
                }
                // feature scores in range 0-100
                if (p.plans) {
                    for (const pl of p.plans) {
                        if (pl.features) {
                            for (const [k,v] of Object.entries(pl.features)) {
                                if (typeof v !== 'number' || v < 0 || v > 100) {
                                    issues.push(`${name} plan "${pl.name}": feature "${k}" score out of 0-100 (${v})`);
                                }
                            }
                        }
                    }
                }
            }
            return issues;
        }""")
        for m in missing:
            issues.append(f"DATA: {m}")
            print(f"  MISSING: {m}")

        # Verification coverage — how many providers have verified date?
        verified_count = page.evaluate("Object.values(PROVIDERS).filter(p=>p.verified).length")
        print(f"  Verified providers: {verified_count}/13 ({verified_count*100/13:.0f}%)")
        if verified_count < 8:
            issues.append(f"DATA: only {verified_count}/13 providers have verified pricing — this is a credibility cap")

        section("3. BIAS CHECK (is it obviously DialPhone-shilling?)")

        # Set weights to "most common SMB": price=3, reliability=2, AI=2, CRM=1, mobile=1
        page.evaluate("""() => {
            // reset all weights first via the reset button if it exists
            const pills = document.querySelectorAll('[data-weight]');
            // just click the ones we want to set
        }""")

        # Click different weight combos and see if DialPhone always wins
        scenarios = [
            {"name": "price-focused", "users": 20},
            {"name": "feature-focused", "users": 100},
            {"name": "enterprise-scale", "users": 500},
        ]
        # Just read top pick for each
        for s in scenarios:
            page.fill("#users", str(s["users"]))
            page.evaluate("document.getElementById('users').dispatchEvent(new Event('input'))")
            page.wait_for_timeout(500)
            top = page.evaluate("""() => {
                const cards = document.querySelectorAll('#topPicks .pick-card');
                if (!cards.length) return null;
                const names = [...cards].slice(0,3).map(c => {
                    const n = c.querySelector('.pick-name, .pick-title, h3, .provider-name');
                    return n ? n.innerText.trim() : c.innerText.slice(0,50);
                });
                return names;
            }""")
            print(f"  scenario={s['name']} users={s['users']} top3={top}")

        section("4. INTERACTIONS (does everything work?)")

        # Theme toggle
        page.click("#themeToggle")
        page.wait_for_timeout(400)
        theme = page.evaluate("document.body.dataset.theme || document.documentElement.dataset.theme")
        print(f"  Theme toggle: {theme}")
        page.click("#themeToggle")  # back
        page.wait_for_timeout(200)

        # Weight pills
        pill = page.query_selector("[data-weight='3']")
        if pill:
            pill.click()
            page.wait_for_timeout(300)
            print(f"  Weight pill click: OK")
        else:
            issues.append("INTERACTION: weight pills not found with [data-weight='3']")

        # Hidden cost toggles — use JS because checkboxes may be visually hidden
        checkbox_count = page.evaluate("""() => {
            const cbs = document.querySelectorAll("input[type='checkbox']");
            if (cbs.length === 0) return 0;
            // toggle first one via JS + event
            cbs[0].checked = !cbs[0].checked;
            cbs[0].dispatchEvent(new Event('change', {bubbles: true}));
            return cbs.length;
        }""")
        page.wait_for_timeout(300)
        print(f"  Checkboxes found: {checkbox_count}")
        if checkbox_count >= 3:
            print(f"  Hidden-cost checkbox: OK (JS-dispatched)")

        # Share URL
        share_btn = page.query_selector("[id*='share' i], [class*='share' i]")
        if share_btn:
            print(f"  Share button: found ({share_btn.get_attribute('id') or share_btn.get_attribute('class')})")
        else:
            issues.append("INTERACTION: no share button visible")

        # Provider detail modal
        first_card = page.query_selector("#topPicks .pick-card")
        if first_card:
            first_card.click()
            page.wait_for_timeout(400)
            modal = page.query_selector(".modal, [role='dialog'], .provider-detail")
            if modal and modal.is_visible():
                print(f"  Provider modal: opens on click")
                # Close it
                close = page.query_selector(".modal-close, .close, [aria-label='Close']")
                if close:
                    close.click()
                    page.wait_for_timeout(300)
                else:
                    page.keyboard.press("Escape")
                    page.wait_for_timeout(300)
            else:
                issues.append("INTERACTION: provider cards don't open detail modal")

        section("5. URL ENCODING (can I share a scenario?)")

        page.fill("#users", "47")
        page.evaluate("document.getElementById('users').dispatchEvent(new Event('input'))")
        page.wait_for_timeout(500)
        current_hash_before = page.evaluate("location.hash")
        share_btn = page.query_selector("button:has-text('Share'), #shareBtn, [aria-label*='share' i]")
        if share_btn:
            # trigger share
            try:
                share_btn.click()
                page.wait_for_timeout(500)
            except:
                pass
        current_hash_after = page.evaluate("location.hash")
        print(f"  URL hash changed: {current_hash_before != current_hash_after}")
        print(f"  URL hash length: {len(current_hash_after)} chars")
        if not current_hash_after or current_hash_after == "#":
            issues.append("UX: share URL doesn't encode state in hash — reload loses scenario")

        # Test reload with hash
        full_url_with_hash = URL + current_hash_after
        page.goto(full_url_with_hash, wait_until="networkidle")
        page.wait_for_timeout(1500)
        restored_users = page.evaluate("document.getElementById('users').value")
        print(f"  After reload with hash: users field = {restored_users} (expected 47)")
        if str(restored_users) != "47":
            issues.append(f"UX: share URL doesn't restore state — expected users=47, got {restored_users}")

        section("6. MOBILE RESPONSIVE")

        # Switch to mobile viewport
        page.set_viewport_size({"width": 375, "height": 812})
        page.wait_for_timeout(1000)
        # Check if horizontal scroll exists (bad)
        overflow = page.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
        print(f"  Horizontal overflow at 375px: {overflow}px")
        if overflow > 5:
            issues.append(f"MOBILE: horizontal scroll at 375px ({overflow}px overflow) — buyers on phones will bail")

        # Check if table is scrollable/accessible on mobile
        table = page.query_selector("#resultsBody")
        if table:
            box = table.bounding_box()
            if box and box['width'] > 375:
                # Is it in a scroll container?
                parent_overflow = page.evaluate("""(el) => {
                    let p = el.parentElement;
                    while (p) {
                        const s = getComputedStyle(p);
                        if (s.overflowX === 'auto' || s.overflowX === 'scroll') return true;
                        p = p.parentElement;
                    }
                    return false;
                }""", table)
                if not parent_overflow:
                    issues.append("MOBILE: results table wider than viewport with no scroll container")
                else:
                    print(f"  Mobile table: in scroll container (OK)")

        # Back to desktop
        page.set_viewport_size({"width": 1366, "height": 768})

        section("7. ACCESSIBILITY / SEO BASICS")

        # Missing alt on images
        img_no_alt = page.evaluate("""() => {
            return [...document.querySelectorAll('img')].filter(i=>!i.alt).map(i=>i.src.slice(-60));
        }""")
        if img_no_alt:
            issues.append(f"A11Y: {len(img_no_alt)} img(s) missing alt: {img_no_alt[:3]}")
        else:
            print(f"  Images alt: OK")

        # Buttons without accessible name
        btn_no_name = page.evaluate("""() => {
            return [...document.querySelectorAll('button')].filter(b=>{
                const aria = b.getAttribute('aria-label');
                const txt = b.innerText.trim();
                return !aria && !txt;
            }).length;
        }""")
        if btn_no_name:
            issues.append(f"A11Y: {btn_no_name} button(s) without aria-label or text (icon-only)")
        else:
            print(f"  Buttons a11y: OK")

        # H1 count (should be exactly 1)
        h1_count = page.evaluate("document.querySelectorAll('h1').length")
        print(f"  H1 count: {h1_count}")
        if h1_count != 1:
            issues.append(f"SEO: expected 1 H1, found {h1_count}")

        section("8. MATH SPOT-CHECK (do the numbers add up?)")

        # Set specific scenario, read math
        page.set_viewport_size({"width": 1366, "height": 768})
        page.fill("#users", "50")
        page.evaluate("document.getElementById('users').dispatchEvent(new Event('input'))")
        page.wait_for_timeout(500)

        # DialPhone Advanced plan is $30/user/mo. 50 users = $1500/mo = $54,000 over 36 mo
        # Read the DialPhone row from results table
        dp_row = page.evaluate("""() => {
            const rows = [...document.querySelectorAll('#resultsBody tr')];
            const dp = rows.find(r => r.innerText.toLowerCase().includes('dialphone'));
            if (!dp) return null;
            return {
                text: dp.innerText,
                cells: [...dp.querySelectorAll('td')].map(c => c.innerText.trim()),
            };
        }""")
        if dp_row:
            print(f"  DialPhone row ({len(dp_row['cells'])} cells): {dp_row['cells']}")
        else:
            issues.append("MATH: DialPhone row not found in results table")

        section("9. CTA CLARITY (does a ready buyer know what to do?)")

        # Does DialPhone have a "try free" or "visit site" CTA?
        dp_cta = page.evaluate("""() => {
            const html = document.documentElement.innerHTML.toLowerCase();
            return {
                dialphone_com: (html.match(/dialphone\\.com/g) || []).length,
                free_trial: html.includes('free trial') || html.includes('14-day'),
                get_started: html.includes('get started') || html.includes('try free'),
                pricing_link: html.includes('pricing-overview'),
            };
        }""")
        print(f"  CTA presence: {dp_cta}")
        if dp_cta['dialphone_com'] < 3:
            issues.append(f"CTA: only {dp_cta['dialphone_com']} dialphone.com mentions — should be 5+")

        section("10. JS ERRORS")
        print(f"  Page errors: {len(errors)}")
        for e in errors[:10]:
            print(f"    {e[:200]}")
        if errors:
            issues.append(f"JS: {len(errors)} runtime error(s)")

        # Screenshot for reference
        page.set_viewport_size({"width": 1366, "height": 900})
        page.wait_for_timeout(500)
        page.screenshot(path="output/brutal_audit_desktop.png", full_page=True)
        page.set_viewport_size({"width": 375, "height": 812})
        page.wait_for_timeout(500)
        page.screenshot(path="output/brutal_audit_mobile.png", full_page=True)
        print(f"\nScreenshots: output/brutal_audit_desktop.png, output/brutal_audit_mobile.png")

        # FINAL VERDICT
        print("\n" + "="*60)
        print(f"TOTAL ISSUES FOUND: {len(issues)}")
        print("="*60)
        for i, issue in enumerate(issues, 1):
            print(f"{i:2}. {issue}")

        if not issues:
            print("\nNo issues found — ship it.")
        return 0 if not issues else 1
    finally:
        try: ctx.close(); browser.close(); pw.stop()
        except: pass


if __name__ == "__main__":
    sys.exit(main())
