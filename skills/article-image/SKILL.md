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
│            1200 x 675 px                │
│           (16:9 aspect ratio)           │
│                                         │
│    Safe zone for text: center 80%       │
│                                         │
└─────────────────────────────────────────┘
```

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

Create a detailed prompt for Nano-Banana (or similar image generator) that includes:

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
- Dimensions: 1200x675 pixels (16:9 aspect ratio)
- Leave space for potential text overlay in [TOP/BOTTOM/CENTER]
- High contrast for thumbnail visibility

Avoid: [SPECIFIC THINGS TO EXCLUDE - e.g., text, human faces, hands, etc.]
```

### Step 4: Generate and Save

Use Nano-Banana MCP tools to generate:

```
mcp__nano-banana__generate_image with the prompt
```

Save to: `/Users/danzakon/dev/life/content/images/`

## Style Guidelines

### Do

- Use bold, simple visuals that read well at small sizes
- Create visual metaphors that intrigue
- Match the article's intellectual level
- Use negative space effectively
- Make it shareable (would someone retweet this?)

### Don't

- Put too much text on the image (title only if needed)
- Use generic stock photo aesthetics
- Include human faces unless essential (AI faces look uncanny)
- Make it too busy or cluttered
- Use cliche AI art styles (the "Midjourney look")

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
- Dimensions: 1200x675 pixels (16:9 aspect ratio)
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
- Dimensions: 1200x675 pixels (16:9 aspect ratio)
- Central negative space for visual breathing room
- Strong silhouettes for thumbnail clarity

Avoid: Literal depictions, busy backgrounds, gradients
```

## MCP Tool Usage

When Nano-Banana MCP is available, use these tools:

| Tool | Purpose |
|------|---------|
| `generate_image` | Create new image from prompt |
| `edit_image` | Modify existing image |
| `iterate_image` | Refine last generated image |

If MCP is not available, output the prompt for manual use in:
- Google Gemini (nano-banana backend)
- Midjourney
- DALL-E
- Other image generators

## Output

Always provide:
1. The image file saved to `/Users/danzakon/dev/life/content/images/`
2. The prompt used (for future reference/iteration)
3. Suggested alt text for accessibility
