---
name: article-thumbnail
description: Generate a thumbnail/header image for an article. Creates 1200x675
  images optimized for X/Twitter cards. Use when asked to "generate thumbnail",
  "create article image", "make a header image", or "image for this article".
argument-hint: "[article path or title]"
---

# Article Thumbnail Generator

Generate optimized thumbnail/header images for articles and social media sharing.

## Image Specifications

| Property | Value |
|----------|-------|
| Dimensions | 1200 x 675 px |
| Aspect Ratio | 16:9 |
| Format | PNG or JPG |
| Max File Size | 5MB |
| Min Dimensions | 800 x 418 px |

### File Naming

```
{YYYY}-{MM}-{slug}-og.png

Example: 2026-02-responsible-for-your-own-slop-og.png
```

## Workflow

### Step 1: Understand the Article

If given an article path, read it. Understand:

- Main topic and angle
- Key visual concepts or metaphors
- Tone (serious, playful, provocative, technical)
- The one-sentence perspective (from frontmatter if available)

### Step 2: Design the Concept

Consider:

- **Visual metaphor**: What single image captures the article's essence?
- **Text overlay**: Minimal (title or key phrase only, if any)
- **Style**: Match the article's tone
- **Contrast**: Must read well when shrunk to thumbnail size

### Step 3: Generate the Prompt

Create a detailed image generation prompt:

```
[SUBJECT DESCRIPTION]

Style: [art style - minimalist illustration, photorealistic, abstract, etc.]
Mood: [emotional tone - ominous, playful, professional, surreal]
Color palette: [primary colors]
Composition: [layout - centered, rule of thirds, etc.]

Technical requirements:
- Dimensions: 1200x675 pixels (16:9 aspect ratio)
- Leave space for potential text overlay in [TOP/BOTTOM/CENTER]
- High contrast for thumbnail visibility

Avoid: [specific exclusions - text, human faces, hands, etc.]
```

### Step 4: Save the Prompt

Save the prompt to `content/images/prompts/{YYYY}-{MM}-{slug}-prompt.md` for future reference and iteration.

### Step 5: Generate and Save

Use available image generation tools (GenerateImage tool, Nano-Banana MCP, or similar).

Save the image to: `content/images/{YYYY}-{MM}-{slug}-og.png`

### Step 6: Update Article Frontmatter

Add the thumbnail path to the article's frontmatter:

```yaml
thumbnail: images/{YYYY}-{MM}-{slug}-og.png
```

## Style Guidelines

### Do

- Bold, simple visuals that read at small sizes
- Visual metaphors that intrigue
- Negative space
- Strong silhouettes for thumbnail clarity

### Don't

- Too much text on the image
- Generic stock photo aesthetics
- Human faces (AI faces look uncanny)
- Busy, cluttered compositions
- Cliche AI art styles ("the Midjourney look")

## Output

Provide:

1. The generated image saved to `content/images/`
2. The prompt saved to `content/images/prompts/`
3. Suggested alt text for accessibility
4. Confirmation that article frontmatter was updated
