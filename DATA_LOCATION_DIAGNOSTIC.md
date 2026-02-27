# 🔍 Data Location & Frontend Connection - Complete Diagnostic

## Where Is The Real Twitter Data?

### ✅ Data Location: Railway PostgreSQL/SQLite Database

**Table:** `discovered_posts`  
**Location:** Railway backend database  
**Status:** ✅ **10 tweets stored** (as of 5:15 UTC)

**Proof:**
```bash
curl https://social-agent-hackathon-production.up.railway.app/api/v1/discovery/twitter/posts?limit=3
```

**Sample data stored:**
1. Tweet from @Prdct_Dznr_47 about personal finance
2. Tweet from @SamarpanDutta72 about car EMI
3. Tweet from @opal_life_ about finance AI agents
...10 total tweets

---

## Why Frontend Shows Nothing

### The Disconnect:

```
Real Data (Backend)          Frontend Display
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
discovered_posts table   →   ❌ NOT CONNECTED
   ↓ (needs sync)
discovered_videos table  →   ✅ CONNECTED (but empty!)
   ↓
/api/v1/hubs/x/stats     →   ✅ Frontend calls this
   ↓
Frontend XHub.tsx        →   Shows empty
```

**Problem:** The sync step is broken due to schema mismatch.

---

## Complete Data Flow (Should Be)

```
1. Twitter API
   ↓
2. Discovery endpoint (/discovery/twitter/search)
   ↓
3. discovered_posts table (✅ HAS DATA)
   ↓
4. Sync endpoint (/discovery/sync-to-hub) ❌ BROKEN
   ↓
5. discovered_videos table (❌ EMPTY)
   ↓
6. Hub stats endpoint (/hubs/x/stats)
   ↓
7. Frontend (XHub.tsx)
```

**Current state:** Stuck at step 4

---

## What Frontend Is Reading

### Frontend Code (`screens/XHub.tsx`)

```typescript
const fetchData = useCallback(async () => {
  try {
    const result = await HubAPI.getStats('x');
    setData(result);
  } catch (err) {
    setError(err instanceof ApiError ? err.detail : 'Failed to load X data.');
  }
}, []);
```

### API Call Made:
```
GET https://social-agent-hackathon-production.up.railway.app/api/v1/hubs/x/stats
```

### What That Endpoint Returns Now:
```json
{
  "stats": {
    "replies": 0,
    "keywords": 0,
    "sentiment": "0.82",
    "quota": "67%"
  },
  "keywords": [],
  "drafts": []
}
```

**Why zeros?** Because it reads from `discovered_videos` table which is empty.

---

## Backend Hub Stats Logic (`backend/routers/hubs.py`)

```python
@router.get("/api/v1/hubs/{platform}/stats")
async def hub_stats(platform: str, user: CurrentUser):
    db = get_supabase_admin()
    
    # Count engagements (empty → replies: 0)
    engagements_resp = db.table("engagements").select("id").eq("platform", platform).execute()
    replies_count = len(engagements_resp.data or [])
    
    # Build keywords from discovered_videos (empty → keywords: 0)
    videos_resp = db.table("discovered_videos").select("hashtags, description, likes").eq("platform", platform).execute()
    videos = videos_resp.data or []
    
    # Build drafts from review_queue (empty → drafts: [])
    review_resp = db.table("review_queue").select("*").is_("decision", "null").execute()
    drafts = []
    
    return {
        "stats": {"replies": replies_count, "keywords": len(keywords), ...},
        "keywords": keywords,
        "drafts": drafts
    }
```

**Tables it reads:**
- `engagements` (empty)
- `discovered_videos` (empty) ← **THIS IS THE PROBLEM**
- `review_queue` (empty)

---

## The Fix (3 Options)

### Option 1: Fix the Sync Endpoint (Best Long-Term)

**Status:** Deploying now (quickfix endpoint)

**When ready (~5:22 UTC):**
```bash
curl -X POST https://social-agent-hackathon-production.up.railway.app/api/v1/quick/sync-to-hub-now
```

This will copy all 10 tweets from `discovered_posts` → `discovered_videos`.

---

### Option 2: Change Frontend to Read discovered_posts (Quick Hack)

Edit `backend/routers/hubs.py`:
```python
# Change line ~25 from:
videos_resp = db.table("discovered_videos").select(...)

# To:
videos_resp = db.table("discovered_posts").select(...)
```

Then map the fields correctly.

---

### Option 3: Use Demo Data Temporarily

```bash
# Populate with sample data
curl -X POST https://social-agent-hackathon-production.up.railway.app/api/v1/demo/populate
```

---

## Current Database State

### ✅ Has Data:
```
discovered_posts
├── id: 1-10
├── platform: "x"
├── post_id: "2027251215109615865", etc.
├── post_text: "Personal finance. How mortgages...", etc.
├── author_username: "Prdct_Dznr_47", etc.
├── likes: 0
├── status: "discovered"
└── discovered_at: "2026-02-27T05:15:28.000Z"
```

### ❌ Empty:
```
discovered_videos
├── (no rows)

engagements
├── (no rows)

review_queue
├── (no rows)
```

---

## What You Should See (After Fix)

### Stats Cards:
- **Mentions Replied:** 0 (no engagements yet)
- **Keywords Triggered:** 10+ (from discovered tweets)
- **Hashtags:** #personalfinance, #money, etc.

### Keyword Streams:
```
#personalfinance
"Personal finance. How mortgages and banking works..."
🔥 Volume: 0 (low engagement)

#money  
"Prestige on EMI: Dream drive or costly detour?..."
🔥 Volume: 0
```

### High-Risk Drafts:
(Empty until you generate comments)

---

## Immediate Action Plan

### Step 1: Wait for Railway Deploy (1 more minute)
Current time: ~5:21 UTC
Deploy complete: ~5:22 UTC

### Step 2: Run Quickfix Sync
```bash
curl -X POST https://social-agent-hackathon-production.up.railway.app/api/v1/quick/sync-to-hub-now
```

**Expected response:**
```json
{
  "success": true,
  "synced_count": 10,
  "total_posts": 10,
  "errors": []
}
```

### Step 3: Verify Hub Stats
```bash
curl https://social-agent-hackathon-production.up.railway.app/api/v1/hubs/x/stats
```

**Should now show:**
```json
{
  "stats": {
    "keywords": 10,
    "replies": 0
  },
  "keywords": [
    {"term": "#personalfinance", "volume": 0, ...},
    ...
  ],
  "drafts": []
}
```

### Step 4: Refresh Frontend
Hard refresh your browser (Cmd+Shift+R or Ctrl+F5)

---

## Why This Happened

1. **Two-table design:** Discovery stores in `discovered_posts`, Hub reads from `discovered_videos`
2. **Sync endpoint broken:** Schema mismatch between what sync tries to insert and what table expects
3. **SQLite vs Supabase:** Local dev uses SQLite (works), Railway might use different schema
4. **Missing columns:** `discovered_videos` table missing `comments`, `shares` columns

---

## Verification Commands

### Check if data exists in discovered_posts:
```bash
curl 'https://social-agent-hackathon-production.up.railway.app/api/v1/discovery/twitter/posts?limit=1'
```

### Check if Hub can see it:
```bash
curl 'https://social-agent-hackathon-production.up.railway.app/api/v1/hubs/x/stats'
```

### Run sync:
```bash
curl -X POST 'https://social-agent-hackathon-production.up.railway.app/api/v1/quick/sync-to-hub-now'
```

### Verify frontend URL:
Check your Vercel deployment - is it calling the correct Railway backend URL?

---

## Summary

**Data Location:** ✅ Railway database, `discovered_posts` table, 10 tweets  
**Frontend Reading:** `/api/v1/hubs/x/stats` endpoint  
**Problem:** Sync broken, `discovered_videos` table empty  
**Fix:** Quickfix endpoint deploying now  
**ETA:** 1 minute until you can see data

---

**Run this at 5:22 UTC:**
```bash
curl -X POST https://social-agent-hackathon-production.up.railway.app/api/v1/quick/sync-to-hub-now && \
curl https://social-agent-hackathon-production.up.railway.app/api/v1/hubs/x/stats
```

Then refresh your frontend! 🎉
