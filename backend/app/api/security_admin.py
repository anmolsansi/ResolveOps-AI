"""V10a security admin API: API keys, rate limits, brute-force, IP allowlist."""
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_current_workspace
from app.core.database import get_db
from app.models.models import User, Workspace
from app.schemas.security import (
    ApiKeyCreateRequest,
    ApiKeyCreateResponse,
    ApiKeyListResponse,
    ApiKeyResponse,
    IpAllowlistEntryCreateRequest,
    IpAllowlistEntryResponse,
    IpAllowlistResponse,
    LoginAttemptListResponse,
    LoginAttemptResponse,
    RateLimitConfigResponse,
    RateLimitConfigUpdateRequest,
    SecuritySettingsResponse,
    SecuritySettingsUpdateRequest,
)
from app.services import security as svc

router = APIRouter()


# --- API Keys ---


@router.post("/api-keys", response_model=ApiKeyCreateResponse)
def create_api_key(
    body: ApiKeyCreateRequest,
    workspace: Workspace = Depends(get_current_workspace),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiKeyCreateResponse:
    result = svc.create_api_key(
        db, workspace.id, user.id, body.name, body.scopes, body.expires_days,
    )
    db.commit()
    return ApiKeyCreateResponse(**result)


@router.get("/api-keys", response_model=ApiKeyListResponse)
def list_api_keys(
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db),
) -> ApiKeyListResponse:
    items = svc.list_api_keys(db, workspace.id)
    return ApiKeyListResponse(items=[ApiKeyResponse(**i) for i in items], total=len(items))


@router.delete("/api-keys/{key_id}")
def revoke_api_key(
    key_id: str,
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db),
) -> dict:
    ok = svc.revoke_api_key(db, uuid.UUID(key_id), workspace.id)
    if not ok:
        raise HTTPException(status_code=404, detail="API key not found")
    db.commit()
    return {"ok": True}


# --- Rate Limits ---


@router.get("/rate-limits", response_model=RateLimitConfigResponse)
def get_rate_limits(
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db),
) -> RateLimitConfigResponse:
    settings = svc.get_security_settings(db, workspace.id)
    return RateLimitConfigResponse(
        requests_per_minute=settings["rate_limit_requests_per_minute"],
        burst=settings["rate_limit_burst"],
    )


@router.put("/rate-limits", response_model=RateLimitConfigResponse)
def update_rate_limits(
    body: RateLimitConfigUpdateRequest,
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db),
) -> RateLimitConfigResponse:
    kwargs = {}
    if body.requests_per_minute is not None:
        kwargs["rate_limit_requests_per_minute"] = body.requests_per_minute
    if body.burst is not None:
        kwargs["rate_limit_burst"] = body.burst
    settings = svc.update_security_settings(db, workspace.id, **kwargs)
    db.commit()
    return RateLimitConfigResponse(
        requests_per_minute=settings["rate_limit_requests_per_minute"],
        burst=settings["rate_limit_burst"],
    )


# --- Login Attempts ---


@router.get("/login-attempts", response_model=LoginAttemptListResponse)
def list_login_attempts(
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db),
) -> LoginAttemptListResponse:
    items = svc.list_login_attempts(db)
    return LoginAttemptListResponse(
        items=[LoginAttemptResponse(**i) for i in items],
        total=len(items),
    )


# --- IP Allowlist ---


@router.post("/ip-allowlist", response_model=IpAllowlistEntryResponse)
def add_ip(
    body: IpAllowlistEntryCreateRequest,
    workspace: Workspace = Depends(get_current_workspace),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> IpAllowlistEntryResponse:
    result = svc.add_ip_allowlist(db, workspace.id, body.ip_address, body.note, user.email)
    db.commit()
    return IpAllowlistEntryResponse(**result)


@router.get("/ip-allowlist", response_model=IpAllowlistResponse)
def list_ips(
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db),
) -> IpAllowlistResponse:
    items = svc.list_ip_allowlist(db, workspace.id)
    return IpAllowlistResponse(
        items=[IpAllowlistEntryResponse(**i) for i in items], total=len(items)
    )


@router.delete("/ip-allowlist/{entry_id}")
def remove_ip(
    entry_id: str,
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db),
) -> dict:
    ok = svc.remove_ip_allowlist(db, uuid.UUID(entry_id), workspace.id)
    if not ok:
        raise HTTPException(status_code=404, detail="IP entry not found")
    db.commit()
    return {"ok": True}


# --- Security Settings ---


@router.get("/settings", response_model=SecuritySettingsResponse)
def get_security(
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db),
) -> SecuritySettingsResponse:
    result = svc.get_security_settings(db, workspace.id)
    return SecuritySettingsResponse(**result)


@router.put("/settings", response_model=SecuritySettingsResponse)
def update_security(
    body: SecuritySettingsUpdateRequest,
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db),
) -> SecuritySettingsResponse:
    kwargs = body.model_dump(exclude_none=True)
    result = svc.update_security_settings(db, workspace.id, **kwargs)
    db.commit()
    return SecuritySettingsResponse(**result)
