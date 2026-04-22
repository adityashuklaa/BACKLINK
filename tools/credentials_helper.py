"""Password generation + accounts-sheet append helper.

Usage:
    from tools.credentials_helper import gen_password, record_account
    pw = gen_password()
    record_account("medium", "https://medium.com/@dialphone", "social@dialphone.com", "dialphone", pw, notes="Signup Apr 21")

Never commits the sheet — .credentials/ is gitignored.
"""
import csv
import os
import random
import string
from datetime import datetime

SHEET = ".credentials/accounts_sheet.csv"
FIELDS = ["platform", "url", "email", "username", "password", "created_date", "notes", "status"]


def gen_password(length=20):
    alphabet = string.ascii_letters + string.digits + "!@#$%&*"
    # Use a system-random source
    rng = random.SystemRandom()
    return "".join(rng.choice(alphabet) for _ in range(length))


def record_account(platform, url="", email="social@dialphone.com", username="", password="", notes="", status="active"):
    os.makedirs(".credentials", exist_ok=True)
    exists = os.path.exists(SHEET)
    with open(SHEET, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if not exists:
            w.writeheader()
        w.writerow(
            {
                "platform": platform,
                "url": url,
                "email": email,
                "username": username,
                "password": password,
                "created_date": datetime.now().strftime("%Y-%m-%d"),
                "notes": notes,
                "status": status,
            }
        )


def list_accounts():
    if not os.path.exists(SHEET):
        return []
    with open(SHEET, encoding="utf-8") as f:
        return list(csv.DictReader(f))


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python tools/credentials_helper.py [genpw | list]")
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "genpw":
        print(gen_password())
    elif cmd == "list":
        for acc in list_accounts():
            redacted = {k: ("***" if k == "password" else v) for k, v in acc.items()}
            print(redacted)
