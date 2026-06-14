"""V6 conversation management service for the admin dashboard."""
import json
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.models import (
    Conversation,
    ConversationMessage,
    CustomerProfile,
    HumanHandoff,
    ResolutionOutcome,
)


def list_conversations(
    db: Session,
    workspace_id,
    status: str | None = None,
    channel: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> dict:
    query = db.query(Conversation).filter(Conversation.workspace_id == workspace_id)
    if status:
        query = query.filter(Conversation.status == status)
    if channel:
        query = query.filter(Conversation.channel == channel)

    total = query.count()
    offset = (page - 1) * page_size
    convos = (
        query.order_by(Conversation.last_message_at.desc())
        .offset(offset).limit(page_size).all()
    )

    items = []
    for c in convos:
        customer = db.get(CustomerProfile, c.customer_id)
        items.append({
            "id": c.id,
            "channel": c.channel,
            "status": c.status,
            "subject": c.subject,
            "customer_name": customer.name if customer else None,
            "customer_email": customer.email if customer else None,
            "sentiment": c.sentiment,
            "ai_resolution_outcome": c.ai_resolution_outcome,
            "last_message_at": c.last_message_at,
            "created_at": c.created_at,
        })

    return {"items": items, "total": total, "page": page, "page_size": page_size}


def get_conversation_detail(db: Session, conversation_id, workspace_id) -> dict | None:
    conv = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.workspace_id == workspace_id,
    ).first()
    if not conv:
        return None

    customer = db.get(CustomerProfile, conv.customer_id)
    messages = (
        db.query(ConversationMessage)
        .filter(ConversationMessage.conversation_id == conv.id)
        .order_by(ConversationMessage.created_at.asc())
        .all()
    )
    handoffs = (
        db.query(HumanHandoff)
        .filter(HumanHandoff.conversation_id == conv.id)
        .order_by(HumanHandoff.created_at.desc())
        .all()
    )

    return {
        "id": conv.id,
        "channel": conv.channel,
        "status": conv.status,
        "subject": conv.subject,
        "product_area": conv.product_area,
        "sentiment": conv.sentiment,
        "ai_resolution_outcome": conv.ai_resolution_outcome,
        "resolution_summary": conv.resolution_summary,
        "customer": {
            "id": customer.id,
            "external_id": customer.external_id,
            "name": customer.name,
            "email": customer.email,
            "company": customer.company,
            "customer_tier": customer.customer_tier,
            "sentiment_score": customer.sentiment_score,
            "total_conversations": customer.total_conversations,
            "unresolved_issues": customer.unresolved_issues,
        } if customer else None,
        "messages": [
            {
                "id": m.id,
                "role": m.role,
                "content": m.content,
                "citations": json.loads(m.citations_json) if m.citations_json else None,
                "confidence": m.confidence,
                "is_escalation_trigger": m.is_escalation_trigger,
                "created_at": m.created_at,
            }
            for m in messages
        ],
        "handoffs": [
            {
                "id": h.id,
                "trigger_reason": h.trigger_reason,
                "summary": h.summary,
                "likely_intent": h.likely_intent,
                "suggested_reply": h.suggested_reply,
                "status": h.status,
                "assigned_to": h.assigned_to,
                "created_at": h.created_at,
                "resolved_at": h.resolved_at,
            }
            for h in handoffs
        ],
        "started_at": conv.started_at,
        "last_message_at": conv.last_message_at,
        "resolved_at": conv.resolved_at,
        "created_at": conv.created_at,
    }


def send_agent_reply(
    db: Session,
    conversation_id,
    content: str,
    workspace_id,
) -> dict | None:
    conv = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.workspace_id == workspace_id,
    ).first()
    if not conv:
        return None

    msg = ConversationMessage(
        conversation_id=conv.id,
        role="agent",
        content=content,
    )
    db.add(msg)
    conv.last_message_at = datetime.now(tz=None)
    if conv.status == "escalated":
        conv.status = "open"
    db.commit()
    db.refresh(msg)

    return {
        "id": msg.id,
        "role": msg.role,
        "content": msg.content,
        "created_at": msg.created_at,
    }


def update_conversation_status(
    db: Session,
    conversation_id,
    status: str,
    workspace_id,
) -> bool:
    conv = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.workspace_id == workspace_id,
    ).first()
    if not conv:
        return False
    conv.status = status
    if status in ("resolved", "escalated"):
        conv.resolved_at = datetime.now(tz=None)
    db.commit()
    return True


def resolve_conversation(
    db: Session,
    conversation_id,
    outcome: str,
    notes: str | None,
    customer_satisfaction: str | None,
    workspace_id,
) -> dict | None:
    conv = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.workspace_id == workspace_id,
    ).first()
    if not conv:
        return None

    messages = (
        db.query(ConversationMessage)
        .filter(ConversationMessage.conversation_id == conv.id)
        .all()
    )
    ai_count = sum(1 for m in messages if m.role == "ai")
    human_count = sum(1 for m in messages if m.role in ("agent", "customer"))
    first_msg_time = min((m.created_at for m in messages), default=None)
    last_msg_time = max((m.created_at for m in messages), default=None)
    time_to_resolution = None
    if first_msg_time and last_msg_time:
        time_to_resolution = int((last_msg_time - first_msg_time).total_seconds())

    resolution = ResolutionOutcome(
        conversation_id=conv.id,
        workspace_id=workspace_id,
        outcome=outcome,
        confidence_at_resolution=0.0,
        total_messages=len(messages),
        ai_message_count=ai_count,
        human_message_count=human_count,
        time_to_resolution_seconds=time_to_resolution,
        customer_satisfaction=customer_satisfaction,
        notes=notes,
    )
    db.add(resolution)

    conv.status = "resolved"
    conv.ai_resolution_outcome = outcome
    conv.resolution_summary = notes
    conv.resolved_at = datetime.now(tz=None)

    customer = db.get(CustomerProfile, conv.customer_id)
    if customer and customer.unresolved_issues > 0:
        customer.unresolved_issues -= 1

    db.commit()
    db.refresh(resolution)

    return {
        "id": resolution.id,
        "conversation_id": resolution.conversation_id,
        "outcome": resolution.outcome,
        "confidence_at_resolution": resolution.confidence_at_resolution,
        "total_messages": resolution.total_messages,
        "ai_message_count": resolution.ai_message_count,
        "human_message_count": resolution.human_message_count,
        "created_at": resolution.created_at,
    }


def list_handoffs(
    db: Session,
    workspace_id,
    status: str | None = None,
) -> dict:
    query = db.query(HumanHandoff).filter(HumanHandoff.workspace_id == workspace_id)
    if status:
        query = query.filter(HumanHandoff.status == status)

    pending_count = db.query(HumanHandoff).filter(
        HumanHandoff.workspace_id == workspace_id,
        HumanHandoff.status == "pending",
    ).count()

    handoffs = query.order_by(HumanHandoff.created_at.desc()).limit(100).all()

    return {
        "items": [
            {
                "id": h.id,
                "trigger_reason": h.trigger_reason,
                "summary": h.summary,
                "likely_intent": h.likely_intent,
                "suggested_reply": h.suggested_reply,
                "status": h.status,
                "assigned_to": h.assigned_to,
                "created_at": h.created_at,
                "resolved_at": h.resolved_at,
            }
            for h in handoffs
        ],
        "pending_count": pending_count,
    }


def update_handoff(
    db: Session,
    handoff_id,
    status: str,
    assigned_to=None,
    workspace_id=None,
) -> bool:
    query = db.query(HumanHandoff).filter(HumanHandoff.id == handoff_id)
    if workspace_id:
        query = query.filter(HumanHandoff.workspace_id == workspace_id)
    handoff = query.first()
    if not handoff:
        return False
    handoff.status = status
    if assigned_to:
        handoff.assigned_to = assigned_to
    if status == "resolved":
        handoff.resolved_at = datetime.now(tz=None)
    db.commit()
    return True


def list_customers(
    db: Session,
    workspace_id,
    page: int = 1,
    page_size: int = 20,
) -> dict:
    query = db.query(CustomerProfile).filter(CustomerProfile.workspace_id == workspace_id)
    total = query.count()
    offset = (page - 1) * page_size
    customers = (
        query.order_by(CustomerProfile.last_seen_at.desc())
        .offset(offset).limit(page_size).all()
    )

    return {
        "items": [
            {
                "id": c.id,
                "external_id": c.external_id,
                "name": c.name,
                "email": c.email,
                "company": c.company,
                "customer_tier": c.customer_tier,
                "sentiment_score": c.sentiment_score,
                "total_conversations": c.total_conversations,
                "unresolved_issues": c.unresolved_issues,
                "last_seen_at": c.last_seen_at,
                "created_at": c.created_at,
            }
            for c in customers
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


def get_customer_profile(db: Session, customer_id, workspace_id) -> dict | None:
    customer = db.query(CustomerProfile).filter(
        CustomerProfile.id == customer_id,
        CustomerProfile.workspace_id == workspace_id,
    ).first()
    if not customer:
        return None

    conversations = (
        db.query(Conversation)
        .filter(Conversation.customer_id == customer.id)
        .order_by(Conversation.created_at.desc())
        .all()
    )

    return {
        "profile": {
            "id": customer.id,
            "external_id": customer.external_id,
            "name": customer.name,
            "email": customer.email,
            "company": customer.company,
            "customer_tier": customer.customer_tier,
            "sentiment_score": customer.sentiment_score,
            "total_conversations": customer.total_conversations,
            "unresolved_issues": customer.unresolved_issues,
            "last_seen_at": customer.last_seen_at,
            "created_at": customer.created_at,
        },
        "timeline": [
            {
                "conversation_id": c.id,
                "channel": c.channel,
                "status": c.status,
                "subject": c.subject,
                "summary": c.resolution_summary,
                "created_at": c.created_at,
            }
            for c in conversations
        ],
    }
