import { useEffect, useState } from "react";
import {
  createConnector,
  createJob,
  deleteConnector,
  getDuplicates,
  listConnectors,
  listJobs,
  runDueJobs,
  syncConnector,
} from "../api/client";
import type {
  ConnectorSummary,
  DuplicateCluster,
  JobSummary,
  SyncResult,
} from "../api/types";
import ErrorState from "../components/ErrorState";
import { badge, btn, card, colors, input, pageTitle, sectionTitle, td, th } from "../styles";

const PROVIDERS = ["zendesk", "freshdesk", "intercom"];

export default function ConnectorsPage() {
  const [connectors, setConnectors] = useState<ConnectorSummary[]>([]);
  const [jobs, setJobs] = useState<JobSummary[]>([]);
  const [duplicates, setDuplicates] = useState<DuplicateCluster[]>([]);
  const [provider, setProvider] = useState(PROVIDERS[0]);
  const [name, setName] = useState("");
  const [interval, setIntervalMins] = useState(60);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [lastSync, setLastSync] = useState<SyncResult | null>(null);

  const refresh = async () => {
    try {
      const [c, j, d] = await Promise.all([listConnectors(), listJobs(), getDuplicates()]);
      setConnectors(c.items);
      setJobs(j.items);
      setDuplicates(d.clusters);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load");
    }
  };

  useEffect(() => {
    void (async () => {
      await refresh();
    })();
  }, []);

  const wrap = async (fn: () => Promise<void>) => {
    setBusy(true);
    setError("");
    try {
      await fn();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Action failed");
    } finally {
      setBusy(false);
    }
  };

  const handleCreate = () =>
    wrap(async () => {
      await createConnector(provider, name || `${provider} connector`);
      setName("");
      await refresh();
    });

  const handleSync = (id: string) =>
    wrap(async () => {
      const res = await syncConnector(id, 6);
      setLastSync(res);
      await refresh();
    });

  const handleSchedule = (id: string) =>
    wrap(async () => {
      await createJob(id, interval);
      await refresh();
    });

  const handleRunDue = () =>
    wrap(async () => {
      const res = await runDueJobs(6);
      if (res.results.length) setLastSync(res.results[res.results.length - 1]);
      await refresh();
    });

  const handleDelete = (id: string) =>
    wrap(async () => {
      await deleteConnector(id);
      await refresh();
    });

  return (
    <div>
      <h1 style={pageTitle}>Connectors</h1>
      <p style={{ color: colors.textMuted, marginTop: "-1rem", marginBottom: "1.5rem" }}>
        Import tickets from Zendesk, Freshdesk, and Intercom. Syncs are incremental
        (cursor-based) and semantically de-duplicated on import.
      </p>

      {error && <ErrorState message={error} />}

      <div style={{ ...card, marginBottom: "1.5rem" }}>
        <h2 style={sectionTitle}>Add connector</h2>
        <div style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap", alignItems: "center" }}>
          <select
            value={provider}
            onChange={(e) => setProvider(e.target.value)}
            style={input}
          >
            {PROVIDERS.map((p) => (
              <option key={p} value={p}>
                {p}
              </option>
            ))}
          </select>
          <input
            style={{ ...input, flex: "1 1 220px" }}
            placeholder="Connector name"
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
          <button onClick={handleCreate} disabled={busy} style={btn("primary")}>
            Add
          </button>
          <span style={{ marginLeft: "auto", display: "flex", gap: "0.5rem", alignItems: "center" }}>
            <span style={{ color: colors.textMuted, fontSize: "0.8rem" }}>Schedule interval (min)</span>
            <input
              type="number"
              min={1}
              value={interval}
              onChange={(e) => setIntervalMins(Number(e.target.value))}
              style={{ ...input, width: 80 }}
            />
            <button onClick={handleRunDue} disabled={busy} style={btn("secondary")}>
              Run due jobs
            </button>
          </span>
        </div>
      </div>

      {lastSync && (
        <div style={{ ...card, marginBottom: "1.5rem", borderLeft: `4px solid ${colors.success}` }}>
          <strong>Last sync:</strong> fetched {lastSync.fetched}, imported{" "}
          <span style={{ color: colors.success, fontWeight: 600 }}>{lastSync.imported}</span>, skipped{" "}
          {lastSync.duplicate_id + lastSync.duplicate_semantic} duplicates ({lastSync.duplicate_semantic}{" "}
          semantic) — cursor now at {lastSync.cursor}.
        </div>
      )}

      <div style={{ ...card, marginBottom: "1.5rem" }}>
        <h2 style={sectionTitle}>Connectors ({connectors.length})</h2>
        {connectors.length === 0 ? (
          <p style={{ color: colors.textMuted }}>No connectors yet.</p>
        ) : (
          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse" }}>
              <thead>
                <tr>
                  <th style={th}>Provider</th>
                  <th style={th}>Name</th>
                  <th style={th}>Cursor</th>
                  <th style={th}>Imported</th>
                  <th style={th}>Last synced</th>
                  <th style={th}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {connectors.map((c) => (
                  <tr key={c.id}>
                    <td style={td}>
                      <span style={badge(colors.primary)}>{c.provider}</span>
                    </td>
                    <td style={td}>{c.name}</td>
                    <td style={td}>{c.cursor ?? "—"}</td>
                    <td style={td}>{c.total_imported}</td>
                    <td style={td}>
                      {c.last_synced_at ? new Date(c.last_synced_at).toLocaleString() : "never"}
                    </td>
                    <td style={{ ...td, display: "flex", gap: "0.5rem" }}>
                      <button onClick={() => handleSync(c.id)} disabled={busy} style={btn("primary")}>
                        Sync
                      </button>
                      <button onClick={() => handleSchedule(c.id)} disabled={busy} style={btn("secondary")}>
                        Schedule
                      </button>
                      <button onClick={() => handleDelete(c.id)} disabled={busy} style={btn("danger")}>
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <div style={{ ...card, marginBottom: "1.5rem" }}>
        <h2 style={sectionTitle}>Scheduled jobs ({jobs.length})</h2>
        {jobs.length === 0 ? (
          <p style={{ color: colors.textMuted }}>No scheduled jobs. Use “Schedule” on a connector.</p>
        ) : (
          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse" }}>
              <thead>
                <tr>
                  <th style={th}>Job</th>
                  <th style={th}>Every</th>
                  <th style={th}>Next run</th>
                  <th style={th}>Last run</th>
                  <th style={th}>Last status</th>
                  <th style={th}>Last imported</th>
                </tr>
              </thead>
              <tbody>
                {jobs.map((j) => (
                  <tr key={j.id}>
                    <td style={td}>{j.id.slice(0, 8)}</td>
                    <td style={td}>{j.interval_minutes} min</td>
                    <td style={td}>{new Date(j.next_run_at).toLocaleString()}</td>
                    <td style={td}>{j.last_run_at ? new Date(j.last_run_at).toLocaleString() : "—"}</td>
                    <td style={td}>
                      {j.last_status ? (
                        <span style={badge(colors.success)}>{j.last_status}</span>
                      ) : (
                        "pending"
                      )}
                    </td>
                    <td style={td}>{j.last_imported}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <div style={card}>
        <h2 style={sectionTitle}>Potential duplicates ({duplicates.length})</h2>
        {duplicates.length === 0 ? (
          <p style={{ color: colors.textMuted }}>
            No near-duplicate clusters detected across ingested tickets.
          </p>
        ) : (
          duplicates.map((cluster, i) => (
            <div
              key={i}
              style={{
                border: `1px solid ${colors.border}`,
                borderRadius: 8,
                padding: "0.75rem 1rem",
                marginBottom: "0.75rem",
              }}
            >
              <div style={{ marginBottom: "0.5rem" }}>
                <span style={badge(colors.warning)}>{cluster.size} tickets</span>{" "}
                <span style={{ color: colors.textMuted, fontSize: "0.8rem" }}>
                  similarity {cluster.max_similarity.toFixed(3)}
                </span>
              </div>
              {cluster.tickets.map((t) => (
                <div key={t.id} style={{ fontSize: "0.85rem", color: colors.text }}>
                  <strong>{t.id}</strong> — {t.title}{" "}
                  <span style={{ color: colors.textMuted }}>({t.product_area})</span>
                </div>
              ))}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
