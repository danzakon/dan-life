---
id: 20260517-RS-002
date: 2026-05-17
category: Research Report
content-status: raw
---

# Tenex → OpenFoundry: A 360° Strategy for Productizing a $15M-ARR Forward-Deployed AI Services Business

> Companion to `20260517-rbac-ai-agents-modern-foundry-wedge.md`. That report argued an industry-wide thesis on agent access control as the wedge into a modern Foundry. **This report is the company-specific operationalization for Tenex** — anchored on $15M ARR, $300/$80 storypoint economics, a growing FDE bench, and F500 distribution. The conclusion is sharper than the industry thesis: **build Tenex Ontology — an agent-ready data layer with bundled MCP governance — as the beachhead, using the FDE motion as the discovery engine, and earn the right to "OpenFoundry" over 24–36 months.**

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [The Strategic Question](#the-strategic-question)
3. [Part I — Foundry, Deeply Understood](#part-i--foundry-deeply-understood)
4. [Part II — Ontology, Deeply Understood](#part-ii--ontology-deeply-understood)
5. [Part III — Salesforce as the Other Reference Architecture](#part-iii--salesforce-as-the-other-reference-architecture)
6. [Part IV — Services-to-Product Economics for Tenex](#part-iv--services-to-product-economics-for-tenex)
7. [Part V — The Beachhead: Tenex Ontology](#part-v--the-beachhead-tenex-ontology)
8. [Part VI — OpenFoundry: The Vision Honest About Its Trajectory](#part-vi--openfoundry-the-vision-honest-about-its-trajectory)
9. [Part VII — The 36-Month Roadmap and Capital Allocation](#part-vii--the-36-month-roadmap-and-capital-allocation)
10. [Key Takeaways](#key-takeaways)
11. [Predictions and Falsifiable Bets](#predictions-and-falsifiable-bets)

---

## Executive Summary

Tenex's instinct is right: this is the inflection point. At $15M ARR, services-led AI transformation businesses either commit to a product spine or drift toward the consultancy gravity well, where revenue scales linearly with headcount and gross margin is structurally capped at ~35–40%. Cresta, Tribe AI, Distyl, and Tryolabs are the cautionary tales; Palantir, Sierra, and Decagon are the proof points that the transition is possible — but each used a different mechanism and the failure modes are louder than the successes.

The single most important decision Tenex faces in the next 90 days is **which of the three candidate products to bet the spine team on**: agent RBAC / access control plane, self-learning data/ontology platform, or agent platform. The full team analysis — six parallel research streams across Foundry's architecture, ontology theory, the Salesforce reference, services-to-product economics, head-to-head product comparison, and OpenFoundry stress-testing — converges on one answer with high confidence: **build the ontology platform with bundled governance**.

The reasoning, condensed:

- **Agent platform** is the most crowded space in software. Sierra ($10B / $150M ARR), Decagon ($4.5B / $35M ARR), Cognition Devin ($10.2B / $155M ARR), plus every framework and every hyperscaler. Tenex has no defensible advantage here; the runtime layer is being absorbed by the frontier model labs.
- **Agent RBAC** is the industry-correct wedge for *someone*, but that someone is Microsoft, Okta, AWS, Palo Alto, or CrowdStrike — not a 1-year-old engineering services firm. Microsoft Entra Agent ID GA'd in May 2026, Okta for AI Agents on April 30, 2026, AWS Bedrock AgentCore Gateway in nine regions. Standalone agent identity is becoming a feature, not a product, within 18 months. Selling to CISOs requires DNA Tenex doesn't have and can't credibly build.
- **Self-learning ontology platform** is the only candidate that scores above 3.0 on a 10-dimension weighted comparison. It attaches to ~80% of Tenex's existing F500 engagements without changing the buyer; it captures the data-modeling output that today walks out the door at the end of every engagement; it compounds into the deepest moat in enterprise software (customer-specific ontology); and it is the only candidate where Year 1 → Year 3 is a single product evolution rather than a strategic pivot.

The critical refinement of the industry thesis: **the MCP-gateway / agent-RBAC capability survives, but as a bundled governance feature of the ontology product, not as a standalone SKU.** This is the synthesis. Pure ontology without governance becomes a Glean-shaped knowledge graph that competitors route around. Pure RBAC commoditizes against hyperscaler bundles. Ontology where governance is the access mode — where the ontology is the *only safe path* to enterprise data — is what becomes OpenFoundry.

The recommended capital allocation at $15M ARR is a **milestone-gated barbell**: keep ~85% of engineering on billable work to ride the demand wave, carve out 6 spine engineers + 1 PM + 1 founding AE + 1 PMM reporting directly to the CEO with a separate P&L, invest $3–4M in year 1 (≈25–30% of realized gross margin), and gate the doubling-down decision on three paying product customers at ≥$100K ARR each by month 12. Below that bar, harvest more aggressively and accept a services destiny. Above it, raise a $15–25M Series A on product trajectory + services cash flow and expand into the operational app layer.

"OpenFoundry" is the **public vision narrative** — agnostic across LLMs, warehouses, and clouds is what F500 CIOs respond to. But the **V1 product** must be opinionated: Anthropic-first, one warehouse (pick Snowflake or Databricks based on your first lighthouse customer), AWS-first, Okta-first. The "ship opinionated, narrate agnostic" discipline is what separates a deliverable product from a deck slide. The right of agnosticism is earned with each F500 win, not promised in the V1 spec.

The arc is Palantir's, compressed: 13 years for them, 36 months for Tenex if the discipline holds. Every quarter, the metric to watch is *what percentage of new-logo first-dollar revenue came from the product versus the engagement*. If that climbs from 5–10% (Y1) → 20–30% (Y2) → 40–50% (Y3), the productization is happening. If it doesn't, Tenex has become Tribe AI with a different logo.

---

## The Strategic Question

Tenex stands at the inflection point where three trajectories diverge:

```
                       Trajectory A: Permanent Consultancy
                       (Cresta, Tribe, Distyl, Tryolabs)
                       Gross margin caps at 35-40%, revenue
                       scales linearly with headcount, exit
                       multiples are 2-4x revenue.

   Tenex at $15M ───►  Trajectory B: Services + Asset Library
   ARR, $300/$80,      (Accenture-shaped, McKinsey QuantumBlack
   FDEs, F500 dist.    Brix, BCG SynOps)
                       Gross margin 35-50%, asset library
                       accelerates delivery, exit profile is
                       a strategic acquisition by a Big 4.

                       Trajectory C: Product Spine + FDE Discovery
                       (Palantir, Sierra at compressed pace)
                       Gross margin climbs to 70-80%, exit
                       multiples 15-40x revenue, decade-long
                       compounding moat.
```

The first two trajectories are stable and survivable — many great businesses live there. The third is the prize. The question is whether Tenex has the conditions for trajectory C, and what the first concrete steps look like.

The conditions for trajectory C, from the case-study record:

| Condition | Tenex status |
|-----------|--------------|
| ARR/FTE at or above $300K threshold | ✓ ~$300K (right at the lower edge of healthy) |
| Repeated delivery patterns across multiple customers | ✓ Implied by storypoint pricing and FDE motion |
| Customer relationships deep enough to deposit metadata, not just code | ✓ F500 channels growing |
| Cultural willingness to separate product P&L from services P&L | Unknown — this is the test |
| Capital structure that can absorb 1–3 years of dilutive product investment | Unknown — current cash position determines |
| Founder/leadership conviction to resist the consultancy gravity well | Unknown — it always feels like a choice in real time |

The remainder of this report assumes the answer to the bottom three is "yes, with discipline." If any of them is "no," the right strategy is trajectory B (Accenture-shaped asset library inside a services business). Trajectory B is *not a failure*; it is just a different game.

---

## Part I — Foundry, Deeply Understood

Tenex cannot productize a Foundry-equivalent without absorbing what Foundry actually is. The prior research report sketched Foundry's moat as ontology + FDE motion + compliance posture. This deeper dive identifies the engineering primitives that are genuinely load-bearing versus the surface area that is replaceable.

### 1.1 The architectural decomposition

Foundry is three layers stacked on a delivery system:

```
┌────────────────────────────────────────────────────────────┐
│  AIP — generative AI platform                              │
│  (k-LLM access, Agent Studio, AIP Logic, Evals, Analyst)   │
├────────────────────────────────────────────────────────────┤
│  Foundry — data ops + Ontology + applications              │
│  (Pipeline Builder, Code Repos, Workshop, Slate, Quiver,   │
│   Vertex, Object Views, Actions, Functions, OSDK)          │
├────────────────────────────────────────────────────────────┤
│  Apollo — continuous delivery / infra orchestration        │
│  (thousands of zero-downtime upgrades, on-prem to cloud)   │
└────────────────────────────────────────────────────────────┘
```

The internal architecture decomposes into roughly thirteen named primitives. The ranking by replicability difficulty matters more than the ranking by visibility:

**Tier 1 — Absolutely load-bearing (must ship in v1):**

1. **Object Storage V2 (OSv2) and the Funnel.** This is the most underrated piece of Foundry. Everyone talks about "the Ontology" as if it's a schema; in practice the Ontology is a *specific database* (OSv2) and a *specific orchestrator* (Funnel) wearing a semantic layer hat. OSv2 is a purpose-built indexed object database that supports row-level and cell-level security policies decoupled from the underlying dataset permissions, and stores user edits in the same store as ingested data with explicit conflict-resolution. The Funnel is the write-path microservice that reads from datasets, restricted views, streams, and Actions, indexes everything into OSv2, and is the single biggest reason the Ontology can be both a derived view of a data lake *and* a system-of-record for operator edits. **Nobody outside Palantir has built this.**
2. **Action types.** Typed schemas for transactional mutations with side effects. Parameters (typed, constrained, environment-aware), rules (add/modify/delete objects, function rules), submission criteria (server-side preconditions), side effects (webhooks, notifications), security (permission-checked at submission). Crucially, **Actions are the only sanctioned write path** — even AIP Logic's LLM tool calls route through Action submission. This is the architectural invariant that makes "agent RBAC" tractable: agents have permissions to invoke Actions, not raw row-level writes.
3. **Functions (FOO — Functions on Objects).** Typed sandboxed code (TypeScript v2, Python, Java) that reads/writes the Ontology via the SDK and is callable from Workshop, Slate, OSDK clients, Action rules, automations, and AIP Logic. The bridge from "data exists" to "the ontology has behavior."
4. **OSDK (Ontology SDK).** Auto-generated typed client code (TS/Python/Java) that mirrors a specific customer's Ontology, published as a versioned npm/pip package. The outbound API of the Ontology. What makes Foundry useful even when you're not in Foundry's own UI.
5. **Lineage-aware permission propagation.** Markings inherited along data lineage; `stop_propagating` / `stop_requiring` syntax for explicit overrides via protected-branch proposals. The single most important piece of Foundry's governance story — compliance teams can prove at audit time that PII never reaches a derived dataset accessible to an unprivileged group, because the lineage graph enforces it deterministically.

**Tier 2 — Strongly load-bearing (must ship by month 12):**

6. **Foundry Branching / Global Branching.** Git-like environments across data pipelines, the ontology itself, Workshop modules, and Actions. Apply Action accepts a `branch` parameter; FDEs can develop on real production data without breaking anything. Trunk-based development model.
7. **Data Connection.** Three architectures (direct, agent-proxy, agent-worker) to handle SaaS APIs vs on-prem systems. The egress story.
8. **Workshop builder runtime.** Declarative module spec (JSON config, not generated code) with sections, widgets typed against Ontology, variables, module interfaces, embedded modules, events. The agent-authorable surface for operational apps.
9. **MCP server(s) exposing ontology to external agents.** Ontology MCP for production data agents; Palantir MCP for platform-building agents. Both enforce the same OSv2 security model, both expose different surface areas to different actors.
10. **Compute Modules.** Serverless Docker containers as first-class platform primitive. Non-root, linux/amd64, zero-trust networking via explicit Sources. Two execution modes (function-backed and pipeline-backed).

**Tier 3 — Surface area / replaceable:**

11. Pipeline Builder (dbt / SQLMesh / Coalesce can substitute)
12. Slate, Quiver, Contour, Vertex (all replaceable or already displaced by AIP)
13. AIP Bootcamps (a sales motion, not a product)
14. Apollo (only matters for on-prem / air-gapped; ignore for SaaS-native rebuild)

### 1.2 The "all writes are Actions" invariant

This is the single most important architectural pattern in Foundry, and the one that directly enables safe AI agents. The Palantir docs are explicit: *"Calling an AIP Logic function from an action is required for edits to be written back to the Ontology. The Ontology will not be edited unless the Logic function is executed from an action, even if the function contains an Apply action block."*

Restated: no matter how an edit is proposed — by a human clicking a button in Workshop, by a Function executing logic, by an AIP Logic LLM choosing to mutate state, by an external agent over MCP — the actual mutation goes through a typed, validated, permission-checked, audited Action submission. The agent does not get a raw write. This is the invariant that makes "give your agent access to your data" safe at enterprise scale. Any product Tenex builds must replicate this invariant from day one.

### 1.3 The day-0-to-day-365 customer journey

Foundry's rollout is more disciplined than it looks. The pattern, synthesized from Palantir docs and customer accounts:

| Phase | Days | FDE hours | Customer ownership |
|-------|------|-----------|---------------------|
| 1. Data integration | 0–30 | ~30–50% | Visibility only |
| 2. Ontology authoring | 30–90 | ~30% (shifting to facilitation) | Joint authoring |
| 3. Operational applications | 90–180 | ~20% (architectural review) | Customer ships Workshop apps + Functions |
| 4. AIP and expansion | 180–365 | ~10% (advisory) | Full operator |

The economics work because **FDE hours per dollar of customer revenue decline asymptotically.** Year 1 is FDE-heavy and unprofitable; Years 2–5 are 80% gross margin expansion revenue with minimal FDE involvement. Top-20 customer ARR up ~50% YoY confirms the model empirically. This is the exact shape Tenex must replicate.

### 1.4 The Tenex-sized spine

If Tenex committed 6 engineers for 6 months to a Foundry-equivalent v1, the irreducible core fits in roughly 10.5 person-months of work:

```
┌─────────────────────────────────────────────────────────────────────┐
│  MCP Server (default surface in 2026)                               │
│  External agents talk MCP. Tools = action types + queries.          │
├─────────────────────────────────────────────────────────────────────┤
│  Typed OSDK (auto-generated TS + Python)                            │
│  Compile-time-safe access to ontology + actions + functions          │
├─────────────────────────────────────────────────────────────────────┤
│  Declarative app surface (Workshop-equivalent)                      │
│  JSON config; agent-authored by default                             │
├─────────────────────────────────────────────────────────────────────┤
│  Function runtime (TS + Python, serverless, OSDK-aware)             │
│  + Compute Modules (Docker on Knative)                              │
├─────────────────────────────────────────────────────────────────────┤
│  Action service (typed, validated, side-effect-aware, audited)      │
│  THE ONLY WRITE PATH                                                │
├─────────────────────────────────────────────────────────────────────┤
│  Object Store (indexed object DB with row+cell-level policies)      │
│  Built on DuckDB/ClickHouse + Iceberg + OPA/Cedar                   │
│  + lineage-aware marking propagation                                │
├─────────────────────────────────────────────────────────────────────┤
│  Data Connection (3 connector types in v1: SaaS, REST, warehouse)   │
│  Iceberg/Delta lake underneath, customer-owned where possible       │
└─────────────────────────────────────────────────────────────────────┘
```

Estimated effort breakdown (6 calendar months, 6–8 engineers):

| Component | Effort | Notes |
|-----------|--------|-------|
| Ontology schema service + Manager UI | 1 mo | CRUD over types/properties/links/actions |
| Object Store with row/cell policies | 2 mo | DuckDB + Iceberg + Cedar; the longest pole |
| Action service | 1 mo | Tightly coupled to Object Store |
| OSDK code generator (TS + Python) | 1 mo | OpenAPI emit + codegen |
| Workshop-equivalent (declarative UI) | 1.5 mo | Config schema + renderer; agent-authorable |
| Function runtime + Compute Modules | 1 mo | Knative wrapper, OSDK auto-injection |
| Data Connection (3 connector types) | 0.5 mo | Snowflake, S3/Iceberg, generic REST |
| MCP server | 0.5 mo | Wraps the OSDK; minor work |
| Branching (ontology + Workshop only) | 1 mo | Skip data branching for v1 |
| Lineage + marking propagation (SQL only) | 1 mo | OpenLineage + marking metadata |

Cost: ~$1M of engineering investment against $15M ARR. Fundable from services P&L if Tenex chooses. The constraint is not capital — it is engineering attention and the cultural discipline to keep the spine team's roadmap set by patterns observed across ≥3 FDE engagements, not by any single loudest customer.

### 1.5 What Tenex's FDEs must learn before they build

A platform play that doesn't internalize Foundry's abstractions drifts into consulting within 18 months. The recommended 5-week FDE curriculum:

- **Week 1.** The Ontology as data + logic + action + security. Build a toy 5-object-type ontology in a Foundry dev instance. Author at least one action type with a function rule.
- **Week 2.** Permissions deep dive. Markings, classifications, organizations, mandatory control properties, object security policies, property security policies, lineage propagation. Build a scenario where the same user sees one object's properties but not another's because of mandatory controls.
- **Week 3.** OSDK and Functions. Generate an OSDK. Build a Next.js app with both confidential and public auth. Write a TypeScript v2 Function that takes an object set, edits properties via an OntologyEditFunction, returns a transformed result.
- **Week 4.** AIP Logic, Actions-as-tools, MCP. Build an AIP Logic function that uses an LLM to triage incidents and applies an action conditionally. Configure Ontology MCP to expose actions as tools to Claude Code.
- **Week 5.** Workshop, Branching, FDE workflow. Build a Workshop module with embedded sub-modules. Use Global Branching to make breaking changes safely.

Mistakes to drill into every FDE before they touch a customer project:

- Don't model business logic inside Pipeline Builder transforms when it should be an Action. Pipelines are for shape; Actions are for behavior.
- Don't use markings as a substitute for object security policies — markings are mandatory and propagate everywhere.
- Don't bypass the OSDK from internal code by calling raw HTTP. The OSDK enforces the user's permissions; raw HTTP is easy to mis-permission.
- Don't author Actions with too-broad submission criteria.
- Don't store secrets in Compute Module Dockerfiles. Use Sources.
- Don't build long-lived branches.

---

## Part II — Ontology, Deeply Understood

If Tenex builds an ontology product, the team must know what an ontology actually is — not just what Palantir markets it as.

### 2.1 The definition that survives

Tom Gruber's 1993 paper "A Translation Approach to Portable Ontology Specifications" remains the canonical reference. The definition: **"An ontology is an explicit specification of a conceptualization."** An ontology is both an *artifact* (a schema with classes, relations, functions, axioms) and a *commitment* (every system implicitly believes that certain things exist; an ontology makes those beliefs inspectable).

The Quinean philosophical formulation makes this sharp: *to be is to be the value of a bound variable*. Whatever your system quantifies over is what your system commits to existing. When Palantir says "the Ontology is the digital twin of an organization," the precise reading is: the Ontology is the set of *what the organization is committed to believing exists*. Customers, orders, aircraft, sorties, claims — these are the bound variables of an operational theory of the world.

### 2.2 The expressiveness ladder

```
                  ┌────────────────────────────────────────────────────┐
                  │  Expressiveness ladder                              │
                  ├────────────────────────────────────────────────────┤
Knowledge Graph   │  Ontology + instance data + identifiers             │
                  ├────────────────────────────────────────────────────┤
Ontology          │  Classes + relations + axioms + logical rules       │
                  │  + actions/verbs + workflows + permissions          │
                  ├────────────────────────────────────────────────────┤
Data Model        │  Classes + properties + simple relationships        │
                  │  (no inference; queries must be predetermined)      │
                  ├────────────────────────────────────────────────────┤
Schema            │  Shapes/constraints on data (tables, columns)       │
                  ├────────────────────────────────────────────────────┤
Taxonomy          │  Hierarchical classification (subclass-of)          │
                  └────────────────────────────────────────────────────┘
```

Most "ontology products" actually sit at the data-model rung but borrow the word for marketing weight. Palantir's Foundry Ontology genuinely lives at the ontology rung because it includes action types (verbs with side-effects), interfaces (polymorphism), and a permission-aware execution layer — none of which fit in a data model.

This matters for Tenex: **shipping a "data model" and calling it an ontology is dishonest and competitors will eat you.** Shipping the action layer + execution + permissions is what separates an ontology product from a catalog product.

### 2.3 The formal stack — what shipped vs what didn't

The Semantic Web (RDF / OWL / SPARQL / SHACL) is technically rigorous but socially unscalable. OWL's open-world assumption ("things you didn't say might still be true") is exactly the wrong default for enterprise data validation. Most teams that adopted RDF used it for vocabulary mapping, not for reasoning. SHACL won for validation because it's procedural and predictable.

What *did* ship at scale:

- **schema.org** (31% of the public web as of 2025). Tens of millions of domains.
- **Wikidata** (1.5B+ statements). The world's largest open KG.
- **JSON-LD** (the dominant serialization). Powers Google's structured data.
- **Enterprise KGs** (curated, narrow, organization-specific). What Foundry is.

The lesson: pragmatic curation beats expressive formalism. Tenex Ontology should ship a typed, opinionated schema with a few constrained semantics (subclass-of, has-property, links-to, performs-action), not a Description Logic engine nobody will author.

### 2.4 The semantic-layer landscape — the practical commercial cousins

```
                 ┌────────────────── Semantic Layer Stack ────────────────┐
                 │                                                        │
Application      │   AI agents, BI dashboards, embedded analytics         │
─────────────────┼────────────────────────────────────────────────────────┤
Serving          │   Cube.dev, dbt Cloud Semantic Layer API               │
─────────────────┼────────────────────────────────────────────────────────┤
Definitions      │   dbt MetricFlow (YAML), Cube schema (YAML/JS),        │
                 │   LookML, Power BI semantic models (TMDL), AtScale     │
─────────────────┼────────────────────────────────────────────────────────┤
Catalog/governance│  Atlan, Alation, Collibra, OpenMetadata, Purview      │
─────────────────┼────────────────────────────────────────────────────────┤
Transformation   │   dbt Core / dbt Cloud, SQLMesh                        │
─────────────────┼────────────────────────────────────────────────────────┤
Warehouse        │   Snowflake, Databricks, BigQuery, Redshift, Fabric    │
                 └────────────────────────────────────────────────────────┘
```

These products are mostly *measures and dimensions over a warehouse*. None of them model action types or workflows. They are necessary but insufficient ingredients of an ontology platform. The gap between dbt Semantic Layer and Foundry Ontology is the gap between "I can compute revenue consistently" and "I can run my operations on this." That gap is precisely where Tenex Ontology lives.

### 2.5 The most strategically relevant competitor — Alation + Numbers Station

**Alation acquired Numbers Station in May 2025** for ~$17M+. Numbers Station built LLM agents over structured enterprise data. Alation contributed a 7+ year head start on metadata coverage and F500 catalog deployments. In October 2025 they launched Agent Builder at revAlation, with MCP support. The CEO's public framing — that LLM hallucination is the wall between enterprises and AI adoption, and the fix is "a translation layer that sits between the LLMs and an enterprise's data" — is *identical* to the Foundry Ontology thesis.

This is the single most directly competitive product to a Tenex ontology play. They have a 12–18 month head start on AI-native posture and a 7+ year head start on metadata coverage. Tenex's offsetting advantages: speed-to-deploy (60–90 days vs Alation's 6–9 month catalog rollout), action layer depth (Alation doesn't ship typed action verbs with side effects), and FDE-led implementation that delivers an end-to-end working ontology + agents + workflows rather than a configured catalog.

Atlan and Collibra are following the same pattern with slightly different positioning. By Q4 2026, every major catalog vendor will have an AI-agent-grounded MCP server. Tenex must ship before this becomes table stakes.

### 2.6 The auto-construction tradeoff

The single most important architectural decision Tenex faces is what to auto-infer versus what to require human authoring for. The line is sharp and not negotiable:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│   AUTO-INFERABLE                       │   FUNDAMENTALLY HUMAN-AUTHORED      │
├────────────────────────────────────────┼─────────────────────────────────────┤
│ • Object types from table schemas      │ • What an object is *for*           │
│   (rows → instances, columns → props)  │   (purpose, role in process)        │
│                                        │                                     │
│ • Property data types                  │ • Business-process action types     │
│   (numeric, categorical, datetime)     │   (approve, escalate, settle)       │
│                                        │                                     │
│ • Link types from FKs                  │ • Side-effects of actions           │
│   (explicit + implicit via overlap)    │   (which other systems change)      │
│                                        │                                     │
│ • Basic taxonomies from enumerations   │ • Organization-specific markings    │
│                                        │   (PII, classified, embargoed)      │
│ • Simple CRUD actions                  │                                     │
│   (create, update, delete)             │ • Permissions / RBAC mapping        │
│                                        │   to business roles                 │
│ • Description text from data samples   │                                     │
│                                        │ • Inter-object workflows            │
│ • Naive entity resolution              │   (when does X trigger Y?)          │
│   (exact / edit-distance match)        │                                     │
│                                        │ • Metric definitions that carry     │
│ • Cardinality estimates                │   organizational meaning            │
│                                        │   ("active customer", "MRR")        │
│ • Predicted relationships              │                                     │
│   (link prediction from data patterns) │ • Cross-system identity resolution  │
└────────────────────────────────────────┴─────────────────────────────────────┘
```

The left column is *structural*; the right column is *intentional*. Auto-inference can recover everything *expressed* in the data; it cannot recover anything *not* in the data — and the most valuable parts of an ontology (the things you can run a business on) are precisely the things that *aren't* in the data because they live in people's heads, in process docs, in regulatory requirements, and in the *purpose* of the system.

The architectural synthesis that wins: **deterministic typed core + LLM-fluid periphery.**

```
                  ┌──────────────────────────────────────────────────┐
                  │   LLM-fluid periphery                            │
                  │   • Description text, synonyms, aliases          │
                  │   • Natural-language → typed tool call           │
                  │   • Auto-generated action suggestions            │
                  │   • Inferred links to be reviewed                │
                  │   • Hypotheses, predictions, recommendations     │
                  │   ┌─────────────────────────────────────────┐    │
                  │   │   Deterministic typed core              │    │
                  │   │   • Object types (Aircraft, Customer)   │    │
                  │   │   • Properties with strict types        │    │
                  │   │   • Link types (FK-grounded)            │    │
                  │   │   • Action types (verbs + side-effects) │    │
                  │   │   • Permissions, markings, lineage      │    │
                  │   │   • Writeback datasets, version control │    │
                  │   └─────────────────────────────────────────┘    │
                  └──────────────────────────────────────────────────┘
```

The deterministic core is what you can audit, govern, version, certify. The LLM periphery is what makes it fast to build and easy to consume. Foundry's Ontology + AIP follows this pattern. Tenex Ontology must follow it from day one.

### 2.7 Agents over typed ontology beats agents over raw SQL

This is the technical bet underneath everything. Text-to-SQL agents hallucinate column names, mis-join tables, invent semantics. Typed-tool agents pick from a constrained vocabulary defined by the ontology schema and validated against the type system. Every action goes through a defined action type with permissions, side-effects, and writeback. The audit trail is a record of typed operations, not opaque queries.

The MCP-exposed schema Foundry settled on is the right shape:

```
Discovery:  object_type_search, object_type_lookup, dataset_lookup
Retrieval:  object_set, object_lookup, search_around, semantic_search
Compute:    ontology_aggregation, function_execution
Mutation:   action_type_execution (with required approval)
```

Notice: mutation is *one* call, parameterized by a named action type that itself encodes the side-effects, the permission requirements, and the approval flow. This is the abstraction Tenex Ontology must ship.

### 2.8 The Kumo wildcard

**KumoRFM** (Kumo.ai, 2025) is a relational foundation model pre-trained on tens of thousands of relational schemas. Represents the database as a temporal heterogeneous graph (rows → nodes, FKs → edges, timestamps preserved). Schema-agnostic row encoder + Relational Graph Transformer + in-context learning. Answers predictive queries zero-shot, no feature engineering. Snowflake-native, Databricks lakehouse app, BigQuery, Athena. Data never leaves the warehouse.

The implication: *predictive ML* over an ontology is becoming a query, not a project. If Kumo wins, ontologies become predictive substrates by default — and a Tenex Ontology that doesn't expose Kumo-style predictive queries as a first-class capability will look dated by 2027.

**Recommendation:** Year 2 of Tenex Ontology should include a "predictive verbs" capability where any object type can be the subject of a predictive query (`predict_churn`, `predict_outcome`, `forecast_value`) that compiles into a Kumo-style relational foundation model call or a custom model trained on the customer's ontology graph. Treat predictive functions as a class of action types.

### 2.9 The Tenex ontology product — what it actually is

```
┌──────────────────────────────────────────────────────────────────────────────┐
│   Tenex Ontology Platform — MVP shape                                         │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   1. CONNECT — to warehouse (Snowflake/Databricks/BQ/Postgres) + SaaS         │
│      (Salesforce/HubSpot/Stripe/Zendesk/etc.) via a connector library.       │
│                                                                              │
│   2. AUTO-INFER deterministic core — object types from tables, properties    │
│      from columns, link types from explicit + implicit FKs, basic CRUD       │
│      actions. Confidence-scored; ambiguous cases flagged for review.         │
│                                                                              │
│   3. LLM-FLUID periphery — description text, synonyms, semantic search       │
│      surface, natural-language queries, suggested action types from CRUD     │
│      patterns. Always with a "convert to deterministic" promotion path.      │
│                                                                              │
│   4. HUMAN-AUTHORING tools for the intentional half — typed action types,    │
│      permissions, markings, workflows. Foundry-style Ontology Manager.       │
│                                                                              │
│   5. AGENT SURFACE — MCP server exposing typed object types and action       │
│      types; SDK generation for TypeScript/Python; tool-use schemas that      │
│      drop into OpenAI/Anthropic/Google agent SDKs.                           │
│                                                                              │
│   6. WORKFLOW EXECUTION — actions triggered, audited, reversible. The        │
│      moat: ontology + actions + agents in one place.                         │
│                                                                              │
│   7. FEEDBACK LOOP — every analyst correction, every approved agent          │
│      action, every metric refinement feeds back to improve auto-inference.   │
│      The ontology *compounds*.                                               │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## Part III — Salesforce as the Other Reference Architecture

Palantir Foundry and Salesforce are the only two "enterprise operating systems" that have crossed escape velocity in the last 25 years. Foundry won the **data/ontology** side. Salesforce won the **record-of-action** side — the customer, the deal, the case, the order. They are best understood as inversions of each other, and any modern enterprise OS play has to absorb both.

### 3.1 The six-layer minimum that both prove necessary

| Layer | Salesforce | Foundry | Required because |
|-------|------------|---------|-------------------|
| **Typed schema / object model** | sObjects (`__c`, `__mdt`, `__x`) | Ontology (Object Types, Link Types) | Without it, no tool can be safe |
| **Metadata-as-code** | Metadata API + SFDX | Ontology resources in version control | Without it, no diff / test / rollback |
| **Declarative customization** | Flow, Permission Sets, Layouts | Workshop, Slate, Quiver | Without it, admins can't ship |
| **Programmatic escape hatch** | Apex, LWC, Triggers | Functions, Transforms (Python / Java) | Without it, the 20% blocks the 80% |
| **Permission + sharing model** | Profiles+PSet / Sharing | Mandatory ACLs on ontology | Without it, AI cannot be trusted |
| **Packaging + distribution** | Managed Packages + AppExchange | Marketplace (newer, weaker) | Without it, no ecosystem moat |

Both prove this six-layer minimum is necessary. Neither proves it is sufficient (both struggle with developer joy, both have legacy weight). Skip any one layer and Tenex Ontology is a tool, not a platform.

### 3.2 The single most important architectural pattern to steal — metadata-driven multitenancy

From Salesforce's 2008 Force.com whitepaper: *"A single instance of the Salesforce Platform uses (1) a single shared multitenant database with a single schema that stores tenant-specific metadata and data, and (2) a multitenant kernel that reads metadata and data to dynamically provide tenant-specific applications, business logic, and APIs."*

The mechanism:

```
┌────────────────────────────────────────────────────────────┐
│                  Salesforce Multitenant Kernel             │
│  (compiled runtime; same binary for every customer)        │
└──────────────────────────┬─────────────────────────────────┘
                           │ reads at runtime
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
┌───────────────┐   ┌──────────────┐  ┌──────────────┐
│   Metadata    │   │     Data     │  │    Pivot     │
│    Tables     │   │    Tables    │  │    Tables    │
│ (UDD: object  │   │ (rows for    │  │ (indexes,    │
│  defs, field  │   │  every tenant│  │  relationships│
│  defs, layouts│   │  in shared   │  │  unique keys)│
│  perms, code) │   │  schema, by  │  │              │
│               │   │  OrgID)      │  │              │
└───────────────┘   └──────────────┘  └──────────────┘
```

Defining a custom object does *not* create a database table. The kernel reads a Universal Data Dictionary at runtime and materializes a "virtual" table over shared pivot tables partitioned by `OrgID`. Every customer's customizations live as rows in the same physical schema as every other customer's customizations.

**This is the only way to ship a multi-tenant customizable platform without going insane.** Every customer-defined object, field, permission, view, and automation is a row in a versioned metadata store, not a schema migration. Tenex Ontology must do this from day one. Retrofitting it later is impossible.

### 3.3 Patterns to steal in OpenFoundry's MVP (year 1)

1. **Metadata-driven object model** (above). Every customization is a row, not a migration.
2. **Strongly-typed named primitives.** Don't ship "string" and "number" — ship `Email`, `Currency`, `Phone`, `URL`, `Address (compound)`, `Geolocation`, `LookupTo(Object)`, `Picklist(values)`. Each named type comes with validation, display, and search behavior. Composite primitives like Address pay for themselves in UX.
3. **Permissions ⊥ Sharing as orthogonal dimensions.** Object/field permissions decide "can this user ever see this column." Record-level access (sharing) decides "which rows." Both must allow. Make them orthogonal in your data model from day one — retrofitting this later is the #1 architectural regret of every B2B platform.
4. **Additive permission sets stacked on a minimal baseline.** User has a baseline + N stacking permission grants. One-role-per-user is an anti-pattern that forces profile explosion.
5. **Describe / introspection API before CRUD API.** Salesforce's `Describe` lets any tool introspect the full schema of an object at runtime. This is what makes LWC dynamic, Apex generic, Agentforce grounded. Build the introspection API first.
6. **Declarative-first UX surface.** Every feature exposed to admins gets a no-code surface. The TypeScript/Python escape hatch is always available but never the default.
7. **Source-driven definition lifecycle.** Every object, permission set, flow, and script is exportable as code, diffable in Git, deployable via CI/CD, packageable as a versioned unit. SFDX is the gold-standard reference.
8. **Foundry-style lineage-propagated ACLs over derived datasets.** Where Salesforce gets it wrong — Roll-up Summary fields can leak data if you misconfigure FLS — Foundry gets it right. Adopt Foundry's lineage propagation as the default ACL behavior.
9. **Audit log of every action at field-level granularity.**
10. **A single workflow runtime.** Don't ship two. Salesforce burned a decade with three (Workflow Rules + Process Builder + Flow). Pick one and evolve it.

### 3.4 Patterns to steal in year 2–3

11. **Sandboxed scripting escape hatch.** WASM/V8/Firecracker over TypeScript / Python, *not* a custom language. Avoid the Apex lock-in trap — Apex's lock-in is generational and the engineer market for Apex is shrinking.
12. **Tenant-level (not transaction-level) resource quotas with backpressure.** Apex governor limits are *the* most-complained-about feature. Set quotas at the org level, surface as soft quotas with backpressure, not uncatchable exceptions.
13. **Versioned, namespaced packages of metadata + code.**
14. **Agent layer that grounds on the object model, sharing rules, and metadata labels.** Make every workflow callable as an agent action.
15. **Trust Layer pattern.** Masking pre-LLM, audit + policy enforcement, zero-retention contracts with model providers.

### 3.5 Patterns to steal in year 3+

16. **Marketplace with security review** — the commercial ecosystem. AppExchange takes 15–25% PNR of partner revenue and the ecosystem is worth $10B+ GMV. Tenex won't need this until customer #100, but the *architectural decisions to enable it* — namespacing, describe API, source format, ACL model — are year-1 decisions that cannot be retrofit.

### 3.6 Patterns to explicitly avoid

| Pattern | Why Salesforce regretted it | Tenex alternative |
|---------|------------------------------|-------------------|
| Custom programming language (Apex) | Generational lock-in; shrinking engineer market | Use TS / Python in a WASM/V8 sandbox |
| Custom frontend framework (Aura) | Multi-billion-dollar mistake; still migrating | Web Components / React / Lit |
| Multiple overlapping automation tools | Decade spent unwinding | Pick one workflow runtime |
| 9-mechanism sharing model | Famously painful complexity | Start with 3 mechanisms (Owner, Group membership, Criteria-based) |
| Per-transaction uncatchable governor exceptions | Most-complained-about feature | Tenant-level soft quotas with backpressure |
| Pre-committing to a single hosting model | Hyperforce migration is 5+ years in | BYO cloud from day one architecturally |
| Pricing models admins can't predict | Agentforce conversation-credit confusion is hurting adoption | Transparent per-object-type / per-connector pricing |

### 3.7 The Agentforce lesson — typed object model is the AI moat

The Salesforce AI architecture as of mid-2026 — Agentforce + Atlas Reasoning Engine + Einstein Trust Layer + Data Cloud — is instructive in three specific ways:

1. **Every Flow and every Apex method is automatically a callable tool for Agentforce.** Salesforce's investment in declarative automation became its agent-action library overnight. The cost of building 10,000 invocable actions was paid in 2014–2024. Agentforce gets it for free. **Tenex Ontology should ship every Action type and every Function as automatically MCP-exposed by default.**
2. **The Trust Layer's grounding and masking ride on the existing permission/sharing model.** An agent acting "as user U" cannot retrieve records U cannot see. This is why Salesforce can ship enterprise agents and OpenAI/Anthropic-on-raw-data cannot. **Agentic action requires a typed access model below it.**
3. **Atlas's ReAct loop is unremarkable; the data grounding is the moat.** Every vendor has a planner. Only Salesforce has the planner *plus* 25 years of opinionated customer-data schemas *plus* a permission system the planner is forced to obey. Per Salesforce's engineering blog, early Atlas pilots showed *"2× increase in response relevance and 33% increase in end-to-end accuracy"* vs DIY agents. The delta is not reasoning — it is grounding.

**The implication for Tenex:** the ontology is the AI moat. Not the reasoning loop, not the agent framework. The typed, governed, lineage-aware ontology that the agent is forced to operate through. That is the bet.

### 3.8 The Salesforce-vs-Foundry synthesis

Foundry wins on lineage-aware mandatory access controls. Salesforce wins on metadata-as-code packaging + ISV ecosystem economics. **Tenex should adopt Foundry's lineage propagation AS the default ACL behavior AND Salesforce's packaging discipline as the year-3 monetization layer.** Every FDE engagement should deposit metadata into Tenex Ontology's reusable library, not just code into a customer repo. The platform leverage is in compounding metadata, not compounding services hours.

---

## Part IV — Services-to-Product Economics for Tenex

The empirical record from Palantir, Sierra, Decagon, Cognition, Cresta, GitLab, HashiCorp, Distyl, Tribe, and the big consultancies shows three reliable patterns.

### 4.1 The three case-study patterns

**Pattern A: Palantir (gold standard, 13 years).** S&M intensity from 62.6% of revenue (FY20) to ~24% (FY25). Gross margin 67.7% → 82.4%. Rule of 40 from <0 to 80+. Top-20 ACV $93.9M TTM. The discipline that made it work: (1) FDEs reported into product/engineering, not a services P&L; (2) bespoke code was aggressively harvested into Foundry primitives; (3) AIP Bootcamps as the productization wedge from 2023 onward.

**Pattern B: Sierra / Decagon (compressed to 2–3 years).** Sierra: $0 → $150M ARR in 9 quarters, 559 employees, $985M raised, outcome-based pricing, ~$15B valuation. Decagon: $10M → $35M ARR over 2025, $4.5B at Series D, per-resolution pricing. Both look services-heavy on the surface but ran product economics underneath — the FDE work is *funded by the product margin*, not a separate services line. Decagon's Series D press release contains the smoking gun quote: *"There's no time for lengthy configuration cycles or even armies of forward-deployed engineering."*

**Pattern C: Cresta / Tribe / Distyl (the cautionary tales).** Cresta: $282M raised, 615 employees, $15–31M revenue, stalled $1.6B valuation, Series D didn't disclose valuation. Stuck in the "AI augments humans" framing while the market moved to "AI replaces humans." Distyl: $1M revenue at a $1.8B valuation with 120 people — pure services, valuation predicated on future productization that hasn't shipped. Tribe AI: explicitly announced in October 2025 it is *"doubling down on Forward Deployed motion"* — a public commitment to the consultancy gravity well.

### 4.2 The KPIs that predict outcome

| KPI | Healthy productization | Failed productization |
|-----|-------------------------|------------------------|
| **Gross margin trajectory** | Rising 2–3 pts/year, crossing 70% by $50M ARR | Flat at 35–55% even at $100M+ ARR |
| **S&M as % of revenue** | Falling 5–10 pts/year after $30M ARR | Stuck above 50% or rising with growth |
| **% engineering on "spine"** | Rising from ~5% at $10M ARR to ~25% at $50M, 40%+ at $100M | Stays at <10% indefinitely |
| **Services revenue as % of total** | <20% by $50M ARR, <10% by $100M ARR | Stays at 50%+ or rises |
| **NDR / customer expansion** | 130%+ for top-quartile AI-native | <110% (signals delivery, not product, drives expansion) |
| **Top-3 customer concentration** | Falling — 50% at $10M to <25% at $50M | Static or rising |
| **Rule of 40** | Crosses 40 by $50M ARR, 60+ by $100M | Below 40 indefinitely |
| **ARR per FTE** | $300–400K hybrid; $1M+ AI-native | $150–200K (consultancy benchmark) |
| **Pricing model** | Subscription / usage / outcome-based | Hourly / storypoint / day-rate |

**Tenex's current position:** ARR/FTE at ~$300K (right at the lower edge of healthy). The next 12 months determine which trajectory the company lands on.

### 4.3 The capital allocation math for Tenex

| Inputs | Value |
|--------|-------|
| ARR | $15M |
| Revenue per storypoint | $300 |
| Cost per storypoint (engineer) | $80 |
| Storypoint contribution margin | 73% before overhead |
| Realized GM (after strategists, ops, COGS) | ~45% (services-business midpoint) |
| Realized GM in dollars | ~$6.75M |
| Engineer FTEs (estimated) | 30–50 (~40 midpoint) |
| Storypoints sold annually | ~50,000 |
| Storypoints per FTE per year | ~1,250 |

The three scenarios:

| Scenario | Spine FTE | Billable FTE | Spine $ Y1 | Billable revenue impact | Product revenue Y2 | Product revenue Y3 |
|----------|-----------|--------------|-------------|--------------------------|---------------------|---------------------|
| **A. Aggressive** | 12 (30% of eng) | 28 | $5–8M | -$5.4M | $1–3M | $5–15M if PMF |
| **B. Conservative** | 4 (10%) | 36 | $1–3M | -$1.8M | $0–1M | $1–4M |
| **C. Barbell (recommended)** | 6 (15%) | 34 | $3–4M | -$2.7M | $1–2M | $4–10M (gated) |

The break-even curve:

```
                Year 1     Year 2     Year 3     Year 4
Aggressive (A):
  Billable lost  -$5.4M    -$8M       -$11M      -$15M  (compounding)
  Product gain   ~$1M      $3M        $12M       $40M+  (if PMF)
  Net cumulative -$4.4M    -$9.4M     -$8.4M     +$17M  (break-even Q4 Y3)
  Net cumulative -$4.4M    -$9.4M     -$20M      -$33M  (if no PMF — disaster)

Conservative (B):
  Billable lost  -$1.8M    -$2.5M     -$3.5M     -$5M
  Product gain   $0        $0.5M      $2M        $5M
  Net cumulative -$1.8M    -$3.8M     -$5.3M     -$5.3M (never escapes)

Barbell (C):
  Billable lost  -$2.7M    -$4M       -$5.5M     -$7M
  Product gain   $0.5M     $2M        $7M        $20M
  Net cumulative -$2.2M    -$4.2M     -$2.7M     +$10M  (break-even mid Y3)
```

Conservative never reaches escape velocity. Aggressive blows up if PMF doesn't hit by Y2. Barbell preserves option value with a gated decision point — this is the recommended posture.

### 4.4 The strategist intensity question

The $300/$80 unit economics imply 73% contribution margin per storypoint *if engineers were the only cost*. They are not. Strategists, ops, PMs, recruiters, sales compress realized GM into the 40–55% range typical of engineering services. Two structural levers:

1. **Push more revenue through engineer-only work** — less strategist time per dollar. This requires a productized intake / discovery layer, which is itself spine work.
2. **Cap strategist intensity per account** — e.g., max 1 strategist per $1M of ARR on any single account.

This is the underappreciated link between spine investment and immediate GM improvement: every dollar invested in productizing intake, scoping, and project tooling *directly lifts the GM* on billable work, even before the standalone product ships.

### 4.5 The seven failure modes ranked by frequency

1. **The 18-month dead zone.** Spine team carved out but underfunded, billable team resentful at lost capacity, neither business wins. *Mitigation: clear P&L separation, executive air cover, milestone-based re-evaluation.*
2. **Building the wrong spine.** Spine team builds what the loudest current customer asked for; becomes a sophisticated project asset library, not a product. *Mitigation: spine roadmap set by patterns observed across ≥3 FDE engagements, not by any single account.*
3. **The "we have a product but our salespeople sell hours" cultural trap.** Sales comp plans reward storypoint deals; salespeople push hours. *Mitigation: separate quota carriers for product, with their own comp plan, from day 1.*
4. **Margin trap.** Services revenue drags product multiples in fundraising. *Mitigation: report product ARR separately, even internally, from day 1, GitLab-style.*
5. **Premature productization.** Spine built before customer patterns are clear (under $10M ARR). Tenex is *just* past this risk threshold.
6. **Becoming a permanent consultancy (Tribe / Distyl / Cresta).** The pattern is identifiable in real time. *Mitigation: every quarter, ask publicly "what % of new logos this quarter bought the product vs. the engagement?"*
7. **Acqui-hire as exit.** Cresta-shaped trajectory ends in a strategic acquisition at modest multiples.

### 4.6 The structural choices

| Decision | Tenex recommendation |
|----------|----------------------|
| **Spine team P&L** | Separate. GitLab-style ARR reporting that excludes professional services revenue. |
| **Reports to** | CEO. A CTO-reported product team is too easily reabsorbed into the engineering pool when billable demand spikes. |
| **Compensation** | Equity-heavy with ARR-tied bonus. Spine engineers need different incentives than billable engineers. |
| **Hiring source** | Both, with bias to convert FDEs. Palantir-pattern says FDEs who already know customer patterns are the right product engineers — but hire 1–2 product PMs from product-native companies (Stripe, Linear, Notion) to set product culture. |
| **Pricing transition** | Outcome-based / per-object-type subscription for v1, usage-based add-on for v2. |
| **Outside capital** | Raise after $30M ARR gate. Raising before product wedge is proven dilutes on services valuation multiples (3–5x revenue) instead of product multiples (15–40x). |

### 4.7 The pricing transition tactic

The hardest cultural transition in this whole process. Current pricing is causally tied to engineer time ($80 cost, $300 charge). Product pricing must be causally tied to *customer value delivered*. The two cannot share a sales conversation cleanly.

**Recommendation: bundle a small product license into every services engagement.** $50K annual platform license layered on top of the storypoint billing — Palantir-style "bootcamp + limited license" entry. This:

- Trains the sales motion to sell software alongside hours.
- Generates trackable product ARR (small at first) that can be reported separately.
- Creates a forcing function for the spine team to make the platform compelling enough to justify the license.

### 4.8 The single most important rule

**Every quarter, ask: what % of new-logo *first-dollar* revenue came from the product versus the engagement?**

The answer at Year 1 will be ~5–10%. At Year 2, it should be 20–30%. At Year 3, 40–50%. If it's not climbing, the productization isn't happening — the company is just adding products to services revenue rather than transitioning.

---

## Part V — The Beachhead: Tenex Ontology

### 5.1 The recommendation in one paragraph

Tenex should build **Tenex Ontology** — an FDE-installed, auto-built semantic data layer for the F500 that exposes a customer's enterprise data and operational verbs as governed MCP tools to whatever agents the customer has chosen. It attaches to ~80% of Tenex's existing F500 engagements without changing the buyer or the sales motion, captures the data-modeling output that today walks out the door at the end of every engagement, and compounds into the deepest moat in enterprise software (customer-specific ontology) at Glean-tier pricing rather than Palantir-tier. The MCP-gateway / RBAC capability is correct as a **bundled governance feature** of Tenex Ontology — it's the choke point that makes the ontology load-bearing — but is the wrong shape for Tenex to sell as a standalone CISO-targeted security category. The agent platform is the most crowded space in software and Tenex has no defensible advantage there. Ship Tenex Ontology MVP in 6 months with 9–11 FTE, target $1.2–2.5M Year 1 ARR from 3 F500 paying customers seeded from current Tenex accounts, and grow into the OpenFoundry vision over 18–36 months by adding the operational app layer and Foundry-style lineage-aware permissions on top.

### 5.2 The full ten-dimension comparison

| Dimension | Weight | Agent RBAC | Data/Ontology | Agent Platform |
|-----------|--------|------------|---------------|----------------|
| Capital intensity to MVP | 10% | 3 | 3 | 1 |
| Time to first revenue from F500 | 10% | 4 | 5 | 2 |
| Attach rate to existing engagements | 15% | 3 (~40%) | 5 (~80%+) | 2 (~20%) |
| Competitive density | 10% | 1 | 3 | 1 |
| Defensibility / moat | 15% | 2 | 5 | 2 |
| Distraction risk | 10% | 3 | 4 | 1 |
| Sales motion compatibility | 10% | 3 | 5 | 2 |
| Pricing unit economics | 5% | 3 | 4 | 3 |
| Expansion path to OpenFoundry | 10% | 3 | 5 | 2 |
| Commoditization half-life | 5% | 1 | 4 | 1 |
| **Weighted total** | 100% | **2.65** | **4.30** | **1.70** |

The data/ontology platform is the only candidate that scores above 3.0 on a weighted average. Agent RBAC is a credible #2 but loses on competitive density (Aembit, Astrix, Oasis, Descope, WorkOS, Arcade, Composio, Pomerium, Cloudflare, Entra Agent ID, Okta AI Agents, AWS AgentCore — 20+ funded) and commoditization half-life (12–24 months). The agent platform is a trap (Sierra, Decagon, Cognition, plus every framework, plus every hyperscaler, plus OpenAI DeployCo).

### 5.3 The MVP feature set

Working name: **Tenex Ontology**. External positioning: **"agent-ready data layer for the F500."**

15 must-ship features (the MVP):

1. **Connector framework with 6 launch connectors:** Snowflake, Databricks, Salesforce, ServiceNow, Workday, S3. Read-only ingestion + schema introspection.
2. **LLM-assisted ontology builder.** From schema + sampled rows + query history (warehouse query logs are gold), propose object types, properties, link types, candidate action verbs. FDE-facing review UI.
3. **Object/property/link storage** in Postgres + JSONB with typed property base types (string, int, geo, marking, fk). Not a graph DB at MVP scale.
4. **Typed action verbs** with transactional execution against source systems via customer credentials. One write path per action; idempotency keys; full audit log.
5. **MCP server that exposes the ontology** as tools. Tool catalog auto-derived from object types and action types. Per-tool RBAC, per-tool description, per-tool typed parameter validation.
6. **Per-user OAuth + audience-bound tokens (RFC 8707)** for the MCP layer. Token exchange against customer's existing IdP (Okta, Entra, Ping). No DCR; CIMD only.
7. **Action policy engine.** Dual-principal (user + agent) authorization. Cerbos-style YAML or OPA Rego. Out-of-the-box policies for "writes require human-in-the-loop" and "PII reads require purpose-binding."
8. **Audit log** with `who / what-agent / which-tool / which-object / policy-version / outcome`. Exportable to customer's SIEM.
9. **Marking-style classifications** on properties (basic: `pii`, `phi`, `financial`, `restricted`). Inherited by derived object types. Enforced at tool-call time.
10. **Agent-interaction feedback loop.** Every tool call generates a signal; weekly batch job proposes ontology refinements. FDE reviews; customer approves.
11. **Embeddings layer** over object properties for semantic search.
12. **Object views.** Thin auto-generated UI showing the ontology to non-technical users for verification. Read-only at MVP.
13. **FDE deployment kit.** Docker Compose for pilot, Terraform module for prod. Single-tenant per customer; runs in customer VPC or Tenex-managed cloud.
14. **Customer dashboards** for the CIO/CDO: which agents call which tools, action volume, denied actions, ontology coverage of source systems.
15. **No agent runtime, no app builder, no workflow engine.** Explicitly cede those layers. Tenex Ontology is the substrate; not the consumer.

Stretch (months 4–6 if MVP lands):

16. SCIM `/Agents` provisioning.
17. **Lineage-aware propagation of markings** across derived object types — the load-bearing Foundry primitive. Ship as soon as the bandwidth allows.
18. Cross-source joins / derived object types.
19. Per-tool sandboxed execution for write actions in dry-run mode.
20. ISO 42001 audit pack and SOC 2 Type 2 attestation.

### 5.4 The first ten F500 customer profiles

These are *shapes of customer* — Tenex's actual current F500 accounts that fit these shapes should be targeted by name in the first round.

1. **Top-5 US bank** with fragmented data estate across Snowflake + on-prem Teradata + Salesforce. Pain: regulatory desire to deploy AI agents on internal data, but no unified data model and no governance plane satisfying OCC/Fed scrutiny. Buyer: CDO + CISO. Entry ACV: $750K–1.5M.
2. **F100 health insurer** wrestling with HIPAA-bound agent deployments. Cannot use Glean (no purpose-binding) and Palantir is priced beyond tolerance. Buyer: CIO + Chief Privacy Officer. Entry ACV: $500K–1M.
3. **F50 manufacturer** with $40B revenue, SAP S/4HANA + ServiceNow + 200 line-of-business apps. Pain: 50+ pilot agents but no consistent view of the supply chain. Buyer: CIO + COO. Entry ACV: $1–2M.
4. **F200 retailer** with Salesforce + Snowflake + a hand-built ML platform. Pain: each business unit's agents reinvent customer/order/inventory models inconsistently. Buyer: Chief Digital Officer. Entry ACV: $400–800K.
5. **F100 oil & gas operator** with operational data in OSIsoft PI + Snowflake + ServiceNow. Operational AI must respect safety policies and union-contract restrictions. Buyer: VP Operational AI + VP IT. Entry ACV: $1M+.
6. **F200 asset manager** with Bloomberg + Snowflake + Salesforce. Wants Claude/ChatGPT to write portfolio commentary referencing actual holdings securely. Buyer: CTO + Chief Compliance Officer. Entry ACV: $500K.
7. **F50 telecom** with massive billing + CRM + network ops data. Sierra-style CX agents deployed but stuck on data integration. Buyer: CIO + VP CX. Entry ACV: $750K.
8. **F100 logistics company.** Operational decisioning needs both real-time and warehouse data. Palantir is already selling to them; Tenex undercut at half the price. Buyer: CTO + COO. Entry ACV: $1M.
9. **F500 staffing/HR services firm.** Workday + ServiceNow + custom CRM. HR agents must respect manager hierarchies and compensation confidentiality. Buyer: Chief People Officer + CIO. Entry ACV: $400K.
10. **F100 utility regulated by FERC/NERC.** Operational agents on grid data must satisfy NERC CIP. Buyer: CIO + Chief Compliance Officer. Entry ACV: $1M+.

**Prioritize the first three:** bank, insurer, manufacturer. These are the verticals where Palantir has the strongest reference architecture, which means buyers already understand the value proposition and the budget pre-exists. Beat Palantir on price + speed-to-value, not features.

### 5.5 Pricing structure

```
Annual subscription:
  Base platform fee:    $120K/year (10 connectors, 30 object types, 1M tool calls)
  Per object type >30:  $3,000/month
  Per connector >10:    $1,500/month
  Per 1M tool calls >1M: $1,500
  
Services (Tenex storypoints @ $300/sp):
  Implementation:       80–200 sp typical
  Ontology refinement:  20–80 sp/month ongoing
  
Typical Year 1 ACV:     $300K–1.5M
Typical Year 2 ACV:     $500K–3M (NDR target >130%)
```

The base $120K platform fee is **CAIO-approvable** — under most enterprise discretionary AI budgets. Expansion is led by FDEs after the first quarter of usage. The base platform fee + storypoint services hybrid is what makes this look like a Palantir deal to the customer without requiring Palantir-tier pricing.

### 5.6 The team

**Engineering (4–6 FTE for months 1–3, ramping to 8–10 by month 6):**

- Tech lead / staff eng (1) — owns ontology data model and write-back transactionality.
- Connector engineers (2) — own the connector framework + first 6 connectors.
- MCP / auth / governance engineer (1) — owns MCP server, OAuth, policy engine.
- LLM / ontology-build engineer (1) — owns auto-ontology builder + feedback loop.
- Frontend / FDE-UX engineer (1) — owns FDE review UI + customer dashboards.
- SRE / multi-tenancy (1, ramp month 2) — deployment, observability, security posture.

**Product & GTM (3 FTE):**

- Product manager (1) — pulled from existing Tenex product leadership.
- Founding AE (1) — hire externally; target someone from Palantir, Glean, or Snowflake commercial.
- Product marketing / category-defining writer (1) — part-time at first; owns "agent-ready data layer" positioning + F500 case studies.

**Design (0.5 FTE):** senior designer shared with current Tenex; ontology review UX is the highest-leverage surface.

**Forward deployed (existing FDE pool, no new hires):** 2 senior FDEs initially seconded onto Tenex Ontology pilots. Plays double duty: bills client time + delivers product. Exactly the Palantir model.

**Total dedicated FTE: 9–11.** Well under 25% of engineering capacity at current scale.

### 5.7 The 6-month roadmap

```
Month 1 — Setup + design
  Hire founding AE, formalize PM, freeze MVP scope.
  Architecture review: Postgres + Postgres-vector for storage; finalize MCP
  spec compliance baseline (2025-11-25 revision).
  Sign 2 design partners from current Tenex F500 accounts at zero or nominal
  cost in exchange for data access + reference rights.

Month 2 — Connectors + ontology builder skeleton
  Ship Snowflake, Salesforce, ServiceNow connectors.
  First version of auto-ontology builder against design partner #1 data.
  MCP server prototype with hardcoded RBAC.

Month 3 — Policy engine + audit + write-back
  Cerbos integration, audit log, write-back actions for design partner #1.
  Beta with design partner #1's existing agents (their Claude + Cursor).
  Lock SOC 2 Type 2 audit kickoff.

Month 4 — Feedback loop + design partner #2
  Auto-refinement of ontology from agent-interaction data.
  Onboard design partner #2; ship Workday + Databricks connectors.
  First paid pilot ($120–250K) signed with design partner #1.

Month 5 — Productization + first commercial customer
  S3 connector. Object views UI. Customer-facing dashboards.
  First "non-design-partner" F500 sale; target $400–750K Year 1.
  Founding AE has 8–12 active F500 opportunities in flight.

Month 6 — MVP GA + category launch
  Public GA with 3 customer logos, 1 case study.
  ISO 42001 audit start. SOC 2 Type 2 in final stage.
  Internal Tenex enablement: every active Tenex engagement gets a
  Tenex Ontology pitch attached.
```

### 5.8 Success metrics

**At 6 months:**

- 3 paying F500 customers (≥$120K ACV each, mix toward $400K).
- $1.2–2.5M Year 1 ARR booked.
- 12+ pipeline opportunities sourced from existing Tenex engagements.
- 6 connectors GA; 3+ in beta.
- MVP-grade auto-ontology that generates an 80%-correct first-pass ontology in <2 weeks.
- Documented 2x reduction in time-to-first-agent-tool-call for a customer vs their prior bespoke MCP setup.

**At 12 months:**

- 8–12 paying F500 customers.
- $6–12M Year 1 ARR (+ committed Year 2 ramp to $15–25M).
- ~50% of new Tenex engagement SOWs include Tenex Ontology as a bundled product line.
- NDR >130% on the cohort that's been on the product >6 months.
- A defensible second product surface mapped (operational app layer, or vertical ontology starter packs).
- A 1–2-sentence "OpenFoundry vision" that customers nod at.

### 5.9 Kill criteria — when Tenex shuts this down

- **Customer pilot completion rate <50%** at month 6 — auto-ontology too brittle, FDE intervention too heavy, product economics break.
- **NDR <110%** at month 12 — moat thesis fails; switching costs aren't materializing.
- **Hyperscaler bundling.** If AWS or Microsoft ships a fully functional auto-ontology with native Bedrock/Foundry integration at <$50K/year by Q4 2026, the moat compresses. Pivot to vertical specialization ("Tenex Ontology for healthcare" with HIPAA-specific primitives).
- **Engineering burn-rate breach.** If Tenex Ontology engineering consumes >30% of total eng capacity at month 6, scale back scope (drop write-back, ship read-only) rather than degrade billable work.
- **Sales motion mismatch.** If <30% of pipeline comes from existing Tenex engagements at month 6, the attach-rate thesis is wrong and Tenex is competing with Palantir on cold ground — kill and rethink.

### 5.10 Why this beats the alternatives — restated

The team lead's prior framing was that agent RBAC is the industry-correct wedge but ontology may attach better for Tenex specifically. The full team analysis confirms this with refinements:

1. **The ontology choice is correct on attach rate.** Score 5/5 vs 3/5 for RBAC; competitive density is meaningfully lower; commoditization half-life is 3–5x longer.
2. **The agent platform rejection is correct.** Most crowded space, no Tenex-specific advantage, runtime commoditizing into model labs.
3. **The RBAC thesis is industry-correct but wrong-shape for Tenex.** RBAC/MCP-gateway is the wedge *for someone* — Microsoft, AWS, CyberArk, Astrix, Aembit. Tenex is not that someone. Tenex would be the 23rd entrant to a winner-take-2 category.
4. **Pure ontology without governance is also wrong.** Without the bundled governance plane, customer agents talk to data via any path (their own MCP, hyperscaler MCP, Composio, Arcade) and Tenex Ontology becomes one optional data source among many — Glean-shaped. With the governance plane bundled, Tenex Ontology becomes the *only safe path* to enterprise data, which is what makes it the operating-model substrate (the Palantir moat).
5. **Sales positioning matters more than product purity.** Don't sell this as "ontology" to most F500 buyers — they hear "we tried Foundry and couldn't afford it." Sell it as **"agent-ready data layer with built-in governance"** to the CDO/CIO co-buying with the CISO. Build the ontology underneath.

---

## Part VI — OpenFoundry: The Vision Honest About Its Trajectory

### 6.1 The verdict on the "agnostic across LLMs, warehouses, and clouds" thesis

Half-right.

- **Right:** F500 is multi-everything by necessity. Flexera 2025: 70% hybrid, avg 2.4 public clouds + private. CIOs say they want an agnostic control plane when interviewed; hyperscaler bundles have pricing power CIOs want to hedge.
- **Wrong:** "Agnostic across LLMs, warehouses, clouds" as a *V1 architecture* is operationally and economically suicidal for a 30-engineer team. The capability surface is too wide; the abstraction leaks too much; the engineering tax is 3x.
- **The actual moat candidate** is portable ontology + lineage-aware policy + identity-federated ABAC, *composed on top of Iceberg + one warehouse + one model provider in V1*, with credibility to add the second and third over years.

### 6.2 Where each agnostic axis leaks

**LLM-agnosticism** is mostly table-stakes (LiteLLM ships 100+ models). But the abstraction leaks badly on:

| Capability | Anthropic | OpenAI | Gemini | Abstraction leak |
|------------|-----------|--------|--------|-------------------|
| Prompt cache read discount | 90% (0.1x) | 50% | ~90% | Same workload can be 5x more expensive on OpenAI |
| Cache write premium | 1.25x (5m) or 2x (1h) | None | None (implicit) | Cache-aware orchestration cannot be uniform |
| Tool use schema | `tool_use` blocks + `cache_control` | function-calling JSON | function declarations | Translatable, but `tool_choice`, programmatic calling don't map cleanly |
| Structured output | `strict` not supported with programmatic | `response_format` + strict schemas | response schema | Strict-mode constraints differ |
| Multimodal | Vision yes, audio limited | Vision + audio | Vision + audio + native video | Routing a vision-heavy workflow uniformly requires the LCD |

"Switch model mid-workflow" works for the cheapest 30% of agentic work and is a dangerous abstraction for the top 70%. The real moat is *capability-aware orchestration*, not gateway translation.

**Warehouse-agnosticism** is being collapsed by Iceberg REST + Unity Catalog / Snowflake Horizon / Polaris federation. All three are public preview or GA as of 2025–2026. Federated query via Trino hits a 36 MB/s JDBC ceiling without system-specific connectors. The realistic V1 shape is "Iceberg + customer-chosen federated catalog" — not "abstract over Snowflake/Databricks." Risk: this is exactly the layer Databricks and Snowflake are themselves commoditizing.

**Cloud-agnosticism** requires BYOC (control plane / data plane separation, zero-access architecture). Operationally 3x the cost of multi-tenant SaaS. Margins drop to 50–70%. Not survivable for 30 engineers across all three hyperscalers in V1. Ship multi-tenant on AWS first, BYOC-on-AWS by month 9–12, Azure year 2, GCP year 3.

### 6.3 The competitive geometry

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

OpenFoundry would sit upper-right (open + horizontal). It would beat Glean on operational write-back / action orchestration. It would beat Atlan on agent orchestration and ontology runtime. It would beat Vendia on data modeling and policy depth. It would *not* beat Databricks Unity / Snowflake Horizon on warehouse-native governance — and trying to is a mistake. The play is to compose on top of them.

It loses to Foundry on enterprise distribution, deployment muscle, and FDE density. It loses to Databricks / Snowflake / Microsoft Fabric on hyperscaler co-sell economics. It loses to Glean on RAG quality and connector breadth in year 1–2.

### 6.4 The lesson from prior agnostic plays

Snyk, Datadog, HashiCorp, Confluent — all four agnostic winners spent 8–15 years compounding integration breadth and developer adoption. Neutrality was the *frame*; the moat was *the integration count + the workflow ownership*. Confluent's own analyst write-up: *"Confluent's multi-cloud, vendor-neutral approach provides some differentiation, but it's not significantly restrictive to competitors. Counter-positioning currently offers minimal competitive insulation."*

Tenex cannot replicate this in year 1–2 with 30 engineers. It can replicate it on a much narrower surface — say, "the ontology + identity-federated policy layer over Iceberg" — if it picks a tight scope.

### 6.5 The "ship opinionated, narrate agnostic" discipline

**The line for Tenex leadership: OpenFoundry as a public vision is sellable. OpenFoundry as a V1 product spec is undeliverable. Pick the discipline: ship opinionated, narrate agnostic, earn the right to expand surface area with each subsequent F500 win.**

The credible roadmap:

- **Year 1:** Anthropic + Snowflake OR Databricks (pick one based on first lighthouse customer) + AWS + Okta. Ontology DSL v1. BYOC-on-AWS by month 9–12. 2–3 lighthouse customers.
- **Year 2:** Add OpenAI as second model with capability-degradation handling. Add second warehouse (Databricks if you started Snowflake, vice versa). Add Azure BYOC. Add Entra ID federation. Cross-customer policy library v1.
- **Year 3:** Add Gemini. Add BigQuery. Add GCP BYOC. Add the second IdP that wins the next big deal. Auto-ontology inference matures. Vertical certified ontologies (BFSI, healthcare).

### 6.6 The required v1 capabilities for credible agnosticism

Even a partially-agnostic V1 needs all six of these to be defensible:

1. **Model abstraction with capability-aware degradation.** Don't just translate API surfaces — surface the diff (cache discount, tool-schema features, multimodal support, batch availability) so workflows route intelligently. Cost-aware + latency-aware routing as first-class.
2. **Iceberg-first warehouse layer with catalog federation.** Customer-owned object storage. Read/write via Iceberg REST. Unity / Horizon / Polaris all supported as catalog source of truth.
3. **BYOC deployment on at least one hyperscaler.** Anchored on AWS makes the most sense (largest market share, broadest F500 distribution).
4. **Ontology as portable artifact.** Declarative DSL or YAML/JSON spec for object types, properties, links, actions, functions, policy bundles. Version-controlled, exportable, diff-able. CLI + GitOps.
5. **Identity federation to any major IdP.** SAML/OIDC/SCIM authN; ABAC engine that inherits IdP attributes for per-cell row/column enforcement.
6. **One genuinely hard "magic" capability.** Lineage-aware permissions, cross-customer policy library, or auto-ontology inference. Pick one and dominate it. Tenex's pick should be lineage-aware permissions — it's the Foundry moat that no commercial alternative has.

### 6.7 The Tenex services bridge

The $300/storypoint pricing is what funds productization. Engagements should be structured as "deliver a Foundry-equivalent ontology on your stack" → "convert to OpenFoundry SaaS." This is the Palantir FDE playbook with a product anchor.

Every FDE engagement is a free distribution channel for OpenFoundry: the engineer learns the abstractions, the customer's data ends up modeled in OpenFoundry-compatible form, the next engagement gets cheaper. Salesforce's lock-in is that every admin who learned the sObject model and every developer who learned Apex became a free distribution channel. Tenex's equivalent: every FDE engagement delivered through OpenFoundry primitives makes the platform more powerful and trains a future Tenex-skilled engineer who will pull Tenex into their next job.

---

## Part VII — The 36-Month Roadmap and Capital Allocation

### 7.1 The full multi-year picture

```
Year 1: $15M → $30M ARR
─────────────────────────
  Engineering: 34 billable / 6 spine (15% on spine)
  Spine investment: $3–4M (engineers + tooling + 1 PMM end of year)
  Beachhead: Tenex Ontology MVP ships Q1 2027
  Pricing experiment: $50K platform license bundled into top 5 engagements
  Reporting: separate product ARR from services revenue in board materials
  Milestone gate (12 months): 3 paying product customers at ≥$100K ARR each
  Public narrative: "agent-ready data layer for the F500"
  Long-term vision narrative: OpenFoundry (used in CIO conversations)

Year 2: $30M → $60M ARR (if milestone gate cleared)
──────────────────────────────────────────────────
  Engineering: 30 billable / 10 spine (~20-25% on spine)
  Raise $15–25M Series A on product trajectory + services cash flow
  Add 2 product-quota sales reps with comp plans tied to product ARR
  Begin second product surface (operational app layer — "Workshop equivalent")
  Add: lineage-aware permissions, Cross-customer policy library v1, ISO 42001
  Onboard 1 named SI partner (target: Accenture or Deloitte)
  Pricing: introduce vertical ontology starter packs (BFSI, healthcare, manuf.)
  Product ARR target end of year: $10–15M (15-25% of total revenue)
  Milestone gate: NDR >130%; <30% engineering on spine maintenance

Year 3: $60M → $120M ARR
─────────────────────────
  Engineering: ~25-30% on spine (Palantir 2018-2020 inflection)
  Add second warehouse, Azure BYOC, second LLM provider
  Vertical certified ontologies in 2 industries
  Product ARR target: $30–50M (35-45% of total revenue)
  S&M intensity falling visibly
  GM trajectory: 45% → 55-60% (services + product blend)
  Public vision: "OpenFoundry — agnostic across the modern data + AI stack"
  Decision point: stay independent or strategic round / acquisition discussions

If milestone gate NOT cleared at month 12:
  Cut spine team to 2 engineers in sustained-pattern role
  Accept services trajectory, optimize for cash flow + strategic acquisition
  Re-test productization in 18 months on a different beachhead
```

### 7.2 The five 90-day decisions

1. **Which vertical?** BFSI (recommended) vs life sciences vs federal vs manufacturing. Pick one and pre-commit. BFSI's advantages: high regulatory pressure, willing-to-pay, lots of fragmented SaaS (CRM + risk + trading + compliance + HR + comms), strong existing forward-deployed culture from the consulting industry, and Anthropic/Accenture's BFSI focus creates a co-sell tailwind.
2. **Which SI partner?** Accenture (Anthropic-aligned) vs Deloitte (Google-aligned) vs in-house FDE-only. Recommendation: in-house first, SI as channel by month 12. But the SI relationship needs to start being cultivated immediately.
3. **OSS or managed-only?** Strong recommendation: OSS-licensable MCP gateway + ontology DSL (Apache 2.0) with managed SaaS on top. The "Anthropic-of-data" positioning — open core, paid governance and managed deployment.
4. **Cedar, OpenFGA, or build-from-scratch on the policy engine?** Strong recommendation: OpenFGA (Auth0/Okta-backed, Zanzibar-style, ReBAC-native). Cedar locks you into AWS thinking; building from scratch is the wrong battle.
5. **What is the metric you sell on?** Time to onboard a new agent into the enterprise from days to minutes with full governance. That is the productivity story a CAIO can defend to a board.

### 7.3 The capital allocation table

| Allocation | Year 1 | Year 2 | Year 3 |
|------------|--------|--------|--------|
| Engineering FTE total | 40 | 60 | 80 |
| Spine FTE | 6 (15%) | 12 (20%) | 24 (30%) |
| Billable FTE | 34 (85%) | 48 (80%) | 56 (70%) |
| Spine $ investment | $3–4M | $8–10M | $20–25M |
| Outside capital raised | $0 | $15–25M Series A | $40–60M Series B (optional) |
| Total ARR | $30M | $60M | $120M |
| Product ARR | $1–2M | $10–15M | $30–50M |
| Product as % of revenue | 5% | 20% | 35–45% |
| Realized GM | 45% | 50% | 55–60% |
| ARR per FTE | $300K | $400K+ | $600K+ |

### 7.4 What changes in the org chart

```
Year 0 (now):
  CEO
   ├─ COO (delivery operations)
   ├─ CTO (engineering)
   │   └─ 30-50 engineers (all billable)
   └─ Strategists, sales, ops

Year 1:
  CEO
   ├─ COO (delivery operations)
   ├─ CTO (engineering)
   │   └─ 34 billable engineers
   ├─ GM Product (Tenex Ontology) ◄── NEW
   │   ├─ 6 spine engineers
   │   ├─ Product Manager
   │   ├─ Founding AE
   │   └─ PMM (part-time → full-time by month 9)
   └─ Strategists, sales, ops

Year 2:
  CEO
   ├─ COO (delivery operations)
   ├─ CTO (engineering, services side)
   ├─ GM Product (Tenex Ontology + 2nd product line)
   │   ├─ VP Eng (Product)
   │   │   └─ 12 spine engineers across 2 product lines
   │   ├─ Director of Product
   │   ├─ 2 product-quota AEs
   │   └─ PMM team (2)
   ├─ VP Marketing ◄── NEW
   └─ Strategists, sales, ops
```

The most important structural choice: **GM Product reports to CEO, not CTO.** A CTO-reported product team is too easily reabsorbed into the engineering pool when billable demand spikes — the #1 failure mode of services-to-product transitions.

### 7.5 Risks and mitigations

| Risk | Probability | Mitigation |
|------|-------------|------------|
| Hyperscaler bundles auto-ontology | High | Vertical-specialized ontologies year 2; FDE moat |
| Alation+Numbers Station outpaces | Medium-high | Ship faster on action layer; F500 distribution advantage |
| Spine team underfunded, dead zone | Medium | Separate P&L, executive air cover, milestone gate |
| Pricing model rejected by F500 | Low | Bundle into existing engagements first; transparent pricing |
| FDE-to-product engineer conversion fails | Medium | Hire 2 product PMs from product-native companies for cultural anchor |
| Outside capital sours on services drag | Medium | Report product ARR separately from day 1, GitLab-style |
| Tenex sales team can't sell software | High | Separate quota carriers for product from day 1 |
| MCP loses to A2A or another protocol | Low-medium | Ontology is the product; MCP is just one consumption interface — swap is a quarter of work |
| Palantir notices and reacts | Medium | Stay below the radar 12 months; target Palantir-skeptical buyers |
| Founder/leadership conviction falters under demand pressure | High | Public commitment to milestone gates; quarterly product ARR reporting |

The most dangerous risk is the last one. Every quarter, a major F500 client will offer Tenex a $5M services engagement on terms that require dedicating product engineers. Saying yes feels like growth; it is actually decision to stay services. The discipline to say no — or to offer the engagement at lower scale to preserve spine capacity — is the test of trajectory C.

---

## Key Takeaways

1. **Tenex at $15M ARR is at the inflection point.** Smaller is too early to productize; bigger is usually too late. The next 12 months determine whether trajectory is Palantir-shaped (product spine + FDE compounding), Accenture-shaped (services + asset library), or Cresta/Tribe-shaped (permanent consultancy).

2. **The right beachhead is a self-learning data/ontology platform with bundled MCP governance — Tenex Ontology.** It attaches to ~80% of existing Tenex engagements, captures the data-modeling output that today walks out the door, scores 4.30 vs 2.65 (RBAC) vs 1.70 (agent platform) on a weighted 10-dimension comparison, and is the only candidate where Year 1 → Year 3 is a single product evolution rather than a pivot.

3. **Foundry's actual moat is the stacked combination of Ontology + FDE motion + lineage-aware mandatory access controls + defense-grade compliance.** The single most underrated piece is Object Storage V2 + the Funnel — the indexed object database with row/cell-level policies decoupled from underlying datasets. Tenex must replicate this from day one.

4. **The "all writes are Actions" invariant is the architectural pattern that makes agent RBAC tractable.** No matter how an edit is proposed (UI, function, LLM, external agent), the actual mutation goes through a typed, validated, permission-checked, audited Action submission. Build this from day one.

5. **The smallest viable Foundry-equivalent spine fits in ~6 months and ~10.5 person-months of engineering work** (Object Store + Action service + OSDK + Workshop-equivalent + MCP + Functions + Data Connection + Branching + Lineage). $1M of engineering investment against $15M ARR. The constraint is not capital — it is discipline.

6. **Salesforce + Foundry triangulate the same six-layer minimum for an enterprise OS** — typed schema, metadata-as-code, declarative customization, programmatic escape hatch, permission+sharing model, packaging+distribution. Ship five and you have a product; ship all six and you have a platform.

7. **Steal from Salesforce: metadata-driven multitenancy, strongly-typed named primitives, permissions ⊥ sharing, additive permission sets, describe API before CRUD API, source-driven definition lifecycle.** Avoid: custom programming language (Apex), custom frontend framework (Aura), multiple overlapping automation tools, per-transaction uncatchable governor exceptions.

8. **The recommended capital allocation is the milestone-gated barbell:** 6 spine FTE (15% of engineering), $3–4M Year 1 investment (~25–30% of realized GM), Tenex Ontology MVP in 6 months, gate the doubling-down decision on 3 paying product customers at ≥$100K ARR each by month 12. Above that bar, raise $15–25M Series A. Below it, harvest more aggressively and accept services destiny.

9. **The pricing transition tactic is bundling a $50K platform license into every top-5 services engagement.** Palantir-style "bootcamp + limited license" entry. Trains the sales motion to sell software alongside hours; generates trackable product ARR; creates a forcing function for the spine team to make the platform compelling enough to justify the license.

10. **"OpenFoundry as agnostic across LLMs, warehouses, and clouds" is half-marketing, half-real.** Ship opinionated (Anthropic-first, one warehouse, AWS-first, Okta-first) in V1; narrate agnostic in CIO conversations; earn surface-area expansion with each F500 win. The real moat is portable ontology + lineage-aware policy, not agnosticism itself.

11. **Every quarter, ask: what % of new-logo first-dollar revenue came from the product vs the engagement?** Year 1: 5–10%. Year 2: 20–30%. Year 3: 40–50%. If it's not climbing, productization isn't happening — the company is just adding products to services revenue rather than transitioning.

12. **The most dangerous risk is the last one.** Founder/leadership conviction faltering under demand pressure. Every quarter, a major F500 client will offer Tenex a $5M services engagement on terms that require dedicating product engineers. Saying yes feels like growth; it is actually a decision to stay services. The discipline to say no — or to scale the engagement to preserve spine capacity — is the test of trajectory C.

---

## Predictions and Falsifiable Bets

1. **By Q2 2027, Alation+Numbers Station will be the strongest direct competitor to Tenex Ontology, not Palantir.** Their May 2025 acquisition + October 2025 Agent Builder launch + 7-year catalog head start positions them best to ship the "translation layer between LLMs and enterprise structured data" thesis. Tenex's offsetting advantages must be speed-to-deploy and action-layer depth.

2. **By Q4 2026, Microsoft will have shipped a Fabric-based auto-ontology with native Copilot Studio integration as part of M365 E5.** This will commoditize the auto-build feature at the low end. Tenex Ontology survives by being deeper at the action layer + governance and by serving Palantir-skeptical buyers who don't want Microsoft lock-in.

3. **By end of 2027, the agent identity/RBAC standalone category will have <5 independent vendors remaining above $50M ARR.** Astrix → Cisco, SGNL → CrowdStrike, and 2–3 others will be acquired. Agent identity becomes a security platform feature, not a product. Tenex made the right call not to enter this category.

4. **MCP standardization will accelerate to the point that "MCP gateway" is a Kong/Apigee/Cloudflare commodity feature by Q3 2026.** Gateways alone will not be a viable standalone business by 2027. The differentiation moves up the stack — to policy/ontology — exactly where Tenex Ontology lives.

5. **By end of 2027, at least one "Foundry-equivalent" vendor outside Palantir will reach $50M+ ARR with a defensible ontology layer.** Whether that vendor is Tenex, Glean (extending into structured data), Alation+Numbers Station, Atlan, or a yet-unfunded startup is the open question. Tenex has the conditions — F500 distribution, FDE bench, $15M ARR services cash flow — to be that vendor if discipline holds.

6. **Sierra and Decagon will diverge in margin profile by end of 2027.** Sierra's FDE-heavy motion will compress GM into the 50–60% range. Decagon's pure-product approach will maintain 65–75% GM. Both will exceed $300M ARR. The lesson for Tenex: FDE delivery works, but only if the *pricing* is product-shaped (outcome-based), not services-shaped (storypoint). Decagon's explicit "no armies of forward-deployed engineering" Series D quote will age well.

7. **Palantir's terminal growth will compress from current expectations.** Morningstar already lowered from 15% to 12%; further compression to 8–10% is plausible by 2028 as AI labs (OpenAI DeployCo) and AI-native data platforms eat the new use cases at the top and the bottom. Palantir's stacked moat (ontology + FDE + compliance) survives in defense and regulated commercial; the broader commercial growth slows.

8. **By 2028, the "ontology + governance + agents" stack will be standard enterprise infrastructure** the way "data warehouse + ETL + BI" was in 2010 and "data lake + Spark + ML platform" was in 2018. The vendors who establish category-defining positioning in 2026–2027 — when buyers are still confused about what to call it — will own the next decade. Tenex's "agent-ready data layer with bundled governance" positioning is a credible bid for that ownership.

9. **Iceberg will become the assumed warehouse substrate for ontology platforms by Q2 2027.** Unity Catalog, Snowflake Horizon, and Polaris federation will make "warehouse-agnostic" via Iceberg the default architecture. Tenex Ontology should bet on Iceberg + customer-chosen federated catalog from V1.

10. **The single most important number for Tenex over the next 36 months is product ARR as a % of new-logo first-dollar revenue, measured quarterly.** If it climbs from 5% (Q1 2027) to 25% (Q1 2028) to 45% (Q1 2029), Tenex is on the Palantir trajectory. If it doesn't, Tenex is on the Cresta trajectory. The transition is identifiable in real time, and the discipline to course-correct is what separates the two outcomes.
