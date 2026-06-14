import { useEffect, useReducer } from "react";
import { useNavigate } from "react-router-dom";
import { listConversations } from "../api/client";
import type { ConversationSummary } from "../api/types";
import ErrorState from "../components/ErrorState";
import LoadingState from "../components/LoadingState";
import { badge, btn, card, colors, pageTitle, td, th } from "../styles";

const STATUS_FILTERS = ["", "open", "waiting_for_customer", "escalated", "resolved"];
const STATUS_LABELS: Record<string, string> = {
  "": "All",
  open: "Open",
  waiting_for_customer: "Waiting",
  escalated: "Escalated",
  resolved: "Resolved",
};
const STATUS_COLORS: Record<string, string> = {
  open: colors.primary,
  waiting_for_customer: colors.warning,
  escalated: colors.danger,
  resolved: colors.success,
};

interface State {
  items: ConversationSummary[];
  total: number;
  page: number;
  statusFilter: string;
  loading: boolean;
  error: string;
}

type Action =
  | { type: "loading" }
  | { type: "loaded"; items: ConversationSummary[]; total: number }
  | { type: "error"; error: string }
  | { type: "filter"; statusFilter: string }
  | { type: "page"; page: number };

const reducer = (state: State, action: Action): State => {
  switch (action.type) {
    case "loading":
      return { ...state, loading: true, error: "" };
    case "loaded":
      return { ...state, items: action.items, total: action.total, loading: false };
    case "error":
      return { ...state, error: action.error, loading: false };
    case "filter":
      return { ...state, statusFilter: action.statusFilter, page: 1 };
    case "page":
      return { ...state, page: action.page };
  }
};

const initialState: State = {
  items: [],
  total: 0,
  page: 1,
  statusFilter: "",
  loading: true,
  error: "",
};

export default function ConversationsPage() {
  const [state, dispatch] = useReducer(reducer, initialState);
  const navigate = useNavigate();

  useEffect(() => {
    dispatch({ type: "loading" });
    listConversations({
      page: state.page,
      page_size: 20,
      status: state.statusFilter || undefined,
    })
      .then((r) => dispatch({ type: "loaded", items: r.items, total: r.total }))
      .catch((e) => dispatch({ type: "error", error: e.message }));
  }, [state.page, state.statusFilter]);

  if (state.loading) return <LoadingState />;
  if (state.error) return <ErrorState message={state.error} />;

  return (
    <div>
      <h1 style={pageTitle}>Conversations</h1>
      <div style={{ display: "flex", gap: "0.5rem", marginBottom: "1.5rem", flexWrap: "wrap" }}>
        {STATUS_FILTERS.map((s) => (
          <button
            key={s}
            onClick={() => dispatch({ type: "filter", statusFilter: s })}
            style={btn(state.statusFilter === s ? "primary" : "secondary")}
          >
            {STATUS_LABELS[s]}
          </button>
        ))}
        <span style={{ marginLeft: "auto", color: colors.textMuted, alignSelf: "center", fontSize: "0.85rem" }}>
          {state.total} conversations
        </span>
      </div>
      <div style={card}>
        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr>
                <th style={th}>Customer</th>
                <th style={th}>Channel</th>
                <th style={th}>Status</th>
                <th style={th}>Sentiment</th>
                <th style={th}>Subject</th>
                <th style={th}>Last Message</th>
                <th style={th}>Created</th>
              </tr>
            </thead>
            <tbody>
              {state.items.map((c) => (
                <tr
                  key={c.id}
                  onClick={() => navigate(`/conversations/${c.id}`)}
                  style={{ cursor: "pointer" }}
                >
                  <td style={td}>{c.customer_name || c.customer_email || "Anonymous"}</td>
                  <td style={td}><span style={badge(colors.primary)}>{c.channel}</span></td>
                  <td style={td}><span style={badge(STATUS_COLORS[c.status] || colors.textMuted)}>{STATUS_LABELS[c.status] || c.status}</span></td>
                  <td style={td}>{c.sentiment || "—"}</td>
                  <td style={td}>{c.subject || "—"}</td>
                  <td style={td}>{new Date(c.last_message_at).toLocaleString()}</td>
                  <td style={td}>{new Date(c.created_at).toLocaleString()}</td>
                </tr>
              ))}
              {state.items.length === 0 && (
                <tr>
                  <td colSpan={7} style={{ ...td, textAlign: "center", color: colors.textMuted, padding: "2rem" }}>
                    No conversations yet.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
        {state.total > 20 && (
          <div style={{ display: "flex", gap: "0.5rem", justifyContent: "center", padding: "1rem" }}>
            <button onClick={() => dispatch({ type: "page", page: Math.max(1, state.page - 1) })} disabled={state.page === 1} style={btn("secondary")}>Prev</button>
            <span style={{ alignSelf: "center", color: colors.textMuted, fontSize: "0.85rem" }}>Page {state.page}</span>
            <button onClick={() => dispatch({ type: "page", page: state.page + 1 })} disabled={state.items.length < 20} style={btn("secondary")}>Next</button>
          </div>
        )}
      </div>
    </div>
  );
}
