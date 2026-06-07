from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.sla import SlaRisk, SlaRisksResponse
from app.services.sla import detect_sla_risks

router = APIRouter()


@router.get("/risks", response_model=SlaRisksResponse)
def sla_risks(db: Session = Depends(get_db)) -> SlaRisksResponse:
    risks = detect_sla_risks(db)
    return SlaRisksResponse(
        items=[SlaRisk(**r) for r in risks],
        breached_count=sum(1 for r in risks if r["breached"]),
        high_risk_count=sum(1 for r in risks if r["risk_level"] == "high"),
    )
