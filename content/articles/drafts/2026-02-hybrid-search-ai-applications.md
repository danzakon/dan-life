---
title: How the Best AI Tools Are Solving Search (And What You Can Learn From Them)
status: draft
platform: blog
---

# How the Best AI Tools Are Solving Search (And What You Can Learn From Them)

The most interesting technical battle in AI tooling right now isn't about model capabilities. It's about search.

Every coding assistant, every RAG application, every AI agent that works with documents faces the same problem: finding the right context to feed the model. The approaches vary wildly. Some tools grep their way through codebases. Others build vector databases. The best ones are doing something more sophisticated.

I've been digging into how the leading AI tools handle retrieval, and the landscape is more fragmented than you'd expect. There's no consensus. There are tradeoffs. And what each company chose reveals something about where they think the leverage is.

## The Current Landscape

The market has split into four camps:

```
                         High Accuracy
                              |
     ┌────────────────────────┼────────────────────────┐
     │                        |                        │
     │   AGENTIC RAG          │      HYBRID SEARCH     │
     │   (Manus, OpenManus)   │      (Cursor, QMD)     │
     │                        │                        │
High │                        │                        │ Low
Cost │                        │                        │ Cost
     │                        │                        │
     │   GREP-BASED           │      PURE VECTOR       │
     │   (Claude Code)        │      (Early RAG apps)  │
     │                        │                        │
     └────────────────────────┼────────────────────────┘
                              |
                         Low Accuracy
```

Each quadrant has legitimate defenders. What's interesting is watching where companies with real engineering resources chose to invest.

## How Cursor Does It

Cursor bet on vector search, and they built serious infrastructure to make it work.

They use Turbopuffer, an object-storage-first vector database that's become the quiet workhorse behind several AI companies. The architecture is clever: code gets chunked and embedded on-device, encrypted, then sent to the server. The server computes embeddings from encrypted content, stores them, then throws away the code. When you search, you get back obfuscated file paths and line numbers. Your client retrieves the actual code locally.

Privacy-first, but also fast. Turbopuffer claims 100B+ vectors at 200ms p99 latency. Linear, Notion, Superhuman, and Readwise all use it.

The results? Cursor published that semantic search improves code retrieval accuracy by 12.5% on average, with a range of 6.5-23.5% depending on the model. Not transformative, but meaningful.

The bet Cursor made: semantic understanding matters more than exact matching for how developers actually search. When someone asks "where do we handle authentication," they probably don't know the file is called `IdentityManager.ts`. Vector search bridges that gap.

## How Claude Code Does It

Claude Code took the opposite approach. No index. No embeddings. Just grep with a reasoning loop.

The tools are simple: Glob for finding files by pattern, Grep for searching content, Read for getting file contents. The model reasons about what to search, executes searches, reads results, reasons again, and iterates until it finds what it needs.

The advantages are real. Works immediately on any codebase. No setup. No infrastructure. Highly flexible for following unexpected leads. Great for exact pattern matching when you know what you're looking for.

The disadvantages are also real. A Milvus engineer's analysis found that agentic grep "just burns too many tokens" due to iterative reasoning loops. Each search requires reasoning about what to search, executing, reading, reasoning about results, deciding if more searches are needed. That's O(n) token cost where n is the number of iterations.

My read: Claude Code optimized for zero-friction onboarding over long-term efficiency. Get users productive immediately, worry about token costs later. Makes sense for their positioning, but it's a bet that token prices will keep falling.

## How Manus AI Does It

Manus represents the most autonomous approach: a fully agentic system that operates its own virtual computer.

For codebase exploration, Manus might use terminal commands, read files directly, execute code to test hypotheses, or browse documentation. It doesn't specialize in search because it treats search as just one tool among many.

This makes it more flexible but also more expensive and slower than specialized search. When your agent has to reason about which approach to take and then execute a multi-step process, latency and cost add up.

The bet here is different: Manus isn't competing on search quality. They're competing on autonomy. Search is a means to an end.

## The Hybrid Trend

The most interesting signal I'm seeing is convergence toward hybrid approaches that combine multiple retrieval strategies.

Morph published data showing a 31% improvement when combining grep with semantic search on large codebases. That's not marginal. And it validates what enterprise search systems have known for years: BM25 (keyword matching) and vector search (semantic matching) complement each other.

The emerging recipe looks like this:

```
┌─────────────────┐
│   User Query    │
└────────┬────────┘
         │
         ├──────────────────────┐
         ▼                      ▼
    ┌─────────┐           ┌─────────┐
    │  BM25   │           │ Vector  │
    │(keyword)│           │(semantic)│
    └────┬────┘           └────┬────┘
         │                      │
         └──────────┬───────────┘
                    ▼
           ┌───────────────┐
           │  RRF Fusion   │
           │   (merge)     │
           └───────┬───────┘
                   ▼
           ┌───────────────┐
           │  Re-ranking   │
           │  (optional)   │
           └───────────────┘
```

Query expansion before retrieval. Parallel keyword and semantic search. Reciprocal Rank Fusion to merge results. Optional re-ranking with a cross-encoder or LLM for fine-grained relevance.

Cohere's benchmarks show re-ranking alone adds 39% improvement on average. Databricks saw up to 48% with LLM-based re-ranking.

## The Local-First Movement

One trend I didn't expect: serious tools for local-first semantic search.

QMD (from Tobi Lütke) runs hybrid search entirely on-device using small models. osgrep and mgrep offer local semantic search CLIs. The models are getting small enough (300MB for embeddings, 600MB for re-ranking) that you don't need cloud APIs anymore.

The drivers are obvious: privacy (your code never leaves your machine), latency (no network round-trips), cost (no per-query API fees), and offline capability.

This matters for AI agents especially. When an agent needs to search iteratively, even 100ms network latency per query compounds. Local search is basically instant.

## What This Means

A few observations from watching this space:

**There's no winning architecture yet.** If there were, everyone would be using it. Cursor's vector-first, Claude Code's grep-first, and Manus's agent-first approaches all have defenders. The market is still exploring.

**Hybrid is becoming table stakes.** The 15-31% accuracy improvement from combining keyword and semantic search is too significant to ignore. Pure approaches are leaving accuracy on the table.

**Re-ranking is underrated.** Adding a cross-encoder on top of retrieval consistently adds 20-40% improvement. It's one of the highest-leverage interventions for search quality.

**The real competition is on context quality.** Finding the right 10,000 tokens out of millions matters more than cramming everything into a giant context window. Better retrieval beats bigger context.

**Local-first tools will proliferate.** As models shrink and quantization improves, the arguments for cloud-based search weaken. Privacy-conscious users and latency-sensitive applications will drive adoption of on-device solutions.

The companies that figure out the right search recipe for their domain will build meaningfully better AI applications. This isn't glamorous infrastructure work, but it's where real differentiation happens.

Search hasn't been solved. It's barely been started.
