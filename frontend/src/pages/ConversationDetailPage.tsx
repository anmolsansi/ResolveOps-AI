import { useEffect, useReducer } from "react";
import { useNavigate, useParams } from "react-router-dom";
import {
  getConversationDetail,
  replyToConversation,
  resolveConversation,
} from "../api/client";
import type { ConversationDetail } from "../api/types";
import ErrorState from "../components/ErrorState";
import LoadingState from "../components/LoadingState";
import { badge, btn, card, colors, input, pageTitle } from "../styles";

interface State {
  conversation: ConversationDetail | null;
  loading: boolean;
  error: string;
  replyText: string;
  sending: boolean;
  resolving: boolean;
}

type Action =
  | { type: "loading" }
  | { type: "loaded"; conversation: ConversationDetail }
  | { type: "error"; error: string }
  | { type: "reply"; text: string }
  | { type: "sending"; sending: boolean }
  | { type: "reply_sent"; conversation: ConversationDetail }
  | { type: "resolving"; resolving: boolean }
  | { type: "resolved"; conversation: ConversationDetail };

const reducer = (state: State, action: Action): State => {
  switch (action.type) {
    case "loading":
      return { ...state, loading: true, error: "" };
    case "loaded":
      return { ...state, conversation: action.conversation, loading: false };
    case "error":
      return { ...state, error: action.error, loading: false };
    case "reply":
      return { ...state, replyText: action.text };
    case "sending":
      return { ...state, sending: action.sending };
    case "reply_sent":
      return {
        ...state,
        conversation: action.conversation,
        replyText: "",
        sending: false,
      };
    case "resolving":
      return { ...state, resolving: action.resolving };
    case "resolved":
      return { ...state, conversation: action.conversation, resolving: false };
  }
};

const initialState: State = {
  conversation: null,
  loading: true,
  error: "",
  replyText: "",
  sending: false,
  resolving: false,
};

export default function ConversationDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [state, dispatch] = useReducer(reducer, initialState);

  useEffect(() => {
    if (!id) return;
    dispatch({ type: "loading" });
    getConversationDetail(id)
      .then((c) => dispatch({ type: "loaded", conversation: c }))
      .catch((e) => dispatch({ type: "error", error: e.message }));
  }, [id]);

  const handleReply = async () => {
    if (!id || !state.replyText.trim()) return;
    dispatch({ type: "sending", sending: true });
    try {
      const updated = await replyToConversation(id, {
        message: state.replyText.trim(),
      });
      dispatch({ type: "reply_sent", conversation: updated });
    } catch (err: unknown) {
      dispatch({ type: "error", error: err instanceof Error ? err.message : "Reply failed" });
    }
  };

  const handleResolve = async () => {
    if (!id) return;
    dispatch({ type: "resolving", resolving: true });
    try {
      const updated = await resolveConversation(id, {
        outcome: "ai_contained",
      });
      dispatch({ type: "resolved", conversation: updated });
    } catch (err: unknown) {
      dispatch({ type: "error", error: err instanceof Error ? err.message : "Resolve failed" });
    }
  };

  if (state.loading) return <LoadingState />;
  if (state.error) return <ErrorState message={state.error} />;
  if (!state.conversation) return <ErrorState message="Conversation not found" />;

  const c = state.conversation;
  const statusColors: Record<string, string> = {
    open: colors.primary,
    waiting_for_customer: colors.warning,
    escalated: colors.danger,
    resolved: colors.success,
  };

  return (
    <div>
      <button
        onClick={() => navigate("/conversations")}
        style={{ ...btn("secondary"), marginBottom: "1rem" }}
      >
        Back to Conversations
      </button>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 280px", gap: "1.5rem" }}>
        <div>
          <h1 style={pageTitle}>
            {c.subject || `Conversation ${c.id.slice(0, 8)}`}
          </h1>
          <div style={{ display: "flex", gap: "0.5rem", marginBottom: "1rem" }}>
            <span style={badge(statusColors[c.status] || colors.textMuted)}>
              {c.status.replace(/_/g, " ")}
            </span>
            {c.sentiment && <span style={badge(colors.warning)}>{c.sentiment}</span>}
            <span style={badge(colors.secondary)}>{c.channel}</span>
            {c.total_messages && <span style={badge(colors.info)}>{c.total_messages} messages</span>}
          </div>

          <div style={card}>
            <h3 style={{ margin: "0 0 1rem", color: colors.text }}>Transcript</h3>
            {c.messages.map((m) => (
              <div
                key={m.id}
                style={{
                  padding: "0.75rem 1rem",
                  marginBottom: "0.5rem",
                  borderRadius: "8px",
                  background: m.role === "agent" ? colors.info + "15" : colors.bgSecondary,
                  borderLeft: `3px solid ${m.role === "agent" ? colors.info : colors.textMuted}`,
                }}
              >
                <div style={{ fontSize: "0.75rem", color: colors.textMuted, marginBottom: "0.25rem" }}>
                  {m.role === "agent" ? "AI Agent" : "Customer"} &middot;{" "}
                  {new Date(m.created_at).toLocaleString()}
                </div>
                <div style={{ color: colors.text, whiteSpace: "pre-wrap" }}>{m.content}</div>
              </div>
            ))}
          </div>

          {c.status !== "resolved" && (
            <div style={{ ...card, marginTop: "1rem" }}>
              <h3 style={{ margin: "0 0 0.75rem", color: colors.text }}>Agent Reply</h3>
              <textarea
                value={state.replyText}
                onChange={(e) => dispatch({ type: "reply", text: e.target.value })}
                placeholder="Type your reply..."
                style={{
                  ...input,
                  width: "100%",
                  minHeight: "100px",
                  resize: "vertical",
                  fontFamily: "inherit",
                }}
              />
              <div style={{ display: "flex", gap: "0.5rem", marginTop: "0.75rem" }}>
                <button onClick={handleReply} disabled={state.sending} style={btn("primary")}>
                  {state.sending ? "Sending..." : "Send Reply"}
                </button>
                <button onClick={handleResolve} disabled={state.resolving} style={btn("secondary")}>
                  {state.resolving ? "Resolving..." : "Mark Resolved"}
                </button>
              </div>
            </div>
          )}
        </div>

        <div>
          <div style={card}>
            <h3 style={{ margin: "0 0 0.75rem", color: colors.text }}>Customer</h3>
            <div style={{ color: colors.text, marginBottom: "0.5rem" }}>
              {c.customer_name || "Unknown"}
            </div>
            {c.customer_email && (
              <div style={{ color: colors.textMuted, fontSize: "0.85rem", marginBottom: "0.5rem" }}>
                {c.customer_email}
              </div>
            )}
            {c.customer_tier && (
              <div style={{ marginBottom: "0.5rem" }}>
                <span style={badge(colors.warning)}>{c.customer_tier}</span>
              </div>
            )}
          </div>

          <div style={{ ...card, marginTop: "1rem" }}>
            <h3 style={{ margin: "0 0 0.75rem", color: colors.text }}>Handoffs</h3>
            {c.handoffs.length === 0 ? (
              <div style={{ color: colors.textMuted, fontSize: "0.85rem" }}>No handoffs</div>
            ) : (
              c.handoffs.map((h) => (
                <div
                  key={h.id}
                  style={{
                    padding: "0.5rem",
                    marginBottom: "0.5rem",
                    borderRadius: "6px",
                    background: h.resolved ? colors.success + "15" : colors.warning + "15",
                    fontSize: "0.85rem",
                  }}
                >
                  <div style={{ color: colors.text }}>
                    {h.reason}
                    {h.resolved && <span style={{ color: colors.success }}> (resolved)</span>}
                  </div>
                  <div style={{ color: colors.textMuted, fontSize: "0.75rem" }}>
                    {new Date(h.created_at).toLocaleString()}
                  </div>
                </div>
              ))
            )}
          </div>

          <div style={{ ...card, marginTop: "1rem" }}>
            <h3 style={{ margin: "0 0 0.75rem", color: colors.text }}>Resolution</h3>
            {c.resolution_outcome ? (
              <div>
                <div style={badge(c.resolution_outcome === "ai_contained" ? colors.success : colors.warning)}>
                  {c.resolution_outcome.replace(/_/g, " ")}
                </div>
                {c.resolution_notes && (
                  <div style={{ color: colors.textMuted, fontSize: "0.85rem", marginTop: "0.5rem" }}>
                    {c.resolution_notes}
                  </div>
                )}
              </div>
            ) : (
              <div style={{ color: colors.textMuted, fontSize: "0.85rem" }}>Unresolved</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
