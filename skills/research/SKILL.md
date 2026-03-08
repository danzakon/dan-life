---
name: research
description: Research a topic thoroughly and produce an opinionated, well-sourced report. Use when asked to research, investigate, or produce a report on any topic.
disable-model-invocation: false
allowed-tools:
  - Task
  - Read
  - Write
  - Glob
  - Grep
  - Bash
---

# Research

Conduct thorough, opinionated research and produce a written report on $ARGUMENTS.

---

## Folder Structure

The default research folder is `research/` in the life repo. Use this layout — create directories if they don't exist:

```
research/
├── .scratchpad/       # Sub-agent working notes and sub-reports
│   └── .history/      # Archived / stale research
└── reports/           # Final published reports only
```

Save all intermediate work to `.scratchpad/`. Only finished, synthesis-complete reports go into `reports/`.

### File Naming Convention

All files use a `YYYYMMDD` date prefix for chronological sorting:

```
reports/{YYYYMMDD}-{slug}.md           # e.g. 20260308-agentic-sdlc-leverage.md
.scratchpad/{YYYYMMDD}-{slug}.md       # e.g. 20260308-mobile-agent-ui-findings.md
```

This matches the date-prefix convention used across the content pipeline. Never omit the date prefix.

---

## What Belongs Here

| Category | Examples |
|----------|----------|
| Technical deep dives | Framework comparisons, architecture patterns |
| Tool evaluations | New tools, libraries, services |
| Industry research | Market trends, competitor analysis |
| Learning notes | Course notes, book summaries |
| Explorations | "What if" investigations, proof of concepts |

---

## Phase 1: Preliminary Research

Before diving deep, get the lay of the land:

1. Use `mcp__exa__web_search_exa` to survey the topic broadly
2. Identify key players, recent developments, and the current state of discourse
3. Note what's well-covered vs. underexplored
4. Flag areas of controversy or disagreement

This phase builds a mental map before committing to specific angles.

**Source-Specific Tools:**

| Source | Tool |
|--------|------|
| Web (default) | `mcp__exa__web_search_exa` |
| X/Twitter | `/xquery` skill — use when explicitly asked |

When instructed to use X/Twitter for sources, invoke the xquery skill:
- `xquery "topic"` — Ask Grok with live X search (interpreted answer)
- `xquery x:search "topic"` — Get raw tweets with metrics
- `xquery x:user @handle` — Get user info and recent tweets

---

## Phase 2: Identify Research Angles

Based on preliminary findings, generate 3–5 interesting angles:

- What questions remain unanswered?
- Where is conventional wisdom potentially wrong?
- What connections aren't being made?
- What predictions can be tested?
- What would be genuinely novel to explore?

Choose angles that will produce insights, not just summaries.

---

## Phase 3: Deep Research via Subagents

Spawn subagents to research each angle in parallel using the Task tool:

```
subagent_type: "general-purpose"
```

Each subagent should:
- Investigate one specific angle
- Use `mcp__exa__web_search_exa` extensively
- Find primary sources, data, and expert opinions
- Follow interesting tangents when warranted
- Return raw findings, not polished prose

Save each subagent's output as a markdown file in `.scratchpad/`:

```
.scratchpad/
├── angle-1-{slug}.md
├── angle-2-{slug}.md
└── angle-3-{slug}.md
```

---

## Phase 4: Synthesis and Report Writing

### Philosophy

The goal is **truth and signal**, not appeasement. Be:

- **Critical** — challenge assumptions, call out flaws, identify failures
- **Opinionated** — take stances based on evidence, don't hedge everything
- **Predictive** — extrapolate from data, make forecasts, stake claims
- **Novel** — find insights others miss, make unexpected connections
- **Brash when warranted** — if something is bad, say it's bad; if overhyped, call it out

Do not:
- Regurgitate information without analysis
- Equivocate to avoid offending anyone
- Present "both sides" when one side is clearly stronger
- Hide behind weasel words and excessive caveats

The reader wants to know what you actually think based on the evidence.

### Report Structure

```markdown
---
id: {YYYYMMDD-RS-NNN}
date: YYYY-MM-DD
category: Research Report
content-status: raw
---

# {Topic}: {Opinionated Subtitle}

---

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [Background](#background)
3. [Section 1](#section-1)
4. [Section 2](#section-2)
...
5. [Key Takeaways](#key-takeaways)
6. [Predictions](#predictions)

---

## Executive Summary

{2-3 paragraphs with the major findings and your strongest takes.
Lead with insight, not throat-clearing.}

---

## Background

{Explain the topic clearly for someone with no prior knowledge.
Define terms. Establish context. Make it accessible.}

---

## {Sections by Research Angle}

{Each major section explores one angle in depth.
Use inline citations: "According to [Source Name](url), ..."
Include data, quotes, and evidence.
End each section with your interpretation.}

---

## Key Takeaways

{Numbered list of major opinionated conclusions.
These should be bold, defensible, and memorable.
Not "X is interesting" but "X will dominate Y within 2 years."}

---

## Predictions

{Specific, falsifiable predictions with reasoning.
Stake a claim. Be willing to be wrong.}
```

### Citation Style

Use inline citations throughout — no footnotes or endnotes:
- "The market grew 40% YoY according to [Industry Report 2025](url)"
- "[Expert Name](url) argues that..."
- "Data from [Source](url) shows..."

Keep sources visible at the point where claims are made.

### Quality Bar

A good research report should:
- Teach something genuinely new
- Take positions others would debate
- Be understandable to an intelligent layperson
- Include at least one insight the reader couldn't find elsewhere
- Make predictions or recommendations that have real stakes

---

## Phase 5: Pipeline Integration

After the report is written and saved, register it in the content pipeline so it can be converted to posts, threads, or articles.

### Step 1: Assign ID

```bash
sqlite3 content/pipeline/index.db \
  "SELECT id FROM items WHERE id LIKE '$(date +%Y%m%d)-RS-%' ORDER BY id DESC LIMIT 1;"
```

Increment NNN (start at 001 if no results). Add the `id` to the report's YAML frontmatter.

### Step 2: Register in index.db

```bash
sqlite3 content/pipeline/index.db \
  "INSERT INTO items (id, created_at, source_type, ingest_source, status, current_title, raw_file)
   VALUES ('{ID}', '{datetime}', 'research', 'research', 'raw',
           '{report title}', 'research/reports/{YYYYMMDD}-{slug}.md');"
```

### Step 3: Write inbox entry

Add an entry to `content/inbox/YYYY-MM-DD.md` with:
- Executive summary (pulled from the report's Summary section)
- Content angles:
  - **Thread**: Key findings distilled into a tweetstorm
  - **Article**: Full editorial treatment of the report
  - **Hot take**: One sharp opinion extracted from the findings
  - **Post**: Single strongest takeaway as a standalone post
- Content tree — develop all applicable formats now

### Step 4: Update _index.md

Add a row to the Item Registry in `content/inbox/_index.md`.

### Step 5: Notify

```
Research report saved: research/reports/{YYYYMMDD}-{slug}.md
Registered in pipeline as {ID}.
Ready for /content-interview to convert to content.
```

---

## Scratchpad File Format

Sub-reports saved in `.scratchpad/` should use this format:

```markdown
# {Topic}

**Category:** Technical | Tool | Industry | Learning | Exploration
**Date Started:** {YYYY-MM-DD}
**Status:** [ ] Active | [ ] Paused | [x] Complete

---

## Summary
{One paragraph overview}

## Key Findings
- Finding 1
- Finding 2

## Details
{Deeper content}

## Sources
- [Link 1](url)
- [Link 2](url)

## Next Steps
- [ ] Follow-up action
```

---

## Cleanup

Move stale `.scratchpad/` files to `.scratchpad/.history/` during periodic cleanup. Final reports in `reports/` are permanent and should not be archived.
