"""V10a analytics schemas."""
from pydantic import BaseModel


class DashboardQueryRequest(BaseModel):
    time_range: str = "all"
    product_area: str | None = None


class TrendPoint(BaseModel):
    label: str
    value: float


class AgentPerformanceItem(BaseModel):
    user_id: str
    email: str
    conversations_handled: int
    resolutions: int
    avg_resolution_time_seconds: float | None
    avg_satisfaction: float | None


class DashboardSummaryResponse(BaseModel):
    total_conversations: int
    resolved_conversations: int
    open_conversations: int
    containment_rate: float
    avg_resolution_time_seconds: float | None
    avg_satisfaction: float | None
    total_rag_queries: int
    avg_confidence: float
    total_tool_executions: int
    tool_success_rate: float
    sla_breach_count: int
    trend: list[TrendPoint]


class AgentPerformanceResponse(BaseModel):
    items: list[AgentPerformanceItem]
    total: int


class TrendDataResponse(BaseModel):
    metric: str
    data_points: list[TrendPoint]


class SavedReportCreateRequest(BaseModel):
    name: str
    report_type: str
    filters: dict = {}


class SavedReportResponse(BaseModel):
    id: str
    name: str
    report_type: str
    filters: dict
    created_by: str
    created_at: str


class SavedReportListResponse(BaseModel):
    items: list[SavedReportResponse]
    total: int


class ExportJobCreateRequest(BaseModel):
    report_type: str
    filters: dict = {}


class ExportJobResponse(BaseModel):
    id: str
    report_type: str
    filters: dict
    status: str
    row_count: int
    created_by: str
    created_at: str
    completed_at: str | None


class ExportJobListResponse(BaseModel):
    items: list[ExportJobResponse]
    total: int
