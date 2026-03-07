---
name: bookmark-mining
description: Pull recent X bookmarks and surface content opportunities. Use when
  asked to "check my bookmarks", "mine my bookmarks", "bookmark ideas", or
  "what have I bookmarked lately".
argument-hint: "[optional: number of bookmarks to check]"
allowed-tools:
  - Read
  - Write
  - Bash
---

# Bookmark Mining

Ingest recent X bookmarks into the content pipeline. Fetches bookmarks, filters for content potential, writes raw files and inbox entries with content angles, and registers everything in `index.db`.

## Prerequisites

The `xquery` command must be in the user's PATH with `x:bookmarks` support configured (OAuth 2.0 user tokens). See the xquery skill for setup.

## Workspace

- `content/raw/x-posts/` — full tweet text storage
- `content/inbox/YYYY-MM-DD.md` — today's inbox
- `content/inbox/_index.md` — master registry
- `content/pipeline/index.db` — item registration
- `content/pipeline/strategy.md` — for angle generation
- `content/pipeline/series.md` — for series connection checks

## Workflow

### Step 1: Fetch Bookmarks

```bash
xquery x:bookmarks --limit 50
```

This returns recent bookmarks with tweet text, author, URLs, and engagement metrics.

If `x:bookmarks` is not available yet (OAuth not configured), fall back to asking the user to paste bookmark URLs or use browser to manually check bookmarks.

### Step 2: Filter Political Content

Before analyzing, filter out bookmarks that are **purely political** — partisan takes, culture war content, candidate/party commentary, policy debates unrelated to tech. These have zero content potential for our purposes.

If the majority of bookmarks in a batch are political (more than ~60%), **automatically paginate** and fetch the next batch:

```bash
xquery x:bookmarks --limit 50 --next-token <token>
```

Keep paginating (up to 3 pages) until you have at least 10 non-political bookmarks to work with. If a bookmark touches politics but has a genuine tech/AI/engineering angle (AI regulation, open-source policy, tech industry impact), keep it — the content angle should be the tech lens, not the political one.

### Step 3: Analyze Content

For each remaining bookmark, identify:

- **Topic**: What is it about?
- **Content type**: Take/opinion, data/research, tool/product, news, tutorial
- **Engagement signals**: High likes/reposts suggest resonance
- **URLs**: Does it link to an article or resource worth reading deeper?

### Step 4: Fetch Linked Content (Optional)

For bookmarks with interesting URLs, optionally fetch the linked content:

- Use Exa MCP (`web_search_exa`) for topic-related searches
- Use WebFetch for specific article URLs
- This adds depth for bookmarks that are just link-shares

### Step 5: Group and Rank

Group bookmarks by theme/topic. Rank by content potential:

- **High potential**: Unique data, contrarian take, something your audience hasn't seen
- **Medium potential**: Interesting but common knowledge, or already widely discussed
- **Low potential**: Personal/tangential, no clear content angle

### Step 6: Write Raw Files and Inbox Entries

For each bookmark worth capturing (high or medium potential), assign a `BM` ID and write to the pipeline:

**Assign ID:**
```bash
sqlite3 content/pipeline/index.db \
  "SELECT id FROM items WHERE id LIKE '$(date +%Y%m%d)-BM-%' ORDER BY id DESC LIMIT 1;"
```
Increment the NNN portion (start at 001 if no results).

**Write raw file** to `content/raw/x-posts/YYYYMMDD-BM-NNN-{handle}-{slug}.md`:

```yaml
---
id: YYYYMMDD-BM-NNN
source-type: x-post
ingest-source: bookmark-mining
original-url: https://x.com/{username}/status/{tweet_id}
author: @{username}
captured: ISO 8601 UTC
---

{Full tweet/thread text}
```

**Write inbox entry** to `content/inbox/YYYY-MM-DD.md`:

```markdown
## [YYYYMMDD-BM-NNN] @{author} — {Topic}

**Status:** unreviewed
**Type:** {content theme tag}
**Original:** {tweet URL}
**Raw file:** content/raw/x-posts/{filename}
**Ingest source:** bookmark-mining

### Summary
{2–3 sentence summary}

### Content angles (develop all applicable formats now)
1. **Hot take**: {provocative read}
2. **Practical**: {actionable spin}
3. **Nuanced**: {the "yes, but" angle}

### Content tree
- **Reply**: {reply opportunity to the original?}
- **Post**: {standalone angle}
- **Thread**: {breakdown opportunity}
- **Article**: {long-form potential}
- **Series**: {connection to series.md?}

### Actions
- [ ] Review in content-interview
```

**Register in index.db:**
```bash
sqlite3 content/pipeline/index.db \
  "INSERT INTO items (id, created_at, source_type, ingest_source, status, current_title, original_url, raw_file)
   VALUES ('{ID}', '{datetime}', 'x-post', 'bookmark-mining', 'raw',
           '@{author}: {topic}', '{url}', 'content/raw/x-posts/{filename}');"
```

**Update `content/inbox/_index.md`** with new item rows.

### Step 7: Present Summary

Show what was captured and what's ready for review:

```
Bookmark Mining — 2026-03-07
─────────────────────────────────────────
Fetched 50 bookmarks, filtered to 8 with content potential.

Captured 8 items to inbox:
  BM-001  @levelsio — pricing take (high potential)
  BM-002  @karpathy — training data quality (high)
  BM-003  @someone — agentic coding patterns (medium)
  ...

Skipped: 42 (political, personal, low potential)

Ready for /content-interview to review.
```

### Step 8: Offer Immediate Action (Optional)

If running interactively (not as part of a Cowork scheduled task), offer:

```
Want to:
  A) Review these in /content-interview now
  B) Workshop the top one immediately (idea-dump style)
  C) Done — I'll review later
```

Based on user choice, delegate to the appropriate skill.

---

## Source Attribution

**Every piece of content that originates from a bookmark must carry source metadata.** This prevents accidental plagiarism and enables proper attribution when publishing.

### Capturing Source Metadata

When banking a thought, creating a post, or writing any content derived from a bookmark, include a source block in the markdown:

```markdown
> **Source:** [@{username}](https://x.com/{username}/status/{tweet_id})
> {Full original tweet text}
```

This block must be preserved through the entire pipeline — from brief to queue to published post. It's the provenance chain.

### Remix Rules

Content derived from bookmarks must be **genuinely remixed**, not rephrased:

- **Add your own take** — Layer your experience, opinion, or expertise on top. The bookmark is a spark, not the content itself.
- **Add new information** — Combine the bookmark's insight with your own knowledge, additional research, or a different framing.
- **Change the angle** — If the original is a data point, your content could be "what this means for engineers." If it's an opinion, yours could be a counterpoint or extension.
- **Never just rephrase** — If the only difference between the original tweet and your post is word choice, it's too close. Add substance or skip it.

### Attribution in Published Content

Depending on the format, attribute differently:

| Format | How to attribute |
|---|---|
| **Quote tweet** | Use X's native quote-tweet. Your commentary goes above, original is embedded. Best when you want to directly respond or riff on the original. |
| **Post referencing a tweet** | Include "h/t @{username}" or "via @{username}" and link to the original tweet in the post text. |
| **Thread** | Reference the source tweet in the first post or as a reply in the thread. |
| **Article** | Link to the original tweet inline where you reference the idea. No need for formal citation — a natural "as @{username} pointed out" with a link is fine. |
| **Fully remixed (no direct reference)** | If your content has diverged far enough that the original is just a starting spark, no attribution needed. Use your judgment — if someone reading both would say "that's the same take," attribute. |

---

## Tips

- Don't just regurgitate bookmarked tweets. The value is in the remix: your take, your angle, your experience layered on top.
- Bookmarks with high engagement are signals of what resonates, but the best content often comes from low-engagement bookmarks that contain insights nobody else noticed.
- Group related bookmarks into themes. Three bookmarks about the same trend might warrant a research deep-dive or article rather than individual posts.
- Quote-tweeting is underrated. If someone said something interesting and you have a strong take on it, a quote tweet with your commentary is fast, attributive, and builds engagement with the original author.
