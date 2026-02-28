# Content

Social media content focused on AI engineering, technology, and business.

---

## Purpose

Build a presence in the AI/tech space by sharing insights that resonate. The goal isn't just to inform—it's to create content people actually want to engage with.

---

## Structure

```
content/
├── .scratchpad/           # Unstructured ideation (ideas, research, fragments)
│   └── .history/          # Archived scratchpad files
├── posts/                 # Short-form: tweets, LinkedIn posts (weekly files)
│   └── W4-01-26.md
├── articles/              # Long-form: full essays (one per file)
│   ├── drafts/            # Work in progress
│   └── published/         # Live articles
└── CLAUDE.md
```

---

## Scratchpad

The `.scratchpad/` folder is for raw ideation—half-baked ideas, research notes, random observations, content fragments. No structure required. Let ideas accumulate and see what rises to the top.

**Archival rule:** When scratchpad exceeds **10 files**, move older files to `.history/`. Keep scratchpad lean and current.

---

## Posts

Short-form content: tweets, LinkedIn posts, quick takes. Organized by **week** to prevent file sprawl.

### Naming Convention

```
W{week}-{month}-{year}.md

Examples:
W1-01-26.md   # Week 1 of January 2026
W52-12-25.md  # Week 52 of December 2025
```

### Post File Format

Each file contains multiple posts. Use checkboxes to track posting status:

```markdown
# Posts — Week 4, January 2026

---

## [ ] The real reason AI projects fail

**Platform:** LinkedIn
**Hook:** Most AI projects don't fail because of the tech.

{Post content here}

---

## [x] Hot take on RAG

**Platform:** Twitter/X
**Posted:** 2026-01-24

{Post content here}

---
```

- `[ ]` — Not yet posted
- `[x]` — Posted (add date)

---

## Articles

Long-form content: full essays, deep dives, thought pieces. **One article per file.**

### Folder Structure

```
articles/
├── drafts/      # Work in progress
└── published/   # Live articles (move here after publishing)
```

### Naming Convention

```
{YYYY}-{MM}-{slug}.md

Examples:
2026-01-why-rag-fails.md
2026-01-building-agents-that-work.md
```

### Article Format

Every article starts with YAML frontmatter:

```yaml
---
title: Why RAG Fails in Production
status: draft | ready | published
published_date: 2026-01-24   # add when published
platform: blog | medium | substack
---

{Article content here}
```

**Status meanings:**
- `draft` — Still writing, not ready for review
- `ready` — Written and polished, waiting to publish
- `published` — Live (move file to `published/` folder)

---

## Workflow

See [pipeline/README.md](pipeline/README.md) for the full content pipeline system, including all skills, automation, and scheduling.

```
Capture -> Create -> Review -> Queue -> Schedule -> Publish -> Track
```

1. **Capture** — Quick thoughts via `capture-thought` skill -> monthly thought-bank files in `.scratchpad/`. Bookmark mining via `bookmark-mining` skill. Research via `research` skill.
2. **Create** — Write content using `write-post` or `write-article` skills. Both accept any input type (thoughts, research, bookmarks, topics). Writing standards are embedded in these skills.
3. **Review** — Edit drafts in `posts/` weekly files or `articles/drafts/`.
4. **Queue** — Approved posts go to `pipeline/queue.md` with target dates and platform variants.
5. **Schedule** — Daily Cowork task reads queue, dedup-checks, schedules via PostBridge API.
6. **Publish** — PostBridge handles posts. Articles staged for X Articles by weekly Cowork task.
7. **Track** — Everything logged to `pipeline/history.md`.

### Key Files

- `pipeline/strategy.md` — Content themes, hot topics, cadence, Tenex messaging
- `pipeline/queue.md` — Posts ready for scheduling
- `pipeline/history.md` — Published content log (dedup database)
- `.scratchpad/thought-bank-YYYY-MM.md` — Monthly thought capture

### Skills

All in `life/skills/`, symlinked to agent directories via `skills/sync.sh`:

| Skill | Purpose |
|-------|---------|
| `capture-thought` | Quick thought capture into monthly thought-bank |
| `content-pipeline` | Pipeline orchestration (delegates to other skills) |
| `write-post` | Write posts from any input (thoughts, research, bookmarks, topics) |
| `write-article` | Write articles from any input |
| `article-image` | Article image generation (1200x675) |
| `bookmark-mining` | X bookmark ingestion + content ideas |
| `postbridge` | PostBridge API scheduling |

---

## Topics

- AI engineering practices and real-world patterns
- LLM application development (what works, what doesn't)
- Tech leadership without the fluff
- Industry trends and honest commentary
- Things I got wrong and what I learned
- Tenex hiring, culture, and positioning

