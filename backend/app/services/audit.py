"""Audit logging: a thin helper to record governance-relevant actions."""
from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.models.models import AuditLog


def record_audit(
    db: Session,
    *,
    actor_email: str = "system",
    action: str,
    resource_type: str = "",
    resource_id: str | None = None,
    workspace_id: uuid.UUID | None = None,
    detail: str | None = None,
    ip_address: str | None = None,
    commit: bool = True,
) -> AuditLog:
    entry = AuditLog(
        actor_email=actor_email,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        workspace_id=workspace_id,
        detail=detail,
        ip_address=ip_address,
    )
    db.add(entry)
    if commit:
        db.commit()
        db.refresh(entry)
    return entry
