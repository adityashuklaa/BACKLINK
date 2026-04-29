"""One-time: backfill core/safety velocity log from the existing
backlinks_log.csv so today's published items are reflected in the
caps for the next 30 days.
"""
import csv
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, ".")
sys.stdout.reconfigure(encoding="utf-8")

from core.safety import LOG_PATH, _normalize_platform


def main():
    rows = list(csv.DictReader(open("output/backlinks_log.csv", encoding="utf-8")))

    cutoff = datetime.now() - timedelta(days=60)
    entries = []
    for r in rows:
        try:
            ts = datetime.fromisoformat(r["date"])
        except Exception:
            continue
        if ts < cutoff:
            continue
        if r.get("status") != "success":
            continue
        url = r.get("backlink_url", "")
        if not url:
            continue
        try:
            host = urlparse(url).netloc
        except Exception:
            continue
        platform = _normalize_platform(host)
        entries.append({
            "ts": ts.isoformat(),
            "platform": platform,
            "url": url,
            "strategy": r.get("strategy", ""),
            "content_excerpt": "",  # we don't have the content text in the log
        })

    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2, default=str)

    # Summarize
    from collections import Counter
    plats = Counter(e["platform"] for e in entries)
    print(f"Backfilled {len(entries)} entries across {len(plats)} platforms")
    for p, c in plats.most_common():
        print(f"  {p:35s} {c}")
    print(f"\nWritten to: {LOG_PATH}")


if __name__ == "__main__":
    main()
