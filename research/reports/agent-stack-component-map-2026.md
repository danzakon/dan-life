---
id: 20260308-RS-001
date: 2026-03-08
category: Research Report
content-status: raw
---

# The Agent Stack: A Component Map for Production Agent Systems

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Background: Why a Component Map](#background-why-a-component-map)
3. [The Stack at a Glance](#the-stack-at-a-glance)
4. [Layer 1: Sandbox Architecture](#layer-1-sandbox-architecture)
5. [Layer 2: Agent Protocols and Networking](#layer-2-agent-protocols-and-networking)
6. [Layer 3: File Systems and State Persistence](#layer-3-file-systems-and-state-persistence)
7. [Layer 4: Permission Systems](#layer-4-permission-systems)
8. [Layer 5: The Agent Harness](#layer-5-the-agent-harness)
9. [Layer 6: Observability and Tracing](#layer-6-observability-and-tracing)
10. [Layer 7: Agent Lifecycle Management](#layer-7-agent-lifecycle-management)
11. [Layer 8: Memory and Context Persistence](#layer-8-memory-and-context-persistence)
12. [Layer 9: Multi-Agent Coordination](#layer-9-multi-agent-coordination)
13. [Layer 10: Deployment and Infrastructure-as-Code](#layer-10-deployment-and-infrastructure-as-code)
14. [The Series Map](#the-series-map)
15. [Key Takeaways](#key-takeaways)
16. [Predictions](#predictions)

---

## Executive Summary

Building a production agent system requires solving ten distinct infrastructure problems, each with its own tooling ecosystem, tradeoffs, and maturity curve. Most teams discover these problems one at a time, in the worst possible order — usually when something breaks in production.

This report is not a deep dive into any single layer. It is a structured landscape map of the entire Agent Stack: every major component needed to run agents reliably at scale, the key tools and approaches for each, and a guide to which components warrant their own standalone deep-dive research. Think of it as a table of contents for a ten-part content series.

The agent infrastructure market is projected to reach [$52 billion by 2030](https://zylos.ai/research/2026-02-19-ai-agent-fleet-management), up from roughly $7.8 billion today. [Gartner recorded a 1,445% surge](https://zylos.ai/research/2026-02-19-ai-agent-fleet-management) in multi-agent system inquiries from Q1 2024 to Q2 2025. Enterprise adoption has reached 35% in two years, but only 11% are actually running in production. The gap between experimentation and deployment is an infrastructure gap — and this map shows where the gaps are.

---

## Background: Why a Component Map

Everyone building agents hits the same wall. The model works. The demo is impressive. Then you try to run it in production and discover you need to solve isolation, persistence, permissions, observability, memory, coordination, and deployment — all at once, all interacting with each other.

The discourse is fragmented. Sandbox companies talk about sandboxes. Observability companies talk about tracing. Memory startups talk about memory. Nobody has mapped the full stack in one place, showing how the pieces relate and where the boundaries fall.

This report fills that gap. For each of the ten layers, it captures:

- **What it is** — the problem this layer solves
- **Key tools and approaches** — the current landscape of solutions
- **Deep-dive potential** — what a standalone research report on this layer would cover

The goal is to define the research agenda, not to execute it. Each layer described here could — and should — become its own report.

---

## The Stack at a Glance

```
┌─────────────────────────────────────────────────────────────────┐
│                    THE AGENT STACK                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   10. Deployment & IaC          CI/CD, containerization,        │
│                                 Dagger, GitOps                  │
│   ─────────────────────────────────────────────────────────     │
│   9. Multi-Agent Coordination   Orchestration, task routing,    │
│                                 swarm patterns                  │
│   ─────────────────────────────────────────────────────────     │
│   8. Memory & Context           Cross-session memory,           │
│                                 vector stores, state mgmt       │
│   ─────────────────────────────────────────────────────────     │
│   7. Lifecycle Management       AgentOps, control planes,       │
│                                 fleet management                │
│   ─────────────────────────────────────────────────────────     │
│   6. Observability & Tracing    OpenTelemetry, GenAI SIG,       │
│                                 cost attribution                │
│   ─────────────────────────────────────────────────────────     │
│   5. The Agent Harness          Framework vs runtime vs         │
│                                 harness, context engineering    │
│   ─────────────────────────────────────────────────────────     │
│   4. Permission Systems         Least privilege, dynamic        │
│                                 auth, tool access control       │
│   ─────────────────────────────────────────────────────────     │
│   3. File Systems & State       Volumes, snapshots, CoW,        │
│                                 workspace management            │
│   ─────────────────────────────────────────────────────────     │
│   2. Protocols & Networking     MCP, A2A, ACP, ANP,             │
│                                 WebSocket vs HTTP               │
│   ─────────────────────────────────────────────────────────     │
│   1. Sandbox Architecture       Firecracker, gVisor, Docker,    │
│                                 E2B, Modal, Daytona             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

The layers are ordered roughly from infrastructure (bottom) to application (top). Lower layers are more foundational — you can't do observability without a runtime, and you can't do coordination without communication protocols. But the stack is not strictly sequential; many layers are developed in parallel, and the boundaries between them are porous.

---

## Layer 1: Sandbox Architecture

### What It Is

The execution boundary that isolates agent-generated code from the host system and from other tenants. When an agent writes `import os; os.system("rm -rf /")`, the sandbox is what prevents that from being your actual filesystem.

### The Problem It Solves

AI agents execute untrusted code. Whether that code comes from LLM generation, user uploads, or tool calls, it needs to run somewhere safe. The sandbox combines three things: a **boundary** (where isolation is enforced), a **policy** (what the code can touch), and a **lifecycle** (what persists between runs).

### Key Tools and Approaches

The isolation spectrum runs from weakest to strongest:

| Technology | Isolation | Startup | Used By |
|---|---|---|---|
| **Containers (Docker)** | Shared kernel, namespace isolation | 10-50ms | AutoGen, OpenHands |
| **gVisor** | Userspace kernel, syscall interception | ~100ms | OpenAI, Google, Cloud Run, Modal |
| **Firecracker microVMs** | Dedicated guest kernel, KVM | ~125ms | E2B, AWS Lambda, Fly.io, Vercel |
| **Hyper-V** | Type-1 hypervisor | Near-instant (pooled) | Azure Dynamic Sessions, Microsoft Copilot |
| **Wasm/V8 Isolates** | Capability-based, no syscall ABI | <10ms | Cloudflare Workers, Pyodide |

The managed platform market is dominated by three players: **E2B** (Firecracker, $21M raised, powers Perplexity and Manus), **Daytona** ($24M Series A, sub-90ms cold starts, 48.7k GitHub stars), and **Modal** (gVisor, Python-first, GPU support). All three major clouds now have purpose-built sandbox offerings.

### Deep-Dive Potential: HIGH

A standalone report would cover: isolation technology comparison with security analysis, snapshot and Copy-on-Write restore mechanics, warm pool economics, the managed vs. DIY build-vs-buy decision at different scale points, networking and egress control patterns, and the RL training use case (Environment-as-a-Service). We already have a [comprehensive report](research/reports/code-execution-sandboxes-complete.md) covering this layer in depth.

---

## Layer 2: Agent Protocols and Networking

### What It Is

The communication standards that allow agents to discover each other, connect to tools, and exchange information. The protocols that are becoming the TCP/IP of the agent era.

### The Problem It Solves

Without standard protocols, every agent-to-tool connection and every agent-to-agent interaction requires custom integration code. MCP solves the vertical problem (agent-to-tool), A2A solves the horizontal problem (agent-to-agent). Together they enable composable, interoperable agent ecosystems.

### Key Tools and Approaches

Four protocols have emerged, addressing different layers:

| Protocol | Origin | Architecture | Primary Use Case |
|---|---|---|---|
| **MCP** (Model Context Protocol) | Anthropic, Nov 2024 | Client-Server, JSON-RPC 2.0 | LLM-to-tool integration |
| **A2A** (Agent-to-Agent) | Google, Apr 2025 | Peer-like, JSON-RPC 2.0 | Enterprise agent collaboration |
| **ACP** (Agent Communication Protocol) | IBM | Brokered, REST | Multi-framework interoperability |
| **ANP** (Agent Network Protocol) | Community | P2P, JSON-LD | Decentralized agent marketplaces |

MCP has achieved remarkable adoption: 10,000+ published servers, support from Claude, ChatGPT, Gemini, Copilot, VS Code, and Cursor. It became a de facto standard within a year. A2A, donated to the Linux Foundation in June 2025 with 50+ partners, is the leading standard for inter-agent collaboration. The two are complementary, not competing.

The formation of the [Agentic AI Foundation (AAIF)](https://medium.com/@Micheal-Lanham/mcp-a2a-the-tcp-ip-moment-for-ai-agents-bf1927112b07) in December 2025 — co-founded by Anthropic, Block, and OpenAI — aspires to become for agentic AI what the W3C has been for the web.

Transport-level choices matter too: WebSocket wins for persistent agent connections (bidirectional, resilient, lower latency), while HTTP handles synchronous operations, Agent Card discovery, and logs. Most systems use both.

### Deep-Dive Potential: HIGH

A standalone report would cover: protocol-by-protocol technical deep dive, Agent Card discovery mechanisms, security models (OAuth 2.1, mTLS, signed cards), the AAIF governance structure, WebSocket vs HTTP vs gRPC tradeoffs for agent communication, and real-world adoption case studies (ServiceNow, Salesforce, AgentMaster).

---

## Layer 3: File Systems and State Persistence

### What It Is

The mechanisms that give agents access to files and persist state across executions. How you mount data into a sandbox, how you snapshot and restore it, and how agent workspaces survive between sessions.

### The Problem It Solves

Agents need to read files, write outputs, and pick up where they left off. But sandboxes are ephemeral by default — everything disappears when the container or VM is destroyed. The file system layer bridges the gap between ephemeral execution and persistent state.

### Key Tools and Approaches

Three fundamental approaches:

```
Block Devices (virtio-blk)     virtio-fs (shared FS)      Network-Attached (FUSE/NFS)
─────────────────────────     ─────────────────────       ────────────────────────────
Raw disk image per VM          Host dir shared into VM     Remote storage mounted
Fast, simple, not shareable    Near-native, POSIX         Flexible, shareable
Firecracker, Lambda            Kata Containers, QEMU      GCS FUSE, S3, Modal
```

The critical optimization in this layer is **Copy-on-Write snapshot restore**. Instead of copying entire memory into RAM, the system maps the snapshot file as read-only and copies pages lazily on write. This takes restore times from 100-500ms down to 15-50ms, and means 70-90% of snapshot memory is never actually copied from disk.

| Platform | Volume Model | Persistence |
|---|---|---|
| **Modal** | Distributed FS, explicit commit/reload | Indefinite |
| **E2B** | Ephemeral, persist via pause/resume | Until explicit delete |
| **Daytona** | Persistent, archivable to object storage | Indefinite + archive |
| **Fly.io** | Persistent volumes, mountable across restarts | Until deleted |

Per-tenant data isolation patterns include dedicated GCS/S3 buckets with IAM scoping, pre-hydration (download at job start, upload results at end), and hybrid patterns (FUSE for read, local for write).

### Deep-Dive Potential: MEDIUM

A standalone report would cover: snapshot mechanics in depth (full vs diff, CoW restore, the uniqueness problem), volume architecture patterns for multi-tenant isolation, FUSE performance characteristics, the emerging pattern of "branchable" file systems (Daytona's Git-like fork/snapshot/restore), and workspace management for long-running agent sessions.

---

## Layer 4: Permission Systems

### What It Is

The controls that determine what an agent can and cannot do — which tools it can call, which files it can access, which APIs it can reach, and under what conditions. The principle of least privilege applied to autonomous systems.

### The Problem It Solves

Traditional least privilege assumes access can be designed in advance. That assumption [breaks the moment you introduce agents](https://www.strata.io/blog/why-agentic-ai-forces-a-rethink-of-least-privilege/) that decide what to do at runtime. Agents don't follow fixed workflows. They reason, plan, and adapt. What they need to do isn't fully known until execution time. Static permission models fail.

### Key Tools and Approaches

The permission landscape operates at multiple levels:

**Process-level restriction:** Anthropic's [`srt` (sandbox runtime)](https://github.com/anthropic-experimental/sandbox-runtime) uses OS-native primitives (`sandbox-exec` on macOS, `bubblewrap` on Linux) plus proxy-based network filtering. Reduced permission prompts by 84%. No container, no VM — the lightest possible approach.

**Tool access control:** Claude Code's hook system fires at 17 lifecycle events (`PreToolUse`, `PostToolUse`, etc.), allowing external validation before any tool executes. Agents can be restricted to read-only tools, scoped to specific directories, or blocked from specific commands.

**Infrastructure-level policies:** AWS [GENSEC05-BP01](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/gensec05-bp01.html) documents least privilege patterns for agentic workflows. Amazon Bedrock AgentCore's Policy service offers deterministic enforcement outside the LLM reasoning loop using a declarative policy language — a critical distinction from probabilistic guardrails.

**Dynamic, runtime permissions:** The emerging approach treats agent permissions as contextual and ephemeral. OAuth 2.0 token exchange, HashiCorp Vault dynamic secrets, and workload identity attestation (Akeyless) provide just-in-time credentials scoped to the requesting agent's current task.

The OWASP Top 10 for Agentic Applications (December 2025) maps the attack surface across ten categories, from Agent Goal Hijack through Rogue Agents. The governing design principle emerging across the industry: **Least Agency** — agents should be granted the minimum autonomy required for their task.

### Deep-Dive Potential: HIGH

A standalone report would cover: the death of static permissions and what replaces them, per-agent identity architecture (Microsoft Entra Agent ID, workload identity), the OWASP Top 10 for agents in detail, tool-level access control patterns (allowlists, confirmation gates, sandbox-exec profiles), secret management at fleet scale, and the tension between agent autonomy and security constraints.

---

## Layer 5: The Agent Harness

### What It Is

The control layer that wraps around an agent and makes it production-ready. Not the model, not the framework — the infrastructure between the two that determines whether the agent succeeds in the real world.

### The Problem It Solves

As [Harrison Chase (LangChain) articulated](https://blog.langchain.com/agent-frameworks-runtimes-and-harnesses-oh-my/), there's a meaningful distinction between three levels of abstraction:

- **Agent Framework** (LangChain, CrewAI, OpenAI Agents SDK): Abstractions and mental models. Makes it easy to get started.
- **Agent Runtime** (LangGraph, Temporal, Inngest): Production infrastructure — durable execution, streaming, human-in-the-loop, thread persistence.
- **Agent Harness** (DeepAgents, Claude Code, Atomic): Batteries-included. Default prompts, opinionated tool handling, filesystem access, planning tools. A "general purpose version of Claude Code."

Five independent teams — [OpenAI, Anthropic, Huntley, Horthy, and Vasilopoulos](https://alexlavaee.me/blog/harness-engineering-why-coding-agents-need-infrastructure/) — all converged on the same finding: **the bottleneck is infrastructure, not intelligence.** Coding agents become reliable only when you build the right scaffolding around them.

### Key Tools and Approaches

The converging best practices form [four pillars of harness engineering](https://alexlavaee.me/blog/harness-engineering-why-coding-agents-need-infrastructure/):

1. **Context Architecture** — Tiered, progressive disclosure. Agents receive exactly the context they need for their current task. Performance degrades beyond ~40% context utilization. Overloading agents with tools, verbose docs, and accumulated history makes them worse, not better.

2. **Agent Specialization** — A focused agent with restricted tools outperforms a general-purpose agent with full access. Not just organizational — it's a context management strategy.

3. **Persistent Memory** — Progress persists on disk, not in the context window. Each new session rebuilds context from filesystem artifacts (AGENTS.md, progress files, research docs).

4. **Structured Execution** — Separate thinking from typing. Research, plan, execute, verify — each in controlled phases with human-in-the-loop gates between them.

Harness extensibility models differ across implementations. Claude Code extends through skills (lazy-loaded instruction files), MCP (server-based tool integration), and hooks (lifecycle event handlers). The design principle is progressive disclosure — context stays lean until needed.

### Deep-Dive Potential: VERY HIGH

This is arguably the most important layer for practitioners. A standalone report would cover: the framework vs runtime vs harness taxonomy in depth, the four pillars with production case studies (OpenAI's million-line codebase, Anthropic's C compiler, Huntley's Ralph loop), context window utilization research (the "smart zone" vs "dumb zone"), specification-driven development as the next evolution, and the emerging tools (Atomic, Claude Agent SDK, DeepAgents).

---

## Layer 6: Observability and Tracing

### What It Is

The telemetry and monitoring infrastructure that makes agent behavior visible, debuggable, and accountable. Not traditional APM — agent-specific observability that captures decision graphs, token costs, and semantic correctness.

### The Problem It Solves

AI agents violate every assumption of traditional monitoring. They're non-deterministic (same input, different output). They have compound operations (one user request triggers ten LLM calls and five tool executions). Token cost is a runtime variable, not a fixed resource. And agents can fail gracefully from a systems perspective (HTTP 200, no exception) while producing completely wrong outputs.

### Key Tools and Approaches

The industry is converging on [OpenTelemetry (OTel)](https://zylos.ai/research/2026-02-28-opentelemetry-ai-agent-observability) as the standard telemetry layer, with the GenAI Semantic Conventions SIG defining attribute schemas for:

- **LLM client spans** — `gen_ai.system`, `gen_ai.request.model`, `gen_ai.usage.input_tokens`, `gen_ai.usage.output_tokens`
- **Agent spans** — `invoke_agent {gen_ai.agent.name}` with agent ID, description, operation name
- **Tool execution spans** — `execute_tool {tool_name}` as children of the agent or LLM span

The trace hierarchy mirrors the agent's decision graph:

```
[invoke_agent: research-agent]          <- root agent span
  [chat: anthropic]                     <- LLM call to plan
  [execute_tool: web_search]            <- tool call #1
  [chat: anthropic]                     <- LLM call to process results
  [execute_tool: write_file]            <- tool call #2
  [chat: anthropic]                     <- final synthesis
```

Critical AI-specific failure modes that traces expose: **stuck tool loops** (alternating LLM/tool spans with no forward progress), **token cost spikes** (per-span attribution reveals which agent consumes 60% of the budget), and **context propagation failures** in multi-agent pipelines (broken W3C TraceContext means disconnected traces).

**The observability stack landscape:**

| Category | Tools |
|---|---|
| Open-source self-hosted | Jaeger, Grafana Tempo, OpenSearch |
| LLM-specific | Langfuse, Arize Phoenix, LangSmith |
| Auto-instrumentation | OpenLLMetry (Traceloop), supports 20+ providers |
| Enterprise | Datadog, Honeycomb, New Relic (all now support GenAI conventions natively) |

Tail-based sampling is the right default for agent systems: keep 100% of error traces, all traces over 5 seconds, all complex traces (20+ spans), and 5% of routine successes. This keeps debugging maximally useful without excessive storage cost.

### Deep-Dive Potential: HIGH

A standalone report would cover: OpenTelemetry GenAI Semantic Conventions specification deep dive, practical instrumentation patterns (auto vs manual), tail-based sampling configuration, token cost attribution and budgeting, the purpose-built vs general-purpose observability platform decision, and debugging patterns for the five most common agent failure modes.

---

## Layer 7: Agent Lifecycle Management

### What It Is

The operational discipline of managing agents as long-lived products — from initialization through execution, learning, adaptation, and eventual retirement. The agent equivalent of DevOps/SRE practices.

### The Problem It Solves

You don't just deploy one agent. You deploy dozens, then hundreds. They need versioning, rolling updates, health monitoring, credential management, configuration that doesn't drift, and governance that scales. This is the ["agent sprawl"](https://boomi.com/blog/ai-agent-governance-framework/) problem: 82% of organizations expect to integrate AI agents, but IT teams can't track what agents exist, whether they work properly, or how to coordinate them.

### Key Tools and Approaches

**The Control Plane concept** — borrowed from Kubernetes — is the dominant mental model. A control plane for agents handles deployment, task routing, monitoring, permissions, and coordination. [AgentCenter](https://agentcenter.cloud/blogs/ai-agent-control-plane-managing-agents-at-scale) and similar platforms are emerging to fill this role.

**Enterprise platforms:**

| Platform | Pricing | Key Feature |
|---|---|---|
| **Google Vertex AI Agent Engine** | $0.00994/vCPU-hr | A2A integration |
| **Azure AI Foundry Agent Service** | GA May 2025, 10K+ customers | Fleet health dashboards |
| **AWS AgentCore** | $0.0895/vCPU-hr | Framework-agnostic runtime |

**Lifecycle stages:** The [agent lifecycle](https://www.azilen.com/learning/agent-lifecycle/) defines how an agent evolves over time — from creation and initialization to execution, learning, adaptation, and eventual retirement. Key concerns at each stage:

- **Configuration management:** Layered config (Global > Fleet > Instance > Runtime), Git-versioned, with drift detection. GitOps (Argo CD, Flux CD) is the delivery mechanism.
- **Version management:** Phased rollouts (canary -> broader), blue/green deployment, state compatibility across versions. In-flight task continuity during updates.
- **Identity and credentials:** Per-instance unique identities, workload identity attestation, dynamic secrets (HashiCorp Vault), zero-secret architecture.
- **Fleet monitoring:** The Agent Card pattern (A2A) enables decentralized health monitoring — each agent publishes capabilities and health at `/.well-known/agent.json`.

The emerging discipline is called **AgentOps** — [Microsoft's term](https://techcommunity.microsoft.com/t5/microsoft-foundry-blog/from-zero-to-hero-agentops-end-to-end-lifecycle-management-for/ba-p/4484922) for end-to-end lifecycle management, analogous to DevOps but specifically designed for the probabilistic, autonomous nature of agent systems.

### Deep-Dive Potential: HIGH

A standalone report would cover: the AgentOps discipline in depth, control plane architectures, configuration drift detection and remediation, agent versioning strategies (including state migration), identity management at fleet scale (Entra Agent ID, workload attestation), the economics of agent fleet operations, and the governance frameworks (OWASP, NIST, AAGATE).

---

## Layer 8: Memory and Context Persistence

### What It Is

The systems that allow agents to remember across sessions — user preferences, past decisions, learned patterns, and accumulated knowledge. The difference between a goldfish and a colleague.

### The Problem It Solves

LLMs are stateless. Each invocation starts with a blank context window. For short tasks, this is invisible. For long-horizon tasks — codebase migrations, multi-day projects, ongoing user relationships — the lack of memory creates ["architectural amnesia"](https://medium.com/@nraman.n6/agent-memory-wars-why-your-multi-agent-system-forgets-what-matters-and-how-to-fix-it-a9a1901df0d9). Agents make the same mistakes repeatedly, re-discover previously resolved issues, and lose continuity between sessions.

### Key Tools and Approaches

Memory has become a [first-class architectural primitive](https://medium.com/@vinniesmandava/the-agentic-ai-infrastructure-landscape-in-2025-2026-a-strategic-analysis-for-tool-builders-b0da8368aee2), no longer an afterthought. The modern taxonomy organizes memory by form, function, and dynamics:

**Memory hierarchy (Letta/MemGPT model):**

```
┌─────────────────────────────────────────────┐
│  Core Memory      Always in-context.        │
│                   Self-edited by agent via   │
│                   tool calls.               │
├─────────────────────────────────────────────┤
│  Recall Memory    Searchable conversation   │
│                   history. Retrieved on     │
│                   demand.                   │
├─────────────────────────────────────────────┤
│  Archival Memory  External vector/graph DB. │
│                   Long-term knowledge.      │
│                   Survives indefinitely.    │
└─────────────────────────────────────────────┘
```

**Three dominant memory infrastructure providers:**

| Provider | Approach | Key Innovation |
|---|---|---|
| **Letta** (ex-MemGPT) | OS-inspired memory hierarchy | Sleep-time compute: background agents reorganize memory during idle |
| **Mem0** | Hybrid datastore (vector + KV + graph) | $24M Series A, AWS exclusive memory provider, highest accuracy on benchmarks |
| **Zep (Graphiti)** | Temporal knowledge graphs | Bi-temporal model: tracks when events occurred and when they were ingested |

**Production patterns:** The dominant approach uses hybrid storage backends — vector databases for semantic retrieval, graph databases for entity relationships, and relational databases for structured state. Filesystem-backed memory (CLAUDE.md, AGENTS.md, research docs) is the simplest and most battle-tested pattern for coding agents.

**Multi-agent memory is the hardest unsolved challenge.** Multi-agent systems consume roughly 15x more tokens than single-agent chats. Emerging solutions include centralized shared memory graphs, memory block coordination APIs, and transactive memory systems that track "who knows what" across agent teams.

### Deep-Dive Potential: VERY HIGH

A standalone report would cover: the memory taxonomy in depth (episodic, semantic, procedural, working), vector database comparison for agent use cases (Pinecone, Weaviate, Chroma, pgvector), the Letta vs Mem0 vs Zep architectural comparison, sleep-time compute and background memory organization, multi-agent memory coordination patterns, the relationship between memory and context engineering, and the practical patterns that work today (filesystem-backed vs vector-backed vs hybrid).

---

## Layer 9: Multi-Agent Coordination

### What It Is

The patterns and infrastructure for multiple agents working together — task distribution, inter-agent communication, conflict resolution, and result synthesis.

### The Problem It Solves

Single agents hit context limits, can't parallelize work, and suffer from anchoring bias when debugging. Multi-agent systems divide complex work across specialized agents, each with focused context and appropriate tools. The challenge is coordination: how do agents divide work, avoid conflicts, share findings, and produce coherent output?

### Key Tools and Approaches

**Orchestration frameworks** have consolidated into a tiered ecosystem:

| Framework | Position | Key Feature |
|---|---|---|
| **LangGraph 1.0** | Market leader (~400 companies, ~90M monthly downloads) | Graph-based execution with cycles, conditionals, parallel |
| **CrewAI** | Strong second tier for role-based orchestration | Scaling walls after 6-12 months |
| **Microsoft Agent Framework** | Merger of AutoGen + Semantic Kernel | GA expected early 2026 |
| **OpenAI Agents SDK** | Minimalist (4 primitives: agents, handoffs, guardrails, sessions) | Leaves orchestration to the developer |
| **AWS Bedrock AgentCore** | Framework-agnostic managed platform | Runs LangGraph, CrewAI, ADK, or OpenAI SDK |
| **Claude Code Agent Teams** | First-party multi-agent for coding | Independent peers with shared task list and peer messaging |

**Coordination patterns by maturity:**

```
Production-Proven          Production-Ready         Research Stage
──────────────────         ────────────────         ──────────────
Supervisor-worker          Planner-executor         Collaborative debate
Sequential pipelines       Hierarchical multi-agent Swarm intelligence
                           Handoff/relay
```

**Claude Code Agent Teams** (shipped with Opus 4.6) represent the most interesting development in coding-specific coordination. Unlike subagents that report back to a parent, teammates are independent Claude instances that message each other directly, self-claim tasks from a shared list, and coordinate without routing through a lead. The killer pattern: **competing hypotheses** — multiple agents investigate different theories and actively try to disprove each other, eliminating anchoring bias.

### Deep-Dive Potential: HIGH

A standalone report would cover: orchestration framework comparison (LangGraph vs CrewAI vs Microsoft vs OpenAI SDK), coordination patterns with production case studies, the competing hypotheses pattern for debugging, Claude Code Agent Teams architecture and usage patterns, token economics of multi-agent systems, the anti-patterns (when NOT to use multiple agents), and the emerging agent-to-agent protocol standards for cross-vendor coordination.

---

## Layer 10: Deployment and Infrastructure-as-Code

### What It Is

The CI/CD pipelines, containerization strategies, and infrastructure automation that move agents from development to production. The same discipline that matured for web services, applied to probabilistic, autonomous systems.

### The Problem It Solves

Agent deployments have unique challenges that traditional CI/CD doesn't address. Prompts, tool definitions, and model configurations all change agent behavior and all need versioning. Evaluation gates are probabilistic, not deterministic. Shadow deployments (running both old and new versions, only returning the old version's output) are critical for validating behavioral changes on real traffic.

### Key Tools and Approaches

**Containerization:** Standard Docker/OCI containers remain the deployment unit. Multi-stage builds keep images small. Health check endpoints verify both the container and external dependencies (LLM APIs, databases). E2B uses OCI images converted to rootfs that Firecracker can boot.

**Dagger** stands out as the most interesting tool in this layer for agent deployments. It's a programmable CI/CD engine where pipelines are code (Go, Python, TypeScript), not YAML. Pipelines run inside containers, behaving identically on laptops and CI servers. [Dagger now explicitly pitches agent containerization](https://thenewstack.io/ai-dev-tools-how-to-containerize-agents-using-dagger/) as a use case. Its BuildKit-based engine handles caching, parallelism, and execution through a GraphQL API.

**Deployment topologies** for agents:

| Pattern | Best For | Key Challenge |
|---|---|---|
| **Serverless** (Lambda, Cloud Run) | Stateless agents, variable traffic | Cold starts, 15-min timeout limits |
| **Containerized** (ECS, Kubernetes) | Stateful agents, consistent environments | Orchestration complexity |
| **Dedicated VMs** | High-volume, latency-sensitive | Cost, capacity planning |
| **Hybrid** | Most production systems | Operational complexity |

**Agent-specific CI/CD concerns:**

- **Evaluation gates** replace unit tests as the primary quality check. LLM metrics (faithfulness, hallucination rate, tool selection accuracy) gate production deployments. [Braintrust](https://medium.com/@vinniesmandava/the-agentic-ai-infrastructure-landscape-in-2025-2026-a-strategic-analysis-for-tool-builders-b0da8368aee2) is the most CI/CD-native evaluation platform, with a dedicated GitHub Action.
- **Shadow deployment** routes live traffic to both old and new agent versions, but only returns the old version's response. The new agent processes silently for offline comparison.
- **Version control extends beyond code** to prompts, tool definitions, and configuration — everything that changes agent behavior.

**GitOps** for agent fleets: treat a Git repository as the single source of truth. Argo CD or Flux CD watches the repo and reconciles live state with declared state. The same pattern from Kubernetes, applied to agent configuration and deployment.

### Deep-Dive Potential: MEDIUM

A standalone report would cover: Dagger for agent pipelines in depth, evaluation-gated CI/CD patterns, shadow deployment implementation, GitOps for agent fleet configuration, the containerization decision (standard containers vs microVMs vs serverless), infrastructure-as-code patterns specific to agent systems, and cost optimization strategies for agent compute.

---

## The Series Map

Each layer described above can become a standalone deep-dive research report. Here's how they map to a content series, ordered by editorial priority:

| # | Report Title | Priority | Existing Coverage |
|---|---|---|---|
| 1 | **The Agent Harness: Why Infrastructure Beats Intelligence** | Very High | None (new territory) |
| 2 | **Agent Memory Wars: Architecture for Persistence** | Very High | None |
| 3 | **The Permission Problem: Least Privilege for Autonomous Systems** | High | None |
| 4 | **MCP + A2A: The Protocol Stack for Agent Communication** | High | None |
| 5 | **Observability for Agents: OpenTelemetry and the GenAI SIG** | High | None |
| 6 | **AgentOps: Lifecycle Management at Fleet Scale** | High | None |
| 7 | **Multi-Agent Coordination: Patterns That Work** | High | Agent Teams report exists |
| 8 | **Code Execution Sandboxes: The Complete Guide** | Medium | Comprehensive report exists |
| 9 | **Agent Deployment: CI/CD, Dagger, and GitOps** | Medium | None |
| 10 | **File Systems and State: Snapshots, Volumes, and Workspaces** | Medium | Partially covered in sandbox report |

Reports 1-6 are the highest priority because they address the least-documented, most-impactful layers. Reports 7-8 can build on existing research. Reports 9-10 have narrower audiences but fill important gaps.

The series should be read as a progressive build-up: start with the harness (conceptual foundation), then memory and permissions (the hardest unsolved problems), then protocols and observability (the standardization wave), then lifecycle and coordination (operational maturity), and finally sandboxes, deployment, and file systems (well-documented infrastructure).

---

## Key Takeaways

1. **The agent stack has ten distinct layers, and most teams are solving fewer than half of them.** The gap between demo and production is not a model problem — it's an infrastructure problem distributed across isolation, permissions, memory, observability, coordination, and deployment.

2. **The harness is the most important and least documented layer.** Five independent teams converged on the same finding: the bottleneck is infrastructure, not intelligence. Better models make harness engineering more important, not less, because more capability unlocks more autonomy, and more autonomy demands better guardrails.

3. **Memory is the hardest unsolved infrastructure problem.** Single-agent memory has credible solutions (Letta, Mem0, Zep). Multi-agent memory coordination — where agents need shared understanding of "who knows what" — remains genuinely unsolved. The team that cracks this captures a category.

4. **Two protocols will define the agent era.** MCP (agent-to-tool) and A2A (agent-to-agent), both under Linux Foundation governance, are becoming the TCP/IP of agents. Multi-protocol coexistence — like HTTP, WebSocket, and gRPC today — is the future.

5. **OpenTelemetry's GenAI conventions are the observability standard.** The GenAI SIG has defined span types for LLM calls, agent invocations, and tool executions. Major vendors (Datadog, Honeycomb, New Relic) support them natively. Instrumenting now positions you to benefit from the ecosystem without vendor lock-in.

6. **AgentOps is the new DevOps.** Managing agents as long-lived products — with versioning, rolling updates, identity management, drift detection, and governance — is becoming a distinct operational discipline. The control plane concept from Kubernetes maps directly to agent fleets.

7. **Evaluation infrastructure is the critical missing layer across the entire stack.** The best models score under 23% on realistic benchmarks. Only 4 of 30 deployed agent systems provide agent-specific system cards. The companies that make agent behavior measurable and trustworthy will capture outsized value.

---

## Predictions

1. **The "agent harness" will become a recognized product category by end of 2026.** Just as "observability" became distinct from "monitoring," the harness — context architecture, specialization, persistent memory, structured execution — will be recognized as distinct from frameworks and runtimes. LangChain's DeepAgents is the first mover, but the race is wide open.

2. **MCP and A2A will achieve HTTP-level ubiquity within 18 months.** Every major agent framework will support both protocols natively. Custom integration code between agents and tools will become as quaint as writing raw socket connections.

3. **Multi-agent memory coordination will be the next $100M+ infrastructure category.** The 15x token multiplier in multi-agent systems is unsustainable. Whoever builds efficient shared memory that reduces redundant context loading across agent teams wins big.

4. **The managed sandbox market will consolidate to 2-3 winners by 2027.** E2B, Daytona, and Modal are the current leaders, but the cloud providers (AWS AgentCore, GKE Agent Sandbox, Azure Dynamic Sessions) have distribution advantages that are hard to overcome.

5. **"AgentOps engineer" will be a real job title within 12 months.** Just as DevOps and SRE emerged from the need to operate complex distributed systems, AgentOps will emerge from the need to operate fleets of autonomous agents. The skillset combines traditional SRE with prompt engineering, evaluation design, and identity management.

6. **The evaluation layer will become the most valuable part of the stack.** Models and protocols are commoditizing. The companies that can reliably measure whether an agent is working correctly — across multi-step reasoning, tool use, and behavioral consistency — will be the ones enterprises pay for.

---

## Sources

### Infrastructure Landscape
- [The Agentic AI Infrastructure Landscape 2025-2026](https://medium.com/@vinniesmandava/the-agentic-ai-infrastructure-landscape-in-2025-2026-a-strategic-analysis-for-tool-builders-b0da8368aee2) — Sri Srujan Mandava
- [The Production Stack for Agentic AI](https://www.nylas.com/blog/agentic-ai-production-stack/) — Nylas
- [Deploying AI Agents to Production](https://machinelearningmastery.com/deploying-ai-agents-to-production-architecture-infrastructure-and-implementation-roadmap/) — MachineLearningMastery
- [Agent Toolkit or Production Platform](https://logic.inc/resources/agent-toolkit-vs-production-platform) — Logic

### The Agent Harness
- [Agent Frameworks, Runtimes, and Harnesses](https://blog.langchain.com/agent-frameworks-runtimes-and-harnesses-oh-my/) — Harrison Chase, LangChain
- [How to Harness Coding Agents with the Right Infrastructure](https://alexlavaee.me/blog/harness-engineering-why-coding-agents-need-infrastructure/) — Alex Lavaee
- [Modern Agent Harness Blueprint 2026](https://gist.github.com/amazingvince/52158d00fb8b3ba1b8476bc62bb562e3) — amazingvince
- [Skills, Forks, and Self-Surgery: How Agent Harnesses Grow](https://michaellivs.com/blog/three-ways-to-extend-an-agent-harness/) — Michael Livs
- [Agent Harness: The Operating Layer Behind Reliable AI Agents](https://conais.com/agent-harness/) — CONAIS
- [Guide to Agent Harnesses](https://www.useparagon.com/learn/guide-to-agent-harnesses/) — Paragon

### Protocols and Networking
- [Agent-to-Agent Communication Protocol Standards](https://zylos.ai/research/2026-02-15-agent-to-agent-communication-protocols) — Zylos Research
- [MCP + A2A: The TCP/IP Moment for AI Agents](https://medium.com/@Micheal-Lanham/mcp-a2a-the-tcp-ip-moment-for-ai-agents-bf1927112b07) — Micheal Lanham
- [MCP vs A2A: Which Protocol Should You Use?](https://workos.com/blog/mcp-vs-a2a) — WorkOS
- [Implementing MCP & A2A Protocols](https://staituned.com/learn/midway/mcp-a2a-protocols-ai-agents-playbook) — stAI tuned
- [MCP vs A2A Guide](https://auth0.com/blog/mcp-vs-a2a/) — Auth0

### Observability and Tracing
- [OpenTelemetry for AI Agents](https://zylos.ai/research/2026-02-28-opentelemetry-ai-agent-observability) — Zylos Research
- [AI Agent Observability: Evolving Standards](https://opentelemetry.io/blog/2025/ai-agent-observability/) — OpenTelemetry
- [AG2 OpenTelemetry Tracing](https://docs.ag2.ai/latest/docs/blog/2026/02/08/AG2-OpenTelemetry-Tracing/) — AG2
- [Observing Agentic AI with Grafana Cloud](https://grafana.com/blog/observing-agentic-ai-workflows-with-grafana-cloud-opentelemetry-and-the-openai-agents-sdk/) — Grafana Labs
- [What Is AI Agent Observability? Complete Guide 2026](https://spanora.ai/blog/what-is-ai-agent-observability-complete-guide-2026) — Spanora
- [Agent Observability for Tool-Using Agents](https://www.agentixlabs.com/blog/general/agent-observability-for-tool-using-agents-stop-costly-loops/) — Agentix Labs

### Lifecycle and Fleet Management
- [AI Agent Fleet Management and Multi-Instance Orchestration](https://zylos.ai/research/2026-02-19-ai-agent-fleet-management) — Zylos Research
- [AgentOps: End-to-End Lifecycle Management](https://techcommunity.microsoft.com/t5/microsoft-foundry-blog/from-zero-to-hero-agentops-end-to-end-lifecycle-management-for/ba-p/4484922) — Microsoft
- [Agent Lifecycle Management](https://orq.ai/blog/agent-lifecycle-management) — Orq.ai
- [Agent Lifecycle in Agentic AI](https://www.azilen.com/learning/agent-lifecycle/) — Azilen
- [The AI Agent Control Plane](https://agentcenter.cloud/blogs/ai-agent-control-plane-managing-agents-at-scale) — AgentCenter
- [AgentOps: Operationalizing AI Agents](https://www.uipath.com/blog/ai/agent-ops-operationalizing-ai-agents-for-enterprise) — UiPath

### Memory and Persistence
- [Agent Memory Wars](https://medium.com/@nraman.n6/agent-memory-wars-why-your-multi-agent-system-forgets-what-matters-and-how-to-fix-it-a9a1901df0d9) — NJ Raman
- [Agent Memory Systems: Context to Persistent Storage](https://mbrenndoerfer.com/writing/agent-memory-systems-architecture) — Michael Brenndoerfer
- [Memory Management for AI Agents](https://medium.com/@fred-zhang/memory-management-for-ai-agents-from-cognitive-architectures-to-context-engineering-to-293ef6a4ccab) — Chenyu Zhang
- [Cross-Session Agent Memory](https://mgx.dev/insights/cross-session-agent-memory-foundations-implementations-challenges-and-future-directions/d03dd30038514b75ad4cbbda2239c468) — MGX
- [Managing State Across Interactions](https://mbrenndoerfer.com/writing/managing-state-across-interactions-agent-lifecycle-persistence) — Michael Brenndoerfer

### Permissions and Security
- [NVIDIA: Practical Security Guidance for Sandboxing Agentic Workflows](https://developer.nvidia.com/blog/practical-security-guidance-for-sandboxing-agentic-workflows-and-managing-execution-risk/) — NVIDIA
- [AWS: Least Privilege for Agentic Workflows](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/gensec05-bp01.html) — AWS
- [Why Agentic AI Forces a Rethink of Least Privilege](https://www.strata.io/blog/why-agentic-ai-forces-a-rethink-of-least-privilege/) — Strata
- [Securing AI Agents: Principles of Least Privilege](https://security.furybee.org/articles/securing-ai-agents) — FuryBee
- [Action Restrictions and Permissions for AI Agents](https://mbrenndoerfer.com/writing/action-restrictions-and-permissions-ai-agents) — Michael Brenndoerfer

### Multi-Agent Coordination
- [The Orchestration of Multi-Agent Systems](https://arxiv.org/html/2601.13671v1) — Adimulam, Gupta, Kumar
- [AI Agent Orchestration for Production Systems](https://redis.io/blog/ai-agent-orchestration/) — Redis
- [Claude Code Agent Teams Report](research/.scratchpad/2026-02-06-claude-code-agent-teams.md) — Internal research

### Deployment and IaC
- [AI Dev Tools: How to Containerize Agents Using Dagger](https://thenewstack.io/ai-dev-tools-how-to-containerize-agents-using-dagger/) — The New Stack
- [How to Run Dagger CI Pipelines in Docker](https://oneuptime.com/blog/post/2026-02-08-how-to-run-dagger-ci-pipelines-in-docker/view) — OneUptime
- [Dagger.io](https://dagger.io/) — Dagger

### Sandbox Architecture
- [Code Execution Sandboxes: Complete Guide](research/reports/code-execution-sandboxes-complete.md) — Internal research
- [Agent Sandbox Architecture Evaluation](research/.scratchpad/2026-02-04-agent-sandbox-architecture-evaluation.md) — Internal research
