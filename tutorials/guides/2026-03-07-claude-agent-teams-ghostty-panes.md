---
id: 20260307-TU-001
date: 2026-03-07
category: Tutorial
status: complete
content-status: raw
---

# How to Run Claude Code Agent Teams with Visible Split Panes in Ghostty

**Date:** 2026-03-07
**Category:** Tutorial
**Difficulty:** Intermediate
**Time estimate:** ~20 minutes
**Prerequisites:** Claude Code CLI, Ghostty terminal, Anthropic API key

---

## What You'll Build

By the end of this guide, you'll have a multi-agent Claude Code team running in your terminal with each agent visible in its own pane. You'll be able to watch an architect, security reviewer, and test engineer all working simultaneously on your codebase.

```
┌──────────────────────┬──────────────────────┐
│                      │                      │
│  Team Lead           │  Teammate: Architect │
│  (coordinating)      │  (designing)         │
│                      │                      │
├──────────────────────┼──────────────────────┤
│                      │                      │
│  Teammate: Security  │  Teammate: Tests     │
│  (auditing)          │  (writing specs)     │
│                      │                      │
└──────────────────────┴──────────────────────┘
```

There's a catch, though. Ghostty doesn't natively support Claude Code's split-pane mode. This guide covers two approaches and recommends one.

---

## The Situation

Claude Code Agent Teams support three display modes:

| Mode | How Teammates Appear | Terminal Support |
|------|---------------------|-----------------|
| `in-process` | All in one terminal, cycle with `Shift+Down` | Any terminal |
| `tmux` | Each teammate in its own tmux pane | tmux or iTerm2 |
| `auto` | Split panes if inside tmux, in-process otherwise | Any terminal |

Ghostty is explicitly **not supported** for the `tmux` split-pane mode. There's an open feature request ([anthropics/claude-code#24189](https://github.com/anthropics/claude-code/issues/24189)) for Ghostty support, blocked on Ghostty shipping a programmatic IPC API.

But you can still make it work. Two approaches:

```
┌──────────────────────────────────────────────────────┐
│                                                      │
│  Approach A: tmux inside Ghostty (recommended)       │
│  ─────────────────────────────────────────────        │
│  Each agent gets its own visible pane.               │
│  You can watch them all at once.                     │
│  Some known friction (see Troubleshooting).          │
│                                                      │
│  Approach B: In-process + Ghostty native splits      │
│  ─────────────────────────────────────────────        │
│  Agent teams run in one Ghostty pane.                │
│  Use other Ghostty panes for monitoring.             │
│  Cleaner, but you can't see all agents at once.      │
│                                                      │
└──────────────────────────────────────────────────────┘
```

This guide walks through **Approach A** as the primary path (it's what you asked for — watching all agents go), with Approach B as an alternative at the end.

---

## Prerequisites

- **Ghostty** installed
  ```bash
  # Verify:
  ghostty --version
  ```

- **Claude Code** CLI installed and authenticated
  ```bash
  # Verify:
  claude --version
  ```

- **tmux** installed
  ```bash
  # Verify:
  tmux -V

  # If not installed:
  brew install tmux
  ```

  | Part | Meaning |
  |------|---------|
  | `brew` | macOS package manager (Homebrew) |
  | `install` | Download and set up the package |
  | `tmux` | Terminal multiplexer — manages panes/sessions |

- **Anthropic API key** configured (or a Claude Max subscription)

---

## Step 1: Enable Agent Teams

Agent Teams is an experimental feature. You need to explicitly enable it.

Edit `~/.claude/settings.json`:

```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  },
  "teammateMode": "tmux"
}
```

| Key | What It Does |
|-----|-------------|
| `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` | Turns on the agent teams feature |
| `teammateMode` | Controls how teammates are displayed. `"tmux"` gives each agent its own pane |

If the file already has content, merge these keys into the existing JSON. Don't overwrite your other settings.

Verify it took effect:

```bash
claude config list
```

You should see the agent teams env var in the output.

---

## Step 2: Fix Shift+Enter for Ghostty + tmux

When running Claude Code inside tmux inside Ghostty, the `Shift+Enter` key (used for multi-line input) breaks. Fix this now to avoid frustration later.

Add to your Ghostty config at `~/.config/ghostty/config`:

```
keybind = shift+enter=text:\x1b\r
```

Restart Ghostty after saving.

---

## Step 3: Start a tmux Session

Open Ghostty and create a named tmux session:

```bash
tmux new-session -s agents
```

| Part | Meaning |
|------|---------|
| `tmux` | Launch the terminal multiplexer |
| `new-session` | Create a new session |
| `-s agents` | Name it "agents" for easy reference |

Your terminal is now running inside tmux inside Ghostty. You'll notice a green status bar at the bottom — that's tmux.

---

## Step 4: Launch Claude Code

From inside the tmux session:

```bash
claude
```

Claude Code detects the `$TMUX` environment variable automatically. When it spawns agent teammates, it will create tmux panes instead of running everything in-process.

---

## Step 5: Create Your Agent Team

Type a prompt that describes the team you want. Be specific about roles and scope:

```
Create an agent team to review this codebase from three angles:

- Architecture reviewer: evaluate the project structure, dependency graph,
  and separation of concerns. Look for architectural smells.

- Security reviewer: audit for vulnerabilities — injection risks, auth
  bypasses, unsafe data handling, exposed secrets.

- Test coverage analyst: identify untested code paths, missing edge cases,
  and areas where test coverage is thin.

Use Sonnet for each teammate to keep costs down.
```

Claude Code will:
1. Create a team with a shared task list
2. Spawn three teammates, each in its own tmux pane
3. Begin coordinating their work

**What you'll see:** Your Ghostty window splits into multiple tmux panes. The team lead stays in one pane, and each teammate appears in its own pane. All four are visible simultaneously.

```
┌──────────────────────┬──────────────────────┐
│ Team Lead            │ Architecture         │
│                      │ Reviewer             │
│ Coordinating tasks,  │                      │
│ reading messages     │ Exploring files...   │
├──────────────────────┼──────────────────────┤
│ Security             │ Test Coverage        │
│ Reviewer             │ Analyst              │
│                      │                      │
│ Scanning auth...     │ Checking tests...    │
└──────────────────────┴──────────────────────┘
```

---

## Step 6: Navigate Between Agent Panes

tmux navigation uses a **prefix key** (`Ctrl+b` by default) followed by a direction:

| Action | Keys | Notes |
|--------|------|-------|
| Move to pane above | `Ctrl+b`, then `Up` | Press `Ctrl+b`, release, then arrow |
| Move to pane below | `Ctrl+b`, then `Down` | |
| Move to left pane | `Ctrl+b`, then `Left` | |
| Move to right pane | `Ctrl+b`, then `Right` | |
| Zoom a pane (fullscreen) | `Ctrl+b`, then `z` | Press again to unzoom |
| Show pane numbers | `Ctrl+b`, then `q` | Press the number to jump to that pane |
| Scroll in a pane | `Ctrl+b`, then `[` | Use arrow keys to scroll. `q` to exit scroll mode |

**Zoom is your best friend.** When you want to focus on what one agent is doing, `Ctrl+b z` makes that pane fullscreen. Press it again to return to the grid.

---

## Step 7: Interact with Individual Agents

Click into any pane to make it active, then type to interact with that specific agent. You can:

- Ask a teammate to focus on something specific
- Give the lead new instructions
- Tell a teammate to coordinate with another

Example — clicking into the security reviewer's pane:

```
Focus specifically on the authentication middleware.
Check if JWT tokens are validated on every protected route.
```

---

## Step 8: Monitor the Task List

From any pane (typically the lead's), press `Ctrl+T` to toggle the shared task list. This shows all tasks across the team with their status.

You can also monitor the filesystem directly. Open a new tmux pane (`Ctrl+b`, then `"` for a horizontal split) and run:

```bash
watch -n 2 'ls -la ~/.claude/tasks/*/  2>/dev/null'
```

| Part | Meaning |
|------|---------|
| `watch -n 2` | Re-run the command every 2 seconds |
| `ls -la ~/.claude/tasks/*/` | List all task files across all teams |

---

## Step 9: Clean Up

When the team finishes, tell the lead:

```
Clean up the team and summarize the findings.
```

The lead will shut down all teammates and synthesize results.

After Claude Code exits, clean up the tmux session:

```bash
tmux kill-session -t agents
```

| Part | Meaning |
|------|---------|
| `tmux kill-session` | Destroy a tmux session |
| `-t agents` | Target the session named "agents" |

---

## Quick-Launch Alias

Add this to your `~/.zshrc` for a one-command start:

```bash
alias cteam='tmux new-session -s agents -c "$(pwd)" "claude"'
```

| Part | Meaning |
|------|---------|
| `alias cteam=` | Create a shortcut command called `cteam` |
| `tmux new-session` | Create a new tmux session |
| `-s agents` | Name it "agents" |
| `-c "$(pwd)"` | Start in the current directory |
| `"claude"` | Immediately run Claude Code inside it |

Now just type `cteam` in Ghostty to start everything.

Reload your shell after adding:

```bash
source ~/.zshrc
```

---

## Alternative: Approach B — In-Process Mode with Ghostty Native Splits

If the tmux friction isn't worth it (mouse issues, key conflicts), use this cleaner approach. The tradeoff: you can't see all agents at once, but the experience is smoother.

### Setup

Set `teammateMode` to `in-process` in `~/.claude/settings.json`:

```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  },
  "teammateMode": "in-process"
}
```

### Workflow

1. Open Ghostty
2. Split into your monitoring layout using native Ghostty shortcuts:

   | Action | Keys |
   |--------|------|
   | Split right | `Cmd+D` |
   | Split down | `Cmd+Shift+D` |
   | Navigate between splits | `Cmd+Option+Arrow` |
   | Zoom current split | `Cmd+Shift+Enter` |
   | Equalize splits | `Cmd+Ctrl+=` |

3. In your main pane, run `claude` and create an agent team
4. Use `Shift+Down` to cycle through teammates within the Claude Code session
5. Use other Ghostty panes for monitoring:

```
┌──────────────────────────┬──────────────────────┐
│                          │                      │
│  Claude Code             │  Monitoring          │
│  (agent team running)    │                      │
│                          │  watch -n 2 'ls -la  │
│  Shift+Down to cycle     │  ~/.claude/tasks/*/' │
│  through teammates       │                      │
│                          │  or: git log --watch │
│  Shift+Up to go back     │  or: tail -f logs    │
│                          │                      │
└──────────────────────────┴──────────────────────┘
```

This avoids all tmux-related bugs while keeping agent teams functional.

---

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| `Shift+Enter` doesn't work in tmux | Ghostty's native support doesn't account for the tmux layer | Add `keybind = shift+enter=text:\x1b\r` to Ghostty config |
| Mouse selection is erratic across panes | Claude Code's terminal escape sequences affect Ghostty's mouse handling | Use keyboard-based copy (`Ctrl+b [` to enter scroll mode, select with keys) |
| `Ctrl+k` / `Ctrl+j` don't navigate tmux panes | Keybinding conflict between Ghostty and tmux | Use `Ctrl+b Arrow` instead, or rebind tmux prefix to `Ctrl+a` |
| Teammates don't spawn in separate panes | `$TMUX` not detected — you launched Claude Code outside tmux | Exit Claude Code, start a tmux session first, then re-launch |
| Visual artifacts when switching panes | Background opacity + tmux redraw issue | Set `background-opacity = 1` in Ghostty config, or ignore |
| Pane layout gets corrupted on spawn | Race condition when multiple teammates spawn simultaneously | Wait for team creation to settle, then `Ctrl+b Space` to cycle layouts |
| Agent team doesn't activate | Feature not enabled | Verify `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` in settings.json or env |
| Orphaned tmux sessions after crash | Teammates didn't shut down cleanly | `tmux ls` to find them, `tmux kill-session -t <name>` to clean up |

---

## Cost Awareness

Agent teams burn tokens significantly faster than single sessions:

| Setup | Relative Token Cost |
|-------|-------------------|
| Single Claude Code session | 1x |
| 3-teammate agent team | ~3-4x |
| 5-teammate agent team | ~5-7x |

**Tips to manage cost:**
- Use **Sonnet** for teammates, reserve **Opus** for the team lead
- Start with 2-3 focused teammates, not 5 scattered ones
- Use agent teams for tasks that genuinely benefit from parallelism (reviews, multi-module features, debugging)
- For independent, non-coordinating tasks, regular subagents (`Task` tool) are cheaper

---

## What's Next

- **Ghostty native support is coming.** The blocker is Ghostty's programmatic IPC API, actively under development. Once it ships, Claude Code will likely add Ghostty as a native `teammateMode` backend, eliminating the need for tmux entirely.
- **cmux** is a Ghostty-based terminal wrapper with a built-in control socket. If you want a more integrated experience today, look into [cmux](https://www.bounds.dev/posts/teaching-claude-code-to-drive-cmux/) — it lets agents split panes, send commands to other surfaces, and report progress through a CLI.

---

## Sources

- [Official Claude Code Agent Teams docs](https://code.claude.com/docs/en/agent-teams)
- [Ghostty Keybinding Reference](https://ghostty.org/docs/config/keybind/reference)
- [Ghostty + Claude Code setup (Eslam Helmy)](https://eslamhelmy.tech/blog/ghostty-claude-code-setup)
- [Claude Code Agent Teams Practical Guide (LaoZhang AI)](https://blog.laozhang.ai/en/posts/claude-code-agent-teams)
- [Watch Claude Code Agents Side by Side (Karan Singh)](https://ksingh7.medium.com/watch-claude-code-agents-work-side-by-side-a-tmux-setup-guide-1ef3ba1531c4)
- [Ghostty IPC/Scripting API discussion](https://github.com/ghostty-org/ghostty/discussions/2353)
- [Feature request: Ghostty as teammateMode backend](https://github.com/anthropics/claude-code/issues/24189)
- [ghostty-pane-splitter CLI tool](https://github.com/rikeda71/ghostty-pane-splitter)
