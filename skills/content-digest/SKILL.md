# Content Digest

Processes new inbox items after ingest. Scores each item against the content strategy, refines content angles, checks for series connections, and re-ranks by opportunity. Runs between ingest and the interview step.

---

## Trigger

- Automated: Part of the daily 7:30 AM Cowork digest task (runs after ingest)
- Manual: "Digest my inbox", "Process today's inbox", "Score my inbox"

---

## Workspace

- `content/inbox/_index.md` — find which days have undigested items
- `content/inbox/YYYY-MM-DD.md` — inbox files to process
- `content/pipeline/strategy.md` — hot topics, themes, cadence for scoring
- `content/pipeline/series.md` — active series for connection detection
- `content/.scratchpad/thought-bank-*.md` — existing thoughts to cross-reference
- `content/pipeline/index.db` — update status raw → inbox

---

## Process

### Step 1: Find items to digest

Read `content/inbox/_index.md`. Find all days with items in `raw` or `inbox` status. Process the most recent undigested day first. If running on schedule, process all undigested days.

```bash
sqlite3 content/pipeline/index.db \
  "SELECT DISTINCT substr(id,1,8) as day FROM items WHERE status = 'raw' ORDER BY day DESC;"
```

### Step 2: Load strategy context

Read `content/pipeline/strategy.md`. Extract:
- Hot topics (high-relevance keywords for scoring)
- Content themes (categories to tag items with)
- Current emphasis (what's most important right now)

Read `content/pipeline/series.md`. Extract active series themes and keywords.

### Step 3: Score and annotate each item

For each item in the inbox file with status `unreviewed`:

**Relevance score (1–10):** How well does this align with hot topics and current emphasis?
- 8–10: Directly on a hot topic, timely, high engagement potential
- 5–7: Adjacent to themes, interesting but not urgent
- 1–4: Off-theme, weak signal, likely to skip

**Content type tag:** Which theme does this belong to?
- research-synthesis | practical-how-to | engineering-take | hot-take | tenex | engagement

**Urgency flag:**
- `time-sensitive` — reply opportunity, breaking news, trending topic (24–48hr window)
- `evergreen` — can be developed anytime
- `research-first` — needs a research report before content can be developed

**Series connection:** Does this connect to any active series in `series.md`? Name the series if so.

**Cross-reference:** Search `content/.scratchpad/thought-bank-*.md` for existing thoughts on the same theme. List any matches.

### Step 4: Refine content angles

For each item, review the angles that were auto-generated during ingest. Improve them based on strategy context:

- Sharpen the hot take to be more provocative or specific
- Make the practical angle more concrete and actionable
- Identify the single strongest angle given current strategy emphasis
- Flag the **lead angle** — the one most worth developing first

### Step 5: Update inbox file

Rewrite the inbox file in-place with:
- Items reordered by relevance score (highest first)
- Score, type tag, urgency, and series connection added to each item header
- Refined angles replacing the original generated ones
- Lead angle flagged

Updated item header format:
```markdown
## [{ID}] {Title}

**Status:** digested
**Score:** 8/10
**Type:** engineering-take
**Urgency:** time-sensitive
**Series:** the-refinement-era
**Lead angle:** Hot take — creation is cheap, refinement is the skill
...
```

### Step 6: Update index.db

For each processed item:
```bash
sqlite3 content/pipeline/index.db \
  "UPDATE items SET status = 'inbox' WHERE id = '{ID}';"
```

### Step 7: Update _index.md

Mark the processed day as `digested` in the Day Status table. Update item rows with current status.

### Step 8: Summary

Report:
```
Digested 8 items from 2026-03-07:

  Time-sensitive (reply now):
    20260307-BM-001  @levelsio pricing — Score 9/10
    20260307-XM-003  Karpathy on training — Score 8/10

  High priority:
    20260307-YM-001  Lex Fridman ep — Score 7/10 (series: AI in Production)

  Normal:
    4 more items scored 4–6

  Skipped: 1 item (off-theme, score 2)

Ready for /content-interview to review these.
```

---

## Scoring Heuristics

| Signal | Score boost |
|--------|-------------|
| Matches a hot topic exactly | +3 |
| From a high-priority mutual account | +2 |
| Has a reply opportunity (reply-monitor flag) | +2 |
| Connects to an active series | +1 |
| Research report on same topic exists | +1 |
| Time-sensitive / trending | +2 |
| Off-theme entirely | -4 |
| Duplicate angle to recent post in history.md | -3 |

---

## Prerequisites

None beyond `sqlite3` (pre-installed on macOS).
