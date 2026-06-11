import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_admin
from app.core.database import get_db
from app.models.models import PromptTemplate, User
from app.schemas.prompts import PromptCreate, PromptListResponse, PromptResponse
from app.services.audit import record_audit
from app.services.prompts import activate_prompt, create_prompt, get_active_prompt

router = APIRouter()


def _to_response(p: PromptTemplate) -> PromptResponse:
    return PromptResponse(
        id=p.id,
        name=p.name,
        version=p.version,
        content=p.content,
        is_active=p.is_active,
        created_at=p.created_at,
    )


@router.get("", response_model=PromptListResponse)
def list_prompts(
    _: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> PromptListResponse:
    prompts = (
        db.query(PromptTemplate)
        .order_by(PromptTemplate.name.asc(), PromptTemplate.version.desc())
        .all()
    )
    active = get_active_prompt(db)
    return PromptListResponse(
        prompts=[_to_response(p) for p in prompts],
        active_id=active.id if active else None,
    )


@router.post("", response_model=PromptResponse)
def create(
    payload: PromptCreate,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> PromptResponse:
    if not payload.name.strip() or not payload.content.strip():
        raise HTTPException(status_code=422, detail="name and content are required")
    prompt = create_prompt(db, payload.name.strip(), payload.content, activate=payload.activate)
    record_audit(
        db,
        actor_email=admin.email,
        action="prompt.create",
        resource_type="prompt",
        resource_id=str(prompt.id),
        detail=f"{prompt.name} v{prompt.version} active={prompt.is_active}",
    )
    return _to_response(prompt)


@router.post("/{prompt_id}/activate", response_model=PromptResponse)
def activate(
    prompt_id: str,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> PromptResponse:
    try:
        pid = uuid.UUID(prompt_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid id")
    prompt = db.get(PromptTemplate, pid)
    if prompt is None:
        raise HTTPException(status_code=404, detail="Prompt not found")
    prompt = activate_prompt(db, prompt)
    record_audit(
        db,
        actor_email=admin.email,
        action="prompt.activate",
        resource_type="prompt",
        resource_id=str(prompt.id),
        detail=f"{prompt.name} v{prompt.version}",
    )
    return _to_response(prompt)
