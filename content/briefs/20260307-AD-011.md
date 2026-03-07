---
id: 20260307-AD-011
created: 2026-03-07
source-type: thought
ingest-source: content-pipeline
status: approved
format: full-tree
platform: Both
series-id:
generate: full-tree
next-action: series-seed
---

## Core Insight

We need to rethink the entire stack for building agents. Sandbox architecture, sandbox-to-server connections, file system/volume mounting, permission systems — none of this infrastructure exists properly yet.

## Your Take

This is a big technical series arc. The infrastructure layer for agents is being hacked together right now. Nobody has built the "right" stack yet. This needs deep research into what exists (Docker, Firecracker, E2B, Modal, Fly.io), what's missing, and what the ideal architecture looks like. Each layer of the stack deserves its own piece. A scaffold project that auto-deploys via Terraform could be both content and an actual open-source project.

Key layers to explore:
- Sandbox architecture (isolation, security, resource limits)
- Sandbox ↔ server connection (how agents talk to the outside world)
- File system / volume mounting (state persistence for agents)
- Permission systems (what agents can and can't do)
- Deployment/infrastructure-as-code (Terraform, auto-deploy scaffolds)

## Lead Angle

Practical/technical — this is "here's what the stack should look like" content, grounded in real architecture decisions. Not theoretical — aimed at people building agent infrastructure today.

## Content Tree

- **Series:** "The Agent Stack" — multi-episode technical arc
  - Episode 1: "The agent infrastructure gap" — what's missing and why it matters (post + article)
  - Episode 2: "Sandbox architecture for agents" — deep dive on isolation (article, needs research)
  - Episode 3: "How agents talk to the world" — the connection layer (article, needs research)
  - Episode 4: "State and storage for agents" — file systems, volumes, persistence (tutorial)
  - Episode 5: "Agent permissions done right" — security and access control (article, needs research)
  - Episode 6: "Deploy an agent stack in 10 minutes" — the Terraform scaffold (tutorial + open source)
- **Research needed:** Survey of existing agent infrastructure (E2B, Modal, Fly, Docker, Firecracker), gaps, patterns
- **Tutorials needed:** Building each layer, end-to-end scaffold deployment

## Draft Instructions

This series needs a planning phase first. Heavy research required — survey what exists, identify gaps, form opinions on what's right. Each episode should be technically deep enough that infrastructure engineers learn something, but accessible enough that senior developers can follow. Architecture diagrams are essential for every episode. The Terraform scaffold could become an actual open-source project — flag this as a potential deliverable beyond content.

## Sources

- Thought bank: content/.scratchpad/thought-bank-2026-02.md

## Related Items

- 20260307-AD-010 (software factories) — factories need this infrastructure
- 20260307-AD-003 (mobile agent UI) — the UI layer sits on top of this stack
- 20260307-AD-006 (agent lifespan) — infrastructure determines agent lifecycle options

## Spinoffs

- Open-source agent stack scaffold (actual project, not just content)
- Comparison matrix: E2B vs Modal vs Fly vs self-hosted for agent infrastructure
- "The permission problem" — why agent permissions are harder than human permissions
