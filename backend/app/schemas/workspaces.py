from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class WorkspaceCreate(BaseModel):
    name: str
    slug: str | None = None


class WorkspaceResponse(BaseModel):
    id: UUID
    name: str
    slug: str
    member_count: int
    created_at: datetime


class WorkspaceListResponse(BaseModel):
    workspaces: list[WorkspaceResponse]


class MemberAddRequest(BaseModel):
    email: str
    role: str = "member"


class MemberRoleUpdate(BaseModel):
    role: str


class MemberResponse(BaseModel):
    membership_id: UUID
    user_id: UUID
    email: str
    role: str
    created_at: datetime


class MemberListResponse(BaseModel):
    workspace_id: UUID
    members: list[MemberResponse]
