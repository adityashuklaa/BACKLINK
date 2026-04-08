import csv
import os
from datetime import datetime

FIELDNAMES = ["date", "strategy", "site_name", "url_submitted", "backlink_url", "status", "notes"]

class CSVLogger:
    def __init__(self, path: str = "output/backlinks_log.csv"):
        self.path = path
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if not os.path.exists(path):
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
                writer.writeheader()

    def log(self, record: dict):
        row = {field: record.get(field, "") for field in FIELDNAMES}
        if not row.get("date"):
            row["date"] = datetime.utcnow().isoformat()
        with open(self.path, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writerow(row)

    def already_done(self, site_name: str) -> bool:
        if not os.path.exists(self.path):
            return False
        with open(self.path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("site_name") == site_name and row.get("status") != "failed":
                    return True
        return False

    def get_done_sites(self) -> set:
        done = set()
        if not os.path.exists(self.path):
            return done
        with open(self.path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("status") != "failed":
                    done.add(row.get("site_name", ""))
        return done

    def get_pending_sites(self) -> list:
        pending = []
        if not os.path.exists(self.path):
            return pending
        with open(self.path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("status") == "pending":
                    pending.append(dict(row))
        return pending

    def update_status(self, site_name: str, new_status: str, notes: str = ""):
        if not os.path.exists(self.path):
            return
        rows = []
        with open(self.path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("site_name") == site_name and row.get("status") == "pending":
                    row["status"] = new_status
                    if notes:
                        row["notes"] = notes
                rows.append(row)
        with open(self.path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()
            writer.writerows(rows)
