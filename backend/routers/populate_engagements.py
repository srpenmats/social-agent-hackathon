"""
Populate engagement data for Overview tab dashboard.
"""

from fastapi import APIRouter
from datetime import datetime, timezone, timedelta
import random

from db.connection import get_supabase_admin

router = APIRouter(prefix="/api/v1/populate", tags=["populate"])


@router.post("/engagements")
async def populate_engagements():
    """
    Populate engagements table with sample Twitter engagement data.
    This makes the Overview dashboard show real-looking metrics.
    """
    db = get_supabase_admin()
    
    # Get the discovered_videos we just populated
    videos = db.table("discovered_videos").select("id, creator, description").eq("platform", "x").limit(5).execute()
    
    if not videos.data:
        return {"success": False, "message": "No discovered_videos found. Run /populate/now first."}
    
    stored_count = 0
    
    # Create engagement records for each video
    for i, video in enumerate(videos.data):
        video_id = video.get("id")
        
        # Create a posted engagement
        engagement = {
            "platform": "x",
            "video_id": video_id,
            "comment_text": f"Great insights! This is exactly what people need to hear about personal finance. 💰",
            "risk_score": random.randint(10, 30),
            "approval_path": "manual",
            "posted_at": (datetime.now(timezone.utc) - timedelta(hours=random.randint(1, 48))).isoformat(),
            "status": "posted"
        }
        
        try:
            result = db.table("engagements").insert(engagement).execute()
            if result.data:
                engagement_id = result.data[0]["id"]
                
                # Add engagement metrics
                metrics = {
                    "engagement_id": engagement_id,
                    "likes": random.randint(50, 500),
                    "replies": random.randint(5, 50),
                    "impressions": random.randint(1000, 10000)
                }
                db.table("engagement_metrics").insert(metrics).execute()
                
                stored_count += 1
        except Exception as e:
            print(f"Error creating engagement: {e}")
    
    return {
        "success": True,
        "stored": stored_count,
        "message": f"Created {stored_count} Twitter engagements with metrics"
    }
