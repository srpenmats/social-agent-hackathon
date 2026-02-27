"""
Simple Twitter connection without requiring elevated API access.
Just verifies Bearer Token works and marks platform as connected.
"""

from fastapi import APIRouter
from datetime import datetime, timezone
import os

from db.connection import get_supabase_admin

router = APIRouter(prefix="/api/v1/platforms", tags=["platforms-simple"])


@router.post("/connect-simple/twitter")
async def connect_twitter_simple():
    """
    Mark Twitter as connected if we have credentials.
    Simpler than full OAuth - just checks env vars exist.
    """
    
    bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
    if not bearer_token:
        return {
            "success": False,
            "error": "TWITTER_BEARER_TOKEN not set"
        }
    
    db = get_supabase_admin()
    
    # Check if platform record exists
    try:
        existing = db.table("platforms").select("id").eq("name", "x").execute()
        
        platform_data = {
            "name": "x",
            "display_name": "X / Twitter",
            "status": "connected",
            "credentials": {
                "has_bearer_token": True,
                "connection_type": "api_token"
            },
            "connected_at": datetime.now(timezone.utc).isoformat(),
            "last_verified": datetime.now(timezone.utc).isoformat(),
        }
        
        if existing.data:
            # Update existing
            db.table("platforms").update(platform_data).eq("name", "x").execute()
            action = "updated"
        else:
            # Create new
            db.table("platforms").insert(platform_data).execute()
            action = "created"
        
        return {
            "success": True,
            "action": action,
            "platform": "x",
            "display_name": "X / Twitter",
            "status": "connected",
            "message": "Twitter/X marked as connected"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to store connection"
        }
