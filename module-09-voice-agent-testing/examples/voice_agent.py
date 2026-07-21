# voice_agent.py
# A small, LOCAL voice agent: audio in -> text out -> audio out.
#
#   microphone / .wav  ──►  Sarvam STT  ──►  Groq LLM (the "brain")  ──►  Sarvam TTS  ──►  .wav
#
# It is deliberately file-in / file-out (not a live WebRTC stack) so it is easy
# to run, easy to reason about, and — the point of this course — easy to TEST:
# every stage returns a value you can assert on, and every stage is timed.
#
# Providers (both have generous free tiers):
#   * Sarvam  — STT (saarika) + TTS (bulbul).  Strong on Indian languages / accents.
#               Official Python SDK: `pip install sarvamai`.  Playground + valid
#               speaker/model names: https://platform.sarvam.ai/api-playground/
#   * Groq    — the LLM, via its OpenAI-compatible API. Very fast + streaming,
#               which is what makes a voice agent feel responsive.
#
# Nothing here needs LiveKit or a cloud room. Keys come from examples/.env:
#   SARVAM_API_KEY, GROQ_API_KEY  (+ optional model/speaker/language overrides).

from __future__ import annotations

import base64
import os
import time
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

# Load .env from THIS file's directory (so it works no matter where you run from).
load_dotenv(Path(__file__).resolve().parent / ".env")

# ── Config (all overridable via .env) ───────────────────────────────────────────
SARVAM_API_KEY = os.getenv("SARVAM_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

STT_MODEL = os.getenv("SARVAM_STT_MODEL", "saarika:v2.5")   # Sarvam speech-to-text
TTS_MODEL = os.getenv("SARVAM_TTS_MODEL", "bulbul:v2")      # Sarvam text-to-speech
TTS_SPEAKER = os.getenv("SARVAM_TTS_SPEAKER", "anushka")    # valid speakers depend on TTS_MODEL
LANGUAGE = os.getenv("VOICE_LANGUAGE", "en-IN")            # BCP-47, e.g. en-IN, hi-IN
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")  # fast Groq chat model

# Voice agents must talk like a person, not print a document. This system prompt
# is itself a voice-specific design choice (short, no markdown, speakable).
DEFAULT_SYSTEM_PROMPT = (
    "You are a friendly voice assistant. Reply in 1-3 short, conversational "
    "sentences that are easy to say out loud. Do not use markdown, bullet points, "
    "code, emojis, or symbols — only plain spoken words. If you don't know, say so."
)


@dataclass
class VoiceTurn:
    """Everything one turn produced — each field is something a test can assert on."""
    transcript: str            # what Sarvam STT heard
    reply_text: str            # what the Groq LLM said (text)
    audio_out_path: str        # where the TTS .wav was written
    timings_ms: dict = field(default_factory=dict)  # per-stage latency: stt / llm / tts / total
    detected_language: str = ""  # language Sarvam reported for the input


class VoiceAgent:
    """Sarvam STT -> Groq LLM -> Sarvam TTS, with per-stage timing."""

    def __init__(self, system_prompt: str = DEFAULT_SYSTEM_PROMPT):
        if not SARVAM_API_KEY:
            raise RuntimeError("SARVAM_API_KEY is not set (see examples/.env.example).")
        if not GROQ_API_KEY:
            raise RuntimeError("GROQ_API_KEY is not set (see examples/.env.example).")

        # Imported here (not at module top) so the file can be imported for reading
        # even before `pip install sarvamai groq-compatible openai` has run.
        from openai import OpenAI
        from sarvamai import SarvamAI

        self.system_prompt = system_prompt
        self.sarvam = SarvamAI(api_subscription_key=SARVAM_API_KEY)
        self.groq = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=GROQ_API_KEY)

    # ── Stage 1: ears ───────────────────────────────────────────────────────────
    def transcribe(self, audio_path: str) -> tuple[str, str, float]:
        """Audio file -> (transcript, detected_language, elapsed_ms) via Sarvam STT."""
        start = time.perf_counter()
        with open(audio_path, "rb") as f:
            resp = self.sarvam.speech_to_text.transcribe(
                file=f,
                model=STT_MODEL,
                language_code=LANGUAGE,
            )
        elapsed_ms = (time.perf_counter() - start) * 1000
        transcript = getattr(resp, "transcript", "") or ""
        detected = getattr(resp, "language_code", "") or ""
        return transcript.strip(), detected, elapsed_ms

    # ── Stage 2: brain ───────────────────────────────────────────────────────────
    def think(self, user_text: str, history: list[dict] | None = None) -> tuple[str, float, float]:
        """User text -> (reply_text, time_to_first_token_ms, total_ms) via Groq (streamed).

        Time-to-first-token matters for voice: it's how long the user waits in
        silence before the agent starts forming a reply.
        """
        messages = [{"role": "system", "content": self.system_prompt}]
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": user_text})

        start = time.perf_counter()
        ttft_ms = 0.0
        chunks: list[str] = []
        stream = self.groq.chat.completions.create(
            model=GROQ_MODEL, messages=messages, temperature=0.3, max_tokens=200, stream=True,
        )
        for event in stream:
            delta = event.choices[0].delta.content
            if delta:
                if not chunks:  # first token seen
                    ttft_ms = (time.perf_counter() - start) * 1000
                chunks.append(delta)
        total_ms = (time.perf_counter() - start) * 1000
        return "".join(chunks).strip(), ttft_ms, total_ms

    # ── Stage 3: mouth ───────────────────────────────────────────────────────────
    def speak(self, text: str, out_path: str) -> tuple[str, float]:
        """Text -> (out_path, elapsed_ms). Writes a .wav via Sarvam TTS."""
        start = time.perf_counter()
        resp = self.sarvam.text_to_speech.convert(
            text=text,
            target_language_code=LANGUAGE,
            model=TTS_MODEL,
            speaker=TTS_SPEAKER,
        )
        elapsed_ms = (time.perf_counter() - start) * 1000
        # Sarvam returns `audios`: a list of base64-encoded WAV strings (one per input chunk).
        audio_b64 = resp.audios[0]
        Path(out_path).write_bytes(base64.b64decode(audio_b64))
        return out_path, elapsed_ms

    # ── The whole turn ────────────────────────────────────────────────────────────
    def respond(self, audio_path: str, out_path: str = "reply.wav",
                history: list[dict] | None = None) -> VoiceTurn:
        """Full pipeline: audio question in -> spoken answer out, everything timed."""
        transcript, detected, stt_ms = self.transcribe(audio_path)
        reply_text, ttft_ms, llm_ms = self.think(transcript, history=history)
        audio_out, tts_ms = self.speak(reply_text, out_path)
        return VoiceTurn(
            transcript=transcript,
            reply_text=reply_text,
            audio_out_path=audio_out,
            detected_language=detected,
            timings_ms={
                "stt": round(stt_ms),
                "llm": round(llm_ms),
                "llm_first_token": round(ttft_ms),
                "tts": round(tts_ms),
                "total": round(stt_ms + llm_ms + tts_ms),
            },
        )

    # ── Convenience: make a test clip WITHOUT recording a mic ─────────────────────
    def make_audio(self, text: str, out_path: str) -> str:
        """TTS a line of text to a .wav — handy for creating input clips to feed the
        agent (and the seed of Day 2's TTS->STT round-trip test)."""
        path, _ = self.speak(text, out_path)
        return path


class VoiceChat:
    """A multi-turn conversation on top of VoiceAgent — it remembers history.

    Two ways to take a turn:
      * say(text)        — you TYPE the turn (skips STT); reply is spoken.
      * ask(audio_path)  — you SPEAK the turn (full STT -> LLM -> TTS).

    Both append (user, assistant) to `history`, so the brain has context on the
    next turn — which is exactly what Day 2's "does it remember?" test checks.
    """

    def __init__(self, agent: VoiceAgent | None = None, system_prompt: str = DEFAULT_SYSTEM_PROMPT):
        self.agent = agent or VoiceAgent(system_prompt=system_prompt)
        self.history: list[dict] = []
        self._turn = 0

    def _next_out(self) -> str:
        self._turn += 1
        Path("audio").mkdir(exist_ok=True)
        return f"audio/reply_{self._turn:02d}.wav"

    def say(self, user_text: str, out_path: str | None = None) -> VoiceTurn:
        """Typed turn: text in -> spoken reply out (no STT)."""
        reply_text, ttft_ms, llm_ms = self.agent.think(user_text, history=self.history)
        audio_out, tts_ms = self.agent.speak(reply_text, out_path or self._next_out())
        self.history += [
            {"role": "user", "content": user_text},
            {"role": "assistant", "content": reply_text},
        ]
        return VoiceTurn(
            transcript=user_text, reply_text=reply_text, audio_out_path=audio_out,
            timings_ms={"llm": round(llm_ms), "llm_first_token": round(ttft_ms),
                        "tts": round(tts_ms), "total": round(llm_ms + tts_ms)},
        )

    def ask(self, audio_path: str, out_path: str | None = None) -> VoiceTurn:
        """Spoken turn: audio in -> spoken reply out (full pipeline, with history)."""
        transcript, detected, stt_ms = self.agent.transcribe(audio_path)
        reply_text, ttft_ms, llm_ms = self.agent.think(transcript, history=self.history)
        audio_out, tts_ms = self.agent.speak(reply_text, out_path or self._next_out())
        self.history += [
            {"role": "user", "content": transcript},
            {"role": "assistant", "content": reply_text},
        ]
        return VoiceTurn(
            transcript=transcript, reply_text=reply_text, audio_out_path=audio_out,
            detected_language=detected,
            timings_ms={"stt": round(stt_ms), "llm": round(llm_ms),
                        "llm_first_token": round(ttft_ms), "tts": round(tts_ms),
                        "total": round(stt_ms + llm_ms + tts_ms)},
        )

    def reset(self) -> None:
        self.history = []
        self._turn = 0


if __name__ == "__main__":
    # Tiny smoke test: a short spoken CONVERSATION (two turns, with memory).
    chat = VoiceChat()
    for line in ["What should I pack for a trip to Manali in December?",
                 "And is it cold enough there for snow?"]:
        turn = chat.say(line)
        print(f"you> {line}")
        print(f"bot> {turn.reply_text}   ({turn.timings_ms['total']} ms)  🔊 {turn.audio_out_path}\n")
