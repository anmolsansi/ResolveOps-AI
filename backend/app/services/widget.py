"""V6 widget service: processes customer-facing chat messages through the RAG
pipeline and manages conversation sessions. V7 adds automatic tool execution."""
import json
from datetime import datetime

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.models import (
    Conversation,
    ConversationMessage,
    CustomerProfile,
    HumanHandoff,
)
from app.services.prompts import get_active_prompt_text
from app.services.providers.factory import get_answer_provider
from app.services.retrieval import compute_confidence, retrieve_chunks
from app.services.tool_execution import execute_tool
from app.services.tool_registry import get_tool_by_slug, upsert_builtin_tools

_ANSWER_THRESHOLD = 0.6


def detect_sentiment(text: str) -> str:
    lower = text.lower()
    for kw in settings.escalation_sentiment_keywords:
        if kw in lower:
            return "angry"
    negative = ["frustrated", "annoyed", "disappointed", "upset", "unhappy", "bad", "broken"]
    if any(kw in lower for kw in negative):
        return "negative"
    positive = ["thanks", "great", "perfect", "awesome", "love", "appreciate"]
    if any(kw in lower for kw in positive):
        return "positive"
    return "neutral"


def should_escalate(
    confidence: float, sentiment: str, message_text: str,
) -> tuple[bool, str | None]:
    if confidence < settings.escalation_confidence_threshold:
        return True, "low_confidence"
    if sentiment == "angry":
        return True, "angry_sentiment"
    lower = message_text.lower()
    for kw in settings.policy_sensitive_keywords:
        if kw in lower:
            return True, "policy_sensitive"
    return False, None


def _build_customer_snapshot(customer: CustomerProfile) -> str:
    return json.dumps({
        "id": str(customer.id),
        "name": customer.name,
        "email": customer.email,
        "company": customer.company,
        "tier": customer.customer_tier,
        "total_conversations": customer.total_conversations,
        "unresolved_issues": customer.unresolved_issues,
    })


def create_or_find_customer(
    db: Session,
    email: str | None,
    name: str | None,
    workspace_id,
) -> CustomerProfile:
    if email:
        existing = db.query(CustomerProfile).filter(
            CustomerProfile.email == email,
            CustomerProfile.workspace_id == workspace_id,
        ).first()
        if existing:
            if name and not existing.name:
                existing.name = name
            existing.last_seen_at = datetime.now(tz=None)
            db.flush()
            return existing

    external_id = email or f"anon-{datetime.now(tz=None).strftime('%Y%m%d%H%M%S')}"
    customer = CustomerProfile(
        workspace_id=workspace_id,
        external_id=external_id,
        name=name,
        email=email,
        customer_tier="free",
    )
    db.add(customer)
    db.flush()
    return customer


def start_conversation(
    db: Session,
    customer: CustomerProfile,
    workspace,
    channel: str = "widget",
    subject: str | None = None,
) -> Conversation:
    conv = Conversation(
        workspace_id=workspace.id,
        customer_id=customer.id,
        channel=channel,
        status="open",
        subject=subject,
        sentiment="neutral",
    )
    db.add(conv)
    db.flush()

    customer.total_conversations += 1
    customer.last_seen_at = datetime.now(tz=None)
    db.flush()
    return conv


def process_widget_message(
    db: Session,
    message: str,
    conversation_id,
    customer_email: str | None,
    customer_name: str | None,
    workspace,
) -> dict:
    customer = create_or_find_customer(db, customer_email, customer_name, workspace.id)

    if conversation_id:
        conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if not conv:
            conv = start_conversation(db, customer, workspace)
    else:
        conv = start_conversation(db, customer, workspace)

    customer_msg = ConversationMessage(
        conversation_id=conv.id,
        role="customer",
        content=message,
    )
    db.add(customer_msg)
    db.flush()

    conv.last_message_at = datetime.now(tz=None)
    if not conv.subject:
        conv.subject = message[:200]
    db.flush()

    results = retrieve_chunks(db, message, top_k=settings.default_top_k, workspace_id=workspace.id)
    scores = [r["score"] for r in results]
    confidence = compute_confidence(scores)

    sentiment = detect_sentiment(message)
    conv.sentiment = sentiment

    is_fallback = confidence < settings.low_confidence_threshold or not results
    if is_fallback:
        answer = (
            "I don't have enough context to answer this question. "
            "I'm connecting you with a human support agent who can help."
        )
        citations: list[str] = []
    else:
        provider = get_answer_provider()
        contexts = [{"ticket_id": r["ticket_id"], "text": r["text"]} for r in results]
        system_prompt = get_active_prompt_text(db)
        answer = provider.generate_answer(message, contexts, system_prompt=system_prompt)
        citations = list(dict.fromkeys(r["ticket_id"] for r in results))

    escalate, trigger_reason = should_escalate(confidence, sentiment, message)

    ai_msg = ConversationMessage(
        conversation_id=conv.id,
        role="ai",
        content=answer,
        citations_json=json.dumps(citations) if citations else None,
        confidence=confidence,
        is_escalation_trigger=escalate,
    )
    db.add(ai_msg)

    if escalate:
        conv.status = "escalated"
        handoff = HumanHandoff(
            conversation_id=conv.id,
            workspace_id=workspace.id,
            trigger_reason=trigger_reason or "unknown",
            summary=f"Customer asked: {message[:500]}",
            likely_intent=_infer_intent(message),
            customer_profile_snapshot=_build_customer_snapshot(customer),
            cited_docs_json=json.dumps(citations) if citations else None,
            suggested_reply=answer if not is_fallback else None,
        )
        db.add(handoff)
    else:
        conv.status = "waiting_for_customer"

    db.commit()
    db.refresh(ai_msg)

    # V7: auto tool execution
    tool_results = _run_auto_tools(db, message, workspace, conv.id)
    db.commit()

    return {
        "answer": answer,
        "conversation_id": conv.id,
        "message_id": ai_msg.id,
        "citations": citations,
        "confidence": confidence,
        "is_fallback": is_fallback,
        "sentiment": sentiment,
        "should_escalate": escalate,
        "tool_results": tool_results,
    }


def _infer_intent(message: str) -> str:
    lower = message.lower()
    if any(kw in lower for kw in ["refund", "money back", "charge"]):
        return "billing_refund_request"
    if any(kw in lower for kw in ["cancel", "subscription", "unsubscribe"]):
        return "cancellation_request"
    if any(kw in lower for kw in ["bug", "error", "crash", "broken", "not working"]):
        return "bug_report"
    if any(kw in lower for kw in ["login", "password", "reset", "access"]):
        return "account_access_issue"
    return "general_inquiry"


# ---------------------------------------------------------------------------
# V7 — Auto tool detection and execution
# ---------------------------------------------------------------------------

_TOOL_INTENT_MAP = [
    {
        "keywords": ["ticket", "create ticket", "file a ticket", "open a ticket", "report issue"],
        "slug": "create_ticket",
        "param_extractor": "_extract_ticket_params",
    },
    {
        "keywords": ["my tickets", "check my ticket", "ticket status", "open tickets"],
        "slug": "lookup_customer",
        "param_extractor": "_extract_customer_lookup_params",
    },
    {
        "keywords": ["knowledge base", "kb article", "help doc", "documentation", "how to"],
        "slug": "search_knowledge_base",
        "param_extractor": "_extract_kb_params",
    },
    {
        "keywords": ["sla", "breach", "overdue", "aging ticket", "slipping"],
        "slug": "check_sla_status",
        "param_extractor": "_extract_sla_params",
    },
    {
        "keywords": ["handoff", "human agent", "talk to someone", "escalate", "real person"],
        "slug": "list_handoffs",
        "param_extractor": "_extract_handoff_params",
    },
]


def _extract_ticket_params(message: str) -> dict:
    return {
        "title": message[:200],
        "body": message,
        "product_area": "other",
        "issue_type": "other",
        "priority": "medium",
    }


def _extract_customer_lookup_params(message: str) -> dict:
    return {}


def _extract_kb_params(message: str) -> dict:
    return {"query": message}


def _extract_sla_params(message: str) -> dict:
    return {}


def _extract_handoff_params(message: str) -> dict:
    return {"status": "pending"}


def _detect_tool_intent(message: str) -> tuple[str | None, dict]:
    """Detect if a message should trigger a tool. Returns (tool_slug, params)."""
    lower = message.lower()
    for mapping in _TOOL_INTENT_MAP:
        if any(kw in lower for kw in mapping["keywords"]):
            extractor = globals()[mapping["param_extractor"]]
            return mapping["slug"], extractor(message)
    return None, {}


def _run_auto_tools(
    db: Session,
    message: str,
    workspace,
    conversation_id,
) -> list[dict]:
    """Attempt auto tool execution for the message. Returns list of tool results."""
    if not settings.tool_auto_register:
        return []

    upsert_builtin_tools(db, workspace.id)

    tool_slug, params = _detect_tool_intent(message)
    if not tool_slug:
        return []

    tool = get_tool_by_slug(db, workspace.id, tool_slug)
    if not tool or not tool.enabled:
        return []

    execution = execute_tool(
        db, workspace.id, tool, params,
        conversation_id=conversation_id, triggered_by="ai",
    )
    db.flush()

    result = {
        "tool_name": tool.name,
        "tool_slug": tool.slug,
        "status": execution.status,
        "output": json.loads(execution.output_json) if execution.output_json else None,
        "error": execution.error,
        "latency_ms": execution.latency_ms,
    }
    return [result]
