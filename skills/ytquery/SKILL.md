---
name: ytquery
description: Query YouTube from the command line — channel videos, metadata, transcripts,
  thumbnails, screenshots, clips, Watch Later, and search. Use when asked to "check
  YouTube", "get transcript", "clip this video", "download thumbnail", "search YouTube",
  "check Watch Later", or when YouTube data is needed.
argument-hint: "[y:command] [args]" e.g. "y:channel @lexfridman" or "y:transcript URL"
allowed-tools: Bash
---

# ytquery: YouTube CLI

A comprehensive YouTube data tool, mirroring xquery's interface pattern for X/Twitter.

## Usage

```bash
# Channel videos
ytquery y:channel @lexfridman              # Recent videos from channel
ytquery y:channel @mkbhd --limit 20        # More results

# Video metadata
ytquery y:video "https://youtube.com/watch?v=abc"   # Full metadata
ytquery y:video abc123                              # By video ID

# Transcripts
ytquery y:transcript "URL"                  # Print transcript to stdout
ytquery y:transcript "URL" --output t.md    # Save to file
ytquery y:transcript "URL" --json           # Structured JSON with timestamps

# Thumbnails
ytquery y:thumbnail "URL"                   # Download as {id}-thumb.jpg
ytquery y:thumbnail "URL" -o cover.jpg      # Custom output path

# Screenshots (frame at timestamp)
ytquery y:screenshot "URL" 1:23:45          # Extract frame at timestamp
ytquery y:screenshot "URL" 0:08:14 -o f.jpg # Custom output

# Video clips (for social media)
ytquery y:clip "URL" 1:43:00 1:45:00        # Extract 2-min clip
ytquery y:clip "URL" 0:30 2:00 --subs       # With burned-in subtitles
ytquery y:clip "URL" 1:00:00 1:02:20 -o my_clip  # Custom name

# Watch Later (requires cookies)
ytquery y:watchlater                        # List Watch Later videos
ytquery y:watchlater --limit 50             # More results
ytquery y:watchlater --json                 # JSON output

# Search
ytquery y:search "AI engineering"           # Search YouTube
ytquery y:search "Claude Code" --limit 20   # More results

# RSS feed URL
ytquery y:rss @lexfridman                   # Get channel RSS URL
```

The `ytquery` command must be in the user's PATH. Symlink to `~/.local/bin/ytquery` if needed.

## Options

| Flag | Description |
|------|-------------|
| `--json` | Output raw JSON (structured, for scripts) |
| `--limit N` | Number of results (default: 10) |
| `--output PATH` or `-o PATH` | Output file path (transcript, thumbnail, screenshot, clip) |
| `--subs` | Burn subtitles into clip (y:clip only) |

## When to Use

**Use y:channel** when:
- Checking a channel for new videos
- Listing recent uploads from a creator
- Channel monitoring for the content pipeline

**Use y:video** when:
- Need metadata: title, duration, views, likes, description
- Looking up a specific video before deciding to pull a transcript

**Use y:transcript** when:
- Pulling a transcript for content mining
- Ingesting a video into the content pipeline
- Reading a long video without watching it

**Use y:thumbnail** when:
- Need a video's preview image for social posts or articles
- Downloading cover art for content

**Use y:screenshot** when:
- Capturing a specific frame (diagram, code, slide) from a video
- Creating images for posts that reference a specific moment

**Use y:clip** when:
- Extracting a segment for social media posting (X, LinkedIn)
- Clipping a podcast highlight with commentary
- Creating short-form content from long-form videos
- Output is social-media-ready: H.264, AAC, MP4, faststart

**Use y:watchlater** when:
- Mining Watch Later for content ideas (like bookmark-mining for X)
- Triaging saved videos
- Note: requires cookie setup (see below)

**Use y:search** when:
- Finding videos on a topic
- Researching what exists before writing content

**Use y:rss** when:
- Getting a channel's RSS feed URL for monitoring
- Setting up sources.md entries

## Setup

### Dependencies

```bash
pip install yt-dlp youtube-transcript-api
brew install ffmpeg deno
```

| Package | Why |
|---------|-----|
| `yt-dlp` | Video metadata, downloads, clip extraction, Watch Later |
| `youtube-transcript-api` | Transcript fetching (v1.2+ API) |
| `ffmpeg` | Thumbnail conversion, screenshots, clip encoding |
| `deno` | Required by yt-dlp for YouTube JS challenges since Nov 2025 |

### Symlink to PATH

```bash
ln -sf ~/dev/life/skills/ytquery/scripts/ytquery ~/.local/bin/ytquery
```

### Config (Optional)

Config file: `~/.config/ytquery/.env`

```bash
# Cookie file for Watch Later and age-restricted content
# See Watch Later Setup below for how to create this
YOUTUBE_COOKIES=~/.config/ytquery/cookies.txt
```

### Watch Later Setup

Watch Later requires browser cookies (YouTube blocked API access in 2016). One-time setup, re-export every ~2 weeks:

1. Install "Get cookies.txt LOCALLY" Firefox extension
2. Open a **private/incognito** window
3. Log into YouTube
4. Navigate to `youtube.com/robots.txt` (prevents cookie rotation)
5. Export cookies, save to `~/.config/ytquery/cookies.txt`
6. **Close the incognito window immediately**

Add to `~/.config/ytquery/.env`:
```bash
YOUTUBE_COOKIES=~/.config/ytquery/cookies.txt
```

## Social Media Clip Specs

`y:clip` outputs are encoded for universal social media compatibility:

| Setting | Value | Why |
|---------|-------|-----|
| Codec | H.264 High + AAC | Works on every platform |
| Pixel format | yuv420p | Required for broad device support |
| Frame rate | 30 fps | X and LinkedIn recommend 30fps |
| Quality | CRF 22 | Good quality, reasonable file size |
| Metadata | +faststart | Required by some platforms |

**Platform limits:**
- X (free): 512 MB, 2:20 duration
- X (Premium+): 16 GB, 4 hours
- LinkedIn: 5 GB, 10-15 min

The script warns if a clip exceeds X free tier limits.

## Integration with Other Skills

ytquery is the YouTube data layer. Other skills call it via Bash:

| Skill | ytquery Command | Purpose |
|-------|----------------|---------|
| `youtube-monitor` | `y:channel`, `y:transcript`, `y:thumbnail` | Channel monitoring, transcript ingestion |
| `bookmark-mining` (YouTube equivalent) | `y:watchlater` | Watch Later mining for content ideas |
| `write-post` | `y:clip`, `y:screenshot` | Attach video/image to posts |
| `content-pipeline` | `y:transcript`, `y:video` | On-demand video ingestion |
| `save-raw` | `y:transcript`, `y:video` | Manual URL ingestion |
