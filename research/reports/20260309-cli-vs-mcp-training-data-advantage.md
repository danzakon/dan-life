---
id: 20260309-RS-004
date: 2026-03-09
category: Research Report
content-status: raw
---

# The CLI Advantage: Why AI Models Are Fluent in Shell but Fumble MCP

---

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [Background](#background)
3. [The Training Data Chasm](#the-training-data-chasm)
4. [The Zero-Shot CLI Advantage](#the-zero-shot-cli-advantage)
5. [Benchmarks: Shell Access vs. Tool Schemas](#benchmarks-shell-access-vs-tool-schemas)
6. [The MCP Tax: Context Windows Under Siege](#the-mcp-tax-context-windows-under-siege)
7. [Google's gws: The Architecture That Proved the Point](#googles-gws-the-architecture-that-proved-the-point)
8. [The Agent-Native CLI Movement](#the-agent-native-cli-movement)
9. [Key Takeaways](#key-takeaways)
10. [Predictions](#predictions)

---

## Executive Summary

LLMs are dramatically better at using CLI tools than MCP schemas, and the reason is embarrassingly simple: training data. Shell commands, bash scripts, and CLI invocations are among the most heavily represented code patterns in every major pretraining corpus — The Stack alone indexes shell as one of its 30 core programming languages across 3.1 TB of permissively licensed code. MCP, launched by Anthropic in November 2024, has effectively zero representation in any model's training data. The result is a measurable reliability gap: agents make fewer errors, use fewer tokens, and complete tasks faster when given a shell instead of a JSON-RPC schema catalog.

This isn't just a training data curiosity — it's reshaping how companies ship tools for the AI agent era. Google deliberately deleted a working MCP server from its Workspace CLI two days after launch. OpenClaw's creator called MCP "a crutch." Andrej Karpathy called CLIs "super exciting precisely because they are a legacy technology." A growing ecosystem of tools — CLIHub, mcp2cli, clime — now exists solely to convert MCP servers back into CLIs. The industry is learning that the best AI agent protocol was invented in 1971.

---

## Background

### What is MCP?

The Model Context Protocol (MCP), open-sourced by Anthropic in November 2024, defines a standard way for AI agents to discover and invoke external tools. An MCP server exposes a catalog of tools as JSON schemas — parameter names, types, descriptions, return formats — which get loaded into the agent's context window at session start. The agent then makes structured JSON-RPC calls to execute tools.

Adoption was rapid: OpenAI, Google DeepMind, and Microsoft all added MCP support. Over 13,000 MCP servers appeared on GitHub in 2025. SDKs shipped for every major language. MCP won the standards battle.

### What is CLI tool use?

CLI tool use is simpler. Give an agent shell access. Let it run commands — `git status`, `curl`, `docker ps`, `npm install` — exactly as a human developer would. The agent constructs command strings from its training knowledge, reads stdout/stderr, and iterates. No schema catalog. No JSON-RPC. Just text in, text out, the Unix way.

### The core question

If MCP standardizes everything, why are practitioners increasingly reverting to raw shell access? The answer sits at the intersection of training data economics, context window engineering, and a 50-year-old design philosophy that accidentally built the perfect AI agent interface.

---

## The Training Data Chasm

### Shell commands are everywhere in pretraining data

Every major LLM pretraining corpus is saturated with shell content:

- **The Stack** (BigCode, 2022): 3.1 TB of permissively licensed source code across 30 programming languages. Shell is one of them — alongside Dockerfile, Makefile, and PowerShell — meaning billions of tokens of bash scripts, shell one-liners, and CLI invocations are baked into the training signal. According to [The Stack paper](https://huggingface.co/datasets/bigcode/admin/resolve/1d235c08e0ec5fa485b8bccc93b2c483d54beb0f/The_Stack.pdf), the dataset includes shell scripts, Dockerfiles (which are essentially CLI invocation sequences), and Makefiles (which are CLI orchestration files).

- **The Stack v2** (BigCode, 2024): Expanded to include GitHub issues, pull requests, and Jupyter notebooks — all of which contain massive amounts of CLI commands embedded in markdown, documentation, and code comments.

- **Stack Overflow**: The Unix & Linux Stack Exchange alone contains hundreds of thousands of answered questions about bash, shell scripting, and CLI tool usage. These Q&A pairs, processed into training data by [EleutherAI's stackexchange-dataset tools](https://github.com/EleutherAI/stackexchange-dataset), teach models not just command syntax but *when* and *why* to use specific flags and patterns.

- **GitHub READMEs and documentation**: Nearly every software project includes CLI installation instructions, usage examples, and troubleshooting commands. This is incidental training data — models learn CLI fluency as a side effect of learning to read documentation.

- **OpenCoder** (2024): The [OpenCoder paper](https://aclanthology.org/2025.acl-long.1591.pdf) (Fudan/NJU/CASIA) documented their data pipeline for training top-tier code LLMs, finding that language-specific filtering rules and high-quality data curation were the key ingredients — and shell/bash content was explicitly included as a core language.

### MCP schemas have zero training data

MCP was released in November 2024. No model trained before that date has seen a single MCP schema. Models released in 2025 and early 2026 may have minimal MCP exposure from the ~15 months of GitHub activity since launch, but this is negligible compared to decades of accumulated shell content.

The asymmetry is stark:

| Content Type | Approximate Training Representation | First Appeared |
|---|---|---|
| Bash/shell scripts | Billions of tokens across all major corpora | 1971 (Unix shell) |
| CLI tool documentation | Hundreds of millions of tokens (READMEs, man pages, Stack Overflow) | 1970s onward |
| Dockerfiles (CLI sequences) | Tens of millions of files on GitHub | 2013 |
| Makefiles (CLI orchestration) | Tens of millions of files across open source | 1976 |
| MCP tool schemas | Negligible — ~15 months of GitHub repos | November 2024 |
| MCP invocation examples | Near-zero — most are in blog posts, not training corpora | 2025 |

As [Manveer Chawla](https://manveerc.substack.com/p/mcp-vs-cli-ai-agents) put it: "even small models are already RL-trained on shell commands, while MCP schemas carry zero training data advantage."

### NVIDIA proved you can RL-train CLI fluency for novel tools

NVIDIA's January 2026 tutorial, ["How to Train an AI Agent for Command-Line Tasks with Synthetic Data and Reinforcement Learning"](https://developer.nvidia.com/blog/how-to-train-an-ai-agent-for-command-line-tasks-with-synthetic-data-and-reinforcement-learning/), demonstrated the pipeline explicitly. Using NeMo Data Designer to generate synthetic CLI training data and GRPO (Group Relative Policy Optimization) via NeMo Gym and Unsloth, they fine-tuned a Nemotron model to use the LangGraph CLI — a tool it had never seen in pretraining.

The key insight: even for *novel* CLI tools, the RL training loop works because the model already has deep structural knowledge of how CLIs work (flags, subcommands, JSON output, stdin/stdout). Teaching it a new CLI is a small delta on top of massive existing competence. Teaching it MCP from scratch requires learning both the protocol *and* the specific tool — a much larger lift.

---

## The Zero-Shot CLI Advantage

### Models can use tools they've never been explicitly taught

This is the phenomenon that makes CLI so powerful for agents: a model that has seen millions of `git` commands in training can use `git` without any schema, documentation, or instruction. It simply knows the interface.

[Karan Sharma](https://mrkaran.dev/posts/plain-text-future/) articulated it clearly: "When you give an agent access to a robust CLI, you don't need to define 50 separate function schemas. You give it a shell and a single instruction: 'Figure it out using `--help`.'"

Andrej Karpathy made the same point in his viral February 2026 post, which pulled nearly [2 million views](https://isagentready.com/en/blog/build-for-agents-why-clis-are-the-new-distribution-channel). He described CLIs as "super exciting precisely because they are a legacy technology" — meaning AI models like Claude and Codex can "natively install and interact" with any CLI tool through the terminal. His demo showed Claude installing the Polymarket CLI (a Rust binary distributed via npm), querying prediction markets, and building a dashboard — all zero-shot, no schema, no integration code.

The demo worked because of three properties that CLI tools inherit from Unix:

1. **Composition**: Pipes (`|`) let agents chain tools into workflows on the fly
2. **Structure**: `--json` flags provide deterministic, machine-readable output
3. **Discovery**: `--help` and man pages are self-describing — no hallucination needed

Peter Steinberger, creator of [OpenClaw](https://luketucker.com/openclaw-kilocode-and-why-cli-mcp/) (the AI agent framework with 190K+ GitHub stars), put it more bluntly:

> "MCP is a crutch. The best thing that came out of MCP is it made companies rethink to open up more APIs... Models are really good at using bash. If it's a CLI I can pipe grep, I can filter, I can do whatever I want."

His architecture uses ~10 focused CLI tools instead of MCP servers. The agent can send messages, manage emails, book flights, browse the web — all through bash.

### The MIT NL2SH research confirms the pattern

Researchers at [MIT CSAIL](https://arxiv.org/html/2502.06858v1) (Westenfelder et al., 2025) created a manually verified dataset of 600 natural-language-to-bash command pairs and a training set of 40,939 pairs — 441% and 135% larger than previous datasets respectively. Their work on "LLM-Supported Natural Language to Bash Translation" found that LLMs already perform remarkably well at translating natural language intent into executable bash commands, precisely because of the density of shell content in pretraining data. The challenge isn't capability — it's evaluation: existing heuristics for determining functional equivalence of bash commands were unreliable.

---

## Benchmarks: Shell Access vs. Tool Schemas

### Terminal-Bench 2.0: The gold standard for CLI agent evaluation

[Terminal-Bench 2.0](https://www.tbench.ai/leaderboard/terminal-bench/2.0) (Stanford/Laude Institute, 2026) is the definitive benchmark for evaluating AI agents on real-world command-line tasks. It consists of 89 carefully curated tasks in terminal environments — system administration, software engineering, scientific computing — where agents must "understand the shell environment and how to use its programs, as well as the state of the computer, including its filesystem and running processes."

Current leaderboard results (as of March 2026):

| Rank | Agent | Model | Accuracy |
|------|-------|-------|----------|
| 18 | Terminus 2 | GPT-5.3-Codex | 64.7% ± 2.7 |
| 22 | Terminus 2 | Claude Opus 4.6 | 62.9% ± 2.7 |
| 35 | Terminus 2 | Claude Opus 4.5 | 57.8% ± 2.5 |
| 36 | Terminus 2 | Gemini 3 Pro | 56.9% ± 2.5 |
| 39 | Terminus 2 | GPT-5.2 | 54.0% ± 2.9 |

These are frontier models scoring 55–65% on hard terminal tasks — demonstrating genuine CLI competence but also showing significant room for improvement. The benchmark maintains a deliberate 50% performance ceiling to remain relevant as models improve.

According to [Snorkel AI's analysis](https://snorkel.ai/blog/terminal-bench-2-0-raising-the-bar-for-ai-agent-evaluation/), Terminal-Bench 2.0 is "substantially more challenging than its predecessor" and "tasks now better represent the frontier challenges that distinguish truly capable agents from those that can only handle routine operations."

### SWE-bench: Shell tools power the best coding agents

[SWE-bench Verified](https://epoch.ai/benchmarks/swe-bench-verified) evaluates agents on resolving real GitHub issues. The top-performing agents — SWE-agent, OpenHands, Warp — all rely heavily on shell access to navigate codebases, run tests, apply patches, and validate fixes. [Warp scored 71% on SWE-bench Verified](https://www.warp.dev/blog/swe-bench-verified) using terminal-native tools.

The [OpenHands Index](https://www.linkedin.com/posts/openhands-ai_what-is-the-best-llm-for-agentic-software-activity-7422641917764632576-5f0b) goes further, evaluating across 5 task domains. The pattern is consistent: agents that interact through shell commands outperform those constrained to structured API calls.

### Mario Zechner's MCP vs CLI benchmark

[Mario Zechner](https://mariozechner.at/posts/2025-08-15-mcp-vs-cli/) built a direct comparison: same tools, same tasks, MCP server vs CLI invocation. His findings:

- "Just like a lot of meetings could have been emails, a lot of MCPs could have been CLI invocations."
- The GitHub MCP Server "reimplements functionality that's already available in the GitHub CLI" and "most often will lead to much worse results than just letting the agent run the command line tool directly."
- Both approaches *can* be efficient if carefully designed, but popular MCP servers tend to flood context with unnecessary output.

His [follow-up post](https://mariozechner.at/posts/2025-11-02-what-if-you-dont-need-mcp/) concluded: "In many situations, you don't need or even want an MCP server... Agents can run Bash and write code well. Bash and code are composable."

---

## The MCP Tax: Context Windows Under Siege

The most damaging practical problem with MCP is token economics. Every MCP server dumps its entire tool catalog into the agent's context window at session start. The numbers are brutal.

### The raw numbers

| Scenario | MCP Tokens | CLI Tokens | Savings |
|---|---|---|---|
| Session start (6 servers, 84 tools) | ~15,540 | ~300 | 98% |
| 1 tool call | ~15,570 | ~910 | 94% |
| 100 tool calls | ~18,540 | ~1,504 | 92% |

*Source: [Kan Yilmaz / CLIHub](https://kanyilmaz.me/2026/02/23/cli-vs-mcp.html)*

[Playwright MCP vs Playwright CLI](https://scrolltest.medium.com/playwright-mcp-burns-114k-tokens-per-test-the-new-cli-uses-27k-heres-when-to-use-each-65dabeaac7a0): 114K tokens per test vs 27K tokens — a 76% reduction. The author's agent started "hallucinating button names that didn't exist on the page" after 15 steps because "the context window was cooked."

The [GitHub MCP server ships with 93 tools](https://www.buildmvpfast.com/blog/mcp-hidden-cost-cli-agent-infrastructure-2026), burning ~55,000 tokens just loading tool definitions — half of GPT-4o's context window, gone before a single question.

[AgentPMT found](https://www.agentpmt.com/articles/thousands-of-mcp-tools-zero-context-left-the-bloat-tax-breaking-ai-agents) that three MCP servers (GitHub, Playwright, IDE integration) consumed 143,000 of a 200,000-token context window — 72% — before the agent read its first user message.

### Why CLI avoids this

CLI tools use lazy loading by design. The agent doesn't need to know every flag of every tool upfront. It discovers capabilities on demand via `--help`, reads only the output it needs, and pipes results without serializing everything through the context window. As [Karan Sharma](https://mrkaran.dev/posts/plain-text-future/) explained, this is "lazy vs. eager loading" — and eager loading is catastrophically expensive when you have dozens of tools.

### The academic evidence

Researchers at Queen's University published ["Model Context Protocol (MCP) Tool Descriptions Are Smelly!"](https://arxiv.org/html/2602.14878v2) (Hasan et al., 2026), finding that MCP tool descriptions suffer from quality problems analogous to code smells — poorly written descriptions, redundant parameters, missing context — that degrade agent performance. Their work on augmented MCP tool descriptions showed that fixing these "smells" improved agent efficiency, but the fundamental overhead of loading all schemas remained.

Separately, the [MCP-Zero paper](https://www.researchgate.net/publication/392336857_MCP-Zero_Proactive_Toolchain_Construction_for_LLM_Agents_from_Scratch) (Fei et al., 2025) introduced a framework where the LLM itself decides when and which tools to retrieve, rather than loading everything upfront — essentially rebuilding lazy loading at the protocol level. The fact that this is a research contribution tells you how broken the default MCP behavior is.

Anthropic themselves acknowledged the problem. Their engineering blog post ["Code execution with MCP: Building more efficient agents"](https://www.anthropic.com/engineering/code-execution-with-mcp) (November 2025) noted that "direct tool calls consume context for each definition and result" and proposed having agents "write code to call tools instead" — which is, essentially, admitting that shell-style code execution is more efficient than structured tool calling.

---

## Google's gws: The Architecture That Proved the Point

### What gws is

Google Workspace CLI (`gws`) is a Rust-based CLI that provides unified command-line access to Gmail, Google Drive, Calendar, Docs, Sheets, Slides, Chat, Admin, and every other Workspace API. Created by [Justin Poehnelt](https://justin.poehnelt.com/posts/rewrite-your-cli-for-ai-agents/), Senior Developer Relations Engineer at Google, it was built from day one for AI agent consumption.

Currently at v0.9.0 with ~42K weekly npm downloads and ~5,100 GitHub stars, `gws` carries the standard "not an officially supported Google product" disclaimer but sits under the official `googleworkspace` GitHub organization.

### The Discovery Service architecture

The most distinctive technical decision: `gws` doesn't ship a static list of commands. It reads [Google's Discovery Service](https://www.npmjs.com/package/@googleworkspace/cli) at runtime and builds its entire command surface dynamically. When Google adds a new API endpoint, `gws` picks it up automatically — no CLI update needed.

This is the inverse of MCP's approach. Instead of pre-loading a static schema catalog, `gws` constructs its interface from the live API surface. The command surface is always current, always complete, and never stale.

### The MCP deletion incident

The most revealing decision was what Google *removed*. According to a [forensic investigation published on DEV Community](https://dev.to/gys/not-everything-needs-mcp-what-google-workspace-cli-taught-us-about-ai-agent-architecture-2doe):

> "Google implemented a full MCP server, improved it, then deliberately deleted all 1,151 lines of it as a breaking change. Two days after launch."

The MCP server was built, tested, and then consciously removed. The CLI was the intended interface for AI agents all along.

### Design philosophy: Agent DX vs Human DX

Poehnelt's [blog post](https://justin.poehnelt.com/posts/rewrite-your-cli-for-ai-agents/) articulated the design philosophy clearly:

- **Human DX optimizes for discoverability and forgiveness** — extensive `--help` menus, loose input, typo suggestions
- **Agent DX optimizes for predictability and defense-in-depth** — raw JSON payloads instead of bespoke flags, deterministic output, safety rails against hallucinations

Key design decisions for agent consumption:
- **Raw JSON input over flags**: Agents prefer `--data '{"title": "Q1 Budget"}'` over 10 flat flags because JSON naturally handles nested structures
- **Structured JSON output by default**: Every command returns machine-parseable JSON
- **Schema introspection replaces documentation**: Commands describe themselves at runtime
- **`--dry-run` for safety**: Agents can preview destructive operations before executing
- **Response sanitization**: Output is cleaned to prevent prompt injection
- **40+ agent skills included**: Pre-built skill files that teach agents common workflows

As the [Better Stack guide](https://betterstack.com/community/guides/ai/cli-gws-ai-agents/) summarized: "Unlike traditional CLIs built around human usability, `gws` optimizes for what agents actually need: predictable, structured input and output, minimal token overhead, and an always-current command surface."

---

## The Agent-Native CLI Movement

Google isn't alone. A wave of companies and projects are shipping CLIs specifically for AI agent consumption.

### The converters: MCP-to-CLI tools

The existence of tools that convert MCP servers back into CLIs tells the whole story:

- **[CLIHub](https://github.com/thellimist/clihub)** (243 GitHub stars): "Turn any MCP server into a compiled CLI binary. One command. Designed for agents." Creator Kan Yilmaz [demonstrated 94% token savings](https://kanyilmaz.me/2026/02/23/cli-vs-mcp.html) across real-world scenarios. His LinkedIn post about it generated 130+ comments and 961 reactions.

- **[mcp2cli](https://github.com/knowsuchagency/mcp2cli)** (298 GitHub stars, created today — March 9, 2026): "Turn any MCP server or OpenAPI spec into a CLI — at runtime, with zero codegen. Save 96–99% of the tokens wasted on tool schemas every turn." Ships with an installable agent skill for Claude Code, Cursor, and Codex.

- **[clime](https://clime.sh/)**: "One CLI to find every CLI." A CLI registry with 845 CLIs indexed, built for agents and humans. Provides deterministic discovery, install, auth, and command mapping — essentially replacing the MCP discovery layer with a shell-native equivalent.

### Companies shipping agent-first CLIs

| Company/Project | CLI | Agent-First Features |
|---|---|---|
| Google | `gws` | Dynamic commands from Discovery Service, JSON I/O, 40+ skills, dry-run |
| Supabase | `supabase` CLI + [Agent Skills](https://www.blog.brightcoding.dev/2026/02/08/supabase-agent-skills-your-ai-powered-postgres-guide) | 8 performance skill categories, auto-discoverable by Claude/Cursor |
| Kiro (AWS) | [`kiro` CLI](https://kiro.dev/blog/introducing-kiro-cli/) | Agent mode, MCP support, steering, custom agents in terminal |
| klaw | [`klaw`](https://klaw.sh/) | kubectl for AI agents — single binary, Slack control, 300+ LLM models |
| OpenClaw | Various CLI tools | ~10 focused CLI tools replacing MCP entirely |
| Warp | Terminal + Agents | Terminal-native agent with [71% SWE-bench](https://www.warp.dev/blog/swe-bench-verified) |
| Playwright | `@playwright/cli` | [76% token reduction](https://scrolltest.medium.com/playwright-mcp-burns-114k-tokens-per-test-the-new-cli-uses-27k-heres-when-to-use-each-65dabeaac7a0) vs MCP |

### The "Is Agent Ready?" question

[Bart Waardenburg](https://isagentready.com/en/blog/build-for-agents-why-clis-are-the-new-distribution-channel) framed the Karpathy thesis as a business question: "If you have any kind of product or service, think: can agents access and use them? If the answer is no, you've got a problem. Your product is becoming invisible to what might be the fastest-growing distribution channel software has ever seen."

CLIs are the answer because they meet every requirement:
- **Installable**: `npm install -g`, `brew install`, `pip install`
- **Discoverable**: `--help` works everywhere
- **Composable**: Pipes, redirects, subshells
- **Structured**: `--json` or `--output json` flags
- **Authenticated**: Environment variables, config files, OAuth flows

---

## Key Takeaways

1. **The training data gap is the root cause.** CLI fluency is baked into every major LLM through billions of tokens of shell scripts, Stack Overflow answers, GitHub READMEs, Dockerfiles, and Makefiles accumulated over 50+ years. MCP has ~15 months of GitHub existence. This isn't a protocol design problem — it's a data problem that will take years to close, if it ever does.

2. **Token economics make MCP unsustainable at scale.** Loading 84 MCP tool schemas costs ~15,540 tokens at session start. The equivalent CLI setup costs ~300 tokens. That's a 98% tax on every conversation before a single tool is called. At production scale with multiple MCP servers, teams report 72% of context windows consumed by tool definitions alone.

3. **CLI tools are zero-shot learnable; MCP tools are not.** A model that has seen `git` in training can use `git` without any schema. A model that has never seen the `notion-search` MCP tool schema must learn it from the injected JSON — which competes with the actual task for context window space and introduces hallucination risk.

4. **Google's gws validates the architecture.** Building, testing, and then deliberately deleting an MCP server in favor of CLI is the strongest signal yet. Dynamic command generation from the Discovery Service is the correct pattern: always-current, zero-stale-schema, minimal token overhead.

5. **The converter ecosystem proves market demand.** CLIHub, mcp2cli, and clime exist because practitioners need to undo MCP overhead. When people build tools to escape your protocol, the protocol has a problem.

6. **NVIDIA's RL pipeline shows CLI tools can be taught faster.** Even for novel CLI tools with zero pretraining exposure, RL fine-tuning works because the model already understands CLI conventions (flags, subcommands, JSON output). The structural knowledge transfers. MCP has no such transfer learning advantage.

7. **The Unix philosophy was accidentally an AI protocol.** stdin/stdout, pipes, flags, structured output, man pages — these conventions, designed for human composability in the 1970s, happen to be exactly what AI agents need. MCP tried to reinvent this and ended up slower, fatter, and harder to learn.

---

## Predictions

1. **Within 12 months, every major SaaS company will ship an agent-optimized CLI alongside or instead of an MCP server.** Google gws is the template. Supabase, Vercel, Linear, Notion, and Stripe will follow. The CLI will be the primary agent interface; MCP will be an optional compatibility layer.

2. **MCP will survive but evolve into a lazy-loading protocol.** The current "dump everything at session start" approach is dead. MCP 2.0 (or whatever replaces it) will adopt the CLI pattern: lightweight tool listing at start, schema discovery on demand. Anthropic's Tool Search feature and MCP-Zero are early signals of this shift.

3. **"Agent DX" will become a standard product requirement.** Companies will evaluate their tools not on human usability but on agent usability — token efficiency, output predictability, composability, self-description. Products that aren't agent-accessible will lose distribution to those that are.

4. **CLI registries (clime, CLIHub) will become critical infrastructure.** Just as npm is the registry for JavaScript packages, a CLI registry for agent tools will emerge as a category winner. The first one to index 5,000+ CLIs with agent-optimized metadata wins.

5. **Training data will eventually close the gap — but CLIs will still win on token economics.** Even when MCP schemas are well-represented in training corpora (probably by late 2027), the fundamental context window tax remains. Lazy loading beats eager loading regardless of training data parity. The architectural advantage of CLI is permanent.

6. **The "MCP abstraction tax" will be quantified and tracked as a metric.** Teams will measure "tokens consumed by tool definitions as a percentage of total context" the way they currently track API latency. A new class of tooling will emerge to optimize this metric, and the winning approach will look more like CLI than MCP.

---

*Sources cited inline throughout. Research conducted March 9, 2026.*
