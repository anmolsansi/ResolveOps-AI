import { useReducer, useEffect } from "react";
import { getDashboardSummary, getAgentPerformance } from "../api/client";
import type { DashboardSummary, AgentPerformanceItem } from "../api/types";

interface State {
  summary: DashboardSummary | null;
  agents: AgentPerformanceItem[];
  timeRange: string;
  loading: boolean;
  error: string | null;
}

type Action =
  | { type: "LOAD_START" }
  | { type: "LOAD_DONE"; summary: DashboardSummary; agents: AgentPerformanceItem[] }
  | { type: "LOAD_ERROR"; error: string }
  | { type: "SET_RANGE"; value: string };

function reducer(state: State, action: Action): State {
  switch (action.type) {
    case "LOAD_START":
      return { ...state, loading: true, error: null };
    case "LOAD_DONE":
      return { ...state, loading: false, summary: action.summary, agents: action.agents };
    case "LOAD_ERROR":
      return { ...state, loading: false, error: action.error };
    case "SET_RANGE":
      return { ...state, timeRange: action.value };
    default:
      return state;
  }
}

export default function AnalyticsPage() {
  const [state, dispatch] = useReducer(reducer, {
    summary: null,
    agents: [],
    timeRange: "all",
    loading: true,
    error: null,
  });

  const load = () => {
    dispatch({ type: "LOAD_START" });
    Promise.all([
      getDashboardSummary(state.timeRange),
      getAgentPerformance(state.timeRange),
    ])
      .then(([summary, agents]) =>
        dispatch({ type: "LOAD_DONE", summary, agents: agents.items })
      )
      .catch((e) => dispatch({ type: "LOAD_ERROR", error: String(e) }));
  };

  useEffect(load, [state.timeRange]);

  const ranges = [
    { value: "all", label: "All Time" },
    { value: "7d", label: "Last 7 Days" },
    { value: "30d", label: "Last 30 Days" },
    { value: "90d", label: "Last 90 Days" },
  ];

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 24 }}>
        <div>
          <h2 style={{ margin: 0 }}>Analytics & Reporting</h2>
          <p style={{ color: "#666", fontSize: "0.875rem", margin: "4px 0 0" }}>
            Platform performance metrics and agent leaderboard.
          </p>
        </div>
        <div style={{ display: "flex", gap: 8 }}>
          {ranges.map((r) => (
            <button
              key={r.value}
              onClick={() => dispatch({ type: "SET_RANGE", value: r.value })}
              style={{
                padding: "6px 14px",
                borderRadius: 6,
                border: "1px solid #ddd",
                background: state.timeRange === r.value ? "#1976d2" : "#fff",
                color: state.timeRange === r.value ? "#fff" : "#333",
                cursor: "pointer",
                fontSize: "0.8rem",
                fontWeight: state.timeRange === r.value ? 600 : 400,
              }}
            >
              {r.label}
            </button>
          ))}
        </div>
      </div>

      {state.error && <div style={{ color: "#d32f2f", marginBottom: 16 }}>{state.error}</div>}

      {state.loading ? (
        <div style={{ color: "#999" }}>Loading...</div>
      ) : state.summary ? (
        <>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 16, marginBottom: 32 }}>
            {[
              { label: "Total Conversations", value: state.summary.total_conversations },
              { label: "Resolved", value: state.summary.resolved_conversations },
              { label: "Containment Rate", value: `${(state.summary.containment_rate * 100).toFixed(1)}%` },
              { label: "Avg Confidence", value: state.summary.avg_confidence.toFixed(3) },
              { label: "Open Conversations", value: state.summary.open_conversations },
              { label: "RAG Queries", value: state.summary.total_rag_queries },
              { label: "Tool Executions", value: state.summary.total_tool_executions },
              { label: "SLA Breaches", value: state.summary.sla_breach_count },
            ].map((card) => (
              <div
                key={card.label}
                style={{
                  padding: 20,
                  borderRadius: 8,
                  border: "1px solid #e0e0e0",
                  background: "#fafafa",
                }}
              >
                <div style={{ color: "#666", fontSize: "0.8rem", marginBottom: 4 }}>{card.label}</div>
                <div style={{ fontSize: "1.5rem", fontWeight: 700 }}>{card.value}</div>
              </div>
            ))}
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "2fr 1fr", gap: 24 }}>
            <div>
              <h3 style={{ fontSize: "1rem", marginBottom: 12 }}>Trend ({state.timeRange})</h3>
              <div style={{ display: "flex", gap: 2, alignItems: "end", height: 120, padding: 16, background: "#fafafa", borderRadius: 8, border: "1px solid #e0e0e0" }}>
                {state.summary.trend.map((t, i) => {
                  const maxVal = Math.max(...state.summary!.trend.map((x) => x.value), 1);
                  const height = (t.value / maxVal) * 80;
                  return (
                    <div key={i} style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", gap: 4 }}>
                      <span style={{ fontSize: "0.65rem", color: "#888" }}>{t.value}</span>
                      <div
                        style={{
                          width: "100%",
                          maxWidth: 24,
                          height: Math.max(height, 2),
                          background: "#1976d2",
                          borderRadius: 3,
                        }}
                      />
                      <span style={{ fontSize: "0.6rem", color: "#999" }}>{t.label}</span>
                    </div>
                  );
                })}
              </div>
            </div>

            <div>
              <h3 style={{ fontSize: "1rem", marginBottom: 12 }}>Tool Success Rate</h3>
              <div style={{ padding: 20, background: "#fafafa", borderRadius: 8, border: "1px solid #e0e0e0", textAlign: "center" }}>
                <div style={{ fontSize: "2rem", fontWeight: 700, color: state.summary.tool_success_rate > 0.8 ? "#2e7d32" : "#d32f2f" }}>
                  {(state.summary.tool_success_rate * 100).toFixed(1)}%
                </div>
                <div style={{ color: "#666", fontSize: "0.8rem" }}>
                  {state.summary.total_tool_executions} total executions
                </div>
              </div>
            </div>
          </div>

          {state.agents.length > 0 && (
            <div style={{ marginTop: 32 }}>
              <h3 style={{ fontSize: "1rem", marginBottom: 12 }}>Agent Leaderboard</h3>
              <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.875rem" }}>
                <thead>
                  <tr style={{ borderBottom: "2px solid #e0e0e0", textAlign: "left" }}>
                    <th style={{ padding: "8px 12px" }}>Agent</th>
                    <th style={{ padding: "8px 12px" }}>Conversations</th>
                    <th style={{ padding: "8px 12px" }}>Resolutions</th>
                    <th style={{ padding: "8px 12px" }}>Avg Time (s)</th>
                    <th style={{ padding: "8px 12px" }}>Satisfaction</th>
                  </tr>
                </thead>
                <tbody>
                  {state.agents.map((a) => (
                    <tr key={a.user_id} style={{ borderBottom: "1px solid #eee" }}>
                      <td style={{ padding: "8px 12px" }}>{a.email || a.user_id.slice(0, 8)}</td>
                      <td style={{ padding: "8px 12px" }}>{a.conversations_handled}</td>
                      <td style={{ padding: "8px 12px" }}>{a.resolutions}</td>
                      <td style={{ padding: "8px 12px" }}>{a.avg_resolution_time_seconds?.toFixed(0) ?? "-"}</td>
                      <td style={{ padding: "8px 12px" }}>{a.avg_satisfaction?.toFixed(1) ?? "-"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </>
      ) : null}
    </div>
  );
}
