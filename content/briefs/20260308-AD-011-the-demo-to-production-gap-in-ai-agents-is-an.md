---
id: 20260308-AD-011
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
35% of enterprises are experimenting with AI agents but only 11% run them in production — and the gap is infrastructure, not intelligence.

## Draft Instructions
Use the agent stack component map as the structure. The argument: the demo-to-production gap in AI agents is not a model problem. It's ten distinct infrastructure problems — sandbox architecture, communication protocols, file system persistence, permission systems, the agent harness, observability, lifecycle management, memory, multi-agent coordination, deployment — and most teams are solving fewer than half. A good agent on bad infrastructure fails in production. A mediocre model in a solid harness ships reliably. Give readers the mental model of the 10 layers without turning it into a deep dive on any one. Point at the layers that are most commonly missed. The goal is to make engineering leaders look at their agent project and ask "which of these 10 layers have we actually solved?" Use the ASCII stack diagram from the research to anchor the structure.

## Sources
- research/reports/20260308-agent-stack-component-map.md

## Related Items
- 20260308-AD-015

---

## Content Tree

### Post Excerpts (draft these, ready for write-post)

1. **The 35% vs 11% gap**
35% of enterprises are experimenting with AI agents. Only 11% have them in production. The gap? Not model quality. It's infrastructure. There are 10 distinct layers needed to run agents reliably, and most teams are solving fewer than half. Sandbox architecture, permissions, observability, memory, lifecycle management. If you haven't solved at least five, you don't have a production agent. You have a demo that runs on your laptop.

2. **The harness is the layer nobody talks about**
Five independent teams, including OpenAI and Anthropic, all landed on the same conclusion: the bottleneck for AI agents is infrastructure, not intelligence. Better models actually make it worse. More capability means more autonomy, and more autonomy demands better guardrails. The "agent harness" (context architecture, specialization, persistent memory, structured execution) is the most important and least documented layer in the stack. A mediocre model in a solid harness ships more reliably than a frontier model with no harness at all.

3. **Agent observability is broken**
AI agents fail in ways traditional monitoring can't see. HTTP 200, no exceptions, completely wrong output. They're non-deterministic, they trigger compound operations, and token cost is a runtime variable. Most teams don't instrument their agents at all. They find out something went wrong when a user reports it, and then they have no trace to debug. OpenTelemetry's GenAI conventions are emerging as the standard, but adoption is early. If you're building agents and not tracing them, you're flying blind.

### Thread Potential

Yes. The 10-layer stack itself is a natural thread structure: quick intro on the 35/11 gap, then one tweet per layer with the key insight, closing with "how many have you actually solved?" Estimated 12-13 tweets.

### Series Connection

This could seed a new series around "Production Agent Infrastructure" with individual deep dives per layer. The research report already maps a 10-part content series. Not yet an active series in series.md, but strong enough signal to promote it.

### Thumbnail Concept

A vertical stack of 10 labeled layers (like a geological cross-section or network diagram), with the top 3-4 layers brightly colored and the bottom 6-7 grayed out or crossed out. Visual message: most teams only see the top of the stack. Alternative: a split screen showing a polished demo on the left and a chaotic infrastructure diagram on the right, with "35% experimenting / 11% in production" overlaid.
