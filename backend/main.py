from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from db.connection import init_clients
from middleware.cors import get_cors_config
from routers import (
    agent_smart,
    comments,
    connections,
    dashboard,
    db_init,
    db_migrate,
    db_seed,
    debug,
    demo,
    discovery,
    discovery_enhanced,
    execution,
    feedback,
    hubs,
    jen,
    neoclaw,
    personas,
    platform_connection,
    platform_direct,
    platform_simple,
    populate,
    populate_engagements,
    quickfix,
    review,
    review_posts,
    scheduler,
    settings,
    smart_discovery,
    twitter_live,
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
app.include_router(review_posts.router)
app.include_router(settings.router)
app.include_router(connections.router)
app.include_router(execution.router)
app.include_router(neoclaw.router)
app.include_router(personas.router)
app.include_router(debug.router)
app.include_router(agent_smart.router)
app.include_router(platform_connection.router)
app.include_router(platform_direct.router)
app.include_router(platform_simple.router)
app.include_router(scheduler.router)
app.include_router(hubs.router)
app.include_router(jen.router)
app.include_router(demo.router)
app.include_router(discovery.router)
app.include_router(discovery_enhanced.router)
app.include_router(db_init.router)
app.include_router(db_migrate.router)
app.include_router(db_seed.router)
app.include_router(quickfix.router)
app.include_router(twitter_live.router)
app.include_router(populate.router)
app.include_router(populate_engagements.router)
app.include_router(smart_discovery.router)
app.include_router(feedback.router)


@app.get("/api/v1/health")
async def health_check():
    return {"status": "ok"}
