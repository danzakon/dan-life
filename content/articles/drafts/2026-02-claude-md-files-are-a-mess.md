---
title: CLAUDE.md Files Are a Mess
status: draft
platform: x-article
---

# CLAUDE.md Files Are a Mess

The idea behind CLAUDE.md is good. Give your AI agent persistent context about your project so it doesn't start from zero every time. In theory, this solves a real problem. In practice, it creates a bunch of new ones that nobody is talking about.

Theo recently cited an ETH Zurich study showing that CLAUDE.md and AGENTS.md files actually reduce task success rates by about 3% while increasing inference costs by over 20%. Meanwhile, Vercel published data showing AGENTS.md hit a 100% pass rate where skills only managed 53%. Both of these findings are interesting, but they're arguing about the wrong thing. The real problems with these files aren't about model performance on benchmarks. They're about what happens when real teams try to use them on real codebases over real time.

## The naming problem

Every file is called the same thing. CLAUDE.md. Or AGENTS.md. You end up with a dozen files across your repo all named identically. You can't tell from the filename what's actually in it. Is this the one about testing conventions? Database patterns? Deployment rules? The only way to know is to check the path, and even then you're guessing.

Compare that to a file called `testing-conventions.md` or `database-patterns.md`. You know exactly what you're looking at. The name carries information. CLAUDE.md carries none.

## They sprawl

These files live wherever someone decides to drop them. Root of the repo, inside `src/`, next to specific modules, nested in component directories. The convention encourages this, because the idea is that each directory can have its own CLAUDE.md with context relevant to that part of the codebase.

What actually happens is that nobody knows where all of them are. New standards get written into one CLAUDE.md while contradicting standards already exist in another. You can't easily audit what rules your agent is operating under because they're scattered across the project. Try answering "what are all the coding standards in this repo?" when the answer is spread across fifteen files in twelve directories, all with the same name.

If these were managed as proper documents in a single location, you could actually maintain them.

## They force shared preferences on everyone

On a team, CLAUDE.md files get committed to the repo. That means one engineer's preferences for how Claude should behave get imposed on everyone else. Maybe you like verbose comments. Your coworker doesn't. Whoever writes the CLAUDE.md first wins, and now every engineer on the project is fighting their agent's behavior or adding exceptions.

This is different from shared standards, which teams agree on deliberately and document in one place. CLAUDE.md files accumulate organically. Someone adds a rule because they hit a bug. Someone else adds three more. Six months later the file is a grab bag of personal preferences, actual project standards, and stale instructions for a tech stack you've already migrated off of.

## They're Claude-specific in a multi-agent world

We're past the point where everyone uses one AI tool. People use Claude Code, Cursor, Copilot, Windsurf, and whatever shipped last week. A file called CLAUDE.md does nothing in Cursor. Your `.cursorrules` do nothing in Claude Code. If you use more than one tool, you're maintaining duplicate files with overlapping content and no shared format.

AGENTS.md was supposed to fix this by being tool-agnostic, but it hasn't meaningfully changed the situation. Each tool reads its own files, ignores the rest, and you end up maintaining parallel configurations.

## You can't control when they load

CLAUDE.md files are passive. They get injected into context automatically, every turn. You don't decide when the agent reads them. You don't decide which parts are relevant to the current task. Everything goes in, every time.

The ETH Zurich study found this is exactly what hurts performance. Agents are too obedient. They read a CLAUDE.md full of testing conventions, and then they apply those conventions even when you asked them to write a quick utility function. The irrelevant instructions compete for attention and sometimes steer the model in wrong directions.

The Vercel data seems to contradict this, but look closer. Their AGENTS.md worked because it contained compressed API documentation for new APIs the model had never seen. That's injecting knowledge the model literally doesn't have. That's a fundamentally different use case from "here are my code style preferences and directory structure," which the model can figure out on its own.

## What actually works better

I've been running a different approach: properly named markdown documents that live in a managed location, with a lightweight router that points the agent to the right doc at the right time.

Instead of CLAUDE.md files scattered everywhere, I have a `skills/` directory with files named for what they do. `research.md` for research workflows. `content-pipeline.md` for content creation. `postbridge.md` for social media scheduling. Each file is loaded when its skill is invoked, not passively injected into every conversation.

The advantages:

**You know what each file does from the name.** No more opening a CLAUDE.md to figure out what's in it.

**They're managed in one place.** I can see all of them, audit them, update them, and know exactly what standards exist across the whole system.

**They load on demand.** The agent gets the context it needs for the current task, not everything all at once. This keeps the context window clean and avoids the attention dilution the ETH Zurich study identified.

**They're agent-agnostic.** A markdown file describing a workflow works with any agent. I symlink the same skills directory to Claude Code, Cursor, and anything else I use. One set of docs, every tool.

## When CLAUDE.md is fine

I'm not saying the concept is useless. A small root-level file with a handful of universal directives is fine. Things like "this repo uses pnpm, not npm" or "always run tests before committing." Three to five lines of truly universal, non-discoverable information that applies to every task.

The problem is that nobody stops there. The file grows. Rules accumulate. Preferences creep in. And before long you have a 200-line file that the model reads every single turn, most of which is irrelevant to what it's actually doing.

## The real issue

The theory behind CLAUDE.md is sound: give the agent context so it makes better decisions. But the implementation encourages patterns that fall apart on teams and at scale. Same-name files everywhere, no central management, passive loading of everything, tool-specific naming, and organic accumulation of stale rules.

If you're going to invest time in context engineering, invest it in well-named documents, managed in one place, loaded when they're relevant. Your agent will perform better, your team won't fight over whose preferences win, and you'll actually be able to answer the question "what rules is my agent following right now?"
