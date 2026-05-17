# AI Gateway / LLM Ops / Token Spend Governance — 2025-2026 Landscape

**Date:** 2026-05-17
**Status:** Raw research findings

---

## 1. The Problem: Enterprises Are Burning 7- and 8-Figure Token Budgets Blind

The enterprise AI bill has crossed from "ignore it, it's small" to a top-5 line item in IT budgets in roughly 18 months. The structural change driving everything else is that **coding agents** (Claude Code, Codex, Cursor, Cline, Devin) burn tokens at unprecedented rates per developer-hour. Anthropic's own Claude Code docs admit the median: **~$13 per developer per active day, $150-$250 per developer per month**, with the 90th percentile under $30/active day. At enterprise scale (1,000 devs × $200/mo × 12) that's $2.4M/year for one tool, ignoring chat/Cowork/other apps.

Anthropic explicitly tells customers to throttle: at 500+ users they recommend dropping per-user TPM allocation to 10-15K (from 200-300K for 1-5 user teams) because organization-level rate limits otherwise blow up.

The visibility problem has three dimensions:

1. **Who** — per-employee, per-team, per-app, per-agent attribution. AWS Bedrock loses developer-level attribution entirely (it shows up as marketplace purchases). Anthropic and Cursor both expose per-API-key/per-email out of the box; OpenAI requires supplemental APIs.
2. **What** — per-model, input vs. output, cached vs. uncached, thinking tokens vs. output tokens (Claude bills thinking as output, which can dominate). Cursor's Composer 1.5 at $3.50/M input + $17.50/M output and Composer 2 at $0.50/$2.50 are an order of magnitude apart — model selection per request matters financially.
3. **Why** — translating "Dev X consumed 2M Opus input tokens last Tuesday" into "payments team's refactor initiative is running $400/week on AI."

Most CIOs in early 2026 do not allocate tokens to teams. It's still a free-for-all or rough per-seat. Token chargeback / showback is emerging as the new **AI FinOps** category, deliberately analogous to cloud FinOps (Apptio, CloudHealth, Vantage). Vantage's own framing: "AI Costs Are Cloud Costs Now" — tag the spend, group it by team or project, roll it up into something a non-technical stakeholder can act on, build unit economics (cost per PR merged, cost per ticket closed).

---

## 2. Enterprise Contracting Reality in 2025-2026

### Anthropic — the most dramatic 2026 story

Anthropic eliminated bundled-token enterprise seat plans in a phased rollout (Nov 2025 renewal cohort → Feb 2026 new contracts → **March 8, 2026** hard cutoff for legacy bundled-token plans). The new model:

- **$20/seat/month base** ("Enterprise self-serve"), covers Claude.ai chat + Claude Code + Cowork on a single seat. Min 20 seats annual, 50 seats for sales-assisted.
- **Every token billed at standard API rates on top.** Mandatory monthly spend commitment (Anthropic estimates your usage, you pay the commitment whether you hit it or not).
- **API volume discounts (10-15%) removed** under the new structure.
- Claude Team capped at 150 seats, still bundles usage but lacks SCIM/audit/1M-context — there is no flat-fee Enterprise upgrade path.

NPI Financial and Redress Compliance both forecast **higher total TCO** under the new model despite the lower headline seat fee. IntuitionLabs' CEO Adrien Laurent: "the seat fee no longer bundles any usage allowance at all. Every token gets billed at standard API rates on top of the base seat." For one 800-user organization, the modeled gap between Team and Enterprise was **$336K-$1.4M annually**.

Benchmark data (VendorBenchmark, 140+ negotiations) on what enterprises actually pay:

| Annual API Commit | Sonnet input discount | Output discount | Haiku discount |
|---|---|---|---|
| $250K-$499K | 12-18% | 12-18% | 10-15% |
| $500K-$999K | 18-24% | 18-24% | 15-20% |
| $1M-$2.4M | 24-30% | 24-30% | 20-26% |
| $2.5M+ | 28-36% | 28-36% | 24-32% |

Multi-year (2-3 yr) commits beat annual by 20-35%. Routing through **AWS Bedrock EDP overlay** can layer 20-30% on top — for orgs with under-utilized AWS EDP this is the cleanest play.

Other Anthropic enterprise levers:
- Batch API: flat 50% off both input and output (not negotiated, structural).
- Prompt caching: up to 90% off repeated input.
- **99.99% SLA** announced March 2026 for enterprise customers.
- Most-favored-nation clauses and model continuity clauses are the new negotiation frontier (model performance guarantees not yet standard).

### OpenAI — Scale Tier + Reserved Capacity

OpenAI's enterprise model is more clearly bifurcated:

**Scale Tier** = on-demand-style commit to TPM units (token units) per model, minimum 30-day commit. Examples (per unit/day):
- GPT-5: $75 input (25K TPM) + $60 output (2.5K TPM), 99.9% uptime SLA, 99% > 50 tps latency SLA
- GPT-5.5: $750/unit/day for 50K TPM combined bundle
- o4-mini: $50 input (30K TPM) + $32.50 output (5K TPM)
- GPT-5.4 introduced **combined input+output bundles** to remove the I/O ratio prediction problem

**Reserved Capacity** = static dedicated model instances, 3-month or 1-year (~15% savings) commits, priced in "compute units" at $260/unit/month (3mo) or $220/unit/month (1yr). Per-instance minimums (3-month total commit):
- GPT-5 (3 instances × 270 units): $210,600
- GPT-4.1 (3 × 400 units): $312,000
- o1 (3 × 800 units): $624,000

99.5% uptime SLA + on-call engineering support. This is real reserved-instance economics — minimum entry roughly $200K for 3 months.

### Azure OpenAI / Microsoft Foundry — PTUs

The cleanest "provisioned throughput" model in the market. **PTUs (Provisioned Throughput Units)** are model-independent capacity units:
- Hourly rate per PTU: **$1 (Global) / $1.10 (Data Zone) / $2 (Regional)** as of 2025-2026 across GPT-4o through GPT-5.5
- Min PTUs vary by model (15 for Global, 25-50 for Regional)
- **Monthly reservation ~64% off hourly; 1-year reservation up to 70% off** ($260/PTU/mo Global, $2,652/PTU/year)
- Reservations are model-agnostic within region/shape — switch models without losing the discount
- Now extends to Azure DeepSeek, Llama, etc. (Foundry Models)

This is the model the rest of the industry is converging toward. Analysts expect both Anthropic and OpenAI to ship something analogous within 6 months.

### Coding agent vendors — the messy middle

- **Cursor**: Teams $40/user/mo includes $20 of agent usage at public API list prices + a **$0.25/M Cursor Token Rate** on top of model API pricing (covers semantic search, indexing, custom Cursor models). Enterprise = pooled usage, custom pricing. Composer 1.5 (Cursor's own model) is $3.50/$17.50 per M; Composer 2 is $0.50/$2.50. BYOK is allowed but Cursor Token Rate still applies.
- **Devin (Cognition)**: Self-serve plans rebuilt April 2026 — Free, Pro ($20), Max ($200), Teams (usage-based, $80/mo minimum), Enterprise. Enterprise billed in **Agent Compute Units (ACUs)** per order form. The previous $500/mo Team entry was scrapped as too high.
- **Claude Code Max**: $100 (5x) / $200 (20x) per month for individuals; Anthropic's own staff note Max gives "several thousand dollars worth of API-rate credits if you actually push it." Enterprises explicitly do not have access to Max — it's a consumer plan and Anthropic is wary of subsidizing enterprise consumption through it.

### Procurement-side: Vendr & Tropic for AI

Both have repositioned around AI as the new top-spend category. Tropic's data shows AI vendors applying **20-37% renewal increases** (vs. 3-9% traditional SaaS uplift), and credit-based pricing making benchmarking nearly impossible. Tropic's stat: Anthropic 2,031% YoY growth, Clay 468%, Cursor 86%.

Vendr's "Ruth" AI procurement agent is trained on 130,000+ completed negotiations, claims average 17.13% savings and 9.5x ROI. Both pitch the same fundamental insight: AI vendors are using usage-based pricing and forced SKU migration to break traditional procurement playbooks. Six-month-ahead negotiations yield **39% more savings** than 30-day-out.

---

## 3. The Gateway / Control Plane Vendor Landscape

The market split into clear archetypes:

| Archetype | Vendors | Core value |
|---|---|---|
| OSS proxy | LiteLLM, Helicone (now maint mode), Bifrost | Self-host, free, broad provider coverage |
| Managed control plane | Portkey, TrueFoundry, Vellum | Governance + obs + cost in one |
| Marketplace router | OpenRouter, Vercel AI Gateway | Unified billing, 400+ models |
| API-management incumbent | Kong AI Gateway, Apigee, Cloudflare AI Gateway | Lives in existing infra footprint |
| Network/security incumbent | F5 AI Gateway, Akamai Firewall for AI | DLP, prompt injection, OWASP LLM Top 10 |
| Observability/eval | Langfuse (acq. ClickHouse), LangSmith, Braintrust, Arize, Patronus | Trace, eval, regression |
| FinOps / chargeback | Vantage, Finout, Apptio AI TCO, CloudZero | Tag, allocate, unit economics |
| MCP/agent gateway | Lunar.dev MCPX, TrueFoundry MCP, Portkey Agent Gateway, Obot | Tool-level access control |

### LiteLLM (BerriAI)
- $1.6M seed (YC W23 + Gravity + Pioneer). Most-deployed OSS proxy: **1B+ requests served, 240M+ Docker pulls, 40K GitHub stars, 1,005+ contributors, 100+ providers**.
- Customers: Netflix, Lemonade, Rocket Money, Samsara, Adobe.
- Enterprise pricing not public; SSO free up to 5 users, then enterprise license; tested at 1K RPS, SOC 2 Type 2 + ISO 27001 on hosted Cloud.
- **Reported supply-chain attack March 2026** on versions 1.82.7-1.82.8 (credential-stealing malware) — a trust hit for the OSS path.
- Known performance ceiling: P99 hits 28s at 500 RPS, crashes at 1K+ RPS per third-party benchmarks (contested).

### Portkey
- **$15M Series A Feb 2026**, led by Elevation Capital with Lightspeed. Headquartered SF; founded by Rohit Agarwal.
- **500B+ tokens/day, 125M+ requests/day, $500K daily AI spend governed, 24,000+ organizations**. Annualized $180M in LLM spend governed, ~180 trillion tokens/year.
- 1,600+ LLM endpoints, MIT-licensed OSS gateway core (50+ contributors). Fortune 500 customers in finance/pharma/tech, plus Postman, Snorkel AI.
- Made the **core enterprise gateway free** at Series A — strategic move to lock in early; monetize on governance/agent surface.
- Compliance: SOC 2, GDPR, ISO 27001. Pricing: $49/mo Production tier, ~$5K+/mo enterprise.
- Performance: claims 99.9999% uptime; 20-40ms overhead with guardrails.
- April 2026 launched **Agent Gateway** (registry, per-agent governance, identity, budgets) — explicitly framed as "Codex works for one dev, breaks at enterprise scale: no visibility, scattered API keys, no isolation, no fallback."
- Rumor floated in search results: "Palo Alto Networks' intent to acquire Portkey" — appears on their own site as marquee. Worth verifying.

### Helicone — **acquired by Mintlify March 2026, maintenance mode**
- ~$1.6M total funding (YC W23). $1.6M ARR pre-acquisition, 3 employees.
- 16,000 organizations using it at time of acquisition. Rust-based, Cloudflare Workers, ~8ms P50 overhead, OSS AI Gateway launched June 2025.
- **New users should evaluate alternatives** — only security/bug patches; no roadmap.

### Cloudflare AI Gateway
- **Core features free** on all plans (analytics, caching, rate limiting). Available globally on Workers edge.
- 100K logs free / 10M logs/gateway on Workers Paid. Logpush $0.05/M requests after 10M/mo.
- **DLP scanning free** — two predefined profiles (financial + national ID); full Cloud One/Zero Trust DLP profiles inherit if subscribed.
- **Guardrails** powered by Llama Guard 3 8B on Workers AI (billed per token of eval).
- **Unified Billing**: load Cloudflare credits, call OpenAI/Anthropic/Google AI Studio without provider API keys. Zero Data Retention (ZDR) flag routes through provider ZDR endpoints.
- The "default zero-config" choice for Cloudflare-shop enterprises.

### Kong AI Gateway
- "AI Gateway Enterprise" tier; many AI plugins gated to enterprise: AI Proxy Advanced, AI Rate Limiting Advanced, AI Semantic Cache, AI Semantic Prompt Guard, AI Sanitizer, AI Prompt Compressor, AI Prompt Decorator, AI RAG Injector, AI AWS Guardrails, AI Azure Content Safety.
- **Cost-based rate limiting** (v3.8+): `cost = (prompt_tokens × input_cost + completion_tokens × output_cost) / 1M` — limit on dollars not just tokens.
- Konnect pricing: Enterprise custom; AI Gateway model proxy enforced at **$100/month per unique LLM proxied** beyond Plus tier inclusions. Per-user $45/mo self-serve up to 50.
- PII sanitization across 20 categories, 9 languages. Won several "API estate already runs on Kong" deals at $200K+/mo regulated-industry tier per Particula Tech's decision framework.

### TrueFoundry
- **$19M Series A Feb 2025**, led by Intel Capital with Peak XV (Sequoia India) + Eniac + Jump Capital. Angels: Gokul Rajaram, Mohit Aron, Cyan Banister.
- 4x YoY customer growth claimed. Gateway: ~3-4ms latency, 350+ RPS on 1 vCPU.
- Full-stack: LLM Gateway + MCP Gateway + Agent Gateway + model serving + fine-tuning on Kubernetes. SOC 2.
- Strong in regulated industries: per-team budgets, audit logging, identity-based MCP access via OAuth2 2LO/3LO + SAML + Okta/Entra/Auth0 integration.

### Vellum
- **$20M Series A July 2025**, led by Leaders Fund + Socii + YC continuity. $24.5M total. GA at the raise.
- Customers: Drata, Swisscom, Redfin, Headspace.
- Positioned as end-to-end AI dev platform (visual builder + SDK + eval + deploy + monitor) — competes with both gateways and observability vendors. Strong in regulated industries.

### Lunar.dev
- $6M total funding (Pre-Seed + Seed Nov 2023, led by Uncork Capital). 17 employees, Tel Aviv.
- Pivoted from generic API consumption mgmt to **MCP Gateway (MCPX)** + agent-native gateway. Recognized by Gartner in Hype Cycle for API & Platform Engineering 2025 as Representative Vendor for AI Gateways.
- Unique pitch: **risk evaluation sandbox** that tests MCP servers in isolation before production (claims to be only provider with this), microgateway architecture per agent, reference-only secrets mgmt.
- MCPX core OSS; enterprise edition adds central RBAC + audit + support. On GCP Marketplace.

### OpenRouter — the consumer-leaning enterprise dark horse
- Founded 2023 by Alex Atallah + Louis Vichy. **$40M combined Seed + Series A June 2025** (a16z + Menlo + Sequoia + angels). **Talks to raise $120M at $1.3B valuation** per Sacra (2026).
- Revenue trajectory: $1M ARR late 2024 → $5M May 2025 → ~$10M Oct 2025 → **~$50M ARR early 2026**.
- GMV: $100M annualized inference spend May 2025 → 8.4 trillion tokens/month.
- Monetization: **~5% markup on inference** (5.5% non-crypto with $0.80 min; 5.0% crypto flat). BYOK includes 1M free requests/month then standard BYOK fee. Future: BYOK moves to fixed monthly sub.
- 400+ models, 60+ providers, 1M+ developers used, 2.5M users, edge-deployed ~25ms overhead.
- Enterprise: zero-logging default, multi-cloud failover across 50+ providers, bring-your-own-capacity (blend customer's contracted capacity with OR burst pool), unified billing across providers.
- The State of AI 2025 report (OpenRouter) shows OSS ~1/3 of token volume by late 2025; Asia is ~31% of spend (up from 13%); North America < 50%.

### Langfuse / LangSmith / Braintrust / Arize / Patronus — eval & observability layer
- **Langfuse**: **acquired by ClickHouse Jan 2026** as part of ClickHouse's $400M Series D at $15B valuation. Was raising $50M Series B at ~$400M val just before — both data points appear; the ClickHouse acq seems to be the more recent and authoritative event. 19 Fortune 50 customers, MIT-licensed.
- **LangSmith**: $25M Series A Feb 2024 (Sequoia). Captured majority of LangChain's hundreds of thousands of monthly active developers via zero-config tracing. Plus tier $39/seat/mo, 5K traces free.
- **Braintrust**: **$80M Series B Feb 2026 at $800M valuation** (Iconiq lead, a16z + Greylock). Customers: Notion, Zapier, Stripe, Vercel, Coursera, Dropbox. Loop AI assistant for custom scorers. $249/mo Pro.
- **Arize**: $131M total funding, $70M Series C Feb 2025. Phoenix is OSS flagship.
- **Patronus AI**: $17M Series A, compliance-first.
- LLM observability market: $510.5M (2024) → projected $8.1B (2034) at 31.8% CAGR. LLMOps market projected $4.8B by 2028 (Bessemer Feb 2026 estimate).

### F5 AI Gateway
- GA Mar 2025 (initial announcement Nov 2024). Containerized, integrates with NGINX + BIG-IP.
- OWASP LLM Top 10 enforcement, semantic caching, content-based routing, OpenTelemetry, prompt injection detection.
- **July 2025: Data Leakage Detection & Prevention** added — proprietary real-time classification engine, redact/block/log policies, integrated into F5 ADSP. Plug-in SDK in Python/Rust/Go.

### Akamai Firewall for AI
- Announced April 29, 2025. Edge-deployed alongside Akamai API Security. **API LLM Discovery** auto-discovers GenAI/LLM endpoints. Multilayered protection: adversarial inputs, model extraction, scraping, prompt injection. Real-time threat detection and OWASP-aligned policies.

### First-party dashboards
- **Anthropic Console**: Workspace spend limits, custom rate limits, audit logs (Enterprise only), Compliance API.
- **OpenAI**: Activity dashboard, scale tier usage view, project-based budgets.
- Both expose per-API-key spend out of the box — but they don't give you cross-provider attribution, which is the entire point of a gateway.

---

## 4. Where Token Budget Intersects with Access Control

The deepest unlock in 2025-2026 is recognizing **token budget IS an access control axis**:

1. **Spend budget**: "this team can spend $X/day on Claude" — Portkey, LiteLLM, Kong (cost-based RL), TrueFoundry all support per-key/per-team/per-org budgets.
2. **Model-level allowlists**: "Finance team can use Opus, Marketing only Haiku" — Curate-Me, Portkey, Kong AI Prompt Guard.
3. **Tool/MCP-level access**: per-virtual-key tool filtering. "Finance Agent gets accounting tools, not email tools." Lunar.dev MCPX, TrueFoundry MCP Gateway, Portkey Agent Gateway, Obot, Bifrost.
4. **PII/DLP on agent traffic**: Cloudflare DLP (free), F5 ADSP DLP (paid), Kong AI Sanitizer, Akamai Firewall for AI.
5. **Identity-based RBAC**: OAuth2 2LO/3LO, SAML, SCIM, Okta/Entra/Auth0 — TrueFoundry, Portkey, LiteLLM Enterprise, Kong Konnect Enterprise.
6. **Tool sandboxing**: Lunar.dev's pre-prod MCP server isolation; TrueFoundry Pre/Post Tool guardrails + Cedar/OPA + SQL Sanitizer; Curate-Me's managed OpenClaw runners + HITL approval queues.

**MCP governance** has emerged as a 2026 P0. Google Cloud now ships IAM deny policies specifically for `mcp.tools.call` with attributes like `tool.isReadOnly`, `request.auth.oauth.client_id`, `resource.service`. GitHub Copilot Enterprise supports MCP registry URL + allow/registry-only modes at org and enterprise level. The pattern repeating across every gateway: agents register through the gateway, the gateway holds the OAuth tokens, every tool call is authorized + logged.

---

## 5. Market Signals & Funding 2025-2026

| Vendor | Round | Date | Lead |
|---|---|---|---|
| OpenRouter | $40M Seed+A; talks for $120M @ $1.3B | Jun 2025; 2026 | a16z + Menlo |
| Portkey | $15M Series A | Feb 2026 | Elevation Capital + Lightspeed |
| TrueFoundry | $19M Series A | Feb 2025 | Intel Capital |
| Vellum | $20M Series A | Jul 2025 | Leaders Fund |
| Langfuse | Acquired by ClickHouse | Jan 2026 | (in $400M Series D @ $15B) |
| Helicone | Acquired by Mintlify | Mar 2026 | — |
| Braintrust | $80M Series B @ $800M | Feb 2026 | Iconiq + a16z + Greylock |
| Arize | $70M Series C (cum. $131M) | Feb 2025 | — |
| Galileo | $32M Series B | 2026 | — |
| Humanloop | $25M Series A | — | — |
| LiteLLM (BerriAI) | $1.6M seed | 2023 | YC + Gravity + Pioneer |
| Helicone | ~$1.6M pre-seed/seed | 2023 | YC |
| Lunar.dev | $6M (Seed) | Nov 2023 | Uncork |
| Vantage | (FinOps incumbent, ~$25M+ raised pre-2024) | — | — |

**Pattern**: data-infrastructure companies absorbing observability tools (ClickHouse → Langfuse) is the consolidation thesis. Datadog, Snowflake, Databricks are the obvious next acquirers. Braintrust's $800M val likely prices acquisition premium. Mintlify → Helicone is the docs/knowledge-infra angle.

**Market size**: Enterprise-grade AI Gateway industry sized at $41.47M (2025) → $180M by 2032 at 20.7% CAGR (Market IntelliX). LLM observability $510.5M → $8.1B by 2034 (31.8% CAGR). LLMOps total $4.8B by 2028 (Bessemer).

**Tier scoping rule of thumb (Particula Tech, May 2026):**
- < $10K/mo, single provider → DIY router
- $10K-$50K/mo → LiteLLM OSS
- $50K-$200K/mo → Portkey or TrueFoundry managed
- $200K+/mo, on-prem/multicloud → Kong AI Gateway or Apigee

---

## 6. Standards & Open Protocols

### OpenLLMetry (Traceloop) & OpenTelemetry GenAI semantic conventions
- Traceloop led OTel's LLM semantic convention WG. The conventions started as `gen_ai.prompt.N.*` / `gen_ai.completion.N.*` span attributes.
- **Deprecation in v1.38.0**: those are deprecated; replaced by `gen_ai.input.messages`, `gen_ai.output.messages`, `gen_ai.system_instructions` (event-based), plus token usage metrics (`gen_ai.usage.prompt_tokens`, `completion_tokens`, `total_tokens`, `reasoning_tokens`).
- Provider-specific semconv now exists for Anthropic, OpenAI, AWS Bedrock, Azure AI Inference. MCP also has its own semconv.
- `OTEL_SEMCONV_STABILITY_OPT_IN=gen_ai_latest_experimental` for new attribute shape.

Every gateway now exports OTel-native traces — this is the standard. F5, Kong, Portkey, LiteLLM, Helicone, Lunar all support OTel export. Datadog LLM Observability, New Relic AI Monitoring, Splunk all consume it.

### FinOps Foundation FOCUS spec
Vantage and Finout both lean on FOCUS as the path for normalized billing data across providers — Vantage has a "custom provider + FOCUS spec" upload path for gateways without native integration.

### MCP (Model Context Protocol)
Now de-facto standard for agent tool integration. Anthropic-led. Google Cloud, GitHub, AWS all shipped MCP support 2025-2026. Gateway governance pattern is universal: centralized registry, per-virtual-key tool filtering, OAuth/PKCE managed by gateway, JSON-RPC to REST/Lambda translation.

---

## 7. Key Tensions & Opinions

1. **The unbundling is the story.** Anthropic March 2026 separating $20 access fee from metered tokens is the canonical move. NPI: "lower seat fees, separate usage billing, mandatory consumption commitments will raise overall costs." This forces enterprises to actually attribute spend or they lose the chargeback fight. Procurement teams that did "seat math" in 2024-2025 ROI spreadsheets need to redo them.

2. **The gateway market is consolidating fast but not into a single winner.** Different segments are picking different leaders:
   - LiteLLM owns OSS developer adoption
   - Portkey owns compliance-driven managed
   - OpenRouter owns model breadth + indie/multi-cloud
   - Kong owns "we already speak API gateway"
   - Cloudflare owns "we're already in the edge path"
   - Helicone is out (Mintlify acq, maint mode)

3. **Eval and obs are converging with gateways.** Portkey already ships traces + dashboards; LiteLLM ships per-key Langfuse routing. LangSmith, Braintrust, Langfuse are eval-first but moving down into gateway/proxy (Braintrust ships an OpenAI-compatible AI proxy). Convergence force: both sides need the request payload in path.

4. **MCP governance is the new front.** Every gateway player in 2026 has announced an MCP/agent gateway: Portkey Agent Gateway (Apr 2026), TrueFoundry MCP Gateway, Lunar MCPX, Bifrost MCP mode. The bet: tool-level access control becomes as important as model-level access. Google Cloud and GitHub putting this in IAM and Copilot enterprise policy proves it's table stakes.

5. **FinOps for AI is a year behind cloud FinOps but closing fast.** Vantage's framing: same tools (budgets, tagging, anomaly detection, unit economics), different data sources. Apptio's IBM AI TCO & Usage product is the enterprise-FP&A-led answer. Finout positions virtual tagging as the wedge. Bedrock's lossy attribution (everything appears as marketplace purchases) creates the structural opportunity for gateways/FinOps tools as enrichment layers.

6. **Procurement is being rewired.** Tropic and Vendr both built AI procurement agents. Forced SKU migration (Anthropic's seat consolidation) and credit-based pricing make benchmarking nearly impossible; the data-broker (real spend benchmarks) is the new procurement layer.

7. **Standards are stable enough to bet on.** OTel GenAI semconv is the trace standard; FOCUS is the billing standard; MCP is the tool standard. Gateways that don't speak all three by mid-2026 are dead. The "deploy a gateway early; even a simple LiteLLM proxy" advice is right because the abstraction layer is the path to swapping providers without rewrites.

---

## 8. Loose Ends to Verify

- The "Palo Alto Networks intent to acquire Portkey" line appears on Portkey's own site marquee but I haven't found a primary press release. Worth verifying — would be a major signal.
- LiteLLM March 2026 supply chain attack appears in one third-party source (NeuralRouting.io) but I haven't found an Anthropic-Berriai disclosure URL.
- Anthropic 99.99% SLA announcement March 2026 — single source so far.
- Langfuse: $50M Series B (CallSphere article) vs. ClickHouse acquisition (multiple sources) — the acquisition appears to supersede; one of those sources may have stale claims.
- F5 AI Gateway pricing — not public; field reports needed.

---

## 9. Sources of Note

- Anthropic enterprise pricing transition: TheRegister 2026-04-16, Groundy 2026-04-28, NPI Financial 2025-12-12, VendorBenchmark 2026-03-03, AgenticBrew 2026-04-18.
- Portkey Series A: GlobeNewswire / ET 2026-02-19.
- OpenAI Scale Tier + Reserved Capacity: openai.com/api-scale-tier, openai.com/reserved-capacity.
- Azure PTU pricing: Microsoft Learn (azure.microsoft.com/pricing/details/cognitive-services/openai-service), techcommunity blog Mar 2025.
- Gateway comparisons: AgentMarketCap 2026-04-06, NeuralRouting.io 2026-04-10, Particula Tech 2026-05-01, Zylos 2026-03-29.
- Eval landscape: AgentMarketCap "$500M Eval War" 2026-04-06, PkgPulse 2026-04-24, AwesomeAgents 2026-03-04 & 2026-04-19.
- FinOps for AI: Vantage blog (multiple 2025-2026), Finout 2026-05-06, Apptio AI TCO page.
- MCP governance: TrueFoundry 2026-05-06, Obot 2026-03-17, Google Cloud MCP IAM docs.
- OpenLLMetry: Traceloop docs, OpenTelemetry semconv spec, GitHub issue #3515.
- OpenRouter: Sacra report 2025-07-04, SiliconAngle 2025-06-25, OpenRouter State of AI report.
- Procurement: Tropic toolkit-ent, Vendr Ruth product page, Tropic 2026 procurement trends.
