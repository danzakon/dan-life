# yt-dlp & youtube-transcript-api: Capabilities Research

**Date:** 2026-03-07
**Purpose:** Evaluate current state of both tools for YouTube channel monitoring, metadata extraction, thumbnail downloading, and transcript retrieval.

---

## 1. yt-dlp: Current State

### Version & Release Cadence

| Field | Value |
|-------|-------|
| Latest stable | `2026.03.03` |
| PyPI | `pip install yt-dlp` |
| Python required | >= 3.10 (CPython), >= 3.11 (PyPy) |
| License | Unlicense |
| Monthly downloads | ~10.2M |

Releases follow a date-based versioning scheme (`YYYY.MM.DD`) with frequent updates -- roughly every 1-3 weeks.

### Critical Breaking Change: External JS Runtime Required

As of **2025.11.12**, yt-dlp requires an external JavaScript runtime for full YouTube support.

```
Why:  YouTube's JS challenges now exceed what yt-dlp's built-in
      JS interpreter can handle.

What: Install Deno (recommended), Node.js, or another supported
      JS runtime alongside yt-dlp.

Impact: Without a JS runtime, YouTube downloads will fail or
        produce incomplete results.
```

**Installation (macOS):**
```bash
# Deno (recommended by yt-dlp maintainers)
brew install deno

# Or Node.js
brew install node
```

yt-dlp auto-detects available runtimes. No configuration needed after installation.

### Other Notable Changes (2025-2026)

| Version | Change |
|---------|--------|
| 2025.11.12 | JS runtime requirement for YouTube |
| 2025.12.08 | Fix `--cookies-from-browser` for Firefox 147+ |
| 2025.12.08 | Detect "super resolution" AI-upscaled formats |
| 2025.12.08 | Extract all automatic caption languages |
| 2026.01.31 | Remove broken `ios_downgraded` player client |
| 2026.02.04 | Default to `tv` player JS variant |
| 2026.02.21 | **CVE-2026-26331**: Arbitrary command injection with `--netrc-cmd` (patched) |
| 2026.02.21 | Cookies: ignore cookies with control characters |
| 2026.03.03 | Force specific YouTube player version |

---

## 2. yt-dlp: Thumbnail Download Capabilities

### Command-Line Options

| Flag | Purpose |
|------|---------|
| `--write-thumbnail` | Download the best quality thumbnail |
| `--write-all-thumbnails` | Download all available thumbnail sizes |
| `--list-thumbnails` | List available thumbnails (ID, width, height, URL) |
| `--convert-thumbnails FORMAT` | Convert to `jpg`, `png`, or `webp` |
| `--skip-download` | Skip video download (thumbnail-only mode) |

### Download Thumbnail Only (No Video)

```bash
# Download best thumbnail as JPG
yt-dlp --skip-download --write-thumbnail --convert-thumbnails jpg "VIDEO_URL"

# Download to a specific directory
yt-dlp --skip-download --write-thumbnail --convert-thumbnails jpg \
  -o "/path/to/thumbnails/%(id)s.%(ext)s" "VIDEO_URL"

# Batch download thumbnails from a file of URLs
yt-dlp --skip-download --write-thumbnail --convert-thumbnails jpg \
  -a urls.txt -o "/path/to/thumbnails/%(id)s.%(ext)s"
```

| Part | Meaning |
|------|---------|
| `--skip-download` | Do not download the video file |
| `--write-thumbnail` | Download the highest-quality thumbnail |
| `--convert-thumbnails jpg` | Convert downloaded thumbnail to JPG format |
| `-o "..."` | Output template controlling filename and directory |
| `-a urls.txt` | Read URLs from a batch file |

### Listing Available Thumbnails

```bash
yt-dlp --list-thumbnails "https://www.youtube.com/watch?v=VIDEO_ID"
```

Output shows all available thumbnail sizes with their dimensions:
```
[info] Available thumbnails for VIDEO_ID:
ID  Width  Height  URL
0   60     60      https://lh3.googleusercontent.com/...
1   120    90      https://i.ytimg.com/vi/VIDEO_ID/...
...
47  1920   1080    https://i.ytimg.com/vi/VIDEO_ID/maxresdefault.webp
```

### Python API for Thumbnails

```python
import yt_dlp

ydl_opts = {
    'writethumbnail': True,          # Note: no hyphens in Python API
    'skip_download': True,
    'outtmpl': 'thumbnails/%(id)s.%(ext)s',
    'postprocessors': [{
        'key': 'FFmpegThumbnailsConvertor',
        'format': 'jpg',
    }],
}

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    ydl.download(['VIDEO_URL'])
```

### Quality Notes

- YouTube serves thumbnails in `webp` format by default
- Max resolution is typically 1280x720 (`maxresdefault`) or 1920x1080
- The `--convert-thumbnails jpg` flag requires `ffmpeg` to be installed
- Thumbnail quality from yt-dlp is limited to what YouTube provides as static images -- it will not extract frames from the video itself

---

## 3. yt-dlp: Channel Monitoring & Metadata Extraction

### Get Latest N Videos from a Channel

```bash
# Get the 15 most recent videos (URLs only)
yt-dlp --flat-playlist --lazy-playlist -I :15 \
  --print url "https://www.youtube.com/@CHANNEL/videos"
```

| Part | Meaning |
|------|---------|
| `--flat-playlist` | Extract metadata without downloading full video pages |
| `--lazy-playlist` | Process playlist entries as they are received (streaming) |
| `-I :15` | Playlist item spec: first 15 items only |
| `--print url` | Print the video URL for each entry |

### Extract Metadata Without Downloading

**Option A: `--print` (lightweight, specific fields)**

```bash
yt-dlp --flat-playlist --lazy-playlist -I :10 \
  --print "%(title)s | %(duration_string)s | %(upload_date)s | %(url)s" \
  "https://www.youtube.com/@CHANNEL/videos"
```

Available fields with `--flat-playlist`: `title`, `url`, `id`, `duration`, `duration_string`, `view_count`, `channel`, `channel_id`, `channel_url`, `description` (may be truncated).

**Note:** `upload_date` may show as `NA` with `--flat-playlist`. To get approximate dates, add:
```bash
--extractor-args "youtubetab:approximate_date"
```

**Option B: `--dump-json` (full JSON per video)**

```bash
# Full metadata as JSON (one JSON object per line)
yt-dlp --flat-playlist --lazy-playlist -I :10 \
  --dump-json "https://www.youtube.com/@CHANNEL/videos"
```

Each line is a complete JSON object. Parse with `jq`:
```bash
yt-dlp --flat-playlist -I :10 --dump-json \
  "https://www.youtube.com/@CHANNEL/videos" | \
  jq '{title, id, url, duration, view_count}'
```

**Option C: `--dump-single-json` (single JSON array)**

```bash
# Single JSON object with all entries in an array
yt-dlp --flat-playlist -I :10 --dump-single-json \
  "https://www.youtube.com/@CHANNEL/videos"
```

This waits for all entries before outputting. Better for small playlists; avoid for large channels.

**Option D: Full metadata per video (slower, more complete)**

```bash
# Without --flat-playlist, each video page is fetched individually
yt-dlp --skip-download -I :5 \
  --print "%(title)s | %(upload_date)s | %(duration_string)s | %(description).100s" \
  "https://www.youtube.com/@CHANNEL/videos"
```

This is significantly slower but returns complete metadata including full description and exact upload dates.

### Print to File

```bash
# Write specific fields to a file
yt-dlp --flat-playlist -I :15 \
  --print-to-file "%(title)s|%(id)s|%(url)s" latest_videos.txt \
  "https://www.youtube.com/@CHANNEL/videos"
```

### Custom JSON Output

```bash
# Print selected fields as JSON objects
yt-dlp --flat-playlist -I :10 \
  -O '%(.{title,id,url,duration,view_count})#j' \
  "https://www.youtube.com/@CHANNEL/videos"
```

| Part | Meaning |
|------|---------|
| `-O` | Alias for `--print` |
| `%(.{...})#j` | Output template: select named fields as JSON |

### Speed Optimization

```
                    ┌─────────────────┐
                    │  --flat-playlist │ ← Fast: metadata from playlist page
                    │  + --lazy-playlist│   only. Some fields may be NA.
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  No --flat-     │ ← Slow: fetches each video's page
                    │  playlist       │   individually. Complete metadata.
                    └─────────────────┘
```

For channel monitoring (checking for new videos), `--flat-playlist` is the right choice. You only need full extraction for videos you actually want to process.

---

## 4. yt-dlp: Channel RSS Feed Alternatives

YouTube still provides RSS feeds, but discovering the URL requires the channel ID.

### Constructing RSS URLs

```
Channel RSS:  https://www.youtube.com/feeds/videos.xml?channel_id=CHANNEL_ID
Playlist RSS: https://www.youtube.com/feeds/videos.xml?playlist_id=PLAYLIST_ID
```

### Getting Channel ID with yt-dlp

```bash
# Extract channel_id from any channel URL
yt-dlp --playlist-items 0 \
  -O "playlist:https://www.youtube.com/feeds/videos.xml?channel_id=%(channel_id)s" \
  "https://www.youtube.com/@CHANNEL_HANDLE"
```

| Part | Meaning |
|------|---------|
| `--playlist-items 0` | Extract only playlist-level metadata (no videos) |
| `-O "playlist:..."` | Print format string, scoped to playlist metadata |

### RSS vs yt-dlp for Monitoring

| Approach | Pros | Cons |
|----------|------|------|
| YouTube RSS | Lightweight, no auth needed, standard format | Only latest ~15 videos, limited metadata |
| yt-dlp `--flat-playlist` | More metadata, configurable count, JSON output | Heavier, may trigger rate limits, needs JS runtime |
| `avtdl` (wrapper tool) | Purpose-built for monitoring, filtering, notifications | Additional dependency |

**Recommendation:** Use RSS for lightweight "new video?" polling. Use yt-dlp for richer metadata extraction when a new video is detected.

---

## 5. yt-dlp: Cookie-Based Authentication

### Authentication Methods (Current Status)

| Method | Status | Notes |
|--------|--------|-------|
| `--cookies FILE` | Working | Netscape-format cookie file |
| `--cookies-from-browser BROWSER` | Partially working | Browser must be closed; Chrome encryption issues |
| `--username oauth2` | Deprecated | YouTube killed OAuth2 support |
| `--username/--password` | Not supported | YouTube does not support password login |

### Using `--cookies`

```bash
# Use a Netscape-format cookies.txt file
yt-dlp --cookies ~/cookies.txt "VIDEO_URL"
```

**How to get cookies.txt:**
1. Use Firefox (recommended -- Chrome encrypts cookies making extraction harder)
2. Install "Get cookies.txt LOCALLY" extension (avoid extensions that phone home)
3. Navigate to youtube.com while logged in
4. Export cookies to a `.txt` file
5. Use the file with `--cookies`

### Using `--cookies-from-browser`

```bash
# Extract cookies directly from browser (browser must be fully closed)
yt-dlp --cookies-from-browser firefox "VIDEO_URL"

# Supported browsers: firefox, chrome, chromium, edge, safari, opera, brave, vivaldi
# Safari on iOS also supported (as of 2025.11.12)
```

| Part | Meaning |
|------|---------|
| `--cookies-from-browser firefox` | Read cookies from Firefox's SQLite database |

**Known issues:**
- Chrome/Chromium browsers lock their cookie database while running. You must fully quit the browser (including background processes).
- Chrome encrypts cookies with DPAPI + AES-256-GCM on Windows (since mid-2024), making external extraction unreliable.
- Firefox is the most reliable source for cookie extraction.
- Cookies expire. For automated/server use, you need to periodically re-export.

### When Are Cookies Needed?

- Age-restricted videos
- Members-only content
- When YouTube shows "Sign in to confirm you're not a bot" (common on datacenter IPs)
- Subscription feeds

For public video metadata extraction and thumbnails, cookies are generally **not required**.

---

## 6. youtube-transcript-api: Current State

### Version History

| Version | Date | Key Changes |
|---------|------|-------------|
| **v1.2.4** | 2026-01-29 | Latest stable (bug fixes) |
| v1.2.0 | 2025-07-21 | **BREAKING:** Removed deprecated `get_transcript`, `get_transcripts`, `list_transcripts` |
| v1.1.0 | 2025-06-11 | Switched to innertube API. Added `PoTokenRequired` exception. **Broke cookie auth** (temporarily disabled). |
| **v1.0.0** | 2025-03-11 | **BREAKING:** New instance-based API. Deprecated static methods. |
| 0.6.3 | Pre-2025 | Last version with old static API |

### The v1.0.0 Breaking API Change

The API moved from static class methods to instance-based methods:

```python
# ========== OLD API (removed in v1.2.0) ==========
from youtube_transcript_api import YouTubeTranscriptApi

# Static methods -- these no longer exist
transcript = YouTubeTranscriptApi.get_transcript("VIDEO_ID")
transcripts = YouTubeTranscriptApi.get_transcripts(["id1", "id2"])
transcript_list = YouTubeTranscriptApi.list_transcripts("VIDEO_ID")


# ========== NEW API (v1.0.0+) ==========
from youtube_transcript_api import YouTubeTranscriptApi

# Instance-based -- shares HTTP session across calls
ytt_api = YouTubeTranscriptApi()
transcript = ytt_api.fetch("VIDEO_ID")          # Returns FetchedTranscript object
transcript_list = ytt_api.list("VIDEO_ID")       # Returns TranscriptList

# Convert to the old list-of-dicts format
raw_data = transcript.to_raw_data()
# [{'text': 'hello', 'start': 0.0, 'duration': 1.5}, ...]
```

**Key benefits of the new API:**
- Shared HTTP session = fewer redundant requests, shared cookies
- `FetchedTranscript` object includes metadata (video_id, language, language_code, is_generated)
- Batch processing is more efficient with a single instance

### Batch Transcript Fetching

There is no built-in batch method in the new API. The old `get_transcripts` was removed because it offered no real advantage. Use a loop or concurrent processing:

```python
from youtube_transcript_api import YouTubeTranscriptApi
from concurrent.futures import ThreadPoolExecutor
import time

ytt_api = YouTubeTranscriptApi()

def fetch_one(video_id):
    """Fetch transcript with rate-limit delay."""
    time.sleep(0.5)  # Avoid throttling
    try:
        return video_id, ytt_api.fetch(video_id)
    except Exception as e:
        return video_id, e

video_ids = ["id1", "id2", "id3"]

# Concurrent fetching (respect rate limits)
with ThreadPoolExecutor(max_workers=3) as executor:
    results = dict(executor.map(lambda vid: fetch_one(vid), video_ids))
```

### Language Selection

```python
ytt_api = YouTubeTranscriptApi()

# Fetch with language preference (fallback chain)
transcript = ytt_api.fetch("VIDEO_ID", languages=['de', 'en'])

# List all available transcripts
transcript_list = ytt_api.list("VIDEO_ID")
for t in transcript_list:
    print(f"{t.language} ({t.language_code}) - Generated: {t.is_generated}")

# Translate a transcript
transcript_list = ytt_api.list("VIDEO_ID")
transcript = transcript_list.find_transcript(['en'])
translated = transcript.translate('fr').fetch()
```

### Formatting Options

```python
from youtube_transcript_api.formatters import (
    TextFormatter,
    SRTFormatter,
    WebVTTFormatter,
    JSONFormatter,
)

ytt_api = YouTubeTranscriptApi()
transcript = ytt_api.fetch("VIDEO_ID")

# Plain text (no timestamps)
text = TextFormatter().format_transcript(transcript)

# SRT subtitle format
srt = SRTFormatter().format_transcript(transcript)

# WebVTT subtitle format
vtt = WebVTTFormatter().format_transcript(transcript)

# JSON format
json_output = JSONFormatter().format_transcript(transcript)
```

### Preserve Formatting

```python
# Keep HTML formatting elements like <i>italics</i>
transcript = ytt_api.fetch("VIDEO_ID", preserve_formatting=True)
```

### Known Issues & Limitations

1. **No cookie authentication (since v1.1.0):** The switch to innertube API broke cookie-based auth. This means members-only or restricted transcripts may not be accessible.
2. **No API key required:** Works by hitting YouTube's internal endpoints directly.
3. **Rate limiting:** YouTube will throttle aggressive usage. Add 0.5-1s delays between requests.
4. **`PoTokenRequired` exception (v1.1.0+):** Raised when YouTube requires a PO token for timedtext URLs. This is a server-side restriction and cannot be worked around by the library.
5. **`TranscriptsDisabled`:** Raised when a video has captions disabled entirely.
6. **`NoTranscriptFound`:** Raised when the requested language is not available.
7. **Auto-generated vs manual:** ~85% of YouTube videos have auto-generated captions. The library handles both.

### CLI Usage

```bash
# Fetch transcript from command line
youtube_transcript_api VIDEO_ID

# With language preference
youtube_transcript_api VIDEO_ID --languages de en

# Exclude auto-generated
youtube_transcript_api VIDEO_ID --exclude-generated

# Multiple videos
youtube_transcript_api VIDEO_ID_1 VIDEO_ID_2 VIDEO_ID_3
```

---

## 7. Architecture for Channel Monitoring Pipeline

Based on this research, here is the recommended approach:

```
┌──────────────────────────────────────────────────────────┐
│                    Channel Monitor                        │
│                                                          │
│  1. RSS Poll (lightweight)                               │
│     youtube.com/feeds/videos.xml?channel_id=XXX          │
│     ├── Check every 15-30 min                            │
│     └── Compare against known video IDs                  │
│                                                          │
│  2. On New Video Detected                                │
│     ├── yt-dlp --skip-download --dump-json VIDEO_URL     │
│     │   → title, description, upload_date, duration      │
│     │                                                    │
│     ├── yt-dlp --skip-download --write-thumbnail         │
│     │   --convert-thumbnails jpg -o "path/%(id)s.%(ext)s"│
│     │   → thumbnail.jpg                                  │
│     │                                                    │
│     └── youtube-transcript-api                            │
│         ytt_api.fetch(video_id)                          │
│         → full transcript text                           │
│                                                          │
│  3. Process & Store                                      │
│     └── Feed into content pipeline                       │
└──────────────────────────────────────────────────────────┘
```

### Quick Reference Commands

```bash
# Install everything
pip install yt-dlp youtube-transcript-api
brew install deno  # Required for yt-dlp YouTube support

# Get latest 10 videos as JSON
yt-dlp --flat-playlist --lazy-playlist -I :10 --dump-json \
  "https://www.youtube.com/@CHANNEL/videos"

# Download thumbnail only
yt-dlp --skip-download --write-thumbnail --convert-thumbnails jpg \
  -o "thumbnails/%(id)s.%(ext)s" "VIDEO_URL"

# Get video metadata without downloading
yt-dlp --skip-download --dump-json "VIDEO_URL" | \
  jq '{title, upload_date, duration_string, description, thumbnail}'

# Get transcript
python -c "
from youtube_transcript_api import YouTubeTranscriptApi
api = YouTubeTranscriptApi()
t = api.fetch('VIDEO_ID')
print(t.to_raw_data())
"

# Get channel RSS feed URL
yt-dlp --playlist-items 0 \
  -O "playlist:https://www.youtube.com/feeds/videos.xml?channel_id=%(channel_id)s" \
  "https://www.youtube.com/@CHANNEL"
```

---

## 8. Dependency Summary

| Package | Version | Python | Extras Required |
|---------|---------|--------|-----------------|
| yt-dlp | 2026.03.03 | >= 3.10 | Deno or Node.js (for YouTube), ffmpeg (for thumbnail conversion) |
| youtube-transcript-api | 1.2.4 | >= 3.8, < 3.15 | None |

### Version Pinning Recommendation

```
# requirements.txt
yt-dlp>=2026.03.03
youtube-transcript-api>=1.2.0,<2.0.0
```

Pin `youtube-transcript-api` at `>=1.2.0` to ensure you are on the new instance-based API with deprecated methods removed (cleaner, no ambiguity).
