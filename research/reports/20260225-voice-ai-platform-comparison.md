# Voice AI Platform Comparison: Raw Research Findings

**Date:** 2-25-26
**Purpose:** Understand why ElevenLabs fails for complex healthcare voice agents and what architectural patterns solve the problem.

---

## TOPIC 1: ElevenLabs Limitations for Complex Voice Agents

---

### 1.1 What ElevenLabs Conversational AI Offers

**Source:** OrangeLoops - "ElevenLabs Voice AI Agents: Pros, Limits & When to Use LangGraph"
**URL:** https://orangeloops.com/2025/12/elevenlabs-voice-ai-agents-pros-limits-when-to-use-langgraph/

ElevenLabs has evolved from a TTS engine into a full voice agent platform. The core offering:
- An agent listens via STT, processes via an LLM (their default or external), responds via synthetic speech
- **No-code Agent Builder** for fast prototyping -- visual drag-and-drop interface
- Managed infrastructure: GPU-powered speech models, real-time audio streaming, scaling, telephony integration, logging/analytics
- Sub-second TTS streaming for natural turn-taking
- Multi-channel deployment: phone lines, websites, mobile apps, internal dashboards
- SDKs for Python and JavaScript for extensibility
- Enterprise features: SOC2, GDPR, optional HIPAA support, analytics dashboards

**Key strength:** "contained, goal-oriented conversations that benefit from clear structure and reliable speech quality" -- works great for simple scheduling, FAQ, appointment booking. A basic agent can be created and deployed in days.

---

### 1.2 ElevenLabs Agent Workflows (The "Fix" for Single-Prompt Architecture)

**Source:** Webfuse - "A Deep Dive into ElevenLabs Agent Workflows"
**URL:** https://www.webfuse.com/blog/a-deep-dive-into-elevenlabs-agent-workflows

ElevenLabs recognized that a single-prompt agent couldn't handle complex use cases. Agent Workflows introduced a visual editor with these building blocks:

**Node Types:**
- **Subagent Nodes:** Change agent behavior at specific conversation points -- swap LLM models, change voice, update system prompt, attach different tools/knowledge bases per step
- **Dispatch Tool Node:** *Guarantees* a specific tool is called at a certain point (not just suggested to LLM). Has success/failure paths for branching.
- **Agent Transfer Node:** Handoff from one AI agent to another (e.g., general coordinator -> billing specialist)
- **Transfer to Number Node:** Escalation to human agent via phone/SIP with conversation summary
- **End Node:** Controlled conversation termination

**Edge/Flow Control:**
- Intent-based routing (LLM analyzes user input, routes to matching edge)
- Tool-based outcomes (success/failure branching)
- Conditional logic on edges
- Default/fallback paths

**What improved over single-prompt:**
- Explicit control over conversation flow
- Cost/latency optimization (lightweight model for triage, powerful model for reasoning)
- Task decomposition (specialized subagents per step)
- Scoped context per subagent (improved accuracy, limited sensitive info access)

---

### 1.3 Specific Limitations of ElevenLabs (Even with Workflows)

**Source:** OrangeLoops article (full crawl)
**URL:** https://orangeloops.com/2025/12/elevenlabs-voice-ai-agents-pros-limits-when-to-use-langgraph/

#### Limitation 1: Limited Support for Complex Dialogue
ElevenLabs is NOT optimized for:
- Open-ended conversations
- Complex branching logic
- **Deep multi-turn discussions**
- **Frequent revisiting of earlier topics**
- **Dynamic strategy changes mid-conversation**

> "As soon as you try to build an agent that behaves more like a knowledgeable human than a guided flow, the constraints of the visual builder become clear."

#### Limitation 2: Reduced Customization and Flexibility
You don't have full control over:
- **Memory architecture**
- **Reasoning loops**
- **Interrupt handling**
- **Multi-agent handoffs** (beyond the basic transfer node)
- **Fallback strategies**
- **Complex tool orchestration**

> "If a particular interaction pattern isn't supported by ElevenLabs' editor, you can't simply modify the system internals. You're constrained to the platform's design philosophy."

#### Limitation 3: Vendor Lock-In
- Logic lives in their visual builder
- Voice models are proprietary
- **Exporting flows is limited**
- **Migrating to another system requires full rebuild**

#### Limitation 4: Cost at Scale
- Usage-based pricing rises significantly for long calls, multiple concurrent calls, high daily volumes
- Thousands of hours per month makes cost a major concern

#### Limitation 5: Cloud-Dependent
- No offline or on-device mode for TTS/STT
- Latency concerns for some regions
- **Compliance challenges for healthcare, finance, government**

**Source:** Webfuse article (limitations section)

#### Limitation 6: "Visual Spaghetti" Problem
> "For simple agents, the visual map is clean and intuitive. However, as you account for every possible user query, error condition, and conversational detour, the workflow can grow into a complex web of nodes and crisscrossing lines."

#### Limitation 7: Debugging Difficulty
> "Debugging often involves re-tracing the conversational path step-by-step. You have to ask: Was the correct context passed from the previous node? Did a tool return data in an unexpected format? Did the user's phrasing trigger an edge case you didn't anticipate? Finding the root cause can feel like chasing a ghost."

#### Limitation 8: Walled Garden Effect
> "The logic, structure, and configurations you create are native to the ElevenLabs environment. You cannot easily export a complex workflow and run it on a different platform."

---

### 1.4 ElevenLabs Has NO Cross-Call Memory

**Source:** MemU Blog - "ElevenLabs Agents Handle 33 Million Conversations -- But Start Each Call From Scratch"
**URL:** https://memu.pro/blog/elevenlabs-agents-voice-memory

Critical finding for healthcare:

> "Cross-call memory doesn't exist natively. What an agent learned during a 15-minute support call -- the caller's communication style, the specific issue context, the resolution approach that worked -- disappears when the call ends."

- 2 million agents deployed, 33 million conversations handled
- Per-conversation personalization only possible through **dynamic variables** passed at call start
- No accumulation of patient preferences, history, communication styles across calls
- For healthcare: a patient who calls about a follow-up gets no benefit from their previous call context

**Workaround:** MemU Agentic Memory Framework adds cross-call memory as an external integration layer.

---

### 1.5 The Custom LLM / "Bring Your Own Agent" Workaround

**Source:** ElevenLabs Documentation - "Integrate your own model"
**URL:** https://elevenlabs.io/docs/agents-platform/customization/llm/custom-llm

**Source:** ElevenLabs Blog - "Integrating external agents with ElevenLabs Agents' voice orchestration"
**URL:** https://elevenlabs.io/blog/integrating-complex-external-agents

YES, you can use ElevenLabs just for voice and handle logic externally. Here's how:

**Custom LLM Integration:**
- Your server must implement an endpoint compatible with OpenAI Chat Completions API format
- ElevenLabs sends conversation messages to YOUR endpoint instead of their LLM
- You can pass custom parameters via `elevenlabs_extra_body` (UUIDs, session IDs, patient context, etc.)
- Buffer words technique ("Let me think about that...") for slow-processing LLMs
- System tools integration: your LLM can trigger end_call, language_detection, agent_transfer, transfer_to_human, skip_turn

**The Stateful Proxy Pattern (from ElevenLabs' own blog):**

This is the architecture ElevenLabs recommends for complex agents:

```
User <-> ElevenLabs Agent (voice orchestration) <-> Stateful Proxy <-> External Agent (your logic)
```

Key components:
- **Stateful Proxy:** Service between ElevenLabs and your agent that maps generation requests to session identifiers. YOU own this service.
- **Session Identifiers:** Passed via `extra_body` during call initiation, flow through ElevenLabs to your proxy
- **Internal State:** Agent's goals, mode of operation, reasoning trace, detected intents/entities/sentiment, current conversational flow
- **External State:** Ongoing tasks, tools/knowledge bases, status of other systems
- **Bidirectional Message Passing:** Proxy can forward VAD events, tool call lifecycle events, etc. between client app and your agent
- **Multi-conversation Mapping:** Single identifier can group web chat sessions, follow-up calls, internal workflows under one logical customer

> "Using these core components and enabling the bidirectional passing of messages between the proxy and the client application allows customers to integrate external agents within ElevenLabs Agents to strictly use the voice orchestration it provides while retaining ownership over all parts of the LLM orchestration."

**Compatible frameworks:** CrewAI, LangChain, LangGraph, HayStack, LlamaIndex -- any framework that supports OpenAI Chat Completions API format.

**Trade-off:** You get ElevenLabs' best-in-class voice but you're essentially building a parallel system. The ElevenLabs visual workflow builder becomes irrelevant -- all logic is in your external agent.

---

### 1.6 The "Rebuilt From Scratch" Case Study

**Source:** Lore Van Oudenhove - "From No-Code to Full Control: How I Rebuilt ElevenLabs' AI Agent with LangGraph and Whisper from Scratch"
**URL:** https://ai.plainenglish.io/from-no-code-to-full-control-how-i-rebuilt-elevenlabs-ai-agent-with-langgraph-and-whisper-from-fd8fe1a112ee

Author rebuilt ElevenLabs agent from ground up using:
- **Whisper** for STT
- **LangGraph** for conversation logic (the "brain")
- **ElevenLabs API** for TTS only (just the voice, not the agent platform)

Architecture: `AudioIn -> Whisper STT -> LangGraph Agent -> ElevenLabs TTS -> AudioOut`

Key insight: Used ElevenLabs exclusively for its voice quality while building all logic in LangGraph. The LangGraph agent had:
- State management via `TypedDict` with annotated message lists
- Memory persistence via `MemorySaver`
- Tool integration (custom tools callable by the LLM)
- Full conversation flow control with graph nodes

> "The no-code approach delivered impressive results, but as a code enthusiast, I wanted more control and customization."

---

## TOPIC 2: Architecture Patterns for Complex Healthcare Voice Agents

---

### 2.1 The Voice Agent Pipeline (Fundamentals)

**Source:** Arun Baby - "Voice Agent Architecture"
**URL:** https://arunbaby.com/ai-agents/0017-voice-agent-architecture/

The six-stage pipeline: `AudioIn -> VAD -> STT -> LLM -> TTS -> AudioOut`

**Critical differentiator between demo and product is CONTROL LOGIC:**
- VAD silence thresholds determine when agent speaks
- Barge-in handling with echo cancellation prevents feedback loops
- Voice-specific prompting keeps responses conversational

**Cost reality:** 10-minute call ranges from $0.29 (economy) to $2.54 (premium stack)

**VAD Tradeoffs:**
- Short timeout (300ms): Snappy but interrupts mid-thought
- Long timeout (1000ms): Polite but feels sluggish
- Adaptive timeout: Use fast LLM to predict if sentence is complete

**Barge-In Protocol:**
1. VAD detects speech energy while agent is SPEAKING
2. Send CLEAR packet to client, wipe audio buffer
3. Kill LLM generation task, kill TTS generation task
4. Transition to LISTENING state
5. Discard what agent was about to say

---

### 2.2 The Voice AI Stack for 2026 (Architecture Patterns)

**Source:** AssemblyAI - "The voice AI stack for building agents in 2026"
**URL:** https://www.assemblyai.com/blog/the-voice-ai-stack-for-building-agents

Three architecture patterns:

| Pattern | Latency | Complexity | Flexibility | Best For |
|---------|---------|------------|-------------|----------|
| Cascading Pipeline | High (800-2000ms) | Low | High | Prototyping, async use cases |
| Streaming Pipeline | Low (<500ms) | Medium | High | Real-time conversation, production |
| All-in-One APIs | Medium (500-1200ms) | Low | Low | Quick deployment, standard use cases |

**Cascading:** Sequential processing. Simple to build/debug but cumulative latency makes conversation unnatural.

**Streaming:** Data flows continuously between components. STT transcribes in chunks, LLM starts generating before full transcript, TTS begins before LLM finishes. "Essential for building agents that can be interrupted and hold a natural conversation."

**The orchestration layer handles:**
- Real-time streaming management
- Turn-taking and interruption handling
- Conversation state tracking
- External API integration

---

### 2.3 The Platform Landscape (Build vs. Buy Decision)

**Source:** Hamming AI - "Best Voice Agent Stack: A Complete Selection Framework"
**URL:** https://hamming.ai/resources/best-voice-agent-stack

Quick decision matrix:

| If you need... | Choose... | Why |
|----------------|-----------|-----|
| Fastest time-to-production (<1 month) | Retell or Vapi | Pre-integrated components, visual builders |
| Lowest latency (<500ms) | Speech-to-speech + custom build | S2S models eliminate text layer overhead |
| Maximum control + auditability | Cascading + LiveKit/Pipecat | Full visibility at each layer |
| **Compliance (HIPAA, SOC2)** | **Bland AI or custom build** | **Clear audit trails, data residency control** |
| Cost efficiency at scale (>50K mins/month) | Custom build with LiveKit | Up to 80% savings vs managed platforms |

Platform comparison:

| Platform | Time to First Call | Monthly Cost (10K mins) | Key Strength | Key Limitation |
|----------|-------------------|------------------------|--------------|----------------|
| Retell | 3 hours | $500-$3,100 | Visual workflow builder | Least flexible; +50-100ms latency overhead |
| Vapi | 2 hours | $500-$1,300 | Strong developer experience/API | Costly at high scale ($0.05-0.13/min) |
| Custom (LiveKit/Pipecat) | 2+ weeks | ~$800 + eng. time | Complete control, lowest latency, 80% cost savings at scale | Large up-front investment (2+ engineers, 3+ months) |

**Key insight:** "roughly half the teams we talk to migrate off [managed platforms] within 12 months once they hit scale or customization limits"

**Source:** AssemblyAI - "6 best orchestration tools to build AI voice agents in 2026"
**URL:** https://www.assemblyai.com/blog/orchestration-tools-ai-voice-agents

Top 6 orchestration tools:
1. **Vapi** - Developer-friendly, visual Flow Studio + API, 1500+ integrations, A/B testing
2. **LiveKit** - Fully open-source, modifiable codebase, native telephony, multimodal
3. **Daily/Pipecat** - Open-source Python framework, vendor-neutral, composable tools, phrase endpointing
4. **Retell** - Natural conversation focus, proprietary turn-taking, <500ms responses, interruptibility
5. **Synthflow** - No-code, drag-and-drop, 200+ pre-built integrations, templates
6. **Bland** - Self-hosted end-to-end, never leaves your network. Financial/healthcare/government use cases.

---

### 2.4 Using LangGraph for Voice Agent Logic

**Source:** DanShw - "Architecting a Medical AI Assistant: LangGraph-Powered Architecture"
**URL:** https://medium.com/@kofsitho/part-2-architecting-a-medical-ai-assistant-a-deep-dive-into-our-langgraph-powered-architecture-f17b51f8883d

Real production medical AI assistant built with LangGraph. Key architectural decisions:

**Why LangGraph over alternatives:**
- **LangChain:** Too linear. Chains work for straightforward tasks but "becomes cumbersome for dynamic, multi-turn conversations"
- **CrewAI:** Too high-level. "Black box behavior" made it hard to control conversation flow
- **AutoGen:** Over-engineered for a single reliable agent. Steep learning curve.
- **LangGraph:** Graph-based, explicit state management, ReAct agent pattern, modular tools

**State Management:**
```python
class State(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
```
- Explicit, persistent state that acts as central memory for entire conversation
- LLM has access to unsent messages, treatment state anchors, limited patient data, read-only message history

**ReAct Agent Pattern:**
- Agent assesses user input -> decides if tool needed -> selects from predefined tools -> returns result to assistant
- Simple but powerful: just two core nodes (assistant + tools)
- Adding new capability = add a tool function to the list. No core graph changes.

**Tool System Design:**
- 6 independent tools, each responsible for one domain
- Each tool queries Qdrant vector database with client-specific filters
- Single Responsibility Principle throughout

**Production Features:**
- Async by default (FastAPI + astream for token-by-token streaming)
- Built-in LLM fallbacks (.with_fallbacks() -- OpenAI primary, Claude fallback)
- Three-service architecture: FastAPI Gateway + LangGraph Agent Service + Extractor Service

---

### 2.5 The State Resolver / Micro-Prompting Pattern

**Source:** Kannappan Suresh - "How I Cut Voice AI Latency by 5x -- By Deleting 90% of the Prompt"
**URL:** https://medium.com/@kannappansuresh99/how-i-cut-voice-ai-latency-by-5x-by-deleting-90-of-the-prompt-cba48fc22555

**This is a critical pattern for healthcare voice agents.**

**Problem:** Most voice agents ship a single 4,000-8,000 token system prompt on every turn. Even when user just says "yes."

**Solution:** State resolvers + micro-prompting

**Architecture:**
```
State machine (FSM) tracks conversation state
  -> State resolver determines current state in microseconds
  -> Micro-prompt (30-50 tokens) loaded for that specific state
  -> LLM gets focused, scoped instructions
```

**Results:**

| Metric | Mega-Prompt | Micro-Prompt | Improvement |
|--------|------------|--------------|-------------|
| Input Tokens/Turn | 4,000-8,000 | 200-800 | ~90% reduction |
| Time to First Token | 800ms-1.5s | 150-300ms | ~5x faster |
| Instruction Adherence | ~85% | ~98% | +13% reliability |

**Net voice-to-voice latency:**
- Mega-prompt: 1.3-2.0s (awkward pause)
- Micro-prompt: 0.65-0.8s (natural conversation)

**Key insight for healthcare:** Each conversation state gets ONLY the context it needs. A medication confirmation state doesn't load the entire patient history, appointment scheduling logic, and insurance verification rules. Just the medication details and confirmation instructions.

**Barge-in handling with micro-prompts:**
1. VAD detects voice while agent SPEAKING
2. TTS playback killed, audio buffer purged
3. LLM generation aborted
4. Only SPOKEN text committed to history (not unspoken generated text)
5. State resolver classifies interruption, transitions to new state
6. New micro-prompt loaded for new state
7. All in ~10ms for symbolic logic, then clean ~200-token prompt to LLM

**Trade-off:** "You're trading prompt generality for speed. A wrong state = a wrong prompt = a wrong response." Requires:
- Robust state transitions
- Confidence thresholds (uncertain? hold current state, ask clarifying question)
- Fallback states (~300 token generic prompt for off-topic)
- Skip detection (user gives info for 3 states in one breath)

---

### 2.6 Building a Clinical AI Agent (Production Case Study)

**Source:** Stride - "How We Built a Clinical AI Agent"
**URL:** https://www.stride.build/blog/how-we-built-a-clinical-ai-agent

**Real production healthcare agent** for at-home treatment of early pregnancy loss. Built with LangGraph + Claude Sonnet.

**From static rules to adaptive agents:**
- Original: "brittle logic trees, hardcoded decision rules, predefined conversational flows"
- Problem: "Any updates required manual code changes. Even minor modifications were time-consuming, fragile, and blocked by limited engineering capacity."
- Solution: LangGraph with Claude Sonnet at center

**Critical design constraints for healthcare:**
- LLM has full access to unsent messages and treatment state anchors
- **Limited access to patient data** (only what it needs, no phone numbers, no medical history beyond what's relevant)
- **Read-only access** to message history (cannot edit historical data or override past)
- Every action logged and traceable (auditability is non-negotiable)

**Graceful Failure Recovery:**
- "Retry node" pattern: when tool call fails (e.g., invalid JSON), system deletes faulty message, loops back to calling node, instructs LLM to retry
- If LLM ends turn without proper response, retry node enforces completion
- Prevents hallucinated tool responses, keeps state machine clean

**Confidence Threshold Pattern:**
- Model evaluates its own confidence
- Below threshold -> escalate to human reviewer
- Distinguishes confidence from correctness: "an answer can be accurate but uncertain, or confident but flawed"
- System reacts based on **operational risk**, not blind trust

**Evaluation Framework:**
- LangSmith for data handling + custom Python evaluation harness
- "Happy path" datasets + targeted edge cases + failure scenarios
- GPT-4o as judge with graded rubric tiers (not exact output match)
- Time-sensitive logic: pre-processed timestamps, normalized time references

**Modularity:**
- Treatment blueprints: once one treatment workflow worked, new ones (e.g., Ozempic) added with just prompt-driven configuration
- Used Cline (agentic coding tool) to generate new treatment configurations
- Frontend/backend unchanged; only treatment blueprint modified

**Async multi-message handling:**
- Patients often send multiple texts in a row
- Configurable delays + thread invalidation logic
- System captures full message burst before responding
- Discards partial responses, recalculates based on most recent state

**Key takeaway:** "We built what we estimate to be a year's worth of conventional software in a few months."

---

### 2.7 Five Failure Modes in Clinical Voice Agents

**Source:** Hamming AI - "5 Failure Modes That Make Voice Agents Unsafe in Clinical Settings"
**URL:** https://hamming.ai/blog/five-failure-modes-that-make-voice-agents-unsafe-in-clinical-settings

| Failure Mode | What Breaks | Clinical Risk |
|--------------|-------------|---------------|
| Perception failures | ASR/NLU mishear or misinterpret | Wrong medication, dosage, or intent |
| Guardrail failures | Safety checks don't trigger | PHI exposure or unsafe instructions |
| Multi-agent reasoning fails | Evidence drops or contradictions persist | Unsafe or inconsistent guidance |
| Workflow logic breaks | State and sequencing drift | Incorrect clinical pathway chosen |
| Latency and infrastructure drift | Slow responses or timing shifts | Interruptions and corrupted inputs |

**Perception Failures (the root of most problems):**
- ~2% of medication names transcribed incorrectly in one deployment
- "Xanax" transcribed as "Zantac" -- patient confirmed "yes" without catching error
- **40% of "agent problems" are actually STT problems** (per Hamming analysis)
- Four types: Non-understanding, Misunderstanding, Misrecognition, Inaccurate transcription

**Guardrail Failures (critical for healthcare):**
- ASR misrecognition can prevent guardrail from triggering ("refill oxycodone" -> "refill my code")
- NLU wrong intent assignment routes to wrong workflow with different guardrails
- LLM rephrasing breaks keyword-based constraints ("dose change" -> "adjust my medication")
- State tracking issues create illusion that security steps already completed

> "Guardrails cannot rely on prompts, regex, or keyword triggers. They must be deterministically enforced."

**Workflow Logic Breaks:**
> "The agent continues speaking fluidly, answering confidently, and appearing to follow protocol, even as it has diverged from the clinically correct sequence."

**Latency as Safety Concern:**
- Slow responses cause patients to repeat/rephrase, generating malformed audio
- Clipped sentences, overlapping speech, broken utterances
- Agent may overwrite previously captured slot values with partial/contradictory information

---

### 2.8 EHR Integration as Non-Negotiable

**Source:** Telnyx - "Why EHR integration defines voice AI success in healthcare"
**URL:** https://telnyx.com/resources/epic-integration-voice-ai-healthcare

Without EHR integration, voice AI hits a ceiling:
- **No reliable identity or history:** Agent can't see allergies, active medications, recent visits
- **Manual rework:** If agent collects info but can't write back to EHR, staff manually enters it
- **Fragmented patient experience:** Voice AI and EHR data out of sync
- **Limited ROI:** Can't prove value without touching core metrics

What meaningful integration looks like:
- Look up patient records live during call
- Manage scheduling using same rules as staff
- Automate outbound outreach, log responses back to EHR
- Trigger actions based on clinical events (new lab results, discharge milestones)

**Telnyx + Epic MCP integration example:** AI agents read/update patient info in real time via Epic MCP APIs.

**Healthcare guardrails via EHR:**
> "If a patient with specific risk factors calls about chest pain, the agent can escalate immediately based on documented history."

---

### 2.9 Healthcare-Specific Agent Design (Artera's Approach)

**Source:** Artera - "Beyond the Prompt: Designing Agentic AI for Healthcare Providers"
**URL:** https://artera.io/blog/agentic-ai-for-healthcare-providers/

**Key principle:** "Building effective AI agents for healthcare is a whole different ballgame. These agents manage critical, multi-step workflows where the margin for error is virtually nonexistent."

**Prompt Engineering Techniques for Healthcare:**

1. **Narrow Scope:** "A scheduling agent should ONLY focus on scheduling." Overly broad prompts yield unhelpful results.

2. **Safety Guardrails:** Explicit do/don't instructions. "You are not a doctor; do not provide medical advice." Handle ambiguous responses (patient says "maybe" to a yes/no -> re-ask, don't assume).

3. **Modular Template System:**
   - Foundational "healthcare agent" template: universal safety guardrails, ethical protocols
   - Secondary "use case" template: customizes for specific workflow
   > "Resist the urge to over-engineer agent prompts for a quick fix... While this might seem efficient for a fast go-live, it's brittle and introduces risk."

4. **Iterative/Flexible Prompts:** Modular sections that can be tested/modified independently.

**Tools > Prompts:**
> "When we initially started building agents, we relied heavily on prompts to guide them. But we quickly learned that giving them the right tools is what really levels up the agent's capabilities."

- Tools perform backend API calls, return only structured/relevant data
- System designed to **limit agent's knowledge to only what's necessary**
- Moving toward MCP (Model Context Protocol) handling more information

**Measurement approach:** Think of it as a conversion funnel. Patient enters -> checkpoints (verify identity, identify reason, check providers, confirm eligibility) -> book appointment. Monitor drop-off at each checkpoint.

**Real result:** Name recognition improvement via backend engineering that interacts with prompt -> **46.15% increase in success rate** for patient name matching.

**LLM-as-a-Judge (LAJ):** Automated scoring of conversations on task completion, compliance/safety, workflow adherence, agent errors, patient experience.

---

### 2.10 Context Engineering for Voice Agents

**Source:** ElevenLabs Blog - "Integrating external agents"
**URL:** https://elevenlabs.io/blog/integrating-complex-external-agents

State management categories for voice agents with complex external agents:

**Internal State:**
- Configuration and operational parameters (active goals, mode of operation, temporary constraints)
- Reasoning trace (intermediate thoughts, hypotheses, prior attempts)
- Real-time transcript analysis (detected intents, entities, sentiment)
- Current conversational flow (voice activity, interruptions, active speaker)

**External State:**
- Ongoing tasks and dependencies involving external systems
- Tools and knowledge bases (APIs, databases, integrations)
- Status of other users or systems

**Strict separation:** Proxy maintains interaction table + stateless routing. External agent handles all substantive state.

---

### 2.11 The Orchestration Layer Pattern (Summary)

The dominant pattern for complex healthcare voice agents separates concerns into layers:

```
┌──────────────────────────────────────────────────┐
│              TELEPHONY / TRANSPORT                │
│  (Twilio, SIP, WebRTC, LiveKit)                  │
├──────────────────────────────────────────────────┤
│              VOICE INFRASTRUCTURE                 │
│  STT: Deepgram / AssemblyAI / Whisper            │
│  TTS: ElevenLabs / Cartesia / Rime               │
│  VAD: Silero / WebRTC                            │
├──────────────────────────────────────────────────┤
│         ORCHESTRATION / CONTROL LOGIC             │
│  (LiveKit Agents / Pipecat / Vapi / Custom)       │
│  - Turn-taking, barge-in, streaming management    │
│  - State machine / conversation flow              │
│  - Context scoping per state                      │
├──────────────────────────────────────────────────┤
│           AGENT / CONVERSATION LOGIC              │
│  (LangGraph / LangChain / Custom state machine)   │
│  - Dynamic prompt construction                    │
│  - Tool calling (EHR, CRM, scheduling)            │
│  - Guardrails enforcement                         │
│  - Confidence scoring + human escalation          │
│  - Patient context management                     │
├──────────────────────────────────────────────────┤
│              EXTERNAL SYSTEMS                     │
│  EHR (Epic, Cerner), CRM, Scheduling,            │
│  Knowledge bases, Compliance logging              │
└──────────────────────────────────────────────────┘
```

**Key principle:** The voice infrastructure (how it sounds) is completely decoupled from the conversation logic (what it says and does). This enables:
- Swapping TTS/STT providers without touching logic
- Testing conversation logic without voice pipeline
- Independent scaling of voice infrastructure vs. logic
- Healthcare-specific guardrails applied at the logic layer, not the voice layer

---

## KEY URLS INDEX

### ElevenLabs Limitations
1. https://orangeloops.com/2025/12/elevenlabs-voice-ai-agents-pros-limits-when-to-use-langgraph/
2. https://elevenlabs.io/blog/integrating-complex-external-agents
3. https://www.webfuse.com/blog/a-deep-dive-into-elevenlabs-agent-workflows
4. https://memu.pro/blog/elevenlabs-agents-voice-memory
5. https://ai.plainenglish.io/from-no-code-to-full-control-how-i-rebuilt-elevenlabs-ai-agent-with-langgraph-and-whisper-from-fd8fe1a112ee
6. https://elevenlabs.io/docs/agents-platform/customization/llm/custom-llm
7. https://elevenlabs.io/blog/elevenlabs-agents-vs-openai-realtime-api-conversational-agents-showdown

### Voice Agent Architecture & Stack
8. https://arunbaby.com/ai-agents/0017-voice-agent-architecture/
9. https://www.assemblyai.com/blog/the-voice-ai-stack-for-building-agents
10. https://hamming.ai/resources/best-voice-agent-stack
11. https://www.assemblyai.com/blog/orchestration-tools-ai-voice-agents
12. https://www.arunbaby.com/ai-agents/0018-voice-agent-frameworks/

### Healthcare-Specific
13. https://hamming.ai/blog/five-failure-modes-that-make-voice-agents-unsafe-in-clinical-settings
14. https://www.stride.build/blog/how-we-built-a-clinical-ai-agent
15. https://medium.com/@kofsitho/part-2-architecting-a-medical-ai-assistant-a-deep-dive-into-our-langgraph-powered-architecture-f17b51f8883d
16. https://telnyx.com/resources/epic-integration-voice-ai-healthcare
17. https://artera.io/blog/agentic-ai-for-healthcare-providers/
18. https://hamming.ai/resources/hipaa-phi-clinical-workflow-testing-checklist
19. https://www.simbo.ai/blog/overcoming-implementation-challenges-in-deploying-voice-ai-agents-in-healthcare-addressing-performance-latency-compliance-guardrails-and-seamless-integration-with-core-hospital-systems-2073496/

### Architecture Patterns & Techniques
20. https://medium.com/@kannappansuresh99/how-i-cut-voice-ai-latency-by-5x-by-deleting-90-of-the-prompt-cba48fc22555
21. https://www.zedhaque.com/blog/safety-acts-realtime/
22. https://elevenlabs.io/blog/safety-framework-for-ai-voice-agents
23. https://www.gladia.io/blog/safety-voice-ai-hallucinations
24. https://docs.synthflow.ai/dynamic-prompt-injection
25. https://medium.com/@deepinfinityai/context-engineering-in-healthcare-agents-shaping-smarter-safer-ai-in-medicine-649d3c76dcd8

### Platform Comparisons
26. https://www.whitespacesolutions.ai/content/bland-ai-vs-vapi-vs-retell-comparison
27. https://orbilontech.com/vapi-vs-retell-voice-ai-platform-comparison-2026/
28. https://docs.vapi.ai/customization/custom-llm/using-your-server
29. https://www.roomkit.live/blog/choosing-the-right-conversational-ai-framework/
30. https://www.speechmatics.com/company/articles-and-news/best-voice-ai-agent-platforms-2025

### LangGraph / State Machine Resources
31. https://github.com/Md-Emon-Hasan/MediGenius (LangGraph medical AI assistant, open source)
32. https://levelup.gitconnected.com/langgraph-for-healthcare-a-comprehensive-technical-guide-e6038b06c108
33. https://activewizards.com/blog/architecting-event-driven-conversational-agents-with-langgraph
34. https://www.youtube.com/watch?v=sn79oS4MZFI (Stride + Avila telemedicine agents workshop)
