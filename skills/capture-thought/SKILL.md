---
name: capture-thought
description: Quickly capture a thought, take, or idea into the content thought bank.
  Use when asked to "add a thought", "capture this", "I'm thinking about", or "thought:".
argument-hint: "[thought text]"
---

# Capture Thought

Fast-path skill for capturing raw thoughts into the content pipeline. No analysis, no suggestions. Just capture and confirm.

## Workspace

The thought bank lives in the user's life repo: `content/.scratchpad/`

## File Routing

Thoughts go into **monthly files**:

```
content/.scratchpad/thought-bank-YYYY-MM.md
```

Use the current month. If the file doesn't exist, create it with this header:

```markdown
# Thought Bank -- {Month Name} {Year}

## Hot Topics

Topics actively on my mind this month:

-

---

## Thoughts
```

## Capture Format

Append each thought as:

```markdown

### YYYY-MM-DD | {Topic Tag}

{The raw thought exactly as provided}

**Potential:** {post | thread | article}
**Used:** [ ]
```

## Rules

1. **Be fast.** Don't rewrite, analyze, or expand the thought. Capture it verbatim.
2. **Infer the topic tag** from the content (e.g., "AI Engineering", "Tech Leadership", "Tenex", "Hot Take"). Keep tags short and consistent.
3. **Infer content potential** based on length and complexity:
   - Short opinion or observation -> `post`
   - Multi-part idea that needs unpacking -> `thread`
   - Deep topic that needs research or long-form treatment -> `article`
4. **Confirm** with a one-line response: "Captured: {topic tag} thought in {month} bank."
5. If the user provides multiple thoughts at once, capture each as a separate entry.
6. Never modify existing entries in the file.

## Series Connection Check

After capturing, do a quick (non-blocking) check:

1. Read `content/pipeline/series.md` — does this thought's topic connect to any active series?
2. Scan the current month's thought bank — are there 2+ unused thoughts on the same topic tag?

If a connection is found, add a brief note after the confirmation:

```
Captured: AI Engineering thought in March bank.
(Connects to "The Refinement Era" series — 3 related thoughts now. Consider /idea-dump to develop.)
```

If 3+ related unused thoughts are found, suggest promoting to a series:

```
Captured: AI Engineering thought in March bank.
You now have 3 unused thoughts on agentic coding. Worth starting a series? Run /idea-dump to workshop them.
```

Keep this lightweight — one extra line maximum. The capture path must stay fast.

## Examples

User: "Add a thought: Most AI agents fail because they try to do too much. The best ones are narrow and deep."

Action: Append to `thought-bank-2026-03.md`:

```markdown

### 2026-03-07 | AI Engineering

Most AI agents fail because they try to do too much. The best ones are narrow and deep.

**Potential:** post
**Used:** [ ]
```

Response: "Captured: AI Engineering thought in March bank."
