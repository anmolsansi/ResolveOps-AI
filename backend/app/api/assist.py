from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.assist import AssistRequest, AssistResponse
from app.services.assist import build_assist

router = APIRouter()


@router.post("/draft", response_model=AssistResponse)
def assist_draft(req: AssistRequest, db: Session = Depends(get_db)) -> AssistResponse:
    result = build_assist(
        db,
        subject=req.subject,
        body=req.body,
        customer_tier=req.customer_tier,
        product_area=req.product_area,
        top_k=req.top_k,
    )
    return AssistResponse(**result)
