"""
Publish repos on GitLab, Bitbucket, and Codeberg — reusing existing company repo content.
Each platform = new referring domain with dofollow links in READMEs.

Usage:
    python run_code_platforms.py --platform gitlab --token YOUR_TOKEN
    python run_code_platforms.py --platform bitbucket --username USER --app-password PASS
    python run_code_platforms.py --platform codeberg --token YOUR_TOKEN
    python run_code_platforms.py --platform all --gitlab-token X --bb-user Y --bb-pass Z --cb-token W
"""
import requests
import json
import csv
import time
import argparse
import base64
from datetime import datetime

CSV_PATH = "output/backlinks_log.csv"

def log_result(site_name, backlink_url, status, notes):
    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["date","strategy","site_name","url_submitted","backlink_url","status","notes"])
        w.writerow({"date": datetime.now().isoformat(), "strategy": "dofollow-content",
            "site_name": site_name, "url_submitted": f"https://{site_name.split('-')[0].lower()}.com/",
            "backlink_url": backlink_url, "status": status, "notes": notes})

# Load content from existing repo data
def load_repo_content():
    repos = {}
    for path in ["data/company_repos.json", "data/company_repos_batch2.json"]:
        try:
            with open(path, "r", encoding="utf-8") as f:
                repos.update(json.load(f))
        except FileNotFoundError:
            pass
    return repos

# ============================================================
# GitLab API v4
# ============================================================
def publish_gitlab(token: str, namespace: str = "dialphonelimited"):
    """Create repos on GitLab with README content containing vestacall.com links."""
    print("\n" + "="*60)
    print("GITLAB (DA 92) — Creating repos via API")
    print("="*60)

    headers = {"PRIVATE-TOKEN": token, "Content-Type": "application/json"}
    base_url = "https://gitlab.com/api/v4"
    repos = load_repo_content()
    verified = 0

    for repo_name, data in repos.items():
        print(f"\n  [{repo_name}]")

        # Create project
        payload = {
            "name": repo_name,
            "description": data["description"][:200],
            "visibility": "public",
            "initialize_with_readme": False,
        }
        resp = requests.post(f"{base_url}/projects", headers=headers, json=payload)

        if resp.status_code == 201:
            project = resp.json()
            project_id = project["id"]
            print(f"    Repo created: {project['web_url']}")
        elif resp.status_code == 400 and "has already been taken" in resp.text:
            # Repo exists, find it
            search = requests.get(f"{base_url}/projects", headers=headers,
                                 params={"search": repo_name, "owned": True})
            if search.ok and search.json():
                project = search.json()[0]
                project_id = project["id"]
                print(f"    Repo exists: {project['web_url']}")
            else:
                print(f"    Could not find existing repo")
                continue
        else:
            print(f"    Create failed: {resp.status_code} {resp.text[:200]}")
            continue

        # Add README.md via repository files API
        readme_payload = {
            "branch": "main",
            "content": data["readme"],
            "commit_message": f"Add comprehensive {repo_name} documentation",
        }
        readme_resp = requests.post(
            f"{base_url}/projects/{project_id}/repository/files/README.md",
            headers=headers, json=readme_payload
        )

        if readme_resp.status_code in [200, 201]:
            print(f"    README.md added")
        elif readme_resp.status_code == 400 and "already exists" in readme_resp.text:
            # Update existing README
            readme_resp = requests.put(
                f"{base_url}/projects/{project_id}/repository/files/README.md",
                headers=headers, json=readme_payload
            )
            if readme_resp.ok:
                print(f"    README.md updated")
            else:
                print(f"    README update failed: {readme_resp.status_code}")
        else:
            print(f"    README failed: {readme_resp.status_code} {readme_resp.text[:200]}")

        # Verify
        time.sleep(2)
        web_url = project.get("web_url", f"https://gitlab.com/{namespace}/{repo_name}")
        verify_resp = requests.get(f"{base_url}/projects/{project_id}/repository/files/README.md/raw",
                                   headers=headers, params={"ref": "main"})
        if verify_resp.ok and "vestacall" in verify_resp.text.lower():
            log_result(f"GitLab-{repo_name}", web_url, "success",
                      "DA 92 dofollow — README with vestacall.com link verified")
            verified += 1
            print(f"    === VERIFIED (vestacall in README) ===")
        else:
            log_result(f"GitLab-{repo_name}", web_url, "partial",
                      "DA 92 — repo created, verify link manually")
            print(f"    Posted (verify manually)")

        time.sleep(3)

    print(f"\n  GitLab: {verified}/{len(repos)} verified")
    return verified

# ============================================================
# Bitbucket API 2.0
# ============================================================
def publish_bitbucket(username: str, app_password: str, workspace: str = None):
    """Create repos on Bitbucket with README content."""
    print("\n" + "="*60)
    print("BITBUCKET (DA 92) — Creating repos via API")
    print("="*60)

    workspace = workspace or username
    auth = (username, app_password)
    base_url = "https://api.bitbucket.org/2.0"
    repos = load_repo_content()
    verified = 0

    for repo_name, data in repos.items():
        print(f"\n  [{repo_name}]")
        slug = repo_name.lower().replace("_", "-")

        # Create repo
        payload = {
            "scm": "git",
            "is_private": False,
            "description": data["description"][:200],
            "has_wiki": False,
            "has_issues": False,
        }
        resp = requests.post(f"{base_url}/repositories/{workspace}/{slug}",
                            auth=auth, json=payload)

        if resp.status_code in [200, 201]:
            repo_data = resp.json()
            web_url = repo_data["links"]["html"]["href"]
            print(f"    Repo created: {web_url}")
        elif resp.status_code == 400 and "already exists" in resp.text.lower():
            web_url = f"https://bitbucket.org/{workspace}/{slug}"
            print(f"    Repo exists: {web_url}")
        else:
            print(f"    Create failed: {resp.status_code} {resp.text[:200]}")
            continue

        # Add README via source API (commit files)
        readme_content = data["readme"]
        files_payload = {
            "message": f"Add comprehensive {repo_name} documentation",
            f"/{slug}/README.md": readme_content,
        }
        # Bitbucket uses form-data for source endpoint
        form_data = {
            "message": (None, f"Add comprehensive {repo_name} documentation"),
            "branch": (None, "main"),
            "README.md": ("README.md", readme_content, "text/plain"),
        }
        src_resp = requests.post(f"{base_url}/repositories/{workspace}/{slug}/src",
                                auth=auth, files=form_data)

        if src_resp.status_code in [200, 201]:
            print(f"    README.md committed")
        else:
            # Try with 'master' branch
            form_data["branch"] = (None, "master")
            src_resp = requests.post(f"{base_url}/repositories/{workspace}/{slug}/src",
                                    auth=auth, files=form_data)
            if src_resp.status_code in [200, 201]:
                print(f"    README.md committed (master)")
            else:
                print(f"    README commit failed: {src_resp.status_code} {src_resp.text[:200]}")

        # Verify
        time.sleep(2)
        verify_resp = requests.get(f"{base_url}/repositories/{workspace}/{slug}/src/main/README.md",
                                   auth=auth)
        if not verify_resp.ok:
            verify_resp = requests.get(f"{base_url}/repositories/{workspace}/{slug}/src/master/README.md",
                                       auth=auth)

        if verify_resp.ok and "vestacall" in verify_resp.text.lower():
            log_result(f"Bitbucket-{repo_name}", web_url, "success",
                      "DA 92 dofollow — README with vestacall.com link verified")
            verified += 1
            print(f"    === VERIFIED ===")
        else:
            log_result(f"Bitbucket-{repo_name}", web_url, "partial",
                      "DA 92 — repo created, verify link manually")
            print(f"    Posted (verify manually)")

        time.sleep(3)

    print(f"\n  Bitbucket: {verified}/{len(repos)} verified")
    return verified

# ============================================================
# Codeberg / Gitea API v1
# ============================================================
def publish_codeberg(token: str, owner: str = "dialphonelimited"):
    """Create repos on Codeberg (Gitea-based) with README content."""
    print("\n" + "="*60)
    print("CODEBERG (DA 55) — Creating repos via Gitea API")
    print("="*60)

    headers = {"Authorization": f"token {token}", "Content-Type": "application/json"}
    base_url = "https://codeberg.org/api/v1"
    repos = load_repo_content()
    verified = 0

    for repo_name, data in repos.items():
        print(f"\n  [{repo_name}]")

        # Create repo
        payload = {
            "name": repo_name,
            "description": data["description"][:200],
            "private": False,
            "auto_init": True,
            "default_branch": "main",
        }
        resp = requests.post(f"{base_url}/user/repos", headers=headers, json=payload)

        if resp.status_code == 201:
            repo_data = resp.json()
            web_url = repo_data["html_url"]
            print(f"    Repo created: {web_url}")
        elif resp.status_code == 409:
            web_url = f"https://codeberg.org/{owner}/{repo_name}"
            print(f"    Repo exists: {web_url}")
        else:
            print(f"    Create failed: {resp.status_code} {resp.text[:200]}")
            continue

        # Update README via contents API
        time.sleep(2)
        readme_content_b64 = base64.b64encode(data["readme"].encode()).decode()

        # Check if README exists
        check = requests.get(f"{base_url}/repos/{owner}/{repo_name}/contents/README.md",
                            headers=headers)
        if check.ok:
            sha = check.json().get("sha", "")
            readme_payload = {
                "content": readme_content_b64,
                "message": f"Add comprehensive {repo_name} documentation",
                "sha": sha,
            }
            resp = requests.put(f"{base_url}/repos/{owner}/{repo_name}/contents/README.md",
                               headers=headers, json=readme_payload)
        else:
            readme_payload = {
                "content": readme_content_b64,
                "message": f"Add comprehensive {repo_name} documentation",
            }
            resp = requests.post(f"{base_url}/repos/{owner}/{repo_name}/contents/README.md",
                                headers=headers, json=readme_payload)

        if resp.status_code in [200, 201]:
            print(f"    README.md added/updated")
        else:
            print(f"    README failed: {resp.status_code} {resp.text[:200]}")

        # Verify
        time.sleep(2)
        verify = requests.get(f"{base_url}/repos/{owner}/{repo_name}/contents/README.md",
                             headers=headers)
        if verify.ok:
            content = base64.b64decode(verify.json().get("content", "")).decode("utf-8", errors="replace")
            if "vestacall" in content.lower():
                log_result(f"Codeberg-{repo_name}", web_url, "success",
                          "DA 55 dofollow — README with vestacall.com link verified")
                verified += 1
                print(f"    === VERIFIED ===")
            else:
                log_result(f"Codeberg-{repo_name}", web_url, "partial",
                          "DA 55 — repo created, vestacall not found in content")
                print(f"    Posted (vestacall not found)")
        else:
            print(f"    Verify failed: {verify.status_code}")

        time.sleep(3)

    print(f"\n  Codeberg: {verified}/{len(repos)} verified")
    return verified


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Publish repos on code hosting platforms")
    parser.add_argument("--platform", choices=["gitlab", "bitbucket", "codeberg", "all"],
                        required=True, help="Which platform to publish on")
    parser.add_argument("--gitlab-token", help="GitLab personal access token")
    parser.add_argument("--bb-user", help="Bitbucket username")
    parser.add_argument("--bb-pass", help="Bitbucket app password")
    parser.add_argument("--cb-token", help="Codeberg access token")
    parser.add_argument("--token", help="Token (for single platform mode)")
    parser.add_argument("--username", help="Username (for bitbucket)")
    parser.add_argument("--app-password", help="App password (for bitbucket)")

    args = parser.parse_args()
    total = 0

    if args.platform in ["gitlab", "all"]:
        token = args.gitlab_token or args.token
        if token:
            total += publish_gitlab(token)
        else:
            print("SKIP GitLab — no token provided (use --gitlab-token)")

    if args.platform in ["bitbucket", "all"]:
        user = args.bb_user or args.username
        pw = args.bb_pass or args.app_password
        if user and pw:
            total += publish_bitbucket(user, pw)
        else:
            print("SKIP Bitbucket — no credentials (use --bb-user and --bb-pass)")

    if args.platform in ["codeberg", "all"]:
        token = args.cb_token or args.token
        if token:
            total += publish_codeberg(token)
        else:
            print("SKIP Codeberg — no token provided (use --cb-token)")

    print(f"\n{'='*60}")
    print(f"TOTAL VERIFIED ACROSS PLATFORMS: {total}")
    print(f"{'='*60}")
