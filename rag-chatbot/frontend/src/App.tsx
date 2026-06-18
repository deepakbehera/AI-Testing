import { useState, useEffect, useRef, useCallback } from "react";
import type { Message, DocumentInfo } from "./types";
import {
  uploadDocument,
  listDocuments,
  deleteDocument,
  sendChat,
  clearAll,
  healthCheck,
} from "./api";
import MessageBubble from "./components/MessageBubble";

export default function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [docs, setDocs] = useState<DocumentInfo[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [connected, setConnected] = useState(false);
  const [dragging, setDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // ---- Health check -------------------------------------------------------
  useEffect(() => {
    const check = async () => {
      const ok = await healthCheck();
      setConnected(ok);
    };
    check();
    const interval = setInterval(check, 10_000);
    return () => clearInterval(interval);
  }, []);

  // ---- Load documents -----------------------------------------------------
  const refreshDocs = useCallback(async () => {
    try {
      const d = await listDocuments();
      setDocs(d);
    } catch {
      console.error("Failed to load documents");
    }
  }, []);

  useEffect(() => {
    if (connected) refreshDocs();
  }, [connected, refreshDocs]);

  // ---- Auto-scroll --------------------------------------------------------
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // ---- Auto-resize textarea -----------------------------------------------
  useEffect(() => {
    const ta = textareaRef.current;
    if (ta) {
      ta.style.height = "auto";
      ta.style.height = Math.min(ta.scrollHeight, 120) + "px";
    }
  }, [input]);

  // ---- File upload --------------------------------------------------------
  const handleFile = async (file: File) => {
    const ext = file.name.split(".").pop()?.toLowerCase();
    if (!ext || !["txt", "md", "pdf"].includes(ext)) {
      alert("Only .txt, .md, and .pdf files are supported.");
      return;
    }
    try {
      setLoading(true);
      await uploadDocument(file);
      await refreshDocs();
    } catch (e: any) {
      alert(e.message || "Upload failed");
    } finally {
      setLoading(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleFile(file);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  // ---- Delete document ----------------------------------------------------
  const handleDelete = async (id: string) => {
    try {
      await deleteDocument(id);
      await refreshDocs();
    } catch {
      console.error("Delete failed");
    }
  };

  // ---- Chat ---------------------------------------------------------------
  const handleSend = async () => {
    const query = input.trim();
    if (!query || loading) return;

    const userMsg: Message = { role: "user", content: query };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const history = messages.map((m) => ({
        role: m.role,
        content: m.content,
      }));
      const res = await sendChat(query, history);
      const assistantMsg: Message = {
        role: "assistant",
        content: res.answer,
        sources: res.sources,
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (e: any) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: `❌ Error: ${e.message || "Chat failed"}`,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // ---- Clear chat ---------------------------------------------------------
  const handleClearChat = () => setMessages([]);

  const fileIcon = (name: string) => {
    const ext = name.split(".").pop()?.toLowerCase();
    if (ext === "pdf") return "📄";
    if (ext === "md") return "📝";
    return "📃";
  };

  return (
    <div className="app-container">
      {/* ── Sidebar ──────────────────────────────────────────────────── */}
      <aside className="sidebar">
        <div className="sidebar-header">
          <span className="logo">🧠</span>
          <h1>RAG Chatbot</h1>
        </div>

        <div className="sidebar-section">
          <h2>Upload Document</h2>
          <div
            className={`upload-area${dragging ? " dragging" : ""}`}
            onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
            onDragLeave={() => setDragging(false)}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".txt,.md,.pdf"
              onChange={handleFileSelect}
            />
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"
              strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
              <polyline points="17 8 12 3 7 8" />
              <line x1="12" y1="3" x2="12" y2="15" />
            </svg>
            {dragging ? "Drop file here" : "Drop a file or click to upload"}
            <br />
            <small>.txt, .md, .pdf</small>
          </div>
        </div>

        <div className="sidebar-section" style={{ flex: 1, display: "flex", flexDirection: "column" }}>
          <h2>Documents ({docs.length})</h2>
          {docs.length === 0 ? (
            <div className="doc-list-empty">
              No documents yet. Upload a file to start.
            </div>
          ) : (
            <ul className="doc-list">
              {docs.map((doc) => (
                <li key={doc.id} className="doc-item">
                  <span className="doc-name">
                    <span className="doc-icon">{fileIcon(doc.filename)}</span>
                    {doc.filename}
                  </span>
                  <span className="doc-chunks">{doc.chunk_count} chunks</span>
                  <button
                    className="delete-btn"
                    title="Remove document"
                    onClick={() => handleDelete(doc.id)}
                  >
                    ✕
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="sidebar-section" style={{ borderTop: "1px solid var(--border)", padding: "0.6rem 1rem" }}>
          <button
            onClick={handleClearChat}
            style={{
              background: "none",
              border: "1px solid var(--border)",
              color: "var(--text-muted)",
              padding: "0.4rem 0.8rem",
              borderRadius: "var(--radius-sm)",
              cursor: "pointer",
              fontSize: "0.78rem",
              width: "100%",
              transition: "all 0.15s",
            }}
            onMouseOver={(e) => e.currentTarget.style.borderColor = "var(--accent)"}
            onMouseOut={(e) => e.currentTarget.style.borderColor = "var(--border)"}
          >
            🗑 Clear conversation
          </button>
        </div>
      </aside>

      {/* ── Chat area ────────────────────────────────────────────────── */}
      <main className="chat-area">
        {messages.length === 0 ? (
          <div className="chat-empty">
            <div className="big-icon">🤖</div>
            <h2>RAG Chatbot</h2>
            <p>
              Upload documents in the sidebar, then ask questions about their content.
              The chatbot uses your local LLM (Ollama) for answers.
            </p>
          </div>
        ) : (
          <div className="chat-messages">
            {messages.map((msg, i) => (
              <MessageBubble key={i} message={msg} />
            ))}
            {loading && (
              <div className="message assistant">
                <div className="avatar">🤖</div>
                <div className="typing-indicator">
                  <span /><span /><span />
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}

        <div className="chat-input-bar">
          <form
            onSubmit={(e) => { e.preventDefault(); handleSend(); }}
          >
            <textarea
              ref={textareaRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask a question about your documents…"
              rows={1}
              disabled={loading}
            />
            <button type="submit" disabled={loading || !input.trim()}>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"
                strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <line x1="22" y1="2" x2="11" y2="13" />
                <polygon points="22 2 15 22 11 13 2 9 22 2" />
              </svg>
            </button>
          </form>
        </div>

        <div className="status-bar">
          <span className={`status-dot${connected ? "" : " disconnected"}`} />
          {connected ? "Connected to backend" : "Backend disconnected"}
          <span style={{ marginLeft: "auto" }}>
            model: llama3.2:3b · local
          </span>
        </div>
      </main>
    </div>
  );
}
