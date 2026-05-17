# OpenFoundry: Stress-Testing the Agnostic Platform Thesis

**Date:** 2026-05-17
**Author:** openfoundry-architect (research agent)
**Audience:** Tenex leadership exploring productization beyond services
**TL;DR:** Agnostic is mostly a positioning narrative, not a defensible architectural moat. The "agnostic everywhere" version of OpenFoundry collapses under operational and economic gravity. A *partially agnostic, opinionated* product anchored on a portable ontology and identity-federated control plane is defensible — but only if Tenex sequences "credible opinion now, agnostic later" and is honest about what gets one-layer-removed from native primitives. The historical precedent for genuinely agnostic moats (Datadog, Snyk, Confluent, HashiCorp) all required >10 years of compounding integrations and ecosystem leverage that Tenex does not currently have at 30 engineers.

---

## Summary

The thesis: F500 enterprises are multi-cloud (Flexera 2025: 70% hybrid, avg 2.4 public clouds + private), multi-LLM, multi-warehouse, and want a Foundry-class control plane that doesn't bundle them into one hyperscaler's stack. OpenFoundry = ontology-driven enterprise OS that works across Anthropic/OpenAI/Google/OSS, Snowflake/Databricks/BigQuery/Postgres, and AWS/GCP/Azure/on-prem.

The verdict after stress-testing:

1. **Agnosticism at the LLM layer** is mostly real and table-stakes (LiteLLM ships 100+ models with OpenAI-compat surface), but the *deep* capabilities — prompt caching economics, tool-use schemas, structured output, programmatic tool calling, multimodal, batching — break the abstraction. Anything more than "string-in / string-out" leaks provider specifics.
2. **Agnosticism at the warehouse layer** is technically possible via Iceberg REST + Polaris/Unity Catalog federation, but the performance and cost geometry punishes federated reads. The pragmatic shape is "Iceberg-first with catalog federation," not "federate everything."
3. **Cloud-agnostic deployment** requires BYOC architecture (control plane / data plane separation) — operationally a 3x tax in support and on-call.
4. **The genuine moat candidate is not "we support everything"** — it is "the ontology is a portable artifact that travels across systems with consistent semantics, lineage, and policy." Everything else (model gateway, warehouse federation, IdP plumbing) is commoditized infrastructure.
5. **Verdict for Tenex:** Productize the ontology + identity-federated policy layer first. Be Anthropic-first, Snowflake-first (or Databricks-first), AWS-first in V1. Earn the right to add the second and third by demonstrating the ontology travels. Use "OpenFoundry" as the *long-term vision* in CIO conversations, but ship an opinionated product. Anything else burns the 30-engineer team trying to maintain a connector farm.

---

## Key Findings

### 1. Agnostic as architecture vs. agnostic as marketing

The honest split:

```
                MARKETING POSITION                ARCHITECTURAL MOAT
                ────────────────────              ──────────────────
LLM-agnostic    "Works with any model"            Cross-provider eval/routing,
                                                  cache-aware orchestration,
                                                  graceful tool-schema degradation
                ────────────────────              ──────────────────
WH-agnostic     "Iceberg REST compatible"         Lineage-aware pushdown w/
                                                  federated permissions across
                                                  Unity ↔ Horizon ↔ Glue
                ────────────────────              ──────────────────
Cloud-agnostic  "Runs on AWS/GCP/Azure"           Zero-access BYOC w/
                                                  customer-managed keys,
                                                  one-control-plane many-DP
                ────────────────────              ──────────────────
IdP-agnostic    "Federates Okta/Entra/Auth0/Ping" Real-time permission
                                                  inheritance into ontology
                                                  + per-cell ABAC
                ────────────────────              ──────────────────
Ontology        "Define once, use anywhere"       Versioned, diff-able,
portability                                       exportable schema + policy
                                                  bundle that round-trips
```

The left column gets you on a slide deck. The right column is what F500 buyers actually pay for after the second POC. Tenex must be honest about which version it is shipping.

### 2. LLM-agnosticism: where the abstraction leaks

LiteLLM is the de facto reference. It exposes ~100 providers under an OpenAI-compatible `/chat/completions` and `/messages` surface, handles auth translation, maps exceptions, and provides spend tracking and virtual keys. Helicone, Portkey, OpenRouter, TrueFoundry are all variations on the same pattern. This part is commoditized; selling it as a moat is naive.

What actually breaks at the abstraction boundary:

| Capability | Anthropic | OpenAI | Gemini | Abstraction leak |
|---|---|---|---|---|
| Prompt cache read discount | 90% (0.1x) | 50% | ~90% | Massive cost-routing implication — same workload can be 5x more expensive on OpenAI |
| Cache write premium | 1.25x (5m) or 2x (1h) | None | None (implicit) | Cache-aware orchestration cannot be uniform |
| Cache control | Explicit breakpoints (4) | Auto only | Implicit + explicit storage fee ($4.50/MTok/hr) | An "agnostic" prompt API has to either pick the LCD or expose provider-specific knobs |
| Min tokens to cache | 1,024–4,096 (per model) | 1,024 | 32,768 (explicit) | A "uniform cache hint" silently fails on Gemini for sub-32k prompts |
| Tool use schema | `tool_use` blocks + `cache_control` | function-calling JSON | function declarations | Translatable, but `tool_choice`, `disable_parallel_tool_use`, programmatic calling (allowed_callers) do not map cleanly |
| Structured output | `strict` not supported w/ programmatic | `response_format` + strict schemas | response schema | Strict-mode constraints differ — agentic workflows that depend on structured output have to test per-provider |
| Programmatic tool calling | Sonnet 4.5/Opus 4.5 + Bedrock + Foundry, NOT Vertex | n/a | n/a | Multi-provider parity is a moving target |
| Multimodal (vision, audio, video) | Vision yes, audio limited | Vision + audio | Vision + audio + native video | Routing a vision-heavy workflow uniformly requires picking the LCD |
| Batch API | Yes, 50% off | Yes, 50% off | Yes | Batch + cache interaction is provider-specific |
| Streaming protocol | SSE w/ event types | SSE delta | SSE | Translatable but error semantics differ |

The takeaway: **"Switch from Claude to GPT to Gemini mid-workflow" is a real capability for the cheapest 30% of agentic work and a dangerous abstraction for the top 70%.** Anyone selling LLM-agnosticism as a value prop is selling commodity routing. The actual moat is *cost-aware, capability-aware orchestration*: route prompts to the optimal model given cache locality, structured-output requirements, tool-use parity, and latency SLA. That is a much harder product than a gateway.

### 3. Warehouse-agnosticism: federation vs. pushdown vs. copy

Three architectural approaches; each has economic gravity:

**(a) Federated query (Trino / Starburst / Dremio).** Trino's generic JDBC connector hits a ~36 MB/s single-threaded ceiling per connection (Starburst's own writeup). Predicate, aggregation, and Top-N pushdown help, but full-query passthrough is needed for performance parity with native execution. Starburst's measurement: full-query-passthrough Teradata = 2x faster than JDBC pushdown for the same query. Federation works for ad-hoc cross-source analytics; it fails for high-concurrency production workloads above the terabyte boundary.

**(b) Pushdown query generation (dbt approach).** Generate native SQL per dialect. Works well for batch transformation; doesn't help with operational ontology serving (low-latency reads, writebacks).

**(c) Copy-data integration (Fivetran approach).** Solves performance, defeats the "no vendor lock-in" promise — now you have data in N copies in N warehouses.

The 2025–2026 inflection: **Apache Iceberg + REST Catalog APIs are collapsing this into a fourth option** — a single physical copy, queried natively by Snowflake, Databricks, Trino, Flink, DuckDB, Spark, Dremio. Unity Catalog (Public Preview as of Data+AI Summit 2025) federates AWS Glue, Hive Metastore, and Snowflake Horizon Iceberg tables. Snowflake Horizon (GA 2025) exposes Iceberg REST endpoints with Polaris (Apache project). Both Databricks and Snowflake now sell "we govern the open table format you bring."

This is the most important shift for the OpenFoundry thesis. **An agnostic data layer in 2026 is no longer "abstract over Snowflake/Databricks/BigQuery" — it is "compose on top of Iceberg + a federated catalog."** That changes the build:

- The realistic V1 supports Iceberg tables in customer-owned S3/ADLS/GCS, governed by Unity Catalog OR Horizon OR Polaris (customer's choice).
- BigQuery becomes a connector via BigLake (which now reads Iceberg). Redshift via Spectrum + Iceberg. Postgres via foreign data wrappers or a sync.
- The ontology references Iceberg tables natively; lineage, masking, and ABAC are inherited from whichever catalog the customer uses, with OpenFoundry layering a *semantic* policy on top.

The risk: **Iceberg standardization is exactly what makes "warehouse-agnostic" no longer a real moat for OpenFoundry.** Whoever federates the catalogs first (Databricks via Unity is already public preview) captures the governance layer. If OpenFoundry's only differentiation is "Iceberg federation," it is racing Databricks and Snowflake to commoditize what Databricks and Snowflake have already commoditized.

### 4. Cloud-agnosticism: BYOC as the only credible answer

For F500 with data residency, sovereignty, GDPR, HIPAA, DORA, NIS2, and FedRAMP requirements, multi-tenant SaaS is increasingly disqualifying. The Tensor9 / Nuon / Pinecone / Confluent / WarpStream pattern is now the industry-standard answer: **split control plane (vendor cloud) from data plane (customer VPC), zero-access architecture, customer-managed keys, audited egress-only metadata channel.**

Operational reality of running BYOC for OpenFoundry across three hyperscalers + on-prem:

| Burden | Multi-tenant SaaS | BYOC across AWS/GCP/Azure |
|---|---|---|
| Observability | Dashboard hits in minutes | Ship collectors into customer perimeter, never see payloads |
| Upgrades | Push once | Per-tenant phased rollout, conformance testing per cloud |
| Support escalation | Read production logs | Customer-mediated diagnostics, redacted telemetry |
| Incident response | Direct fix | Coordinate with customer SRE under their change-control |
| Compliance | Inherit vendor's SOC2 | Inherit *each customer's* SOC2/HIPAA/FedRAMP/GDPR |
| Margin | 75-85% | 50-70% (per Confluent, Pinecone disclosures) |

Tensor9's playbook (validated across dozens of BYOC deployments): build "platform intelligence" centrally, ship "hardened data planes" per customer, accept that delivery + support eats most engineering cycles in year 1-2.

**For a 30-engineer Tenex team, supporting BYOC across three hyperscalers from V1 is not survivable.** The pragmatic path: ship multi-tenant SaaS on AWS first; add BYOC-on-AWS once a flagship F500 demands it; add Azure BYOC for the second; add GCP last. Each takes 2-3 engineers of dedicated maintenance forever.

### 5. Identity-agnosticism (covered in prior research)

Briefly: Okta, Entra, Auth0, Ping all federate via SAML/OIDC/SCIM. The plumbing is solved. The hard part is **per-row, per-cell ABAC that inherits from the IdP's group + attribute graph and is enforced in the ontology layer.** Unity Catalog ABAC (Beta, 2025) and Horizon tag-based masking have set the bar. OpenFoundry's identity story has to assume this is table stakes by 2026.

### 6. Ontology portability — the real moat candidate

Foundry's actual moat is not the warehouse layer or the LLM layer. It is the **Ontology** as the four-fold integration of data, logic, action, and security (Palantir's own framing). Foundry's docs are unambiguous: the Ontology is "a multimodal system consisting of dozens of underlying components — a Language, an Engine, and a Toolchain."

The open-source replication argument (Dataworkers, April 2026): semantic layer (dbt metrics / Cube / LookML) + catalog (DataHub / OpenMetadata) + orchestration (Dagster / Temporal) + action layer (MCP) covers ~70-80% of the ontology capability — but with significant integration tax. The remaining 20-30% gap is *polish + integration density*, which is exactly where a product like OpenFoundry could create defensibility.

The defensible question for OpenFoundry: **is the ontology a portable artifact?**

- Can a customer export their ontology (object types, properties, link types, action types, function definitions, policy bundle) as a versioned, diff-able, declarative spec?
- Can it round-trip into a second deployment (e.g., on a different warehouse) with semantics preserved?
- Can it cross-customer share certified objects (a "PurchaseOrder" object type with industry-standard semantics)?

If yes — the ontology becomes the network-effect artifact. Cross-customer policy libraries, certified ontologies per vertical, partner extensions. This is what Glean is building toward with its "agent library" and Atlan with its "Context Layer for AI / MCP server / certified context flows."

If no — OpenFoundry is just a thinner UI on top of the underlying lakehouse, and there is no moat.

### 7. Competitive geometry

```
                          OPEN / AGNOSTIC
                                │
              Vendia ──── Glean ──── OpenFoundry?
              (MCP        (search    (ontology
              gateway,    + agent     + workflow
              audit)      orchestr.)  + agent)
                                │
                                │
Vertical    ────────────────────┼──────────────────── Horizontal
                                │
(Cognite,                       │            (Foundry, Databricks,
AVEVA,                          │             Snowflake, Fabric,
SymphonyAI,                     │             Atlan)
ABB)                            │
                                │
                                │
                Fabric ──── Databricks ──── Snowflake
                                │
                          CLOSED / BUNDLED
```

**Where OpenFoundry would sit (proposed):** upper-right quadrant — horizontal, agnostic. This is *not* where Foundry lives (Foundry is upper-bundled if anything, since it's tied to its own stack; vertical-ish in practice through industry templates).

**What dominates the upper-right today?**
- **Glean:** Best LLM-agnostic, connector-driven horizontal AI search; ships 100+ pre-built connectors, real-time permissions inheritance, agent builder. Sells "ask anything across your enterprise" — a *retrieval* and *agent orchestration* product, not an *ontology* product. Has explicitly committed to LLM-agnosticism with Claude/Gemini/GPT support.
- **Atlan:** Modern data catalog as control plane; "Context Layer for AI" with MCP server, certified context flows, AI-bootstrapped documentation, 80+ connectors. Has 2025 momentum as the agnostic catalog of record.
- **Vendia:** MCP gateway + audit ledger; integrates APIs, S3, MCP servers; immutable audit logs. Narrow but real.
- **Databricks (extending up):** Unity Catalog open-sourced, Iceberg-federated, ABAC GA-ing; explicitly committed to "open lakehouse" and the Databricks AI Functions agent layer.

**What does OpenFoundry beat?**
- It would beat *Glean* on operational write-back / action orchestration (Glean is read-mostly).
- It would beat *Atlan* on agent orchestration and ontology runtime (Atlan is metadata-first).
- It would beat *Vendia* on data modeling and policy depth (Vendia is gateway-thin).
- It would *not* beat *Databricks Unity / Snowflake Horizon* on warehouse-native governance — and trying to is a mistake. The play is to compose on top of them.

**What does it lose to?**
- It loses to Foundry on enterprise distribution, deployment muscle, and forward-deployed engineering — Palantir's actual moat is people + integration density.
- It loses to Databricks / Snowflake / Microsoft Fabric on hyperscaler co-sell economics.
- It loses to Glean on RAG quality and connector breadth in year 1-2.

### 8. Industrial DataOps as a reference frame

IDC MarketScape Industrial DataOps 2026 names Cognite a Leader. Verdantix Green Quadrant 2025 names ABB, AVEVA, Cognite, Inductive Automation, Palantir, SymphonyAI as IDM leaders. The common thread: **they all sell agnostic, purpose-built platforms for industrial data foundations.** IDC's Jonathan Lang: *"Companies that adopt agnostic, purpose-built platforms for building and managing the data foundation have been particularly successful in scaling up and out."*

The lesson is double-edged: agnostic + vertical-specialized wins (Cognite, AVEVA). Agnostic + horizontal-undifferentiated loses (it's the layer everyone wraps and commoditizes). OpenFoundry as proposed is horizontal — which raises the bar enormously.

### 9. Structural advantages of being agnostic (the case FOR)

1. **TAM expansion.** 70% of enterprises are hybrid (Flexera 2025); avg 2.4 public clouds + private. Anchoring on one hyperscaler immediately disqualifies 50%+ of large deals.
2. **Switzerland positioning.** Partner with everyone, threatened by none. Confluent built this stance with Snowflake + Databricks integrations as a Kafka-level dependency. HashiCorp built it with multi-cloud Terraform.
3. **CIO-side hedging.** A CIO buying an agnostic layer is hedging against AWS price increases, Snowflake credit inflation, OpenAI rate-limiting. The agnostic vendor sells *optionality*.
4. **Data residency / sovereign cloud compliance.** A BYOC-capable agnostic product can deploy in any region, any sovereign cloud — table stakes for EU/UAE/GCC.
5. **Easier compliance simplification.** When data stays in the customer's cloud, the vendor inherits the customer's existing SOC2/HIPAA/FedRAMP controls (Nuon's pitch).

### 10. Structural disadvantages of being agnostic (the case AGAINST)

1. **Loss of integration depth.** Always one layer removed from native primitives. When Snowflake ships a new Cortex capability or Databricks ships Lakebase, the agnostic vendor is 6-18 months behind.
2. **Slower feature parity.** N x M problem: every new capability has to be wrapped for every provider. Engineering velocity halves.
3. **No hyperscaler tailwinds.** AWS, Azure, GCP all push first-party stacks. A multi-cloud-neutral vendor gets less co-sell support, less marketplace promotion, fewer joint accounts.
4. **3x operational complexity.** Every connector, every cloud, every region, every IdP, every catalog has to be tested, monitored, and updated.
5. **Lower margins.** No marketplace rev share at the same scale as a single-hyperscaler-deep partner.
6. **Easier to commoditize.** Every "agnostic" capability has a hyperscaler-native equivalent. OpenAI's AI Foundry on Azure, AWS Bedrock + Q, Google's Vertex AI Agent Builder — each is bundled, subsidized, and "good enough" for 60% of workloads.

### 11. What prior agnostic plays show

- **Snyk** — Cloud-agnostic dev-security platform. Moat: developer-first IDE integration + CI/CD plumbing + signature DB. Took 8+ years to compound. Now faces commoditization from GitHub Advanced Security + native cloud tools.
- **Datadog** — Cloud-agnostic observability. Moat: 700+ integrations + dashboard switching cost. Took 10+ years. Now faces Azure Monitor / AWS CloudWatch + Grafana on the low end. KoalaGains analysis (2026): "few large companies rely on just one cloud vendor… few large companies rely on just one cloud vendor" is the durable thesis.
- **HashiCorp Terraform** — Cloud-agnostic infrastructure-as-code. Moat: provider DSL + state management. Acquired by IBM for $6.4B in 2024. Was effective but margin-constrained; couldn't capture the value of the workloads it provisioned.
- **Confluent** — Cloud-agnostic streaming. Moat: Kora engine + 120+ connectors + multi-cloud Cluster Linking. Pumice Capital (2025) is blunt: *"Confluent's multi-cloud, vendor-neutral approach provides some differentiation, but it's not significantly restrictive to competitors. Counter-positioning currently offers minimal competitive insulation."* The moat is integration depth, not neutrality itself.

**Pattern:** All four agnostic winners spent 8-15 years compounding integration breadth and developer adoption. Neutrality was the *frame*; the moat was *the integration count + the workflow ownership*. **OpenFoundry cannot replicate this in year 1-2 with 30 engineers.** It can replicate it on a much narrower surface — say, "the ontology + identity-federated policy layer over Iceberg" — if it picks a tight scope.

### 12. Required V1 capabilities for *credible* agnosticism

Even a partially-agnostic V1 needs these to be defensible:

1. **Model abstraction with capability-aware degradation.** Don't just translate API surfaces — surface the diff (cache discount, tool-schema features, multimodal support, batch availability) so workflows are routed intelligently. Cost-aware + latency-aware routing as a first-class feature.
2. **Iceberg-first warehouse layer with catalog federation.** Customer-owned object storage. Read/write via Iceberg REST. Unity / Horizon / Polaris all supported as the catalog source of truth.
3. **BYOC deployment on at least one hyperscaler in V1.** Anchored on AWS makes the most sense (largest market share, broadest enterprise distribution).
4. **Ontology as portable artifact.** Declarative DSL or YAML/JSON spec for object types, properties, links, actions, functions, policy bundles. Version-controlled, exportable, diff-able. CLI + GitOps.
5. **Identity federation to any major IdP.** SAML/OIDC/SCIM for authN; ABAC engine that inherits IdP attributes for per-cell row/column enforcement.
6. **One genuinely hard "magic" capability.** Lineage-aware permissions (a permission change on a source table propagates through derived ontology objects); cross-customer policy library (certified industry ontologies); auto-ontology inference from existing warehouse tables. Pick one and dominate it.

If V1 doesn't have all six, the product is undifferentiated middleware.

### 13. Tenex-specific reality check

- **Distribution is real.** Tenex's $15M ARR + F500 channels + $300/storypoint pricing is a genuine asset. CIOs buy people they trust. The product gets a hearing it would not otherwise.
- **30 engineers is the constraint.** Building OpenFoundry as scoped above (LLM + WH + cloud + IdP + ontology + BYOC) requires ~80-100 engineers in year 1. Trying to ship all of it with 30 means shipping none of it well.
- **The credible V1 is opinionated.** "Anthropic-first, Snowflake-first (or Databricks-first — pick one), AWS-first, Okta-first." That is shippable in 9-12 months and demos against Foundry in head-to-head F500 evals. Agnostic surface area gets added over the next 24 months, paid for by the first $5M in ARR.
- **"OpenFoundry" works as the **public** vision narrative.** CIOs respond to "we will be your control plane regardless of your stack choices." Internally, the engineering org should be ruthlessly opinionated about what V1 actually supports.
- **The credible Y2/Y3 roadmap looks like:**
  - Y1: Anthropic + Snowflake (or Databricks — pick) + AWS + Okta. BYOC-on-AWS by end of year. Ontology DSL v1. 2-3 lighthouse customers.
  - Y2: Add OpenAI as second model provider with capability-degradation handling. Add Iceberg-on-Databricks (or Snowflake) as second warehouse. Add Azure BYOC. Add Entra ID federation. Cross-customer policy library v1.
  - Y3: Add Gemini. Add BigQuery. Add GCP BYOC. Add the second IdP that wins the next big deal. Auto-ontology inference. Vertical certified ontologies.

This is "agnostic on paper, opinionated in shipping." It is the only path that survives the math.

### 14. Is agnostic a moat or a position?

Cynical read: agnostic = "we wrap everything with a thin UI." Easy to clone. No defensibility. Every YC batch ships an LLM gateway and a catalog wrapper.

Generous read: agnostic + portable ontology + customer-specific metadata graph + lineage-aware policy = a real network effect. The hyperscalers cannot be agnostic because their business model demands lock-in. That structural gap is exploitable.

The evidence from Snyk/Datadog/HashiCorp/Confluent says **both reads are partially right.** Agnosticism alone is not a moat — but agnosticism *combined with sufficient integration depth and workflow ownership* is, and it takes a decade to build. For Tenex, the question is not "is agnostic a moat?" — it is "do we have ten years and the capital to compound integration depth?" If yes, OpenFoundry as scoped is a long-term bet worth making. If no, ship the opinionated V1 and let the "open" story be a CIO-conversation accelerant, not a product spec.

---

## Verdict

**On the OpenFoundry thesis as stated:** Half-right.

- **Right:** F500 is multi-everything by necessity; an agnostic control plane is what they say they want when interviewed; hyperscaler bundles do have pricing power that CIOs want to hedge.
- **Wrong:** "Agnostic across LLMs, warehouses, clouds" as a *V1 architecture* is operationally and economically suicidal for a 30-engineer team. The capability surface is too wide; the abstraction leaks too much; the engineering tax is 3x.
- **The actual moat candidate** is portable ontology + lineage-aware policy + identity-federated ABAC, *composed on top of Iceberg + one warehouse + one model provider in V1*, with credibility to add the second and third over years.

**On the Tenex-specific play:**

1. **Pick the V1 opinion.** Anthropic-first (Tenex already has this muscle). Pick Databricks OR Snowflake — not both — based on which lighthouse F500 customer you want to land first. AWS-first. Okta-first.
2. **Build the ontology as the moat artifact, not the gateway.** A portable, versioned, diff-able ontology spec is the only thing the hyperscalers cannot ship credibly because their business models prevent it.
3. **Use "OpenFoundry" as the marketing horizon.** In CIO conversations, lean into "we will not lock you to one hyperscaler" — it is true at the *product roadmap* level even if year 1 ships against one stack. Do not promise V1 agnosticism you cannot ship; the F500 demo room is unforgiving.
4. **Sequence BYOC carefully.** Multi-tenant SaaS-on-AWS for V1. BYOC-on-AWS by month 9-12 when the first F500 demands it. Azure BYOC in year 2. GCP BYOC in year 3.
5. **Use services revenue as the bridge.** The $300/storypoint pricing is what funds productization. Engagements should be structured as "deliver a Foundry-equivalent ontology on your stack" → "convert to OpenFoundry SaaS." This is the Palantir FDE playbook with a product anchor.

**The line for Tenex leadership:** OpenFoundry as a public vision is sellable. OpenFoundry as a V1 product spec is undeliverable. Pick the discipline: ship opinionated, narrate agnostic, earn the right to expand surface area with each subsequent F500 win.

---

## Sources

1. **Flexera 2025 State of the Cloud Report** — 70% hybrid, 2.4 public clouds avg, AWS/Azure neck-and-neck. https://www.flexera.com/blog/finops/the-latest-cloud-computing-trends-flexera-2025-state-of-the-cloud-report/
2. **Palantir Foundry Ontology architecture docs** — Language + Engine + Toolchain framing. https://palantir.com/docs/foundry/architecture-center/ontology-system/
3. **Dataworkers — Palantir Ontology Open Source Alternative (April 2026)** — 70-80% coverage of Foundry ontology via OSS. https://dataworkers.io/resources/palantir-ontology-open-source-alternative/
4. **LiteLLM docs** — 100+ providers, unified OpenAI surface, programmatic tool calling. https://berriai.github.io/litellm/
5. **AgentPatterns — Prompt Cache Economics by Provider** — Anthropic 90%, OpenAI 50%, Gemini ~90% read discounts; cache write economics. https://agentpatterns.ai/context-engineering/prompt-cache-economics/
6. **Starburst — JDBC Bottleneck in Trino + Full Query Passthrough** — federated query performance reality. https://starburst.io/blog/jdbc-trino-starburst, https://starburst.io/blog/introducing-full-query-passthrough-for-faster-query-federation
7. **Databricks Unity Catalog Data+AI Summit 2025** — Iceberg REST GA reads / PP writes, Iceberg catalog federation PP, ABAC Beta. https://databricks.com/blog/whats-new-databricks-unity-catalog-data-ai-summit-2025
8. **Snowflake Horizon Catalog Iceberg REST PP (Dec 2025)** — Polaris-powered open interop. https://medium.com/snowflake/unlock-open-interoperability-with-horizon-catalog-89ae67b7ee66
9. **Snowflake Polaris Catalog announcement (June 2024)** — vendor-neutral Iceberg catalog. https://investors.snowflake.com/news/news-details/2024/Snowflake-Unveils-Polaris-Catalog…
10. **Tensor9 — BYOC Design Playbook (Jan 2026)** — control plane / data plane separation, metadata vs payload, zero-access architecture. https://www.tensor9.com/resources/byoc-playbook/
11. **Confluent — Bring Your Own Cloud explainer** — BYOC tradeoffs vs SaaS. https://confluent.io/learn/bring-your-own-cloud
12. **Pinecone BYOC** — zero-access operating model reference. https://www.pinecone.io/product/bring-your-own-cloud/
13. **IDC MarketScape Industrial DataOps 2026 — Cognite Leader** — agnostic platforms win in industrial vertical. https://www.businesswire.com/news/home/20260319090389/en/
14. **Verdantix Green Quadrant IDM 2025** — ABB, AVEVA, Cognite, Inductive Automation, Palantir, SymphonyAI as leaders. https://www.verdantix.com/report/green-quadrant-industrial-data-management-solutions-2025
15. **Glean Agents announcement** — LLM-agnostic agentic reasoning engine, 100+ connectors. https://www.glean.com/blog/agents-product-blog
16. **Atlan vs Collibra (2026)** — Context Layer for AI, MCP server, certified context flows. https://www.modern-datatools.com/compare/atlan-vs-collibra
17. **Vendia MCP Gateway** — MCP-driven federation across APIs/S3/SaaS with audit ledger. https://www.vendia.com/platform/mcp-gateway/
18. **LLM Gateway Review 2025** — TrueFoundry, Portkey, Helicone, LiteLLM, OpenRouter comparison. https://wavesandalgorithms.com/reviews/llm-gateway-review
19. **TrueFoundry vs Portkey** — gateway depth vs full-stack infrastructure. https://www.truefoundry.com/truefoundry-vs-portkey
20. **Datadog Moat Analysis 2026** — multi-cloud agnostic positioning, 700+ integrations, switching cost moat. https://koalagains.com/stocks/NASDAQ/DDOG/business-and-moat
21. **Confluent CFLT Long Thesis (Pumice Capital, June 2025)** — *"counter-positioning offers minimal competitive insulation"* — agnostic neutrality not enough. https://www.pumicecapital.com/p/confluent-cflt-long-term-investment-thesis
22. **Horkan — Databricks vs Snowflake vs Microsoft Fabric (Sept 2025)** — competitive geometry. https://horkan.com/2025/09/22/databricks-vs-snowflake-vs-microsoft-fabric-positioning-the-future-of-enterprise-data-platforms
23. **Nuon — BYOC enterprise buyer guide** — five evaluation questions for BYOC vendors. https://www.nuon.co/buyers
