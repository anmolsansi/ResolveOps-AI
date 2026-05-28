import { useState } from "react";
import { uploadTickets } from "../api/client";
import type { UploadResponse } from "../api/types";
import ErrorState from "../components/ErrorState";
import LoadingState from "../components/LoadingState";
import MetricCard from "../components/MetricCard";

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
      <h1>Upload Tickets</h1>
      <div style={{ marginBottom: "1rem" }}>
        <input
          type="file"
          accept=".csv"
          onChange={(e) => setFile(e.target.files?.[0] ?? null)}
        />
        <button
          onClick={handleUpload}
          disabled={!file || loading}
          style={{ marginLeft: "0.5rem", padding: "0.4rem 1rem" }}
        >
          Upload
        </button>
      </div>

      {loading && <LoadingState message="Uploading and processing..." />}
      {error && <ErrorState message={error} />}

      {result && (
        <div>
          <h2>Upload Results</h2>
          <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap", marginBottom: "1rem" }}>
            <MetricCard label="Batch ID" value={result.batch_id.slice(0, 8)} />
            <MetricCard label="Total" value={result.total_count} />
            <MetricCard label="Valid" value={result.valid_count} />
            <MetricCard label="Invalid" value={result.invalid_count} />
            <MetricCard label="Duplicates" value={result.duplicate_count} />
            <MetricCard label="Embedding Failures" value={result.embedding_failure_count} />
          </div>

          {result.errors.length > 0 && (
            <>
              <h3>Row Errors</h3>
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
            </>
          )}

          <p style={{ marginTop: "1rem" }}>
            <a href="/tickets">View uploaded tickets &rarr;</a>
          </p>
        </div>
      )}
    </div>
  );
}

const th: React.CSSProperties = {
  textAlign: "left",
  padding: "0.5rem",
  borderBottom: "2px solid #ddd",
};
const td: React.CSSProperties = { padding: "0.5rem", borderBottom: "1px solid #eee" };
