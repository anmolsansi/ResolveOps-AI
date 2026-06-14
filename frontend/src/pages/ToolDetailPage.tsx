import { useEffect, useReducer } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { executeTool, getTool, updateTool } from "../api/client";
import type { ToolSummary, ToolExecutionResponse } from "../api/types";
import ErrorState from "../components/ErrorState";
import LoadingState from "../components/LoadingState";
import { badge, btn, card, colors, input, pageTitle } from "../styles";

interface State {
  tool: ToolSummary | null;
  loading: boolean;
  error: string;
  executing: boolean;
  lastResult: ToolExecutionResponse | null;
  paramValues: Record<string, string>;
}

type Action =
  | { type: "loading" }
  | { type: "loaded"; tool: ToolSummary }
  | { type: "error"; error: string }
  | { type: "executing"; executing: boolean }
  | { type: "result"; result: ToolExecutionResponse }
  | { type: "param"; key: string; value: string };

const reducer = (state: State, action: Action): State => {
  switch (action.type) {
    case "loading":
      return { ...state, loading: true, error: "" };
    case "loaded":
      return { ...state, tool: action.tool, loading: false };
    case "error":
      return { ...state, error: action.error, loading: false, executing: false };
    case "executing":
      return { ...state, executing: true, lastResult: null };
    case "result":
      return { ...state, lastResult: action.result, executing: false };
    case "param":
      return { ...state, paramValues: { ...state.paramValues, [action.key]: action.value } };
  }
};

const initialState: State = {
  tool: null,
  loading: true,
  error: "",
  executing: false,
  lastResult: null,
  paramValues: {},
};

export default function ToolDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [state, dispatch] = useReducer(reducer, initialState);

  useEffect(() => {
    if (!id) return;
    dispatch({ type: "loading" });
    getTool(id)
      .then((tool) => {
        dispatch({ type: "loaded", tool });
        const defaults: Record<string, string> = {};
        const schema = tool.parameters_schema as Record<string, unknown>;
        if (schema && typeof schema === "object" && "properties" in schema) {
          const props = schema.properties as Record<string, Record<string, unknown>>;
          for (const [k] of Object.entries(props)) {
            defaults[k] = "";
          }
        }
        dispatch({ type: "loaded", tool });
        Object.entries(defaults).forEach(([k, v]) => dispatch({ type: "param", key: k, value: v }));
      })
      .catch((e) => dispatch({ type: "error", error: e.message }));
  }, [id]);

  const handleExecute = async () => {
    if (!state.tool) return;
    dispatch({ type: "executing", executing: true });
    try {
      const params: Record<string, unknown> = {};
      for (const [k, v] of Object.entries(state.paramValues)) {
        if (v.trim()) params[k] = v.trim();
      }
      const result = await executeTool(state.tool.id, params);
      dispatch({ type: "result", result });
    } catch (e: unknown) {
      dispatch({ type: "error", error: e instanceof Error ? e.message : "Execution failed" });
    }
  };

  const handleToggle = async () => {
    if (!state.tool) return;
    try {
      const updated = await updateTool(state.tool.id, { enabled: !state.tool.enabled });
      dispatch({ type: "loaded", tool: updated });
    } catch (e: unknown) {
      dispatch({ type: "error", error: e instanceof Error ? e.message : "Toggle failed" });
    }
  };

  if (state.loading) return <LoadingState />;
  if (state.error && !state.tool) return <ErrorState message={state.error} />;
  if (!state.tool) return <ErrorState message="Tool not found" />;

  const t = state.tool;
  const schema = t.parameters_schema as Record<string, unknown>;
  const properties = (schema?.properties as Record<string, Record<string, unknown>>) || {};
  const required = ((schema?.required as string[]) || []);

  return (
    <div>
      <button
        onClick={() => navigate("/tools")}
        style={{ ...btn("secondary"), marginBottom: "1rem" }}
      >
        Back to Tools
      </button>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 360px", gap: "1.5rem" }}>
        <div>
          <h1 style={pageTitle}>{t.name}</h1>
          <div style={{ display: "flex", gap: "0.5rem", marginBottom: "1rem" }}>
            <span style={badge(t.enabled ? colors.success : colors.danger)}>
              {t.enabled ? "enabled" : "disabled"}
            </span>
            <span style={badge(colors.primary)}>{t.category}</span>
          </div>
          <p style={{ color: colors.text, marginBottom: "1.5rem", lineHeight: 1.6 }}>
            {t.description}
          </p>

          <div style={card}>
            <h3 style={{ margin: "0 0 1rem", color: colors.text }}>Parameters</h3>
            {Object.entries(properties).map(([key, prop]) => (
              <div key={key} style={{ marginBottom: "1rem" }}>
                <label style={{ display: "block", fontSize: "0.85rem", fontWeight: 600, marginBottom: "0.25rem", color: colors.text }}>
                  {key}
                  {required.includes(key) && <span style={{ color: colors.danger }}> *</span>}
                </label>
                {prop.description && (
                  <div style={{ fontSize: "0.78rem", color: colors.textMuted, marginBottom: "0.25rem" }}>
                    {String(prop.description)}
                  </div>
                )}
                {prop.enum ? (
                  <select
                    value={state.paramValues[key] || ""}
                    onChange={(e) => dispatch({ type: "param", key, value: e.target.value })}
                    style={{ ...input, width: "100%" }}
                  >
                    <option value="">Select...</option>
                    {(prop.enum as string[]).map((v) => (
                      <option key={v} value={v}>{v}</option>
                    ))}
                  </select>
                ) : (
                  <input
                    value={state.paramValues[key] || ""}
                    onChange={(e) => dispatch({ type: "param", key, value: e.target.value })}
                    placeholder={String(prop.description || key)}
                    style={{ ...input, width: "100%" }}
                  />
                )}
              </div>
            ))}
            {Object.keys(properties).length === 0 && (
              <div style={{ color: colors.textMuted, fontSize: "0.85rem" }}>No parameters required.</div>
            )}
            <div style={{ display: "flex", gap: "0.5rem", marginTop: "1rem" }}>
              <button onClick={handleExecute} disabled={state.executing || !t.enabled} style={btn("primary")}>
                {state.executing ? "Executing..." : "Execute Tool"}
              </button>
              <button onClick={handleToggle} style={btn("secondary")}>
                {t.enabled ? "Disable Tool" : "Enable Tool"}
              </button>
            </div>
          </div>

          {state.lastResult && (
            <div style={{ ...card, marginTop: "1rem" }}>
              <h3 style={{ margin: "0 0 0.75rem", color: colors.text }}>Execution Result</h3>
              <div style={{ display: "flex", gap: "0.5rem", marginBottom: "0.75rem" }}>
                <span style={badge(state.lastResult.status === "succeeded" ? colors.success : colors.danger)}>
                  {state.lastResult.status}
                </span>
                {state.lastResult.latency_ms !== null && (
                  <span style={badge(colors.info)}>{state.lastResult.latency_ms}ms</span>
                )}
              </div>
              {state.lastResult.error && (
                <div style={{ padding: "0.75rem", background: colors.danger + "15", borderRadius: 8, marginBottom: "0.75rem", color: colors.danger, fontSize: "0.85rem" }}>
                  {state.lastResult.error}
                </div>
              )}
              {state.lastResult.output && (
                <pre style={{ background: colors.bgSecondary, padding: "0.75rem", borderRadius: 8, fontSize: "0.82rem", overflow: "auto", color: colors.text }}>
                  {JSON.stringify(state.lastResult.output, null, 2)}
                </pre>
              )}
            </div>
          )}
        </div>

        <div>
          <div style={card}>
            <h3 style={{ margin: "0 0 0.75rem", color: colors.text }}>Tool Info</h3>
            <div style={{ fontSize: "0.85rem", color: colors.textMuted, marginBottom: "0.5rem" }}>
              <strong>Handler:</strong> <code>{t.handler}</code>
            </div>
            <div style={{ fontSize: "0.85rem", color: colors.textMuted, marginBottom: "0.5rem" }}>
              <strong>Slug:</strong> <code>{t.slug}</code>
            </div>
            <div style={{ fontSize: "0.85rem", color: colors.textMuted }}>
              <strong>Created:</strong> {new Date(t.created_at).toLocaleString()}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
