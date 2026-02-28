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

### {M-DD-YY} | {Topic Tag}

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

## Examples

User: "Add a thought: Most AI agents fail because they try to do too much. The best ones are narrow and deep."

Action: Append to `thought-bank-2026-02.md`:

```markdown

### 2-28-26 | AI Engineering

Most AI agents fail because they try to do too much. The best ones are narrow and deep.

**Potential:** post
**Used:** [ ]
```

Response: "Captured: AI Engineering thought in February bank."
