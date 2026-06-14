"""V7 tool API: endpoints for managing tools, executing them, and viewing
action logs."""
import json
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_workspace
from app.core.database import get_db
from app.models.models import ActionLog, Tool, ToolExecution, Workspace
from app.schemas.tools import (
    ActionLogListResponse,
    ActionLogResponse,
    ToolExecuteRequest,
    ToolExecutionListResponse,
    ToolExecutionResponse,
    ToolListResponse,
    ToolSummary,
    ToolUpdateRequest,
)
from app.services import tool_registry as reg_svc
from app.services.tool_execution import execute_tool

router = APIRouter()


def _tool_to_summary(tool: Tool) -> ToolSummary:
    return ToolSummary(
        id=str(tool.id),
        name=tool.name,
        slug=tool.slug,
        description=tool.description,
        handler=tool.handler,
        enabled=tool.enabled,
        category=tool.category,
        parameters_schema=json.loads(tool.parameters_schema_json),
        created_at=tool.created_at.isoformat() if tool.created_at else "",
    )


def _exec_to_response(e: ToolExecution, tool_name: str) -> ToolExecutionResponse:
    return ToolExecutionResponse(
        id=str(e.id),
        tool_id=str(e.tool_id),
        tool_name=tool_name,
        input=json.loads(e.input_json),
        output=json.loads(e.output_json) if e.output_json else None,
        status=e.status,
        error=e.error,
        latency_ms=e.latency_ms,
        triggered_by=e.triggered_by,
        created_at=e.created_at.isoformat() if e.created_at else "",
    )


# --- Static paths (must come before /{tool_id}) ---


@router.get("", response_model=ToolListResponse)
def list_tools(
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db),
) -> ToolListResponse:
    reg_svc.upsert_builtin_tools(db, workspace.id)
    db.commit()
    tools = reg_svc.list_tools(db, workspace.id)
    return ToolListResponse(
        items=[_tool_to_summary(t) for t in tools],
        total=len(tools),
    )


@router.get("/executions", response_model=ToolExecutionListResponse)
def list_executions(
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db),
) -> ToolExecutionListResponse:
    execs = (
        db.query(ToolExecution)
        .filter(ToolExecution.workspace_id == workspace.id)
        .order_by(ToolExecution.created_at.desc())
        .limit(100)
        .all()
    )
    items = []
    for e in execs:
        tool = db.query(Tool).filter(Tool.id == e.tool_id).first()
        items.append(_exec_to_response(e, tool.name if tool else "unknown"))
    return ToolExecutionListResponse(items=items, total=len(items))


@router.get("/action-logs", response_model=ActionLogListResponse)
def list_action_logs(
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db),
) -> ActionLogListResponse:
    logs = (
        db.query(ActionLog)
        .filter(ActionLog.workspace_id == workspace.id)
        .order_by(ActionLog.created_at.desc())
        .limit(100)
        .all()
    )
    items = [
        ActionLogResponse(
            id=str(log_entry.id),
            action_type=log_entry.action_type,
            resource_type=log_entry.resource_type,
            resource_id=log_entry.resource_id,
            tool_execution_id=(
                str(log_entry.tool_execution_id) if log_entry.tool_execution_id else None
            ),
            detail=log_entry.detail,
            actor=log_entry.actor,
            created_at=log_entry.created_at.isoformat() if log_entry.created_at else "",
        )
        for log_entry in logs
    ]
    return ActionLogListResponse(items=items, total=len(items))


# --- Dynamic paths ---


@router.get("/{tool_id}", response_model=ToolSummary)
def get_tool(
    tool_id: str,
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db),
) -> ToolSummary:
    reg_svc.upsert_builtin_tools(db, workspace.id)
    db.commit()
    tool = reg_svc.get_tool(db, workspace.id, uuid.UUID(tool_id))
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    return _tool_to_summary(tool)


@router.put("/{tool_id}", response_model=ToolSummary)
def update_tool(
    tool_id: str,
    body: ToolUpdateRequest,
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db),
) -> ToolSummary:
    tool = reg_svc.get_tool(db, workspace.id, uuid.UUID(tool_id))
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    if body.enabled is not None:
        tool.enabled = body.enabled
    if body.description is not None:
        tool.description = body.description
    db.commit()
    db.refresh(tool)
    return _tool_to_summary(tool)


@router.post("/{tool_id}/execute", response_model=ToolExecutionResponse)
def execute_tool_endpoint(
    tool_id: str,
    body: ToolExecuteRequest,
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db),
) -> ToolExecutionResponse:
    reg_svc.upsert_builtin_tools(db, workspace.id)
    db.commit()
    tool = reg_svc.get_tool(db, workspace.id, uuid.UUID(tool_id))
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    if not tool.enabled:
        raise HTTPException(status_code=400, detail="Tool is disabled")

    conversation_id = uuid.UUID(body.conversation_id) if body.conversation_id else None
    execution = execute_tool(
        db, workspace.id, tool, body.parameters,
        conversation_id=conversation_id, triggered_by="user",
    )
    db.commit()
    db.refresh(execution)

    return _exec_to_response(execution, tool.name)
