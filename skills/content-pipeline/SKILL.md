---
name: content-pipeline
description: The content pipeline. Use for ANY content work — "check my pipeline",
  "pipeline status", "what should I post", "I have a thought", "thought:",
  "idea dump", "save this URL", "fetch this", "add to pipeline", "work session",
  "refine drafts", "review inbox", "I want to create content", "queue this",
  or any content workflow question.
argument-hint: "[command, thought, URL, or just invoke to start a session]"
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
  - Grep
---

# Content Pipeline

The single entry point for all content work. Reads system state, shows a health dashboard, and routes you to the right action. Everything flows through here.

Read `content/pipeline/README.md` for the full system architecture.

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
     WHEN 'draft' THEN 4 WHEN 'refined' THEN 5
     WHEN 'queued' THEN 7 WHEN 'published' THEN 8
   END;"

# Queue depth
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

# Refined items ready to queue
sqlite3 content/pipeline/index.db \
  "SELECT COUNT(*) FROM items WHERE status = 'refined';"
```

Also check:
- `content/pipeline/queue.md` — how many posts are queued with target dates

### Step 2: Check for direct input

If the user provided arguments when invoking, smart-route before showing the menu:

| Input pattern | Route to |
|---------------|----------|
| Contains `http://` or `https://` | Jump to **Add: URL** |
| Starts with "thought:" or "capture:" | Jump to **Add: Thought** |
| Starts with "idea dump:" or contains multiple ideas | Jump to **Add: Workshop** |
| Contains "research" / "investigate" / "deep dive" | Jump to **Add: Research** |
| Contains "guide" / "tutorial" / "how-to" | Jump to **Add: Tutorial** |
| "status" / "health" / "check my pipeline" | Show dashboard only, no menu |
| "what should I post" | Query strategy + briefs, suggest 3-5 ideas |
| "queue this" / "queue these" | Jump to **Work Session: Queue Flow** |
| No arguments or general intent | Show dashboard + menu |

### Step 3: Present dashboard and menu

Always show the dashboard, then the menu.

**Dashboard format:**

```
Pipeline — {date}
═══════════════════════════════════════════════════════

  Stage         Items   Notes
  ──────────────────────────────────────────────────
  Inbox           8     unreviewed signals
  Approved       10     ready to draft
  Drafts          3     need refining
  Refined         0     —
  Queue           0     EMPTY

  Queue Runway: 0 days — CRITICAL
  Today: nothing scheduled

  Suggested Actions:
  → Work session: 10 approved + 3 drafts to move through
  → 8 inbox items waiting for triage
  → Queue is empty — prioritize getting content queued

═══════════════════════════════════════════════════════

  INGEST — pull new signals from sources
  ──────────────────────────────────────────────────
  1) Bookmark mining        check X bookmarks
  2) Watch Later mining     check YouTube Watch Later
  3) X account monitor      check followed X accounts
  4) YouTube monitor        check subscribed channels
  5) Reply monitor          check replies to @danzakon
  6) Full sweep             run all ingest sources

  ADD — put something into the system
  ──────────────────────────────────────────────────
  7) Add to pipeline        thought, URL, bulk ideas,
                            research request, anything

  WORK — develop and ship content
  ──────────────────────────────────────────────────
  8) Work session           move items through the pipe
  9) Review inbox           triage unreviewed signals

  Pick a number, or just tell me what you need.
```

**Dashboard adapts to state:**

- If queue is empty, mark as `CRITICAL`
- If queue < 3 days of runway, mark as `LOW`
- If inbox is empty, note "Inbox clear — nothing to triage"
- If no approved items and no drafts, recommend ingest or idea dump
- Only show `Suggested Actions` that are relevant to current state
- Hide menu options that have zero items (e.g., hide option 8 if nothing to work on)

**Suggested Actions logic:**

Priority order for recommendations (pick top 2-3):
1. Queue empty or critically low → recommend work session or refine+queue
2. Refined items sitting un-queued → recommend queueing them
3. Drafts waiting for refine → recommend work session (just refining)
4. Large approved backlog → recommend work session (drafting)
5. Inbox items waiting → recommend review inbox
6. Theme gaps (compare history.md vs strategy.md) → recommend specific content type
7. Pending next-actions (briefs needing research/tutorial) → flag them

Wait for user selection.

---

## INGEST — Options 1-6

### Options 1-5: Individual ingest sources

Each option delegates to the corresponding skill. Read the skill's SKILL.md and execute its instructions:

| Option | Skill directory | What it does |
|--------|----------------|-------------|
| 1 | `skills/bookmark-mining/SKILL.md` | Fetch X bookmarks via `xquery x:bookmarks` |
| 2 | `skills/watch-later-mining/SKILL.md` | Fetch YouTube Watch Later via `ytquery y:watchlater` |
| 3 | `skills/x-account-monitor/SKILL.md` | Check X accounts from `sources.md` |
| 4 | `skills/youtube-monitor/SKILL.md` | Check YouTube channels from `sources.md` |
| 5 | `skills/reply-monitor/SKILL.md` | Check replies to @danzakon |

After any ingest completes, run `content-digest` (read `skills/content-digest/SKILL.md` and execute) to score and rank new items.

Then return to the dashboard with updated state.

### Option 6: Full Sweep

Run all 5 ingest sources in sequence:

1. Bookmark mining
2. X account monitor
3. Reply monitor
4. YouTube monitor
5. Watch Later mining

After all complete, run content-digest on the full batch.

Present a summary of everything ingested, then return to the dashboard with updated state.

---

## ADD — Option 7

### Smart Router

When the user selects option 7, ask: "What do you want to add?"

Then classify their input using this decision tree:

```
User provides input
│
├── Contains a URL (http:// or https://)
│   ├── YouTube URL (youtube.com or youtu.be)
│   │   └── Add: URL flow (offer transcript fetch)
│   └── Any other URL
│       └── Add: URL flow
│
├── Keyword triggers (confirm before committing):
│   ├── "research" / "investigate" / "dig into" / "deep dive"
│   │   └── Confirm: "Run a full research session on [topic]?"
│   │       ├── Yes → delegate to skills/research/SKILL.md
│   │       └── No, just capture it → Add: Thought flow
│   │
│   └── "guide" / "tutorial" / "how-to" / "walk me through"
│       └── Confirm: "Create a step-by-step guide on [topic]?"
│           ├── Yes → delegate to skills/tutorial/SKILL.md
│           └── No, just capture it → Add: Thought flow
│
├── Multiple distinct ideas (bullets, numbered list, newlines
│   between distinct topics, 3+ sentences on different subjects)
│   └── Add: Workshop flow
│
├── Single thought / sentence / short paragraph
│   └── Add: Thought flow
│
└── Ambiguous (could be one idea or several)
    └── Ask: "Is this one thought, or should I break
         it into separate ideas?"
```

### ID Assignment (AD prefix)

All items created through Add mode use the `AD` prefix:

```bash
sqlite3 content/pipeline/index.db \
  "SELECT id FROM items WHERE id LIKE '$(date +%Y%m%d)-AD-%' ORDER BY id DESC LIMIT 1;"
```

Increment by 1 (start at 001 if no results). Format: `YYYYMMDD-AD-NNN`.

Note: Research and tutorial items still use `RS` and `TU` prefixes when delegated to those skills. The `AD` prefix covers thoughts, URLs, and bulk ideas only.

### Add: Thought

Fast-path for capturing a single thought. No analysis, no conversation, no workshopping. Speed is the priority.

1. **Capture verbatim** — do not rewrite, expand, or analyze. Use the raw input as the Core Insight.

2. **Infer a short title** from the content (under 60 chars). Example: "AI agents should be narrow and deep."

3. **Infer format** based on length and complexity:
   - Short opinion or observation → `post`
   - Multi-part idea needing unpacking → `thread`
   - Deep topic needing research or long-form → `article`

4. **Write brief** to `content/briefs/{ID}.md`:

   ```markdown
   ---
   id: {ID}
   created: {YYYY-MM-DD}
   source-type: thought
   ingest-source: content-pipeline
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

5. **Register in index.db:**

   ```bash
   sqlite3 content/pipeline/index.db \
     "INSERT INTO items (id, created_at, source_type, ingest_source, status, current_title, format, platform, brief_file)
      VALUES ('{ID}', '$(date -u +%Y-%m-%dT%H:%M:%SZ)', 'thought', 'content-pipeline', 'raw', '{short title}', '{format}', 'Both', 'content/briefs/{ID}.md');"
   ```

6. **Write inbox entry** to `content/inbox/YYYY-MM-DD.md` (create if needed):

   ```markdown
   ## [{ID}] {Short title}

   **Status:** unreviewed
   **Type:** thought
   **Brief:** content/briefs/{ID}.md

   ### Summary
   {One-sentence summary}

   ### Actions
   - [ ] Review in content-interview
   ```

7. **Update `content/inbox/_index.md`** — add a row for the new item.

8. **Series connection check** (lightweight, non-blocking):
   - Read `content/pipeline/series.md` — does this connect to an active series?
   - Query recent items with similar topics:
     ```bash
     sqlite3 content/pipeline/index.db \
       "SELECT id, current_title FROM items WHERE source_type = 'thought' AND status IN ('raw','inbox') ORDER BY created_at DESC LIMIT 10;"
     ```
   - If series match, add one line after confirmation.
   - If 3+ related raw thoughts exist, suggest workshopping them.

9. **Confirm** with one line: `Captured: {short title} → {ID}`

If the user provides multiple thoughts at once, capture each as a separate brief with sequential IDs.

Then return to the dashboard.

### Add: Workshop

Interactive session for developing unstructured ideas. This is a creative workshop, not a filing operation.

**Step 1: Parse the raw input**

Extract individual ideas, themes, and fragments. Preserve the author's voice. Group ideas about the same thing.

Show a numbered list:

```
I found 4 distinct ideas in your dump:

1. **Vibe coding creates a complexity explosion** — adding features instead of refining
2. **Attention to detail requires reducing details** — quality over quantity
3. **Junior devs shipping faster but QA suffering** — the production gap
4. **AI as a first draft tool, not a final one** — refinement as skill

Do these look right? Anything I'm missing or combining wrong?
```

Wait for confirmation before proceeding.

**Step 2: Develop each idea**

For each confirmed idea, surface:

- **Core insight:** One sharp sentence distilling the idea.

- **Content angles:**
  - Hot take — the punchy, provocative read
  - Practical — the "here's how to use this" version
  - Nuanced — the "yes but here's what people miss" version
  - Counterintuitive — the surprising angle
  - Personal — connection to specific Tenex experience

- **Content tree — all applicable formats:**
  - Reply: specific person or post to reply to?
  - Post: standalone short-form version
  - Thread: 5-7 part breakdown
  - Article: long-form potential
  - Series: connection to existing series or seed for new one

- **Related inventory:** Check `series.md` for connections. Query `index.db` for existing items on the same theme.

- **Spinoffs:** What follow-up questions deserve their own piece?

**Step 3: Workshop each idea**

Open the conversation for each:
- "Which angle resonates most?"
- "Standalone post or does it want to be a series?"
- "Anything you'd add to the core insight?"

Capture the user's reaction and direction. Update the breakdown.

**Step 4: Route each idea**

Present a routing summary and confirm before writing:

```
Here's what we've decided:

1. Vibe coding complexity → Thread + article
   Angle: "Counterintuitive"
   Series: The Refinement Era (episode 3)
   Next action: draft

2. Attention to detail → Standalone post
   Angle: "Hot take"
   Next action: draft

3. Junior devs / production gap → Research first
   Next action: research

4. AI as first draft → Skip (overlaps with #1)

Ready to write briefs for items 1-3?
```

Wait for confirmation.

**Step 5: Write briefs and register**

For each approved item, assign an `AD` ID and write a full brief:

```markdown
---
id: {ID}
created: {YYYY-MM-DD}
source-type: thought
ingest-source: content-pipeline
status: approved
format: {post | thread | article | post+article}
platform: Both
series-id: {series slug or blank}
generate: {single | full-tree}
next-action: {draft | research | tutorial | series-seed}
---

## Core Insight
{One sharp sentence}

## Your Take
{What the user said during the workshop — their angle, voice, direction}

## Lead Angle
{Which angle from the breakdown}

## Content Tree
{What formats are being generated — what's planned for later}

## Draft Instructions
{Tone, hooks to try, things to avoid, examples to reference}

## Sources
- Captured directly via content-pipeline

## Related Items
- {ID} — {title, if any existing items connect}
```

Register each in `index.db`, write inbox entries, update `_index.md`.

Spinoff ideas become their own briefs linked to the parent via Related Items. Set spinoffs to `status: raw` with appropriate `next-action`.

**Step 6: Offer next steps**

```
Briefs written for 3 items:

  draft items:
  - Item 1: Draft the thread + article now?
  - Item 2: Draft the post now?

  research items:
  - Item 3: Kick off research now?

Or save everything for later?
```

| next-action | Offer |
|-------------|-------|
| `draft` | Start a work session to draft these items |
| `research` | Delegate to `skills/research/SKILL.md` with the brief as context |
| `tutorial` | Delegate to `skills/tutorial/SKILL.md` with the brief as context |
| `series-seed` | Open `series.md` and help plan the series arc |

After the delegated action completes, return to the dashboard.

**Tone:** This is a creative workshop. Be energetic, sharp, collaborative, and efficient. If an idea is weak or redundant, say so directly.

### Add: URL

Manually ingest any piece of content — URLs, pasted text, paywalled articles.

**Step 1: Determine content type**

| Signal | Content type | Raw folder |
|--------|-------------|------------|
| `x.com/status/` or `twitter.com/status/` | x-post | `raw/x-posts/` |
| `x.com/i/articles/` | x-article | `raw/x-articles/` |
| `youtube.com` or `youtu.be` | youtube | `raw/youtube/` (offer transcript fetch via ytquery) |
| Substack, Medium, blog URL | web | `raw/web/` |
| Pasted text with no URL | thought | Route to **Add: Thought** instead |
| Any other URL | web | `raw/web/` |

If YouTube URL: "This is a YouTube video. Want me to fetch the full transcript? (uses ytquery)" If yes, use `ytquery y:transcript {url}` and `ytquery y:video {url}` for metadata.

**Step 2: Fetch content**

Try in order:
1. `mcp__exa__crawling_exa` with the URL — best for most web content
2. Fall back to `WebFetch` if Exa fails
3. For X posts: parse what's available, note thread may be truncated

If fetch fails (paywalled, auth-gated):
```
Couldn't fetch the full content (likely paywalled). Options:
  1. Paste the content directly and I'll save it
  2. Save just the URL as a placeholder — paste content later
```

**Step 3: Assign AD ID** (same process as above)

**Step 4: Write raw file** to `content/raw/{type}/YYYYMMDD-AD-NNN-{slug}.md`:

```markdown
---
id: {ID}
source-type: {x-post | x-article | youtube | web}
ingest-source: content-pipeline
fetch-method: {exa | webfetch | manual-paste | ytquery}
original-url: {url or "pasted"}
author: {if known}
captured: {ISO datetime}
---

{Full content — never truncated}
```

**Step 5: Write brief** to `content/briefs/{ID}.md` with minimal frontmatter + Core Insight extracted from the content.

**Step 6: Generate inbox entry** with summary and 3 content angles (read `strategy.md` for relevant themes).

**Step 7: Register in index.db** and update `_index.md`.

**Step 8: Confirm and offer next step**

```
Saved: {ID}
  Type: {type}
  File: content/raw/{type}/{filename}

Workshop this now or save for the next inbox review?
```

If workshop now, run the development flow inline: show summary + angles, ask for take, write a developed brief, offer to draft.

Then return to the dashboard.

---

## WORK — Options 8-9

### Option 8: Work Session

A guided batch session that moves items through the pipeline. Starts at the earliest bottleneck, works forward.

**Mode selection:**

Query items by status, then present:

```
Work Session — {N} items to move
═══════════════════════════════════════════════════════

  approved ({N})  →  need drafting
  draft ({N})     →  need refining
  refined ({N})   →  need queueing

  How do you want to work?

  a) Guided — walk through everything, one at a time (default)
  b) Just drafting — draft approved items, refine later
  c) Just refining — polish existing drafts only
  d) Full batch — draft all, then refine all, then queue
```

| Mode | Behavior |
|------|----------|
| **Guided** | For each item: show brief → ask for input → draft → offer to refine immediately → offer to queue. One at a time. |
| **Just drafting** | Iterate approved items, draft each, move to next. Skip refine. |
| **Just refining** | Only show `status: draft` items. Present each, get edits, mark refined. |
| **Full batch** | Two passes: draft all approved first, then refine all drafts, then queue all refined. |

#### Drafting Flow

For each approved item:

1. **Show the brief:**

   ```
   ─────────────────────────────────────────────────────
   [{N}/{total}]  {ID} — {title}
   Status: approved
   Format: {format}  ·  Next action: {next-action}

   Core insight: {from brief}
   Your take: {from brief, if present}
   Lead angle: {from brief, if present}
   ─────────────────────────────────────────────────────
   ```

2. **Check `next-action` and route:**

   | next-action | What happens |
   |-------------|-------------|
   | `draft` | Ask for input, then draft (step 3) |
   | `research` | "This needs research first. What angle do you want me to investigate?" → delegate to `skills/research/SKILL.md` → fold results into brief Sources → flip `next-action` to `draft` → "Ready to draft now?" |
   | `tutorial` | Same pattern — delegate to `skills/tutorial/SKILL.md` → fold results back → then draft |
   | `series-seed` | Open `series.md`, help plan the series arc → then draft |

3. **Ask for input before drafting:**

   "Anything to add? Different angle? Additional context? Or looks good as-is?"

   - User adds input → incorporate into brief's Draft Instructions
   - "looks good" → proceed to draft

4. **Draft:** Read the brief (and raw file if it exists in Sources). Delegate to the appropriate creation skill:
   - Posts/threads: read `skills/write-post/SKILL.md` and execute its instructions
   - Articles: read `skills/write-article/SKILL.md` and execute its instructions

   Show the draft output.

5. **After drafting (Guided mode):**

   "Refine this now while it's fresh? (yes / skip / stop session)"

   - yes → enter Refine Flow for this item
   - skip → move to next item
   - stop → end session, return to dashboard

#### Refine Flow

For each draft item:

1. **Find the draft:** Read the post file or article file. Query for the specific entry.

2. **Present the draft:**

   ```
   ─────────────────────────────────────────────────────
   [{N}/{total}]  {ID} — {title}
   Format: {format}  ·  Platform: {platform}

   TWITTER ({char count} chars):
     {Twitter content}

   LINKEDIN ({char count} chars):
     {LinkedIn content}

   ALT HOOKS:
     A) "{hook A}"
     B) "{hook B}"
     C) "{hook C}"

   Source brief: content/briefs/{ID}.md
   ─────────────────────────────────────────────────────

   What do you want to do?
     [approve] [use alt A/B/C] [edit: instruction] [rewrite] [skip]
   ```

3. **Handle feedback:**

   - **approve** — Mark as refined, move on.
   - **use alt A/B/C** — Rewrite the post using the selected hook as the opener. Show the new version and ask for approval.
   - **edit: {instruction}** — Apply the edit. Examples: "make LinkedIn more direct", "shorten Twitter version", "add a concrete number." Show updated version, ask again. Keep iterating until approved.
   - **rewrite** — Full rewrite with different approach. Read the brief and every file listed in Sources to rebuild full context. Generate a fresh draft. Show and ask.
   - **skip** — Leave in draft status, move to next.

4. **Quality checks** (run silently before presenting, flag issues):
   - **Em-dash scan:** Flag if em-dashes present — "This draft has em-dashes — replace them?"
   - **AI vocabulary:** Scan for banned words from write-post/write-article standards. Flag matches.
   - **Length check:** Twitter must be ≤280 chars (or properly threaded). LinkedIn 500-3000 chars.
   - **Opinion check:** Does the draft contain an actual stance? Flag if wishy-washy.

5. **Write approved version:** Update the draft file in-place. Match by content-id frontmatter in weekly post files.

6. **Update index.db:**

   ```bash
   sqlite3 content/pipeline/index.db \
     "UPDATE items SET status = 'refined' WHERE id = '{ID}';"
   ```

#### Queue Flow

After items are refined (or when refined items already exist):

"You have {N} refined items ready to queue. Queue them now?"

For each refined item:

1. **Dedup check:** Compare content against `content/pipeline/history.md` and optionally `xquery x:user @danzakon --limit 20`.

2. **Assign target date:** Spread across upcoming days, respecting cadence from `strategy.md` (default: multiple posts/day).

3. **Move article files (articles only):** If the item's format is `article` or `post+article` or `full-tree` and the item has a draft file in `content/articles/drafts/`, move it to `content/articles/queued/`:

   ```bash
   mv content/articles/drafts/{filename}.md content/articles/queued/{filename}.md
   ```

   Update the brief's `## Draft` path to reflect the new location. For non-article items (posts, threads), skip this step.

4. **Write to `content/pipeline/queue.md`:**

   For posts/threads:
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

   For articles:
   ```markdown
   ### [ ] {Title}

   **Content ID:** {ID}
   **Target date:** YYYY-MM-DD
   **Platform:** {blog | x-article}
   **Priority:** normal
   **Type:** article
   **File:** content/articles/queued/{filename}.md

   **Status:** queued
   ```

5. **Update index.db:** `status = 'queued'`

6. Report what was queued and when.

**On publish:** When an article is marked as published (added to `history.md`), move the file from `content/articles/queued/` to `content/articles/published/` and update `published_date` in the frontmatter.

#### After each item

- **Guided mode:** "Next item, or done for now?"
- **Batch modes:** Continue automatically until all items in scope are processed.

#### After the session

```
Session complete:
  {N} drafted
  {N} refined
  {N} queued
  {N} skipped

{Return to dashboard with updated state}
```

### Option 9: Review Inbox

Delegate to `skills/content-interview/SKILL.md`. Read that file and execute its full flow.

After the interview session completes, return to the dashboard with updated state.

---

## Direct Commands

These bypass the menu for quick actions:

| Input | Route |
|-------|-------|
| "pipeline status" / "check my pipeline" / "health" | Dashboard only |
| "what should I post" | Query strategy + approved briefs, suggest 3-5 ideas |
| "queue this" / "queue these" | Run Queue Flow on specified or all refined items |
| "thought: {text}" | Add: Thought (fast-path) |
| "idea dump: {text}" | Add: Workshop |
| URL as argument | Add: URL |
| "research {topic}" | Add: Research (confirm, then delegate) |
| "tutorial {topic}" | Add: Tutorial (confirm, then delegate) |
| No argument / general intent | Full dashboard + menu |

---

## Session Loop

After every action completes (ingest, add, work session, etc.), re-query the database and return to the dashboard with updated state. Present the menu again. Continue until the user is done.

---

## Workspace

All state lives in the life repo:

- `content/pipeline/README.md` — full system architecture
- `content/pipeline/strategy.md` — content themes, voice, cadence
- `content/pipeline/sources.md` — X accounts + YouTube channels
- `content/pipeline/series.md` — content series tracker
- `content/pipeline/queue.md` — posts pending scheduling
- `content/pipeline/history.md` — published content log
- `content/pipeline/index.db` — SQLite index (items + series)
- `content/inbox/` — daily intake files
- `content/raw/` — source material by type
- `content/briefs/` — work items (the atomic unit)
- `content/posts/` — weekly post files (`YYYY-W{NN}.md`)
- `content/articles/` — long-form drafts and published
- `research/reports/` — research output
- `tutorials/guides/` — technical guides

---

## Prerequisites

`sqlite3` (pre-installed on macOS). Ingest skills require `xquery` and/or `ytquery` — see `skills/CLAUDE.md` for setup.
