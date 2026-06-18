/** API client for the RAG Chatbot backend. */

import type { DocumentInfo } from "./types";

const BASE = "/api";

export interface ChatResponse {
  answer: string;
  sources: string[];
}

export async function uploadDocument(file: File): Promise<DocumentInfo> {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${BASE}/upload`, { method: "POST", body: form });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Upload failed");
  }
  return res.json();
}

export async function listDocuments(): Promise<DocumentInfo[]> {
  const res = await fetch(`${BASE}/documents`);
  return res.json();
}

export async function deleteDocument(id: string): Promise<void> {
  const res = await fetch(`${BASE}/documents/${id}`, { method: "DELETE" });
  if (!res.ok) throw new Error("Delete failed");
}

export async function sendChat(
  query: string,
  history?: { role: string; content: string }[],
  topK = 5,
): Promise<ChatResponse> {
  const res = await fetch(`${BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, history, top_k: topK }),
  });
  if (!res.ok) throw new Error("Chat request failed");
  return res.json();
}

export async function clearAll(): Promise<void> {
  await fetch(`${BASE}/clear`, { method: "POST" });
}

export async function healthCheck(): Promise<boolean> {
  try {
    const res = await fetch(`${BASE}/health`);
    return res.ok;
  } catch {
    return false;
  }
}
