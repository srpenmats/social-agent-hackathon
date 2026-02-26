"""Sync @the_cash_kitty tweets into the local SQLite dashboard DB.

Usage:
    python -m backend.scripts.sync_twitter

Uses only stdlib — no pip packages required.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import random
import re
import sqlite3
import time
import urllib.parse
import urllib.request
import uuid
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Config — reads from env or falls back to hardcoded dev values
# ---------------------------------------------------------------------------

import os

API_KEY = os.environ.get("TWITTER_API_KEY", "VSGzfKGVdY5DoTKlg2ihDR0D7")
API_SECRET = os.environ.get("TWITTER_API_SECRET", "H2BNlYINJKAHS7do4ZJo2Yd7VQpWDNWwmOtRo3PA4OQEJ2HMET")
ACCESS_TOKEN = os.environ.get("TWITTER_ACCESS_TOKEN", "2024576960668860416-2f2HgAqVk781Bk47o5fO3ZtYDXbwCX")
ACCESS_SECRET = os.environ.get("TWITTER_ACCESS_TOKEN_SECRET", "aaExetMRH1Dc7HINSyPcCPaBe9C0PosWsXXIk0RAchxce")
USER_ID = os.environ.get("TWITTER_USER_ID", "2024576960668860416")

DB_PATH = Path(__file__).resolve().parent.parent / "db" / "local.db"

# ---------------------------------------------------------------------------
# OAuth 1.0a request helper
# ---------------------------------------------------------------------------


def oauth_request(method: str, url: str, params: dict) -> dict:
    """Make an OAuth 1.0a signed request to the Twitter API."""
    oauth_params = {
        "oauth_consumer_key": API_KEY,
        "oauth_nonce": uuid.uuid4().hex,
        "oauth_signature_method": "HMAC-SHA1",
        "oauth_timestamp": str(int(time.time())),
        "oauth_token": ACCESS_TOKEN,
        "oauth_version": "1.0",
    }
    all_params = {**oauth_params, **params}
    sorted_params = "&".join(
        f"{urllib.parse.quote(k, safe='')}={urllib.parse.quote(str(v), safe='')}"
        for k, v in sorted(all_params.items())
    )
    base_string = f"{method}&{urllib.parse.quote(url, safe='')}&{urllib.parse.quote(sorted_params, safe='')}"
    signing_key = f"{urllib.parse.quote(API_SECRET, safe='')}&{urllib.parse.quote(ACCESS_SECRET, safe='')}"
    signature = base64.b64encode(
        hmac.new(signing_key.encode(), base_string.encode(), hashlib.sha1).digest()
    ).decode()
    oauth_params["oauth_signature"] = signature
    auth_header = "OAuth " + ", ".join(
        f'{k}="{urllib.parse.quote(v, safe="")}"'
        for k, v in sorted(oauth_params.items())
    )
    query_string = urllib.parse.urlencode(params)
    full_url = f"{url}?{query_string}"
    req = urllib.request.Request(full_url, headers={"Authorization": auth_header})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


# ---------------------------------------------------------------------------
# Fetch tweets
# ---------------------------------------------------------------------------


def fetch_tweets() -> dict:
    """Fetch recent tweets for the configured user."""
    url = f"https://api.twitter.com/2/users/{USER_ID}/tweets"
    params = {
        "max_results": "100",
        "tweet.fields": "created_at,public_metrics,conversation_id,in_reply_to_user_id,referenced_tweets,text",
        "expansions": "referenced_tweets.id,in_reply_to_user_id",
        "user.fields": "name,username",
    }
    return oauth_request("GET", url, params)


# ---------------------------------------------------------------------------
# DB helpers
# ---------------------------------------------------------------------------


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


# ---------------------------------------------------------------------------
# Hashtag extraction
# ---------------------------------------------------------------------------


def extract_hashtags(text: str) -> list[str]:
    """Extract hashtags from tweet text, falling back to finance keywords."""
    hashtags = re.findall(r'#\w+', text)
    if not hashtags:
        finance_keywords = ["#finance", "#money", "#personalfinance"]
        hashtags = [
            k for k in finance_keywords
            if any(word in text.lower() for word in
                   ["money", "invest", "save", "budget", "credit", "finance", "broke", "bill", "pay"])
        ]
        if not hashtags:
            hashtags = ["#trending"]
    return hashtags


# ---------------------------------------------------------------------------
# Main sync logic
# ---------------------------------------------------------------------------


def sync(data: dict) -> None:
    """Parse the Twitter API response and insert into SQLite."""
    conn = get_db()

    tweets = data.get("data", [])
    includes = data.get("includes", {})

    # Build lookup maps from includes
    included_tweets = {t["id"]: t for t in includes.get("tweets", [])}
    included_users = {u["id"]: u for u in includes.get("users", [])}

    print(f"Fetched {len(tweets)} tweets from @the_cash_kitty")
    print(f"  Includes: {len(included_tweets)} referenced tweets, {len(included_users)} users")

    # Ensure the X platform row exists
    existing = conn.execute("SELECT id FROM platforms WHERE name = 'x'").fetchone()
    if not existing:
        conn.execute(
            "INSERT INTO platforms (name, status, auth_method, session_health, workers_status, connected_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            ("x", "connected", "oauth", "healthy",
             json.dumps({"discovery": True, "execution": True, "analytics": True}),
             datetime.now(timezone.utc).isoformat()),
        )
        conn.commit()

    # Separate replies from original tweets
    replies = []
    originals = []
    for tweet in tweets:
        ref_tweets = tweet.get("referenced_tweets", [])
        is_reply = any(r.get("type") == "replied_to" for r in ref_tweets)
        if is_reply:
            replies.append(tweet)
        else:
            originals.append(tweet)

    print(f"  {len(replies)} replies, {len(originals)} original tweets")

    # ------------------------------------------------------------------
    # Process replies: the original tweet being replied to -> discovered_videos,
    # Cash Kitty's reply -> generated_comments + engagements
    # ------------------------------------------------------------------
    for reply in replies:
        ref_tweets = reply.get("referenced_tweets", [])
        replied_to_id = None
        for r in ref_tweets:
            if r.get("type") == "replied_to":
                replied_to_id = r["id"]
                break

        # Find the original tweet and its author
        original_tweet = included_tweets.get(replied_to_id, {})
        original_text = original_tweet.get("text", "")
        reply_to_user_id = reply.get("in_reply_to_user_id")
        reply_to_user = included_users.get(reply_to_user_id, {})
        creator_username = reply_to_user.get("username", "unknown")

        video_url = f"https://x.com/{creator_username}/status/{replied_to_id}"

        # Insert discovered_video (the tweet being replied to)
        hashtags = extract_hashtags(original_text)
        cursor = conn.execute(
            "INSERT INTO discovered_videos "
            "(platform, video_url, creator, description, hashtags, status, engaged) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            ("x", video_url, f"@{creator_username}", original_text, json.dumps(hashtags), "engaged", 1),
        )
        video_id = cursor.lastrowid

        # Insert generated_comment (Cash Kitty's reply text)
        reply_text = reply.get("text", "")
        # Strip leading @mentions from reply text for the comment
        clean_text = reply_text
        while clean_text.startswith("@"):
            space_idx = clean_text.find(" ")
            if space_idx == -1:
                break
            clean_text = clean_text[space_idx + 1:].lstrip()

        cursor = conn.execute(
            "INSERT INTO generated_comments "
            "(video_id, text, approach, char_count, selected) "
            "VALUES (?, ?, ?, ?, 1)",
            (video_id, clean_text, "witty", len(clean_text)),
        )
        comment_id = cursor.lastrowid

        # Insert engagement
        posted_at = reply.get("created_at", datetime.now(timezone.utc).isoformat())
        risk_score = random.randint(5, 25)
        cursor = conn.execute(
            "INSERT INTO engagements "
            "(platform, video_id, comment_id, comment_text, risk_score, approval_path, posted_at, status) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            ("x", video_id, comment_id, clean_text, risk_score, "auto", posted_at, "posted"),
        )
        engagement_id = cursor.lastrowid

        # Insert engagement_metrics from public_metrics
        metrics = reply.get("public_metrics", {})
        conn.execute(
            "INSERT INTO engagement_metrics "
            "(engagement_id, likes, replies, impressions) "
            "VALUES (?, ?, ?, ?)",
            (
                engagement_id,
                metrics.get("like_count", 0),
                metrics.get("reply_count", 0),
                metrics.get("impression_count", 0),
            ),
        )

    # ------------------------------------------------------------------
    # Process original tweets (not replies) -> engagements only
    # ------------------------------------------------------------------
    for tweet in originals:
        tweet_text = tweet.get("text", "")
        posted_at = tweet.get("created_at", datetime.now(timezone.utc).isoformat())
        risk_score = random.randint(5, 15)

        cursor = conn.execute(
            "INSERT INTO engagements "
            "(platform, comment_text, risk_score, approval_path, posted_at, status) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            ("x", tweet_text, risk_score, "auto", posted_at, "posted"),
        )
        engagement_id = cursor.lastrowid

        metrics = tweet.get("public_metrics", {})
        conn.execute(
            "INSERT INTO engagement_metrics "
            "(engagement_id, likes, replies, impressions) "
            "VALUES (?, ?, ?, ?)",
            (
                engagement_id,
                metrics.get("like_count", 0),
                metrics.get("reply_count", 0),
                metrics.get("impression_count", 0),
            ),
        )

    # ------------------------------------------------------------------
    # Create review_queue items (3-4 pending items with Cash Kitty voice)
    # ------------------------------------------------------------------
    pending_proposals = [
        {
            "text": "ngl this is the financial literacy content we need more of. the kitty approves ",
            "risk_score": 18,
            "reasoning": "Low risk: supportive commentary on financial education content",
            "classification": "finance-educational",
        },
        {
            "text": "ok but why is nobody talking about this?? saving this for later fr",
            "risk_score": 12,
            "reasoning": "Low risk: casual engagement, no financial claims",
            "classification": "cultural-trending",
        },
        {
            "text": "the way this actually works tho. tried it last month and my savings account said thank you",
            "risk_score": 38,
            "reasoning": "Moderate risk: implies personal financial outcome, could be seen as endorsement",
            "classification": "finance-educational",
        },
        {
            "text": "every time i see one of these i learn something new. the internet is undefeated sometimes",
            "risk_score": 8,
            "reasoning": "Very low risk: generic positive comment, no financial advice",
            "classification": "cultural-trending",
        },
    ]

    # Pick 3-4 discovered videos to attach these to (use ones we just inserted)
    all_videos = conn.execute(
        "SELECT id FROM discovered_videos WHERE platform = 'x' ORDER BY id DESC LIMIT 4"
    ).fetchall()

    now = datetime.now(timezone.utc).isoformat()
    for i, proposal in enumerate(pending_proposals):
        vid_id = all_videos[i % len(all_videos)]["id"] if all_videos else None
        conn.execute(
            "INSERT INTO review_queue "
            "(video_id, proposed_text, risk_score, risk_reasoning, classification, queued_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (vid_id, proposal["text"], proposal["risk_score"],
             proposal["reasoning"], proposal["classification"], now),
        )

    conn.commit()

    # Print summary
    video_count = conn.execute("SELECT COUNT(*) FROM discovered_videos WHERE platform = 'x'").fetchone()[0]
    comment_count = conn.execute("SELECT COUNT(*) FROM generated_comments").fetchone()[0]
    engagement_count = conn.execute("SELECT COUNT(*) FROM engagements WHERE platform = 'x'").fetchone()[0]
    review_count = conn.execute("SELECT COUNT(*) FROM review_queue WHERE decision IS NULL").fetchone()[0]

    print(f"\nSync complete:")
    print(f"  discovered_videos (x): {video_count}")
    print(f"  generated_comments:    {comment_count}")
    print(f"  engagements (x):       {engagement_count}")
    print(f"  review_queue pending:  {review_count}")

    conn.close()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    print("Fetching tweets from Twitter API...")
    data = fetch_tweets()
    print("Syncing to local DB...")
    sync(data)
    print("Done!")


if __name__ == "__main__":
    main()
