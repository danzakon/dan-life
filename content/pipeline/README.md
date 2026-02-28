# Content Pipeline System

End-to-end system for managing content creation, scheduling, and publishing on Twitter/X and LinkedIn.

---

## How It Works

```
Capture -> Create -> Review -> Queue -> Schedule -> Publish -> Track
```

**Capture**: Thoughts, bookmarks, research reports feed the pipeline. Quick capture via `capture-thought` skill or `bookmark-mining` skill.

**Create**: Write content using `write-post` or `write-article` skills. Both accept any input type (thoughts, research, bookmarks, topics) and have writing standards embedded directly.

**Review**: Human reviews and edits generated content in weekly post files or article drafts.

**Queue**: Approved posts move to `queue.md` with target dates and platform variants.

**Schedule**: Daily Cowork task reads the queue, dedup-checks against history + recent X posts, and schedules via PostBridge API.

**Publish**: PostBridge publishes posts automatically. Articles are staged by weekly Cowork task, then published manually on X.

**Track**: Everything logged to `history.md` for dedup and analytics.

---

## Directory Structure

```
life/
├── skills/                          # All personal skills (symlinked to agent dirs)
│   ├── sync.sh                      # Symlink manager
│   ├── capture-thought/             # Quick thought capture
│   ├── content-pipeline/            # Pipeline orchestration
│   ├── write-post/                  # Write posts from any input
│   ├── write-article/               # Write articles from any input
│   ├── article-image/               # Article image generation
│   ├── bookmark-mining/             # X bookmark ingestion
│   ├── postbridge/                  # PostBridge API scheduling
│   ├── research/                    # Research report generation
│   └── xquery/                      # X/Grok queries + bookmarks
│
├── content/
│   ├── CLAUDE.md                    # Directory structure, naming conventions, workflow
│   ├── .scratchpad/                 # Raw ideation + thought banks
│   │   ├── thought-bank-YYYY-MM.md  # Monthly thought capture files
│   │   └── {date}-{topic}.md        # Ideation files
│   ├── pipeline/
│   │   ├── README.md                # This file
│   │   ├── strategy.md              # Content themes, hot topics, cadence
│   │   ├── queue.md                 # Posts ready for scheduling
│   │   └── history.md               # Published content log (dedup)
│   ├── posts/                       # Short-form content (weekly files)
│   │   └── W{week}-{month}-{year}.md
│   ├── articles/
│   │   ├── drafts/                  # Work in progress
│   │   └── published/               # Live articles
│   └── images/
│       ├── prompts/                 # Saved image generation prompts
│       └── {generated images}
│
└── research/
    ├── .scratchpad/                 # Active research
    └── curiosity-reports/           # Completed reports (content source)
```

---

## Skills Reference

### Capture
| Skill | Trigger | What it does |
|-------|---------|--------------|
| `capture-thought` | "add a thought", "I'm thinking about" | Appends to current month's thought-bank file |
| `bookmark-mining` | "check my bookmarks", "bookmark ideas" | Pulls X bookmarks, surfaces content candidates |

### Create
| Skill | Trigger | What it does |
|-------|---------|--------------|
| `write-post` | "write a post about", "turn this into a post" | Writes posts from any input with platform variants |
| `write-article` | "write an article about", "turn this into an article" | Writes long-form articles from any input |
| `article-image` | "generate thumbnail for this article" | Creates 1200x675 image for article |

### Orchestrate
| Skill | Trigger | What it does |
|-------|---------|--------------|
| `content-pipeline` | "pipeline status", "what should I post", "queue this" | Master skill: delegates to others, manages queue, reviews pipeline |

### Publish
| Skill | Trigger | What it does |
|-------|---------|--------------|
| `postbridge` | "schedule this post", "post this" | Schedules content via PostBridge API to Twitter/LinkedIn |
| `xquery` | "search X for", "check my bookmarks" | X/Grok queries, bookmark access |

### Research
| Skill | Trigger | What it does |
|-------|---------|--------------|
| `research` | "research {topic}" | 4-phase research workflow producing opinionated reports |

---

## Pipeline Files

### `strategy.md`
The brain. Contains content themes, platform tone differences, posting cadence, hot topics, and Tenex messaging. This is a living document -- update it as interests shift.

### `queue.md`
Content ready to schedule. Each entry has Twitter + LinkedIn variants, a target date, priority, and status (queued/scheduled/posted). The daily Cowork task reads this file.

### `history.md`
Everything that's been published. Used by the daily scheduler for dedup and by the weekly review for tracking. Rolling log format.

### `thought-bank-YYYY-MM.md` (in `.scratchpad/`)
Monthly thought capture files. Each thought has a timestamp, topic tag, content potential (post/thread/article), and a used checkbox. The `capture-thought` skill auto-routes to the current month.

---

## Automation (Cowork Scheduled Tasks)

See [cowork-tasks.md](cowork-tasks.md) for exact setup instructions and prompts to paste into Cowork `/schedule`.

### Daily Morning Scheduler (7:30 AM)
Reads queue.md, dedup-checks against history + recent X posts, schedules today's posts via PostBridge, updates statuses, logs to history.

### Weekly Article Prep (Monday 9 AM)
Scans article drafts for `status: ready`, generates thumbnails if needed, writes staging summary, notifies that articles are ready for X Article publishing.

### Weekly Pipeline Review (Friday 4 PM)
Counts queue depth, checks content mix, reviews unused thoughts and unconverted research, suggests next week's focus, flags if queue is running low.

---

## Human Workflow

**Anytime (~10 sec)**: "Add a thought: {idea}" -> captured instantly

**Weekly or ad-hoc**: "Check my bookmarks for content ideas" -> review what surfaces

**1-2x per week (~30-60 min)**: Content creation session -> "Turn my thoughts into posts", review, edit, "Queue these"

**Weekly (~5 min)**: Review staged articles, create X Article if one is ready

**Friday glance**: Read pipeline health report, decide if more content needed

Everything else (scheduling, dedup, history tracking, queue monitoring) runs on autopilot.
