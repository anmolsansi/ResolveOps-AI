import { useEffect, useReducer } from "react";
import { listHandoffs, updateHandoff } from "../api/client";
import type { HandoffResponse } from "../api/types";
import ErrorState from "../components/ErrorState";
import LoadingState from "../components/LoadingState";
import { badge, btn, card, colors, pageTitle } from "../styles";

const TRIGGER_LABELS: Record<string, string> = {
  low_confidence: "Low Confidence",
  angry_sentiment: "Angry Sentiment",
  policy_sensitive: "Policy Sensitive",
  customer_request: "Customer Request",
  unknown: "Other",
};

const TRIGGER_COLORS: Record<string, string> = {
  low_confidence: colors.warning,
  angry_sentiment: colors.danger,
  policy_sensitive: colors.danger,
  customer_request: colors.primary,
  unknown: colors.textMuted,
};

interface State {
  items: HandoffResponse[];
  pendingCount: number;
  loading: boolean;
  error: string;
}

type Action =
  | { type: "loading" }
  | { type: "loaded"; items: HandoffResponse[]; pendingCount: number }
  | { type: "error"; error: string };

const reducer = (state: State, action: Action): State => {
  switch (action.type) {
    case "loading":
      return { ...state, loading: true, error: "" };
    case "loaded":
      return { ...state, items: action.items, pendingCount: action.pendingCount, loading: false };
    case "error":
      return { ...state, error: action.error, loading: false };
  }
};

const initialState: State = { items: [], pendingCount: 0, loading: true, error: "" };

export default function HandoffsPage() {
  const [state, dispatch] = useReducer(reducer, initialState);

  const load = () => {
    dispatch({ type: "loading" });
    listHandoffs()
      .then((r) => dispatch({ type: "loaded", items: r.items, pendingCount: r.pending_count }))
      .catch((e) => dispatch({ type: "error", error: e.message }));
  };

  useEffect(load, []);

  const handleUpdate = async (id: string, status: string) => {
    try {
      await updateHandoff(id, status);
      load();
    } catch (e: unknown) {
      dispatch({ type: "error", error: e instanceof Error ? e.message : "Update failed" });
    }
  };

  if (state.loading) return <LoadingState />;
  if (state.error) return <ErrorState message={state.error} />;

  return (
    <div>
      <h1 style={pageTitle}>Human Handoffs</h1>
      <div style={{ marginBottom: "1.5rem", display: "flex", gap: "0.75rem", alignItems: "center" }}>
        <span style={badge(colors.danger)}>{state.pendingCount} pending</span>
        <span style={{ color: colors.textMuted, fontSize: "0.85rem" }}>
          {state.items.length} total handoffs
        </span>
      </div>

      {state.items.length === 0 ? (
        <div style={{ ...card, textAlign: "center", padding: "3rem" }}>
          <p style={{ color: colors.textMuted }}>No handoffs yet. Handoffs are created when AI detects low confidence, angry sentiment, or policy-sensitive topics.</p>
        </div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
          {state.items.map((h) => (
            <div key={h.id} style={{ ...card, borderLeft: `4px solid ${TRIGGER_COLORS[h.trigger_reason] || colors.border}` }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "0.75rem" }}>
                <div>
                  <div style={{ display: "flex", gap: "0.5rem", alignItems: "center", marginBottom: 4 }}>
                    <span style={badge(TRIGGER_COLORS[h.trigger_reason] || colors.textMuted)}>{TRIGGER_LABELS[h.trigger_reason] || h.trigger_reason}</span>
                    <span style={badge(h.status === "pending" ? colors.danger : h.status === "acknowledged" ? colors.warning : colors.success)}>{h.status}</span>
                  </div>
                  <div style={{ fontSize: "0.82rem", color: colors.textMuted }}>
                    Likely intent: <strong>{h.likely_intent}</strong>
                  </div>
                </div>
                <div style={{ fontSize: "0.78rem", color: colors.textMuted }}>
                  {new Date(h.created_at).toLocaleString()}
                </div>
              </div>

              <p style={{ fontSize: "0.88rem", marginBottom: "0.75rem", lineHeight: 1.5 }}>{h.summary}</p>

              {h.suggested_reply && (
                <div style={{ padding: "0.75rem", background: "#f0fdf4", borderRadius: 8, marginBottom: "0.75rem", border: "1px solid #bbf7d0" }}>
                  <div style={{ fontSize: "0.72rem", fontWeight: 600, color: "#166534", marginBottom: 4 }}>Suggested Reply</div>
                  <div style={{ fontSize: "0.85rem", color: "#15803d" }}>{h.suggested_reply}</div>
                </div>
              )}

              {h.status === "pending" && (
                <div style={{ display: "flex", gap: "0.5rem" }}>
                  <button onClick={() => handleUpdate(h.id, "acknowledged")} style={btn("primary")}>
                    Acknowledge
                  </button>
                  <button onClick={() => handleUpdate(h.id, "resolved")} style={btn("secondary")}>
                    Resolve
                  </button>
                </div>
              )}
              {h.status === "acknowledged" && (
                <button onClick={() => handleUpdate(h.id, "resolved")} style={btn("secondary")}>
                  Mark Resolved
                </button>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
