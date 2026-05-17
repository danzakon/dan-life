# Market Sizing & GTM: Centralized Access Control for AI Agents — Wedge into AI-Native Foundry

Date: 2026-05-17
Status: Raw findings dump from Exa research pass
Purpose: Inputs for a "modern Palantir Foundry" thesis where the wedge is enterprise agent access governance

---

## 1. Market Sizing

### Core IAM (workforce, IGA, PAM, CIEM)

| Segment | 2024-2025 size | Forecast | CAGR | Source |
|---|---|---|---|---|
| Global IAM (all) | ~$22.9B (2024) → $24B+ (2025) | $34.3B by 2029 | 8.4% | MarketsandMarkets (conservative) |
| Global IAM (alt) | — | $61.7B by 2032 / ~$48.8B by 2029 | 15.3% | Fortune Business Insights |
| Global IAM (mid) | — | — | 13% | Identity Management Institute |
| IGA software | $4.5B (2024) | $5.8B (2027) | ~8.8% | ISG/IMI |
| PAM | $4.8B (2024) | $5.2B (2025), $5.6B (proj) | quoted 30% (overstated, real ~10-15%) | ISG |
| CIEM | $1.2B (2023) | $7.5B by 2028 | **44.2%** | MarketsandMarkets — fastest-growing IAM sub-segment |

Key vendors in workforce IAM that matter for competitive framing: Microsoft (Entra), Okta, Ping, IBM, SailPoint, Saviynt, CyberArk, Oracle, Delinea, BeyondTrust. Newer/relevant: Veza, Lumos, Oleria, Cerby, Rippling (workforce IAM at the edges).

CIEM is the analog most relevant to "agent access governance" — same fundamental problem (entitlements sprawl across cloud + SaaS), same buyer (CISO/Cloud Security), and growing 44% CAGR. CIEM landscape: Ermetic (acquired by Tenable), Sonrai, Authomize (acquired by Delinea), Britive, StrongDM.

### Agent identity / NHI sub-segment

There is no consensus TAM yet — this is a category being defined in real time in 2026. Useful proxies:

- **NHI density**: Service accounts/bots outnumber humans 40:1 to 100:1 (average enterprise ~144:1 per NHI Mgmt Group / 250,000+ NHIs in average cloud enterprise per "2026 NHI Reality Report"). 71% haven't been rotated in time; 97% are over-privileged.
- **Gartner positioning**: "Identity and Access Management Adapts to AI Agents" named a top-6 cybersecurity trend for 2026. Gartner places "Agentic Identities" in the 1-3 year adoption horizon at "very high mass." Gartner published *Reference Architecture Brief: IAM for AI Agents and Other Workloads* in May 2026, introducing CeDeSec, WIM (Workload Identity Management), and AuthZ Management Platform constructs.
- **Gartner prediction**: 40% of agentic AI projects will fail by 2027 due to insufficient risk controls. By 2028, 15% of daily workplace decisions made by AI agents. Orgs without NHI governance will have 3x the identity-related breach rate by 2027.
- **Funding action** (signal of market formation):
  - **Astrix** — $85M total, $25.1M ARR (Sept 2025), 123 employees, Cisco reportedly evaluating acquisition at $250-350M (April 2026).
  - **Oasis Security** — $200M total (Series B led by Craft Ventures Apr 2026, plus Sequoia Series A), 115 employees, +80% YoY headcount.
  - **Aembit** — $43M, $1.6M ARR (early), workload IAM focus, backed by Okta Ventures + CrowdStrike Falcon Fund.
  - **Token Security** (Tel Aviv) — NHI for agents.
  - **SGNL** — acquired by CrowdStrike Jan 2026 for **$627.9M** (dynamic real-time access orchestration).
  - **Otterize** — acquired by Cyera (June 2025) for NHI in cloud.
  - **GitGuardian** — $50M from Insight Partners (Feb 2026) for NHI/secrets.

Implied TAM signal: if CIEM is $7.5B by 2028 and NHI/agent identity expands the addressable population 40-100x, even a small per-identity capture rate yields a $10-20B TAM by 2030. The most credible "agent identity / NHI" market sizing implied by funding rounds and Gartner positioning is **$3-5B by 2027 → $15-25B by 2030**.

### Data integration / Foundry-adjacent TAM

- **IDC Data Integration & Intelligence Software**: 2024 MAP report is at the segment-leader level. IDC's 2025-2029 forecast explicitly cites agentic AI as a growth driver. Worldwide data integration software is broadly ~$15B today on a path to ~$25-30B by 2029.
- **IDC Market Glance: Data Platforms (4Q24)** segments the market into data repositories, virtualization/federation, control plane, and streaming. Palantir Foundry sits in the **data control plane** layer.
- **Forrester TEI of Foundry (Palantir-commissioned)**: composite enterprise of $50B revenue/100k employees with 5,000 Foundry users realized $161M+ over 3 years in supply chain cost savings; 178-186% ROI typical pattern.
- **IDC Industrial DataOps Platforms 2026 MarketScape** (Mar 2026) lists Cognite, AVEVA, AspenTech, PTC, Rockwell, SymphonyAI, HighByte — these are Foundry's vertical/industrial competitors.

Combined "Foundry adjacent" TAM (data integration + data ops + analytics control plane): ~$40-50B by 2028.

### Forward-deployed AI services market

- Sierra: **$100M ARR Oct 2025**, up 400% YoY, $10B valuation, 100x revenue multiple. Greenoaks led $350M round Sept 2025.
- Decagon: **$35M ARR Oct 2025** (up from $10M end 2024, 3x+ YoY), 100+ new enterprise logos in 2025 (Avis, Mercado Libre, Deutsche Telekom, Block).
- Glean: **$200M ARR Nov 2025**, doubled in 9 months from $100M, $7.2B valuation (Series F Kleiner Perkins), $1M+ customer segment nearly tripled.
- Cresta: $15M revenue (smaller than peers), 486 employees, $276M total funding, contact-center focused — feels stalled vs Sierra/Decagon. First contact-center AI to hit ISO/IEC 42001 (Jan 2025).
- Cognition (Devin): coding agents, raised at multi-B valuation.
- Crucible.ai, /dev/agents: stealth/early; not yet revenue-disclosed publicly.

Aggregate "forward-deployed AI app layer" revenue across top 10 names is approaching ~$1B ARR in 2026 with collective valuations ~$50B+. This is the cohort that defines the FDE playbook.

### LLM API spend

| Period | Total enterprise LLM API spend | Source |
|---|---|---|
| 2024 (full year) | $3.5B (of $13.8B total gen AI) | Menlo Ventures Nov 2024 |
| 2025 (mid-year run-rate) | $8.4B | Menlo Ventures Jul 2025 |
| 2025 (full year, implied) | ~$15-18B | Composite |
| 2026 (projected) | $30-40B+ | extrapolation from Anthropic forecast |

Vendor revenue (annualized run-rate, early 2026):
- **OpenAI**: $25B ARR (Feb 2026), 9M paying biz users, 910M WAU. Enterprise = 40%+ of revenue and rising. Projects $85B revenue by 2030.
- **Anthropic**: $19B ARR (early 2026), 85-86% enterprise B2B. Internal 2026 forecast $18B (revised up 18%). $26-55B run-rate by late 2026/2027. 9+ customers at >$100M ACV (vs OpenAI's 7). Claude Code at $2.5B+ run-rate.
- **Enterprise market share**: Anthropic 32%, OpenAI 25%, Google 20%, Meta 9%, DeepSeek 1% (Menlo mid-2025). Anthropic's share of OpenAI+Anthropic biz subscription spend went from ~10% (start 2025) to >65% (Feb 2026) per Ramp data.
- **Inference vs training shift**: 49% of enterprise compute is inference-driven (up from 29% YoY); 74% for startups.

---

## 2. Buyer / Persona

### Who actually buys

The buying committee for "agent access governance" sits at the intersection of three orgs:

1. **CISO** — owns identity, owns the breach narrative, controls budget for IAM/security tools. This is the dominant economic buyer for NHI/agent identity today. Most NHI startups (Astrix, Oasis, Aembit) sell here.
2. **CIO / Head of Platform Engineering** — owns the platform, owns developer workflow, integrates the tool. Often the technical evaluator.
3. **Chief AI Officer (CAIO)** — the wild card. Per IBM IBV 2026 study, **76% of orgs now have a CAIO** (up from 26% in 2025, 11% in 2023). 57% report to CEO/Board with budget authority; the other 43% report to CIO/CTO and "coordinate" rather than control. Companies with empowered CAIOs see 10% higher AI ROI.

### CAIO budget authority

| Company size | Annual AI budget | CAIO control |
|---|---|---|
| <1,000 employees | $5M-$20M | 61% have control |
| 1,000-10,000 | $20M-$100M | 61% have control |
| 10,000+ | $100M-$500M+ | 61% have control |
| Tech giants (MSFT/GOOG) | $1B-$10B+ | Full control |

AI spend is moving from 1-2% of IT budget (pre-2024) to 4-5% in 2025. Gartner expects 9.3% growth in global IT spend to $5.74T. AI is the line item growing fastest.

**Implication**: A wedge product priced at $250K-$1M ACV can be approved by an empowered CAIO directly. A $5M+ platform contract requires CISO + CIO + CAIO alignment.

### Sales cycle benchmarks

| ACV | Median cycle | P75 (slow) |
|---|---|---|
| <$5K | 14 days | 21 days |
| $5K-$25K | 30 days | 45 days |
| $25K-$100K | 60-72 days | 90-100 days |
| $100K-$250K | 90-128 days | 120-175 days |
| $250K-$500K | 120 days | 180 days |
| $500K+ | 180 days | 270+ days |

The **$100K threshold** triggers formal procurement at 78% of enterprises and adds 30-45 days alone. Enterprise IAM tools historically have **9-18 month deployment** windows for large enterprises (10M+ identities, multi-region), 6-9 months for SMB/mid-market.

### Procurement gauntlet
- **SOC 2 Type II** — table stakes; absence kills 60%+ of enterprise deals
- **ISO 27001** — required for European deals
- **HIPAA / BAA** — required for healthcare
- **FedRAMP Moderate** — gate for federal; Palantir, Salesforce, ServiceNow all hold it
- **Data residency** (EU, in-country) — increasingly mandatory; on-prem deployment option becomes a differentiator at >$200K/mo workloads
- **GDPR DPA** — table stakes for any EU sale

Portkey's positioning ("SOC 2 + GDPR + ISO 27001 is no longer premium — it's the minimum bar") is a useful 2026 benchmark.

---

## 3. GTM Models That Work

### PLG / Developer-led (Auth0 / WorkOS)

Worked because:
- "Build before you buy" — developers integrate in <30 min via SDK
- Transparent pricing, usage-based
- Free tier with usage limits
- Trust built through highly technical content + open source
- Auth0 went from PLG → enterprise by adding Organizations, SSO/SCIM, professional services, and SI partnerships (Twilio, AWS, Sendgrid).

**Does it work for governance products?** Historically no — governance is sold top-down because the buyer is the CISO, not the developer. But the modern path: developer adopts an open-source SDK/gateway (Portkey-style), generates production metadata, and the security team is then forced to formalize. This is the Snyk/Datadog/Sentry pattern applied to identity.

### Top-down enterprise sales + FDE (Palantir)

Palantir's specific economics (worth memorizing for any FDE pitch):
- 80%+ gross margins maintained despite heavy field deployment
- S&M expense dropped from **62.6% of revenue in 2020 → 24.3% in 2025** (compounding operating leverage)
- Until 2016, Palantir had more FDEs than core engineers
- Contracts start at ~$1M (AIP Bootcamp + limited licenses), expand to $10-100M+ over 3-5 years
- Engineers report into product/engineering, not a services P&L — this is the key cultural lever
- "Deltas" (deployment) and "Echoes" (expansion) are the internal designations

FDE economics for new entrants:
- Per-engineer fully loaded cost: ~$300-400K/year (Niles Lawrence, Palantir/Sierra)
- Customer paying $200K+/engineer/year minimum makes the math work
- Margin trap: if you have >50% FDEs vs product engineers after Year 3, you're a consultancy

### SI channel (Deloitte / Accenture)

The 2026 moves are decisive:
- **Accenture-Anthropic Business Group** (Dec 2025): 30,000 Accenture professionals trained on Claude, "reinvention deployed engineers" embedded with clients. Claude Code COE inside Accenture.
- **Deloitte-Google Cloud Agentic Transformation Practice** (April 2026): 1,000+ pre-built agents, Deloitte Ascend platform, Google FDEs embedded alongside Deloitte teams.
- **Deloitte-ElevenLabs** (March 2026): Big Four first partnership with voice agents.
- **Google Cloud $750M partner fund** at Cloud Next '26 to Accenture, BCG, Bain, Deloitte, McKinsey, plus AI-native shops (Distyl.ai, Tribe.ai, Tryolabs, Artefact).

**Implication**: SI partnerships are now table stakes for any vertical AI play. A "modern Foundry" wedge would need at least one named SI partner pre-Series B to be credible in regulated verticals.

### Forward-deployed engineer model — margins & scalability

Critical distinction from a16z's "Palantirization of everything" (Jan 2026) and N47/Marty Cagan analysis:
- FDEs are **product discovery**, not services delivery — they report to product/eng
- Platform spine (Ontology, Workshop, Functions in Palantir's case) is mandatory; without it FDEs produce bespoke deployments that don't compound
- FDE hiring is up **800-1000% in 2025** across industry (per a16z + Pragmatic Engineer)
- Pattern: aggressive FDE in years 1-3 → transition to product-led at years 4-5 as platform matures (Palantir Foundry launch in 2016 was this inflection)

---

## 4. Wedge Strategies

### A. Land with an AI gateway, expand to access governance

Current AI gateway landscape (2026):
- **LiteLLM** — OSS leader; ~1B requests/day; covers 100+ providers
- **Portkey** — managed, 1,600+ LLMs, 50B tokens/day, full SOC 2/GDPR/ISO 27001 stack; $49/mo entry → custom enterprise; raised Series A
- **Helicone** — Rust+Cloudflare Workers, ~8ms P50, OSS
- **Cloudflare AI Gateway** — bundled with edge; 350+ models
- **Kong AI Gateway** — incumbent API mgmt extending to AI; enterprise/on-prem; +1T API+AI requests/day
- **AWS Bedrock AgentCore Gateway** — GA Oct 13, 2025, 9 regions
- **Apigee** with AI add-ons — for GCP shops

Tier thresholds for AI gateway adoption: $30K/mo LLM spend = mandatory; $50K = governance enters the room; $200K+ = on-prem/Kong/Apigee territory.

**Wedge math**: 10K+ enterprises hitting the $30K/mo threshold by 2026 → ~$30B addressable annual gateway/governance spend if 1% take rate at $1M ACV.

**Risk**: Commoditization is fast. MCP standardization (97M monthly SDK downloads, OAuth 2.1 + PKCE + RFC 8707 mandatory as of March 2026) reduces the "integration" moat. AWS AgentCore Gateway and Microsoft Foundry MCP Server both align to spec.

### B. Land with MCP gateway, expand to data platform

MCP went from Anthropic announcement (Nov 2024) to multi-stakeholder Linux Foundation governance (AAIF, Dec 2025) in **18 months** — 2-3x faster than OAuth 2.0 (2012→2015) or SAML (2005→2010). 10,000+ public MCP servers by Q1 2026. AWS Bedrock AgentCore Gateway, Cloudflare MCP Server Portals, Kong, Composio, Bifrost, Zuplo all shipped between Sept 2025 and Q1 2026.

The MCP gateway is the **session layer** for agent-tool interactions. Owning it means owning:
- Per-tool authorization
- Centralized audit log (still a gap per official MCP 2026 roadmap)
- Rate-limiting
- Egress policy
- Cross-agent delegation policy

This is structurally the same as owning the data-plane for agent activity — the natural expansion path is into an ontology/metadata layer (Foundry-equivalent) since you're already in every agent-tool packet.

### C. Land with free agent observability, expand to governance

Helicone playbook (OSS observability → managed governance). Similar to Datadog's wedge from monitoring → APM → security. Risk: observability is the most crowded layer (LangSmith, Langfuse, Helicone, Arize, Braintrust, Weights & Biases all compete).

### D. Land via vertical SI partnership

The vertical FDE-via-SI play: pick one vertical (financial services or life sciences), land one anchor SI (Accenture or Deloitte), become the "Palantir for the AI-native era" reference architecture in that vertical. This is exactly what Sierra did in CX, then expanded.

### Historical wedges in adjacent markets

| Wedge | Company | Expansion |
|---|---|---|
| Free vuln scanner | Snyk | Application security platform |
| Free SIM card check | Twilio | Communications platform |
| OAuth-as-a-service | Auth0 | Full IAM platform |
| Free monitoring | Datadog | APM, security, logs, RUM |
| API contract testing | Postman | Full API lifecycle |
| Free CI/CD | CircleCI / GitHub Actions | DevOps platform |
| MCP server | (TBD) | Agent governance + data platform |

---

## 5. Recent Precedents — Services-Heavy → Product Companies

| Co | Started as | Now | Critical decision |
|---|---|---|---|
| **Palantir** | Government FDE-heavy, near-services from 2003 | $80B+ market cap, 80% GM, 24.3% S&M | Foundry 2016 productized the platform; FDEs migrated to product |
| **Sierra** | High-touch FDE for chat/voice agents | $100M ARR Oct 2025, 400% YoY, $10B val | Single platform for CX agents; clients build agents on Sierra Studio |
| **Decagon** | Anti-FDE; productized agent builder | $35M ARR Oct 2025, 100+ new logos | Explicitly *rejected* Palantir-style FDE — see Decagon blog: "AI agents need constant iteration; FDE makes iteration expensive" |
| **Cognition (Devin)** | Productized SWE agent | Multi-B valuation, traction TBD | Pure product; minimal FDE |
| **Cresta** | Contact center AI, smaller FDE motion | $15M revenue, slowing | Slower productization vs Sierra |
| **Glean** | Productized enterprise search → agents | $200M ARR, $7.2B val | Connector ecosystem (100+) is the moat; no FDE |
| **Crucible.ai / /dev/agents** | Stealth/early agent infra | TBD | — |

**Key tension**: Sierra and Decagon are running diametrically opposite plays. Sierra is doubling down on FDE-led ("Agent Development" as a discipline per Niles Lawrence). Decagon is pure product. Both are working — Sierra 3x Decagon's ARR, but Decagon's margin profile is cleaner. The "modern Foundry" pitch should explicitly pick one side.

---

## 6. Risks for a New Entrant

### Incumbent encirclement

**Microsoft Entra Agent ID** (GA April/May 2026):
- First-class agent identities as Microsoft Entra service principals
- Agent identity blueprints (templates), federated identity credentials
- Conditional Access policies specifically for agents (autonomous + OBO templates)
- Sponsor lifecycle workflows (prevent orphaned agents)
- Convergence with Microsoft Agent 365 registry
- Sidecar pattern + federation for non-Microsoft agents (AWS, GCP, n8n)
- Bundled with Entra ID Governance

**Okta for AI Agents** (GA April 30, 2026):
- Universal Directory for agents (human + non-human in one fabric)
- Prebuilt integrations with Salesforce Agentforce, Bedrock AgentCore, ServiceNow AI Platform
- Shadow AI agent discovery via managed Chrome OAuth grant monitoring
- "Universal Logout" — instant token revocation across all systems (kill switch)
- Cross App Access protocol
- Auth0 SDK side for developer-side build motion

**AWS Bedrock AgentCore Gateway + Verified Permissions**:
- Cedar policy language (open-source, AWS-led)
- Natural language policy authoring
- Fine-grained authorization at the tool boundary
- Tight Bedrock + IAM + CloudWatch integration

**Anthropic / OpenAI first-party governance**: Both increasingly ship admin consoles, audit logs, enterprise SSO, BYOK, residency controls. Anthropic has SOC 2, ISO 42001, FedRAMP Moderate ambitions. The "we'll handle governance for you" pitch from the model vendor is real.

**Cloud bundling**: AWS Verified Permissions + Bedrock + AgentCore is essentially free if you're already on AWS. Same for Microsoft (Entra + Foundry + Copilot Studio) and Google (Gemini Enterprise + Workspace + Agentspace).

### Speed of MCP standardization

MCP-the-protocol is open and standardizing fast. The gateway layer (transport, auth, observability) is commoditizing. Differentiation has to move up the stack: policy semantics, ontology, behavioral analytics, cross-customer pattern matching, regulated-vertical certifications.

### Other risks

- **Buying-committee fragmentation**: CISO/CIO/CAIO triad means longer cycles, more failure modes
- **CAIO churn**: 76% adoption today but Harvard Business Review called many CAIO roles "tenuous"; turnover at this role could reset deals
- **Model vendor consolidation**: If Anthropic + OpenAI directly absorb 70%+ of API spend, they own the choke point and can vertically integrate governance

---

## 7. Defensibility Plays

### Ontology / metadata moat
Foundry's Ontology is the lock-in. For an agent-native equivalent: capture *how* agents map to business objects, *which* tools they're authorized for, *under what conditions*. The metadata graph itself becomes uncopyable. This is the strongest moat available.

### FDE relationship moat
Per a16z + Palantir analysis: FDEs are not a cost center but a product-discovery mechanism. The defensibility comes from operational dependency, not contract terms. Once an FDE has been embedded for 12+ months, switching cost is measured in years.

### Compliance certification moat
SOC 2 + ISO 27001 + ISO 42001 (AI mgmt) + HIPAA + FedRAMP Moderate + EU residency + StateRAMP combo takes 18-24 months to assemble and is a real barrier. Cresta got ISO 42001 first in contact center AI (Jan 2025) — analogous play.

### Data network effect
Anonymized policy patterns across customers: "98% of agents accessing Salesforce write APIs in production also have these 3 tools enabled." Aggregating policy + behavior across hundreds of enterprises produces a recommendation engine for least-privilege policy and threat detection that no single-customer deployment can match. This is the Astrix/Oasis pitch and the most replicable network effect.

### Vertical depth
Become *the* agent governance layer for financial services, with deep BFSI ontology pre-loaded (KYC patterns, OFAC tools, trade surveillance integrations). Sierra did this in CX; Decagon followed; same playbook works in BFSI or life sciences.

---

## Synthesis / Hypothesis for the "Modern Foundry" Wedge

Strongest wedge ranking based on this research:

1. **MCP gateway → policy engine → ontology** — owns the agent-tool packet flow, leverages the fastest-standardizing protocol in enterprise infra history, sits between every agent and every tool. Requires racing AWS AgentCore Gateway and Microsoft Foundry MCP Server, but those are tied to their clouds.

2. **NHI/agent identity wedge into Foundry-style data platform** — Astrix/Oasis pattern but with explicit "expand to data" roadmap. Risk: Cisco buying Astrix at $250-350M sets a low ceiling.

3. **Vertical FDE-led with SI partner** — pick BFSI or life sciences, anchor with Accenture or Deloitte, sell to CAIO+CISO, build platform spine concurrently. Higher capital intensity but cleanest path to $100M ARR in 3 years given Sierra's pattern.

Combined approach: **Land with MCP gateway (PLG/OSS) → expand via FDE-led ontology builds in 2 named verticals → defend via cross-customer policy network effect + compliance moat.**

Pricing posture:
- OSS gateway: free
- Cloud governance tier: $50K-$250K ACV (mid-market, CAIO-approved)
- Enterprise platform: $500K-$5M ACV (CISO+CIO+CAIO)
- FDE-led platform: $5M-$50M ACV (Palantir-tier, FDE included)

Sales cycle assumption: 6-9 months for mid-market, 12-18 months for enterprise platform, 18-24 months for FDE-led — but cushioned by OSS adoption pulling the platform team into the security conversation.
