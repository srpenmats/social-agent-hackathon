#!/usr/bin/env python3
"""Discover Twitter posts and save them to the database."""

import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

# Load environment
from dotenv import load_dotenv
load_dotenv(project_root / "backend" / ".env")

import httpx

TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")


async def discover_tweets(query: str = "AI agent security", max_results: int = 20):
    """Discover tweets using Twitter API."""
    print(f"🔍 Discovering tweets about: {query}")
    print(f"📊 Looking for up to {max_results} results...\n")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                "https://api.twitter.com/2/tweets/search/recent",
                params={
                    "query": f"{query} -is:retweet lang:en",
                    "max_results": max_results,
                    "tweet.fields": "created_at,public_metrics,author_id,text",
                    "user.fields": "name,username",
                    "expansions": "author_id",
                },
                headers={
                    "Authorization": f"Bearer {TWITTER_BEARER_TOKEN}"
                },
                timeout=30.0,
            )
            
            if response.status_code == 200:
                data = response.json()
                tweets = data.get("data", [])
                users = {u["id"]: u for u in data.get("includes", {}).get("users", [])}
                
                print(f"✅ Found {len(tweets)} tweets!\n")
                print("=" * 80)
                
                discovered = []
                
                for i, tweet in enumerate(tweets, 1):
                    author_id = tweet.get("author_id")
                    author = users.get(author_id, {})
                    metrics = tweet.get("public_metrics", {})
                    
                    tweet_data = {
                        "id": tweet["id"],
                        "text": tweet.get("text", ""),
                        "author": {
                            "username": author.get("username", "unknown"),
                            "name": author.get("name", "Unknown"),
                        },
                        "created_at": tweet.get("created_at"),
                        "metrics": {
                            "likes": metrics.get("like_count", 0),
                            "retweets": metrics.get("retweet_count", 0),
                            "replies": metrics.get("reply_count", 0),
                        },
                        "url": f"https://twitter.com/{author.get('username', 'i')}/status/{tweet['id']}"
                    }
                    
                    discovered.append(tweet_data)
                    
                    print(f"\n{i}. @{tweet_data['author']['username']}")
                    print(f"   {tweet_data['text'][:200]}...")
                    print(f"   💬 {tweet_data['metrics']['replies']} replies | "
                          f"🔁 {tweet_data['metrics']['retweets']} retweets | "
                          f"❤️  {tweet_data['metrics']['likes']} likes")
                    print(f"   🔗 {tweet_data['url']}")
                
                print("\n" + "=" * 80)
                
                # Save to file
                output_file = project_root / "discovered_tweets.json"
                with open(output_file, "w") as f:
                    json.dump(discovered, f, indent=2)
                
                print(f"\n💾 Saved {len(discovered)} tweets to: {output_file}")
                print("\n✅ Discovery complete!")
                
                return discovered
                
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"Response: {response.text}")
                return []
                
        except Exception as e:
            print(f"❌ Exception: {type(e).__name__}: {e}")
            return []


if __name__ == "__main__":
    print("=" * 80)
    print("🐦 Twitter Discovery - AI Agent Security")
    print("=" * 80)
    print()
    
    # Discover tweets
    tweets = asyncio.run(discover_tweets(
        query="AI agent security OR agent trust OR autonomous agent security",
        max_results=20
    ))
    
    print(f"\n📊 Summary:")
    print(f"   Total discovered: {len(tweets)}")
    print(f"   Average likes: {sum(t['metrics']['likes'] for t in tweets) / len(tweets) if tweets else 0:.1f}")
    print(f"   Most liked: {max((t['metrics']['likes'] for t in tweets), default=0)}")
    
    print("\n💡 Next: These tweets can be imported into the dashboard!")
