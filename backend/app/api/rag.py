import json
import time

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.models import RagQuery
from app.schemas.rag import ChunkDebugInfo, RagQueryRequest, RagQueryResponse, RetrievedChunk
from app.services.providers.factory import get_answer_provider, get_embedding_provider
from app.services.retrieval import compute_confidence, retrieve_chunks

router = APIRouter()


@router.post("/query", response_model=RagQueryResponse)
def rag_query(req: RagQueryRequest, db: Session = Depends(get_db)) -> RagQueryResponse:
    start = time.time()

    filters_dict: dict[str, str | None] | None = None
    if req.filters:
        filters_dict = req.filters.model_dump(exclude_none=True)

    results = retrieve_chunks(db, req.question, filters=filters_dict, top_k=req.top_k)

    scores = [r["score"] for r in results]
    confidence = compute_confidence(scores)

    answer_provider = get_answer_provider()
    embedding_provider = get_embedding_provider()

    if confidence < settings.low_confidence_threshold or not results:
        answer = (
            "I don't have enough context to answer this question. "
            "Please upload more support tickets or try a different query."
        )
        citations: list[str] = []
    else:
        contexts = [
            {"ticket_id": r["ticket_id"], "text": r["text"]} for r in results
        ]
        answer = answer_provider.generate_answer(req.question, contexts)
        cited_ids = list(dict.fromkeys(r["ticket_id"] for r in results))
        citations = cited_ids

    elapsed_ms = int((time.time() - start) * 1000)
    total_tokens = sum(len(r.get("text", "").split()) for r in results) * 4 // 3
    cost = embedding_provider.estimated_cost(total_tokens) + answer_provider.estimated_cost(
        total_tokens
    )

    rag_row = RagQuery(
        question=req.question,
        filters_json=json.dumps(filters_dict) if filters_dict else None,
        answer=answer,
        cited_ticket_ids_json=json.dumps(citations),
        retrieved_chunk_ids_json=json.dumps([str(r["chunk_id"]) for r in results]),
        confidence=confidence,
        latency_ms=elapsed_ms,
        estimated_cost_usd=round(cost, 6),
    )
    db.add(rag_row)
    db.commit()

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
        answer=answer,
        citations=citations,
        confidence=confidence,
        retrieved_chunks=retrieved,
        latency_ms=elapsed_ms,
        estimated_cost_usd=round(cost, 6),
    )
