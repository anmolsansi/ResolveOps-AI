import json

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import KbArticle
from app.schemas.kb import KbArticleResponse, KbGenerateResponse, KbListResponse
from app.services.kb import generate_kb

router = APIRouter()


def _to_response(a: KbArticle) -> KbArticleResponse:
    return KbArticleResponse(
        id=a.id,
        title=a.title,
        product_area=a.product_area,
        issue_type=a.issue_type,
        summary=a.summary,
        resolution_steps=a.resolution_steps,
        source_ticket_ids=json.loads(a.source_ticket_ids_json) if a.source_ticket_ids_json else [],
        ticket_count=a.ticket_count,
        created_at=a.created_at,
    )


@router.post("/generate", response_model=KbGenerateResponse)
def generate(db: Session = Depends(get_db)) -> KbGenerateResponse:
    articles = generate_kb(db)
    items = [_to_response(a) for a in articles]
    return KbGenerateResponse(generated=len(items), items=items)


@router.get("/articles", response_model=KbListResponse)
def list_articles(db: Session = Depends(get_db)) -> KbListResponse:
    rows = db.query(KbArticle).order_by(KbArticle.product_area, KbArticle.issue_type).all()
    return KbListResponse(items=[_to_response(a) for a in rows])
