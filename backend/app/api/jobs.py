import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_member
from app.core.database import get_db
from app.models.models import BackgroundJob, User
from app.schemas.jobs import (
    JobCreate,
    JobListResponse,
    JobProcessResponse,
    JobResponse,
)
from app.services.audit import record_audit
from app.services.jobs import JOB_TYPES, enqueue_job, process_pending_jobs

router = APIRouter()


def _to_response(j: BackgroundJob) -> JobResponse:
    return JobResponse(
        id=j.id,
        job_type=j.job_type,
        status=j.status,
        payload_json=j.payload_json,
        result_json=j.result_json,
        error=j.error,
        attempts=j.attempts,
        created_at=j.created_at,
        started_at=j.started_at,
        finished_at=j.finished_at,
    )


@router.post("", response_model=JobResponse)
def create_job(
    payload: JobCreate,
    user: User = Depends(require_member),
    db: Session = Depends(get_db),
) -> JobResponse:
    if payload.job_type not in JOB_TYPES:
        raise HTTPException(status_code=422, detail=f"job_type must be one of {list(JOB_TYPES)}")
    job = enqueue_job(db, payload.job_type, payload.payload)
    record_audit(
        db,
        actor_email=user.email,
        action="job.enqueue",
        resource_type="job",
        resource_id=str(job.id),
        detail=job.job_type,
    )
    return _to_response(job)


@router.get("", response_model=JobListResponse)
def list_jobs(
    status_filter: str | None = Query(default=None, alias="status"),
    limit: int = Query(default=50, le=200),
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> JobListResponse:
    query = db.query(BackgroundJob)
    if status_filter:
        query = query.filter(BackgroundJob.status == status_filter)
    jobs = query.order_by(BackgroundJob.created_at.desc()).limit(limit).all()
    return JobListResponse(jobs=[_to_response(j) for j in jobs])


@router.post("/process-pending", response_model=JobProcessResponse)
def process_pending(
    limit: int = Query(default=10, le=100),
    user: User = Depends(require_member),
    db: Session = Depends(get_db),
) -> JobProcessResponse:
    processed = process_pending_jobs(db, limit=limit)
    succeeded = sum(1 for j in processed if j.status == "succeeded")
    failed = sum(1 for j in processed if j.status == "failed")
    if processed:
        record_audit(
            db,
            actor_email=user.email,
            action="job.process",
            resource_type="job",
            detail=f"processed={len(processed)} ok={succeeded} failed={failed}",
        )
    return JobProcessResponse(
        processed=len(processed),
        succeeded=succeeded,
        failed=failed,
        jobs=[_to_response(j) for j in processed],
    )


@router.get("/{job_id}", response_model=JobResponse)
def get_job(
    job_id: str, _: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> JobResponse:
    try:
        jid = uuid.UUID(job_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid id")
    job = db.get(BackgroundJob, jid)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return _to_response(job)
