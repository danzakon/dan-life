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

Ingest recent X bookmarks and surface content ideas. Finds interesting takes, data, and topics worth remixing into your own content.

## Prerequisites

The `xquery` command must be in the user's PATH with `x:bookmarks` support configured (OAuth 2.0 user tokens). See the xquery skill for setup.

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

### Step 6: Present Candidates

Show the top 5-8 bookmarks with highest content potential:

```
## Bookmark Content Candidates

### 1. {Topic} (by @{author})
{Tweet summary}
**Why it's interesting:** {brief explanation}
**Content angle:** {how you could remix this}
**Suggested format:** post | thread | article | research-first

### 2. ...
```

### Step 7: User Chooses

Ask: "Which of these should I work with? Options:"

- **Bank it**: Invoke `capture-thought` to save the idea for later
- **Post now**: Invoke `thought-to-post` to create a post immediately
- **Research first**: Suggest running the `research` skill to go deeper before creating content
- **Skip**: Move on

### Step 8: Execute

Based on user choice, delegate to the appropriate skill with the bookmark context as input.

## Tips

- Don't just regurgitate bookmarked tweets. The value is in the remix: your take, your angle, your experience layered on top.
- Bookmarks with high engagement are signals of what resonates, but the best content often comes from low-engagement bookmarks that contain insights nobody else noticed.
- Group related bookmarks into themes. Three bookmarks about the same trend might warrant a research deep-dive or article rather than individual posts.
