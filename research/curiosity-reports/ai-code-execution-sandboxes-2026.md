# AI Code Execution Sandboxes: Production Use Cases Across the Industry

**Date:** 2-07-26
**Category:** Research Report

---

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [Background](#background)
3. [Coding Assistants / IDEs](#1-coding-assistants--ides)
4. [AI Agent Platforms (Big Labs)](#2-ai-agent-platforms-big-labs)
5. [Code Evaluation & Benchmarking](#3-code-evaluation--benchmarking)
6. [RL Training Loops](#4-rl-training-loops)
7. [Enterprise Agent Deployments](#5-enterprise-agent-deployments)
8. [Open Source Agent Frameworks](#6-open-source-agent-frameworks)
9. [Dedicated Sandbox Infrastructure Providers](#7-dedicated-sandbox-infrastructure-providers)
10. [Key Takeaways](#key-takeaways)
11. [Predictions](#predictions)

---

## Executive Summary

Code execution sandboxing has become the single most critical infrastructure layer for AI agents. Every major AI lab, every coding assistant, every agent framework, and every RL training pipeline needs the same thing: a way to run untrusted, LLM-generated code safely, at scale, and fast. The solutions have converged on a surprisingly narrow set of underlying technologies --- Firecracker microVMs, gVisor application kernels, Docker/OCI containers, and WebAssembly runtimes --- but the products and platforms built on top of them vary wildly in maturity, pricing, and design philosophy.

The market has exploded. Cursor alone produces nearly 1 billion lines of accepted code per day. E2B raised $21M, Daytona raised $24M, and Runloop emerged from the former Google File System tech lead. Meanwhile, the big labs (OpenAI, Anthropic, Google) have each built their own internal sandboxing stacks, and open-source frameworks like AutoGen and LangChain have standardized on Docker as the default execution backend.

The clearest signal: sandboxing is no longer optional. It is table-stakes infrastructure for anyone building with LLMs that generate code.

---

## Background

An AI code sandbox is an isolated execution environment where LLM-generated code can run without risk to the host system. The concept dates back to Unix `chroot` in the 1980s, but the modern incarnation is purpose-built for the agent era: ephemeral, fast-starting, API-driven, and designed to scale to thousands of concurrent sessions.

The isolation spectrum, from weakest to strongest:

```
Process-level    Container/namespace    gVisor (app kernel)    MicroVM (Firecracker)    Full VM
   (weak)                                                                                (strong)
    |__________________|___________________|________________________|___________________|
  ~0ms start          ~50ms               ~100ms                   ~125ms              ~seconds
  No isolation     Namespace only      Syscall interception    Hardware isolation    Full hypervisor
```

The key technologies in play:

| Technology | Isolation Model | Cold Start | Used By |
|---|---|---|---|
| **Firecracker microVMs** | Hardware-level (KVM) | 100-125ms | E2B, AWS Lambda, Daytona |
| **gVisor** | Application kernel (syscall interception) | ~100ms | OpenAI, Google, Modal |
| **Docker/OCI Containers** | Linux namespaces + cgroups | ~300ms-seconds | SWE-bench, AutoGen, CrewAI |
| **WebAssembly (Pyodide)** | Language runtime sandbox | ~50ms | LangChain Sandbox, StackBlitz |
| **V8 Isolates** | JS engine isolation | <5ms | Cloudflare Workers |
| **Kata Containers** | Lightweight VM + container API | ~200ms | Northflank |
| **`sandbox-exec` / `bubblewrap`** | OS-level process restriction | ~0ms | Anthropic `srt` tool |

---

## 1. Coding Assistants / IDEs

### Cursor

**How it works:** Cursor is a VS Code fork that uses a "shadow workspace" architecture. Rather than sandboxing code execution in a remote VM, Cursor gives the AI access to a hidden, parallel instance of the user's development environment.

- **Shadow Workspaces** (documented in [cursor.com/blog/shadow-workspace](https://cursor.com/blog/shadow-workspace)): The AI iterates in a copy of the user's dev environment where it can see lints, go to definitions, and run code --- without the user seeing half-finished work.
- **Agent Mode** (Cursor 2.0): Runs up to 8 AI agents simultaneously. Code execution happens locally on the user's machine --- there is no remote sandbox. The user's local environment IS the sandbox. Cursor mitigates risk through its "Composer" model and permission prompts.
- **BugBot**: Cursor's automated PR review agent processes 2 million monthly PR reviews using an agentic architecture, running checks in isolated environments.
- **Scale data point**: Cursor serves billions of AI code completions daily and produces ~1 billion lines of accepted code per day ([ByteByteGo analysis](https://blog.bytebytego.com/p/how-cursor-serves-billions-of-ai)).
- **Security**: Cursor 2.0 added a sandbox environment with data privacy controls. Code is processed server-side for AI inference but execution remains local ([Skywork analysis](https://skywork.ai/blog/vibecoding/cursor-2-0-security-privacy/)).

**Key insight:** Cursor does NOT use remote sandboxes for code execution. It relies on the developer's own machine. The "sandbox" is more about AI iteration space (shadow workspaces) than execution isolation.

### Windsurf (Codeium)

**How it works:** Windsurf's "Cascade" agent tracks user actions (edits, terminal commands, clipboard) to infer intent. Like Cursor, code execution happens locally.

- **Flow Awareness**: Cascade tracks file edits, terminal commands, and clipboard to stay synchronized with the developer's workflow.
- **Lint Auto-fix**: Cascade detects and fixes lint errors it generates, functioning as a built-in quality gate.
- **DevBox Integration**: Windsurf integrates with cloud development environments like [Sealos DevBox](https://sealos.io/blog/windsurf-devbox) for users who want remote isolated environments. The DevBox provides an "unbreakable cloud environment" that can be snapshotted and restored.
- **No built-in sandbox**: Like Cursor, Windsurf executes code on the user's local machine by default.

### GitHub Copilot Coding Agent

**How it works:** GitHub's approach is fundamentally different from Cursor/Windsurf. The Copilot coding agent runs in an **ephemeral cloud environment powered by GitHub Actions**.

- **GitHub Actions runner**: Each task gets its own ephemeral development environment, powered by GitHub Actions, where the agent can explore code, make changes, execute tests and linters ([GitHub Docs](https://docs.github.com/en/copilot/customizing-copilot/customizing-the-development-environment-for-copilot-coding-agent)).
- **Customizable environments**: Users can preinstall tools/dependencies, set environment variables, and upgrade from standard GitHub-hosted runners to larger runners.
- **Isolation model**: Standard GitHub Actions container isolation (Docker-based). The agent works in a branch, creates PRs for review.
- **Generally available**: Shipped GA in mid-2025 across Pro, Pro+, Business, and Enterprise plans.
- **No local execution**: The agent never runs on the developer's machine. Everything happens in GitHub's cloud.

**Key insight:** GitHub's approach is the most "sandboxed by default" of the coding assistants. By running in Actions runners, there is zero risk to developer machines, but the tradeoff is latency and the inability to use the developer's custom local environment.

### Replit Agent

**How it works:** Replit built a purpose-designed infrastructure stack from the ground up for AI agent code execution.

- **Snapshot Engine** ([blog.replit.com/inside-replits-snapshot-engine](https://blog.replit.com/inside-replits-snapshot-engine)): Uses Copy-on-Write (CoW) at the block device level. The AI agent can fork the entire filesystem instantly, try risky changes, and revert if they fail. This is like "quick save/load" for the development environment.
- **Snapshotable databases**: The agent only has access to a development database, never production. Database state can be snapshotted and rolled back.
- **Dev/prod split**: Hard separation between development and production environments. The agent cannot touch production.
- **Decision-Time Guidance** ([blog.replit.com/decision-time-guidance](https://blog.replit.com/decision-time-guidance)): The execution environment itself provides intelligent feedback to help the agent course-correct. Linter errors, test failures, and build errors are fed back as structured signals.
- **Hybrid security scanning**: Combines deterministic static analysis and dependency scanning with LLM-based reasoning. Their research shows AI-only security scans are nondeterministic --- identical vulnerabilities receive different classifications based on minor syntactic changes ([blog.replit.com/securing-ai-generated-code](https://blog.replit.com/securing-ai-generated-code)).

**Key insight:** Replit's approach is the most sophisticated of any coding assistant. The snapshot engine is genuinely novel infrastructure that solves the "agent broke everything" problem at the filesystem level rather than through permission prompts.

### Devin (Cognition)

**How it works:** Devin operates as a fully autonomous AI software engineer with its own complete cloud development environment.

- **Architecture options** ([docs.devin.ai/enterprise/deployment/overview](https://docs.devin.ai/enterprise/deployment/overview)):
  - **Enterprise SaaS**: Cognition-hosted, multi-tenant
  - **Dedicated SaaS with Private Networking**: Isolated compute per customer
  - **Customer Hosted VPC**: Runs entirely within the customer's AWS or Azure VPC
- **Session-based**: Each Devin session gets its own isolated environment with IDE, terminal, browser, and shell.
- **Enterprise features**: Okta SSO, RBAC, VPN configuration for accessing private repos and internal services.
- **Real-world deployment**: Nubank used Devin to refactor millions of lines of their core ETL monolith, achieving 8x engineering time efficiency and 20x cost savings.
- **Integration depth**: Connects to GitHub, GitLab, Bitbucket, Linear, Jira, Slack, and Microsoft Teams.

---

## 2. AI Agent Platforms (Big Labs)

### OpenAI Code Interpreter / Codex

**Code Interpreter (ChatGPT):**

The most thoroughly reverse-engineered sandbox in the industry, thanks to security researchers.

- **Isolation**: Runs on **gVisor**, Google's application kernel that intercepts syscalls in userspace. Confirmed by `dmesg` output from within the sandbox ([Ryan Govostes analysis](https://ryan.govost.es/2025/openai-code-interpreter/)).
- **Internal architecture**: The container launches with entrypoint `/home/sandbox/.openai-internal/user_machine/run-server.sh`, which runs a **FastAPI** application via `uvicorn` on port 8080.
- **API endpoints**: The sandbox exposes endpoints like `/check_liveness` (Kubernetes health checks), plus endpoints for code execution, file upload/download, and state management.
- **Environment**: Full Linux environment running as user `sandbox`. Has Python with common data science libraries (numpy, pandas, matplotlib, etc.) pre-installed.
- **Network isolation**: No internet access from within the sandbox. The container is isolated from other machines, with only API commands flowing in and results flowing out.
- **Known limitations**: Security researchers have demonstrated various escapes and information exfiltration techniques, though OpenAI has been patching them ([LessWrong analysis](https://www.lesswrong.com/posts/KSroBnxCHodGmPPJ8/jailbreaking-gpt-4-s-code-interpreter), [ChatGPT Linux secrets](https://incoherency.co.uk/blog/stories/chatgpt-linux.html)).
- **Infrastructure**: Runs on Kubernetes with gVisor as the container runtime. OpenAI stated in June 2024: "For some higher-risk tasks we use gVisor, a container runtime that provides additional isolation."

**Codex (Cloud Agent):**

Launched May 2025 as a cloud-based software engineering agent.

- **Sandbox per task**: Each task runs in its own cloud sandbox environment, preloaded with the user's repository ([openai.com/index/introducing-codex](https://openai.com/index/introducing-codex/)).
- **Agent loop**: The core logic orchestrates interaction between the user, the model, and the tools. Documented in detail in [openai.com/index/unrolling-the-codex-agent-loop](https://openai.com/index/unrolling-the-codex-agent-loop/).
- **Parallel execution**: Can work on many tasks simultaneously, each in isolated sandboxes.
- **Internet access**: Initially launched without internet access; added in June 2025 update.
- **Powered by codex-1**: A version of o3 optimized for software engineering, trained with RL on real-world coding tasks.
- **Security model**: The sandbox prevents the agent from accessing the user's systems or leaking secrets. Repository code is cloned into the sandbox but the sandbox cannot phone home.

### Anthropic (Claude Code / Artifacts)

**Claude Code Sandboxing:**

Anthropic open-sourced their sandboxing approach in October 2025.

- **`sandbox-runtime` (srt)** ([github.com/anthropic-experimental/sandbox-runtime](https://github.com/anthropic-experimental/sandbox-runtime)): A lightweight sandboxing tool that uses native OS primitives --- `sandbox-exec` on macOS, `bubblewrap` on Linux --- plus proxy-based network filtering. No container required.
- **Two boundaries**: Filesystem isolation and network isolation. The tool can sandbox agents, MCP servers, bash commands, and arbitrary processes.
- **Impact**: In Anthropic's internal usage, sandboxing safely reduced permission prompts by 84% ([anthropic.com/engineering/claude-code-sandboxing](https://www.anthropic.com/engineering/claude-code-sandboxing)).
- **Design philosophy**: Lightweight, no Docker dependency, runs at the OS level. This is deliberately NOT a container or VM approach --- it is process-level restriction using OS sandboxing primitives.

**Claude Artifacts:**

- Artifacts execute code in the browser using a sandboxed iframe. The rendering is client-side.
- According to [Pragmatic Engineer's deep dive](https://newsletter.pragmaticengineer.com/p/how-anthropic-built-artifacts), Artifacts were built in three months by a distributed team.
- Security researchers have found exploitation vectors in the artifact system, including cross-user attacks through the verified user system ([Sobele analysis](https://www.sobele.com/en/blogs/security-breach-analysis/bulk-exploitation-of-verified-users-in-the-claudeai-artifact-system)).

### Google Gemini Code Execution

- **Built-in Python sandbox**: Gemini models have access to a Python sandbox for generating and running code iteratively ([developers.googleblog.com](https://developers.googleblog.com/gemini-20-deep-dive-code-execution/)).
- **API-accessible**: Available as a "tool" in both Google AI Studio and the Gemini API, similar to function calling.
- **Libraries available**: NumPy, SciPy, pandas, matplotlib, and others are pre-installed in the sandbox environment.
- **Isolation**: Uses gVisor-based isolation. Security researchers extracted internal binaries and proto files from the sandbox without breaking out of it, revealing traces of Google's internal source code ([Vulnu report](https://www.vulnu.com/p/researchers-hack-source-code-from-google-gemini)).
- **Gemini CLI sandboxing**: The Gemini CLI supports sandboxing via Docker containers on Linux and macOS ([gemini-cli.xyz/docs/en/sandbox](https://gemini-cli.xyz/docs/en/sandbox)).
- **Attack surface research**: A January 2026 case study analyzed the real attack surface of code-executing LLMs using Gemini as the subject, noting that "an LLM that only talks can be wrong; an LLM that can execute code can be dangerous" ([Towards AI](https://pub.towardsai.net/the-real-attack-surface-of-code-executing-llms-a-gemini-code-execution-case-study-467767c324f4)).

---

## 3. Code Evaluation & Benchmarking

### SWE-bench

The dominant benchmark for evaluating LLMs on real-world software engineering tasks.

- **Docker-based evaluation harness**: Every evaluation runs in a containerized Docker environment to ensure consistent, reproducible results ([swebench.com](https://www.swebench.com/SWE-bench/)).
- **Per-repository Docker images**: Each of the 12 open-source Python repositories in SWE-bench gets its own Docker image with the correct dependencies, Python version, and test configuration.
- **Resource requirements**: Minimum 120GB disk space, 16GB+ RAM, 8+ CPUs recommended.
- **Evaluation flow**:
  1. Docker environment is set up for the repository
  2. The model's generated patch is applied
  3. The repository's test suite runs
  4. Results determine if the patch resolved the issue
- **Cloud-based evaluation via Modal**: As of January 2025, SWE-bench supports cloud-based evaluations through Modal, enabling parallel execution at scale ([swebench.com](https://www.swebench.com/SWE-bench/)).
- **Optimized Docker images**: Epoch AI released a public registry of optimized Docker images that reduced total size to 67 GiB for all 2,290 images (10x reduction) and enabled running SWE-bench Verified in 62 minutes on a single GitHub Actions VM ([epoch.ai/blog/swebench-docker](https://epoch.ai/blog/swebench-docker)).
- **LangSmith integration**: LangChain provides a workflow for running SWE-bench evaluations with observability through LangSmith ([docs.langchain.com/langsmith/swe-benchmark](https://docs.langchain.com/langsmith/swe-benchmark)).

### OpenHands (formerly OpenDevin) Evaluation

- Evaluated LLMs as coding agents on SWE-bench at 30x speed by parallelizing Docker-based evaluation across many containers ([openhands.dev/blog](https://openhands.dev/blog/evaluation-of-llms-as-coding-agents-on-swe-bench-at-30x-speed)).
- Each agent instance runs in its own Docker container with the repository pre-cloned and dependencies installed.

### HumanEval

- Simpler than SWE-bench: evaluates single-function code generation.
- Typically runs in standard Python environments with basic sandboxing.
- Lower infrastructure requirements since there are no full repository setups.

---

## 4. RL Training Loops

### The Core Challenge

Reinforcement learning for coding agents requires running generated code thousands or millions of times during training. Each rollout needs:
- Isolation (one bad rollout cannot crash the training run)
- Speed (GPU utilization drops if waiting for environment setup)
- Reproducibility (deterministic starting states)
- Scale (hundreds of parallel rollouts)

### LLM-in-Sandbox-RL Paradigm

A rapidly emerging research area as of January 2026, per [EmergentMind](https://www.emergentmind.com/topics/llm-in-sandbox-reinforcement-learning-llm-in-sandbox-rl):

- Embeds LLMs within controlled sandbox environments for autonomous decision-making through formal RL methods.
- Uses cold-start data generation, supervised fine-tuning, and on-policy RL to integrate language processing with tool manipulation.
- Shows enhanced sample efficiency across mathematical, automation, and simulation tasks.

### verl (Agentic RL Training)

An open-source framework for agentic RL training ([verl.readthedocs.io](https://verl.readthedocs.io/en/latest/start/agentic_rl.html)):

- **Server-based asynchronous rollout**: Agents interact with environments through tool calls. To avoid GPU idling while waiting for tool call returns, uses asyncio-based coroutines.
- **Architecture**: The inference engine (server) and the agent (client) are separated, enabling load balancing across multiple environment instances.
- **Multi-turn conversations**: Supports multi-turn tool-calling interactions within a single rollout.
- **LangGraph integration**: Uses LangGraph-based agents for complex environment interaction patterns.

### Fireworks AI Eval Protocol

[Fireworks.ai](https://fireworks.ai/blog/eval-protocol-rl-on-your-agents) released Eval Protocol, an open-source framework for RL on agents in any environment:

- Language-agnostic, framework-agnostic approach to RL fine-tuning.
- Focuses on tracing agent behavior to generate feedback signals.
- Designed for production RL where agents interact with real-world environments (APIs, databases, web browsers).

### NVIDIA NeMo Gym / NeMo RL

[NVIDIA's approach](https://developer.nvidia.com/blog/how-to-train-scientific-agents-with-reinforcement-learning/) for training scientific agents:

- **NeMo Gym**: Provides extensible, REST-API-based training environments with granular abstractions.
- **NeMo RL**: Handles the RL training loop with scalable infrastructure.
- Designed for scientific domains where agents need to automate multi-step research processes.

### Environment-as-a-Service

According to [Collinear AI's analysis](https://blog.collinear.ai/p/rl-env-as-a-service), the key architectural insight for production RL is treating environments as first-class infrastructure:

- **Data plane / control plane separation**: The environment (sandbox) is the data plane; orchestration is the control plane.
- **Why this matters**: RL training is fundamentally a distributed systems problem. The ML is the easy part; the infrastructure for managing thousands of parallel sandbox instances is the hard part.
- **Current gap**: Most teams are building bespoke environment infrastructure. There is no dominant "Environment-as-a-Service" provider yet, though E2B, Daytona, and Modal are all positioning for this.

### Training Safety Risks

A February 2026 paper from Tsinghua/NUS ([arxiv.org/html/2602.04196v1](https://arxiv.org/html/2602.04196v1)) identifies implicit safety risks during RL training:

- During code-based RL, models may covertly manipulate sandbox environments to inflate reward signals.
- Models can learn to exploit sandbox weaknesses during training, not just deployment.
- This makes sandbox security during training as important as during inference.

---

## 5. Enterprise Agent Deployments

### Devin Enterprise

The most mature enterprise deployment of an autonomous coding agent:

- **Three deployment tiers** ([docs.devin.ai](https://docs.devin.ai/enterprise/deployment/overview)):
  - Enterprise SaaS (multi-tenant)
  - Dedicated SaaS with private networking
  - Customer Hosted VPC (AWS or Azure)
- **Security**: SOC 2, SSO (Okta, Azure AD), RBAC, VPN support for private repos.
- **Case study**: Nubank deployed Devin to refactor their 8-year-old, multi-million-line ETL monolith. Achieved 8x efficiency improvement and 20x cost savings.

### Amazon Bedrock AgentCore

AWS published best practices for enterprise AI agents in February 2026 ([aws.amazon.com/blogs/machine-learning](https://aws.amazon.com/blogs/machine-learning/ai-agents-in-enterprises-best-practices-with-amazon-bedrock-agentcore/)):

- Provides an agentic platform with services for creating, deploying, and managing AI agents at scale.
- Nine best practices covering scoping, architecture, scaling.
- Emphasis on starting small and defining success criteria before scaling agent deployments.

### Enterprise Security Architecture Patterns

Based on analysis across multiple sources, the common enterprise architecture for coding agents looks like:

```
                    +-----------------+
                    |   Developer     |
                    |   (Slack/IDE)   |
                    +--------+--------+
                             |
                    +--------v--------+
                    |   Agent API     |
                    |   Gateway       |
                    +--------+--------+
                             |
              +--------------+--------------+
              |                             |
     +--------v--------+          +--------v--------+
     |   LLM Service   |          |  Sandbox Pool   |
     |   (Model API)   |          |  (Isolated VMs) |
     +--------+--------+          +--------+--------+
              |                             |
              +--------------+--------------+
                             |
                    +--------v--------+
                    |   Git Service   |
                    |   (GitHub/GL)   |
                    +--------+--------+
                             |
                    +--------v--------+
                    |   CI/CD         |
                    |   Pipeline      |
                    +-----------------+
```

Key security principles across enterprise deployments:
- **Zero trust**: All LLM-generated code is treated as potentially malicious.
- **Network segmentation**: Sandboxes have no access to production networks by default.
- **Secret management**: Credentials injected via secure vaults, never visible to the LLM.
- **Audit logging**: Every sandbox action is logged for compliance.
- **Human-in-the-loop**: Agent outputs go through PR review, not direct deployment.

### Docker's Position

Docker published guidance in February 2026 on sandboxing for enterprise AI agent adoption ([JP Caparas, Medium](https://jpcaparas.medium.com/docker-sandboxes-make-ai-agents-safe-for-enterprise-adoption-ad686c12af23)):

- Positions Docker containers as the default isolation layer for enterprise agents.
- Argues that microVM isolation "finally solves the 'do I trust this robot with sudo?' dilemma."
- Notes the industry convergence on container-based isolation as the minimum acceptable security boundary.

---

## 6. Open Source Agent Frameworks

### AutoGen (Microsoft)

The strongest built-in code execution support of any agent framework.

- **Default Docker execution**: As of AutoGen 0.2.8 (January 2024), code execution defaults to running inside a Docker container ([microsoft.github.io/autogen](https://microsoft.github.io/autogen/0.2/blog/2024/01/23/Code-execution-in-docker)).
- **`DockerCommandLineCodeExecutor`**: Creates a Docker container from a specified image (default: `python:3-slim`), executes code blocks inside it, and tears it down after execution.
- **Supports Python and shell scripts**: Language is specified per code block.
- **Configurable**: Custom Docker images, timeout settings, working directories, bind mounts.
- **Breaking change rationale**: Previously, code executed locally by default. Microsoft changed this because "it's easy particularly for new users to overlook code-execution risks."

### LangChain / LangGraph

Multiple sandboxing approaches:

- **LangChain Sandbox** ([pip install langchain-sandbox](https://www.youtube.com/watch?v=FBnER2sxt0w)): Uses **Pyodide (Python in WebAssembly)** for in-process isolation. No Docker or remote execution required. Supports configurable permissions and persistent state across executions via sessions.
- **Sandboxes for DeepAgents** ([blog.langchain.com](https://www.blog.langchain.com/execute-code-with-sandboxes-for-deepagents/)): Launched November 2025, integrates with three sandbox providers: **Runloop**, **Daytona**, and **Modal**. Allows safe execution of arbitrary code in remote sandboxes.
- **Covalent integration**: For scientific computing, LangChain integrates with Covalent Cloud for high-performance sandboxed execution on GPU clusters.
- **LangSmith + SWE-bench**: Provides tooling for running SWE-bench evaluations with full observability.

### CrewAI

- Supports code execution but requires users to set up their own security measures (Docker).
- Less integrated sandboxing compared to AutoGen.
- Focuses more on agent orchestration than execution infrastructure.

### smolagents (Hugging Face)

- Uses an **`additional_authorized_imports`** allowlist approach.
- By default, only imports explicitly listed are permitted.
- Simpler but more restrictive than container-based approaches.

### OpenHands (formerly OpenDevin)

- Each agent instance runs in its own Docker container.
- Designed as an open-source alternative to Devin.
- Achieved strong SWE-bench results by parallelizing evaluations across containers.

---

## 7. Dedicated Sandbox Infrastructure Providers

A new category of infrastructure companies has emerged specifically to provide sandboxing for AI agents.

### E2B

- **URL**: [e2b.dev](https://e2b.dev)
- **Funding**: $21M Series A
- **Technology**: Firecracker microVMs
- **Cold start**: <200ms
- **Key customers**: Perplexity (shipped advanced data analysis in 1 week), Manus (virtual computers for agents), Hugging Face (replicating DeepSeek-R1), Groq, Lindy
- **GitHub stars**: 10,791
- **API**: Python and JavaScript SDKs. Create a sandbox, run code, manage files, all via API.
- **Template system**: Custom sandbox templates with pre-installed dependencies, versioning, and caching.
- **Use cases**: Deep research agents, computer use agents, automation, background agents, RL training.
- **Session limit**: 24 hours maximum.

### Daytona

- **URL**: [daytona.io](https://www.daytona.io)
- **Funding**: $24M Series A (February 2026, led by FirstMark Capital)
- **Technology**: Stateful, composable sandboxes
- **Cold start**: Sub-90ms (fastest in the market)
- **GitHub stars**: 48,700
- **Key customers**: LangChain, Turing, Writer, SambaNova
- **Revenue**: Hit $1M forward ARR in under 3 months, doubled it 6 weeks later.
- **Differentiators**: Stateful sandboxes that persist across failures, Git-like branching (fork, snapshot, restore), composability.
- **Use cases**: Code execution, computer use by agents, RL at scale.
- **Investors include**: Datadog, Figma Ventures.

### Runloop

- **URL**: [runloop.ai](https://runloop.ai)
- **Founded by**: Jonathan Wall (former tech lead of Google File System, founding engineer at Google Wallet, founder of Inde acquired by Stripe)
- **Technology**: Custom bare-metal hypervisor with 2x faster vCPUs
- **Differentiators**: Only provider with both arm64 and x86 support. Agent, Object, and Secret stores for reusing tools/files/keys. Automatic build environment inference from Git repos.
- **Enterprise focus**: SOC 2, Blueprints, Snapshots for environment management.
- **LangChain integration**: Official sandbox provider for LangChain DeepAgents.

### Modal

- **URL**: [modal.com](https://modal.com)
- **Technology**: gVisor-based isolation
- **Strengths**: Massive autoscaling, Python-centric, GPU support, notebook integration.
- **SWE-bench**: Official cloud evaluation partner for SWE-bench.
- **Cold start**: Fast but variable depending on image size.
- **Limitation**: No BYOC (bring-your-own-cloud) option.

### Cloudflare Sandbox SDK

- **URL**: [developers.cloudflare.com/sandbox](https://developers.cloudflare.com/sandbox/)
- **Launched**: June 2025
- **Technology**: Container-based, built on Cloudflare's container infrastructure
- **Integration**: Native to Cloudflare Workers. Sandboxes are created and managed from Workers code.
- **API**: TypeScript SDK with `exec()`, `gitCheckout()`, `writeFile()`, `readFile()`, file watching, WebSocket connections.
- **Status**: Beta / Experimental
- **AI code executor tutorial**: Official tutorial for building an AI code executor using Sandbox SDK + Claude ([developers.cloudflare.com](https://developers.cloudflare.com/sandbox/tutorials/ai-code-executor/)).
- **Edge execution**: Runs at Cloudflare's edge, potentially the lowest-latency option for globally distributed use cases.

### Northflank

- **URL**: [northflank.com](https://northflank.com)
- **Technology**: Kata Containers + gVisor
- **Scale**: Processes 2M+ isolated workloads monthly.
- **Differentiators**: BYOC deployment, unlimited session duration, any OCI image.
- **Positioning**: "Best overall AI sandbox platform" (self-assessed in their January 2026 comparison).

### Others

- **Fly.io**: General-purpose VM platform, used by some agent frameworks.
- **CodeSandbox**: Primarily for web development, integrates with Cursor via SSH.
- **StackBlitz**: WebAssembly-based (WebContainers), runs Node.js in the browser.
- **Val Town**: Serverless JavaScript/TypeScript execution.
- **Vercel Sandbox**: AI SDK sandbox for Next.js apps.
- **Koyeb**: Positions as a sandbox platform for AI code execution with CI/CD integration.
- **Hopx.ai**: Blog/tutorial-focused platform for AI agent code execution.
- **Blaxel**: Focuses on sandbox lifecycle management for AI coding agents.

---

## 8. Manus (Meta) --- Noteworthy Case Study

Manus warrants its own section as the most complete "agent + sandbox" integration in production.

- **Acquired by Meta** in late 2025.
- **Sandbox architecture** ([manus.im/blog/manus-sandbox](https://manus.im/blog/manus-sandbox)):
  - Each task gets a **fully isolated cloud virtual machine** with networking, filesystem, browser, and development tools.
  - Zero Trust security model.
  - Persistent file storage across the session.
  - 24/7 autonomous operation capability.
  - AI can write and execute code, browse the web, manage files, and create complete websites.
- **Uses E2B**: Manus uses E2B sandboxes as its virtual computer infrastructure ([E2B case study](https://e2b.dev)).
- **Agent Skills integration**: Manus adopted Anthropic's Agent Skills open standard for modular, reusable capabilities ([manus.im/blog/manus-skills](https://manus.im/blog/manus-skills)).
- **Design philosophy**: The sandbox IS the agent's "hands." The name "Manus" comes from "Mens et Manus" (Mind and Hand) --- the model thinks, the sandbox acts.

---

## Key Takeaways

1. **The sandbox stack has converged on three tiers**: Process-level restriction (Anthropic `srt`), container/gVisor (OpenAI, Google, Docker), and microVM (E2B, Daytona, AWS). Most production deployments use the middle tier as the sweet spot between security and performance.

2. **Coding assistants are split on execution model**: Cursor and Windsurf execute locally (no sandbox), GitHub Copilot runs in cloud Actions runners (full sandbox), Replit has the most sophisticated snapshot-based approach, and Devin runs everything in cloud VMs.

3. **E2B and Daytona are the infrastructure winners so far**: E2B has the customer logos (Perplexity, Manus, Hugging Face, Groq). Daytona has the growth velocity ($24M Series A, 48.7k GitHub stars, $2M ARR in months). Runloop has the deepest technical pedigree.

4. **SWE-bench standardized on Docker**: The entire LLM coding benchmark ecosystem runs on Docker containers. This is both a strength (reproducibility) and a weakness (heavyweight, slow cold starts). Epoch AI's optimized images (10x size reduction) show there is significant room for infrastructure optimization.

5. **RL training is the next frontier for sandboxes**: The "Environment-as-a-Service" concept for RL training loops is an unsolved infrastructure problem. Teams are building bespoke solutions. Whoever builds the "AWS Lambda of RL environments" will capture a massive market.

6. **Security is an afterthought almost everywhere**: Researchers have found exploitable weaknesses in OpenAI's, Google's, and Anthropic's sandbox implementations. The industry is in a "ship fast, patch later" mode. Only Replit's hybrid approach (deterministic analysis + LLM reasoning) shows genuine security maturity.

7. **Open-source frameworks default to Docker**: AutoGen made Docker the default in January 2024. LangChain offers WebAssembly (Pyodide) as a lightweight alternative. The trend is toward mandatory isolation rather than optional.

---

## Predictions

1. **Sandbox infrastructure will become a $1B+ market by 2028.** E2B, Daytona, and Runloop are the early leaders, but AWS, GCP, and Azure will all launch first-party offerings. The cloud providers' advantage in VPC integration and compliance will be hard to beat at enterprise scale.

2. **Firecracker microVMs will win over gVisor for most use cases.** gVisor's syscall compatibility issues and performance overhead make it a poor fit for complex agent workloads. Firecracker's hardware-level isolation with sub-200ms cold starts is the better tradeoff.

3. **Cursor will eventually add remote sandbox execution.** Running LLM-generated code on the developer's local machine is a liability. As agents become more autonomous (8 parallel agents, multi-file edits), the risk of local execution becomes unacceptable. Expect Cursor to partner with or acquire a sandbox provider within 18 months.

4. **RL Environment-as-a-Service will be the next hot infrastructure category.** The separation of data plane (sandbox) and control plane (orchestration) mirrors the evolution of databases and compute. Daytona's stateful, branchable sandboxes are the closest to what RL training needs.

5. **WebAssembly sandboxes will grow for lightweight use cases.** LangChain's Pyodide-based sandbox and StackBlitz's WebContainers show that WASM can handle many agent code execution needs without any container overhead. Expect more frameworks to adopt this approach for simple code execution.

---

## Sources

All URLs are embedded inline throughout the document. Key references:

| Source | URL |
|---|---|
| Modal: What is an AI code sandbox? | https://modal.com/blog/what-is-ai-code-sandbox |
| Cursor Shadow Workspaces | https://cursor.com/blog/shadow-workspace |
| ByteByteGo: How Cursor Serves Billions | https://blog.bytebytego.com/p/how-cursor-serves-billions-of-ai |
| GitHub Copilot Agent Docs | https://docs.github.com/en/copilot/customizing-copilot/customizing-the-development-environment-for-copilot-coding-agent |
| Ryan Govostes: OpenAI Code Interpreter | https://ryan.govost.es/2025/openai-code-interpreter/ |
| OpenAI: Introducing Codex | https://openai.com/index/introducing-codex/ |
| OpenAI: Unrolling the Codex Agent Loop | https://openai.com/index/unrolling-the-codex-agent-loop/ |
| Anthropic: Claude Code Sandboxing | https://www.anthropic.com/engineering/claude-code-sandboxing |
| Anthropic sandbox-runtime GitHub | https://github.com/anthropic-experimental/sandbox-runtime |
| Google: Gemini 2.0 Code Execution | https://developers.googleblog.com/gemini-20-deep-dive-code-execution/ |
| Vulnu: Researchers Hack Gemini Sandbox | https://www.vulnu.com/p/researchers-hack-source-code-from-google-gemini |
| SWE-bench Official | https://www.swebench.com/SWE-bench/ |
| Epoch AI: SWE-bench Docker | https://epoch.ai/blog/swebench-docker |
| Replit Snapshot Engine | https://blog.replit.com/inside-replits-snapshot-engine |
| Replit: Securing AI-Generated Code | https://blog.replit.com/securing-ai-generated-code |
| Devin Enterprise Deployment | https://docs.devin.ai/enterprise/deployment/overview |
| E2B | https://e2b.dev |
| Daytona | https://www.daytona.io |
| Runloop | https://runloop.ai |
| Cloudflare Sandbox SDK | https://developers.cloudflare.com/sandbox/ |
| Northflank Sandbox Comparison | https://northflank.com/blog/best-code-execution-sandbox-for-ai-agents |
| Modal: Top AI Code Sandbox Products | https://modal.com/blog/top-code-agent-sandbox-products |
| LangChain: Sandboxes for DeepAgents | https://www.blog.langchain.com/execute-code-with-sandboxes-for-deepagents/ |
| AutoGen Docker Execution | https://microsoft.github.io/autogen/0.2/blog/2024/01/23/Code-execution-in-docker |
| Manus Sandbox | https://manus.im/blog/manus-sandbox |
| verl Agentic RL Training | https://verl.readthedocs.io/en/latest/start/agentic_rl.html |
| Collinear AI: RL Env-as-a-Service | https://blog.collinear.ai/p/rl-env-as-a-service |
| Fireworks AI: Eval Protocol | https://fireworks.ai/blog/eval-protocol-rl-on-your-agents |
| AWS Bedrock AgentCore | https://aws.amazon.com/blogs/machine-learning/ai-agents-in-enterprises-best-practices-with-amazon-bedrock-agentcore/ |
| awesome-sandbox (curated list) | https://github.com/restyler/awesome-sandbox |
| BetterStack: 10 Best Sandbox Runners 2026 | https://betterstack.com/community/comparisons/best-sandbox-runners/ |
| Koyeb: Top Sandbox Platforms 2026 | https://www.koyeb.com/blog/top-sandbox-code-execution-platforms-for-ai-code-execution-2026 |
| EmergentMind: LLM-in-Sandbox-RL | https://www.emergentmind.com/topics/llm-in-sandbox-reinforcement-learning-llm-in-sandbox-rl |
| ITNEXT: OpenAI Code Execution & gVisor | https://itnext.io/openais-code-execution-runtime-replicating-sandboxing-infrastructure-a2574e22dc3c |
