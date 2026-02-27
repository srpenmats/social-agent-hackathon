import logging

from fastapi import APIRouter, HTTPException

from db.connection import get_supabase_admin
from middleware.auth import CurrentUser

logger = logging.getLogger(__name__)
router = APIRouter(tags=["hubs"])


@router.get("/api/v1/hubs/{platform}/stats")
async def hub_stats(platform: str, user: CurrentUser):
    if platform not in ("tiktok", "instagram", "x"):
        raise HTTPException(status_code=400, detail="Invalid platform")

    db = get_supabase_admin()

    # Count reply engagements for this platform
    engagements_resp = (
        db.table("engagements")
        .select("id")
        .eq("platform", platform)
        .execute()
    )
    replies_count = len(engagements_resp.data or [])

    # Build keywords from discovered_videos hashtags
    videos_resp = (
        db.table("discovered_videos")
        .select("hashtags, description, likes")
        .eq("platform", platform)
        .execute()
    )
    videos = videos_resp.data or []

    tag_map: dict[str, dict] = {}
    for v in videos:
        tags = v.get("hashtags") or []
        if isinstance(tags, str):
            import json
            try:
                tags = json.loads(tags)
            except (json.JSONDecodeError, ValueError):
                tags = []
        for tag in tags:
            if tag not in tag_map:
                tag_map[tag] = {
                    "term": tag,
                    "action": "monitor",
                    "match": v.get("description", "")[:80],
                    "volume": v.get("likes", 0),
                }
            else:
                tag_map[tag]["volume"] += v.get("likes", 0)

    keywords = list(tag_map.values())

    # Build drafts from review_queue (pending items where decision IS NULL)
    review_resp = (
        db.table("review_queue")
        .select("id, video_id, proposed_text, risk_score")
        .is_("decision", "null")
        .execute()
    )
    drafts = []
    for item in review_resp.data or []:
        video_id = item.get("video_id")
        user_name = "unknown"
        original_msg = ""
        tweet_url = ""
        if video_id:
            vid_resp = (
                db.table("discovered_videos")
                .select("creator, description, platform, video_url")
                .eq("id", video_id)
                .execute()
            )
            vid_rows = vid_resp.data or []
            if vid_rows:
                vid = vid_rows[0]
                # Only include drafts matching this platform
                if vid.get("platform") != platform:
                    continue
                user_name = vid.get("creator", "unknown")
                original_msg = vid.get("description", "")
                tweet_url = vid.get("video_url", "")

        drafts.append({
            "id": item.get("id"),
            "user": user_name,
            "msg": original_msg,
            "draft": item.get("proposed_text", ""),
            "risk_score": item.get("risk_score", 0),
            "tweet_url": tweet_url,
        })

    # For Instagram, also return discovered videos directly
    reels = []
    if platform == "instagram":
        for v in videos:
            tags = v.get("hashtags") or []
            if isinstance(tags, str):
                import json as _json
                try:
                    tags = _json.loads(tags)
                except (json.JSONDecodeError, ValueError):
                    tags = []
            reels.append({
                "creator": v.get("creator", "unknown"),
                "description": v.get("description", ""),
                "likes": v.get("likes", 0),
                "hashtags": tags[:3],
            })

    return {
        "stats": {
            "replies": replies_count,
            "keywords": len(keywords),
            "sentiment": "0.82",
            "quota": "67%",
        },
        "keywords": keywords,
        "reels": reels,
        "drafts": drafts,
    }


@router.post("/api/v1/hubs/x/sync")
async def sync_twitter(user: CurrentUser):
    """Pull latest tweets from Twitter API and update the local DB."""
    try:
        from scripts.sync_twitter import fetch_tweets, sync
        data = fetch_tweets()
        sync(data)
        return {"status": "ok", "message": "Twitter sync complete"}
    except Exception as e:
        logger.exception("Twitter sync failed")
        raise HTTPException(status_code=500, detail=f"Sync failed: {e}")


@router.post("/api/v1/hubs/instagram/sync")
async def sync_instagram(user: CurrentUser):
    """Re-seed Instagram finance Reels into the local DB."""
    try:
        from scripts.seed_instagram import seed
        seed()
        return {"status": "ok", "message": "Instagram sync complete"}
    except Exception as e:
        logger.exception("Instagram sync failed")
        raise HTTPException(status_code=500, detail=f"Sync failed: {e}")
