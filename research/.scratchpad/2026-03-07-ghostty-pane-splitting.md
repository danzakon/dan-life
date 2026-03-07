# Ghostty Pane Splitting

**Category:** Tool
**Date Started:** 3-07-26
**Status:** [x] Complete

---

## Summary

Comprehensive reference for Ghostty terminal's pane splitting capabilities, including default keybindings (macOS and Linux), navigation between panes, config customization, programmatic control status, and the third-party `ghostty-pane-splitter` CLI tool.

---

## Key Findings

- Ghostty has solid built-in split support with sensible defaults on both macOS and Linux
- Directional pane navigation (up/down/left/right) is supported in addition to sequential (next/previous)
- Split resizing and equalizing are first-class features
- Ghostty does NOT yet have a scripting API or CLI for programmatic pane control (as of March 2026)
- `ghostty-pane-splitter` fills the gap by simulating keyboard input via the `enigo` Rust library
- A scripting API is the most-requested feature in the Ghostty repo (Discussion #2353), but no timeline exists

---

## 1. Default Keybindings for Creating Splits

### macOS

| Action              | Keybinding       | Action ID           |
|---------------------|------------------|---------------------|
| New split (right)   | `Cmd+D`          | `new_split:right`   |
| New split (down)    | `Cmd+Shift+D`    | `new_split:down`    |

### Linux / Windows

| Action              | Keybinding         | Action ID           |
|---------------------|-------------------|---------------------|
| New split (right)   | `Ctrl+Shift+O`    | `new_split:right`   |
| New split (down)    | `Ctrl+Shift+E`    | `new_split:down`    |

### All Valid `new_split` Directions

The `new_split` action accepts: `right`, `down`, `left`, `up`, `auto`.

- `auto` splits along the larger dimension (wider = vertical split, taller = horizontal split)

---

## 2. Keybindings for Navigating Between Panes

### macOS

| Action                | Keybinding           | Action ID              |
|-----------------------|---------------------|------------------------|
| Focus previous split  | `Cmd+[`             | `goto_split:previous`  |
| Focus next split      | `Cmd+]`             | `goto_split:next`      |
| Focus split up        | `Cmd+Option+Up`     | `goto_split:up`        |
| Focus split down      | `Cmd+Option+Down`   | `goto_split:down`      |
| Focus split left      | `Cmd+Option+Left`   | `goto_split:left`      |
| Focus split right     | `Cmd+Option+Right`  | `goto_split:right`     |

### Linux / Windows

| Action                | Keybinding              | Action ID              |
|-----------------------|------------------------|------------------------|
| Focus previous split  | `Ctrl+Super+[`         | `goto_split:previous`  |
| Focus next split      | `Ctrl+Super+]`         | `goto_split:next`      |
| Focus split up        | `Ctrl+Alt+Up`          | `goto_split:up`        |
| Focus split down      | `Ctrl+Alt+Down`        | `goto_split:down`      |
| Focus split left      | `Ctrl+Alt+Left`        | `goto_split:left`      |
| Focus split right     | `Ctrl+Alt+Right`       | `goto_split:right`     |

### Other Split Actions (Both Platforms)

| Action              | macOS                  | Linux                      | Action ID              |
|---------------------|------------------------|----------------------------|------------------------|
| Toggle split zoom   | `Cmd+Shift+Enter`      | `Ctrl+Shift+Enter`         | `toggle_split_zoom`    |
| Resize split up     | `Cmd+Ctrl+Up`          | `Ctrl+Super+Shift+Up`      | `resize_split:up,10`   |
| Resize split down   | `Cmd+Ctrl+Down`        | `Ctrl+Super+Shift+Down`    | `resize_split:down,10` |
| Resize split left   | `Cmd+Ctrl+Left`        | `Ctrl+Super+Shift+Left`    | `resize_split:left,10` |
| Resize split right  | `Cmd+Ctrl+Right`       | `Ctrl+Super+Shift+Right`   | `resize_split:right,10`|
| Equalize splits     | `Cmd+Ctrl+=`           | `Ctrl+Super+Shift+=`       | `equalize_splits`      |
| Close split         | `Cmd+W`                | `Ctrl+Shift+W`             | `close_surface`        |

---

## 3. Customizing Keybindings in the Ghostty Config

### Config File Location

- **macOS:** `~/Library/Application Support/com.mitchellh.ghostty/config`
  (also accessible via symlink at `~/.config/ghostty/config`)
- **Linux:** `~/.config/ghostty/config`

### Config Syntax

```
keybind = trigger=action
```

### Listing Default Keybindings

```bash
ghostty +list-keybinds --default
```

This CLI command dumps all default keybindings.

### Examples: Customizing Split Keybindings

```ini
# Remap splits to pipe and underscore (common tmux-like setup)
keybind = cmd+shift+|=new_split:right
keybind = cmd+shift+-=new_split:down

# Vim-style directional navigation (using unconsumed modifier
# so these keys pass through to vim/neovim when it consumes them)
keybind = unconsumed:ctrl+k=goto_split:top
keybind = unconsumed:ctrl+j=goto_split:bottom
keybind = unconsumed:ctrl+h=goto_split:left
keybind = unconsumed:ctrl+l=goto_split:right

# Custom resize amounts
keybind = cmd+ctrl+up=resize_split:up,20
keybind = cmd+ctrl+down=resize_split:down,20

# Equalize all splits
keybind = cmd+ctrl+=equalize_splits

# Unbind a default keybinding
keybind = cmd+d=unbind
```

### Trigger Modifiers

| Modifier   | macOS Key | Linux Key    |
|------------|-----------|--------------|
| `super`    | Cmd       | Super/Win    |
| `ctrl`     | Ctrl      | Ctrl         |
| `alt`      | Option    | Alt          |
| `shift`    | Shift     | Shift        |

### Special Prefixes

| Prefix          | Behavior                                                                    |
|-----------------|-----------------------------------------------------------------------------|
| `global:`       | Keybind works even when Ghostty is not focused                              |
| `unconsumed:`   | Only triggers if the terminal app didn't consume the key (useful for vim)   |
| `all:`          | Apply action to all surfaces (e.g., `all:close_window`)                     |

### Important Notes

- After changing keybindings, reload config with `Cmd+Shift+,` (macOS) or `Ctrl+Shift+,` (Linux), or restart Ghostty.
- The `goto_split` action accepts: `right`, `down`, `left`, `up`, `previous`, `next`.
- The `resize_split` action takes direction and pixel amount, comma-separated: `resize_split:up,10`.

---

## 4. Programmatic Pane Control

### Current State: No Scripting API (as of March 2026)

Ghostty does NOT have a scripting/remote-control API. This is the single most requested feature in the project (GitHub Discussion #2353, 233 upvotes, 45+ comments, ongoing since October 2023).

### What's Being Discussed

The maintainer (Mitchell Hashimoto) outlined two parallel approaches under consideration:

1. **Escape sequence-based control** (for TUI apps running inside Ghostty)
   - Similar to Kitty's remote control protocol or iTerm2's OSC 1337
   - Blocked on security design (escape sequences can be sent by anything, even `cat`-ing a file)
   - Shelved for now

2. **Platform-native IPC** (for external apps controlling Ghostty)
   - **macOS:** Apple Shortcuts / App Intents (partially working already)
   - **Linux:** D-Bus (already used for `ghostty +new-window`)
   - These are platform-specific by design

### What Works Today

| Method                           | Platform | Capabilities                    |
|----------------------------------|----------|---------------------------------|
| `ghostty +new-window`            | Linux    | Open new window only            |
| `open -na Ghostty.app --args`    | macOS    | Open new instance with args     |
| Apple Shortcuts / App Intents    | macOS    | Limited automation              |
| D-Bus                            | Linux    | New window only                 |
| Hammerspoon (accessibility API)  | macOS    | Window/tab switching via HS     |
| AppleScript (System Events)      | macOS    | Keystroke simulation (hacky)    |

### Bottom Line

You cannot currently:
- Create splits programmatically via CLI
- Send commands to specific panes
- Query which panes exist
- Focus specific panes from external scripts

The only viable workaround is simulating keyboard input, which is exactly what `ghostty-pane-splitter` does.

---

## 5. ghostty-pane-splitter CLI Tool

**Repository:** [rikeda71/ghostty-pane-splitter](https://github.com/rikeda71/ghostty-pane-splitter)
**Language:** Rust
**License:** MIT
**Latest Version:** v0.2.0 (March 1, 2026)
**Stars:** 2

### What It Does

Automates Ghostty's pane splitting by simulating keyboard inputs via the `enigo` Rust library. It reads your Ghostty config to know which keybindings to simulate, then sends those keystrokes to create multi-pane layouts with a single command.

### Installation

```bash
# Homebrew (macOS) - easiest
brew install rikeda71/tap/ghostty-pane-splitter

# Cargo (cross-platform)
cargo install ghostty-pane-splitter

# curl - macOS Apple Silicon
curl -fsSL https://github.com/rikeda71/ghostty-pane-splitter/releases/latest/download/ghostty-pane-splitter-aarch64-apple-darwin.tar.gz | tar xz
sudo mv ghostty-pane-splitter /usr/local/bin/

# curl - macOS Intel
curl -fsSL https://github.com/rikeda71/ghostty-pane-splitter/releases/latest/download/ghostty-pane-splitter-x86_64-apple-darwin.tar.gz | tar xz
sudo mv ghostty-pane-splitter /usr/local/bin/

# curl - Linux x86_64
curl -fsSL https://github.com/rikeda71/ghostty-pane-splitter/releases/latest/download/ghostty-pane-splitter-x86_64-unknown-linux-gnu.tar.gz | tar xz
sudo mv ghostty-pane-splitter /usr/local/bin/

# From source
git clone https://github.com/rikeda71/ghostty-pane-splitter.git
cd ghostty-pane-splitter
cargo install --path .
```

**Linux prerequisite:** `sudo apt install libxdo-dev`

### Required Ghostty Config

The tool reads keybindings from your Ghostty config. You MUST have these keybindings configured:

```ini
keybind = super+d=new_split:right
keybind = super+shift+d=new_split:down
keybind = super+ctrl+right_bracket=goto_split:next
keybind = super+ctrl+left_bracket=goto_split:previous
keybind = super+ctrl+shift+equal=equalize_splits
```

After adding these, restart Ghostty (config reload alone may not suffice).

### Usage

```bash
ghostty-pane-splitter <LAYOUT>
```

`<LAYOUT>` accepts three formats:

| Format              | Example                | Description                        |
|---------------------|------------------------|------------------------------------|
| Pane count          | `ghostty-pane-splitter 4`    | Creates a 2x2 grid            |
| Grid spec (COLSxROWS) | `ghostty-pane-splitter 2x3` | Explicit 2 cols, 3 rows       |
| Custom column layout | `ghostty-pane-splitter 1,3`  | Left: 1 pane, Right: 3 panes |

### Layout Examples

```
Input: 2          Input: 4          Input: 9
+-------+----+   +------+------+   +---+---+---+
|       |    |   |      |      |   |   |   |   |
|       |    |   +------+------+   +---+---+---+
+-------+----+   |      |      |   |   |   |   |
                 +------+------+   +---+---+---+
                                   |   |   |   |
                                   +---+---+---+

Input: 1,3                Input: 2,1,3
+--------+--------+       +----+----+----+
|        |        |       |    |    |    |
|        +--------+       |    |    +----+
|        |        |       +----+    |    |
|        +--------+       |    |    +----+
|        |        |       +----+    |    |
+--------+--------+       +----+----+----+
```

### AI Coding Agent Use Case

The tool is explicitly designed for multi-agent workflows:

```bash
# 3-pane layout: Left = AI agent, Right-top = editor, Right-bottom = terminal
ghostty-pane-splitter 1,2

# 4-pane layout for parallel AI agents with git worktrees
ghostty-pane-splitter 4
```

### Limitations

- Works by simulating keyboard input, so it needs accessibility permissions (macOS)
- The Ghostty window must be focused when the tool runs
- No ability to run commands in specific panes after splitting (just creates the layout)
- If keybindings in your config don't match what the tool expects, it will error

---

## Sources

- [Ghostty Keybinding Action Reference](https://ghostty.org/docs/config/keybind/reference) -- official docs
- [Ghostty Keybindings Configuration](https://ghostty.org/docs/config/keybind) -- official docs
- [Ghostty Keyboard Shortcuts Gist](https://gist.github.com/trashhalo/2fc177d74c1d6791f1874a3c59865660) -- community reference
- [ghostty-pane-splitter GitHub](https://github.com/rikeda71/ghostty-pane-splitter) -- tool repo
- [ghostty-pane-splitter on crates.io](https://lib.rs/crates/ghostty-pane-splitter) -- Rust crate
- [Scripting API Discussion #2353](https://github.com/ghostty-org/ghostty/discussions/2353) -- feature request
- [Ghostty Splits Blog Post](https://perrotta.dev/2026/01/ghostty-splits/) -- Thiago Perrotta
- [Ghostty Keybindings Blog Post](https://perrotta.dev/2026/01/ghostty-keybindings/) -- Thiago Perrotta
- [Neovim + Ghostty Split Navigation](https://www.reddit.com/r/neovim/comments/1hne1q6/navigation_between_ghostty_and_neovim_splits/) -- Reddit

---

## Next Steps

- [ ] Install ghostty-pane-splitter via Homebrew
- [ ] Add required keybindings to Ghostty config
- [ ] Test common layouts (2, 4, 1,2)
- [ ] Monitor Ghostty scripting API discussion for progress
