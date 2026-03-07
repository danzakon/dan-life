# Skills

Agent skill definitions and CLI tools for the Life OS. Skills are symlinked into all agent directories (Claude Code, Cursor, Codex, Gemini, Clawd) via `sync.sh` — one source of truth, available everywhere.

---

## How the System Works

```
life/skills/
├── {skill-name}/
│   ├── SKILL.md        ← Agent instructions (what any agent does when this skill runs)
│   └── scripts/        ← Optional: CLI executables called by the skill via Bash
├── sync.sh             ← Symlinks all skills into every agent's skill directory
└── CLAUDE.md           ← This file
```

`sync.sh` creates symlinks:
```
~/.claude/skills/{skill-name}  →  life/skills/{skill-name}/
~/.cursor/skills/{skill-name}  →  life/skills/{skill-name}/
~/.codex/skills/{skill-name}   →  life/skills/{skill-name}/
~/.gemini/skills/{skill-name}  →  life/skills/{skill-name}/
~/clawd/skills/{skill-name}    →  life/skills/{skill-name}/
```

Run after adding any new skill: `bash skills/sync.sh`

---

## Two Layers: Skills vs CLI Tools

**Skills** (`SKILL.md`) are agent instructions — they document a workflow that any agent executes. They have no code; they orchestrate via Bash tool calls.

**CLI tools** (`scripts/`) are standalone Python executables that skills call via Bash. They have their own interfaces, config files, and auth. The two CLI tools are:

| Tool | Location | What it does |
|------|----------|-------------|
| `xquery` | `xquery/scripts/xquery` | Query X/Twitter: search, users, tweets, bookmarks (OAuth). Also queries Grok (xAI). |
| `ytquery` | `ytquery/scripts/ytquery` | Query YouTube: channels, videos, transcripts, thumbnails, screenshots, clips, Watch Later, search. |

Both are symlinked to `~/.local/bin/` for PATH access:
```bash
~/.local/bin/xquery  →  ~/.claude/skills/xquery/scripts/xquery
~/.local/bin/ytquery →  life/skills/ytquery/scripts/ytquery
```

---

## CLI Tool Reference

### xquery

```bash
xquery "prompt"                # Grok query with live X search
xquery x:search "query"        # Search recent tweets
xquery x:user @handle          # User profile + recent tweets
xquery x:tweet <id>            # Single tweet lookup
xquery x:bookmarks             # Your bookmarks (OAuth required)
xquery x:bookmarks --limit 50
xquery --json ...              # Raw JSON output
```

Config: `~/.config/xquery/.env`
- `XAI_API_KEY` — for Grok queries
- `X_BEARER_TOKEN` — for x:search, x:user, x:tweet ($100/mo X Basic tier)
- `X_CLIENT_ID` + `X_USER_ID` — for x:bookmarks (OAuth 2.0 PKCE, one-time browser auth)

### ytquery

```bash
ytquery y:channel @handle       # Recent videos from a channel
ytquery y:video <url>           # Video metadata
ytquery y:transcript <url>      # Fetch transcript text
ytquery y:thumbnail <url>       # Download video thumbnail (no deps)
ytquery y:screenshot <url> <ts> # Frame at timestamp
ytquery y:clip <url> <s> <e>    # Extract clip (social-media-ready MP4)
ytquery y:clip ... --subs       # Clip with burned-in subtitles
ytquery y:watchlater            # Watch Later playlist (needs cookies)
ytquery y:search "query"        # Search YouTube
ytquery y:rss @handle           # Get channel RSS feed URL
ytquery --json ...              # Raw JSON output
ytquery --limit N ...           # Control result count
ytquery --output path ...       # Save output to file
```

Config: `~/.config/ytquery/.env`
- `YOUTUBE_COOKIES` — path to cookies.txt for Watch Later + age-restricted content

Dependencies (install separately):
```bash
pip install yt-dlp youtube-transcript-api
brew install ffmpeg deno          # deno required by yt-dlp since Nov 2025
```

---

## All Skills

### Content Pipeline

The pipeline flows: **Ingest → Digest → Interview → Draft → Refine → Queue → Publish**

| Skill | Stage | What it does |
|-------|-------|-------------|
| `content-pipeline` | Orchestrator | Master session menu. Reads pipeline state, presents options, delegates to all other skills. Start here. |
| `content-digest` | Digest | Scores inbox items against strategy, refines angles, re-ranks by opportunity. Runs after ingest. |
| `content-interview` | Interview (human) | Interactive inbox review. Shows items one at a time, captures your take, writes briefs. |
| `content-refine` | Refine (human) | Iterative draft editing. Presents drafts, captures feedback, polishes. |
| `db-rebuild` | Maintenance | Reconstructs `index.db` from file frontmatter when DB is corrupted or lost. |

### Ingest Skills (Sources → Raw Files + Inbox)

All ingest skills follow the same output contract: assign ID → write raw file → write inbox entry → register in `index.db`.

| Skill | Source | ID Prefix | CLI Tool |
|-------|--------|-----------|---------|
| `bookmark-mining` | X bookmarks | `BM` | `xquery x:bookmarks` |
| `x-account-monitor` | X accounts from sources.md | `XM` | `xquery x:user` |
| `reply-monitor` | Replies to @danzakon | `RM` | `xquery x:search` |
| `youtube-monitor` | YouTube channels from sources.md | `YM` | `ytquery y:channel`, `y:transcript`, `y:thumbnail` |
| `watch-later-mining` | YouTube Watch Later playlist | `WL` | `ytquery y:watchlater` |
| `save-raw` | Manual URL or pasted text | `SR` | Exa MCP / WebFetch |
| `idea-dump` | Raw thoughts → structured content | `ID` | None |
| `research` | Deep research reports | `RS` | Exa MCP |
| `tutorial` | Technical how-to guides | `TU` | Exa MCP |

### Creation Skills (Briefs → Content)

| Skill | Input | Output |
|-------|-------|--------|
| `write-post` | Brief file | Twitter + LinkedIn variants, alt hooks |
| `write-article` | Brief file | Long-form draft in `content/articles/drafts/` |
| `article-image` | Article file | 1200×628px header image in `content/images/` |
| `capture-thought` | Raw thought | Entry in `content/.scratchpad/thought-bank-YYYY-MM.md` |

### Publishing

| Skill | What it does |
|-------|-------------|
| `postbridge` | PostBridge API: upload media, schedule posts, manage social accounts |

### Research + Learning

| Skill | What it does |
|-------|-------------|
| `research` | Multi-agent research → opinionated report in `research/reports/` |
| `tutorial` | Multi-agent research → practical step-by-step guide in `tutorials/guides/` |
| `xquery` | Query Grok + X API directly (also a CLI tool, see above) |
| `ytquery` | Query YouTube directly (also a CLI tool, see above) |

---

## Pipeline ID Prefixes

Every pipeline item gets a stable ID: `YYYYMMDD-{PREFIX}-NNN`

| Prefix | Source skill | Data type |
|--------|-------------|-----------|
| `BM` | bookmark-mining | X bookmarks |
| `XM` | x-account-monitor | X posts from monitored accounts |
| `RM` | reply-monitor | Replies to @danzakon |
| `YM` | youtube-monitor | YouTube videos (channel monitoring) |
| `WL` | watch-later-mining | YouTube Watch Later videos |
| `SR` | save-raw | Manually ingested URLs / pasted content |
| `ID` | idea-dump | Raw thoughts → structured ideas |
| `RS` | research | Research reports |
| `TU` | tutorial | Technical guides |

---

## Adding a New Skill

1. Create `skills/{name}/SKILL.md` with YAML frontmatter:
   ```yaml
   ---
   name: skill-name
   description: "One line. Describes when the agent should invoke this skill."
   argument-hint: "[optional args hint]"
   allowed-tools:
     - Read
     - Write
     - Bash
   ---
   ```
2. Add any scripts to `skills/{name}/scripts/` and `chmod +x`
3. Run `bash skills/sync.sh` to link to all agent directories
4. If a CLI tool needs to be in PATH: `ln -sf $(pwd)/skills/{name}/scripts/{tool} ~/.local/bin/{tool}`
5. Update this CLAUDE.md with the new skill

---

## Key Files the Skills Operate On

```
content/pipeline/
├── index.db          ← SQLite: every pipeline item + status
├── strategy.md       ← Content themes, voice, hot topics, cadence
├── sources.md        ← X accounts + YouTube channels to monitor
├── series.md         ← Active content series tracker
├── queue.md          ← Posts approved and scheduled
└── history.md        ← Published content log (dedup)

content/
├── inbox/            ← Daily intake files (YYYY-MM-DD.md)
├── raw/              ← Source material (x-posts/, youtube/, web/)
├── briefs/           ← Post-interview work items (YYYYMMDD-SRC-NNN.md)
├── posts/            ← Weekly post drafts (YYYY-W{NN}.md)
├── articles/         ← Long-form (drafts/ + published/)
└── .scratchpad/      ← Thought banks + ideation files

research/reports/     ← Research output
tutorials/guides/     ← Technical guide output
```
