# Social Media Video Upload Specs & Encoding Research

Research date: 2026-03-07

---

## 1. Twitter/X Video Specifications

### Upload Limits

| Spec | Free/Basic | Premium Plus |
|------|-----------|--------------|
| Max file size | 512 MB | 16 GB (web/iOS) |
| Max duration | 2 min 20 sec (140s) | 4 hours (web/iOS), 10 min (Android) |
| Resolution cap | 720p | 1080p (up to 2h), 720p (2-4h) |
| Formats | MP4, MOV | MP4, MOV |
| Frame rate | 30 fps recommended | 30 fps recommended |

### Supported Codecs

- **Video:** H.264 (required). VP9 is rejected at FINALIZE or during processing.
- **Audio:** AAC
- **Container:** MP4 or MOV

### Resolutions & Aspect Ratios

| Orientation | Resolution | Aspect Ratio |
|-------------|-----------|--------------|
| Landscape | 1280x720 | 16:9 (recommended) |
| Vertical | 720x1280 | 9:16 |
| Square | 720x720 | 1:1 |

### API Upload (X API v2)

Yes, video upload is fully supported via the v2 API. The v1.1 media upload endpoints were deprecated for self-serve tiers on March 31, 2025.

**Chunked upload flow (3 steps):**

```
INIT -> APPEND (chunks) -> FINALIZE -> poll STATUS
```

1. **INIT** -- `POST /2/media/upload/initialize` with `media_type`, `total_bytes`, `media_category` (`tweet_video`). Returns `media_id`.
2. **APPEND** -- `POST /2/media/upload/{media_id}/append` as multipart/form-data. Max 5 MB per chunk. Each chunk has a `segment_index` starting at 0.
3. **FINALIZE** -- `POST /2/media/upload/{media_id}/finalize`. For videos, response includes `processing_info` with `check_after_secs`.
4. **STATUS** -- `GET /2/media/upload/{media_id}` -- poll until `state` is `succeeded`.

Then attach to a tweet:

```json
{
  "text": "Your caption",
  "media": {
    "media_ids": ["<MEDIA_ID>"]
  }
}
```

**Rate limits per tier:**

| Tier | Posts | Media uploads (24h) | Cost |
|------|-------|-------------------|------|
| Free | 500/month (~17/day) | 85 total (34 init, 170 append, 34 finalize) | $0 |
| Basic | Higher (varies) | Higher | $200/mo |
| Pro | Significantly higher | Full access | $5,000/mo |

**Auth:** OAuth 2.0 with PKCE (recommended) or OAuth 1.0a. Requires `tweet.read`, `tweet.write`, `users.read`, `media.write`, `offline.access` scopes. Access tokens expire after 2 hours; use refresh tokens.

---

## 2. LinkedIn Video Specifications

### Upload Limits

| Spec | Organic Posts | Ads / Company Pages |
|------|-------------|-------------------|
| Max file size | 5 GB | 200 MB |
| Max duration | 10 min (15 min on desktop) | 30 min |
| Min duration | 3 seconds | 3 seconds |
| Formats | MP4, MOV | MP4, MOV |
| Frame rate | 30 fps max | 30 fps max |
| Audio | AAC or MPEG4, <64 kHz | AAC or MPEG4, <64 kHz |

**Engagement note:** Videos under 60 seconds get significantly more engagement.

### Supported Codecs

- **Video:** H.264 (primary), VP8, VP9, HEVC also accepted
- **Audio:** AAC or MPEG4
- **Container:** MP4 (recommended), MOV, ASF, MKV, MPEG, WMV

### Resolutions & Aspect Ratios

| Orientation | Resolution | Aspect Ratio |
|-------------|-----------|--------------|
| Landscape | 1920x1080 | 16:9 (recommended for desktop) |
| Portrait | 1080x1350 | 4:5 (recommended for mobile feed) |
| Square | 1080x1080 | 1:1 |
| Full vertical | 1080x1920 | 9:16 |

### API Upload (LinkedIn Videos API)

Yes, video upload is supported via the **Videos API** (replaced the deprecated Assets API).

**Requires:** LinkedIn Partner Program membership. The review process is notoriously slow (weeks to months). Requires a Company Page for the developer app.

**Permissions:** `w_member_social` (personal), `w_organization_social` (org pages). Uses the Posts API (`/rest/posts`) for publishing.

**Upload flow (4 steps with ETag tracking):**

```
initializeUpload -> upload chunks -> finalizeUpload -> poll status
```

1. `POST /rest/videos?action=initializeUpload` with owner URN, `fileSizeBytes`, `uploadThumbnail: true`. Returns video URN, `uploadToken`, and `uploadInstructions` (array of parts with byte ranges and upload URLs).
2. Upload each 4 MB chunk to its assigned URL. **Save the `ETag` from each response header** -- this is critical.
3. `POST /rest/videos?action=finalizeUpload` with video URN, `uploadToken`, and `uploadedPartIds` (the array of ETags). Fails if any ETag is missing.
4. Poll `GET /rest/videos/{video-urn}` until status is `AVAILABLE`.

**Limits:** MP4 only for API, 3 sec to 30 min, 75 KB to 500 MB via API.

**Gotcha:** LinkedIn's API versioning is aggressive -- Marketing API versions are sunset rapidly. Rate limits are hidden; you discover them empirically.

---

## 3. PostBridge API -- Media & Video Support

PostBridge (post-bridge.com) **fully supports video and image uploads** via their API.

### Access

- Requires active PostBridge subscription + $5/mo API add-on
- API keys at: `https://www.post-bridge.com/dashboard/api-keys`
- Docs: `https://api.post-bridge.com/reference`
- Support: Discord `#api` channel

### Media Upload Endpoint

**`POST /v1/media/create-upload-url`**

Creates a signed upload URL for media files.

| Parameter | Description |
|-----------|-------------|
| `mime_type` | `image/png`, `image/jpeg`, `video/mp4`, `video/quicktime` |
| `size_bytes` | File size in bytes |
| `name` | Filename |

**Returns:** `media_id` and `upload_url` (signed URL for client-side upload).

**Flow:**

```
1. POST /v1/media/create-upload-url  -->  get media_id + upload_url
2. PUT file to upload_url  (client-side upload to signed URL)
3. POST /v1/posts  -->  reference media_id in `media` array
```

### Post Creation with Media

**`POST /v1/posts`**

| Parameter | Type | Description |
|-----------|------|-------------|
| `caption` | string (required) | Post text |
| `media` | array | Array of `media_id` values from upload step |
| `media_urls` | array | Alternative: array of public URLs (PostBridge fetches) |
| `social_accounts` | array (required) | Account IDs to post to |
| `scheduled_at` | ISO datetime | Schedule for future (omit for immediate) |
| `platform_configurations` | object | Platform-specific overrides |
| `account_configurations` | object | Account-specific overrides |
| `is_draft` | boolean | Save as draft |
| `processing_enabled` | boolean | Default true; PostBridge processing |

### Other Media Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/media` | GET | List media (filterable by `type`: image/video) |
| `/v1/media/{id}` | GET | Get specific media |
| `/v1/media/{id}` | DELETE | Delete media |

### Supported Platforms

TikTok, YouTube, Instagram, LinkedIn, Pinterest, Threads, Twitter/X, Facebook, Bluesky.

### Video-Specific Features

- YouTube Shorts: 9:16 videos under 3 min auto-posted as Shorts
- Custom thumbnails supported for Instagram and TikTok
- YouTube titles/descriptions via `platform_configurations`
- Carousel/slideshow posts supported

### Key Takeaway

PostBridge handles all the platform-specific video transcoding, chunked uploads, ETag tracking, and container model differences behind the scenes. You upload once, and it distributes to all platforms. This is a massive simplification compared to direct API integration.

---

## 4. Optimal FFmpeg Encoding Settings

### The Universal Social Media Command

Every major platform accepts **MP4 container + H.264 video + AAC audio**. This is the one format that works everywhere without re-encoding surprises.

```bash
ffmpeg -i input.mp4 \
  -c:v libx264 \
  -preset medium \
  -crf 18 \
  -profile:v high \
  -level 4.1 \
  -pix_fmt yuv420p \
  -movflags +faststart \
  -c:a aac \
  -b:a 192k \
  output.mp4
```

### Flag Breakdown

| Flag | Purpose |
|------|---------|
| `-c:v libx264` | H.264 codec -- universally accepted by all platforms |
| `-preset medium` | Balance of speed vs compression. ~95% quality of `slower` at half the encode time |
| `-crf 18` | Constant Rate Factor. 18 is "visually lossless" sweet spot. Range 0-51; lower = better quality, larger file |
| `-profile:v high` | High profile -- best compression tools while staying broadly compatible |
| `-level 4.1` | Compatibility with older devices. Supports up to 1080p60 |
| `-pix_fmt yuv420p` | 4:2:0 chroma subsampling -- required for broad device compatibility |
| `-movflags +faststart` | Moves the moov atom to the front of the file for progressive playback. Critical for web/social uploads |
| `-c:a aac` | AAC audio codec -- universal compatibility |
| `-b:a 192k` | 192 kbps audio bitrate. Good quality for speech and music |

### CRF Guidelines by Content Type

| Content Type | CRF | Notes |
|-------------|-----|-------|
| Talking head / simple | 22-25 | Low motion, simple backgrounds. Higher CRF is fine |
| Screen recording / slides | 20-23 | Sharp edges and text benefit from slightly lower CRF |
| General / mixed content | 18-22 | The safe default zone |
| Fast motion / gameplay | 16-20 | High-motion scenes need more bits |
| Animation / clean graphics | 16-20 | Flat colors and sharp edges show artifacts more |

### Preset Comparison (1080p, 5-min video)

| Preset | Encode Time | File Size | Quality |
|--------|------------|-----------|---------|
| ultrafast | ~12s | ~1.2 GB | Noticeably worse |
| medium | ~45s | ~450 MB | Excellent (sweet spot) |
| slow | ~2 min | ~420 MB | Marginally better |
| slower | ~2 min+ | ~420 MB | Diminishing returns |
| placebo | ~12 min | ~410 MB | Imperceptible gain |

**Recommendation:** Use `medium` for 90% of encodes. Use `slow` only for archival or final-output content where you will not re-encode.

### Resolution-Specific Bitrate Targets (for VBR/constrained)

If you need to constrain file size rather than using CRF:

| Resolution | Bitrate (30fps) | Bitrate (60fps) |
|-----------|-----------------|-----------------|
| 720p (1280x720) | 3-5 Mbps | 4.5-7.5 Mbps |
| 1080p (1920x1080) | 6-10 Mbps | 9-15 Mbps |
| 1440p (2560x1440) | 12-20 Mbps | 18-30 Mbps |
| 4K (3840x2160) | 25-40 Mbps | 40-60 Mbps |

### Social Media Specific Commands

**For Twitter/X (720p, tight file size):**

```bash
ffmpeg -i input.mp4 \
  -c:v libx264 -preset medium -crf 20 \
  -vf "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:-1:-1:color=black" \
  -profile:v high -level 4.1 -pix_fmt yuv420p \
  -movflags +faststart \
  -c:a aac -b:a 128k \
  -t 140 \
  twitter_output.mp4
```

**For LinkedIn (1080p, professional quality):**

```bash
ffmpeg -i input.mp4 \
  -c:v libx264 -preset medium -crf 18 \
  -vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:-1:-1:color=black" \
  -profile:v high -level 4.1 -pix_fmt yuv420p \
  -movflags +faststart \
  -c:a aac -b:a 192k \
  linkedin_output.mp4
```

**For vertical/shorts (9:16, 1080x1920):**

```bash
ffmpeg -i input.mp4 \
  -c:v libx264 -preset medium -crf 20 \
  -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:-1:-1:color=black" \
  -profile:v high -level 4.1 -pix_fmt yuv420p \
  -movflags +faststart \
  -c:a aac -b:a 128k \
  vertical_output.mp4
```

### Critical Encoding Rules

1. **Always use `-movflags +faststart`** -- Instagram and some platforms silently reject videos without the moov atom at the front.
2. **Always use `yuv420p`** -- `yuv444p` produces better quality but many devices and platforms cannot decode it.
3. **Always use H.264, not VP9 or AV1** -- X rejects VP9 outright. LinkedIn requires H.264. Instagram requires H.264. H.264 is the only codec that works on every platform in 2026.
4. **Audio must be AAC** -- All platforms require or strongly prefer AAC audio.
5. **Keep frame rate at 30fps** -- Both X and LinkedIn recommend 30fps. Higher frame rates are accepted but provide diminishing returns for social content.

---

## 5. Aspect Ratio Strategy

### Cross-Platform Comparison

```
                    X/Twitter   LinkedIn   Instagram   TikTok   YouTube
                    ---------   --------   ---------   ------   -------
16:9 (landscape)    Best        Best        OK          No       Best
 9:16 (vertical)    Good        OK          Reels       Best     Shorts
  1:1 (square)      Good        Good        Feed        No       No
  4:5 (portrait)    OK          Best mob.   Best feed   No       No
```

### Recommendation by Use Case

| Use Case | Best Ratio | Resolution | Why |
|----------|-----------|-----------|-----|
| Technical content / screen share | 16:9 | 1920x1080 | Landscape fits code, slides, demos naturally |
| LinkedIn + Twitter cross-post | 16:9 | 1920x1080 | Both platforms prefer landscape for feed |
| Mobile-first / short-form | 9:16 | 1080x1920 | TikTok, Reels, Shorts all want vertical |
| Universal safe choice | 1:1 | 1080x1080 | Works everywhere without cropping, but suboptimal everywhere |
| Instagram feed | 4:5 | 1080x1350 | Takes up maximum feed real estate on mobile |

### The "Shoot Once, Export Multiple" Strategy

If you are producing content that needs to go to multiple platforms:

```
Master recording: 16:9 at 1920x1080 (or 4K)
   |
   +---> 16:9 export  (Twitter, LinkedIn, YouTube)
   |
   +---> 9:16 export  (TikTok, Reels, Shorts) -- center-crop or reframe
   |
   +---> 1:1 export   (fallback / carousel posts)
```

**For AI/tech content specifically (your use case):**

16:9 is the clear winner. Technical content involves screen recordings, code, diagrams, and slides -- all of which are inherently landscape. Twitter and LinkedIn (your primary platforms) both favor 16:9. If you also want to create vertical clips for short-form platforms, crop the most visually interesting portion.

### FFmpeg Aspect Ratio Conversion

**16:9 to 9:16 (center crop):**

```bash
ffmpeg -i input_16x9.mp4 \
  -vf "crop=ih*9/16:ih,scale=1080:1920" \
  -c:v libx264 -crf 20 -preset medium \
  -movflags +faststart -c:a aac -b:a 128k \
  output_9x16.mp4
```

**16:9 to 1:1 (center crop):**

```bash
ffmpeg -i input_16x9.mp4 \
  -vf "crop=ih:ih,scale=1080:1080" \
  -c:v libx264 -crf 20 -preset medium \
  -movflags +faststart -c:a aac -b:a 128k \
  output_1x1.mp4
```

**16:9 to 9:16 (letterbox with blur background):**

```bash
ffmpeg -i input_16x9.mp4 \
  -filter_complex "[0:v]scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:-1:-1:color=black[fg]; \
  [0:v]scale=1080:1920,boxblur=20:20[bg]; \
  [bg][fg]overlay=(W-w)/2:(H-h)/2" \
  -c:v libx264 -crf 20 -preset medium \
  -movflags +faststart -c:a aac -b:a 128k \
  output_blur_bg.mp4
```

---

## 6. Quick Reference Card

### Platform Specs at a Glance

| Platform | Max Size | Max Duration | Resolution | Codec | Aspect Ratio |
|----------|---------|-------------|-----------|-------|-------------|
| X (free) | 512 MB | 2:20 | 720p | H.264 + AAC | 16:9 |
| X (Premium+) | 16 GB | 4 hours | 1080p | H.264 + AAC | 16:9 |
| LinkedIn (organic) | 5 GB | 10-15 min | 1080p | H.264 + AAC | 16:9 or 4:5 |
| LinkedIn (ads) | 200 MB | 30 min | 1080p | H.264 + AAC | 16:9 or 4:5 |

### Universal Encode Command (copy-paste)

```bash
ffmpeg -i INPUT -c:v libx264 -preset medium -crf 18 -profile:v high -level 4.1 -pix_fmt yuv420p -movflags +faststart -c:a aac -b:a 192k OUTPUT.mp4
```

### API Upload Summary

| Platform | API Video Upload? | Upload Method | Key Barrier |
|----------|-------------------|---------------|-------------|
| X (Twitter) | Yes (v2 API) | Chunked INIT/APPEND/FINALIZE | Free tier: 500 posts/mo, ~34 video uploads/day |
| LinkedIn | Yes (Videos API) | Chunked with ETag tracking | Partner Program approval (weeks-months) |
| PostBridge | Yes | Signed URL upload | $5/mo add-on, simplest by far |

---

## Sources

- https://postfa.st/sizes/x/video
- https://postfa.st/sizes/linkedin/video
- https://postproxy.dev/blog/social-media-platform-api-rules-rate-limits-media-specs/
- https://postproxy.dev/blog/handling-image-and-video-uploads-across-social-media-apis/
- https://postproxy.dev/blog/x-twitter-api-posting-integration-guide/
- https://docs.x.com/x-api/media/finalize-media-upload
- https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/videos-api
- https://api.post-bridge.com/reference
- https://support.post-bridge.com/api
- https://toxigon.com/optimizing-ffmpeg-settings-for-h264-encoding
- https://compresto.app/blog/ffmpeg-compress-video
- https://vid-crush.com/blog/best-video-format-social-media/
- https://sproutsocial.com/insights/social-media-video-specs-guide/
