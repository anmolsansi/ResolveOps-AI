import { useEffect, useState } from "react";
import { activatePrompt, createPrompt, getToken, listPrompts } from "../api/client";
import type { PromptResponse } from "../api/types";
import ErrorState from "../components/ErrorState";
import { badge, btn, card, colors, input, pageTitle, sectionTitle, td, th } from "../styles";

export default function PromptsPage() {
  const [prompts, setPrompts] = useState<PromptResponse[]>([]);
  const [activeId, setActiveId] = useState<string | null>(null);
  const [name, setName] = useState("support-assistant");
  const [content, setContent] = useState("");
  const [activate, setActivate] = useState(true);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const refresh = async () => {
    try {
      const res = await listPrompts();
      setPrompts(res.prompts);
      setActiveId(res.active_id);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load prompts");
    }
  };

  useEffect(() => {
    void (async () => {
      await refresh();
    })();
  }, []);

  const handleCreate = async () => {
    setBusy(true);
    setError("");
    try {
      await createPrompt(name, content, activate);
      setContent("");
      await refresh();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Create failed (admin only)");
    } finally {
      setBusy(false);
    }
  };

  const handleActivate = async (id: string) => {
    setError("");
    try {
      await activatePrompt(id);
      await refresh();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Activate failed (admin only)");
    }
  };

  if (!getToken()) {
    return (
      <div>
        <h1 style={pageTitle}>Prompts</h1>
        <ErrorState message="Please sign in from the Account page to manage prompts." />
      </div>
    );
  }

  return (
    <div>
      <h1 style={pageTitle}>Prompt &amp; Version Management</h1>
      <p style={{ color: colors.textMuted, marginTop: "-1rem", marginBottom: "1.5rem" }}>
        Versioned system prompts for answer generation. Exactly one prompt is active at a time
        and is applied to RAG and Assist answers (used by the OpenAI provider).
      </p>

      {error && <ErrorState message={error} />}

      <div style={{ ...card, marginBottom: "1.5rem" }}>
        <h2 style={sectionTitle}>New prompt version</h2>
        <div style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap", marginBottom: "0.75rem" }}>
          <input
            style={{ ...input, flex: "1 1 240px" }}
            placeholder="Prompt name"
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
          <label style={{ display: "flex", alignItems: "center", gap: 8, color: colors.textMuted }}>
            <input type="checkbox" checked={activate} onChange={(e) => setActivate(e.target.checked)} />
            Activate on save
          </label>
        </div>
        <textarea
          style={{ ...input, width: "100%", minHeight: 120, fontFamily: "monospace", resize: "vertical" }}
          placeholder="You are a support intelligence assistant. Answer using only the provided ticket context..."
          value={content}
          onChange={(e) => setContent(e.target.value)}
        />
        <div style={{ marginTop: "0.75rem" }}>
          <button onClick={handleCreate} disabled={busy || !content || !name} style={btn("primary")}>
            Save version
          </button>
        </div>
      </div>

      <div style={card}>
        <h2 style={sectionTitle}>Versions ({prompts.length})</h2>
        {prompts.length === 0 ? (
          <p style={{ color: colors.textMuted }}>No prompts yet — the built-in default is in use.</p>
        ) : (
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr>
                <th style={th}>Name</th>
                <th style={th}>Version</th>
                <th style={th}>Content</th>
                <th style={th}>Status</th>
                <th style={th}></th>
              </tr>
            </thead>
            <tbody>
              {prompts.map((p) => (
                <tr key={p.id}>
                  <td style={td}>{p.name}</td>
                  <td style={td}>v{p.version}</td>
                  <td style={{ ...td, maxWidth: 360, color: colors.textMuted }}>
                    {p.content.slice(0, 100)}
                    {p.content.length > 100 ? "…" : ""}
                  </td>
                  <td style={td}>
                    {p.id === activeId ? (
                      <span style={badge(colors.success)}>active</span>
                    ) : (
                      <span style={badge(colors.textMuted)}>inactive</span>
                    )}
                  </td>
                  <td style={td}>
                    {p.id !== activeId && (
                      <button onClick={() => handleActivate(p.id)} style={btn("secondary")}>
                        Activate
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
