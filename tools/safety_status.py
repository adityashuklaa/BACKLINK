"""CLI: show current velocity status across all platforms — warning where we're
near caps, BLOCKED where we've hit them.

Run anytime: python tools/safety_status.py
"""
import json
import sys
from datetime import datetime

sys.path.insert(0, ".")
sys.stdout.reconfigure(encoding="utf-8")

from core.safety import velocity_status, DAILY_CAPS


def color(text, code):
    return f"\033[{code}m{text}\033[0m"


def status_color(status):
    return {"OK": "32", "WARN": "33", "BLOCKED": "31"}.get(status, "0")


def main():
    s = velocity_status()
    print("=" * 80)
    print(f"DialPhone Backlink Velocity Status — {s['as_of']}")
    print("=" * 80)
    if s["is_rest_day"]:
        print("\n  REST DAY (Sunday) — automated batches will skip today by default.")

    # Header
    print(f"\n  {'Platform':<35} {'Status':<10} {'24h':>10} {'7d':>10} {'30d':>10} {'24h headroom':>12}")
    print(f"  {'-'*35} {'-'*10} {'-'*10} {'-'*10} {'-'*10} {'-'*12}")

    rows = list(s["platforms"].items())
    rows.sort(key=lambda x: -x[1]["count_30d"])
    for plat, p in rows:
        statu = p["status"]
        c24 = f"{p['count_24h']}/{p['cap_24h']}"
        c7d = f"{p['count_7d']}/{p['cap_7d']}"
        c30d = f"{p['count_30d']}/{p['cap_30d']}"
        head = p["headroom_24h"]
        print(f"  {plat:<35} {statu:<10} {c24:>10} {c7d:>10} {c30d:>10} {head:>12}")

    # Summary
    blocked = [p for p, v in s["platforms"].items() if v["status"] == "BLOCKED"]
    warn = [p for p, v in s["platforms"].items() if v["status"] == "WARN"]
    print(f"\n  BLOCKED ({len(blocked)}): {', '.join(blocked) if blocked else 'none'}")
    print(f"  WARN ({len(warn)}): {', '.join(warn) if warn else 'none'}")

    print("\n  How to read:")
    print("    OK       — safe to publish")
    print("    WARN     — at 80%+ of 24h cap; slow down")
    print("    BLOCKED  — at or above 24h cap; pre_publish_check will reject")

    print("\n  Caps reference (per-platform 24h / 7d / 30d):")
    for plat, caps in DAILY_CAPS.items():
        if plat == "default": continue
        print(f"    {plat:<25} {caps[0]:>5} / {caps[1]:>5} / {caps[2]:>5}")


if __name__ == "__main__":
    main()
