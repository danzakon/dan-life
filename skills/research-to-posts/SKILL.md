---
name: research-to-posts
description: Convert a research report into 5-10 short-form posts with platform-specific
  variants for Twitter and LinkedIn. Use when asked to "turn this research into posts",
  "make posts from this report", or "extract posts from research".
argument-hint: "[path to research report or topic]"
---

# Research to Posts

Convert a research report into 5-10 short-form, platform-targeted posts. The goal is extracting the most compelling insights and packaging them for social media engagement.

## Inputs

1. A research report from `research/curiosity-reports/` or `research/.scratchpad/`
2. `content/CLAUDE.md` for tone/voice rules and anti-AI writing patterns
3. `content/pipeline/strategy.md` for current content emphasis and hot topics

## Process

### Step 1: Read the Report

Read the full research report. Identify:

- The 5-10 most compelling individual insights, findings, or takes
- Surprising data points or statistics
- Contrarian conclusions that challenge conventional wisdom
- Actionable takeaways
- Predictions or forward-looking claims

Prioritize insights that are **hard to find elsewhere** -- this is the value-add of research synthesis.

### Step 2: Read Voice and Strategy

Read `content/CLAUDE.md` for:
- Tone principles (sound like a person, have opinions, be specific)
- Anti-AI writing patterns to avoid (em-dashes, contrast cliches, banned vocabulary)
- Sentence rhythm guidelines

Read `content/pipeline/strategy.md` for:
- Current hot topics (align posts with what's top-of-mind)
- Platform tone differences (Twitter vs LinkedIn)

### Step 3: Generate Posts

For each insight, create a post with **Twitter and LinkedIn variants**:

**Twitter variant:**
- 280 chars max (or thread format if the idea needs it)
- Punchy, direct, personality-forward
- Hot take framing when appropriate
- No hashtag spam (1-2 max if relevant)

**LinkedIn variant:**
- 500-1500 chars (LinkedIn rewards longer posts)
- More context and framing
- Professional but human tone
- Can include "here's what this means" explanation
- Structure with line breaks for readability

### Step 4: Write to Weekly File

Write all posts to the current week's file:

```
content/posts/W{week}-{month}-{year}.md
```

Create the file if it doesn't exist. Use the format from `content/CLAUDE.md`:

```markdown
## [ ] {Post title/hook}

**Platform:** Both
**Source:** research/{report-filename}

**Twitter:**
{Twitter-length content}

**LinkedIn:**
{LinkedIn-length content}

---
```

### Step 5: Tag Source

Add a reference to each post indicating which research report it came from. This enables traceability and prevents re-extracting the same insights later.

## Quality Standards

Before finalizing each post:

1. **Read it aloud.** Does it sound like a person talking? Or a press release?
2. **Check for AI tells.** Search for em-dashes, "it's not X, it's Y", banned vocabulary (delve, landscape, leverage, etc.)
3. **Does it have an opinion?** Wishy-washy content gets scrolled past.
4. **Is it specific?** Vague advice is forgettable. Include numbers, examples, concrete details.
5. **Would someone share this?** The best test: would this make someone tag a friend or hit repost?

## Output

Report what was generated:

- Number of posts created
- Which weekly file they're in
- Brief summary of each post's angle
- Suggestion for which ones to prioritize for the queue
