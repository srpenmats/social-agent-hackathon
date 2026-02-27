"""
Twitter Discovery and Engagement Service using twclaw CLI.

This integrates the native Twitter X API skill for OpenClaw.
"""

import os
import asyncio
import subprocess
import json
from datetime import datetime, timezone
from typing import List, Dict, Optional
from db.connection import get_supabase_admin


class TwitterDiscoveryService:
    """Discover relevant tweets and generate comment recommendations using twclaw."""
    
    def __init__(self):
        self.bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
        if not self.bearer_token:
            raise ValueError("TWITTER_BEARER_TOKEN not set")
        
        self.db = get_supabase_admin()
    
    def _run_twclaw(self, args: List[str]) -> Dict:
        """
        Execute twclaw command and return parsed JSON output.
        
        Args:
            args: Command arguments (e.g., ['search', 'query', '-n', '10', '--json'])
        
        Returns:
            Parsed JSON output from twclaw
        """
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
            context: Optional context for filtering
        
        Returns:
            List of tweet dictionaries with ALL metrics
        """
        # Build search query with context
        full_query = query
        if context:
            full_query = f"{query} {context}"
        
        # Execute twclaw search
        results = await asyncio.to_thread(
            self._run_twclaw,
            ['search', full_query, '-n', str(max_results), '--json']
        )
        
        return results
    
    async def discover_by_query(
        self,
        query: str,
        max_results: int = 20,
        min_engagement: int = 50
    ) -> List[Dict]:
        """
        Discover tweets by query with minimum engagement filter.
        
        Args:
            query: Search query
            max_results: Maximum number of results
            min_engagement: Minimum likes for quality filtering
        
        Returns:
            List of tweet dictionaries filtered by engagement
        """
        # Search for tweets
        tweets = await self.search_tweets(query, max_results)
        
        # Filter by minimum engagement
        filtered_tweets = [
            tweet for tweet in tweets
            if tweet.get("likes", 0) >= min_engagement
        ]
        
        return filtered_tweets
    
    async def get_tweet_details(self, tweet_id: str) -> Dict:
        """
        Get full details for a single tweet including all metrics.
        
        Args:
            tweet_id: Tweet ID or URL
        
        Returns:
            Tweet dictionary with full metrics
        """
        result = await asyncio.to_thread(
            self._run_twclaw,
            ['read', tweet_id, '--json']
        )
        
        return result
    
    async def post_reply(self, tweet_id: str, text: str) -> Dict:
        """
        Post a reply to a tweet.
        
        Args:
            tweet_id: Tweet ID or URL to reply to
            text: Reply text
        
        Returns:
            Posted reply details with URL
        """
        result = await asyncio.to_thread(
            self._run_twclaw,
            ['reply', tweet_id, text, '--json']
        )
        
        return result
    
    async def post_tweet(self, text: str) -> Dict:
        """
        Post a new tweet.
        
        Args:
            text: Tweet text
        
        Returns:
            Posted tweet details with URL
        """
        result = await asyncio.to_thread(
            self._run_twclaw,
            ['tweet', text, '--json']
        )
        
        return result
    
    async def verify_credentials(self) -> Dict:
        """
        Verify Twitter API credentials.
        
        Returns:
            Authentication status and user info
        """
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
                "quotes": tweet.get("quotes", 0),
                "bookmarks": tweet.get("bookmarks", 0),
                "impressions": tweet.get("impressions", 0),
                "status": "discovered",
                "discovered_at": tweet.get("created_at")
            }
            
            # Check if post already exists
            existing = self.db.table("discovered_posts").select("id").eq("post_id", record["post_id"]).execute()
            if existing.data:
                # Update existing
                self.db.table("discovered_posts").update(record).eq("post_id", record["post_id"]).execute()
            else:
                # Insert new
                self.db.table("discovered_posts").insert(record).execute()
            stored_count += 1
        
        return {
            "success": True,
            "query": query,
            "context": context,
            "found": len(tweets),
            "stored": stored_count,
            "tweets": tweets[:5]  # Return first 5 as preview
        }
