from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.dashboard import router as dashboard_router
from app.api.eval import router as eval_router
from app.api.health import router as health_router
from app.api.rag import router as rag_router
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
    return application


app = create_app()
