---
title: The Metric That Matters for AI Coding Isn't Speed
status: draft
platform: x-article
thumbnail: pending
perspective: "The percentage of merged PRs authored by agents is the only metric that captures real AI coding leverage, and teams measuring individual developer speed are optimizing for the wrong thing."
sources:
  - research/reports/20260308-agentic-sdlc-big-team-leverage.md
content-id: 20260308-AD-013
---

Ramp hit 30% of merged PRs authored by agents within a couple months. Not 30% faster developers. 30% of the actual shipped code written by machines.

That distinction is the whole argument.

## The Wrong Metric Won

Most engineering leaders evaluate their AI coding investment by asking some version of: "How much faster are our developers now?" They survey the team. They look at time-to-merge for individual PRs. They track how many minutes Copilot saves per day. Then they report a tidy number to leadership. "Our developers are 2x faster."

That number is almost meaningless at the organizational level.

Individual speed improvements are real, but they measure the wrong axis. A developer who writes a PR in four hours instead of eight is still one developer writing one PR. They freed up four hours, sure. But the organizational output didn't fundamentally change. You got one PR, slightly sooner.

Now look at what's happening at companies that measure differently.

## What the Numbers Actually Show

| Company | What they measure | Result |
|---------|------------------|--------|
| Ramp | % of merged PRs authored by agents | ~30% |
| Stripe | Agent PRs merged per week | 1,000+ |
| OpenAI (Harness) | Lines of agent-authored code shipped | 1M lines across 1,500 PRs |
| TELUS | Hours saved across workforce | 500K hours across 57K team members |
| Rakuten | Time-to-market reduction | 79% (24 days down to 5) |

These are throughput metrics. They measure what the organization ships, not how fast one person types. And the gap between "individual speed" and "organizational throughput" is where the real leverage lives.

Stripe's engineers aren't coding faster. They dispatch agents for dependency updates, security patches, flaky test fixes, and maintenance work. Then they stay in flow on architectural problems that actually need a human brain. The result is 1,000+ additional PRs per week that wouldn't have existed otherwise. That's not a speed improvement. That's a capacity expansion.

## Why Latency Metrics Lie

The developer-speed framing has a subtle problem: it assumes the bottleneck is how fast humans type code. For most teams, it isn't.

The bottleneck is all the work that never gets prioritized. Dependency updates that sit for months. Security patches that pile up in a backlog. Flaky tests that everyone routes around instead of fixing. Dead code that accumulates because nobody has time for cleanup. Feature flags from two years ago that are still in the codebase.

This is the long tail of engineering work. Each individual task has low marginal value relative to its context-switching cost, so it never rises to the top of the sprint. It just sits there, compounding into technical debt.

Agents eliminate the context-switching cost. A scheduled agent can process SonarQube alerts and open fix PRs on Tuesday morning. Another can bump dependencies weekly, modifying code when API signatures change between versions. A third can scan for dead code and stale feature flags.

None of this shows up in "developer speed" metrics. All of it shows up in "percentage of merged PRs authored by agents."

## The Metric: % of Agent-Authored Merged PRs

Here's what I think engineering leaders should actually track: **what percentage of the PRs that merge into your codebase were authored by agents?**

This metric captures several things at once:

**It measures real output.** A merged PR passed code review, passed CI, and shipped. Unlike "time saved" or "lines generated," there's no ambiguity about whether value was created.

**It separates organizational leverage from individual convenience.** If I use Copilot autocomplete to write a function faster, my PR still counts as human-authored. The metric only moves when agents independently produce work that ships. That's the threshold that matters.

**It creates the right incentives.** Teams that optimize for this metric invest in the things that actually compound: sandbox infrastructure, deterministic quality gates, ticket-to-PR pipelines, comprehensive CLAUDE.md files. They build systems that let agents do real work autonomously, not just assist humans marginally.

**It's honest about where you are.** Most teams are at 0%. That's fine. But knowing you're at 0% when Ramp is at 30% gives you a concrete gap to close, not a vague aspiration to "adopt AI."

## What Moving This Metric Requires

You don't get to 30% agent-authored PRs by giving everyone a Copilot license. The companies that moved this number all invested in the same things:

**Sandboxed environments.** Agents need their own isolated workspaces with pre-warmed dev environments. Ramp pre-builds repository images every 30 minutes on Modal. Stripe spins up devbox VMs in under 10 seconds. Without this, agents either work on the developer's machine (blocking them) or can't run at all.

**Deterministic quality gates.** Stripe's most important architectural decision: the agent cannot skip linting or testing. Hardcoded scripts run unconditionally between every creative step. The LLM decides what code to write. The system decides whether that code meets quality standards. This is how you make probabilistic systems reliable.

**Ticket-to-PR integration.** The highest leverage comes when an agent can pick up a Linear issue, understand the codebase context, implement the change, and open a PR without a human typing a single prompt. GitHub Copilot's coding agent does this today. Cursor Automations can trigger on new Linear issues. The plumbing exists.

**Codified knowledge.** Here's the hard one. If your engineering conventions, architectural decisions, and code patterns live in people's heads or scattered Slack threads, agents can't access any of it. OpenAI's Harness team learned this: "anything not written down is lost context." The teams with the highest agent-authored PR percentages are the ones that most aggressively externalized their knowledge into repo-level documentation.

## The Counterargument, Honestly

The obvious pushback: "Not all PRs are equal. Comparing an agent's dependency bump to a human's architecture refactor is apples to oranges."

Fair. A 30% agent-authored PR rate doesn't mean 30% of engineering value comes from agents. The agent PRs tend to be smaller, more routine, and more mechanical. That's the point. They clear the backlog of necessary-but-low-creativity work so humans can focus entirely on the high-judgment problems.

But you do need to watch for metric gaming. If teams start breaking work into artificially small PRs to inflate the agent percentage, the metric becomes noise. Track it alongside merge quality signals (CI pass rate, review turnaround, post-merge revert rate) to keep it honest.

Another fair critique: some teams genuinely need individual speed more than organizational throughput. A three-person startup doesn't have a maintenance backlog problem. For them, "my developer ships features 2x faster" might actually be the right metric. This argument is aimed at teams of 10 or more, where the coordination costs and maintenance overhead start to dominate.

## Where This Goes

I think within 18 months, the percentage of agent-authored code will be the most tracked engineering metric at top-tier tech companies. More than velocity. More than cycle time.

The reason is simple: it directly measures organizational leverage. A company where 40-50% of merged PRs are agent-authored has a fundamentally different cost structure than one where agents are just autocomplete tools. That gap will show up in hiring economics, speed to market, and ability to maintain large codebases without proportionally large teams.

The teams that start measuring this now, even if they're at 0%, will be the ones that know what infrastructure to build. The ones still measuring developer speed will keep optimizing the wrong thing.
