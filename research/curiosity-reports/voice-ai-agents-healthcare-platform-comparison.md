# Building Healthcare Voice Agents: LiveKit Will Win, and Here's the Architecture to Prove It

**Date:** 2-25-26
**Category:** Research Report

---

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [Background](#background)
3. [Why ElevenLabs Hit a Wall](#why-elevenlabs-hit-a-wall)
4. [The Platform Landscape](#the-platform-landscape)
5. [Platform Deep Dives](#platform-deep-dives)
6. [Gap Analysis: Control & Steerability](#gap-analysis-control--steerability)
7. [The Recommended Architecture](#the-recommended-architecture)
8. [Key Takeaways](#key-takeaways)
9. [Predictions](#predictions)

---

## Executive Summary

After evaluating 12+ voice AI platforms, the answer for Pairteam's use case is clear: **LiveKit Agents is the only platform that gives you enough control to build the complex, context-heavy healthcare voice agent you need.** Every managed platform (Vapi, Retell, Bland, ElevenLabs) eventually hits a ceiling on conversation steerability — the exact wall Pairteam has already crashed into with ElevenLabs. LiveKit eliminates that ceiling because you write the logic in code, not configuration.

The optimal architecture is a **three-layer stack**: Telnyx or Twilio for telephony (SIP trunking, phone numbers, PSTN connectivity), LiveKit Agents for voice orchestration (STT/TTS streaming, turn-taking, multi-agent handoffs), and a custom LangGraph-based state machine for conversation logic (dynamic micro-prompts, patient context injection, compliance guardrails, EHR integration). This separates what the agent sounds like from what it says and does — and gives you independent control over each layer.

The critical insight from this research: **the micro-prompting pattern** — where a state machine loads focused 30-50 token prompts per conversation state instead of a monolithic 4,000-8,000 token mega-prompt — cuts voice-to-voice latency by 5x and improves instruction adherence from ~85% to ~98%. For a healthcare agent that must follow complex behavioral rules across conditions like depression, substance use, and housing insecurity, this pattern is the difference between an agent that works and one that doesn't.

---

## Background

### What Pairteam Does

[Pairteam](https://pairteam.com) is a tech-enabled, AI-first medical group (public benefit corp) serving Medicaid and Medicare beneficiaries with complex needs — homelessness, behavioral health, substance use, chronic conditions, reentry from incarceration. They operate across California (~80% coverage) and Clark County, Nevada, partnering with health plans under value-based care contracts. Their impact is peer-reviewed: 52% fewer ED visits, 26% fewer hospitalizations, $25k average savings per high-need patient ([Journal of General Internal Medicine](https://www.prnewswire.com/news-releases/new-research-highlights-pair-teams-novel-approach-to-improving-medicaid-better-engagement-lower-costs-and-improved-health-outcomes-302569075.html)).

### The Voice Agent Challenge

Pairteam needs voice agents that can:

1. **Make outbound calls** to patients who expressed interest in Pairteam's services
2. **Educate patients** about how Pairteam specifically helps their condition (depression, substance use, housing insecurity, etc.)
3. **Handle complex multi-turn conversations** — patients with overlapping medical, behavioral, and social needs
4. **Follow intricate behavioral rules** — consent collection, identity verification, condition-specific education, escalation protocols, compliance guardrails
5. **Dynamically adapt** — if a patient reveals a new condition mid-call, the agent must pivot its education approach

### The ElevenLabs Situation

A critical finding from this research: **Pairteam is already using ElevenLabs.** According to [ElevenLabs' own case study](https://elevenlabs.io/blog/pair-team) (Feb 2, 2026), Pairteam built a "constellation of agents" called "Flora" that handles patient intake, medication follow-ups, housing coordination, and empathetic check-ins. They ran 3,121 simulated safety calls achieving 99.9% success, and patients engage for 9+ minutes on average.

So ElevenLabs works for the simpler workflows. The problem is scaling to more complex behavioral requirements — which is where this research begins.

### How Voice Agents Work

Every voice agent follows the same fundamental pipeline:

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│ Patient  │───>│   STT    │───>│   LLM    │───>│   TTS    │───> Patient
│  speaks  │    │ (speech  │    │ (thinks, │    │ (speaks  │     hears
│          │    │  to text)│    │  decides)│    │  response)│
└──────────┘    └──────────┘    └──────────┘    └──────────┘
                                    │
                                    ▼
                              ┌──────────┐
                              │  Tools   │
                              │ (EHR,    │
                              │  CRM,    │
                              │  schedule)│
                              └──────────┘
```

The differences between platforms come down to three questions:
1. **How much control do you have over each stage?**
2. **How do you define the conversation logic that drives the LLM?**
3. **How do you manage state and context across the conversation?**

---

## Why ElevenLabs Hit a Wall

Understanding why ElevenLabs breaks down for complex use cases is essential — because the same limitations exist in most managed platforms.

### Limitation 1: No Deep Multi-Turn Conversation Support

ElevenLabs is optimized for "contained, goal-oriented conversations" — scheduling, FAQ, appointment booking. According to [OrangeLoops' analysis](https://orangeloops.com/2025/12/elevenlabs-voice-ai-agents-pros-limits-when-to-use-langgraph/), ElevenLabs is NOT optimized for open-ended conversations, complex branching logic, frequent revisiting of earlier topics, or dynamic strategy changes mid-conversation. These are exactly what Pairteam needs.

> "As soon as you try to build an agent that behaves more like a knowledgeable human than a guided flow, the constraints of the visual builder become clear." — [OrangeLoops](https://orangeloops.com/2025/12/elevenlabs-voice-ai-agents-pros-limits-when-to-use-langgraph/)

### Limitation 2: Visual Spaghetti at Scale

ElevenLabs' Agent Workflows introduced a visual editor with subagent nodes, dispatch tools, and conditional branching — a genuine improvement over single-prompt agents. But [Webfuse's deep dive](https://www.webfuse.com/blog/a-deep-dive-into-elevenlabs-agent-workflows) identified the scaling problem:

> "For simple agents, the visual map is clean and intuitive. However, as you account for every possible user query, error condition, and conversational detour, the workflow can grow into a complex web of nodes and crisscrossing lines."

For a Pairteam agent that handles depression education, substance use support, housing coordination, medication adherence, insurance verification, and appointment scheduling — all with condition-specific branching and compliance guardrails — the visual editor becomes unmanageable.

### Limitation 3: No Cross-Call Memory

[MemU's analysis](https://memu.pro/blog/elevenlabs-agents-voice-memory) revealed that despite 33 million conversations handled, ElevenLabs has no native cross-call memory. Every call starts from scratch. For healthcare — where a patient who called about depression last week is now calling about medication side effects — this is a fundamental gap.

### Limitation 4: Constrained Customization

You can't control memory architecture, reasoning loops, interrupt handling, fallback strategies, or complex tool orchestration beyond what ElevenLabs' editor supports. If an interaction pattern isn't in their design, you can't build it.

### Limitation 5: Vendor Lock-In

Logic, flows, and configurations live in ElevenLabs' proprietary environment. Migration means full rebuild. For a healthcare company that may need to switch providers as requirements evolve, this is serious risk.

### The Workaround Exists (But Defeats the Purpose)

ElevenLabs [documented a "Stateful Proxy" pattern](https://elevenlabs.io/blog/integrating-complex-external-agents) where you use their voice orchestration but route ALL LLM calls to your own server. This essentially means building a parallel system — at which point, the ElevenLabs visual workflow builder is irrelevant and you're paying for voice infrastructure you could get elsewhere for less.

---

## The Platform Landscape

Here's how the market breaks down for healthcare voice agents in 2026:

```
                    CONTROL
                      ▲
                      │
         LiveKit ●    │
                      │    ● Twilio ConvRelay
         Pipecat ●    │
                      │    ● SignalWire
    Cartesia Line ●   │
                      │    ● Telnyx
                      │
                      │    ● Retell AI
                      │    ● Bland AI
                      │    ● Vapi
                      │
                      │    ● ElevenLabs
                      │    ● Synthflow
                      │    ● Thoughtly
          ────────────┼──────────────────> EASE OF USE
                      │
                MORE ENGINEERING        LESS ENGINEERING
```

### The Three Tiers

| Tier | Platforms | Trade-off |
|------|-----------|-----------|
| **Build (max control)** | LiveKit, Pipecat, Twilio ConvRelay | Full code-level control. You build the logic. 2+ weeks to first call. |
| **Managed (with escape hatches)** | Retell, Vapi, Bland, Telnyx, SignalWire | Dashboard + API. Fast to demo. Hit ceiling on complex flows. |
| **No-code (simplest)** | ElevenLabs, Synthflow, Thoughtly, PlayHT | Visual builders. Hours to first call. Walls appear fast for complex cases. |

---

## Platform Deep Dives

### LiveKit Agents — The Clear Winner for Control

**What it is:** An open-source framework (Apache 2.0, [9.4K GitHub stars](https://github.com/livekit/agents)) that lets you write voice AI agents in Python or Node.js. Agents join LiveKit rooms as real-time participants via WebRTC, with phone calls bridged in via SIP. Powers ChatGPT's Advanced Voice Mode for OpenAI.

**Why it wins for Pairteam:**

1. **Multi-Agent Handoffs.** Model different conversation phases as different agents: IntakeAgent → ConsentAgent → EducationAgent → EnrollmentAgent. Each has its own instructions, tools, and LLM configuration. Handoffs happen via tool calls — the LLM decides when to transfer. ([Docs](https://docs.livekit.io/agents/logic/agents-handoffs/))

2. **Tasks & TaskGroups.** Structured data collection with typed results — collect consent (bool), verify identity (bool), capture condition details (string). TaskGroups enable ordered multi-step flows with the ability to revisit earlier steps. ([Docs](https://docs.livekit.io/agents/logic-structure/tasks/))

3. **Pipeline Node Overrides.** Override any step in STT→LLM→TTS. The `on_user_turn_completed` hook is where you inject patient-specific condition information via RAG before the LLM generates a response. This is the exact mechanism for dynamic context injection. ([Docs](https://docs.livekit.io/agents/logic-structure/nodes/))

4. **Dynamic Instructions.** Each agent, each task, each `generate_reply` call can have different instructions. You can construct prompts dynamically based on patient data, conversation state, and real-time context. No other managed platform offers this granularity.

5. **Provider Independence.** Swap STT (Deepgram nova-3-medical for healthcare), LLM (GPT-4.1, Claude, custom), and TTS (Cartesia Sonic-3, ElevenLabs) at the session, agent, or task level. No vendor lock-in.

6. **Healthcare Battle-Tested.** [Assort Health](https://livekit.io/customers/assort-health) has processed 27M+ patient interactions with 4.3/5 satisfaction, handling 90% of inbound calls with AI on LiveKit. LiveKit is HIPAA-compliant with BAA at Scale tier ($500/month), SOC 2 Type II certified, and offers medical-specific STT models.

**What it doesn't do:**
- No visual conversation flow builder (you write code)
- Tasks are Python-only (no Node.js yet)
- Turn detection tuning is [reportedly difficult](https://github.com/livekit/agents/issues/3427)
- Requires HIPAA Scale tier at $500/month minimum
- More engineering effort than managed platforms (2+ engineers, weeks to production)

**The Code Pattern for Pairteam:**

```python
# Simplified — full example in raw findings
class PatientEducationAgent(Agent):
    def __init__(self, patient_info):
        super().__init__(
            instructions=f"""You are a care coordinator for Pairteam.
            Speaking with {patient_info.name} about {patient_info.condition}.
            Educate them on how Pairteam helps with {patient_info.condition}..."""
        )

    # RAG: inject condition-specific info before each response
    async def on_user_turn_completed(self, turn_ctx, new_message):
        rag_content = await lookup_condition_info(
            self.patient_info.condition,
            new_message.text_content()
        )
        turn_ctx.add_message(role="assistant", content=rag_content)

    @function_tool()
    async def transfer_to_enrollment(self, context):
        """Transfer when patient is ready to sign up."""
        return EnrollmentAgent(chat_ctx=self.chat_ctx), "Transferring"
```

---

### Vapi — Fast to Demo, Frustrating in Production

**What it is:** A voice orchestration platform with proprietary models for endpointing, barge-in detection, emotion detection, and filler injection. 350K+ developers, 150M+ calls processed.

**The Good:**
- Fastest path to a working voice agent — universally praised ([Coval Review](https://www.coval.dev/blog/vapi-review-2026-is-this-voice-ai-platform-right-for-your-project))
- Proprietary orchestration intelligence (custom endpointing model, background voice filtering, emotion-aware LLM context) that no competitor matches
- Provider flexibility — swap any STT/LLM/TTS
- Custom LLM endpoint support (point to your own `/chat/completions` server)
- Automated testing suite for simulating calls

**Where it breaks for Pairteam:**

The [Coval Review (Feb 2026)](https://www.coval.dev/blog/vapi-review-2026-is-this-voice-ai-platform-right-for-your-project) nailed it: "Speed to demo isn't speed to production."

1. **Cannot dynamically update system prompt mid-call.** If a patient reveals a new condition, you can't change the agent's behavior mid-conversation. Workaround exists (tool calls returning context) but it's hacky and adds latency. ([Community confirmation](https://vapi.ai/community/m/1241162638566621194))

2. **Squads (multi-agent) are buggy.** Multiple sources describe Squads as "a headache... buggy, unreliable" ([TopAutomator](https://topautomator.com/reviews/vapi-review)). This is the feature you'd need for multi-phase patient conversations.

3. **Workflows are rigid decision trees.** Community members say Workflows are "pretty much deprecated" and the "reliance on strict if-statements feels like a rigid decision tree — not well-suited for live calls where topics can shift dynamically." ([Community](https://vapi.ai/community/m/1414880041480749056))

4. **No cross-call memory.** Like ElevenLabs, you must build this yourself.

5. **Reliability concerns.** Support rated 3.5/10. Latency spikes of 3-5+ seconds reported. Monthly platform incidents. Assistant messages sometimes lost from recordings and transcripts. ([TopAutomator](https://topautomator.com/reviews/vapi-review), [Status Page](https://status.vapi.ai/incidents/))

6. **HIPAA costs $1,000/month** for zero-retention, and when enabled, you lose all dashboard analytics. ([Docs](https://docs.vapi.ai/security-and-privacy/hipaa))

**Verdict:** Good for rapid prototyping to validate conversation designs. Not reliable enough for production healthcare with complex behavioral requirements.

---

### Retell AI — The Best Managed Platform (If You Must Use One)

**What it is:** A voice agent platform by former Google/Meta/ByteDance engineers (YC company). 3,000+ companies, 40M+ calls managed. Best latency in the managed tier (~600ms).

**Why it's the best managed option:**

1. **Conversation Flow Builder.** Six node types (Conversation, Function, Call Transfer, Press Digit, End, Logic Split) with per-node prompts, transition conditions, and variable extraction. Different LLMs per node for cost optimization. This is more structured than Vapi's approach. ([Docs](https://docs.retellai.com/build/conversation-flow/overview))

2. **Custom LLM via WebSocket.** Retell connects to YOUR backend WebSocket server. You have full control over response generation — use any LLM, any logic, any context injection. This is the key escape hatch. ([Docs](https://docs.retellai.com/integrate-llm/overview))

3. **HIPAA included in standard pricing.** BAA available to ALL users, not enterprise-only. No $1,000/month add-on like Vapi. SOC 2 Type II. ([Blog](https://www.retellai.com/blog/do-retell-ais-voice-agents-have-hipaa-compliance-and-baas))

4. **Healthcare-specific features.** Dedicated healthcare page, EHR integrations (Epic, OpenDental, Dentrix), patient management workflows. ([Healthcare Page](https://www.retellai.com/healthcare))

5. **Best latency.** ~600ms average (500-750ms range) according to [WhiteSpace Solutions' practitioner testing](https://www.whitespacesolutions.ai/content/bland-ai-vs-vapi-vs-retell-comparison).

**Where it falls short:**
- Conversation Flow trades natural conversation for determinism. More control = more rigid.
- Less flexible than LiveKit for truly dynamic, code-level conversation management
- Smaller integration ecosystem than Bland

**Verdict:** If you want a managed platform with good healthcare support and an escape hatch to custom LLM logic, Retell is the pick. But for Pairteam's level of complexity, you'll likely end up on the Custom LLM WebSocket path — at which point you're building significant logic yourself anyway, and LiveKit gives you more control for similar effort.

---

### Telnyx — Best Infrastructure, Weaker on Agent Logic

**What it is:** A licensed telecom carrier in 30+ countries that added AI inference. Private MPLS backbone, co-located GPUs, sub-200ms RTT. Owns the entire stack from fiber to inference.

**The Strengths:**
- Best telephony infrastructure of any voice AI platform — private network, not public internet
- Epic EHR integration (launched Nov 2025) with real-time patient record access ([Blog](https://telnyx.com/resources/epic-integration-voice-ai-healthcare))
- Dynamic variables with 4-level resolution precedence and webhook-based context injection at call start ([Docs](https://developers.telnyx.com/docs/inference/ai-assistants/dynamic-variables))
- Custom LLM support (any OpenAI-compatible endpoint) ([Docs](https://developers.telnyx.com/docs/inference/ai-assistants/custom-llm))
- AI Missions for multi-call orchestration (batch outreach, sequential campaigns) ([Blog](https://telnyx.com/resources/ai-missions-launch))
- Forward Deployed Engineers program for complex implementations
- Competitive pricing (~$0.085/min all-in, STT and TTS free)
- HIPAA with BAA, SOC 2

**Where it falls short:**
- No visual conversation flow builder — all complex logic lives in prompts and tool calls
- Prompt-based steerability only — no explicit state machine, no structured conversation flow definition
- Telnyx's own blog [acknowledges](https://telnyx.com/resources/when-voice-ai-prompts-stop-scaling): "Models and latency rarely kill voice AI systems. Decaying instructions do."
- Limited STT language support (6 languages)
- Reddit complaints about support quality (older, but concerning for healthcare SLA requirements)
- Telephony-first DNA — the AI was bolted onto a telecom company

**The Telling Detail:** Telnyx explicitly positions itself as [complementary to LiveKit](https://telnyx.com/the-best-livekit-alternative), not a replacement: "Telnyx doesn't replace how you build agents. It upgrades what they run on." They provide SIP trunk configuration guides for LiveKit. **Telnyx knows its strength is infrastructure, not agent logic.**

**Verdict:** Use Telnyx for telephony infrastructure under LiveKit, not as a standalone agent platform. The Telnyx + LiveKit combination gives you best-in-class telephony with best-in-class agent control.

---

### Bland AI — Powerful Pathways, Concerning Reliability

**What it is:** A voice AI platform with a standout feature — Conversational Pathways — that provides a graph-based visual builder with conditions, global nodes, variable extraction, and per-node testing.

**The Standout:**
Conversational Pathways is genuinely well-designed for structured conversations. Conditions force the agent to stay on a node until required information is collected. Global nodes handle off-topic questions and return to the previous flow. Per-node unit testing with simulated variations stress-tests every branch. ([Docs](https://docs.bland.ai/tutorials/pathways))

**The Concerns:**
- **No clear Custom LLM support.** The docs page for custom LLM [returns 404](https://docs.bland.ai/enterprise-features/custom-llm). Bland runs a self-hosted model stack. Unlike Retell's WebSocket escape hatch or LiveKit's full code control, you may be locked into Bland's infrastructure.
- **Platform stability.** [Ringg AI (Feb 2026)](https://www.ringg.ai/blogs/bland-ai-review): "Platform's aggressive focus on beta features and speed often results in service fluctuations and downtime."
- **Discord-based support.** Not enterprise-grade for healthcare.
- **Hallucination risks.** "Without strict guardrails, agents can promise refunds or make up policies." For healthcare, this is a safety issue.
- **3.0/5 Product Hunt rating** with mixed reviews.
- **Slowest latency** (~800ms vs ~600ms for Retell).

**Verdict:** Pathways is a good idea, but the platform reliability and support model are not healthcare-grade. The lack of custom LLM support is a dealbreaker for Pairteam's complex logic requirements.

---

### Cartesia — Amazing Voice, Agent Platform Too Early

**What it is:** A speech model company making Sonic (TTS) and Ink (STT) — widely regarded as having the best low-latency TTS. Their Line agent platform launched August 2025 and is still in alpha (v0.2.3alpha1).

Sonic TTS is genuinely excellent — sub-100ms model latency, preferred over ElevenLabs in [blinded human evaluations](https://cartesia.ai/blog/cartesia-vs-elevenlabs) (61.4% vs 38.6%). Retell AI uses Cartesia as a TTS provider. LiveKit has an official Cartesia plugin.

**But the agent platform is not ready.** 92 GitHub stars. Alpha release. Telephony via Voximplant only added Feb 2026. HIPAA only on Enterprise plan. No battle-tested production deployments at scale.

**Verdict:** Use Cartesia Sonic as the TTS component in LiveKit. Don't use Line for production healthcare.

---

### Emerging Platforms Worth Noting

**SignalWire** deserves more attention than it gets. Built by the creators of FreeSWITCH, it owns the full telecom stack with native AI. HIPAA with full BAA on ALL plans (no enterprise tier required, no extra fees). Python Agent SDK with multi-agent orchestration. Phoenix Children's Hospital is a customer. At $0.16/min it's not cheap, but the HIPAA-first approach is rare. ([Compliance](https://signalwire.com/c/signalwire-compliance))

**Deepgram Voice Agent API** ($4.50/hr all-in) is the best price/performance option if you want a simpler full-stack solution. #1 on the VAQI benchmark. HIPAA compliant. Nova-3 Medical for healthcare STT. On-prem deployment available. But it lacks the higher-level orchestration that LiveKit or Retell provide. ([Product](https://deepgram.com/product/voice-agent-api))

**Twilio ConversationRelay** (GA May 2025) is the "BYOAI" approach — Twilio handles telephony and STT/TTS, you handle all agent logic on a WebSocket server. HIPAA eligible. Maximum flexibility but maximum engineering. ([Blog](https://twilio.com/en-us/blog/conversationrelay-generally-available))

---

## Gap Analysis: Control & Steerability

This is the table that matters most for Pairteam's decision. Every row is a capability Pairteam needs for complex healthcare conversations.

| Capability | LiveKit | Retell | Vapi | Telnyx | Bland | ElevenLabs |
|---|---|---|---|---|---|---|
| **Dynamic system prompt mid-call** | Full (per-agent, per-task, per-reply) | Via Custom LLM WebSocket | NO (confirmed limitation) | Via tool calls only | Per-node prompts | Per-subagent node |
| **State machine / explicit flow** | Code (agents + tasks + handoffs) | Conversation Flow (visual) | Squads (buggy) / Workflows (rigid) | Prompt-based only | Pathways (visual graph) | Workflows (visual) |
| **RAG context injection per turn** | `on_user_turn_completed` hook | Custom LLM endpoint | Tool call workaround | Tool calls | Webhook node | Custom LLM proxy |
| **Multi-agent handoffs** | Native (tool-call based) | Not native | Squads (unreliable) | Supported | Transfer Call node | Agent Transfer node |
| **Custom LLM (bring your own)** | Any (plugin system) | YES (WebSocket) | YES (HTTP endpoint) | YES (OpenAI-compatible) | NO (404 docs page) | YES (HTTP endpoint) |
| **Provider swapping (STT/TTS)** | Per-session/agent/task | Limited | Full flexibility | Full flexibility | Locked to their stack | Limited |
| **Cross-call memory** | Build yourself (full control) | Build yourself | Build yourself | Memory feature (webhook) | Build yourself | Build yourself |
| **Typed data collection** | Tasks with typed results | Conversation Flow nodes | Structured outputs | Gather Using AI | Variable extraction | Dispatch Tool node |
| **Medical STT** | Deepgram nova-3-medical | Deepgram nova-2-medical | Deepgram nova-2-medical | Their own (6 languages) | Unknown | Unknown |
| **HIPAA** | $500/mo Scale tier | Included (all plans) | $1,000/mo add-on | BAA available | Available | Enterprise |
| **Self-hosting option** | YES (open source) | NO | NO | NO | NO | NO |
| **EHR integration** | Build yourself | Epic, OpenDental, etc. | Build yourself | Epic (native, Nov 2025) | Build yourself | Build yourself |
| **Turn detection control** | 4 modes + manual override | Proprietary | Proprietary | Start Speaking Plan (explicit) | Unknown | Unknown |
| **Open source** | YES (Apache 2.0) | NO | NO | NO | NO | NO |

### The Key Insight

Every managed platform converges to the same escape hatch: **Custom LLM integration.** Retell's WebSocket, Vapi's HTTP endpoint, Telnyx's OpenAI-compatible endpoint — they all let you bypass their built-in logic and run your own. But once you're running your own LLM logic, you're paying for voice infrastructure + a managed platform fee while getting less control than LiveKit gives you natively.

LiveKit doesn't need an escape hatch because the whole thing is code. The "escape hatch" IS the platform.

---

## The Recommended Architecture

### The Three-Layer Stack

```
┌─────────────────────────────────────────────────────────────────┐
│                    LAYER 1: TELEPHONY                           │
│                                                                 │
│  Telnyx SIP Trunking  ──or──  Twilio                           │
│  • PSTN connectivity (inbound + outbound)                      │
│  • Phone numbers                                                │
│  • Call recording (your storage)                                │
│  • Private network (Telnyx) or global coverage (Twilio)        │
│                                                                 │
│  SIP ──────────────────────────────────────────────────> LiveKit│
├─────────────────────────────────────────────────────────────────┤
│                 LAYER 2: VOICE ORCHESTRATION                    │
│                                                                 │
│  LiveKit Agents (Python)                                        │
│  • STT: Deepgram nova-3-medical (medical terminology)          │
│  • TTS: Cartesia Sonic-3 (lowest latency, natural voice)       │
│  • VAD: Silero (voice activity detection)                      │
│  • Turn Detection: LiveKit multilingual model                  │
│  • Noise Cancellation: Krisp BVC plugin                        │
│  • Multi-agent handoffs (intake → education → enrollment)      │
│  • Tasks for structured data collection (consent, identity)    │
│  • Session state management (PatientInfo dataclass)            │
│                                                                 │
│  on_user_turn_completed hook ──────────────> RAG / Context      │
├─────────────────────────────────────────────────────────────────┤
│              LAYER 3: CONVERSATION LOGIC                        │
│                                                                 │
│  Custom State Machine (LangGraph or pure Python)                │
│  • State resolver: determines conversation phase                │
│  • Micro-prompts: focused 30-50 token instructions per state   │
│  • Patient context: loaded from your DB per call                │
│  • Condition-specific RAG: Pairteam knowledge base per topic   │
│  • Compliance guardrails: deterministic rules, not just prompts│
│  • Confidence thresholds: escalate to human below threshold    │
│  • Tool calls: EHR read, appointment scheduling, enrollment    │
│  • Audit logging: every decision, every state transition       │
│                                                                 │
│  External Systems ──────────────> EHR, CRM, Scheduling,        │
│                                   Knowledge Base, Compliance    │
└─────────────────────────────────────────────────────────────────┘
```

### Why This Architecture

**Layer separation means independent control.** You can swap Cartesia for ElevenLabs TTS without touching conversation logic. You can change compliance guardrails without touching voice infrastructure. You can A/B test different LLMs per conversation phase without changing telephony.

**The micro-prompting pattern is the key to steerability.** According to [Kannappan Suresh's analysis](https://medium.com/@kannappansuresh99/how-i-cut-voice-ai-latency-by-5x-by-deleting-90-of-the-prompt-cba48fc22555):

| Metric | Mega-Prompt (typical) | Micro-Prompt (recommended) |
|---|---|---|
| Input tokens per turn | 4,000-8,000 | 200-800 |
| Time to first token | 800ms-1.5s | 150-300ms |
| Instruction adherence | ~85% | ~98% |
| Voice-to-voice latency | 1.3-2.0s (awkward) | 0.65-0.8s (natural) |

For Pairteam, this means: a "depression education" state loads ONLY depression-specific context and instructions. A "consent collection" state loads ONLY consent language. The agent never gets confused by 8,000 tokens of instructions for every possible scenario.

### How Patient Calls Would Flow

```
Outbound Call Initiated (patient: Maria, condition: depression)
    │
    ├─ IntakeAgent loads → "Verify speaking with Maria"
    │   ├─ VerifyIdentity task → typed result (bool)
    │   └─ CollectConsent task → typed result (bool)
    │
    ├─ HANDOFF → EducationAgent loads
    │   ├─ Instructions: depression-specific Pairteam services
    │   ├─ on_user_turn_completed: RAG lookup for Maria's question
    │   │   └─ "How does Pairteam help with depression?"
    │   │     → Injects: peer support, therapy coordination, crisis line
    │   ├─ Maria mentions housing insecurity
    │   │   └─ Dynamic context: housing services added to next reply
    │   └─ Maria expresses interest in enrolling
    │
    ├─ HANDOFF → EnrollmentAgent loads
    │   ├─ CollectInfo task → typed result (address, insurance, etc.)
    │   └─ ScheduleFollowup tool → books appointment
    │
    └─ EndCall → audit log written, transcript stored, CRM updated
```

### The Guardrail Layer (Non-Negotiable for Healthcare)

[Hamming AI identified](https://hamming.ai/blog/five-failure-modes-that-make-voice-agents-unsafe-in-clinical-settings) five clinical failure modes that any architecture must address:

| Failure Mode | How to Prevent |
|---|---|
| Perception failures (STT errors) | Medical-specific STT (Deepgram nova-3-medical), confirmation for critical info |
| Guardrail failures | Deterministic enforcement in code, not just prompts |
| Multi-agent reasoning failures | Explicit state passing between agents, not implicit context |
| Workflow logic breaks | State machine with transition validation |
| Latency drift | Micro-prompting, streaming pipeline, monitoring |

Guardrails must be **deterministic, not probabilistic.** As [Hamming notes](https://hamming.ai/blog/five-failure-modes-that-make-voice-agents-unsafe-in-clinical-settings): "Guardrails cannot rely on prompts, regex, or keyword triggers. They must be deterministically enforced." This means code-level checks before and after every LLM response — something only LiveKit (and custom builds) give you.

### Testing Infrastructure

Regardless of platform choice, invest in **Hamming AI** (or similar) for voice agent testing. Pairteam already demonstrated the right instinct — 3,121 simulated calls before deployment. Hamming provides:
- Automated scenario simulation across conditions, accents, background noise
- Per-conversation compliance checking
- Production call monitoring and alerting
- HIPAA-specific testing scenarios
- Works with LiveKit natively

### Estimated Build Timeline

| Phase | Duration | Deliverable |
|---|---|---|
| Infrastructure setup | 1-2 weeks | Telnyx SIP + LiveKit Cloud + dev environment |
| First agent (simple) | 1-2 weeks | Consent + identity verification agent, working outbound call |
| Conversation logic | 3-4 weeks | State machine, micro-prompts, condition-specific RAG |
| Guardrails + compliance | 2-3 weeks | Deterministic safety checks, audit logging, HIPAA validation |
| Testing + iteration | 2-4 weeks | 3,000+ simulated calls (matching current ElevenLabs baseline) |
| **Total** | **9-15 weeks** | **Production-ready healthcare voice agent** |

Engineering requirement: 2-3 engineers (1 backend/voice, 1 ML/LLM, 1 healthcare domain/QA).

---

## Key Takeaways

1. **LiveKit Agents is the only platform that won't hit a ceiling for Pairteam's complexity requirements.** Every managed platform (Vapi, Retell, Bland, ElevenLabs) converges to "bring your own LLM" as the escape hatch for complex logic. LiveKit starts there.

2. **The micro-prompting pattern is the single most important architectural decision.** It cuts latency 5x, improves instruction adherence from 85% to 98%, and prevents the "confused agent" problem that emerges from mega-prompts with dozens of behavioral rules.

3. **Retell AI is the best fallback if LiveKit engineering investment is too high.** Its Custom LLM WebSocket gives genuine control, HIPAA is included, and latency is best-in-class for managed platforms. But you'll still be building significant logic externally.

4. **Vapi is great for prototyping, dangerous for production healthcare.** Use it to validate conversation designs quickly, then build the real system on LiveKit. Don't plan to ship on Vapi.

5. **Telnyx is infrastructure, not an agent platform.** Use it for SIP trunking and telephony under LiveKit. Don't use it as a standalone agent platform for complex behavioral requirements.

6. **ElevenLabs' limitations are architectural, not just feature gaps.** Visual builders fundamentally can't represent the complexity of multi-condition healthcare conversations with dynamic branching, cross-call context, and compliance guardrails. This isn't something a feature update fixes.

7. **Cartesia Sonic-3 is the TTS to use.** Best latency, best quality in blinded tests, works as a LiveKit plugin. Use it for voice synthesis while LiveKit handles orchestration.

8. **Guardrails must be deterministic, not probabilistic.** Prompts cannot enforce healthcare compliance. Code-level checks before and after every LLM response are non-negotiable. Only code-first platforms (LiveKit, custom builds) support this.

9. **Invest in testing infrastructure from day one.** Hamming AI or similar automated voice agent testing is essential. Match or exceed the 3,000+ simulation baseline that Pairteam already established with ElevenLabs.

10. **The hybrid architecture (Telnyx telephony + LiveKit orchestration + LangGraph logic) is the optimal stack.** It gives you best-in-class infrastructure at every layer while maintaining the separation of concerns needed for a healthcare-grade system.

---

## Predictions

1. **LiveKit will become the dominant framework for complex voice agents within 18 months.** Their $122.5M in funding, OpenAI partnership, and open-source strategy create network effects that managed platforms can't match. Half of teams currently on Vapi/Retell will migrate to LiveKit by end of 2027.

2. **Managed voice AI platforms will consolidate.** Vapi, Retell, and Bland are chasing the same mid-market. At least one will be acquired or pivot by end of 2026. Retell is the most likely survivor due to healthcare focus and YC network.

3. **Pairteam should migrate from ElevenLabs to LiveKit within 6 months.** The complexity of their patient population (homelessness, substance use, mental health, chronic conditions) will continue to push against ElevenLabs' limits. Better to invest in the right architecture now than patch an increasingly complex ElevenLabs setup.

4. **The micro-prompting / state machine pattern will become standard practice.** Within a year, every serious voice agent deployment will use some form of state-resolved micro-prompting instead of monolithic system prompts. The latency and reliability improvements are too significant to ignore.

5. **Medical-specific STT models will be table stakes by end of 2026.** The "Xanax transcribed as Zantac" problem ([Hamming AI](https://hamming.ai/blog/five-failure-modes-that-make-voice-agents-unsafe-in-clinical-settings)) is a known clinical safety issue. Deepgram's nova-3-medical will be the standard, and platforms without medical STT support will be excluded from healthcare procurement.

---

## Sources

### Primary Platform Documentation
- [LiveKit Agents Docs](https://docs.livekit.io/agents/overview/)
- [LiveKit Telephony](https://docs.livekit.io/telephony/agents-integration/)
- [LiveKit HIPAA](https://livekit.io/legal/hipaa)
- [Vapi How It Works](https://docs.vapi.ai/how-vapi-works)
- [Vapi HIPAA](https://docs.vapi.ai/security-and-privacy/hipaa)
- [Retell Conversation Flow](https://docs.retellai.com/build/conversation-flow/overview)
- [Retell Custom LLM](https://docs.retellai.com/integrate-llm/overview)
- [Telnyx Voice AI Agents](https://telnyx.com/products/voice-ai-agents)
- [Telnyx Dynamic Variables](https://developers.telnyx.com/docs/inference/ai-assistants/dynamic-variables)
- [Bland Conversational Pathways](https://docs.bland.ai/tutorials/pathways)
- [Cartesia Line](https://cartesia.ai/agents)

### Reviews & Comparisons
- [Coval: Vapi Review 2026](https://www.coval.dev/blog/vapi-review-2026-is-this-voice-ai-platform-right-for-your-project) (Feb 2026)
- [WhiteSpace: Bland vs Vapi vs Retell](https://www.whitespacesolutions.ai/content/bland-ai-vs-vapi-vs-retell-comparison) (Feb 2026)
- [TopAutomator: Vapi Review](https://topautomator.com/reviews/vapi-review) (Dec 2025)
- [AssemblyAI: Orchestration Tools Comparison](https://www.assemblyai.com/blog/orchestration-tools-ai-voice-agents) (Jan 2026)
- [Hamming: Best Voice Agent Stack](https://hamming.ai/resources/best-voice-agent-stack)

### Healthcare-Specific
- [Assort Health on LiveKit](https://livekit.io/customers/assort-health)
- [Pairteam on ElevenLabs](https://elevenlabs.io/blog/pair-team) (Feb 2026)
- [Hamming: Clinical Failure Modes](https://hamming.ai/blog/five-failure-modes-that-make-voice-agents-unsafe-in-clinical-settings)
- [Stride: Building a Clinical AI Agent](https://www.stride.build/blog/how-we-built-a-clinical-ai-agent)
- [Artera: Agentic AI for Healthcare](https://artera.io/blog/agentic-ai-for-healthcare-providers/)
- [Telnyx Epic Integration](https://telnyx.com/resources/epic-integration-voice-ai-healthcare)

### Architecture Patterns
- [Micro-Prompting: 5x Latency Reduction](https://medium.com/@kannappansuresh99/how-i-cut-voice-ai-latency-by-5x-by-deleting-90-of-the-prompt-cba48fc22555)
- [OrangeLoops: ElevenLabs Limits & LangGraph](https://orangeloops.com/2025/12/elevenlabs-voice-ai-agents-pros-limits-when-to-use-langgraph/)
- [ElevenLabs: Stateful Proxy Pattern](https://elevenlabs.io/blog/integrating-complex-external-agents)
- [LangGraph Medical AI Architecture](https://medium.com/@kofsitho/part-2-architecting-a-medical-ai-assistant-a-deep-dive-into-our-langgraph-powered-architecture-f17b51f8883d)
- [AssemblyAI: Voice AI Stack 2026](https://www.assemblyai.com/blog/the-voice-ai-stack-for-building-agents)

### Emerging Platforms
- [SignalWire](https://signalwire.com/c/telecom-stack-ai-voice)
- [Deepgram Voice Agent API](https://deepgram.com/product/voice-agent-api)
- [Twilio ConversationRelay](https://twilio.com/en-us/blog/conversationrelay-generally-available)
- [OpenAI Realtime API](https://openai.com/index/introducing-gpt-realtime/)

### Raw Research Files
- [LiveKit Raw Findings](/research/curiosity-reports/livekit-agents-raw-findings.md)
- [Vapi Raw Findings](/research/curiosity-reports/vapi-voice-ai-platform-raw-findings.md)
- [Telnyx Raw Findings](/research/curiosity-reports/telnyx-voice-ai-raw-findings.md)
- [Retell/Bland/Cartesia Raw Findings](/research/.scratchpad/2-25-26-voice-ai-platform-comparison-raw-findings.md)
- [ElevenLabs Limitations + Architecture Patterns](/research/curiosity-reports/voice-ai-platform-comparison-raw-findings.md)
- [Pairteam + Emerging Platforms](/research/.scratchpad/2-25-26-voice-ai-platform-research-raw-findings.md)
