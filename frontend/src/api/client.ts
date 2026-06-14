import type {
  AssistResponse,
  AuditListResponse,
  BgJobListResponse,
  BgJobProcessResponse,
  BgJobResponse,
  ChartsResponse,
  ConnectorListResponse,
  ConnectorSummary,
  ConversationDetailResponse,
  ConversationListResponse,
  CostResponse,
  CustomerListResponse,
  CustomerProfileDetailResponse,
  DuplicatesResponse,
  EvalCompareResponse,
  EvalConfig,
  EvalRunSummary,
  FailedQueriesResponse,
  FeedbackResponse,
  FeedbackValue,
  HandoffListResponse,
  JobListResponse,
  JobSummary,
  KbGenerateResponse,
  KbListResponse,
  MemberListResponse,
  MemberResponse,
  PiiScanResponse,
  PromptListResponse,
  PromptResponse,
  QualityByAreaResponse,
  QualityResponse,
  RagFilters,
  RagQueryResponse,
  ResolutionOutcomeResponse,
  RetentionPreviewResponse,
  RetentionRunResponse,
  RetrievalResponse,
  RunDueResponse,
  SavedEvalQuestion,
  SettingsResponse,
  SettingsUpdate,
  SlaRisksResponse,
  SyncResult,
  TicketDetail,
  TicketListResponse,
  TokenResponse,
  UploadResponse,
  UserListResponse,
  UserResponse,
  VectorBackendStatus,
  WorkspaceListResponse,
  WorkspaceResponse,
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

export async function submitFeedback(
  queryId: string,
  feedback: FeedbackValue,
): Promise<FeedbackResponse> {
  return request<FeedbackResponse>(`/rag/queries/${queryId}/feedback`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ feedback }),
  });
}

export async function getQualityMetrics(): Promise<QualityResponse> {
  return request<QualityResponse>("/dashboard/quality");
}

export async function getCostMetrics(): Promise<CostResponse> {
  return request<CostResponse>("/dashboard/cost");
}

export async function getQualityByArea(): Promise<QualityByAreaResponse> {
  return request<QualityByAreaResponse>("/dashboard/quality-by-area");
}

export async function getFailedQueries(): Promise<FailedQueriesResponse> {
  return request<FailedQueriesResponse>("/dashboard/failed-queries");
}

export async function getRetrievalMetrics(): Promise<RetrievalResponse> {
  return request<RetrievalResponse>("/dashboard/retrieval");
}

export async function getChartsData(): Promise<ChartsResponse> {
  return request<ChartsResponse>("/dashboard/charts");
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

export async function compareEval(
  configA: EvalConfig,
  configB: EvalConfig,
  name?: string,
): Promise<EvalCompareResponse> {
  return request<EvalCompareResponse>("/eval/compare", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, config_a: configA, config_b: configB }),
  });
}

export function getEvalExportUrl(runId: string, format: "csv" | "json"): string {
  return `${API_BASE}/eval/runs/${runId}/export?format=${format}`;
}

export async function listEvalQuestions(): Promise<SavedEvalQuestion[]> {
  return request<SavedEvalQuestion[]>("/eval/questions");
}

export async function createEvalQuestion(
  question: string,
  filters?: Record<string, string>,
): Promise<SavedEvalQuestion> {
  return request<SavedEvalQuestion>("/eval/questions", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, filters: filters || null }),
  });
}

export async function updateEvalQuestion(
  id: string,
  question: string,
  filters?: Record<string, string>,
): Promise<SavedEvalQuestion> {
  return request<SavedEvalQuestion>(`/eval/questions/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, filters: filters || null }),
  });
}

export async function deleteEvalQuestion(id: string): Promise<void> {
  const res = await fetch(`${API_BASE}/eval/questions/${id}`, { method: "DELETE" });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`API error ${res.status}: ${body}`);
  }
}

// ---------------- V4: workflow integration ----------------

export async function listConnectors(): Promise<ConnectorListResponse> {
  return request<ConnectorListResponse>("/connectors");
}

export async function createConnector(
  provider: string,
  name: string,
): Promise<ConnectorSummary> {
  return request<ConnectorSummary>("/connectors", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ provider, name }),
  });
}

export async function deleteConnector(id: string): Promise<void> {
  const res = await fetch(`${API_BASE}/connectors/${id}`, { method: "DELETE" });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`API error ${res.status}: ${body}`);
  }
}

export async function syncConnector(id: string, limit = 6): Promise<SyncResult> {
  return request<SyncResult>(`/connectors/${id}/sync?limit=${limit}`, {
    method: "POST",
  });
}

export async function listJobs(): Promise<JobListResponse> {
  return request<JobListResponse>("/connectors/jobs");
}

export async function createJob(
  connectorId: string,
  intervalMinutes: number,
): Promise<JobSummary> {
  return request<JobSummary>(`/connectors/${connectorId}/jobs`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ interval_minutes: intervalMinutes }),
  });
}

export async function runDueJobs(limit = 6): Promise<RunDueResponse> {
  return request<RunDueResponse>(`/connectors/jobs/run-due?limit=${limit}`, {
    method: "POST",
  });
}

export async function getDuplicates(): Promise<DuplicatesResponse> {
  return request<DuplicatesResponse>("/connectors/duplicates");
}

export async function assistDraft(payload: {
  subject: string;
  body?: string;
  customer_tier?: string;
  product_area?: string;
  top_k?: number;
}): Promise<AssistResponse> {
  return request<AssistResponse>("/assist/draft", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export async function generateKb(): Promise<KbGenerateResponse> {
  return request<KbGenerateResponse>("/kb/generate", { method: "POST" });
}

export async function listKbArticles(): Promise<KbListResponse> {
  return request<KbListResponse>("/kb/articles");
}

export async function getSlaRisks(): Promise<SlaRisksResponse> {
  return request<SlaRisksResponse>("/sla/risks");
}

// ---------------- V5: auth + enterprise governance ----------------

const TOKEN_KEY = "resolveops_token";

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken(): void {
  localStorage.removeItem(TOKEN_KEY);
}

function authHeaders(extra?: Record<string, string>): Record<string, string> {
  const headers: Record<string, string> = { ...(extra || {}) };
  const token = getToken();
  if (token) headers.Authorization = `Bearer ${token}`;
  return headers;
}

export async function register(
  email: string,
  password: string,
  role?: string,
): Promise<TokenResponse> {
  return request<TokenResponse>("/auth/register", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password, role }),
  });
}

export async function login(email: string, password: string): Promise<TokenResponse> {
  return request<TokenResponse>("/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
}

export async function getMe(): Promise<UserResponse> {
  return request<UserResponse>("/auth/me", { headers: authHeaders() });
}

export async function listUsers(): Promise<UserListResponse> {
  return request<UserListResponse>("/auth/users", { headers: authHeaders() });
}

export async function updateUserRole(userId: string, role: string): Promise<UserResponse> {
  return request<UserResponse>(`/auth/users/${userId}/role`, {
    method: "PUT",
    headers: authHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify({ role }),
  });
}

export async function listWorkspaces(): Promise<WorkspaceListResponse> {
  return request<WorkspaceListResponse>("/workspaces", { headers: authHeaders() });
}

export async function createWorkspace(name: string): Promise<WorkspaceResponse> {
  return request<WorkspaceResponse>("/workspaces", {
    method: "POST",
    headers: authHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify({ name }),
  });
}

export async function listMembers(workspaceId: string): Promise<MemberListResponse> {
  return request<MemberListResponse>(`/workspaces/${workspaceId}/members`, {
    headers: authHeaders(),
  });
}

export async function addMember(
  workspaceId: string,
  email: string,
  role: string,
): Promise<MemberResponse> {
  return request<MemberResponse>(`/workspaces/${workspaceId}/members`, {
    method: "POST",
    headers: authHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify({ email, role }),
  });
}

export async function getAuditLogs(params?: {
  action?: string;
  actor_email?: string;
  limit?: number;
}): Promise<AuditListResponse> {
  const qs = new URLSearchParams();
  for (const [k, v] of Object.entries(params || {})) {
    if (v !== undefined && v !== "") qs.set(k, String(v));
  }
  return request<AuditListResponse>(`/audit?${qs.toString()}`, { headers: authHeaders() });
}

export async function getSettings(): Promise<SettingsResponse> {
  return request<SettingsResponse>("/settings", { headers: authHeaders() });
}

export async function updateSettings(update: SettingsUpdate): Promise<SettingsResponse> {
  return request<SettingsResponse>("/settings", {
    method: "PUT",
    headers: authHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify(update),
  });
}

export async function getVectorBackend(): Promise<VectorBackendStatus> {
  return request<VectorBackendStatus>("/settings/vector-backend", { headers: authHeaders() });
}

export async function previewRetention(): Promise<RetentionPreviewResponse> {
  return request<RetentionPreviewResponse>("/retention", { headers: authHeaders() });
}

export async function runRetention(): Promise<RetentionRunResponse> {
  return request<RetentionRunResponse>("/retention/run", {
    method: "POST",
    headers: authHeaders(),
  });
}

export async function scanPii(text: string): Promise<PiiScanResponse> {
  return request<PiiScanResponse>("/pii/scan", {
    method: "POST",
    headers: authHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify({ text }),
  });
}

export async function listPrompts(): Promise<PromptListResponse> {
  return request<PromptListResponse>("/prompts", { headers: authHeaders() });
}

export async function createPrompt(
  name: string,
  content: string,
  activate: boolean,
): Promise<PromptResponse> {
  return request<PromptResponse>("/prompts", {
    method: "POST",
    headers: authHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify({ name, content, activate }),
  });
}

export async function activatePrompt(promptId: string): Promise<PromptResponse> {
  return request<PromptResponse>(`/prompts/${promptId}/activate`, {
    method: "POST",
    headers: authHeaders(),
  });
}

export async function listBgJobs(status?: string): Promise<BgJobListResponse> {
  const qs = status ? `?status=${encodeURIComponent(status)}` : "";
  return request<BgJobListResponse>(`/jobs${qs}`, { headers: authHeaders() });
}

export async function createBgJob(
  jobType: string,
  payload?: Record<string, unknown>,
): Promise<BgJobResponse> {
  return request<BgJobResponse>("/jobs", {
    method: "POST",
    headers: authHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify({ job_type: jobType, payload }),
  });
}

export async function processPendingJobs(limit = 10): Promise<BgJobProcessResponse> {
  return request<BgJobProcessResponse>(`/jobs/process-pending?limit=${limit}`, {
    method: "POST",
    headers: authHeaders(),
  });
}

// ---------------- V6: Customer-Facing AI Support Agent ----------------

export async function listConversations(params: {
  page?: number;
  page_size?: number;
  status?: string;
  channel?: string;
}): Promise<ConversationListResponse> {
  const qs = new URLSearchParams();
  for (const [k, v] of Object.entries(params)) {
    if (v !== undefined && v !== "") qs.set(k, String(v));
  }
  return request<ConversationListResponse>(`/conversations?${qs.toString()}`, { headers: authHeaders() });
}

export async function getConversation(id: string): Promise<ConversationDetailResponse> {
  return request<ConversationDetailResponse>(`/conversations/${encodeURIComponent(id)}`, { headers: authHeaders() });
}

export async function updateConversationStatus(id: string, status: string): Promise<void> {
  await request(`/conversations/${encodeURIComponent(id)}/status`, {
    method: "PUT",
    headers: authHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify({ status }),
  });
}

export async function sendAgentReply(id: string, content: string): Promise<{ id: string; role: string; content: string; created_at: string }> {
  return request(`/conversations/${encodeURIComponent(id)}/reply`, {
    method: "POST",
    headers: authHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify({ content }),
  });
}

export async function resolveConversation(
  id: string,
  outcome: string,
  notes?: string,
): Promise<ResolutionOutcomeResponse> {
  return request<ResolutionOutcomeResponse>(`/conversations/${encodeURIComponent(id)}/resolve`, {
    method: "POST",
    headers: authHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify({ outcome, notes }),
  });
}

export async function listHandoffs(params?: { status?: string }): Promise<HandoffListResponse> {
  const qs = params?.status ? `?status=${encodeURIComponent(params.status)}` : "";
  return request<HandoffListResponse>(`/conversations/handoffs${qs}`, { headers: authHeaders() });
}

export async function updateHandoff(id: string, status: string): Promise<void> {
  await request(`/conversations/handoffs/${encodeURIComponent(id)}`, {
    method: "PUT",
    headers: authHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify({ status }),
  });
}

export async function listCustomers(params: {
  page?: number;
  page_size?: number;
}): Promise<CustomerListResponse> {
  const qs = new URLSearchParams();
  for (const [k, v] of Object.entries(params)) {
    if (v !== undefined && v !== "") qs.set(k, String(v));
  }
  return request<CustomerListResponse>(`/conversations/customers?${qs.toString()}`, { headers: authHeaders() });
}

export async function getCustomer(id: string): Promise<CustomerProfileDetailResponse> {
  return request<CustomerProfileDetailResponse>(`/conversations/customers/${encodeURIComponent(id)}`, { headers: authHeaders() });
}

// ---------------- V7: Action-Taking Agent Workflows ----------------

export async function listTools(): Promise<ToolListResponse> {
  return request<ToolListResponse>("/tools", { headers: authHeaders() });
}

export async function getTool(toolId: string): Promise<ToolSummary> {
  return request<ToolSummary>(`/tools/${encodeURIComponent(toolId)}`, { headers: authHeaders() });
}

export async function updateTool(
  toolId: string,
  update: { enabled?: boolean; description?: string },
): Promise<ToolSummary> {
  return request<ToolSummary>(`/tools/${encodeURIComponent(toolId)}`, {
    method: "PUT",
    headers: authHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify(update),
  });
}

export async function executeTool(
  toolId: string,
  parameters: Record<string, unknown>,
  conversationId?: string,
): Promise<ToolExecutionResponse> {
  return request<ToolExecutionResponse>(`/tools/${encodeURIComponent(toolId)}/execute`, {
    method: "POST",
    headers: authHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify({ parameters, conversation_id: conversationId || null }),
  });
}

export async function listToolExecutions(): Promise<ToolExecutionListResponse> {
  return request<ToolExecutionListResponse>("/tools/executions", { headers: authHeaders() });
}

export async function listActionLogs(): Promise<ActionLogListResponse> {
  return request<ActionLogListResponse>("/tools/action-logs", { headers: authHeaders() });
}
