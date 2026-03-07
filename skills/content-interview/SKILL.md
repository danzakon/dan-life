# Content Interview

Interactive inbox review session. Presents digested inbox items one at a time, captures your take on each, creates briefs for approved items, and hands off to drafting. The human-in-the-loop checkpoint between ingest and content creation.

---

## Trigger

- Manual: "/content-interview", "Review my inbox", "Let's go through the inbox"
- From content-pipeline session menu (option A)

---

## Workspace

- `content/inbox/_index.md` — find which days have items to review
- `content/inbox/YYYY-MM-DD.md` — inbox files
- `content/pipeline/strategy.md` — context for angle suggestions
- `content/pipeline/series.md` — series connections
- `content/briefs/` — output: one brief per approved item
- `content/pipeline/index.db` — status tracking
- `content/inbox/_index.md` — update after session

---

## Session Flow

### Step 1: Find items to review

Read `content/inbox/_index.md`. Find days with `digested` or `unreviewed` items. Start with the most recent day. Query index.db for the items:

```bash
sqlite3 content/pipeline/index.db \
  "SELECT id, current_title, source_type, ingest_source
   FROM items
   WHERE status IN ('raw','inbox')
   ORDER BY id DESC;"
```

Open the corresponding inbox file. Sort by score (highest first — already done by content-digest).

Announce the session:
```
You have 8 items to review from 2026-03-07.
2 are time-sensitive (reply opportunities).
Let's go through them — I'll show you one at a time.
```

### Step 2: Present each item

For each item, show a clean card:

```
─────────────────────────────────────────────────
[1/8]  Score: 9/10  ⚡ TIME-SENSITIVE  · engineering-take

@levelsio on pricing SaaS products
Source: bookmark  ·  https://x.com/levelsio/status/...

"pricing is something most founders get wrong — they
price based on cost, not based on value captured"

LEAD ANGLE: Hot take — cost-based pricing is a founder trap
Other angles:
  · Practical: 3 signals your pricing is too low
  · Nuanced: When value-based pricing backfires

Series: none detected

What do you think? Your reaction, or one of:
  [reply] [post] [thread] [article] [full tree] [skip] [research first]
─────────────────────────────────────────────────
```

Wait for input.

### Step 3: Capture response and decide

**If the user gives a reaction or take:**
- Record their exact words as the brief's "Your Take" section
- Ask: "What format — post, thread, article, or the full tree?"
- Ask: "Any specific direction on angle or tone?"
- Create a brief

**If the user picks a shortcut:**
- `reply` — create a brief flagged for immediate reply, pre-populate with a draft reply angle
- `post` — create brief for standalone post
- `thread` — create brief for thread format
- `article` — create brief for long-form
- `full tree` — create brief with all formats flagged, generate everything
- `skip` — mark as skipped in index.db, move on
- `research first` — note in index.db, suggest research skill, move on

**Time-sensitive items:** After any approval, surface the urgency: "This one is time-sensitive — want me to draft the reply right now before we continue?"

### Step 4: Write the brief

For each approved item, assign the next available ID sequence and write `content/briefs/{ID}.md`:

```markdown
---
id: {ID}
created: {YYYY-MM-DD}
source-type: {x-post | youtube | web | research | thought}
ingest-source: {source skill}
status: approved
format: {post | thread | article | post+article | full-tree | reply}
platform: Both
series-id: {series slug or blank}
generate: {single | full-tree}
---

## Core Insight
{One sharp sentence distilling the idea}

## Your Take
{Verbatim or close-paraphrase of what you said}

## Lead Angle
{The angle selected}

## All Angles
{The full list from the inbox entry, for reference}

## Content Tree
{What formats to develop — all applicable, develop now}
- Reply: {yes/no — draft hook}
- Post: {yes/no — angle}
- Thread: {yes/no — structure idea}
- Article: {yes/no — working title}

## Draft Instructions
{Specific guidance: tone, hooks to try, references to use, things to avoid}

## Series
{Series name if applicable, which episode}

## Source
{original-url or raw file path}
```

### Step 5: Update index.db

```bash
# Approve and link brief
sqlite3 content/pipeline/index.db \
  "UPDATE items SET status = 'approved', brief_file = 'content/briefs/{ID}.md'
   WHERE id = '{original-item-id}';"

# Skip
sqlite3 content/pipeline/index.db \
  "UPDATE items SET status = 'skipped' WHERE id = '{ID}';"
```

### Step 6: After each item

Keep pace light. After approving or skipping, immediately show the next item. Don't recap unnecessarily — just move.

If a time-sensitive item was approved, offer to draft it now:
```
Brief written. This one has a 24hr reply window.
Draft the reply now? [yes / continue reviewing]
```

### Step 7: Session wrap-up

After all items are reviewed, show a summary:

```
Session complete. 2026-03-07 inbox:
  ✓ 5 approved → briefs written
  · 2 skipped
  · 1 flagged for research

Next:
  - Draft all 5 now? [yes]
  - Draft just the time-sensitive reply? [just the reply]
  - Come back to drafting later? [done for now]
```

If the user wants to draft: hand off to write-post / write-article with the brief paths.

### Step 8: Update _index.md

Mark the reviewed day as `reviewed` with item counts. Update item rows.

---

## Tone

This session should feel like a fast, energetic editorial meeting — not a form. Keep it:
- **Quick** — one item at a time, minimal preamble
- **Opinionated** — surface the best angle, not a neutral list
- **Conversational** — match the user's energy
- **Decisive** — push toward a decision on each item, don't linger

If an item is clearly weak, say so: "This one scored a 3. Nothing obviously worth developing — skip?" Don't treat every item as equally interesting.

---

## Prerequisites

`sqlite3` (pre-installed on macOS).
