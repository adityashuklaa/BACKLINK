"""Mark all high-spam-score backlinks as status=spam_quarantined in master CSV.
The dashboard already filters to successful rows — so quarantined rows stop showing
as 'wins' without losing the historical record."""
import csv
import sys
sys.path.insert(0, ".")
from dashboard.dialphone_dashboard import SPAM_SCORES

MASTER = "output/backlinks_log.csv"
TRUTH = "output/backlinks_final_truth.csv"
HIGH_SPAM_DOMAINS = {d for d, s in SPAM_SCORES.items() if s > 55}

print(f"Treating these domains as high-spam: {sorted(HIGH_SPAM_DOMAINS)}")

def quarantine(path, field_domain_fn):
    rows = list(csv.DictReader(open(path, encoding="utf-8", errors="replace")))
    if not rows:
        return 0
    changed = 0
    for r in rows:
        if r.get("status") != "success":
            continue
        url = r.get("backlink_url", "")
        if "//" not in url:
            continue
        d = url.split("//")[1].split("/")[0]
        if "github" in d and "gist" not in d:
            d = "github.com"
        if d in HIGH_SPAM_DOMAINS:
            r["status"] = "spam_quarantined"
            changed += 1
    # Write back
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    return changed

n1 = quarantine(MASTER, lambda r: r.get("backlink_url", "").split("//")[1].split("/")[0])
print(f"{MASTER}: quarantined {n1} rows")

n2 = quarantine(TRUTH, lambda r: r.get("backlink_url", "").split("//")[1].split("/")[0])
print(f"{TRUTH}: quarantined {n2} rows")
