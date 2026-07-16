# agent.py
# A simple, REAL agent for module 7's live-agent notebook cells — same
# PROVIDER switch and .env convention as ../examples/agent_tools.py, but its
# tools make real HTTP calls instead of hitting an in-memory dict or an MCP
# server: open-meteo.com's free weather API (no API key required).
#
# Deliberately no MCP/subprocess involved (unlike the earlier repo_agent
# attempt) — just plain async HTTP calls from Python, which sidesteps the
# anyio/subprocess event-loop issues that showed up running an MCP stdio
# client repeatedly inside a Jupyter kernel's top-level await.
#
# Exposes the same shape as agent_tools.py (AgentResponse, ToolCallRecord,
# run_agent, to_deepeval_tool_calls) so the Day 1/2 notebooks can swap their
# import source with minimal changes.

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import httpx
import tenacity
from dotenv import load_dotenv
from openai import AsyncOpenAI, RateLimitError

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

# WMO weather interpretation codes -> short human-readable description.
WEATHER_CODES = {
    0: "clear sky", 1: "mainly clear", 2: "partly cloudy", 3: "overcast",
    45: "fog", 48: "depositing rime fog",
    51: "light drizzle", 53: "moderate drizzle", 55: "dense drizzle",
    61: "slight rain", 63: "moderate rain", 65: "heavy rain",
    71: "slight snow", 73: "moderate snow", 75: "heavy snow",
    80: "slight rain showers", 81: "moderate rain showers", 82: "violent rain showers",
    95: "thunderstorm", 96: "thunderstorm with slight hail", 99: "thunderstorm with heavy hail",
}

PROVIDER = os.getenv("PROVIDER", "azure").lower()

if PROVIDER == "azure":
    _client = AsyncOpenAI(
        base_url=os.getenv("AZURE_OPENAI_ENDPOINT_C"),
        api_key=os.getenv("AZURE_OPENAI_KEY"),
    )
    _llm_model = os.getenv("AZURE_OPENAI_DEPLOYMENT", "DeepSeek-V3.2")
elif PROVIDER == "openai":
    _client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    _llm_model = os.getenv("DEMO_MODEL", "gpt-4o-mini")
else:  # ollama
    _client = AsyncOpenAI(base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1"), api_key="ollama")
    _llm_model = os.getenv("DEMO_MODEL", "llama3.2:3b")

SYSTEM_PROMPT = """You are a weather assistant. You can answer questions about current weather
conditions and short-term forecasts for real places, using live data from a weather API.

Always call the appropriate tool to check live conditions before answering a weather question —
never guess at temperature, wind, or conditions from memory, since weather changes constantly and
your training data is not current. If a city name is ambiguous, pick the most populous match.
"""

# The shared Azure deployment has a request-rate limit; back off and retry on 429s.
_retry_on_rate_limit = tenacity.retry(
    retry=tenacity.retry_if_exception_type(RateLimitError),
    wait=tenacity.wait_exponential(multiplier=2, min=5, max=60),
    stop=tenacity.stop_after_attempt(8),
    reraise=True,
)


@_retry_on_rate_limit
async def _create_completion(**kwargs):
    return await _client.chat.completions.create(**kwargs)


@dataclass
class ToolCallRecord:
    """Records one tool invocation: what was called, with what, and what came back."""
    name: str
    input_parameters: dict
    output: str  # JSON-serialized tool result


@dataclass
class AgentResponse:
    """The agent's complete response after one interaction turn."""
    output: str
    tools_called: list[ToolCallRecord] = field(default_factory=list)


# ---------------------------------------------------------------------------
#  Real tool implementations — live HTTP calls to open-meteo.com, no API key.
# ---------------------------------------------------------------------------

async def _geocode(http: httpx.AsyncClient, city: str) -> dict:
    resp = await http.get(GEOCODING_URL, params={"name": city, "count": 1})
    resp.raise_for_status()
    results = resp.json().get("results")
    if not results:
        return {"error": f"Could not find a location matching {city!r}."}
    place = results[0]
    return {
        "name": place["name"],
        "country": place.get("country"),
        "latitude": place["latitude"],
        "longitude": place["longitude"],
    }


async def get_current_weather(http: httpx.AsyncClient, city: str) -> dict:
    """Look up live current weather conditions for a city."""
    place = await _geocode(http, city)
    if "error" in place:
        return place

    resp = await http.get(
        FORECAST_URL,
        params={"latitude": place["latitude"], "longitude": place["longitude"], "current_weather": "true"},
    )
    resp.raise_for_status()
    current = resp.json().get("current_weather", {})
    code = current.get("weathercode")
    return {
        "city": place["name"],
        "country": place["country"],
        "temperature_c": current.get("temperature"),
        "windspeed_kmh": current.get("windspeed"),
        "conditions": WEATHER_CODES.get(code, f"code {code}"),
        "observed_at": current.get("time"),
    }


async def get_forecast(http: httpx.AsyncClient, city: str, days: int = 3) -> dict:
    """Look up a live multi-day forecast (max/min temp, conditions) for a city."""
    place = await _geocode(http, city)
    if "error" in place:
        return place

    days = max(1, min(days, 7))
    resp = await http.get(
        FORECAST_URL,
        params={
            "latitude": place["latitude"],
            "longitude": place["longitude"],
            "daily": "weathercode,temperature_2m_max,temperature_2m_min",
            "forecast_days": days,
            "timezone": "auto",
        },
    )
    resp.raise_for_status()
    daily = resp.json().get("daily", {})
    forecast = [
        {
            "date": date,
            "temp_max_c": daily["temperature_2m_max"][i],
            "temp_min_c": daily["temperature_2m_min"][i],
            "conditions": WEATHER_CODES.get(daily["weathercode"][i], f"code {daily['weathercode'][i]}"),
        }
        for i, date in enumerate(daily.get("time", []))
    ]
    return {"city": place["name"], "country": place["country"], "forecast": forecast}


TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get live current weather conditions (temperature, wind, conditions) for a named city.",
            "parameters": {
                "type": "object",
                "properties": {"city": {"type": "string", "description": "City name, e.g. 'Tokyo'."}},
                "required": ["city"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_forecast",
            "description": "Get a live multi-day weather forecast (daily high/low temp, conditions) for a named city.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "City name, e.g. 'Paris'."},
                    "days": {"type": "integer", "description": "Number of days to forecast (1-7). Default 3."},
                },
                "required": ["city"],
            },
        },
    },
]


async def run_agent(user_message: str, verbose: bool = False) -> AgentResponse:
    """Run the weather agent for one user message against the real open-meteo.com API.

    Mirrors agent_tools.run_agent's signature/return shape so notebook cells built
    around that interface need only swap the import.
    """
    tool_fns = {"get_current_weather": get_current_weather, "get_forecast": get_forecast}

    async with httpx.AsyncClient(timeout=15.0) as http:
        messages: list[Any] = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ]
        tools_called: list[ToolCallRecord] = []

        for _turn in range(5):  # hard cap, same as agent_tools.run_agent
            response = await _create_completion(
                model=_llm_model,
                messages=messages,
                tools=TOOL_DEFINITIONS,
                tool_choice="auto",
            )
            choice = response.choices[0]
            messages.append(choice.message)

            if not choice.message.tool_calls:
                break

            for tc in choice.message.tool_calls:
                tool_name = tc.function.name
                try:
                    tool_args = json.loads(tc.function.arguments)
                except json.JSONDecodeError:
                    tool_args = {}

                if verbose:
                    print(f"[tool call] {tool_name}({tool_args})")

                tool_fn = tool_fns.get(tool_name)
                result = {"error": f"Unknown tool: {tool_name!r}"} if tool_fn is None else await tool_fn(http, **tool_args)
                result_str = json.dumps(result)

                if verbose:
                    print(f"[tool result] {result_str[:300]}\n")

                tools_called.append(ToolCallRecord(name=tool_name, input_parameters=tool_args, output=result_str))
                messages.append({"role": "tool", "tool_call_id": tc.id, "content": result_str})

        final_output = ""
        for msg in reversed(messages):
            if isinstance(msg, dict):
                if msg.get("role") == "assistant" and msg.get("content"):
                    final_output = msg["content"]
                    break
            elif msg.role == "assistant" and msg.content:
                final_output = msg.content
                break

        return AgentResponse(output=final_output, tools_called=tools_called)


def to_deepeval_tool_calls(agent_response: AgentResponse):
    """Convert an AgentResponse's tool records to deepeval.test_case.ToolCall objects."""
    from deepeval.test_case import ToolCall  # lazy import — deepeval is a test dependency

    return [
        ToolCall(name=tc.name, input_parameters=tc.input_parameters, output=tc.output)
        for tc in agent_response.tools_called
    ]


def attach_trace(test_case, query: str, agent_response: AgentResponse) -> None:
    """Populate test_case._trace_dict from an AgentResponse.

    StepEfficiencyMetric (and TaskCompletionMetric's trace-aware path) read
    test_case._trace_dict — a DeepEval-native execution trace — rather than
    tools_called. That field is normally populated by decorating tools with
    deepeval.tracing.observe() and running through deepeval's own tracing
    context; since weather_agent's tools are plain async functions with no
    DeepEval tracing wired in, we build the equivalent minimal trace by hand
    from the same ToolCallRecord data already captured in tools_called.
    """
    import time
    import uuid as uuid_lib

    from deepeval.tracing.tracing import trace_manager
    from deepeval.tracing.types import BaseSpan, ToolSpan, TraceSpanStatus

    trace_uuid = str(uuid_lib.uuid4())
    now = time.time()

    child_spans = [
        ToolSpan(
            uuid=str(uuid_lib.uuid4()),
            status=TraceSpanStatus.SUCCESS,
            trace_uuid=trace_uuid,
            start_time=now,
            end_time=now,
            name=tc.name,
            input=tc.input_parameters,
            output=tc.output,
        )
        for tc in agent_response.tools_called
    ]
    root_span = BaseSpan(
        uuid=str(uuid_lib.uuid4()),
        status=TraceSpanStatus.SUCCESS,
        trace_uuid=trace_uuid,
        start_time=now,
        end_time=now,
        name="run_agent",
        input=query,
        output=agent_response.output,
        children=child_spans,
    )
    test_case._trace_dict = trace_manager.create_nested_spans_dict(root_span)


if __name__ == "__main__":
    import asyncio
    load_dotenv(BASE_DIR / ".env")
    user_message = "What is the current weather in Bengaluru City?"
    agent_response = asyncio.run(run_agent(user_message, verbose=True))
    print(f"\n[agent output] {agent_response.output}")
