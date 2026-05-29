import { useEffect, useState } from "react";
import {
  createEvalQuestion,
  deleteEvalQuestion,
  getEvalExportUrl,
  listEvalQuestions,
  listEvalRuns,
  runEval,
  updateEvalQuestion,
} from "../api/client";
import type { EvalRunSummary, SavedEvalQuestion } from "../api/types";
import ErrorState from "../components/ErrorState";
import LoadingState from "../components/LoadingState";
import { btn, card, colors, input, pageTitle, sectionTitle, td, th } from "../styles";

export default function EvalRunsPage() {
  const [runs, setRuns] = useState<EvalRunSummary[]>([]);
  const [questions, setQuestions] = useState<SavedEvalQuestion[]>([]);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState("");
  const [newQuestion, setNewQuestion] = useState("");
  const [editId, setEditId] = useState<string | null>(null);
  const [editText, setEditText] = useState("");
  const [selectedRun, setSelectedRun] = useState<string | null>(null);

  const fetchAll = () => {
    Promise.all([listEvalRuns(), listEvalQuestions()])
      .then(([r, q]) => {
        setRuns(r);
        setQuestions(q);
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchAll();
  }, []);

  const handleRun = async () => {
    setRunning(true);
    setError("");
    try {
      await runEval(`eval-${Date.now()}`);
      fetchAll();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Eval failed");
    } finally {
      setRunning(false);
    }
  };

  const handleAddQuestion = async () => {
    if (!newQuestion.trim()) return;
    try {
      await createEvalQuestion(newQuestion.trim());
      setNewQuestion("");
      fetchAll();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to add question");
    }
  };

  const handleUpdateQuestion = async (id: string) => {
    if (!editText.trim()) return;
    try {
      await updateEvalQuestion(id, editText.trim());
      setEditId(null);
      setEditText("");
      fetchAll();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to update question");
    }
  };

  const handleDeleteQuestion = async (id: string) => {
    try {
      await deleteEvalQuestion(id);
      fetchAll();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to delete question");
    }
  };

  if (loading) return <LoadingState />;

  const activeRun = selectedRun ? runs.find((r) => r.id === selectedRun) : null;

  return (
    <div>
      <h1 style={pageTitle}>Eval Runs</h1>

      {error && <ErrorState message={error} />}

      <div style={{ ...card, marginBottom: "1.5rem" }}>
        <h3 style={{ ...sectionTitle, fontSize: "0.95rem" }}>Eval Dataset</h3>
        <p style={{ fontSize: "0.85rem", color: colors.textMuted, margin: "0 0 0.75rem" }}>
          Manage the questions used for evaluation runs. Saved questions will be available for
          custom eval runs.
        </p>

        <div style={{ display: "flex", gap: "0.5rem", marginBottom: "1rem" }}>
          <input
            placeholder="Add a new eval question..."
            value={newQuestion}
            onChange={(e) => setNewQuestion(e.target.value)}
            style={{ ...input, flex: 1 }}
            onKeyDown={(e) => e.key === "Enter" && handleAddQuestion()}
          />
          <button onClick={handleAddQuestion} style={btn("primary")} disabled={!newQuestion.trim()}>
            Add
          </button>
        </div>

        {questions.length > 0 && (
          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse" }}>
              <thead>
                <tr>
                  <th style={th}>Question</th>
                  <th style={{ ...th, width: 180 }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {questions.map((q) => (
                  <tr key={q.id}>
                    <td style={td}>
                      {editId === q.id ? (
                        <input
                          value={editText}
                          onChange={(e) => setEditText(e.target.value)}
                          style={{ ...input, width: "100%" }}
                          onKeyDown={(e) => e.key === "Enter" && handleUpdateQuestion(q.id)}
                        />
                      ) : (
                        q.question
                      )}
                    </td>
                    <td style={td}>
                      {editId === q.id ? (
                        <div style={{ display: "flex", gap: "0.25rem" }}>
                          <button onClick={() => handleUpdateQuestion(q.id)} style={btn("primary")}>
                            Save
                          </button>
                          <button onClick={() => setEditId(null)} style={btn("secondary")}>
                            Cancel
                          </button>
                        </div>
                      ) : (
                        <div style={{ display: "flex", gap: "0.25rem" }}>
                          <button
                            onClick={() => {
                              setEditId(q.id);
                              setEditText(q.question);
                            }}
                            style={btn("secondary")}
                          >
                            Edit
                          </button>
                          <button onClick={() => handleDeleteQuestion(q.id)} style={btn("danger")}>
                            Delete
                          </button>
                        </div>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <div style={{ display: "flex", gap: "0.75rem", alignItems: "center", marginBottom: "1.5rem" }}>
        <button
          onClick={handleRun}
          disabled={running}
          style={{ ...btn("primary"), opacity: running ? 0.5 : 1 }}
        >
          {running ? "Running..." : "Run Eval"}
        </button>
      </div>

      {runs.length === 0 ? (
        <div style={{ ...card, textAlign: "center", padding: "2rem" }}>
          <p style={{ color: colors.textMuted }}>No eval runs yet. Click "Run Eval" to start one.</p>
        </div>
      ) : (
        <div style={{ ...card, marginBottom: "1.5rem" }}>
          <h3 style={{ ...sectionTitle, fontSize: "0.95rem" }}>Run History</h3>
          <div style={{ overflowX: "auto" }}>
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
                  <th style={th}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {runs.map((r) => (
                  <tr key={r.id}>
                    <td style={td}>{r.name}</td>
                    <td style={td}>{r.total_questions}</td>
                    <td style={{ ...td, color: colors.success, fontWeight: 600 }}>{r.passed_count}</td>
                    <td style={{ ...td, color: colors.danger, fontWeight: 600 }}>{r.failed_count}</td>
                    <td style={td}>{(r.average_confidence * 100).toFixed(1)}%</td>
                    <td style={td}>{r.average_latency_ms.toFixed(0)}ms</td>
                    <td style={td}>{new Date(r.created_at).toLocaleString()}</td>
                    <td style={td}>
                      <div style={{ display: "flex", gap: "0.25rem" }}>
                        <button
                          onClick={() => setSelectedRun(selectedRun === r.id ? null : r.id)}
                          style={btn("secondary")}
                        >
                          {selectedRun === r.id ? "Hide" : "Details"}
                        </button>
                        <a href={getEvalExportUrl(r.id, "csv")} style={btn("secondary")} download>
                          CSV
                        </a>
                        <a href={getEvalExportUrl(r.id, "json")} style={btn("secondary")} download>
                          JSON
                        </a>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {activeRun?.results_json && (
        <div style={card}>
          <h3 style={{ ...sectionTitle, fontSize: "0.95rem" }}>Run Details: {activeRun.name}</h3>
          <pre
            style={{
              background: colors.bg,
              padding: "1rem",
              overflow: "auto",
              borderRadius: 8,
              fontSize: "0.8rem",
              border: `1px solid ${colors.border}`,
            }}
          >
            {JSON.stringify(JSON.parse(activeRun.results_json), null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}
