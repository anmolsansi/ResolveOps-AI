import type {
  EvalRunSummary,
  QualityResponse,
  RagFilters,
  RagQueryResponse,
  RetrievalResponse,
  TicketDetail,
  TicketListResponse,
  UploadResponse,
} from "./types";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, init);
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`API error ${res.status}: ${body}`);
  }
  return res.json() as Promise<T>;
}

export async function uploadTickets(file: File): Promise<UploadResponse> {
  const form = new FormData();
  form.append("file", file);
  return request<UploadResponse>("/tickets/upload", { method: "POST", body: form });
}

export async function listTickets(params: {
  page?: number;
  page_size?: number;
  product_area?: string;
  issue_type?: string;
  priority?: string;
  customer_tier?: string;
  status?: string;
  search?: string;
}): Promise<TicketListResponse> {
  const qs = new URLSearchParams();
  for (const [k, v] of Object.entries(params)) {
    if (v !== undefined && v !== "") qs.set(k, String(v));
  }
  return request<TicketListResponse>(`/tickets?${qs.toString()}`);
}

export async function getTicket(id: string): Promise<TicketDetail> {
  return request<TicketDetail>(`/tickets/${encodeURIComponent(id)}`);
}

export async function ragQuery(
  question: string,
  filters?: RagFilters,
  top_k?: number,
): Promise<RagQueryResponse> {
  return request<RagQueryResponse>("/rag/query", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, filters, top_k }),
  });
}

export async function getQualityMetrics(): Promise<QualityResponse> {
  return request<QualityResponse>("/dashboard/quality");
}

export async function getRetrievalMetrics(): Promise<RetrievalResponse> {
  return request<RetrievalResponse>("/dashboard/retrieval");
}

export async function runEval(name?: string): Promise<EvalRunSummary> {
  return request<EvalRunSummary>("/eval/run", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name }),
  });
}

export async function listEvalRuns(): Promise<EvalRunSummary[]> {
  return request<EvalRunSummary[]>("/eval/runs");
}
