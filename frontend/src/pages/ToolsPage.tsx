import { useEffect, useReducer } from "react";
import { useNavigate } from "react-router-dom";
import { listTools, updateTool } from "../api/client";
import type { ToolSummary } from "../api/types";
import ErrorState from "../components/ErrorState";
import LoadingState from "../components/LoadingState";
import { badge, btn, card, colors, pageTitle, td, th } from "../styles";

const CATEGORY_COLORS: Record<string, string> = {
  tickets: colors.primary,
  customers: colors.warning,
  knowledge: colors.success,
  operations: colors.info,
  general: colors.textMuted,
};

interface State {
  items: ToolSummary[];
  loading: boolean;
  error: string;
}

type Action =
  | { type: "loading" }
  | { type: "loaded"; items: ToolSummary[] }
  | { type: "error"; error: string }
  | { type: "toggled"; id: string; enabled: boolean };

const reducer = (state: State, action: Action): State => {
  switch (action.type) {
    case "loading":
      return { ...state, loading: true, error: "" };
    case "loaded":
      return { ...state, items: action.items, loading: false };
    case "error":
      return { ...state, error: action.error, loading: false };
    case "toggled":
      return {
        ...state,
        items: state.items.map((t) =>
          t.id === action.id ? { ...t, enabled: action.enabled } : t,
        ),
      };
  }
};

const initialState: State = { items: [], loading: true, error: "" };

export default function ToolsPage() {
  const [state, dispatch] = useReducer(reducer, initialState);
  const navigate = useNavigate();

  useEffect(() => {
    dispatch({ type: "loading" });
    listTools()
      .then((r) => dispatch({ type: "loaded", items: r.items }))
      .catch((e) => dispatch({ type: "error", error: e.message }));
  }, []);

  const toggleTool = async (tool: ToolSummary) => {
    try {
      await updateTool(tool.id, { enabled: !tool.enabled });
      dispatch({ type: "toggled", id: tool.id, enabled: !tool.enabled });
    } catch (e: unknown) {
      dispatch({ type: "error", error: e instanceof Error ? e.message : "Toggle failed" });
    }
  };

  if (state.loading) return <LoadingState />;
  if (state.error) return <ErrorState message={state.error} />;

  return (
    <div>
      <h1 style={pageTitle}>Agent Tools</h1>
      <p style={{ color: colors.textMuted, marginBottom: "1.5rem", fontSize: "0.9rem" }}>
        Manage tools the AI agent can use to take actions. Disable tools you don't want the agent to invoke.
      </p>
      <div style={card}>
        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr>
                <th style={th}>Tool</th>
                <th style={th}>Category</th>
                <th style={th}>Handler</th>
                <th style={th}>Status</th>
                <th style={th}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {state.items.map((t) => (
                <tr
                  key={t.id}
                  style={{ cursor: "pointer" }}
                  onClick={() => navigate(`/tools/${t.id}`)}
                >
                  <td style={td}>
                    <div style={{ fontWeight: 600 }}>{t.name}</div>
                    <div style={{ fontSize: "0.78rem", color: colors.textMuted, maxWidth: 400 }}>
                      {t.description.slice(0, 100)}...
                    </div>
                  </td>
                  <td style={td}>
                    <span style={badge(CATEGORY_COLORS[t.category] || colors.textMuted)}>
                      {t.category}
                    </span>
                  </td>
                  <td style={td}><code style={{ fontSize: "0.82rem" }}>{t.handler}</code></td>
                  <td style={td}>
                    <span style={badge(t.enabled ? colors.success : colors.danger)}>
                      {t.enabled ? "enabled" : "disabled"}
                    </span>
                  </td>
                  <td style={td} onClick={(e) => e.stopPropagation()}>
                    <button
                      onClick={() => toggleTool(t)}
                      style={btn(t.enabled ? "secondary" : "primary")}
                    >
                      {t.enabled ? "Disable" : "Enable"}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
