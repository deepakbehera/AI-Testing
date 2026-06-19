#!/usr/bin/env bash
# ─── RAG Chatbot — One-command launcher ───────────────────────────────────
# Starts the backend (FastAPI) and frontend (Vite dev server) in parallel.
# Press Ctrl+C to stop both.
#
# Usage:
#   cd rag-chatbot
#   ./start.sh
#
# Prerequisites:
#   - Ollama running locally (ollama serve)
#   - pip install -r backend/requirements.txt
#   - cd frontend && npm install
# ──────────────────────────────────────────────────────────────────────────

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"
BACKEND_PORT=8000
FRONTEND_PORT=5173

# Detect Python from virtual env or fallback to system python3
if [ -n "$VIRTUAL_ENV" ]; then
    PYTHON="$VIRTUAL_ENV/bin/python"
elif [ -f "$ROOT_DIR/../.venv/bin/python" ]; then
    PYTHON="$ROOT_DIR/../.venv/bin/python"
elif [ -f "$ROOT_DIR/.venv/bin/python" ]; then
    PYTHON="$ROOT_DIR/.venv/bin/python"
elif [ -f "$ROOT_DIR/venv/bin/python" ]; then
    PYTHON="$ROOT_DIR/venv/bin/python"
else
    PYTHON="python3"
fi

cleanup() {
    echo ""
    echo "⏹ Shutting down..."
    kill "$BACKEND_PID" 2>/dev/null || true
    kill "$FRONTEND_PID" 2>/dev/null || true
    wait "$BACKEND_PID" 2>/dev/null || true
    wait "$FRONTEND_PID" 2>/dev/null || true
    echo "✓ Stopped"
    exit 0
}
trap cleanup SIGINT SIGTERM

echo "━━━ RAG Chatbot ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Backend :  http://localhost:$BACKEND_PORT"
echo "  Frontend:  http://localhost:$FRONTEND_PORT"
echo "  Python  :  $PYTHON"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# ── Start Backend ────────────────────────────────────────────────────────
echo ""
echo "▶ Starting backend..."
cd "$BACKEND_DIR"
$PYTHON -m uvicorn main:app --host 0.0.0.0 --port "$BACKEND_PORT" --reload &
BACKEND_PID=$!

# Wait for backend to be ready (poll health endpoint, up to 30s)
echo -n "   Waiting for backend..."
for i in $(seq 1 30); do
    if curl -s "http://localhost:$BACKEND_PORT/api/health" >/dev/null 2>&1; then
        echo " ready ✓"
        break
    fi
    echo -n "."
    sleep 1
done
if ! curl -s "http://localhost:$BACKEND_PORT/api/health" >/dev/null 2>&1; then
    echo ""
    echo "✖ Backend failed to start within 30s — check backend/ for errors."
    cleanup
fi

# ── Start Frontend ───────────────────────────────────────────────────────
echo "▶ Starting frontend..."
cd "$FRONTEND_DIR"
npx vite --host 0.0.0.0 --port "$FRONTEND_PORT" &
FRONTEND_PID=$!

echo ""
echo "━━━ Both servers are running ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Open http://localhost:$FRONTEND_PORT in your browser"
echo "  Press Ctrl+C to stop everything"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Wait for either process to exit, then clean up the other
# Uses polling instead of wait -n for macOS bash 3.2 compatibility
while kill -0 "$BACKEND_PID" 2>/dev/null && kill -0 "$FRONTEND_PID" 2>/dev/null; do
    sleep 1
done
cleanup
