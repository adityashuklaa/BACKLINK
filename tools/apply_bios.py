"""Push profile bios to Dev.to + GitHub via their APIs. Idempotent — safe to re-run."""
import json
import os
import sys
import requests

config = json.load(open("config.json"))

PERSONA = {
    "name": "Bhavesh Shukla",
    "username": "dialphonelimited",
    "location": "Manchester, UK",
    "website": "https://dialphone.com",
    "devto_summary": "VoIP engineer @ DialPhone. Writing about SIP, codec comparison, and migrating UK businesses off ISDN. 10 years in telecom.",
    "devto_available_for": "Consulting on UK VoIP migrations",
    "devto_currently_learning": "Kamailio scripting, WebRTC performance tuning",
    "devto_currently_hacking_on": "Internal tools for VoIP deployment automation",
    "devto_skills_languages": "SIP, Asterisk, FreeSWITCH, Kamailio, WebRTC, Python, Bash",
    "github_bio": "VoIP @ DialPhone Limited. SIP, Kamailio, Asterisk, PBX migrations. Manchester, UK.",
    "github_company": "@dialphonelimited",
}


def apply_devto():
    """Dev.to doesn't have a direct profile-edit API. PATCH /api/users/me is users-only
    and limited. Print manual instructions instead."""
    print("\n=== Dev.to ===")
    print("Dev.to does NOT expose a profile-update API endpoint. Apply manually:")
    print(f"  1. Go to https://dev.to/settings")
    print(f"  2. Set Name:          {PERSONA['name']}")
    print(f"     Summary:           {PERSONA['devto_summary']}")
    print(f"     Location:          {PERSONA['location']}")
    print(f"     Website:           {PERSONA['website']}")
    print(f"     Available for:     {PERSONA['devto_available_for']}")
    print(f"     Currently learning: {PERSONA['devto_currently_learning']}")
    print(f"     Currently hacking:  {PERSONA['devto_currently_hacking_on']}")
    print(f"     Skills/languages:   {PERSONA['devto_skills_languages']}")
    print(f"  3. Save")
    return "manual_only"


def apply_github():
    """GitHub PATCH /user with auth token updates profile fields."""
    print("\n=== GitHub ===")
    token = (config.get("api_keys", {}).get("github")
             or config.get("github", {}).get("token")
             or os.environ.get("GITHUB_TOKEN"))
    if not token:
        print("  No GitHub token in config.api_keys.github or $GITHUB_TOKEN")
        print("  Create a classic PAT at https://github.com/settings/tokens with 'user' scope")
        print("  Add to config.json under api_keys.github, then rerun this script.")
        return "no_token"
    url = "https://api.github.com/user"
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github+json"}
    payload = {
        "name": PERSONA["name"],
        "bio": PERSONA["github_bio"],
        "company": PERSONA["github_company"],
        "location": PERSONA["location"],
        "blog": PERSONA["website"],
    }
    r = requests.patch(url, headers=headers, json=payload)
    if r.status_code == 200:
        data = r.json()
        print(f"  OK — Name: {data.get('name')}, Bio: {data.get('bio')[:60]}..., Location: {data.get('location')}, Blog: {data.get('blog')}")
        return "ok"
    print(f"  FAIL {r.status_code}: {r.text[:200]}")
    return "failed"


def apply_gitlab():
    """GitLab API doesn't allow self-profile update (PUT /user/:id is admin-only).
    Print manual instructions."""
    print("\n=== GitLab ===")
    print("GitLab API does NOT allow updating your own profile (admin-only endpoint).")
    print("Apply manually at https://gitlab.com/-/profile:")
    print(f"  Full name:     {PERSONA['name']}")
    print(f"  Job title:     Head of VoIP Operations")
    print(f"  Organization:  DialPhone Limited")
    print(f"  Location:      Manchester, United Kingdom")
    print(f"  Bio:           VoIP infrastructure at DialPhone. UK business phone systems.")
    print(f"  Website:       {PERSONA['website']}")
    return "manual_only"


def apply_codeberg():
    """Codeberg uses Gitea API. PATCH /user/settings updates bio etc."""
    print("\n=== Codeberg ===")
    token = (config.get("api_keys", {}).get("codeberg")
             or config.get("codeberg", {}).get("token")
             or os.environ.get("CODEBERG_TOKEN"))
    if not token:
        print("  No Codeberg API token. Generate at https://codeberg.org/user/settings/applications")
        print("  Add to config.codeberg.token, then rerun.")
        return "no_token"
    url = "https://codeberg.org/api/v1/user/settings"
    headers = {"Authorization": f"token {token}", "Content-Type": "application/json"}
    payload = {
        "full_name": PERSONA["name"],
        "description": "VoIP infrastructure at DialPhone Limited. UK business phone systems.",
        "website": PERSONA["website"],
        "location": PERSONA["location"],
    }
    r = requests.patch(url, headers=headers, json=payload)
    if r.status_code in (200, 204):
        print(f"  OK — applied to Codeberg")
        return "ok"
    print(f"  FAIL {r.status_code}: {r.text[:200]}")
    return "failed"


def main():
    print(f"Applying persona for: {PERSONA['name']} / {PERSONA['username']}")
    results = {
        "devto": apply_devto(),
        "github": apply_github(),
        "gitlab": apply_gitlab(),
        "codeberg": apply_codeberg(),
    }
    print("\n=== Summary ===")
    for k, v in results.items():
        marker = "OK" if v == "ok" else "MANUAL" if v == "manual_only" else "NEEDS_TOKEN" if v == "no_token" else "FAIL"
        print(f"  {k}: {marker}")
    print("\nNext: run tools/warm_accounts.py to follow/star popular VoIP accounts.")


if __name__ == "__main__":
    main()
