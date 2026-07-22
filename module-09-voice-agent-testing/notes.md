# Module 9 — Voice Agent Testing

**Duration:** 2 hours · split across **2 online sessions of 1 hour each**
**Prerequisites:** Module 4 (DeepEval, the testing mindset — Day 4 & the `LatencyMetric` — Day 5) · Module 7 (agents) · Module 8 (Promptfoo, adversarial testing)

This is the course finale, and it reuses everything. A voice agent is the text brain you have tested for eight modules, wrapped in **ears** (speech-to-text) and a **mouth** (text-to-speech). The brain testing does not change — you already own it. What's new is the two organs around it, and the one property that dominates voice and barely mattered in text: **latency**.

- **Day 1** — understand and *build* a local voice agent (Sarvam STT + Groq LLM + Sarvam TTS), and get introduced to the voice-specific failure modes you now have to test.
- **Day 2** — *implement* those tests: STT accuracy (WER), the TTS→STT round-trip, latency budgets, and hard-negative fallback cases — plus reusing Promptfoo/DeepEval on the brain.

---

## How the 2 sessions are organized

| Day | Focus | What you'll do |
|---|---|---|
| **1** | Build a local voice agent + meet voice testing | STT → LLM → TTS pipeline with per-stage latency; the checklist of what's new to test |
| **2** | Test it with an LLM judge (DeepEval `GEval`) | Grade reply quality, STT fidelity, and TTS intelligibility; plus a latency check |

---

## DAY 1 — Build a Local Voice Agent (60 min)

### Learning objectives
- Explain the STT → LLM → TTS pipeline and why **streaming + latency** define the experience
- Build a local, file-in/file-out voice agent with **Sarvam** (ears + mouth) and **Groq** (brain)
- See that the **brain** is tested exactly as in Modules 4–8, and identify what is *genuinely new* to test
- Leave with the voice-testing coverage checklist that Day 2 implements

### The pipeline

```
🎙️ audio in → [ STT ] → transcript → [ LLM ] → reply text → [ TTS ] → 🔊 audio out
                ears                    brain                  mouth
              (Sarvam saarika)        (Groq, streamed)      (Sarvam bulbul)
```

Two properties separate this from every system tested so far:

1. **Three failure surfaces.** The ears can mishear, the brain can answer wrong, the mouth can mispronounce — and they compound. A flawless brain still fails if the ears turned "Manali" into "monolli."
2. **Latency is a feature.** A 3-second pause is fine in chat and feels *broken* in conversation. This is why the brain must **stream** (Groq is chosen for speed) and why the agent times every stage. Module 4 Day 5 made latency a metric; here it is *the* metric.

> **Plain English:** you've been grading the chef. A voice agent also has a waiter taking the order by ear in a noisy room and another reading the dish back aloud — any of the three can ruin the meal, and if any is slow, the diner leaves.

### The stack: Sarvam + Groq

- **Sarvam** ([playground](https://platform.sarvam.ai/api-playground/)) — the ears and mouth. `saarika` STT and `bulbul` TTS, both strong on Indian languages, accents, and Hindi-English **code-switching** (the conditions generic STT fails on). Official SDK: `pip install sarvamai`.
- **Groq** — the brain, over an OpenAI-compatible API that is fast and streaming. Default `llama-3.1-8b-instant`. Speed is *why* it's here.

Both free-tier friendly — the same "runnable by everyone" bar as Ollama in Module 8. Keys go in `examples/.env`.

### The agent (`examples/voice_agent.py`)

A `VoiceAgent` with three timed stages and a `respond()` that chains them:

```python
turn = VoiceAgent().respond("audio/question.wav", out_path="audio/reply.wav")
# VoiceTurn(transcript=..., reply_text=..., audio_out_path=..., timings_ms={stt, llm, tts, total})
```

Two design choices are already **testing decisions**:

1. **File-in / file-out.** Audio → a structured `VoiceTurn` where every stage returns a value you can assert on. (A live WebRTC stack would be harder to test; we deliberately keep it deterministic — the same "build it plainly so you can test it" instinct from Modules 5–6.)
2. **The system prompt forces *speakable* replies** — 1–3 short sentences, no markdown/bullets/emojis. A brain that returns a bulleted list is correct *text* and a broken *voice* reply. That's a voice-specific requirement, and a Day 2 test.

`make_audio()` synthesizes a question via TTS so you can run the agent **without a microphone** — and that same trick is the seed of Day 2's **TTS→STT round-trip** test.

### Introducing voice-specific testing

The split is honest: **the brain is tested exactly as before** (Promptfoo from Module 8, DeepEval from Modules 4/7) — relevancy, safety, tool correctness, injection resistance, all on the transcript text. What's **new** is everything around it:

| Stage | New failure mode | How Day 2 tests it | Mindset callback |
|---|---|---|---|
| **STT (ears)** | Mishears — accents, code-switch, noise, numbers, names | Audio fixtures + reference → **WER/CER**; partition by accent/noise | Equivalence partitions over *audio* (M4 D4) |
| **LLM (brain)** | Wrong / unsafe / **un-speakable** reply (markdown, walls of text) | Reuse Promptfoo/DeepEval on the transcript; add a "speakable" check | Modules 4, 7, 8 |
| **TTS (mouth)** | Mispronounces names/numbers, wrong language, unintelligible | **TTS→STT round-trip**: speak it, transcribe it, compare | new dimension, same mindset |
| **End-to-end** | Too slow — the conversation-killer | Assert **latency budgets** on `timings_ms` (first-token, total) | M4 D5 `LatencyMetric`; Promptfoo `latency` |
| **Turn-taking / interruption** | Cuts the user off; won't stop when interrupted | Scripted timing tests (for real-time agents) | boundary values |
| **Fallback paths** | Silence, gibberish, STT failure, out-of-scope | **Hard negatives**: feed each, assert graceful reprompt | M6 graceful failure |

The Day-1 agent hands Day 2 two things for free: **`timings_ms`** (→ latency assertions) and **`make_audio()`** (→ the round-trip test and accented test-clip generation).

### Demo you'll run
**`examples/01_build_voice_agent.ipynb`** — build the agent, run a full spoken turn (no mic), listen to both ends, and walk the voice-testing checklist.

### Key takeaways
1. A voice agent is **STT → LLM → TTS**: three failure surfaces, and **latency dominates**.
2. Choosing Groq (fast, streaming) + Sarvam (accent-robust) + a *speakable* system prompt are all decisions you will later **test**.
3. The **brain** is tested with your existing tools; STT accuracy, TTS intelligibility, latency, turn-taking, and fallbacks are the **new** surface.
4. Building the agent **file-in/file-out with per-stage timings** is what makes Day 2's tests possible — the same "build to be tested" discipline as the whole course.

---

## DAY 2 — Testing the Voice Agent with an LLM Judge (60 min)

Day 1 introduced *what* to test; Day 2 **runs** it. The scope is **LLM-as-a-judge** — DeepEval `GEval`, the same tool from Modules 4, 7 & 8 — because speech is noisy and replies are open-ended, so we grade **meaning, not exact strings**. One judging method, three stages.

### Learning objectives
- Point DeepEval `GEval` at a **Groq** judge via `LocalModel` (self-contained — no new provider)
- Grade all three stages with plain-English criteria: reply quality, STT fidelity, TTS intelligibility
- Keep latency as a plain numeric check (no judge needed)

### The judge
A `GEval` metric backed by `LocalModel(model="llama-3.3-70b-versatile", base_url=Groq)` — a **stronger, different** model than the agent's brain (`llama-3.1-8b-instant`), so it isn't grading its own homework.

### The three tests (`examples/02_testing_voice_agent.ipynb`)

| Stage | Metric | What the judge is asked |
|---|---|---|
| **LLM (brain)** | Reply quality | Is the reply relevant, safe, and *speakable* (1–3 sentences, no markdown)? |
| **STT (ears)** | Transcription fidelity | Does the transcript preserve the meaning of the known reference? (a changed place/number fails — catches Day 1's "Manali → Lanali") |
| **TTS (mouth)** | Intelligibility (round-trip) | Speak a line, transcribe it back: did the meaning (number, city) survive? |

Each `GEval` is just a **criteria** string + which fields the judge sees (`INPUT`, `ACTUAL_OUTPUT`, `EXPECTED_OUTPUT`) — identical to Modules 4/8, now on audio. Latency stays a plain `timings_ms` budget check.

### Going deeper (optional)
Add more turns (accents, code-switching, numbers) and reuse the same metrics; add **WER** with `jiwer` alongside STT fidelity for hard cases; tighten the latency budget. That's the full **pipeline stage × failure mode** coverage — the Module 4 Day 4 artifact, one last time, for voice.

### Demo you'll run
**`examples/02_testing_voice_agent.ipynb`** — configure the Groq judge, run one turn, grade all three stages, check latency.

---

## Plain-English Glossary

| Term | What it means |
|---|---|
| Voice agent | An STT → LLM → TTS pipeline: hear speech, think, speak back |
| STT (ASR) | Speech-to-text — the "ears" (Sarvam `saarika`) |
| TTS | Text-to-speech — the "mouth" (Sarvam `bulbul`) |
| Brain / LLM | The model that decides what to say (Groq, streamed) |
| Streaming | Emitting the reply token-by-token so speech can start before thinking finishes |
| Time-to-first-token (TTFT) | How long the user waits in silence before the reply begins — a key voice latency metric |
| WER / CER | Word / character error rate — how wrong a transcript is vs. a reference |
| TTS→STT round-trip | Speak text, transcribe it back, compare — an automatic TTS intelligibility check |
| Code-switching | Mixing languages in one utterance (e.g. Hindi + English) — a hard STT case |
| Endpointing / turn-taking | Deciding when the user has finished speaking |
| Barge-in / interruption | The user talking over the agent; the agent should stop and listen |
| Speakable reply | A reply that sounds natural aloud — short, no markdown/lists/symbols |
| Fallback | Graceful handling of silence, gibberish, or out-of-scope input |
