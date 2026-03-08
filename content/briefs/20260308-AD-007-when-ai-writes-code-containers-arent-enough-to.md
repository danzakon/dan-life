---
id: 20260308-AD-007
created: 2026-03-08
source-type: research
ingest-source: content-pipeline
status: approved
format: article
platform: Both
series-id:
generate: single
next-action: draft
---

## Core Insight
The shared kernel that makes containers fast also makes them the wrong security boundary for untrusted AI-generated code.

## Draft Instructions
Don't make this about any specific product. Make it about the architectural misconception. The argument: most teams running AI agents are executing code in Docker containers because Docker is what they know. But containers share the host kernel — every syscall from container code goes to the same kernel. A kernel bug reachable via any allowed syscall is a host escape. Dirty COW, Dirty Pipe, runc overwrite — all were container escapes from properly configured containers. 94% of organizations have reported serious container security incidents. The threat model for AI agents specifically: secret exfiltration (agent reads ~/.ssh or API tokens), lateral movement (pivots from sandbox to production DB), resource exhaustion (fork bombs, crypto mining). The alternative: gVisor (syscall interception) or Firecracker (dedicated guest kernel). Be concrete about what isolation actually means. This is a security-education article, not a product comparison.

## Sources
- research/reports/20260219-code-execution-sandboxes.md

## Related Items
- 20260308-AD-006
