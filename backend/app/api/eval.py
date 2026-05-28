import json
import time

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.models import EvalRun, RagQuery
from app.schemas.eval import EvalQuestion, EvalRunRequest, EvalRunResponse
from app.services.providers.factory import get_answer_provider, get_embedding_provider
from app.services.retrieval import compute_confidence, retrieve_chunks

router = APIRouter()

DEFAULT_EVAL_QUESTIONS = [
    EvalQuestion(question="How do I fix a billing error?"),
    EvalQuestion(question="What should I do if login fails?"),
    EvalQuestion(question="How to resolve integration sync issues?"),
    EvalQuestion(question="Dashboard is loading slowly, what can I do?"),
    EvalQuestion(question="Notifications are not being sent, what is the fix?"),
]


@router.post("/run", response_model=EvalRunResponse)
def run_eval(req: EvalRunRequest, db: Session = Depends(get_db)) -> EvalRunResponse:
    questions = req.questions or DEFAULT_EVAL_QUESTIONS
    name = req.name or "eval-run"

    results = []
    passed = 0
    failed = 0
    total_conf = 0.0
    total_lat = 0

    embedding_provider = get_embedding_provider()
    answer_provider = get_answer_provider()

    for eq in questions:
        start = time.time()
        filters_dict = eq.filters or {}
        chunks = retrieve_chunks(db, eq.question, filters=filters_dict, top_k=5)

        scores = [c["score"] for c in chunks]
        confidence = compute_confidence(scores)
        elapsed_ms = int((time.time() - start) * 1000)

        if confidence >= settings.low_confidence_threshold and chunks:
            contexts = [{"ticket_id": c["ticket_id"], "text": c["text"]} for c in chunks]
            answer = answer_provider.generate_answer(eq.question, contexts)
            cited_ids = list(dict.fromkeys(c["ticket_id"] for c in chunks))
            has_citation = len(cited_ids) > 0
        else:
            answer = (
                "I don't have enough context to answer this question. "
                "Please upload more support tickets or try a different query."
            )
            cited_ids = []
            has_citation = False

        is_pass = has_citation and confidence >= settings.low_confidence_threshold
        if is_pass:
            passed += 1
        else:
            failed += 1

        total_conf += confidence
        total_lat += elapsed_ms

        total_tokens = sum(len(c.get("text", "").split()) for c in chunks) * 4 // 3
        cost = embedding_provider.estimated_cost(total_tokens) + answer_provider.estimated_cost(
            total_tokens
        )

        rag_row = RagQuery(
            question=eq.question,
            filters_json=json.dumps(filters_dict) if filters_dict else None,
            answer=answer,
            cited_ticket_ids_json=json.dumps(cited_ids),
            retrieved_chunk_ids_json=json.dumps([str(c["chunk_id"]) for c in chunks]),
            confidence=confidence,
            latency_ms=elapsed_ms,
            estimated_cost_usd=round(cost, 6),
        )
        db.add(rag_row)

        results.append(
            {
                "question": eq.question,
                "passed": is_pass,
                "confidence": confidence,
                "latency_ms": elapsed_ms,
                "citations": cited_ids,
                "answer_preview": answer[:200],
            }
        )

    total_q = len(questions)
    avg_conf = total_conf / total_q if total_q > 0 else 0.0
    avg_lat = total_lat / total_q if total_q > 0 else 0.0

    eval_run = EvalRun(
        name=name,
        total_questions=total_q,
        passed_count=passed,
        failed_count=failed,
        average_confidence=round(avg_conf, 4),
        average_latency_ms=round(avg_lat, 2),
        results_json=json.dumps(results),
    )
    db.add(eval_run)
    db.commit()
    db.refresh(eval_run)

    return EvalRunResponse(
        id=eval_run.id,
        name=eval_run.name,
        total_questions=eval_run.total_questions,
        passed_count=eval_run.passed_count,
        failed_count=eval_run.failed_count,
        average_confidence=eval_run.average_confidence,
        average_latency_ms=eval_run.average_latency_ms,
        results_json=eval_run.results_json,
        created_at=eval_run.created_at,
    )


@router.get("/runs", response_model=list[EvalRunResponse])
def list_eval_runs(db: Session = Depends(get_db)) -> list[EvalRunResponse]:
    runs = db.query(EvalRun).order_by(EvalRun.created_at.desc()).limit(50).all()
    return [
        EvalRunResponse(
            id=r.id,
            name=r.name,
            total_questions=r.total_questions,
            passed_count=r.passed_count,
            failed_count=r.failed_count,
            average_confidence=r.average_confidence,
            average_latency_ms=r.average_latency_ms,
            results_json=r.results_json,
            created_at=r.created_at,
        )
        for r in runs
    ]
