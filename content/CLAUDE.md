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

## Tone & Voice

The content needs to sound like a real person—someone who knows their stuff but doesn't take themselves too seriously.

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

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ .scratchpad │────▶│   drafts/   │────▶│ published/  │
│  (ideation) │     │  (writing)  │     │   (live)    │
└─────────────┘     └─────────────┘     └─────────────┘
       │                                       │
       │            ┌─────────────┐            │
       └───────────▶│   posts/    │◀───────────┘
                    │  (weekly)   │
                    └─────────────┘
```

1. **Capture** — Drop raw ideas in `.scratchpad/`
2. **Develop** — Flesh out the idea, find the angle
3. **Write** — Draft in `articles/drafts/` or current week's `posts/` file
4. **Vibe check** — Read it out loud. Does it sound like you?
5. **Publish** — Post and update status/checkbox. Move articles to `published/`

---

## Topics

- AI engineering practices and real-world patterns
- LLM application development (what works, what doesn't)
- Tech leadership without the fluff
- Industry trends and honest commentary
- Things I got wrong and what I learned

---

## Writing Articles That Don't Sound Like AI

When converting research reports into published articles, the goal is writing that performs well online while sounding unmistakably human. Here's how.

### The Research-to-Article Pipeline

```
Research Report              Article
┌──────────────────┐         ┌──────────────────┐
│ Comprehensive    │         │ One perspective  │
│ Multiple angles  │   ──▶   │ Multiple angles  │
│ All the data     │         │   in service of  │
│ Exploratory tone │         │   the narrative  │
└──────────────────┘         └──────────────────┘
```

Research reports explore. Articles argue.

The article needs a singular perspective, a clear throughline that everything else supports. But that doesn't mean one narrow point. Multiple angles, examples, and sections all contribute to the main narrative. They reinforce the perspective from different directions.

Think of it like a legal case: one argument, many pieces of evidence.

---

### Sentence Rhythm and Cadence

Good writing has a beat. It's not monotonous. You vary the length.

Some sentences are short. They punch.

Others need room to breathe, to unfold across a longer structure that lets a more complex thought develop naturally before landing on its point.

**The principle:** Alternate. Don't string together five sentences of identical length. Don't make every sentence complex. Mix it up. Let short sentences carry weight after longer ones. Let longer sentences provide context before a short one drives it home.

**Read it aloud.** If you run out of breath, the sentence is too long. If it sounds like a robot reciting bullet points, add some flow.

| Pattern | Effect |
|---------|--------|
| Short after long | Creates emphasis, drives point home |
| Long after short | Provides context, explains the punch |
| Three shorts in a row | Builds urgency, creates staccato rhythm |
| Sustained long sentences | Slows pace, adds contemplation |

The goal isn't following rules. It's making the writing feel alive.

---

### Avoiding AI Writing Patterns

AI has tells. These patterns make writing feel synthetic even when the ideas are good. Actively avoid them.

**The em-dash epidemic**

AI loves em-dashes. It inserts them constantly. This has become such a well-known tell that readers now pattern-match "em-dash heavy" to "AI-generated."

```
BAD:  The problem isn't technical—it's organizational.
BAD:  We tried everything—caching, indexing, sharding—nothing worked.
BAD:  This approach—while unconventional—solved our issue.

GOOD: The problem isn't technical. It's organizational.
GOOD: We tried caching, indexing, sharding. Nothing worked.
GOOD: The approach was unconventional, but it solved our issue.
```

Use em-dashes sparingly, if at all. Periods, commas, and "but" accomplish the same thing without the AI smell.

**The contrast cliché**

AI constantly writes "it's not X, it's Y" or "X isn't Y—it's Z." This structure is now a dead giveaway.

```
BAD:  Ramp isn't demonstrating a toy—they're showing production infrastructure.
BAD:  The real story isn't the agent. It's what the approach reveals.
BAD:  This isn't about speed—it's about control.

GOOD: Ramp moved past the toy phase. This is production infrastructure.
GOOD: The agent itself matters less than what Ramp's approach reveals.
GOOD: Speed matters, but control matters more.
```

Find other ways to make contrasts. Use "but." Use separate sentences. Reframe entirely.

**Vocabulary AI overuses**

These words appear constantly in AI output and rarely in natural human writing:

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| delve | Massively overused since 2023 | dig into, explore, examine |
| tapestry | AI's favorite metaphor for complexity | mix, web, combination |
| landscape | AI's favorite opening word | space, world, field |
| unlock | AI loves this verb | enable, open up, make possible |
| unveil | Theatrical and overused | show, reveal, introduce |
| foster | Formal and stiff | encourage, build, grow |
| leverage | Corporate AI speak | use |
| realm | Fantasy novel energy | area, space, domain |
| multifaceted | AI's way of saying "complex" | complex, complicated, layered |
| underscores | AI's favorite way to say "shows" | shows, highlights, proves |

If you catch yourself using these, pause. Find a simpler word.

**Structural patterns to avoid**

- Starting with "In today's [X]" or "In the world of [X]"
- "It's important to note that..."
- "Let's dive in" or "Let's explore"
- Lists of exactly three examples when two or four would be more natural
- Every paragraph being exactly the same length
- Rhetorical questions that answer themselves immediately

---

### Writing With Personal Voice

The article should sound like it came from a person with opinions, experiences, and a specific point of view. That person is you.

**First person is fine.** "I've seen this fail" hits harder than "This often fails." Use "I" when you have direct experience. Use "we" when describing shared industry experiences.

**Include specifics from your experience.** Not "teams struggle with X" but "I watched three teams struggle with X last year." Not "this approach works" but "we shipped this approach and it cut our costs 40%."

**Have opinions.** Research reports can be balanced. Articles should take stances. "Both approaches have merit" is boring. "Approach A is better for most teams, and here's why" is interesting.

**Acknowledge uncertainty honestly.** "I'm not sure about this, but..." is more human than hedging with weasel words. Admit what you don't know directly rather than hiding it in qualifications.

**Let personality through.** Mild frustration, enthusiasm, humor when appropriate. The writing should have temperature, not be room-temperature neutral.

---

### The Vibe Check for Articles

Before publishing, run through this:

1. **Read it aloud.** Does it sound like you talking? Or like a press release?
2. **Check sentence variety.** Do you have a mix of short and long? Or all medium?
3. **Search for em-dashes.** Can you replace most of them with periods or commas?
4. **Search for "it's not X, it's Y."** Rewrite any instances.
5. **Search for the AI vocabulary list.** Replace offenders.
6. **Find your "I" statements.** Are there enough? Do they feel authentic?
7. **Identify the perspective.** Can you state it in one sentence? Do all sections support it?
8. **Cut the throat-clearing.** Does the piece get to the point quickly?

If it passes, it's ready.
