import { useEffect, useRef, useState } from "react";
import type { FormEvent } from "react";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
const API_KEY = "dev-widget-key";

interface Message {
  role: "customer" | "ai" | "system";
  content: string;
  citations?: string[];
  confidence?: number;
}

export default function WidgetHost() {
  const [messages, setMessages] = useState<Message[]>(() => [
    { role: "system", content: "Welcome! How can we help you today?" },
  ]);
  const [input, setInput] = useState("");
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [sending, setSending] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const send = async (e: FormEvent) => {
    e.preventDefault();
    const text = input.trim();
    if (!text || sending) return;
    setInput("");
    setSending(true);

    setMessages((prev) => [...prev, { role: "customer", content: text }]);

    try {
      const res = await fetch(`${API_BASE}/widget/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-Widget-Key": API_KEY },
        body: JSON.stringify({
          message: text,
          conversation_id: conversationId,
          customer_email: "demo@example.com",
          customer_name: "Demo User",
        }),
      });
      if (!res.ok) throw new Error(`API error ${res.status}`);
      const data = await res.json();

      setConversationId(data.conversation_id);
      setMessages((prev) => [
        ...prev,
        { role: "ai", content: data.answer, citations: data.citations, confidence: data.confidence },
      ]);
      if (data.should_escalate) {
        setMessages((prev) => [...prev, { role: "system", content: "Escalating to a human support agent..." }]);
      }
    } catch {
      setMessages((prev) => [...prev, { role: "ai", content: "Sorry, something went wrong. Please try again." }]);
    } finally {
      setSending(false);
    }
  };

  return (
    <div style={{ fontFamily: "Inter, system-ui, sans-serif", height: "100vh", display: "flex", flexDirection: "column", background: "#f9fafb" }}>
      <div style={{ background: "#6366f1", color: "white", padding: "16px 20px", fontWeight: 600, fontSize: 16 }}>
        ResolveOps Support
      </div>
      <div style={{ flex: 1, overflowY: "auto", padding: 20, display: "flex", flexDirection: "column", gap: 12 }}>
        {messages.map((msg, i) => (
          <div
            key={i}
            style={{
              maxWidth: "80%",
              padding: "12px 16px",
              borderRadius: 12,
              fontSize: 14,
              lineHeight: 1.5,
              alignSelf: msg.role === "customer" ? "flex-end" : msg.role === "system" ? "center" : "flex-start",
              background: msg.role === "customer" ? "#6366f1" : msg.role === "system" ? "#fef3c7" : "white",
              color: msg.role === "customer" ? "white" : msg.role === "system" ? "#92400e" : "#111",
              border: msg.role === "ai" ? "1px solid #e5e7eb" : "none",
            }}
          >
            {msg.content}
            {msg.citations && msg.citations.length > 0 && (
              <div style={{ marginTop: 6, fontSize: 11, color: "#6b7280" }}>Sources: {msg.citations.join(", ")}</div>
            )}
            {msg.confidence !== undefined && (
              <div style={{ fontSize: 11, color: "#9ca3af", marginTop: 4 }}>
                Confidence: {Math.round(msg.confidence * 100)}%
              </div>
            )}
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>
      <form onSubmit={send} style={{ padding: 16, borderTop: "1px solid #e5e7eb", display: "flex", gap: 8, background: "white" }}>
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a question..."
          disabled={sending}
          style={{ flex: 1, padding: "12px 16px", border: "1px solid #d1d5db", borderRadius: 8, fontSize: 14, outline: "none" }}
        />
        <button
          type="submit"
          disabled={sending || !input.trim()}
          style={{ padding: "12px 20px", background: "#6366f1", color: "white", border: "none", borderRadius: 8, cursor: "pointer", fontWeight: 600, fontSize: 14, opacity: sending || !input.trim() ? 0.5 : 1 }}
        >
          Send
        </button>
      </form>
    </div>
  );
}
