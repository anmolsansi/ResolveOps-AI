"""V9 workflow API: routing rules, canned responses, and portal articles."""
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_workspace
from app.core.database import get_db
from app.models.models import Workspace
from app.schemas.workflow import (
    CannedResponseCreateRequest,
    CannedResponseListResponse,
    CannedResponseResponse,
    CannedResponseUpdateRequest,
    PortalArticleCreateRequest,
    PortalArticleListResponse,
    PortalArticleResponse,
    PortalArticleUpdateRequest,
    PortalSearchResponse,
    RoutingRuleCreateRequest,
    RoutingRuleListResponse,
    RoutingRuleResponse,
    RoutingRuleUpdateRequest,
)
from app.services import canned_responses as cr_svc
from app.services import portal as portal_svc
from app.services import routing as routing_svc

router = APIRouter()


# --- Routing Rules ---


@router.get("/routing", response_model=RoutingRuleListResponse)
def list_routing(
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db),
) -> RoutingRuleListResponse:
    items = routing_svc.list_routing_rules(db, workspace.id)
    return RoutingRuleListResponse(
        items=[RoutingRuleResponse(**i) for i in items],
        total=len(items),
    )


@router.post("/routing", response_model=RoutingRuleResponse)
def create_routing(
    body: RoutingRuleCreateRequest,
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db),
) -> RoutingRuleResponse:
    result = routing_svc.create_routing_rule(
        db, workspace.id, body.name, body.description,
        body.priority, body.conditions, body.actions,
    )
    db.commit()
    return RoutingRuleResponse(**result)


@router.put("/routing/{rule_id}", response_model=RoutingRuleResponse)
def update_routing(
    rule_id: str,
    body: RoutingRuleUpdateRequest,
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db),
) -> RoutingRuleResponse:
    result = routing_svc.update_routing_rule(
        db, uuid.UUID(rule_id), workspace.id,
        name=body.name, description=body.description,
        priority=body.priority, enabled=body.enabled,
        conditions=body.conditions, actions=body.actions,
    )
    if not result:
        raise HTTPException(status_code=404, detail="Rule not found")
    db.commit()
    return RoutingRuleResponse(**result)


@router.delete("/routing/{rule_id}")
def delete_routing(
    rule_id: str,
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db),
) -> dict:
    ok = routing_svc.delete_routing_rule(db, uuid.UUID(rule_id), workspace.id)
    if not ok:
        raise HTTPException(status_code=404, detail="Rule not found")
    db.commit()
    return {"ok": True}


# --- Canned Responses ---


@router.get("/canned-responses", response_model=CannedResponseListResponse)
def list_canned(
    category: str | None = None,
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db),
) -> CannedResponseListResponse:
    items = cr_svc.list_canned_responses(db, workspace.id, category)
    return CannedResponseListResponse(
        items=[CannedResponseResponse(**i) for i in items],
        total=len(items),
    )


@router.post("/canned-responses", response_model=CannedResponseResponse)
def create_canned(
    body: CannedResponseCreateRequest,
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db),
) -> CannedResponseResponse:
    result = cr_svc.create_canned_response(
        db, workspace.id, body.title, body.content,
        body.category, body.shortcut,
    )
    db.commit()
    return CannedResponseResponse(**result)


@router.put("/canned-responses/{response_id}", response_model=CannedResponseResponse)
def update_canned(
    response_id: str,
    body: CannedResponseUpdateRequest,
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db),
) -> CannedResponseResponse:
    result = cr_svc.update_canned_response(
        db, uuid.UUID(response_id), workspace.id,
        title=body.title, content=body.content,
        category=body.category, shortcut=body.shortcut,
        enabled=body.enabled,
    )
    if not result:
        raise HTTPException(status_code=404, detail="Response not found")
    db.commit()
    return CannedResponseResponse(**result)


@router.delete("/canned-responses/{response_id}")
def delete_canned(
    response_id: str,
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db),
) -> dict:
    ok = cr_svc.delete_canned_response(db, uuid.UUID(response_id), workspace.id)
    if not ok:
        raise HTTPException(status_code=404, detail="Response not found")
    db.commit()
    return {"ok": True}


@router.post("/canned-responses/{response_id}/use", response_model=CannedResponseResponse)
def use_canned(
    response_id: str,
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db),
) -> CannedResponseResponse:
    result = cr_svc.use_canned_response(db, uuid.UUID(response_id), workspace.id)
    if not result:
        raise HTTPException(status_code=404, detail="Response not found")
    db.commit()
    return CannedResponseResponse(**result)


@router.get("/canned-responses/search", response_model=CannedResponseListResponse)
def search_canned(
    q: str = "",
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db),
) -> CannedResponseListResponse:
    items = cr_svc.search_canned_responses(db, workspace.id, q)
    return CannedResponseListResponse(
        items=[CannedResponseResponse(**i) for i in items],
        total=len(items),
    )


# --- Portal Articles ---


@router.get("/portal", response_model=PortalArticleListResponse)
def list_portal(
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db),
) -> PortalArticleListResponse:
    items = portal_svc.list_portal_articles(db, workspace.id, published_only=False)
    return PortalArticleListResponse(
        items=[PortalArticleResponse(**i) for i in items],
        total=len(items),
    )


@router.post("/portal", response_model=PortalArticleResponse)
def create_portal(
    body: PortalArticleCreateRequest,
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db),
) -> PortalArticleResponse:
    result = portal_svc.create_portal_article(
        db, workspace.id, body.title, body.content,
        body.category, body.product_area, body.tags, body.published,
    )
    db.commit()
    return PortalArticleResponse(**result)


@router.put("/portal/{article_id}", response_model=PortalArticleResponse)
def update_portal(
    article_id: str,
    body: PortalArticleUpdateRequest,
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db),
) -> PortalArticleResponse:
    result = portal_svc.update_portal_article(
        db, uuid.UUID(article_id), workspace.id,
        title=body.title, content=body.content,
        category=body.category, product_area=body.product_area,
        tags=body.tags, published=body.published,
    )
    if not result:
        raise HTTPException(status_code=404, detail="Article not found")
    db.commit()
    return PortalArticleResponse(**result)


@router.delete("/portal/{article_id}")
def delete_portal(
    article_id: str,
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db),
) -> dict:
    ok = portal_svc.delete_portal_article(db, uuid.UUID(article_id), workspace.id)
    if not ok:
        raise HTTPException(status_code=404, detail="Article not found")
    db.commit()
    return {"ok": True}


@router.get("/portal/search", response_model=PortalSearchResponse)
def search_portal(
    q: str = "",
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db),
) -> PortalSearchResponse:
    items = portal_svc.search_portal_articles(db, workspace.id, q)
    return PortalSearchResponse(
        items=[
            {
                "id": i["id"], "title": i["title"], "slug": i["slug"],
                "content": i["content"], "category": i["category"],
                "tags": i["tags"], "view_count": i["view_count"],
            }
            for i in items
        ],
        total=len(items),
    )


@router.get("/portal/ticket-status")
def ticket_status(
    ticket_id: str,
    email: str | None = None,
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db),
) -> dict:
    result = portal_svc.lookup_ticket_status(db, ticket_id, workspace.id, email)
    if not result:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return result
