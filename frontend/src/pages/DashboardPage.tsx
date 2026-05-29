import { useEffect, useState } from "react";
import type { PieLabelRenderProps } from "recharts";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { getChartsData, getQualityMetrics, getRetrievalMetrics } from "../api/client";
import type { ChartsResponse, QualityResponse, RetrievalResponse } from "../api/types";
import ErrorState from "../components/ErrorState";
import LoadingState from "../components/LoadingState";
import MetricCard from "../components/MetricCard";
import { card, colors, pageTitle, sectionTitle, td, th } from "../styles";

export default function DashboardPage() {
  const [quality, setQuality] = useState<QualityResponse | null>(null);
  const [retrieval, setRetrieval] = useState<RetrievalResponse | null>(null);
  const [charts, setCharts] = useState<ChartsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([getQualityMetrics(), getRetrievalMetrics(), getChartsData()])
      .then(([q, r, c]) => {
        setQuality(q);
        setRetrieval(r);
        setCharts(c);
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <LoadingState />;
  if (error) return <ErrorState message={error} />;

  const pieData = quality
    ? [
        { name: "Valid", value: quality.total_valid_rows, color: colors.success },
        { name: "Invalid", value: quality.total_invalid_rows, color: colors.danger },
        { name: "Duplicate", value: quality.total_duplicate_rows, color: colors.warning },
      ].filter((d) => d.value > 0)
    : [];

  return (
    <div>
      <h1 style={pageTitle}>Dashboard</h1>

      <h2 style={sectionTitle}>Ingestion Quality</h2>
      {quality && (
        <>
          <div style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap", marginBottom: "1.5rem" }}>
            <MetricCard label="Total Rows" value={quality.total_rows_seen} />
            <MetricCard label="Valid" value={quality.total_valid_rows} accent={colors.success} />
            <MetricCard label="Invalid" value={quality.total_invalid_rows} accent={colors.danger} />
            <MetricCard label="Duplicates" value={quality.total_duplicate_rows} accent={colors.warning} />
            <MetricCard label="Valid Rate" value={`${(quality.valid_rate * 100).toFixed(1)}%`} accent={colors.success} />
          </div>

          <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap", marginBottom: "1.5rem" }}>
            {pieData.length > 0 && (
              <div style={{ ...card, flex: "1 1 300px", minHeight: 260 }}>
                <h3 style={{ ...sectionTitle, fontSize: "0.95rem" }}>Ingestion Breakdown</h3>
                <ResponsiveContainer width="100%" height={200}>
                  <PieChart>
                    <Pie
                      data={pieData}
                      dataKey="value"
                      nameKey="name"
                      cx="50%"
                      cy="50%"
                      outerRadius={70}
                      label={(props: PieLabelRenderProps) =>
                        `${String(props.name ?? "")} ${((Number(props.percent) || 0) * 100).toFixed(0)}%`
                      }
                    >
                      {pieData.map((entry, i) => (
                        <Cell key={i} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            )}

            {charts && charts.ingestion.length > 0 && (
              <div style={{ ...card, flex: "2 1 450px", minHeight: 260 }}>
                <h3 style={{ ...sectionTitle, fontSize: "0.95rem" }}>Per-Batch Breakdown</h3>
                <ResponsiveContainer width="100%" height={200}>
                  <BarChart data={charts.ingestion}>
                    <CartesianGrid strokeDasharray="3 3" stroke={colors.border} />
                    <XAxis dataKey="batch_label" tick={{ fontSize: 11 }} />
                    <YAxis tick={{ fontSize: 11 }} />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="valid" fill={colors.success} name="Valid" />
                    <Bar dataKey="invalid" fill={colors.danger} name="Invalid" />
                    <Bar dataKey="duplicate" fill={colors.warning} name="Duplicate" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}
          </div>

          {quality.recent_batches.length > 0 && (
            <div style={{ ...card, marginBottom: "2rem" }}>
              <h3 style={{ ...sectionTitle, fontSize: "0.95rem" }}>Recent Batches</h3>
              <div style={{ overflowX: "auto" }}>
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
              </div>
            </div>
          )}
        </>
      )}

      <h2 style={sectionTitle}>Retrieval Metrics</h2>
      {retrieval && (
        <>
          <div style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap", marginBottom: "1.5rem" }}>
            <MetricCard label="Total Queries" value={retrieval.total_queries} />
            <MetricCard
              label="Avg Confidence"
              value={`${(retrieval.average_confidence * 100).toFixed(1)}%`}
              accent={colors.success}
            />
            <MetricCard label="Low Confidence" value={retrieval.low_confidence_query_count} accent={colors.warning} />
            <MetricCard label="Avg Latency" value={`${retrieval.average_latency_ms.toFixed(0)}ms`} />
            <MetricCard
              label="Citation Rate"
              value={`${(retrieval.citation_rate * 100).toFixed(1)}%`}
              accent={colors.primary}
            />
          </div>

          {charts && charts.queries.length > 0 && (
            <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap", marginBottom: "1.5rem" }}>
              <div style={{ ...card, flex: "1 1 400px", minHeight: 260 }}>
                <h3 style={{ ...sectionTitle, fontSize: "0.95rem" }}>Confidence Trend</h3>
                <ResponsiveContainer width="100%" height={200}>
                  <LineChart data={charts.queries}>
                    <CartesianGrid strokeDasharray="3 3" stroke={colors.border} />
                    <XAxis dataKey="timestamp" tick={false} />
                    <YAxis domain={[0, 1]} tick={{ fontSize: 11 }} />
                    <Tooltip
                      labelFormatter={(v) => new Date(String(v)).toLocaleString()}
                      formatter={(v) => `${(Number(v) * 100).toFixed(1)}%`}
                    />
                    <Line
                      type="monotone"
                      dataKey="confidence"
                      stroke={colors.primary}
                      strokeWidth={2}
                      dot={false}
                      name="Confidence"
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>

              <div style={{ ...card, flex: "1 1 400px", minHeight: 260 }}>
                <h3 style={{ ...sectionTitle, fontSize: "0.95rem" }}>Latency Trend</h3>
                <ResponsiveContainer width="100%" height={200}>
                  <LineChart data={charts.queries}>
                    <CartesianGrid strokeDasharray="3 3" stroke={colors.border} />
                    <XAxis dataKey="timestamp" tick={false} />
                    <YAxis tick={{ fontSize: 11 }} />
                    <Tooltip
                      labelFormatter={(v) => new Date(String(v)).toLocaleString()}
                      formatter={(v) => `${v}ms`}
                    />
                    <Line
                      type="monotone"
                      dataKey="latency_ms"
                      stroke={colors.warning}
                      strokeWidth={2}
                      dot={false}
                      name="Latency (ms)"
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}

          {retrieval.recent_queries.length > 0 && (
            <div style={{ ...card }}>
              <h3 style={{ ...sectionTitle, fontSize: "0.95rem" }}>Recent Queries</h3>
              <div style={{ overflowX: "auto" }}>
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
              </div>
            </div>
          )}
        </>
      )}

      {quality?.total_batches === 0 && retrieval?.total_queries === 0 && (
        <div style={{ ...card, textAlign: "center", padding: "3rem" }}>
          <p style={{ color: colors.textMuted, fontSize: "1rem" }}>
            No data yet. Upload some tickets to get started.
          </p>
        </div>
      )}
    </div>
  );
}
