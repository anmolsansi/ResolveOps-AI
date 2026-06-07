import { useState } from "react";
import { assistDraft } from "../api/client";
import type { AssistResponse, Escalation } from "../api/types";
import ErrorState from "../components/ErrorState";
import LoadingState from "../components/LoadingState";
import { badge, btn, card, colors, input, pageTitle, sectionTitle } from "../styles";

const TIERS = ["", "Enterprise", "Pro", "Free"];

const ESCALATION_LABEL: Record<Escalation, string> = {
  answer: "Send answer",
  ask_clarification: "Ask for clarification",
  route_to_human: "Route to human",
};

const ESCALATION_COLOR: Record<Escalation, string> = {
  answer: colors.success,
  ask_clarification: colors.warning,
  route_to_human: colors.danger,
};

export default function AssistPage() {
  const [subject, setSubject] = useState("");
  const [body, setBody] = useState("");
  const [tier, setTier] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState<AssistResponse | null>(null);

  const handleSubmit = async () => {
    if (!subject.trim()) return;
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const data = await assistDraft({
        subject,
        body,
        customer_tier: tier || undefined,
      });
      setResult(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Request failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1 style={pageTitle}>Live Ticket Assist</h1>
      <p style={{ color: colors.textMuted, marginTop: "-1rem", marginBottom: "1.5rem" }}>
        Paste a live ticket to get a grounded draft reply, an escalation recommendation,
        and customer-tier-aware guidance — with separate customer-facing and internal modes.
      </p>

      {error && <ErrorState message={error} />}

      <div style={{ ...card, marginBottom: "1.5rem" }}>
        <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
          <input
            style={input}
            placeholder="Ticket subject"
            value={subject}
            onChange={(e) => setSubject(e.target.value)}
          />
          <textarea
            style={{ ...input, minHeight: 90, resize: "vertical" }}
            placeholder="Ticket body / customer message"
            value={body}
            onChange={(e) => setBody(e.target.value)}
          />
          <div style={{ display: "flex", gap: "0.75rem", alignItems: "center" }}>
            <select value={tier} onChange={(e) => setTier(e.target.value)} style={input}>
              {TIERS.map((t) => (
                <option key={t} value={t}>
                  {t || "Customer tier (optional)"}
                </option>
              ))}
            </select>
            <button onClick={handleSubmit} disabled={loading || !subject.trim()} style={btn("primary")}>
              Generate draft
            </button>
          </div>
        </div>
      </div>

      {loading && <LoadingState message="Drafting a grounded response..." />}

      {result && (
        <div>
          <div style={{ ...card, marginBottom: "1.5rem", display: "flex", gap: "1.5rem", alignItems: "center", flexWrap: "wrap" }}>
            <div>
              <div style={{ fontSize: "0.78rem", color: colors.textMuted, marginBottom: 4 }}>
                Recommendation
              </div>
              <span style={badge(ESCALATION_COLOR[result.recommendation])}>
                {ESCALATION_LABEL[result.recommendation]}
              </span>
            </div>
            <div>
              <div style={{ fontSize: "0.78rem", color: colors.textMuted, marginBottom: 4 }}>
                Confidence
              </div>
              <strong style={{ fontSize: "1.1rem" }}>{(result.confidence * 100).toFixed(1)}%</strong>
            </div>
            <div style={{ flex: 1, minWidth: 220, color: colors.textMuted, fontSize: "0.85rem" }}>
              {result.recommendation_reason}
            </div>
          </div>

          <div style={{ display: "flex", gap: "1.5rem", flexWrap: "wrap" }}>
            <div style={{ ...card, flex: "1 1 360px", borderTop: `3px solid ${colors.primary}` }}>
              <h2 style={sectionTitle}>Customer-facing draft</h2>
              <p style={{ whiteSpace: "pre-wrap", color: colors.text, fontSize: "0.9rem" }}>
                {result.customer_facing_draft}
              </p>
              {result.citations.length > 0 && (
                <div style={{ marginTop: "0.75rem", fontSize: "0.8rem", color: colors.textMuted }}>
                  Cited tickets:{" "}
                  {result.citations.map((id) => (
                    <a
                      key={id}
                      href={`/tickets/${encodeURIComponent(id)}`}
                      style={{ ...badge(colors.primary), textDecoration: "none", marginRight: 4 }}
                    >
                      {id}
                    </a>
                  ))}
                </div>
              )}
            </div>

            <div style={{ ...card, flex: "1 1 360px", borderTop: `3px solid ${colors.warning}` }}>
              <h2 style={sectionTitle}>Internal note (agent only)</h2>
              <pre
                style={{
                  whiteSpace: "pre-wrap",
                  fontFamily: "inherit",
                  color: colors.text,
                  fontSize: "0.85rem",
                  margin: 0,
                }}
              >
                {result.internal_note}
              </pre>
              <div style={{ marginTop: "0.75rem", fontSize: "0.82rem", color: colors.textMuted }}>
                <strong>Tier guidance:</strong> {result.tier_guidance}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
