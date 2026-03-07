# Content Pipeline System — Full Architecture & Build Checklist

This is the canonical orchestration document for the content pipeline. It defines every component, how they connect, and what remains to be built. Any agent picking up work on this system should read this document first.

---

## System Overview

An autonomous content pipeline that ingests signals from multiple sources, develops them into content with human input at two checkpoints, and publishes on schedule. Designed to run on any agent platform (Claude Code, Claude Cowork, OpenClaw, cron) by storing all state in files and a SQLite index.

```
INGEST → DIGEST → INTERVIEW (human) → DRAFT → REFINE (human) → STAGE → PUBLISH
```

---

## Design Principles

### 1. State lives in files and SQLite, not in memory
Any agent can pick up where another left off. Content files (markdown) are the ground truth. The SQLite index (`index.db`) is a fast query layer that can be rebuilt from files.

### 2. IDs are stable and namespaced
Every item gets an ID at ingestion: `YYYYMMDD-{SOURCE}-NNN`. Source prefixes prevent collisions between concurrent agents. IDs follow items through every stage and every file. Titles can change; IDs never do.

| Prefix | Source |
|--------|--------|
| `BM` | bookmark-mining |
| `XM` | x-account-monitor |
| `RM` | reply-monitor |
| `YM` | youtube-monitor |
| `SR` | save-raw (manual) |
| `ID` | idea-dump |
| `RS` | research |
| `TU` | tutorial |

### 3. Develop everything now, sequence at queue time
Do not delay drafting because a format feels "longer-term." Stories get stale. All applicable formats (reply, post, thread, article) are developed immediately. When each piece gets posted is decided at the queue stage.

### 4. One signal, many outputs (content multiplication)
Every signal is evaluated for its full content tree: reply, post, thread, article, series connection. The default is to surface all opportunities, not just one.

### 5. SQLite + markdown hybrid
Content (raw files, briefs, drafts, articles) stays as markdown — human-readable, git-diffable. The index (`index.db`) is SQLite — concurrent-safe, queryable, fast. IDs also live in every file's frontmatter so the DB can be rebuilt.

### 6. Naming conventions sort correctly
- **Human-navigable containers** (inbox days, post weeks): `YYYY-{period}.md`
- **ID-bearing item files** (raw, briefs): `{ID}-{slug}.md`
- **Scratchpad files**: `YYYY-MM-DD-{slug}.md`
- **Articles**: `YYYY-MM-{slug}.md`
- All formats sort chronologically by filename.

---

## Directory Structure

```
life/
├── content/
│   ├── CLAUDE.md
│   ├── pipeline/                        # CONTROL PLANE
│   │   ├── README.md                    # User-facing system docs
│   │   ├── SYSTEM.md                    # This file — build checklist + agent instructions
│   │   ├── strategy.md                  # Content themes, voice, cadence targets
│   │   ├── sources.md                   # X accounts + YouTube channels to monitor
│   │   ├── series.md                    # Ongoing content series tracker
│   │   ├── queue.md                     # Approved posts pending scheduling
│   │   ├── history.md                   # Published content log (dedup)
│   │   ├── index.db                     # SQLite index (items + series tables)
│   │   ├── schema.sql                   # DB schema (source of truth for structure)
│   │   ├── migrations/                  # Schema migration scripts
│   │   └── cowork-tasks.md              # Cowork scheduled task setup + prompts
│   ├── inbox/                           # DAILY INTAKE
│   │   ├── _index.md                    # Item registry + day status
│   │   └── YYYY-MM-DD.md               # One file per day
│   ├── raw/                             # SOURCE MATERIAL (permanent)
│   │   ├── x-posts/
│   │   ├── x-articles/
│   │   ├── youtube/
│   │   └── web/
│   ├── briefs/                          # POST-INTERVIEW WORK ITEMS
│   │   └── YYYYMMDD-SRC-NNN.md
│   ├── posts/                           # SHORT-FORM DRAFTS
│   │   └── YYYY-W{NN}.md
│   ├── articles/
│   │   ├── drafts/
│   │   └── published/
│   └── images/
│       ├── prompts/
│       └── {slug}-og.png
├── research/
│   ├── .scratchpad/
│   └── reports/
├── tutorials/
│   ├── .scratchpad/
│   └── guides/
└── skills/                              # All skill definitions
    ├── sync.sh
    ├── content-pipeline/
    ├── content-digest/
    ├── content-interview/
    ├── content-refine/
    ├── write-post/
    ├── write-article/
    ├── article-image/
    ├── bookmark-mining/
    ├── x-account-monitor/
    ├── reply-monitor/
    ├── youtube-monitor/
    ├── save-raw/
    ├── idea-dump/
    ├── capture-thought/
    ├── research/
    ├── tutorial/
    ├── postbridge/
    └── db-rebuild/
```

---

## Database Schema

See `schema.sql` for the authoritative version.

```sql
CREATE TABLE items (
  id              TEXT PRIMARY KEY,   -- YYYYMMDD-SRC-NNN
  created_at      TEXT NOT NULL,
  source_type     TEXT,               -- x-post | x-article | youtube | web | research | thought | tutorial
  ingest_source   TEXT,               -- bookmark-mining | x-account-monitor | ... | research | tutorial
  status          TEXT NOT NULL DEFAULT 'raw',
                                      -- raw → inbox → approved → brief → draft → refined → queued → published
  current_title   TEXT,
  original_url    TEXT,
  raw_file        TEXT,               -- relative path from repo root
  brief_file      TEXT,
  draft_file      TEXT,
  series_id       TEXT,
  platform        TEXT,               -- Twitter | LinkedIn | Both
  format          TEXT,               -- post | thread | article | post+article | full-tree | reply
  published_at    TEXT,
  multiplier      TEXT,               -- single | full-tree
  notes           TEXT
);

CREATE TABLE series (
  id       TEXT PRIMARY KEY,
  title    TEXT NOT NULL,
  theme    TEXT,
  status   TEXT NOT NULL DEFAULT 'seeding'
);
```

---

## Pipeline Stages — Detailed

### Stage 1: Ingest (automated daily + manual)

All ingest agents share the same output contract:
1. Assign a namespaced ID by querying `index.db` for the highest number for that source prefix today
2. Write full source content to `content/raw/{type}/YYYYMMDD-SRC-NNN-{slug}.md` with standard frontmatter
3. Write summary + angles to `content/inbox/YYYY-MM-DD.md`
4. `INSERT` into `index.db`
5. Update `content/inbox/_index.md`

**Automated agents (daily 7:00 AM):**
- `bookmark-mining` — X bookmarks via xquery
- `x-account-monitor` — accounts from `sources.md` via xquery
- `reply-monitor` — replies to @danzakon via xquery
- `youtube-monitor` — channels from `sources.md`, transcript on approval

**Manual agents (on-demand):**
- `save-raw` — any URL or pasted content
- `idea-dump` — raw thought stream → clusters + multiplication
- `research` → `research/reports/` + inbox entry
- `tutorial` → `tutorials/guides/` + inbox entry (if content-worthy)

### Stage 2: Digest (automated, after ingest)

`content-digest` reads undigested inbox items, scores each against `strategy.md`, refines angles, checks `series.md` for connections, re-ranks by opportunity score. Updates `index.db` status from `raw` to `inbox`.

### Stage 3: Interview — Human Checkpoint 1

`content-interview` presents digested items one at a time. User reacts: share a take, pick an angle, choose format (post/thread/article/full-tree), or skip. Approved items get a brief written to `content/briefs/`. `index.db` status moves to `approved`.

### Stage 4: Draft (automated from briefs)

`write-post` and `write-article` read from briefs, generate platform variants + 3 alternative hooks + content tree assessment. Output to `content/posts/YYYY-W{NN}.md` or `content/articles/drafts/`. `index.db` status moves to `draft`.

### Stage 5: Refine — Human Checkpoint 2

`content-refine` presents drafts with alternative hooks. User can approve, pick a different hook, give edit instructions, or request a rewrite. Approved drafts move to `refined` in `index.db`.

### Stage 6: Stage (automated)

Moves refined items to `queue.md` with target dates, platform selection, dedup check. `index.db` status moves to `queued`.

### Stage 7: Publish (automated daily 7:30 AM)

Daily Cowork task reads `queue.md`, schedules via PostBridge API, logs to `history.md`. `index.db` status moves to `published`.

---

## Raw File Frontmatter Standard

Every raw file includes:

```yaml
---
id: YYYYMMDD-SRC-NNN
source-type: x-post | x-article | youtube | web | research | thought
ingest-source: bookmark-mining | x-account-monitor | reply-monitor | youtube-monitor | save-raw | idea-dump | research
original-url: https://...
author: @handle or name
captured: ISO 8601 UTC
---
```

---

## Inbox Entry Standard

Each entry in `inbox/YYYY-MM-DD.md`:

```markdown
## [YYYYMMDD-SRC-NNN] Title

**Status:** unreviewed | digested | reviewed | skipped
**Score:** N/10 (added by content-digest)
**Type:** content theme tag
**Urgency:** time-sensitive | evergreen | research-first
**Series:** series slug or none
**Lead angle:** the single strongest angle
**Original:** URL
**Raw file:** relative path

### Summary
2–3 sentences.

### Content angles (develop all applicable formats now)
1. **Hot take**: ...
2. **Practical**: ...
3. **Nuanced**: ...

### Content tree
- **Reply**: ...
- **Post**: ...
- **Thread**: ...
- **Article**: ...
- **Series**: ...

### Actions
- [ ] Review in content-interview
```

---

## Brief Standard

Each file in `content/briefs/`:

```yaml
---
id: YYYYMMDD-SRC-NNN
created: YYYY-MM-DD
source-type: ...
ingest-source: ...
status: approved
format: post | thread | article | post+article | full-tree | reply
platform: Both | Twitter | LinkedIn
series-id: slug or blank
generate: single | full-tree
---

## Core Insight
One sharp sentence.

## Your Take
Verbatim from the interview.

## Lead Angle
Selected angle.

## Content Tree
What to develop — all applicable.

## Draft Instructions
Specific guidance.

## Source
URL or raw file path.
```

---

## Content Multiplication

Every signal is assessed for its full content tree. Skills surface:
- 2–3 angle variations per item
- Series connections (check `series.md`)
- The full format spectrum (reply → post → thread → article)
- Related items already in the system
- Follow-up questions that deserve their own piece

The `idea-dump` skill clusters raw thoughts, identifies themes, and surfaces series opportunities. A single cluster can generate multiple briefs in one session.

---

## Build Checklist

### Foundation (DONE)
- [x] Directory structure created (inbox, raw, briefs, pipeline/migrations)
- [x] `sources.md` created (control plane — ingest config)
- [x] `series.md` created (content series tracker)
- [x] `schema.sql` created and `index.db` initialized
- [x] Series seeded (the-refinement-era)
- [x] `research/curiosity-reports/` renamed to `research/reports/`
- [x] All scratchpad files renamed to `YYYY-MM-DD` prefix
- [x] Post files renamed to `YYYY-W{NN}` format
- [x] CLAUDE.md files updated across repo
- [x] `content/pipeline/README.md` rewritten
- [x] `content/pipeline/SYSTEM.md` — this file

### New Skills (BUILD)
- [x] `idea-dump` — conversational content workshop
- [x] `youtube-monitor` — channel monitoring + transcript fetching (includes `fetch-transcript.py`)
- [x] `content-digest` — score + rank inbox items
- [x] `content-interview` — interactive inbox review → briefs
- [x] `save-raw` — manual URL/content ingest
- [ ] `content-refine` — iterative draft editing loop
- [ ] `x-account-monitor` — scrape sources.md X accounts via xquery
- [ ] `reply-monitor` — surface replies to @danzakon
- [ ] `db-rebuild` — reconstruct index.db from file frontmatter
- [x] `tutorial` — practical technical guide creation (parallel to research)

### Skill Rewrites (UPDATE)
- [ ] `content-pipeline` — full rewrite as session orchestrator
- [ ] `bookmark-mining` — output to raw/ + inbox + ID assignment
- [ ] `research` — inbox entry on completion + updated paths
- [ ] `capture-thought` — series connection check + YYYY-MM-DD date format
- [ ] `write-post` — read from briefs, content tree output, alt hooks
- [ ] `write-article` — read from briefs, content tree output
- [ ] `article-image` — 1200×628px, consistent style, PNG output

### Infrastructure (LATER)
- [ ] Populate `sources.md` with actual X accounts + YouTube channels
- [ ] Add Morning Ingest Cowork task (7:00 AM)
- [ ] Add Morning Digest Cowork task (7:30 AM)
- [ ] Update Daily Scheduler Cowork task (reference new paths)
- [ ] Update Weekly Review Cowork task (query index.db)
- [ ] Install `youtube-transcript-api` and test on a real video
- [ ] End-to-end test: idea-dump → brief → write-post → queue
- [ ] `tutorials/` folder structure created

---

## Agent Instructions

### For agents picking up build tasks:

1. Read this document (SYSTEM.md) for the full system design
2. Read `README.md` for user-facing documentation
3. Check the Build Checklist above — find an unchecked item
4. Read any existing skill files before rewriting them
5. Follow these conventions:
   - Skills live in `life/skills/{skill-name}/SKILL.md`
   - Scripts live inside the skill directory alongside `SKILL.md`
   - All ingest skills must follow the output contract (Step 1 of Ingest above)
   - All processing skills query/update `index.db` via `sqlite3` CLI
   - All content creation skills read from briefs when available
   - All date-stamped files use ISO format (`YYYY-MM-DD` or `YYYYMMDD` in IDs)
   - Post files use `YYYY-W{NN}.md`
6. After building, run `bash skills/sync.sh` to link new skills to all agents
7. Commit with descriptive messages following the repo's commit conventions
8. Update this checklist when tasks are completed

### For agents running the pipeline interactively:

1. Start with `/content-pipeline` — it reads system state and guides you
2. Or jump to any specific stage skill directly
3. Always check `index.db` for current item status before processing
4. Always update `index.db` after changing item status

---

## Control Plane Files Reference

| File | Purpose | Updated by |
|------|---------|------------|
| `strategy.md` | Content themes, voice, cadence | Human (periodically) |
| `sources.md` | X accounts, YouTube channels to monitor | Human (as needed) |
| `series.md` | Active content series and episodes | Skills + human |
| `queue.md` | Posts pending scheduling | content-pipeline, content-refine |
| `history.md` | Published content log | Daily scheduler Cowork task |
| `index.db` | All items + status | Every skill |
| `schema.sql` | DB schema definition | Human (on schema changes) |
| `cowork-tasks.md` | Cowork automation prompts | Human (on task changes) |
