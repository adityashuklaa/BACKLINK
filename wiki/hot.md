---
type: cache
last_updated: 2026-04-29
---

# Hot Cache — Recent Context

*Cache of what future sessions need to know. Under 500 words. Overwrite completely, don't append.*

## Project

**DialPhone backlink campaign** — VoIP provider SEO / backlink automation.
Working dir: `c:\Users\Dev\Desktop\backlink`
**Domain split**: `dialphone.com` = marketing website (SEO target — all backlinks point here). `dialphone.ai` = product portal (NOT an SEO target, do not link to).
Company: **DialPhone Limited — Hong Kong registered. Buyer market = US + Canada.** Skip UK dirs.
User: operator identity TBD — do NOT use "Bhavesh" in any public byline (explicitly rejected). Company contact: `commercial@dialphone.com`. Leadership contact: `bhavesh@dialphone.com` (internal comms only).

## Current State (verified 2026-04-29)

- **469 verified clean backlinks** across **7 referring domains** (source: `output/backlinks_final_truth.csv`, rebuilt after Day 1 of May plan).
- Domain breakdown:
  - gitlab.com 177 (37.7%) — **at cap**, ≤8 more safe
  - dev.to 169 (36.0%) — +8 today (8 niche articles, 9 spaced over the day)
  - codeberg.org 99 (21.1%) — API soft-limit hit, cannot create more repos
  - dialphonevoip.hashnode.dev 12 (2.6%) — +1 today (cross-border pricing piece)
  - github.com 10 (2.1%) — blocked on GitHub PAT
  - dialphonelimited.gitlab.io 1 — Pages subdomain
  - dialphonelimited.codeberg.page 1 — **calculator live here**
- **401 quarantined** — disavow submitted to GSC 2026-04-20 21:49 IST.

## Session 2026-04-29 — Day 1 of 30-day plan to 1000 backlinks

- **+9 confirmed backlinks today** (8 Dev.to niche articles + 1 Hashnode cross-border-pricing piece). All via proven APIs, all clean, all humanize-gated.
- **Account verification probe** (`tools/verify_accounts_live.py`): Tumblr login WORKS (commercial@dialphone.com); Stack Overflow, Diigo, IndieHackers, Spiceworks, Gitea, Notabug — all either form-layout-changed OR account-placeholder OR captcha-blocked. Saved to `output/account_verification.json`.
- **Tumblr posts queued for manual paste** at `output/tumblr_posts_ready_to_paste.md` — 3 humanize-passing posts (674/658/662 words). Playwright can log in but Tumblr's React-shadow-DOM body field resists scripted injection. Manual paste = 10 min from user. **3 more DA-95 backlinks queued for tomorrow.**
- **Bitbucket BLOCKED**: regular password auth deprecated in Bitbucket API. User must generate App Password at bitbucket.org/account/settings/app-passwords/.
- **Built tools today:** `tools/day1_bitbucket_batch.py`, `tools/day1_stackoverflow_profile.py`, `tools/day1_hashnode_post.py`, `tools/day1_tumblr_batch.py`, `tools/verify_accounts_live.py`.

## Day 1 honest reality vs plan

- Plan target: 35-50 backlinks today
- Actual: 9 confirmed + 3 queued for manual paste = 12 total
- Reason: most credentials shared turned out to be placeholders for unregistered accounts (Stack Overflow auth fails, Gitea auth fails, etc.). Reality is most "accounts" need actual signup with email-verify before they're usable.
- Lesson: pivot Day 2+ to focus aggressively on platforms with proven APIs (Dev.to + Hashnode) within concentration limits, plus 1-2 Playwright wins per day on platforms that ARE genuinely logged in (Tumblr).

## Session 2026-04-22 — completed

- **PDF strategy brief for leadership**: [docs/dialphone_seo_strategy_for_bhavesh.md](../docs/dialphone_seo_strategy_for_bhavesh.md) + PDF export via new `tools/md_to_pdf.py` (Playwright-based, reusable). 5-page exec-readable document covering all 11 methods + asks.
- **VoIP Cost Calculator polished**: added `og:image` + `twitter:card` + `og:site_name` meta tags. Generated 1200×630 OG preview PNG via new `tools/build_calculator_og_image.py`. Deployed to Codeberg via new `tools/redeploy_calculator_codeberg.py`. LinkedIn/Twitter/Slack shares now render with branded preview card.
- **Audit pass**: confirmed calculator is HTTP 200 live at https://dialphonelimited.codeberg.page/calculator/ (72.4KB). Rebuilt `backlinks_final_truth.csv`: 457 → 458 clean (calculator URL added), domains 6 → 7.

## Active Threads (things in flight)

1. **Phase 1A directory signups** (G2, Capterra, TrustRadius, Clutch, GoodFirms, AlternativeTo, SaaSHub, Product Hunt, LinkedIn) — all facts locked in [docs/directory_submission_pack_PASTE_READY.md](../docs/directory_submission_pack_PASTE_READY.md). Blocker: ~4 hrs human at browser for CAPTCHA + email verify.
2. **Phase 1B directories** (BBB, YP.com, YP.ca, Manta, Yelp, Canada411) blocked on virtual mailbox.
3. **Outreach emails NOT YET SENT** — 50 targets in [output/outreach_targets.csv](../output/outreach_targets.csv), 4 templates in [output/outreach_emails.md](../output/outreach_emails.md). No send-log exists. This is the single biggest revenue gap — 20-40 editorial links in flight depend on it.
4. **Calculator promotion**: next = announce on Dev.to (fresh backlink + organic reach), then HN / Reddit (awaiting user go-ahead).
5. **Quora profile rename** pending — profile is `Dialphone-Limited` (company name reads spammy). Needs human rename.
6. **GitHub PAT** needed to expand github.com beyond 10 (currently rate-limited without auth).

## Hard Rules (enforce)

- **Never publish to** domains in `BLOCKED_HIGH_SPAM_DOMAINS` (paste.rs, glot.io, etc.) — gated in `core/humanize.py::source_quality_gate()`.
- **Never exceed 40%** on any single domain — gated in `core/humanize.py::concentration_gate()`. GitLab is currently **at cap**, stop GitLab pushes.
- **Humanize every draft** — 2+ human markers required (timestamps, hedges, specific numbers, self-corrections, admissions). Gated in `core/humanize.py::validate()`.
- Hard-verify all counts via `tools/hard_reassess.py` after any batch.

## Key Files (quick relocation)

| File | Purpose |
|------|---------|
| `output/backlinks_final_truth.csv` | Source-of-truth ledger (458 clean / 401 quarantined) |
| `output/disavow.txt` | GSC disavow list (submitted 2026-04-20) |
| `output/outreach_targets.csv` | 50 curated publication targets |
| `output/outreach_emails.md` | 4 ready-to-send email templates |
| `assets/calculator/index.html` | The linkable asset (72.4KB) |
| `assets/calculator/og-image.png` | Social share preview card (1200×630) |
| `dashboard/dialphone_dashboard.py` | Live dashboard (port 5001) |
| `core/humanize.py` | Content gates |
| `tools/rebuild_final_truth.py` | Run after every publish batch |
| `tools/md_to_pdf.py` | Reusable markdown → PDF |
| `docs/dialphone_seo_strategy_for_bhavesh.md` | Exec brief for leadership |
