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
