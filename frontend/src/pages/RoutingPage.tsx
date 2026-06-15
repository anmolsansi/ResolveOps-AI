import { useReducer, useEffect } from "react";
import { listRouting, createRouting, updateRouting, deleteRouting } from "../api/client";
import type { RoutingRuleResponse } from "../api/types";

interface State {
  items: RoutingRuleResponse[];
  loading: boolean;
  error: string | null;
  editingId: string | null;
  form: { name: string; description: string; priority: number; conditions: string; actions: string };
}

type Action =
  | { type: "LOAD_START" }
  | { type: "LOAD_DONE"; items: RoutingRuleResponse[] }
  | { type: "LOAD_ERROR"; error: string }
  | { type: "TOGGLE_EDIT"; id?: string | null }
  | { type: "SET_FORM"; field: string; value: string }
  | { type: "SAVED"; items: RoutingRuleResponse[] };

const emptyForm = { name: "", description: "", priority: 100, conditions: "{}", actions: "{}" };

function reducer(state: State, action: Action): State {
  switch (action.type) {
    case "LOAD_START":
      return { ...state, loading: true, error: null };
    case "LOAD_DONE":
      return { ...state, loading: false, items: action.items };
    case "LOAD_ERROR":
      return { ...state, loading: false, error: action.error };
    case "TOGGLE_EDIT":
      if (action.id) {
        const item = state.items.find((i) => i.id === action.id);
        if (item) {
          return {
            ...state,
            editingId: action.id,
            form: {
              name: item.name,
              description: item.description || "",
              priority: item.priority,
              conditions: JSON.stringify(item.conditions, null, 2),
              actions: JSON.stringify(item.actions, null, 2),
            },
          };
        }
      }
      return { ...state, editingId: null, form: emptyForm };
    case "SET_FORM":
      return { ...state, form: { ...state.form, [action.field]: action.value } };
    case "SAVED":
      return { ...state, editingId: null, form: emptyForm, items: action.items };
    default:
      return state;
  }
}

export default function RoutingPage() {
  const [state, dispatch] = useReducer(reducer, {
    items: [],
    loading: true,
    error: null,
    editingId: null,
    form: emptyForm,
  });

  const load = () => {
    dispatch({ type: "LOAD_START" });
    listRouting()
      .then((r) => dispatch({ type: "LOAD_DONE", items: r.items }))
      .catch((e) => dispatch({ type: "LOAD_ERROR", error: String(e) }));
  };

  useEffect(load, []);

  const handleSave = async () => {
    try {
      const conditions = JSON.parse(state.form.conditions);
      const actions = JSON.parse(state.form.actions);
      if (state.editingId) {
        await updateRouting(state.editingId, {
          name: state.form.name,
          description: state.form.description,
          priority: state.form.priority,
          conditions,
          actions,
        });
      } else {
        await createRouting({
          name: state.form.name,
          description: state.form.description,
          priority: state.form.priority,
          conditions,
          actions,
        });
      }
      load();
    } catch (e) {
      dispatch({ type: "LOAD_ERROR", error: String(e) });
    }
  };

  const handleDelete = async (id: string) => {
    await deleteRouting(id);
    load();
  };

  const handleToggle = async (id: string, enabled: boolean) => {
    await updateRouting(id, { enabled: !enabled });
    load();
  };

  return (
    <div>
      <h2>Routing Rules</h2>
      <p style={{ color: "#666", fontSize: "0.875rem" }}>
        Define rules to automatically route incoming conversations based on product area, sentiment, or channel.
      </p>
      {state.error && <div style={{ color: "#d32f2f", marginBottom: 16 }}>{state.error}</div>}
      <div style={{ display: "flex", gap: 16, alignItems: "start" }}>
        <div style={{ flex: 2 }}>
          {state.loading ? (
            <div style={{ color: "#999" }}>Loading...</div>
          ) : (
            <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.875rem" }}>
              <thead>
                <tr style={{ borderBottom: "2px solid #e0e0e0", textAlign: "left" }}>
                  <th style={{ padding: "8px 12px" }}>Name</th>
                  <th style={{ padding: "8px 12px" }}>Priority</th>
                  <th style={{ padding: "8px 12px" }}>Enabled</th>
                  <th style={{ padding: "8px 12px" }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {state.items.map((item) => (
                  <tr key={item.id} style={{ borderBottom: "1px solid #eee" }}>
                    <td style={{ padding: "8px 12px" }}>
                      <strong>{item.name}</strong>
                      {item.description && (
                        <div style={{ color: "#888", fontSize: "0.8rem" }}>{item.description}</div>
                      )}
                    </td>
                    <td style={{ padding: "8px 12px" }}>{item.priority}</td>
                    <td style={{ padding: "8px 12px" }}>
                      <button
                        onClick={() => handleToggle(item.id, item.enabled)}
                        style={{
                          background: item.enabled ? "#4caf50" : "#ccc",
                          color: "#fff",
                          border: "none",
                          padding: "4px 12px",
                          borderRadius: 4,
                          cursor: "pointer",
                        }}
                      >
                        {item.enabled ? "On" : "Off"}
                      </button>
                    </td>
                    <td style={{ padding: "8px 12px" }}>
                      <button
                        onClick={() => dispatch({ type: "TOGGLE_EDIT", id: item.id })}
                        style={{ background: "none", border: "none", color: "#1976d2", cursor: "pointer", marginRight: 8 }}
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => handleDelete(item.id)}
                        style={{ background: "none", border: "none", color: "#d32f2f", cursor: "pointer" }}
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
                {state.items.length === 0 && (
                  <tr>
                    <td colSpan={4} style={{ padding: 16, color: "#999", textAlign: "center" }}>
                      No routing rules yet. Create one to get started.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          )}
        </div>
        <div style={{ flex: 1, padding: 16, border: "1px solid #e0e0e0", borderRadius: 8, background: "#fafafa" }}>
          <h3 style={{ marginTop: 0, fontSize: "1rem" }}>{state.editingId ? "Edit Rule" : "New Rule"}</h3>
          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            <input
              placeholder="Name"
              value={state.form.name}
              onChange={(e) => dispatch({ type: "SET_FORM", field: "name", value: e.target.value })}
              style={{ padding: "8px 12px", borderRadius: 4, border: "1px solid #ddd" }}
            />
            <input
              placeholder="Description"
              value={state.form.description}
              onChange={(e) => dispatch({ type: "SET_FORM", field: "description", value: e.target.value })}
              style={{ padding: "8px 12px", borderRadius: 4, border: "1px solid #ddd" }}
            />
            <label style={{ fontSize: "0.8rem", color: "#666" }}>
              Priority
              <input
                type="number"
                value={state.form.priority}
                onChange={(e) => dispatch({ type: "SET_FORM", field: "priority", value: e.target.value })}
                style={{ marginLeft: 8, padding: "4px 8px", borderRadius: 4, border: "1px solid #ddd", width: 80 }}
              />
            </label>
            <div>
              <label style={{ fontSize: "0.8rem", color: "#666", display: "block", marginBottom: 4 }}>Conditions (JSON)</label>
              <textarea
                rows={4}
                value={state.form.conditions}
                onChange={(e) => dispatch({ type: "SET_FORM", field: "conditions", value: e.target.value })}
                style={{ width: "100%", padding: 8, borderRadius: 4, border: "1px solid #ddd", fontFamily: "monospace", fontSize: "0.8rem" }}
              />
            </div>
            <div>
              <label style={{ fontSize: "0.8rem", color: "#666", display: "block", marginBottom: 4 }}>Actions (JSON)</label>
              <textarea
                rows={3}
                value={state.form.actions}
                onChange={(e) => dispatch({ type: "SET_FORM", field: "actions", value: e.target.value })}
                style={{ width: "100%", padding: 8, borderRadius: 4, border: "1px solid #ddd", fontFamily: "monospace", fontSize: "0.8rem" }}
              />
            </div>
            <div style={{ display: "flex", gap: 8 }}>
              <button
                onClick={handleSave}
                disabled={!state.form.name}
                style={{
                  padding: "8px 20px",
                  borderRadius: 4,
                  border: "none",
                  background: state.form.name ? "#1976d2" : "#ccc",
                  color: "#fff",
                  cursor: state.form.name ? "pointer" : "default",
                  fontWeight: 600,
                }}
              >
                {state.editingId ? "Update" : "Create"}
              </button>
              {state.editingId && (
                <button
                  onClick={() => dispatch({ type: "TOGGLE_EDIT" })}
                  style={{ padding: "8px 20px", borderRadius: 4, border: "1px solid #ddd", background: "#fff", cursor: "pointer" }}
                >
                  Cancel
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
