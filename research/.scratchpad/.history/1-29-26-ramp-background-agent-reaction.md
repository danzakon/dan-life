# Ramp's Background Agent: What It Reveals About the Future of Software Development

**Date:** 1-29-26
**Category:** Research Report / Reaction Piece
**Source:** [Why We Built Our Own Background Agent](https://builders.ramp.com/post/why-we-built-our-background-agent)

---

## Executive Summary

Ramp's "Inspect" agent represents the first credible signal that background agents are crossing from "interesting experiment" to "load-bearing infrastructure." With 30% of their frontend and backend PRs now authored by an AI agent, Ramp isn't demonstrating a toy—they're showing a production workflow that fundamentally changes what it means to be a software team.

But the real story isn't Inspect itself. It's what Ramp's approach reveals about *where this is going*. Their decision to build rather than buy, their "it only has to work on your code" philosophy, and their multiplayer-first architecture all point to a future most companies aren't preparing for.

This piece examines Ramp's blog through several lenses: the technical architecture choices that matter, the organizational implications that aren't being discussed, the security elephant in the room, and predictions for how this plays out across the industry.

---

## Table of Contents

1. [The Core Insight: "It Only Has to Work on Your Code"](#the-core-insight)
2. [Architecture Decisions That Will Age Well](#architecture-decisions)
3. [The 30% Number and What It Actually Means](#the-30-number)
4. [The Security Problem Nobody Wants to Talk About](#security-problem)
5. [Multiplayer: The Underrated Feature](#multiplayer)
6. [Why Build vs. Buy Is the Wrong Frame](#build-vs-buy)
7. [What This Means for Engineering Organizations](#organizational-implications)
8. [Predictions](#predictions)

---

## The Core Insight: "It Only Has to Work on Your Code" {#the-core-insight}

The most important sentence in Ramp's post is easily missed:

> "We built Inspect because owning tooling enables building something more powerful than off-the-shelf alternatives... it only has to work on your code."

This is a profound reframing of the AI coding assistant problem. Every major tool—Cursor, Copilot, Claude Code, Devin—is trying to be a general-purpose solution. They optimize for working *reasonably well* across millions of codebases. Ramp is optimizing for working *exceptionally well* on exactly one codebase.

The implications cascade:

```
┌─────────────────────────────────────────────────────────────────┐
│                    General-Purpose Agent                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │   Codebase  │  │   Codebase  │  │   Codebase  │  × millions  │
│  │      A      │  │      B      │  │      C      │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
│         ↓                ↓                ↓                      │
│     Works OK         Works OK         Works OK                   │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    Ramp's Approach                               │
│                    ┌─────────────┐                               │
│                    │    Ramp     │  × 1                          │
│                    │  Codebase   │                               │
│                    └─────────────┘                               │
│                          ↓                                       │
│                    Works Great                                   │
│                                                                  │
│  + Sentry integration   + LaunchDarkly context                   │
│  + Datadog access       + Internal skills library                │
│  + Temporal awareness   + Team conventions encoded               │
└─────────────────────────────────────────────────────────────────┘
```

This isn't a small optimization. When your agent understands your feature flag system, can query your telemetry, knows your internal abstractions, and follows your exact style guide—the compound effect is substantial.

The question for other engineering orgs: Is your codebase large enough and specialized enough to justify custom tooling? For Ramp (and likely any company with 50+ engineers), the answer is increasingly yes.

---

## Architecture Decisions That Will Age Well {#architecture-decisions}

Ramp made several architectural bets worth examining:

### 1. Modal for Sandboxed Execution

Using Modal for VM sandboxes with file system snapshots is clever infrastructure. Each session runs in complete isolation with the full development environment—Vite, Postgres, Temporal—pre-warmed. The key insight:

> "Repository images built every 30 minutes with cloned code and dependencies pre-installed. File system snapshots that freeze and restore state, reducing sync time to just 30 minutes of changes."

This matters because the dominant failure mode for coding agents is **context staleness**. By the time an agent finishes a task, the codebase may have moved. Ramp's snapshot approach bounds this problem to 30-minute windows, which is aggressive but practical.

### 2. OpenCode as Foundation

They chose [OpenCode](https://github.com/opencodefoundation/opencode) over building their own agent core. The reason:

> "It's structured as a server first with strong SDK typing and a comprehensive plugin system."

This is smart. The agent loop itself is becoming commoditized. The differentiation is in the integrations, skills, and organizational context you wrap around it. Ramp treats the core agent as infrastructure and competes on what surrounds it.

### 3. Cloudflare Durable Objects for Session State

Each session gets its own SQLite database via Durable Objects. This prevents cross-session contamination and scales horizontally without coordination overhead. It's a bet on many concurrent sessions being more valuable than deep shared state.

### 4. Authentication via GitHub, Not Custom Auth

> "Using GitHub authentication prevents unreviewed code merging by having users open PRs with their own tokens rather than as the app itself."

This is crucial and often missed. The agent can do work, but it can't merge its own work. All commits are attributable to real humans. This maintains the audit trail and prevents the nightmare scenario of agents merging agents' code without human review.

---

## The 30% Number and What It Actually Means {#the-30-number}

Ramp claims:

> "~30% of all pull requests merged to our frontend and backend repos are written by Inspect"

This is an extraordinary claim that deserves scrutiny. What does it actually mean?

**What it probably means:**
- 30% of merged PRs have Inspect as the code author
- Human engineers reviewed and approved these PRs
- The PRs passed CI/CD and code review

**What it doesn't tell us:**
- What's the complexity distribution? (Bug fixes vs. features vs. refactors)
- How much human editing happens post-agent?
- What's the bug rate on agent-authored code vs. human-authored?
- What percentage of *attempted* agent PRs get merged vs. discarded?

I suspect the reality is that Inspect handles a large volume of lower-complexity work—bug fixes, routine features, mechanical refactors—freeing humans for architecture decisions, complex debugging, and novel feature work. This is still valuable. It's just a different story than "agents write 30% of our code."

The honest framing: **Agents are becoming excellent at the reproducible, well-specified portions of software development.** The creative, ambiguous, high-judgment work remains firmly human.

---

## The Security Problem Nobody Wants to Talk About {#security-problem}

[Varun Badhwar's critique](https://www.linkedin.com/posts/vbadhwar_sdlc-activity-7416901057987121152--Mcu) of Ramp's post deserves amplification:

> "Security isn't mentioned once. No threat model. No discussion of blast radius. No guardrails for autonomous code changes."

This isn't an oversight specific to Ramp—it's an industry-wide blind spot. The entire "AI agents in SDLC" conversation is happening without serious security consideration.

### The Threat Model Nobody Writes

Consider what an agentic coding system has access to:

```
┌─────────────────────────────────────────────────────────────┐
│                    Agent Attack Surface                      │
├─────────────────────────────────────────────────────────────┤
│  Source Code Access      → Full codebase read/write         │
│  Secrets Exposure        → Env vars, API keys, credentials  │
│  External Integrations   → Sentry, Datadog, LaunchDarkly    │
│  Execution Environment   → Can run arbitrary commands       │
│  Network Access          → Can call APIs, fetch resources   │
│  Database Queries        → Telemetry and feature flag state │
└─────────────────────────────────────────────────────────────┘
```

The agent is, by design, a maximally capable actor in your system. The only thing preventing disaster is:
1. Model behavior (hoping it doesn't go rogue)
2. Human review (assuming reviewers catch everything)
3. Sandbox isolation (which must be perfect)

### Specific Risks

| Risk | Description | Mitigation Status |
|------|-------------|-------------------|
| Prompt injection via codebase | Malicious code comments could manipulate agent behavior | Largely unaddressed |
| Secrets exfiltration | Agent could encode secrets in code or logs | Assumed sandbox isolation |
| Subtle vulnerability introduction | Agent could introduce non-obvious security flaws | Depends on human review |
| Supply chain attacks | Agent could add malicious dependencies | Depends on human review |
| Denial of service | Runaway agents consuming resources | Rate limiting, presumably |

The uncomfortable truth: **We are deploying agents to production codebases before we have robust security models for their behavior.**

Ramp's post focuses on velocity and productivity. That's the narrative that sells internally. But someone at Ramp has thought about security—they're just not publishing it. Other organizations may be less thoughtful.

---

## Multiplayer: The Underrated Feature {#multiplayer}

Ramp's multiplayer approach is buried in the post but may be the most forward-looking decision:

> "Building multiplayer support required decoupling sessions from single authors and passing authorship data with each prompt. This enables teaching non-engineers, live QA sessions, and collaborative PR reviews."

This hints at where agents go next. Today, the mental model is:

```
Developer → Agent → Code
```

Ramp is building for:

```
Product Manager ─┐
Designer ────────┼─→ Agent → Code → Engineer Review
QA ──────────────┘
```

The agent becomes a translation layer between non-technical intent and technical implementation. A PM can describe a feature in Slack, the agent proposes an implementation, an engineer reviews it, and it ships.

This is much more disruptive to the software development model than "engineers get faster." It potentially changes *who* can contribute to a codebase and *how* work gets prioritized.

The Slack bot and Chrome extension integrations are early experiments in this direction. The Chrome extension is particularly clever—allowing visual changes to React apps through DOM inspection rather than requiring users to understand the codebase.

---

## Why Build vs. Buy Is the Wrong Frame {#build-vs-buy}

The tech press will likely frame Ramp's story as "Ramp builds instead of buys." This misses the point.

Ramp didn't build a complete agent from scratch. They:
- Used Modal for compute
- Used OpenCode for the agent core
- Used Cloudflare for session state
- Used existing MCP protocols for tool integration

What they built was the **integration layer**—the glue connecting off-the-shelf components to their specific context.

The real frame should be: **How much custom integration is your codebase worth?**

```
┌─────────────────────────────────────────────────────────────────┐
│                    Integration Spectrum                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Zero Config ─────────────────────────────────────→ Full Custom  │
│                                                                  │
│  Copilot         Cursor + Rules       Ramp Inspect               │
│  (out of box)    (MCP servers)        (custom agent)             │
│                                                                  │
│  ← Lower Ceiling                    Higher Ceiling →             │
│  ← Lower Investment                Higher Investment →           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

Most teams will be well-served by tools like Cursor with custom MCP servers and rules files. The Ramp approach—standing up entire infrastructure—only makes sense at scale with strong DevOps/platform teams and unique internal tooling worth integrating.

---

## What This Means for Engineering Organizations {#organizational-implications}

Several implications for how engineering orgs should think about 2026:

### 1. Platform Teams Become Critical

The competitive advantage isn't the agent—it's how well the agent is integrated with your systems. Platform engineering that makes agents effective is now load-bearing infrastructure.

### 2. Specification Quality Matters More

If agents handle more execution, the bottleneck shifts upstream to specification. Tickets, designs, and requirements that are clear and unambiguous will ship faster. Vague requirements will get stuck in human clarification loops.

### 3. Code Review Becomes the Skill

When 30% of PRs are agent-authored, code review is no longer "check your colleague's work." It's "validate AI output for correctness, security, and design alignment." This is a different skill set.

### 4. Junior Engineer Role Changes

The traditional "junior engineer does the routine work" model is disrupted when agents do routine work faster and cheaper. Junior engineers need to specialize faster—either becoming agent operators or focusing on domains agents struggle with.

### 5. Engineering Velocity Metrics Need Rethinking

If an agent opens 500 PRs that each require human review, is that velocity or overhead? Current metrics (PR count, cycle time) don't capture this nuance.

---

## Predictions {#predictions}

Based on this analysis, here are specific predictions:

### Near-Term (2026)

1. **Top-10 tech companies will each have internal agents rivaling Inspect by end of 2026.** The ROI math works at scale. Google, Meta, Stripe, Shopify, and others will build or heavily customize.

2. **"Agent integration engineer" becomes a real job title.** The work of connecting agents to internal systems, creating skills, and maintaining context is specialized enough to warrant dedicated roles.

3. **At least one major security incident will be publicly attributed to an AI agent.** Whether prompt injection, secret exposure, or subtle vulnerability introduction—it's a matter of when, not if.

### Medium-Term (2026-2027)

4. **Agents will primarily reduce team size on new projects rather than existing ones.** Greenfield projects will start with smaller teams + agents. Existing teams will use agents for augmentation, not replacement.

5. **The "30% of PRs" benchmark becomes table stakes.** Companies will compete on agent-authored PR percentages like they currently compete on deployment frequency.

6. **Non-technical roles will routinely initiate code changes via agent interfaces.** Product managers filing a Jira ticket that results in a PR, reviewed and merged without an engineer touching the code, will become normal for certain categories of work.

### Long-Term (2028+)

7. **The distinction between "using an agent" and "programming" will blur.** Writing a detailed spec that an agent implements is programming. The medium changes, not the essence.

8. **Software development economics will bifurcate.** Some categories (CRUD apps, standard integrations) become commodity-priced as agent efficiency approaches 100%. Complex systems work (distributed systems, performance engineering) retains premium pricing as agent limits become apparent.

---

## Key Takeaways

1. **Ramp's "it only has to work on your code" philosophy is the right frame.** General-purpose tools hit a ceiling. Custom integration unlocks the next tier of value.

2. **30% of PRs is impressive but likely skewed toward routine work.** This is still valuable—it just isn't "agents are writing most of our software."

3. **Security is the unaddressed elephant.** The industry is moving faster on capability than on safety. This will bite us.

4. **Multiplayer agent interfaces are the sleeper feature.** Enabling non-engineers to initiate code changes via agents is more disruptive than making engineers faster.

5. **The winning strategy is integrating deeply, not building entirely custom.** Use commoditized components (Modal, OpenCode, Cloudflare) and invest in the integration layer specific to your context.

6. **Prepare for a shift in what engineering work looks like.** More specification, more review, less routine implementation. The value is moving upstream.

---

## Sources

- [Why We Built Our Own Background Agent](https://builders.ramp.com/post/why-we-built-our-background-agent) - Ramp Builders Blog
- [Ramp Builds Internal Coding Agent That Powers 30% of Engineering Pull Requests](https://www.infoq.com/news/2026/01/ramp-coding-agent-platform/) - InfoQ
- [AI Agents in SDLC: Security Omission in Innovation](https://www.linkedin.com/posts/vbadhwar_sdlc-activity-7416901057987121152--Mcu) - Varun Badhwar, LinkedIn
- [Best Background Agents for Developers in 2026](https://www.builder.io/blog/best-ai-background-agents-for-developers-2026) - Builder.io
- [2026 Agentic Coding Trends Report](https://resources.anthropic.com/hubfs/2026%20Agentic%20Coding%20Trends%20Report.pdf) - Anthropic
- [Building Agents with the Claude Agent SDK](https://www.anthropic.com/engineering/building-agents-with-the-claude-agent-sdk) - Anthropic
- [Effective Harnesses for Long-Running Agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) - Anthropic
- [Enabling Claude Code to Work More Autonomously](https://www.anthropic.com/news/enabling-claude-code-to-work-more-autonomously) - Anthropic
