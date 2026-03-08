---
title: "The CEO of Shopify Built the Best Search Tool for AI Agents. That Should Embarrass the Industry."
content-id: 20260201-AD-003
status: draft
platform: blog
---

# The CEO of Shopify Built the Best Search Tool for AI Agents. That Should Embarrass the Industry.

Tobi Lütke runs a $100B+ company. He manages thousands of employees, overseas billions in GMV, and sits in the chair that determines the strategic direction of one of the most important companies in commerce.

He also found time to build QMD — a local-first hybrid search tool for AI agents that is, technically, better than what most dedicated AI teams have shipped.

Let that sit.

There are entire companies whose sole focus is search infrastructure for AI. There are teams of engineers at every major AI lab thinking about retrieval. Millions of developers have bumped into this exact problem — how do you find the right context to feed a model without burning tokens or missing what matters? — and most of them reached for grep, stuffed embeddings into Pinecone, or gave up and expanded the context window.

Tobi Lütke built QMD, open-sourced it, and 4.4k GitHub stars later it's quietly become the most thoughtful implementation of this pattern available to individual developers. Not "pretty good for a side project." Just good. Full stop.

## What QMD Is

QMD (Quick Markdown Search) is a local-first hybrid search engine with MCP integration, designed to give AI agents sophisticated retrieval over your local documents and code. No cloud APIs. No per-query costs. No data leaving your machine.

If you've read about the [hybrid search landscape for AI tools](https://danzakon.com/articles/hybrid-search), QMD is the most complete implementation of that pattern available to individual developers — and it runs on your MacBook.

## The Architecture

The pipeline is the thing. This isn't grep wrapped in a vector store. It's a multi-stage retrieval system with custom-trained models at each step.

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

A few things here are genuinely clever, not just competent.

**Query expansion with a fine-tuned 1.7B model.** QMD doesn't search your exact query — it expands it first with related terms using a model trained specifically for this task. The original query gets 2x weight to prevent exact matches from being diluted by expansions. Most tools skip this step entirely. Tobi's tool has a custom-trained model for it.

**Position-aware blending after RRF fusion.** Standard Reciprocal Rank Fusion can dilute high-confidence exact matches when expanded queries return noisy results. QMD applies top-rank bonuses (+0.05 for rank 1, +0.02 for ranks 2-3) so that if both retrieval methods are confident about a result, it stays confident after fusion. This is the kind of detail that matters in production but gets skipped in prototypes.

**LLM re-ranking with logprobs.** The final stage uses a 640MB re-ranker that scores Yes/No relevance with probability values — not just binary classification. You get calibrated confidence, not a coin flip. Cohere's benchmarks show re-ranking adds 39% improvement on average. Tobi included it.

## The Model Stack

Three small models, all running locally:

| Model | Size | Purpose |
|-------|------|---------|
| embeddinggemma-300M | ~300MB | Text embeddings |
| qwen3-reranker-0.6b | ~640MB | Relevance re-ranking |
| qmd-query-expansion-1.7B | ~1.1GB | Query expansion |

Total: roughly 2GB. They run via node-llama-cpp with GGUF quantization — consumer hardware, no GPU required. Not instant on a MacBook Air, but fast enough that it doesn't break the agent loop.

## MCP Integration

QMD exposes five tools through the Model Context Protocol:

| Tool | Purpose |
|------|---------|
| `qmd_search` | Fast BM25 keyword search |
| `qmd_vsearch` | Semantic vector search |
| `qmd_query` | Full hybrid search with re-ranking |
| `qmd_get` | Retrieve document by path |
| `qmd_multi_get` | Retrieve multiple documents |

Claude Desktop, Claude Code, or any MCP-compatible agent gets smart search over your local content natively. The separation of tools is thoughtful — sometimes an agent needs exact keyword lookup, sometimes semantic, sometimes the full pipeline. Having all three lets the model choose based on query type rather than being forced through an expensive path every time.

## Why Local-First

The obvious reason is privacy: your notes, your code, your documents never leave the machine. For anything sensitive, that's not optional.

The less obvious reason is latency. When an agent is doing iterative retrieval — searching, reading results, refining, searching again — network round-trips compound. Local search is effectively instant. At 10 search iterations per task, even 100ms of network latency per call is a full second of unnecessary waiting.

Cost compounds too. Embedding APIs charge per token. At any meaningful scale of queries over a large corpus, the marginal cost of cloud embeddings adds up in a way that zero marginal cost local models don't.

## What It Says

Here's what I keep coming back to: Tobi Lütke had no reason to build this.

Not in the sense that it wasn't a good idea — clearly it was, 4.4k stars suggests the market agrees. But in the sense that he had every reason not to. He's a CEO with a full-time job that is considerably more demanding than "build open source search tooling for developers." The opportunity cost of his time is astronomical. There are teams of people who are literally paid to solve this problem.

And yet what those teams shipped — most of it, anyway — is coarser than what Tobi built on the side. The agentic grep loops that burn tokens. The pure vector implementations that miss exact matches. The "just expand the context window" non-solution. The RAG pipelines with no re-ranking, no query expansion, no position-aware fusion.

QMD has all of it. Shipped and open-sourced.

The most charitable read is that Tobi is genuinely a technical CEO who scratches his own itches and happens to be very good at it. The less charitable read is that the AI infrastructure space has failed to make this kind of sophisticated retrieval accessible, and a billionaire had to fill the gap himself.

Both reads are probably right. And both should push engineers who are building in this space to ask whether they're actually solving the problem or just shipping something that looks like a solution.

Tobi built this because he needed it. That's usually how the best tools start. It's less usual when the builder is running a $100B company and still found the time to do it right.
