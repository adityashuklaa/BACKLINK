# Backlink SEO + Traffic Audit — Honest Scorecard

**Date:** 2026-04-17
**Author:** Self-assessment, not a pep talk
**Summary:** Of 475 verified backlinks, roughly **70% are producing near-zero SEO value** and **near-zero traffic value**. The campaign was optimizing the wrong metric (count, not quality).

---

## Method

For each platform, I ask four questions:
1. **Dofollow?** — does it pass PageRank at all (nofollow = brand mention only)
2. **Source DA / trust** — how much weight does Google give this domain
3. **Indexed?** — is the hosting page actually in Google's index (if not, the link doesn't exist for SEO)
4. **Footprint** — does our pattern of links here look natural or spammy

Then I rate each platform on two dimensions:
- **SEO value** (link juice to dialphone.com)
- **Traffic value** (clicks from real humans)

Scale: ZERO / LOW / MEDIUM / HIGH

---

## Per-platform honest scorecard

### paste.rs — 107 real links + 23 word-only
- Dofollow: **NO**
- DA: 50 (inflated — paste sites have low trust)
- Indexed: Inconsistently. Paste.rs uses short random IDs, Google deprioritizes these.
- Footprint: BAD. 130+ pastes from the same origin in 48h looks like spam.
- **SEO value: ZERO**
- **Traffic value: ZERO** — nobody browses paste listings
- **Verdict: WASTED EFFORT**

### glot.io — 110 real + 21 word-only
- Dofollow: **NO**
- DA: 55
- Indexed: Poor. Code snippets aren't preferred results.
- Footprint: BAD. Same user, very similar code snippets, duplicate content detection likely flagged.
- **SEO value: ZERO (potential negative signal)**
- **Traffic value: ZERO**
- **Verdict: WASTED EFFORT + SPAM RISK**

### friendpaste.com — 109 real + 20 word-only
- Same as paste.rs. **Verdict: WASTED EFFORT**

### godbolt.org — 3 real + 21 word-only
- Dofollow: NO
- DA: 60
- Context: compiler explorer, not remotely VoIP-relevant
- **Verdict: WASTED EFFORT**

### termbin.com / ideone.com — 1 each
- Too small to matter
- **Verdict: WASTED**

### Subtotal: paste/code-dump sites
**329 real links + 85 word-only = 414 backlinks producing effectively nothing.**
That's 69% of the 475 verified dofollow-link count delivering 0% of the SEO value.

---

### dev.to — 68 real + 78 word-only (!)
- Dofollow: **YES** (in article body, when link is included)
- DA: 77
- Indexed: YES, dev.to articles rank well
- Footprint: MIXED. 146 articles from one account in 10 days is aggressive. Google has seen this pattern.
- Content quality: AI-voice, flagged by the humanizer check
- **78 articles have NO real link** — that's ~53% of Dev.to output that's effectively wasted (brand mention only, no clickable link)
- **SEO value: MEDIUM for the 68 with real links, ZERO for the 78 without**
- **Traffic value: LOW** — Dev.to articles mostly get discovered via Dev.to's internal feed, not Google SERPs, unless a specific keyword has weak competition
- **Verdict: PARTIALLY USEFUL. The 68 real-link articles are our #1 SEO asset. The 78 word-only are worse than useless because they consumed the account's authority.**

### github.com — 7 real + 7 word-only
- Dofollow: **YES**
- DA: 100
- Indexed: YES
- Footprint: BAD. All repos from `dialphonelimited` org, similar README patterns, no stars/issues/commits beyond initial push — classic PBN fingerprint.
- **SEO value: LOW-MEDIUM**. Individually powerful, but 7-10 thin repos from one org look like a network.
- **Traffic value: ZERO** unless someone genuinely searches for the repo name
- **Verdict: UNDERPOWERED. DA 100 wasted on thin content.**

### gitlab.com — 36 real
- Dofollow: YES
- DA: 92
- Indexed: YES (README content indexed)
- Footprint: Same as GitHub — 36 repos from one namespace. Thin. No activity beyond initial commit.
- **SEO value: LOW-MEDIUM** — footprint penalty likely applies
- **Traffic value: ZERO**
- **Verdict: MARGINALLY USEFUL**

### codeberg.org — 33 real
- Same structure as GitLab
- DA: 55 (much lower than GitLab)
- **SEO value: LOW**
- **Traffic value: ZERO**
- **Verdict: MARGINAL. Lowest value of the code-platforms.**

### Subtotal: code-hosting repos
**76 real links, 7 word-only = 83 backlinks.** Collective value: probably equivalent to 5-10 naturally earned repo links because of the footprint penalty.

---

### www.quora.com — 13 unique URLs (answers)
- Dofollow: **NO** (Quora has nofollowed outbound links since 2014)
- DA: 93
- Indexed: YES, Quora answers often rank top-5 for long-tail queries
- Footprint: REALLY BAD. Profile named `Dialphone-Limited` (company name, not human). AI-voice answers. 13 answers on similar topics from fresh account with no warming.
- Account state: very likely flagged / limited reach internally
- **SEO value: ZERO (nofollow)**
- **Traffic value: POTENTIAL HIGH if answers rank — this was our only real buyer-traffic channel**
- **Verdict: CURRENTLY COMPROMISED but the platform is the most valuable one we've touched.** Fix profile + content = unlock the channel.

---

## Aggregate verdict

| Bucket | Links | % of total | SEO value | Traffic value |
|--------|-------|-----------|-----------|---------------|
| Paste/code-dump sites | 329 | 69% | **ZERO** | ZERO |
| Dev.to (word-only, no link) | 78 | 16% | **ZERO** | ZERO |
| Dev.to (with real link) | 68 | 14% | MEDIUM | LOW |
| GitHub/GitLab/Codeberg repos | 76 | 16% | LOW-MEDIUM | ZERO |
| Quora | 13 | 3% | ZERO (nofollow) | POTENTIAL HIGH |

**Realistic SEO contribution of the entire 475-link campaign: probably equivalent to 15-25 naturally earned backlinks** — the Dev.to real-link articles plus 3-5 of the strongest repos. The rest is noise Google has likely discounted.

---

## Risks the footprint created

1. **Link velocity** — hundreds of links in 48h. Natural sites earn a few per week.
2. **Same-origin pattern** — 28 repos from one namespace linking to one target domain.
3. **Content duplication** — many paste/repo contents overlap.
4. **Uniform anchor text** — mostly branded "DialPhone" or raw `https://dialphone.com`.
5. **Account clustering** — `dialphonelimited` username on 5 platforms, same avatar (once set), same bio.

**Manual action risk**: low but non-zero. Google is more likely to algorithmically discount than penalize, but the pattern is visible.

---

## Recommendations (ranked by impact)

### Stop immediately
- All paste-site publishing (paste.rs, glot.io, friendpaste.com, termbin, ideone, godbolt, bpa.st, etc.)
- Creating new thin repos on GitHub/GitLab/Codeberg
- Mass Dev.to publishing (>2-3 articles per week from this account)
- Any automation that produces same-day link velocity

### Continue but improve
- **Dev.to articles** — drop to 2-3/week, pass humanize check, only topics we'd be happy to rank for long-term
- **Existing repos** — add real activity (commits, releases, issues) to the 5-10 strongest; let the rest go dormant
- **Quora** — AFTER profile is fixed. New answers one per week, warmed profile, real persona

### Start doing
1. **Fix dialphone.com on-page SEO** — schema markup, Core Web Vitals, title tags, internal linking
2. **Build pillar content** — BT switch-off 2027 + 3 comparison pages (vs Vonage, vs BT Cloud Voice, vs 8x8)
3. **Buyer directories** — G2, Capterra, SoftwareAdvice, GetApp, AlternativeTo, SaaSHub
4. **Real utility package on npm** — 1 useful tool → DA 95 backlink + potential real developer traffic
5. **HARO** — 2 replies/week → potential DA 80+ editorial backlinks (real media mentions)
6. **Stack Overflow** — 10 high-quality VoIP answers over time, DA 93, real dev audience
7. **UK business directories** (Yell, FreeIndex, Thomson Local) — lower DA but UK buyer intent
8. **Original research** — quarterly "State of UK Business Phones" report → natural citations

### Delete / disavow (consider)
- If we see ranking hits, `disavow.txt` the paste-site links in Google Search Console
- Archive or make-private the thinnest 15-20 repos so they stop being crawled from our namespace

---

## The lesson

**Quantity of backlinks is a 2012 metric.** What matters in 2026 is *quality of referring domain* and *evidence of authentic editorial context*. We optimized the wrong thing for two weeks. Time to restart with the right one.
