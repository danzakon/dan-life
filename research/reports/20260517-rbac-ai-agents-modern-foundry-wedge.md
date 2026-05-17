---
id: 20260517-RS-001
date: 2026-05-17
category: Research Report
content-status: raw
---

# RBAC, AI Agents, and the Modern Foundry: Why Centralized Access Control Is the Wedge

> An opinionated end-to-end research report on access control fundamentals, the enterprise IAM incumbent landscape, the new agent/MCP identity problem, Palantir Foundry's actual moat, and the case for building an AI-native enterprise operating system with RBAC as the entry point.

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Part I — Foundations of Access Control](#part-i--foundations-of-access-control)
3. [Part II — How Enterprises Actually Handle IAM Today](#part-ii--how-enterprises-actually-handle-iam-today)
4. [Part III — The AI Age Breaks the IAM Stack](#part-iii--the-ai-age-breaks-the-iam-stack)
5. [Part IV — The Competitive Landscape for an "Agent Access Layer"](#part-iv--the-competitive-landscape-for-an-agent-access-layer)
6. [Part V — Palantir Foundry, Honestly Read](#part-v--palantir-foundry-honestly-read)
7. [Part VI — The Modern Foundry Thesis](#part-vi--the-modern-foundry-thesis)
8. [Part VII — Token Spend Governance: The Tertiary Wedge Worth Taking Seriously](#part-vii--token-spend-governance-the-tertiary-wedge-worth-taking-seriously)
9. [Part VIII — Market Sizing, GTM, and a Concrete Path](#part-viii--market-sizing-gtm-and-a-concrete-path)
10. [Key Takeaways](#key-takeaways)
11. [Predictions](#predictions)

---

## Executive Summary

The user's intuition is correct but the timing window is tighter than they think. Enterprises do not have a centralized access control plane for AI agents, MCP servers, and the cross-system actions agents now perform on behalf of employees. Okta and WorkOS solved the *human-to-SaaS* problem; SailPoint and Saviynt solved (badly) the *governance-of-human-access* problem; CyberArk solved the *privileged-human* problem. None of them solved — or were architected to solve — what happens when an autonomous agent acts on behalf of a user, with its own identity, across thirty SaaS systems, each with their own internal RBAC model the IdP cannot see. That is the gap, and it is real.

The harder truth is that the obvious incumbents have already noticed. **Microsoft Entra Agent ID went GA in May 2026. Okta for AI Agents went GA April 30, 2026. AWS Bedrock AgentCore Gateway + Verified Permissions is GA in nine regions. Palo Alto Networks just paid $25B for CyberArk (Feb 2026). SGNL was bought by CrowdStrike for $627.9M in January 2026. Cisco is reportedly in talks to acquire Astrix at $250–350M.** The greenfield window for "agent identity" as a standalone wedge product is closing within 12–18 months. Pure-play "NHI security" startups will be acqui-hired into security platforms. The opportunity is *not* to build a better Astrix.

The real opportunity — and where the user's Palantir Foundry analogy is right — is one layer up. Foundry's moat is not its data integration; it is the **ontology + lineage-aware permissions + forward-deployed engineer motion + compliance pedigree** stacked together. If you started Foundry in 2026, you would not build a heavy-handed data integration platform first; you would build the **agent-and-data access control plane**, use *that* as the customer-specific metadata graph (the agent-native ontology), and let agent-driven operational workflows accrete on top. RBAC for agents is not a security product. It is the *acquisition vector* for the enterprise's operating system of AI work, exactly as the ontology was for Palantir's operating system of data.

This report walks the entire stack — from Ferraiolo-Kuhn 1992 to the MCP authorization spec to the Cisco/Astrix rumor — and ends with a concrete wedge: **OSS MCP gateway → managed agent access plane → FDE-led ontology builds in one named vertical with one named SI partner, priced from $250K (CAIO-approvable) to $5M+ (full triad).** The token spend problem is real and worth $10–20B by 2030, but it is the tertiary wedge, not the primary — it commoditizes faster than identity, and the gateways already in market (Portkey, LiteLLM, Cloudflare) are well ahead.

---

## Part I — Foundations of Access Control

### 1.1 Why this matters before we get to agents

You cannot reason about agent authorization without a clean model of human authorization, because every credible agent-auth proposal in 2026 is a delta on existing OAuth 2.1 + RBAC + ABAC primitives. This section is the novice-to-advanced curriculum, compressed.

### 1.2 The historical arc: DAC → MAC → RBAC

The Trusted Computer Security Evaluation Criteria ("Orange Book," 1983) established two access-control families:

- **Discretionary Access Control (DAC).** Object owners grant access at their discretion. Unix file modes, Windows ACLs. Failure mode in enterprises: the user is not actually the owner of corporate data; the corporation is.
- **Mandatory Access Control (MAC).** A system-enforced policy ties subject clearances to object labels (Bell-LaPadula confidentiality, Biba integrity). Too rigid for commercial use.

In 1992, [Ferraiolo and Kuhn presented "Role-Based Access Controls"](https://csrc.nist.gov/files/pubs/conference/1992/10/13/rolebased-access-controls/final/docs/ferraiolo-kuhn-92.pdf) at the 15th National Computer Security Conference. The insight: in real organizations, access is naturally organized by *function* (teller, auditor, doctor), not by ownership or sensitivity label. RBAC formalized **users**, **roles**, **permissions**, **sessions**, role hierarchies, and constraints — all access flows through roles, roles change slowly, and user-role and permission-role mappings change more often.

[Sandhu, Coyne, Feinstein, Youman (1996)](https://csrc.nist.gov/csrc/media/projects/role-based-access-control/documents/sandhu96.pdf) formalized the RBAC0/1/2/3 family. ANSI/INCITS adopted the unified [NIST model in 2004 as INCITS 359-2004](https://csrc.nist.gov/Projects/role-based-access-control/faqs), defining Core RBAC, Hierarchical RBAC, Static SoD, and Dynamic SoD.

### 1.3 Core RBAC, fast

```
User  ──UA──► Role ──PA──► Permission (operation, object)
                 │
                 ▼
              Session (subset of authorized roles activated at runtime)
```

- **Role hierarchy** — `Manager ⊒ Employee`. Tree (single inheritance) or DAG (multiple).
- **Separation of Duties (SoD)** — the most-cited constraint type because it directly maps to SOX-style financial fraud controls. Static SoD prevents both being *assigned*; Dynamic SoD prevents both being *activated* in the same session. Per [NIST SP 800-192](https://nvlpubs.nist.gov/nistpubs/specialpublications/nist.sp.800-192.pdf): "no user should be given enough privileges to misuse the system on their own."

### 1.4 The progression: PoLP → ZSP → JIT → Zero Trust

```
Principle of Least Privilege (PoLP)
  └─► Zero Standing Privilege (ZSP) — no permanent elevation
        └─► Just-in-Time access (JIT) — grant on demand, time-bound
              └─► Zero Trust Architecture (NIST SP 800-207) — every request re-evaluated
```

Plain definitions:

- **Principle of Least Privilege (PoLP).** Grant a user (or agent) the minimum permissions needed to do their job — nothing more. If a marketing analyst only needs to read three Salesforce reports, they should not have write access to the customer database. The oldest and most foundational rule in access control, articulated by Saltzer and Schroeder in 1975.

- **Zero Standing Privilege (ZSP).** A stricter version of PoLP that says: no one — not even admins — should *permanently* hold elevated permissions. Privileges only exist while they are actively being used. The reasoning: any standing privilege is a blast radius waiting to be exploited if the account is compromised.

- **Just-in-Time access (JIT).** The mechanism that makes ZSP practical. Instead of carrying admin rights all the time, a user requests them when needed. The request is approved (automatically or by a human), permissions are granted for a short, time-bound session (CyberArk defaults to 4 hours), and then auto-revoked when the session ends or the work is done.

- **Zero Trust Architecture (ZTA).** The umbrella security philosophy from [NIST SP 800-207](https://nvlpubs.nist.gov/nistpubs/specialpublications/NIST.SP.800-207.pdf): never grant implicit trust based on network location ("inside the corporate firewall"). Every request from any user, device, or service must be authenticated and authorized fresh, based on current identity, device posture, and context. The phrase "never trust, always verify" is the slogan.

The progression: *don't grant more than needed* (PoLP) → *don't keep it standing* (ZSP) → *grant on demand* (JIT) → *re-verify every request* (Zero Trust).

[NIST SP 800-53 AC-6](https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final) codifies least privilege as a mandatory control for federal systems. The modern enterprise pattern (CyberArk, Teleport, ConductorOne, Opal) is JIT with 4-hour default sessions, automated approval, instant revocation.

### 1.5 RBAC vs ABAC vs ReBAC vs PBAC vs ACL — the five access control models

These five models are the universe of how systems decide "is this person allowed to do this thing?" Each one represents a different basis for the decision.

- **ACL — Access Control List.** The oldest model. Each object (file, database row, document) carries a literal list saying which specific users or groups can do what. Unix file permissions are an ACL (`alice: read, bob: write, others: none`). Windows NTFS file permissions are an ACL. Works fine for small systems; falls apart at enterprise scale because the list size grows as users × objects, and there is no abstraction for "everyone on the marketing team."

- **RBAC — Role-Based Access Control.** Adds *roles* as an indirection between users and permissions. Instead of granting Alice access to 47 specific objects, you grant Alice the "Marketing Manager" role, and the role itself carries the 47 permissions. Now when Bob joins marketing, you grant him one role instead of 47 individual grants. The model the rest of this report is largely about. Failure mode: "role explosion" — every contextual nuance (Marketing Manager in EU vs US vs APAC, with vs without budget approval authority) spawns a new role until there are 1,300 of them.

- **ABAC — Attribute-Based Access Control.** Replaces "what role do you have?" with "what are the attributes of the user, the resource, the action, and the environment, and do they satisfy this predicate?" Example policy: `allow if user.department == resource.owner_department AND time.hour BETWEEN 9 AND 17 AND user.location.country == "US"`. Solves role explosion by encoding context as predicates rather than as new roles. Cost: policies become harder to read and audit, and the same policy logic ends up scattered across many systems if not centralized. Defined in [NIST SP 800-162](https://nvlpubs.nist.gov/nistpubs/specialpublications/NIST.SP.800-162.pdf).

- **ReBAC — Relationship-Based Access Control.** Replaces predicates with *graph relationships*. The question is no longer "what role does Alice have?" but "what is the relationship between Alice and document X, and does that relationship grant edit access?" Example: "Alice can edit document X because Alice is a member of the engineering team, the engineering team owns the engineering folder, and document X lives in the engineering folder." This is how Google Drive, GitHub, and most modern collaboration tools actually work under the hood. The canonical implementation is [Google Zanzibar (USENIX ATC 2019)](https://www.usenix.org/system/files/atc19-pang.pdf) — see below.

- **PBAC — Policy-Based Access Control.** Orthogonal to the others. PBAC is about *where the policy lives and how it is governed*: instead of access logic being scattered across application code, it lives as a versioned, reviewable artifact in a policy language (Rego for Open Policy Agent, Cedar for AWS, XACML historically). A central Policy Decision Point (PDP) evaluates the policy against each request. PBAC can encode RBAC, ABAC, or ReBAC inside it — it is about externalization, not the decision basis.

| Model | Decision basis | Best for | Failure mode |
|-------|---------------|----------|--------------|
| **ACL** | Identity → object | Filesystems, small systems | O(users × objects) explosion |
| **RBAC** | Role → permission | Stable job functions, coarse policy | Role explosion (1,300 roles at a 50k-employee EU bank — canonical NIST example) |
| **ABAC** | Attribute predicates (user, resource, env, action) | Context-dependent decisions (time, location, risk, classification) | Policy authoring complexity; scattered ABAC in code is unauditable |
| **ReBAC** | Subject↔object graph traversal | Resource-level sharing (Drive, GitHub, Jira) | Recursive policies hard to audit |
| **PBAC** | Externalized policy artifact (Rego, Cedar, XACML) | Governing the decision process itself | PDP becomes single point of failure |

NIST explicitly notes that ACL and RBAC are special cases of ABAC. Practically, every mature B2B SaaS in 2026 runs **hybrid**: RBAC for coarse policy (admin/member), ReBAC for resource sharing, ABAC for contextual edge cases, PBAC as the control plane that hosts whichever combination you use.

**Google Zanzibar — the paper to know.** Google's internal authorization system, made public in a 2019 USENIX paper. Models all permissions as **relation tuples** of the form `(object#relation@user)` — for example, `(doc:readme#editor@alice)` means "Alice has the `editor` relation on `doc:readme`." Answering "Can Alice edit document X?" becomes a graph traversal over these tuples. Powers Drive, YouTube, Calendar, Photos, and Google Cloud. The numbers are absurd: trillions of stored relations, millions of authorization checks per second, p95 latency under 10ms, availability over 99.999%. Two key technical contributions: **zookies** (opaque consistency tokens that solve the "new enemy problem" — preventing stale, revoked permissions from being applied to newly created content) and **Leopard** (a specialized index for fast traversal of nested group memberships). Open-source implementations: SpiceDB/AuthZed, OpenFGA (sponsored by Auth0/Okta), Permify, Ory Keto, Auth0 FGA, WorkOS FGA.

### 1.6 The identity protocol stack — what each protocol actually does

A working enterprise identity system uses six or seven protocols in concert. Most practitioners conflate them. Here is what each one is for, in plain terms.

- **LDAP — Lightweight Directory Access Protocol** (RFC 4511, 1993). LDAP is *not* an authentication protocol — it is a way to query and modify a directory of users, groups, and other organizational data. Think of it as a read/write API for a phone book. The classic enterprise pattern is to have an LDAP server (OpenLDAP, Active Directory's LDAP interface, etc.) holding all employee records, and applications look up users via LDAP. Authentication happens via a "simple bind" (try to log in as the user with their password) or by handing off to a real auth protocol like Kerberos.

- **Kerberos** (RFC 4120, originally MIT 1980s, now ubiquitous in Windows networks). A network authentication protocol that uses tickets and a trusted third party (the Key Distribution Center) so that users prove their identity once and then receive time-limited tickets to access other services. The model: "Alice authenticates to the KDC, the KDC gives her a ticket-granting ticket, she uses that to request service tickets for the file server, mail server, etc." Active Directory is essentially Kerberos + LDAP + DNS + replication wrapped together. Mostly invisible inside corporate networks; rarely used in modern cloud SaaS.

- **SAML 2.0 — Security Assertion Markup Language** (OASIS, 2005). An XML-based protocol for *federated single sign-on* in enterprise environments. The flow: you click "Sign in with corporate SSO" on a SaaS app (e.g. Salesforce), the SaaS app redirects you to your company's identity provider (Okta, Microsoft Entra, Ping), you authenticate there, and the IdP sends back a signed XML document (the SAML assertion) that says "this is Alice, here are her email and groups." The SaaS app trusts the signature and logs you in. SAML still dominates the Fortune 500 install base. Verbose, XML-heavy, mostly used for browser-based enterprise SSO.

- **OAuth 2.0 — Open Authorization** (RFC 6749, 2012). A *delegated authorization* protocol — not authentication, despite being widely misused for login. The model: a user authorizes a client app to access an API on their behalf, the API issues an access token to the client, the client uses that token to call the API. The classic example: "Sign in with Google" to a third-party app — Google issues a token that lets the app read your Google Calendar, but the token does not log you into Google itself. The token is what the client holds and presents; the user does not see it. OAuth 2.0 was widely misused as a login mechanism, which led to OIDC.

- **OAuth 2.1** ([draft-ietf-oauth-v2-1](https://datatracker.ietf.org/doc/draft-ietf-oauth-v2-1/), in progress). A consolidation of OAuth 2.0 plus all the security best-practice updates from the past decade, with the worst patterns removed. Specific changes from 2.0: **PKCE** (Proof Key for Code Exchange — a way to bind an auth request to the specific client that started it, preventing interception attacks) is **mandatory** for the auth code flow; the **implicit grant** (which leaked tokens in URL fragments) is **removed**; the **Resource Owner Password Credentials grant** (which had the user hand their password to the client app) is **removed**; redirect URIs must match exactly as strings (not as patterns); bearer tokens cannot be sent in URL query strings; refresh tokens must be sender-constrained or single-use. Every credible agent-authentication proposal in 2026 sits on OAuth 2.1, not 2.0.

- **OIDC — OpenID Connect** (OpenID Foundation, 2014). An *authentication* layer built on top of OAuth 2.0. Adds three things: an **ID Token** (a JWT — see below — that says "this user is Alice, authenticated at this time, by this IdP"), a `/userinfo` endpoint to fetch user profile data, and standard scopes (`openid`, `profile`, `email`). The result: OAuth 2.0 underneath lets a client get authorization to call APIs; OIDC on top lets the same flow also serve as login. Modern "Sign in with Google / Microsoft / Apple" is OIDC.

- **SCIM — System for Cross-domain Identity Management** (RFCs 7643 and 7644). A REST API for managing the *lifecycle* of user accounts across systems — creating, updating, deactivating users and groups. When HR hires a new employee, the HR system sends a SCIM `POST /Users` to Slack, GitHub, Salesforce, and 50 other apps, and each one provisions the account automatically. When the employee is terminated, the same flow sends a `DELETE` or deactivation update everywhere. SCIM is the most underrated control in the stack — broken SCIM is why ex-employees retain access for weeks. **SCIM is not SSO.** SAML/OIDC log a user in at a given moment; SCIM is what creates and removes the account in the first place.

- **JWT — JSON Web Token** (RFC 7519). A *token format*, not a protocol. A JWT is a JSON object with three parts (header, payload, signature) base64-encoded and joined with dots. The payload contains **claims** — facts about the subject like `sub` (subject), `iss` (issuer), `aud` (audience), `exp` (expiration), plus custom claims. The signature is cryptographic, so anyone with the issuer's public key can verify the JWT was not tampered with. JWTs are what OIDC ID tokens look like, what OAuth access tokens often look like (when not opaque), and what SPIFFE JWT-SVIDs are. When you see a long string like `eyJhbGciOiJIUzI1NiIs...` that's a JWT.

- **SPIFFE — Secure Production Identity Framework For Everyone** (CNCF specification). The modern open standard for *workload identity* — giving cryptographically verifiable identities to services, containers, and (now) agents, rather than to humans. A SPIFFE ID is a URI like `spiffe://example.com/ns/staging/sa/payment-service`. Each workload presents an **SVID** (SPIFFE Verifiable Identity Document, available as either an X.509 certificate or a JWT) that proves its identity to other workloads. SPIRE is the reference implementation. SPIFFE is becoming the foundation under agent identity — workload identity federation lets a Kubernetes pod or a cloud function exchange its SPIFFE SVID for a short-lived cloud IAM credential, eliminating long-lived API keys.

| Protocol | Layer | Purpose | Spec |
|---------|-------|---------|------|
| LDAP | Directory access | Query/modify identity store | RFC 4511 |
| Kerberos | Authentication | Ticket-based mutual auth in trusted networks | RFC 4120 |
| SAML 2.0 | Federation | XML assertions for enterprise SSO | OASIS 2005 |
| OAuth 2.0 | Authorization | Delegated API access | RFC 6749 |
| OAuth 2.1 | Authorization | 2.0 + BCP, PKCE mandatory, no implicit, no ROPC | [draft-ietf-oauth-v2-1](https://datatracker.ietf.org/doc/draft-ietf-oauth-v2-1/) |
| OIDC | Authentication | Identity layer on OAuth (ID Token = JWT) | OpenID 2014 |
| SCIM 2.0 | Provisioning | REST CRUD for user lifecycle | RFC 7643/7644 |
| JWT | Token format | Signed/encrypted JSON claims | RFC 7519 |
| SPIFFE | Workload identity | Platform-agnostic workload IDs | CNCF |

The mistakes practitioners get wrong, restated:

- **OAuth 2.0 is authorization, not authentication.** Using it to log users in was the misuse that motivated OIDC. If you only have an OAuth access token, you know *the user authorized something*, not *who the user is*.
- **SCIM ≠ SSO.** SAML/OIDC let a user log in to an app. SCIM creates the account in the app in the first place, and removes it when the user leaves. Most enterprises have working SAML and broken SCIM, which is why offboarding is the #1 access-control incident pattern.
- **LDAP is not an auth protocol.** It is the directory; authentication happens via simple bind, or LDAP is used as the lookup behind Kerberos in Active Directory.

### 1.7 SSO architecture — what actually happens when you click "Sign in with Okta"

**SSO — Single Sign-On.** A pattern (not a protocol) where a user authenticates once with a central identity provider and then accesses many applications without re-entering credentials. Implemented via SAML or OIDC under the hood. The two roles to know:

- **IdP — Identity Provider** (sometimes called **OP — OpenID Provider** in OIDC terminology). The system that owns the user directory and performs authentication. Okta, Microsoft Entra ID, Ping Identity, Google Workspace, Auth0. The IdP is where the user actually types their password (or scans a fingerprint, or taps a YubiKey).

- **SP — Service Provider** (sometimes called **RP — Relying Party** in OIDC terminology). The application the user is trying to use — Salesforce, Slack, Notion, an internal app. The SP does not authenticate the user itself; it trusts the IdP's signed claim.

```
┌──────────┐   1. Request    ┌──────────┐
│  User    │ ──────────────▶ │   SP     │   (Service Provider /
│ (Browser)│                 │  (App)   │    Relying Party in OIDC)
└──────────┘                 └────┬─────┘
     ▲                            │ 2. Redirect to IdP
     │                            ▼
     │  4. Assertion         ┌──────────┐
     │  / ID Token           │   IdP    │   (Identity Provider /
     └──────────────────────▶│  (Okta,  │    OpenID Provider)
                             │  Entra)  │
                             └──────────┘
                                  │ 3. Authenticate
                                  ▼   (password, MFA, biometric)
```

The flow, step by step:

1. **Request.** The user navigates to the SP (e.g. `salesforce.com`). The SP sees the user has no active session and needs to authenticate.
2. **Redirect to IdP.** The SP redirects the user's browser to the configured IdP, including a request for an authentication assertion.
3. **Authenticate.** The IdP shows its login UI, the user enters credentials (password + MFA, passkey, etc.), the IdP verifies them against its directory.
4. **Assertion / ID Token.** The IdP redirects the user's browser back to the SP, carrying a cryptographically signed message: either a SAML assertion (XML) or an OIDC ID Token (JWT). The SP verifies the signature against the IdP's public key, reads the claims (who the user is, when they authenticated, what groups they're in), and establishes a local session.

**Federation** is what happens when one organization's IdP trusts another organization's IdP — for example, a contractor at Acme can access Beta Corp's SaaS apps because Beta Corp's IdP federates to Acme's IdP. The mechanism is the same trust-by-signature model, just chained.

Per-organization SSO configuration is what makes B2B SaaS scalable: each customer org has its own IdP connection, attribute mapping, and signing key inside the SP. This is exactly what WorkOS, Auth0, and Frontegg sell — turnkey "Enterprise SSO" so a B2B SaaS startup can support 200 different customer IdPs without writing 200 integrations.

SAML still dominates the F500 install base (XML metadata exchange, ADFS, Shibboleth, Ping). OIDC dominates new integrations (discovery via `.well-known/openid-configuration`, JWKS-based key rotation, mobile-friendly with PKCE).

### 1.8 The four layers built on top of SSO — IGA, PAM, CIEM, and workload identity

SSO solves "let users log in." Real enterprises need four additional capability layers on top.

**IGA — Identity Governance and Administration.** The "manage the lifecycle and prove compliance" layer. Gartner defines IGA as "the solution to manage the identity life cycle and govern access across on-premises and cloud environments." Core capabilities:

- **Provisioning and deprovisioning.** Automated creation and removal of user accounts in connected systems, driven by HR events (hire, transfer, terminate — the "joiner-mover-leaver" or JML pattern). SCIM is the modern delivery mechanism; legacy systems still require ITSM tickets.
- **Access requests.** A self-service catalog where users request additional entitlements ("I need access to the Salesforce reports for the EMEA region"), routed through an approval workflow, then provisioned.
- **Access certifications.** Periodic reviews where managers attest that current entitlements are still justified. Required quarterly or annually by SOX, SOC 2, and ISO 27001.
- **Entitlement management.** A catalog of granular permissions with descriptions, owners, and sensitivity ratings.
- **Role management and role mining.** Discovering roles from existing access patterns and managing role lifecycle.
- **SoD enforcement.** Detective and preventive controls for separation-of-duties violations.

Vendors: SailPoint (the F500 default), Saviynt, Omada, Oracle IGA, IBM Verify Governance, One Identity Manager. The 2025–2026 next-gen disruptors (Lumos, ConductorOne, Opal, Veza, Apono) attack the "18-month deployment, multi-million dollar implementation" weakness of legacy IGA with SaaS-first, faster-time-to-value pitches.

**PAM — Privileged Access Management.** The "control the high-blast-radius accounts" layer. Aimed at admin accounts where a compromise causes catastrophic damage: root on a Linux host, domain admin in Active Directory, the AWS root account, database administrators, break-glass emergency accounts. Core capabilities:

- **Credential vault.** Tamper-proof storage with policy-based rotation. Credentials are never exposed to end users; the vault checks them in and out.
- **Session isolation and recording.** A Privileged Session Manager proxies the admin session, records video and keystrokes for forensics, and prevents the user from ever seeing the raw credential.
- **Just-in-time elevation.** Ephemeral creation of privileged sessions instead of permanent admin group membership. Hits the ZSP target.
- **Discovery.** Find all privileged accounts, keys, and secrets across on-prem, cloud, and operational technology (OT/ICS).
- **Threat detection.** Anomaly detection on session behavior.

Vendors: CyberArk (dominates regulated industries; the F500 default), BeyondTrust, Delinea (Thycotic + Centrify). The cloud-native disruptors — Teleport, StrongDM, HashiCorp Boundary — replace the bastion-host model with short-lived certificate-bound access where there are no standing credentials at all. CyberArk just sold to Palo Alto Networks for $25B in February 2026 — the largest identity-security M&A in history.

**CIEM — Cloud Infrastructure Entitlement Management.** The "make sense of cloud permissions sprawl" layer. Coined by Gartner in 2020. The problem CIEM exists to solve: AWS IAM has roughly 17,000 distinct actions; Azure RBAC has 10,000+; GCP has thousands more. The effective permission for a single AWS API call resolves through six layers of policy (identity-based policies, resource-based policies, permissions boundaries, Service Control Policies, session policies, VPC endpoint policies). No human can reason about this at scale. [Sysdig found that 98% of granted cloud permissions are unused.](https://sysdig.com/solutions/permissions-entitlement-management)

Core CIEM capabilities:

- **Rightsizing.** Compare actual usage (from CloudTrail, GCP Audit Logs, Azure Activity Logs) against granted permissions, and recommend least-privilege policies.
- **Anomaly detection.** Flag unusual behavior — a service account suddenly calling unfamiliar APIs, or a developer assuming a production role at 3am.
- **Visualization.** Graph who can access what across multi-cloud environments.
- **Compliance reporting.** Map entitlements to control frameworks.

CIEM as a standalone category is now mostly subsumed into **CNAPP — Cloud-Native Application Protection Platform** (Wiz, Tenable, CrowdStrike, Palo Alto). Standalone CIEM startups have been culled; the category resolved upward into broader cloud security.

**Workload identity / non-human identity (NHI).** The "give cryptographic identity to services and agents" layer. The fastest-growing identity category. Service accounts, IAM roles, API keys, bots, CI/CD pipelines, and AI agents — collectively called **non-human identities** — now outnumber human identities by 30:1 to 100:1 depending on whose stats you trust.

The legacy answer for workload identity was static credentials: a `service-account.json` key file, an AWS access key, a Salesforce integration user with a password. These leak constantly. The modern answer is **workload identity federation**: workloads prove their identity through their runtime attestation (where they are running, in which cluster, under which service account) and exchange that for short-lived credentials.

- **SPIFFE** — the open standard. A SPIFFE ID is a URI like `spiffe://acme.com/payment-service`. The workload presents an SVID — a SPIFFE Verifiable Identity Document, either an X.509 cert or a JWT — proving its identity. SPIRE is the open-source reference implementation. Adopted by HPE, Bloomberg, Pinterest, Uber.
- **AWS IRSA** — IAM Roles for Service Accounts. A Kubernetes pod with a service account can assume an AWS IAM role through OIDC token exchange, with no static AWS keys anywhere.
- **GCP Workload Identity Federation** — lets external workloads (AWS, Azure, on-prem AD, GitHub Actions, any OIDC/SAML IdP) exchange native credentials for short-lived GCP access tokens.
- **Azure Federated Identity Credentials** — the same pattern for Azure resources.

This federation layer — short-lived OIDC token exchange replacing long-lived service-account keys — is the substrate the agent-identity drafts now sit on. When IETF drafts talk about "the agent's workload identity," they mean SPIFFE-style attestation. When they talk about "the user-on-behalf-of claim on top," they mean a SAML-or-OIDC user identity bound to that workload identity via OAuth token exchange (RFC 8693). The whole agent-auth architecture is a recombination of these existing primitives — which is why §3.1 frames most of "agent identity" as rebranded IAM.

### 1.9 Compliance — what's actually required for access control

Every framework requires some flavor of: least privilege, RBAC, unique user IDs, session timeout, access logging, privileged access restrictions, MFA. The actual delta:

| Framework | Type | Access-control requirement |
|-----------|------|---------------------------|
| **SOC 2** | AICPA attestation | CC6.1: logical access controls, RBAC, provisioning/deprovisioning, MFA, periodic review |
| **ISO/IEC 27001** | Certification | Annex A.5.15, A.5.16, A.5.18, A.8.2 |
| **HIPAA Security Rule** | US regulation | §164.312(a) unique IDs, auto-logoff, emergency access; §164.312(b) audit controls |
| **SOX** | US public-co regulation | SoD on financial systems; ITGCs covering provisioning, review, deprovisioning |
| **PCI-DSS v4.0** | Industry standard | Reqs 7 (need-to-know), 8 (unique IDs + MFA), 10 (audit trails) — most prescriptive |
| **GDPR** | EU regulation | Art. 5 purpose limitation, Art. 32 security by need; breach notification 72h |
| **FedRAMP / NIST 800-53** | US federal | AC family (AC-2, AC-3, AC-5, AC-6, AC-17) |
| **ISO/IEC 42001** | New (2024) | AI management system certification — the new gate |

Roughly 60–70% of controls overlap between SOC 2, ISO 27001, and GDPR, which is why GRC platforms (Vanta, Drata, Secureframe) sell "implement once, certify many." Note **ISO 42001** (AI management) as the new emerging gate for AI vendors — Cresta got it first in contact-center AI in January 2025.

### 1.10 The ten failure modes that fund the next-gen IGA market

1. **Role explosion** — 1,300 roles at a 50k-employee EU bank is the canonical example.
2. **Privilege creep** — "temporary" admin grants that become permanent.
3. **Stale entitlements / orphaned accounts** — ex-employees and decommissioned service accounts.
4. **Shadow IT** — 61% of SaaS apps qualify as shadow IT in 2026 ([Torii benchmark](https://torii.com)).
5. **Rubber-stamp access reviews** — mass approvals within minutes of campaign launch.
6. **The new-enemy problem** — revoked users still see content modified after revocation (Zanzibar's zookies solve this).
7. **Cloud permissions explosion** — 40,000+ IAM policies common in a single AWS org.
8. **Service account key sprawl** — long-lived static credentials in source control.
9. **Mover gap** — role changes leave behind old access (the weakest link in JML automation).
10. **Additive-only culture** — granting is fast and rewarded; revoking causes outages and is punished.

Every line in the next-gen IGA pitch deck attacks one of these.

---

## Part II — How Enterprises Actually Handle IAM Today

### 2.1 The shape of the market

```
┌────────────────────────────────────────────────────────────────────┐
│                   ENTERPRISE IDENTITY STACK (2026)                  │
├──────────────────────────────────────────────────────────────────────┤
│ WORKFORCE IAM / SSO    │   CUSTOMER IAM (CIAM)                       │
│ Okta, Entra ID, Ping,  │   Auth0, Entra External ID, WorkOS,         │
│ OneLogin, JumpCloud,   │   Descope, Stytch (→ Twilio), Frontegg,     │
│ GWS Identity           │   Clerk, Ping (ForgeRock)                   │
├──────────────────────────────────────────────────────────────────────┤
│ IGA (legacy)           │   NEXT-GEN IGA / ACCESS GOV                 │
│ SailPoint, Saviynt,    │   Lumos, ConductorOne, Opal, Veza,          │
│ Omada, Oracle, IBM,    │   Apono, Andromeda, Zluri                   │
│ One Identity Manager   │                                             │
├──────────────────────────────────────────────────────────────────────┤
│ PAM (legacy)           │   MODERN INFRA ACCESS                       │
│ CyberArk (PANW),       │   Teleport, StrongDM,                       │
│ BeyondTrust, Delinea   │   HashiCorp Boundary, Akeyless              │
├──────────────────────────────────────────────────────────────────────┤
│ CIEM (now CNAPP)       │   APP AUTHZ ENGINES                         │
│ Wiz, Tenable, Sonrai,  │   OpenFGA, Cerbos, Permit.io, Oso,          │
│ Permiso, CrowdStrike   │   AuthZed/SpiceDB, AWS Verified Permissions │
├──────────────────────────────────────────────────────────────────────┤
│ NHI / WORKLOAD/AGENTS  │   IDENTITY ORCH / FABRIC                    │
│ Astrix, Oasis, Entro,  │   Strata, Aembit, SGNL (CrowdStrike),       │
│ Token, P0, Aembit      │   Otterize (Cyera)                          │
├──────────────────────────────────────────────────────────────────────┤
│ SHADOW SAAS            │   SYSTEM-NATIVE RBAC                        │
│ Cerby, Grip, Nudge,    │   AWS IAM, Azure RBAC, GCP IAM,             │
│ Reco, Wing             │   Databricks Unity Catalog, Snowflake RBAC, │
│                        │   Salesforce Profiles, GitHub, Workday      │
└────────────────────────────────────────────────────────────────────────┘
```

### 2.2 The two gravity wells: Microsoft Entra vs Okta

Microsoft Entra ID and Okta together command roughly 30–40% of workforce-identity mindshare. Microsoft wins on **bundling** (Entra ID P1/P2 included in M365 E3/E5; the new E7 SKU at $99 PUPM bundles E5 + Copilot + Agent 365 + Entra Suite). Okta wins on **integration breadth** (19,000+ OIN connectors) and on being the only credible vendor-neutral choice.

**Okta's vulnerability is real.** TTM revenue $2.84B, subscription growth +18% YoY, but cRPO growth has decelerated to 12% — the leading indicator. GAAP operating margin -10%. The 2023 support-system breach still surfaces in F500 RFP security reviews. Microsoft bundling is an existential threat anywhere the customer is M365-heavy. Auth0 integration synergies haven't materialized.

**Microsoft Entra's weakness is product polish, not economics.** Gartner Peer reviews flag Group Management as "half-baked," MFA database limitations, inconsistent multi-tenant behavior. Directions on Microsoft estimates 20–30% of E5/P2-licensed users actually deploy what they're licensed for. Shelfware is the long-term tax. Outside Microsoft workloads, depth drops fast.

### 2.3 Private equity has consolidated the legacy second tier

- **Palo Alto Networks ← CyberArk** ($25B, closed Feb 11, 2026) — largest identity-security deal in history.
- **Thoma Bravo ← SailPoint** ($6.9B, 2022; re-IPO'd Feb 2025).
- **Thoma Bravo ← Ping Identity** ($2.8B, 2022).
- **Thoma Bravo ← ForgeRock** ($2.3B, 2023; merged into Ping).
- **One Identity ← OneLogin**.
- **Okta ← Auth0** ($6.5B, 2021).

The independent pure-play identity vendor is going extinct above the $500M revenue line. This is a structurally important fact for any new entrant: by the time you cross $500M ARR, you are either acquired or you have already become a public security platform.

### 2.4 The next-gen IGA disruption is real

Wedge: "Legacy IGA takes 18 months to deploy and costs millions. We do it in weeks for the SaaS-heavy parts of your stack."

- **Lumos** — $65M total, 7x faster / 80% lower TCO claim. SaaS-first. Strong for mid-market and tech-forward enterprises; thin on regulated/on-prem.
- **ConductorOne** — Cloud-native IGA with on-prem connectors, JIT, Slack/Teams/CLI UX, Terraform provider. Transparent pricing ($9–11 PUPM by tier). Closed-loop control plane.
- **Opal Security** — $33.8M total, $1.3M revenue, 17% headcount drop YoY. Developer-native; in danger of being consolidated.
- **Veza** — $108M Series D at $808M valuation (Apr 2025). Access Graph across IdP/SaaS/cloud/data. Strategic investors include Snowflake, Workday, Atlassian — suggests acquisition path.

### 2.5 The dirty secret: spreadsheets and Jira tickets

The actual state of enterprise access management in 2026, behind the $24B+ market:

- **830 apps avg per enterprise** ([Torii 2026](https://torii.com)). Large enterprises (5,000+) avg **2,191 apps**.
- **61.3% of apps are shadow IT.** Only 15.5% formally sanctioned.
- **85% of SaaS apps are unknown and unmanaged.** 91% of AI tools are unmanaged ([Grip Security 2025](https://gripsecurity.com)).
- **61% of provisioned SaaS apps are inactive but still paid.** 73% of provisioned users don't use the app ([Torii 2025](https://torii.com)).
- **70% of SaaS spend** is by lines of business, not IT ([Zylo 2025](https://zylo.com)).
- **NHIs outnumber humans 30:1 to 100:1** depending on whom you ask.
- **Access requests are filed in Jira/ServiceNow/Slack,** approved by managers who have no idea what the access does, provisioned manually.
- **Access reviews are quarterly Excel spreadsheets.** Mass approvals within minutes of launch are the norm.
- **88% of basic web app attacks use stolen credentials** ([Verizon DBIR 2025](https://verizon.com/dbir)).

When a CISO buys Okta + SailPoint + CyberArk + Wiz + Lumos + Astrix + Cerby, they are still not covering the majority of the access surface area. The "managed" stack is the tip; 60%+ is unmanaged and growing as AI tools proliferate.

### 2.6 The "last mile" gap — SSO ≠ RBAC

This is the misunderstood gap that funds everything in next-gen IGA, and it is exactly the gap an AI-agent access plane sits in.

```
        Okta / Entra (IdP)
              │
              ▼ SSO + SCIM
   ┌──────────────────────────┐
   │   Salesforce             │ → Internal: 50+ profiles, 200+ permission sets,
   │                          │   sharing rules, field-level security
   │                          │   (IdP has zero visibility into any of this)
   ├──────────────────────────┤
   │   Snowflake              │ → warehouse/db/schema/table grants, masking
   ├──────────────────────────┤
   │   AWS Identity Center    │ → 30K+ IAM perms, SCPs, resource policies,
   │                          │   session policies, ABAC tags
   ├──────────────────────────┤
   │   GitHub                 │ → org/team/repo/branch/CODEOWNERS
   ├──────────────────────────┤
   │   Workday                │ → security groups, domains, business processes
   └──────────────────────────┘
```

The IdP authenticates and provisions a coarse role. Inside each system, the *actual meaningful* permission decisions are made — and the IdP cannot see them, cannot revoke them, cannot certify them. Veza, SailPoint, Saviynt, ConductorOne, Lumos, and Cerby all attack different angles of this gap. **None has solved it fully.** This is the next $5–10B opportunity in IAM — and the structural reason an "agent access plane" lands.

### 2.7 The winners and losers, opinionated

**Strongest position right now.** Microsoft Entra ID (bundling), CyberArk/PANW (depth + distribution), SailPoint (F500 lock-in), WorkOS (AI-first B2B SaaS mindshare), Wiz (CIEM-as-CNAPP).

**Most vulnerable.** Okta (sandwich attack), Auth0 (losing devs to WorkOS/Clerk/Stytch), Saviynt (demo-vs-production reputation problem is the most damning in this entire research), Delinea (squeezed between Teleport/StrongDM and CyberArk), Ping/ForgeRock (Thoma Bravo extraction mode).

**Most over-valued.** Veza at $808M with small ARR. Opal at $33M raised on $1.3M revenue.

**Best risk/reward.** Oasis Security for NHI, Cerby for shadow SaaS, ConductorOne for next-gen IGA.

---

## Part III — The AI Age Breaks the IAM Stack

### 3.1 What's actually new

Most of what is being sold as "agent identity" is rebranded IAM: OAuth 2.1 + Token Exchange (RFC 8693) + Resource Indicators (RFC 8707) + SCIM + a gateway. The genuinely new parts are smaller than the marketing implies. The genuinely new parts are:

1. **CIMD replacing DCR.** Client ID Metadata Documents solve the "arbitrary client wants to talk to arbitrary server" problem in a way DCR couldn't. Bluesky pioneered this; MCP adopted it Nov 2025.
2. **RFC 8707 audience binding becoming MUST.** The RFC existed since 2020; mandating it and policing it is the new part.
3. **The `act` claim chain.** RFC 8693 supports nested `act`, but the IETF AI-agent drafts are the first time it's the explicit model for "agent A delegated to agent B which called API foo."
4. **Blended identity** (Aembit's framing). A single policy decision evaluating user identity AND workload identity together.
5. **Cryptographic agent identity via system-prompt+tools+config checksum** ([Goswami draft](https://datatracker.ietf.org/doc/html/draft-goswami-agentic-jwt-00)). Whether it survives contact with reality is another matter.
6. **Shadow MCP detection at the network layer** (Cloudflare).
7. **SCIM `/Agents` resource type** ([WorkOS / OpenID Foundation draft](https://workos.com/blog/scim-agents-agentic-applications)).
8. **Tool poisoning / rug-pull / schema injection** — a new attack class because no other protocol lets a server retroactively change tool definitions mid-session.

### 3.2 The MCP authorization spec — what it actually says

[The current MCP spec (2025-11-25 revision)](https://modelcontextprotocol.io/specification/draft/basic/authorization.md) splits two OAuth roles:

- **MCP Server = OAuth 2.1 Resource Server.** Validates tokens, validates audience, rejects passthrough.
- **Authorization Server = separate component.** Can be co-hosted but the spec strongly prefers external IdP.

| Component | RFC | MCP Requirement |
|-----------|-----|-----------------|
| OAuth 2.1 (PKCE, no implicit, no ROPC) | draft-ietf-oauth-v2-1 | MUST |
| Authorization Server Metadata | RFC 8414 | MUST |
| Protected Resource Metadata | RFC 9728 | MUST |
| Resource Indicators (audience binding) | RFC 8707 | **MUST since 2025-06-18** |
| Dynamic Client Registration | RFC 7591 | MAY (downgraded from SHOULD Nov 2025) |
| Client ID Metadata Documents | draft-ietf-oauth-cimd | **SHOULD as of Nov 2025** |

**The flow.** Client hits server → 401 with `WWW-Authenticate: Bearer resource_metadata="..."` → client fetches `/.well-known/oauth-protected-resource` → discovers AS → fetches `/.well-known/oauth-authorization-server` → registers (CIMD/DCR/pre-reg) → auth code + PKCE → token with `aud` matching the MCP server → resource request.

**The DCR fiasco.** The original spec made DCR a SHOULD. In practice DCR was a disaster — unbounded database growth, no revocation story, denial-of-service vector, per-instance client_id proliferation. [Aaron Parecki](https://aaronparecki.com/2025/11/25/1/mcp-authorization-spec-update): "DCR has been a massive barrier to enterprise adoption of MCP." The Nov 2025 spec replaces it with CIMD.

**The RFC 8707 IdP gap (Q1 2026).** This is the most operationally important table in this report:

| Provider | RFC 8707 | DCR | MCP Compliance |
|----------|----------|-----|----------------|
| PingFederate 12.1+ | Yes | Yes | Fully compliant |
| Keycloak | Custom mapper | Yes | Partial |
| Amazon Cognito | Yes | No | Partial |
| Auth0 | Non-standard `audience` | Partial | Incompatible |
| Okta | No | Partial | Incompatible |
| Microsoft Entra ID | Proprietary syntax | No | Incompatible |

In other words, **the IdPs every enterprise has bought are not yet MCP-compliant.** Most enterprise MCP deployments today either run a proxy that synthesizes `aud` claims or live with the audience-binding weakness. This is a real wedge for any vendor that lands a compliant MCP AS in front of an enterprise's existing IdP.

### 3.3 The six ways agents authenticate (badly) today

1. **Personal Access Tokens.** Still dominant for developer tools. Long-lived, broad-scoped, stored in `~/.claude.json`, `.env`, environment variables. [Cyata's analysis of 5,200+ open-source MCP servers found 24,008 unique embedded secrets.](https://policylayer.com/attacks/credential-leak-via-errors) 53% of MCP servers rely on long-lived static credentials.
2. **OAuth on-behalf-of (classic).** Works fine when there's a human at the keyboard. Breaks when agents run unattended, make autonomous decisions, or cross multiple resource servers.
3. **Service accounts with long-lived credentials.** The pattern behind the Okta, Cloudflare, Snowflake, and Microsoft Midnight Blizzard breaches.
4. **Workload identity federation.** SPIFFE/SPIRE, AWS IRSA, GCP Workload Identity, Azure Federated Identity Credentials. Modern but solves "what workload" not "for which user."
5. **Pass-through user identity (impersonation).** "Agent becomes user." Works for mechanical tool-agents.
6. **Agent-as-its-own-identity (delegation).** "Agent has its own identity and acts on user's behalf." Required as autonomy increases.

The architectural debate (impersonation vs delegation) is converging on **both**, via the `act` claim model — `sub`=user, `act.sub`=agent. Microsoft Entra Agent ID ships this in production with proprietary claims (`xms_act_fct`, `xms_idrel`). Vendor-neutral version: [draft-oauth-ai-agents-on-behalf-of-user](https://www.ietf.org/id/draft-oauth-ai-agents-on-behalf-of-user-00.html).

### 3.4 The NHI explosion — real but a junk metric

The numbers, all defensible:

- **45:1** NHI-to-human — [CSA + Astrix RSAC 2025](https://cloudsecurityalliance.org/artifacts/securing-non-human-identities-in-the-age-of-ai-agents-rsac-2025).
- **96:1** in financial services — [CyberArk Oct 2025](https://www.cyberark.com/resources/blog/96-machines-per-human-the-financial-sectors-agentic-ai-identity-crisis).
- **20:1–50:1** in hybrid envs — [Silverfort 2025](https://resources.silverfort.com/insecurity-in-the-shadows/the-volume-of-nhis-is-growing-fast).
- **Up to 100:1** — GitGuardian/Entro.

The honest critique from Cyber Strategy Institute: these ratios are not directly comparable because different orgs count radically different things as NHIs (workload identities? IAM roles? SSH keys? OAuth apps? bot accounts?). They convey scale, not risk. **Blast-radius density** is the better metric, but the marketing-friendly 45:1 ratio has stuck.

What is real and important: only 19% of orgs have automated NHI offboarding. 58% try to use general IAM for NHIs, 54% PAM, 36% secrets managers — none designed for NHI lifecycle. 45% cite lack of credential rotation as the top NHI incident cause. 38% have no visibility into OAuth third-party apps.

### 3.5 The four governance problems specific to agents

1. **The confused deputy.** [MCPBlog](https://mcpblog.dev/blog/2026-03-10-confused-deputy-mcp-auth): "When an MCP server receives a tool call, it faces a question it cannot answer: was the calling agent actually authorized to use these credentials?" Three flavors: (a) MCP server holding broad credentials and acting on user requests without carrying user identity through — the Asana cross-tenant June 2025 incident; (b) token confusion — token for Server X replayed at Server Y because Y doesn't check `aud` — RFC 8707 fixes it; (c) DCR confused deputy — attacker registers a client via proxy DCR, uses proxy's trusted static client_id.
2. **Prompt injection as authorization bypass.** Tool-level RBAC does not catch this. Audience binding does not catch this. The agent has valid scope; the user approved the session; the tool is in the allowlist; the injection lives in fetched content. The only real defenses are (a) per-session scoping, (b) content-safety filters on tool results before they reach the model, (c) reader/writer MCP server separation.
3. **Token theft.** The Mitiga May 2026 Claude Code MitM disclosure: malicious npm postinstall rewrites `~/.claude.json` to route MCP server URLs through an attacker proxy. Token rotation does not help — next refresh hits the proxy again.
4. **Audit trail confusion.** Most logging infra was designed around a single principal. Cerbos and Aembit both make dual attribution a marketing point ("who, what agent, which resource, policy outcome") because no one else does it natively.

### 3.6 The incident tape (2025–2026)

This is the most damning artifact in this entire research. The pattern is consistent: long-lived broad-scoped credentials + a prompt-injection sink + missing audience checks. Almost none are protocol bugs; they are architectural defaults of "give the agent the user's PAT and hope."

| Date | Incident | Class |
|------|----------|-------|
| Apr 2025 | WhatsApp MCP exfiltration | Malicious MCP server, full message history exfil |
| May 2025 | GitHub MCP / Invariant Labs | Prompt injection via public issue + over-scoped PAT → private repo exfil into public PR |
| Jun 2025 | Asana MCP cross-tenant leak | Service-account confused deputy |
| Jun/Oct 2025 | Smithery.ai / GitGuardian | Path traversal → fly.io token theft → 3,000+ hosted MCP servers exposed |
| Jul 2025 | Supabase MCP / Cursor | Service-role key + prompt injection via support ticket → `integration_tokens` table dumped |
| Sep 2025 | postmark-mcp v1.0.16 | Supply chain — silent BCC of all email to attacker |
| 2025 | CVE-2025-49596 Anthropic MCP Inspector | RCE on dev machine, credential harvest |
| 2025 | CVE-2025-59536 / CVE-2026-21852 Claude Code | Malicious project config → RCE + token theft |
| Feb 2026 | ContextCrush / Context7 (50K stars, 8M dl) | Custom Rules injection → .env exfil |
| Apr 2026 | Splunk MCP CVE-2026-20205 | Clear-text tokens in `_internal` index, CVSS 7.2 |
| May 2026 | Claude Code MitM (Mitiga) | npm postinstall rewrites `~/.claude.json` |
| Ongoing | Trend Micro probe | 492 internet-exposed MCP servers with no auth or encryption |

[Bloomberry analysis of 1,400 dedicated MCP servers](https://bloomberry.com/blog/we-analyzed-1400-mcp-servers-heres-what-we-learned/): **38.7% require no authentication.** 92% of analyzed servers are rated high-risk.

### 3.7 MCP adoption is genuinely huge

- **10,000+ public MCP servers** (Anthropic, Dec 2025).
- **97M monthly SDK downloads** (Mar 2026). Trajectory: 2M → 22M → 45M → 68M → 97M from Nov 2024 to Mar 2026.
- **28% of Fortune 500** deployed MCP in production by early 2026. Fintech 45%, healthcare 32%, e-commerce 27%.
- **232% server growth in 6 months** (Aug 2025 → Feb 2026).
- **Linux Foundation Agentic AI Foundation (AAIF)** formed Dec 2025. Platinum: AWS, Google, Microsoft, OpenAI, Bloomberg, Cloudflare. This killed the "MCP is an Anthropic protocol" framing.
- **Gartner**: 75% of API gateway vendors will have MCP features by end of 2026. 40% of agentic AI projects will be canceled by end of 2027.

MCP standardized roughly 2-3x faster than OAuth 2.0 (2012→2015) or SAML (2005→2010). 18 months from announcement to multi-stakeholder governance. This is the single most important velocity number in this report.

### 3.8 The MCP gateway pattern — what enterprises actually buy

```
┌─────────────┐    ┌──────────────────────┐    ┌──────────────┐
│  Agents     │───▶│   MCP Gateway        │───▶│  MCP Servers │
│  (Claude,   │    │                      │    │  (Slack, GH, │
│  Cursor,    │    │ • Auth (OAuth/IdP)   │    │  internal,   │
│  Cline,     │    │ • Rate limit         │    │  Postgres,   │
│  ChatGPT,   │    │ • Audit logs         │    │  S3, etc.)   │
│  Cowork)    │    │ • Tool catalog       │    │              │
│             │    │ • RBAC per tool      │    │              │
│             │    │ • Token vault        │    │              │
│             │    │ • DLP scanning       │    │              │
└─────────────┘    └──────────────────────┘    └──────────────┘
```

Every enterprise that builds a serious agent practice ends up with a gateway. Why:

1. **SSO/SCIM federation.** No enterprise lets an agent platform run its own user directory.
2. **Per-user OAuth lifecycle.** Tokens must be per-user, not per-agent. Aembit's blended identity is this with policy.
3. **Action-level RBAC.** Engineering can `github:create_pr`. Marketing can't. Team Leads only for `github:delete_repo`.
4. **Audit trail.** SOC 2 / HIPAA tablestakes.
5. **Tool catalog.** Versioning, deprecation, discovery. Cloudflare's MCP Server Portals aggregate 13 internal servers exposing 182 tools as one endpoint.
6. **Context bloat control.** Apideck found 3 MCP servers + ~40 tools consumed 143K of 200K context tokens before the first user query.
7. **Shadow MCP detection.** Hostname patterns on `mcp.*`, URI patterns on `/mcp` and `/mcp/sse`, JSON-RPC method inspection.
8. **DLP at the gateway.**

This is the **session layer for agent-tool interactions**. Owning it means owning the choke point.

### 3.9 The agent identity vendor landscape

| Layer | What | Vendors |
|-------|------|---------|
| Workload identity / NHI primitives | "Who is this thing?" | Aembit, SPIFFE/SPIRE, Astrix, Token, Oasis, Entro, Clutch, Silverfort |
| Agent identity providers | OAuth + new draft specs | Descope Agentic Identity Hub, WorkOS AuthKit for MCP, Microsoft Entra Agent ID, Vouched MCP-I (DIF) |
| MCP gateways / OAuth brokers | The session layer enterprises buy | Arcade.dev, Composio, Pomerium, Cloudflare Access for MCP, Solo.io AgentGateway (LF), Gram/Speakeasy, TrueFoundry, Docker MCP Gateway, Pipedream Connect, Stainless |
| Authorization (PDP) | Policy decisions | Cerbos, OpenFGA, OPA, Permit.io, Aserto, Styra, AWS Verified Permissions (Cedar) |
| Just-in-time / privileged | Time-bound elevation | Granted.dev / Common Fate, HashiCorp Boundary |

The IETF has a small forest of drafts in the past 12 months. The serious ones to track: [draft-oauth-ai-agents-on-behalf-of-user](https://www.ietf.org/id/draft-oauth-ai-agents-on-behalf-of-user-00.html), [draft-rosenberg-oauth-aauth](https://www.ietf.org/archive/id/draft-rosenberg-oauth-aauth-01.html), [draft-ietf-oauth-identity-assertion-authz-grant](https://www.ietf.org/archive/id/draft-ietf-oauth-identity-assertion-authz-grant-00.txt) (WG-adopted; the path for enterprise SSO → MCP token issuance), and OpenID Foundation's SCIM-for-Agents. OWASP MCP Top 10 (beta 2026) lists "Token Mismanagement and Secret Exposure" as #1.

---

## Part IV — The Competitive Landscape for an "Agent Access Layer"

### 4.1 The encirclement is real and recent

The most important fact in this entire research:

- **Microsoft Entra Agent ID** — GA May 2026. First-class agent identities as Entra service principals. Agent identity blueprints, federated identity credentials, Conditional Access policies specifically for agents (autonomous + OBO templates), sponsor lifecycle workflows, convergence with Agent 365 registry, sidecar federation for non-Microsoft agents.
- **Okta for AI Agents** — GA April 30, 2026. Universal Directory for agents (human + non-human in one fabric). Prebuilt integrations with Salesforce Agentforce, Bedrock AgentCore, ServiceNow AI Platform. Shadow AI agent discovery via managed Chrome OAuth grant monitoring. **"Universal Logout"** — instant token revocation across all systems. Cross App Access protocol. Auth0 SDK side for developer build motion.
- **AWS Bedrock AgentCore Gateway + Verified Permissions** — GA Oct 13, 2025, in 9 regions. Cedar policy language (open-source). Natural-language policy authoring. Fine-grained authz at the tool boundary.
- **Palo Alto + CyberArk** — Closed Feb 2026, $25B. CyberArk's machine identity + Conjur + Cloud Entitlements Manager folded into Strata/Cortex.
- **CrowdStrike ← SGNL** — $627.9M, Jan 2026. Dynamic real-time access orchestration.
- **Cisco ← Astrix (rumored)** — $250–350M in talks as of April 2026.

The greenfield "agent identity" window — the period where a startup could build a standalone product and not be encircled — is structurally closing within 12 to 18 months. Pure NHI-discovery plays will either be acquired or absorbed into security platforms.

### 4.2 But "agent identity" is not the same as "agent operating system"

This is the strategic insight the user has correctly identified. Microsoft, Okta, AWS, and Palo Alto will own **agent identity primitives** (issuance, federation, basic policy, audit). What they will *not* own — because their architectures don't reach that far up the stack — is:

- The **ontology** of what agents do, on which business objects, under which conditions, for which business processes.
- The **operational application layer** (Workshop-equivalent) where business users actually compose agent-powered workflows.
- The **policy decision plane** above the gateway that does ABAC/ReBAC/PBAC reasoning with business-domain context.
- The **cross-customer policy network effect** ("98% of finance teams with Salesforce write access also have these 3 tools enabled").
- The **vertical-specific compliance posture** (HIPAA + ISO 42001 + state-specific data residency + sector regulations).

Microsoft will sell "Entra Agent ID + Copilot Studio + Agent 365." That stack is workflow-shaped, not ontology-shaped. Okta will sell "Universal Directory + Cross App Access." That stack is identity-shaped, not operational-shaped. **Neither is a Foundry.** Both have a credible 12–18 month head start on the access-control primitives; neither has shipped the higher-order operating system.

### 4.3 The MCP-specific competitive geometry

The MCP gateway category is the fastest-commoditizing layer in this entire stack. By end of 2026, expect:

- AWS AgentCore Gateway, Microsoft Foundry MCP Server, Google Cloud's MCP plays all bundled free with their respective clouds.
- Cloudflare Access for MCP fully productized; effectively free for Cloudflare-shop customers.
- 75% of API gateway vendors (Kong, Apigee, F5, Akamai) shipping MCP features (Gartner).
- Portkey, TrueFoundry, LiteLLM, Composio, Arcade all converging on the same feature set.

The take-rate on a pure MCP gateway is going to be very thin. **The wedge is the gateway; the moat is the policy/ontology layer above it.**

---

## Part V — Palantir Foundry, Honestly Read

### 5.1 What Foundry actually is

Foundry is not a data warehouse. It is closer to an **enterprise operating system** — vertically integrated data integration + semantic ontology + operational applications + (now) an LLM/agent platform on top.

```
┌────────────────────────────────────────────────────────────┐
│  AIP — generative AI platform                              │
│  (k-LLM access, Agent Studio, AIP Logic, Evals, Analyst)   │
├────────────────────────────────────────────────────────────┤
│  Foundry — data ops + Ontology + applications              │
│  (Pipeline Builder, Code Workbook, Workshop, Slate,        │
│   Quiver, Vertex, Object Views, Actions, Functions)        │
├────────────────────────────────────────────────────────────┤
│  Apollo — continuous delivery / infra orchestration        │
│  (thousands of zero-downtime upgrades, on-prem to cloud)   │
└────────────────────────────────────────────────────────────┘
```

### 5.2 The Ontology — the crown jewel

| Dataset world | Ontology world |
|---------------|----------------|
| Dataset | Object type |
| Row | Object instance |
| Column | Property |
| Join | Link type |
| (none — implicit) | **Action type (verbs)** |
| (none — implicit) | **Function (typed logic)** |
| (none — implicit) | **Interface (polymorphism)** |

The Ontology is fundamentally different from a semantic layer (dbt semantic, Cube, LookML, Fabric semantic models) because it includes **typed mutations** (Action types — transactional, side-effect aware, writeback datasets), **functions** (typed code in TS/Python/Java available as tools to agents), **interfaces** (object-type polymorphism), and **security-as-data** (markings as object properties, mandatory control properties).

It is a four-fold integration of **data + logic + action + security** sitting on top of the data lake. Once an enterprise models its operations as a few hundred object types with thousands of links and actions, that schema *is* the company's operating model. Migrating is not a tooling exercise; it is organizational re-architecture.

### 5.3 The underrated piece: Foundry's access control model

This is the most under-discussed part of Foundry's moat. Defense heritage left Palantir with the most sophisticated commercial access control system in any data platform.

```
┌──────────────────────────────────────────────────────────────┐
│ Discretionary controls (role-based, granted by data owners)  │
│   - Viewer / Editor / Owner roles on Projects, resources     │
├──────────────────────────────────────────────────────────────┤
│ Mandatory controls (centrally managed, propagate via lineage)│
│   - Markings (PII, PHI) — conjunctive AND                    │
│   - Classifications (SECRET, FVEY) — can be disjunctive OR   │
│   - Organizations — silo membership                          │
├──────────────────────────────────────────────────────────────┤
│ Lineage-aware propagation                                    │
│   - Markings inherited through data lineage + file hierarchy │
│   - `stop_propagating` / `stop_requiring` syntax             │
│   - Simulation mode for impact preview                       │
├──────────────────────────────────────────────────────────────┤
│ Ontology-level controls                                      │
│   - Object security policies (row-level)                     │
│   - Property security policies (cell-level)                  │
│   - Mandatory control properties (markings as object props)  │
├──────────────────────────────────────────────────────────────┤
│ Containers                                                   │
│   - Spaces (one ontology) > Projects > Folders > files       │
└──────────────────────────────────────────────────────────────┘
```

The load-bearing innovation: **lineage-aware permissions.** If you mark `raw/passengers` as PII, every downstream derived dataset inherits it automatically. To drop the marking, you need explicit `stop_propagating` on a protected branch via reviewed code. No commercial SaaS has anything close to this.

| Capability | Typical SaaS | Snowflake/BigQuery | Foundry |
|------------|--------------|--------------------|----|
| Roles | Yes | Yes | Yes |
| Row-level security | Sometimes | Yes (RLS) | Yes (OSP) |
| Cell/column masking | Rare | Yes | Yes (PSP) |
| Mandatory controls separate from sharing | No | No | **Yes (markings)** |
| Permissions propagate via data lineage | No | No | **Yes — unique** |
| Multi-level classification | No | Limited | **Yes** |
| Purpose-based / scoped sessions | No | No | **Yes** |
| Permission preview/simulation | No | No | **Yes** |
| Cross-system enforcement (incl. agents) | Federated only | Limited | **Markings traverse pipelines, Ontology, Actions, agent tools** |

The cross-system piece matters in the AI era: an LLM agent invoking a tool to write back into the Ontology is constrained by the **invoking user's full permission posture, including markings inherited via lineage**. There is no escape hatch through the agent. This is what Palantir means when it claims AIP runs on "the same rigorous security model."

### 5.4 The numbers (FY2025)

- **Total revenue:** $4.475B (+56% YoY)
- **US commercial:** $1.465B (+109% YoY); Q4 alone +137% YoY
- **US government:** $1.855B (+55% YoY)
- **Customer count:** 954 total (vs 711 prior); US commercial = 571 (+49% YoY)
- **Top 20 customer avg TTM revenue:** $93.9M (vs $64.6M prior)
- **Rule of 40:** 127% in Q4
- **FY2026 guidance:** $7.18–7.20B (+61% YoY)
- **Gross margin:** ~80% maintained despite heavy FDE deployment
- **S&M expense:** dropped from **62.6% of revenue in 2020 → 24.3% in 2025**

The S&M curve is the proof point that FDE is not disguised consulting. FDE-led discovery feeds platform abstractions back into product; subsequent customers consume those abstractions without proportional services lift.

### 5.5 Why "built today, would look different"

| Current Foundry design | An AI-native re-imagining |
|------------------------|---------------------------|
| Deterministic, rigorously typed Ontology authored by humans | **Typed core + LLM-fluid periphery** — auto-inferred edges, suggested actions, retrieval — but typed core kept deterministic for security/transactionality |
| Human-driven workflows (Workshop, Slate, Quiver) | Goals declared in natural language, agents compose Actions to achieve them. AOP-style (Sierra/Decagon) |
| 3–12 month FDE-led rollouts | Self-configuring: connectors → agent ingests samples → infers starter ontology → proposes security model → asks only on ambiguity (Corvic, Datris, Meko pattern) |
| Actions as Workshop UI buttons | Actions as **agent tools by default** with typed signatures, side effects, security — exactly the MCP tool pattern |
| $1M–$50M enterprise contracts | Barbell: bottom-up mid-market at $30K–$300K; top-down enterprise at $5M+ |
| Foundry-the-UI is where agents live | Agents live in Claude/Cursor/ChatGPT/Cowork — Foundry-equivalent stays the **backend of record** via MCP exposure |

### 5.6 What's actually moaty (ranked by replicability)

1. **The Ontology** (intangible asset / switching cost). Genuine moat for high-stakes operational use cases. Erodes at the low end as AI-native alternatives mature.
2. **The FDE motion** (process / organizational moat). Replicable culturally but hard executionally. Sierra has copied at $100M ARR. OpenAI's DeployCo is the most strategic threat per Morningstar.
3. **Trust / compliance / security posture** (the most underrated moat). FedRAMP High, IL-5/IL-6, defense heritage, lineage-aware marking propagation. Hardest to replicate. Caps the addressable market but creates a near-monopoly in regulated environments.

The **stacked combination** is the real moat. Any one is replicable; all three together are not — at least not by any current competitor.

### 5.7 Death by a thousand cuts is the actual risk

The risk isn't a single Foundry killer; it's:

- Mid-market AI-native data platforms (Datris, Corvic, Meko, Exabase) eating the bottom of the TAM Palantir never served.
- AI labs (OpenAI's DeployCo, Anthropic, future others) eating new AI use cases at the top before they become "Ontology-shaped." Morningstar lowered Palantir's terminal growth rate from 15% to 12% specifically because of this risk.
- Glean-type horizontal AI search eating simpler "find/answer/automate" workflows.
- Sierra/Decagon eating customer-experience and outreach automation.

---

## Part VI — The Modern Foundry Thesis

### 6.1 The core argument

If you were starting Foundry in 2026, you would not begin with data integration. You would begin with the **agent access control plane** — the layer that intermediates every agent-to-tool, agent-to-data, and agent-to-system interaction in the enterprise. That layer has three structural properties Foundry's data integration had in 2003:

1. **It is unsolved.** Every CISO knows it; no incumbent has shipped a complete answer.
2. **It is the single highest-leverage chokepoint in the AI stack.** Whoever owns it sees every action, every tool, every authorization decision, every audit event — across every system the agent touches.
3. **It generates customer-specific metadata that compounds into an ontology.** Every policy decision is a labeled training example: this user, this agent, this tool, this object, this outcome. After 18 months of operation, the customer's policy graph *is* the de facto ontology of who-can-do-what in the enterprise.

The wedge is not "we sell better RBAC." The wedge is: **we are the access plane for agents; that plane is also the data plane; that plane is also where the operational AI workflows of your enterprise will eventually run.**

### 6.2 The architectural picture

```
┌──────────────────────────────────────────────────────────────────┐
│ LAYER 5: Operational Apps (the future Foundry-equivalent)         │
│   - Agent-composed workflows, natural-language declared           │
│   - Workshop-style UIs auto-generated from ontology + intent      │
│   - Approval queues, HITL, escalation rules                       │
├──────────────────────────────────────────────────────────────────┤
│ LAYER 4: The Ontology (built bottom-up from agent activity)       │
│   - Object types inferred from connected systems                  │
│   - Action types == tool catalog                                  │
│   - Markings, classifications, lineage propagation                │
├──────────────────────────────────────────────────────────────────┤
│ LAYER 3: Policy Engine (PDP)                                      │
│   - RBAC + ABAC + ReBAC + dual-principal (user + agent)           │
│   - Cross-customer policy library (network effect)                │
│   - Cedar/Rego/OpenFGA under the hood                             │
├──────────────────────────────────────────────────────────────────┤
│ LAYER 2: MCP / Agent Gateway (the wedge)                          │
│   - OAuth 2.1 + RFC 8707 + CIMD                                   │
│   - Federation to Okta/Entra/Auth0                                │
│   - Per-user OAuth lifecycle for downstream systems               │
│   - Token vault, DLP, audit                                       │
│   - Shadow MCP detection                                          │
├──────────────────────────────────────────────────────────────────┤
│ LAYER 1: Workload + NHI Identity                                  │
│   - SPIFFE/SPIRE for agent runtime identity                       │
│   - `act` claim chain for delegation                              │
│   - Federation to AWS IRSA / GCP WIF / Azure FIC                  │
└──────────────────────────────────────────────────────────────────┘
```

The land sequence:

1. **OSS MCP gateway** — free, broad coverage, captures developer mindshare like LiteLLM did for AI gateways.
2. **Cloud governance tier** — $50K–$250K ACV, sells to a CAIO direct. Adds SSO, audit, per-tool RBAC, token vault, basic policy.
3. **Enterprise platform** — $500K–$5M ACV, CISO + CIO + CAIO triad. Adds policy engine, ontology inference, cross-system policy enforcement, compliance posture.
4. **FDE-led ontology builds** — $5M–$50M ACV, vertical-specific (BFSI or life sciences first), with named SI partner (Accenture or Deloitte). Full operational apps on top.

### 6.3 Why this wedge specifically — and not the alternatives

The user proposed several wedges implicitly. Ranked:

| Wedge | Time to ARR | Defensibility | Risk |
|-------|------------|---------------|------|
| **MCP gateway → policy → ontology** (recommended) | Fast (PLG-able) | Moves up-stack to ontology over time | Race against AWS/Microsoft gateway-bundling |
| NHI / agent identity standalone | Fast | Low | Acqui-hire ceiling (Astrix → Cisco at $250–350M) |
| Token spend governance | Fast | Low | Portkey, LiteLLM, OpenRouter are ahead; commoditizing |
| Vertical FDE-led from day one | Slow | High | Capital intensive, hard before product spine exists |
| Foundry-equivalent direct | Very slow | Very high | Requires customer-specific ontology before any wedge exists |

The MCP-gateway wedge is the right answer because (a) it's the fastest commoditizing layer *and* the only entry point that touches every agent-tool packet, (b) it's the natural seat from which to claim the ontology and policy layers later, (c) it's PLG-able (developers adopt it before security teams), and (d) it's where the most volatile standards work is happening — meaning the team that ships the cleanest enterprise implementation owns the conversation.

### 6.4 The forward-deployed engineer model — apply it discriminately

The FDE pattern works only if you apply Palantir-style discipline:

- **FDEs report to product/engineering**, not to a services P&L. This is the cultural lever Sierra preserved and Cresta did not.
- **Platform spine first.** Without a spine, FDEs produce bespoke deployments that don't compound — you become a consultancy.
- **Per-engineer fully loaded cost** ~$300–400K/year ([N47 analysis](https://n47.com/insights/the-forward-deployed-engineer-dilemma)). Customer must pay $200K+/engineer/year minimum for the math to work.
- **>50% FDE vs product engineer after Year 3 = consultancy alert.**

Decagon explicitly *rejected* FDE at $35M ARR; Sierra is doubling down at $100M ARR (400% YoY). Both work — different margin/growth tradeoffs. For an access-control-led play, **start product-led** (OSS gateway, mid-market cloud governance) and only spin up FDEs when the enterprise platform tier requires bespoke ontology builds.

### 6.5 The network effect to build deliberately

This is the moat the user did not name but should:

After deploying the access plane to 50 enterprises, you have anonymized data on:

- "98% of finance teams with Salesforce write access also enable these 3 specific tools."
- "Agents that touch both `customer.email` and `payment.account_number` have a 12x higher confused-deputy incident rate."
- "92% of healthcare orgs require `phi_marker.propagation = true` on derived data."

This **cross-customer policy library** is uncopyable — it requires the labeled deployment data from many real enterprises. It powers a recommendation engine for least-privilege policy ("here's the policy 80% of similar orgs use") and an anomaly detection layer ("this agent is acting outside the patterns of similar agents at peer companies"). This is exactly the Astrix/Oasis pitch and the only true network effect in the access-control space.

---

## Part VII — Token Spend Governance: The Tertiary Wedge Worth Taking Seriously

### 7.1 The problem is real and growing fast

Coding agents burn tokens at unprecedented rates per developer-hour. Anthropic's own data: median **~$13 per developer per active day, $150–$250 per developer per month**, with 90th percentile under $30/active day. At 1,000 developers, that's $2.4M/year for one tool, ignoring chat and other apps.

Anthropic explicitly tells customers to throttle: at 500+ users they recommend dropping per-user TPM allocation to 10–15K (from 200–300K for 1–5 user teams) because organization-level rate limits otherwise blow up.

### 7.2 The Anthropic March 2026 unbundling is the central story

Anthropic eliminated bundled-token enterprise seat plans in a phased rollout culminating **March 8, 2026**. The new model:

- $20/seat/month base (chat + Claude Code + Cowork on one seat).
- Min 20 seats annual, 50 seats sales-assisted.
- **Every token billed at standard API rates on top.** Mandatory monthly spend commitment.
- API volume discounts (10–15%) removed under the new structure.

NPI Financial and Redress Compliance both forecast **higher total TCO** under the new model despite the lower headline seat fee. For one 800-user organization, modeled gap was **$336K–$1.4M annually**. OpenAI and Google still bundle but are expected to follow within 6 months.

### 7.3 The gateway landscape

| Vendor | What | Position |
|--------|------|----------|
| **LiteLLM** | OSS proxy, 100+ providers, 240M Docker pulls, 1B+ requests | OSS leader |
| **Portkey** | Managed control plane, 500B+ tokens/day, 24K orgs, **$15M Series A Feb 2026** | Compliance-managed leader |
| **Cloudflare AI Gateway** | Edge, free tier, unified billing | Cloudflare-shop default |
| **Helicone** | **Acquired by Mintlify Mar 2026, maint mode** | Out |
| **Kong AI Gateway** | API gateway extending to AI, cost-based rate limiting | Incumbent gateway plays |
| **OpenRouter** | 400+ models, 5% markup, $50M ARR, talks for $120M @ $1.3B | Indie/multi-cloud dark horse |
| **TrueFoundry** | Full-stack gateway + MCP + agent | Regulated-industry play |
| **Vellum** | End-to-end AI dev platform | Eval-adjacent |
| **Braintrust** | $80M Series B @ $800M val Feb 2026 | Eval leader |
| **Langfuse** | **Acquired by ClickHouse Jan 2026** | Absorbed |

### 7.4 Where token budget intersects with access control

This is the strategic insight: **token budget IS an access control axis.**

- **Spend budget:** "this team can spend $X/day on Claude."
- **Model-level allowlists:** "Finance can use Opus, Marketing only Haiku."
- **Tool/MCP-level access:** per-virtual-key tool filtering. "Finance Agent gets accounting tools, not email tools."
- **PII/DLP on agent traffic.**
- **Identity-based RBAC at the gateway.**
- **Tool sandboxing.**

Google Cloud already ships IAM deny policies specifically for `mcp.tools.call` with attributes like `tool.isReadOnly`, `request.auth.oauth.client_id`, `resource.service`. This is the convergence point: the AI gateway and the agent access plane are the same layer logically. **The recommended wedge product unifies them deliberately.**

### 7.5 Why this is tertiary, not primary

Three reasons not to lead with token governance:

1. **The category is crowded and commoditizing.** Portkey, LiteLLM, Cloudflare, OpenRouter, Kong are all well ahead. The 2026 entrant has to either be 10x better or sit one layer up.
2. **It is procurement-led, not architecturally load-bearing.** A FinOps tool is a cost lens; it does not own the policy decision plane. It can be added to any access plane after the fact.
3. **The margin profile is thin.** OpenRouter is at 5% markup on inference. LiteLLM is OSS. Portkey is governing $180M ARR equivalent for a base price of $49/mo. The dollars do not concentrate at this layer.

That said, **build it as a feature of the access plane, not a separate product.** Anthropic's March 2026 unbundling forces every enterprise to attribute spend — and per-agent attribution is exactly the data the access plane is already capturing. The gateway sees every token; layering a chargeback/showback view on top is essentially free.

---

## Part VIII — Market Sizing, GTM, and a Concrete Path

### 8.1 Market sizing — the numbers that matter

| Segment | 2024–2025 | 2028–2030 forecast | CAGR | Source |
|---------|-----------|---------------------|------|--------|
| Global IAM (all) | $22.9–24B | $34–49B by 2029 | 8.4–15% | MarketsandMarkets / Fortune Business |
| IGA software | $4.5B (2024) | $5.8B (2027) | ~9% | ISG/IMI |
| PAM | $4.8B (2024) | $5.6B+ | 10–15% | ISG |
| **CIEM** | $1.2B (2023) | **$7.5B by 2028** | **44.2%** | MarketsandMarkets — fastest-growing |
| AI Gateway | $41M (2025) | $180M by 2032 | 20.7% | Market IntelliX |
| LLM observability | $510M (2024) | $8.1B by 2034 | 31.8% | — |
| LLMOps | — | $4.8B by 2028 | — | Bessemer |
| **Agent identity / NHI (implied)** | undefined | **$3–5B by 2027, $15–25B by 2030** | very high | extrapolation from funding |
| Data integration / Foundry-adjacent | ~$15B | $40–50B by 2028 | mid-teens | IDC composite |
| Forward-deployed AI app layer (top 10) | ~$1B ARR aggregate | tens of $B by 2028 | very high | Composite (Sierra, Decagon, Glean, Cognition) |

CIEM at 44.2% CAGR is the most relevant historical analog to "agent access governance" — same buyer (CISO/Cloud Security), same fundamental problem (entitlements sprawl). Implied "modern Foundry" TAM (combining policy + ontology + agent ops) by 2030: **$30–60B**.

LLM API spend trajectory: 2024 $3.5B → mid-2025 $8.4B → 2026 projected $30–40B → 2028+ unclear but $100B+ plausible. Anthropic $19B ARR (early 2026, 85%+ enterprise); OpenAI $25B ARR; Claude Code alone at $2.5B+ run-rate.

### 8.2 The buyer triad

| Persona | Role | Budget authority |
|---------|------|---------------------|
| **CISO** | Owns identity, owns breach narrative | Dominant for NHI/identity wedge |
| **CIO / Head of Platform Eng** | Owns platform, integrates the tool | Technical evaluator |
| **Chief AI Officer (CAIO)** | The wild card | **76% of orgs have a CAIO in 2026** (up from 26% in 2025); 61% control AI budgets ranging $5M (small co) to $500M+ (large enterprise) |

A $250K–$1M ACV wedge is CAIO-approvable solo. A $5M+ contract requires the full triad.

### 8.3 Sales cycle reality

| ACV | Median cycle |
|-----|-------------|
| <$25K | 14–30 days |
| $25K–$100K | 60–72 days |
| $100K–$250K | 90–128 days |
| $250K–$500K | 120 days |
| $500K+ | 180+ days |
| Enterprise IAM (10M+ identities) | **9–18 months deployment** |

The $100K threshold triggers formal procurement at 78% of enterprises (+30–45 days). SOC 2 Type II is table stakes. ISO 27001 + GDPR DPA required for EU. HIPAA + BAA for healthcare. FedRAMP Moderate for federal. **ISO/IEC 42001 (AI management) is the new emerging gate** — Cresta got it first in contact-center AI in January 2025.

### 8.4 The SI moves that just happened

- **Accenture–Anthropic Business Group** (Dec 2025): 30,000 Accenture professionals trained on Claude. "Reinvention deployed engineers." Claude Code COE inside Accenture.
- **Deloitte–Google Cloud Agentic Transformation Practice** (April 2026): 1,000+ pre-built agents, Deloitte Ascend platform, Google FDEs embedded alongside Deloitte teams.
- **Google Cloud $750M partner fund** at Cloud Next '26 to Accenture, BCG, Bain, Deloitte, McKinsey, plus AI-native shops (Distyl.ai, Tribe.ai, Tryolabs, Artefact).
- **Palantir–Accenture** partnership (2,000+ Palantir-skilled professionals).

SI partnerships are table stakes for any vertical AI play. A modern Foundry wedge needs at least one named SI partner pre-Series B to be credible in regulated verticals.

### 8.5 The concrete go-to-market path

**Phase 0 (months 0–6): Build the OSS MCP gateway.**
- Best-in-class OAuth 2.1 + RFC 8707 + CIMD support. Aim to be the most spec-compliant gateway in market.
- Federation to Okta, Entra ID, Auth0, WorkOS.
- Per-user OAuth lifecycle, token vault, audit log.
- Free, MIT-licensed, fully self-hostable.
- Goal: become the LiteLLM of MCP — capture developer mindshare.

**Phase 1 (months 6–12): Cloud governance tier ($50K–$250K ACV).**
- Managed multi-tenant version of the gateway.
- Per-tool RBAC, basic policy engine (Cedar or OpenFGA under the hood).
- Cross-system audit log with `act` claim chain support.
- Token spend attribution (FinOps view) as included feature.
- SOC 2 Type II, ISO 27001.
- Sell to CAIOs at AI-forward enterprises ($5M–$100M AI budget).
- Pick **one named vertical** to land deep (BFSI is the recommendation — high regulatory pressure, willing-to-pay, lots of fragmented SaaS).

**Phase 2 (months 12–24): Enterprise platform ($500K–$5M ACV).**
- Policy engine matures: ABAC + ReBAC + dual-principal authorization.
- **Ontology layer** begins: auto-inferred from connected systems + agent activity.
- Compliance: HIPAA + BAA, FedRAMP Moderate in flight, ISO 42001.
- Sell to CISO + CIO + CAIO triad.
- One named SI partner (target: Accenture or Deloitte alliance).
- Cross-customer policy library starts generating network effect.

**Phase 3 (months 24–48): FDE-led ontology builds ($5M–$50M ACV).**
- Forward-deployed engineers reporting to product/engineering.
- Workshop-equivalent operational app layer.
- Vertical-specific ontologies (BFSI ontology with KYC, OFAC, trade surveillance pre-loaded).
- Full Foundry-equivalent posture.

### 8.6 Defensibility — the four moats to build in parallel

1. **Cross-customer policy network effect.** Anonymized policy patterns across hundreds of enterprises. Recommendation engine for least-privilege. Anomaly detection for "agent acting outside peer patterns."
2. **Vertical ontology depth.** BFSI first. Deep pre-loaded object types, action types, security model. Sierra did this in CX; same playbook works in BFSI.
3. **Compliance certification stack.** SOC 2 + ISO 27001 + ISO 42001 + HIPAA + FedRAMP Moderate + EU residency + StateRAMP combo takes 18–24 months to assemble. Real barrier.
4. **FDE relationship moat.** Once an FDE is embedded for 12+ months building the customer's ontology, switching cost is measured in years.

### 8.7 The risks to take seriously

- **Incumbent encirclement is happening now.** Microsoft Entra Agent ID (GA May 2026), Okta for AI Agents (GA April 30, 2026), AWS AgentCore Gateway (GA Oct 2025). 12–18 month window before the bundled-free option commoditizes the gateway layer.
- **CAIO churn.** 76% adoption today but Harvard Business Review called many CAIO roles "tenuous." Turnover at this role resets deals.
- **Model vendor consolidation.** If Anthropic + OpenAI absorb 70%+ of API spend and ship first-party enterprise governance, they own the choke point.
- **MCP standardization is moving so fast** that any vendor-specific extensions become liabilities — bet on the standards, do not try to fragment.
- **The FDE margin trap.** Hire FDEs into product/engineering or you become a consultancy.

### 8.8 The five questions to answer in the next 90 days

1. **Which vertical?** BFSI (recommended) vs life sciences vs federal vs manufacturing. Pick one and pre-commit.
2. **Which SI partner?** Accenture (Anthropic-aligned) vs Deloitte (Google-aligned) vs in-house FDE-only. The right answer is "in-house first, SI as channel later" — but the SI relationship needs to start in parallel.
3. **OSS or managed-only at the gateway layer?** Strong recommendation: OSS. The take-rate is too thin; the mindshare matters too much.
4. **Cedar, OpenFGA, or build-from-scratch on the policy engine?** Strong recommendation: OpenFGA (Auth0/Okta-backed, Zanzibar-style, ReBAC-native). Cedar locks you into AWS thinking; building from scratch is the wrong battle.
5. **What is the metric you sell on?** Token-spend reduction, breach risk reduction, agent activation count, time-to-production-agent? The one that lands cleanest in 2026 is **"time to onboard a new agent into your enterprise from days to minutes with full governance" — that is the productivity story a CAIO can defend to a board.**

---

## Key Takeaways

1. **The agent access control problem is real and the user is right that no incumbent has solved it — but the window to claim "agent identity" as a standalone wedge is closing within 12–18 months.** Microsoft Entra Agent ID (May 2026), Okta for AI Agents (April 30, 2026), and AWS Bedrock AgentCore Gateway (Oct 2025) are all GA. Pure NHI-discovery startups will be acqui-hired into security platforms; Cisco-Astrix at $250–350M sets the ceiling.

2. **The genuine opportunity is one layer up: the policy + ontology + operational application plane built on top of the access plane.** This is what Foundry actually is. Building it requires winning the gateway wedge first.

3. **The MCP gateway is the right wedge because it is the session layer for agent-tool interactions and the only structural chokepoint that touches every agent-tool packet.** It is also the fastest-commoditizing layer, so first-mover with cleanest spec compliance matters disproportionately.

4. **Foundry's actual moat is the stack — ontology + FDE motion + compliance posture — not any single piece.** Lineage-aware mandatory access controls are uniquely Foundry; nothing in commercial SaaS comes close. Any modern equivalent must replicate this layered access model from day one.

5. **Most enterprise IdPs are not yet MCP-compliant** (Okta, Entra ID, Auth0 all incompatible with RFC 8707 as of Q1 2026). This is a real wedge for a compliant MCP authorization server that fronts existing IdPs.

6. **Token spend governance is real, $30–40B in 2026 spend, but it is the tertiary wedge.** Build it as a feature of the access plane; don't lead with it. Portkey, LiteLLM, Cloudflare, and OpenRouter are too far ahead, and the margin profile is too thin.

7. **The FDE motion works only with Palantir-style discipline:** FDEs report to product/engineering; platform spine first; >50% FDEs vs product engineers after Year 3 is a consultancy alert. Sierra preserves this discipline; Cresta did not.

8. **The strongest defensible moat available to a new entrant is the cross-customer policy network effect.** Anonymized policy patterns across hundreds of enterprises is the only true network effect in the access-control space and exactly the Astrix/Oasis pitch.

9. **The buyer is a CISO/CIO/CAIO triad. 76% of orgs have a CAIO in 2026.** A $250K–$1M ACV wedge is CAIO-approvable solo; $5M+ requires the full triad. CAIO budgets range from $5M (small co) to $500M+ (large enterprise).

10. **Incumbent encirclement: Palo Alto + CyberArk closed at $25B in Feb 2026. CrowdStrike bought SGNL for $627.9M in Jan 2026. Thoma Bravo owns SailPoint, Ping, and ForgeRock. The independent identity vendor above $500M ARR is going extinct.** A new entrant must plan for acquisition as the most likely outcome — and structure to maximize position when that bid arrives.

---

## Predictions

1. **By end of 2027, Microsoft Entra Agent ID and Okta for AI Agents will own >40% of "agent identity primitive" deployments combined.** Bundling and existing IdP relationships are too strong. Standalone agent identity startups will either be acquired (Astrix → Cisco; another → Microsoft or Okta) or pivot up-stack to policy/ontology.

2. **The MCP gateway category will commoditize by Q4 2026.** AWS, Microsoft, Google, and Cloudflare will all ship free or near-free MCP gateways bundled with their clouds. Standalone gateway vendors (Composio, Arcade, TrueFoundry) survive only by moving up-stack to policy and ontology layers.

3. **At least one new "Foundry-equivalent" vendor will emerge by end of 2027 with $50M+ ARR and a defensible ontology layer built on top of the agent access plane.** It will be vertical-led (BFSI or life sciences), SI-channeled, and FDE-heavy in years 1–3 transitioning to product-led by year 4. This is the company the user should build.

4. **Cisco will close on Astrix at $250–350M by Q3 2026.** This sets the ceiling for pure-play NHI vendors and reinforces that the standalone NHI category is an acqui-hire market.

5. **Anthropic and OpenAI will both ship first-party enterprise governance consoles by Q1 2027** that handle SSO + audit + per-team budget + per-tool access + BYOK. They will not own the customer's full agent-access plane (because their view stops at their API) — but they will pressure-test any third-party access vendor's ability to add value above the model.

6. **MCP will absorb at least one major attack class CVE-style incident affecting a Fortune 100 in 2026** that triggers either (a) an OWASP-style mandatory remediation framework or (b) a wave of enterprise procurement gates requiring "MCP security certification." Either outcome is bullish for a compliance-led access plane.

7. **ISO/IEC 42001 will be required by 30%+ of enterprise AI procurement RFPs by end of 2027.** Cresta got it first in January 2025. The cluster of regulated-vertical AI vendors who lock this in before mid-2026 will have a year of pricing power.

8. **Palantir's terminal growth will compress from current expectations** as AI labs forward-deploy directly into customer environments (OpenAI DeployCo and successors). Morningstar already lowered terminal growth from 15% to 12%; further compression to 8–10% is plausible by 2028. The bull case for Palantir requires they convert their AIP + Ontology + FDE stack into a credible "AI-native Foundry" before three competitors do — they have a real chance, but not a structural lock.

9. **Token spend will exceed cloud compute spend at 20%+ of enterprises by 2028.** AI FinOps will become a recognized category equal in size to cloud FinOps. Vantage, Apptio, CloudHealth, and at least one purpose-built AI FinOps vendor will emerge as the dominant tools. The agent access plane that includes per-user/per-agent/per-tool token attribution from day one wins the FinOps conversation by default.

10. **The single most important question for a "modern Foundry" entrant is which vertical to land first.** BFSI is the recommendation: high regulatory pressure, willing-to-pay, lots of fragmented SaaS (CRM + risk + trading + compliance + HR + comms all in different systems), strong existing forward-deployed culture from the consulting industry, and Anthropic/Accenture's BFSI focus creates a co-sell tailwind. Life sciences is the credible alternative, with the FDA's emerging AI guidance creating a similar regulatory pressure cooker.
