"""V10a security schemas."""
from pydantic import BaseModel


class ApiKeyCreateRequest(BaseModel):
    name: str
    scopes: list[str] = ["read"]
    expires_days: int | None = None


class ApiKeyCreateResponse(BaseModel):
    id: str
    name: str
    key_prefix: str
    raw_key: str
    scopes: list[str]
    expires_at: str | None
    created_at: str


class ApiKeyResponse(BaseModel):
    id: str
    name: str
    key_prefix: str
    scopes: list[str]
    enabled: bool
    last_used_at: str | None
    expires_at: str | None
    created_at: str


class ApiKeyListResponse(BaseModel):
    items: list[ApiKeyResponse]
    total: int


class RateLimitConfigResponse(BaseModel):
    requests_per_minute: int
    burst: int


class RateLimitConfigUpdateRequest(BaseModel):
    requests_per_minute: int | None = None
    burst: int | None = None


class LoginAttemptResponse(BaseModel):
    id: str
    email: str
    ip_address: str
    success: bool
    created_at: str


class LoginAttemptListResponse(BaseModel):
    items: list[LoginAttemptResponse]
    total: int


class IpAllowlistEntryCreateRequest(BaseModel):
    ip_address: str
    note: str = ""


class IpAllowlistEntryResponse(BaseModel):
    id: str
    ip_address: str
    note: str
    enabled: bool
    created_by: str
    created_at: str


class IpAllowlistResponse(BaseModel):
    items: list[IpAllowlistEntryResponse]
    total: int


class SecuritySettingsResponse(BaseModel):
    rate_limit_requests_per_minute: int
    rate_limit_burst: int
    max_login_attempts: int
    lockout_duration_minutes: int
    session_timeout_minutes: int
    ip_allowlist_enabled: bool


class SecuritySettingsUpdateRequest(BaseModel):
    rate_limit_requests_per_minute: int | None = None
    rate_limit_burst: int | None = None
    max_login_attempts: int | None = None
    lockout_duration_minutes: int | None = None
    session_timeout_minutes: int | None = None
    ip_allowlist_enabled: bool | None = None
