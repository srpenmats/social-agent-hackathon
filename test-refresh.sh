#!/bin/bash
# Test auto-refresh functionality

API="https://social-agent-hackathon-production.up.railway.app/api/v1"

echo "🔄 Testing Auto-Refresh System"
echo ""
echo "Waiting 120s for deployment..."
sleep 120
echo ""

echo "1️⃣ Testing scheduler health..."
curl -s "$API/scheduler/health" | python3 -m json.tool
echo ""

echo "2️⃣ Running manual hourly refresh..."
curl -s -X POST "$API/scheduler/hourly-refresh" | python3 -m json.tool | head -40
echo ""

echo "3️⃣ Checking X Hub data..."
curl -s "$API/hubs/x/stats" | python3 -m json.tool | head -30
echo ""

echo "✅ Test complete!"
echo ""
echo "Next steps:"
echo "1. Click 'Refresh' button in X Hub (frontend)"
echo "2. Set up cron: openclaw cron add --schedule '0 * * * *' --task 'curl -X POST $API/scheduler/hourly-refresh'"
echo "3. Or use cron-job.org to call the endpoint hourly"
