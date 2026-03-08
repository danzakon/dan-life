---
id: 20260308-AD-012
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
The key to reliable AI-generated code isn't smarter models — it's making quality checks deterministic so the agent has no choice but to run them.

## Draft Instructions
Anchor on Stripe's Minions architecture, specifically Layer 4: the interleaved architecture. The insight: in standard agent workflows, the LLM decides everything — including whether to lint, run tests, commit. Stripe removed those decisions from the LLM entirely. Creative work (writing code, fixing bugs) alternates with deterministic gates (linting, testing, committing) that execute unconditionally. The agent cannot skip quality checks. Also: the two-round CI cap as a circuit breaker. If the agent can't fix a test in two attempts, it stops and surfaces to a human. This prevents infinite loops and the "gutter" — where context fills with error logs and the agent spirals. The article's argument: probabilistic systems become reliable when you constrain creativity within deterministic process. The Stripe stat: 1,000+ PRs merged weekly, fire-and-forget. Also touch on why "letting the LLM decide whether to lint" is the wrong architecture and how most teams make this mistake.

## Sources
- research/reports/20260308-agentic-sdlc-big-team-leverage.md

## Related Items
- 20260308-AD-013
- 20260308-AD-014
