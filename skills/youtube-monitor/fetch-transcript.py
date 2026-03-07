#!/usr/bin/env python3
"""
Fetch a YouTube video transcript and write it to content/raw/youtube/.

Usage:
    python3 fetch-youtube-transcript.py <youtube_url> <output_id> [--slug <slug>]

Arguments:
    youtube_url   Full YouTube URL or video ID
    output_id     Pipeline item ID (e.g., 20260307-YM-001)
    --slug        Optional short slug for the filename (derived from title if omitted)

Output:
    Writes to content/raw/youtube/{output_id}-{slug}.md
    Prints the output file path on success, or an error message on failure.

Prerequisites:
    pip install youtube-transcript-api
"""

import sys
import re
import os
import json
import argparse
from datetime import datetime, timezone

def extract_video_id(url):
    """Extract YouTube video ID from various URL formats."""
    patterns = [
        r'(?:v=|/v/|youtu\.be/|/embed/|/shorts/)([A-Za-z0-9_-]{11})',
        r'^([A-Za-z0-9_-]{11})$',  # bare video ID
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def slugify(text, max_len=60):
    """Convert text to a filename-safe slug."""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = text.strip('-')
    return text[:max_len]

def fetch_transcript(video_id):
    """Fetch transcript using youtube-transcript-api."""
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
    except ImportError:
        print("ERROR: youtube-transcript-api not installed. Run: pip install youtube-transcript-api", file=sys.stderr)
        sys.exit(1)

    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

        # Prefer manual English, fall back to auto-generated
        try:
            transcript = transcript_list.find_manually_created_transcript(['en'])
        except Exception:
            try:
                transcript = transcript_list.find_generated_transcript(['en'])
            except Exception:
                # Try any available language
                transcript = list(transcript_list)[0]

        return transcript.fetch(), transcript.language_code, transcript.is_generated

    except Exception as e:
        print(f"ERROR: Could not fetch transcript — {e}", file=sys.stderr)
        sys.exit(1)

def get_video_title(video_id):
    """Attempt to get video title via yt-dlp, fall back to video ID."""
    try:
        import subprocess
        result = subprocess.run(
            ['yt-dlp', '--print', 'title', '--no-playlist', f'https://youtube.com/watch?v={video_id}'],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return video_id  # fall back to ID if yt-dlp unavailable

def format_timestamp(seconds):
    """Convert seconds to HH:MM:SS format."""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"

def main():
    parser = argparse.ArgumentParser(description='Fetch YouTube transcript')
    parser.add_argument('url', help='YouTube URL or video ID')
    parser.add_argument('output_id', help='Pipeline item ID (e.g., 20260307-YM-001)')
    parser.add_argument('--slug', help='Filename slug (derived from title if omitted)')
    parser.add_argument('--repo-root', default='.', help='Path to repo root')
    args = parser.parse_args()

    video_id = extract_video_id(args.url)
    if not video_id:
        print(f"ERROR: Could not extract video ID from: {args.url}", file=sys.stderr)
        sys.exit(1)

    video_url = f"https://www.youtube.com/watch?v={video_id}"
    print(f"Fetching transcript for {video_url}...", file=sys.stderr)

    title = get_video_title(video_id)
    slug = args.slug or slugify(title)

    transcript_data, lang, is_generated = fetch_transcript(video_id)

    # Format transcript with timestamps
    lines = []
    for entry in transcript_data:
        ts = format_timestamp(entry['start'])
        text = entry['text'].replace('\n', ' ').strip()
        lines.append(f"[{ts}] {text}")

    transcript_text = '\n'.join(lines)
    now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    date_prefix = args.output_id[:8]  # YYYYMMDD from ID

    # Build output filename and path
    filename = f"{args.output_id}-{slug}.md"
    output_dir = os.path.join(args.repo_root, 'content', 'raw', 'youtube')
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, filename)

    frontmatter = f"""---
id: {args.output_id}
source-type: youtube
ingest-source: youtube-monitor
video-id: {video_id}
original-url: {video_url}
title: {title}
transcript-language: {lang}
transcript-type: {"auto-generated" if is_generated else "manual"}
captured: {now}
---

# {title}

**URL:** {video_url}
**Transcript language:** {lang} ({"auto-generated" if is_generated else "manual"})
**Captured:** {now}

---

## Transcript

{transcript_text}
"""

    with open(output_path, 'w') as f:
        f.write(frontmatter)

    # Print output path for the calling skill to use
    print(output_path)

if __name__ == '__main__':
    main()
