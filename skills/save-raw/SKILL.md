# Save Raw

Manually ingest any piece of content into the pipeline. Handles URLs (fetches content), pasted text, or anything that can't be scraped automatically — X articles, paywalled posts, Substack, blog posts, screenshots of tweets.

---

## Trigger

- "Save this: {url}"
- "Fetch this: {url}"
- "Add this to my pipeline: {url or pasted text}"
- "Ingest this article"
- Pasting content directly with "save this"

---

## Workspace

- `content/raw/x-posts/` — tweets, threads
- `content/raw/x-articles/` — X long-form articles
- `content/raw/youtube/` — video transcripts (use youtube-monitor instead for full flow)
- `content/raw/web/` — everything else
- `content/inbox/YYYY-MM-DD.md` — today's inbox
- `content/inbox/_index.md` — master registry
- `content/pipeline/index.db` — item registration
- `content/pipeline/strategy.md` — for generating angles

---

## Step 1: Determine content type and source

From the input, identify:

| Signal | Content type | Raw folder |
|--------|-------------|------------|
| `x.com/status/` or `twitter.com/status/` | x-post | `raw/x-posts/` |
| `x.com/i/articles/` | x-article | `raw/x-articles/` |
| `youtube.com` or `youtu.be` | youtube | `raw/youtube/` (prompt to use youtube-monitor for transcript) |
| Substack, Medium, blog URL | web | `raw/web/` |
| Pasted text with no URL | thought | route to `idea-dump` instead |
| Any other URL | web | `raw/web/` |

If the input is a YouTube URL, offer: "This looks like a YouTube video. Want me to fetch the full transcript instead? (uses youtube-monitor)" If yes, hand off to that skill.

---

## Step 2: Fetch content

**If a URL is provided:**

Try fetching in this order:
1. Use `mcp__exa__crawling_exa` with the URL — best for most web content
2. Fall back to `WebFetch` if Exa fails
3. For X posts: parse what's available from the URL, note that full thread may be truncated

**If text is pasted directly:**
Use the pasted content as-is. Ask for the original URL to include as a source link (optional but preferred).

---

## Step 3: Assign ID

Query `index.db` for the highest `SR` (save-raw) ID today, increment:

```bash
sqlite3 content/pipeline/index.db \
  "SELECT id FROM items WHERE id LIKE '$(date +%Y%m%d)-SR-%' ORDER BY id DESC LIMIT 1;"
```

Format: `YYYYMMDD-SR-NNN`

---

## Step 4: Write raw file

Write to `content/raw/{type}/YYYYMMDD-SR-NNN-{slug}.md`:

```markdown
---
id: {ID}
source-type: {x-post | x-article | youtube | web}
ingest-source: save-raw
fetch-method: {exa | webfetch | manual-paste}
original-url: {url or "pasted"}
author: {if known}
captured: {ISO datetime}
---

{Full content here — as complete as possible}
```

---

## Step 5: Generate inbox entry

Read `content/pipeline/strategy.md` to generate relevant angles.

Write entry to `content/inbox/YYYY-MM-DD.md` (create the file if it doesn't exist):

```markdown
## [{ID}] {Source type}: {Title or first line}

**Status:** unreviewed
**Type:** {type}
**Original:** {url}
**Raw file:** content/raw/{type}/{filename}
**Ingest source:** save-raw

### Summary
{2–3 sentence summary of what this is about}

### Content angles (develop all applicable formats now)
1. **Hot take**: {provocative angle}
2. **Practical**: {actionable spin}
3. **Nuanced**: {the "yes, but" angle}

### Content tree
- **Reply**: {if there's someone to reply to}
- **Post**: {standalone angle}
- **Thread**: {breakdown opportunity}
- **Article**: {long-form potential}
- **Series**: {connection to series.md if applicable}

### Actions
- [ ] Review in content-interview
```

---

## Step 6: Register in index.db

```bash
sqlite3 content/pipeline/index.db \
  "INSERT INTO items (id, created_at, source_type, ingest_source, status, current_title, original_url, raw_file)
   VALUES (
     '{ID}',
     '{datetime UTC}',
     '{source_type}',
     'save-raw',
     'raw',
     '{title or slug}',
     '{url}',
     'content/raw/{type}/{filename}'
   );"
```

---

## Step 7: Update _index.md

Add a row to the Item Registry and update the Day Status table.

---

## Step 8: Confirm and offer next step

```
Saved: 20260307-SR-001
  Type: x-article
  File: content/raw/x-articles/20260307-SR-001-dan-abramov-on-react.md
  Inbox: content/inbox/2026-03-07.md

Want to workshop this now (idea-dump style) or save it for the next
content-interview session?
```

If the user wants to workshop it now, run the content development flow inline:
- Show summary + angles
- Ask for their take
- Write a brief immediately
- Offer to draft

---

## Handling Failures

**Fetch fails / paywalled content:**
```
I couldn't fetch the full content from that URL (likely paywalled or
auth-gated). Options:
  1. Paste the content directly and I'll save it
  2. Use Claude Cowork with browser extension to visit the page
  3. Save just the URL as a placeholder — you can paste content later
```

**X article (x.com/i/articles/):**
These often require being logged in. Recommend Option 2 (browser extension) or paste the article text directly.

---

## Prerequisites

No external tools required beyond Exa MCP (already connected).
