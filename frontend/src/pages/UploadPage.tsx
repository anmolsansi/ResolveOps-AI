import { useState } from "react";
import { uploadTickets } from "../api/client";
import type { UploadResponse } from "../api/types";
import ErrorState from "../components/ErrorState";
import LoadingState from "../components/LoadingState";
import MetricCard from "../components/MetricCard";
import { btn, card, colors, pageTitle, sectionTitle, td, th } from "../styles";

function downloadInvalidRowsCsv(result: UploadResponse) {
  if (!result.invalid_rows.length) return;
  const first = result.invalid_rows[0];
  const dataKeys = Object.keys(first.data);
  const headers = ["row", ...dataKeys, "reason"];
  const rows = result.invalid_rows.map((r) => {
    const vals = [String(r.row), ...dataKeys.map((k) => `"${(r.data[k] || "").replace(/"/g, '""')}"`), `"${r.reason}"`];
    return vals.join(",");
  });
  const csv = [headers.join(","), ...rows].join("\n");
  const blob = new Blob([csv], { type: "text/csv" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `invalid_rows_${result.batch_id.slice(0, 8)}.csv`;
  a.click();
  URL.revokeObjectURL(url);
}

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState<UploadResponse | null>(null);

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const data = await uploadTickets(file);
      setResult(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Upload failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1 style={pageTitle}>Upload Tickets</h1>

      <div style={{ ...card, marginBottom: "1.5rem" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
          <input
            type="file"
            accept=".csv"
            onChange={(e) => setFile(e.target.files?.[0] ?? null)}
          />
          <button
            onClick={handleUpload}
            disabled={!file || loading}
            style={{ ...btn("primary"), opacity: !file || loading ? 0.5 : 1 }}
          >
            Upload
          </button>
        </div>
      </div>

      {loading && <LoadingState message="Uploading and processing..." />}
      {error && <ErrorState message={error} />}

      {result && (
        <div>
          <h2 style={sectionTitle}>Upload Results</h2>
          <div style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap", marginBottom: "1.5rem" }}>
            <MetricCard label="Batch ID" value={result.batch_id.slice(0, 8)} />
            <MetricCard label="Total" value={result.total_count} />
            <MetricCard label="Valid" value={result.valid_count} accent={colors.success} />
            <MetricCard label="Invalid" value={result.invalid_count} accent={colors.danger} />
            <MetricCard label="Duplicates" value={result.duplicate_count} accent={colors.warning} />
            <MetricCard label="Embedding Failures" value={result.embedding_failure_count} accent={colors.danger} />
          </div>

          {result.errors.length > 0 && (
            <div style={{ ...card, marginBottom: "1rem" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.75rem" }}>
                <h3 style={{ ...sectionTitle, marginBottom: 0, fontSize: "0.95rem" }}>Row Errors</h3>
                {result.invalid_rows.length > 0 && (
                  <button
                    onClick={() => downloadInvalidRowsCsv(result)}
                    style={btn("secondary")}
                  >
                    Download Invalid Rows CSV
                  </button>
                )}
              </div>
              <div style={{ overflowX: "auto" }}>
                <table style={{ width: "100%", borderCollapse: "collapse" }}>
                  <thead>
                    <tr>
                      <th style={th}>Row</th>
                      <th style={th}>Ticket ID</th>
                      <th style={th}>Reason</th>
                    </tr>
                  </thead>
                  <tbody>
                    {result.errors.map((err, i) => (
                      <tr key={i}>
                        <td style={td}>{err.row}</td>
                        <td style={td}>{err.ticket_id ?? "-"}</td>
                        <td style={td}>{err.reason}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          <div style={{ ...card, padding: "1rem 1.25rem" }}>
            <a href="/tickets" style={{ color: colors.primary, fontWeight: 600, textDecoration: "none" }}>
              View uploaded tickets &rarr;
            </a>
          </div>
        </div>
      )}
    </div>
  );
}
