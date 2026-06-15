import { useEffect, useReducer } from "react";
import {
  generateCopilotSuggestions,
  listCopilotSuggestions,
  updateCopilotSuggestion,
} from "../api/client";
import type { CopilotSuggestionResponse } from "../api/types";
import ErrorState from "../components/ErrorState";
import LoadingState from "../components/LoadingState";
import { badge, btn, card, colors, pageTitle } from "../styles";

const TYPE_COLORS: Record<string, string> = {
  next_best_action: colors.primary,
  related_ticket: colors.info,
  canned_response: colors.success,
  escalation_tip: colors.warning,
};

interface State {
  items: CopilotSuggestionResponse[];
  loading: boolean;
  error: string;
  generating: boolean;
}

type Action =
  | { type: "loading" }
  | { type: "loaded"; items: CopilotSuggestionResponse[] }
  | { type: "error"; error: string }
  | { type: "generating"; generating: boolean }
  | { type: "update"; id: string; status: string };

const reducer = (state: State, action: Action): State => {
  switch (action.type) {
    case "loading":
      return { ...state, loading: true, error: "" };
    case "loaded":
      return { ...state, items: action.items, loading: false };
    case "error":
      return { ...state, error: action.error, loading: false, generating: false };
    case "generating":
      return { ...state, generating: action.generating };
    case "update":
      return {
        ...state,
        items: state.items.map((s) =>
          s.id === action.id ? { ...s, status: action.status } : s,
        ),
      };
  }
};

const initialState: State = { items: [], loading: true, error: "", generating: false };

export default function CopilotPage() {
  const [state, dispatch] = useReducer(reducer, initialState);

  useEffect(() => {
    dispatch({ type: "loading" });
    listCopilotSuggestions()
      .then((r) => dispatch({ type: "loaded", items: r.items }))
      .catch((e) => dispatch({ type: "error", error: e.message }));
  }, []);

  const handleGenerate = async () => {
    dispatch({ type: "generating", generating: true });
    try {
      const r = await generateCopilotSuggestions();
      dispatch({ type: "loaded", items: r.items });
      dispatch({ type: "generating", generating: false });
    } catch (e: unknown) {
      dispatch({ type: "error", error: e instanceof Error ? e.message : "Generate failed" });
    }
  };

  const handleUpdate = async (id: string, status: string) => {
    try {
      await updateCopilotSuggestion(id, status);
      dispatch({ type: "update", id, status });
    } catch (e: unknown) {
      dispatch({ type: "error", error: e instanceof Error ? e.message : "Update failed" });
    }
  };

  if (state.loading) return <LoadingState />;
  if (state.error) return <ErrorState message={state.error} />;

  const pending = state.items.filter((s) => s.status === "pending");
  const completed = state.items.filter((s) => s.status !== "pending");

  return (
    <div>
      <h1 style={pageTitle}>AI Copilot</h1>
      <div style={{ display: "flex", gap: "0.75rem", marginBottom: "1.5rem", alignItems: "center" }}>
        <button onClick={handleGenerate} disabled={state.generating} style={btn("primary")}>
          {state.generating ? "Generating..." : "Generate Suggestions"}
        </button>
        <span style={{ color: colors.textMuted, fontSize: "0.85rem" }}>
          {pending.length} pending | {completed.length} actioned
        </span>
      </div>

      {state.items.length === 0 ? (
        <div style={{ ...card, textAlign: "center", padding: "3rem" }}>
          <div style={{ fontSize: "2rem", marginBottom: "1rem" }}>0</div>
          <p style={{ color: colors.textMuted }}>No suggestions yet. Click "Generate Suggestions" to get started.</p>
        </div>
      ) : (
        <>
          {pending.length > 0 && (
            <div style={{ marginBottom: "2rem" }}>
              <h2 style={{ fontSize: "1.1rem", color: colors.text, marginBottom: "1rem" }}>
                Pending ({pending.length})
              </h2>
              {pending.map((s) => (
                <CopilotCard key={s.id} suggestion={s} onUpdate={handleUpdate} />
              ))}
            </div>
          )}
          {completed.length > 0 && (
            <div>
              <h2 style={{ fontSize: "1.1rem", color: colors.textMuted, marginBottom: "1rem" }}>
                Actioned ({completed.length})
              </h2>
              {completed.map((s) => (
                <CopilotCard key={s.id} suggestion={s} onUpdate={handleUpdate} />
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}

function CopilotCard({
  suggestion,
  onUpdate,
}: {
  suggestion: CopilotSuggestionResponse;
  onUpdate: (id: string, status: string) => void;
}) {
  const s = suggestion;
  return (
    <div
      style={{
        ...card,
        marginBottom: "1rem",
        borderLeft: `4px solid ${TYPE_COLORS[s.suggestion_type] || colors.border}`,
        opacity: s.status === "dismissed" ? 0.6 : 1,
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <div style={{ flex: 1 }}>
          <div style={{ display: "flex", gap: "0.5rem", marginBottom: "0.5rem", alignItems: "center" }}>
            <span style={badge(TYPE_COLORS[s.suggestion_type] || colors.textMuted)}>
              {s.suggestion_type.replace(/_/g, " ")}
            </span>
            <span style={badge(s.status === "accepted" ? colors.success : s.status === "dismissed" ? colors.textMuted : colors.warning)}>
              {s.status}
            </span>
            <span style={{ fontSize: "0.78rem", color: colors.textMuted }}>
              {Math.round(s.confidence * 100)}% confidence
            </span>
          </div>
          <h3 style={{ margin: "0 0 0.5rem", color: colors.text }}>{s.title}</h3>
          <p style={{ margin: 0, color: colors.textMuted, fontSize: "0.88rem", lineHeight: 1.5 }}>
            {s.content}
          </p>
        </div>
        {s.status === "pending" && (
          <div style={{ display: "flex", gap: "0.5rem", marginLeft: "1rem" }}>
            <button onClick={() => onUpdate(s.id, "accepted")} style={btn("primary")}>
              Accept
            </button>
            <button onClick={() => onUpdate(s.id, "dismissed")} style={btn("secondary")}>
              Dismiss
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
