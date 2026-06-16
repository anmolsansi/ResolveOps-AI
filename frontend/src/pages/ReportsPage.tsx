import { useReducer, useEffect } from "react";
import {
  listSavedReports,
  createSavedReport,
  deleteSavedReport,
  listExportJobs,
  createExportJob,
  downloadExport,
} from "../api/client";
import type { SavedReport, ExportJob } from "../api/types";

interface State {
  reports: SavedReport[];
  exports: ExportJob[];
  loading: boolean;
  error: string | null;
  showCreate: boolean;
  form: { name: string; report_type: string; time_range: string };
}

type Action =
  | { type: "LOAD_START" }
  | { type: "LOAD_DONE"; reports: SavedReport[]; exports: ExportJob[] }
  | { type: "LOAD_ERROR"; error: string }
  | { type: "TOGGLE_CREATE" }
  | { type: "SET_FORM"; field: string; value: string };

const emptyForm = { name: "", report_type: "quality", time_range: "all" };

function reducer(state: State, action: Action): State {
  switch (action.type) {
    case "LOAD_START":
      return { ...state, loading: true, error: null };
    case "LOAD_DONE":
      return { ...state, loading: false, reports: action.reports, exports: action.exports };
    case "LOAD_ERROR":
      return { ...state, loading: false, error: action.error };
    case "TOGGLE_CREATE":
      return { ...state, showCreate: !state.showCreate, form: emptyForm };
    case "SET_FORM":
      return { ...state, form: { ...state.form, [action.field]: action.value } };
    default:
      return state;
  }
}

export default function ReportsPage() {
  const [state, dispatch] = useReducer(reducer, {
    reports: [],
    exports: [],
    loading: true,
    error: null,
    showCreate: false,
    form: emptyForm,
  });

  const load = () => {
    dispatch({ type: "LOAD_START" });
    Promise.all([listSavedReports(), listExportJobs()])
      .then(([reports, exports]) =>
        dispatch({ type: "LOAD_DONE", reports: reports.items, exports: exports.items })
      )
      .catch((e) => dispatch({ type: "LOAD_ERROR", error: String(e) }));
  };

  useEffect(load, []);

  const handleCreate = async () => {
    try {
      await createSavedReport({
        name: state.form.name,
        report_type: state.form.report_type,
        filters: { time_range: state.form.time_range },
      });
      dispatch({ type: "TOGGLE_CREATE" });
      load();
    } catch (e) {
      dispatch({ type: "LOAD_ERROR", error: String(e) });
    }
  };

  const handleExport = async (reportType: string) => {
    try {
      await createExportJob({ report_type: reportType, filters: { time_range: "all" } });
      load();
    } catch (e) {
      dispatch({ type: "LOAD_ERROR", error: String(e) });
    }
  };

  const handleDownload = async (jobId: string) => {
    try {
      const blob = await downloadExport(jobId);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `export-${jobId.slice(0, 8)}.csv`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (e) {
      dispatch({ type: "LOAD_ERROR", error: String(e) });
    }
  };

  const reportTypes = [
    { value: "quality", label: "Quality Metrics" },
    { value: "retrieval", label: "Retrieval Performance" },
    { value: "cost", label: "Cost Analysis" },
    { value: "agent_performance", label: "Agent Performance" },
    { value: "sla", label: "SLA Compliance" },
  ];

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 24 }}>
        <div>
          <h2 style={{ margin: 0 }}>Reports & Exports</h2>
          <p style={{ color: "#666", fontSize: "0.875rem", margin: "4px 0 0" }}>
            Save report configurations and export data as CSV.
          </p>
        </div>
        <button
          onClick={() => dispatch({ type: "TOGGLE_CREATE" })}
          style={{
            padding: "8px 20px",
            borderRadius: 6,
            border: "none",
            background: "#1976d2",
            color: "#fff",
            cursor: "pointer",
            fontWeight: 600,
          }}
        >
          New Report
        </button>
      </div>

      {state.error && <div style={{ color: "#d32f2f", marginBottom: 16 }}>{state.error}</div>}

      {state.showCreate && (
        <div style={{ padding: 20, border: "1px solid #e0e0e0", borderRadius: 8, background: "#fafafa", marginBottom: 24 }}>
          <h3 style={{ marginTop: 0, fontSize: "1rem" }}>Create Saved Report</h3>
          <div style={{ display: "flex", gap: 12, alignItems: "end", flexWrap: "wrap" }}>
            <input
              placeholder="Report name"
              value={state.form.name}
              onChange={(e) => dispatch({ type: "SET_FORM", field: "name", value: e.target.value })}
              style={{ padding: "8px 12px", borderRadius: 4, border: "1px solid #ddd", flex: 1, minWidth: 200 }}
            />
            <select
              value={state.form.report_type}
              onChange={(e) => dispatch({ type: "SET_FORM", field: "report_type", value: e.target.value })}
              style={{ padding: "8px 12px", borderRadius: 4, border: "1px solid #ddd" }}
            >
              {reportTypes.map((t) => (
                <option key={t.value} value={t.value}>{t.label}</option>
              ))}
            </select>
            <select
              value={state.form.time_range}
              onChange={(e) => dispatch({ type: "SET_FORM", field: "time_range", value: e.target.value })}
              style={{ padding: "8px 12px", borderRadius: 4, border: "1px solid #ddd" }}
            >
              <option value="all">All Time</option>
              <option value="7d">Last 7 Days</option>
              <option value="30d">Last 30 Days</option>
              <option value="90d">Last 90 Days</option>
            </select>
            <button
              onClick={handleCreate}
              disabled={!state.form.name}
              style={{
                padding: "8px 20px",
                borderRadius: 4,
                border: "none",
                background: state.form.name ? "#1976d2" : "#ccc",
                color: "#fff",
                cursor: state.form.name ? "pointer" : "default",
                fontWeight: 600,
              }}
            >
              Save
            </button>
            <button
              onClick={() => dispatch({ type: "TOGGLE_CREATE" })}
              style={{ padding: "8px 16px", borderRadius: 4, border: "1px solid #ddd", background: "#fff", cursor: "pointer" }}
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {state.loading ? (
        <div style={{ color: "#999" }}>Loading...</div>
      ) : (
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24 }}>
          <div>
            <h3 style={{ fontSize: "1rem", marginBottom: 12 }}>Saved Reports</h3>
            {state.reports.length === 0 ? (
              <div style={{ padding: 20, color: "#999", textAlign: "center", border: "1px solid #eee", borderRadius: 8 }}>
                No saved reports yet.
              </div>
            ) : (
              <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                {state.reports.map((r) => (
                  <div
                    key={r.id}
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                      padding: "12px 16px",
                      border: "1px solid #e0e0e0",
                      borderRadius: 8,
                      background: "#fafafa",
                    }}
                  >
                    <div>
                      <strong>{r.name}</strong>
                      <div style={{ fontSize: "0.8rem", color: "#666" }}>
                        {reportTypes.find((t) => t.value === r.report_type)?.label || r.report_type}
                        {" "}&middot;{" "}
                        {r.filters.time_range || "all"}
                      </div>
                    </div>
                    <div style={{ display: "flex", gap: 8 }}>
                      <button
                        onClick={() => handleExport(r.report_type)}
                        style={{ background: "none", border: "none", color: "#1976d2", cursor: "pointer" }}
                      >
                        Export
                      </button>
                      <button
                        onClick={async () => { await deleteSavedReport(r.id); load(); }}
                        style={{ background: "none", border: "none", color: "#d32f2f", cursor: "pointer" }}
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}

            <h3 style={{ fontSize: "1rem", marginTop: 32, marginBottom: 12 }}>Quick Export</h3>
            <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
              {reportTypes.map((t) => (
                <button
                  key={t.value}
                  onClick={() => handleExport(t.value)}
                  style={{
                    padding: "8px 16px",
                    borderRadius: 6,
                    border: "1px solid #ddd",
                    background: "#fff",
                    cursor: "pointer",
                    fontSize: "0.8rem",
                  }}
                >
                  {t.label}
                </button>
              ))}
            </div>
          </div>

          <div>
            <h3 style={{ fontSize: "1rem", marginBottom: 12 }}>Export History</h3>
            {state.exports.length === 0 ? (
              <div style={{ padding: 20, color: "#999", textAlign: "center", border: "1px solid #eee", borderRadius: 8 }}>
                No exports yet.
              </div>
            ) : (
              <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                {state.exports.map((e) => (
                  <div
                    key={e.id}
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                      padding: "12px 16px",
                      border: "1px solid #e0e0e0",
                      borderRadius: 8,
                      background: "#fafafa",
                    }}
                  >
                    <div>
                      <span
                        style={{
                          padding: "2px 8px",
                          borderRadius: 4,
                          fontSize: "0.75rem",
                          background: e.status === "succeeded" ? "#e8f5e9" : "#fff3e0",
                          color: e.status === "succeeded" ? "#2e7d32" : "#e65100",
                        }}
                      >
                        {e.status}
                      </span>
                      <span style={{ marginLeft: 8, fontSize: "0.85rem" }}>
                        {reportTypes.find((t) => t.value === e.report_type)?.label || e.report_type}
                      </span>
                      <span style={{ marginLeft: 8, fontSize: "0.8rem", color: "#888" }}>
                        {e.row_count} rows
                      </span>
                    </div>
                    {e.status === "succeeded" && (
                      <button
                        onClick={() => handleDownload(e.id)}
                        style={{ background: "none", border: "none", color: "#1976d2", cursor: "pointer" }}
                      >
                        Download CSV
                      </button>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
