"""
Twitter Discovery and Engagement Service with twclaw/httpx fallback.

Tries twclaw first (native skill), falls back to httpx if unavailable.
"""

import os
import asyncio
import subprocess
import json
import shutil
from datetime import datetime, timezone
from typing import List, Dict, Optional
import httpx
from db.connection import get_supabase_admin


class TwitterDiscoveryService:
    """Discover relevant tweets with automatic twclaw/httpx fallback."""
    
    def __init__(self):
        self.bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
        if not self.bearer_token:
            raise ValueError("TWITTER_BEARER_TOKEN not set")
        
        self.db = get_supabase_admin()
        
        # Check if twclaw is available
        self.has_twclaw = shutil.which("twclaw") is not None
        
        if not self.has_twclaw:
            print("⚠️ twclaw not found, using httpx fallback")
    
    def _run_twclaw(self, args: List[str]) -> Dict:
        """Execute twclaw command and return parsed JSON output."""
        env = os.environ.copy()
        env['TWITTER_BEARER_TOKEN'] = self.bearer_token
        
        try:
            result = subprocess.run(
                ['twclaw'] + args,
                capture_output=True,
                text=True,
                env=env,
                timeout=30
            )
            
            if result.returncode != 0:
                raise Exception(f"twclaw error: {result.stderr}")
            
            return json.loads(result.stdout)
        except subprocess.TimeoutExpired:
            raise Exception("twclaw command timed out")
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse twclaw output: {e}")
    
    async def _search_httpx_fallback(self, query: str, max_results: int) -> List[Dict]:
        """Fallback to httpx if twclaw not available."""
        headers = {
            "Authorization": f"Bearer {self.bearer_token}",
            "Content-Type": "application/json"
        }
        
        params = {
            "query": f"{query} -is:retweet lang:en",
            "max_results": min(max_results, 100),
            "tweet.fields": "created_at,public_metrics,author_id,conversation_id,text",
            "expansions": "author_id",
            "user.fields": "username,name,public_metrics,verified"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.twitter.com/2/tweets/search/recent",
                headers=headers,
                params=params,
                timeout=30.0
            )
            
            if response.status_code != 200:
                raise Exception(f"Twitter API error: {response.status_code}")
            
            data = response.json()
            tweets = data.get("data", [])
            users = {u["id"]: u for u in data.get("includes", {}).get("users", [])}
            
            results = []
            for tweet in tweets:
                author = users.get(tweet.get("author_id"), {})
                metrics = tweet.get("public_metrics", {})
                
                results.append({
                    "id": tweet["id"],
                    "text": tweet.get("text", ""),
                    "author_username": author.get("username", "unknown"),
                    "author_name": author.get("name", "Unknown"),
                    "author_verified": author.get("verified", False),
                    "author_followers": author.get("public_metrics", {}).get("followers_count", 0),
                    "likes": metrics.get("like_count", 0),
                    "retweets": metrics.get("retweet_count", 0),
                    "replies": metrics.get("reply_count", 0),
                    "quotes": metrics.get("quote_count", 0),
                    "bookmarks": metrics.get("bookmark_count", 0),
                    "impressions": metrics.get("impression_count", 0),
                    "created_at": tweet.get("created_at"),
                    "url": f"https://twitter.com/{author.get('username', 'i')}/status/{tweet['id']}"
                })
            
            return results
    
    async def search_tweets(
        self,
        query: str,
        max_results: int = 20,
        context: Optional[str] = None
    ) -> List[Dict]:
        """
        Search for tweets. Uses twclaw if available, httpx otherwise.
        """
        full_query = query
        if context:
            full_query = f"{query} {context}"
        
        if self.has_twclaw:
            try:
                results = await asyncio.to_thread(
                    self._run_twclaw,
                    ['search', full_query, '-n', str(max_results), '--json']
                )
                return results
            except Exception as e:
                print(f"⚠️ twclaw failed ({e}), falling back to httpx")
                return await self._search_httpx_fallback(full_query, max_results)
        else:
            return await self._search_httpx_fallback(full_query, max_results)
    
    async def discover_by_query(
        self,
        query: str,
        max_results: int = 20,
        min_engagement: int = 50
    ) -> List[Dict]:
        """
        Discover tweets. 
        
        Changed logic: Don't hard-filter by min_engagement (would return 0 posts).
        Instead, return ALL posts and let Smart Discovery scoring handle ranking.
        Higher engagement posts will naturally score higher.
        """
        tweets = await self.search_tweets(query, max_results)
        
        # Don't filter out low-engagement posts - just return everything
        # Smart Discovery will score them and rank by relevance + engagement
        return tweets
    
    async def get_tweet_details(self, tweet_id: str) -> Dict:
        """Get full details for a single tweet."""
        if self.has_twclaw:
            result = await asyncio.to_thread(
                self._run_twclaw,
                ['read', tweet_id, '--json']
            )
            return result
        else:
            raise Exception("Tweet details requires twclaw (not available)")
    
    async def post_reply(self, tweet_id: str, text: str) -> Dict:
        """Post a reply to a tweet."""
        if self.has_twclaw:
            result = await asyncio.to_thread(
                self._run_twclaw,
                ['reply', tweet_id, text, '--json']
            )
            return result
        else:
            raise Exception("Posting requires twclaw (not available)")
    
    async def post_tweet(self, text: str) -> Dict:
        """Post a new tweet."""
        if self.has_twclaw:
            result = await asyncio.to_thread(
                self._run_twclaw,
                ['tweet', text, '--json']
            )
            return result
        else:
            raise Exception("Posting requires twclaw (not available)")
    
    async def verify_credentials(self) -> Dict:
        """Verify Twitter API credentials."""
        try:
            result = await asyncio.to_thread(
                self._run_twclaw,
                ['auth-check']
            )
            return {"authenticated": True, "info": result}
        except Exception as e:
            return {"authenticated": False, "error": str(e)}
    
    async def discover_and_store(
        self,
        query: str,
        max_results: int = 20,
        context: Optional[str] = None
    ) -> Dict:
        """Discover tweets and store them in discovered_posts table."""
        tweets = await self.search_tweets(query, max_results, context)
        
        stored_count = 0
        for tweet in tweets:
            record = {
                "platform": "x",
                "post_id": tweet["id"],
                "post_url": tweet["url"],
                "post_text": tweet["text"],
                "author_username": tweet["author_username"],
                "author_name": tweet["author_name"],
                "likes": tweet["likes"],
                "retweets": tweet["retweets"],
                "replies": tweet["replies"],
                "quotes": tweet.get("quotes", 0),
                "bookmarks": tweet.get("bookmarks", 0),
                "impressions": tweet.get("impressions", 0),
                "status": "discovered",
                "discovered_at": tweet.get("created_at")
            }
            
            existing = self.db.table("discovered_posts").select("id").eq("post_id", record["post_id"]).execute()
            if existing.data:
                self.db.table("discovered_posts").update(record).eq("post_id", record["post_id"]).execute()
            else:
                self.db.table("discovered_posts").insert(record).execute()
            stored_count += 1
        
        return {
            "success": True,
            "query": query,
            "context": context,
            "found": len(tweets),
            "stored": stored_count,
            "tweets": tweets[:5]
        }


def get_twitter_service() -> TwitterDiscoveryService:
    return TwitterDiscoveryService()
