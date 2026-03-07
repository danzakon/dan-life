---
name: content-pipeline
description: Orchestrate the content pipeline. Use when asked to "check my pipeline",
  "pipeline status", "what should I post", "queue this", "I want to create content",
  or any general content workflow question.
argument-hint: "[command, question, or just invoke to start a session]"
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
  - Grep
---

# Content Pipeline

Master orchestration skill. Reads system state, presents a guided session menu, and delegates to specialized skills. This is the starting point for any content work.

Read `content/pipeline/SYSTEM.md` for the full architecture. Read `content/pipeline/README.md` for user-facing docs.

---

## On Invocation

### Step 1: Read pipeline state

Query `index.db` and check key files to build a status snapshot:

```bash
# Item counts by status
sqlite3 content/pipeline/index.db \
  "SELECT status, COUNT(*) FROM items GROUP BY status ORDER BY
   CASE status
     WHEN 'raw' THEN 1 WHEN 'inbox' THEN 2 WHEN 'approved' THEN 3
     WHEN 'brief' THEN 4 WHEN 'draft' THEN 5 WHEN 'refined' THEN 6
     WHEN 'queued' THEN 7 WHEN 'published' THEN 8
   END;"

# Queue depth (days of content at 3 posts/day)
sqlite3 content/pipeline/index.db \
  "SELECT COUNT(*) FROM items WHERE status = 'queued';"

# Unreviewed inbox items
sqlite3 content/pipeline/index.db \
  "SELECT COUNT(*) FROM items WHERE status IN ('raw','inbox');"

# Items ready to draft
sqlite3 content/pipeline/index.db \
  "SELECT COUNT(*) FROM items WHERE status = 'approved';"

# Drafts waiting for review
sqlite3 content/pipeline/index.db \
  "SELECT COUNT(*) FROM items WHERE status = 'draft';"
```

Also check:
- `content/pipeline/queue.md` — how many posts are queued with target dates
- `content/.scratchpad/thought-bank-*.md` — count unused thoughts (entries with `Used: [ ]`)

### Step 2: Present status and session menu

Show a compact status report and offer actions:

```
Pipeline Status — 2026-03-07
─────────────────────────────────────────
  Inbox:    8 items waiting for review
  Approved: 2 briefs ready to draft
  Drafts:   3 awaiting refinement
  Queue:    5 posts (1.7 days at 3/day)
  Thoughts: 4 unused in thought bank

What do you want to do?

  A) Review inbox — go through 8 unreviewed items (/content-interview)
  B) Draft approved — write posts/articles from 2 briefs
  C) Refine drafts — review and polish 3 drafts (/content-refine)
  D) Idea dump — I have new thoughts to workshop
  E) Pull from sources — run bookmarks, account monitor, YouTube check
  F) Research a topic — deep dive into something specific
  G) Write a tutorial — create a step-by-step guide
  H) Save something — ingest a URL or paste content (/save-raw)
  I) Queue approved — move refined posts into the queue
  J) Pipeline health — full health report with recommendations
```

The menu adapts to state:
- If inbox is empty, don't offer A
- If no approved briefs, don't offer B
- If queue is low (< 3 days), flag it as urgent
- If queue is empty, flag as critical

Wait for user selection.

### Step 3: Delegate

Based on selection, invoke the appropriate skill or run the action inline:

| Selection | Action |
|-----------|--------|
| A | Invoke `content-interview` skill |
| B | Read approved briefs, invoke `write-post` / `write-article` for each |
| C | Invoke `content-refine` skill |
| D | Invoke `idea-dump` skill |
| E | Run ingest agents (bookmark-mining, x-account-monitor, etc.) |
| F | Invoke `research` skill |
| G | Invoke `tutorial` skill |
| H | Invoke `save-raw` skill |
| I | Run queue action (see below) |
| J | Run health report (see below) |

After the delegated action completes, return to the session menu with an updated status. Continue until the user is done.

---

## Queue Action (I)

Move refined posts into `queue.md`:

1. Query index.db for items with `status = 'refined'`
2. Read the draft file for each
3. For each post:
   a. **Dedup check:** Compare content against `history.md` and optionally `xquery x:user @danzakon --limit 20`
   b. **Assign target date:** Spread across upcoming days, respecting cadence from `strategy.md` (default: 3 posts/day)
   c. **Write to queue.md:**
      ```markdown
      ### [ ] {Hook/Title}

      **Content ID:** {ID}
      **Target date:** YYYY-MM-DD
      **Platform:** Both
      **Priority:** normal

      **Twitter:**
      {280-char content}

      **LinkedIn:**
      {context-heavy content}

      **Status:** queued
      ```
   d. **Update index.db:** `status = 'queued'`
4. Report what was queued and when

---

## Health Report (J)

Generate a comprehensive pipeline health report:

1. **Queue depth:** Posts queued, days of runway at cadence
2. **Bottlenecks:** Items stuck at each stage (e.g., 5 drafts waiting for refine)
3. **Thought bank:** Unused thought count, top themes
4. **Unconverted research:** Reports in `research/reports/` not yet in the pipeline (check index.db for items with source_type='research')
5. **Content mix:** Last 2 weeks of history.md vs. strategy.md theme distribution
6. **Series status:** Active series from series.md, episodes delivered vs. planned
7. **Recommendations:** 2–3 specific actions to take

```
Pipeline Health Report — 2026-03-07
─────────────────────────────────────────

Queue:       5 posts / 1.7 days runway — LOW
Bottleneck:  3 drafts stuck in "draft" (need /content-refine)
Thoughts:    4 unused across 1 month
Research:    2 reports unconverted to content
Series:      "The Refinement Era" — 2/4 episodes delivered

Content Mix (last 2 weeks):
  engineering-take:  4 (target: 4) OK
  hot-take:          3 (target: 3) OK
  practical-how-to:  0 (target: 2) MISSING
  tenex:             1 (target: 1) OK

Recommendations:
  1. Run /content-refine to clear the draft backlog
  2. Write a practical how-to post (underrepresented)
  3. Convert "AI agents in production" research report to content
```

---

## Direct Commands

These bypass the session menu for quick actions:

| Command | Action |
|---------|--------|
| "pipeline status" / "check my pipeline" | Jump to health report |
| "what should I post" | Query strategy + thought bank + inbox, suggest 3-5 ideas |
| "queue this" / "queue these" | Run queue action on specified or all refined posts |
| "I want to create content" | Full session menu |

---

## Workspace

All state lives in the life repo:

- `content/pipeline/SYSTEM.md` — full architecture and build checklist
- `content/pipeline/strategy.md` — content themes, voice, cadence
- `content/pipeline/sources.md` — X accounts + YouTube channels
- `content/pipeline/series.md` — content series tracker
- `content/pipeline/queue.md` — posts pending scheduling
- `content/pipeline/history.md` — published content log
- `content/pipeline/index.db` — SQLite index (items + series)
- `content/inbox/` — daily intake files
- `content/raw/` — source material by type
- `content/briefs/` — approved work items
- `content/posts/` — weekly post files (`YYYY-W{NN}.md`)
- `content/articles/` — long-form drafts and published
- `content/.scratchpad/thought-bank-YYYY-MM.md` — monthly thoughts
- `research/reports/` — research output
- `tutorials/guides/` — technical guides

---

## Prerequisites

`sqlite3` (pre-installed on macOS). All other dependencies are in the delegated skills.
