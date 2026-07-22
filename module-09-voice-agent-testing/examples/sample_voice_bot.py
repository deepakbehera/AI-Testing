import os
import tempfile
import dotenv
import numpy as np
import sounddevice as sd
import soundfile as sf

from groq import Groq
from sarvamai import SarvamAI

# =====================================================
# Load Environment Variables
# =====================================================
dotenv.load_dotenv()

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# =====================================================
# Initialize Clients
# =====================================================
sarvam = SarvamAI(
    api_subscription_key=SARVAM_API_KEY,
)

groq = Groq(
    api_key=GROQ_API_KEY,
)

SAMPLE_RATE = 16000

# =====================================================
# Speech to Text
# =====================================================
def stt(
    sample_rate: int = SAMPLE_RATE,
    output_file: str = "recording.wav",
    model: str = "saaras:v3",
):
    """
    Record microphone input until ENTER is pressed again
    and return the transcribed text.
    """

    print("\nPress ENTER to start recording...")
    input()

    recording = []

    def callback(indata, frames, time, status):
        if status:
            print(status)
        recording.append(indata.copy())

    stream = sd.InputStream(
        samplerate=sample_rate,
        channels=1,
        dtype="int16",
        callback=callback,
    )

    stream.start()

    print("🎤 Recording... Press ENTER to stop.")
    input()

    stream.stop()
    stream.close()

    if len(recording) == 0:
        return ""

    audio = np.concatenate(recording, axis=0)

    sf.write(output_file, audio, sample_rate)

    with open(output_file, "rb") as f:
        response = sarvam.speech_to_text.transcribe(
            file=f,
            model=model,
            mode="transcribe",
        )

    # Depending on SDK version, this may be transcript/text
    return response.transcript


# =====================================================
# LLM
# =====================================================
def chat(messages):
    """
    Sends conversation to Groq and returns assistant reply.
    """

    response = groq.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        temperature=0.7,
    )

    return response.choices[0].message.content


# =====================================================
# Text To Speech
# =====================================================
def tts(text):
    """
    Convert text to speech using Sarvam and play it.
    """

    response = sarvam.text_to_speech.convert(
        model="bulbul:v3",
        text=text,
        target_language_code="en-IN",
        speaker="amit",
    )

    # If your SDK exposes a different field, print(response)
    # once and update the line below.
    audio_bytes = response.audios[0]

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        f.write(audio_bytes)
        temp_audio = f.name

    audio, sample_rate = sf.read(temp_audio, dtype="float32")

    sd.play(audio, sample_rate)
    sd.wait()

    os.remove(temp_audio)


# =====================================================
# Main
# =====================================================
def main():

    print("=" * 60)
    print("🎙️ Voice Chatbot")
    print("Press ENTER to record.")
    print("Say 'exit', 'quit', or 'bye' to stop.")
    print("=" * 60)

    messages = [
        {
            "role": "system",
            "content": (
                "You are a friendly AI assistant. "
                "Keep responses concise (2-3 sentences)."
            ),
        }
    ]

    while True:

        try:
            user_text = stt()

            if not user_text:
                continue

            print(f"\n🧑 You: {user_text}")

            if user_text.lower().strip() in ["exit", "quit", "bye"]:
                print("👋 Goodbye!")
                break

            messages.append(
                {
                    "role": "user",
                    "content": user_text,
                }
            )

            assistant_text = chat(messages)

            messages.append(
                {
                    "role": "assistant",
                    "content": assistant_text,
                }
            )

            print(f"\n🤖 Assistant: {assistant_text}")

            # Speak response
            tts(assistant_text)

        except KeyboardInterrupt:
            print("\nExiting...")
            break

        except Exception as e:
            print("\nError:", e)


if __name__ == "__main__":
    main()