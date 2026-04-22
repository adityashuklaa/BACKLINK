# Double-Down Plan — Clean Sources Only

**Date:** 2026-04-18 (rev 2026-04-19 — buyer market corrected from UK to US + Canada)
**Starting state:** 161 clean backlinks, avg DA 77, 95% dofollow
**Target by end of May 2026:** 220 clean backlinks, 20+ referring domains, all spam score ≤ 25
**Company:** DialPhone Limited — Hong Kong registered, buyer market = US + Canada. No UK targeting.

## What just happened (summary)

- 326 high-spam backlinks quarantined (status flipped to `spam_quarantined`)
- Disavow file generated at `output/disavow.txt` — upload to Google Search Console
- Dashboard filters to clean links only
- SEO score now spam-penalized

## The portfolio going forward

### Sources we continue (spam score ≤ 25)

| Source | Current count | Cap / week | Notes |
|--------|--------------|------------|-------|
| Dev.to articles | 68 | 2 per week | Humanizer-gated, fresh topics only |
| GitLab repos | 36 | 0 (frozen) | Already over-concentrated; let mature |
| Codeberg repos | 33 | 0 (frozen) | Same |
| GitHub repos | 7 | 0 (frozen) | Same |
| Quora answers | 3 | 1 per week | After profile rename to [PERSONA_TBD] |
| Trustpilot | 0 | 1 setup + ongoing reviews | Apply free tier, US/CA reviews |
| G2 / Capterra / GetApp / SW Advice | 0 | 1 setup | US-centric SaaS dirs, pack to rewrite |
| TrustRadius | 0 | 1 setup | US B2B reviews, DA 82 |
| Clutch / GoodFirms | 0 | 1 setup | US B2B services dirs |
| AlternativeTo / SaaSHub | 0 | 1 setup each | Product-fit, market-agnostic |
| Product Hunt | 0 | 1 launch | US product-launch platform |
| Crunchbase | 0 | 1 setup | DA 92, needs DUNS or LinkedIn |
| US business dirs (BBB, Manta, YP.com, Yelp, Foursquare, Bing Places, Chamber) | 0 | 1 each | 7 US local-biz listings |
| Canada business dirs (YP.ca, Canada411, Goldbook, ProFile Canada) | 0 | 1 each | 4 CA listings |
| VoIP-specific (GetVoIP, VoIP Review, WhichVoIP) | 0 | 1 each | US/CA buyer-intent traffic |
| Stack Overflow | 0 | 1 answer / week | Slow burn, DA 93 |
| HARO / Qwoted | 0 | 2 replies / week | US editorial links |
| LinkedIn (company page + [PERSONA_TBD]) | 0 | 2-3 posts / week | DA 98 ongoing |

### Sources we never touch again (spam score > 25)

paste.rs, friendpaste.com, godbolt.org, termbin.com, ideone.com, bpa.st, paste2.org, snippet.host, pastebin.fi, dpaste.com, glot.io.

Hard-coded in `core/humanize.py`-style gate → I'll wire this into the publish pipeline as a pre-flight check.

## 30-day execution plan

### Week 1 (now → 2026-04-26): the directory sprint — US + Canada edition
**Target:** +12 real buyer-intent backlinks

Ordered by impact/effort ratio. Paste-ready pack at `docs/directory_submission_pack_PASTE_READY.md` **needs rewrite** — current copy is UK-toned (£, Limited company, VAT). Switch to US/CA vocab: $, LLC/Inc, EIN/BN, +1 phone.

**What you need before starting** (most dirs require at least one of these):
- US phone number (Google Voice or your own DialPhone +1 line)
- US OR Canada mailing address (can be a virtual mailbox like Earth Class Mail, or HK HQ if dir allows foreign biz)
- DUNS number (for Crunchbase + enterprise dirs) — free from Dun & Bradstreet, takes ~30 days, start now
- EIN (if US LLC/subsidiary) OR just declare as foreign corp with HK parent
- Logo, 2-3 product screenshots, 60-word + 160-word + 500-word descriptions

| Day | Task | Time |
|-----|------|------|
| Mon | Upload `output/disavow.txt` to Google Search Console | 5 min |
| Mon | Create LinkedIn company page (US HQ or HK HQ — your call) | 30 min |
| Mon | Trustpilot — claim domain, request US/CA review invites | 20 min |
| Mon | Start DUNS application (30-day wait, start the clock now) | 15 min |
| Tue | G2 — full product listing | 45 min |
| Tue | Capterra submission (→ 3 backlinks: Capterra + GetApp + SoftwareAdvice, all Gartner-owned) | 30 min |
| Wed | TrustRadius + Clutch + GoodFirms | 45 min |
| Wed | AlternativeTo + SaaSHub + Product Hunt (queue launch for later) | 40 min |
| Wed | Fix Quora profile (rename to [PERSONA_TBD], real photo, warm 2 weeks) | 30 min |
| Thu | BBB (Better Business Bureau) + Manta + Yellowpages.com | 45 min |
| Thu | Yelp for Business + Foursquare for Business + Bing Places | 30 min |
| Fri | Yellowpages.ca + Canada411 + Goldbook.ca + ProFile Canada | 45 min |
| Fri | VoIP-specific: GetVoIP + VoIP Review + WhichVoIP | 40 min |

**Expected backlinks earned by end of week 1:** 14-18 live within days (product-fit + VoIP dirs are instant), + 3-5 more within 2-4 weeks (BBB verification, YP approval cycles). Crunchbase requires DUNS → late May.

### Week 2 (2026-04-26 → 2026-05-02): content sprint
**Target:** +4 real dofollow + Stack Overflow foothold

| Task | Time |
|------|------|
| Publish 2 humanized Dev.to articles (fresh topics, not rehash) | 2 hrs |
| Post 2 humanized Quora answers (now from [PERSONA_TBD] account, after profile warm) | 1 hr |
| Answer 2 high-view VoIP questions on Stack Overflow | 2 hrs |
| LinkedIn: 3 posts from [PERSONA_TBD] persona + 2 on company page | 2 hrs |
| HARO / Qwoted signup + first 2 reply attempts (US editorial) | 2 hrs |

**Expected backlinks earned:** 6-8 (2 Dev.to dofollow + 2 Quora + 1-2 SO + potentially 1 editorial from HARO).

### Week 3 (2026-05-03 → 2026-05-09): outreach + reviews
**Target:** First editorial backlink + review base

| Task | Time |
|------|------|
| Guest post outreach to 8 US/CA business + SaaS blogs | 3 hrs |
| Email last 30 paying customers asking for Trustpilot review | 1 hr |
| 2 more Dev.to articles | 2 hrs |
| 2 more Quora answers | 1 hr |
| HARO / Qwoted replies (4 per week target now) | 3 hrs |
| LinkedIn ongoing (6 posts) | 2 hrs |

**Expected backlinks:** 4 Dev.to + 2 Quora + 15+ Trustpilot reviews + 1-2 potential guest post responses (slow cycle).

### Week 4 (2026-05-10 → 2026-05-16): compound + measure
**Target:** First tracked ranking movement

| Task | Time |
|------|------|
| Google Search Console: check which keywords we're ranking for, impressions trend | 30 min |
| Set up rank tracker for 20 US/CA VoIP keywords (google.com + google.ca) | 1 hr |
| 2 more Dev.to articles | 2 hrs |
| Respond to any Capterra/G2 review requests | 30 min |
| Send follow-up email round for Trustpilot reviews | 30 min |
| Plan month 2 based on what's actually ranking | 1 hr |

## Cumulative 30-day outcome estimate

| Metric | Today | Day 30 target |
|--------|-------|--------------|
| Clean backlinks (spam ≤ 25) | 157 | 200-220 |
| Referring domains | 6 | 20+ |
| Dofollow | 149 | 180+ |
| Avg DA of portfolio | 77 | 82+ |
| DA 70+ backlinks | 77 | 140+ |
| Real buyer-intent directory listings | 0 | 12+ |
| Editorial mentions (HARO-style) | 0 | 1-3 |
| Trustpilot reviews | 0 | 20+ |

## The guardrails (so we don't relapse)

1. **Pre-publish spam gate** — I'll add a `source_quality_gate()` check that blocks any publish function from posting to a domain with spam score > 25
2. **Weekly audit script** — runs every Monday, alerts if any domain's concentration > 25% or if any new spam_quarantined row appeared
3. **Dashboard "Risk" section** — now always visible, updates in real-time
4. **Humanize check** — already wired, continues rejecting AI-voice drafts

## The single rule going forward

> Every new backlink must answer YES to both:
> 1. Is the source domain's spam score ≤ 25?
> 2. Would a real US or Canadian business buyer ever land on this page via Google?
>
> If either answer is NO, don't post it.

This rule would have prevented every paste-site link from day 1.
