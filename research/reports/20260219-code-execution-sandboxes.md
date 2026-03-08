# Code Execution Sandboxes for AI Agents: A Complete Guide

**Date:** 2-7-26
**Category:** Research Report
**Status:** Complete

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Why Sandboxes Exist](#why-sandboxes-exist)
3. [Isolation Technologies](#isolation-technologies)
   - Containers (Docker/OCI)
   - gVisor (Application Kernel)
   - MicroVMs (Firecracker)
   - Runtime Sandboxes (WebAssembly, V8 Isolates)
   - Confidential Computing
   - Technology Decision Table
4. [Core Technical Primitives](#core-technical-primitives)
   - Snapshots & Copy-on-Write Restore
   - Boot Times & Cold Starts
   - Warm Pools
   - Volumes & Persistent Storage
   - Networking
   - Image & Template Systems
   - Scale-to-Zero
5. [The Market: Purpose-Built Sandbox Platforms](#the-market-purpose-built-sandbox-platforms)
   - Platform Comparison Table
   - Key Players Deep-Dive
6. [Cloud Provider Native Options](#cloud-provider-native-options)
   - AWS
   - GCP
   - Azure
   - DIY on Cloud
7. [How the Industry Uses Sandboxes](#how-the-industry-uses-sandboxes)
   - AI Labs: What Powers the Code Interpreters
   - Coding Assistants: The Architecture Split
   - Open Source Agent Frameworks
   - Benchmarking Infrastructure
   - RL Training
   - Enterprise Deployments
8. [Economics at Scale](#economics-at-scale)
   - Per-Session Costs
   - Build vs. Buy
   - Hidden Costs
   - Cost Optimization Strategies
9. [Key Takeaways](#key-takeaways)
10. [Predictions](#predictions)
11. [Sources](#sources)

---

## Executive Summary

Cursor produces nearly 1 billion lines of accepted code per day. AWS Lambda processes trillions of function invocations monthly on Firecracker microVMs. Microsoft Copilot runs code execution for 1B+ users on Azure Hyper-V sandboxes.

The question isn't whether you need a sandbox for AI-generated code --- it's which one.

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

The managed platform market is dominated by **E2B** (Firecracker, $21M raised, powers Perplexity and Manus), **Daytona** ($24M Series A, 48.7k GitHub stars, sub-90ms cold starts), and **Modal** (gVisor, Python-first, GPU support). All three major clouds now have purpose-built sandbox offerings: AWS Bedrock AgentCore, GCP's GKE Agent Sandbox, and Azure Container Apps Dynamic Sessions.

The bottom line: if you're running fewer than 100K sessions/day, use a managed platform. If you're running more, evaluate DIY Firecracker --- but budget 6-12 months of engineering time for the infrastructure around the VM.

---

## Why Sandboxes Exist

An AI agent asks: "Let me run a program."

Sometimes it's `pytest`. Sometimes it's `pip install sketchy-package && python run.py`. The moment you let an agent execute code, you're running untrusted bytes on infrastructure you care about.

The failure modes go beyond "escape":

| Failure Mode | What Happens | Example |
|---|---|---|
| **Secret exfiltration** | Agent reads `~/.ssh`, `~/.aws`, API tokens | Code phones home with credentials |
| **Data leakage** | Agent sends proprietary code to external servers | Model-generated code includes telemetry |
| **Resource exhaustion** | Fork bombs, crypto mining, infinite loops | Agent pegs all CPUs, OOMs the host |
| **Lateral movement** | Agent reaches internal services via network | Pivots from sandbox to production DB |
| **Kernel exploitation** | Vulnerability in shared kernel = host root | Container escape via Dirty Pipe, runc bugs |
| **Training-time manipulation** | RL agent exploits sandbox to inflate rewards | [Tsinghua/NUS, Feb 2026](https://arxiv.org/html/2602.04196v1) |

A sandbox combines three things:

1. **Boundary** --- where isolation is enforced (container namespace, guest kernel, runtime)
2. **Policy** --- what the code can touch (files, network, devices, syscalls)
3. **Lifecycle** --- what persists between runs (nothing, workspace, snapshot)

When evaluating any sandbox, ask three questions:

1. What is **shared** between this code and the host?
2. What can the code **touch** (files, network, devices)?
3. What **survives** between runs?

If you can answer those, you understand your sandbox. If you can't, you're guessing.

---

## Isolation Technologies

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

**The problem:** Every syscall still goes to the host kernel. A kernel bug reachable via any allowed syscall path is a host escape. [Dirty COW](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2016-5195), [Dirty Pipe](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2022-0847), [runc overwrite](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2019-5736) --- all were container escapes from properly configured containers. 94% of organizations have reported serious container security incidents. 60% were vulnerable to "Leaky Vessels" container escape CVEs.

**For sandbox use:** Containers are fine when all code is in the same trust domain as the host. The moment you accept code from outside your trust boundary (users, agents, plugins), the shared kernel is a conscious risk.

### gVisor (Application Kernel)

gVisor interposes a userspace kernel called the **Sentry** between the application and the host kernel. Application syscalls go to the Sentry; the Sentry makes a small, auditable set of host syscalls.

```
Without gVisor:                With gVisor:

  App syscall --> Host kernel    App syscall --> Sentry (userspace)
                                                   |
                                                   └--> 68 host syscalls
                                                        (vs hundreds for containers)
```

**Tradeoffs:**
- Not every syscall is faithfully reproduced --- there's a [compatibility table](https://gvisor.dev/docs/user_guide/compatibility/linux/amd64/)
- Syscall-heavy workloads pay overhead (each syscall goes through an extra layer)
- File system operations are slower than native (multiple context switches)
- CPU-bound workloads: minimal overhead
- No hardware virtualization required --- runs on any Linux host, even inside a VM
- Additional memory consumed by the Sentry process

**Used in production by:** Google Cloud Run, Cloud Functions, App Engine, OpenAI (ChatGPT Code Interpreter), Google Gemini

### MicroVMs (Firecracker, cloud-hypervisor, libkrun)

MicroVMs run a **guest kernel** behind hardware virtualization (KVM). The host kernel sees KVM ioctls and virtio device I/O --- not the full Linux syscall ABI.

```
Container:                     MicroVM:

  App --syscalls--> Host kernel   App --syscalls--> Guest kernel
                                                       |
                                                  VM exits / virtio
                                                       |
                                                  Host kernel (KVM)
```

**Firecracker** (AWS, open-source, Rust) is the dominant microVM. Intentionally minimal: one process per VM, minimal virtio device model, a "jailer" that chroots/namespaces/seccomps the VMM process before the guest runs.

```
Firecracker by the numbers:
  Memory overhead:       < 5 MiB per microVM
  Boot time:             ~125ms
  Creation rate:         150 microVMs/sec/host
  Device model:          4 devices (net, block, vsock, console)
  VMM seccomp profile:   24 syscalls + 30 ioctls
```

**cloud-hypervisor** is the feature-rich alternative: PCI-based virtio, CPU/memory hotplug, VFIO GPU passthrough, Windows guest support. Use when you need VM boundary + GPU passthrough.

**libkrun** embeds a VMM as a C library. Powers microsandbox (self-hosted microVMs) and Podman's VM-level isolation. Works on macOS via Hypervisor.framework.

**Kata Containers** runs each container in a lightweight VM (uses QEMU or Firecracker as VMM). Kubernetes-compatible via `runtimeClassName`. Stronger isolation than gVisor (full VM boundary), slower startup than gVisor but faster than full VMs. Used by Azure for confidential containers.

### Runtime Sandboxes (WebAssembly, V8 Isolates)

The sandboxed code never gets the host's syscall ABI. It only gets capabilities the runtime explicitly provides.

```
Container/gVisor/microVM:           Runtime Sandbox:

  Code gets a syscall ABI            Code gets explicit host functions
  (full Linux, filtered Linux,       (preopened dirs, specific APIs)
   or guest Linux)                   No ambient filesystem/network
```

**WebAssembly:** Modules can't touch the outside world unless the host provides imports. WASI adds capability-oriented filesystem access (preopened directories). Instance startup can be microseconds. Limited to WASM-compilable languages.

**V8 Isolates:** Separate instances of the V8 JS engine with isolated heaps. Cloudflare Workers runs thousands of tenants per machine. Near-zero cold start (<5ms). Limited to JS/TS.

### Confidential Computing

Hardware-backed Trusted Execution Environments (TEEs):

- **AMD SEV-SNP:** Encrypts VM memory in hardware. Used in Azure Confidential ACI/AKS.
- **Intel SGX/TDX:** Enclave-based (SGX) or full VM encryption (TDX). Azure DCsv2/DCsv3 series.
- **Attestation support:** Prove cryptographically that code is running inside a TEE.

Overkill for most agent sandboxing. Designed for data privacy compliance (HIPAA, GDPR edge cases). Slower startup, more expensive. Not positioned for high-throughput agent sandboxing.

### Technology Decision Table

| Workload | Threat Model | Recommended Boundary |
|---|---|---|
| AI coding agent (multi-tenant SaaS) | Hostile (user code) | **MicroVM** (Firecracker) |
| AI coding agent (single-tenant) | Semi-trusted | **gVisor** or hardened container |
| RL rollouts (parallel, many resets) | Needs fast reset | **MicroVM** with snapshot |
| Code interpreter (stateless snippets) | Hostile | **gVisor** or runtime sandbox |
| Tool calling / plugins | Mixed | **Wasm / V8 isolates** |
| Shell access + package managers | Hostile | **MicroVM** (only option with full Linux) |
| Regulated industry (HIPAA, etc.) | Provable isolation | **Confidential computing** |

### Isolation Comparison Summary

| Technology | Isolation Level | Boundary | Startup |
|---|---|---|---|
| **Standard containers** | Weakest --- shared kernel | Linux namespaces/cgroups | ~10-50ms |
| **gVisor** | Strong --- syscall interception | User-space kernel | ~100ms |
| **Firecracker** | Strongest (practical) --- dedicated kernel | Hardware VM (KVM) | ~125ms |
| **Hyper-V** | Strongest (practical) --- bare-metal hypervisor | Type-1 hypervisor | Near-instant (pooled) |
| **Kata Containers** | Strongest (practical) --- full VM per container | Hardware VM (QEMU/FC) | ~200ms |
| **Confidential (SEV-SNP/SGX)** | Strongest + provably secure | Hardware TEE + encryption | Slower |
| **V8 Isolates** | Different model --- JS engine isolation | Language runtime | <5ms |
| **WebAssembly** | Different model --- capability-based | Runtime sandbox | Microseconds |

---

## Core Technical Primitives

These are the building blocks that every sandbox platform uses. Understanding them is essential for evaluating any option.

### Snapshots & Copy-on-Write Restore

This is the single most important optimization in the sandbox space. It's how platforms achieve sub-100ms startup times.

A snapshot captures VM state at a point in time:

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
│ - Open file handles  │                          │
├──────────────────────┼──────────────────────────┤
│ Size: 128 MB - 2 GB  │ Size: 50 MB - 20 GB     │
│ Restore: 15-50ms     │ Restore: 100-500ms       │
│ Full process state   │ Filesystem only          │
│ (exact clone)        │ (must re-boot + re-init) │
└──────────────────────┴──────────────────────────┘
```

#### How Firecracker Snapshots Work

Firecracker supports two snapshot types:

```
1. FULL SNAPSHOT
   - vmstate file: vCPU registers, device model state, interrupt controller
   - memory file: complete guest RAM dump (size = allocated guest memory)
   - disk files: separate block device images (can use backing file + overlay)

2. DIFF SNAPSHOT (incremental)
   Only stores pages that changed since the last snapshot.
   Dramatically smaller for repeat snapshots.

   Full:  ████████████████████████  512 MB
   Diff:  ██░░░░░░░░░░░░░░░░░░░░   ~30 MB (only dirty pages)
```

#### Copy-on-Write Restore (The Key Innovation)

Instead of copying the entire memory file into RAM:

```
Traditional restore:
  1. Read entire memory file from disk     <-- Slow (512 MB ~ 100ms on NVMe)
  2. Map into guest address space
  3. Resume vCPU
  Total: 100-500ms

Copy-on-Write restore:
  1. mmap() memory file as read-only       <-- Near-instant (page table setup only)
  2. Set up userfaultfd for write traps
  3. Resume vCPU
  4. On write: copy single 4KB page        <-- Happens lazily, on demand
  Total: 15-50ms

Memory access pattern after CoW restore:
  Page 0: [READ]  --> Served from mmap'd snapshot file (zero copy)
  Page 1: [WRITE] --> Trap --> Copy page --> Write to private copy
  Page 2: [READ]  --> Served from mmap'd snapshot file (zero copy)
  Page 3: [NEVER] --> Never loaded at all (saves I/O)

  Typical working set: only 10-30% of pages are ever touched
  = 70-90% of snapshot memory never copied from disk
```

#### On-Demand Paging with Prefetching

Research systems like [FaaSnap](http://faculty.washington.edu/wlloyd/courses/tcss591/papers/FaaSnap-FaaSMadeFastUsingSnapshot-basedVMs.pdf) go further:

1. Profile which pages are accessed during the first N invocations
2. Build a "loading set" of commonly needed pages
3. On restore: prefetch loading set pages in background while the guest starts immediately
4. Result: **3.5x faster end-to-end** than baseline snapshot restore

#### The Uniqueness Problem

When you clone a snapshot, all clones start with identical state --- same random seed, same UUID generator state, same TLS session keys. Clone 1 and Clone 2 generate the same "random" UUID.

[AWS's solution](https://arxiv.org/abs/2102.12892) ("Restoring Uniqueness in MicroVM Snapshots"):
1. Inject fresh entropy into `/dev/urandom` on restore
2. Re-seed all PRNGs via MMIO device
3. Force TLS renegotiation
4. Kernel patches: RDRAND instruction returns fresh values

#### Snapshot Implementations by Platform

```
Platform       | Snapshot Type       | Restore Time | Persistence
───────────────+─────────────────────+──────────────+──────────────
Blaxel         | Standby + resume    | ~25ms        | Configurable
HopX           | Memory snapshot     | 15-50ms (CoW)| Session-scoped
Daytona        | Optimized snapshots | ~90ms        | Indefinite
E2B            | Pause/resume + tpls | ~150ms       | Until explicit delete
Lambda         | SnapStart (CRaC)    | <200ms       | Managed by AWS
Modal          | Filesystem snap     | Sub-second   | Indefinite (30d dir, 7d mem)
Together       | Memory snapshot     | 500ms (P95)  | Session-scoped
```

### Boot Times & Cold Starts

#### What Determines Cold Start Time?

```
Cold Start Breakdown (microVM without snapshots):

  VMM Init        ██              ~1-5ms     (Firecracker starts, configures KVM)
  Kernel Boot     ████████████    ~80-125ms  (Linux kernel init, drivers, mm setup)
  Userspace Init  ████████        ~50-200ms  (/init, mount filesystems, services)
  App Start       ████████████    ~100ms-10s (Python: ~300ms, Java: ~2-5s, Node: ~200ms)
                  ├──────────────────────────┤
                  Total: 230ms - 10s+ (app-dependent)
```

With snapshot restore, you skip everything and land directly in a running state.

#### Cold Start Comparison

| Platform | P50 | P95 | Method |
|---|---|---|---|
| **HopX** (warm pool) | 12ms | 18ms | Pre-warmed pool |
| **Blaxel** (standby) | ~25ms | ~40ms | Warm standby |
| **Daytona** | ~90ms | ~150ms | Optimized containers |
| **Firecracker** (raw) | ~125ms | ~180ms | Cold boot |
| **AWS Lambda** (simple) | 100-200ms | -- | Python/Node, minimal deps |
| **E2B** | ~150ms | ~300ms | Firecracker templates |
| **Lambda + SnapStart** | <200ms | ~400ms | CRaC snapshots |
| **Bedrock AgentCore** | 300-800ms | -- | Per-session Firecracker |
| **Together Sandbox** | 500ms (snap) | 2.7s (clean) | CodeSandbox microVMs |
| **Cloud Run** | 0.5-2s | -- | Hardware virt + gVisor |
| **Modal** | Sub-second | ~1-2s | Container + snap |
| **Lambda** (real-world) | 1-5s | -- | With dependencies, VPC |
| **Cloudflare Containers** | 2-3s | ~5s | Container start |
| **AWS Fargate** | 15-40s | -- | New task from scratch |
| **Traditional VM** | 30-60s | ~90s | Full OS boot |

### Warm Pools

Warm pools eliminate cold starts by keeping pre-booted VMs ready for instant handoff:

```
                    Warm Pool Architecture

  ┌─────────────────────────────────────────────────┐
  │                  Pool Manager                    │
  │                                                  │
  │  Inputs:                                         │
  │    - Historical request rate                     │
  │    - Time-of-day patterns                        │
  │    - Current pool size                           │
  │    - Boot time for new VMs                       │
  │                                                  │
  │  Output: target_size = f(demand + buffer)        │
  │                                                  │
  │  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐      │
  │  │ VM1 │ │ VM2 │ │ VM3 │ │ VM4 │ │ VM5 │      │
  │  │READY│ │READY│ │READY│ │READY│ │READY│      │
  │  └─────┘ └─────┘ └─────┘ └─────┘ └─────┘      │
  └─────────────────────────────────────────────────┘
         │
    Request arrives
         │
         v
  ┌─────────────────────┐
  │  1. Claim VM (~1-2ms)│
  │  2. Configure net    │ ~3-5ms
  │  3. Return handle    │ ~2ms
  │  4. Replenish pool   │ (background)
  └─────────────────────┘

  Total handoff time: ~10-15ms
  Rule of thumb: pool_size = peak_concurrent_sessions * 1.2
```

GKE Agent Sandbox's pre-warmed pools deliver **sub-second startup latency, 90% improvement over cold starts**. Azure Dynamic Sessions uses session pools to achieve near-instant handoff.

### Volumes & Persistent Storage

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

**Block devices (virtio-blk):** A raw disk image on the host presented to the guest as `/dev/vda`. This is how Firecracker and Lambda work. Simple, fast, well-supported, but not shareable across VMs and fixed size at creation.

**virtio-fs:** A shared filesystem protocol over virtio, using FUSE in the guest. Host runs a `virtiofsd` daemon; guest mounts a host directory with near-native performance and full POSIX semantics. DAX (Direct Access) mode maps host pages directly into the guest. Available since Linux 5.4. Used by Kata Containers and QEMU-based platforms. **Not supported in Firecracker** (deliberately minimal device model).

**Network-attached storage:** How managed platforms handle volumes at scale.

| Platform | Volume Model | Persistence | Notes |
|---|---|---|---|
| **Modal** | Distributed FS, explicit commit/reload | Indefinite | Up to 2.5 GB/s, 500K files (v1), unlimited (v2 beta) |
| **E2B** | Ephemeral, persist via pause/resume | Until explicit delete | Can connect external S3 buckets |
| **Daytona** | Persistent, archivable to object storage | Indefinite + archive | Configurable |
| **Cloudflare** | Ephemeral disk + Durable Objects | Session + DO lifetime | 2-20 GB by instance |
| **Fly.io** | Persistent volumes, mountable across restarts | Until deleted | Configurable |

### Networking

Sandbox networking balances three concerns: **isolation** (prevent escape), **connectivity** (sandbox needs internet), and **accessibility** (users need to reach services inside).

#### Outbound (Sandbox --> Internet)

```
  ┌────────────────────┐
  │     Guest VM       │
  │  eth0: 172.16.0.2  │
  └────────┬───────────┘
           │ virtio-net
  ┌────────┴───────────┐
  │    TAP device      │  <-- Virtual network interface on host
  └────────┬───────────┘
  ┌────────┴───────────┐
  │   iptables NAT     │  <-- Source NAT (MASQUERADE) + egress allowlist
  └────────┬───────────┘
  ┌────────┴───────────┐
  │    Host NIC --> Internet
  └────────────────────┘

  Each microVM gets its own TAP device.
  At 100+ VMs/host, that means 100+ TAP interfaces.
```

#### Egress Controls by Platform

| Platform | Default | Controls Available |
|---|---|---|
| **Modal** | Open | `block_network=True`, `cidr_allowlist=["10.0.0.0/8"]` |
| **E2B** | Open, unrestricted | No built-in egress filtering |
| **OpenAI Code Interpreter** | No internet access | Fully air-gapped |
| **Cloudflare** | Through Workers gateway | Gateway policies |
| **Firecracker (DIY)** | You decide | iptables/nftables, anything you build |

#### Inbound (Internet --> Sandbox)

| Approach | How It Works | Used By |
|---|---|---|
| **Tunnels** | Proxy routes traffic to sandbox port via unique URL | Modal, Fly.io |
| **Preview URLs** | Sandbox gets unique subdomain, reverse proxy routes to VM | E2B, Daytona, CodeSandbox |
| **Connect tokens** | Auth token scoped to sandbox, passed in headers | Modal |
| **SSH tunnels** | Direct SSH access + port forwarding | E2B, traditional |

### Image & Template Systems

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

**E2B templates:** Write a `e2b.Dockerfile`, run `e2b template build`. Under the hood, the OCI image is converted to a rootfs that Firecracker can boot, then pre-snapshotted for fast restore. Docker familiarity, fast iteration.

**Modal SDK-defined images:** Pure Python --- `modal.Image.debian_slim().pip_install("numpy").apt_install("ffmpeg")`. Each method call creates a content-addressed layer (like Docker layers). No Dockerfile, no Docker daemon, no registry config. Images compose at runtime.

**Cloudflare:** Standard OCI containers from any registry. Managed by Durable Objects for stateful lifecycle.

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
```

**The fundamental tradeoff:**

```
                         Scale-to-Zero           Warm Pool
                         ═══════════════         ═══════════════
  Idle cost              $0                      $$$ (pool * rate)
  Cold start latency     200ms - 5s              10-50ms
  First-request UX       Poor (wait)             Excellent (instant)
  Cost at low traffic    Very low                High (wasted capacity)
  Cost at high traffic   Same as warm pool       Same as scale-to-zero
  Complexity             Low                     High (pool management)
```

**Most platforms use a hybrid approach:**

```
  Night/weekend --> Scale to zero ($0/hr)
  Business hours --> Warm pool ($$$/hr)
  Demand spikes --> Auto-scale up
```

**Platform-specific implementations:**

| Platform | Behavior |
|---|---|
| **Lambda** | Aggressive zero-out after ~5-15 min idle. SnapStart mitigates cold start. Provisioned concurrency for guaranteed warm (~$0.015/hr/instance). |
| **Cloudflare** | CPU charges stop when container sleeps. Memory/disk still billed on provisioned. Wake on HTTP request via Worker. |
| **Modal** | Functions scale to zero by default. Sandboxes run until explicitly terminated (no auto scale-to-zero). |
| **E2B** | Configurable TTL (max 1hr free, 24hr pro). Auto-terminate after TTL. Persist via pause/resume. |
| **Cloud Run** | Minimum instances setting to keep warm (costs money). Startup CPU boost available. |

---

## The Market: Purpose-Built Sandbox Platforms

### Platform Comparison Table

| Platform | Technology | Cold Start | SDKs | GPU | Self-Host | Pricing Model |
|---|---|---|---|---|---|---|
| **E2B** | Firecracker microVM | ~150ms | Python, JS/TS | No | Yes (GCP) | $0.000014/vCPU/s |
| **Daytona** | OCI containers | ~90ms | Python, TS | Yes | Yes | $0.000014/vCPU/s |
| **Modal** | gVisor containers | Sub-second | Python, JS/Go (beta) | Extensive | No | $0.00003942/core/s |
| **Blaxel** | Standby + resume | ~25ms | Python, TS | No | No | $0.0000115/GB/s |
| **Runloop** | Custom hypervisor | Not published | Python, TS | No | No | Not published |
| **Cloudflare Sandbox** | Containers | 2-3s | TypeScript | No | No | $0.000020/vCPU/s |
| **Vercel Sandbox** | Firecracker microVM | Fast | TypeScript | No | No | $0.128/CPU-hr |
| **Fly.io Machines** | Firecracker microVM | Sub-second | REST/CLI | No | No | ~$0.000002/CPU/s |
| **microsandbox** | libkrun microVM | <200ms | Python, TS | No | Yes (only) | Free (self-hosted) |
| **Beam** | Containers | 2-3s | Python, TS (beta) | Extensive | Yes | $0.190/core/hr |
| **Northflank** | Kata + gVisor | Seconds | API | No | Yes (BYOC) | Usage-based |

### Key Players Deep-Dive

**E2B** --- The AI sandbox incumbent. Raised $21M Series A. Open-source (Apache 2.0). Firecracker-based with ~150ms cold starts. Key customers: [Perplexity](https://e2b.dev) (shipped advanced data analysis in one week using E2B), [Manus](https://manus.im/blog/manus-sandbox) (virtual computers for agents, later acquired by Meta), Hugging Face (RL training pipelines), Groq, Lindy. Template system lets you pre-bake environments with Docker. 24-hour max session on Pro. 10,791 GitHub stars.

**Daytona** --- The growth rocket. Raised $24M Series A (Feb 2026, led by FirstMark Capital, with Datadog and Figma Ventures). Hit $1M forward ARR in under 3 months, doubled it 6 weeks later. 48.7k GitHub stars. Sub-90ms cold starts. Differentiator: **stateful sandboxes with Git-like branching** (fork, snapshot, restore). Key customers: LangChain, Turing, Writer, SambaNova. AGPL-3.0 license (requires open-sourcing modifications available over a network, pushes enterprises toward commercial licenses).

**Modal** --- The Python-first infrastructure play. Not purely a sandbox company --- also does inference, training, batch jobs. Strengths: massive autoscaling (10K+ concurrent units), GPU support, code-first image definition. Used by Lovable and Quora for millions of daily code executions. Official cloud evaluation partner for SWE-bench. No BYOC option.

**Runloop** --- The deepest technical pedigree. Founded by Jonathan Wall (former tech lead of Google File System, founding engineer at Google Wallet, founder of Inde acquired by Stripe). Custom bare-metal hypervisor with 2x faster vCPUs. Only provider with both arm64 and x86 support. Agent, Object, and Secret stores for reusing tools/files/keys. Official LangChain sandbox provider.

**Fly.io** --- The pragmatic middle ground. Firecracker microVMs via REST API without managing bare metal. Sub-second starts, per-second billing, global networking across 35 regions. Not specifically built for agent sandboxes, but Fly explicitly pitches: "Confidently deploy sketchy LLM-generated code."

**Together AI Code Sandbox** --- Uses CodeSandbox's microVM infrastructure under the hood. VM from snapshot: 500ms (P95). VM from scratch: under 2.7s (P95). Hot-swappable VM sizes (2-64 vCPUs, 1-128 GB RAM). Credit-based pricing.

**Manus** (acquired by Meta, late 2025) --- The most complete agent + sandbox integration. Each task gets a fully isolated cloud VM with networking, filesystem, browser, dev tools. Uses E2B sandboxes as its virtual computer infrastructure. Zero Trust security model. The name "Manus" comes from "Mens et Manus" (Mind and Hand) --- the model thinks, the sandbox acts.

---

## Cloud Provider Native Options

### AWS

| Service | Technology | Cold Start | Max Duration | Best For |
|---|---|---|---|---|
| **Bedrock AgentCore Runtime** | Firecracker microVM | 300-800ms | 15 min (awaiting input) | Agents in the Bedrock ecosystem |
| **Lambda** | Firecracker microVM | 100ms-5s | 15 min (hard limit) | Short code execution |
| **Lambda + SnapStart** | Firecracker + CRaC | <200ms | 15 min | Cold-start-sensitive workloads |
| **Fargate** | Firecracker microVM | 15-40s | Unlimited | Long-running containers |

**Bedrock AgentCore** is the purpose-built option. Each agent session gets a dedicated Firecracker microVM with deterministic teardown. Supports container-based (Dockerfile + ECR) or direct Python deployment (no Docker required, launched Nov 2025). Code Interpreter tool with pre-built runtimes, up to 100MB inline upload or 5GB via S3. Tied to the Bedrock ecosystem.

**Lambda** pricing: $0.20/1M requests + $0.0000166667/GB-second (x86). ARM/Graviton2 is ~20% cheaper. Free tier: 1M requests + 400,000 GB-seconds/month (always free). Provisioned Concurrency: ~$0.0000041667/GB-second to keep warm. SnapStart available for Java, Python, .NET --- takes a Firecracker snapshot of memory + disk after init, encrypts and caches it, restores from snapshot on cold start.

**Lambda limitations for sandboxing:** 15-minute max, 10GB max memory, 250MB deployment package, no persistent filesystem (only ephemeral /tmp, 10GB max), no inbound TCP. Fine for short code execution, unsuitable for long-running agent sandboxes.

**Fargate** pricing: per-second billing (1-min minimum). Linux/x86: $0.04048/vCPU/hour + $0.004445/GB/hour. ARM: ~20% cheaper. Spot: up to 70% discount (interruptible). Image caching via Seekable OCI (SOCI) helps reduce cold starts.

### GCP

| Service | Technology | Cold Start | Max Duration | Best For |
|---|---|---|---|---|
| **GKE Agent Sandbox** (Nov 2025) | gVisor + optional Kata | Sub-second (pre-warmed) | Unlimited | Agent workloads on Kubernetes |
| **Cloud Run** | Hardware virt + gVisor | 0.5-2s | 60 min (services), 24h (jobs) | Sandboxed containers, simplest path |
| **Cloud Functions (2nd gen)** | Same as Cloud Run | 0.5-2s | 60 min | Short functions |

**GKE Agent Sandbox** is the most opinionated GCP answer. Announced at KubeCon NA 2025 as a CNCF open-source project (not GKE-locked). Killer features: pre-warmed pools (**90% cold start reduction**), Pod Snapshots (GKE-exclusive, checkpoint/restore for running pods including GPU state), massive parallelism (thousands of sandboxes). Supports both gVisor and Kata Containers.

**Cloud Run** uses a two-layer sandbox: hardware-backed virtualization equivalent to individual VMs, plus gVisor user-space kernel for syscall interception. Google explicitly markets it for AI agent code execution: "When you deploy your code, Cloud Run confines the code within the sandboxing environment. This isolation lets you run untrusted code, such as code generated by a large language model." Pricing: $0.00002400/vCPU-second + $0.00000250/GiB-second + $0.40/million requests. Free tier: 2M requests/month.

**Nested virtualization:** GCP supports nested virtualization on Haswell+ CPUs. You can run Firecracker/KVM inside a GCE VM. No bare-metal instances like AWS --- nested virt is the path for DIY microVMs on GCP.

### Azure

| Service | Technology | Cold Start | Best For |
|---|---|---|---|
| **Container Apps Dynamic Sessions** | Hyper-V (Type-1) | Near-instant (pooled) | Agent code execution at scale |
| **Confidential ACI/AKS** | AMD SEV-SNP / Intel TDX | Slower | Regulated industries, data privacy |
| **Azure Functions** | Various | 100ms-seconds | Short functions (5-10 min) |

**Dynamic Sessions** is the standout. Hyper-V is a Type-1 (bare-metal) hypervisor --- stronger isolation than containers or gVisor. GA for Python code interpreter and custom containers (Nov 2024), JavaScript interpreter in preview. The proof point: **Microsoft Copilot uses this for code execution, serving 1B+ users**. Built-in LangChain and Semantic Kernel integrations. Session pools mitigate cold starts.

**Azure Confidential Computing:** DCsv2/DCsv3 (Intel SGX), DCasv5/DCadsv5 (AMD SEV-SNP). Full VM-level confidential computing for regulated industries. Not relevant for general agent sandboxing --- too heavy, too expensive.

### DIY on Cloud

```
Option 1: Firecracker on bare-metal EC2

  What you get:
    ~125ms boot, <5MB overhead, 150 VMs/sec, strongest isolation

  What you must build:
    1. Kernel + rootfs management (build/maintain Linux images)
    2. Networking (TAP devices, iptables/nftables, DHCP per VM)
    3. Storage (block devices or overlay filesystems per VM)
    4. API layer (REST/gRPC to create/destroy/manage VMs)
    5. Scheduling (bin packing: which host gets which VM)
    6. Monitoring (metrics, logging, health checks for 1000s of VMs)
    7. Snapshotting (snapshot/restore pipeline if you want fast restores)
    8. Security (seccomp filters, cgroup limits, jailer config)
    9. Image registry (manage and distribute rootfs images)

  Cost:
    i3.metal: ~$4.99/hr on-demand (~$3,593/month)
    72 vCPUs, 512 GB RAM, NVMe storage
    Can run 200+ concurrent microVMs per host

  Reality:
    "Firecracker is straightforward to use...the documentation and
    examples are pretty clear" -- Julia Evans
    The hard part is everything AROUND it. Companies like Fly.io,
    Vercel, and AWS spent years building these systems.

Option 2: Firecracker without KVM (SlicerVM / actuated approach)

  Alex Ellis (actuated.dev) built a way to run Firecracker on regular
  cloud VMs without /dev/kvm. Software emulation -- slower but works
  anywhere. Removes the bare-metal requirement.

  SlicerVM: "Boot Linux Kernel + systemd in less than 300ms" with
  optimized images. (Compared to: EC2 15-20s, EKS nodes 1-2 min.)

Option 3: gVisor on GKE/Kubernetes

  Add runtimeClassName: gvisor to pod spec. Works on GKE natively
  (enable GKE Sandbox on node pool) or self-managed K8s with gVisor
  installed as containerd runtime. GKE Autopilot makes this ~zero ops.

Option 4: Fly.io Machines API

  Firecracker microVMs via API. No bare metal management.
  Per-second billing (~$0.000002/CPU/s). Sub-second starts.
  Global networking. The pragmatic "DIY-adjacent" option.
```

---

## How the Industry Uses Sandboxes

### AI Labs: What Powers the Code Interpreters

| Company | Technology | Notable Detail |
|---|---|---|
| **OpenAI** (Code Interpreter) | gVisor on Kubernetes | [Reverse-engineered](https://ryan.govost.es/2025/openai-code-interpreter/): FastAPI server on port 8080, Kubernetes health checks, no internet access. Full Linux as user `sandbox` with numpy, pandas, matplotlib pre-installed. |
| **OpenAI** (Codex) | Per-task cloud sandbox | Each task gets isolated sandbox with cloned repo. Initially no internet; added June 2025. Powered by codex-1 (o3 variant trained with RL on coding tasks). |
| **Anthropic** (Claude Code) | OS-level primitives (`sandbox-exec` / `bubblewrap`) | [Open-sourced as `srt`](https://github.com/anthropic-experimental/sandbox-runtime). No container, no VM --- process-level restriction using native OS primitives + proxy-based network filtering. Reduced permission prompts by 84%. |
| **Google** (Gemini) | gVisor | [Researchers extracted internal source code](https://www.vulnu.com/p/researchers-hack-source-code-from-google-gemini) from the sandbox without escaping it. Available as API tool for code execution. NumPy, SciPy, pandas, matplotlib pre-installed. |
| **Microsoft** (Copilot) | Azure Dynamic Sessions (Hyper-V) | 1B+ users. Production-proven at extreme scale. |

The pattern: OpenAI and Google use gVisor. Anthropic went lightest possible (OS-level process restriction). Microsoft went heaviest (full Type-1 hypervisor). All approaches have had security incidents or researcher-demonstrated weaknesses.

### Coding Assistants: The Architecture Split

```
Local Execution (no sandbox)          Cloud Execution (sandboxed)
─────────────────────────────         ────────────────────────────
Cursor (shadow workspaces)            GitHub Copilot (Actions runners)
Windsurf (local + optional DevBox)    Devin (cloud VMs, 3 deployment tiers)
                                      Replit (CoW snapshots, most sophisticated)
```

**Cursor** does NOT use remote sandboxes for code execution. Agent Mode runs up to 8 AI agents simultaneously, all executing on the user's local machine. The "sandbox" is a **shadow workspace** --- a hidden, parallel instance of the dev environment where the AI iterates (sees lints, go-to-definitions, runs code) without the user seeing half-finished work. BugBot processes 2M monthly PR reviews. Scale: ~1 billion lines of accepted code/day. This local execution model is a ticking time bomb as agents become more autonomous.

**Windsurf (Codeium):** "Cascade" agent tracks file edits, terminal commands, clipboard to infer intent. Executes locally like Cursor. Optional integration with [Sealos DevBox](https://sealos.io/blog/windsurf-devbox) for cloud isolation ("unbreakable cloud environment" with snapshots).

**GitHub Copilot Coding Agent:** Fundamentally different. Runs in **ephemeral GitHub Actions runners** --- each task gets its own isolated environment. The agent never runs on the developer's machine. Standard GitHub Actions container isolation. Creates PRs for review. GA across Pro, Pro+, Business, Enterprise. Most "sandboxed by default" of any coding assistant.

**Replit Agent:** The most sophisticated approach. [Snapshot engine](https://blog.replit.com/inside-replits-snapshot-engine) uses Copy-on-Write at the block device level: agent forks the entire filesystem instantly, tries risky changes, reverts if they fail. Databases are snapshotable too. Dev/prod split is enforced --- agent cannot touch production. [Decision-Time Guidance](https://blog.replit.com/decision-time-guidance): the execution environment provides structured feedback (linter errors, test failures, build errors) to help the agent course-correct. [Hybrid security scanning](https://blog.replit.com/securing-ai-generated-code): deterministic static analysis + LLM reasoning (AI-only scans are nondeterministic --- identical vulnerabilities get different classifications based on minor syntactic changes).

**Devin (Cognition):** Fully autonomous AI software engineer with its own cloud VM per session. Three deployment tiers: Enterprise SaaS (multi-tenant), Dedicated SaaS with private networking, Customer Hosted VPC (AWS or Azure). SOC 2, Okta SSO, RBAC, VPN support. Nubank case study: refactored millions of lines of ETL monolith, 8x efficiency improvement, 20x cost savings.

### Open Source Agent Frameworks

| Framework | Default Sandbox | Approach |
|---|---|---|
| **AutoGen** (Microsoft) | Docker container | `DockerCommandLineCodeExecutor`, made default in v0.2.8 (Jan 2024). Breaking change rationale: "easy for new users to overlook code-execution risks." |
| **LangChain** | Multi-tier | Lightweight: Pyodide (Python in WebAssembly), no Docker needed. Heavy: [Sandboxes for DeepAgents](https://www.blog.langchain.com/execute-code-with-sandboxes-for-deepagents/) (Nov 2025) integrates Runloop, Daytona, and Modal. |
| **CrewAI** | Manual Docker setup | Less integrated. Focuses on agent orchestration, not execution infrastructure. |
| **smolagents** (HuggingFace) | Import allowlist | `additional_authorized_imports` approach. Simplest, most restrictive. |
| **OpenHands** (ex-OpenDevin) | Docker per agent | Each agent instance in its own container. [30x speed](https://openhands.dev/blog) by parallelizing evaluations. |

The trend: mandatory isolation, not optional. AutoGen making Docker default was deliberate. LangChain offering WebAssembly for lightweight and VM-backed providers for heavy is the emerging pattern.

### Benchmarking Infrastructure

**SWE-bench** standardized on Docker. Each of 12 Python repositories gets its own Docker image with correct dependencies, Python version, test config. Minimum: 120GB disk, 16GB+ RAM, 8+ CPUs.

[Epoch AI optimized these images 10x](https://epoch.ai/blog/swebench-docker) (670 GiB to 67 GiB for all 2,290 images), enabling full SWE-bench Verified in 62 minutes on a single GitHub Actions VM.

As of January 2025, SWE-bench supports cloud-based evaluations through **Modal** for parallel execution at scale. LangChain provides LangSmith integration for observability.

**HumanEval:** Simpler --- evaluates single-function code generation. Standard Python environments with basic sandboxing. Lower infrastructure requirements.

### RL Training

The core challenge: RL for coding agents requires running generated code thousands or millions of times during training. Each rollout needs isolation, speed, reproducibility, and massive parallelism.

**The key insight from [Collinear AI](https://blog.collinear.ai/p/rl-env-as-a-service):** RL training is fundamentally a **distributed systems problem**, not an ML problem. The ML is the easy part; managing thousands of parallel sandbox instances is the hard part. The concept of "Environment-as-a-Service" --- separating the data plane (sandbox) from the control plane (orchestration) --- mirrors the evolution of databases and compute. There is no dominant provider yet.

Key frameworks:

- **[verl](https://verl.readthedocs.io/en/latest/start/agentic_rl.html):** Open-source agentic RL training. Server-based async rollout with asyncio coroutines to avoid GPU idling. LangGraph integration for complex multi-turn interactions.
- **[Fireworks AI Eval Protocol](https://fireworks.ai/blog/eval-protocol-rl-on-your-agents):** Language/framework-agnostic RL fine-tuning. Traces agent behavior to generate feedback signals.
- **[NVIDIA NeMo Gym / NeMo RL](https://developer.nvidia.com/blog/how-to-train-scientific-agents-with-reinforcement-learning/):** REST-API-based training environments for scientific domains.

**Training safety risk:** A [February 2026 paper from Tsinghua/NUS](https://arxiv.org/html/2602.04196v1) showed models can covertly manipulate sandbox environments during RL training to inflate reward signals. Sandbox security during training is as important as during inference.

### Enterprise Deployments

The common enterprise architecture:

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

Enterprise security principles across deployments:

- **Zero trust:** All LLM-generated code is treated as potentially malicious
- **Network segmentation:** Sandboxes have no access to production networks by default
- **Secret management:** Credentials injected via secure vaults, never visible to the LLM
- **Audit logging:** Every sandbox action is logged for compliance
- **Human-in-the-loop:** Agent outputs go through PR review, not direct deployment

---

## Economics at Scale

### Per-Session Costs (1 vCPU, 512 MiB, 5-minute session)

```
Platform         | Per-Session Cost | Daily Cost (1M/day) | Monthly Cost
─────────────────+──────────────────+─────────────────────+─────────────
Novita (E2B alt) | ~$0.003          | ~$3,200             | ~$96,000
E2B              | ~$0.005          | ~$4,500             | ~$135,000
Daytona          | ~$0.005          | ~$4,500             | ~$135,000
Blaxel           | ~$0.005          | ~$4,500             | ~$135,000
Modal            | ~$0.006          | ~$6,000             | ~$180,000
Cloudflare       | ~$0.006          | ~$6,300             | ~$189,000
DIY (Firecracker)| ~$0.001-0.003    | ~$800-2,000         | ~$24K-90K
```

**How the per-session math works (E2B example):**

```
  vCPU:  1 vCPU  x 300s x $0.000014/vCPU/s  = $0.0042
  RAM:   0.5 GiB x 300s x $0.0000045/GiB/s  = $0.000675
  Total per session:                          ~$0.0049
```

**Billing granularity matters enormously:**

```
Time granularity comparison (1 vCPU, 30-second task):

  Per-second:   30s x $0.000014 = $0.00042
  Per-minute:   1m  x $0.00084  = $0.00084   (2x overpay)
  Per-hour:     1hr x $0.05     = $0.05       (120x overpay)

  At 1M sessions/day, that's $420/day vs $50,000/day.
  Per-second billing saves ~99% for short-lived workloads.
```

### Build vs. Buy

```
Sessions/day     Recommendation     Why
─────────────    ──────────────     ─────────────────────────
< 10K            Managed            Not worth the eng cost
10K - 100K       Managed            Still cheaper overall
100K - 500K      Evaluate           Depends on team size/capability
500K - 1M        Likely DIY         Savings justify engineering
> 1M             Definitely DIY     Managed costs explode linearly
```

```
Break-even Analysis (managed vs DIY):

  Cost
   ^
   |         DIY (fixed cost: hosts + engineering)
   |    ___________________________
   |   /
   |  /   Managed (linear, per-second)
   | /
   |/
   +-----------------------------------> Sessions/day
        ^
     Break-even: ~200K-500K sessions/day
```

**Full comparison:**

```
                    DIY (Firecracker on EC2)     Managed (E2B / Modal)
                    ========================     =====================
Infra cost          Low at scale                 Linear with usage
Engineering cost    HIGH (6-12 months to build)  Near zero
Cold start          You control it               150ms-3s (varies)
Security updates    Your responsibility          Provider handles it
Scaling             Manual or custom autoscaler  Automatic
Multi-tenancy       You build isolation          Built in
Observability       You build it                 Dashboards included
Compliance          Full control                 Depends on provider
Egress              AWS rates apply              Often bundled
Break-even          ~200K-500K sessions/day      Below that threshold
```

### Hidden Costs

These don't show up in headline pricing but can add 20-40% to base compute:

**1. Data Egress**

```
If each session produces 1 MB of output:
  1M sessions x 1 MB = 1 TB/day = 30 TB/month

  AWS:        30 TB x $0.09  = $2,700/month
  GCP:        30 TB x $0.11  = $3,300/month
  Cloudflare: 30 TB x $0.025 = $750/month (1 TB free)
  Modal:      Included (no separate egress charges)
```

**2. Warm Pool Overhead**

```
1,000 idle VMs (1 vCPU, 512 MiB each):

  On E2B:   1000 x $0.000014/s x 86400s = $1,210/day = $36K/mo
  On EC2:   ~12 m5.xlarge instances      = $1,659/mo

  Managed warm pools cost ~20x more than DIY
  because you're paying per-second for idle compute.
```

**3. Snapshot & Image Storage**

```
  Memory snapshot: ~128 MB-2 GB per snapshot (compressed)
  100K snapshots: 100K x 500 MB = 50 TB
  S3 storage: $0.023/GB/mo = $1,150/mo just for snapshots

  Building custom images (PyTorch, etc.):
    Build time: 5-15 minutes per build (billed on provider infra)
    Image size: 5-20 GB
```

**4. API Request Overhead**

```
Cloudflare specifically charges for Workers requests:
  $0.30/million requests
  At 1M sandbox creations + N API calls each:
  Estimate: 5M total requests = $1.50/day

Durable Objects:
  $0.15/million requests
  $12.50/million GB-seconds of duration
```

### Cost Optimization Strategies

**1. Snapshot Cloning (CoW):** Clone from snapshot instead of cold boot. Share 70-90% of base memory. Restore in 15-50ms vs 125ms.

**2. Scale-to-Zero at Night:** Full zero-out during dead periods, warm pool during business hours. Saves 30-50% vs 24/7 warm pools.

**3. Spot/Preemptible Instances (DIY):**

```
  AWS Spot pricing (i3en.metal):
    On-demand:  $10.85/hr
    Spot:       $3.25/hr (typical, ~70% savings)

  Strategy: On-demand for baseline warm pool, spot for overflow.
```

**4. Right-Size Warm Pools:** `pool_size = peak_concurrent_sessions * 1.2`. Predict demand with historical patterns. Too small = cold starts. Too large = wasted spend.

---

## Key Takeaways

1. **The sandbox stack has converged on three practical tiers.** Process-level restriction (Anthropic `srt`) for lightweight/local use, container/gVisor (OpenAI, Google, Modal) for the middle ground, and microVM (E2B, AWS, Fly.io) for maximum isolation. Most production deployments use the middle tier. Most *should* use microVMs.

2. **Firecracker won.** It powers AWS Lambda (trillions of invocations/month), E2B, Fly.io, Vercel Sandbox, and every serious DIY deployment. At <5MB overhead, 125ms boot, and hardware-level isolation, it hits the sweet spot better than anything else. gVisor is a strong runner-up when you can't get KVM access.

3. **Containers are not a security boundary for untrusted code.** If you're running agent-generated code in plain Docker, you're betting on the Linux kernel having no exploitable bugs in any reachable syscall path. That's a losing bet.

4. **Snapshots are the critical optimization.** Copy-on-Write snapshot restore separates 15ms cold starts from 5-second cold starts. It's what makes warm pools affordable and RL training feasible. If a platform doesn't support snapshots, it has a fundamental ceiling on performance.

5. **The three players to watch are E2B, Daytona, and Runloop.** E2B has the customer logos and Firecracker foundation. Daytona has the growth velocity and VC backing. Runloop has the deepest technical pedigree. All three are viable. Modal is a strong option if you're Python-centric and need GPU support.

6. **Cloud providers are catching up fast.** Azure Dynamic Sessions (1B+ users via Copilot), GKE Agent Sandbox (pre-warmed pools, Pod Snapshots), and Bedrock AgentCore (Firecracker) are all production-ready. If you're deep in one cloud, the native option is increasingly compelling.

7. **Local execution is a ticking time bomb.** Cursor and Windsurf run agent-generated code directly on the developer's machine. As agents become more autonomous, the risk becomes unacceptable.

8. **Security is an afterthought almost everywhere.** Researchers have found exploitable weaknesses in OpenAI's, Google's, and Anthropic's implementations. Only Replit's hybrid approach (deterministic analysis + LLM reasoning) shows genuine security maturity.

9. **The RL training use case is about to explode.** "Environment-as-a-Service" is an unsolved infrastructure problem. Whoever builds the "AWS Lambda of RL environments" captures a category.

---

## Predictions

1. **Sandbox infrastructure becomes a $1B+ market by 2028.** E2B, Daytona, and Runloop are early leaders, but AWS/GCP/Azure will ship integrated offerings that win at enterprise scale through VPC, IAM, and compliance integration.

2. **Firecracker beats gVisor for most agent use cases.** gVisor's syscall compatibility issues and performance overhead are friction. Firecracker's hardware isolation with sub-200ms cold starts is the better tradeoff. gVisor survives for lightweight/embedded use and environments without KVM access.

3. **Cursor adds remote sandbox execution within 18 months.** Running LLM-generated code on developer machines is a liability that scales with agent autonomy. They'll partner with or acquire a sandbox provider.

4. **"Environment-as-a-Service" for RL training becomes the next hot infra category.** Daytona's stateful, branchable sandboxes are closest to what RL needs. The data plane / control plane separation mirrors databases and compute.

5. **WebAssembly sandboxes grow for lightweight tool-calling use cases.** LangChain's Pyodide sandbox and StackBlitz's WebContainers prove that Wasm handles many code execution needs without container overhead.

6. **A major security incident involving an unsandboxed coding agent hits the mainstream press by end of 2026.** Autonomous agents + local execution + package installation + network access is too large a surface area. Something will go badly wrong, and it will accelerate adoption industry-wide.

---

## Sources

### Primary References

| Source | URL |
|---|---|
| Modal: Top AI Code Sandbox Products | https://modal.com/blog/top-code-agent-sandbox-products |
| Superagent: AI Code Sandbox Benchmark 2026 | https://www.superagent.sh/blog/ai-code-sandbox-benchmark-2026 |
| Luis Cardoso: A Field Guide to Sandboxes for AI | https://www.luiscardoso.dev/blog/sandboxes-for-ai |
| awesome-sandbox (curated list) | https://github.com/restyler/awesome-sandbox |

### Isolation Technologies

| Source | URL |
|---|---|
| Firecracker Snapshot Docs | https://github.com/firecracker-microvm/firecracker/blob/main/docs/snapshotting/snapshot-support.md |
| AWS: Restoring Uniqueness in MicroVM Snapshots | https://arxiv.org/abs/2102.12892 |
| FaaSnap Paper | http://faculty.washington.edu/wlloyd/courses/tcss591/papers/FaaSnap-FaaSMadeFastUsingSnapshot-basedVMs.pdf |
| gVisor Performance Guide | https://gvisor.dev/docs/architecture_guide/performance |
| virtio-fs Design | https://virtio-fs.gitlab.io/design.html |
| Northflank: Firecracker Explainer | https://northflank.com/blog/what-is-aws-firecracker |

### AI Labs & Coding Assistants

| Source | URL |
|---|---|
| Ryan Govostes: OpenAI Code Interpreter | https://ryan.govost.es/2025/openai-code-interpreter/ |
| OpenAI: Introducing Codex | https://openai.com/index/introducing-codex/ |
| OpenAI: Unrolling the Codex Agent Loop | https://openai.com/index/unrolling-the-codex-agent-loop/ |
| Anthropic: Claude Code Sandboxing | https://www.anthropic.com/engineering/claude-code-sandboxing |
| Anthropic sandbox-runtime GitHub | https://github.com/anthropic-experimental/sandbox-runtime |
| Google: Gemini 2.0 Code Execution | https://developers.googleblog.com/gemini-20-deep-dive-code-execution/ |
| Vulnu: Researchers Hack Gemini Sandbox | https://www.vulnu.com/p/researchers-hack-source-code-from-google-gemini |
| Cursor Shadow Workspaces | https://cursor.com/blog/shadow-workspace |
| ByteByteGo: How Cursor Serves Billions | https://blog.bytebytego.com/p/how-cursor-serves-billions-of-ai |
| GitHub Copilot Agent Docs | https://docs.github.com/en/copilot/customizing-copilot/customizing-the-development-environment-for-copilot-coding-agent |
| Replit Snapshot Engine | https://blog.replit.com/inside-replits-snapshot-engine |
| Replit: Securing AI-Generated Code | https://blog.replit.com/securing-ai-generated-code |
| Replit: Decision-Time Guidance | https://blog.replit.com/decision-time-guidance |
| Devin Enterprise Deployment | https://docs.devin.ai/enterprise/deployment/overview |

### Sandbox Platforms

| Source | URL |
|---|---|
| E2B | https://e2b.dev |
| Daytona | https://www.daytona.io |
| Runloop | https://runloop.ai |
| Modal | https://modal.com |
| Cloudflare Sandbox SDK | https://developers.cloudflare.com/sandbox/ |
| Fly.io Machines | https://fly.io/machines |
| Fly.io AI Pitch | https://fly.io/ai |
| Vercel Sandbox | https://vercel.com/docs/vercel-sandbox/concepts |
| Together Code Sandbox | https://docs.together.ai/docs/together-code-sandbox |
| Northflank Sandbox | https://northflank.com/blog/best-code-execution-sandbox-for-ai-agents |
| Manus Sandbox | https://manus.im/blog/manus-sandbox |

### Cloud Providers

| Source | URL |
|---|---|
| AWS Lambda Pricing | https://cloudchipr.com/blog/aws-lambda-pricing |
| AWS SnapStart | https://docs.aws.amazon.com/lambda/latest/dg/snapstart.html |
| AWS Fargate Pricing | https://aws.amazon.com/fargate/pricing/ |
| AWS Bedrock AgentCore | https://blog.radixia.ai/serverless-ai-agents-with-amazon-bedrock-agentcore/ |
| AWS Bedrock AgentCore Direct Deploy | https://aws.amazon.com/blogs/machine-learning/iterate-faster-with-amazon-bedrock-agentcore-runtime-direct-code-deployment/ |
| AWS Bedrock Enterprise Best Practices | https://aws.amazon.com/blogs/machine-learning/ai-agents-in-enterprises-best-practices-with-amazon-bedrock-agentcore/ |
| GCP Cloud Run Pricing | https://cloudchipr.com/blog/cloud-run-pricing |
| GCP Cloud Run Code Execution | https://docs.google.com/run/docs/code-execution |
| GKE Agent Sandbox | https://cloud.google.com/blog/products/containers-kubernetes/agentic-ai-on-kubernetes-and-gke |
| Azure Dynamic Sessions GA | https://techcommunity.microsoft.com/blog/appsonazureblog/azure-container-apps-dynamic-sessions-general-availability-and-more/4303561 |
| Azure Dynamic Sessions Docs | https://learn.microsoft.com/en-us/azure/container-apps/sessions |

### Economics & Benchmarking

| Source | URL |
|---|---|
| E2B Pricing | https://e2b.dev/pricing |
| Modal Pricing | https://modal.com/pricing |
| Cloudflare Containers Pricing | https://developers.cloudflare.com/containers/pricing/ |
| HopX 100ms Cold Starts | https://hopx.ai/blog/deep-dives/how-hopx-achieves-100ms-cold-starts/ |
| Novita vs E2B Pricing | https://blogs.novita.ai/novita-sandbox-e2b/ |
| SWE-bench Official | https://www.swebench.com/SWE-bench/ |
| Epoch AI: SWE-bench Docker | https://epoch.ai/blog/swebench-docker |
| Firecracker without KVM | https://blog.alexellis.io/how-to-run-firecracker-without-kvm-on-regular-cloud-vms/ |
| SlicerVM | https://slicervm.com/blog/microvms-sandboxes-in-300ms/ |

### RL Training & Research

| Source | URL |
|---|---|
| Collinear AI: RL Env-as-a-Service | https://blog.collinear.ai/p/rl-env-as-a-service |
| Fireworks AI: Eval Protocol | https://fireworks.ai/blog/eval-protocol-rl-on-your-agents |
| NVIDIA NeMo Gym | https://developer.nvidia.com/blog/how-to-train-scientific-agents-with-reinforcement-learning/ |
| verl Agentic RL Training | https://verl.readthedocs.io/en/latest/start/agentic_rl.html |
| EmergentMind: LLM-in-Sandbox-RL | https://www.emergentmind.com/topics/llm-in-sandbox-reinforcement-learning-llm-in-sandbox-rl |
| Training Safety Risks (Tsinghua/NUS) | https://arxiv.org/html/2602.04196v1 |
| AutoGen Docker Execution | https://microsoft.github.io/autogen/0.2/blog/2024/01/23/Code-execution-in-docker |
| LangChain: Sandboxes for DeepAgents | https://www.blog.langchain.com/execute-code-with-sandboxes-for-deepagents/ |
| Lambda Daily Cold Start Benchmark | https://maxday.github.io/lambda-perf/ |

### Additional

| Source | URL |
|---|---|
| Koyeb: Top Sandbox Platforms 2026 | https://www.koyeb.com/blog/top-sandbox-code-execution-platforms-for-ai-code-execution-2026 |
| BetterStack: 10 Best Sandbox Runners 2026 | https://betterstack.com/community/comparisons/best-sandbox-runners/ |
| ITNEXT: OpenAI Code Execution & gVisor | https://itnext.io/openais-code-execution-runtime-replicating-sandboxing-infrastructure-a2574e22dc3c |
| Docker Sandboxes for Enterprise AI | https://jpcaparas.medium.com/docker-sandboxes-make-ai-agents-safe-for-enterprise-adoption-ad686c12af23 |
| Self-Hosted Containers vs MicroVMs | https://medium.com/@odafe41/self-hosted-sandboxes-how-to-pick-between-containers-and-microvms-1fa4803b7bdf |
| Modal Volumes Docs | https://modal.com/docs/guide/volumes |
| Modal Sandbox Snapshots | https://modal.com/docs/guide/sandbox-snapshots |
| Modal Sandbox Networking | https://modal.com/docs/guide/sandbox-networking |
| E2B Template Docs | https://e2b.dev/docs/sandbox-template |
| Cloudflare Sandbox Architecture | https://developers.cloudflare.com/sandbox/concepts/architecture/ |
| Replit Regional Goval | https://blog.replit.com/regional-goval |
| SkyPilot Self-Hosted Sandbox | https://blog.skypilot.co/skypilot-llm-sandbox/ |
| Fork in the Road (OSDI 2025) | https://www.usenix.org/conference/osdi25/presentation/chai-xiaohu |
| PASS/SnapStart in PMEM (USENIX ATC 2024) | https://www.usenix.org/conference/atc24/presentation/pang |
