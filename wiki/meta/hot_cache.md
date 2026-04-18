---
type: meta
tags: [meta, memory]
---

# Hot Cache — How `wiki/hot.md` Works

## Purpose

`wiki/hot.md` is the **recent-context cache**. A fresh Claude session reads this FIRST before touching the full wiki index. It replaces the 2000-word "let me remind you what we've been doing" re-brief that otherwise burns context.

## Lifecycle

1. **Session start** — hook in `.claude/settings.local.json` reads `wiki/hot.md` and silently injects into context.
2. **During session** — Claude works against project code. Wiki pages get updated if facts change.
3. **Post-compact** — if the conversation hit auto-compaction, the `PostCompact` hook re-reads `hot.md` to restore context.
4. **Session stop** — `Stop` hook checks if wiki files changed. If yes, Claude is prompted to update `hot.md` before ending.

## Format rules

- **Under 500 words.** This is the single most-important rule. Longer = burns context for every session.
- **Overwrite, don't append.** It's a cache, not a journal. Use `log.md` for history.
- **Structure:**
  - Frontmatter (`type: cache`, `last_updated: YYYY-MM-DD`)
  - `## Project` — one-line identity: dir, target, user
  - `## Key Recent Facts` — 5-10 bullets on current state
  - `## Recent Changes` — what just shipped
  - `## Active Threads` — what's in flight / blocked
  - `## Key Files` — for fast relocation after context loss

## What belongs in hot.md

- Counts that change frequently (backlink totals, active integrations)
- Blockers waiting on the user
- Recently-decided strategy shifts
- File paths that a future session will need quickly

## What does NOT belong

- Historical decisions (put in `log.md` or a concept page)
- Background (put in concept or entity pages)
- Raw data (put in `.raw/`)
- Anything that hasn't changed in weeks — move it to a concept page and link

## Editing cadence

- **Update whenever a headline metric changes** (backlink count, domain count, blocker status)
- **Full rewrite at end of session** if anything substantive shifted
- **Review weekly** to prune stale info
