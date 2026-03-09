---
id: 20260308-RS-002
date: 2026-03-08
category: Research Report
content-status: raw
---

# Agent Memory Wars: Letta vs Mem0 vs Zep — and Why Your Filesystem Might Be Enough

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Background: Why Memory Is the Hardest Layer](#background-why-memory-is-the-hardest-layer)
3. [The Three Contenders](#the-three-contenders)
4. [Letta: The Operating System Approach](#letta-the-operating-system-approach)
5. [Mem0: The Memory API](#mem0-the-memory-api)
6. [Zep: The Temporal Knowledge Graph](#zep-the-temporal-knowledge-graph)
7. [Head-to-Head Comparison](#head-to-head-comparison)
8. [The Benchmark Wars: Nobody's Winning Honestly](#the-benchmark-wars-nobodys-winning-honestly)
9. [The Multi-Agent Memory Problem](#the-multi-agent-memory-problem)
10. [The Filesystem Pattern: CLAUDE.md and the Simplest Thing That Works](#the-filesystem-pattern-claudemd-and-the-simplest-thing-that-works)
11. [Which Memory Architecture Wins for Which Use Case](#which-memory-architecture-wins-for-which-use-case)
12. [Key Takeaways](#key-takeaways)
13. [Predictions](#predictions)

---

## Executive Summary

Agent memory has become a $100M+ venture-funded category in under two years. Three providers — Letta (ex-MemGPT), Mem0, and Zep/Graphiti — dominate the landscape with fundamentally different architectures: an OS-inspired memory hierarchy, a hybrid datastore API, and a temporal knowledge graph, respectively. Each claims benchmark superiority. None of those claims hold up to scrutiny.

The most important finding from this research: **the benchmarks everyone uses to compare these systems are broken**, and the most battle-tested memory pattern for coding agents today is the simplest one — filesystem-backed markdown files like CLAUDE.md. Letta's own research shows a basic filesystem agent scoring 74% on LoCoMo with gpt-4o-mini, beating Mem0's best graph variant at 68.5%. Zep disputes Mem0's benchmark methodology entirely, demonstrating that a correct implementation outperforms Mem0 by 10% on Mem0's own chosen benchmark.

Meanwhile, the genuinely unsolved problem isn't single-agent memory at all — it's multi-agent memory coordination. Anthropic's own data shows multi-agent systems consume roughly 15x the tokens of single-agent interactions, and [36.9% of multi-agent failures](https://arxiv.org/abs/2503.13657) trace back to agents operating on inconsistent views of shared state. The team that cracks shared memory coordination captures a category worth far more than what any of these three providers are building today.

---

## Background: Why Memory Is the Hardest Layer

LLMs are stateless. Every invocation starts with a blank context window. For a quick coding task, this is invisible. For anything that spans sessions — codebase migrations, ongoing user relationships, multi-day projects — the lack of memory creates what [NJ Raman calls "architectural amnesia"](https://medium.com/@nraman.n6/agent-memory-wars-why-your-multi-agent-system-forgets-what-matters-and-how-to-fix-it-a9a1901df0d9): agents make the same mistakes repeatedly, re-discover resolved issues, and lose continuity.

The field has converged on a taxonomy borrowed from cognitive science, mapping closely to [Endel Tulving's 1972 work](https://gist.github.com/spikelab/7551c6368e23caa06a4056350f6b2db3) on human memory:

| Memory Type | Agent Equivalent | Duration | Implementation |
|---|---|---|---|
| **Working** | Context window, scratchpad | Seconds to minutes | In-context tokens |
| **Episodic** | Conversation history, task logs | Sessions to months | Vector store, log files |
| **Semantic** | Facts, preferences, knowledge | Indefinite | Knowledge graph, KV store |
| **Procedural** | Learned workflows, tool patterns | Permanent once codified | Skills files, fine-tuning |

The engineering challenge: each type has different retention requirements, retrieval patterns, and consistency needs. Systems that treat all memory uniformly — stuffing everything into a vector store, for example — either overpersist transient state (polluting retrieval) or underpersist durable knowledge (forcing agents to relearn what they should already know).

Memory's importance has been codified by the agent infrastructure landscape. [The agent stack component map](research/reports/20260308-agent-stack-component-map.md) identified memory as the hardest unsolved infrastructure problem, rated "VERY HIGH" for deep-dive potential. This report delivers that deep dive.

---

## The Three Contenders

Three startups have raised a combined $58M+ to solve agent memory:

```
┌─────────────────────────────────────────────────────────────────────┐
│                    THE MEMORY LANDSCAPE                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   LETTA (ex-MemGPT)          MEM0                   ZEP/GRAPHITI   │
│   ────────────────           ────                   ────────────   │
│   UC Berkeley spinout        YC W24 → Series A      Temporal KG    │
│   $10M seed (Felicis)        $24M (Basis Set)       Undisclosed    │
│   OS-inspired hierarchy      Hybrid datastore        Knowledge     │
│   Sleep-time compute         3-line API              graph engine   │
│   Agents edit own memory     Vector + KV + Graph     Bi-temporal    │
│                                                     model          │
│   Self-hosted + Cloud        Self-hosted + Cloud     Cloud +        │
│   Open source (Apache 2)     Open source (Apache 2)  Graphiti OSS  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

They represent three genuinely different philosophies about what memory should be. Understanding those differences matters more than any benchmark score.

---

## Letta: The Operating System Approach

### Origin and Philosophy

Letta emerged from the [MemGPT research paper](https://www.letta.com/blog/agent-memory) at UC Berkeley, which introduced the core insight: agent memory should work like an operating system's memory hierarchy. Just as an OS manages virtual memory across registers, cache, RAM, and disk, an LLM agent should manage information across a hierarchy of storage tiers with different access speeds and capacities.

The company [raised $10M from Felicis](https://www.hpcwire.com/bigdatawire/this-just-in/letta-emerges-from-stealth-with-10m-to-build-ai-agents-with-advanced-memory/) in September 2024 and launched publicly with the Letta platform.

### Architecture

Letta's memory hierarchy has three tiers:

```
┌─────────────────────────────────────────────────┐
│  CORE MEMORY                                     │
│  Always loaded in-context. Self-edited by the    │
│  agent via tool calls. Think: "system prompt     │
│  that the agent rewrites as it learns."          │
│  ─────────────────────────────────────────────   │
│  Size: Small (fits in context window)            │
│  Access: Instant (already in prompt)             │
│  Update: Agent calls core_memory_append/replace  │
├─────────────────────────────────────────────────┤
│  RECALL MEMORY                                   │
│  Searchable conversation history. Every message  │
│  is stored and retrievable on demand.            │
│  ─────────────────────────────────────────────   │
│  Size: Unbounded                                 │
│  Access: Agent calls conversation_search         │
│  Update: Automatic (all messages stored)         │
├─────────────────────────────────────────────────┤
│  ARCHIVAL MEMORY                                 │
│  Long-term external storage. Vector database     │
│  for arbitrary knowledge.                        │
│  ─────────────────────────────────────────────   │
│  Size: Unbounded                                 │
│  Access: Agent calls archival_memory_search      │
│  Update: Agent calls archival_memory_insert      │
└─────────────────────────────────────────────────┘
```

The critical differentiator: **agents actively manage their own memory.** The LLM decides what to promote from recall to core, what to archive, what to forget. This is fundamentally different from passive retrieval systems where an external process decides what's relevant.

### Sleep-Time Compute

Letta's most novel contribution is [sleep-time compute](https://www.letta.com/blog/sleep-time-compute), introduced in April 2025. The core idea: agents should think during idle periods, not just when users are waiting.

Sleep-time compute creates two agents behind the scenes:

1. **Primary agent** — handles user-facing conversation, tool calls, retrieval. Cannot edit core memory.
2. **Sleep-time agent** — runs in the background during idle periods. Reorganizes memory, consolidates insights, rewrites core memory for clarity. Can use a stronger, slower model since latency doesn't matter.

This solves two problems with the original MemGPT design:
- **Latency**: Memory management no longer blocks conversation. The primary agent is fast because it doesn't pause to reorganize memory mid-conversation.
- **Quality**: Memory consolidation is done by a dedicated agent that can use expensive reasoning models (e.g., gpt-4.1 or Claude Sonnet) without impacting user-facing response times.

The analogy to human sleep is apt: during sleep, the brain consolidates episodic memories into long-term semantic memory. Letta's sleep-time agent does the same — transforming raw conversational context into clean, structured learned context.

### Context Repositories (February 2026)

Letta's most recent evolution is [Context Repositories](https://www.letta.com/blog/context-repositories): git-backed memory for coding agents. Instead of the MemGPT-style memory tools, agents store their context in the local filesystem and manage it with full terminal capabilities — writing scripts, spawning subagents, running searches. Every change is automatically versioned with git commits, enabling concurrent collaborative memory management.

This represents a significant philosophical shift: from structured memory APIs toward giving agents the same tools developers use to manage knowledge.

### Pricing

| Plan | Price | Key Limits |
|---|---|---|
| Free | $0 | 3 agents, BYOK only |
| Pro | $20/mo | Unlimited agents, $20 API credits |
| Max | $200/mo | Higher limits, early access |
| Enterprise | Contact | RBAC, SSO, volume pricing |

Self-hosting is fully supported via the open-source repo (Apache 2.0 license). BYOK (bring your own key) works on all plans, meaning you can use your own LLM API keys and only pay for Letta's infrastructure.

---

## Mem0: The Memory API

### Origin and Philosophy

Mem0 takes the opposite approach from Letta: instead of building an agent framework with memory built in, Mem0 provides **memory as a pluggable API** that works with any agent framework. Three lines of code to add memory to any application.

The company went through Y Combinator (W24) and [raised $24M across Seed and Series A](https://mem0.ai/series-a) in October 2025, led by Basis Set Ventures with participation from Peak XV Partners, GitHub Fund, and strategic angels including the CEOs of Datadog, Supabase, PostHog, and Weights & Biases.

The traction numbers are real: 41,000+ GitHub stars, 14M+ Python downloads, API calls growing from 35M in Q1 2025 to 186M in Q3 2025.

### Architecture

Mem0's architecture is a hybrid datastore combining three retrieval strategies:

```
┌─────────────────────────────────────────────────────┐
│                    MEM0 ARCHITECTURE                  │
│                                                       │
│   ┌─────────────┐  ┌──────────────┐  ┌────────────┐ │
│   │   Vector     │  │  Key-Value   │  │   Graph    │ │
│   │   Store      │  │  Store       │  │   Store    │ │
│   │             │  │              │  │ (Pro+)     │ │
│   │  Semantic    │  │  Structured  │  │  Entity    │ │
│   │  similarity  │  │  facts &     │  │  relations │ │
│   │  search      │  │  preferences │  │  & links   │ │
│   └──────┬──────┘  └──────┬───────┘  └─────┬──────┘ │
│          │                │                 │         │
│          └────────────────┼─────────────────┘         │
│                           │                           │
│                    ┌──────┴──────┐                     │
│                    │   Unified   │                     │
│                    │   Memory    │                     │
│                    │   API       │                     │
│                    └─────────────┘                     │
└─────────────────────────────────────────────────────┘
```

Key design decisions:

- **Memory extraction is automatic.** You pass in conversations; Mem0 extracts facts, preferences, and entities without explicit tagging. The agent doesn't need memory-specific tools — Mem0 handles it behind the scenes.
- **Three memory scopes**: user memory (persists across all conversations for a person), agent memory (what the agent has learned), and session memory (within a single conversation).
- **Memory compression and deduplication.** Mem0 compresses memories to reduce token usage, applies confidence scores and decay, and intelligently resolves conflicts when new facts contradict old ones.
- **Graph memory is a Pro+ feature.** The open-source version uses vector + KV; the full knowledge graph (entity/relationship extraction, Neo4j/Memgraph backends) requires a paid plan.

### AWS Exclusive Partnership

In May 2025, [AWS partnered with Mem0](https://mem0.ai/blog/aws-and-mem0-partner-to-bring-persistent-memory-to-next-gen-ai-agents-with-strands/) to make it the exclusive memory provider for the Strands Agents SDK. This gives Mem0 distribution through AWS's massive developer ecosystem and legitimizes it as enterprise infrastructure.

### Pricing

| Plan | Price | Key Limits |
|---|---|---|
| Free | $0 | Limited (25 notes/mo per some reports) |
| Pro | $19/mo | Graph memory, higher limits |
| Business | $249/mo | Full features, higher throughput |
| Enterprise | Contact | Custom |

Self-hosting is supported via the open-source repo (Apache 2.0). The managed platform handles scaling, but the open-source version doesn't include the graph memory features available on Pro+.

---

## Zep: The Temporal Knowledge Graph

### Origin and Philosophy

Zep's thesis is that memory is fundamentally a **graph problem**, not a vector search problem. Agents don't just need to find similar text — they need to understand entities, relationships, and how those relationships change over time. A vector store can tell you "the user mentioned Python" but can't model "the user switched from Python to Rust in January 2026."

Zep's core engine is [Graphiti](https://github.com/getzep/graphiti) (23,400+ GitHub stars, Apache 2.0), a framework for building temporally-aware knowledge graphs.

### Architecture

Zep's architecture centers on a bi-temporal knowledge graph:

```
┌─────────────────────────────────────────────────────────┐
│                ZEP / GRAPHITI ARCHITECTURE                │
│                                                           │
│  ┌─────────────────────────────────────────────────────┐ │
│  │              TEMPORAL KNOWLEDGE GRAPH                 │ │
│  │                                                       │ │
│  │   Nodes: Entities (people, places, concepts)         │ │
│  │   Edges: Relationships with temporal metadata         │ │
│  │                                                       │ │
│  │   BI-TEMPORAL MODEL:                                  │ │
│  │   ┌─────────────────┐  ┌───────────────────┐         │ │
│  │   │  Valid Time      │  │  Transaction Time │         │ │
│  │   │  When did this   │  │  When was this    │         │ │
│  │   │  actually happen?│  │  recorded?        │         │ │
│  │   └─────────────────┘  └───────────────────┘         │ │
│  │                                                       │ │
│  │   Enables: "What was true as of January?"            │ │
│  │   vs "What did we know as of January?"               │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                           │
│  Search Capabilities:                                     │
│  ├── Semantic (vector similarity)                        │
│  ├── Full-text (keyword matching)                        │
│  ├── Graph traversal (relationship paths)                │
│  └── Temporal (time-scoped queries)                      │
│                                                           │
│  Auto-extraction:                                         │
│  ├── Entity recognition                                  │
│  ├── Relationship extraction                             │
│  ├── Temporal reasoning                                  │
│  └── Contradiction detection + resolution                │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

The bi-temporal model is Zep's sharpest technical differentiator. Most systems track when data was stored. Zep tracks two timelines independently:

1. **Valid time**: When the fact was actually true in the real world.
2. **Transaction time**: When the fact was recorded in the system.

This enables queries that no vector store can answer: "What did we believe about this customer's preferences last month?" vs "What were their actual preferences last month?" The distinction matters for audit trails, debugging, and handling information that arrives out of order.

### Graphiti MCP Server

Zep recently released an [MCP server for Graphiti](https://github.com/getzep/graphiti), allowing Claude, Cursor, and other MCP clients to use Graphiti as a memory backend. This positions Zep to be the memory layer for coding agents that already support MCP.

### Pricing

| Plan | Price | Key Limits |
|---|---|---|
| Free | $0 | 1,000 credits/mo |
| Flex | $25/mo | 20,000 credits, 10 custom entity types |
| Flex Plus | $475/mo | 300,000 credits, webhooks, API logs |
| Enterprise | Contact | SOC 2 Type II, HIPAA BAA, BYOC |

Graphiti (the core engine) is open source (Apache 2.0). The Zep managed service adds hosted infrastructure, automatic extraction, and enterprise features. Zep is cloud-only for the managed service; you can self-host Graphiti and build your own memory layer on top.

---

## Head-to-Head Comparison

| Dimension | Letta | Mem0 | Zep |
|---|---|---|---|
| **Core philosophy** | Agents manage own memory | Memory as pluggable API | Memory as knowledge graph |
| **Architecture** | OS-inspired hierarchy (core/recall/archival) | Hybrid datastore (vector + KV + graph) | Temporal knowledge graph (bi-temporal) |
| **Memory model** | Agent actively edits structured memory blocks | Automatic extraction + compression | Automatic entity/relationship extraction |
| **Unique innovation** | Sleep-time compute | 3-line API integration | Bi-temporal model |
| **Open source** | Yes (Apache 2.0, full platform) | Yes (Apache 2.0, partial — no graph) | Graphiti is OSS; Zep service is cloud-only |
| **Self-hostable** | Yes | Yes (limited features) | Graphiti only |
| **Graph support** | No (filesystem + vector) | Yes (Pro+, via Neo4j/Memgraph) | Yes (core feature, native) |
| **Temporal reasoning** | No native support | No | Yes (bi-temporal, first-class) |
| **Framework coupling** | Tightly coupled (Letta agents) | Framework-agnostic (any agent) | Framework-agnostic (any agent) |
| **SDKs** | Python, TypeScript | Python, JavaScript | Python, TypeScript, Go |
| **Starting price** | Free (3 agents) | Free (limited) | Free (1,000 credits) |
| **Paid plans** | $20-200/mo | $19-249/mo | $25-475/mo |
| **Funding** | $10M Seed | $24M (Seed + Series A) | Undisclosed |
| **Key partnership** | — | AWS (exclusive memory for Strands SDK) | — |
| **GitHub stars** | ~30K (MemGPT/Letta combined) | 41K+ | 23K+ (Graphiti) |

---

## The Benchmark Wars: Nobody's Winning Honestly

The state of agent memory benchmarking is a mess. Every provider claims superiority, and none of the claims fully hold up.

### The LoCoMo Saga

The primary benchmark used across the industry is [LoCoMo](https://arxiv.org/html/2501.13956v1) — a question-answering benchmark over long conversations. The problem: **it's fundamentally flawed as a memory benchmark.**

Mem0 published results claiming SOTA performance: 68.5% on their best graph variant. But three independent analyses exposed serious problems:

1. **Zep's rebuttal**: [Zep demonstrated](https://blog.getzep.com/lies-damn-lies-statistics-is-mem0-really-sota-in-agent-memory/) that Mem0's evaluation of Zep used a flawed implementation — sequential instead of parallel searches, improper timestamp handling, and incorrect user model configuration. When correctly implemented, Zep scores 75.14% (later improved to 80%), outperforming Mem0 by 10%+.

2. **Letta's filesystem experiment**: [Letta showed](https://www.letta.com/blog/benchmarking-ai-agent-memory) that a simple filesystem-based agent using gpt-4o-mini — with no specialized memory tools at all, just file search and grep — scores 74.0% on LoCoMo. This beats Mem0's best score and approaches Zep's corrected score, using the simplest possible approach.

3. **The full-context baseline**: Most damning of all, Mem0's own results show a simple full-context baseline (just feeding the entire conversation to the LLM) achieving ~73%, beating Mem0's specialized system. If dumping all text into the context window outperforms your memory product, the benchmark isn't testing memory.

### Why LoCoMo Fails as a Benchmark

| Flaw | Impact |
|---|---|
| Conversations average only 16-26K tokens | Fits entirely in modern context windows |
| Underspecified questions with multiple correct answers | Ambiguous scoring |
| Incorrect speaker attribution in ground truth | False negatives |
| Missing ground truth (Category 5 unusable) | Incomplete evaluation |
| No temporal reasoning or knowledge update tests | Misses a core memory function |

### What Should Replace It

Zep advocates for [LongMemEval](https://blog.getzep.com/state-of-the-art-agent-memory/), which features 115K+ token conversations, human-curated questions, explicit temporal reasoning tests, and knowledge update scenarios. Letta created their own [Letta Memory Benchmark](https://www.letta.com/blog/benchmarking-ai-agent-memory) (Letta Leaderboard) that evaluates memory in dynamic contexts rather than just retrieval, plus [Context-Bench](https://www.letta.com/blog/context-bench-benchmarking-llms-on-agentic-context-engineering) for evaluating context engineering capabilities.

The bottom line: **don't choose a memory provider based on LoCoMo scores.** The benchmark doesn't test what matters for production memory systems.

---

## The Multi-Agent Memory Problem

Single-agent memory is approaching "good enough" with existing tools. Multi-agent memory coordination is genuinely unsolved and economically catastrophic.

### The 15x Token Multiplier

[Anthropic's documentation](https://www.anthropic.com/engineering/multi-agent-research-system) on multi-agent systems provides the key numbers:
- Single agents use roughly **4x** the tokens of equivalent chat interactions
- Multi-agent systems use roughly **15x** tokens
- The gap is coordination overhead: agents re-retrieving information, re-explaining context, re-validating assumptions

At current API pricing ($0.30-$3.00 per million context tokens), this overhead makes many multi-agent workflows economically unviable.

### 36.9% of Failures Are Shared-State Failures

[Cemri et al.'s MAST taxonomy](https://arxiv.org/abs/2503.13657), built from 1,600+ annotated execution traces across AutoGen, CrewAI, and LangGraph, found that **interagent misalignment accounts for 36.9% of all multi-agent failures.** Agents don't fail because they can't reason — they fail because they operate on inconsistent views of shared state.

As [Mikiko Bazeley explains in O'Reilly](https://www.oreilly.com/radar/why-multi-agent-systems-need-memory-engineering/): "Agent A completes a subtask and moves on. Agent B, with no visibility into A's work, reexecutes the same operation. Agent C receives inconsistent results from both and confabulates a reconciliation." The system produces output that costs 3x what it should and contains errors that propagate through every downstream task.

### The Five Pillars of Multi-Agent Memory

Bazeley's analysis identifies five capabilities that production agent teams require:

```
1. TAXONOMY      — What kinds of memory? Working, episodic, semantic,
                   procedural, shared. Each has different requirements.

2. PERSISTENCE   — What survives and for how long? Explicit lifecycle
                   policies, not "store everything forever."

3. RETRIEVAL     — How agents access relevant memory without drowning
                   in noise. Recency, relevance, scope, role all matter.

4. COORDINATION  — Which memories are visible to which agents? What can
                   each read vs write? How do scopes nest?

5. CONSISTENCY   — What happens when memory updates collide? Last-write-
                   wins is almost never correct. Need merge strategies.
```

None of the three memory providers adequately solve pillars 4 and 5. Letta has a [Conversations API](https://www.letta.com/blog/conversations-shared-agent-memory) (January 2026) for shared memory across concurrent experiences, which is a start. Mem0 has multi-user support but no explicit coordination semantics. Zep's graph structure could theoretically model shared state, but the tooling for multi-agent coordination isn't there yet.

### The Homogeneity Trap

[Xu et al.](https://arxiv.org/abs/2601.12307) make a sharp observation: many deployed "multi-agent" systems are so homogeneous — same model everywhere, agents differentiated only by prompts — that a single model can simulate the entire workflow with equivalent results. If a single agent can replace your multi-agent system, you haven't built a team. You've built an expensive way to run one model.

Genuine multi-agent value comes from **heterogeneity**: different models at different price points for different subtasks. But smaller models can't maintain the context required for coordination on their own — they depend on shared memory infrastructure. Memory engineering is what makes heterogeneous agent teams viable.

---

## The Filesystem Pattern: CLAUDE.md and the Simplest Thing That Works

While the memory startups raise millions, the most battle-tested memory pattern for coding agents is the simplest one: files on disk.

### How It Works

```
project/
├── CLAUDE.md          # Project conventions, architecture, rules
├── AGENTS.md          # Multi-agent coordination state
├── .claude/
│   └── MEMORY.md      # Auto-generated persistent memory
└── src/
    └── ...
```

CLAUDE.md loads at the start of every Claude Code session and receives high priority in the context window. [78% of advanced Claude Code users](https://institute.sfeir.com/en/claude-code/claude-code-memory-system-claude-md/deep-dive/) leverage at least one CLAUDE.md file. The pattern extends to Cursor (.cursorrules), GitHub Copilot (copilot-instructions.md), and other coding agents (AGENTS.md).

### Why It Works So Well

As [Letta's own research showed](https://www.letta.com/blog/benchmarking-ai-agent-memory), agents are extremely effective at using filesystem tools, largely because these tools dominate their post-training data. An agent that can grep, search files, and read directories is using skills deeply embedded in its weights from training on millions of coding sessions.

The [agent design patterns analysis](https://rlancemartin.github.io/2026/01/09/agent_design/) from Lance Martin captures it precisely: "The filesystem gives agents access to persistent context. The shell lets agents run built-in utilities, CLIs, provided scripts, or code they write." This is the most natural memory interface for models that were trained to be software engineers.

### Filesystem Memory Advantages

| Advantage | Details |
|---|---|
| **Zero dependencies** | No API keys, no external services, no vector DB |
| **Git-native versioning** | Every memory change is tracked in version control |
| **Human-readable** | Developers can read, edit, and debug memory directly |
| **Framework-agnostic** | Works with any coding agent that can read files |
| **Progressive disclosure** | CLAUDE.md hierarchy: global > project > directory |
| **Battle-tested** | Millions of sessions daily across Claude Code users |

### Filesystem Memory Limitations

| Limitation | Details |
|---|---|
| **No semantic search** | Can only grep/search, not query by meaning |
| **No entity relationships** | Can't model "user X works at company Y" |
| **No temporal reasoning** | Can't answer "what was true last month?" |
| **Context window bounded** | Large CLAUDE.md files consume context budget |
| **Single-agent only** | No coordination primitives for multi-agent |
| **Coding-agent specific** | Doesn't generalize to conversational or enterprise agents |

### Letta's Convergence Toward Filesystem

Notably, Letta's February 2026 [Context Repositories](https://www.letta.com/blog/context-repositories) release is a convergence toward the filesystem pattern. Instead of MemGPT-style memory tools, agents use git-backed files to store context — the same approach CLAUDE.md pioneered, but with structured versioning and concurrent access support. The best agent framework in the memory space is evolving toward the pattern that emerged organically from coding practice.

---

## Which Memory Architecture Wins for Which Use Case

The right memory architecture depends entirely on what you're building:

| Use Case | Best Choice | Why |
|---|---|---|
| **Coding agent (single repo)** | Filesystem (CLAUDE.md) | Zero deps, git-native, agents are trained on file tools |
| **Conversational assistant (single user)** | Mem0 | Fastest integration, automatic extraction, framework-agnostic |
| **Customer support (entity-heavy)** | Zep/Graphiti | Temporal knowledge graph models relationships and changes |
| **Long-horizon tasks (multi-day)** | Letta | Sleep-time compute consolidates memory during idle periods |
| **Personalization at scale** | Mem0 | AWS partnership, managed platform, proven at 186M+ API calls/quarter |
| **Compliance/audit requirements** | Zep | Bi-temporal model enables point-in-time queries |
| **Multi-agent systems** | None are adequate yet | All three have gaps in coordination and consistency |
| **Budget-constrained prototype** | Filesystem or Mem0 (free tier) | Simplest path to working memory |

### Decision Framework

```
Do you need memory for a coding agent?
├── YES → Use CLAUDE.md / AGENTS.md (filesystem)
│         The simplest thing that works. No dependencies.
│
└── NO → Is temporal reasoning important?
         ├── YES → Zep/Graphiti
         │         Bi-temporal model is genuinely unique.
         │
         └── NO → Do you want memory tightly coupled to your agent framework?
                  ├── YES → Letta
                  │         Full agent platform with memory built in.
                  │         Sleep-time compute for idle learning.
                  │
                  └── NO → Mem0
                           Pluggable API for any framework.
                           Fastest integration path.
```

---

## Key Takeaways

1. **The benchmarks are broken, and every provider knows it.** LoCoMo, the most-cited agent memory benchmark, is beaten by dumping all text into a context window. Don't choose a provider based on benchmark scores. Choose based on architectural fit for your use case.

2. **Letta's sleep-time compute is the most genuinely novel idea in the space.** Using idle periods for background memory consolidation — with a stronger model than the user-facing agent — is an elegant solution to the latency-vs-quality tradeoff that plagues all memory systems. No competitor has anything equivalent.

3. **Mem0 wins on distribution, not architecture.** The AWS exclusive partnership and 3-line API make it the easiest path to production memory. The architecture (hybrid vector + KV + graph) is competent but not distinctive. Mem0's moat is ecosystem, not technology.

4. **Zep's bi-temporal model is underappreciated.** For any use case involving knowledge that changes over time — customer preferences, project status, organizational state — Zep's ability to distinguish "when was it true" from "when did we learn it" is genuinely powerful and unique among competitors.

5. **For coding agents, a filesystem is all you need today.** CLAUDE.md, AGENTS.md, and auto-memory files are the most battle-tested agent memory pattern in production. Letta's own research proves that filesystem agents beat specialized memory tools on existing benchmarks. The memory startups are solving for conversational and enterprise use cases, not coding.

6. **Multi-agent memory coordination is the real unsolved problem.** Single-agent memory is approaching commodity. Multi-agent shared state — where agents maintain consistent views, avoid duplicated work, and coordinate updates — is where the 15x token multiplier lives and where 36.9% of multi-agent failures originate. None of the three providers have a complete answer.

7. **Memory portability will become the next battleground.** Mem0's pitch for portable, provider-neutral memory ("your memory, wherever you need it") is prescient. As users accumulate rich context in one agent, the friction of starting from scratch in another will become intolerable. Whoever owns the portable memory standard captures the coordination layer.

---

## Predictions

1. **Letta and Zep will merge or partner within 18 months.** Letta's agent framework + sleep-time compute paired with Graphiti's temporal knowledge graph would be the strongest combined offering in the space. Neither is complete alone. Letta lacks graph capabilities; Zep lacks an agent framework.

2. **Mem0 will be acquired by a cloud provider by end of 2027.** The AWS partnership is a precursor. Mem0's value is as infrastructure embedded in cloud SDKs, not as a standalone product. AWS, Google, or Microsoft will absorb it into their agent platform.

3. **LoCoMo will be abandoned as a benchmark within 12 months.** The Letta filesystem result (74% with gpt-4o-mini, no memory tools) is the final nail. A benchmark that can't distinguish "no memory system" from "specialized memory system" is not testing memory. LongMemEval or Letta's Context-Bench will replace it.

4. **Filesystem-backed memory will become a first-class feature in all coding agents.** Claude Code's CLAUDE.md pattern will be replicated in every coding agent. Expect cursor/.rules, copilot/.context, and equivalents to evolve into full memory management systems with versioning, search, and progressive disclosure.

5. **The multi-agent memory coordination market will attract $200M+ in funding by end of 2027.** The 15x token multiplier is unsustainable. Shared memory that reduces redundant context loading across agent teams is the critical infrastructure gap. The team that solves coordination, consistency, and scoped sharing will own the most valuable layer of the agent stack.

6. **Sleep-time compute will be adopted by all major agent frameworks within 12 months.** The idea is too good and too obvious once demonstrated. Background memory consolidation during idle periods is a Pareto improvement — better quality, lower latency, at the cost of compute that would otherwise be wasted. Expect OpenAI, Google, and Anthropic to ship their own versions.

---

## Sources

### Letta / MemGPT
- [Sleep-time Compute](https://www.letta.com/blog/sleep-time-compute) — Letta Research, April 2025
- [Benchmarking AI Agent Memory: Is a Filesystem All You Need?](https://www.letta.com/blog/benchmarking-ai-agent-memory) — Letta Research, August 2025
- [Agent Memory: How to Build Agents that Learn and Remember](https://www.letta.com/blog/agent-memory) — Letta, July 2025
- [Context Repositories: Git-based Memory for Coding Agents](https://www.letta.com/blog/context-repositories) — Letta, February 2026
- [Rearchitecting Letta's Agent Loop](https://www.letta.com/blog/letta-v1-agent) — Letta, October 2025
- [Letta Pricing](https://www.letta.com/pricing) — Letta
- [Letta Emerges from Stealth with $10M](https://www.hpcwire.com/bigdatawire/this-just-in/letta-emerges-from-stealth-with-10m-to-build-ai-agents-with-advanced-memory/) — HPCwire, September 2024

### Mem0
- [Mem0 Raises $24M Series A](https://mem0.ai/series-a) — Mem0, October 2025
- [AWS and Mem0 Partner for Strands SDK](https://mem0.ai/blog/aws-and-mem0-partner-to-bring-persistent-memory-to-next-gen-ai-agents-with-strands/) — Mem0, May 2025
- [The Architecture of Remembrance](https://mem0.ai/blog/what-is-ai-agent-memory) — Mem0, January 2026
- [$24M Funding Announcement](https://www.prnewswire.com/news-releases/mem0-raises-24m-series-a-to-build-memory-layer-for-ai-agents-302597157.html) — PR Newswire, October 2025

### Zep / Graphiti
- [Zep: A Temporal Knowledge Graph Architecture for Agent Memory](https://arxiv.org/html/2501.13956v1) — Rasmussen et al., January 2025
- [Is Mem0 Really SOTA in Agent Memory?](https://blog.getzep.com/lies-damn-lies-statistics-is-mem0-really-sota-in-agent-memory/) — Zep Blog, May 2025
- [Zep Is The New State of the Art in Agent Memory](https://blog.getzep.com/state-of-the-art-agent-memory/) — Zep Blog, January 2025
- [Graphiti: Temporal Knowledge Graphs for Agentic Apps](https://blog.getzep.com/graphiti-knowledge-graphs-for-agents/) — Zep Blog, August 2024
- [Graphiti GitHub Repository](https://github.com/getzep/graphiti) — 23,400+ stars
- [Zep Pricing](https://www.getzep.com/pricing/) — Zep

### Multi-Agent Memory
- [Why Multi-Agent Systems Need Memory Engineering](https://www.oreilly.com/radar/why-multi-agent-systems-need-memory-engineering/) — Mikiko Bazeley, O'Reilly Radar, February 2026
- [Why Multi-Agent Systems Need Memory Engineering](https://www.mongodb.com/company/blog/technical/why-multi-agent-systems-need-memory-engineering) — MongoDB, September 2025
- [Agent Memory Wars](https://medium.com/@nraman.n6/agent-memory-wars-why-your-multi-agent-system-forgets-what-matters-and-how-to-fix-it-a9a1901df0d9) — NJ Raman
- [Why Do Multi-Agent LLM Systems Fail?](https://arxiv.org/abs/2503.13657) — Cemri et al., CMU/UC Berkeley, 2025
- [Two Agents Are a Distributed System](https://www.agentpmt.com/articles/multi-agent-coordination-distributed-systems-2026) — AgentPMT, January 2026

### Comparisons and Analyses
- [Mem0 vs Zep vs LangMem vs MemoClaw](https://dev.to/anajuliabit/mem0-vs-zep-vs-langmem-vs-memoclaw-ai-agent-memory-comparison-2026-1l1k) — DEV Community, 2026
- [From Beta to Battle-Tested: Picking Between Letta, Mem0 & Zep](https://medium.com/asymptotic-spaghetti-integration/from-beta-to-battle-tested-picking-between-letta-mem0-zep-for-ai-memory-6850ca8703d1) — Calvin Ku, May 2025
- [Memory Systems for AI Agents: Practical Implementations](https://gist.github.com/spikelab/7551c6368e23caa06a4056350f6b2db3) — spikelab, February 2026
- [Agent Memory: Why Your AI Has Amnesia](https://blogs.oracle.com/developers/agent-memory-why-your-ai-has-amnesia-and-how-to-fix-it) — Oracle Developers, February 2026

### Filesystem Memory
- [The Complete Guide to CLAUDE.md and AGENTS.md](https://medium.com/data-science-collective/the-complete-guide-to-ai-agent-memory-files-claude-md-agents-md-and-beyond-49ea0df5c5a9) — Paolo Perrone, February 2026
- [The CLAUDE.md Memory System Deep Dive](https://institute.sfeir.com/en/claude-code/claude-code-memory-system-claude-md/deep-dive/) — SFEIR Institute, February 2026
- [AI Agent Memory Management: When Markdown Files Are All You Need](https://dev.to/imaginex/ai-agent-memory-management-when-markdown-files-are-all-you-need-5ekk) — DEV Community
- [Agent Design Patterns](https://rlancemartin.github.io/2026/01/09/agent_design/) — Lance Martin, January 2026

### Market Context
- [Stateful Agents with Letta.ai](https://machinelearningatscale.substack.com/p/stateful-agents-with-lettaai) — Ludovico Bessi, June 2025
- [The Agentic AI Infrastructure Landscape](https://medium.com/@vinniesmandava/the-agentic-ai-infrastructure-landscape-in-2025-2026-a-strategic-analysis-for-tool-builders-b0da8368aee2) — Sri Srujan Mandava
- [The Agent Stack Component Map](research/reports/20260308-agent-stack-component-map.md) — Internal research
