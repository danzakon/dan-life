# Content Sources

Configuration for all ingest agents. Edit this file to control which accounts and channels are monitored. Changes take effect on the next ingest run.

---

## X Accounts — Monitor

These accounts are scraped on every ingest run. Posts since the last run are surfaced as inbox items.

```
# Format: @handle  # description
@levelsio        # indie hacking, pricing, solo founder
@karpathy        # AI/ML depth, LLM internals
@sama            # AI strategy, OpenAI
```

---

## X Accounts — Mutuals (Priority Engagement)

These accounts get a higher priority score in the digest and are always flagged for reply opportunities. Add people you want to consistently engage with.

```
# Format: @handle  # context
```

---

## YouTube Channels

Channels are checked for new videos on every ingest run. Transcripts are NOT pulled automatically — the youtube-monitor surfaces new video titles and asks for approval before fetching a transcript.

```
# Format: {channel-id}  # channel name | keyword filter (optional)
# Keyword filter: only surface videos whose titles contain these terms (comma-separated)
# Leave blank to surface all new videos

# Example:
# UCxxxxxxxxxxxxxxxx  # Lex Fridman | (no filter — all videos)
# UCyyyyyyyyyyyyyyyy  # MKBHD | AI, software, coding
```

---

## Research Triggers

When these terms appear in 3 or more inbox items within a 7-day window, the digest will suggest kicking off a research report on the topic.

```
agentic coding
context windows
production AI
```
