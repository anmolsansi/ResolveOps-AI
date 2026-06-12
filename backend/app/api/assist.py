from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_current_workspace
from app.core.database import get_db
from app.models.models import User, Workspace
from app.schemas.assist import AssistRequest, AssistResponse
from app.services.assist import build_assist

router = APIRouter()


@router.post("/draft", response_model=AssistResponse)
def assist_draft(
    req: AssistRequest,
    workspace: Workspace = Depends(get_current_workspace),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AssistResponse:
    result = build_assist(
        db,
        subject=req.subject,
        body=req.body,
        customer_tier=req.customer_tier,
        product_area=req.product_area,
        top_k=req.top_k,
        workspace_id=workspace.id,
    )
    return AssistResponse(**result)
