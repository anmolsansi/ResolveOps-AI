"""IP allowlist middleware."""
import os

from fastapi import Request, Response
from sqlalchemy.orm import Session
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.core.database import SessionLocal
from app.models.models import IpAllowlist, SecuritySetting


class IpAllowlistMiddleware(BaseHTTPMiddleware):
    """Check client IP against workspace allowlist."""

    SKIP_PATHS = {"/health", "/docs", "/openapi.json", "/auth/login", "/auth/register", "/widget"}

    def __init__(self, app):
        super().__init__(app)
        self._testing = os.getenv("TESTING", "0") == "1"

    async def dispatch(self, request: Request, call_next) -> Response:
        if self._testing:
            return await call_next(request)

        path = request.url.path
        if any(path.startswith(s) for s in self.SKIP_PATHS):
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        if client_ip in ("127.0.0.1", "::1", "localhost"):
            return await call_next(request)

        try:
            db: Session = SessionLocal()
            setting = db.query(SecuritySetting).first()
            if not setting or not setting.ip_allowlist_enabled:
                db.close()
                return await call_next(request)

            allowed = db.query(IpAllowlist).filter(
                IpAllowlist.enabled,
            ).all()
            db.close()

            allowed_ips = {entry.ip_address for entry in allowed}
            if client_ip not in allowed_ips:
                return JSONResponse(
                    status_code=403,
                    content={"detail": "IP address not allowed."},
                )
        except Exception:
            pass

        return await call_next(request)
