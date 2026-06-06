from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class BatchSummary(BaseModel):
    id: UUID
    filename: str
    total_count: int
    valid_count: int
    invalid_count: int
    duplicate_count: int
    embedding_failure_count: int
    started_at: datetime
    completed_at: datetime | None


class QualityResponse(BaseModel):
    total_batches: int
    total_rows_seen: int
    total_valid_rows: int
    total_invalid_rows: int
    total_duplicate_rows: int
    total_embedding_failures: int
    valid_rate: float
    invalid_rate: float
    duplicate_rate: float
    embedding_failure_rate: float
    recent_batches: list[BatchSummary]


class RecentQuery(BaseModel):
    id: UUID
    question: str
    confidence: float
    latency_ms: int
    estimated_cost_usd: float
    created_at: datetime


class RetrievalResponse(BaseModel):
    total_queries: int
    average_confidence: float
    low_confidence_query_count: int
    average_latency_ms: float
    latency_p50_ms: float
    latency_p95_ms: float
    latency_p99_ms: float
    total_estimated_cost_usd: float
    citation_rate: float
    average_hallucination_risk: float
    average_citation_coverage: float
    average_retrieval_precision: float
    average_answer_completeness: float
    recent_queries: list[RecentQuery]


class CostByModel(BaseModel):
    provider: str
    model: str
    query_count: int
    total_cost_usd: float


class CostResponse(BaseModel):
    total_estimated_cost_usd: float
    total_queries: int
    by_model: list[CostByModel]


class ProductAreaQuality(BaseModel):
    product_area: str
    query_count: int
    average_confidence: float
    average_hallucination_risk: float
    average_citation_coverage: float
    average_retrieval_precision: float
    average_answer_completeness: float
    citation_rate: float


class QualityByAreaResponse(BaseModel):
    areas: list[ProductAreaQuality]


class FailedQuery(BaseModel):
    id: UUID
    question: str
    confidence: float
    reason: str
    feedback: str | None
    product_area: str | None
    created_at: datetime


class FailedQueriesResponse(BaseModel):
    count: int
    items: list[FailedQuery]


class IngestionChartPoint(BaseModel):
    batch_label: str
    valid: int
    invalid: int
    duplicate: int


class QueryChartPoint(BaseModel):
    timestamp: str
    confidence: float
    latency_ms: int
    has_citations: bool


class ChartsResponse(BaseModel):
    ingestion: list[IngestionChartPoint]
    queries: list[QueryChartPoint]
