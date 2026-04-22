"""Convert a markdown file to a nicely-styled PDF via Playwright headless Chromium.

Usage: python tools/md_to_pdf.py <input.md> <output.pdf>
"""
import sys
from pathlib import Path

import markdown
from playwright.sync_api import sync_playwright

CSS = """
@page { size: A4; margin: 20mm 18mm; }
body {
  font-family: -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  font-size: 10.5pt; line-height: 1.55; color: #1a1a1a; max-width: 100%;
}
h1 { font-size: 22pt; margin: 0 0 6pt; color: #0b3954; border-bottom: 2px solid #0b3954; padding-bottom: 6pt; }
h2 { font-size: 15pt; margin: 18pt 0 6pt; color: #0b3954; border-bottom: 1px solid #d0d7de; padding-bottom: 3pt; }
h3 { font-size: 12pt; margin: 12pt 0 4pt; color: #1f4e79; }
h4 { font-size: 11pt; margin: 8pt 0 3pt; color: #24292f; }
p { margin: 0 0 6pt; }
ul, ol { margin: 0 0 6pt 18pt; padding: 0; }
li { margin-bottom: 3pt; }
strong { color: #0b3954; }
a { color: #0366d6; text-decoration: none; }
code { font-family: "Consolas", "Courier New", monospace; font-size: 9.5pt; background: #f6f8fa; padding: 1px 4px; border-radius: 3px; }
pre { background: #f6f8fa; padding: 8pt; border-radius: 4pt; overflow-x: auto; }
pre code { background: transparent; padding: 0; }
blockquote { margin: 0 0 6pt; padding: 0 12pt; border-left: 3px solid #d0d7de; color: #57606a; }
hr { border: 0; border-top: 1px solid #d0d7de; margin: 14pt 0; }
table { border-collapse: collapse; margin: 6pt 0 10pt; width: 100%; font-size: 10pt; }
th, td { border: 1px solid #d0d7de; padding: 5pt 8pt; text-align: left; vertical-align: top; }
th { background: #f6f8fa; font-weight: 600; color: #0b3954; }
tr:nth-child(even) td { background: #fafbfc; }
em { color: #57606a; }
.footer { margin-top: 18pt; padding-top: 8pt; border-top: 1px solid #d0d7de; font-size: 9pt; color: #57606a; }
"""


def main():
    if len(sys.argv) != 3:
        print("Usage: python md_to_pdf.py <input.md> <output.pdf>")
        sys.exit(1)

    md_path = Path(sys.argv[1])
    pdf_path = Path(sys.argv[2])
    md_text = md_path.read_text(encoding="utf-8")
    html_body = markdown.markdown(
        md_text,
        extensions=["extra", "tables", "sane_lists", "smarty"],
    )
    html_full = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>{md_path.stem}</title>
<style>{CSS}</style></head>
<body>{html_body}</body></html>"""

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_content(html_full, wait_until="networkidle")
        pdf_path.parent.mkdir(parents=True, exist_ok=True)
        page.pdf(
            path=str(pdf_path),
            format="A4",
            margin={"top": "20mm", "bottom": "18mm", "left": "18mm", "right": "18mm"},
            print_background=True,
        )
        browser.close()

    size_kb = pdf_path.stat().st_size / 1024
    print(f"PDF written: {pdf_path}  ({size_kb:.1f} KB)")


if __name__ == "__main__":
    main()
