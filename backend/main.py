from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.db.connection import init_clients
from backend.middleware.cors import get_cors_config
from backend.routers import (
    comments,
    connections,
    dashboard,
    demo,
    execution,
    hubs,
    neoclaw,
    personas,
    review,
    settings,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        init_clients()
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning(f"DB init skipped: {e}")
    yield


app = FastAPI(
    title="MoneyLion Social Agent API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(CORSMiddleware, **get_cors_config())

app.include_router(dashboard.router)
app.include_router(comments.router)
app.include_router(review.router)
app.include_router(settings.router)
app.include_router(connections.router)
app.include_router(execution.router)
app.include_router(neoclaw.router)
app.include_router(personas.router)
app.include_router(hubs.router)
app.include_router(demo.router)


@app.get("/api/v1/health")
async def health_check():
    return {"status": "ok"}
