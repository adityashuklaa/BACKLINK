---
type: index
last_updated: 2026-04-18
---

# Wiki Index — DialPhone Backlink Project

Master catalog of all wiki pages. Maintained by Claude via the `/wiki` skill.

## Entities
*(people, companies, accounts involved in the project)*

- [[wiki/entities/dialphone|DialPhone Limited]] — the target company
- [[wiki/entities/bhavesh|Bhavesh Shukla]] — the user / persona for all profiles
- (add entities as they become canonical: Andrea, the senior, etc.)

## Concepts
*(ideas, strategies, mental models used in the project)*

- [[wiki/concepts/spam_score|Spam score]] — 0-100 per domain, Penguin-era quality metric
- [[wiki/concepts/karpathy_llm_wiki|Karpathy LLM Wiki pattern]] — compilation over retrieval
- [[wiki/concepts/humanize_gate|Humanize gate]] — pre-publish AI-smell rejection
- [[wiki/concepts/source_quality_gate|Source quality gate]] — pre-publish domain rejection
- (add concepts as they become load-bearing)

## Sources
*(raw inputs: audits, research, reports referenced repeatedly)*

- [[wiki/sources/backlink_seo_audit|Backlink SEO audit]] — at `reports/backlink_seo_audit.md`
- [[wiki/sources/root_cause_spam|Root cause analysis]] — at `reports/root_cause_spam.md`
- [[wiki/sources/double_down_plan|Double-down plan]] — at `reports/double_down_plan.md`

## Meta
*(wiki about the wiki — structure docs, plugin docs)*

- [[wiki/meta/plugin_set|Plugin set]] — which Claude Code plugins this project requires
- [[wiki/meta/hot_cache|Hot cache]] — how `hot.md` works, update cadence

## Quick search

- `tag:backlink` — all backlink-related pages
- `tag:platform` — per-platform analysis (dev.to, quora, etc.)
- `tag:campaign` — campaign-state pages (daily snapshots etc.)

## When to read what

- **Start of session**: auto-loaded `hot.md` gives you recent context
- **Re-orient after compact**: hot.md is re-read via PostCompact hook
- **Deep dive on a topic**: open the relevant `wiki/concepts/` or `wiki/sources/` page
- **"What's the history of X"**: `git log wiki/ --grep X` — wiki is auto-committed on every Write/Edit
