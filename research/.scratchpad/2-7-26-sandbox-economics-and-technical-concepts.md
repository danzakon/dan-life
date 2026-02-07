# Code Execution Sandboxes: Economics at Scale & Core Technical Concepts

**Date:** 2-7-26
**Status:** Research complete

---

## TOPIC 1: The Economics of Code Execution Sandboxes at Scale

### What Does 1M Sandbox Sessions/Day Actually Cost?

The answer depends heavily on session duration, resource allocation, and platform choice. Here's a model using real pricing data.

**Assumptions for modeling:**
- 1 vCPU, 512 MiB RAM per session
- Average session duration: 5 minutes (300 seconds)
- 1,000,000 sessions/day

#### Per-Platform Cost Estimates (1M sessions/day)

```
Platform         | Per-Session Cost | Daily Cost     | Monthly Cost
-----------------+------------------+----------------+-------------
E2B              | ~$0.0045         | ~$4,500        | ~$135,000
Daytona          | ~$0.0045         | ~$4,500        | ~$135,000
Blaxel           | ~$0.0045         | ~$4,500        | ~$135,000
Cloudflare       | ~$0.0063         | ~$6,300        | ~$189,000
Modal            | ~$0.0060         | ~$6,000        | ~$180,000
Novita (E2B alt) | ~$0.0032         | ~$3,200        | ~$96,000
DIY (Firecracker)| ~$0.0008-0.002   | ~$800-2,000    | ~$24K-60K
```

**How the per-session math works:**

```
E2B:
  vCPU:  1 vCPU  x 300s x $0.000014/vCPU/s  = $0.0042
  RAM:   0.5 GiB x 300s x $0.0000045/GiB/s  = $0.000675
  Total per session:                          ~$0.0049

Modal (note: prices per physical core = 2 vCPU):
  CPU:   0.5 core x 300s x $0.0000131/core/s = $0.001965
  RAM:   0.5 GiB  x 300s x $0.00000222/GiB/s = $0.000333
  Total per session:                          ~$0.0023
  + platform fee ($250/mo for Team plan)

Cloudflare Containers:
  vCPU:  1 vCPU  x 300s x $0.000020/vCPU/s   = $0.006
  RAM:   0.25 GiB x 300s x $0.0000025/GiB/s  = $0.000188
  Total per session:                           ~$0.006
  + $5/mo base plan

DIY Firecracker on EC2 bare metal:
  i3en.metal ($10.85/hr) = 96 vCPU, 768 GiB RAM
  Can pack ~90 concurrent microVMs (1 vCPU each, ~5 MiB VMM overhead)
  At 5-min sessions: 90 * (60/5) * 24 = 25,920 sessions/day/host
  Need ~39 hosts for 1M sessions/day
  Cost: 39 * $10.85 * 24 = ~$10,156/day = ~$305K/mo (on-demand)
  With reserved instances (1yr): ~$152K/mo
  With spot: ~$90K/mo
  Per-session: $0.003-0.010 (depending on instance strategy)
```

**Critical insight:** The DIY approach looks cheaper per-session, but only when you achieve high utilization. At low utilization, managed services win because you only pay for what you use.

```
Break-even Analysis (vs E2B):

  Cost
   ^
   |         DIY (fixed)
   |    ___________________________
   |   /
   |  /   E2B (linear, per-second)
   | /
   |/
   +-----------------------------------> Sessions/day
        ^
     Break-even: ~200K-500K sessions/day
     (depending on infrastructure choices)
```

---

### Pricing Models Compared

| Model | How It Works | Who Uses It | Best For |
|-------|-------------|-------------|----------|
| **Per-second billing** | Pay for actual vCPU-seconds + GiB-seconds consumed | E2B, Modal, Cloudflare, Daytona | Bursty workloads, short sessions |
| **Per-hour billing** | Minimum 1-hour increments | Traditional VMs (EC2, GCE) | Long-running workloads |
| **Reserved capacity** | Pre-pay for committed use (1yr/3yr) | AWS RIs, Savings Plans | Predictable baseline load |
| **Flat + usage** | Monthly base fee + per-use charges | E2B Pro ($150/mo), Modal Team ($250/mo) | Mid-scale production |
| **Spot/preemptible** | Deeply discounted interruptible compute | AWS Spot, GCP Preemptible | Fault-tolerant batch workloads |

**Per-second billing deep-dive:**

```
Time granularity comparison (1 vCPU, 30-second task):

  Per-second:   30s x $0.000014 = $0.00042
  Per-minute:   1m  x $0.00084  = $0.00084   (2x overpay)
  Per-hour:     1hr x $0.05     = $0.05       (120x overpay)

  At 1M sessions/day, overpay from per-hour billing:
  $0.05 x 1,000,000 = $50,000/day vs $420/day

  Per-second billing saves ~99% for short-lived workloads.
```

---

### Hidden Costs

These are the costs that don't show up in the headline pricing:

#### 1. Data Egress

```
AWS:     $0.09/GB (first 10 TB/mo), $0.085/GB (next 40 TB)
GCP:     $0.12/GB (first 1 TB), $0.11/GB (1-10 TB)
Azure:   $0.087/GB (first 5 GB free, then tiered)
CF:      $0.025/GB (NA/EU), $0.05/GB (Asia), $0.08/GB (other)
Modal:   Included (no separate egress charges listed)
E2B:     Not prominently listed (likely bundled or billed separately)

Hidden impact at scale:
  If each session produces 1 MB of output:
  1M sessions x 1 MB = 1 TB/day = 30 TB/month
  AWS egress: 30 TB x $0.09 = $2,700/month
  Cloudflare: 30 TB x $0.025 = $750/month (1 TB free)
```

#### 2. Storage (Snapshots, Volumes, Images)

```
Snapshot storage costs:
  - Memory snapshot: ~128 MB-2 GB per snapshot (compressed)
  - If you keep 100K snapshots: 100K x 500 MB = 50 TB
  - S3 storage: $0.023/GB/mo = $1,150/mo just for snapshots
  - Plus GET requests for restores: $0.0004/1000 requests

Volume storage:
  Modal Volumes: Free (included in compute pricing)
  E2B:           20 GB free on Novita, varies on E2B
  Cloudflare:    $0.00000007/GB-second disk
  RunPod:        $0.07/GB/month for network volumes
```

#### 3. Warm Pool Overhead

```
Keeping VMs warm for instant starts has a direct cost:

  Warm pool of 1000 VMs (1 vCPU, 512 MiB each):

  On E2B:   1000 x $0.000014/s x 86400s = $1,209.60/day = $36K/mo
  On Modal: 1000 x $0.0000131/s x 86400s = $1,131.84/day = $34K/mo
  On EC2:   ~12 m5.xlarge instances = 12 x $0.192/hr x 720hr = $1,659/mo

  The managed-service warm pool costs 20x more than DIY
  because you're paying per-second for idle compute.
```

#### 4. Template/Image Build & Storage

```
Building custom sandbox images:
  E2B:  Build time is billed (Docker build on their infra)
  Modal: Image builds run on Modal compute (billed normally)

  Large images with ML dependencies (PyTorch, etc.):
    Build time: 5-15 minutes per build
    Image size: 5-20 GB
    Storage: varies by provider
```

#### 5. API Request Overhead

```
Cloudflare specifically charges for Workers requests:
  $0.30/million requests
  At 1M sandbox creations + N API calls each:
  Estimate: 5M total requests = $1.50/day (minor but adds up)

Durable Objects (Cloudflare sandbox backend):
  $0.15/million requests
  $12.50/million GB-seconds of duration
```

---

### Cost Optimization Strategies

#### 1. Warm Pools (Pre-warmed Sandboxes)

```
Strategy: Keep N sandboxes pre-booted, ready for instant handoff

  ┌──────────┐     ┌──────────────────┐     ┌──────────┐
  │ Request  │────>│  Warm Pool (N)   │────>│ Sandbox  │
  │ arrives  │     │  Pre-booted VMs  │     │  Ready!  │
  └──────────┘     └──────────────────┘     └──────────┘
                          │
                   Pool replenisher
                   (background process)
                          │
                   ┌──────────────────┐
                   │  Boot new VMs    │
                   │  to maintain N   │
                   └──────────────────┘

Sizing the pool:
  - Too small: requests wait for cold boots
  - Too large: paying for idle compute
  - Right-size: predict demand with historical patterns + buffer

  Rule of thumb: pool_size = peak_concurrent_sessions * 1.2
```

#### 2. Snapshot Cloning (Copy-on-Write)

```
Instead of booting fresh VMs, clone from a snapshot:

  Snapshot (on disk/PMEM)
       │
       ├── Clone 1 (CoW pages)  ← Only modified pages copied
       ├── Clone 2 (CoW pages)
       └── Clone 3 (CoW pages)

  Memory savings: Typically 60-80% of base image is shared
  Boot time: ~15-50ms (vs 125ms cold boot)

  HopX benchmarks:
    P50 snapshot restore: 45ms
    P95 snapshot restore: 62ms
    P99 snapshot restore: 85ms
```

#### 3. Scale-to-Zero

```
When no requests: spin down all compute, pay $0.

  Requests ──────────────────────────────────────────────>
                    ▲▲▲▲▲                    ▲▲
  Instances:  0 → 5 → 10 → 5 → 0 --------→ 3 → 0
                                   ^
                              idle timeout
                              (5-30 min)

  Tradeoff:
    Scale-to-zero saves:    100% of idle compute cost
    Scale-to-zero costs:    Cold start latency on first request

  Hybrid approach (what most platforms do):
    - Scale to zero after extended idle (>15 min)
    - Maintain small warm pool during business hours
    - Use snapshots for fast restore when scaling up
```

#### 4. Spot/Preemptible Instances (DIY)

```
For non-latency-sensitive sandbox workloads:

  AWS Spot pricing (i3en.metal):
    On-demand:  $10.85/hr
    Spot:       $3.25/hr (typical, ~70% savings)

  Strategy: Run warm pool on on-demand, overflow to spot

  ┌─────────────────┐     ┌─────────────────┐
  │  On-Demand Pool  │     │   Spot Fleet    │
  │  (baseline)     │     │   (overflow)    │
  │  Always running │     │   Interruptible │
  └─────────────────┘     └─────────────────┘
         ▲                        ▲
         │                        │
    Guaranteed              Best-effort
    availability            60-90% savings
```

---

### DIY vs Managed: Full Comparison

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

Build vs Buy Decision Matrix:

  Sessions/day     Recommendation     Why
  ─────────────    ──────────────     ─────────────────────
  < 10K            Managed            Not worth the eng cost
  10K - 100K       Managed            Still cheaper overall
  100K - 500K      Evaluate           Depends on team size
  500K - 1M        Likely DIY         Savings justify eng
  > 1M             Definitely DIY     Managed costs explode
```

---

## TOPIC 2: Core Technical Concepts Explained

### 1. Volumes: Persistent Storage Across Sandboxes

Volumes solve the fundamental problem of ephemeral sandboxes: how do you persist data when the execution environment is destroyed after each session?

#### Approaches to Sandbox Storage

```
┌─────────────────────────────────────────────────────────────┐
│                    Storage Approaches                        │
├─────────────────┬──────────────────┬────────────────────────┤
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

#### Block Devices (virtio-blk)

The simplest approach. A raw disk image file on the host is presented to the guest VM as a block device.

```
Host filesystem:
  /var/lib/firecracker/drives/rootfs.ext4   ← Disk image file

Guest sees:
  /dev/vda   ← virtio block device

Firecracker config:
  "drives": [{
    "drive_id": "rootfs",
    "path_on_host": "/var/lib/firecracker/drives/rootfs.ext4",
    "is_root_device": true,
    "is_read_only": false
  }]
```

- **Pros:** Simple, fast I/O, well-supported
- **Cons:** Not shareable between VMs, fixed size, requires pre-allocation
- **Used by:** Firecracker (default rootfs), AWS Lambda

#### virtio-fs (Shared Filesystem)

A newer approach designed specifically for VM-host file sharing. Uses the FUSE protocol over virtio, but with a direct memory path.

```
Architecture:
  ┌────────────────────┐
  │     Guest VM       │
  │   ┌────────────┐   │
  │   │ virtio-fs  │   │  FUSE-over-virtio
  │   │  driver    │   │  (shared memory, no network)
  │   └─────┬──────┘   │
  └─────────┼──────────┘
            │ VFIO / vhost-user
  ┌─────────┼──────────┐
  │   ┌─────┴──────┐   │
  │   │ virtiofsd  │   │  Userspace daemon on host
  │   │ (Rust)     │   │
  │   └─────┬──────┘   │
  │         │          │
  │   Host filesystem  │
  └────────────────────┘

Key properties:
  - Near-native performance (shared memory, no network hop)
  - Full POSIX semantics (unlike NFS)
  - DAX (Direct Access) mode: guest maps host pages directly
  - Available since Linux 5.4, QEMU 5.0
```

- **Pros:** Near-native speed, POSIX compliant, DAX for zero-copy access
- **Cons:** Requires host daemon, not supported in Firecracker (QEMU/KVM only), snapshot complexity
- **Used by:** Kata Containers, Proxmox, QEMU-based platforms

#### Network-Attached Storage

How managed platforms typically handle volumes at scale.

```
Modal Volumes architecture:
  ┌──────────┐   ┌──────────┐   ┌──────────┐
  │Container1│   │Container2│   │Container3│
  │  /data ──┤   │  /data ──┤   │  /data ──┤
  └────┬─────┘   └────┬─────┘   └────┬─────┘
       │              │              │
       └──────────────┼──────────────┘
                      │
              ┌───────┴────────┐
              │  Modal Volume  │
              │  (distributed  │
              │   filesystem)  │
              └───────┬────────┘
                      │
              ┌───────┴────────┐
              │  Object Store  │
              │  (persistent)  │
              └────────────────┘

Key behaviors:
  - Explicit commit() to persist writes
  - Explicit reload() to see other containers' changes
  - Background auto-commit every few seconds
  - Last-write-wins for concurrent file modification
  - Up to 2.5 GB/s bandwidth
  - v1: max 500K files; v2 (beta): unlimited

E2B storage:
  - Ephemeral by default (sandbox dies, data dies)
  - Persistence via pause/resume (snapshot the whole sandbox)
  - Can connect external S3 buckets
  - Templates pre-bake filesystem state

Cloudflare:
  - Durable Objects provide stateful storage
  - Containers get ephemeral disk (2-20 GB by instance type)
  - R2 (S3-compatible) for persistent object storage
```

---

### 2. Environment Snapshots & Memory Snapshots

This is the most important optimization in the sandbox space. It's how platforms achieve sub-100ms cold starts.

#### What Gets Snapshotted

```
┌─────────────────────────────────────────────────┐
│              MicroVM State                       │
├──────────────────────┬──────────────────────────┤
│   Memory Snapshot    │   Filesystem Snapshot     │
├──────────────────────┼──────────────────────────┤
│ - vCPU registers     │ - Root filesystem        │
│ - RAM contents       │ - Installed packages     │
│ - Device state       │ - User files             │
│ - Kernel state       │ - Config files           │
│ - Running processes  │ - Temp files             │
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
   ┌─────────────────────────────────────┐
   │         Snapshot Artifact            │
   ├─────────────────────────────────────┤
   │  vmstate file:                       │
   │    - vCPU registers                  │
   │    - device model state              │
   │    - interrupt controller state      │
   │                                      │
   │  memory file:                        │
   │    - Complete guest RAM dump          │
   │    - Size = allocated guest memory   │
   │                                      │
   │  disk files:                         │
   │    - Separate block device images    │
   │    - Can use backing file + overlay  │
   └─────────────────────────────────────┘

2. DIFF SNAPSHOT (incremental)
   Only stores memory pages that changed since last snapshot.
   Dramatically smaller for repeat snapshots.

   Full:  ████████████████████████  512 MB
   Diff:  ██░░░░░░░░░░░░░░░░░░░░   ~30 MB (only dirty pages)
```

#### Copy-on-Write Restore (The Key Innovation)

This is what makes snapshot restore fast. Instead of copying the entire memory file into RAM:

```
Traditional restore:
  1. Read entire memory file from disk     ← Slow (512 MB = ~100ms on NVMe)
  2. Map into guest address space
  3. Resume vCPU
  Total: 100-500ms

Copy-on-Write restore:
  1. mmap() memory file as read-only       ← Near-instant (just page table setup)
  2. Set up userfaultfd for write traps
  3. Resume vCPU
  4. On write: copy single 4KB page        ← Happens lazily, on demand
  Total: 15-50ms (page faults handled on demand)

Memory access pattern after CoW restore:

  Page 0: [READ]  → Served from mmap'd snapshot file (zero copy)
  Page 1: [WRITE] → Trap → Copy page → Write to private copy
  Page 2: [READ]  → Served from mmap'd snapshot file (zero copy)
  Page 3: [NEVER] → Never loaded at all (saves I/O)

  Typical working set: only 10-30% of pages are ever touched
  = 70-90% of snapshot memory never copied from disk
```

#### On-Demand Paging with Prefetching (Advanced)

Research systems like FaaSnap go further:

```
Standard CoW:
  Guest accesses page → page fault → load from disk → resume
  Problem: each fault adds ~10-50us latency

FaaSnap optimization:
  1. Profile which pages are accessed during first N invocations
  2. Build a "loading set" of commonly needed pages
  3. On restore: prefetch loading set pages in background
  4. Guest starts immediately, most pages already in memory

  ┌──────────────────────────────────────────┐
  │  Time ──────────────────────────────>     │
  │                                          │
  │  Guest:  [RESUME]────[RUNNING]──────>    │
  │                                          │
  │  Prefetch: ████████░░░░░░░░░░░░░░░░     │
  │            ^                             │
  │            Loading set pages             │
  │            fetched in parallel           │
  └──────────────────────────────────────────┘

  Result: ~3.5x faster end-to-end than baseline snapshot restore
```

#### Uniqueness Problem

When you clone a snapshot, all clones start with identical state. This is dangerous:

```
Snapshot taken at time T:
  - Random seed = X
  - UUID generator state = Y
  - TLS session keys = Z

Clone 1: generates UUID "abc-123" using state Y
Clone 2: generates UUID "abc-123" using state Y  ← COLLISION!

Solution (AWS paper: "Restoring Uniqueness in MicroVM Snapshots"):
  1. Inject fresh entropy into /dev/urandom on restore
  2. Re-seed all PRNGs via MMIO device
  3. Force TLS renegotiation
  4. Kernel patches: RDRAND instruction returns fresh values
```

#### Platform Snapshot Implementations

```
Platform    | Snapshot Type     | Restore Time | Persistence
────────────+───────────────────+──────────────+─────────────
Modal       | Filesystem snap   | Sub-second   | Indefinite
            | Directory snap    | Fast         | 30 days
            | Memory snap (α)   | Fast         | 7 days
E2B         | Pause/resume      | ~150ms       | Until explicit delete
            | Templates         | ~150ms       | Permanent
HopX        | Memory snapshot   | 15-50ms      | Session-scoped
Blaxel      | Standby + resume  | ~25ms        | Configurable
Lambda      | SnapStart (CRaC)  | <200ms       | Managed by AWS
```

---

### 3. Boot Times and Cold Starts

#### What Determines Cold Start Time?

```
Cold Start Breakdown (without snapshots):

  ┌─────────────────────────────────────────────────────┐
  │                                                     │
  │  VMM Init        ██  ~5ms                           │
  │  (Firecracker)                                      │
  │                                                     │
  │  Kernel Boot     ████████████  ~80-125ms             │
  │  (minimal Linux)                                    │
  │                                                     │
  │  Userspace Init  ████████  ~50-200ms                 │
  │  (init, systemd)                                    │
  │                                                     │
  │  App Start       ████████████████  ~100ms-10s        │
  │  (Python/Node/Java)                                 │
  │                                                     │
  └─────────────────────────────────────────────────────┘

  Component breakdown:
  ┌──────────────────┬────────────┬─────────────────────────┐
  │ Component        │ Time       │ What's happening         │
  ├──────────────────┼────────────┼─────────────────────────┤
  │ VMM init         │ 1-5ms      │ Firecracker process      │
  │                  │            │ starts, configures KVM   │
  │ Kernel boot      │ 80-125ms   │ Linux kernel init,       │
  │                  │            │ driver loading, mm setup  │
  │ Userspace init   │ 50-200ms   │ /init, mount filesystems │
  │                  │            │ start essential services  │
  │ App init         │ 100ms-10s  │ Load runtime, libraries  │
  │                  │            │ (Python: ~300ms,          │
  │                  │            │  Java: ~2-5s,            │
  │                  │            │  Node: ~200ms)           │
  └──────────────────┴────────────┴─────────────────────────┘

  Total cold boot: 230ms - 10s+ (depending on app)
```

#### Cold Start Comparison Across Platforms

```
Platform              │ P50        │ P95        │ Method
──────────────────────┼────────────┼────────────┼──────────────────
Blaxel (standby)      │ ~25ms      │ ~40ms      │ Warm standby
HopX (warm pool)      │ 12ms       │ 18ms       │ Pre-warmed pool
HopX (snapshot)       │ 45ms       │ 62ms       │ Snapshot + CoW
Daytona               │ ~90ms      │ ~150ms     │ Snapshots
E2B                   │ ~150ms     │ ~300ms     │ Template snapshots
Firecracker (raw)     │ ~125ms     │ ~180ms     │ Cold boot
Lambda SnapStart      │ <200ms     │ ~400ms     │ CRaC snapshots
Modal                 │ Sub-second │ ~1-2s      │ Container + snap
Docker                │ 2-5s       │ ~10s       │ Container start
Cloudflare            │ 2-3s       │ ~5s        │ Container start
Traditional VM        │ 30-60s     │ ~90s       │ Full OS boot
```

#### How Warm Pools Work

```
                    Warm Pool Architecture

  ┌─────────────────────────────────────────────────┐
  │                  Pool Manager                    │
  │                                                  │
  │  ┌──────────────────────────────────────────┐   │
  │  │  Target Pool Size Calculator             │   │
  │  │                                          │   │
  │  │  Inputs:                                 │   │
  │  │    - Historical request rate             │   │
  │  │    - Time-of-day patterns               │   │
  │  │    - Current pool size                  │   │
  │  │    - Boot time for new VMs              │   │
  │  │                                          │   │
  │  │  Output: target_size = f(demand + buffer)│   │
  │  └──────────────────────────────────────────┘   │
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
  │  1. Claim VM from   │ ← ~1-2ms (just pointer swap)
  │     pool             │
  │  2. Configure net   │ ← ~3-5ms
  │  3. Return handle   │ ← ~2ms
  │  4. Replenish pool  │ ← Background (boot new VM)
  └─────────────────────┘

  Total handoff time: 10-15ms
```

---

### 4. Networking

Sandbox networking must balance three concerns: isolation (prevent escape), connectivity (sandbox needs internet), and accessibility (users need to reach services inside).

#### Outbound Networking (Sandbox -> Internet)

```
Architecture:

  ┌────────────────────┐
  │     Guest VM       │
  │  eth0: 172.16.0.2  │
  └────────┬───────────┘
           │ virtio-net
  ┌────────┴───────────┐
  │    TAP device      │  ← Virtual network interface on host
  │    tap0             │
  └────────┬───────────┘
           │
  ┌────────┴───────────┐
  │    iptables NAT    │  ← Source NAT (MASQUERADE)
  │    + egress rules  │
  └────────┬───────────┘
           │
  ┌────────┴───────────┐
  │    Host NIC        │  → Internet
  │    eth0             │
  └────────────────────┘

Firecracker networking setup:
  1. Create TAP interface: ip tuntap add tap0 mode tap
  2. Configure NAT: iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
  3. Enable forwarding: echo 1 > /proc/sys/net/ipv4/ip_forward
  4. Pass TAP to Firecracker via API

  Each microVM gets its own TAP device.
  At 100+ VMs per host, this means 100+ TAP interfaces.
```

#### Egress Policies

```
Modal sandbox networking controls:

  # Block all network access
  sb = modal.Sandbox.create(block_network=True)

  # Allow only specific CIDRs
  sb = modal.Sandbox.create(
      cidr_allowlist=["10.0.0.0/8", "93.184.216.0/24"]
  )

E2B:
  - Internet access enabled by default
  - No built-in egress filtering (as of current docs)

Cloudflare:
  - Inherits Workers networking model
  - Egress through Cloudflare's network
  - Can use Gateway policies for filtering
```

#### Inbound Networking (Internet -> Sandbox)

How users access services running inside sandboxes:

```
Approach 1: Tunnels (Modal, Fly.io)
  ┌─────────┐     ┌───────────────┐     ┌──────────┐
  │  User   │────>│  Tunnel Proxy │────>│ Sandbox  │
  │ browser │     │  (TLS term)   │     │ port 8080│
  └─────────┘     └───────────────┘     └──────────┘

  URL: https://{sandbox-id}.modal.run
  Supports: HTTP, WebSocket, raw TCP

Approach 2: Connect Tokens (Modal)
  - Generate auth token scoped to a sandbox
  - Pass in Authorization header or query param
  - Server receives X-Verified-User-Data header
  - No way to spoof user identity

Approach 3: Preview URLs (E2B, CodeSandbox, Daytona)
  - Sandbox gets a unique subdomain
  - Reverse proxy routes traffic to correct VM
  - Often includes auto-HTTPS

  URL: https://{port}-{sandbox-id}.e2b.dev

Approach 4: SSH Tunnels (E2B, traditional)
  - Direct SSH access to sandbox
  - Port forwarding via SSH
  - Most flexible, least user-friendly
```

---

### 5. Image/Template Systems

How you define what's inside a sandbox before it starts.

#### The Three Approaches

```
┌─────────────────────────────────────────────────────────────┐
│                  Image Definition Approaches                 │
├───────────────────┬───────────────────┬─────────────────────┤
│  Docker/OCI       │  VM Images        │  SDK-Defined         │
│  Images           │  (disk images)    │  (code-first)        │
├───────────────────┼───────────────────┼─────────────────────┤
│ Dockerfile or     │ Raw ext4/squashfs │ Python/TS code       │
│ pre-built image   │ disk images       │ defines the env      │
│                   │                   │                      │
│ E2B, Cloudflare,  │ Firecracker,      │ Modal                │
│ Daytona, Beam     │ Lambda (internal) │                      │
├───────────────────┼───────────────────┼─────────────────────┤
│ FROM ubuntu:22.04 │ dd if=/dev/zero   │ modal.Image          │
│ RUN pip install   │ mkfs.ext4         │  .debian_slim()      │
│ COPY app /app     │ mount + install   │  .pip_install("np")  │
│                   │ umount            │  .run_commands(...)   │
└───────────────────┴───────────────────┴─────────────────────┘
```

#### E2B Templates (Docker-based)

```
E2B template workflow:

  1. Define: e2b.Dockerfile
     ┌────────────────────────────┐
     │ FROM e2b/base:latest       │
     │ RUN pip install numpy      │
     │ RUN apt-get install -y git │
     │ COPY config /etc/config    │
     └────────────────────────────┘

  2. Build: e2b template build --name my-template
     - Runs Docker build on E2B infrastructure
     - Creates a template artifact (snapshot-ready image)
     - Stores in E2B's template registry

  3. Use:
     from e2b import Sandbox
     sandbox = Sandbox("my-template")

  4. What happens under the hood:
     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
     │  Dockerfile  │────>│  OCI Image   │────>│  MicroVM     │
     │  (source)    │     │  (artifact)  │     │  (running)   │
     └──────────────┘     └──────────────┘     └──────────────┘

     The OCI image is converted to a rootfs that Firecracker
     can boot. Template includes a pre-snapshotted state for
     fast restore.
```

#### Modal SDK-Defined Images

```
Modal's code-first approach:

  image = (
      modal.Image.debian_slim()          # Base OS
      .pip_install("numpy", "pandas")    # Python packages
      .apt_install("ffmpeg", "git")      # System packages
      .run_commands("echo 'setup done'") # Arbitrary commands
      .copy_local_file("config.py")      # Local files
  )

  sb = modal.Sandbox.create(
      image=image,
      app=app
  )

How it works internally:
  1. Each method call creates a layer (like Docker layers)
  2. Layers are content-addressed and cached
  3. Image is built on Modal's build infrastructure
  4. Result is a container image stored in Modal's registry
  5. Images can be dynamically composed at runtime

Advantage: No Dockerfile, no Docker daemon, no registry config.
           Pure Python. Images are defined as code, not config.
```

#### Cloudflare (Container Images)

```
Deploy any OCI-compatible container:

  - Standard Dockerfiles work
  - Images pulled from any registry (Docker Hub, GHCR, etc.)
  - Instance types define resource limits
  - Containers managed by Durable Objects (for state)

  Architecture:
    Worker (your code)
      └── Creates Sandbox via SDK
            └── Durable Object (manages lifecycle)
                  └── Container (isolated Linux environment)
                        └── Your code runs here
```

---

### 6. Scale-to-Zero

The mechanism by which sandbox platforms avoid charging you when there's no work to do.

#### How It Works Technically

```
Scale-to-Zero State Machine:

  ┌─────────┐  request   ┌──────────┐  complete  ┌──────────┐
  │  ZERO   │──────────>│ SCALING  │──────────>│ RUNNING  │
  │(no VMs) │           │   UP     │           │(serving) │
  └─────────┘           └──────────┘           └──────────┘
       ^                                            │
       │              idle timeout                  │
       └────────────────────────────────────────────┘
                    (e.g., 5-30 min idle)

What happens during scale-up from zero:

  T+0ms:    Request arrives at load balancer
  T+1ms:    LB detects no healthy backends
  T+2ms:    Triggers provisioning
  T+50ms:   VM/container starts booting
  T+200ms:  Health check passes
  T+250ms:  Request forwarded to new instance
  T+300ms:  Response returned

  Total cold start penalty: ~300ms (best case)

What happens during scale-down to zero:

  T+0:        Last request completes
  T+5min:     Idle timer expires (configurable)
  T+5min+1s:  Snapshot taken (if supported)
  T+5min+2s:  VM terminated
  T+5min+3s:  Resources released

  Cost during idle period: still billed (5 min * rate)
```

#### Scale-to-Zero vs Warm Pools: The Fundamental Tradeoff

```
                         Scale-to-Zero           Warm Pool
                         ═══════════════         ═══════════════
  Idle cost              $0                      $$$ (pool * rate)
  Cold start latency     200ms - 5s              10-50ms
  First-request UX       Poor (wait)             Excellent (instant)
  Predictable perf       No (varies)             Yes (consistent)
  Cost at low traffic    Very low                High (wasted capacity)
  Cost at high traffic   Same as warm pool       Same as scale-to-zero
  Complexity             Low                     High (pool management)

  The hybrid approach (what most platforms actually do):

  Traffic ──────────────────────────────────────────────>

  ┌───────────┐  ┌────────────────┐  ┌───────────────┐
  │  Night    │  │   Business     │  │   Evening     │
  │           │  │    Hours       │  │               │
  │ Scale to  │  │  Warm pool    │  │  Scale down   │
  │   zero    │  │  (N instances) │  │  gradually    │
  │           │  │               │  │               │
  │ $0/hr     │  │ $$/hr         │  │ $/hr          │
  └───────────┘  └────────────────┘  └───────────────┘

  Pool sizing adapts to demand:
    - ML model predicts traffic patterns
    - Pool grows 10-15 min before predicted spike
    - Pool shrinks as traffic drops
    - Full zero-out only during dead periods
```

#### Platform-Specific Implementations

```
Cloudflare Containers:
  - Charges stop when container sleeps
  - Sleep triggered by configurable inactivity timeout
  - Wake on HTTP request (routed through Worker)
  - CPU billed on active usage only
  - Memory/disk billed on provisioned (even when sleeping)

Modal:
  - Functions scale to zero by default
  - Sandboxes run until explicitly terminated
  - No automatic scale-to-zero for sandboxes
  - Use snapshots + destroy/restore for manual scale-to-zero

E2B:
  - Sandboxes have configurable TTL (max 1hr free, 24hr pro)
  - Auto-terminate after TTL
  - Persistence via pause/resume snapshots
  - No true scale-to-zero (sandbox exists or doesn't)

Lambda:
  - Aggressive scale-to-zero (after ~5-15 min idle)
  - SnapStart mitigates cold start penalty
  - Provisioned concurrency for guaranteed warm instances
  - Provisioned concurrency cost: ~$0.015/hr per instance
```

---

## Summary: Key Takeaways

### Economics

```
Decision Framework:

  ┌─────────────────────────────────────────────────────┐
  │  Scale         │  Best Approach     │  Monthly Cost  │
  ├────────────────┼────────────────────┼────────────────┤
  │  < 10K/day     │  Managed (E2B)     │  $200-500      │
  │  10K-100K/day  │  Managed (Modal)   │  $500-5,000    │
  │  100K-500K/day │  Evaluate both     │  $5K-50K       │
  │  > 500K/day    │  DIY Firecracker   │  $25K-150K     │
  └────────────────┴────────────────────┴────────────────┘

Hidden costs can add 20-40% to base compute:
  - Egress: 5-15% of compute cost
  - Storage: 5-10%
  - Warm pools: 10-30% (if over-provisioned)
  - Engineering (DIY): 1-3 engineers full-time
```

### Technical Concepts Hierarchy

```
How everything connects:

  Image/Template ──builds──> Rootfs + Packages
       │
       v
  Cold Boot ──or──> Snapshot Restore (CoW) ──> Running VM
       │                    │
       │                    └── Warm Pool (pre-restored)
       │
       v
  Volumes ──mount──> Persistent data across sessions
       │
       v
  Networking ──configures──> NAT + Egress rules + Tunnels
       │
       v
  Scale-to-Zero ──terminates──> Snapshot + Destroy
       │                              │
       └──── Request arrives ─────────┘
              (restore from snapshot)
```

---

## Sources

- Superagent AI Code Sandbox Benchmark 2026: https://www.superagent.sh/blog/ai-code-sandbox-benchmark-2026
- E2B Pricing: https://e2b.dev/pricing
- Modal Pricing: https://modal.com/pricing
- Modal Volumes Docs: https://modal.com/docs/guide/volumes
- Modal Sandbox Snapshots: https://modal.com/docs/guide/sandbox-snapshots
- Modal Sandbox Networking: https://modal.com/docs/guide/sandbox-networking
- Cloudflare Containers Pricing: https://developers.cloudflare.com/containers/pricing/
- HopX 100ms Cold Starts: https://hopx.ai/blog/deep-dives/how-hopx-achieves-100ms-cold-starts/
- SkyPilot Self-Hosted Sandbox: https://blog.skypilot.co/skypilot-llm-sandbox/
- Novita vs E2B Pricing: https://blogs.novita.ai/novita-sandbox-e2b/
- Northflank Firecracker Explainer: https://northflank.com/blog/what-is-aws-firecracker
- Firecracker Snapshot Docs: https://github.com/firecracker-microvm/firecracker/blob/main/docs/snapshotting/snapshot-support.md
- "Restoring Uniqueness in MicroVM Snapshots" (AWS, 2021): https://arxiv.org/abs/2102.12892
- FaaSnap Paper: http://faculty.washington.edu/wlloyd/courses/tcss591/papers/FaaSnap-FaaSMadeFastUsingSnapshot-basedVMs.pdf
- "Fork in the Road: Cold Start Latency in Production" (OSDI 2025): https://www.usenix.org/conference/osdi25/presentation/chai-xiaohu
- PASS/SnapStart in Persistent Memory (USENIX ATC 2024): https://www.usenix.org/conference/atc24/presentation/pang
- virtio-fs Design: https://virtio-fs.gitlab.io/design.html
- Self-Hosted Containers vs MicroVMs: https://medium.com/@odafe41/self-hosted-sandboxes-how-to-pick-between-containers-and-microvms-1fa4803b7bdf
- E2B Template Docs: https://e2b.dev/docs/sandbox-template
- Cloudflare Sandbox Architecture: https://developers.cloudflare.com/sandbox/concepts/architecture/
