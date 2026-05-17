# Foundry Architecture: One Level Deeper

**Date:** 2026-05-17
**Companion to:** `20260517-palantir-foundry-analysis.md` (do not re-read; this builds on it)
**Audience:** Tenex leadership exploring an "OpenFoundry" productization path
**Question:** What is genuinely load-bearing in Foundry's engineering substrate, what is surface area, and what is the irreducible "spine" Tenex could ship?

---

## Summary

Foundry looks like a sprawl of 30+ applications, but architecturally it is a small number of **load-bearing primitives** wrapped in a lot of **surface-area apps** that are increasingly being subsumed by AIP and the OSDK. The load-bearing core is, in order of how hard it is to replicate:

1. **The Ontology backend (Object Storage V2 + Funnel)** — the indexed object database with lineage-aware permissions, mandatory control properties, and Action-driven writeback. This is the part nobody outside Palantir has built.
2. **Action types + Functions + OSDK as a unified runtime** — the tri-layer that makes the Ontology *callable* and *mutable* with typed, governed semantics from code, no-code, and agents simultaneously.
3. **Global Branching across data, ontology, code, and UI** — Git-like environments for the *whole platform state*, not just code. This is the customer-trust feature; it's what lets FDEs work on a customer's live ontology without breaking production.
4. **Apollo** — the only system that lets you deliver platform updates to air-gapped IL-5/IL-6 customers continuously. Largely irrelevant to a 2026 SaaS-native rebuild.
5. **Surface area (Workshop, Slate, Quiver, Contour, Vertex, Pipeline Builder)** — replaceable. Workshop is the only one still net-new value; the rest are increasingly displaced by AIP, OSDK-React apps, and external BI tools.

For Tenex's purposes, the spine collapses to: **a typed ontology backend with row/cell-level permissions, an action runtime with writeback, an auto-generated typed SDK, and a branching model that covers both data and ontology**. That is roughly six months of focused engineering, but only if you accept that 80% of Foundry's product surface area is *not* what makes Foundry valuable.

---

## 1. The Engineering Primitives That Constitute the Spine

### 1.1 Object Storage V2 (OSv2) + Object Data Funnel

This is the most underrated piece of Foundry. Everyone talks about "the Ontology" as if it's a schema; in practice the Ontology is **a specific database (OSv2) and a specific orchestrator (Funnel) wearing a semantic layer hat.**

**What it is.** OSv2 is a purpose-built indexed object database. It separates indexing from querying (V1 conflated them), supports row-level and cell-level security policies decoupled from the underlying dataset permissions, and stores user edits (Actions) in the same store as ingested data, with explicit conflict-resolution strategies (apply user edit / apply most recent value).

**The Funnel** is the microservice that reads from datasets, restricted views, streams, and Actions, and indexes everything into OSv2. It is the *write path* for the entire Ontology. When a transform updates a backing dataset, Funnel re-indexes; when an Action submits an edit, Funnel applies it transactionally. This is the single biggest reason the Ontology can be both a derived view of a data lake and a system-of-record for operator edits.

**Why it exists.** A data warehouse can't do this because warehouse rows are not addressable as mutable, typed entities with side effects. A graph DB can't do this because graph DBs don't natively understand "this row in this dataset is the source-of-record for this object". Foundry needed *both* analytical scale (read paths against billions of rows) and operational writes (transactional edits on individual primary keys) with consistent permission enforcement.

**What replication costs.** This is the longest pole. You need:
- A row-store with secondary indices that survives schema drift from upstream datasets
- A change-data-capture-style ingest from your raw store (Iceberg/Delta/Parquet) into the object index
- A writeback path that doesn't corrupt the source-of-truth dataset
- Row-level and cell-level policy evaluation at query time, with policies expressed against object properties (not just user attributes)
- Mandatory-control properties: properties whose *values* (markings, classifications) are themselves access predicates

The closest open-source analog stack is: **Iceberg/Delta** for the lake, **DuckDB or ClickHouse** as the indexed query layer, **OPA or Cedar** for policy evaluation, and a custom write-path for Actions. Nobody has stitched these together into a single coherent product, which is exactly Tenex's opportunity.

### 1.2 Action Types

An Action type is a **typed schema for a transactional mutation that may have side effects**. It is not a function and it is not a stored procedure; it is a contract.

The contract specifies:
- **Parameters** with types, constraints (multiple-choice, ranges), and default values (including environment values like `currentUser`, `currentTime`)
- **Rules** that transform parameters into ontology edits: add object, modify object, create-or-modify, delete object, create link, delete link, *function rule* (delegate to a Foundry Function)
- **Submission criteria** — server-side preconditions that must hold for the action to apply (e.g., "ticket status is Open")
- **Side effects** — webhooks (pre- or post-edit) and notifications (push, email, in-platform)
- **Security** — who can submit; layered on top of OSv2 policies on the affected objects

Crucially, Actions are also the *only sanctioned write path* to the Ontology. Even AIP Logic, which has a separate `Apply Action` block, must invoke an action to actually persist edits; the LLM doesn't get a raw write. This is the load-bearing security invariant: **all writes are typed, audited, validated, and permission-checked Actions**.

**Why it matters for Tenex.** This is the abstraction that makes "agent RBAC" actually possible. An LLM agent doesn't have permissions over rows; it has permissions to invoke Actions. The action carries the user's permission posture into the mutation, which is checked against object/property security policies and mandatory controls. Any agent platform that wants to be safe at enterprise scale needs an analogue.

### 1.3 Functions ("FOO" — Functions on Objects)

Functions are **typed, sandboxed code (TypeScript v1/v2, Python, Java, or AIP Logic) that takes Ontology objects/object sets as inputs and optionally returns objects or emits OntologyEdits**. They are the "logic" leg of the data/logic/action triangle.

Key architectural points from the docs:

- TypeScript v2 runs in serverless Node.js with full `fs`, `child_process`, `crypto` access — i.e., it is a real runtime, not a Lambda-style sandboxed eval.
- Functions can be **invoked synchronously by Workshop, Slate, OSDK clients, and Action rules**, and **asynchronously by automations or AIP Logic**.
- The Python/TS v2 SDKs include `OntologyEditFunctions` — a typed editing API that compiles down to Actions at submission time. You don't write SQL; you write `client.actions.create_ticket.execute(...)` and the runtime resolves it.
- Functions cannot return certain primitive types directly (`User`, `Principal`, `OntologyEdit`, `ClassificationMarking`) — these are reserved for action rules, which keeps the security model clean.

Functions are the bridge from "data exists in the ontology" to "the ontology has *behavior*." Combined with Action types, they are how Foundry encodes business logic without dropping into raw Spark or SQL.

### 1.4 OSDK (Ontology SDK)

The OSDK is **auto-generated typed client code, in TS/Python/Java, that mirrors a specific customer's Ontology**. It is published as a versioned npm/pip package from Developer Console.

A representative TS snippet from the docs:

```ts
import { Country } from "@serverside-osdk-example/sdk";
import { client } from "./client";
const resp = await client(Country).fetchPage();
```

Three things are happening here that are easy to miss:

1. **`Country` is a generated TypeScript class**, not a string. Property names, types, action signatures, and search filters are all type-checked at compile time.
2. **`client(Country)` is a type-aware fluent builder**. `.where(Country.capacity.gt(100))`, `.aggregate(...)`, `.applyAction(...)` are all generated.
3. **Auth is bifurcated**: `createPublicOauthClient` (end-user auth, browser) vs `createConfidentialOauthClient` (service-user auth, server). The OSDK enforces that the *runtime user* is the permission scope — there is no platform service account that elevates the agent's powers.

The OSDK is the **outbound API of the Ontology**, and it is what makes Foundry useful even when you're not in Foundry's own UI. Workshop apps, Slate apps, AIP agents, external Next.js apps, mobile apps — all of them route through the same generated SDK, with the same security model.

**Critical for Tenex:** any productized agent platform must offer an equivalent. The "auto-generated typed client" pattern is now standard (Hasura, Supabase, PostgREST, etc.) but none of them generate Action types, function calls, search filters, and OSv2-style aggregations as a coherent client. This is achievable in 2-3 months of TS tooling work *if* the underlying ontology schema is well-typed.

### 1.5 Foundry Branching / Global Branching

Branching in Foundry is **not just code branching**. It is a unified branching model across:

- Data pipelines (Pipeline Builder + Code Repositories transforms)
- The Ontology itself (object types, link types, action types, properties)
- Workshop modules (the UI)
- Actions (you can run actions on a branch without writing back to main)

The Apply Action endpoint accepts a `branch` query parameter — you can run a mutation against a branched copy of the ontology, see how it propagates, and merge only if it works. Protected branches require approval proposals; enrollment-level admin settings can force this on all new pipelines.

The docs are explicit that this is a **trunk-based development** model: short-lived branches, fast merges, monorepo discipline. This is how FDEs work safely in a live customer instance: they branch the entire ontology + pipelines + Workshop modules, build their use case end-to-end, and merge.

**Why this is load-bearing.** Without it, FDE work is destructive. With it, FDEs can develop on real data, in a real production-shaped instance, without an enterprise saying "you need a separate dev environment." This collapses the typical enterprise dev/staging/prod three-environment dance into a branch-and-merge dance — closer to how software engineers actually work in 2026.

**Replication cost.** High. You need versioned schemas (think Liquibase-meets-Iceberg-time-travel), branched data lineage (which is its own graph problem), and a UI that surfaces conflicts across all four surfaces. Tenex could ship a v1 with branching only on the ontology + Workshop equivalent, and treat data pipelines as upstream (unbranched) — this is the right compromise.

### 1.6 Compute Modules

Compute Modules are **serverless Docker containers as a first-class Foundry primitive**. They replaced an earlier pattern where you had to wrap arbitrary code in a Foundry Function. Now you publish a Docker image to an Artifact repository inside Foundry, and Foundry runs it as a horizontally scaling stateless service.

Architectural specifics worth knowing:

- Containers run as **non-root numeric users**, **linux/amd64**, no `latest` tag (digest or pinned tag required), zero-trust network model (no egress by default; "Sources" must be explicitly granted)
- Each compute module is **N replicas**, each with one or more containers (the entry container polls Foundry's API for jobs; sidecars can do whatever)
- Two execution modes: **function-backed** (callable from Workshop/Slate/Actions like a Function) and **pipeline-backed** (sits between input/output datasets in a streaming or batch pipeline)
- A separate **Functions CLI** infers function specs from your source code and publishes the image with the right metadata labels; supports a GoCR engine for CI/CD environments without a Docker daemon
- "Sources" are how compute modules access the outside world. A Source is a network policy + credentials bundle (REST API, S3, Postgres, etc.). The compute module reads credentials from a JSON file mounted at `$SOURCE_CREDENTIALS`. There is no implicit network access.

This is Foundry's answer to "what if the Ontology isn't enough and I need raw code with arbitrary libraries?" It is also their answer to "what if my data scientist wants to ship a model?" Models in Foundry are increasingly just compute modules with a typed API and an Ontology binding via Functions.

**For Tenex:** this is also a Kubernetes-on-rails pattern. Replicate this with Knative or a managed Cloud Run / Fargate front-end + an "Artifact repository" that is just a private container registry. Six weeks of work for a v1.

### 1.7 Pipeline Builder vs Code Repositories

This is one of Foundry's smartest product decisions. **Both are first-class, and they interoperate at the dataset boundary.**

- **Pipeline Builder** is a graph + form environment with strongly-typed transforms, real-time data preview at every node, and branch-and-propose workflows. The output of every node is a real Foundry dataset; you can break out of Pipeline Builder anywhere by hitting a "Switch to code" or by reading the output dataset from a Code Repository.
- **Code Repositories** is a Git-backed IDE for full transforms (Python/SQL/Java/Mesa). It is used for: filesystem/API access, custom libraries, specialized streaming, anything Pipeline Builder can't express.

The interoperation is the key: a Pipeline Builder pipeline can consume the output of a Code Repository transform and vice versa. **There is no "low-code lock-in"** — that is what makes Pipeline Builder safe to use for production.

**The pattern Tenex should steal:** every "low-code" surface area must produce *normal artifacts that can be consumed by code paths*. The moment you have a low-code object that only exists inside the low-code tool, you've built a trap. Foundry's discipline here is the discipline.

### 1.8 Workshop Builder Runtime

Workshop is the no-code app builder for Ontology-driven operator apps. It is the single most-used part of Foundry by non-engineers, and it is the only piece of the "surface area" tier that is still net-new value in 2026.

Architectural model:

- **Modules** are the unit. A module is a tree of **sections** (layouts) containing **widgets**. Widgets are typed against Ontology object sets, properties, actions, and functions.
- **Variables** are the runtime state. Variables have base types (String, Object, ObjectSet, Boolean, Number, ...), default values, transformations (a variable can be backed by a function call), and recalculation behaviors. They are the "redux store" of the app.
- **Module Interface** — variables can be marked as part of the module's *interface*, making them mappable from parent modules when the module is embedded, or initializable from URL query parameters. This is how Workshop modules become composable.
- **Embedded Modules** — Workshop modules can embed other Workshop modules. Variable mapping at the boundary lets parent and child share state. This is how big Workshop apps stay maintainable.
- **Events** — declarative event bindings. Buttons emit events; events update variables, run actions, navigate, open overlays.
- **Custom Widgets** — when you need raw React, you build a custom widget via the OSDK's `@osdk/widget.client` package and publish it as a versioned artifact. The widget gets typed parameter/event definitions and accesses the Ontology via the OSDK.

The runtime is **declarative**: a Workshop module is a JSON-shaped config tree, not generated code. Foundry renders it. This is why "Build with AIP" can generate Workshop modules — they're just config blobs.

**For Tenex:** this is the part where Workshop genuinely beats a 2026 codebase. A 2026 equivalent should be **agent-authored config**, not human-clicked config. Same declarative substrate, different authoring surface.

### 1.9 Slate, Quiver, Contour, Vertex

Looking at the 2024-2025 release notes, these are **maintenance-mode products** with steadily diminishing investment. Specifically:

- **Slate** — HTML/CSS/JS app framework. Lower-level than Workshop. Still used in legacy deployments, but new builds are pushed to Workshop + custom widgets + OSDK-React. Not load-bearing.
- **Quiver** — chart-based exploration, multi-dimensional, streaming. Real-time investigative analytics tool. Still actively developed (2024 release notes show Vega plot additions), but the "AIP Analyst" agent has eaten most of its workflow.
- **Contour** — point-and-click Tableau-ish analytics. Heavily deprecated; new ML workflows go to AIP Bootcamp / AIP Logic.
- **Vertex** — graph/relational exploration. Niche; mostly used for investigative work in defense + finance.

None of these are load-bearing in 2026. They are surface area that increases switching cost by giving every customer a dozen tools to learn, but they don't shape the platform's value proposition.

### 1.10 AIP Logic Block Model

AIP Logic is a no-code function builder where each function is a chain of **blocks**:

- **Use LLM** — prompt + tools + output. Tools are Ontology-driven (Apply Actions, Call Function, Query Objects, Calculator). The LLM only *requests* tool calls; AIP executes them in the invoking user's permission scope. Cost: 4 compute-seconds for basic, 8 for tool-using executions.
- **Apply Action** — deterministic action call without an LLM. This is the *only way* edits get written back to the Ontology; even when an LLM "uses" an action as a tool, the action is invoked through the same Apply Action machinery.
- **Execute Function** — call a Foundry Function directly.
- **Loops, Conditionals, Create Variable** — control flow primitives.

**Crucial detail** from the docs: "*Calling an AIP Logic function from an action is required for edits to be written back to the Ontology. The Ontology will not be edited unless the Logic function is executed from an action, even if the function contains an Apply action block.*"

This is the same "all writes are Actions" invariant from §1.2, restated for the LLM case. Even when an agent "decides" to make a change, the actual change goes through a typed, audited Action submission.

**For Tenex:** the AIP Logic block model is the right abstraction layer for an agent platform's *no-code surface*. The atomic units are: LLM call with tools, deterministic tool call, control flow, variable. This is a near-perfect match for LangGraph nodes, but with first-class typed tool definitions backed by an ontology and an action schema. That's the differentiator.

### 1.11 Ontology MCP & Palantir MCP

These are Palantir's two MCP servers, and they serve different audiences:

- **Ontology MCP (OMCP)** — *external* AI agents can connect to a customer's Ontology and use object types/action types/queries as tools. App-scope restrictions limit which actions an agent can invoke. The "Agent tool description" field in Ontology Manager is *just for the agent* — separate from human-facing descriptions, so you can tell Claude "use this action when the user reports a defective product" while keeping the human label clean.
- **Palantir MCP** — 70+ tools for *Foundry developers* to build with Foundry from Claude Code / Cursor / etc. Read ontology, propose new object types, generate transforms, regenerate OSDK. All writes go through proposals requiring human approval.

The bifurcation is intentional: production data agents (OMCP) vs platform-building agents (Palantir MCP). Both run on the same MCP protocol, both enforce the same OSv2 security model, but they expose different surface areas to different actors.

**For Tenex:** this is the move. The MCP layer is the **public API** of an ontology platform in 2026. The actual platform UI is increasingly something an FDE uses; the day-to-day surface is an agent (Claude, Cursor, custom Tenex agent) talking MCP. A productized OpenFoundry should default to MCP-first.

### 1.12 Apollo

Apollo is the **continuous-delivery system for Palantir's own platform**. It is what lets Palantir deploy software updates to IL-5/IL-6 air-gapped environments, FedRAMP cloud, public cloud, and on-prem hybrid simultaneously, with thousands of zero-downtime upgrades a month.

Key architecture points from the docs:

- **Hub + Spoke**: a central Hub orchestrates; **Agents** running in each environment (the Spoke) execute Plans.
- **Plans**: discrete units of work (upgrade, config change). Issued by the Hub, executed by Agents only when *constraints* are satisfied (maintenance windows, health checks, dependency versions, suppression windows).
- **Release Channels**: Apollo uses a *pull* model — environments subscribe to channels (RELEASE, CANARY, STABLE), and developers define promotion criteria. Releases auto-promote when criteria pass.
- **Reported State**: agents continuously report version, config, liveness back to the Hub. The Hub never has a hard target state; it just keeps generating new Plans that move toward the latest valid release.
- **Rollback**: if a Plan fails and the environment state has changed, the Hub issues a rollback Plan automatically.

**Verdict:** Apollo is largely irrelevant to a 2026 SaaS-native rebuild. If your customers are all in your own multi-tenant cloud, you don't need it. It becomes load-bearing only when you sell to defense / IL-5 / on-prem regulated customers. For Tenex's F500 commercial focus, ignore.

### 1.13 Data Lineage as a First-Class System

Lineage in Foundry is **a queryable, simulatable, propagation-aware graph that operates over datasets, restricted views, object types, transforms, and Pipeline Builder pipelines simultaneously.**

What it does beyond a typical lineage tool:

- **Permission coloring** — view the graph "as" a specific user. See which nodes that user can read, can't read, or partially read. Drill into the upstream node that's blocking access.
- **Marking simulation** — apply or remove a marking on a node and preview which downstream datasets are affected, before committing. The graph color-codes "access affected" vs "access unaffected" vs "simulated changes applied."
- **`stop_propagating` / `stop_requiring`** — code-level directives that break marking inheritance. E.g., after dropping a PII column, the downstream transform can `stop_propagating` the PII marking. These directives are reviewed via protected-branch proposals.
- **Cross-application** — lineage spans Pipeline Builder, Code Repositories, Ontology, and Workshop modules. A Workshop builder can see which dataset ultimately feeds a chart.

This is the single most important piece of Foundry's governance story. **Compliance teams can prove, at audit time, that PII never reaches a derived dataset that's accessible to an unprivileged group, because the lineage graph + marking propagation enforces it deterministically.**

**Replication:** OpenLineage gives you the graph. Marking propagation is the hard part — it requires every transform engine (your dbt / Dagster / Spark layer) to emit marking metadata as a transform output, *and* the policy engine to consume it. Doable, not trivial. Estimate: 2-3 months for a v1 that covers SQL-only transforms.

---

## 2. The Day-0 to Day-365 Customer Journey

The Foundry rollout is more disciplined than it looks. Here's the actual shape, synthesized from Palantir's platform docs, the AIP Bootcamp model, and customer accounts.

### Phase 1 — Days 0-30: Data Integration

**Activities.** Data Connection sources stood up (REST APIs, S3, Postgres, SAP, on-prem agents). Batch syncs configured to land raw data as Foundry datasets. Initial ingest schedules. Network egress / agent installation in customer infra.

**Architecture in play.** Data Connection (three architectures: direct connection, agent-proxy, agent-worker). Foundry workers as isolated compute. Pipeline Builder for initial cleanup transforms.

**FDE work.** Heavy. The FDE writes connector configurations, gets network/firewall approvals, validates schema mappings. ~30-50% of total FDE hours in the engagement.

**Customer ownership at end of phase.** Almost nothing. The customer can see datasets in Foundry but can't do anything with them.

### Phase 2 — Days 30-90: Ontology Authoring

**Activities.** FDE-led discovery sessions with operational SMEs. What are the entities your business actually operates on? Not "tables in your warehouse" — *things you make decisions about* (orders, shipments, patients, aircraft, nurses). For each entity, what are the properties, links, mandatory controls, and verbs (actions) you act on them with?

The output is a first ontology: 30-100 object types, 100-300 property types, 50-100 link types, 30-80 action types.

**Architecture in play.** Ontology Manager. Object Storage V2 indexing the new types from the cleaned datasets. Action types authored with rules + submission criteria. Mandatory control properties wired to existing marking taxonomy.

**FDE work.** Decreases to ~30% of hours but shifts toward facilitation. The FDE is teaching the customer to think in objects/actions, not building everything themselves.

**Customer ownership at end of phase.** Customer team can author new object types and modify action types in Ontology Manager. Joint ownership of the schema.

### Phase 3 — Days 90-180: Operational Applications

**Activities.** Workshop modules built on the ontology. Slate apps for anything Workshop can't express. Custom widgets where needed. Functions for specialized logic (scheduling optimization, anomaly detection, eligibility rules). First production go-lives — usually a single workflow (e.g., "nurse shift swap approval" or "supply chain disruption response").

**Architecture in play.** Workshop runtime. OSDK published to Developer Console. Functions in TypeScript/Python. Compute Modules for ML model serving. Pipeline Builder for any ongoing transforms.

**FDE work.** ~20% of hours; mostly architectural review. The customer team is building most of the apps.

**Customer ownership at end of phase.** Customer ships their own Workshop modules. Customer can write Functions in TypeScript. FDE is a senior engineer reviewing PRs, not a builder.

### Phase 4 — Days 180-365: AIP & Expansion

**Activities.** AIP Bootcamp on a second use case (~75% conversion to expansion contract per Palantir disclosures). AIP Logic functions wired to existing actions. AIP Agent Studio (Chatbot Studio) for operator-facing assistants. Ontology MCP exposed to external Claude / Cursor for the customer's internal AI team. Expansion to new departments / new use cases.

**Architecture in play.** AIP Logic. AIP Agent Studio. Ontology MCP. Evals framework. AI FDE (Palantir's own agent that operates Foundry) increasingly takes over the "build a Workshop module that does X" work.

**FDE work.** ~10% of hours, advisory. The customer is the primary operator.

**Customer ownership.** Full. Customer is an independent operator of the platform, expanding without Palantir intervention. This is when the contract starts to compound.

### Handoff Summary

| Phase | What FDE keeps | What customer owns |
|---|---|---|
| 0-30 (Integration) | All | Visibility only |
| 30-90 (Ontology) | Architectural decisions, complex types | New object types, simple actions |
| 90-180 (Apps) | Reviews, custom widgets | Workshop apps, Functions, OSDK use |
| 180-365 (AIP) | Advisory only | Everything, including AIP Logic + agent authoring |

The economics work because **FDE hours per dollar of customer revenue decline asymptotically**. Year 1 is FDE-heavy and unprofitable; Years 2-5 are 80% gross margin expansion revenue with minimal FDE involvement. Top-20 customer ARR up ~50% YoY confirms the model empirically.

---

## 3. Load-Bearing vs Surface Area

Ranked by "what would a credible Foundry-alternative absolutely have to ship in v1":

### Tier 1 — Absolutely Load-Bearing

1. **Typed Ontology with object types, link types, properties (incl. mandatory control properties), action types, and link semantics.** This is the schema. Without it nothing else matters.
2. **An indexed object store (OSv2 equivalent) with row-level and cell-level policies decoupled from the underlying data lake.** This is where queries actually run. It must enforce policies that reference object properties (not just user attributes).
3. **An Action runtime that's the only sanctioned write path, with submission criteria, side effects (webhooks/notifications), and transactional semantics.** Without this, "agent RBAC" is impossible — agents need a typed, governed surface to mutate state.
4. **A typed, auto-generated SDK (TS/Python at minimum) that mirrors the customer's ontology and enforces user permissions at the call site.** This is the only way ontology-driven apps don't drift.
5. **A Function runtime (typed code that reads/writes the ontology via the SDK) callable from apps, actions, and agents.** This is the "business logic" leg.
6. **Lineage-aware permission propagation, with marking inheritance and simulation.** This is the compliance moat. Without it you can't sell to regulated industries.

### Tier 2 — Strongly Load-Bearing

7. **Branching across data + ontology + UI**, even if just on the ontology + Workshop-equivalent in v1.
8. **Connectors / Data Connection architecture** — multiple egress patterns (direct, agent-proxy) to handle SaaS APIs vs on-prem systems.
9. **A no-code app builder (Workshop equivalent)** producing config blobs that can be authored by either humans or LLMs.
10. **MCP server(s) exposing ontology to external agents with app-scope restrictions.**
11. **Serverless container runtime (Compute Modules equivalent)** for arbitrary code with zero-trust networking.

### Tier 3 — Nice-to-Have / Surface Area

12. Pipeline Builder (a no-code transform builder is replaceable by dbt / Coalesce / SQLMesh)
13. Slate, Quiver, Contour, Vertex (all replaceable by external tools or AIP equivalents)
14. AIP Logic block UI (the *blocks* matter; the UI is replaceable by LangGraph / Claude Skills / custom DSL)
15. AIP Bootcamp programs (a sales motion, not a product)
16. Apollo (only matters for on-prem / air-gapped customers)
17. Evals framework (good to have, but Braintrust/LangFuse/etc. exist)

The hypothesis in the original brief — that **ontology + actions + lineage-aware permissions are load-bearing; Quiver/Slate/Contour are surface area** — is correct, with the caveat that **the OSv2 backend itself is the deepest and most-underrated load-bearing piece**. Without that you have a schema spec, not a platform.

---

## 4. The Smallest Viable Spine for Tenex

If Tenex were to invest 6 months of focused engineering into "MiniFoundry v1," the irreducible spine looks like:

```
┌─────────────────────────────────────────────────────────────────────┐
│  MCP Server (default surface)                                       │
│  External agents talk MCP. Tools = action types + queries.          │
├─────────────────────────────────────────────────────────────────────┤
│  Typed OSDK (auto-generated TS + Python)                            │
│  Compile-time-safe access to ontology + actions + functions          │
├─────────────────────────────────────────────────────────────────────┤
│  Workshop-equivalent (declarative module spec, JSON config)         │
│  Agent-authored by default; human-editable. Renders generic React.  │
├─────────────────────────────────────────────────────────────────────┤
│  Function runtime (TS + Python, serverless, OSDK-aware)             │
│  + Compute Modules (Docker-on-Knative for everything else)          │
├─────────────────────────────────────────────────────────────────────┤
│  Action service (typed, validated, side-effect-aware, audited)      │
│  THE ONLY WRITE PATH                                                │
├─────────────────────────────────────────────────────────────────────┤
│  Object Store (indexed object DB w/ row+cell-level policies)        │
│  Built on DuckDB/ClickHouse + Iceberg + OPA/Cedar                   │
│  + lineage-aware marking propagation                                │
├─────────────────────────────────────────────────────────────────────┤
│  Data Connection (SaaS + on-prem agent + REST + warehouse)          │
│  Iceberg/Delta lake underneath, customer-owned where possible       │
└─────────────────────────────────────────────────────────────────────┘
```

**Estimated investment (6 months, ~6-8 engineers):**

| Component | Effort | Notes |
|---|---|---|
| Ontology schema service + Ontology Manager UI | 1 mo | CRUD over types/properties/links/actions |
| Object Store with row/cell policies | 2 mo | DuckDB + Iceberg + Cedar; the longest pole |
| Action service | 1 mo | Tightly coupled to Object Store |
| OSDK code generator (TS + Python) | 1 mo | OpenAPI-spec emit + codegen |
| Workshop-equivalent (declarative UI) | 1.5 mo | Config schema + renderer; agent-authorable |
| Function runtime + Compute Modules | 1 mo | Knative wrapper, OSDK auto-injection |
| Data Connection (3 connector types in v1) | 0.5 mo | Snowflake, S3/Iceberg, generic REST |
| MCP server | 0.5 mo | Wraps the OSDK; minor work |
| Branching (ontology + Workshop only) | 1 mo | Skip data branching for v1 |
| Lineage + marking propagation (SQL only) | 1 mo | OpenLineage + marking metadata |

This totals ~10.5 person-months, achievable in 6 calendar months with 2-3 engineers in parallel on the slowest paths (Object Store, Actions, OSDK codegen).

The strategic point: **Tenex doesn't need to ship Workshop's full widget library, doesn't need Pipeline Builder, doesn't need Slate/Quiver/Contour/Vertex, doesn't need Apollo, doesn't need Evals.** A six-month MVP that nails Ontology + Action + OSDK + Object Store with row-level security + a basic declarative UI + MCP is enough to demonstrate the thesis on a real F500 deployment.

---

## 5. The Foundry-Knowledge Curriculum for Tenex FDEs

If Tenex is going to build OpenFoundry, every FDE needs to absorb Foundry's abstractions so they don't reinvent them poorly. A 5-week curriculum:

**Week 1: The Ontology as data + logic + action + security.** Read the Ontology Architecture page. Build a toy 5-object-type ontology in a Foundry dev instance. Author at least one action type with a function rule. Read the OSv2 docs end-to-end.

**Week 2: Permissions deep dive.** Markings, classifications, organizations, mandatory control properties, object security policies, property security policies, lineage propagation, `stop_propagating`. Build a scenario where the same user can see one object's properties but not another's, because of mandatory controls.

**Week 3: The OSDK and Functions.** Generate an OSDK from your ontology. Build a Next.js app with both confidential (service-user) and public (end-user) auth. Write a TypeScript v2 Function that takes an object set, edits properties via an OntologyEditFunction, and returns a transformed result.

**Week 4: AIP Logic, Actions-as-tools, and MCP.** Build an AIP Logic function that uses an LLM to triage incidents and applies an action conditionally. Configure Ontology MCP to expose your actions as tools to Claude Code. Build a Claude Skill that uses your MCP tools.

**Week 5: Workshop, Branching, and the FDE workflow.** Build a Workshop module with embedded sub-modules. Use Global Branching to make breaking changes to your ontology + Workshop without disrupting "production." Submit a proposal, review it, merge it.

**Mistakes to avoid (documented patterns):**

- Don't model business logic inside Pipeline Builder transforms when it should be an Action. Pipelines are for shape; Actions are for behavior.
- Don't use Foundry markings as a substitute for object security policies — markings are *mandatory*, hard to remove, and propagate everywhere. Use them only for genuinely sensitive data classes.
- Don't bypass the OSDK from internal code by calling raw HTTP. The OSDK enforces the user's permissions; raw HTTP is easy to mis-permission.
- Don't author Actions with too-broad submission criteria. Submission criteria are your last server-side guard rail.
- Don't store secrets in Compute Module Dockerfiles. Use Sources.
- Don't build long-lived branches. Trunk-based development is enforced for a reason.

---

## 6. Tenex Translation: Recommendations for Productization

Mapping each finding to a recommendation:

### Recommendation 1: Build the spine, not the surface
The temptation will be to ship a Workshop-equivalent or a Pipeline Builder first because those are visible. Resist. **Build the ontology + action + object-store spine first.** Everything else is replaceable by existing tools; the spine is not.

### Recommendation 2: MCP-first, not UI-first
In 2026, the *default* surface for an ontology platform should be MCP, not a web app. Customers' agents (Claude, Cursor, custom Tenex agents) talk MCP. The web app is for FDEs and Foundry-equivalent ontology authors, not for end users. This inverts Palantir's order of operations and is the right bet for 2026.

### Recommendation 3: Agent-authored Workshop equivalent
The Workshop runtime is declarative config. The 2026 differentiator is *who authors the config*. Build a Workshop equivalent where the default authoring path is an agent (Claude / Tenex's internal model), not a human. The human surface is "review and approve config diff," not "drag widget onto canvas."

### Recommendation 4: Lineage + marking propagation are the regulated-customer moat
Tenex's F500 commercial customer base will eventually want to deploy in regulated industries (healthcare, financial services). Without lineage-aware permissions, those deals are off the table. **Build the lineage graph and marking propagation in v1, even if it only handles SQL transforms initially.** This is the longest-tail moat.

### Recommendation 5: Ride OSDK / MCP / Iceberg open standards
Don't build a proprietary object store; build on Iceberg + DuckDB/ClickHouse. Don't build a proprietary client protocol; emit OpenAPI and generate clients. Don't build a proprietary agent protocol; speak MCP. **The "OpenFoundry" thesis only works if Tenex is genuinely agnostic at the storage / model / client layers.** Palantir's lock-in is at the ontology + action runtime layer; that's where Tenex can match them. Below and above that layer, be open.

### Recommendation 6: FDE training is a 5-week curriculum
Every FDE should complete the curriculum in §5 before being deployed to a customer. The abstractions are the moat. Engineers who don't understand the difference between an Action and a Function, or markings vs property security policies, will build customer deployments that don't generalize, which is exactly the failure mode that turns a platform play into a consultancy.

### Recommendation 7: The 6-month MVP is a real bet
The §4 plan is a credible 6-month bet for 6-8 engineers. Tenex's $80/storypoint engineer cost ≈ ~$120-150K all-in per engineer per 6 months at ~50% utilization on this; total ~$1M of engineering investment. That is small relative to $15M ARR. The question is whether to fund it from the services P&L (slows down current growth) or take outside capital (dilutes). Either is defensible, but the engineering plan itself is not the gating risk; the GTM is.

### Recommendation 8: Don't try to be Apollo
Skip on-prem and air-gapped deployments in v1. If a customer demands them, decline politely or charge enough to fund the entire delivery. Apollo took Palantir 15 years; trying to replicate it would burn 18 months and produce nothing differentiated.

---

## Sources

Palantir docs (primary):

- Object Storage architecture: https://palantir.com/docs/foundry/object-backend/overview/
- Ontology MCP: https://www.palantir.com/docs/foundry/ontology-mcp and /ontology-mcp/mcp-tools-and-agent-configuration/
- Palantir MCP: https://www.palantir.com/docs/foundry/palantir-mcp/security and /palantir-mcp/example-mcp-workflows/
- Compute Modules: https://www.palantir.com/docs/foundry/compute-modules (and /containers/, /functions/, /sources, /get-started)
- Pipeline Builder vs Code Repositories: https://www.palantir.com/docs/foundry/building-pipelines/considerations-pb-cr
- Pipeline Builder branch protection / propose-a-change: https://www.palantir.com/docs/foundry/pipeline-builder/branches-protected-branches and /branches-propose-a-change
- Global Branching: https://www.palantir.com/docs/foundry/foundry-branching/overview and /best-practices-and-technical-details
- Action types — rules, side effects, getting started: https://www.palantir.com/docs/foundry/action-types/rules and /side-effects-overview/ and /getting-started
- Apply Action API: https://palantir.com/docs/foundry/api/ontologies-v2-resources/actions/apply-action/
- Functions language support: https://www.palantir.com/docs/foundry/functions/language-feature-support
- Functions on Objects: https://palantir.com/docs/foundry/functions/functions-on-objects/ and /python-functions-on-objects
- OSDK overviews: https://palantir.com/docs/foundry/ontology-sdk/typescript-osdk/ and /python-osdk/ and /generate-osdk-for-other-languages and /how-to-bootstrapping-server-side-typescript
- Mandatory control properties: https://palantir.com/docs/foundry/object-link-types/mandatory-control-properties/
- Object and property security policies: https://www.palantir.com/docs/foundry/object-permissioning/object-and-property-policies
- Workshop module interface + embedded modules: https://palantir.com/docs/foundry/workshop/module-interface/ and /embedded-modules/ and /embedding-workshop-modules-overview
- Custom widgets dev mode: https://www.palantir.com/docs/foundry/custom-widgets/development
- AIP Logic blocks + compute usage: https://www.palantir.com/docs/foundry/logic/blocks and /logic/compute-usage/ and /logic
- AI FDE: https://palantir.com/docs/foundry/ai-fde/overview/
- Apollo: https://www.palantir.com/docs/apollo/core/introduction/ and /how-apollo-works and /plans-and-constraints/ and /managing-environments/environment-settings
- Data Lineage: https://palantir.com/docs/foundry/data-lineage/see-impact-marking-changes/ and /check-permissions/ and /explore-lineage
- Data Connection architecture: https://palantir.com/docs/foundry/data-connection/architecture/ and /set-up-source and /set-up-sync
- Foundry platform overview: http://www.palantir.com/docs/foundry/platform-overview/overview

Secondary:

- Ontologize (ex-Palantir engineers) on Actions-as-tools vs Apply Action blocks: https://www.youtube.com/watch?v=mCOvUImg2U8
- AI CERTs on AIP Bootcamps: https://www.aicerts.ai/news/palantir-bootcamps-propel-defense-ai-platforms-adoption/

Baseline document for this deep-dive: `/Users/danzakon/dev/life/research/.scratchpad/20260517-palantir-foundry-analysis.md`
