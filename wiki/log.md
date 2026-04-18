---
type: log
---

# Operation Log

Append-only. One entry per significant wiki operation. Newest on top.

## 2026-04-18 22:30 — Wiki bootstrapped

Set up the Karpathy LLM Wiki pattern for this project using `claude-obsidian`.
- Scaffolding: `wiki/{concepts,entities,sources,meta,pages}`, `.raw/`, `_templates/`
- Hooks: SessionStart reads `hot.md`, Stop prompts to update it, PostToolUse auto-commits wiki changes
- Hot cache seeded with full 2026-04-17/18 session state (161 clean backlinks, spam quarantine, concentration problem, waiting-on-user list)
- Index initialized with stub pages (to be filled as needed)

Rationale: prior sessions lost context at compaction. Karpathy LLM Wiki pattern (plain markdown, compile-on-write, read-on-read) eliminates the need to re-explain state.
