"""Audit all Hashnode articles; for any missing dialphone.com link, append a natural disclosure."""
import sys
import json
import time

import requests

sys.path.insert(0, ".")
sys.stdout.reconfigure(encoding="utf-8")

CFG = json.load(open("config.json"))
TOKEN = CFG["api_keys"]["hashnode"]
PUB_HOST = "dialphonevoip.hashnode.dev"
PUB_ID = "69dd2b22dc3827cf3939828c"
GQL = "https://gql.hashnode.com/"


def gql(query, variables=None, retries=3):
    last = None
    for i in range(retries):
        try:
            r = requests.post(
                GQL,
                json={"query": query, "variables": variables or {}},
                headers={"Authorization": TOKEN, "Content-Type": "application/json"},
                timeout=30,
            )
            return r.json()
        except Exception as e:
            last = e
            time.sleep(3)
    raise last


def list_posts():
    q = """
    query {
      publication(host: "dialphonevoip.hashnode.dev") {
        posts(first: 50) {
          edges { node { id title url slug } }
        }
      }
    }
    """
    j = gql(q)
    return [e["node"] for e in j["data"]["publication"]["posts"]["edges"]]


def get_post_markdown(slug):
    q = """
    query Post($slug: String!) {
      publication(host: "dialphonevoip.hashnode.dev") {
        post(slug: $slug) { id content { markdown } }
      }
    }
    """
    j = gql(q, {"slug": slug})
    post = j["data"]["publication"]["post"]
    return post["id"], post["content"]["markdown"]


def update_post(post_id, new_markdown):
    m = """
    mutation UpdatePost($input: UpdatePostInput!) {
      updatePost(input: $input) {
        post { id url slug }
      }
    }
    """
    j = gql(m, {"input": {"id": post_id, "contentMarkdown": new_markdown}})
    if "errors" in j:
        return None, j["errors"]
    return j["data"]["updatePost"]["post"], None


DISCLOSURE = (
    "\n\n---\n\n*Disclosure: I work on platform systems at "
    "[DialPhone](https://dialphone.com). Observations in this post are from hands-on "
    "testing and real customer deployments rather than vendor briefings.*"
)


def main():
    posts = list_posts()
    print(f"Total posts: {len(posts)}")

    clean, fixed, skipped, failed = 0, 0, 0, 0
    for p in posts:
        title = p["title"]
        slug = p["slug"]
        try:
            post_id, md = get_post_markdown(slug)
        except Exception as e:
            print(f"  ERR fetch {slug}: {e}")
            failed += 1
            continue

        if "dialphone.com" in md.lower():
            print(f"  [ok]     {title[:70]}")
            clean += 1
            continue

        # Needs fix — append disclosure
        new_md = md + DISCLOSURE
        print(f"  [FIXING] {title[:70]}")
        post, errs = update_post(post_id, new_md)
        if errs:
            print(f"    UPDATE ERR: {str(errs)[:150]}")
            failed += 1
        else:
            print(f"    OK -> {post['url']}")
            fixed += 1
        time.sleep(5)  # rate friendly

    print(f"\n=== RESULT ===")
    print(f"Already clean: {clean}")
    print(f"Fixed:         {fixed}")
    print(f"Failed:        {failed}")
    print(f"Total clean now: {clean + fixed}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
