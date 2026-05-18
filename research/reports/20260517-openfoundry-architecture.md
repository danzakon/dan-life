---
id: 20260517-RS-003
date: 2026-05-17
category: Architecture Document
content-status: raw
---

# OpenFoundry — Architecture Document

> A C4-style architecture for OpenFoundry as a **semantic + governance control plane** sitting on top of customer-owned systems. We do not own the data; we own the ontology, the action runtime, the policy decision plane, and the audit trail. This document defines every container, component, technology choice, integration pattern, monorepo structure, and the 90-day first-customer deployment plan.

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Architecture Principles](#architecture-principles)
3. [C4 Level 1 — System Context](#c4-level-1--system-context)
4. [C4 Level 2 — Container Diagram](#c4-level-2--container-diagram)
5. [C4 Level 3 — Component Diagrams](#c4-level-3--component-diagrams)
6. [Cross-Cutting Concerns](#cross-cutting-concerns)
7. [Data Flows](#data-flows)
8. [The Salesforce Integration Pattern (Worked Example)](#the-salesforce-integration-pattern-worked-example)
9. [Monorepo Structure](#monorepo-structure)
10. [Technology Choices Summary](#technology-choices-summary)
11. [The First-Customer Deployment Plan (90 Days)](#the-first-customer-deployment-plan-90-days)
12. [Building the System While Deploying the First Customer](#building-the-system-while-deploying-the-first-customer)
13. [Roadmap and Milestones](#roadmap-and-milestones)
14. [Appendix A — Data Model](#appendix-a--data-model)
15. [Appendix B — API Surface](#appendix-b--api-surface)

---

## Executive Summary

OpenFoundry is a Foundry-equivalent designed for the 2026 reality where customers already pay for warehouses (Snowflake, Databricks), source systems (Salesforce, ServiceNow, Workday), identity providers (Okta, Entra), and AI models (Anthropic, OpenAI). We do not try to be any of those things. We are the **layer that sits on top of them** and makes them collectively safe and useful for agents.

The thesis: **we own the metadata, not the data.** A customer's records stay in Salesforce. Their warehouse rows stay in Snowflake. Their auth tokens stay in Okta. OpenFoundry stores object type definitions, action type definitions, policy bundles, audit logs, and a small amount of user-edit overlay state. Reads flow through OpenFoundry as federated queries to the source systems. Writes flow through OpenFoundry as typed Actions that route to source-system APIs. Every operation is permission-checked, audited, and exposed to agents via MCP and to engineers via a typed OSDK.

This is **dramatically lighter than Foundry**. We build five custom services (Ontology, Action, Query, Functions, OSDK codegen) and compose everything else from open-source projects and managed services. The v1 stack ships in 90 days with five engineers, hits first revenue from an existing Tenex F500 account in months 4–5, and scales architecturally to 100+ customers without a fundamental rewrite.

The architecture is opinionated. Every container has a specific job and a specific technology choice with stated rationale. Multi-tenancy is namespace-based on Kubernetes. Auth is OAuth 2.1 + OIDC federation. Authorization is OpenFGA-backed PDP/PEP separation. Observability is OpenTelemetry end-to-end. The whole thing lives in a single Turborepo monorepo with five apps, ten services, six initial source adapters, and shared packages for the SDKs and protocol types.

The document is deliberately concrete. An engineering team should be able to start sprint planning from it on Monday.

---

## Architecture Principles

These are the non-negotiable design constraints that drive every concrete decision below. When in doubt, return here.

1. **The customer's systems remain the source of truth.** We do not duplicate, migrate, or take ownership of business data. Salesforce records live in Salesforce. Warehouse rows live in the warehouse. OpenFoundry stores ontology metadata, action definitions, policies, audit events, and a small write-edit overlay only.

2. **Every change is a typed Action.** Raw writes are not allowed at any layer. Actions are the only sanctioned mutation path. Agents, humans, and Functions all submit Actions; the Action Service validates, evaluates policy, executes against the relevant source system, and emits audit events.

3. **The ontology is the API.** Object types, property types, link types, and action types compile into an OSDK (TypeScript + Python) and into MCP tools. Internal services consume the ontology via this same surface; there are no "internal" raw-SQL backdoors.

4. **Permissions are evaluated by a single Policy Decision Point.** Every read and every action call passes through the same PDP (OpenFGA). The customer's IdP is federated for user identity; policy decisions reason about user + group + agent + object + action attributes uniformly.

5. **All events are observable, all traffic is audited.** Every action submission, every policy decision, every read, every error becomes an audit event. Events ship to the customer's SIEM via OpenTelemetry. The audit log is a first-class queryable artifact.

6. **Multi-tenant by default; BYOC by month 12.** v1 ships as multi-tenant SaaS on AWS, with per-customer Kubernetes namespaces and per-customer Postgres schemas. BYOC (customer-deployed control plane / data plane separation) is a year-2 capability gated on a real F500 customer demanding it.

7. **TypeScript everywhere it makes sense.** Backend services in TypeScript (Node 22 LTS + Fastify) for consistency with the OSDK and the frontend. Python only inside the Functions runtime (for customer code) and in the OSDK Python client. Go only if we hit a real performance ceiling in v2.

8. **Buy before build.** OpenFGA (policy), Inngest (workflows), workerd (Functions runtime), Airbyte (connectors for Mode B), Postgres (everything stateful), Cloudflare (edge), Anthropic MCP SDK (agent protocol). Five custom services. Everything else composed.

9. **One monorepo, one deploy.** Turborepo + pnpm workspaces. Every service and adapter lives in one repo. Atomic cross-cutting changes are the norm.

10. **No customer-specific code in `main`.** Customer-specific configurations (ontology definitions, policy bundles, connector credentials) live in a per-customer config repo that the platform consumes at runtime. The platform code is one binary, multi-tenant.

---

## C4 Level 1 — System Context

The system in its environment, showing the people and external systems OpenFoundry interacts with.

```
                                ┌────────────────────────┐
                                │   FDE / Customer SME   │
                                │   (authors ontology)   │
                                └───────────┬────────────┘
                                            │ FDE Console
                                            ▼
┌───────────────────┐                ┌──────────────────────────────┐
│ AI Agents (Claude,│                │                              │      ┌──────────────────────┐
│ Cursor, ChatGPT,  │ ◄──── MCP ────►│        OpenFoundry           │ ◄──► │   Customer IdP       │
│ internal LangChain│                │     (control plane only)     │      │ (Okta/Entra/Auth0)   │
└─────────┬─────────┘                │                              │      └──────────────────────┘
          │                          │  - Ontology definitions      │
          │ OSDK                     │  - Action runtime            │      ┌──────────────────────┐
          ▼                          │  - Policy engine             │ ◄──► │   Customer SIEM      │
┌───────────────────┐                │  - Audit log forwarder       │      │ (Splunk/Datadog)     │
│ Customer Internal │ ◄──── OSDK ───►│  - MCP gateway               │      └──────────────────────┘
│ Apps (Next.js,    │                │  - OSDK generator            │
│ FastAPI, etc.)    │                │  - Federation services       │
└───────────────────┘                │                              │
                                     │  NO customer business data.  │
                                     │  Metadata + audit only.      │
                                     └─────────┬────────────────────┘
                                               │
                            ┌──────────────────┼──────────────────────────────────┐
                            │                  │                                  │
                            ▼                  ▼                                  ▼
                  ┌──────────────────┐  ┌──────────────────┐         ┌──────────────────┐
                  │ Customer         │  │ Customer Source  │         │ Customer Cloud   │
                  │ Warehouse        │  │ Systems          │         │ Storage          │
                  │ (Snowflake,      │  │ (Salesforce,     │         │ (S3, ADLS, GCS)  │
                  │ Databricks,      │  │ ServiceNow,      │         │ + Iceberg tables │
                  │ BigQuery)        │  │ Workday, EHR)    │         │                  │
                  └──────────────────┘  └──────────────────┘         └──────────────────┘
                       (reads via            (reads + writes              (reads via
                       federated query)      via REST/SOQL APIs)          Iceberg / S3)
```

**Actors:**

- **FDE / Customer SME** — Tenex's forward-deployed engineers and customer subject-matter experts who author the ontology, policies, and Workshop modules. They access OpenFoundry through the FDE Console.
- **AI Agents** — external agent runtimes (Claude Code, Cursor, ChatGPT Enterprise, internal LangChain/CrewAI deployments) that consume the ontology via MCP.
- **Customer Internal Apps** — Next.js, FastAPI, mobile, or any other customer-built software that consumes the ontology via the generated OSDK.

**External Systems:**

- **Customer IdP** (Okta, Microsoft Entra, Auth0, Ping) — source of user identity. Federated via OIDC.
- **Customer SIEM** (Splunk, Datadog, Sentinel, Sumo) — receives audit events via OpenTelemetry.
- **Customer Warehouse** (Snowflake, Databricks, BigQuery, Redshift) — source of analytical data. Read via federated query or per-system adapters.
- **Customer Source Systems** (Salesforce, ServiceNow, Workday, NetSuite, SAP, Epic/Cerner) — sources of operational data. Reads and writes go via their native APIs.
- **Customer Cloud Storage** (S3, ADLS, GCS + Iceberg) — for cross-source query and ML workloads. Mode B materialization lives here when needed.

---

## C4 Level 2 — Container Diagram

The deployable units. Every box below is a separately deployable container (Kubernetes Deployment or StatefulSet). All run inside OpenFoundry's AWS account in v1.

```
╔══════════════════════════════════════════════════════════════════════════════════════════╗
║                          OPENFOUNDRY — CONTAINER ARCHITECTURE                              ║
╠══════════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                            ║
║   EDGE LAYER                                                                               ║
║   ┌──────────────────────────┐    ┌──────────────────────────────────────────────────┐   ║
║   │ Cloudflare (CDN + WAF)   │    │ Identity Federation Service                       │   ║
║   │ + Cloudflare Access      │    │ (Hono on Node 22)                                 │   ║
║   │ (DDoS, bot, rate limit)  │    │ - OIDC client to customer IdPs                    │   ║
║   └──────────────────────────┘    │ - Token exchange (RFC 8693)                       │   ║
║                                   │ - Issues OpenFoundry session JWTs                 │   ║
║                                   │ - Manages OAuth flows for source systems          │   ║
║                                   └──────────────────────────────────────────────────┘   ║
║                                                                                            ║
║   PRESENTATION LAYER                                                                       ║
║   ┌──────────────────────────────┐  ┌────────────────────────────────────────────────┐   ║
║   │ FDE Console (Next.js 15)     │  │ MCP Gateway (Fastify + Anthropic MCP SDK)      │   ║
║   │ - Ontology authoring UI      │  │ - Multi-tenant MCP endpoints (one per customer)│   ║
║   │ - Policy editor              │  │ - Tool catalog auto-derived from ontology      │   ║
║   │ - Audit log explorer         │  │ - RFC 8707 audience binding                    │   ║
║   │ - Customer dashboards        │  │ - CIMD-based client registration               │   ║
║   │ - Connector admin            │  │ - Per-user OAuth scope translation             │   ║
║   │ - Workshop module preview    │  │ - Routes to Query Service / Action Service     │   ║
║   └──────────────────────────────┘  └────────────────────────────────────────────────┘   ║
║                                                                                            ║
║   APPLICATION SERVICES (custom-built — the 5 services that matter)                         ║
║   ┌──────────────────────────────┐  ┌────────────────────────────────────────────────┐   ║
║   │ Ontology Service             │  │ Action Service                                  │   ║
║   │ (Fastify + Zod + Postgres)   │  │ (Fastify + Inngest + Postgres + Source Adapters)│   ║
║   │ - CRUD over object/property/ │  │ - Action submission endpoint                    │   ║
║   │   link/action type defs      │  │ - Parameter validation (Zod schemas)            │   ║
║   │ - Versioning via Git-style   │  │ - Submission criteria evaluation (Functions)    │   ║
║   │   commits + content hashing  │  │ - Policy check via Policy Service               │   ║
║   │ - Emits OpenAPI specs        │  │ - Source-system execution via adapters          │   ║
║   │ - Publishes type events to   │  │ - Side effects (webhooks, notifications)        │   ║
║   │   NATS for downstream codegen│  │ - Emits audit events                            │   ║
║   └──────────────────────────────┘  └────────────────────────────────────────────────┘   ║
║                                                                                            ║
║   ┌──────────────────────────────┐  ┌────────────────────────────────────────────────┐   ║
║   │ Query Service                │  │ Functions Runtime (Cloudflare workerd self-host)│   ║
║   │ (Fastify + Trino + Postgres) │  │ - V8 isolates for TypeScript Functions          │   ║
║   │ - Ontology-typed queries     │  │ - Modal for Python Functions                    │   ║
║   │ - Translates to per-source   │  │ - OSDK auto-injected into each isolate          │   ║
║   │   queries via adapters       │  │ - Resource quotas per tenant                    │   ║
║   │ - Optional Trino federation  │  │ - Audit events on every invocation              │   ║
║   │   for cross-source joins     │  │                                                 │   ║
║   │ - Result materialization to  │  │                                                 │   ║
║   │   Ontology objects           │  │                                                 │   ║
║   │ - Cell-level masking         │  │                                                 │   ║
║   └──────────────────────────────┘  └────────────────────────────────────────────────┘   ║
║                                                                                            ║
║   ┌──────────────────────────────┐                                                         ║
║   │ OSDK Generator               │                                                         ║
║   │ (TS codegen + Inngest job)   │                                                         ║
║   │ - Watches Ontology Service   │                                                         ║
║   │   events                     │                                                         ║
║   │ - Emits OpenAPI from         │                                                         ║
║   │   ontology metadata          │                                                         ║
║   │ - Runs openapi-typescript,   │                                                         ║
║   │   openapi-python-client      │                                                         ║
║   │ - Publishes versioned npm /  │                                                         ║
║   │   pip packages to private    │                                                         ║
║   │   artifact registry          │                                                         ║
║   └──────────────────────────────┘                                                         ║
║                                                                                            ║
║   POLICY + AUDIT (composed from open-source)                                               ║
║   ┌──────────────────────────────┐  ┌────────────────────────────────────────────────┐   ║
║   │ Policy Service (OpenFGA)     │  │ Audit Service (Fastify + Postgres + OTel)      │   ║
║   │ - Self-hosted OpenFGA        │  │ - Append-only event store                       │   ║
║   │ - Per-tenant authorization   │  │ - OTel collector forwards to customer SIEM      │   ║
║   │   model                      │  │ - Queryable via FDE Console + OSDK              │   ║
║   │ - Decisions in <10ms p99     │  │ - Retention configurable per customer           │   ║
║   │ - Integrates with customer   │  │                                                 │   ║
║   │   IdP groups via SCIM        │  │                                                 │   ║
║   └──────────────────────────────┘  └────────────────────────────────────────────────┘   ║
║                                                                                            ║
║   LINEAGE + METADATA                                                                       ║
║   ┌──────────────────────────────┐  ┌────────────────────────────────────────────────┐   ║
║   │ Lineage Service              │  │ Connector Manager                               │   ║
║   │ (Marquez + custom propagator)│  │ (Airbyte self-hosted + custom orchestration)    │   ║
║   │ - Marquez OpenLineage server │  │ - Manages Mode B materialization sync           │   ║
║   │ - Marking propagation logic  │  │ - Schedules Iceberg writes                      │   ║
║   │ - Subscribes to dbt / Spark  │  │ - Schema introspection for new sources          │   ║
║   │   OpenLineage events         │  │ - Surfaces source schemas to Ontology Service   │   ║
║   │ - Updates Ontology marking   │  │   for auto-inference                            │   ║
║   │   inheritance                │  │                                                 │   ║
║   └──────────────────────────────┘  └────────────────────────────────────────────────┘   ║
║                                                                                            ║
║   SOURCE ADAPTERS (one container per source system, deployed per customer as needed)       ║
║   ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌────────────┐ ┌──────┐║
║   │ Salesforce  │ │ Snowflake   │ │ Databricks  │ │ ServiceNow  │ │ Workday    │ │ S3   │║
║   │ Adapter     │ │ Adapter     │ │ Adapter     │ │ Adapter     │ │ Adapter    │ │Adapt.│║
║   │ (Node+jsforce│ │ (Node+sf-jdbc│ │ (Node+rest) │ │ (Node+sn-rest│ │ (Node+wd-r)│ │(Node)│║
║   └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ └────────────┘ └──────┘║
║                                                                                            ║
║   PERSISTENCE                                                                              ║
║   ┌──────────────────────────────┐  ┌────────────────────────────────────────────────┐   ║
║   │ Postgres 16                  │  │ Redis 7 (Upstash or ElastiCache)                │   ║
║   │ (RDS Multi-AZ; per-customer  │  │ - Caching of policy decisions (<60s TTL)        │   ║
║   │ schemas in shared cluster)   │  │ - Rate limit counters                           │   ║
║   │ - ontology metadata          │  │ - MCP session state                             │   ║
║   │ - audit log (partitioned)    │  │ - OAuth state and nonces                        │   ║
║   │ - policy bundles             │  │                                                 │   ║
║   │ - user-edit overlays         │  │                                                 │   ║
║   │ - encrypted source credentials│ │                                                 │   ║
║   │ - workshop module definitions│  │                                                 │   ║
║   └──────────────────────────────┘  └────────────────────────────────────────────────┘   ║
║                                                                                            ║
║   ┌──────────────────────────────┐  ┌────────────────────────────────────────────────┐   ║
║   │ S3 (customer-region buckets) │  │ NATS JetStream (event bus)                      │   ║
║   │ - Generated OSDK artifacts   │  │ - Action emitted events                         │   ║
║   │ - Workshop bundles           │  │ - Audit events                                  │   ║
║   │ - Ontology snapshots         │  │ - Type system changes (triggers codegen)        │   ║
║   │ - Lineage snapshots          │  │ - Lineage events                                │   ║
║   └──────────────────────────────┘  └────────────────────────────────────────────────┘   ║
║                                                                                            ║
║   ASYNC WORKFLOW                                                                           ║
║   ┌──────────────────────────────┐                                                         ║
║   │ Inngest (managed)            │                                                         ║
║   │ - OSDK codegen jobs          │                                                         ║
║   │ - Action retries / DLQ       │                                                         ║
║   │ - Lineage propagation jobs   │                                                         ║
║   │ - Ontology refinement (LLM-  │                                                         ║
║   │   assisted suggestions)      │                                                         ║
║   └──────────────────────────────┘                                                         ║
║                                                                                            ║
╚══════════════════════════════════════════════════════════════════════════════════════════╝
```

### Container Catalog

| Container | Tech | Purpose | Build vs Buy |
|-----------|------|---------|--------------|
| **FDE Console** | Next.js 15 + React 19 + tRPC | UI for ontology authoring, policies, audit, dashboards | Build |
| **MCP Gateway** | Fastify + Anthropic MCP SDK | Agent-facing entrypoint; multi-tenant MCP endpoints | Build (thin wrapper over SDK) |
| **Identity Federation Service** | Hono + WorkOS SDK | OIDC client to customer IdPs; OAuth flows for source systems | Build |
| **Ontology Service** | Fastify + Zod + Postgres | CRUD over type definitions; OpenAPI emission | Build |
| **Action Service** | Fastify + Inngest + Postgres | Action submission, validation, execution | Build |
| **Query Service** | Fastify + Trino client + adapters | Ontology-typed reads; federated query when needed | Build |
| **Functions Runtime** | Cloudflare workerd (self-hosted) + Modal | V8 + Python execution for customer Functions | Buy + wrap |
| **OSDK Generator** | Node + openapi-typescript + openapi-python-client | Generates typed SDKs from ontology | Build (thin codegen) |
| **Policy Service** | OpenFGA (self-hosted) | Authorization decisions | Buy |
| **Audit Service** | Fastify + Postgres + OpenTelemetry | Audit event store and SIEM forwarder | Build |
| **Lineage Service** | Marquez (OpenLineage server) + custom propagator | Lineage graph + marking propagation | Buy + build |
| **Connector Manager** | Airbyte (self-hosted) + custom orchestration | Mode B sync, schema introspection | Buy + wrap |
| **Source Adapters** | Node + per-system SDKs | Read/write to individual source systems | Build (one per source) |
| **Postgres 16** | AWS RDS Multi-AZ | Primary persistence | Buy |
| **Redis 7** | Upstash | Cache, rate limiting, session state | Buy |
| **NATS JetStream** | Self-hosted | Event bus | Buy |
| **Inngest** | Managed | Async workflows, retries, scheduled jobs | Buy |
| **S3** | AWS | Artifact and snapshot storage | Buy |
| **Cloudflare** | Managed | CDN, WAF, DDoS, edge auth | Buy |

**Custom services to build: 5** (Ontology, Action, Query, OSDK Generator, Lineage propagation logic). Plus 1 frontend (FDE Console), 1 gateway (MCP), 1 federation service, 1 audit service, and per-source adapters. Everything stateful is bought.

---

## C4 Level 3 — Component Diagrams

For each major container, the internal structure. This is where the engineering team gets concrete.

### 3.1 Ontology Service

```
┌──────────────────────────────────────────────────────────────────┐
│ Ontology Service (Fastify, Node 22, single Docker image)          │
├──────────────────────────────────────────────────────────────────┤
│                                                                    │
│  Routes                                                            │
│  ├─ POST   /v1/ontology/object-types        (create/update)        │
│  ├─ GET    /v1/ontology/object-types/:id    (read)                 │
│  ├─ POST   /v1/ontology/action-types        (create/update)        │
│  ├─ GET    /v1/ontology/action-types/:id    (read)                 │
│  ├─ POST   /v1/ontology/property-types      (create/update)        │
│  ├─ POST   /v1/ontology/link-types          (create/update)        │
│  ├─ POST   /v1/ontology/markings            (create/update)        │
│  ├─ GET    /v1/ontology/openapi.json        (compiled spec)        │
│  ├─ GET    /v1/ontology/describe            (introspection)        │
│  ├─ POST   /v1/ontology/commit              (commit + version)     │
│  └─ GET    /v1/ontology/history             (commit log)           │
│                                                                    │
│  Components                                                        │
│  ├─ TypeRegistry — in-memory cache of compiled ontology            │
│  ├─ VersionManager — content-addressed commits in Postgres         │
│  ├─ OpenAPIEmitter — generates OpenAPI 3.1 from ontology metadata  │
│  ├─ ZodSchemaCompiler — emits runtime Zod schemas for validation   │
│  ├─ MarkingResolver — computes effective markings per object       │
│  ├─ EventPublisher — NATS publisher for type-changed events        │
│  └─ AuthorizationGuard — gates writes to ontology metadata itself  │
│                                                                    │
│  Storage                                                           │
│  └─ Postgres tables:                                               │
│      ontology_commits (id, customer_id, sha, parent_sha, author,   │
│                        message, created_at, payload JSONB)          │
│      object_types (id, commit_id, name, schema JSONB, markings[])   │
│      property_types (id, commit_id, name, type, constraints JSONB)  │
│      link_types (id, commit_id, name, source, target, kind)         │
│      action_types (id, commit_id, name, params JSONB, rules JSONB,  │
│                    criteria JSONB, side_effects JSONB)              │
│      markings (id, commit_id, name, kind, inherits_from)            │
│                                                                    │
│  Events emitted to NATS                                            │
│  ├─ ontology.commit.created                                        │
│  ├─ ontology.object_type.changed                                   │
│  ├─ ontology.action_type.changed                                   │
│  └─ ontology.marking.changed                                       │
│                                                                    │
└──────────────────────────────────────────────────────────────────┘
```

**Key design choices:**

- **Versioning is content-addressed** like Git. Every ontology change creates a new commit with a SHA, a parent SHA, and a payload. Rolling back is `git checkout <sha>` — write a new commit pointing to an old payload.
- **Validation is Zod-compiled at runtime.** Object types and action types compile into Zod schemas; the Action Service uses those schemas to validate incoming requests.
- **OpenAPI is the compiled output.** Whenever an ontology commit is created, the OpenAPI Emitter publishes a fresh OpenAPI 3.1 document; the OSDK Generator listens for those events and rebuilds clients.

### 3.2 Action Service

```
┌──────────────────────────────────────────────────────────────────┐
│ Action Service (Fastify, Node 22)                                 │
├──────────────────────────────────────────────────────────────────┤
│                                                                    │
│  Routes                                                            │
│  ├─ POST   /v1/actions/:actionName/submit                          │
│  ├─ POST   /v1/actions/:actionName/dry-run  (no side effects)      │
│  ├─ GET    /v1/actions/:submissionId/status                        │
│  └─ GET    /v1/actions/:submissionId/audit                         │
│                                                                    │
│  Pipeline (per submission)                                         │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │ 1. AuthN — verify session JWT from Identity Federation        │ │
│  │ 2. Load — fetch action_type definition from Ontology Service  │ │
│  │ 3. Validate — Zod schema on parameters                        │ │
│  │ 4. Authorize — Policy Service check (PDP)                     │ │
│  │ 5. Criteria — evaluate submission criteria (may call Functions│ │
│  │    Runtime; runs as the submitting user)                      │ │
│  │ 6. Plan — translate rules into source-system operations       │ │
│  │ 7. Execute — call relevant Source Adapter(s) transactionally  │ │
│  │ 8. Side Effects — fire webhooks, notifications, audit events  │ │
│  │ 9. Respond — return status + audit submission ID              │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                    │
│  Components                                                        │
│  ├─ SubmissionController — request handler, orchestrates pipeline  │
│  ├─ ActionTypeLoader — pulls action def from Ontology Service      │
│  ├─ ParameterValidator — Zod-based validation                      │
│  ├─ PolicyClient — gRPC client to Policy Service                   │
│  ├─ CriteriaEvaluator — invokes Functions Runtime for predicates   │
│  ├─ RulePlanner — translates declarative rules to adapter calls    │
│  ├─ AdapterDispatcher — routes to the right Source Adapter         │
│  ├─ SideEffectRunner — webhooks + notifications via Inngest        │
│  ├─ AuditEmitter — writes to Audit Service + NATS                  │
│  └─ DryRunSimulator — runs steps 2-6 only, returns predicted plan  │
│                                                                    │
│  Idempotency                                                       │
│  - Every submission has a client-provided idempotency_key          │
│  - Replays return cached result for 24h                            │
│  - Implemented via Postgres UNIQUE constraint                      │
│                                                                    │
│  Transactional Boundary                                            │
│  - Reads: Snowflake/Databricks queries (read-only; no rollback)    │
│  - Writes: per-adapter; usually NOT distributed-transactional      │
│  - Saga pattern via Inngest for multi-step actions                 │
│  - Compensating actions defined in action_type.rules.compensations │
│                                                                    │
└──────────────────────────────────────────────────────────────────┘
```

**Key design choices:**

- **No distributed transactions across source systems.** Salesforce + ServiceNow + Workday do not support 2PC together. We use saga patterns with compensating actions, orchestrated by Inngest. If a multi-step action fails halfway, Inngest runs the reverse adapter calls.
- **Dry-run is a first-class concept.** Agents can call `/dry-run` to preview an action's effects without executing. The MCP Gateway exposes this as a separate tool for safety-critical actions.
- **Submission criteria can call Functions.** A criterion like "amount must be under the user's approval limit" calls a Function that queries the user's profile. This is how business logic stays out of action_type definitions.

### 3.3 Query Service

```
┌──────────────────────────────────────────────────────────────────┐
│ Query Service (Fastify, Node 22)                                  │
├──────────────────────────────────────────────────────────────────┤
│                                                                    │
│  Routes                                                            │
│  ├─ POST   /v1/query/objects                (object-set query)     │
│  ├─ GET    /v1/query/objects/:id            (single object)        │
│  ├─ POST   /v1/query/aggregate              (sum/count/avg)        │
│  ├─ POST   /v1/query/semantic               (embedding search)     │
│  └─ POST   /v1/query/cross-source           (federated via Trino)  │
│                                                                    │
│  Query Plan                                                        │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │ 1. AuthN — verify session JWT                                 │ │
│  │ 2. Parse — ontology-typed query (object type, filter, fields) │ │
│  │ 3. Policy filter — augment query with permission predicates   │ │
│  │ 4. Plan — single-source or cross-source?                      │ │
│  │    ├─ Single: route to one Source Adapter                     │ │
│  │    └─ Cross: route to Trino via per-source connectors         │ │
│  │ 5. Execute — adapter returns raw rows                         │ │
│  │ 6. Materialize — wrap raw rows in Ontology object shape       │ │
│  │ 7. Mask — apply cell-level masking from markings              │ │
│  │ 8. Return — paginated, ontology-typed JSON                    │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                    │
│  Components                                                        │
│  ├─ QueryController — request handler                              │
│  ├─ QueryPlanner — single vs federated routing                     │
│  ├─ PolicyAugmenter — adds row-level predicates from PDP           │
│  ├─ AdapterDispatcher — same as Action Service                     │
│  ├─ TrinoClient — federated query for cross-source                 │
│  ├─ MaterializationLayer — raw rows → typed Ontology objects       │
│  ├─ MaskingEngine — cell-level redaction by marking                │
│  └─ EmbeddingClient — pgvector for semantic search                 │
│                                                                    │
│  Caching                                                           │
│  - Read-through cache in Redis for hot queries (60s TTL)           │
│  - Per-tenant cache namespace                                      │
│  - Invalidation on action submissions via NATS                     │
│                                                                    │
└──────────────────────────────────────────────────────────────────┘
```

**Key design choices:**

- **Cell-level masking happens at the Query Service, not the adapter.** Adapters return raw data; the Query Service applies markings. This keeps adapters simple and ensures masking is uniform.
- **Policy is enforced as query augmentation, not post-filter.** When a user queries `Patient where status = 'admitted'`, the PDP returns a predicate like `(department_id IN [user.departments])` that gets injected into the adapter call. Faster than fetching everything and filtering after.
- **Cross-source queries use Trino.** Trino's connector ecosystem covers Snowflake, Databricks, BigQuery, Postgres, Salesforce, MongoDB, Elasticsearch — everything we need. Trino runs as a separate StatefulSet, only invoked when a query spans sources.

### 3.4 MCP Gateway

```
┌──────────────────────────────────────────────────────────────────┐
│ MCP Gateway (Fastify + Anthropic MCP SDK)                         │
├──────────────────────────────────────────────────────────────────┤
│                                                                    │
│  Endpoints (per customer)                                          │
│  ├─ https://{tenant}.mcp.openfoundry.io/sse  (SSE transport)       │
│  ├─ /.well-known/oauth-protected-resource    (RFC 9728)            │
│  ├─ /.well-known/oauth-authorization-server  (RFC 8414, proxied)   │
│  └─ /v1/mcp/tools                            (catalog introspection)│
│                                                                    │
│  Auth Flow (per MCP spec 2025-11-25)                               │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │ 1. Agent client hits /sse without token                       │ │
│  │ 2. Server returns 401 + WWW-Authenticate: Bearer              │ │
│  │    resource_metadata="https://.../oauth-protected-resource"   │ │
│  │ 3. Client fetches metadata; discovers AS at                   │ │
│  │    Identity Federation Service                                │ │
│  │ 4. Client registers via CIMD (URL-based client ID)            │ │
│  │ 5. Client gets auth code via PKCE flow                        │ │
│  │ 6. Client exchanges code for access token with                │ │
│  │    resource=https://{tenant}.mcp.openfoundry.io               │ │
│  │ 7. Token's `aud` claim binds to this MCP server               │ │
│  │ 8. Subsequent calls include bearer token; server validates    │ │
│  │    aud + scope + iss                                          │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                    │
│  Tool Catalog                                                      │
│  - Auto-derived from Ontology Service                              │
│  - For each object_type: query, lookup, search_around              │
│  - For each action_type: submit, dry_run                           │
│  - Per-tool descriptions from action_type.agent_description field  │
│  - Per-tool schemas as JSON Schema (compiled from Zod)             │
│                                                                    │
│  Components                                                        │
│  ├─ SSETransport — Anthropic SDK MCP SSE server                    │
│  ├─ ToolRegistry — refreshes catalog on ontology changes           │
│  ├─ AuthBridge — translates MCP OAuth token to internal JWT        │
│  ├─ ToolDispatcher — routes tool calls to Query or Action Service  │
│  ├─ RateLimiter — Redis-backed per-token rate limits               │
│  └─ TelemetryEmitter — every tool call → audit event               │
│                                                                    │
└──────────────────────────────────────────────────────────────────┘
```

**Key design choices:**

- **One MCP endpoint per customer.** `acme.mcp.openfoundry.io`. Routing happens at the Cloudflare edge based on subdomain. Multi-tenancy is namespace-level at Postgres + cluster-level via Kubernetes namespace.
- **No DCR; CIMD only.** Per the November 2025 MCP spec revision. Client registration is via URL-published metadata documents.
- **Audience binding is mandatory.** Tokens issued for `acme.mcp.openfoundry.io` are rejected at `beta.mcp.openfoundry.io`. Enforced at the AuthBridge.

### 3.5 OSDK Generator

```
┌──────────────────────────────────────────────────────────────────┐
│ OSDK Generator (Node + Inngest job)                               │
├──────────────────────────────────────────────────────────────────┤
│                                                                    │
│  Trigger                                                           │
│  └─ NATS subscription: ontology.commit.created                     │
│                                                                    │
│  Pipeline (per commit)                                             │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │ 1. Fetch ontology snapshot at commit SHA                      │ │
│  │ 2. Emit OpenAPI 3.1 spec                                      │ │
│  │ 3. Run openapi-typescript → @customer/sdk-ts                  │ │
│  │ 4. Run openapi-python-client → customer-sdk-python            │ │
│  │ 5. Add hand-written runtime layer:                            │ │
│  │    - applyAction() with idempotency keys                      │ │
│  │    - client(ObjectType).where(...).fetchPage()                │ │
│  │    - Automatic auth header injection                          │ │
│  │ 6. Compile TypeScript                                         │ │
│  │ 7. Run tsc --declaration to emit .d.ts                        │ │
│  │ 8. Publish to private npm registry (Verdaccio or AWS CodeArtifact)│
│  │ 9. Publish to private PyPI                                    │ │
│  │ 10. Notify FDE Console: new SDK version available             │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                    │
│  Versioning                                                        │
│  - npm version = "{ontology_commit_sha[0:7]}-{semver}"             │
│  - Each ontology commit produces an immutable SDK version          │
│  - Customer apps pin to specific versions; rolling forward is opt-in│
│                                                                    │
│  Distribution                                                      │
│  - Private npm via AWS CodeArtifact (per-customer namespace)       │
│  - Private PyPI via AWS CodeArtifact                               │
│  - Customer installs with org-scoped credentials issued by FDE     │
│                                                                    │
└──────────────────────────────────────────────────────────────────┘
```

### 3.6 Source Adapter (Generic Pattern)

Every Source Adapter follows the same interface. Below is the contract; the Salesforce-specific implementation is in §8.

```
┌──────────────────────────────────────────────────────────────────┐
│ Source Adapter (per source system, Node 22)                       │
├──────────────────────────────────────────────────────────────────┤
│                                                                    │
│  Contract (gRPC service, defined in packages/protocol)             │
│  ├─ Introspect(ConnectionConfig) → SchemaDescriptor                │
│  ├─ Query(ObjectType, Filter, Fields) → AsyncIterable<Row>         │
│  ├─ Lookup(ObjectType, ID) → Row | null                            │
│  ├─ Execute(ActionRules, Parameters, Identity) → ExecutionResult   │
│  ├─ Subscribe(ChangeStreamSpec) → AsyncIterable<ChangeEvent>       │
│  └─ HealthCheck() → AdapterHealth                                  │
│                                                                    │
│  Per-adapter responsibilities                                      │
│  ├─ Auth — OAuth refresh, token caching, per-customer credentials  │
│  ├─ Rate limiting — respect source-system limits                   │
│  ├─ Pagination — cursor handling                                   │
│  ├─ Type mapping — source columns ↔ ontology property types        │
│  ├─ Error normalization — map source errors to standard codes      │
│  └─ Idempotency — for writes, use source-system idempotency tokens │
│                                                                    │
│  NOT the adapter's job                                             │
│  ├─ Policy decisions (Action / Query Service does this)            │
│  ├─ Audit logging (Action / Query Service does this)               │
│  ├─ Masking (Query Service does this)                              │
│  └─ Cross-source orchestration (Action Service does this)          │
│                                                                    │
└──────────────────────────────────────────────────────────────────┘
```

**Why adapters are containers, not libraries:** because adapters have different dependencies (jsforce, snowflake-sdk, mongodb, etc.), different scaling profiles, and different failure domains. Salesforce adapter going down should not break the Snowflake adapter. Each adapter is its own deployable Docker image. The Action Service and Query Service dispatch to adapters via gRPC.

### 3.7 Policy Service (OpenFGA wrapper)

```
┌──────────────────────────────────────────────────────────────────┐
│ Policy Service (OpenFGA self-hosted + thin Fastify wrapper)       │
├──────────────────────────────────────────────────────────────────┤
│                                                                    │
│  Routes                                                            │
│  ├─ POST   /v1/check                  (single decision)            │
│  ├─ POST   /v1/batch-check            (multiple in one call)       │
│  ├─ POST   /v1/list-objects           (PDP for read augmentation)  │
│  ├─ POST   /v1/expand                 (debug visualization)        │
│  └─ POST   /v1/write                  (update relation tuples)     │
│                                                                    │
│  OpenFGA Authorization Model (per customer)                        │
│  - Types: user, group, role, agent, object_type, action_type       │
│  - Relations: member, owner, viewer, editor, can_invoke,           │
│    can_read, can_write                                             │
│  - Computed relations for inheritance:                             │
│    can_invoke = direct_grant OR via_role OR via_group              │
│                                                                    │
│  Inputs (per request)                                              │
│  ├─ subject (user URI or agent URI)                                │
│  ├─ relation (e.g. can_invoke)                                     │
│  ├─ object (action_type URI or object instance URI)                │
│  └─ context (agent capabilities, time, IP)                         │
│                                                                    │
│  Group / Role Sync                                                 │
│  ├─ SCIM endpoint receives updates from customer IdP               │
│  ├─ Group memberships sync into OpenFGA relation tuples            │
│  ├─ Tenex Console UI for role definitions                          │
│  └─ Customer-defined roles compile to OpenFGA model fragments      │
│                                                                    │
│  Cached decisions in Redis                                         │
│  - 60s TTL per (subject, relation, object) tuple                   │
│  - Invalidated on relation writes                                  │
│  - p99 with cache: <2ms                                            │
│  - p99 without cache: <10ms                                        │
│                                                                    │
└──────────────────────────────────────────────────────────────────┘
```

**Why OpenFGA over Cedar:** OpenFGA is Zanzibar-style (relation-based, graph-native), which fits the ontology's link-type structure. Cedar is policy-language-based, better for AWS-centric IAM patterns but worse for "Alice can edit Project X because she's in the team that owns the parent folder." Plus OpenFGA is Auth0/Okta-backed and the agent identity story is converging on this model.

### 3.8 Functions Runtime

```
┌──────────────────────────────────────────────────────────────────┐
│ Functions Runtime                                                  │
├──────────────────────────────────────────────────────────────────┤
│                                                                    │
│  Two runtimes, one interface                                       │
│                                                                    │
│  TypeScript: Cloudflare workerd (self-hosted)                      │
│  ├─ V8 isolates with full TypeScript runtime                       │
│  ├─ Memory limit: 128 MB / isolate                                 │
│  ├─ CPU limit: 30s wall / 50ms CPU per request                     │
│  ├─ No file I/O, no arbitrary network (proxied via Sources)        │
│  ├─ OSDK pre-loaded                                                │
│  └─ Auth context injected as a global                              │
│                                                                    │
│  Python: Modal                                                     │
│  ├─ Per-Function Modal app                                         │
│  ├─ Containerized; supports numpy/pandas/scikit-learn              │
│  ├─ Cold start ~1-2s; warm start <100ms                            │
│  ├─ OSDK Python pre-installed                                      │
│  └─ Auth context via env var                                       │
│                                                                    │
│  Function Definition                                               │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │ // packages/sdk-ts/functions.ts                               │ │
│  │ export const calculateDiscount = Function({                   │ │
│  │   inputs: { order: Order },                                   │ │
│  │   output: z.number(),                                         │ │
│  │   handler: async ({ order, client }) => {                     │ │
│  │     const customer = await client(order.placed_by).lookup();  │ │
│  │     const history = await client(Order)                       │ │
│  │       .where(o => o.placed_by === customer.id)                │ │
│  │       .aggregate(o => o.total.sum());                         │ │
│  │     return history > 100_000 ? 0.15 : 0.05;                   │ │
│  │   }                                                            │ │
│  │ });                                                            │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                    │
│  Lifecycle                                                         │
│  - Customer pushes Functions to a Git repo (FDE-managed)            │
│  - CI builds and deploys to workerd / Modal                         │
│  - Action Service invokes via gRPC                                  │
│  - Every invocation emits audit event                               │
│                                                                    │
└──────────────────────────────────────────────────────────────────┘
```

### 3.9 Lineage Service

```
┌──────────────────────────────────────────────────────────────────┐
│ Lineage Service (Marquez + custom Marking Propagator)             │
├──────────────────────────────────────────────────────────────────┤
│                                                                    │
│  Marquez (open-source OpenLineage server)                          │
│  ├─ Receives OpenLineage events from:                              │
│  │   - dbt (every model run)                                       │
│  │   - Spark jobs (via OpenLineage Spark agent)                    │
│  │   - Airflow / Dagster / Prefect (native integrations)           │
│  │   - Action Service (every successful action that writes)        │
│  │   - Customer-instrumented pipelines                             │
│  ├─ Stores graph: datasets → jobs → derived datasets               │
│  └─ Exposes REST API for graph traversal                           │
│                                                                    │
│  Marking Propagator (custom service)                               │
│  ├─ Subscribes to Marquez events                                   │
│  ├─ For each new derived dataset:                                  │
│  │   1. Look up upstream datasets                                  │
│  │   2. Resolve their markings from Ontology Service               │
│  │   3. Compute union of inherited markings                        │
│  │   4. Apply to derived dataset's object type                     │
│  │   5. Unless ontology has explicit stop_propagating(marking)      │
│  ├─ Emits ontology.marking.changed events                          │
│  └─ FDE Console shows lineage graph + marking flow                 │
│                                                                    │
│  Simulation Mode                                                   │
│  - FDE can preview marking changes before committing               │
│  - "What if I add PII to dataset A?" → tool shows all derived       │
│    datasets that would inherit, plus downstream apps affected      │
│                                                                    │
└──────────────────────────────────────────────────────────────────┘
```

### 3.10 Identity Federation Service

```
┌──────────────────────────────────────────────────────────────────┐
│ Identity Federation Service (Hono on Node 22)                     │
├──────────────────────────────────────────────────────────────────┤
│                                                                    │
│  Three identity flows                                              │
│                                                                    │
│  A. FDE Console login                                              │
│     FDE Console → Identity Federation → WorkOS → Tenex IdP          │
│     (Tenex employees authenticate via Tenex's own IdP, e.g. Google) │
│                                                                    │
│  B. End-user agent access (the MCP flow)                           │
│     Customer agent → MCP Gateway → Identity Federation →           │
│     Customer's Okta/Entra → returns OIDC ID token →                │
│     Identity Federation issues OpenFoundry session JWT             │
│                                                                    │
│  C. Source-system OAuth (per customer, per source)                 │
│     FDE Console → Identity Federation → Salesforce OAuth →         │
│     Refresh + access tokens stored encrypted in Postgres           │
│     Source Adapter pulls fresh access tokens from Identity Service │
│                                                                    │
│  Routes                                                            │
│  ├─ GET    /v1/auth/login/:idp_id              (start OIDC flow)    │
│  ├─ GET    /v1/auth/callback/:idp_id           (OIDC callback)      │
│  ├─ POST   /v1/auth/token/exchange             (RFC 8693)           │
│  ├─ GET    /v1/auth/sources/:source_id/connect (OAuth start)        │
│  ├─ GET    /v1/auth/sources/:source_id/callback                     │
│  ├─ POST   /v1/auth/scim                       (SCIM endpoint)      │
│  └─ GET    /v1/auth/whoami                     (current session)    │
│                                                                    │
│  Components                                                        │
│  ├─ WorkOS SDK — handles OIDC heavy lifting                        │
│  ├─ JWT issuer — signs OpenFoundry session JWTs (RS256)            │
│  ├─ Token vault — encrypted at-rest source-system credentials      │
│  ├─ SCIM receiver — syncs customer IdP groups to OpenFGA           │
│  └─ Audit emitter — every auth event becomes audit log entry       │
│                                                                    │
└──────────────────────────────────────────────────────────────────┘
```

### 3.11 FDE Console (Next.js 15)

```
┌──────────────────────────────────────────────────────────────────┐
│ FDE Console (Next.js 15 App Router)                                │
├──────────────────────────────────────────────────────────────────┤
│                                                                    │
│  Routes                                                            │
│  ├─ /                                  (customer selector)         │
│  ├─ /:customer/dashboard                                           │
│  ├─ /:customer/ontology                                            │
│  │   ├─ /object-types                                              │
│  │   ├─ /action-types                                              │
│  │   ├─ /markings                                                  │
│  │   └─ /history                                                   │
│  ├─ /:customer/policies                                            │
│  ├─ /:customer/agents                                              │
│  │   ├─ /catalog                                                   │
│  │   └─ /access-grants                                             │
│  ├─ /:customer/connectors                                          │
│  │   ├─ /salesforce                                                │
│  │   ├─ /snowflake                                                 │
│  │   └─ ...                                                        │
│  ├─ /:customer/audit                                               │
│  ├─ /:customer/lineage                                             │
│  └─ /:customer/workshop                                            │
│                                                                    │
│  Components                                                        │
│  ├─ OntologyEditor — visual ontology authoring                     │
│  ├─ ActionTypeBuilder — drag-and-drop rule composition             │
│  ├─ PolicyEditor — OpenFGA model editor with visualization         │
│  ├─ AuditLogExplorer — filter, search, correlate events            │
│  ├─ LineageGraph — D3 force graph + marking simulation             │
│  ├─ ConnectorWizard — per-source configuration UI                  │
│  ├─ AgentAccessGrants — manage which agents have which tools       │
│  └─ WorkshopPreview — renders Workshop JSON configs live           │
│                                                                    │
│  Backend communication                                             │
│  ├─ tRPC procedures call Ontology / Action / Audit services        │
│  ├─ Server actions for mutations                                   │
│  ├─ Streaming SSE for live audit log / lineage                     │
│  └─ Auth: WorkOS-issued JWT in HttpOnly cookies                    │
│                                                                    │
└──────────────────────────────────────────────────────────────────┘
```

---

## Cross-Cutting Concerns

### 4.1 Multi-Tenancy

```
                Approach: Namespace-isolated, Postgres schema-per-customer

┌──────────────────────────────────────────────────────────────────┐
│ Single Kubernetes cluster (EKS) per region                        │
├──────────────────────────────────────────────────────────────────┤
│  Namespace: openfoundry-shared                                     │
│    ├─ Cloudflare ingress                                           │
│    ├─ Identity Federation Service                                  │
│    ├─ FDE Console                                                  │
│    ├─ NATS                                                         │
│    ├─ Inngest worker                                               │
│    └─ Trino coordinator                                            │
├──────────────────────────────────────────────────────────────────┤
│  Namespace: openfoundry-tenant-{customer_id}                       │
│    ├─ MCP Gateway (one per customer)                               │
│    ├─ Action Service                                               │
│    ├─ Query Service                                                │
│    ├─ Functions Runtime (workerd + Modal proxy)                    │
│    ├─ Source Adapters (deployed per source that customer uses)     │
│    ├─ Policy Service (OpenFGA instance)                            │
│    └─ Lineage Service (Marquez + propagator)                       │
├──────────────────────────────────────────────────────────────────┤
│  Shared Postgres (RDS Multi-AZ)                                    │
│    ├─ Database: openfoundry                                        │
│    │   ├─ Schema: shared (Identity Federation, audit metadata)     │
│    │   ├─ Schema: tenant_{customer_id_1}                           │
│    │   ├─ Schema: tenant_{customer_id_2}                           │
│    │   └─ ...                                                       │
│    └─ Per-customer row-level security policies via RLS              │
└──────────────────────────────────────────────────────────────────┘
```

**Why schema-per-customer, not database-per-customer:** v1 simplicity. We get isolation via Postgres `search_path` and RLS, but share connection pools, monitoring, and operational overhead. When a customer demands true isolation (BYOC or sovereign cloud), we promote to database-per-customer or cluster-per-customer.

### 4.2 Authorization (PDP / PEP Separation)

```
┌──────────────────────────────────────────────────────────────────┐
│ Policy Decision Architecture                                       │
├──────────────────────────────────────────────────────────────────┤
│                                                                    │
│  PEPs (Policy Enforcement Points) — every service                  │
│  ├─ MCP Gateway: gates tool catalog visibility per agent           │
│  ├─ Action Service: gates action invocation                        │
│  ├─ Query Service: augments queries with row predicates            │
│  ├─ FDE Console: hides UI affordances per role                     │
│  └─ Audit Service: gates log access                                │
│                                                                    │
│  PDP (Policy Decision Point) — Policy Service (OpenFGA)            │
│  ├─ Single source of truth for decisions                           │
│  ├─ Per-customer authorization model                               │
│  └─ Caches decisions in Redis (60s TTL)                            │
│                                                                    │
│  PIPs (Policy Information Points)                                  │
│  ├─ Identity Federation (user + group attributes)                  │
│  ├─ Ontology Service (object markings, action permissions schema)  │
│  └─ Source Adapters (per-row attributes for ABAC)                  │
│                                                                    │
└──────────────────────────────────────────────────────────────────┘
```

### 4.3 Audit Trail Architecture

Every action, every query, every config change, every auth event becomes an audit event. The pipeline:

```
Service → NATS (action.completed, query.executed, auth.login, ontology.committed)
   ↓
Audit Service (subscribes to all event streams)
   ↓
Postgres (immutable append-only table, partitioned by month)
   ↓
OpenTelemetry collector
   ↓
Customer's SIEM (Splunk HEC, Datadog Logs API, Sentinel, etc.)
```

**Audit event schema** (all events conform):

```typescript
interface AuditEvent {
  id: string;                    // ULID
  timestamp: string;             // ISO 8601
  tenant_id: string;
  trace_id: string;              // for cross-service correlation
  
  // Identity chain
  subject: {
    user_id?: string;            // human user
    agent_id?: string;           // agent identity (RFC 8693 act.sub)
    workload_id?: string;        // SPIFFE-style
    on_behalf_of?: string;       // user_id when agent acting for human
  };
  
  // What happened
  category: 'action' | 'query' | 'auth' | 'ontology' | 'policy' | 'admin';
  type: string;                  // e.g. 'action.submit.success'
  resource: {
    object_type?: string;
    object_id?: string;
    action_type?: string;
  };
  
  // Context
  policy_version: string;
  ontology_commit_sha: string;
  source_systems_touched: string[];
  
  // Outcome
  outcome: 'success' | 'denied' | 'error';
  details?: object;
  error?: object;
}
```

### 4.4 Observability

| Layer | Tool |
|-------|------|
| **Tracing** | OpenTelemetry (auto-instrumented + manual spans on critical paths) |
| **Metrics** | Prometheus (scraped by Grafana Cloud or self-hosted Mimir) |
| **Logs** | Loki (or Grafana Cloud Logs) |
| **APM** | Grafana Cloud (v1) → Datadog (v2 if scale demands) |
| **Frontend RUM** | Sentry |
| **Error tracking** | Sentry across all services |

**Service-level objectives (SLOs) at GA:**

- MCP Gateway tool call: p99 < 500ms (excluding source-system latency)
- Action Service submit: p99 < 1s (excluding source-system write)
- Query Service single-source: p99 < 200ms + source latency
- Query Service cross-source: p99 < 2s
- Policy Service check (cached): p99 < 2ms
- Policy Service check (uncached): p99 < 10ms
- OSDK regeneration: p95 < 30s from ontology commit

### 4.5 Deployment Topology

```
                                                ┌─────────────────────┐
                                                │ Customer's VPC      │
                                                │ ┌─────────────────┐ │
                                                │ │ Source systems  │ │
                                                │ │ (Salesforce SaaS│ │
                                                │ │  or on-prem)    │ │
                                                │ └────────┬────────┘ │
                                                └──────────┼──────────┘
                                                           │
                                                  Public OAuth / API
                                                           │
┌──────────────────────────────────────────────────────────┼────────────────────┐
│ OpenFoundry AWS account (us-east-1 in v1)                ▼                    │
│ ┌──────────────────────────────────────────────────────────────────────────┐ │
│ │ EKS cluster                                                               │ │
│ │ ┌────────────────────────────────────────────────────────────────────┐  │ │
│ │ │ Namespaces                                                          │  │ │
│ │ │ - openfoundry-shared                                                │  │ │
│ │ │ - openfoundry-tenant-acme                                           │  │ │
│ │ │ - openfoundry-tenant-beta                                           │  │ │
│ │ └────────────────────────────────────────────────────────────────────┘  │ │
│ │ - ArgoCD (GitOps controller)                                              │ │
│ │ - Cert-manager (TLS via Let's Encrypt)                                    │ │
│ │ - External-DNS (Route 53)                                                 │ │
│ │ - Cluster autoscaler                                                      │ │
│ └──────────────────────────────────────────────────────────────────────────┘ │
│                                                                                │
│ RDS Postgres Multi-AZ (db.r6g.2xlarge)                                         │
│ ElastiCache Redis (cache.r6g.large)                                            │
│ S3 buckets (per-customer for OSDK artifacts; shared for ontology snapshots)    │
│ CodeArtifact (private npm + pip)                                               │
│ Secrets Manager (source credentials, JWT signing keys)                         │
│ KMS (encryption keys, per-customer key separation)                             │
│ Route 53 (DNS, including wildcard *.mcp.openfoundry.io)                        │
│                                                                                │
└────────────────────────────────────────────────────────────────────────────────┘
                                       ▲
                                       │ HTTPS over Cloudflare
                                       │
                              ┌────────┴─────────┐
                              │ Customer agents  │
                              │ + customer apps  │
                              └──────────────────┘
```

**Per-customer deployment cost (v1 estimate):** ~$800-1,200/month of AWS spend (RDS allocation, EKS namespace, S3, network egress) before customer scale. Comfortable inside any $120K+ ACV.

---

## Data Flows

Three canonical sequence diagrams: an agent reading data, an agent submitting an action, and an FDE authoring the ontology.

### 5.1 Agent Tool Call — Read Path

```
Claude Code (agent)                MCP Gateway          Query Service       Salesforce Adapter      Salesforce
       │                                │                     │                       │                  │
       │  MCP: list_tools               │                     │                       │                  │
       │───────────────────────────────►│                     │                       │                  │
       │                                │  GET ontology       │                       │                  │
       │                                │  /ontology/openapi  │                       │                  │
       │                                ├────────────────────►│                       │                  │
       │                                │◄────────────────────┤                       │                  │
       │  ◄── tool catalog (object types + action types as tools)                     │                  │
       │                                │                     │                       │                  │
       │  MCP: call_tool                │                     │                       │                  │
       │  query_Account where=...       │                     │                       │                  │
       │───────────────────────────────►│                     │                       │                  │
       │                                │  AuthBridge:        │                       │                  │
       │                                │  verify aud, scope, │                       │                  │
       │                                │  issue internal JWT │                       │                  │
       │                                │                     │                       │                  │
       │                                │  POST /query/objects│                       │                  │
       │                                │  body: Account, where, fields              │                  │
       │                                ├────────────────────►│                       │                  │
       │                                │                     │  PDP check:           │                  │
       │                                │                     │  can_read(user, Account)│               │
       │                                │                     ├──► Policy Service     │                  │
       │                                │                     │◄──── allow + filter   │                  │
       │                                │                     │                       │                  │
       │                                │                     │  Adapter dispatch     │                  │
       │                                │                     ├──────────────────────►│                  │
       │                                │                     │                       │  SOQL query      │
       │                                │                     │                       ├─────────────────►│
       │                                │                     │                       │◄─── rows          │
       │                                │                     │◄──────────────────────┤                  │
       │                                │                     │                       │                  │
       │                                │                     │  Materialize → Account objects           │
       │                                │                     │  Apply cell masks per markings           │
       │                                │                     │                       │                  │
       │                                │◄────────────────────┤                       │                  │
       │  ◄── typed JSON (Account[])    │                     │                       │                  │
       │                                │                     │                       │                  │
       │                                │  Audit event: query.executed                │                  │
       │                                ├──► Audit Service ──► Postgres ──► OTel ──► Customer SIEM       │
```

### 5.2 Agent Tool Call — Action Submission (with side effects)

```
Claude (agent)        MCP Gateway      Action Service    Policy Svc   Salesforce Adapter   Salesforce   Slack
      │                    │                  │              │                │                 │           │
      │ submit_action       │                  │              │                │                 │           │
      │ approve_purchase    │                  │              │                │                 │           │
      │ order(id=#4839)     │                  │              │                │                 │           │
      ├────────────────────►│                  │              │                │                 │           │
      │                     │ POST /actions/   │              │                │                 │           │
      │                     │ approve_po/submit│              │                │                 │           │
      │                     ├─────────────────►│              │                │                 │           │
      │                     │                  │ Load action  │                │                 │           │
      │                     │                  │ type def     │                │                 │           │
      │                     │                  │              │                │                 │           │
      │                     │                  │ Validate     │                │                 │           │
      │                     │                  │ params (Zod) │                │                 │           │
      │                     │                  │              │                │                 │           │
      │                     │                  │ Policy check │                │                 │           │
      │                     │                  ├─────────────►│                │                 │           │
      │                     │                  │◄─── allow   │                │                 │           │
      │                     │                  │              │                │                 │           │
      │                     │                  │ Eval submission criteria      │                 │           │
      │                     │                  │ (call Function checkPOLimit) │                 │           │
      │                     │                  ├──► Functions Runtime ──► returns true          │           │
      │                     │                  │              │                │                 │           │
      │                     │                  │ Plan rules → updates needed   │                 │           │
      │                     │                  │                                │                 │           │
      │                     │                  │ Execute via Salesforce Adapter│                 │           │
      │                     │                  ├──────────────────────────────►│                 │           │
      │                     │                  │                                │ PATCH PO #4839  │           │
      │                     │                  │                                │ status=approved │           │
      │                     │                  │                                ├────────────────►│           │
      │                     │                  │                                │◄── 200 OK       │           │
      │                     │                  │◄──────────────────────────────┤                 │           │
      │                     │                  │                                │                 │           │
      │                     │                  │ Side effects (Inngest queues)                  │           │
      │                     │                  ├──► Inngest ─► notify Slack ──────────────────────────────►│
      │                     │                  │                                │                 │           │
      │                     │                  │ Audit event: action.submit.success                          │
      │                     │                  ├──► Audit Service                                            │
      │                     │                  │                                │                 │           │
      │                     │◄─── 200 + submission_id                                             │           │
      │◄────────────────────┤                  │                                │                 │           │
      │ ◄── success         │                  │                                │                 │           │
```

### 5.3 FDE Ontology Authoring

```
FDE                    FDE Console           Ontology Service        OSDK Generator    Customer's npm
 │                          │                       │                       │                    │
 │ Open /:cust/ontology     │                       │                       │                    │
 ├─────────────────────────►│                       │                       │                    │
 │                          │  GET /v1/ontology/    │                       │                    │
 │                          │  describe             │                       │                    │
 │                          ├──────────────────────►│                       │                    │
 │                          │◄─── full ontology     │                       │                    │
 │                          │                       │                       │                    │
 │ Add object type "Patient"│                       │                       │                    │
 ├─────────────────────────►│                       │                       │                    │
 │ + properties (mrn,       │                       │                       │                    │
 │   name, dob, ...)        │                       │                       │                    │
 │ + action types (discharge,│                      │                       │                    │
 │   admit, transfer)       │                       │                       │                    │
 │                          │                       │                       │                    │
 │ Commit                   │                       │                       │                    │
 ├─────────────────────────►│                       │                       │                    │
 │                          │  POST /ontology/commit│                       │                    │
 │                          │  message="Add Patient"│                       │                    │
 │                          ├──────────────────────►│                       │                    │
 │                          │                       │ Validate              │                    │
 │                          │                       │ Write commit row      │                    │
 │                          │                       │ Emit ontology.commit.created                │
 │                          │                       │                       │                    │
 │                          │                       │ NATS ──────────────► │                    │
 │                          │                       │                       │ Pull snapshot       │
 │                          │                       │                       │ Emit OpenAPI        │
 │                          │                       │                       │ Run openapi-ts      │
 │                          │                       │                       │ Build sdk package   │
 │                          │                       │                       │ Publish ──────────►│
 │                          │                       │                       │                    │
 │                          │ SSE: new SDK version  │                       │                    │
 │                          │ available (notification)                      │                    │
 │◄─────────────────────────┤                       │                       │                    │
 │                          │                       │                       │                    │
 │ "Test in Claude Code"    │                       │                       │                    │
 │ FDE switches to Claude   │                       │                       │                    │
 │ Code, points at MCP URL  │                       │                       │                    │
 │ acme.mcp.openfoundry.io  │                       │                       │                    │
 │ Claude lists tools →     │                       │                       │                    │
 │ sees query_Patient,      │                       │                       │                    │
 │ submit_discharge, etc.   │                       │                       │                    │
```

---

## The Salesforce Integration Pattern (Worked Example)

Salesforce is the most likely first integration. Working through it in detail establishes the pattern for every other source adapter.

### 6.1 Auth — Salesforce Connected App

```
1. Customer admin in Salesforce: install OpenFoundry Connected App
   - Defines OAuth scopes: api, refresh_token, full
   - Sets callback URL to https://api.openfoundry.io/v1/auth/sources/salesforce/callback
   - Issues Consumer Key + Consumer Secret

2. FDE in FDE Console: Add Salesforce connector
   - Enter Consumer Key, Consumer Secret, instance URL (e.g. acme.my.salesforce.com)
   - Click "Authorize"

3. Identity Federation Service:
   - Generates state nonce
   - Redirects FDE's browser to acme.my.salesforce.com/services/oauth2/authorize
   - Salesforce returns auth code
   - Identity Federation exchanges code for refresh + access tokens
   - Encrypted at rest in Postgres (per-customer KMS key)

4. Salesforce Adapter on first call:
   - Pulls refresh token from Identity Federation
   - Exchanges for fresh access token
   - Caches in Redis for ~50min
   - Subsequent calls reuse cached token
```

### 6.2 Schema Introspection (auto-ontology bootstrap)

```typescript
// services/salesforce-adapter/src/introspect.ts

import jsforce from 'jsforce';

export async function introspectSchema(
  conn: jsforce.Connection
): Promise<SchemaDescriptor> {
  // 1. List all SObjects accessible to the auth user
  const globalDescribe = await conn.describeGlobal();
  
  // 2. For each Standard + Custom Object the user has access to
  const objectTypes: ObjectTypeDescriptor[] = [];
  for (const sobj of globalDescribe.sobjects) {
    if (!sobj.queryable) continue;
    if (sobj.deprecatedAndHidden) continue;
    
    // 3. Get the full description
    const desc = await conn.sobject(sobj.name).describe();
    
    objectTypes.push({
      source_name: sobj.name,                    // "Account"
      suggested_ontology_name: humanize(sobj.name), // "Account" or "Customer"
      properties: desc.fields.map(f => ({
        source_name: f.name,                     // "Industry"
        suggested_name: humanize(f.name),         // "Industry"
        type: mapSalesforceType(f.type),          // "string" | "enum" | etc
        constraints: {
          required: !f.nillable,
          max_length: f.length,
          values: f.picklistValues?.map(v => v.value),
        },
        suggested_marking: f.name.includes('SSN') ? ['pii'] : [],
      })),
      links: desc.fields
        .filter(f => f.type === 'reference')
        .map(f => ({
          name: f.relationshipName,
          target: f.referenceTo[0],
          cardinality: 'many-to-one',
        })),
    });
  }
  
  // 4. Discover Apex methods exposed as REST resources for actions
  // (Salesforce-specific: an Apex @RestResource method becomes an action_type candidate)
  
  return { object_types: objectTypes, /* ... */ };
}
```

The FDE Console renders this discovered schema as a *proposed* ontology. The FDE walks through it with the customer SME: rename `Account` to `Customer`, demote 200 properties down to 30 important ones, mark `SSN__c` as PII, add action types like `update_status` for the workflow they care about.

### 6.3 Read Path — Query Translation

```typescript
// services/salesforce-adapter/src/query.ts

export async function query(
  conn: jsforce.Connection,
  objectType: ObjectTypeMapping,
  filter: OntologyFilter,
  fields: string[]
): AsyncIterable<Row> {
  // Translate ontology filter to SOQL WHERE
  const where = translateFilter(filter, objectType.field_map);
  
  // Translate ontology field names to source field names
  const sourceFields = fields.map(f => objectType.field_map[f]);
  
  // Build SOQL
  const soql = `
    SELECT ${sourceFields.join(', ')}
    FROM ${objectType.source_name}
    WHERE ${where}
    ORDER BY Id
    LIMIT 200
  `;
  
  // Stream with pagination
  let result = await conn.query(soql);
  while (true) {
    for (const record of result.records) {
      yield translateRecord(record, objectType.field_map);
    }
    if (result.done) break;
    result = await conn.queryMore(result.nextRecordsUrl);
  }
}
```

The Query Service calls this when the ontology query is `client(Customer).where(c => c.industry === 'Tech')`. The adapter handles all SOQL specifics; the Query Service just sees ontology-shaped objects coming back.

### 6.4 Write Path — Action Execution

```typescript
// services/salesforce-adapter/src/execute.ts

export async function execute(
  conn: jsforce.Connection,
  rules: ActionRules,
  params: Record<string, unknown>,
  identity: Identity
): Promise<ExecutionResult> {
  const updates: Promise<unknown>[] = [];
  
  for (const rule of rules.steps) {
    switch (rule.kind) {
      case 'modify_object': {
        const targetId = resolveReference(rule.target, params);
        const fields = mapFields(rule.set, params);
        updates.push(
          conn.sobject(rule.object_type.source_name).update({
            Id: targetId,
            ...fields,
            // Idempotency via External_Id__c if Salesforce object has one
          }, {
            // Use Compositive API for atomic multi-update if rule.steps.length > 1
            allOrNone: true,
          })
        );
        break;
      }
      case 'create_object': {
        const fields = mapFields(rule.with, params);
        updates.push(
          conn.sobject(rule.object_type.source_name).create(fields)
        );
        break;
      }
      case 'apex_callout': {
        // For complex business logic exposed by customer as Apex REST endpoint
        updates.push(
          conn.apex.post(`/services/apexrest/${rule.endpoint}`, params)
        );
        break;
      }
    }
  }
  
  // If atomic-required and >1 step, use Salesforce Composite API
  // Otherwise issue parallel updates and let saga handle compensation
  const results = await Promise.all(updates);
  
  return { success: true, source_ids: extractIds(results) };
}
```

### 6.5 Change Feed (Mode B optional)

Mode B (Materialized View) uses Salesforce Change Data Capture:

```typescript
// services/salesforce-adapter/src/subscribe.ts

export async function* subscribe(
  conn: jsforce.Connection,
  spec: ChangeStreamSpec
): AsyncIterable<ChangeEvent> {
  const channel = `/data/${spec.object_type}ChangeEvent`;
  
  // CometD subscription via jsforce streaming
  const subscription = conn.streaming.topic(channel).subscribe(message => {
    yield {
      kind: message.event.changeType, // CREATE | UPDATE | DELETE
      object_type: spec.object_type,
      source_id: message.payload.ChangeEventHeader.recordIds[0],
      changed_fields: message.payload.ChangeEventHeader.changedFields,
      changed_at: new Date(message.payload.ChangeEventHeader.commitTimestamp),
      payload: message.payload,
    };
  });
}
```

Feeds into Connector Manager → Iceberg table for materialized reads. Most v1 customers won't need this; pass-through reads are sufficient.

### 6.6 Per-Adapter Footprint

This pattern is roughly 800–1,500 lines of TypeScript per source. Estimated build time:

| Adapter | Effort | Notes |
|---------|--------|-------|
| Salesforce | 4 weeks | jsforce + introspection + Composite API + change feed |
| Snowflake | 2 weeks | snowflake-sdk; mostly read-only |
| Databricks | 2 weeks | REST + JDBC; mostly read-only |
| ServiceNow | 3 weeks | sn-rest; tricky pagination |
| Workday | 4 weeks | SOAP-based, painful auth; consider Workday Web Services SDK |
| S3 + Iceberg | 1 week | mostly direct PyIceberg / Iceberg-rs use |

Total for 6 launch adapters: ~16 person-weeks. One engineer dedicated for 4 months, or two engineers for 2 months.

---

## Monorepo Structure

```
openfoundry/
├── apps/
│   ├── fde-console/                      # Next.js 15 — FDE-facing UI
│   ├── mcp-gateway/                      # Fastify — agent-facing MCP server
│   └── workshop-runtime/                 # Vite library — embeddable Workshop renderer
│
├── services/
│   ├── ontology/                         # Custom — type definition CRUD + versioning
│   ├── action/                           # Custom — action execution pipeline
│   ├── query/                            # Custom — read path with policy augmentation
│   ├── functions/                        # workerd wrapper for TS Functions
│   ├── policy/                           # OpenFGA + thin auth wrapper
│   ├── lineage/                          # Marquez + marking propagator
│   ├── audit/                            # Audit ingest + OTel forwarder
│   ├── identity/                         # OIDC federation + source OAuth
│   ├── osdk-generator/                   # Codegen worker (Inngest-driven)
│   └── connector-manager/                # Airbyte orchestration
│
├── adapters/
│   ├── salesforce/                       # jsforce-based adapter (Node)
│   ├── snowflake/                        # snowflake-sdk-based
│   ├── databricks/                       # databricks-sql-node
│   ├── servicenow/                       # custom REST client
│   ├── workday/                          # @workday/web-services-node
│   ├── s3-iceberg/                       # pyiceberg via WASI sidecar
│   └── _scaffolding/                     # template for new adapters
│
├── packages/
│   ├── protocol/                         # Shared TS types, Protobuf, gRPC defs
│   │   ├── proto/                        # *.proto files
│   │   └── src/                          # generated TS + hand-written types
│   ├── sdk-ts/                           # OSDK TypeScript runtime (hand-written)
│   ├── sdk-python/                       # OSDK Python runtime
│   ├── policy-lang/                      # OpenFGA model helpers + Cerbos compat
│   ├── workshop-spec/                    # Workshop module JSON schemas
│   ├── audit-events/                     # Audit event schemas + Zod validators
│   ├── ontology-core/                    # Ontology type primitives shared across svcs
│   ├── eslint-config/                    # Shared lint rules
│   └── tsconfig/                         # Shared TS configs (base, node, react)
│
├── infra/
│   ├── terraform/
│   │   ├── modules/                      # Reusable TF modules
│   │   │   ├── eks-cluster/
│   │   │   ├── rds-postgres/
│   │   │   ├── elasticache-redis/
│   │   │   ├── s3-customer-bucket/
│   │   │   ├── codeartifact-repos/
│   │   │   └── route53-zone/
│   │   ├── environments/
│   │   │   ├── dev/
│   │   │   ├── staging/
│   │   │   └── production/
│   │   └── customer-templates/           # TF that runs per new customer onboarded
│   ├── helm/
│   │   ├── charts/                       # One Helm chart per service
│   │   │   ├── ontology/
│   │   │   ├── action/
│   │   │   └── ...
│   │   └── umbrella/                     # Per-customer umbrella chart
│   ├── docker/                           # Shared Dockerfile patterns
│   ├── k8s/                              # Raw manifests for shared infra (ArgoCD, etc.)
│   └── argocd/                           # ApplicationSet definitions
│
├── tools/
│   ├── cli/                              # `openfoundry` CLI for FDEs
│   │   └── src/commands/
│   │       ├── customer-onboard.ts
│   │       ├── ontology-init.ts
│   │       ├── adapter-deploy.ts
│   │       └── ...
│   ├── scaffolder/                       # `openfoundry create-adapter foo`
│   ├── fixtures/                         # Test data generators
│   └── load-test/                        # k6 scripts
│
├── docs/
│   ├── architecture/                     # This doc and ADRs
│   │   ├── adr-001-multitenancy.md
│   │   ├── adr-002-policy-engine.md
│   │   └── ...
│   ├── runbooks/
│   ├── customer-onboarding/
│   └── api-reference/                    # Auto-generated from OpenAPI
│
├── tests/
│   ├── e2e/                              # Playwright + REST tests across services
│   ├── load/                             # k6 load tests
│   └── contract/                         # Adapter contract tests
│
├── customer-configs/                     # GitOps repo for per-customer configs
│   ├── acme/
│   │   ├── ontology.yaml                 # Or pointer to acme-specific repo
│   │   ├── policies/
│   │   ├── connectors.yaml
│   │   └── workshop-modules/
│   └── ...
│
├── turbo.json                            # Turborepo pipeline config
├── pnpm-workspace.yaml
├── package.json
├── tsconfig.base.json
├── biome.json                            # Linting + formatting (replaces ESLint+Prettier)
└── README.md
```

### Turborepo pipeline

```jsonc
// turbo.json
{
  "$schema": "https://turbo.build/schema.json",
  "tasks": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": ["dist/**", ".next/**"]
    },
    "test": {
      "dependsOn": ["build"],
      "outputs": ["coverage/**"]
    },
    "lint": {},
    "dev": { "cache": false, "persistent": true },
    "docker:build": {
      "dependsOn": ["build"],
      "outputs": []
    },
    "deploy:dev": { "dependsOn": ["docker:build"], "cache": false }
  }
}
```

A change to `packages/protocol` triggers rebuilds of every service that consumes it. A change to one adapter only rebuilds that adapter. CI runs `turbo run test --filter=...[origin/main]` to test only what changed.

---

## Technology Choices Summary

The full table of choices, with the rationale for each.

| Concern | Choice | Why |
|---------|--------|-----|
| **Language (services)** | TypeScript on Node 22 LTS | OSDK is TS-first; engineers don't context-switch; Bun considered but ecosystem still risky in production |
| **Framework (services)** | Fastify + Zod | Fastest Node HTTP framework; first-class TypeScript; built-in JSON schema |
| **Frontend framework** | Next.js 15 + React 19 | Industry standard; SSR for FDE Console performance; tRPC integration |
| **Backend-frontend RPC** | tRPC | End-to-end type safety from Fastify routes to React |
| **Database** | Postgres 16 on RDS Multi-AZ | Boring, reliable, RLS for tenant isolation, JSONB for flexibility, pgvector for embeddings |
| **Cache** | Redis 7 (Upstash for v1) | Industry standard; Upstash for serverless billing; ElastiCache for v2 |
| **Event bus** | NATS JetStream (self-hosted) | Lighter than Kafka; sufficient for our throughput; native TypeScript client |
| **Async workflow** | Inngest (managed) | Cleaner DX than Temporal; webhook-friendly; built-in retries + cron |
| **Identity (FDE)** | WorkOS | B2B-first; SAML/SCIM for Tenex enterprise customers in v2; Auth0 considered but more expensive |
| **Identity (customer end-users)** | OIDC federation to customer's IdP | Customer IdP is source of truth; we issue session JWTs from theirs |
| **Authorization** | OpenFGA (self-hosted) | Zanzibar-style; Auth0/Okta-backed; agent identity story converges here |
| **Functions runtime (TS)** | Cloudflare workerd (self-hosted) | V8 isolates; lowest cold-start cost; same engine as production CF Workers |
| **Functions runtime (Python)** | Modal | Best-in-class Python serverless; container-native; first-class ML deps |
| **Federated query** | Trino (self-hosted) | Industry standard; broadest connector ecosystem; only invoked for cross-source |
| **Object storage** | S3 with Iceberg | Customer-region buckets; Iceberg for any materialized state |
| **Connector platform** | Airbyte (self-hosted) | OSS; 350+ connectors; only used for Mode B sync |
| **MCP SDK** | Anthropic's @modelcontextprotocol/sdk | First-party; will stay current with spec |
| **Lineage** | Marquez (OpenLineage server) | Reference implementation; OSS; integrates with dbt/Spark/Airflow natively |
| **Observability** | OpenTelemetry + Grafana Cloud | Vendor-neutral; cheaper than Datadog at small scale; upgrade path |
| **Error tracking** | Sentry | Best DX; affordable; first-class TS/React/Python |
| **Container orchestration** | EKS (Kubernetes) | Industry standard; ArgoCD for GitOps; v2 considers Fargate |
| **GitOps** | ArgoCD | Standard; declarative; multi-cluster ready |
| **IaC** | Terraform + Helm | Boring; well-understood; team can hire for these skills |
| **CDN / edge** | Cloudflare | DDoS, WAF, Cache, Workers if we need edge logic; ZTNA for FDE access |
| **CI/CD** | GitHub Actions + ArgoCD | GitHub Actions for build/test; ArgoCD for deploy |
| **Monorepo** | Turborepo + pnpm workspaces | Faster than Bazel for our scale; first-class TS support; incremental builds |
| **Linting / formatting** | Biome | 10-100x faster than ESLint + Prettier; one tool; written in Rust |
| **Testing (unit)** | Vitest | Faster than Jest; native TS; works with Turborepo |
| **Testing (e2e)** | Playwright | Industry standard; cross-browser; great DX |
| **Testing (load)** | k6 (Grafana) | Code-as-tests; cloud-runnable |
| **Private package registry** | AWS CodeArtifact | npm + pip in one; KMS-encrypted; same account as everything else |
| **Secrets** | AWS Secrets Manager + per-customer KMS keys | Industry standard; rotation automation |
| **DNS** | Route 53 | Same account; Terraform-native |

---

## The First-Customer Deployment Plan (90 Days)

The build-and-deploy compression: ship enough platform to support one customer in 90 days, with the FDE engagement at that customer simultaneously delivering customer value and forcing real-world testing.

### Pre-flight (Week 0)

Before kickoff, the following must be in place:

- Customer signs design-partner agreement (free or nominal $25K)
- Customer designates a Chief Data Officer or Chief AI Officer sponsor
- Tenex assigns 1 senior FDE + 1 ontology architect to the engagement
- Five spine engineers locked in (hires confirmed; existing FDEs rotated as needed)
- AWS account opened; production VPC + EKS cluster Terraformed
- Domain `openfoundry.io` purchased; `*.mcp.openfoundry.io` DNS configured
- GitHub org `tenex-openfoundry` created; monorepo skeleton scaffolded

### Sprint 1 (Weeks 1–2): Platform skeleton + Salesforce connection

Goal: stand up the bare minimum platform stack and prove we can read from the customer's Salesforce in a permission-respecting way.

**Platform team (5 engineers):**

- Monorepo scaffolded with Turborepo + pnpm
- `services/ontology` — basic CRUD over object/property/action types in Postgres
- `services/identity` — OIDC federation working with the customer's Okta; OAuth flow for Salesforce
- `adapters/salesforce` — auth + introspect + basic query
- `services/query` — minimum viable: routes single-source queries to adapters
- `apps/fde-console` — basic Next.js shell; connector wizard for Salesforce
- AWS infra: RDS, ElastiCache, EKS, ArgoCD, Cloudflare DNS

**FDE team (2 people on customer site):**

- Discovery sessions: what are the operational verbs the customer wants?
- Maps existing Salesforce schema → proposed ontology
- Walks customer through "what is an Ontology?"
- Sets expectations for week 6 demo

**Deliverable end of Sprint 1:** FDE can authenticate the customer's Salesforce in FDE Console; basic SOQL queries return through OpenFoundry. No agent integration yet. No write path yet.

### Sprint 2 (Weeks 3–4): MCP exposure + read-only agent integration

Goal: customer's Claude Code instance can call `query_Account`, `query_Opportunity` through OpenFoundry's MCP endpoint.

**Platform team:**

- `apps/mcp-gateway` — wraps Anthropic MCP SDK; reads tool catalog from Ontology Service; routes calls to Query Service
- Identity Service: complete OAuth 2.1 + RFC 8707 + CIMD support
- Per-customer MCP endpoint: `acme.mcp.openfoundry.io`
- Basic `services/policy` (OpenFGA installed; first authorization model defined)
- `services/osdk-generator` — generates TypeScript OSDK from ontology commits
- AWS CodeArtifact set up; first private npm package published

**FDE team:**

- Refines ontology with customer SMEs (~30 object types, ~80 properties)
- Configures customer's Claude Code instance with MCP endpoint
- Writes the first test prompts: "show me the 10 largest open opportunities in EMEA"
- Demonstrates working agent-to-Salesforce read flow

**Deliverable end of Sprint 2:** Customer's Claude Code agent reads Salesforce data through OpenFoundry. Customer dashboards in FDE Console show audit log of agent queries.

### Sprint 3 (Weeks 5–6): Action runtime + write path

Goal: agent can submit typed Actions that write back to Salesforce.

**Platform team:**

- `services/action` — submission pipeline, validation, policy check, execution via adapter
- Salesforce adapter: write path with idempotency
- Action type schema in Ontology Service
- Audit Service end-to-end (events flow to customer's Splunk)
- Dry-run mode for actions
- Per-tool descriptions in MCP catalog (the `agent_description` field)

**FDE team:**

- Authors 5–10 action types with customer SMEs (`update_opportunity_stage`, `log_call`, `assign_owner`, etc.)
- Sets policy: "agents can dry-run any action; only specific users + agents can submit"
- Walks through first agent action: agent proposes, human approves, action executes
- Documents the workflow as the case study draft

**Deliverable end of Sprint 6 (mid-engagement demo):** Customer's CDO + sponsor see a live demo. Claude Code agent: "find the 5 stalled opportunities in EMEA above $500K and propose an action plan." Agent queries Salesforce through OpenFoundry, drafts proposed actions, requests human approval, executes against Salesforce on approval. Audit log shows every step in Splunk. The CDO understands what was just built.

### Sprint 4 (Weeks 7–8): Functions + a second data source

Goal: customer-authored business logic runs in OpenFoundry; second source system (Snowflake) integrated.

**Platform team:**

- `services/functions` — workerd integration; TypeScript Functions deployable per-tenant
- `adapters/snowflake` — read path
- Query Service: cross-source query via Trino (Salesforce ↔ Snowflake)
- Workshop renderer (basic): JSON-defined views for ontology objects

**FDE team:**

- Authors first Function with customer: scoring algorithm that takes an Opportunity, looks at related historical Account spend in Snowflake, returns a "deal quality score"
- Wires Function as a computed property on Opportunity
- Customer's agents can now query opportunities with the computed score

**Deliverable end of Sprint 8:** OpenFoundry handles cross-source reads (Salesforce + Snowflake) and customer-authored Functions execute safely. Two source systems integrated.

### Sprint 5 (Weeks 9–10): Lineage + markings

Goal: regulated-customer-grade governance is operational.

**Platform team:**

- `services/lineage` — Marquez + custom propagator
- OpenLineage events emitted by Action Service + Query Service
- Marking propagation: PII on a Salesforce field flows through to derived Function outputs
- FDE Console: lineage graph view + simulation mode

**FDE team:**

- Marks customer's PII fields explicitly (SSN, DOB, email if applicable)
- Tests: simulates removing PII marking from a field; sees the downstream impact
- Demonstrates to customer's CISO

**Deliverable end of Sprint 10:** CISO is comfortable. Markings inherit through queries. SIEM logs show every PII access. Audit-ready evidence.

### Sprint 6 (Weeks 11–12): Polish, hardening, first paid contract

Goal: ship a real (small) production deployment; convert design partner to paid.

**Platform team:**

- SOC 2 Type 2 controls implemented
- Load testing (k6) up to 10× expected customer volume
- Per-customer KMS keys; secrets rotation tested
- Backup + DR procedures documented
- Observability dashboards in Grafana per service
- Runbooks for the top 10 incident categories
- Production deployment hardened: ArgoCD, autoscaling, alerting

**FDE team:**

- Writes the case study with the customer
- Customer agrees to convert to paid: $120K base + ~$50K services year 1
- Reference call with prospect #2 booked
- Second customer engagement begins

**Deliverable end of Sprint 12:** Production-quality deployment for design partner #1. First paid contract signed. Pipeline of 4–6 next-customer conversations underway.

---

## Building the System While Deploying the First Customer

The hardest organizational pattern in services-to-product transitions is doing product development and customer delivery simultaneously. The platform engineering team builds the platform; the FDE team uses what the platform team has shipped *yesterday* to deliver customer value *today*. This forces real-world testing without making customers wait for v1 to be perfect.

### The two-track structure

```
                       ┌─────────────────────────────────────┐
                       │  CEO                                │
                       └─────────┬───────────────────────────┘
                                 │
            ┌────────────────────┼──────────────────────┐
            ▼                    ▼                      ▼
┌──────────────────┐  ┌──────────────────┐    ┌──────────────────┐
│ GM Product       │  │ COO              │    │ CTO              │
│ (OpenFoundry)    │  │ (Services)       │    │ (Engineering)    │
└────────┬─────────┘  └────────┬─────────┘    └────────┬─────────┘
         │                     │                       │
         ▼                     ▼                       ▼
┌──────────────────┐  ┌──────────────────┐    ┌──────────────────┐
│ Platform Team    │  │ Delivery Ops     │    │ Billable Eng     │
│ (5 engineers     │  │ (project mgmt)   │    │ (~34 engineers)  │
│ + 1 PM + 1 AE    │  │                  │    │                  │
│ + 1 PMM)         │  │                  │    │                  │
├──────────────────┤  │                  │    │                  │
│ Building the     │  │                  │    │ Billable client  │
│ platform         │  │                  │    │ engagements      │
└──────────────────┘  └──────────────────┘    └──────────────────┘
         │                                              ▲
         │                                              │
         │  Rotating FDE assignments                    │
         │  (2 FDEs at a time, 8-week rotations)        │
         └──────────────────────────────────────────────┘
                              │
                              ▼
                  ┌──────────────────────┐
                  │ Design Partner       │
                  │ Engagement (Customer)│
                  └──────────────────────┘
```

### The FDE rotation pattern

Two FDEs are seconded from the billable pool into the design-partner engagement for an 8-week rotation. They are *not* "on the platform team" — they're delivering customer value using whatever the platform team has shipped. Their feedback drives the platform team's priorities.

After 8 weeks, two new FDEs rotate in. The previous two go back to billable engagements, but they carry platform muscle into those engagements. Within 6 months, half of Tenex's FDE bench has hands-on experience with OpenFoundry primitives, and platform features have been pressure-tested by 3–4 different FDE perspectives.

This is exactly how Palantir compounds field abstractions back into the platform. The Tenex variant is faster because the rotation is explicit and the platform team is small enough to react in days, not quarters.

### The "loud feedback channel"

A weekly platform-team-meets-FDE-team sync. Standing agenda:

1. **What was painful this week in customer delivery?** FDEs report friction points. Each becomes a GitHub issue tagged `field-feedback`.
2. **What was shipped this week?** Platform team demos the latest. FDEs note what they can adopt immediately.
3. **What's blocking the next customer milestone?** Sometimes a missing platform feature. Sometimes a customer-specific configuration. Categorize honestly.

Every `field-feedback` issue is reviewed in the next platform planning cycle. The rule: if three different FDEs raise the same issue independently, it becomes a Tier 1 platform priority. This is the explicit harvest mechanism that prevents the platform from drifting into one customer's bespoke shape.

### What gets customer-specific vs platform code

The cardinal rule: **customer-specific code never lands in the platform monorepo's `main` branch.**

| Customer-specific | Goes in |
|--------------------|---------|
| Ontology definitions (object types, action types, markings) | `customer-configs/{customer}/ontology.yaml` |
| Policies (OpenFGA models) | `customer-configs/{customer}/policies/` |
| Source-system credentials (OAuth tokens) | AWS Secrets Manager (per-customer KMS) |
| Workshop modules | `customer-configs/{customer}/workshop-modules/` |
| Custom Functions (TS/Python code) | `customer-configs/{customer}/functions/` |
| Connector configurations | `customer-configs/{customer}/connectors.yaml` |

The platform repo contains only generic infrastructure. The customer-configs repo is a separate GitOps repo that ArgoCD reads to deploy per-customer Helm releases. When customer #2 onboards, we add a `customer-configs/beta/` directory; nothing in the platform repo changes.

This is the discipline that prevents a services company from drifting into custom-software-per-customer territory.

---

## Roadmap and Milestones

### v1.0 (Month 3) — Design Partner GA

- 5 services (Ontology, Action, Query, OSDK Generator, OSDK runtime)
- 2 source adapters (Salesforce, Snowflake)
- MCP Gateway with full RFC 8707 compliance
- OpenFGA-backed policy engine
- Audit log + Splunk forwarder
- FDE Console (ontology editor, audit explorer, connector wizard)
- SOC 2 Type 1
- 1 paying customer ($120K+ base)

### v1.5 (Month 6) — Multi-customer MVP

- 6 source adapters (add Databricks, ServiceNow, Workday, S3)
- Functions runtime (TS via workerd; Python via Modal)
- Lineage Service with marking propagation
- Workshop renderer (basic)
- 3 paying customers totaling $1.2–2.5M Year 1 ARR

### v2.0 (Month 12) — Series A worthy

- 12 source adapters (Microsoft 365, NetSuite, SAP, Epic, etc.)
- Cross-source federation via Trino in production
- BYOC-on-AWS (control plane / data plane separation)
- ISO 42001 audit started
- 8–12 customers, $6–12M ARR
- SOC 2 Type 2
- Mode B materialization (Iceberg) for cross-source heavy queries
- Cross-customer policy library (anonymized recommendations)

### v3.0 (Month 24) — OpenFoundry brand launch

- Azure BYOC deployment
- Second LLM provider abstraction (OpenAI parity)
- Workshop module agent-authoring (agents generate Workshop JSON via MCP)
- Vertical certified ontologies (BFSI, healthcare)
- Marketplace skeleton for partner-built modules
- 20+ customers, $20–40M ARR

### v4.0 (Month 36) — Platform maturity

- GCP BYOC
- Gemini provider abstraction
- ISV ecosystem launched
- FedRAMP Moderate audit started
- Auto-ontology inference from agent activity (the "self-learning" pitch matures)
- 50+ customers, $50–100M ARR

---

## Appendix A — Data Model

The core Postgres tables. Most live in per-customer schemas; the shared schema holds system-wide tables.

```sql
-- Shared schema (system-wide)

CREATE SCHEMA shared;

CREATE TABLE shared.customers (
  id          TEXT PRIMARY KEY,           -- e.g. "acme"
  name        TEXT NOT NULL,
  tier        TEXT NOT NULL,              -- 'design-partner' | 'paid' | 'enterprise'
  created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  config      JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE shared.users (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id TEXT NOT NULL REFERENCES shared.customers(id),
  external_id TEXT NOT NULL,              -- subject claim from customer IdP
  email       TEXT NOT NULL,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE (customer_id, external_id)
);

CREATE TABLE shared.agents (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id TEXT NOT NULL REFERENCES shared.customers(id),
  name        TEXT NOT NULL,              -- "claude-code-prod"
  cimd_url    TEXT NOT NULL,              -- client metadata document URL
  owner_user_id UUID NOT NULL REFERENCES shared.users(id),
  created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Per-customer schema (one schema per customer; identical structure)

CREATE SCHEMA tenant_acme;

CREATE TABLE tenant_acme.ontology_commits (
  sha           TEXT PRIMARY KEY,
  parent_sha    TEXT,
  author_id     UUID NOT NULL REFERENCES shared.users(id),
  message       TEXT NOT NULL,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  payload       JSONB NOT NULL            -- full ontology snapshot at this commit
);

CREATE TABLE tenant_acme.object_types (
  id            TEXT PRIMARY KEY,         -- e.g. "Customer"
  commit_sha    TEXT NOT NULL REFERENCES tenant_acme.ontology_commits(sha),
  source_system TEXT NOT NULL,            -- "salesforce"
  source_name   TEXT NOT NULL,            -- "Account"
  schema        JSONB NOT NULL,           -- field defs
  markings      TEXT[] NOT NULL DEFAULT '{}',
  description   TEXT,
  agent_description TEXT,                 -- shown to agents in tool catalog
  is_active     BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE tenant_acme.action_types (
  id            TEXT PRIMARY KEY,
  commit_sha    TEXT NOT NULL REFERENCES tenant_acme.ontology_commits(sha),
  parameters    JSONB NOT NULL,
  rules         JSONB NOT NULL,
  criteria      JSONB,
  side_effects  JSONB,
  description   TEXT,
  agent_description TEXT,
  is_active     BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE tenant_acme.action_submissions (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  action_type_id TEXT NOT NULL,
  submitted_by  UUID REFERENCES shared.users(id),
  submitted_by_agent UUID REFERENCES shared.agents(id),
  on_behalf_of_user UUID REFERENCES shared.users(id),
  parameters    JSONB NOT NULL,
  status        TEXT NOT NULL,            -- 'pending' | 'success' | 'denied' | 'error'
  idempotency_key TEXT,
  submitted_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  completed_at  TIMESTAMPTZ,
  result        JSONB,
  audit_event_id UUID,
  UNIQUE (action_type_id, idempotency_key)
);

CREATE TABLE tenant_acme.audit_events (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  timestamp     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  trace_id      TEXT,
  category      TEXT NOT NULL,
  type          TEXT NOT NULL,
  subject       JSONB NOT NULL,
  resource      JSONB,
  policy_version TEXT,
  ontology_commit_sha TEXT,
  sources_touched TEXT[],
  outcome       TEXT NOT NULL,
  details       JSONB,
  error         JSONB
) PARTITION BY RANGE (timestamp);

-- Partitioned monthly for query performance + retention management
CREATE TABLE tenant_acme.audit_events_2026_06 PARTITION OF tenant_acme.audit_events
  FOR VALUES FROM ('2026-06-01') TO ('2026-07-01');
-- ... etc

CREATE INDEX ON tenant_acme.audit_events (subject);
CREATE INDEX ON tenant_acme.audit_events (resource);
CREATE INDEX ON tenant_acme.audit_events (trace_id);

CREATE TABLE tenant_acme.source_credentials (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  source_id     TEXT NOT NULL,            -- "salesforce"
  customer_id   TEXT NOT NULL,
  encrypted_payload BYTEA NOT NULL,       -- KMS-encrypted OAuth tokens
  expires_at    TIMESTAMPTZ,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE tenant_acme.workshop_modules (
  id            TEXT PRIMARY KEY,
  commit_sha    TEXT NOT NULL,
  definition    JSONB NOT NULL,
  authored_by   UUID NOT NULL,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- RLS for cross-tenant safety (in addition to schema isolation)
ALTER TABLE tenant_acme.audit_events ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON tenant_acme.audit_events
  USING (current_setting('app.current_customer_id') = 'acme');
```

---

## Appendix B — API Surface

The HTTP API contract. All services follow the same conventions: JSON in/out, Bearer JWT auth, problem-details errors (RFC 7807).

### Ontology Service

```http
GET    /v1/ontology/describe                  # full ontology snapshot
GET    /v1/ontology/openapi.json              # compiled OpenAPI 3.1
GET    /v1/ontology/history                   # commit log
POST   /v1/ontology/commit                    # create new commit

GET    /v1/ontology/object-types
GET    /v1/ontology/object-types/:id
POST   /v1/ontology/object-types
PATCH  /v1/ontology/object-types/:id
DELETE /v1/ontology/object-types/:id

GET    /v1/ontology/action-types
GET    /v1/ontology/action-types/:id
POST   /v1/ontology/action-types
PATCH  /v1/ontology/action-types/:id
DELETE /v1/ontology/action-types/:id

GET    /v1/ontology/markings
POST   /v1/ontology/markings
```

### Action Service

```http
POST   /v1/actions/:actionTypeId/submit       # submit action; returns submission_id
POST   /v1/actions/:actionTypeId/dry-run      # preview; no side effects
GET    /v1/actions/:submissionId              # status + result
GET    /v1/actions/:submissionId/audit        # audit chain
```

### Query Service

```http
POST   /v1/query/objects                      # object-set query
GET    /v1/query/objects/:objectTypeId/:id    # single object lookup
POST   /v1/query/aggregate                    # sum/count/avg
POST   /v1/query/semantic                     # embedding search
POST   /v1/query/cross-source                 # federated via Trino
```

### MCP Gateway

```http
# MCP protocol endpoints (SSE)
GET    /sse                                   # MCP SSE channel
POST   /v1/mcp/tools/call                     # JSON-RPC tool calls
GET    /v1/mcp/tools                          # tool catalog

# OAuth metadata
GET    /.well-known/oauth-protected-resource
GET    /.well-known/oauth-authorization-server
```

### Policy Service

```http
POST   /v1/policy/check                       # single decision
POST   /v1/policy/batch-check
POST   /v1/policy/list-objects                # for query augmentation
POST   /v1/policy/expand                      # debugging
POST   /v1/policy/write                       # update relation tuples
```

### Identity Federation

```http
GET    /v1/auth/login/:idpId                  # start OIDC flow
GET    /v1/auth/callback/:idpId               # OIDC callback
POST   /v1/auth/token/exchange                # RFC 8693
GET    /v1/auth/whoami                        # current session

GET    /v1/auth/sources/:sourceId/connect     # start source OAuth
GET    /v1/auth/sources/:sourceId/callback

POST   /v1/auth/scim/v2/Users                 # SCIM
POST   /v1/auth/scim/v2/Groups
```

### Audit Service

```http
POST   /v1/audit/events                       # internal: ingest event
GET    /v1/audit/events                       # query audit log
GET    /v1/audit/events/:id
GET    /v1/audit/events/correlate/:traceId    # full trace
```

### Functions Runtime

```http
POST   /v1/functions/:functionName/invoke
GET    /v1/functions/:functionName/manifest
POST   /v1/functions/deploy                   # FDE workflow
```

### OSDK Generator

```http
POST   /v1/osdk/build                         # trigger build for commit_sha
GET    /v1/osdk/builds/:buildId
GET    /v1/osdk/latest/:language              # npm/pypi package URL
```

---

The architecture is internally consistent, externally pragmatic, and bounded in scope. Five custom services. Three months to first paying customer. Everything else composed from well-understood open-source infrastructure. The Foundry-style ontology + governance moat is preserved; the OSv2 engineering investment is avoided; the customer's existing systems remain authoritative. This is OpenFoundry as it can actually be built.
