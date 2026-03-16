# KPMG Access & Provisioning Request (v2)

**Type:** Technical
**Status:** In Progress
**Date:** 3-15-26
**Contact:** Dan Zakon (dan@tenex.co)

All tools and licenses provisioned for this engagement would be used exclusively for KPMG project work.

---

## 1. Source Control & Tooling

| Item | Request |
|------|---------|
| **GitHub Organization** | Client-provided GitHub org with all 5 developers as members. Our tooling, AI workflows, and CI/CD are built around GitHub. |
| **GitHub Actions** | CI/CD runners enabled with sufficient minutes for automated testing, builds, and deployments. |
| **Claude Code licenses** | 5 seats on the **Max plan** ($200/seat/mo). This is Anthropic's highest-usage individual tier with the most generous limits, which is critical since Claude Code is our primary AI coding tool and the team uses it heavily throughout the day. Alternatively, Anthropic offers a **Team plan** ($30/seat/mo) or **Enterprise plan** (custom pricing) with centralized billing and admin controls if KPMG prefers a managed/org-level plan. |
| **Cursor licenses** | 5 seats on the **Ultra plan** ($200/seat/mo). Cursor's highest tier, designed for full-time AI-native development with maximum usage. Alternatively, Cursor offers a **Business plan** ($40/seat/mo) or **Enterprise plan** (custom pricing) with SSO, admin controls, and org-wide usage analytics. |

### Dedicated Devices (Optional)

Given the sensitivity of financial data in this engagement, we're open to working on KPMG-provisioned laptops dedicated to this project if that aligns with your security posture. Not a hard requirement on our end, but we want to flag it as an option given the enterprise context.

---

## 2. Compute

| Azure Service | Purpose | Notes |
|---------------|---------|-------|
| **Azure Container Apps** | Primary backend hosting, serverless containers with autoscaling, Dapr, KEDA scaling | Preferred for most services. Lower ops overhead than AKS. |
| **Azure Container Apps Jobs** | Scheduled and event-driven background processing, data ingestion, batch AI processing, ETL | Critical for agentic workflows on schedules or triggers. |
| **Azure Functions** | Lightweight event-driven triggers, webhooks, real-time event processing | Consumption or Premium plan. Glue logic between services. |
| **Azure Durable Functions** | Long-running, stateful orchestration workflows with retry, fan-out/fan-in | Strong fit for multi-step AI agent workflows that need resilience. |
| **Azure Kubernetes Service (AKS)** | Fallback for complex workloads requiring full Kubernetes control or GPU scheduling | May not use in MVP, but avoids delay if scope grows. |

---

## 3. AI & Model Services

This is the most critical section. The platform is AI-heavy. We need broad model access to evaluate and select the best models for each task (accuracy-critical CFO Q&A vs. fast classification vs. document extraction).

### Direct API Keys

We strongly prefer direct API keys from providers. This gives us maximum flexibility, access to the latest model releases, and full control over our integration layer.

| Provider | Key | Purpose |
|----------|-----|---------|
| **Anthropic** | API key | **Near must-have.** Primary model provider. Powers the Claude Agent SDK (our agent framework, see below), Claude Code (dev tooling), and production inference. Access to Claude Opus 4.6, Claude Sonnet 4.6, Claude Haiku 4.5. |
| **OpenAI** | API key | Access to latest models (GPT-5.4, GPT-5.4 Pro) without waiting for Azure deployment cycles. Direct access to Responses API for agentic tool use. |

The Anthropic key in particular is important because the Claude Agent SDK (our planned agent framework) calls the Anthropic API directly. While there's a path to route it through Azure Foundry's Claude endpoint, the direct key is simpler, gives us access to the latest models immediately, and avoids Azure-specific markup on token costs.

### Azure OpenAI Service / Microsoft Foundry

Provision these on Azure as a complement to (or fallback for) direct keys:

| Model | Purpose |
|-------|---------|
| **GPT-5.4** | Latest flagship model. Stronger reasoning, built-in computer use, reliable tool invocation. Designed for agentic workflows at scale. ($2.50/M input, $15/M output) |
| **GPT-5.4 Pro** | Premium variant for deeper analytical work. Evaluates multiple reasoning paths. Best for complex financial analysis where thoroughness matters more than speed. ($30/M input, $180/M output) |
| **GPT-4o** | Multimodal (text + image), useful for analyzing charts and scanned documents |
| **o3** | Most capable reasoning model, complex multi-step analysis. First reasoning model with full tool support for agentic use. |
| **o4-mini** | Efficient reasoning at lower cost for high-volume tasks |
| **text-embedding-3-large** | Vector embeddings for RAG pipeline over financial documents |
| **text-embedding-3-small** | Cost-efficient embeddings for large-scale indexing |

### Claude Models (via Microsoft Foundry)

If the direct Anthropic key is not possible, Claude models are available on Foundry in preview (East US 2 and Sweden Central only):

| Model | Purpose |
|-------|---------|
| **claude-opus-4-6** | Most capable, complex financial reasoning, high-accuracy Q&A |
| **claude-sonnet-4-6** | Balanced performance/cost, primary workhorse model |
| **claude-haiku-4-5** | Fast and cheap, routing, classification, extraction |

> Azure Foundry's Claude endpoint uses the same Messages API as Anthropic's direct API (`/anthropic/v1/messages`), so the Claude Agent SDK can potentially be configured to work through Foundry. However, Foundry Claude is still in preview, model availability is region-limited, and token pricing may differ from Anthropic's direct rates.

### Claude Agent SDK

We plan to build the agent framework using the **Claude Agent SDK** (`@anthropic-ai/claude-agent-sdk`). This is the same engine that powers Claude Code, exposed as a library. It provides:

- Agent loop with autonomous tool use (file reading, command execution, web search)
- MCP (Model Context Protocol) integration for connecting to external tools and data sources
- Subagent orchestration for multi-agent workflows
- Hooks for custom lifecycle management and guardrails

**What this requires:**

- Anthropic API key (direct key preferred; Azure Foundry Claude endpoint is a possible alternative but untested with the SDK in production)
- Network egress to `api.anthropic.com` from Azure VNet (or to the Foundry Claude endpoint if routed through Azure)
- Sufficient API rate limits and TPM allocation

### Azure AI Document Intelligence

| Capability | Notes |
|------------|-------|
| **OCR / Text Extraction** (Read model) | Extracts text from PDFs, scans, Word, Excel, PowerPoint, HTML |
| **Invoice Processing** (Invoice model) | Pre-built model for extracting invoice fields |
| **Layout Analysis** (Layout model) | Table extraction, structure detection from complex financial documents |
| **Custom Document Models** | Train on specific document formats if needed |

---

## 4. Data Services

| Azure Service | Purpose | Notes |
|---------------|---------|-------|
| **Azure Database for PostgreSQL, Flexible Server** | Primary relational database | General Purpose or Memory Optimized tier. Enable pgvector extension. |
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
| **Owner** | Resource Group | Full resource management + ability to assign roles. Preferred: lets us self-serve RBAC for managed identities and service principals without filing tickets. |
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

> **Note on Anthropic access:** If Claude models are accessed via Microsoft Foundry, the **Azure AI User** role on the Foundry resource is required for both user principals and managed identities. If we use direct Anthropic API keys instead, no additional Azure RBAC is needed for Anthropic; the keys are stored in Key Vault and accessed by our application.

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
| **Azure Managed Grafana** | Dashboards and visualization | Useful for operational dashboards. |

---

## 10. Third-Party Integrations

### Rillet (ERP)

- **What it is:** AI-native accounting ERP. Source of truth for financial data: general ledger, AR/AP, revenue recognition, multi-entity consolidation.
- **API:** REST API with OpenAPI spec. Bearer token auth.
- **Environments:** Sandbox (`sandbox.api.rillet.com`) and Production (`api.rillet.com`).
- **What we need:** Rillet API keys (sandbox + production), documentation on the client's Rillet data model, a Rillet technical contact for API questions (per meeting discussion, intro to be facilitated), and network allowlisting for Azure VNet egress.

### Stuut (AR Automation)

- **What it is:** Autonomous accounts receivable platform. AI agents for collections, cash application, payment matching.
- **API:** REST API. Integrates with CRM, ERP, KYC data sources.
- **What we need:** Stuut API keys or service account credentials, API documentation, a Stuut technical contact, and clarity on which data we'll be pulling (invoices, payment status, collections activity, cash application results).

### Sample Data

If available, any sample or representative financial data from the pilot customer would be helpful for development and testing. Anonymized or synthetic data is fine. This doesn't need to come from Rillet or Stuut specifically; any representative dataset that reflects the types of financial data we'll be working with would accelerate development.

### Network Egress for External APIs

Azure Firewall rules to allow outbound HTTPS to:
- `api.rillet.com` / `sandbox.api.rillet.com`
- Stuut API endpoints (TBD)
- `api.anthropic.com` (Claude Agent SDK, Claude Code)
- `api.openai.com` (if using direct OpenAI key)

---

## Open Questions for KPMG

These are the essentials we need answered to begin work. Happy to discuss any of these on a call.

### Before We Start

- **Azure region:** Which region should we deploy to? This constrains model availability (e.g., Claude on Foundry is only in East US 2 and Sweden Central).
- **Subscription/resource group:** New resource group for this project, or existing? Do we get Owner or Contributor access?
- **Direct API keys:** Can we get Anthropic and OpenAI API keys provisioned directly (outside of Azure)? The Anthropic key in particular is important for our agent framework (Claude Agent SDK). If not feasible, we can route through Azure Foundry but would like to understand the constraints.
- **Rillet + Stuut access:** API keys, technical contacts, and sandbox/test environments for both vendors.
- **Budget awareness:** Any spending caps on the subscription we should know about? AI token costs can scale quickly.

### Good to Know Early

- **Environment strategy:** Separate dev/staging/prod resource groups, or single environment for the MVP sprint?
- **Azure policies or naming conventions** we need to follow?
- **Data residency constraints** on where financial data can be stored/processed?
- **Portal access:** Do all 5 developers get Azure portal access?

---

## Summary: Full Service List

### Must-Have (MVP)

1. Azure Container Apps
2. Azure Container Apps Jobs
3. Azure Database for PostgreSQL, Flexible Server (with pgvector)
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
21. Direct Anthropic API key (for Claude Agent SDK + production inference)

### Must-Have (AI Models, one of these paths)

**Path A (Preferred):** Direct Anthropic API key + Direct OpenAI API key
**Path B:** Azure OpenAI Service (GPT-5.4, GPT-5.4 Pro, o3, o4-mini, GPT-4o, embeddings) + Claude models via Microsoft Foundry
**Path C:** Both (maximum flexibility)

### Should-Have

22. Azure Durable Functions
23. Azure Functions
24. Azure Cosmos DB for NoSQL (with vector indexing)
25. Azure Data Lake Storage Gen2
26. Azure DNS Private Zones
27. Azure Firewall
28. Azure Application Gateway / WAF
29. Azure Event Hubs
30. Azure Managed Grafana
31. Direct OpenAI API key

### Provision If Scope Grows

32. Azure Kubernetes Service (AKS)
