# Content Sources

Configuration for all ingest agents. Edit this file to control which accounts and channels are monitored. Changes take effect on the next ingest run.

---

## X Accounts — Monitor

These accounts are scraped on every ingest run. Posts since the last run are surfaced as inbox items.

```
# Format: @handle  # description

# --- Tenex ---
@ArmanHezarkhani  # Tenex
@businessbarista  # Tenex
@seejayhess       # Tenex

# --- AI / ML / Engineering ---
@karpathy         # AI/ML depth, LLM internals
@sama             # AI strategy, OpenAI
@bcherny          # TypeScript, developer tools
@clairevo         # AI, tech
@trq212           # tech, engineering
@mitchellh        # systems engineering, Ghostty, Zig
@aidenybai        # React, JavaScript frameworks
@thdxr            # SST, serverless, infra
@RhysSullivan     # TypeScript, Next.js
@hwchase17        # LangChain, AI agents
@mattshumer_      # AI agents, prompting
@DhravyaShah      # AI engineering, dev tools
@leerob           # Next.js, Vercel, DX
@rauchg           # Vercel, web dev
@kepano           # Obsidian, tools for thought
@mckaywrigley     # AI coding, dev tools
@theo             # web dev, TypeScript
@yacineMTB        # AI engineering, open source
@IterIntellectus  # AI reasoning, research
@TheGregYang      # AI research, theory
@AISafetyMemes    # AI safety, memes
@8teAPi           # AI engineering
@jxnlco           # AI engineering, structured output
@mansourtarek_    # AI, tech
@AravSrinivas     # Perplexity, AI search
@dwr              # Farcaster, crypto, social
@andruyeung       # AI, engineering

# --- Founders / Builders ---
@levelsio         # indie hacking, pricing, solo founder
@gregisenberg     # community-led growth, startups
@ryancarson       # tech education, startups
@ericzakariasson  # startups, engineering leadership
@kieranklaassen   # startups, product
@sweatystartup    # bootstrapping, small business
@bonam            # startups, product
@snowmaker        # startups, venture
@codyschneiderxx  # growth, startups
@tobi             # Shopify, building at scale
@natfriedman      # AI, ex-GitHub CEO
@gfodor           # startups, AI
@jackfriks        # creator economy, building
@iannuttall       # indie hacking, newsletters
@apples_jimmy     # building, startups
@radbackwards     # startups, product
@bubbleboi        # startups, building

# --- VCs / Investors ---
@tunguz           # SaaS metrics, VC
@milesgrimshaw    # venture, enterprise
@eglyman          # venture, fintech
@based16z         # a16z, venture
@danielgross      # AI investing, building
@alexisohanian    # Reddit co-founder, investing
@TurnerNovak      # venture, consumer
@emilyinvc        # venture, tech
@eladgil          # investing, startups
@martin_casado    # a16z, enterprise
@levie            # Box, enterprise SaaS
@VinnyLingham      # investing, crypto

# --- Business / Media / Thought Leaders ---
@alliekmiller     # AI strategy, enterprise
@MollySOShea      # media, tech
@rowancheung      # AI news, content
@emollick         # AI in education, research
@ShaanVP          # business ideas, pods
@Codie_Sanchez    # SMB acquisition, business
@thesamparr       # media, entrepreneurship
@beffjezos        # tech commentary
@bryan_johnson    # longevity, biohacking
@tylercowen       # economics, culture
@BillAckman       # investing, business
@austin_rief      # Morning Brew, media
@OfficialLoganK   # tech, AI content
@johncoogan       # tech, media
@mattparlmer      # content, business

# --- Creators / Writers ---
@BrettFromDJ      # creator economy
@yasser_elsaid_   # content, writing
@billyjhowell     # writing, content
@rileybrown       # content, building
@justinskycak     # math, education
@iruletheworldmo  # tech, commentary
@gmiller          # tech, writing
@ben_m_somers     # writing, business
@growing_daniel   # growth, content
@iamgingertrash   # content, creator
@virattt          # finance, AI

# --- Niche / Misc ---
```

---

## X Accounts — Mutuals (Priority Engagement)

These accounts get a higher priority score in the digest and are always flagged for reply opportunities. Add people you want to consistently engage with.

```
# Format: @handle  # context
@ArmanHezarkhani  # Tenex — co-founder
@businessbarista  # Tenex — co-founder
@seejayhess       # Tenex — co-founder
```

---

## YouTube Channels

Channels are checked for new videos on every ingest run. Transcripts are NOT pulled automatically — the youtube-monitor surfaces new video titles and asks for approval before fetching a transcript.

Use `ytquery y:channel @handle --limit 5` to check a channel manually.
Use `ytquery y:rss @handle` to resolve a channel ID from a handle.

```
# Format: {channel-id}  # @handle | channel name | keyword filter (optional)
# Keyword filter: only surface videos whose titles contain these terms (comma-separated)
# Leave blank to surface all new videos from that channel

# --- AI / ML / Engineering (no filter — all content relevant) ---
UCSHZKyawb77ixDdsGog4iWA  # @lexfridman | Lex Fridman | AI, LLM, coding, AGI
UCe4jUOmQPKMDvOkzJpDfMRQ  # @karpathy | Andrej Karpathy | AI, neural, LLM, backprop, GPT, software, coding
UCsBjURrPoezykLs9EqgamOA  # @fireship | Fireship | AI, TypeScript, web
UCLKPca3kwwd-B59HNr-_lvA  # @aiDotEngineer | AI Engineer Summit
UCxBcwypKK-W3GHd_RZ9FZrQ  # @latentspacepod | Latent Space
UCrDwWp7EBBv4NwvScIpBDOA  # @anthropic-ai | Anthropic

# --- Dev / Tech ---
UCbRP3c757lWg9M-U7TyEkXA  # @t3dotgg | Theo | TypeScript, Next.js, web dev
UC8ENHE5xdFSwx71u3fDH5Xw  # @theprimeagen | ThePrimeagen | engineering, systems, coding
UCcefcZRL2oaA_uBNeo5UOWg  # @ycombinator | Y Combinator | startups, founders

# --- VC / Business ---
UC9cn0TuPq4dnbTY-CBsm8XA  # @a16z | a16z | AI, investing, enterprise
```

---

## Research Triggers

When these terms appear in 3 or more inbox items within a 7-day window, the digest will suggest kicking off a research report on the topic.

```
agentic coding
context windows
production AI
```
