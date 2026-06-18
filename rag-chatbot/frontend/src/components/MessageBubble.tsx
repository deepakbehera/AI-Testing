import { useState } from "react";
import type { Message } from "../types";

interface Props {
  message: Message;
}

export default function MessageBubble({ message }: Props) {
  const [showSources, setShowSources] = useState(message.sourcesVisible ?? false);

  return (
    <div className={`message ${message.role}`}>
      <div className="avatar">
        {message.role === "user" ? "👤" : "🤖"}
      </div>
      <div>
        <div className="bubble">{message.content}</div>
        {message.role === "assistant" && message.sources && message.sources.length > 0 && (
          <div className="sources-toggle">
            <button onClick={() => setShowSources(!showSources)}>
              {showSources ? "Hide" : "Show"} sources ({message.sources.length})
            </button>
          </div>
        )}
        {showSources && message.sources && (
          <div className="sources">
            {message.sources.map((src, i) => (
              <details key={i} open={i === 0}>
                <summary>Source {i + 1}</summary>
                <div className="source-text">{src}</div>
              </details>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
