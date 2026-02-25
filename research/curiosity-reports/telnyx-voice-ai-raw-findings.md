# Telnyx Voice AI: Raw Research Findings

**Date:** 2026-02-25
**Context:** Evaluating Telnyx as a platform for building a healthcare voice agent for Pairteam (outbound patient engagement, complex multi-turn conversations, behavioral rules)

---

## 1. Architecture & How It Works

### Full-Stack Approach (Own Telephony + AI Inference)

Telnyx is fundamentally a **telecom company that added AI**, not an AI company that added telephony. Founded in 2009 as a programmable telephony provider, they have evolved to own the entire stack:

- **Licensed carrier in 30+ countries** with direct PSTN access in 100+ countries
- **Private MPLS fiber backbone** connecting data centers and PoPs globally
- **Co-located GPU clusters** alongside telephony PoPs for inference
- **Own STT, TTS, and LLM hosting** (plus bring-your-own options)
- ~261 employees, $16M annual revenue, headquartered in Austin, TX

The key architectural claim: "Most Voice AI platforms sit on top of someone else's telephony stack. Telnyx runs the AI within our telephony layer." -- Ian Reither, COO

**Source:** https://telnyx.com/resources/build-great-ai-voice-agents

### The Three Pillars

Telnyx frames their platform around three pillars:

| Pillar | What It Means |
|--------|---------------|
| Infrastructure | Dedicated GPUs + private MPLS network with 18 global PoPs |
| Telephony | Licensed carrier in 30+ countries with direct PSTN access |
| AI Stack | Instantly swap STT engines, TTS voices, LLMs from a dropdown |

**Source:** https://telnyx.com/resources/build-great-ai-voice-agents

### AI Missions Feature (NEW - Feb 11, 2026)

AI Missions is a **task tracking and orchestration API designed for AI agents -- not developers -- to call directly.** This is their newest major feature.

**What it does:**
- Persist state across restarts for long-running tasks with retries/recovery
- Collect structured insights from completed calls (quotes, availability, sentiment) using customizable templates
- Deploy voice and SMS agents with custom instructions, assign phone numbers, schedule calls
- Track execution step-by-step with complete audit trail
- Create missions with goals like "find the cheapest contractor" or "book a dinner reservation"

**How it works (BYOA - Bring Your Own Agent):**
1. Set up a Clawdbot or compatible agent
2. Install the Telnyx Toolkit (from clawhub.ai/dotcom-squad/telnyx-toolkit)
3. Give the agent a goal
4. The agent calls the Missions API to create missions, log steps, extract insights, persist state

The Toolkit includes a SKILL.md that teaches the agent how to use the API for multi-call workflows, IVR navigation, insight extraction, error recovery.

**Use cases:**
- Parallel outreach (call multiple vendors simultaneously)
- Sequential negotiation (use info from call 1 in call 5)
- Appointment booking across multiple providers
- IVR navigation and data extraction
- Surveys and research

**CRITICAL NOTE:** AI Missions is about **multi-call orchestration**, not single-call conversation control. It coordinates *across* calls, not *within* a single complex conversation. For Pairteam's use case of a single complex outbound call, this is less directly relevant but could be useful for batch outreach.

**Source:** https://telnyx.com/resources/ai-missions-launch
**Source:** https://telnyx.com/release-notes/missions-multi-call-orchestration

### Voice AI Agent Builder

Two modes:
1. **No-code UI** -- AI Assistant Builder in the Mission Control Portal. Define behavior with natural-language instructions and greetings. Test via in-browser simulator. Deploy in minutes.
2. **Full API** -- REST APIs + webhooks for complete control. Supports TeXML (Twilio-compatible markup language). Flexible APIs and MCP server support.

**Source:** https://telnyx.com/products/voice-ai-agents
**Source:** https://telnyx.com/resources/voice-AI-agent-platform

### Edge GPU Deployment

GPUs are co-located with telephony PoPs:
- US infrastructure: already deployed
- Europe: sub-200ms RTT across the continent (GPUs in same data halls as telephony core)
- Plans to expand to MENA and Australia

"By embedding its inference stack directly inside the same data halls as its pan-European telephony core, Telnyx delivers sub-200ms round-trip time (RTT) to end users across the continent."

**Source:** https://telnyx.com/resources/voice-ai-agents-compared-latency

---

## 2. Control & Steerability

### How Agent Behavior Is Defined

Agent behavior is defined primarily through **natural language instructions** (system prompts). This is similar to Vapi and Retell -- you write instructions telling the agent how to behave, what tone to use, what rules to follow.

Telnyx's approach to conversation control:

**Instructions (System Prompt)**
- Natural language instructions define the agent's purpose, tone, and behavioral rules
- Prompt refactoring tool in Mission Control helps clean up prompts that have grown organically
- They acknowledge prompt drift as a real production problem and have tooling to address it

**Source:** https://telnyx.com/resources/when-voice-ai-prompts-stop-scaling

### Dynamic Variables (Dynamic Context Injection)

Rich system for injecting per-call context into conversations:

- **Syntax:** `{{variable_name}}` in instructions, greeting, or tools
- **Resolution order (precedence):**
  1. API injection (via `AIAssistantDynamicVariables` parameter in outbound call request) -- highest priority
  2. Custom SIP headers (`X-Variable-Name` becomes `{{variable_name}}`)
  3. Dynamic Variables Webhook (POST to your URL at conversation start, 1-second timeout)
  4. Default values in Assistant builder
  5. Raw form (unresolved `{{variable_name}}`)

**For Pairteam this is critical** -- you can inject patient name, condition, Pairteam service details, etc. at call initiation time via the API.

The webhook approach is powerful: at conversation start, Telnyx POSTs to your URL with caller info, and you return:
- `dynamic_variables` -- personalization data
- `memory` -- conversation history query
- `conversation` -- metadata (customer tier, preferred language, timezone)

Must respond within 1 second or call proceeds with fallbacks.

System variables also available: `{{telnyx_current_time}}`, `{{telnyx_conversation_channel}}`, `{{telnyx_agent_target}}`, `{{telnyx_end_user_target}}`, `{{call_control_id}}`

**Source:** https://developers.telnyx.com/docs/inference/ai-assistants/dynamic-variables

### Custom LLMs (Bring Your Own Model)

Telnyx supports pointing AI Assistants at **any OpenAI-compatible model endpoint**:
- Azure OpenAI Service
- AWS Bedrock
- Baseten, Replicate, together.ai
- Self-hosted (vLLM, sglang, TGI on your own GPUs)
- Custom fine-tuned models

**Requirement:** Endpoint must implement OpenAI Chat Completions API (`/v1/chat/completions`)

**Latency trade-off:** Default Telnyx inference is sub-200ms RTT. External endpoints add:
- Near Telnyx PoP (e.g., us-east-1): +20-50ms
- Remote endpoints: +100-300ms per turn
- Still faster than most stitched stacks, but no longer guaranteed sub-200ms

**Built-in LLM options:** Telnyx hosts open-source models including Qwen3-235B-A22B on their own GPUs, plus passes through OpenAI (GPT-4o, GPT-4.1, GPT-5, GPT-5.1), Google, Anthropic, Groq, xAI via BYOK.

**Source:** https://developers.telnyx.com/docs/inference/ai-assistants/custom-llm
**Source:** https://telnyx.com/resources/run-telnyx-voice-ai-assistants-with-any-open-ai-compatible-llm

### Tool Calling / Function Calling

Telnyx supports tool calling during live conversations:
- **Real-time tool calling** that can invoke external APIs mid-conversation
- Tools are defined in the assistant configuration
- Dynamic variables can be used in tool definitions
- 30+ native integrations available (Airtable, Atlassian, Stripe, Notion, Shopify, etc.)
- Webhook notifications to external systems
- Conditional logic based on conversation content

**Gather Using AI API** -- specialized endpoint for gathering structured data:
- Pass JSON Schema of parameters to collect
- Voice assistant attempts to gather the information
- Webhooks for: `call.ai_gather.message_history_updated`, `call.ai_gather.partial_results`, `call.conversation.ended`, `call.ai_gather.ended`

**Source:** https://developers.telnyx.com/api-reference/call-commands/gather-using-ai
**Source:** https://telnyx.com/products/voice-ai-agents

### Conversation State Management

- **Memory feature** -- assistant can query past conversations for context
- Dynamic variables webhook can return a `memory.conversation_query` to pull relevant past interactions
- Conversation metadata can be set and tracked
- Multi-agent handoffs supported -- "seamlessly transfer calls or orchestrate smooth conversations across multiple AI agents on a single call"

### Complex Branching Logic

**This is where Telnyx's approach gets interesting and potentially limiting for Pairteam:**

Telnyx does NOT appear to have a visual conversation flow builder like Bland AI's Conversational Pathways or Voiceflow's flow designer. Instead, control is achieved through:

1. **Prompt engineering** -- behavioral rules in natural language instructions
2. **Tool calling** -- functions that the agent can invoke based on conversation state
3. **Multi-agent handoffs** -- transfer between specialized agents on a single call
4. **Gather Using AI** -- structured data collection with defined schemas
5. **Call Control API** -- programmatic control of call state (hold, transfer, record, etc.)

The Telnyx blog article on context engineering explicitly recommends:
- Separation of concerns (instructions, tools, dynamic state, conversation history, examples as separate layers)
- Lean context to maintain low latency
- Clear contracts defining agent purpose and rules
- Treating context like software (test suites, incremental refactoring)

**Source:** https://telnyx.com/resources/voice-ai-context-engineering

### Start Speaking Plan (Turn-Taking Control)

Granular control over when the agent starts responding:

```json
"interruption_settings": {
    "start_speaking_plan": {
      "wait_seconds": 0.4,
      "transcription_endpointing_plan": {
        "on_punctuation_seconds": 0.1,
        "on_no_punctuation_seconds": 1.5,
        "on_number_seconds": 0.5
      }
    }
  }
```

Four types of pauses handled differently:
1. `on_number_seconds` -- digit sequences (people reading numbers slowly)
2. `on_no_punctuation_seconds` -- uncertain pauses (looking at screen)
3. `on_punctuation_seconds` -- high-confidence endpoints (period/question mark)
4. `wait_seconds` -- baseline wait time

Telnyx chose **explicit controls over "smart endpointing" ML** -- reasoning: "You know your use case better than an algorithm does."

**Source:** https://telnyx.com/resources/control-voice-ai-response-timing-with-start-speaking-plan

---

## 3. Telephony Advantages

### Own PSTN Network

- **Licensed carrier in 30+ countries** (not a virtual provider or API wrapper)
- Direct PSTN access in 100+ countries
- **Private MPLS backbone** -- voice traffic never touches public internet
- Direct peering agreements with major carriers
- PSTN replacement in 60+ countries
- QoS policies prioritize voice traffic
- Enhanced DDoS protection
- Predictable latency and jitter

"Unlike competitors who rely on public internet routing, voice traffic is run on a private network and carried across dedicated infrastructure."

**Source:** https://telnyx.com/resources/voice-ai-agents-compared-latency

### SIP Trunking

- Full SIP trunking product with API-based call management
- TeXML support (Twilio-compatible markup for voice applications)
- WebRTC for browser-based calling
- Call Control API for programmatic call management
- Can be used as telephony provider for LiveKit (SIP trunk configuration guide exists)

**Source:** https://telnyx.com/products/voice-api

### Latency Benchmarks (Telnyx's Own Claims)

| Provider | Latency Claim |
|----------|---------------|
| **Telnyx** | Sub-200ms RTT (audio round-trip) |
| Vapi | ~465ms optimal, 3-4 seconds reported by users |
| Twilio | 950ms average |
| Retell AI | ~600ms |
| Bland AI | Inconsistent, premium pricing for mixed results |

*Note: These are Telnyx's published benchmarks in their own blog. Take with appropriate grain of salt.*

**Source:** https://telnyx.com/resources/voice-ai-agents-compared-latency

### Global Coverage

- 30+ countries with carrier licenses
- 100+ countries with local numbers
- 18 global PoPs
- 30+ languages supported
- HD voice with 16kHz wideband codecs

---

## 4. Healthcare-Specific Capabilities

### HIPAA Compliance

- Signs **Business Associate Agreements (BAAs)**
- End-to-end encryption (TLS 1.2+)
- Encrypted data storage with customer-managed keys
- Access controls with MFA
- Audit logging for all PHI access
- Incident response procedures
- SOC 2 Type II certification (claimed)
- Regional GPU deployment for data locality
- Private network routing (voice data never touches public internet)

**Source:** https://telnyx.com/resources/ai-voice-agents-for-healthcare

### Epic EHR Integration (Launched Nov 2025)

Direct integration between Telnyx Voice AI and Epic:
- Look up patient records in real-time during calls
- Manage scheduling using Epic's scheduling rules
- Automate outbound outreach (reminders, post-visit instructions)
- Trigger follow-up calls based on Epic events (lab results, care plan changes, discharge)
- Log responses back to Epic
- Connected via Epic MCP (Model Context Protocol)

**Integration flow:**
1. Call lands on Telnyx's private network
2. AI Agent handles speech recognition with sub-second latency
3. Agent connects to Epic MCP for real-time data (identity, visit history, scheduling)
4. Data written back to EHR
5. Escalation/routing controlled by Telnyx Call Control

**Source:** https://telnyx.com/resources/epic-integration-voice-ai-healthcare
**Source:** https://telnyx.com/release-notes/integration-telnyx-epic-voiceai

### Healthcare Use Cases Documented

| Use Case | Volume | Complexity | ROI Timeline |
|----------|--------|------------|--------------|
| Patient intake & registration | High | Low | 3-6 months |
| Symptom triage & care navigation | Medium-high | Medium | 6-9 months |
| Appointment scheduling & reminders | Very high | Low | 3-6 months |
| Medication adherence & refill | Medium | Medium | 9-12 months |
| Chronic care follow-up | Medium | High | 12+ months |

Healthcare-specific claims:
- 99% accuracy in symptom triage (from 300K+ simulated interactions reviewed by clinicians)
- 70% reduction in administrative tasks
- 50-60% reduction in call abandonment rates
- Wait times from 11+ minutes to under 2 minutes
- No-show rates down 25-35%
- $80K-$100K+ annual savings per eliminated FTE

**Source:** https://telnyx.com/resources/ai-voice-agents-for-healthcare

### Healthcare Customers

- Updox
- Doximity
- American Red Cross
- Weave

**Source:** https://telnyx.com/solutions/healthcare

### "11 Best Voice AI Agents for Healthcare" Article

Telnyx-authored listicle ranking themselves #1. Key competitors identified:
1. **Telnyx** (themselves)
2. **Prosper AI** -- healthcare-native, 80+ EHR integrations, no-code customization
3. **CloudTalk** -- healthcare-specific, maintains conversational context
4. **ElevenLabs** -- voice quality layer
5. **Hyro** -- enterprise healthcare integrations
6. **Retell AI** -- medical terminology ASR with 95%+ accuracy, drag-and-drop builder
7. **Assort Health** -- specialty-specific scheduling
8. **Zocdoc's Zo** -- 24/7 appointment booking
9. **Synthflow** -- no-code, acknowledged "as call flows get complicated it might be difficult to manage"
10. **PolyAI** -- enterprise, multilingual
11. **Callin.io** -- chronic care, mental health (47% better therapy homework completion)

**Source:** https://telnyx.com/resources/11-best-voice-ai-agents-healthcare

---

## 5. Pricing

### Pay-As-You-Go Breakdown

| Component | Price |
|-----------|-------|
| **Conversational AI base** | $0.06 / minute |
| Call Control | $0.002 / minute |
| WebRTC | $0.002 / minute |
| Inbound telephony | SIP trunking fee (separate) |
| Outbound telephony | SIP trunking fee (separate) |
| SMS Messaging | From $0.004 / message + carrier fees |
| **Speech-to-Text (STT)** | **FREE** |
| **Telnyx TTS (Natural & NaturalHD)** | **FREE** |
| Third-party TTS (ElevenLabs, Azure, AWS) | Provider costs |
| Cloud Storage (knowledge base) | $0.006 / GiB/month |

### LLM Pricing (per 1,000 tokens)

**Telnyx-hosted (Qwen3-235B-A22B):**
- Input: $0.0006
- Cached Input: $0.0004
- Output: $0.002

**OpenAI (passed through):**
- GPT-4.1: Input $0.002 / Output $0.008
- GPT-4o: Input $0.0025 / Output $0.01
- GPT-5: Input $0.00125 / Output $0.01

Other providers (Anthropic, Google, Groq, xAI) via BYOK at their own rates.

### Estimated All-In Cost

Using their calculator with 1,000 calls/month, 5 min/call:
- Conversational AI base: included
- LLM (OpenAI): ~$0.025/min
- TTS: $0.00
- Voice API: $0.060/min
- **Total: ~$0.085/min** (+ telephony separately)

Telnyx claims "customers typically save 45% when switching from another provider."

**Source:** https://telnyx.com/pricing/conversational-ai

---

## 6. Developer Experience

### API & SDK

- REST APIs with webhook-based event model
- TeXML (Twilio-compatible XML markup for voice)
- Call Control API for programmatic call management
- Python, Node.js, Ruby examples in documentation
- MCP server support for agent deployment and management
- Documentation at developers.telnyx.com (uses Mintlify)
- Has an `llms.txt` file for AI consumption of docs

### Mission Control Portal

- No-code AI Assistant Builder
- In-browser agent simulator/testing
- Prompt refactoring tool (AI-assisted cleanup of degraded prompts)
- Conversation logs and transcript viewer
- Webhook logs for debugging
- Integration credentials management
- AI Missions dashboard with full audit trail

### Testing Capabilities

- "Comprehensive testing -- confidently launch agents after running automated multi-path simulations and automated tests for accuracy, reliability, and response quality."
- In-browser test calls
- Publicly shareable AI widget demos with client-side latency measurement

### Forward Deployed Engineers

Telnyx offers to embed their engineers with customer teams to build custom prototypes and deploy production-ready solutions. This is a significant differentiator for complex implementations.

**Source:** https://telnyx.com/products/voice-ai-agents

### Migration Tools

"Instantly migrate your existing AI agents to our platform from Vapi, ElevenLabs, and more. Import agents with a single click and reuse existing voice flows, scripts, and settings without rebuilding."

---

## 7. Limitations & Criticisms

### Support Quality (Major Red Flag from Reddit)

**Multiple Reddit complaints about Telnyx support quality:**

r/VOIP, 2023: "In all of my years in tech this is BY FAR the worst support ever. Never mind that if you chat then they say they are working on it and hours and hours go by. I will literally die before I ever hear back any useful information from them."
- Score: 14 upvotes

r/VOIP, 2022: "I have tickets opened for months on end, but nobody is actually doing anything... They keep asking us to provide fresh log samples because they took too long to look into the issue and their call logs are only kept for 72 hours."
- Score: 8 upvotes

**Source:** https://www.reddit.com/r/VOIP/comments/13jaykz/telnyx_support_is_trash/
**Source:** https://www.reddit.com/r/VOIP/comments/vdl1bx/telnyx_support_is_absolute_garbage/

*Note: These complaints are from 2022-2023 and may predate their Voice AI pivot. They now advertise "24/7 support and a dedicated customer success manager" on contract plans.*

### Bland AI's Critique of Telnyx

From Bland AI's comparison blog:
- "Originally founded as a programmable telephony provider, Telnyx has evolved" -- i.e., AI was bolted on
- "Telnyx's TrustPilot reviews don't share a completely positive story. One repeated concern was an overwhelming lack of customer support."
- "Higher technical barrier to entry... Users report a steep learning curve, needing to comb through the technical documentation"
- Dynamic pricing system "can be difficult to get to grips with"

**Source:** https://www.bland.ai/blogs/bland-vs-telnyx-whos-the-better-voice-ai-option-for-enterprises

### STT Review (Third-Party, 6.2/10)

VoiceTypingTools rated Telnyx STT at **6.2/10**:
- "Best for teams already running voice calls through Telnyx who want to add transcription without a new vendor."
- "Skip if you need a standalone STT API with broad language support"
- Only 6 languages supported for STT
- No offline mode
- No free trial

**Source:** https://www.voicetypingtools.com/tools/telnyx-stt

### Conversation Control Limitations (Inferred)

Based on the research, key limitations for complex agent behavior:

1. **No visual flow builder** -- Unlike Bland AI (Conversational Pathways), Voiceflow, or Synthflow, Telnyx relies on prompt engineering + tool calling for conversation control. No drag-and-drop conversation designer for complex branching.

2. **Prompt-based control** -- For complex behavioral rules like Pairteam's multi-step conversation flows, all logic must be encoded in natural language system prompts. Telnyx's own blog acknowledges this creates maintainability problems: "Models and latency rarely kill voice AI systems. Decaying instructions do."

3. **No explicit state machine** -- Conversation state is managed implicitly through the LLM's context window and tool calls, not through an explicit state machine or flow definition. This makes complex branching harder to reason about and test.

4. **Limited language support for STT** -- Only 6 languages (could be an issue for diverse patient populations)

5. **Telephony-first DNA** -- Multiple sources note Telnyx was built as a telecom provider first. The AI capabilities, while increasingly sophisticated, were layered on top of a telephony platform rather than being built AI-first.

### Telnyx vs LiveKit Comparison

Telnyx's own positioning against LiveKit:
- "Telnyx doesn't replace how you build agents. It upgrades what they run on."
- "Keep your LiveKit setup and power it with native telephony"
- They explicitly position as LiveKit's **infrastructure layer**, not a replacement
- Telnyx provides SIP trunk configuration guides for LiveKit
- LiveKit integration documentation exists for using Telnyx inference in LiveKit agents

This is telling: **Telnyx sees itself as complementary to LiveKit, not competing with it on agent logic.** You could use LiveKit for agent orchestration and Telnyx for telephony + inference.

**Source:** https://telnyx.com/the-best-livekit-alternative

### Not Included in Major Comparison

The Medium "20+ AI Voice Agent Platforms" comparison by Call Notes (Jan 2026) did **not include Telnyx** in their testing of 12 platforms. They tested Retell, Vapi, AgentVoice, Bland, Synthflow, ElevenLabs, PolyAI, Voiceflow, LiveKit, Cartesia, Hume, and Whisper. Telnyx's absence from this independent comparison is notable.

**Source:** https://medium.com/@callnotes/i-researched-20-ai-voice-agent-platforms-heres-what-i-found-b16395ff2126

---

## 8. Key Insights for Pairteam Use Case

### Strengths for Pairteam

1. **HIPAA compliance with BAA** -- essential for healthcare
2. **Epic EHR integration** -- if Pairteam uses Epic, this is a major advantage
3. **Dynamic variables** -- can inject patient name, condition, appointment details into each outbound call
4. **Low latency** -- sub-200ms RTT for natural conversation
5. **Outbound calling capability** -- first-class outbound support with AI Missions for batch orchestration
6. **Pricing** -- competitive at ~$0.085/min all-in, STT and TTS included free
7. **Custom LLM support** -- can bring Anthropic models via BYOK for complex reasoning
8. **Forward Deployed Engineers** -- for complex healthcare implementation

### Weaknesses for Pairteam

1. **No visual conversation flow builder** -- complex behavioral rules must be encoded in prompts. For a healthcare agent with many branching paths (depression education, medication questions, insurance verification, appointment scheduling), this could become hard to maintain.

2. **Prompt-based steerability** -- Pairteam's requirement for "complex behavioral rules and conversation flows" is the hardest thing to achieve with prompt-only control. Telnyx acknowledges this problem in their own content but their solution is better prompt engineering, not structured flow definition.

3. **Limited STT language support** -- 6 languages may not cover all patient populations

4. **Support quality concerns** -- Reddit complaints are older but concerning for a healthcare deployment where issues need rapid resolution

5. **Telephony-first vs. AI-first** -- The platform's DNA is telephony infrastructure. For the most sophisticated agent logic, a tool like LiveKit gives more programmatic control (at the cost of building more yourself).

6. **State management is implicit** -- No explicit conversation state machine. State is maintained via LLM context window and tool calls. For complex multi-step healthcare conversations with strict compliance requirements, explicit state tracking may be more reliable.

### The Hybrid Option

Telnyx + LiveKit is explicitly supported:
- Use **Telnyx for telephony** (SIP trunking, phone numbers, PSTN connectivity)
- Use **Telnyx for inference** (their co-located GPUs for low latency)
- Use **LiveKit for agent orchestration** (explicit conversation state management, complex branching logic)

This could give Pairteam the best of both worlds: Telnyx's telephony infrastructure and latency advantages with LiveKit's developer-first agent control.

---

## 9. Source URLs (Complete List)

### Telnyx Official
- Products page: https://telnyx.com/products/voice-ai-agents
- Voice API: https://telnyx.com/products/voice-api
- Pricing: https://telnyx.com/pricing/conversational-ai
- Healthcare solution: https://telnyx.com/solutions/healthcare
- Healthcare communications: https://telnyx.com/resources/healthcare-communications-best-practices
- AI Missions launch: https://telnyx.com/resources/ai-missions-launch
- AI Missions release notes: https://telnyx.com/release-notes/missions-multi-call-orchestration
- Epic integration blog: https://telnyx.com/resources/epic-integration-voice-ai-healthcare
- Epic integration release notes: https://telnyx.com/release-notes/integration-telnyx-epic-voiceai
- Healthcare voice AI use cases: https://telnyx.com/resources/ai-voice-agents-for-healthcare
- 11 best healthcare voice AI: https://telnyx.com/resources/11-best-voice-ai-agents-healthcare
- Healthcare front-desk automation: https://telnyx.com/resources/best-voice-ai-for-healthcare-front-desk-automation
- After-hours patient calls: https://telnyx.com/resources/ai-to-handle-after-hours-patient-calls
- Voice AI for developers: https://telnyx.com/resources/voice-ai-for-developers
- Building great AI voice agents: https://telnyx.com/resources/build-great-ai-voice-agents
- Voice AI that works on real calls: https://telnyx.com/resources/how-to-build-a-voice-ai-product-that-does-not-fall-apart-on-real-calls
- Latency benchmarks: https://telnyx.com/resources/voice-ai-agents-compared-latency
- Context engineering: https://telnyx.com/resources/voice-ai-context-engineering
- Prompt scaling problems: https://telnyx.com/resources/when-voice-ai-prompts-stop-scaling
- Start Speaking Plan: https://telnyx.com/resources/control-voice-ai-response-timing-with-start-speaking-plan
- Custom LLM blog: https://telnyx.com/resources/run-telnyx-voice-ai-assistants-with-any-open-ai-compatible-llm
- Vendor lock-in avoidance: https://telnyx.com/resources/vendor-lock-in-voice-ai-stt-tts
- LiveKit alternative page: https://telnyx.com/the-best-livekit-alternative
- No-code AI: https://telnyx.com/resources/no-code-ai
- n8n integration: https://telnyx.com/resources/n8n-ai-voice-agent
- AI Assistant builder: https://telnyx.com/resources/ai-assistant-builder
- State of Voice AI 2026: https://telnyx.com/resources/state-of-voice-ai-trust-execution-2026
- Top voice AI providers 2026: https://telnyx.com/resources/top-voice-ai-providers
- Telnyx Flow: https://telnyx.com/resources/how-we-built-flow
- ISV solution: https://telnyx.com/solutions/isv

### Telnyx Developer Docs
- Dynamic Variables: https://developers.telnyx.com/docs/inference/ai-assistants/dynamic-variables
- Custom LLM: https://developers.telnyx.com/docs/inference/ai-assistants/custom-llm
- Gather Using AI API: https://developers.telnyx.com/api-reference/call-commands/gather-using-ai
- AIGather TeXML: https://developers.telnyx.com/docs/voice/programmable-voice/texml-verbs/aigather

### Third-Party Sources
- Medium comparison (20+ platforms): https://medium.com/@callnotes/i-researched-20-ai-voice-agent-platforms-heres-what-i-found-b16395ff2126
- Bland vs Telnyx: https://www.bland.ai/blogs/bland-vs-telnyx-whos-the-better-voice-ai-option-for-enterprises
- Reddit support complaint 1: https://www.reddit.com/r/VOIP/comments/13jaykz/telnyx_support_is_trash/
- Reddit support complaint 2: https://www.reddit.com/r/VOIP/comments/vdl1bx/telnyx_support_is_absolute_garbage/
- STT review (6.2/10): https://www.voicetypingtools.com/tools/telnyx-stt
- Telnyx ClawdTalk announcement: https://telecomreseller.com/2026/02/13/telnyx-introduces-clawdtalk-giving-ai-agents-a-voice/
- Weekend project (Ultravox + Telnyx): https://medium.com/@kapincev/voice-ai-agent-in-a-weekend-ultravox-telnyx-and-500-lines-of-javascript-ad35740260c6
- MyAIFrontDesk on Telnyx healthcare: https://www.myaifrontdesk.com/blogs/revolutionizing-patient-engagement-the-power-of-telnyx-voice-ai-in-healthcare
- LiveKit vs Vapi comparison: https://modal.com/blog/livekit-vs-vapi-article
- YouTube test of 6 platforms: https://www.youtube.com/watch?v=sDvtiF5qQik
