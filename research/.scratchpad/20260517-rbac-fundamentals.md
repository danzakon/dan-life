# RBAC and Enterprise IAM: Educational Deep-Dive Findings

**Category:** Technical
**Date Started:** 2026-05-17
**Status:** [x] Complete

---

## Summary

Comprehensive raw findings on access control and enterprise IAM, organized as a novice-to-advanced curriculum. Covers the historical arc from DAC/MAC through the 1992 Ferraiolo-Kuhn RBAC paper, the Sandhu et al. (1996) RBAC0-3 family, the ANSI/INCITS 359-2004 standard, modern alternatives (ABAC, ReBAC/Zanzibar, PBAC), the federation protocol stack (SAML, OIDC, OAuth 2.1, SCIM, LDAP, Kerberos), and the enterprise governance layers built on top (IGA, PAM, CIEM, workload identity, compliance, audit). Each section concludes with practical failure modes documented from real enterprise deployments.

---

## 1. History: From DAC/MAC to RBAC

The Trusted Computer Security Evaluation Criteria (TCSEC, "Orange Book," 1983) institutionalized two access-control models:

- **Discretionary Access Control (DAC)**: object owners grant/revoke permissions at their discretion. Familiar through Unix file modes and Windows ACLs.
- **Mandatory Access Control (MAC)**: a system-enforced policy ties subjects (clearances) to objects (sensitivity labels). Designed for multilevel-secure military systems (Bell-LaPadula confidentiality; Biba integrity).

DAC's weakness in commercial settings is that "the corporation or agency is the actual owner of system objects" — the end user shouldn't be granting access discretionarily ([Ferraiolo & Kuhn, 1992](https://csrc.nist.gov/files/pubs/conference/1992/10/13/rolebased-access-controls/final/docs/ferraiolo-kuhn-92.pdf)). MAC, conversely, is too rigid for civilian use; it's built around classification labels, not job functions.

**The Ferraiolo & Kuhn paper (1992)**, presented at the 15th National Computer Security Conference, introduced **Role-Based Access Control (RBAC)** as a *non-discretionary* control that is not based on multilevel labels. The core insight: in commercial organizations, access is naturally organized by *function* (teller, auditor, doctor), not by owner discretion or sensitivity label. The paper formalized roles as sets of permissions, role hierarchies, subject-role activation, subject-object mediation, and constraints on user/role membership. Three baseline rules: role assignment, role authorization, and permission authorization ([NIST RBAC FAQ](https://csrc.nist.gov/Projects/role-based-access-control/faqs)).

Rudimentary role-based controls existed in commercial systems through the 1970s and 80s, but Ferraiolo-Kuhn gave it a formal model. Their key contribution: "all access is through roles" — users get permissions only via roles; roles are stable while user-to-role and permission-to-role mappings change.

## 2. The Sandhu RBAC0/1/2/3 Family (1996)

Sandhu, Coyne, Feinstein, and Youman (SCFY) at George Mason published "Role-Based Access Control Models" in IEEE Computer (1996), formalizing four conceptual layers ([Sandhu et al. 1996](https://csrc.nist.gov/csrc/media/projects/role-based-access-control/documents/sandhu96.pdf)):

| Model | Adds |
|-------|------|
| RBAC0 | Base: Users (U), Roles (R), Permissions (P), Sessions (S); UA (user-role assignment), PA (permission-role assignment) |
| RBAC1 | Role hierarchies as a partial order; senior roles inherit permissions of junior roles |
| RBAC2 | Constraints — predicates over UA, PA, sessions (mutual exclusion, cardinality, prerequisite) |
| RBAC3 | Combines RBAC1 + RBAC2; both hierarchies and constraints |

RBAC1 and RBAC2 are *incomparable* — either can be added without the other. RBAC3 introduces subtle interactions (e.g., a mutual-exclusion constraint on roles A and B may be violated by a senior role that inherits both; the model intentionally permits multiple resolutions).

## 3. NIST Unified Model and ANSI/INCITS 359-2004

In 2000, Sandhu, Ferraiolo, and Kuhn published "The NIST Model for Role-Based Access Control: Towards a Unified Standard" at the 5th ACM RBAC Workshop ([NIST 2000](https://www.nist.gov/publications/nist-model-role-based-access-control-towards-unified-standard)). After community review, the model was adopted by ANSI/INCITS as **INCITS 359-2004**, the formal US national RBAC standard. It defines four components:

1. **Core RBAC** — users, roles, permissions, sessions, UA, PA, role activation
2. **Hierarchical RBAC** — partial-order role inheritance
3. **Static Separation of Duty (SSD)** — prevents conflicting role *assignments*
4. **Dynamic Separation of Duty (DSoD)** — prevents simultaneous *activation* of conflicting roles in one session

RBAC3 ≈ INCITS 359 except RBAC3 specifies a partial-order hierarchy while Ferraiolo-Kuhn 1992 originally specified a rooted tree (single inheritance vs. multiple).

## 4. Core RBAC Concepts

- **User**: a human or non-human principal.
- **Role**: a named collection of permissions matching a job function.
- **Permission**: an (operation, object) pair.
- **Session**: a runtime instantiation; a user activates a *subset* of their authorized roles. Sessions enable least privilege at activation time.
- **Role hierarchy**: senior inherits junior. E.g., `Manager ⊒ Employee`. Can be tree (single inheritance) or DAG (multiple).
- **Constraints**: predicates that gate UA/PA/session configurations. Most important class: separation of duty.

### Separation of Duties (SoD)

NIST SP 800-192 defines SoD as "no user should be given enough privileges to misuse the system on their own" ([NIST SP 800-192](https://nvlpubs.nist.gov/nistpubs/specialpublications/nist.sp.800-192.pdf)).

- **Static SoD**: roles A and B cannot both be assigned to the same user (e.g., payment-initiator and payment-approver).
- **Dynamic SoD**: assignment is allowed but simultaneous *activation* in one session is not (e.g., teller and account-holder roles).
- **History-based SoD**: constraints based on past actions (e.g., reviewer cannot also approve a record they edited).

Kuhn (1997) proved necessary and sufficient conditions for SoD safety in RBAC. SoD is the most-cited RBAC constraint type because it directly enforces SOX-style financial-fraud controls.

## 5. Least Privilege, Zero Standing Privilege, Just-in-Time Access

**Principle of Least Privilege (PoLP)** — encoded in [NIST SP 800-53 AC-6](https://nist-sp-800-53-r5.bsafes.com/docs/3-1-access-control/ac-6-least-privilege): "allow only authorized accesses that are necessary to accomplish assigned organizational tasks." Originally articulated by Saltzer and Schroeder (1975).

**Zero Standing Privilege (ZSP)** — a stronger property: no human (or workload) carries permanent elevated entitlements. Privilege is granted at the moment of need and revoked immediately. CyberArk frames it as "creating permissions on the fly and removing them after use" ([CyberArk PAM](https://cyberark.com/products/privileged-access-manager)).

**Just-in-Time (JIT) access** — the mechanism that operationalizes ZSP: a request triggers an approval (automated or human), permissions are bound to a short-lived session (4 hours is a common default in CyberArk), then auto-revoked. NIST SP 800-207 ([Zero Trust Architecture](https://nvlpubs.nist.gov/nistpubs/specialpublications/NIST.SP.800-207.pdf)) makes per-session, dynamically-evaluated access a foundational tenet.

The progression: PoLP (don't grant more than needed) → ZSP (don't keep it standing) → JIT (grant on demand). Zero Trust Architecture is the umbrella: NIST CSWP 20 emphasizes "all resource authentication and authorization are dynamic and strictly enforced before access is allowed."

## 6. RBAC vs. ABAC vs. ReBAC vs. PBAC vs. ACL

| Model | Decision Basis | Best For | Failure Mode |
|-------|---------------|----------|--------------|
| ACL | Identity → object | Filesystems, small systems | O(users × objects) explosion |
| RBAC | Role → permission | Stable job functions, coarse policy | Role explosion (1300 roles for a 50k-employee bank per NIST) |
| ABAC | Attribute predicates | Context-dependent (time, location, risk, classification) | Policy authoring complexity; scattered ABAC logic in code is unauditable |
| ReBAC | Subject ↔ object graph | Resource-level sharing (Drive, GitHub, Jira) | Recursive policies hard to audit; resource-intensive |
| PBAC | Externalized policy artifact (Rego/CEL/XACML) | Governing the decision process itself | Policy engine becomes single point of failure |

**ABAC** is defined in [NIST SP 800-162](https://nvlpubs.nist.gov/nistpubs/specialpublications/NIST.SP.800-162.pdf): "controls access by evaluating rules against the attributes of entities, operations, and the environment." NIST explicitly notes that ACLs and RBAC are special cases of ABAC (identity-attribute and role-attribute respectively). ABAC addresses RBAC's "role explosion" — when every contextual nuance forces a new role, ABAC encodes the nuance as a predicate.

**ReBAC** (Relationship-Based Access Control) was named by Carrie Gates in 2006 but exploded into mainstream practice with [Google's Zanzibar paper (USENIX ATC 2019)](https://www.usenix.org/system/files/atc19-pang.pdf). Zanzibar models permissions as relation-tuples — `(object#relation@user)` — and answers "Can Alice edit document X?" by graph traversal. It powers Drive, YouTube, Calendar, Photos, Maps, Cloud. Key technical contributions:

- **Trillions of ACLs**, **millions of authz checks/sec**, **<10ms p95**, **>99.999% availability**
- **External consistency** via Spanner TrueTime
- **Zookies** — opaque consistency tokens that solve the "new enemy problem" (preventing old ACLs from being applied to new content after a revocation)
- **Leopard** — specialized index for nested group membership

OSS Zanzibar implementations: **SpiceDB/AuthZed**, **OpenFGA**, **Permify**, **Ory Keto**, **Auth0 FGA**, **WorkOS FGA**. Per [authzed.com](https://authzed.com/learn/google-zanzibar), ReBAC "can model RBAC (roles as objects with member relationships) plus complex scenarios... difficult in traditional RBAC."

**PBAC** treats policies as first-class artifacts evaluated by a Policy Decision Point (PDP) — Open Policy Agent (OPA) with Rego, AWS Cedar, XACML historically. The split: ABAC is the *input model* (attributes); PBAC is the *governance model* (where policy lives and how it's reviewed/versioned). Modern systems use all of them: RBAC for coarse policy (org admin vs. member), ReBAC for resource sharing, ABAC for contextual edge cases, PBAC as the control plane.

**Real-world choice**: [Deepak Gupta's CIAM Compass](https://guptadeepak.com/ciam-compass/guides/rbac-vs-abac-vs-rebac/) observes: "RBAC scales to 5–10 roles; beyond that, role explosion makes maintenance expensive... most B2B SaaS in 2026 ends up with a hybrid: RBAC for coarse-grained policy, ReBAC for resource-level permissions."

## 7. Identity Protocols

| Protocol | Layer | Purpose | RFC / Spec |
|----------|-------|---------|------------|
| LDAP | Directory access | Query/modify identity store | RFC 4511 |
| Kerberos | Authentication | Ticket-based mutual auth in trusted networks | RFC 4120 |
| SAML 2.0 | Federation | XML assertions for enterprise SSO | OASIS 2005 |
| OAuth 2.0 | Authorization | Delegated API access | RFC 6749 |
| OAuth 2.1 | Authorization | Consolidates 2.0 + BCP, removes Implicit/ROPC, mandates PKCE | draft-ietf-oauth-v2-1 |
| OIDC | Authentication | Identity layer on OAuth 2.0 (ID token = JWT) | OpenID Foundation 2014 |
| SCIM 2.0 | Provisioning | REST API for user lifecycle (CRUD) | RFC 7643/7644 |
| JWT | Token format | Signed/encrypted JSON claims | RFC 7519 |

Key distinctions practitioners get wrong:

- **LDAP is not an auth protocol** — it's the directory. Auth happens via simple bind, SASL, or by being the lookup behind Kerberos. Active Directory wraps LDAP + Kerberos + DNS + replication.
- **OAuth 2.0 is authorization, not authentication** — using it as login was the misuse that motivated OIDC (2014). OIDC adds the ID Token (a JWT), `userinfo` endpoint, standard scopes (`openid`, `profile`, `email`).
- **SCIM ≠ SSO** — SAML/OIDC log a user in; SCIM creates/updates/deactivates the account. SCIM deprovisioning is the critical lifecycle control: it's what removes ex-employee access from every connected SaaS in near-real-time.
- **JWT is a token format, not a protocol** — used inside OIDC ID tokens, OAuth access tokens (when not opaque), SPIFFE JWT-SVIDs.

[OAuth 2.1 (draft-ietf-oauth-v2-1)](https://datatracker.ietf.org/doc/draft-ietf-oauth-v2-1/) changes from 2.0:
1. PKCE (RFC 7636) mandatory for Authorization Code grant
2. Implicit grant removed
3. Resource Owner Password Credentials grant removed
4. Exact-string `redirect_uri` matching required
5. No bearer tokens in URI query strings
6. Refresh tokens must be sender-constrained or single-use

## 8. SSO Architecture: IdP vs SP

```
┌──────────┐   1. Request   ┌──────────┐
│  User    │ ─────────────▶ │   SP     │  (Service Provider /
│ (Browser)│                │  (App)   │   Relying Party in OIDC)
└──────────┘                └────┬─────┘
     ▲                           │ 2. Redirect to IdP
     │                           ▼
     │ 4. Assertion        ┌──────────┐
     │ /ID Token           │   IdP    │  (Identity Provider /
     └────────────────────▶│  (Okta,  │   OpenID Provider)
                           │  Entra)  │
                           └──────────┘
                                 │
                                 ▼ 3. Authenticate user
                              (MFA, biometric, password)
```

- **IdP** owns the user directory and authenticates. SAML: signs an XML assertion. OIDC: issues an ID Token (JWT).
- **SP** (or RP) trusts the IdP's signed claim, establishes a local session.
- **Federation** = IdP-to-IdP trust delegation (corporate IdP federates to a partner's IdP).
- **SAML still dominates install base** in F500 enterprises (XML metadata exchange, ADFS, Shibboleth, Ping); **OIDC dominates new integrations** (discovery via `.well-known/openid-configuration`, JWKS-based key rotation, mobile-friendly with PKCE).

Per-organization SSO config is what makes B2B SaaS scalable: each customer org has its own IdP connection, attribute mapping, signing key.

## 9. IGA — Identity Governance and Administration

Gartner defines IGA as "the solution to manage the identity life cycle and govern access across on-premises and cloud environments" ([Gartner IGA](https://www.gartner.com/reviews/market/identity-governance-administration)). Core capabilities:

1. **Provisioning / deprovisioning** — automated connectors (SCIM where available, ITSM-triggered manual flows otherwise) tied to HR joiner-mover-leaver events.
2. **Access requests** — self-service request → approval workflow → fulfillment.
3. **Access certifications / reviews** — periodic attestation that current entitlements remain justified.
4. **Entitlement management** — catalog of granular permissions with descriptions, owners, sensitivity ratings.
5. **Role management / role mining** — discover roles from existing access patterns; manage role lifecycle.
6. **SoD enforcement** — preventive (block conflicting grants) and detective (find existing conflicts).

Vendors: SailPoint, Saviynt, Oracle Identity Governance, IBM Security Verify Governance, One Identity, Omada, Symantec IGA, Pathlock.

## 10. PAM — Privileged Access Management

PAM secures the high-blast-radius accounts: root, domain admin, DBA, AWS root, break-glass. Core capabilities ([CyberArk](https://cyberark.com/products/privileged-access-manager)):

- **Credential vault** — tamper-proof storage with policy-based rotation; credentials never exposed to end users.
- **Session isolation and recording** — Privileged Session Manager proxies sessions; video/keystroke recording for forensics ([PSM docs](https://docs.cyberark.com/pam-self-hosted/latest/en/content/pasimp/privileged-session%20manager-introduction.htm)).
- **Just-in-time elevation** — ephemeral local user creation with time-bound permissions, ABAC-tagged resources.
- **Zero standing privileges mode** — no permanent admin group membership; permissions injected per session.
- **Discovery** — find all privileged accounts, keys, secrets across on-prem, cloud, OT/ICS.
- **Threat detection** — anomaly detection on session behavior.

Vendors: CyberArk, BeyondTrust, Delinea (Thycotic+Centrify), HashiCorp Boundary, Teleport.

## 11. CIEM — Cloud Infrastructure Entitlement Management

Coined by Gartner in 2020. The problem: cloud permission space is enormous (AWS IAM has ~17,000 distinct actions; Azure RBAC ~10,000+; GCP thousands more), and **>90% of granted cloud permissions go unused** ([CloudQuery 2026](https://www.cloudquery.io/learning-center/ciem); [Sysdig: 98% of granted cloud permissions unused](https://sysdig.com/solutions/permissions-entitlement-management)).

Effective permissions in AWS alone resolve six policy layers: identity-based policies, resource-based policies, permissions boundaries, SCPs, session policies, VPC endpoint policies. No human can reason about this at scale.

**Core CIEM capabilities** (per AWS, Gartner, Sysdig):
1. **Rightsizing** — compare actual usage (CloudTrail/Audit Logs/Activity Logs) vs. granted permissions; recommend least-privilege policies.
2. **Anomaly detection** — flag unusual behavior (e.g., a service account suddenly calling unfamiliar APIs).
3. **Visualization** — graph who can access what across multi-cloud.
4. **Compliance reporting** — map entitlements to frameworks.

Native tools: AWS IAM Access Analyzer (unused-access analyzer, external-access analyzer, policy generation from CloudTrail), Azure Entra Permissions Management (formerly CloudKnox), GCP Policy Analyzer. Third-party: Sysdig, Wiz, Orca, Sonrai, Ermetic (now Tenable), Permiso.

## 12. Non-Human / Workload Identity

The fastest-growing identity category. Service accounts, IAM roles, API keys, bots, CI/CD pipelines, agents — increasingly outnumber human identities 10:1 to 50:1.

**SPIFFE** (Secure Production Identity Framework for Everyone) — CNCF spec for platform-agnostic workload identity ([spiffe.io](https://spiffe.io/docs/latest/spiffe-specs/spiffe-id/)). Key concepts:
- **SPIFFE ID** — RFC 3986 URI: `spiffe://trust-domain/path` (e.g., `spiffe://example.com/ns/staging/sa/default`).
- **SVID** (SPIFFE Verifiable Identity Document) — cryptographically verifiable doc proving identity. Two formats: X.509-SVID (cert) and JWT-SVID.
- **Trust domain** — namespace under a signing authority.
- **SPIFFE Federation** — bundle endpoints expose trust bundles so workloads across trust domains can authenticate each other.

**SPIRE** is the reference SPIFFE implementation (SPIRE Server + SPIRE Agents on each node). Adopted by HPE, Bloomberg, Pinterest, Uber.

**Workload Identity Federation** (cloud-native) — eliminates long-lived service-account keys. [Google Cloud Workload Identity Federation](https://docs.cloud.google.com/iam/docs/workload-identity-federation) lets external workloads (AWS, Azure, on-prem AD, GitHub, GitLab, any OIDC/SAML IdP) exchange their native credentials for short-lived GCP access tokens via OAuth 2.0 token exchange. AWS has analogous OIDC-federated IAM role assumption. The pattern is now standard for GitHub Actions → cloud deploys.

## 13. Compliance Drivers

| Framework | Type | Access-Control Requirement |
|-----------|------|---------------------------|
| **SOC 2** (AICPA) | Attestation, Trust Services Criteria | CC6.1: logical access controls, RBAC, provisioning/deprovisioning, MFA, periodic review |
| **ISO/IEC 27001** | Certification (ISMS) | Annex A.5.15 (access control), A.5.16 (identity mgmt), A.5.18 (access rights), A.8.2 (privileged access) |
| **HIPAA Security Rule** (US) | Regulation | §164.312(a) unique user IDs, automatic logoff, emergency access; §164.312(b) audit controls |
| **SOX** (US public co.) | Regulation, financial reporting | SoD on financial systems; ITGCs covering access provisioning, periodic review, deprovisioning |
| **PCI-DSS v4.0** | Standard | Reqs 7 (need-to-know), 8 (unique IDs + MFA), 10 (audit trails) — most prescriptive |
| **GDPR** | EU regulation | Art. 5 (purpose limitation), Art. 32 (security: access by need); breach notification 72h |
| **FedRAMP / NIST 800-53** | US federal | AC family (AC-2 account mgmt, AC-3 enforcement, AC-5 SoD, AC-6 least privilege, AC-17 remote) |

Per [Adaptive's access mapping](https://www.adaptive.live/blog/access-security-requirements-across-major-compliance-frameworks): least privilege, RBAC, unique user ID, session timeout, access logging, privileged access restrictions are **required by every major framework**. MFA is required by HIPAA, PCI-DSS, NIST, CMMC, SOC 2; recommended by ISO 27001 and GDPR.

~60-70% of controls overlap between SOC 2, ISO 27001, and GDPR — which is why GRC platforms (Vanta, Drata, Secureframe, Anecdotes) sell on "implement once, certify many."

## 14. Audit Logging — The "Who Did What When"

Required by every major framework. The canonical fields ([AWS CloudTrail](https://docs.aws.amazon.com/IAM/latest/UserGuide/cloudtrail-integration.html), [GCP Cloud Audit Logs](https://cloud.google.com/logging/docs/audit)):

- `eventTime`, `eventName`, `eventSource`
- `userIdentity` — principal type (IAM user, AssumedRole, root, federated), ARN, MFA-authenticated flag, session issuer
- `sourceIPAddress`, `userAgent`
- `requestParameters`, `responseElements`
- `mfaAuthenticated`, `sessionContext`

GCP splits into Admin Activity (always on, free), Data Access (opt-in, can be expensive), System Event, Policy Denied. AWS CloudTrail logs all IAM/STS API calls including federated principal `AssumeRoleWithSAML` / `AssumeRoleWithWebIdentity` events, letting you trace SaaS → cloud actions back to the human.

The forensic pattern: SIEM (Splunk, Elastic, Chronicle, Sumo) ingests audit logs from IdP + cloud + apps; correlation rules + UEBA flag anomalies; logs feed quarterly access reviews and incident response. The hard problem isn't generating logs — it's correlating *identity-across-systems* so that an action in Salesforce, AWS, and GitHub by the same human can be traced as one chain.

## 15. Practical Enterprise Failure Modes

Documented across multiple sources ([Clarity Security](https://claritysecurity.com/clarity-blog/why-managers-rubberstamp-uars/), [OpenIAM](https://www.openiam.com/blog/reduce-access-review-fatigue-regulated-enterprises), [Linx Security](https://www.linx.security/blog/user-access-reviews-access-certifications-why-they-fail-and-how-to-fix-them), [Zluri](https://www.zluri.com/blog/modern-identity-strategy)):

1. **Role explosion** — the European bank case (50,000 employees, 1,400 branches, ~1,300 roles discovered) is the canonical example. Every contextual nuance becomes a new role; the role catalog becomes unmanageable. Fix: ABAC overlays on RBAC, or ReBAC for resource-level permissions.

2. **Privilege creep** — entitlements are durable, intent is ephemeral. Devs get "temporary" admin for an incident; six months later the access remains. NIST AC-6(7) mandates periodic privilege review specifically to counter this.

3. **Stale entitlements / orphaned accounts** — ex-employees, former contractors, decommissioned-app service accounts still active. SCIM deprovisioning closes most of this, but apps without SCIM (long tail) require ITSM tickets and inevitably leak.

4. **Shadow IT** — SaaS apps adopted without IT involvement. Browser extensions, finance-system OAuth integrations, and SSO discovery tools (Zluri, Nudge Security, Torii) are needed to inventory.

5. **Rubber-stamp access reviews** — reviewers face hundreds-to-thousands of entitlements per cycle with no context; default approve. Mass approvals "occurring within minutes of campaign launch" is the tell. Causes: review fatigue, no context on what an entitlement actually does, no risk differentiation, fear of breaking production. Fixes: risk-based scoping, event-driven reviews (job changes, inactivity), usage data alongside entitlement, peer comparison, pre-review cleanup of obvious stale access.

6. **The new-enemy problem** — when ACL changes and content changes aren't causally ordered, revoked users can still see content modified after their revocation. Solved at scale only by systems like Zanzibar with external-consistency guarantees.

7. **Cloud permissions explosion** — 40,000+ IAM policies in a single AWS org is now common; most permissions unused. CIEM is the response category.

8. **Service account key sprawl** — long-lived static credentials in source control, CI/CD configs, kubernetes secrets. Workload identity federation + SPIFFE is the modern remediation.

9. **Joiner-mover-leaver mover gap** — provisioning at hire works; offboarding at termination works (mostly); but role *changes* leave behind old access. "Mover" is the weakest link in JML automation.

10. **Implicit "additive only" culture** — granting is fast and rewarded; revoking causes outages and is socially penalized. Counter with rollback mechanisms ("removed but easy-to-restore") so revocation feels cheap.

---

## Sources (Primary)

- [Ferraiolo & Kuhn, 1992 — Role-Based Access Controls (NIST)](https://csrc.nist.gov/files/pubs/conference/1992/10/13/rolebased-access-controls/final/docs/ferraiolo-kuhn-92.pdf)
- [Sandhu, Coyne, Feinstein, Youman, 1996 — Role-Based Access Control Models](https://csrc.nist.gov/csrc/media/projects/role-based-access-control/documents/sandhu96.pdf)
- [Sandhu, Ferraiolo, Kuhn, 2000 — The NIST Model for RBAC](https://www.nist.gov/publications/nist-model-role-based-access-control-towards-unified-standard)
- [NIST RBAC FAQ / ANSI INCITS 359-2004](https://csrc.nist.gov/Projects/role-based-access-control/faqs)
- [NIST SP 800-53 Rev 5 — Security and Privacy Controls](https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final)
- [NIST SP 800-162 — Guide to ABAC](https://nvlpubs.nist.gov/nistpubs/specialpublications/NIST.SP.800-162.pdf)
- [NIST SP 800-192 — Verification and Test Methods for Access Control Policies](https://nvlpubs.nist.gov/nistpubs/specialpublications/nist.sp.800-192.pdf)
- [NIST SP 800-207 — Zero Trust Architecture](https://nvlpubs.nist.gov/nistpubs/specialpublications/NIST.SP.800-207.pdf)
- [NIST CSWP 20 — Planning for a Zero Trust Architecture](https://nvlpubs.nist.gov/nistpubs/CSWP/NIST.CSWP.20.pdf)
- [Pang et al., 2019 — Zanzibar: Google's Consistent, Global Authorization System (USENIX ATC)](https://www.usenix.org/system/files/atc19-pang.pdf)
- [OAuth 2.1 draft-ietf-oauth-v2-1](https://datatracker.ietf.org/doc/draft-ietf-oauth-v2-1/)
- [SPIFFE specifications](https://spiffe.io/docs/latest/spiffe-specs/spiffe-id/)
- [Google Cloud Workload Identity Federation](https://docs.cloud.google.com/iam/docs/workload-identity-federation)
- [AWS IAM Access Analyzer / CloudTrail docs](https://docs.aws.amazon.com/IAM/latest/UserGuide/what-is-access-analyzer.html)
- [Gartner IGA Market Guide 2025](https://origin.oneidentity.com/analyst-report/2025-gartner-market-guide-for-identity-governance-and-administration/)
- [CyberArk PAM product docs](https://cyberark.com/products/privileged-access-manager)
- [AuthZed annotated Zanzibar paper](https://zanzibar.tech/)
- [Compliance-frameworks access control mapping (Adaptive)](https://www.adaptive.live/blog/access-security-requirements-across-major-compliance-frameworks)

## Next Steps
- [x] Findings saved as scratchpad foundation for major report.
