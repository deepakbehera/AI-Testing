# test_deepeval_day1.py
# Written by the notebook — run with: pytest test_deepeval_day1.py -v

import os
from dotenv import load_dotenv
from openai import OpenAI
from deepeval import assert_test
from deepeval.test_case import LLMTestCase
from deepeval.metrics import AnswerRelevancyMetric

# ---------- Setup ----------
load_dotenv()

PROVIDER = os.getenv("PROVIDER", "ollama").lower()

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


def call_llm(prompt: str) -> str:
    """Helper: send a prompt to the configured LLM and return the text."""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content


# ---------- Tests ----------
def test_password_reset_is_relevant():
    """The bot's password-reset answer should be relevant to the question."""
    user_question = "How do I reset my password?"
    bot_answer = call_llm(user_question)
    case = LLMTestCase(
        input=user_question,
        actual_output=bot_answer,
    )
    assert_test(case, [AnswerRelevancyMetric(threshold=0.7)])


def test_capital_city_is_relevant():
    """A geography question should get a geographically relevant answer."""
    user_question = "What is the capital city of Japan?"
    bot_answer    = call_llm(user_question)
    case = LLMTestCase(
        input=user_question,
        actual_output=bot_answer,
    )
    assert_test(case, [AnswerRelevancyMetric(threshold=0.7)])
