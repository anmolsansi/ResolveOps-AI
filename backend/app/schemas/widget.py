from uuid import UUID

from pydantic import BaseModel


class WidgetSessionStartRequest(BaseModel):
    customer_email: str | None = None
    customer_name: str | None = None
    subject: str | None = None
    workspace_id: str | None = None


class WidgetSessionStartResponse(BaseModel):
    conversation_id: UUID
    status: str


class WidgetChatRequest(BaseModel):
    message: str
    conversation_id: UUID | None = None
    customer_email: str | None = None
    customer_name: str | None = None
    workspace_id: str | None = None


class WidgetChatResponse(BaseModel):
    answer: str
    conversation_id: UUID
    message_id: UUID
    citations: list[str]
    confidence: float
    is_fallback: bool
    sentiment: str | None = None
    should_escalate: bool = False
    tool_results: list[dict] = []


class WidgetFeedbackRequest(BaseModel):
    message_id: UUID
    feedback: str  # helpful | not_helpful | wrong_answer
