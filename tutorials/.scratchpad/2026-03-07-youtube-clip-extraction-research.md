# YouTube Clip Extraction Research

Extracting video segments from YouTube programmatically for social media upload.

**Use case:** Given a YouTube URL and a time range (e.g., 1:43:00 to 1:45:00), extract that segment as a video file ready for upload to X/Twitter, LinkedIn, etc.

---

## Table of Contents

1. [Approach Comparison](#approach-comparison)
2. [yt-dlp `--download-sections`](#1-yt-dlp---download-sections)
3. [yt-dlp + ffmpeg Stream URL Approach](#2-yt-dlp--ffmpeg-stream-url-approach)
4. [Keyframe vs Exact Cuts](#3-keyframe-vs-exact-cuts)
5. [YouTube Native Clip Features](#4-youtube-native-clip-features)
6. [Social Media Format Requirements](#5-social-media-format-requirements)
7. [Audio/Video Sync Issues](#6-audiovideo-sync-issues)
8. [Subtitle/Caption Overlay](#7-subtitlecaption-overlay)
9. [End-to-End Workflow](#8-end-to-end-workflow)
10. [Shell Script](#9-shell-script)

---

## Approach Comparison

| Approach | Downloads Full Video? | Exact Cuts? | Speed | Complexity |
|---|---|---|---|---|
| `--download-sections` (default) | No | Nearest keyframe | Fast | Low |
| `--download-sections` + `--force-keyframes-at-cuts` | No | Exact | Slow (re-encodes) | Low |
| `--get-url` + ffmpeg | No | Configurable | Medium | Medium |
| Download full + ffmpeg trim | Yes | Configurable | Slowest | Medium |

**Recommendation:** Use `--download-sections` with `--force-keyframes-at-cuts` for clips destined for social media. The re-encoding overhead is acceptable for 1-3 minute clips, and you get frame-accurate cuts without downloading the full video.

---

## 1. yt-dlp `--download-sections`

The dedicated feature for downloading segments. Available since yt-dlp version 2022.06.22.1.

### Basic Syntax

```bash
yt-dlp --download-sections "*START-END" URL
```

The `*` prefix is required. It tells yt-dlp this is a time range (not a chapter name).

### Time Format Options

```bash
# Timestamp format (HH:MM:SS or H:MM:SS)
yt-dlp --download-sections "*1:43:00-1:45:00" URL

# Seconds format
yt-dlp --download-sections "*6180-6300" URL

# Use "inf" for "end of video"
yt-dlp --download-sections "*1:43:00-inf" URL
```

### With Format Selection

```bash
# MP4 output, best quality up to 1080p
yt-dlp --download-sections "*1:43:00-1:45:00" \
  -f "bestvideo[ext=mp4][height<=1080]+bestaudio[ext=m4a]/best[ext=mp4]" \
  --merge-output-format mp4 \
  URL
```

### With Exact Cuts (Force Keyframes)

```bash
yt-dlp --download-sections "*1:43:00-1:45:00" \
  --force-keyframes-at-cuts \
  -f "bestvideo[ext=mp4][height<=1080]+bestaudio[ext=m4a]/best[ext=mp4]" \
  --merge-output-format mp4 \
  -o "%(title)s_clip.%(ext)s" \
  URL
```

### Output Template Variables for Sections

```bash
# Include section start/end in filename
-o "%(title)s-%(section_start)s-%(section_end)s.%(ext)s"
```

### Multiple Sections

```bash
yt-dlp --download-sections "*1:00-2:00" \
       --download-sections "*5:00-6:00" \
       URL
```

### Key Behaviors

- **Does NOT download the full video.** Only fetches the bytes needed for the segment.
- **Requires ffmpeg** for merging separate video/audio streams and for keyframe cutting.
- **Default behavior:** Cuts at the nearest keyframe (looking backward). This means the clip may start a few seconds early.
- **With `--force-keyframes-at-cuts`:** Re-encodes to cut at the exact timestamp. Slower but frame-accurate.
- **Format selection works normally** with `--download-sections`. Use `-f` to pick codecs/resolution.
- **Protocol tip:** Add `-S proto:https` if you experience connection issues with HLS streams.

### Known Issues

- Audio-only downloads with `--download-sections` may have inaccurate start times without `--force-keyframes-at-cuts`.
- Some very specific timeframes on certain videos can produce corrupt 258-byte files (rare, related to HLS playlist edge cases).
- Connection resets during audio download have been reported on YouTube (issue #12540, March 2025).

---

## 2. yt-dlp + ffmpeg Stream URL Approach

An alternative approach: get the direct stream URLs from yt-dlp and feed them to ffmpeg for precise control.

### Step 1: Get Stream URLs

```bash
# Get video and audio URLs (separate DASH streams)
yt-dlp --youtube-skip-dash-manifest -g URL
```

This outputs two URLs: first is video, second is audio.

### Step 2: Extract Segment with ffmpeg

```bash
# Capture URLs into variables
readarray -t urls <<< "$(yt-dlp --youtube-skip-dash-manifest -g URL)"

# Extract segment
ffmpeg -ss 1:43:00 -i "${urls[0]}" \
       -ss 1:43:00 -i "${urls[1]}" \
       -t 120 \
       -map 0:v -map 1:a \
       -c:v libx264 -c:a aac \
       output.mp4
```

### ffmpeg Flag Breakdown

| Flag | Meaning |
|---|---|
| `-ss 1:43:00` | Seek to this timestamp (before `-i` = input seeking, fast) |
| `-i "${urls[0]}"` | Input: video stream URL |
| `-i "${urls[1]}"` | Input: audio stream URL |
| `-t 120` | Duration of output (120 seconds = 2 minutes) |
| `-map 0:v` | Take video from first input |
| `-map 1:a` | Take audio from second input |
| `-c:v libx264` | Re-encode video with H.264 |
| `-c:a aac` | Re-encode audio with AAC |

### Important: `-ss` Placement Matters

```
ffmpeg -ss BEFORE -i input ...   # Input seeking: fast, seeks to nearest keyframe
ffmpeg -i input -ss AFTER ...    # Output seeking: slow but frame-accurate (decodes from start)
```

**For stream URLs, always use input seeking** (`-ss` before `-i`). Output seeking would try to download from the beginning.

### The "Double -ss" Trick for Precision

```bash
# Seek to 5 seconds before desired start, then trim precisely
ffmpeg -ss 1:42:55 -i "${urls[0]}" \
       -ss 1:42:55 -i "${urls[1]}" \
       -ss 5 \               # Skip first 5 seconds (now at exact start)
       -t 120 \
       -map 0:v -map 1:a \
       -c:v libx264 -c:a aac \
       output.mp4
```

The third `-ss 5` is an output seek that trims the extra 5 seconds of buffer, giving you a precise cut point even when the initial input seek landed on a keyframe slightly before your target.

### Pros/Cons vs `--download-sections`

| | `--download-sections` | Stream URL + ffmpeg |
|---|---|---|
| Simplicity | Single command | Multi-step |
| Control | Limited to yt-dlp flags | Full ffmpeg control |
| Subtitle integration | Separate step | Can do in one pass |
| Audio sync | Handled by yt-dlp | Must handle manually |
| Speed | Fast (no re-encode default) | Depends on encode settings |

---

## 3. Keyframe vs Exact Cuts

### What Are Keyframes?

Video is compressed in groups of frames (GOP). A keyframe (I-frame) is a complete picture; frames between keyframes only store differences. You can only cleanly cut at a keyframe without re-encoding.

```
Keyframe Spacing (typical YouTube):
├── I ── P ── P ── P ── P ── I ── P ── P ── P ── P ── I ──
    0s   0.5  1.0  1.5  2.0  2.5  3.0  3.5  4.0  4.5  5.0

Requested cut at 1.2s lands at keyframe 0s (2+ seconds early)
```

YouTube videos typically have keyframes every 2-5 seconds. This means a keyframe-only cut could start up to 5 seconds before your requested timestamp.

### When to Use Each

| Scenario | Approach | Why |
|---|---|---|
| Quick preview/draft | Default (no `--force-keyframes-at-cuts`) | Speed; a few seconds off is fine |
| Final social media upload | `--force-keyframes-at-cuts` | Frame-accurate; re-encode is fine since we're making a short clip |
| Audio extraction only | Default is usually fine | Audio keyframes are much closer together |

### Performance Impact

For a 2-minute clip from a 1080p video:
- **Without `--force-keyframes-at-cuts`:** ~5-10 seconds
- **With `--force-keyframes-at-cuts`:** ~30-60 seconds (must re-encode the boundary frames)

The re-encode only applies to the cut points, not the entire clip, so it scales with the number of cuts rather than clip duration.

---

## 4. YouTube Native Clip Features

### YouTube Clips (In-App Feature)

YouTube has a "Clip" feature that lets users create 5-60 second clips from videos:
- Available only for videos longer than 8 minutes
- Creates a shareable YouTube URL, NOT a downloadable file
- The clip lives on YouTube as a link back to the original video
- Max 60 seconds

### YouTube Data API

The YouTube Data API v3 does NOT have endpoints for:
- Creating clips programmatically
- Downloading video segments
- Accessing clip creation functionality

The API supports `list`, `insert` (upload), `update`, `delete`, `rate`, and `reportAbuse` for videos. No clip extraction.

### YouTube.js (Unofficial)

The `youtube.js` library (youtubei.js) has a `ClipCreation` class that interacts with YouTube's internal API, but:
- It creates YouTube-hosted clips (links), not downloadable files
- It mimics the browser UI interaction
- Fragile; depends on YouTube's internal API staying stable
- Not a path to getting a video file

### Timestamped Share Links

```
https://youtu.be/VIDEO_ID?t=6180   # Starts playback at 1:43:00
```

These are just playback hints. They don't enable downloading or server-side clipping.

**Bottom line:** There is no official YouTube API for extracting video file segments. yt-dlp is the way.

---

## 5. Social Media Format Requirements

### X/Twitter (2026)

| Spec | Requirement |
|---|---|
| Format | MP4 or MOV |
| Video codec | H.264 (Main or High profile) |
| Audio codec | AAC (Low Complexity) |
| Max file size | 512 MB (free), 2 GB (Premium), 16 GB (Premium Plus) |
| Max duration | 2 min 20 sec (free), up to 4 hours (Premium Plus on web/iOS) |
| Resolution | Up to 1920x1200 (landscape), 1200x1900 (vertical) |
| Recommended | 1280x720 (16:9 landscape) or 720x1280 (9:16 vertical) |
| Frame rate | Up to 60 fps (30 fps recommended) |
| Bit rate | Up to 25 Mbps |
| Aspect ratios | 1:2.39 to 2.39:1 |

### LinkedIn (2026)

| Spec | Requirement |
|---|---|
| Format | MP4 (recommended), MOV, AVI, MKV, WebM also supported |
| Video codec | H.264 (best compatibility) |
| Max file size | 5 GB |
| Max duration | 3 sec to 10 min (native), up to 30 min (ads) |
| Best resolution | 1920x1080 (16:9), 1080x1080 (1:1), 1080x1350 (4:5) |
| Optimal length | 30 sec to 3 min for thought leadership |
| Aspect ratios | 16:9, 1:1, 4:5, 9:16 |

### Universal Safe Settings for Both Platforms

```bash
# ffmpeg encoding flags for maximum compatibility
-c:v libx264 -profile:v high -level 4.0 \
-pix_fmt yuv420p \
-c:a aac -b:a 128k \
-movflags +faststart \
-r 30
```

| Flag | Purpose |
|---|---|
| `-c:v libx264` | H.264 video codec (universal support) |
| `-profile:v high` | H.264 High profile (good quality/compression) |
| `-level 4.0` | Compatibility level for 1080p/30fps |
| `-pix_fmt yuv420p` | Pixel format required by most players |
| `-c:a aac -b:a 128k` | AAC audio at 128kbps |
| `-movflags +faststart` | Moves metadata to file start for faster streaming/upload |
| `-r 30` | 30 fps output |

### Resolution Strategy

For clips that will go to both X and LinkedIn:
- **Landscape (16:9):** 1920x1080 or 1280x720
- **Square (1:1):** 1080x1080
- **Vertical (9:16):** 1080x1920

1280x720 is the sweet spot: good quality, small file size, works everywhere.

---

## 6. Audio/Video Sync Issues

### When Does Sync Drift Happen?

1. **Separate stream download:** YouTube serves video and audio as separate DASH streams. When downloading them separately (especially with the `--get-url` + ffmpeg approach), they can have slightly different start times.

2. **HLS streams:** When yt-dlp uses HLS protocol, segment boundaries may not align perfectly between audio and video.

3. **Keyframe cutting without re-encode:** Cutting at a keyframe for video but at an exact timestamp for audio creates a mismatch.

### Mitigations

```bash
# Option 1: Let yt-dlp handle it (recommended)
yt-dlp --download-sections "*1:43:00-1:45:00" \
  --force-keyframes-at-cuts \
  -f "bestvideo[ext=mp4]+bestaudio[ext=m4a]" \
  --merge-output-format mp4 \
  URL
# yt-dlp handles sync internally when merging

# Option 2: Force HTTPS protocol to avoid HLS issues
yt-dlp --download-sections "*1:43:00-1:45:00" \
  -S proto:https \
  URL

# Option 3: For stream URL approach, re-encode both streams
ffmpeg -ss 1:43:00 -i "$video_url" \
       -ss 1:43:00 -i "$audio_url" \
       -t 120 \
       -map 0:v -map 1:a \
       -c:v libx264 -c:a aac \
       -async 1 \
       output.mp4
```

| ffmpeg sync flag | Purpose |
|---|---|
| `-async 1` | Stretches/squeezes audio to match video timestamps |
| `-af aresample=async=1` | Resamples audio to match timing |

### Best Practice

Let yt-dlp handle the merge when possible. The `--download-sections` approach with `--force-keyframes-at-cuts` produces properly synced output because yt-dlp invokes ffmpeg internally with the correct parameters.

---

## 7. Subtitle/Caption Overlay

### Step 1: Download Subtitles

```bash
# Download auto-generated subtitles (most YouTube videos have these)
yt-dlp --write-auto-sub --sub-lang en --sub-format srt \
  --convert-subs srt --skip-download \
  -o "%(id)s" \
  URL
# Produces: VIDEO_ID.en.srt

# Download manual/uploaded subtitles (if available)
yt-dlp --write-sub --sub-lang en --sub-format srt \
  --convert-subs srt --skip-download \
  URL

# List available subtitle tracks
yt-dlp --list-subs URL

# Prefer manual subs, fall back to auto-generated
yt-dlp --write-sub --write-auto-sub --sub-lang en --sub-format srt \
  --convert-subs srt --skip-download \
  URL
```

| Flag | Purpose |
|---|---|
| `--write-auto-sub` | Download auto-generated (speech-to-text) subtitles |
| `--write-sub` | Download human-uploaded subtitles |
| `--sub-lang en` | English subtitles only |
| `--sub-format srt` | Request SRT format |
| `--convert-subs srt` | Convert to SRT if source is different format (e.g., VTT) |
| `--skip-download` | Do not download the video, just the subtitles |

### Step 2: Trim Subtitles to Match Clip Time Range

The downloaded SRT covers the full video. You need to trim it to your clip's time range and re-zero the timestamps.

```bash
# ffmpeg can extract a subtitle segment
ffmpeg -i full_subs.srt -ss 1:43:00 -to 1:45:00 clip_subs.srt
```

This extracts only the subtitle entries within the time range and adjusts timestamps to start at 00:00:00.

**Alternative: Python script for precise control:**

```python
import re
from datetime import timedelta

def parse_srt_time(time_str):
    """Parse SRT timestamp to timedelta."""
    h, m, s = time_str.replace(',', '.').split(':')
    return timedelta(hours=int(h), minutes=int(m), seconds=float(s))

def format_srt_time(td):
    """Format timedelta as SRT timestamp."""
    total = int(td.total_seconds() * 1000)
    h = total // 3600000
    m = (total % 3600000) // 60000
    s = (total % 60000) // 1000
    ms = total % 1000
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

def trim_srt(input_file, output_file, start_seconds, end_seconds):
    """Trim SRT file to a time range, re-zeroing timestamps."""
    start = timedelta(seconds=start_seconds)
    end = timedelta(seconds=end_seconds)

    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Parse SRT blocks
    blocks = re.split(r'\n\n+', content.strip())
    trimmed = []
    idx = 1

    for block in blocks:
        lines = block.strip().split('\n')
        if len(lines) >= 3:
            time_line = lines[1]
            match = re.match(
                r'(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2},\d{3})',
                time_line
            )
            if match:
                sub_start = parse_srt_time(match.group(1))
                sub_end = parse_srt_time(match.group(2))

                if sub_end > start and sub_start < end:
                    # Clamp and re-zero
                    new_start = max(sub_start - start, timedelta(0))
                    new_end = min(sub_end - start, end - start)
                    text = '\n'.join(lines[2:])

                    trimmed.append(
                        f"{idx}\n"
                        f"{format_srt_time(new_start)} --> {format_srt_time(new_end)}\n"
                        f"{text}"
                    )
                    idx += 1

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n\n'.join(trimmed) + '\n')

# Usage: trim to 1:43:00 - 1:45:00
trim_srt('video.en.srt', 'clip.srt', 6180, 6300)
```

### Step 3: Burn Subtitles into Video

```bash
# Basic burn-in
ffmpeg -i clip.mp4 -vf "subtitles=clip.srt" -c:a copy output.mp4

# With custom styling (larger font, background box)
ffmpeg -i clip.mp4 \
  -vf "subtitles=clip.srt:force_style='FontName=Arial,FontSize=24,PrimaryColour=&H00FFFFFF,BackColour=&H80000000,BorderStyle=4,Outline=0,Shadow=0,MarginV=30'" \
  -c:v libx264 -crf 22 -c:a copy \
  output.mp4
```

### Subtitle Style Parameters (ASS Format)

| Parameter | Example | Effect |
|---|---|---|
| `FontName` | `Arial` | Font family |
| `FontSize` | `24` | Font size |
| `PrimaryColour` | `&H00FFFFFF` | Text color (ABGR hex, white) |
| `BackColour` | `&H80000000` | Background color (semi-transparent black) |
| `BorderStyle` | `4` | 1=outline, 3=opaque box, 4=shadow box |
| `Outline` | `2` | Outline thickness in pixels |
| `Shadow` | `0` | Shadow depth |
| `MarginV` | `30` | Vertical margin from bottom |
| `Bold` | `1` | Bold text |

**Color format:** `&HAABBGGRR` where AA=alpha (00=opaque, FF=transparent), BB=blue, GG=green, RR=red.

### One-Command: Download Clip + Burn Subtitles

This is not possible in a single yt-dlp invocation. The workflow requires:
1. Download the clip
2. Download/trim subtitles
3. Burn subtitles with ffmpeg

---

## 8. End-to-End Workflow

### The complete pipeline for: "I found an interesting segment, now I want a social-media-ready clip"

```
Step 1               Step 2                Step 3              Step 4
┌──────────┐    ┌──────────────┐    ┌───────────────┐    ┌──────────────┐
│ Identify │    │   Download   │    │ (Optional)    │    │   Format     │
│ segment  │───>│   clip with  │───>│ Download +    │───>│   for social │
│ from     │    │   yt-dlp     │    │ burn subs     │    │   media      │
│ transcript│    └──────────────┘    └───────────────┘    └──────────────┘
└──────────┘
  1:43:00         --download-         Subtitle trim         -movflags
  to 1:45:00      sections            + ffmpeg burn          +faststart
```

### Step-by-Step Commands

```bash
VIDEO_URL="https://www.youtube.com/watch?v=XXXXXXXXXXXX"
START="1:43:00"
END="1:45:00"
START_SEC=6180
END_SEC=6300
OUTPUT="clip"

# --- Step 1: Download the clip ---
yt-dlp --download-sections "*${START}-${END}" \
  --force-keyframes-at-cuts \
  -f "bestvideo[ext=mp4][height<=1080]+bestaudio[ext=m4a]/best[ext=mp4]" \
  --merge-output-format mp4 \
  -o "${OUTPUT}_raw.%(ext)s" \
  "$VIDEO_URL"

# --- Step 2 (optional): Download and trim subtitles ---
yt-dlp --write-auto-sub --write-sub --sub-lang en \
  --sub-format srt --convert-subs srt \
  --skip-download \
  -o "${OUTPUT}" \
  "$VIDEO_URL"

# Trim subtitles to clip range (using ffmpeg)
ffmpeg -i "${OUTPUT}.en.srt" -ss "$START" -to "$END" "${OUTPUT}_trimmed.srt"

# --- Step 3: Final encode with subtitles burned in ---
ffmpeg -i "${OUTPUT}_raw.mp4" \
  -vf "subtitles=${OUTPUT}_trimmed.srt:force_style='FontName=Arial,FontSize=22,PrimaryColour=&H00FFFFFF,BackColour=&H80000000,BorderStyle=4'" \
  -c:v libx264 -profile:v high -level 4.0 \
  -crf 22 -preset medium \
  -pix_fmt yuv420p \
  -c:a aac -b:a 128k \
  -movflags +faststart \
  -r 30 \
  "${OUTPUT}_final.mp4"

# --- Step 3 (alt): Final encode WITHOUT subtitles ---
ffmpeg -i "${OUTPUT}_raw.mp4" \
  -c:v libx264 -profile:v high -level 4.0 \
  -crf 22 -preset medium \
  -pix_fmt yuv420p \
  -c:a aac -b:a 128k \
  -movflags +faststart \
  -r 30 \
  "${OUTPUT}_final.mp4"

# Clean up intermediate files
rm -f "${OUTPUT}_raw.mp4" "${OUTPUT}.en.srt" "${OUTPUT}_trimmed.srt"
```

### Without Subtitles (Simplest Path)

If you do not need subtitles, the entire workflow collapses to one command:

```bash
yt-dlp --download-sections "*1:43:00-1:45:00" \
  --force-keyframes-at-cuts \
  -f "bestvideo[ext=mp4][height<=1080]+bestaudio[ext=m4a]/best[ext=mp4]" \
  --merge-output-format mp4 \
  --postprocessor-args "ffmpeg:-c:v libx264 -profile:v high -pix_fmt yuv420p -c:a aac -b:a 128k -movflags +faststart" \
  -o "clip.%(ext)s" \
  "https://www.youtube.com/watch?v=XXXXXXXXXXXX"
```

Note: `--postprocessor-args` runs AFTER download/merge, so this re-encodes the clip with social-media-friendly settings in one pass.

---

## 9. Shell Script

A reusable script for the full workflow:

```bash
#!/bin/bash
# ytclip.sh - Extract a clip from a YouTube video
#
# Usage:
#   ./ytclip.sh <url> <start> <end> [--subs] [--output name]
#
# Examples:
#   ./ytclip.sh "https://youtube.com/watch?v=abc" "1:43:00" "1:45:00"
#   ./ytclip.sh "https://youtube.com/watch?v=abc" "1:43:00" "1:45:00" --subs
#   ./ytclip.sh "https://youtube.com/watch?v=abc" "0:30" "2:00" --subs --output my_clip

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
echo "URL: ${URL}"
echo "Subtitles: ${SUBS}"
echo "Output: ${OUTPUT}_final.mp4"
echo "---"

# Convert timestamp to seconds for subtitle trimming
ts_to_sec() {
  local parts
  IFS=: read -ra parts <<< "$1"
  local len=${#parts[@]}
  local sec=0
  if [ "$len" -eq 3 ]; then
    sec=$(( ${parts[0]} * 3600 + ${parts[1]} * 60 + ${parts[2]} ))
  elif [ "$len" -eq 2 ]; then
    sec=$(( ${parts[0]} * 60 + ${parts[1]} ))
  else
    sec="${parts[0]}"
  fi
  echo "$sec"
}

# Step 1: Download clip
yt-dlp --download-sections "*${START}-${END}" \
  --force-keyframes-at-cuts \
  -f "bestvideo[ext=mp4][height<=1080]+bestaudio[ext=m4a]/best[ext=mp4]" \
  --merge-output-format mp4 \
  -o "${OUTPUT}_raw.mp4" \
  "$URL"

if [ "$SUBS" = true ]; then
  echo "Downloading subtitles..."

  # Step 2: Download subtitles
  yt-dlp --write-auto-sub --write-sub --sub-lang en \
    --sub-format srt --convert-subs srt \
    --skip-download \
    -o "${OUTPUT}" \
    "$URL" 2>/dev/null || true

  SRT_FILE=$(ls ${OUTPUT}*.srt 2>/dev/null | head -1)

  if [ -n "$SRT_FILE" ]; then
    echo "Trimming subtitles..."
    ffmpeg -y -i "$SRT_FILE" -ss "$START" -to "$END" "${OUTPUT}_trimmed.srt" 2>/dev/null

    echo "Encoding with subtitles..."
    ffmpeg -y -i "${OUTPUT}_raw.mp4" \
      -vf "subtitles=${OUTPUT}_trimmed.srt:force_style='FontName=Arial,FontSize=22,PrimaryColour=&H00FFFFFF,BackColour=&H80000000,BorderStyle=4,MarginV=25'" \
      -c:v libx264 -profile:v high -level 4.0 \
      -crf 22 -preset medium \
      -pix_fmt yuv420p \
      -c:a aac -b:a 128k \
      -movflags +faststart \
      -r 30 \
      "${OUTPUT}_final.mp4"

    rm -f "$SRT_FILE" "${OUTPUT}_trimmed.srt"
  else
    echo "No subtitles found. Encoding without."
    SUBS=false
  fi
fi

if [ "$SUBS" = false ]; then
  echo "Encoding for social media..."
  ffmpeg -y -i "${OUTPUT}_raw.mp4" \
    -c:v libx264 -profile:v high -level 4.0 \
    -crf 22 -preset medium \
    -pix_fmt yuv420p \
    -c:a aac -b:a 128k \
    -movflags +faststart \
    -r 30 \
    "${OUTPUT}_final.mp4"
fi

rm -f "${OUTPUT}_raw.mp4"

echo "---"
echo "Done: ${OUTPUT}_final.mp4"
ls -lh "${OUTPUT}_final.mp4"
```

---

## Dependencies

```bash
# macOS (Homebrew)
brew install yt-dlp ffmpeg

# Verify
yt-dlp --version
ffmpeg -version
```

Both are required. ffmpeg is needed by yt-dlp for:
- Merging separate video+audio DASH streams
- Re-encoding at cut points (`--force-keyframes-at-cuts`)
- Subtitle conversion
- Format remuxing

---

## Quick Reference Card

```
DOWNLOAD CLIP (no subs):
  yt-dlp --download-sections "*START-END" --force-keyframes-at-cuts \
    -f "bestvideo[ext=mp4][height<=1080]+bestaudio[ext=m4a]" \
    --merge-output-format mp4 -o "clip.%(ext)s" URL

DOWNLOAD SUBTITLES ONLY:
  yt-dlp --write-auto-sub --sub-lang en --convert-subs srt --skip-download URL

BURN SUBTITLES:
  ffmpeg -i clip.mp4 -vf "subtitles=subs.srt" -c:v libx264 -c:a copy out.mp4

SOCIAL MEDIA ENCODE:
  ffmpeg -i in.mp4 -c:v libx264 -profile:v high -pix_fmt yuv420p \
    -c:a aac -b:a 128k -movflags +faststart -r 30 out.mp4

GET STREAM URLS:
  yt-dlp --youtube-skip-dash-manifest -g URL
```

---

## Sources

- yt-dlp GitHub Issues: #10970, #8793, #7703, #10181, #11176, #12408, #12540, #13333
- yt-dlp README and CLI help
- Stack Overflow / Unix Stack Exchange: youtube-dl + ffmpeg approaches
- FFmpeg wiki: HowToBurnSubtitlesIntoVideo
- Social media specs: postfa.st, socialrails.com, recurpost.com, heyorca.com (2026 specs)
- Mux.com articles on ffmpeg clipping and subtitle extraction
- owainlewis/clippy GitHub project (reference implementation)
