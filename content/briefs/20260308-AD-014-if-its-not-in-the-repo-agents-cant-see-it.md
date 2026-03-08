---
id: 20260308-AD-014
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
If your engineering knowledge lives in people's heads and Slack threads, agents can't access it — and that's now a measurable constraint on how much you can leverage AI.

## Draft Instructions
From OpenAI's Harness team: "anything not written down is lost context. The team treats the repo as the single system of record for product principles, engineering norms, architecture decisions, and even team culture preferences." The argument: tacit knowledge has always had a cost — onboarding time, bus factor, institutional memory loss. AI agents make that cost visible and quantifiable. An agent operating with incomplete context produces worse code. Every engineering decision, convention, and architecture call that lives in someone's head or a Slack thread is invisible to the agents doing your work. The implication: teams that aggressively codify their engineering knowledge (CLAUDE.md files, AGENTS.md, ADRs, spec docs) will get disproportionately better results from AI agents. Make this feel urgent and practical. Give concrete examples of what should be in the repo vs. what typically isn't.

## Sources
- research/reports/20260308-agentic-sdlc-big-team-leverage.md

## Related Items
- 20260308-AD-012

---

## Content Tree

### Post Excerpts (draft these)

1. **The invisible cost of tribal knowledge**

Your agents don't know what you agreed on in Slack six months ago. They can't ask the senior engineer who knows everything. They operate on what's committed to the repo. That's it.

Every engineering convention, architecture decision, and operational constraint that lives in someone's head is directly reducing the quality of your agent's output.

One hour writing a CLAUDE.md file in your repo. Compound returns on every agent-generated PR after that.

2. **The onboarding test**

Here's a quick test for your team's AI-readiness: if a competent engineer joining tomorrow would need weeks to absorb unwritten conventions, naming patterns, and operational constraints... your agents are missing all of that context too.

OpenAI's Harness team shipped 1M lines of agent-written code. Their biggest lesson had nothing to do with model capability: "anything not written down is lost context."

3. **The documentation flywheel**

Teams with documented codebases get better agent output. Better output means fewer review comments. Fewer comments means faster merges. More capacity means more time to document.

Teams without documentation get worse agent output. More review comments. Slower merges. Less capacity. Less documentation. The gap compounds.

### Thread Potential

Yes. The article could compress into a 5-tweet thread:
1. OpenAI Harness finding (hook)
2. What tacit knowledge actually costs (now quantifiable)
3. What belongs in a CLAUDE.md (concrete examples)
4. The compounding effect (Ramp/Stripe data)
5. Start with one file. Watch what happens.

### Series Connection

Could seed a new series: "agent-ready engineering" or similar, focused on organizational changes teams need to make for effective agent adoption. This article + AD-012 (Stripe's deterministic architecture) + AD-013 (PR metric) could form a trilogy on what makes engineering orgs effective with AI agents.

### Thumbnail Concept

1. A split-screen visual: on the left, a messy Slack thread / whiteboard / sticky notes. On the right, a clean repo file structure with CLAUDE.md highlighted. A robot/agent icon looking at each side, confused on the left, productive on the right.

2. A magnifying glass over a git repo, with glowing CLAUDE.md and AGENTS.md files among regular code files. The "hidden knowledge" concept visualized as faded/ghosted text floating outside the repo boundary.
