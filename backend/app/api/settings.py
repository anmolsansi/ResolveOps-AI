from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_admin
from app.core.database import get_db
from app.models.models import User
from app.schemas.governance import SettingsResponse, SettingsUpdate
from app.services.audit import record_audit
from app.services.settings_store import apply_updates, get_all_settings
from app.services.vector import backend_status

router = APIRouter()


def _to_response(values: dict) -> SettingsResponse:
    active_prompt = str(values.get("active_prompt_id") or "") or None
    return SettingsResponse(
        llm_provider=str(values["llm_provider"]),
        embedding_provider=str(values["embedding_provider"]),
        llm_model=str(values["llm_model"]),
        embedding_model=str(values["embedding_model"]),
        low_confidence_threshold=float(values["low_confidence_threshold"]),
        default_top_k=int(values["default_top_k"]),
        vector_backend=str(values["vector_backend"]),
        pii_redaction_enabled=bool(values["pii_redaction_enabled"]),
        retention_rag_query_days=int(values["retention_rag_query_days"]),
        retention_audit_log_days=int(values["retention_audit_log_days"]),
        active_prompt_id=active_prompt,
    )


@router.get("", response_model=SettingsResponse)
def get_settings(
    _: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> SettingsResponse:
    return _to_response(get_all_settings(db))


@router.put("", response_model=SettingsResponse)
def update_settings(
    payload: SettingsUpdate,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> SettingsResponse:
    changed = apply_updates(db, payload.model_dump(exclude_none=True))
    if changed:
        record_audit(
            db,
            actor_email=admin.email,
            action="settings.update",
            resource_type="settings",
            detail=", ".join(sorted(changed)),
        )
    return _to_response(get_all_settings(db))


@router.get("/vector-backend")
def vector_backend(
    _: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> dict:
    return backend_status(db)
