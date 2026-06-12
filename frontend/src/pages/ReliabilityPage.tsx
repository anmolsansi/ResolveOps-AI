import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  compareEval,
  getCostMetrics,
  getFailedQueries,
  getQualityByArea,
  getRetrievalMetrics,
} from "../api/client";
import type {
  CostResponse,
  EvalCompareResponse,
  EvalConfig,
  FailedQueriesResponse,
  QualityByAreaResponse,
  RetrievalResponse,
} from "../api/types";
import ErrorState from "../components/ErrorState";
import LoadingState from "../components/LoadingState";
import MetricCard from "../components/MetricCard";
import { badge, btn, card, colors, input, pageTitle, sectionTitle, td, th } from "../styles";

function pct(v: number): string {
  return `${(v * 100).toFixed(1)}%`;
}

function reasonColor(reason: string): string {
  if (reason.startsWith("feedback:")) return colors.danger;
  if (reason === "no_citations") return colors.warning;
  return colors.textMuted;
}

const metricExplanations: Record<string, string> = {
  "Hallucination Risk": "Share of answer tokens not supported by any retrieved context. Lower is better.",
  "Citation Coverage": "Share of answer tokens supported by cited ticket contexts. Higher is better.",
  "Retrieval Precision": "Share of retrieved chunks that overlap with the user question after tokenization. Higher is better.",
  "Answer Completeness": "Share of the user question addressed by the answer tokens. Higher is better.",
  "Citation Rate": "Percentage of queries that returned at least one citation. Higher is better.",
  "p50": "Median latency — 50% of queries complete within this time.",
  "p95": "95th percentile latency — 95% of queries complete within this time.",
  "p99": "99th percentile latency — 99% of queries complete within this time.",
};

export default function ReliabilityPage() {
  const [retrieval, setRetrieval] = useState<RetrievalResponse | null>(null);
  const [cost, setCost] = useState<CostResponse | null>(null);
  const [byArea, setByArea] = useState<QualityByAreaResponse | null>(null);
  const [failed, setFailed] = useState<FailedQueriesResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [configA, setConfigA] = useState<EvalConfig>({ label: "Baseline", top_k: 3, threshold: 0.3 });
  const [configB, setConfigB] = useState<EvalConfig>({ label: "Candidate", top_k: 5, threshold: 0.3 });
  const [compare, setCompare] = useState<EvalCompareResponse | null>(null);
  const [comparing, setComparing] = useState(false);
  const [compareError, setCompareError] = useState("");

  useEffect(() => {
    Promise.all([
      getRetrievalMetrics(),
      getCostMetrics(),
      getQualityByArea(),
      getFailedQueries(),
    ])
      .then(([r, c, a, f]) => {
        setRetrieval(r);
        setCost(c);
        setByArea(a);
        setFailed(f);
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  const runCompare = async () => {
    setComparing(true);
    setCompareError("");
    setCompare(null);
    try {
      const data = await compareEval(configA, configB, "regression-compare");
      setCompare(data);
    } catch (e) {
      setCompareError(e instanceof Error ? e.message : "Compare failed");
    } finally {
      setComparing(false);
    }
  };

  if (loading) return <LoadingState />;
  if (error) return <ErrorState message={error} />;

  const delta = (v: number): string => {
    const sign = v > 0 ? "+" : "";
    return `${sign}${v}`;
  };
  const deltaColor = (v: number, goodLow = false): string => {
    if (v === 0) return colors.textMuted;
    const positiveGood = goodLow ? v < 0 : v > 0;
    return positiveGood ? colors.success : colors.danger;
  };

  return (
    <div>
      <h1 style={pageTitle}>Reliability</h1>

      <h2 style={sectionTitle}>Answer Quality (averages)</h2>
      {retrieval && (
        <div style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap", marginBottom: "1.5rem" }}>
          <MetricCard
            label="Hallucination Risk"
            value={pct(retrieval.average_hallucination_risk)}
            accent={retrieval.average_hallucination_risk < 0.5 ? colors.success : colors.danger}
            explanation={metricExplanations["Hallucination Risk"]}
          />
          <MetricCard
            label="Citation Coverage"
            value={pct(retrieval.average_citation_coverage)}
            accent={colors.success}
            explanation={metricExplanations["Citation Coverage"]}
          />
          <MetricCard
            label="Retrieval Precision"
            value={pct(retrieval.average_retrieval_precision)}
            accent={colors.primary}
            explanation={metricExplanations["Retrieval Precision"]}
          />
          <MetricCard
            label="Answer Completeness"
            value={pct(retrieval.average_answer_completeness)}
            accent={colors.primary}
            explanation={metricExplanations["Answer Completeness"]}
          />
          <MetricCard
            label="Citation Rate"
            value={pct(retrieval.citation_rate)}
            accent={colors.success}
            explanation={metricExplanations["Citation Rate"]}
          />
        </div>
      )}

      <h2 style={sectionTitle}>Latency Percentiles</h2>
      {retrieval && (
        <div style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap", marginBottom: "1.5rem" }}>
          <MetricCard label="Avg" value={`${retrieval.average_latency_ms.toFixed(0)}ms`} />
          <MetricCard
            label="p50"
            value={`${retrieval.latency_p50_ms.toFixed(0)}ms`}
            accent={colors.success}
            explanation={metricExplanations["p50"]}
          />
          <MetricCard
            label="p95"
            value={`${retrieval.latency_p95_ms.toFixed(0)}ms`}
            accent={colors.warning}
            explanation={metricExplanations["p95"]}
          />
          <MetricCard
            label="p99"
            value={`${retrieval.latency_p99_ms.toFixed(0)}ms`}
            accent={colors.danger}
            explanation={metricExplanations["p99"]}
          />
          <MetricCard label="Total Queries" value={retrieval.total_queries} />
        </div>
      )}

      <h2 style={sectionTitle}>Cost by Provider / Model</h2>
      {cost && (
        <div style={{ ...card, marginBottom: "1.5rem" }}>
          <div style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap", marginBottom: "1rem" }}>
            <MetricCard label="Total Cost" value={`$${cost.total_estimated_cost_usd.toFixed(4)}`} accent={colors.primary} />
            <MetricCard label="Queries" value={cost.total_queries} />
          </div>
          {cost.by_model.length === 0 ? (
            <p style={{ color: colors.textMuted, margin: 0 }}>No queries recorded yet.</p>
          ) : (
            <div style={{ overflowX: "auto" }}>
              <table style={{ width: "100%", borderCollapse: "collapse" }}>
                <thead>
                  <tr>
                    <th style={th}>Provider</th>
                    <th style={th}>Model</th>
                    <th style={th}>Queries</th>
                    <th style={th}>Total Cost</th>
                  </tr>
                </thead>
                <tbody>
                  {cost.by_model.map((m) => (
                    <tr key={`${m.provider}/${m.model}`}>
                      <td style={td}>{m.provider}</td>
                      <td style={td}>{m.model}</td>
                      <td style={td}>{m.query_count}</td>
                      <td style={td}>${m.total_cost_usd.toFixed(6)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      <h2 style={sectionTitle}>Quality by Product Area</h2>
      {byArea && (
        <div style={{ ...card, marginBottom: "1.5rem" }}>
          {byArea.areas.length === 0 ? (
            <p style={{ color: colors.textMuted, margin: 0 }}>No product-area data yet.</p>
          ) : (
            <div style={{ overflowX: "auto" }}>
              <table style={{ width: "100%", borderCollapse: "collapse" }}>
                <thead>
                  <tr>
                    <th style={th}>Product Area</th>
                    <th style={th}>Queries</th>
                    <th style={th}>Avg Confidence</th>
                    <th style={th}>Hallucination</th>
                    <th style={th}>Citation Cov.</th>
                    <th style={th}>Retrieval Prec.</th>
                    <th style={th}>Completeness</th>
                  </tr>
                </thead>
                <tbody>
                  {byArea.areas.map((a) => (
                    <tr key={a.product_area}>
                      <td style={td}>
                        <span style={badge(colors.primary)}>{a.product_area}</span>
                      </td>
                      <td style={td}>{a.query_count}</td>
                      <td style={td}>{pct(a.average_confidence)}</td>
                      <td style={{ ...td, color: a.average_hallucination_risk < 0.5 ? colors.success : colors.danger }}>
                        {pct(a.average_hallucination_risk)}
                      </td>
                      <td style={td}>{pct(a.average_citation_coverage)}</td>
                      <td style={td}>{pct(a.average_retrieval_precision)}</td>
                      <td style={td}>{pct(a.average_answer_completeness)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      <h2 style={sectionTitle}>
        Failed-Query Review Queue {failed && `(${failed.count})`}
      </h2>
      {failed && (
        <div style={{ ...card, marginBottom: "1.5rem" }}>
          {failed.items.length === 0 ? (
            <p style={{ color: colors.textMuted, margin: 0 }}>No failed queries. 🎉</p>
          ) : (
            <div style={{ overflowX: "auto" }}>
              <table style={{ width: "100%", borderCollapse: "collapse" }}>
                <thead>
                  <tr>
                    <th style={th}>Question</th>
                    <th style={th}>Confidence</th>
                    <th style={th}>Reason</th>
                    <th style={th}>Product Area</th>
                  </tr>
                </thead>
                <tbody>
                  {failed.items.map((q) => (
                    <tr key={q.id}>
                      <td style={{ ...td, maxWidth: 360 }}>{q.question}</td>
                      <td style={{ ...td, color: q.confidence >= 0.3 ? colors.text : colors.warning }}>
                        {pct(q.confidence)}
                      </td>
                      <td style={td}>
                        <span style={badge(reasonColor(q.reason))}>{q.reason}</span>
                      </td>
                      <td style={td}>{q.product_area ?? "-"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      <h2 style={sectionTitle}>Regression Eval — Compare Two Configs</h2>
      <div style={{ ...card, marginBottom: "1.5rem" }}>
        <div style={{ display: "flex", gap: "1.5rem", flexWrap: "wrap", marginBottom: "1rem" }}>
          {[
            { cfg: configA, set: setConfigA, title: "Config A" },
            { cfg: configB, set: setConfigB, title: "Config B" },
          ].map(({ cfg, set, title }) => (
            <div key={title} style={{ flex: "1 1 260px" }}>
              <h3 style={{ ...sectionTitle, fontSize: "0.9rem" }}>{title}</h3>
              <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
                <label style={{ fontSize: "0.78rem", color: colors.textMuted }}>
                  Label
                  <input
                    value={cfg.label}
                    onChange={(e) => set({ ...cfg, label: e.target.value })}
                    style={{ ...input, width: "100%" }}
                  />
                </label>
                <label style={{ fontSize: "0.78rem", color: colors.textMuted }}>
                  Top-K
                  <input
                    type="number"
                    min={1}
                    value={cfg.top_k}
                    onChange={(e) => set({ ...cfg, top_k: Number(e.target.value) })}
                    style={{ ...input, width: "100%" }}
                  />
                </label>
                <label style={{ fontSize: "0.78rem", color: colors.textMuted }}>
                  Threshold
                  <input
                    type="number"
                    min={0}
                    max={1}
                    step={0.05}
                    value={cfg.threshold}
                    onChange={(e) => set({ ...cfg, threshold: Number(e.target.value) })}
                    style={{ ...input, width: "100%" }}
                  />
                </label>
              </div>
            </div>
          ))}
        </div>
        <button onClick={runCompare} disabled={comparing} style={{ ...btn("primary"), opacity: comparing ? 0.5 : 1 }}>
          {comparing ? "Running..." : "Run Comparison"}
        </button>
        {compareError && <p style={{ color: colors.danger, marginTop: "0.5rem" }}>{compareError}</p>}

        {compare && (
          <div style={{ marginTop: "1.25rem" }}>
            <div style={{ overflowX: "auto", marginBottom: "1rem" }}>
              <table style={{ width: "100%", borderCollapse: "collapse" }}>
                <thead>
                  <tr>
                    <th style={th}>Metric</th>
                    <th style={th}>{compare.config_a.label}</th>
                    <th style={th}>{compare.config_b.label}</th>
                    <th style={th}>Delta (B − A)</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td style={td}>Passed</td>
                    <td style={td}>{compare.config_a.passed_count}/{compare.total_questions}</td>
                    <td style={td}>{compare.config_b.passed_count}/{compare.total_questions}</td>
                    <td style={{ ...td, color: deltaColor(compare.passed_delta), fontWeight: 600 }}>
                      {delta(compare.passed_delta)}
                    </td>
                  </tr>
                  <tr>
                    <td style={td}>Avg Confidence</td>
                    <td style={td}>{pct(compare.config_a.average_confidence)}</td>
                    <td style={td}>{pct(compare.config_b.average_confidence)}</td>
                    <td style={{ ...td, color: deltaColor(compare.confidence_delta), fontWeight: 600 }}>
                      {delta(compare.confidence_delta)}
                    </td>
                  </tr>
                  <tr>
                    <td style={td}>Avg Latency</td>
                    <td style={td}>{compare.config_a.average_latency_ms.toFixed(0)}ms</td>
                    <td style={td}>{compare.config_b.average_latency_ms.toFixed(0)}ms</td>
                    <td style={{ ...td, color: deltaColor(compare.latency_delta_ms, true), fontWeight: 600 }}>
                      {delta(compare.latency_delta_ms)}ms
                    </td>
                  </tr>
                  <tr>
                    <td style={td}>Avg Hallucination</td>
                    <td style={td}>{pct(compare.config_a.average_hallucination_risk)}</td>
                    <td style={td}>{pct(compare.config_b.average_hallucination_risk)}</td>
                    <td style={{ ...td, color: deltaColor(compare.hallucination_risk_delta, true), fontWeight: 600 }}>
                      {delta(compare.hallucination_risk_delta)}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <h3 style={{ ...sectionTitle, fontSize: "0.9rem" }}>Per-Question Confidence</h3>
            <div style={{ overflowX: "auto" }}>
              <table style={{ width: "100%", borderCollapse: "collapse" }}>
                <thead>
                  <tr>
                    <th style={th}>Question</th>
                    <th style={th}>A</th>
                    <th style={th}>B</th>
                    <th style={th}>Delta</th>
                  </tr>
                </thead>
                <tbody>
                  {compare.per_question.map((q) => (
                    <tr key={q.question}>
                      <td style={{ ...td, maxWidth: 360 }}>{q.question}</td>
                      <td style={td}>{pct(q.confidence_a)}</td>
                      <td style={td}>{pct(q.confidence_b)}</td>
                      <td style={{ ...td, color: deltaColor(q.confidence_delta), fontWeight: 600 }}>
                        {delta(q.confidence_delta)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>

      {retrieval && retrieval.recent_queries.length > 0 && (
        <>
          <h2 style={sectionTitle}>Recent Queries</h2>
          <div style={card}>
            <div style={{ overflowX: "auto" }}>
              <table style={{ width: "100%", borderCollapse: "collapse" }}>
                <thead>
                  <tr>
                    <th style={th}>Question</th>
                    <th style={th}>Confidence</th>
                    <th style={th}>Latency</th>
                    <th style={th}>Cost</th>
                  </tr>
                </thead>
                <tbody>
                  {retrieval.recent_queries.map((q) => (
                    <tr key={q.id}>
                      <td style={{ ...td, maxWidth: 360 }}>{q.question}</td>
                      <td style={td}>{pct(q.confidence)}</td>
                      <td style={td}>{q.latency_ms}ms</td>
                      <td style={td}>${q.estimated_cost_usd.toFixed(6)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <p style={{ marginTop: "0.75rem", fontSize: "0.8rem", color: colors.textMuted }}>
              See the <Link to="/eval" style={{ color: colors.primary }}>Eval Runs</Link> page for saved regression runs.
            </p>
          </div>
        </>
      )}
    </div>
  );
}
