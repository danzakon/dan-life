# Life OS

A personal knowledge and task management system built on markdown files.

---

## Purpose

This repository is an operating system for managing life—work, content, research, and everything in between. Each directory serves a specific function and contains its own CLAUDE.md with context and rules.

---

## Directory Structure

```
life/
├── content/          # Social media content (AI engineering, tech, business)
├── tenex/            # Work scratchpad for Tenex (tech lead responsibilities)
├── research/         # Research notes and explorations
├── prompts/          # Prompt templates and experiments
├── shopping/         # Shopping lists and purchase tracking
└── CLAUDE.md         # This file
```

---

## The Scratchpad System

Most directories support a `.scratchpad/` subfolder for active working documents.

### File Naming Convention

```
{M-DD-YY}-{title}.md

Examples:
1-12-26-quarterly-planning.md
1-12-26-content-ideas.md
```

### Archival Rules

When `.scratchpad/` contains more than 15 files:
1. Move older files to `.scratchpad/.history/`
2. Keep the 15 most recent files in `.scratchpad/`
3. Files in `.history/` are retained indefinitely

```
directory/
├── .scratchpad/
│   ├── .history/          # Archived files (>15 in scratchpad)
│   │   └── 12-15-25-old-doc.md
│   ├── 1-10-26-recent.md
│   └── 1-12-26-current.md
└── CLAUDE.md
```

---

## Task Tracking

Use checkboxes to track progress throughout all documents:

```markdown
## Planning
- [ ] Draft quarterly objectives
- [ ] Review team capacity
- [x] Complete performance reviews
```

- `[ ]` — Planned / To do
- `[x]` — Completed

When working on documents, update checkboxes as tasks are completed. This provides a clear audit trail of progress.

---

## Conventions

### Writing Style
- Clear, concise prose
- No unnecessary ceremony
- Headings and structure over walls of text
- Tables and lists for comparisons

### File Organization
- One topic per file when possible
- Use descriptive titles in filenames
- Date prefix for scratchpad files only

### What Doesn't Belong Here
- Binary files (images, PDFs) — link to external storage instead
- Sensitive credentials — use a secrets manager
- Large datasets — reference, don't store

---

## Working With Claude

When navigating this repo:
1. Check the relevant directory's CLAUDE.md first for context
2. Respect the scratchpad/archive system
3. Update checkboxes as work progresses
4. Suggest CLAUDE.md updates when patterns evolve
