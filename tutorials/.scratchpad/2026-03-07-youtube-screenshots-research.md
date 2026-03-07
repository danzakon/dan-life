# YouTube Screenshot / Thumbnail Extraction — Research Notes

**Date:** 2026-03-07
**Goal:** Understand all practical approaches to extracting screenshots and thumbnails from YouTube videos programmatically, for CLI automation workflows.

---

## 1. YouTube Thumbnail URLs (No API Required)

YouTube auto-generates thumbnails at predictable URLs. Given a video ID (e.g., `dQw4w9WgXcQ`), thumbnails are available at:

```
https://img.youtube.com/vi/{VIDEO_ID}/{FILENAME}
```

### Available Sizes

| Filename             | Resolution   | Notes                                          |
|----------------------|-------------|------------------------------------------------|
| `maxresdefault.jpg`  | 1280x720    | Highest quality. Only exists for HD+ uploads.  |
| `sddefault.jpg`      | 640x480     | Standard definition.                           |
| `hqdefault.jpg`      | 480x360     | High quality. Always available.                |
| `mqdefault.jpg`      | 320x180     | Medium quality. 16:9 aspect, no letterboxing.  |
| `default.jpg`        | 120x90      | Small thumbnail.                               |
| `0.jpg`              | 480x360     | Full-size frame (same as hqdefault usually).   |
| `1.jpg`              | 120x90      | Auto-generated frame 1 (early in video).       |
| `2.jpg`              | 120x90      | Auto-generated frame 2 (mid video).            |
| `3.jpg`              | 120x90      | Auto-generated frame 3 (late in video).        |

### Alternative Domain

The same images are also available via:
```
https://i.ytimg.com/vi/{VIDEO_ID}/{FILENAME}
```

### Key Gotchas

- **`maxresdefault.jpg` is NOT guaranteed.** It only exists for videos uploaded in 720p or higher. Older or low-res videos will 404. Always fall back to `hqdefault.jpg`.
- **`mqdefault.jpg` is the only one with clean 16:9 aspect ratio** (no black letterboxing bars). Good for consistent UI layouts.
- **These are video thumbnails, not arbitrary timestamps.** You get the creator's custom thumbnail (or YouTube's auto-picked frames), not a frame at a specific time.
- **WebP variants** also exist at the same paths with `.webp` extension on some CDN endpoints.

### Quick CLI Download

```bash
# Download the highest-res thumbnail for a video
VIDEO_ID="dQw4w9WgXcQ"
curl -o thumbnail.jpg "https://img.youtube.com/vi/${VIDEO_ID}/maxresdefault.jpg"

# With fallback if maxres doesn't exist (404)
curl -f -o thumbnail.jpg "https://img.youtube.com/vi/${VIDEO_ID}/maxresdefault.jpg" \
  || curl -o thumbnail.jpg "https://img.youtube.com/vi/${VIDEO_ID}/hqdefault.jpg"
```

| Part   | Meaning                                            |
|--------|----------------------------------------------------|
| `curl` | Command-line HTTP client                           |
| `-f`   | Fail silently on HTTP errors (enables `||` fallback) |
| `-o`   | Write output to file instead of stdout             |

---

## 2. yt-dlp Thumbnail Extraction

yt-dlp has built-in thumbnail handling. This is the most reliable approach for getting the video's official thumbnail.

### Download Thumbnail Only (Skip Video)

```bash
yt-dlp --write-thumbnail --skip-download -o "%(title)s.%(ext)s" "URL"
```

| Flag                | Purpose                                         |
|---------------------|--------------------------------------------------|
| `--write-thumbnail` | Save the thumbnail image to disk                |
| `--skip-download`   | Don't download the actual video                 |
| `-o "%(title)s..."`| Output filename template                         |

The thumbnail is saved as `.webp` by default (YouTube's native format).

### Convert Thumbnail to JPG/PNG

```bash
yt-dlp --write-thumbnail --skip-download \
  --convert-thumbnails jpg \
  -o "%(id)s.%(ext)s" "URL"
```

| Flag                       | Purpose                                    |
|----------------------------|--------------------------------------------|
| `--convert-thumbnails jpg` | Convert thumbnail to JPG (also supports png) |

### List All Available Thumbnails

```bash
yt-dlp --list-thumbnails "URL"
```

This shows all thumbnail IDs, resolutions, and URLs. YouTube videos often have 40+ thumbnail variants at different crops and resolutions.

### Write All Thumbnails

```bash
yt-dlp --write-all-thumbnails --skip-download -o "%(id)s.%(ext)s" "URL"
```

### Embed Thumbnail in Downloaded Video

```bash
yt-dlp --embed-thumbnail "URL"
```

### Python API Usage

```python
import yt_dlp

# Note: Python API uses underscores, not hyphens
opts = {
    'writethumbnail': True,     # not 'write-thumbnail'
    'skip_download': True,      # not 'skip-download'
    'outtmpl': '%(id)s.%(ext)s',
}

with yt_dlp.YoutubeDL(opts) as ydl:
    ydl.download(['https://www.youtube.com/watch?v=VIDEO_ID'])
```

### Limitation

Like the URL approach, yt-dlp only gives you the video's **thumbnail** (the image the creator set or YouTube auto-generated). It does NOT extract frames at arbitrary timestamps.

---

## 3. ffmpeg Frame Extraction

ffmpeg is the standard tool for extracting frames at specific timestamps. This is the answer to "get a screenshot at timestamp X."

### Extract One Frame at a Specific Timestamp

```bash
ffmpeg -ss 01:23:45 -i input.mp4 -frames:v 1 -q:v 2 output.jpg
```

| Flag           | Purpose                                                  |
|----------------|----------------------------------------------------------|
| `-ss 01:23:45` | Seek to this timestamp (HH:MM:SS or seconds)             |
| `-i input.mp4` | Input file                                               |
| `-frames:v 1`  | Extract exactly one video frame                          |
| `-q:v 2`       | JPEG quality (1-31 scale, lower = better, 2-5 is good)  |

### Important: `-ss` Placement Matters

```bash
# FAST: -ss before -i (input seeking, seeks to nearest keyframe)
ffmpeg -ss 01:23:45 -i input.mp4 -frames:v 1 -q:v 2 output.jpg

# PRECISE but SLOW: -ss after -i (output seeking, decodes from start)
ffmpeg -i input.mp4 -ss 01:23:45 -frames:v 1 -q:v 2 output.jpg
```

For screenshots, input seeking (before `-i`) is almost always good enough and dramatically faster.

### Output as PNG (Lossless)

```bash
ffmpeg -ss 00:05:30 -i input.mp4 -frames:v 1 output.png
```

No quality flag needed for PNG since it's lossless.

### Extract by Frame Number

```bash
ffmpeg -i input.mp4 -vf "select=eq(n\,34)" -frames:v 1 out.png
```

| Flag                          | Purpose                                   |
|-------------------------------|-------------------------------------------|
| `-vf "select=eq(n\,34)"`     | Select frame number 34 (0-indexed)        |
| Note: slow for late frames    | Must decode all frames up to that point   |

### Extract Multiple Frames (One Per N Seconds)

```bash
# One frame every 60 seconds
ffmpeg -i input.mp4 -vf fps=1/60 frame_%04d.jpg

# One frame every 5 seconds
ffmpeg -i input.mp4 -vf fps=1/5 frame_%04d.jpg
```

---

## 4. The Killer Combo: yt-dlp + ffmpeg (No Full Download)

This is the most powerful approach. Use yt-dlp to get the direct stream URL, then feed it to ffmpeg. **No full video download required.**

### One-liner: Screenshot at Timestamp from YouTube URL

```bash
ffmpeg -ss 00:08:14 \
  -i "$(yt-dlp -f 'bv*[height<=1080]' --get-url 'YOUTUBE_URL')" \
  -frames:v 1 -q:v 2 screenshot.jpg
```

#### How This Works

```
                                    ┌──────────────┐
                                    │   YouTube    │
                                    │   Server     │
                                    └──────┬───────┘
                                           │
                    ┌──────────────────────┐│ Direct stream URL
                    │  yt-dlp --get-url    │◀─────────────
                    │  (resolves URL only, │
                    │   no download)       │
                    └──────────┬───────────┘
                               │ URL string
                    ┌──────────▼───────────┐
                    │  ffmpeg -ss -i URL   │
                    │  (HTTP range seek,   │
                    │   downloads ~1 frame)│
                    └──────────┬───────────┘
                               │
                    ┌──────────▼───────────┐
                    │  screenshot.jpg      │
                    └──────────────────────┘
```

#### Breaking Down the yt-dlp Part

```bash
yt-dlp -f 'bv*[height<=1080]' --get-url 'YOUTUBE_URL'
```

| Flag                        | Purpose                                         |
|-----------------------------|-------------------------------------------------|
| `-f 'bv*[height<=1080]'`   | Best video stream, max 1080p                    |
| `--get-url`                 | Print the direct media URL, don't download      |

The `--get-url` flag is the key. It resolves the temporary CDN URL for the video stream without downloading anything.

### Important Caveats

1. **URLs are temporary.** The direct URLs from `--get-url` expire after some hours. Don't cache them.
2. **Video-only streams.** When using format selectors like `bv*`, you get video-only (no audio). That's fine for screenshots.
3. **Quoting.** The URL from yt-dlp is long and contains special characters. Always wrap in quotes.

### Practical Shell Script

```bash
#!/bin/bash
# yt-screenshot.sh — Extract a frame from a YouTube video at a given timestamp
#
# Usage: ./yt-screenshot.sh <youtube_url> <timestamp> [output_file]
# Example: ./yt-screenshot.sh "https://youtu.be/dQw4w9WgXcQ" "00:01:30" frame.jpg

set -euo pipefail

URL="${1:?Usage: yt-screenshot.sh <url> <timestamp> [output]}"
TIMESTAMP="${2:?Provide a timestamp like 00:01:30 or 90 (seconds)}"
OUTPUT="${3:-screenshot.jpg}"

echo "Resolving stream URL..."
STREAM_URL=$(yt-dlp -f 'bv*[height<=1080]' --get-url "$URL")

echo "Extracting frame at ${TIMESTAMP}..."
ffmpeg -ss "$TIMESTAMP" -i "$STREAM_URL" -frames:v 1 -q:v 2 "$OUTPUT" -y 2>/dev/null

echo "Saved: ${OUTPUT}"
```

| Flag in script | Purpose                                               |
|----------------|-------------------------------------------------------|
| `set -euo pipefail` | Exit on errors, undefined vars, pipe failures   |
| `-y`           | Overwrite output without asking                       |
| `2>/dev/null`  | Suppress ffmpeg's verbose stderr output               |

---

## 5. Python Libraries

### Option A: yt-dlp + ffmpeg-python (Recommended)

The most reliable combo for 2025-2026. Both are actively maintained.

```python
import subprocess
import yt_dlp

def youtube_screenshot(url: str, timestamp: str, output: str = "screenshot.jpg"):
    """Extract a single frame from a YouTube video at a given timestamp."""

    # Step 1: Resolve the direct stream URL via yt-dlp
    opts = {
        'format': 'bv*[height<=1080]',
        'quiet': True,
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=False)
        stream_url = info['url']

    # Step 2: Use ffmpeg to extract the frame
    cmd = [
        'ffmpeg',
        '-ss', timestamp,
        '-i', stream_url,
        '-frames:v', '1',
        '-q:v', '2',
        '-y',
        output,
    ]
    subprocess.run(cmd, capture_output=True, check=True)
    return output

# Usage
youtube_screenshot(
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "00:01:30",
    "frame.jpg"
)
```

### Option B: cap_from_youtube + OpenCV

A lightweight library that wraps yt-dlp to create an OpenCV `VideoCapture` from a YouTube URL. Good for computer vision workflows where you need multiple frames.

```bash
pip install cap_from_youtube
```

```python
import cv2
from cap_from_youtube import cap_from_youtube

youtube_url = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
cap = cap_from_youtube(youtube_url, '720p')

# Seek to a specific timestamp (in milliseconds)
timestamp_ms = 90 * 1000  # 1 minute 30 seconds
cap.set(cv2.CAP_PROP_POS_MSEC, timestamp_ms)

ret, frame = cap.read()
if ret:
    cv2.imwrite('screenshot.png', frame)

cap.release()
```

**Status:** Actively maintained (last release 2023, but relies on yt-dlp which is current). Uses yt-dlp under the hood. Works in 2025-2026.

**Trade-off:** Requires downloading/streaming the video data up to the seek point. Less efficient than the yt-dlp `--get-url` + ffmpeg approach for a single screenshot. Better if you need to grab many frames from the same video.

### Option C: vidgear CamGear (For Real-Time / Streaming)

```bash
pip install vidgear[core]
```

```python
from vidgear.gears import CamGear

stream = CamGear(
    source='https://www.youtube.com/watch?v=dQw4w9WgXcQ',
    stream_mode=True,
    logging=True
).start()

frame = stream.read()  # Read frames in a loop
# Process frame with OpenCV...
stream.stop()
```

**Best for:** Real-time streaming / continuous frame extraction. Overkill for a single screenshot.

### Libraries to AVOID (Broken/Unmaintained as of 2025-2026)

| Library     | Status                                                              |
|-------------|---------------------------------------------------------------------|
| `pytube`    | Frequently breaks due to YouTube changes. Maintenance is sporadic. |
| `pafy`      | Depends on `youtube-dl` which is rarely updated. Use yt-dlp instead.|
| `youtube-dl`| Mostly superseded by yt-dlp. Still works but updates are infrequent.|

---

## 6. YouTube Data API v3

The official API provides thumbnail URLs (but not arbitrary frame extraction).

### Endpoint

```
GET https://www.googleapis.com/youtube/v3/videos
  ?part=snippet
  &id={VIDEO_ID}
  &key={API_KEY}
```

### Response (Thumbnail Portion)

```json
{
  "snippet": {
    "thumbnails": {
      "default":  { "url": "...", "width": 120,  "height": 90  },
      "medium":   { "url": "...", "width": 320,  "height": 180 },
      "high":     { "url": "...", "width": 480,  "height": 360 },
      "standard": { "url": "...", "width": 640,  "height": 480 },
      "maxres":   { "url": "...", "width": 1280, "height": 720 }
    }
  }
}
```

### When to Use the API

- You need metadata alongside thumbnails (title, description, duration, etc.)
- You're working with many videos and want batch processing
- You want the thumbnail URL without any scraping / yt-dlp dependency

### When NOT to Use the API

- You need a frame at a **specific timestamp** (API only gives the thumbnail, not arbitrary frames)
- You don't want to deal with API keys and quota limits
- The predictable URL pattern (`img.youtube.com/vi/...`) is sufficient

### Quota Cost

- `videos.list` costs 1 unit per call
- Default daily quota: 10,000 units
- For thumbnails alone, the direct URL approach is free and unlimited

---

## 7. Decision Matrix

```
What do you need?
       │
       ├─── The video's THUMBNAIL (what viewers see before clicking)?
       │         │
       │         ├─── Just the image? ──────────▶ Direct URL pattern
       │         │                                 curl https://img.youtube.com/vi/{ID}/maxresdefault.jpg
       │         │
       │         ├─── Image + metadata? ────────▶ YouTube Data API v3
       │         │
       │         └─── Downloaded to disk? ──────▶ yt-dlp --write-thumbnail --skip-download
       │
       └─── A FRAME at a specific TIMESTAMP?
                 │
                 ├─── Single frame, CLI? ───────▶ yt-dlp --get-url + ffmpeg  (RECOMMENDED)
                 │
                 ├─── Single frame, Python? ────▶ yt-dlp Python API + subprocess ffmpeg
                 │
                 ├─── Many frames, same video? ─▶ cap_from_youtube + OpenCV
                 │
                 └─── Real-time streaming? ─────▶ vidgear CamGear
```

---

## 8. Recommended CLI Workflow

For the use case "given a YouTube URL and a timestamp, save a screenshot as PNG/JPG locally," here is the simplest, most reliable approach:

### Prerequisites

```bash
# Install yt-dlp (keep updated — YouTube changes frequently)
pip install -U yt-dlp

# Install ffmpeg (if not already present)
brew install ffmpeg     # macOS
# apt install ffmpeg    # Ubuntu/Debian
```

### The Command

```bash
ffmpeg -ss "1:23:45" \
  -i "$(yt-dlp -f 'bv*[height<=1080]' --get-url 'https://www.youtube.com/watch?v=VIDEO_ID')" \
  -frames:v 1 -q:v 2 screenshot.jpg
```

### Why This Is the Best Approach

| Factor        | Rating | Notes                                                  |
|---------------|--------|--------------------------------------------------------|
| Reliability   | High   | yt-dlp is actively maintained, handles YouTube changes |
| Speed         | Fast   | No full video download; HTTP range seeking             |
| Quality       | High   | Direct stream access, configurable resolution          |
| Dependencies  | Minimal| Just yt-dlp + ffmpeg (both widely available)           |
| Scriptability | Great  | One-liner, easy to wrap in shell/Python scripts        |

### Edge Cases

- **Age-restricted videos:** May need `--cookies-from-browser firefox` flag on yt-dlp
- **Private/unlisted videos:** Need authentication via cookies
- **Livestreams:** Use `--live-from-start` with yt-dlp, then ffmpeg on the downloaded segment
- **Very long videos:** Input seeking (`-ss` before `-i`) is critical for performance

---

## 9. Quick Reference Card

```
┌─────────────────────────────────────────────────────────────────────┐
│                    YouTube Screenshot Cheat Sheet                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  THUMBNAIL (the video's preview image):                             │
│    curl "https://img.youtube.com/vi/{ID}/maxresdefault.jpg"         │
│                                                                     │
│  THUMBNAIL via yt-dlp:                                              │
│    yt-dlp --write-thumbnail --skip-download --convert-thumbnails    │
│           jpg -o "%(id)s.%(ext)s" "URL"                             │
│                                                                     │
│  FRAME AT TIMESTAMP (the main use case):                            │
│    ffmpeg -ss HH:MM:SS \                                            │
│      -i "$(yt-dlp -f 'bv*[height<=1080]' --get-url 'URL')" \       │
│      -frames:v 1 -q:v 2 output.jpg                                 │
│                                                                     │
│  MULTIPLE FRAMES (every N seconds from local file):                 │
│    ffmpeg -i input.mp4 -vf fps=1/60 frame_%04d.jpg                 │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```
