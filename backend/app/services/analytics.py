"""V10a analytics service: dashboard enhancements, agent performance, reports, exports."""
import csv
import io
import json
import uuid
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models.models import (
    Conversation,
    ExportJob,
    RagQuery,
    ResolutionOutcome,
    SavedReport,
    ToolExecution,
)


def _parse_time_range(time_range: str) -> datetime | None:
    """Convert time range string to cutoff datetime. None means all time."""
    now = datetime.utcnow()
    if time_range == "7d":
        return now - timedelta(days=7)
    if time_range == "30d":
        return now - timedelta(days=30)
    if time_range == "90d":
        return now - timedelta(days=90)
    return None


def get_dashboard_summary(db: Session, workspace_id, time_range: str = "all") -> dict:
    """Enhanced dashboard with time-range filtering."""
    cutoff = _parse_time_range(time_range)

    conv_q = db.query(Conversation).filter(Conversation.workspace_id == workspace_id)
    if cutoff:
        conv_q = conv_q.filter(Conversation.created_at >= cutoff)
    conversations = conv_q.all()

    total = len(conversations)
    resolved = sum(1 for c in conversations if c.status == "resolved")
    open_ = sum(1 for c in conversations if c.status in ("open", "waiting_for_customer"))
    ai_contained = sum(1 for c in conversations if c.ai_resolution_outcome == "contained")
    containment_rate = ai_contained / total if total > 0 else 0.0

    resolutions = db.query(ResolutionOutcome).join(Conversation).filter(
        Conversation.workspace_id == workspace_id,
    )
    if cutoff:
        resolutions = resolutions.filter(ResolutionOutcome.created_at >= cutoff)
    resolution_list = resolutions.all()
    avg_time = None
    times = [r.time_to_resolution_seconds for r in resolution_list if r.time_to_resolution_seconds]
    if times:
        avg_time = sum(times) / len(times)

    satisfactions = [r.customer_satisfaction for r in resolution_list if r.customer_satisfaction]
    avg_sat = sum(satisfactions) / len(satisfactions) if satisfactions else None

    rag_q = db.query(RagQuery).filter(RagQuery.workspace_id == workspace_id)
    if cutoff:
        rag_q = rag_q.filter(RagQuery.created_at >= cutoff)
    rag_list = rag_q.all()
    total_rag = len(rag_list)
    avg_conf = sum(r.confidence for r in rag_list) / total_rag if total_rag > 0 else 0.0

    tool_q = db.query(ToolExecution).join(Conversation).filter(
        Conversation.workspace_id == workspace_id,
    )
    if cutoff:
        tool_q = tool_q.filter(ToolExecution.created_at >= cutoff)
    tool_list = tool_q.all()
    total_tools = len(tool_list)
    tool_success = sum(1 for t in tool_list if t.status == "success")
    tool_rate = tool_success / total_tools if total_tools > 0 else 0.0

    trend = []
    if cutoff:
        days = (datetime.utcnow() - cutoff).days
        for i in range(min(days, 30)):
            day_start = cutoff + timedelta(days=i)
            day_end = day_start + timedelta(days=1)
            day_convs = sum(
                1 for c in conversations
                if c.created_at and day_start <= c.created_at < day_end
            )
            trend.append({"label": day_start.strftime("%m-%d"), "value": day_convs})
    else:
        trend = [{"label": "all", "value": total}]

    return {
        "total_conversations": total,
        "resolved_conversations": resolved,
        "open_conversations": open_,
        "containment_rate": round(containment_rate, 4),
        "avg_resolution_time_seconds": avg_time,
        "avg_satisfaction": round(avg_sat, 2) if avg_sat else None,
        "total_rag_queries": total_rag,
        "avg_confidence": round(avg_conf, 4),
        "total_tool_executions": total_tools,
        "tool_success_rate": round(tool_rate, 4),
        "sla_breach_count": 0,
        "trend": trend,
    }


def get_agent_performance(db: Session, workspace_id, time_range: str = "all") -> dict:
    """Per-agent performance metrics."""
    cutoff = _parse_time_range(time_range)

    conv_q = db.query(Conversation).filter(
        Conversation.workspace_id == workspace_id,
        Conversation.assigned_agent_id.isnot(None),
    )
    if cutoff:
        conv_q = conv_q.filter(Conversation.created_at >= cutoff)
    conversations = conv_q.all()

    agent_map: dict[str, dict] = {}
    for c in conversations:
        aid = str(c.assigned_agent_id)
        if aid not in agent_map:
            agent_map[aid] = {"handled": 0, "resolved": 0, "times": [], "satisfactions": []}
        agent_map[aid]["handled"] += 1
        if c.status == "resolved":
            agent_map[aid]["resolved"] += 1

    for rid, data in agent_map.items():
        resolutions = db.query(ResolutionOutcome).join(Conversation).filter(
            Conversation.assigned_agent_id == uuid.UUID(rid),
        )
        if cutoff:
            resolutions = resolutions.filter(ResolutionOutcome.created_at >= cutoff)
        for r in resolutions.all():
            if r.time_to_resolution_seconds:
                data["times"].append(r.time_to_resolution_seconds)
            if r.customer_satisfaction:
                data["satisfactions"].append(r.customer_satisfaction)

    items = []
    for uid, data in agent_map.items():
        avg_t = sum(data["times"]) / len(data["times"]) if data["times"] else None
        avg_s = (
            sum(data["satisfactions"]) / len(data["satisfactions"])
            if data["satisfactions"] else None
        )
        items.append({
            "user_id": uid,
            "email": "",
            "conversations_handled": data["handled"],
            "resolutions": data["resolved"],
            "avg_resolution_time_seconds": avg_t,
            "avg_satisfaction": round(avg_s, 2) if avg_s else None,
        })

    items.sort(key=lambda x: x["conversations_handled"], reverse=True)
    return {"items": items, "total": len(items)}


def create_saved_report(
    db: Session, workspace_id, name: str, report_type: str,
    filters: dict, created_by: str,
) -> dict:
    report = SavedReport(
        workspace_id=workspace_id,
        name=name,
        report_type=report_type,
        filters_json=json.dumps(filters),
        created_by=created_by,
    )
    db.add(report)
    db.flush()
    return _report_to_dict(report)


def list_saved_reports(db: Session, workspace_id) -> list[dict]:
    reports = db.query(SavedReport).filter(
        SavedReport.workspace_id == workspace_id,
    ).order_by(SavedReport.created_at.desc()).all()
    return [_report_to_dict(r) for r in reports]


def delete_saved_report(db: Session, report_id, workspace_id) -> bool:
    report = db.query(SavedReport).filter(
        SavedReport.id == report_id,
        SavedReport.workspace_id == workspace_id,
    ).first()
    if not report:
        return False
    db.delete(report)
    return True


def create_export_job(
    db: Session, workspace_id, report_type: str,
    filters: dict, created_by: str,
) -> dict:
    job = ExportJob(
        workspace_id=workspace_id,
        report_type=report_type,
        filters_json=json.dumps(filters),
        status="succeeded",
        row_count=0,
        created_by=created_by,
        completed_at=datetime.utcnow(),
    )
    db.add(job)
    db.flush()
    return _export_to_dict(job)


def list_export_jobs(db: Session, workspace_id) -> list[dict]:
    jobs = db.query(ExportJob).filter(
        ExportJob.workspace_id == workspace_id,
    ).order_by(ExportJob.created_at.desc()).all()
    return [_export_to_dict(j) for j in jobs]


def generate_csv_export(db: Session, export_job_id, workspace_id) -> str | None:
    job = db.query(ExportJob).filter(
        ExportJob.id == export_job_id,
        ExportJob.workspace_id == workspace_id,
    ).first()
    if not job:
        return None

    filters = json.loads(job.filters_json)
    cutoff = _parse_time_range(filters.get("time_range", "all"))

    conv_q = db.query(Conversation).filter(Conversation.workspace_id == workspace_id)
    if cutoff:
        conv_q = conv_q.filter(Conversation.created_at >= cutoff)
    conversations = conv_q.all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "id", "channel", "status", "subject",
        "product_area", "sentiment", "created_at",
    ])
    for c in conversations:
        writer.writerow([
            str(c.id), c.channel, c.status, c.subject or "",
            c.product_area or "", c.sentiment or "",
            c.created_at.isoformat() if c.created_at else "",
        ])

    job.status = "succeeded"
    job.row_count = len(conversations)
    job.completed_at = datetime.utcnow()
    return output.getvalue()


def _report_to_dict(report: SavedReport) -> dict:
    return {
        "id": str(report.id),
        "name": report.name,
        "report_type": report.report_type,
        "filters": json.loads(report.filters_json),
        "created_by": report.created_by,
        "created_at": report.created_at.isoformat() if report.created_at else "",
    }


def _export_to_dict(job: ExportJob) -> dict:
    return {
        "id": str(job.id),
        "report_type": job.report_type,
        "filters": json.loads(job.filters_json),
        "status": job.status,
        "row_count": job.row_count,
        "created_by": job.created_by,
        "created_at": job.created_at.isoformat() if job.created_at else "",
        "completed_at": job.completed_at.isoformat() if job.completed_at else None,
    }
