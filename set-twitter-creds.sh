#!/bin/bash
# Set Twitter credentials on Railway

echo "🔐 Setting Twitter API credentials on Railway..."
echo ""

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "⚠️  Railway CLI not installed."
    echo ""
    echo "Please set these environment variables manually in Railway dashboard:"
    echo "https://railway.app/dashboard → social-agent-hackathon-production → Variables"
    echo ""
    echo "Add these variables:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "TWITTER_BEARER_TOKEN=AAAAAAAAAAAAAAAAAAAAAHnq7gEAAAAAQP%2B3ENHCj3Oxrt5Qq8OiXgQXyzw%3DSWCH80a84HXwRCsU1igJijJK3d4KiWh43r8GiziQ4YslxiGoGx"
    echo ""
    echo "Optional (for posting):"
    echo "TWITTER_API_KEY=VSGzfKGVdY5DoTKlg2ihDR0D7"
    echo "TWITTER_API_SECRET=H2BNlYINJKAHS7do4ZJo2Yd7VQpWDNWwmOtRo3PA4OQEJ2HMET"
    echo "TWITTER_ACCESS_TOKEN=2024576960668860416-2f2HgAqVk781Bk47o5fO3ZtYDXbwCX"
    echo "TWITTER_ACCESS_TOKEN_SECRET=aaExetMRH1Dc7HINSyPcCPaBe9C0PosWsXXIk0RAchxce"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "After setting, Railway will auto-deploy in ~1 minute."
    exit 0
fi

# If Railway CLI is available, set variables
echo "Setting TWITTER_BEARER_TOKEN..."
railway variables set TWITTER_BEARER_TOKEN="AAAAAAAAAAAAAAAAAAAAAHnq7gEAAAAAQP%2B3ENHCj3Oxrt5Qq8OiXgQXyzw%3DSWCH80a84HXwRCsU1igJijJK3d4KiWh43r8GiziQ4YslxiGoGx"

echo "Setting optional write credentials..."
railway variables set TWITTER_API_KEY="VSGzfKGVdY5DoTKlg2ihDR0D7"
railway variables set TWITTER_API_SECRET="H2BNlYINJKAHS7do4ZJo2Yd7VQpWDNWwmOtRo3PA4OQEJ2HMET"
railway variables set TWITTER_ACCESS_TOKEN="2024576960668860416-2f2HgAqVk781Bk47o5fO3ZtYDXbwCX"
railway variables set TWITTER_ACCESS_TOKEN_SECRET="aaExetMRH1Dc7HINSyPcCPaBe9C0PosWsXXIk0RAchxce"

echo ""
echo "✅ Credentials set! Railway will auto-deploy in ~1 minute."
echo ""
echo "Test the API after deployment:"
echo "curl https://social-agent-hackathon-production.up.railway.app/api/v1/health"
