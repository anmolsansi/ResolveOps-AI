from datetime import datetime, timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import Connector, IngestionJob
from app.schemas.connectors import (
    ConnectorCreate,
    ConnectorListResponse,
    ConnectorSummary,
    DuplicateCluster,
    DuplicatesResponse,
    JobCreate,
    JobListResponse,
    JobSummary,
    RunDueResponse,
    SyncResult,
)
from app.services.connectors.factory import SUPPORTED_PROVIDERS
from app.services.dedup import DEFAULT_DEDUP_THRESHOLD, find_duplicate_clusters
from app.services.sync import run_connector_sync

router = APIRouter()


def _connector_summary(c: Connector) -> ConnectorSummary:
    return ConnectorSummary(
        id=c.id,
        provider=c.provider,
        name=c.name,
        cursor=c.cursor,
        enabled=c.enabled,
        last_synced_at=c.last_synced_at,
        total_imported=c.total_imported,
        created_at=c.created_at,
    )


def _job_summary(j: IngestionJob) -> JobSummary:
    return JobSummary(
        id=j.id,
        connector_id=j.connector_id,
        interval_minutes=j.interval_minutes,
        enabled=j.enabled,
        next_run_at=j.next_run_at,
        last_run_at=j.last_run_at,
        last_status=j.last_status,
        last_imported=j.last_imported,
        created_at=j.created_at,
    )


@router.post("", response_model=ConnectorSummary)
def create_connector(req: ConnectorCreate, db: Session = Depends(get_db)) -> ConnectorSummary:
    provider = req.provider.lower().strip()
    if provider not in SUPPORTED_PROVIDERS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported provider. Supported: {', '.join(SUPPORTED_PROVIDERS)}",
        )
    connector = Connector(provider=provider, name=req.name.strip() or provider)
    db.add(connector)
    db.commit()
    db.refresh(connector)
    return _connector_summary(connector)


@router.get("", response_model=ConnectorListResponse)
def list_connectors(db: Session = Depends(get_db)) -> ConnectorListResponse:
    rows = db.query(Connector).order_by(Connector.created_at.desc()).all()
    return ConnectorListResponse(items=[_connector_summary(c) for c in rows])


@router.delete("/{connector_id}")
def delete_connector(connector_id: UUID, db: Session = Depends(get_db)) -> dict:
    connector = db.query(Connector).filter(Connector.id == connector_id).first()
    if not connector:
        raise HTTPException(status_code=404, detail="Connector not found")
    db.query(IngestionJob).filter(IngestionJob.connector_id == connector_id).delete()
    db.delete(connector)
    db.commit()
    return {"deleted": str(connector_id)}


@router.post("/{connector_id}/sync", response_model=SyncResult)
def sync_connector(
    connector_id: UUID,
    limit: int = Query(6, ge=1, le=100),
    db: Session = Depends(get_db),
) -> SyncResult:
    connector = db.query(Connector).filter(Connector.id == connector_id).first()
    if not connector:
        raise HTTPException(status_code=404, detail="Connector not found")
    result = run_connector_sync(db, connector, limit=limit)
    return SyncResult(**result)


@router.post("/{connector_id}/jobs", response_model=JobSummary)
def create_job(
    connector_id: UUID, req: JobCreate, db: Session = Depends(get_db)
) -> JobSummary:
    connector = db.query(Connector).filter(Connector.id == connector_id).first()
    if not connector:
        raise HTTPException(status_code=404, detail="Connector not found")
    job = IngestionJob(
        connector_id=connector_id,
        interval_minutes=req.interval_minutes,
        next_run_at=datetime.now(tz=None),
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return _job_summary(job)


@router.get("/jobs", response_model=JobListResponse)
def list_jobs(db: Session = Depends(get_db)) -> JobListResponse:
    rows = db.query(IngestionJob).order_by(IngestionJob.created_at.desc()).all()
    return JobListResponse(items=[_job_summary(j) for j in rows])


@router.post("/jobs/run-due", response_model=RunDueResponse)
def run_due_jobs(
    limit: int = Query(6, ge=1, le=100), db: Session = Depends(get_db)
) -> RunDueResponse:
    now = datetime.now(tz=None)
    jobs = (
        db.query(IngestionJob)
        .filter(IngestionJob.enabled.is_(True), IngestionJob.next_run_at <= now)
        .all()
    )
    results: list[SyncResult] = []
    for job in jobs:
        connector = db.query(Connector).filter(Connector.id == job.connector_id).first()
        if not connector or not connector.enabled:
            continue
        result = run_connector_sync(db, connector, limit=limit)
        job.last_run_at = now
        job.next_run_at = now + timedelta(minutes=job.interval_minutes)
        job.last_status = "success"
        job.last_imported = result["imported"]
        db.commit()
        results.append(SyncResult(**result))
    return RunDueResponse(ran=len(results), results=results)


@router.get("/duplicates", response_model=DuplicatesResponse)
def list_duplicates(
    threshold: float = Query(DEFAULT_DEDUP_THRESHOLD, ge=0.0, le=1.0),
    db: Session = Depends(get_db),
) -> DuplicatesResponse:
    clusters = find_duplicate_clusters(db, threshold=threshold)
    return DuplicatesResponse(
        clusters=[DuplicateCluster(**c) for c in clusters]
    )
