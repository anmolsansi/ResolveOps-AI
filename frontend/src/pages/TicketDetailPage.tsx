import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { getTicket } from "../api/client";
import type { TicketDetail } from "../api/types";
import ErrorState from "../components/ErrorState";
import LoadingState from "../components/LoadingState";
import { badge, card, colors, pageTitle, sectionTitle } from "../styles";

export default function TicketDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [ticket, setTicket] = useState<TicketDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!id) return;
    getTicket(id)
      .then(setTicket)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) return <LoadingState />;
  if (error) return <ErrorState message={error} />;
  if (!ticket) return <ErrorState message="Ticket not found" />;

  const fields = [
    { label: "ID", value: ticket.id },
    { label: "Product Area", value: ticket.product_area },
    { label: "Issue Type", value: ticket.issue_type },
    { label: "Priority", value: ticket.priority },
    { label: "Customer Tier", value: ticket.customer_tier },
    { label: "Status", value: ticket.status },
    { label: "Created", value: new Date(ticket.created_at).toLocaleString() },
    { label: "Resolved", value: ticket.resolved_at ? new Date(ticket.resolved_at).toLocaleString() : "-" },
    { label: "Validation", value: ticket.validation_status },
    { label: "Batch ID", value: ticket.ingestion_batch_id ?? "-" },
  ];

  return (
    <div>
      <div style={{ marginBottom: "0.5rem" }}>
        <Link to="/tickets" style={{ color: colors.primary, fontSize: "0.85rem", textDecoration: "none" }}>
          &larr; Back to Tickets
        </Link>
      </div>

      <h1 style={pageTitle}>{ticket.title}</h1>

      <div style={{ ...card, marginBottom: "1.5rem" }}>
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "auto 1fr",
            gap: "0.4rem 1.5rem",
          }}
        >
          {fields.map(({ label, value }) => (
            <div key={label} style={{ display: "contents" }}>
              <span style={{ fontWeight: 600, fontSize: "0.85rem", color: colors.textMuted }}>{label}</span>
              <span style={{ fontSize: "0.85rem", color: colors.text }}>
                {label === "Status" ? (
                  <span style={badge(ticket.status === "Resolved" ? colors.success : colors.primary)}>
                    {value}
                  </span>
                ) : (
                  value
                )}
              </span>
            </div>
          ))}
        </div>
      </div>

      <div style={{ ...card, marginBottom: "1.5rem" }}>
        <h2 style={sectionTitle}>Body</h2>
        <div style={{ whiteSpace: "pre-wrap", lineHeight: 1.6, color: colors.text, fontSize: "0.9rem" }}>
          {ticket.body}
        </div>
      </div>

      {ticket.resolution && (
        <div style={{ ...card, marginBottom: "1.5rem", borderLeft: `3px solid ${colors.success}` }}>
          <h2 style={sectionTitle}>Resolution</h2>
          <div style={{ whiteSpace: "pre-wrap", lineHeight: 1.6, color: colors.text, fontSize: "0.9rem" }}>
            {ticket.resolution}
          </div>
        </div>
      )}

      {ticket.chunks.length > 0 && (
        <div style={card}>
          <h2 style={sectionTitle}>Chunks ({ticket.chunks.length})</h2>
          {ticket.chunks.map((c) => (
            <div
              key={c.id}
              style={{
                border: `1px solid ${colors.border}`,
                borderRadius: 8,
                padding: "0.75rem",
                marginBottom: "0.5rem",
                background: colors.bg,
              }}
            >
              <span style={{ fontWeight: 600, fontSize: "0.8rem", color: colors.textMuted }}>
                Chunk {c.chunk_index}
              </span>
              <div style={{ marginTop: 4, fontSize: "0.85rem", color: colors.text }}>{c.preview}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
