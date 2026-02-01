---
title: "QMD: What Cutting-Edge Search Looks Like for AI Agents"
status: draft
platform: blog
---

# QMD: What Cutting-Edge Search Looks Like for AI Agents

Search is the bottleneck for AI applications, and most people are solving it wrong.

Before I get into QMD, the tool that prompted this piece, let me explain why search matters so much and why it's harder than it looks.

## The Search Problem Nobody Talks About

Every AI assistant that works with your documents, code, or notes faces a fundamental question: how do you find the right context to give the model?

The naive answer is "just put everything in the context window." This fails immediately at scale. A 1M token context window sounds huge until you realize most codebases are 100K-10M+ lines of code. And even if it fit, loading a million tokens per query at $3/million tokens means $3 per question. At 100 queries/day, that's $9,000/month. Nobody's paying that.

So you need retrieval. You need to find the relevant pieces before sending them to the model. But there are fundamentally different ways to search, and each has tradeoffs.

## How Search Actually Works

There are two main approaches, and understanding them matters for what comes next.

**Keyword search (BM25)** is what you'd expect. You type "authentication," it finds documents containing "authentication." Fast, precise, great when you know exactly what you're looking for. The algorithm (BM25 is the modern standard) scores documents based on term frequency and document length. It's been the backbone of search engines for decades.

The problem: it can't handle synonyms or conceptual queries. Search for "auth" and you won't find "authentication." Search for "where do we handle login" and you'll miss the file called `IdentityManager.ts`. There's no understanding of meaning, just pattern matching.

**Semantic/vector search** solves this by converting text into numerical representations (embeddings) that capture meaning. "Authentication" and "login" end up close together in vector space because they're conceptually related. You can ask "where do we handle user identity" and find relevant code even if those exact words never appear.

The problem: it can lose precision. Search for the exact function `getUserById` and you might get back a bunch of files about users, IDs, and databases that are conceptually related but not what you wanted.

**Hybrid search** combines both. Run keyword and semantic search in parallel, merge the results, get the benefits of both. Documents that rank highly in both methods get boosted. Documents that only one method finds still surface.

The implementation matters. How do you merge two ranked lists? The standard approach is Reciprocal Rank Fusion (RRF): `score = Σ 1/(rank + 60)`. Simple, stable, requires no tuning.

**Re-ranking** is the final layer. Take your top results and run them through a more sophisticated model that scores relevance more carefully. This catches cases where both retrieval methods ranked something highly but it's actually off-topic. Cohere's benchmarks show re-ranking adds 39% improvement on average. That's not marginal.

## Enter QMD

Now you have context for why QMD matters.

Tobi Lütke, Shopify's founder, released QMD (Quick Markdown Search) as an open-source project. 4.4k GitHub stars later, it's clear this scratched an itch.

QMD combines everything I just described into a single local-first tool: hybrid search with query expansion and re-ranking, running entirely on your machine, with native integration for AI agents.

No cloud APIs. No sending your documents anywhere. No per-query costs. Just download some models and go.

## The Architecture

QMD's pipeline is worth studying:

```
┌─────────────────┐
│   User Query    │
└────────┬────────┘
         │
         ├──────────────────────────────────┐
         ▼                                  ▼
┌────────────────┐                ┌────────────────┐
│ Original Query │                │ Query Expansion│
│   (×2 weight)  │                │ (fine-tuned)   │
└───────┬────────┘                └───────┬────────┘
        │                                 │
        │    ┌────────────────────────────┤
        │    │                            │
        ▼    ▼                            ▼
   ┌────────────────┐               ┌────────────────┐
   │     BM25       │               │  Vector Search │
   │    (FTS5)      │               │  (embeddings)  │
   └───────┬────────┘               └───────┬────────┘
           │                                │
           └───────────────┬────────────────┘
                           ▼
                  ┌─────────────────┐
                  │   RRF Fusion    │
                  │   + top-rank    │
                  │     bonus       │
                  └────────┬────────┘
                           │
                           ▼ (Top 30)
                  ┌─────────────────┐
                  │  LLM Re-ranking │
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │ Position-Aware  │
                  │ Blend           │
                  └─────────────────┘
```

Several things stand out.

**Query expansion with a fine-tuned model.** QMD doesn't just run your query as-is. It expands it with related terms using a custom 1.7B parameter model trained specifically for this task. The original query gets 2x weight so exact matches aren't drowned out by expansions.

**Parallel BM25 and vector retrieval.** Standard hybrid approach, but the execution is smart. BM25 uses SQLite's FTS5 for fast keyword matching. Vector search uses a small embedding model (300MB). Both run locally, both are fast.

**Position-aware blending after fusion.** This is the clever bit. Pure RRF can dilute exact matches when expanded queries miss them. QMD adds top-rank bonuses: +0.05 for rank 1, +0.02 for ranks 2-3. High-confidence results from either method stay high-confidence after fusion.

**LLM re-ranking with logprobs.** The final stage uses a 640MB re-ranker model that outputs Yes/No relevance scores with probability values. This catches cases where both retrieval methods ranked something highly but it's actually off-topic.

## Why Local-First Matters

There's a reason this runs entirely on-device.

Privacy is obvious. Your documents, your notes, your code never leaves your machine. For personal knowledge bases, work documentation, or anything sensitive, this isn't just nice-to-have.

Latency is underrated. Network round-trips add up. When your agent is doing iterative search, even 100ms per request compounds into noticeable delays. Local search is basically instant.

Cost is real. Embedding APIs charge per token. If you're searching frequently across a large corpus, those costs accumulate. Local models have zero marginal cost after the initial download.

Offline capability exists. Sounds trivial until you're on a plane or somewhere with bad connectivity and need to search your notes.

## The Model Stack

QMD runs three small models:

| Model | Size | Purpose |
|-------|------|---------|
| embeddinggemma-300M | ~300MB | Text embeddings |
| qwen3-reranker-0.6b | ~640MB | Relevance re-ranking |
| qmd-query-expansion-1.7B | ~1.1GB | Query expansion |

Total: roughly 2GB on disk. These run via node-llama-cpp with GGUF quantization, so they work on consumer hardware without a dedicated GPU. Not blazing fast on a MacBook Air, but usable.

## MCP Integration

QMD exposes five tools through the Model Context Protocol:

| Tool | Purpose |
|------|---------|
| `qmd_search` | Fast BM25 keyword search |
| `qmd_vsearch` | Semantic vector search |
| `qmd_query` | Full hybrid search with re-ranking |
| `qmd_get` | Retrieve document by path |
| `qmd_multi_get` | Retrieve multiple documents |

This means Claude Desktop, Claude Code, or any MCP-compatible agent can use QMD natively. Point it at your notes directory, your documentation, your local knowledge base. The agent now has smart search over your content.

The separation of tools is thoughtful. Sometimes you want fast keyword lookup. Sometimes you want semantic search. Sometimes you want the full pipeline. Having all three lets the agent choose appropriately based on the query type.

## What This Represents

QMD isn't just a search tool. It's a statement about where AI infrastructure is heading.

**Local-first tools are proliferating.** osgrep, mgrep, now QMD. The pattern is clear: serious users want on-device semantic search that doesn't require cloud services.

**Hybrid search is becoming standard.** Pure keyword or pure vector isn't enough. The 15-30% accuracy improvement from combining them is too significant to ignore.

**MCP is the integration layer.** Tools designed for AI agents export MCP interfaces. This is the emerging standard for how agents access external capabilities.

**Small models are surprisingly capable.** A 640MB re-ranker and 300MB embedding model, running locally, get you most of the quality of much larger cloud models. The gap keeps shrinking.

## Should You Use It?

If you use Claude Desktop or any MCP-compatible agent and have a significant local knowledge base, QMD is worth trying. The setup is straightforward: install, point at your directories, add the MCP configuration.

If you're building your own AI application with search needs, QMD's architecture is worth studying even if you don't use it directly. The query expansion, position-aware blending, and multi-stage pipeline represent current best practices.

If you're just doing occasional searches on a small document set, the 2GB model download might be overkill. Simple grep or a basic semantic search tool would suffice.

## The Bigger Picture

The search infrastructure for AI agents is still immature. Most agents use naive approaches: grep everything, stuff it into context, hope for the best. This burns tokens and misses relevant information.

QMD shows what thoughtful search infrastructure looks like. Hybrid retrieval. Query expansion. Re-ranking. Position-aware fusion. Running locally with small models.

These techniques aren't new. Enterprise search systems have used them for years. What's new is packaging them for individual use, for AI agents, running on consumer hardware.

The agents that ship quality work will be the ones with quality search. Finding the right context is as important as what the model does with it. QMD is one answer to that problem, and it's a good one.

Tobi built this because he needed it. That's usually how the best tools start.
