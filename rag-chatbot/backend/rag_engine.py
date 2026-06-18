"""
RAG engine: embeddings via sentence-transformers, LLM via Ollama.
Manages the retrieval-augmented generation pipeline.
"""

import os
import re
from typing import List, Optional
from openai import OpenAI

from vector_store import InMemoryVectorStore


# ---------------------------------------------------------------------------
#  Text chunking
# ---------------------------------------------------------------------------

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """Split text into overlapping chunks at sentence boundaries."""
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks = []
    current = []
    current_len = 0
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        current.append(sentence)
        current_len += len(sentence)
        if current_len >= chunk_size:
            chunks.append(" ".join(current))
            # keep overlap sentences
            overlap_count = 0
            overlap_sentences = []
            for s in reversed(current):
                overlap_count += len(s)
                overlap_sentences.insert(0, s)
                if overlap_count >= overlap:
                    break
            current = list(overlap_sentences)
            current_len = overlap_count
    if current:
        chunks.append(" ".join(current))
    return chunks


# ---------------------------------------------------------------------------
#  Document loaders
# ---------------------------------------------------------------------------

def load_txt(filepath: str) -> str:
    """Load a plain-text file."""
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def load_pdf(filepath: str) -> str:
    """Load a PDF file using PyMuPDF."""
    import fitz
    doc = fitz.open(filepath)
    text = "\n".join(page.get_text() for page in doc)
    doc.close()
    return text


SUPPORTED_EXTENSIONS = {
    ".txt": load_txt,
    ".md":  load_txt,
    ".pdf": load_pdf,
}


# ---------------------------------------------------------------------------
#  RAG Engine
# ---------------------------------------------------------------------------

class RagEngine:
    """Orchestrates embedding, retrieval, and LLM answer generation."""

    def __init__(self,
                 ollama_base_url: str = "http://localhost:11434/v1",
                 llm_model: str = "llama3.2:3b",
                 embed_model: str = "all-MiniLM-L6-v2"):
        self.ollama_base_url = ollama_base_url
        self.llm_model = llm_model
        self.embed_model_name = embed_model

        # sentence-transformers for local embeddings
        from sentence_transformers import SentenceTransformer
        self.embedder = SentenceTransformer(self.embed_model_name)

        # OpenAI-compatible client for Ollama
        self.llm_client = OpenAI(
            base_url=self.ollama_base_url,
            api_key="ollama",  # Ollama ignores the key but requires something
        )

        self.vector_store = InMemoryVectorStore()

    # ---- Embeddings -------------------------------------------------------

    def _embed(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using sentence-transformers."""
        embeddings = self.embedder.encode(texts, show_progress_bar=False)
        return [emb.tolist() for emb in embeddings]

    # ---- Ingestion --------------------------------------------------------

    def ingest_file(self, filepath: str) -> Optional[str]:
        """Ingest a document. Returns document_id or None on failure."""
        ext = os.path.splitext(filepath)[1].lower()
        loader = SUPPORTED_EXTENSIONS.get(ext)
        if loader is None:
            raise ValueError(f"Unsupported file type: {ext}")

        text = loader(filepath)
        if not text.strip():
            raise ValueError("File is empty")

        chunks = chunk_text(text)
        embeddings = self._embed(chunks)
        # convert to numpy arrays
        import numpy as np
        emb_arrays = [np.array(e, dtype=np.float32) for e in embeddings]
        filename = os.path.basename(filepath)
        return self.vector_store.add_document(filename, chunks, emb_arrays)

    # ---- Retrieval --------------------------------------------------------

    def retrieve(self, query: str, top_k: int = 5) -> List[str]:
        """Retrieve the most relevant chunks for a query."""
        query_emb = self._embed([query])[0]
        import numpy as np
        results = self.vector_store.search(np.array(query_emb, dtype=np.float32),
                                            top_k=top_k)
        return [r["text"] for r, _ in results]

    # ---- Generation --------------------------------------------------------

    def _build_prompt(self, context_chunks: List[str]) -> str:
        """Build a RAG system prompt with context (no query — that comes as user msg)."""
        context = "\n\n".join(
            f"[Chunk {i+1}] {chunk}"
            for i, chunk in enumerate(context_chunks)
        )
        return (
            "You are a helpful assistant. Answer the user's question based on the "
            "provided context. If the context doesn't contain the answer, say so.\n\n"
            f"--- Context ---\n{context}"
        )

    def chat(self, query: str, history: Optional[List[dict]] = None,
             top_k: int = 5) -> tuple:
        """Full RAG pipeline: retrieve context, then generate answer.

        Returns (answer_text, source_chunks).
        """
        # retrieve relevant chunks
        chunks = self.retrieve(query, top_k=top_k)

        # build messages
        system_prompt = self._build_prompt(chunks)
        messages = [{"role": "system", "content": system_prompt}]

        if history:
            messages.extend(history)

        messages.append({"role": "user", "content": query})

        response = self.llm_client.chat.completions.create(
            model=self.llm_model,
            messages=messages,
            temperature=0.7,
            max_tokens=1024,
        )
        answer = response.choices[0].message.content
        return answer, chunks

    # ---- Document management -----------------------------------------------

    def list_documents(self) -> List[dict]:
        return self.vector_store.list_documents()

    def delete_document(self, doc_id: str) -> bool:
        return self.vector_store.delete_document(doc_id)

    def clear_all(self):
        self.vector_store.clear()


# ---------------------------------------------------------------------------
#  Factory
# ---------------------------------------------------------------------------

def create_engine() -> RagEngine:
    """Create a RagEngine configured from environment variables.

    Reads .env file from the backend/ directory if python-dotenv is available.
    """
    import os
    # optionally load .env file
    try:
        from dotenv import load_dotenv
        dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
        if os.path.isfile(dotenv_path):
            load_dotenv(dotenv_path)
    except ImportError:
        pass

    ollama_url = os.environ.get(
        "OLLAMA_BASE_URL", "http://localhost:11434/v1"
    )
    llm_model = os.environ.get("LLM_MODEL", "llama3.2:3b")
    embed_model = os.environ.get("EMBED_MODEL", "all-MiniLM-L6-v2")
    return RagEngine(
        ollama_base_url=ollama_url,
        llm_model=llm_model,
        embed_model=embed_model,
    )
