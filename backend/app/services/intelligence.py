"""V8 intelligence service: computes agent performance metrics, generates
KB suggestions from conversation patterns, and provides copilot suggestions."""
import json
import uuid
from collections import Counter

from sqlalchemy.orm import Session

from app.models.models import (
    Conversation,
    ConversationMessage,
    ConversationSummaryModel,
    CopilotSuggestion,
    KbArticle,
    KbSuggestion,
    ResolutionOutcome,
    ToolExecution,
)

# ---------------------------------------------------------------------------
# Performance metrics
# ---------------------------------------------------------------------------


def compute_performance_metrics(db: Session, workspace_id) -> dict:
    """Compute AI agent KPIs for the workspace."""
    total = db.query(Conversation).filter(
        Conversation.workspace_id == workspace_id,
    ).count()

    resolved = db.query(ResolutionOutcome).filter(
        ResolutionOutcome.workspace_id == workspace_id,
    ).count()

    ai_contained = db.query(ResolutionOutcome).filter(
        ResolutionOutcome.workspace_id == workspace_id,
        ResolutionOutcome.outcome == "ai_contained",
    ).count()

    human_escalated = db.query(ResolutionOutcome).filter(
        ResolutionOutcome.workspace_id == workspace_id,
        ResolutionOutcome.outcome == "human_escalated",
    ).count()

    containment_rate = (ai_contained / resolved * 100) if resolved > 0 else 0.0

    avg_resolution_time = None
    resolutions = db.query(ResolutionOutcome).filter(
        ResolutionOutcome.workspace_id == workspace_id,
        ResolutionOutcome.time_to_resolution_seconds.isnot(None),
    ).all()
    if resolutions:
        times = [r.time_to_resolution_seconds for r in resolutions if r.time_to_resolution_seconds]
        if times:
            avg_resolution_time = sum(times) / len(times)

    # Tool usage stats
    tool_execs = db.query(ToolExecution).filter(
        ToolExecution.workspace_id == workspace_id,
    ).all()
    tool_stats: dict[str, dict] = {}
    for te in tool_execs:
        db.query(ToolExecution).filter(ToolExecution.id == te.id).first()
        key = str(te.tool_id)
        if key not in tool_stats:
            tool_stats[key] = {"total": 0, "success": 0, "failure": 0, "latencies": []}
        tool_stats[key]["total"] += 1
        if te.status == "succeeded":
            tool_stats[key]["success"] += 1
        elif te.status == "failed":
            tool_stats[key]["failure"] += 1
        if te.latency_ms is not None:
            tool_stats[key]["latencies"].append(te.latency_ms)

    from app.models.models import Tool

    tool_usage = []
    for tool_id_str, stats in tool_stats.items():
        tool_obj = db.query(Tool).filter(Tool.id == uuid.UUID(tool_id_str)).first()
        avg_lat = sum(stats["latencies"]) / len(stats["latencies"]) if stats["latencies"] else 0.0
        tool_usage.append({
            "tool_name": tool_obj.name if tool_obj else "unknown",
            "slug": tool_obj.slug if tool_obj else "unknown",
            "total_executions": stats["total"],
            "success_count": stats["success"],
            "failure_count": stats["failure"],
            "average_latency_ms": round(avg_lat, 1),
        })

    total_tool_execs = len(tool_execs)
    successful_tool_execs = sum(
        1 for te in tool_execs if te.status == "succeeded"
    )
    tool_success_rate = (
        successful_tool_execs / total_tool_execs * 100
    ) if total_tool_execs > 0 else 0.0

    # Sentiment distribution
    convos = db.query(Conversation).filter(
        Conversation.workspace_id == workspace_id,
    ).all()
    sentiment_dist = Counter(c.sentiment for c in convos if c.sentiment)

    # Top escalation reasons
    handoffs = db.query(Conversation).filter(
        Conversation.workspace_id == workspace_id,
        Conversation.status == "escalated",
    ).all()
    escalation_reasons = Counter()
    for c in handoffs:
        if c.sentiment:
            escalation_reasons[c.sentiment] += 1
    top_escalations = [
        {"reason": r, "count": cnt}
        for r, cnt in escalation_reasons.most_common(5)
    ]

    return {
        "total_conversations": total,
        "resolved_conversations": resolved,
        "ai_contained": ai_contained,
        "human_escalated": human_escalated,
        "containment_rate": round(containment_rate, 1),
        "average_resolution_time_seconds": (
            round(avg_resolution_time, 1) if avg_resolution_time else None
        ),
        "total_tool_executions": total_tool_execs,
        "tool_success_rate": round(tool_success_rate, 1),
        "tool_usage": tool_usage,
        "sentiment_distribution": dict(sentiment_dist),
        "top_escalation_reasons": top_escalations,
    }


# ---------------------------------------------------------------------------
# Conversation summaries
# ---------------------------------------------------------------------------


def generate_conversation_summary(
    db: Session, conversation_id, workspace_id,
) -> dict | None:
    """Generate a summary for a resolved conversation."""
    conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conv or conv.status != "resolved":
        return None

    existing = db.query(ConversationSummaryModel).filter(
        ConversationSummaryModel.conversation_id == conversation_id,
    ).first()
    if existing:
        return _summary_to_dict(existing)

    messages = (
        db.query(ConversationMessage)
        .filter(ConversationMessage.conversation_id == conversation_id)
        .order_by(ConversationMessage.created_at)
        .all()
    )
    if not messages:
        return None

    customer_msgs = [m.content for m in messages if m.role == "customer"]
    ai_msgs = [m.content for m in messages if m.role == "ai"]

    summary_parts = []
    if conv.subject:
        summary_parts.append(f"Topic: {conv.subject}")
    if customer_msgs:
        summary_parts.append(f"Customer asked about: {customer_msgs[0][:200]}")
    if ai_msgs:
        summary_parts.append(f"Resolution: {ai_msgs[-1][:300]}")

    summary = ". ".join(summary_parts) if summary_parts else "Conversation resolved."

    resolution_steps = None
    if len(ai_msgs) > 1:
        resolution_steps = "\n".join(
            f"{i+1}. {msg[:150]}" for i, msg in enumerate(ai_msgs[:5])
        )

    key_topics = []
    if conv.product_area:
        key_topics.append(conv.product_area)
    if conv.subject:
        words = conv.subject.split()[:5]
        key_topics.extend(words)

    cs = ConversationSummaryModel(
        id=uuid.uuid4(),
        conversation_id=conversation_id,
        workspace_id=workspace_id,
        summary=summary,
        resolution_steps=resolution_steps,
        key_topics_json=json.dumps(key_topics[:10]),
        sentiment_at_resolution=conv.sentiment,
    )
    db.add(cs)
    db.flush()

    return _summary_to_dict(cs)


def _summary_to_dict(cs: ConversationSummaryModel) -> dict:
    return {
        "id": str(cs.id),
        "conversation_id": str(cs.conversation_id),
        "summary": cs.summary,
        "resolution_steps": cs.resolution_steps,
        "key_topics": json.loads(cs.key_topics_json) if cs.key_topics_json else [],
        "sentiment_at_resolution": cs.sentiment_at_resolution,
        "created_at": cs.created_at.isoformat() if cs.created_at else "",
    }


def list_summaries(db: Session, workspace_id) -> list[dict]:
    items = (
        db.query(ConversationSummaryModel)
        .filter(ConversationSummaryModel.workspace_id == workspace_id)
        .order_by(ConversationSummaryModel.created_at.desc())
        .limit(50)
        .all()
    )
    return [_summary_to_dict(cs) for cs in items]


# ---------------------------------------------------------------------------
# KB suggestions
# ---------------------------------------------------------------------------


def detect_kb_suggestions(db: Session, workspace_id) -> list[dict]:
    """Analyze resolved conversations to suggest new KB articles."""

    resolved = (
        db.query(Conversation)
        .filter(
            Conversation.workspace_id == workspace_id,
            Conversation.status == "resolved",
        )
        .order_by(Conversation.created_at.desc())
        .limit(50)
        .all()
    )

    topic_groups: dict[str, list[str]] = {}
    for conv in resolved:
        key = f"{conv.product_area or 'general'}::{conv.subject or 'general'}"
        if key not in topic_groups:
            topic_groups[key] = []
        topic_groups[key].append(str(conv.id))

    existing_articles = db.query(KbArticle).filter(
        KbArticle.workspace_id == workspace_id,
    ).all()
    existing_titles = {a.title.lower() for a in existing_articles}

    suggestions = []
    for key, conv_ids in topic_groups.items():
        if len(conv_ids) < 2:
            continue
        product_area, subject = key.split("::", 1)
        title = f"How to: {subject[:200]}"
        if title.lower() in existing_titles:
            continue

        existing_sugg = db.query(KbSuggestion).filter(
            KbSuggestion.workspace_id == workspace_id,
            KbSuggestion.suggested_title == title,
        ).first()
        if existing_sugg:
            existing_sugg.occurrence_count = len(conv_ids)
            existing_sugg.source_conversation_ids_json = json.dumps(conv_ids)
            db.flush()
            suggestions.append(_suggestion_to_dict(existing_sugg))
            continue

        sugg = KbSuggestion(
            id=uuid.uuid4(),
            workspace_id=workspace_id,
            suggested_title=title,
            suggested_content=(
                f"Based on {len(conv_ids)} resolved conversations about "
                f"{subject[:100]}."
            ),
            product_area=product_area if product_area != "general" else None,
            issue_type=None,
            source_conversation_ids_json=json.dumps(conv_ids),
            occurrence_count=len(conv_ids),
            status="pending",
        )
        db.add(sugg)
        db.flush()
        suggestions.append(_suggestion_to_dict(sugg))

    return suggestions


def _suggestion_to_dict(s: KbSuggestion) -> dict:
    return {
        "id": str(s.id),
        "suggested_title": s.suggested_title,
        "suggested_content": s.suggested_content,
        "product_area": s.product_area,
        "issue_type": s.issue_type,
        "source_conversation_ids": (
            json.loads(s.source_conversation_ids_json)
            if s.source_conversation_ids_json else []
        ),
        "occurrence_count": s.occurrence_count,
        "status": s.status,
        "created_at": s.created_at.isoformat() if s.created_at else "",
    }


def list_kb_suggestions(db: Session, workspace_id) -> list[dict]:
    items = (
        db.query(KbSuggestion)
        .filter(KbSuggestion.workspace_id == workspace_id)
        .order_by(KbSuggestion.occurrence_count.desc())
        .limit(50)
        .all()
    )
    return [_suggestion_to_dict(s) for s in items]


def update_kb_suggestion(db: Session, suggestion_id, status: str, workspace_id) -> bool:
    s = db.query(KbSuggestion).filter(
        KbSuggestion.id == suggestion_id,
        KbSuggestion.workspace_id == workspace_id,
    ).first()
    if not s:
        return False
    s.status = status
    db.flush()
    return True


# ---------------------------------------------------------------------------
# Copilot suggestions
# ---------------------------------------------------------------------------


def generate_copilot_suggestions(
    db: Session, workspace_id, conversation_id=None,
) -> list[dict]:
    """Generate proactive suggestions for agents."""
    suggestions = []

    # 1. Check for pending handoffs
    from app.models.models import HumanHandoff

    pending_handoffs = db.query(HumanHandoff).filter(
        HumanHandoff.workspace_id == workspace_id,
        HumanHandoff.status == "pending",
    ).count()
    if pending_handoffs > 0:
        suggestions.append({
            "suggestion_type": "next_best_action",
            "title": f"{pending_handoffs} handoff(s) awaiting response",
            "content": (
                f"There are {pending_handoffs} customer handoffs pending. "
                "Review the handoff queue to prioritize urgent cases."
            ),
            "confidence": 0.9,
        })

    # 2. Suggest canned responses for common patterns
    recent_escalated = (
        db.query(Conversation)
        .filter(
            Conversation.workspace_id == workspace_id,
            Conversation.status == "escalated",
        )
        .order_by(Conversation.created_at.desc())
        .limit(5)
        .all()
    )
    if recent_escalated:
        subjects = [c.subject for c in recent_escalated if c.subject]
        if subjects:
            suggestions.append({
                "suggestion_type": "canned_response",
                "title": f"Common escalation pattern: {subjects[0][:80]}",
                "content": (
                    "Recent escalations share similar topics. Consider creating "
                    "a canned response for: " + "; ".join(subjects[:3])
                ),
                "confidence": 0.7,
            })

    # 3. Related tickets for active conversation
    if conversation_id:
        conv = db.query(Conversation).filter(
            Conversation.id == conversation_id,
        ).first()
        if conv and conv.product_area:
            related = (
                db.query(Conversation)
                .filter(
                    Conversation.workspace_id == workspace_id,
                    Conversation.product_area == conv.product_area,
                    Conversation.id != conversation_id,
                    Conversation.status.in_(["open", "waiting_for_customer"]),
                )
                .limit(3)
                .all()
            )
            if related:
                suggestions.append({
                    "suggestion_type": "related_ticket",
                    "title": f"{len(related)} related open ticket(s)",
                    "content": (
                        "Related tickets in the same product area: "
                        + "; ".join((r.subject or r.id.hex[:8]) for r in related)
                    ),
                    "confidence": 0.6,
                })

    # 4. Escalation tips
    if recent_escalated:
        from collections import Counter
        reasons = Counter(c.sentiment for c in recent_escalated if c.sentiment)
        top_reason = reasons.most_common(1)
        if top_reason:
            suggestions.append({
                "suggestion_type": "escalation_tip",
                "title": f"Most common escalation trigger: {top_reason[0][0]}",
                "content": (
                    f"The most frequent escalation trigger is '{top_reason[0][0]}' "
                    f"({top_reason[0][1]} occurrences). "
                    "Consider addressing this pattern proactively."
                ),
                "confidence": 0.8,
            })

    # Store suggestions
    stored = []
    for s in suggestions:
        cs = CopilotSuggestion(
            id=uuid.uuid4(),
            workspace_id=workspace_id,
            conversation_id=conversation_id,
            suggestion_type=s["suggestion_type"],
            title=s["title"],
            content=s["content"],
            confidence=s["confidence"],
            status="pending",
        )
        db.add(cs)
        db.flush()
        stored.append(_copilot_to_dict(cs))

    return stored


def _copilot_to_dict(cs: CopilotSuggestion) -> dict:
    return {
        "id": str(cs.id),
        "suggestion_type": cs.suggestion_type,
        "title": cs.title,
        "content": cs.content,
        "confidence": cs.confidence,
        "status": cs.status,
        "conversation_id": str(cs.conversation_id) if cs.conversation_id else None,
        "created_at": cs.created_at.isoformat() if cs.created_at else "",
    }


def list_copilot_suggestions(db: Session, workspace_id) -> list[dict]:
    items = (
        db.query(CopilotSuggestion)
        .filter(CopilotSuggestion.workspace_id == workspace_id)
        .order_by(CopilotSuggestion.created_at.desc())
        .limit(50)
        .all()
    )
    return [_copilot_to_dict(cs) for cs in items]


def update_copilot_suggestion(
    db: Session, suggestion_id, status: str, workspace_id,
) -> bool:
    cs = db.query(CopilotSuggestion).filter(
        CopilotSuggestion.id == suggestion_id,
        CopilotSuggestion.workspace_id == workspace_id,
    ).first()
    if not cs:
        return False
    cs.status = status
    db.flush()
    return True


# ---------------------------------------------------------------------------
# Feedback summary
# ---------------------------------------------------------------------------


def compute_feedback_summary(db: Session, workspace_id) -> dict:
    """Aggregate feedback signals from conversations."""
    convos = db.query(Conversation).filter(
        Conversation.workspace_id == workspace_id,
    ).all()

    resolutions = db.query(ResolutionOutcome).filter(
        ResolutionOutcome.workspace_id == workspace_id,
    ).all()

    total_feedback = len(resolutions)
    positive = sum(1 for r in resolutions if r.outcome == "ai_contained")
    negative = sum(1 for r in resolutions if r.outcome in ("human_escalated", "bad_answer"))
    satisfaction_rate = (positive / total_feedback * 100) if total_feedback > 0 else 0.0

    # Top issues from escalated conversations
    escalated = [c for c in convos if c.status == "escalated"]
    issue_counter = Counter()
    for c in escalated:
        issue_counter[c.sentiment or "unknown"] += 1
    top_issues = [
        {"reason": r, "count": cnt}
        for r, cnt in issue_counter.most_common(5)
    ]

    improvement_areas = []
    if negative > 0:
        improvement_areas.append(
            f"{negative} conversations required human escalation"
        )
    low_conf_count = sum(
        1 for r in resolutions
        if r.confidence_at_resolution < 0.5
    )
    if low_conf_count > 0:
        improvement_areas.append(
            f"{low_conf_count} resolutions had low confidence (< 50%)"
        )
    missing_kb = sum(
        1 for r in resolutions if r.outcome == "missing_knowledge"
    )
    if missing_kb > 0:
        improvement_areas.append(
            f"{missing_kb} resolutions flagged as missing knowledge"
        )

    return {
        "total_feedback": total_feedback,
        "positive_count": positive,
        "negative_count": negative,
        "satisfaction_rate": round(satisfaction_rate, 1),
        "top_issues": top_issues,
        "improvement_areas": improvement_areas,
    }
