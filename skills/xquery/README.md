# xquery

Query Grok and the X API from the command line.

```bash
# Ask Grok (with live X search)
xquery "What's trending in AI today?"

# Direct X API
xquery x:search "Claude Code"
xquery x:user @anthropic
xquery x:tweet 1234567890123456789
```

Works as both a CLI tool and a Claude Code skill.

## Installation

```bash
# 1. Clone to your Claude skills directory
git clone https://github.com/youruser/xquery ~/.claude/skills/xquery

# 2. Make executable and add to PATH
chmod +x ~/.claude/skills/xquery/scripts/xquery
mkdir -p ~/.local/bin
ln -sf ~/.claude/skills/xquery/scripts/xquery ~/.local/bin/xquery

# 3. Configure API keys
mkdir -p ~/.config/xquery
cat > ~/.config/xquery/.env << 'EOF'
# Required for Grok queries
XAI_API_KEY=xai-your-key-here

# Required for direct X API (x:search, x:user, x:tweet)
# Get at developer.x.com - Basic tier is $100/mo
X_BEARER_TOKEN=AAAA...your-bearer-token
EOF
chmod 600 ~/.config/xquery/.env

# 4. Test
xquery "Hello Grok"
```

## Usage

### Grok Queries (Default)

Ask Grok with live X/Twitter search enabled:

```bash
xquery "What are people saying about Claude Code?"
xquery "What's the sentiment on the new iPhone?"
xquery --no-x-search "Explain transformers"  # Disable X search
```

### Direct X API Commands

Query the X API directly for raw data:

```bash
# Search recent tweets (last 7 days)
xquery x:search "Claude Code" --limit 20

# Look up a user (includes recent tweets)
xquery x:user @elonmusk

# Get a specific tweet by ID
xquery x:tweet 1234567890123456789

# Get raw JSON
xquery x:search "AI agents" --json | jq .
```

## Options

| Flag | Description |
|------|-------------|
| `--no-x-search` | Disable Grok's live X search |
| `--json` | Output raw JSON response |
| `--limit N` | Results for X API commands (default: 10) |
| `--model MODEL` | Grok model (default: grok-4) |
| `--include-rts` | Include retweets in x:search |
| `--include-replies` | Include replies in x:search |
| `--all` | Include both retweets and replies |

**Note:** x:search results are sorted by relevancy (engagement-weighted) and exclude retweets/replies by default.

## Configuration

Config file: `~/.config/xquery/.env`

```bash
# For Grok queries (xAI)
XAI_API_KEY=xai-your-key-here
XAI_MODEL=grok-4

# For direct X API commands
X_BEARER_TOKEN=AAAA...
```

### Getting API Keys

| API | Where | Cost |
|-----|-------|------|
| xAI (Grok) | [x.ai](https://x.ai) | Pay per use |
| X API | [developer.x.com](https://developer.x.com) | Basic: $100/mo |

The X API Free tier is effectively useless for reading tweets. Basic ($100/mo) is required for search.

## As a Claude Code Skill

Once installed, Claude can use xquery automatically or via manual invocation:

```
/xquery What's the sentiment on X about the new Claude update?
/xquery x:search "Claude Code" --limit 15
```

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│  xquery "prompt"                    xquery x:search "query"         │
│       │                                    │                        │
│       ▼                                    ▼                        │
│  ┌─────────┐                         ┌──────────┐                   │
│  │  Grok   │ ◄─── x_search tool      │  X API   │                   │
│  │  (xAI)  │      (internal)         │  v2      │                   │
│  └────┬────┘                         └────┬─────┘                   │
│       │                                   │                         │
│       ▼                                   ▼                         │
│  Interpreted                         Raw tweets                     │
│  answer                              + metrics                      │
└─────────────────────────────────────────────────────────────────────┘
```

## Requirements

- Python 3.7+
- xAI API key (for Grok queries)
- X API Bearer Token (for direct X API, $100/mo minimum)

## License

MIT
