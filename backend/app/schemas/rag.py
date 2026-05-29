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


class RagQueryResponse(BaseModel):
    answer: str
    citations: list[str]
    confidence: float
    retrieved_chunks: list[RetrievedChunk]
    latency_ms: int
    estimated_cost_usd: float
