"""
Twitter Discovery and Engagement Service using x-twitter skill approach.

This integrates real Twitter API calls with your dashboard backend.
"""

import os
import asyncio
from datetime import datetime, timezone
from typing import List, Dict, Optional
import httpx
from db.connection import get_supabase_admin


class TwitterDiscoveryService:
    """Discover relevant tweets and generate comment recommendations."""
    
    def __init__(self):
        self.bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
        if not self.bearer_token:
            raise ValueError("TWITTER_BEARER_TOKEN not set")
        
        self.base_url = "https://api.twitter.com/2"
        self.headers = {
            "Authorization": f"Bearer {self.bearer_token}",
            "Content-Type": "application/json"
        }
        self.db = get_supabase_admin()
    
    async def search_tweets(
        self,
        query: str,
        max_results: int = 20,
        context: Optional[str] = None
    ) -> List[Dict]:
        """
        Search for relevant tweets based on query and optional context.
        
        Args:
            query: Search query (e.g., "AI agent security")
            max_results: Number of tweets to return (max 100)
            context: Optional context for filtering (e.g., "cybersecurity", "finance")
        
        Returns:
            List of tweet dictionaries with metadata
        """
        # Build search query with context
        full_query = query
        if context:
            full_query = f"{query} {context}"
        
        # Add filters for engagement quality
        full_query += " -is:retweet lang:en"
        
        params = {
            "query": full_query,
            "max_results": min(max_results, 100),
            "tweet.fields": "created_at,public_metrics,author_id,conversation_id,text",
            "expansions": "author_id",
            "user.fields": "username,name,public_metrics,verified"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/tweets/search/recent",
                headers=self.headers,
                params=params,
                timeout=30.0
            )
            
            if response.status_code != 200:
                raise Exception(f"Twitter API error: {response.status_code} - {response.text}")
            
            data = response.json()
            
            # Parse results
            tweets = data.get("data", [])
            users = {u["id"]: u for u in data.get("includes", {}).get("users", [])}
            
            results = []
            for tweet in tweets:
                author_id = tweet.get("author_id")
                author = users.get(author_id, {})
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
                    "created_at": tweet.get("created_at"),
                    "conversation_id": tweet.get("conversation_id"),
                    "url": f"https://twitter.com/{author.get('username', 'i')}/status/{tweet['id']}"
                })
            
            return results
    
    async def discover_and_store(
        self,
        query: str,
        max_results: int = 20,
        context: Optional[str] = None
    ) -> Dict:
        """
        Discover tweets and store them in discovered_posts table.
        
        Returns:
            Dictionary with discovery stats
        """
        tweets = await self.search_tweets(query, max_results, context)
        
        stored_count = 0
        for tweet in tweets:
            # Store in discovered_posts table
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
                "status": "discovered",
                "discovered_at": tweet["created_at"],
                "metadata": {
                    "author_verified": tweet["author_verified"],
                    "author_followers": tweet["author_followers"],
                    "conversation_id": tweet["conversation_id"],
                    "discovery_query": query,
                    "discovery_context": context
                }
            }
            
            self.db.table("discovered_posts").upsert(record, on_conflict="post_id").execute()
            stored_count += 1
        
        return {
            "success": True,
            "query": query,
            "context": context,
            "found": len(tweets),
            "stored": stored_count,
            "tweets": tweets[:5]  # Return first 5 as preview
        }
    
    async def get_thread_context(self, tweet_id: str) -> List[Dict]:
        """
        Get the full conversation thread for a tweet.
        Useful for understanding context before replying.
        """
        # Get the original tweet first to find conversation_id
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/tweets/{tweet_id}",
                headers=self.headers,
                params={
                    "tweet.fields": "conversation_id,created_at,public_metrics,text",
                    "expansions": "author_id",
                    "user.fields": "username,name"
                },
                timeout=30.0
            )
            
            if response.status_code != 200:
                raise Exception(f"Twitter API error: {response.status_code}")
            
            data = response.json()
            tweet = data.get("data", {})
            conversation_id = tweet.get("conversation_id")
            
            if not conversation_id:
                return [tweet]
            
            # Get full thread
            thread_response = await client.get(
                f"{self.base_url}/tweets/search/recent",
                headers=self.headers,
                params={
                    "query": f"conversation_id:{conversation_id}",
                    "max_results": 100,
                    "tweet.fields": "created_at,public_metrics,author_id,text",
                    "expansions": "author_id",
                    "user.fields": "username,name"
                },
                timeout=30.0
            )
            
            thread_data = thread_response.json()
            return thread_data.get("data", [])
    
    def score_engagement_potential(self, tweet: Dict) -> int:
        """
        Score a tweet's engagement potential (0-100).
        Higher scores mean better opportunity to engage.
        
        Factors:
        - Author follower count
        - Existing engagement (likes, retweets, replies)
        - Recency
        - Verification status
        """
        score = 50  # Base score
        
        # Author influence (0-20 points)
        followers = tweet.get("author_followers", 0)
        if followers > 1_000_000:
            score += 20
        elif followers > 100_000:
            score += 15
        elif followers > 10_000:
            score += 10
        elif followers > 1_000:
            score += 5
        
        # Existing engagement (0-15 points)
        engagement = tweet.get("likes", 0) + tweet.get("retweets", 0) * 2
        if engagement > 10_000:
            score += 15
        elif engagement > 1_000:
            score += 10
        elif engagement > 100:
            score += 5
        
        # Reply activity (0-10 points)
        replies = tweet.get("replies", 0)
        if replies > 100:
            score += 10
        elif replies > 20:
            score += 7
        elif replies > 5:
            score += 4
        
        # Verification bonus (5 points)
        if tweet.get("author_verified", False):
            score += 5
        
        return min(score, 100)
    
    def extract_key_topics(self, tweet_text: str) -> List[str]:
        """Extract key topics/hashtags from tweet text."""
        import re
        
        # Extract hashtags
        hashtags = re.findall(r'#\w+', tweet_text)
        
        # Extract key terms (simple keyword matching)
        keywords = [
            "AI", "agent", "security", "automation", "cybersecurity",
            "privacy", "authentication", "vulnerability", "threat",
            "machine learning", "neural network", "LLM", "GPT"
        ]
        
        found_keywords = [kw for kw in keywords if kw.lower() in tweet_text.lower()]
        
        return list(set(hashtags + found_keywords))


# Singleton instance
_twitter_service = None

def get_twitter_service() -> TwitterDiscoveryService:
    """Get or create TwitterDiscoveryService instance."""
    global _twitter_service
    if _twitter_service is None:
        _twitter_service = TwitterDiscoveryService()
    return _twitter_service
