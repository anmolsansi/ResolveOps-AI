"""V6 conversations API: admin-facing endpoints for managing conversations,
handoffs, and customer profiles."""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_current_workspace
from app.core.database import get_db
from app.models.models import User, Workspace
from app.schemas.conversations import (
    AgentReplyRequest,
    ConversationDetailResponse,
    ConversationListResponse,
    ConversationStatusUpdate,
    CustomerListResponse,
    CustomerProfileDetailResponse,
    HandoffCreateRequest,
    HandoffListResponse,
    HandoffUpdateRequest,
    ResolutionOutcomeRequest,
    ResolutionOutcomeResponse,
)
from app.services import conversations as conv_svc

router = APIRouter()


@router.get("", response_model=ConversationListResponse)
def list_conversations(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str | None = None,
    channel: str | None = None,
    workspace: Workspace = Depends(get_current_workspace),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ConversationListResponse:
    result = conv_svc.list_conversations(
        db, workspace.id, status=status, channel=channel,
        page=page, page_size=page_size,
    )
    return ConversationListResponse(**result)


@router.get("/handoffs", response_model=HandoffListResponse)
def list_handoffs(
    status: str | None = None,
    workspace: Workspace = Depends(get_current_workspace),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> HandoffListResponse:
    result = conv_svc.list_handoffs(db, workspace.id, status=status)
    return HandoffListResponse(**result)


@router.put("/handoffs/{handoff_id}")
def update_handoff(
    handoff_id: UUID,
    req: HandoffUpdateRequest,
    workspace: Workspace = Depends(get_current_workspace),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ok = conv_svc.update_handoff(db, handoff_id, req.status, req.assigned_to, workspace.id)
    if not ok:
        raise HTTPException(status_code=404, detail="Handoff not found")
    return {"status": "updated"}


@router.get("/customers", response_model=CustomerListResponse)
def list_customers(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    workspace: Workspace = Depends(get_current_workspace),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CustomerListResponse:
    result = conv_svc.list_customers(db, workspace.id, page=page, page_size=page_size)
    return CustomerListResponse(**result)


@router.get("/customers/{customer_id}", response_model=CustomerProfileDetailResponse)
def get_customer_profile(
    customer_id: UUID,
    workspace: Workspace = Depends(get_current_workspace),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CustomerProfileDetailResponse:
    result = conv_svc.get_customer_profile(db, customer_id, workspace.id)
    if not result:
        raise HTTPException(status_code=404, detail="Customer not found")
    return CustomerProfileDetailResponse(**result)


@router.get("/{conversation_id}", response_model=ConversationDetailResponse)
def get_conversation(
    conversation_id: UUID,
    workspace: Workspace = Depends(get_current_workspace),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ConversationDetailResponse:
    result = conv_svc.get_conversation_detail(db, conversation_id, workspace.id)
    if not result:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return ConversationDetailResponse(**result)


@router.put("/{conversation_id}/status")
def update_conversation_status(
    conversation_id: UUID,
    req: ConversationStatusUpdate,
    workspace: Workspace = Depends(get_current_workspace),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ok = conv_svc.update_conversation_status(db, conversation_id, req.status, workspace.id)
    if not ok:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"status": "updated"}


@router.post("/{conversation_id}/reply")
def agent_reply(
    conversation_id: UUID,
    req: AgentReplyRequest,
    workspace: Workspace = Depends(get_current_workspace),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    result = conv_svc.send_agent_reply(db, conversation_id, req.content, workspace.id)
    if not result:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return result


@router.post("/{conversation_id}/handoff")
def create_handoff(
    conversation_id: UUID,
    req: HandoffCreateRequest,
    workspace: Workspace = Depends(get_current_workspace),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    from app.models.models import HumanHandoff

    handoff = HumanHandoff(
        conversation_id=conversation_id,
        workspace_id=workspace.id,
        trigger_reason=req.trigger_reason,
        summary=req.summary,
        likely_intent=req.likely_intent,
        customer_profile_snapshot="{}",
        suggested_reply=req.suggested_reply,
    )
    db.add(handoff)
    db.commit()
    db.refresh(handoff)
    return {"id": str(handoff.id), "status": handoff.status}


@router.post("/{conversation_id}/resolve", response_model=ResolutionOutcomeResponse)
def resolve_conversation(
    conversation_id: UUID,
    req: ResolutionOutcomeRequest,
    workspace: Workspace = Depends(get_current_workspace),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ResolutionOutcomeResponse:
    result = conv_svc.resolve_conversation(
        db, conversation_id, req.outcome, req.notes, req.customer_satisfaction, workspace.id,
    )
    if not result:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return ResolutionOutcomeResponse(**result)
