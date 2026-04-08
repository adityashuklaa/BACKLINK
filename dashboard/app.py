"""Backlink Dashboard — Flask web UI for monitoring backlink automation."""
import csv
import os
import json
from datetime import datetime
from collections import Counter
from flask import Flask, render_template, jsonify

app = Flask(__name__)

CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "output", "backlinks_log.csv")
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config.json")


def read_csv():
    rows = []
    if not os.path.exists(CSV_PATH):
        return rows
    with open(CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def read_config():
    if not os.path.exists(CONFIG_PATH):
        return {}
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def get_stats(rows):
    total = len(rows)
    status_counts = Counter(r.get("status", "unknown") for r in rows)
    strategy_counts = Counter(r.get("strategy", "unknown") for r in rows)

    # Group by strategy + status
    strategy_status = {}
    for r in rows:
        s = r.get("strategy", "unknown")
        st = r.get("status", "unknown")
        if s not in strategy_status:
            strategy_status[s] = Counter()
        strategy_status[s][st] += 1

    # Timeline: group by date (just the date part)
    timeline = Counter()
    for r in rows:
        date_str = r.get("date", "")[:10]
        if date_str:
            timeline[date_str] += 1

    return {
        "total": total,
        "status_counts": dict(status_counts),
        "strategy_counts": dict(strategy_counts),
        "strategy_status": {k: dict(v) for k, v in strategy_status.items()},
        "timeline": dict(sorted(timeline.items())),
        "success_rate": round((status_counts.get("success", 0) / total * 100) if total else 0, 1),
        "pending_count": status_counts.get("pending", 0),
        "failed_count": status_counts.get("failed", 0),
        "skipped_count": status_counts.get("skipped", 0),
        "verified_count": status_counts.get("verified", 0),
    }


@app.route("/")
def dashboard():
    rows = read_csv()
    config = read_config()
    stats = get_stats(rows)
    business = config.get("business", {})
    return render_template("dashboard.html", rows=rows, stats=stats, business=business)


@app.route("/api/stats")
def api_stats():
    rows = read_csv()
    stats = get_stats(rows)
    return jsonify(stats)


@app.route("/api/rows")
def api_rows():
    rows = read_csv()
    return jsonify(rows)


if __name__ == "__main__":
    print("\n  Dashboard running at: http://127.0.0.1:5000\n")
    app.run(debug=False, port=5000, use_reloader=False)
