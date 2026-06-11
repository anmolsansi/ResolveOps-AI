from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


# ---- Audit ----
class AuditLogResponse(BaseModel):
    id: UUID
    actor_email: str
    action: str
    resource_type: str
    resource_id: str | None
    workspace_id: UUID | None
    detail: str | None
    ip_address: str | None
    created_at: datetime


class AuditListResponse(BaseModel):
    total: int
    logs: list[AuditLogResponse]


# ---- Settings ----
class SettingsResponse(BaseModel):
    llm_provider: str
    embedding_provider: str
    llm_model: str
    embedding_model: str
    low_confidence_threshold: float
    default_top_k: int
    vector_backend: str
    pii_redaction_enabled: bool
    retention_rag_query_days: int
    retention_audit_log_days: int
    active_prompt_id: str | None


class SettingsUpdate(BaseModel):
    llm_provider: str | None = None
    embedding_provider: str | None = None
    llm_model: str | None = None
    embedding_model: str | None = None
    low_confidence_threshold: float | None = None
    default_top_k: int | None = None
    vector_backend: str | None = None
    pii_redaction_enabled: bool | None = None
    retention_rag_query_days: int | None = None
    retention_audit_log_days: int | None = None
    active_prompt_id: str | None = None


# ---- Retention ----
class RetentionPreviewResponse(BaseModel):
    retention_rag_query_days: int
    retention_audit_log_days: int
    rag_queries_to_purge: int
    audit_logs_to_purge: int


class RetentionRunResponse(BaseModel):
    rag_queries_deleted: int
    audit_logs_deleted: int


# ---- PII ----
class PiiScanRequest(BaseModel):
    text: str


class PiiMatch(BaseModel):
    type: str
    value: str
    start: int
    end: int


class PiiScanResponse(BaseModel):
    matches: list[PiiMatch]
    counts: dict[str, int]
    redacted_text: str
