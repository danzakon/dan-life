---
id: 20260308-AD-009
created: 2026-03-08
source-type: research
ingest-source: content-pipeline
status: approved
format: article
platform: Both
series-id:
generate: single
next-action: draft
---

## Core Insight
Voice AI latency is not a model problem — it's a context engineering problem — and the fix is counterintuitive: use dramatically less prompt, not more.

## Draft Instructions
The framing: most teams building voice agents ship a single 4,000-8,000 token system prompt on every turn. Even when the user says "yes." The solution: state machines + micro-prompts. A fast state resolver (symbolic logic, ~10ms) determines the current conversation state, then loads a 200-800 token micro-prompt scoped to that state. Results: input tokens drop 90%, time to first token goes from 800ms-1.5s to 150-300ms, instruction adherence improves from ~85% to ~98%. Net voice-to-voice latency: 1.3-2.0s (mega-prompt) vs 0.65-0.8s (micro-prompt). Frame this as practical architecture guidance. Also touch on the streaming pipeline pattern (STT transcribes in chunks, LLM starts before full transcript, TTS begins before LLM finishes) as the baseline for real-time voice. This is not written from a "I did this" perspective — it's "here's the pattern and the numbers behind it."

## Sources
- research/reports/20260225-voice-ai-platform-comparison.md

## Related Items
- 20260308-AD-010
