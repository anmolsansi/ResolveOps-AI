import { useEffect, useReducer, useState } from "react";
import { Link } from "react-router-dom";
import { listTickets } from "../api/client";
import type { TicketSummary } from "../api/types";
import ErrorState from "../components/ErrorState";
import LoadingState from "../components/LoadingState";

interface State {
  tickets: TicketSummary[];
  total: number;
  loading: boolean;
  error: string;
}

type Action =
  | { type: "loading" }
  | { type: "success"; tickets: TicketSummary[]; total: number }
  | { type: "error"; message: string };

function reducer(state: State, action: Action): State {
  switch (action.type) {
    case "loading":
      return { ...state, loading: true, error: "" };
    case "success":
      return { tickets: action.tickets, total: action.total, loading: false, error: "" };
    case "error":
      return { ...state, loading: false, error: action.message };
  }
}

export default function TicketsPage() {
  const [state, dispatch] = useReducer(reducer, {
    tickets: [],
    total: 0,
    loading: true,
    error: "",
  });
  const [page, setPage] = useState(1);
  const pageSize = 20;

  const [productArea, setProductArea] = useState("");
  const [issueType, setIssueType] = useState("");
  const [priority, setPriority] = useState("");
  const [customerTier, setCustomerTier] = useState("");
  const [status, setStatus] = useState("");
  const [search, setSearch] = useState("");
  const [filterKey, setFilterKey] = useState(0);

  useEffect(() => {
    let cancelled = false;
    dispatch({ type: "loading" });
    listTickets({
      page,
      page_size: pageSize,
      product_area: productArea || undefined,
      issue_type: issueType || undefined,
      priority: priority || undefined,
      customer_tier: customerTier || undefined,
      status: status || undefined,
      search: search || undefined,
    })
      .then((data) => {
        if (!cancelled) dispatch({ type: "success", tickets: data.items, total: data.total });
      })
      .catch((e: Error) => {
        if (!cancelled) dispatch({ type: "error", message: e.message });
      });
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [page, filterKey]);

  const handleFilter = () => {
    setPage(1);
    setFilterKey((n) => n + 1);
  };

  const totalPages = Math.ceil(state.total / pageSize);

  return (
    <div>
      <h1>Tickets</h1>

      <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap", marginBottom: "1rem" }}>
        <input placeholder="Search..." value={search} onChange={(e) => setSearch(e.target.value)} />
        <input
          placeholder="Product Area"
          value={productArea}
          onChange={(e) => setProductArea(e.target.value)}
        />
        <input
          placeholder="Issue Type"
          value={issueType}
          onChange={(e) => setIssueType(e.target.value)}
        />
        <input
          placeholder="Priority"
          value={priority}
          onChange={(e) => setPriority(e.target.value)}
        />
        <input
          placeholder="Customer Tier"
          value={customerTier}
          onChange={(e) => setCustomerTier(e.target.value)}
        />
        <input
          placeholder="Status"
          value={status}
          onChange={(e) => setStatus(e.target.value)}
        />
        <button onClick={handleFilter}>Filter</button>
      </div>

      {state.loading && <LoadingState />}
      {state.error && <ErrorState message={state.error} />}

      {!state.loading && (
        <>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr>
                <th style={th}>ID</th>
                <th style={th}>Title</th>
                <th style={th}>Product Area</th>
                <th style={th}>Type</th>
                <th style={th}>Priority</th>
                <th style={th}>Tier</th>
                <th style={th}>Status</th>
                <th style={th}>Created</th>
              </tr>
            </thead>
            <tbody>
              {state.tickets.map((t) => (
                <tr key={t.id}>
                  <td style={td}>
                    <Link to={`/tickets/${t.id}`}>{t.id}</Link>
                  </td>
                  <td style={td}>{t.title}</td>
                  <td style={td}>{t.product_area}</td>
                  <td style={td}>{t.issue_type}</td>
                  <td style={td}>{t.priority}</td>
                  <td style={td}>{t.customer_tier}</td>
                  <td style={td}>{t.status}</td>
                  <td style={td}>{new Date(t.created_at).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>

          <div style={{ marginTop: "1rem", display: "flex", gap: "0.5rem", alignItems: "center" }}>
            <button disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>
              Prev
            </button>
            <span>
              Page {page} of {totalPages || 1} ({state.total} total)
            </span>
            <button disabled={page >= totalPages} onClick={() => setPage((p) => p + 1)}>
              Next
            </button>
          </div>
        </>
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
