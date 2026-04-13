#!/usr/bin/env python3
"""Generate hourly reports from backlinks_log.csv for Excel paste."""

import csv
from datetime import datetime, timedelta
from collections import defaultdict
import sys

def read_backlinks_log(log_path="output/backlinks_log.csv"):
    """Read backlinks log and return list of records."""
    records = []
    try:
        with open(log_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                records.append(row)
    except FileNotFoundError:
        print(f"⚠️  Log file not found: {log_path}")
        return []
    return records

def generate_hourly_report(records, target_date=None):
    """Generate hourly summary from records."""
    if target_date is None:
        target_date = datetime.utcnow().date()
    elif isinstance(target_date, str):
        target_date = datetime.fromisoformat(target_date).date()

    target_date_str = target_date.isoformat()
    
    # Group by hour
    hourly_data = defaultdict(lambda: {
        "total": 0, "successful": 0, "failed": 0,
        "directories": 0, "social": 0, "profiles": 0, 
        "outreach": 0, "comments": 0,
        "issues": []
    })
    
    # Strategy mapping (normalize names)
    STRATEGY_MAP = {
        "directories": "directories",
        "directory_submissions": "directories",
        "social": "social",
        "social_bookmarking": "social",
        "profiles": "profiles",
        "profile_forum_links": "profiles",
        "forum": "profiles",
        "outreach": "outreach",
        "guest_post_outreach": "outreach",
        "comments": "comments",
        "blog_comment_links": "comments",
        "blog": "comments",
    }
    
    for record in records:
        date_str = record.get("date", "")
        if not date_str:
            continue
        
        # Parse ISO timestamp (e.g., 2026-04-01T08:23:45.123456)
        try:
            record_datetime = datetime.fromisoformat(date_str.split(".")[0])
        except ValueError:
            continue
        
        record_date = record_datetime.date()
        if record_date != target_date:
            continue
        
        hour_key = f"{record_datetime.hour:02d}:00"
        strategy = STRATEGY_MAP.get(record.get("strategy", "").lower(), "unknown")
        status = record.get("status", "").lower()
        
        hourly_data[hour_key]["total"] += 1
        
        if status in ["success", "submitted", "accepted"]:
            hourly_data[hour_key]["successful"] += 1
            if strategy in hourly_data[hour_key]:
                hourly_data[hour_key][strategy] += 1
        elif status == "failed":
            hourly_data[hour_key]["failed"] += 1
        
        # Track issues
        notes = record.get("notes", "")
        if notes and status == "failed":
            hourly_data[hour_key]["issues"].append(notes)
    
    return hourly_data

def format_csv_output(hourly_data, target_date):
    """Format as CSV for Excel paste."""
    target_date_str = target_date.isoformat() if hasattr(target_date, "isoformat") else target_date
    
    # Header
    csv_lines = [
        "Date,Hour,Total_Submissions,Total_Successful,Total_Failed,Success_Rate_Pct,"
        "Directories,Social_Bookmarking,Forum_Profiles,Guest_Post_Outreach,Blog_Comments,"
        "Issues,Overall_Status"
    ]
    
    # All 24 hours
    for hour in range(24):
        hour_key = f"{hour:02d}:00"
        data = hourly_data.get(hour_key, {
            "total": 0, "successful": 0, "failed": 0,
            "directories": 0, "social": 0, "profiles": 0,
            "outreach": 0, "comments": 0, "issues": []
        })
        
        total = data["total"]
        successful = data["successful"]
        failed = data["failed"]
        success_rate = f"{(successful/total*100):.0f}%" if total > 0 else "—"
        
        issues_str = "; ".join(data["issues"][:2]) if data["issues"] else "None"
        status = "✓ On track" if total >= 8 else ("⚠ Low" if total > 0 else "—")
        
        row = f'{target_date_str},{hour_key},{total},{successful},{failed},{success_rate},' \
              f'{data["directories"]},{data["social"]},{data["profiles"]},' \
              f'{data["outreach"]},{data["comments"]},{issues_str},{status}'
        csv_lines.append(row)
    
    return "\n".join(csv_lines)

def format_markdown_output(hourly_data, target_date):
    """Format as Markdown table."""
    target_date_str = target_date.isoformat() if hasattr(target_date, "isoformat") else target_date
    
    lines = [
        f"# Hourly Report — {target_date_str}",
        "",
        "| Hour | Submissions | Successful | Failed | Success % | Directories | Social | Forums | Guest | Blog | Issues |",
        "|------|-------------|-----------|--------|-----------|-------------|--------|--------|-------|------|--------|"
    ]
    
    total_sub = 0
    total_succ = 0
    total_failed = 0
    
    for hour in range(24):
        hour_key = f"{hour:02d}:00"
        data = hourly_data.get(hour_key, {
            "total": 0, "successful": 0, "failed": 0,
            "directories": 0, "social": 0, "profiles": 0,
            "outreach": 0, "comments": 0, "issues": []
        })
        
        total = data["total"]
        successful = data["successful"]
        failed = data["failed"]
        success_rate = f"{(successful/total*100):.0f}%" if total > 0 else "—"
        
        total_sub += total
        total_succ += successful
        total_failed += failed
        
        issues = ": ".join(data["issues"][:1]) if data["issues"] else "—"
        
        row = f"| {hour_key} | {total} | {successful} | {failed} | {success_rate} | {data['directories']} | {data['social']} | {data['profiles']} | {data['outreach']} | {data['comments']} | {issues} |"
        lines.append(row)
    
    # Total row
    overall_rate = f"{(total_succ/total_sub*100):.1f}%" if total_sub > 0 else "—"
    lines.append(f"| **TOTAL** | **{total_sub}** | **{total_succ}** | **{total_failed}** | **{overall_rate}** | — | — | — | — | — | — |")
    
    return "\n".join(lines)

def main():
    """Main entry point."""
    print("📊 VestaCall Hourly Report Generator")
    print("=" * 50)
    
    # Get date from arg or use today
    target_date = sys.argv[1] if len(sys.argv) > 1 else datetime.utcnow().date()
    
    # Read log
    records = read_backlinks_log()
    if not records:
        print("❌ No records found in backlinks_log.csv")
        return 1
    
    # Generate report
    hourly_data = generate_hourly_report(records, target_date)
    
    # Format outputs
    print("\n--- CSV (Paste into Excel) ---\n")
    csv_output = format_csv_output(hourly_data, target_date)
    print(csv_output)
    
    print("\n\n--- Markdown (For Documentation) ---\n")
    md_output = format_markdown_output(hourly_data, target_date)
    print(md_output)
    
    print("\n✅ Report Generated Successfully")
    print(f"📅 Date: {target_date}")
    
    # Save to file
    filename = f"reports/hourly_report_{target_date}.csv"
    import os
    os.makedirs("reports", exist_ok=True)
    with open(filename, "w") as f:
        f.write(csv_output)
    print(f"💾 Saved to: {filename}")
    
    return 0

if __name__ == "__main__":
    exit(main())
