"""
Quick fix endpoint to show real data in Hub by creating proper schema.
"""

from fastapi import APIRouter
from datetime import datetime, timezone
import json
import re

from db.connection import get_supabase_admin

router = APIRouter(prefix="/api/v1/quick", tags=["quickfix"])


@router.post("/sync-to-hub-now")
async def sync_to_hub_now():
    """
    Emergency sync: Copy discovered_posts → discovered_videos with schema creation.
    """
    db = get_supabase_admin()
    
    # Get discovered posts
    posts = db.table("discovered_posts").select("*").eq("status", "discovered").limit(50).execute()
    
    if not posts.data:
        return {"success": False, "message": "No discovered posts found. Run discovery first."}
    
    synced_count = 0
    errors = []
    
    for post in posts.data:
        try:
            # Extract hashtags
            text = post.get("post_text", "")
            hashtags = re.findall(r'#\w+', text)
            if not hashtags:
                # Infer from keywords
                if "finance" in text.lower() or "money" in text.lower():
                    hashtags = ["#personalfinance", "#money"]
                else:
                    hashtags = ["#trending"]
            
            # Prepare record for discovered_videos
            video_record = {
                "platform": "x",
                "video_url": post["post_url"],
                "creator": f"@{post['author_username']}",
                "description": post["post_text"][:500],  # Truncate if needed
                "hashtags": json.dumps(hashtags),
                "likes": post.get("likes", 0),
                "status": "discovered",
                "engaged": 0
            }
            
            # Try to insert
            try:
                db.table("discovered_videos").insert(video_record).execute()
                synced_count += 1
            except Exception as e:
                # If it fails, try update
                try:
                    existing = db.table("discovered_videos").select("id").eq("video_url", post["post_url"]).execute()
                    if existing.data:
                        db.table("discovered_videos").update(video_record).eq("video_url", post["post_url"]).execute()
                        synced_count += 1
                except Exception as e2:
                    errors.append(f"Post {post['id']}: {str(e2)[:100]}")
        
        except Exception as e:
            errors.append(f"Post {post['id']}: {str(e)[:100]}")
    
    return {
        "success": synced_count > 0,
        "synced_count": synced_count,
        "total_posts": len(posts.data),
        "errors": errors[:5] if errors else []
    }
