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
**Suggested format:** post | quote-tweet | thread | article | research-first

### 2. ...
```

### Step 7: User Chooses

Ask: "Which of these should I work with? Options:"

- **Bank it**: Invoke `capture-thought` to save the idea for later (source metadata is preserved — see below)
- **Post now**: Invoke `thought-to-post` to create a post immediately
- **Quote tweet**: Draft a quote-tweet response to the original
- **Research first**: Suggest running the `research` skill to go deeper before creating content
- **Skip**: Move on

### Step 8: Execute

Based on user choice, delegate to the appropriate skill with the bookmark context as input. Always pass the source metadata block (see below) so downstream skills have full attribution context.

---

## Source Attribution

**Every piece of content that originates from a bookmark must carry source metadata.** This prevents accidental plagiarism and enables proper attribution when publishing.

### Capturing Source Metadata

When banking a thought, creating a post, or writing any content derived from a bookmark, include a source block in the markdown:

```markdown
> **Source:** [@{username}](https://x.com/{username}/status/{tweet_id})
> {Full original tweet text}
```

This block must be preserved through the entire pipeline — from thought bank to queue to published post. It's the provenance chain.

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

### Thought Bank Format

When saving a bookmark-sourced idea via `capture-thought`, use this format:

```markdown
- **{time}** | #{topic} | {content_type}
  {Your idea / angle / take}
  > **Source:** [@{username}](https://x.com/{username}/status/{tweet_id})
  > {Original tweet text}
  - Used: [ ]
```

This ensures the source travels with the idea through the entire pipeline.

---

## Tips

- Don't just regurgitate bookmarked tweets. The value is in the remix: your take, your angle, your experience layered on top.
- Bookmarks with high engagement are signals of what resonates, but the best content often comes from low-engagement bookmarks that contain insights nobody else noticed.
- Group related bookmarks into themes. Three bookmarks about the same trend might warrant a research deep-dive or article rather than individual posts.
- Quote-tweeting is underrated. If someone said something interesting and you have a strong take on it, a quote tweet with your commentary is fast, attributive, and builds engagement with the original author.
