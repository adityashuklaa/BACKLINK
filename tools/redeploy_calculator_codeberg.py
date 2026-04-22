"""Push the updated calculator HTML + og-image.png to Codeberg pages repo."""
import base64
import json
import sys
from pathlib import Path

import requests

sys.stdout.reconfigure(encoding="utf-8")

CFG = json.load(open("config.json"))
CB = CFG["codeberg"]
AUTH = (CB["username"], CB["password"])
REPO = f"{CB['username']}/pages"


def upsert_file(path_in_repo, content_bytes, commit_msg):
    """Create or update a file in the Codeberg repo."""
    api = f"https://codeberg.org/api/v1/repos/{REPO}/contents/{path_in_repo}"
    # Get current SHA if file exists
    r = requests.get(api, auth=AUTH, timeout=20)
    content_b64 = base64.b64encode(content_bytes).decode("ascii")
    payload = {
        "message": commit_msg,
        "content": content_b64,
        "branch": "main",
    }
    if r.status_code == 200:
        payload["sha"] = r.json()["sha"]
        r2 = requests.put(api, auth=AUTH, json=payload, timeout=60)
    else:
        r2 = requests.post(api, auth=AUTH, json=payload, timeout=60)
    if r2.status_code in (200, 201):
        print(f"  OK  {path_in_repo}  ({len(content_bytes):,} bytes)")
        return True
    print(f"  FAIL {path_in_repo}: {r2.status_code} {r2.text[:200]}")
    return False


def main():
    html = Path("assets/calculator/index.html").read_bytes()
    png = Path("assets/calculator/og-image.png").read_bytes()
    print(f"Deploying to Codeberg repo {REPO}...")
    upsert_file("calculator/index.html", html, "Add og:image + twitter:card metadata")
    upsert_file("calculator/og-image.png", png, "Add OG preview image for social shares")
    print(f"\nLive in ~30 sec:")
    print(f"  https://dialphonelimited.codeberg.page/calculator/")
    print(f"  https://dialphonelimited.codeberg.page/calculator/og-image.png")


if __name__ == "__main__":
    main()
