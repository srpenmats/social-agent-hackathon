# OpenClaw as Intelligent Bridge - Setup Guide

## Architecture

```
Frontend (Vercel)
    ↓
Backend API (Railway)
    ↓
    ├─→ Task Queue (creates tasks)
    ↓
OpenClaw Agent (GenClaw) - Polls task queue
    ↓
    ├─→ Twitter X API Skill
    ├─→ Claude (with RAG)
    ├─→ Agent Trust Hub Knowledge
    ↓
    └─→ Completes tasks, returns data to backend
```

**This is the NeoClaw pattern!** The backend is already set up for this.

---

## What's Already Built ✅

The codebase **already has NeoClaw integration**:

1. **Task Queue System** (`backend/services/neoclaw_queue.py`)
   - Create tasks
   - Claim tasks
   - Complete/fail tasks
   - Kill switch support

2. **NeoClaw API Router** (`backend/routers/neoclaw.py`)
   - Agent authentication (API key)
   - Task polling endpoint
   - Task completion endpoint
   - Video/content ingestion
   - Metrics reporting

3. **Integration Points:**
   - Discovery service can create tasks
   - Comment generation can be task-based
   - Agent polls for work

---

## How It Works

### Step 1: Backend Creates Tasks

When discovery runs:
```python
# Backend creates a task
task_queue.create_task(
    task_type="discover_twitter_posts",
    platform="x",
    payload={
        "query": "AI agent security",
        "max_results": 10
    }
)
```

### Step 2: OpenClaw Agent (You!) Polls for Tasks

I (GenClaw) can:
```python
# Poll for next task
GET /api/v1/neoclaw/tasks/next?platform=x
Authorization: Bearer <NEOCLAW_API_KEY>
```

### Step 3: I Execute Using Skills

When I get a task:
1. Use **Twitter X API skill** to search
2. Analyze with my intelligence
3. Score relevance
4. Generate comments (if needed)

### Step 4: I Complete the Task

```python
# Report results back
POST /api/v1/neoclaw/tasks/{task_id}/complete
{
    "result": {
        "tweets": [...],
        "scored": true,
        "generated_comments": [...]
    }
}
```

---

## Railway Setup for NeoClaw Integration

### Required Environment Variables

Add these to Railway backend:

**1. NeoClaw API Key**
```
NEOCLAW_API_KEY=your-secure-random-key-here
```

Generate one:
```bash
openssl rand -hex 32
```

**2. OpenClaw Base URL (Optional)**
```
OPENCLAW_BASE_URL=http://localhost:8080
```
(Only needed if backend needs to push to OpenClaw)

---

## OpenClaw Agent Setup

### Option 1: I Run as a Polling Agent

I can run a background process that:
1. Polls `/api/v1/neoclaw/tasks/next` every N seconds
2. Claims tasks
3. Executes using my skills
4. Reports results

**To set this up:**
- Create a cron job in OpenClaw that runs every minute
- Calls the polling logic
- Processes tasks

### Option 2: Backend Invokes Me Directly

Backend can call OpenClaw's agent invocation API:
```python
# Backend invokes OpenClaw agent
POST https://your-openclaw-gateway/api/invoke/genclaw
{
    "command": "process_twitter_discovery",
    "params": {
        "query": "AI agent security"
    }
}
```

---

## Current State: What's Missing

### ✅ Already Built:
- Task queue system
- NeoClaw API endpoints
- Authentication
- Task lifecycle management

### ⚠️ Need to Configure:
1. **NEOCLAW_API_KEY** in Railway
2. **Agent polling logic** (I can help build this)
3. **Task creation** in discovery service
4. **My skills integration** (Twitter X API)

### ❌ Not Yet Built:
- Automatic task creation when discovery runs
- My polling worker implementation
- Skills → Task results mapping

---

## Quick Setup: NeoClaw Integration

### Step 1: Generate NeoClaw API Key

Run locally or use:
```
neoclaw-api-key-d4e8f9a2b5c7e1f3a6d8c9b4e7f2a5c8d1e4f7a9b2c5e8
```

### Step 2: Add to Railway

In Railway → Backend → Variables:

**Key:** `NEOCLAW_API_KEY`
**Value:** (paste the generated key above)

### Step 3: Test NeoClaw Endpoint

After deployment:
```bash
curl -X GET \
  https://your-backend.railway.app/api/v1/neoclaw/tasks/next \
  -H "X-API-Key: neoclaw-api-key-d4e8f9a2b5c7e1f3a6d8c9b4e7f2a5c8d1e4f7a9b2c5e8"
```

Should return:
```json
{"task": null}
```
(No tasks yet, but endpoint works)

### Step 4: I Can Start Polling

Once deployed, I (GenClaw) can:
1. Poll for tasks using the NeoClaw API
2. Execute using my Twitter X API skill
3. Return results to the backend

---

## Making Me the Intelligence Layer

### What I'll Do:

**1. Twitter Discovery:**
- Poll backend for discovery tasks
- Use Twitter X API skill to search
- Apply intelligent filtering
- Score relevance using my AI
- Return structured results

**2. Comment Generation:**
- Receive post + context from backend
- Use Claude with RAG (through me)
- Apply persona blending
- Generate multiple candidates
- Return with confidence scores

**3. Learning & Optimization:**
- Track what works
- Adjust strategies
- Improve over time
- Report insights

---

## Recommendation: Hybrid Approach

**For this demo, do both:**

### Phase 1 (Current): Direct Integration ✅
- Backend uses Twitter API directly
- Fast, reliable, already built
- **Deploy this first to Railway**

### Phase 2 (Next): Add OpenClaw Layer 🌟
- Backend creates tasks for me
- I poll and execute using skills
- Showcase intelligent orchestration
- **This is the "wow" factor**

**Why hybrid:**
- Phase 1 works immediately (demo-ready)
- Phase 2 shows OpenClaw's value (differentiation)
- Can switch between modes
- Best of both worlds

---

## Next Steps

### To Deploy Now (Phase 1):
1. ✅ Add `NEOCLAW_API_KEY` to Railway (even if not using yet)
2. ✅ Complete Railway deployment
3. ✅ Test direct Twitter integration
4. ✅ Get the demo working

### To Add OpenClaw Intelligence (Phase 2):
1. Build task creation in discovery service
2. I create a polling worker
3. Integrate my Twitter X API skill
4. Test task-based flow
5. Showcase intelligent orchestration

---

## TL;DR

**You're right!** OpenClaw should be the intelligent bridge.

**Good news:** The backend is already built for this (NeoClaw integration exists!)

**Current status:** Backend can work standalone OR with OpenClaw

**For deployment:**
1. Add `NEOCLAW_API_KEY` to Railway (use: `neoclaw-api-key-d4e8f9a2b5c7e1f3a6d8c9b4e7f2a5c8d1e4f7a9b2c5e8`)
2. Deploy everything (Phase 1 works immediately)
3. Then we build Phase 2 (me as the intelligence layer)

**Ready to add the NeoClaw API key and continue deployment?** 🚀
