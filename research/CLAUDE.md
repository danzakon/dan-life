# Research

Research reports and explorations on technical topics, tools, frameworks, and ideas.

---

## Structure

```
research/
├── .scratchpad/           # Working notes and sub-agent output
│   └── .history/          # Archived research
├── reports/               # Completed research reports
└── CLAUDE.md
```

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

## File Naming Convention

All files use a `YYYYMMDD` date prefix for chronological sorting:

```
reports/{YYYYMMDD}-{slug}.md             # 20260308-agentic-sdlc-big-team-leverage.md
.scratchpad/{YYYYMMDD}-{slug}.md         # 20260308-mobile-agent-ui-findings.md
```

This matches the date-prefix convention used across the content pipeline. Never omit the date prefix.

---

## Pipeline Integration

Research reports are registered in the content pipeline as `RS`-prefixed items (`YYYYMMDD-RS-NNN`). The `/research` skill handles this automatically. See `skills/research/SKILL.md` for the full research workflow.

---

## Guidelines

- Capture sources and links as you go
- Summarize key findings at the top
- Move stale `.scratchpad/` files to `.scratchpad/.history/` during cleanup
- Final reports in `reports/` are permanent
