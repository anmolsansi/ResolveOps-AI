import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.assist import router as assist_router
from app.api.audit import router as audit_router
from app.api.auth import router as auth_router
from app.api.connectors import router as connectors_router
from app.api.conversations import router as conversations_router
from app.api.dashboard import router as dashboard_router
from app.api.eval import router as eval_router
from app.api.health import router as health_router
from app.api.intelligence import router as intelligence_router
from app.api.jobs import router as jobs_router
from app.api.kb import router as kb_router
from app.api.pii import router as pii_router
from app.api.prompts import router as prompts_router
from app.api.rag import router as rag_router
from app.api.reliability import router as reliability_router
from app.api.retention import router as retention_router
from app.api.settings import router as settings_router
from app.api.sla import router as sla_router
from app.api.tickets import router as tickets_router
from app.api.tools import router as tools_router
from app.api.widget import router as widget_router
from app.api.workflow import router as workflow_router
from app.api.workspaces import router as workspaces_router
from app.api.analytics import router as analytics_router
from app.api.security_admin import router as security_admin_router
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.ip_allowlist import IpAllowlistMiddleware


def _cors_origins() -> list[str]:
    configured_origins = os.getenv("CORS_ALLOW_ORIGINS", "http://localhost:5173")
    return [origin.strip() for origin in configured_origins.split(",") if origin.strip()]


def create_app() -> FastAPI:
    application = FastAPI(title="ResolveOps AI", version="0.1.0")
    application.add_middleware(
        CORSMiddleware,
        allow_origins=_cors_origins(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.include_router(health_router)
    application.include_router(tickets_router, prefix="/tickets", tags=["tickets"])
    application.include_router(rag_router, prefix="/rag", tags=["rag"])
    application.include_router(dashboard_router, prefix="/dashboard", tags=["dashboard"])
    application.include_router(eval_router, prefix="/eval", tags=["eval"])
    application.include_router(reliability_router, prefix="/reliability", tags=["reliability"])
    application.include_router(connectors_router, prefix="/connectors", tags=["connectors"])
    application.include_router(assist_router, prefix="/assist", tags=["assist"])
    application.include_router(kb_router, prefix="/kb", tags=["kb"])
    application.include_router(sla_router, prefix="/sla", tags=["sla"])
    application.include_router(auth_router, prefix="/auth", tags=["auth"])
    application.include_router(workspaces_router, prefix="/workspaces", tags=["workspaces"])
    application.include_router(audit_router, prefix="/audit", tags=["audit"])
    application.include_router(settings_router, prefix="/settings", tags=["settings"])
    application.include_router(retention_router, prefix="/retention", tags=["retention"])
    application.include_router(pii_router, prefix="/pii", tags=["pii"])
    application.include_router(prompts_router, prefix="/prompts", tags=["prompts"])
    application.include_router(jobs_router, prefix="/jobs", tags=["jobs"])
    application.include_router(widget_router, prefix="/widget", tags=["widget"])
    application.include_router(
        conversations_router, prefix="/conversations", tags=["conversations"]
    )
    application.include_router(tools_router, prefix="/tools", tags=["tools"])
    application.include_router(
        intelligence_router, prefix="/intelligence", tags=["intelligence"]
    )
    application.include_router(
        workflow_router, prefix="/workflow", tags=["workflow"]
    )
    application.include_router(
        analytics_router, prefix="/analytics", tags=["analytics"]
    )
    application.include_router(
        security_admin_router, prefix="/security", tags=["security"]
    )
    application.add_middleware(IpAllowlistMiddleware)
    application.add_middleware(RateLimitMiddleware)
    return application


app = create_app()
