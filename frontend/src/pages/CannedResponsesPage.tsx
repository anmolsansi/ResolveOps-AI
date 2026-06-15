import { useReducer, useEffect } from "react";
import {
  listCannedResponses,
  createCannedResponse,
  updateCannedResponse,
  deleteCannedResponse,
  incrementCannedResponseUsage,
  searchCannedResponses,
} from "../api/client";
import type { CannedResponse } from "../api/types";

interface State {
  items: CannedResponse[];
  loading: boolean;
  error: string | null;
  editingId: string | null;
  search: string;
  form: { title: string; content: string; category: string; shortcut: string };
}

type Action =
  | { type: "LOAD_START" }
  | { type: "LOAD_DONE"; items: CannedResponse[] }
  | { type: "LOAD_ERROR"; error: string }
  | { type: "TOGGLE_EDIT"; id?: string | null }
  | { type: "SET_FORM"; field: string; value: string }
  | { type: "SET_SEARCH"; value: string }
  | { type: "SAVED"; items: CannedResponse[] };

const emptyForm = { title: "", content: "", category: "", shortcut: "" };

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
            form: { title: item.title, content: item.content, category: item.category || "", shortcut: item.shortcut || "" },
          };
        }
      }
      return { ...state, editingId: null, form: emptyForm };
    case "SET_FORM":
      return { ...state, form: { ...state.form, [action.field]: action.value } };
    case "SET_SEARCH":
      return { ...state, search: action.value };
    case "SAVED":
      return { ...state, editingId: null, form: emptyForm, items: action.items };
    default:
      return state;
  }
}

export default function CannedResponsesPage() {
  const [state, dispatch] = useReducer(reducer, {
    items: [],
    loading: true,
    error: null,
    editingId: null,
    search: "",
    form: emptyForm,
  });

  const load = (q?: string) => {
    dispatch({ type: "LOAD_START" });
    const p = q ? searchCannedResponses(q) : listCannedResponses();
    p.then((r) => dispatch({ type: "LOAD_DONE", items: r.items }))
      .catch((e) => dispatch({ type: "LOAD_ERROR", error: String(e) }));
  };

  useEffect(() => load(), []);

  const handleSave = async () => {
    try {
      if (state.editingId) {
        await updateCannedResponse(state.editingId, state.form);
      } else {
        await createCannedResponse(state.form);
      }
      load();
    } catch (e) {
      dispatch({ type: "LOAD_ERROR", error: String(e) });
    }
  };

  const handleDelete = async (id: string) => {
    await deleteCannedResponse(id);
    load();
  };

  const handleUse = async (id: string) => {
    const result = await incrementCannedResponseUsage(id);
    dispatch({ type: "LOAD_DONE", items: state.items.map((i) => (i.id === id ? { ...i, usage_count: result.usage_count } : i)) });
  };

  const handleSearch = () => {
    load(state.search || undefined);
  };

  return (
    <div>
      <h2>Canned Responses</h2>
      <p style={{ color: "#666", fontSize: "0.875rem" }}>
        Manage pre-written responses for common questions. Use the shortcut prefix to quickly insert them.
      </p>
      {state.error && <div style={{ color: "#d32f2f", marginBottom: 16 }}>{state.error}</div>}
      <div style={{ display: "flex", gap: 16, alignItems: "start" }}>
        <div style={{ flex: 2 }}>
          <div style={{ display: "flex", gap: 8, marginBottom: 16 }}>
            <input
              placeholder="Search responses..."
              value={state.search}
              onChange={(e) => dispatch({ type: "SET_SEARCH", value: e.target.value })}
              onKeyDown={(e) => e.key === "Enter" && handleSearch()}
              style={{ flex: 1, padding: "8px 12px", borderRadius: 4, border: "1px solid #ddd" }}
            />
            <button
              onClick={handleSearch}
              style={{ padding: "8px 16px", borderRadius: 4, border: "1px solid #ddd", background: "#fff", cursor: "pointer" }}
            >
              Search
            </button>
          </div>
          {state.loading ? (
            <div style={{ color: "#999" }}>Loading...</div>
          ) : (
            <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.875rem" }}>
              <thead>
                <tr style={{ borderBottom: "2px solid #e0e0e0", textAlign: "left" }}>
                  <th style={{ padding: "8px 12px" }}>Title</th>
                  <th style={{ padding: "8px 12px" }}>Shortcut</th>
                  <th style={{ padding: "8px 12px" }}>Category</th>
                  <th style={{ padding: "8px 12px" }}>Used</th>
                  <th style={{ padding: "8px 12px" }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {state.items.map((item) => (
                  <tr key={item.id} style={{ borderBottom: "1px solid #eee" }}>
                    <td style={{ padding: "8px 12px" }}>
                      <strong>{item.title}</strong>
                      <div style={{ color: "#888", fontSize: "0.8rem", maxWidth: 300, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                        {item.content}
                      </div>
                    </td>
                    <td style={{ padding: "8px 12px", fontFamily: "monospace" }}>{item.shortcut || "-"}</td>
                    <td style={{ padding: "8px 12px" }}>{item.category || "-"}</td>
                    <td style={{ padding: "8px 12px" }}>{item.usage_count}</td>
                    <td style={{ padding: "8px 12px" }}>
                      <button
                        onClick={() => handleUse(item.id)}
                        style={{ background: "none", border: "none", color: "#4caf50", cursor: "pointer", marginRight: 8 }}
                      >
                        Use
                      </button>
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
                    <td colSpan={5} style={{ padding: 16, color: "#999", textAlign: "center" }}>
                      No canned responses yet.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          )}
        </div>
        <div style={{ flex: 1, padding: 16, border: "1px solid #e0e0e0", borderRadius: 8, background: "#fafafa" }}>
          <h3 style={{ marginTop: 0, fontSize: "1rem" }}>{state.editingId ? "Edit Response" : "New Response"}</h3>
          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            <input
              placeholder="Title"
              value={state.form.title}
              onChange={(e) => dispatch({ type: "SET_FORM", field: "title", value: e.target.value })}
              style={{ padding: "8px 12px", borderRadius: 4, border: "1px solid #ddd" }}
            />
            <textarea
              rows={4}
              placeholder="Response content..."
              value={state.form.content}
              onChange={(e) => dispatch({ type: "SET_FORM", field: "content", value: e.target.value })}
              style={{ width: "100%", padding: 8, borderRadius: 4, border: "1px solid #ddd", fontSize: "0.875rem" }}
            />
            <input
              placeholder="Category (e.g. billing, account)"
              value={state.form.category}
              onChange={(e) => dispatch({ type: "SET_FORM", field: "category", value: e.target.value })}
              style={{ padding: "8px 12px", borderRadius: 4, border: "1px solid #ddd" }}
            />
            <input
              placeholder="Shortcut (e.g. !reset)"
              value={state.form.shortcut}
              onChange={(e) => dispatch({ type: "SET_FORM", field: "shortcut", value: e.target.value })}
              style={{ padding: "8px 12px", borderRadius: 4, border: "1px solid #ddd" }}
            />
            <div style={{ display: "flex", gap: 8 }}>
              <button
                onClick={handleSave}
                disabled={!state.form.title || !state.form.content}
                style={{
                  padding: "8px 20px",
                  borderRadius: 4,
                  border: "none",
                  background: state.form.title && state.form.content ? "#1976d2" : "#ccc",
                  color: "#fff",
                  cursor: state.form.title && state.form.content ? "pointer" : "default",
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
