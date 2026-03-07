---
name: content-refine
description: Review and iterate on content drafts before queuing. Use when asked to
  "refine my drafts", "review drafts", "polish these posts", or "content-refine".
argument-hint: "[optional: specific content ID to refine]"
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
---

# Content Refine

Interactive draft review and editing loop. The second human checkpoint — between drafting and queuing. Shows drafts with their alternative hooks, accepts edit instructions, iterates until the user approves.

---

## Trigger

- "/content-refine"
- "Review my drafts"
- "Polish these posts"
- "Refine {content ID}"
- From content-pipeline session menu (option C)

---

## Workspace

- `content/pipeline/index.db` — find items with status='draft'
- `content/posts/YYYY-W{NN}.md` — weekly post files
- `content/articles/drafts/` — article drafts
- `content/briefs/` — original brief for context
- `content/pipeline/strategy.md` — voice and quality reference

---

## Session Flow

### Step 1: Find drafts to refine

```bash
sqlite3 content/pipeline/index.db \
  "SELECT id, current_title, format, draft_file
   FROM items WHERE status = 'draft'
   ORDER BY created_at DESC;"
```

If a specific content ID was provided, filter to just that item.

Present the list:

```
You have 3 drafts to review:

  1. 20260307-BM-001 — "Pricing is a founder trap" (post, Both)
  2. 20260307-ID-002 — "Vibe coding's dirty secret" (thread, Both)
  3. 20260307-RS-001 — "The production gap" (article)

Review all in order? Or jump to a specific one?
```

### Step 2: Present each draft

For each draft, read the post file or article file and show:

```
─────────────────────────────────────────
[1/3]  20260307-BM-001 — "Pricing is a founder trap"
Format: post  ·  Platform: Both

TWITTER (276 chars):
  Most founders price based on cost. That's the trap.
  Value-based pricing sounds obvious until you try to
  measure the value you create. Here's the thing nobody
  tells you: your best customers already know your
  product is underpriced.

LINKEDIN (892 chars):
  [full LinkedIn version]

ALT HOOKS:
  A) "Your best customers already know you're underpriced."
  B) "The pricing question most founders get backwards."
  C) "Stop pricing based on what it costs you to build."

Source brief: content/briefs/20260307-BM-001.md
─────────────────────────────────────────

What do you want to do?
  [approve] [use alt A/B/C] [edit: instruction] [rewrite] [skip]
```

### Step 3: Handle user feedback

**approve** — Mark as refined, move on.

**use alt A/B/C** — Rewrite the post using the selected hook as the opener. Show the new version and ask for approval.

**edit: {instruction}** — Apply the specific edit instruction. Examples:
- "edit: make the LinkedIn version more direct"
- "edit: shorten the Twitter version"
- "edit: change the tone to be more provocative"
- "edit: add a concrete number or example"

Show the updated version and ask again. Keep iterating until approved.

**rewrite** — Full rewrite with a different approach. Read the brief, then read each file listed in `## Sources` to rebuild full context before rewriting. Generate a fresh draft grounded in the source material. Show and ask for approval.

**skip** — Leave in draft status, move to the next item.

### Step 4: Write approved version

When approved, update the draft file with the final version. If using a weekly post file, update the specific post entry in-place (match by content-id frontmatter).

### Step 5: Update index.db

```bash
sqlite3 content/pipeline/index.db \
  "UPDATE items SET status = 'refined' WHERE id = '{ID}';"
```

### Step 6: After each item

Move immediately to the next draft. After the last one:

```
Session complete:
  3 refined (ready to queue)
  0 skipped

Queue all 3 now? [yes / not yet]
```

If yes, run the queue action from `content-pipeline`.

---

## Quality Checks

Before presenting a draft for approval, run these checks silently and flag any issues:

1. **Em-dash scan:** If the draft contains em-dashes, flag: "This draft has em-dashes — want me to replace them?"
2. **AI vocabulary:** Scan for the banned word list from write-post/write-article standards. Flag any matches.
3. **Length check:** Twitter must be ≤280 chars (or properly threaded). LinkedIn should be 500–3000 chars.
4. **Opinion check:** Does the draft contain an actual stance, or is it vague? Flag if wishy-washy.

---

## Prerequisites

`sqlite3` (pre-installed on macOS).
