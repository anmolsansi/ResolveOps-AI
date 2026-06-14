from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ConversationSummary(BaseModel):
    id: UUID
    channel: str
    status: str
    subject: str | None = None
    customer_name: str | None = None
    customer_email: str | None = None
    sentiment: str | None = None
    ai_resolution_outcome: str | None = None
    last_message_at: datetime
    created_at: datetime


class ConversationListResponse(BaseModel):
    items: list[ConversationSummary]
    total: int
    page: int
    page_size: int


class ConversationMessageResponse(BaseModel):
    id: UUID
    role: str
    content: str
    citations: list[str] | None = None
    confidence: float | None = None
    is_escalation_trigger: bool
    created_at: datetime


class ConversationDetailResponse(BaseModel):
    id: UUID
    channel: str
    status: str
    subject: str | None = None
    product_area: str | None = None
    sentiment: str | None = None
    ai_resolution_outcome: str | None = None
    resolution_summary: str | None = None
    customer: "CustomerSummary"
    messages: list[ConversationMessageResponse]
    handoffs: list["HandoffSummary"]
    started_at: datetime
    last_message_at: datetime
    resolved_at: datetime | None = None
    created_at: datetime


class CustomerSummary(BaseModel):
    id: UUID
    external_id: str
    name: str | None = None
    email: str | None = None
    company: str | None = None
    customer_tier: str
    sentiment_score: float
    total_conversations: int
    unresolved_issues: int


class ConversationStatusUpdate(BaseModel):
    status: str


class AgentReplyRequest(BaseModel):
    content: str


class HandoffSummary(BaseModel):
    id: UUID
    trigger_reason: str
    summary: str
    likely_intent: str
    suggested_reply: str | None = None
    status: str
    assigned_to: UUID | None = None
    created_at: datetime
    resolved_at: datetime | None = None


class HandoffListResponse(BaseModel):
    items: list[HandoffSummary]
    pending_count: int


class HandoffCreateRequest(BaseModel):
    trigger_reason: str
    summary: str
    likely_intent: str
    suggested_reply: str | None = None


class HandoffUpdateRequest(BaseModel):
    status: str
    assigned_to: UUID | None = None


class CustomerProfileResponse(BaseModel):
    id: UUID
    external_id: str
    name: str | None = None
    email: str | None = None
    company: str | None = None
    customer_tier: str
    sentiment_score: float
    total_conversations: int
    unresolved_issues: int
    last_seen_at: datetime | None = None
    created_at: datetime


class CustomerTimelineItem(BaseModel):
    conversation_id: UUID
    channel: str
    status: str
    subject: str | None = None
    summary: str | None = None
    created_at: datetime


class CustomerProfileDetailResponse(BaseModel):
    profile: CustomerProfileResponse
    timeline: list[CustomerTimelineItem]


class CustomerListResponse(BaseModel):
    items: list[CustomerProfileResponse]
    total: int
    page: int
    page_size: int


class ResolutionOutcomeRequest(BaseModel):
    """Request body for submitting a resolution outcome."""
    # ai_contained | human_escalated | bad_answer | missing_knowledge | customer_reopened
    outcome: str
    notes: str | None = None
    customer_satisfaction: str | None = None


class ResolutionOutcomeResponse(BaseModel):
    id: UUID
    conversation_id: UUID
    outcome: str
    confidence_at_resolution: float
    total_messages: int
    ai_message_count: int
    human_message_count: int
    created_at: datetime
