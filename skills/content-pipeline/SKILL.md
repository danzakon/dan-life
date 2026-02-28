---
name: content-pipeline
description: Orchestrate the content pipeline. Use when asked to "check my pipeline",
  "pipeline status", "what should I post", "queue this", or "queue these posts".
argument-hint: "[command or context]"
---

# Content Pipeline

Master orchestration skill for the content pipeline. Delegates to specialized skills for content creation, manages the queue, and reviews pipeline health.

## Workspace

All pipeline state lives in the user's life repo:

- `content/pipeline/strategy.md` -- content themes, hot topics, cadence
- `content/pipeline/queue.md` -- posts ready for scheduling
- `content/pipeline/history.md` -- published content log
- `content/.scratchpad/thought-bank-YYYY-MM.md` -- monthly thought capture
- `content/posts/` -- weekly post files
- `content/articles/drafts/` -- article drafts
- `content/CLAUDE.md` -- tone, voice, writing standards
- `research/curiosity-reports/` -- completed research (content source)

## Commands

### "Pipeline status" / "Check my pipeline"

Generate a pipeline health report:

1. Count items in `queue.md` by status (queued, scheduled, posted)
2. Count unused thoughts across all `thought-bank-*.md` files (entries where `Used: [ ]`)
3. Count ideation files in `content/.scratchpad/` (excluding thought-bank files)
4. Count research reports in `research/curiosity-reports/` not yet converted to content (cross-reference against `history.md` and existing `posts/` files)
5. Read posting cadence from `strategy.md`
6. Calculate days of content remaining in queue
7. Report:
   - Queue depth and days remaining
   - Unused thought count
   - Unconverted research reports
   - Content mix assessment
   - Urgent flag if queue < 3 days

### "What should I post" / "Content ideas"

1. Read `strategy.md` for current hot topics and content themes
2. Read the most recent thought-bank file for unused thoughts
3. Check `research/curiosity-reports/` for unconverted research
4. Suggest 3-5 specific content ideas with recommended format (post/thread/article) and platform

### "Turn my thoughts into posts" / "Turn this research into posts"

Delegate to the appropriate skill:

- For thoughts: invoke the `thought-to-post` skill workflow
- For research: invoke the `research-to-posts` skill workflow
- For articles: invoke the `research-to-article` skill workflow

Read `strategy.md` first to understand current emphasis, then pass context to the delegated skill.

### "Queue this" / "Queue these posts"

Move approved posts from the current week's post file into `queue.md`:

1. Read the specified posts (or all unchecked posts in the current week file)
2. For each approved post, add an entry to `queue.md` with:
   - Title/hook
   - Target date (spread across upcoming days, respecting cadence targets)
   - Platform (Twitter, LinkedIn, or Both)
   - Twitter and LinkedIn content variants
   - Status: `queued`
   - Source reference (which file/thought it came from)
3. Dedup check: compare against `history.md` and existing queue entries
4. Report what was queued and the target schedule

### "Dedup check" / Before queuing

Cross-reference content against:

1. `history.md` -- everything already published
2. Existing entries in `queue.md` -- don't double-queue
3. Optionally: `xquery x:user @{handle} --limit 20` for recent X posts

Flag any potential duplicates and ask before proceeding.

## Content Creation Guidelines

When delegating to content creation skills, always pass:

1. The source material (thought, research report, or bookmark)
2. Current strategy context from `strategy.md` (hot topics, current emphasis)
3. Reference to `content/CLAUDE.md` for tone/voice rules
4. Target platform(s)

## Weekly Post File Format

Posts created by content skills go into weekly files:

```
content/posts/W{week}-{month}-{year}.md
```

See `content/CLAUDE.md` for the exact post file format.
