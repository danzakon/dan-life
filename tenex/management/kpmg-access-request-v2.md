# KPMG / PESCALE — Comprehensive Access & Provisioning Request (v2)

**Type:** Technical
**Status:** [ ] In Progress
**Date:** 3-15-26
**Contact:** Dan Zakon (dan@tenex.co)

---

## Context

We're building PESCALE — an AI-native financial intelligence platform with a CFO agent that ingests data from Rillet (ERP) and Stuut (AR automation), provides automated 13-week cash flow forecasting, surfaces financial variances and stressors, and enables natural-language Q&A over financial data with high accuracy requirements. This document expands the original access request to be liberal and forward-looking, per the guidance from the KPMG infrastructure team.

**Team size:** 4–6 developers
**Emails:** dan@tenex.co, brandon@tenex.co, scott@tenex.co, cj@tenex.co, jason@tenex.co

---

## 1. Source Control & Tooling

| Item | Request |
|------|---------|
| **GitHub Organization** | Client-provided GitHub org with all 5 developers as members. Our team's tooling, AI workflows, and CI/CD are built around GitHub. |
| **GitHub Actions** | CI/CD runners enabled with sufficient minutes for automated testing, builds, and deployments. |
| **AI Coding Tools** | Claude Code and/or Cursor licenses for team (5 seats). Highest-leverage investment in delivery velocity. |

---

## 2. Compute

| Azure Service | Purpose | Notes |
|---------------|---------|-------|
| **Azure Container Apps** | Primary backend hosting — serverless containers with autoscaling, built-in Dapr, KEDA scaling | Preferred for most services. Lower ops overhead than AKS. |
| **Azure Container Apps Jobs** | Scheduled and event-driven background processing — data ingestion pipelines, batch AI processing, ETL | Critical for agentic workflows that run on schedules or triggers. |
| **Azure Kubernetes Service (AKS)** | Fallback for complex workloads requiring full Kubernetes control, custom networking, or GPU scheduling | Provision as a safety net — may not use in MVP, but avoids delay if needed. |
| **Azure Functions** | Lightweight event-driven triggers, webhooks, real-time event processing | Consumption or Premium plan. Useful for glue logic between services. |
| **Azure Durable Functions** | Long-running, stateful agentic orchestration workflows with retry, fan-out/fan-in | Strong fit for multi-step AI agent workflows that need resilience. |

---

## 3. AI & Model Services

This is the most critical section. PESCALE is an AI-heavy platform. We need broad model access to evaluate and select the best models for each task (accuracy-critical CFO Q&A vs. fast summarization vs. document extraction).

### Azure OpenAI Service / Microsoft Foundry

| Model | Purpose |
|-------|---------|
| **GPT-4o** | Primary reasoning model for CFO agent Q&A, financial analysis |
| **GPT-4o-mini** | Cost-optimized model for lower-stakes tasks (summarization, classification, routing) |
| **GPT-4 Turbo** | Fallback high-capability model |
| **o1 / o1-mini** | Deep reasoning for complex financial calculations, multi-step analysis |
| **text-embedding-ada-002 / text-embedding-3-large** | Vector embeddings for RAG pipeline over financial documents |
| **GPT-image-1** | If document/chart image analysis is needed |

### Anthropic Claude (via Microsoft Foundry)

| Model | Purpose |
|-------|---------|
| **Claude Sonnet 4** | Alternative reasoning model — critical for evaluating best-fit per task |
| **Claude Haiku** | Fast, cheap alternative for routing and classification |

### Other Foundry Models

| Model | Purpose |
|-------|---------|
| **DeepSeek** | Cost-effective alternative for certain reasoning tasks |
| **Mistral Large** | European-origin model, potential compliance advantages |

### Direct API Keys (if Azure model catalog is insufficient)

| Provider | Purpose |
|----------|---------|
| **Anthropic API key** | Direct access to latest Claude models if Azure deployment lags |
| **OpenAI API key** | Direct access to latest OpenAI models, including any not yet on Azure |

> **Key question for KPMG:** Does the Azure subscription include Microsoft Foundry (formerly Azure AI Foundry) access with the full model catalog? Or do we need separate API keys provisioned for each provider?

### Azure AI Services (Cognitive Services)

| Service | Purpose |
|---------|---------|
| **Azure AI Document Intelligence** | OCR, document extraction, invoice processing, form recognition — critical for ingesting financial documents (PDFs, scanned invoices, bank statements) |
| **Azure AI Speech** | If voice interaction with CFO agent is in scope |
| **Azure AI Language** | Named entity recognition, sentiment analysis, key phrase extraction from financial text |
| **Azure AI Content Safety** | Guardrails for AI-generated financial advice |

### Azure AI Foundry / Agent Service

| Service | Purpose |
|---------|---------|
| **Microsoft Foundry Agent Service** | Managed agent orchestration runtime — handles conversations, tool calls, content safety. Evaluate as alternative to custom agent framework. |
| **AI Foundry Portal access** | Model playground, prompt experimentation, evaluation runs |

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

This is critical for the RAG (Retrieval-Augmented Generation) pipeline that powers the CFO agent's Q&A accuracy.

| Azure Service | Purpose | Notes |
|---------------|---------|-------|
| **Azure AI Search** | Full-featured vector + hybrid search with semantic ranking | Best option for RAG: combines keyword search, vector search, and semantic reranking. Built-in chunking and vectorization. |
| **Azure Cosmos DB (vector indexing)** | Native vector search alongside operational data | Good if we want vectors co-located with source documents. Uses DiskANN for high performance. |
| **PostgreSQL + pgvector** | Vector search within existing Postgres | Simplest option. May be sufficient for MVP. Request pgvector extension enabled. |

> **Recommendation:** Provision Azure AI Search AND enable pgvector on PostgreSQL. This gives us flexibility to start simple and scale to dedicated vector search as data grows.

---

## 6. Networking & Security

| Azure Service | Purpose | Notes |
|---------------|---------|-------|
| **Azure Virtual Network (VNet)** | Network isolation for all services | Minimum 3 subnets: app subnet, private link subnet, perimeter subnet. |
| **Azure Private Endpoints / Private Link** | Secure connectivity to Azure AI, databases, storage without public internet exposure | Critical for financial data. All AI services and databases should be accessible only via private endpoints. |
| **Azure API Management** | API gateway for all external and internal API traffic | Includes AI Gateway capabilities for model governance, token tracking, rate limiting, load balancing across model deployments. Supports MCP server and A2A agent protocols. |
| **Azure Application Gateway / WAF** | Web application firewall for frontend traffic | If there's a user-facing web application. |
| **Azure DNS (Private Zones)** | DNS resolution within VNet for private endpoints | Required for private endpoint connectivity. |
| **Network Security Groups (NSGs)** | Fine-grained network access control rules | Per-subnet traffic filtering. |
| **Azure Firewall** | Centralized egress filtering | Control outbound traffic from VNet to third-party APIs (Rillet, Stuut). |

---

## 7. Identity & Access Management

| Azure Service | Purpose | Notes |
|---------------|---------|-------|
| **Microsoft Entra ID (Azure AD)** | Identity provider for all team members and service identities | 5 developer accounts with MFA. |
| **Managed Identities** | Passwordless authentication for Azure services | System-assigned for Container Apps, Functions. No API key management needed. |
| **Service Principals** | Application identities for CI/CD pipelines and external integrations | GitHub Actions OIDC federation for secure deployments. |
| **Azure RBAC** | Role-based access control across all resources | Request Contributor role on the resource group. Specific roles: Cognitive Services OpenAI User, Storage Blob Data Contributor, Key Vault Secrets Officer, Azure AI Developer. |
| **Azure Key Vault** | Secrets, certificates, and credential management | Store all API keys, connection strings, third-party credentials. |

### Specific RBAC Roles Needed

| Role | Scope | Purpose |
|------|-------|---------|
| Contributor | Resource Group | General resource management |
| Cognitive Services OpenAI User | Azure OpenAI resources | Model deployments and inference |
| Cognitive Services User | AI Services | Document Intelligence, Speech, Language |
| Search Index Data Contributor | Azure AI Search | Manage search indexes and data |
| Storage Blob Data Contributor | Storage Accounts | Read/write blob data |
| Cosmos DB Operator | Cosmos DB accounts | Database operations |
| Key Vault Secrets Officer | Key Vault | Manage secrets |
| Azure AI Developer | Foundry resources | Full AI development access |
| AcrPush / AcrPull | Container Registry | Push and pull container images |

---

## 8. Messaging & Event-Driven Architecture

| Azure Service | Purpose | Notes |
|---------------|---------|-------|
| **Azure Service Bus** | Reliable message queuing between services | Dead-letter queues, sessions, transactions. Core for async processing pipeline. |
| **Azure Event Grid** | Lightweight event routing and pub/sub | Trigger processing when new documents arrive in blob storage, when data syncs from Rillet/Stuut. |
| **Azure Event Hubs** | High-throughput event streaming | If real-time financial data streaming is needed at scale. |

---

## 9. Monitoring & Observability

| Azure Service | Purpose | Notes |
|---------------|---------|-------|
| **Azure Monitor** | Platform-level metrics and alerts | |
| **Application Insights** | APM, distributed tracing, custom metrics | Critical for tracing AI agent execution paths and latency. |
| **Log Analytics Workspace** | Centralized log aggregation and querying (KQL) | All services should ship logs here. |
| **Azure Managed Grafana** | Dashboards and visualization | Optional but useful for real-time operational dashboards. |

---

## 10. Third-Party Integrations

### Rillet (ERP)

- **What it is:** AI-native accounting ERP. Source of truth for financial data — general ledger, accounts receivable/payable, revenue recognition, multi-entity consolidation.
- **API:** REST API with OpenAPI specification. Authentication via Bearer token (API key).
- **Environments:** Sandbox (sandbox.api.rillet.com) and Production (api.rillet.com).
- **What we need from KPMG:**
  - [ ] Rillet API keys (sandbox + production) or service account credentials
  - [ ] Documentation on the client's Rillet data model and configuration
  - [ ] Test/sandbox Rillet environment with realistic financial data
  - [ ] Rillet technical contact for API questions
  - [ ] Network allowlisting if Rillet API calls need to originate from Azure VNet (firewall rules)

### Stuut (AR Automation)

- **What it is:** Autonomous accounts receivable platform. AI agents for collections, cash application, payment matching.
- **API:** REST API integration. Connects with CRM, CMS, ERP, KYC data sources.
- **What we need from KPMG:**
  - [ ] Stuut API keys or service account credentials
  - [ ] Stuut API documentation and SDK access
  - [ ] Test/sandbox Stuut environment
  - [ ] Stuut technical contact for integration questions
  - [ ] Clarity on which Stuut data we need to pull (invoices, payment status, collections activity, cash application results)

### Network Connectivity for Third-Party APIs

- **Azure Firewall egress rules** to allow outbound HTTPS to:
  - `api.rillet.com` / `sandbox.api.rillet.com`
  - Stuut API endpoints (TBD)
  - Any Anthropic/OpenAI direct API endpoints if used
- **Azure API Management** as a unified gateway for third-party API calls (rate limiting, retry, logging)

---

## 11. Document Processing Pipeline

Given the financial domain, we anticipate heavy document processing:

| Capability | Azure Service | Notes |
|------------|---------------|-------|
| **OCR / Text Extraction** | Azure AI Document Intelligence (Read model) | Extracts printed and handwritten text from PDFs, scans. Supports Word, Excel, PowerPoint, HTML. |
| **Invoice Processing** | Azure AI Document Intelligence (Invoice model) | Pre-built model for extracting invoice fields. |
| **Receipt Processing** | Azure AI Document Intelligence (Receipt model) | If expense receipt processing is in scope. |
| **Custom Document Models** | Azure AI Document Intelligence (Custom models) | Train models on KPMG-specific document formats. |
| **Layout Analysis** | Azure AI Document Intelligence (Layout model) | Table extraction, structure detection from complex financial documents. |
| **Document Storage** | Azure Blob Storage + metadata in PostgreSQL/Cosmos DB | Raw documents in blob, extracted data in database. |
| **Document Chunking & Embedding** | Azure AI Search (integrated vectorization) or custom pipeline | Split documents into chunks, generate embeddings, index for RAG. |

---

## 12. Additional Services to Consider

| Azure Service | Purpose | Priority |
|---------------|---------|----------|
| **Azure Front Door** | Global load balancing and CDN for frontend | If user-facing web app is deployed. |
| **Azure Static Web Apps** | Frontend hosting | If dashboard/UI is a static SPA. |
| **Azure Notification Hubs** | Push notifications | If mobile alerts for CFO insights. |
| **Azure Logic Apps** | Low-code workflow automation | For non-developer-facing integrations. |
| **Azure Batch** | Large-scale parallel compute | If batch processing of huge document sets is needed. |
| **Azure OpenAI Provisioned Throughput Units (PTUs)** | Reserved AI capacity | For predictable latency and cost on production workloads. Consider once usage patterns are established. |
| **GitHub Copilot** | AI-assisted development for the team | Alternative to Claude Code/Cursor if client prefers Microsoft ecosystem. |

---

## Open Questions for KPMG

### Architecture & Scope

- [ ] **Azure subscription structure:** Will we work within an existing subscription/resource group, or will a new one be provisioned for PESCALE?
- [ ] **Azure region:** Which region(s) should we deploy to? (Affects model availability — e.g., Claude models are only available in East US 2 and Sweden Central.)
- [ ] **Environment strategy:** Do we need separate resource groups for dev/staging/production, or a single environment for the MVP sprint?
- [ ] **Existing Azure policies:** Are there Azure Policy guardrails, naming conventions, or tagging requirements we need to follow?
- [ ] **Budget/spending limits:** Are there spending caps on the Azure subscription? AI token costs can scale quickly — need to understand limits.

### AI & Models

- [ ] **Model access approvals:** Some Azure OpenAI models (o1, GPT-image, DALL-E) require access applications. Has this been done, or should we submit requests?
- [ ] **Azure AI Foundry / Microsoft Foundry access:** Is this provisioned in the subscription? We need access to the model catalog and agent service.
- [ ] **Direct provider API keys:** If Azure model catalog doesn't include all models we need (e.g., latest Anthropic or OpenAI releases), can we get direct API keys provisioned?
- [ ] **Token usage limits:** Are there per-model or aggregate token-per-minute (TPM) limits we should be aware of?

### Data & Integration

- [ ] **Rillet environment details:** Which Rillet instance is the pilot customer on? Do we get our own sandbox, or share one?
- [ ] **Stuut environment details:** Same question — sandbox access, API credentials, technical contact.
- [ ] **Sample financial data:** Can we get a representative dataset for development? Anonymized/synthetic is fine.
- [ ] **Data residency requirements:** Are there regulatory constraints on where financial data can be stored/processed?
- [ ] **Data retention policies:** How long must we retain raw documents, processed data, AI interaction logs?

### Security & Compliance

- [ ] **Compliance frameworks:** SOC 2, SOX, PCI-DSS, or other compliance requirements we need to design for?
- [ ] **Data classification:** What sensitivity level is the financial data? Does it require encryption at rest + in transit (assume yes)?
- [ ] **Audit logging requirements:** Do we need immutable audit logs for all AI decisions on financial data?
- [ ] **Penetration testing:** Is there a security review or pen test requirement before production?

### Operations & Access

- [ ] **VPN or bastion access:** How do we access Azure resources for debugging/management? Azure Bastion, VPN gateway, or direct portal access?
- [ ] **Azure portal access:** Do all 5 developers get portal access, or only specific roles?
- [ ] **Support plan:** What Azure support tier is active? (Standard, Professional Direct, etc.)
- [ ] **Incident response:** Who do we contact for Azure infrastructure issues?

---

## Summary: Full Service List

For quick reference, here's every Azure service we're requesting:

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
11. Azure OpenAI Service (GPT-4o, GPT-4o-mini, embeddings)
12. Azure AI Document Intelligence
13. Azure AI Search
14. Azure API Management
15. Azure Service Bus
16. Azure Event Grid
17. Microsoft Entra ID (5 developer accounts + managed identities)
18. Azure RBAC (roles listed in Section 7)
19. GitHub Organization + GitHub Actions

### Should-Have (Strong Recommendation)
20. Azure Durable Functions
21. Azure Functions
22. Anthropic Claude models (via Foundry or direct API key)
23. Azure Cosmos DB for NoSQL (with vector indexing)
24. Azure AI Foundry / Agent Service
25. Azure DNS Private Zones
26. Azure Firewall
27. Azure Application Gateway / WAF
28. AI Coding Tools (Claude Code / Cursor — 5 seats)
29. Azure Data Lake Storage Gen2

### Nice-to-Have (Future-Proofing)
30. Azure Kubernetes Service (AKS)
31. Azure Event Hubs
32. Azure Front Door
33. Azure Static Web Apps
34. Azure Managed Grafana
35. Azure Batch
36. Azure OpenAI PTUs (Provisioned Throughput)
37. Direct Anthropic API key
38. Direct OpenAI API key

---

## Next Steps

- [ ] Send this document to KPMG infrastructure contact for provisioning
- [ ] Get answers to open questions (Section 12)
- [ ] Receive Rillet API documentation and sandbox credentials
- [ ] Receive Stuut API documentation and sandbox credentials
- [ ] Confirm Azure region and subscription structure
- [ ] Confirm model access and any required application submissions
- [ ] Technical intro call between Tenex and Rillet engineering (per meeting discussion)
