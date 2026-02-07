# Cloud-Native Sandbox & Isolated Execution Primitives: Raw Research Findings

**Date:** 2-7-26
**Category:** Research Report
**Status:** [x] Active

---

## Table of Contents
1. [AWS Approaches](#aws-approaches)
2. [GCP Approaches](#gcp-approaches)
3. [Azure Approaches](#azure-approaches)
4. [DIY on Cloud](#diy-on-cloud)
5. [Company-Specific Architectures](#company-specific-architectures)
6. [Comparison Matrix](#comparison-matrix)
7. [Key Data Points](#key-data-points)

---

## AWS Approaches

### AWS Lambda (Firecracker-based)

**Isolation model:**
- Each Lambda invocation runs in a Firecracker microVM
- Firecracker is an open-source VMM (Virtual Machine Monitor) written in Rust
- Uses Linux KVM for hardware-level isolation
- Minimalist device model -- excludes unnecessary devices and guest functionality
- Memory overhead: **< 5 MiB per microVM**
- Raw Firecracker boot time: **~125ms** to boot a microVM
- Can create **up to 150 microVMs per second** on a single host

**Cold start benchmarks (real-world Lambda, not raw Firecracker):**
- Simple functions (Python/Node.js, minimal deps): **100-200ms**
- Real-world with dependencies: **1-5 seconds**
- Java/Spring Boot without SnapStart: **3-10+ seconds**
- Java with SnapStart: **sub-second** (as low as 200-300ms)
- VPC-attached functions add additional latency (historically seconds, now ~1s with Hyperplane ENI)
- Source: Multiple benchmarks. maxday's daily benchmark at https://maxday.github.io/lambda-perf/ tracks 10 cold starts per runtime daily.

**SnapStart (cold start mitigation):**
- Available for Java, Python, and .NET runtimes
- Takes a Firecracker microVM snapshot of memory + disk state after initialization
- Encrypts and caches the snapshot
- Restores from snapshot on cold start instead of re-initializing
- Can reduce cold starts from "several seconds to sub-second"
- Source: https://docs.aws.amazon.com/lambda/latest/dg/snapstart.html

**Pricing:**
- $0.20 per 1M requests
- $0.0000166667 per GB-second (x86)
- ARM/Graviton2: ~20% cheaper than x86
- Free tier: 1M requests + 400,000 GB-seconds/month (always free, not just 12 months)
- Provisioned Concurrency: pay for keeping functions warm (~$0.0000041667/GB-second for provisioned + execution costs)
- Source: https://cloudchipr.com/blog/aws-lambda-pricing

**For sandbox use case:**
- Lambda has a **15-minute max execution time** -- hard limit
- Max memory: 10,240 MB
- Max deployment package: 250 MB (unzipped), 50 MB (zipped)
- No persistent filesystem (only /tmp, 10 GB max, ephemeral)
- No inbound TCP connections (HTTP only via API Gateway/Function URLs)
- These constraints make Lambda unsuitable for long-running agent sandboxes but fine for short code execution tasks

### AWS ECS/Fargate (also Firecracker-based)

**Isolation model:**
- Fargate tasks run in Firecracker microVMs (since late 2018)
- Each task gets its own dedicated microVM
- Hardware-level isolation between tasks/customers

**Cold start times:**
- Fargate cold starts are significantly slower than Lambda
- Typical: **15-40+ seconds** for a new task from scratch
- One source reports: "38 seconds to process the first batch" for a fintech fraud engine
- With pre-warmed capacity / minimum tasks configured: can be reduced
- Image caching (Seekable OCI / SOCI) can help -- streams container layers instead of downloading fully
- Source: https://aws.plainenglish.io/taming-cold-starts-on-aws-fargate-the-architecture-behind-sub-5-second-task-launches-622ebd73b051

**Pricing:**
- Per-second billing (1-minute minimum)
- Linux/x86: $0.04048/vCPU/hour + $0.004445/GB memory/hour
- Linux/ARM: ~20% cheaper
- Fargate Spot: up to 70% discount (but can be interrupted)
- No free tier
- Source: https://aws.amazon.com/fargate/pricing/

**For sandbox use case:**
- No execution time limits (runs until stopped)
- Full container environment -- install anything
- Can expose ports, run servers
- More flexible than Lambda but much slower cold starts
- Operational complexity: moderate (ECS task definitions, VPCs, security groups, IAM roles)

### AWS CodeBuild Sandbox

**What it is:**
- CodeBuild added a "sandbox" debugging feature (April 2025)
- SSH into a running CodeBuild environment for interactive debugging
- Persistent filesystem during debug session
- Same isolation as regular CodeBuild builds

**Pricing:**
- Per-minute billing (rounded up)
- BUILD_GENERAL1_SMALL: ~$0.005/min
- BUILD_GENERAL1_MEDIUM: ~$0.01/min
- BUILD_GENERAL1_LARGE: ~$0.02/min
- Free tier: 100 build minutes/month (indefinite, not 12-month)
- Source: https://cloudburn.io/tools/aws-codebuild-pricing-calculator

**For sandbox use case:**
- Not designed for this -- it's a CI/CD debugging tool
- Cold starts are slow (building containers from scratch)
- Useful reference point but not a viable sandbox primitive

### AWS Bedrock AgentCore Runtime (NEW - 2025)

**What it is:**
- Part of Amazon Bedrock AgentCore suite (launched mid-2025)
- Fully managed runtime for deploying AI agents
- Uses Firecracker microVMs for session-level isolation
- Each agent invocation gets a dedicated, ephemeral microVM

**Cold start:**
- **300-800ms** typically
- Teardown is deterministic -- microVM wiped at session end
- State preserved up to 15 minutes if agent awaits user input
- Source: https://blog.radixia.ai/serverless-ai-agents-with-amazon-bedrock-agentcore/

**Isolation:**
- Each session is a separate Firecracker microVM
- No cross-tenant leakage
- Deterministic teardown

**Code Interpreter tool:**
- Pre-built runtimes for multiple languages
- File upload: up to 100 MB inline, up to 5 GB via S3
- Network access configurable
- CloudTrail logging
- Source: https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/code-interpreter-tool.html

**Deployment options:**
- Container-based (Dockerfile + ECR)
- Direct code deployment (Python zip, no Docker required) -- launched Nov 2025
- Source: https://aws.amazon.com/blogs/machine-learning/iterate-faster-with-amazon-bedrock-agentcore-runtime-direct-code-deployment/

**For sandbox use case:**
- Purpose-built for agent code execution
- Tied to AWS Bedrock ecosystem
- Not a general-purpose sandbox primitive -- specifically for Bedrock agents

---

## GCP Approaches

### Cloud Run (gVisor-based)

**Isolation model:**
- Two-layer sandbox:
  1. **Hardware-backed layer**: x86 virtualization equivalent to individual VMs
  2. **Software kernel layer**: gVisor (user-space kernel that intercepts syscalls)
- Google explicitly markets this for AI agent code execution
- "When you deploy your code, Cloud Run confines the code within the sandboxing environment. This isolation lets you run untrusted code, such as code generated by a large language model (LLM), with greater security."
- Source: https://docs.cloud.google.com/run/docs/code-execution

**Code execution modes:**
- Synchronous: direct code execution in the running container
- Asynchronous: Cloud Run jobs for longer/background tasks
- Google provides explicit guidance: restrict IAM permissions, use VPC firewall rules to prevent internet access for untrusted code

**Cold start:**
- Typical: **0.5-2 seconds** for a new instance
- Minimum instances setting eliminates cold starts (but costs money)
- Startup CPU boost available

**Pricing:**
- Per-request billing: charges only while processing requests
- vCPU: $0.00002400/vCPU-second
- Memory: $0.00000250/GiB-second
- Per request: $0.40/million
- Free tier: 2 million requests/month, 360,000 vCPU-seconds, 180,000 GiB-seconds
- Source: https://cloudchipr.com/blog/cloud-run-pricing

**For sandbox use case:**
- Very good fit for code execution sandboxes
- Google is explicitly positioning it for this
- Two-layer isolation is strong but not as strong as dedicated microVMs
- More flexible than Lambda (arbitrary containers, longer timeouts up to 60 min for services, 24h for jobs)

### GKE Sandbox / Agent Sandbox (gVisor-based) -- NEW November 2025

**What it is:**
- Announced at KubeCon NA 2025 (November 2025)
- New Kubernetes primitive specifically for AI agent workloads
- Kernel-level separation built on **gVisor** (with support for Kata Containers)
- Being built as a CNCF open-source project -- not GKE-locked
- Source: https://cloud.google.com/blog/products/containers-kubernetes/agentic-ai-on-kubernetes-and-gke

**Key features:**
- **Pre-warmed pools**: deliver **sub-second startup latency**, "up to 90% improvement over cold starts"
- **Network access controls**: limits what sandboxes can reach
- **Massive parallelism**: schedules thousands of sandboxes in parallel
- **Pod Snapshots**: GKE-exclusive feature that checkpoints/restores running pods (CPU and GPU), "cutting pod start times from minutes to seconds"
- Source: https://techinformed.com/google-launches-agent-sandbox-for-secure-ai-agents-on-kubernetes/

**Isolation model:**
- gVisor intercepts syscalls in user space -- guest kernel never directly touches host kernel
- Compatible with existing container tooling
- Optional Kata Containers support for hardware-level VM isolation
- Each sandbox gets its own gVisor kernel instance

**For sandbox use case:**
- Purpose-built for this exact use case
- Requires running GKE (Kubernetes operational complexity)
- Most modern/opinionated GCP approach to agent sandboxing
- Pre-warmed pools are the killer feature for latency
- Still in early days (limited preview for Pod Snapshots)

### GKE Sandbox (Original -- pre-Agent Sandbox)

**What it is:**
- gVisor-based sandbox available on GKE since ~2019
- Adds gVisor isolation to individual pods
- Enabled per-node-pool

**Performance overhead:**
- gVisor adds overhead on system calls (additional software layers)
- Memory overhead: additional memory for the Sentry process
- File system operations: slower than native (multiple context switches)
- Network: some overhead but generally acceptable
- CPU-bound workloads: minimal overhead
- Source: https://gvisor.dev/docs/architecture_guide/performance

### Cloud Functions

- Similar to AWS Lambda conceptually
- Runs on same infrastructure as Cloud Run
- Second-gen Cloud Functions are actually built on Cloud Run
- Same two-layer sandbox model
- Max execution time: 60 minutes (2nd gen) vs 9 minutes (1st gen)
- Not a separate evaluation -- effectively Cloud Run under the hood

### Compute Engine with Nested Virtualization

- GCP supports nested virtualization on Haswell+ CPUs
- Can run Firecracker/KVM inside a GCE VM
- Useful for DIY sandbox setups
- No bare-metal instances like AWS -- nested virt is the path
- Performance: nested virt adds overhead vs bare metal KVM

---

## Azure Approaches

### Azure Container Apps Dynamic Sessions (PRIMARY SANDBOX OFFERING)

**What it is:**
- Purpose-built sandbox feature for running untrusted code
- Each session runs in its own **Hyper-V isolation boundary**
- GA for Python code interpreter and custom containers (November 2024)
- JavaScript code interpreter in public preview
- **Microsoft Copilot uses this** for its Advanced Data Analytics feature (1B+ users)
- Source: https://techcommunity.microsoft.com/blog/appsonazureblog/azure-container-apps-dynamic-sessions-general-availability-and-more/4303561

**Key features:**
- Session pools mitigate cold starts (pre-warmed sessions)
- Strong isolation via Hyper-V
- Built-in code interpreter sessions (Python, JavaScript)
- Custom container sessions for arbitrary workloads
- LangChain and Semantic Kernel integrations built-in
- Source: https://learn.microsoft.com/en-us/azure/container-apps/sessions

**Isolation:**
- Hyper-V is a Type-1 (bare-metal) hypervisor
- Each session gets its own Hyper-V VM
- Stronger isolation than containers or gVisor -- full hardware virtualization
- Industry-standard isolation (same tech running Azure's multi-tenant cloud)

**For sandbox use case:**
- This IS the Azure sandbox offering
- Session pool model handles cold starts well
- Direct integration with AI frameworks (LangChain, Semantic Kernel)
- Microsoft Copilot is the proof point at scale (1B+ users)

### Azure Container Instances (ACI)

**Confidential Containers:**
- Hardware-backed Trusted Execution Environment (TEE)
- Uses AMD SEV-SNP or Intel TDX
- Encrypts container memory in hardware
- Attestation support -- prove code is running in TEE
- Stronger than any other option here -- provably secure execution

**For sandbox use case:**
- Overkill for most agent sandboxing
- Designed for data privacy compliance (HIPAA, GDPR edge cases)
- Slower startup, more expensive
- Not positioned for high-throughput agent sandboxing

### Azure Functions

- Similar to AWS Lambda
- Consumption plan: auto-scale, pay per execution
- Cold starts: similar range to Lambda (100ms-seconds depending on runtime)
- Max execution time: 5 min (Consumption), 10 min (Premium), unlimited (Dedicated)
- Not the primary Azure sandbox primitive

### Azure Confidential Computing VMs

- DCsv2, DCsv3 series (Intel SGX)
- DCasv5, DCadsv5 series (AMD SEV-SNP)
- Full VM-level confidential computing
- For when you need provable isolation (regulated industries)
- Not relevant for general agent sandboxing -- too heavy, too expensive

---

## DIY on Cloud

### Firecracker on Bare Metal EC2

**Setup requirements:**
- Need bare-metal EC2 instance (i3.metal, m5.metal, c5.metal, etc.)
- i3.metal: ~$4.99/hour on-demand (72 vCPUs, 512 GB RAM, NVMe storage)
- Or nested virtualization on a cloud VM (AWS recently started supporting this on some instance types)
- KVM must be available (/dev/kvm)
- Source: https://blog.alexellis.io/how-to-run-firecracker-without-kvm-on-regular-cloud-vms/

**What you need to build:**
1. **Kernel + rootfs management**: Build/maintain Linux kernel images and root filesystems for microVMs
2. **Networking**: Set up TAP devices, iptables/nftables rules, DHCP for each microVM
3. **Storage**: Manage block devices or overlay filesystems per microVM
4. **API layer**: Build REST/gRPC API to create/destroy/manage microVMs
5. **Scheduling**: Decide which host gets which microVM (bin packing)
6. **Monitoring**: Metrics, logging, health checks for potentially thousands of microVMs
7. **Snapshotting**: If you want fast restores, build snapshot/restore pipeline
8. **Security**: Seccomp filters, cgroup limits, jailer process configuration
9. **Image registry**: Manage and distribute rootfs images

**Operational burden:**
- Alex Ellis (actuated.dev) describes the friction: "the cost is typically over $5/hour and the minimum commitment is one bare-metal machine"
- Need to handle multi-host orchestration yourself
- Need to build your own control plane
- Firecracker itself is simple -- the infrastructure around it is the hard part
- "Firecracker is straightforward to use... the documentation and examples are pretty clear" -- Julia Evans

**Performance on bare metal:**
- Boot time: **~125ms** for the microVM itself
- With kernel + rootfs load + network setup: **~200-500ms** end-to-end
- Can run 150+ microVMs per second creation rate on a single host
- Memory overhead: < 5 MiB per microVM

**Alternative: Firecracker without KVM (actuated/SlicerVM approach):**
- Alex Ellis built a way to run Firecracker on regular cloud VMs without /dev/kvm
- Uses software emulation -- slower but works anywhere
- Removes the bare-metal requirement
- Source: https://blog.alexellis.io/how-to-run-firecracker-without-kvm-on-regular-cloud-vms/

**SlicerVM numbers:**
- "Boot the Linux Kernel and systemd in less than 300ms" with optimized images
- Comparison: EC2 instances take 15-20s to provision, EKS nodes 1-2 minutes
- Source: https://slicervm.com/blog/microvms-sandboxes-in-300ms/

### gVisor on GKE/Kubernetes

**Setup:**
- Enable gVisor runtime class on your Kubernetes cluster
- Add `runtimeClassName: gvisor` to pod spec
- Works on GKE natively (just enable GKE Sandbox on node pool)
- Works on self-managed K8s with gVisor installed as containerd runtime

**Operational burden:**
- Much lower than Firecracker DIY
- gVisor is a drop-in runtime -- no kernel/rootfs management
- But: you still need Kubernetes (which is its own operational burden)
- GKE Autopilot makes this nearly zero-ops

**Performance tradeoffs vs Firecracker:**
- gVisor: faster startup (no VM boot), less memory overhead
- gVisor: slower syscall-heavy workloads (user-space kernel adds overhead)
- Firecracker: slower startup, but stronger isolation (hardware VM boundary)
- Firecracker: near-native performance once booted

### Kata Containers on Kubernetes

- Runs each container in a lightweight VM (uses QEMU or Firecracker as VMM)
- Kubernetes-compatible (runtimeClassName)
- Stronger isolation than gVisor (full VM boundary)
- Slower startup than gVisor, faster than full VMs
- Used by: Azure (for confidential containers), various Kubernetes deployments

---

## Company-Specific Architectures

### Vercel Sandbox

**Architecture:**
- **Firecracker microVMs** -- "same infrastructure that powers 1M+ builds a day at Vercel"
- Each sandbox is an isolated Linux environment
- Base image: Amazon Linux 2023
- Full root access
- Configurable timeout
- Source: https://vercel.com/docs/vercel-sandbox/concepts

**Performance:**
- Not explicitly published cold start numbers
- Claim: starts from "clean state (or snapshot) every time"
- Snapshot support for faster restarts

**Status:** GA as of January 30, 2026
**Pricing:** Not publicly detailed in research (likely usage-based)
**SDK:** Open-source CLI and SDK (`@vercel/sandbox`)
**Source:** https://vercel.com/blog/vercel-sandbox-is-now-generally-available

### Replit

**Architecture:**
- Linux containers (historically), now heavily Nix-based
- Each Repl is a "Linux container with a filesystem"
- Infrastructure called "Goval" -- manages VMs, databases, cloud storage, reverse proxies
- Running tens of thousands of Repls concurrently
- Nix for reproducible environments (30,000+ OS packages available)
- Source: https://blog.replit.com/regional-goval

**Snapshot Engine (December 2025):**
- "Instant filesystem forks, versioned databases, and isolated sandboxes"
- Enables reversible AI development
- Agent gets an isolated environment; changes can be rolled back
- Initially built for professional developers/teams, then repurposed for Replit Agent
- Source: https://blog.replit.com/inside-replits-snapshot-engine

**Key insight from Replit:**
> "Giving an AI Agent direct access to your code and database can be risky: it might make a change you don't like, or drop or alter your data."
Their solution: snapshot-before-execute, with the ability to revert.

### Cursor

**Architecture:**
- No detailed public architecture docs found for sandbox infrastructure
- Background Agent feature runs in remote environments
- Likely uses cloud-hosted VMs or containers (not publicly documented)
- Previously referenced as using remote execution for background tasks

### Together AI Code Sandbox

**Architecture:**
- Uses **CodeSandbox's microVM infrastructure** under the hood
- Not their own infra -- built on CodeSandbox's platform
- Source: https://docs.together.ai/docs/together-code-sandbox

**Performance:**
- VM from snapshot: **500ms** (P95)
- VM from scratch: **under 2.7 seconds** (P95)
- Memory snapshotting for hibernate/resume
- Hot-swappable VM sizes: 2-64 vCPUs, 1-128 GB RAM

**Pricing:**
- Credit-based pricing by VM size
- Concurrent VM limits
- Enterprise pricing available
- Source: https://docs.together.ai/docs/together-code-sandbox

### Fly.io

**Architecture:**
- Firecracker microVMs (Machines API)
- "Sub-second starts and stops with full VM control"
- Global private networking between machines
- OCI container support (if Docker runs it, Fly runs it)
- Source: https://fly.io/machines

**AI-specific pitch:**
- "Confidently deploy sketchy LLM-generated code"
- Kernel isolation via Firecracker VMs
- Isolated code per run
- Restricted network access
- Clean slate for every run
- Source: https://fly.io/ai

**Pricing:**
- Per-second billing
- Machines that are stopped don't incur compute charges
- Shared-1x 1GB: ~$6.79/month if running 24/7
- Pay only for actual uptime

### Modal

**Architecture:**
- Serverless container fabric (not microVMs)
- Sub-second cold starts
- Autoscale from 0 to 10,000+ concurrent units
- Source: https://modal.com/blog/top-code-agent-sandbox-products

**Users at scale:**
- Lovable and Quora run "millions of untrusted code snippets a day"
- Built-in tunneling for direct external connections
- Granular egress controls

### Northflank

**Architecture:**
- Supports multiple isolation backends: Firecracker, gVisor, Kata Containers
- "Spin up microVM-backed containers in seconds"
- Source: https://northflank.com/blog/how-to-spin-up-a-secure-code-sandbox-and-microvm-in-seconds-with-northflank-firecracker-gvisor-kata-clh

---

## Comparison Matrix

### Cold Start Times

| Service | Cold Start | Notes |
|---------|-----------|-------|
| **Firecracker (raw)** | ~125ms | Just the microVM boot, no app |
| **AWS Lambda (simple)** | 100-200ms | Python/Node, minimal deps |
| **AWS Lambda (real-world)** | 1-5s | With dependencies, VPC |
| **AWS Lambda + SnapStart** | <1s | Java/Python/.NET |
| **Bedrock AgentCore** | 300-800ms | Per session |
| **AWS Fargate** | 15-40s | New task from scratch |
| **Cloud Run** | 0.5-2s | New instance |
| **GKE Agent Sandbox** | Sub-second | With pre-warmed pools |
| **Azure Dynamic Sessions** | Near-instant | With session pool |
| **Together Code Sandbox** | 500ms from snapshot, 2.7s clean | P95 |
| **Fly.io Machines** | Sub-second | Firecracker-based |
| **Modal** | Sub-second | Container-based |
| **SlicerVM** | <300ms | Optimized Firecracker images |

### Pricing Models

| Service | Model | Example Cost |
|---------|-------|-------------|
| **Lambda** | Per-request + per-GB-second | $0.20/1M requests + $0.0000167/GB-s |
| **Fargate** | Per-second (vCPU + memory) | ~$0.04/vCPU-hour + $0.004/GB-hour |
| **Cloud Run** | Per-request + per-vCPU-second | $0.000024/vCPU-s + $0.40/1M requests |
| **Azure Dynamic Sessions** | Part of Container Apps pricing | Usage-based |
| **Fly.io** | Per-second | ~$6.79/month for shared-1x-1GB 24/7 |
| **CodeBuild** | Per-minute | $0.005-0.02/min by instance size |
| **Together** | Credit-based by VM size | VM size tiers |

### Isolation Guarantees

| Technology | Isolation Level | Boundary |
|-----------|----------------|----------|
| **Firecracker** | Hardware VM (KVM) | Strongest -- dedicated kernel per workload |
| **Hyper-V** | Hardware VM (Type-1) | Strongest -- bare-metal hypervisor |
| **gVisor** | User-space kernel | Strong -- syscall interception, no direct kernel access |
| **Kata Containers** | Hardware VM (QEMU/FC) | Strongest -- full VM per container |
| **Standard containers** | Linux namespaces/cgroups | Weakest -- shared kernel |
| **Confidential (SEV-SNP/SGX)** | Hardware TEE + encryption | Strongest + provably secure |

### Operational Complexity

| Approach | Complexity | What You Manage |
|----------|-----------|----------------|
| **Lambda** | Low | Code + config only |
| **Bedrock AgentCore** | Low | Agent code + framework config |
| **Cloud Run** | Low-Medium | Container + IAM + VPC rules |
| **Azure Dynamic Sessions** | Low | Session pool config |
| **GKE Agent Sandbox** | Medium | Kubernetes cluster + sandbox config |
| **Fargate** | Medium | Task defs + VPC + IAM + service config |
| **Firecracker DIY** | Very High | Everything: kernel, rootfs, networking, storage, scheduling, monitoring, API |
| **gVisor on K8s** | Medium | Kubernetes + runtime config |

---

## Key Data Points

### Raw Numbers Worth Remembering

- Firecracker: **< 5 MiB memory overhead per microVM**, **125ms boot**, **150 microVMs/sec/host**
- AWS Lambda handles **trillions of function executions monthly** on Firecracker
- Microsoft Copilot (1B+ users) runs code execution on **Azure Container Apps Dynamic Sessions**
- GKE Agent Sandbox pre-warmed pools: **90% improvement** over cold starts
- Cursor writes **~1 billion lines of accepted code per day** (as of mid-2025)
- Replit runs **tens of thousands of Repls concurrently**
- Modal users (Lovable, Quora) run **millions of untrusted code snippets daily**
- Together Code Sandbox snapshot restore: **500ms P95**

### Cost of Bare-Metal DIY

- i3.metal on-demand: **~$4.99/hour** (~$3,593/month)
- Can run potentially hundreds of microVMs per host (given 512 GB RAM, 72 vCPUs)
- At 200 concurrent microVMs per host, that's ~$0.025/hour per microVM
- But: you pay for the host 24/7, plus engineering time to build and maintain the orchestration layer
- Minimum commitment: 1 bare-metal machine

### Who Uses What

| Company | Technology | Source |
|---------|-----------|--------|
| AWS Lambda | Firecracker | AWS (creator) |
| AWS Fargate | Firecracker | AWS (creator) |
| AWS Bedrock AgentCore | Firecracker | AWS |
| Vercel Sandbox | Firecracker microVMs | https://vercel.com/docs/vercel-sandbox/reference/readme |
| Fly.io | Firecracker | https://fly.io/machines |
| Microsoft Copilot | Azure Dynamic Sessions (Hyper-V) | Microsoft blog |
| Google Cloud Run | gVisor | Google |
| GKE Agent Sandbox | gVisor (+ Kata option) | Google |
| Replit | Linux containers + Nix + snapshots | Replit blog |
| Together Code Sandbox | CodeSandbox microVMs | Together docs |
| Modal | Serverless containers | Modal |
| Northflank | Firecracker / gVisor / Kata (configurable) | Northflank |
| Koyeb | Firecracker | Firecracker project page |
| Cloudflare | V8 isolates (Workers) | Cloudflare (different model entirely) |

### Key Tradeoffs Summary

```
                    ISOLATION STRENGTH
                         ^
                         |
         Confidential    |   Firecracker/Hyper-V
         Computing       |   (Lambda, Fargate, Fly.io,
         (SEV-SNP)       |    Vercel, Bedrock AgentCore)
                         |
                         |   gVisor
                         |   (Cloud Run, GKE Sandbox)
                         |
                         |   Kata Containers
                         |   (GKE option, Azure option)
                         |
                         |   Standard Containers
                         |   (Docker, basic K8s)
                         |
                         |   V8 Isolates
                         |   (Cloudflare Workers)
         ----------------+-------------------------->
                    STARTUP SPEED / OPERATIONAL SIMPLICITY
```

### Bottom Line for "Build Your Own Agent Sandbox"

**If you want the managed path:**
- **AWS**: Bedrock AgentCore Runtime (purpose-built), or Lambda for short tasks
- **GCP**: Cloud Run (easiest) or GKE Agent Sandbox (most control)
- **Azure**: Container Apps Dynamic Sessions (battle-tested at Copilot scale)

**If you want to DIY with strong isolation:**
- Firecracker on bare-metal EC2: strongest isolation, highest operational burden
- Fly.io Machines API: Firecracker without managing bare metal (significant middle ground)
- gVisor on GKE/K8s: good isolation, lower ops than Firecracker DIY

**The uncomfortable truth about DIY Firecracker:**
The microVM technology is simple and well-documented. The hard part is everything around it: networking, storage, scheduling, monitoring, snapshotting, API layers, multi-host orchestration. Companies like Fly.io, Vercel, and AWS spent years building these systems. Building a production-grade version from scratch is a multi-month, multi-engineer effort.

**The "Fly.io middle ground":**
Fly.io gives you Firecracker microVMs via API without managing bare metal. Per-second billing, sub-second starts, global networking. If you want VM-level isolation without building infrastructure, this is the most pragmatic DIY-adjacent option.
