"""V7 tool execution engine: validates parameters, executes tool handlers,
and logs results to tool_executions and action_logs."""
import json
import time
import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.models import ActionLog, Ticket, Tool, ToolExecution

# ---------------------------------------------------------------------------
# Mock tool handler implementations
# ---------------------------------------------------------------------------


def _handle_create_ticket(db: Session, workspace_id, params: dict) -> dict:
    ticket_id = f"TICKET-{uuid.uuid4().hex[:8].upper()}"
    now = datetime.now(tz=None)
    ticket = Ticket(
        id=ticket_id,
        workspace_id=workspace_id,
        title=params.get("title", "Untitled"),
        body=params.get("body", ""),
        product_area=params.get("product_area", "other"),
        issue_type=params.get("issue_type", "other"),
        priority=params.get("priority", "medium"),
        customer_tier="free",
        status="open",
        created_at=now,
        inserted_at=now,
        updated_at=now,
    )
    db.add(ticket)
    db.flush()
    return {"ticket_id": ticket_id, "status": "open", "message": f"Ticket {ticket_id} created"}


def _handle_update_ticket_status(db: Session, workspace_id, params: dict) -> dict:
    ticket_id = params["ticket_id"]
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        return {"error": f"Ticket {ticket_id} not found"}
    ticket.status = params["status"]
    if params.get("resolution"):
        ticket.resolution = params["resolution"]
    if params["status"] == "resolved":
        ticket.resolved_at = datetime.now(tz=None)
    db.flush()
    return {
        "ticket_id": ticket_id,
        "status": ticket.status,
        "message": f"Ticket {ticket_id} updated to {params['status']}",
    }


def _handle_lookup_customer(db: Session, workspace_id, params: dict) -> dict:
    from app.models.models import CustomerProfile

    email = params.get("email")
    name = params.get("name")
    query = db.query(CustomerProfile).filter(CustomerProfile.workspace_id == workspace_id)
    if email:
        query = query.filter(CustomerProfile.email == email)
    elif name:
        query = query.filter(CustomerProfile.name.ilike(f"%{name}%"))
    else:
        return {"error": "Provide email or name"}
    customers = query.limit(5).all()
    return {
        "customers": [
            {
                "id": str(c.id),
                "name": c.name,
                "email": c.email,
                "tier": c.customer_tier,
                "total_conversations": c.total_conversations,
                "unresolved_issues": c.unresolved_issues,
            }
            for c in customers
        ],
        "count": len(customers),
    }


def _handle_search_knowledge_base(db: Session, workspace_id, params: dict) -> dict:
    from app.models.models import KbArticle

    query_text = params["query"].lower()
    articles = (
        db.query(KbArticle)
        .filter(KbArticle.workspace_id == workspace_id)
        .all()
    )
    matches = []
    for a in articles:
        if (
            query_text in (a.title or "").lower()
            or query_text in (a.summary or "").lower()
            or query_text in (a.resolution_steps or "").lower()
        ):
            matches.append({
                "id": str(a.id),
                "title": a.title,
                "product_area": a.product_area,
                "issue_type": a.issue_type,
                "summary": a.summary[:200] if a.summary else "",
            })
    return {"articles": matches[:5], "count": len(matches)}


def _handle_check_sla_status(db: Session, workspace_id, params: dict) -> dict:
    from app.services.sla import compute_sla_risks

    risks = compute_sla_risks(db, workspace_id)
    ticket_id = params.get("ticket_id")
    if ticket_id:
        risks = [r for r in risks if r["ticket_id"] == ticket_id]
    return {
        "risks": risks[:10],
        "total_at_risk": len(risks),
        "breached_count": sum(1 for r in risks if r.get("breached")),
    }


def _handle_list_handoffs(db: Session, workspace_id, params: dict) -> dict:
    from app.models.models import HumanHandoff

    query = db.query(HumanHandoff).filter(HumanHandoff.workspace_id == workspace_id)
    status = params.get("status")
    if status:
        query = query.filter(HumanHandoff.status == status)
    handoffs = query.order_by(HumanHandoff.created_at.desc()).limit(20).all()
    return {
        "handoffs": [
            {
                "id": str(h.id),
                "trigger_reason": h.trigger_reason,
                "summary": h.summary[:200],
                "status": h.status,
                "likely_intent": h.likely_intent,
            }
            for h in handoffs
        ],
        "count": len(handoffs),
    }


HANDLER_MAP = {
    "create_ticket": _handle_create_ticket,
    "update_ticket_status": _handle_update_ticket_status,
    "lookup_customer": _handle_lookup_customer,
    "search_knowledge_base": _handle_search_knowledge_base,
    "check_sla_status": _handle_check_sla_status,
    "list_handoffs": _handle_list_handoffs,
}


# ---------------------------------------------------------------------------
# Execution engine
# ---------------------------------------------------------------------------


def execute_tool(
    db: Session,
    workspace_id,
    tool: Tool,
    parameters: dict,
    conversation_id=None,
    triggered_by: str = "ai",
) -> ToolExecution:
    """Execute a tool and record the execution + action log."""
    execution = ToolExecution(
        id=uuid.uuid4(),
        tool_id=tool.id,
        workspace_id=workspace_id,
        input_json=json.dumps(parameters),
        status="running",
        conversation_id=conversation_id,
        triggered_by=triggered_by,
    )
    db.add(execution)
    db.flush()

    handler_fn = HANDLER_MAP.get(tool.handler)
    if not handler_fn:
        execution.status = "failed"
        execution.error = f"Unknown handler: {tool.handler}"
        db.flush()
        return execution

    start = time.monotonic()
    try:
        result = handler_fn(db, workspace_id, parameters)
        elapsed = int((time.monotonic() - start) * 1000)
        execution.output_json = json.dumps(result)
        execution.status = "succeeded"
        execution.latency_ms = elapsed
    except Exception as exc:
        elapsed = int((time.monotonic() - start) * 1000)
        execution.status = "failed"
        execution.error = str(exc)
        execution.latency_ms = elapsed

    db.flush()

    action_log = ActionLog(
        id=uuid.uuid4(),
        workspace_id=workspace_id,
        action_type=f"tool.{tool.slug}",
        resource_type="tool_execution",
        resource_id=str(execution.id),
        tool_execution_id=execution.id,
        detail=json.dumps({
            "tool_name": tool.name,
            "status": execution.status,
            "triggered_by": triggered_by,
        }),
        actor="ai_agent" if triggered_by == "ai" else "user",
    )
    db.add(action_log)
    db.flush()

    return execution
