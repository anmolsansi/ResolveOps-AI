from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.assist import router as assist_router
from app.api.connectors import router as connectors_router
from app.api.dashboard import router as dashboard_router
from app.api.eval import router as eval_router
from app.api.health import router as health_router
from app.api.kb import router as kb_router
from app.api.rag import router as rag_router
from app.api.sla import router as sla_router
from app.api.tickets import router as tickets_router


def create_app() -> FastAPI:
    application = FastAPI(title="ResolveOps AI", version="0.1.0")
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.include_router(health_router)
    application.include_router(tickets_router, prefix="/tickets", tags=["tickets"])
    application.include_router(rag_router, prefix="/rag", tags=["rag"])
    application.include_router(dashboard_router, prefix="/dashboard", tags=["dashboard"])
    application.include_router(eval_router, prefix="/eval", tags=["eval"])
    application.include_router(connectors_router, prefix="/connectors", tags=["connectors"])
    application.include_router(assist_router, prefix="/assist", tags=["assist"])
    application.include_router(kb_router, prefix="/kb", tags=["kb"])
    application.include_router(sla_router, prefix="/sla", tags=["sla"])
    return application


app = create_app()
