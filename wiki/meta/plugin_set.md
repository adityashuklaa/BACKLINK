---
type: meta
tags: [meta, plugins]
---

# Plugin Set — Required for This Project

Any Claude Code session on this project **must** follow this plugin set. Future Claude: if any of these aren't loaded, fix it before starting substantive work.

## Required plugins

### 1. claude-obsidian (memory system)
- **Repo:** https://github.com/AgriciDaniel/claude-obsidian
- **Why:** persistent memory across sessions via the Karpathy LLM Wiki pattern. Without this, every session re-learns the project from scratch.
- **Location of clone:** `~/.claude/plugins/manual/claude-obsidian/`
- **Skills mounted:** `.claude/skills/{wiki,wiki-ingest,wiki-query,wiki-lint,autoresearch,canvas,save,obsidian-markdown,obsidian-bases,defuddle}`
- **Commands mounted:** `.claude/commands/{wiki.md,save.md,autoresearch.md,canvas.md}`
- **Hooks wired in `.claude/settings.local.json`:** SessionStart, PostCompact, PostToolUse, Stop

### 2. caveman (token reduction)
- **Repo:** https://github.com/JuliusBrussee/caveman
- **Why:** available for when the user wants terse output. Not force-activated.
- **Location of clone:** `~/.claude/plugins/manual/caveman/`
- **Skills mounted:** `.claude/skills/{caveman.md,caveman-compress.md}`
- **Activation:** default `off` — user must explicitly invoke if they want it on
- **Env var:** `CAVEMAN_PLUGIN_ROOT` points to the clone

## Reinstallation (if the plugins go missing)

```bash
mkdir -p "$HOME/.claude/plugins/manual"
cd "$HOME/.claude/plugins/manual"
git clone --depth 1 https://github.com/AgriciDaniel/claude-obsidian.git
git clone --depth 1 https://github.com/JuliusBrussee/caveman.git

# From the project root:
cd /c/Users/Dev/Desktop/backlink
cp -r "$HOME/.claude/plugins/manual/claude-obsidian/skills/"* .claude/skills/
cp -r "$HOME/.claude/plugins/manual/claude-obsidian/commands/"* .claude/commands/
cp "$HOME/.claude/plugins/manual/caveman/caveman/SKILL.md" .claude/skills/caveman.md
cp "$HOME/.claude/plugins/manual/caveman/caveman-compress/SKILL.md" .claude/skills/caveman-compress.md
```

## Why plugin CLI install doesn't work here

The `claude plugin install` CLI forces SSH clone of the marketplace repos, which fails on Windows without a configured SSH key. Manual HTTPS clone + file copy is the reliable path. Metadata is still registered in `~/.claude/settings.json` via the `claude plugin marketplace add` step, which does work (it uses HTTPS).

## Not using (deliberate exclusion)

- **cavekit** (natural-language-to-blueprint tool) — out of scope, this is an SEO/backlink project not a software build
- **Other Obsidian AI plugins** (Cortex, Claudian) — they run INSIDE Obsidian; we run Claude Code from terminal + dashboard, different architecture
- **obsidian-mind** — another persistent-memory plugin, largely duplicates claude-obsidian
