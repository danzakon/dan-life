# Voice AI Platform Comparison: Raw Research Findings

**Date:** 2025-02-25
**Context:** Evaluating Retell AI, Bland AI, and Cartesia for Pairteam healthcare voice agent
**Use case:** Outbound calls to patients who expressed interest, complex multi-turn conversations, complex behavioral rules

---

## RETELL AI

### Agent Builder Architecture

Retell offers THREE approaches to building agents:

**1. Single Prompt Agent**
- One comprehensive prompt defines all behavior
- Great for simple use cases
- Known issues at scale: hallucinations, unreliable function calling, hard to maintain as prompt grows
- Retell themselves recommend against this for complex agents
- Source: https://docs.retellai.com/build/single-multi-prompt/prompt-overview

**2. Multi-Prompt Agent (Tree Structure)**
- Structured tree of prompts where each node has its own prompt, function calling instructions, and transition logic
- Example: "Lead Qualification" template has two nodes: (1) Lead Qualification (gather info), (2) Appointment Scheduling (book only after qualification)
- Prevents issues like premature appointment booking before completing qualification
- Source: https://docs.retellai.com/build/single-multi-prompt/prompt-overview

**3. Conversation Flow Agent (Node-Based Visual Builder)**
- Multiple nodes to handle different scenarios
- Node types: Conversation Node, Function Node, Call Transfer Node, Press Digit Node, End Node, Logic Split Node
- Edges define transition conditions between nodes
- Global Settings for agent-wide parameters, default voice, global prompt
- Key benefits: fine-tuning per node, conditional branching, state management, predictable behavior
- Different LLM models can be used per node (cost optimization)
- Pricing calculated per node based on model used and time spent
- Source: https://docs.retellai.com/build/conversation-flow/overview

### Custom LLM Support

YES - Full custom LLM integration via WebSocket:
- You set up a backend WebSocket server
- Retell connects to your `llm_websocket_url`
- Interaction flow: User speaks -> Retell STT -> sends transcript to your LLM server -> your server responds -> Retell TTS -> audio back to user
- Demo repos available: Python and Node.js
- You have FULL control over response generation
- Can use any LLM (OpenAI, Anthropic, self-hosted, etc.)
- Source: https://docs.retellai.com/integrate-llm/overview

Built-in LLM options: GPT-4, GPT-4 Turbo, GPT-4.1, Claude 3, Claude 3.5

### Healthcare Features

Dedicated healthcare page: https://www.retellai.com/healthcare

**Use cases covered:**
- Patient Frontdesk
- Healthcare Back Office
- Patient Management
- Provider Management

**Key capabilities:**
- Call Routing: dynamic routing to departments, smart routing to assigned contacts (e.g., primary doctor), warm transfer with context
- IVR Navigation: AI navigates IVR to retrieve clinic information, press digits
- Patient Management: appointment booking, smart notifications/check-ins, prescreening/surveys
- EHR integrations: Jane App, Dentrix, OpenDental, Epic, ChiroTouch, aCOM Health, eClinical, Keragon

**Customer quotes:**
- GiftHealth: "45-50% of calls completely resolved by Retell AI without touching a human"
- Doxy.me: "became our first point of contact for free users"
- Everise: "able to contain 65% of voice calls with the bot"

**Compliance:**
- HIPAA compliant (INCLUDED in standard pricing, not an add-on)
- BAAs offered as standard for all users under pay-as-you-go plan (no enterprise account required)
- Zero data retention policies available
- Opt-out recording settings
- SOC 2 Type II certified
- GDPR compliant
- Source: https://www.retellai.com/blog/do-retell-ais-voice-agents-have-hipaa-compliance-and-baas

### Complex Conversation Flow Handling

Three approaches with increasing control:
1. Single prompt (least control, most natural)
2. Multi-prompt tree (moderate control)
3. Conversation Flow (most control, node-based)

Key insight from YouTube tutorial (Tech Tomlet): "AI voice agents generate responses probabilistically, which means they might say something different every time. Conversational flows force structure and make AI more reliable in the right situations. However, if used incorrectly, they can make conversations feel rigid."

Trade-off: More control = more predictable but potentially less natural conversation.

### Developer SDK and API

- REST API with WebSocket support
- SDKs available (Python, Node.js based on GitHub repos)
- MCP server for AI assistant integration
- Knowledge base synchronization
- Batch campaign management
- Function calling: End call, Transfer call, Check Calendar, Book Calendar, Press digit (IVR), Custom functions
- Source: https://docs.retellai.com/build/single-multi-prompt/custom-function

### Post-Call Analysis

Comprehensive feature: https://www.retellai.com/features/post-call-analysis

**Analysis categories:**
- Boolean (True/False): e.g., "Was the user reached?"
- Text (String): e.g., detailed call summaries, action items
- Number (Numerical value): e.g., transaction amounts
- Selector (Enum): e.g., issue categories from a fixed list

**Custom categories supported** - define your own analysis fields

**Consumption methods:**
1. Dashboard - visual interface
2. Webhook - real-time notifications with `call_analyzed` event
3. API - programmatic access via Get Call API

Source: https://docs.retellai.com/features/post-call-analysis

### Pricing

- Pay-as-you-go: $0 to start, $0.07-$0.12/min, 60 min free, 20 concurrent calls
- Enterprise: white glove service, custom pricing, dedicated solution engineers
- Component-based: Voice Engine ($0.07-0.08/min) + LLM ($0.006-0.50/min) + Knowledge Base ($0.005/min) + Telephony (~$0.015/min)
- **Realistic total: $0.13-$0.31/min**
- At 10K min/month: ~$700 total (cheapest of the three platforms)
- HIPAA included, not an add-on

### Limitations for Complex Behavioral Control

- Conversation Flow agent provides the most control but requires more setup time
- Less granular control than VAPI (middleware-level customization)
- Voice cloning requires ElevenLabs integration (not native)
- Knowledge base has per-item fees after 10 bases
- Smaller integration ecosystem than Bland
- The Conversation Flow approach trades natural conversation for deterministic control

### What Makes Retell Unique

- Lowest latency in industry: ~600ms average (500-750ms range)
- HIPAA included in standard pricing
- SOC 2 Type II (not just SOC 2)
- Visual builder genuinely usable by non-developers
- Backchannel ("uh-huh") responses for natural feel
- Ambient sound options (office)
- Founded by former Google, Meta, ByteDance engineers (YC company)
- 3,000+ companies, 40M+ calls managed
- **Cartesia is one of their TTS providers** (interesting connection)

### Key URLs
- Homepage: https://www.retellai.com/
- Healthcare: https://www.retellai.com/healthcare
- Docs: https://docs.retellai.com/
- Custom LLM: https://docs.retellai.com/integrate-llm/overview
- Conversation Flow: https://docs.retellai.com/build/conversation-flow/overview
- Post-Call Analysis: https://docs.retellai.com/features/post-call-analysis
- HIPAA: https://www.retellai.com/blog/do-retell-ais-voice-agents-have-hipaa-compliance-and-baas

---

## BLAND AI

### Conversational Pathways - Deep Dive

Source: https://docs.bland.ai/tutorials/pathways

**Architecture:**
- Graph-based visual builder with Nodes and Pathways (edges)
- Agent starts at first node, moves through based on pathway decisions
- Each node contains instructions that become dialogue
- Pathways have labels that the agent uses to decide transitions

**Node Types (6 total):**
1. **Default/Base Node** - Generate response via prompt OR static text toggle (fixed response)
2. **Wait for Response Node** - Like default but can wait/hold for user
3. **Transfer Call Node** - Transfer to another number after dialogue
4. **End Call Node** - End call after dialogue
5. **Knowledge Base Node** - Connect to knowledge base for Q&A
6. **Webhook Node** - Execute webhooks mid-conversation, use response data in dialogue

**Key Features:**
- **Conditions**: Must be met before agent moves to next node (e.g., "You must get the date, time, and number of guests"). Agent stays on node until condition fulfilled.
- **Global Nodes**: Take precedence over condition decisions. Accessible from ANY node. Agent returns to previous node after handling global node. Great for edge cases (e.g., user asks off-topic question).
- **Variables**: `{{variable_name}}` syntax, built-in vars (`{{call_id}}`, `{{to}}`, `{{from}}`, `{{now_utc}}`, `{{prevNodePrompt}}`, `{{lastUserMessage}}`), can extract variables from conversation per node
- **Decision Guide**: Optional per-node examples of user input -> pathway mapping (for when agent picks wrong path)
- **Global Prompt**: Instructions applied to ALL nodes (tone, personality, general rules)

**Testing:**
- Web-based chat (text or voice)
- Real phone call testing
- Per-node unit testing with historical call data
- Branching conversations from any message
- Expanded call logs with variable extraction, loop conditions, route decisions, webhook data
- Simulated variations (generates 5+ variants of user message to stress-test)
- LLM-as-a-judge evaluation for pass/fail

**Variable Extraction:**
- Per-node configuration: description, type (string/integer/boolean), name
- Extracted variables available in subsequent nodes
- Variables available in webhook request data
- Webhook response variables available in post-webhook dialogue
- Latency note: extraction adds slight latency

### How Much Control Over Conversation Logic

VERY HIGH control through Pathways:
- Prompt every step from beginning to end
- Define decisions and forward conditions
- Set loop conditions (keep asking until info collected)
- Global triggers for transfers
- Static text for deterministic responses at specific points
- Variable extraction at every node
- Webhooks at any point
- The "Don't rely on a single prompt -- map out the entire conversation" philosophy

### Custom LLM Support

- The docs page at `docs.bland.ai/enterprise-features/custom-llm` returns **404 - Page Not Found**
- Bland runs on a **self-hosted model stack** with dedicated servers and GPUs
- Their enterprise pitch is about dedicated infrastructure, NOT about bringing your own LLM
- Bland uses **proprietary models** for voice/TTS
- For the LLM brain: appears to support GPT-4, Claude through their platform
- **KEY FINDING: No clear BYOL (Bring Your Own LLM) documentation exists**. Bland appears to use their own model stack and third-party LLMs through their infrastructure, not a custom LLM endpoint you host.

### Developer Experience and API

- Simple REST API: ~10 lines of code to send a call
- Conversational Pathways visual builder (no-code for flows, code for integrations)
- Webhook support for custom workflows
- Native CRM integrations (HubSpot, Salesforce, Slack, Notion, Calendly)
- SMS integration ($0.02/message)
- Voice cloning from single audio sample (native, no third-party needed)
- Custom tools for mid-call actions (calendar API, database queries)
- Personas for agent configuration (voice style, rules, routing logic)

### Limitations

**From multiple review sources:**

1. **No true no-code setup**: Visual builders exist but non-technical teams still need developers for integrations, tool logic, edge cases
2. **Discord-based support**: Primary support through Discord, not dedicated account managers (enterprise tier may differ)
3. **Hallucination risks**: Without strict guardrails, agents can promise refunds or make up policies
4. **Platform stability concerns**: "Move fast" approach results in service fluctuations (per Ringg AI review, CallBotics review)
5. **Complex pricing**: Multiple cost layers make forecasting hard (minutes + transfers + minimums + messaging + Turbo mode)
6. **No automated testing sandbox**: Manual testing; automated regression testing requires custom DIY harnesses
7. **Voice quality slightly behind Retell** in head-to-head testing (per WhiteSpace comparison)
8. **Latency ~800ms** (700-1000ms range) -- slowest of the three platforms compared
9. **Product Hunt rating: 3.0** with mixed reviews, complaints about customer service
10. **Turbo mode adds cost**: Achieving lowest latency requires premium Turbo mode

**From Ringg AI review (Feb 2026):**
- "Platform's aggressive focus on beta features and speed often results in service fluctuations and downtime"
- "Discord-based support model insufficient for enterprises needing SLA-backed guarantees"
- "Without strict guardrails, creative nature of models can lead to agents promising refunds or making up policies"
- "Marketing and Operations managers cannot make simple script changes without waiting for developer"

**From CallBotics review (Feb 2026):**
- "Bland AI works best for teams comfortable managing ongoing testing, QA, and iteration internally"
- "Pricing combines monthly plans with multiple usage-based charges, which can complicate forecasting"
- "No automated testing sandbox"

### Healthcare Use Cases

- Bland has healthcare content: https://www.bland.ai/blogs/ai-call-center-automation-in-healthcare
- Their Conversational Pathways page features "Karen - Healthcare Appointment Scheduling" as example
- Claims HIPAA compliance with self-hosted infrastructure
- Blog post on HIPAA/BAAs: https://www.bland.ai/blogs/does-blands-voice-ai-have-enterprise-compliances-like-baas-and-hipaa
- "Platform was architected from the ground up assuming every call would contain PHI"
- Healthcare use cases: appointment scheduling, post-discharge follow-ups, insurance verification, medication adherence, pre-surgical intake
- Enterprise customers include CareTrack (healthcare)
- SOC 2, HIPAA, GDPR, PCI compliance listed via Delve trust portal

### Pricing

| Plan | Monthly | Daily Call Limit | Concurrent Calls | Voice Clones |
|------|---------|-----------------|------------------|-------------|
| Start | Free | 100 | 10 | 1 |
| Build | $299/mo | 2,000 | 50 | 5 |
| Scale | $499/mo | 5,000 | 100 | 15 |
| Enterprise | Custom | Unlimited | Unlimited | Unlimited |

Per-minute: $0.09 (Start/Build), $0.11 (Scale)
Additional charges: SMS $0.02/msg, transfers $0.025/min, $0.015 minimum for calls <10s
**Realistic total: $0.09-$0.15/min** (simpler than Retell/VAPI)
At 10K min/month: ~$900-$1,200

### Key URLs
- Homepage: https://www.bland.ai/
- Conversational Pathways: https://docs.bland.ai/tutorials/pathways
- Product page: https://www.bland.ai/product/conversational-pathways
- Healthcare blog: https://www.bland.ai/blogs/ai-call-center-automation-in-healthcare
- HIPAA: https://www.bland.ai/blogs/does-blands-voice-ai-have-enterprise-compliances-like-baas-and-hipaa
- Enterprise: https://www.bland.ai/for-enterprises
- Voice Agent: https://www.bland.ai/voice-agent

---

## CARTESIA

### What Cartesia Is

Cartesia is PRIMARILY a speech model company, not a full voice agent platform (until recently). They make:

1. **Sonic** - Text-to-Speech (TTS) model family
2. **Ink** - Speech-to-Text (STT) model (Ink-Whisper)
3. **Line** - Voice agent development platform (launched Aug 2025, NEW)

Founded by researchers building SSM-based (State Space Model) architectures. $120M+ raised including $100M round. 50,000+ customers including Nvidia, Samsung, ServiceNow. Source: https://www.todayin-ai.com/p/cartesia

### Sonic TTS - Quality and Benchmarks

**Models:**
- Sonic-2 (flagship): 90ms time-to-first-audio, multilingual, highest quality
- Sonic-Turbo: Even faster, 500 char limit for English
- Sonic-3: Latest, "best text-to-speech for voice agents", laughs, emotes, conversational

**Quality claims:**
- Blinded human evaluation: Sonic-2 preferred over ElevenLabs Flash V2 by 61.4% vs 38.6% (Cartesia's own test)
- "Only product in existence with model latency of less than 100ms, outperforming next best by factor of four" (Bob Summers, CEO quote)
- "Best voice model today for real-time multimodal use cases" (Kwindla Hultman, Daily.co CEO)

**From ElevenLabs comparison (biased - ElevenLabs source):**
- ElevenLabs claims 75ms latency vs Cartesia 95ms
- ElevenLabs: 32 languages vs Cartesia: 15 languages
- ElevenLabs: 4000+ voices vs Cartesia: ~130 voices
- ElevenLabs claims better quality, but they're clearly biased
- Source: https://elevenlabs.io/blog/elevenlabs-vs-cartesia

**From Murf AI comparison (neutral third-party):**
- Both praised for different strengths
- Cartesia: speed and low latency champion
- ElevenLabs: more voices, more languages, more features
- Source: https://murf.ai/blog/cartesia-vs-elevenlabs

**From TeamDay benchmarks (Feb 2026):**
- Cartesia Sonic-3 listed alongside ElevenLabs, OpenAI as top-tier
- Sub-100ms latency category
- Source: https://www.teamday.ai/sk/blog/best-ai-voice-models-2026

**Key differentiator: SSM architecture** (not Transformer-based) enables:
- Constant memory usage regardless of context length
- Can run on-device / edge deployment
- Extremely low latency by design

### Cartesia Line - Agent Platform (NEW)

Launched: August 19, 2025
Source: https://cartesia.ai/blog/introducing-line-for-voice-agents
GitHub: https://github.com/cartesia-ai/line (92 stars, 34 forks, Apache 2.0)
Latest release: v0.2.3alpha1 (Feb 2026) -- NOTE: still in alpha/pre-release

**Philosophy: Code-first, not visual builder**
- "The best products are built with code"
- "Intelligent agents and great conversations are impossible to express in rigid conversational builders"
- References Stripe, Twilio, Vercel as inspirations
- Designed for AI-assisted coding (agents writing agent code)

**SDK Features:**
- Python SDK (`cartesia-line` package)
- LLM provider agnostic via LiteLLM (100+ providers: OpenAI, Anthropic, Google, etc.)
- Real-time interruption support
- Tool calling (loopback tools, passthrough tools, handoff tools)
- Multi-agent handoffs
- Web search built-in
- Background reasoning
- Context management (add_history_entry, set_history_processor)
- Custom agent wrapper pattern (GuardedAgent example)

**Tool Types:**
| Type | How to create | Result goes to | Use for |
|------|--------------|----------------|---------|
| Loopback | `@loopback_tool` | Back to LLM | API calls, data lookup |
| Passthrough | `@passthrough_tool` | Directly to user | Deterministic actions |
| Handoff | `agent_as_handoff()` | Another agent | Multi-agent workflows |

**Deployment:**
- CLI for local dev and deployment
- GitHub integration
- One-command deploy
- Call analytics and observability built-in
- LLM-as-a-judge custom metrics

**Enterprise:**
- Can be deployed entirely on-prem (agents + models)
- Models can be customized with fine-tuning
- Globally distributed infrastructure

**IMPORTANT CAVEAT:** Line is VERY NEW (6 months old) and still in alpha/pre-release. Only 92 GitHub stars. This is early-stage compared to Retell (40M+ calls) and Bland (enterprise customers).

### How Cartesia Fits in the Voice Agent Stack

Two ways to use Cartesia:

**1. As a component (TTS/STT provider) in other frameworks:**
- LiveKit Agents: Official plugin for TTS and STT
  - Source: https://docs.cartesia.ai/integrations/live-kit, https://docs.livekit.io/agents/v0/integrations/cartesia
- Pipecat: Integration available
  - Source: https://docs.cartesia.ai/2025-04-16/integrations
- Rasa: Integration available
- Thoughtly: Integration available
- Twilio: Integration available
- Vapi: Free Sonic 3 TTS week promotion (Oct 2025)
- **Retell AI uses Cartesia as a TTS provider** (confirmed: https://cartesia.ai/customers/retell)

**2. As a full agent platform via Line:**
- Code-first agent development
- Telephony via Voximplant integration (Feb 2026)
- PSTN, SIP, WebRTC, WhatsApp Business Calling support through Voximplant
- Source: https://voximplant.com/blog/extend-cartesia-line-agents-to-sip-whatsapp-and-global-phone-networks

### Developer SDK and API

**TTS/STT API:**
- JavaScript/TypeScript SDK
- Python SDK
- WebSocket streaming support
- REST API
- Voice cloning (Instant and Pro)
- Voice library (~130 voices)
- Voice design (create custom voices)
- 15 languages supported

**Line Agent SDK (Python):**
```python
from line.llm_agent import LlmAgent, LlmConfig, end_call
from line.voice_agent_app import VoiceAgentApp

async def get_agent(env, call_request):
    return LlmAgent(
        model="gemini/gemini-2.5-flash-preview-09-2025",
        api_key=os.getenv("GEMINI_API_KEY"),
        tools=[end_call],
        config=LlmConfig(
            system_prompt="You are a helpful voice assistant.",
            introduction="Hello! How can I help you today?",
        ),
    )

app = VoiceAgentApp(get_agent=get_agent)
```

- Built-in tools: end_call, send_dtmf, transfer_call, web_search
- Custom tool decorators: @loopback_tool, @passthrough_tool, @handoff_tool
- Dynamic prompts from API call requests
- History management and transformation
- Background long-running tools

### Pricing

**Model credits system (not per-minute like Retell/Bland):**

| Plan | Monthly | Model Credits | Agent Prepaid | Concurrent Calls (Line) |
|------|---------|--------------|---------------|------------------------|
| Free | $0 | 20K | $1 | 8 |
| Pro | $5 | 100K | $5 | 12 |
| Startup | $49 | 1.25M | $49 | 20 |
| Scale | $299 | 8M | $299 | 60 |
| Enterprise | Custom | Custom | Custom | Custom |

**Line Agent costs:**
- Call duration: $0.06/min
- Telephony: $0.014/min
- LLM usage during calls: Currently free (limited time)
- Text-to-Agent creation: $0.05 per creation (currently free limited time)

**Sonic TTS:** 1 credit per character
**Ink STT:** 1 credit per second of audio
**Ink-Whisper at Scale plan:** $0.13/hr (cheapest streaming STT claim)

**HIPAA compliance:** Enterprise plan only (not standard)
**SOC 2 Type II:** Available (check current status)
**GDPR:** Achieved Sept 2025

### Limitations

1. **Line is alpha/pre-release** -- not production-battle-tested at scale
2. **Fewer voices than ElevenLabs** (~130 vs 4000+)
3. **Fewer languages** (15 vs 32+ for ElevenLabs)
4. **No visual builder** -- code-only approach (by design, but limits non-dev access)
5. **Limited telephony** -- needs Voximplant or similar for PSTN (just integrated Feb 2026)
6. **Healthcare compliance (HIPAA) only on Enterprise plan**
7. **Small community** -- 92 GitHub stars vs massive Retell/Bland ecosystems
8. **No built-in CRM integrations** -- you build everything in code
9. **Missing features vs Retell/Bland:** No batch calling, no visual analytics dashboard, no branded caller ID
10. **500 character limit on Sonic-Turbo** (fastest model)

### Key URLs
- Homepage: https://cartesia.ai/
- Sonic (TTS): https://cartesia.ai/sonic
- Line (Agents): https://cartesia.ai/agents
- Pricing: https://cartesia.ai/pricing-09-26
- Docs: https://docs.cartesia.ai/
- Line SDK GitHub: https://github.com/cartesia-ai/line
- Line blog post: https://cartesia.ai/blog/introducing-line-for-voice-agents
- LiveKit integration: https://docs.cartesia.ai/integrations/live-kit
- Retell case study: https://cartesia.ai/customers/retell
- vs ElevenLabs: https://cartesia.ai/blog/cartesia-vs-elevenlabs

---

## HEAD-TO-HEAD COMPARISON DATA

### From WhiteSpace Solutions (practitioner who built on all three, Feb 2026)

Source: https://www.whitespacesolutions.ai/content/bland-ai-vs-vapi-vs-retell-comparison

| Factor | Bland AI | VAPI | Retell AI |
|--------|----------|------|-----------|
| Best For | High-volume outbound | Custom dev | Low-latency conversational |
| Base Price | $0.09/min | $0.05/min + providers | $0.07/min |
| True Cost/Min | $0.09-0.15 | $0.13-0.31 | $0.13-0.31 |
| Latency | ~800ms | ~700ms | ~600ms |
| No-Code | Pathways builder | Dashboard only | Full visual builder |
| Compliance | SOC 2, HIPAA, GDPR | SOC 2, HIPAA ($1K add-on) | SOC 2 Type II, HIPAA, GDPR |

**Voice Quality Winner:** Retell AI (100+ calls tested per platform)
**Latency Winner:** Retell AI (600ms avg vs 700ms VAPI vs 800ms Bland)
**Customization Winner:** VAPI (bring any LLM, STT, TTS)
**Integration Winner:** Bland AI (most polished native integrations)
**Pricing at Scale Winner:** Retell AI ($700/mo at 10K min vs $900-1200 Bland vs $1400-1600 VAPI)
**Compliance Winner:** Retell AI (tie with Bland; HIPAA included not add-on)

### Latency Comparison (measured)

| Platform | Average | Range |
|----------|---------|-------|
| Retell AI | ~600ms | 500-750ms |
| VAPI | ~700ms | 600-900ms |
| Bland AI | ~800ms | 700-1000ms |

### At 10,000 min/month cost

| Platform | Monthly Cost |
|----------|-------------|
| Retell AI | ~$700 |
| Bland AI | ~$900-1,200 |
| VAPI | ~$1,400-1,600 |

---

## HEALTHCARE-SPECIFIC ANALYSIS

### For Pairteam's Use Case (Outbound to interested patients, complex conversations)

**HIPAA Compliance:**
- Retell: INCLUDED in standard pricing, BAA available to all users
- Bland: Available, self-hosted infrastructure pitch, enterprise-focused
- Cartesia: Enterprise plan only for HIPAA
- VAPI (reference): $1,000/month add-on

**Complex Multi-Turn Conversations:**
- Retell: Conversation Flow (node-based) or Custom LLM (full control)
- Bland: Conversational Pathways (node-based with conditions, loops, globals)
- Cartesia Line: Code-first with multi-agent handoffs, history management (BUT alpha)

**Complex Behavioral Rules:**
- Retell: Multi-prompt tree or Conversation Flow with per-node logic
- Bland: Pathways with conditions, global nodes, decision guides, variable extraction
- Cartesia: Pure code control -- most flexible in theory, but most engineering effort

**Custom LLM (Bring Your Own):**
- Retell: YES -- WebSocket integration, full control
- Bland: UNCLEAR -- no BYOL docs found, appears to use their infrastructure
- Cartesia Line: YES -- 100+ providers via LiteLLM, any model string

**Post-Call Analysis:**
- Retell: Built-in with custom categories, webhook/API/dashboard consumption
- Bland: Post-call webhooks available
- Cartesia Line: Call analytics, LLM-as-a-judge metrics

**EHR Integration:**
- Retell: Epic, OpenDental, Dentrix, Jane App, etc. (via partners)
- Bland: EMR integration mentioned in healthcare blog, custom tools during calls
- Cartesia: Build your own via code (no native EHR connectors)

---

## RED FLAGS AND RISK FACTORS

### Retell AI
- Relatively young company (founded 2023)
- Conversation Flow is powerful but complex to set up
- Less flexible than a fully custom stack
- Voice cloning not native (ElevenLabs dependency)

### Bland AI
- Product Hunt rating 3.0 with mixed reviews
- Customer service complaints in reviews
- Discord-based support model
- Platform stability concerns from multiple sources
- Aggressive beta feature release cadence
- Complex pricing with hidden layers
- No clear custom LLM documentation
- Hallucination risks without strict guardrails

### Cartesia
- Line agent platform is 6 months old and in ALPHA
- Tiny community (92 GitHub stars)
- No battle-tested production deployments at scale for agents
- HIPAA only on Enterprise
- No visual builder
- Limited telephony (just got Voximplant integration)
- Fewer voices and languages than competitors
- Would be building on very early-stage infrastructure

---

## COMPARISON SOURCES

1. WhiteSpace Solutions (practitioner, Feb 2026): https://www.whitespacesolutions.ai/content/bland-ai-vs-vapi-vs-retell-comparison
2. CallBotics Bland review (Feb 2026): https://callbotics.ai/blog/bland-ai-review
3. CallBotics Retell review (Feb 2026): https://callbotics.ai/blog/retell-ai-review
4. Ringg AI Bland review (Feb 2026): https://www.ringg.ai/blogs/bland-ai-review
5. Synthflow comparison (Dec 2025): https://synthflow.ai/blog/8-best-ai-voice-agents-for-business-in-2026
6. Softcery 11-platform comparison (2025): https://softcery.com/lab/choosing-the-right-voice-agent-platform-in-2025
7. Dialora Bland review (Oct 2025): https://www.dialora.ai/blog/bland-ai-review
8. Dograh Bland review (Aug 2025): https://blog.dograh.com/bland-ai-review-2025-pros-cons-pricing-and-features/
9. Smallest.ai Cartesia review (Jan 2026): https://smallest.ai/blog/cartesia-ai-review-2025-features-pricing-and-comparison
10. Inworld TTS benchmarks (Jan 2026): https://inworld.ai/resources/best-voice-ai-tts-apis-for-real-time-voice-agents-2026-benchmarks
11. Famulor TTS comparison (Feb 2026): https://www.famulor.io/fr/blog/cartesia-sonic-elevenlabs-and-minimax-the-ultimate-comparison-for-ai-voice-agents-and-famulors-strategic-advantage
12. Podcastle TTS benchmark (Nov 2025): https://podcastle.ai/blog/tts-latency-vs-quality-benchmark/
