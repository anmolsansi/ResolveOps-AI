import { useState } from "react";
import { Link } from "react-router-dom";
import { ragQuery, submitFeedback } from "../api/client";
import type { FeedbackValue, RagQueryResponse } from "../api/types";
import ErrorState from "../components/ErrorState";
import LoadingState from "../components/LoadingState";
import { badge, btn, card, colors, input, pageTitle, sectionTitle, td, th } from "../styles";

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
  const [feedback, setFeedback] = useState<FeedbackValue | null>(null);
  const [feedbackError, setFeedbackError] = useState("");

  const handleFeedback = async (value: FeedbackValue) => {
    if (!result) return;
    setFeedbackError("");
    try {
      await submitFeedback(result.query_id, value);
      setFeedback(value);
    } catch (e) {
      setFeedbackError(e instanceof Error ? e.message : "Feedback failed");
    }
  };

  const handleSubmit = async () => {
    if (!question.trim()) return;
    setLoading(true);
    setError("");
    setResult(null);
    setFeedback(null);
    setFeedbackError("");
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
      <h1 style={pageTitle}>RAG Playground</h1>

      <div style={{ ...card, marginBottom: "1.5rem" }}>
        <div style={{ marginBottom: "1rem" }}>
          <textarea
            placeholder="Ask a question about support tickets..."
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            rows={3}
            style={{
              ...input,
              width: "100%",
              maxWidth: 700,
              resize: "vertical",
              fontFamily: "inherit",
            }}
          />
        </div>

        <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap", marginBottom: "1rem" }}>
          {[
            { placeholder: "Product Area", value: productArea, setter: setProductArea },
            { placeholder: "Issue Type", value: issueType, setter: setIssueType },
            { placeholder: "Priority", value: priority, setter: setPriority },
            { placeholder: "Customer Tier", value: customerTier, setter: setCustomerTier },
            { placeholder: "Status", value: status, setter: setStatus },
          ].map(({ placeholder, value, setter }) => (
            <input
              key={placeholder}
              placeholder={placeholder}
              value={value}
              onChange={(e) => setter(e.target.value)}
              style={{ ...input, width: 130 }}
            />
          ))}
        </div>

        <button
          onClick={handleSubmit}
          disabled={!question.trim() || loading}
          style={{
            ...btn("primary"),
            opacity: !question.trim() || loading ? 0.5 : 1,
          }}
        >
          {loading ? "Querying..." : "Ask"}
        </button>
      </div>

      {loading && <LoadingState message="Querying..." />}
      {error && <ErrorState message={error} />}

      {result && (
        <>
          <div style={{ ...card, marginBottom: "1rem" }}>
            <h3 style={{ ...sectionTitle, fontSize: "0.95rem" }}>Answer</h3>
            <p style={{ whiteSpace: "pre-wrap", margin: 0, lineHeight: 1.6, color: colors.text }}>
              {result.answer}
            </p>
          </div>

          <div style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap", marginBottom: "1rem" }}>
            <div style={{ ...card, flex: 1, textAlign: "center" }}>
              <div style={{ fontSize: "1.2rem", fontWeight: 700, color: result.confidence >= 0.3 ? colors.success : colors.warning }}>
                {(result.confidence * 100).toFixed(1)}%
              </div>
              <div style={{ fontSize: "0.78rem", color: colors.textMuted }}>Confidence</div>
            </div>
            <div style={{ ...card, flex: 1, textAlign: "center" }}>
              <div style={{ fontSize: "1.2rem", fontWeight: 700, color: colors.primary }}>{result.latency_ms}ms</div>
              <div style={{ fontSize: "0.78rem", color: colors.textMuted }}>Latency</div>
            </div>
            <div style={{ ...card, flex: 1, textAlign: "center" }}>
              <div style={{ fontSize: "1.2rem", fontWeight: 700, color: colors.primary }}>
                ${result.estimated_cost_usd.toFixed(4)}
              </div>
              <div style={{ fontSize: "0.78rem", color: colors.textMuted }}>Est. Cost</div>
            </div>
            <div style={{ ...card, flex: 1, textAlign: "center" }}>
              <div style={{ fontSize: "0.95rem", fontWeight: 700, color: colors.text }}>
                {result.product_area ?? "-"}
              </div>
              <div style={{ fontSize: "0.78rem", color: colors.textMuted }}>
                Product Area &middot; {result.provider}/{result.model}
              </div>
            </div>
          </div>

          <div style={{ ...card, marginBottom: "1rem" }}>
            <h3 style={{ ...sectionTitle, fontSize: "0.95rem" }}>Answer Quality</h3>
            <div style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap" }}>
              {[
                {
                  label: "Hallucination Risk",
                  value: result.quality.hallucination_risk,
                  goodLow: true,
                },
                {
                  label: "Citation Coverage",
                  value: result.quality.citation_coverage,
                  goodLow: false,
                },
                {
                  label: "Retrieval Precision",
                  value: result.quality.retrieval_precision,
                  goodLow: false,
                },
                {
                  label: "Answer Completeness",
                  value: result.quality.answer_completeness,
                  goodLow: false,
                },
              ].map(({ label, value, goodLow }) => {
                const good = goodLow ? value < 0.5 : value >= 0.5;
                return (
                  <div key={label} style={{ flex: 1, minWidth: 130, textAlign: "center" }}>
                    <div
                      style={{
                        fontSize: "1.2rem",
                        fontWeight: 700,
                        color: good ? colors.success : colors.warning,
                      }}
                    >
                      {(value * 100).toFixed(1)}%
                    </div>
                    <div style={{ fontSize: "0.78rem", color: colors.textMuted }}>{label}</div>
                  </div>
                );
              })}
            </div>
          </div>

          <div style={{ ...card, marginBottom: "1rem" }}>
            <h3 style={{ ...sectionTitle, fontSize: "0.95rem" }}>Was this helpful?</h3>
            <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
              {([
                { value: "helpful" as const, text: "\uD83D\uDC4D Helpful", color: colors.success },
                { value: "not_helpful" as const, text: "\uD83D\uDC4E Not helpful", color: colors.warning },
                { value: "wrong_citation" as const, text: "\u26A0 Wrong citation", color: colors.danger },
              ]).map(({ value, text, color }) => (
                <button
                  key={value}
                  onClick={() => handleFeedback(value)}
                  style={{
                    ...btn("secondary"),
                    borderColor: feedback === value ? color : undefined,
                    color: feedback === value ? color : undefined,
                    fontWeight: feedback === value ? 700 : 500,
                  }}
                >
                  {text}
                </button>
              ))}
            </div>
            {feedback && (
              <p style={{ margin: "0.5rem 0 0", fontSize: "0.8rem", color: colors.success }}>
                Thanks — feedback recorded.
              </p>
            )}
            {feedbackError && (
              <p style={{ margin: "0.5rem 0 0", fontSize: "0.8rem", color: colors.danger }}>
                {feedbackError}
              </p>
            )}
          </div>

          {result.citations.length > 0 && (
            <div style={{ ...card, marginBottom: "1rem" }}>
              <h3 style={{ ...sectionTitle, fontSize: "0.95rem" }}>Citations</h3>
              <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
                {result.citations.map((id) => (
                  <Link
                    key={id}
                    to={`/tickets/${id}`}
                    style={{
                      ...badge(colors.primary),
                      textDecoration: "none",
                      cursor: "pointer",
                    }}
                  >
                    {id}
                  </Link>
                ))}
              </div>
            </div>
          )}

          {result.retrieved_chunks.length > 0 && (
            <div style={card}>
              <h3 style={{ ...sectionTitle, fontSize: "0.95rem" }}>
                Retrieval Debug ({result.retrieved_chunks.length} chunks)
              </h3>
              <div style={{ overflowX: "auto" }}>
                <table style={{ width: "100%", borderCollapse: "collapse" }}>
                  <thead>
                    <tr>
                      <th style={th}>Ticket</th>
                      <th style={th}>Final Score</th>
                      <th style={th}>Cosine</th>
                      <th style={th}>Keyword Boost</th>
                      <th style={th}>Hits</th>
                      <th style={th}>Matched Tokens</th>
                      <th style={th}>Preview</th>
                    </tr>
                  </thead>
                  <tbody>
                    {result.retrieved_chunks.map((c) => (
                      <tr key={c.chunk_id}>
                        <td style={td}>
                          <Link to={`/tickets/${c.ticket_id}`} style={{ color: colors.primary, fontWeight: 600 }}>
                            {c.ticket_id}
                          </Link>
                        </td>
                        <td style={td}>{c.score.toFixed(4)}</td>
                        <td style={td}>{c.debug?.cosine_score.toFixed(4) ?? "-"}</td>
                        <td style={td}>
                          <span style={badge(c.debug && c.debug.keyword_boost > 0 ? colors.success : colors.textMuted)}>
                            +{c.debug?.keyword_boost.toFixed(4) ?? "0"}
                          </span>
                        </td>
                        <td style={td}>{c.debug?.keyword_hits ?? 0}</td>
                        <td style={td}>
                          {c.debug?.matched_tokens.length
                            ? c.debug.matched_tokens.map((t) => (
                                <span key={t} style={{ ...badge(colors.primary), marginRight: 4 }}>
                                  {t}
                                </span>
                              ))
                            : "-"}
                        </td>
                        <td style={{ ...td, maxWidth: 250, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                          {c.preview.slice(0, 120)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
