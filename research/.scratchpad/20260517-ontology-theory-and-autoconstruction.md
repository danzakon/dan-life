---
title: Ontology — Theory, Landscape, and the Auto-Construction Problem
date: 2026-05-17
author: ontology-researcher (tenex-openfoundry-research)
status: scratchpad
purpose: Take "ontology" from buzzword to deeply understood concept, and map the landscape of automated ontology construction to inform Tenex's beachhead-product decision.
---

# Summary

"Ontology" is a forty-year-old computer-science term that Palantir resurrected, rebranded, and weaponized into the most defensible piece of its $300B market cap. In 1993 Tom Gruber defined it as **"an explicit specification of a conceptualization"** — the set of objects, properties, and relations that some system commits to existing. The Semantic Web spent two decades trying to build a global one with RDF/OWL/SPARQL and largely failed; Google's Knowledge Graph, schema.org, and enterprise knowledge graphs succeeded by being narrower, more pragmatic, and centrally curated.

In 2025–2026 the term is being reclaimed by three different camps at once:

1. **Semantic-layer vendors** (dbt, Cube, LookML, Microsoft Fabric, AtScale) — metrics-as-code over warehouses, now adding MCP for agents.
2. **Data catalogs** (Alation, Atlan, Collibra) — metadata graphs adding agentic agents; Alation bought Numbers Station in May 2025 to do exactly this.
3. **Agent-native data startups** (Datris, Corvic, Meko, Exabase, Kumo, Glean) — building data layers where AI agents are first-class citizens and where ontology is constructed continuously from data, schemas, and agent interactions.

**The central tradeoff:** ontologies that are precisely correct require human authoring; ontologies that are fluid and useful at scale require LLM inference. The frontier — and Tenex's potential beachhead — is the **typed-deterministic-core + LLM-fluid-periphery** synthesis. What can be auto-inferred (object types from schemas, link types from FKs, basic actions from CRUD) is now table stakes; what fundamentally requires human authoring (business-process actions, organization-specific markings, the *purpose* of an object) is the moat.

For Tenex: the minimum viable ontology product is probably **not** a standalone ontology platform — it's an **ontology layer welded to workflow/agent execution**, sold to F500 mid-market companies that can't afford Palantir but need agents that don't hallucinate over their structured data. Glean has proven the unstructured-data version of this; the structured-data version is wide open and Alation+Numbers Station has a one-year head start.

---

# Key Findings

1. **The original definition is still the cleanest one.** Gruber's "explicit specification of a conceptualization" survives because it captures both the *artifact* (a schema with classes, relations, axioms) and the *commitment* (every system implicitly believes some things exist; an ontology makes those beliefs inspectable). Every commercial ontology product is some compromise on which parts of this you formalize.

2. **There is a strict expressiveness ladder:** Taxonomy ⊂ Data Model ⊂ Ontology ⊂ Knowledge Graph (= Ontology + Instance Data). Most "ontology products" actually sit at the data-model rung but borrow the word for marketing weight. Palantir's Foundry Ontology genuinely lives at the ontology rung because it includes action types (verbs, with side-effects), interfaces (polymorphism), and a permission-aware execution layer — none of which fit in a data model.

3. **The Semantic Web's failure is instructive, not damning.** RDF/OWL/SPARQL/SHACL is technically rigorous but socially unscalable: nobody wants to author OWL, and "anyone can say anything" produces noise, not knowledge. The pieces that survived — JSON-LD, schema.org, Wikidata, enterprise KGs, SHACL for validation — are the ones that traded expressive power for curation discipline and pragmatic scope.

4. **The semantic-layer market is bifurcating into "thin metrics" and "thick ontology."** dbt MetricFlow + Cube + LookML + Power BI semantic models all do *measures and dimensions over a warehouse*. None of them model action types or workflows. They are necessary but insufficient ingredients of an ontology platform; the gap between "semantic model" and "Foundry Ontology" is roughly the gap between "I can compute revenue consistently" and "I can run my operations on this".

5. **Data catalogs are racing to become semantic layers AND agent platforms.** Alation's acquisition of Numbers Station (May 2025) and launch of Agent Builder (Oct 2025) is the clearest signal: the catalog vendors realized that *metadata + governance + a knowledge layer + agents* is the same product as *what Palantir calls the Ontology*. Atlan and Collibra are following. None of them have Foundry's action-types-as-verbs model yet.

6. **Auto-construction works for the structural skeleton and fails for the semantic body.** Recent LLM-driven approaches (RIGOR, OntoKGen, OLLM, GalaxyWeaver, Schema-Miner) reliably extract: object types from tables, properties from columns, link types from foreign keys (including *implicit* FKs via value-overlap analysis), simple taxonomies from documents. They fail at: domain-specific *actions* (what does "approve" mean here?), business-specific *markings* (export-controlled? PII? embargoed?), organization-specific *roles* and *workflows*, and the *purpose* an object serves in a process. These require human-in-the-loop authoring and they always will, because the information needed simply isn't in the data.

7. **The agent–ontology interface is where the next wedge is being driven.** Tool-use over typed object types (rather than raw SQL) is dramatically more reliable: the agent picks from a constrained vocabulary, every action is a structured-output call, every write goes through a governed action type. MCP is becoming the lingua franca — Cube, dbt, Glean, Alation, Datris, Meko, Exabase, Corvic, and Palantir all ship MCP servers in 2025–2026. The interesting design question is no longer "should agents have MCP access?" but "what is the schema of the operations the MCP server exposes?"

8. **Kumo and KumoRFM hint at a deeper shift.** A foundation model pre-trained on tens of thousands of relational schemas can do zero-shot prediction on a *new* schema without feature engineering. The implication: the warehouse itself can become predictive infrastructure, and the ontology becomes the substrate the predictions reference. This collapses the ML pipeline into the ontology layer.

9. **For Tenex specifically:** an ontology platform is *only* defensible if bundled with execution (workflows + agents). The standalone-semantic-layer market (dbt, Cube) is being aggressively commoditized; the standalone-catalog market (Alation, Collibra, Atlan) is consolidating into AI-native platforms. The white space is **mid-market industrial / financial-services / healthcare ops** — companies that need a Foundry-like operational digital twin but cannot pay Foundry prices or wait Foundry timelines.

---

# Details

## 1. What ontologies actually are

### CS roots: Gruber, 1993

The canonical reference is Tom Gruber's 1993 *Knowledge Acquisition* paper "A Translation Approach to Portable Ontology Specifications" and his 1995 follow-up "Toward Principles for the Design of Ontologies Used for Knowledge Sharing." Both are among the most-cited CS papers of the 1990s. The core definition:

> *"An ontology is an explicit specification of a conceptualization."* — Gruber, 1993
>
> *"A conceptualization is an abstract, simplified view of the world that we wish to represent for some purpose. Every knowledge base, knowledge-based system, or knowledge-level agent is committed to some conceptualization, explicitly or implicitly."*

Two things matter here. First, an ontology is an *artifact* — it's a thing you write down: classes, relations, functions, axioms. Second, an ontology is a *commitment* — every system that processes data implicitly believes that certain things exist (customers, orders, machines, transactions). Making that commitment explicit is the move.

Gruber's 1995 design principles — clarity, coherence, extendibility, minimal encoding bias, minimal ontological commitment — are still the right design checklist thirty years later.

### Philosophy roots

The term is borrowed from philosophy, where it means "a systematic account of Existence" — what kinds of things are there? Aristotle's *Categories* (substance, quantity, quality, relation, place, time, position, state, action, passion) is a paradigmatic ontology. Quine's "On What There Is" (1948) made the modern philosophical version sharp: *to be is to be the value of a bound variable*; whatever your theory quantifies over is what your theory commits to existing.

This matters for engineering because it tells you what "ontology" means at its limit. When Palantir says "the Ontology is the digital twin of an organization," the philosophical reading is: the Ontology is the set of *what your organization is committed to believing exists*. Customers, orders, aircraft, sorties, claims — these are the bound variables of your operational theory of the world.

### AI roots

In AI, ontologies got their first practical use in expert systems and knowledge-based agents in the late 1980s — CYC (Lenat, 1984+) being the most famous attempt to formalize commonsense knowledge. The Ontolingua project at Stanford KSL (where Gruber worked) was the systems infrastructure for *sharing* ontologies between AI systems. The intuition driving all of this work: agents that share a vocabulary can cooperate; agents that don't, can't.

This is exactly the intuition behind today's MCP-for-agents wave, three decades later.

### Taxonomy vs. schema vs. data model vs. ontology vs. knowledge graph

```
                  ┌────────────────────────────────────────────────────┐
                  │  Expressiveness ladder                              │
                  ├────────────────────────────────────────────────────┤
Knowledge Graph   │  Ontology + instance data + identifiers             │
                  ├────────────────────────────────────────────────────┤
Ontology          │  Classes + relations + axioms + logical rules       │
                  │  (can infer new facts: transitivity, subclassing,   │
                  │  cardinality, equivalence, disjointness)            │
                  ├────────────────────────────────────────────────────┤
Data Model        │  Classes + properties + simple relationships        │
                  │  (no inference; queries must be predetermined)      │
                  ├────────────────────────────────────────────────────┤
Schema            │  Shapes/constraints on data (tables, columns,       │
                  │  types, cardinality)                                │
                  ├────────────────────────────────────────────────────┤
Taxonomy          │  Hierarchical classification (subclass-of)          │
                  └────────────────────────────────────────────────────┘
```

Concretely:
- **Taxonomy**: "A Border Collie is a Dog is a Mammal is an Animal."
- **Schema**: `CREATE TABLE dog (id INT PRIMARY KEY, name TEXT, breed TEXT REFERENCES breed(id))`
- **Data model**: a UML diagram of Person, Dog, Breed with `owns` and `is_a` relationships.
- **Ontology**: the data model plus "a Vegetarian is a Person who does not eat Meat" plus enough axioms that you can ask "find Vegetarians whose Dogs eat raw meat" and get an answer.
- **Knowledge graph**: the ontology plus the actual facts about Spot, Fluffy, Dan, Alice — with globally unique identifiers.

Kurt Cagle's compact formulation (Jan 2025): `Knowledge Graph = Schema + Taxonomy + Conformant Instance Data`. Ontology is `Schema + Taxonomy`.

### Why "ontology" became the Palantir-chosen word

Palantir could have called it the "object model," the "domain model," the "semantic layer," the "knowledge graph," or even the "digital twin." They chose "Ontology" — capital O — and stuck with it. Reasons (some inferable from product docs and Karp/Sankar interviews):

1. **It commits to more than schema.** A schema is structural; an ontology is *semantic*. Calling it "ontology" signals that there is *meaning* in the model, not just shape.
2. **It includes verbs.** Foundry's Ontology has *action types* — modifications to the world. No data model worth the name has those. "Ontology" is the only word in the CS vocabulary expansive enough to include actions, side effects, and write paths alongside object types and relationships.
3. **It's culture as much as technology.** Foundry Ontology training is a multi-day investment for analysts. Calling it "ontology" forces the customer to take it seriously as an organizational artifact, not as a database schema that some intern can rename.
4. **It's the right word philosophically.** What Foundry is doing — making explicit the entities the organization is committed to believing exist, and the actions it is committed to being able to perform on them — is *exactly* ontology in the Gruber/Quine sense.

## 2. The formal stack: RDF, OWL, SPARQL, SHACL, schema.org

Layer by layer:

| Layer | What it is | Year | Practical role today |
|---|---|---|---|
| RDF | Triples: `<subject> <predicate> <object>` | 1999, revised 2004, 2014 | Universal data model; substrate for KGs |
| RDFS | Classes, subclass-of, domain/range | 2004 | Light schema; rarely used alone |
| OWL | Description-logic ontology language | 2004, OWL 2 in 2009 | Used in life sciences, libraries; mostly avoided elsewhere |
| SPARQL | Query language for RDF | 2008, SPARQL 1.1 in 2013 | Production query language for RDF stores |
| SHACL | Shape-based constraint language | 2017 | Has largely replaced OWL for validation |
| JSON-LD | RDF in JSON form | 2014, 2020 | What actually shipped on the web (schema.org markup) |
| schema.org | A curated vocabulary | 2011 | Powers Google rich results; quietly enormous |

The honest story is this: the *expressive power* of OWL was never matched by *practical demand*. Most teams that adopted RDF used it for vocabulary mapping, not for reasoning. SHACL won for validation because it's procedural and predictable; OWL's open-world assumption — "things you didn't say might still be true" — is exactly the wrong default for enterprise data validation. Bob DuCharme's 2021 essay "You probably don't need OWL" captures the consensus.

What *did* happen on the Semantic Web:
- **schema.org** became universal. As of December 2025 (v29.4), 31% of the public web has schema.org markup; tens of millions of domains. It's the most successful ontology ever deployed — vocabulary across people, places, events, products, recipes, organizations, jobs, medical procedures. Google's Knowledge Graph is largely populated from it.
- **Wikidata** (1.5B+ statements) became the world's largest open KG, a structured Wikipedia that everything from Apple's Siri to academic NLP datasets draws on.
- **JSON-LD** quietly became the dominant serialization, supplanting RDF/XML.
- **DBpedia** anchored the "Linking Open Data" cloud of cross-referenced KGs.

So: the Semantic Web *as envisioned* (a global graph of distributed inference) didn't ship. The Semantic Web *as it happened* (curated vocabularies + JSON-LD + a few mega-KGs + schema.org as the lingua franca of structured web data) shipped enormously.

**When formalism matters**: cross-organizational data integration with strict semantics (pharma, libraries, government, regulated finance); domains where logical inference produces real lift (drug interactions, legal compliance); and where multiple parties must agree on terms (FIBO, MeSH, GO).

**When formalism is overkill**: single-organization operational systems; cases where a typed object model + business logic in code does the job; anywhere the cost of authoring OWL exceeds the value of the inference it would produce. Which is most of enterprise.

## 3. The semantic-layer landscape — practical commercial cousins

The semantic-layer market is the *most direct* commercial analog to ontology, even if it sits one rung down on the expressiveness ladder. The market split:

```
                 ┌────────────────────── Semantic-Layer Stack ──────────────────────┐
                 │                                                                  │
Application      │   AI agents, BI dashboards, embedded analytics, notebooks        │
─────────────────┼──────────────────────────────────────────────────────────────────┤
Serving          │   Cube.dev (REST/SQL/GraphQL/MCP) │ dbt Cloud Semantic Layer API │
                 │   Bonnard (Cube + multi-tenant)    │ Cube MDX endpoint for Excel │
─────────────────┼──────────────────────────────────────────────────────────────────┤
Definitions      │   dbt MetricFlow (YAML)            │ Cube schema (YAML/JS)        │
                 │   LookML                            │ AtScale models                │
                 │   Power BI semantic models (TMDL)   │ Kyligence                     │
─────────────────┼──────────────────────────────────────────────────────────────────┤
Catalog/governance│  Atlan, Alation, Collibra, OpenMetadata, Purview                 │
─────────────────┼──────────────────────────────────────────────────────────────────┤
Transformation   │   dbt Core / dbt Cloud, SQLMesh                                   │
─────────────────┼──────────────────────────────────────────────────────────────────┤
Warehouse        │   Snowflake, Databricks, BigQuery, Redshift, Fabric               │
                 └──────────────────────────────────────────────────────────────────┘
```

### dbt Semantic Layer + MetricFlow

- **What it is**: Metrics-as-code defined in YAML alongside dbt models. MetricFlow is the query engine that resolves measures, dimensions, entities, joins, and time grains into warehouse SQL.
- **What it does well**: Native to the dbt project; Git-versioned; tests and lineage out of the box; dbt MCP server (announced 2025) exposes metrics to agents.
- **Where it falls short**: No native serving layer (you need dbt Cloud's API, which is paid). No caching/pre-aggregation. No multi-tenancy. No actions — only measures. It's a metrics layer, not an ontology.

### Cube.dev

- **What it is**: Universal semantic layer / "headless BI". Define cubes (entities), dimensions, measures, joins, and pre-aggregations in YAML or JS. Serve over REST, SQL, GraphQL, MDX (Excel), and increasingly MCP.
- **What it does well**: API-first, sub-second response via CubeStore pre-aggregation, multi-tenancy via security contexts, embedded analytics primitives.
- **Where it falls short**: Still measures-and-dimensions; no action types; no permissioned write path. The model is read-shaped. Agent governance is bolted on, not native.

### LookML (Looker / Google Cloud)

- **What it is**: The original metrics-as-code DSL (2012). Defines explores, views, dimensions, and measures. Now integrated with Gemini for AI-driven model suggestions.
- **What it does well**: Battle-tested governance; tight Looker BI integration; Google is investing heavily in AI augmentation.
- **Where it falls short**: Locked to Looker; not a serving layer for external apps; not action-aware.

### Microsoft Fabric semantic models / Power BI

- **What it is**: The Power BI tabular model, rebranded as "semantic models" in Fabric. Direct Lake mode reads Parquet/Iceberg directly; TMDL is the open definition language; XMLA endpoint provides programmability.
- **What it does well**: Massive enterprise installed base (tens of millions of active models); ubiquitous in F500 BI; strong AI integration via Fabric IQ. Microsoft retired *auto-generated default* semantic models in late 2025, signaling a bet on **explicit, curated** semantic modeling.
- **Where it falls short**: Microsoft-centric stack; star-schema-oriented; not a general ontology platform. Like LookML, it models analysis, not operations.

### AtScale, Kyligence

- **What they are**: Older semantic-layer products focused on OLAP-style virtualization and pre-aggregation across cloud warehouses. AtScale leans BI; Kyligence leans Apache Kylin heritage + Copilot AI assistant.
- **Where they sit**: Mid-market enterprise BI acceleration; not building toward operational ontologies.

### Atlan, Alation, Collibra — catalog + semantic + AI

These are *data catalogs* that are aggressively expanding into semantic-layer + agentic territory:

| Vendor | Stance | Recent moves |
|---|---|---|
| **Alation** | "Data intelligence platform"; metadata + knowledge layer + agent builder | Acquired Numbers Station (May 2025) for ~$17M+ to add AI-agent capability on structured data. Launched Agent Builder at revAlation Oct 2025 with MCP support. Chat with Your Data feature (Aug 2025 beta) uses knowledge layer for grounded query agent. |
| **Atlan** | "Active metadata platform"; AI-native context pipeline | Enterprise Data Graph with 80+ connectors; AI agents bootstrap descriptions, link business terms, generate semantic views from query history; MCP server for downstream AI tools. Pricing aggressive ($15-$30/user/mo on lower tiers). |
| **Collibra** | "Data governance + AI registry"; structured workflows | Unified AI registry centralizes use cases/models/agents across Vertex AI, SageMaker, Databricks. Stewardship workflows. Slower to AI-native posture; enterprise compliance lean. |

**The strategically important thing about Alation+Numbers Station**: Sangani's public framing is that LLM hallucination is the wall between enterprises and AI adoption, and the fix is "a translation layer that sits between the LLMs and an enterprise's data." That translation layer is *exactly what Palantir calls the Ontology.* Alation's bet is that they own the metadata foundation, Numbers Station owned the LLM-over-structured-data agents, and together they're building Foundry-for-everyone-else.

This is the single most direct competitor to a Tenex ontology product.

## 4. The AI-native ontology landscape (2024–2026)

A wave of startups has been building "data layers for agents" — most of them claim some form of ontology-construction. They split roughly into four camps:

### 4a. Agent-native data platforms

| Vendor | Pitch | Reality |
|---|---|---|
| **Datris.ai** | "First MCP-native data platform"; AI-powered ingest/validate/transform; AI schema generation; 30+ MCP tools | Open-source (AGPL-3.0); positioned against Airbyte/Fivetran/dbt; useful for agent-driven ETL but *not* an ontology in the Foundry sense — closer to an AI-augmented data pipeline |
| **Corvic AI** | "Intelligence Composition Platform"; CAPA + Mixture-of-Spaces + ECoAA layers; agentic data transformation; multimodal retrieval | Invite-only beta; reframes ontology as embedding spaces with agent orchestration on top; less rigorous as a typed object model, more focused on multimodal reasoning |
| **Meko (Yugabyte)** | "Agent-native data infrastructure" with compounding memory, shared knowledge, decision traces; built on YugabyteDB | Launched May 2026; "datapack" primitive holds memory, knowledge, conversations, traces. Targets the multi-agent memory/state problem more than enterprise data modeling. |
| **Exabase** | "Data layer for agents"; Memory API + Resources API + Bases API; "dynamic ontology" that tracks relationships, resolves contradictions | Pitch is consumer-flavored ("notes, files, bookmarks"); operates as agent memory infrastructure, not enterprise data modeling. Uses "ontology" loosely. |
| **Vendia** | MCP gateway / data sharing across enterprises | Closer to a federated data fabric with agent access than an ontology platform; useful integration point but not a competitor product |
| **Cinchy** | "Dataware / data collaboration"; network of meaning; eliminate the integration tax | The most ontology-shaped of this group philosophically (data exists independently of apps; network-based architecture). Older positioning (2023+); slower commercial traction than the AI-native crowd. |

### 4b. Knowledge-graph / enterprise-search incumbents

| Vendor | Pitch | What's actually under the hood |
|---|---|---|
| **Glean** | "System of context" for enterprise AI; horizontal knowledge graph + personal graph; 100+ connectors | Knowledge graph built per customer over indexed content, people, activity. Permissions-respecting at item level. Hosts MCP servers integrated with OpenAI Agents SDK, LangGraph, Bedrock, Google ADK. The *unstructured-data* gold standard for agent-grounded enterprise AI. |
| **Cognite** | Industrial DataOps + ontology for asset-heavy industries | Cognite Data Fusion white-labeled by other vendors; Cognite Atlas AI on top. Named Leader in IDC MarketScape Worldwide Industrial DataOps Platforms 2026 (March 2026). The strongest existing vertical ontology platform outside Palantir. |

### 4c. Foundation models for relational data — Kumo

**Kumo.ai** is in a category of one and worth a separate treatment.

- **KumoRFM**: A "relational foundation model" pre-trained on tens of thousands of heterogeneous relational datasets. Represents the database as a temporal heterogeneous graph: rows → nodes, FKs → edges, timestamps preserved.
- **How it works**: Schema-agnostic row encoder + Relational Graph Transformer + in-context learning module. At inference, it samples historical entities, retrieves their ground-truth labels via a graph sampler, and predicts using context examples — same principle as few-shot prompting, applied to subgraphs.
- **What you do with it**: Write a PQL (predictive query) like "predict churn for these users in the next 30 days." It returns predictions zero-shot, no feature engineering. Snowflake-native, Databricks lakehouse app, BigQuery, Athena. Data never leaves the warehouse.
- **Why this matters for ontology**: It implies that *predictive ML* over an ontology is becoming a query, not a project. If your ontology has the FK structure and timestamps, KumoRFM can answer predictive questions over it directly. This collapses the "build a model" loop into the ontology layer.

KumoRFM 2.0 (2026) extended this to single-table tabular data. Jure Leskovec is the technical lead — Stanford GNN heritage.

### 4d. Vertical AI-native ontology adjacencies

Worth noting:
- **OpenAI Agents SDK, Anthropic's Agent SDK, Google ADK**: tool-use abstractions that assume agents call typed tools. Every ontology platform now ships SDKs into these.
- **Foundry's own Ontology SDK**: TypeScript/Python clients that expose object types as typed classes — the agent calls `Aircraft.search()` or `applyAction(AssignSortie, {...})`, not raw SQL. This is the model.
- **Anthropic structured outputs / OpenAI function calling**: the schema-constrained-generation primitive that makes typed ontology actions reliable.

## 5. Auto-construction vs. human-authored ontologies — the central tradeoff

The most useful frame for thinking about ontology auto-construction is this binary:

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
│                                        │   (PII, classified, embargoed)     │
│ • Simple CRUD actions                  │                                     │
│   (create, update, delete)             │ • Permissions / RBAC mapping        │
│                                        │   to business roles                 │
│ • Description text from data samples   │                                     │
│                                        │ • Inter-object workflows            │
│ • Naive entity resolution              │   (when does X trigger Y?)          │
│   (exact/edit-distance match)          │                                     │
│                                        │ • The metric definitions that       │
│ • Cardinality estimates                │   carry organizational meaning      │
│   (one-to-many vs many-to-many)        │   ("active customer", "MRR")        │
│                                        │                                     │
│ • Predicted relationships              │ • Cross-system identity resolution  │
│   (link prediction from data patterns) │   (which Acme Corp record is the    │
│                                        │   same Acme Corp across CRMs?)      │
└────────────────────────────────────────┴─────────────────────────────────────┘
```

The deeper insight: the left column is *structural*, and the right column is *intentional*. Auto-inference can recover everything that is *expressed* in the data; it cannot recover anything that is *not* in the data — and the most valuable parts of an ontology (the things you can run a business on) are precisely the things that *aren't* in the data because they live in people's heads, in process docs, in regulatory requirements, and in the *purpose* of the system.

### State of the art in auto-inference (2024–2026)

Recent academic and applied work demonstrates roughly what's possible today:

- **RIGOR (Jun 2025)** — Retrieval-augmented Iterative Generation of RDB Ontologies. Combines DB schema + documentation + domain-ontology repositories + a growing core ontology, prompts an LLM for provenance-tagged delta fragments, refines via a judge-LLM. Walks FK constraints table-by-table. Produces OWL ontologies that score competitively on accuracy/completeness/consistency. The state of the art for relational-to-OWL today.

- **OntoKGen (Nov 2024)** — Interactive ontology+KG generation with chain-of-thought; targets reliability/maintainability domain. Emphasizes that *there is no universally correct ontology* — final ontology depends on user preferences. Always human-in-the-loop.

- **GalaxyWeaver (VLDB 2025)** — Autonomous table-to-graph schema generation; LLM-driven prompt-guided analysis; query-aware schema optimization (the graph schema is optimized for the queries you want to ask, not just produced from FKs).

- **Schema-Miner pro** — Three-stage LLM-driven schema discovery with ontology grounding (against e.g. QUDT). Agentic grounding via lexical heuristics + semantic similarity. Open source.

- **OLLM (Oct 2024)** — End-to-end ontology learning with fine-tuned LLM modeling whole subgraphs at once (not just individual relations). Custom regulariser to avoid overfitting on high-frequency concepts. Transferable to new domains.

- **Multi-factor relationship discovery for implicit FKs (arXiv 2602.00029)** — For relational databases where FKs are *missing*, infer them by combining column-name similarity, datatype compatibility, value-overlap on sampled rows, and cardinality analysis. Above a confidence threshold δ, declare an edge. The same techniques industrial vendors quietly use.

What's notable: every one of these is human-in-the-loop. The LLM proposes, the human disposes. *Nobody is shipping fully autonomous ontology construction* because the "intentional" half cannot be recovered without humans.

### The synthesis: deterministic-typed-core + LLM-fluid-periphery

This is the architectural pattern that the leading platforms are converging on:

```
                  ┌──────────────────────────────────────────────────┐
                  │   LLM-fluid periphery                            │
                  │   • Description text, synonyms, aliases          │
                  │   • Natural-language → typed-tool-call           │
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

The deterministic core is what you can audit, govern, version, and certify. The LLM periphery is what makes it *fast to build* and *easy to consume*. Foundry's Ontology + AIP follows this pattern: the Ontology Manager produces hard typed schemas and action types; AIP Analyst and Logic agents work fluidly *over* that typed substrate.

The Tenex-relevant claim: any commercially viable ontology product for the next 5 years has to be this shape. Pure-LLM "infer everything" platforms are too unreliable for operations; pure-deterministic platforms are too slow to build for mid-market customers.

## 6. How agents interact with ontologies

Agents over raw SQL is the wrong abstraction. Agents over typed ontology operations is the right one. The difference is enormous and not appreciated outside the Foundry/Glean/Alation crowd.

### Why typed ontology > raw SQL for agents

- **Reliability**: A text-to-SQL agent will hallucinate column names, mis-join tables, and invent semantics. A typed-tool agent picks from a constrained vocabulary defined by the ontology schema and validated against the type system.
- **Governance**: Every action goes through a defined action type with permissions, side-effects, and (in Foundry) writeback datasets. Raw SQL has no permission model beyond row/column ACLs.
- **Auditability**: The action log is a record of typed operations, not opaque queries. You can ask "who edited this Aircraft's status in the last 24h?" trivially.
- **Reversibility**: Action types can carry reversal semantics. SQL writes do not.
- **Composability**: Typed actions are programmatic functions; LLMs are now good at multi-step tool composition. Multi-step SQL composition is brittle.

### MCP as the universal agent-ontology protocol

Model Context Protocol (Anthropic, late 2024) is rapidly becoming the lingua franca for exposing ontology operations to any agent runtime:

- **Foundry**: Ontology MCP server (`aip mcp` / Logic) — agent reads object types, runs typed queries, applies action types.
- **dbt**: `dbt MCP server` exposes Semantic Layer metrics to agents.
- **Glean**: Hosted MCP servers integrated with OpenAI Agents SDK, LangGraph, Bedrock Agents, Google ADK.
- **Alation**: MCP support announced in Agent Builder (Oct 2025).
- **Atlan**: MCP server delivers governed context downstream.
- **Datris**: 30+ tools via native MCP server — first OSS data platform with MCP-as-primary-interface.
- **Cube**: MCP server (in Bonnard layer, not core Cube) for governed metrics.
- **Meko / Exabase / Corvic**: MCP-first by construction.

The strategically interesting question is: *what is the right MCP-exposed schema for an ontology platform?* You want enough primitives for an agent to do real work (search, create, update, link, aggregate, simulate, apply named action) without exposing so much surface that the agent's choices become unreliable. Foundry's split is instructive:

```
Discovery:  object_type_search, object_type_lookup, dataset_lookup
Retrieval:  object_set, object_lookup, search_around, semantic_search
Compute:    ontology_aggregation, function_execution
Mutation:   action_type_execution (with required approval)
```

Notice: mutation is *one* call, parameterized by a named action type that itself encodes the side-effects, the permission requirements, and the approval flow. That's the right shape.

### Agent SDKs and typed ontology clients

Foundry's Ontology SDK generates TypeScript/Python clients where each object type is a typed class. An agent (or a developer) writes:

```ts
const flights = await Flight.objects.where(f => f.status === 'delayed').take(20);
await applyAction(ReassignSortie, { sortie: s, newAircraft: a });
```

This is the *correct* abstraction for an agent to compose against. It's the gap between "tool use" and "raw text generation" — exactly what makes the next 5 years of agent reliability work.

## 7. The actual engineering challenges of ontology auto-construction

This section is the most useful for Tenex's product/engineering planning. The hard problems:

### 7a. Schema inference

Easy: derive object types from tables, properties from columns, types from columns. Already solved.

Medium: distinguish *entities* from *events* from *junction tables* from *audit logs* from *configuration*. Heuristics work most of the time; failures are subtle. (A table named `order_status_history` is event-shaped; `users` is entity-shaped; `user_role` is a junction. An LLM gets this right ~90% with table+column names + 10-row samples.)

Hard: handle *wide flat tables* that hide multiple entity types (e.g., a 200-column denormalized `transactions` table that actually contains Customer, Merchant, Product, Card, and Transaction). This is where most production data lives.

### 7b. Entity resolution / deduplication

Easy: exact match on primary keys.

Medium: probabilistic linkage on names + emails + addresses; well-studied (Fellegi-Sunter is 1969). Splink, Zingg, Senzing, and most CDPs do this well.

Hard: cross-system identity resolution where the same logical entity has multiple records across CRM, ERP, support tickets, and finance — with stale, conflicting, partially-overlapping data. This is *the* hardest unsolved problem in enterprise data; LLMs help but don't solve it.

Hardest: *temporal* entity resolution — is the "Acme Corp" of 2023 the same legal entity as the "Acme Holdings" of 2026 after a restructuring? Requires human knowledge.

### 7c. Link discovery

Explicit FKs: trivial.

Implicit FKs (no declared constraint, but values overlap): solvable via the multi-factor algorithm above (name similarity + datatype + overlap + cardinality + confidence threshold). Industrial pipelines do this routinely.

Cross-database link discovery: harder; requires both schemas plus value sampling plus type unification.

Cross-domain link discovery (semantic, not structural): the LLM-territory. "These two columns mean the same thing despite different names." This is where embedding-similarity + LLM-judge approaches help.

### 7d. Type unification across systems

The two Salesforce tenants don't have the same fields; the SAP and Salesforce "Account" are not the same shape; the warehouse `dim_customer` has a different lifecycle than the CRM `Account`. Auto-unifying these into a single object type requires either:

1. A canonical model (slow to author, expensive to maintain) — Cinchy and the old MDM vendors live here.
2. Schema mapping with human review (Foundry's pattern) — author once, propagate via lineage.
3. LLM-on-demand mapping (fast, brittle, hard to govern).

The frontier is (2) augmented with (3): LLM proposes the mapping, human accepts/edits, the result becomes deterministic.

### 7e. Schema drift

Real systems change: columns added, renamed, deprecated; downstream consumers break. The ontology has to track:

- *Source-system drift* (the upstream Postgres added a column).
- *Ontology drift* (we want to add a new property).
- *Drift propagation* (which datasets, dashboards, actions, agents are affected?).

This is solvable with active metadata / lineage tracking (Atlan, Alation, Foundry all do this). It's a heavy ongoing investment, not a one-shot feature.

### 7f. Propagating user corrections

When an analyst fixes a wrong link or renames a property, that correction has to:

1. Persist (not be overwritten on the next ingest).
2. Influence future auto-inference (the system should *learn* from corrections).
3. Be versioned (so we can audit *why* the ontology says what it says).

The "compounding ontology" — where corrections improve future inference — is the holy grail. Meko, Exabase, and Glean's personal graph all gesture at this; nobody has nailed it for structured business data yet.

### 7g. Versioning the ontology itself

Ontologies are code. They should be:

- Versioned (Git or equivalent).
- Reviewable (PR-like workflows for changes).
- Reversible (roll back a bad action-type change).
- Branchable (test a new object type in a sandbox before promoting).

Foundry has this; Alation/Atlan are building toward it; the AI-native startups mostly don't yet.

## 8. Tenex translation

This is where the abstract becomes concrete for the OpenFoundry thesis and the beachhead decision.

### 8a. If Tenex built a self-learning data/ontology platform, what would it do?

The minimum viable shape, derived from the analysis above:

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
│      types; SDK generation for typescript/python; tool-use schemas that      │
│      drop into OpenAI/Anthropic/Google agent SDKs.                          │
│                                                                              │
│   6. WORKFLOW EXECUTION — actions triggered, audited, reversible. This       │
│      is the moat: ontology + actions + agents in one place.                  │
│                                                                              │
│   7. FEEDBACK LOOP — every analyst correction, every approved agent          │
│      action, every metric refinement feeds back to improve auto-inference.   │
│      The ontology *compounds*.                                               │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

### 8b. Is it sellable as a standalone product or must it be bundled?

**Sellable standalone**: very hard. The market signal is clear:
- The standalone semantic-layer market (dbt, Cube) is commoditizing fast.
- The standalone catalog market is consolidating into AI-native platforms (Alation+Numbers Station, Atlan, Collibra).
- Pure "AI memory for agents" startups (Meko, Exabase) are infrastructure plays, not enterprise products.

**Must be bundled with workflow + agent execution**: yes. The moat is *operating on the ontology*, not just *modeling it*. Palantir's pricing power comes from operations, not modeling. Glean's traction comes from grounded answers, not just the knowledge graph.

The Tenex bet should be: **ontology + agents + workflows, sold as an operating system for mid-market F500 functions** (procurement ops, supply chain, claims, finance close, customer ops). Not "we sell you a semantic layer." More like "we sell you a working agent-driven supply-chain operations center, and an ontology is how we get there."

### 8c. Real threats vs. noise

**Real threats**:

1. **Alation + Numbers Station + Agent Builder** — directly competitive; metadata foundation + AI agents on structured data + MCP. They have a 12-18 month head start on AI-native posture and 7+ years on metadata coverage. The single most-aligned competitor.
2. **Atlan's Enterprise Data Graph** — AI-native context pipeline, aggressive pricing, modern UX. Particularly threatening at mid-market.
3. **Glean** — owns the unstructured-data play; will move into structured data via partnerships (already integrates with Snowflake, dbt). Strongest brand for "system of context."
4. **Foundry itself moving down-market** — Palantir's AIP is being positioned for mid-market. Hardest to compete with on capability; easiest to compete with on price and accessibility.
5. **Microsoft Fabric semantic models + Copilot** — distribution moat. Most F500 customers already pay Microsoft; semantic models + Copilot is the path of least resistance.
6. **Kumo as adjacent disruption** — by collapsing the ML pipeline into the ontology, Kumo changes what "ontology" means. If Kumo wins, ontologies become predictive substrates by default.

**Noise** (interesting tech, not threats to a beachhead):

- Datris (good for AI-augmented ETL; not an ontology platform)
- Corvic (intelligence composition; pre-commercial)
- Meko / Exabase (agent memory infra; different layer)
- Cinchy (right idea, slow traction, older positioning)
- Vendia (federation tool, integration not competition)

### 8d. The strategically critical insight

The "ontology" market is being *redefined in real-time*. In 2023 it meant Palantir's Foundry Ontology and a few semantic-web nerds. In 2025 it means *the typed substrate that grounds enterprise AI agents on structured data*. By 2027 it will be the assumed plumbing of every enterprise AI deployment.

The window is short and Alation/Atlan/Glean/Foundry are all racing to own it. Tenex's advantage is *not* technology (these are well-understood patterns) but **services-led implementation**: getting an ontology + agents + workflows live in 60-90 days for an F500 function, where Foundry takes 9-18 months and Alation+Numbers Station is still maturing.

The Tenex play is *not* "we built a better ontology platform than Palantir." It's: **"we deliver a working ontology-grounded agent operations center for your function, faster than anyone else, using open-source primitives so you don't get locked in."** OpenFoundry-as-services-first, with the platform crystallizing out of repeated implementations.

The minimum viable beachhead is probably **one function in one industry** — e.g., supply-chain ops in industrials, or claims ops in P&C insurance, or revenue ops in B2B SaaS — where Tenex can deliver an ontology + agent stack tied to specific outcome metrics (cycle time reduction, leakage reduction, exception rate reduction). Once that pattern repeats 5–10 times, the platform writes itself.

---

# Sources

## Primary papers

- Gruber, T. R. (1993). "A Translation Approach to Portable Ontology Specifications." *Knowledge Acquisition* 5(2):199-220. https://tomgruber.org/writing/ontolingua-kaj-1993.pdf
- Gruber, T. R. (1995). "Toward Principles for the Design of Ontologies Used for Knowledge Sharing." *International Journal of Human-Computer Studies* 43(5-6):907-928.
- Gruber, T. R. (2009). "Ontology." In *Encyclopedia of Database Systems.* http://tomgruber.org/writing/ontology-definition-2007.htm
- Studer, R., Benjamins, V. R., & Fensel, D. (1998). "Knowledge Engineering: Principles and Methods." *Data & Knowledge Engineering* 25(1-2):161-197.

## W3C specifications

- RDF 1.1: https://www.w3.org/TR/rdf11-concepts/
- RDF Schema 1.1: https://www.w3.org/TR/rdf-schema/
- OWL 2 Web Ontology Language: https://www.w3.org/TR/owl2-overview/
- SPARQL 1.1: https://www.w3.org/TR/sparql11-query/
- SHACL: https://www.w3.org/TR/shacl/
- Semantic Web Stack overview: https://en.wikipedia.org/wiki/Semantic_Web_Stack

## Schema.org and Google KG

- Guha, R. V., Brickley, D., & Macbeth, S. (2016). "Schema.org: Evolution of Structured Data on the Web." *ACM Queue.* https://queue.acm.org/detail.cfm?id=2857276
- "Four years of Schema.org — Recent Progress and Looking Forward" — Google Research blog. https://research.google/blog/four-years-of-schemaorg-recent-progress-and-looking-forward
- Schema.org Wikipedia: https://en.wikipedia.org/wiki/Schema.org

## Palantir Foundry Ontology

- Foundry Ontology Core Concepts: https://palantir.com/docs/foundry/ontology/core-concepts/
- Foundry Object & Link Types reference: https://www.palantir.com/docs/foundry/object-link-types/type-reference
- Foundry Object Edits and Materializations: https://www.palantir.com/docs/foundry/object-edits/overview
- AIP Analyst Overview: https://www.palantir.com/docs/foundry/aip-analyst/overview

## Semantic-layer vendors

- dbt Semantic Layer docs: https://docs.getdbt.com/docs/use-dbt-semantic-layer/dbt-sl
- dbt Labs product page: https://www.getdbt.com/product/semantic-layer
- Cube.dev: "Universal Semantic Layer: Capabilities, Integrations, and Enterprise Benefits" (Dec 2024): https://cube.dev/blog/universal-semantic-layer-capabilities-integrations-and-enterprise-benefits
- "Semantic Layer Tools 2026: dbt Semantic Layer vs Cube vs MetricFlow vs Lightdash" — StackFYI (May 2026)
- Microsoft Fabric — Power BI Semantic Models: https://learn.microsoft.com/en-us/fabric/data-warehouse/manage-semantic-model
- Microsoft Fabric — Manage a Power BI Semantic Model: https://learn.microsoft.com/en-us/power-bi/connect-data/semantic-models-third-party
- "Microsoft Fabric to lose auto-generated semantic models" (Jul 2025)

## Data catalogs / Alation + Numbers Station

- "Alation Acquires Numbers Station to Unlock a New Era of Agentic Workflows" — globenewswire (May 20, 2025)
- TechCrunch: "Alation acquires Numbers Station to bolster its AI agent offerings" (May 20, 2025)
- TechTarget: "Alation boosts agentic AI with Numbers Station acquisition" (May 20, 2025)
- "Alation launches Agent Builder to bring enterprise-grade AI agents to structured data" — SiliconANGLE (Oct 1, 2025)
- "Alation unveils agentic AI-powered query capabilities" — TechTarget (Aug 19, 2025)
- Atlan vs Collibra (2026): https://www.modern-datatools.com/compare/atlan-vs-collibra
- Atlan comparison page: https://atlan.com/alation-vs-collibra-vs-openmetadata-vs-atlan

## Glean

- Glean Knowledge Graph docs: https://docs.glean.com/security/knowledge-graph
- Glean Knowledge Graph guide: https://www.glean.com/resources/guides/glean-knowledge-graph
- Glean System of Context: https://www.glean.com/product/system-of-context
- Arvind Jain on AI search and grounding: https://glean.com/blog/search-launch-announcement

## AI-native ontology startups

- Datris.ai: https://datris.ai/ and Open Source For You writeup (April 2026)
- Corvic AI Intelligence Composition Platform: https://www.corvic.ai/
- Meko / Yugabyte launch (May 2026): https://www.yugabyte.com/blog/meko-data-infrastructure-for-agents-that-work-and-learn-together/
- Exabase: https://exabase.io/
- Cinchy "From data fabric to data collaboration": https://cinchy.com/resources/from-data-fabric-to-data-collaboration/

## Foundation models for relational data

- Kumo.ai platform overview: https://kumo.ai/platform
- "Introducing KumoRFM: A Foundation Model for In-Context Learning on Relational Data" (May 2025): https://kumo.ai/company/news/kumo-relational-foundation-model
- "Understanding KumoRFM": https://kumo.ai/research/kumo-rfm-guide/
- Kumo GitHub: https://github.com/kumo-ai/kumo-rfm

## Industrial DataOps / Cognite

- IDC MarketScape Worldwide Industrial DataOps Platforms 2026 Vendor Assessment (March 2026): https://my.idc.com/getdoc.jsp?containerId=US53013025
- Cognite IDC press release (March 19, 2026)

## Auto-construction research

- Toro Bermúdez et al. (Jun 2025), "RIGOR: Retrieval-augmented Iterative Generation of RDB Ontologies" — arXiv 2506.01232
- "Leveraging LLM for Automated Ontology Extraction and Knowledge Graph Generation" (OntoKGen) — arXiv 2412.00608 (Nov 2024)
- "GalaxyWeaver: Autonomous Table-to-Graph Conversion and Schema Optimization with Large Language Models" — VLDB 2025 (Vol 18, No 12)
- Multi-factor implicit-FK discovery — arXiv 2602.00029
- "OLLM: End-to-end Ontology Learning with LLMs" — arXiv 2410.23584 (Oct 2024)
- Schema-Miner pro repo: https://github.com/sciknoworg/schema-miner

## Conceptual references

- "Ontology vs Taxonomy vs Data Model" — Dan Selman / Docusign (2024): https://www.docusign.com/blog/developers/ontology-vs-taxonomy-vs-data-model
- Kurt Cagle, "Ontologies and Knowledge Graphs" (Jan 2025): https://www.linkedin.com/pulse/ontologies-knowledge-graphs-kurt-cagle-j83dc
- Enterprise Knowledge — "Ontologies vs Knowledge Graphs" (2020 PDF)
- Synaptica — Terminology & Standards: https://synaptica.com/terminology/
- BigBear.ai — "Taxonomies, Ontologies, Semantic Models & Knowledge Graphs": https://bigbear.ai/blog/taxonomies-ontologies-semantic-models-knowledge-graphs/
- Bob DuCharme, "You probably don't need OWL" (2021): https://www.bobdc.com/blog/dontneedowl/
