# Vapi Voice AI Platform - Raw Research Findings

**Date:** 2025-02-25
**Context:** Evaluating Vapi for Pairteam healthcare voice agent (outbound patient engagement, complex multi-turn conversations, behavioral rules)

---

## 1. ARCHITECTURE & HOW IT WORKS

### Core Pipeline

Vapi is a **voice orchestration platform** that connects STT -> LLM -> TTS into a unified pipeline.

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  Audio   │───>│   STT    │───>│   LLM    │───>│   TTS    │───> Audio Out
│  Input   │    │(Deepgram,│    │(OpenAI,  │    │(11Labs,  │
│          │    │ Azure,   │    │ Anthropic│    │ Azure,   │
│          │    │ Assembly)│    │ Custom)  │    │ PlayHT)  │
└──────────┘    └──────────┘    └──────────┘    └──────────┘
       │                                               │
       └──────── Orchestration Layer (Vapi) ──────────┘
         - Endpointing (custom audio-text fusion model)
         - Interruption handling (barge-in detection)
         - Background noise filtering (proprietary)
         - Background voice filtering (proprietary)
         - Backchanneling ("uh-huh", "got it")
         - Emotion detection (real-time audio model)
         - Filler injection ("umm", "like", "so")
```

**Source:** https://docs.vapi.ai/how-vapi-works

### Orchestration Models (Proprietary)

Vapi runs a suite of proprietary audio and text models on top of core STT/LLM/TTS:

- **Endpointing:** Custom fusion audio-text model that uses both tone and content to decide when user is done speaking. Not just silence detection -- considers semantic completeness.
- **Interruptions (Barge-in):** Custom model distinguishes true interruptions ("stop", "hold up") from backchannel ("yeah", "oh gotcha"). Also tracks where assistant was cut off so LLM knows what it couldn't say.
- **Background Noise Filtering:** Proprietary real-time noise filtering without latency sacrifice.
- **Background Voice Filtering:** Proprietary model that focuses on primary speaker and blocks background voices (TV, echo). This is a harder problem than noise -- "not well-researched."
- **Backchanneling:** Proprietary model determines best moment to backchannel and which cue to use.
- **Emotion Detection:** Real-time audio model extracts emotional inflection, feeds to LLM so it can adapt behavior.
- **Filler Injection:** Custom model converts formal LLM output to sound conversational with fillers -- without modifying the actual prompt.

**Source:** https://docs.vapi.ai/how-vapi-works

### Latency Architecture

Vapi treats the 1200ms latency budget as a scarce resource. Key insight from their blog:

- Conversational flow breaks when latency exceeds 1200ms
- The bottleneck is almost always the LLM (time to first meaningful sentence)
- They tracked OpenAI GPT-4o mini over 7 days -- latency was wildly unstable. "A model that performs well on a Friday night can be unusable on Monday morning."
- They have 40+ Azure OpenAI deployments and built a dynamic routing system

**Their latency solution (multi-step evolution):**
1. Brute-force race (send to all 40+ deployments, use first response) -- too expensive (40x tokens)
2. Polling every 10 minutes for fastest deployment -- still saw spikes lasting 5+ minutes between polls
3. Live production data + exploration -- route most to fastest known endpoint, send small subset to test others (explore/exploit)
4. Dynamic fallback -- if request to fastest deployment is an outlier (based on per-deployment historical std dev), cancel and fire to second-fastest. Chained fallbacks.

**Result:** Shaved over 1000ms off P95 latency.

**Claimed latency:** Sub-600ms response time. Real-world: 550-800ms depending on provider choices and geography.

**Source:** https://vapi.ai/blog/how-we-solved-latency-at-vapi

### API Structure

- REST API with endpoints for: Assistants, Squads, Calls, Campaigns, Sessions, Chats, Phone Numbers
- Webhook-driven event system for real-time call events
- `POST /call/phone` for outbound calls
- `PATCH /assistant/{id}` for updates
- Structured outputs via JSON Schema extraction
- Dynamic variables via `{{variableName}}` in prompts with LiquidJS templating

**SDKs:**
- Python: `pip install vapi_server_sdk` (official, 25 stars, auto-generated via Fern)
- Node.js/TypeScript: server SDK available
- Web SDK for browser-based calls
- CLI tool (`vapi init` detects framework, generates code)
- Supported frameworks: React, Vue, Angular, Next.js, Svelte, React Native, Flutter, Python, Node.js, Go, Ruby, Java, C#/.NET

**Sources:**
- https://github.com/VapiAI/server-sdk-python
- https://docs.vapi.ai/api-reference/assistants/create-assistant
- https://docs.vapi.ai/cli/init

### Three Ways to Build Agents

1. **Assistants:** Single-agent, single-topic conversations. Configure model, voice, transcriber, tools.
2. **Squads:** Multi-agent orchestration with handoffs between specialized assistants. Each assistant in the squad has its own prompt/tools/voice config.
3. **Workflows:** Visual node-based builder with discrete steps (Say, Gather, API Request, Transfer, Hangup) and conditional edges. Currently in Open Beta.

**Critical community insight (Sep 2025):**
> "Workflows are pretty much deprecated at this point." -- community member
> "With Workflows, the reliance on strict if-statements feels like a rigid decision tree -- not well-suited for live calls where topics can shift dynamically."
> "With Squads, the forced transfer between agents often breaks the natural conversation flow."
> "The agent can't 'jump' across nodes or reuse prompt training from other branches of the tree, which limits flexibility."

**Source:** https://vapi.ai/community/m/1414880041480749056

---

## 2. CONTROL & STEERABILITY

### Dynamic Variables

- Use `{{variableName}}` in system prompts and messages
- Set via `assistantOverrides.variableValues` when placing calls
- Built-in variables: `{{now}}`, `{{date}}`, `{{time}}`, `{{customer.number}}`, `{{transport.conversationType}}`
- Supports LiquidJS date formatting with timezone: `{{"now" | date: "%A, %B %d, %Y", "America/Los_Angeles"}}`
- Can conditionally change prompt based on `transport.conversationType` (chat vs voice)
- **Cannot set variable values directly in the dashboard** -- must use API

**Source:** https://docs.vapi.ai/assistants/dynamic-variables

### Custom LLM Integration

You can bring your own LLM by pointing Vapi to a custom endpoint:
- Set up a server that accepts POST requests at `/chat/completions`
- Vapi sends conversation context and metadata
- Your server processes and returns OpenAI-compatible response format
- Use Ngrok for local dev, any HTTPS endpoint for production
- Full control over model selection, preprocessing, postprocessing

**Source:** https://docs.vapi.ai/customization/custom-llm/using-your-server

### Tool Calling / Function Calling

- Define custom tools that the LLM can invoke during conversation
- Webhook-based: Vapi POSTs to your server URL when tool is called
- Server returns result which is fed back to LLM
- **Important:** Webhook timeout is 5 seconds. If your API takes >3s, return immediately and process async.
- Support for MCP (Model Context Protocol) server integration

**Known issue:** When using Custom LLM with tool calls, "after a tool run, the tool call and response are not passed to our LLM. This makes the LLM lose context on what has happened." (Community report, May 2025)

**Source:** https://vapi.ai/community/m/1374394319162572970

### Context / Memory Management

**Injecting context at call start:**
- Pass `variableValues` in the call creation payload
- Pass `assistantOverrides` to customize behavior per-call
- Include patient history, condition details, etc. in the system prompt via variables

**Cross-call context (memory between calls):**
- Vapi does NOT natively store conversation history between calls
- Community question (Sep 2025): "How to put the context of past calls into a newer call?" -- no native solution
- You must implement this yourself: store transcripts/summaries in your DB, inject into next call's system prompt

**Mid-call dynamic updates:**
- System prompt CANNOT be replaced mid-call dynamically based on conversation content (community confirmed, May 2024)
- "Currently, Vapi does not support dynamically altering the system prompt during a call based on the content of responses"
- Workaround: Use tool calls to fetch new context and return it as tool results
- Workflows can branch to different nodes with different prompts, but it's rigid

**Source:** https://vapi.ai/community/m/1241162638566621194, https://vapi.ai/community/m/1412339761904881704

### Structured Outputs

- Define JSON Schema for data extraction from calls
- Automatically extracts structured data after each call
- Can use any AI model (OpenAI, Anthropic, Google, Azure)
- Reusable definitions across multiple assistants

**Source:** https://docs.vapi.ai/assistants/structured-outputs

### Conversation State Management

- Squads enable multi-assistant flows with handoffs
- Silent transfers possible (same voice across assistants, caller doesn't notice)
- Context passed between assistants in a squad
- For complex branching: Squads > Workflows (Workflows feels deprecated)
- **No native cross-node learning or dynamic jumping between conversation branches**

### Outbound Campaigns

- CSV upload for batch outbound campaigns (shipped Jun 2025)
- API-based outbound calling for programmatic campaigns
- Previously required external tools (Make.com, n8n) for campaign orchestration
- Campaign management via API: create, list, get, delete, update

**Source:** https://vapi.ai/blog/now-run-outbound-call-campaigns-with-vapi

---

## 3. LIMITATIONS & PAIN POINTS

### Developer Complaints (Aggregated)

**Squads feature is buggy and hard to use:**
> "One feature I was incredibly excited about was 'Squads.' In practice, it was a headache. I found it incredibly hard to understand and set up. The documentation didn't quite bridge the gap between theory and practice. When I finally did get a configuration that looked correct, it simply didn't work. It was buggy, unreliable."
-- TopAutomator review, Dec 2025

**Workflows are too rigid:**
> "With Workflows, the reliance on strict if-statements feels like a rigid decision tree -- not well-suited for live calls where topics can shift dynamically."
-- Vapi community, Sep 2025

**Saving progress doesn't work:**
> "The most frustration came from simple UI interactions -- saving my progress. There were times I would spend an hour tweaking a prompt or a configuration, hit save, and... nothing. The progress wouldn't stick."
-- TopAutomator review

**Documentation is incomplete:**
> "The platform relies on passing variables into the prompt to make the AI personalized... You would assume there is a clear list of 'System Variables' in the sidebar of the docs. There isn't. I spent ages trying to figure out how to pass the customer's phone number automatically into the prompt context."
-- TopAutomator review

**Support is slow:**
> "VAPI Support is so terrible. They take min 24 hours to reply to messages, then disappear for another 24 hours."
> "Complaint: How do I get faster support from Vapi? ...it can take days if not weeks to get the issue resolved."
-- Multiple community posts, Jun 2025

**Outbound flow is virtually non-existent in dashboard:**
> "The biggest shock for me was the outbound calling architecture... you cannot easily set up a complex outbound campaign sequence strictly within their dashboard. To get any real value out of it, you have to connect it to external automation tools."
-- TopAutomator review

**Unfixable incorrect responses:**
> "My VAPI assistant has a major malfunction. After this step where we ask if the recipient can make a full payment... EVERY time, no matter what the person says - 'SURE', 'YES', 'ABSOLUTELY'... The VAPI assistant always [gives wrong response]."
-- Community post, May 2025

**Transcription accuracy issues:**
> "Transcriber is not able to get the spelling of my name properly. Even if I spell my name it gives different spellings every time."
-- Community post, Jun 2025

**Pipeline errors:**
> "We've been receiving following error when the call gets connected to our customers: pipeline-error-openai-llm-failed. However, the openai api key is active and has enough credits."
-- Community post, May 2025

**Intermittent latency spikes:**
> "Hello, recently I have experienced a huge latency in my voice agent... 5 seconds"
> "We've been experiencing 3-4 second delays with responses across all client calls, it's very disruptive to the calls"
> Similar threads: "Huge Call Latency - 10 seconds", "High Latency"
-- Multiple community posts throughout 2025

**Assistant messages lost:**
> "URGENT: hitting some very weird bugs that make voice calls completely unusable... The assistant says messages after the user answers, but the assistant messages are not picked up in the recording, transcript, or even model messages."
-- Community post, Oct 2025

**Sources:**
- https://topautomator.com/reviews/vapi-review
- https://vapi.ai/community/m/1388531370124640378
- https://vapi.ai/community/m/1384762241343447070
- https://vapi.ai/community/m/1380169001157791845
- https://vapi.ai/community/m/1435457717874458624
- https://vapi.ai/community/m/1415236753589141514
- https://vapi.ai/community/m/1424203104005390356

### Platform Stability (Status Page)

Selected incidents from status.vapi.ai:
- **Nov 14, 2024:** ElevenLabs degraded
- **Nov 12, 2024:** API degraded -- DB contention, monitoring probes missed it
- **Nov 11, 2024:** Phone calls degraded -- API gateway rejected WebSocket requests
- **Apr 29, 2025:** Call recordings failing for some users
- **Apr 22, 2025:** 404 errors on phone numbers -- new CIDR range caused SIP discovery issues
- **Apr 04, 2025:** Phone calls stuck in queued state + API degradation (503s)
- **Apr 02, 2025:** Intermittent 503s in API

**Source:** https://status.vapi.ai/incidents/

### The "Speed to Demo vs Speed to Production" Gap (Coval Review, Feb 2026)

This is the most important critique. Key quotes:

> "Vapi will get you to a working demo faster than any other voice AI platform. Period."

> "But speed to demo isn't speed to production. And 'easy to start' isn't the same as 'right for your project.'"

**Where teams hit the ceiling:**
- Custom models for specialized domains (medical terminology, heavy accents)
- Proprietary voice synthesis for brand differentiation
- **Advanced conversation state management across complex multi-turn flows**
- Deep latency optimization below what Vapi exposes
- Full ownership of tech stack for competitive reasons

> "If you need... advanced conversation state management across complex multi-turn flows... you'll eventually find Vapi's abstractions limiting."

**Source:** https://www.coval.dev/blog/vapi-review-2026-is-this-voice-ai-platform-right-for-your-project

### TopAutomator Rating Breakdown (7.5/10)

| Category | Rating |
|---|---|
| Ease of understanding | 4.8/10 |
| Setup & onboarding | 4.2/10 |
| Pricing & value | 9.0/10 |
| Features | 8.5/10 |
| Integrations | 9.6/10 |
| **Reliability** | **6.8/10** |
| Speed & performance | 9.8/10 |
| **Support & docs** | **3.5/10** |
| Customization | 9.7/10 |
| Usefulness / ROI | 9.5/10 |

Notable: Reliability at 6.8 and Support & docs at 3.5 are the weakest areas.

**Source:** https://topautomator.com/reviews/vapi-review

---

## 4. HEALTHCARE-SPECIFIC

### HIPAA Compliance

Vapi offers HIPAA compliance with important caveats:

**How it works:**
- Set `hipaaEnabled: true` at organization or assistant level
- When enabled: NO call logs, recordings, or transcriptions are stored by Vapi
- End-of-call report is generated and sent to YOUR server
- PHI may only pass through the `/call` endpoint -- NOT in `/assistant` prompts or `/phone-number` labels
- When HIPAA mode on, Vapi uses HIPAA-compliant services (e.g., Azure OpenAI) for processing

**Cost:**
- Basic HIPAA mode: Included in $0.05/min platform fee
- HIPAA zero-retention add-on: **$1,000/month**
- Reddit community member: "I noticed that VAPI charges around $1k extra just to enable HIPAA compliance"

**Key restrictions with HIPAA enabled:**
- No access to call logs, recordings, or transcriptions in Vapi dashboard
- Variables are only available during active call session, not persisted
- Structured outputs are generated but not stored -- you get them via webhook only
- You lose visibility in Vapi's built-in analytics

**Your responsibilities under BAA:**
1. Do NOT put PHI in API endpoints other than `/call`
2. Use HIPAA-compliant enterprise accounts with ALL third-party providers (STT, LLM, TTS)
3. Do NOT use underlying providers through Vapi without your own HIPAA-compliant enterprise accounts with those providers

**Healthcare implementations documented:**
- Appointment scheduling with EHR integration (CallStack.tech tutorial, Feb 2026)
- Custom voice profiles for healthcare (CallStack.tech, Jan 2026)
- Patient satisfaction follow-up agents (Vapi template)
- Telehealth intake with HIPAA compliance (dev.to tutorial, Dec 2025)

**Important architectural pattern for healthcare:**
- Vapi handles voice orchestration
- YOUR server handles ALL PHI
- PHI extraction happens on YOUR webhook server, not in Vapi
- Use encrypted database on your side
- Vapi purges all data when `hipaaEnabled: true`

**Source:** https://docs.vapi.ai/security-and-privacy/hipaa, https://dev.to/callstacktech/building-a-hipaa-compliant-telehealth-solution-with-vapi-what-i-learned-18n4

### Medical-Specific STT

- Deepgram `nova-2-medical` model available for medical vocabulary
- Generic models misinterpret medical terms: "metformin" transcribed as "met for men" (47 occurrences in 30 days -- real production error)
- Custom keywords can boost recognition for domain-specific terms by 15-20%

---

## 5. DEVELOPER EXPERIENCE

### SDK Quality

**Python SDK:**
- Auto-generated via Fern (common for API-first companies)
- 25 GitHub stars, 12 forks, 50 commits
- Sync and async clients available
- Built-in retries with exponential backoff (408, 429, 5xx)
- Pagination support
- Custom httpx client support (proxies, transports)
- **Con:** Auto-generated = less idiomatic Python, may feel clunky

**CLI:**
- `vapi init` detects framework and generates boilerplate
- 29 GitHub stars
- Relatively new

### Documentation Quality

Mixed feedback:
- **Positive:** Coval review says "The documentation is clear, the API is intuitive"
- **Negative:** TopAutomator says "Key information (like prompt variables) is hidden or poorly documented"
- **Negative:** "I spent ages trying to figure out how to pass the customer's phone number automatically into the prompt context"
- Variable syntax and system variables are not prominently documented
- Custom LLM integration guide uses outdated `gpt-3.5-turbo-instruct` example

### Community

- Discord server: 24,000+ members (as of late 2025)
- Active community forum at vapi.ai/community
- Many questions go unanswered or get bot responses
- Support bot often provides generic answers that don't solve the issue

### Debugging

- Call logs with transcripts and recordings (when not in HIPAA mode)
- Webhook events for real-time debugging
- Automated testing suite for simulating calls
- Boards for custom analytics dashboards
- **No native deep debugging of orchestration layer** -- you can't see why endpointing/interruption decisions were made

---

## 6. UNIQUE ADVANTAGES

### Speed to Prototype

Universally praised as the fastest path to a working voice agent:
> "Sign up takes 10 minutes. Pick a template or build from scratch in another 20 minutes. Configure your first agent in 30 minutes. Make a test call immediately."

### Provider Flexibility

- Mix and match STT, LLM, and TTS providers
- Not locked into any single provider
- Can use OpenAI Realtime API OR traditional cascading pipeline
- Supports: OpenAI, Anthropic, Azure, Groq, Deepgram, AssemblyAI, ElevenLabs, PlayHT, Azure Neural TTS, Cartesia, and more
- Can bring your own custom LLM endpoint

### Automated Testing

- Simulate calls without manually dialing
- Define expected behavior with exact match, regex, or AI judges
- Chat mode (faster, text-based) or voice mode (actual audio)
- CI/CD integration potential

### Scale

- 350,000+ developers
- 150M+ calls processed
- 99.99% uptime SLA (enterprise)
- Handles millions of concurrent calls with auto-scaling

### Multi-Agent Orchestration (Squads)

- Unique capability for specialized agent handoffs
- Silent transfers (same voice, caller doesn't notice)
- Each agent has own tools, prompts, voice config
- **But:** Currently buggy and hard to implement reliably

### Proprietary Orchestration Intelligence

No competitor offers the same depth of:
- Custom endpointing model (not just silence detection)
- Background voice filtering (novel problem)
- Emotion-aware LLM context
- Automatic filler injection without prompt modification

---

## 7. PRICING

### Structure

- **Platform fee:** $0.05/min (Ad-Hoc plan)
- **On top of that:** STT + LLM + TTS + Telephony charges
- **Real cost:** $0.13-0.35/min all-in depending on provider choices

### Tiers

| Plan | Monthly Fee | Minutes Included | Effective Rate |
|---|---|---|---|
| Ad-Hoc | $0 | Pay-as-you-go | ~$0.18/min |
| Agency | $400-500/mo | 3,000 | ~$0.18/min |
| Startup | $800/mo | 7,500 | ~$0.16/min |
| Enterprise | Custom | Custom | Negotiated |

### HIPAA Add-ons
- Basic HIPAA mode: Included
- Zero-retention add-on: $1,000/mo

### Key pricing concerns
- "Vapi's $0.05/minute base rate requires additional third-party services that multiply real costs by 3-6x"
- "Usage-based pricing provides flexibility at low volumes but becomes harder to predict as volume increases"
- Telnyx reports Vapi has a 2.6 Trustpilot rating, "particularly around pricing transparency"

**Sources:**
- https://telnyx.com/resources/vapi-pricing
- https://callbotics.ai/blog/vapi-pricing
- https://www.cloudtalk.io/blog/vapi-ai-pricing/

---

## 8. COMPETITIVE POSITIONING (from AssemblyAI Comparison)

| Platform | Strength | Trade-off |
|---|---|---|
| **Vapi** | Speed + flexibility, visual + API | Abstraction ceiling for complex flows |
| **LiveKit** | Open-source, maximum control | More dev work required |
| **Pipecat (Daily)** | Vendor-neutral, composable | Framework, not platform |
| **Retell** | Natural conversation, <500ms | Strict/opinionated, less flexible |
| **Synthflow** | No-code, 200+ integrations | Limited customization |
| **Bland** | Self-hosted, enterprise security | Narrower ecosystem |

**Source:** https://www.assemblyai.com/blog/orchestration-tools-ai-voice-agents

---

## 9. ASSESSMENT FOR PAIRTEAM USE CASE

### Requirements vs Capabilities

| Requirement | Vapi Capability | Risk Level |
|---|---|---|
| Outbound calls to patients | Supported (API + Campaigns) | LOW |
| Patient education per condition | Dynamic variables + custom prompts | MEDIUM |
| Complex multi-turn conversations | Possible but hits ceiling | HIGH |
| Complex behavioral rules | Squads or Workflows (both limited) | HIGH |
| HIPAA compliance | Supported ($1k/mo add-on) | MEDIUM |
| Custom conversation flows | Limited dynamic branching | HIGH |
| Context injection (patient history) | Via variables at call start | MEDIUM |
| Mid-conversation context updates | NOT natively supported | HIGH |

### Key Risks for Pairteam

1. **Complex conversation flow management** -- This is Vapi's weakest area. Workflows are rigid decision trees. Squads force agent transfers. Neither supports the fluid, dynamic multi-branch conversations needed for patient education about specific conditions.

2. **No dynamic system prompt updates mid-call** -- If the patient reveals new information that should change the agent's behavior (e.g., reveals a new condition), you can't update the system prompt mid-conversation. Workaround: Use tool calls, but it's hacky.

3. **Squads reliability** -- If you need multi-agent coordination for different conversation phases, Squads is the right feature but it's described as "buggy" and "unreliable" by multiple reviewers.

4. **Support responsiveness** -- With healthcare production workloads, slow support (24-48hr response times) is a real risk.

5. **Platform stability** -- Regular incidents on status page. Latency spikes of 3-5+ seconds reported by multiple users.

### Where Vapi Could Work for Pairteam

1. **Rapid prototyping** -- Get a working demo extremely fast to test conversation flows
2. **Provider flexibility** -- Medical-optimized STT (Deepgram nova-2-medical), choice of LLM
3. **Outbound campaigns** -- Native CSV campaign support + API for programmatic outreach
4. **HIPAA framework** -- Architecture pattern (Vapi handles voice, your server handles PHI) is well-documented
5. **Custom LLM** -- Could use own model endpoint for complex behavioral logic

---

## KEY SOURCES

| Source | URL | Date |
|---|---|---|
| Coval.dev Vapi Review 2026 | https://www.coval.dev/blog/vapi-review-2026-is-this-voice-ai-platform-right-for-your-project | Feb 14, 2026 |
| TopAutomator Vapi Review | https://topautomator.com/reviews/vapi-review | Dec 17, 2025 |
| Vapi Orchestration Docs | https://docs.vapi.ai/how-vapi-works | Current |
| Vapi Workflows Docs | https://docs.vapi.ai/workflows | Current |
| Vapi HIPAA Docs | https://docs.vapi.ai/security-and-privacy/hipaa | Current |
| Vapi Custom LLM Docs | https://docs.vapi.ai/customization/custom-llm/using-your-server | Current |
| Vapi Dynamic Variables | https://docs.vapi.ai/assistants/dynamic-variables | Current |
| Vapi Latency Blog | https://vapi.ai/blog/how-we-solved-latency-at-vapi | Jul 14, 2025 |
| HIPAA Telehealth Tutorial | https://dev.to/callstacktech/building-a-hipaa-compliant-telehealth-solution-with-vapi-what-i-learned-18n4 | Dec 24, 2025 |
| Healthcare Appointment Scheduling | https://callstack.tech/blog/how-to-set-up-vapi-for-ai-appointment-scheduling-in-healthcare-a-developer-s-guide | Feb 5, 2026 |
| AssemblyAI Orchestration Comparison | https://www.assemblyai.com/blog/orchestration-tools-ai-voice-agents | Jan 6, 2026 |
| SoftwareCurio User Feedback | https://www.softwarecurio.com/blog/vapi-ai-review-2026-in-depth-analysis-honest-user-feedback-pros-cons/ | Jan 12, 2026 |
| Telnyx Pricing Analysis | https://telnyx.com/resources/vapi-pricing | Feb 10, 2026 |
| CallBotics Pricing Breakdown | https://callbotics.ai/blog/vapi-pricing | Jan 30, 2026 |
| Ry Walker Research | https://rywalker.com/research/vapi | Feb 14, 2026 |
| Vapi Status Page | https://status.vapi.ai/incidents/ | Ongoing |
| Community: Assistants vs Squads vs Workflows | https://vapi.ai/community/m/1414880041480749056 | Sep 9, 2025 |
| Community: Support complaints | https://vapi.ai/community/m/1388531370124640378 | Jun 28, 2025 |
| Community: Latency issues | https://vapi.ai/community/m/1435457717874458624 | Nov 5, 2025 |
| Community: Tool call context loss | https://vapi.ai/community/m/1374394319162572970 | May 20, 2025 |
| Community: Cross-call context | https://vapi.ai/community/m/1412339761904881704 | Sep 2, 2025 |
| Community: Dynamic prompt replacement | https://vapi.ai/community/m/1241162638566621194 | May 17, 2024 |
| Python SDK GitHub | https://github.com/VapiAI/server-sdk-python | Current |
| Vapi Outbound Campaigns Blog | https://vapi.ai/blog/now-run-outbound-call-campaigns-with-vapi | Jun 26, 2025 |
