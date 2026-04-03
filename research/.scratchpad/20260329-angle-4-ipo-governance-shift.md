# Angle 4: Reddit's IPO and the Governance Shift

**Research Date:** 2026-03-29
**Status:** Raw findings

---

## 1. Pre-IPO vs Post-IPO Governance: The Pattern

### Timeline of Key Policy Changes

| Date | Event | Direction |
|------|-------|-----------|
| Apr 2023 | API pricing announced ($0.24/1000 calls) | Revenue extraction |
| Jun 2023 | 6,500+ subreddits go dark in protest | Community pushback |
| Jun-Jul 2023 | Reddit forcibly removes protesting mods | Admin control |
| Mar 2024 | IPO at $34/share, $6.4B valuation | Public company begins |
| Feb 2024 | Google content licensing deal ($60M/year) announced same day as IPO filing | Data monetization |
| May 2024 | OpenAI content licensing deal (~$70M/year) | Data monetization |
| Jul 2024 | Moderator Code of Conduct updated with new enforcement rules | Admin control |
| Sep 2024 | Community Types policy: mods must get admin approval to go private/NSFW | Protest suppression |
| Jun 2025 | Reddit sues Anthropic for scraping | Data control |
| Jun 2025 | Mod Code of Conduct Rule 1 updated | Admin control |
| Aug 2025 | Reddit blocks Internet Archive's Wayback Machine from crawling most pages | Data control |
| Sep 2025 | Mod limits announced: max 5 high-traffic communities per mod | Power redistribution |
| Dec 2025 | Mod limit enforcement begins (no new invites if over limit) | Power redistribution |
| Mar 2026 | Full mod limit enforcement: non-compliant mods auto-removed | Power redistribution |

### The Clear Pattern

The trajectory follows a consistent logic:

```
Phase 1 (Pre-IPO, 2023):     Monetize the API → provokes protest
Phase 2 (IPO prep, early 2024): License data to AI companies → monetize content
Phase 3 (Post-IPO, late 2024): Remove ability to protest → lock down governance
Phase 4 (2025-2026):          Break up power mods → atomize resistance
```

Each phase removes a layer of community leverage. The API changes killed third-party tools (which mods relied on). The Community Types policy killed the ability to go dark. The mod limits broke up the "power mod" network that could coordinate action. It is a systematic dismantling of the community's capacity to push back.

---

## 2. Content Licensing Deals: Who Owns Reddit's Content?

### The Deals

- **Google:** $60M/year, announced Feb 2024 (same day as IPO filing). Gives Google real-time access to Reddit's Data API. Google also boosted Reddit in search rankings, nearly tripling readership from 132M to 346M visitors between Aug 2023 and Apr 2024.
- **OpenAI:** ~$70M/year, confirmed May 2024. OpenAI gets access to Reddit's Data API for training and real-time content display in ChatGPT.
- **Next round (2025-2026):** Reddit is negotiating dynamic pricing with Google and OpenAI, proposing a model where Reddit gets paid more as it becomes more vital to AI answers. Also proposing that Google users be encouraged to contribute to Reddit forums, so Google traffic generates content for future training.

### Revenue from data licensing (FY2025)

"Other revenue" (includes data licensing): $140M, up 22% YoY. This is still small relative to $2.1B in ad revenue, but it is growing and carries near-100% margins.

### The Legal Framework: Users Have No Say

Reddit's User Agreement contains an extraordinarily broad license:

> "When Your Content is created with or submitted to the Services, you grant us a worldwide, royalty-free, perpetual, irrevocable, non-exclusive, transferable, and sublicensable license to use, copy, modify, adapt, prepare derivative works of, distribute, store, perform, and display Your Content... This license includes the right for us to make Your Content available for syndication, broadcast, distribution, or publication by other companies, organizations, or individuals who partner with Reddit."

Key implications:
- Users cannot opt out of AI training for content they have already posted
- Reddit confirmed deleted posts/comments are not licensed, but anything posted is immediately available via the Data API
- Users irrevocably waive moral rights and attribution
- Moderators, who curate and organize the content that makes it valuable, have zero say in licensing

### The Anthropic Lawsuit (June 2025)

Reddit sued Anthropic in San Francisco Superior Court, alleging Anthropic scraped Reddit content 100,000+ times even after claiming to have stopped. Reddit demanded restitution and an injunction. The lawsuit frames Reddit's data as proprietary property that must be licensed --- establishing a legal precedent that Reddit, not its users, controls access to user-generated content.

### The Fundamental Irony

Reddit is monetizing a corpus of user-generated content that cost it nothing to produce. The company's primary "product" for AI licensing --- authentic human conversation --- was created by the same volunteer community whose autonomy is being systematically reduced. Users generated the content. Mods organized and curated it. Reddit sells it.

---

## 3. Financial Performance: Are the Governance Changes "Working"?

### Stock Price Trajectory

| Date | Price | Notes |
|------|-------|-------|
| Mar 21, 2024 | $34 (IPO) | Priced at top of range |
| Mar 21, 2024 (close) | ~$50 | Popped 48% on day one |
| Sep 18, 2025 | $270.71 | All-time high closing price |
| Mar 27, 2026 | $121.84 | Current (down ~55% from ATH) |

### Revenue and Profitability

| Metric | FY2024 | FY2025 | Change |
|--------|--------|--------|--------|
| Total Revenue | $1.30B | $2.20B | +69% |
| Ad Revenue | $1.18B | $2.06B | +74% |
| Other Revenue (incl. data licensing) | $115M | $140M | +22% |
| Net Income (Loss) | ($484M) | $530M | Swing of +$1B |
| Adjusted EBITDA | $298M | $845M | +$547M |
| Free Cash Flow | $216M | $684M | +$468M |
| DAUq | 101.7M | 121.4M | +19% |
| Gross Margin | 90.5% | 91.2% | +70bps |

### The Verdict

From a pure business perspective, the governance changes are working spectacularly. Reddit went from a $484M net loss in 2024 to $530M net income in 2025. Revenue grew 69%. Ad revenue grew 74%. The company announced a $1B share repurchase program in Feb 2026. Market cap sits around $25-28B.

The stock's decline from its Sept 2025 all-time high (~$271) to current levels (~$122) likely reflects broader market conditions rather than governance backlash. Reddit's fundamentals are stronger than ever.

---

## 4. The Fundamental Tension: Reddit vs. Every Other Platform

### Reddit's Unique Structural Vulnerability

```
┌──────────────────────────────────────────────────────┐
│                  PUBLIC PLATFORMS                      │
├──────────────┬──────────────┬────────────────────────┤
│   Reddit     │   Meta       │   X (Twitter)          │
├──────────────┼──────────────┼────────────────────────┤
│ Moderation:  │ Moderation:  │ Moderation:            │
│ ~60K unpaid  │ Paid staff + │ Gutted paid staff,     │
│ volunteers   │ AI systems   │ replaced with          │
│              │              │ "Community Notes"      │
│              │              │ (crowdsourced)         │
├──────────────┼──────────────┼────────────────────────┤
│ Content:     │ Content:     │ Content:               │
│ Community-   │ Individual   │ Individual             │
│ organized    │ feed-driven  │ feed-driven            │
│ (subreddits) │ (algorithmic)│ (algorithmic)          │
├──────────────┼──────────────┼────────────────────────┤
│ Protest      │ No mechanism │ Musk fired staff,      │
│ leverage:    │ for          │ advertisers left,      │
│ Mods can     │ collective   │ revenue dropped ~50%   │
│ shut down    │ action       │ in 2023                │
│ content flow │              │                        │
├──────────────┼──────────────┼────────────────────────┤
│ Risk:        │ Risk:        │ Risk:                  │
│ Community    │ Regulatory,  │ Owner instability,     │
│ revolt       │ user fatigue │ advertiser flight      │
└──────────────┴──────────────┴────────────────────────┘
```

### Why Reddit Is Different

1. **Volunteer labor as infrastructure.** Reddit had ~60,000 daily active moderators as of late 2023. A Northwestern study estimated their unpaid labor is worth at least $3.4 million/year (likely a massive undercount at current scale). Meta and X employ paid moderation staff or use AI systems. Reddit's model is uniquely fragile because the workers can walk away.

2. **Community-organized content.** On Meta/X, content is organized algorithmically. On Reddit, subreddits are human-curated knowledge bases. The moderator is not just a janitor --- they are a curator, community builder, and subject matter expert. Losing experienced mods degrades content quality in ways that are difficult to measure but real.

3. **The protest vector.** No other major platform gives unpaid workers the ability to turn off access to content at scale. The June 2023 blackout (6,500+ subreddits going dark) had no equivalent on any other platform. This is why Reddit's Sept 2024 Community Types policy was so significant --- it eliminated this nuclear option.

4. **The IPO risk factor.** Reddit's own S-1 filing explicitly acknowledged that moderator revolts could hurt the business. The company wrote that another protest "could adversely affect our revenue" and noted that "we rely on our communities to self-organize and supplement our site-wide rules."

### Steve Huffman's "Landed Gentry" Comment

During the 2023 API protests, Reddit CEO Steve Huffman compared moderators to "landed gentry" in an interview, suggesting they held too much power and were not representative of average users. This framing was strategically important: it recast the relationship from "valued volunteers who keep the site running" to "entrenched power holders whose authority needs to be checked." The comment was widely received as hostile and remains a sore point with moderators.

---

## 5. Reddit's Moderator Code of Conduct

### History

- **Original Code:** The Moderator Code of Conduct was introduced as a formal policy document, building on earlier informal guidelines. The current version was most recently updated on **June 5, 2025**.
- **July 2024 update:** Introduced clarifications and additional help center articles about the Code's rules. This was the first major update after the IPO.
- **June 2025 update:** Updated Rule 1 ("Create, Facilitate, and Maintain a Stable Community"), tightening expectations.

### The Five Rules

| Rule | Summary | Admin Power |
|------|---------|-------------|
| 1. Create, Facilitate, and Maintain a Stable Community | Mods must enforce Reddit Rules, never create/approve/enable/encourage rule-breaking content | Admins can remove mods, adjust settings, ban communities |
| 2. Set Appropriate and Reasonable Expectations | Accurate descriptions, proper NSFW labeling, clear rules | Admins can adjust subreddit settings |
| 3. Respect Your Neighbors | No coordinating interference in other communities | Admins can suspend accounts |
| 4. Be Active and Engaged | Enough mods, no squatting on communities | Admins can seek new mods or allow adoption |
| 5. Moderate with Integrity | No paid moderation actions, no selling influence | Admins can remove mods, suspend accounts |

### Enforcement Powers

The Code gives admins a sweeping toolkit:
- Issue warnings
- Remove rule-breaking content or subreddit styling
- Remove moderators from communities
- Adjust subreddit settings (NSFW tags, spam filters, content controls)
- Seek new moderators or allow community adoption (effectively hostile takeover)
- Prohibit moderators from joining additional mod teams or creating new subreddits
- Temporary or permanent account suspensions
- Ban entire communities

### How It Has Been Used

The Code was most visibly enforced during the June-July 2023 API protests, when Reddit:
- Sent messages threatening to remove mods who kept subreddits locked
- Forcibly removed moderators from protesting subreddits who refused to reopen
- Warned that marking communities NSFW to avoid ads was "not acceptable"
- Framed ongoing protests as violations of Rule 1 (failing to maintain a stable community)

The Code effectively converts "protest" into a policy violation. By defining a "stable community" as one that is public, active, and accessible, Reddit made the act of going dark or restricting access a Code violation rather than a legitimate form of dissent.

---

## 6. Advertiser Influence on Moderation

### The Revenue Picture

- **FY2025 ad revenue:** $2.06B (93% of total revenue)
- Ad revenue grew 74% YoY
- ARPU (global): $5.98/quarter in Q4 2025, up from $4.21

Reddit is overwhelmingly an advertising business. This creates direct pressure:

### How Advertisers Shape Policy

1. **NSFW restrictions.** Ads cannot run on NSFW-tagged subreddits. During the 2023 protests, moderators weaponized this by marking their subreddits NSFW, directly cutting Reddit's ad revenue. Reddit's response --- requiring admin approval for NSFW status changes (Sept 2024) --- was explicitly motivated by protecting ad inventory.

2. **Brand safety.** Reddit's S-1 acknowledged that harmful content could cause an advertiser exodus, citing the X/Twitter example where 200+ companies pulled or considered pulling ads after Elon Musk's content moderation changes. An analyst quoted in Inc. warned: "If they had something that was incredibly offensive, and had a lot of publicity, you could expect those advertisers to potentially pull out of the platform."

3. **Content moderation as investor concern.** Julian Klymochko (Accelerate Financial Technologies) told Reuters that Reddit's reliance on volunteer moderators is unsustainable for a public company: "It's like relying on unpaid labor when the company has nearly a billion dollars in revenue."

4. **The NSFW balancing act.** Reddit has historically tolerated NSFW content as a community feature. But as a public company dependent on advertising, there is growing tension. In June 2025, Reddit introduced features to let users participate in NSFW communities without throwaway accounts (privacy controls), suggesting an attempt to keep NSFW users engaged while containing brand safety risks.

### The Feedback Loop

```
Advertiser demands brand safety
        │
        ▼
Reddit tightens content controls
        │
        ▼
Mods lose autonomy over NSFW/access settings
        │
        ▼
Community feels less self-governed
        │
        ▼
But revenue grows, stock rises
        │
        ▼
Incentive to continue tightening
```

---

## 7. Synthesis: The Governance Ratchet

### What Reddit Has Built

Reddit has constructed a one-way governance ratchet since the IPO:

1. **Monetize the content** (API pricing, AI licensing deals) without user consent or compensation
2. **Remove the protest mechanism** (Community Types policy requiring admin approval)
3. **Break up organized resistance** (mod limits capping high-traffic communities at 5 per person)
4. **Formalize admin authority** (Moderator Code of Conduct with expansive enforcement powers)
5. **Protect ad revenue** (NSFW restrictions, brand safety controls)

Each step is individually defensible ("we need to protect the community experience" / "power mods have too much control" / "we need to ensure brand safety"). But taken together, they represent a systematic transfer of power from the community to the corporation.

### The Core Contradiction

Reddit's most valuable asset --- authentic human conversation and community-curated knowledge --- exists only because volunteers create and maintain it. The company's post-IPO governance changes are designed to ensure those volunteers can never again threaten the business. But if governance tightening eventually degrades the volunteer experience enough to cause an exodus, the content quality that makes Reddit valuable to advertisers and AI companies degrades with it.

Reddit is betting that:
- Most moderators will accept reduced autonomy because they are emotionally invested in their communities
- The content flywheel is self-sustaining enough to survive moderator turnover
- AI tools can eventually supplement or replace human moderation

### Open Questions

- [ ] At what point does governance tightening degrade content quality enough to matter commercially?
- [ ] Will the mod limits cause an actual exodus, or just grumbling?
- [ ] Can Reddit's AI moderation tools replace the nuanced judgment of experienced human mods?
- [ ] Will Reddit's AI licensing revenue eventually rival or exceed ad revenue?
- [ ] Could a competitor (Lemmy, Tildes, etc.) capture disillusioned Reddit communities at scale?
- [ ] Will the Anthropic lawsuit establish legal precedent that gives Reddit total control over user-generated content?

---

## Sources

- Ars Technica: "In fear of more user protests, Reddit announces controversial policy change" (Sep 2024)
- The Verge: "Reddit is making sitewide protests basically impossible" (Sep 2024)
- Ars Technica: "Mods react as Reddit kicks some of them out again" (Sep 2025)
- CNBC: "Reddit power users balk at chance to participate in IPO" (Mar 2024)
- Mashable: "Reddit's deal with OpenAI is confirmed" (May 2024)
- Columbia Journalism Review: "Reddit Is Winning the AI Game" (Oct 2025)
- Reuters: "Reddit in AI content licensing deal with Google" (Feb 2024)
- Reuters: "Reddit sues AI startup Anthropic" (Jun 2025)
- Reddit Investor Relations: Q4/FY2025 Earnings Release (Feb 2026)
- Reddit Inc: Moderator Code of Conduct (effective Jun 5, 2025)
- Reddit Help Center: Moderation Limits (Jan 2026)
- Inc.: "Volunteer Moderators Who Helped Reddit Grow Are Now a Concern for Investors" (Mar 2024)
- Campaign US: "Reddit's first day of IPO ends on a high" (Mar 2024)
- Northwestern University: "Unpaid social media moderators perform labor worth $3.4 million/year on Reddit alone" (May 2022)
- MacroTrends: RDDT stock price history
