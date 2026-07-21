# Module 9 — Resources: Voice Agent Testing

---

## The Stack

### Sarvam (ears + mouth)
- [Sarvam Playground](https://platform.sarvam.ai/api-playground/) — try STT/TTS in the browser; find valid speaker + model names
- [Sarvam Dashboard](https://platform.sarvam.ai/) — sign up, get `SARVAM_API_KEY` (free tier)
- [Sarvam Docs](https://docs.sarvam.ai/) — API reference and the `sarvamai` Python SDK
- [Speech-to-Text (`saarika`)](https://docs.sarvam.ai/api-reference/speech-to-text/transcribe) — `POST https://api.sarvam.ai/speech-to-text`, header `api-subscription-key`, returns `transcript`
- [Text-to-Speech (`bulbul`)](https://docs.sarvam.ai/api-reference/text-to-speech/convert) — `POST https://api.sarvam.ai/text-to-speech`, returns `audios` (base64 WAV)

### Groq (the brain)
- [Groq Console](https://console.groq.com/) — sign up, get `GROQ_API_KEY` (free tier)
- [Groq Models](https://console.groq.com/docs/models) — production chat models: `llama-3.1-8b-instant` (fastest), `llama-3.3-70b-versatile`, `openai/gpt-oss-120b`
- [Groq OpenAI compatibility](https://console.groq.com/docs/openai) — drop-in with the OpenAI SDK at `https://api.groq.com/openai/v1`
- [Groq + LiveKit voice guide](https://console.groq.com/docs/livekit) — if you later move to a real-time WebRTC stack

---

## Carrying the Testing Mindset Forward (from earlier modules)

- Module 4 `examples/04_testing_mindset.ipynb` — equivalence partitioning, boundary values, coverage matrix, hard negatives. Day 2 applies all four to **audio** conditions (accent × noise × speaking rate × code-switch).
- Module 4 Day 5 — `LatencyMetric`: latency as a first-class test. In voice it becomes *the* metric (`VoiceTurn.timings_ms`).
- Module 8 — Promptfoo. The **brain** of the voice agent is tested exactly as there (relevancy, safety, injection) — on the transcript text.

---

## Voice-Specific Testing Concepts

- [Word Error Rate (WER) — overview](https://en.wikipedia.org/wiki/Word_error_rate) — the standard STT accuracy metric used on Day 2
- [`jiwer`](https://github.com/jitsi/jiwer) — the Python library that computes WER/CER (in `requirements.txt`)
- [Deepgram — Measuring STT accuracy with WER](https://developers.deepgram.com/docs/measuring-speech-to-text-accuracy) — practical guidance on WER, normalization, and its pitfalls
- [LiveKit Agents — testing & evaluations](https://docs.livekit.io/agents/build/testing/) — how a production real-time voice framework structures agent tests (LLM-as-judge, tool-call and behavior assertions); good background for turn-taking / interruption testing beyond our file-based agent

---

## Why Latency Dominates Voice

- [Groq — why inference speed matters for voice](https://console.groq.com/docs/livekit) — the streaming/low-latency argument for a fast LLM brain
- Rule of thumb: aim for **sub-second** time-to-first-audio; a full turn much over ~1.5–2s feels laggy. Day 2's budgets assert against this.

---

## Going Further (beyond this module)

- [LiveKit Agents](https://docs.livekit.io/agents/) — a real-time WebRTC voice framework with built-in VAD, endpointing, and interruption handling; the natural next step from our file-based agent, and it has Groq and Sarvam plugins
- [Sarvam WebSocket streaming TTS/STT](https://docs.sarvam.ai/) — streaming variants that cut latency vs. the request/response calls used in Day 1
