#!/usr/bin/env python3
"""Upload discovered tweets to Railway backend via API."""

import json
import asyncio
import httpx
from pathlib import Path

BACKEND_URL = "https://social-agent-hackathon-production.up.railway.app"
tweets_file = Path(__file__).parent / "discovered_tweets.json"

async def upload_tweets():
    """Upload tweets via API."""
    
    if not tweets_file.exists():
        print("❌ No discovered_tweets.json found!")
        print("Run: python3 discover_tweets.py first")
        return
    
    with open(tweets_file) as f:
        tweets = json.load(f)
    
    print(f"📤 Uploading {len(tweets)} tweets to Railway backend...")
    print(f"🌐 Backend: {BACKEND_URL}\n")
    
    # Start a discovery job first
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # Create discovery job
            resp = await client.post(
                f"{BACKEND_URL}/api/v1/discovery/start",
                json={"query": "AI agent security", "max_results": len(tweets)}
            )
            
            if resp.status_code == 200:
                job_data = resp.json()
                print(f"✅ Discovery job created: {job_data.get('job_id')}")
            else:
                print(f"⚠️  Status: {resp.status_code}")
                print(f"Response: {resp.text}")
                
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(upload_tweets())
