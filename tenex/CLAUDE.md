# Tenex

Work scratchpad for Tenex responsibilities as Tech Lead.

---

## Purpose

A space to plan, draft, and track management objectives, technical decisions, and team-related work. This is the thinking ground for leadership responsibilities.

---

## Structure

```
tenex/
├── .scratchpad/           # Active working documents
│   └── .history/          # Archived documents
├── {subfolders as needed} # Organize by project, initiative, or theme
└── CLAUDE.md
```

Subfolders can be created as needed for specific projects, initiatives, or recurring themes. Each subfolder may have its own CLAUDE.md if context is needed.

---

## What Belongs Here

| Category | Examples |
|----------|----------|
| Planning | Quarterly objectives, roadmap drafts, capacity planning |
| People | 1:1 prep, feedback drafts, hiring plans |
| Process | Workflow improvements, retrospective notes |
| Technical | Architecture decisions, tech debt priorities |
| Communication | Stakeholder updates, announcement drafts |

---

## File Format for Scratchpad

```markdown
# {Title}

**Type:** Planning | People | Process | Technical | Communication
**Status:** [ ] In Progress | [ ] Ready for Review | [x] Complete

---

{Content}

---

## Action Items
- [ ] Task 1
- [ ] Task 2
```

---

## Working Patterns

### Weekly Review
- [ ] Review open scratchpad docs
- [ ] Update status on in-progress items
- [ ] Archive completed work
- [ ] Identify next priorities

### Before 1:1s
- Create or update relevant prep doc in scratchpad
- Review previous notes if they exist

### Decision Documentation
When making significant technical or process decisions, capture:
1. Context and problem statement
2. Options considered
3. Decision and rationale
4. Follow-up actions

---

## Guidelines

- Scratchpad is for working documents, not permanent reference
- Move completed/stale docs to `.history/` regularly
- Create subfolders when a theme has 3+ related documents
- Link to external systems (Linear, Notion, etc.) rather than duplicating
