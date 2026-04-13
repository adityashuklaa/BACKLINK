# 📊 Hourly Report System — Quick Start

Your hourly tracking system is now ready. Here's how to use it:

---

## **Option 1: Manual Excel Template (Simplest)**

### Steps:

1. **Open** [HOURLY_REPORT_TEMPLATE.md](HOURLY_REPORT_TEMPLATE.md)
2. **Copy the summary table** from the "Summary (Paste into Excel)" section
3. **Paste into Excel** as a new row for each hour
4. **Fill in your data** from your monitoring dashboard

### Fields to Track Each Hour:

| Field | How to Get This |
|-------|-----------------|
| **Hour** | Current time (e.g., 08:00) |
| **Submissions** | Count from your logs/dashboard |
| **Successful** | Count of "accepted" status |
| **Failed** | Count of "failed" status |
| **Success Rate** | Successful ÷ Submissions × 100 |
| **Strategy Breakdown** | Count per strategy (Directories, Social, Forums, Guest, Blog) |
| **Issues** | Any rate-limits, CAPTCHAs, delays |
| **Owner** | Who ran this hour |

### Example Excel Row:

```
2026-04-10 | 08:00 | 12 | 9 | 75% | 3 | 2 | 1 | 4 | 2 | None
```

---

## **Option 2: Auto-Generated from Logs (Best)**

### Steps:

1. **Run the script** (automatically reads your CSV logs):
   ```bash
   python generate_hourly_report.py
   ```

2. **For a specific date**:
   ```bash
   python generate_hourly_report.py 2026-04-10
   ```

3. **Output**:
   - CSV version (ready to paste into Excel)
   - Markdown version (for documentation)
   - Saved file: `reports/hourly_report_YYYY-MM-DD.csv`

### What It Does:

- ✅ Reads your `output/backlinks_log.csv` 
- ✅ Groups submissions by hour
- ✅ Counts by strategy
- ✅ Automatically calculates success rates
- ✅ Identifies issues from failed entries

### Example Command Sequence:

```bash
# Generate report for today
python generate_hourly_report.py

# Generate for specific date
python generate_hourly_report.py 2026-04-05

# Pipe to Excel clipboard
python generate_hourly_report.py | clip
```

---

## **Option 3: Pre-Made CSV Template**

If you need a blank template to fill in:

- **File**: [hourly_report.csv](hourly_report.csv)
- **Columns**: Date, Hour, Total_Submissions, Total_Successful, etc.
- **Use**: Fill in your numbers and upload directly to Excel

---

## **Daily Excel Setup (Recommended)**

### Structure:

```
DAILY_2026-04-10.xlsx
├─ Metadata
│  ├─ Date: 2026-04-10
│  ├─ Target: 60+ backlinks
│  ├─ Success Rate: ≥75%
│  └─ Team: [List of owners]
│
├─ Hourly Table (by hour)
│  ├─ 08:00 | 12 | 9 | 75% | ...
│  ├─ 09:00 | 10 | 8 | 80% | ...
│  └─ ...
│
└─ Summary
   ├─ Total Submitted: 65
   ├─ Total Successful: 51
   ├─ Daily Success Rate: 78.5%
   └─ Issues: [List]
```

### Excel Columns (One Row per Hour):

```
A           B       C           D           E           F       G       H       I       J       K       L       M
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────
Date        Hour    Submissions Successful Failed      Success Dirs    Social  Forums  Guest   Blog    Issues  Owner
2026-04-10  08:00   12          9           0           75%     3       2       1       4       2       None    Backend Eng
2026-04-10  09:00   10          8           2           80%     2       2       0       4       2       1 rate-limit Social Lead
...
DAILY_TOTAL         65          51          8           78.5%   15      12      5       20      13      —       —
```

---

## **Metrics & Targets**

Keep these in mind while tracking:

| Metric | Target | Green Zone | Yellow Alert | Red Alert |
|--------|--------|-----------|--------------|-----------|
| **Submissions/Hour** | 8–12 | 8+ | 4–7 | 0–3 |
| **Hourly Success Rate** | ≥75% | 75%+ | 60–74% | <60% |
| **Daily Total (60h max)** | 60+ | 60+ | 40–59 | <40 |
| **Backlinks/Day** | 60+ | 60+ | 40–59 | <40 |

---

## **What to Report When Pasting into Excel**

### Summary Section:
- ✅ Total submissions (all hours combined)
- ✅ Total successful (accepted)
- ✅ Success rate (%)
- ✅ Backlinks by strategy
- ✅ Any critical issues

### Issues Section:
Log any blockers:
- Rate limits (auto-resolved)
- CAPTCHA incidents
- Email delivery failures
- Detection warnings
- Manual approvals needed

### Team Accountability:
- Who ran each hour
- What strategy each person owned
- Any handoff notes

---

## **Files Created**

| File | Purpose | Use Case |
|------|---------|----------|
| [HOURLY_REPORT_TEMPLATE.md](HOURLY_REPORT_TEMPLATE.md) | Manual template | Fill in by hand |
| [hourly_report.csv](hourly_report.csv) | Blank CSV | Paste into Excel |
| [generate_hourly_report.py](generate_hourly_report.py) | Auto-generator | Read logs → Excel |
| [reports/](reports/) | Archive folder | Historical reports |

---

## **Daily Workflow (Shift-Based)**

### **Every Hour (During Active Hours: 8 AM – 8 PM)**

```
⏰ At the TOP of each hour:

1. [ ] Check CSVLogger output (or dashboard)
2. [ ] Count: Submissions, Successful, Failed for LAST hour
3. [ ] Note any issues or blockers
4. [ ] Fill in hourly row in Excel
5. [ ] Pass to next shift owner (if handoff)

⏰ At END of day (8 PM):

6. [ ] Run: python generate_hourly_report.py
7. [ ] Copy CSV → Daily totals row
8. [ ] Calculate success rate
9. [ ] Archive file to reports/
10. [ ] Send to leadership
```

---

## **Example: How It Works in Real-Time**

### **During Hour (8:00 AM – 8:59 AM)**

Backlinks are being submitted...

```python
# Each submission logs to: output/backlinks_log.csv
{
  "date": "2026-04-10T08:15:23",
  "strategy": "directories",
  "site_name": "yelp.com/vestacall",
  "status": "success",
  "notes": ""
}
```

### **At End of Hour (9:00 AM)**

Run the report:

```bash
python generate_hourly_report.py 2026-04-10
```

**Output for 08:00 row:**
```
Date        Hour    Submissions  Successful  Failed  Success Rate  Directories  Social  Forums  Guest  Blog  Issues
2026-04-10  08:00   12           9           0       75%           3            2       1       4      2     None
```

### **Copy to Excel**

Paste the CSV row into your daily tracker.

---

## **Troubleshooting**

### **Script shows 0 data**
- Check if `output/backlinks_log.csv` exists
- Verify timestamps in log match your target date
- Try with a date you know has data

### **Wrong strategy counts**
- Script normalizes strategy names (e.g., `guest_post_outreach` → `outreach`)
- Check [generate_hourly_report.py](generate_hourly_report.py) line 29-37 for STRATEGY_MAP

### **Excel not importing CSV properly**
- Copy CSV output → paste into Notepad first
- In Excel: Data → From Text → Select CSV → Delimited by comma

---

## **Next Steps**

1. ✅ **Choose your method**: Manual template, CSV, or auto-script?
2. ✅ **Set up Excel sheet** with column headers (copy from examples above)
3. ✅ **Run first report** to test: `python generate_hourly_report.py`
4. ✅ **Train team** on hourly logging process
5. ✅ **Schedule daily rollup** for leadership reporting

---

## **Questions?**

- **For manual tracking**: See [HOURLY_REPORT_TEMPLATE.md](HOURLY_REPORT_TEMPLATE.md)
- **For detailed metrics**: Check [team_efficiency.md](team_efficiency.md) and [ROI_TRACKING.md](ROI_TRACKING.md)
- **For compliance**: See [COMPLIANCE_CHECKLIST.md](COMPLIANCE_CHECKLIST.md)

---

**Ready to go!** 🚀 Pick your method and start tracking.
