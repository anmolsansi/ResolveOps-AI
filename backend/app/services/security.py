"""V10a security service: API keys, rate limiting, brute-force protection, IP allowlist."""
import hashlib
import json
import secrets
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.models import ApiKey, IpAllowlist, LoginAttempt, RateLimitLog, SecuritySetting

# --- API Keys ---


def create_api_key(
    db: Session, workspace_id, user_id, name: str,
    scopes: list[str], expires_days: int | None = None,
) -> dict:
    raw_key = f"ro_{secrets.token_hex(24)}"
    key_prefix = raw_key[:12]
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()

    expires_at = None
    if expires_days:
        expires_at = datetime.utcnow() + timedelta(days=expires_days)

    api_key = ApiKey(
        workspace_id=workspace_id,
        user_id=user_id,
        name=name,
        key_prefix=key_prefix,
        key_hash=key_hash,
        scopes_json=json.dumps(scopes),
        expires_at=expires_at,
    )
    db.add(api_key)
    db.flush()

    return {
        "id": str(api_key.id),
        "name": api_key.name,
        "key_prefix": key_prefix,
        "raw_key": raw_key,
        "scopes": scopes,
        "expires_at": expires_at.isoformat() if expires_at else None,
        "created_at": api_key.created_at.isoformat() if api_key.created_at else "",
    }


def list_api_keys(db: Session, workspace_id) -> list[dict]:
    keys = db.query(ApiKey).filter(
        ApiKey.workspace_id == workspace_id,
    ).order_by(ApiKey.created_at.desc()).all()
    return [_key_to_dict(k) for k in keys]


def revoke_api_key(db: Session, key_id, workspace_id) -> bool:
    key = db.query(ApiKey).filter(
        ApiKey.id == key_id,
        ApiKey.workspace_id == workspace_id,
    ).first()
    if not key:
        return False
    key.enabled = False
    return True


def verify_api_key(db: Session, raw_key: str) -> dict | None:
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
    api_key = db.query(ApiKey).filter(
        ApiKey.key_hash == key_hash,
        ApiKey.enabled,
    ).first()
    if not api_key:
        return None
    if api_key.expires_at and api_key.expires_at < datetime.utcnow():
        return None
    api_key.last_used_at = datetime.utcnow()
    return {
        "id": str(api_key.id),
        "workspace_id": api_key.workspace_id,
        "user_id": api_key.user_id,
        "scopes": json.loads(api_key.scopes_json),
    }


# --- Rate Limiting ---


def check_rate_limit(db: Session, key: str, limit: int, window_seconds: int = 60) -> bool:
    """Return True if under limit, False if over."""
    cutoff = datetime.utcnow() - timedelta(seconds=window_seconds)
    count = db.query(RateLimitLog).filter(
        RateLimitLog.key == key,
        RateLimitLog.timestamp >= cutoff,
    ).count()
    return count < limit


def record_rate_limit_hit(db: Session, key: str, endpoint: str = "") -> None:
    db.add(RateLimitLog(key=key, endpoint=endpoint))


# --- Brute-Force Protection ---


def check_brute_force(
    db: Session, email: str, max_attempts: int = 5,
    window_minutes: int = 15,
) -> bool:
    """Return True if NOT locked out (safe to proceed), False if locked out."""
    cutoff = datetime.utcnow() - timedelta(minutes=window_minutes)
    failures = db.query(LoginAttempt).filter(
        LoginAttempt.email == email,
        LoginAttempt.success.is_(False),
        LoginAttempt.created_at >= cutoff,
    ).count()
    return failures < max_attempts


def record_login_attempt(db: Session, email: str, ip_address: str, success: bool) -> None:
    db.add(LoginAttempt(
        email=email,
        ip_address=ip_address,
        success=success,
    ))


# --- Security Settings ---


def get_security_settings(db: Session, workspace_id) -> dict:
    setting = db.query(SecuritySetting).filter(
        SecuritySetting.workspace_id == workspace_id,
    ).first()
    if not setting:
        return {
            "rate_limit_requests_per_minute": settings.rate_limit_requests_per_minute,
            "rate_limit_burst": settings.rate_limit_burst,
            "max_login_attempts": settings.max_login_attempts,
            "lockout_duration_minutes": settings.lockout_duration_minutes,
            "session_timeout_minutes": settings.session_timeout_minutes,
            "ip_allowlist_enabled": settings.ip_allowlist_enabled,
        }
    return {
        "rate_limit_requests_per_minute": setting.rate_limit_requests_per_minute,
        "rate_limit_burst": setting.rate_limit_burst,
        "max_login_attempts": setting.max_login_attempts,
        "lockout_duration_minutes": setting.lockout_duration_minutes,
        "session_timeout_minutes": setting.session_timeout_minutes,
        "ip_allowlist_enabled": setting.ip_allowlist_enabled,
    }


def update_security_settings(db: Session, workspace_id, **kwargs) -> dict:
    setting = db.query(SecuritySetting).filter(
        SecuritySetting.workspace_id == workspace_id,
    ).first()
    if not setting:
        setting = SecuritySetting(workspace_id=workspace_id)
        db.add(setting)

    for key, value in kwargs.items():
        if value is not None and hasattr(setting, key):
            setattr(setting, key, value)

    db.flush()
    return get_security_settings(db, workspace_id)


# --- IP Allowlist ---


def add_ip_allowlist(
    db: Session, workspace_id, ip_address: str,
    note: str, created_by: str,
) -> dict:
    entry = IpAllowlist(
        workspace_id=workspace_id,
        ip_address=ip_address,
        note=note,
        created_by=created_by,
    )
    db.add(entry)
    db.flush()
    return _ip_to_dict(entry)


def list_ip_allowlist(db: Session, workspace_id) -> list[dict]:
    entries = db.query(IpAllowlist).filter(
        IpAllowlist.workspace_id == workspace_id,
    ).order_by(IpAllowlist.created_at.desc()).all()
    return [_ip_to_dict(e) for e in entries]


def remove_ip_allowlist(db: Session, entry_id, workspace_id) -> bool:
    entry = db.query(IpAllowlist).filter(
        IpAllowlist.id == entry_id,
        IpAllowlist.workspace_id == workspace_id,
    ).first()
    if not entry:
        return False
    db.delete(entry)
    return True


def check_ip_allowed(db: Session, workspace_id, ip_address: str) -> bool:
    setting = db.query(SecuritySetting).filter(
        SecuritySetting.workspace_id == workspace_id,
    ).first()
    if not setting or not setting.ip_allowlist_enabled:
        return True
    entry = db.query(IpAllowlist).filter(
        IpAllowlist.workspace_id == workspace_id,
        IpAllowlist.ip_address == ip_address,
        IpAllowlist.enabled,
    ).first()
    return entry is not None


def list_login_attempts(db: Session, limit: int = 50) -> list[dict]:
    attempts = db.query(LoginAttempt).order_by(
        LoginAttempt.created_at.desc(),
    ).limit(limit).all()
    return [_login_to_dict(a) for a in attempts]


def _key_to_dict(key: ApiKey) -> dict:
    return {
        "id": str(key.id),
        "name": key.name,
        "key_prefix": key.key_prefix,
        "scopes": json.loads(key.scopes_json),
        "enabled": key.enabled,
        "last_used_at": key.last_used_at.isoformat() if key.last_used_at else None,
        "expires_at": key.expires_at.isoformat() if key.expires_at else None,
        "created_at": key.created_at.isoformat() if key.created_at else "",
    }


def _ip_to_dict(entry: IpAllowlist) -> dict:
    return {
        "id": str(entry.id),
        "ip_address": entry.ip_address,
        "note": entry.note,
        "enabled": entry.enabled,
        "created_by": entry.created_by,
        "created_at": entry.created_at.isoformat() if entry.created_at else "",
    }


def _login_to_dict(attempt: LoginAttempt) -> dict:
    return {
        "id": str(attempt.id),
        "email": attempt.email,
        "ip_address": attempt.ip_address,
        "success": attempt.success,
        "created_at": attempt.created_at.isoformat() if attempt.created_at else "",
    }
