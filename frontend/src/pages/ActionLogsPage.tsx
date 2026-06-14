import { useEffect, useReducer } from "react";
import { useNavigate } from "react-router-dom";
import { listActionLogs, listToolExecutions } from "../api/client";
import type { ActionLogResponse, ToolExecutionResponse } from "../api/types";
import ErrorState from "../components/ErrorState";
import LoadingState from "../components/LoadingState";
import { badge, btn, card, colors, pageTitle, td, th } from "../styles";

type Tab = "executions" | "logs";

interface State {
  tab: Tab;
  executions: ToolExecutionResponse[];
  logs: ActionLogResponse[];
  loading: boolean;
  error: string;
}

type Action =
  | { type: "loading" }
  | { type: "loaded_executions"; executions: ToolExecutionResponse[] }
  | { type: "loaded_logs"; logs: ActionLogResponse[] }
  | { type: "error"; error: string }
  | { type: "tab"; tab: Tab };

const reducer = (state: State, action: Action): State => {
  switch (action.type) {
    case "loading":
      return { ...state, loading: true, error: "" };
    case "loaded_executions":
      return { ...state, executions: action.executions, loading: false };
    case "loaded_logs":
      return { ...state, logs: action.logs, loading: false };
    case "error":
      return { ...state, error: action.error, loading: false };
    case "tab":
      return { ...state, tab: action.tab };
  }
};

const initialState: State = {
  tab: "executions",
  executions: [],
  logs: [],
  loading: true,
  error: "",
};

const STATUS_COLORS: Record<string, string> = {
  succeeded: colors.success,
  failed: colors.danger,
  running: colors.warning,
  pending: colors.textMuted,
};

const ACTOR_COLORS: Record<string, string> = {
  ai_agent: colors.info,
  user: colors.primary,
};

export default function ActionLogsPage() {
  const [state, dispatch] = useReducer(reducer, initialState);
  const navigate = useNavigate();

  useEffect(() => {
    dispatch({ type: "loading" });
    if (state.tab === "executions") {
      listToolExecutions()
        .then((r) => dispatch({ type: "loaded_executions", executions: r.items }))
        .catch((e) => dispatch({ type: "error", error: e.message }));
    } else {
      listActionLogs()
        .then((r) => dispatch({ type: "loaded_logs", logs: r.items }))
        .catch((e) => dispatch({ type: "error", error: e.message }));
    }
  }, [state.tab]);

  if (state.loading && state.executions.length === 0 && state.logs.length === 0) {
    return <LoadingState />;
  }
  if (state.error && state.executions.length === 0 && state.logs.length === 0) {
    return <ErrorState message={state.error} />;
  }

  return (
    <div>
      <h1 style={pageTitle}>Action Logs</h1>
      <div style={{ display: "flex", gap: "0.5rem", marginBottom: "1.5rem" }}>
        <button
          onClick={() => dispatch({ type: "tab", tab: "executions" })}
          style={btn(state.tab === "executions" ? "primary" : "secondary")}
        >
          Tool Executions
        </button>
        <button
          onClick={() => dispatch({ type: "tab", tab: "logs" })}
          style={btn(state.tab === "logs" ? "primary" : "secondary")}
        >
          Action Audit Log
        </button>
      </div>

      {state.tab === "executions" && (
        <div style={card}>
          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse" }}>
              <thead>
                <tr>
                  <th style={th}>Tool</th>
                  <th style={th}>Status</th>
                  <th style={th}>Latency</th>
                  <th style={th}>Triggered By</th>
                  <th style={th}>Input</th>
                  <th style={th}>Time</th>
                </tr>
              </thead>
              <tbody>
                {state.executions.map((e) => (
                  <tr key={e.id} style={{ cursor: "pointer" }} onClick={() => navigate(`/tools/${e.tool_id}`)}>
                    <td style={td}>
                      <div style={{ fontWeight: 600 }}>{e.tool_name}</div>
                    </td>
                    <td style={td}>
                      <span style={badge(STATUS_COLORS[e.status] || colors.textMuted)}>
                        {e.status}
                      </span>
                    </td>
                    <td style={td}>
                      {e.latency_ms !== null ? `${e.latency_ms}ms` : "—"}
                    </td>
                    <td style={td}>
                      <span style={badge(ACTOR_COLORS[e.triggered_by] || colors.textMuted)}>
                        {e.triggered_by}
                      </span>
                    </td>
                    <td style={td}>
                      <code style={{ fontSize: "0.78rem" }}>
                        {JSON.stringify(e.input).slice(0, 60)}
                        {JSON.stringify(e.input).length > 60 ? "..." : ""}
                      </code>
                    </td>
                    <td style={td}>{new Date(e.created_at).toLocaleString()}</td>
                  </tr>
                ))}
                {state.executions.length === 0 && (
                  <tr>
                    <td colSpan={6} style={{ ...td, textAlign: "center", color: colors.textMuted, padding: "2rem" }}>
                      No tool executions yet. Execute a tool from the Tools page.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {state.tab === "logs" && (
        <div style={card}>
          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse" }}>
              <thead>
                <tr>
                  <th style={th}>Action</th>
                  <th style={th}>Resource</th>
                  <th style={th}>Actor</th>
                  <th style={th}>Detail</th>
                  <th style={th}>Time</th>
                </tr>
              </thead>
              <tbody>
                {state.logs.map((l) => (
                  <tr key={l.id}>
                    <td style={td}>
                      <code style={{ fontSize: "0.82rem" }}>{l.action_type}</code>
                    </td>
                    <td style={td}>
                      <span style={{ fontSize: "0.82rem" }}>{l.resource_type}</span>
                      {l.resource_id && (
                        <span style={{ color: colors.textMuted, fontSize: "0.75rem" }}>
                          {" "}{l.resource_id.slice(0, 8)}
                        </span>
                      )}
                    </td>
                    <td style={td}>
                      <span style={badge(ACTOR_COLORS[l.actor] || colors.textMuted)}>
                        {l.actor}
                      </span>
                    </td>
                    <td style={td}>
                      {l.detail ? (
                        <code style={{ fontSize: "0.78rem" }}>
                          {l.detail.slice(0, 80)}
                          {l.detail.length > 80 ? "..." : ""}
                        </code>
                      ) : "—"}
                    </td>
                    <td style={td}>{new Date(l.created_at).toLocaleString()}</td>
                  </tr>
                ))}
                {state.logs.length === 0 && (
                  <tr>
                    <td colSpan={5} style={{ ...td, textAlign: "center", color: colors.textMuted, padding: "2rem" }}>
                      No action logs yet.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
