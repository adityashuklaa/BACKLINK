# Agent Teams — Master Reference Guide

> Source: https://code.claude.com/docs/en/agent-teams
> Last verified: 2026-04-07
> Status: Experimental feature

---

## Quick-Start Checklist

1. Verify Claude Code >= v2.1.32: `claude --version`
2. Enable the feature in `~/.claude/settings.json` (see [Enable](#enable-agent-teams))
3. Start with a research or review task (low risk, high parallel value)
4. Use 3–5 teammates, 5–6 tasks per teammate
5. Clean up when done: tell the lead `Clean up the team`

---

## Enable Agent Teams

Add to `~/.claude/settings.json`:

```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

Or set in your shell environment: `export CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`

---

## Architecture

```
YOU
 │
 ▼
TEAM LEAD (your main Claude Code session)
 │  creates/assigns tasks, spawns teammates, synthesizes results
 │
 ├── Shared Task List  ──────────────────────┐
 │    (pending → in-progress → completed)    │
 │    file-locked claims, auto-unblocks      │
 │                                           │
 ├── Mailbox (inter-agent messaging)         │
 │                                           │
 ├── TEAMMATE A ─────────────────────────────┤
 │    own context window, reads task list    │
 │    messages other teammates directly      │
 │                                           │
 ├── TEAMMATE B ─────────────────────────────┤
 │                                           │
 └── TEAMMATE C ─────────────────────────────┘
```

| Component   | Role |
|-------------|------|
| Team lead   | Main session — creates team, spawns teammates, coordinates |
| Teammates   | Separate Claude instances — independent context windows |
| Task list   | Shared work items with states: pending / in-progress / completed |
| Mailbox     | Direct messaging between any agents |

**Storage locations:**
- Team config: `~/.claude/teams/{team-name}/config.json` (auto-managed, do not hand-edit)
- Task list: `~/.claude/tasks/{team-name}/`

---

## Agent Teams vs. Subagents

| Dimension | Subagents | Agent Teams |
|-----------|-----------|-------------|
| Context | Own window; results return to caller | Own window; fully independent |
| Communication | Report to main agent only | Teammates message each other directly |
| Coordination | Main agent manages all | Shared task list + self-coordination |
| Best for | Focused tasks where only result matters | Complex work needing discussion/debate |
| Token cost | Lower (results summarized back) | Higher (each teammate = full instance) |

**Rule of thumb:** Use subagents for sequential or isolated work. Use agent teams when teammates need to share findings, challenge each other, and self-coordinate.

---

## When to Use Agent Teams

### Strong Use Cases
- **Parallel research/review** — multiple teammates investigate different facets simultaneously
- **New independent modules** — each teammate owns a separate file set with no overlap
- **Competing hypothesis debugging** — teammates test different root-cause theories in parallel
- **Cross-layer changes** — frontend/backend/tests owned by different teammates

### Weak Use Cases (use single session or subagents instead)
- Sequential tasks
- Same-file edits (conflict risk)
- Work with many inter-dependencies
- Routine/simple tasks (coordination overhead not worth it)

---

## Display Modes

| Mode | Description | Requirement |
|------|-------------|-------------|
| `auto` (default) | Split panes if inside tmux, else in-process | — |
| `in-process` | All teammates in your main terminal; Shift+Down to cycle | Any terminal |
| `tmux` | Each teammate in its own pane | tmux or iTerm2 + `it2` CLI |

Set globally in `~/.claude.json`:
```json
{ "teammateMode": "in-process" }
```

Or per-session:
```bash
claude --teammate-mode in-process
```

**Note:** Split-pane mode does NOT work in VS Code integrated terminal, Windows Terminal, or Ghostty.

### tmux / iTerm2 Setup
- **tmux**: install via package manager; entry point `tmux -CC` in iTerm2 recommended
- **iTerm2**: install [`it2` CLI](https://github.com/mkusaka/it2), enable Python API in iTerm2 → Settings → General → Magic

---

## Key Controls (In-Process Mode)

| Action | Control |
|--------|---------|
| Cycle through teammates | Shift+Down (wraps after last back to lead) |
| Message current teammate | Just type after cycling to them |
| View a teammate's session | Press Enter |
| Interrupt a teammate's turn | Escape |
| Toggle task list | Ctrl+T |

---

## Prompting Patterns

### Create a Team (natural language)
```
Create an agent team to [task]. Spawn [N] teammates:
- Teammate 1 focused on [role/angle]
- Teammate 2 focused on [role/angle]
- Teammate 3 focused on [role/angle]
```

### Specify Model
```
Create a team with 4 teammates to refactor these modules in parallel.
Use Sonnet for each teammate.
```

### Require Plan Approval Before Implementation
```
Spawn an architect teammate to refactor the authentication module.
Require plan approval before they make any changes.
```
Flow: teammate plans → sends approval request to lead → lead approves or rejects with feedback → on approval, teammate implements.

### Assign Tasks Explicitly
```
Assign the API integration task to the backend teammate.
```

### Talk to a Specific Teammate
Cycle with Shift+Down until you reach them, then type your message.

### Prevent Lead from Working Ahead of Teammates
```
Wait for your teammates to complete their tasks before proceeding.
```

### Shutdown a Teammate Gracefully
```
Ask the researcher teammate to shut down.
```

### Clean Up the Entire Team
```
Clean up the team.
```
Always clean up via the lead. Teammates should NOT run cleanup (their context may not resolve correctly).

---

## Using Subagent Definitions as Teammates

Define a reusable agent type (e.g., `security-reviewer`) in any subagent scope (project / user / plugin / CLI), then reference it by name:

```
Spawn a teammate using the security-reviewer agent type to audit the auth module.
```

**What carries over from the definition:**
- `tools` allowlist
- `model`
- Definition body appended to system prompt

**What does NOT carry over:**
- `skills` frontmatter
- `mcpServers` frontmatter (loaded from project/user settings instead)

Team coordination tools (`SendMessage`, task tools) are always available even when `tools` is restricted.

---

## Permissions

- Teammates inherit the lead's permission settings at spawn time.
- If lead uses `--dangerously-skip-permissions`, all teammates do too.
- Per-teammate modes can be changed after spawning, not at spawn time.

---

## Context & Communication Rules

- Teammates load: CLAUDE.md, MCP servers, skills from project — same as a regular session.
- Teammates do NOT inherit the lead's conversation history.
- Spawn prompt is the primary way to give a teammate task-specific context.
- Messages are delivered automatically (no polling needed).
- Idle teammates automatically notify the lead.

### Messaging Types
| Type | Use |
|------|-----|
| `message` | Send to one specific teammate |
| `broadcast` | Send to all teammates simultaneously (use sparingly — costs scale with team size) |

---

## Hooks for Quality Gates

| Hook | Trigger | Exit 2 behavior |
|------|---------|-----------------|
| `TeammateIdle` | Teammate about to go idle | Send feedback, keep teammate working |
| `TaskCreated` | Task being created | Prevent creation, send feedback |
| `TaskCompleted` | Task being marked complete | Prevent completion, send feedback |

---

## Best Practices

### Team Size
- **Start with 3–5 teammates** for most workflows
- 5–6 tasks per teammate keeps everyone productive without excessive context switching
- Token cost scales linearly — each teammate = separate Claude instance
- More teammates ≠ faster results after a point; coordination overhead grows

### Task Sizing
- **Too small**: coordination overhead > benefit
- **Too large**: long stretches without check-ins, risk of wasted effort
- **Just right**: self-contained units with a clear deliverable (a function, a test file, a review)

### Context
Include all task-specific details in the spawn prompt since teammates don't have the lead's history:
```
Spawn a security reviewer teammate with the prompt: "Review src/auth/ for 
security vulnerabilities. Focus on token handling, session management, and 
input validation. The app uses JWT tokens in httpOnly cookies. Report issues 
with severity ratings."
```

### File Conflicts
Each teammate should own a **non-overlapping set of files**. Two teammates editing the same file leads to overwrites.

### Monitoring
- Check in on teammates regularly
- Redirect approaches that aren't working
- Synthesize findings as they come in
- Don't let the team run unattended for too long

### Starting Out
Begin with **research and review tasks** (no code writes) to learn coordination patterns before moving to parallel implementation.

---

## Use Case Examples

### Parallel Code Review
```
Create an agent team to review PR #142. Spawn three reviewers:
- One focused on security implications
- One checking performance impact
- One validating test coverage
Have them each review and report findings.
```

### Competing Hypothesis Debugging
```
Users report the app exits after one message instead of staying connected.
Spawn 5 agent teammates to investigate different hypotheses. Have them talk 
to each other to try to disprove each other's theories, like a scientific 
debate. Update the findings doc with whatever consensus emerges.
```

### Multi-Angle Design Exploration
```
I'm designing a CLI tool that helps developers track TODO comments across 
their codebase. Create an agent team to explore this from different angles: 
one teammate on UX, one on technical architecture, one playing devil's advocate.
```

---

## Limitations (Experimental)

| Limitation | Workaround |
|------------|------------|
| No session resumption for in-process teammates | After `/resume`, spawn new teammates |
| Task status can lag (teammate forgets to mark done) | Manually update or tell lead to nudge the teammate |
| Slow shutdown (finishes current request first) | Expected behavior; wait it out |
| One team per session (lead) | Clean up before starting a new team |
| No nested teams (teammates can't spawn sub-teams) | Break work so only lead spawns |
| Lead is fixed for team lifetime | Can't promote a teammate to lead |
| Permissions set at spawn, not per-teammate beforehand | Change individual modes after spawn |
| Split panes not supported in VS Code/Windows Terminal/Ghostty | Use in-process mode |

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Teammates not appearing | In-process: press Shift+Down. Check task complexity. Verify tmux in PATH: `which tmux` |
| Too many permission prompts | Pre-approve common operations in permission settings before spawning |
| Teammate stops on error | Shift+Down to view output, give direct instructions or spawn a replacement |
| Lead shuts down early | Tell it: "Keep going, wait for teammates to finish" |
| Orphaned tmux session | `tmux ls` then `tmux kill-session -t <session-name>` |

---

## Token Cost Guidance

- Each teammate = full independent Claude instance with its own context window
- Costs scale linearly with number of active teammates
- Research, review, and new feature work: extra tokens usually worthwhile
- Routine or sequential tasks: single session is more cost-effective
- Broadcast messages are expensive — use targeted messages when possible

---

## Related Features

| Feature | When to Use |
|---------|-------------|
| [Subagents](/en/sub-agents) | Lightweight delegation within one session; no inter-agent coordination needed |
| [Git Worktrees](/en/common-workflows#run-parallel-claude-code-sessions-with-git-worktrees) | Manual parallel sessions without automated team coordination |
| Agent Teams | Complex parallel work where agents need to communicate and self-coordinate |
