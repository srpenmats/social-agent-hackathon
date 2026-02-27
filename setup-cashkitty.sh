#!/bin/bash
# One-command setup for CashKitty Command Hub

echo "🐱 Setting up CashKitty Command Hub with Real Twitter Data"
echo ""

BASE_URL="https://social-agent-hackathon-production.up.railway.app/api/v1"

echo "Step 1: Initialize database tables..."
curl -s -X POST "$BASE_URL/db/init-discovery-tables" | python3 -m json.tool
echo ""

echo "Step 2: Waiting for Railway deployment..."
sleep 120
echo ""

echo "Step 3: Discovering financial tweets..."
curl -s -X POST "$BASE_URL/discovery/twitter/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "personal finance OR money tips OR budgeting OR broke OR paycheck", "max_results": 20}' \
  | python3 -m json.tool | head -20
echo ""

echo "Step 4: Syncing to Hub..."
curl -s -X POST "$BASE_URL/discovery/sync-to-hub" | python3 -m json.tool
echo ""

echo "✅ Done! Open your X/Twitter Hub in the browser and click Refresh."
echo ""
echo "What you'll see:"
echo "  - Real tweets about personal finance"
echo "  - Hashtags: #personalfinance #money #budgeting"
echo "  - Engagement metrics (likes, retweets, replies)"
echo "  - Keyword streams"
echo ""
echo "To generate AI comments:"
echo "  curl -X POST $BASE_URL/discovery/generate-comment \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"post_id\":\"TWEET_ID\",\"tweet_text\":\"...\",\"author_username\":\"...\",\"num_candidates\":3,\"tone\":\"casual\"}'"
