import csv
import io
import json
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import IngestionBatch, Ticket, TicketChunk
from app.schemas.tickets import (
    ChunkPreview,
    RowError,
    TicketDetail,
    TicketListResponse,
    TicketSummary,
    UploadResponse,
)
from app.services.chunking import build_ticket_text, chunk_text, estimate_tokens
from app.services.providers.factory import get_embedding_provider

router = APIRouter()

REQUIRED_COLUMNS = [
    "id", "title", "body", "product_area", "issue_type",
    "priority", "customer_tier", "status", "resolution", "created_at",
]

REQUIRED_FIELDS = [
    "id", "title", "body", "product_area", "issue_type",
    "priority", "customer_tier", "status", "resolution", "created_at",
]


def _parse_date(value: str) -> datetime | None:
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d", "%m/%d/%Y"):
        try:
            return datetime.strptime(value.strip(), fmt)
        except ValueError:
            continue
    return None


@router.post("/upload", response_model=UploadResponse)
def upload_tickets(file: UploadFile, db: Session = Depends(get_db)) -> UploadResponse:
    if not file.filename or not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted")

    content = file.file.read().decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(content))

    if not reader.fieldnames:
        raise HTTPException(status_code=400, detail="CSV file is empty or has no headers")

    missing_cols = [c for c in REQUIRED_COLUMNS if c not in reader.fieldnames]
    if missing_cols:
        raise HTTPException(
            status_code=400,
            detail=f"Missing required columns: {', '.join(missing_cols)}",
        )

    batch = IngestionBatch(filename=file.filename or "upload.csv")
    db.add(batch)
    db.flush()

    errors: list[RowError] = []
    total = 0
    valid = 0
    invalid = 0
    duplicate = 0
    embedding_failures = 0
    provider = get_embedding_provider()

    existing_ids: set[str] = set()
    db_existing = db.query(Ticket.id).all()
    for (tid,) in db_existing:
        existing_ids.add(tid)
    batch_seen_ids: set[str] = set()

    for row_num, row in enumerate(reader, start=2):
        total += 1
        row_errors: list[str] = []

        for field in REQUIRED_FIELDS:
            if not row.get(field, "").strip():
                row_errors.append(f"Missing required field: {field}")

        ticket_id = row.get("id", "").strip()

        created_at = None
        if row.get("created_at", "").strip():
            created_at = _parse_date(row["created_at"])
            if created_at is None:
                row_errors.append("Invalid created_at date format")

        resolved_at = None
        if row.get("resolved_at", "").strip():
            resolved_at = _parse_date(row["resolved_at"])
            if resolved_at is None:
                row_errors.append("Invalid resolved_at date format")

        if row_errors:
            invalid += 1
            errors.append(
                RowError(
                    row=row_num,
                    ticket_id=ticket_id or None,
                    reason="; ".join(row_errors),
                )
            )
            continue

        if ticket_id in existing_ids or ticket_id in batch_seen_ids:
            duplicate += 1
            errors.append(
                RowError(row=row_num, ticket_id=ticket_id, reason="Duplicate ticket ID")
            )
            continue

        batch_seen_ids.add(ticket_id)

        ticket = Ticket(
            id=ticket_id,
            title=row["title"].strip(),
            body=row["body"].strip(),
            product_area=row["product_area"].strip(),
            issue_type=row["issue_type"].strip(),
            priority=row["priority"].strip(),
            customer_tier=row["customer_tier"].strip(),
            status=row["status"].strip(),
            resolution=row.get("resolution", "").strip(),
            created_at=created_at,  # type: ignore[arg-type]
            resolved_at=resolved_at,
            source_row_number=row_num,
            ingestion_batch_id=batch.id,
            validation_status="valid",
        )
        db.add(ticket)
        db.flush()

        ticket_text = build_ticket_text(ticket)
        text_chunks = chunk_text(ticket_text)

        try:
            embeddings = provider.embed_texts(text_chunks)
        except Exception:
            embedding_failures += 1
            embeddings = [None] * len(text_chunks)  # type: ignore[list-item]

        for idx, (chunk_str, emb) in enumerate(zip(text_chunks, embeddings)):
            tc = TicketChunk(
                ticket_id=ticket.id,
                chunk_index=idx,
                text=chunk_str,
                embedding=json.dumps(emb) if emb else None,
                token_count=estimate_tokens(chunk_str),
            )
            db.add(tc)

        valid += 1

    batch.total_count = total
    batch.valid_count = valid
    batch.invalid_count = invalid
    batch.duplicate_count = duplicate
    batch.embedding_failure_count = embedding_failures
    batch.completed_at = datetime.now(tz=None)
    db.commit()

    return UploadResponse(
        batch_id=batch.id,
        filename=batch.filename,
        total_count=total,
        valid_count=valid,
        invalid_count=invalid,
        duplicate_count=duplicate,
        embedding_failure_count=embedding_failures,
        errors=errors,
    )


@router.get("", response_model=TicketListResponse)
def list_tickets(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    product_area: str | None = None,
    issue_type: str | None = None,
    priority: str | None = None,
    customer_tier: str | None = None,
    status: str | None = None,
    search: str | None = None,
    db: Session = Depends(get_db),
) -> TicketListResponse:
    query = db.query(Ticket)

    if product_area:
        query = query.filter(Ticket.product_area == product_area)
    if issue_type:
        query = query.filter(Ticket.issue_type == issue_type)
    if priority:
        query = query.filter(Ticket.priority == priority)
    if customer_tier:
        query = query.filter(Ticket.customer_tier == customer_tier)
    if status:
        query = query.filter(Ticket.status == status)
    if search:
        pattern = f"%{search}%"
        query = query.filter(Ticket.title.ilike(pattern) | Ticket.body.ilike(pattern))

    total = query.count()
    offset = (page - 1) * page_size
    tickets = query.order_by(Ticket.created_at.desc()).offset(offset).limit(page_size).all()

    items = [
        TicketSummary(
            id=t.id,
            title=t.title,
            product_area=t.product_area,
            issue_type=t.issue_type,
            priority=t.priority,
            customer_tier=t.customer_tier,
            status=t.status,
            created_at=t.created_at,
            resolved_at=t.resolved_at,
        )
        for t in tickets
    ]

    return TicketListResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/{ticket_id}", response_model=TicketDetail)
def get_ticket(ticket_id: str, db: Session = Depends(get_db)) -> TicketDetail:
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    chunks = (
        db.query(TicketChunk)
        .filter(TicketChunk.ticket_id == ticket_id)
        .order_by(TicketChunk.chunk_index)
        .all()
    )

    return TicketDetail(
        id=ticket.id,
        title=ticket.title,
        body=ticket.body,
        product_area=ticket.product_area,
        issue_type=ticket.issue_type,
        priority=ticket.priority,
        customer_tier=ticket.customer_tier,
        status=ticket.status,
        resolution=ticket.resolution,
        created_at=ticket.created_at,
        resolved_at=ticket.resolved_at,
        ingestion_batch_id=ticket.ingestion_batch_id,
        validation_status=ticket.validation_status,
        validation_errors=ticket.validation_errors,
        chunks=[
            ChunkPreview(id=c.id, chunk_index=c.chunk_index, preview=c.text[:200])
            for c in chunks
        ],
    )
