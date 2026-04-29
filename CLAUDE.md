# CLAUDE.md — DialPhone Backlink Project

This project uses the **Karpathy LLM Wiki pattern** for persistent memory plus the **claude-obsidian** and **caveman** plugins. Any Claude Code session working on this repo must follow the rules below.

---

## 1. Memory system (READ THIS FIRST every session)

### At session start
1. Read `wiki/hot.md` — this is the **recent context cache**. It tells you what the prior session(s) accomplished and what's in flight.
2. If a question touches deep context, also read the relevant `wiki/concepts/*.md` or `wiki/sources/*.md` page.
3. Don't ask the user to re-explain state that's in the wiki. Read it.

### During session
- When you learn a fact that will matter in future sessions, add/update the corresponding `wiki/` page. Use `Write` or `Edit` — the PostToolUse hook auto-commits.
- When a metric or strategy changes, update `wiki/hot.md` to reflect it.

### At session end
- If the `Stop` hook emits `WIKI_CHANGED:`, update `wiki/hot.md` with a fresh under-500-word summary before the next session starts.

### File layout
```
wiki/
├── hot.md              # recent-context cache (under 500w, overwrite-don't-append)
├── index.md            # master catalog of wiki pages
├── log.md              # append-only operation log
├── concepts/           # ideas, mental models
├── entities/           # people, companies, accounts
├── sources/            # audits, research, reports
├── meta/               # docs about the wiki itself
└── pages/              # default bucket
.raw/                   # immutable raw source material (don't edit)
```

---

## 2. Required plugins

See [wiki/meta/plugin_set.md](wiki/meta/plugin_set.md) for full setup + reinstall commands.

- **claude-obsidian** (vault-based memory) — MUST be available. Skills at `.claude/skills/wiki*`, commands at `.claude/commands/{wiki,save,autoresearch,canvas}.md`, hooks in `.claude/settings.local.json`.
- **caveman** (token-compression, OPTIONAL) — available but default-off. User explicitly toggles.

If the plugins ever go missing, follow the reinstall commands in `wiki/meta/plugin_set.md`.

---

## 3. Project context (short)

**What this is:** SEO / backlink automation for **dialphone.com** (VoIP provider, DialPhone Limited — Hong Kong registered). **Buyer market: US + Canada.** No UK targeting. Directory strategy: product-fit (G2, Capterra, Clutch) + US/CA business dirs (BBB, Manta, YP.com, YP.ca, Canada411). Content vocab: $, LLC/Inc, EIN/BN, +1 phone format, US/CA geography examples.
**Target:** grow clean buyer-intent backlinks, not volume.
**User / operator:** identity TBD — do not reference "Bhavesh" or `bhavesh@dialphone.com` (both explicitly rejected). Company handle: `commercial@dialphone.com`.

**Current state (as of 2026-04-18, refresh from `wiki/hot.md` for latest):**
- 161 clean backlinks across 6 domains
- 326 high-spam-score backlinks quarantined (can't delete — disavow.txt generated)
- Dev.to over-concentrated at 49% → stop publishing until other domains catch up
- Pre-publish spam gate live in `core/humanize.py::source_quality_gate()`

---

## 4. Hard rules (enforce always)

### Content quality
- **Humanize gate** — every Dev.to draft must pass `core/humanize.py::validate(text, "devto")`. No banned AI-tell phrases. At least 2 human markers (timestamps, hedges, specific numbers).
- **Source quality gate** — never publish to a domain listed in `BLOCKED_HIGH_SPAM_DOMAINS` in `core/humanize.py`. Never add one back.

### Concentration
- No single domain may exceed 40% of the clean portfolio (currently dev.to at 49% — the top offender, do not feed it).
- Before publishing, check `output/backlinks_final_truth.csv` for concentration.

### Data integrity
- Only count links as "real" if they're in `output/backlinks_final_truth.csv` with `status=success`.
- Never inflate counts by counting quarantined or word-only links.
- Dashboard source of truth: `dashboard/dialphone_dashboard.py` on port 5001.

### Execution
- Don't burn time on channels already flagged dead (Bitbucket, Hashnode, paste sites — see [reports/backlink_seo_audit.md](reports/backlink_seo_audit.md)).
- Do measure before expanding — no new platform without an indexation check after 24h.

### Velocity & detection safety (added 2026-04-29)
- **Every batch publish must call `core.safety.pre_publish_check(platform, content)` before each individual publish.** Wired into `tools/gen_and_push.py`, `tools/gen_and_push_devto.py`, `tools/publish_hashnode_batch.py`. Future publishing scripts MUST do the same.
- Cap reference (per-platform 24h / 7d / 30d), tightest first: Hashnode `1/4/15`, Codeberg-orgs `1/3/8`, Codeberg.page `1/3/8`, Tumblr/Medium/Substack `1/5/15`, IndieHackers `1/3/8`, GitLab/GitHub `3/18/60`, Stack Overflow/Quora `3/12/35`, Dev.to `5/25/80`, Codeberg repos `5/30/100`, Diigo `5/25/60`.
- Use `python tools/safety_status.py` before running any batch — see what's BLOCKED.
- Sundays = rest day by default. Override with `--ignore-rest-day` only when justified.
- Use jitter, not fixed sleep — `safety.jitter_sleep(35)` instead of `time.sleep(35)`.
- **Never use `--ignore-velocity-cap` without explicit leadership justification logged in `wiki/log.md`.**
- Full plan + per-incident response: [docs/safety_and_cooldown_plan.md](docs/safety_and_cooldown_plan.md).

---

## 5. Available slash commands (from plugins)

- `/wiki` — interact with the wiki (search, summarize, rebuild)
- `/save` — save a note from the current conversation into the wiki
- `/autoresearch` — automated research pipeline with wiki citations
- `/canvas` — open the wiki canvas / graph view

---

## 6. Common files (fast index)

| File | Purpose |
|------|---------|
| `output/backlinks_final_truth.csv` | Source-of-truth backlink ledger |
| `output/backlinks_log.csv` | Raw publish log (includes quarantined) |
| `output/disavow.txt` | For Google Search Console upload |
| `dashboard/dialphone_dashboard.py` | Live dashboard on :5001 |
| `core/humanize.py` | Content validator + source gate |
| `run_parallel_publish.py` | Multi-platform publisher |
| `run_quora_batch.py` | Quora browser automation |
| `run_quality_only.py` | Dev.to-only quality publisher (skips paste sites) |
| `reports/backlink_seo_audit.md` | Per-platform SEO quality audit |
| `reports/root_cause_spam.md` | Why we ended up 67% spam |
| `reports/double_down_plan.md` | 30-day clean-sources roadmap |
| `docs/humanization_spec.md` | Full content + profile rules |
| `docs/directory_submission_pack_PASTE_READY.md` | Copy-paste directory submissions |

---

## 7. When in doubt

1. Check `wiki/hot.md` first.
2. Check `wiki/index.md` for pointers.
3. Check the relevant `reports/*.md` file.
4. Then ask.
