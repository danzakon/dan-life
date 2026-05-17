# Enterprise IAM / Access Management Incumbent Landscape — 2025-2026

**Date:** 2026-05-17
**Status:** Raw research findings, opinionated
**Purpose:** Map the current state of enterprise identity/access management vendors, find the seams, identify where incumbents are vulnerable, and where new entrants are eating market.

---

## TL;DR — The State of Play

1. **The market has effectively bifurcated into two gravity wells.** Microsoft Entra ID and Okta together command roughly 30-40% of access management mindshare; Microsoft is winning on bundling economics (Entra ID P1/P2 included in E3/E5), Okta is winning on integration breadth (19,000+ OIN connectors) and being the only credible vendor-neutral option. ETR's 2026 Observatory: Entra leads "rebuild preference," Okta leads "most innovative."

2. **Private equity has consolidated the legacy "second tier."** Thoma Bravo owns SailPoint ($6.9B, 2022), Ping Identity ($2.8B, 2022), and ForgeRock ($2.3B, 2023, since merged into Ping). One Identity owns OneLogin. Thales owns Ping. CyberArk was acquired by Palo Alto Networks for $25B in Feb 2026 — the largest identity-security deal in history. The "independent pure-play" identity vendor is going extinct above the $500M revenue line.

3. **The hot money is flowing to three places:** (a) modern access governance / next-gen IGA (Lumos, ConductorOne, Opal, Veza), (b) non-human identity (Astrix, Oasis, Entro, Token), and (c) developer-first B2B CIAM (WorkOS at $2B, Descope $88M, Clerk $50M Series C, Stytch acquired by Twilio for $90M).

4. **The dirty secret:** Despite $24B+ being spent annually on IAM, the average enterprise runs ~830 SaaS apps (Torii 2026), 61% of which are shadow IT, and 73% of provisioned licenses are unused. Most "managed" access is still tracked in spreadsheets, Jira tickets, and Slack DMs — not in any IAM platform. SSO covers maybe 20-30% of the actual app estate.

5. **The "last mile" is the unaddressed gap.** SSO gets you in the front door. It does not touch the internal RBAC inside Salesforce, NetSuite, Workday, Snowflake, Databricks, GitHub, AWS, etc. Each of those has its own permission model that the IdP cannot see, govern, or revoke from. This is the actual problem enterprises are still solving with humans.

---

## Market Segmentation Map

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        ENTERPRISE IDENTITY STACK                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  WORKFORCE IAM (SSO/MFA)      │   CUSTOMER IAM (CIAM)                    │
│  Okta, Entra ID, Ping,        │   Auth0 (Okta), Entra External ID,       │
│  OneLogin, JumpCloud          │   WorkOS, Descope, Stytch, Frontegg      │
│  GWS Identity                 │   Clerk, Ping (ForgeRock)                │
│                                                                           │
├─────────────────────────────────────────────────────────────────────────┤
│  IGA (legacy)                 │   "NEXT-GEN IGA" / ACCESS GOV            │
│  SailPoint, Saviynt,          │   Lumos, ConductorOne, Opal,             │
│  Omada, Oracle IGA,           │   Veza, Apono, Andromeda,                │
│  IBM Verify Gov.,             │   Zluri                                  │
│  One Identity Manager         │                                          │
│                                                                           │
├─────────────────────────────────────────────────────────────────────────┤
│  PAM (legacy)                 │   MODERN INFRASTRUCTURE ACCESS           │
│  CyberArk (PANW),             │   Teleport, StrongDM,                    │
│  BeyondTrust, Delinea         │   HashiCorp Boundary,                    │
│                                │   Akeyless, Keeper                       │
│                                                                           │
├─────────────────────────────────────────────────────────────────────────┤
│  CIEM (cloud entitlements)    │   APP AUTHZ ENGINES                      │
│  Wiz, Tenable (Ermetic),      │   OpenFGA, Auth0 FGA, Cerbos,            │
│  Sonrai, Permiso,             │   Permit.io, Oso, AuthZed,               │
│  CrowdStrike Falcon Identity  │   AWS Verified Permissions, Topaz        │
│                                                                           │
├─────────────────────────────────────────────────────────────────────────┤
│  NHI / WORKLOAD / AGENTS      │   IDENTITY ORCHESTRATION / FABRIC        │
│  Astrix, Oasis, Entro,        │   Strata Identity, Aembit,               │
│  Token Security, Natoma,      │   SGNL (CrowdStrike),                    │
│  P0 Security, Aembit          │   Otterize (Cyera)                       │
│                                                                           │
├─────────────────────────────────────────────────────────────────────────┤
│  SHADOW SAAS / SAAS-TO-SAAS   │   SYSTEM-NATIVE RBAC                     │
│  Cerby, Grip Security,        │   AWS IAM/Identity Center, Azure RBAC,   │
│  Nudge Security, Reco,        │   GCP IAM, Databricks Unity Catalog,     │
│  Wing Security                │   Snowflake RBAC, Salesforce Profiles    │
│                                                                           │
└─────────────────────────────────────────────────────────────────────────┘
```

The lines between these boxes are dissolving fast. Saviynt explicitly converges IGA + PAM + AAG. Microsoft Entra Suite bundles IGA + Verified ID + Internet Access + Private Access. CyberArk now does CIEM. SailPoint added Machine Identity Security and Agent Identity Security modules. Veza, Lumos, and ConductorOne all explicitly position as "the new control plane" that replaces legacy IGA + PAM + CIEM.

---

## Workforce IAM / SSO

### Okta — The vulnerable leader

**What they do:** Workforce Identity + Customer Identity (Auth0). ~19,100 customers, 40% of Fortune 500. $2.84B TTM revenue. Subscription revenue grew 18% YoY to $631M in Q3 FY25 but cRPO growth slowing to 12% — a leading indicator of deceleration.

**Strengths:**
- The Okta Integration Network (OIN) with 19,000+ pre-built SSO/SCIM connectors is the moat. No one else has this breadth.
- Vendor-neutral positioning matters in multi-cloud, polyglot SaaS environments.
- 111% net retention, ~95% renewal — very sticky once embedded.
- 9 consecutive years as Gartner MQ Leader for Access Management.

**Vulnerabilities (be honest):**
- **The 2023 support system breach.** Trust permanently dented. Multiple Fortune 500 RFPs in 2024-2025 explicitly required addressing this in security posture reviews.
- **GAAP operating margin of -10%** despite cuts. Profitability story is shaky.
- **Microsoft bundling is a direct existential threat.** For any org on M365 E3/E5, Okta is a $500K+/year line item ($6-15 PUPM) competing with capabilities effectively "free" via Entra ID P1/P2.
- **Auth0 integration has been slower than expected.** Synergy thesis hasn't materialized — Auth0 still operates semi-independently with separate pricing and stack.
- **IGA and PAM are the obvious land-grabs and Okta is mediocre at both.** TechVision: "Okta's IGA is not as strong as SailPoint, Saviynt, MicroFocus, Clear Skye or ForgeRock." Okta IGA is mostly access requests + reviews bolted onto the IdP. Real IGA customers still buy SailPoint or Saviynt separately.
- **SKU sprawl.** The product portfolio confuses customers.

**Where they're vulnerable to displacement:** Anywhere the customer is Microsoft-heavy and budget-conscious. Anywhere developer-first B2B CIAM is the use case (WorkOS, Descope eat Auth0 lunch under 1M MAU). Anywhere "modern IGA" is the wedge (ConductorOne, Lumos).

### Microsoft Entra ID — The bundling juggernaut

**What they do:** Identity layer for everything Microsoft. 425M-750M monthly active users depending on the source. Free tier bundled with Azure/M365; P1 included in M365 E3 ($6/user standalone); P2 included in M365 E5 ($9/user standalone). Entra ID Governance is now a separate $7 PUPM add-on. Entra Suite (Internet Access, Private Access, Governance, Verified ID) is the newer upmarket bundle. The new E7 SKU at $99 PUPM bundles E5 + Copilot + Agent 365 + Entra Suite.

**Strengths:**
- **Bundling is the weapon.** For an M365-licensed org, the marginal cost of Entra is near-zero. Okta has to justify $500K+ to a CFO who already paid for the alternative.
- Native first-party integration with M365, Defender, Conditional Access, Windows Hello, Intune.
- 9 consecutive years as Gartner MQ Leader for Access Management.
- Entra ID P2's PIM (Privileged Identity Management) is genuinely strong for Azure/M365-scoped privileged workloads.
- First-mover on agent identity with Entra Agent ID (June 2025).

**Vulnerabilities (be honest):**
- **Reviewer pain is real.** Gartner Peer reviews flag Group Management as "half-baked," complex UI, complicated policy engine, MFA database limitations, inconsistent multi-tenant behavior. Microsoft's identity engineering experience is not as good as the licensing economics suggest.
- **IGA capabilities still trail SailPoint/Saviynt despite the Entra ID Governance push.** Lifecycle Workflows and Entitlement Management are usable but not deep.
- **Shelfware.** Directions on Microsoft estimates 20-30% of users actually deploy the E5/P2 capability they're licensed for. The bundling moves shelf — not adoption.
- **Lock-in is the long-term tax.** Every step deeper into Entra Suite is a step further from being able to leave.
- **Outside Microsoft workloads, depth drops fast.** OIN-equivalent breadth for non-Microsoft SaaS just isn't there.

### Ping Identity (Thoma Bravo, merged with ForgeRock)

**What they do:** Enterprise federation, complex hybrid identity, API security, decentralized identity. Now under Thoma Bravo umbrella alongside ForgeRock (acquired Aug 2023, merged into Ping). Estimated 8-12% of CIAM market.

**Strengths:** The "messy middle" of digital transformation — heavy on-prem + cloud, regulated industries (banking, healthcare, government), API security with PingAccess, customer identity orchestration with Ping DaVinci.

**Vulnerabilities:** Private equity ownership has slowed perceived innovation velocity. The Ping + ForgeRock merger is still digesting (architectural overlap is significant). Smaller integration network than Okta. Less developer-friendly than Auth0/WorkOS. Thoma Bravo's playbook is well-known: extract margin, slow new feature investment, eventually re-IPO or sell — customers feel this in their renewal experience.

### OneLogin (One Identity / Quest)

Has effectively been demoted to "mid-market alternative to Okta when you don't want to pay Okta prices." Lost momentum after acquisition. Decent product, no longer a contender for greenfield large-enterprise deals.

### JumpCloud

**What they do:** Cloud directory replacing Active Directory, with SSO + MDM + UEM bundled. Strong in SMB and lower-mid-market (~50-5,000 users), especially Mac/Linux-heavy shops.

**Strengths:** Replaces multiple categories (directory, SSO, MDM, conditional access) in one product. Lower price point. Better than Entra ID for non-Windows fleets.

**Vulnerabilities:** Ceiling is real around 5,000 users — governance, access certification, audit depth don't scale to F2000. Not viable as enterprise IdP for regulated industries.

### Google Workspace Identity

Strong SSO and device-trust for GWS-centric organizations but never broke out as a standalone enterprise IdP. Useful for adjunct use cases (BeyondCorp, context-aware access for Google-stack orgs) but not a serious Okta/Entra contender.

### WorkOS — The B2B SaaS quiet winner

**What they do:** Enterprise auth APIs for B2B SaaS (SSO, SCIM, Audit Logs, FGA). Pure developer-first. Launched 2019. Customers: OpenAI, Anthropic, xAI, Cursor, Perplexity, Vercel, Replit.

**Funding:** $100M Series C at $2B valuation (Mar 2026), led by Meritech and Sapphire. Total raised: $210M.

**Strengths:**
- AuthKit free up to 1M MAU is the most generous free tier in the space. Genuinely changes the math vs Auth0.
- B2B-first product surface (Organizations, Enterprise SSO, SCIM, Audit Logs) is what every modern B2B SaaS sales motion actually needs to close enterprise deals.
- Ate Auth0's developer-mindshare lunch for B2B SaaS use cases.

**Vulnerabilities:** Weak B2C (no progressive profiling, weak bot detection, no adaptive risk). Compliance breadth (no FedRAMP, no PCI direct attestation) limits regulated enterprise sales. Below the upmarket ceiling where Okta/Entra fight.

### Descope, Stytch, Frontegg, Clerk

The developer-first CIAM cluster. All competing for the same wedge: "Auth0 is too expensive, too clunky, too B2C-leaning for modern B2B SaaS."

- **Descope:** $88M total funding (seed extension Oct 2025). Drag-and-drop identity workflows. Strong agentic identity (MCP server auth). FedRAMP High in 2025. Founded by Demisto/Palo Alto Networks alumni.
- **Stytch:** Acquired by Twilio Oct 2025 (~$90M). Strong passwordless, fraud signals, B2C focus. Twilio integration story.
- **Frontegg:** $70M raised. Multi-tenancy + admin portal for B2B. Customers include Cisco, CrowdStrike, Palo Alto Networks (notably their security platforms use Frontegg, not their own products).
- **Clerk:** $50M Series C in Oct 2025. React/Next.js-first. Strong DX. Smaller enterprise muscle.

**Pattern:** All four investing heavily in "agent identity" pivots in 2025-2026 — this is the new differentiation wedge as B2B CIAM commoditizes.

### Auth0 (inside Okta)

Still operates semi-independently. Strong B2C, customer identity, developer brand. Losing developer mindshare to WorkOS/Clerk/Stytch on the bottom end and to Frontegg/Descope on B2B. Pricing remains the sore point — material price increases since Okta acquisition have driven a lot of <1M MAU shops to alternatives.

---

## IGA — The Legacy Tier

### SailPoint (Thoma Bravo)

**What they do:** Enterprise IGA. ~50% of Fortune 500 use SailPoint. Two products: IdentityIQ (IIQ, on-prem, deepest customization), and Identity Security Cloud (ISC, SaaS, more constrained).

**Strengths:** Connector breadth, mature access certification, SaaS Workflows, AI access modeling (Harbor Pilot AI agent, peer-group access recommendations). The default vendor in F500 IGA RFPs.

**Vulnerabilities:**
- **Configuration-driven model frustrates self-service customers.** Practitioner reviews consistently flag that customizations require routing through SailPoint engineers or partners. "Want to understand a workflow? Pay us."
- **IIQ to ISC migrations are bumpy.** 10-30% of custom logic doesn't translate. Two different feature sets create governance gaps for orgs running both.
- **SoD and non-human modules are paid add-ons** — base license understates real deployment spend. Agent Identity Security and Machine Identity Security are separate SKUs.
- **No native PAM** — they integrate with CyberArk/BeyondTrust rather than converging. This becomes a problem now that Saviynt converges PAM in.
- **Implementation is a 12-18 month project.** This is the seam ConductorOne/Lumos hammer in every sales cycle.
- **Thoma Bravo ownership:** the playbook of price hike + reduced R&D investment is a real risk that customers feel at renewal.

### Saviynt

**What they do:** Cloud-only converged platform — IGA + PAM + AAG + CIEM in one product. Reports 50M+ identities under management. Recognized as Gartner Peer Insights Customers' Choice 5 years running.

**Strengths:** The converged story is genuinely differentiated — for an org consolidating from 4 point products, this lands. SoD included in core (not an add-on like SailPoint). Strong cloud-app coverage.

**Vulnerabilities (be candid):**
- **The most damning practitioner pattern in this entire research:** "demo and POC do not match production." Multiple sources document organizations where Saviynt POCs looked spectacular and then production deployments hit performance walls, crashes when adding users to roles, and slow support response. One described it as "flashy stuff with a mediocre engine running it."
- **Multiple concurrent versions** — clean SaaS story is partially marketing; in practice customers run different versions and feel the upgrade tax.
- **Legacy on-prem integration is harder than the connector list suggests.**
- **No on-prem option** is a real blocker for some regulated/sovereign environments.

### Omada, Oracle IGA, IBM Verify Governance, One Identity Manager

The "second-tier legacy" cluster. Real customer bases, mostly defending installed base, occasionally winning in regional or vertical niches:

- **Omada:** Strong in EU (Danish HQ), data residency story, regulatory IGA.
- **Oracle IGA:** Defended only by Oracle-stack lock-in. Not winning new logos outside Oracle shops.
- **IBM Verify Governance:** Mainframe + AS/400 + regulated industries. Customer base aging out. AskIAM (GenAI within Consulting Advantage, June 2025) is the modernization push.
- **One Identity Manager (Quest):** Practitioner favorite for self-service configuration (no vendor lock-in on every customization, unlike SailPoint). Bought OneLogin. Mid-market enterprise lean.

---

## Modern Access Governance / Next-Gen IGA — The Real Disruption

This is the layer where actual displacement is happening. The wedge: "legacy IGA takes 18 months to deploy and costs millions. We do it in weeks for the SaaS-heavy parts of your stack."

### Lumos

**Funding:** $35M Series B (May 2024) at unknown valuation. $65M total. Customers: Pinterest, MongoDB, GitHub, Mars, Anduril.

**What they do:** Unified access platform — SaaS Management + IGA + just-in-time access in one platform. Launched "Albus" autonomous identity agent April 2025.

**Pitch:** "7x faster, 80% lower TCO than legacy IGA." JML automation, access reviews, app discovery, 300+ SaaS integrations.

**Where they're weak:** On-prem and legacy app coverage is thin. Won't replace SailPoint for a regulated bank. Strong for the mid-market and tech-forward enterprises with primarily SaaS stacks.

### ConductorOne

**What they do:** Cloud-native IGA with strong on-prem connectors, just-in-time access, Slack/Teams/CLI UX, Terraform provider. Transparent pricing ($9-11 PUPM by tier).

**Position:** Goes further than Veza (visibility) by adding governance/automation. Goes further than Lumos by claiming on-prem depth via "deep bidirectional connectors."

**Strength:** Developer/DevOps friendly. Pricing transparency. The Veza vs C1 framing is real: Veza is the access graph, C1 is the closed-loop control plane.

### Opal Security

**Funding:** $33.8M total. $1.3M annual revenue (small — early stage). Founded 2020. SF.

**What they do:** Continuous authorization for humans, service accounts, agents. Strong JIT focus. Programmable governance (Terraform, Slack, Jira, PagerDuty integrations).

**Strength:** The most developer-native IGA. "Identity that thinks" branding. Strong policy-as-code story.

**Concern:** Revenue is small ($1.3M). They're in a very crowded space (Lumos, ConductorOne, Veza all going after the same wedge). Headcount dropped 17% YoY. Either they consolidate or they get acquired.

### Veza

**Funding:** $108M Series D at $808M valuation (Apr 2025) led by NEA. $235M total. Strategic investors include Atlassian Ventures, Workday Ventures, Snowflake Ventures.

**What they do:** Access Graph — visualize who has access to what across IdP, SaaS, cloud, data systems (Snowflake, Databricks). Strong on data system access (the unique wedge). Open Authorization API (OAA).

**Position:** "Identity Security Posture Management" — the visibility/discovery layer. Now adding governance via "Access Profiles" and policy enforcement.

**Vulnerability:** Visibility-first products eventually need to enforce. C1 explicitly attacks Veza here. The Snowflake/Atlassian/Workday strategic investment suggests potential acquisition path — Veza is positioning itself to be bought by a data infrastructure player rather than building independence.

### Apono, Andromeda, Zluri

- **Apono:** Strong JIT for cloud infrastructure access. Smaller scale.
- **Andromeda Security:** Autonomous identity security, AI-driven posture management. Early stage.
- **Zluri:** SaaS management + IGA. Strong India market presence. Targets the mid-market.

---

## PAM — The Consolidation Just Happened

### CyberArk — Now Palo Alto Networks

**The bombshell:** Palo Alto Networks closed its $25B acquisition of CyberArk on **February 11, 2026** — the largest identity-security deal ever. Palo Alto integrates CyberArk into Strata and Cortex. This materially changes the long-term picture for CyberArk customers.

**What CyberArk does:** The deepest enterprise PAM platform. Vault, session management, JIT, EPM, secrets management (Conjur), Cloud Entitlements Manager (CIEM). 7 consecutive Gartner MQ Leader. ETR's 2026 data shows Palo Alto/CyberArk combined as a top 3 expansion vendor.

**Strengths:** Unmatched depth for regulated, complex, hybrid environments. The default vendor for F500 PAM. Strong machine/agent identity push.

**Vulnerabilities:**
- **Operational complexity is famous.** "Every update is a nightmare." Native Linux/cloud coverage is weaker than the marketing suggests — most non-Windows protection routes through a Windows bastion. Reviewers explicitly say the SaaS version is "fragile and inconsistent."
- **The PANW acquisition is a wildcard.** Customers who want a heterogeneous security stack now face pressure to standardize on PANW. Some will accelerate exits to Delinea or BeyondTrust.
- **Modern infrastructure access is eating from below** — Teleport, StrongDM, HashiCorp Boundary attack the cloud-native and DevOps use cases where CyberArk feels heavyweight.

### BeyondTrust

**Strengths:** Best-in-class endpoint privilege management. Privileged Remote Access for vendor/third-party access. 7 consecutive Gartner MQ Leader. Pathfinder unified platform. Strong third-party access stories.

**Vulnerabilities:** Sits awkwardly between CyberArk depth and Delinea simplicity. Less brand momentum than either. Owned by Bomgar/Francisco Partners — PE ownership tax applies.

### Delinea (Thycotic + Centrify merger)

**Strengths:** Faster time-to-value, lower TCO, friendlier to mid-market. Acquisitions of Fastpath (IGA) and Authomize (ITDR) broadened the platform. Added to Microsoft Security Store in October 2025.

**Vulnerabilities:** Outgrown by enterprises with the most complex environments. Session management and reporting depth lag CyberArk. Won't win the largest, most regulated deals.

### Teleport / StrongDM / HashiCorp Boundary — Modern infrastructure access

The cloud-native PAM disruptors. Different positioning:

- **Teleport:** Identity-bound short-lived X.509 certificates. No secrets. Native MCP, Kubernetes, SSH, RDP, database access. FedRAMP-capable. Air-gapped support. Per-resource pricing ($20+/resource/month).
- **StrongDM:** Human-first, proxy/credential-vault model. Simpler. Cloud-only.
- **HashiCorp Boundary:** Open-source, identity-aware proxy. Strongest as part of broader HashiCorp stack (Vault, Terraform). Per-session pricing ($0.20/session).

**Where they win:** Engineering-led orgs replacing bastion hosts + VPNs. DevOps-heavy environments. Anywhere "no standing credentials" is the goal.

**Where they don't:** Regulated environments still want CyberArk's session recording compliance pedigree. Windows-heavy admin workflows still favor the legacy vendors.

---

## CIEM — Subsumed by CNAPP

CIEM as a standalone category is effectively dead. Wiz, Tenable, CrowdStrike, Palo Alto all bundle CIEM into broader cloud security platforms.

- **Wiz:** Graph-based attack path analysis across AWS/Azure/GCP. Agentless. Now the default CIEM-as-part-of-CNAPP for cloud-native shops.
- **Tenable (acquired Ermetic 2023):** Strong AWS IAM expertise. Integrated into Tenable Exposure Management.
- **Sonrai:** Independent CIEM specialist, niche relevance.
- **Permiso:** Identity Threat Detection and Response (ITDR) angle — runtime detection, not just posture.

**Insight:** Standalone CIEM startups have been culled. Sonrai is still independent but losing ground. The category resolved upward into CNAPP and downward into CSPM. CIEM is now a feature, not a product.

---

## Application-Level Authorization Engines

The "fine-grained authz" market is finally heating up. State of Authorization 2025: 53% of developers plan to implement fine-grained authz within the next year. Permit.io's report shows ReBAC trending up, driven by Google Zanzibar and OpenFGA.

**The split:**

- **Open source / engineer-led:** OpenFGA (Auth0/Okta-sponsored, Zanzibar-style), Cerbos (YAML policies, OSS core), OPA (general-purpose, Kubernetes-heavy), SpiceDB/AuthZed (Zanzibar pure-play).
- **Managed SaaS:** Permit.io (UI + APIs, MAU-based pricing), Oso Cloud (Polar language, microservices-first), Auth0 FGA (Okta's Zanzibar), AWS Verified Permissions (Cedar policy language), Aserto, Topaz.
- **Embedded in vendors:** Salt Security uses Permit.io. WorkOS shipped FGA in 2024.

**Pattern:** Authz is the new "build vs buy" frontier. Most teams build their own permissions for the first year, then hit a wall when enterprise customers demand custom roles + multi-tenancy + delegation, and adopt an external solution.

**Most likely winners:** OpenFGA (community + Okta backing), Permit.io (UX + breadth), Cerbos (enterprise OSS path). Oso is well-engineered but smaller GTM. Cedar/Verified Permissions wins inside AWS-heavy shops.

---

## Non-Human Identity (NHI) — The Hottest Category of 2024-2026

NHIs outnumber humans by 45:1 in the average enterprise. The Treasury Department, Okta, and Microsoft Midnight Blizzard breaches all started with a single non-human identity (OAuth token, service account, or API key).

**The pure-plays:**

- **Astrix Security:** $85M raised ($45M Series B Dec 2024, Menlo via Anthology Fund / Anthropic strategic). Customers: Workday, NetApp, Priceline, Figma. **Cisco reportedly in talks to acquire for $250-350M (April 2026).**
- **Oasis Security:** $200M total ($120M Series B March 2026, Craft Ventures led; previously $35M Series A from Accel/Sequoia/Cyberstarts). 142 employees. Pivoting to "intent-based access" for agentic AI.
- **Entro Security:** $24M total. Cambridge MA. Strong on secrets in the SDLC, NHIDR (Non-Human Identity Detection & Response).
- **Token Security:** Tel Aviv-based, narrower focus on API tokens and accountability.
- **Natoma, P0 Security:** Smaller, niche plays.

**Adjacent moves:**
- CrowdStrike acquired SGNL for $627.9M (January 2026) — dynamic AI-driven access orchestration.
- Cyera acquired Otterize (June 2025) — NHI for cloud.
- GitGuardian raised $50M (Feb 2026) — secrets sprawl angle.

**Workload identity:**
- **Aembit:** Workload IAM. Identity Federation Hub across AWS/Azure/GCP/SaaS. Strong technical depth. Smaller GTM.
- **Astrix:** Now expanding into broader identity security as a platform.

**Investor thesis:** NHI is the layer existing IAM doesn't touch and existing PAM doesn't scale to. Every legacy player (SailPoint, Saviynt, CyberArk, Veza, Okta) is bolting on NHI features — but they're retrofitting human-centric platforms, which is a structural disadvantage vs Oasis/Astrix/Entro who built for it natively. This is exactly the dynamic that gave Veza its valuation against SailPoint.

---

## Identity Orchestration / Fabric

**Strata Identity:** Maverics platform. Multi-IdP abstraction layer. Built by Eric Olden (SAML co-author). Goes after orgs running Okta + Entra + ADFS + PingFederate post-M&A who need to unify them. Added MCP-native AI agent orchestration July 2025.

**The pitch:** "You don't need to consolidate IdPs — we orchestrate across them." Real customer need post-acquisition. Hexa (open-source IDQL) is the standardization play.

**Vulnerability:** Customers eventually want to consolidate, not orchestrate. Strata is selling a transitional product — the question is whether the transition is permanent enough to build a $1B business on.

---

## SaaS-to-SaaS / Shadow IT Identity

The "everything Okta SCIM can't reach" category.

- **Cerby:** $112.5M total funding ($40M Series B May 2025, DTCP). 2,000+ apps automated. Strong on "disconnected applications" — apps without SCIM, SAML, or modern auth. Notable investor: Okta Ventures (Okta funding its own complement).
- **Grip Security:** $66M total. Strong SSPM + identity threat detection for SaaS. Boston-based, Israeli founders.
- **Nudge Security:** $22.5M Series A (Nov 2025, Cerberus Ventures). 3x ARR growth two years running. Strong workforce-edge AI/SaaS governance.

**Why this matters:** The Okta/Entra ID strategy assumes apps support SAML/OIDC/SCIM. In reality, the long tail of enterprise SaaS — partner portals, marketing tools, social media accounts, AI tools, legacy systems — doesn't. Cerby's whole business is the gap between "we have SSO" and "we actually control access to every app."

---

## System-Native RBAC — The Unaddressed Iceberg

This is the part of the market everyone politely ignores. Each major SaaS / cloud platform has its own internal permission model that no external IAM tool can natively govern:

- **AWS IAM / Identity Center:** 30,000+ permissions across services. Identity Center is the IdP layer; IAM is the resource permission layer.
- **GCP IAM:** Project/folder/org hierarchy + roles.
- **Azure RBAC:** Subscription/resource group/resource scopes + role assignments.
- **Databricks Unity Catalog:** Workspace + catalog + schema + table + column permissions.
- **Snowflake RBAC:** Account/warehouse/database/schema/table grants. Notoriously complex.
- **Salesforce Profiles + Permission Sets:** Profile (base) + permission sets (additive) + permission set groups + sharing rules. Famously chaotic in any mature org.
- **GitHub:** Org/team/repo/branch permissions.
- **Workday, NetSuite, ServiceNow:** Each has multi-thousand-line internal authorization models.

**The hard truth:** SSO + SCIM provisioning gets a user "into" these systems with a coarse role. The actual *meaningful* access — who can approve a $5M wire, who can read salary data, who can drop a production table — is configured *inside* each system. Most IGA platforms can read but not effectively govern these internal models. SailPoint and Saviynt have deep connectors for some (Workday, SAP, Salesforce); Veza explicitly differentiates on reading data system permissions. ConductorOne and Lumos lean on the JIT model — request elevated access, time-bound, then revoke — to sidestep the problem rather than solve it.

This is *the* unaddressed seam in enterprise IAM and the reason most access governance work happens in spreadsheets, Jira tickets, and Slack DMs — not in any vendor platform.

---

## How Fragmented Enterprise Access Actually Is — The Statistics

The data is staggering:

- **Torii 2026 SaaS Benchmark:** Avg enterprise runs **830 apps**. Large enterprises (5,000+ employees) average **2,191 apps**. Average employee uses **40 apps**.
- **Torii 2026:** **61.3%** of apps qualify as shadow IT. Only **15.5%** are formally sanctioned.
- **Okta Businesses at Work 2025:** Average org crossed **101 apps**. Most catalogs list 30-40 — so the official IT inventory is missing 60-70% of reality.
- **Grip Security 2025 report:** **85%** of SaaS apps are unknown and unmanaged. **91%** of AI tools are unmanaged. Analyzed 29M user accounts, 1.7M identities, 23,987 distinct apps.
- **Torii 2025:** **61% of provisioned SaaS apps are inactive** but still paid for. **73%** of provisioned users don't use the app.
- **Zylo 2025 SaaS Management Index:** Large enterprise (10,000+ employees) avg $284M SaaS spend, 660 apps. Lines of business (not IT) account for **70% of SaaS spend**. IT is just 26.1%.
- **Netskope 2025:** Average org uses **9.6 GenAI apps**; top quartile uses 24+. Mostly via personal accounts or browser extensions outside the IdP.
- **Verizon DBIR 2025:** **88%** of Basic Web App Attacks use stolen credentials.
- **NHI ratio:** ~45 NHIs per human user in modern cloud environments.

**The implication:** When a CISO buys Okta + SailPoint + CyberArk + Wiz + Lumos + Astrix + Cerby, they are *still not covering* the majority of access surface area in their org. The "managed" stack is the tip; 60%+ is unmanaged and the percentage is growing as AI tools proliferate.

---

## The "Last Mile" Problem — SSO ≠ RBAC

This deserves its own callout because it's the misunderstood gap that funds the entire next-gen IGA space.

**The story enterprises tell themselves:**
> "We have Okta. Our access is governed. SSO + MFA = secure."

**What actually happens:**

```
        Okta/Entra (Identity Provider)
              │
              ▼ SSO + SCIM
   ┌──────────────────────────┐
   │   Salesforce             │ → Internal: 50+ profiles, 200+ permission sets,
   │                          │   sharing rules, field-level security
   │                          │   (Okta has no visibility into any of this)
   ├──────────────────────────┤
   │   Snowflake              │ → Internal: warehouse grants, database/schema/table
   │                          │   grants, future grants, masking policies
   ├──────────────────────────┤
   │   AWS Identity Center    │ → Internal: 30K+ IAM permissions, SCPs, resource
   │                          │   policies, session policies, ABAC tags
   ├──────────────────────────┤
   │   GitHub                 │ → Internal: org/team/repo/branch/CODEOWNERS
   ├──────────────────────────┤
   │   Workday                │ → Internal: security groups, domains, business
   │                          │   processes, role-based access — thousands of perms
   └──────────────────────────┘
```

The IdP authenticates and provisions a coarse role. Inside each system, the *actual* permission decisions are made — and the IdP cannot see them, cannot revoke them, and cannot certify them.

**Who's trying to solve this:**
- **Veza** — data system access graph is the explicit wedge. Reads Snowflake/Databricks/Salesforce permissions.
- **SailPoint / Saviynt** — deep connectors for the largest SaaS apps but breadth is limited.
- **ConductorOne / Lumos** — JIT model sidesteps standing entitlements.
- **Cerby** — handles the long tail of apps that don't support SCIM at all.
- **System-native answers** — Databricks Unity Catalog, Snowflake Horizon — vendors are racing to be the "control plane for their own product."

**Verdict:** No vendor has solved this fully. This is the next $5-10B opportunity in IAM and the reason valuations like Veza ($808M), Lumos, and ConductorOne keep climbing despite small ARR.

---

## Recent Funding & M&A — 2024-2026

**Mega deals:**
- **Palo Alto Networks / CyberArk:** $25B (closed Feb 2026). Largest identity-security M&A ever.
- **Thoma Bravo / SailPoint:** $6.9B (Aug 2022; SailPoint re-IPO'd Feb 2025).
- **Thoma Bravo / Ping Identity:** $2.8B (Aug 2022).
- **Thoma Bravo / ForgeRock:** $2.3B (Aug 2023, merged into Ping).
- **Thales / Imperva:** Adjacent but relevant ($3.6B 2023).
- **Okta / Auth0:** $6.5B (2021, still being digested).

**Modern access governance / next-gen IGA:**
- **Veza:** $108M Series D at $808M val (Apr 2025, NEA). Total $235M. Atlassian/Workday/Snowflake strategic investors.
- **Lumos:** $35M Series B (May 2024, Scale Venture Partners). Total $65M.
- **Opal:** $33.8M total.
- **ConductorOne:** Series B raised (specific amount/date unclear from sources).

**Developer CIAM:**
- **WorkOS:** $100M Series C at $2B (Mar 2026, Meritech + Sapphire). Total $210M.
- **Descope:** $35M seed extension (Oct 2025). Total $88M.
- **Clerk:** $50M Series C (Oct 2025).
- **Twilio acquired Stytch:** ~$90M (Oct 2025).

**Non-human identity:**
- **Oasis:** $120M Series B at undisclosed val (March 2026, Craft Ventures). Total $200M.
- **Astrix:** $45M Series B (Dec 2024, Menlo Anthology Fund). Total $85M. **In talks with Cisco for $250-350M acquisition (April 2026).**
- **CrowdStrike / SGNL:** $627.9M (Jan 2026).
- **Cyera / Otterize:** undisclosed (June 2025).
- **GitGuardian:** $50M (Feb 2026, Insight).
- **Entro:** $18M Series A (June 2024, Dell Technologies Capital). Total $24M.

**Shadow SaaS:**
- **Cerby:** $40M Series B (May 2025, DTCP) + $40M extension (Oct 2025). Total $112.5M.
- **Nudge Security:** $22.5M Series A (Nov 2025, Cerberus Ventures).

**Investor thesis pattern:** The biggest bets in 2024-2026 are NOT on workforce SSO (mature, dominated by MSFT/Okta) or legacy IGA (Thoma Bravo owns the assets). They're on (1) the access governance control plane above SaaS apps (Veza, Lumos, ConductorOne), (2) non-human/agent identity (Oasis, Astrix), and (3) developer-first B2B CIAM (WorkOS, Descope). These three categories are where 80%+ of identity venture capital is flowing.

---

## The Dirty Secret: Spreadsheets and Jira Tickets

Despite the $24B+ market and the hundreds of vendors above, the actual reality of enterprise access management is:

- **Access requests:** Filed in Jira, ServiceNow, or Slack. Approved by managers who have no idea what the access does. Provisioned manually by IT.
- **Access reviews:** Quarterly Excel spreadsheets emailed to managers. "Rubber-stamping" is the norm. SailPoint's own data shows reviewers revoke access 2x as often when AI recommendations are present — implying that without recommendations, the default is to approve everything.
- **Joiner-Mover-Leaver:** HR systems push a status change, but the actual access modification often relies on Workday → manual ticket → IT acts → maybe 24 hours later. Movers (role changes) are the worst: accumulated access from prior roles is rarely revoked.
- **Offboarding:** The most-cited security incident pattern. Terminated employees retain access to SaaS apps for weeks or months because deprovisioning relies on a manual checklist or a partial SCIM connection.
- **Shadow IT:** 61% of apps. Nobody knows who has access. There is no review process because there is no inventory.
- **Service accounts and tokens:** Created by developers, documented nowhere, often shared, with permissions accumulated over years. The Okta breach (Oct 2023) and Treasury breach (Dec 2024) both started with non-human credentials nobody was tracking.

**Opal's own analysis** (March 2026): They analyzed 500,000 access requests on their platform — median approval time was 15 minutes, but some enterprises were taking 24+ hours per request. **43.5% of all requests** went through approval friction that delayed user productivity.

**Implication for buyers:** The actual problem most enterprises have is not "we don't have an IdP." It's:
1. "We have an IdP and we still don't know who has access to what."
2. "We have an IGA and access reviews are still a quarterly fire drill."
3. "We have PAM but 80% of the access that matters is outside it."

The vendors that win the next decade are the ones that bridge from "policy on paper" to "actual operational reality" — automation that doesn't require dedicated identity engineers to maintain, and visibility that doesn't require six-figure SI implementations to surface.

---

## Vulnerability / Strength Snapshot — Opinionated

**Strongest position right now:**
1. **Microsoft Entra ID** — bundling is the unbeatable weapon. Will continue gaining share, especially among CFO-pressured orgs with M365 deployments.
2. **CyberArk (PANW)** — depth + the PANW distribution machine. Even if customers grumble, switching costs are massive.
3. **SailPoint** — F500 lock-in is durable for 5+ years. Re-IPO gives them capital and credibility.
4. **WorkOS** — owns AI-first B2B SaaS. Genuine moat in developer mindshare.
5. **Wiz** — CIEM-as-CNAPP is the resolution and Wiz is the default.

**Most vulnerable incumbents:**
1. **Okta** — Microsoft on one flank, ConductorOne/Lumos on the other, Auth0 alternatives on the third. Net retention still strong but cRPO deceleration is telling.
2. **Auth0** — losing developer mindshare to WorkOS/Clerk/Stytch. Pricing keeps pushing customers away.
3. **Saviynt** — the demo-vs-production gap is becoming a real reputation problem.
4. **Delinea** — squeezed between cloud-native (Teleport/StrongDM) and CyberArk depth.
5. **Ping Identity / ForgeRock** — Thoma Bravo extraction mode, slowing innovation, customers feel it at renewal.

**Most over-valued (or at risk of being so):**
- **Veza at $808M** with small ARR. Beautiful technology, crowded space, strategic investors suggest acquisition path. Could be a great exit or a down round.
- **Opal** at $33M raised with $1.3M revenue and headcount cuts.

**Best risk/reward bets right now:**
- **Oasis Security** for NHI — the founder bet (ex-IDF head of cyber R&D), the technical pivot to intent-based access for agents, $200M war chest.
- **Cerby** for shadow SaaS — the only player solving the genuinely-disconnected-app problem at scale with 2,000+ integrations.
- **ConductorOne** for next-gen IGA — pricing transparency, on-prem connectors, doesn't rely on Veza's visibility-only thesis.

**The category that will be biggest in 2028 that nobody is fully solving in 2026:** Agent identity and authorization. Every vendor in this report is racing to add "agent" features (Microsoft Entra Agent ID, SailPoint Agent Identity Security, Okta agent identity, Descope Agentic Identity Hub, WorkOS MCP auth, Strata MCP-native, Aembit workload IAM, Astrix AI Agents). Nobody has won yet. The winner needs to solve: (1) ephemeral agent identity issuance, (2) intent-based authorization (Oasis's bet), (3) human-in-the-loop step-up for sensitive actions, (4) cross-system audit trail. The first vendor to ship this cohesively at production scale will own the agentic identity layer the way Okta owned the SaaS SSO layer.

---

## Where the Lines Are Blurring (Convergence Map)

```
Okta ────► IGA (acquiring/building)
            ▲
SailPoint ──┤── Saviynt ──► PAM (converged, native)
            │
CyberArk ───┤── Adding CIEM (Cloud Entitlements Mgr)
            │── Adding NHI (Conjur, Secrets Hub)
            │
Microsoft ──┤── Adding everything (Entra Suite + Agent ID)
            │
Wiz ────────┤── CIEM became CNAPP
            │
Lumos/C1 ───┤── SaaS Mgmt + IGA + PAM-lite (JIT)
            │
Veza ───────┴── ISPM → IGA → data system govern.
```

The pattern is clear: every vendor is trying to become the "identity security platform" — one console, every identity type, every system. Microsoft has the best chance to actually pull it off because they have the bundling distribution. Everyone else is racing to build "consolidation" stories.

The opposite force: best-of-breed vendors (Wiz, CrowdStrike, Palo Alto, CyberArk) are eating into the converged-platform pitch by being demonstrably better at one slice. Microsoft customers routinely buy CrowdStrike instead of MDE, Wiz instead of Defender for Cloud, Okta instead of Entra ID — because the bundle is "good enough" but not actually best.

---

## Open Questions for Follow-Up

- **Is Veza heading to a Workday/Snowflake/Atlassian acquisition?** Strategic investor pattern suggests yes within 18 months.
- **Will Cisco actually close on Astrix?** $250-350M would set the NHI category benchmark.
- **Does Lumos or ConductorOne consolidate?** Both attacking same wedge with similar messaging; M&A is plausible.
- **How does Palo Alto integrate CyberArk?** This determines whether F500 CyberArk customers stay loyal or exit to BeyondTrust/Delinea.
- **Where does Okta land in 5 years?** Microsoft pressure is real. They either become the dominant independent platform via IGA/PAM/agent identity expansion, or they become the next ForgeRock — bought by PE, slowly milked.

---

## Sources (Selected)

- ETR Identity Security Observatory 2026 (310 IT decision-makers)
- Gartner Magic Quadrant for Access Management 2025 (Microsoft 9-year Leader)
- Gartner Magic Quadrant for PAM 2025 (CyberArk Leader, 7th consecutive)
- Forrester Wave: Workforce Identity Security Platforms Q4 2025 (32 vendors)
- Forrester Wave: Privileged Identity Management 2025 (CyberArk Leader)
- MarketsandMarkets: US IAM market $7.34B → $11.09B by 2030 (CAGR 8.6%)
- Deepak Gupta CIAM Industry Research (CIAM $14.12B → $22.47B by 2030)
- Torii SaaS Benchmark Report 2026 (830 apps avg, 61% shadow IT)
- Grip Security 2025 SaaS Risks Report (85% unknown, 91% AI unmanaged)
- Okta Businesses at Work 2025 (101 apps avg)
- Netskope Cloud & Threat Report 2025 (9.6 GenAI apps avg)
- Permit.io State of Authorization 2025 (53% planning fine-grained authz)
- Verizon DBIR 2025 (88% credential-based attacks)
- Multiple vendor funding announcements and Exa company profiles
