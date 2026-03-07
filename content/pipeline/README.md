# Content Pipeline System

End-to-end system for ingesting signals, developing ideas, and publishing content on Twitter/X and LinkedIn. Designed to run autonomously with two human checkpoints, and to maximize the content yield from every signal that enters the system.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│  STAGE 1: INGEST  (automated, daily 7:00 AM)                        │
│                                                                     │
│  bookmark-mining  x-account-monitor  reply-monitor  youtube-monitor │
│  save-raw (manual)  idea-dump (manual)  research (on-demand)        │
│                          │                                          │
│                          ▼                                          │
│  raw/{x-posts,x-articles,youtube,web}/   ← full source content      │
│  content/pipeline/index.db               ← item registered with ID  │
│  inbox/YYYY-MM-DD.md                     ← summary + angles linked  │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STAGE 2: DIGEST  (automated, after ingest)                         │
│                                                                     │
│  Scores and ranks inbox items against strategy.md                   │
│  Generates content angles for each item                             │
│  Flags series opportunities and content tree potential              │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
               ┌───────────▼───────────┐
               │  HUMAN CHECKPOINT 1   │
               │                       │
               │  /content-interview   │
               │                       │
               │  Review digest items  │
               │  Share your take      │
               │  Approve / skip       │
               └───────────┬───────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STAGE 3: DRAFT  (automated, runs on approved items)                │
│                                                                     │
│  Approved items → briefs/YYYYMMDD-NNN.md (one brief per item)       │
│  write-post → posts/W{n}-{m}-{y}.md                                 │
│  write-article → articles/drafts/                                   │
│  Content tree generated: post + variants + article angle + series   │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
               ┌───────────▼───────────┐
               │  HUMAN CHECKPOINT 2   │
               │                       │
               │  /content-refine      │
               │                       │
               │  Review drafts        │
               │  Iterate on hooks     │
               │  Approve for queue    │
               └───────────┬───────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STAGE 4: STAGE  (automated, runs on approved drafts)               │
│                                                                     │
│  Dedup check against history + recent X posts                       │
│  Assign target dates respecting cadence                             │
│  Write to queue.md                                                  │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STAGE 5: PUBLISH  (automated, daily 7:30 AM Cowork task)           │
│                                                                     │
│  Reads queue.md for today's posts                                   │
│  Schedules via PostBridge API (9am, 12pm, 3pm, 6pm ET)             │
│  Updates queue.md status + logs to history.md + updates index.db    │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Core Design Principles

### IDs

Every content item receives a stable ID the moment it enters the system. The ID never changes — it follows the item across every file and every stage.

**Format:** `YYYYMMDD-{SOURCE}-{NNN}`

```
20260307-BM-001    ← first bookmark-mining item on March 7
20260307-XM-003    ← third x-account-monitor item on March 7
20260307-RS-001    ← first research report registered on March 7
20260307-ID-002    ← second idea-dump item on March 7
```

Source prefixes:

| Prefix | Source |
|--------|--------|
| `BM` | bookmark-mining |
| `XM` | x-account-monitor |
| `RM` | reply-monitor |
| `YM` | youtube-monitor |
| `SR` | save-raw (manual) |
| `ID` | idea-dump |
| `RS` | research |

Each source maintains its own sequential counter. No coordination needed between concurrent agents — different namespaces cannot collide.

IDs appear in:
- Raw filenames: `raw/x-posts/20260307-BM-001-levelsio-pricing.md`
- Raw file frontmatter: `id: 20260307-BM-001`
- Inbox entries: `## [20260307-BM-001] @levelsio — Pricing`
- Brief filenames: `briefs/20260307-BM-001.md`
- Draft file frontmatter: `content-id: 20260307-BM-001`
- History log: `20260307-BM-001 | 2026-03-09 | Twitter | ...`

Titles can change at any stage. IDs never do.

### SQLite + Markdown Hybrid

- **Content files** (raw, briefs, drafts, articles) stay as markdown. Written by agents, edited by humans, git-tracked and diffable.
- **The index** (`content/pipeline/index.db`) is SQLite. Concurrent-safe, queryable, fast. Agents read from and write to it via the `sqlite3` CLI.
- **Frontmatter in every content file** contains the item's ID and key metadata. This makes the database reconstructable from files if it's ever lost or corrupted — run the `db:rebuild` skill.

### Content Multiplication

The default mindset is: one signal unlocks a content tree, not a single post. Every inbox item carries angle suggestions and a multiplication assessment. The interview step always offers to generate the full tree, not just one piece.

```
ONE SIGNAL → content tree (develop all applicable formats now)
  ├── Reply — draft and post immediately if time-sensitive
  ├── Post — draft now, queue for same day or next
  ├── Thread — draft now, can post same day as the post
  ├── Article — draft now, can go out same week
  └── Series — flag connection, plan next episodes

Sequencing when each piece gets posted happens at the queue stage.
Do not delay drafting because a format feels "longer-term."
Stories get stale. Develop everything that has merit immediately.
```

When generating any piece of content, skills always surface:
- 2–3 additional angle variations
- Whether this connects to an existing series in `series.md`
- Related content already in the system (by theme/tag)
- Follow-up questions this topic raises that deserve their own piece

---

## Directory Structure

```
life/
├── content/
│   ├── CLAUDE.md                        # Directory documentation
│   ├── pipeline/                        # CONTROL PLANE
│   │   ├── README.md                    # This file
│   │   ├── strategy.md                  # Content themes, voice, cadence targets
│   │   ├── sources.md                   # Accounts + channels to monitor
│   │   ├── series.md                    # Ongoing content series tracker
│   │   ├── queue.md                     # Approved posts pending scheduling
│   │   ├── history.md                   # Published content log (dedup)
│   │   ├── index.db                     # SQLite index (all items + state)
│   │   ├── schema.sql                   # DB schema source of truth
│   │   ├── migrations/                  # Schema migration scripts
│   │   └── cowork-tasks.md              # Cowork automation setup + prompts
│   │
│   ├── inbox/                           # DAILY INTAKE
│   │   ├── _index.md                    # Master item registry + day status
│   │   └── YYYY-MM-DD.md               # One file per day, links to raw/
│   │
│   ├── raw/                             # SOURCE MATERIAL (permanent record)
│   │   ├── x-posts/                     # Tweets and threads
│   │   ├── x-articles/                  # X long-form articles (browser-fetched)
│   │   ├── youtube/                     # Video transcripts
│   │   └── web/                         # Anything else: Substack, blogs, etc.
│   │
│   ├── briefs/                          # POST-INTERVIEW WORK ITEMS
│   │   └── YYYYMMDD-{SOURCE}-NNN.md    # One brief per approved item
│   │
│   ├── posts/                           # SHORT-FORM DRAFTS
│   │   └── W{week}-{month}-{year}.md
│   │
│   ├── articles/
│   │   ├── drafts/
│   │   └── published/
│   │
│   └── images/
│       ├── prompts/
│       └── {slug}-og.png
│
└── research/
    └── reports/                         # Research output (renamed from curiosity-reports)
```

---

## The Control Plane (`pipeline/`)

The pipeline folder contains ops configuration and live operational state. Skills read these files as config. Nothing in here is content — it's how the machine runs.

### `strategy.md`
Content themes, voice guidelines, platform tone differences, posting cadence targets, hot topics, and Tenex messaging. The north star for all content decisions. Update this as interests and priorities shift.

### `sources.md`
Configuration for all ingest agents. Defines which X accounts to monitor, which YouTube channels to watch, and optional keyword filters. Skills read this file at the start of every ingest run.

```markdown
## X Accounts — Monitor (all recent posts)
- @levelsio     # indie hacking, pricing
- @karpathy     # AI/ML

## X Accounts — Mutuals (priority reply flagging)
- @handle1
- @handle2

## YouTube Channels
- UCxxxxxxxx    # Lex Fridman — all videos
- UCyyyyyyyy    # MKBHD — keyword filter: AI, software
```

### `series.md`
Tracks ongoing content narratives. Skills check this when generating content to flag series connections and surface next-episode opportunities.

```markdown
## Active Series

### The Refinement Era
Theme: Quality over quantity in AI-assisted development
Episodes:
- [x] "Fewer details, all perfect" (post, 2026-02-28)
- [ ] "Vibe coding's dirty secret" (planned)
- [ ] Full article: "The Refinement Era of Software Engineering"
```

### `queue.md`
Approved posts awaiting scheduling. The daily Cowork task reads this file. Each entry has both platform variants, a target date, and a content ID for traceability.

### `history.md`
Everything published. Used for dedup checks and content mix analysis. Format: `| ID | Date | Platform | Type | Summary | Source |`

### `index.db`
SQLite database. The state machine for all content items. See the Database section below.

### `schema.sql`
The canonical schema definition, tracked in git. When the schema changes, this file is updated and a migration script is added to `migrations/`.

---

## Stage 1: Ingest

### Sourcing Agents

All ingest agents share the same output contract:
1. Write full source content to `raw/{type}/YYYYMMDD-{SOURCE}-NNN-{slug}.md`
2. Write a summary entry to `inbox/YYYY-MM-DD.md`
3. Register the item in `index.db`
4. Update `inbox/_index.md`

**Automated (daily 7:00 AM Cowork task — runs all four):**

| Agent | Status | Source | Tool |
|-------|--------|--------|------|
| `bookmark-mining` | update existing | X bookmarks | xquery |
| `x-account-monitor` | build | `sources.md` X accounts | xquery |
| `reply-monitor` | build | Replies to @danzakon | xquery |
| `youtube-monitor` | build | `sources.md` channels | yt-dlp |

**Manual / on-demand:**

| Agent | Status | Purpose |
|-------|--------|---------|
| `save-raw` | build | Ingest any URL or pasted content |
| `idea-dump` | build | Parse raw thought stream (Notes export, voice-to-text) |
| `research` | update existing | Deep research → `research/reports/` + inbox entry |

### Raw File Format

Every raw file has a standard frontmatter header regardless of content type:

```yaml
---
id: 20260307-BM-001
source-type: x-post          # x-post | x-article | youtube | web | research | thought
ingest-source: bookmark-mining
original-url: https://x.com/levelsio/status/...
author: @levelsio
captured: 2026-03-07T07:23Z
---

[Full source content here — never truncated]
```

### Inbox Entry Format

Each entry in `inbox/YYYY-MM-DD.md` is a summary with angles. No raw content — that lives in `raw/`. The inbox stays scannable.

```markdown
## [20260307-BM-001] @levelsio — Pricing SaaS products

**Status:** unreviewed
**Type:** x-post
**Original:** https://x.com/levelsio/status/...
**Raw file:** content/raw/x-posts/20260307-BM-001-levelsio-pricing.md
**Ingest source:** bookmark-mining

### Summary
Two-sentence summary of what the source material actually says.

### Content angles
1. **Hot take**: The contrarian read — disagree with the premise
2. **Practical**: Actionable spin for engineers or founders
3. **Nuanced**: "Yes, but here's what most people miss"
4. **Series fit**: Connects to "The Refinement Era" series

### Content tree (develop all applicable formats now)
- **Reply**: Reply to @levelsio directly — agree/push back
- **Post**: Standalone hot take on pricing psychology
- **Thread**: 5 pricing mistakes founders make
- **Article**: "The pricing trap no one talks about"
- **Series**: Yes — adds to "Product Thinking" theme

### Actions
- [ ] Reply to original
- [ ] Write standalone post
- [ ] Research deeper → article
- [ ] Skip
```

### Handling Content You Can't Scrape

X articles, paywalled posts, and anything requiring a real browser can't be ingested automatically. Use `save-raw`:

1. Paste the URL (and optionally the text) into a Claude session
2. `save-raw` formats it correctly and writes to `raw/x-articles/` or `raw/web/`
3. Inbox entry is created automatically

For Claude Cowork with the browser extension: navigate to the article, then trigger `save-raw` and it will read the DOM directly.

---

## Stage 2: Digest

The `content-digest` skill runs after ingest. It:
- Reads all `unreviewed` items from the current day's inbox file
- Scores each item for relevance against `strategy.md` hot topics
- Re-ranks items by opportunity score
- Generates or refines content angles
- Checks `series.md` for connections
- Marks the inbox file as `digested`

Skills read the `_index.md` to find which days have unreviewed items. The digest doesn't change the structure of inbox files — it adds scores and refines angles in-place.

---

## Stage 3: Interview (Human Checkpoint 1)

Run `/content-interview` to start a review session.

The skill:
1. Reads `inbox/_index.md` to find the most recent unreviewed or digested inbox file
2. Presents items one at a time: summary + angles + original URL
3. Captures your reaction as a thought capture (adds to the brief)
4. Asks: "Generate just this piece, or the full content tree?"
5. Marks approved items in `index.db` (`status: approved`)
6. Creates `briefs/YYYYMMDD-{SOURCE}-NNN.md` for each approved item
7. Marks inbox entry as `reviewed`

**Brief format:**

```markdown
---
id: 20260307-BM-001
source: content/raw/x-posts/20260307-BM-001-levelsio-pricing.md
inbox-entry: content/inbox/2026-03-07.md#20260307-BM-001
created: 2026-03-07
format: post          # post | thread | article | post+article
platform: Both
series: the-refinement-era
generate: full-tree   # single | full-tree
---

## Your Take
[Captured from the interview — your exact reaction and angle]

## Angle Selected
Practical: Actionable spin for engineers on pricing psychology

## Draft Instructions
[Any specific direction: tone, length, hooks to try, things to avoid]
```

---

## Stage 4: Draft

After interview, approved briefs are automatically picked up by `write-post` and/or `write-article`. Skills read the brief and the raw source file, then generate:

- **Twitter/X variant** (280 chars, thread if needed)
- **LinkedIn variant** (context-heavy, up to 3000 chars)
- **Article outline** (if `format` includes article)
- **2–3 alternative hooks** (always — for refine step to choose from)

Output lands in `posts/W{n}-{m}-{y}.md` or `articles/drafts/`, with the `content-id` frontmatter field set to the item's ID for traceability.

---

## Stage 5: Refine (Human Checkpoint 2)

Run `/content-refine` to review generated drafts.

The skill presents each new draft with its alternative hooks. You can:
- Approve as-is
- Pick an alternative hook
- Give specific edit instructions ("make the LinkedIn version more direct")
- Request a full rewrite with different angle

Approved drafts move to `status: queued` in `index.db`. The item is now ready for staging.

---

## Stage 6: Stage

The staging step (part of `content-pipeline`) moves approved drafts into `queue.md` with:
- Target date (spread across days at cadence pace)
- Platform selection
- Dedup check against `history.md` and recent X posts
- Content ID for the history log

---

## Stage 7: Publish

Handled by the daily Cowork task (7:30 AM). See `cowork-tasks.md` for the exact prompt. Posts are scheduled via the PostBridge API. History is updated. `index.db` status moves to `published`.

Articles are staged by the weekly Monday Cowork task and published manually as X Articles.

---

## Content Multiplication

Every signal that enters should be treated as a potential content tree, not a single post. These defaults are built into the digest and interview stages:

**Always surface:**
- 2–3 angle variations per item (not just one direction)
- Series connections (check `series.md` for existing threads)
- The full content tree (post → thread → article progression)
- Related items already in the system (by theme)
- Follow-up questions this topic raises

**Idea Dump (`/idea-dump`):**
Paste raw stream-of-consciousness notes — from the Notes app, voice-to-text, anything. The skill:
1. Parses individual thoughts
2. Clusters related ideas by theme
3. Flags series opportunities
4. Writes each thought to the thought bank
5. Creates inbox entries for clusters with high multiplication potential

```
idea-dump input (raw):
  "vibe coding creating complexity explosion... Dorsey fewer details...
   junior devs shipping faster but quality..."

Output:
  Cluster: "Complexity vs quality in AI-assisted coding" (3 items)
  → Thought bank: 3 individual entries
  → Inbox: 1 cluster entry with full content tree
  Series trigger: "The Refinement Era" — 3 new episodes suggested
```

**Series Tracker (`series.md`):**
When a theme appears across 3+ items, promote it to an active series. Series give a content calendar structure: each episode is planned, tracked, and crosslinked to previous episodes when published.

---

## Database Schema

```sql
-- See schema.sql for authoritative version
-- Current: v1

CREATE TABLE items (
  id              TEXT PRIMARY KEY,   -- e.g., 20260307-BM-001
  created_at      TEXT NOT NULL,
  source_type     TEXT,               -- x-post | x-article | youtube | web | research | thought
  ingest_source   TEXT,               -- bookmark-mining | x-account-monitor | etc.
  status          TEXT,               -- raw | inbox | approved | brief | draft | refined | queued | published
  current_title   TEXT,               -- mutable, always reflects latest working title
  original_url    TEXT,
  raw_file        TEXT,               -- relative path from repo root
  brief_file      TEXT,
  draft_file      TEXT,               -- path + optional #anchor for items inside weekly files
  series_id       TEXT,               -- FK to series.id
  platform        TEXT,               -- Twitter | LinkedIn | Both
  format          TEXT,               -- post | thread | article | post+article
  published_at    TEXT,
  multiplier      TEXT                -- single | full-tree (what was generated)
);

CREATE TABLE series (
  id       TEXT PRIMARY KEY,          -- e.g., the-refinement-era
  title    TEXT,
  theme    TEXT,
  status   TEXT                       -- active | paused | complete
);
```

**Common queries:**

```bash
# Items ready for interview
sqlite3 content/pipeline/index.db \
  "SELECT id, current_title FROM items WHERE status = 'inbox' ORDER BY created_at DESC;"

# Items ready for drafting
sqlite3 content/pipeline/index.db \
  "SELECT id, current_title, raw_file FROM items WHERE status = 'approved';"

# Full pipeline status
sqlite3 content/pipeline/index.db \
  "SELECT status, COUNT(*) FROM items GROUP BY status;"

# Everything in a series
sqlite3 content/pipeline/index.db \
  "SELECT id, current_title, status FROM items WHERE series_id = 'the-refinement-era';"

# Lookup by ID
sqlite3 content/pipeline/index.db \
  "SELECT * FROM items WHERE id = '20260307-BM-001';"
```

**Recovery (`db:rebuild`):**
If `index.db` is lost or corrupted, the skill scans all markdown files in `raw/`, `briefs/`, `posts/`, and `articles/`, reads their frontmatter IDs, and reconstructs the database. The content files are the ground truth; the DB is a fast query layer on top.

---

## Skills Reference

### Ingest
| Skill | Status | Trigger | What it does |
|-------|--------|---------|--------------|
| `bookmark-mining` | update | automated / "check bookmarks" | Pulls X bookmarks → `raw/x-posts/` + inbox |
| `x-account-monitor` | build | automated | Scrapes accounts in `sources.md` → raw + inbox |
| `reply-monitor` | build | automated | Pulls replies to @danzakon → raw + inbox |
| `youtube-monitor` | build | automated | Checks channels in `sources.md` → inbox; pulls transcript on approval |
| `save-raw` | build | "fetch this: {url}" | Manually ingest any URL or pasted content |
| `idea-dump` | build | "idea dump: {text}" | Parse raw thought stream → thought bank + inbox clusters |
| `research` | update | "research {topic}" | Deep research → `research/reports/` + inbox entry |

### Process
| Skill | Status | Trigger | What it does |
|-------|--------|---------|--------------|
| `content-digest` | build | automated | Scores and ranks inbox items, refines angles |
| `content-interview` | build | "/content-interview" | Interactive item review, brief creation |
| `content-pipeline` | update | "/content-pipeline" | Master orchestration: status, ideas, queue |

### Create
| Skill | Status | Trigger | What it does |
|-------|--------|---------|--------------|
| `write-post` | update | automated / "write a post" | Generates post variants + alternative hooks + content tree |
| `write-article` | update | automated / "write an article" | Long-form draft from brief or topic |
| `content-refine` | build | "/content-refine" | Iterative draft review and editing |
| `article-image` | exists | "generate thumbnail" | Creates 1200x675 article header image |
| `capture-thought` | update | "add a thought: {idea}" | Quick capture + series connection check |

### Publish
| Skill | Status | Trigger | What it does |
|-------|--------|---------|--------------|
| `postbridge` | exists | automated / "schedule this" | PostBridge API scheduling |

---

## Automation (Cowork Scheduled Tasks)

See `cowork-tasks.md` for exact setup instructions and prompts.

| Task | Schedule | What it does |
|------|----------|--------------|
| Morning Ingest | 7:00 AM daily | Runs all 4 ingest agents (bookmarks, accounts, replies, YouTube) |
| Morning Digest | 7:30 AM daily | Scores and ranks new inbox items |
| Daily Scheduler | 7:30 AM daily | Schedules today's queued posts via PostBridge |
| Weekly Article Prep | Monday 9:00 AM | Stages `status: ready` articles, generates thumbnails |
| Weekly Review | Friday 4:00 PM | Pipeline health report, queue depth, content mix analysis |

---

## Human Workflow Cadence

**Anytime (~10 sec):**
- "Add a thought: {idea}" — instant capture

**Daily or every few days (~20–30 min):**
- Run `/content-interview` — review the latest digest, share your takes, approve items
- Run `/content-refine` — review generated drafts, approve for queue

**On-demand:**
- "Idea dump: {paste notes}" — convert raw thoughts into pipeline items
- "Research {topic}" — kick off a deep research session
- "Fetch this: {url}" — manually ingest a specific piece of content

**Weekly (~5 min):**
- Review staged articles (Monday notification from Cowork)
- Read the Friday health report

Everything else — ingest, digest, scheduling, history tracking, dedup — runs automatically.

---

## Adding New Sources

**New X account to monitor:**
Add a line to `sources.md` under the appropriate section. The next morning ingest run will pick it up.

**New YouTube channel:**
Add the channel ID to `sources.md` with an optional keyword filter. The youtube-monitor will surface new videos from it.

**One-off content (article, blog post, X article):**
Use `save-raw` with the URL. Content is ingested, formatted, and added to the inbox immediately.

---

## Recovery

**If `index.db` is corrupted or deleted:**
Run `/db:rebuild`. The skill scans all content files for frontmatter IDs and reconstructs the database from the markdown source of truth.

**If inbox or content files are accidentally deleted:**
Restore from git: `git restore content/inbox/` or `git restore content/raw/`.

**If a Cowork task fails:**
All tasks are idempotent — re-running them produces the same result without duplication. Check that the working folder is set to `~/dev/life/` and required environment variables (`POST_BRIDGE_API_KEY`) are accessible.
