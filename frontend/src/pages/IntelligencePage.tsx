import { useEffect, useReducer } from "react";
import {
  detectKbSuggestions,
  getFeedbackSummary,
  getPerformanceMetrics,
  listCopilotSuggestions,
  listKbSuggestions,
  listSummaries,
  updateCopilotSuggestion,
  updateKbSuggestion,
} from "../api/client";
import type {
  CopilotSuggestionResponse,
  FeedbackSummaryResponse,
  KbSuggestionResponse,
  PerformanceMetricsResponse,
  ConversationSummaryResponse,
} from "../api/types";
import ErrorState from "../components/ErrorState";
import LoadingState from "../components/LoadingState";
import { badge, btn, card, colors, pageTitle } from "../styles";

type Tab = "overview" | "kb" | "copilot" | "summaries" | "feedback";

interface State {
  tab: Tab;
  metrics: PerformanceMetricsResponse | null;
  kbSuggestions: KbSuggestionResponse[];
  copilotSuggestions: CopilotSuggestionResponse[];
  summaries: ConversationSummaryResponse[];
  feedback: FeedbackSummaryResponse | null;
  loading: boolean;
  error: string;
}

type Action =
  | { type: "loading" }
  | { type: "tab"; tab: Tab }
  | { type: "metrics"; data: PerformanceMetricsResponse }
  | { type: "kb"; items: KbSuggestionResponse[] }
  | { type: "copilot"; items: CopilotSuggestionResponse[] }
  | { type: "summaries"; items: ConversationSummaryResponse[] }
  | { type: "feedback"; data: FeedbackSummaryResponse }
  | { type: "error"; error: string }
  | { type: "copilot_update"; id: string; status: string }
  | { type: "kb_update"; id: string; status: string };

const reducer = (state: State, action: Action): State => {
  switch (action.type) {
    case "loading":
      return { ...state, loading: true, error: "" };
    case "tab":
      return { ...state, tab: action.tab };
    case "metrics":
      return { ...state, metrics: action.data, loading: false };
    case "kb":
      return { ...state, kbSuggestions: action.items, loading: false };
    case "copilot":
      return { ...state, copilotSuggestions: action.items, loading: false };
    case "summaries":
      return { ...state, summaries: action.items, loading: false };
    case "feedback":
      return { ...state, feedback: action.data, loading: false };
    case "error":
      return { ...state, error: action.error, loading: false };
    case "copilot_update":
      return {
        ...state,
        copilotSuggestions: state.copilotSuggestions.map((s) =>
          s.id === action.id ? { ...s, status: action.status } : s,
        ),
      };
    case "kb_update":
      return {
        ...state,
        kbSuggestions: state.kbSuggestions.map((s) =>
          s.id === action.id ? { ...s, status: action.status } : s,
        ),
      };
  }
};

const initialState: State = {
  tab: "overview",
  metrics: null,
  kbSuggestions: [],
  copilotSuggestions: [],
  summaries: [],
  feedback: null,
  loading: true,
  error: "",
};

const SUGGESTION_COLORS: Record<string, string> = {
  next_best_action: colors.primary,
  related_ticket: colors.info,
  canned_response: colors.success,
  escalation_tip: colors.warning,
};

const STATUS_COLORS: Record<string, string> = {
  pending: colors.warning,
  accepted: colors.success,
  dismissed: colors.textMuted,
};

export default function IntelligencePage() {
  const [state, dispatch] = useReducer(reducer, initialState);

  useEffect(() => {
    dispatch({ type: "loading" });
    if (state.tab === "overview") {
      getPerformanceMetrics()
        .then((data) => dispatch({ type: "metrics", data }))
        .catch((e) => dispatch({ type: "error", error: e.message }));
    } else if (state.tab === "kb") {
      listKbSuggestions()
        .then((r) => dispatch({ type: "kb", items: r.items }))
        .catch((e) => dispatch({ type: "error", error: e.message }));
    } else if (state.tab === "copilot") {
      listCopilotSuggestions()
        .then((r) => dispatch({ type: "copilot", items: r.items }))
        .catch((e) => dispatch({ type: "error", error: e.message }));
    } else if (state.tab === "summaries") {
      listSummaries()
        .then((r) => dispatch({ type: "summaries", items: r.items }))
        .catch((e) => dispatch({ type: "error", error: e.message }));
    } else if (state.tab === "feedback") {
      getFeedbackSummary()
        .then((data) => dispatch({ type: "feedback", data }))
        .catch((e) => dispatch({ type: "error", error: e.message }));
    }
  }, [state.tab]);

  const handleDetectKb = async () => {
    dispatch({ type: "loading" });
    try {
      const r = await detectKbSuggestions();
      dispatch({ type: "kb", items: r.items });
    } catch (e: unknown) {
      dispatch({ type: "error", error: e instanceof Error ? e.message : "Detect failed" });
    }
  };

  const handleKbUpdate = async (id: string, status: string) => {
    try {
      await updateKbSuggestion(id, status);
      dispatch({ type: "kb_update", id, status });
    } catch (e: unknown) {
      dispatch({ type: "error", error: e instanceof Error ? e.message : "Update failed" });
    }
  };

  const handleCopilotUpdate = async (id: string, status: string) => {
    try {
      await updateCopilotSuggestion(id, status);
      dispatch({ type: "copilot_update", id, status });
    } catch (e: unknown) {
      dispatch({ type: "error", error: e instanceof Error ? e.message : "Update failed" });
    }
  };

  return (
    <div>
      <h1 style={pageTitle}>Agent Intelligence</h1>
      <div style={{ display: "flex", gap: "0.5rem", marginBottom: "1.5rem", flexWrap: "wrap" }}>
        {(["overview", "kb", "copilot", "summaries", "feedback"] as Tab[]).map((t) => (
          <button
            key={t}
            onClick={() => dispatch({ type: "tab", tab: t })}
            style={btn(state.tab === t ? "primary" : "secondary")}
          >
            {t === "overview" ? "Performance" : t === "kb" ? "KB Suggestions" : t === "copilot" ? "Copilot" : t === "summaries" ? "Summaries" : "Feedback"}
          </button>
        ))}
      </div>

      {state.loading && <LoadingState />}
      {state.error && !state.loading && <ErrorState message={state.error} />}

      {!state.loading && !state.error && state.tab === "overview" && state.metrics && (
        <OverviewTab metrics={state.metrics} />
      )}

      {!state.loading && !state.error && state.tab === "kb" && (
        <KbTab
          items={state.kbSuggestions}
          onDetect={handleDetectKb}
          onUpdate={handleKbUpdate}
        />
      )}

      {!state.loading && !state.error && state.tab === "copilot" && (
        <CopilotTab items={state.copilotSuggestions} onUpdate={handleCopilotUpdate} />
      )}

      {!state.loading && !state.error && state.tab === "summaries" && (
        <SummariesTab items={state.summaries} />
      )}

      {!state.loading && !state.error && state.tab === "feedback" && state.feedback && (
        <FeedbackTab data={state.feedback} />
      )}
    </div>
  );
}

function StatCard({ label, value, color }: { label: string; value: string | number; color?: string }) {
  return (
    <div style={{ ...card, textAlign: "center", minWidth: 140 }}>
      <div style={{ fontSize: "1.8rem", fontWeight: 700, color: color || colors.text }}>{value}</div>
      <div style={{ fontSize: "0.82rem", color: colors.textMuted, marginTop: "0.25rem" }}>{label}</div>
    </div>
  );
}

function OverviewTab({ metrics }: { metrics: PerformanceMetricsResponse }) {
  return (
    <div>
      <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap", marginBottom: "1.5rem" }}>
        <StatCard label="Total Conversations" value={metrics.total_conversations} />
        <StatCard label="Resolved" value={metrics.resolved_conversations} color={colors.success} />
        <StatCard label="AI Contained" value={metrics.ai_contained} color={colors.info} />
        <StatCard label="Human Escalated" value={metrics.human_escalated} color={colors.danger} />
        <StatCard label="Containment Rate" value={`${metrics.containment_rate}%`} color={colors.success} />
        <StatCard label="Tool Executions" value={metrics.total_tool_executions} />
        <StatCard label="Tool Success Rate" value={`${metrics.tool_success_rate}%`} color={colors.success} />
      </div>

      {metrics.average_resolution_time_seconds !== null && (
        <div style={{ ...card, marginBottom: "1rem" }}>
          <h3 style={{ margin: "0 0 0.5rem", color: colors.text }}>Avg Resolution Time</h3>
          <span style={{ fontSize: "1.2rem", fontWeight: 600 }}>
            {Math.round(metrics.average_resolution_time_seconds)}s
          </span>
        </div>
      )}

      {metrics.tool_usage.length > 0 && (
        <div style={{ ...card, marginBottom: "1rem" }}>
          <h3 style={{ margin: "0 0 0.75rem", color: colors.text }}>Tool Usage</h3>
          {metrics.tool_usage.map((t) => (
            <div key={t.slug} style={{ display: "flex", justifyContent: "space-between", padding: "0.5rem 0", borderBottom: `1px solid ${colors.border}` }}>
              <span style={{ fontWeight: 500 }}>{t.tool_name}</span>
              <span style={{ color: colors.textMuted, fontSize: "0.85rem" }}>
                {t.total_executions} runs | {t.success_count} ok | {Math.round(t.average_latency_ms)}ms avg
              </span>
            </div>
          ))}
        </div>
      )}

      {Object.keys(metrics.sentiment_distribution).length > 0 && (
        <div style={{ ...card, marginBottom: "1rem" }}>
          <h3 style={{ margin: "0 0 0.75rem", color: colors.text }}>Sentiment Distribution</h3>
          <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
            {Object.entries(metrics.sentiment_distribution).map(([s, count]) => (
              <span key={s} style={badge(colors.primary)}>{s}: {count}</span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function KbTab({
  items,
  onDetect,
  onUpdate,
}: {
  items: KbSuggestionResponse[];
  onDetect: () => void;
  onUpdate: (id: string, status: string) => void;
}) {
  return (
    <div>
      <div style={{ marginBottom: "1rem" }}>
        <button onClick={onDetect} style={btn("primary")}>Detect New Suggestions</button>
      </div>
      {items.length === 0 ? (
        <div style={{ ...card, textAlign: "center", padding: "3rem", color: colors.textMuted }}>
          No KB suggestions yet. Click "Detect" to analyze conversations for article patterns.
        </div>
      ) : (
        items.map((s) => (
          <div key={s.id} style={{ ...card, marginBottom: "1rem" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
              <div>
                <h3 style={{ margin: "0 0 0.5rem", color: colors.text }}>{s.suggested_title}</h3>
                <p style={{ margin: "0 0 0.5rem", color: colors.textMuted, fontSize: "0.88rem" }}>
                  {s.suggested_content}
                </p>
                <div style={{ display: "flex", gap: "0.5rem" }}>
                  {s.product_area && <span style={badge(colors.primary)}>{s.product_area}</span>}
                  <span style={badge(colors.info)}>{s.occurrence_count} conversations</span>
                  <span style={badge(STATUS_COLORS[s.status] || colors.textMuted)}>{s.status}</span>
                </div>
              </div>
              {s.status === "pending" && (
                <div style={{ display: "flex", gap: "0.5rem" }}>
                  <button onClick={() => onUpdate(s.id, "accepted")} style={btn("primary")}>Accept</button>
                  <button onClick={() => onUpdate(s.id, "dismissed")} style={btn("secondary")}>Dismiss</button>
                </div>
              )}
            </div>
          </div>
        ))
      )}
    </div>
  );
}

function CopilotTab({
  items,
  onUpdate,
}: {
  items: CopilotSuggestionResponse[];
  onUpdate: (id: string, status: string) => void;
}) {
  return (
    <div>
      {items.length === 0 ? (
        <div style={{ ...card, textAlign: "center", padding: "3rem", color: colors.textMuted }}>
          No copilot suggestions yet. Generate suggestions to get started.
        </div>
      ) : (
        items.map((s) => (
          <div key={s.id} style={{ ...card, marginBottom: "1rem", borderLeft: `4px solid ${SUGGESTION_COLORS[s.suggestion_type] || colors.border}` }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
              <div>
                <div style={{ display: "flex", gap: "0.5rem", marginBottom: "0.5rem" }}>
                  <span style={badge(SUGGESTION_COLORS[s.suggestion_type] || colors.textMuted)}>
                    {s.suggestion_type.replace(/_/g, " ")}
                  </span>
                  <span style={badge(STATUS_COLORS[s.status] || colors.textMuted)}>{s.status}</span>
                  <span style={{ fontSize: "0.78rem", color: colors.textMuted }}>
                    {Math.round(s.confidence * 100)}% confidence
                  </span>
                </div>
                <h3 style={{ margin: "0 0 0.5rem", color: colors.text }}>{s.title}</h3>
                <p style={{ margin: 0, color: colors.textMuted, fontSize: "0.88rem" }}>{s.content}</p>
              </div>
              {s.status === "pending" && (
                <div style={{ display: "flex", gap: "0.5rem" }}>
                  <button onClick={() => onUpdate(s.id, "accepted")} style={btn("primary")}>Accept</button>
                  <button onClick={() => onUpdate(s.id, "dismissed")} style={btn("secondary")}>Dismiss</button>
                </div>
              )}
            </div>
          </div>
        ))
      )}
    </div>
  );
}

function SummariesTab({ items }: { items: ConversationSummaryResponse[] }) {
  return (
    <div>
      {items.length === 0 ? (
        <div style={{ ...card, textAlign: "center", padding: "3rem", color: colors.textMuted }}>
          No conversation summaries yet. Summaries are generated when conversations are resolved.
        </div>
      ) : (
        items.map((s) => (
          <div key={s.id} style={{ ...card, marginBottom: "1rem" }}>
            <div style={{ display: "flex", gap: "0.5rem", marginBottom: "0.5rem" }}>
              {s.sentiment_at_resolution && (
                <span style={badge(colors.primary)}>{s.sentiment_at_resolution}</span>
              )}
              {s.key_topics.slice(0, 3).map((t) => (
                <span key={t} style={badge(colors.info)}>{t}</span>
              ))}
            </div>
            <p style={{ margin: "0 0 0.5rem", color: colors.text }}>{s.summary}</p>
            {s.resolution_steps && (
              <pre style={{ background: colors.bgSecondary, padding: "0.75rem", borderRadius: 8, fontSize: "0.82rem", whiteSpace: "pre-wrap", color: colors.textMuted }}>
                {s.resolution_steps}
              </pre>
            )}
            <div style={{ fontSize: "0.78rem", color: colors.textMuted, marginTop: "0.5rem" }}>
              {new Date(s.created_at).toLocaleString()}
            </div>
          </div>
        ))
      )}
    </div>
  );
}

function FeedbackTab({ data }: { data: FeedbackSummaryResponse }) {
  return (
    <div>
      <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap", marginBottom: "1.5rem" }}>
        <StatCard label="Total Feedback" value={data.total_feedback} />
        <StatCard label="Positive" value={data.positive_count} color={colors.success} />
        <StatCard label="Negative" value={data.negative_count} color={colors.danger} />
        <StatCard label="Satisfaction Rate" value={`${data.satisfaction_rate}%`} color={colors.success} />
      </div>

      {data.top_issues.length > 0 && (
        <div style={{ ...card, marginBottom: "1rem" }}>
          <h3 style={{ margin: "0 0 0.75rem", color: colors.text }}>Top Issues</h3>
          {data.top_issues.map((issue) => (
            <div key={issue.reason} style={{ display: "flex", justifyContent: "space-between", padding: "0.5rem 0", borderBottom: `1px solid ${colors.border}` }}>
              <span>{issue.reason}</span>
              <span style={badge(colors.danger)}>{issue.count}</span>
            </div>
          ))}
        </div>
      )}

      {data.improvement_areas.length > 0 && (
        <div style={card}>
          <h3 style={{ margin: "0 0 0.75rem", color: colors.text }}>Improvement Areas</h3>
          {data.improvement_areas.map((area, i) => (
            <div key={i} style={{ padding: "0.5rem 0", borderBottom: `1px solid ${colors.border}`, color: colors.text }}>
              {area}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
