# agent.py
# A trip-planning agent whose tools come from a REAL local MCP server
# (../trip_mcp_server/server.py), launched over stdio. This is the MCP
# counterpart to weather_agent: same PROVIDER/.env convention and the same
# AgentResponse / ToolCallRecord / run_agent / to_deepeval_tool_calls /
# attach_trace interface (so ci/ can test it with the same DeepEval metrics),
# but instead of calling in-process Python functions it speaks the MCP protocol
# to a separate server process that owns the tools.
#
# For a "what should I pack for <place>?" question the agent chains three MCP
# tools: geocode -> get_weather -> suggest_packing. Every tool call is wrapped
# in a LangSmith @traceable span (run_type="tool"), and the whole run is a
# @traceable chain — so with LANGSMITH_TRACING=true and a LANGSMITH_API_KEY set,
# each query shows up in the LangSmith UI as a trip_agent trace with the MCP
# tool calls as nested child spans (name, arguments, output per call). Without
# those env vars the decorators are no-ops and the agent runs exactly the same.

import json
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import tenacity
from dotenv import load_dotenv
from langsmith import traceable
from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client
from openai import AsyncOpenAI, RateLimitError

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

# The local MCP server this agent launches over stdio. sys.executable ensures
# it runs under the same interpreter/venv as the agent (so mcp + httpx resolve).
MCP_SERVER_PATH = BASE_DIR.parent / "trip_mcp_server" / "server.py"

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

SYSTEM_PROMPT = """You are a trip-planning assistant. Your tools come from an MCP server and must
be used to answer questions about what to pack for a trip.

To answer a "what should I pack for <destination>?" question you MUST use all three tools, in order:
  1. geocode(place)                     -> get the destination's latitude/longitude
  2. get_weather(latitude, longitude)   -> get the forecast for those coordinates
  3. suggest_packing(temp_max_c, temp_min_c, conditions) -> the authoritative packing list,
     using a representative day from the forecast returned by get_weather

Never skip suggest_packing and improvise the packing list yourself — call it so the recommendation
is grounded in the real forecast numbers. Never guess coordinates or weather from memory. Once you
have the packing suggestion, relay it to the user in a short, friendly summary.
"""

# The shared Azure deployment is rate-limited; back off and retry on 429s.
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
    """Records one MCP tool invocation: what was called, with what, and what came back."""
    name: str
    input_parameters: dict
    output: str


@dataclass
class AgentResponse:
    """The agent's complete response after one interaction turn."""
    output: str
    tools_called: list[ToolCallRecord] = field(default_factory=list)


def _mcp_tool_to_openai(tool) -> dict:
    return {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description or "",
            "parameters": tool.inputSchema or {"type": "object", "properties": {}},
        },
    }


def _make_traced_dispatch(session: ClientSession):
    """Build a LangSmith-traced tool dispatcher bound to this MCP session.

    session is captured in the closure rather than passed as an argument so it
    doesn't end up as a (non-serializable) traced input — each span records just
    the tool name, arguments, and output, which is what's useful to see in the
    LangSmith UI.
    """

    @traceable(run_type="tool")
    async def _dispatch(tool_name: str, tool_args: dict) -> str:
        result = await session.call_tool(tool_name, arguments=tool_args)
        texts = [b.text for b in result.content if getattr(b, "type", None) == "text"]
        combined = "\n".join(texts)
        if result.isError:
            return json.dumps({"error": combined or "Tool call failed."})
        return combined

    return _dispatch


@traceable(run_type="chain", name="trip_agent")
async def run_agent(user_message: str, verbose: bool = False) -> AgentResponse:
    """Run the trip agent for one user message against the live MCP server.

    Launches ../trip_mcp_server/server.py over stdio, discovers its tools, and
    runs an OpenAI function-calling loop, chaining geocode -> get_weather ->
    suggest_packing. Returns the same shape as weather_agent.run_agent.
    """
    server_params = StdioServerParameters(command=sys.executable, args=[str(MCP_SERVER_PATH)])
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            mcp_tools = (await session.list_tools()).tools
            tool_defs = [_mcp_tool_to_openai(t) for t in mcp_tools]
            dispatch = _make_traced_dispatch(session)

            messages: list[Any] = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ]
            tools_called: list[ToolCallRecord] = []

            for _turn in range(8):  # cap tool-call rounds
                response = await _create_completion(
                    model=_llm_model,
                    messages=messages,
                    tools=tool_defs,
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
                        print(f"[mcp tool call] {tool_name}({tool_args})")

                    result_str = await dispatch(tool_name, tool_args, langsmith_extra={"name": tool_name})

                    if verbose:
                        print(f"[mcp tool result] {result_str[:300]}\n")

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

    StepEfficiencyMetric reads test_case._trace_dict — a DeepEval-native
    execution trace — rather than tools_called. Since this agent's tracing goes
    to LangSmith (not DeepEval's tracer), we build the equivalent minimal
    DeepEval trace by hand from the captured ToolCallRecords. Same helper as
    weather_agent.attach_trace.
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
        name="trip_agent",
        input=query,
        output=agent_response.output,
        children=child_spans,
    )
    test_case._trace_dict = trace_manager.create_nested_spans_dict(root_span)
