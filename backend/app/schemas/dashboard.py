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
    total_estimated_cost_usd: float
    citation_rate: float
    recent_queries: list[RecentQuery]


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
