---
name: xquery
description: Query Grok (xAI) with live X search, or query the X API directly.
  Use when asked to "ask grok", "query grok", "search X for", "what's trending",
  "get tweets from @user", "look up tweet", "check my bookmarks",
  or when real-time X/Twitter data is needed.
argument-hint: "[query]" or "x:search [query]" or "x:user @handle" or "x:bookmarks"
allowed-tools: Bash
---

# xquery: Query Grok + X API

Three modes of operation:
1. **Grok queries** (default) - Ask Grok with live X search, get interpreted answers
2. **Direct X API** - Get raw tweet data, user info, metrics
3. **Bookmarks** - Fetch your bookmarked tweets (requires OAuth 2.0 user tokens)

## Usage

```bash
# Grok query (interpreted answer)
xquery "$ARGUMENTS"

# Direct X API commands
xquery x:search "query"      # Search recent tweets
xquery x:user @handle        # Get user info + tweets
xquery x:tweet 123456789     # Look up specific tweet
xquery x:bookmarks           # Fetch your bookmarked tweets
```

The `xquery` command is in the user's PATH. Always use it directly.

## Options

| Flag | Description |
|------|-------------|
| `--no-x-search` | Disable Grok's live X search |
| `--json` | Output raw JSON response |
| `--limit N` | Number of results for X API commands (default: 10) |
| `--model MODEL` | Override Grok model (default: grok-4) |
| `--include-rts` | Include retweets in x:search |
| `--include-replies` | Include replies in x:search |
| `--all` | Include both retweets and replies |

## When to Use

**Use Grok (default)** when:
- User wants an interpreted/synthesized answer
- "What are people saying about..."
- "What's the sentiment on..."

**Use x:search** when:
- User wants raw tweet data
- Need actual tweet text and metrics
- Building a dataset

**Use x:user** when:
- Looking up a specific account
- Getting follower counts, bio
- Seeing recent tweets from someone

**Use x:tweet** when:
- Have a specific tweet ID or URL
- Need full metrics on one tweet

**Use x:bookmarks** when:
- Mining bookmarks for content ideas (see `bookmark-mining` skill)
- Checking what you've saved recently
- Finding interesting tweets to remix into content

## Examples

```bash
# Ask Grok about trending topics
xquery "What's the AI community saying about Claude Code?"

# Get raw search results
xquery x:search "Claude Code" --limit 20

# Look up a user
xquery x:user @AnthropicAI

# Get a specific tweet
xquery x:tweet 1234567890123456789

# Fetch recent bookmarks
xquery x:bookmarks --limit 50
```

## Setup

Config file: `~/.config/xquery/.env`

```bash
# For Grok queries (xAI API)
XAI_API_KEY=xai-your-key

# For direct X API (x:search, x:user, x:tweet)
# Get at developer.x.com - Basic tier $100/mo required for search
X_BEARER_TOKEN=AAAA...
```

Both keys are independent - Grok works without X API and vice versa.

## Bookmarks Setup (OAuth 2.0)

The bookmarks API requires **user-level OAuth 2.0 tokens** (different from the app-level bearer token used for search). One-time setup:

### Prerequisites

- An X Developer App with OAuth 2.0 enabled
- Client ID and Client Secret from the X Developer Portal
- Scopes: `bookmark.read`, `tweet.read`, `users.read`

### Configuration

Add to `~/.config/xquery/.env`:

```bash
# For bookmarks (OAuth 2.0 PKCE)
X_CLIENT_ID=your-client-id
X_CLIENT_SECRET=your-client-secret
X_USER_ID=your-numeric-user-id
```

### First-Time Authorization

Run the OAuth setup (opens browser for authorization):

```bash
xquery x:bookmarks --setup
```

This performs the OAuth 2.0 PKCE flow:
1. Opens browser to authorize the app
2. You approve access to your bookmarks
3. Tokens are stored in `~/.config/xquery/oauth-tokens.json`
4. Tokens auto-refresh on subsequent calls

### API Details

The bookmarks endpoint:

```
GET https://api.x.com/2/users/{id}/bookmarks
Authorization: Bearer {user_access_token}
```

Query parameters:
- `max_results`: 1-100 (default: 50)
- `pagination_token`: for paging through results
- `tweet.fields`: `created_at,author_id,public_metrics,entities`
- `expansions`: `author_id` (to get usernames)

Returns tweet text, author info, URLs, and engagement metrics.
