"""In-process background job queue.

Jobs are persisted in ``background_jobs`` and processed by ``process_pending_jobs``
(invoked synchronously via the API for determinism/testing, or by a worker loop
in production). Each job type maps to a handler that returns a JSON-serializable
result dict.
"""
from __future__ import annotations

import json
import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.models import BackgroundJob, Connector, Ticket, TicketChunk
from app.services.pii import redact_pii
from app.services.providers.factory import get_embedding_provider

JOB_TYPES = ("embedding_backfill", "connector_sync", "retention_run", "pii_redact_tickets")


def enqueue_job(db: Session, job_type: str, payload: dict | None = None) -> BackgroundJob:
    if job_type not in JOB_TYPES:
        raise ValueError(f"Unknown job_type: {job_type}")
    job = BackgroundJob(
        job_type=job_type,
        status="pending",
        payload_json=json.dumps(payload) if payload else None,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


# ---- Handlers -------------------------------------------------------------


def _handle_embedding_backfill(db: Session, payload: dict) -> dict:
    provider = get_embedding_provider()
    missing = db.query(TicketChunk).filter(TicketChunk.embedding.is_(None)).all()
    embedded = 0
    for chunk in missing:
        vec = provider.embed_texts([chunk.text])[0]
        chunk.embedding = json.dumps(vec)
        embedded += 1
    db.commit()
    return {"chunks_embedded": embedded}


def _handle_connector_sync(db: Session, payload: dict) -> dict:
    from app.services.sync import run_connector_sync

    connector_id = payload.get("connector_id")
    if not connector_id:
        raise ValueError("connector_sync requires 'connector_id'")
    connector = db.get(Connector, uuid.UUID(str(connector_id)))
    if connector is None:
        raise ValueError("connector not found")
    limit = int(payload.get("limit", 6))
    result = run_connector_sync(db, connector, limit=limit)
    return {
        "fetched": result["fetched"],
        "imported": result["imported"],
        "duplicate_semantic": result["duplicate_semantic"],
        "cursor": result["cursor"],
    }


def _handle_retention_run(db: Session, payload: dict) -> dict:
    from app.services.retention import run_retention

    return run_retention(db)


def _handle_pii_redact_tickets(db: Session, payload: dict) -> dict:
    tickets = db.query(Ticket).all()
    redacted_count = 0
    total_pii = 0
    for ticket in tickets:
        new_title, c1 = redact_pii(ticket.title)
        new_body, c2 = redact_pii(ticket.body)
        hits = sum(c1.values()) + sum(c2.values())
        if hits:
            ticket.title = new_title
            ticket.body = new_body
            redacted_count += 1
            total_pii += hits
    if redacted_count:
        for chunk in db.query(TicketChunk).all():
            new_text, _ = redact_pii(chunk.text)
            chunk.text = new_text
    db.commit()
    return {"tickets_redacted": redacted_count, "pii_instances": total_pii}


_HANDLERS = {
    "embedding_backfill": _handle_embedding_backfill,
    "connector_sync": _handle_connector_sync,
    "retention_run": _handle_retention_run,
    "pii_redact_tickets": _handle_pii_redact_tickets,
}


def process_job(db: Session, job: BackgroundJob) -> BackgroundJob:
    job.status = "running"
    job.started_at = datetime.utcnow()
    job.attempts += 1
    db.commit()

    payload = json.loads(job.payload_json) if job.payload_json else {}
    try:
        result = _HANDLERS[job.job_type](db, payload)
        job.result_json = json.dumps(result)
        job.status = "succeeded"
        job.error = None
    except Exception as exc:  # noqa: BLE001 - record failure on the job row
        db.rollback()
        job.status = "failed"
        job.error = str(exc)
    job.finished_at = datetime.utcnow()
    db.commit()
    db.refresh(job)
    return job


def process_pending_jobs(db: Session, limit: int = 10) -> list[BackgroundJob]:
    pending = (
        db.query(BackgroundJob)
        .filter(BackgroundJob.status == "pending")
        .order_by(BackgroundJob.created_at.asc())
        .limit(limit)
        .all()
    )
    return [process_job(db, job) for job in pending]
