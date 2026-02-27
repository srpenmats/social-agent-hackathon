# Twitter Real Data Integration - Recommendations

## Executive Summary

To see **real Twitter data** in the X/Twitter Hub, you need to:

1. **Use the live discovery system** that's already partially built
2. **Connect to Twitter API** with proper credentials
3. **Wire the discovery data into the Hub UI**
4. **Optional:** Use the sync script to populate initial data

---

## Current State Analysis

### ✅ What's Already Built

1. **Backend Discovery System** (`backend/routers/discovery.py`)
   - Live Twitter API integration
   - Background job processing
   - Database persistence (`discovery_jobs`, `discovered_posts`)
   - Status tracking

2. **Twitter Service** (`backend/services/social/twitter.py`)
   - Full OAuth 2.0 with PKCE support
   - API key fallback method
   - Rate limiting
   - Tweet search, posting, metrics

3. **Hub Stats Endpoint** (`backend/routers/hubs.py`)
   - Returns stats, keywords, drafts for X platform
   - Currently reads from `discovered_videos` and `review_queue` tables

4. **Frontend Hub UI** (`screens/XHub.tsx`)
   - Displays stats, keyword streams, high-risk drafts
   - Has refresh button, approve/reject/edit workflow
   - Ready to display real data

### ⚠️ Current Gaps

1. **Discovery data flows to `discovered_posts` table** but Hub reads from `discovered_videos`
2. **No automatic sync** between discovery tables and dashboard tables
3. **Twitter API credentials** need to be configured in Railway environment
4. **No bridge** connecting discovery → scoring → review queue flow

---

## Recommended Changes

### Option A: Quick Win - Use Existing Sync Script (30 minutes)

**What:** Use the existing `sync_twitter.py` script to populate dashboard with real data.

**How:**

1. **Set environment variables on Railway:**
   ```bash
   TWITTER_API_KEY=your_api_key
   TWITTER_API_SECRET=your_api_secret
   TWITTER_ACCESS_TOKEN=your_access_token
   TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret
   TWITTER_USER_ID=your_user_id  # e.g., 2024576960668860416
   ```

2. **Run sync script on Railway:**
   ```bash
   cd backend
   python scripts/sync_twitter.py
   ```

3. **Refresh the X Hub UI** - you'll now see:
   - Real tweet replies as "discovered videos"
   - Cash Kitty's responses as "generated comments"
   - Engagement metrics from Twitter
   - 3-4 pending review items

**Pros:**
- Works immediately
- No code changes needed
- Uses existing database schema

**Cons:**
- Manual process (not automated)
- Only syncs historical data
- Doesn't include live discovery

---

### Option B: Bridge Discovery to Hub (2 hours)

**What:** Connect the live discovery system to the Hub display.

**Changes needed:**

#### 1. Create Bridge Script: `backend/services/discovery_bridge.py`

```python
"""Bridge between discovery_posts and dashboard tables."""

from datetime import datetime, timezone
import json
from db.connection import get_supabase_admin

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

def extract_hashtags(text: str) -> list[str]:
    """Extract hashtags from text."""
    import re
    hashtags = re.findall(r'#\w+', text)
    if not hashtags:
        # Fallback to keywords
        keywords = ["AI", "agent", "security", "automation"]
        hashtags = [f"#{k.lower()}" for k in keywords if k.lower() in text.lower()]
    return hashtags or ["#trending"]
```

#### 2. Add Bridge Endpoint: `backend/routers/discovery.py`

```python
@router.post("/sync-to-hub")
async def sync_discovery_to_hub():
    """Sync discovered_posts to discovered_videos for Hub display."""
    from services.discovery_bridge import sync_discovered_posts_to_videos
    
    synced_count = sync_discovered_posts_to_videos()
    
    return {
        "success": True,
        "synced_count": synced_count,
        "message": f"Synced {synced_count} posts to Hub"
    }
```

#### 3. Update Frontend: Add Auto-Sync on Refresh

In `screens/XHub.tsx`, modify `handleRefresh`:

```typescript
const handleRefresh = async () => {
  setRefreshing(true);
  try {
    // Trigger discovery
    await fetch(`${API_BASE}/discovery/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query: "AI agent security OR cybersecurity OR agent automation",
        max_results: 20
      })
    });
    
    // Wait for discovery to complete (poll job status)
    await new Promise(resolve => setTimeout(resolve, 5000));
    
    // Sync to Hub
    await fetch(`${API_BASE}/discovery/sync-to-hub`, { method: 'POST' });
    
    // Load fresh data
    await fetchData();
  } catch (e) {
    console.warn('Refresh failed:', e);
  }
  setRefreshing(false);
};
```

#### 4. Set Twitter Bearer Token on Railway

```bash
railway variables set TWITTER_BEARER_TOKEN=your_bearer_token_here
```

**Result:**
- Click "Refresh" in X Hub → discovers real tweets
- Auto-syncs to dashboard tables
- Displays in UI immediately
- Fully automated workflow

---

### Option C: Full Integration (4 hours)

**What:** Complete end-to-end flow: Discovery → Scoring → Generation → Review → Posting

**Components:**

1. **Discovery Worker** (already exists in `services/workers/discovery_worker.py`)
2. **Scoring System** (needs to be built - scores tweets 0-10 for engagement potential)
3. **Comment Generation** (integrate Claude API to generate responses)
4. **Review Queue** (already partially built)
5. **Posting Automation** (use `twitter.py` service to post approved comments)

**This is the full Jen system** as described in MEMORY.md Part 1-6.

**Time estimate:** 4-6 hours of focused development

---

## Immediate Action Plan (Recommended: Option B)

### Step 1: Configure Twitter API (10 min)

1. Go to Railway dashboard
2. Add environment variables:
   ```
   TWITTER_BEARER_TOKEN=AAAAAAAAAAAAAAAAAAAAAMLheAAAAAAA0%2BuS...
   ```
3. Deploy changes

### Step 2: Create Bridge Script (30 min)

```bash
cd /home/ubuntu/.openclaw/workspace/social-agent-hackathon/backend/services
touch discovery_bridge.py
```

Copy the bridge script code from Option B above.

### Step 3: Add Bridge Endpoint (15 min)

Edit `backend/routers/discovery.py` and add the sync endpoint.

### Step 4: Update Frontend (20 min)

Edit `screens/XHub.tsx` and update the refresh handler.

### Step 5: Test (15 min)

1. Click "Refresh" in X Hub
2. Verify API calls in Network tab
3. Check that tweets appear in dashboard
4. Verify data persists after page reload

### Step 6: Deploy (10 min)

```bash
git add .
git commit -m "feat: Bridge discovery to Hub UI for real Twitter data"
git push origin main
```

Railway auto-deploys.

---

## Alternative: Use Demo Mode with Real Structure

If you want to see the UI working **immediately** without API setup:

### Quick Demo Data Population

Run this SQL on your Railway database:

```sql
-- Insert discovered tweets
INSERT INTO discovered_videos (platform, video_url, creator, description, hashtags, likes, comments, status)
VALUES 
  ('x', 'https://x.com/elonmusk/status/123', '@elonmusk', 'AI agents will change everything', '["#AI", "#agents"]', 1500, 89, 'discovered'),
  ('x', 'https://x.com/sama/status/456', '@sama', 'Security for AI agents is critical', '["#security", "#AI"]', 890, 45, 'discovered'),
  ('x', 'https://x.com/karpathy/status/789', '@karpathy', 'Agent orchestration patterns', '["#agents", "#engineering"]', 2100, 156, 'discovered');

-- Insert pending review items
INSERT INTO review_queue (video_id, proposed_text, risk_score, classification, queued_at)
SELECT 
  id,
  'This is exactly what we need to be talking about. The security implications of autonomous agents are massive.',
  35,
  'technical-security',
  NOW()
FROM discovered_videos WHERE platform = 'x' LIMIT 1;
```

Refresh the X Hub → you'll see real-looking data immediately.

---

## Environment Variables Checklist

### Required on Railway:

- ✅ `TWITTER_BEARER_TOKEN` - For read-only API access (search, read tweets)
- ⚠️ `TWITTER_API_KEY` - For posting (optional if only discovering)
- ⚠️ `TWITTER_API_SECRET` - For posting (optional)
- ⚠️ `TWITTER_ACCESS_TOKEN` - For posting as user (optional)
- ⚠️ `TWITTER_ACCESS_TOKEN_SECRET` - For posting (optional)

### How to Get Bearer Token:

1. Go to https://developer.twitter.com/en/portal/dashboard
2. Create a Project + App (if you haven't)
3. Navigate to "Keys and tokens"
4. Generate "Bearer Token"
5. Copy and add to Railway

---

## Testing Strategy

### 1. Test Discovery Endpoint Directly

```bash
curl -X POST https://your-app.railway.app/api/v1/discovery/start \
  -H "Content-Type: application/json" \
  -d '{"query": "AI agent security", "max_results": 10}'

# Response: {"job_id": "1", "status": "pending", ...}

# Check status
curl https://your-app.railway.app/api/v1/discovery/jobs/1

# Get posts
curl https://your-app.railway.app/api/v1/discovery/posts?status=discovered
```

### 2. Test Bridge Sync

```bash
curl -X POST https://your-app.railway.app/api/v1/discovery/sync-to-hub
```

### 3. Test Hub Stats

```bash
curl https://your-app.railway.app/api/v1/hubs/x/stats \
  -H "Authorization: Bearer your_token"
```

---

## Success Metrics

After implementation, you should see in X Hub:

- ✅ **Real tweet counts** in stats cards
- ✅ **Live hashtags/keywords** from discovered tweets
- ✅ **Actual Twitter usernames** and tweet URLs
- ✅ **Clickable links** that open real tweets on Twitter
- ✅ **Fresh data** when clicking Refresh
- ✅ **Persistence** - data survives page reloads

---

## Next Steps After Real Data is Flowing

1. **Add Comment Generation** - Generate AI responses to discovered tweets
2. **Implement Scoring** - Prioritize which tweets to engage with
3. **Build Review Workflow** - Human-in-the-loop approval
4. **Add Posting** - Auto-post approved comments
5. **Track Performance** - Monitor engagement metrics

---

## Files to Create/Modify

### New Files:
- `backend/services/discovery_bridge.py`

### Modified Files:
- `backend/routers/discovery.py` (add sync endpoint)
- `screens/XHub.tsx` (update refresh handler)
- `railway.json` (ensure env vars are documented)

### Railway Config:
- Add `TWITTER_BEARER_TOKEN` environment variable

---

## Estimated Time to Completion

| Task | Time | Difficulty |
|------|------|------------|
| Set up Twitter API credentials | 10 min | Easy |
| Create bridge script | 30 min | Medium |
| Add bridge endpoint | 15 min | Easy |
| Update frontend refresh | 20 min | Easy |
| Test end-to-end | 15 min | Easy |
| Deploy to Railway | 10 min | Easy |
| **Total** | **~90 min** | **Medium** |

---

## Want Me to Implement This?

I can build **Option B (Bridge Discovery to Hub)** for you right now. It will:

1. Create the bridge script
2. Add the sync endpoint
3. Update the frontend
4. Give you deployment instructions

Just say "yes, implement Option B" and I'll get started! 🚀

---

## Support Resources

- Twitter API Docs: https://developer.twitter.com/en/docs/twitter-api
- Railway Docs: https://docs.railway.app/
- Backend Routers: `/backend/routers/`
- Frontend Screens: `/screens/XHub.tsx`
- Discovery System: `/backend/routers/discovery.py`
