---
name: youtube-monitor
description: Check approved YouTube channels for new videos, surface them for review,
  and fetch transcripts on approval. Use when asked to "check YouTube channels",
  "any new videos?", "get transcript for URL", or as part of daily ingest.
argument-hint: "[optional: specific channel or URL]"
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
  - Grep
---

# YouTube Monitor

Checks approved YouTube channels for new videos, surfaces them for review, and fetches full transcripts on approval. Writes raw transcript files and inbox entries for the content pipeline.

Uses the `ytquery` CLI tool for all YouTube operations.

---

## Trigger

- Automated: Part of the daily 7:00 AM ingest Cowork task
- Manual: "Check YouTube channels", "Any new videos from my channels?", "Get transcript for: {url}"

---

## Workspace

- `content/pipeline/sources.md` — approved channel list (YouTube section)
- `content/raw/youtube/` — transcript + thumbnail output files
- `content/inbox/YYYY-MM-DD.md` — today's inbox
- `content/inbox/_index.md` — master item registry
- `content/pipeline/index.db` — SQLite index

## Prerequisites

The `ytquery` CLI must be in the user's PATH. See `skills/ytquery/SKILL.md` for setup.

---

## Mode 1: Channel Monitoring (automated / "check channels")

### Step 1: Read approved channels

Read `content/pipeline/sources.md`, extract the YouTube Channels section. Parse channel handles/IDs and any keyword filters.

### Step 2: Check for new videos

For each channel, use ytquery to check for recent uploads:

```bash
ytquery y:channel @handle --limit 5
```

Or via RSS for lighter polling:

```bash
ytquery y:rss @handle
# Then fetch RSS:
curl -s "RSS_URL" | grep -E '<title>|<link>|<published>' | head -30
```

Collect videos published in the last 7 days (or since `last-run` date in `_index.md`).

### Step 3: Apply keyword filters

If a channel has a keyword filter in `sources.md`, only surface videos whose titles contain at least one of the filter keywords (case-insensitive).

### Step 4: Present new videos

Show a list of new videos from approved channels. **Do not fetch transcripts automatically.** Ask which ones to pull:

```
New videos since your last check:

Lex Fridman
  1. "Andrej Karpathy: LLMs, AGI, and the Future of AI" (2026-03-05, 3h 42m)
     https://youtube.com/watch?v=abc123

MKBHD
  2. "How AI is changing software development" (2026-03-06, 18m)
     https://youtube.com/watch?v=def456

Which ones should I pull transcripts for? (reply with numbers, or "all", or "none")
```

Wait for confirmation before fetching any transcripts.

### Step 5: Fetch approved transcripts and thumbnails

For each approved video, assign a pipeline ID and fetch content:

1. **Assign ID** — query `index.db` for highest `YM` ID today, increment:
   ```bash
   sqlite3 content/pipeline/index.db \
     "SELECT id FROM items WHERE id LIKE '$(date +%Y%m%d)-YM-%' ORDER BY id DESC LIMIT 1;"
   ```

2. **Fetch transcript:**
   ```bash
   ytquery y:transcript "{video_url}" \
     --output "content/raw/youtube/{ID}-{slug}.md"
   ```

3. **Download thumbnail:**
   ```bash
   ytquery y:thumbnail "{video_url}" \
     --output "content/raw/youtube/{ID}-{slug}-thumb.jpg"
   ```

4. **Get video metadata** (for duration, publish date):
   ```bash
   ytquery y:video "{video_url}" --json
   ```

5. **Write inbox entry** — see format below.

6. **Register in index.db.**

7. **Update `_index.md`.**

---

## Mode 2: Direct URL ("Get transcript for: {url}")

Use this when you have a specific video URL outside the monitored channels.

1. Assign an `ID` (still use `YM` prefix — same source type)
2. Fetch transcript: `ytquery y:transcript "{url}" --output ...`
3. Download thumbnail: `ytquery y:thumbnail "{url}" --output ...`
4. Get metadata: `ytquery y:video "{url}" --json`
5. Write inbox entry
6. Register in index.db
7. Optionally surface content angles immediately if the user wants to workshop it now

---

## Mode 3: Watch Later Mining

Similar to bookmark-mining but for YouTube Watch Later.

1. **Fetch Watch Later list:**
   ```bash
   ytquery y:watchlater --limit 30
   ```

2. **Dedup against index.db** — skip videos already ingested.

3. **Present new videos** to user (same as channel monitor format).

4. **For approved videos**, follow the same ingest flow as Mode 2.

Note: Watch Later requires cookie setup. See `ytquery` SKILL.md for instructions. Cookies expire every ~2 weeks.

---

## Mode 4: Clip Extraction

When a transcript reveals a clip-worthy segment:

1. **Identify the timestamp range** from the transcript
2. **Extract the clip:**
   ```bash
   ytquery y:clip "{video_url}" "1:43:00" "1:45:00" \
     --output "content/raw/youtube/{ID}-{slug}-1h43m-1h45m"
   ```
   Add `--subs` for burned-in subtitles.

3. **Clip is social-media-ready** (H.264, AAC, MP4, faststart)

4. **Reference the clip** in the post draft:
   ```markdown
   **Media:** content/raw/youtube/{ID}-{slug}-1h43m-1h45m.mp4
   ```

5. Upload via PostBridge when scheduling.

---

## Inbox Entry Format

```markdown
## [{ID}] YouTube: {Channel} — {Video Title}

**Status:** unreviewed
**Type:** youtube
**Original:** {video_url}
**Raw file:** content/raw/youtube/{ID}-{slug}.md
**Thumbnail:** content/raw/youtube/{ID}-{slug}-thumb.jpg
**Ingest source:** youtube-monitor
**Duration:** {duration if available}
**Published:** {publish date}

### Summary
[2–3 sentence summary of what the video covers — read the transcript to generate this]

### Content angles
1. **Hot take**: [Punchy reaction to the most interesting claim]
2. **Practical**: [Actionable spin for engineers or founders]
3. **Research trigger**: [Does this warrant a deeper research report?]
4. **Series fit**: [Does this connect to anything in series.md?]

### Content tree (develop all applicable formats now)
- **Reply**: [If there's a specific person or post to respond to]
- **Post**: [Standalone short-form angle — draft immediately]
- **Thread**: [Multi-part breakdown — draft immediately if applicable]
- **Article**: [Long-form treatment — draft immediately, don't hold]
- **Clip**: [Is there a specific segment worth clipping? Note timestamps.]
- **Series**: [Does this connect to or seed a series?]

Sequencing when each piece gets posted happens at the queue stage.

### Actions
- [ ] Write post based on this
- [ ] Extract clip at [timestamps]
- [ ] Research deeper
- [ ] Skip
```

---

## index.db Registration

```bash
sqlite3 content/pipeline/index.db \
  "INSERT INTO items (id, created_at, source_type, ingest_source, status, current_title, original_url, raw_file)
   VALUES ('{ID}', '{datetime}', 'youtube', 'youtube-monitor', 'raw',
           '{video_title}', '{video_url}', 'content/raw/youtube/{filename}');"
```

---

## Error Handling

**No transcript available:** Some videos have transcripts disabled. If `ytquery y:transcript` fails, note this in the inbox entry and offer alternatives:
- `ytquery y:video` for metadata-only ingestion
- Manual transcription from audio

**Private or unavailable video:** Report to user, skip.

**Watch Later cookies expired:** `ytquery y:watchlater` will report the error. Prompt user to re-export cookies.

**Channel RSS unavailable:** Fall back to `ytquery y:channel` which uses yt-dlp directly.
