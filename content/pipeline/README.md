# Content Pipeline System

End-to-end system for ingesting signals, developing ideas, and publishing content on Twitter/X and LinkedIn. Designed to run autonomously with two human checkpoints, and to maximize the content yield from every signal that enters the system.

---

## Architecture

```
INGEST → DIGEST → INTERVIEW (human) → DRAFT → REFINE (human) → STAGE → PUBLISH
```

```
┌─────────────────────────────────────────────────────────────────────┐
│  STAGE 1: INGEST  (automated daily + manual on-demand)              │
│                                                                     │
│  bookmark-mining  x-account-monitor  reply-monitor  youtube-monitor │
│  watch-later-mining  save-raw  idea-dump  capture-thought           │
│  research  tutorial                                                 │
│                          │                                          │
│                          ▼                                          │
│  raw/{type}/              ← full source content (when applicable)   │
│  briefs/YYYYMMDD-SRC-NNN.md  ← every item gets a brief             │
│  pipeline/index.db        ← item registered with ID                 │
│  inbox/YYYY-MM-DD.md      ← summary + angles                       │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STAGE 2: DIGEST  (automated, after ingest)                         │
│                                                                     │
│  Scores and ranks inbox items against strategy.md                   │
│  Refines content angles for each item                               │
│  Flags series opportunities and content tree potential               │
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
│  write-post → posts/YYYY-W{NN}.md                                   │
│  write-article → articles/drafts/                                   │
│  Content tree generated: post + variants + article + series         │
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
│  Schedules via PostBridge API (9am, 12pm, 3pm, 6pm ET)              │
│  Updates queue.md status + logs to history.md + updates index.db    │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Design Principles

### 1. Inbox and briefs serve different purposes

**Inbox entries** are for triage. They represent content that arrived passively — a bookmark saved, a YouTube video from a monitored channel, a post from an X account. You haven't reacted yet. The inbox entry is the agent surfacing what's worth your attention: a summary, the strongest angles, timestamps for long-form content. It's a lead, not a commitment. The content-interview session is where you react.

**Briefs** are work orders. They contain your take, your selected angle, and instructions for drafting. The agent can write from a brief immediately. A brief is created when you commit to developing an idea — either during content-interview (for passive ingest) or directly (for idea-dump, capture-thought, or when you already have a take from watching/reading something).

The practical distinction: **inbox = "I received this"** / **brief = "I decided this"**.

Some sources skip the inbox entirely and write a brief directly, because you're already in an active session with a take:

| Flow | Through inbox? | Why |
|------|---------------|-----|
| bookmark-mining, X monitors, youtube-monitor, watch-later-mining | Yes | Passive ingest — you haven't reacted yet |
| idea-dump | No | You're in a live workshop session, take is captured in real time |
| capture-thought | No | You have the thought right now; no triage needed |
| save-raw (manual URL + "workshop now") | Optional | You can go direct to brief if you already have a take |

Everything that enters the system gets an ID and a database entry regardless. The brief may start minimal (just frontmatter + core insight from the agent's read) and get developed during interview, or it may be fully written in one session. No side channels, no untracked parking lots.

### 2. IDs are stable and namespaced

Every item receives an ID at ingestion: `YYYYMMDD-{SOURCE}-NNN`. Source prefixes prevent collisions between concurrent agents. IDs follow items across every file and every stage. Titles can change; IDs never do.

```
20260307-BM-001    ← first bookmark-mining item on March 7
20260307-CT-003    ← third capture-thought item on March 7
20260307-ID-001    ← first idea-dump item on March 7
```

| Prefix | Source |
|--------|--------|
| `BM` | bookmark-mining |
| `XM` | x-account-monitor |
| `RM` | reply-monitor |
| `YM` | youtube-monitor |
| `WL` | watch-later-mining |
| `SR` | save-raw (manual) |
| `CT` | capture-thought |
| `ID` | idea-dump |
| `RS` | research |
| `TU` | tutorial |

Each source maintains its own sequential counter per day. No coordination needed between concurrent agents — different namespaces cannot collide.

IDs appear in:
- Brief filenames: `briefs/20260307-BM-001.md`
- Raw filenames: `raw/x-posts/20260307-BM-001-levelsio-pricing.md`
- File frontmatter: `id: 20260307-BM-001`
- Inbox entries: `## [20260307-BM-001] @levelsio — Pricing`
- Draft frontmatter: `content-id: 20260307-BM-001`
- History log: `20260307-BM-001 | 2026-03-09 | Twitter | ...`

### 3. State lives in files and SQLite, not in memory

Any agent can pick up where another left off. Content files (markdown) are the ground truth. The SQLite index (`index.db`) is a fast query layer that can be rebuilt from files via the `db-rebuild` skill.

### 4. Develop everything now, sequence at queue time

Do not delay drafting because a format feels "longer-term." Stories get stale. All applicable formats (reply, post, thread, article) are developed immediately. When each piece gets posted is decided at the queue stage.

### 5. One signal, many outputs (content multiplication)

Every signal is evaluated for its full content tree: reply, post, thread, article, series connection. The default is to surface all opportunities, not just one. Spinoff ideas become new briefs linked to the parent via the Related Items field.

```
ONE SIGNAL → content tree (develop all applicable formats now)
  ├── Reply — draft and post immediately if time-sensitive
  ├── Post — draft now, queue for same day or next
  ├── Thread — draft now, can post same day as the post
  ├── Article — draft now, can go out same week
  └── Series — flag connection, plan next episodes

Sequencing when each piece gets posted happens at the queue stage.
```

### 6. Naming conventions sort correctly

- **Weekly containers** (posts): `YYYY-W{NN}.md`
- **ID-bearing item files** (raw, briefs): `{ID}-{slug}.md`
- **Articles**: `YYYY-MM-{slug}.md`
- **Inbox days**: `YYYY-MM-DD.md`
- All formats sort chronologically by filename.

---

## Directory Structure

```
content/
├── CLAUDE.md                        # Directory conventions (file naming, formats)
├── pipeline/                        # CONTROL PLANE
│   ├── README.md                    # This file — full system documentation
│   ├── strategy.md                  # Content themes, voice, cadence targets
│   ├── sources.md                   # X accounts + YouTube channels to monitor
│   ├── series.md                    # Ongoing content series tracker
│   ├── queue.md                     # Approved posts pending scheduling
│   ├── history.md                   # Published content log (dedup)
│   ├── index.db                     # SQLite index (all items + state)
│   ├── schema.sql                   # DB schema source of truth
│   ├── migrations/                  # Schema migration scripts
│   └── cowork-tasks.md              # Cowork automation setup + prompts
├── inbox/                           # DAILY INTAKE
│   ├── _index.md                    # Master item registry + day status
│   └── YYYY-MM-DD.md               # One file per day, links to raw/
├── raw/                             # SOURCE MATERIAL (permanent record)
│   ├── x-posts/                     # Tweets and threads
│   ├── x-articles/                  # X long-form articles
│   ├── youtube/                     # Video transcripts
│   └── web/                         # Substack, blogs, anything else
├── briefs/                          # WORK ITEMS (the atomic unit)
│   └── YYYYMMDD-{SRC}-NNN.md       # One brief per item
├── posts/                           # SHORT-FORM DRAFTS
│   └── YYYY-W{NN}.md               # Weekly files, multiple posts each
├── articles/
│   ├── drafts/                      # Work in progress
│   └── published/                   # Live articles
└── images/
    ├── prompts/                     # Image generation prompts
    └── {slug}-og.png                # Article header images
```

---

## The Control Plane (`pipeline/`)

Configuration and operational state. Skills read these files as config. Nothing here is content — it's how the machine runs.

| File | Purpose | Updated by |
|------|---------|------------|
| `strategy.md` | Content themes, voice, cadence, hot topics | Human (periodically) |
| `sources.md` | X accounts + YouTube channels to monitor | Human (as needed) |
| `series.md` | Active content series and episodes | Skills + human |
| `queue.md` | Posts pending scheduling | content-pipeline, content-refine |
| `history.md` | Published content log (dedup reference) | Daily scheduler |
| `index.db` | All items + status (query layer) | Every skill |
| `schema.sql` | DB schema definition (git-tracked) | Human (on schema changes) |
| `cowork-tasks.md` | Cowork automation prompts | Human (on task changes) |

### `strategy.md`
Content themes, voice guidelines, platform tone differences, posting cadence targets, hot topics, and Tenex messaging. The north star for all content decisions.

### `sources.md`
Configuration for ingest agents. Defines which X accounts to monitor, which YouTube channels to watch, and optional keyword filters. Skills read this at the start of every ingest run.

### `series.md`
Tracks ongoing content narratives. Skills check this when generating content to flag series connections and surface next-episode opportunities.

### `queue.md`
Approved posts awaiting scheduling. The daily Cowork task reads this file. Each entry has both platform variants, a target date, and a content ID for traceability.

### `history.md`
Everything published. Used for dedup checks and content mix analysis.

Format: `| ID | Date | Platform | Type | Summary | Source |`

---

## Pipeline Stages

### Stage 1: Ingest

All ingest agents share the same output contract:

1. **Assign a namespaced ID** — query `index.db` for the highest number for that source prefix today, increment
2. **Write source content** to `raw/{type}/YYYYMMDD-SRC-NNN-{slug}.md` (when applicable — some sources like capture-thought have no raw file)
3. **Register in `index.db`** — INSERT with `status: 'raw'`
4. **Write inbox entry** to `inbox/YYYY-MM-DD.md` (passive ingest sources: bookmark-mining, X monitors, youtube-monitor, watch-later-mining, save-raw, research, tutorial)
   — OR —
   **Write a brief directly** to `briefs/YYYYMMDD-SRC-NNN.md` (active session sources: idea-dump, capture-thought)
5. **Update `inbox/_index.md`**

Passive sources write an inbox entry; the brief is created later during content-interview when you give your take. Active session sources write the brief immediately because your take is captured in real time.

**Automated (daily 7:00 AM Cowork task):**

| Agent | Source | Tool |
|-------|--------|------|
| `bookmark-mining` | X bookmarks | xquery |
| `x-account-monitor` | `sources.md` X accounts | xquery |
| `reply-monitor` | Replies to @danzakon | xquery |
| `youtube-monitor` | `sources.md` channels | ytquery |
| `watch-later-mining` | YouTube Watch Later | ytquery |

**Manual / on-demand:**

| Agent | Purpose |
|-------|---------|
| `capture-thought` | Single thought → brief (instant, no conversation) |
| `idea-dump` | Raw thought stream → workshop → multiple briefs |
| `save-raw` | Ingest any URL or pasted content |
| `research` | Deep research → `research/reports/` + brief |
| `tutorial` | Technical guide → `tutorials/guides/` + brief |

#### Raw File Frontmatter

Every raw file includes standard frontmatter:

```yaml
---
id: 20260307-BM-001
source-type: x-post          # x-post | x-article | youtube | web | research | thought | tutorial
ingest-source: bookmark-mining
original-url: https://x.com/levelsio/status/...
author: @levelsio
captured: 2026-03-07T07:23Z
---

[Full source content — never truncated]
```

#### Inbox Entry Format

Each entry in `inbox/YYYY-MM-DD.md` is a summary with angles. No raw content — that lives in `raw/`. The inbox stays scannable.

```markdown
## [20260307-BM-001] @levelsio — Pricing SaaS products

**Status:** unreviewed
**Type:** x-post
**Urgency:** time-sensitive | evergreen | research-first
**Series:** series slug or none
**Lead angle:** the single strongest angle
**Original:** https://x.com/levelsio/status/...
**Raw file:** content/raw/x-posts/20260307-BM-001-levelsio-pricing.md
**Brief:** content/briefs/20260307-BM-001.md

### Summary
Two-sentence summary of what the source material actually says.

### Content angles (develop all applicable formats now)
1. **Hot take**: The contrarian read
2. **Practical**: Actionable spin for engineers or founders
3. **Nuanced**: "Yes, but here's what most people miss"

### Content tree
- **Reply**: Reply to @levelsio directly
- **Post**: Standalone hot take
- **Thread**: 5 pricing mistakes founders make
- **Article**: "The pricing trap no one talks about"

### Actions
- [ ] Review in content-interview
```

#### Brief Format

Every item in the system has a brief. Briefs range from minimal (a captured thought) to fully developed (post-interview with angles, instructions, and content tree).

```yaml
---
id: YYYYMMDD-SRC-NNN
created: YYYY-MM-DD
source-type: x-post | x-article | youtube | web | research | thought | tutorial
ingest-source: bookmark-mining | capture-thought | idea-dump | ...
status: raw | inbox | approved | draft | refined | queued | published
format: post | thread | article | post+article | full-tree | reply
platform: Both | Twitter | LinkedIn
series-id: slug or blank
generate: single | full-tree
next-action: draft | research | tutorial | series-seed
---

## Core Insight
One sharp sentence. (May be minimal for raw captures, developed during interview.)

## Your Take
Verbatim from the interview — your angle, voice, direction. (Added during interview stage.)

## Lead Angle
Selected angle from the breakdown. (Added during interview stage.)

## Content Tree
What formats to develop — all applicable. (Added during interview stage.)

## Draft Instructions
Specific guidance: tone, hooks to try, things to avoid. (Added during interview stage.)

## Sources
- Raw file: content/raw/{type}/{ID}-{slug}.md
- Research: research/reports/{filename}.md
- External: https://...

## Related Items
- {ID} — {title or note, if any existing pipeline items connect}
```

For a quick thought via `capture-thought`, only the frontmatter and Core Insight are populated. Everything else gets filled in during the interview stage.

### Stage 2: Digest

The `content-digest` skill runs after ingest:

- Reads all `unreviewed` items from the current day's inbox file
- Scores each item for relevance against `strategy.md` hot topics
- Re-ranks items by opportunity score
- Refines content angles
- Checks `series.md` for connections
- Updates `index.db` status from `raw` to `inbox`

### Stage 3: Interview (Human Checkpoint 1)

Run `/content-interview` to start a review session.

The skill:
1. Reads `inbox/_index.md` to find the most recent unreviewed or digested inbox file
2. Presents items one at a time: summary + angles + original URL
3. Captures your reaction (adds to the brief's "Your Take" section)
4. Asks: "Generate just this piece, or the full content tree?"
5. Updates the brief with selected angle, format, draft instructions
6. Marks approved items in `index.db` (`status: approved`)
7. Marks inbox entry as `reviewed`

### Stage 4: Draft

After interview, approved briefs are picked up by `write-post` and/or `write-article`. Skills read the brief and the raw source file, then generate:

- **Twitter/X variant** (280 chars, thread if needed)
- **LinkedIn variant** (context-heavy, up to 3000 chars)
- **Article outline** (if format includes article)
- **2-3 alternative hooks** (always — for refine step to choose from)

Output lands in `posts/YYYY-W{NN}.md` or `articles/drafts/`, with `content-id` frontmatter set to the item's ID. `index.db` status moves to `draft`.

### Stage 5: Refine (Human Checkpoint 2)

Run `/content-refine` to review generated drafts.

The skill presents each new draft with its alternative hooks. You can:
- Approve as-is
- Pick an alternative hook
- Give specific edit instructions ("make the LinkedIn version more direct")
- Request a full rewrite with a different angle

Approved drafts move to `status: refined` in `index.db`.

### Stage 6: Stage

Moves refined items to `queue.md` with:
- Target date (spread across days at cadence pace)
- Platform selection
- Dedup check against `history.md` and recent X posts
- Content ID for traceability

`index.db` status moves to `queued`.

### Stage 7: Publish

Handled by the daily Cowork task (7:30 AM). Posts are scheduled via the PostBridge API. History is updated. `index.db` status moves to `published`.

Articles are staged by the weekly Monday Cowork task and published manually as X Articles.

See `cowork-tasks.md` for exact automation prompts.

---

## Content Multiplication

Every signal that enters should be treated as a potential content tree, not a single post. These defaults are built into the digest and interview stages.

**Always surface:**
- 2-3 angle variations per item
- Series connections (check `series.md`)
- The full content tree (reply → post → thread → article)
- Related items already in the system (by theme)
- Follow-up questions this topic raises

**Spinoffs become briefs.** When developing an idea surfaces follow-up questions or related angles that deserve their own piece, those become new briefs linked to the parent via the Related Items field. No side channels.

**Series Tracker (`series.md`):** When a theme appears across 3+ items, promote it to an active series. Series give a content calendar structure: each episode is planned, tracked, and crosslinked to previous episodes when published.

**Idea Dump (`/idea-dump`):** For bulk thought processing. Paste raw stream-of-consciousness notes — from the Notes app, voice-to-text, anything. The skill parses individual ideas, workshops angles with you, and creates a brief for each approved idea. Spinoffs become linked briefs.

---

## Database

The schema is defined in `schema.sql` (the source of truth). The database is `index.db`.

**Status flow:**

```
raw → inbox → approved → draft → refined → queued → published
```

| Status | Set by | Meaning |
|--------|--------|---------|
| `raw` | Ingest skill | Item registered, brief created |
| `inbox` | content-digest | Scored, ranked, angles refined |
| `approved` | content-interview | User approved; brief fully developed |
| `draft` | write-post / write-article | Content drafted with variants |
| `refined` | content-refine | User approved draft |
| `queued` | content-pipeline (stage) | In queue.md with target date |
| `published` | Daily scheduler | Posted via PostBridge, logged in history.md |

**Common queries:**

```bash
# Pipeline status overview
sqlite3 content/pipeline/index.db \
  "SELECT status, COUNT(*) FROM items GROUP BY status;"

# Items ready for interview
sqlite3 content/pipeline/index.db \
  "SELECT id, current_title FROM items WHERE status = 'inbox' ORDER BY created_at DESC;"

# Items ready for drafting
sqlite3 content/pipeline/index.db \
  "SELECT id, current_title, brief_file FROM items WHERE status = 'approved';"

# Everything in a series
sqlite3 content/pipeline/index.db \
  "SELECT id, current_title, status FROM items WHERE series_id = 'the-refinement-era';"

# Lookup by ID
sqlite3 content/pipeline/index.db \
  "SELECT * FROM items WHERE id = '20260307-BM-001';"
```

**Recovery:** If `index.db` is lost or corrupted, run `/db-rebuild`. The skill scans all content files for frontmatter IDs and reconstructs the database. Content files are the ground truth; the DB is a fast query layer on top.

---

## Skills Reference

### Ingest Skills

All ingest skills follow the output contract: assign ID → write raw file (if applicable) → write brief → register in `index.db` → write inbox entry → update `_index.md`.

| Skill | Trigger | What it does | Tool |
|-------|---------|--------------|------|
| `bookmark-mining` | automated / "check bookmarks" | X bookmarks → raw + brief + inbox | xquery |
| `x-account-monitor` | automated | `sources.md` X accounts → raw + brief + inbox | xquery |
| `reply-monitor` | automated | Replies to @danzakon → raw + brief + inbox | xquery |
| `youtube-monitor` | automated / "check YouTube" | `sources.md` channels → raw + brief + inbox | ytquery |
| `watch-later-mining` | automated | Watch Later playlist → raw + brief + inbox | ytquery |
| `save-raw` | "fetch this: {url}" | Any URL or pasted content → raw + brief + inbox | Exa / WebFetch |
| `capture-thought` | "thought: {idea}" | Single thought → brief + inbox (instant, no conversation) | None |
| `idea-dump` | "idea dump: {text}" | Raw thought stream → workshop → multiple briefs + inbox | None |
| `research` | "research {topic}" | Deep research → `research/reports/` + brief + inbox | Exa |
| `tutorial` | "tutorial: {topic}" | Technical guide → `tutorials/guides/` + brief + inbox | Exa |

### Process Skills

| Skill | Trigger | What it does |
|-------|---------|--------------|
| `content-digest` | automated (after ingest) | Scores and ranks inbox items, refines angles |
| `content-interview` | `/content-interview` | Interactive item review → develops briefs |
| `content-pipeline` | `/content-pipeline` | Master orchestration: status, routing, queue |
| `content-refine` | `/content-refine` | Iterative draft review and editing |

### Creation Skills

| Skill | Trigger | What it does |
|-------|---------|--------------|
| `write-post` | automated / "write a post" | Brief → post variants + alt hooks + content tree |
| `write-article` | automated / "write an article" | Brief → long-form draft |
| `article-image` | "generate thumbnail" | Article → 1200x628 header image |

### Publishing

| Skill | Trigger | What it does |
|-------|---------|--------------|
| `postbridge` | automated / "schedule this" | PostBridge API scheduling |

---

## Automation (Cowork Scheduled Tasks)

See `cowork-tasks.md` for exact setup instructions and prompts.

| Task | Schedule | What it does |
|------|----------|--------------|
| Morning Ingest | 7:00 AM daily | Runs all automated ingest agents |
| Morning Digest | 7:30 AM daily | Scores and ranks new inbox items |
| Daily Scheduler | 7:30 AM daily | Schedules today's queued posts via PostBridge |
| Weekly Article Prep | Monday 9:00 AM | Stages ready articles, generates thumbnails |
| Weekly Review | Friday 4:00 PM | Pipeline health report, queue depth, content mix |

---

## Human Workflow

**Anytime (~10 sec):**
- "Thought: {idea}" — instant capture as a brief

**Daily or every few days (~20-30 min):**
- `/content-interview` — review the latest digest, share your takes, approve items
- `/content-refine` — review generated drafts, approve for queue

**On-demand:**
- "Idea dump: {paste notes}" — workshop raw thoughts into pipeline items
- "Research {topic}" — kick off a deep research session
- "Fetch this: {url}" — manually ingest a specific piece of content

**Weekly (~5 min):**
- Review staged articles (Monday notification from Cowork)
- Read the Friday health report

Everything else — ingest, digest, scheduling, history tracking, dedup — runs automatically.

---

## Operations

### Adding New Sources

**New X account to monitor:** Add a line to `sources.md` under the appropriate section. The next morning ingest run picks it up.

**New YouTube channel:** Add the channel ID to `sources.md` with an optional keyword filter.

**One-off content:** Use `save-raw` with the URL. Content is ingested, formatted, and added to the inbox immediately.

### Handling Content You Can't Scrape

X articles, paywalled posts, and anything requiring a real browser can't be ingested automatically. Use `save-raw`:

1. Paste the URL (and optionally the text) into a Claude session
2. `save-raw` formats it correctly and writes to `raw/x-articles/` or `raw/web/`
3. Brief and inbox entry are created automatically

### Recovery

**If `index.db` is corrupted or deleted:** Run `/db-rebuild`. Scans all content files for frontmatter IDs and reconstructs the database.

**If content files are accidentally deleted:** Restore from git: `git restore content/inbox/` or `git restore content/raw/`.

**If a Cowork task fails:** All tasks are idempotent — re-running produces the same result without duplication.

---

## Build Status

### Complete
- [x] Directory structure (inbox, raw, briefs, pipeline/migrations)
- [x] Control plane files (sources.md, series.md, schema.sql, index.db)
- [x] Series seeded (the-refinement-era)
- [x] Post files renamed to `YYYY-W{NN}` format
- [x] CLAUDE.md files updated across repo
- [x] Pipeline README rewritten (this file)

### Skills — Complete
- [x] `content-pipeline` — session orchestrator
- [x] `content-digest` — score + rank inbox items
- [x] `content-interview` — interactive inbox review → briefs
- [x] `content-refine` — iterative draft editing loop
- [x] `idea-dump` — conversational content workshop
- [x] `capture-thought` — instant thought capture → brief
- [x] `bookmark-mining` — X bookmark ingest
- [x] `x-account-monitor` — X account monitoring
- [x] `reply-monitor` — reply monitoring
- [x] `youtube-monitor` — channel monitoring + transcripts
- [x] `watch-later-mining` — Watch Later ingest
- [x] `save-raw` — manual URL/content ingest
- [x] `research` — deep research reports
- [x] `tutorial` — technical guide creation
- [x] `write-post` — post drafting from briefs
- [x] `write-article` — article drafting from briefs
- [x] `article-image` — header image generation
- [x] `db-rebuild` — reconstruct index.db from files
- [x] `postbridge` — PostBridge API scheduling
- [x] `ytquery` — YouTube CLI tool
- [x] `xquery` — X/Twitter CLI tool

### Infrastructure — Remaining
- [ ] Install ytquery dependencies: `pip install yt-dlp youtube-transcript-api && brew install ffmpeg deno`
- [ ] Symlink ytquery to PATH: `ln -sf ~/dev/life/skills/ytquery/scripts/ytquery ~/.local/bin/ytquery`
- [ ] Set up YouTube cookies for Watch Later
- [ ] Add YouTube channel IDs to `sources.md`
- [ ] Set up Cowork scheduled tasks (see `cowork-tasks.md`)
- [ ] End-to-end test: capture-thought → brief → interview → write-post → queue

---

## Agent Instructions

### For agents picking up build tasks:

1. Read this document for the full system design
2. Check the Build Status above — find an unchecked item
3. Read any existing skill files before rewriting them
4. Follow these conventions:
   - Skills live in `life/skills/{skill-name}/SKILL.md`
   - Scripts live inside the skill directory alongside `SKILL.md`
   - All ingest skills must follow the output contract (see Stage 1)
   - All processing skills query/update `index.db` via `sqlite3` CLI
   - All content creation skills read from briefs
   - All date-stamped files use ISO format (`YYYY-MM-DD` or `YYYYMMDD` in IDs)
   - Post files use `YYYY-W{NN}.md`
5. After building, run `bash skills/sync.sh` to link new skills to all agents
6. Commit with descriptive messages following the repo's commit conventions

### For agents running the pipeline interactively:

1. Start with `/content-pipeline` — it reads system state and guides you
2. Or jump to any specific stage skill directly
3. Always check `index.db` for current item status before processing
4. Always update `index.db` after changing item status
