from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class EvalQuestion(BaseModel):
    question: str
    filters: dict[str, str] | None = None


class EvalRunRequest(BaseModel):
    name: str | None = None
    questions: list[EvalQuestion] | None = None


class EvalRunSummary(BaseModel):
    id: UUID
    name: str
    total_questions: int
    passed_count: int
    failed_count: int
    average_confidence: float
    average_latency_ms: float
    results_json: str | None
    created_at: datetime


class EvalRunResponse(BaseModel):
    id: UUID
    name: str
    total_questions: int
    passed_count: int
    failed_count: int
    average_confidence: float
    average_latency_ms: float
    results_json: str | None
    created_at: datetime


class SavedEvalQuestionResponse(BaseModel):
    id: UUID
    question: str
    filters_json: str | None
    created_at: datetime


class SavedEvalQuestionCreate(BaseModel):
    question: str
    filters: dict[str, str] | None = None


class SavedEvalQuestionUpdate(BaseModel):
    question: str | None = None
    filters: dict[str, str] | None = None
