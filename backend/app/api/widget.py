"""V6 widget API: public-facing endpoints for the embeddable chat widget."""
import json
import uuid as _uuid

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.models import Workspace
from app.schemas.widget import (
    WidgetChatRequest,
    WidgetChatResponse,
    WidgetFeedbackRequest,
    WidgetSessionStartRequest,
    WidgetSessionStartResponse,
)
from app.services.widget import create_or_find_customer, process_widget_message, start_conversation

router = APIRouter()


def _verify_widget_key(x_widget_key: str | None = Header(default=None)) -> None:
    if x_widget_key != settings.widget_api_key:
        raise HTTPException(status_code=401, detail="Invalid widget API key")


def _get_workspace_for_widget(db: Session, workspace_id: str | None = None) -> Workspace:
    if workspace_id:
        try:
            ws_uuid = _uuid.UUID(workspace_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid workspace_id")
        ws = db.query(Workspace).filter(Workspace.id == ws_uuid).first()
        if ws:
            return ws
    ws = db.query(Workspace).first()
    if not ws:
        ws = Workspace(name="Default Workspace", slug="default")
        db.add(ws)
        db.commit()
        db.refresh(ws)
    return ws


@router.get("/health")
def widget_health():
    return {"status": "ok", "version": "v6"}


@router.post("/session", response_model=WidgetSessionStartResponse)
def start_widget_session(
    req: WidgetSessionStartRequest,
    db: Session = Depends(get_db),
    _key: None = Depends(_verify_widget_key),
) -> WidgetSessionStartResponse:
    workspace = _get_workspace_for_widget(db, getattr(req, "workspace_id", None))
    customer = create_or_find_customer(db, req.customer_email, req.customer_name, workspace.id)
    conv = start_conversation(db, customer, workspace, channel="widget", subject=req.subject)
    return WidgetSessionStartResponse(conversation_id=conv.id, status=conv.status)


@router.post("/chat", response_model=WidgetChatResponse)
def widget_chat(
    req: WidgetChatRequest,
    db: Session = Depends(get_db),
    _key: None = Depends(_verify_widget_key),
) -> WidgetChatResponse:
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    workspace = _get_workspace_for_widget(db, getattr(req, "workspace_id", None))
    result = process_widget_message(
        db,
        message=req.message,
        conversation_id=req.conversation_id,
        customer_email=req.customer_email,
        customer_name=req.customer_name,
        workspace=workspace,
    )
    return WidgetChatResponse(**result)


@router.post("/feedback")
def widget_feedback(
    req: WidgetFeedbackRequest,
    db: Session = Depends(get_db),
    _key: None = Depends(_verify_widget_key),
):
    from app.models.models import ConversationMessage

    msg = db.query(ConversationMessage).filter(ConversationMessage.id == req.message_id).first()
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")
    metadata = json.loads(msg.metadata_json) if msg.metadata_json else {}
    metadata["customer_feedback"] = req.feedback
    msg.metadata_json = json.dumps(metadata)
    db.commit()
    return {"status": "recorded", "message_id": str(req.message_id), "feedback": req.feedback}
