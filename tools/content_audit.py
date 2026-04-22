"""Deep content audit — check every factual claim against our own data."""
import json, re, sys
sys.path.insert(0, ".")
sys.stdout.reconfigure(encoding="utf-8")
from core.browser import get_browser, new_page

CFG = json.load(open("config.json"))
URL = "https://dialphonelimited.codeberg.page/calculator/"


def main():
    pw, browser = get_browser(CFG, headed_override=False)
    ctx, page = new_page(browser, CFG, "content-audit")
    page.goto(URL, wait_until="networkidle")
    page.wait_for_timeout(2000)

    data = page.evaluate("""() => {
      const out = {};
      for (const [name, p] of Object.entries(PROVIDERS)) {
        out[name] = {
          min: Math.min(...p.plans.map(pl=>pl.price)),
          max: Math.max(...p.plans.map(pl=>pl.price)),
          plan_count: p.plans.length,
          plan_names: p.plans.map(pl=>pl.name),
          plan_prices: p.plans.map(pl=>pl.price),
          pros: p.pros, cons: p.cons, bestFor: p.bestFor,
          setupFee: p.setupFee, hardware: p.hardwareRequired,
          portingFee: p.portingFee, verified: p.verified || null,
        };
      }
      return out;
    }""")

    print("=" * 70)
    print("1. PRICE LADDER CHECK (claims vs data)")
    print("=" * 70)
    min_prices = sorted([(n, d["min"]) for n, d in data.items()], key=lambda x: x[1])
    for n, p in min_prices:
        mark = " <-- DialPhone" if n == "DialPhone" else ""
        print(f"  ${p:>3d}  {n}{mark}")
    lowest_name, lowest_price = min_prices[0]
    dp_price = data["DialPhone"]["min"]
    print(f"\n  Actual lowest: {lowest_name} @ ${lowest_price}")
    print(f"  DialPhone: ${dp_price}")
    print(f"  {'*** FALSE CLAIM ***' if dp_price > lowest_price else 'OK'}: DialPhone pros claim 'Lowest price in US/CA market'")

    print("\n" + "=" * 70)
    print("2. EVERY DIALPHONE PROS CLAIM, LINE BY LINE")
    print("=" * 70)
    for claim in data["DialPhone"]["pros"]:
        print(f"  - {claim}")

    print("\n" + "=" * 70)
    print("3. UPTIME / SLA CLAIMS ACROSS PROVIDERS")
    print("=" * 70)
    for provider, d in data.items():
        for claim in d["pros"] + d["cons"]:
            if any(k in claim.lower() for k in ["uptime", "sla", "99."]):
                print(f"  {provider}: {claim}")

    print("\n" + "=" * 70)
    print("4. PLAN COUNT (more plans = more buyer-friendly)")
    print("=" * 70)
    for n, d in sorted(data.items(), key=lambda x: -x[1]["plan_count"]):
        names = ", ".join(d["plan_names"])
        prices = "/".join([f"${p}" for p in d["plan_prices"]])
        print(f"  {d['plan_count']} plans  {n:25s} {prices}  ({names})")

    print("\n" + "=" * 70)
    print("5. SETUP FEES / HARDWARE / PORTING — any non-zero claims?")
    print("=" * 70)
    any_nonzero = False
    for n, d in data.items():
        if d["setupFee"] > 0 or d["hardware"] or d["portingFee"] > 0:
            print(f"  {n}: setup=${d['setupFee']} hw={d['hardware']} porting=${d['portingFee']}")
            any_nonzero = True
    if not any_nonzero:
        print("  ALL PROVIDERS: setup=$0, hardware=False, porting=$0")
        print("  *** PROBLEM: Our calculator has 'hidden costs' toggles but no provider actually has any.")
        print("      Toggles are cosmetic — they do nothing because data says everyone is $0 everywhere.")

    print("\n" + "=" * 70)
    print("6. VERIFICATION — who has dates, who doesn't?")
    print("=" * 70)
    for n, d in data.items():
        v = d["verified"] or "ESTIMATED"
        print(f"  {v:>12s}  {n}")

    print("\n" + "=" * 70)
    print("7. BEST-FOR LENGTHS — any too short / too long?")
    print("=" * 70)
    for n, d in data.items():
        bf = d["bestFor"]
        warn = ""
        if len(bf) < 40: warn = " *** too short"
        if len(bf) > 200: warn = " *** too long"
        print(f"  {len(bf):>3d} chars  {n:25s} {bf[:80]}...{warn}")

    print("\n" + "=" * 70)
    print("8. CLAIM CROSS-CHECK (dollar amounts mentioned in pros/cons)")
    print("=" * 70)
    dollar_pattern = re.compile(r"\$(\d{1,3}(?:[\.,]\d{1,3})?)")
    for provider, d in data.items():
        all_claims = d["pros"] + d["cons"] + [d["bestFor"]]
        all_text = " ".join(all_claims)
        amounts = dollar_pattern.findall(all_text)
        if amounts:
            provider_prices = d["plan_prices"]
            for a in amounts:
                af = float(a.replace(",", ""))
                if af not in provider_prices and af > 3:
                    # only flag if it's a suspiciously specific dollar amount
                    if 10 <= af <= 1000:
                        print(f"  {provider}: mentions ${af} — but plans are {provider_prices}. Is this a real ref?")
    ctx.close(); browser.close(); pw.stop()


if __name__ == "__main__":
    main()
