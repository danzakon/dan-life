# LiveKit Agents: Raw Research Findings

**Category:** Tool Evaluation
**Date Started:** 2-25-26
**Status:** [ ] Active
**Context:** Voice AI platform comparison for Pairteam healthcare outbound calling agent

---

## 1. Architecture & How It Works

### Core Framework Architecture

LiveKit Agents is an open-source framework (Apache 2.0) for building realtime multimodal and voice AI agents. The framework allows you to add a Python or Node.js program to any LiveKit room as a full realtime participant. The SDK includes tools and abstractions for feeding realtime media and data through an AI pipeline that works with any provider, and publishing results back to the room.

**Source:** https://docs.livekit.io/agents/overview/

### Pipeline Architecture

The standard voice pipeline is **STT -> LLM -> TTS**:

1. **STT (Speech-to-Text):** Audio frames from user transcribed to text
2. **LLM (Large Language Model):** Text processed, response generated (or tool calls made)
3. **TTS (Text-to-Speech):** Response text synthesized to audio, streamed back to user

LiveKit also supports **Realtime Models** (speech-to-speech) that bypass STT/TTS entirely:
- OpenAI Realtime API
- Gemini Live API
- Amazon Nova Sonic
- Azure OpenAI Realtime API
- Ultravox Realtime
- xAI Grok Voice Agent API

**Source:** https://docs.livekit.io/agents/overview/

### How Agents Connect

When agent code starts, it registers with a LiveKit server (self-hosted or LiveKit Cloud) as an "agent server" process. The agent server waits for a dispatch request, then boots a "job" subprocess which joins the room. WebRTC is used between the frontend/phone and the agent, while the agent communicates with backend using HTTP and WebSockets.

**Source:** https://docs.livekit.io/agents/overview/

### Programming Language Support

- **Python:** Full support, most mature (v1.0+ released)
- **Node.js/TypeScript:** Full support (v1.0 recently released)
- Both support the same core concepts: AgentSession, Agent, tools, tasks, handoffs

**Source:** https://docs.livekit.io/agents/overview/

### Notable Users

OpenAI built ChatGPT's Advanced Voice Mode on LiveKit. Other users include Character.ai, Retell (itself!), Speak, Hello Patient, Assort Health, and xAI.

**Source:** https://blog.livekit.io/livekits-series-b/

---

## 2. Control & Steerability

### Agent Definition & Behavior Control

Agents are defined by extending the `Agent` class with:
- **Instructions** (system prompt equivalent)
- **Tools** (function calling capabilities)
- **Lifecycle hooks** (`on_enter`, `on_exit`, `on_user_turn_completed`)
- **Pipeline node overrides** (customize STT, LLM, TTS behavior)

```python
from livekit.agents import Agent

class HelpfulAssistant(Agent):
    def __init__(self):
        super().__init__(instructions="You are a helpful voice AI assistant.")

    async def on_enter(self) -> None:
        await self.session.generate_reply(
            instructions="Greet the user and ask how you can help them."
        )
```

**Source:** https://docs.livekit.io/agents/logic/agents-handoffs/

### Multi-Agent Workflows & Handoffs

LiveKit supports multi-agent architectures with explicit handoffs. You can model different conversation phases as different agents:

- **Specialized contexts:** Agents optimized for particular conversation phases
- **Different permissions:** Agent with API access vs. one for general inquiries
- **Model specialization:** Lightweight triage model before escalating to a larger one
- **Different roles:** Moderator agent vs. coaching agent

Handoffs happen via tool calls -- the LLM decides when to hand off:

```python
class CustomerServiceAgent(Agent):
    def __init__(self):
        super().__init__(instructions="...")

    @function_tool()
    async def transfer_to_billing(self, context: RunContext):
        """Transfer the customer to a billing specialist."""
        return BillingAgent(chat_ctx=self.chat_ctx), "Transferring to billing"
```

**Source:** https://docs.livekit.io/agents/logic/agents-handoffs/

### Tasks & Task Groups (Structured Conversation Flows)

Tasks are focused, reusable units that perform a specific objective and return a typed result. This is how you model structured data collection flows:

```python
class CollectConsent(AgentTask[bool]):
    def __init__(self, chat_ctx=None):
        super().__init__(
            instructions="Ask for recording consent. Be polite and professional.",
            chat_ctx=chat_ctx,
        )

    @function_tool
    async def consent_given(self) -> None:
        """Use this when the user gives consent to record."""
        self.complete(True)

    @function_tool
    async def consent_denied(self) -> None:
        """Use this when the user denies consent to record."""
        self.complete(False)
```

TaskGroups enable ordered multi-step flows with the ability to revisit earlier steps:

```python
task_group = TaskGroup(chat_ctx=chat_ctx)
task_group.add(lambda: GetEmailTask(), id="get_email_task", description="Collects the user's email")
task_group.add(lambda: GetCommuteTask(), id="get_commute_task", description="Records commute flexibility")
results = await task_group
```

**IMPORTANT:** Tasks are currently Python-only. Node.js support not yet available.

Prebuilt tasks include:
- `WarmTransferTask` (agent-assisted warm transfer)
- `GetDtmfTask` (collect keypad inputs)
- `GetAddressTask` (collect/validate mailing address)
- `GetEmailTask` (collect/validate email)

**Source:** https://docs.livekit.io/agents/logic-structure/tasks/

### Pipeline Nodes & Hooks (Deep Customization)

You can override any node in the processing pipeline:

**Lifecycle hooks:**
- `on_user_turn_completed()` -- Called when user's turn ends, before agent reply. **This is where you inject RAG context.**
- `on_exit()` -- Called before agent gives control to another agent
- `on_enter()` -- Called when agent becomes active

**STT-LLM-TTS pipeline nodes:**
- `stt_node()` -- Transcribe input audio to text
- `llm_node()` -- Perform inference and generate response/tool calls
- `tts_node()` -- Synthesize speech from LLM text output

**RAG injection example:**
```python
async def on_user_turn_completed(
    self, turn_ctx: ChatContext, new_message: ChatMessage,
) -> None:
    rag_content = await my_rag_lookup(new_message.text_content())
    turn_ctx.add_message(
        role="assistant",
        content=f"Additional information relevant to the user's next message: {rag_content}"
    )
```

**Source:** https://docs.livekit.io/agents/logic-structure/nodes/

### Context & Memory Management

- **Chat context (`chat_ctx`)** is the full conversation history available to the agent
- When handing off between agents, you can **pass or reset chat context**
- `session.history` always has the complete conversation history for the session
- **`userdata`** attribute on sessions for arbitrary state (e.g., patient info, call metadata)
- Dynamic context injection via `on_user_turn_completed` hook
- Initial context can be loaded from job metadata before session starts

```python
@dataclass
class MySessionInfo:
    user_name: str | None = None
    age: int | None = None

session = AgentSession[MySessionInfo](
    userdata=MySessionInfo(user_name="Steve"),
    # ... vad, stt, tts, llm, etc.
)
```

**Source:** https://docs.livekit.io/agents/logic/agents-handoffs/

### Dynamic System Prompt / Instructions

Each agent has its own `instructions`. You can:
- Set instructions at agent construction time
- Generate dynamic replies with temporary `instructions` parameter
- Change instructions by updating the agent or handing off to a different agent
- Different agents in the same session can have completely different instructions

```python
await self.session.generate_reply(
    instructions="Inform the user about their specific condition and how Pairteam can help."
)
```

**Source:** https://docs.livekit.io/agents/logic/sessions/

### Turn Detection & Interruption Handling

Multiple turn detection modes:
- **Turn detector model:** Custom open-weights model for context-aware turn detection (recommended)
- **VAD only:** Detect end of turn from speech and silence data alone
- **STT endpointing:** Use phrase endpoints from STT provider
- **Manual turn control:** Disable automatic turn detection entirely
- **Realtime models:** Built-in turn detection in models like OpenAI Realtime API

Configuration options:
- `min_interruption_words` -- Minimum words before an interruption is registered
- `min_interruption_duration` -- Minimum duration before interruption
- `min_endpointing_delay` -- Minimum silence before turn end
- Noise cancellation built-in (Krisp BVC plugin)

**Known challenge:** GitHub issue #3427 reports difficulty tuning interruption sensitivity independently for `thinking` vs `speaking` states. Users find it hard to make agent hard to interrupt while being friendly to slow speakers.

**Source:** https://docs.livekit.io/agents/build/turns
**Source:** https://github.com/livekit/agents/issues/3427

### Provider Swapping

You can swap STT, LLM, and TTS providers freely:
- At the session level (default for all agents in the session)
- At the agent level (override for specific agents)
- At the task level (override for specific tasks)

```python
class CustomerServiceManager(Agent):
    def __init__(self):
        super().__init__(
            instructions="You are a customer service manager.",
            tts="cartesia/sonic-3:6f84f4b8-58a2-430c-8c79-688dad597532"  # different voice
        )
```

**Source:** https://docs.livekit.io/agents/logic/agents-handoffs/

---

## 3. Supported Models & Providers

### STT Providers

**Via LiveKit Inference (managed):**
| Provider | Model | Notes |
|----------|-------|-------|
| AssemblyAI | Universal-Streaming | English only |
| AssemblyAI | Universal-Streaming-Multilingual | 6 languages |
| Cartesia | Ink Whisper | 100 languages |
| Deepgram | Flux, Nova-3, Nova-3 Medical, Nova-2 | Various |
| ElevenLabs | Scribe V2 Realtime | 41 languages |

**Via Plugins (BYOK):**
Amazon Transcribe, AssemblyAI, Azure AI Speech, Azure OpenAI, Baseten, Cartesia, Clova, Deepgram, ElevenLabs, fal, Gladia, Google Cloud, Gradium, Groq, Mistral AI, Nvidia, OpenAI, OVHCloud, Sarvam, Simplismart, Soniox, Speechmatics, Spitch

**Source:** https://docs.livekit.io/agents/models/stt/

### LLM Providers

**Via LiveKit Inference:**
| Family | Models |
|--------|--------|
| OpenAI | GPT-4o, GPT-4.1, GPT-4.1 mini/nano, GPT-5, GPT-5 mini/nano, GPT-5.1, GPT-5.2 |
| Gemini | Gemini 3 Pro/Flash, 2.5 Pro/Flash/Flash Lite, 2.0 Flash/Flash Lite |
| Kimi | Kimi K2 Instruct |
| DeepSeek | DeepSeek V3, V3.2 |

**Via Plugins (BYOK):**
Amazon Bedrock, **Anthropic**, Baseten, Google Gemini, Groq, **LangChain**, Mistral AI, OpenAI, Azure OpenAI, Cerebras, DeepSeek, Fireworks, Letta, **Ollama**, OpenRouter, OVHCloud, Perplexity, Telnyx, Together AI, xAI

**NOTE:** Anthropic/Claude is available as a plugin. LangChain plugin allows any LangChain-compatible model.

**Source:** https://docs.livekit.io/agents/models/llm/

### TTS Providers

**Via LiveKit Inference:**
Rime, Inworld, ElevenLabs, Deepgram, Cartesia

**Via Plugins:**
Multiple additional providers available

**Source:** https://docs.livekit.io/agents/models/tts/

### Realtime (Speech-to-Speech) Models

| Provider | Python | Node.js |
|----------|--------|---------|
| Amazon Nova Sonic | Yes | No |
| Azure OpenAI Realtime API | Yes | Yes |
| Gemini Live API | Yes | Yes |
| OpenAI Realtime API | Yes | Yes |
| Ultravox Realtime | Yes | No |
| xAI Grok Voice Agent API | Yes | No |

**Source:** https://docs.livekit.io/agents/models/realtime/

---

## 4. Telephony Integration (SIP/PSTN)

### How It Works

Telephony integration uses SIP (Session Initiation Protocol). Phone calls are bridged into LiveKit rooms using a special SIP participant type. **No significant changes to existing agent code required** -- phone calls are just another participant.

**Source:** https://docs.livekit.io/telephony/agents-integration/

### Outbound Calling

Full outbound calling support. The workflow:
1. Create an outbound SIP trunk (authenticated with provider like Twilio)
2. Dispatch an agent to a room
3. Create a SIP participant to dial the number
4. Agent and callee interact in the room

```python
await ctx.api.sip.create_sip_participant(api.CreateSIPParticipantRequest(
    room_name=ctx.room.name,
    sip_trunk_id='ST_xxxx',
    sip_call_to=phone_number,
    participant_identity=sip_participant_identity,
    wait_until_answered=True,
))
```

**Source:** https://docs.livekit.io/telephony/agents-integration/

### Outbound Caller Example (GitHub)

Complete example repo: `livekit-examples/outbound-caller-python`

Features demonstrated:
- Making outbound calls
- Detecting voicemail
- Looking up availability via function calling
- Transferring to a human operator
- Detecting intent to end the call
- Krisp background voice cancellation

**Source:** https://github.com/livekit-examples/outbound-caller-python

### LiveKit Phone Numbers

LiveKit now offers phone numbers directly (no need for Twilio):
- Purchase through LiveKit Cloud
- For inbound calls
- Included in free tier: 1 US local phone number with 50 inbound minutes

For outbound, you still need a SIP trunk provider (Twilio, etc.)

**Source:** https://docs.livekit.io/telephony/agents-integration/

### Supported SIP Features

- DTMF (touch-tone) sending and receiving
- SIP REFER (call transfer)
- Cold transfer to other phone numbers
- Warm transfer (agent-assisted, via WarmTransferTask)
- Voicemail detection
- Caller ID customization
- Dial tone playback while connecting
- Region pinning for outbound calls

### Provider-Specific Guides

- Twilio: Full setup guide available
- Other SIP providers supported generically

**Source:** https://docs.livekit.io/telephony/start/providers/twilio/

---

## 5. Healthcare-Specific Capabilities

### HIPAA Compliance

**LiveKit Cloud is HIPAA-compliant.** From their legal page:

HIPAA-eligible services include:
- Agent observability
- Agent hosting
- Ingress (stream ingestion)
- Egress (recording and export)
- Realtime transport with WebRTC and SIP

**LiveKit Inference** is HIPAA-compliant when using specific models:

STT: Deepgram (nova-2/nova-3 variants, including **nova-3-medical**), Cartesia Ink Whisper, AssemblyAI Universal-Streaming
LLM: DeepSeek V3/V3.2, Kimi K2 (and presumably others listed on the page)

**LiveKit signs BAAs with customers.** Available at Scale tier ($500/month) and above.

**Source:** https://livekit.io/legal/hipaa
**Source:** https://livekit.io/security

### Security Posture

- SOC2 Type II compliant
- GDPR compliant
- 256-bit TLS encryption for connections
- AES-128 encryption for media streams
- AES-256 encryption for data at rest
- Never records or stores audio/video/data streams (recordings via API go to developer-specified storage)
- Analytics data retained (encrypted) for max 14 days
- End-to-end encryption available
- JWT tokens and room permissions
- Background checks on all staff
- Annual security training

**Source:** https://livekit.io/security

### Healthcare Case Study: Assort Health

Assort Health builds AI agents for specialty healthcare practices (orthopedic surgery, dermatology, OBGYN, pediatrics, cardiology, ENT).

Key details:
- **27 million+ patient-facing interactions** with 4.3/5 satisfaction rating
- Supports both inbound and outbound agents
- Handles: appointment scheduling, payment processing, prescription refills
- **90% of inbound calls handled by AI** with seamless handoffs to humans for remaining 10%
- Over **20 million patient interactions processed on LiveKit**
- Expected to exceed **100 million by end of 2025**
- Team uses LiveKit because it allows **complete control over stack** -- swap STT, LLM, TTS providers freely
- Native SIP support was "non-negotiable" for phone system integration

Quote from CEO: "The LiveKit team is responsive, and we've seen a lot of new and important features shipped over the past year to customize agent behavior further. The documentation is clear and includes numerous examples."

**Source:** https://livekit.io/customers/assort-health

### Healthcare Recipe: Medical Office Triage

LiveKit provides a "Medical Office Triage" recipe: "Agent that triages patients based on symptoms and medical history."

**Source:** https://docs.livekit.io/agents/overview/

### Healthcare-Specific STT Models

Deepgram offers medical-specific models available through LiveKit Inference:
- `deepgram/nova-3-medical` -- English only
- `deepgram/nova-2-medical` -- English only

These are HIPAA-compliant and optimized for medical terminology.

**Source:** https://docs.livekit.io/agents/models/stt/

---

## 6. Developer Experience

### Open Source

The entire framework is open source under Apache 2.0:
- Core server: open source
- Agents framework: open source
- Client SDKs: open source
- 9.4K+ GitHub stars on agents repo

**Source:** https://github.com/livekit/agents

### Documentation Quality

Extensive documentation at docs.livekit.io covering:
- Quickstart guides (voice AI, telephony)
- Conceptual docs (architecture, sessions, workflows, tasks)
- Reference docs (SDK reference for Python and Node.js)
- 50+ focused single-concept examples
- 20+ production-style complex agent examples with frontends
- llms.txt for LLM-optimized documentation
- AGENTS.md files for coding assistants
- Deeplearning.ai course available
- Agent Builder (no-code prototyping tool)

**Source:** https://docs.livekit.io/agents/
**Source:** https://github.com/livekit-examples/python-agents-examples

### Deployment Options

**LiveKit Cloud (managed):**
- Deploy with single CLI command
- Automatic scaling and load balancing
- Built-in observability (transcripts, traces, session analytics)
- Graceful draining during version updates
- Instant rollbacks
- Global edge network

**Self-hosted:**
- Deploy on any container orchestration system (Kubernetes)
- Worker pool model with automatic job dispatch
- Complete infrastructure control
- No per-minute LiveKit charges
- Requires DevOps expertise

**Source:** https://docs.livekit.io/agents/v0/deployment
**Source:** https://docs.livekit.io/deploy/custom/deployments/

### Community & Ecosystem

- Active Slack community
- GitHub issues actively maintained
- $122.5M+ raised (including $100M Series B in Jan 2026 led by Index Ventures)
- OpenAI as customer/partner
- Regular feature releases and new plugins

**Source:** https://rywalker.com/research/livekit-agents

---

## 7. Pricing

### LiveKit Cloud Tiers

| Plan | Monthly Fee | Agent Session Minutes | HIPAA |
|------|-------------|----------------------|-------|
| Build | $0 | 1,000 | No |
| Ship | $50 | 5,000 | No |
| Scale | $500 | 50,000 | **Yes (with BAA)** |
| Enterprise | Custom | Negotiated | Yes |

### Per-Minute Costs

| Service | Build/Ship Rate | Scale Rate |
|---------|----------------|------------|
| Agent Session Minutes | $0.01/min | $0.01/min |
| WebRTC Minutes | $0.0005/min | $0.0004/min |
| SIP Minutes | $0.004/min | $0.003/min |

**CRITICAL FOR PAIRTEAM:** HIPAA requires Scale tier minimum ($500/month). No lower-cost path for healthcare applications.

### Self-Hosting Cost

Self-hosting is free (open source). You only pay for your own infrastructure. At 1M minutes, estimated self-hosted TCO is ~$4,100/month vs ~$6,500/month managed (37% savings).

### Comparison to Managed Platforms

From Reddit discussion (r/AI_Agents, Dec 2025):
- Retell AI: ~$275-320/mo for 3,000 min/month
- Vapi: ~$370-500+/mo (unpredictable with add-ons)
- LiveKit Cloud (Ship plan): ~$320-350/mo + dev time

Key community insight: "LiveKit gives more control but adds dev overhead. If time-to-launch and low maintenance matter, Retell is usually the safer bet."

Another: "Start on Retell for production reliability, then prototype a LiveKit + OpenAI Realtime stack in parallel."

**Source:** https://checkthat.ai/brands/livekit/pricing
**Source:** https://www.reddit.com/r/AI_Agents/comments/1pjuevf/lost_between_livekit_cloud_vs_vapi_vs_retell_for/

---

## 8. Unique Advantages vs. Managed Platforms

### What LiveKit Can Do That Vapi/Retell/Bland Cannot

1. **Full code-level control.** You write Python/Node.js, not configure a dashboard. Every aspect of the pipeline is overridable.

2. **Multi-agent orchestration.** Native support for agent handoffs, tasks, task groups. You can model entire conversation workflows as state machines with different agents handling different phases.

3. **Provider independence.** Swap STT, LLM, TTS providers at the session, agent, or task level without changing your architecture. No vendor lock-in.

4. **Self-hosting option.** Run on your own infrastructure for complete data control and cost optimization at scale. Critical for healthcare/HIPAA.

5. **Pipeline node customization.** Override any step in the STT->LLM->TTS pipeline. Insert RAG, modify pronunciations, filter content, add custom audio processing.

6. **Realtime model support.** Use OpenAI Realtime API, Gemini Live, etc. for speech-to-speech without STT/TTS.

7. **Battle-tested at massive scale.** Powers ChatGPT Advanced Voice Mode for millions of users. Not a startup experiment.

8. **Open source.** Read the code. Contribute. Fork. No black boxes.

9. **Medical-specific STT models.** Deepgram nova-3-medical available through LiveKit Inference for medical terminology accuracy.

10. **Rich telephony features.** DTMF, SIP REFER, warm transfer, cold transfer, voicemail detection, caller ID -- all built into the framework.

### Where LiveKit Falls Short vs. Managed Platforms

1. **Higher development effort.** You're writing code, not configuring a dashboard. A blog post states: "engineering: custom ASR/TTS wiring, observability, interrupt handling, and call flows add up."

2. **No visual builder for conversation flows.** While Agent Builder exists for prototyping, production agents require code. Vapi and Retell have visual flow builders.

3. **Turn detection tuning is hard.** GitHub issues report difficulty getting interruption handling right. The shared interruption logic across agent states is a known pain point.

4. **Tasks only in Python.** Node.js support for tasks/task groups is not yet available, limiting structured workflow options for TypeScript teams.

5. **HIPAA requires $500/month minimum.** Scale tier is mandatory for healthcare. Managed platforms may offer HIPAA at lower tiers.

6. **No pre-built analytics/reporting.** You get session data and transcripts, but building call outcome analytics, performance dashboards, etc. is on you.

7. **Smaller community than Twilio.** While growing fast (9.4K GitHub stars), the ecosystem is smaller than established telecom platforms.

**Source:** https://atalupadhyay.wordpress.com/2025/11/03/building-production-ready-voice-ai-agents-with-livekit/
**Source:** https://www.moravio.com/blog/livekit-agents-for-building-real-time-ai-agents

---

## 9. Code Examples: Complex Agent Configuration

### Complete Healthcare-Relevant Outbound Calling Agent Pattern

Based on the documented patterns, here is how you would architect a Pairteam-style agent:

```python
from dataclasses import dataclass
from livekit.agents import (
    AgentSession, Agent, AgentTask, function_tool,
    RunContext, ChatContext, ChatMessage, room_io, get_job_context
)
from livekit.plugins import silero, noise_cancellation
from livekit.plugins.turn_detector.multilingual import MultilingualModel
from livekit import api
import json

@dataclass
class PatientInfo:
    patient_name: str | None = None
    condition: str | None = None
    phone_number: str | None = None
    interest_expressed: str | None = None
    consent_given: bool = False
    education_completed: bool = False

# Task: Collect recording consent
class CollectConsent(AgentTask[bool]):
    def __init__(self, chat_ctx=None):
        super().__init__(
            instructions="Ask for recording consent. Be polite and professional.",
            chat_ctx=chat_ctx,
        )

    async def on_enter(self) -> None:
        await self.session.generate_reply(
            instructions="Let the patient know this call may be recorded for quality purposes. Ask for their permission."
        )

    @function_tool
    async def consent_given(self) -> None:
        """Use when the patient gives consent."""
        self.complete(True)

    @function_tool
    async def consent_denied(self) -> None:
        """Use when the patient denies consent."""
        self.complete(False)

# Task: Verify patient identity
class VerifyIdentity(AgentTask[bool]):
    def __init__(self, patient_name: str, chat_ctx=None):
        super().__init__(
            instructions=f"Verify you are speaking with {patient_name}. Confirm their identity politely.",
            chat_ctx=chat_ctx,
        )

    @function_tool
    async def identity_confirmed(self) -> None:
        """Patient confirmed their identity."""
        self.complete(True)

    @function_tool
    async def wrong_person(self) -> None:
        """Speaking with wrong person or patient unavailable."""
        self.complete(False)

# Main agent for patient education
class PatientEducationAgent(Agent):
    def __init__(self, patient_info: PatientInfo):
        super().__init__(
            instructions=f"""You are a patient care coordinator for Pairteam.
            You are speaking with {patient_info.patient_name} who expressed interest
            in Pairteam's services related to {patient_info.condition}.

            Your goals:
            1. Educate them about how Pairteam can help with {patient_info.condition}
            2. Answer their questions
            3. If they're interested, schedule a follow-up or transfer to enrollment

            Be warm, professional, and empathetic. Do not provide medical advice."""
        )
        self.patient_info = patient_info

    async def on_enter(self) -> None:
        # Run consent task first
        consent = await CollectConsent(chat_ctx=self.chat_ctx)
        self.session.userdata.consent_given = consent

        if not consent:
            await self.session.generate_reply(
                instructions="Thank them and let them know you understand. End the call politely."
            )
            return

        # Verify identity
        verified = await VerifyIdentity(
            patient_name=self.patient_info.patient_name,
            chat_ctx=self.chat_ctx
        )

        if not verified:
            await self.session.generate_reply(
                instructions="Apologize for the mix-up and end the call politely."
            )
            return

        # Begin education
        await self.session.generate_reply(
            instructions=f"Begin educating the patient about Pairteam's services for {self.patient_info.condition}."
        )

    # RAG: inject relevant condition information before each response
    async def on_user_turn_completed(
        self, turn_ctx: ChatContext, new_message: ChatMessage,
    ) -> None:
        rag_content = await lookup_condition_info(
            self.patient_info.condition,
            new_message.text_content()
        )
        if rag_content:
            turn_ctx.add_message(
                role="assistant",
                content=f"Relevant information about {self.patient_info.condition}: {rag_content}"
            )

    @function_tool()
    async def schedule_followup(self, context: RunContext[PatientInfo], preferred_date: str):
        """Schedule a follow-up appointment when the patient is interested."""
        # Call your scheduling API
        result = await schedule_appointment(context.userdata.patient_name, preferred_date)
        return f"Appointment scheduled for {preferred_date}"

    @function_tool()
    async def transfer_to_enrollment(self, context: RunContext[PatientInfo]):
        """Transfer to enrollment specialist when patient is ready to sign up."""
        return EnrollmentAgent(chat_ctx=self.chat_ctx), "Transferring to enrollment"

    @function_tool()
    async def end_call(self, context: RunContext[PatientInfo]):
        """End the call when conversation is complete."""
        await context.session.generate_reply(
            instructions="Thank them warmly, summarize what you discussed, and end the call."
        )
        job_ctx = get_job_context()
        await job_ctx.api.room.delete_room(
            api.DeleteRoomRequest(room=job_ctx.room.name)
        )

# Entrypoint
@server.rtc_session(agent_name="pairteam-outbound")
async def entrypoint(ctx):
    # Load patient info from job metadata
    dial_info = json.loads(ctx.job.metadata)

    patient_info = PatientInfo(
        patient_name=dial_info["patient_name"],
        condition=dial_info["condition"],
        phone_number=dial_info["phone_number"],
        interest_expressed=dial_info["interest"],
    )

    session = AgentSession[PatientInfo](
        stt="deepgram/nova-3-medical:en",  # Medical-specific STT
        llm="openai/gpt-4.1",
        tts="cartesia/sonic-3:9626c31c-bec5-4cca-baa8-f8ba9e84c8bc",
        vad=silero.VAD.load(),
        turn_detection=MultilingualModel(),
        userdata=patient_info,
    )

    await session.start(
        room=ctx.room,
        agent=PatientEducationAgent(patient_info),
        room_options=room_io.RoomOptions(
            audio_input=room_io.AudioInputOptions(
                noise_cancellation=noise_cancellation.BVC(),
            ),
        ),
    )

    # Place outbound call
    await ctx.api.sip.create_sip_participant(api.CreateSIPParticipantRequest(
        room_name=ctx.room.name,
        sip_trunk_id='ST_xxxx',
        sip_call_to=patient_info.phone_number,
        participant_identity=patient_info.phone_number,
        wait_until_answered=True,
    ))
    # Agent waits for patient to speak first (outbound convention)
```

**NOTE:** This is a synthesized example based on documented patterns, not from a single source.

---

## 10. Key URLs & Sources

### Official Documentation
- Overview: https://docs.livekit.io/agents/overview/
- Sessions: https://docs.livekit.io/agents/logic/sessions/
- Workflows: https://docs.livekit.io/agents/logic/workflows/
- Agents & Handoffs: https://docs.livekit.io/agents/logic/agents-handoffs/
- Tasks & Task Groups: https://docs.livekit.io/agents/logic-structure/tasks/
- Pipeline Nodes & Hooks: https://docs.livekit.io/agents/logic-structure/nodes/
- Telephony Integration: https://docs.livekit.io/telephony/agents-integration/
- Turn Detection: https://docs.livekit.io/agents/build/turns
- External Data & RAG: https://docs.livekit.io/agents/build/external-data
- Models (STT): https://docs.livekit.io/agents/models/stt/
- Models (LLM): https://docs.livekit.io/agents/models/llm/
- Models (TTS): https://docs.livekit.io/agents/models/tts/
- Models (Realtime): https://docs.livekit.io/agents/models/realtime/
- HIPAA: https://livekit.io/legal/hipaa
- Security: https://livekit.io/security
- Quickstart: https://docs.livekit.io/agents/start/voice-ai-quickstart/

### GitHub
- Framework repo: https://github.com/livekit/agents (9.4K stars)
- Outbound caller example: https://github.com/livekit-examples/outbound-caller-python
- Python examples (50+): https://github.com/livekit-examples/python-agents-examples

### Case Studies & Blog
- Assort Health (healthcare): https://livekit.io/customers/assort-health
- Series B announcement: https://blog.livekit.io/livekits-series-b/
- Cloud deployment: https://blog.livekit.io/deploy-and-scale-agents-on-livekit-cloud

### Community & Reviews
- Reddit comparison: https://www.reddit.com/r/AI_Agents/comments/1pjuevf/lost_between_livekit_cloud_vs_vapi_vs_retell_for/
- Moravio architecture breakdown: https://www.moravio.com/blog/livekit-agents-for-building-real-time-ai-agents
- Dev.to telephony tutorial: https://dev.to/drguthals/build-a-livekit-telephony-agent-3ibe
- Ry Walker research summary: https://rywalker.com/research/livekit-agents

### Pricing
- Pricing analysis: https://checkthat.ai/brands/livekit/pricing
- LiveKit vs Agora pricing: https://www.forasoft.com/blog/article/livekit-vs-agora-cost-analysis

### Comparison Resources
- AssemblyAI voice stack overview: https://www.assemblyai.com/blog/the-voice-ai-stack-for-building-agents
- Speechmatics platform comparison: https://www.speechmatics.com/company/articles-and-news/best-voice-ai-agent-platforms-2025
- Hamming testing guide: https://hamming.ai/resources/testing-and-monitoring-livekit-voice-agents-production
