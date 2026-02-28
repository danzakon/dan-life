# Cowork Scheduled Tasks

Setup instructions and exact prompts for the three automated tasks that power the content pipeline.

---

## How to Set Up

1. Open Claude Desktop (make sure it's up to date)
2. Open Cowork
3. Type `/schedule` in any task OR click "Scheduled" in the sidebar -> "New task"
4. For each task below: paste the name, description, prompt, and set the cadence
5. Set the working folder to your `life/` directory

---

## Task 1: Daily Morning Scheduler

**Name:** Content Pipeline - Daily Post Scheduler

**Cadence:** Daily, 7:30 AM

**Working folder:** ~/dev/life/

**Prompt:**

```
Read content/pipeline/queue.md in this workspace. Find all posts with today's date
as their target date and status "queued".

For each queued post:

1. Dedup check: Run `xquery x:user @danzakon --limit 20` to get my recent tweets.
   Compare the queued post content against these recent posts and against
   content/pipeline/history.md. If the content is substantially similar to something
   already posted, skip it and note the duplicate.

2. Schedule via PostBridge: Use curl to call the PostBridge API.
   - API key is in the POST_BRIDGE_API_KEY environment variable
   - Base URL: https://api.post-bridge.com
   - First: GET /v1/social-accounts to get Twitter and LinkedIn account IDs
   - Then: POST /v1/posts with:
     - "caption" set to the LinkedIn content variant (default)
     - "social_accounts" array with both Twitter and LinkedIn account IDs
     - "scheduled_at" set to an optimal time today (spread posts across 9am, 12pm,
       3pm, 6pm ET)
     - "platform_configurations" with twitter.caption set to the Twitter content variant
   - No media upload needed for text-only posts

3. Update queue.md: Change the post's status from "queued" to "scheduled"

4. Log to history.md: Append a row with today's date, platforms (Twitter, LinkedIn),
   type (post), content summary (first line), and source file reference

After processing all posts, write a summary:
- How many posts were scheduled and at what times
- Any duplicates skipped
- Current queue depth remaining
```

---

## Task 2: Weekly Article Prep

**Name:** Content Pipeline - Weekly Article Prep

**Cadence:** Weekly, Monday 9:00 AM

**Working folder:** ~/dev/life/

**Prompt:**

```
Scan content/articles/drafts/ for any article files with "status: ready" in their
YAML frontmatter.

For each ready article:

1. Check content/pipeline/history.md to confirm this article hasn't already been
   published.

2. Check if a thumbnail image exists in content/images/ matching the article slug
   (e.g., for 2026-02-responsible-for-your-own-slop.md, look for
   2026-02-responsible-for-your-own-slop-og.png).

3. If no thumbnail exists:
   - Read the article to understand its topic, tone, and key concepts
   - Create a detailed image generation prompt following the style guidelines
     in skills/article-thumbnail/SKILL.md (1200x675, 16:9, bold/simple visuals)
   - Save the prompt to content/images/prompts/{slug}-prompt.md
   - Generate the image and save to content/images/{slug}-og.png
   - Update the article frontmatter with: thumbnail: images/{slug}-og.png

4. Update the article's frontmatter status from "ready" to "staged"

5. Write a staging summary listing:
   - Article title
   - Thumbnail path (generated or existing)
   - Note: "Ready for X Article publishing - review and post manually"

This task prepares articles for publishing but does NOT publish them. The human
reviews and creates the X Article manually.
```

---

## Task 3: Weekly Pipeline Review

**Name:** Content Pipeline - Weekly Review

**Cadence:** Weekly, Friday 4:00 PM

**Working folder:** ~/dev/life/

**Prompt:**

```
Review the content pipeline health. Generate a Pipeline Health Report.

1. Queue status: Read content/pipeline/queue.md. Count entries by status:
   queued, scheduled, posted. Calculate how many days of content remain assuming
   3 posts per day (the target cadence from content/pipeline/strategy.md).

2. Thought bank: Read all content/.scratchpad/thought-bank-*.md files. Count
   entries where "Used: [ ]" (unused thoughts). List the topic tags of unused
   thoughts to show theme distribution.

3. Ideation files: Count files in content/.scratchpad/ (excluding thought-bank
   files). Note any recent ones that might have content potential.

4. Unconverted research: List files in research/curiosity-reports/ that have NOT
   been referenced in content/pipeline/history.md or in any content/posts/ weekly
   files. These are research reports that haven't been turned into content yet.

5. Content mix: Review the last 2 weeks of content/pipeline/history.md entries.
   Compare the theme distribution against content/pipeline/strategy.md content
   themes. Note any themes that are underrepresented.

6. Hot topics: Read content/pipeline/strategy.md "Hot Topics" section. Suggest
   updates based on patterns in recent thoughts and research.

Write the report in this format:

## Pipeline Health Report - {date}

### Queue
- {n} posts queued ({n} days at current cadence)
- {n} posts scheduled
- {n} posts posted this week
- **Status:** {Healthy / Low / Urgent}

### Thought Bank
- {n} unused thoughts across {n} months
- Top themes: {list}

### Unconverted Research
- {n} reports not yet converted to content
- {list of report names}

### Content Mix (last 2 weeks)
- {theme distribution vs targets}

### Recommendations
- {2-3 specific suggestions for next week}
- {flag if queue will run dry}

If the queue has fewer than 3 days of content remaining, mark the status as
URGENT and emphasize that a content creation session is needed.
```

---

## Tips

- All three tasks can be paused/resumed from the Cowork sidebar
- Run any task manually anytime by clicking "Run now"
- If a task fails, check that the working folder is set correctly and API keys are accessible
- The daily scheduler needs `POST_BRIDGE_API_KEY` as an environment variable or in `~/.config/postbridge/.env`
- The daily scheduler needs `xquery` in your PATH for dedup checks
