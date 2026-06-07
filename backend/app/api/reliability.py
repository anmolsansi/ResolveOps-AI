import json
from collections import defaultdict
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.models.models import EvalRun, RagQuery, SavedEvalQuestion
from app.core.database import get_db

router = APIRouter()


class FailedQueryReviewRequest(BaseModel):
    action: str = Field(pattern="^(reviewed|ignored)$")
    note: str | None = None


class FailedQueryActionResponse(BaseModel):
    query_id: UUID
    action: str
    feedback: str | None
    eval_question_id: UUID | None = None


class FeedbackByArea(BaseModel):
    product_area: str
    total_feedback: int
    helpful: int
    not_helpful: int
    wrong_citation: int
    negative_rate: float


class FeedbackAnalyticsResponse(BaseModel):
    total_feedback: int
    helpful_count: int
    not_helpful_count: int
    wrong_citation_count: int
    reviewed_count: int
    ignored_count: int
    helpful_rate: float
    negative_feedback_rate: float
    by_product_area: list[FeedbackByArea]


class StoredComparisonSummary(BaseModel):
    id: UUID
    name: str
    total_questions: int
    passed_delta: int
    confidence_delta: float
    latency_delta_ms: float
    hallucination_risk_delta: float
    results: dict
    created_at: str


def _safe_rate(num: int, denom: int) -> float:
    return round(num / denom, 4) if denom > 0 else 0.0


@router.post("/failed-queries/{query_id}/review", response_model=FailedQueryActionResponse)
def review_failed_query(
    query_id: UUID,
    req: FailedQueryReviewRequest,
    db: Session = Depends(get_db),
) -> FailedQueryActionResponse:
    row = db.query(RagQuery).filter(RagQuery.id == query_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Query not found")
    row.feedback = req.action
    db.commit()
    return FailedQueryActionResponse(
        query_id=query_id,
        action=req.action,
        feedback=row.feedback,
        eval_question_id=None,
    )


@router.post("/failed-queries/{query_id}/add-to-eval", response_model=FailedQueryActionResponse)
def add_failed_query_to_eval(
    query_id: UUID,
    db: Session = Depends(get_db),
) -> FailedQueryActionResponse:
    row = db.query(RagQuery).filter(RagQuery.id == query_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Query not found")
    saved = SavedEvalQuestion(question=row.question, filters_json=row.filters_json)
    row.feedback = "reviewed"
    db.add(saved)
    db.commit()
    db.refresh(saved)
    return FailedQueryActionResponse(
        query_id=query_id,
        action="added_to_eval",
        feedback=row.feedback,
        eval_question_id=saved.id,
    )


@router.get("/feedback", response_model=FeedbackAnalyticsResponse)
def feedback_analytics(db: Session = Depends(get_db)) -> FeedbackAnalyticsResponse:
    rows = db.query(RagQuery).filter(RagQuery.feedback.isnot(None)).all()
    total = len(rows)
    helpful = sum(1 for row in rows if row.feedback == "helpful")
    not_helpful = sum(1 for row in rows if row.feedback == "not_helpful")
    wrong_citation = sum(1 for row in rows if row.feedback == "wrong_citation")
    reviewed = sum(1 for row in rows if row.feedback == "reviewed")
    ignored = sum(1 for row in rows if row.feedback == "ignored")
    negative = not_helpful + wrong_citation

    grouped: dict[str, list[RagQuery]] = defaultdict(list)
    for row in rows:
        grouped[row.product_area or "unknown"].append(row)

    by_area = []
    for area, items in grouped.items():
        area_helpful = sum(1 for row in items if row.feedback == "helpful")
        area_not_helpful = sum(1 for row in items if row.feedback == "not_helpful")
        area_wrong = sum(1 for row in items if row.feedback == "wrong_citation")
        by_area.append(
            FeedbackByArea(
                product_area=area,
                total_feedback=len(items),
                helpful=area_helpful,
                not_helpful=area_not_helpful,
                wrong_citation=area_wrong,
                negative_rate=_safe_rate(area_not_helpful + area_wrong, len(items)),
            )
        )

    by_area.sort(key=lambda item: item.total_feedback, reverse=True)
    return FeedbackAnalyticsResponse(
        total_feedback=total,
        helpful_count=helpful,
        not_helpful_count=not_helpful,
        wrong_citation_count=wrong_citation,
        reviewed_count=reviewed,
        ignored_count=ignored,
        helpful_rate=_safe_rate(helpful, total),
        negative_feedback_rate=_safe_rate(negative, total),
        by_product_area=by_area,
    )


@router.get("/comparisons", response_model=list[StoredComparisonSummary])
def list_stored_comparisons(db: Session = Depends(get_db)) -> list[StoredComparisonSummary]:
    rows = (
        db.query(EvalRun)
        .filter(EvalRun.name.startswith("compare:"))
        .order_by(EvalRun.created_at.desc())
        .limit(25)
        .all()
    )
    items = []
    for row in rows:
        data = json.loads(row.results_json or "{}")
        items.append(
            StoredComparisonSummary(
                id=row.id,
                name=row.name,
                total_questions=row.total_questions,
                passed_delta=int(data.get("passed_delta", 0)),
                confidence_delta=float(data.get("confidence_delta", 0.0)),
                latency_delta_ms=float(data.get("latency_delta_ms", 0.0)),
                hallucination_risk_delta=float(data.get("hallucination_risk_delta", 0.0)),
                results=data,
                created_at=row.created_at.isoformat() if row.created_at else "",
            )
        )
    return items
