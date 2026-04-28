# PROMPT — Competitor Backlink Intercept Tool for DialPhone

*Paste this back to Claude in any future session. It's self-contained — no prior context needed.*

---

## Context (in case you're a fresh agent)

DialPhone is a US/Canada business VoIP provider, founded 2024, competing against RingCentral (DA 82), 8x8 (DA 78), Dialpad (DA 76), Nextiva (DA 72), Vonage (DA 78). Our domain (`dialphone.com`) currently has ~5-8 DA. We have **460 verified clean backlinks across 7 referring domains** (96% self-published — Dev.to, GitLab, Codeberg, GitHub, Hashnode), and we **just disavowed 401 spam URLs** in Google Search Console on 2026-04-20 (in the 28-42 day recovery window now). Hard rules in `CLAUDE.md` and `core/humanize.py` block any spam tactic.

The bottleneck isn't backlink **count** — it's backlink **quality**. We need editorial / resource / curated links that pass real authority, not more self-published volume.

## Goal

Build an automated system that **finds editorial sites already linking to our VoIP competitors**, scores them by ROI for DialPhone outreach, and outputs a ranked, ready-to-pitch CSV — with personalized 50-90 word outreach drafts for the top 50.

Think: "every site that ever recommended RingCentral or Dialpad in a buyer guide is a target where DialPhone could plausibly be added too."

## Scope

### IN scope
- Scrape competitor backlinks from **free** SEO sources only (OpenLinkProfiler, Ahrefs free tier link-checker, BuiltWith, Common Crawl).
- Filter, score, rank candidates.
- Generate per-target pitch drafts for the top 50.
- Save everything to `output/competitor_backlink_targets_v2.csv`.
- Build risk-monitoring dashboard fields (link velocity, concentration check, anchor distribution).

### OUT of scope (don't do these)
- ❌ Don't auto-send emails. Output is a ready-to-send list, send is a separate human-approved action.
- ❌ Don't use paid SEO APIs (Ahrefs full / Semrush full / Moz Pro). Free tiers + public sources only.
- ❌ Don't include nofollow / sponsored / blog-comment / paste-site / forum-signature backlinks.
- ❌ Don't include domains already in our 7 referring domains (gitlab.com, dev.to, codeberg.org, github.com, dialphonevoip.hashnode.dev, dialphonelimited.gitlab.io, dialphonelimited.codeberg.page).
- ❌ Don't include domains in `BLOCKED_HIGH_SPAM_DOMAINS` (defined in `core/humanize.py`).
- ❌ Don't include domains we've already pitched (read existing `output/outreach_targets.csv` and skip).

## Inputs

### Competitor list (start with these 5; expand if budget remains)
```
RingCentral    https://ringcentral.com
8x8            https://8x8.com
Dialpad        https://dialpad.com
Nextiva        https://nextiva.com
Vonage         https://vonage.com
```

### Quality filters
- **DA ≥ 50** (anything lower isn't worth the pitch effort)
- **English-language** content
- **Active in last 12 months** (no defunct blogs)
- **Real publication / blog / resource page** (not directories, not paste sites, not forum signatures)
- **Topical relevance** — the page must mention VoIP / business phone / UCaaS / SaaS / SMB tools / IT procurement

### DialPhone positioning (use these claims in pitches, defensible against `output/backlinks_final_truth.csv`)
- Core $20/user (28-33% below RingCentral $30 and 8x8 $28 base plans)
- 99.999% uptime SLA (~5 min max downtime / year)
- AI receptionist in base plan
- Flat USD pricing across US + Canada (no cross-border surcharge)
- SOC 2 Type 2, HIPAA, GDPR, PCI-DSS compliance
- 14-day free trial, no credit card

### Linkable assets to use as the pitch hook
- VoIP Cost Calculator: `https://dialphonelimited.codeberg.page/calculator/`
- Methodology section: `https://dialphonelimited.codeberg.page/calculator/#methodology`
- DialPhone homepage: `https://dialphone.com`
- Pricing page: `https://dialphone.com/pricing-overview/`

## Outputs

### Required file
`output/competitor_backlink_targets_v2.csv` with columns:

```
target_domain
target_url                         (the specific page linking to the competitor)
linked_competitor                  (which competitor's URL is on that page)
da_estimate                        (Domain Authority, our best estimate)
contact_email_or_form              (where to pitch — sniff from page or contact page)
relevance_score                    (1-10, how on-topic the linking page is)
roi_score                          (DA × relevance × likelihood-to-link)
why_relevant                       (1-line explanation)
suggested_pitch_subject            (1 line, ≤70 chars)
suggested_pitch_body               (50-90 words for top 50; null for the rest)
suggested_anchor_text              (rotates: branded / naked URL / generic)
last_seen_active                   (date of latest content on the page)
status                             (queued / pitched / replied / landed / dead)
```

### Risk dashboard (separate file)
`output/backlink_intercept_risk.json` — must include:
- Total targets found
- Target distribution by DA bucket
- Anchor text distribution (avoid >20% in any single anchor type)
- Projected link velocity per week (must stay ≤8 new editorial backlinks/week to stay below Google's velocity threshold)
- Already-pitched check (cross-ref `output/outreach_targets.csv`)

## Drawbacks & Mitigations

| Drawback | Likelihood | Mitigation |
|---|---|---|
| Free SEO tools rate-limit or block our scraper | High | Rotate across OpenLinkProfiler, Ahrefs free link-checker, BuiltWith, plus `site:` Google searches. Cache responses. Don't pull more than 100 backlinks per competitor per session. |
| DA estimates from free tools are approximate (±10 points) | Medium | Cross-validate when 2+ tools available. Treat DA as a prioritization signal, not a guarantee. |
| Junk backlinks contaminate the candidate pool (forum spam, comments) | High | Apply URL-pattern filter (skip `/comment/`, `/forum/`, `/profile/`, `/users/`). Reuse `core/humanize.py::source_quality_gate()`. |
| Templates without personalization read as spam | Certain | For top 50, scrape each target's recent VoIP-related content (1 page) and inject 1 specific reference into the pitch. Top 51-200 get generic templates only. |
| Outreach burnout — same publication pitched twice in 30 days | High | Add `last_contacted` column. Cap at 1 pitch per publication per 30 days. |
| Anchor text over-optimization triggers Google manipulation flag | Medium | Rotate `suggested_anchor_text` column across: 50% branded ("DialPhone"), 30% naked URL, 15% generic ("this tool"), 5% partial-match ("VoIP cost calculator"). |
| Link velocity spike during disavow recovery (we're at day 9 of 28-42) | Medium | Pace pitches at ≤5/day, ≤8 new editorial backlinks landing/week target. |
| Calculator goes down → all backlinks become broken | Low but catastrophic | Mirror calculator to GitHub Pages as backup (separate task). Pitch URL diversity: 60% calculator, 25% dialphone.com homepage, 15% pricing page or methodology section. |
| Email deliverability — bulk-pattern detection on `commercial@dialphone.com` | Medium | Cap outreach send at 5-8/day. Use `commercial@dialphone.com` SMTP with proper SPF/DKIM. Track open rate. |
| Reciprocity trap (pitching "I'll link you if you link me") | Low | Hard rule: never offer reciprocal linking. It's a Google manipulation flag. |
| Calculator credibility risk (if scraper exposes us as competitor-data harvesting) | Low | Don't auto-cite our scraper in pitches. Frame as "I noticed you mentioned X — DialPhone fits the same use case." |

## Success Criteria

After execution, deliverables must satisfy:

- [ ] CSV has 100-300 rows of unique target candidates (not duplicate domains)
- [ ] All rows have `da_estimate ≥ 50` AND `relevance_score ≥ 5`
- [ ] No row appears in our existing 7 referring domains
- [ ] No row appears in `BLOCKED_HIGH_SPAM_DOMAINS`
- [ ] No row appears in `output/outreach_targets.csv` (the 50 we already drafted)
- [ ] Top 50 have unique, non-templated `suggested_pitch_body` with 1 specific page reference
- [ ] Anchor text distribution ≤20% in any single category
- [ ] Risk dashboard JSON exists and shows green across velocity / concentration / anchor

## Phased delivery

**Phase 1** (this session, ~45 min):
- Build scraper + filter + scoring logic
- Pull 200-500 raw candidates from free sources
- Output `output/competitor_backlink_targets_v2.csv` with first ~150 ranked targets
- Output `output/backlink_intercept_risk.json` with current state

**Phase 2** (next session, ~60 min):
- Personalize top 50 pitch drafts (scrape each target's recent VoIP content for the specific reference)
- Generate first 5 ready-to-send emails for human review

**Phase 3** (after first pitches sent, weekly):
- Track responses → update `status` column
- Run scraper monthly to refresh candidate list
- Surface top 5 new targets each week

## Constraints / Hard Rules (NEVER violate)

- 🚫 Never publish to or pitch a domain in `BLOCKED_HIGH_SPAM_DOMAINS`
- 🚫 Never exceed concentration cap on any platform (40%, gated in `core/humanize.py::concentration_gate()`)
- 🚫 Never auto-send emails without explicit user "go" command
- 🚫 Never use paid SEO APIs (free tier only)
- 🚫 Never include reciprocity offers in pitches
- 🚫 Always log every action — `output/competitor_backlink_targets_v2.csv` and `output/backlink_intercept_risk.json` must be source-of-truth, hard-verified
- 🚫 Don't burn cycles re-scraping data we already have — cache aggressively
- 🚫 Don't write code that hits real production APIs without first testing with `--dry-run`

## Files you should READ before starting

- `wiki/hot.md` (current state cache)
- `output/backlinks_final_truth.csv` (existing referring domains to exclude)
- `output/outreach_targets.csv` (already-drafted pitches to skip)
- `core/humanize.py` (BLOCKED_HIGH_SPAM_DOMAINS and validation gates)
- `assets/calculator/index.html` (the linkable asset; reference for pitch claims)
- `docs/dialphone_seo_strategy_for_bhavesh.md` (positioning context)

## How to know you're done

End the run with:
1. `output/competitor_backlink_targets_v2.csv` saved
2. `output/backlink_intercept_risk.json` saved
3. Top 5 target domains printed to stdout with their scores + suggested pitches
4. A summary section: "X targets found, Y with personalized pitches, Z duplicates filtered, A on the priority list ready for human review"
5. Commit with message: `Add competitor backlink intercept tool + initial target pool (N candidates)`

---

## My ask back when running this

Once execution finishes, I want a 1-page report covering:

1. How many targets found at each DA tier (50-60 / 60-70 / 70-80 / 80+)
2. Top 5 highest-ROI targets with full scoring breakdown
3. Any drawback/mitigation that came up unexpectedly
4. The 1 thing I should know before sending the first 5 pitches
5. Estimated time-to-first-backlink-landed (be honest about timeline)
