"""Configurable data retention: purge rows older than a per-resource window."""
from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models.models import AuditLog, RagQuery
from app.services.settings_store import get_int_setting


def _cutoff(days: int) -> datetime | None:
    if days <= 0:
        return None
    return datetime.utcnow() - timedelta(days=days)


def preview_retention(db: Session) -> dict:
    rag_days = get_int_setting(db, "retention_rag_query_days")
    audit_days = get_int_setting(db, "retention_audit_log_days")

    rag_cutoff = _cutoff(rag_days)
    audit_cutoff = _cutoff(audit_days)

    rag_count = (
        db.query(RagQuery).filter(RagQuery.created_at < rag_cutoff).count()
        if rag_cutoff
        else 0
    )
    audit_count = (
        db.query(AuditLog).filter(AuditLog.created_at < audit_cutoff).count()
        if audit_cutoff
        else 0
    )
    return {
        "retention_rag_query_days": rag_days,
        "retention_audit_log_days": audit_days,
        "rag_queries_to_purge": rag_count,
        "audit_logs_to_purge": audit_count,
    }


def run_retention(db: Session) -> dict:
    rag_days = get_int_setting(db, "retention_rag_query_days")
    audit_days = get_int_setting(db, "retention_audit_log_days")

    rag_cutoff = _cutoff(rag_days)
    audit_cutoff = _cutoff(audit_days)

    rag_deleted = 0
    audit_deleted = 0
    if rag_cutoff:
        rag_deleted = (
            db.query(RagQuery)
            .filter(RagQuery.created_at < rag_cutoff)
            .delete(synchronize_session=False)
        )
    if audit_cutoff:
        audit_deleted = (
            db.query(AuditLog)
            .filter(AuditLog.created_at < audit_cutoff)
            .delete(synchronize_session=False)
        )
    db.commit()
    return {"rag_queries_deleted": rag_deleted, "audit_logs_deleted": audit_deleted}
