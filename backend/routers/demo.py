"""Simple endpoint to serve review queue data for demo."""

from fastapi import APIRouter
from pathlib import Path
import json

router = APIRouter(tags=["demo"])

@router.get("/api/v1/review/queue-demo")
async def get_review_queue_demo():
    """Serve the generated review queue for demo purposes."""
    queue_file = Path(__file__).parent.parent.parent / "review_queue.json"
    
    if queue_file.exists():
        with open(queue_file) as f:
            data = json.load(f)
        return data['review_queue']
    
    return []


@router.get("/api/v1/dashboard/demo-stats")
async def get_demo_stats():
    """Serve demo dashboard stats."""
    queue_file = Path(__file__).parent.parent.parent / "review_queue.json"
    
    if queue_file.exists():
        with open(queue_file) as f:
            data = json.load(f)
        
        return {
            "total_discovered": 20,
            "pending_review": len(data['review_queue']),
            "avg_confidence": 7.7,
            "platforms": {
                "x": len(data['review_queue'])
            }
        }
    
    return {
        "total_discovered": 0,
        "pending_review": 0,
        "avg_confidence": 0,
        "platforms": {}
    }
