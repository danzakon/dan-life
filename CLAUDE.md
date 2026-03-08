# Life OS

A personal knowledge and task management system built on markdown files.

---

## Purpose

This repository is an operating system for managing life—work, content, research, and everything in between. Each directory serves a specific function and contains its own CLAUDE.md with context and rules.

---

## Directory Structure

```
life/
├── content/           # Social media content (AI engineering, tech, business)
├── skills/            # Agent skill definitions, symlinked to all agent dirs
├── tutorials/         # Step-by-step technical guides: tutorial skill output + personal setup guides
├── research/          # Research reports and explorations (output of research skill)
├── tenex/             # Engineering leadership and process development
├── prompts/           # Prompt templates and experiments
├── shopping/          # Shopping lists and purchase tracking
├── private/           # Personal/sensitive files (gitignored, never accessed)
└── CLAUDE.md          # This file
```

Each directory has its own CLAUDE.md with conventions and context. Check it before working in any directory.

---

## Skills System

`skills/` is the source of truth for all agent skills. Skills are symlinked from here to `~/.claude/skills/`, `~/.cursor/skills/`, and other agent directories via `skills/sync.sh`.

```
skills/
├── {skill-name}/
│   ├── SKILL.md        # Agent instructions for this skill
│   └── scripts/        # Optional CLI executables
├── sync.sh             # Run after adding any skill to sync symlinks
└── CLAUDE.md           # Full reference: all skills, CLI tools, ID prefixes
```

See `skills/CLAUDE.md` for the complete skill inventory, CLI tool reference (`xquery`, `ytquery`), and pipeline ID prefix table. After adding a new skill, run `bash skills/sync.sh`.

---

## Private Folder

The `private/` directory contains personal and sensitive files that are:
- **Gitignored** — never committed to version control
- **Off-limits by default** — do not read, reference, or explore files in this folder

**Access rule:** Only access files in `private/` when the user explicitly adds a specific file from that folder into the conversation context. Do not proactively search, glob, or read from this directory.

---

## The Scratchpad System

Most directories support a `.scratchpad/` subfolder for active working documents.

### File Naming Convention

```
{YYYY-MM-DD}-{title}.md

Examples:
2026-01-12-quarterly-planning.md
2026-01-12-content-ideas.md
```

ISO date prefix. Year first so files sort chronologically by filename.

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
2. Follow each directory's conventions — some use scratchpads, some use other tracking systems
3. Update checkboxes as work progresses
4. Suggest CLAUDE.md updates when patterns evolve

---

## Commit Early, Commit Often

After completing meaningful work, **proactively commit and push**. Don't wait to be asked.

**Commit after:**
- Generating new content (articles, research notes, posts)
- Creating or significantly editing files
- Completing a task or request
- Any batch of related changes

**How:**
```bash
git add -A && git commit -m "feat: {concise description}" && git push
```

The goal is to never lose work and keep the repo in sync. Small, frequent commits are better than large, infrequent ones. If in doubt, commit.
