# Code Execution Sandboxes for Agent Runtimes: The Infrastructure That Actually Matters

**Date:** 2-7-26
**Category:** Research Report

---

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [Background: Why Sandboxes Exist](#background-why-sandboxes-exist)
3. [Core Concepts: The Technical Primitives](#core-concepts-the-technical-primitives)
4. [Isolation Technologies: What You're Actually Choosing Between](#isolation-technologies-what-youre-actually-choosing-between)
5. [The Market: Every Option Compared](#the-market-every-option-compared)
6. [Cloud Provider Native Options](#cloud-provider-native-options)
7. [How the Industry Actually Uses These](#how-the-industry-actually-uses-these)
8. [Economics: What This Costs at Scale](#economics-what-this-costs-at-scale)
9. [Key Takeaways](#key-takeaways)
10. [Predictions](#predictions)

---

## Executive Summary

Cursor alone produces nearly 1 billion lines of accepted code per day. AWS Lambda processes trillions of function invocations monthly on Firecracker microVMs. Microsoft Copilot runs code execution for 1B+ users on Azure Hyper-V sandboxes. The question isn't whether you need a sandbox for AI-generated code --- it's which one.

The landscape has converged on four isolation technologies, each with different tradeoffs between security, speed, and compatibility:

```
Isolation Strength vs. Startup Speed

  Isolation
     ^
     |
     |   Confidential VMs (SEV-SNP/TDX) --- Provably secure, slow, expensive
     |
     |   MicroVMs (Firecracker) ----------- Hardware boundary, 125ms boot, <5MB overhead
     |
     |   App Kernels (gVisor) ------------- Syscall interposition, ~100ms, no KVM needed
     |
     |   Containers (Docker/OCI) ---------- Shared kernel, 10-50ms, weakest isolation
     |
     |   Runtime Sandboxes (Wasm/V8) ------ No syscall ABI, <10ms, limited compatibility
     |
     +--------------------------------------------------------------> Startup Speed
```

The managed platform market is dominated by **E2B** (Firecracker, $21M raised, powers Perplexity and Manus), **Daytona** (containers, $24M Series A, 48.7k GitHub stars), and **Modal** (gVisor, Python-first, GPU support). All three major clouds now have purpose-built sandbox offerings: AWS Bedrock AgentCore, GCP's GKE Agent Sandbox, and Azure Container Apps Dynamic Sessions.

The bottom line: if you're building agents that generate and execute code, you need a sandbox. If you're running fewer than 100K sessions/day, use a managed platform. If you're running more, evaluate DIY Firecracker --- but budget 6-12 months of engineering time for the infrastructure around the VM.

---

## Background: Why Sandboxes Exist

An AI agent asks: "Let me run a program."

Sometimes it's `pytest`. Sometimes it's `pip install sketchy-package && python run.py`. The moment you let an agent execute code, you're running untrusted bytes on infrastructure you care about.

The failure modes go well beyond "escape":

| Failure Mode | What Happens | Example |
|---|---|---|
| **Secret exfiltration** | Agent reads `~/.ssh`, `~/.aws`, API tokens | Code phones home with credentials |
| **Data leakage** | Agent sends proprietary code to external servers | Model-generated code includes telemetry |
| **Resource exhaustion** | Fork bombs, crypto mining, infinite loops | Agent pegs all CPUs, OOMs the host |
| **Lateral movement** | Agent reaches internal services via network | Pivots from sandbox to production DB |
| **Kernel exploitation** | Vulnerability in shared kernel = host root | Container escape via Dirty Pipe, runc bugs |
| **Training-time manipulation** | RL agent learns to exploit sandbox weaknesses | [Inflates reward signals during training](https://arxiv.org/html/2602.04196v1) |

A sandbox is the answer. It combines three things:

1. **Boundary** --- where isolation is enforced (container namespace, guest kernel, runtime)
2. **Policy** --- what the code can touch (files, network, devices, syscalls)
3. **Lifecycle** --- what persists between runs (nothing, workspace, snapshot)

When evaluating any sandbox, ask three questions:
1. What is **shared** between this code and the host?
2. What can the code **touch** (files, network, devices)?
3. What **survives** between runs?

If you can answer those, you understand your sandbox. If you can't, you're guessing.

---

## Core Concepts: The Technical Primitives

These are the building blocks that every sandbox platform uses. Understanding them is essential for evaluating any option.

### Volumes: How Data Persists

Sandboxes are ephemeral by default. Volumes solve the persistence problem.

```
                   Volume Approaches

  ┌─────────────────┬──────────────────┬────────────────────────┐
  │  Block Devices  │   virtio-fs      │  Network-Attached      │
  │  (virtio-blk)   │   (shared fs)    │  (NFS/FUSE/custom)     │
  ├─────────────────┼──────────────────┼────────────────────────┤
  │ Raw disk image  │ Host dir shared  │ Remote storage mounted │
  │ attached to VM  │ into guest VM    │ over network           │
  │                 │                  │                        │
  │ Fast, simple    │ Near-native perf │ Flexible, shareable    │
  │ Not shareable   │ POSIX semantics  │ Higher latency         │
  │ Fixed size      │ DAX support      │ Scalable               │
  └─────────────────┴──────────────────┴────────────────────────┘
```

**Block devices (virtio-blk):** A raw disk image on the host presented to the guest as `/dev/vda`. Simple, fast, well-supported. This is how Firecracker and Lambda work. The downside: you can't share a block device across multiple VMs, and the size is fixed at creation.

**virtio-fs:** A shared filesystem protocol over virtio, using FUSE in the guest. The host runs a `virtiofsd` daemon; the guest mounts a host directory with near-native performance and full POSIX semantics. Available since Linux 5.4. Used by Kata Containers and QEMU-based platforms. Not supported in Firecracker (Firecracker deliberately keeps its device model minimal).

**Network-attached storage:** How managed platforms handle volumes at scale. Modal's volume system uses a distributed filesystem backed by object storage --- containers mount `/data`, writes are explicitly committed with `commit()`, and other containers see changes after `reload()`. E2B keeps storage ephemeral by default and uses pause/resume snapshots for persistence.

**How platforms handle volumes:**

| Platform | Volume Model | Persistence | Max Size |
|---|---|---|---|
| **Modal** | Distributed FS, explicit commit/reload | Indefinite | 2.5 GB/s bandwidth, 500K files (v1) |
| **E2B** | Ephemeral, persist via pause/resume | Until explicit delete | Per-template |
| **Daytona** | Persistent, archivable to object storage | Indefinite + archive | Configurable |
| **Cloudflare** | Ephemeral disk + Durable Objects for state | Session + DO lifetime | 2-20 GB by instance |
| **Fly.io** | Persistent volumes, mountable across restarts | Until deleted | Configurable |

### Snapshots: The Key to Fast Cold Starts

This is the single most important optimization in the sandbox space. It's how platforms achieve sub-100ms startup times.

A snapshot captures VM state at a point in time. There are two types:

```
┌──────────────────────┬──────────────────────────┐
│   Memory Snapshot    │   Filesystem Snapshot     │
├──────────────────────┼──────────────────────────┤
│ - vCPU registers     │ - Root filesystem        │
│ - RAM contents       │ - Installed packages     │
│ - Device state       │ - User files             │
│ - Kernel state       │ - Config files           │
│ - Running processes  │                          │
│ - Network state      │                          │
├──────────────────────┼──────────────────────────┤
│ Size: 128 MB - 2 GB  │ Size: 50 MB - 20 GB     │
│ Restore: 15-50ms     │ Restore: 100-500ms       │
│ Full process state   │ Must re-boot + re-init   │
└──────────────────────┴──────────────────────────┘
```

**How Firecracker snapshots work:** Firecracker creates a `vmstate` file (vCPU registers, device state, interrupt controller) and a `memory` file (complete guest RAM dump). It also supports **diff snapshots** --- only storing pages that changed since the last snapshot. A full snapshot of a 512MB VM is ~512MB; a diff snapshot might be ~30MB.

**Copy-on-Write restore (the real innovation):**

Instead of reading the entire memory file into RAM (100-500ms for 512MB on NVMe), CoW restore does this:

```
1. mmap() memory file as read-only       ← Near-instant (just page table setup)
2. Set up userfaultfd for write traps
3. Resume vCPU
4. On write: copy single 4KB page        ← Happens lazily, on demand

Typical working set: only 10-30% of pages are ever touched
= 70-90% of snapshot memory is never copied from disk

Result: 15-50ms restore time vs 100-500ms for full copy
```

Research systems like [FaaSnap](http://faculty.washington.edu/wlloyd/courses/tcss591/papers/FaaSnap-FaaSMadeFastUsingSnapshot-basedVMs.pdf) go further: they profile which pages are accessed during the first N invocations, build a "loading set," and prefetch those pages in the background while the guest starts immediately. This achieves 3.5x faster end-to-end than baseline snapshot restore.

**The uniqueness problem:** When you clone a snapshot, all clones start with identical state --- same random seed, same UUID generator state, same TLS session keys. Clone 1 and Clone 2 generate the same "random" UUID. [AWS's solution](https://arxiv.org/abs/2102.12892): inject fresh entropy via an MMIO device on restore, re-seed all PRNGs, force TLS renegotiation.

### Boot Times: What Determines Cold Start

```
Cold Start Breakdown (microVM without snapshots):

  VMM Init        ██              ~1-5ms     (Firecracker starts, configures KVM)
  Kernel Boot     ████████████    ~80-125ms  (Linux kernel init, drivers, mm setup)
  Userspace Init  ████████        ~50-200ms  (/init, mount filesystems, services)
  App Start       ████████████    ~100ms-10s (Python: ~300ms, Java: ~2-5s, Node: ~200ms)
                  ├──────────────────────────┤
                  Total: 230ms - 10s+ (app-dependent)
```

With snapshot restore, you skip everything and land directly in a running state. The kernel is already booted, packages are loaded, the application is initialized.

**Cold start comparison across platforms:**

| Platform | P50 | P95 | Method |
|---|---|---|---|
| **Blaxel** (standby resume) | ~25ms | ~40ms | Warm standby |
| **HopX** (warm pool) | 12ms | 18ms | Pre-warmed pool |
| **Daytona** | ~90ms | ~150ms | Optimized containers |
| **E2B** | ~150ms | ~300ms | Firecracker templates |
| **Firecracker** (raw cold boot) | ~125ms | ~180ms | Cold boot |
| **Lambda + SnapStart** | <200ms | ~400ms | CRaC snapshots |
| **Modal** | Sub-second | ~1-2s | Container + snap |
| **Cloudflare Containers** | 2-3s | ~5s | Container start |
| **Traditional VM** | 30-60s | ~90s | Full OS boot |

**Warm pools** eliminate cold starts entirely by keeping pre-booted VMs ready for instant handoff:

```
Request arrives → Claim VM from pool (~1-2ms) → Configure networking (~3-5ms) → Ready

Total handoff time: ~10-15ms

Cost: You're paying for idle VMs 24/7
Pool sizing: target = peak_concurrent_sessions * 1.2
```

### Networking: Isolation, Connectivity, and Access

Sandbox networking balances three concerns: **isolation** (prevent escape), **connectivity** (sandbox needs internet), and **accessibility** (users need to reach services inside the sandbox).

```
Outbound (Sandbox → Internet):

  ┌────────────────────┐
  │     Guest VM       │
  │  eth0: 172.16.0.2  │
  └────────┬───────────┘
           │ virtio-net
  ┌────────┴───────────┐
  │    TAP device      │  ← Virtual network interface on host
  └────────┬───────────┘
  ┌────────┴───────────┐
  │   iptables NAT     │  ← Source NAT (MASQUERADE) + egress allowlist
  └────────┬───────────┘
  ┌────────┴───────────┐
  │    Host NIC → Internet
  └────────────────────┘
```

**Egress controls vary wildly:**

| Platform | Default | Controls Available |
|---|---|---|
| **Modal** | Open | `block_network=True`, `cidr_allowlist=["10.0.0.0/8"]` |
| **E2B** | Open, unrestricted | No built-in egress filtering |
| **OpenAI Code Interpreter** | No internet access | Fully air-gapped |
| **Cloudflare** | Through Workers gateway | Gateway policies |
| **Firecracker (DIY)** | You decide | iptables/nftables, anything you build |

**Inbound access patterns:**

| Approach | How It Works | Used By |
|---|---|---|
| **Tunnels** | Proxy routes traffic to sandbox port via unique URL | Modal, Fly.io |
| **Preview URLs** | Sandbox gets unique subdomain, reverse proxy routes to VM | E2B, Daytona, CodeSandbox |
| **Connect tokens** | Auth token scoped to a sandbox, passed in headers | Modal |
| **SSH** | Direct SSH access, port forwarding | E2B, traditional |

### Image / Template Systems

How you define what's inside a sandbox before it starts.

```
Three approaches:

  Docker/OCI Images          VM Images (disk)         SDK-Defined (code-first)
  ─────────────────          ────────────────         ─────────────────────────
  FROM ubuntu:22.04          dd if=/dev/zero          modal.Image
  RUN pip install numpy      mkfs.ext4                 .debian_slim()
  COPY app /app              mount + install            .pip_install("numpy")

  Used by: E2B, Daytona,    Used by: Firecracker     Used by: Modal
  Cloudflare, Beam           (internal), Lambda
```

**E2B templates:** Write a Dockerfile, run `e2b template build`, get a snapshot-ready image. Under the hood, the OCI image is converted to a rootfs that Firecracker can boot, then pre-snapshotted for fast restore. Fast iteration, Docker familiarity.

**Modal SDK-defined images:** Pure Python --- `modal.Image.debian_slim().pip_install("numpy").apt_install("ffmpeg")`. Each method call creates a content-addressed layer. No Dockerfile, no Docker daemon, no registry config. Images compose at runtime.

### Scale-to-Zero

The mechanism by which platforms stop charging you when there's no work.

```
Scale-to-Zero State Machine:

  ┌─────────┐  request   ┌──────────┐  complete  ┌──────────┐
  │  ZERO   │──────────>│ SCALING  │──────────>│ RUNNING  │
  │(no VMs) │           │   UP     │           │(serving) │
  └─────────┘           └──────────┘           └──────────┘
       ^                                            │
       │              idle timeout                  │
       └────────────────────────────────────────────┘
                    (5-30 min idle)

Tradeoff:
  Scale-to-zero saves:    100% of idle compute cost
  Scale-to-zero costs:    Cold start latency on first request

Most platforms use a hybrid:
  Night/weekend → Scale to zero ($0/hr)
  Business hours → Warm pool ($$$/hr)
  Demand spikes → Auto-scale up
```

---

## Isolation Technologies: What You're Actually Choosing Between

This is the most important decision. Everything else is details.

### Containers (Docker/OCI)

Containers are processes in separate Linux namespaces, sharing the host kernel. Isolation comes from four kernel features:

```
Namespace Isolation:
  - PID namespace:     Isolated process tree
  - Mount namespace:   Isolated filesystem view
  - Network namespace: Isolated network stack
  - User namespace:    Maps container root to unprivileged host UID

+ Cgroups:    CPU/memory/IO limits (prevent resource exhaustion)
+ Seccomp:    Syscall filtering (block dangerous syscalls)
+ AppArmor/SELinux: Additional access control
```

**The problem:** Every syscall still goes to the host kernel. A kernel bug reachable via any allowed syscall path is a host escape. Dirty COW ([CVE-2016-5195](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2016-5195)), Dirty Pipe ([CVE-2022-0847](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2022-0847)), runc overwrite ([CVE-2019-5736](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2019-5736)) --- all were container escapes from properly configured containers.

**For sandbox use:** Containers are fine when all code inside is in the same trust domain as the host. The moment you accept code from outside your trust boundary (users, agents, plugins), the shared kernel is a conscious risk.

### gVisor (Application Kernel)

gVisor interposes a userspace kernel called the **Sentry** between the application and the host kernel. Application syscalls go to the Sentry; the Sentry makes a small, auditable set of host syscalls.

```
Without gVisor:                With gVisor:

  App syscall ──→ Host kernel    App syscall ──→ Sentry (userspace)
                                                   │
                                                   └──→ 68 host syscalls
                                                        (vs hundreds for containers)
```

**Tradeoffs:**
- Not every syscall and kernel behavior is identical --- there's a [compatibility table](https://gvisor.dev/docs/user_guide/compatibility/linux/amd64/)
- Syscall-heavy workloads pay overhead (each syscall goes through an extra layer)
- No hardware virtualization required --- runs on any Linux host, even inside a VM
- Used in production by Google Cloud Run, Cloud Functions, App Engine, and by OpenAI for ChatGPT's code interpreter

### MicroVMs (Firecracker, cloud-hypervisor, libkrun)

MicroVMs run a **guest kernel** behind hardware virtualization (KVM). The host kernel sees KVM ioctls and virtio device I/O --- not the full Linux syscall ABI.

```
Container:                     MicroVM:

  App ──syscalls──→ Host kernel   App ──syscalls──→ Guest kernel
                                                       │
                                                  VM exits/virtio
                                                       │
                                                  Host kernel (KVM)
```

**Firecracker** (AWS, open-source) is the dominant microVM. Intentionally boring: one process per VM, minimal virtio device model (net, block, vsock, console), a "jailer" that chroots/namespaces/seccomps the VMM process before the guest runs. The VMM itself uses only 24 syscalls and 30 ioctls.

```
Firecracker by the numbers:
  Memory overhead:       < 5 MiB per microVM
  Boot time:             ~125ms
  Creation rate:         150 microVMs/sec/host
  Device model:          4 devices (net, block, vsock, console)
  VMM seccomp profile:   24 syscalls + 30 ioctls
```

**cloud-hypervisor** is the feature-rich alternative: PCI-based virtio, CPU/memory hotplug, VFIO GPU passthrough, Windows guest support. Use this when you need "VM boundary + GPU passthrough."

**libkrun** embeds a VMM as a C library. Powers microsandbox (self-hosted microVMs) and Podman's VM-level isolation. Works on macOS via Hypervisor.framework.

### Runtime Sandboxes (WebAssembly, V8 Isolates)

The sandboxed code never gets the host's syscall ABI. It only gets capabilities the runtime explicitly provides.

```
Container/gVisor/microVM:           Runtime Sandbox:

  Code gets a syscall ABI            Code gets explicit host functions
  (full Linux, filtered Linux,       (preopened dirs, specific APIs)
   or guest Linux)                   No ambient filesystem/network
```

**WebAssembly:** Modules can't touch the outside world unless the host provides imports. WASI adds capability-oriented filesystem access (preopened directories). Instance startup can be microseconds. Limited to WASM-compilable languages.

**V8 Isolates:** Separate instances of the V8 JS engine with isolated heaps. Cloudflare Workers runs thousands of tenants per machine. Near-zero cold start. Limited to JS/TS.

### Technology Decision Table

| Workload | Threat Model | Recommended Boundary |
|---|---|---|
| AI coding agent (multi-tenant SaaS) | Hostile (user code) | **MicroVM** (Firecracker) |
| AI coding agent (single-tenant) | Semi-trusted | **gVisor** or hardened container |
| RL rollouts (parallel, many resets) | Needs fast reset | **MicroVM** with snapshot |
| Code interpreter (stateless snippets) | Hostile | **gVisor** or runtime sandbox |
| Tool calling / plugins | Mixed | **Wasm / V8 isolates** |
| Shell access + package managers | Hostile | **MicroVM** (only option with full Linux) |

---

## The Market: Every Option Compared

### Purpose-Built Agent Sandbox Platforms

| Platform | Technology | Cold Start | SDKs | GPU | Self-Host | Pricing |
|---|---|---|---|---|---|---|
| **E2B** | Firecracker microVM | ~150ms | Python, JS/TS | No | Yes (GCP) | $0.000014/vCPU/s |
| **Daytona** | OCI containers | ~90ms | Python, TS | Yes | Yes | $0.000014/vCPU/s |
| **Modal** | gVisor containers | Sub-second | Python, JS (beta), Go (beta) | Extensive | No | $0.00003942/core/s |
| **Blaxel** | Standby + resume | ~25ms | Python, TS | No | No | $0.0000115/GB/s |
| **Runloop** | Custom hypervisor | Not published | Python, TS | No | No | Not published |
| **Cloudflare Sandbox** | Containers | 2-3s | TypeScript | No | No | $0.000020/vCPU/s |
| **Vercel Sandbox** | Firecracker microVM | Fast | TypeScript | No | No | $0.128/CPU-hr |
| **Fly.io Machines** | Firecracker microVM | Sub-second | REST/CLI | No | No | ~$0.000002/CPU/s |
| **microsandbox** | libkrun microVM | <200ms | Python, TS | No | Yes (only) | Free (self-hosted) |
| **Beam** | Containers | 2-3s | Python, TS (beta) | Extensive | Yes | $0.190/core/hr |

### Key Players Deep-Dive

**E2B** --- The AI sandbox incumbent. Raised $21M. Open-source (Apache 2.0). Firecracker-based with 150ms cold starts. Key customers: Perplexity (shipped advanced data analysis in one week using E2B), Manus (virtual computers for agents), Hugging Face (RL training pipelines), Groq. Template system lets you pre-bake environments with Docker. 24-hour max session on Pro.

**Daytona** --- The growth rocket. Raised $24M Series A (Feb 2026, led by FirstMark, with Datadog and Figma Ventures). Hit $1M forward ARR in under 3 months, doubled it 6 weeks later. 48.7k GitHub stars. Sub-90ms cold starts through optimized container orchestration. Differentiator: stateful sandboxes with Git-like branching (fork, snapshot, restore). Key customers: LangChain, Turing, Writer, SambaNova. AGPL-3.0 license (important --- requires open-sourcing modifications made available over a network, which pushes enterprises toward commercial licenses).

**Modal** --- The Python-first infrastructure play. Not purely a sandbox company --- also does inference, training, batch jobs. Strengths: massive autoscaling (10K+ concurrent units), GPU support, code-first image definition. Used by Lovable and Quora for millions of daily code executions. Official cloud evaluation partner for SWE-bench. Weakness: no BYOC option.

**Runloop** --- The deepest technical pedigree. Founded by Jonathan Wall (former tech lead of Google File System, founding engineer at Google Wallet, founder of Inde acquired by Stripe). Custom bare-metal hypervisor with 2x faster vCPUs. Only provider with both arm64 and x86 support. Official LangChain sandbox provider. Less visibility than E2B/Daytona but potentially the strongest technology.

**Fly.io** --- The pragmatic middle ground. Firecracker microVMs via REST API without managing bare metal. Sub-second starts, per-second billing, global networking across 35 regions. Not specifically built for agent sandboxes, but Fly explicitly pitches: "Confidently deploy sketchy LLM-generated code." The most accessible DIY-adjacent option.

---

## Cloud Provider Native Options

You don't have to use a third-party platform. All three clouds now have purpose-built offerings.

### AWS

| Service | Technology | Cold Start | Best For |
|---|---|---|---|
| **Bedrock AgentCore Runtime** | Firecracker microVM | 300-800ms | Agents in the Bedrock ecosystem |
| **Lambda** | Firecracker microVM | 100ms-5s | Short code execution (<15 min) |
| **Lambda + SnapStart** | Firecracker + CRaC snapshots | <200ms | Cold-start-sensitive workloads |
| **Fargate** | Firecracker microVM | 15-40s | Long-running containers |

**Bedrock AgentCore** is the purpose-built option. Each agent session gets a dedicated Firecracker microVM, deterministic teardown, session-level isolation. Supports container-based or direct Python deployment. Tied to the Bedrock ecosystem.

**Lambda** processes trillions of invocations monthly, but the 15-minute timeout and ephemeral filesystem make it unsuitable for long-running agent sandboxes. Great for short code execution.

### GCP

| Service | Technology | Cold Start | Best For |
|---|---|---|---|
| **GKE Agent Sandbox** (Nov 2025) | gVisor + optional Kata | Sub-second (pre-warmed) | Agent workloads on Kubernetes |
| **Cloud Run** | Hardware virt + gVisor | 0.5-2s | Sandboxed containers, simplest path |
| **Cloud Functions (2nd gen)** | Same as Cloud Run | 0.5-2s | Short functions |

**GKE Agent Sandbox** is the most opinionated GCP answer. Announced at KubeCon NA 2025. Killer feature: **pre-warmed pools with 90% cold start reduction**. Supports Pod Snapshots for checkpoint/restore. Being built as a CNCF open-source project (not GKE-locked). Google explicitly states: "This isolation lets you run untrusted code, such as code generated by a large language model."

### Azure

| Service | Technology | Cold Start | Best For |
|---|---|---|---|
| **Container Apps Dynamic Sessions** | Hyper-V (Type-1) | Near-instant (pooled) | Agent code execution at scale |
| **Confidential ACI/AKS** | AMD SEV-SNP / Intel TDX | Slower | Regulated industries, data privacy |

**Dynamic Sessions** is the standout. Hyper-V is a Type-1 (bare-metal) hypervisor --- stronger isolation than containers or gVisor. The proof point: **Microsoft Copilot uses this for code execution, serving 1B+ users**. Built-in LangChain and Semantic Kernel integrations. Session pools mitigate cold starts.

### DIY on Cloud

For teams that want full control:

```
Option 1: Firecracker on bare-metal EC2

  What you get: ~125ms boot, <5MB overhead, 150 VMs/sec, strongest isolation
  What you build: Kernel images, rootfs, networking (TAP+iptables), storage,
                  scheduling, monitoring, snapshotting, API layer, multi-host
                  orchestration
  Cost: i3.metal at ~$5/hr + 6-12 months engineering
  Reality: The microVM tech is simple. The infrastructure around it is the
           multi-month, multi-engineer effort.

Option 2: gVisor on GKE/Kubernetes

  What you get: Strong isolation without KVM, Kubernetes-native, drop-in runtime
  What you build: Kubernetes cluster management (or use GKE Autopilot for ~zero ops)
  Cost: GKE pricing + gVisor overhead
  Reality: Lowest-ops path to strong isolation. Kubernetes is the operational burden.

Option 3: Fly.io Machines API

  What you get: Firecracker microVMs via API, no bare metal management
  What you build: Orchestration logic on top of their API
  Cost: Per-second billing, ~$0.000002/CPU/s
  Reality: The pragmatic "DIY-adjacent" option. VM isolation without VM ops.
```

---

## How the Industry Actually Uses These

### AI Labs: What Powers the Code Interpreters

| Company | Technology | Notable Detail |
|---|---|---|
| **OpenAI** (Code Interpreter) | gVisor on Kubernetes | [Reverse-engineered](https://ryan.govost.es/2025/openai-code-interpreter/): FastAPI server on port 8080, no internet access |
| **OpenAI** (Codex) | Per-task cloud sandbox | Each task gets isolated sandbox with cloned repo |
| **Anthropic** (Claude Code) | OS-level primitives (`sandbox-exec` / `bubblewrap`) | [Open-sourced as `srt`](https://github.com/anthropic-experimental/sandbox-runtime). Reduced permission prompts by 84% |
| **Google** (Gemini) | gVisor | [Researchers extracted internal source code](https://www.vulnu.com/p/researchers-hack-source-code-from-google-gemini) from inside the sandbox without escaping it |
| **Microsoft** (Copilot) | Azure Dynamic Sessions (Hyper-V) | 1B+ users. Production-proven at extreme scale |

The striking pattern: OpenAI and Google both use gVisor. Anthropic went the lightest possible route --- OS-level process restriction, no container, no VM. Microsoft went the heaviest --- full Hyper-V Type-1 hypervisor. All approaches have had security incidents or researcher-demonstrated weaknesses.

### Coding Assistants: A Fundamental Architecture Split

```
Local Execution (no sandbox)          Cloud Execution (sandboxed)
─────────────────────────────         ────────────────────────────
Cursor (shadow workspaces)            GitHub Copilot (Actions runners)
Windsurf (local + optional DevBox)    Devin (cloud VMs, 3 deployment tiers)
                                      Replit (CoW snapshots, most sophisticated)
```

**Cursor** does NOT use remote sandboxes. Agent Mode runs 8 AI agents simultaneously, all executing on the user's local machine. The "sandbox" is a shadow workspace for AI iteration, not execution isolation. This is a ticking time bomb as agents become more autonomous.

**Replit** has the most sophisticated approach. Their [snapshot engine](https://blog.replit.com/inside-replits-snapshot-engine) uses Copy-on-Write at the block device level: the agent forks the entire filesystem instantly, tries risky changes, and reverts if they fail. Databases are snapshotable too. The agent never touches production.

**Devin** operates as a fully autonomous engineer with its own cloud VM per session. Three enterprise deployment tiers: multi-tenant SaaS, dedicated SaaS with private networking, and customer-hosted VPC. Nubank deployed Devin to refactor millions of lines, achieving 8x efficiency and 20x cost savings.

### Open Source Agent Frameworks

| Framework | Default Sandbox | Approach |
|---|---|---|
| **AutoGen** (Microsoft) | Docker container | `DockerCommandLineCodeExecutor`, made default in v0.2.8 |
| **LangChain** | Pyodide (WebAssembly) for light, Runloop/Daytona/Modal for heavy | Multi-tier |
| **CrewAI** | Manual Docker setup | Less integrated |
| **smolagents** (Hugging Face) | Import allowlist | Simplest, most restrictive |
| **OpenHands** | Docker container per agent | Parallelized across containers |

AutoGen making Docker the default was a deliberate breaking change. Microsoft's rationale: "It's easy particularly for new users to overlook code-execution risks." The trend is toward mandatory isolation, not optional.

### Benchmarking Infrastructure

**SWE-bench** standardized on Docker. Each of 12 Python repositories gets its own Docker image. [Epoch AI optimized these images 10x](https://epoch.ai/blog/swebench-docker) (670 GiB to 67 GiB), enabling the full SWE-bench Verified benchmark in 62 minutes on a single GitHub Actions VM. Modal is the official cloud evaluation partner for parallelized runs.

### RL Training: The Next Frontier

RL training for coding agents requires running generated code thousands or millions of times. Each rollout needs isolation, speed, reproducibility, and massive parallelism.

The key insight from [Collinear AI](https://blog.collinear.ai/p/rl-env-as-a-service): RL training is fundamentally a **distributed systems problem**, not an ML problem. The ML is the easy part; managing thousands of parallel sandbox instances is the hard part. The concept of "Environment-as-a-Service" --- separating the data plane (sandbox) from the control plane (orchestration) --- mirrors the evolution of databases and compute.

A [February 2026 paper from Tsinghua/NUS](https://arxiv.org/html/2602.04196v1) showed that models can learn to exploit sandbox weaknesses *during training itself*, manipulating environments to inflate reward signals. This makes sandbox security during training as important as during inference.

---

## Economics: What This Costs at Scale

### Per-Session Costs (1 vCPU, 512 MiB, 5-minute session)

```
Platform         │ Per-Session Cost │ Monthly at 1M/day
─────────────────┼──────────────────┼──────────────────
E2B              │ ~$0.005          │ ~$135,000
Daytona          │ ~$0.005          │ ~$135,000
Blaxel           │ ~$0.005          │ ~$135,000
Modal            │ ~$0.006          │ ~$180,000
Cloudflare       │ ~$0.006          │ ~$189,000
DIY (Firecracker)│ ~$0.001-0.003    │ ~$24K-90K
```

### Build vs. Buy Decision

```
Sessions/day     Recommendation     Why
─────────────    ──────────────     ─────────────────────
< 10K            Managed            Not worth the eng cost
10K - 100K       Managed            Still cheaper overall
100K - 500K      Evaluate           Depends on team size/capability
500K - 1M        Likely DIY         Savings justify engineering
> 1M             Definitely DIY     Managed costs explode linearly
```

### Hidden Costs That Kill You

**Egress:** At 1M sessions/day producing 1MB output each = 30TB/month. AWS: $2,700/month. Cloudflare: $750/month.

**Warm pools:** 1,000 idle VMs on E2B = $36K/month. Same 1,000 VMs on EC2 = ~$1,660/month. Managed warm pools cost 20x more than DIY because you're paying per-second for idle compute.

**Billing granularity matters enormously:** A 30-second task billed per-second costs $0.00042. Billed per-hour, it costs $0.05 --- 120x more. At 1M sessions/day, that's the difference between $420/day and $50,000/day.

### Cost Optimization Strategies

1. **Snapshot cloning (CoW):** Clone from a snapshot instead of cold booting. Share 70-90% of base image memory. Restore in 15-50ms vs 125ms.
2. **Scale-to-zero at night:** Full zero-out during dead periods, warm pool during business hours. Saves 30-50% vs 24/7 warm pools.
3. **Spot instances (DIY):** AWS Spot for non-latency-sensitive sandbox workloads. 60-70% savings. Use on-demand for baseline, spot for overflow.
4. **Right-size warm pools:** `pool_size = peak_concurrent_sessions * 1.2`. Too small = cold starts. Too large = wasted spend.

---

## Key Takeaways

1. **The sandbox stack has converged on three practical tiers.** Process-level restriction (Anthropic `srt`) for lightweight/local use, container/gVisor (OpenAI, Google, Modal) for the middle ground, and microVM (E2B, AWS, Fly.io) for maximum isolation. Most production deployments use the middle tier. Most *should* use microVMs.

2. **Firecracker won.** It powers AWS Lambda (trillions of invocations/month), E2B, Fly.io, Vercel Sandbox, and every "serious" DIY deployment. At <5MB overhead, 125ms boot, and hardware-level isolation, it hits the sweet spot better than anything else. gVisor is a strong runner-up when you can't get KVM access.

3. **The three players to watch are E2B, Daytona, and Runloop.** E2B has the customer logos and Firecracker foundation. Daytona has the growth velocity and VC backing. Runloop has the deepest technical pedigree. All three are viable. Modal is a strong option if you're Python-centric and need GPU support.

4. **Cloud providers are catching up fast.** Azure Dynamic Sessions (Hyper-V, 1B+ users via Copilot), GKE Agent Sandbox (gVisor, pre-warmed pools, Pod Snapshots), and Bedrock AgentCore (Firecracker) are all production-ready. If you're already deep in one cloud, the native option is increasingly compelling.

5. **Containers are not a security boundary for untrusted code.** 94% of organizations reported serious container security incidents. 60% were vulnerable to "Leaky Vessels" container escape CVEs. If you're running agent-generated code in plain Docker, you're betting on the Linux kernel having no exploitable bugs in any reachable syscall path. That's a losing bet.

6. **Snapshots are the critical optimization.** Copy-on-Write snapshot restore is what separates 15ms cold starts from 5-second cold starts. It's what makes warm pools affordable and RL training feasible. If a platform doesn't support snapshots, it has a fundamental ceiling on performance.

7. **The RL training use case is about to explode.** "Environment-as-a-Service" is an unsolved infrastructure problem. Whoever builds the "AWS Lambda of RL environments" --- fast reset, snapshot/restore, massive parallelism, stateful sandboxes --- captures a category. Daytona's Git-like branching is the closest match to what RL pipelines actually need.

8. **Local execution is a ticking time bomb.** Cursor and Windsurf run agent-generated code directly on the developer's machine. As agents become more autonomous (8 parallel agents, multi-file edits, package installation), the risk of local execution becomes unacceptable. Expect both to adopt remote sandboxing within 18 months.

---

## Predictions

1. **Sandbox infrastructure becomes a $1B+ market by 2028.** E2B, Daytona, and Runloop are early leaders, but AWS/GCP/Azure will all ship first-party offerings that integrate with their VPC, IAM, and compliance stacks. Cloud providers win at enterprise scale.

2. **Firecracker beats gVisor for most agent use cases.** gVisor's syscall compatibility issues and performance overhead are friction. Firecracker's hardware isolation with sub-200ms cold starts is the better tradeoff. gVisor survives for lightweight/embedded use and environments without KVM access.

3. **Cursor adds remote sandbox execution within 18 months.** Running LLM-generated code on developer machines is a liability that scales with agent autonomy. They'll partner with or acquire a sandbox provider.

4. **"Environment-as-a-Service" for RL training becomes the next hot infra category.** The separation of data plane (sandbox) and control plane (orchestration) mirrors databases and compute. Daytona's stateful, branchable sandboxes are closest to what RL needs.

5. **WebAssembly sandboxes grow for lightweight tool-calling use cases.** LangChain's Pyodide sandbox and StackBlitz's WebContainers prove that Wasm handles many code execution needs without container overhead. For "run this Python snippet," Wasm is faster and cheaper than spinning up a VM.

6. **A major security incident involving an unsandboxed coding agent hits the mainstream press by end of 2026.** The combination of autonomous agents + local execution + package installation + network access is too large a surface area. Something will go badly wrong, and it will accelerate sandbox adoption industry-wide.

---

## Sources

All sources are cited inline throughout the document. Key references:

- [Modal: Top AI Code Sandbox Products](https://modal.com/blog/top-code-agent-sandbox-products)
- [Superagent: AI Code Sandbox Benchmark 2026](https://www.superagent.sh/blog/ai-code-sandbox-benchmark-2026)
- [Luis Cardoso: A Field Guide to Sandboxes for AI](https://www.luiscardoso.dev/blog/sandboxes-for-ai)
- [awesome-sandbox (curated list)](https://github.com/restyler/awesome-sandbox)
- [Northflank: Best Code Execution Sandbox for AI Agents](https://northflank.com/blog/best-code-execution-sandbox-for-ai-agents)
- [Anthropic: Claude Code Sandboxing](https://www.anthropic.com/engineering/claude-code-sandboxing)
- [Ryan Govostes: OpenAI Code Interpreter](https://ryan.govost.es/2025/openai-code-interpreter/)
- [Replit: Inside Replit's Snapshot Engine](https://blog.replit.com/inside-replits-snapshot-engine)
- [E2B](https://e2b.dev) | [Daytona](https://www.daytona.io) | [Modal](https://modal.com) | [Runloop](https://runloop.ai)
- [Google: Agentic AI on Kubernetes and GKE](https://cloud.google.com/blog/products/containers-kubernetes/agentic-ai-on-kubernetes-and-gke)
- [Azure Dynamic Sessions GA](https://techcommunity.microsoft.com/blog/appsonazureblog/azure-container-apps-dynamic-sessions-general-availability-and-more/4303561)
- [AWS Bedrock AgentCore](https://aws.amazon.com/blogs/machine-learning/ai-agents-in-enterprises-best-practices-with-amazon-bedrock-agentcore/)
- [Collinear AI: RL Env-as-a-Service](https://blog.collinear.ai/p/rl-env-as-a-service)
- [Firecracker Snapshot Documentation](https://github.com/firecracker-microvm/firecracker/blob/main/docs/snapshotting/snapshot-support.md)
- [AWS: Restoring Uniqueness in MicroVM Snapshots](https://arxiv.org/abs/2102.12892)
