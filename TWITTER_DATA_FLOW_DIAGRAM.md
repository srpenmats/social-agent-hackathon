# Twitter Data Flow - Current vs. Desired State

## Current State (Disconnected)

```
┌─────────────────────────────────────────────────────────────┐
│                     TWITTER API                              │
│              (Not Connected to UI)                           │
└─────────────────────────────────────────────────────────────┘
                              │
                              ↓
┌─────────────────────────────────────────────────────────────┐
│            Backend Discovery System                          │
│  /api/v1/discovery/start → discovered_posts table           │
│  (Data exists but not visible in UI)                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ↓
                         ❌ GAP ❌
                              │
                              ↓
┌─────────────────────────────────────────────────────────────┐
│              Hub Stats Endpoint                              │
│  /api/v1/hubs/x/stats → reads discovered_videos table       │
│  (Different table, no data)                                 │
└─────────────────────────────────────────────────────────────┘
                              │
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                 Frontend X Hub                               │
│              (Shows empty state)                             │
└─────────────────────────────────────────────────────────────┘
```

## Desired State (Connected)

```
┌─────────────────────────────────────────────────────────────┐
│                     TWITTER API                              │
│         (Bearer Token configured on Railway)                 │
└─────────────────────────────────────────────────────────────┘
                              │
                              ↓
┌─────────────────────────────────────────────────────────────┐
│         Backend Discovery System                             │
│  POST /api/v1/discovery/start                               │
│  → Calls Twitter API                                        │
│  → Stores in discovered_posts table                         │
│  → Returns job_id                                           │
└─────────────────────────────────────────────────────────────┘
                              │
                              ↓
┌─────────────────────────────────────────────────────────────┐
│         ✅ NEW: Bridge Service                               │
│  POST /api/v1/discovery/sync-to-hub                         │
│  → Copies discovered_posts → discovered_videos              │
│  → Extracts hashtags                                        │
│  → Formats for Hub display                                  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ↓
┌─────────────────────────────────────────────────────────────┐
│              Hub Stats Endpoint                              │
│  GET /api/v1/hubs/x/stats                                   │
│  → Reads discovered_videos (now populated)                  │
│  → Returns stats, keywords, drafts                          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ↓
┌─────────────────────────────────────────────────────────────┐
│         ✅ Frontend X Hub (Updated)                          │
│  Refresh button triggers:                                   │
│  1. Discovery                                               │
│  2. Bridge sync                                             │
│  3. Stats refresh                                           │
│  → Displays real Twitter data                               │
└─────────────────────────────────────────────────────────────┘
```

## Data Tables

### Current Tables

```
discovered_posts           discovered_videos        review_queue
├─ id                     ├─ id                    ├─ id
├─ platform (x)           ├─ platform (x)          ├─ video_id (FK)
├─ post_id                ├─ video_url             ├─ proposed_text
├─ post_url               ├─ creator               ├─ risk_score
├─ post_text              ├─ description           ├─ classification
├─ author_username        ├─ hashtags (JSON)       ├─ decision
├─ likes                  ├─ likes                 └─ queued_at
├─ retweets               ├─ comments
├─ replies                ├─ shares
├─ status                 ├─ status
└─ discovered_at          └─ engaged

❌ NOT CONNECTED           ✅ USED BY HUB          ✅ USED BY HUB
```

### Bridge Transforms

```
discovered_posts          →    discovered_videos
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
platform: "x"             →    platform: "x"
post_url                  →    video_url
author_username           →    creator: "@username"
post_text                 →    description
extract_hashtags(text)    →    hashtags: ["#ai", "#security"]
likes                     →    likes
replies                   →    comments
retweets                  →    shares
status: "discovered"      →    status: "discovered"
discovered_at             →    discovered_at
```

## User Journey

### Current Experience:
1. User opens X Hub
2. Sees "No data" or demo data
3. Clicks "Refresh"
4. Nothing happens (no real data)

### After Implementation:
1. User opens X Hub
2. ✅ Sees real tweets from Twitter
3. Clicks "Refresh"
4. ✅ New tweets discovered
5. ✅ Hashtags populated from real tweets
6. ✅ Can click through to actual tweets on Twitter
7. ✅ Sees engagement metrics (likes, retweets, replies)

## Configuration Required

### Railway Environment Variables

```bash
# Required for discovery (read-only)
TWITTER_BEARER_TOKEN=AAA...xyz

# Optional for posting
TWITTER_API_KEY=VSGz...D7
TWITTER_API_SECRET=H2BN...MT
TWITTER_ACCESS_TOKEN=2024...CX
TWITTER_ACCESS_TOKEN_SECRET=aaEx...ce
TWITTER_USER_ID=2024576960668860416
```

## Implementation Checklist

### Phase 1: Setup (10 min)
- [ ] Get Twitter Bearer Token from developer portal
- [ ] Add `TWITTER_BEARER_TOKEN` to Railway env vars
- [ ] Deploy changes

### Phase 2: Bridge Service (45 min)
- [ ] Create `backend/services/discovery_bridge.py`
- [ ] Add `extract_hashtags()` function
- [ ] Add `sync_discovered_posts_to_videos()` function
- [ ] Test bridge logic locally

### Phase 3: API Endpoint (15 min)
- [ ] Add sync endpoint to `backend/routers/discovery.py`
- [ ] Test endpoint with curl
- [ ] Verify data appears in discovered_videos table

### Phase 4: Frontend Integration (20 min)
- [ ] Update `handleRefresh()` in `screens/XHub.tsx`
- [ ] Add discovery trigger
- [ ] Add sync call
- [ ] Add loading states
- [ ] Test in browser

### Phase 5: Deploy & Test (10 min)
- [ ] Commit changes
- [ ] Push to GitHub
- [ ] Railway auto-deploys
- [ ] Test on production URL
- [ ] Verify real Twitter data displays

---

## Alternative: Quick Demo

If you want to see the UI **working right now** without Twitter API:

```sql
-- Run this SQL in Railway database
INSERT INTO discovered_videos (platform, video_url, creator, description, hashtags, likes, comments, status)
VALUES 
  ('x', 'https://x.com/sama/status/123', '@sama', 'AI agents need robust security frameworks', '["#AI", "#security"]', 1200, 67, 'discovered'),
  ('x', 'https://x.com/karpathy/status/456', '@karpathy', 'Building autonomous agent systems', '["#agents", "#ML"]', 890, 45, 'discovered');
```

Refresh X Hub → see demo data immediately.

---

## Summary

**Problem:** X Hub shows no data because discovery system writes to different table.

**Solution:** Create a bridge that syncs `discovered_posts` → `discovered_videos`.

**Result:** Real Twitter data flows through entire system and displays in UI.

**Time:** ~90 minutes of focused work.

**Next:** Build comment generation → review workflow → posting automation.
