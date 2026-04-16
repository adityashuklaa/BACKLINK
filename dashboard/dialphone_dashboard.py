"""DialPhone.com Backlink Dashboard — shows only dialphone.com backlinks."""
import csv
import os
from datetime import datetime
from flask import Flask, render_template_string

app = Flask(__name__)
CSV_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output", "backlinks_log.csv")

TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DialPhone.com Backlink Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #0a0a1a; color: #e0e0e0; }
        .header { background: linear-gradient(135deg, #1a1a3e, #2d1b69); padding: 30px 40px; border-bottom: 2px solid #4a3f8a; }
        .header h1 { font-size: 28px; color: #fff; }
        .header .subtitle { color: #a0a0c0; margin-top: 5px; font-size: 14px; }
        .stats { display: flex; gap: 20px; padding: 25px 40px; flex-wrap: wrap; }
        .stat-card { background: #12122a; border: 1px solid #2a2a4a; border-radius: 12px; padding: 20px 25px; min-width: 180px; flex: 1; }
        .stat-card .label { font-size: 12px; color: #8080a0; text-transform: uppercase; letter-spacing: 1px; }
        .stat-card .value { font-size: 32px; font-weight: 700; color: #fff; margin-top: 5px; }
        .stat-card .value.green { color: #4ade80; }
        .stat-card .value.blue { color: #60a5fa; }
        .stat-card .value.purple { color: #a78bfa; }
        .stat-card .value.orange { color: #fb923c; }
        .domains { padding: 10px 40px 25px; }
        .domains h2 { font-size: 18px; margin-bottom: 15px; color: #c0c0e0; }
        .domain-grid { display: flex; gap: 10px; flex-wrap: wrap; }
        .domain-chip { background: #1a1a3e; border: 1px solid #3a3a6a; border-radius: 8px; padding: 8px 16px; font-size: 13px; }
        .domain-chip .name { color: #a78bfa; font-weight: 600; }
        .domain-chip .count { color: #8080a0; margin-left: 6px; }
        .table-section { padding: 0 40px 40px; }
        .table-section h2 { font-size: 18px; margin-bottom: 15px; color: #c0c0e0; }
        .filters { display: flex; gap: 10px; margin-bottom: 15px; }
        .filter-btn { background: #1a1a3e; border: 1px solid #3a3a6a; color: #c0c0e0; padding: 6px 16px; border-radius: 6px; cursor: pointer; font-size: 13px; }
        .filter-btn.active { background: #4a3f8a; border-color: #6a5faa; color: #fff; }
        table { width: 100%; border-collapse: collapse; }
        th { text-align: left; padding: 10px 12px; background: #12122a; color: #8080a0; font-size: 11px; text-transform: uppercase; letter-spacing: 1px; border-bottom: 1px solid #2a2a4a; }
        td { padding: 10px 12px; border-bottom: 1px solid #1a1a2e; font-size: 13px; }
        tr:hover { background: #15152e; }
        .badge { padding: 3px 10px; border-radius: 4px; font-size: 11px; font-weight: 600; }
        .badge.success { background: #065f46; color: #4ade80; }
        .badge.dofollow { background: #1e3a5f; color: #60a5fa; }
        .badge.partial { background: #78350f; color: #fbbf24; }
        a { color: #818cf8; text-decoration: none; }
        a:hover { text-decoration: underline; }
        .footer { text-align: center; padding: 20px; color: #4a4a6a; font-size: 12px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>DialPhone.com Backlink Dashboard</h1>
        <div class="subtitle">Target: dialphone.com | Last updated: {{ updated }} | Only showing dialphone.com backlinks</div>
    </div>

    <div class="stats">
        <div class="stat-card">
            <div class="label">Total Backlinks</div>
            <div class="value green">{{ total }}</div>
        </div>
        <div class="stat-card">
            <div class="label">Referring Domains</div>
            <div class="value blue">{{ domains_count }}</div>
        </div>
        <div class="stat-card">
            <div class="label">Dofollow</div>
            <div class="value purple">{{ dofollow }}</div>
        </div>
        <div class="stat-card">
            <div class="label">Quora Answers</div>
            <div class="value orange">{{ quora }}</div>
        </div>
    </div>

    <div class="domains">
        <h2>Referring Domains</h2>
        <div class="domain-grid">
            {% for domain, count in domain_list %}
            <div class="domain-chip">
                <span class="name">{{ domain }}</span>
                <span class="count">({{ count }})</span>
            </div>
            {% endfor %}
        </div>
    </div>

    <div class="table-section">
        <h2>DialPhone.com Backlinks ({{ total }})</h2>
        <table>
            <thead>
                <tr>
                    <th>Date</th>
                    <th>Platform</th>
                    <th>URL</th>
                    <th>Type</th>
                    <th>Notes</th>
                </tr>
            </thead>
            <tbody>
                {% for row in rows %}
                <tr>
                    <td>{{ row.date[:16] }}</td>
                    <td>{{ row.site_name }}</td>
                    <td><a href="{{ row.backlink_url }}" target="_blank">{{ row.backlink_url[:60] }}{% if row.backlink_url|length > 60 %}...{% endif %}</a></td>
                    <td>
                        {% if 'DOFOLLOW' in row.notes or 'dofollow' in row.notes %}
                        <span class="badge dofollow">DOFOLLOW</span>
                        {% elif 'quora' in row.site_name|lower %}
                        <span class="badge success">BUYER</span>
                        {% else %}
                        <span class="badge success">LIVE</span>
                        {% endif %}
                    </td>
                    <td>{{ row.notes[:50] }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>

    <div class="footer">
        DialPhone Backlink Dashboard | Auto-refreshes on page reload
    </div>
</body>
</html>
"""

@app.route("/")
def dashboard():
    rows = []
    with open(CSV_PATH, "r", encoding="utf-8", errors="replace") as f:
        for r in csv.DictReader(f):
            if r["status"] == "success":
                url = r.get("backlink_url", "")
                notes = r.get("notes", "")
                # Only show dialphone.com backlinks
                if "dialphone" in notes.lower() or "dialphone" in url.lower() or r.get("date", "") >= "2026-04-16":
                    rows.append(r)

    # Deduplicate
    seen = set()
    unique = []
    for r in rows:
        url = r.get("backlink_url", "")
        if url and url not in seen:
            seen.add(url)
            unique.append(r)

    # Sort newest first
    unique.sort(key=lambda x: x.get("date", ""), reverse=True)

    # Count domains
    domains = {}
    for r in unique:
        url = r.get("backlink_url", "")
        if "//" in url:
            d = url.split("//")[1].split("/")[0]
            if "github" in d and "gist" not in d:
                d = "github.com"
            domains[d] = domains.get(d, 0) + 1

    domain_list = sorted(domains.items(), key=lambda x: -x[1])

    # Count dofollow
    dofollow = sum(1 for r in unique if "dofollow" in r.get("notes", "").lower() or "DOFOLLOW" in r.get("notes", ""))
    quora = sum(1 for r in unique if "quora" in r.get("site_name", "").lower())

    return render_template_string(TEMPLATE,
        total=len(unique),
        domains_count=len(domains),
        dofollow=dofollow,
        quora=quora,
        domain_list=domain_list,
        rows=unique,
        updated=datetime.now().strftime("%Y-%m-%d %H:%M"),
    )

if __name__ == "__main__":
    print("\n  DialPhone Dashboard running at: http://127.0.0.1:5001\n")
    app.run(port=5001, debug=False)
