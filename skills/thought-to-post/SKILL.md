---
name: thought-to-post
description: Expand a raw thought or take into a polished, platform-ready post with
  Twitter and LinkedIn variants. Use when asked to "turn this thought into a post",
  "polish this take", or "make this into a post".
argument-hint: "[thought text or reference to thought-bank entry]"
---

# Thought to Post

Take a raw thought from the thought bank (or provided inline) and expand it into a polished, platform-ready post with Twitter and LinkedIn variants.

## Inputs

1. The raw thought (from `content/.scratchpad/thought-bank-*.md` or inline)
2. `content/CLAUDE.md` for tone/voice rules
3. `content/pipeline/strategy.md` for current emphasis

## Process

### Step 1: Understand the Thought

Read the raw thought. Identify:

- The core insight or opinion
- The best angle to present it (hot take? observation? advice? story?)
- Whether it needs supporting context or stands alone
- The emotional register (frustrated? enthusiastic? matter-of-fact?)

### Step 2: Choose the Format

Based on the thought's complexity:

- **Single post**: The idea can land in one shot
- **Thread**: The idea needs 3-5 tweets to unpack properly (Twitter only, LinkedIn gets a single longer post)
- **Both**: Some thoughts work as a quick take on Twitter and a more developed take on LinkedIn

### Step 3: Write Platform Variants

**Twitter variant:**
- Lead with the strongest version of the opinion
- Short, punchy sentences
- Personal voice ("I've seen...", "Here's what I think...")
- No hedging -- say the thing
- If thread: first tweet must hook, each subsequent adds value

**LinkedIn variant:**
- More context: why this matters, what prompted the thought
- Can include a brief story or example
- Still opinionated, not corporate
- Structure with line breaks
- End with something that invites discussion (not engagement-bait)

### Step 4: Vibe Check

Run through the checklist from `content/CLAUDE.md`:

1. Read it aloud. Sound like you?
2. Check sentence variety (short + long mix)
3. No em-dash overuse
4. No "it's not X, it's Y" constructions
5. No AI vocabulary (delve, landscape, leverage, etc.)
6. Has enough "I" statements to feel personal
7. Clear opinion that someone might disagree with

If it fails any check, rewrite.

### Step 5: Write to Weekly File

Write the post to the current week's file in `content/posts/`. Use the standard format:

```markdown
## [ ] {Post title/hook}

**Platform:** Both
**Source:** thought-bank-{YYYY-MM}.md

**Twitter:**
{content}

**LinkedIn:**
{content}

---
```

### Step 6: Mark as Used

If the thought came from a thought-bank file, update its entry:

```markdown
**Used:** [x]
```

## Tips

- The best posts from thoughts are ones where the original thought was already sharp. If the thought is vague, it might need research first (suggest `research-to-posts` instead).
- Don't over-expand. A tight 3-sentence take often outperforms a 3-paragraph explanation.
- Match the energy of the original thought. If it was fired up, keep that heat. If it was contemplative, don't inject false urgency.
