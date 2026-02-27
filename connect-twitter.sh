#!/bin/bash
# Connect Twitter account and verify

API="https://social-agent-hackathon-production.up.railway.app/api/v1"

echo "🔌 Connecting Twitter Account"
echo ""
echo "Waiting 120s for deployment..."
sleep 120
echo ""

echo "Step 1: Connecting Twitter..."
curl -s -X POST "$API/platforms/connect/twitter" | python3 -m json.tool
echo ""

echo "Step 2: Checking platform status..."
curl -s "$API/platforms/status" | python3 -m json.tool
echo ""

echo "Step 3: Checking Overview (should show 1/3 active)..."
curl -s "$API/dashboard/overview?timeframe=7d" | python3 -m json.tool | grep -A 5 "active_platforms"
echo ""

echo "✅ Done!"
echo ""
echo "Your Twitter account should now show as connected in Overview (1/3 platforms active)"
