import { useReducer, useEffect } from "react";
import {
  listPortalArticles,
  createPortalArticle,
  updatePortalArticle,
  deletePortalArticle,
  searchPortalArticles,
} from "../api/client";
import type { PortalArticle } from "../api/types";

interface State {
  items: PortalArticle[];
  loading: boolean;
  error: string | null;
  editingId: string | null;
  search: string;
  form: { title: string; content: string; category: string; product_area: string; tags: string; published: boolean };
}

type Action =
  | { type: "LOAD_START" }
  | { type: "LOAD_DONE"; items: PortalArticle[] }
  | { type: "LOAD_ERROR"; error: string }
  | { type: "TOGGLE_EDIT"; id?: string | null }
  | { type: "SET_FORM"; field: string; value: string | boolean }
  | { type: "SET_SEARCH"; value: string }
  | { type: "SAVED"; items: PortalArticle[] };

const emptyForm = { title: "", content: "", category: "", product_area: "", tags: "", published: false };

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
              title: item.title,
              content: item.content,
              category: item.category || "",
              product_area: item.product_area || "",
              tags: (item.tags || []).join(", "),
              published: item.published,
            },
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

export default function PortalPage() {
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
    const p = q ? searchPortalArticles(q) : listPortalArticles();
    p.then((r) => dispatch({ type: "LOAD_DONE", items: r.items }))
      .catch((e) => dispatch({ type: "LOAD_ERROR", error: String(e) }));
  };

  useEffect(() => load(), []);

  const handleSave = async () => {
    try {
      const tags = state.form.tags
        .split(",")
        .map((t) => t.trim())
        .filter(Boolean);
      const payload = { ...state.form, tags };
      if (state.editingId) {
        await updatePortalArticle(state.editingId, payload);
      } else {
        await createPortalArticle(payload);
      }
      load();
    } catch (e) {
      dispatch({ type: "LOAD_ERROR", error: String(e) });
    }
  };

  const handleDelete = async (id: string) => {
    await deletePortalArticle(id);
    load();
  };

  const handleSearch = () => {
    load(state.search || undefined);
  };

  return (
    <div>
      <h2>Self-Service Portal</h2>
      <p style={{ color: "#666", fontSize: "0.875rem" }}>
        Manage knowledge base articles for customers to self-serve. Published articles appear in the customer widget.
      </p>
      {state.error && <div style={{ color: "#d32f2f", marginBottom: 16 }}>{state.error}</div>}
      <div style={{ display: "flex", gap: 16, alignItems: "start" }}>
        <div style={{ flex: 2 }}>
          <div style={{ display: "flex", gap: 8, marginBottom: 16 }}>
            <input
              placeholder="Search articles..."
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
                  <th style={{ padding: "8px 12px" }}>Category</th>
                  <th style={{ padding: "8px 12px" }}>Views</th>
                  <th style={{ padding: "8px 12px" }}>Published</th>
                  <th style={{ padding: "8px 12px" }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {state.items.map((item) => (
                  <tr key={item.id} style={{ borderBottom: "1px solid #eee" }}>
                    <td style={{ padding: "8px 12px" }}>
                      <strong>{item.title}</strong>
                      <div style={{ color: "#888", fontSize: "0.8rem" }}>{item.slug}</div>
                    </td>
                    <td style={{ padding: "8px 12px" }}>{item.category || "-"}</td>
                    <td style={{ padding: "8px 12px" }}>{item.view_count}</td>
                    <td style={{ padding: "8px 12px" }}>
                      <span
                        style={{
                          padding: "2px 8px",
                          borderRadius: 4,
                          fontSize: "0.75rem",
                          background: item.published ? "#e8f5e9" : "#fff3e0",
                          color: item.published ? "#2e7d32" : "#e65100",
                        }}
                      >
                        {item.published ? "Published" : "Draft"}
                      </span>
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
                    <td colSpan={5} style={{ padding: 16, color: "#999", textAlign: "center" }}>
                      No articles yet.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          )}
        </div>
        <div style={{ flex: 1, padding: 16, border: "1px solid #e0e0e0", borderRadius: 8, background: "#fafafa" }}>
          <h3 style={{ marginTop: 0, fontSize: "1rem" }}>{state.editingId ? "Edit Article" : "New Article"}</h3>
          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            <input
              placeholder="Title"
              value={state.form.title}
              onChange={(e) => dispatch({ type: "SET_FORM", field: "title", value: e.target.value })}
              style={{ padding: "8px 12px", borderRadius: 4, border: "1px solid #ddd" }}
            />
            <textarea
              rows={6}
              placeholder="Article content (Markdown supported)..."
              value={state.form.content}
              onChange={(e) => dispatch({ type: "SET_FORM", field: "content", value: e.target.value })}
              style={{ width: "100%", padding: 8, borderRadius: 4, border: "1px solid #ddd", fontSize: "0.875rem" }}
            />
            <input
              placeholder="Category (e.g. getting-started, billing)"
              value={state.form.category}
              onChange={(e) => dispatch({ type: "SET_FORM", field: "category", value: e.target.value })}
              style={{ padding: "8px 12px", borderRadius: 4, border: "1px solid #ddd" }}
            />
            <input
              placeholder="Product area"
              value={state.form.product_area}
              onChange={(e) => dispatch({ type: "SET_FORM", field: "product_area", value: e.target.value })}
              style={{ padding: "8px 12px", borderRadius: 4, border: "1px solid #ddd" }}
            />
            <input
              placeholder="Tags (comma-separated)"
              value={state.form.tags}
              onChange={(e) => dispatch({ type: "SET_FORM", field: "tags", value: e.target.value })}
              style={{ padding: "8px 12px", borderRadius: 4, border: "1px solid #ddd" }}
            />
            <label style={{ display: "flex", alignItems: "center", gap: 8, fontSize: "0.875rem", cursor: "pointer" }}>
              <input
                type="checkbox"
                checked={state.form.published}
                onChange={(e) => dispatch({ type: "SET_FORM", field: "published", value: e.target.checked })}
              />
              Publish immediately
            </label>
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
