"""Audit Quora answer visibility by fetching profile page (403 on answer pages is expected).
Prints which of the logged Quora answers are reachable via profile."""
import csv
import requests
import re

PROFILE_SLUG = "Dialphone-Limited"
PROFILE_URL = f"https://www.quora.com/profile/{PROFILE_SLUG}"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"}


def fetch_profile():
    r = requests.get(PROFILE_URL, headers=HEADERS, timeout=15)
    print(f"Profile GET: {r.status_code}")
    if r.status_code != 200:
        return None, r.status_code
    body = r.text
    return body, 200


def extract_answer_questions(html):
    """Find question slugs Quora renders on the profile."""
    found = set()
    # profile page JSON-embedded question slugs
    for m in re.finditer(r'"question":\{"url":"https://www\.quora\.com/([^"]+)"', html):
        found.add(m.group(1))
    # fallback: <a href="/question-slug"> in visible HTML
    for m in re.finditer(r'href="(/[A-Z][^"?]+?)"', html):
        slug = m.group(1).lstrip("/")
        if slug and not slug.startswith(("profile/", "topic/", "search/", "spaces/")):
            found.add(slug)
    return found


def main():
    # Load logged Quora URLs
    rows = list(csv.DictReader(open("output/backlinks_log.csv", encoding="utf-8", errors="replace")))
    unique_urls = set(r["backlink_url"] for r in rows
                      if "quora.com" in r.get("backlink_url", "") and r.get("status") == "success")

    # Also hit each URL directly — usually 403 but a 404 tells us it was deleted
    print(f"\n=== Per-URL liveness ({len(unique_urls)} unique URLs) ===")
    per_url = {}
    for u in sorted(unique_urls):
        try:
            r = requests.get(u, headers=HEADERS, timeout=10)
            per_url[u] = r.status_code
        except Exception as e:
            per_url[u] = f"err_{type(e).__name__}"

    status_counts = {}
    for u, s in per_url.items():
        status_counts[s] = status_counts.get(s, 0) + 1
        marker = "LIVE" if s == 200 else "DEAD" if s == 404 else "BLOCKED" if s == 403 else str(s)
        print(f"  [{marker}] {u}")

    print(f"\nStatus summary: {status_counts}")

    # Fetch profile page and try to list visible answers
    print(f"\n=== Profile: {PROFILE_URL} ===")
    html, code = fetch_profile()
    if html:
        slugs = extract_answer_questions(html)
        print(f"Found {len(slugs)} question/profile links on the profile page")
        q_slugs = [s for s in slugs if not s.startswith(("unanswered/", "topic/"))]
        print(f"Visible question answers on profile: ~{len(q_slugs)}")
        for s in sorted(q_slugs)[:20]:
            print(f"  https://www.quora.com/{s}")

    print("\n=== Recommendation ===")
    dead = sum(1 for s in per_url.values() if s == 404)
    blocked = sum(1 for s in per_url.values() if s == 403)
    if dead > 0:
        print(f"  {dead} URLs returned 404 — likely deleted. Treat those as lost.")
    if blocked > 0:
        print(f"  {blocked} URLs returned 403 (normal Quora bot block — not a signal of deletion).")
    print(f"  To verify answer visibility, manually visit: {PROFILE_URL}")
    print(f"  Count the actual answers shown. If count < logged unique questions, some were flagged.")


if __name__ == "__main__":
    main()
