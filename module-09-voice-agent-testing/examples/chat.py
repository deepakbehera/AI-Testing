#!/usr/bin/env python3
# chat.py — a conversational voice chatbot in your terminal.
#
# By default you TYPE each turn and the bot REPLIES IN TEXT + SPEAKS it aloud,
# keeping the whole conversation in context. With --mic you SPEAK each turn.
#
#   python chat.py            # typed turns, spoken replies (works everywhere)
#   python chat.py --mic      # spoken turns (needs: pip install sounddevice soundfile)
#   python chat.py --no-audio # don't play the reply audio, just print text
#
# Needs examples/.env with SARVAM_API_KEY + GROQ_API_KEY (see .env.example).
# Type 'quit' / 'exit' (or Ctrl-C) to leave.

import argparse
import os
import platform
import subprocess
import sys
from pathlib import Path

from voice_agent import VoiceChat


def play_audio(path: str) -> None:
    """Best-effort cross-platform playback; degrades to just noting the file."""
    system = platform.system()
    try:
        if system == "Darwin":
            subprocess.run(["afplay", path], check=False)
        elif system == "Linux":
            subprocess.run(["aplay", "-q", path], check=False)
        elif system == "Windows":
            os.startfile(path)  # type: ignore[attr-defined]
        else:
            print(f"   (reply audio saved to {path})")
    except Exception:
        print(f"   (reply audio saved to {path})")


def record_mic(seconds: int, out_path: str, samplerate: int = 16000) -> str:
    """Record one utterance from the default mic to a .wav (needs sounddevice+soundfile)."""
    import sounddevice as sd
    import soundfile as sf

    print(f"🎙️  Recording {seconds}s — speak now...")
    audio = sd.rec(int(seconds * samplerate), samplerate=samplerate, channels=1)
    sd.wait()
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    sf.write(out_path, audio, samplerate)
    return out_path


def main() -> None:
    ap = argparse.ArgumentParser(description="Conversational voice chatbot (Sarvam + Groq).")
    ap.add_argument("--mic", action="store_true", help="speak your turns instead of typing")
    ap.add_argument("--seconds", type=int, default=5, help="mic recording length per turn")
    ap.add_argument("--no-audio", action="store_true", help="don't play reply audio")
    args = ap.parse_args()

    Path("audio").mkdir(exist_ok=True)

    try:
        chat = VoiceChat()
    except RuntimeError as e:
        print(f"Setup error: {e}")
        sys.exit(1)

    mode = "🎙️ mic" if args.mic else "⌨️  text"
    print(f"Voice chatbot ready ({mode} mode). Type 'quit' to exit.\n")

    while True:
        try:
            if args.mic:
                cmd = input("Press Enter to speak (or type 'quit'): ").strip().lower()
                if cmd in {"quit", "exit"}:
                    break
                wav = record_mic(args.seconds, "audio/you.wav")
                turn = chat.ask(wav)
                print(f"you (heard)> {turn.transcript}")
            else:
                user = input("you> ").strip()
                if user.lower() in {"quit", "exit"}:
                    break
                if not user:
                    continue
                turn = chat.say(user)

            print(f"bot> {turn.reply_text}   ({turn.timings_ms['total']} ms)")
            if not args.no_audio:
                play_audio(turn.audio_out_path)
            print()

        except (KeyboardInterrupt, EOFError):
            break
        except Exception as e:  # keep the conversation alive on a transient API error
            print(f"   [turn failed: {type(e).__name__}: {e}]\n")

    print("\nbye 👋")


if __name__ == "__main__":
    main()
