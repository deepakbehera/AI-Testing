# 🧠 RAG Chatbot

A local, free, privacy-first Retrieval-Augmented Generation chatbot built with:

- **Backend:** FastAPI (Python) + sentence-transformers + Ollama
- **Frontend:** Vite + React + TypeScript
- **Vector Store:** In-memory (numpy cosine similarity)

All processing happens on your machine — no data leaves your computer.

---

## Prerequisites

- **Python 3.10+** with `pip`
- **Node.js 18+** with `npm`
- **[Ollama](https://ollama.com)** running locally with at least one model pulled
  (e.g. `ollama pull llama3.2:3b`)

## Setup

### 1. Ollama

Make sure Ollama is running and you have a model downloaded:

```bash
ollama serve          # start the Ollama server
ollama list           # verify models are available
```

### 2. Backend

```bash
cd backend
pip install -r requirements.txt
python main.py        # starts on http://localhost:8000
```

The first run will download the `all-MiniLM-L6-v2` embedding model (~80 MB)
from Hugging Face — this is a one-time download.

**Optional:** Copy `.env.example` to `.env` and customize:

```bash
cp .env.example .env
```

| Variable         | Default                    | Description                              |
|------------------|----------------------------|------------------------------------------|
| `OLLAMA_BASE_URL` | `http://localhost:11434/v1` | Ollama OpenAI-compatible endpoint        |
| `LLM_MODEL`      | `llama3.2:3b`              | Model for answering (must be in Ollama)  |
| `EMBED_MODEL`    | `all-MiniLM-L6-v2`         | Sentence-transformers model for embeddings |

### 3. Frontend

```bash
cd frontend
npm install
npm run dev          # starts on http://localhost:5173
```

The Vite dev server proxies `/api` requests to the backend, so you only need
to open http://localhost:5173 in your browser.

---

## Usage

1. **Upload documents** — Drag & drop or click to upload `.txt`, `.md`, or `.pdf` files
2. **Ask questions** — Type your question in the chat input
3. **Retrieve & answer** — The chatbot retrieves relevant chunks from your documents
   and generates an answer using your local Ollama model

---

## Switching Models

### Change the LLM (Ollama)

```bash
# Set in .env
LLM_MODEL=deepseek-r1:1.5b
```

Or export the variable before starting the backend:

```bash
export LLM_MODEL=deepseek-r1:1.5b
```

### Change the Embedding Model

```bash
# Set in .env
EMBED_MODEL=all-mpnet-base-v2
```

---

## Project Structure

```
rag-chatbot/
├── backend/
│   ├── main.py            # FastAPI app & routes
│   ├── rag_engine.py      # RAG pipeline (embeddings → retrieval → generation)
│   ├── vector_store.py    # In-memory vector store with cosine similarity
│   ├── test_rag.py        # Quick validation script
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── App.tsx         # Main app with sidebar & chat
│   │   ├── api.ts          # Backend API client
│   │   ├── types.ts        # Shared TypeScript types
│   │   └── components/
│   │       └── MessageBubble.tsx
│   ├── package.json
│   ├── vite.config.ts
│   └── index.html
└── README.md
```

---

## API Endpoints

| Method | Endpoint             | Description                     |
|--------|----------------------|---------------------------------|
| GET    | `/api/health`        | Health check                    |
| GET    | `/api/models`        | List available Ollama models    |
| POST   | `/api/upload`        | Upload & ingest a document      |
| GET    | `/api/documents`     | List ingested documents         |
| DELETE | `/api/documents/:id` | Delete a document               |
| POST   | `/api/chat`          | Send a chat message (with RAG)  |
| POST   | `/api/clear`         | Clear all documents             |

---

## License

MIT
