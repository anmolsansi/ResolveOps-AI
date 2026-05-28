import { useEffect, useState } from "react";
import { listEvalRuns, runEval } from "../api/client";
import type { EvalRunSummary } from "../api/types";
import ErrorState from "../components/ErrorState";
import LoadingState from "../components/LoadingState";

export default function EvalRunsPage() {
  const [runs, setRuns] = useState<EvalRunSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState("");

  const fetchRuns = () => {
    listEvalRuns()
      .then(setRuns)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchRuns();
  }, []);

  const handleRun = async () => {
    setRunning(true);
    setError("");
    try {
      await runEval(`eval-${Date.now()}`);
      fetchRuns();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Eval failed");
    } finally {
      setRunning(false);
    }
  };

  if (loading) return <LoadingState />;

  return (
    <div>
      <h1>Eval Runs</h1>

      <button onClick={handleRun} disabled={running} style={{ marginBottom: "1rem" }}>
        {running ? "Running..." : "Run Eval"}
      </button>

      {error && <ErrorState message={error} />}

      {runs.length === 0 ? (
        <p style={{ color: "#888" }}>No eval runs yet. Click "Run Eval" to start one.</p>
      ) : (
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr>
              <th style={th}>Name</th>
              <th style={th}>Questions</th>
              <th style={th}>Passed</th>
              <th style={th}>Failed</th>
              <th style={th}>Avg Confidence</th>
              <th style={th}>Avg Latency</th>
              <th style={th}>Created</th>
            </tr>
          </thead>
          <tbody>
            {runs.map((r) => (
              <tr key={r.id}>
                <td style={td}>{r.name}</td>
                <td style={td}>{r.total_questions}</td>
                <td style={td}>{r.passed_count}</td>
                <td style={td}>{r.failed_count}</td>
                <td style={td}>{(r.average_confidence * 100).toFixed(1)}%</td>
                <td style={td}>{r.average_latency_ms.toFixed(0)}ms</td>
                <td style={td}>{new Date(r.created_at).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {runs.length > 0 && runs[0].results_json && (
        <details style={{ marginTop: "1rem" }}>
          <summary style={{ cursor: "pointer", fontWeight: 600 }}>
            Latest Run Details
          </summary>
          <pre style={{ background: "#f8f9fa", padding: "1rem", overflow: "auto" }}>
            {JSON.stringify(JSON.parse(runs[0].results_json), null, 2)}
          </pre>
        </details>
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
