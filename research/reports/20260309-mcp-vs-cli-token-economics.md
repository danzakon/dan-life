---
id: 20260309-RS-001
date: 2026-03-09
category: Research Report
content-status: raw
---

# The MCP Token Tax: Why CLI Is 94% Cheaper and What It Means for Agent Architecture

---

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [Background](#background)
3. [The Hard Numbers: MCP Schema Token Costs](#the-hard-numbers-mcp-schema-token-costs)
4. [CLI vs MCP: Per-Request Token Comparison](#cli-vs-mcp-per-request-token-comparison)
5. [Scaling: Multiple MCP Servers in Production](#scaling-multiple-mcp-servers-in-production)
6. [Dollar Cost Implications at Scale](#dollar-cost-implications-at-scale)
7. [Emerging Solutions](#emerging-solutions)
8. [Case Studies with Hard Numbers](#case-studies-with-hard-numbers)
9. [Key Takeaways](#key-takeaways)
10. [Predictions](#predictions)

---

## Executive Summary

MCP (Model Context Protocol) has a crippling token economics problem that the ecosystem is only now reckoning with. The GitHub MCP server alone dumps ~42,000–55,000 tokens of tool schemas into context before an agent processes a single user message. Connect 3–6 MCP servers — a realistic production setup — and you're burning 60,000–150,000+ tokens on tool definitions that contribute nothing to task completion. That's 30–75% of a 200K context window, gone.

CLI-based tool calling achieves the same capabilities at 92–98% lower token cost. A 6-server, 84-tool setup costs ~15,500 tokens via MCP but only ~300 tokens via CLI at session start. The savings hold through extended sessions: at 100 tool calls, MCP accumulates ~18,540 tokens vs CLI's ~1,504 tokens. The reason is architectural — CLI lazy-loads tool details via `--help` on demand, while MCP front-loads every schema into context regardless of whether the agent needs it.

The ecosystem is responding. Anthropic shipped Tool Search (85% context reduction), Cloudflare invented Code Mode (99.9% reduction from 1.17M tokens to ~1,000), and tools like CLIHub and mcp2cli bridge the gap by converting MCP servers to CLIs at runtime. But the fundamental tension remains: MCP's design philosophy of "advertise everything upfront" is fundamentally at odds with how agents actually use tools.

---

## Background

### What Is MCP?

Model Context Protocol is Anthropic's open standard for connecting AI agents to external tools, APIs, and data sources. When an agent connects to an MCP server, the server advertises its full tool catalog — names, descriptions, JSON parameter schemas, return types — via a `tools/list` call. The MCP client then injects all of these schemas into the LLM's context window so the model knows what tools exist and how to call them.

### What Is CLI-Based Tool Calling?

CLI-based tool calling gives the agent shell access and lets it invoke command-line tools directly. Instead of loading tool schemas upfront, the agent discovers tools on demand: it sees a lightweight listing of available CLI tools (~50 tokens per tool name+description), and when it needs one, it runs `tool --help` to get the full interface (~600 tokens per tool). Then it executes the command.

### Why This Matters

Context windows are finite and expensive. Every token consumed by tool schemas is a token unavailable for reasoning, conversation history, code, or retrieved documents. At GPT-4o's pricing ($2.50/M input tokens), filling a 128K context window costs $0.32 per request. At Claude Sonnet's pricing ($3/M input tokens), 90,000 tokens of MCP schema overhead costs $0.27 per request. This is pure overhead — infrastructure metadata that the agent pays for on every single interaction.

---

## The Hard Numbers: MCP Schema Token Costs

### Per-Server Token Counts

Data from multiple independent sources converges on consistent numbers for how many tokens each MCP server's tool definitions consume:

| MCP Server | Tools | Schema Tokens | Source |
|---|---|---|---|
| GitHub MCP (official) | 93 | ~55,000 | [BuildMVPFast](https://www.buildmvpfast.com/blog/mcp-hidden-cost-cli-agent-infrastructure-2026) |
| GitHub MCP (official) | 93 | ~42,000 | [Nebula/DEV Community](https://dev.to/nebulagg/mcp-tool-overload-why-more-tools-make-your-agent-worse-5a49) |
| GitHub MCP (reduced) | 60 | ~33,000 | [Huawei SEP-1576 analysis](https://github.com/modelcontextprotocol/modelcontextprotocol/issues/1576) |
| GitHub Copilot MCP | 96 | ~55,000+ | [Tetrate](https://tetrate.io/learn/ai/mcp/tool-filtering-performance) |
| MySQL MCP | 106 | ~54,600 | [MCP Issue #1978](https://github.com/modelcontextprotocol/modelcontextprotocol/issues/1978) |
| Playwright MCP | — | ~114,000 per test | [Pramod Dutta](https://medium.com/@scrolltest/playwright-mcp-burns-114k-tokens-per-test-the-new-cli-uses-27k-heres-when-to-use-each-65dabeaac7a0) |
| Slack MCP | — | ~8,000 | [Nebula/DEV Community](https://dev.to/nebulagg/mcp-tool-overload-why-more-tools-make-your-agent-worse-5a49) |
| Notion MCP | — | ~6,500 | [Nebula/DEV Community](https://dev.to/nebulagg/mcp-tool-overload-why-more-tools-make-your-agent-worse-5a49) |
| Linear MCP | — | ~5,800 | [Nebula/DEV Community](https://dev.to/nebulagg/mcp-tool-overload-why-more-tools-make-your-agent-worse-5a49) |
| Postgres MCP | — | ~3,200 | [Nebula/DEV Community](https://dev.to/nebulagg/mcp-tool-overload-why-more-tools-make-your-agent-worse-5a49) |
| SigNoz MCP | 26 | ~15,000–20,000 | [Alyshia Ledlie](https://www.aledlie.com/reports/2026-01-19-signoz-mcp-context-optimization/) |
| Cloudflare API (full) | 2,500+ endpoints | ~1,170,000 | [Cloudflare Blog](https://blog.cloudflare.com/code-mode-mcp/) |
| Cloudflare API (alternate estimate) | 2,594 endpoints | ~2,000,000 | [Cloudflare Threads](https://www.threads.com/@cloudflare/post/DU-4CCODspY/) |

### Per-Tool Average

The data consistently shows each individual tool definition runs **300–600 tokens**, accounting for the name, description, and full parameter schema. According to [BuildMVPFast](https://www.buildmvpfast.com/blog/mcp-hidden-cost-cli-agent-infrastructure-2026): "A typical MCP server exposes 20 to 30 tools. Each tool definition runs 300-500 tokens once you account for the name, description, and parameter schema."

Some tools are far heavier. The [SigNoz MCP analysis](https://www.aledlie.com/reports/2026-01-19-signoz-mcp-context-optimization/) found three tools (`signoz_create_dashboard`, `signoz_update_dashboard`, `signoz_execute_builder_query`) alone accounted for ~11,500 tokens out of 15,000–20,000 total — nearly 60% of the server's schema cost from just 3 of 26 tools.

### The 96% Waste Problem

[AgentPMT](https://www.agentpmt.com/articles/mcp-servers-waste-96-of-agent-context-on-tool-definitions) conducted a quantitative study loading 74 tools onto an MCP server: **46,568 tokens consumed** before the agent read a single user message. That's over 156,000 characters of JSON. Most sessions use 2–5 tools. The other 69+ tool schemas sit in context doing nothing but burning tokens and degrading attention.

---

## CLI vs MCP: Per-Request Token Comparison

[Kan Yilmaz](https://kanyilmaz.me/2026/02/23/cli-vs-mcp.html) (creator of CLIHub) published the most rigorous side-by-side comparison. Setup: 6 MCP servers, 14 tools each, 84 tools total — the same capabilities exposed via both protocols.

### Session Start Cost

| Approach | What Loads | Tokens |
|---|---|---|
| **MCP** | Full JSON schema for all 84 tools | ~15,540 |
| **CLI** | Lightweight name+location listing for 6 tools | ~300 |
| **Savings** | | **98%** |

MCP loads ~185 tokens per tool × 84 tools. CLI loads ~50 tokens per tool × 6 top-level tools (grouped by server).

### Cumulative Cost Over a Session

| Tools Used | MCP Tokens | CLI Tokens | Savings |
|---|---|---|---|
| Session start only | ~15,540 | ~300 | 98% |
| 1 tool call | ~15,570 | ~910 | 94% |
| 10 tool calls | ~15,840 | ~964 | 94% |
| 100 tool calls | ~18,540 | ~1,504 | 92% |

CLI's cost grows slowly because `--help` output (~600 tokens for 14 tools in one server) is fetched once per server, then cached in conversation context. MCP's cost is front-loaded and fixed — you pay for all 84 tools whether you use 1 or 84.

### Playwright: A Real-World Head-to-Head

[Pramod Dutta](https://medium.com/@scrolltest/playwright-mcp-burns-114k-tokens-per-test-the-new-cli-uses-27k-heres-when-to-use-each-65dabeaac7a0) ran both Playwright MCP and Playwright CLI on the same login flow test:

- **Playwright MCP**: ~114,000 tokens per test
- **Playwright CLI**: ~27,000 tokens per test
- **Savings**: 76%

The difference: MCP streams full accessibility tree snapshots and tool schemas into context on every turn. CLI saves page state to disk and the agent reads only what it needs.

### mcp2cli: Runtime MCP-to-CLI Conversion

[mcp2cli](https://github.com/knowsuchagency/mcp2cli) (launched today, 298 GitHub stars) converts any MCP server into a CLI at runtime with zero codegen. Its token measurements using cl100k_base tokenizer:

- **30 tools over 15 turns**: 96% savings vs native MCP
- **120 tools over 25 turns**: 99% savings vs native MCP
- Per-tool listing: ~16 tokens/tool via `--list`
- Full tool help: ~120 tokens, fetched once via `--help`

From the [Hacker News launch](https://news.ycombinator.com/item?id=47305149): "Every MCP server injects its full tool schemas into context on every turn — 30 tools costs ~3,600 tokens/turn whether the model uses them or not. Over 25 turns with 120 tools, that's 362,000 tokens just for schemas."

---

## Scaling: Multiple MCP Servers in Production

### The Combinatorial Explosion

This is where MCP's design truly breaks down. Real production agents don't connect to one MCP server — they connect to many.

From [AgentPMT](https://www.agentpmt.com/articles/thousands-of-mcp-tools-zero-context-left-the-bloat-tax-breaking-ai-agents): "Three MCP servers — GitHub, Playwright, an IDE integration — consumed 143,000 of a 200,000-token context window before an agent read its first user message. Seventy-two percent of the model's working memory, gone on tool descriptions it mostly never touched."

### Realistic Multi-Server Configurations

| Configuration | Servers | Est. Total Tools | Est. Schema Tokens | % of 200K Context |
|---|---|---|---|---|
| Dev agent (GitHub + DB + Slack) | 3 | ~130 | ~66,200 | 33% |
| Product agent (GitHub + Slack + Notion + Linear + Jira) | 5 | ~180 | ~117,300 | 59% |
| Full-stack agent (all of the above + Playwright + Stripe) | 7 | ~230+ | ~150,000+ | 75%+ |
| Enterprise agent (10+ integrations) | 10+ | ~300+ | ~200,000+ | 100%+ |

Based on per-server numbers: GitHub (~55K), Slack (~8K), Notion (~6.5K), Linear (~5.8K), Postgres (~3.2K), Playwright (~30K+ for schemas alone).

### The Hard Wall

[AgentPMT's scaling analysis](https://www.agentpmt.com/articles/mcp-servers-waste-96-of-agent-context-on-tool-definitions) projects that standard MCP hits a hard wall at approximately **380 tools**, where tool schemas alone exceed a 200,000-token context window:

| Tool Count | Standard MCP Tokens | DynamicMCP Tokens | Savings |
|---|---|---|---|
| 74 | 46,568 | 1,688 | 96.4% |
| 100 | ~60,311 | 1,688 | 97.2% |
| 200 | ~113,173 | 1,688 | 98.5% |
| 500 | ~271,757 | 1,688 | 99.4% |
| 1,000 | ~536,065 | 1,688 | 99.7% |

### Accuracy Degradation

It's not just about cost — tool overload actively degrades agent performance. From [Nebula's benchmarks](https://dev.to/nebulagg/mcp-tool-overload-why-more-tools-make-your-agent-worse-5a49):

- **Focused toolset (4 tools)**: ~95% correct tool selection
- **Full MCP toolset (46 tools)**: ~71% correct tool selection
- **24-point accuracy gap** caused purely by context bloat

The same article cites three mechanisms: attention dilution across large context, tool collision between semantically similar tools, and prompt budget starvation that forces shorter system prompts.

---

## Dollar Cost Implications at Scale

### Cost Per Request

Using Claude Sonnet pricing ($3/M input tokens):

| Configuration | Schema Tokens | Cost per Request | Daily Cost (1K req) | Monthly Cost (30K req) |
|---|---|---|---|---|
| 6 MCP servers, all tools loaded | 90,000 | $0.27 | $270 | **$8,100** |
| 6 MCP servers, progressive disclosure | 2,000 | $0.006 | $6 | **$180** |
| CLI only | ~500 | $0.0015 | $1.50 | **$45** |
| Hybrid (MCP discovery + CLI execution) | ~1,500 | $0.0045 | $4.50 | **$135** |

Source: [BuildMVPFast](https://www.buildmvpfast.com/blog/mcp-hidden-cost-cli-agent-infrastructure-2026)

### Scaling to Expensive Models

On Claude Opus ($15/M input tokens), from the same source: "that naive MCP setup costs $40,500 per month in schema overhead alone."

### The Full Context Window Cost

From [MyEngineeringPath's Token Budgeting Guide](https://myengineeringpath.dev/genai-engineer/context-windows/): "At GPT-4o's input pricing of $2.50 per million tokens, filling a 128K context window costs $0.32 per request. Run that 10,000 times a day and you are spending $3,200 daily — $96,000 per month — on input tokens alone."

MCP schema overhead doesn't just cost its own tokens — it pushes the overall context fill rate higher, accelerating how fast you hit these total-cost thresholds.

### Intermediate Results Compound the Problem

Tool responses flow through the context window too. According to [Anthropic's own engineering blog](https://www.anthropic.com/engineering/code-execution-with-mcp), a two-hour meeting transcript flowing through the model twice consumes an additional 50,000 tokens with direct tool calls. A database query might return 50,000 tokens of data when the agent only needs five rows.

---

## Emerging Solutions

### 1. Anthropic's Tool Search (85% Reduction)

Anthropic shipped [MCP Tool Search](https://www.anthropic.com/engineering/advanced-tool-use) in Claude Code v2.1.7 (January 2026). Instead of preloading all tool definitions, Claude loads a lightweight search index and fetches tool details on demand.

- **Automatic activation**: Triggers when MCP tools would consume >10% of context
- **Reported reduction**: 85% token reduction for large tool libraries
- **Real-world example**: 51K tokens down to 8.5K — a [46.9% reduction](https://medium.com/@joe.njenga/claude-code-just-cut-mcp-context-bloat-by-46-9-51k-tokens-down-to-8-5k-with-new-tool-search-ddf9e905f734) in one documented case
- **One user's experience**: "67,000 tokens gone, just from connecting four MCP servers" → fixed with Tool Search
- **Simon Willison** [endorsed it](https://www.atcyrus.com/stories/mcp-tool-search-claude-code-context-pollution-guide): "context pollution is why I rarely used MCP, now that it's solved there's no reason not to hook up dozens or even hundreds of MCPs"

Limitation: It still pulls full JSON Schema per tool when fetched. CLI's `--help` is cheaper. From [Kan Yilmaz's comparison](https://kanyilmaz.me/2026/02/23/cli-vs-mcp.html):

| Tools Used | MCP | Tool Search | CLI | CLI Savings vs TS |
|---|---|---|---|---|
| Session start | ~15,540 | ~500 | ~300 | 40% |
| 1 tool call | ~15,570 | ~3,530 | ~910 | 74% |
| 10 tool calls | ~15,840 | ~3,800 | ~964 | 75% |
| 100 tool calls | ~18,540 | ~12,500 | ~1,504 | 88% |

Tool Search is Anthropic-only. CLI works with any model.

### 2. OpenAI's Tool Search (Comparable Approach)

[OpenAI shipped tool search](https://developers.openai.com/api/docs/guides/tools-tool-search/) with `defer_loading: true` — similar lazy loading concept. When new tools are discovered, they're injected at the end of the context window to preserve cache. Works with namespaces and MCP servers.

### 3. Cloudflare's Code Mode (99.9% Reduction)

[Cloudflare's Code Mode](https://blog.cloudflare.com/code-mode-mcp/) is the most dramatic optimization documented to date. Their API has 2,500+ endpoints. Naive MCP: **1,170,000+ tokens**. Code Mode: **~1,000 tokens**.

The technique: instead of describing every operation as a separate tool, expose two tools — `search()` and `execute()`. The agent writes code against a typed SDK and executes it in a sandboxed Worker. The code acts as a compact plan. Token cost stays fixed regardless of how many API endpoints exist.

### 4. DynamicMCP / On-Demand Architecture (96% Reduction)

[AgentPMT's DynamicMCP](https://www.agentpmt.com/articles/mcp-servers-waste-96-of-agent-context-on-tool-definitions) replaces 74 individual tool schemas (46,568 tokens) with 4 meta-tools (1,688 tokens):
- Tool Search and Execution (600 tokens)
- Workflow Skills (700 tokens)
- Send Human Request (300 tokens)
- Report Tool Issue (88 tokens)

On-demand fetching costs 800–1,800 tokens per tool. Break-even at ~34 unique tools per session. Most sessions use 2–5 tools, so DynamicMCP wins overwhelmingly.

### 5. CLI Conversion Tools

**CLIHub** ([github.com/thellimist/clihub](https://github.com/thellimist/clihub)) — 592 stars. One command to generate a compiled Go CLI binary from any MCP server. Created by Kan Yilmaz, whose blog post documenting 94% savings went viral on LinkedIn (130+ comments).

**mcp2cli** ([github.com/knowsuchagency/mcp2cli](https://github.com/knowsuchagency/mcp2cli)) — 298 stars (launched today). Turns any MCP server or OpenAPI spec into a CLI at runtime with zero codegen. 96–99% token savings measured with cl100k_base.

**Philipp Schmid's MCP CLI** ([philschmid.de/mcp-cli](https://www.philschmid.de/mcp-cli)) — 3-subcommand architecture (`info`, `grep`, `call`), connection pooling daemon, tool filtering via `allowedTools`/`disabledTools`.

### 6. Schema-Level Optimizations

**JSON Schema $ref deduplication** — [Huawei researchers (SEP-1576)](https://github.com/modelcontextprotocol/modelcontextprotocol/issues/1576) found 65% of GitHub MCP tools share an identical `repo` field definition and 60% share `owner`. Schema deduplication via `$ref` could cut significant redundancy.

**Lazy tool hydration** — [MCP Issue #1978](https://github.com/modelcontextprotocol/modelcontextprotocol/issues/1978) proposes a `tools/get_schema` method for on-demand schema fetch and a `minimal` flag for `tools/list`. Reference implementation shows 91% savings (54,604 → 4,899 tokens for 106 tools).

**Description trimming** — Cutting verbose descriptions from ~340 tokens to ~47 tokens per tool. Example from the [DEV Community analysis](https://dev.to/nebulagg/mcp-tool-overload-why-more-tools-make-your-agent-worse-5a49): a GitHub `create_issue` description went from 340 tokens to 47 tokens — an 86% reduction — with zero loss in agent accuracy.

### 7. Proxy Filtering

**mcp-filter** — Used in the [SigNoz optimization case study](https://www.aledlie.com/reports/2026-01-19-signoz-mcp-context-optimization/) to wrap an MCP server and block the 3 heaviest tools (11,500 tokens). Combined with `ENABLE_TOOL_SEARCH=auto:5`, achieved 85%+ reduction.

### 8. Task-Specific Sub-Agents

From [Nebula's analysis](https://dev.to/nebulagg/mcp-tool-overload-why-more-tools-make-your-agent-worse-5a49): Instead of one agent with 50 tools, use an orchestrator that routes to sub-agents with 4–8 tools each. Total token cost per operation drops because you never load the full combined toolset into a single context window.

---

## Case Studies with Hard Numbers

### Case Study 1: Claude Code + 4 MCP Servers
**Source**: [Reddit user documented by Joe Njenga](https://medium.com/@joe.njenga/claude-code-just-cut-mcp-context-bloat-by-46-9-51k-tokens-down-to-8-5k-with-new-tool-search-ddf9e905f734)
- 4 MCP servers connected to Claude Code
- **67,000 tokens consumed** before typing a single prompt
- Claude Sonnet 4.5's 200K limit → 33% of context gone on tool definitions
- After enabling Tool Search: 51K → 8.5K tokens (83% reduction)

### Case Study 2: Björn Büdenbender's Claude Code Setup
**Source**: [AI Advances / Medium](https://ai.gopubby.com/mcp-tools-are-eating-82-of-your-context-window-the-10-minute-fix-for-claude-code-1619733d00dc)
- **82% of context window** consumed by MCP tool definitions before typing a word
- Fix: lazy-mcp tool, 10 minutes setup, claimed 99% token savings

### Case Study 3: SigNoz MCP Context Optimization
**Source**: [Alyshia Ledlie](https://www.aledlie.com/reports/2026-01-19-signoz-mcp-context-optimization/)
- SigNoz MCP: 26 tools, ~15,000–20,000 tokens at session start
- 3 heaviest tools accounted for ~11,500 tokens (58% of total)
- Fix: mcp-filter proxy + `ENABLE_TOOL_SEARCH=auto:5`
- Result: **85%+ reduction** in context consumption

### Case Study 4: Playwright MCP vs CLI
**Source**: [Pramod Dutta](https://medium.com/@scrolltest/playwright-mcp-burns-114k-tokens-per-test-the-new-cli-uses-27k-heres-when-to-use-each-65dabeaac7a0)
- Same login flow test, both approaches
- MCP: ~114,000 tokens per test (agent started hallucinating button names at step 15 due to context exhaustion)
- CLI: ~27,000 tokens per test
- **76% savings**, plus fewer hallucinations

### Case Study 5: Cloudflare API
**Source**: [Cloudflare Blog](https://blog.cloudflare.com/code-mode-mcp/)
- 2,500+ API endpoints
- Naive MCP: 1,170,000+ tokens (exceeds every production LLM context window)
- Code Mode: ~1,000 tokens (two tools: `search()` + `execute()`)
- **99.9% reduction**

### Case Study 6: Scott Spence's Claude Code Session
**Source**: [Cyrus / Connor Turland](https://www.atcyrus.com/stories/mcp-tool-search-claude-code-context-pollution-guide)
- Documented starting Claude Code and watching **66,000 tokens disappear** before typing anything
- Multiple MCP servers connected
- Problem severe enough that Simon Willison publicly stated context pollution was why he "rarely used MCP"

### Case Study 7: CLIHub Production Benchmarks
**Source**: [Kan Yilmaz / Reddit](https://www.reddit.com/r/AI_Agents/comments/1rei6km/i_made_mcps_94_cheaper_by_generating_clis_from/)
- 6 MCP servers, 14 tools each, 84 tools total
- MCP: ~15,540 tokens at session start
- CLI: ~300 tokens at session start
- **94% cheaper** across full sessions
- Task completion: CLI achieved 28% higher task completion score with same token count
- Token Efficiency Score: CLI 202 vs MCP 152 (33% efficiency advantage)

---

## Key Takeaways

1. **MCP's design is fundamentally token-hostile.** The `tools/list` mechanism dumps every schema into context on connection. This isn't a bug — it's how MCP was designed. The protocol treats the context window as a catalog page rather than a scarce resource.

2. **CLI is 92–98% cheaper for the same capabilities.** The lazy-loading model — list tool names upfront, fetch details via `--help` on demand — is structurally more efficient. CLI also benefits from LLMs' massive pre-training on shell commands, man pages, and Stack Overflow.

3. **The cost scales multiplicatively with MCP servers, but linearly with CLI tools.** Adding an MCP server adds its full schema cost. Adding a CLI tool adds ~50 tokens for a name/location entry. The gap widens as integrations grow.

4. **Tool overload degrades accuracy, not just cost.** 24-point accuracy drop from 4 tools to 46 tools. Agents hallucinate parameters, pick wrong tools, and starve their system prompts for space. This is arguably worse than the dollar cost.

5. **The solutions exist but require architectural changes.** Tool Search (Anthropic/OpenAI), Code Mode (Cloudflare), DynamicMCP (AgentPMT), CLI conversion (CLIHub/mcp2cli), and proxy filtering (mcp-filter) all work. The question is whether the MCP spec itself will adopt lazy loading as a first-class primitive.

6. **MCP and CLI aren't competing — they're complementary layers.** MCP provides discovery, authentication, typed interfaces, and audit trails. CLI provides token-efficient execution and composability. The hybrid pattern — MCP for discovery, CLI for execution — is where production systems are heading.

7. **$8,100/month vs $45/month for the same agent.** Naive MCP vs CLI-only, 30K requests/month on Sonnet. That's a 180x cost difference in pure schema overhead. Even with Tool Search, you're at $180/month vs $45.

---

## Predictions

1. **MCP spec will adopt lazy tool hydration within 6 months.** The `tools/get_schema` method and `minimal` flag proposals ([Issue #1978](https://github.com/modelcontextprotocol/modelcontextprotocol/issues/1978)) have too much community pressure behind them to ignore. MCP joined the Linux Foundation's Agentic AI Foundation with backing from Anthropic, OpenAI, Google, Microsoft, and AWS. Native progressive disclosure will become a spec-level feature.

2. **"Code Mode" will become the dominant pattern for large APIs.** Cloudflare proved that 2 tools + a typed SDK can replace 2,500 tool definitions. Every major API provider (AWS, GCP, Azure, Stripe, Twilio) will ship Code Mode-style MCP servers within 12 months. The pattern is too compelling: fixed context cost regardless of API surface area.

3. **CLI-to-MCP bridges will proliferate and then disappear.** Tools like CLIHub and mcp2cli are necessary stopgaps. Once MCP natively supports lazy loading and the major MCP servers implement efficient schemas, the bridge pattern becomes unnecessary. The bridges will peak in usage by mid-2026 and decline by end of year.

4. **Token-efficient tool calling will become a competitive differentiator for AI platforms.** The platform that solves this transparently — so developers don't have to think about schema overhead — will win the agent infrastructure market. Anthropic's auto-enabling Tool Search at >10% context is the right instinct.

5. **The 200K context window is not enough for production multi-tool agents.** Even with all optimizations, production agents connecting to 10+ services while maintaining conversation history, RAG context, and system prompts will push against 200K limits. This will drive demand for either larger context windows or fundamentally different architecture (sub-agents with focused toolsets, external tool memory).

---

## Sources

All sources are cited inline throughout the report. Key references:

- [BuildMVPFast — MCP Token Cost Problem (2026)](https://www.buildmvpfast.com/blog/mcp-hidden-cost-cli-agent-infrastructure-2026)
- [AgentPMT — MCP Servers Waste 96% of Context](https://www.agentpmt.com/articles/mcp-servers-waste-96-of-agent-context-on-tool-definitions)
- [AgentPMT — The MCP Bloat Tax](https://www.agentpmt.com/articles/thousands-of-mcp-tools-zero-context-left-the-bloat-tax-breaking-ai-agents)
- [Kan Yilmaz — I Made MCP 94% Cheaper](https://kanyilmaz.me/2026/02/23/cli-vs-mcp.html)
- [Pramod Dutta — Playwright MCP vs CLI](https://medium.com/@scrolltest/playwright-mcp-burns-114k-tokens-per-test-the-new-cli-uses-27k-heres-when-to-use-each-65dabeaac7a0)
- [Cloudflare — Code Mode: Entire API in 1,000 Tokens](https://blog.cloudflare.com/code-mode-mcp/)
- [Nebula — MCP Tool Overload: Why More Tools Make Your Agent Worse](https://dev.to/nebulagg/mcp-tool-overload-why-more-tools-make-your-agent-worse-5a49)
- [Layered System — MCP Tool Schema Bloat](https://layered.dev/mcp-tool-schema-bloat-the-hidden-token-tax-and-how-to-fix-it/)
- [Joe Njenga — Claude Code Cut MCP Context Bloat by 46.9%](https://medium.com/@joe.njenga/claude-code-just-cut-mcp-context-bloat-by-46-9-51k-tokens-down-to-8-5k-with-new-tool-search-ddf9e905f734)
- [Cyrus — What is MCP Tool Search?](https://www.atcyrus.com/stories/mcp-tool-search-claude-code-context-pollution-guide)
- [Can Dedeoglu — Claude Tool Search API](https://www.candede.com/articles/claude-tool-search)
- [Alyshia Ledlie — SigNoz MCP Context Optimization](https://www.aledlie.com/reports/2026-01-19-signoz-mcp-context-optimization/)
- [mcp2cli GitHub](https://github.com/knowsuchagency/mcp2cli)
- [CLIHub GitHub](https://github.com/thellimist/clihub)
- [MCP Issue #1978 — Lazy Tool Hydration](https://github.com/modelcontextprotocol/modelcontextprotocol/issues/1978)
- [Huawei SEP-1576 — Schema Redundancy](https://github.com/modelcontextprotocol/modelcontextprotocol/issues/1576)
- [OpenAI — Tool Search API](https://developers.openai.com/api/docs/guides/tools-tool-search/)
- [Tetrate — MCP Tool Filtering & Performance](https://tetrate.io/learn/ai/mcp/tool-filtering-performance)
- [Manveer Chawla — MCP vs CLI Decision Framework](https://manveerc.substack.com/p/mcp-vs-cli-ai-agents)
- [MyEngineeringPath — Token Budgeting Guide](https://myengineeringpath.dev/genai-engineer/context-windows/)
- [Speakeasy — Reducing MCP Token Usage by 100x](https://www.speakeasy.com/blog/how-we-reduced-token-usage-by-100x-dynamic-toolsets-v2)
- [Philipp Schmid — MCP CLI](https://www.philschmid.de/mcp-cli)
- [Björn Büdenbender — MCP Tools Eating 82% of Context](https://ai.gopubby.com/mcp-tools-are-eating-82-of-your-context-window-the-10-minute-fix-for-claude-code-1619733d00dc)
