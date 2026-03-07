# Idea Dump

A content strategy workshop. Takes raw, unstructured ideas and opens a collaborative conversation about what to build with them — posts, threads, articles, series, or all of the above.

This is not a filing operation. It is an interactive session where the agent and the user together decide how to develop and route ideas into the pipeline.

---

## Trigger

Use when:
- "Idea dump: {raw text}"
- "I have some thoughts I want to get into the pipeline"
- "Here are some ideas from my notes"
- Pasting raw text from Notes, voice-to-text, or stream-of-consciousness writing

---

## Workspace

- `content/pipeline/strategy.md` — content themes and hot topics
- `content/pipeline/series.md` — active series (check for connections)
- `content/pipeline/index.db` — SQLite index
- `content/briefs/` — where new briefs are written
- `content/inbox/YYYY-MM-DD.md` — today's inbox (items land here)
- `content/inbox/_index.md` — master item registry

---

## The Session

### Step 1: Parse the raw input

Read the raw text. Extract individual ideas, themes, and fragments. Do not over-structure — preserve the author's voice and intent. Group ideas that are clearly about the same thing.

Produce a numbered list of distinct ideas or clusters. Show it to the user.

Example output:

```
I found 4 distinct ideas in your dump:

1. **Vibe coding creates a complexity explosion** — the instinct to keep adding features instead of refining
2. **Attention to detail requires reducing details** — the Dorsey connection, quality over quantity
3. **Junior devs shipping faster but QA suffering** — the production gap angle
4. **AI as a first draft tool, not a final one** — the refinement-as-skill framing

Do these look right? Anything I'm missing or combining wrong?
```

Wait for confirmation before proceeding.

### Step 2: Develop each idea

For each confirmed idea, generate a full content development breakdown. Present this one idea at a time or all at once — read the pace of the conversation.

For each idea, surface:

**The core insight:** What is this really saying? Distill it to one sharp sentence.

**Content angles:**
- Hot take — the punchy, provocative read
- Practical — the "here's how to use this" version
- Nuanced — the "yes but here's what people miss" version
- Counterintuitive — what's the surprising or counterintuitive angle?
- Personal — how does this connect to your specific experience at Tenex?

**Content tree — develop all applicable formats now:**
- Reply: Is there a specific person or post to reply to? Draft it.
- Post: What's the standalone short-form version? Draft it.
- Thread: Does this want to be a 5–7 part breakdown? Draft it.
- Article: Is there enough here for long-form? Draft it — don't wait.
- Series: Does this connect to an existing series, or seed a new one?

Develop everything that has merit. Sequencing when each piece gets posted happens at the queue stage, not here. A post and its companion article can both go out this week.

**Related inventory:** Check `content/pipeline/series.md` for series connections. Query `index.db` for existing items on the same theme. Surface any connections.

**Spinoffs:** What questions does this idea raise that deserve their own piece?

### Step 3: Workshop each idea

After presenting the breakdown, open the conversation:

- "Which angle resonates most for this one?"
- "Is this a standalone post or does it feel like it wants to be a series?"
- "Do you want to develop the thread or go straight to an article?"
- "Anything you'd add or change to the core insight?"

Capture the user's reaction and direction. Update the breakdown based on their input.

### Step 4: Decide and route

After discussing each idea, present a routing summary and confirm before writing anything:

```
Here's what we've decided:

1. Vibe coding complexity → Thread + article (develop both now)
   Angle: "Counterintuitive" — creation is the easy part now
   Series: The Refinement Era (episode 3)
   Next action: draft

2. Attention to detail → Standalone post (develop now)
   Angle: "Hot take" — distilled from Dorsey angle
   Next action: draft

3. Junior devs / production gap → Research first, then content
   Suggest: kick off a research report, content follows immediately after
   Next action: research

4. AI as first draft → Skip (overlaps with #1)

Ready to write briefs for items 1–3? Or adjust anything first?
```

Wait for confirmation.

### Step 5: Write briefs and register items

For each approved item:

1. **Assign an ID** using the `ID` source prefix:
   - Query `content/pipeline/index.db` for the highest ID number today with source `ID`:
     ```bash
     sqlite3 content/pipeline/index.db \
       "SELECT id FROM items WHERE id LIKE '$(date +%Y%m%d)-ID-%' ORDER BY id DESC LIMIT 1;"
     ```
   - Increment by 1 (start at 001 if no results)

2. **Write the brief** to `content/briefs/{ID}.md`:
   ```markdown
   ---
   id: {ID}
   created: {YYYY-MM-DD}
   source-type: thought
   ingest-source: idea-dump
   status: approved
   format: {post | thread | article | post+article}
   platform: Both
   series-id: {series-id or blank}
   generate: {single | full-tree}
   next-action: {draft | research | tutorial | series-seed}
   ---

   ## Core Insight
   {One sharp sentence}

   ## Your Take
   {What the user said during the session — their angle, voice, direction}

   ## Lead Angle
   {Which angle from the breakdown}

   ## Content Tree
   {What formats are being generated — what's planned for later}

   ## Draft Instructions
   {Specific guidance: tone, hooks to try, things to avoid, examples to reference}

   ## Sources
   {Any URLs or files referenced during the workshop}
   - Captured directly via idea-dump

   ## Related Items
   - {ID} — {title or note, if any existing pipeline items connect}
   ```

3. **Register in index.db**:
   ```bash
   sqlite3 content/pipeline/index.db \
     "INSERT INTO items (id, created_at, source_type, ingest_source, status, current_title, brief_file, series_id, format, platform)
      VALUES ('{ID}', '{datetime}', 'thought', 'idea-dump', 'approved', '{title}', 'content/briefs/{ID}.md', '{series_id}', '{format}', 'Both');"
   ```

4. **Add to today's inbox** (`content/inbox/YYYY-MM-DD.md`) if the file exists, or create it:
   ```markdown
   ## [{ID}] {Core insight title}

   **Status:** approved
   **Type:** thought
   **Brief:** content/briefs/{ID}.md
   **Ingest source:** idea-dump
   ```

5. **Create spinoff briefs** — any follow-up ideas that came up during the workshop become their own briefs (using the same ID assignment + registration process). Link them to the parent item via the Related Items field. Set `status: raw` and `next-action` based on what the spinoff needs (draft, research, etc.).

6. **Update `content/inbox/_index.md`** — add rows for each new item (including spinoffs).

### Step 6: Offer next steps based on next-action

After routing is confirmed, offer the appropriate next step for each item based on its `next-action` value. Don't always offer to draft.

```
Briefs written for 3 items:

  draft items:
  - Item 1: Draft the thread + article now? → /write-post, /write-article
  - Item 2: Draft the post now? → /write-post

  research items:
  - Item 3: Kick off research now? → /research

Or save everything for later?
```

| next-action | Offer |
|-------------|-------|
| `draft` | Invoke `write-post` / `write-article` |
| `research` | Invoke `research` with the brief as context |
| `tutorial` | Invoke `tutorial` with the brief as context |
| `series-seed` | Open `series.md` and help plan the series arc |

---

## Tone

This is a creative workshop, not a form to fill out. Keep the conversation:
- **Energetic** — ideas are exciting, treat them that way
- **Sharp** — always push toward the most interesting angle, not the safest
- **Collaborative** — surface options, let the user decide direction
- **Efficient** — don't belabor ideas the user wants to skip

If an idea is weak or redundant, say so directly. "This overlaps heavily with the vibe coding thread — worth merging, or do you see it as distinct?"

---

## Prerequisites

None. No external tools or API keys required.
