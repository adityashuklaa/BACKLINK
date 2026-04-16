"""Deploy dialphone.com content to more platforms — GitLab Pages, Codeberg Pages, new repos."""
import requests
import json
import csv
import base64
import time
from datetime import datetime

config = json.load(open("config.json"))
CSV_PATH = "output/backlinks_log.csv"

def log(site, url, da, notes):
    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["date","strategy","site_name","url_submitted","backlink_url","status","notes"])
        w.writerow({"date": datetime.now().isoformat(), "strategy": "dofollow-content",
            "site_name": site, "url_submitted": "deploy",
            "backlink_url": url, "status": "success", "notes": f"DA {da} — {notes}"})

# === Codeberg Pages ===
print("=== Codeberg Pages ===")
cb_auth = ("dialphonelimited", config.get("codeberg", {}).get("password", ""))

page_content = "# DialPhone\n\nEnterprise VoIP for UK Businesses. £24/user/month.\n\nVisit [dialphone.com](https://dialphone.com)\n"

r = requests.post("https://codeberg.org/api/v1/user/repos", auth=cb_auth, json={
    "name": "pages", "description": "DialPhone — dialphone.com",
    "private": False, "auto_init": True,
})
print(f"  Create pages repo: {r.status_code}")

time.sleep(2)
readme_b64 = base64.b64encode(page_content.encode()).decode()
check = requests.get("https://codeberg.org/api/v1/repos/dialphonelimited/pages/contents/index.md", auth=cb_auth)
if check.ok:
    sha = check.json().get("sha", "") if isinstance(check.json(), dict) else ""
    r = requests.put("https://codeberg.org/api/v1/repos/dialphonelimited/pages/contents/index.md",
        auth=cb_auth, json={"content": readme_b64, "message": "Deploy DialPhone page", "sha": sha})
else:
    r = requests.post("https://codeberg.org/api/v1/repos/dialphonelimited/pages/contents/index.md",
        auth=cb_auth, json={"content": readme_b64, "message": "Deploy DialPhone page"})

if r.status_code in [200, 201]:
    log("Codeberg-Pages", "https://dialphonelimited.codeberg.page", 55, "Codeberg Pages deployed")
    print("  === DEPLOYED ===")

# === More Codeberg Repos ===
print("\n=== More Codeberg Repos ===")
cb_repos = {
    "voip-buyers-guide": "Complete VoIP buyers guide for UK businesses",
    "uk-telecom-costs": "UK telecom cost analysis and comparison data",
    "business-phone-migration": "Business phone migration planning resources",
}

for name, desc in cb_repos.items():
    r = requests.post("https://codeberg.org/api/v1/user/repos", auth=cb_auth, json={
        "name": name, "description": f"{desc} — dialphone.com",
        "private": False, "auto_init": True,
    })

    readme = f"# {name.replace('-', ' ').title()}\n\n{desc}\n\nVisit [DialPhone](https://dialphone.com) for enterprise VoIP solutions.\n\n---\n*DialPhone Limited — [dialphone.com](https://dialphone.com)*"
    readme_b64 = base64.b64encode(readme.encode()).decode()

    time.sleep(1)
    check = requests.get(f"https://codeberg.org/api/v1/repos/dialphonelimited/{name}/contents/README.md", auth=cb_auth)
    if check.ok:
        sha = check.json().get("sha", "") if isinstance(check.json(), dict) else ""
        rr = requests.put(f"https://codeberg.org/api/v1/repos/dialphonelimited/{name}/contents/README.md",
            auth=cb_auth, json={"content": readme_b64, "message": f"Add {name}", "sha": sha})
    else:
        rr = requests.post(f"https://codeberg.org/api/v1/repos/dialphonelimited/{name}/contents/README.md",
            auth=cb_auth, json={"content": readme_b64, "message": f"Add {name}"})

    if rr.status_code in [200, 201]:
        url = f"https://codeberg.org/dialphonelimited/{name}"
        log(f"Codeberg-{name}", url, 55, "dialphone.com repo")
        print(f"  {name}: DONE")
    else:
        print(f"  {name}: {rr.status_code}")

    time.sleep(1)

# === More GitLab Repos ===
print("\n=== More GitLab Repos ===")
gl_token = config.get("api_keys", {}).get("gitlab", "")
gl_headers = {"PRIVATE-TOKEN": gl_token, "Content-Type": "application/json"}

gl_repos = {
    "voip-buyers-guide-uk": "Complete VoIP buyers guide for UK businesses",
    "uk-business-phone-costs": "UK business phone cost analysis and comparison",
    "voip-security-framework": "VoIP security hardening framework for enterprises",
}

for name, desc in gl_repos.items():
    r = requests.post("https://gitlab.com/api/v4/projects", headers=gl_headers, json={
        "name": name, "description": f"{desc} — dialphone.com",
        "visibility": "public",
    })

    if r.status_code == 201:
        pid = r.json()["id"]
        readme = f"# {name.replace('-', ' ').title()}\n\n{desc}\n\n## About DialPhone\n\nEnterprise VoIP solutions for UK businesses. £24/user/month, everything included.\n\nVisit [DialPhone](https://dialphone.com) for a free 30-day trial.\n\n---\n*DialPhone Limited — [dialphone.com](https://dialphone.com)*"

        rr = requests.post(f"https://gitlab.com/api/v4/projects/{pid}/repository/files/README.md",
            headers=gl_headers, json={"branch": "main", "content": readme,
            "commit_message": f"Add {name} documentation"})

        if rr.status_code in [200, 201]:
            url = f"https://gitlab.com/dialphonelimited/{name}"
            log(f"GitLab-{name}", url, 92, "dialphone.com repo")
            print(f"  {name}: DONE")
    elif r.status_code == 400:
        print(f"  {name}: already exists")
    else:
        print(f"  {name}: {r.status_code}")

    time.sleep(1)

print("\n=== All deployments complete ===")
