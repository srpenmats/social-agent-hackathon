#!/bin/bash
# Complete data population for Overview + X Hub

echo "🎯 Populating CashKitty Dashboard with Full Data"
echo ""

API="https://social-agent-hackathon-production.up.railway.app/api/v1"

echo "Step 1: Waiting for Railway deployment..."
sleep 120
echo ""

echo "Step 2: Populating discovered tweets..."
curl -s -X POST "$API/populate/now" | python3 -m json.tool
echo ""

echo "Step 3: Creating engagement data..."
curl -s -X POST "$API/populate/engagements" | python3 -m json.tool
echo ""

echo "Step 4: Verifying Overview stats..."
curl -s "$API/dashboard/overview?timeframe=7d" | python3 -m json.tool | head -40
echo ""

echo "Step 5: Verifying X Hub stats..."
curl -s "$API/hubs/x/stats" | python3 -m json.tool | head -30
echo ""

echo "✅ COMPLETE!"
echo ""
echo "What you should see:"
echo ""
echo "📊 Overview Tab:"
echo "  - Total Engagements: 5"
echo "  - Platform Health: X/Twitter active"
echo "  - Chart: Activity over time"
echo ""
echo "🐦 X / Twitter Hub:"
echo "  - 5 discovered tweets"
echo "  - Hashtags: #personalfinance, #budgeting, #investing"
echo "  - Engagement metrics visible"
echo ""
echo "Now refresh your frontend!"
