"""Warm up profiles by following writers + starring relevant repos.
API-based only — no Playwright, no Quora (too risky)."""
import json
import time
import argparse
import requests

config = json.load(open("config.json"))
DEVTO_KEY = config.get("api_keys", {}).get("devto", "")
GITHUB_TOKEN = config.get("api_keys", {}).get("github", "")

# --- Dev.to: follow popular VoIP/networking/sysadmin writers ---
# Dev.to API: POST /api/follows/users (requires api-key auth)
# We'll discover users by fetching articles tagged #networking, #voip, #sysadmin, #devops
# then deduping authors.

DEVTO_TAGS = ["networking", "voip", "sysadmin", "devops", "telecom", "sip"]

def devto_discover_authors(per_tag=10):
    authors = {}
    for tag in DEVTO_TAGS:
        try:
            r = requests.get(f"https://dev.to/api/articles?tag={tag}&per_page={per_tag}", timeout=15)
            if r.status_code != 200:
                continue
            for art in r.json():
                u = art.get("user", {})
                uid = u.get("user_id") or u.get("id")
                if uid and uid not in authors:
                    authors[uid] = {"username": u.get("username"), "name": u.get("name")}
        except Exception as e:
            print(f"  [devto] tag {tag} error: {e}")
    return authors

def devto_follow(user_ids):
    """Dev.to API endpoint for following is limited. Only a few official endpoints exist.
    The 'follow a user' flow isn't in the public Article API v1. Print manual guidance instead."""
    print(f"\n  Found {len(user_ids)} Dev.to authors to follow.")
    print(f"  Dev.to does NOT provide a public follow-users API endpoint.")
    print(f"  To follow them, visit these profiles manually and click Follow:")
    for uid, info in list(user_ids.items())[:40]:
        username = info.get("username", "?")
        print(f"    https://dev.to/{username}")
    return "manual"

# --- GitHub: star popular VoIP repos ---
GITHUB_REPOS_TO_STAR = [
    "kamailio/kamailio",
    "asterisk/asterisk",
    "signalwire/freeswitch",
    "pjsip/pjproject",
    "OpenSIPS/opensips",
    "versatica/mediasoup",
    "jitsi/jitsi",
    "meetecho/janus-gateway",
    "coturn/coturn",
    "seven1240/sip-clients",
    "pion/webrtc",
    "restcomm/sip-servlets",
    "twilio/twilio-python",
    "plivo/plivo-python",
    "vonage/vonage-python-sdk",
    "bandwidthcom/python-sdk",
    "sippy/b2bua",
    "davehorton/drachtio-server",
    "respoke/sdk-js",
    "Rhizomatica/rccn",
    "fonoster/fonoster",
    "routr-io/routr",
    "vitalets/websocket-as-promised",
    "boringssl/boringssl",
    "grpc/grpc",
]

def github_star_repo(token, repo):
    """PUT /user/starred/:owner/:repo — stars a repo on behalf of the authenticated user."""
    url = f"https://api.github.com/user/starred/{repo}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
        "Content-Length": "0",
    }
    r = requests.put(url, headers=headers)
    return r.status_code == 204

def github_follow_user(token, user):
    """PUT /user/following/:username — follow a user."""
    url = f"https://api.github.com/user/following/{user}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
        "Content-Length": "0",
    }
    r = requests.put(url, headers=headers)
    return r.status_code == 204

GITHUB_USERS_TO_FOLLOW = [
    "torvalds", "gaearon", "yyx990803", "getify",  # general well-known (follows blend in)
    "miconda",       # Kamailio lead
    "asterisk",
    "signalwire",
    "pjsipproject",
    "opensips",
    "versatica",
    "pion",
    "twilio",
    "jitsi",
    "meetecho",
    "coturn",
    "fonoster",
]


def run_github(args):
    if not GITHUB_TOKEN:
        print("\n  GitHub token missing — add config.api_keys.github")
        return
    print(f"\n=== GitHub — starring {args.github_stars} repos + following {args.github_follows} users ===")
    # Verify token first
    r = requests.get("https://api.github.com/user", headers={"Authorization": f"token {GITHUB_TOKEN}"})
    if r.status_code != 200:
        print(f"  Token auth failed {r.status_code}: {r.text[:200]}")
        return
    me = r.json().get("login")
    print(f"  Authenticated as: {me}")

    starred = 0
    for repo in GITHUB_REPOS_TO_STAR[:args.github_stars]:
        try:
            ok = github_star_repo(GITHUB_TOKEN, repo)
            print(f"  {'STAR' if ok else 'FAIL'}: {repo}")
            if ok: starred += 1
            time.sleep(0.5)
        except Exception as e:
            print(f"  ERR {repo}: {e}")

    followed = 0
    for user in GITHUB_USERS_TO_FOLLOW[:args.github_follows]:
        try:
            ok = github_follow_user(GITHUB_TOKEN, user)
            print(f"  {'FOLLOW' if ok else 'FAIL'}: {user}")
            if ok: followed += 1
            time.sleep(0.5)
        except Exception as e:
            print(f"  ERR {user}: {e}")

    print(f"\n  GitHub: starred={starred}/{args.github_stars} followed={followed}/{args.github_follows}")


def run_devto(args):
    print(f"\n=== Dev.to — discovering {args.devto_follows} authors ===")
    authors = devto_discover_authors(per_tag=max(10, args.devto_follows // len(DEVTO_TAGS) + 2))
    devto_follow(dict(list(authors.items())[:args.devto_follows]))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--devto-follows", type=int, default=40)
    p.add_argument("--github-stars", type=int, default=25)
    p.add_argument("--github-follows", type=int, default=15)
    p.add_argument("--skip-devto", action="store_true")
    p.add_argument("--skip-github", action="store_true")
    args = p.parse_args()

    if not args.skip_github:
        run_github(args)
    if not args.skip_devto:
        run_devto(args)

    print("\n=== Done ===")


if __name__ == "__main__":
    main()
