# Claude Code Agent Teams + Ghostty: Research Notes

**Date:** 2026-03-07

---

## Key Findings

### Agent Teams Setup
- Enable: `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` in settings.json or env
- Three display modes: `auto`, `in-process`, `tmux`
- Split-pane mode does NOT officially support Ghostty (only tmux + iTerm2)
- Feature request for Ghostty support: anthropics/claude-code#24189 (18 upvotes)

### Workaround: tmux Inside Ghostty
- Start tmux manually inside Ghostty before launching Claude Code
- Claude Code detects $TMUX and auto-creates panes
- Known issues: mouse selection breaks, Shift+Enter broken, key conflicts
- Fix Shift+Enter: add `keybind = shift+enter=text:\\x1b\\r` to Ghostty config

### Alternative: In-Process Mode + Native Ghostty Splits
- Run agent teams in in-process mode (all in one terminal)
- Use Ghostty native splits (Cmd+D) for monitoring panes
- Shift+Up/Down to cycle through teammates
- Cleanest experience, no tmux bugs

### Ghostty Pane Splitting
- macOS: Cmd+D (right), Cmd+Shift+D (down)
- Navigate: Cmd+Option+Arrow, Cmd+[ and Cmd+]
- Zoom: Cmd+Shift+Enter
- Equalize: Cmd+Ctrl+=
- No programmatic API yet (most requested feature)

### ghostty-pane-splitter Tool
- Rust CLI that simulates keyboard input to create layouts
- Install: `brew install rikeda71/tap/ghostty-pane-splitter`
- Usage: `ghostty-pane-splitter 4` (creates 2x2 grid)
- Requires specific keybindings in Ghostty config

## Sources
- Official docs: code.claude.com/docs/en/agent-teams
- Ghostty keybindings: ghostty.org/docs/config/keybind
- ghostty-pane-splitter: github.com/rikeda71/ghostty-pane-splitter
- Eslam Helmy setup: eslamhelmy.tech/blog/ghostty-claude-code-setup
- cmux integration: bounds.dev/posts/teaching-claude-code-to-drive-cmux/
- Karan Singh tmux guide: ksingh7.medium.com
- Feature request: github.com/anthropics/claude-code/issues/24189
