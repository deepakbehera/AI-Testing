from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

PROVIDER = os.getenv("PROVIDER", "azure").lower()

if PROVIDER == "azure":
    client = OpenAI(
        base_url=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_KEY"),
    )
    MODEL = os.getenv("AZURE_OPENAI_DEPLOYMENT", "DeepSeek-V3.2")
elif PROVIDER == "openai":
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
else:  # ollama
    client = OpenAI(
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1"),
        api_key="ollama",
    )
    MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")

print(f"Provider : {PROVIDER}")
print(f"Model    : {MODEL}")

completion = client.chat.completions.create(
    model=MODEL,
    messages=[
        {
            "role": "user",
            "content": "What is the capital of France?",
        }
    ],
)

print(completion.choices[0].message.content)
