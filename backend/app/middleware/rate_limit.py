"""Rate limiting middleware using sliding window."""
import os
import time

from fastapi import Request, Response
from sqlalchemy.orm import Session
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.core.database import SessionLocal
from app.models.models import RateLimitLog


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple in-memory + DB sliding window rate limiter."""

    def __init__(self, app, requests_per_minute: int = 60, burst: int = 10):
        super().__init__(app)
        self.rpm = requests_per_minute
        self.burst = burst
        self._window: dict[str, list[float]] = {}
        self._skip_prefixes = ("/health", "/docs", "/openapi.json", "/auth/")
        self._testing = os.getenv("TESTING", "0") == "1"

    def _get_key(self, request: Request) -> str:
        auth = request.headers.get("authorization", "")
        if auth.startswith("Bearer "):
            return f"bearer:{auth[7:24]}"
        widget_key = request.headers.get("x-widget-key", "")
        if widget_key:
            return f"widget:{widget_key[:8]}"
        return f"ip:{request.client.host if request.client else 'unknown'}"

    async def dispatch(self, request: Request, call_next) -> Response:
        path = request.url.path
        if (path in ("/health", "/docs", "/openapi.json")
                or any(path.startswith(p) for p in self._skip_prefixes)
                or self._testing):
            return await call_next(request)

        key = self._get_key(request)
        now = time.time()
        window_start = now - 60

        if key not in self._window:
            self._window[key] = []

        self._window[key] = [t for t in self._window[key] if t > window_start]

        if len(self._window[key]) >= self.rpm:
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded. Try again later."},
            )

        self._window[key].append(now)

        try:
            db: Session = SessionLocal()
            db.add(RateLimitLog(key=key, endpoint=path))
            db.commit()
            db.close()
        except Exception:
            pass

        return await call_next(request)
