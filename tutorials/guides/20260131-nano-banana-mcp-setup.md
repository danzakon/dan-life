# Nano-Banana MCP Setup for Claude Code

Set up AI image generation directly in Claude Code using the Nano-Banana MCP server.

---

## Overview

Nano-Banana is an MCP server that connects Claude Code to Google's Gemini 2.5 Flash Image API, enabling image generation and editing without leaving your terminal.

```
┌─────────────────────────────────────────────────────────────┐
│                      CLAUDE CODE                             │
│                                                              │
│   "Generate an image of..."                                  │
│              │                                               │
│              ▼                                               │
│   ┌─────────────────────┐                                    │
│   │  Nano-Banana MCP    │                                    │
│   │  (local server)     │                                    │
│   └──────────┬──────────┘                                    │
│              │                                               │
│              ▼                                               │
│   ┌─────────────────────┐     ┌─────────────────────┐       │
│   │  Gemini 2.5 Flash   │────▶│  Generated Image    │       │
│   │  Image API          │     │  (saved locally)    │       │
│   └─────────────────────┘     └─────────────────────┘       │
└─────────────────────────────────────────────────────────────┘
```

---

## Prerequisites

- [ ] Node.js 18+ installed
- [ ] Google Cloud account with Gemini API access
- [ ] Gemini API key

---

## Step 1: Get a Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/apikey)
2. Click "Create API Key"
3. Copy the key (starts with `AIza...`)

---

## Step 2: Install Nano-Banana MCP

Two options:

### Option A: Global Installation (Recommended)

Add to your global Claude config at `~/.claude.json`:

```json
{
  "mcpServers": {
    "nano-banana": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@helios123/nano-banana-mcp"],
      "env": {
        "GEMINI_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

| Part | Meaning |
|------|---------|
| `type: stdio` | Server communicates via standard input/output |
| `command: npx` | Use npx to run the package |
| `-y` | Auto-confirm npx prompts |
| `@helios123/nano-banana-mcp` | The package to run |
| `GEMINI_API_KEY` | Your API key passed as environment variable |

### Option B: Project-Local Installation

Create `.mcp.json` in your project root:

```json
{
  "mcpServers": {
    "nano-banana": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@helios123/nano-banana-mcp"],
      "env": {
        "GEMINI_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

---

## Step 3: Verify Installation

Restart Claude Code, then run:

```
/mcp
```

You should see `nano-banana` listed with these tools:
- `generate_image` - Create images from text prompts
- `edit_image` - Modify existing images
- `iterate_image` - Refine the last generated image

---

## Available Tools

### generate_image

Create a new image from a text prompt.

```
Parameters:
- prompt (required): Text description of the image
- width (optional): Image width in pixels (default: 1024)
- height (optional): Image height in pixels (default: 1024)
- output_path (optional): Where to save the image
```

### edit_image

Modify an existing image with a text prompt.

```
Parameters:
- image_path (required): Path to the image to edit
- prompt (required): Description of the edit to make
- output_path (optional): Where to save the result
```

### iterate_image

Refine the last generated or edited image.

```
Parameters:
- prompt (required): Description of refinements to make
```

---

## Usage Examples

### Basic Generation

```
Generate an image: A minimalist illustration of interconnected nodes
forming a social network, with one node glowing brighter than the others.
Electric blue on dark navy background. 1200x675 pixels.
```

### Iterative Refinement

```
1. Generate initial image
2. "Make the glowing node more prominent"
3. "Add subtle connection lines between nodes"
4. "Increase contrast for better thumbnail visibility"
```

### Editing Existing Images

```
Edit the image at content/images/header.png:
Add a subtle vignette effect and increase saturation slightly.
```

---

## Best Practices

### Prompting Tips

| Do | Don't |
|----|-------|
| Be specific about style | Use vague terms like "cool" or "nice" |
| Specify dimensions | Assume default sizes work |
| Describe composition | Just describe the subject |
| Mention what to avoid | Hope it doesn't add unwanted elements |

### File Management

- Save images to organized directories
- Use descriptive filenames with dates
- Keep prompts documented for iteration

---

## Troubleshooting

### "API key not found"

Ensure `GEMINI_API_KEY` is set in the MCP config, not as a system environment variable.

### "Server not responding"

1. Check Node.js version: `node --version` (need 18+)
2. Try running directly: `npx @anthropic/nano-banana-mcp`
3. Check for firewall blocking the Gemini API

### "Image generation failed"

- Simplify the prompt
- Check API quota at [Google AI Studio](https://aistudio.google.com/)
- Try a smaller image size first

---

## Security Notes

- Never commit API keys to version control
- Consider using environment variables from a `.env` file
- API keys can be rotated at Google AI Studio if compromised

---

## Cost

Gemini 2.5 Flash Image API pricing (as of Jan 2026):
- ~$0.02 per image generation
- Free tier available with limits

Check current pricing: https://ai.google.dev/pricing

---

## Related

- [Claude Skills Setup Guide](claude-skills-setup-guide.md) - For creating skills that use image generation
- [Article Image Skill](~/.claude/skills/article-image/SKILL.md) - Pre-built skill for generating article images
