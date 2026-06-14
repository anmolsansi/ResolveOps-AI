import { useEffect, useReducer } from "react";
import { useNavigate } from "react-router-dom";
import { listCustomers } from "../api/client";
import type { CustomerProfileResponse } from "../api/types";
import ErrorState from "../components/ErrorState";
import LoadingState from "../components/LoadingState";
import { badge, btn, card, colors, pageTitle, td, th } from "../styles";

interface State {
  items: CustomerProfileResponse[];
  total: number;
  page: number;
  loading: boolean;
  error: string;
}

type Action =
  | { type: "loading" }
  | { type: "loaded"; items: CustomerProfileResponse[]; total: number }
  | { type: "error"; error: string }
  | { type: "page"; page: number };

const reducer = (state: State, action: Action): State => {
  switch (action.type) {
    case "loading":
      return { ...state, loading: true, error: "" };
    case "loaded":
      return { ...state, items: action.items, total: action.total, loading: false };
    case "error":
      return { ...state, error: action.error, loading: false };
    case "page":
      return { ...state, page: action.page };
  }
};

const initialState: State = {
  items: [],
  total: 0,
  page: 1,
  loading: true,
  error: "",
};

export default function CustomersPage() {
  const [state, dispatch] = useReducer(reducer, initialState);
  const navigate = useNavigate();

  useEffect(() => {
    dispatch({ type: "loading" });
    listCustomers({ page: state.page, page_size: 20 })
      .then((r) => dispatch({ type: "loaded", items: r.items, total: r.total }))
      .catch((e) => dispatch({ type: "error", error: e.message }));
  }, [state.page]);

  if (state.loading) return <LoadingState />;
  if (state.error) return <ErrorState message={state.error} />;

  return (
    <div>
      <h1 style={pageTitle}>Customers</h1>
      <div style={card}>
        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr>
                <th style={th}>Name</th>
                <th style={th}>Email</th>
                <th style={th}>Tier</th>
                <th style={th}>Sentiment</th>
                <th style={th}>Conversations</th>
                <th style={th}>Unresolved</th>
                <th style={th}>Last Seen</th>
              </tr>
            </thead>
            <tbody>
              {state.items.map((c) => (
                <tr key={c.id} onClick={() => navigate(`/customers/${c.id}`)} style={{ cursor: "pointer" }}>
                  <td style={td}>{c.name || "—"}</td>
                  <td style={td}>{c.email || "—"}</td>
                  <td style={td}><span style={badge(colors.primary)}>{c.customer_tier}</span></td>
                  <td style={td}>{(c.sentiment_score * 100).toFixed(0)}%</td>
                  <td style={td}>{c.total_conversations}</td>
                  <td style={td}>{c.unresolved_issues > 0 ? <span style={badge(colors.danger)}>{String(c.unresolved_issues)}</span> : "0"}</td>
                  <td style={td}>{c.last_seen_at ? new Date(c.last_seen_at).toLocaleString() : "—"}</td>
                </tr>
              ))}
              {state.items.length === 0 && (
                <tr><td colSpan={7} style={{ ...td, textAlign: "center", color: colors.textMuted, padding: "2rem" }}>No customers yet.</td></tr>
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
