"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response

from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.api.v1.router import api_router
from app.middleware.metrics import PrometheusMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


def create_application() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        description="REST API for discovering academic conferences, symposiums, workshops, and call-for-papers events.",
        version="1.0.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        lifespan=lifespan,
    )
    app.add_middleware(PrometheusMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    register_exception_handlers(app)
    app.include_router(api_router, prefix=settings.api_v1_prefix)
    return app


app = create_application()


@app.get("/health")
async def health():
    """Liveness probe."""
    return {"status": "ok"}


@app.get("/health/ready")
async def readiness():
    """Readiness probe: checks DB connectivity."""
    from sqlalchemy import text
    from app.db.session import async_session_factory

    try:
        async with async_session_factory() as session:
            await session.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception:
        return JSONResponse(content={"status": "not ready"}, status_code=503)


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )
