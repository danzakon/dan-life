# Content

Social media content focused on AI engineering, technology, and business.

---

## Purpose

Build a presence in the AI/tech space by sharing insights that resonate. The goal isn't just to inform—it's to create content people actually want to engage with.

---

## Structure

```
content/
├── posts/                 # Weekly post files with multiple posts per file
│   └── W4-01-26.md        # Week 4 of January 2026
├── .scratchpad/           # Ideas, research, rough drafts
│   └── .history/          # Archived scratchpad files
└── CLAUDE.md
```

---

## Posts Folder

The `posts/` folder contains markdown files organized by **week**, not day. This prevents file sprawl while keeping posts organized.

### Naming Convention

```
W{week}-{month}-{year}.md

Examples:
W1-01-26.md   # Week 1 of January 2026
W52-12-25.md  # Week 52 of December 2025
```

Week number is the ISO week of the year (1-52/53).

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

Separate each post with `---` for clear visual breaks.

---

## Tone & Voice

This is the most important section. The content needs to sound like a real person wrote it—someone who knows their stuff but doesn't take themselves too seriously.

### Core Principles

**Sound like a person, not a press release.** Write how you'd explain something to a smart friend over coffee. Use contractions. Start sentences with "And" or "But" when it flows better. Break grammar rules if it sounds more natural.

**Knowledgeable but not preachy.** Share what you've learned without lecturing. "Here's what I've seen work" beats "You should always do X." Show your thinking, not just your conclusions.

**Have opinions.** Wishy-washy content gets scrolled past. Take a stance. It's fine if not everyone agrees—that's what makes it interesting.

**Be specific.** Vague advice is forgettable. "Use caching" is boring. "We cut our API costs 70% by caching embeddings for 24 hours" is something people remember and share.

### What to Avoid

- **Corporate speak:** "leverage," "synergy," "revolutionize," "game-changing"
- **AI-bot phrases:** "In today's fast-paced world," "It's important to note that," "Let's dive in"
- **Hedging everything:** "It might be worth considering that perhaps..." Just say the thing.
- **Engagement bait:** "You won't BELIEVE what happened next" — be interesting, not clickbait
- **Obvious statements:** If everyone already knows it, why post it?

### The Vibe Check

Before posting, ask: Would a real person actually say this out loud? If it sounds like it came from a content mill or a ChatGPT prompt with no editing, rewrite it.

---

## Content Strategy

Content that performs isn't just informative—it makes people feel something.

### What Makes People Care

**Validate a frustration.** "Am I the only one who thinks X is overcomplicated?" — People love knowing they're not alone.

**Challenge conventional wisdom.** "Everyone says do X, but here's why I stopped" — Contrarian takes get attention (when backed by real experience).

**Share the uncomfortable truth.** Things people know but don't say publicly. Insider knowledge. The gap between how things "should" work and how they actually work.

**Make them feel smart.** Explain something complex in a way that clicks. The "aha moment" is shareable.

**Be the person who says what they're thinking.** If you're noticing something, others probably are too but haven't articulated it yet.

### Content Types That Work

| Type | Why It Works |
|------|--------------|
| Contrarian takes | Stops the scroll, invites debate |
| Behind-the-scenes | People love seeing how things really work |
| Lessons from failure | More relatable than success stories |
| Predictions | Stakes make it interesting |
| "Here's what I'd do" | Actionable and opinionated |
| Observations | "Has anyone else noticed..." |

### What Doesn't Work

- Pure information dumps (that's what docs are for)
- Humble brags disguised as advice
- Regurgitating what everyone else is saying
- Being controversial just for engagement

---

## Workflow

1. **Capture** — Drop raw ideas in `.scratchpad/`
2. **Develop** — Flesh out the idea, find the angle that makes it interesting
3. **Write** — Draft the post in the current week's file in `posts/`
4. **Vibe check** — Read it out loud. Does it sound like you?
5. **Post** — Publish and mark checkbox as done with date

---

## Topics

- AI engineering practices and real-world patterns
- LLM application development (what works, what doesn't)
- Tech leadership without the fluff
- Industry trends and honest commentary
- Things I got wrong and what I learned
