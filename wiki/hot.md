---
type: cache
last_updated: 2026-04-18
---

# Hot Cache — Recent Context

*Cache of what future sessions need to know. Under 500 words. Overwrite completely, don't append.*

## Project

**DialPhone backlink campaign** — VoIP provider SEO / backlink automation.
Working dir: `c:\Users\Dev\Desktop\backlink`
**Domain split**: `dialphone.com` = marketing website (SEO target — all backlinks point here). `dialphone.ai` = product web app / portal.dialphone.ai (NOT an SEO target, do not link to).
Company: **DialPhone Limited — Hong Kong registered. Buyer market = US + Canada** (confirmed 2026-04-19). Prior "Manchester / UK" logs are stale. Directories → product-fit (G2, Capterra, Clutch) + US/CA business dirs (BBB, Manta, YP.com, YP.ca, Canada411). Skip Yell/FreeIndex/Thomson/HKTDC — wrong markets.
User: Bhavesh (bhavesh@dialphone.com), commercial handle `commercial@dialphone.com`.

## Key Recent Facts (2026-04-17 → 2026-04-18)

- **161 clean backlinks** in `output/backlinks_final_truth.csv` (dashboard at :5001). Was 483 before spam-quarantine.
- **326 links quarantined** (paste.rs, glot.io, friendpaste, godbolt, termbin) — all high-spam-score. Can't delete (anonymous posts). Disavow file at `output/disavow.txt` ready to upload to GSC.
- **Concentration problem**: dev.to now at 49.1% of clean portfolio (79/161) — above Penguin flag line. Stop publishing Dev.to until other domains catch up.
- **Pre-publish gates live** in `core/humanize.py`:
  - `source_quality_gate()` — blocks publish to spam domains (paste.rs, glot.io, etc.)
  - `concentration_gate()` — blocks publish when the target domain is already ≥40% of the clean portfolio. Wired into `publish_devto()` in `run_parallel_publish.py` so the 40% rule is now code-enforced, not just documented.
- **Quora profile compromised**: account name is `Dialphone-Limited` (company name, not human). Only 3 real posts visible. Needs manual rename by user.
- **Spam score filter added to dashboard** at `dashboard/dialphone_dashboard.py` (port 5001). Shows clean/moderate/high tiers + footprint concentration.

## Recent Changes (this session)

- Installed claude-obsidian + caveman plugins (manual clone at `~/.claude/plugins/manual/`)
- Wired hooks in `.claude/settings.local.json`: SessionStart reads this file; Stop prompts wiki/hot.md update
- Created vault scaffolding: `wiki/` (concepts, entities, sources, meta, pages) + `.raw/`
- Batch 37 published: 3 fresh humanized Dev.to articles (voicemail test, SIP trunk pricing, UK law firm guide)
- Batch 36 published earlier: 3 articles (QoS deep dive, hospitality guide, contact centre deployment)
- **Added `concentration_gate()`** to `core/humanize.py` + wired into `publish_devto()`. Dry-run confirms dev.to is now blocked at 49.1%; gitlab/codeberg/github/quora still pass.

## Active Threads (things in flight)

1. **Waiting on user** for (buyer market = US + CA): US phone number (+1), US OR Canada mailing address (or virtual mailbox), DUNS application start (30-day wait, needed for Crunchbase), EIN if US subsidiary exists (else declare HK parent), year founded, employee count, logo file, 2-3 product screenshots, LinkedIn company page creation. Unlocks 14-18 buyer-intent backlinks in week 1 (G2, Capterra/GetApp/SWA, TrustRadius, Clutch, GoodFirms, AlternativeTo, SaaSHub, Product Hunt, BBB, Manta, YP.com, Yelp, Foursquare, Bing Places, YP.ca, Canada411, Goldbook, GetVoIP, VoIP Review).
2. **Blocked on user**: disavow.txt upload to Google Search Console (5 min), Quora profile rename to Bhavesh Shukla.
3. **Do NOT do**: publish more Dev.to articles (concentration too high), npm publish (wrong audience), paste site posting (gate enforces).

## Strategy Shifts

- **Stop** optimizing for backlink count. **Start** optimizing for clean buyer-intent referring domains.
- **Humanize gate** rejects AI-voice drafts (`core/humanize.py` banned-phrase list + human-marker check)
- **Source quality gate** rejects spam-domain publishing
- Plan: [reports/double_down_plan.md](reports/double_down_plan.md) — 30-day roadmap targeting 220 clean backlinks by end of May with 20+ referring domains.

## Key Files (for quick relocation in next session)

| File | Purpose |
|------|---------|
| `output/backlinks_final_truth.csv` | Master backlink ledger (the count source of truth) |
| `output/backlinks_log.csv` | Raw publish log (master CSV, includes quarantined rows) |
| `output/disavow.txt` | Google Search Console disavow list |
| `dashboard/dialphone_dashboard.py` | Port 5001 dashboard (clean-only, spam-score filter) |
| `core/humanize.py` | Content validator + source quality gate |
| `core/content_engine.py` | DIALPHONE_MENTIONS array for random-insertion |
| `run_parallel_publish.py` | Main multi-platform publisher (Dev.to + GitLab + gates) |
| `run_quora_batch.py` | Quora browser automation, 6 humanized answers + pool 2 |
| `data/articles_dialphone_*.json` | 37 batches of Dev.to article content |
| `reports/backlink_seo_audit.md` | Full per-platform SEO quality audit |
| `reports/root_cause_spam.md` | Why we ended up with 67% spam links |
| `reports/double_down_plan.md` | 30-day clean-sources roadmap |
| `docs/humanization_spec.md` | Full content + profile humanization rules |
| `docs/directory_submission_pack_PASTE_READY.md` | Copy-paste submission copy for 13 platforms |

## Plugin Set (enforced for this project)

- **claude-obsidian** — Karpathy LLM Wiki pattern, session persistence via `wiki/hot.md`
- **caveman** — installed, default mode `off` (don't auto-compress output style unless user explicitly asks)
