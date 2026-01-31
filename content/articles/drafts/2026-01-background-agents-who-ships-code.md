---
title: Your Coding Agent Should Be a Master of Your Stack, Not a Generalist
status: draft
platform: blog
---

# Your Coding Agent Should Be a Master of Your Stack, Not a Generalist

Ramp quietly dropped a blog post that most people will misread. The headline stat is that 30% of their merged PRs come from an AI agent. The tech press will focus on that number. They'll miss the more important insight buried in the details.

Ramp built their own agent. Not from scratch, but customized deeply for their specific codebase. And that decision reveals where this whole space is heading.

## The Line That Matters

Here's the sentence that should reframe how you think about coding agents:

> "We built Inspect because owning tooling enables building something more powerful than off-the-shelf alternatives... it only has to work on your code."

Read that last part again. It only has to work on your code.

Every major coding agent, Cursor, Copilot, Claude Code, Devin, is built to work reasonably well across millions of codebases. That's the product requirement. They need to handle Python shops, Ruby shops, monorepos, microservices, legacy code, greenfield projects. All of it. The business model demands generalization.

Ramp asked a different question. What if we built an agent that only needed to work on one codebase? Ours.

## Why Specialization Compounds

When your agent is a generalist, it reasons from first principles constantly. It reads your code, infers your patterns, makes educated guesses about your conventions. Sometimes it gets things right. Sometimes it suggests a logging approach you don't use, or a testing pattern that doesn't match your setup, or an abstraction that fights against your architecture.

When your agent is a specialist, it knows. Not infers. Knows.

Ramp's agent connects to Sentry, Datadog, LaunchDarkly, their internal tools. It understands their feature flag system. It can query their telemetry. It knows their internal abstractions. It follows their exact style conventions.

The compound effect of this is significant. A PM asks for a feature. The agent doesn't need to be told how Ramp handles logging, or error tracking, or gradual rollouts, or analytics. It already knows. It writes code that looks like a Ramp engineer wrote it because it has internalized what Ramp code looks like.

General-purpose agents give you code that compiles. Specialized agents give you code that belongs.

## The Architecture That Makes This Work

Ramp made several infrastructure bets worth understanding.

They use Modal for sandboxed execution. Each agent session runs in a VM with the full development environment pre-warmed: Vite, Postgres, Temporal, everything. Repository images rebuild every 30 minutes with fresh code and dependencies. This bounds the context staleness problem. By the time an agent finishes a task, the codebase has moved at most 30 minutes.

They chose OpenCode for the agent core rather than building their own. Why? Because the agent loop itself is becoming commoditized. The differentiation isn't in how you implement tool calls or manage context windows. It's in what you connect the agent to.

Each session gets its own SQLite database via Cloudflare Durable Objects. No cross-session contamination. Horizontal scaling without coordination overhead.

And critically: all commits go through GitHub authentication with user tokens. The agent can do work, but it can't merge its own work. Every change is attributable to a real human who reviewed and approved it.

This is infrastructure that exists to make specialization possible. The agent core is off-the-shelf. Everything around it is custom.

## Elite Companies Will Build This

Here's the prediction I'm confident about: every company with more than 50 engineers will either build something like this or fall behind.

The ROI math is straightforward. If your agent is 20% more effective because it understands your systems deeply, and you have 100 engineers, that's 20 engineer-equivalents of productivity. At that scale, investing in custom agent infrastructure pays for itself quickly.

Google will build this. Meta will build this. Stripe, Shopify, Airbnb. Any company with meaningful scale and a differentiated codebase will conclude that general-purpose agents leave value on the table.

The question for smaller companies is where to draw the line. You probably can't justify Ramp's full infrastructure investment. But you can move along the spectrum.

```
Zero Config                                              Full Custom
    |                                                          |
    |     Copilot       Cursor + MCP      Ramp Inspect        |
    |   (out of box)    (some custom)    (deep custom)        |
    |                                                          |
    └──────────────────────────────────────────────────────────┘
         Lower investment                    Higher investment
         Lower ceiling                       Higher ceiling
```

Most teams should be somewhere in the middle. Use a general-purpose agent as the foundation. Add MCP servers that connect to your systems. Write rules files that encode your conventions. Feed it documentation about your architecture. Each layer of customization makes the agent more native to your environment.

## What This Means for You

If you're an engineer thinking about how to get more out of coding agents, the takeaway is clear: invest in specialization.

Don't just drop Cursor into your workflow and hope for the best. Teach it your codebase. Write rules that capture your patterns. Build MCP integrations for your internal tools. The more context your agent has about how your team works, the more useful its output becomes.

If you're leading an engineering team, think about this as platform work. The agent itself is a commodity. The integration layer is where you compete. Teams that make their agents native to their environment will ship faster than teams running generic tools with default settings.

And if you're at a company with real scale, watch what Ramp did carefully. They didn't build an agent from scratch. They assembled one from commoditized components and invested heavily in the connective tissue. Modal for compute. OpenCode for the core. Cloudflare for state. Custom integrations for everything else.

That's the playbook. The agent core is table stakes. The specialization is the advantage.

## The Ceiling on General-Purpose

There's a reason Cursor and Copilot feel like they plateau. You get a productivity boost when you first adopt them. Then you hit a ceiling. The agent keeps making suggestions that almost work but need adjustment. It keeps forgetting your conventions. It keeps proposing patterns you've explicitly decided against.

That ceiling exists because general-purpose agents optimize for the average codebase. Yours isn't average. It has history, decisions, tradeoffs, context that no generic model can infer.

Ramp's 30% number isn't impressive because of the percentage. It's impressive because those PRs presumably need less human correction, follow existing patterns more closely, and integrate with internal systems correctly. The agent isn't just generating code. It's generating code that fits.

That's the difference between an agent that can help and an agent that actually ships.

## Where This Goes

The current generation of coding agents will look primitive in two years. Not because the models will be dramatically smarter, though they will be. Because the integration patterns will mature.

Today, customizing an agent for your codebase requires real engineering effort. Standing up MCP servers, writing rules, maintaining context. Tomorrow, this will be productized. You'll point a tool at your repo, your Jira, your Sentry, your CI system, and it'll build the integration layer automatically.

When that happens, the companies that invested early in understanding how to specialize their agents will have a head start. They'll know what integrations matter. They'll have learned what context makes agents effective. They'll have developed intuitions that new adopters will need to build from scratch.

Ramp is early to this. They're figuring out what works through direct investment. Most companies are waiting for off-the-shelf solutions.

Both strategies can work. But the early movers will have compounding advantages, better internal tooling, more institutional knowledge, engineers who understand how to think about agent-assisted development.

The generalist agent era is ending. The specialist agent era is beginning. The companies that recognize this shift will pull ahead. The ones that keep waiting for general-purpose tools to magically understand their codebase will keep wondering why the productivity gains plateau.

Your agent should be a master of your stack. That's the insight. Everything else follows from there.
