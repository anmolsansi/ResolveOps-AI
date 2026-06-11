import re
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.models import Membership, User, Workspace
from app.schemas.workspaces import (
    MemberAddRequest,
    MemberListResponse,
    MemberResponse,
    MemberRoleUpdate,
    WorkspaceCreate,
    WorkspaceListResponse,
    WorkspaceResponse,
)
from app.services.audit import record_audit

router = APIRouter()

VALID_ROLES = {"admin", "member", "viewer"}


def _slugify(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return slug or "workspace"


def _parse_uuid(value: str) -> uuid.UUID:
    try:
        return uuid.UUID(value)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid id")


def _require_workspace_admin(db: Session, workspace_id: uuid.UUID, user: User) -> None:
    if user.role == "admin":
        return
    membership = (
        db.query(Membership)
        .filter(Membership.workspace_id == workspace_id, Membership.user_id == user.id)
        .first()
    )
    if membership is None or membership.role != "admin":
        raise HTTPException(status_code=403, detail="Requires workspace admin role")


def _member_count(db: Session, workspace_id: uuid.UUID) -> int:
    return db.query(Membership).filter(Membership.workspace_id == workspace_id).count()


@router.post("", response_model=WorkspaceResponse)
def create_workspace(
    payload: WorkspaceCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> WorkspaceResponse:
    slug = _slugify(payload.slug or payload.name)
    if db.query(Workspace).filter(Workspace.slug == slug).first():
        raise HTTPException(status_code=409, detail=f"Workspace slug '{slug}' already exists")
    ws = Workspace(name=payload.name, slug=slug)
    db.add(ws)
    db.flush()
    # Creator becomes the workspace admin.
    db.add(Membership(workspace_id=ws.id, user_id=user.id, role="admin"))
    db.commit()
    db.refresh(ws)
    record_audit(
        db,
        actor_email=user.email,
        action="workspace.create",
        resource_type="workspace",
        resource_id=str(ws.id),
        workspace_id=ws.id,
        detail=f"slug={slug}",
    )
    return WorkspaceResponse(
        id=ws.id, name=ws.name, slug=ws.slug, member_count=1, created_at=ws.created_at
    )


@router.get("", response_model=WorkspaceListResponse)
def list_workspaces(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> WorkspaceListResponse:
    if user.role == "admin":
        workspaces = db.query(Workspace).order_by(Workspace.created_at.asc()).all()
    else:
        workspaces = (
            db.query(Workspace)
            .join(Membership, Membership.workspace_id == Workspace.id)
            .filter(Membership.user_id == user.id)
            .order_by(Workspace.created_at.asc())
            .all()
        )
    return WorkspaceListResponse(
        workspaces=[
            WorkspaceResponse(
                id=w.id,
                name=w.name,
                slug=w.slug,
                member_count=_member_count(db, w.id),
                created_at=w.created_at,
            )
            for w in workspaces
        ]
    )


@router.get("/{workspace_id}/members", response_model=MemberListResponse)
def list_members(
    workspace_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MemberListResponse:
    ws_id = _parse_uuid(workspace_id)
    ws = db.get(Workspace, ws_id)
    if ws is None:
        raise HTTPException(status_code=404, detail="Workspace not found")
    rows = (
        db.query(Membership, User)
        .join(User, User.id == Membership.user_id)
        .filter(Membership.workspace_id == ws_id)
        .order_by(Membership.created_at.asc())
        .all()
    )
    return MemberListResponse(
        workspace_id=ws_id,
        members=[
            MemberResponse(
                membership_id=m.id,
                user_id=u.id,
                email=u.email,
                role=m.role,
                created_at=m.created_at,
            )
            for m, u in rows
        ],
    )


@router.post("/{workspace_id}/members", response_model=MemberResponse)
def add_member(
    workspace_id: str,
    payload: MemberAddRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MemberResponse:
    ws_id = _parse_uuid(workspace_id)
    ws = db.get(Workspace, ws_id)
    if ws is None:
        raise HTTPException(status_code=404, detail="Workspace not found")
    _require_workspace_admin(db, ws_id, user)
    role = payload.role.lower()
    if role not in VALID_ROLES:
        raise HTTPException(status_code=422, detail=f"role must be one of {sorted(VALID_ROLES)}")
    target = db.query(User).filter(User.email == payload.email.strip().lower()).first()
    if target is None:
        raise HTTPException(status_code=404, detail="User with that email not found")
    existing = (
        db.query(Membership)
        .filter(Membership.workspace_id == ws_id, Membership.user_id == target.id)
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail="User already a member")
    membership = Membership(workspace_id=ws_id, user_id=target.id, role=role)
    db.add(membership)
    db.commit()
    db.refresh(membership)
    record_audit(
        db,
        actor_email=user.email,
        action="workspace.member_add",
        resource_type="membership",
        resource_id=str(membership.id),
        workspace_id=ws_id,
        detail=f"{target.email} as {role}",
    )
    return MemberResponse(
        membership_id=membership.id,
        user_id=target.id,
        email=target.email,
        role=membership.role,
        created_at=membership.created_at,
    )


@router.put("/{workspace_id}/members/{membership_id}", response_model=MemberResponse)
def update_member_role(
    workspace_id: str,
    membership_id: str,
    payload: MemberRoleUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MemberResponse:
    ws_id = _parse_uuid(workspace_id)
    _require_workspace_admin(db, ws_id, user)
    role = payload.role.lower()
    if role not in VALID_ROLES:
        raise HTTPException(status_code=422, detail=f"role must be one of {sorted(VALID_ROLES)}")
    membership = db.get(Membership, _parse_uuid(membership_id))
    if membership is None or membership.workspace_id != ws_id:
        raise HTTPException(status_code=404, detail="Membership not found")
    membership.role = role
    db.commit()
    db.refresh(membership)
    target = db.get(User, membership.user_id)
    record_audit(
        db,
        actor_email=user.email,
        action="workspace.member_role_change",
        resource_type="membership",
        resource_id=str(membership.id),
        workspace_id=ws_id,
        detail=f"role={role}",
    )
    return MemberResponse(
        membership_id=membership.id,
        user_id=membership.user_id,
        email=target.email if target else "",
        role=membership.role,
        created_at=membership.created_at,
    )


@router.delete("/{workspace_id}/members/{membership_id}")
def remove_member(
    workspace_id: str,
    membership_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    ws_id = _parse_uuid(workspace_id)
    _require_workspace_admin(db, ws_id, user)
    membership = db.get(Membership, _parse_uuid(membership_id))
    if membership is None or membership.workspace_id != ws_id:
        raise HTTPException(status_code=404, detail="Membership not found")
    db.delete(membership)
    db.commit()
    record_audit(
        db,
        actor_email=user.email,
        action="workspace.member_remove",
        resource_type="membership",
        resource_id=str(membership_id),
        workspace_id=ws_id,
    )
    return {"status": "removed", "membership_id": membership_id}
