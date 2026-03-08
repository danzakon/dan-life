---
title: Every Coding Agent Has Made a Different Bet on Search. Here's the Breakdown.
content-id: 20260201-AD-002
status: draft
platform: blog
---

# Every Coding Agent Has Made a Different Bet on Search. Here's the Breakdown.

There's a technical problem every AI coding tool has to solve, and every major player has solved it differently.

The problem: how do you find the right code to put in front of the model? Your codebase has millions of tokens. The context window holds maybe a hundred thousand. Something has to decide what's relevant before the model ever sees a line. That decision — the retrieval strategy — is one of the most consequential architectural choices a coding tool makes, and the answers across the industry are all over the map.

Cursor built a cloud vector index with cryptographic path masking. Claude Code threw the index out entirely and lets the model search with grep. GitHub Copilot retrained a proprietary embedding model on hard negatives and got a 37.6% quality lift. Sourcegraph built a three-retriever system with a RecSys paper behind it. JetBrains skipped semantic embeddings altogether and uses token overlap. They're all working on the same underlying problem. They all went a different direction.

This is the breakdown of how each of them made that bet, and what it reveals about what they actually prioritize.

---

## Claude Code: No Index, No Embeddings, Just Search

The most unusual choice in the field belongs to Anthropic. Claude Code has no pre-built index. It doesn't embed your codebase. There's no vector database, no cloud sync, no build phase.

Instead, the model drives its own search. It starts with `Glob` (near-zero token cost, pattern-based file discovery), chains into `Grep` (ripgrep under the hood, exact regex match), reads specific files as needed, and spins up isolated sub-agents via `Explore` when it needs to go deeper without polluting the main context window. The sub-agent runs on Claude Haiku, does its own Glob/Grep/Read work, and returns a summary — not raw file contents — back to the main session. It's a hierarchy of retrieval, cheapest tools first.

This was a deliberate choice made after testing the alternative. Boris Cherny (the engineer who built Claude Code) ran RAG against agentic search and described the result in a Hacker News thread: agentic search won "by a lot, and this was surprising."

The reasons he cited: precision (grep finds exact matches; embeddings introduce fuzzy positives that are noise for code), freshness (a pre-built index drifts from code during active editing), and privacy (data never leaves the machine, full stop). There's also a product reason: zero setup. No index build time means the tool works immediately on any codebase.

The economics work because of prompt caching. An LMCache analysis found a 92% prompt prefix reuse rate across Claude Code's agentic loop turns, which means cache reads at 0.1x the base price. For a 2M-token session, total cost drops from ~$6 to ~$1.15. Without that, the "burns too many tokens" critique would be decisive.

**The weakness is real though.** If a function called `createD1HttpClient` was renamed `buildGatewayClient` last sprint, grep returns nothing. Exact-match retrieval is blind to semantic relationships. On large codebases with inconsistent naming conventions, the iterative search loops get expensive.

**What the bet reveals:** Anthropic treats Claude Code as a Unix utility, not a product. The design philosophy is to do the simple thing first, defer complexity until demonstrated necessary. The RAG experiment showed it wasn't necessary — for typical developer workloads at current scale. That could change.

---

## Cursor: The Most Documented Commercial Vector Implementation

Cursor built an actual indexing infrastructure, and they've published more technical detail about it than almost anyone else in the space.

The pipeline: every file gets hashed into a Merkle tree. Every 10 minutes (or on file change), Cursor walks the tree to find diverging hashes and syncs only changed chunks. Changed files are split using tree-sitter — AST-aware chunking that respects function and class boundaries, not naive text splitting. Chunks get embedded and stored in Turbopuffer, a serverless vector database that does both approximate nearest-neighbor search and BM25 full-text search in one backend.

The privacy model is thoughtful. Raw source code never leaves your machine. File paths are HMAC-hashed before leaving. Embeddings live in Cursor's cloud, but an attacker who obtained them couldn't reconstruct your code.

The more interesting engineering is in their shared index reuse. When a new team member joins, their client computes a "simhash" of their Merkle tree and finds the most similar existing index in their org's namespace. If similarity clears a threshold, they copy that index as a starting point. Time-to-first-query dropped from a p99 of 4.03 hours to 21 seconds. That's not a retrieval quality improvement — it's an adoption improvement. It removes the "wait for the index to build before I can use this" friction that kills tool adoption on day one for new engineers.

Cursor's own evaluation puts semantic search at a +12.5% improvement in agent response accuracy versus no indexing, with a range of 6.5-23.5% depending on the model.

**What the bet reveals:** Cursor is building for teams, not individuals. The Merkle tree reuse optimization only matters if multiple engineers are sharing a codebase index. The privacy architecture is designed to pass enterprise security reviews. The +12.5% accuracy number is the justification for the infrastructure cost — semantic search is worth it, but only if you can prove it.

---

## GitHub Copilot: Proprietary Embeddings and Hard Negative Mining

Copilot's September 2025 embedding model update produced the clearest published numbers on retrieval quality improvement in the industry: +37.6% retrieval quality on their benchmark suite, 8x smaller index size, 2x higher embedding throughput. For C# developers specifically, code acceptance ratios went up 110.7%. For Java, 113.1%.

The architecture behind those numbers: contrastive learning with InfoNCE loss and Matryoshka Representation Learning (embeddings that support multiple output sizes). But the biggest lever wasn't the architecture — it was the training data.

GitHub mined "hard negatives": code that looks semantically similar to what you'd want but isn't the right answer. Near-miss code from public GitHub repos and Microsoft internal repos, surfaced with LLM assistance. The model was trained explicitly on cases where naive semantic similarity would hallucinate relevance. Code has a property that most text doesn't: `findOne` and `find` are meaningfully different in ways that a model trained on prose will blur. Copilot's model was trained to not make that mistake.

The index is tiered: repos under 750 files get a full local advanced index built automatically by VS Code. 750-2,500 files requires a manual trigger. Above 2,500, it falls back to a basic index. For uncommitted changes, local hybrid search kicks in. The freshness tradeoff is visible here — files you're actively editing may not be in the cloud index yet.

**What the bet reveals:** GitHub has an asset no one else has: the largest corpus of public code on earth. Their embedding model is trained on more code, with better-constructed training examples, than any third-party model can match. The retrieval quality lift is real, and it came from investing in the training data problem more than the architecture problem. Their moat is not the vector database — it's the training data and the distribution advantage of being the default IDE tool for millions of developers.

---

## Sourcegraph Cody: The Multi-Retriever Architecture

Cody is the only tool in the mainstream field with a published conference paper behind its retrieval design (RecSys '24). The architecture is the most explicitly reasoned about in the space.

Rather than picking one retrieval method, Cody runs three in parallel — and they're designed to be complementary, not redundant:

**Keyword retrieval via Zoekt** — a trigram-based full-text search engine Sourcegraph built years before Cody existed. It finds exact symbol matches and keyword variants. Fast, precise, blind to meaning.

**Semantic retrieval via code embeddings** — dense vector search that finds conceptually related code even when the exact terms differ. Slower, higher recall, fuzzier precision.

**Graph-based retrieval via static analysis** — traverses the dependency graph to surface files that the other two methods would miss entirely: callers, callees, related interfaces, shared types. This is the layer that handles cross-file structural relationships.

Results from all three get merged into a ranking stage powered by a transformer cross-encoder model, framed as a knapsack problem: select the most relevant items within the token budget. The ranking model is the final arbiter of what goes into context.

Sourcegraph has also published on why they don't believe long context windows eliminate the need for retrieval: cost, latency, and precision all still favor retrieval for most workloads, even at 128K+ context sizes.

**What the bet reveals:** Sourcegraph built Zoekt long before LLMs existed — it's a mature, battle-tested keyword search engine that was already indexing code for human search. Cody is Sourcegraph's existing code intelligence infrastructure extended with semantic and graph layers. They didn't have to choose between keyword and semantic search because they already had both. The multi-retriever architecture is partly an engineering bet and partly a consequence of their history.

---

## JetBrains Mellum: The Deliberately CPU-Efficient Choice

The most underappreciated retrieval architecture in the space. JetBrains published a full paper on Mellum (arXiv, October 2025) that includes an explicit justification of why they chose IoU-based BPE token overlap over semantic embeddings for inline completion retrieval.

The decision tree works like this: for a given cursor position, collect candidate files from the same directory ranked by line-level Intersection over Union similarity. If the project is highly modular, extend the search via path distance BFS. For larger candidate sets, score chunks using IoU over byte-pair encoded tokens against the cursor context, and select the highest-scoring ones.

No GPU inference. No embedding model to run. No vector database. Just fast token overlap scoring on the CPU.

The reasoning is explicit in the paper: "IoU works well for selecting relevant code chunks while being computationally efficient. Calculating this metric requires minimal computational overhead, unlike more expensive approaches such as cosine distance over semantic embeddings."

For inline completion specifically — where the "query" is the code immediately surrounding your cursor — BPE-token overlap turns out to be a surprisingly strong signal. You're not doing conceptual search; you're looking for code that structurally resembles your current editing context. The precision requirements for completion are different from the semantic discovery requirements of chat or agentic search.

Their production telemetry is interesting: cloud Mellum vs local smaller model shows 14-57% RoCC improvement depending on language. The model capability matters more than the retrieval sophistication for completion quality.

**What the bet reveals:** JetBrains serves hundreds of thousands of active developers with sub-100ms inline completion latency requirements. Semantic embedding inference on every keystroke is not a viable option at that scale and latency target. IoU is fast enough and accurate enough for the specific task of completion context retrieval. It's an engineering choice optimized for real constraints, not a research choice optimized for a benchmark.

---

## The Comparative Picture

Each approach has a genuine advantage in specific conditions:

```
Approach        Precision   Recall   Freshness   Cost    Scale Limit
─────────────────────────────────────────────────────────────────────
Agentic grep    High        Lower    Perfect     Low     Large repos
Vector embed    Medium      High     Index lag   Medium  Unlimited
IoU/BPE         High        Medium   Perfect     Lowest  Completion only
Multi-retriever High        High     Index lag   High    Enterprise
Graph-based     Structural  Medium   Index lag   Highest Large codebases
```

No tool dominates across all dimensions. The workload determines the winner:

- **Unfamiliar codebase, no pre-index possible** → agentic navigation (Devin, Claude Code)
- **Large enterprise multi-repo, conceptual search** → multi-retriever (Cody, Augment Code)
- **Inline completion, latency-critical** → IoU/context-window packing (JetBrains)
- **Team adoption, semantic query, freshness secondary** → shared vector index (Cursor)
- **Training data advantage, scale** → proprietary embed model (Copilot)

---

## The Uncomfortable Research Finding

Here's what the latest academic work says about all of this: more sophisticated retrieval scaffolding delivers only marginal gains in context quality.

ContextBench (February 2026, Nanjing University and UCL) ran 1,136 issue-resolution tasks across 66 repositories and evaluated five coding agents. The headline finding: complex retrieval scaffolding produced only marginal improvements in what context actually gets retrieved. The underlying model matters more than the orchestration. LLMs consistently favor recall over precision — they retrieve too much, not too little. And there's a substantial gap between what an agent *looks at* and what it actually *uses* in its response.

The Agentless paper (UIUC, FSE 2025) found that a simple three-phase approach — find the relevant files, generate the fix, run tests — was competitive with much more complex agentic frameworks, without giving the model tool-calling autonomy at all.

"Keyword Search Is All You Need" (Amazon Science, February 2026) found that agentic keyword search achieves more than 90% of vector RAG performance without a vector database.

None of this makes the retrieval architecture choices irrelevant. A +37.6% retrieval quality lift from a better embedding model is not nothing. Cody's multi-retriever has a published paper showing it handles cases the others miss. But the research pushes back against the assumption that more complex pipelines automatically produce better outcomes.

The companies spending the most engineering effort on retrieval infrastructure are partly betting that the remaining gap — the part sophisticated retrieval actually closes — is where real product differentiation lives. That might be right. It might also be that the gap is smaller than the infrastructure cost justifies, and the next frontier of improvement is somewhere else entirely.

---

Every tool here made a defensible bet. The bets are different because the constraints are different: Sourcegraph had Zoekt. GitHub had the training corpus. JetBrains had latency requirements. Anthropic had a philosophy. Cursor had a team adoption problem to solve.

The retrieval problem is not solved. It's just being solved in different ways by different people with different priors about what matters.

That's what makes it interesting to watch.
