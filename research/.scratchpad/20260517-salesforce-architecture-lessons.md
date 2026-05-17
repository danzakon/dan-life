# Salesforce as the OTHER Reference Architecture for Enterprise OS
**Lessons for Tenex / OpenFoundry**

Date: 2026-05-17
Author: salesforce-historian (Tenex OpenFoundry research)
Companion to: `20260517-palantir-foundry-analysis.md`

---

## Summary

Palantir Foundry and Salesforce are the only two "enterprise operating systems" that have crossed escape velocity in the last 25 years. Foundry won the **data/ontology** side of the enterprise. Salesforce won the **record-of-action** side — the customer, the deal, the case, the order. The two architectures are best understood as inversions of each other:

- **Foundry**: starts from the warehouse, builds an ontology over governed data, runs code against that ontology under lineage-aware permissions.
- **Salesforce**: starts from a *shared multi-tenant relational schema* with a metadata-driven object layer, then bolts on a sandboxed scripting language (Apex), a declarative UI layer (LWC), a workflow runtime (Flow), and a packaging/distribution layer (Metadata API + AppExchange).

Salesforce's foundational insight — earlier and more durably than anyone else — is that **every primitive in the system (object, field, view, button, automation, permission, page, app) is metadata in a shared kernel, not code in a deployed binary**. That single bet enabled multitenancy, declarative customization, an ISV ecosystem, and now Agentforce's metadata-grounded agents. It is the most important architectural lesson a "platform play" can absorb.

For Tenex / OpenFoundry, the take-home is: **a typed object model + metadata layer + declarative customization + scripting escape hatch + packaging boundary is the minimum viable surface of an enterprise OS.** Skip any one of these and you are building either a tool (no platform) or a programming language (no admin distribution). Salesforce's mistakes (Apex governor limits, sharing-model complexity, custom-language lock-in) are equally instructive about *how* to ship each layer.

---

## Key Findings

1. **Metadata is the kernel.** In Salesforce, defining a custom object does *not* create a database table. The kernel reads a Universal Data Dictionary (UDD) at runtime and materializes a "virtual" table over shared pivot tables partitioned by `OrgID`. Every customer's customizations live as rows in the same physical schema as every other customer's. (Source: Force.com Multitenant Architecture whitepaper, 2008; `architect.salesforce.com/fundamentals/platform-multitenant-architecture`.)

2. **The Object Model is the lingua franca.** sObjects (Standard, Custom `__c`, External `__x`, Custom Metadata `__mdt`) with strongly-typed Fields and four relationship kinds (Lookup, Master-Detail, External-Lookup, Junction many-to-many) are the unit of programming for both admins and developers. Apex, SOQL, REST API, UI components, and now Agentforce all speak the same noun set.

3. **Sharing is a separate algebra from permissions.** Object/field permissions (Profiles + Permission Sets + Permission Set Groups + PSLs) decide *whether* a user can ever read a field. Sharing (Org-Wide Defaults + Role Hierarchy + Sharing Rules + Manual Sharing + Apex Managed Sharing + Teams + Territories + Implicit Sharing) decides *which records* a user can see. Both must allow access. This bifurcation is famous for being painful and famous for being correct.

4. **Declarative beats programmatic for adoption; programmatic is required for power.** Apex, LWC, and Flow are escape hatches. The platform's center of gravity is point-and-click admins. Every programmatic capability eventually gets a declarative wrapper (Workflow Rules → Process Builder → Flow Builder).

5. **Packaging makes the ecosystem.** The Metadata API + Managed Packages (now 2GP) + namespaces + AppExchange security review created an ISV market that Salesforce taxes at 15-25% of revenue. Without the Metadata API, AppExchange is impossible; the API is the product.

6. **Apex is a deliberately weak language.** Java-like syntax, but with governor limits (100 SOQL/txn, 150 DML, 6MB heap, 10s CPU sync), no threads, no file I/O, no arbitrary library imports, mandatory ≥75% test coverage to deploy to production. Salesforce built a custom language *specifically so customer code cannot break tenancy*. The cost is that Apex has trapped a generation of engineers in a low-mobility skill silo.

7. **The AI moment rewards the existing object model.** Agentforce + Atlas + Data Cloud do not replace the object/permission/metadata stack — they layer on top of it. The Trust Layer's grounding, masking, audit, and access enforcement only work because Salesforce already had typed objects, field-level security, and sharing rules. **A reasoning engine is only as good as the schema it grounds in.**

---

## Details

### 1. Foundational architectural bets

#### 1a. Metadata-driven multitenancy

The original 2008 Force.com whitepaper is still the clearest statement of the thesis. From `architect.salesforce.com`:

> A single instance of the Salesforce Platform uses (1) a single shared multitenant database with a single schema that stores tenant-specific metadata and data, and (2) a multitenant kernel that reads metadata and data to dynamically provide tenant-specific applications, business logic, and APIs.

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

Every tenant-specific record in shared database tables carries an `OrgID`. The kernel injects `OrgID` predicates into every query. There are no per-tenant schemas. **The database is a key-value store dressed in relational clothing.**

Why this matters: every customer gets every kernel upgrade simultaneously, with zero migration effort, because the kernel changes but the metadata doesn't. A 2015 Salesforce release is the same binary running over Citi's metadata as over a 5-seat startup's metadata. This is the single biggest reason Salesforce can ship a release three times a year across millions of orgs.

#### 1b. The Object Model

The basic noun:

| Type | Notation | Example | Notes |
|---|---|---|---|
| Standard Object | `Account` | `Account`, `Contact`, `Opportunity`, `Case`, `Lead` | Pre-built, opinionated CRM semantics |
| Custom Object | `Foo__c` | `Project__c`, `Invoice__c` | Tenant-defined |
| Custom Metadata Type | `Foo__mdt` | `Tax_Rate__mdt` | Metadata, *not* data — deployable, queryable, but stored in the metadata layer |
| External Object | `Foo__x` | `SAP_Order__x` | Federated via OData; lives in another system |
| Junction Object | (CustomObj with 2 MD relationships) | `Contact_Project__c` | Implements N:N |

Field types span the expected primitives (Text, Number, Currency, Date, Email, Phone, URL, Checkbox), plus a long tail of platform-native types (Formula, Roll-up Summary, Picklist, Multi-Picklist, Geolocation, Address as a compound field, Lookup, Master-Detail, Hierarchy, Encrypted, Long Text Area, Rich Text). Salesforce treats Address and Location as **compound fields** — first-class composite primitives — which is a small but underappreciated UX bet.

**Relationships:**

```
Lookup            : weak FK, no cascade, child has its own owner & sharing
Master-Detail     : strong FK, cascade-delete, child inherits master's sharing
                    and ownership; required field on detail
External Lookup   : FK from Salesforce object → external object (OData)
Indirect Lookup   : FK from external object → Salesforce object (rare)
Many-to-Many      : pattern using a Junction custom object with two MD fields
```

Master-Detail is **the** key abstraction. By choosing MD over Lookup, an admin makes a sharing/security decision (child inherits) *and* a lifecycle decision (cascade) and a UX decision (related list). One mouse click; three semantic commitments. This is the kind of bundling Tenex needs to think hard about.

#### 1c. Sharing and visibility — why it's complex and why that's correct

There are nine distinct mechanisms by which a user can come to see a record:

```
1. Ownership           — user owns the record
2. Role Hierarchy      — user is above the owner in the role tree
3. Org-Wide Default    — record's object is Public R/W or Public Read
4. Sharing Rule        — owner-based or criteria-based, opens access
5. Manual Sharing      — clicked Share button on a record
6. Apex Managed        — code wrote a row to `Foo__Share`
7. Teams               — Account/Opp/Case team membership
8. Territory           — territory hierarchy assignment
9. Implicit Sharing    — parent↔child auto-grants (Account→Opp/Contact/Case)
```

All grants are written to a per-object `*__Share` table at the row level, with a `RowCause`. **Most-permissive wins.** Object-level Permission Sets/Profiles gate whether the user can ever even reach the share table for that object. Field-level security gates which columns are returned.

```
┌─────────────────────────────────────────────────────────────┐
│  Can user U see field F of record R on object O?            │
└─────────────────────────────────────────────────────────────┘
                          │
            ┌─────────────┴─────────────┐
            ▼                           ▼
   ┌────────────────┐         ┌──────────────────┐
   │ Permissions    │   AND   │ Sharing          │
   │ (Profile +     │         │ (any of 9 paths  │
   │  Perm Sets):   │         │  produces a row  │
   │  - Object R?   │         │  in O__Share for │
   │  - Field F R?  │         │  user U on R?)   │
   └────────────────┘         └──────────────────┘
```

This complexity is the price of supporting a single architecture that serves a 3-person startup with public-everything OWDs and Citigroup with criteria-based, territory-aware, regulatory-segregated record visibility. **The model is famously complex because the requirements are famously complex** — Salesforce did not invent the complexity, it surfaced and named it.

The pattern to steal: **separate the "is this column readable" question (permissions) from the "is this row visible" question (sharing).** Foundry's mandatory ACLs over ontology objects do not currently make this distinction crisp enough; Tenex should.

#### 1d. Profiles, Permission Sets, Permission Set Groups, PSLs

The layered permission model:

```
User License       : the SKU you bought (Full CRM, Platform, Chatter Free, etc.)
   └─ Profile      : exactly ONE per user; legacy baseline; should be minimal
        └─ Permission Set       : zero or more per user; additive
             └─ Permission Set Group  : a bundle of permission sets
                  └─ Permission Set License : SKU add-on (e.g. CRM Analytics)
```

Modern Salesforce best practice: keep profiles empty (just default record types / layouts / login hours), put *all* capability into Permission Sets, bundle into Permission Set Groups by persona. Salesforce is now formally migrating Profile permissions to Permission Sets (`Migrate to Permission Sets` is its own tool in Setup).

Lesson: **start additive.** A "user has one role and the role grants everything" model collapses under the second exception. Start with "user has a baseline + N stacking permission sets" or you will retrofit it later under pain.

#### 1e. Apex — the deliberately weak language

Apex is a Java-like, strongly-typed, compiled-to-VM language that runs inside a sandbox with hard limits called *governor limits*. Synchronous limits include:

| Limit | Synchronous | Asynchronous (Batch / @future / Queueable) |
|---|---|---|
| SOQL queries / txn | 100 | 200 |
| SOQL rows retrieved | 50,000 | 50,000 |
| DML statements | 150 | 150 |
| DML rows | 10,000 | 10,000 |
| CPU time | 10s | 60s |
| Heap | 6MB | 12MB |
| Callouts | 100, 120s cumulative | — |

If you exceed any limit, the transaction throws an `uncatchable` exception and rolls back. **The tenant's bad code cannot starve the platform.** This is the entire reason the language exists. A Salesforce engineer once told me: "Apex isn't a programming language. It's a rate-limiter with syntax."

Apex enforces other isolation properties:
- 75% test coverage minimum to deploy to production
- Bulk-safe patterns are mandatory (`for (Account a : Trigger.new)` cannot do SOQL inside the loop without dying)
- No threading, no file I/O, no arbitrary HTTP without a Named Credential
- All HTTP callouts require pre-registered remote site/Named Credential
- All DML obeys sharing rules unless class is marked `without sharing`
- Inheritance, generics, anonymous blocks, asynchronous primitives (`@future`, `Queueable`, `Database.Batchable`, `Schedulable`)

**Why a custom language instead of letting customers run arbitrary code?** Because in 2006 there was no Docker, no Firecracker, no V8 isolates, no WASM. The only way to run untrusted tenant code safely in a shared multitenant kernel was to design a language that *could not* misbehave. In 2026, this is no longer true — but the existing fleet of Apex code is a generational moat that locks customers in.

Modern lesson: **you still need a sandbox boundary for tenant code, but you no longer need to invent a language.** A WASM/V8/Firecracker isolate around TypeScript with metered limits gets you 80% of the Apex benefit with 0% of the lock-in.

#### 1f. Lightning Web Components (LWC) and the Aura migration

Salesforce's frontend extensibility model went through three eras:

```
Visualforce (2008)    → Apex pages with custom server tags. Server-rendered.
Aura (2014)           → Salesforce's bespoke client-side framework.
                        Pre-dated Web Components. Heavy, slow, idiosyncratic.
Lightning Web         → 2019. Built on Web Components / ES7+. ~65% reduction
  Components (LWC)      in JS errors, 40% page-time improvement (per SF
                        internal data, 2023 dev blog).
```

The Aura → LWC migration is a multi-year project Salesforce is still finishing — they've migrated 75%+ of record home pages and have an internal "LWC All the Way" (LAW) program. Components can interop: Aura can contain LWC, but LWC *cannot* contain Aura. This asymmetry shapes migration order (bottom-up: replace leaf Aura components with LWC, work up the tree).

Lesson: **a frontend framework is a 10-year commitment.** Pick the most boring, most standards-aligned option you can find. Salesforce paid an enormous tax for Aura. The LWC bet on Web Components paid off, but only because Salesforce had the runway to migrate the entire ecosystem. **Don't write your own framework — wrap a standard one.**

#### 1g. Flow Builder — the declarative workflow runtime

Salesforce had three overlapping automation tools, and is killing two:

```
Workflow Rules (2003)  ─┐
                        ├─ end-of-life; "Migrate to Flow" tool available
Process Builder (2015) ─┘
                        ▲
Flow Builder (2014→)    ┘ — the survivor
```

Flow is a visual workflow runtime that runs in the same transaction context as Apex triggers, can be entry-point-triggered (record change, schedule, platform event, screen action), and is the substrate for Agentforce's invokable actions today. Flows compile into a metadata format and run inside governor limits.

Lesson: **converge on one automation tool.** Salesforce burned a decade with three. The convergence story is going to define Agentforce's success — every Flow is a callable tool for an LLM agent.

#### 1h. Salesforce DX, the Metadata API, and source-driven development

Salesforce's modern dev lifecycle:

```
                ┌──────────────────────────────────┐
                │  Production Org / Sandbox        │
                │  (the running system)            │
                └────────────┬─────────────────────┘
                             ▲ Metadata API
                             │
              ┌──────────────┴──────────────┐
              ▼                             ▼
       ┌────────────┐               ┌─────────────┐
       │  Scratch   │               │   Git repo  │
       │   Org      │◄─── sf CLI ──►│   (source   │
       │ (ephemeral)│   source-     │    format)  │
       │            │   tracked     │             │
       └────────────┘               └─────────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │  Unlocked / Managed Package  │
              │  (versioned, installable)    │
              └──────────────────────────────┘
```

The Metadata API exposes *every* configurable element as XML/JSON metadata. Salesforce DX (the `sf` CLI) deconstructs that metadata into a Git-friendly source format, supports ephemeral *scratch orgs* (think `docker run` for a Salesforce environment), and packages source into versioned, installable units.

Lesson: **the Metadata API is the platform.** If you cannot diff, version, package, and reinstall every customization as text, you do not have a platform — you have a SaaS app. Foundry has this (Marketplace + branches over ontology), but less crisply than Salesforce DX. Tenex must build this on day one. Make sure that the *first* user-facing primitive in OpenFoundry is "definitions as code."

### 2. AppExchange and the ISV ecosystem

Launched in 2006. Today: 7,000+ apps, 11M+ installs, ~$10B+ ecosystem GMV. The architecture:

```
ISV Partner
   │
   │ develops in a Partner Business Org (PBO, aka Dev Hub)
   │ in scratch orgs, source-controlled
   │
   ▼
Managed Package (2GP)
   ├─ Owns a unique namespace (e.g. `ns_finco`)
   ├─ All custom metadata prefixed with namespace
   ├─ Versioned releases (semver-ish)
   ├─ Customer-installed metadata is upgrade-controlled by the ISV
   └─ Customer cannot edit ISV-owned code; can extend via extension packages
       │
       │ submits for Security Review (mandatory, paid, multi-month)
       │
       ▼
AppExchange Listing
   │
   │ Customer browses, installs into their org (managed package metadata
   │ inserts into the customer's org with namespace; same kernel, same DB)
   │
   ▼
License Management App (LMA) + Channel Order App (COA) + AppExchange Checkout
   │
   │ Salesforce takes 15% (AppExchange Checkout) up to 25% (ISVforce / OEM)
   │ of partner revenue. Marginal PNR program reduces rate as ISV scales.
   │
   ▼
Certified managed packages get their OWN governor limit pool, so an ISV's
code doesn't compete with the customer's code for the same 100 SOQL
queries/transaction. (This is a *huge* architectural concession that
enabled the ecosystem.)
```

Per Salesforce's published policies:
- **AppExchange Checkout fee**: 15% flat (plus $0.30/credit-card transaction via Stripe).
- **ISVforce PNR (Percent Net Revenue)**: 15% baseline, drops to 10% at $20M+ AOV (Marginal PNR Model).
- **OEM PNR**: 25% baseline, drops to 15% at $20M+ AOV (because OEM partners embed Salesforce as their own platform).

Why ISVs accept this:
1. **Distribution**: AppExchange is the #1 enterprise software discovery surface in B2B.
2. **Architecture leverage**: ISVs don't rebuild auth, data model, sharing, audit, UI primitives, mobile, search, reporting. They write *business logic* and ship.
3. **Co-sell motion**: Salesforce sellers will pull ISV packages into deals.
4. **Per-namespace governor limits**: Cumulative cross-namespace limit is 11× per-namespace (e.g. 1,100 SOQL/txn across 11 namespaces). This is the technical concession that makes complex multi-ISV orgs survivable.

Lesson for Tenex: **packaging + namespacing + per-package resource budgets is the moat.** Once an ISV ecosystem exists, switching costs become asymmetric — every ISV is a lobbyist for the platform. The economics also work: a $10B GMV ecosystem at 15% gross take = $1.5B/yr of high-margin platform tax. Tenex's $300/storypoint engineering revenue is *amazing* short-term, but a fraction of what an ISV ecosystem could throw off at scale.

### 3. Declarative vs programmatic — the cultural commitment

Salesforce's deepest cultural pattern is **"clicks not code"**:

```
Declarative tier              Programmatic tier              Hybrid
──────────────────            ──────────────────             ──────
Object/Field designer    →    Apex Object describes
Page Layout / Lightning  →    LWC / Aura components          Embed LWC in pages
  App Builder
Flow Builder             →    Apex Triggers / Queueables     Flow → Apex action
Validation Rules         →    Apex `addError()`              Either layer
Approval Processes       →    Custom workflow in Apex
Reports & Dashboards     →    SOQL + CRM Analytics SAQL
Permission Sets          →    Apex sharing recalculation
Email Templates          →    Apex outbound email
```

Every capability has a declarative entry point. The programmatic escape hatch is *always available* but never preferred. This matters because **the admin population is 10-100× the developer population in the average Salesforce org**, and admins ship most of the change. If your platform requires a developer for ordinary change, you have a tool, not a platform.

But there is a tension Salesforce has not resolved: complex Flows become unmaintainable. A 200-step Flow is harder to debug than 200 lines of Apex. The right pattern (which Tenex should adopt explicitly): **declarative for the 80% case, programmatic when the Flow exceeds N steps or needs deterministic ordering, observability, or unit testing.** Make the boundary visible and intentional, not accidental.

### 4. Data Cloud + Agentforce + Atlas + Einstein Trust Layer (2024-2026)

The Salesforce AI architecture as of mid-2026:

```
┌──────────────────────────────────────────────────────────────────┐
│                    Customer 360 Platform                         │
│                                                                  │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  Agentforce (Agents)                                    │   │
│   │  ├─ Agent Builder (natural-language config)             │   │
│   │  ├─ Topics → Instructions → Actions                     │   │
│   │  └─ Actions = Flows + Apex + Prompt Templates + APIs    │   │
│   └────────────────────┬────────────────────────────────────┘   │
│                        │ orchestrated by                        │
│   ┌────────────────────▼────────────────────────────────────┐   │
│   │  Atlas Reasoning Engine                                 │   │
│   │  ├─ Chit-Chat Detector → Query Evaluator                │   │
│   │  ├─ Query Expander → Retriever (RAG over Data Cloud)    │   │
│   │  ├─ Planner (ReAct loop, "System 2" inference)          │   │
│   │  ├─ Re-ranker, Refiner, Response Synthesizer            │   │
│   │  └─ Quality Evaluator                                   │   │
│   └────────────────────┬────────────────────────────────────┘   │
│                        │ all I/O passes through                  │
│   ┌────────────────────▼────────────────────────────────────┐   │
│   │  Einstein Trust Layer                                   │   │
│   │  ├─ Secure data retrieval (respects sharing!)           │   │
│   │  ├─ Dynamic grounding                                   │   │
│   │  ├─ PII / sensitive data masking (pre-LLM)              │   │
│   │  ├─ Prompt-injection defense                            │   │
│   │  ├─ Toxicity / bias detection (post-LLM)                │   │
│   │  ├─ Zero data retention contracts w/ model providers    │   │
│   │  └─ Audit trail of every agent action                   │   │
│   └────────────────────┬────────────────────────────────────┘   │
│                        │ grounded in                            │
│   ┌────────────────────▼────────────────────────────────────┐   │
│   │  Data Cloud ("Data 360")                                │   │
│   │  ├─ Zero-Copy federation to Snowflake/Databricks/BQ     │   │
│   │  ├─ Real-time identity resolution / harmonization       │   │
│   │  ├─ Vector index over structured + unstructured         │   │
│   │  └─ Streams into the Salesforce Object Model            │   │
│   └────────────────────┬────────────────────────────────────┘   │
│                        │ governed by                            │
│   ┌────────────────────▼────────────────────────────────────┐   │
│   │  Salesforce Metadata Layer (sObjects, fields,           │   │
│   │   permissions, sharing, flows, apex, LWC)               │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

Three things to internalize:

1. **Every Flow and every Apex method is automatically a callable tool for Agentforce.** Salesforce's investment in declarative automation became its agent-action library overnight. The cost of building 10,000 invocable actions was paid in 2014-2024. Agentforce gets it for free.

2. **The Trust Layer's grounding and masking enforcement rides on the existing permission/sharing model.** An agent acting "as user U" cannot retrieve records U cannot see. This is why Salesforce can ship enterprise agents and OpenAI/Anthropic-on-raw-data cannot: **agentic action requires a typed access model below it.**

3. **Atlas's ReAct loop is unremarkable; the data grounding is the moat.** Every vendor has a planner. Only Salesforce has the planner *plus* 25 years of opinionated customer-data schemas *plus* a permission system that the planner is forced to obey. (Per Phil Mui's engineering blog: early Atlas pilots showed "2× increase in response relevance and 33% increase in end-to-end accuracy" vs. DIY agents. The delta isn't reasoning — it's grounding.)

What Salesforce is doing *wrong* in the AI age:
- Pricing Agentforce in a way that confuses customers (conversation credits, consumption tiers, $0.02-$2/conversation depending on tier — admins can't predict cost).
- Forcing customers through Data Cloud as a paywall ($100k+ entry) even when zero-copy makes it technically optional.
- Lock-in to Salesforce-hosted LLMs ("Models" allows BYO via API, but the Trust Layer features are weaker against external models).

What it's doing *right*:
- Treating metadata as the agent's context. Field labels, help text, validation rules, and Flow names become natural-language descriptions of capabilities. Years of admin labor become free agent comprehension.
- Audit Trail by default. Every agent action is logged at field-level granularity, like every UI action always has been.

### 5. The pattern that proves matters for enterprise OS plays

Salesforce + Foundry triangulate the same six necessary layers:

| Layer | Salesforce | Foundry | Required because |
|---|---|---|---|
| **Typed schema/object model** | sObjects (`__c`, `__mdt`, `__x`) | Ontology (Object Types, Link Types) | Without it, no tool can be safe |
| **Metadata-as-code** | Metadata API + SFDX | Ontology resources in version control | Without it, no diff/test/rollback |
| **Declarative customization** | Flow, Permission Sets, Layouts | Workshop, Slate, Quiver | Without it, admins can't ship |
| **Programmatic escape hatch** | Apex, LWC, Triggers | Functions, Transforms (Python/Java) | Without it, the 20% blocks the 80% |
| **Permission + sharing model** | Profiles+PSet / Sharing | Mandatory ACLs on ontology | Without it, AI cannot be trusted |
| **Packaging + distribution** | Managed Packages + AppExchange | Marketplace (newer, weaker) | Without it, no ecosystem moat |

**Both proved that this six-layer minimum is necessary.** Neither proved it is sufficient (both struggle with developer joy, both have legacy weight). But if you ship five of six, you have a product. Ship all six and you have a platform.

### 6. What Tenex should steal from Salesforce

**Steal immediately (year 1):**

1. **Metadata-driven object model.** Every customer-defined object, field, permission, view, and automation is a row in a versioned metadata store, not a schema migration. This is the *only* way to ship a multi-tenant customizable platform without going insane.

2. **Strong typing with named primitives.** Don't ship "string" and "number" — ship `Email`, `Currency`, `Phone`, `URL`, `Address (compound)`, `Geolocation`, `LookupTo(Object)`, `Picklist(values)`. Each named type comes with validation, display, and search behavior. Composite primitives like Address pay for themselves in UX.

3. **Permissions ≠ Sharing.** Object/field permissions decide "can this user ever see this column." Record-level access (analog of Sharing) decides "which rows." Both must allow. Make them orthogonal in your data model from day one — retrofitting this later is the #1 architectural regret of every B2B platform.

4. **Additive permission sets, not role-replaces-role.** User has a baseline + N stacking permission grants. One-role-per-user is an anti-pattern; it forces profile explosion. Salesforce has been migrating *away* from profiles for a decade — don't recreate the mistake.

5. **Declarative-first, programmatic-second.** Every feature exposed to admins gets a no-code surface. The TypeScript/Python escape hatch is always available but never the default path. The admin/developer ratio in successful enterprise tools is ~10:1; design for the 10.

6. **A "describe API."** Salesforce's `Describe` lets any tool introspect the full schema of an object at runtime (fields, types, picklists, relationships, permissions for the current user). This is what makes LWC dynamic, Apex generic, and Agentforce grounded. **Build the introspection API before you build the CRUD API.**

**Steal in year 2-3:**

7. **A scripting escape hatch with metered limits.** Tenant code runs in a WASM/V8 isolate with per-execution CPU/memory/network/storage caps. Don't invent a language — pick TypeScript or Python and constrain the runtime, not the syntax. Avoid Apex's lock-in trap.

8. **Source-driven definition lifecycle.** Every object, permission set, flow, and script is exportable as code, diffable in Git, deployable via CI/CD, packagable as a versioned unit. SFDX is the gold-standard reference here.

9. **An automation runtime (Tenex's "Flow").** Visual + JSON-serializable, runs in the same transaction as the data layer, has entry-point triggers (record change, schedule, event), and — critically — every automation becomes a callable tool for the LLM agent layer.

10. **Per-tenant agent layer that grounds on the typed object model + permission system.** Agentforce is the proof. The reasoning engine is commodity (everyone will have ReAct + RAG by EOY 2026). The moat is the grounding context: schemas, labels, validation rules, sharing rules. Make sure your object model captures enough metadata that the agent doesn't need additional prompt engineering.

**Steal in year 3+:**

11. **A packaging/distribution layer.** Versioned, namespaced bundles of metadata + code that customers install into their tenant. This becomes the ISV motion. Tenex won't need this for FDE-led customer #1 through #100, but at customer #1,000 the question becomes "how does an agency in São Paulo ship a customization to a Tenex customer in Frankfurt without a Tenex engineer in the loop?" The answer is managed packages.

12. **A marketplace with a security review.** AppExchange's security review is friction, but it is also the trust mechanism that makes installing a third-party package safe. Without curation, the ecosystem becomes the Chrome extension store.

### 7. What Tenex should NOT copy

1. **Don't invent a programming language.** Apex's lock-in is generational and the engineer market for Apex is shrinking. WASM/V8 sandboxes around TypeScript get you the same isolation without the recruiting nightmare.

2. **Don't ship multiple overlapping automation tools.** Salesforce had Workflow Rules + Process Builder + Flow and spent a decade unwinding it. Pick one and evolve it.

3. **Don't ship your own frontend framework.** Aura was a multi-billion-dollar mistake. Build on web standards (Web Components, React, Lit) — wrap them, don't replace them.

4. **Don't make sharing 9 different mechanisms.** Salesforce's sharing model has Owner + Role Hierarchy + Sharing Rules + Manual + Apex + Teams + Territories + Implicit + Public Groups. The complexity is famous. **Start with 3: Owner, Group membership, Criteria-based rule.** Add more only when customers demand it with money.

5. **Don't bind compute to per-transaction governor limits visible to developers.** Apex governor limits are *the* most-complained-about feature. Set quotas at the org/tenant level, not the transaction level, and surface them as soft quotas with backpressure, not uncatchable exceptions. Modern infra (k8s, serverless, isolates) gives you better primitives.

6. **Don't pre-commit to a single hosting model.** Salesforce's Hyperforce migration (from owned data centers to AWS/Azure/GCP) is still ongoing in 2026, 5+ years in. OpenFoundry's "BYO cloud + BYO LLM + BYO warehouse" thesis is the right reaction.

### 8. Salesforce vs Foundry — synthesis

```
                   SALESFORCE                       FOUNDRY
                   ──────────                       ───────
Origin            Records of action                 Operational data
                  (CRM)                             (intelligence /
                                                    industrial ops)

Primary unit      sObject (typed object             Ontology Object Type
                  in shared schema)                 (over governed data)

Customization     Metadata-driven,                  Pipelines + Ontology
  primitive       click-to-create                   manager + Workshop

Permissions       Profile + Perm Set                Mandatory ACLs from
                                                    lineage

Record visibility 9-mechanism sharing model         Lineage-derived ACL
                  + per-row Share table             propagation

Scripting         Apex (custom VM,                  Functions, Transforms
                  governor limits)                  (Python / Java / SQL),
                                                    plus Code Workbooks

UI extensibility  LWC + Lightning App Builder       Slate (low-code) +
                                                    Workshop apps

Workflow          Flow Builder                      Quiver / Actions

Packaging         Managed Packages 2GP +            Marketplace (newer,
                  AppExchange (15-25% rev share)    less mature, less
                                                    standardized)

Source control    SFDX + Metadata API               Branches in Foundry
                                                    + Marketplace SCM

AI layer          Agentforce + Atlas +              AIP + Logic +
                  Trust Layer over object           Functions over
                  model                             ontology

Wins              Adoption curve (admin-buildable), Lineage-aware safety,
                  ecosystem (AppExchange),          deep data integration,
                  packaging discipline              ontology as graph

Loses             Sharing complexity, Apex          Less admin-friendly,
                  lock-in, opinionated CRM          steeper learning
                  schema bias                       curve, weaker ISV
                                                    motion
```

**What each gets right that the other doesn't:**

- **Foundry's lineage-aware mandatory access** is correct in a way Salesforce's sharing model is not. If a derived dataset is produced from a sensitive parent, Foundry forces the derived dataset's ACL to be at least as restrictive as the parent. Salesforce has no equivalent — a Roll-up Summary field on a Master-Detail child can leak data if you misconfigure FLS on the rollup. **Tenex should adopt Foundry's lineage propagation as the default.**

- **Salesforce's metadata-as-code packaging** is correct in a way Foundry's isn't yet. The Metadata API + Managed Packages + AppExchange security review create a *commercial* ecosystem with real money flowing through it. Foundry's Marketplace is closer to a private template gallery. **Tenex should adopt Salesforce's packaging discipline and revenue-share economics.**

- **Both miss developer joy.** Apex is sad. Foundry's Functions are slightly less sad. The next platform should ship modern TypeScript/Python with a great local dev experience (Cursor / Claude Code integration, fast feedback loops, real unit testing). **This is Tenex's wedge.**

---

## Tenex Translation (Concrete Patterns to Steal vs Avoid)

### Steal in OpenFoundry's MVP

```
✓ Metadata-driven object model (every customization is a row, not a migration)
✓ Strongly-typed named primitives (Email, Currency, LookupTo, Picklist, Address)
✓ Permissions ⊥ Sharing (orthogonal access dimensions, both must allow)
✓ Additive permission sets stacked on a minimal baseline (no role-explosion)
✓ Describe / introspection API before CRUD API
✓ Declarative-first UX surface for objects, automations, permissions
✓ Source-driven definition lifecycle (Git-able, diffable, deployable as code)
✓ Foundry-style lineage-propagated ACLs over derived datasets
✓ Audit log of every action at field-level granularity
✓ A single workflow runtime (don't ship two)
```

### Steal in year 2-3

```
✓ Sandboxed scripting escape hatch (WASM/V8/Firecracker over TS/Python,
  NOT a custom language — avoid the Apex trap)
✓ Tenant-level (not transaction-level) resource quotas with backpressure
✓ Versioned, namespaced packages of metadata + code
✓ Agent layer that grounds on the object model, sharing rules, and
  metadata labels — make every workflow callable as an agent action
✓ Trust Layer pattern: masking pre-LLM, audit + policy enforcement,
  zero-retention contracts with model providers
```

### Steal in year 3+

```
✓ Marketplace with security review (the commercial ecosystem)
✓ Revenue share economics (15-25% PNR with marginal reduction at scale)
✓ ISV partner program with per-package resource budgets
```

### Avoid

```
✗ Custom programming language (use TS/Python in a sandbox)
✗ Custom frontend framework (use Web Components / React)
✗ Multiple overlapping automation tools (pick one)
✗ 9-mechanism sharing model (start with 3, grow under pressure)
✗ Per-transaction uncatchable governor exceptions (use soft quotas)
✗ Pre-committing to a single hosting model (BYO cloud is the right bet)
✗ Pricing models that admins can't predict (don't repeat Agentforce's
  conversation-credit confusion)
```

### What this implies for Tenex's near-term path

Tenex today is selling engineering capacity at $300/storypoint. The Salesforce lesson is that this is *services revenue*, and services revenue scales linearly with bodies. The platform leverage comes when the same engineering output that delivers customer value also accretes to a reusable metadata catalog, a reusable component library, a reusable agent action library. **Every FDE engagement should be designed to deposit metadata into OpenFoundry's library, not just code into a customer's repo.** Salesforce's lock-in is that every admin who learned the sObject model and every developer who learned Apex became a free distribution channel. Tenex's equivalent: every FDE engagement that delivers via OpenFoundry primitives makes the platform more powerful, makes the next engagement cheaper, and trains a future Tenex-skilled engineer who will pull Tenex into their next job.

The packaging + marketplace play is a year-3+ question, but the *architectural decisions to enable* it are year-1 decisions. Once you ship a non-namespaced metadata layer, you can't add namespacing later without breaking every customer. Same for permissions, sharing, the describe API, and the source format. **Pay the architectural tax now; reap the ecosystem in year 3.**

---

## Sources

- Force.com Multi-Tenant Architecture whitepaper (2008). developerforce.s3.amazonaws.com/whitepapers/WP_Force-MT_101508_PRINT.pdf
- "Platform Multitenant Architecture" — Salesforce Architects. architect.salesforce.com/fundamentals/platform-multitenant-architecture
- "Architecture Basics" — Salesforce Architects. architect.salesforce.com/docs/architect/fundamentals/guide/architecture-basics
- "Overview of Salesforce Objects and Fields" — Salesforce Developers. developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_concepts.htm
- "Relationships Among Standard Objects and Fields" — Salesforce Developers.
- "Salesforce Data Model Notation" — Salesforce Developers.
- "Work with sObjects in Apex" — Trailhead. trailhead.salesforce.com/content/learn/modules/apex_database/apex_database_sobjects
- "Platform Sharing Architecture" — Salesforce Architects. architect.salesforce.com/docs/architect/fundamentals/guide/platform-sharing-architecture
- "Salesforce Visibility Explained: How Record Access Really Works" — Salesforce Ben, 2026-01-05.
- "Salesforce Sharing Models: The Complete Guide" — SFDC Developers, 2025-09-13.
- "Apex Security and Sharing Model: Enforce Sharing Rules" — Salesforce Developers.
- "Execution Governors and Limits" — Salesforce Developers (2025-08-26).
- "Apex Transactions and Governor Limits" — Salesforce Developers.
- "Governor Limits Explained — Complete Guide" — Salesforce Decoded.
- "User Functionality Management in Salesforce" — Trailhead.
- "Salesforce Data Security Model — Explained Visually" — Salesforce Developers Blog (2017-04).
- "Salesforce Roles vs Profiles vs Permission Sets" — Talantir Guides, 2026-03-30.
- "Use Permission Sets To Overcome Common Access Dilemmas" — Salesforce Admins, 2024-11-11.
- "Working with Aura and Lightning Web Components: Interoperability and Migration" — Salesforce Developers Blog (2019-02).
- "Unlocking Aura-to-LWC Migration at Salesforce" — Salesforce Developers Blog (2023-01).
- "Aura Coexistence" — LWC Developer Guide.
- "Go with the Flow: What's Happening with Workflow Rules and Process Builder?" — Salesforce Admins (2021-10).
- "Improving Salesforce Automation" / "Migrate to Flow" — Trailhead.
- "What Is Package Development" — Trailhead.
- "Source-Driven Development with Salesforce DX Explained" — Trailhead.
- "Scratch Orgs" — Salesforce DX Developer Guide.
- "Deploy Source From Your Project to the Scratch Org" — SFDX Developer Guide.
- "Salesforce Packaging Guide" (2025-12). resources.docs.salesforce.com/latest/latest/en-us/sfdc/pdf/salesforce_packaging_guide.pdf
- "AppExchange Partner Program" — partners.salesforce.com.
- "Salesforce Partner Program Policies" (2024-04). salesforce.com/content/dam/web/en_us/www/documents/legal/Agreements/...
- "How Is Revenue Shared in AppExchange Checkout?" — ISVforce Guide.
- "Pricing Plan Creation & Tiers" — Trailhead.
- "How Data Cloud Fuels Agentforce & the Next Era of AI" — Salesforce (2024-11-20).
- "How Does Agentforce Work?" — Salesforce.
- "How the Atlas Reasoning Engine Powers Agentforce" — Salesforce.
- "Inside Agentforce: Revealing the Atlas Reasoning Engine" — Salesforce Engineering Blog (2024-12-10).
- "Explained: How Salesforce Agentforce's Atlas reasoning engine works" — InfoWorld (2024-09-30).
- "Trusted AI: Key Principles" — Salesforce.
