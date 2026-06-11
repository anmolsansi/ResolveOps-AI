from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class JobCreate(BaseModel):
    job_type: str
    payload: dict | None = None


class JobResponse(BaseModel):
    id: UUID
    job_type: str
    status: str
    payload_json: str | None
    result_json: str | None
    error: str | None
    attempts: int
    created_at: datetime
    started_at: datetime | None
    finished_at: datetime | None


class JobListResponse(BaseModel):
    jobs: list[JobResponse]


class JobProcessResponse(BaseModel):
    processed: int
    succeeded: int
    failed: int
    jobs: list[JobResponse]
