"""V8 intelligence API: performance metrics, KB suggestions, copilot
suggestions, feedback summary."""
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_workspace
from app.core.database import get_db
from app.models.models import Workspace
from app.schemas.intelligence import (
    ConversationSummaryListResponse,
    ConversationSummaryResponse,
    CopilotSuggestionListResponse,
    CopilotSuggestionResponse,
    CopilotSuggestionUpdateRequest,
    FeedbackSummaryResponse,
    KbSuggestionListResponse,
    KbSuggestionResponse,
    KbSuggestionUpdateRequest,
    PerformanceMetricsResponse,
    ToolUsageStats,
)
from app.services import intelligence as intel_svc

router = APIRouter()


@router.get("/performance", response_model=PerformanceMetricsResponse)
def get_performance(
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db),
) -> PerformanceMetricsResponse:
    metrics = intel_svc.compute_performance_metrics(db, workspace.id)
    return PerformanceMetricsResponse(
        total_conversations=metrics["total_conversations"],
        resolved_conversations=metrics["resolved_conversations"],
        ai_contained=metrics["ai_contained"],
        human_escalated=metrics["human_escalated"],
        containment_rate=metrics["containment_rate"],
        average_resolution_time_seconds=metrics["average_resolution_time_seconds"],
        total_tool_executions=metrics["total_tool_executions"],
        tool_success_rate=metrics["tool_success_rate"],
        tool_usage=[ToolUsageStats(**t) for t in metrics["tool_usage"]],
        sentiment_distribution=metrics["sentiment_distribution"],
        top_escalation_reasons=metrics["top_escalation_reasons"],
    )


@router.get("/summaries", response_model=ConversationSummaryListResponse)
def list_summaries(
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db),
) -> ConversationSummaryListResponse:
    items = intel_svc.list_summaries(db, workspace.id)
    return ConversationSummaryListResponse(
        items=[ConversationSummaryResponse(**i) for i in items],
        total=len(items),
    )


@router.post("/summaries/{conversation_id}/generate")
def generate_summary(
    conversation_id: str,
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db),
) -> ConversationSummaryResponse:
    result = intel_svc.generate_conversation_summary(
        db, uuid.UUID(conversation_id), workspace.id,
    )
    if not result:
        raise HTTPException(status_code=400, detail="Cannot generate summary")
    db.commit()
    return ConversationSummaryResponse(**result)


@router.get("/kb-suggestions", response_model=KbSuggestionListResponse)
def list_kb_suggestions(
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db),
) -> KbSuggestionListResponse:
    items = intel_svc.list_kb_suggestions(db, workspace.id)
    return KbSuggestionListResponse(
        items=[KbSuggestionResponse(**i) for i in items],
        total=len(items),
    )


@router.post("/kb-suggestions/detect")
def detect_kb_suggestions(
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db),
) -> KbSuggestionListResponse:
    items = intel_svc.detect_kb_suggestions(db, workspace.id)
    db.commit()
    return KbSuggestionListResponse(
        items=[KbSuggestionResponse(**i) for i in items],
        total=len(items),
    )


@router.put("/kb-suggestions/{suggestion_id}", response_model=KbSuggestionResponse)
def update_kb_suggestion(
    suggestion_id: str,
    body: KbSuggestionUpdateRequest,
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db),
) -> KbSuggestionResponse:
    ok = intel_svc.update_kb_suggestion(
        db, uuid.UUID(suggestion_id), body.status, workspace.id,
    )
    if not ok:
        raise HTTPException(status_code=404, detail="Suggestion not found")
    db.commit()
    items = intel_svc.list_kb_suggestions(db, workspace.id)
    updated = next((i for i in items if i["id"] == suggestion_id), None)
    if not updated:
        raise HTTPException(status_code=404, detail="Suggestion not found")
    return KbSuggestionResponse(**updated)


@router.get("/copilot", response_model=CopilotSuggestionListResponse)
def list_copilot(
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db),
) -> CopilotSuggestionListResponse:
    items = intel_svc.list_copilot_suggestions(db, workspace.id)
    return CopilotSuggestionListResponse(
        items=[CopilotSuggestionResponse(**i) for i in items],
        total=len(items),
    )


@router.post("/copilot/generate")
def generate_copilot(
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db),
) -> CopilotSuggestionListResponse:
    items = intel_svc.generate_copilot_suggestions(db, workspace.id)
    db.commit()
    return CopilotSuggestionListResponse(
        items=[CopilotSuggestionResponse(**i) for i in items],
        total=len(items),
    )


@router.put("/copilot/{suggestion_id}", response_model=CopilotSuggestionResponse)
def update_copilot(
    suggestion_id: str,
    body: CopilotSuggestionUpdateRequest,
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db),
) -> CopilotSuggestionResponse:
    ok = intel_svc.update_copilot_suggestion(
        db, uuid.UUID(suggestion_id), body.status, workspace.id,
    )
    if not ok:
        raise HTTPException(status_code=404, detail="Suggestion not found")
    db.commit()
    items = intel_svc.list_copilot_suggestions(db, workspace.id)
    updated = next((i for i in items if i["id"] == suggestion_id), None)
    if not updated:
        raise HTTPException(status_code=404, detail="Suggestion not found")
    return CopilotSuggestionResponse(**updated)


@router.get("/feedback-summary", response_model=FeedbackSummaryResponse)
def get_feedback_summary(
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db),
) -> FeedbackSummaryResponse:
    result = intel_svc.compute_feedback_summary(db, workspace.id)
    return FeedbackSummaryResponse(**result)
