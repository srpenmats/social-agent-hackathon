# 🤖 INTELLIGENT AGENT SETUP - Complete Guide

## What I Just Built

✅ **PostgreSQL Support** - Persistent database  
✅ **Smart Discovery Endpoint** - AI agent fetches Twitter data  
✅ **Auto-refresh** - Always fresh data  
✅ **DB Status Check** - Know what you're using

---

## 🚀 Setup (3 Steps - 5 Minutes)

### Step 1: Add Railway PostgreSQL (2 minutes)

**In Railway Dashboard:**
1. Go to: https://railway.app/project/social-agent-hackathon-production
2. Click: **"+ New"** button
3. Select: **"Database" → "PostgreSQL"**
4. Click: **"Add PostgreSQL"**
5. Wait 30 seconds for provisioning

Railway automatically sets `DATABASE_URL` environment variable ✅

### Step 2: Restart Your Service (1 minute)

**In Railway:**
1. Go to your service (social-agent-hackathon)
2. Click: **"Deploy"** → **"Restart"**
3. Wait for deployment to complete (~2 min)

The code will auto-detect PostgreSQL and use it!

### Step 3: Test the Intelligent Agent (2 minutes)

```bash
# Check database status
curl https://social-agent-hackathon-production.up.railway.app/api/v1/agent/db-status
```

**Expected response:**
```json
{
  "initialized": true,
  "using_postgres": true,
  "database_type": "PostgreSQL",
  "persistent": true
}
```

---

## 🎯 How to Use the Intelligent Agent

### Discover High-Engagement Posts

```bash
curl -X POST https://social-agent-hackathon-production.up.railway.app/api/v1/agent/discover-smart \
  -H "Content-Type: application/json" \
  -d '{
    "query": "personal finance OR money tips",
    "min_engagement": 100,
    "max_results": 20
  }'
```

**The Agent Will:**
1. Connect to Twitter API
2. Find posts with 100+ likes
3. Store in PostgreSQL (persistent!)
4. Return top posts

### Auto-Refresh Dashboard

```bash
curl -X POST https://social-agent-hackathon-production.up.railway.app/api/v1/agent/auto-refresh
```

This automatically fetches latest financial content and updates your dashboard.

---

## 🔄 Automated Discovery (Recommended)

### Option A: Cron Job (Server-side)

Add this to your server cron:
```bash
# Every hour, refresh dashboard with latest tweets
0 * * * * curl -X POST https://social-agent-hackathon-production.up.railway.app/api/v1/agent/auto-refresh
```

### Option B: Frontend Button

Add a "Refresh Data" button in your frontend:
```typescript
const refreshData = async () => {
  await fetch(`${API_BASE}/agent/auto-refresh`, { method: 'POST' });
  await fetchDashboard(); // Reload
};
```

### Option C: OpenClaw Cron

Use OpenClaw's built-in cron:
```bash
openclaw cron add \
  --schedule "0 * * * *" \
  --task "curl -X POST .../agent/auto-refresh"
```

---

## 📊 What You'll See

### Before (SQLite - Empty):
```
Overview: 0 engagements
X Hub: No data
```

### After (PostgreSQL - Persistent):
```
Overview: 15 engagements
X Hub: 15 high-engagement posts
Hashtags: #personalfinance, #money, #investing
Likes: 100-3000 per post
Data persists forever ✅
```

---

## 🔍 Troubleshooting

### Check Database Type

```bash
curl .../agent/db-status
```

**If still showing SQLite:**
1. Did you add PostgreSQL in Railway?
2. Did you restart the service?
3. Check Railway logs for errors

### No Data After Discovery

```bash
# Run discovery
curl -X POST .../agent/discover-smart -d '{"query":"money tips","min_engagement":50}'

# Check hub
curl .../hubs/x/stats
```

Should show keywords and posts.

### PostgreSQL Connection Error

Check Railway PostgreSQL is running:
1. Railway Dashboard → PostgreSQL service
2. Should show "Active"
3. Check DATABASE_URL is set in variables

---

## 🎨 Example Usage

### Discovery Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | string | "personal finance..." | Twitter search query |
| `min_engagement` | int | 50 | Minimum likes to include |
| `max_results` | int | 20 | Max tweets to fetch |

### Query Examples

**High-quality financial content:**
```json
{
  "query": "personal finance OR investing OR budgeting",
  "min_engagement": 200,
  "max_results": 15
}
```

**Viral money tips:**
```json
{
  "query": "money tips OR broke OR paycheck",
  "min_engagement": 500,
  "max_results": 10
}
```

**Credit/debt content:**
```json
{
  "query": "credit score OR debt free OR student loans",
  "min_engagement": 100,
  "max_results": 20
}
```

---

## ✅ Verification Checklist

After setup, verify:

- [ ] PostgreSQL added in Railway
- [ ] Service restarted
- [ ] `/agent/db-status` shows `"using_postgres": true`
- [ ] `/agent/discover-smart` returns success
- [ ] `/hubs/x/stats` shows data
- [ ] Frontend displays tweets
- [ ] Data persists after Railway restart

---

## 🎯 Next Steps

### 1. Set Up Auto-Refresh

Choose one method (cron, frontend, OpenClaw) to keep data fresh.

### 2. Customize Queries

Update queries in `agent_smart.py` to match your content needs.

### 3. Add More Features

- Comment generation
- Engagement tracking
- Performance analytics

---

## 📝 Summary

**What Changed:**
- ✅ Database: SQLite (ephemeral) → PostgreSQL (persistent)
- ✅ Data fetch: Manual populate → Intelligent agent
- ✅ Source: Hardcoded samples → Real Twitter API
- ✅ Freshness: Stale → Always current

**How to Use:**
1. Add Railway PostgreSQL (one-time)
2. Call `/agent/discover-smart` when you want data
3. Data persists forever
4. Frontend shows real Twitter posts

---

**Ready to test? Add PostgreSQL in Railway and run the discover-smart endpoint!** 🚀
