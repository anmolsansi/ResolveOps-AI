import { useEffect, useState } from "react";
import { getSlaRisks } from "../api/client";
import type { SlaRisk } from "../api/types";
import ErrorState from "../components/ErrorState";
import LoadingState from "../components/LoadingState";
import MetricCard from "../components/MetricCard";
import { badge, card, colors, pageTitle, sectionTitle, td, th } from "../styles";

const LEVEL_COLOR: Record<string, string> = {
  high: colors.danger,
  medium: colors.warning,
  low: colors.success,
};

export default function SlaPage() {
  const [risks, setRisks] = useState<SlaRisk[]>([]);
  const [breached, setBreached] = useState(0);
  const [highRisk, setHighRisk] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    (async () => {
      try {
        const data = await getSlaRisks();
        setRisks(data.items);
        setBreached(data.breached_count);
        setHighRisk(data.high_risk_count);
      } catch (e) {
        setError(e instanceof Error ? e.message : "Failed to load");
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  return (
    <div>
      <h1 style={pageTitle}>SLA Risk</h1>
      <p style={{ color: colors.textMuted, marginTop: "-1rem", marginBottom: "1.5rem" }}>
        Open tickets ranked by SLA breach risk, weighted by priority and customer tier.
      </p>

      {error && <ErrorState message={error} />}
      {loading && <LoadingState message="Computing SLA risk..." />}

      {!loading && (
        <>
          <div style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap", marginBottom: "1.5rem" }}>
            <MetricCard label="Open at risk" value={risks.length} />
            <MetricCard label="SLA breached" value={breached} accent={colors.danger} />
            <MetricCard label="High risk" value={highRisk} accent={colors.warning} />
          </div>

          <div style={card}>
            <h2 style={sectionTitle}>Risk queue</h2>
            {risks.length === 0 ? (
              <p style={{ color: colors.textMuted }}>No open tickets at risk.</p>
            ) : (
              <div style={{ overflowX: "auto" }}>
                <table style={{ width: "100%", borderCollapse: "collapse" }}>
                  <thead>
                    <tr>
                      <th style={th}>Risk</th>
                      <th style={th}>Ticket</th>
                      <th style={th}>Priority</th>
                      <th style={th}>Tier</th>
                      <th style={th}>Open (h)</th>
                      <th style={th}>SLA</th>
                      <th style={th}>Reason</th>
                    </tr>
                  </thead>
                  <tbody>
                    {risks.map((r) => (
                      <tr key={r.ticket_id}>
                        <td style={td}>
                          <span style={badge(LEVEL_COLOR[r.risk_level] || colors.textMuted)}>
                            {r.risk_level} {(r.risk_score * 100).toFixed(0)}
                          </span>
                        </td>
                        <td style={td}>
                          <a
                            href={`/tickets/${encodeURIComponent(r.ticket_id)}`}
                            style={{ color: colors.primary, textDecoration: "none" }}
                          >
                            {r.ticket_id}
                          </a>
                          <div style={{ fontSize: "0.78rem", color: colors.textMuted }}>{r.title}</div>
                        </td>
                        <td style={td}>{r.priority}</td>
                        <td style={td}>{r.customer_tier}</td>
                        <td style={td}>{r.hours_open}</td>
                        <td style={td}>
                          {r.breached ? (
                            <span style={badge(colors.danger)}>breached</span>
                          ) : (
                            `${r.sla_hours}h`
                          )}
                        </td>
                        <td style={{ ...td, color: colors.textMuted }}>{r.reason}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}
