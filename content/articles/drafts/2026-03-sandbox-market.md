---
title: The $1B Sandbox Market Nobody Talks About
status: draft
platform: x-article
thumbnail: pending
perspective: "A billion-dollar infrastructure category is forming around 'where does AI-generated code safely run,' and most engineers building AI agents have never heard of the companies building it."
sources:
  - research/reports/20260219-code-execution-sandboxes.md
content-id: 20260308-AD-006
---

# The $1B Sandbox Market Nobody Talks About

Cursor produces nearly a billion lines of accepted code per day. GitHub Copilot runs agents in ephemeral cloud VMs. Claude Code sandboxes untrusted executions with OS-level primitives. Every one of these systems has to answer the same question before a single line runs: *where does this code execute safely?*

That question has spawned an infrastructure category that barely existed two years ago. E2B just raised $21M. Daytona raised $24M and hit $1M ARR in under three months. Runloop was founded by the former tech lead of Google File System. All three major clouds shipped purpose-built sandbox offerings in the last twelve months. And yet most engineers building with AI agents have never heard of any of them.

## The problem is real and obvious once you see it

An AI agent asks to run a program. Sometimes it's `pytest`. Sometimes it's `pip install sketchy-package && python run.py`. The moment you let an agent execute code, you're running untrusted bytes on infrastructure you care about.

The failure modes go beyond "the agent escapes the sandbox." Secret exfiltration, where the agent reads `~/.ssh` or `~/.aws` and phones home with credentials. Resource exhaustion from fork bombs or crypto mining. Lateral movement from a sandbox into your production database over the network. Kernel exploits that turn a container escape into host root access.

Here's the part that should make you uncomfortable: Cursor and Windsurf run agent-generated code directly on the developer's machine. No sandbox. No isolation boundary. Every file, every credential, every SSH key on your laptop is accessible to whatever code the model generates. As agents become more autonomous, this gets worse, not better.

## The market map

Three startups and three cloud providers are racing to own this category.

**E2B** is the incumbent. Firecracker microVMs, ~150ms cold starts, Apache 2.0 open source. Their customer list reads like an AI who's-who: Perplexity shipped advanced data analysis in one week using E2B sandboxes. Manus (acquired by Meta) built its entire virtual computer infrastructure on E2B. Hugging Face uses them for RL training pipelines.

**Daytona** is the growth story. $24M Series A led by FirstMark Capital with Datadog and Figma Ventures participating. Sub-90ms cold starts. Their differentiator is stateful sandboxes with Git-like branching. You can fork a running sandbox, try something risky, and revert if it breaks. LangChain, Turing, Writer, and SambaNova are customers. They doubled their ARR from $1M to $2M in six weeks.

**Modal** is the Python-first infrastructure play. Not purely a sandbox company. They also do inference, training, and batch jobs. But their sandbox product supports massive autoscaling (10K+ concurrent units), GPU access, and a code-first image definition system that eliminates Dockerfiles entirely. Lovable and Quora run millions of daily code executions on Modal. They're the official cloud evaluation partner for SWE-bench.

**Runloop** is the deep-tech bet. Founded by Jonathan Wall, former tech lead of Google File System, founding engineer at Google Wallet, founder of Inde (acquired by Stripe). Custom bare-metal hypervisor with 2x faster vCPUs. The only provider offering both arm64 and x86 support. They're the official LangChain sandbox provider.

On the cloud side, all three majors shipped within months of each other:

- **AWS Bedrock AgentCore**: Firecracker microVMs per agent session, 300-800ms cold starts, tied to the Bedrock ecosystem.
- **GKE Agent Sandbox**: gVisor plus optional Kata Containers, pre-warmed pools that cut cold starts 90%, open-sourced through CNCF.
- **Azure Dynamic Sessions**: Hyper-V Type-1 hypervisor, the strongest isolation of the bunch. The proof point: Microsoft Copilot uses this for code execution serving 1B+ users.

## Why not just use Docker?

Because containers share the host kernel. Every syscall from inside a container goes directly to the host kernel. A kernel bug reachable via any allowed syscall path is a container escape.

This isn't theoretical. Dirty COW, Dirty Pipe, runc overwrite. All were container escapes from properly configured containers. 94% of organizations have reported serious container security incidents. 60% were vulnerable to the "Leaky Vessels" container escape CVEs.

For code you wrote and trust, containers are fine. For code an LLM generated five seconds ago, containers are a conscious bet that the Linux kernel has no exploitable bugs in any reachable syscall path. That's a bet you will eventually lose.

The sandbox market exists because the industry figured this out. The three practical isolation tiers look like this:

1. **Process-level restriction** (lightest). Anthropic's approach for Claude Code. No container, no VM. OS-level primitives (`sandbox-exec` on macOS, `bubblewrap` on Linux) plus proxy-based network filtering. Reduced permission prompts by 84%. Open-sourced as `srt`.

2. **gVisor / application kernel** (middle ground). A userspace kernel intercepts syscalls before they reach the host. The application sees Linux, but only 68 host syscalls are actually exposed instead of hundreds. OpenAI uses this for ChatGPT Code Interpreter. Google uses it for Gemini. Modal uses it. No KVM required.

3. **MicroVM / Firecracker** (strongest practical isolation). A dedicated guest kernel behind hardware virtualization. Less than 5MB overhead per VM. 125ms boot time. 150 VMs per second per host. This is what AWS Lambda runs on (trillions of invocations monthly), what E2B uses, what Fly.io uses. Hardware-level isolation.

## The numbers that matter

A 5-minute sandbox session with 1 vCPU and 512MB of RAM costs about $0.005 on E2B or Daytona. At a million sessions per day, that's roughly $135,000 per month.

DIY Firecracker on bare metal drops the per-session cost to $0.001-0.003, but budget 6-12 months of engineering time to build the networking, scheduling, monitoring, snapshot management, and security infrastructure around the VM. The break-even is somewhere around 200K-500K sessions per day. Below that, use a managed platform.

The hidden cost that kills budgets is warm pools. Keeping 1,000 idle VMs ready on a managed platform runs about $36,000 per month. The same capacity on self-managed EC2 costs about $1,600. Managed warm pools cost roughly 20x more than DIY because you're paying per-second rates for idle compute.

Billing granularity matters enormously for short-lived workloads. A 30-second task billed per-second costs $0.00042. The same task billed per-hour costs $0.05. At a million sessions per day, that's $420 versus $50,000. Per-second billing saves 99% for short-lived sandbox sessions.

## What I think happens next

The startup players have a window, but it's closing. AWS, GCP, and Azure all shipped sandbox products in the last year. They'll win at enterprise scale through VPC integration, IAM, and compliance. The startups win on developer experience, speed of iteration, and not being locked to a single cloud.

Cursor will add remote sandbox execution within 18 months. Running LLM-generated code on developer machines is a liability that scales with agent autonomy. They'll partner with or acquire a sandbox provider.

The RL training use case is about to make this market much bigger. Training a coding agent requires running generated code thousands or millions of times per training run. Every rollout needs isolation, speed, and reproducibility. Collinear AI calls this "Environment-as-a-Service" and argues it's a fundamentally unsolved infrastructure problem. Daytona's stateful, branchable sandboxes are closest to what RL training actually needs.

And at some point, probably before the end of 2026, a major security incident involving an unsandboxed coding agent will hit the mainstream press. Autonomous agents plus local execution plus package installation plus network access is too large a surface area. Something will go badly wrong, and it will accelerate adoption industry-wide.

The boring infrastructure always wins. Databases, container orchestration, CI/CD. They all followed the same arc: open-source projects, then startups, then cloud providers, then consolidation. Sandboxes for AI code execution are somewhere between stage one and stage two. Most engineers haven't thought about this category yet. They will.
