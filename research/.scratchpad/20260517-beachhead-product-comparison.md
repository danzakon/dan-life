---
date: 2026-05-17
type: strategy / opinionated comparison
author: beachhead-strategist (team: tenex-openfoundry-research)
status: complete
---

# Tenex Beachhead Product Comparison: Agent RBAC vs Data/Ontology Platform vs Agent Platform

> Pick one. Specify the MVP. Defend it. The team lead's prior — that for Tenex specifically the data/ontology platform attaches better than the broadly-correct industry play (agent RBAC) — is mostly right but needs a sharper edge. The crowded one (agent platform) is not the answer.

---

## 1. Summary — the recommendation up front

**Build the Self-Learning Data/Ontology Platform, but ship it as an "Agent-Ready Data Layer" wedge inside existing Tenex engagements, with an embedded Agent RBAC capability as a bundled (not separately-priced) governance feature.**

Concretely:

- **Primary product:** an FDE-installed, customer-private semantic ontology that auto-builds from a customer's data sources (warehouses, SaaS, ops systems) and is consumed by their agents as a governed, write-back-capable knowledge graph. Call it **Tenex Ontology** (working name).
- **Bundled governance plane:** a thin MCP-gateway-shaped access/audit layer on top of the ontology — *not* a standalone Agent RBAC product. It exists so the data layer is the only path agents take to enterprise data, which is what makes Tenex Ontology load-bearing and sticky.
- **Not** a runtime/framework. We do not compete with LangChain, CrewAI, Sierra, Decagon, Cognition, or the lab-deployed teams. Customer agents stay where they are; we are the thing those agents call.

This is a **synthesis** of the team lead's bias (ontology attaches to current Tenex work) with the prior team's insight (RBAC/MCP-gateway is the wedge mechanically *intermediating* every agent action). Pure ontology without an enforcement choke point becomes a knowledge graph that competitors can route around. Pure RBAC without ontology becomes a commoditized gateway that AWS/Microsoft/Google bundle for free in 18–24 months. The combination — *ontology that is also the policy decision point because all agent traffic flows through it* — is what becomes OpenFoundry.

Rank order:

1. **Self-Learning Data/Ontology Platform** — win. Highest attach rate to existing Tenex work, hardest to commoditize, only credible path to OpenFoundry.
2. **Agent RBAC / Access Control Plane** — second. Industry-correct but the window is closing (Entra Agent ID, Okta AI Agents, AWS AgentCore + Verified Permissions are all GA in 2026; CyberArk → PANW $25B; SGNL → CrowdStrike $628M; Cisco → Astrix rumored). Tenex is not the right shape of company to win a pure security category.
3. **Agent Platform** — pass. Most crowded space in software. Sierra at $10B/$100M ARR, Decagon at $650M+/$50M ARR, Cognition Devin self-serve $20–200/mo, plus every framework on earth. No defensible wedge for Tenex here.

---

## 2. Evaluation matrix

Scoring 1–5 where 5 = strongly favorable to Tenex shipping this beachhead. Weights reflect Tenex constraints: services-heavy DNA, F500 distribution, ≤25% engineering off billable, must attach to existing engagements.

| Dimension | Weight | Agent RBAC | Data/Ontology | Agent Platform |
|---|---|---|---|---|
| Capital intensity to MVP | 10% | 3 (MCP gateway + OAuth + policy engine — 6–8 eng-months) | 3 (ingestion + auto-ontology + MCP exposure — 8–12 eng-months) | 1 (runtime+SDK+evals+orchestration is a 30+ eng-month build to be credible) |
| Time to first revenue from F500 | 10% | 4 (CISO budget is liquid; "agent security" is a 2026 line item) | 5 (slots into existing Tenex SOWs as a paid add-on this quarter) | 2 (needs reference deployments before any F500 signs) |
| Attach rate to existing Tenex engagements | 15% | 3 (~40% — only ones with material agent rollouts) | 5 (~80%+ — nearly every Tenex engagement touches data integration + agent enablement) |  2 (~20% — only engagements with no chosen runtime, shrinking fast) |
| Competitive density | 10% | 1 (Aembit, Astrix, Oasis, Descope, WorkOS, Arcade, Composio, Pomerium, Cloudflare, Entra Agent ID, Okta AI Agents, AWS AgentCore — 20+ funded) | 3 (Galaxy, Stardog, Timbr, Kamiwaza, VERSATIL, Glean's KG, Palantir, Databricks Genie, Snowflake Cortex — crowded but no winner) | 1 (Sierra, Decagon, Cognition, Adept, Imbue, CrewAI, LangChain, Microsoft Copilot Studio, OpenAI DeployCo, Anthropic Claude for Work — apocalyptic density) |
| Defensibility / moat | 15% | 2 (policy logic is replicable; the moat is integrations and SOC2/FedRAMP — both buyable) | 5 (customer-specific ontology is the deepest switching cost in enterprise software, per Palantir's 80% gross margins and 120%+ NDR) | 2 (model layer keeps eating the framework layer; agents-as-services is the actual winning shape and Tenex can't out-FDE Sierra) |
| Distraction risk | 10% | 3 (clean scope but builds an unfamiliar security muscle) | 4 (built on the same data + AI work Tenex already does for clients) | 1 (huge engineering investment + product surface area; pulls 40%+ of engineering off billable just to be credible) |
| Sales motion compatibility | 10% | 3 (CISO is a different buyer than the CDO/CTO Tenex usually sells to) | 5 (same buyer Tenex already has; same SOW; same FDE motion) | 2 (line-of-business buyer for vertical agents; bottoms-up dev for frameworks — neither is Tenex's motion) |
| Pricing unit economics | 5% | 3 ($/policy decision is metered, low-margin once gateways commoditize) | 4 (per-object-type or per-connector + FDE day rate — fits Tenex's $300/sp model) | 3 ($/seat or $/resolution — outcome pricing is hard and Sierra is already at $1.50/resolution) |
| Expansion path to OpenFoundry | 10% | 3 (governance plane is a layer of OpenFoundry but not the load-bearing one) | 5 (ontology IS OpenFoundry's load-bearing primitive — Palantir's own analysis confirms this) | 2 (agent platform leads to "Tenex agent runtime" not "Tenex foundry" — wrong vector) |
| Commoditization half-life | 5% | 1 (12–24 months — Microsoft and AWS are GA already) | 4 (5–7 years — auto-ontology is hard, customer-specific by definition) | 1 (12–18 months — framework layer commoditizes into model layer) |
| **Weighted total** | 100% | **2.65** | **4.30** | **1.70** |

The data/ontology platform isn't just the best choice — it's the only one that scores above 3.0 on a weighted average. Agent RBAC is a credible #2 but loses on competitive density and commoditization half-life. The agent platform is a trap.

---

## 3. Candidate 1: Agent RBAC / Access Control Plane

### What it is

The wedge from the prior report (`20260517-rbac-ai-agents-modern-foundry-wedge.md`): an MCP-gateway-led access control plane that intermediates every agent-to-tool and agent-to-data interaction across the enterprise. OAuth 2.1 + RFC 8707 audience binding + per-user token scoping + dual-principal (user + agent) policy decisions + audit trail. Sells against CISO/IAM budget.

### Honest case for it

- **Real gap, real pain.** The prior report is correct: 38.7% of public MCP servers ship with no auth; named breaches across GitHub MCP/Invariant, Asana, Supabase/Cursor, Smithery, postmark-mcp, Splunk MCP, ContextCrush; OWASP MCP Top 10; multiple CVEs. Enterprises will buy this in 2026.
- **CISO budget is liquid.** Identity security spend grew faster than any other security category in 2024–2026. Palo Alto paying $25B for CyberArk, CrowdStrike paying $628M for SGNL, Cisco reportedly $250–350M for Astrix — the category is being priced at strategic premiums.
- **Tenex's compliance pedigree could matter.** F500 buyers won't trust a 2-year-old startup with MCP traffic; they might trust a services firm with $15M ARR and demonstrable F500 references.

### Why I'm not picking it

- **The window is already closing.** Entra Agent ID GA (May 2026), Okta AI Agents GA (April 30, 2026), AWS Bedrock AgentCore Gateway + Verified Permissions GA in 9 regions. By the time Tenex ships an MVP (Q1 2027), the hyperscalers will have bundled this for free into Azure / AWS / Workspace tenants. Standalone gateways will be a feature, not a product.
- **Tenex doesn't have the right DNA.** Selling Aembit, Astrix, or a CyberArk-shaped product requires deep IAM/security DNA, FedRAMP High track record, SOC 2 + ISO 27001 + ISO 42001, dedicated security sales reps, channel partners (Optiv, Trace3, GuidePoint). Tenex is a $15M ARR engineering-as-a-service firm. Building a credible security category presence takes 3+ years and ~$30M of investment that Tenex does not currently have positioned.
- **Wrong buyer.** Tenex's existing engagements run through CIOs, CDOs, and CTOs. RBAC sells to CISOs. Cross-selling RBAC into existing engagements means winning a *new* economic buyer per account — possible, but expensive.
- **Competitive density is apocalyptic.** Aembit ($25M+), Astrix ($85M, possibly Cisco-acquired), Oasis ($200M), Descope ($88M), WorkOS ($210M), Arcade, Composio, Pomerium, Solo.io AgentGateway, TrueFoundry, Cloudflare AI Gateway, Gram by Speakeasy, Docker MCP Gateway — and that's just the standalone players. Every existing identity vendor has bolted on "agent identity."
- **Commoditization risk.** Per the IAM landscape research: MCP gateway pricing is already racing to the bottom. Composio at $0.249/1K tool calls; Arcade Hobby tier free for 1,000 executions. By 2027 this layer is sub-$1 per 100K calls and not a viable standalone business.

**Verdict:** correct industry thesis, wrong company. If Tenex were a 5-year-old security firm with FedRAMP High and $50M raised, this is the wedge. As a 1-year-old engineering services firm scaling F500 distribution, it's a distraction.

### What survives

The MCP-gateway pattern, scoped down, becomes a **bundled governance feature** of the recommended product. Not its own SKU. See §5.

---

## 4. Candidate 2: Self-Learning Data/Ontology Platform (recommended)

### What it is

An FDE-installed, customer-private semantic ontology that:

1. Connects to the customer's existing data sources (warehouses — Snowflake, Databricks, BigQuery; operational systems — Salesforce, Workday, NetSuite, ServiceNow; data lakes — S3, GCS; lines-of-business apps).
2. **Auto-builds an ontology** by inferring entity types, relationships, and action verbs from schemas, query logs, and (crucially) the actual agent interactions the customer is starting to run. Datris.ai, Corvic, Meko, Exabase, Kamiwaza, Galaxy, and VERSATIL are all proving the auto-build pattern works for at least the structural ontology; nobody has paired it with the operational + governance layer.
3. **Exposes the ontology as governed MCP tools** — object reads, typed actions with side effects, queries — that the customer's existing agents (Claude, ChatGPT Enterprise, internal LangChain stacks, Sierra-style vertical agents) can call. The governance/audit/RBAC plane is built in here, not sold separately.
4. **Compounds over use.** Each agent interaction is a signal — what entities co-occur, what verbs the org actually performs, what edges between data sources matter. The ontology refines itself. This is the Palantir moat (institutional knowledge graph) but auto-bootstrapped rather than FDE-hand-built.

### Why this attaches to existing Tenex work like nothing else

Nearly every Tenex engagement today involves either (a) data integration / pipeline / warehouse work, (b) custom application or workflow development, or (c) AI/agent enablement. The Tenex Ontology is *the artifact those engagements would already be producing if Tenex had the product to harvest it*. Today, every Tenex client gets a custom ETL + a custom data model + a custom agent integration — and at the end of each engagement, that work walks out the door with the client and is not reusable.

Tenex Ontology turns every existing engagement into:

1. Billable services time as before (no cannibalization).
2. **Plus** a recurring Ontology subscription that captures the data-modeling output of the engagement as ongoing value.
3. **Plus** a compounding asset where the next engagement at that client builds on the prior ontology rather than starting from scratch.

This is the Palantir FDE flywheel — field abstractions migrate back into product — but starting from Tenex's existing book of business rather than greenfield.

### Capital intensity to MVP

8–12 engineer-months. Components:

- Connector framework (start with 6 core connectors: Snowflake, Databricks, Salesforce, S3, Workday, ServiceNow). ~3 eng-months.
- Auto-ontology builder (LLM-assisted schema → object types + link inference, with human-in-the-loop refinement UI). ~3 eng-months.
- Object/action store + write-back transactionality (use Postgres + a typed action layer; no need to invent storage). ~2 eng-months.
- MCP server / governance / audit plane. ~2 eng-months.
- F500-grade SOC 2 prep + observability + multi-tenancy hardening. ~2 eng-months.

≤25% of engineering off billable means roughly 4–6 dedicated engineers; ships MVP in ~3–4 calendar months.

### Time to first revenue from F500

This product can be sold **now**, before MVP, by attaching it to existing Tenex SOWs. Tenex already has F500 clients paying $300/sp for integration and agent work. A 200-storypoint engagement with a paying client can be re-bundled this quarter as "Tenex Ontology pilot + integration services," with the ontology product priced separately (~$150K–500K/yr) and the integration services billed normally. The first booking can happen in 60–90 days; the MVP catches up in 90–120 days.

### Defensibility

The deepest moat available in enterprise software. Palantir Foundry is valued at >$200B almost entirely on the strength of this moat. The ontology becomes the customer's operating model; migrating it is organizational re-architecture, not a tooling swap.

Critically: the auto-build approach + agent-interaction feedback loop *gets stronger over time*. Every prompt, every tool call, every action verb the customer's agents execute is a refinement signal. A competitor entering 18 months from now has zero of this data on the customer's actual operations.

The MCP-governance bundling makes this stickier: once the customer's agents are configured to call Tenex Ontology as their MCP server, ripping it out means rewriting every agent and re-pointing every tool. This is the Foundry mandatory-marking-propagation moat translated to the agent era.

### Distraction risk

Lowest of the three. The product is built from the same primitives Tenex's engineers are already shipping on client engagements: data connectors, schema modeling, MCP servers, agent integration. The Ontology is the *productization of the work Tenex is already doing*. Engineers building it can rotate in and out from client engagements without context loss.

### Sales motion compatibility

Perfect fit. Same buyer (CDO/CTO/CIO, sometimes Chief AI Officer), same engagement shape (FDE-led discovery → pilot → expansion), same pricing structure ($/storypoint plus subscription), same compliance posture. The first ten customers can be Tenex's current top-10 accounts.

### Pricing unit economics

- **Per object type, per month** — primary metric. $X per object type (call it $2,500–5,000/object type/month for the first 20 object types, with volume discounts after). A typical F500 engagement starts with ~30–80 object types in year one.
- **Plus per connector** — $X per connector/month for managed connectors to enterprise systems. $1,000–3,000/connector/month.
- **Plus FDE day rate** — Tenex storypoints layered on top for ontology design, action authoring, agent integration. Same $300/sp.
- **Year-one ACV target:** $250K–1.5M depending on customer size. Compare Palantir entry-level ACV ~$1M+; Glean ~$60K minimum / 100 seats; data ontology platforms today at $20K–60K (Timbr, Galaxy mid-market).

This lands Tenex Ontology between Glean (knowledge graph for search) and Palantir Foundry (full operational stack) — a real gap in the market, anchored by the price points buyers already accept on either side.

### Expansion path to OpenFoundry

The ontology *is* the load-bearing primitive of OpenFoundry. The recipe:

```
Year 1: Tenex Ontology — auto-built data+action graph, MCP-served to agents.
        + bundled governance/RBAC plane.
        + connectors to top-10 enterprise systems.

Year 2: Add the operational app layer. Workshop-equivalent declarative UI
        builder, customer agents compose workflows over the ontology.
        + Add Foundry-style lineage-aware permissions for sensitive data.
        + Add ISO 42001 + FedRAMP Moderate.

Year 3: OpenFoundry — explicitly model-agnostic, warehouse-agnostic,
        cloud-agnostic. The ontology runs on top of customer-chosen
        Snowflake/Databricks/BQ + Anthropic/OpenAI/Gemini + AWS/Azure/GCP.
        Tenex is the layer that turns those choices into one coherent
        operating model, vs. Palantir's vertically-integrated lock-in.
```

This is the only candidate where Year 1 → Year 3 is a single product evolution, not a strategic pivot.

### Commoditization risk

The structural ontology — auto-detecting entity types and relationships — is on a 3–5 year commoditization curve. Datris, Corvic, Meko, Kamiwaza, and others are racing here. By 2028 LLM-driven schema inference will be a feature in every catalog (Atlan, Alation, Collibra).

The action layer (typed verbs + transactional write-back + lineage-aware governance) is on a 5–7 year curve. This is where Palantir's 10-year head start lives.

The customer-specific ontology that accretes from a customer's actual agent traffic is *not commoditizable* — it is by definition specific to that customer's operations.

The competitive question is therefore: can Tenex ship faster than Datris/Kamiwaza on auto-build, faster than Palantir on agent-readiness, and lock in F500 customers before either side catches up? Yes — provided Tenex uses its existing F500 distribution. That distribution is the unfair advantage.

### Concerns / red flags

- **Palantir reaction.** If this works, Palantir notices. Their Ontology MCP + Palantir MCP releases show they understand the threat shape. Mitigation: stay below the radar for 12 months (don't market as "Foundry alternative"; market as "agent-ready data layer"), and target Palantir-skeptical buyers (financial services who got priced out of Foundry, healthcare who wanted Foundry but couldn't justify $5M ACV, manufacturing mid-market).
- **Auto-build quality.** If the auto-built ontology is shallow or wrong, customers will reject it. Mitigation: ship with FDE-in-the-loop refinement from day one; never claim "fully autonomous" until the data backs it up.
- **MCP-as-foundation risk.** The Linux Foundation now owns MCP; the spec is on its 3rd revision in 12 months. If MCP loses to A2A or some other protocol, Tenex's gateway play needs to migrate. Mitigation: the *ontology is the product*; MCP is just the consumption interface. Swap MCP → A2A is a quarter of work.

---

## 5. Candidate 3: Agent Platform

### What it is

A runtime + framework + governance layer for building, deploying, and operating AI agents inside the enterprise. Includes orchestration, tool calling, observability/evals, deployment, governance. Examples: Sierra, Decagon, Cognition Devin (for code agents), CrewAI Enterprise, LangChain LangSmith, OpenAI Agent Builder, Anthropic Claude for Work / Agent SDK, Microsoft Copilot Studio + Agent 365.

### Why the team lead's bias against this is right

- **Apocalyptic competitive density.** Sierra ($10B / $100M ARR, ex-Salesforce co-CEO founder, openly running the FDE motion against Tenex's exact same playbook). Decagon ($650M / $50M ARR). Cognition / Devin (self-serve $20–200/mo, enterprise custom). Plus every framework on earth (LangChain, CrewAI, LlamaIndex), every hyperscaler (AWS Bedrock Agents, Azure AI Foundry, Vertex AI Agent Builder), every model lab (OpenAI DeployCo, Anthropic Claude for Work, Google Agentspace), every vertical agent company spawning weekly.
- **Wrong shape for Tenex.** Sierra is what Tenex would become if Tenex bet on agent platform. But Sierra had Bret Taylor, a $175M Series A in 2024, and explicit framing as a Salesforce-replacement BPO. Tenex would be a follower with no model lab partnership, no vertical specialization, no $/resolution data, no foundation models to fine-tune. The reference customers Tenex would target are already buying Sierra or Decagon.
- **Sales motion mismatch.** Sierra and Decagon sell to line-of-business operations buyers (Head of CX, Head of Sales Ops). Tenex sells to the CDO/CTO. Different deal cycle, different decision criteria, different references required.
- **The runtime layer commoditizes into the model layer.** Anthropic's Computer Use + Claude Code Agent SDK, OpenAI's Agent SDK, Gemini's Agent Builder — frontier labs are pulling the runtime into their stacks. CrewAI and LangChain are increasingly thin shims. Whoever owns the model owns the runtime; Tenex owns neither.
- **No expansion path to OpenFoundry.** An agent platform leads to "Tenex agent platform." That's a fine outcome ($1B exit, maybe) but it is not the foundry. The foundry has a *data substrate* and an *operating model* that agents call into. Building the agent without the substrate is building the consumer without the producer.

### What's salvageable

If Tenex wants to participate in the agent-runtime narrative, the right move is **observability / evals plus governance for customer-chosen runtimes**, not a Tenex runtime. That gets absorbed into the Ontology product naturally (the ontology is the eval target — "did the agent take the right action, with the right object, under the right policy?"). It is a feature, not a product.

**Verdict:** Pass. The agent platform is the most expensive way for Tenex to lose to better-funded, better-positioned competitors with a 24-month head start.

---

## 6. Hybrid strategies considered and rejected

| Hybrid | Why considered | Why rejected |
|---|---|---|
| Agent RBAC → expand into ontology | Prior team's recommendation; uses CISO budget to seed F500 footprint, then upsell CDO with ontology in year 2 | Two different buyers means two different sales motions and one of them (RBAC) is a 12–24 month commoditization race against Microsoft and AWS. Tenex loses the security category before the data play matures. |
| Ontology → expand into vertical agents | Build ontology in year 1, then ship Tenex-branded vertical agents (CX, sales ops, HR) on top in year 2 | Vertical agents put Tenex in direct competition with Sierra/Decagon. The ontology is more valuable as an *enabler of customer-built or third-party agents* than as a substrate for Tenex's own agents. Keep agents the customer's problem; own the substrate they call. |
| Agent RBAC + Agent Platform combined | Sell a "secure agent platform" | Has the disadvantages of both: crowded category, wrong buyer mix, no defensible moat. Worst of both worlds. |
| **Ontology + bundled governance (recommended)** | — | — |

The recommended hybrid (ontology with embedded governance) is the only one where the two components reinforce each other architecturally: governance is not a separate product but the access mode of the data substrate. This is exactly what Foundry's mandatory-marking-propagation is.

---

## 7. The MVP — what to ship in the first 6 months

Working name: **Tenex Ontology** (internal); external positioning **"agent-ready data layer for the F500."**

### Feature set (15 bullets, ranked by must-ship-for-MVP)

1. **Connector framework with 6 launch connectors:** Snowflake, Databricks, Salesforce, ServiceNow, Workday, S3. Read-only ingestion + schema introspection. Pull-based; no agent runs against the source.
2. **LLM-assisted ontology builder.** From schema + sampled rows + query history (warehouse query logs are gold), propose object types, properties, link types, and candidate action verbs. Surface in an FDE-facing review UI; FDE confirms or edits.
3. **Object/property/link storage** in Postgres + JSONB with typed property base types (string, int, geo, marking, fk). Not a graph DB — the action and write-back layer matters more than graph traversal performance at MVP scale.
4. **Typed action verbs** with transactional execution against source systems via existing customer credentials (`create_purchase_order`, `update_case_status`, etc.). One write path per action; idempotency keys; full audit log.
5. **MCP server that exposes the ontology** as tools. Tool catalog auto-derived from object types and action types. Per-tool RBAC, per-tool description, per-tool typed parameter validation.
6. **Per-user OAuth + audience-bound tokens (RFC 8707)** for the MCP layer. Token exchange against customer's existing IdP (Okta, Entra, Ping). No DCR; CIMD only.
7. **Action policy engine.** Dual-principal (user + agent) authorization. Cerbos-style YAML or OPA Rego. Out-of-the-box policies for "writes require human-in-the-loop" and "PII reads require purpose-binding."
8. **Audit log** with `who/what-agent/which-tool/which-object/policy-version/outcome`. Exportable to customer's SIEM (Splunk, Datadog, Sentinel).
9. **Marking-style classifications** on properties (basic: `pii`, `phi`, `financial`, `restricted`). Inherited by derived object types. Enforced at tool-call time.
10. **Agent-interaction feedback loop.** Every tool call generates a signal; weekly batch job proposes ontology refinements (new object types, missing relationships, frequently co-occurring entities). FDE reviews; customer approves.
11. **Embeddings layer** over object properties for semantic search (`find_objects_like`). Pluggable model — OpenAI, Anthropic, Cohere, or BYO.
12. **Object views** — a thin auto-generated UI showing the ontology to non-technical users for verification and trust. Read-only; not a competing app layer at MVP.
13. **FDE deployment kit.** Docker Compose for pilot, Terraform module for prod. Single-tenant deployment per customer; runs in customer VPC or Tenex-managed cloud.
14. **Customer-specific dashboards** for the CIO/CDO: which agents are calling which tools, action volume, denied actions, ontology coverage of source systems.
15. **No agent runtime, no app builder, no workflow engine.** Explicitly cede those layers to the customer's existing tools and to model labs. Tenex Ontology is the substrate; not the consumer.

Stretch features for months 4–6 (ship if MVP lands cleanly):

16. SCIM `/Agents` provisioning per the WorkOS draft.
17. Lineage-aware propagation of markings across derived object types (the load-bearing Foundry primitive).
18. Cross-source joins / derived object types (e.g., a `Customer` object whose properties span Salesforce + Workday + Snowflake).
19. Per-tool sandboxed execution for write actions in a dry-run mode.
20. ISO 42001 audit pack and SOC 2 Type 2 attestation.

### First 5–10 F500 customer profiles to target

These are the *shape of customer* — Tenex's actual current F500 accounts that fit this shape should be targeted by name in the first round.

1. **Top-5 US bank with a fragmented data estate across Snowflake + on-prem Teradata + Salesforce.** Pain: regulatory desire to deploy AI agents on internal data, but no unified data model and no governance plane that satisfies OCC/Fed scrutiny. Buyer: Chief Data Officer + Chief Information Security Officer (joint). Entry ACV: $750K–1.5M.
2. **F100 health insurer wrestling with HIPAA-bound agent deployments.** They cannot use Glean (no purpose-binding) and Palantir Foundry is priced beyond their tolerance. Buyer: CIO + Chief Privacy Officer. Entry ACV: $500K–1M.
3. **F50 manufacturer with $40B revenue, SAP S/4HANA + ServiceNow + 200 line-of-business apps.** Pain: 50+ pilot agents but no consistent view of the supply chain across them. Buyer: CIO + COO. Entry ACV: $1–2M.
4. **F200 retailer with Salesforce + Snowflake + a hand-built ML platform.** Pain: each business unit's agents reinvent customer/order/inventory models inconsistently, leading to wrong recommendations. Buyer: Chief Digital Officer. Entry ACV: $400–800K.
5. **F100 oil & gas operator with operational data in OSIsoft PI + Snowflake + ServiceNow.** Pain: operational AI agents must respect both safety policies and union-contract restrictions. Buyer: VP Operational AI + VP IT. Entry ACV: $1M+.
6. **F200 asset manager with Bloomberg + Snowflake + Salesforce.** Wants Claude/ChatGPT to write portfolio commentary referencing actual holdings, securely. Buyer: CTO + Chief Compliance Officer. Entry ACV: $500K.
7. **F50 telecom with massive billing + CRM + network ops data.** Sierra-style CX agents already deployed but stuck on data integration. Buyer: CIO + VP CX. Entry ACV: $750K.
8. **F100 logistics company.** Operational decisioning needs both real-time and warehouse data. Palantir is selling to them already; Tenex undercut at half the price. Buyer: CTO + COO. Entry ACV: $1M.
9. **F500 staffing/HR services firm.** Workday + ServiceNow + custom CRM. Wants HR agents that respect manager hierarchies and compensation confidentiality. Buyer: Chief People Officer + CIO (joint). Entry ACV: $400K.
10. **F100 utility regulated by FERC/NERC.** Operational agents on grid data must satisfy NERC CIP. Buyer: CIO + Chief Compliance Officer. Entry ACV: $1M+.

Prioritize the first three: bank, insurer, manufacturer. These are the verticals where Palantir has the strongest reference architecture, which means buyers there already understand the value proposition and the budget is pre-existing. Beat Palantir on price + speed-to-value, not features.

### Pricing structure

```
Annual subscription:
  Base platform fee: $120K/year (includes 10 connectors, 30 object types, 1M tool calls)
  Per object type beyond 30: $3,000/month
  Per connector beyond 10: $1,500/month
  Per 1M tool calls beyond 1M: $1,500
  
Services (Tenex storypoints @ $300/sp):
  Implementation: 80–200 sp typical
  Ontology refinement / new connectors: ongoing 20–80 sp/month
  
Typical Year 1 ACV: $300K–1.5M
Typical Year 2 ACV with expansion: $500K–3M (NDR target >130%)
```

The base platform fee is **CAIO-approvable** ($120K is under most enterprise CAIO discretionary budget); expansion is led by FDEs after the first quarter of usage.

### Team to ship it

**Engineering (4–6 FTE for 6 months, ramping to 8–10):**

- Tech lead / staff eng (1) — owns the ontology data model and write-back transactionality.
- Connector engineers (2) — own the connector framework + first 6 connectors.
- MCP / auth / governance engineer (1) — owns the MCP server, OAuth, policy engine.
- LLM / ontology-build engineer (1) — owns the auto-ontology builder + feedback loop.
- Frontend / FDE-UX engineer (1) — owns the FDE review UI and customer dashboards.
- SRE / multi-tenancy (1, ramp month 2) — owns deployment, observability, security posture.

**Product & GTM (3 FTE):**

- Product manager (1) — pulled from existing Tenex product leadership.
- Founding AE (1) — hire externally; target someone from Palantir, Glean, or Snowflake commercial.
- Product marketing / category-defining writer (1) — part-time at first; owns the "agent-ready data layer" positioning and the F500 case studies.

**Design (0.5 FTE):**

- Senior designer shared with current Tenex product team; ontology review UX is the highest-leverage design surface.

**Forward deployed (existing FDE pool, no new hires):**

- 2 senior FDEs initially seconded onto Tenex Ontology pilots. Plays double duty: bills client time + delivers product. This is exactly the Palantir model; the only thing Tenex must enforce is that abstractions migrate back to product (a process discipline, not a hire).

Total dedicated FTE: **9–11**. This is well under 25% of engineering capacity for Tenex at current scale.

### 6-month roadmap

```
Month 1 — Setup + design
  Hire founding AE, formalize PM, freeze MVP scope.
  Architecture review w/ tech lead; choose Postgres + Postgres-vector for embedded; finalize MCP spec compliance baseline (2025-11-25 revision).
  Sign first 2 design partners from current Tenex F500 accounts at zero or nominal cost in exchange for data access + reference rights.

Month 2 — Connectors + ontology builder skeleton
  Ship Snowflake, Salesforce, ServiceNow connectors.
  First version of auto-ontology builder against design partner #1 data.
  MCP server prototype with hardcoded RBAC.

Month 3 — Policy engine + audit + write-back
  Cerbos integration, audit log, write-back actions for design partner #1.
  Beta with design partner #1's existing agents (their Claude + Cursor deployments).
  Lock SOC 2 Type 2 audit kickoff.

Month 4 — Feedback loop + design partner #2
  Auto-refinement of ontology from agent-interaction data.
  Onboard design partner #2; ship Workday + Databricks connectors.
  First paid pilot ($120K–250K) signed with design partner #1 (convert pilot to paid).

Month 5 — Productization + first commercial customer
  S3 connector. Object views UI. Customer-facing dashboards.
  First "non-design-partner" F500 sale; target $400–750K Year 1.
  Founding AE has 8–12 active F500 opportunities in flight.

Month 6 — MVP GA + category launch
  Public GA with 3 customer logos, 1 case study.
  ISO 42001 audit start. SOC 2 Type 2 in final stage.
  Internal Tenex enablement: every active Tenex engagement gets a Tenex Ontology pitch attached.
```

### What success looks like

**At 6 months:**
- 3 paying F500 customers (≥$120K ACV each, mix toward $400K).
- $1.2–2.5M Year 1 ARR booked.
- 12+ pipeline opportunities sourced from existing Tenex engagements.
- 6 connectors GA; 3+ more in beta.
- MVP-grade auto-ontology that generates an 80%-correct first-pass ontology for a customer in <2 weeks.
- Documented 2x reduction in time-to-first-agent-tool-call for a customer vs. their prior bespoke MCP setup.

**At 12 months:**
- 8–12 paying F500 customers.
- $6–12M Year 1 ARR (+committed Year 2 ramp to $15–25M ARR).
- ~50% of new Tenex engagement SOWs include Tenex Ontology as a bundled product line.
- NDR >130% on the cohort that's been on the product >6 months.
- A defensible second product surface mapped (operational app layer, or vertical ontology starter packs).
- A 1-2-sentence answer to "what's the OpenFoundry vision" that customers nod at.

### Kill criteria — when Tenex shuts this down

- **Customer pilot completion rate <50%** at month 6. If auto-ontology is too brittle and FDE intervention is too heavy, the product economics break.
- **NDR <110%** at month 12. Below this, the moat thesis fails — switching costs aren't materializing.
- **Hyperscaler bundling.** If AWS or Microsoft ships a fully-functional auto-ontology with native Bedrock/Foundry integration at <$50K/year by Q4 2026, the moat compresses fast. Pivot to vertical specialization (e.g., "Tenex Ontology for healthcare" with HIPAA-specific primitives).
- **Engineering burn-rate breach.** If Tenex Ontology engineering consumes >30% of total eng capacity at month 6, scale back scope (drop write-back, ship read-only) rather than degrade billable client work.
- **Sales motion mismatch.** If <30% of pipeline comes from existing Tenex engagements at month 6, the attach-rate thesis is wrong and we're competing with Palantir on cold ground — kill and rethink.

---

## 8. Confirming or challenging the team lead's prior

The team lead's framing was:

> The prior report argued agent RBAC / MCP gateway is the right wedge for an industry-wide play. BUT for Tenex specifically, with its services-heavy DNA and the fact that nearly every engagement Tenex does involves data integration + agent-building for the client, the data/ontology platform may attach better to existing work and feel less "this is a separate product." The agent platform is the most crowded space.

**Confirming, with refinements:**

1. **The bias is correct on the data/ontology choice.** Attach-rate to current engagements scores 5/5 vs. 3/5 for RBAC; competitive density is meaningfully lower; commoditization half-life is 3–5x longer.
2. **The bias on the agent platform is correct.** Most crowded space, most expensive to compete in, no Tenex-specific advantage.

**Refining (the part the team lead understated):**

3. **The prior report's RBAC thesis is industry-correct.** RBAC/MCP-gateway *is* the wedge — *for someone*. That someone is Microsoft, AWS, CyberArk, Astrix, and Aembit. The category will be won by a security-DNA company with FedRAMP High and CISO relationships, not by a services-DNA company. Tenex would be the 23rd entrant to a winner-take-2 category.
4. **Pure ontology without governance is also wrong.** This is where the prior report's insight survives. If Tenex ships Tenex Ontology *without* the bundled governance plane, then a customer's agents can talk to the data via any path (their own MCP, their hyperscaler's MCP, Composio, Arcade) and Tenex Ontology becomes one optional data source among many — Glean-shaped. With the governance plane bundled, Tenex Ontology becomes the *only safe* path to enterprise data, which is what makes it the operating-model substrate (the Palantir moat).
5. **Sales positioning matters more than product purity.** Don't sell this as "ontology" to most F500 buyers — they hear "we tried Foundry and couldn't afford it." Sell it as **"agent-ready data layer with built-in governance"** to the CDO/CIO co-buying with the CISO. Then build the ontology underneath.

**Net:** The team lead's instinct is the right call. The refinement is that the wedge must include the choke-point governance feature *bundled into the ontology*, not as a separate product or category positioning. This is the synthesis that creates a defensible OpenFoundry trajectory.

---

## 9. The one-paragraph version

Tenex should build Tenex Ontology — an FDE-installed, auto-built semantic data layer for the F500 that exposes a customer's enterprise data and operational verbs as governed MCP tools to whatever agents the customer has chosen. It attaches to ~80% of Tenex's existing F500 engagements without changing the buyer or the sales motion, captures the data-modeling output that today walks out the door at the end of every engagement, and compounds into the deepest moat in enterprise software (customer-specific ontology) at Glean-tier pricing rather than Palantir-tier. The MCP-gateway/RBAC product the prior report endorsed is correct as a *bundled governance feature* of Tenex Ontology — it's the choke point that makes the ontology load-bearing — but is the wrong shape for Tenex to sell as a standalone CISO-targeted security category. The agent platform is the most crowded space in software and Tenex has no defensible advantage there. Ship Tenex Ontology MVP in 6 months with 9–11 FTE, target $1.2–2.5M Year 1 ARR from 3 F500 paying customers seeded from current Tenex accounts, and grow into the OpenFoundry vision over 18–36 months by adding the operational app layer and Foundry-style lineage-aware permissions on top.

---

## Sources

- `/Users/danzakon/dev/life/research/reports/20260517-rbac-ai-agents-modern-foundry-wedge.md` — prior team's full RBAC + Modern Foundry thesis.
- `/Users/danzakon/dev/life/research/.scratchpad/20260517-palantir-foundry-analysis.md` — Foundry architecture, moats, financials, 5.x AI-native re-imagining.
- `/Users/danzakon/dev/life/research/.scratchpad/20260517-agent-mcp-identity.md` — MCP authorization spec arc, breach catalogue, MCP gateway pattern, IdP compatibility matrix.
- `/Users/danzakon/dev/life/research/.scratchpad/20260517-iam-incumbent-landscape.md` — IAM market segmentation, funding/M&A through 2026, NHI category, next-gen IGA, the "last mile" problem.
- Sacra — Sierra vs Decagon: https://sacra.com/research/sierra-vs-decagon ($100M ARR Sierra Oct 2025; Decagon $17M ARR April 2025; Sierra $10B / Decagon $650M).
- Decagon pricing (Vendr / eesel breakdown 2026): https://www.eesel.ai/en/blog/decagon-ai-pricing — median ACV $400K, range $100K–580K, $50K minimum platform fee.
- Quiq — 2026 Decagon Pricing: https://quiq.com/blog/decagon-pricing/ — $50K platform fee + ~$0.99/conversation.
- Quiq — Sierra vs Decagon 2026: https://quiq.com/blog/sierra-ai-vs-decagon/ — Sierra $1.50/resolution + $150K typical ACV + $50K implementation.
- Decagon — Pricing the AI Agent Economy: https://decagon.ai/blog/pricing-ai-agents — per-conversation vs per-resolution rationale.
- Cognition Devin self-serve plans: https://cognition.ai/blog/new-self-serve-plans-for-devin — Free / $20 / $200 / $80 Teams / Enterprise custom.
- Glean pricing (gosearch breakdown 2026): https://www.gosearch.ai/blog/glean-pricing-explained/ — ~$50/user/mo, 100-seat min, ~$60K floor, $240K+ typical, paid POC up to $70K.
- RetrieveIT Glean pricing breakdown: https://www.retrieveit.ai/blog/glean-pricing-breakdown — annual 7–12% renewal increase, 10% support surcharge, 2–3x TCO.
- Vendr Glean marketplace: https://www.vendr.com/marketplace/glean — 100–250 seat minimums, multi-year discounting.
- Composio pricing: https://composio.dev/pricing — free 20K tool calls, $29/200K, $229/2M, enterprise custom, $0.249/1K marginal.
- Arcade.dev pricing: https://agentsindex.ai/pricing/arcade-dev — free Hobby (1K standard), $25/mo Growth (2K standard + $0.01 each).
- Speakeasy MCP gateway comparison: https://speakeasyapi.dev/blog/choosing-an-mcp-gateway — Gram, Composio, Arcade, TrueFoundry ($499/mo Pro), Docker MCP Gateway.
- Galaxy Top Knowledge Graph Platforms 2026: https://www.getgalaxy.io/articles/top-knowledge-graph-platforms-enterprise-data-intelligence-2026 — Galaxy, Stardog, Graphwise, Tamr, Timbr, TextQL, Palantir, Cambridge Semantics, Neo4j.
- Timbr Teams/Business pricing: https://timbr.ai/product-overview — $599/$1,199/mo tiers.
- VERSATIL pricing: https://www.vrstl.ai/pricing/ — Ontological Context $1,900/mo, Reasoning Swarm $4,900/mo, Sovereign custom.
- Kamiwaza product: https://www.kamiwaza.ai/product — auto-ontology / Context Manager pattern from a competitor.
- Coginiti pricing: https://coginiti.co/pricing/ — semantic intelligence platform $189/user/yr.
- CrewAI pricing: https://crewai.com/pricing — Basic free, Enterprise custom.
