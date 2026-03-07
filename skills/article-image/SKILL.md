---
name: article-image
description: Generate social media images for articles. Creates images optimized for
  X/Twitter cards and blog headers. Use when asked to "create article image",
  "generate header image", "make a social image", or "image for this article".
argument-hint: [article-title-or-path]
---

# Article Image Generator

Generate optimized images for articles and social media sharing.

## Image Specifications

### X/Twitter Summary Large Image Card (Primary)

```
┌─────────────────────────────────────────┐
│                                         │
│            1200 x 628 px                │
│          (1.91:1 aspect ratio)          │
│                                         │
│    Safe zone for text: center 80%       │
│                                         │
└─────────────────────────────────────────┘
```

| Property | Value |
|----------|-------|
| Dimensions | 1200 x 628 px |
| Aspect Ratio | 1.91:1 (Twitter OG card standard) |
| Format | PNG |
| Max File Size | 5MB |
| Min Dimensions | 800 x 418 px |

This is the standard Twitter/X OG card size. No cropping occurs — what you generate is exactly what displays.

### File Naming

```
{YYYY}-{MM}-{slug}-og.png

Example: 2026-01-moltbook-ai-social-network-og.png
```

## Workflow

### Step 1: Understand the Article

If given an article path, read it first to understand:
- Main topic and angle
- Key visual concepts
- Tone (serious, playful, provocative, etc.)
- Target audience

### Step 2: Design the Image Concept

Consider:
- **Visual metaphor**: What single image captures the article's essence?
- **Text overlay**: Keep minimal (title or key phrase only, if any)
- **Style**: Match the article's tone
- **Contrast**: Ensure readability when shrunk to thumbnail

### Step 3: Generate the Prompt

Create a detailed prompt for `mediagen` (or any image generator) that includes:

1. **Subject**: The main visual element
2. **Style**: Art style, mood, color palette
3. **Composition**: Where elements are placed
4. **Technical specs**: Dimensions, aspect ratio
5. **What to avoid**: Common AI image pitfalls

### Prompt Template

```
[SUBJECT DESCRIPTION]

Style: [ART STYLE - e.g., minimalist illustration, photorealistic, abstract, etc.]
Mood: [EMOTIONAL TONE - e.g., ominous, playful, professional, surreal]
Color palette: [PRIMARY COLORS]
Composition: [LAYOUT DESCRIPTION - e.g., centered subject, rule of thirds, etc.]

Technical requirements:
- Dimensions: 1200x628 pixels (1.91:1 aspect ratio, Twitter OG card)
- Leave space for potential text overlay in [TOP/BOTTOM/CENTER]
- High contrast for thumbnail visibility

Avoid: [SPECIFIC THINGS TO EXCLUDE - e.g., text, human faces, hands, etc.]
```

### Step 4: Generate and Save

Use `mediagen` to generate the image:

```bash
mediagen i:gen "{prompt}" \
  -o content/images/{YYYY}-{MM}-{slug}-og.png \
  --size 1792x1024
```

If `mediagen` is not installed or returns an error, output the full prompt for
manual generation in Gemini AI Studio, Midjourney, or DALL-E — and continue
with the rest of the article workflow.

## House Visual Style

All article images follow a consistent visual identity. This is what makes content recognizable across posts.

### The Style: Dark + Bold + Minimal

```
Background:  Dark (#0a0a0a to #1a1a2e gradient range)
Accent:      One strong color per image (varies by topic — see below)
Typography:  Not rendered in the image (X handles titles via cards)
Composition: Single strong visual element, generous negative space
Aesthetic:   Clean, editorial, data-viz inspired — not "AI art"
```

### Accent Color by Theme

| Content theme | Accent color | Hex |
|---------------|-------------|-----|
| AI / Engineering | Electric blue | `#64ffda` |
| Hot take / Opinion | Coral red | `#ff6b6b` |
| Practical / How-to | Amber | `#ffd93d` |
| Research / Analysis | Purple | `#a78bfa` |
| Tenex / Company | Teal | `#2dd4bf` |

### Style Rules

**Do:**
- Use bold, simple visuals that read at thumbnail size
- Create visual metaphors — abstract over literal
- Use negative space generously
- Match the article's intellectual weight
- Keep the dark background consistent across all images

**Don't:**
- Put text on the image (X renders title via the card)
- Use generic stock photo aesthetics
- Include human faces (AI faces look uncanny)
- Make it busy or cluttered
- Use the "Midjourney look" (over-rendered, hyper-detailed)
- Use bright or white backgrounds (breaks the visual identity)

## Examples

### Tech/AI Article

```
A stylized neural network rendered as a constellation map, with nodes glowing
in electric blue against a dark navy background. One node significantly brighter
than others, suggesting emergence or awakening.

Style: Minimalist data visualization aesthetic
Mood: Mysterious, slightly ominous
Color palette: Navy blue (#0a192f), electric blue (#64ffda), white accents
Composition: Central focal point with radiating connections

Technical requirements:
- Dimensions: 1200x628 pixels (1.91:1 aspect ratio, Twitter OG card)
- Leave bottom third relatively clean for potential text overlay
- High contrast for thumbnail visibility

Avoid: Literal robot imagery, generic "tech" backgrounds, human faces
```

### Opinion/Commentary Article

```
Two speech bubbles facing each other, one human-shaped and one geometric/digital,
with the space between them filled with static or interference patterns.

Style: Bold graphic design, almost poster-like
Mood: Tense, thought-provoking
Color palette: Black, white, one accent color (coral #FF6B6B)
Composition: Symmetrical, centered

Technical requirements:
- Dimensions: 1200x628 pixels (1.91:1 aspect ratio, Twitter OG card)
- Central negative space for visual breathing room
- Strong silhouettes for thumbnail clarity

Avoid: Literal depictions, busy backgrounds, gradients
```

## CLI Tool Usage

All image generation goes through the `mediagen` CLI:

| Command | Purpose |
|---------|---------|
| `mediagen i:gen "prompt" -o path.png --size 1792x1024` | Create new image |
| `mediagen i:edit existing.png "edit prompt" -o path.png` | Modify existing image |
| `mediagen providers` | Check which providers are configured |

If `mediagen` is not installed or no API keys are available, output the prompt
for manual use in Gemini AI Studio, Midjourney, or DALL-E.

## Output

Always provide all three artifacts:

1. **Image file** saved to `content/images/{YYYY}-{MM}-{slug}-og.png`
2. **Prompt file** saved to `content/images/prompts/{YYYY}-{MM}-{slug}-prompt.md` with the full generation prompt for reproducibility
3. **Alt text** suggested for accessibility

### Prompt File Format

```markdown
# Image Prompt: {Article Title}

**Article:** content/articles/drafts/{filename}
**Generated:** YYYY-MM-DD
**Tool:** mediagen [{provider}/{model}]
**Theme accent:** {color name} ({hex})

## Prompt

{The exact prompt used to generate the image}

## Alt Text

{Suggested alt text for the image}

## Notes

{Any iteration notes — what was tried, what worked}
```

This file is the reproducibility record. If the image needs to be regenerated (e.g., after a style update), the prompt is right here.
