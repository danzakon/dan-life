---
title: You Are Responsible for Your Own Slop
status: draft
platform: blog
---

# You Are Responsible for Your Own Slop

AI got dramatically better this year. And somehow, the average quality of AI-assisted work got worse.

That sounds contradictory. It isn't. The better AI gets, the more tempting it is to do less. To type a one-line prompt, accept the first output, and ship it. The tool improved. The human in the loop got lazy.

Here's the thing nobody wants to hear: if you paste an AI-generated document into an email, a codebase, a report, a legal brief, or a blog post, and it's wrong, shallow, or embarrassing, that's on you. Not the model. Not the prompt. You. You clicked send.

The AI didn't publish that hallucinated statistic. You did. The AI didn't ship that buggy function without reading it. You did. The AI didn't send that proposal full of generic platitudes to your client. You did.

And yet the default workflow for most people is still: type something vague, get something back, use it.

## The One-Shot Trap

Most people use AI like a vending machine. Insert prompt, receive output. Maybe they'll try again if the first result is obviously bad. But the mental model is transactional: I asked, it answered, we're done.

This is the worst possible way to use these tools.

A one-shot prompt produces one-shot quality. You're getting the model's generic best guess at what you probably meant, without any of the context that lives in your head. No wonder it sounds like every other AI output. You gave it nothing to work with.

Think about how you'd work with a smart colleague. You wouldn't walk up to someone, say "write me a marketing strategy," and expect something usable. You'd explain the context. You'd discuss the audience. You'd debate the approach. You'd review drafts together. You'd push back on weak sections. You'd go through multiple rounds.

That's how AI works well too. The difference is that AI can do this at any hour, with infinite patience, across any domain. You have the best collaborator in history available 24/7, and you're using it like a search engine with fancier output.

## What Ownership Actually Looks Like

Taking ownership of AI output means your final deliverable is the product of your thinking, amplified by the AI. Not the AI's thinking, rubber-stamped by you.

Here's what that looks like in practice.

**Before you prompt, you think.** What specifically do I need? What does good look like? What constraints matter? What have I already decided? The clearer your input, the better the output. A paragraph of context beats a sentence of instruction.

**You write real prompts.** Not "write me an article about X." Instead, you write detailed paragraphs explaining your perspective, your audience, the tone you want, the points that matter, the things you explicitly don't want. Your prompt should be a document, not a tweet. If your prompt is shorter than the output you're expecting, you're probably not giving enough direction.

**You iterate relentlessly.** The first output is a starting point, not a finished product. You read it critically. You push back. "This section is too vague. What specific evidence supports this claim? The tone here is too formal. You're missing the counterargument. This structure buries the lead." You go back and forth until the output reflects your actual thinking, not a generic approximation of it.

**You use AI to understand, not just to produce.** Before writing that architecture doc, you spend an hour discussing the tradeoffs with an AI. Before drafting that contract, you have the AI explain every clause and flag potential issues. Before building that feature, you talk through the edge cases. The goal isn't just getting output. It's getting understanding. When you deeply understand what you're producing, the quality shows.

**You build systems, not one-off prompts.** A prompt you use once teaches you nothing. A prompt you've refined over twenty uses becomes a precision instrument. You develop prompt templates for the kinds of work you do regularly. A research prompt. A writing prompt. A code review prompt. A "challenge my thinking" prompt. Each one tuned through experience.

## The New Skills Nobody Talks About

Everyone talks about prompt engineering. Almost nobody talks about the broader skill set that separates people who use AI well from people who produce slop.

**Skimming large documents quickly.** AI generates volume. The ability to scan a 3,000-word output in two minutes, identify the three paragraphs that matter, and zero in on what needs to change is critical. If you can't skim effectively, you'll either read everything slowly (and never iterate) or read nothing carefully (and ship garbage).

**Writing expressively in natural language.** Your prompts are only as good as your ability to articulate what you want. People who write clearly and think precisely get dramatically better AI output than people who communicate vaguely. The irony is that AI makes human writing ability more important, not less. Your words are now a programming language.

**Thinking critically under the pressure of convenience.** AI gives you a plausible answer instantly. The cognitive pull to accept it is enormous. The skill is pausing, questioning, probing. Does this actually make sense? Is this supported by evidence? Am I being told what I want to hear? Confirmation bias was already a problem. AI makes it worse because the confirming voice sounds confident and articulate.

**Iterating on markdown and structured text.** So much AI collaboration happens in documents. The ability to receive a draft, restructure it, annotate it, and send it back for revision is a workflow skill that barely existed three years ago. Treat AI output like a Google Doc from a colleague, not like a finished deliverable from a consultant.

**Challenging the AI explicitly.** Most people are polite to AI. They accept outputs they're unsure about because confrontation feels weird, even with a machine. Get over it. "I disagree. Here's why." "This is wrong. The actual situation is..." "You're being too generic. Be more specific about..." The best outputs come from productive friction, not passive acceptance.

## The Thought Partner Model

The highest-leverage way to use AI isn't generation. It's conversation.

Before I write anything significant, I talk it through with an AI. Not "write this for me" but "here's what I'm thinking, poke holes in it." I use it as a sounding board, a devil's advocate, a research assistant, and a first reader. By the time I actually produce the deliverable, my thinking is sharper than it would have been working alone.

This works for everything, not just writing. Engineers can discuss system designs at length before writing a line of code. Product managers can stress-test requirements before locking a spec. Lawyers can explore edge cases in a contract before sending it to the client. Founders can pressure-test business models before pitching investors.

The pattern is the same everywhere:

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Research   │────▶│   Discuss    │────▶│   Produce    │
│  (AI-aided)  │     │  (with AI)   │     │ (AI-aided)   │
└──────────────┘     └──────────────┘     └──────────────┘
       │                    │                     │
       ▼                    ▼                     ▼
  You understand       You decide            You own it
  the landscape        the approach           completely
```

Research. Discuss. Produce. In that order. Most people skip straight to "produce" and wonder why the output is mediocre.

The research phase alone changes everything. Ask an AI to compile a report on any topic you're about to make a decision about. Read it. Ask follow-up questions. Challenge the findings. Now you're working from a foundation of understanding that would have taken days to build manually. Your decisions are better. Your output is sharper. Not because AI is smart, but because you bothered to learn before you built.

## The Prompts That Matter

You don't need a hundred prompts. You need a handful that you use constantly and refine over time.

**The Self-Interviewer.** Before producing anything, have the AI interview you about what you want. "Ask me ten questions about this project so you understand my goals, constraints, and preferences before we start." This surfaces assumptions you didn't know you had. It forces you to articulate your thinking. And it gives the AI the context it needs to actually help.

**The Devil's Advocate.** After you've developed a position, run it through opposition. "Here's my plan. What are the three strongest arguments against it? What am I not seeing? Where will this fail?" You won't always agree with the pushback. But you'll always think more clearly because of it.

**The Research Compiler.** When facing a decision, have the AI survey the landscape. "I need to choose between X and Y. Research both approaches. Give me a comparison including tradeoffs, real-world examples, and common failure modes." Then read the output critically. AI research isn't always right, but it's a remarkable starting point.

**The Draft Reviewer.** Once you have output, have the AI review it from a specific perspective. "Review this as a skeptical customer." "Review this as a senior engineer who's seen too many over-engineered systems." "Review this as my boss who only has two minutes to read it." Each lens catches different problems.

## The Part Nobody Wants to Hear

All of this is more work than one-shotting. Significantly more.

That's the point.

The people producing great work with AI aren't saving time on thinking. They're spending the same amount of time thinking, but getting dramatically more out of it. The AI didn't remove the work. It changed the nature of the work, from mechanical production to critical thinking and clear communication.

If you thought AI was going to let you stop thinking, you were always going to produce slop. AI is an amplifier. It amplifies good thinking into great output. It amplifies lazy thinking into confident-sounding garbage.

The uncomfortable truth is that being good at AI requires being good at thinking. Being good at communicating. Being good at knowing what you want. These are the same skills that made people effective before AI. They just matter more now because the ceiling is higher and the floor is lower.

A skilled person with AI produces work that would have been impossible alone. An unskilled person with AI produces work that looks polished but crumbles under scrutiny. The gap between these two outcomes is not the tool. It's the person.

## Own It

Your AI's output is your output. Every hallucination you ship, every generic paragraph you send, every shallow analysis you present, that has your name on it.

The tools will keep getting better. Prompts will get more sophisticated. Context windows will grow. Agents will handle more complex workflows. None of that absolves you of responsibility for the final product.

Read what the AI gives you. Think about whether it's right. Push back when it isn't. Iterate until it reflects your actual thinking. Develop systems for getting consistently good output. Invest in the human skills that make AI collaboration work: clear writing, critical thinking, domain knowledge, and the discipline to not just ship the first thing that comes back.

The slop isn't the AI's fault. It's yours. And the fix isn't a better model. It's you, actually doing the work that matters.
