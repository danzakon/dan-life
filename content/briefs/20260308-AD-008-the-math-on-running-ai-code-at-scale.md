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

---

## Content Tree

### Post Excerpts (draft these -- ready for write-post)

1. **The warm pool trap**: "Keeping 1,000 idle VMs warm on E2B costs $36K/month. The same capacity on EC2 costs $1,659. That's a 20x premium for compute that does nothing but wait. If your AI product needs fast response times at scale, warm pool economics matter more than per-session pricing."

2. **The billing granularity post**: "A 30-second AI code execution task costs $0.00042 with per-second billing. The same task with per-hour billing costs $0.05. That's 120x more. At a million sessions per day, the difference is $420/day versus $50,000/day. Before you compare sandbox platforms, check how they bill."

3. **The sequential decision**: "Start with a managed sandbox platform. Every time. But know your break-even: 200K-500K sessions per day. If your growth points there within 18 months, start building DIY Firecracker infrastructure now. The 6-12 month build time means you need to move before the economics force your hand."

### Thread Potential

Yes. The article compresses well into a 6-tweet thread: (1) the per-session cost, (2) how it scales, (3) warm pool trap, (4) billing granularity, (5) break-even point, (6) the sequential strategy.

### Series Connection

No active series match. Could seed a new "Infrastructure Economics" series if paired with the sandbox market article (AD-006) and the containers security article (AD-007).

### Thumbnail Concept

1. A simple cost curve chart showing two lines diverging: "Managed" scaling linearly upward and "DIY" flattening out, with the crossover point labeled "200K-500K sessions/day". Clean, minimal, dark background.
2. A calculator or spreadsheet aesthetic with the key number "$0.005" prominently displayed, scaling up to "$135K/mo" with an arrow.
