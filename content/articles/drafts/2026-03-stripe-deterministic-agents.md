---
title: "Stripe's Trick for Reliable AI Code: Make the Agent Skip Nothing"
status: draft
platform: x-article
thumbnail: pending
perspective: "Probabilistic AI systems become reliable when you wrap them in deterministic process, removing the LLM's ability to skip quality checks."
sources:
  - research/reports/20260308-agentic-sdlc-big-team-leverage.md
content-id: 20260308-AD-012
---

Stripe merges over 1,000 agent-generated pull requests every week. Engineers send a Slack message, a production-ready PR comes back, and they never touch it again.

That number sounds reckless. A thousand PRs from an AI, merged without babysitting? Most teams can barely trust an LLM to write a clean function without reviewing every line.

So how does Stripe get away with fire-and-forget?

The answer has nothing to do with a better model. Stripe's agents run on a fork of Goose, an open-source coding tool. The secret is in the six layers of infrastructure wrapped around it. And the most important layer is one that most teams get wrong.

## The mistake everyone makes

In a standard agent workflow, the LLM decides everything. It decides when to write code, when to lint, whether to run tests, and when to commit. The agent has full discretion over the entire development loop.

This sounds reasonable. The LLM is smart. Let it figure out the right sequence.

But here is what actually happens: the agent skips steps. Not maliciously. Not even consistently. It just... sometimes doesn't lint. Sometimes doesn't run the tests it should. Sometimes commits code that would have failed a check it decided to skip. Probabilistic systems produce probabilistic behavior, and "usually runs the linter" is not good enough for production code at scale.

Most teams respond to this by adding more instructions. "Always run lint before committing." "Never skip tests." They're trying to solve an architecture problem with prompting. It doesn't work reliably, because the LLM is still the one deciding whether to follow those instructions.

## Stripe's fix: remove the decision

Stripe's architecture, which they call the "interleaved architecture," takes a different approach. Instead of asking the LLM to decide when to run quality checks, it removes that decision entirely.

Creative work alternates with deterministic gates. The LLM writes code. Then a hardcoded script runs the linter, unconditionally. The LLM fixes issues. Then a hardcoded script runs the relevant tests, unconditionally. The LLM finalizes changes. Then a hardcoded script commits, unconditionally.

The agent cannot skip quality checks because quality checks are not the agent's responsibility.

```
┌──────────────────────────────────────────┐
│         INTERLEAVED ARCHITECTURE         │
│                                          │
│   LLM writes code          (creative)    │
│         │                                │
│         ▼                                │
│   Linter runs              (hardcoded)   │
│         │                                │
│         ▼                                │
│   LLM fixes lint errors    (creative)    │
│         │                                │
│         ▼                                │
│   Tests run                (hardcoded)   │
│         │                                │
│         ▼                                │
│   LLM fixes failures      (creative)    │
│         │                                │
│         ▼                                │
│   Git commit               (hardcoded)   │
│                                          │
│   Creative steps:  LLM decides           │
│   Gate steps:      Always execute         │
└──────────────────────────────────────────┘
```

This is the entire insight. The LLM handles what LLMs are good at: reasoning about code, diagnosing errors, generating solutions. The deterministic infrastructure handles what scripts are good at: running the same checks the same way every time.

## The circuit breaker

There is a second piece that matters just as much. Stripe caps their agents at two CI rounds.

If the agent writes code, the tests fail, the agent tries to fix it, and the tests fail again, the agent stops. It surfaces the problem to a human. No third attempt.

This solves a failure mode I've seen wreck agent workflows: the spiral. When an agent fails a test and tries to fix it, its context fills up with error logs. The fix attempt often introduces new errors. The next attempt has even more noise in context. After three or four rounds, the agent is effectively working blind, generating increasingly desperate patches against a wall of error messages.

Stripe calls this the "gutter." Two rounds is the cap because if the agent can't fix it in two tries, a third attempt is statistically unlikely to succeed and will only burn compute while degrading output quality.

The constraint feels aggressive. But that's the point. A hard limit forces the system to be honest about what agents can and cannot handle. And the constraint scales better than hope.

## What this actually looks like in production

The interleaved architecture is one layer of six in Stripe's agent platform. The full stack:

1. **Context engineering.** Before the agent starts, deterministic prefetching pulls in Slack threads, stack traces, and documentation. The LLM doesn't decide what context it needs. The system provides it.

2. **Curated tool access.** Stripe has 400+ internal tools exposed via MCP, but any given task gets roughly 15. The agent never sees the full catalog. Fewer tools means fewer hallucinated tool calls.

3. **Sandbox isolation.** Every agent run gets a fresh VM. Zero internet access, zero production access. If the agent gets prompt-injected through a code comment, it can't exfiltrate data because it can't reach anything outside the sandbox.

4. **Interleaved architecture.** The creative/deterministic alternation described above.

5. **Tiered feedback with a hard cap.** Local lint in under 5 seconds. Selective CI runs only the relevant tests from their suite of 3 million. And the two-round cap if self-healing fails.

6. **Integration.** Slack triggers, "Fix with Minion" buttons in the bug tracker, branch creation, PR submission. The full loop from signal to shipped PR, automated end to end.

During Stripe's internal Fix-It Week, their agents resolved 30% of all bugs autonomously. Not 30% attempted. 30% resolved. These are dependency updates where the agent modifies code for breaking API changes, flaky test fixes, security patches. The kind of work that sits in backlogs for months because no individual task justifies the context-switching cost.

## The pattern, not the stack

You don't need six layers of custom infrastructure to apply this. The core pattern is simple: separate creative decisions from quality gates, and never let the LLM control the gates.

If you're using Claude Code, Cursor, or any agent tool today, you can implement the interleaved architecture in your own workflow. Wrap agent code generation steps in a script that unconditionally runs your linter and test suite after every change. Don't instruct the agent to "always run tests." Make it structurally impossible to skip them.

Add a retry cap. Two attempts is a reasonable default. If the agent can't fix a failing test in two rounds, it escalates. You can adjust the number, but having a number is what matters.

The deeper lesson from Stripe's system is about where to draw the line between probabilistic and deterministic. LLMs are powerful but unreliable decision-makers for process control. They're excellent at creative work within constraints. The teams that figure out where to draw that line will build agent systems that actually scale. The teams that let the LLM decide everything will keep wondering why their agents are inconsistent.

Stripe didn't build a smarter agent. They built a smarter cage.

---

## Content Tree

### Post Excerpts (draft these — ready for write-post)

1. **"The agent can't skip what the agent doesn't control"**

Most teams try to make agents reliable by adding more instructions. "Always lint." "Never skip tests." This is prompt engineering for process control, and it fails the same way all prompt engineering fails: probabilistically.

Stripe took a different approach. They removed the decision entirely. Creative steps (writing code, fixing bugs) alternate with deterministic gates (linting, testing, committing) that execute unconditionally. The agent cannot skip quality checks because quality checks are not the agent's job.

The result: 1,000+ PRs merged weekly, fire-and-forget. The trick wasn't a better model. It was better architecture.

2. **"The two-round rule"**

Stripe caps their AI agents at two CI attempts. If the agent can't fix a failing test in two tries, it stops and surfaces the problem to a human.

Why? Because of what they call the "gutter." After a couple failed attempts, the agent's context fills with error logs. Each fix attempt introduces new errors. The agent spirals, generating increasingly desperate patches against a wall of noise.

Two rounds. Then escalate. The constraint sounds aggressive, but it scales better than hope.

3. **"Stripe didn't build a smarter agent"**

Stripe merges 1,000+ AI-generated PRs every week using a fork of an open-source tool. The model isn't special. The infrastructure is.

Six layers: deterministic context prefetching, curated tool access (15 tools per task from a catalog of 400+), sandbox isolation with zero internet access, an interleaved architecture that never lets the LLM skip quality checks, a two-round CI cap, and end-to-end integration from Slack to merged PR.

The bottleneck to reliable AI code isn't model intelligence. It's the deterministic process you wrap around it.

### Thread Potential

Yes. The six-layer architecture naturally decomposes into a thread:

1. Hook: Stripe merges 1,000+ agent PRs/week. Here's the architecture that makes it work.
2. Layer 1-2: Context engineering + curated tools
3. Layer 3: Sandbox isolation ("isolation IS the permission system")
4. Layer 4: The interleaved architecture (the key insight)
5. Layer 5: The two-round cap and the "gutter" problem
6. Layer 6: End-to-end integration
7. Closer: The pattern you can apply today without building custom infra

### Series Connection

Could seed a new series on "agent reliability patterns" or "deterministic AI architecture." This article, plus the sandbox/security piece (AD-007) and the demo-to-production gap (AD-011), form a natural trilogy about what it takes to make AI agents production-ready.

### Thumbnail Concept

1. A split visual: one side shows a tangled, chaotic flowchart (agent deciding everything), the other shows a clean, alternating pattern of colored blocks (creative steps in one color, deterministic gates in another). The contrast between chaos and structure.

2. A conveyor belt / assembly line metaphor: code blocks moving through quality checkpoints (lint, test, commit) with robotic arms representing the deterministic gates. Industrial, mechanical, reliable.
