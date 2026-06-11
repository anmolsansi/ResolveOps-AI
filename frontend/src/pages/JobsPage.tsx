import { useEffect, useState } from "react";
import { createBgJob, getToken, listBgJobs, processPendingJobs } from "../api/client";
import type { BgJobResponse } from "../api/types";
import ErrorState from "../components/ErrorState";
import { badge, btn, card, colors, input, pageTitle, sectionTitle, td, th } from "../styles";

const JOB_TYPES = [
  "embedding_backfill",
  "retention_run",
  "pii_redact_tickets",
  "connector_sync",
];

function statusColor(status: string): string {
  if (status === "succeeded") return colors.success;
  if (status === "failed") return colors.danger;
  if (status === "running") return colors.warning;
  return colors.textMuted;
}

export default function JobsPage() {
  const [jobs, setJobs] = useState<BgJobResponse[]>([]);
  const [jobType, setJobType] = useState(JOB_TYPES[0]);
  const [error, setError] = useState("");
  const [status, setStatus] = useState("");
  const [busy, setBusy] = useState(false);

  const refresh = async () => {
    try {
      const res = await listBgJobs();
      setJobs(res.jobs);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load jobs");
    }
  };

  useEffect(() => {
    void (async () => {
      await refresh();
    })();
  }, []);

  const handleEnqueue = async () => {
    setBusy(true);
    setError("");
    setStatus("");
    try {
      await createBgJob(jobType);
      setStatus(`Enqueued ${jobType}.`);
      await refresh();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Enqueue failed");
    } finally {
      setBusy(false);
    }
  };

  const handleProcess = async () => {
    setBusy(true);
    setError("");
    try {
      const res = await processPendingJobs(10);
      setStatus(`Processed ${res.processed}: ${res.succeeded} succeeded, ${res.failed} failed.`);
      await refresh();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Process failed");
    } finally {
      setBusy(false);
    }
  };

  if (!getToken()) {
    return (
      <div>
        <h1 style={pageTitle}>Background Jobs</h1>
        <ErrorState message="Please sign in from the Account page to manage jobs." />
      </div>
    );
  }

  return (
    <div>
      <h1 style={pageTitle}>Background Job Queue</h1>
      <p style={{ color: colors.textMuted, marginTop: "-1rem", marginBottom: "1.5rem" }}>
        In-process queue for ingestion and embedding work — enqueue jobs and process the pending
        batch. Handlers: embedding backfill, retention purge, PII redaction, connector sync.
      </p>

      {error && <ErrorState message={error} />}
      {status && (
        <div style={{ ...card, marginBottom: "1.5rem", borderLeft: `4px solid ${colors.success}` }}>
          {status}
        </div>
      )}

      <div style={{ ...card, marginBottom: "1.5rem" }}>
        <h2 style={sectionTitle}>Enqueue &amp; process</h2>
        <div style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap", alignItems: "center" }}>
          <select value={jobType} onChange={(e) => setJobType(e.target.value)} style={input}>
            {JOB_TYPES.map((t) => (
              <option key={t} value={t}>{t}</option>
            ))}
          </select>
          <button onClick={handleEnqueue} disabled={busy} style={btn("primary")}>
            Enqueue
          </button>
          <button onClick={handleProcess} disabled={busy} style={{ ...btn("secondary"), marginLeft: "auto" }}>
            Process pending
          </button>
        </div>
      </div>

      <div style={card}>
        <h2 style={sectionTitle}>Jobs ({jobs.length})</h2>
        {jobs.length === 0 ? (
          <p style={{ color: colors.textMuted }}>No jobs yet.</p>
        ) : (
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr>
                <th style={th}>Type</th>
                <th style={th}>Status</th>
                <th style={th}>Result / Error</th>
                <th style={th}>Created</th>
              </tr>
            </thead>
            <tbody>
              {jobs.map((j) => (
                <tr key={j.id}>
                  <td style={td}>{j.job_type}</td>
                  <td style={td}>
                    <span style={badge(statusColor(j.status))}>{j.status}</span>
                  </td>
                  <td style={{ ...td, maxWidth: 360, color: colors.textMuted, fontFamily: "monospace", fontSize: "0.8rem" }}>
                    {j.error || j.result_json || "—"}
                  </td>
                  <td style={td}>{new Date(j.created_at).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
