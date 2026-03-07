---
name: capture-thought
description: Quickly capture a thought, take, or idea as a pipeline brief.
  Use when asked to "add a thought", "capture this", "I'm thinking about", or "thought:".
argument-hint: "[thought text]"
---

# Capture Thought

Fast-path skill for capturing raw thoughts into the content pipeline. No analysis, no conversation, no workshopping. Just create a brief, register the item, and confirm.

Every thought becomes a brief — the atomic unit of the pipeline. The brief starts minimal (just the core insight) and gets developed later during the interview stage.

---

## Process

### 1. Assign an ID

Query `index.db` for the highest CT number today:

```bash
sqlite3 content/pipeline/index.db \
  "SELECT id FROM items WHERE id LIKE '$(date +%Y%m%d)-CT-%' ORDER BY id DESC LIMIT 1;"
```

Increment by 1 (start at 001 if no results).

### 2. Write the brief

Create `content/briefs/{ID}.md`:

```markdown
---
id: {ID}
created: {YYYY-MM-DD}
source-type: thought
ingest-source: capture-thought
status: raw
format: {post | thread | article}
platform: Both
series-id:
generate: single
next-action: draft
---

## Core Insight
{The raw thought exactly as provided}

## Sources
- Captured directly

## Related Items
```

### 3. Register in index.db

```bash
sqlite3 content/pipeline/index.db \
  "INSERT INTO items (id, created_at, source_type, ingest_source, status, current_title, format, platform)
   VALUES ('{ID}', '$(date -u +%Y-%m-%dT%H:%M:%SZ)', 'thought', 'capture-thought', 'raw', '{short title}', '{format}', 'Both');"
```

### 4. Write inbox entry

Add to today's inbox file (`content/inbox/YYYY-MM-DD.md`), creating the file if needed:

```markdown
## [{ID}] {Short title}

**Status:** unreviewed
**Type:** thought
**Brief:** content/briefs/{ID}.md

### Summary
{One-sentence summary of the thought}

### Actions
- [ ] Review in content-interview
```

### 5. Update inbox index

Add a row to `content/inbox/_index.md`.

### 6. Confirm

One-line response: `Captured: {short title} → {ID}`

---

## Rules

1. **Be fast.** Don't rewrite, analyze, or expand the thought. Capture it verbatim as the Core Insight.
2. **Infer a short title** from the content (e.g., "AI agents should be narrow and deep"). Keep it under 60 chars.
3. **Infer format** based on length and complexity:
   - Short opinion or observation → `post`
   - Multi-part idea that needs unpacking → `thread`
   - Deep topic that needs research or long-form treatment → `article`
4. If the user provides multiple thoughts at once, capture each as a separate brief.
5. Never modify existing briefs.

---

## Series Connection Check

After capturing, do a quick (non-blocking) check:

1. Read `content/pipeline/series.md` — does this thought's topic connect to any active series?
2. Query `index.db` for recent items with similar topics:
   ```bash
   sqlite3 content/pipeline/index.db \
     "SELECT id, current_title FROM items WHERE source_type = 'thought' AND status IN ('raw','inbox') ORDER BY created_at DESC LIMIT 10;"
   ```

If a series connection is found, add a brief note after the confirmation:

```
Captured: AI agents should be narrow → 20260307-CT-001
(Connects to "The Refinement Era" series)
```

If 3+ related raw thoughts exist, suggest workshopping them:

```
Captured: AI agents should be narrow → 20260307-CT-003
You have 3 raw thoughts on agentic coding. Worth workshopping? Run /idea-dump to develop them together.
```

Keep this lightweight — one extra line maximum. The capture path must stay fast.

---

## Examples

User: "Add a thought: Most AI agents fail because they try to do too much. The best ones are narrow and deep."

Action:
1. Assign ID: `20260307-CT-001`
2. Write brief to `content/briefs/20260307-CT-001.md`
3. Register in `index.db` with `status: raw`, title: "AI agents should be narrow and deep"
4. Write inbox entry to `content/inbox/2026-03-07.md`
5. Update `content/inbox/_index.md`

Response: `Captured: AI agents should be narrow and deep → 20260307-CT-001`
