# Alternative Online Community Governance Models

How other platforms govern themselves, and what Reddit can learn from each.

---

## The Governance Landscape at a Glance

```
                    CENTRALIZED CONTROL
                          |
               Facebook Groups / Twitch
                          |
                       Reddit
                          |
            Stack Overflow / Wikipedia
                          |
                       Discord
                          |
               Mastodon / Fediverse
                          |
                        4chan
                          |
                  MINIMAL GOVERNANCE
```

This is a rough spectrum. The interesting insight is that Reddit sits in a strange middle zone -- more structured than Discord, less democratic than Wikipedia, more federated than Facebook, but less so than Mastodon. That ambiguity is both its strength and its vulnerability.

---

## 1. Wikipedia

**Model:** Democratic bureaucracy with elected administrators, bureaucrats, and a supreme arbitration committee (ArbCom).

### Who Has Power and How They Get It

Wikipedia operates on a tiered system of escalating authority, all rooted in community election:

| Role | How Acquired | Key Powers |
|------|-------------|------------|
| **Editor** | Anyone with an account | Edit articles, participate in discussions |
| **Administrator** | Elected via Request for Adminship (RfA) -- community vote, ~65-80% approval needed | Delete/protect pages, block users, edit protected pages |
| **Bureaucrat** | Elected via community process (Request for Bureaucratship) | Grant/revoke admin status, rename accounts |
| **Arbitration Committee** | Elected annually by the community | Final binding dispute resolution, impose sanctions, topic bans |

The Request for Adminship (RfA) process is remarkably transparent. Any editor can nominate themselves or be nominated. The entire community can vote (support, oppose, neutral) and must provide written rationale. Bureaucrats evaluate consensus -- not just raw numbers -- to determine the outcome. Candidates are typically long-term editors with thousands of edits and years of experience. No candidate has ever been appointed who was not already an administrator.

### Checks on Power

- **Transparency:** All admin actions are logged and publicly visible. Any editor can challenge an admin action.
- **Community recall:** Admins can be desysopped (stripped of tools) through community consensus or ArbCom.
- **ArbCom scope limits:** ArbCom explicitly cannot make content decisions -- they only adjudicate conduct disputes. They cannot subvert community consensus.
- **Escalation ladder:** Arbitration is a last resort. Disputes must go through discussion, mediation, and other processes first.
- **Annual elections:** ArbCom members serve fixed terms and face re-election.

### How Disputes Are Resolved

Wikipedia has the most formalized dispute resolution process of any community platform:

```
Dispute arises
      |
      v
Talk page discussion (between editors)
      |
      v
Third-party input (noticeboards, WikiProjects)
      |
      v
Request for Comment (RFC) -- broader community input
      |
      v
Mediation (informal or formal)
      |
      v
Arbitration Committee (binding, final)
```

ArbCom can impose sanctions ranging from topic bans to editing restrictions to indefinite blocks. Their decisions include detailed "findings of fact" and "remedies" -- closer to judicial opinions than moderation actions.

### Platform-Community Relationship

The Wikimedia Foundation (WMF) owns the infrastructure but has historically deferred to the community on governance. This separation is unusual and significant. The WMF can intervene in extreme cases (legal threats, Terms of Use violations) but generally does not override community-elected bodies. There have been tensions -- notably around the WMF's 2023 Universal Code of Conduct -- but the principle of community sovereignty remains strong.

### What Reddit Could Learn

Wikipedia proves that democratic legitimacy in online governance is possible at scale. The key elements Reddit lacks:
- **Elected moderators** with transparent selection processes
- **An appeals body** independent of the moderator who made the decision
- **Documented escalation paths** that users can actually navigate
- **Scope limits on power** -- ArbCom cannot make content decisions, only conduct decisions

### What Makes Wikipedia Different

Wikipedia's governance works because it has a singular shared mission (building an encyclopedia) that constrains the scope of governance decisions. Reddit's subreddits each have different purposes, making a universal governance framework harder to impose.

---

## 2. Discord

**Model:** Server feudalism -- absolute owner authority within a decentralized network of independent servers.

### Who Has Power and How They Get It

| Role | How Acquired | Key Powers |
|------|-------------|------------|
| **Server Owner** | Creates the server | Absolute power -- all permissions, cannot be overridden by anyone except Discord itself |
| **Administrator** | Appointed by owner | Near-full power, but owner can revoke at will |
| **Moderator** | Appointed by owner/admin | Manage messages, kick/ban users, mute -- as configured by owner |
| **Custom Roles** | Configured by owner | Granular permission system allows any combination of powers |

Discord's permission system is the most granular of any major platform. Owners can create unlimited custom roles with fine-tuned permissions per channel. This means governance structures vary wildly from server to server -- some run like democracies with community input, others like dictatorships.

### Checks on Power

- **Exit:** Users can leave any server instantly. The primary check on power is competition for members.
- **Discord ToS:** Discord itself can shut down servers or ban users for ToS violations, but this is rare and reactive.
- **No democratic mechanisms built in:** There is no election system, no appeals process, no community override. Any checks are voluntarily implemented by the owner.
- **Role hierarchy:** Lower roles cannot act on higher roles, creating a clear chain of command.

### How Disputes Are Resolved

There is no formal dispute resolution. It depends entirely on what the server owner has set up. In practice:
- Most disputes are resolved by moderator fiat
- Appeals go to the server owner, who is the final authority
- If users disagree, their option is to leave and start their own server
- Discord's Trust & Safety team handles only ToS violations, not internal community disputes

### Platform-Community Relationship

Discord provides infrastructure and enforces ToS, but is otherwise hands-off. There is no centralized content feed, no algorithmic recommendation of servers, and no mechanism for Discord to influence internal server governance. Each server is truly independent in a way that subreddits are not -- Discord does not share users' activity across servers or recommend content from one server to another.

### What Reddit Could Learn

- **Granular permissions:** Discord's role system is far more sophisticated than Reddit's binary mod/non-mod distinction. Subreddits could benefit from configurable permission tiers.
- **Channel-level governance:** Discord allows different rules per channel within a server. Subreddits are monolithic.

### The Feudalism Problem

Discord's model works for small-to-medium communities but creates the same accountability gaps as Reddit for large servers. A 500,000-member Discord server with an abusive owner has no recourse mechanisms. The "just leave" principle fails when the server is the only place for a particular community (e.g., a game's official Discord).

---

## 3. Mastodon / Fediverse

**Model:** True digital federalism -- independent instances connected by protocol, each with sovereign governance, linked by voluntary federation.

### Who Has Power and How They Get It

| Role | How Acquired | Key Powers |
|------|-------------|------------|
| **Instance Admin** | Sets up and funds the server | Full control over instance rules, moderation policy, federation decisions |
| **Moderators** | Appointed by admin | Enforce instance rules, handle reports |
| **Users** | Create an account on an instance | Choose which instance to join; can migrate to another |

The crucial difference: governance is at the instance level, not the platform level. There is no "Mastodon Inc." that controls the network. Each instance is an independent server running compatible software (ActivityPub protocol).

### Checks on Power

The fediverse has the most radical check on power: **defederation**.

```
Instance A ←→ Instance B ←→ Instance C
     |                           |
     |    Instance B goes bad    |
     |                           |
Instance A ──X── Instance B ──X── Instance C
                 (defederated)
```

- **Defederation:** Any instance can cut off communication with any other instance. If an instance tolerates abuse, other instances block it entirely. This is digital exile -- and it works.
- **User migration:** Users can move their account (and followers) to a different instance. This is "exit" with lower switching costs than most platforms.
- **Financial accountability:** Many instances are funded by user donations or cooperatives. Admins who abuse power lose funding.
- **Code is open source:** Anyone can fork the software and start a competing instance.

According to the Kissane & Kazemi (2024) governance study, the most effective fediverse instances use a mix of:
- Published codes of conduct
- Transparent moderation logs
- Community input on federation/defederation decisions
- Shared blocklists curated collaboratively across instances

### How Disputes Are Resolved

- **Within an instance:** Admin/mod decision, similar to any other platform
- **Between instances:** Diplomacy. Instance admins communicate directly, often through admin-only channels. If diplomacy fails, defederation is the nuclear option.
- **No central appeals body:** There is no "fediverse Supreme Court." Each instance is sovereign.

The Carnegie Endowment (2025) report on defederation notes that this creates a "trust and safety" challenge: there are no standardized processes, and the burden of moderation decisions falls heavily on volunteer admins who often lack resources.

### Platform-Community Relationship

There is no platform company. The relationship is between users and their instance admin. Some instances are run by individuals, some by nonprofits, some by cooperatives. The Mastodon software project (led by Eugen Rochko) develops the code but has no control over instances running it.

### What Reddit Could Learn

- **Defederation as accountability:** The idea that communities can sever ties with bad actors is powerful. Reddit has nothing equivalent -- subreddits cannot "defederate" from other subreddits.
- **Instance-level sovereignty with network effects:** The fediverse proves you can have independent governance without losing network connectivity.
- **Portability:** Account migration means users are not locked in. Reddit users cannot take their karma, history, or followers to another platform.

### The Fediverse's Weakness

Scale. The fediverse governance model works well for small-to-medium instances (hundreds to low thousands of users). Large instances (mastodon.social with 200k+ users) face many of the same governance challenges as centralized platforms. The Kissane & Kazemi report found that most well-governed instances are in the 500-5,000 user range.

---

## 4. Stack Overflow

**Model:** Meritocratic reputation system with earned privileges and elected diamond moderators.

### Who Has Power and How They Get It

Stack Overflow's governance is uniquely tied to demonstrated contribution:

| Reputation | Privilege Unlocked |
|-----------|-------------------|
| 1 | Ask/answer questions |
| 15 | Flag posts, upvote |
| 50 | Comment anywhere |
| 125 | Downvote |
| 500 | Access review queues |
| 2,000 | Edit any post |
| 3,000 | Vote to close/reopen |
| 10,000 | Access moderator tools, view deleted posts |
| 20,000 | Vote to delete questions |
| **Elected** | Diamond moderator -- binding votes, user suspension, tag management |

This is the closest thing to a "governance ladder" in any major platform. Power is earned through contribution, and each level grants specific, well-defined capabilities.

Diamond moderators are elected by the community in formal elections. Candidates must meet a minimum reputation threshold (typically 3,000+), answer a questionnaire, and participate in a community Q&A period. Elections use a single transferable vote (STV) system.

### Checks on Power

- **Graduated privileges:** No single user has outsized power until they have demonstrated sustained, quality contribution.
- **Collective action:** Most moderation actions (close votes, delete votes) require multiple users to agree. A single user with 3,000 rep cannot close a question alone -- it takes 5 close votes.
- **Meta governance:** Stack Overflow Meta is a separate site where governance policies are debated and decided by community consensus.
- **Elected moderators are accountable:** Diamond mods can be removed by Stack Exchange staff or through community processes.
- **Transparent moderation:** All close/reopen/delete actions are visible and reversible.

### How Disputes Are Resolved

```
User disagrees with action
        |
        v
Meta post (community discussion)
        |
        v
Diamond moderator review
        |
        v
Stack Exchange Community Team (staff)
        |
        v
Stack Exchange leadership (rare)
```

### Platform-Community Relationship

This is where Stack Overflow's model shows cracks. Stack Exchange (the company) has overridden community consensus multiple times, most notably:
- **2019 Monica Cellio incident:** SE fired a diamond moderator without due process, sparking a moderator strike.
- **2023 AI content policy:** SE imposed a blanket ban on AI-generated content against the wishes of some communities, triggering another moderator/contributor strike (documented in Wu et al., 2025 arXiv paper).

These incidents reveal the tension: the community builds the content and governs day-to-day, but the company owns the platform and can unilaterally override community governance when corporate interests diverge.

### What Reddit Could Learn

- **Graduated privileges:** Tying moderation power to demonstrated contribution is elegant and reduces the "random person with a subreddit" problem.
- **Collective moderation:** Requiring multiple users to agree on actions (close votes) prevents individual abuse.
- **Formal elections:** Stack Overflow's moderator elections with STV voting are more legitimate than Reddit's "whoever creates the subreddit" model.

### The Meritocracy Trap

Stack Overflow's reputation system can calcify into an oligarchy. High-rep users accumulate privileges that make it easier to gain more reputation. New users face steep barriers. The system rewards a specific type of contribution (technical Q&A) and marginalizes others. Jeff Atwood's original "A Theory of Moderation" (2009) envisioned moderators as "human exception handlers" -- intervening only when the system fails. In practice, power has concentrated more than intended.

---

## 5. Twitch

**Model:** Creator-owned channels with appointed moderators, nested within a corporate platform.

### Who Has Power and How They Get It

| Role | How Acquired | Key Powers |
|------|-------------|------------|
| **Streamer (Broadcaster)** | Creates a channel | Full control over channel rules, mod appointments, bans |
| **Lead Moderator** | Appointed by streamer (introduced 2025) | Elevated mod role, can manage other mods |
| **Moderator** | Appointed by streamer | Timeout/ban users, delete messages, slow mode, manage chat |
| **VIP** | Appointed by streamer | Bypass slow mode/sub-only mode, cosmetic badge |
| **Subscriber** | Pays monthly fee | Emotes, chat privileges as configured |

### Checks on Power

- **Twitch ToS:** Twitch enforces platform-wide rules and can suspend streamers or their channels.
- **DMCA and legal compliance:** Twitch acts on legal obligations regardless of streamer wishes.
- **Hate raid protections:** After high-profile harassment campaigns (2021), Twitch implemented platform-level tools (phone verification, shield mode) that streamers can activate but cannot disable at a platform level.
- **No community override:** Viewers have no formal mechanism to challenge a streamer's moderation decisions.

### How Disputes Are Resolved

- **Within a channel:** Streamer decides. Period.
- **Against a streamer:** Report to Twitch Trust & Safety. Twitch investigates and may issue warnings, suspensions, or permanent bans.
- **Between mods and streamers:** Research by Cai et al. (2023, CHI) documents frequent conflicts between moderators and streamers, particularly around inconsistent rule enforcement and emotional labor. Resolution is informal and often results in the moderator leaving.

### Platform-Community Relationship

Twitch is more involved than Discord or Reddit in day-to-day governance. Twitch's Partner and Affiliate programs create a financial relationship with streamers that gives Twitch leverage. Streamers who violate ToS risk losing their income stream, not just their community. This economic lever is a powerful governance tool that Reddit lacks (Reddit mods are unpaid).

### What Reddit Could Learn

- **Clear ownership:** Twitch channels have unambiguous ownership. The streamer created the content, built the audience, and has clear authority. Reddit's ambiguity about who "owns" a subreddit (the creator? the community? Reddit?) is a source of constant conflict.
- **Economic alignment:** Twitch streamers have financial incentives to maintain healthy communities. Reddit mods have no such alignment.

### The Creator Problem

Twitch's model works because channels are organized around a single creator. Subreddits are organized around topics, not people. Applying Twitch's ownership model to Reddit would be like saying one person "owns" the topic of r/science.

---

## 6. 4chan

**Model:** Minimal moderation as governance philosophy, with anonymous participation and ephemeral content.

### Who Has Power and How They Get It

Contrary to the popular "no moderation" narrative, 4chan does have a governance structure -- it was just secret until the 2025 breach:

| Role | How Acquired | Key Powers |
|------|-------------|------------|
| **Site Owner** | Owns the site (currently Hiroyuki Nishimura) | Ultimate authority |
| **Managers** | Appointed by owner | Oversee moderation staff |
| **Moderators** | Recruited privately, often from existing users | Delete posts, ban users (by IP), manage threads |
| **Janitors** | Applied and vetted privately | Delete posts and report to mods, cannot ban |

The 2025 breach (documented by OSINord) revealed that 4chan had approximately 100+ janitors and moderators, many of whom had served for years. The moderation team was organized through private IRC channels and internal dashboards.

### Checks on Power

Essentially none beyond the site owner's discretion:
- **No transparency:** Users cannot see who moderates or why posts are removed.
- **No appeals:** There is no appeals process. Bans are IP-based and easily circumvented via VPN, which itself reduces the stakes.
- **No accountability:** Moderators are anonymous to users. The 2025 breach was the first time the public learned the identities of 4chan's moderation team.
- **Ephemerality as governance:** Content automatically expires. Threads that are not bumped fall off the board. This is a form of governance-by-architecture -- the software itself limits the persistence of harmful content.

### How Disputes Are Resolved

They are not resolved. There is no dispute resolution mechanism. Users who are banned can evade the ban trivially. Content that is deleted is simply gone. The philosophy is that the chaos is the feature.

### Platform-Community Relationship

4chan is a rare case where the platform owner has minimal financial incentive to moderate. The site runs on minimal ad revenue, the owner is not accountable to advertisers or investors in the way that Reddit is, and the culture explicitly resists moderation as censorship.

### What Reddit Could Learn

4chan demonstrates the consequences of minimal governance: it is simultaneously a crucible of internet culture and a breeding ground for extremism. "4chan's Law" (coined by users themselves) states that any minimally moderated forum will trend toward extreme or controversial viewpoints. This happens through self-selection -- moderate voices leave, extreme voices stay and amplify each other.

The lesson for Reddit is that governance is not optional at scale. The question is not whether to govern, but how.

### The Anonymity Factor

4chan's governance challenges are inseparable from its anonymity. Without persistent identity, reputation systems are impossible, social consequences are nonexistent, and community memory cannot form. Reddit's pseudonymous identity (persistent usernames, karma, post history) provides a governance foundation that 4chan structurally cannot have.

---

## 7. Facebook Groups

**Model:** Admin/moderator hierarchy within a tightly controlled corporate platform.

### Who Has Power and How They Get It

| Role | How Acquired | Key Powers |
|------|-------------|------------|
| **Group Creator** | Creates the group | Full admin privileges, cannot be removed |
| **Admin** | Appointed by creator or another admin | Manage members, approve/deny posts, remove members, appoint mods, change group settings |
| **Moderator** | Appointed by admin | Approve/deny posts, remove posts, mute members -- but cannot change settings or remove admins |
| **Member** | Joins (or is approved, in private groups) | Post, comment, react |

### Checks on Power

- **Meta/Facebook oversight:** Facebook enforces Community Standards across all Groups. Groups that violate standards can be removed entirely.
- **Algorithmic demotion:** Facebook can reduce a Group's visibility in recommendations and search if it accumulates violations.
- **Admin redundancy:** Multiple admins can check each other, but the group creator has ultimate authority.
- **Reporting mechanisms:** Members can report content and groups directly to Facebook, bypassing group admins.
- **Group Quality program:** Facebook requires admins of large groups to manage content or risk the group being archived or removed.

### How Disputes Are Resolved

- **Within a group:** Admin decision.
- **Against an admin:** Report to Facebook. No internal community mechanism.
- **Facebook Oversight Board:** For content moderation decisions made by Facebook itself (not group admins), the Oversight Board provides independent review. This is the closest thing to a "Supreme Court" for platform governance, but it does not extend to group-level decisions.

### Platform-Community Relationship

Facebook Groups exist within the most controlled platform ecosystem of any model discussed here. Facebook:
- Controls the algorithmic distribution of group content
- Can and does remove groups unilaterally
- Requires real-name identity (in theory)
- Collects data on all group activity for advertising purposes
- Can insert "context labels" on content within groups

Group admins have less actual autonomy than Reddit moderators. They cannot customize the platform, cannot use bots or automation (beyond Facebook's built-in tools), and cannot prevent Facebook from inserting content or notifications into their group.

### What Reddit Could Learn

- **Platform-level quality enforcement:** Facebook's willingness to archive or remove low-quality groups is something Reddit has historically been reluctant to do with subreddits.
- **Oversight Board model:** An independent body reviewing moderation decisions is a governance innovation worth studying, even if Facebook's implementation is imperfect.
- **Real identity reduces (some) toxicity:** Facebook Groups generally have less extreme content than Reddit, partly because of identity requirements (though this comes with privacy tradeoffs).

### The Walled Garden Problem

Facebook Groups illustrate the failure mode of excessive centralization. Group admins are essentially middle managers within Facebook's corporate hierarchy. They can be overridden at any time, their tools are limited to what Facebook provides, and their communities exist entirely at Facebook's discretion. This creates learned helplessness -- admins invest less in governance because they know they do not truly control anything.

---

## Comparative Analysis

### The Power Matrix

| Platform | Who holds power? | How is it acquired? | Can it be checked? | Can it be removed? |
|----------|-----------------|--------------------|--------------------|-------------------|
| **Wikipedia** | Elected admins, ArbCom | Community election | Yes -- transparency, community recall | Yes -- community process |
| **Discord** | Server owner | Creates server | No formal checks | Only by Discord ToS |
| **Mastodon** | Instance admin | Runs the server | Defederation, user migration | Users leave, instance dies |
| **Stack Overflow** | Rep-holders, elected mods | Contribution + election | Collective voting, Meta | Company override, election |
| **Twitch** | Streamer | Creates channel | Twitch ToS | Twitch suspension |
| **4chan** | Anonymous mod team | Private appointment | None | Owner discretion |
| **Facebook Groups** | Group creator/admins | Creates group | Facebook oversight | Facebook removal |
| **Reddit** | Subreddit creator/mods | Creates sub or appointed | Very few | Admin intervention (rare) |

### The Dispute Resolution Spectrum

```
Formal                                                    Informal
  |                                                          |
  Wikipedia ---- Stack Overflow ---- Facebook ---- Reddit ---- Discord ---- Twitch ---- 4chan
  (ArbCom,       (Meta, elected     (Oversight    (no formal  (owner       (streamer   (none)
   multi-step     mods, staff)       Board)        process)    decides)     decides)
   escalation)
```

Reddit is closer to the informal end than most users realize.

### The Accountability Gap

```
                    HIGH ACCOUNTABILITY
                          |
                      Wikipedia
                    (elected, transparent,
                     removable, scoped)
                          |
                    Stack Overflow
                    (elected, collective,
                     but company can override)
                          |
                    Facebook Groups
                    (platform oversight,
                     but limited admin autonomy)
                          |
                      Mastodon
                    (defederation check,
                     but no formal process)
                          |
                       Reddit
                    (almost no checks,
                     rare admin intervention)
                          |
                    Discord / Twitch
                    (owner/creator fiat,
                     only ToS enforcement)
                          |
                        4chan
                    (no accountability)
                          |
                    LOW ACCOUNTABILITY
```

---

## Academic Frameworks

### Key Papers and Concepts

**Tarleton Gillespie, *Custodians of the Internet* (2018):** Foundational text on platform governance. Argues that moderation is not a side effect of platforms -- it IS the platform. Every design choice is a governance choice. The decision to have upvotes, downvotes, karma, subreddits -- these are all governance architecture.

**Seth Frey et al., "Governing Online Goods" (NSF-funded):** Studies governance maturation in Minecraft, Reddit, and World of Warcraft communities. Finds that communities develop increasingly formal governance structures over time, mirroring Elinor Ostrom's principles for governing commons. Reddit communities that survive long-term tend to develop rule systems that map to Ostrom's eight principles (clearly defined boundaries, collective-choice arrangements, monitoring, graduated sanctions, etc.).

**Amy Zhang et al., *PolicyKit* (2020, Stanford/UW):** Built a system for encoding governance processes directly into platform software. Key insight: most platforms hardcode governance into their architecture (Reddit's mod tools ARE the governance system), but communities need the ability to define their own governance processes programmatically. PolicyKit allows communities to create custom governance workflows (e.g., "any mod action on a post with >100 upvotes requires a second mod to approve").

**Robyn Caplan, "Networked Platform Governance" (2023, IJOC):** Argues that platform governance is not a binary between centralized control and community self-governance. Instead, it operates through networks of actors -- platform companies, moderators, users, advertisers, governments -- each with different power and incentives. Reddit is a case study in how these networks create ambiguous authority.

**Kissane & Kazemi, "Governance on Fediverse Microblogging Servers" (2024):** The most comprehensive empirical study of fediverse governance. Key findings:
- Most fediverse admins are solo operators or very small teams
- Effective governance requires community input on major decisions (especially defederation)
- Shared blocklists and collaborative moderation tools are emerging as governance infrastructure
- The biggest threat to fediverse governance is burnout among volunteer admins

**Leon Leibmann et al., "Reddit Rules and Rulers" (2025, ICWSM):** Quantifies the relationship between subreddit rules and community perceptions of governance quality. Finds that more rules do not necessarily mean better governance -- what matters is clarity, consistency, and perceived fairness of enforcement.

**Carnegie Endowment, "Navigating Defederation" (2025):** Analyzes defederation as a trust and safety mechanism. Argues that defederation is a powerful but blunt tool -- it addresses instance-level problems but cannot handle individual bad actors who move between instances.

### Ostrom's Principles Applied to Online Communities

Elinor Ostrom's eight principles for governing commons map remarkably well to successful online communities:

| Ostrom Principle | Online Equivalent | Reddit's Status |
|-----------------|-------------------|-----------------|
| Clearly defined boundaries | Who is a member, what is on-topic | Varies wildly by subreddit |
| Rules match local conditions | Community-specific rules | Strong -- subreddits set own rules |
| Collective-choice arrangements | Members can participate in rule-making | Weak -- mods set rules unilaterally |
| Monitoring | Ability to observe compliance | Moderate -- reports, AutoMod |
| Graduated sanctions | Proportional responses to violations | Weak -- ban is often the only tool |
| Conflict resolution mechanisms | Accessible, low-cost dispute resolution | Very weak -- no formal process |
| Right to organize | Community can create its own governance | Moderate -- limited by platform tools |
| Nested enterprises | Multiple layers of governance | Weak -- subreddit level only |

---

## Synthesis: What Reddit's Model Is Missing

Drawing from all seven models and the academic literature, Reddit's governance has specific structural gaps:

### 1. Democratic Legitimacy (from Wikipedia)
Reddit moderators are not elected. They are self-appointed (created the subreddit) or appointed by existing mods. There is no mechanism for the community to select, evaluate, or remove its leaders.

### 2. Graduated Privileges (from Stack Overflow)
Reddit has a binary: you are a mod or you are not. Stack Overflow's reputation ladder creates a continuum of trust and responsibility. Reddit could implement contribution-based privileges (e.g., trusted users who can flag content, review queues for experienced members).

### 3. Formal Dispute Resolution (from Wikipedia)
Reddit has no appeals process, no escalation path, no independent review body. Wikipedia's multi-step dispute resolution -- from talk pages to mediation to arbitration -- provides a model for what formal process could look like.

### 4. Defederation / Community Sovereignty (from Mastodon)
Reddit communities cannot meaningfully isolate themselves from bad actors in other communities. Cross-subreddit brigading has no structural remedy. The fediverse's defederation model suggests that communities need the ability to control their boundaries.

### 5. Granular Permissions (from Discord)
Reddit's mod tools are a blunt instrument. Discord's per-channel, per-role permission system shows what fine-grained governance tools look like.

### 6. Economic Alignment (from Twitch)
Reddit mods have zero economic incentive to moderate well. Twitch streamers' income depends on community health. Reddit's governance would benefit from some form of alignment between mod effort and mod reward.

### 7. Platform Accountability Infrastructure (from Facebook)
Facebook's Oversight Board -- whatever its flaws -- represents an attempt at independent review of moderation decisions. Reddit has no equivalent institution.

---

## Sources

- Wikipedia:Arbitration -- https://en.wikipedia.org/wiki/Wikipedia:Arbitration
- Wikipedia:Requests for adminship -- https://en.wikipedia.org/wiki/Wikipedia:RFB
- Discord Safety: Developing Moderator Guidelines (2022) -- https://discord.com/safety/developing-moderator-guidelines
- Kissane & Kazemi, "Governance on Fediverse Microblogging Servers" (2024) -- https://fediverse-governance.github.io/
- Carnegie Endowment, "Navigating Defederation on Decentralized Social Media" (2025) -- https://carnegieendowment.org/research/2025/03/fediverse-social-media-internet-defederation/
- Rozenshtein, "Moderating the Fediverse" (2023) -- https://www.journaloffreespeechlaw.org/rozenshtein2.pdf
- Stack Overflow Blog, "A Theory of Moderation" (2009) -- https://stackoverflow.blog/2009/05/18/a-theory-of-moderation/
- Stack Overflow Blog, "Our Theory of Moderation, Re-visited" (2018) -- https://stackoverflow.blog/2018/11/21/our-theory-of-moderation-re-visited/
- Wu et al., "AI Didn't Start the Fire: Examining the Stack Exchange Moderator and Contributor Strike" (2025) -- https://arxiv.org/html/2512.08884v1
- Seering & Kairam, "Who Moderates on Twitch and What Do They Do?" (2023) -- https://dl.acm.org/doi/abs/10.1145/3567568
- Cai et al., "Understanding Moderators' Conflict with Streamers" (2023, CHI) -- https://dl.acm.org/doi/full/10.1145/3544548.3580982
- OSINord, "Inside the Chaos: 4chan's Hidden Power Structure After the 2025 Breach" -- https://www.osinord.com/post/inside-the-chaos-unmasking-4chan-s-hidden-power-structure-after-the-2025-breach
- WIRED, "Inside 4chan's Top-Secret Moderation Machine" (2023) -- https://www.wired.com/story/4chan-moderation-buffalo-shooting/
- Bernstein et al., "4chan and /b/: An Analysis of Anonymity and Ephemerality" (2011, MIT) -- https://www.media.mit.edu/publications/4chan-and-b-an-analysis-of-anonymity-and-ephemerality-in-a-large-online-community-2/
- Gillespie, *Custodians of the Internet* (2018, Yale University Press)
- Frey et al., "Governing Online Goods: Maturity and Formalization in Minecraft, Reddit, and World of Warcraft" -- https://par.nsf.gov/servlets/purl/10451120
- Zhang et al., "PolicyKit: Building Governance in Online Communities" (2020) -- https://arxiv.org/pdf/2008.04236
- Caplan, "Networked Platform Governance" (2023, IJOC) -- https://ijoc.org/index.php/ijoc/article/download/20035/4180
- Leibmann et al., "Reddit Rules and Rulers" (2025, ICWSM) -- https://arxiv.org/abs/2501.14163
- Lee et al., "Mapping Community Appeals Systems" (2025) -- https://joseph.seering.org/papers/Lee_et_al_2025_Appeals_Systems.pdf
