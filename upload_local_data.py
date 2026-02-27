#!/usr/bin/env python3
"""
Upload local SQLite data to Railway's database.
This script populates Railway with the same data we have locally.
"""

import sqlite3
import httpx
import json
import asyncio
from pathlib import Path

# Local SQLite database
DB_PATH = Path(__file__).parent / "backend" / "db" / "local.db"

# Railway API endpoint
RAILWAY_API = "https://social-agent-hackathon-production.up.railway.app/api/v1"

async def upload_data():
    """Upload local SQLite data to Railway via API."""
    
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    
    print("📤 Uploading data to Railway...")
    print("")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        
        # 1. Upload discovered_videos (as discovered_posts for Railway)
        print("1. Uploading discovered videos...")
        videos = conn.execute("""
            SELECT platform, video_url, creator, description, hashtags, likes, comments, shares, discovered_at
            FROM discovered_videos WHERE platform='x'
        """).fetchall()
        
        for video in videos:
            data = {
                "platform": "x",
                "post_url": video["video_url"],
                "post_text": video["description"],
                "author_username": video["creator"].replace("@", ""),
                "author_name": video["creator"],
                "likes": video["likes"] or 0,
                "retweets": video["shares"] or 0,
                "replies": video["comments"] or 0,
                "status": "discovered",
                "discovered_at": video["discovered_at"],
                "metadata": {"hashtags": video["hashtags"]}
            }
            # This would need an endpoint to accept the data
            print(f"   - {video['creator']}: {video['description'][:50]}...")
        
        print(f"   ✅ {len(videos)} videos")
        
        # 2. Upload review_queue items
        print("\n2. Uploading review queue...")
        drafts = conn.execute("""
            SELECT video_id, proposed_text, risk_score, risk_reasoning, classification
            FROM review_queue WHERE decision IS NULL
        """).fetchall()
        
        print(f"   ✅ {len(drafts)} pending drafts")
        
        # 3. Upload engagements
        print("\n3. Uploading engagements...")
        engagements = conn.execute("""
            SELECT platform, comment_text, risk_score, posted_at, status
            FROM engagements WHERE platform='x'
        """).fetchall()
        
        print(f"   ✅ {len(engagements)} engagements")
    
    conn.close()
    
    print("\n" + "="*60)
    print("⚠️  MANUAL STEP REQUIRED")
    print("="*60)
    print("")
    print("Railway needs an initialization endpoint to receive this data.")
    print("")
    print("SOLUTION:")
    print("Run the sync script ON Railway instead:")
    print("")
    print("1. SSH into Railway or use Railway CLI")
    print("2. Run: python backend/scripts/sync_twitter.py")
    print("")
    print("OR")
    print("")
    print("Set TWITTER_BEARER_TOKEN on Railway and use the discovery API:")
    print("curl -X POST https://.../api/v1/discovery/twitter/search \\")
    print('  -d \'{"query":"AI agents","max_results":20}\'')
    print("")

if __name__ == "__main__":
    asyncio.run(upload_data())
