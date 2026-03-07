---
name: mediagen
description: Generate AI images and videos from the command line using multiple providers
  (OpenAI GPT-Image, Google Imagen 4, Sora 2, Veo 3.1, Kling, SeedDance, Runway,
  MiniMax). Use when asked to generate, create, or edit images or videos via AI.
argument-hint: "[i:gen|i:edit|v:gen|v:status|providers|models] [args...]"
allowed-tools:
  - Bash
---

# mediagen

CLI tool for AI image and video generation. Provider-agnostic with graceful
degradation when keys are missing.

## Config

`~/.config/mediagen/.env`

```
OPENAI_API_KEY=...           # GPT-Image-1.5 (image) + Sora 2 (video)
GEMINI_API_KEY=...           # Imagen 4 / Gemini 2.0 Flash (image) + Veo 3.1 (video)
KLING_API_KEY=...            # Kling 3.0 (video, via piapi.ai)
SEEDANCE_API_KEY=...         # SeedDance 2.0 (video)
RUNWAY_API_KEY=...           # Runway Gen-4.5 (video)
MINIMAX_API_KEY=...          # MiniMax Hailuo 2.3 (video)

DEFAULT_IMAGE_PROVIDER=openai
DEFAULT_IMAGE_MODEL=gpt-image-1.5
DEFAULT_VIDEO_PROVIDER=google
DEFAULT_VIDEO_MODEL=veo-3.1-generate-001
```

## Commands

### Image generation

```bash
# Generate an image
mediagen i:gen "prompt" -o content/images/2026-03-slug-og.png

# With explicit provider and size
mediagen i:gen "prompt" \
  -o content/images/2026-03-slug-og.png \
  --size 1792x1024 \
  --quality high \
  --provider openai \
  --model gpt-image-1.5

# Google Imagen 4 (fast, cost-effective)
mediagen i:gen "prompt" -o output.png \
  --provider google \
  --model imagen-4.0-fast-generate-001

# Edit an existing image
mediagen i:edit image.png "make the background darker" -o output.png

# JSON output (for scripting)
mediagen --json i:gen "prompt" -o output.png
```

### Video generation

```bash
# Generate video (blocks until complete, ~2-10 minutes)
mediagen v:gen "prompt" -o clip.mp4 --duration 8

# Submit only, download later
mediagen v:gen "prompt" -o clip.mp4 --no-wait
# → prints: Task submitted: operations/abc123  [provider: google]

# Download previously submitted video
mediagen v:status operations/abc123 -o clip.mp4 --provider google

# Kling for cinematic motion
mediagen v:gen "prompt" -o clip.mp4 \
  --provider kling \
  --model kling-3.0 \
  --duration 5 \
  --aspect-ratio 16:9
```

### Discovery

```bash
mediagen providers   # Table of all providers + configured status
mediagen models      # Table of all models per provider
```

## Article Image Defaults

For article social images (used by the `article-image` skill):

```bash
mediagen i:gen "{detailed prompt}" \
  -o content/images/{YYYY}-{MM}-{slug}-og.png \
  --size 1792x1024 \
  --quality high
```

**Preferred style:** dark background (#0a0a0a–#1a1a2e), bold minimal
composition, single strong visual element. No text in image. High contrast
for thumbnail legibility.

**Default provider:** OpenAI (gpt-image-1.5) for quality; Google Imagen 4
Fast as cost-effective alternative.

## Provider Summary

| Provider | Images | Videos | Key var |
|----------|--------|--------|---------|
| openai | gpt-image-1.5, gpt-image-1, gpt-image-1-mini, dall-e-3 | sora-2, sora-2-pro | OPENAI_API_KEY |
| google | imagen-4.0-generate-001, -ultra, -fast; gemini-2.0-flash-exp | veo-3.1-generate-001, -preview | GEMINI_API_KEY |
| kling | — | kling-3.0, kling-2.6 | KLING_API_KEY |
| seedance | — | seedance-2.0 | SEEDANCE_API_KEY |
| runway | — | gen-4.5, gen-4, gen-3-alpha | RUNWAY_API_KEY |
| minimax | — | hailuo-2.3, hailuo-02 | MINIMAX_API_KEY |

## Fallback

If mediagen is not installed or errors, output the full prompt for manual
use in Google Gemini (Imagen), OpenAI DALL-E, or Midjourney.

## Installation

```bash
chmod +x skills/mediagen/scripts/mediagen
ln -sf $(realpath skills/mediagen/scripts/mediagen) ~/.local/bin/mediagen
bash skills/sync.sh
```
