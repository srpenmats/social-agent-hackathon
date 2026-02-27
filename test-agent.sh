#!/bin/bash
# Test the intelligent agent with PostgreSQL

echo "🤖 Testing Intelligent Agent with PostgreSQL"
echo ""

API="https://social-agent-hackathon-production.up.railway.app/api/v1"

echo "Step 1: Checking database status..."
curl -s "$API/agent/db-status" | python3 -m json.tool
echo ""

echo "Step 2: Discovering high-engagement financial posts from Twitter..."
curl -s -X POST "$API/agent/discover-smart" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "personal finance OR money tips OR budgeting",
    "min_engagement": 50,
    "max_results": 20
  }' | python3 -m json.tool
echo ""

echo "Step 3: Checking X Hub stats..."
curl -s "$API/hubs/x/stats" | python3 -m json.tool | head -30
echo ""

echo "Step 4: Checking Overview dashboard..."
curl -s "$API/dashboard/overview?timeframe=7d" | python3 -m json.tool | head -40
echo ""

echo "✅ Test complete!"
echo ""
echo "If you see:"
echo "  - db_status: using_postgres = true"
echo "  - discover-smart: stored > 0"
echo "  - hubs stats: keywords > 0"
echo ""
echo "Then it's working! Refresh your frontend to see the data."
