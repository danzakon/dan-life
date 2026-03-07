---
name: x-account-monitor
description: Monitor X accounts and surface content and engagement opportunities.
  Use when asked to "check my X accounts", "what are my follows posting", or as part
  of the daily ingest automation.
argument-hint: "[optional: specific @handle to check]"
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
---

# X Account Monitor

Scrapes recent posts from a curated list of X accounts defined in `sources.md`. Surfaces content ideas and engagement opportunities, especially reply opportunities with mutuals. Writes to the pipeline's raw + inbox system.

---

## Trigger

- Automated: Part of the daily 7:00 AM ingest Cowork task
- Manual: "Check my X accounts", "What are people posting?"
- Specific: "Check @handle"

---

## Workspace

- `content/pipeline/sources.md` — X Accounts Monitor + Mutuals sections
- `content/raw/x-posts/` — full tweet/thread text
- `content/inbox/YYYY-MM-DD.md` — today's inbox
- `content/inbox/_index.md` — master registry
- `content/pipeline/index.db` — item registration
- `content/pipeline/strategy.md` — for angle generation

---

## Process

### Step 1: Read account list

Read `content/pipeline/sources.md`. Parse two sections:

**X Accounts — Monitor:** All recent posts from these accounts are fetched and evaluated.

**X Accounts — Mutuals (Priority Engagement):** Same as Monitor, but these accounts get a priority score boost and are always flagged for reply opportunities.

### Step 2: Fetch recent posts

For each account, use xquery:

```bash
xquery x:user @{handle} --limit 10
```

Collect posts from the last 24 hours (or since the last ingest run, whichever is longer). Skip retweets unless they include commentary.

If checking a specific handle (manual invocation), fetch up to 20 posts.

### Step 3: Filter and evaluate

For each post, evaluate:

- **Relevance:** Does it touch any hot topic from `strategy.md`?
- **Reply opportunity:** Is this something worth responding to with a take?
- **Content spark:** Does this inspire a standalone post, thread, or article?
- **Engagement value:** Is the author a mutual? High-engagement post?

Skip posts that are:
- Purely personal / mundane
- Retweets without commentary
- Promotional / sponsored content
- Purely political (same filter as bookmark-mining)

### Step 4: Assign IDs and write raw files

For each post worth capturing, assign an `XM` ID:

```bash
sqlite3 content/pipeline/index.db \
  "SELECT id FROM items WHERE id LIKE '$(date +%Y%m%d)-XM-%' ORDER BY id DESC LIMIT 1;"
```

Write to `content/raw/x-posts/YYYYMMDD-XM-NNN-{handle}-{slug}.md`:

```yaml
---
id: YYYYMMDD-XM-NNN
source-type: x-post
ingest-source: x-account-monitor
original-url: https://x.com/{handle}/status/{id}
author: @{handle}
captured: ISO 8601 UTC
is-mutual: true | false
---

{Full tweet/thread text}
```

### Step 5: Write inbox entries

For each captured item, write an inbox entry with:
- Summary of the post
- Content angles (develop all applicable formats now)
- Reply opportunity flag (especially for mutuals)
- Content tree

For mutuals, always generate a suggested reply angle:

```markdown
### Reply opportunity
@{handle} posted about {topic}. Suggested reply angle: "{your take on their point}."
This is a mutual — high-value engagement.
```

### Step 6: Register in index.db

```bash
sqlite3 content/pipeline/index.db \
  "INSERT INTO items (id, created_at, source_type, ingest_source, status, current_title, original_url, raw_file)
   VALUES ('{ID}', '{datetime}', 'x-post', 'x-account-monitor', 'raw',
           '@{handle}: {first line}', '{url}', 'content/raw/x-posts/{filename}');"
```

### Step 7: Update _index.md

Add rows for each new item. Update the day's entry count.

### Step 8: Summary

```
X Account Monitor — 2026-03-07
─────────────────────────────────────────
Checked 12 accounts (8 monitor + 4 mutuals)

Captured 5 items:
  XM-001  @levelsio — pricing take (reply opportunity)
  XM-002  @karpathy — training data quality
  XM-003  @handle1 — mutuals reply opportunity
  XM-004  @sama — AI regulation take
  XM-005  @handle2 — mutuals reply opportunity

2 reply opportunities flagged (mutuals).
Ready for /content-interview.
```

---

## Prerequisites

`xquery` CLI must be in PATH with X API access configured. See the xquery skill for setup.
