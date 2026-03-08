# Vercel Agent Browser + Claude Code Setup

A guide to setting up Vercel's agent-browser CLI to give Claude Code full browser automation capabilities.

---

## Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Claude Code                                  │
│                                                                      │
│   "Test the login flow on staging"                                  │
│              │                                                       │
│              ▼                                                       │
│   ┌─────────────────────┐                                           │
│   │   agent-browser     │◀─── Skill provides context on how to use  │
│   │   (CLI commands)    │                                           │
│   └──────────┬──────────┘                                           │
│              │                                                       │
└──────────────┼───────────────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    Browser Automation                                │
│                                                                      │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐            │
│   │   open      │    │  snapshot   │    │   click     │            │
│   │   (navigate)│───▶│  (get refs) │───▶│   (act)     │            │
│   └─────────────┘    └─────────────┘    └─────────────┘            │
│                                                                      │
│   Headless Chromium controlled via Playwright                       │
└─────────────────────────────────────────────────────────────────────┘
```

**What agent-browser does:**
- Provides a CLI for headless browser automation
- Uses a "ref" system that makes element selection deterministic and AI-friendly
- Outputs accessibility trees that Claude can parse to understand page structure
- Supports sessions, persistent profiles, authentication, and cloud browser providers

**Why it's useful for Claude Code:**
- Test web applications end-to-end
- Scrape data from websites
- Automate repetitive browser tasks
- Debug UI issues by taking screenshots
- Fill forms, click buttons, navigate flows

---

## Part 1: Installation

### 1.1 Install agent-browser globally

```bash
npm install -g agent-browser
```

| Part | Meaning |
|------|---------|
| `npm install` | Install a package from the npm registry |
| `-g` | **Global**—install system-wide, not just in current project |
| `agent-browser` | The package name |

### 1.2 Download the browser engine

```bash
agent-browser install
```

This downloads Chromium (~150MB) to your system. On Linux, you may need additional dependencies:

```bash
agent-browser install --with-deps
```

| Flag | Meaning |
|------|---------|
| `--with-deps` | Also install system dependencies (Linux only) |

### 1.3 Verify installation

```bash
agent-browser --version
agent-browser open example.com
agent-browser snapshot
agent-browser close
```

You should see an accessibility tree output from `snapshot` showing the page structure.

---

## Part 2: Add the Skill to Claude Code

The "skill" gives Claude Code detailed context on how to use agent-browser effectively.

### 2.1 Install the skill

```bash
npx add-skill vercel-labs/agent-browser
```

| Part | Meaning |
|------|---------|
| `npx` | Run a package without installing it globally |
| `add-skill` | Vercel's tool for adding agent skills across AI coding assistants |
| `vercel-labs/agent-browser` | GitHub shorthand for the repo |

This installs the skill to `~/.claude/skills/agent-browser/` (or your project's `.claude/skills/` directory).

### 2.2 Alternative: Manual CLAUDE.md instructions

If you prefer not to use the skill system, add this to your project's `CLAUDE.md` or `~/.claude/CLAUDE.md`:

```markdown
## Browser Automation

Use `agent-browser` for web automation. Run `agent-browser --help` for all commands.

Core workflow:
1. `agent-browser open <url>` - Navigate to page
2. `agent-browser snapshot -i` - Get interactive elements with refs (@e1, @e2)
3. `agent-browser click @e1` / `fill @e2 "text"` - Interact using refs
4. Re-snapshot after page changes

Key commands:
- `agent-browser screenshot page.png` - Take screenshot
- `agent-browser get text @e1` - Get element text
- `agent-browser fill @e1 "value"` - Fill input field
- `agent-browser close` - Close browser
```

---

## Part 3: Core Workflow

The key insight: **refs make element selection deterministic**.

```
┌─────────────────────────────────────────────────────────────────┐
│  1. OPEN                                                         │
│     agent-browser open https://myapp.com/login                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  2. SNAPSHOT (get refs)                                          │
│     agent-browser snapshot -i                                    │
│                                                                  │
│     Output:                                                      │
│     - heading "Login" [ref=e1] [level=1]                        │
│     - textbox "Email" [ref=e2]                                  │
│     - textbox "Password" [ref=e3]                               │
│     - button "Sign In" [ref=e4]                                 │
│     - link "Forgot password?" [ref=e5]                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  3. ACT (using refs)                                             │
│     agent-browser fill @e2 "user@example.com"                   │
│     agent-browser fill @e3 "secretpassword"                     │
│     agent-browser click @e4                                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  4. RE-SNAPSHOT (page changed)                                   │
│     agent-browser snapshot -i                                    │
│                                                                  │
│     Output:                                                      │
│     - heading "Dashboard" [ref=e1]                              │
│     - ...                                                        │
└─────────────────────────────────────────────────────────────────┘
```

### Why refs matter

Traditional selectors (`#id`, `.class`, `xpath`) are fragile:
- They require knowledge of the DOM structure
- They break when the page changes
- AI agents struggle to construct them reliably

Refs are:
- **Deterministic**: Assigned fresh on each snapshot
- **Readable**: `@e2` is easier for AI to track than `#login-form > div:nth-child(2) > input`
- **Scoped**: Only valid until the next snapshot (forces you to re-observe after actions)

---

## Part 4: Command Reference

### Navigation

| Command | Description |
|---------|-------------|
| `agent-browser open <url>` | Navigate to URL |
| `agent-browser back` | Go back |
| `agent-browser forward` | Go forward |
| `agent-browser reload` | Reload page |

### Observation

| Command | Description |
|---------|-------------|
| `agent-browser snapshot` | Full accessibility tree with refs |
| `agent-browser snapshot -i` | Interactive elements only (buttons, inputs, links) |
| `agent-browser snapshot -c` | Compact (remove empty structural elements) |
| `agent-browser snapshot -d 3` | Limit depth to 3 levels |
| `agent-browser screenshot [path]` | Take screenshot (base64 to stdout if no path) |
| `agent-browser screenshot --full` | Full page screenshot |

### Interaction

| Command | Description |
|---------|-------------|
| `agent-browser click @e1` | Click element |
| `agent-browser fill @e1 "text"` | Clear and fill input |
| `agent-browser type @e1 "text"` | Type without clearing |
| `agent-browser press Enter` | Press key |
| `agent-browser hover @e1` | Hover element |
| `agent-browser select @e1 "option"` | Select dropdown option |
| `agent-browser check @e1` | Check checkbox |
| `agent-browser uncheck @e1` | Uncheck checkbox |

### Getting Information

| Command | Description |
|---------|-------------|
| `agent-browser get text @e1` | Get element text |
| `agent-browser get value @e1` | Get input value |
| `agent-browser get attr @e1 href` | Get attribute |
| `agent-browser get title` | Get page title |
| `agent-browser get url` | Get current URL |
| `agent-browser is visible @e1` | Check visibility |

### Waiting

| Command | Description |
|---------|-------------|
| `agent-browser wait @e1` | Wait for element to be visible |
| `agent-browser wait 2000` | Wait 2 seconds |
| `agent-browser wait --text "Success"` | Wait for text to appear |
| `agent-browser wait --url "**/dashboard"` | Wait for URL pattern |

### Session Management

| Command | Description |
|---------|-------------|
| `agent-browser close` | Close browser |
| `agent-browser --session work open site.com` | Use named session |
| `agent-browser session list` | List active sessions |

---

## Part 5: Sessions and Profiles

### Sessions (Isolated instances)

Run multiple browsers in parallel:

```bash
# Terminal 1: Testing as admin
agent-browser --session admin open myapp.com/admin

# Terminal 2: Testing as regular user
agent-browser --session user open myapp.com/dashboard
```

Each session has its own:
- Browser instance
- Cookies and storage
- Navigation history

### Profiles (Persistent state)

By default, browser state is lost when the browser closes. Use `--profile` to persist:

```bash
# First time: log in manually
agent-browser --profile ~/.myapp-profile open myapp.com
# ... perform login ...
agent-browser close

# Later: session is preserved
agent-browser --profile ~/.myapp-profile open myapp.com/dashboard
# You're already logged in!
```

| Flag | Meaning |
|------|---------|
| `--profile <path>` | Directory to store cookies, localStorage, IndexedDB, cache |

---

## Part 6: Authentication Strategies

### Option A: Persistent profile (recommended for development)

```bash
# Log in once interactively
agent-browser --profile ~/.myprofile --headed open myapp.com/login
# Perform login in the visible browser window
agent-browser close

# Reuse authenticated session
agent-browser --profile ~/.myprofile open myapp.com/dashboard
```

### Option B: HTTP headers (for API tokens)

```bash
agent-browser open api.example.com --headers '{"Authorization": "Bearer <token>"}'
```

Headers are scoped to the origin—won't leak to other domains.

### Option C: Save/load state

```bash
# After logging in
agent-browser state save ~/auth-state.json

# Restore later
agent-browser state load ~/auth-state.json
```

---

## Part 7: Cloud Browser Providers

For CI/CD or serverless environments where local Chromium isn't available.

### Browserbase

```bash
export BROWSERBASE_API_KEY="your-api-key"
export BROWSERBASE_PROJECT_ID="your-project-id"

agent-browser -p browserbase open https://example.com
```

### Browser Use

```bash
export BROWSER_USE_API_KEY="your-api-key"

agent-browser -p browseruse open https://example.com
```

All commands work identically—the provider just runs the browser remotely.

---

## Part 8: Debugging

### Headed mode (see the browser)

```bash
agent-browser open example.com --headed
```

Opens a visible browser window instead of running headless.

### Console and errors

```bash
agent-browser console          # View console messages
agent-browser errors           # View JS exceptions
```

### Highlight elements

```bash
agent-browser highlight @e1    # Visually highlight element
```

### Tracing

```bash
agent-browser trace start
# ... perform actions ...
agent-browser trace stop trace.zip
```

Open the trace file at [trace.playwright.dev](https://trace.playwright.dev) for a full timeline.

---

## Part 9: Example Workflows

### Testing a login flow

```bash
# Navigate
agent-browser open https://staging.myapp.com/login

# Observe
agent-browser snapshot -i
# Output shows: textbox "Email" [ref=e2], textbox "Password" [ref=e3], button "Log in" [ref=e4]

# Act
agent-browser fill @e2 "test@example.com"
agent-browser fill @e3 "testpassword"
agent-browser click @e4

# Wait for navigation
agent-browser wait --url "**/dashboard"

# Verify
agent-browser snapshot -i
agent-browser screenshot dashboard.png

# Cleanup
agent-browser close
```

### Scraping data from a table

```bash
agent-browser open https://example.com/data

# Get the table structure
agent-browser snapshot -s "table"

# Extract specific cell values
agent-browser get text @e5
agent-browser get text @e6

# Or use JavaScript for complex extraction
agent-browser eval "JSON.stringify([...document.querySelectorAll('tr')].map(r => r.textContent))"

agent-browser close
```

### Form automation

```bash
agent-browser open https://forms.example.com

agent-browser snapshot -i

agent-browser fill @e2 "John Doe"
agent-browser fill @e3 "john@example.com"
agent-browser select @e4 "United States"
agent-browser check @e5   # Terms checkbox
agent-browser click @e6   # Submit button

agent-browser wait --text "Thank you"
agent-browser screenshot confirmation.png

agent-browser close
```

---

## Part 10: Environment Variables

Configure defaults via environment variables:

| Variable | Description |
|----------|-------------|
| `AGENT_BROWSER_SESSION` | Default session name |
| `AGENT_BROWSER_PROFILE` | Default profile path |
| `AGENT_BROWSER_EXECUTABLE_PATH` | Custom Chromium path |
| `AGENT_BROWSER_PROXY` | Proxy server URL |
| `AGENT_BROWSER_USER_AGENT` | Custom User-Agent string |
| `AGENT_BROWSER_PROVIDER` | Cloud provider (browserbase, browseruse) |
| `AGENT_BROWSER_STREAM_PORT` | Enable viewport streaming on this port |

---

## Troubleshooting

### Browser won't start

```bash
# Reinstall browser
agent-browser install

# On Linux, install system deps
agent-browser install --with-deps
```

### "No browser session" error

The browser closed unexpectedly or was never opened:

```bash
agent-browser open example.com   # Start fresh
```

### Refs not found

Refs are invalidated after page changes. Always re-snapshot:

```bash
agent-browser click @e4
agent-browser snapshot -i        # Get new refs
agent-browser click @e2          # Use new refs
```

### Timeout waiting for element

The element doesn't exist or isn't visible:

```bash
# Take a screenshot to see current state
agent-browser screenshot debug.png

# Try waiting longer
agent-browser wait @e1 --timeout 10000

# Check if in iframe
agent-browser frame "iframe-selector"
agent-browser snapshot -i
```

### HTTPS certificate errors

For self-signed certs in development:

```bash
agent-browser open https://localhost:3000 --ignore-https-errors
```

---

## Quick Reference Card

```
┌─────────────────────────────────────────────────────────────────┐
│  NAVIGATION                                                      │
│    open <url>          Navigate                                 │
│    back / forward      History navigation                       │
│    reload              Refresh page                             │
├─────────────────────────────────────────────────────────────────┤
│  OBSERVATION                                                     │
│    snapshot -i         Get interactive elements with refs       │
│    screenshot [path]   Capture current view                     │
│    get text @ref       Extract text content                     │
│    get url / title     Page metadata                            │
├─────────────────────────────────────────────────────────────────┤
│  INTERACTION                                                     │
│    click @ref          Click element                            │
│    fill @ref "text"    Clear and type                           │
│    press Enter         Keyboard input                           │
│    select @ref "opt"   Dropdown selection                       │
├─────────────────────────────────────────────────────────────────┤
│  WAITING                                                         │
│    wait @ref           Wait for element                         │
│    wait 2000           Wait milliseconds                        │
│    wait --text "..."   Wait for text                            │
│    wait --url "..."    Wait for URL pattern                     │
├─────────────────────────────────────────────────────────────────┤
│  SESSION                                                         │
│    --session <name>    Use named session                        │
│    --profile <path>    Persistent browser state                 │
│    --headed            Show browser window                      │
│    close               End session                              │
└─────────────────────────────────────────────────────────────────┘
```

---

## Next Steps

- [ ] Install agent-browser and verify it works
- [ ] Add the skill to Claude Code
- [ ] Test a simple workflow (open, snapshot, click, close)
- [ ] Set up a persistent profile for your main app
- [ ] Consider Browserbase/Browser Use for CI environments
