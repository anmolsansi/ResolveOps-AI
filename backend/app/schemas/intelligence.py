from pydantic import BaseModel

# --- Performance metrics ---


class ToolUsageStats(BaseModel):
    tool_name: str
    slug: str
    total_executions: int
    success_count: int
    failure_count: int
    average_latency_ms: float


class PerformanceMetricsResponse(BaseModel):
    total_conversations: int
    resolved_conversations: int
    ai_contained: int
    human_escalated: int
    containment_rate: float
    average_resolution_time_seconds: float | None
    total_tool_executions: int
    tool_success_rate: float
    tool_usage: list[ToolUsageStats]
    sentiment_distribution: dict[str, int]
    top_escalation_reasons: list[dict]


# --- KB Suggestions ---


class KbSuggestionResponse(BaseModel):
    id: str
    suggested_title: str
    suggested_content: str
    product_area: str | None = None
    issue_type: str | None = None
    source_conversation_ids: list[str]
    occurrence_count: int
    status: str
    created_at: str


class KbSuggestionListResponse(BaseModel):
    items: list[KbSuggestionResponse]
    total: int


class KbSuggestionUpdateRequest(BaseModel):
    status: str  # accepted | dismissed


# --- Copilot Suggestions ---


class CopilotSuggestionResponse(BaseModel):
    id: str
    suggestion_type: str
    title: str
    content: str
    confidence: float
    status: str
    conversation_id: str | None = None
    created_at: str


class CopilotSuggestionListResponse(BaseModel):
    items: list[CopilotSuggestionResponse]
    total: int


class CopilotSuggestionUpdateRequest(BaseModel):
    status: str  # accepted | dismissed


# --- Conversation Summaries ---


class ConversationSummaryResponse(BaseModel):
    id: str
    conversation_id: str
    summary: str
    resolution_steps: str | None = None
    key_topics: list[str]
    sentiment_at_resolution: str | None = None
    created_at: str


class ConversationSummaryListResponse(BaseModel):
    items: list[ConversationSummaryResponse]
    total: int


# --- Feedback summary ---


class FeedbackSummaryResponse(BaseModel):
    total_feedback: int
    positive_count: int
    negative_count: int
    satisfaction_rate: float
    top_issues: list[dict]
    improvement_areas: list[str]
