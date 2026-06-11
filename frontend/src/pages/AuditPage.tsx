import { useEffect, useState } from "react";
import { getAuditLogs, getToken } from "../api/client";
import type { AuditLogResponse } from "../api/types";
import ErrorState from "../components/ErrorState";
import { badge, btn, card, colors, input, pageTitle, sectionTitle, td, th } from "../styles";

export default function AuditPage() {
  const [logs, setLogs] = useState<AuditLogResponse[]>([]);
  const [total, setTotal] = useState(0);
  const [actionFilter, setActionFilter] = useState("");
  const [error, setError] = useState("");

  const refresh = async () => {
    setError("");
    try {
      const res = await getAuditLogs({ action: actionFilter || undefined, limit: 200 });
      setLogs(res.logs);
      setTotal(res.total);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load audit logs (admin only)");
    }
  };

  useEffect(() => {
    void (async () => {
      await refresh();
    })();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  if (!getToken()) {
    return (
      <div>
        <h1 style={pageTitle}>Audit Logs</h1>
        <ErrorState message="Please sign in from the Account page to view audit logs." />
      </div>
    );
  }

  return (
    <div>
      <h1 style={pageTitle}>Audit Logs</h1>
      <p style={{ color: colors.textMuted, marginTop: "-1rem", marginBottom: "1.5rem" }}>
        Immutable record of governance events — logins, role changes, settings updates,
        retention runs, and prompt changes. Admin only.
      </p>

      {error && <ErrorState message={error} />}

      <div style={{ ...card, marginBottom: "1.5rem", display: "flex", gap: "0.75rem", flexWrap: "wrap" }}>
        <input
          style={{ ...input, flex: "1 1 220px" }}
          placeholder="Filter by action (e.g. user.login)"
          value={actionFilter}
          onChange={(e) => setActionFilter(e.target.value)}
        />
        <button onClick={refresh} style={btn("primary")}>
          Apply
        </button>
      </div>

      <div style={card}>
        <h2 style={sectionTitle}>Events ({total})</h2>
        {logs.length === 0 ? (
          <p style={{ color: colors.textMuted }}>No audit events.</p>
        ) : (
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr>
                <th style={th}>Time</th>
                <th style={th}>Actor</th>
                <th style={th}>Action</th>
                <th style={th}>Resource</th>
                <th style={th}>Detail</th>
              </tr>
            </thead>
            <tbody>
              {logs.map((l) => (
                <tr key={l.id}>
                  <td style={td}>{new Date(l.created_at).toLocaleString()}</td>
                  <td style={td}>{l.actor_email || "—"}</td>
                  <td style={td}>
                    <span style={badge(colors.primary)}>{l.action}</span>
                  </td>
                  <td style={td}>
                    {l.resource_type}
                    {l.resource_id ? ` · ${l.resource_id}` : ""}
                  </td>
                  <td style={{ ...td, color: colors.textMuted }}>{l.detail || "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
