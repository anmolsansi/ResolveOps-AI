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


class EvalConfig(BaseModel):
    label: str
    top_k: int = 5
    threshold: float = 0.3


class EvalCompareRequest(BaseModel):
    name: str | None = None
    questions: list[EvalQuestion] | None = None
    config_a: EvalConfig
    config_b: EvalConfig


class ConfigResult(BaseModel):
    label: str
    top_k: int
    threshold: float
    passed_count: int
    failed_count: int
    average_confidence: float
    average_latency_ms: float
    average_hallucination_risk: float


class QuestionDelta(BaseModel):
    question: str
    confidence_a: float
    confidence_b: float
    confidence_delta: float
    passed_a: bool
    passed_b: bool


class EvalCompareResponse(BaseModel):
    name: str
    total_questions: int
    config_a: ConfigResult
    config_b: ConfigResult
    passed_delta: int
    confidence_delta: float
    latency_delta_ms: float
    hallucination_risk_delta: float
    per_question: list[QuestionDelta]
