from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_current_workspace
from app.core.database import get_db
from app.models.models import User, Workspace
from app.schemas.sla import SlaRisk, SlaRisksResponse
from app.services.sla import detect_sla_risks

router = APIRouter()


@router.get("/risks", response_model=SlaRisksResponse)
def sla_risks(
    workspace: Workspace = Depends(get_current_workspace),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SlaRisksResponse:
    risks = detect_sla_risks(db, workspace_id=workspace.id)
    return SlaRisksResponse(
        items=[SlaRisk(**r) for r in risks],
        breached_count=sum(1 for r in risks if r["breached"]),
        high_risk_count=sum(1 for r in risks if r["risk_level"] == "high"),
    )
