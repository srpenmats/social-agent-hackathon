# NeoClaw Smart Discovery - Implementation Complete

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│  Frontend (Vercel)                                      │
│  - SmartDiscoveryWidget.tsx (updated)                  │
│  - Polls for results every 2 seconds                   │
└────────────────┬────────────────────────────────────────┘
                 │
                 │ 1. POST /api/v1/discovery/smart-query
                 │ 2. Poll GET /api/v1/discovery/status/:id
                 ↓
┌─────────────────────────────────────────────────────────┐
│  Backend (Railway)                                      │
│  - neoclaw_discovery.py (new)                          │
│  - PostgreSQL tables:                                   │
│    - discovery_queue (pending requests)                │
│    - discovery_results (completed results)             │
│    - discovered_posts (individual posts)               │
└────────────────┬────────────────────────────────────────┘
                 │
                 │ 3. GET /api/v1/discovery/queue (polling)
                 │ 4. POST /api/v1/discovery/complete (results)
                 ↓
┌─────────────────────────────────────────────────────────┐
│  NeoClaw (OpenClaw Agent)                              │
│  - worker.py (polls for work)                          │
│  - processor.py (Jen intelligence)                     │
│  - Uses twclaw (Twitter X API)                         │
│  - Loads Jen context from MEMORY.md                    │
└─────────────────────────────────────────────────────────┘
```

## What Was Built

### 1. Backend Queue System (Railway)

**New File:** `backend/routers/neoclaw_discovery.py`

**Endpoints:**
- `POST /api/v1/discovery/smart-query` - Submit query, get query_id
- `GET /api/v1/discovery/status/{query_id}` - Check status
- `POST /api/v1/discovery/complete` - NeoClaw posts results here
- `GET /api/v1/discovery/queue` - NeoClaw polls for work
- `POST /api/v1/discovery/claim/{query_id}` - Claim a query

**Database Migration:** `backend/db/migrations/007_neoclaw_discovery.sql`

**Tables Created:**
```sql
discovery_queue        -- Pending queries
discovery_results      -- Completed results
discovered_posts       -- Individual posts (reused existing)
```

### 2. NeoClaw Intelligence Layer

**Location:** `~/.openclaw/workspace/neoclaw-discovery/`

**Files:**
- `worker.py` - Polls backend every run, processes pending queries
- `processor.py` - Core intelligence:
  - Loads Jen context from MEMORY.md
  - Generates multi-query search strategy
  - Calls twclaw (Twitter X API skill)
  - Scores posts using Jen framework
  - Returns structured results
- `setup.sh` - Setup and dependency check script
- `README.md` - Documentation

### 3. Frontend Updates

**Updated:** `components/SmartDiscoveryWidget.tsx`

**Changes:**
- Now uses async queue endpoint
- Polls for results every 2 seconds
- Shows "NeoClaw is analyzing..." while processing
- 2-minute timeout with error handling

## How to Deploy

### Step 1: Deploy Backend Changes

```bash
cd ~/.openclaw/workspace/social-agent-hackathon

# Run database migration
# (Railway will auto-migrate on deploy, or run manually)

# Push to git
git add backend/routers/neoclaw_discovery.py
git add backend/db/migrations/007_neoclaw_discovery.sql
git add backend/main.py
git commit -m "feat: Add NeoClaw async discovery queue"
git push origin main

# Railway will auto-deploy
```

### Step 2: Run Database Migration

Connect to Railway PostgreSQL and run:
```bash
# Option A: Via Railway CLI
railway run psql -f backend/db/migrations/007_neoclaw_discovery.sql

# Option B: Add migration endpoint to backend
curl -X POST https://your-backend.railway.app/api/v1/db/migrate
```

### Step 3: Setup NeoClaw Worker

```bash
# Run setup
~/.openclaw/workspace/neoclaw-discovery/setup.sh

# Test manually
python3 ~/.openclaw/workspace/neoclaw-discovery/worker.py

# Or add as OpenClaw cron job (recommended)
# This makes NeoClaw check for work every 2 minutes automatically
```

### Step 4: Deploy Frontend

```bash
# Frontend is already updated in SmartDiscoveryWidget.tsx
# Vercel will auto-deploy on git push

git add components/SmartDiscoveryWidget.tsx
git commit -m "feat: Update SmartDiscoveryWidget for async processing"
git push origin main
```

## How It Works (User Flow)

1. **User enters query:** "Find posts about AI agent security"

2. **Frontend submits to backend:**
   ```
   POST /api/v1/discovery/smart-query
   { "query": "Find posts about AI agent security", "max_results": 10 }
   
   Response: { "query_id": "abc-123", "status": "queued" }
   ```

3. **Backend stores in queue:**
   ```sql
   INSERT INTO discovery_queue (query_id, query_text, status)
   VALUES ('abc-123', 'Find posts...', 'queued');
   ```

4. **Frontend starts polling:**
   ```
   Every 2 seconds: GET /api/v1/discovery/status/abc-123
   Response: { "status": "queued", "message": "Waiting for NeoClaw..." }
   ```

5. **NeoClaw worker runs** (manually or via cron):
   ```bash
   python3 worker.py
   ```
   - Polls: `GET /api/v1/discovery/queue`
   - Sees pending query
   - Claims it: `POST /api/v1/discovery/claim/abc-123`
   - Processes with Jen intelligence:
     * Loads MEMORY.md for Agent Trust Hub context
     * Generates multi-query search strategy
     * Calls `twclaw search` for each query
     * Scores posts using Jen framework
     * Generates context-aware summary

6. **NeoClaw posts results back:**
   ```
   POST /api/v1/discovery/complete
   {
     "query_id": "abc-123",
     "recommendations": [...scored posts...],
     "context_summary": "Found 12 posts about AI agent security..."
   }
   ```

7. **Backend stores results:**
   ```sql
   INSERT INTO discovery_results (query_id, results) VALUES (...);
   INSERT INTO discovered_posts (post_id, ...) VALUES (...);
   UPDATE discovery_queue SET status='complete' WHERE query_id='abc-123';
   ```

8. **Frontend polls again:**
   ```
   GET /api/v1/discovery/status/abc-123
   Response: { "status": "complete", "results": {...} }
   ```

9. **Frontend displays results** with Jen's analysis

## Testing

### Manual Test

```bash
# 1. Start backend (Railway should be running)

# 2. Submit a test query via curl
curl -X POST https://your-backend.railway.app/api/v1/discovery/smart-query \
  -H "Content-Type: application/json" \
  -d '{"query": "AI agent security", "max_results": 10}'

# Response: {"query_id": "...", "status": "queued"}

# 3. Run NeoClaw worker
python3 ~/.openclaw/workspace/neoclaw-discovery/worker.py

# 4. Check status
curl https://your-backend.railway.app/api/v1/discovery/status/{query_id}

# Should show: {"status": "complete", "results": {...}}
```

### Frontend Test

1. Open frontend: https://your-app.vercel.app
2. Navigate to X/Twitter Hub
3. Enter query: "AI agent security vulnerabilities"
4. Click "Discover & Analyze"
5. Watch "NeoClaw is analyzing..." message
6. Results appear in ~20-40 seconds

## Running NeoClaw Worker

### Option 1: Manual (for testing)

```bash
python3 ~/.openclaw/workspace/neoclaw-discovery/worker.py
```

### Option 2: OpenClaw Cron (recommended for production)

Add via OpenClaw chat:
```
"Set up a cron job to run the discovery worker every 2 minutes"
```

Or via CLI:
```bash
openclaw cron add \
  --every 2m \
  --task "Run discovery worker: python3 ~/.openclaw/workspace/neoclaw-discovery/worker.py"
```

### Option 3: System Cron

```bash
crontab -e

# Add this line:
*/2 * * * * cd ~/.openclaw/workspace/neoclaw-discovery && python3 worker.py >> worker.log 2>&1
```

## Environment Variables

### Backend (Railway)

```bash
DATABASE_URL=postgresql://...  # Railway provides automatically
TWITTER_BEARER_TOKEN=your_token
```

### NeoClaw Worker

```bash
BACKEND_URL=https://social-agent-hackathon-production.up.railway.app
TWITTER_BEARER_TOKEN=your_token  # Same as backend
```

## Monitoring

### Check Queue Status

```bash
curl https://your-backend.railway.app/api/v1/discovery/queue
```

### Check Specific Query

```bash
curl https://your-backend.railway.app/api/v1/discovery/status/{query_id}
```

### View Worker Logs

```bash
# If running manually
tail -f ~/.openclaw/workspace/neoclaw-discovery/worker.log

# If running as cron
tail -f /var/log/syslog | grep discovery
```

## Troubleshooting

### "No pending queries" but frontend shows "Processing..."

**Cause:** Worker isn't running or backend can't reach NeoClaw

**Fix:**
```bash
# Run worker manually
python3 ~/.openclaw/workspace/neoclaw-discovery/worker.py
```

### "twclaw command not found"

**Fix:**
```bash
npm install -g twclaw
export TWITTER_BEARER_TOKEN='your_token'
```

### "Backend connection failed"

**Fix:**
```bash
# Check Railway deployment
railway status

# Check DATABASE_URL is set
railway variables
```

### Posts not appearing in frontend

**Check:**
1. Results stored in database?
   ```sql
   SELECT * FROM discovery_results WHERE query_id = '...';
   ```
2. Frontend polling correct endpoint?
   - Check browser Network tab
3. CORS issues?
   - Check backend CORS_ORIGINS includes frontend URL

## Next Steps

### Performance Optimizations

1. **Pre-cache common queries** before demo
2. **Increase worker frequency** (every 30 seconds instead of 2 minutes)
3. **Add Redis** for faster polling (optional)

### User Experience

1. **Show progress messages:**
   - "Queued..." (0-2 sec)
   - "Generating search strategy..." (2-10 sec)
   - "Searching Twitter..." (10-20 sec)
   - "Scoring posts with Jen framework..." (20-30 sec)

2. **Add cancel button** to stop long-running queries

3. **Show queue position** if multiple queries pending

### Monitoring

1. **Add analytics:**
   - Average processing time
   - Success rate
   - Most common queries

2. **Alert on failures:**
   - Email/Slack when query fails
   - Monitor worker health

## Files Changed/Added

### Backend
- ✅ `backend/routers/neoclaw_discovery.py` (NEW)
- ✅ `backend/db/migrations/007_neoclaw_discovery.sql` (NEW)
- ✅ `backend/main.py` (UPDATED - added router)

### NeoClaw Worker
- ✅ `~/.openclaw/workspace/neoclaw-discovery/worker.py` (NEW)
- ✅ `~/.openclaw/workspace/neoclaw-discovery/processor.py` (NEW)
- ✅ `~/.openclaw/workspace/neoclaw-discovery/setup.sh` (NEW)
- ✅ `~/.openclaw/workspace/neoclaw-discovery/README.md` (NEW)

### Frontend
- ✅ `components/SmartDiscoveryWidget.tsx` (UPDATED - async polling)

---

**Status:** ✅ Implementation complete, ready for deployment and testing!
