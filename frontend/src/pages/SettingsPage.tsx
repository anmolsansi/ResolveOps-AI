import { useEffect, useState } from "react";
import {
  getSettings,
  getToken,
  getVectorBackend,
  previewRetention,
  runRetention,
  updateSettings,
} from "../api/client";
import type {
  RetentionPreviewResponse,
  SettingsResponse,
  VectorBackendStatus,
} from "../api/types";
import ErrorState from "../components/ErrorState";
import { badge, btn, card, colors, input, pageTitle, sectionTitle } from "../styles";

const field: React.CSSProperties = { display: "flex", flexDirection: "column", gap: 4, flex: "1 1 200px" };
const label: React.CSSProperties = { fontSize: "0.8rem", color: colors.textMuted, fontWeight: 600 };

export default function SettingsPage() {
  const [settings, setSettings] = useState<SettingsResponse | null>(null);
  const [vector, setVector] = useState<VectorBackendStatus | null>(null);
  const [retention, setRetention] = useState<RetentionPreviewResponse | null>(null);
  const [error, setError] = useState("");
  const [status, setStatus] = useState("");
  const [busy, setBusy] = useState(false);

  const refresh = async () => {
    try {
      const [s, v, r] = await Promise.all([getSettings(), getVectorBackend(), previewRetention()]);
      setSettings(s);
      setVector(v);
      setRetention(r);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load settings");
    }
  };

  useEffect(() => {
    void (async () => {
      await refresh();
    })();
  }, []);

  const update = (patch: Partial<SettingsResponse>) => {
    setSettings((prev) => (prev ? { ...prev, ...patch } : prev));
  };

  const handleSave = async () => {
    if (!settings) return;
    setBusy(true);
    setError("");
    setStatus("");
    try {
      await updateSettings({
        llm_provider: settings.llm_provider,
        embedding_provider: settings.embedding_provider,
        llm_model: settings.llm_model,
        embedding_model: settings.embedding_model,
        low_confidence_threshold: settings.low_confidence_threshold,
        default_top_k: settings.default_top_k,
        vector_backend: settings.vector_backend,
        pii_redaction_enabled: settings.pii_redaction_enabled,
        retention_rag_query_days: settings.retention_rag_query_days,
        retention_audit_log_days: settings.retention_audit_log_days,
      });
      setStatus("Settings saved.");
      await refresh();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Save failed (admin only)");
    } finally {
      setBusy(false);
    }
  };

  const handleRunRetention = async () => {
    setBusy(true);
    setError("");
    try {
      const res = await runRetention();
      setStatus(
        `Retention run: ${res.rag_queries_deleted} queries, ${res.audit_logs_deleted} audit logs deleted.`,
      );
      await refresh();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Retention run failed (admin only)");
    } finally {
      setBusy(false);
    }
  };

  if (!getToken()) {
    return (
      <div>
        <h1 style={pageTitle}>Settings</h1>
        <ErrorState message="Please sign in from the Account page to view settings." />
      </div>
    );
  }

  return (
    <div>
      <h1 style={pageTitle}>Model &amp; Governance Settings</h1>
      <p style={{ color: colors.textMuted, marginTop: "-1rem", marginBottom: "1.5rem" }}>
        Runtime provider/model configuration, retrieval backend, PII redaction, and data
        retention windows. Changes require an admin and are audit-logged.
      </p>

      {error && <ErrorState message={error} />}
      {status && (
        <div style={{ ...card, marginBottom: "1.5rem", borderLeft: `4px solid ${colors.success}` }}>
          {status}
        </div>
      )}

      {settings && (
        <div style={{ ...card, marginBottom: "1.5rem" }}>
          <h2 style={sectionTitle}>Providers &amp; models</h2>
          <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap", marginBottom: "1rem" }}>
            <div style={field}>
              <span style={label}>LLM provider</span>
              <input style={input} value={settings.llm_provider} onChange={(e) => update({ llm_provider: e.target.value })} />
            </div>
            <div style={field}>
              <span style={label}>Embedding provider</span>
              <input style={input} value={settings.embedding_provider} onChange={(e) => update({ embedding_provider: e.target.value })} />
            </div>
            <div style={field}>
              <span style={label}>LLM model</span>
              <input style={input} value={settings.llm_model} onChange={(e) => update({ llm_model: e.target.value })} />
            </div>
            <div style={field}>
              <span style={label}>Embedding model</span>
              <input style={input} value={settings.embedding_model} onChange={(e) => update({ embedding_model: e.target.value })} />
            </div>
          </div>
          <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap" }}>
            <div style={field}>
              <span style={label}>Low-confidence threshold</span>
              <input style={input} type="number" step="0.05" value={settings.low_confidence_threshold} onChange={(e) => update({ low_confidence_threshold: Number(e.target.value) })} />
            </div>
            <div style={field}>
              <span style={label}>Default top-k</span>
              <input style={input} type="number" value={settings.default_top_k} onChange={(e) => update({ default_top_k: Number(e.target.value) })} />
            </div>
            <div style={field}>
              <span style={label}>Vector backend</span>
              <select style={input} value={settings.vector_backend} onChange={(e) => update({ vector_backend: e.target.value })}>
                {["auto", "pgvector", "memory"].map((b) => (
                  <option key={b} value={b}>{b}</option>
                ))}
              </select>
            </div>
            <div style={{ ...field, justifyContent: "flex-end" }}>
              <label style={{ ...label, display: "flex", alignItems: "center", gap: 8, cursor: "pointer" }}>
                <input type="checkbox" checked={settings.pii_redaction_enabled} onChange={(e) => update({ pii_redaction_enabled: e.target.checked })} />
                PII redaction on ingestion
              </label>
            </div>
          </div>
          <div style={{ marginTop: "1rem" }}>
            <button onClick={handleSave} disabled={busy} style={btn("primary")}>
              Save settings
            </button>
          </div>
        </div>
      )}

      {vector && (
        <div style={{ ...card, marginBottom: "1.5rem" }}>
          <h2 style={sectionTitle}>Retrieval backend</h2>
          <p style={{ margin: "0 0 0.5rem" }}>
            Active:{" "}
            <span style={badge(vector.active_backend === "pgvector" ? colors.success : colors.warning)}>
              {vector.active_backend}
            </span>
          </p>
          <p style={{ color: colors.textMuted, margin: 0, fontSize: "0.875rem" }}>
            Configured <code>{vector.configured}</code> · dialect <code>{vector.dialect}</code> ·
            package {vector.pgvector_importable ? "installed" : "missing"} · extension{" "}
            {vector.extension_present ? "enabled" : "absent"} — {vector.reason}
          </p>
        </div>
      )}

      {settings && retention && (
        <div style={card}>
          <h2 style={sectionTitle}>Data retention</h2>
          <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap", marginBottom: "1rem" }}>
            <div style={field}>
              <span style={label}>RAG query retention (days, 0 = keep forever)</span>
              <input style={input} type="number" value={settings.retention_rag_query_days} onChange={(e) => update({ retention_rag_query_days: Number(e.target.value) })} />
            </div>
            <div style={field}>
              <span style={label}>Audit log retention (days, 0 = keep forever)</span>
              <input style={input} type="number" value={settings.retention_audit_log_days} onChange={(e) => update({ retention_audit_log_days: Number(e.target.value) })} />
            </div>
          </div>
          <p style={{ color: colors.textMuted, fontSize: "0.875rem" }}>
            Would purge now: <strong>{retention.rag_queries_to_purge}</strong> RAG queries,{" "}
            <strong>{retention.audit_logs_to_purge}</strong> audit logs (save thresholds first).
          </p>
          <div style={{ display: "flex", gap: "0.75rem" }}>
            <button onClick={handleSave} disabled={busy} style={btn("secondary")}>
              Save thresholds
            </button>
            <button onClick={handleRunRetention} disabled={busy} style={btn("danger")}>
              Run retention purge
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
