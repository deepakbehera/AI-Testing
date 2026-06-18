"""
FastAPI backend for RAG Chatbot.
Provides endpoints for uploading documents, chatting, and managing documents.
"""

import os
import tempfile
from typing import List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from rag_engine import create_engine


# ---------------------------------------------------------------------------
#  Lifespan (replaces on_event)
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup – engine reads env vars OLLAMA_BASE_URL, LLM_MODEL, EMBED_MODEL
    app.state.engine = create_engine()
    yield
    # shutdown – nothing to clean up


app = FastAPI(title="RAG Chatbot", version="1.0.0", lifespan=lifespan)

# Allow the Vite frontend to talk to us
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
#  Schemas
# ---------------------------------------------------------------------------

class ChatRequest(BaseModel):
    query: str
    history: Optional[List[dict]] = None
    top_k: int = 5


class ChatResponse(BaseModel):
    answer: str
    sources: List[str]


class DocumentInfo(BaseModel):
    id: str
    filename: str
    chunk_count: int


# ---------------------------------------------------------------------------
#  Routes
# ---------------------------------------------------------------------------

@app.get("/api/health")
async def health():
    return {"status": "ok"}


@app.get("/api/models")
async def list_models():
    """Return available Ollama models."""
    from openai import OpenAI
    client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
    try:
        models = client.models.list()
        return {"models": [m.id for m in models.data]}
    except Exception as e:
        return {"models": [app.state.engine.llm_model], "note": str(e)}


@app.post("/api/upload", response_model=DocumentInfo)
async def upload_document(file: UploadFile = File(...)):
    """Upload and ingest a document (txt, md, pdf)."""
    ext = os.path.splitext(file.filename or "file.txt")[1].lower()
    if ext not in (".txt", ".md", ".pdf"):
        raise HTTPException(400,
                            f"Unsupported file type '{ext}'. Use .txt, .md, or .pdf.")

    # save to a temp file, then ingest
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        doc_id = app.state.engine.ingest_file(tmp_path)
    except ValueError as e:
        raise HTTPException(400, str(e))
    finally:
        os.unlink(tmp_path)

    doc = app.state.engine.vector_store.documents[doc_id]
    return DocumentInfo(id=doc_id, filename=doc["filename"],
                        chunk_count=doc["chunk_count"])


@app.get("/api/documents", response_model=List[DocumentInfo])
async def list_documents():
    """List all ingested documents."""
    docs = app.state.engine.list_documents()
    return [DocumentInfo(**d) for d in docs]


@app.delete("/api/documents/{doc_id}")
async def delete_document(doc_id: str):
    """Delete a document and its chunks."""
    ok = app.state.engine.delete_document(doc_id)
    if not ok:
        raise HTTPException(404, "Document not found")
    return {"status": "deleted"}


@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """Chat with RAG: retrieve context and generate an answer."""
    engine = app.state.engine
    answer, sources = engine.chat(query=req.query, history=req.history,
                                   top_k=req.top_k)
    return ChatResponse(answer=answer, sources=sources)


@app.post("/api/clear")
async def clear_all():
    """Clear all documents from the vector store."""
    app.state.engine.clear_all()
    return {"status": "cleared"}


# ---------------------------------------------------------------------------
#  Entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
