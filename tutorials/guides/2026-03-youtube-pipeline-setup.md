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
- **Clips video segments** for social media posting with commentary
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

## Clipping Video Segments for Social Media

This is the workflow for: "I read a transcript, found something interesting at 1:43:00-1:45:00, now I want to clip it, add commentary, and post it."

### The Core Command

yt-dlp's `--download-sections` downloads only the bytes for a segment — no full video download:

```bash
yt-dlp --download-sections "*1:43:00-1:45:00" \
  --force-keyframes-at-cuts \
  -f "bestvideo[ext=mp4][height<=1080]+bestaudio[ext=m4a]/best[ext=mp4]" \
  --merge-output-format mp4 \
  -o "clip.%(ext)s" \
  "https://www.youtube.com/watch?v=XXXXXXXXXXXX"
```

| Flag | Purpose |
|------|---------|
| `--download-sections "*1:43:00-1:45:00"` | Download only this time range. The `*` prefix is required. |
| `--force-keyframes-at-cuts` | Re-encode at cut points for frame-accurate start/end. Without this, clip may start up to 5 seconds early (nearest keyframe). |
| `-f "bestvideo[ext=mp4]..."` | Best quality MP4 video + M4A audio, max 1080p |
| `--merge-output-format mp4` | Output as MP4 container |

### Why `--force-keyframes-at-cuts` Matters

Video is compressed in groups of frames. You can only cleanly cut at a keyframe without re-encoding:

```
YouTube keyframe spacing (typical):
├── I ── P ── P ── P ── P ── I ── P ── P ── P ── P ── I ──
    0s   0.5  1.0  1.5  2.0  2.5  3.0  3.5  4.0  4.5  5.0

Without --force-keyframes-at-cuts:
  Requested start at 1:43:00 → clip starts at 1:42:57 (nearest keyframe)

With --force-keyframes-at-cuts:
  Requested start at 1:43:00 → clip starts exactly at 1:43:00 (re-encodes boundary)
```

The re-encode adds ~30-60 seconds for a 2-minute 1080p clip. Always worth it for social media.

### Adding Burned-In Subtitles

Three-step pipeline:

```
┌──────────────┐     ┌──────────────────┐     ┌──────────────────┐
│  1. Download │     │  2. Download +   │     │  3. Encode with  │
│     clip     │────▶│     trim subs    │────▶│     subs burned  │
│              │     │                  │     │     in           │
│  yt-dlp      │     │  yt-dlp + ffmpeg │     │  ffmpeg          │
│  --download- │     │  --write-auto-sub│     │  -vf subtitles=  │
│  sections    │     │  + trim to range │     │                  │
└──────────────┘     └──────────────────┘     └──────────────────┘
```

```bash
VIDEO_URL="https://www.youtube.com/watch?v=XXXXXXXXXXXX"
START="1:43:00"
END="1:45:00"

# Step 1: Download the clip segment
yt-dlp --download-sections "*${START}-${END}" \
  --force-keyframes-at-cuts \
  -f "bestvideo[ext=mp4][height<=1080]+bestaudio[ext=m4a]/best[ext=mp4]" \
  --merge-output-format mp4 \
  -o "clip_raw.mp4" \
  "$VIDEO_URL"

# Step 2: Download subtitles and trim to clip range
yt-dlp --write-auto-sub --write-sub --sub-lang en \
  --sub-format srt --convert-subs srt \
  --skip-download -o "clip" "$VIDEO_URL"

ffmpeg -i clip.en.srt -ss "$START" -to "$END" clip_trimmed.srt

# Step 3: Burn subtitles + encode for social media
ffmpeg -i clip_raw.mp4 \
  -vf "subtitles=clip_trimmed.srt:force_style='FontName=Arial,FontSize=22,PrimaryColour=&H00FFFFFF,BackColour=&H80000000,BorderStyle=4,MarginV=25'" \
  -c:v libx264 -profile:v high -level 4.0 \
  -crf 22 -preset medium -pix_fmt yuv420p \
  -c:a aac -b:a 128k -movflags +faststart -r 30 \
  clip_final.mp4
```

### Social Media Video Specs

| Platform | Max Size | Max Duration | Resolution | Notes |
|----------|---------|-------------|-----------|-------|
| X (free) | 512 MB | **2:20** | 720p | H.264+AAC required. VP9 rejected. |
| X (Premium+) | 16 GB | 4 hours | 1080p | |
| LinkedIn | 5 GB | 10-15 min | 1080p | Under 60s gets most engagement |
| PostBridge | Handles it | Handles it | Handles it | Upload once, distributes to all platforms |

The 2:20 limit on free X is the key constraint. Most podcast clips will need to be under that.

### Universal Social Media Encode Settings

```bash
# The safe settings that work on every platform
ffmpeg -i input.mp4 \
  -c:v libx264 -profile:v high -level 4.0 \
  -crf 22 -preset medium -pix_fmt yuv420p \
  -c:a aac -b:a 128k -movflags +faststart -r 30 \
  output.mp4
```

| Rule | Why |
|------|-----|
| Always H.264 | X rejects VP9. LinkedIn requires H.264. Only universal codec. |
| Always `yuv420p` | `yuv444p` is higher quality but many devices can't decode it |
| Always `-movflags +faststart` | Instagram and some platforms silently reject without this |
| Always AAC audio | All platforms require or prefer AAC |

### PostBridge Upload Flow for Video Clips

PostBridge fully supports video uploads, which means the clipping workflow can feed directly into the existing publishing pipeline:

```
┌──────────────┐     ┌───────────────┐     ┌──────────────┐
│  Clip video  │     │  PostBridge   │     │  PostBridge   │
│  with yt-dlp │────▶│  media upload │────▶│  create post  │
│  + ffmpeg    │     │               │     │  with media   │
└──────────────┘     │  POST /v1/    │     │               │
                     │  media/create-│     │  POST /v1/    │
                     │  upload-url   │     │  posts        │
                     │  + PUT file   │     │  {media: [id]}│
                     └───────────────┘     └──────────────┘
```

PostBridge handles all platform-specific transcoding behind the scenes. Upload the MP4 once, it distributes to X, LinkedIn, etc.

### Pipeline Integration: Transcript → Clip → Post

Here's how clipping connects to the existing content pipeline:

```
┌─────────────────────────────────────────────────────────────────┐
│                     Clip Pipeline Flow                            │
│                                                                  │
│  1. youtube-monitor fetches transcript                           │
│     └── content/raw/youtube/20260307-YM-001-karpathy-llms.md    │
│                                                                  │
│  2. During content-interview, user identifies a clip-worthy      │
│     segment: "The part about reasoning at 1:43:00 is gold"      │
│                                                                  │
│  3. Clip extraction:                                             │
│     └── yt-dlp --download-sections → ffmpeg encode               │
│     └── content/raw/youtube/20260307-YM-001-clip-1h43m.mp4      │
│                                                                  │
│  4. Write post with video attachment:                            │
│     └── content/posts/2026-W10.md (post text + clip reference)  │
│                                                                  │
│  5. Queue stage:                                                 │
│     └── Upload clip to PostBridge → schedule with commentary     │
│                                                                  │
│  6. index.db tracks the clip as format: "clip"                   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Clip File Naming Convention

```
content/raw/youtube/
├── 20260307-YM-001-karpathy-llms.md              # transcript
├── 20260307-YM-001-karpathy-llms-thumb.jpg        # thumbnail
├── 20260307-YM-001-karpathy-llms-1h43m00s.jpg    # screenshot
└── 20260307-YM-001-karpathy-llms-1h43m-1h45m.mp4 # clip
```

### Schema Consideration

The current `format` field in `index.db` supports `post | thread | article | post+article`. Clips could either:

1. **Use existing format field**: A clip is always paired with a post, so `format: "post"` with the clip as an attachment
2. **Add `clip` as a format**: Treat clips as a first-class content type
3. **Add a `media_file` column**: Track attached media separately from the content format

Option 1 is simplest and matches reality — a clip is a post with a video attached, not a standalone format.

### Reusable Script: `ytclip.sh`

This belongs in `skills/youtube-monitor/` alongside `fetch-transcript.py`:

```bash
#!/bin/bash
# ytclip.sh — Extract a clip from a YouTube video, ready for social media
#
# Usage:
#   ./ytclip.sh <url> <start> <end> [--subs] [--output name]
#
# Examples:
#   ./ytclip.sh "https://youtube.com/watch?v=abc" "1:43:00" "1:45:00"
#   ./ytclip.sh "https://youtube.com/watch?v=abc" "1:43:00" "1:45:00" --subs
#   ./ytclip.sh "https://youtube.com/watch?v=abc" "0:30" "2:00" --output my_clip

set -euo pipefail

URL="$1"
START="$2"
END="$3"
SUBS=false
OUTPUT="clip_$(date +%Y%m%d_%H%M%S)"

shift 3
while [[ $# -gt 0 ]]; do
  case $1 in
    --subs) SUBS=true; shift ;;
    --output) OUTPUT="$2"; shift 2 ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

echo "Downloading clip: ${START} to ${END}"
echo "Subtitles: ${SUBS}"

# Step 1: Download clip segment
yt-dlp --download-sections "*${START}-${END}" \
  --force-keyframes-at-cuts \
  -f "bestvideo[ext=mp4][height<=1080]+bestaudio[ext=m4a]/best[ext=mp4]" \
  --merge-output-format mp4 \
  -o "${OUTPUT}_raw.mp4" \
  "$URL"

if [ "$SUBS" = true ]; then
  echo "Downloading subtitles..."
  yt-dlp --write-auto-sub --write-sub --sub-lang en \
    --sub-format srt --convert-subs srt \
    --skip-download -o "${OUTPUT}" "$URL" 2>/dev/null || true

  SRT_FILE=$(ls ${OUTPUT}*.srt 2>/dev/null | head -1)

  if [ -n "$SRT_FILE" ]; then
    ffmpeg -y -i "$SRT_FILE" -ss "$START" -to "$END" "${OUTPUT}_trimmed.srt" 2>/dev/null
    ffmpeg -y -i "${OUTPUT}_raw.mp4" \
      -vf "subtitles=${OUTPUT}_trimmed.srt:force_style='FontName=Arial,FontSize=22,PrimaryColour=&H00FFFFFF,BackColour=&H80000000,BorderStyle=4,MarginV=25'" \
      -c:v libx264 -profile:v high -level 4.0 \
      -crf 22 -preset medium -pix_fmt yuv420p \
      -c:a aac -b:a 128k -movflags +faststart -r 30 \
      "${OUTPUT}.mp4"
    rm -f "$SRT_FILE" "${OUTPUT}_trimmed.srt"
  else
    echo "No subtitles found. Encoding without."
    SUBS=false
  fi
fi

if [ "$SUBS" = false ]; then
  ffmpeg -y -i "${OUTPUT}_raw.mp4" \
    -c:v libx264 -profile:v high -level 4.0 \
    -crf 22 -preset medium -pix_fmt yuv420p \
    -c:a aac -b:a 128k -movflags +faststart -r 30 \
    "${OUTPUT}.mp4"
fi

rm -f "${OUTPUT}_raw.mp4"
echo "Done: ${OUTPUT}.mp4"
ls -lh "${OUTPUT}.mp4"
```

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

**Phase 3: Video clipping**

- [ ] Create `ytclip.sh` in `skills/youtube-monitor/`
- [ ] Test clip extraction on a real podcast (with and without subs)
- [ ] Test PostBridge video upload via `/v1/media/create-upload-url`
- [ ] Update `write-post` skill to handle video attachments
- [ ] Add clip file naming convention to SYSTEM.md
- [ ] End-to-end test: transcript → identify segment → clip → post with commentary → schedule

**Phase 4: Watch Later integration**

- [ ] Set up Firefox cookie export workflow
- [ ] Create `~/.config/youtube/cookies.txt` with valid session
- [ ] Add `WL` source prefix to SYSTEM.md and pipeline docs
- [ ] Build watch-later mode into youtube-monitor (or create separate skill)
- [ ] Test: export Watch Later → dedup → present → ingest

**Phase 5: Automation polish**

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
| Clip starts a few seconds early | Cutting at nearest keyframe | Add `--force-keyframes-at-cuts` |
| Clip audio/video out of sync | Separate stream download | Let yt-dlp handle merge; don't use `--get-url` for clips |
| X rejects video upload | Wrong codec (VP9, HEVC) | Ensure H.264 + AAC in MP4. Use `-c:v libx264 -c:a aac` |
| Clip exceeds X 2:20 limit | Free tier duration cap | Keep clips under 2:20 or use Premium |

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
