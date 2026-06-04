import pytest
import os
from dotenv import load_dotenv
load_dotenv()

creation_count = {"function": 0, "session": 0}

@pytest.fixture(scope="function")
def function_config():
    """Rebuilt before every test."""
    creation_count["function"] += 1
    print(f"\n  [function fixture #{creation_count['function']} created]")
    return {"temperature": 0.3, "max_tokens": 500}

@pytest.fixture(scope="session")
def llm_client():
    """
    Built ONCE for the entire test session.
    Perfect for the OpenAI/Ollama client — cheap to reuse, expensive to rebuild.
    """
    from openai import OpenAI
    creation_count["session"] += 1
    print(f"\n  [session fixture #{ creation_count['session']} created]")
    provider = os.getenv("PROVIDER", "ollama")
    if provider == "openai":
        return OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    return OpenAI(base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1"), api_key="ollama")


# These three tests all use llm_client — but it's only created ONCE
def test_client_exists(llm_client, function_config):
    assert llm_client is not None
    assert function_config["temperature"] == 0.3

def test_config_has_max_tokens(llm_client, function_config):
    assert function_config["max_tokens"] > 0

def test_config_temperature_range(function_config):
    assert 0.0 <= function_config["temperature"] <= 2.0
