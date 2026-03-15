# KPMG — Comprehensive Access & Provisioning Request (v2)

**Type:** Technical
**Status:** [ ] In Progress
**Date:** 3-15-26
**Contact:** Dan Zakon (dan@tenex.co)

---

## Context

We're building an AI-native financial intelligence platform (referred to as "PESCALE" in the kickoff discussions) with a CFO agent that ingests data from Rillet (ERP) and Stuut (AR automation), provides automated 13-week cash flow forecasting, surfaces financial variances and stressors, and enables natural-language Q&A over financial data with high accuracy requirements. This document expands the original access request to be liberal and forward-looking, per the guidance from the KPMG infrastructure team.

**Team size:** 4–6 developers
**Emails:** dan@tenex.co, brandon@tenex.co, scott@tenex.co, cj@tenex.co, jason@tenex.co

---

## 1. Source Control & Tooling

| Item | Request |
|------|---------|
| **GitHub Organization** | Client-provided GitHub org with all 5 developers as members. Our tooling, AI workflows, and CI/CD are built around GitHub. |
| **GitHub Actions** | CI/CD runners enabled with sufficient minutes for automated testing, builds, and deployments. |
| **Claude Code licenses** | 5 seats. This is a direct Anthropic product — our primary AI coding tool. Dramatically accelerates delivery. |
| **Cursor licenses** | 5 seats. Secondary AI coding tool. Provides AI-assisted IDE with multi-model support. |

---

## 2. Compute

| Azure Service | Purpose | Notes |
|---------------|---------|-------|
| **Azure Container Apps** | Primary backend hosting — serverless containers with autoscaling, built-in Dapr, KEDA scaling | Preferred for most services. Lower ops overhead than AKS. |
| **Azure Container Apps Jobs** | Scheduled and event-driven background processing — data ingestion, batch AI processing, ETL | Critical for agentic workflows on schedules or triggers. |
| **Azure Functions** | Lightweight event-driven triggers, webhooks, real-time event processing | Consumption or Premium plan. Glue logic between services. |
| **Azure Durable Functions** | Long-running, stateful orchestration workflows with retry, fan-out/fan-in | Strong fit for multi-step AI agent workflows that need resilience. |
| **Azure Kubernetes Service (AKS)** | Fallback for complex workloads requiring full Kubernetes control or GPU scheduling | May not use in MVP, but avoids delay if scope grows. |

---

## 3. AI & Model Services

This is the most critical section. The platform is AI-heavy. We need broad model access to evaluate and select the best models for each task (accuracy-critical CFO Q&A vs. fast classification vs. document extraction). We strongly prefer **direct API keys** from providers where possible — this gives us maximum flexibility, access to the latest model releases, and full control over our integration layer.

### Direct API Keys (Preferred)

| Provider | Key | Purpose |
|----------|-----|---------|
| **Anthropic** | API key | Primary model provider. Powers the Claude Agent SDK (our agent framework), Claude Code (dev tooling), and production inference. Required for Claude Opus 4.6, Claude Sonnet 4.6, Claude Haiku 4.5. |
| **OpenAI** | API key | Access to latest models (GPT-4.1, o3, o4-mini) without waiting for Azure deployment cycles. Direct access to Responses API for agentic tool use. |

> Direct API keys ensure we're never blocked by Azure model catalog deployment timelines and can use the latest capabilities the moment they're released.

### Azure OpenAI Service / Microsoft Foundry (Complementary)

If direct keys aren't feasible, or as a complement to them, provision the following on Azure:

| Model | Purpose |
|-------|---------|
| **GPT-4.1** | Latest mainline model — strong at coding, long-context, instruction following |
| **GPT-4.1-mini** | Cost-efficient alternative for high-volume tasks |
| **GPT-4.1-nano** | Ultra-lightweight for classification, routing, simple extraction |
| **GPT-4o** | Multimodal (text + image) — useful for analyzing charts, scanned documents |
| **o3** | Most capable reasoning model — complex financial calculations, multi-step analysis. First reasoning model with full tool support for agentic use. |
| **o4-mini** | Efficient reasoning model — high-volume reasoning at lower cost |
| **text-embedding-3-large** | Vector embeddings for RAG pipeline over financial documents |
| **text-embedding-3-small** | Cost-efficient embeddings for large-scale indexing |

### Claude Models (via Microsoft Foundry, if direct key not available)

Available on Foundry in preview (East US 2 and Sweden Central only):

| Model | Purpose |
|-------|---------|
| **claude-opus-4-6** | Most capable — complex financial reasoning, high-accuracy Q&A |
| **claude-sonnet-4-6** | Balanced performance/cost — primary workhorse model |
| **claude-haiku-4-5** | Fast and cheap — routing, classification, extraction |

### Claude Agent SDK

We plan to build the agent framework using the **Claude Agent SDK** (`@anthropic-ai/claude-agent-sdk`). This is the same engine that powers Claude Code, exposed as a library. It provides:
- Agent loop with autonomous tool use (file reading, command execution, web search)
- MCP (Model Context Protocol) integration for connecting to external tools and data sources
- Subagent orchestration for multi-agent workflows
- Hooks for custom lifecycle management and guardrails

**Requirements for Claude Agent SDK:**
- Direct Anthropic API key (the SDK calls the Anthropic API directly)
- Network egress to `api.anthropic.com` from Azure VNet
- Sufficient API rate limits / token-per-minute (TPM) allocation from Anthropic

### Azure AI Document Intelligence

| Capability | Notes |
|------------|-------|
| **OCR / Text Extraction** (Read model) | Extracts text from PDFs, scans, Word, Excel, PowerPoint, HTML |
| **Invoice Processing** (Invoice model) | Pre-built model for extracting invoice fields |
| **Layout Analysis** (Layout model) | Table extraction, structure detection from complex financial documents |
| **Custom Document Models** | Train on KPMG-specific document formats if needed |

---

## 4. Data Services

| Azure Service | Purpose | Notes |
|---------------|---------|-------|
| **Azure Database for PostgreSQL — Flexible Server** | Primary relational database | General Purpose or Memory Optimized tier. Enable pgvector extension. |
| **Azure Cosmos DB for NoSQL** | Document store with native vector search (DiskANN) | For high-scale unstructured financial data, real-time vector queries. Strong candidate if data volume is large. |
| **Azure Blob Storage** | File and object storage | Financial documents, PDFs, exports, model artifacts. Hot + Cool tiers. |
| **Azure Data Lake Storage Gen2** | Large-scale data lake for raw financial data ingestion | If data volumes warrant dedicated lake architecture. |
| **Azure Managed Redis** | In-memory caching and session management | Cache AI responses, rate limiting, session state. |

---

## 5. Vector Database / Search

Critical for the RAG (Retrieval-Augmented Generation) pipeline that powers the CFO agent's Q&A accuracy.

| Azure Service | Purpose | Notes |
|---------------|---------|-------|
| **Azure AI Search** | Full-featured vector + hybrid search with semantic ranking | Best option for RAG: combines keyword search, vector search, and semantic reranking. Built-in chunking and vectorization. |
| **Azure Cosmos DB (vector indexing)** | Native vector search alongside operational data | Good if we want vectors co-located with source documents. Uses DiskANN for high performance. |
| **PostgreSQL + pgvector** | Vector search within existing Postgres | Simplest option. May be sufficient for MVP. Request pgvector extension enabled. |

> **Recommendation:** Provision Azure AI Search AND enable pgvector on PostgreSQL. Start simple, scale to dedicated vector search as data grows.

---

## 6. Networking & Security

| Azure Service | Purpose | Notes |
|---------------|---------|-------|
| **Azure Virtual Network (VNet)** | Network isolation for all services | Minimum 3 subnets: app, private link, perimeter. |
| **Azure Private Endpoints / Private Link** | Secure connectivity to AI services, databases, storage without public internet exposure | Critical for financial data. |
| **Azure API Management** | API gateway for external and internal API traffic | AI Gateway capabilities: token tracking, rate limiting, load balancing across model deployments. |
| **Azure Application Gateway / WAF** | Web application firewall for frontend traffic | If user-facing web application. |
| **Azure DNS (Private Zones)** | DNS resolution within VNet for private endpoints | Required for private endpoint connectivity. |
| **Network Security Groups (NSGs)** | Network access control rules | Per-subnet traffic filtering. |
| **Azure Firewall** | Centralized egress filtering | Control outbound traffic to Rillet, Stuut, Anthropic, OpenAI APIs. |

---

## 7. Identity & Access Management

| Azure Service | Purpose | Notes |
|---------------|---------|-------|
| **Microsoft Entra ID** | Identity provider for team members and service identities | 5 developer accounts with MFA. |
| **Managed Identities** | Passwordless auth for Azure services | System-assigned for Container Apps, Functions. |
| **Service Principals** | Application identities for CI/CD and integrations | GitHub Actions OIDC federation. |
| **Azure Key Vault** | Secrets, certificates, credential management | Store all API keys, connection strings, third-party credentials. |

### RBAC Roles

We'd like the broadest permissions feasible to avoid access friction during the build. Ideally:

| Role | Scope | Purpose |
|------|-------|---------|
| **Owner** | Resource Group | Full resource management + ability to assign roles. Preferred — lets us self-serve RBAC for managed identities and service principals without filing tickets. |
| **Contributor** | Resource Group | Acceptable fallback if Owner is too broad. Covers resource creation and management but not role assignments. |

If neither Owner nor Contributor at the resource group level is possible, we'd need at minimum:

| Role | Scope |
|------|-------|
| Cognitive Services OpenAI Contributor | Azure OpenAI resources |
| Cognitive Services User | AI Services (Document Intelligence) |
| Azure AI User | Microsoft Foundry resources (if Claude models are accessed via Foundry) |
| Search Index Data Contributor | Azure AI Search |
| Search Service Contributor | Azure AI Search |
| Storage Blob Data Contributor | Storage Accounts |
| Cosmos DB Operator | Cosmos DB accounts |
| Key Vault Secrets Officer | Key Vault |
| AcrPush + AcrPull | Container Registry |

> **Note on Anthropic access:** If Claude models are accessed via Microsoft Foundry, the **Azure AI User** role on the Foundry resource is required for both user principals and managed identities. If we use direct Anthropic API keys instead, no additional Azure RBAC is needed for Anthropic — the keys are stored in Key Vault and accessed by our application.

---

## 8. Messaging & Event-Driven Architecture

| Azure Service | Purpose | Notes |
|---------------|---------|-------|
| **Azure Service Bus** | Reliable message queuing between services | Dead-letter queues, sessions, transactions. Core for async pipeline. |
| **Azure Event Grid** | Lightweight event routing and pub/sub | Trigger processing on new documents in blob storage, data syncs from Rillet/Stuut. |
| **Azure Event Hubs** | High-throughput event streaming | If real-time financial data streaming is needed at scale. |

---

## 9. Monitoring & Observability

| Azure Service | Purpose | Notes |
|---------------|---------|-------|
| **Azure Monitor** | Platform-level metrics and alerts | |
| **Application Insights** | APM, distributed tracing, custom metrics | Critical for tracing AI agent execution paths and latency. |
| **Log Analytics Workspace** | Centralized log aggregation and querying (KQL) | All services ship logs here. |
| **Azure Managed Grafana** | Dashboards and visualization | Optional — useful for operational dashboards. |

---

## 10. Third-Party Integrations

### Rillet (ERP)

- **What it is:** AI-native accounting ERP. Source of truth for financial data — general ledger, AR/AP, revenue recognition, multi-entity consolidation.
- **API:** REST API with OpenAPI spec. Bearer token auth.
- **Environments:** Sandbox (`sandbox.api.rillet.com`) and Production (`api.rillet.com`).
- **What we need:**
  - [ ] Rillet API keys (sandbox + production)
  - [ ] Documentation on the client's Rillet data model
  - [ ] Test/sandbox environment with realistic financial data
  - [ ] Rillet technical contact for API questions (per meeting: intro to be facilitated)
  - [ ] Network allowlisting for Azure VNet egress

### Stuut (AR Automation)

- **What it is:** Autonomous accounts receivable platform. AI agents for collections, cash application, payment matching.
- **API:** REST API. Integrates with CRM, ERP, KYC data sources.
- **What we need:**
  - [ ] Stuut API keys or service account credentials
  - [ ] Stuut API documentation
  - [ ] Test/sandbox environment
  - [ ] Stuut technical contact
  - [ ] Clarity on which data we pull (invoices, payment status, collections activity, cash application results)

### Network Egress for External APIs

Azure Firewall rules to allow outbound HTTPS to:
- `api.rillet.com` / `sandbox.api.rillet.com`
- Stuut API endpoints (TBD)
- `api.anthropic.com` (Claude Agent SDK, Claude Code)
- `api.openai.com` (if using direct OpenAI key)

---

## Open Questions for KPMG

These are the essentials we need answered to begin work. We've kept this short — happy to discuss any of these on a call.

### Must-Answer Before We Start

- [ ] **Azure region:** Which region should we deploy to? This constrains model availability (e.g., Claude on Foundry is only in East US 2 and Sweden Central).
- [ ] **Subscription/resource group:** New resource group for this project, or existing? Do we get Owner or Contributor access?
- [ ] **Direct API keys:** Can we get Anthropic and OpenAI API keys provisioned directly (outside of Azure), or must everything go through Azure/Foundry?
- [ ] **Rillet + Stuut sandbox access:** API keys, technical contacts, and test data for both vendors.
- [ ] **Budget awareness:** Any spending caps on the subscription we should know about? AI token costs can scale quickly.

### Good to Know Early

- [ ] **Environment strategy:** Separate dev/staging/prod resource groups, or single environment for the MVP sprint?
- [ ] **Azure policies or naming conventions** we need to follow?
- [ ] **Data residency constraints** on where financial data can be stored/processed?
- [ ] **Portal access:** Do all 5 developers get Azure portal access?

---

## Summary: Full Service List

### Must-Have (MVP)

1. Azure Container Apps
2. Azure Container Apps Jobs
3. Azure Database for PostgreSQL — Flexible Server (with pgvector)
4. Azure Blob Storage
5. Azure Managed Redis
6. Azure Container Registry
7. Azure Key Vault
8. Azure Monitor / Application Insights / Log Analytics
9. Azure Virtual Network (with subnets + NSGs)
10. Azure Private Endpoints / Private Link
11. Azure AI Document Intelligence
12. Azure AI Search
13. Azure API Management
14. Azure Service Bus
15. Azure Event Grid
16. Microsoft Entra ID (5 developer accounts + managed identities)
17. RBAC: Owner or Contributor on resource group
18. GitHub Organization + GitHub Actions
19. Claude Code licenses (5 seats)
20. Cursor licenses (5 seats)

### Must-Have (AI Models — one of these paths)

**Path A (Preferred):** Direct Anthropic API key + Direct OpenAI API key
**Path B:** Azure OpenAI Service (GPT-4.1, GPT-4.1-mini, o3, o4-mini, GPT-4o, embeddings) + Claude models via Microsoft Foundry
**Path C:** Both (maximum flexibility)

### Should-Have

21. Azure Durable Functions
22. Azure Functions
23. Azure Cosmos DB for NoSQL (with vector indexing)
24. Azure Data Lake Storage Gen2
25. Azure DNS Private Zones
26. Azure Firewall
27. Azure Application Gateway / WAF
28. Azure Event Hubs
29. Azure Managed Grafana

### Provision If Scope Grows

30. Azure Kubernetes Service (AKS)
