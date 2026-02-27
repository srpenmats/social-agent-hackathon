#!/usr/bin/env python3
"""Test Twitter API credentials with a simple search."""

import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

import httpx
from dotenv import load_dotenv

# Load environment variables
backend_env = project_root / "backend" / ".env"
print(f"📁 Loading .env from: {backend_env}")
print(f"📁 File exists: {backend_env.exists()}")
load_dotenv(backend_env)

TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")

if not TWITTER_BEARER_TOKEN:
    print("❌ TWITTER_BEARER_TOKEN not found in .env")
    sys.exit(1)


async def test_twitter_search():
    """Test Twitter API v2 search endpoint."""
    print("🔍 Testing Twitter API v2 search...")
    print(f"Bearer token: {TWITTER_BEARER_TOKEN[:20]}...")

    async with httpx.AsyncClient() as client:
        try:
            # Recent search for "AI agent security" (limited to 10 results)
            response = await client.get(
                "https://api.twitter.com/2/tweets/search/recent",
                params={
                    "query": "AI agent security -is:retweet lang:en",
                    "max_results": 10,
                    "tweet.fields": "created_at,public_metrics,author_id",
                },
                headers={
                    "Authorization": f"Bearer {TWITTER_BEARER_TOKEN}"
                },
                timeout=30.0,
            )

            print(f"\n📊 Status Code: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                tweets = data.get("data", [])
                print(f"✅ Success! Found {len(tweets)} tweets")
                
                if tweets:
                    print("\n📝 Sample tweets:")
                    for i, tweet in enumerate(tweets[:3], 1):
                        text = tweet.get("text", "")[:100]
                        metrics = tweet.get("public_metrics", {})
                        likes = metrics.get("like_count", 0)
                        print(f"\n{i}. {text}...")
                        print(f"   👍 {likes} likes")
                else:
                    print("⚠️  No tweets found (search may be too specific)")
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"Response: {response.text[:500]}")

        except Exception as e:
            print(f"❌ Exception: {type(e).__name__}: {e}")


if __name__ == "__main__":
    asyncio.run(test_twitter_search())
