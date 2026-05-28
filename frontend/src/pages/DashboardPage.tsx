import { useEffect, useState } from "react";
import { getQualityMetrics, getRetrievalMetrics } from "../api/client";
import type { QualityResponse, RetrievalResponse } from "../api/types";
import ErrorState from "../components/ErrorState";
import LoadingState from "../components/LoadingState";
import MetricCard from "../components/MetricCard";

export default function DashboardPage() {
  const [quality, setQuality] = useState<QualityResponse | null>(null);
  const [retrieval, setRetrieval] = useState<RetrievalResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([getQualityMetrics(), getRetrievalMetrics()])
      .then(([q, r]) => {
        setQuality(q);
        setRetrieval(r);
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <LoadingState />;
  if (error) return <ErrorState message={error} />;

  return (
    <div>
      <h1>Dashboard</h1>

      <h2>Ingestion Quality</h2>
      {quality && (
        <>
          <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap", marginBottom: "1.5rem" }}>
            <MetricCard label="Total Rows" value={quality.total_rows_seen} />
            <MetricCard label="Valid" value={quality.total_valid_rows} />
            <MetricCard label="Invalid" value={quality.total_invalid_rows} />
            <MetricCard label="Duplicates" value={quality.total_duplicate_rows} />
            <MetricCard label="Embedding Failures" value={quality.total_embedding_failures} />
            <MetricCard label="Valid Rate" value={`${(quality.valid_rate * 100).toFixed(1)}%`} />
          </div>
          {quality.recent_batches.length > 0 && (
            <>
              <h3>Recent Batches</h3>
              <table style={{ width: "100%", borderCollapse: "collapse" }}>
                <thead>
                  <tr>
                    <th style={th}>Filename</th>
                    <th style={th}>Total</th>
                    <th style={th}>Valid</th>
                    <th style={th}>Invalid</th>
                    <th style={th}>Duplicates</th>
                    <th style={th}>Started</th>
                  </tr>
                </thead>
                <tbody>
                  {quality.recent_batches.map((b) => (
                    <tr key={b.id}>
                      <td style={td}>{b.filename}</td>
                      <td style={td}>{b.total_count}</td>
                      <td style={td}>{b.valid_count}</td>
                      <td style={td}>{b.invalid_count}</td>
                      <td style={td}>{b.duplicate_count}</td>
                      <td style={td}>{new Date(b.started_at).toLocaleString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </>
          )}
        </>
      )}

      <h2 style={{ marginTop: "2rem" }}>Retrieval Metrics</h2>
      {retrieval && (
        <>
          <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap", marginBottom: "1.5rem" }}>
            <MetricCard label="Total Queries" value={retrieval.total_queries} />
            <MetricCard
              label="Avg Confidence"
              value={`${(retrieval.average_confidence * 100).toFixed(1)}%`}
            />
            <MetricCard label="Low Confidence" value={retrieval.low_confidence_query_count} />
            <MetricCard label="Avg Latency" value={`${retrieval.average_latency_ms.toFixed(0)}ms`} />
            <MetricCard
              label="Total Cost"
              value={`$${retrieval.total_estimated_cost_usd.toFixed(4)}`}
            />
            <MetricCard
              label="Citation Rate"
              value={`${(retrieval.citation_rate * 100).toFixed(1)}%`}
            />
          </div>
          {retrieval.recent_queries.length > 0 && (
            <>
              <h3>Recent Queries</h3>
              <table style={{ width: "100%", borderCollapse: "collapse" }}>
                <thead>
                  <tr>
                    <th style={th}>Question</th>
                    <th style={th}>Confidence</th>
                    <th style={th}>Latency</th>
                    <th style={th}>Time</th>
                  </tr>
                </thead>
                <tbody>
                  {retrieval.recent_queries.map((q) => (
                    <tr key={q.id}>
                      <td style={td}>{q.question}</td>
                      <td style={td}>{(q.confidence * 100).toFixed(1)}%</td>
                      <td style={td}>{q.latency_ms}ms</td>
                      <td style={td}>{new Date(q.created_at).toLocaleString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </>
          )}
        </>
      )}

      {quality?.total_batches === 0 && retrieval?.total_queries === 0 && (
        <p style={{ color: "#888" }}>No data yet. Upload some tickets to get started.</p>
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
