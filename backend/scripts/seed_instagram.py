"""Seed the local DB with finance-related Instagram Reels for Cash Kitty to engage with.

Usage:
    python -m backend.scripts.seed_instagram
"""

from __future__ import annotations

import json
import random
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "db" / "local.db"


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


# ---------------------------------------------------------------------------
# Finance Instagram Reels / Posts seed data
# ---------------------------------------------------------------------------

INSTAGRAM_REELS = [
    {
        "creator": "@personalfinanceclub",
        "video_url": "https://www.instagram.com/personalfinanceclub/reels/",
        "description": "The 50/30/20 rule changed my life. 50% needs, 30% wants, 20% savings. Here's how I actually stick to it every month.",
        "hashtags": ["#budgeting", "#personalfinance", "#moneytips", "#savingmoney", "#financialliteracy"],
        "likes": 48200,
        "comments_count": 1340,
        "shares": 8900,
        "classification": "finance-educational",
    },
    {
        "creator": "@humphreytalks",
        "video_url": "https://www.instagram.com/humphreytalks/reels/",
        "description": "Stop saving money in your checking account. Here are 3 high-yield savings accounts paying 5%+ APY right now.",
        "hashtags": ["#highyieldsavings", "#savemoney", "#financetips", "#investing101", "#money"],
        "likes": 92400,
        "comments_count": 3200,
        "shares": 15600,
        "classification": "finance-educational",
    },
    {
        "creator": "@herfirst100k",
        "video_url": "https://www.instagram.com/herfirst100k/reels/",
        "description": "I paid off $100k in student loans in 3 years. Here's the exact strategy I used and what I'd do differently.",
        "hashtags": ["#debtfree", "#studentloans", "#debtpayoff", "#financialfreedom", "#personalfinance"],
        "likes": 156000,
        "comments_count": 5400,
        "shares": 22300,
        "classification": "finance-educational",
    },
    {
        "creator": "@callowaycook",
        "video_url": "https://www.instagram.com/callowaycook/reels/",
        "description": "Meal prep Sunday but make it budget-friendly. All 5 lunches for $22. Your wallet and your body will thank you.",
        "hashtags": ["#budgetmeals", "#mealprep", "#savemoney", "#frugalliving", "#moneysaving"],
        "likes": 67800,
        "comments_count": 2100,
        "shares": 11200,
        "classification": "lifestyle-finance",
    },
    {
        "creator": "@investwithqai",
        "video_url": "https://www.instagram.com/investwithqai/reels/",
        "description": "The S&P 500 just hit another all-time high. If you invested $100/month starting 5 years ago, here's what you'd have today.",
        "hashtags": ["#investing", "#sp500", "#stockmarket", "#passiveincome", "#compoundinterest"],
        "likes": 134500,
        "comments_count": 4800,
        "shares": 19700,
        "classification": "finance-educational",
    },
    {
        "creator": "@sidehustlequeen",
        "video_url": "https://www.instagram.com/sidehustlequeen/reels/",
        "description": "5 side hustles that actually pay $2k+/month. No selling courses. No MLMs. Just real businesses I've tried myself.",
        "hashtags": ["#sidehustle", "#extraincome", "#makemoney", "#entrepreneurship", "#financialfreedom"],
        "likes": 203000,
        "comments_count": 7200,
        "shares": 31400,
        "classification": "finance-educational",
    },
    {
        "creator": "@creditcardking",
        "video_url": "https://www.instagram.com/creditcardking/reels/",
        "description": "I traveled to Japan for FREE using credit card points. Here's my exact strategy for maximizing travel rewards.",
        "hashtags": ["#creditcards", "#travelrewards", "#pointsandmiles", "#freetravel", "#creditcardpoints"],
        "likes": 87600,
        "comments_count": 2900,
        "shares": 14500,
        "classification": "finance-lifestyle",
    },
    {
        "creator": "@thefinancialdiet",
        "video_url": "https://www.instagram.com/thefinancialdiet/reels/",
        "description": "3 money habits that are keeping you broke without you even realizing it. Number 2 hit different for me.",
        "hashtags": ["#moneyhabits", "#financialliteracy", "#personalfinance", "#moneymanagement", "#budgeting"],
        "likes": 112300,
        "comments_count": 3800,
        "shares": 16900,
        "classification": "finance-educational",
    },
    {
        "creator": "@genzmoney",
        "video_url": "https://www.instagram.com/genzmoney/reels/",
        "description": "Your 401k match is literally free money. If your employer offers 6% match and you're not taking it, you're leaving $3k+ on the table every year.",
        "hashtags": ["#401k", "#retirement", "#investing", "#financetips", "#genzfinance"],
        "likes": 78400,
        "comments_count": 2600,
        "shares": 12800,
        "classification": "finance-educational",
    },
    {
        "creator": "@themoneycouple",
        "video_url": "https://www.instagram.com/themoneycouple/reels/",
        "description": "We saved $40k for our wedding without going into debt. Here's our complete timeline and budget breakdown.",
        "hashtags": ["#weddingbudget", "#savingmoney", "#couplegoals", "#financeplanning", "#budgeting"],
        "likes": 95200,
        "comments_count": 3100,
        "shares": 13700,
        "classification": "lifestyle-finance",
    },
    {
        "creator": "@mikirai_money",
        "video_url": "https://www.instagram.com/mikirai_money/reels/",
        "description": "The truth about Roth IRA vs Traditional IRA that nobody explains simply. Let me break it down in 60 seconds.",
        "hashtags": ["#rothira", "#investing", "#retirement", "#financialliteracy", "#taxes"],
        "likes": 145000,
        "comments_count": 4200,
        "shares": 20100,
        "classification": "finance-educational",
    },
    {
        "creator": "@richgirlpenny",
        "video_url": "https://www.instagram.com/richgirlpenny/reels/",
        "description": "Cash stuffing my February budget envelopes. $2,800 total. Watch how I organize every dollar.",
        "hashtags": ["#cashstuffing", "#budgeting", "#envelopesystem", "#savemoney", "#financeaesthetic"],
        "likes": 234000,
        "comments_count": 6800,
        "shares": 28500,
        "classification": "finance-educational",
    },
]


# Cash Kitty draft comments in brand voice
DRAFT_COMMENTS = [
    {
        "text": "ok the cash stuffing aesthetic is immaculate but the DISCIPLINE is what's really impressive here. kitty takes notes",
        "risk_score": 12,
        "reasoning": "Low risk: supportive commentary, no financial claims, on-brand casual tone",
        "classification": "finance-educational",
    },
    {
        "text": "high-yield savings hitting 5%+ while most people still have their money sitting in a 0.01% account is actually wild. this is the content that changes lives fr",
        "risk_score": 22,
        "reasoning": "Low-moderate risk: references specific rates but doesn't recommend specific products",
        "classification": "finance-educational",
    },
    {
        "text": "paying off $100k in 3 years is genuinely insane dedication. this is proof that a plan + consistency beats everything",
        "risk_score": 8,
        "reasoning": "Very low risk: encouraging comment, no financial advice given",
        "classification": "finance-educational",
    },
    {
        "text": "the 50/30/20 rule is great but honestly the hardest part is being real about what's a 'need' vs a 'want'. that daily oat milk latte is testing me",
        "risk_score": 10,
        "reasoning": "Very low risk: relatable humor about budgeting, no financial claims",
        "classification": "finance-educational",
    },
    {
        "text": "compound interest really is the 8th wonder of the world. $100/month adds up way faster than people think when you start early",
        "risk_score": 28,
        "reasoning": "Moderate risk: references compound interest benefits, could be seen as investment encouragement",
        "classification": "finance-educational",
    },
    {
        "text": "finally someone keeping it real about side hustles. no 'passive income' fairy tales, just actual work that pays. respect",
        "risk_score": 14,
        "reasoning": "Low risk: positive engagement with content creator, no financial claims",
        "classification": "finance-educational",
    },
]


def seed() -> None:
    """Insert Instagram finance Reels into the local DB."""
    conn = get_db()

    # Ensure the Instagram platform row exists
    existing = conn.execute("SELECT id FROM platforms WHERE name = 'instagram'").fetchone()
    if not existing:
        conn.execute(
            "INSERT INTO platforms (name, status, auth_method, session_health, workers_status, connected_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            ("instagram", "connected", "graph_api", "healthy",
             json.dumps({"discovery": True, "execution": True, "analytics": True}),
             datetime.now(timezone.utc).isoformat()),
        )
        conn.commit()

    # Clear previous Instagram seed data (order matters for FK constraints)
    conn.execute("DELETE FROM engagement_metrics WHERE engagement_id IN (SELECT id FROM engagements WHERE platform = 'instagram')")
    conn.execute("DELETE FROM engagements WHERE platform = 'instagram'")
    conn.execute("DELETE FROM review_queue WHERE video_id IN (SELECT id FROM discovered_videos WHERE platform = 'instagram')")
    conn.execute("DELETE FROM risk_scores WHERE comment_id IN (SELECT id FROM generated_comments WHERE video_id IN (SELECT id FROM discovered_videos WHERE platform = 'instagram'))")
    conn.execute("DELETE FROM generated_comments WHERE video_id IN (SELECT id FROM discovered_videos WHERE platform = 'instagram')")
    conn.execute("DELETE FROM discovered_videos WHERE platform = 'instagram'")
    conn.commit()

    # Insert discovered Reels
    video_ids = []
    for reel in INSTAGRAM_REELS:
        cursor = conn.execute(
            "INSERT INTO discovered_videos "
            "(platform, video_url, creator, description, hashtags, likes, comments_count, shares, classification, status, engaged) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                "instagram",
                reel["video_url"],
                reel["creator"],
                reel["description"],
                json.dumps(reel["hashtags"]),
                reel["likes"],
                reel["comments_count"],
                reel["shares"],
                reel["classification"],
                random.choice(["new", "engaged", "engaged", "new"]),
                random.choice([True, False]),
            ),
        )
        video_ids.append(cursor.lastrowid)

    # Insert some engagements (already-posted comments)
    engaged_videos = random.sample(video_ids, min(4, len(video_ids)))
    posted_comments = [
        "this is the financial literacy content we need more of. the kitty approves",
        "ngl every time i see these breakdowns i learn something new. the internet is undefeated sometimes",
        "ok but why don't they teach this in school?? saving this for later",
        "the way this actually makes sense when you explain it like this. more of this pls",
    ]
    for vid_id, comment_text in zip(engaged_videos, posted_comments):
        cursor = conn.execute(
            "INSERT INTO generated_comments "
            "(video_id, text, approach, char_count, selected) "
            "VALUES (?, ?, ?, ?, 1)",
            (vid_id, comment_text, "witty", len(comment_text)),
        )
        comment_id = cursor.lastrowid

        risk_score = random.randint(5, 20)
        cursor = conn.execute(
            "INSERT INTO engagements "
            "(platform, video_id, comment_id, comment_text, risk_score, approval_path, posted_at, status) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            ("instagram", vid_id, comment_id, comment_text, risk_score, "auto",
             datetime.now(timezone.utc).isoformat(), "posted"),
        )
        engagement_id = cursor.lastrowid

        conn.execute(
            "INSERT INTO engagement_metrics "
            "(engagement_id, likes, replies, impressions) "
            "VALUES (?, ?, ?, ?)",
            (engagement_id, random.randint(5, 120), random.randint(0, 15), random.randint(500, 8000)),
        )

    # Insert review_queue items (pending draft comments)
    now = datetime.now(timezone.utc).isoformat()
    available_videos = [v for v in video_ids if v not in engaged_videos]
    for i, draft in enumerate(DRAFT_COMMENTS):
        vid_id = available_videos[i % len(available_videos)] if available_videos else video_ids[i % len(video_ids)]
        conn.execute(
            "INSERT INTO review_queue "
            "(video_id, proposed_text, risk_score, risk_reasoning, classification, queued_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (vid_id, draft["text"], draft["risk_score"],
             draft["reasoning"], draft["classification"], now),
        )

    conn.commit()

    # Print summary
    video_count = conn.execute("SELECT COUNT(*) FROM discovered_videos WHERE platform = 'instagram'").fetchone()[0]
    engagement_count = conn.execute("SELECT COUNT(*) FROM engagements WHERE platform = 'instagram'").fetchone()[0]
    review_count = conn.execute("SELECT COUNT(*) FROM review_queue WHERE decision IS NULL AND video_id IN (SELECT id FROM discovered_videos WHERE platform = 'instagram')").fetchone()[0]

    print(f"\nInstagram seed complete:")
    print(f"  discovered_videos (instagram): {video_count}")
    print(f"  engagements (instagram):       {engagement_count}")
    print(f"  review_queue pending:          {review_count}")

    conn.close()


def main() -> None:
    print("Seeding Instagram finance Reels...")
    seed()
    print("Done!")


if __name__ == "__main__":
    main()
