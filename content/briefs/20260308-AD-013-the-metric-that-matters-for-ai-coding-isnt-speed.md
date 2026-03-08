---
id: 20260308-AD-013
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
The right metric for AI coding isn't how much faster individual developers write code — it's the percentage of merged pull requests authored by agents.

## Draft Instructions
The argument: "developer productivity gains" is the wrong frame for evaluating AI coding tools at an organizational level. Individual latency metrics miss the real leverage. The companies getting the most out of AI coding agents measure organizational throughput: Ramp at ~30% of merged PRs authored by agents, Stripe at 1,000+ agent PRs per week, TELUS at 500K hours saved across 57K team members, Rakuten at 79% reduction in time-to-market. The metric that matters: what percentage of the work that ships is human-authored vs. agent-authored? Not "did my PR take 4 hours instead of 8?" but "what percentage of our merged PRs needed a human to write them?" Make the case that teams measuring the wrong thing are optimizing for the wrong thing. This reframing should feel provocative and practical.

## Sources
- research/reports/20260308-agentic-sdlc-big-team-leverage.md

## Related Items
- 20260308-AD-012

---

## Content Tree

### Post Excerpts (draft these, ready for write-post)

1. **The wrong metric angle:**
Most engineering leaders evaluate AI coding by asking "how much faster are our developers?" That's the wrong question. At Ramp, 30% of merged PRs are authored by agents. At Stripe, agents merge 1,000+ PRs per week. These companies don't measure speed. They measure what percentage of shipped code needed a human to write it. The difference between "my devs are 2x faster" and "30% of our output is agent-authored" is the difference between a convenience tool and an organizational capacity expansion.

2. **The invisible backlog angle:**
The biggest leverage of AI coding agents isn't making developers faster. It's clearing the work that never gets done. Dependency updates sitting for months. Security patches piling up. Flaky tests everyone routes around. Dead code nobody has time to clean. Each task has low value relative to its context-switching cost, so it never gets prioritized. Agents eliminate the context-switching cost. That work just starts getting done. And none of it shows up in "developer speed" surveys.

3. **The knowledge externalization angle:**
The companies with the highest percentage of agent-authored PRs all have one thing in common: they wrote everything down. OpenAI's Harness team treats the repo as the single system of record for engineering norms, architecture decisions, even team culture preferences. "Anything not written down is lost context." Your agent-authored PR percentage has a ceiling, and that ceiling is determined by how much of your engineering knowledge lives in people's heads vs. in the repo.

### Thread Potential
Yes. The article's argument compresses well into a 5-6 tweet thread:
1. Hook: "The wrong metric for AI coding"
2. The latency vs. throughput distinction
3. The data table (Ramp, Stripe, OpenAI, TELUS, Rakuten)
4. What the invisible backlog is
5. What infrastructure you need to move the metric
6. Where this goes in 18 months

### Series Connection
This could seed a new series around "AI engineering metrics" or "organizational AI leverage." The repo-knowledge article (AD-014) is a natural companion. Could also connect to the Stripe determinism article (AD-012) as part of a broader "what the best teams actually do" narrative.

### Thumbnail Concept
1. A dashboard or scoreboard visual showing "% Agent-Authored PRs" as the primary metric, with traditional metrics (velocity, cycle time) faded or crossed out in the background. Clean, minimal, dark background with a bright accent on the percentage number.
2. A split-frame comparison: left side shows a single developer at a screen (labeled "2x faster"), right side shows a fleet of parallel agents producing PRs (labeled "30% of output"). The visual contrast between one-person optimization and organizational throughput.
