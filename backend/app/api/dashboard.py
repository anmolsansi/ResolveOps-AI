import json

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.models import IngestionBatch, RagQuery
from app.schemas.dashboard import (
    BatchSummary,
    ChartsResponse,
    IngestionChartPoint,
    QualityResponse,
    QueryChartPoint,
    RecentQuery,
    RetrievalResponse,
)

router = APIRouter()


@router.get("/quality", response_model=QualityResponse)
def quality_metrics(db: Session = Depends(get_db)) -> QualityResponse:
    batches = db.query(IngestionBatch).order_by(IngestionBatch.started_at.desc()).all()

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
def retrieval_metrics(db: Session = Depends(get_db)) -> RetrievalResponse:
    queries = db.query(RagQuery).order_by(RagQuery.created_at.desc()).all()

    total_queries = len(queries)
    if total_queries == 0:
        return RetrievalResponse(
            total_queries=0,
            average_confidence=0.0,
            low_confidence_query_count=0,
            average_latency_ms=0.0,
            total_estimated_cost_usd=0.0,
            citation_rate=0.0,
            recent_queries=[],
        )

    avg_conf = sum(q.confidence for q in queries) / total_queries
    low_conf = sum(1 for q in queries if q.confidence < settings.low_confidence_threshold)
    avg_lat = sum(q.latency_ms for q in queries) / total_queries
    total_cost = sum(q.estimated_cost_usd for q in queries)

    cited = 0
    for q in queries:
        if q.cited_ticket_ids_json:
            ids = json.loads(q.cited_ticket_ids_json)
            if ids:
                cited += 1
    citation_rate = cited / total_queries

    return RetrievalResponse(
        total_queries=total_queries,
        average_confidence=round(avg_conf, 4),
        low_confidence_query_count=low_conf,
        average_latency_ms=round(avg_lat, 2),
        total_estimated_cost_usd=round(total_cost, 6),
        citation_rate=round(citation_rate, 4),
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
def charts_data(db: Session = Depends(get_db)) -> ChartsResponse:
    batches = (
        db.query(IngestionBatch)
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
