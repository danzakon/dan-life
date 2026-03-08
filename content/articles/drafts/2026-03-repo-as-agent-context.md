---
title: "If It's Not in the Repo, Your Agents Can't See It"
status: draft
platform: x-article
thumbnail: pending
perspective: "Tacit engineering knowledge has always had a cost, but AI agents make that cost visible and quantifiable. Teams that codify what they know into the repo will get disproportionately better results from agents."
sources:
  - research/reports/20260308-agentic-sdlc-big-team-leverage.md
content-id: 20260308-AD-014
---

# If It's Not in the Repo, Your Agents Can't See It

OpenAI's Harness team shipped an internal product. One million lines of code across 1,500 pull requests, zero manually written lines, built entirely by Codex agents over five months. Along the way, they learned something that had nothing to do with model capability: "anything not written down is lost context."

They started treating the repo as the single system of record for everything. Product principles. Engineering norms. Architecture decisions. Team culture preferences. All of it, in the codebase.

Most engineering teams have not caught up to this. And it is costing them.

## The Tacit Knowledge Tax

Every engineering organization runs on knowledge that lives outside the codebase. You know this because you have seen it:

- The naming convention your team agreed on in a Slack thread six months ago
- The reason you chose Postgres over DynamoDB, discussed in a meeting nobody documented
- The "we never deploy on Fridays" rule that exists only as tribal knowledge
- The architectural boundary between the billing service and the user service, drawn on a whiteboard and photographed by one person
- The fact that the `legacy_auth` module is deprecated but still handles 30% of traffic, so don't touch it
- The performance implications of querying the orders table without a date range filter

Every senior engineer on your team carries dozens of these in their heads. Historically, the cost of this tacit knowledge was slow onboarding, bus factor risk, and the occasional production incident when someone didn't know the unwritten rule.

Those costs were real but tolerable. You could onboard a new hire in a few weeks. The senior engineer who knew everything was usually available on Slack.

AI agents changed the math.

## Agents Hit a Wall You Can't See

When you dispatch an agent to implement a feature, fix a bug, or refactor a module, it starts by reading files. It reads the code. It reads the tests. It reads whatever documentation you have committed. Then it does the work based on what it found.

Here is what it cannot do: ask the senior engineer on your team why you chose that particular API design. Scroll through Slack history to find the thread where someone explained the migration strategy. Remember the standup where the team decided to deprecate that service.

The agent operates on what is written down, in the repo, right now. Everything else is invisible.

This means every piece of engineering knowledge that lives in someone's head or a Slack thread is directly reducing the quality of your agent's output. Not theoretically. Measurably. The agent that doesn't know about your naming conventions will use its own. The agent that doesn't know about the deprecated module will build on top of it. The agent that doesn't know you chose Postgres for a specific reason will suggest switching to something else.

I've watched this happen. An agent produces a technically correct PR that violates three team conventions nobody wrote down. The review takes longer than if a human had written it from scratch. The team concludes "agents don't understand our codebase" and dials back their usage.

The agents understood the codebase fine. They didn't understand the decisions behind it, because those decisions were never committed.

## What Should Be in the Repo (But Usually Is Not)

Most teams have a README and maybe some API docs. Here is what actually matters for agent context:

**Architecture decisions.** Why you chose this database, this framework, this deployment model. Not just what you use, but why, and what alternatives you rejected. Architecture Decision Records (ADRs) are the established format, but even a simple markdown file works.

**Naming conventions and code style beyond what a linter catches.** Your linter enforces semicolons and indentation. It does not enforce that you call them "organizations" not "companies," that boolean variables start with `is_` or `has_`, or that API endpoints follow a specific resource naming pattern.

**Module boundaries and ownership.** Which team owns which service. Where the boundaries are between modules. What should be a separate service versus part of an existing one. The dependencies that are intentional versus the ones that are tech debt.

**Operational knowledge.** Don't query this table without a date filter. This service has a 5-second timeout you need to account for. The staging environment doesn't have the same feature flags as production.

**Team preferences.** We prefer composition over inheritance. We use the repository pattern for data access. We write integration tests, not unit tests, for API endpoints. Error messages should be user-facing, not developer-facing.

**Context that would take a new hire weeks to absorb.** If a competent engineer joining your team would need to learn it, write it down.

## CLAUDE.md and AGENTS.md: The Practical Solution

The emerging pattern for codifying this knowledge is simple. Files in your repo that agents read at the start of every session.

Anthropic's Claude Code uses `CLAUDE.md`. Cursor uses `.cursorrules`. The broader ecosystem is converging on `AGENTS.md` as a vendor-neutral standard. The format matters less than the habit.

Ramp, whose background coding agent now authors roughly 30% of all merged PRs, built their entire agent infrastructure around rich repository context. Their agents have access to structured documentation about the codebase, conventions, and operational constraints before they write a single line of code.

Here is what a useful `CLAUDE.md` looks like in practice:

```markdown
# Project Context

## Architecture
We use a modular monolith with clear domain boundaries.
Services communicate through an internal event bus, not direct imports.
The billing module is the exception. It has direct access to the user
module for historical reasons. Do not extend this pattern.

## Conventions
- API endpoints: /api/v1/{resource} (plural nouns, no verbs)
- Database columns: snake_case, timestamps are always UTC
- Error responses: { "error": { "code": "THING_NOT_FOUND", "message": "..." } }
- We use the Result pattern for operations that can fail. No throwing in business logic.

## Do Not Touch
- legacy_auth/ is deprecated but still handles OAuth for mobile clients.
  Route new auth work through auth_v2/ instead.
- The orders table has no index on customer_id alone.
  Always include a date range in queries or you will take down the read replica.

## Testing
- Integration tests over unit tests for API endpoints
- Use the test factory at test/factories/ rather than building fixtures inline
- The CI pipeline runs tests in parallel. Tests must not depend on execution order.
```

This takes maybe an hour to write. The return on that hour compounds every time an agent reads it.

## The Compounding Effect

Stripe's internal agents ("Minions") merge over 1,000 pull requests weekly. Their architecture wraps a deterministic harness around the agent, including context engineering as the first layer. They use deterministic prefetching to load relevant documentation, conventions, and constraints before the agent begins creative work.

OpenAI's Harness team went further. They codified product principles, engineering norms, and even team culture preferences into the repo. The result was agents that could operate without constant human correction, because the correction was already embedded in the context.

This is where the compounding happens. Every convention you document prevents a class of review comments on every future agent-generated PR. Every architecture decision you record prevents the agent from relitigating it. Every operational constraint you write down prevents a production incident.

The teams that figure this out early will pull ahead in ways that are hard to reverse. An organization with a deeply documented codebase gets better agent output, which generates fewer review comments, which means faster merges, which means more capacity, which means more time to document further. The flywheel is real.

## The Uncomfortable Implication

This is fundamentally a cultural shift, not a tooling problem. The Thoughtworks analysis of agentic development puts it bluntly: knowledge codification is a prerequisite, not a nice-to-have. "If it is not in the repo, it does not exist for agents."

Most engineering cultures treat documentation as a chore. Something you do after the real work. Something that gets stale and nobody updates. That attitude was survivable when humans could compensate with tribal knowledge.

It is not survivable in an organization that wants to get meaningful output from AI agents. The teams that treat their repo as the single source of truth for all engineering knowledge, not just code, will be the ones that actually achieve the 30%+ agent-authored PR rates that companies like Ramp are reporting.

The teams that don't will keep wondering why their agents produce mediocre work.

Start with one file. One `CLAUDE.md` in your most active repository. Write down the ten things a new engineer would need to know. Commit it. Watch what happens to your agent output.

Then do the next repo.
