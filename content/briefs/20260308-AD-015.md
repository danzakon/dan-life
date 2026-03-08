---
id: 20260308-AD-015
created: 2026-03-08
source-type: research
ingest-source: content-pipeline
status: approved
format: article
platform: Both
series-id:
generate: single
next-action: research
---

## Core Insight
Agent memory has multiple competing architectural approaches with meaningfully different tradeoffs, and the best choice depends on use case in ways most teams building agents don't understand yet.

## Draft Instructions
This article compares the main agent memory providers: Letta (ex-MemGPT, OS-inspired hierarchy, sleep-time compute), Mem0 (hybrid vector+KV+graph, AWS exclusive, highest benchmark accuracy), Zep/Graphiti (temporal knowledge graphs, bi-temporal model). Also cover the simpler filesystem-backed approach (CLAUDE.md, AGENTS.md) as the most practical pattern for coding agents. The article should help readers understand which memory architecture is right for their use case and why. Needs additional research before drafting — the agent stack component map has a summary but not enough depth for a full comparison article. Research should cover: benchmark comparisons, pricing, specific use case strengths, the multi-agent memory coordination problem (15x token multiplier), and what "sleep-time compute" actually means in practice.

## Research Scope
Compare Letta vs Mem0 vs Zep/Graphiti in depth. Focus on: architecture differences, performance benchmarks, pricing, integration complexity, and which use cases each wins for. Also research the multi-agent memory problem specifically.

## Sources
- research/reports/20260308-agent-stack-component-map.md

## Related Items
- 20260308-AD-011
