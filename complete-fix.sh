#!/bin/bash
# Complete working solution to show Twitter data in frontend

echo "🐱 CashKitty Command Hub - Complete Setup"
echo ""

API="https://social-agent-hackathon-production.up.railway.app/api/v1"

echo "Step 1: Waiting for Railway deployment..."
echo "  (Deploying twitter_live endpoint with schema fix)"
sleep 120
echo ""

echo "Step 2: Discovering TOP engagement posts from Twitter..."
echo "  (Looking for posts with 50+ likes or 20+ retweets)"
curl -s -X POST "$API/twitter/discover-top-posts" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "personal finance OR money tips OR budgeting OR investing",
    "min_likes": 50,
    "max_results": 20
  }' | python3 -m json.tool
echo ""

echo "Step 3: Verifying data in Hub..."
curl -s "$API/hubs/x/stats" | python3 -m json.tool | head -30
echo ""

echo "✅ DONE!"
echo ""
echo "What you should see:"
echo "  - High-engagement tweets (50+ likes)"
echo "  - Real hashtags and metrics"
echo "  - Keyword streams populated"
echo ""
echo "Now refresh your frontend at:"
echo "  https://your-app.vercel.app"
echo ""
echo "Click: X / Twitter Hub → See real data!"
echo ""
echo "To discover more:"
echo "  curl -X POST $API/twitter/discover-top-posts \\"
echo "    -d '{\"query\":\"YOUR_QUERY\",\"min_likes\":50}'"
