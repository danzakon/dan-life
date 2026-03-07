# YouTube Monitor

Checks approved YouTube channels for new videos, surfaces them for review, and fetches full transcripts on approval. Writes raw transcript files and inbox entries for the content pipeline.

---

## Trigger

- Automated: Part of the daily 7:00 AM ingest Cowork task
- Manual: "Check YouTube channels", "Any new videos from my channels?", "Get transcript for: {url}"

---

## Workspace

- `content/pipeline/sources.md` — approved channel list (YouTube section)
- `content/raw/youtube/` — transcript output files
- `content/inbox/YYYY-MM-DD.md` — today's inbox
- `content/inbox/_index.md` — master item registry
- `content/pipeline/index.db` — SQLite index

## Script

`fetch-transcript.py` — in this skill directory. Fetches YouTube transcripts via `youtube-transcript-api`.

**Prerequisite:** `pip install youtube-transcript-api`

Optional (for title fetching): `yt-dlp` installed and in PATH.

---

## Mode 1: Channel Monitoring (automated / "check channels")

### Step 1: Read approved channels

Read `content/pipeline/sources.md`, extract the YouTube Channels section. Parse channel IDs and any keyword filters.

### Step 2: Check for new videos

For each channel, use the YouTube RSS feed to check for new videos since the last run:

```bash
# YouTube provides RSS feeds for channels without API key:
curl -s "https://www.youtube.com/feeds/videos.xml?channel_id={CHANNEL_ID}" \
  | grep -E '<title>|<link>|<published>' | head -30
```

Alternatively, use `yt-dlp`:
```bash
yt-dlp --flat-playlist --print "%(upload_date)s | %(title)s | %(url)s" \
  --playlist-end 5 "https://www.youtube.com/channel/{CHANNEL_ID}"
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

### Step 5: Fetch approved transcripts

For each approved video, assign a pipeline ID and run the transcript script:

1. **Assign ID** — query `index.db` for highest `YM` ID today, increment:
   ```bash
   sqlite3 content/pipeline/index.db \
     "SELECT id FROM items WHERE id LIKE '$(date +%Y%m%d)-YM-%' ORDER BY id DESC LIMIT 1;"
   ```

2. **Run transcript script:**
   ```bash
   python3 skills/youtube-monitor/fetch-transcript.py \
     "{video_url}" "{ID}" \
     --repo-root /Users/danzakon/dev/life
   ```
   The script prints the output file path on success.

3. **Write inbox entry** — see format below.

4. **Register in index.db.**

5. **Update `_index.md`.**

---

## Mode 2: Direct URL ("Get transcript for: {url}")

Use this when you have a specific video URL outside the monitored channels.

1. Assign an `ID` (still use `YM` prefix — same source type)
2. Run the transcript script with the URL
3. Write inbox entry
4. Register in index.db
5. Optionally surface content angles immediately if the user wants to workshop it now

---

## Inbox Entry Format

```markdown
## [{ID}] YouTube: {Channel} — {Video Title}

**Status:** unreviewed
**Type:** youtube
**Original:** {video_url}
**Raw file:** content/raw/youtube/{ID}-{slug}.md
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
- **Series**: [Does this connect to or seed a series?]

Sequencing when each piece gets posted happens at the queue stage.

### Actions
- [ ] Write post based on this
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

**No transcript available:** Some videos have transcripts disabled. If `fetch-transcript.py` fails, note this in the inbox entry and offer to use `yt-dlp` to download audio for manual transcription.

**Private or unavailable video:** Report to user, skip.

**Channel RSS unavailable:** Fall back to `yt-dlp --flat-playlist` for the channel.

---

## Prerequisites

```bash
pip install youtube-transcript-api   # required
# yt-dlp is optional but recommended for title fetching and fallback
brew install yt-dlp                  # or: pip install yt-dlp
```

No API keys required. YouTube transcripts are fetched directly without authentication.
