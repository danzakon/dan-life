---
name: reply-monitor
description: Monitor replies to your X posts and surface engagement opportunities.
  Use when asked to "check my replies", "who's replying to me", or as part of the
  daily ingest automation.
argument-hint: "[optional: specific post URL to check replies on]"
allowed-tools:
  - Read
  - Write
  - Bash
---

# Reply Monitor

Fetches recent replies to @danzakon's posts on X. Surfaces reply opportunities, drafts suggested responses, and routes interesting replies into the content pipeline. Designed for consistent engagement without manual reply management.

---

## Trigger

- Automated: Part of the daily 7:00 AM ingest Cowork task
- Manual: "Check my replies", "Who's replying to me?"
- Specific: "Check replies on {post URL}"

---

## Workspace

- `content/raw/x-posts/` — reply context storage
- `content/inbox/YYYY-MM-DD.md` — today's inbox
- `content/inbox/_index.md` — master registry
- `content/pipeline/index.db` — item registration
- `content/pipeline/strategy.md` — for angle generation

---

## Process

### Step 1: Fetch replies

```bash
# Get recent mentions / replies
xquery x:search "to:danzakon" --limit 30

# Or check a specific post
xquery x:replies {post_url}
```

Collect replies from the last 24 hours (or since last run).

### Step 2: Categorize replies

Group each reply by type:

| Type | Action |
|------|--------|
| **Substantive question** | Draft a helpful reply — this is engagement gold |
| **Interesting take / pushback** | Draft a thoughtful response — builds discussion |
| **Agreement / compliment** | Quick acknowledgment reply (like or short thank you) |
| **Troll / bad faith** | Skip — don't engage |
| **Content spark** | The reply raises an interesting angle worth its own post |

### Step 3: Process substantive replies

For each substantive reply or content spark:

1. **Assign ID** with `RM` prefix
2. **Write raw file** to `content/raw/x-posts/YYYYMMDD-RM-NNN-{replier}-reply.md`:

```yaml
---
id: YYYYMMDD-RM-NNN
source-type: x-post
ingest-source: reply-monitor
original-url: https://x.com/{replier}/status/{reply_id}
author: @{replier}
in-reply-to: https://x.com/danzakon/status/{original_id}
captured: ISO 8601 UTC
reply-type: question | pushback | content-spark
---

Original post by @danzakon:
{original tweet text}

Reply by @{replier}:
{reply text}
```

3. **Write inbox entry** with:
   - Summary of the exchange
   - **Suggested reply draft** (the key value-add of this skill)
   - Content angles if the exchange sparks a new topic
   - Mark as `time-sensitive` (replies get stale fast)

### Step 4: Generate reply drafts

For each substantive reply, draft a response that:
- Addresses their specific point
- Adds value (don't just agree — extend, clarify, or offer a new angle)
- Matches the tone of the exchange
- Is concise (reply threads should be snappy)
- Follows the anti-AI writing standards from write-post

Inbox entry format for replies:

```markdown
## [YYYYMMDD-RM-NNN] Reply from @{replier} on "{original topic}"

**Status:** unreviewed
**Type:** reply-opportunity
**Urgency:** time-sensitive
**Original post:** {URL to your post}
**Reply:** {URL to their reply}
**Raw file:** content/raw/x-posts/YYYYMMDD-RM-NNN-{replier}-reply.md

### Context
{1-sentence summary of what you posted and what they replied}

### Suggested reply
"{Draft reply text — ready to post if approved}"

### Content angles (if this exchange sparks content)
1. **Post**: {if the exchange surfaces a new angle worth a standalone post}
2. **Thread**: {if the discussion could expand into a thread}

### Actions
- [ ] Post the suggested reply
- [ ] Edit and post
- [ ] Write standalone post from this exchange
- [ ] Skip
```

### Step 5: Register in index.db

```bash
sqlite3 content/pipeline/index.db \
  "INSERT INTO items (id, created_at, source_type, ingest_source, status, current_title, original_url, raw_file, format)
   VALUES ('{ID}', '{datetime}', 'x-post', 'reply-monitor', 'raw',
           'Reply from @{replier}: {summary}', '{reply_url}',
           'content/raw/x-posts/{filename}', 'reply');"
```

### Step 6: Summary

```
Reply Monitor — 2026-03-07
─────────────────────────────────────────
Found 14 replies to your recent posts.

  Substantive (reply drafts ready): 3
    RM-001  @engineer_joe — question about agent architecture
    RM-002  @startup_cto — pushback on your pricing take
    RM-003  @ai_dev — interesting extension of your point

  Quick acknowledgments: 8 (like or short reply)
  Skipped (trolls/noise): 3

  Content sparks: 1
    RM-002 could become a standalone post about pricing counterarguments

Reply drafts are in today's inbox. Review with /content-interview.
```

---

## Prerequisites

`xquery` CLI must be in PATH with X API access configured.
