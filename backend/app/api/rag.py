import json
import time
import uuid as _uuid
from collections import Counter

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_current_workspace
from app.core.config import settings
from app.core.database import get_db
from app.models.models import RagQuery, User, Workspace
from app.schemas.rag import (
    ChunkDebugInfo,
    FeedbackRequest,
    FeedbackResponse,
    QualityScores,
    RagQueryRequest,
    RagQueryResponse,
    RetrievedChunk,
)
from app.services.prompts import get_active_prompt_text
from app.services.providers.factory import get_answer_provider, get_embedding_provider
from app.services.quality import compute_quality_metrics
from app.services.retrieval import compute_confidence, retrieve_chunks

router = APIRouter()


def _dominant_product_area(results: list[dict]) -> str | None:
    areas = [r.get("product_area") for r in results if r.get("product_area")]
    if not areas:
        return None
    return Counter(areas).most_common(1)[0][0]


@router.post("/query", response_model=RagQueryResponse)
def rag_query(
    req: RagQueryRequest,
    workspace: Workspace = Depends(get_current_workspace),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RagQueryResponse:
    start = time.time()

    filters_dict: dict[str, str | None] | None = None
    if req.filters:
        filters_dict = req.filters.model_dump(exclude_none=True)

    results = retrieve_chunks(
        db, req.question, filters=filters_dict, top_k=req.top_k,
        workspace_id=workspace.id,
    )

    scores = [r["score"] for r in results]
    confidence = compute_confidence(scores)

    answer_provider = get_answer_provider()
    embedding_provider = get_embedding_provider()

    is_fallback = confidence < settings.low_confidence_threshold or not results
    if is_fallback:
        answer = (
            "I don't have enough context to answer this question. "
            "Please upload more support tickets or try a different query."
        )
        citations: list[str] = []
    else:
        contexts = [
            {"ticket_id": r["ticket_id"], "text": r["text"]} for r in results
        ]
        answer = answer_provider.generate_answer(
            req.question, contexts, system_prompt=get_active_prompt_text(db)
        )
        citations = list(dict.fromkeys(r["ticket_id"] for r in results))

    quality = compute_quality_metrics(
        req.question, answer, results, citations, is_fallback
    )

    elapsed_ms = int((time.time() - start) * 1000)
    total_tokens = sum(len(r.get("text", "").split()) for r in results) * 4 // 3
    cost = embedding_provider.estimated_cost(total_tokens) + answer_provider.estimated_cost(
        total_tokens
    )

    rag_row = RagQuery(
        workspace_id=workspace.id,
        question=req.question,
        filters_json=json.dumps(filters_dict) if filters_dict else None,
        answer=answer,
        cited_ticket_ids_json=json.dumps(citations),
        retrieved_chunk_ids_json=json.dumps([str(r["chunk_id"]) for r in results]),
        confidence=confidence,
        latency_ms=elapsed_ms,
        estimated_cost_usd=round(cost, 6),
        hallucination_risk=quality["hallucination_risk"],
        citation_coverage=quality["citation_coverage"],
        retrieval_precision=quality["retrieval_precision"],
        answer_completeness=quality["answer_completeness"],
        product_area=_dominant_product_area(results),
        provider=answer_provider.name,
        model=answer_provider.model,
        is_fallback=is_fallback,
    )
    db.add(rag_row)
    db.commit()
    db.refresh(rag_row)

    retrieved = [
        RetrievedChunk(
            chunk_id=r["chunk_id"],
            ticket_id=r["ticket_id"],
            score=r["score"],
            preview=r["preview"],
            debug=ChunkDebugInfo(**r["debug"]) if r.get("debug") else None,
        )
        for r in results
    ]

    return RagQueryResponse(
        query_id=rag_row.id,
        answer=answer,
        citations=citations,
        confidence=confidence,
        retrieved_chunks=retrieved,
        latency_ms=elapsed_ms,
        estimated_cost_usd=round(cost, 6),
        provider=rag_row.provider,
        model=rag_row.model,
        product_area=rag_row.product_area,
        is_fallback=is_fallback,
        quality=QualityScores(**quality),
    )


@router.post("/queries/{query_id}/feedback", response_model=FeedbackResponse)
def submit_feedback(
    query_id: _uuid.UUID,
    req: FeedbackRequest,
    workspace: Workspace = Depends(get_current_workspace),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> FeedbackResponse:
    row = db.query(RagQuery).filter(
        RagQuery.id == query_id, RagQuery.workspace_id == workspace.id
    ).first()
    if not row:
        raise HTTPException(status_code=404, detail="Query not found")
    row.feedback = req.feedback.value
    db.commit()
    return FeedbackResponse(query_id=query_id, feedback=req.feedback)
