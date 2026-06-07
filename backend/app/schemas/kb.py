from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class KbArticleResponse(BaseModel):
    id: UUID
    title: str
    product_area: str
    issue_type: str
    summary: str
    resolution_steps: str
    source_ticket_ids: list[str]
    ticket_count: int
    created_at: datetime


class KbListResponse(BaseModel):
    items: list[KbArticleResponse]


class KbGenerateResponse(BaseModel):
    generated: int
    items: list[KbArticleResponse]
