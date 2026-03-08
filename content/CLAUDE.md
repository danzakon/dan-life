# Content

Social media content focused on AI engineering, technology, and business.

---

## Purpose

Build a presence in the AI/tech space by sharing insights that resonate. The goal isn't just to inform — it's to create content people actually want to engage with.

---

## Structure

```
content/
├── CLAUDE.md              # This file — directory conventions
├── pipeline/              # CONTROL PLANE: ops config + live state
│   ├── README.md          # Full pipeline system documentation
│   ├── strategy.md        # Content themes, voice, cadence
│   ├── sources.md         # X accounts + YouTube channels to monitor
│   ├── series.md          # Ongoing content series tracker
│   ├── queue.md           # Approved posts pending scheduling
│   ├── history.md         # Published content log (dedup)
│   ├── index.db           # SQLite index (all items + pipeline state)
│   ├── schema.sql         # DB schema source of truth
│   ├── migrations/        # Schema migration scripts
│   └── cowork-tasks.md    # Cowork scheduled task setup + prompts
├── inbox/                 # DAILY INTAKE: signals from ingest agents
│   ├── _index.md          # Item registry + day status
│   └── YYYY-MM-DD.md      # One file per day (summaries + angles)
├── raw/                   # SOURCE MATERIAL: full content, never truncated
│   ├── x-posts/
│   ├── x-articles/
│   ├── youtube/
│   └── web/
├── briefs/                # WORK ITEMS: the atomic unit of the pipeline
│   └── YYYYMMDD-SRC-NNN.md
├── posts/                 # SHORT-FORM DRAFTS (weekly files)
│   └── YYYY-W{NN}.md
├── articles/
│   ├── drafts/       # status: draft — actively being written
│   ├── queued/       # status: ready — approved, waiting to publish
│   └── published/    # status: published — live
└── images/
    ├── prompts/
    └── {slug}-og.png
```

---

## Pipeline System

The full pipeline architecture, stages, skills, automation, and standards are documented in [pipeline/README.md](pipeline/README.md). That is the canonical reference for how content moves through the system.

```
INGEST → DIGEST → INTERVIEW (human) → DRAFT → REFINE (human) → STAGE → PUBLISH
```

Every idea that enters the system — thoughts, bookmarks, videos, research — becomes a **brief** with a tracked ID. Briefs are the atomic unit. No side channels.

---

## File Naming Conventions

### Posts

Weekly files containing multiple posts:

```
YYYY-W{NN}.md

Examples:
2026-W01.md
2026-W09.md
2026-W52.md
```

Year first, zero-padded week number. Sorts chronologically.

### Post File Format

```markdown
# Posts — 2026-W09

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

### Articles

One article per file in `articles/drafts/` or `articles/published/`:

```
YYYY-MM-{slug}.md

Examples:
2026-01-why-rag-fails.md
2026-02-agentic-second-brain.md
```

### Article Format

```yaml
---
title: Why RAG Fails in Production
status: draft | ready | published
published_date: 2026-01-24
platform: blog | medium | substack
---

{Article content here}
```

- `draft` — Still writing
- `ready` — Polished, waiting to publish
- `published` — Live (move to `published/`)

### Briefs

One brief per pipeline item:

```
YYYYMMDD-{SRC}-NNN.md

Examples:
20260307-BM-001.md
20260307-AD-003.md
```

See [pipeline/README.md](pipeline/README.md) for the full brief format and ID prefix table.

### Raw Files

Source material with ID prefix:

```
YYYYMMDD-{SRC}-NNN-{slug}.md

Examples:
20260307-BM-001-levelsio-pricing.md
20260307-YM-002-lex-fridman-transcript.md
```

---

## Topics

- AI engineering practices and real-world patterns
- LLM application development (what works, what doesn't)
- Tech leadership without the fluff
- Industry trends and honest commentary
- Things I got wrong and what I learned
- Tenex hiring, culture, and positioning
