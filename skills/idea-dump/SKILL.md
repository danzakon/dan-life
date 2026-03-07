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
- `content/.scratchpad/thought-bank-YYYY-MM.md` — current month's thought bank
- `content/inbox/YYYY-MM-DD.md` — today's inbox (approved items land here)
- `content/inbox/_index.md` — master item registry
- `content/pipeline/index.db` — SQLite index

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

**Related inventory:** Check `content/pipeline/series.md` and `content/.scratchpad/thought-bank-YYYY-MM.md` for existing thoughts on the same theme. Surface any connections.

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

2. Attention to detail → Standalone post (develop now)
   Angle: "Hot take" — distilled from Dorsey angle

3. Junior devs / production gap → Research first, then content
   Suggest: kick off a research report, content follows immediately after

4. AI as first draft → Skip (overlaps with #1)

Ready to write briefs for items 1 and 2? Or adjust anything first?
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
   ---

   ## Core Insight
   {One sharp sentence}

   ## Your Take
   {What the user said during the session — their angle, voice, direction}

   ## Angle Selected
   {Which angle from the breakdown}

   ## Content Tree
   {What formats are being generated — what's planned for later}

   ## Draft Instructions
   {Specific guidance: tone, hooks to try, things to avoid, examples to reference}

   ## Spinoffs
   {Follow-up ideas to capture in the thought bank}
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

5. **Write spinoff ideas to thought bank** — any follow-up ideas that came up during the workshop go into `content/.scratchpad/thought-bank-YYYY-MM.md` with `Used: [ ]`.

6. **Update `content/inbox/_index.md`** — add rows for each new item.

### Step 6: Offer to draft

After routing is confirmed, offer to generate content immediately:

```
Briefs are written for 2 items. Want me to:
- Draft the thread for item 1 right now?
- Draft the post for item 2 right now?
- Or save that for a content session later?
```

If the user wants drafts now, invoke the `write-post` or `write-article` skill with the brief as input.

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
