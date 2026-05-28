import { useState } from "react";
import { ragQuery } from "../api/client";
import type { RagQueryResponse } from "../api/types";
import ErrorState from "../components/ErrorState";
import LoadingState from "../components/LoadingState";

export default function RagPlaygroundPage() {
  const [question, setQuestion] = useState("");
  const [productArea, setProductArea] = useState("");
  const [issueType, setIssueType] = useState("");
  const [priority, setPriority] = useState("");
  const [customerTier, setCustomerTier] = useState("");
  const [status, setStatus] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState<RagQueryResponse | null>(null);

  const handleSubmit = async () => {
    if (!question.trim()) return;
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const filters: Record<string, string> = {};
      if (productArea) filters.product_area = productArea;
      if (issueType) filters.issue_type = issueType;
      if (priority) filters.priority = priority;
      if (customerTier) filters.customer_tier = customerTier;
      if (status) filters.status = status;
      const data = await ragQuery(
        question,
        Object.keys(filters).length > 0 ? filters : undefined,
      );
      setResult(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Query failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1>RAG Playground</h1>

      <div style={{ marginBottom: "1rem" }}>
        <textarea
          placeholder="Ask a question about support tickets..."
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          rows={3}
          style={{ width: "100%", maxWidth: 600, padding: "0.5rem" }}
        />
      </div>

      <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap", marginBottom: "1rem" }}>
        <input
          placeholder="Product Area"
          value={productArea}
          onChange={(e) => setProductArea(e.target.value)}
        />
        <input
          placeholder="Issue Type"
          value={issueType}
          onChange={(e) => setIssueType(e.target.value)}
        />
        <input
          placeholder="Priority"
          value={priority}
          onChange={(e) => setPriority(e.target.value)}
        />
        <input
          placeholder="Customer Tier"
          value={customerTier}
          onChange={(e) => setCustomerTier(e.target.value)}
        />
        <input
          placeholder="Status"
          value={status}
          onChange={(e) => setStatus(e.target.value)}
        />
      </div>

      <button onClick={handleSubmit} disabled={!question.trim() || loading}>
        Ask
      </button>

      {loading && <LoadingState message="Querying..." />}
      {error && <ErrorState message={error} />}

      {result && (
        <div style={{ marginTop: "1.5rem" }}>
          <div
            style={{
              background: "#f8f9fa",
              padding: "1rem",
              borderRadius: 8,
              marginBottom: "1rem",
            }}
          >
            <h3 style={{ marginTop: 0 }}>Answer</h3>
            <p style={{ whiteSpace: "pre-wrap" }}>{result.answer}</p>
          </div>

          <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap", marginBottom: "1rem" }}>
            <div>
              <strong>Confidence:</strong> {(result.confidence * 100).toFixed(1)}%
            </div>
            <div>
              <strong>Latency:</strong> {result.latency_ms}ms
            </div>
            <div>
              <strong>Est. Cost:</strong> ${result.estimated_cost_usd.toFixed(4)}
            </div>
          </div>

          {result.citations.length > 0 && (
            <div style={{ marginBottom: "1rem" }}>
              <strong>Citations:</strong>{" "}
              {result.citations.map((id) => (
                <span
                  key={id}
                  style={{
                    display: "inline-block",
                    background: "#e3f2fd",
                    padding: "2px 8px",
                    borderRadius: 4,
                    margin: "2px",
                  }}
                >
                  {id}
                </span>
              ))}
            </div>
          )}

          {result.retrieved_chunks.length > 0 && (
            <details>
              <summary style={{ cursor: "pointer", fontWeight: 600 }}>
                Retrieved Chunks ({result.retrieved_chunks.length})
              </summary>
              {result.retrieved_chunks.map((c) => (
                <div
                  key={c.chunk_id}
                  style={{
                    border: "1px solid #ddd",
                    borderRadius: 8,
                    padding: "0.75rem",
                    marginTop: "0.5rem",
                  }}
                >
                  <div>
                    <strong>Ticket:</strong> {c.ticket_id} | <strong>Score:</strong>{" "}
                    {c.score.toFixed(4)}
                  </div>
                  <div style={{ color: "#555", fontSize: "0.9rem", marginTop: 4 }}>{c.preview}</div>
                </div>
              ))}
            </details>
          )}
        </div>
      )}
    </div>
  );
}
