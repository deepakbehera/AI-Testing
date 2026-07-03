# agent_tools.py
# A real tool-calling customer service agent using OpenAI's function-calling API.
# Same PROVIDER switch and .env loading convention as Module 6's agent.py.
# Same WidgetPro/TurboMax theme, extended with order management (check_order_status,
# process_refund, get_product_info, escalate_to_human).
#
# Key differences from Module 6's agent.py:
#   - Module 6: LLM decides WHEN to retrieve (planner loop)
#   - Module 7: LLM decides WHICH TOOL to call AND WHAT ARGUMENTS to pass
#     (OpenAI tools parameter, function-calling API)
#
# Every tool is @traceable — each invocation appears as its own child span in
# LangSmith with run_type="tool", so you can inspect name/args/output per-call.
#
# Exposes judge_client and judge_model at module level (same pattern as Module 6)
# for use in notebook LLM-judge cells.

import json
import os
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import instructor
import tenacity
from dotenv import load_dotenv
from langsmith import traceable
from openai import AsyncOpenAI, BadRequestError
from pydantic import BaseModel

# Anchored to this file's own directory — same convention as Module 6's agent.py.
load_dotenv(Path(__file__).resolve().parent / ".env")

PROVIDER = os.getenv("PROVIDER", "azure").lower()

if PROVIDER == "azure":
    _client = AsyncOpenAI(
        base_url=os.getenv("AZURE_OPENAI_ENDPOINT_C"),
        api_key=os.getenv("AZURE_OPENAI_KEY"),
    )
    _llm_model = os.getenv("AZURE_OPENAI_DEPLOYMENT", "DeepSeek-V3.2")
    # Mode.JSON_SCHEMA for non-OpenAI models that don't emit native function calls;
    # used only for judge_client structured-output calls, not the agent loop itself.
    _instructor_client = instructor.from_openai(_client, mode=instructor.Mode.JSON_SCHEMA)
elif PROVIDER == "openai":
    _client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    _llm_model = os.getenv("DEMO_MODEL", "gpt-4o-mini")
    _instructor_client = instructor.from_openai(_client)
else:  # ollama
    _ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
    _client = AsyncOpenAI(base_url=_ollama_url, api_key="ollama")
    _llm_model = os.getenv("DEMO_MODEL", "llama3.2:3b")
    _instructor_client = instructor.from_openai(_client, mode=instructor.Mode.JSON_SCHEMA)


# ---------------------------------------------------------------------------
#  In-memory "database" — same WidgetPro/TurboMax theme as Module 6, extended
#  with order records and amounts for refund processing.
# ---------------------------------------------------------------------------

ORDERS: dict[str, dict[str, Any]] = {
    "12345": {
        "status": "shipped",
        "product": "WidgetPro 3000",
        "estimated_delivery": "2 days",
        "amount": 199.00,
    },
    "67890": {
        "status": "processing",
        "product": "TurboMax Pro",
        "estimated_delivery": "5 days",
        "amount": 299.00,
    },
    "99999": {
        "status": "delivered",
        "product": "WidgetPro 3000",
        "estimated_delivery": None,
        "amount": 199.00,
    },
}

PRODUCTS: dict[str, dict[str, Any]] = {
    "WidgetPro 3000": {
        "price": "$199",
        "cancellation_fee": "$0",
        "support_type": "online",
    },
    "TurboMax Pro": {
        "price": "$299/year",
        "cancellation_fee": "unknown",   # no data — agent should say so, not invent a number
        "support_type": "online",
    },
    "WidgetPro 2000": {
        "price": "discontinued",
        "cancellation_fee": "$50",
        "support_type": "none",
    },
}


# ---------------------------------------------------------------------------
#  Tool implementations — each is @traceable so every call appears as its own
#  LangSmith span under the agent trace. run_type="tool" lets you filter to
#  just tool-call spans in the LangSmith UI.
# ---------------------------------------------------------------------------

@traceable(run_type="tool", name="check_order_status")
def check_order_status(order_id: str) -> dict:
    """Look up the current status of an order by its ID.

    Returns the order's status, product name, estimated delivery window, and
    order amount. Returns an error dict if the order_id is not found.
    """
    order = ORDERS.get(order_id)
    if order is None:
        return {"error": f"Order {order_id!r} not found."}
    return {
        "status": order["status"],
        "product": order["product"],
        "estimated_delivery": order["estimated_delivery"],
        "amount": order["amount"],
    }


@traceable(run_type="tool", name="process_refund")
def process_refund(order_id: str, reason: str) -> dict:
    """Initiate a refund for a given order.

    Returns a refund confirmation with a generated refund_id, the order
    amount, and an initial status of "initiated". Returns an error dict if
    the order_id is not found.
    """
    order = ORDERS.get(order_id)
    if order is None:
        return {"error": f"Order {order_id!r} not found — cannot process refund."}
    return {
        "refund_id": f"R-{uuid.uuid4().hex[:6].upper()}",
        "amount": order["amount"],
        "status": "initiated",
        "reason": reason,
    }


@traceable(run_type="tool", name="get_product_info")
def get_product_info(product_name: str) -> dict:
    """Return pricing, cancellation fee, and support type for a product.

    Returns an error dict if the product_name is not in the catalogue.
    Note: TurboMax Pro's cancellation_fee is 'unknown' — the agent should
    report this honestly rather than inventing a number (the Air Canada
    pattern from Day 1).
    """
    product = PRODUCTS.get(product_name)
    if product is None:
        return {"error": f"Product {product_name!r} not found in catalogue."}
    return {
        "price": product["price"],
        "cancellation_fee": product["cancellation_fee"],
        "support_type": product["support_type"],
    }


@traceable(run_type="tool", name="escalate_to_human")
def escalate_to_human(reason: str) -> dict:
    """Create a human-agent escalation ticket.

    Routes to the appropriate queue (billing, technical, or general) based on
    the reason string. Returns a ticket_id and estimated wait time.
    """
    reason_lower = reason.lower()
    if any(w in reason_lower for w in ("refund", "charge", "payment", "billing", "invoice")):
        queue = "billing"
        wait = "30 minutes"
    elif any(w in reason_lower for w in ("broken", "bug", "error", "crash", "not working", "technical")):
        queue = "technical"
        wait = "45 minutes"
    else:
        queue = "general"
        wait = "2 hours"
    return {
        "ticket_id": f"CS-{uuid.uuid4().hex[:4].upper()}",
        "estimated_wait": wait,
        "queue": queue,
    }


# ---------------------------------------------------------------------------
#  OpenAI function-calling tool definitions — the schema the LLM uses to
#  decide which function to call and what arguments to pass.
# ---------------------------------------------------------------------------

TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "check_order_status",
            "description": "Look up the current status, product name, estimated delivery, and amount for a customer order by its ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "The order ID (e.g. '12345').",
                    }
                },
                "required": ["order_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "process_refund",
            "description": "Initiate a refund for a customer order. Use only when the customer explicitly requests a refund.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "The order ID to refund.",
                    },
                    "reason": {
                        "type": "string",
                        "description": "The reason for the refund as stated by the customer.",
                    },
                },
                "required": ["order_id", "reason"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_product_info",
            "description": "Return pricing, cancellation fee, and support type for a named product.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_name": {
                        "type": "string",
                        "description": "The product name exactly as it appears in the catalogue (e.g. 'WidgetPro 3000', 'TurboMax Pro').",
                    }
                },
                "required": ["product_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "escalate_to_human",
            "description": "Escalate the customer's issue to a human agent when the AI cannot resolve it. Use for complex complaints, policy disputes, or situations requiring human judgment.",
            "parameters": {
                "type": "object",
                "properties": {
                    "reason": {
                        "type": "string",
                        "description": "A brief description of why escalation is needed.",
                    }
                },
                "required": ["reason"],
            },
        },
    },
]

TOOL_MAP = {
    "check_order_status": check_order_status,
    "process_refund": process_refund,
    "get_product_info": get_product_info,
    "escalate_to_human": escalate_to_human,
}


# ---------------------------------------------------------------------------
#  ToolCall record — mirrors deepeval.test_case.ToolCall for internal use.
#  We define our own here so agent_tools.py doesn't depend on deepeval at
#  runtime; notebooks import from deepeval directly when building test cases.
# ---------------------------------------------------------------------------

@dataclass
class ToolCallRecord:
    """Records one tool invocation: what was called, with what, and what came back."""
    name: str
    input_parameters: dict
    output: str  # JSON-serialized tool result


@dataclass
class AgentResponse:
    """The agent's complete response after one interaction turn."""
    output: str                                  # The final natural-language response to the user
    tools_called: list[ToolCallRecord] = field(default_factory=list)
    # For debugging: the full LLM-side tool call object (OpenAI ChatCompletionMessageToolCall)
    raw_tool_calls: list[Any] = field(default_factory=list)


# ---------------------------------------------------------------------------
#  The agent loop — uses OpenAI's tools parameter for real function-calling.
#
#  Flow:
#    1. Send user message + TOOL_DEFINITIONS to the LLM
#    2. LLM returns a tool call (name + arguments JSON)
#    3. Execute the tool using TOOL_MAP
#    4. Append tool result to messages
#    5. LLM generates the final natural-language response
#
#  Supports multi-tool calls in a single turn (the loop in step 2-4 handles
#  multiple tool_calls if the LLM returns them).
# ---------------------------------------------------------------------------

@traceable(run_type="chain", name="customer_service_agent")
async def run_agent(
    user_message: str,
    verbose: bool = False,
) -> AgentResponse:
    """Run the customer service agent for one user message.

    verbose=True prints tool names and arguments as they're called, useful
    in notebooks to see the real function-calling flow without needing a
    LangSmith account.

    Returns an AgentResponse with the final output and a list of ToolCallRecord
    objects for each tool the agent invoked. Pass tools_called to DeepEval's
    LLMTestCase as ToolCall objects (see notebooks for the conversion helper).
    """
    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful customer service agent for WidgetPro Inc. "
                "You have access to tools to check order status, process refunds, "
                "look up product information, and escalate to human agents. "
                "Always use the appropriate tool to answer questions — never answer "
                "policy or order questions from memory alone. "
                "If a tool returns an error or 'unknown', say so honestly rather than guessing."
            ),
        },
        {"role": "user", "content": user_message},
    ]

    tools_called: list[ToolCallRecord] = []
    raw_tool_calls: list[Any] = []

    # Multi-tool call loop: keep calling tools until the LLM stops requesting them.
    for _turn in range(5):  # hard cap at 5 tool calls per turn
        response = await _client.chat.completions.create(
            model=_llm_model,
            messages=messages,
            tools=TOOL_DEFINITIONS,
            tool_choice="auto",
        )

        choice = response.choices[0]
        messages.append(choice.message)

        # If the LLM didn't request any tool call, it's done.
        if not choice.message.tool_calls:
            break

        # Execute each tool call the LLM requested this turn.
        for tc in choice.message.tool_calls:
            tool_name = tc.function.name
            try:
                tool_args = json.loads(tc.function.arguments)
            except json.JSONDecodeError:
                tool_args = {}

            if verbose:
                print(f"[tool call] {tool_name}({tool_args})")

            tool_fn = TOOL_MAP.get(tool_name)
            if tool_fn is None:
                result = {"error": f"Unknown tool: {tool_name!r}"}
            else:
                result = tool_fn(**tool_args)

            if verbose:
                print(f"[tool result] {result}\n")

            result_str = json.dumps(result)
            tools_called.append(
                ToolCallRecord(
                    name=tool_name,
                    input_parameters=tool_args,
                    output=result_str,
                )
            )
            raw_tool_calls.append(tc)

            messages.append(
                {
                    "role": "tool",
                    "content": result_str,
                    "tool_call_id": tc.id,
                }
            )

    # The final message after the last tool-result round trip is the assistant's
    # natural-language response. If we exited because tool_calls was empty, the
    # last appended message is already the response.
    final_output = ""
    for msg in reversed(messages):
        if isinstance(msg, dict):
            if msg.get("role") == "assistant" and msg.get("content"):
                final_output = msg["content"]
                break
        else:
            # OpenAI ChatCompletionMessage object
            if msg.role == "assistant" and msg.content:
                final_output = msg.content
                break

    return AgentResponse(
        output=final_output,
        tools_called=tools_called,
        raw_tool_calls=raw_tool_calls,
    )


# ---------------------------------------------------------------------------
#  Judge client and model — exposed at module level so notebooks can use the
#  same LLM for structured-output judgment calls. Same pattern as Module 6.
# ---------------------------------------------------------------------------

judge_client = _instructor_client
judge_model = _llm_model


# ---------------------------------------------------------------------------
#  Convenience: convert AgentResponse.tools_called to deepeval ToolCall objects.
#  Import deepeval lazily so agent_tools.py itself doesn't require deepeval.
# ---------------------------------------------------------------------------

def to_deepeval_tool_calls(agent_response: AgentResponse):
    """Convert an AgentResponse's tool records to deepeval.test_case.ToolCall objects."""
    from deepeval.test_case import ToolCall  # lazy import — deepeval is a test dependency

    return [
        ToolCall(
            name=tc.name,
            input_parameters=tc.input_parameters,
            output=tc.output,
        )
        for tc in agent_response.tools_called
    ]
