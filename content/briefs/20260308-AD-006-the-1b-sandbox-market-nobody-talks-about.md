---
id: 20260308-AD-006
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
There's a $1B+ infrastructure market forming around "where does AI-generated code safely run" and most engineers building with AI agents have never heard of the companies building it.

## Draft Instructions
The article is an accessible map of the sandbox market: E2B ($21M Series A, powers Perplexity and Manus), Daytona ($24M Series A, sub-90ms cold starts), Modal (GPU support, Python-first), and the cloud providers catching up (AWS Bedrock AgentCore, GKE Agent Sandbox, Azure Dynamic Sessions). The argument: every AI agent that writes or executes code needs a place to run it safely — and that place is not your laptop, not a plain Docker container, not your production server. This is an infrastructure category forming in real time. Keep it accessible — explain why this market exists (the failure modes when you don't isolate agent code), then give the lay of the land. Good for engineers who are building agents but haven't thought about execution environments.

## Sources
- research/reports/20260219-code-execution-sandboxes.md

## Related Items
- 20260308-AD-007
- 20260308-AD-008
