---
name: write-post
description: Write a polished social media post with Twitter and LinkedIn variants.
  Accepts any input — a thought, a research report, a bookmark, a topic, or just a
  conversation. Use when asked to "write a post", "draft a tweet", "turn this into
  a post", "make a post about", or "polish this take".
argument-hint: "[thought, topic, research path, or bookmark context]"
allowed-tools:
  - Read
  - Write
  - Bash
---

# Write Post

Write a polished, platform-ready post with Twitter and LinkedIn variants from any input.

## Inputs

This skill handles any starting point:

- A raw thought (inline or from `content/.scratchpad/thought-bank-*.md`)
- A research report (from `research/curiosity-reports/`)
- A bookmarked tweet (with source attribution)
- A topic or idea mentioned in conversation
- A link to an article or resource

Read `content/pipeline/strategy.md` for current content themes and hot topics.

## Process

### Step 1: Understand the Input

Identify:

- The core insight, opinion, or information
- The best angle (hot take? observation? how-to? experience? data point?)
- Whether it needs supporting context or stands alone
- The natural tone (frustrated? enthusiastic? matter-of-fact? curious?)

### Step 2: Choose Format

Based on the idea's complexity:

- **Single post**: The idea lands in one shot
- **Thread**: Needs 3-5 tweets to unpack (Twitter only; LinkedIn gets a single longer post)
- **Both**: Quick take on Twitter, more developed version on LinkedIn

### Step 3: Write Platform Variants

**Twitter:**
- 280 chars for single tweets, threads for anything longer
- Lead with the strongest version of the opinion
- Personal voice when you have direct experience
- No hedging
- No hashtag spam (1-2 max if genuinely relevant)

**LinkedIn:**
- 500-1500 chars (LinkedIn rewards longer, more developed posts)
- More context and framing: why this matters, what prompted the thought
- Professional but human. Not corporate.
- Structure with line breaks for readability
- Can end with something that invites genuine discussion

### Step 4: Quality Check

Run through this before finishing:

1. Read it aloud. Does it sound like something a real person would say?
2. Does it have an actual opinion? Wishy-washy content gets scrolled past.
3. Is it specific? Vague advice is forgettable. Include numbers, examples, concrete details when possible.
4. Would someone share this? Would it make someone tag a friend or hit repost?
5. Check for AI patterns (see Writing Standards below).

### Step 5: Write to Weekly File

Save to the current week's file:

```
content/posts/W{week}-{month}-{year}.md
```

Create the file if it doesn't exist. Format:

```markdown
## [ ] {Post title/hook}

**Platform:** Both
**Source:** {where the idea came from}

**Twitter:**
{content}

**LinkedIn:**
{content}

---
```

### Step 6: Mark Sources Used

- If from a thought-bank entry, update it to `Used: [x]`
- If from a bookmark, include the source attribution block (see bookmark-mining skill)

---

## Writing Standards

These apply to every post this skill produces.

### Voice

Write like a person explaining something to a smart colleague. Not a press release, not a LinkedIn influencer, not a content mill.

**Have real opinions.** Take stances. Say what you actually think. If not everyone agrees, good.

**Be specific over general.** "We cut API costs 70% by caching embeddings for 24 hours" is something people remember. "Caching can help reduce costs" is something they scroll past.

**Use first person when you have experience.** "I've seen this fail" hits harder than "this often fails." Don't fake experience you don't have.

**Match the natural energy of the idea.** If the thought was fired up, keep that heat. If it was contemplative, don't inject false urgency. Don't force every post into the same register.

**Write to be understood, not to sound smart.** Use plain language for plain ideas. Use precise language for precise ideas. Don't inflate simple concepts with complex vocabulary, but don't dumb down genuinely complex ones either.

### Anti-AI Patterns

AI-generated text has recognizable tells. Avoid all of these:

**Em-dashes.** AI overuses them to the point where they're now a dead giveaway. Use periods, commas, or "but" instead.

```
BAD:  The problem isn't technical—it's organizational.
GOOD: The problem isn't technical. It's organizational.
```

**The contrast cliche.** "It's not X, it's Y" or "X isn't about Y — it's about Z." Find other ways to draw contrasts.

```
BAD:  The real story isn't the agent. It's what the approach reveals.
GOOD: The agent itself matters less than what the approach reveals.
```

**Overused AI vocabulary.** These words appear constantly in AI output and rarely in natural writing:

| Avoid | Use instead |
|-------|-------------|
| delve | dig into, explore |
| tapestry | mix, combination |
| landscape | space, world, field |
| unlock | enable, open up |
| foster | encourage, build |
| leverage | use |
| realm | area, domain |
| multifaceted | complex, layered |
| underscores | shows, highlights |

**Structural tells:**

- Don't start with "In today's..." or "In the world of..."
- Don't write "It's important to note that..."
- Don't use "Let's dive in" or "Let's explore"
- Don't write lists of exactly three when two or four would be more natural
- Don't ask rhetorical questions that you answer immediately

### What Makes Content Work

**Validate a frustration.** "Am I the only one who thinks X is overcomplicated?" People engage when they feel seen.

**Challenge conventional wisdom.** "Everyone says do X, but here's why I stopped." Contrarian takes get attention when backed by real experience.

**Share what people know but don't say.** Insider knowledge. The gap between how things should work and how they actually work.

**Be the person who articulates what others are thinking.** If you're noticing something, others probably are too but haven't put words to it yet.

### What Doesn't Work

- Pure information dumps (that's what documentation is for)
- Humble brags disguised as advice
- Regurgitating what everyone else is saying
- Being controversial just for engagement
- Engagement bait ("You won't BELIEVE...")
- Obvious statements everyone already agrees with
