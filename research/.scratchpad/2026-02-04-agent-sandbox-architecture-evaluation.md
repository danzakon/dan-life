# Agent Sandbox Architecture Evaluation: Cloud Run vs MicroVMs for Secure Code Execution

**Date:** 2-4-26
**Category:** Research Report
**Status:** [x] Active

---

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [The Problem Statement](#the-problem-statement)
3. [Architecture Options](#architecture-options)
4. [Detailed Analysis](#detailed-analysis)
5. [Comparison Matrix](#comparison-matrix)
6. [File Access Patterns](#file-access-patterns)
7. [Key Tradeoffs](#key-tradeoffs)
8. [Recommendations](#recommendations)

---

## Executive Summary

The client's use case—agents reviewing PDFs, CSVs, and Excel files while executing code to explore datasets—sits at the intersection of two competing concerns: **simplicity** and **security isolation**. After researching the current landscape, my assessment is:

**Cloud Run is likely sufficient for this use case, but with important caveats.**

Cloud Run provides a two-layer sandbox (hardware-backed x86 virtualization + software kernel layer) that Google explicitly markets for AI agent code execution. This isolation is stronger than standard containers but weaker than dedicated microVMs. For a multi-tenant SaaS where users upload files and agents write/execute code, the critical question is not "can code escape?" but "can user A's code access user B's data?"

The real security boundary isn't the execution environment—it's the **file access pattern**. Whether you use Cloud Run, Modal, or Firecracker, you still need per-tenant isolation of uploaded files. MicroVMs don't magically solve this; they just provide a stronger blast radius if something goes wrong.

**Bottom line:** Start with Cloud Run + per-tenant GCS buckets. Graduate to microVMs only if you have regulatory requirements, extremely adversarial threat models, or the latency budget allows for cold starts.

---

## The Problem Statement

The client described a specific workflow:

```
┌─────────────────────────────────────────────────────────────────┐
│                     LINE REVIEW WORKFLOW                        │
├─────────────────────────────────────────────────────────────────┤
│  Input: ~12 files (PDF, CSV, XLSX)                              │
│  Agent: Reads files, writes Python code, executes analysis      │
│  Output: Review deck with findings                              │
│  Mode: Background/non-interactive                               │
└─────────────────────────────────────────────────────────────────┘
```

**Security concerns explicitly stated:**
1. Arbitrary code execution across shared filesystem via user uploads
2. Prompt injection leading to cross-tenant data access
3. Need for "maximal capabilities" in main agent (not just task agents)

**Constraints mentioned:**
- Preference for mounted volumes over API-based file hydration (latency concerns)
- Claude Code optimized for filesystem access
- Want to avoid excessive management overhead

---

## Architecture Options

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        ISOLATION SPECTRUM                                   │
│                                                                             │
│  Weaker ◄─────────────────────────────────────────────────────────► Stronger │
│                                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │ Shared   │  │ Container│  │ Cloud Run│  │ gVisor/  │  │ MicroVM  │      │
│  │ Process  │  │ (Docker) │  │ Sandbox  │  │ Kata     │  │ (Firecracker) │ │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘      │
│       ↓             ↓             ↓             ↓             ↓            │
│  No isolation  Namespace    2-layer VM    Syscall      Full VM             │
│               isolation     + kernel      interception  isolation          │
│                             sandbox                                         │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Option A: Cloud Run Services/Jobs (Containerized)

**What it is:** Standard Cloud Run deployment where each agent invocation runs in an isolated container with Google's two-layer sandbox.

```
┌─────────────────────────────────────────────────────────────────┐
│                    CLOUD RUN ARCHITECTURE                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   Request ──► Cloud Run Service ──► Container Instance          │
│                     │                      │                    │
│                     │              ┌───────┴───────┐            │
│                     │              │   2-Layer     │            │
│                     │              │   Sandbox     │            │
│                     │              │ ┌───────────┐ │            │
│                     │              │ │ x86 Virt  │ │            │
│                     │              │ │ (hardware)│ │            │
│                     │              │ └───────────┘ │            │
│                     │              │ ┌───────────┐ │            │
│                     │              │ │ Kernel    │ │            │
│                     │              │ │ (software)│ │            │
│                     │              │ └───────────┘ │            │
│                     │              └───────────────┘            │
│                     │                                           │
│              GCS FUSE Mount ◄── Per-tenant bucket               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Security model:**
- Each container instance gets hardware-backed isolation equivalent to individual VMs
- Software kernel layer provides additional syscall filtering
- Containers from different customers never share the same sandbox
- [Google explicitly documents](https://docs.cloud.google.com/run/docs/securing/security) this for AI agent code execution

### Option B: Cloud Run Jobs (Background Processing)

**What it is:** Same as above, but using Cloud Run Jobs instead of Services for background/async workloads.

**Key difference from Services:**
- Jobs run to completion then exit (no long-lived instances)
- Can run up to 10,000 parallel tasks per job
- Better for batch processing like "review these 12 files"
- Same security isolation as Services

```
┌─────────────────────────────────────────────────────────────────┐
│              CLOUD RUN JOBS FOR BACKGROUND TASKS                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   Trigger ──► Cloud Run Job ──► Task 1 (container)              │
│                    │                                            │
│                    ├──────────► Task 2 (container)              │
│                    │                                            │
│                    └──────────► Task N (container)              │
│                                                                 │
│   Each task: isolated, ephemeral, billed only during execution  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Advantages for this use case:**
- Natural fit for "review this deck" workflow
- Clean execution lifecycle (start → process → exit)
- No idle capacity costs
- Client mentioned this suits background/non-interactive processing

### Option C: MicroVMs (Firecracker/Modal/E2B)

**What it is:** True VM-level isolation where each agent session gets its own minimal VM with dedicated kernel.

```
┌─────────────────────────────────────────────────────────────────┐
│                   MICROVM ARCHITECTURE                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   Request ──► Orchestrator ──► Firecracker MicroVM              │
│                    │               │                            │
│                    │         ┌─────┴─────┐                      │
│                    │         │  Guest OS │                      │
│                    │         │  (kernel) │                      │
│                    │         ├───────────┤                      │
│                    │         │ Agent SDK │                      │
│                    │         │ + Code    │                      │
│                    │         ├───────────┤                      │
│                    │         │  Mounted  │                      │
│                    │         │   Files   │                      │
│                    │         └───────────┘                      │
│                    │                                            │
│   ~150ms cold start (E2B) to ~300ms (Modal)                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Key providers:**
| Provider | Isolation | Cold Start | Max Runtime | Notes |
|----------|-----------|------------|-------------|-------|
| **Modal** | gVisor | Sub-second | 24 hours | Python-centric, great autoscaling |
| **E2B** | Firecracker | ~150ms | 24 hours (Pro) | AI-first SDK, purpose-built for agents |
| **Northflank** | Kata/gVisor | ~200ms | Unlimited | BYOC, production-grade |
| **Daytona** | Firecracker | ~90ms | Unlimited | Fastest cold starts |

### Option D: Hybrid Approaches

**D1: Per-tenant buckets with IAM impersonation**
```
┌─────────────────────────────────────────────────────────────────┐
│              IAM IMPERSONATION PATTERN                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   Agent (Tenant A) ──► Service Account A ──► Bucket A           │
│                              │                                  │
│                        IAM Policy:                              │
│                        - Can only access Bucket A               │
│                        - Scoped permissions                     │
│                                                                 │
│   Agent (Tenant B) ──► Service Account B ──► Bucket B           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**D2: API hydration (files fetched on demand)**
```
┌─────────────────────────────────────────────────────────────────┐
│              API HYDRATION PATTERN                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   Agent ──► File Request ──► API ──► Auth Check ──► GCS         │
│                                          │                      │
│                                    Verify tenant                │
│                                    owns file                    │
│                                          │                      │
│                                    Return bytes                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```
- Client expressed concern about latency
- More explicit access control
- Breaks filesystem abstraction Claude Code expects

**D3: Custom tool reads (MCP-style)**
```
┌─────────────────────────────────────────────────────────────────┐
│              CUSTOM MCP FILE TOOLS                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   Claude Agent ──► read_file(path) ──► MCP Server               │
│                                             │                   │
│                                       Validate path             │
│                                       Check tenant              │
│                                       Return content            │
│                                                                 │
│   Pros: Fine-grained control, audit logging                     │
│   Cons: Slower, breaks CC filesystem optimization               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Detailed Analysis

### Cloud Run: The Pragmatic Choice

**What Google says:**
> "Cloud Run isolates all instances by using a two-layer sandbox that consists of a hardware-backed layer equivalent to individual VMs (x86 virtualization) and a software kernel layer."
> — [Cloud Run Security Design Overview](https://docs.cloud.google.com/run/docs/securing/security)

**What this means in practice:**
- Container escapes are extremely difficult (not just namespace breakouts)
- Even if code escapes the container, it's still trapped in the VM sandbox
- Google runs Gmail and YouTube on the same underlying infrastructure (Borg)

**The real question:** Is this "enough" isolation?

For most multi-tenant SaaS applications, **yes**. The attack surface isn't typically "escape the container and access other containers." It's:
1. Accessing files you shouldn't have access to (data isolation)
2. Making network calls you shouldn't make (egress control)
3. Consuming excessive resources (resource limits)

Cloud Run addresses all three:
- File isolation via per-tenant GCS buckets + FUSE mounts
- Network policies and VPC configuration
- CPU/memory/timeout limits per instance

**When Cloud Run isn't enough:**
- Regulatory requirements demanding VM-level isolation (some financial/healthcare)
- Nation-state adversary threat models
- Zero-trust environments where Google's sandbox is in the threat model
- Need for custom kernels or kernel-level capabilities

### MicroVMs: The Maximum Security Choice

**Why Firecracker exists:**
AWS built Firecracker specifically because containers weren't isolated enough for Lambda/Fargate multi-tenancy. Key properties:
- Each microVM has its own Linux kernel
- Memory isolation enforced by hypervisor
- ~125ms boot time for minimal VMs
- ~5MB memory overhead per VM

**The isolation difference:**

```
┌─────────────────────────────────────────────────────────────────┐
│           CONTAINER vs MICROVM ATTACK SURFACE                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   CONTAINER (Cloud Run style):                                  │
│   ┌─────────────────────────────────────────┐                   │
│   │ Container A    Container B              │ ← Shared kernel   │
│   │ (tenant A)     (tenant B)               │   (sandboxed)     │
│   │      │              │                   │                   │
│   │      └──────┬───────┘                   │                   │
│   │             ↓                           │                   │
│   │      Kernel syscall filtering           │                   │
│   │             ↓                           │                   │
│   │      Hardware virtualization            │                   │
│   └─────────────────────────────────────────┘                   │
│                                                                 │
│   MICROVM (Firecracker style):                                  │
│   ┌───────────────┐    ┌───────────────┐                        │
│   │ MicroVM A     │    │ MicroVM B     │   ← Separate kernels   │
│   │ (tenant A)    │    │ (tenant B)    │                        │
│   │ ┌───────────┐ │    │ ┌───────────┐ │                        │
│   │ │ Own kernel│ │    │ │ Own kernel│ │                        │
│   │ └───────────┘ │    │ └───────────┘ │                        │
│   └───────┬───────┘    └───────┬───────┘                        │
│           └────────┬──────────┘                                 │
│                    ↓                                            │
│             Hypervisor (KVM)                                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Key insight:** In the microVM model, a kernel exploit in tenant A's VM cannot affect tenant B because they have separate kernels. In the container model, a kernel exploit (even with sandboxing) theoretically has a larger blast radius.

**However:** Kernel exploits against modern sandboxed environments are rare and valuable. They're not the common attack vector for AI agent abuse.

### What Actually Goes Wrong

Based on [NVIDIA's security research](https://developer.nvidia.com/blog/how-code-execution-drives-key-risks-in-agentic-ai-systems/) and [production incident patterns](https://developer.nvidia.com/blog/practical-security-guidance-for-sandboxing-agentic-workflows-and-managing-execution-risk/), the real threats are:

| Threat | Likelihood | Mitigation |
|--------|------------|------------|
| Prompt injection leading to data exfil | **High** | Per-tenant file isolation |
| Agent reads wrong user's files | **High** | IAM + bucket separation |
| Resource exhaustion (fork bombs) | Medium | CPU/memory limits |
| Network-based attacks (SSRF) | Medium | Egress filtering |
| Container escape to host | Low | Sandboxing (Cloud Run sufficient) |
| Kernel exploit to escape VM | Very Low | MicroVMs (overkill for most) |

**The uncomfortable truth:** Most agent security failures aren't exotic escapes—they're misconfigurations, over-permissioned access, and inadequate data isolation.

---

## Comparison Matrix

| Dimension | Cloud Run Service | Cloud Run Job | Modal | E2B | Self-hosted Firecracker |
|-----------|------------------|---------------|-------|-----|------------------------|
| **Isolation Level** | 2-layer sandbox | 2-layer sandbox | gVisor | Firecracker microVM | Firecracker microVM |
| **Cold Start** | 0-2s | 0-2s | Sub-second | ~150ms | ~125ms |
| **Max Runtime** | 60 min (configurable) | 24 hours | 24 hours | 24 hours | Unlimited |
| **File Access** | GCS FUSE mount | GCS FUSE mount | Volume mounts | Filesystem API | Direct mount |
| **Startup Complexity** | Low | Low | Low | Low | High |
| **Ops Overhead** | Minimal | Minimal | Low | Low | High |
| **Cost Model** | Per-request + compute | Per-execution | Per-second | Per-GB-hour | Infra cost |
| **Multi-tenant Isolation** | Per-instance | Per-task | Per-sandbox | Per-sandbox | Per-VM |
| **GCP Integration** | Native | Native | None | None | Manual |
| **Filesystem Semantics** | POSIX (via FUSE) | POSIX (via FUSE) | POSIX | POSIX | POSIX |

### Latency Profile

```
┌─────────────────────────────────────────────────────────────────┐
│                    COLD START COMPARISON                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   Daytona        ████ 90ms                                      │
│   E2B            ██████ 150ms                                   │
│   Firecracker    ██████ 125ms                                   │
│   Modal          ████████████ 300ms                             │
│   Cloud Run      ████████████████████████ 1-2s (with deps)      │
│   Full VM        ████████████████████████████████████ 10-30s    │
│                                                                 │
│   Note: Cloud Run cold start depends heavily on image size      │
│   and dependencies. Optimized images can hit sub-second.        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## File Access Patterns

This is where the rubber meets the road. The client mentioned:
> "I much prefer the simpler abstraction of mounted volumes"
> "CC is optimized for filesystems and I think works most efficiently controlling all artifacts in that layer"

### Pattern 1: Per-Tenant GCS Bucket + FUSE Mount

```
┌─────────────────────────────────────────────────────────────────┐
│              PER-TENANT BUCKET ARCHITECTURE                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   Upload Flow:                                                  │
│   User A uploads file.pdf ──► gs://tenant-a-uploads/file.pdf    │
│   User B uploads data.csv ──► gs://tenant-b-uploads/data.csv    │
│                                                                 │
│   Agent Execution:                                              │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │ Cloud Run Instance (Tenant A)                           │   │
│   │                                                         │   │
│   │   /workspace/ ◄── GCS FUSE ◄── gs://tenant-a-uploads/   │   │
│   │        │                                                │   │
│   │   Agent sees: /workspace/file.pdf                       │   │
│   │   Agent CANNOT see: gs://tenant-b-uploads/*             │   │
│   │                                                         │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│   Isolation enforced by: GCS IAM + service account binding      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Implementation:**
1. Each tenant gets a dedicated GCS bucket (or prefix with IAM)
2. Agent runtime configured with service account scoped to that bucket
3. GCS FUSE mounts the bucket at `/workspace` or similar
4. Claude Code sees a normal filesystem

**Pros:**
- Clean filesystem abstraction
- Strong isolation via IAM
- Native GCP integration
- Audit logging built-in

**Cons:**
- FUSE has latency overhead vs local disk
- Requires per-tenant service account management
- Bucket proliferation at scale

### Pattern 2: Ephemeral Local Filesystem + Pre-hydration

```
┌─────────────────────────────────────────────────────────────────┐
│              PRE-HYDRATION PATTERN                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   1. Job starts                                                 │
│   2. Download tenant files from GCS to /tmp/workspace/          │
│   3. Agent executes with local filesystem                       │
│   4. Upload results back to GCS                                 │
│   5. Container destroyed (files gone)                           │
│                                                                 │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │ Cloud Run Job                                           │   │
│   │                                                         │   │
│   │   gs://tenant-a-uploads/ ──► /tmp/workspace/ (local)    │   │
│   │                                    │                    │   │
│   │                              Agent executes             │   │
│   │                                    │                    │   │
│   │   /tmp/results/ ──────────► gs://tenant-a-outputs/      │   │
│   │                                                         │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Pros:**
- Fastest filesystem access (local SSD)
- Simple mental model
- No FUSE complexity
- Ephemeral = auto-cleanup

**Cons:**
- Download time at job start
- Storage limits (Cloud Run disk)
- Large files = significant startup cost

### Pattern 3: Hybrid (FUSE for read, local for write)

```
┌─────────────────────────────────────────────────────────────────┐
│              HYBRID READ/WRITE PATTERN                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   /input/  ◄── GCS FUSE (read-only) ◄── tenant uploads          │
│   /output/ ◄── Local disk ──► Synced to GCS on completion       │
│   /scratch/ ◄── Local disk (ephemeral, for code execution)      │
│                                                                 │
│   Benefits:                                                     │
│   - Input files streamed on demand (no bulk download)           │
│   - Output writes are fast (local)                              │
│   - Scratch space for agent code execution                      │
│   - Clean separation of concerns                                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Key Tradeoffs

### Tradeoff 1: Simplicity vs Maximum Security

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   Cloud Run                              MicroVM                │
│   ┌────────────────────┐                 ┌────────────────────┐ │
│   │ ✓ GCP-native       │                 │ ✓ Strongest        │ │
│   │ ✓ Simple deploy    │                 │   isolation        │ │
│   │ ✓ Low ops burden   │                 │ ✓ Custom kernels   │ │
│   │ ✓ Built-in scaling │                 │ ✓ Full VM features │ │
│   │                    │                 │                    │ │
│   │ ✗ Less isolation   │                 │ ✗ More infra work  │ │
│   │   than microVM     │                 │ ✗ No GCP native    │ │
│   │                    │                 │ ✗ Higher latency   │ │
│   └────────────────────┘                 └────────────────────┘ │
│                                                                 │
│   Choose based on: threat model, compliance needs, team capacity│
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Tradeoff 2: Latency vs Isolation

For **interactive agents** (user waiting for response):
- Cold start matters significantly
- Sub-second response expected
- MicroVM cold starts (90-300ms) acceptable
- Cloud Run cold starts (1-2s) may be noticeable

For **background agents** (client's line review use case):
- Cold start less critical (user not waiting in real-time)
- Job duration dominates (minutes to hours)
- Cloud Run Jobs well-suited
- MicroVM overhead amortized over job duration

### Tradeoff 3: Filesystem Abstraction vs Security Control

| Approach | Filesystem Feel | Security Granularity | Latency |
|----------|-----------------|---------------------|---------|
| GCS FUSE mount | Excellent | Bucket-level IAM | Medium |
| Pre-hydration | Excellent | Per-job | High startup |
| API hydration | Poor | Per-file | Per-access |
| Custom MCP tools | Poor | Per-operation | Per-access |

The client correctly identified that Claude Code is optimized for filesystem access. Breaking that abstraction (API hydration, custom tools) has real costs:
- More agent tokens spent on tool calls
- Slower iteration loops
- Claude Code's internal optimizations don't apply

### Tradeoff 4: Main Agent vs Task Agent Parity

Client stated:
> "I'd prefer that the main agent is just as capable as task level agents"

This is achievable with both approaches:

**Cloud Run:** Run both orchestrator and task agents in Cloud Run. Same isolation model throughout.

**MicroVM:** Run everything in microVMs. Higher cost but consistent security posture.

**Hybrid risk:** If orchestrator runs in Cloud Run but tasks run in microVMs, the orchestrator becomes the weakest link. An attacker might target the orchestrator to escape before spawning tasks.

---

## Recommendations

### For This Specific Use Case

Given:
- Background processing (non-interactive)
- ~12 files per review
- Code execution required
- Multi-tenant SaaS
- Preference for simplicity

**Recommended architecture:**

```
┌─────────────────────────────────────────────────────────────────┐
│                 RECOMMENDED ARCHITECTURE                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   API Layer (Cloud Run Service)                                 │
│        │                                                        │
│        ▼                                                        │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │ Review Orchestrator (Cloud Run Service)                 │   │
│   │   - Receives review request                             │   │
│   │   - Creates Cloud Run Job with tenant-scoped config     │   │
│   │   - Returns job ID for status polling                   │   │
│   └─────────────────────────────────────────────────────────┘   │
│        │                                                        │
│        ▼                                                        │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │ Review Agent (Cloud Run Job)                            │   │
│   │   - Per-tenant service account                          │   │
│   │   - GCS FUSE mount to tenant bucket                     │   │
│   │   - Claude Agent SDK                                    │   │
│   │   - Ephemeral execution                                 │   │
│   └─────────────────────────────────────────────────────────┘   │
│        │                                                        │
│        ▼                                                        │
│   Results written to gs://tenant-X-outputs/                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Why this works:**
1. **Isolation via Cloud Run's 2-layer sandbox** — sufficient for most threat models
2. **Data isolation via per-tenant GCS + IAM** — the actual security boundary
3. **Filesystem abstraction preserved** — GCS FUSE gives Claude Code what it needs
4. **Background processing via Jobs** — natural fit, clean lifecycle
5. **Simple operations** — GCP-native, no external dependencies

### Security Hardening Layers

If additional hardening needed, add in this order:

| Priority | Measure | Complexity | Impact |
|----------|---------|------------|--------|
| 1 | Per-tenant service accounts | Low | High |
| 2 | Network egress filtering | Low | Medium |
| 3 | Hooks for command validation | Medium | Medium |
| 4 | File content scanning pre-mount | Medium | Medium |
| 5 | Migrate to microVM (Modal/E2B) | High | High |

### When to Choose MicroVMs

Upgrade to microVM architecture if:
- Regulatory requirement for VM-level isolation
- Handling extremely sensitive data (healthcare PHI, financial PII)
- Adversarial threat model (nation-state, targeted attacks)
- Compliance audit requires it
- Team has capacity to manage additional infrastructure

### The Non-Recommendation

**Don't do:** Run a single Cloud Run instance with a shared filesystem where tenant isolation is enforced only by code-level checks.

This is the failure mode the client correctly identified. Prompt injection could trivially bypass code-level access controls if the filesystem is shared. The architecture must enforce isolation at the infrastructure layer, not the application layer.

---

## Final Thoughts

The client's instinct—that the main agent should be "just as capable as task level agents"—is correct. But capability parity doesn't require microVM parity. It requires:

1. **Same filesystem semantics** (solved by FUSE)
2. **Same tool availability** (controlled by agent configuration)
3. **Same isolation guarantees** (solved by per-tenant buckets + IAM)

The microVM question is orthogonal to capability. It's about blast radius if isolation fails. For most multi-tenant SaaS applications, Cloud Run's blast radius is small enough, and the operational simplicity is worth it.

**Start with Cloud Run. Measure. Harden as needed. Migrate to microVMs only if you hit a wall that Cloud Run can't solve.**

---

## Sources

- [Cloud Run Security Design Overview](https://docs.cloud.google.com/run/docs/securing/security)
- [Cloud Run Code Execution for AI Agents](https://docs.cloud.google.com/run/docs/code-execution)
- [Host AI Agents on Cloud Run](https://docs.cloud.google.com/run/docs/ai-agents)
- [GKE Agent Sandbox Documentation](https://docs.cloud.google.com/kubernetes-engine/docs/how-to/agent-sandbox)
- [Anthropic Claude Code Sandboxing](https://www.anthropic.com/engineering/claude-code-sandboxing)
- [Docker Sandboxes for Claude Code](https://www.docker.com/blog/docker-sandboxes-run-claude-code-and-other-coding-agents-unsupervised-but-safely/)
- [Modal Coding Agents Solution](https://modal.com/solutions/coding-agents)
- [Northflank MicroVM Sandboxing](https://northflank.com/blog/secure-runtime-for-codegen-tools-microvms-sandboxing-and-execution-at-scale)
- [E2B vs Modal Benchmark 2026](https://www.superagent.sh/blog/ai-code-sandbox-benchmark-2026)
- [Firecracker MicroVM GitHub](https://github.com/firecracker-microvm/firecracker)
- [NVIDIA AI Agent Security Guidance](https://developer.nvidia.com/blog/practical-security-guidance-for-sandboxing-agentic-workflows-and-managing-execution-risk/)
- [AWS Firecracker Announcement](https://aws.amazon.com/blogs/opensource/firecracker-open-source-secure-fast-microvm-serverless/)
- [Cloud Storage FUSE for AI/ML](https://docs.cloud.google.com/architecture/optimize-ai-ml-workloads-cloud-storage-fuse)
- [Multi-Tenant Agent Isolation Patterns](https://blaxel.ai/blog/tenant-isolation)
