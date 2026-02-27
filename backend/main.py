from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from db.connection import init_clients
from middleware.cors import get_cors_config
from routers import (
    comments,
    connections,
    dashboard,
    db_init,
    demo,
    discovery,
    discovery_enhanced,
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
app.include_router(discovery.router)
app.include_router(discovery_enhanced.router)
app.include_router(db_init.router)


@app.get("/api/v1/health")
async def health_check():
    return {"status": "ok"}
