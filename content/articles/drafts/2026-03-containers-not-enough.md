---
title: "When AI Writes Code, Containers Aren't Enough to Contain It"
status: draft
platform: x-article
thumbnail: pending
perspective: "The shared kernel that makes containers fast is exactly what makes them the wrong security boundary for untrusted AI-generated code."
sources:
  - research/reports/20260219-code-execution-sandboxes.md
content-id: 20260308-AD-007
---

# When AI Writes Code, Containers Aren't Enough to Contain It

Most teams running AI agents in production are executing AI-generated code inside Docker containers. It makes sense. Docker is what everyone knows. It's fast to set up, well-documented, and feels like isolation.

It isn't. Not for this.

## What a Container Actually Is

A container is a process running in separate Linux namespaces, sharing the host kernel. Four kernel features do the work: PID namespaces give it an isolated process tree, mount namespaces give it its own filesystem view, network namespaces give it an isolated network stack, and user namespaces map the container's root to an unprivileged host UID. Cgroups cap CPU and memory. Seccomp filters dangerous syscalls. AppArmor or SELinux add another access control layer.

That sounds like a lot of protection. Here's the problem: every syscall from inside the container still goes to the same host kernel. The namespace boundaries are enforced *by* that kernel. If the kernel has a bug reachable via any allowed syscall path, the container boundary disappears.

This is a well-understood architectural limitation when you're running your own code. It becomes an unacceptable risk when you're running code written by an LLM.

## The Track Record

Container escapes from properly configured containers are not theoretical.

**CVE-2016-5195 (Dirty COW):** A race condition in the kernel's copy-on-write mechanism let any process write to read-only memory mappings. An attacker inside a container could overwrite files owned by root on the host. The bug had existed in the Linux kernel since 2007. It was actively exploited in the wild before it was patched.

**CVE-2019-5736 (runc overwrite):** The runc container runtime allowed a malicious container to overwrite the host runc binary. A container that managed to exploit this could execute arbitrary commands on the host as root. The fix required patching runc itself, not the kernel.

**CVE-2022-0847 (Dirty Pipe):** A flaw in the Linux pipe buffer handling allowed overwriting data in arbitrary read-only files. Similar to Dirty COW but easier to exploit. Any process could escalate to root by overwriting `/etc/passwd` or injecting into SUID binaries.

These weren't obscure edge cases. They were all container escapes that worked against properly configured, hardened containers. And they keep happening. 94% of organizations have reported serious container security incidents. 60% were vulnerable to the "Leaky Vessels" container escape CVEs disclosed in early 2024.

The shared kernel is the shared attack surface.

## Why AI Agents Make This Worse

When a human developer runs code in a container, there's implicit trust. The developer wrote the code, or at least reviewed it. They have context about what it should do and what it shouldn't.

AI agents don't have that trust relationship. The failure modes go beyond simple escape:

**Secret exfiltration.** The agent's code reads `~/.ssh`, `~/.aws`, or API tokens from the environment and sends them to an external server. Inside a container that shares the host filesystem or mounts sensitive directories, this is trivial.

**Lateral movement.** The agent's code discovers it can reach internal services via the network. It pivots from the sandbox to a production database, an internal API, or another service that assumed network-level trust.

**Resource exhaustion.** Fork bombs, crypto mining, infinite loops. The agent pegs all CPUs or OOMs the host. Cgroups help here, but they're a resource limit, not a security boundary.

**Kernel exploitation.** This is the big one. The agent generates code that triggers a kernel vulnerability through a legal, unsuspicious syscall. The container boundary ceases to exist. The agent now has host-level access.

The attack surface is enormous because the code is arbitrary. A human developer writes predictable patterns. An LLM generates whatever its training data and prompt lead it to. The range of syscalls it might invoke, the packages it might install, the network calls it might make are all unbounded.

## What Isolation Actually Means

The question to ask about any sandbox is: what does the untrusted code share with the host?

For a standard container, the answer is: the kernel. Every one of the hundreds of Linux syscalls is a potential attack vector.

**gVisor** takes a different approach. It interposes a userspace kernel (called the Sentry) between the application and the host kernel. The application's syscalls go to the Sentry. The Sentry makes a small, auditable set of host syscalls, around 68 compared to the hundreds a container exposes. A kernel bug in the host is only exploitable if it's reachable through one of those 68 calls. OpenAI uses gVisor for ChatGPT's Code Interpreter. Google uses it for Gemini, Cloud Run, and Cloud Functions.

**Firecracker microVMs** go further. Each sandbox runs its own guest kernel behind hardware virtualization (KVM). The host kernel never sees the application's syscalls at all. It only sees KVM ioctls and virtio device I/O. The attack surface is the hypervisor interface, which is deliberately minimal: 4 devices, 24 syscalls, 30 ioctls. AWS Lambda runs trillions of monthly invocations on Firecracker. E2B, Fly.io, and Vercel all use it for agent sandboxes. Boot time is around 125ms with less than 5MB of memory overhead per VM.

Microsoft went even further for Copilot's code execution: Hyper-V, a Type-1 bare-metal hypervisor. Over a billion users run code through it.

The pattern across every major AI lab is the same: none of them use plain containers for untrusted code execution.

## The Cost of Getting This Right

The argument against stronger isolation usually comes down to performance and complexity. "Containers boot in 10ms. Firecracker takes 125ms. We can't afford that latency."

But 125ms is not a meaningful delay in an agent workflow where the LLM inference step takes seconds. And with snapshot-based restore (copy-on-write memory mapping), platforms like E2B and Daytona get that down to 15-50ms. Warm pools eliminate cold starts entirely.

The engineering cost is real if you build it yourself. Firecracker is straightforward to run, but everything around it (networking, storage, scheduling, monitoring, image management) takes months of infrastructure work. That's why managed platforms exist. Below 100K sessions per day, the managed option is almost always cheaper than DIY.

The cost of getting it wrong is harder to quantify until it happens. A single credential exfiltration incident, a single lateral movement from a sandbox to a production database, and the economics of "containers were good enough" stop looking so attractive.

## The Uncomfortable Bottom Line

If you're running AI-generated code in Docker containers, you're making a specific bet: that the Linux kernel has no exploitable bugs in any syscall path reachable by arbitrary, untrusted code. Given that Dirty COW lived in the kernel for nine years before discovery, and that new container escapes surface regularly, that's a bet most teams should not be making.

gVisor and Firecracker exist. They're mature, production-proven at massive scale, and the performance gap is negligible for agent workloads. The only reason to skip them is if you haven't thought about the threat model.

Think about the threat model.
