"""
In-memory vector store for RAG chatbot.
Stores document chunks and their embeddings in memory using numpy.
"""

import numpy as np
import uuid
from typing import List, Dict, Optional, Tuple


class InMemoryVectorStore:
    """Simple in-memory vector store with cosine similarity search."""

    def __init__(self):
        self.chunks: List[Dict] = []          # metadata for each chunk
        self.embeddings: List[np.ndarray] = [] # corresponding embeddings
        self.documents: Dict[str, Dict] = {}   # document_id -> document metadata

    def add_document(self, filename: str, chunks: List[str],
                     embeddings: List[np.ndarray]) -> str:
        """Store all chunks for a document. Returns document_id."""
        doc_id = str(uuid.uuid4())
        self.documents[doc_id] = {
            "id": doc_id,
            "filename": filename,
            "chunk_count": len(chunks),
        }
        for i, (chunk, emb) in enumerate(zip(chunks, embeddings)):
            self.chunks.append({
                "doc_id": doc_id,
                "filename": filename,
                "chunk_index": i,
                "text": chunk,
            })
            self.embeddings.append(emb / np.linalg.norm(emb))
        return doc_id

    def delete_document(self, doc_id: str) -> bool:
        """Remove a document and all its chunks."""
        if doc_id not in self.documents:
            return False
        del self.documents[doc_id]
        # rebuild chunk/embedding lists excluding this doc
        keep = [i for i, c in enumerate(self.chunks) if c["doc_id"] != doc_id]
        self.chunks = [self.chunks[i] for i in keep]
        self.embeddings = [self.embeddings[i] for i in keep]
        return True

    def search(self, query_embedding: np.ndarray, top_k: int = 5
               ) -> List[Tuple[Dict, float]]:
        """Return top-k (chunk, score) results via cosine similarity."""
        if not self.embeddings:
            return []
        query_norm = query_embedding / np.linalg.norm(query_embedding)
        emb_matrix = np.stack(self.embeddings)  # (N, D)
        scores = emb_matrix @ query_norm        # cosine similarity
        top_indices = np.argsort(scores)[-top_k:][::-1]
        return [
            (self.chunks[i], float(scores[i]))
            for i in top_indices
            if scores[i] > 0
        ]

    def list_documents(self) -> List[Dict]:
        """Return metadata for all stored documents."""
        return list(self.documents.values())

    def clear(self):
        """Remove all data."""
        self.chunks.clear()
        self.embeddings.clear()
        self.documents.clear()
