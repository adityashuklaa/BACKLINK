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
User: operator identity TBD — do not assume / do not use "Bhavesh" anywhere (explicitly rejected 2026-04-19). Company contact: `commercial@dialphone.com`.

## Key Recent Facts (2026-04-17 → 2026-04-18)

- **267 clean backlinks** across **9 referring domains** in `output/backlinks_final_truth.csv` (rebuilt 2026-04-20 from backlinks_log.csv with correct status-priority logic; old snapshot was stuck at 161).
- **401 quarantined** (was 326 — rebuild caught more godbolt/glot/paste.rs rows). All covered by **disavow uploaded to GSC on 2026-04-20 at 21:49 IST** on https://www.dialphone.com/ property. 5 domain-level + 132 URL-level disavows. Recovery signal expected 4-6 weeks.
- **Concentration problem**: dev.to at 58.1% (155/267) — deeper over-concentration than previously thought (was 49.1%). Hard publish freeze until other domains dilute.
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
- **Added `concentration_gate()`** to `core/humanize.py` + wired into `publish_devto()`. Blocks dev.to at 58.1% (refreshed count); gitlab/codeberg/github/quora/hashnode still pass.
- **Hashnode unlocked as new referring domain** (2026-04-20): 12 articles on dialphonevoip.hashnode.dev audited, 10 pre-existing ones had their dialphone.com link added via `updatePost` GraphQL mutation. All 12 now dofollow-backlinks. Publisher at `tools/publish_hashnode_batch.py`, link-fixer at `tools/fix_hashnode_links.py`.
- **final_truth.csv rebuild**: stale snapshot (161) → fresh rebuild (267) using correct status-priority dedup. Script embedded in inline Python; worth saving as `tools/rebuild_final_truth.py` if re-used.

## Active Threads (things in flight)

1. **Phase 1A READY TO SHIP** — all facts filled in `docs/directory_submission_pack_PASTE_READY.md`:
   - Pricing: Core $20 / Advanced $30 / Ultra $40 / Customer Engagement $55 per user/month (scraped from dialphone.com/pricing-overview/ via Playwright stealth 2026-04-20)
   - Founded 2024, employees 11-50, compliance SOC 2/HIPAA/GDPR/PCI-DSS
   - HQ: Level 7 Suite C World Trust Tower Hong Kong
   - US phone (public): +1 (914) 431-7523
   - LinkedIn company page exists: https://www.linkedin.com/company/dialphone
   - Uptime SLA 99.999% (public claim)
   - Submitter default: Aditya Shukla, Growth Operations
   - **10 Phase 1A dirs ready for human signup**: G2, Capterra trio (Capterra/GetApp/SWA), TrustRadius, Clutch, GoodFirms, AlternativeTo, SaaSHub, Product Hunt, Crunchbase basic, LinkedIn (page exists, connect only). Blocker = human at browser for CAPTCHA + email verification.
   - Logos received as PNG 2026-04-19 (user to save at assets/logos/dialphone_monogram.png + dialphone_horizontal.png)
2. **Phase 1B still blocked** — needs virtual mailbox setup (iPostal1 or Earth Class Mail). Without it: skip BBB, Yelp, YP.com, YP.ca, Canada411, Manta, Foursquare, Bing Places.
3. **Quora profile rename** pending (target persona identity TBD, explicitly NOT "Bhavesh").
4. **Compliance audit status** — senior asserted "ALL" for SOC 2/HIPAA/GDPR/PCI but audit reports may be demanded by G2/Capterra — needs clarification (completed / in-progress / self-assessed per cert).
5. **GSC disavow** ✅ DONE 2026-04-20 at 21:49 IST — 5 domains + 132 URLs submitted on https://www.dialphone.com/ property. Ranking recovery signal expected 4-6 weeks.
6. **Do NOT do**: publish more Dev.to articles (concentration too high), npm publish (wrong audience), paste site posting (gate enforces).
7. **Also** `vestacall.com` property exists in GSC (prior campaign). May also have spam links needing disavow — user to audit separately.

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
