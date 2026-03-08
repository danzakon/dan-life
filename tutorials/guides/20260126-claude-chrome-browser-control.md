# Claude Chrome Extension Setup

A guide to setting up the Claude browser extension and connecting it to Claude Code for browser automation and control.

---

## Overview

```
┌─────────────────┐    Native Messaging    ┌─────────────────┐
│   Claude Code   │◀──────────────────────▶│  Chrome Browser │
│   (CLI)         │                         │  (Extension)    │
└────────┬────────┘                         └────────┬────────┘
         │                                           │
         │ Commands                                  │ Actions
         │                                           │
         ▼                                           ▼
┌─────────────────────────────────────────────────────────────┐
│                     Your Web Apps                            │
│  • localhost dev servers    • Google Docs, Gmail            │
│  • Any authenticated site   • Web scraping targets          │
└─────────────────────────────────────────────────────────────┘
```

**What you'll end up with:**
- Claude Code can control Chrome to click, type, navigate, and read pages
- Debug web apps by reading console errors directly
- Test UI flows in your actual browser (with your login sessions)
- Automate repetitive browser tasks
- Record browser interactions as GIFs

---

## Requirements

| Requirement | Details |
|-------------|---------|
| Browser | Google Chrome (not Brave, Arc, or other Chromium browsers) |
| OS | macOS or Linux (WSL not supported) |
| Claude Plan | Pro, Team, or Enterprise (paid plan required) |
| Claude Code | Version 2.0.73 or higher |
| Extension | Version 1.0.36 or higher |

---

## Part 1: Install the Chrome Extension

### 1.1 Install from Chrome Web Store

- [ ] Open Google Chrome
- [ ] Go to the Chrome Web Store: https://chromewebstore.google.com/detail/claude/fcoeoabgfenejglbffodgkkbkcdhcgfn
- [ ] Click **Add to Chrome**
- [ ] Click **Add extension** in the confirmation popup

### 1.2 Pin the Extension

- [ ] Click the puzzle piece icon (Extensions) in Chrome's toolbar
- [ ] Find "Claude" in the list
- [ ] Click the pin/thumbtack icon to keep it visible

### 1.3 Sign In

- [ ] Click the Claude extension icon in the toolbar
- [ ] Sign in with your Claude account credentials
- [ ] Grant the requested permissions when prompted

---

## Part 2: Connect to Claude Code

### 2.1 Update Claude Code

Make sure you're running the latest version:

```bash
claude update
```

### 2.2 Start Claude Code with Chrome Enabled

Launch Claude Code with the `--chrome` flag:

```bash
claude --chrome
```

| Part | Meaning |
|------|---------|
| `claude` | The Claude Code CLI |
| `--chrome` | Enable browser control tools for this session |

### 2.3 Verify the Connection

Inside Claude Code, run:

```
/chrome
```

This shows the connection status. You should see that the extension is detected and connected.

**If the extension isn't detected:**
1. Make sure Chrome is running
2. Verify the extension is installed and enabled
3. Select "Reconnect extension" from the `/chrome` menu

### 2.4 Enable Chrome by Default (Optional)

If you want browser tools available in every session without the `--chrome` flag:

1. Run `/chrome` inside Claude Code
2. Select **Enabled by default**

Note: This increases context usage since browser tools are always loaded, even when you don't need them.

---

## Part 3: What the Extension Can Do

### Available Capabilities

| Capability | Description |
|------------|-------------|
| **Navigate** | Open URLs, go back/forward, refresh pages |
| **Click** | Click buttons, links, and interactive elements |
| **Type** | Enter text into forms and inputs |
| **Read** | Extract text, HTML, or structured data from pages |
| **Screenshot** | Capture the visible page or specific elements |
| **Console** | Read browser console output (errors, logs, network) |
| **Multi-tab** | Open new tabs, switch between tabs, close tabs |
| **Record GIFs** | Capture browser interactions as animated GIFs |

### Practical Use Cases

**Live debugging:**
```
"Open localhost:3000, click the submit button, and tell me what errors appear in the console"
```

**Design verification:**
```
"Open the homepage and compare the header layout to this Figma screenshot"
```

**Automated testing:**
```
"Fill out the registration form with test data and verify the success message appears"
```

**Data extraction:**
```
"Go to this URL and extract all the product names and prices into a CSV"
```

**Authenticated workflows:**
```
"Open my Google Doc at this URL and add a summary section at the top"
```

### View Available Tools

To see the full list of browser tools:

```
/mcp
```

Click into `claude-in-chrome` to see all available actions.

---

## Part 4: How It Works

### Architecture

The extension uses Chrome's Native Messaging API to communicate with Claude Code:

1. **Claude Code** sends commands (click, type, navigate) to the extension
2. **Extension** executes commands in your actual browser
3. **Browser** performs the action using your real session (cookies, logins)
4. **Extension** sends results (screenshots, DOM content, console logs) back

### Important Behaviors

| Behavior | Explanation |
|----------|-------------|
| Uses real browser | Not headless—uses your actual Chrome with your logins |
| Opens new tabs | Claude opens new tabs for tasks rather than taking over existing ones |
| Requires visible window | Chrome must be open and visible (can't run minimized) |
| Pauses for auth | When Claude encounters a login page or CAPTCHA, it stops and asks you to handle it |

---

## Part 5: Permissions Explained

The extension requests 15 permissions. Here's what they do:

| Permission | Why It's Needed |
|------------|-----------------|
| `sidePanel` | Display Claude alongside your browser |
| `debugger` | Control browser actions (clicking, typing, screenshots) |
| `scripting` | Read webpage text and DOM content |
| `tabs` | Manage browser tabs (open, close, switch) |
| `tabGroups` | Organize tabs into groups |
| `notifications` | Send alerts when tasks complete |
| `alarms` | Schedule recurring tasks |
| `downloads` | Download files from websites |

### Site-Level Permissions

You can control which sites Claude can access:

- **Grant access** to specific sites when prompted
- **Revoke access** in Chrome's extension settings
- Certain high-risk categories (financial services) are blocked by default

---

## Part 6: Model Selection

Available models depend on your Claude plan:

| Plan | Available Models |
|------|------------------|
| Pro | Haiku 4.5 only |
| Max / Team / Enterprise | Opus 4.5, Sonnet 4.5, Haiku 4.5 |

For browser control tasks, faster models (Haiku) often work well since the actions are straightforward.

---

## Part 7: Safety Features

The extension includes several safety mechanisms:

| Feature | Description |
|---------|-------------|
| Site permissions | Grant/revoke access to specific websites |
| Action confirmations | Claude asks before sensitive operations |
| Website blocklists | Financial services and high-risk categories blocked |
| Attack detection | Classifiers detect prompt injection attempts on web pages |
| Auth handling | Claude pauses at login pages and CAPTCHAs for you to handle |

---

## Troubleshooting

### Extension not detected

1. Verify Chrome is running (not just in background)
2. Check extension is enabled in `chrome://extensions`
3. Confirm versions meet minimum requirements
4. Run `/chrome` and select "Reconnect extension"
5. Try restarting Chrome completely

### Browser not responding to commands

- Check for modal dialogs or popups blocking the page
- Ask Claude to open a new tab instead
- Verify the target site hasn't blocked automation

### First-time setup issues

The first connection installs a native messaging host on your system. If this fails:

1. Restart Chrome after installing the extension
2. Run `/chrome` in Claude Code to reinitialize
3. Check for permission issues in your home directory

### "Permission denied" on certain sites

Some sites are blocked by default. If you need access to a blocked site:

1. Check if it's in a high-risk category (financial, etc.)
2. Grant explicit permission when prompted
3. Some sites may have anti-automation measures that can't be bypassed

---

## Quick Reference

### Commands

| Command | Action |
|---------|--------|
| `claude --chrome` | Start Claude Code with browser tools |
| `/chrome` | Check connection status, manage settings |
| `/mcp` | View all available tools including browser actions |

### Common Prompts

```
# Debug a local app
"Open localhost:3000 and click around to test the navigation. Tell me if anything breaks."

# Extract data
"Go to [URL] and get me a list of all the links on the page."

# Test a form
"Fill out the contact form with test data and submit it."

# Take screenshots
"Open [URL] and take a screenshot of the hero section."

# Read console
"Open my app and tell me if there are any JavaScript errors."
```

---

## Limitations

- **Chrome only**: Doesn't work in Brave, Arc, Firefox, or other browsers
- **No headless mode**: Requires a visible Chrome window
- **No WSL**: Windows Subsystem for Linux is not supported
- **Paid plans only**: Requires Claude Pro, Team, or Enterprise
- **Some sites blocked**: Financial services and certain high-risk categories

---

## Resources

- Chrome Web Store: https://chromewebstore.google.com/detail/claude/fcoeoabgfenejglbffodgkkbkcdhcgfn
- Claude Code Chrome Docs: https://code.claude.com/docs/en/chrome
- Claude for Chrome Guide: https://support.claude.com/en/articles/12012173-getting-started-with-claude-for-chrome
