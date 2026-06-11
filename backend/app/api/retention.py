from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.core.database import get_db
from app.models.models import User
from app.schemas.governance import RetentionPreviewResponse, RetentionRunResponse
from app.services.audit import record_audit
from app.services.retention import preview_retention, run_retention

router = APIRouter()


@router.get("", response_model=RetentionPreviewResponse)
def retention_preview(
    _: User = Depends(require_admin), db: Session = Depends(get_db)
) -> RetentionPreviewResponse:
    return RetentionPreviewResponse(**preview_retention(db))


@router.post("/run", response_model=RetentionRunResponse)
def retention_run(
    admin: User = Depends(require_admin), db: Session = Depends(get_db)
) -> RetentionRunResponse:
    result = run_retention(db)
    record_audit(
        db,
        actor_email=admin.email,
        action="retention.run",
        resource_type="retention",
        detail=(
            f"rag_deleted={result['rag_queries_deleted']}, "
            f"audit_deleted={result['audit_logs_deleted']}"
        ),
    )
    return RetentionRunResponse(**result)
