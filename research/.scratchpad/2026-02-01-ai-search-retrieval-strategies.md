# AI Search and Retrieval Strategies: From Grep to Agentic RAG

**Date:** 2-1-26
**Category:** Research Report

---

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [Background](#background)
3. [The Search Strategy Landscape](#the-search-strategy-landscape)
4. [QMD: The New Kid on the Block](#qmd-the-new-kid-on-the-block)
5. [How Cursor Does It](#how-cursor-does-it)
6. [How Claude Code Does It](#how-claude-code-does-it)
7. [How Manus AI Does It](#how-manus-ai-does-it)
8. [Hybrid Search: The Emerging Consensus](#hybrid-search-the-emerging-consensus)
9. [Key Takeaways](#key-takeaways)
10. [Predictions](#predictions)

---

## Executive Summary

The AI search and retrieval landscape is fragmenting into distinct approaches, each with meaningful tradeoffs. After researching how leading AI tools handle codebase and document search, the verdict is clear: **hybrid approaches win, but the specific hybrid recipe matters enormously**.

Three major findings:

1. **Pure grep is burning tokens.** Claude Code's grep-only approach costs significantly more than vector-based retrieval for large codebases. A [Milvus engineer analysis](https://milvus.io/blog/why-im-against-claude-codes-grep-only-retrieval-it-just-burns-too-many-tokens.md) found agentic grep patterns "just burn too many tokens" due to iterative reasoning loops.

2. **Semantic search adds 12-31% accuracy.** Cursor's research shows semantic search improves code retrieval accuracy by [12.5% on average](https://cursor.com/blog/semsearch), while Morph found [31% improvement](https://www.morphllm.com/blog/semantic-search) when combining grep with semantic search on large codebases.

3. **QMD represents a new paradigm.** Tobi Lütke's [QMD](https://github.com/tobi/qmd) (Quick Markdown Search) combines BM25, vector search, and LLM re-ranking in a local-first package. With 4.4k GitHub stars and MCP integration, it's the most sophisticated open-source hybrid search tool for AI agents.

The industry is converging on "context engineering" - a governed, explainable evolution of RAG that treats retrieval as a first-class engineering discipline rather than a simple lookup.

---

## Background

Every AI coding assistant faces the same fundamental problem: how do you help an LLM understand a codebase it's never seen before?

The naive answer is "just put everything in the context window." But this fails for three reasons:

```
┌─────────────────────────────────────────────────────────────────┐
│                  Why "Just Use Context" Fails                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. SCALE                                                       │
│     Fortune 500 avg: 347TB of data                              │
│     1M token window ≈ 50K lines of code                         │
│     Most codebases: 100K-10M+ lines                             │
│                                                                 │
│  2. COST                                                        │
│     Claude input: $3/M tokens (Sonnet)                          │
│     Loading 1M tokens every query = $3/query                    │
│     At 100 queries/day = $9,000/month                           │
│                                                                 │
│  3. ACCURACY                                                    │
│     "Lost in the Middle" problem (Stanford)                     │
│     20-25% accuracy variance by position                        │
│     Models struggle with middle content                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

So you need retrieval. The question is: what kind?

**Key terms:**

| Term | Definition |
|------|------------|
| **BM25** | Classic keyword-based scoring (TF-IDF successor). Fast, exact matching. |
| **Vector/Semantic Search** | Embed text as vectors, find by cosine similarity. Understands meaning. |
| **RAG** | Retrieval-Augmented Generation. Fetch context before generating. |
| **Agentic RAG** | RAG with autonomous agents that iterate, reason, and use tools. |
| **Hybrid Search** | Combining BM25 + vector search (and often re-ranking). |
| **RRF** | Reciprocal Rank Fusion. Merging ranked lists: `score = Σ 1/(rank + k)` |

---

## The Search Strategy Landscape

The market has split into four camps:

```
                         High Accuracy
                              │
                              │
     ┌────────────────────────┼────────────────────────┐
     │                        │                        │
     │   AGENTIC RAG          │      HYBRID SEARCH     │
     │   (Manus, OpenManus)   │      (Cursor, QMD)     │
     │                        │                        │
     │   • Multi-step         │      • BM25 + Vector   │
High │   • Tool orchestration │      • Re-ranking      │    Low
Cost │   • Iterative          │      • Query expansion │    Cost
     │                        │                        │
     │   GREP-BASED           │      PURE VECTOR       │
     │   (Claude Code)        │      (Early RAG apps)  │
     │                        │                        │
     │   • Token-heavy        │      • Fast lookups    │
     │   • Flexible           │      • Semantic only   │
     │                        │                        │
     └────────────────────────┼────────────────────────┘
                              │
                              │
                         Low Accuracy
```

Each has legitimate use cases. Small codebases? Grep is fine. Need semantic understanding? You need vectors. Building a production system? Hybrid or you're leaving accuracy on the table.

---

## QMD: The New Kid on the Block

[QMD](https://github.com/tobi/qmd) (Quick Markdown Search) is an open-source, local-first search engine created by Tobi Lütke (Shopify founder). It combines the best practices from search and retrieval research into a single CLI tool.

### Architecture

QMD runs entirely on-device using node-llama-cpp with GGUF models:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        QMD Hybrid Search Pipeline                           │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐
│   User Query    │
└────────┬────────┘
         │
         ├──────────────────────────────────────┐
         ▼                                      ▼
┌────────────────┐                    ┌────────────────┐
│ Original Query │                    │ Query Expansion│
│   (×2 weight)  │                    │ (fine-tuned)   │
└───────┬────────┘                    └───────┬────────┘
        │                                     │
        │    ┌────────────────────────────────┤
        │    │                                │
        ▼    ▼                                ▼
   ┌────────────────┐                   ┌────────────────┐
   │     BM25       │                   │  Vector Search │
   │    (FTS5)      │                   │  (embeddings)  │
   └───────┬────────┘                   └───────┬────────┘
           │                                    │
           └───────────────┬────────────────────┘
                           ▼
                  ┌─────────────────┐
                  │   RRF Fusion    │
                  │   k=60          │
                  │   +top-rank     │
                  │    bonus        │
                  └────────┬────────┘
                           │
                           ▼ (Top 30)
                  ┌─────────────────┐
                  │  LLM Re-ranking │
                  │  (qwen3-reranker)│
                  │  Yes/No+logprobs│
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │ Position-Aware  │
                  │ Blend           │
                  │ Rank 1-3: 75%RRF│
                  │ Rank 4-10: 60%  │
                  │ Rank 11+: 40%   │
                  └─────────────────┘
```

### Why It Matters

QMD's position-aware blending is clever. Pure RRF can dilute exact matches when expanded queries don't find them. By giving top-rank results a bonus (+0.05 for #1, +0.02 for #2-3), QMD preserves high-confidence retrieval while still benefiting from semantic understanding.

The tool uses three local models:
- `embeddinggemma-300M-Q8_0` (~300MB) for embeddings
- `qwen3-reranker-0.6b-q8_0` (~640MB) for re-ranking
- `qmd-query-expansion-1.7B-q4_k_m` (~1.1GB) for query expansion (fine-tuned)

### MCP Integration

QMD exposes an MCP server with five tools:
- `qmd_search` - Fast BM25 keyword search
- `qmd_vsearch` - Semantic vector search
- `qmd_query` - Hybrid search with re-ranking
- `qmd_get` - Retrieve document by path or docid
- `qmd_multi_get` - Retrieve multiple documents

This makes it trivial to plug into Claude Desktop or Claude Code.

---

## How Cursor Does It

Cursor uses [Turbopuffer](https://turbopuffer.com/), an object-storage-first vector database, for semantic code search.

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Cursor's Search Pipeline                     │
└─────────────────────────────────────────────────────────────────┘

  Local                                      Server
┌─────────────────────┐                ┌─────────────────────────┐
│                     │                │                         │
│  1. File changed    │                │  4. Compute embeddings  │
│  2. Chunk into      │   encrypted    │     (Cursor's model)    │
│     functions       │────────────────│                         │
│  3. Hash + encrypt  │                │  5. Store in Turbopuffer│
│                     │                │     (code discarded)    │
│                     │                │                         │
│  9. Retrieve code   │   obfuscated   │  6. Query comes in      │
│     locally         │◄───────────────│  7. Vector similarity   │
│ 10. Send to LLM     │   paths+lines  │  8. Return positions    │
│                     │                │                         │
└─────────────────────┘                └─────────────────────────┘
```

Key design decisions:

1. **Namespace-per-codebase**: Each (user_id, codebase) gets its own Turbopuffer namespace. Billions of vectors across millions of codebases.

2. **Privacy-first**: Server only sees encrypted chunks. Embeddings are computed from encrypted content, then the content is discarded. Client retrieves actual code locally.

3. **Merkle tree indexing**: Detects file changes efficiently. Cursor claims this "cuts time-to-first-query from hours to seconds."

4. **Shared index fragments**: Teams with similar codebases share 92% of indexing work.

### Performance

According to [Cursor's research](https://cursor.com/blog/semsearch):
- **12.5% average accuracy improvement** over grep-only
- Range: 6.5-23.5% depending on model
- Higher code retention in codebases
- Higher overall request satisfaction

### Why Turbopuffer?

Turbopuffer is object-storage-native (built on S3), which means:
- **20x cost reduction** vs traditional vector DBs
- Inactive namespaces cost almost nothing (cold storage)
- 100B+ vectors at 200ms p99 latency
- Used by Cursor, Notion, Linear, Superhuman, Readwise

---

## How Claude Code Does It

Claude Code takes a fundamentally different approach: **agentic grep**.

### Tools Available

Claude Code uses three primary search tools:

| Tool | Purpose | When Used |
|------|---------|-----------|
| `Glob` | Find files by pattern | `**/*.ts`, `src/**/*.py` |
| `Grep` | Search file contents | Regex patterns, exact matches |
| `Read` | Read file contents | After finding relevant files |
| `Task` (Explore agent) | Multi-step codebase exploration | Complex, open-ended searches |

### The Agentic Loop

```
┌─────────────────────────────────────────────────────────────────┐
│                 Claude Code Search Pattern                       │
└─────────────────────────────────────────────────────────────────┘

  ┌───────────────────┐
  │  User Question    │
  │  "Where is auth   │
  │   handled?"       │
  └─────────┬─────────┘
            │
            ▼
  ┌───────────────────┐      ┌───────────────────┐
  │  Reason about     │      │                   │
  │  what to search   │─────►│  Glob/Grep        │
  └───────────────────┘      │  "auth", "login"  │
            ▲                └─────────┬─────────┘
            │                          │
            │                          ▼
  ┌─────────┴─────────┐      ┌───────────────────┐
  │  Reason about     │◄─────│  Read results     │
  │  results          │      │  (files found)    │
  └───────────────────┘      └───────────────────┘
            │
            ├──────► More searches needed? ──► Loop back
            │
            ▼
  ┌───────────────────┐
  │  Answer user      │
  └───────────────────┘
```

### Tradeoffs

**Advantages:**
- No index required (works immediately)
- No infrastructure costs
- Flexible (can follow any lead)
- Good for small-medium codebases
- Great for exact pattern matching (`getUserById`)

**Disadvantages:**
- Higher token usage (iterative reasoning)
- Can't answer "where do we handle authentication?" without knowing the file is called `IdentityManager.ts`
- Slower for repeated queries (no caching)
- Scales poorly with codebase size

### The Token Problem

A [Milvus engineer's analysis](https://milvus.io/blog/why-im-against-claude-codes-grep-only-retrieval-it-just-burns-too-many-tokens.md) found Claude Code's approach "just burns too many tokens" because each search requires:

1. Reason about what to search
2. Execute grep/glob
3. Read results
4. Reason about results
5. Decide if more searches needed
6. Repeat

This creates an O(n) token cost where n is the number of search iterations. Vector search is O(1) per query.

---

## How Manus AI Does It

[Manus AI](https://manus.im/) takes the most autonomous approach: a fully agentic system that operates its own virtual computer.

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      Manus AI Modules                           │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│    PLANNER      │     │    EXECUTOR     │     │   USER-PROXY    │
│                 │     │                 │     │                 │
│ • Breaks tasks  │────►│ • Controls      │◄───►│ • Natural lang  │
│ • Creates       │     │   browser       │     │   interface     │
│   todo.md       │     │ • Runs code     │     │                 │
│ • Pseudocode    │     │ • File I/O      │     │                 │
│   planning      │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │
                               ▼
                        ┌─────────────────┐
                        │  TOOL PROVIDER  │
                        │                 │
                        │ • Browser       │
                        │ • Terminal      │
                        │ • File system   │
                        │ • Code exec     │
                        └─────────────────┘
```

### Key Differences

Manus doesn't specialize in search - it's a general-purpose agent that uses whatever tools are needed. For codebase exploration, it might:

1. Use terminal commands (grep, find, tree)
2. Read files directly
3. Execute code to test hypotheses
4. Browse documentation

This makes it more flexible but also more expensive and slower than specialized search tools.

### When Manus Makes Sense

- Complex multi-step tasks requiring multiple tools
- Tasks that go beyond search (write code, deploy, test)
- Exploratory work where the goal isn't fully defined
- Background autonomous work

---

## Hybrid Search: The Emerging Consensus

The industry is converging on hybrid approaches that combine multiple retrieval strategies.

### The Hybrid Recipe

```
┌─────────────────────────────────────────────────────────────────┐
│              Production Hybrid Search Pipeline                   │
└─────────────────────────────────────────────────────────────────┘

STAGE 1: QUERY UNDERSTANDING
┌──────────────────────────────────────────────────────────────────┐
│  • Query Expansion (HyDE, multi-query)                           │
│  • Intent Classification (navigational vs exploratory)          │
│  • Dynamic alpha tuning (keyword-heavy vs semantic-heavy)       │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
STAGE 2: PARALLEL RETRIEVAL
┌──────────────────────────────────────────────────────────────────┐
│                                                                  │
│   BM25 (Sparse)              Vector (Dense)                      │
│   ┌────────────┐             ┌────────────┐                      │
│   │ Fast       │             │ Semantic   │                      │
│   │ Exact match│             │ Conceptual │                      │
│   │ Keywords   │             │ Similarity │                      │
│   └─────┬──────┘             └─────┬──────┘                      │
│         │                          │                             │
│         └──────────┬───────────────┘                             │
│                    ▼                                             │
│              ┌──────────┐                                        │
│              │RRF Fusion│  score = Σ 1/(rank + 60)               │
│              └──────────┘                                        │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
STAGE 3: RE-RANKING
┌──────────────────────────────────────────────────────────────────┐
│  Options (in order of quality/cost):                             │
│  1. Cross-Encoder (Cohere Rerank 3.5) - 39% avg improvement      │
│  2. ColBERT (late interaction) - fast, pre-computed docs         │
│  3. LLM-based - highest ceiling, most expensive                  │
└──────────────────────────────────────────────────────────────────┘
```

### Fusion Techniques

**Reciprocal Rank Fusion (RRF)**

The most common fusion method. Simple, stable, requires no tuning:

```
RRF_score = Σ 1/(rank + k)
```

Where k=60 is the standard constant. This means:
- Rank 1 contributes: 1/61 = 0.016
- Rank 10 contributes: 1/70 = 0.014
- Rank 100 contributes: 1/160 = 0.006

Documents ranked highly by multiple methods get boosted.

**Weighted Score Combination**

```
Final_score = α · Vector_score + (1-α) · BM25_score
```

Dynamic alpha tuning adjusts based on query type:
- Navigational queries (exact lookup): α ≈ 0.2 (favor BM25)
- Exploratory queries (conceptual): α ≈ 0.8 (favor vector)

### Benchmarks

| Approach | Improvement over BM25 alone |
|----------|----------------------------|
| Hybrid (BM25 + Vector) | 15-30% recall |
| Hybrid + Cross-Encoder Rerank | 39% average (BEIR) |
| Hybrid + LLM Rerank | Up to 48% (Databricks) |

Source: [Weaviate](https://weaviate.io/blog/hybrid-search-explained), [Cohere](https://cohere.com/blog/rerank-3pt5)

---

## Key Takeaways

1. **Hybrid search wins.** Pure grep or pure vector isn't enough. The 12-31% accuracy improvement from combining approaches is real and significant.

2. **QMD is the most sophisticated open-source option.** If you want local-first hybrid search with MCP integration, QMD is the current state of the art.

3. **Cursor's architecture is production-proven.** Turbopuffer + privacy-first design + Merkle tree indexing shows what enterprise-grade looks like.

4. **Claude Code's grep approach works but doesn't scale.** Fine for small codebases, token-expensive for large ones.

5. **Re-ranking is underrated.** Adding a re-ranker on top of hybrid retrieval consistently adds 20-40% improvement.

6. **Context engineering is the new discipline.** RAG isn't dead - it's evolving into a governed, explainable retrieval practice.

7. **Local-first tools are proliferating.** QMD, osgrep, mgrep represent a trend toward privacy-preserving, on-device semantic search.

---

## Predictions

### Near-Term (2026)

1. **Claude Code will add semantic search.** The grep-only approach burns too many tokens. Anthropic will likely add vector search or integrate with tools like QMD.

2. **MCP-based search tools will proliferate.** QMD's MCP integration is a template. Expect more tools to follow.

3. **Hybrid search becomes table stakes.** Any serious coding assistant will need BM25 + vector + re-ranking.

### Medium-Term (2027)

4. **Model-Document Protocol (MDP) gains traction.** The paradigm of transforming raw documents into LLM-consumable formats will become standard.

5. **Context window size becomes less important.** Better retrieval means you don't need to stuff everything into context.

6. **Specialized retrieval models emerge.** Fine-tuned embedding models for code, legal docs, medical records, etc.

### Long-Term (2028+)

7. **Agentic search becomes default.** Not just retrieve-then-generate, but iterative, tool-using, self-correcting retrieval.

8. **Search merges with reasoning.** The line between "finding information" and "reasoning about information" blurs completely.

9. **Privacy regulations force local-first.** GDPR-style rules will push more processing to the edge, making tools like QMD more valuable.

---

## Sources

### Primary Sources
- [QMD GitHub Repository](https://github.com/tobi/qmd)
- [Cursor Semantic Search Blog](https://cursor.com/blog/semsearch)
- [Cursor Secure Codebase Indexing](https://cursor.com/blog/secure-codebase-indexing)
- [Turbopuffer Architecture](https://turbopuffer.com/docs/architecture)
- [Morph: Grep Isn't Enough](https://www.morphllm.com/blog/semantic-search)

### Research Papers
- [Model-Document Protocol for AI Search (arXiv)](https://arxiv.org/abs/2510.25160)
- [Agentic Information Retrieval (arXiv)](https://arxiv.org/abs/2410.09713)
- [Is Agentic RAG Worth It? (arXiv)](https://arxiv.org/html/2601.07711v1)

### Industry Analysis
- [Milvus: Why I'm Against Claude Code's Grep-Only Retrieval](https://milvus.io/blog/why-im-against-claude-codes-grep-only-retrieval-it-just-burns-too-many-tokens.md)
- [Weaviate: Hybrid Search Explained](https://weaviate.io/blog/hybrid-search-explained)
- [NVIDIA: Traditional RAG vs Agentic RAG](https://developer.nvidia.com/blog/traditional-rag-vs-agentic-rag-why-ai-agents-need-dynamic-knowledge-to-get-smarter/)
- [TurboPuffer: Object Storage-First Vector Database](https://jxnl.co/writing/2025/09/11/turbopuffer-object-storage-first-vector-database-architecture/)

### Tools
- [osgrep: Local Semantic Search](https://github.com/Ryandonofrio3/osgrep)
- [mgrep: CLI Semantic Search](https://github.com/mixedbread-ai/mgrep)
- [Manus AI](https://manus.im/)
