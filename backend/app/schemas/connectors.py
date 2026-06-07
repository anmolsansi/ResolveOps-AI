from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ConnectorCreate(BaseModel):
    provider: str
    name: str


class ConnectorSummary(BaseModel):
    id: UUID
    provider: str
    name: str
    cursor: str | None
    enabled: bool
    last_synced_at: datetime | None
    total_imported: int
    created_at: datetime


class ConnectorListResponse(BaseModel):
    items: list[ConnectorSummary]


class SyncResult(BaseModel):
    connector_id: UUID
    batch_id: UUID
    fetched: int
    imported: int
    duplicate_id: int
    duplicate_semantic: int
    embedding_failures: int
    cursor: str
    imported_ids: list[str]


class JobCreate(BaseModel):
    interval_minutes: int = 60


class JobSummary(BaseModel):
    id: UUID
    connector_id: UUID
    interval_minutes: int
    enabled: bool
    next_run_at: datetime
    last_run_at: datetime | None
    last_status: str | None
    last_imported: int
    created_at: datetime


class JobListResponse(BaseModel):
    items: list[JobSummary]


class RunDueResponse(BaseModel):
    ran: int
    results: list[SyncResult]


class DuplicateTicket(BaseModel):
    id: str
    title: str
    product_area: str


class DuplicateCluster(BaseModel):
    ticket_ids: list[str]
    size: int
    max_similarity: float
    tickets: list[DuplicateTicket]


class DuplicatesResponse(BaseModel):
    clusters: list[DuplicateCluster]
