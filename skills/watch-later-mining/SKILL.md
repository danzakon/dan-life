---
name: watch-later-mining
description: Pull recent YouTube Watch Later videos and surface content opportunities.
  Use when asked to "check my Watch Later", "mine Watch Later", "YouTube saved videos",
  or "what have I saved on YouTube lately".
argument-hint: "[optional: number of videos to check]"
allowed-tools:
  - Read
  - Write
  - Bash
---

# Watch Later Mining

Ingest YouTube Watch Later videos into the content pipeline. Mirrors `bookmark-mining` exactly — fetches saved videos, filters for content potential, writes raw files and inbox entries with content angles, and registers everything in `index.db`.

The parallel to `bookmark-mining` for YouTube: X bookmarks ↔ YouTube Watch Later.

---

## Prerequisites

`ytquery` must be in PATH with cookies configured. See `skills/ytquery/SKILL.md` for setup.

```bash
# Verify:
ytquery y:watchlater --limit 1
```

If cookies are missing or expired, ytquery will print setup instructions.

---

## Workspace

- `content/raw/youtube/` — transcript and thumbnail storage
- `content/inbox/YYYY-MM-DD.md` — today's inbox
- `content/inbox/_index.md` — master registry
- `content/pipeline/index.db` — item registration
- `content/pipeline/strategy.md` — for angle generation
- `content/pipeline/series.md` — for series connection checks

---

## Workflow

### Step 1: Fetch Watch Later

```bash
ytquery y:watchlater --limit 30
```

Returns a list of saved videos with titles, channels, durations, and URLs. If cookies are expired, ytquery will report it — prompt the user to re-export.

### Step 2: Dedup against index.db

Check which videos are already in the pipeline:

```bash
sqlite3 content/pipeline/index.db \
  "SELECT original_url FROM items WHERE ingest_source = 'watch-later-mining';"
```

Skip any video whose URL is already registered.

### Step 3: Filter for content potential

Evaluate each new video for content relevance:

- **High potential**: Topic directly matches hot topics in `strategy.md`, strong hook, meaty content
- **Medium potential**: Adjacent to themes, interesting signal
- **Low potential**: Off-topic, personal interest only, no content angle visible

If the majority of Watch Later is off-theme (e.g., gaming, recipes), don't force content angles — just note it.

### Step 4: Present new videos

Show the filtered list:

```
Watch Later Mining — 2026-03-07
─────────────────────────────────────────
Fetched 30 videos, 8 new (not yet ingested).

New videos with content potential:

  High potential:
    1. Karpathy: "The Bottleneck of AI in Production" (Lex Fridman, 3h 42m)
       https://youtube.com/watch?v=abc123

  Medium potential:
    2. "Why Most RAG Pipelines Fail" (Weaviate, 24m)
       https://youtube.com/watch?v=def456
    3. "Agentic Coding Patterns" (AI Engineer Summit, 45m)
       https://youtube.com/watch?v=ghi789

  Low potential (skipping):
    5 videos — off-theme

Which ones should I pull transcripts for? (reply with numbers, "all", or "none")
```

Wait for user selection before fetching anything.

### Step 5: Fetch approved videos

For each approved video, assign a `WL` ID and ingest:

**Assign ID:**
```bash
sqlite3 content/pipeline/index.db \
  "SELECT id FROM items WHERE id LIKE '$(date +%Y%m%d)-WL-%' ORDER BY id DESC LIMIT 1;"
```
Increment the NNN portion (start at 001 if no results).

**Fetch metadata:**
```bash
ytquery y:video "{url}" --json
```

**Fetch transcript (requires youtube-transcript-api):**
```bash
ytquery y:transcript "{url}" \
  --output "content/raw/youtube/YYYYMMDD-WL-NNN-{slug}.md"
```

**Download thumbnail:**
```bash
ytquery y:thumbnail "{url}" \
  --output "content/raw/youtube/YYYYMMDD-WL-NNN-{slug}-thumb.jpg"
```

If transcript fetch fails (disabled captions), create a metadata-only raw file.

**Write raw file frontmatter** (if transcript succeeded, prepend to the transcript file; if not, create manually):

```yaml
---
id: YYYYMMDD-WL-NNN
source-type: youtube
ingest-source: watch-later-mining
original-url: {video_url}
author: {channel_name}
captured: ISO 8601 UTC
title: {video_title}
duration: {duration_string}
---
```

**Write inbox entry** to `content/inbox/YYYY-MM-DD.md`:

```markdown
## [YYYYMMDD-WL-NNN] YouTube: {Channel} — {Video Title}

**Status:** unreviewed
**Type:** youtube
**Original:** {video_url}
**Raw file:** content/raw/youtube/YYYYMMDD-WL-NNN-{slug}.md
**Thumbnail:** content/raw/youtube/YYYYMMDD-WL-NNN-{slug}-thumb.jpg
**Ingest source:** watch-later-mining
**Duration:** {duration}

### Summary
[2–3 sentence summary — read the transcript to generate this]

### Content angles (develop all applicable formats now)
1. **Hot take**: [Punchy reaction to the most interesting claim]
2. **Practical**: [Actionable spin for engineers or founders]
3. **Research trigger**: [Does this warrant a deeper research report?]
4. **Series fit**: [Does this connect to anything in series.md?]

### Content tree
- **Reply**: [Reply opportunity to the original creator or topic]
- **Post**: [Standalone short-form angle — draft immediately]
- **Thread**: [Multi-part breakdown if applicable]
- **Article**: [Long-form treatment if the content warrants it]
- **Clip**: [Is there a specific segment worth extracting? Note timestamps.]
- **Series**: [Series connection?]

### Actions
- [ ] Review in content-interview
- [ ] Extract clip at [timestamps] if applicable
```

**Register in index.db:**
```bash
sqlite3 content/pipeline/index.db \
  "INSERT INTO items (id, created_at, source_type, ingest_source, status, current_title, original_url, raw_file)
   VALUES ('{ID}', '{datetime}', 'youtube', 'watch-later-mining', 'raw',
           '{video_title}', '{video_url}', 'content/raw/youtube/{filename}');"
```

**Update `content/inbox/_index.md`** with new item rows.

### Step 6: Present summary

```
Watch Later Mining — 2026-03-07
─────────────────────────────────────────
Fetched 30, filtered to 3 with content potential.

Ingested 3 items to inbox:
  WL-001  Karpathy: AI in Production (Lex Fridman) — high
  WL-002  Why RAG Pipelines Fail (Weaviate) — medium
  WL-003  Agentic Coding Patterns (AI Summit) — medium

Skipped: 27 (off-theme, already ingested, or low potential)

Ready for /content-interview to review.
```

### Step 7: Offer immediate action (optional)

If running interactively:

```
Want to:
  A) Review these in /content-interview now
  B) Workshop the top one immediately
  C) Done — I'll review later
```

---

## Cookie Management

Watch Later requires browser cookies (YouTube blocked API access to Watch Later in 2016). Cookies expire every ~2 weeks.

When `ytquery y:watchlater` fails with an auth error, prompt:

```
Watch Later access failed — cookies may have expired.

To refresh:
  1. Open Firefox in private/incognito mode
  2. Log into YouTube
  3. Navigate to youtube.com/robots.txt
  4. Export youtube.com cookies via "Get cookies.txt LOCALLY" extension
  5. Save to ~/.config/ytquery/cookies.txt
  6. Close the incognito window immediately

Then retry watch-later-mining.
```

---

## Comparison with bookmark-mining

| Aspect | bookmark-mining | watch-later-mining |
|--------|----------------|-------------------|
| Source | X bookmarks | YouTube Watch Later |
| CLI tool | `xquery x:bookmarks` | `ytquery y:watchlater` |
| Auth | OAuth tokens (auto-refresh) | Browser cookies (expire ~2 weeks) |
| ID prefix | `BM` | `WL` |
| Content depth | Tweet text (short) | Transcript (long) |
| Extra output | — | Thumbnail + optional clip |

The key difference: X bookmarks are fully automated (OAuth refresh tokens never expire); Watch Later requires periodic manual cookie re-export.

---

## Source Attribution

Videos from Watch Later are content inspiration, not content to copy. Every piece derived from a Watch Later video must:

- Add your own take, interpretation, or experience
- Reference the source in the raw file and brief
- When posting about a video, credit the creator: "h/t @handle" or "as [Name] puts it..."

Never paraphrase a creator's point without adding something of your own.
