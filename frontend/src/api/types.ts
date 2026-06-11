export interface RowError {
  row: number;
  ticket_id: string | null;
  reason: string;
}

export interface InvalidRow {
  row: number;
  data: Record<string, string>;
  reason: string;
}

export interface UploadResponse {
  batch_id: string;
  filename: string;
  total_count: number;
  valid_count: number;
  invalid_count: number;
  duplicate_count: number;
  embedding_failure_count: number;
  errors: RowError[];
  invalid_rows: InvalidRow[];
}

export interface TicketSummary {
  id: string;
  title: string;
  product_area: string;
  issue_type: string;
  priority: string;
  customer_tier: string;
  status: string;
  created_at: string;
  resolved_at: string | null;
}

export interface TicketListResponse {
  items: TicketSummary[];
  total: number;
  page: number;
  page_size: number;
}

export interface ChunkPreview {
  id: string;
  chunk_index: number;
  preview: string;
}

export interface TicketDetail {
  id: string;
  title: string;
  body: string;
  product_area: string;
  issue_type: string;
  priority: string;
  customer_tier: string;
  status: string;
  resolution: string | null;
  created_at: string;
  resolved_at: string | null;
  ingestion_batch_id: string | null;
  validation_status: string;
  validation_errors: string | null;
  chunks: ChunkPreview[];
}

export interface RagFilters {
  product_area?: string;
  issue_type?: string;
  priority?: string;
  customer_tier?: string;
  status?: string;
}

export interface ChunkDebugInfo {
  cosine_score: number;
  keyword_boost: number;
  keyword_hits: number;
  matched_tokens: string[];
}

export interface RetrievedChunk {
  chunk_id: string;
  ticket_id: string;
  score: number;
  preview: string;
  debug: ChunkDebugInfo | null;
}

export interface QualityScores {
  hallucination_risk: number;
  citation_coverage: number;
  retrieval_precision: number;
  answer_completeness: number;
}

export type FeedbackValue = "helpful" | "not_helpful" | "wrong_citation";

export interface RagQueryResponse {
  query_id: string;
  answer: string;
  citations: string[];
  confidence: number;
  retrieved_chunks: RetrievedChunk[];
  latency_ms: number;
  estimated_cost_usd: number;
  provider: string;
  model: string;
  product_area: string | null;
  is_fallback: boolean;
  quality: QualityScores;
}

export interface FeedbackResponse {
  query_id: string;
  feedback: FeedbackValue;
}

export interface BatchSummary {
  id: string;
  filename: string;
  total_count: number;
  valid_count: number;
  invalid_count: number;
  duplicate_count: number;
  embedding_failure_count: number;
  started_at: string;
  completed_at: string | null;
}

export interface QualityResponse {
  total_batches: number;
  total_rows_seen: number;
  total_valid_rows: number;
  total_invalid_rows: number;
  total_duplicate_rows: number;
  total_embedding_failures: number;
  valid_rate: number;
  invalid_rate: number;
  duplicate_rate: number;
  embedding_failure_rate: number;
  recent_batches: BatchSummary[];
}

export interface RecentQuery {
  id: string;
  question: string;
  confidence: number;
  latency_ms: number;
  estimated_cost_usd: number;
  created_at: string;
}

export interface RetrievalResponse {
  total_queries: number;
  average_confidence: number;
  low_confidence_query_count: number;
  average_latency_ms: number;
  latency_p50_ms: number;
  latency_p95_ms: number;
  latency_p99_ms: number;
  total_estimated_cost_usd: number;
  citation_rate: number;
  average_hallucination_risk: number;
  average_citation_coverage: number;
  average_retrieval_precision: number;
  average_answer_completeness: number;
  recent_queries: RecentQuery[];
}

export interface CostByModel {
  provider: string;
  model: string;
  query_count: number;
  total_cost_usd: number;
}

export interface CostResponse {
  total_estimated_cost_usd: number;
  total_queries: number;
  by_model: CostByModel[];
}

export interface ProductAreaQuality {
  product_area: string;
  query_count: number;
  average_confidence: number;
  average_hallucination_risk: number;
  average_citation_coverage: number;
  average_retrieval_precision: number;
  average_answer_completeness: number;
  citation_rate: number;
}

export interface QualityByAreaResponse {
  areas: ProductAreaQuality[];
}

export interface FailedQuery {
  id: string;
  question: string;
  confidence: number;
  reason: string;
  feedback: FeedbackValue | null;
  product_area: string | null;
  created_at: string;
}

export interface FailedQueriesResponse {
  count: number;
  items: FailedQuery[];
}

export interface EvalRunSummary {
  id: string;
  name: string;
  total_questions: number;
  passed_count: number;
  failed_count: number;
  average_confidence: number;
  average_latency_ms: number;
  results_json: string | null;
  created_at: string;
}

export interface IngestionChartPoint {
  batch_label: string;
  valid: number;
  invalid: number;
  duplicate: number;
}

export interface QueryChartPoint {
  timestamp: string;
  confidence: number;
  latency_ms: number;
  has_citations: boolean;
}

export interface ChartsResponse {
  ingestion: IngestionChartPoint[];
  queries: QueryChartPoint[];
}

export interface SavedEvalQuestion {
  id: string;
  question: string;
  filters_json: string | null;
  created_at: string;
}

export interface EvalConfig {
  label: string;
  top_k: number;
  threshold: number;
}

export interface EvalConfigResult {
  label: string;
  top_k: number;
  threshold: number;
  passed_count: number;
  failed_count: number;
  average_confidence: number;
  average_latency_ms: number;
  average_hallucination_risk: number;
}

export interface EvalQuestionDelta {
  question: string;
  confidence_a: number;
  confidence_b: number;
  confidence_delta: number;
  passed_a: boolean;
  passed_b: boolean;
}

export interface EvalCompareResponse {
  name: string;
  total_questions: number;
  config_a: EvalConfigResult;
  config_b: EvalConfigResult;
  passed_delta: number;
  confidence_delta: number;
  latency_delta_ms: number;
  hallucination_risk_delta: number;
  per_question: EvalQuestionDelta[];
}

// ---------------- V4: workflow integration ----------------

export interface ConnectorSummary {
  id: string;
  provider: string;
  name: string;
  cursor: string | null;
  enabled: boolean;
  last_synced_at: string | null;
  total_imported: number;
  created_at: string;
}

export interface ConnectorListResponse {
  items: ConnectorSummary[];
}

export interface SyncResult {
  connector_id: string;
  batch_id: string;
  fetched: number;
  imported: number;
  duplicate_id: number;
  duplicate_semantic: number;
  embedding_failures: number;
  cursor: string;
  imported_ids: string[];
}

export interface JobSummary {
  id: string;
  connector_id: string;
  interval_minutes: number;
  enabled: boolean;
  next_run_at: string;
  last_run_at: string | null;
  last_status: string | null;
  last_imported: number;
  created_at: string;
}

export interface JobListResponse {
  items: JobSummary[];
}

export interface RunDueResponse {
  ran: number;
  results: SyncResult[];
}

export interface DuplicateTicket {
  id: string;
  title: string;
  product_area: string;
}

export interface DuplicateCluster {
  ticket_ids: string[];
  size: number;
  max_similarity: number;
  tickets: DuplicateTicket[];
}

export interface DuplicatesResponse {
  clusters: DuplicateCluster[];
}

export type Escalation = "answer" | "ask_clarification" | "route_to_human";

export interface AssistRetrieved {
  ticket_id: string;
  score: number;
  preview: string;
  product_area: string | null;
}

export interface AssistResponse {
  recommendation: Escalation;
  recommendation_reason: string;
  confidence: number;
  customer_facing_draft: string;
  internal_note: string;
  citations: string[];
  tier_guidance: string;
  retrieved: AssistRetrieved[];
}

export interface KbArticle {
  id: string;
  title: string;
  product_area: string;
  issue_type: string;
  summary: string;
  resolution_steps: string;
  source_ticket_ids: string[];
  ticket_count: number;
  created_at: string;
}

export interface KbListResponse {
  items: KbArticle[];
}

export interface KbGenerateResponse {
  generated: number;
  items: KbArticle[];
}

export interface SlaRisk {
  ticket_id: string;
  title: string;
  product_area: string;
  priority: string;
  customer_tier: string;
  status: string;
  hours_open: number;
  sla_hours: number;
  due_in_hours: number;
  breached: boolean;
  risk_score: number;
  risk_level: string;
  reason: string;
}

export interface SlaRisksResponse {
  items: SlaRisk[];
  breached_count: number;
  high_risk_count: number;
}

// ---------------- V5: enterprise (auth, governance) ----------------

export interface TokenResponse {
  access_token: string;
  token_type: string;
  role: string;
  email: string;
}

export interface UserResponse {
  id: string;
  email: string;
  role: string;
  is_active: boolean;
  created_at: string;
}

export interface UserListResponse {
  users: UserResponse[];
}

export interface WorkspaceResponse {
  id: string;
  name: string;
  slug: string;
  member_count: number;
  created_at: string;
}

export interface WorkspaceListResponse {
  workspaces: WorkspaceResponse[];
}

export interface MemberResponse {
  membership_id: string;
  user_id: string;
  email: string;
  role: string;
  created_at: string;
}

export interface MemberListResponse {
  workspace_id: string;
  members: MemberResponse[];
}

export interface AuditLogResponse {
  id: string;
  actor_email: string;
  action: string;
  resource_type: string;
  resource_id: string | null;
  workspace_id: string | null;
  detail: string | null;
  ip_address: string | null;
  created_at: string;
}

export interface AuditListResponse {
  total: number;
  logs: AuditLogResponse[];
}

export interface SettingsResponse {
  llm_provider: string;
  embedding_provider: string;
  llm_model: string;
  embedding_model: string;
  low_confidence_threshold: number;
  default_top_k: number;
  vector_backend: string;
  pii_redaction_enabled: boolean;
  retention_rag_query_days: number;
  retention_audit_log_days: number;
  active_prompt_id: string | null;
}

export interface SettingsUpdate {
  llm_provider?: string;
  embedding_provider?: string;
  llm_model?: string;
  embedding_model?: string;
  low_confidence_threshold?: number;
  default_top_k?: number;
  vector_backend?: string;
  pii_redaction_enabled?: boolean;
  retention_rag_query_days?: number;
  retention_audit_log_days?: number;
  active_prompt_id?: string;
}

export interface VectorBackendStatus {
  configured: string;
  dialect: string;
  pgvector_importable: boolean;
  extension_present: boolean;
  active_backend: string;
  reason: string;
}

export interface RetentionPreviewResponse {
  retention_rag_query_days: number;
  retention_audit_log_days: number;
  rag_queries_to_purge: number;
  audit_logs_to_purge: number;
}

export interface RetentionRunResponse {
  rag_queries_deleted: number;
  audit_logs_deleted: number;
}

export interface PiiMatch {
  type: string;
  value: string;
  start: number;
  end: number;
}

export interface PiiScanResponse {
  matches: PiiMatch[];
  counts: Record<string, number>;
  redacted_text: string;
}

export interface PromptResponse {
  id: string;
  name: string;
  version: number;
  content: string;
  is_active: boolean;
  created_at: string;
}

export interface PromptListResponse {
  prompts: PromptResponse[];
  active_id: string | null;
}

export interface BgJobResponse {
  id: string;
  job_type: string;
  status: string;
  payload_json: string | null;
  result_json: string | null;
  error: string | null;
  attempts: number;
  created_at: string;
  started_at: string | null;
  finished_at: string | null;
}

export interface BgJobListResponse {
  jobs: BgJobResponse[];
}

export interface BgJobProcessResponse {
  processed: number;
  succeeded: number;
  failed: number;
  jobs: BgJobResponse[];
}
