# Tutorials

Practical, step-by-step technical guides. Where `research/` produces opinionated reports, `tutorials/` produces working guides that teach how to do something.

---

## Purpose

Create the most practical, usable technical guides possible. A tutorial succeeds when someone can follow it start to finish and have a working result. Not thought leadership. Not opinion. Just "here's how to do the thing."

---

## Structure

```
tutorials/
├── CLAUDE.md              # This file
├── .scratchpad/            # Active research + drafts for tutorials
│   └── .history/           # Archived scratchpad files
└── guides/                 # Finished, published tutorials
```

---

## Guide File Format

```markdown
# {How to Do X}

**Date:** YYYY-MM-DD
**Category:** Tutorial
**Difficulty:** Beginner | Intermediate | Advanced
**Time estimate:** ~{N} minutes
**Prerequisites:** {what you need before starting}

---

## What You'll Build / Learn

{One paragraph: what the reader will have at the end.}

---

## Prerequisites

- {Tool 1} installed (version X+)
- {Account / API key} for {service}

---

## Steps

### Step 1: {Verb phrase}

{Explanation of what and why.}

```bash
{exact command or code}
```

{Expected output or result.}

### Step 2: ...

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| {Common issue} | {Fix} |

---

## What's Next

- {Follow-up tutorial or extension}
- {Related resources}

---

## Sources

- [Link](url)
```

---

## Naming Convention

```
guides/{YYYY}-{MM}-{slug}.md

Examples:
2026-03-deploy-fastify-to-cloud-run.md
2026-03-youtube-transcript-pipeline.md
```

---

## Scratchpad

`.scratchpad/` holds sub-agent research, raw notes, and draft tutorials. Move files to `.history/` during cleanup. Archival threshold: 15 files.

---

## Pipeline Integration

Tutorials can be content sources. When a tutorial is complete, it may warrant posts or articles:
- A post summarizing the key technique
- An article exploring the "why" behind the approach
- A thread walking through the most interesting step

The `tutorial` skill handles pipeline registration on completion.
