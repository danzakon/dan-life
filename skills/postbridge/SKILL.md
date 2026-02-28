---
name: post-bridge-social-manager
description: Autonomously manage social media posting using the Post Bridge API. Use when scheduling, posting, or managing content across TikTok, Instagram Reels, YouTube Shorts, Twitter/X, LinkedIn, Pinterest, Facebook, Threads, or Bluesky. Covers media upload, post creation, scheduling, platform-specific configs, draft mode, and post result tracking.
allowed-tools:
  - Read
  - Bash
  - Write
---

# Post Bridge Social Manager

Autonomously manage social media posting via [Post Bridge](https://post-bridge.com) API.

**Requirements:** `POST_BRIDGE_API_KEY` in `~/.config/postbridge/.env`, `ffmpeg` installed.

## Setup

1. Create a Post Bridge account at [post-bridge.com](https://post-bridge.com)
2. Connect your social accounts (Twitter/X, LinkedIn, etc.)
3. Enable API access ($5/mo add-on)
4. API key is stored at `~/.config/postbridge/.env`:
   ```
   POST_BRIDGE_API_KEY=pb_live_xxxxx
   ```

## Auth

Load the key from config, then use as Bearer token:
```bash
# Read key
POST_BRIDGE_API_KEY=$(grep POST_BRIDGE_API_KEY ~/.config/postbridge/.env | cut -d= -f2)
```
```
Authorization: Bearer <POST_BRIDGE_API_KEY>
```

Base URL: `https://api.post-bridge.com`

## Core Workflow

### 1. Get Social Accounts
```
GET /v1/social-accounts
```
Returns array of connected accounts with `id`, `platform`, `username`. Store these IDs — you need them for every post.

### 2. Upload Media
```
POST /v1/media/create-upload-url
Body: { "mime_type": "video/mp4", "size_bytes": <int>, "name": "video.mp4" }
```
Returns `media_id` + `upload_url`. Then:
```
PUT <upload_url>
Content-Type: video/mp4
Body: <binary file>
```

### 3. Create Post
```
POST /v1/posts
Body: {
  "caption": "your caption here #hashtags",
  "media": ["<media_id>"],
  "social_accounts": [<account_id_1>, <account_id_2>],
  "scheduled_at": "2026-01-01T14:00:00Z",  // omit for instant post
  "platform_configurations": { ... }  // optional, see below
}
```

### 4. Check Results
```
GET /v1/posts/<post_id>
```
Returns status: `processing`, `scheduled`, `posted`, `failed`.

## Platform Configurations

Pass inside `platform_configurations` object on post creation:

**TikTok:**
- `draft: true` — save as draft (publish manually on TikTok with trending sound)
- `video_cover_timestamp_ms: 3000` — cover thumbnail at 3 seconds
- `is_aigc: true` — label as AI-generated content

**Instagram:**
- `video_cover_timestamp_ms: 3000` — cover thumbnail
- `is_trial_reel: true` — trial reel mode (needs 1000+ followers)
- `trial_graduation: "SS_PERFORMANCE"` — auto-graduate based on performance

**YouTube:**
- `video_cover_timestamp_ms: 3000` — cover thumbnail
- `title: "My Short Title"` — override post title

**Twitter/X:**
- `caption: "override caption"` — platform-specific caption

All platforms support `caption` and `media` overrides for per-platform customization.

## Recommended Workflow for Video Content

1. Store videos in a local folder
2. Extract a frame with ffmpeg to read any text overlays:
   ```
   ffmpeg -i video.mp4 -ss 00:00:04 -frames:v 1 frame.jpg -y
   ```
3. Write caption based on video content + hashtags
4. Upload → create post → schedule or post instantly
5. Move posted videos to a `posted/` subfolder to avoid duplicates
6. Set a cron to check post status 5 mins after scheduled time
7. Track performance by browsing platform pages or checking post results

## Content Pipeline Integration

This skill integrates with the content pipeline in `content/pipeline/`.

### Scheduling from Queue

When scheduling posts from the pipeline queue (`content/pipeline/queue.md`):

1. Read the queue for entries with status `queued` and today's (or specified) target date
2. For each entry, the queue provides Twitter and LinkedIn content variants
3. Get social account IDs via `GET /v1/social-accounts` (cache these -- they don't change)
4. Create the post with platform-specific content overrides:
   ```json
   {
     "caption": "{LinkedIn content (default)}",
     "social_accounts": [twitter_id, linkedin_id],
     "scheduled_at": "{ISO 8601 timestamp}",
     "platform_configurations": {
       "twitter": {
         "caption": "{Twitter-specific content}"
       }
     }
   }
   ```
5. Spread posts through the day (e.g., 9am, 12pm, 3pm, 6pm) for better reach
6. After successful scheduling, update `queue.md` status: `queued` -> `scheduled`
7. Append to `content/pipeline/history.md`:
   ```
   | {date} | Twitter, LinkedIn | post | {first line of content} | posts/{weekly-file} |
   ```

### Checking Post Results

After posts are published, check results to confirm:

```
GET /v1/post-results
```

Update history.md with confirmation and any platform URLs returned.

## Tips

- Post to multiple platforms simultaneously by including multiple account IDs
- Stagger posts throughout the day (e.g. 9am + 3pm) for better reach
- Use `scheduled_at` to pre-schedule batches -- Post Bridge handles the timing
- Use platform-specific caption overrides for Twitter (shorter) vs LinkedIn (more context)
- Keep hashtags to 4-5 per post for best engagement
- Monitor what works and iterate on captions/formats
