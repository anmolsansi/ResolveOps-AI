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

// ---------------- V6: Customer-Facing AI Support Agent ----------------

export interface ConversationSummary {
  id: string;
  channel: string;
  status: string;
  subject: string | null;
  customer_name: string | null;
  customer_email: string | null;
  sentiment: string | null;
  ai_resolution_outcome: string | null;
  last_message_at: string;
  created_at: string;
}

export interface ConversationListResponse {
  items: ConversationSummary[];
  total: number;
  page: number;
  page_size: number;
}

export interface ConversationMessageResponse {
  id: string;
  role: string;
  content: string;
  citations: string[] | null;
  confidence: number | null;
  is_escalation_trigger: boolean;
  created_at: string;
}

export interface ConversationCustomerSummary {
  id: string;
  external_id: string;
  name: string | null;
  email: string | null;
  company: string | null;
  customer_tier: string;
  sentiment_score: number;
  total_conversations: number;
  unresolved_issues: number;
}

export interface ConversationHandoffSummary {
  id: string;
  trigger_reason: string;
  summary: string;
  likely_intent: string;
  suggested_reply: string | null;
  status: string;
  assigned_to: string | null;
  created_at: string;
  resolved_at: string | null;
}

export interface ConversationDetailResponse {
  id: string;
  channel: string;
  status: string;
  subject: string | null;
  product_area: string | null;
  sentiment: string | null;
  ai_resolution_outcome: string | null;
  resolution_summary: string | null;
  customer: ConversationCustomerSummary | null;
  messages: ConversationMessageResponse[];
  handoffs: ConversationHandoffSummary[];
  started_at: string;
  last_message_at: string;
  resolved_at: string | null;
  created_at: string;
}

export interface CustomerProfileResponse {
  id: string;
  external_id: string;
  name: string | null;
  email: string | null;
  company: string | null;
  customer_tier: string;
  sentiment_score: number;
  total_conversations: number;
  unresolved_issues: number;
  last_seen_at: string | null;
  created_at: string;
}

export interface CustomerListResponse {
  items: CustomerProfileResponse[];
  total: number;
  page: number;
  page_size: number;
}

export interface CustomerTimelineItem {
  conversation_id: string;
  channel: string;
  status: string;
  subject: string | null;
  summary: string | null;
  created_at: string;
}

export interface CustomerProfileDetailResponse {
  profile: CustomerProfileResponse;
  timeline: CustomerTimelineItem[];
}

export interface HandoffResponse {
  id: string;
  trigger_reason: string;
  summary: string;
  likely_intent: string;
  suggested_reply: string | null;
  status: string;
  assigned_to: string | null;
  created_at: string;
  resolved_at: string | null;
}

export interface HandoffListResponse {
  items: HandoffResponse[];
  pending_count: number;
}

export interface ResolutionOutcomeResponse {
  id: string;
  conversation_id: string;
  outcome: string;
  confidence_at_resolution: number;
  total_messages: number;
  ai_message_count: number;
  human_message_count: number;
  created_at: string;
}

// ---------------- V7: Action-Taking Agent Workflows ----------------

export interface ToolSummary {
  id: string;
  name: string;
  slug: string;
  description: string;
  handler: string;
  enabled: boolean;
  category: string;
  parameters_schema: Record<string, unknown>;
  created_at: string;
}

export interface ToolListResponse {
  items: ToolSummary[];
  total: number;
}

export interface ToolExecutionResponse {
  id: string;
  tool_id: string;
  tool_name: string;
  input: Record<string, unknown>;
  output: Record<string, unknown> | null;
  status: string;
  error: string | null;
  latency_ms: number | null;
  triggered_by: string;
  created_at: string;
}

export interface ToolExecutionListResponse {
  items: ToolExecutionResponse[];
  total: number;
}

export interface ActionLogResponse {
  id: string;
  action_type: string;
  resource_type: string;
  resource_id: string | null;
  tool_execution_id: string | null;
  detail: string | null;
  actor: string;
  created_at: string;
}

export interface ActionLogListResponse {
  items: ActionLogResponse[];
  total: number;
}

// ---------------- V8: Agent Intelligence & Feedback Loop ----------------

export interface ToolUsageStats {
  tool_name: string;
  slug: string;
  total_executions: number;
  success_count: number;
  failure_count: number;
  average_latency_ms: number;
}

export interface PerformanceMetricsResponse {
  total_conversations: number;
  resolved_conversations: number;
  ai_contained: number;
  human_escalated: number;
  containment_rate: number;
  average_resolution_time_seconds: number | null;
  total_tool_executions: number;
  tool_success_rate: number;
  tool_usage: ToolUsageStats[];
  sentiment_distribution: Record<string, number>;
  top_escalation_reasons: Array<{ reason: string; count: number }>;
}

export interface KbSuggestionResponse {
  id: string;
  suggested_title: string;
  suggested_content: string;
  product_area: string | null;
  issue_type: string | null;
  source_conversation_ids: string[];
  occurrence_count: number;
  status: string;
  created_at: string;
}

export interface KbSuggestionListResponse {
  items: KbSuggestionResponse[];
  total: number;
}

export interface CopilotSuggestionResponse {
  id: string;
  suggestion_type: string;
  title: string;
  content: string;
  confidence: number;
  status: string;
  conversation_id: string | null;
  created_at: string;
}

export interface CopilotSuggestionListResponse {
  items: CopilotSuggestionResponse[];
  total: number;
}

export interface ConversationSummaryResponse {
  id: string;
  conversation_id: string;
  summary: string;
  resolution_steps: string | null;
  key_topics: string[];
  sentiment_at_resolution: string | null;
  created_at: string;
}

export interface ConversationSummaryListResponse {
  items: ConversationSummaryResponse[];
  total: number;
}

export interface FeedbackSummaryResponse {
  total_feedback: number;
  positive_count: number;
  negative_count: number;
  satisfaction_rate: number;
  top_issues: Array<{ reason: string; count: number }>;
  improvement_areas: string[];
}

// ---------------- V9: Workflow Automation & Self-Service Portal ----------------

export interface RoutingRuleResponse {
  id: string;
  name: string;
  description: string;
  priority: number;
  enabled: boolean;
  conditions: Record<string, unknown>;
  actions: Record<string, unknown>;
  created_at: string;
  updated_at: string | null;
}

export interface RoutingRuleListResponse {
  items: RoutingRuleResponse[];
  total: number;
}

export interface CannedResponse {
  id: string;
  title: string;
  content: string;
  category: string | null;
  shortcut: string | null;
  enabled: boolean;
  usage_count: number;
  created_at: string;
}

export interface CannedResponseListResponse {
  items: CannedResponse[];
  total: number;
}

export interface PortalArticle {
  id: string;
  title: string;
  slug: string;
  content: string;
  category: string | null;
  product_area: string | null;
  tags: string[];
  published: boolean;
  view_count: number;
  helpful_count: number;
  created_at: string;
  updated_at: string | null;
}

export interface PortalArticleListResponse {
  items: PortalArticle[];
  total: number;
}

export interface PortalSearchResult {
  id: string;
  title: string;
  slug: string;
  content: string;
  category: string | null;
  tags: string[];
  view_count: number;
}

export interface PortalSearchResponse {
  items: PortalSearchResult[];
  total: number;
}
