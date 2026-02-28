---
name: research-to-article
description: Convert a research report into a long-form article draft for X Articles.
  Use when asked to "turn this into an article", "write an article from this research",
  or "draft an article about".
argument-hint: "[path to research report or topic]"
---

# Research to Article

Convert a research report into a long-form article draft. Research explores. Articles argue.

## Inputs

1. A research report from `research/curiosity-reports/` or `research/.scratchpad/`
2. `content/CLAUDE.md` for tone/voice rules, anti-AI patterns, and the research-to-article pipeline docs
3. `content/pipeline/strategy.md` for current content emphasis

## The Core Principle

A research report is comprehensive and exploratory. An article needs a **singular perspective** -- a clear throughline that everything else supports. Multiple angles, examples, and sections all contribute to the main narrative, reinforcing it from different directions.

Think of it like a legal case: one argument, many pieces of evidence.

## Process

### Step 1: Find the Narrative

Read the full research report. Ask:

- What's the single most interesting conclusion?
- What would make someone stop and think "I didn't know that" or "I disagree"?
- What's the throughline that ties the best parts together?
- Can you state the article's perspective in one sentence?

Write down the one-sentence perspective before proceeding.

### Step 2: Structure the Article

Build a structure where every section serves the throughline:

```
1. Opening hook (get to the point fast, no throat-clearing)
2. The perspective stated clearly
3. Evidence/sections supporting the perspective from different angles
4. Nuance or counterarguments (acknowledged honestly, not dismissed)
5. What this means going forward / implications
```

Cut anything from the research that doesn't serve the article's argument, no matter how interesting. Save those for separate posts instead.

### Step 3: Write the Draft

Follow `content/CLAUDE.md` writing standards rigorously:

**Sentence rhythm**: Mix short punchy sentences with longer ones. Read aloud.

**Personal voice**: Use "I" when you have experience. Include specifics. Have opinions.

**Anti-AI patterns**: 
- Minimal em-dashes (use periods, commas, "but")
- No "it's not X, it's Y" constructions
- No banned vocabulary (delve, landscape, leverage, tapestry, realm, etc.)
- No "In today's..." openings
- No throat-clearing paragraphs
- Vary paragraph length

**Be specific**: Not "teams struggle with X" but "I watched three teams struggle with X last year."

### Step 4: Create the File

Save to `content/articles/drafts/` with proper frontmatter:

```yaml
---
title: {Article Title}
status: draft
platform: x-article
thumbnail: pending
perspective: "{one-sentence perspective}"
source: research/{report-filename}
---
```

Naming: `{YYYY}-{MM}-{slug}.md`

### Step 5: Suggest Thumbnail Concept

After writing, suggest 1-2 image concepts for the article thumbnail. Don't generate the image yet -- just describe the visual concept so the user can invoke `article-thumbnail` when ready.

### Step 6: Suggest Post Excerpts

Identify 2-3 sections of the article that could be extracted as standalone posts to promote the article. Note these at the bottom of the draft:

```markdown
---

## Post Excerpts (for promotion)

1. {excerpt idea 1}
2. {excerpt idea 2}
```

## Quality Gate

Before finishing the draft:

1. State the perspective in one sentence. Do all sections support it?
2. Read the opening. Does it hook within 2 sentences?
3. Search for em-dashes. Can most be replaced?
4. Search for AI vocabulary. Replace offenders.
5. Read a random paragraph aloud. Sound like a person?
6. Is there at least one thing a reader couldn't find elsewhere?
7. Does the article take a stance someone might push back on?

If it passes, mark the draft as ready for review.
