from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel


class RagFilters(BaseModel):
    product_area: str | None = None
    issue_type: str | None = None
    priority: str | None = None
    customer_tier: str | None = None
    status: str | None = None


class RagQueryRequest(BaseModel):
    question: str
    filters: RagFilters | None = None
    top_k: int = 5


class ChunkDebugInfo(BaseModel):
    cosine_score: float
    keyword_boost: float
    keyword_hits: int
    matched_tokens: list[str]


class RetrievedChunk(BaseModel):
    chunk_id: UUID
    ticket_id: str
    score: float
    preview: str
    debug: ChunkDebugInfo | None = None


class QualityScores(BaseModel):
    hallucination_risk: float
    citation_coverage: float
    retrieval_precision: float
    answer_completeness: float


class RagQueryResponse(BaseModel):
    query_id: UUID
    answer: str
    citations: list[str]
    confidence: float
    retrieved_chunks: list[RetrievedChunk]
    latency_ms: int
    estimated_cost_usd: float
    provider: str
    model: str
    product_area: str | None = None
    is_fallback: bool
    quality: QualityScores


class FeedbackValue(StrEnum):
    helpful = "helpful"
    not_helpful = "not_helpful"
    wrong_citation = "wrong_citation"


class FeedbackRequest(BaseModel):
    feedback: FeedbackValue


class FeedbackResponse(BaseModel):
    query_id: UUID
    feedback: FeedbackValue
