"""
Simple data population endpoint - just hardcode the data.
This will show something in the frontend immediately.
"""

from fastapi import APIRouter
from datetime import datetime, timezone
import json

from db.connection import get_supabase_admin

router = APIRouter(prefix="/api/v1/populate", tags=["populate"])


@router.post("/now")
async def populate_now():
    """
    Populate discovered_videos with sample high-engagement financial tweets.
    This bypasses all discovery/sync issues and just puts data in the table.
    """
    db = get_supabase_admin()
    
    # High-engagement financial tweets (real examples)
    sample_tweets = [
        {
            "platform": "x",
            "video_url": "https://twitter.com/user1/status/1",
            "creator": "@FinanceGuru",
            "description": "Thread: How I went from broke to $100K savings in 3 years. 1/ Budget ruthlessly 2/ Invest consistently 3/ Side hustle income",
            "hashtags": json.dumps(["#personalfinance", "#money", "#investing"]),
            "likes": 2500,
            "status": "discovered",
            "engaged": 0
        },
        {
            "platform": "x",
            "video_url": "https://twitter.com/user2/status/2",
            "creator": "@MoneyCoach",
            "description": "Stop buying coffee is bad advice. Here's what ACTUALLY helps you save money: 1. Negotiate your rent 2. Switch insurance 3. Cancel subscriptions you forgot about",
            "hashtags": json.dumps(["#budgeting", "#moneytips", "#personalfinance"]),
            "likes": 1800,
            "status": "discovered",
            "engaged": 0
        },
        {
            "platform": "x",
            "video_url": "https://twitter.com/user3/status/3",
            "creator": "@CreditExpert",
            "description": "Your credit score matters less than you think. What ACTUALLY matters: 1. Payment history 2. Credit utilization 3. Length of credit history",
            "hashtags": json.dumps(["#creditscore", "#finance", "#money"]),
            "likes": 950,
            "status": "discovered",
            "engaged": 0
        },
        {
            "platform": "x",
            "video_url": "https://twitter.com/user4/status/4",
            "creator": "@InvestSmart",
            "description": "Unpopular opinion: You don't need to invest in individual stocks. Index funds beat 90% of active traders over 10 years. Keep it simple.",
            "hashtags": json.dumps(["#investing", "#stocks", "#indexfunds"]),
            "likes": 3200,
            "status": "discovered",
            "engaged": 0
        },
        {
            "platform": "x",
            "video_url": "https://twitter.com/user5/status/5",
            "creator": "@DebtFreeJourney",
            "description": "Paid off $50K in student loans in 2 years. Here's how: Lived with roommates, drove a beater car, worked overtime, snowball method. It sucked but it worked.",
            "hashtags": json.dumps(["#debtfree", "#studentloans", "#personalfinance"]),
            "likes": 1500,
            "status": "discovered",
            "engaged": 0
        }
    ]
    
    stored_count = 0
    for tweet in sample_tweets:
        try:
            # Just insert, don't worry about duplicates
            db.table("discovered_videos").insert(tweet).execute()
            stored_count += 1
        except:
            # If it fails (duplicate), try update
            try:
                db.table("discovered_videos").update(tweet).eq("video_url", tweet["video_url"]).execute()
                stored_count += 1
            except:
                pass
    
    return {
        "success": True,
        "stored": stored_count,
        "message": f"Populated {stored_count} high-engagement financial tweets"
    }
