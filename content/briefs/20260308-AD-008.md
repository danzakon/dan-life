---
id: 20260308-AD-008
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
Running AI agent code at scale has a predictable economic inflection point where managed platforms become more expensive than building your own, and most teams hit it earlier than they expect.

## Draft Instructions
Use the real numbers from the research: $0.005 per 5-minute session on E2B or Daytona. At 1M sessions/day that's $135,000/month. DIY Firecracker on bare metal gets you to $24K-90K/month — but costs 6-12 months of engineering time to build. The break-even is around 200K-500K sessions/day. Also explain the hidden costs: warm pool overhead (1,000 idle VMs on E2B = $36K/month vs $1,659 on EC2), egress ($2,700/month at 1M sessions with 1MB output each), per-minute vs per-second billing (120x overpay for short tasks with hourly billing). The argument: teams discover this math too late, after they've built on a managed platform and are facing scaling costs. Concrete, numbers-driven, actionable. Good for engineering leaders planning AI agent infrastructure.

## Sources
- research/reports/20260219-code-execution-sandboxes.md

## Related Items
- 20260308-AD-006
