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

**CLI tools** (`scripts/`) are standalone Python executables that skills call via Bash. They have their own interfaces, config files, and auth.

| Tool | Location | What it does |
|------|----------|-------------|
| `xquery` | `xquery/scripts/xquery` | Query X/Twitter: search, users, tweets, bookmarks (OAuth). Also queries Grok (xAI). |
| `ytquery` | `ytquery/scripts/ytquery` | Query YouTube: channels, videos, transcripts, thumbnails, screenshots, clips, Watch Later, search. |
| `mediagen` | `mediagen/scripts/mediagen` | Generate AI images and videos: openai, google, kling, seedance, runway, minimax. |

All three are symlinked to `~/.local/bin/` for PATH access:
```bash
~/.local/bin/xquery   →  ~/.claude/skills/xquery/scripts/xquery
~/.local/bin/ytquery  →  life/skills/ytquery/scripts/ytquery
~/.local/bin/mediagen →  life/skills/mediagen/scripts/mediagen
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
brew install ffmpeg deno          # deno required by yt-dlp since Nov 2025
# Python deps (yt-dlp, youtube-transcript-api) auto-installed via uv on first run
```

### mediagen

```bash
mediagen i:gen "prompt"                 # Generate image (default: openai/gpt-image-1.5)
mediagen i:gen "prompt" -o path.png --size 1792x1024
mediagen i:gen "prompt" --provider google --model imagen-4.0-fast-generate-001
mediagen i:edit image.png "make it darker" -o out.png
mediagen v:gen "prompt" -o clip.mp4 --duration 8
mediagen v:gen "prompt" --no-wait       # Return task ID immediately
mediagen v:status TASK_ID -o clip.mp4 --provider google
mediagen providers                      # Show configured/available providers
mediagen models                         # Show all models by provider
mediagen --json i:gen "prompt" -o out.png  # JSON output
```

Config: `~/.config/mediagen/.env`
- `OPENAI_API_KEY` — GPT-Image-1.5 (image) + Sora 2 (video)
- `GEMINI_API_KEY` — Imagen 4 (image) + Veo 3.1 (video)
- `KLING_API_KEY` — Kling 3.0/2.6 video (via piapi.ai)
- `SEEDANCE_API_KEY` — SeedDance 2.0 video
- `RUNWAY_API_KEY` — Runway Gen-4.5 video
- `MINIMAX_API_KEY` — MiniMax Hailuo video
- `DEFAULT_IMAGE_PROVIDER` / `DEFAULT_IMAGE_MODEL` — override image defaults
- `DEFAULT_VIDEO_PROVIDER` / `DEFAULT_VIDEO_MODEL` — override video defaults

Setup:
```bash
chmod +x skills/mediagen/scripts/mediagen
bash skills/sync.sh
ln -sf $(realpath skills/mediagen/scripts/mediagen) ~/.local/bin/mediagen
# Python deps auto-installed via uv on first run
```

---

## All Skills

### Content Pipeline

The pipeline is accessed through a single entry point: **`/content-pipeline`**.

```
/content-pipeline
├── Dashboard (always shown — health, queue status, recommendations)
├── INGEST — pull new signals from sources
│   ├── bookmark-mining, x-account-monitor, reply-monitor
│   ├── youtube-monitor, watch-later-mining
│   └── Full sweep (all sources + digest)
├── ADD — put something into the system
│   └── Smart router: thoughts, URLs, bulk ideas, research, tutorials
└── WORK — develop and ship content
    ├── Work session (draft → refine → queue, batch or one-at-a-time)
    └── Review inbox (delegates to content-interview)
```

| Skill | Role | User-invocable? |
|-------|------|-----------------|
| `content-pipeline` | Single entry point for all content work. Dashboard, ingest, add, work session. | Yes — `/content-pipeline` |
| `content-interview` | Interactive inbox review. Shows items one at a time, captures your take, writes briefs. | No — called by pipeline option 9 |
| `content-digest` | Scores inbox items against strategy, refines angles, re-ranks by opportunity. | No — runs automatically after ingest |
| `db-rebuild` | Reconstructs `index.db` from file frontmatter when DB is corrupted or lost. | Yes — `/db-rebuild` |

### Ingest Skills (Sources → Raw Files + Inbox)

All ingest skills follow the same output contract: assign ID → write raw file → write inbox entry → register in `index.db`. Called by content-pipeline options 1-6.

| Skill | Source | ID Prefix | CLI Tool |
|-------|--------|-----------|---------|
| `bookmark-mining` | X bookmarks | `BM` | `xquery x:bookmarks` |
| `x-account-monitor` | X accounts from sources.md | `XM` | `xquery x:user` |
| `reply-monitor` | Replies to @danzakon | `RM` | `xquery x:search` |
| `youtube-monitor` | YouTube channels from sources.md | `YM` | `ytquery y:channel`, `y:transcript`, `y:thumbnail` |
| `watch-later-mining` | YouTube Watch Later playlist | `WL` | `ytquery y:watchlater` |

### Creation Skills (Briefs → Content)

Called internally by the content-pipeline work session.

| Skill | Input | Output | User-invocable? |
|-------|-------|--------|-----------------|
| `write-post` | Brief file | Twitter + LinkedIn variants, alt hooks | No — called by pipeline |
| `write-article` | Brief file | Long-form draft in `content/articles/drafts/` | No — called by pipeline |
| `article-image` | Article file | 1200x628px header image in `content/images/` | No — called by pipeline |
| `mediagen` | CLI: generate images + videos from prompts. Supports openai, google, kling, seedance, runway, minimax. | Image or video file | No — called by article-image and other skills |

### Research + Learning

These remain directly invocable AND accessible through content-pipeline's Add mode.

| Skill | What it does | ID Prefix |
|-------|-------------|-----------|
| `research` | Multi-agent research → opinionated report in `research/reports/` | `RS` |
| `tutorial` | Multi-agent research → practical step-by-step guide in `tutorials/guides/` | `TU` |

### Publishing

| Skill | What it does |
|-------|-------------|
| `postbridge` | PostBridge API: upload media, schedule posts, manage social accounts |

### CLI Tools (also skills)

| Skill | What it does |
|-------|-------------|
| `xquery` | Query Grok + X API directly (also a CLI tool, see above) |
| `ytquery` | Query YouTube directly (also a CLI tool, see above) |
| `mediagen` | Generate AI images and videos from the command line (also a CLI tool, see above) |

---

## Pipeline ID Prefixes

Every pipeline item gets a stable ID: `YYYYMMDD-{PREFIX}-NNN`

| Prefix | Source | Data type |
|--------|--------|-----------|
| `AD` | content-pipeline (Add mode) | Manual additions: thoughts, URLs, bulk ideas |
| `BM` | bookmark-mining | X bookmarks |
| `XM` | x-account-monitor | X posts from monitored accounts |
| `RM` | reply-monitor | Replies to @danzakon |
| `YM` | youtube-monitor | YouTube videos (channel monitoring) |
| `WL` | watch-later-mining | YouTube Watch Later videos |
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
├── briefs/           ← Work items (YYYYMMDD-SRC-NNN-{slug}.md)
├── posts/            ← Weekly post drafts (YYYY-W{NN}.md)
└── articles/         ← Long-form (drafts/ + queued/ + published/)

research/reports/     ← Research output
tutorials/guides/     ← Technical guide output
```
