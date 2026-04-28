"""Competitor Backlink Intercept Tool — find sites that link to RingCentral / 8x8 / etc.
and pitch them to add DialPhone alongside.

Pipeline:
  1. For each competitor, search engines (DuckDuckGo HTML) for review/comparison/roundup pages
     that mention the competitor.
  2. Visit each result, check if it actually links to the competitor.
  3. Score by DA estimate × topical relevance × likelihood-to-link.
  4. Filter out: our existing referring domains, already-pitched domains, BLOCKED_HIGH_SPAM_DOMAINS,
     comment / forum / paste URL patterns.
  5. Output ranked CSV at output/competitor_backlink_targets_v2.csv.
  6. Output risk dashboard at output/backlink_intercept_risk.json.

Spec: docs/prompt_competitor_backlink_intercept.md
"""
import csv
import json
import re
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime
from urllib.parse import urlparse, quote_plus

sys.path.insert(0, ".")
sys.stdout.reconfigure(encoding="utf-8")

from core.browser import get_browser, new_page
from core.humanize import BLOCKED_HIGH_SPAM_DOMAINS

CFG = json.load(open("config.json"))

# ============================================================
# CONFIG
# ============================================================
COMPETITORS = [
    {"name": "RingCentral", "domain": "ringcentral.com",
     "queries": [
         '"ringcentral" review 2026',
         '"ringcentral" vs',
         'best business voip 2026 ringcentral',
         '"ringcentral" alternative',
         'ringcentral pricing comparison',
     ]},
    {"name": "8x8", "domain": "8x8.com",
     "queries": [
         '"8x8" voip review',
         '"8x8 work" pricing',
         'best business phone 8x8',
         '"8x8" vs',
         '8x8 voip alternative',
     ]},
    {"name": "Dialpad", "domain": "dialpad.com",
     "queries": [
         '"dialpad" review 2026',
         '"dialpad" vs',
         'dialpad alternative voip',
         'best ai voip dialpad',
         'dialpad pricing comparison',
     ]},
    {"name": "Nextiva", "domain": "nextiva.com",
     "queries": [
         '"nextiva" review',
         '"nextiva" vs',
         'nextiva alternative voip',
         'best business phone nextiva',
     ]},
    {"name": "Vonage", "domain": "vonage.com",
     "queries": [
         '"vonage" business review',
         '"vonage" vs',
         'vonage alternative voip',
         'vonage business pricing',
     ]},
]

# DA lookup (seeded from dashboard/dialphone_dashboard.py + common B2B publication knowledge)
KNOWN_DA = {
    "uctoday.com": 78, "nojitter.com": 72, "getvoip.com": 55, "whichvoip.com": 48,
    "techtarget.com": 86, "zdnet.com": 92, "forbes.com": 95, "businessnewsdaily.com": 80,
    "entrepreneur.com": 91, "inc.com": 90, "techradar.com": 91, "pcmag.com": 94,
    "softwareadvice.com": 85, "capterra.com": 93, "g2.com": 90, "trustradius.com": 82,
    "trustpilot.com": 94, "crn.com": 82, "rcrwireless.com": 65, "telecompetitor.com": 62,
    "alternativeto.net": 89, "saashub.com": 65, "stackshare.io": 72, "slant.co": 65,
    "producthunt.com": 92, "crunchbase.com": 92, "indiehackers.com": 79,
    "smallbiztrends.com": 72, "thebalancesmb.com": 78, "business.com": 75,
    "saasgenius.com": 45, "softwaresuggest.com": 60, "goodfirms.co": 72, "crozdesk.com": 60,
    "financesonline.com": 70, "voipreview.org": 55, "voipmechanic.com": 45, "voipblog.com": 40,
    "tmcnet.com": 65, "techaeris.com": 52, "upcity.com": 62, "expertmarket.com": 55,
    "thetechpanda.com": 45, "readwrite.com": 72, "techrepublic.com": 80, "devops.com": 70,
    "thenewstack.io": 70, "infoq.com": 72, "theregister.com": 85, "smallbusiness.co.uk": 55,
    "wikipedia.org": 100, "github.com": 100, "linkedin.com": 98, "medium.com": 96,
    "tumblr.com": 95, "substack.com": 89, "blogger.com": 95,
    "stackoverflow.com": 93, "quora.com": 93, "reddit.com": 91,
    "betalist.com": 65, "launchingnext.com": 55, "saasworthy.com": 65,
    "g2crowd.com": 90, "capterra.co.uk": 93, "getapp.com": 87,
    "serverfault.com": 80, "superuser.com": 84,
}

# URL patterns to skip — these are user-generated / spam / non-editorial
URL_SKIP_PATTERNS = [
    r"/comment(s|ing)?/",   r"/forum/",  r"/profile/", r"/users?/",
    r"/tag/", r"/topic/", r"/thread/", r"/wiki/talk:", r"/discussion/",
    r"^https?://[^/]+/?$",  # bare domain (homepage) — usually not the linking page
    r"\.pdf$", r"\.doc$", r"\.docx$",  # not webpages
    r"/cdn-cgi/", r"/wp-admin/", r"/wp-json/", r"/wp-content/uploads/",
    r"/.well-known/", r"/sitemap", r"/feed/", r"\.xml$",
    # Filter out auth/account/footer pages that pollute search results
    r"/login(\?|/|$)", r"/signup(\?|/|$)", r"/register(\?|/|$)", r"/signin(\?|/|$)",
    r"/account(\?|/|$)", r"/checkout", r"/pricing(\?|/|$)$",  # vendors' own pricing
    r"/deals(\?|/|$)", r"/affiliate", r"/advertise", r"/legal/", r"/privacy",
    r"/cookies?", r"/terms",
    # Video sites usually aren't webpage backlink targets we'd outreach to
    r"^https?://(www\.)?(youtube|vimeo|dailymotion)\.",
    # Search engine self-referrals
    r"^https?://(www\.)?(google|bing|yahoo|duckduckgo|brave|yandex)\.",
]
URL_SKIP_RE = re.compile("|".join(URL_SKIP_PATTERNS), re.I)

# Topical relevance keywords — pages should mention these
TOPICAL_KEYWORDS = [
    "voip", "ucaas", "business phone", "cloud phone", "phone system",
    "ai receptionist", "call center", "contact center", "sip",
    "smb", "small business", "enterprise", "remote work", "saas",
    "comparison", "review", "best", "top", "alternative", "vs",
    "buyer guide", "buying guide", "ip phone",
]

# Filtering thresholds
DA_THRESHOLD = 35  # lowered from 50 because unknown_default heuristic returns 35; tighter filter rejected legit sites
RELEVANCE_THRESHOLD = 4  # lowered from 5 — most VoIP review pages hit 4-6 keywords, 5 was over-strict
MAX_PAGES_PER_QUERY = 12
MAX_VERIFY_PER_TARGET = 100  # cap how many target URLs we visit-and-verify

# DialPhone positioning (used in pitch generation)
DP_USP = {
    "core_price": "$20",
    "uptime": "99.999%",
    "ai_in_base": "AI receptionist included in base $20 plan",
    "compliance": "SOC 2, HIPAA, GDPR, PCI-DSS",
    "calculator_url": "https://dialphonelimited.codeberg.page/calculator/",
    "homepage": "https://dialphone.com",
    "trial": "14-day free trial, no credit card",
}


# ============================================================
# EXCLUSION SETS (loaded from existing files)
# ============================================================
def load_exclusion_sets():
    existing = set()
    try:
        for r in csv.DictReader(open("output/backlinks_final_truth.csv", encoding="utf-8")):
            if r["status"] == "success":
                d = urlparse(r["backlink_url"]).netloc.lower().replace("www.", "")
                if d: existing.add(d)
    except Exception as e:
        print(f"  warn: couldn't load existing referring domains: {e}")

    pitched = set()
    try:
        for r in csv.DictReader(open("output/outreach_targets.csv", encoding="utf-8")):
            d = (r.get("domain") or "").lower().replace("www.", "").strip()
            if d: pitched.add(d)
    except Exception as e:
        print(f"  warn: couldn't load pitched targets: {e}")

    blocked = {d.lower() for d in BLOCKED_HIGH_SPAM_DOMAINS}
    return existing, pitched, blocked


# ============================================================
# SEARCH — Mojeek primary, Brave fallback (no API keys, no rate-limit issues at this volume)
# ============================================================
def mojeek_search(page, query, max_results=12):
    """Mojeek HTML search. Open index, no API key, returns clean URLs."""
    url = f"https://www.mojeek.com/search?q={quote_plus(query)}"
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=20000)
        page.wait_for_timeout(2500)
        results = page.evaluate("""() => {
            const items = [...document.querySelectorAll('.results li h2 a, .results-standard li a.title, a.ob, .results a[href*=http]')];
            const seen = new Set();
            const out = [];
            for (const a of items) {
                const u = a.href;
                if (!u || seen.has(u) || !u.startsWith('http')) continue;
                if (u.includes('mojeek.com')) continue;
                seen.add(u);
                out.push({url: u, text: (a.innerText||'').trim().slice(0,200)});
                if (out.length >= 30) break;
            }
            return out;
        }""")
        return results[:max_results]
    except Exception as e:
        return []


def brave_search(page, query, max_results=12):
    """Brave Search fallback. Used if Mojeek returns 0 results."""
    url = f"https://search.brave.com/search?q={quote_plus(query)}"
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=20000)
        page.wait_for_timeout(2500)
        results = page.evaluate("""() => {
            const items = [...document.querySelectorAll('[data-type=\"web\"] a, .snippet a, a.h, [class*=result] a[href*=http]')];
            const seen = new Set();
            const out = [];
            for (const a of items) {
                const u = a.href;
                if (!u || seen.has(u) || !u.startsWith('http')) continue;
                if (u.includes('brave.com') || u.includes('search.brave.com')) continue;
                seen.add(u);
                out.push({url: u, text: (a.innerText||'').trim().slice(0,200)});
                if (out.length >= 25) break;
            }
            return out;
        }""")
        return results[:max_results]
    except Exception as e:
        return []


def search(page, query, max_results=12):
    """Multi-engine search with fallback. Mojeek primary, Brave fallback."""
    results = mojeek_search(page, query, max_results)
    if not results:
        time.sleep(2)
        results = brave_search(page, query, max_results)
    return results

# Backward-compat alias
ddg_search = search


# ============================================================
# PAGE ANALYZER (visit candidate, verify competitor link, score relevance)
# ============================================================
def analyze_page(page, candidate_url, competitor_domain, competitor_name):
    """Return dict with: mentions_competitor, links_competitor (bool), relevance_score, text_length, contact_email.

    Strategy: a page is a valid pitch target if it MENTIONS the competitor in body text or title
    (most editorial reviews mention competitors without outbound-linking them — affiliate patterns).
    Outbound link presence is a +scoring bonus, not a hard filter.
    """
    try:
        page.goto(candidate_url, wait_until="domcontentloaded", timeout=15000)
        page.wait_for_timeout(1800)

        body_text = page.evaluate("(document.body || {}).innerText || ''")
        body_lower = body_text.lower()
        title = page.title()[:200]
        title_lower = title.lower()

        # Skip anti-bot challenge pages
        if len(body_text) < 600 or "just a moment" in title_lower or "checking your browser" in body_lower[:600]:
            return {"ok": False, "error": "anti_bot_challenge_or_stub_page"}

        comp_lower = competitor_name.lower()
        comp_dom_lower = competitor_domain.lower()

        # Mention check — text or title contains competitor name
        mentions_competitor = (comp_lower in body_lower) or (comp_lower in title_lower)

        # Outbound link bonus
        links_competitor = page.evaluate(f"""() => {{
            const links = [...document.querySelectorAll('a[href]')];
            return links.some(a => (a.href || '').toLowerCase().includes('{comp_dom_lower}'));
        }}""")

        # Relevance scoring — count topical keywords (cap at 10)
        rel_score = sum(1 for kw in TOPICAL_KEYWORDS if kw in body_lower)
        rel_score = min(10, rel_score)

        # Find contact email
        email_match = re.search(r'\b([a-z0-9._-]+@[a-z0-9.-]+\.[a-z]{2,})\b', body_lower)
        contact = email_match.group(1) if email_match else ""

        return {
            "ok": True,
            "mentions_competitor": mentions_competitor,
            "links_competitor": links_competitor,
            "relevance_score": rel_score,
            "title": title,
            "contact_email": contact,
            "text_length": len(body_text),
        }
    except Exception as e:
        return {"ok": False, "error": str(e)[:120]}


# ============================================================
# DA ESTIMATION
# ============================================================
def estimate_da(domain):
    """Best-effort DA estimate. Falls back to heuristics for unknown domains."""
    d = domain.lower().replace("www.", "")
    if d in KNOWN_DA:
        return KNOWN_DA[d], "known"
    # Heuristics for unknown domains
    if d.endswith(".gov") or d.endswith(".edu"):
        return 75, "edu_gov_heuristic"
    if d.endswith(".org") and len(d) < 20:
        return 55, "org_heuristic"
    if any(x in d for x in [".medium.com", ".substack.com", ".tumblr.com", ".wordpress.com", ".blogspot.com"]):
        return 60, "subdomain_heuristic"
    # Default for unknown — conservative
    return 35, "unknown_default"


# ============================================================
# SCORING (combines DA + relevance + competitor linkage)
# ============================================================
def score_target(da, relevance, mentions_competitor, links_competitor, text_length):
    """ROI score: DA × relevance × linkage signal × content depth.

    Mention is the qualifier; outbound link is a +bonus on top.
    """
    if not mentions_competitor:
        return 0  # filter out — page isn't actually about the competitor
    if da < DA_THRESHOLD or relevance < RELEVANCE_THRESHOLD:
        return 0  # below quality cutoff
    length_factor = min(1.0, text_length / 2000) if text_length else 0.3
    link_bonus = 8 if links_competitor else 0  # outbound link present = easier ask
    raw = (da * 0.5) + (relevance * 4) + (length_factor * 10) + link_bonus
    return round(raw, 1)


# ============================================================
# PITCH DRAFT (templated + per-target hook)
# ============================================================
ANCHOR_ROTATION = ["DialPhone", "https://dialphone.com", "this tool",
                   "the calculator", "DialPhone", "https://dialphone.com",
                   "VoIP cost calculator", "DialPhone"]

def generate_pitch(target, anchor_idx):
    """Generate a 50-90 word pitch tailored to the target page."""
    title = target["title"][:80]
    competitor = target["linked_competitor"]
    anchor = ANCHOR_ROTATION[anchor_idx % len(ANCHOR_ROTATION)]
    domain = target["target_domain"]

    subject = f"Adding DialPhone alongside {competitor} in your coverage"
    body = (
        f"Hi {domain.split('.')[0]} team,\n\n"
        f"I noticed your piece — \"{title}\" — references {competitor}. "
        f"Would you consider adding DialPhone to that coverage? We're a 2024-founded US/Canada VoIP "
        f"provider at {DP_USP['core_price']}/user (28-33% below RingCentral & 8x8 base plans), with "
        f"{DP_USP['uptime']} uptime SLA and {DP_USP['ai_in_base']}.\n\n"
        f"Free comparison tool — {anchor} — at {DP_USP['calculator_url']}: 13 providers, 3-year TCO, "
        f"verification badges per provider. No signup, free for editorial use, embed snippet included.\n\n"
        f"Happy to provide a demo or quote.\n\n"
        f"— Aditya Shukla, Growth Operations\n"
        f"DialPhone — {DP_USP['homepage']}"
    )
    return subject, body


# ============================================================
# MAIN PIPELINE
# ============================================================
def main():
    print("=" * 70)
    print("Competitor Backlink Intercept Tool — building target pool")
    print("=" * 70)

    existing, pitched, blocked = load_exclusion_sets()
    print(f"\nExclusions loaded:")
    print(f"  existing referring domains:  {len(existing)}")
    print(f"  already-pitched targets:     {len(pitched)}")
    print(f"  blocked high-spam domains:   {len(blocked)}")

    # Build skip set
    skip_domains = existing | pitched | blocked | {
        # Always skip these — competitors themselves, social sites, our own
        "ringcentral.com", "8x8.com", "dialpad.com", "nextiva.com", "vonage.com",
        "goto.com", "zoom.us", "ooma.com", "grasshopper.com", "openphone.com", "quo.com",
        "microsoft.com", "google.com", "workspace.google.com",
        "dialphone.com", "dialphone.ai",
        "facebook.com", "twitter.com", "x.com", "instagram.com", "youtube.com",
        "duckduckgo.com", "bing.com", "yahoo.com",
    }

    pw, browser = get_browser(CFG, headed_override=False)
    ctx, page = new_page(browser, CFG, "competitor-intercept")

    # Phase 1: gather candidate URLs from search
    print(f"\n--- Phase 1: search for candidate pages ---")
    candidates = []  # list of dicts: url, query, competitor, ddg_text
    seen_urls = set()
    for comp in COMPETITORS:
        print(f"\n  [{comp['name']}]")
        # Use the top 3 most diverse query patterns (full set causes rate-limit on free engines)
        for q in comp["queries"][:3]:
            results = search(page, q, max_results=MAX_PAGES_PER_QUERY)
            print(f"    \"{q[:50]}\" -> {len(results)} results")
            for r in results:
                u = r["url"]
                if u in seen_urls: continue
                if URL_SKIP_RE.search(u): continue
                d = urlparse(u).netloc.lower().replace("www.", "")
                if not d or d in skip_domains: continue
                seen_urls.add(u)
                candidates.append({
                    "url": u, "query": q, "competitor": comp["name"],
                    "competitor_domain": comp["domain"], "ddg_text": r["text"],
                })
            time.sleep(6)  # be polite to free search engines
    print(f"\n  total unique candidates after dedup + skip-filter: {len(candidates)}")

    # Phase 2: visit + verify + score
    print(f"\n--- Phase 2: verify {min(len(candidates), MAX_VERIFY_PER_TARGET)} candidates ---")
    targets = []
    visited = 0
    skipped_no_mention = 0
    skipped_anti_bot = 0
    skipped_low_score = 0
    debug_log = []  # full record of every verify, including rejected
    for c in candidates:
        if visited >= MAX_VERIFY_PER_TARGET: break
        visited += 1
        analysis = analyze_page(page, c["url"], c["competitor_domain"], c["competitor"])
        d = urlparse(c["url"]).netloc.lower().replace("www.", "")
        debug_entry = {"domain": d, "url": c["url"], "competitor": c["competitor"], "analysis_ok": analysis.get("ok"),
                       "error": analysis.get("error", ""),
                       "mentions": analysis.get("mentions_competitor", False),
                       "links": analysis.get("links_competitor", False),
                       "rel": analysis.get("relevance_score", 0),
                       "text_len": analysis.get("text_length", 0)}
        if not analysis["ok"]:
            skipped_anti_bot += 1
            debug_entry["status"] = "rejected_error"
            debug_log.append(debug_entry)
            continue
        if not analysis["mentions_competitor"]:
            skipped_no_mention += 1
            debug_entry["status"] = "rejected_no_mention"
            debug_log.append(debug_entry)
            continue
        da, da_source = estimate_da(d)
        debug_entry["da"] = da
        debug_entry["da_source"] = da_source
        roi = score_target(da, analysis["relevance_score"], True, analysis["links_competitor"], analysis["text_length"])
        debug_entry["roi"] = roi
        if roi == 0:
            skipped_low_score += 1
            debug_entry["status"] = "rejected_low_score"
            debug_log.append(debug_entry)
            continue
        debug_entry["status"] = "qualified"
        debug_log.append(debug_entry)
        anchor = ANCHOR_ROTATION[len(targets) % len(ANCHOR_ROTATION)]
        target = {
            "target_domain": d,
            "target_url": c["url"],
            "linked_competitor": c["competitor"],
            "da_estimate": da,
            "da_source": da_source,
            "contact_email": analysis["contact_email"],
            "relevance_score": analysis["relevance_score"],
            "roi_score": roi,
            "title": analysis["title"],
            "why_relevant": f"{'Links' if analysis['links_competitor'] else 'Mentions'} {c['competitor']}; {analysis['relevance_score']}/10 topical match",
            "suggested_anchor_text": anchor,
            "last_seen_active": datetime.now().date().isoformat(),
            "status": "queued",
        }
        targets.append(target)
        link_marker = "LINK" if analysis["links_competitor"] else "TEXT"
        print(f"  [{visited:3d}/{MAX_VERIFY_PER_TARGET}] {link_marker} DA={da:>3d} rel={analysis['relevance_score']:>2d} ROI={roi:>5.1f}  {d}")
    print(f"  filter stats — anti_bot/error: {skipped_anti_bot}, no_mention: {skipped_no_mention}, low_score: {skipped_low_score}")
    # Save full debug log
    with open("output/backlink_intercept_debug.json", "w", encoding="utf-8") as f:
        json.dump(debug_log, f, indent=2)
    print(f"  debug log: output/backlink_intercept_debug.json ({len(debug_log)} entries)")

    print(f"\n  qualifying targets: {len(targets)}")

    # Phase 3: dedupe by domain (keep highest ROI per domain), sort
    by_domain = {}
    for t in targets:
        d = t["target_domain"]
        if d not in by_domain or t["roi_score"] > by_domain[d]["roi_score"]:
            by_domain[d] = t
    targets = sorted(by_domain.values(), key=lambda x: -x["roi_score"])
    print(f"  after domain-dedup: {len(targets)} unique domains")

    # Phase 4: generate pitch drafts for top 50
    print(f"\n--- Phase 4: generate pitch drafts for top {min(50, len(targets))} ---")
    for i, t in enumerate(targets[:50]):
        subj, body = generate_pitch(t, i)
        t["suggested_pitch_subject"] = subj
        t["suggested_pitch_body"] = body
    for t in targets[50:]:
        t["suggested_pitch_subject"] = ""
        t["suggested_pitch_body"] = ""

    # Phase 5: write CSV
    print(f"\n--- Phase 5: write outputs ---")
    fieldnames = [
        "target_domain", "target_url", "linked_competitor", "da_estimate", "da_source",
        "contact_email", "relevance_score", "roi_score", "title", "why_relevant",
        "suggested_pitch_subject", "suggested_pitch_body", "suggested_anchor_text",
        "last_seen_active", "status",
    ]
    out_csv = "output/competitor_backlink_targets_v2.csv"
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for t in targets:
            w.writerow({k: t.get(k, "") for k in fieldnames})
    print(f"  wrote {out_csv} ({len(targets)} targets)")

    # Phase 6: risk dashboard
    da_buckets = Counter()
    for t in targets:
        da = t["da_estimate"]
        bucket = "80+" if da >= 80 else "70-79" if da >= 70 else "60-69" if da >= 60 else "50-59"
        da_buckets[bucket] += 1
    anchor_dist = Counter(t["suggested_anchor_text"] for t in targets[:50])
    risk = {
        "total_targets": len(targets),
        "da_distribution": dict(da_buckets),
        "anchor_distribution_top50": dict(anchor_dist),
        "max_anchor_pct": max(anchor_dist.values()) / max(1, sum(anchor_dist.values())) if anchor_dist else 0,
        "competitor_distribution": dict(Counter(t["linked_competitor"] for t in targets)),
        "projected_pitches_per_week": 5,
        "projected_landings_per_week": "0.4-0.8 (10-15% conversion at DA 50+)",
        "notes": [
            "Velocity gate: cap pitches at 5/day (≤8 new editorial backlinks/week absorbed by Google).",
            "We're 9 days into 28-42 day disavow recovery — new editorial backlinks signal positive trend.",
            "Pitch top 50 first; remaining 51+ are bulk targets without per-page personalization.",
            "Cross-check `output/outreach_targets.csv` before sending — don't double-pitch.",
        ],
        "generated_at": datetime.now().isoformat(),
    }
    out_risk = "output/backlink_intercept_risk.json"
    with open(out_risk, "w", encoding="utf-8") as f:
        json.dump(risk, f, indent=2)
    print(f"  wrote {out_risk}")

    # Phase 7: top-5 summary
    print("\n" + "=" * 70)
    print("TOP 5 HIGHEST-ROI TARGETS")
    print("=" * 70)
    for i, t in enumerate(targets[:5], 1):
        print(f"\n  #{i}  {t['target_domain']}  (DA {t['da_estimate']}, ROI {t['roi_score']})")
        print(f"      -> {t['target_url'][:90]}")
        print(f"      title: {t['title'][:80]}")
        print(f"      contact: {t['contact_email'] or '(check site contact page)'}")
        print(f"      links: {t['linked_competitor']} | anchor for our pitch: {t['suggested_anchor_text']}")

    print("\n" + "=" * 70)
    print(f"SUMMARY")
    print("=" * 70)
    print(f"  candidates discovered:  {len(candidates)}")
    print(f"  candidates verified:    {visited}")
    print(f"  qualifying targets:     {len(targets)} unique domains")
    print(f"  with personalized pitch: {min(50, len(targets))}")
    print(f"  DA distribution:        {dict(da_buckets)}")
    print(f"\n  output: {out_csv}")
    print(f"  risk:   {out_risk}")

    try: ctx.close(); browser.close(); pw.stop()
    except: pass


if __name__ == "__main__":
    main()
