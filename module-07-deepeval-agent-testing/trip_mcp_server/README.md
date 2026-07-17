# trip_mcp_server — running & inspecting a local MCP server

A tiny, standalone **MCP server** built with the official `mcp` SDK's `FastMCP`.
It exposes three tools that a trip-planning agent chains together:

| Tool | Input | What it does |
|---|---|---|
| `geocode` | `place` | place name → latitude / longitude / country (open-meteo, no key) |
| `get_weather` | `latitude, longitude, days` | coordinates → current conditions + daily forecast |
| `suggest_packing` | `temp_max_c, temp_min_c, conditions` | forecast → a packing list |

---

## 1. What is MCP (the one-slide version)

**MCP (Model Context Protocol)** is a standard way to expose *tools* (and data)
to an LLM agent — think of it as **"a USB-C port for AI tools"** or **"OpenAPI/Swagger,
but for LLM tool-calling."** An MCP **server** publishes a list of tools, each with a
JSON input schema; an MCP **client** (inside the agent) discovers those tools and calls
them. The agent's LLM never talks to open-meteo directly — it asks the MCP server.

**How it actually runs here:** the server speaks over **stdio** (standard in/out) using
JSON-RPC. The client *launches the server as a subprocess* and talks to it over that pipe —
there is no port to open, no HTTP. That's why running `python server.py` on its own just
"hangs": it's a server waiting for a client to speak JSON-RPC on stdin. You don't run it
directly; something connects to it.

---

## 2. Inspect it visually — the MCP Inspector (the "Swagger UI" for MCP)

The **MCP Inspector** is a web app that connects to any MCP server and lets you browse its
tools, read their schemas, fill in a form, click **Run**, and see the JSON response — exactly
like Swagger UI's "Try it out." Launch it against this server (run from the module root,
`module-07-deepeval-agent-testing/`):

```bash
npx -y @modelcontextprotocol/inspector \
  /Users/takshinvarma/Desktop/AI-Testing-APR/.venv/bin/python3 \
  /Users/takshinvarma/Desktop/AI-Testing-APR/module-07-deepeval-agent-testing/trip_mcp_server/server.py
```

> **Use ABSOLUTE paths for both** the venv Python and `server.py`. The Inspector's proxy spawns
> the server from its own working directory, so a relative path like `../.venv/bin/python3`
> fails with `spawn ... ENOENT` (file not found). Absolute paths work from any directory.
> `npx` downloads the Inspector the first time (needs Node, already installed here).

It prints a `http://localhost:6274/?...` URL and opens your browser. What students see:

- **Tools** tab → the three tools, each with its description and input schema.
- Pick `geocode`, type `place = Paris`, click **Run Tool** → the JSON result appears.
- The **History / notifications** pane shows the raw JSON-RPC request & response for each call —
  great for showing "this is literally what the agent sends the server."

> Official shortcut: `mcp dev trip_mcp_server/server.py` does the same thing, but it shells
> out to `uv` — install it first with `pip install uv`. The `npx` command above needs no `uv`.

---

## 3. Inspect it from the terminal (no browser — good for slides)

The Inspector also has a `--cli` mode that prints and exits — handy for a live terminal demo:

```bash
# List the tools = the server's "API spec"
npx -y @modelcontextprotocol/inspector --cli \
  /Users/takshinvarma/Desktop/AI-Testing-APR/.venv/bin/python3 \
  /Users/takshinvarma/Desktop/AI-Testing-APR/module-07-deepeval-agent-testing/trip_mcp_server/server.py \
  --method tools/list

# Call one tool = Swagger's "Try it out"
npx -y @modelcontextprotocol/inspector --cli \
  /Users/takshinvarma/Desktop/AI-Testing-APR/.venv/bin/python3 \
  /Users/takshinvarma/Desktop/AI-Testing-APR/module-07-deepeval-agent-testing/trip_mcp_server/server.py \
  --method tools/call --tool-name geocode --tool-arg place=Paris
```

---

## 4. See the tools used *by the agent* (LangSmith)

Sections 2–3 inspect the server in isolation. To watch the agent actually *chain* the tools
(`geocode → get_weather → suggest_packing`) on a real question, run the agent with LangSmith
tracing on — set `LANGSMITH_TRACING=true` and `LANGSMITH_API_KEY=...` in `../trip_agent/.env`,
then:

```bash
cd ../trip_agent
python cli.py "What should I pack for a 3-day trip to Reykjavik?"
```

Each run shows up in the LangSmith UI as a `trip_agent` trace with the MCP tool calls as
nested child spans (name, arguments, output per call). Without the LangSmith env vars it runs
identically, just untraced — and `--verbose` still prints each `[mcp tool call]` to the terminal.
