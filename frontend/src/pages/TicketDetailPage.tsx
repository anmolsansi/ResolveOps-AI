import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { getTicket } from "../api/client";
import type { TicketDetail } from "../api/types";
import ErrorState from "../components/ErrorState";
import LoadingState from "../components/LoadingState";

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

  return (
    <div>
      <h1>{ticket.title}</h1>
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "auto 1fr",
          gap: "0.5rem 1rem",
          marginBottom: "1.5rem",
        }}
      >
        <strong>ID:</strong> <span>{ticket.id}</span>
        <strong>Product Area:</strong> <span>{ticket.product_area}</span>
        <strong>Issue Type:</strong> <span>{ticket.issue_type}</span>
        <strong>Priority:</strong> <span>{ticket.priority}</span>
        <strong>Customer Tier:</strong> <span>{ticket.customer_tier}</span>
        <strong>Status:</strong> <span>{ticket.status}</span>
        <strong>Created:</strong> <span>{new Date(ticket.created_at).toLocaleString()}</span>
        <strong>Resolved:</strong>
        <span>{ticket.resolved_at ? new Date(ticket.resolved_at).toLocaleString() : "-"}</span>
        <strong>Validation:</strong> <span>{ticket.validation_status}</span>
        <strong>Batch ID:</strong> <span>{ticket.ingestion_batch_id ?? "-"}</span>
      </div>

      <h2>Body</h2>
      <div
        style={{
          background: "#f8f9fa",
          padding: "1rem",
          borderRadius: 8,
          whiteSpace: "pre-wrap",
          marginBottom: "1.5rem",
        }}
      >
        {ticket.body}
      </div>

      {ticket.resolution && (
        <>
          <h2>Resolution</h2>
          <div
            style={{
              background: "#f0fff0",
              padding: "1rem",
              borderRadius: 8,
              whiteSpace: "pre-wrap",
              marginBottom: "1.5rem",
            }}
          >
            {ticket.resolution}
          </div>
        </>
      )}

      {ticket.chunks.length > 0 && (
        <>
          <h2>Chunks</h2>
          {ticket.chunks.map((c) => (
            <div
              key={c.id}
              style={{
                border: "1px solid #ddd",
                borderRadius: 8,
                padding: "0.75rem",
                marginBottom: "0.5rem",
              }}
            >
              <strong>Chunk {c.chunk_index}:</strong> {c.preview}
            </div>
          ))}
        </>
      )}
    </div>
  );
}
