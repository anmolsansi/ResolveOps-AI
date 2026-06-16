"""V10a analytics API: dashboard, agent performance, reports, exports."""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_current_workspace
from app.core.database import get_db
from app.models.models import User, Workspace
from app.schemas.analytics import (
    AgentPerformanceResponse,
    DashboardSummaryResponse,
    ExportJobCreateRequest,
    ExportJobListResponse,
    ExportJobResponse,
    SavedReportCreateRequest,
    SavedReportListResponse,
    SavedReportResponse,
    TrendDataResponse,
)
from app.services import analytics as svc

router = APIRouter()


@router.get("/dashboard", response_model=DashboardSummaryResponse)
def dashboard_summary(
    time_range: str = "all",
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db),
) -> DashboardSummaryResponse:
    result = svc.get_dashboard_summary(db, workspace.id, time_range)
    return DashboardSummaryResponse(**result)


@router.get("/agent-performance", response_model=AgentPerformanceResponse)
def agent_performance(
    time_range: str = "all",
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db),
) -> AgentPerformanceResponse:
    result = svc.get_agent_performance(db, workspace.id, time_range)
    return AgentPerformanceResponse(**result)


@router.get("/trends", response_model=TrendDataResponse)
def trends(
    metric: str = "conversations",
    time_range: str = "30d",
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db),
) -> TrendDataResponse:
    summary = svc.get_dashboard_summary(db, workspace.id, time_range)
    return TrendDataResponse(
        metric=metric,
        data_points=summary.get("trend", []),
    )


@router.post("/reports", response_model=SavedReportResponse)
def create_report(
    body: SavedReportCreateRequest,
    workspace: Workspace = Depends(get_current_workspace),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SavedReportResponse:
    result = svc.create_saved_report(
        db, workspace.id, body.name, body.report_type, body.filters, user.email
    )
    db.commit()
    return SavedReportResponse(**result)


@router.get("/reports", response_model=SavedReportListResponse)
def list_reports(
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db),
) -> SavedReportListResponse:
    items = svc.list_saved_reports(db, workspace.id)
    return SavedReportListResponse(
        items=[SavedReportResponse(**i) for i in items], total=len(items)
    )


@router.delete("/reports/{report_id}")
def delete_report(
    report_id: str,
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db),
) -> dict:
    import uuid
    ok = svc.delete_saved_report(db, uuid.UUID(report_id), workspace.id)
    if not ok:
        raise HTTPException(status_code=404, detail="Report not found")
    db.commit()
    return {"ok": True}


@router.post("/export", response_model=ExportJobResponse)
def create_export(
    body: ExportJobCreateRequest,
    workspace: Workspace = Depends(get_current_workspace),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ExportJobResponse:
    result = svc.create_export_job(db, workspace.id, body.report_type, body.filters, user.email)
    db.commit()
    return ExportJobResponse(**result)


@router.get("/exports", response_model=ExportJobListResponse)
def list_exports(
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db),
) -> ExportJobListResponse:
    items = svc.list_export_jobs(db, workspace.id)
    return ExportJobListResponse(items=[ExportJobResponse(**i) for i in items], total=len(items))


@router.get("/exports/{job_id}/download")
def download_export(
    job_id: str,
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db),
) -> PlainTextResponse:
    import uuid
    csv_content = svc.generate_csv_export(db, uuid.UUID(job_id), workspace.id)
    if csv_content is None:
        raise HTTPException(status_code=404, detail="Export not found")
    db.commit()
    return PlainTextResponse(content=csv_content, media_type="text/csv")
