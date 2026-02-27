# Quick Start Guide: Get Real Twitter Data in X Hub

## TL;DR

Run these commands to see real Twitter data in your X Hub:

```bash
# 1. Set Twitter API credentials on Railway
railway variables set TWITTER_BEARER_TOKEN="your_bearer_token_here"

# 2. Create bridge service
cd /home/ubuntu/.openclaw/workspace/social-agent-hackathon
cat > backend/services/discovery_bridge.py << 'EOF'
"""Bridge between discovery_posts and dashboard tables."""

from datetime import datetime, timezone
import json
import re
from db.connection import get_supabase_admin

def extract_hashtags(text: str) -> list[str]:
    """Extract hashtags from text."""
    hashtags = re.findall(r'#\w+', text)
    if not hashtags:
        keywords = ["AI", "agent", "security", "automation", "cybersecurity"]
        hashtags = [f"#{k.lower()}" for k in keywords if k.lower() in text.lower()]
    return hashtags or ["#trending"]

def sync_discovered_posts_to_videos():
    """Copy discovered_posts → discovered_videos for Hub display."""
    db = get_supabase_admin()
    
    posts = db.table("discovered_posts").select("*").eq("status", "discovered").execute()
    
    synced_count = 0
    for post in posts.data or []:
        hashtags = extract_hashtags(post.get("post_text", ""))
        
        video_record = {
            "platform": post["platform"],
            "video_url": post["post_url"],
            "creator": f"@{post['author_username']}",
            "description": post["post_text"],
            "hashtags": json.dumps(hashtags),
            "likes": post.get("likes", 0),
            "comments": post.get("replies", 0),
            "shares": post.get("retweets", 0),
            "status": "discovered",
            "engaged": 0,
            "discovered_at": post.get("discovered_at"),
        }
        
        db.table("discovered_videos").upsert(video_record, on_conflict="video_url").execute()
        
        db.table("discovered_posts").update({
            "status": "synced",
            "updated_at": datetime.now(timezone.utc).isoformat()
        }).eq("id", post["id"]).execute()
        
        synced_count += 1
    
    return synced_count
EOF

# 3. Add sync endpoint to discovery router
# Edit backend/routers/discovery.py and add at the end:
cat >> backend/routers/discovery.py << 'EOF'

@router.post("/sync-to-hub")
async def sync_discovery_to_hub():
    """Sync discovered_posts to discovered_videos for Hub display."""
    from services.discovery_bridge import sync_discovered_posts_to_videos
    
    try:
        synced_count = sync_discovered_posts_to_videos()
        return {
            "success": True,
            "synced_count": synced_count,
            "message": f"Synced {synced_count} posts to Hub"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Sync failed"
        }
EOF

# 4. Deploy to Railway
git add .
git commit -m "feat: Bridge discovery to Hub for real Twitter data"
git push origin main

echo "✅ Deployment complete! Railway will auto-deploy in ~2 minutes."
echo ""
echo "Next steps:"
echo "1. Wait for Railway deployment to complete"
echo "2. Test discovery: curl -X POST https://your-app.railway.app/api/v1/discovery/start -H 'Content-Type: application/json' -d '{\"query\": \"AI agent security\", \"max_results\": 20}'"
echo "3. Check job status: curl https://your-app.railway.app/api/v1/discovery/jobs/1"
echo "4. Sync to hub: curl -X POST https://your-app.railway.app/api/v1/discovery/sync-to-hub"
echo "5. Open X Hub in browser and click Refresh"
```

---

## Step-by-Step Instructions

### Step 1: Get Twitter Bearer Token (5 min)

1. Go to https://developer.twitter.com/en/portal/dashboard
2. Create a project and app (if you haven't)
3. Navigate to your app → "Keys and tokens"
4. Under "Authentication Tokens", click "Generate" for Bearer Token
5. **Copy the token** (starts with `AAAAAAAAAAAAA...`)

### Step 2: Add to Railway (2 min)

**Option A: Via Railway CLI**
```bash
cd /home/ubuntu/.openclaw/workspace/social-agent-hackathon
railway link  # Link to your project if not already
railway variables set TWITTER_BEARER_TOKEN="AAAAAAAAAAAAA..."
```

**Option B: Via Railway Dashboard**
1. Go to https://railway.app/dashboard
2. Select your project: `social-agent-hackathon-production`
3. Click "Variables" tab
4. Add new variable:
   - Key: `TWITTER_BEARER_TOKEN`
   - Value: `AAAAAAAAAAAAA...` (your bearer token)
5. Click "Deploy"

### Step 3: Create Bridge Service (5 min)

```bash
cd /home/ubuntu/.openclaw/workspace/social-agent-hackathon
touch backend/services/discovery_bridge.py
```

Copy this content into the file:

```python
"""Bridge between discovery_posts and dashboard tables."""

from datetime import datetime, timezone
import json
import re
from db.connection import get_supabase_admin

def extract_hashtags(text: str) -> list[str]:
    """Extract hashtags from text."""
    hashtags = re.findall(r'#\w+', text)
    if not hashtags:
        keywords = ["AI", "agent", "security", "automation", "cybersecurity"]
        hashtags = [f"#{k.lower()}" for k in keywords if k.lower() in text.lower()]
    return hashtags or ["#trending"]

def sync_discovered_posts_to_videos():
    """Copy discovered_posts → discovered_videos for Hub display."""
    db = get_supabase_admin()
    
    # Get new discovered posts not yet synced
    posts = db.table("discovered_posts").select("*").eq("status", "discovered").execute()
    
    synced_count = 0
    for post in posts.data or []:
        # Extract hashtags from post text
        hashtags = extract_hashtags(post.get("post_text", ""))
        
        # Insert into discovered_videos
        video_record = {
            "platform": post["platform"],  # "x"
            "video_url": post["post_url"],
            "creator": f"@{post['author_username']}",
            "description": post["post_text"],
            "hashtags": json.dumps(hashtags),
            "likes": post.get("likes", 0),
            "comments": post.get("replies", 0),
            "shares": post.get("retweets", 0),
            "status": "discovered",
            "engaged": 0,
            "discovered_at": post.get("discovered_at"),
        }
        
        db.table("discovered_videos").upsert(video_record, on_conflict="video_url").execute()
        
        # Mark as synced
        db.table("discovered_posts").update({
            "status": "synced",
            "updated_at": datetime.now(timezone.utc).isoformat()
        }).eq("id", post["id"]).execute()
        
        synced_count += 1
    
    return synced_count
```

### Step 4: Add Sync Endpoint (3 min)

Edit `backend/routers/discovery.py` and add this at the end (before the final blank lines):

```python
@router.post("/sync-to-hub")
async def sync_discovery_to_hub():
    """Sync discovered_posts to discovered_videos for Hub display."""
    from services.discovery_bridge import sync_discovered_posts_to_videos
    
    try:
        synced_count = sync_discovered_posts_to_videos()
        return {
            "success": True,
            "synced_count": synced_count,
            "message": f"Synced {synced_count} posts to Hub"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Sync failed"
        }
```

### Step 5: Update Frontend Refresh (5 min)

Edit `screens/XHub.tsx` and replace the `handleRefresh` function:

```typescript
const handleRefresh = async () => {
  setRefreshing(true);
  try {
    // Step 1: Start discovery
    const discoveryResp = await fetch(`${API_BASE}/discovery/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query: "AI agent security OR cybersecurity OR autonomous agents",
        max_results: 20
      })
    });
    
    if (!discoveryResp.ok) {
      throw new Error('Discovery failed');
    }
    
    const discoveryData = await discoveryResp.json();
    const jobId = discoveryData.job_id;
    
    // Step 2: Poll job status (wait up to 15 seconds)
    let attempts = 0;
    let jobStatus = 'pending';
    while (jobStatus === 'pending' || jobStatus === 'running') {
      if (attempts > 15) break; // Timeout after 15 seconds
      
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const statusResp = await fetch(`${API_BASE}/discovery/jobs/${jobId}`);
      if (statusResp.ok) {
        const statusData = await statusResp.json();
        jobStatus = statusData.status;
      }
      attempts++;
    }
    
    // Step 3: Sync to hub
    await fetch(`${API_BASE}/discovery/sync-to-hub`, { method: 'POST' });
    
    // Step 4: Reload hub data
    await fetchData();
  } catch (e) {
    console.warn('Refresh failed:', e);
    // Still try to reload whatever data exists
    await fetchData();
  }
  setRefreshing(false);
};
```

### Step 6: Deploy (2 min)

```bash
cd /home/ubuntu/.openclaw/workspace/social-agent-hackathon
git add .
git commit -m "feat: Bridge discovery to Hub for real Twitter data"
git push origin main
```

Railway will auto-deploy in ~2 minutes.

### Step 7: Test (5 min)

Once Railway deployment completes:

**Test discovery API:**
```bash
curl -X POST https://your-railway-url.railway.app/api/v1/discovery/start \
  -H "Content-Type: application/json" \
  -d '{"query": "AI agent security", "max_results": 20}'

# Response: {"job_id": "1", "status": "pending", "message": "Discovery started..."}
```

**Check job status:**
```bash
curl https://your-railway-url.railway.app/api/v1/discovery/jobs/1

# Response: {"id": 1, "status": "completed", "posts_found": 15, ...}
```

**Sync to hub:**
```bash
curl -X POST https://your-railway-url.railway.app/api/v1/discovery/sync-to-hub

# Response: {"success": true, "synced_count": 15, "message": "Synced 15 posts to Hub"}
```

**Open browser:**
1. Navigate to your frontend URL
2. Click "X / Twitter Hub" in sidebar
3. Click "Refresh" button
4. ✅ See real Twitter data!

---

## Troubleshooting

### Issue: "Rate limit exceeded"

**Solution:** Twitter API has rate limits. Wait 15 minutes and try again.

### Issue: "Bearer token validation failed"

**Solution:** Check that `TWITTER_BEARER_TOKEN` is set correctly in Railway env vars. Token should start with `AAAAAAAAAAAAA`.

### Issue: "No posts found"

**Solution:** Try a broader search query:
```bash
curl -X POST .../discovery/start -d '{"query": "AI OR agents OR automation", "max_results": 50}'
```

### Issue: "discovered_posts table doesn't exist"

**Solution:** Run the database migration first:
```bash
# On Railway, run this command:
python add_discovery_tables.py
```

### Issue: Frontend still shows "No data"

**Solution:** 
1. Check browser console for errors
2. Verify API calls are reaching backend (Network tab)
3. Check Railway logs for backend errors
4. Manually test sync endpoint with curl

---

## Success Checklist

After completing all steps, you should have:

- ✅ Twitter Bearer Token configured on Railway
- ✅ Bridge service created (`backend/services/discovery_bridge.py`)
- ✅ Sync endpoint added (`/api/v1/discovery/sync-to-hub`)
- ✅ Frontend refresh updated to trigger full flow
- ✅ Code pushed to GitHub
- ✅ Railway deployment successful
- ✅ Discovery API returning real tweets
- ✅ Sync endpoint moving data to Hub tables
- ✅ X Hub UI displaying real Twitter data
- ✅ Hashtags populated from real tweets
- ✅ Clickable tweet URLs working
- ✅ Refresh button fetching new data

---

## What You'll See in X Hub

After successful implementation:

**Stats Cards:**
- Mentions Replied: 0 (will increase as you approve comments)
- Keywords Triggered: 15-20 (from discovered tweets)
- Avg Sentiment: Will calculate from tweets
- API Quota: Shows remaining Twitter API calls

**Keyword Streams Section:**
- Real hashtags from discovered tweets (#AI, #security, etc.)
- Sample text from tweets
- Volume counts (likes on original tweets)

**High-Risk Drafts Section:**
- Will be empty initially
- Will populate once you build comment generation

**Next Steps:**
- Build comment generation (generate AI responses)
- Add scoring system (prioritize tweets)
- Build review workflow (approve/reject)
- Implement posting (auto-post approved comments)

---

## Time Investment

| Task | Time |
|------|------|
| Get Twitter token | 5 min |
| Configure Railway | 2 min |
| Create bridge service | 5 min |
| Add sync endpoint | 3 min |
| Update frontend | 5 min |
| Deploy & test | 7 min |
| **Total** | **~27 min** |

---

## Need Help?

Check these resources:
- Railway logs: `railway logs`
- Backend API docs: `https://your-url.railway.app/docs`
- Twitter API status: https://api.twitterstat.us/
- Discovery tables SQL: `add_discovery_tables.py`

---

**Ready to implement? Start with Step 1! 🚀**
