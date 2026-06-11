from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.core.database import get_db
from app.models.models import AuditLog, User
from app.schemas.governance import AuditListResponse, AuditLogResponse

router = APIRouter()


@router.get("", response_model=AuditListResponse)
def list_audit_logs(
    action: str | None = Query(default=None),
    actor_email: str | None = Query(default=None),
    limit: int = Query(default=100, le=500),
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> AuditListResponse:
    query = db.query(AuditLog)
    if action:
        query = query.filter(AuditLog.action == action)
    if actor_email:
        query = query.filter(AuditLog.actor_email == actor_email.strip().lower())
    total = query.count()
    rows = query.order_by(AuditLog.created_at.desc()).limit(limit).all()
    return AuditListResponse(
        total=total,
        logs=[
            AuditLogResponse(
                id=r.id,
                actor_email=r.actor_email,
                action=r.action,
                resource_type=r.resource_type,
                resource_id=r.resource_id,
                workspace_id=r.workspace_id,
                detail=r.detail,
                ip_address=r.ip_address,
                created_at=r.created_at,
            )
            for r in rows
        ],
    )
