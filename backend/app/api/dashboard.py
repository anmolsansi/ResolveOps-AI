import json
from collections import defaultdict

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_current_workspace
from app.core.config import settings
from app.core.database import get_db
from app.models.models import IngestionBatch, RagQuery, User, Workspace
from app.schemas.dashboard import (
    BatchSummary,
    ChartsResponse,
    CostByModel,
    CostResponse,
    FailedQueriesResponse,
    FailedQuery,
    IngestionChartPoint,
    ProductAreaQuality,
    QualityByAreaResponse,
    QualityResponse,
    QueryChartPoint,
    RecentQuery,
    RetrievalResponse,
)
from app.services.quality import percentile

router = APIRouter()


def _has_citations(q: RagQuery) -> bool:
    if not q.cited_ticket_ids_json:
        return False
    try:
        return len(json.loads(q.cited_ticket_ids_json)) > 0
    except (json.JSONDecodeError, TypeError):
        return False


def _failure_reason(q: RagQuery) -> str | None:
    if q.feedback in ("not_helpful", "wrong_citation"):
        return f"feedback:{q.feedback}"
    if q.confidence < settings.low_confidence_threshold:
        return "low_confidence"
    if not _has_citations(q):
        return "no_citations"
    return None


@router.get("/quality", response_model=QualityResponse)
def quality_metrics(
    workspace: Workspace = Depends(get_current_workspace),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> QualityResponse:
    batches = db.query(IngestionBatch).filter(
        IngestionBatch.workspace_id == workspace.id
    ).order_by(IngestionBatch.started_at.desc()).all()

    total_batches = len(batches)
    total_rows = sum(b.total_count for b in batches)
    total_valid = sum(b.valid_count for b in batches)
    total_invalid = sum(b.invalid_count for b in batches)
    total_duplicate = sum(b.duplicate_count for b in batches)
    total_emb_fail = sum(b.embedding_failure_count for b in batches)

    def safe_rate(num: int, denom: int) -> float:
        return round(num / denom, 4) if denom > 0 else 0.0

    return QualityResponse(
        total_batches=total_batches,
        total_rows_seen=total_rows,
        total_valid_rows=total_valid,
        total_invalid_rows=total_invalid,
        total_duplicate_rows=total_duplicate,
        total_embedding_failures=total_emb_fail,
        valid_rate=safe_rate(total_valid, total_rows),
        invalid_rate=safe_rate(total_invalid, total_rows),
        duplicate_rate=safe_rate(total_duplicate, total_rows),
        embedding_failure_rate=safe_rate(total_emb_fail, total_rows),
        recent_batches=[
            BatchSummary(
                id=b.id,
                filename=b.filename,
                total_count=b.total_count,
                valid_count=b.valid_count,
                invalid_count=b.invalid_count,
                duplicate_count=b.duplicate_count,
                embedding_failure_count=b.embedding_failure_count,
                started_at=b.started_at,
                completed_at=b.completed_at,
            )
            for b in batches[:10]
        ],
    )


@router.get("/retrieval", response_model=RetrievalResponse)
def retrieval_metrics(
    workspace: Workspace = Depends(get_current_workspace),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RetrievalResponse:
    queries = db.query(RagQuery).filter(
        RagQuery.workspace_id == workspace.id
    ).order_by(RagQuery.created_at.desc()).all()

    total_queries = len(queries)
    if total_queries == 0:
        return RetrievalResponse(
            total_queries=0,
            average_confidence=0.0,
            low_confidence_query_count=0,
            average_latency_ms=0.0,
            latency_p50_ms=0.0,
            latency_p95_ms=0.0,
            latency_p99_ms=0.0,
            total_estimated_cost_usd=0.0,
            citation_rate=0.0,
            average_hallucination_risk=0.0,
            average_citation_coverage=0.0,
            average_retrieval_precision=0.0,
            average_answer_completeness=0.0,
            recent_queries=[],
        )

    avg_conf = sum(q.confidence for q in queries) / total_queries
    low_conf = sum(1 for q in queries if q.confidence < settings.low_confidence_threshold)
    avg_lat = sum(q.latency_ms for q in queries) / total_queries
    total_cost = sum(q.estimated_cost_usd for q in queries)
    latencies = [float(q.latency_ms) for q in queries]

    cited = sum(1 for q in queries if _has_citations(q))
    citation_rate = cited / total_queries

    return RetrievalResponse(
        total_queries=total_queries,
        average_confidence=round(avg_conf, 4),
        low_confidence_query_count=low_conf,
        average_latency_ms=round(avg_lat, 2),
        latency_p50_ms=percentile(latencies, 50),
        latency_p95_ms=percentile(latencies, 95),
        latency_p99_ms=percentile(latencies, 99),
        total_estimated_cost_usd=round(total_cost, 6),
        citation_rate=round(citation_rate, 4),
        average_hallucination_risk=round(
            sum(q.hallucination_risk for q in queries) / total_queries, 4
        ),
        average_citation_coverage=round(
            sum(q.citation_coverage for q in queries) / total_queries, 4
        ),
        average_retrieval_precision=round(
            sum(q.retrieval_precision for q in queries) / total_queries, 4
        ),
        average_answer_completeness=round(
            sum(q.answer_completeness for q in queries) / total_queries, 4
        ),
        recent_queries=[
            RecentQuery(
                id=q.id,
                question=q.question,
                confidence=q.confidence,
                latency_ms=q.latency_ms,
                estimated_cost_usd=q.estimated_cost_usd,
                created_at=q.created_at,
            )
            for q in queries[:10]
        ],
    )


@router.get("/charts", response_model=ChartsResponse)
def charts_data(
    workspace: Workspace = Depends(get_current_workspace),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ChartsResponse:
    batches = (
        db.query(IngestionBatch)
        .filter(IngestionBatch.workspace_id == workspace.id)
        .order_by(IngestionBatch.started_at.asc())
        .limit(50)
        .all()
    )
    ingestion_points = [
        IngestionChartPoint(
            batch_label=b.filename[:20] + (
                f" ({b.started_at.strftime('%m/%d')})" if b.started_at else ""
            ),
            valid=b.valid_count,
            invalid=b.invalid_count,
            duplicate=b.duplicate_count,
        )
        for b in batches
    ]

    queries = (
        db.query(RagQuery)
        .filter(RagQuery.workspace_id == workspace.id)
        .order_by(RagQuery.created_at.asc())
        .limit(200)
        .all()
    )
    query_points = []
    for q in queries:
        has_cit = False
        if q.cited_ticket_ids_json:
            ids = json.loads(q.cited_ticket_ids_json)
            has_cit = len(ids) > 0
        query_points.append(
            QueryChartPoint(
                timestamp=q.created_at.isoformat() if q.created_at else "",
                confidence=round(q.confidence, 4),
                latency_ms=q.latency_ms,
                has_citations=has_cit,
            )
        )

    return ChartsResponse(ingestion=ingestion_points, queries=query_points)


@router.get("/cost", response_model=CostResponse)
def cost_metrics(
    workspace: Workspace = Depends(get_current_workspace),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CostResponse:
    queries = db.query(RagQuery).filter(RagQuery.workspace_id == workspace.id).all()

    grouped: dict[tuple[str, str], dict[str, float]] = defaultdict(
        lambda: {"count": 0.0, "cost": 0.0}
    )
    for q in queries:
        key = (q.provider or "unknown", q.model or "unknown")
        grouped[key]["count"] += 1
        grouped[key]["cost"] += q.estimated_cost_usd

    by_model = [
        CostByModel(
            provider=provider,
            model=model,
            query_count=int(vals["count"]),
            total_cost_usd=round(vals["cost"], 6),
        )
        for (provider, model), vals in sorted(
            grouped.items(), key=lambda kv: kv[1]["cost"], reverse=True
        )
    ]

    return CostResponse(
        total_estimated_cost_usd=round(sum(q.estimated_cost_usd for q in queries), 6),
        total_queries=len(queries),
        by_model=by_model,
    )


@router.get("/quality-by-area", response_model=QualityByAreaResponse)
def quality_by_area(
    workspace: Workspace = Depends(get_current_workspace),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> QualityByAreaResponse:
    queries = db.query(RagQuery).filter(
        RagQuery.workspace_id == workspace.id, RagQuery.product_area.isnot(None)
    ).all()

    grouped: dict[str, list[RagQuery]] = defaultdict(list)
    for q in queries:
        if q.product_area:
            grouped[q.product_area].append(q)

    areas = []
    for area, items in grouped.items():
        n = len(items)
        cited = sum(1 for q in items if _has_citations(q))
        areas.append(
            ProductAreaQuality(
                product_area=area,
                query_count=n,
                average_confidence=round(sum(q.confidence for q in items) / n, 4),
                average_hallucination_risk=round(
                    sum(q.hallucination_risk for q in items) / n, 4
                ),
                average_citation_coverage=round(
                    sum(q.citation_coverage for q in items) / n, 4
                ),
                average_retrieval_precision=round(
                    sum(q.retrieval_precision for q in items) / n, 4
                ),
                average_answer_completeness=round(
                    sum(q.answer_completeness for q in items) / n, 4
                ),
                citation_rate=round(cited / n, 4),
            )
        )

    areas.sort(key=lambda a: a.query_count, reverse=True)
    return QualityByAreaResponse(areas=areas)


@router.get("/failed-queries", response_model=FailedQueriesResponse)
def failed_queries(
    workspace: Workspace = Depends(get_current_workspace),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> FailedQueriesResponse:
    queries = db.query(RagQuery).filter(
        RagQuery.workspace_id == workspace.id
    ).order_by(RagQuery.created_at.desc()).all()

    items = []
    for q in queries:
        reason = _failure_reason(q)
        if reason is None:
            continue
        items.append(
            FailedQuery(
                id=q.id,
                question=q.question,
                confidence=q.confidence,
                reason=reason,
                feedback=q.feedback,
                product_area=q.product_area,
                created_at=q.created_at,
            )
        )

    return FailedQueriesResponse(count=len(items), items=items[:100])
