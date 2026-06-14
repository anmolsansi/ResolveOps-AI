from pydantic import BaseModel


class ToolSummary(BaseModel):
    id: str
    name: str
    slug: str
    description: str
    handler: str
    enabled: bool
    category: str
    parameters_schema: dict
    created_at: str


class ToolListResponse(BaseModel):
    items: list[ToolSummary]
    total: int


class ToolUpdateRequest(BaseModel):
    enabled: bool | None = None
    description: str | None = None


class ToolExecuteRequest(BaseModel):
    parameters: dict
    conversation_id: str | None = None


class ToolExecutionResponse(BaseModel):
    id: str
    tool_id: str
    tool_name: str
    input: dict
    output: dict | None = None
    status: str
    error: str | None = None
    latency_ms: int | None = None
    triggered_by: str
    created_at: str


class ToolExecutionListResponse(BaseModel):
    items: list[ToolExecutionResponse]
    total: int


class ActionLogResponse(BaseModel):
    id: str
    action_type: str
    resource_type: str
    resource_id: str | None = None
    tool_execution_id: str | None = None
    detail: str | None = None
    actor: str
    created_at: str


class ActionLogListResponse(BaseModel):
    items: list[ActionLogResponse]
    total: int
