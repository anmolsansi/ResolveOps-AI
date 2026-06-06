import csv
import io
import json
import time
import uuid as _uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.models import EvalRun, RagQuery, SavedEvalQuestion
from app.schemas.eval import (
    ConfigResult,
    EvalCompareRequest,
    EvalCompareResponse,
    EvalConfig,
    EvalQuestion,
    EvalRunRequest,
    EvalRunResponse,
    QuestionDelta,
    SavedEvalQuestionCreate,
    SavedEvalQuestionResponse,
    SavedEvalQuestionUpdate,
)
from app.services.providers.base import AnswerProvider, EmbeddingProvider
from app.services.providers.factory import get_answer_provider, get_embedding_provider
from app.services.quality import compute_quality_metrics
from app.services.retrieval import compute_confidence, retrieve_chunks

router = APIRouter()

FALLBACK_ANSWER = (
    "I don't have enough context to answer this question. "
    "Please upload more support tickets or try a different query."
)

DEFAULT_EVAL_QUESTIONS = [
    EvalQuestion(question="How do I fix a billing error?"),
    EvalQuestion(question="What should I do if login fails?"),
    EvalQuestion(question="How to resolve integration sync issues?"),
    EvalQuestion(question="Dashboard is loading slowly, what can I do?"),
    EvalQuestion(question="Notifications are not being sent, what is the fix?"),
]


def _evaluate_question(
    db: Session,
    eq: EvalQuestion,
    top_k: int,
    threshold: float,
    embedding_provider: EmbeddingProvider,
    answer_provider: AnswerProvider,
    persist: bool,
) -> dict:
    start = time.time()
    filters_dict: dict[str, str | None] = dict(eq.filters or {})
    chunks = retrieve_chunks(db, eq.question, filters=filters_dict, top_k=top_k)

    scores = [c["score"] for c in chunks]
    confidence = compute_confidence(scores)

    is_fallback = not (confidence >= threshold and chunks)
    if not is_fallback:
        contexts = [{"ticket_id": c["ticket_id"], "text": c["text"]} for c in chunks]
        answer = answer_provider.generate_answer(eq.question, contexts)
        cited_ids = list(dict.fromkeys(c["ticket_id"] for c in chunks))
    else:
        answer = FALLBACK_ANSWER
        cited_ids = []

    quality = compute_quality_metrics(eq.question, answer, chunks, cited_ids, is_fallback)
    elapsed_ms = int((time.time() - start) * 1000)
    is_pass = len(cited_ids) > 0 and confidence >= threshold

    total_tokens = sum(len(c.get("text", "").split()) for c in chunks) * 4 // 3
    cost = embedding_provider.estimated_cost(total_tokens) + answer_provider.estimated_cost(
        total_tokens
    )

    if persist:
        db.add(
            RagQuery(
                question=eq.question,
                filters_json=json.dumps(filters_dict) if filters_dict else None,
                answer=answer,
                cited_ticket_ids_json=json.dumps(cited_ids),
                retrieved_chunk_ids_json=json.dumps([str(c["chunk_id"]) for c in chunks]),
                confidence=confidence,
                latency_ms=elapsed_ms,
                estimated_cost_usd=round(cost, 6),
                hallucination_risk=quality["hallucination_risk"],
                citation_coverage=quality["citation_coverage"],
                retrieval_precision=quality["retrieval_precision"],
                answer_completeness=quality["answer_completeness"],
                product_area=chunks[0]["product_area"] if chunks else None,
                provider=answer_provider.name,
                model=answer_provider.model,
                is_fallback=is_fallback,
            )
        )

    return {
        "question": eq.question,
        "passed": is_pass,
        "confidence": confidence,
        "latency_ms": elapsed_ms,
        "citations": cited_ids,
        "hallucination_risk": quality["hallucination_risk"],
        "answer_preview": answer[:200],
    }


@router.post("/run", response_model=EvalRunResponse)
def run_eval(req: EvalRunRequest, db: Session = Depends(get_db)) -> EvalRunResponse:
    questions = req.questions or DEFAULT_EVAL_QUESTIONS
    name = req.name or "eval-run"

    embedding_provider = get_embedding_provider()
    answer_provider = get_answer_provider()

    results = [
        _evaluate_question(
            db,
            eq,
            top_k=settings.default_top_k,
            threshold=settings.low_confidence_threshold,
            embedding_provider=embedding_provider,
            answer_provider=answer_provider,
            persist=True,
        )
        for eq in questions
    ]

    passed = sum(1 for r in results if r["passed"])
    failed = len(results) - passed
    total_conf = sum(r["confidence"] for r in results)
    total_lat = sum(r["latency_ms"] for r in results)

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


def _run_config(
    db: Session,
    questions: list[EvalQuestion],
    config: EvalConfig,
    embedding_provider: EmbeddingProvider,
    answer_provider: AnswerProvider,
) -> tuple[ConfigResult, list[dict]]:
    results = [
        _evaluate_question(
            db,
            eq,
            top_k=config.top_k,
            threshold=config.threshold,
            embedding_provider=embedding_provider,
            answer_provider=answer_provider,
            persist=False,
        )
        for eq in questions
    ]
    n = len(results) or 1
    passed = sum(1 for r in results if r["passed"])
    summary = ConfigResult(
        label=config.label,
        top_k=config.top_k,
        threshold=config.threshold,
        passed_count=passed,
        failed_count=len(results) - passed,
        average_confidence=round(sum(r["confidence"] for r in results) / n, 4),
        average_latency_ms=round(sum(r["latency_ms"] for r in results) / n, 2),
        average_hallucination_risk=round(
            sum(r["hallucination_risk"] for r in results) / n, 4
        ),
    )
    return summary, results


@router.post("/compare", response_model=EvalCompareResponse)
def compare_eval(req: EvalCompareRequest, db: Session = Depends(get_db)) -> EvalCompareResponse:
    questions = req.questions or DEFAULT_EVAL_QUESTIONS
    embedding_provider = get_embedding_provider()
    answer_provider = get_answer_provider()

    summary_a, results_a = _run_config(db, questions, req.config_a, embedding_provider,
                                       answer_provider)
    summary_b, results_b = _run_config(db, questions, req.config_b, embedding_provider,
                                       answer_provider)

    per_question = [
        QuestionDelta(
            question=ra["question"],
            confidence_a=ra["confidence"],
            confidence_b=rb["confidence"],
            confidence_delta=round(rb["confidence"] - ra["confidence"], 4),
            passed_a=ra["passed"],
            passed_b=rb["passed"],
        )
        for ra, rb in zip(results_a, results_b)
    ]

    return EvalCompareResponse(
        name=req.name or "regression-compare",
        total_questions=len(questions),
        config_a=summary_a,
        config_b=summary_b,
        passed_delta=summary_b.passed_count - summary_a.passed_count,
        confidence_delta=round(
            summary_b.average_confidence - summary_a.average_confidence, 4
        ),
        latency_delta_ms=round(
            summary_b.average_latency_ms - summary_a.average_latency_ms, 2
        ),
        hallucination_risk_delta=round(
            summary_b.average_hallucination_risk - summary_a.average_hallucination_risk, 4
        ),
        per_question=per_question,
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


@router.get("/runs/{run_id}/export")
def export_eval_run(
    run_id: _uuid.UUID,
    format: str = Query("json", pattern="^(json|csv)$"),
    db: Session = Depends(get_db),
) -> Response:
    run = db.query(EvalRun).filter(EvalRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Eval run not found")

    results = json.loads(run.results_json) if run.results_json else []

    if format == "csv":
        output = io.StringIO()
        fields = [
            "question", "passed", "confidence",
            "latency_ms", "citations", "answer_preview",
        ]
        writer = csv.DictWriter(output, fieldnames=fields)
        writer.writeheader()
        for r in results:
            row = dict(r)
            row["citations"] = "; ".join(row.get("citations", []))
            writer.writerow(row)
        return Response(
            content=output.getvalue(),
            media_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="eval-{run_id}.csv"'},
        )

    return Response(
        content=json.dumps(
            {
                "id": str(run.id),
                "name": run.name,
                "total_questions": run.total_questions,
                "passed_count": run.passed_count,
                "failed_count": run.failed_count,
                "average_confidence": run.average_confidence,
                "average_latency_ms": run.average_latency_ms,
                "results": results,
                "created_at": run.created_at.isoformat() if run.created_at else None,
            },
            indent=2,
        ),
        media_type="application/json",
        headers={"Content-Disposition": f'attachment; filename="eval-{run_id}.json"'},
    )


# --- Eval Question CRUD ---


@router.get("/questions", response_model=list[SavedEvalQuestionResponse])
def list_eval_questions(db: Session = Depends(get_db)) -> list[SavedEvalQuestionResponse]:
    questions = (
        db.query(SavedEvalQuestion)
        .order_by(SavedEvalQuestion.created_at.desc())
        .all()
    )
    return [
        SavedEvalQuestionResponse(
            id=q.id,
            question=q.question,
            filters_json=q.filters_json,
            created_at=q.created_at,
        )
        for q in questions
    ]


@router.post("/questions", response_model=SavedEvalQuestionResponse, status_code=201)
def create_eval_question(
    req: SavedEvalQuestionCreate, db: Session = Depends(get_db)
) -> SavedEvalQuestionResponse:
    q = SavedEvalQuestion(
        question=req.question,
        filters_json=json.dumps(req.filters) if req.filters else None,
    )
    db.add(q)
    db.commit()
    db.refresh(q)
    return SavedEvalQuestionResponse(
        id=q.id,
        question=q.question,
        filters_json=q.filters_json,
        created_at=q.created_at,
    )


@router.put("/questions/{question_id}", response_model=SavedEvalQuestionResponse)
def update_eval_question(
    question_id: _uuid.UUID,
    req: SavedEvalQuestionUpdate,
    db: Session = Depends(get_db),
) -> SavedEvalQuestionResponse:
    q = db.query(SavedEvalQuestion).filter(SavedEvalQuestion.id == question_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")
    if req.question is not None:
        q.question = req.question
    if req.filters is not None:
        q.filters_json = json.dumps(req.filters) if req.filters else None
    db.commit()
    db.refresh(q)
    return SavedEvalQuestionResponse(
        id=q.id,
        question=q.question,
        filters_json=q.filters_json,
        created_at=q.created_at,
    )


@router.delete("/questions/{question_id}", status_code=204)
def delete_eval_question(
    question_id: _uuid.UUID, db: Session = Depends(get_db)
) -> None:
    q = db.query(SavedEvalQuestion).filter(SavedEvalQuestion.id == question_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")
    db.delete(q)
    db.commit()
