"""Feedback Loop API — exposes AI learning stats, trend data, and examples."""

from fastapi import APIRouter

from services.ai.feedback_loop import FeedbackLoopService

router = APIRouter(tags=["feedback"])


@router.get("/api/v1/feedback/stats")
async def feedback_stats():
    svc = FeedbackLoopService()
    return svc.get_stats()


@router.get("/api/v1/feedback/accuracy-trend")
async def feedback_accuracy_trend():
    svc = FeedbackLoopService()
    return svc.get_accuracy_trend()


@router.get("/api/v1/feedback/examples")
async def feedback_examples():
    svc = FeedbackLoopService()
    return svc.get_examples()


@router.post("/api/v1/feedback/seed")
async def feedback_seed():
    svc = FeedbackLoopService()
    result = svc.seed_demo_data()
    return {"status": "seeded", **result}
