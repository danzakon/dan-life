# How to Set Up YouTube Monitoring for the Content Pipeline

**Date:** 2026-03-07
**Category:** Tutorial
**Difficulty:** Intermediate
**Time estimate:** ~30 minutes
**Prerequisites:** macOS with Homebrew, Python 3.10+, a YouTube account

---

## What You'll Build

A working YouTube monitoring system that:
- Monitors channels for new videos via RSS
- Fetches transcripts and thumbnails
- Extracts screenshots at specific timestamps
- Ingests Watch Later videos (with known limitations)
- Integrates with the content pipeline (`index.db`, inbox, raw files)

---

## Current State Assessment

Before building, here's where things stand:

### What Exists

| Component | Status | Notes |
|-----------|--------|-------|
| `skills/youtube-monitor/SKILL.md` | Done | Well-structured skill definition |
| `skills/youtube-monitor/fetch-transcript.py` | **BROKEN** | Uses removed API (see below) |
| `sources.md` YouTube section | Exists | Template only, no real channels |
| `content/raw/youtube/` | Exists | Empty, ready for files |
| `yt-dlp` | Not installed | |
| `youtube-transcript-api` | Not installed | |
| `ffmpeg` | Not installed | |
| `deno` | Not installed | Required by yt-dlp since 2025.11.12 |

### Critical Issue: fetch-transcript.py Uses a Removed API

The current script uses `YouTubeTranscriptApi.list_transcripts()` and `transcript.fetch()` — static methods that were **removed in youtube-transcript-api v1.2.0** (July 2025). The library underwent a major rewrite:

```
OLD API (removed)                          NEW API (v1.0.0+)
─────────────────                          ──────────────────
YouTubeTranscriptApi.list_transcripts()    ytt_api = YouTubeTranscriptApi()
transcript.fetch()                         ytt_api.fetch(video_id)
YouTubeTranscriptApi.get_transcript()      ytt_api.list(video_id)
```

**The script will crash on install.** This must be fixed before anything else.

---

## Prerequisites

### Step 1: Install system dependencies

```bash
brew install deno ffmpeg
```

| Package | Why |
|---------|-----|
| `deno` | yt-dlp requires an external JS runtime for YouTube since 2025.11.12. YouTube's JS challenges exceed yt-dlp's built-in interpreter. Deno is the recommended runtime. |
| `ffmpeg` | Frame extraction from video streams, thumbnail format conversion (WebP to JPG) |

Verify:

```bash
deno --version
# deno 2.x.x

ffmpeg -version | head -1
# ffmpeg version 7.x ...
```

### Step 2: Install Python packages

```bash
pip3 install yt-dlp youtube-transcript-api
```

| Package | Version | Purpose |
|---------|---------|---------|
| `yt-dlp` | 2026.03.03+ | Video metadata, thumbnails, channel listing, Watch Later access |
| `youtube-transcript-api` | 1.2.4+ | Transcript fetching (new instance-based API) |

Verify:

```bash
yt-dlp --version
# 2026.03.03

python3 -c "import youtube_transcript_api; print(youtube_transcript_api.__version__)"
# 1.2.4
```

---

## Step 3: Fix fetch-transcript.py

The script at `skills/youtube-monitor/fetch-transcript.py` must be updated to use the new API. The key change is in the `fetch_transcript()` function:

**Before (broken):**
```python
from youtube_transcript_api import YouTubeTranscriptApi

transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
transcript = transcript_list.find_manually_created_transcript(['en'])
return transcript.fetch(), transcript.language_code, transcript.is_generated
```

**After (working):**
```python
from youtube_transcript_api import YouTubeTranscriptApi

ytt_api = YouTubeTranscriptApi()

# Try manual English first, then auto-generated, then any language
transcript_list = ytt_api.list(video_id)
try:
    transcript = transcript_list.find_manually_created_transcript(['en'])
except Exception:
    try:
        transcript = transcript_list.find_generated_transcript(['en'])
    except Exception:
        transcript = list(transcript_list)[0]

fetched = transcript.fetch()
return fetched.to_raw_data(), transcript.language_code, transcript.is_generated
```

The `to_raw_data()` call returns the same `[{'text': ..., 'start': ..., 'duration': ...}]` format the rest of the script expects, so no other changes are needed.

### Test with a real video

```bash
python3 skills/youtube-monitor/fetch-transcript.py \
  "https://www.youtube.com/watch?v=jvqFAi7vkBc" \
  "20260307-YM-001" \
  --repo-root /Users/danzakon/dev/life
```

Expected output: a file path like `content/raw/youtube/20260307-YM-001-{slug}.md`.

---

## Step 4: Add YouTube channels to sources.md

The `sources.md` YouTube section has template examples but no real channels. Add channels you want to monitor:

```
# Format: {channel-id}  # channel name | keyword filter (optional)

UCbmNph6atAoGfqLoCL_duAg  # Lex Fridman
UCsBjURrPoezykLs9EqgamOA  # Fireship
```

### How to find a channel ID

```bash
yt-dlp --playlist-items 0 \
  -O "playlist:%(channel_id)s" \
  "https://www.youtube.com/@lexfridman"
```

| Part | Meaning |
|------|---------|
| `--playlist-items 0` | Extract only playlist-level metadata, no video pages |
| `-O "playlist:..."` | Print format, scoped to playlist metadata |
| `%(channel_id)s` | The internal channel ID (starts with UC...) |

The channel ID is what you need for both RSS feeds and yt-dlp queries. The `@handle` format works with yt-dlp but not with RSS.

---

## Step 5: Test channel monitoring

### Via RSS (lightweight, used in the skill)

```bash
CHANNEL_ID="UCbmNph6atAoGfqLoCL_duAg"  # Lex Fridman
curl -s "https://www.youtube.com/feeds/videos.xml?channel_id=${CHANNEL_ID}" \
  | grep -oP '(?<=<title>).*?(?=</title>)' | head -10
```

### Via yt-dlp (richer metadata)

```bash
yt-dlp --flat-playlist --lazy-playlist -I :5 \
  --print "%(title)s | %(duration_string)s | %(url)s" \
  "https://www.youtube.com/@lexfridman/videos"
```

| Flag | Purpose |
|------|---------|
| `--flat-playlist` | Extract from playlist page only, don't fetch each video's page |
| `--lazy-playlist` | Stream results as they arrive (don't wait for all) |
| `-I :5` | First 5 items only |
| `--print "..."` | Custom output format per video |

---

## YouTube Screenshots

Two capabilities, two very different approaches:

### Capability 1: Video thumbnails (the preview image)

Thumbnails are available at predictable URLs — no download needed:

```
https://img.youtube.com/vi/{VIDEO_ID}/maxresdefault.jpg   # 1280x720 (HD+ only)
https://img.youtube.com/vi/{VIDEO_ID}/hqdefault.jpg       # 480x360 (always exists)
https://img.youtube.com/vi/{VIDEO_ID}/mqdefault.jpg       # 320x180 (clean 16:9)
```

Download with fallback:

```bash
VIDEO_ID="jvqFAi7vkBc"
curl -f -o thumbnail.jpg "https://img.youtube.com/vi/${VIDEO_ID}/maxresdefault.jpg" \
  || curl -o thumbnail.jpg "https://img.youtube.com/vi/${VIDEO_ID}/hqdefault.jpg"
```

Or via yt-dlp (handles WebP conversion):

```bash
yt-dlp --skip-download --write-thumbnail --convert-thumbnails jpg \
  -o "content/raw/youtube/%(id)s.%(ext)s" "VIDEO_URL"
```

### Capability 2: Frame at a specific timestamp

This is the powerful one — extract any frame from any video without downloading the whole thing:

```bash
ffmpeg -ss "00:08:14" \
  -i "$(yt-dlp -f 'bv*[height<=1080]' --get-url 'YOUTUBE_URL')" \
  -frames:v 1 -q:v 2 screenshot.jpg
```

How it works:

```
┌──────────┐     ┌──────────────┐     ┌──────────┐
│  yt-dlp  │────▶│  YouTube CDN │────▶│  ffmpeg  │
│ --get-url│     │  (direct URL)│     │ -ss -i   │
│          │     │              │     │ (HTTP    │
│ Resolves │     │  Temporary   │     │  range   │
│ stream   │     │  stream URL  │     │  seek)   │
│ URL only │     │              │     │          │
└──────────┘     └──────────────┘     └────┬─────┘
                                           │
                                    ┌──────▼──────┐
                                    │ screenshot  │
                                    │   .jpg      │
                                    └─────────────┘
```

| Part | Meaning |
|------|---------|
| `yt-dlp -f 'bv*[height<=1080]'` | Select best video stream up to 1080p |
| `--get-url` | Print the direct CDN URL, don't download |
| `ffmpeg -ss "00:08:14"` | Seek to timestamp (before `-i` = fast input seeking) |
| `-i "$(...)"` | Use the resolved URL as input |
| `-frames:v 1` | Extract exactly one frame |
| `-q:v 2` | JPEG quality (1-31, lower = better) |

**Important caveat:** The CDN URL from `--get-url` expires after a few hours. Always resolve and consume in the same step — don't cache the URL.

### Pipeline integration for screenshots

Screenshots could live alongside raw transcript files:

```
content/raw/youtube/
├── 20260307-YM-001-karpathy-llms.md         # transcript
├── 20260307-YM-001-karpathy-llms-thumb.jpg  # thumbnail
└── 20260307-YM-001-karpathy-llms-08m14s.jpg # screenshot at timestamp
```

The naming convention `{ID}-{slug}-{timestamp}.jpg` keeps screenshots associated with their source video. This could be added to `fetch-transcript.py` as an optional `--screenshot` flag, or handled as a separate utility.

### When screenshots are useful for content

| Use Case | Approach |
|----------|----------|
| Social card for a post about a video | Thumbnail (predictable URL) |
| Highlighting a specific moment | Frame at timestamp |
| Diagram or code shown in video | Frame at timestamp |
| Article header image | Thumbnail or styled frame |

---

## YouTube Watch Later as an Ingest Source

### The Reality

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   X Bookmarks (xquery)          YouTube Watch Later             │
│   ────────────────────          ─────────────────────           │
│   OAuth 2.0 API access          API blocked since 2016          │
│   Refresh tokens (permanent)    Browser cookies (expire ~2 wk)  │
│   Full automation                Semi-manual cookie refresh      │
│   xquery x:bookmarks            yt-dlp --cookies cookies.txt    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

YouTube permanently blocked Watch Later (`WL`) and Watch History (`HL`) from the Data API on September 12, 2016. There is no OAuth path. The only access method is browser cookies.

### Best approach: yt-dlp with cookie file

```bash
yt-dlp --cookies ~/.config/youtube/cookies.txt \
  --flat-playlist \
  --print "%(title)s | %(id)s | %(url)s | %(duration_string)s | %(channel)s" \
  "https://www.youtube.com/playlist?list=WL"
```

Or for JSON output:

```bash
yt-dlp --cookies ~/.config/youtube/cookies.txt \
  --flat-playlist --dump-json \
  "https://www.youtube.com/playlist?list=WL"
```

### Cookie setup (one-time, repeat every ~2 weeks)

1. Install "Get cookies.txt LOCALLY" Firefox extension (Firefox recommended — Chrome encrypts cookies since mid-2024, making extraction unreliable)
2. Open an **incognito/private** window in Firefox
3. Log into YouTube
4. Navigate to `https://www.youtube.com/robots.txt` (prevents cookie rotation)
5. Export `youtube.com` cookies via the extension
6. Save to `~/.config/youtube/cookies.txt`
7. **Close the incognito window immediately** (so YouTube never rotates those cookies)

```bash
mkdir -p ~/.config/youtube
# Move exported file:
mv ~/Downloads/cookies.txt ~/.config/youtube/cookies.txt
```

### Why the incognito trick matters

YouTube rotates session cookies on active tabs. By logging in via incognito, exporting, and immediately closing, the cookies are never rotated. They can last weeks or even months if the session is never reopened.

### Pipeline integration design

A new skill (or mode within youtube-monitor) — call it `watch-later-mining`:

```
┌────────────────────────────────────────────────────────────┐
│               Watch Later Mining Workflow                    │
│                                                             │
│  1. yt-dlp --cookies ... --flat-playlist --dump-json WL    │
│     └── Get list of Watch Later videos                     │
│                                                             │
│  2. Dedup against index.db                                  │
│     └── Skip videos already ingested                       │
│                                                             │
│  3. Present new videos to user (same as channel monitor)   │
│     └── User picks which ones to pull                      │
│                                                             │
│  4. For approved videos:                                    │
│     ├── Assign WL prefix ID (new prefix)                   │
│     ├── Fetch transcript                                    │
│     ├── Download thumbnail                                  │
│     ├── Write raw file + inbox entry                       │
│     └── Register in index.db                               │
│                                                             │
│  5. If cookies expired → notify user to re-export          │
│                                                             │
└────────────────────────────────────────────────────────────┘
```

This would need a new source prefix. Suggested: `WL` (watch-later).

| Prefix | Source |
|--------|--------|
| `BM` | bookmark-mining |
| `XM` | x-account-monitor |
| `RM` | reply-monitor |
| `YM` | youtube-monitor (channel) |
| `WL` | watch-later-mining (new) |
| `SR` | save-raw |
| `ID` | idea-dump |
| `RS` | research |

---

## Skill Evaluation and Improvement Roadmap

### Current Gaps

```
┌─────────────────────────────────────────────────────────────┐
│                    YouTube Skill Health                       │
├───────────────────────────┬──────┬──────────────────────────┤
│ Component                 │ Score│ Issue                     │
├───────────────────────────┼──────┼──────────────────────────┤
│ SKILL.md definition       │  9/10│ Well-structured           │
│ fetch-transcript.py       │  0/10│ Uses removed API          │
│ Dependencies installed    │  0/10│ Nothing installed          │
│ sources.md channels       │  2/10│ Template only, no real IDs│
│ Thumbnail support         │  0/10│ Not implemented           │
│ Screenshot support        │  0/10│ Not implemented           │
│ Watch Later support       │  0/10│ Not designed yet          │
│ Cowork task integration   │  5/10│ Designed but not testable │
│ Error handling            │  7/10│ Good in SKILL.md          │
│ Pipeline integration      │  8/10│ ID scheme, inbox format   │
└───────────────────────────┴──────┴──────────────────────────┘
```

### Recommended Improvement Order

**Phase 1: Get it working (blockers)**

- [ ] Install dependencies (`brew install deno ffmpeg && pip3 install yt-dlp youtube-transcript-api`)
- [ ] Fix `fetch-transcript.py` to use new youtube-transcript-api v1.2+ API
- [ ] Test transcript fetch on a real video end-to-end
- [ ] Add at least 3 real channel IDs to `sources.md`

**Phase 2: Enhance capabilities**

- [ ] Add thumbnail download to `fetch-transcript.py` (via direct URL pattern — no yt-dlp needed)
- [ ] Create `yt-screenshot.sh` utility for timestamp-based frame extraction
- [ ] Add `--thumbnail` and `--screenshot TIMESTAMP` flags to the transcript script
- [ ] Store thumbnails alongside transcripts: `{ID}-{slug}-thumb.jpg`

**Phase 3: Watch Later integration**

- [ ] Set up Firefox cookie export workflow
- [ ] Create `~/.config/youtube/cookies.txt` with valid session
- [ ] Add `WL` source prefix to SYSTEM.md and pipeline docs
- [ ] Build watch-later mode into youtube-monitor (or create separate skill)
- [ ] Test: export Watch Later → dedup → present → ingest

**Phase 4: Automation polish**

- [ ] Add `--cookies` fallback to channel monitoring (for age-restricted videos)
- [ ] Add cookie expiration detection and user notification
- [ ] Integrate with Cowork daily task (7:00 AM ingest)
- [ ] Add `jq` parsing for yt-dlp JSON output in channel monitoring
- [ ] Consider RSS + yt-dlp hybrid: RSS for polling, yt-dlp for enrichment

---

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|---------|
| `yt-dlp` fails on YouTube URLs | Missing JS runtime | `brew install deno` |
| `youtube-transcript-api` AttributeError on `list_transcripts` | Using old API (removed in v1.2.0) | Update script to instance-based API |
| `maxresdefault.jpg` returns 404 | Video is not HD | Fall back to `hqdefault.jpg` |
| Watch Later returns empty | Cookies expired or invalid | Re-export from incognito session |
| `--cookies-from-browser chrome` fails | Chrome locks cookie DB while running | Quit Chrome first, or use Firefox |
| `PoTokenRequired` from transcript API | YouTube server-side restriction | No workaround; try again later or use yt-dlp `--write-subs` as fallback |
| Frame extraction is slow | `-ss` placed after `-i` | Move `-ss` before `-i` for input seeking |
| yt-dlp `--get-url` returns stale URL | CDN URLs expire after hours | Always resolve and consume in one step |

---

## What's Next

- Fix `fetch-transcript.py` and test (Phase 1 — immediate)
- Install dependencies and verify
- Add real channels to `sources.md`
- Build screenshot utility
- Set up Watch Later cookie workflow

---

## Sources

- [youtube-transcript-api v1.0.0 migration guide](https://github.com/jdepoix/youtube-transcript-api)
- [yt-dlp documentation](https://github.com/yt-dlp/yt-dlp)
- [yt-dlp Wiki: Exporting YouTube cookies](https://github.com/yt-dlp/yt-dlp/wiki/Extractors#exporting-youtube-cookies)
- [YouTube Data API v3 revision history (WL blocked)](https://developers.google.com/youtube/v3/revision_history#september-15-2016)
- [YouTube thumbnail URL patterns](https://stackoverflow.com/questions/2068344/how-do-i-get-a-youtube-video-thumbnail-from-the-youtube-api)
- [yt-playlist-export (Watch Later wrapper)](https://github.com/daydiff/yt-playlist-export)
