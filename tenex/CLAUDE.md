# Tenex

Engineering leadership and process development at Tenex.

---

## Purpose

A space to plan, draft, and build the systems that will shape how Tenex operates. This is where management thinking, process design, and team development come together.

---

## Context

Tenex is an applied AI consultancy and high-tech dev shop. The team is currently ~15 people and growing fast. As an engineering leader here, I'm defining core processes that will shape how we operate at scale.

**The challenge:** Limited management experience, high ambition, significant opportunity.

**The approach:** Be intentional. Research what works. Build processes deliberately. Learn from the best and adapt to our context.

---

## Structure

```
tenex/
├── .scratchpad/           # Active working documents
│   └── .history/          # Archived documents
├── processes/             # Documented engineering processes
├── frameworks/            # Mental models and decision frameworks
├── 1-on-1s/               # Templates and notes for direct reports
├── hiring/                # Interview processes, rubrics, job specs
├── culture/               # Values, norms, team dynamics
└── CLAUDE.md
```

Create subfolders as topics mature. Start in `.scratchpad/`, graduate to folders when a theme has 3+ related documents.

---

## What Belongs Here

| Category | Examples |
|----------|----------|
| Planning | Quarterly objectives, roadmap drafts, capacity planning |
| People | 1:1 prep, feedback drafts, career conversations |
| Process | Code review standards, deployment workflows, incident response |
| Technical | Architecture decisions, tech debt priorities |
| Hiring | Interview loops, rubrics, onboarding checklists |
| Culture | Values articulation, team rituals, communication norms |
| Research | How other orgs solve these problems |

---

## Scratchpad

The `.scratchpad/` folder is for active work—drafts, research notes, half-formed ideas, meeting prep.

**Archival rule:** When scratchpad exceeds **15 files**, move older files to `.history/`.

---

## File Formats

### Scratchpad Documents

```markdown
# {Title}

**Type:** Planning | People | Process | Technical | Hiring | Culture | Research
**Status:** [ ] In Progress | [ ] Ready for Review | [x] Complete

---

{Content}

---

## Action Items
- [ ] Task 1
- [ ] Task 2
```

### Process Documents

```markdown
# {Process Name}

**Status:** [ ] Draft | [ ] In Review | [x] Active
**Owner:** {Who maintains this}
**Last Updated:** {M-DD-YY}

---

## Purpose
{Why this process exists}

## When to Use
{Trigger conditions}

## The Process
{Step-by-step}

## Examples
{Concrete illustrations}

## FAQ
{Common questions}
```

### Research Notes

```markdown
# {Topic}: What [Company/Leader] Does

**Source:** {Book, article, podcast, etc.}
**Date:** {M-DD-YY}

---

## Summary
{Core ideas}

## What's Applicable
{How this maps to Tenex}

## What Doesn't Fit
{Context differences}

## Action Items
- [ ] Thing to try
```

---

## Guiding Principles

### On Process

- **Minimal viable process.** Only add structure when the pain of not having it exceeds the cost of maintaining it.
- **Write it down.** If it's not documented, it doesn't exist. Tribal knowledge doesn't scale.
- **Iterate publicly.** Processes should evolve. Version them. Explain changes.
- **Automate the boring parts.** If a process can be a script, make it a script.

### On Leadership

- **Clarity over comfort.** People deserve to know where they stand and where they're going.
- **Context over control.** Give people the why, trust them with the how.
- **Feedback is a gift.** Give it often, receive it gracefully.
- **Your job is to make others successful.** Individual contribution is now secondary.

### On Scale

- **What got you here won't get you there.** Practices that work at 15 people break at 50.
- **Hire ahead of the curve.** Build for where you're going, not where you are.
- **Culture is what you tolerate.** Standards set by action, not aspiration.

---

## Key Questions to Revisit

Regularly ask:

- What's the biggest source of friction on the team right now?
- What would I wish existed if I were a new engineer joining today?
- What are we doing manually that we'll regret at 50 people?
- Where are decisions getting stuck? Why?
- What does "great" look like for an engineer here at each level?
- How do we know if someone is struggling before it's too late?
- What would make me proud of this organization in 2 years?

---

## Resources to Explore

| Resource | Why |
|----------|-----|
| *The Manager's Path* (Fournier) | Engineering management fundamentals |
| *An Elegant Puzzle* (Larson) | Systems thinking for eng orgs |
| *High Output Management* (Grove) | Classic on leverage and meetings |
| *Radical Candor* (Scott) | Feedback and direct communication |
| *Team Topologies* | Org design for fast flow |
| *Accelerate* | What actually predicts high performance |
| Lara Hogan's blog | Practical management tactics |
| Will Larson's blog | Scaling engineering orgs |

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

## Working With Claude

When working in this folder:

1. **Challenge proposed processes.** Ask "what could go wrong?" and "does this scale?"
2. **Research how others solve it.** Before inventing, see what exists.
3. **Push for specificity.** Vague principles are useless. Make it concrete.
4. **Pressure-test with scenarios.** "How would this work when X happens?"
5. **Be opinionated.** I want a thought partner, not a rubber stamp.

---

## Guidelines

- Scratchpad is for working documents, not permanent reference
- Move completed/stale docs to `.history/` regularly
- Create subfolders when a theme has 3+ related documents
- Link to external systems (Linear, Notion, etc.) rather than duplicating
