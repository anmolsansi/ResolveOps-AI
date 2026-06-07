from enum import StrEnum

from pydantic import BaseModel


class Escalation(StrEnum):
    answer = "answer"
    ask_clarification = "ask_clarification"
    route_to_human = "route_to_human"


class AssistRequest(BaseModel):
    subject: str
    body: str = ""
    customer_tier: str | None = None
    product_area: str | None = None
    top_k: int = 5


class AssistRetrieved(BaseModel):
    ticket_id: str
    score: float
    preview: str
    product_area: str | None = None


class AssistResponse(BaseModel):
    recommendation: Escalation
    recommendation_reason: str
    confidence: float
    customer_facing_draft: str
    internal_note: str
    citations: list[str]
    tier_guidance: str
    retrieved: list[AssistRetrieved]
