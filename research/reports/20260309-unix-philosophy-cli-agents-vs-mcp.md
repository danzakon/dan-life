---
id: 20260309-RS-002
date: 2026-03-09
category: Research Report
content-status: raw
---

# Unix Philosophy & CLI Composability for AI Agents: Why Bash Beats MCP

---

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [Background](#background)
3. [Peter Steinberger: "MCP Was a Mistake. Bash Is Better."](#peter-steinberger)
4. [Andrej Karpathy: CLIs as "Legacy Technology" Are the Future](#andrej-karpathy)
5. [Joel Hooks: HATEOAS for CLIs and Agent-First Design](#joel-hooks)
6. [Eric Holmes: The Composability Gap](#eric-holmes)
7. [The Pre-Filtering Advantage](#pre-filtering)
8. [The CLI Army Pattern](#cli-army)
9. [The Academic Angle: Unix Philosophy Meets Agentic AI](#academic)
10. [Key Takeaways](#key-takeaways)
11. [Predictions](#predictions)

---

## Executive Summary

The AI agent community is going through a reckoning with MCP (Model Context Protocol). The consensus that emerged in early 2026 is stark: for developers running local agents with shell access, CLIs dramatically outperform MCP servers across every meaningful dimension — composability, context efficiency, debuggability, and reliability. Peter Steinberger, creator of OpenClaw (190K+ GitHub stars, now 289K), built his entire agent framework around ~10 focused CLI tools and zero MCP in the core, then posted "mcp were a mistake. bash is better." Andrej Karpathy called CLIs "super exciting precisely because they are legacy technology." Joel Hooks designed a complete CLI protocol with HATEOAS-style `next_actions` that makes every tool self-navigable. Eric Holmes wrote the definitive teardown showing MCP provides "no real-world benefit."

The core insight: Unix pipes let agents pre-filter data before it enters the context window, while MCP dumps everything. A `terraform show -json | jq` pipeline does in one shell command what would require either blowing the context window or building custom MCP server logic. The 50-year-old Unix philosophy — small tools, text streams, pipes — accidentally built the perfect agent protocol decades before agents existed.

This doesn't mean MCP is useless. It has a role in multi-tenant enterprise SaaS where CLIs don't exist and OAuth discovery matters. But for the developer-with-an-agent use case that represents the bleeding edge of agentic work, CLI wins decisively.

---

## Background

MCP (Model Context Protocol) was announced by Anthropic in late 2024 as a standardized way for LLMs to interact with external tools. The protocol defines a JSON-RPC interface where tools declare schemas, parameters, and descriptions, and the model sends structured requests and receives structured responses. Every major AI company scrambled to ship MCP servers — GitHub, Jira, Slack, Notion, you name it.

The Unix philosophy, by contrast, dates to the 1970s at Bell Labs. Ken Thompson and Dennis Ritchie established principles that remain foundational: do one thing well, expect the output of every program to become the input of another, and use text as the universal interface. Pipes (`|`), stdin/stdout, exit codes, and `--help` flags form a composable protocol that's been battle-tested for 50+ years.

AI coding agents (Claude Code, Cursor, OpenClaw, Codex, Pi) all have shell access. They can execute any CLI tool. This means the entire Unix ecosystem — thousands of existing tools — is immediately available to every agent without any integration work.

---

## Peter Steinberger: "MCP Was a Mistake. Bash Is Better." {#peter-steinberger}

### Who He Is

Peter Steinberger is a solo developer from Vienna who shipped OpenClaw (originally Clawdbot) as a weekend project in early 2026. It became the fastest-growing repository in GitHub history — 190,000 stars within three months, two million visitors in a single week, and is now at 289K stars. Sam Altman reportedly made a nine-figure offer to recruit him to OpenAI.

### What He Built

OpenClaw is a personal AI assistant that operates across platforms. The key architectural decision: **everything is a CLI**. Steinberger built approximately 10 focused command-line tools that his agent orchestrates through bash. From his [Homebrew tap](https://github.com/steipete/homebrew-tap), these include:

| Tool | Purpose |
|------|---------|
| `wacli` | WhatsApp CLI built on whatsmeow |
| `imsg` | Send and read iMessage/SMS from the terminal |
| `gogcli` | Google CLI for Gmail, Calendar, Drive, Contacts |
| `peekaboo` | macOS screenshots & AI vision analysis |
| `camsnap` | RTSP/ONVIF camera frame/clip capture |
| `ordercli` | Multi-provider food ordering (Foodora, Deliveroo) |
| `summarize` | Link → clean text → summary |
| `sag` | ElevenLabs TTS with mac-style flags |
| `sonoscli` | Sonos speaker control |
| `blucli` | BluOS playback and automation |
| `mcporter` | MCP runtime and CLI generator (converts MCPs to CLIs) |

OpenClaw itself started as a one-liner: WhatsApp message in → Claude Code CLI → result out. No MCP. Built in an hour. He even built `mcporter` — a tool to **convert existing MCP servers into CLIs** — because he wanted everything scriptable.

### His Exact Argument

From the [Luke Tucker interview transcript](https://luketucker.com/openclaw-kilocode-and-why-cli-mcp/), Steinberger said:

> "In order for this (OpenClaw) to work you want everything to be a CLI. Why CLIs and not MCPs? MCP is a crutch. The best thing that came out of MCP is it made companies rethink to open up more APIs. The whole concept is silly. You have to pre-export all the functions of all the tools and all the explanations when your tool loads. And then the model has to send a precise blob of JSON there and gets JSON back. But surprise, models are really good at using bash."

He gave a concrete example of the filtering problem:

> "Imagine you have a weather service and the model could ask for a list of available cities and get like 500 cities back, and then it picks one city out of that list but it cannot filter that list because that's not part of how MCP works … and you'd say okay give me the weather for London. And you'd get weather forecast, temperature, wind… and 50 other things I don't care about because I just want to know 'is it raining or not?' But the model needs to digest everything and then you have so much crap in your context. Whereas if it's a CLI I could filter for exactly what it needs."

And the composability kill shot:

> "I cannot chain them. I cannot easily build a script that says hey give me all the cities that are over 25 degrees and then filter out only that part of information and pack it in one command. It's all individual MCP calls I cannot script it."

A [LinkedIn summary](https://www.linkedin.com/posts/mojoshi1_ai-agenticai-cli-activity-7430453696087609344-Fuvq) captured the contrast:
- **MCP**: Dumps everything at the model — ask for weather in London, get 50 fields you don't need. Context bloat is real.
- **CLI**: Lets you pipe, filter, chain. The model reads the help menu and figures it out. No JSON blobs, no pre-exported schemas.

### Peekaboo: The Case Study

Steinberger's [Peekaboo tool](https://steipete.me/posts/2025/peekaboo-2-freeing-the-cli-from-its-mcp-shackles) was originally an MCP server for macOS screenshots. He rewrote it as a CLI in version 2.0, explicitly "freeing the CLI from its MCP shackles." His reasoning:

> "Lately there's a mind shift in the community to realize that most MCPs are actually better if they're just CLIs. Agents have an easier time calling CLIs, they can be loaded on-demand without cluttering the context, and they are composable."

The MCP version had to be pre-loaded into every session, consuming context tokens even when screenshots weren't needed. The CLI version is discovered and invoked on-demand — zero tokens until the agent actually needs it.

---

## Andrej Karpathy: CLIs as "Legacy Technology" Are the Future {#andrej-karpathy}

### The Statement

On February 24, 2026, Andrej Karpathy — former Tesla AI chief, OpenAI co-founder, and one of the most respected voices in machine learning — posted on X that CLIs are "super exciting precisely because they are a legacy technology." The post pulled nearly 2 million views.

According to [multiple](https://blockchain.news/flashnews/andrej-karpathy-highlights-ai-integration-with-legacy-clis) [sources](https://isagentready.com/en/blog/build-for-agents-why-clis-are-the-new-distribution-channel) covering his statements, Karpathy's argument was:

1. **CLIs are legacy, and that's the point.** AI agents can natively use CLIs, combine them, and interact with them via the entire terminal toolkit. We spent 40 years hiding the terminal from humans behind GUIs. In 2026, the most advanced technology needs the terminal again.

2. **The Polymarket demo.** Karpathy asked Claude Code to install the [Polymarket CLI](https://github.com/Polymarket/polymarket-cli) (a Rust-built prediction market tool) and "build any arbitrary dashboards or interfaces or logic." Three minutes later, Claude had a working terminal dashboard showing highest-volume markets with 24-hour price changes. No API integration code. No auth flow. No SDK setup.

3. **The GitHub CLI demo.** He then did the same with `gh` — Claude navigated repos, inspected issues, reviewed PRs, read code. All from the agent, all via CLI.

4. **The checklist for every product in 2026.** Karpathy laid out what every product builder should ask:
   - Are your docs exportable in markdown? LLMs read markdown, not JavaScript-rendered docs sites.
   - Have you written Skills for your product? On-demand instructions agents load when needed.
   - Do you have a CLI? The most universal agent interface.
   - Do you have an MCP server? (Listed last, not first.)

As [Paolo Perrone summarized](https://www.linkedin.com/posts/paoloperrone_andrej-karpathy-said-clis-are-the-most-exciting-activity-7436790278100967424-lGlO) Karpathy's position: "Agents don't need your fancy UI. They need a terminal."

### The Broader Context

This came alongside Karpathy's February 2026 statement that "programming has changed more in the last 2 months than in decades" — that AI coding agents "basically didn't work before December and basically work since." He described giving Claude Code a multi-step task (set up vLLM on a DGX Spark, build a video analysis dashboard, configure systemd services) and having it completed autonomously in 30 minutes. A weekend project compressed to a background task. This is the context in which CLIs matter — agents that can do real work need real tools, and CLIs are those tools.

---

## Joel Hooks: HATEOAS for CLIs and Agent-First Design {#joel-hooks}

Joel Hooks built [`joelclaw`](https://joelclaw.com/cli-design-for-ai-agents), a CLI that operates 35 Inngest functions, an always-on gateway, video transcription, email triage, and meeting analysis. His [CLI Design for AI Agents](https://joelclaw.com/cli-design-for-ai-agents) article (published February 19, 2026) defines the most sophisticated agent-first CLI protocol anyone has published. Five principles:

### Principle 1: JSON Always

No plain text. No tables. No ANSI color codes. No `--json` flag to opt in. JSON is the default and only format. Every command, every time. The agent never guesses what format it's getting.

> "Design CLIs for agents first, and humans get a perfectly usable tool for free — pipe through `jq`. Design for humans first, and agents get nothing."

### Principle 2: HATEOAS — Tell the Agent What to Do Next

This is the breakthrough. Every response includes `next_actions` — command templates the agent can run next. This is [Roy Fielding's HATEOAS constraint](https://en.wikipedia.org/wiki/HATEOAS) from REST, applied to CLIs. But where REST gives you links, Hooks gives you **forms** — hypermedia controls with typed inputs.

```json
{
  "ok": true,
  "command": "joelclaw send video/download",
  "result": { "event_id": "01KHF98SKZ7RE6HC2BH8PW2HB2", "status": "accepted" },
  "next_actions": [
    {
      "command": "joelclaw run <run-id>",
      "description": "Inspect the triggered run",
      "params": {
        "run-id": { "value": "01KHF98SKZ7RE6HC2BH8PW2HB2", "description": "Run ID (ULID)" }
      }
    },
    {
      "command": "joelclaw runs [--status <status>] [--count <count>]",
      "description": "List recent runs",
      "params": {
        "status": { "enum": ["COMPLETED", "FAILED", "RUNNING", "QUEUED", "CANCELLED"] },
        "count": { "default": 10 }
      }
    }
  ]
}
```

The `params` object carries metadata:
- `value` — pre-filled from context (the agent knows the exact ID to use)
- `enum` — valid choices (the agent picks from a closed set instead of hallucinating)
- `default` — what happens if omitted
- `description` — what this parameter means

The `next_actions` are **contextual** — they change based on what just happened. A failed command suggests different templates than a successful one. Errors include a `fix` field in plain language. The agent has everything it needs to self-recover without consulting documentation.

### Principle 3: Self-Documenting Command Tree

The root command (no arguments) returns the full command tree as JSON. One call and the agent knows everything available. No `--help` parsing. No man pages.

### Principle 4: Protect Context

Auto-limit lists with reasonable defaults. When truncated, point to full output via a file path. Show last 30 lines, not all 4,582. This is explicit context window discipline built into the CLI contract.

### Principle 5: NDJSON for Temporal Data

For streaming/temporal operations, use Newline-Delimited JSON — one JSON object per line, same pattern as `docker events --format '{{json .}}'` and `kubectl get pods -w -o json`. The last line is always the HATEOAS envelope. Pipe-native, grep-able, `jq`-friendly.

This eliminates polling. Instead of five tool calls to follow a pipeline (`send` → `runs` → `runs` → `runs` → `run`), the agent runs `send --follow` and sees every step as it happens via NDJSON stream.

### The Anti-Patterns Table

| Don't | Do |
|-------|-----|
| Plain text output | JSON envelope |
| `--json` flag | JSON is the only format |
| Dump unbounded output | Truncate + file pointer |
| Static `--help` text | Self-documenting root command |
| `Error: something went wrong` | `{ ok: false, error: {...}, fix: "..." }` |
| Hardcoded literal next_actions | Templates with `params` |
| Poll for temporal data | Stream NDJSON |
| ANSI colors | JSON fields |

---

## Eric Holmes: The Composability Gap {#eric-holmes}

Eric Holmes published ["MCP is dead. Long live the CLI."](https://ejholmes.github.io/2026/02/28/mcp-is-dead-long-live-the-cli.html) on February 28, 2026. It became the most-shared post in the CLI vs. MCP debate. His argument is surgical:

### LLMs Don't Need a Special Protocol

> "LLMs are really good at using command-line tools. They've been trained on millions of man pages, Stack Overflow answers, and GitHub repos full of shell scripts. When I tell Claude to use `gh pr view 123`, it just works."

MCP promised a cleaner interface, but Holmes found himself writing the same documentation anyway — what each tool does, what parameters it accepts, when to use it. The LLM didn't need a new protocol.

### Debugging Is Transparent

> "When Claude does something unexpected with Jira, I can run the same `jira issue view` command and see exactly what it saw. Same input, same output, no mystery. With MCP, the tool only exists inside the LLM conversation."

### The Terraform Example

The composability argument, distilled to one example:

```bash
terraform show -json plan.out | jq '[.resource_changes[] | select(.change.actions[0] == "no-op" | not)] | length'
```

With MCP, you either dump the entire Terraform plan into the context window (expensive, often impossible) or build custom filtering into the MCP server itself. The CLI approach uses tools that already exist and that both humans and agents understand.

### Auth Already Works

`aws` uses profiles and SSO. `gh` uses `gh auth login`. `kubectl` uses kubeconfig. These are battle-tested auth flows that work the same whether a human or an agent is driving. No MCP-specific auth troubleshooting required.

### No Moving Parts

MCP servers are processes that need to start up, stay running, and not silently hang. Holmes reports losing count of the times he's restarted Claude Code because an MCP server didn't initialize. CLIs are binaries on disk — no background processes, no state, no initialization dance.

### His Plea to Builders

> "If you're a company investing in an MCP server but you don't have an official CLI, stop and rethink what you're doing. Ship a good API, then ship a good CLI. The agents will figure it out."

---

## The Pre-Filtering Advantage {#pre-filtering}

This is the most technically consequential argument for CLI over MCP, and multiple sources converge on it.

### The Problem: MCP is Eager, CLI is Lazy

As [Karan Sharma wrote](https://mrkaran.dev/posts/plain-text-future/) (January 31, 2026):

> "The current approach to agent tooling often involves dumping massive JSON schemas into the context window. Connecting to a standard MCP server might load dozens of tool definitions, involving thousands of tokens describing every possible parameter, before the user has even asked a question. This is 'eager loading,' and it is expensive."

> "A CLI-driven approach is 'lazy loaded.' The agent starts with zero knowledge of the tool's internals. It burns zero tokens on schema definitions. Only when tasked with a specific goal does it invoke `--help`. It retrieves exactly the information needed to construct the command, executes it, and parses the result."

### The Numbers

According to [Jannik Reinhard](https://jannikreinhard.com/2026/02/22/why-cli-tools-are-beating-mcp-for-ai-agents/), a standard GitHub MCP server dumps ~55,000 tokens into the context window before the agent does anything. [Phil at Rentier Digital](https://medium.com/@rentierdigital/why-clis-beat-mcp-for-ai-agents-and-how-to-build-your-own-cli-army-6c27b0aec969) found MCP servers "ate 40% of my context window."

[Manveer Chawla's framework](https://manveerc.substack.com/p/mcp-vs-cli-ai-agents) (March 8, 2026) quantified it:

> "The CLI crowd correctly identifies that connecting a standard GitHub MCP server dumps ~55,000 tokens into context before the agent does anything useful. They correctly note that MCP tools don't chain. You can't pipe one into another. They correctly observe that even small models are already RL-trained on shell commands, while MCP schemas carry zero training data advantage."

### How Pipes Pre-Filter

The Unix pipe is the pre-filtering primitive. Consider Steinberger's weather example:

**MCP approach:** Agent calls weather MCP → gets 50 fields for London → all 50 fields enter context window → agent extracts "is it raining."

**CLI approach:** `weather london --format json | jq '.precipitation.is_raining'` → only the boolean enters the context window.

Scale this to real workflows:

```bash
# Find all failing CI jobs in the last 24 hours, extract just names and error messages
gh run list --status failure --json name,conclusion,headBranch --limit 50 \
  | jq '[.[] | {name, branch: .headBranch}]'

# Get Terraform drift — only resources that changed, not the entire state
terraform show -json plan.out \
  | jq '[.resource_changes[] | select(.change.actions != ["no-op"]) | {address, actions: .change.actions}]'

# Find the 5 most-commented open issues across all repos
gh search issues --state open --sort comments --limit 5 --json title,url,comments \
  | jq '.[] | "\(.comments) comments: \(.title) — \(.url)"'
```

Each pipeline narrows data **before** it enters the context window. The agent's working memory receives signal, not noise. With MCP, the agent receives everything and must spend tokens parsing and discarding irrelevant fields.

### The xargs Pattern

For batch operations, `xargs` lets agents process items in parallel without loading everything into context:

```bash
# Review the 3 most recent PRs
gh pr list --limit 3 --json number -q '.[].number' \
  | xargs -I{} gh pr view {} --json title,body,reviews

# Delete all completed workflow runs older than 30 days
gh run list --status completed --json databaseId --created "<2026-02-07" \
  | jq '.[].databaseId' \
  | xargs -I{} gh run delete {}
```

MCP has no equivalent to this pattern. Each operation would be a separate tool call, each response fully loaded into context.

---

## The CLI Army Pattern {#cli-army}

Multiple sources describe the same pattern independently: build focused, single-purpose CLI tools and compose them.

### Steinberger's ~10 Tools

As documented above, Steinberger built roughly 10 CLI tools (`wacli`, `imsg`, `gogcli`, `peekaboo`, `ordercli`, etc.) that each do one thing. The agent orchestrates them through bash. Each tool would have required a separate MCP server with its own initialization, auth flow, schema loading, and background process. Instead, they're binaries on disk invoked on demand.

### Hooks' joelclaw

Joel Hooks runs 35 Inngest functions through a single `joelclaw` CLI. The CLI is the control plane for video transcription, email triage, meeting analysis, and system monitoring. One binary replaces what would be multiple MCP servers.

### The Pattern Formalized

From [Nikola Balic's "Designing CLI Tools for AI Agents"](http://nibzard.com/ai-native/) (February 24, 2026):

> "The 'API' an agent uses is the command surface + help text + output shapes + exit codes."

Nine principles for agent-native CLIs:
1. Treat interfaces as contracts (`--help` is a contract, not documentation)
2. JSON-first output (machine-readable by default)
3. Deterministic exit codes
4. Structured errors with remediation steps
5. Self-describing schemas
6. Context-aware output limits
7. Composable with pipes
8. Idempotent operations where possible
9. Explicit dry-run modes for safety

### Google's Agent-First CLI

[Justin Poehnelt](https://justin.poehnelt.com/posts/rewrite-your-cli-for-ai-agents/) (Senior Developer Relations at Google, March 4, 2026) built a CLI for Google Workspace with agents as the primary consumer from day one:

> "These are different enough that retrofitting a human-first CLI for agents is a losing bet. Agent DX optimizes for predictability and defense-in-depth. Human DX optimizes for discoverability and forgiveness."

He ships "Agent Skills" alongside the CLI — on-demand instruction files agents load when needed, rather than baking documentation into the context window.

---

## The Academic Angle: Unix Philosophy Meets Agentic AI {#academic}

An [arXiv paper](https://arxiv.org/pdf/2601.11672) by Deepak Babu Piskala ("From 'Everything is a File' to 'Files Are All You Need': How Unix Philosophy Informs the Design of Agentic AI Systems") traces how the same design principle — collapsing diverse resources into uniform interfaces — keeps solving the same problems at different scales:

> "In the early 1970s, Ken Thompson and Dennis Ritchie faced a practical problem at Bell Labs. The computing systems of the day required programmers to learn different interfaces for different resources… Their solution was elegant in its simplicity: represent everything—devices, processes, network connections, data—as files."

The paper argues that designing agents around file-like abstractions and code as the action language offers a path to more maintainable, auditable systems — the same conclusion practitioners are reaching empirically.

A separate [paper from OpenDev](https://arxiv.org/html/2603.05344v1) (March 5, 2026) presents a terminal-native AI coding agent architecture with "lazy tool discovery" — tools are only loaded into context when needed, not pre-declared like MCP schemas. This mirrors the CLI lazy-loading pattern exactly.

---

## Key Takeaways

1. **MCP's fatal flaw is eager loading.** Pre-exporting all tool schemas into the context window is the wrong default. A GitHub MCP server burns ~55,000 tokens before doing anything. CLIs burn zero tokens until invoked.

2. **Composability is non-negotiable for real work.** Unix pipes let agents chain operations (`grep | jq | xargs`), pre-filter data before it enters the context window, and build complex workflows without custom orchestration. MCP calls are isolated — you can't pipe one into another.

3. **LLMs are natively trained on CLI usage.** Millions of man pages, Stack Overflow answers, and shell scripts in training data mean models are already fluent in bash. MCP schemas have zero training data advantage.

4. **The HATEOAS pattern is the missing piece.** Joel Hooks' `next_actions` with typed `params` turns CLIs into self-navigable hypermedia. The agent always knows what to do next without consulting external documentation.

5. **The ~10 CLI tools pattern beats multiple MCP servers.** Steinberger proved this at 289K-star scale. Single-purpose CLIs compose better, debug easier, and carry no runtime overhead.

6. **MCP's real contribution was cultural, not technical.** As Steinberger said: "The best thing that came out of MCP is it made companies rethink to open up more APIs." The protocol was a forcing function for better tooling, even if the protocol itself isn't the right answer.

7. **The MCP counterarguments have merit in specific contexts.** Multi-tenant enterprise SaaS, non-developer users, OAuth discovery, and services without CLIs are legitimate MCP use cases. The debate isn't absolute — it's about defaults. As [Manveer Chawla's framework](https://manveerc.substack.com/p/mcp-vs-cli-ai-agents) puts it: "make the transport decision per tool integration, not per system."

---

## Predictions

1. **By end of 2026, every major SaaS product will ship a CLI as a first-class agent interface.** The ones that already have CLIs (GitHub, AWS, Vercel, Supabase) will dominate agent workflows. Those without will scramble.

2. **The HATEOAS-for-CLIs pattern will become a de facto standard.** Joel Hooks' `next_actions` with `params` is too obviously correct not to spread. Expect CLI frameworks (Effect CLI, oclif, Commander.js) to add first-class support.

3. **MCP will survive but narrow.** It will find its niche in enterprise contexts where OAuth discovery and multi-tenant auth matter. For individual developers and local agent workflows, CLI will be the default.

4. **"Agent DX" will become a product discipline.** Companies will hire for it. CLIs will be designed for agents first, humans second. Markdown docs, agent skills, and JSON-only output will be baseline expectations.

5. **Context window efficiency will be the primary metric for tool design.** Not developer experience, not feature completeness — how many tokens does your tool cost the agent? Pre-filtering via pipes will be the optimization primitive.

---

## Sources

| Source | Author | Date | URL |
|--------|--------|------|-----|
| "MCP is dead. Long live the CLI." | Eric Holmes | Feb 28, 2026 | [ejholmes.github.io](https://ejholmes.github.io/2026/02/28/mcp-is-dead-long-live-the-cli.html) |
| "CLI Design for AI Agents" | Joel Hooks | Feb 19, 2026 | [joelclaw.com](https://joelclaw.com/cli-design-for-ai-agents) |
| OpenClaw/Steinberger interview transcript | Luke Tucker | Jan 2026 | [luketucker.com](https://luketucker.com/openclaw-kilocode-and-why-cli-mcp/) |
| "Why CLIs Beat MCP for AI Agents" | Phil, Rentier Digital | Feb 17, 2026 | [Medium](https://medium.com/@rentierdigital/why-clis-beat-mcp-for-ai-agents-and-how-to-build-your-own-cli-army-6c27b0aec969) |
| Karpathy on CLIs as legacy tech | Andrej Karpathy | Feb 24, 2026 | [blockchain.news summary](https://blockchain.news/flashnews/andrej-karpathy-highlights-ai-integration-with-legacy-clis) |
| "CLIs are the New AI Interfaces" | Karan Sharma | Jan 31, 2026 | [mrkaran.dev](https://mrkaran.dev/posts/plain-text-future/) |
| "Peekaboo 2.0 – Free the CLI from its MCP shackles" | Peter Steinberger | Jul 3, 2025 | [steipete.me](https://steipete.me/posts/2025/peekaboo-2-freeing-the-cli-from-its-mcp-shackles) |
| Steinberger's Homebrew tap (CLI inventory) | Peter Steinberger | — | [github.com/steipete/homebrew-tap](https://github.com/steipete/homebrew-tap) |
| "You Need to Rewrite Your CLI for AI Agents" | Justin Poehnelt (Google) | Mar 4, 2026 | [justin.poehnelt.com](https://justin.poehnelt.com/posts/rewrite-your-cli-for-ai-agents/) |
| "Designing CLI Tools for AI Agents" | Nikola Balic | Feb 24, 2026 | [nibzard.com](http://nibzard.com/ai-native/) |
| "MCP Isn't Dead. We're Just Early." | Matthew Hall | Mar 2026 | [matthewhall.com](https://matthewhall.com/posts/mcp-isnt-dead-were-just-early/) |
| "MCP vs. CLI for AI agents" decision framework | Manveer Chawla | Mar 8, 2026 | [manveerc.substack.com](https://manveerc.substack.com/p/mcp-vs-cli-ai-agents) |
| "Build for Agents: Why CLIs Are the New Distribution Channel" | Bart Waardenburg | Mar 5, 2026 | [isagentready.com](https://isagentready.com/en/blog/build-for-agents-why-clis-are-the-new-distribution-channel) |
| "Why CLI Tools Are Beating MCP for AI Agents" | Jannik Reinhard | Feb 22, 2026 | [jannikreinhard.com](https://jannikreinhard.com/2026/02/22/why-cli-tools-are-beating-mcp-for-ai-agents/) |
| arXiv: "From 'Everything is a File' to 'Files Are All You Need'" | Deepak Babu Piskala | Jan 2026 | [arxiv.org](https://arxiv.org/pdf/2601.11672) |
| arXiv: "Building AI Coding Agents for the Terminal" | Nghi D. Q. Bui | Mar 5, 2026 | [arxiv.org](https://arxiv.org/html/2603.05344v1) |
| "Writing CLI Tools That AI Agents Actually Want to Use" | dev.to | Mar 2026 | [dev.to](https://dev.to/uenyioha/writing-cli-tools-that-ai-agents-actually-want-to-use-39no) |
| Polymarket CLI (Karpathy demo subject) | Polymarket | Feb 24, 2026 | [github.com](https://github.com/Polymarket/polymarket-cli) |
| "The PM's Guide to Agent Distribution" | Aakash Gupta | Mar 7, 2026 | [news.aakashg.com](https://www.news.aakashg.com/p/master-ai-agent-distribution-channel) |
| "Replace MCP With CLI" | Cobus Greyling | Feb 13, 2026 | [Medium](https://office.qz.com/replace-mcp-with-cli-the-best-ai-agent-interface-already-exists-bcbb8094cff8) |
