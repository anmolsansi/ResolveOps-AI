from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class RowError(BaseModel):
    row: int
    ticket_id: str | None = None
    reason: str


class InvalidRow(BaseModel):
    row: int
    data: dict[str, str]
    reason: str


class UploadResponse(BaseModel):
    batch_id: UUID
    filename: str
    total_count: int
    valid_count: int
    invalid_count: int
    duplicate_count: int
    embedding_failure_count: int
    errors: list[RowError]
    invalid_rows: list[InvalidRow]


class TicketSummary(BaseModel):
    id: str
    title: str
    product_area: str
    issue_type: str
    priority: str
    customer_tier: str
    status: str
    created_at: datetime
    resolved_at: datetime | None = None


class TicketListResponse(BaseModel):
    items: list[TicketSummary]
    total: int
    page: int
    page_size: int


class ChunkPreview(BaseModel):
    id: UUID
    chunk_index: int
    preview: str


class TicketDetail(BaseModel):
    id: str
    title: str
    body: str
    product_area: str
    issue_type: str
    priority: str
    customer_tier: str
    status: str
    resolution: str | None
    created_at: datetime
    resolved_at: datetime | None
    ingestion_batch_id: UUID | None
    validation_status: str
    validation_errors: str | None
    chunks: list[ChunkPreview]
