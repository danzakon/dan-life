# Identity, Access, and Authorization for AI Agents & MCP in the Enterprise

**Category:** Industry / Technical
**Date Started:** 2026-05-17
**Status:** [x] Complete

---

## Summary

The enterprise AI agent boom is colliding with an identity stack that was built for humans clicking buttons in browsers. The Model Context Protocol (MCP) shipped a real OAuth 2.1-based authorization spec in 2025 — and then walked back its most novel parts (Dynamic Client Registration) less than six months later because they did not survive contact with enterprise IdPs. Meanwhile non-human identities (NHIs) now outnumber humans by 45:1 to 100:1 depending on whom you ask, and a wave of named MCP breaches in 2025-2026 (Smithery, GitHub MCP/Invariant, Supabase/Cursor, Asana, postmark-mcp, Splunk, Claude Code MitM, ContextCrush) made it impossible to pretend this is a developer-tools problem.

Most of what is being sold as "agent identity" is rebranded IAM: OAuth 2.1 + token exchange + RFC 8707 + SCIM + a gateway. The genuinely new parts are smaller than the marketing implies — explicit `act` claims for agents in tokens, audience binding becoming non-negotiable, Client ID Metadata Documents replacing DCR, and the slow recognition that the agent must be a first-class identity distinct from both the user it acts for and the workload it runs in. The vendors that will matter are the ones that combine workload identity federation, OAuth-broker gateway, and policy-decision-point authz in a single control plane. Standalone "NHI security" tools that only do discovery will get absorbed.

---

## Key Findings

1. **MCP auth landed on OAuth 2.1 + RS/AS split + RFC 8707** but the spec is on its third major revision in 12 months (2025-03-26 → 2025-06-18 → 2025-11-25). DCR is now deprecated in favor of CIMD. Token passthrough is explicitly forbidden. Audience binding (RFC 8707) is now MUST.
2. **The IdP support gap is the real bottleneck**: as of Q1 2026, Entra ID, Okta, Auth0 are all only partially compliant with RFC 8707. Keycloak just added it. PingFederate 12.1+ is the only fully-compliant major vendor. Most enterprise MCP "compliance" is duct tape.
3. **NHI ratios are real but a junk metric.** 45:1, 96:1, 100:1 all get cited interchangeably. The honest number from Silverfort/Astrix telemetry is 30:1–50:1 in hybrid envs, higher in multi-cloud. The Cyber Strategy Institute correctly calls this a "scare stat" and proposes blast-radius density instead.
4. **At least eight named MCP-related incidents** are documented for 2025-2026: GitHub MCP/Invariant (May 2025), WhatsApp MCP exfil (April 2025), Asana cross-tenant (June 2025), Supabase/Cursor (July 2025), postmark-mcp BCC backdoor (Sept 2025), Smithery (June/Oct 2025 disclosure, 3,000+ servers), Splunk MCP CVE-2026-20205 (Apr 2026), ContextCrush/Context7 (Feb 2026), Claude Code MitM via npm postinstall (May 2026), Anthropic MCP Inspector RCE CVE-2025-49596.
5. **The confused deputy problem is the architectural one MCP cannot patch.** Tool-level RBAC does not fix it. Audience binding helps for token confusion but does nothing for prompt injection-driven scope abuse inside a single legitimate session.
6. **The agent-as-identity vs pass-through-user debate is converging on "both"** — the `act` claim model (RFC 8693 + IETF on-behalf-of-AI-agents draft) where `sub`=user, `act.sub`=agent. Microsoft Entra Agent ID is shipping this. Vendor-neutral spec still in draft.
7. **MCP gateways are the answer enterprises actually buy**, not protocol fixes. Cloudflare, Composio, Arcade, Pomerium, Gram/Speakeasy, TrueFoundry, and Solo.io AgentGateway (Linux Foundation) all converged on the same pattern in 6 months.
8. **MCP adoption is genuinely huge**: 10,000+ public servers, 97M monthly SDK downloads, 28% of Fortune 500, donated to Linux Foundation's Agentic AI Foundation Dec 2025. But 38.7% of MCP servers ship with no authentication. 92% of analyzed servers are rated high-risk.

---

## Details

### 1. The MCP Authorization Spec

#### What it actually says (2025-11-25 current revision)

MCP defines authorization at the transport layer for HTTP-based transports. The protocol explicitly splits two roles:

- **MCP Server = OAuth 2.1 Resource Server** — accepts tokens, validates audience, rejects passthrough.
- **Authorization Server = separate component** (can be co-hosted, but spec strongly prefers external IdP since the April 2025 PR #284 by localden et al.).

The required pieces, with their RFCs:

| Component | RFC | MCP Requirement |
|---|---|---|
| OAuth 2.1 baseline (PKCE mandatory, no implicit, no ROPC) | draft-ietf-oauth-v2-1-13/14 | MUST |
| Authorization Server Metadata | RFC 8414 | MUST |
| Protected Resource Metadata | RFC 9728 | MUST |
| Resource Indicators (`resource` param, audience binding) | RFC 8707 | MUST (since 2025-06-18) |
| Dynamic Client Registration | RFC 7591 | MAY (downgraded from SHOULD in Nov 2025) |
| Client ID Metadata Documents (CIMD) | draft-ietf-oauth-client-id-metadata-document-00 | SHOULD (new default since Nov 2025) |

The flow: client hits server → server returns 401 with `WWW-Authenticate: Bearer resource_metadata="..."` → client fetches `/.well-known/oauth-protected-resource` → discovers AS → fetches `/.well-known/oauth-authorization-server` → registers (CIMD or DCR or pre-reg) → auth code + PKCE → token with `aud` matching the MCP server → resource request.

[Source: modelcontextprotocol.io/specification/2025-06-18/basic/authorization](https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization)
[Source: blog.modelcontextprotocol.io/posts/client_registration](https://blog.modelcontextprotocol.io/posts/client_registration/)
[Source: aaronparecki.com/2025/11/25/1/mcp-authorization-spec-update](https://aaronparecki.com/2025/11/25/1/mcp-authorization-spec-update)

#### The gaps and criticisms

**The DCR fiasco.** The original 2025-03-26 spec made DCR a SHOULD because MCP needed clients (Claude Desktop, Cursor, VS Code, ChatGPT) to talk to arbitrary unknown servers. In practice DCR was a disaster: unbounded database growth, no revocation story, denial-of-service vector, per-instance client_id proliferation, no way to tell a client its registration was nuked. Aaron Parecki: "DCR has been a massive barrier to enterprise adoption of MCP." The Nov 2025 spec replaces it with CIMD — the client publishes a metadata JSON at an HTTPS URL and uses that URL as its `client_id`. Bluesky already does this. It's elegant but desktop clients can't fully use it (no controlled domain).

**The RFC 8707 IdP gap.** [IAMDevBox compatibility table](https://www.iamdevbox.com/posts/mcp-oauth-21-authentication-how-ai-agents-securely-connect-to-tools/) as of Feb 2026:

| Provider | RFC 8707 | DCR | MCP Compliance |
|---|---|---|---|
| PingFederate 12.1+ | Yes | Yes | Fully compliant |
| Keycloak | Custom mapper | Yes | Partial |
| Amazon Cognito | Yes | No | Partial |
| Auth0 | Non-standard `audience` | Partial | Incompatible |
| Okta | No | Partial | Incompatible |
| Microsoft Entra ID | Proprietary syntax | No | Incompatible |

This is why the spec is moving faster than IdPs can keep up. Most enterprise MCP deployments either run their own proxy that synthesizes `aud` claims, or live with the audience-binding weakness.

**Confused deputy in multi-server deployments.** [GitHub issue #1581](https://github.com/modelcontextprotocol/modelcontextprotocol/issues/1581) documents the attack: two MCP servers share an IdP and tenant, the client has one `client_id` consented to scope A on Server1, Server2 advertises scope A via PRM, client requests a token for scope A via Server2, IdP issues without re-consent because client is already trusted. Server2 now has Server1's access. RFC 8707 mitigates this only if the IdP actually validates `resource`. Today most don't.

**Confused deputy via DCR.** Attacker registers a malicious client against a proxy's DCR endpoint, uses the proxy's static client ID (which users have seen before and trust), gets the user to authorize, captures the code. This is part of why DCR is being deprecated.

### 2. How Agents Currently Authenticate

The honest answer: badly, with a six-way mess depending on environment.

**Personal Access Tokens (PATs).** Still dominant for developer tools. GitHub PAT, Slack user token, Notion integration token. Long-lived, broad-scoped, stored in plaintext in `~/.claude.json`, `.env`, or environment variables. The Invariant Labs GitHub MCP attack worked precisely because PATs cover both public and private repos with one token. GitGuardian reported 29M leaked secrets in 2025, and [Cyata's analysis of 5,200+ open-source MCP servers found 24,008 unique secrets embedded in MCP configs](https://policylayer.com/attacks/credential-leak-via-errors). 53% of MCP servers rely on long-lived static credentials.

**OAuth on-behalf-of (delegated, classic).** The web pattern: user authorizes a client to act on their behalf, client gets a token with the user as subject, calls the API. Works fine when there's a human at the keyboard. Breaks when (a) the agent runs unattended, (b) the agent makes autonomous decisions the user didn't specifically authorize, (c) the agent needs to act across multiple resource servers.

**Service accounts with long-lived credentials.** The GCP/AWS service account JSON key, Salesforce integration user, Snowflake user/password. These have been the standard answer for headless workloads forever. They also have caused most of the recent supply-chain breaches (Okta, Cloudflare, Snowflake, Microsoft Midnight Blizzard all involved compromised service accounts).

**Workload identity federation (WIF).** The modern alternative: SPIFFE/SPIRE issues cryptographically verifiable identities (SVIDs) to workloads based on attestation of their runtime environment. AWS IRSA federates Kubernetes service accounts to IAM roles via OIDC. GCP Workload Identity does the same. Azure has Federated Identity Credentials. Aembit's pitch is "workload IAM" that abstracts this across clouds and adds policy. SPIFFE solves "what is this workload" — it does not solve "is this workload acting for the right user." That's the gap blended identity tries to fill.

**Pass-through user identity vs agent-as-its-own-identity.** This is the live architectural debate.

Christian Posta's [June 2025 framing](https://blog.christianposta.com/agent-identity-impersonation-or-delegation/) is the cleanest: **impersonation** ("agent becomes user") works for tool-agents that mechanically execute user intent. **Delegation** ("agent has its own identity and acts on user's behalf") is required as autonomy increases — compliance, audit, and over-privilege all force it. The marketing manager asking her agent to check GDPR compliance is the canonical example: she doesn't have permission to query compliance systems directly, but her agent should be allowed to with explicit attribution.

The technical primitive enabling delegation: the `act` claim in OAuth tokens (RFC 8693 token exchange), nested for multi-hop agent chains. Microsoft Entra Agent ID ships this in production today with proprietary claims (`appid`, `xms_act_fct`, `xms_idrel`). Vendor-neutral version: [draft-oauth-ai-agents-on-behalf-of-user-00](https://www.ietf.org/id/draft-oauth-ai-agents-on-behalf-of-user-00.html) (`requested_actor` on auth request, `actor_token` on token request).

WorkOS [endorsed this approach explicitly](https://workos.com/blog/oauth-on-behalf-of-ai-agents) in April 2026: "What is missing is a vendor-neutral, front-channel flow that asks the user for explicit consent to delegate to a named agent."

### 3. The NHI Explosion

**The numbers**, with sources:

- 45:1 NHI-to-human ratio — [CSA + Astrix Summit RSAC 2025](https://cloudsecurityalliance.org/artifacts/securing-non-human-identities-in-the-age-of-ai-agents-rsac-2025).
- 96:1 in financial services — [CyberArk Oct 2025](https://www.cyberark.com/resources/blog/96-machines-per-human-the-financial-sectors-agentic-ai-identity-crisis), 82:1 across other sectors.
- 20:1–50:1 in hybrid environments per [Silverfort 2025 report](https://resources.silverfort.com/insecurity-in-the-shadows/the-volume-of-nhis-is-growing-fast), with 2020 baseline at 10:1.
- 20,000 NHIs per 1,000 employees per [Astrix](https://cyberdefensemagazine.com/the-frontier-of-security-safeguarding-non-human-identities).
- Up to 100:1 per GitGuardian/Entro cited in [Cyber Strategy Institute 2026 NHI Reality Report](https://cyberstrategyinstitute.cm/2026-nhi-reality-report).

The honest critique from CSI: these numbers are not directly comparable because different orgs count radically different things as NHIs (workload identities? IAM roles? SSH keys? OAuth apps? bot accounts?). They convey scale, not risk.

**What's driving it.** Cloud-native architectures (every service = an identity), AI agents (every agent run = potentially a new identity), shorter certificate lifespans, microservice proliferation. Citi GPS calls it the "Do It For Me" economy. 51% of FinServ orgs expect their identity count to double in 12 months.

**Why traditional IAM fails.** [CSA/Astrix data](https://astrix.security/learn/whitepapers/the-state-of-non-human-identity-security): only 19% of orgs have automated NHI offboarding. 58% try to use general IAM for NHIs, 54% PAM, 36% secrets managers — none designed for NHI lifecycle. 1.5/10 confidence in NHI security vs 2.5/10 for human identity (and humans aren't great either). 45% cite lack of credential rotation as the top NHI incident cause. 38% have no visibility into OAuth third-party apps. Workday's Albert Attias at RSAC 2025: traditional IAM tools "fail at NHI" because they assume an HR system feeds them users — there is no HR system for service accounts.

### 4. Agent-Specific Governance Problems

#### RBAC when the agent acts for the user AND has its own permissions

Aembit calls this "blended identity": Access Policy evaluates user identity (from IdP) AND agent identity (from OAuth redirect URL or client cert) simultaneously, issues a short-lived token scoped to both. Cerbos calls it "dual-principal authorization" in its policy engine. The hard part is not the model — it's that legacy systems downstream only know how to consume a user identity. So you either lie (`sub`=user, drop the agent) or you require every downstream service to be agent-aware.

#### The confused deputy problem

[MCPBlog.dev](https://mcpblog.dev/blog/2026-03-10-confused-deputy-mcp-auth) summarizes it cleanly: "When an MCP server receives a tool call, it faces a question it cannot answer: was the calling agent actually authorized to use these credentials?" Three named variants:

- **Flavour A**: MCP server holds broad service-account credentials and acts on user requests without carrying user identity through. The Asana cross-tenant June 2025 incident is the canonical case — Asana's MCP integration leaked data across organizational boundaries.
- **Flavour B**: Token-confusion — token issued for Server X is replayed at Server Y because Y doesn't check `aud`. RFC 8707 is the fix.
- **Flavour C**: DCR confused deputy — attacker registers a client via MCP proxy DCR, uses proxy's trusted static client ID, redirects auth code.

#### Prompt injection as authorization bypass

This is the architectural one. [PipeLab](https://pipelab.org/learn/mcp-authorization/): "the hardest MCP authorization problem is not in the spec. It is that authentication and authorization both succeed while the agent is being used against the user's interests." The agent has valid scope. The user approved the session. The tool is in the allowlist. The injection lives in fetched content. Tool-level RBAC does not catch this. Audience binding does not catch this. The only real defenses are (a) scoping the token to one repo/tenant/session, (b) content-safety filters on tool results before they reach the model, (c) separating reader/writer MCP servers.

The May 2025 Invariant Labs GitHub MCP disclosure ([devclass.com coverage](https://policylayer.com/attacks/data-exfiltration-via-tool-chaining)): attacker plants instructions in a public GitHub issue, victim asks Claude 4 Opus "check open issues," agent fetches the poisoned issue via `get_issue`, follows the hidden instruction into private repos via `list_repositories` + `get_file_contents`, exfiltrates contents into a PR on the public repo. GitHub explicitly said the fix is architectural (per-session PAT scoping), not a patch.

#### Token theft / exfiltration

[Mitiga's May 2026 Claude Code MitM disclosure](https://www.mitiga.io/blog/claude-code-mcp-token-theft-mitm): malicious npm postinstall hook silently rewrites `~/.claude.json` to point MCP server URLs through an attacker proxy. Tokens transit attacker infra. Provider-side logs show valid OAuth from trusted origin (Anthropic's egress). Token rotation doesn't help — next refresh hits the proxy again.

[ContextCrush / Context7](https://ienable.ai/blog/mcp-supply-chain-compromised.html) (Feb 2026): MCP server with 50K GitHub stars, 8M npm downloads, vulnerable to Custom Rules injection. `.env` exfiltration, arbitrary file deletion, credential theft. Noma Labs presented at RSAC 2026.

[CVE-2025-49596 Anthropic MCP Inspector](https://policylayer.com/attacks/credential-leak-via-errors): Oligo Security disclosure, RCE on developer machine harvests anything in Inspector logs.

[CVE-2025-59536 / CVE-2026-21852 Claude Code](https://policylayer.com/attacks/credential-leak-via-errors): Check Point disclosure, malicious project config including MCP server defs and env vars → RCE + API token theft.

[Splunk MCP CVE-2026-20205](https://policylayer.com/mcp-incidents/splunk-mcp-server-token-disclosure-cve-2026-20205): clear-text token logging to `_internal` index. Patched in 1.0.3 on April 15 2026.

#### Audit trail: user vs agent decision

OBO with `act` claims gives you `sub`=user, `act.sub`=agent. Downstream services can attribute. The problem: most logging infra was designed around a single principal. Cerbos and Aembit both make dual attribution a marketing point ("who, what agent, which resource, policy outcome") because no one else does it natively.

### 5. The Vendor Landscape

The taxonomy that's emerged in 2025-2026:

**Layer 1: Workload identity / NHI primitives** (the "who is this thing?" layer)
- **Aembit** — workload IAM, federates across clouds, SPIFFE JWT-SVID support, "blended identity" model for agents (user + workload in one policy). [aembit.io](https://aembit.io)
- **SPIRE/SPIFFE** — the open-source primitive. Foundational, not a product.
- **Astrix Security** — NHI discovery/posture (the "find all your service accounts and OAuth apps" play). $88M+ funding range. Strong on OAuth third-party app discovery.
- **Token Security, Oasis Security, Entro, Clutch Security, Silverfort** — all in NHI discovery/governance. Largely overlapping pitch. This category will consolidate.

**Layer 2: Agent identity providers** (OAuth + the new draft specs)
- **Descope Agentic Identity Hub** (April 2025 launch) + Control Plane (Aug 2025). MCP Auth SDKs, OAuth + PKCE, supports DCR, policy-based governance. $88M raised. Aggressive on agentic but track record short.
- **WorkOS AuthKit for MCP** — OAuth 2.1 AS for MCP apps. SCIM for agents IETF draft. The B2B SaaS pick.
- **Microsoft Entra Agent ID** — first-party. Agent OBO with `xms_act_fct` claims. Vendor-locked but production-ready.
- **Vouched MCP-I** / DIF — decentralized identity for agents using DIDs + Verifiable Credentials. First open standard donated to DIF.

**Layer 3: MCP gateways / OAuth brokers** (the layer most enterprises actually buy)
- **Arcade.dev** — "MCP runtime", per-user OAuth, scope-pinned tokens, ~100 toolkits, ~8,000 agent-optimized tools. Opinionated on auth scoping. SOC2/HIPAA pitch. Their thesis: ["multi-user agents don't need NHI"](https://www.arcade.dev/blog/why-agents-dont-need-non-human-identity/) — credentials should belong to users, not to the agent.
- **Composio** — 250+ (or 500+ depending on source) managed integrations, OAuth lifecycle, SCIM 2.0, action-level RBAC, SOC2 II, ISO 27001. The "buy don't build" pitch.
- **Pomerium** — identity-aware proxy with first-class MCP support. PPL policies, MCP + upstream OAuth, service accounts for headless agents, RFC 9728 auto-discovery.
- **Cloudflare Access for MCP + AI Gateway + MCP Server Portals** — the most fleshed-out enterprise stack. April 14 2026 reference architecture published. Cloudflare runs 13 production MCP servers internally exposing 182+ tools, all behind Access + portal.
- **Solo.io AgentGateway** — Linux Foundation project. Envoy ext_authz integration with Cerbos for policy.
- **Gram by Speakeasy** — API-to-MCP server generation with built-in auth.
- **TrueFoundry** — RBAC-focused MCP gateway for regulated industries.
- **Docker MCP Gateway** — container-native control plane.
- **Pipedream Connect** — for shops already on Pipedream.
- **Stainless** — MCP server generation from OpenAPI with auth scaffolding.

**Layer 4: Authorization (PDP)**
- **Cerbos** — opinionated YAML policy engine, dual-principal auth, sub-ms eval, Agent2Agent + Agent Gateway integrations, ext_authz over gRPC.
- **OpenFGA** — ReBAC primitives. General-purpose, agent demos exist (agentic-authz repo on GitHub).
- **OPA** — the workhorse. Heavier lift than Cerbos for agent-specific patterns.
- **Permit.io, Aserto, Styra** — competitors in the policy-as-a-service space, all adding "agent" framing.

**Layer 5: Just-in-time access / privileged access** (the "Granted" category)
- **Granted.dev / Common Fate** — JIT cloud access. Repositioning around agent access ("can my agent assume this role for 5 minutes?").
- **HashiCorp Boundary** — session brokering and identity-based access. The classic "no SSH keys" pitch, now being extended to agent sessions.

### 6. The MCP Gateway Pattern

Every enterprise that builds a serious agent practice ends up with an MCP gateway. The pattern, from [Composio's guide](https://composio.dev/content/mcp-gateways-guide):

```
┌─────────────┐    ┌──────────────────────┐    ┌──────────────┐
│  Agents     │───▶│   MCP Gateway        │───▶│  MCP Servers │
│  (Claude,   │    │                      │    │  (Slack, GH, │
│  Cursor,    │    │ • Auth (OAuth/IdP)   │    │  internal,   │
│  Cline,     │    │ • Rate limit         │    │  Postgres,   │
│  ChatGPT)   │    │ • Audit logs         │    │  S3, etc.)   │
│             │    │ • Tool catalog       │    │              │
│             │    │ • RBAC per tool      │    │              │
│             │    │ • Token vault        │    │              │
│             │    │ • DLP scanning       │    │              │
└─────────────┘    └──────────────────────┘    └──────────────┘
```

**Why enterprises build them:**

1. **SSO/SCIM federation.** No enterprise will let an agent platform run its own user directory. Gateway federates Okta/Entra ID/Google. Composio: "SCIM is where most internal builds hit their first serious wall."
2. **Per-user OAuth lifecycle.** Tokens must be per-user, not per-agent. Refresh, rotate, revoke handled centrally. Aembit's blended identity is this with policy.
3. **Action-level RBAC.** Cerbos/OpenFGA/internal. Engineering can `github:create_pr`. Marketing can't. Team Leads only for `github:delete_repo`.
4. **Audit trail.** Who, which agent, which tool, what data, allow/deny, policy version. SOC2/HIPAA tablestakes.
5. **Tool catalog.** Versioning, deprecation, discovery. Cloudflare's "MCP Server Portals" aggregate 13 internal servers exposing 182 tools as one endpoint.
6. **Context bloat control.** Apideck found 3 MCP servers + ~40 tools consumed 143K of 200K context tokens before the first user query. Cloudflare's Code Mode collapses to `search`+`execute` as a 99.9% reduction claim.
7. **Shadow MCP detection.** Cloudflare Gateway April 2026: hostname pattern matching on `mcp.*`, URI patterns on `/mcp`/`/mcp/sse`, JSON-RPC body inspection of `method` field. Block, redirect, or log.
8. **DLP at the gateway.** Cloudflare DLP, regex on tool args and outputs.

**Adoption stats (Q1-Q2 2026):**

- 10,000+ public MCP servers (Anthropic, Dec 2025).
- 97M monthly SDK downloads (March 2026). 2M → 22M → 45M → 68M → 97M trajectory over Nov 2024 → Mar 2026 as OpenAI, Microsoft, AWS, Google adopted.
- 28% of Fortune 500 deployed MCP in production (early 2026). Fintech 45%, healthcare 32%, e-commerce 27%.
- [Bloomberry analysis of 1,400 dedicated MCP subdomains](https://bloomberry.com/blog/we-analyzed-1400-mcp-servers-heres-what-we-learned/): 232% growth in 6 months (Aug 2025 → Feb 2026). 38.7% require no authentication. Auth0 is the most popular auth provider. 50% of companies with an MCP server have no public API at all — meaning MCP is being deployed as a primary integration channel, not an add-on.
- Linux Foundation Agentic AI Foundation (AAIF) formed Dec 2025, AWS/Google/Microsoft/OpenAI/Bloomberg/Cloudflare platinum backers.
- Gartner: 75% of API gateway vendors will have MCP features by end of 2026. 40% of agentic AI projects will be canceled by end of 2027 (cost/value/risk reasons).
- Only 12% of enterprise AI agent projects reach production despite 78% of orgs having pilots (March 2026 650-leader survey).

### 7. Real Incidents (2025-2026)

A complete-as-I-could-make-it list of named, public agent/MCP identity incidents:

| Date | Incident | Class | Source |
|---|---|---|---|
| Apr 2025 | WhatsApp MCP exfiltration | Malicious MCP server with valid scope exfiltrates entire message history | [iEnable summary](https://ienable.ai/blog/mcp-supply-chain-compromised.html) |
| May 2025 | GitHub MCP / Invariant Labs | Prompt injection via public issue + over-scoped PAT → private repo exfil into public PR | [Invariant Labs disclosure 26-05-2025](https://policylayer.com/attacks/data-exfiltration-via-tool-chaining) |
| Jun 2025 | Asana MCP cross-tenant leak | Service-account confused deputy, cross-org data exposure | [PolicyLayer + AuthZed writeup](https://policylayer.com/attacks/confused-deputy) |
| Jun/Oct 2025 | Smithery.ai / GitGuardian | Path traversal in MCP registry build → fly.io token theft → 3,000+ hosted MCP servers accessible, thousands of customer API keys at risk | [GitGuardian disclosure](https://blog.gitguardian.com/breaking-mcp-server-hosting/) |
| Jul 2025 | Supabase MCP / Cursor (General Analysis) | Service-role key + prompt injection via support ticket → `integration_tokens` table dumped into reply | [PolicyLayer](https://policylayer.com/attacks/data-exfiltration-via-tool-chaining) |
| Sep 2025 | postmark-mcp v1.0.16 | Supply chain — silent BCC of all email to attacker | [Koi Security, The Hacker News 30-09-2025](https://policylayer.com/attacks/data-exfiltration-via-tool-chaining) |
| Sep 2025 | Securitypulse "malicious MCP server" | PoC: malicious MCP harvests env vars / tokens on init | [securitypulse.tech](https://securitypulse.tech/en_gb/2025/09/30/malicious-mcp-server-secrets-exfiltration/) |
| 2025 | CVE-2025-49596 Anthropic MCP Inspector | RCE on dev machine, log credential harvest | Oligo Security |
| 2025 | CVE-2025-59536 / CVE-2026-21852 Claude Code | Malicious project config → RCE + token theft | Check Point Research |
| Feb 2026 | ContextCrush / Context7 (50K stars, 8M dl) | Custom Rules injection → .env exfil, arbitrary file deletion | Noma Labs / RSAC 2026 |
| Apr 2026 | Splunk MCP Server CVE-2026-20205 | Clear-text tokens in `_internal` index, CVSS 7.2 | Splunk SVD-2026-0407 |
| May 2026 | Claude Code MitM (Mitiga) | npm postinstall rewrites `~/.claude.json` → OAuth tokens transit attacker proxy, persistent across rotation | [Mitiga disclosure](https://www.mitiga.io/blog/claude-code-mcp-token-theft-mitm) |
| Ongoing | Trend Micro probe | 492 internet-exposed MCP servers with no auth or encryption | [Trend Micro](https://www.trendmicro.com/vinfo/it/security/news/cybercrime-and-digital-threats/mcp-security-network-exposed-servers-are-backdoors-to-your-private-data) |

The pattern is consistent: long-lived broad-scoped credentials + a prompt-injection sink + missing audience checks. Almost none of these are protocol bugs — they are architectural defaults of "give the agent the user's PAT and hope."

### 8. Standards Bodies

The IETF has gone from one agent-auth draft to a small forest in 12 months. The active ones:

- **[draft-oauth-ai-agents-on-behalf-of-user](https://www.ietf.org/id/draft-oauth-ai-agents-on-behalf-of-user-00.html)** — Senarath/Dissanayaka. Auth-code-flow extension with `requested_agent` and `actor_token`. JWT with `sub`=user, `azp`=client, `act.sub`=agent. The cleanest "vendor-neutral OBO for agents."
- **[draft-rosenberg-oauth-aauth](https://www.ietf.org/archive/id/draft-rosenberg-oauth-aauth-01.html)** — Pat White / Jonathan Rosenberg. "Agentic Authorization OAuth 2.1 Extension." Tailored to voice/SMS agents collecting PII over PSTN to get scoped tokens.
- **[draft-klrc-aiagent-auth](https://datatracker.ietf.org/doc/draft-klrc-aiagent-auth/00/)** — leverages WIMSE + OAuth 2.0 family, identity assertion JWT (ID-JAG) for cross-domain access.
- **[draft-yao-agent-auth-considerations](https://www.ietf.org/archive/id/draft-yao-agent-auth-considerations-01.html)** — China Mobile. Considers OBO-user, OBO-self, OBO-agent (chained agents). Defines AID concept.
- **[draft-goswami-agentic-jwt](https://datatracker.ietf.org/doc/html/draft-goswami-agentic-jwt-00)** — "Agentic JWT" with cryptographic agent checksums (hash of system prompt + tools + LLM config) as the agent identity primitive. New `agent_checksum` grant type. Proof-of-Possession at agent identity level.
- **[draft-mishra-oauth-agent-grants](https://datatracker.ietf.org/doc/html/draft-mishra-oauth-agent-grants-00)** — DAAP, DIDs for agent identity, hash-chained audit trail, cascade revocation.
- **[draft-gudlab-agentid-protocol](https://www.ietf.org/archive/id/draft-gudlab-agentid-protocol-00.html)** — AgentID, signed JWT (AIT) with delegation chain claims, scope attenuation.
- **[draft-sharif-openid-agent-identity](https://datatracker.ietf.org/doc/html/draft-sharif-openid-agent-identity-00)** — OIDC profile for agent ID tokens with trust posture, sanctions screening.
- **[draft-beyer-agent-identity-problem-statement](https://www.ietf.org/archive/id/draft-beyer-agent-identity-problem-statement-00.html)** — the problem statement that says "we don't have a model for human-anchored agent identity with delegation and provenance."
- **[draft-ietf-oauth-identity-assertion-authz-grant](https://www.ietf.org/archive/id/draft-ietf-oauth-identity-assertion-authz-grant-00.txt)** — Identity Assertion JWT Authorization Grant (ID-JAG), cross-domain via OIDC IdP. WG-adopted. Aaron Parecki's Nov 2025 writeup called this out as the path for enterprise SSO → MCP token issuance.
- **[draft-ietf-oauth-resource-metadata-13](https://datatracker.ietf.org/doc/draft-mcguinness-oauth-resource-token-resp/)** — McGuinness draft on resource-token-response. Addresses the AS-doesn't-support-RFC-8707 gap by returning audience in token response.

**OpenID Foundation** is hosting the SCIM-for-Agents extension ([WorkOS writeup](https://workos.com/blog/scim-agents-agentic-applications)) — `/Agents` and `/AgenticApplications` SCIM resources with `agentType`, `owners`, `protocols` (including `MCP-Server`), `parent` for hierarchy, `subject` to correlate inbound OIDC tokens.

**Linux Foundation Agentic AI Foundation** (Dec 2025) now stewards MCP, with platinum members AWS/Google/Microsoft/OpenAI/Bloomberg/Cloudflare. This is the governance shift that mostly killed the "MCP is an Anthropic protocol" framing.

**Cloud Security Alliance** is hosting NHI security working groups, RSAC 2025 NHI track partnered with Astrix.

**OWASP** published the MCP Top 10 (beta for 2026), with MCP01:2025 "Token Mismanagement and Secret Exposure" as the top entry, ahead of Insufficient Authorization, Confused Deputy, Prompt Injection via Tool Results, etc.

---

## What's Genuinely New vs Rebranded Old IAM

**Rebranded:**
- "NHI security" = service account hygiene + OAuth third-party app inventory. CIEM/ITDR repackaged.
- "Agent gateway" = API gateway with MCP awareness. Kong, Apigee, Envoy patterns applied to JSON-RPC over HTTP.
- "Workload IAM" = SPIFFE + cloud IAM federation, productized. Aembit's pitch.
- "Agentic OBO" = OAuth Token Exchange (RFC 8693) with one extra `act` claim layer. Microsoft has shipped this since 2018, just not for "agents."
- Most "agent authorization" features in PDPs (Cerbos, OpenFGA, Permit) = the same engine with dual-principal docs and an MCP integration page.

**Genuinely new:**
- **CIMD as a replacement for DCR** — clients identifying themselves by HTTPS metadata URLs. Solves a real open-ecosystem problem that pre-MCP OAuth didn't have.
- **RFC 8707 audience binding becoming MUST** in a major protocol. RFC 8707 existed; it being mandatory and policed is new.
- **The `act` claim chain for autonomous agents** — RFC 8693 supports nested `act`, but the IETF AI-agent drafts are the first time it's the explicit model for "agent A delegated to agent B which called API foo."
- **Blended identity** as Aembit defines it: a single policy decision that evaluates user identity AND workload identity together. Not just "the workload acts as the user" but "is this user via this agent allowed to do this now."
- **Cryptographic agent identity via system-prompt+tools+config checksum** (Goswami draft) — genuinely novel. Whether it survives contact with reality is another matter.
- **Shadow MCP detection at the network layer** (Cloudflare) — new attack surface, new defense.
- **SCIM `/Agents` resource type** — IETF/WorkOS draft. Treats agents as first-class provisionable entities in the directory.
- **Tool poisoning / rug pull / schema injection** — new attack class that doesn't exist outside MCP because no other protocol lets a server retroactively change tool definitions mid-session without a new handshake.

---

## Sources

- [MCP Authorization Spec 2025-06-18](https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization)
- [MCP Authorization Spec draft (2025-11-25)](https://modelcontextprotocol.io/specification/draft/basic/authorization.md)
- [Evolving OAuth Client Registration in MCP — Paul Carleton 22-08-2025](https://blog.modelcontextprotocol.io/posts/client_registration/)
- [Aaron Parecki — Client Registration and Enterprise Management in November 2025 MCP](https://aaronparecki.com/2025/11/25/1/mcp-authorization-spec-update)
- [MCP RFC #284 (Resource Server architecture)](https://github.com/modelcontextprotocol/modelcontextprotocol/pull/284/files)
- [MCP Issue #205 — RS not AS](https://github.com/modelcontextprotocol/specification/issues/205)
- [Keycloak MCP support guide](https://www.keycloak.org/securing-apps/mcp-authz-server)
- [PolicyLayer — Token Mis-redemption / RFC 8707](https://policylayer.com/attacks/token-mis-redemption)
- [PolicyLayer — Confused Deputy in MCP](https://policylayer.com/attacks/confused-deputy)
- [PolicyLayer — Prompt Injection via Tool Results](https://policylayer.com/attacks/prompt-injection-via-tool-results)
- [PolicyLayer — Data Exfiltration via Tool Chaining (2025 incidents)](https://policylayer.com/attacks/data-exfiltration-via-tool-chaining)
- [PolicyLayer — Credential Leak via Errors / OWASP MCP01](https://policylayer.com/attacks/credential-leak-via-errors)
- [PolicyLayer — Splunk MCP CVE-2026-20205](https://policylayer.com/mcp-incidents/splunk-mcp-server-token-disclosure-cve-2026-20205)
- [Mitiga — Claude Code MCP token theft MitM May 2026](https://www.mitiga.io/blog/claude-code-mcp-token-theft-mitm)
- [eSecurityPlanet — Claude Code MCP attack persistent token theft](https://www.esecurityplanet.com/threats/claude-code-mcp-attack-enables-persistent-token-theft/)
- [GitGuardian — Smithery MCP supply chain compromise](https://blog.gitguardian.com/breaking-mcp-server-hosting/)
- [GBHackers — Smithery flaw exposes 3,000+ servers](https://gbhackers.com/critical-mcp-server-flaw/)
- [Deconvolute — MCP Rug Pull / Schema Injection](https://deconvoluteai.com/blog/mcp-schema-injection-attack)
- [iEnable — MCP supply chain compromised](https://ienable.ai/blog/mcp-supply-chain-compromised.html)
- [Trend Micro — 492 exposed MCP servers](https://www.trendmicro.com/vinfo/it/security/news/cybercrime-and-digital-threats/mcp-security-network-exposed-servers-are-backdoors-to-your-private-data)
- [Repello — MCP prompt injection](https://repello.ai/blog/mcp-prompt-injection)
- [MCPBlog.dev — Confused Deputy in MCP Authentication](https://mcpblog.dev/blog/2026-03-10-confused-deputy-mcp-auth)
- [FlowHunt — MCP authentication and authorization](https://www.flowhunt.io/blog/mcp-authentication-authorization-oauth-confused-deputy/)
- [PipeLab — MCP Authorization guide](https://pipelab.org/learn/mcp-authorization/)
- [IAMDevBox — MCP OAuth 2.1 deep dive + IdP compatibility table](https://www.iamdevbox.com/posts/mcp-oauth-21-authentication-how-ai-agents-securely-connect-to-tools/)
- [redteams.ai — MCP auth bypass techniques](https://redteams.ai/topics/agentic-exploitation/mcp-tool-exploitation/mcp-auth-bypass-techniques)
- [CyberArk 2025 State of Machine Identity Security report](https://www.cyberark.com/CyberArk-2025-state-of-machine-identity-security-report.pdf)
- [CyberArk — 96 machines per human FinServ](https://www.cyberark.com/resources/blog/96-machines-per-human-the-financial-sectors-agentic-ai-identity-crisis)
- [CSA + Astrix — State of Non-Human Identity Security](https://astrix.security/learn/whitepapers/the-state-of-non-human-identity-security/)
- [CSA RSAC 2025 — Securing NHI in age of AI agents](https://cloudsecurityalliance.org/artifacts/securing-non-human-identities-in-the-age-of-ai-agents-rsac-2025)
- [Cybersecurity Insiders — NHI 45:1](https://www.cybersecurity-insiders.com/taming-the-machine-securing-the-exploding-world-of-non-human-identities/)
- [Silverfort — Insecurity in the Shadows NHI](https://resources.silverfort.com/insecurity-in-the-shadows/the-volume-of-nhis-is-growing-fast)
- [CSI 2026 NHI Reality Report](https://cyberstrategyinstitute.com/2026-nhi-reality-report/)
- [Astrix CTO Idan Gour — Frontier of NHI security](https://cyberdefensemagazine.com/the-frontier-of-security-safeguarding-non-human-identities)
- [Arcade.dev — Multi-user agent auth without NHI](https://www.arcade.dev/blog/why-agents-dont-need-non-human-identity/)
- [Arcade Docs — MCP Gateways](https://docs.arcade.dev/en/home/mcp-gateways)
- [Composio — Building vs Buying enterprise MCP gateway](https://composio.dev/content/building-vs-buying-an-enterprise-mcp-gateway)
- [Composio — MCP Gateways guide 2026](https://composio.dev/content/mcp-gateways-guide)
- [Speakeasy — Choosing an MCP gateway](https://www.speakeasy.com/blog/choosing-an-mcp-gateway)
- [PkgPulse — Composio vs Arcade vs Pipedream 2026](https://www.pkgpulse.com/guides/composio-vs-arcade-vs-pipedream-connect-ai-agent-tools-2026)
- [Pomerium MCP capabilities](https://www.pomerium.com/docs/capabilities/mcp)
- [Cloudflare — Scaling MCP adoption reference architecture (April 2026)](https://blog.cloudflare.com/enterprise-mcp/)
- [Cloudflare — Internal AI engineering stack](https://blog.cloudflare.com/internal-ai-engineering-stack/)
- [Cloudflare One — Secure MCP servers docs](https://developers.cloudflare.com/cloudflare-one/access-controls/ai-controls/secure-mcp-servers/)
- [Cloudflare AI Gateway features](https://developers.cloudflare.com/ai-gateway/features)
- [Victorino — Enterprise MCP crosses engineering line](https://victorinollc.com/thinking/enterprise-mcp-crosses-silo)
- [gentic.news — Cloudflare ships enterprise MCP governance](https://gentic.news/article/cloudflare-ships-enterprise-mcp)
- [Cerbos — agentic authorization](https://cerbos.dev/features-benefits-and-use-cases/agentic-authorization)
- [Cerbos + Agent Gateway integration](https://www.cerbos.dev/ecosystem/agent-gateway)
- [Cerbos + Agent2Agent integration](https://www.cerbos.dev/ecosystem/a2a)
- [Siddhant-K-code/agentic-authz — OpenFGA agent demo](https://github.com/Siddhant-K-code/agentic-authz)
- [WorkOS — Descope vs WorkOS agentic identity](https://workos.com/blog/descope-vs-workos-agentic-identity-enterprise-authentication)
- [WorkOS — SCIM for AI agents IETF draft](https://workos.com/blog/scim-agents-agentic-applications)
- [WorkOS — OAuth OBO for AI agents (April 2026)](https://workos.com/blog/oauth-on-behalf-of-ai-agents)
- [Aembit — Workload IAM overview](https://aembit.io/wp-content/uploads/2025/02/Aembit-Workload-IAM-Overview-Jan-2025.pdf)
- [Aembit — Blended identities](https://docs.aembit.io/ai-guide/blended-identity)
- [Aembit — AWS WIF support](https://aembit.io/blog/aembit-adds-aws-workload-identity-federation-wif-support/)
- [Aembit — Identity federation for workloads](https://aembit.io/blog/what-identity-federation-means-for-workloads-in-cloud-native-environments)
- [Aembit — JWT-SVID Credential Provider](https://docs.aembit.io/user-guide/access-policies/credential-providers/about-spiffe-jwt-svid/)
- [Microsoft Entra Agent ID OBO flow](https://learn.microsoft.com/en-us/entra/agent-id/agent-on-behalf-of-oauth-flow)
- [Microsoft Entra Agent ID — Interactive agent authentication](https://learn.microsoft.com/en-us/entra/agent-id/identity-platform/interactive-agent-authentication-authorization-flow?tabs=microsoft-graph-api%2Cidentity-web-tokens)
- [Christian Posta — Agent identity: impersonation or delegation?](https://blog.christianposta.com/agent-identity-impersonation-or-delegation/)
- [Christian Posta — Explaining OBO for AI agents](https://blog.christianposta.com/explaining-on-behalf-of-for-ai-agents/)
- [draft-oauth-ai-agents-on-behalf-of-user-00](https://www.ietf.org/id/draft-oauth-ai-agents-on-behalf-of-user-00.html)
- [draft-rosenberg-oauth-aauth-01](https://www.ietf.org/archive/id/draft-rosenberg-oauth-aauth-01.html)
- [draft-klrc-aiagent-auth-00](https://datatracker.ietf.org/doc/draft-klrc-aiagent-auth/00/)
- [draft-yao-agent-auth-considerations-01](https://www.ietf.org/archive/id/draft-yao-agent-auth-considerations-01.html)
- [draft-goswami-agentic-jwt-00](https://datatracker.ietf.org/doc/html/draft-goswami-agentic-jwt-00)
- [draft-mishra-oauth-agent-grants-00](https://datatracker.ietf.org/doc/html/draft-mishra-oauth-agent-grants-00)
- [draft-gudlab-agentid-protocol-00](https://www.ietf.org/archive/id/draft-gudlab-agentid-protocol-00.html)
- [draft-sharif-openid-agent-identity-00](https://datatracker.ietf.org/doc/html/draft-sharif-openid-agent-identity-00)
- [draft-beyer-agent-identity-problem-statement-00](https://www.ietf.org/archive/id/draft-beyer-agent-identity-problem-statement-00.html)
- [draft-ietf-oauth-identity-assertion-authz-grant-00](https://www.ietf.org/archive/id/draft-ietf-oauth-identity-assertion-authz-grant-00.txt)
- [oauth-wg issue #73 — Workload/Agent SSO + OBO](https://github.com/oauth-wg/oauth-identity-assertion-authz-grant/issues/73)
- [Digital Applied — MCP adoption Q2-Q3 2026 forecast](https://www.digitalapplied.com/blog/mcp-adoption-wave-6-month-forecast-q2-q3-2026)
- [Truto — Best MCP server platforms 2026](https://truto.one/blog/buyers-guide-best-mcp-server-platforms-for-enterprise-2026/)
- [Synvestable — MCP enterprise deployment guide](https://www.synvestable.com/model-context-protocol.html)
- [Bloomberry — 1,400 MCP servers analysis](https://bloomberry.com/blog/we-analyzed-1400-mcp-servers-heres-what-we-learned/)
- [AgentMarketCap — MCP April 2026](https://agentmarketcap.ai/blog/2026/04/13/mcp-april-2026-context-layers-agent-identity-observability-enterprise)
- [DreamFactory — MCP server statistics 2026](https://www.dreamfactory.com/hub/mcp-server-statistics)
- [TokenMix — MCP protocol 2026 guide](https://tokenmix.ai/blog/mcp-protocol-guide-2026)
- [SecurityPulse — Malicious MCP attack exposes secrets](https://securitypulse.tech/en_gb/2025/09/30/malicious-mcp-server-secrets-exfiltration/)
- [MCP issue #1581 — multi-server OAuth vulnerability](https://github.com/modelcontextprotocol/modelcontextprotocol/issues/1581)

## Next Steps

- [ ] Draft final reports/20260517-agent-mcp-identity.md with opinionated framing
- [ ] Register in pipeline index.db with new 20260517-RS-NNN ID
- [ ] Write inbox entry with thread, article, hot-take, and post angles
