"""Render a 1200x630 og:image PNG for the calculator via Playwright."""
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8")

OG_HTML = """<!DOCTYPE html>
<html>
<head><style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  width: 1200px; height: 630px;
  background: linear-gradient(135deg, #0a0a0a 0%, #1a2332 55%, #0b3954 100%);
  font-family: -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  color: #fff; overflow: hidden; position: relative;
}
.blob1 { position: absolute; top: -120px; right: -120px; width: 480px; height: 480px;
  background: radial-gradient(circle, rgba(82,196,255,0.25) 0%, transparent 65%); }
.blob2 { position: absolute; bottom: -160px; left: -100px; width: 520px; height: 520px;
  background: radial-gradient(circle, rgba(0,230,160,0.18) 0%, transparent 65%); }
.wrap { position: absolute; top: 58px; left: 72px; right: 72px; bottom: 58px;
  display: flex; flex-direction: column; justify-content: space-between; }
.eyebrow { display: inline-flex; align-items: center; gap: 10px;
  font-size: 15px; font-weight: 700; letter-spacing: 2.5px; text-transform: uppercase;
  color: #52c4ff; margin-bottom: 22px; }
.eyebrow .dot { width: 9px; height: 9px; border-radius: 50%; background: #00e6a0; box-shadow: 0 0 12px #00e6a0; }
h1 { font-size: 72px; line-height: 1.02; font-weight: 900; letter-spacing: -1.5px; margin-bottom: 20px; }
h1 .accent { color: #52c4ff; }
.sub { font-size: 26px; color: #c8d3e0; line-height: 1.35; max-width: 920px; font-weight: 400; }
.stats { display: flex; gap: 48px; margin-top: 28px; }
.stat .num { font-size: 56px; font-weight: 900; line-height: 1; color: #fff; }
.stat .lbl { font-size: 15px; color: #8ea2b8; margin-top: 6px; letter-spacing: 0.5px; text-transform: uppercase; }
.footer { display: flex; justify-content: space-between; align-items: flex-end;
  padding-top: 18px; border-top: 1px solid rgba(255,255,255,0.12); }
.brand { font-size: 22px; font-weight: 800; }
.brand .dollar { display: inline-block; width: 42px; height: 42px; line-height: 42px; text-align: center;
  background: #fff; color: #0b3954; border-radius: 10px; margin-right: 12px; font-size: 26px; font-weight: 900;
  vertical-align: middle; }
.url { font-size: 17px; color: #8ea2b8; font-family: "Consolas", monospace; }
.badge { display: inline-block; background: rgba(0,230,160,0.18); color: #00e6a0; border: 1px solid #00e6a0;
  padding: 6px 14px; border-radius: 6px; font-size: 14px; font-weight: 700; letter-spacing: 0.5px;
  text-transform: uppercase; margin-left: 18px; }
</style></head><body>
<div class="blob1"></div><div class="blob2"></div>
<div class="wrap">
  <div>
    <div class="eyebrow"><span class="dot"></span>Business VoIP · 2026 Edition</div>
    <h1>Compare 13 VoIP providers<br><span class="accent">in 30 seconds.</span></h1>
    <div class="sub">Free, interactive calculator. 3-year TCO, hidden costs, shareable results.
      Verified pricing from provider sites.</div>
    <div class="stats">
      <div class="stat"><div class="num">13</div><div class="lbl">Providers</div></div>
      <div class="stat"><div class="num">4</div><div class="lbl">Chart views</div></div>
      <div class="stat"><div class="num">$0</div><div class="lbl">Signup cost</div></div>
      <div class="stat"><div class="num">30s</div><div class="lbl">To first result</div></div>
    </div>
  </div>
  <div class="footer">
    <div class="brand"><span class="dollar">$</span>DialPhone Cost Calculator<span class="badge">Verified 2026</span></div>
    <div class="url">dialphonelimited.codeberg.page/calculator</div>
  </div>
</div>
</body></html>"""


def main():
    out = Path("assets/calculator/og-image.png")
    out.parent.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1200, "height": 630}, device_scale_factor=1)
        page.set_content(OG_HTML, wait_until="networkidle")
        page.screenshot(path=str(out), type="png", full_page=False,
                        clip={"x": 0, "y": 0, "width": 1200, "height": 630})
        browser.close()
    kb = out.stat().st_size / 1024
    print(f"Wrote {out}  ({kb:.1f} KB, 1200x630)")


if __name__ == "__main__":
    main()
