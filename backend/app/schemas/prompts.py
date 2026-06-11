from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class PromptCreate(BaseModel):
    name: str
    content: str
    activate: bool = False


class PromptResponse(BaseModel):
    id: UUID
    name: str
    version: int
    content: str
    is_active: bool
    created_at: datetime


class PromptListResponse(BaseModel):
    prompts: list[PromptResponse]
    active_id: UUID | None
