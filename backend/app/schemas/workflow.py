import json
import re

from pydantic import BaseModel


# --- Routing Rules ---


class RoutingRuleCreateRequest(BaseModel):
    name: str
    description: str | None = None
    priority: int = 0
    conditions: dict = {}
    actions: dict = {}


class RoutingRuleUpdateRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    priority: int | None = None
    enabled: bool | None = None
    conditions: dict | None = None
    actions: dict | None = None


class RoutingRuleResponse(BaseModel):
    id: str
    name: str
    description: str | None = None
    priority: int
    enabled: bool
    conditions: dict
    actions: dict
    match_count: int
    created_at: str


class RoutingRuleListResponse(BaseModel):
    items: list[RoutingRuleResponse]
    total: int


# --- Canned Responses ---


class CannedResponseCreateRequest(BaseModel):
    title: str
    content: str
    category: str = "general"
    shortcut: str | None = None


class CannedResponseUpdateRequest(BaseModel):
    title: str | None = None
    content: str | None = None
    category: str | None = None
    shortcut: str | None = None
    enabled: bool | None = None


class CannedResponseResponse(BaseModel):
    id: str
    title: str
    content: str
    category: str
    shortcut: str | None = None
    usage_count: int
    enabled: bool
    created_at: str
    updated_at: str


class CannedResponseListResponse(BaseModel):
    items: list[CannedResponseResponse]
    total: int


# --- Portal Articles ---


class PortalArticleCreateRequest(BaseModel):
    title: str
    content: str
    category: str = "general"
    product_area: str | None = None
    tags: list[str] = []
    published: bool = False


class PortalArticleUpdateRequest(BaseModel):
    title: str | None = None
    content: str | None = None
    category: str | None = None
    product_area: str | None = None
    tags: list[str] | None = None
    published: bool | None = None


class PortalArticleResponse(BaseModel):
    id: str
    title: str
    slug: str
    content: str
    category: str
    product_area: str | None = None
    tags: list[str]
    published: bool
    view_count: int
    helpful_count: int
    created_at: str
    updated_at: str


class PortalArticlePublicResponse(BaseModel):
    id: str
    title: str
    slug: str
    content: str
    category: str
    tags: list[str]
    view_count: int


class PortalArticleListResponse(BaseModel):
    items: list[PortalArticleResponse]
    total: int


class PortalSearchResponse(BaseModel):
    items: list[PortalArticlePublicResponse]
    total: int


def _slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug or "article"
