# Prompts

Prompt templates, experiments, and proven patterns for working with LLMs.

---

## Purpose

A library of prompts that work well, experiments with new techniques, and templates for common tasks. Building a personal prompt engineering toolkit.

---

## Structure

```
prompts/
├── .scratchpad/           # Prompt experiments and drafts
│   └── .history/          # Archived experiments
├── templates/             # Proven, reusable prompts
├── techniques/            # Prompt engineering patterns
└── CLAUDE.md
```

---

## What Belongs Here

| Category | Examples |
|----------|----------|
| Templates | Code review prompts, writing assistants, analysis frameworks |
| Techniques | Chain of thought patterns, few-shot examples, system prompts |
| Experiments | Testing new approaches, A/B comparisons |
| Failures | What didn't work and why (learning from mistakes) |

---

## File Format

```markdown
# {Prompt Name}

**Purpose:** {What this prompt does}
**Model:** {Best model for this prompt, if specific}
**Status:** [ ] Experimental | [x] Proven

---

## Prompt

```
{The actual prompt text}
```

## Usage Notes
- When to use this
- Variables to customize
- Tips for best results

## Examples
{Example inputs and outputs if helpful}

## Iterations
- v1: {date} - Initial version
- v2: {date} - {What changed and why}
```

---

## Guidelines

- Test prompts before marking as "Proven"
- Document what works and what doesn't
- Note which models work best for each prompt
- Keep templates generic and customizable
- Version your iterations to track improvements
