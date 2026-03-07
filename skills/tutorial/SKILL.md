---
name: tutorial
description: Research a topic and produce a practical, step-by-step technical guide.
  Use when asked to "write a tutorial", "create a guide for", "how do I", or
  "walk me through". Produces working guides, not opinion pieces.
argument-hint: "[topic or task to create a guide for]"
disable-model-invocation: false
allowed-tools:
  - Task
  - Read
  - Write
  - Glob
  - Grep
  - Bash
---

# Tutorial

Research a topic thoroughly and produce a practical, working technical guide on $ARGUMENTS.

This skill mirrors the `research` skill's process (Exa search, subagents, parallel investigation) but produces a different output: a step-by-step guide that someone can follow to completion, not an opinionated report.

---

## Folder Structure

```
tutorials/
├── .scratchpad/       # Sub-agent working notes and research
│   └── .history/      # Archived scratchpad files
└── guides/            # Finished, published tutorials
```

Save all intermediate work to `.scratchpad/`. Only finished, tested guides go into `guides/`.

---

## What Belongs Here

| Category | Examples |
|----------|----------|
| Setup guides | How to configure a tool or service end-to-end |
| Implementation guides | How to build a specific feature or system |
| Workflow guides | How to set up a repeatable process |
| Integration guides | How to connect two tools or services |
| Migration guides | How to move from X to Y |

**What does NOT belong here:**
- Opinion pieces (use `research`)
- Conceptual explainers with no actionable steps (use `research`)
- Tool comparisons without a recommended path (use `research`)

---

## Phase 1: Preliminary Research

Survey the landscape to understand what already exists:

1. Use `mcp__exa__web_search_exa` to find existing tutorials, docs, and guides on the topic
2. Use `mcp__exa__get_code_context_exa` for code examples, API documentation, and SDK usage
3. Identify the current best practices and common pitfalls
4. Note what existing guides get wrong or leave out
5. Find the official documentation for any tools involved

The goal: understand the territory well enough to write the best available guide, not just another one.

---

## Phase 2: Identify Guide Structure

Based on research, determine:

- **The end state:** What will the reader have when they're done?
- **Prerequisites:** What do they need before starting?
- **The critical path:** What are the minimum steps to get a working result?
- **Common pitfalls:** Where do people usually get stuck?
- **Decision points:** Where might the reader need to choose between approaches?

Draft an outline of numbered steps before proceeding. Keep it as short as possible while still being complete. Every step should produce a visible, testable result.

---

## Phase 3: Deep Research via Subagents

Spawn subagents to investigate specific areas in parallel using the Task tool:

```
subagent_type: "general-purpose"
```

Each subagent should investigate one specific aspect:
- Exact API calls or CLI commands needed (with current syntax)
- Version-specific gotchas and compatibility notes
- Error handling and edge cases
- Configuration options and what the recommended defaults are
- Real code examples from official docs or reputable sources

Save each subagent's output to `.scratchpad/`:

```
.scratchpad/
├── YYYY-MM-DD-{topic}-setup-research.md
├── YYYY-MM-DD-{topic}-api-research.md
└── YYYY-MM-DD-{topic}-deployment-research.md
```

---

## Phase 4: Synthesis and Guide Writing

### Philosophy

The goal is **practical and complete**. The reader should be able to follow the guide from start to finish without needing to consult other sources. Be:

- **Precise** — exact commands, exact file paths, exact config values
- **Honest about tradeoffs** — if there are multiple approaches, recommend one and explain why
- **Defensive** — anticipate where things go wrong and address it proactively
- **Tested** — every command and code snippet should actually work (verify against docs)
- **Opinionated about approach** — don't present three options without a recommendation

Do not:
- Leave steps vague ("configure your database" without showing how)
- Assume the reader knows which flags to use
- Skip error handling because the happy path is simpler to write
- Include unnecessary theory before getting to the practical steps

### Guide Structure

```markdown
# How to {Do the Thing}

**Date:** YYYY-MM-DD
**Category:** Tutorial
**Difficulty:** Beginner | Intermediate | Advanced
**Time estimate:** ~{N} minutes
**Prerequisites:** {what you need}

---

## What You'll Build / Learn

{One paragraph: the concrete end state. "By the end of this guide,
you'll have a working X that does Y."}

---

## Prerequisites

- {Tool} version {X}+ installed
  ```bash
  # Verify:
  tool --version
  ```
- {Account / API key} for {service}
  {How to get one if they don't have it}

---

## Step 1: {Verb phrase — e.g., "Set up the project"}

{Brief explanation of what this step accomplishes and why.}

```bash
{exact command}
```

{Expected output or how to verify it worked.}

---

## Step 2: {Next verb phrase}

...

---

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| {Error message or symptom} | {Why it happens} | {Exact fix} |

---

## What's Next

- {Natural extension or follow-up}
- {Related guide if one exists}

---

## Sources

- [{Official docs}](url)
- [{Reference implementation}](url)
```

### Writing Style

- **Commands over prose.** If you can show a command, show the command. Don't describe what to type when you can just type it.
- **Show expected output.** After commands that produce output, show what the reader should see. This is how they verify each step worked.
- **One thing per step.** Each step should do one thing and produce one verifiable result. Don't combine unrelated operations.
- **Name your files.** When creating files, always show the full filename and path. Never say "create a config file" without specifying where.
- **Version-pin when it matters.** If a specific version is required, say so. If any recent version works, say that too.

### Quality Bar

A good tutorial should:
- Be followable by someone who's never done this before (at the stated difficulty level)
- Produce a working result at the end, not just understanding
- Include exact commands that actually work (verified against current docs)
- Handle the 2–3 most common errors explicitly
- Take no longer than the stated time estimate
- Not require any knowledge beyond the stated prerequisites

---

## Pipeline Integration (Optional)

When a tutorial is complete and might be worth sharing as content:

1. Register in `content/pipeline/index.db` with source type `tutorial`:
   ```bash
   sqlite3 content/pipeline/index.db \
     "INSERT INTO items (id, created_at, source_type, ingest_source, status, current_title, raw_file)
      VALUES ('{ID}', '{datetime}', 'tutorial', 'tutorial', 'raw',
              '{title}', 'tutorials/guides/{filename}');"
   ```

2. Write an inbox entry with content angles:
   - Post: summarize the key technique in one post
   - Thread: walk through the most interesting step
   - Article: explore the "why" behind the approach

Not every tutorial needs to become content. Only register tutorials that have genuine content potential.

---

## Cleanup

Move stale `.scratchpad/` files to `.scratchpad/.history/` when the folder exceeds 15 files. Finished guides in `guides/` are permanent.
