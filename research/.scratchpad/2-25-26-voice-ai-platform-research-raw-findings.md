# Voice AI Platform Research: Raw Findings

Date: 2-25-26

---

## TOPIC 1: PAIRTEAM COMPANY RESEARCH

### What Pairteam Does

Pair Team is a tech-enabled, AI-first medical group (public benefit corporation) focused on "whole-person care" for high-need Medicaid and Medicare beneficiaries. They describe themselves as building the "safety net of the future."

- Virtual and community-based primary care solution
- Connects highest-risk patients to coordinated medical, behavioral health, and social services
- Partners with shelters, food pantries, rehab facilities, and community-based organizations (CBOs)
- Turns community locations into healthcare sites via telemedicine
- Coordinates housing, food, transportation, behavioral health, and medical care
- Headquarters: San Francisco, CA
- ~500+ employees (per job listing)
- Founded by Neil Batlivala (engineer, from India) and Cassie Choi (registered nurse)

**Sources:**
- https://pairteam.com/patients
- https://pairteam.com/payers
- https://pairteam.com/technology
- https://www.chcf.org/resource/pair-team-business-model-closes-care-gaps-people-experiencing-homelessness/

### Patient Populations Served

- Medicaid (Medi-Cal in California) and Medicare beneficiaries
- "Duals" members (dual Medicaid/Medicare eligible)
- People experiencing homelessness
- People with complex health needs
- People reentering from incarceration
- Substance use recovery patients
- People with behavioral health needs
- People with housing, financial, or food insecurity
- People with chronic health conditions
- Populations with limited smartphone/internet access

**Geographic coverage:** California (contracts covering ~80% of the state across multiple counties including LA, Central Valley) and Clark County, Nevada. Expanding nationally.

**Source:** https://pairteam.com/patients

### Eligibility Criteria (from patient page)

- Social needs overlooked by traditional healthcare
- Assistance scheduling or accessing medical appointments
- Support navigating or understanding Medicaid
- Reentry from incarceration
- Substance use recovery
- Behavioral health needs
- Housing, financial, or food insecurity
- Chronic health conditions

### Business Model

- **Value-based care** contracts with Medicaid/Medicare health plans
- Partners with health plans (payers) to engage hard-to-reach members
- CHW-led (Community Health Worker) care teams with AI-powered coordination
- Collaborates with or serves as PCP directly when needed
- Revenue from Medi-Cal/Medicare contracts

**Funding:**
- $9M Series A (Oct 2023) - Led by Next Ventures, with PTX Capital, Kapor Capital, Kleiner Perkins, Y Combinator
- NTTVC invested at Seed stage
- California Health Care Foundation is a strategic investor

### Proven Impact (from their site, peer-reviewed study)

- 52% reduction in Emergency Department visits
- 26% reduction in inpatient visits
- $25k average cost savings for high-need patients
- 60% of patients with suicidal ideation improve after 3 months
- 70% of patients have had HbA1c reductions
- 1 in 3 ED visits prevented because patients call Pair Team first

**Published in:** Journal of General Internal Medicine: "A Novel Intervention for Medicaid Beneficiaries with Complex Needs"

**Source:** https://www.prnewswire.com/news-releases/new-research-highlights-pair-teams-novel-approach-to-improving-medicaid-better-engagement-lower-costs-and-improved-health-outcomes-302569075.html

### How Patients Currently Engage

1. Outreach through community-based organizations (shelters, food pantries, etc.)
2. Online enrollment form -> Pair Team contacts within 24 hours
3. Phone-based intake and triage
4. Dedicated care team assigned (nurse, NP, care coordinator)
5. 24/7 support available
6. Phone calls, video calls, text messages
7. **AI voice agents now handling patient interactions** (see below)

### Technology Stack & AI Approach

**CRITICAL FINDING: Pair Team is already using ElevenLabs Agents Platform for voice AI**

From ElevenLabs case study (Feb 2, 2026):
- Built a "constellation of agents" to help patients navigate healthcare and public assistance
- AI care agent system engages patients in natural, empathetic voice conversations
- Agents help secure housing, access food programs, manage medical appointments
- Voice and SMS are primary interfaces (most inclusive for their population)
- Named agent: "Flora" - AI social services coordinator

**Agent capabilities:**
- Empathetic check-ins for high-needs individuals
- Medication adherence follow-ups
- Medical appointment coordination
- Housing and food assistance coordination
- Patient intake calls

**Safety testing:**
- 3,121 simulated calls before deployment
- 99.9% success rate in safety-critical interactions
- Medical advice: 1,050 simulations, 100% success rate
- Domestic violence: 1,033 simulations, 99.8% success rate
- Suicidal ideation: 1,038 simulations, 100% success rate

**Engagement metrics:**
- Thousands of patients engaged
- Average conversation >9 minutes (strong engagement signal)

**Platform description from technology page:**
- "Unified data platform that bridges healthcare and public assistance"
- "Agentic infrastructure" for the safety net
- AI-first approach: "Safety-critical AI, Voice and LLM systems in production, Complex data and orchestration problems"
- Hiring: Engineers, product managers, AI practitioners
- Job listing mentions: Senior Software Engineer role, "AI-first, whole-person infrastructure"

**Sources:**
- https://elevenlabs.io/blog/pair-team
- https://pairteam.com/technology
- https://job-boards.greenhouse.io/pairteam/jobs/8425944002

---

## TOPIC 2: EMERGING/ALTERNATIVE VOICE AI PLATFORMS

---

### 1. VOCODE

**What it is:** Open-source library + hosted platform for building voice agents.

**GitHub:** https://github.com/vocodedev/vocode-core
- 3.3k stars, 562 forks
- Description: "Build voice-based LLM agents. Modular + open source."

**Hosted platform features:**
- Phone number setup and configuration
- Webhook-based architecture
- Agents, Prompts, Voices, Actions, Action Triggers
- Conversational Dials (tuning parameters)
- Answering Machine Detection
- Do Not Call Detection
- IVR Navigation (beta)
- Warm Transfer (beta)
- Multilingual bots (beta)
- Vector databases (beta)
- External Actions (beta)
- Injecting context (beta)
- **HIPAA Compliance (beta)** - `hipaa_compliant` flag that redacts prompt content, prevents transcript persistence, disables recording

**Enterprise features:**
- Bring Your Own Telephony
- Bring Your Own OpenAI API Keys

**SDK:** Python SDK available (`vocode_client.calls.create_call()`)

**Developer Experience:**
- Open source quickstarts available
- API Reference documented
- Hosted quickstart for rapid deployment

**Current state:** The website (vocode.dev) redirects to GitHub org page. Docs at docs.vocode.dev appear maintained. 11 repositories in the org. Last repo activity noted Nov 2024 on GitHub org page.

**Assessment:** Evolved from pure open-source to a hosted platform (similar trajectory to Vapi). HIPAA compliance is beta. The redirect from main site to GitHub may indicate the company is more engineering-focused or still early. Has telephony, actions, and voice agent primitives.

**Healthcare relevance:** HIPAA compliance flag exists (beta). Enterprise BYOT available.

**Sources:**
- https://docs.vocode.dev/welcome
- https://docs.vocode.dev/hipaa-compliance
- https://github.com/vocodedev/vocode-core

---

### 2. HAMMING AI

**What it is:** Automated AI voice agent testing, production call analytics, and governance platform. NOT a voice agent builder -- it's the QA/testing layer.

**Raised:** $3.8M Seed funding

**Core products:**
1. **Automated Testing**
   - Scenario generation (simulates different noises, languages, accents)
   - AI voice agent testing (simulated users)
   - AI chat agent testing
   - Concurrency load testing
   - Convert real production calls into replayable test cases
2. **Call Analytics**
   - Health checks
   - Call quality reports
   - Voice agent A/B testing
   - Actionable alerts
3. **Compliance**
   - Red-teaming
   - Compliance reports

**Integrations:** Works with Retell, LiveKit, Pipecat, OpenAI, Vapi

**4-Layer Quality Framework:**
| Layer | Focus | Key Metrics |
|---|---|---|
| Infrastructure | Audio quality, latency, ASR/TTS | TTFA, WER, packet loss |
| Execution | Intent classification, accuracy, tool-calling | Task success rate |
| User Behavior | Interruption handling, flow, sentiment | Barge-in recovery |
| Business Outcome | Containment rate, FCR, escalation | ROI |

**Healthcare relevance:** Discovered a medical voice agent prescribing medication instead of directing to professionals. Can test HIPAA compliance scenarios. Wrote detailed guide on HIPAA-compliant voice agents.

**Assessment:** Very relevant as a complementary tool regardless of which voice platform is chosen. Would be used for testing, not building. Could be critical for healthcare deployments where safety testing is paramount. The fact that Pair Team ran 3,121 simulated calls with ElevenLabs suggests this kind of testing is essential.

**Sources:**
- https://hamming.ai/
- https://hamming.ai/product
- https://hamming.ai/product/automated-testing
- https://hamming.ai/resources/how-to-evaluate-voice-agents-2026
- https://hamming.ai/blog/hipaa-compliant-voice-agents
- https://hamming.ai/resources/testing-and-monitoring-livekit-voice-agents-production

---

### 3. DEEPGRAM

**What it is:** Started as best-in-class STT provider, now offers a unified Voice Agent API that combines STT + LLM orchestration + TTS in one streaming API.

**Voice Agent API (GA as of June 2025):**
- Unified voice-to-voice API
- Single bidirectional WebSocket
- Built-in conversational control (turn-taking, barge-in, streaming function execution)
- BYOLLM and BYOTTS support
- Event-driven design

**Core models:**
- Nova-3 (STT) - best-in-class speech recognition, noisy conditions, multilingual
- Aura-2 (TTS) - expressive speech, sub-200ms TTFB
- Built-in orchestration layer

**Pricing:**
- **$4.50/hour** all-in (STT + LLM + TTS)
- Reduced rates for BYOLLM/BYOTTS
- 24% cheaper than ElevenLabs ($5.79/hr)
- 75% cheaper than OpenAI Realtime ($18.03/hr)
- NOT token-based (predictable costs)

**VAQI Benchmark (Voice Agent Quality Index):**
- Deepgram: 71.5 (ranked #1)
- OpenAI: 67.2
- ElevenLabs: 55.3
- Azure: 50.9

**Enterprise deployment:**
- Managed cloud, private VPC, or on-premises (Docker/Kubernetes)
- **HIPAA, GDPR** compliant
- Regional data hosting
- Single-tenant runtime environments available

**SDKs:** Python, JavaScript

**Customers:** Aircall, Jack in the Box, StreamIt, OpenPhone

**Healthcare-specific:**
- Nova-3 Medical Streaming product exists
- HIPAA compliant
- On-prem deployment for data residency

**How it fits in the stack:**
- Can be used as STT-only component plugged into LiveKit/Vapi/Retell
- OR can be used as a full voice agent platform via Voice Agent API
- Competes directly with the main platforms at a lower price point

**Assessment:** Serious contender as a full voice agent platform, not just an STT component. Best price/performance ratio. Strong enterprise features. HIPAA compliant. The $4.50/hr pricing is very competitive. However, may lack the higher-level abstractions and telephony integrations that platforms like Vapi/Retell provide out of the box.

**Sources:**
- https://deepgram.com/product/voice-agent-api
- https://deepgram.com/learn/voice-agent-api-generally-available
- https://deepgram.com/learn/ai-voice-agents

---

### 4. PLAYHT / PLAY.AI

**What it is:** Originally a TTS platform, now offers voice agent building capabilities.

**Voice Agent Platform features:**
- Build AI voice agents "in minutes" with no code
- Customer support agents (knowledge base, order tracking)
- Sales agents (inbound/outbound, pre-qualification)
- Appointment scheduling agents
- Integrations via Zapier and Make
- Healthcare demo number listed: +1 310-919-0613
- Concierge and Front Desk demo numbers available

**Positioning:**
- "Conversational Voice AI, trained to speak your business"
- Launched "Play AI" as a conversational voice interface
- Mission: "build a universal Voice Interface for AI"

**Technology:**
- TTS is core strength (one of the leading TTS providers)
- Voice cloning capabilities
- Multi-language support
- API available

**Assessment:** Strong TTS technology but the voice agent platform appears more no-code/low-code focused. Better for simpler use cases (appointment scheduling, basic customer support). Likely less suitable for complex healthcare workflows that need deep custom integrations, safety guardrails, and HIPAA compliance. No mention of HIPAA compliance found. More of a TTS provider that added agent capabilities on top.

**Sources:**
- https://play.ht/voice-agents/
- https://play.ht/blog/introducing-play-ai/
- https://play.ht/blog/best-ai-voice-agents/

---

### 5. THOUGHTLY

**What it is:** No-code/low-code AI voice agent platform for business phone automation.

**Key features:**
- Visual flow builder (drag-and-drop conversation design)
- Deploy voice agents in "17 minutes"
- Inbound and outbound call handling
- Bulk calling/automations for campaigns
- BYOC (Bring Your Own Carrier, e.g., Twilio)
- CRM integrations
- Real-time analytics
- SMS functionality
- Customizable agent persona, voice, script

**Industries targeted:** Healthcare, real estate, insurance, customer service

**Pricing:** Paid plan, custom pricing. Was available on AppSumo with credit-based system.

**Reviews:** Mixed - 3.3/5 on AppSumo (68 reviews). Complaints about support responsiveness. Some praise for intuitive UI and AI agent learning.

**Assessment:** Entry-level/mid-market no-code voice agent platform. Not suitable for complex healthcare use cases requiring deep customization, HIPAA compliance, or enterprise-grade reliability. The AppSumo presence and mixed reviews suggest this is more of a SMB tool. Would not recommend for Pairteam's use case.

**Sources:**
- https://www.callpod.ai/blog/thoughtly-review
- https://aichief.com/ai-audio-tools/thoughtly/
- https://appsumo.com/products/thoughtly/reviews/

---

### 6. SIGNALWIRE

**What it is:** Programmable Unified Communications (PUC) platform with native AI voice agent capabilities. Built by the creators of FreeSWITCH.

**Key differentiator:** Full telecom stack + AI in one platform. Not just an API layer on top of telephony -- they own the entire infrastructure.

**Core capabilities:**
- SIP, PSTN, WebRTC, TTS, call control -- all native
- Multi-agent orchestration in a single call
- Serverless, stateless AI voice runtime
- Context-aware routing, escalations, agent handoffs
- ~500ms roundtrip latency (with AI in loop)
- SWML (SignalWire Markup Language) for call flow definition
- SWAIG (SignalWire AI Gateway) for backend function integration
- Python-based Agent SDK

**Agent SDK features:**
- Composable prompts and modular skills
- Barge-in handling
- Multi-agent support and agent memory
- Prefab agents for rapid development
- Embedded RAG search
- CLI tools and serverless deploys
- Transfer between agents, humans, SIP endpoints

**Developer Toolkit:**
- 25+ production-ready applications
- Open-source Agent Builder (beta, July 2025)
- No-code visual interface + SWML configuration
- Sigmond embedded AI assistant in dashboard

**Pricing:**
- AI Agent: **$0.16/min** ($9.60/hr)
- Voice (local outbound): $0.008/min
- Phone numbers: $0.50/month (local)
- Standard TTS: $0.00008/10 chars
- STT: $0.015/15 sec

**Compliance:**
- **HIPAA compliant** - Full BAA coverage (voice, messaging, AI, video, fax)
- SOC 2 Type II
- PCI compliant
- NO enterprise tier required for HIPAA -- available on all plans
- No extra fees for HIPAA activation

**Healthcare presence:**
- Dedicated healthcare page with use cases
- Telehealth voice & video
- Appointment management
- Virtual care
- Customer quote from Phoenix Children's Hospital: "SignalWire's HIPAA-compliant platform gives us the confidence to communicate with families securely and at scale"

**Assessment:** STRONG contender. The fact that they own the entire telecom stack (built by FreeSWITCH creators) is a significant differentiator. HIPAA compliance is first-class, not an afterthought. The pricing is reasonable. The Agent SDK with multi-agent orchestration is sophisticated. Would be worth serious evaluation for healthcare voice AI use cases. Main concern: smaller ecosystem/community compared to Twilio.

**Sources:**
- https://signalwire.com/c/telecom-stack-ai-voice
- https://signalwire.com/pricing/ai-agent-pricing
- https://signalwire.com/pricing/voice
- https://signalwire.com/c/signalwire-compliance
- https://signalwire.com/products/baa-hipaa-compliance
- https://signalwire.com/use-cases/healthcare
- https://signalwire.com/blogs/press/open-source-agent-builder
- https://signalwire.com/developers/developer-toolkit
- https://signalwire.com/blogs/developers/swaig-101-ai-function-integration

---

### 7. OPENAI REALTIME API

**What it is:** Speech-to-speech API from OpenAI that processes and generates audio directly through a single model (not a chained pipeline).

**GA announcement:** August 28, 2025 (was in beta since Oct 2024)

**Latest model:** `gpt-realtime` (and `gpt-realtime-1.5` as of Feb 2026)
- Also: `gpt-realtime-mini` for cheaper workloads (dropped Dec 2025)

**Key capabilities:**
- Speech-to-speech (not STT -> LLM -> TTS pipeline)
- Single model processes and generates audio directly
- Reduces latency, preserves speech nuance
- Natural, expressive responses
- Two new voices: Cedar, Marin
- Remote MCP server support (auto-handles tool calls)
- Image input support
- **SIP phone calling support** (connect to PSTN, PBX, desk phones)
- Reusable prompts
- Asynchronous function calling (model continues talking while waiting)
- EU Data Residency

**Benchmarks (gpt-realtime):**
- Big Bench Audio: 82.8% (vs 65.6% previous model)
- MultiChallenge Audio: 30.5% (vs 20.6%)
- ComplexFuncBench Audio: 66.5% (vs 49.7%)

**Pricing:**
- $32/1M audio input tokens ($0.40 cached)
- $64/1M audio output tokens
- 20% reduction from previous model
- Token-based = **unpredictable costs**
- Real-world testing shows system prompt can 8x per-minute cost
- Can reach $1.63/min ($98/hr) with gpt-4o
- Estimated ~$18/hr in Deepgram's comparison

**Agents SDK:**
- JavaScript/TypeScript SDK available (`@openai/agents-realtime`)
- Voice agents quickstart for browser-based agents
- Ephemeral client tokens for secure browser connections
- Can build with Next.js or Vite

**Can you build voice agents with it?** YES, but:
- It's a building block, not a platform
- No built-in telephony (need SIP integration or separate provider)
- No built-in analytics, testing, or monitoring
- No built-in HIPAA compliance framework (though enterprise privacy commitments exist)
- Expensive for production workloads
- Best quality speech-to-speech model available

**Assessment:** The highest quality speech model, but not a complete platform. You'd use this as the LLM layer inside another platform (LiveKit, Vapi, etc.) or build your own infrastructure around it. The SIP support added in Aug 2025 makes direct telephony possible but still requires significant engineering. Cost is prohibitive for high-volume healthcare use. The `gpt-realtime-mini` model may change the economics.

**Sources:**
- https://openai.com/index/introducing-gpt-realtime/
- https://openai.github.io/openai-agents-js/guides/voice-agents/quickstart/
- https://www.reddit.com/r/singularity/comments/1pnk2wp/openai_just_stealthdropped_new_20251215_versions/
- https://community.openai.com/t/gpt-realtime-1-5-is-live-in-realtime-api/1374919

---

### 8. TWILIO + AI

**What it is:** Twilio's approach to AI voice agents via ConversationRelay (GA May 2025) and AI Assistants (Developer Preview).

#### ConversationRelay (GA)
- Converts spoken words to text and back
- WebSocket-based: connects Twilio Voice to your AI/LLM
- BYOLLM: Works with OpenAI, Anthropic, DeepSeek, Mistral, and others via LiteLLM
- **HIPAA eligible** (as of GA)
- Supports multiple STT/TTS providers: ElevenLabs, Deepgram, Google, Amazon
- Connects with Twilio Conversational Intelligence (analytics)
- Simple TwiML integration

**How it works:**
```xml
<Response>
  <Connect action="https://myserver.com/connect_action">
    <ConversationRelay url="wss://mywebsocketserver.com/websocket"
      welcomeGreeting="Hi! Ask me anything!" />
  </Connect>
</Response>
```

- You handle the LLM logic on your WebSocket server
- Twilio handles telephony, STT, TTS
- Full control over conversation logic

#### AI Assistants (Developer Preview)
- Higher-level abstraction for building customer-aware agents
- Omnichannel (SMS, Voice, etc.)
- Tools and Knowledge sources (RAG without managing pipeline)
- Segment integration for customer profiles
- Guardrails: prompt injection detection, content moderation
- Handoff to Twilio Flex contact center
- Still in Developer Preview / Alpha quality

**Healthcare customer:** OhMD using ConversationRelay for AI-powered patient communication ("Nia" voice assistant)

**Assessment:** Twilio's approach is more "bring your own AI" than a turnkey platform. ConversationRelay is the infrastructure layer -- you still need to build the agent logic. This gives maximum flexibility but requires more engineering. The HIPAA eligibility is important. Main advantage: existing Twilio telephony infrastructure, phone numbers, routing. Main disadvantage: you're assembling pieces, not getting a platform.

**Sources:**
- https://twilio.com/en-us/blog/conversationrelay-generally-available
- https://twilio.com/en-us/blog/introducing-twilio-ai-assistants
- https://www.twilio.com/en-us/blog/developers/tutorials/product/ai-agent-conversationrelay-voice-mistral
- https://twilioalpha.com/ai-assistants

---

## COMPARISON MATRIX: Emerging Platforms vs. Main Platforms

| Platform | Type | Full Agent Platform? | Telephony? | HIPAA? | Healthcare? | Pricing | SDK? |
|---|---|---|---|---|---|---|---|
| **Vocode** | Open-source + hosted | Yes | Yes | Beta | Limited | Unknown | Python |
| **Hamming AI** | Testing/QA only | No (testing) | N/A | Testing support | Strong | Unknown | N/A |
| **Deepgram** | STT/TTS + Voice Agent API | Yes (GA) | Limited (no native) | Yes | Yes (medical STT) | $4.50/hr | Python, JS |
| **PlayHT/Play.ai** | TTS + no-code agents | Yes (simple) | Yes | Not mentioned | Demo only | Unknown | API |
| **Thoughtly** | No-code voice agents | Yes (simple) | Yes (BYOC) | Not mentioned | Listed but basic | Custom | No-code |
| **SignalWire** | Full telecom + AI | Yes | Yes (owns stack) | Yes (full BAA) | Yes (healthcare page) | $0.16/min | Python |
| **OpenAI Realtime** | Speech-to-speech model | No (building block) | SIP support | Enterprise only | No | ~$18/hr | JS |
| **Twilio + AI** | Telephony + BYOAI | Partial (ConvRelay) | Yes (owns stack) | Yes (HIPAA eligible) | Yes (OhMD case) | Usage-based | TwiML + WS |

---

## KEY INSIGHT: PAIRTEAM IS ALREADY USING ELEVENLABS

This is the most important finding for the voice AI comparison report. Pair Team has already chosen ElevenLabs Agents Platform as their voice AI provider. They've:
- Built and deployed a constellation of AI agents ("Flora")
- Run 3,121 safety simulations
- Achieved 99.9% success rate on safety-critical interactions
- Deployed to thousands of patients
- Average conversation duration >9 minutes

This means any voice AI platform comparison for Pairteam-like use cases should benchmark against ElevenLabs as the incumbent, not just the platforms in the original comparison list.

**ElevenLabs pricing context (from Deepgram comparison):** ~$5.79/hr

---

## PLATFORMS WORTH SERIOUS CONSIDERATION (for healthcare voice AI)

### Tier 1: Full platforms with healthcare readiness
1. **SignalWire** - Full stack, HIPAA first-class, good pricing, multi-agent orchestration
2. **Deepgram Voice Agent API** - Best price/performance, HIPAA, on-prem option, medical STT
3. **Twilio ConversationRelay** - HIPAA eligible, massive infrastructure, but BYOAI

### Tier 2: Worth monitoring
4. **Vocode** - Open source flexibility, HIPAA beta, but uncertain company trajectory
5. **OpenAI Realtime API** - Best model quality but cost-prohibitive, not a platform

### Tier 3: Not suitable for healthcare
6. **PlayHT/Play.ai** - No HIPAA, too simplistic
7. **Thoughtly** - No HIPAA, SMB-focused, mixed reviews

### Complementary tool (any tier)
- **Hamming AI** - Essential for voice agent testing/QA regardless of platform choice
