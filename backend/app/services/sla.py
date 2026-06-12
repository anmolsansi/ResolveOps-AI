"""SLA risk detection for open tickets.

Combines time-to-SLA-deadline with priority and customer-tier weighting into a
single risk score. Deterministic given a reference ``now``.
"""
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.models import Ticket

CLOSED_STATUSES = {"resolved", "closed", "done"}

SLA_HOURS = {"critical": 4, "high": 8, "medium": 24, "low": 72}
DEFAULT_SLA_HOURS = 24

PRIORITY_WEIGHT = {"critical": 1.0, "high": 0.8, "medium": 0.5, "low": 0.3}
TIER_WEIGHT = {"enterprise": 1.0, "pro": 0.7, "free": 0.4}


def _level(score: float) -> str:
    if score >= 0.7:
        return "high"
    if score >= 0.4:
        return "medium"
    return "low"


def detect_sla_risks(db: Session, now: datetime | None = None, workspace_id=None) -> list[dict]:
    now = now or datetime.now(tz=None)
    risks: list[dict] = []

    query = db.query(Ticket)
    if workspace_id is not None:
        query = query.filter(Ticket.workspace_id == workspace_id)

    for t in query.all():
        if t.status.lower() in CLOSED_STATUSES or t.resolved_at is not None:
            continue
        if t.created_at is None:
            continue

        age_hours = max(0.0, (now - t.created_at).total_seconds() / 3600)
        sla_hours = SLA_HOURS.get(t.priority.lower(), DEFAULT_SLA_HOURS)
        breached = age_hours > sla_hours
        due_in_hours = round(sla_hours - age_hours, 1)

        time_factor = min(age_hours / sla_hours, 1.5) / 1.5 if sla_hours else 1.0
        pr = PRIORITY_WEIGHT.get(t.priority.lower(), 0.5)
        tw = TIER_WEIGHT.get(t.customer_tier.lower(), 0.5)
        score = round(min(1.0, 0.6 * time_factor + 0.25 * pr + 0.15 * tw), 4)

        if breached:
            reason = f"Past {sla_hours}h SLA by {round(age_hours - sla_hours, 1)}h"
        else:
            reason = f"{due_in_hours}h until {sla_hours}h SLA deadline"

        risks.append(
            {
                "ticket_id": t.id,
                "title": t.title,
                "product_area": t.product_area,
                "priority": t.priority,
                "customer_tier": t.customer_tier,
                "status": t.status,
                "hours_open": round(age_hours, 1),
                "sla_hours": sla_hours,
                "due_in_hours": due_in_hours,
                "breached": breached,
                "risk_score": score,
                "risk_level": _level(score),
                "reason": reason,
            }
        )

    risks.sort(key=lambda r: r["risk_score"], reverse=True)
    return risks
