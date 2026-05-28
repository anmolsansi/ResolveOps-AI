export interface RowError {
  row: number;
  ticket_id: string | null;
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

export interface RetrievedChunk {
  chunk_id: string;
  ticket_id: string;
  score: number;
  preview: string;
}

export interface RagQueryResponse {
  answer: string;
  citations: string[];
  confidence: number;
  retrieved_chunks: RetrievedChunk[];
  latency_ms: number;
  estimated_cost_usd: number;
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
  total_estimated_cost_usd: number;
  citation_rate: number;
  recent_queries: RecentQuery[];
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
