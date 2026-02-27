# 🔄 Auto-Refresh Setup - Hourly Twitter Data Updates

## What This Does

Automatically refreshes your CashKitty dashboard with fresh Twitter data **every hour**.

---

## Two Ways to Enable

### Option 1: Railway Cron (Recommended)

**Best for:** Production deployment

Railway can automatically call your endpoint every hour using a cron job.

#### Setup Steps:

1. **Add Railway Cron Service** (if available in your plan)
   - Railway Dashboard → New → Cron
   - Schedule: `0 * * * *` (every hour)
   - Command: 
     ```bash
     curl -X POST https://social-agent-hackathon-production.up.railway.app/api/v1/scheduler/hourly-refresh
     ```

2. **Alternative: Use External Cron Service**
   - Use [cron-job.org](https://cron-job.org) (free)
   - Or [EasyCron](https://easycron.com) (free tier)
   - Schedule: Every hour
   - URL: `https://social-agent-hackathon-production.up.railway.app/api/v1/scheduler/hourly-refresh`
   - Method: POST

---

### Option 2: OpenClaw Cron (Your Machine)

**Best for:** Running from your local machine or server with OpenClaw

```bash
openclaw cron add \
  --name "CashKitty Hourly Refresh" \
  --schedule "0 * * * *" \
  --task "curl -X POST https://social-agent-hackathon-production.up.railway.app/api/v1/scheduler/hourly-refresh"
```

**Verify it's running:**
```bash
openclaw cron list
```

---

## Manual Testing

Test the refresh right now:

```bash
curl -X POST https://social-agent-hackathon-production.up.railway.app/api/v1/scheduler/hourly-refresh
```

**Expected response:**
```json
{
  "success": true,
  "timestamp": "2026-02-27T13:15:00Z",
  "auto_refresh": true,
  "stored": 25,
  "message": "Agent discovered 25 high-engagement posts from Twitter"
}
```

---

## Frontend Refresh Button

The **Refresh button** in X/Twitter Hub now calls:
```
POST /api/v1/agent/auto-refresh
```

This fetches fresh data immediately when you click it.

---

## How It Works

### Hourly Auto-Refresh Flow:
```
Cron (every hour)
  ↓
POST /scheduler/hourly-refresh
  ↓
Intelligent Agent Discovery
  ↓
Twitter API (find top posts)
  ↓
PostgreSQL (store)
  ↓
Dashboard updated ✅
```

### Manual Refresh Flow:
```
User clicks "Refresh"
  ↓
POST /agent/auto-refresh
  ↓
Twitter API (find top posts)
  ↓
PostgreSQL (store)
  ↓
Dashboard reloads ✅
```

---

## What Gets Updated

Every refresh discovers:
- **25 high-engagement posts** (100+ likes)
- **Financial topics:** personal finance, money tips, budgeting, investing, debt, savings
- **Fresh data:** Only recent tweets (last 7 days)
- **Stored permanently:** In PostgreSQL

---

## Monitoring

### Check scheduler health:
```bash
curl https://social-agent-hackathon-production.up.railway.app/api/v1/scheduler/health
```

### Check last discovery:
```bash
curl https://social-agent-hackathon-production.up.railway.app/api/v1/hubs/x/stats
```

---

## Configuration

### Change Refresh Frequency

Edit the cron schedule:

| Frequency | Cron Expression |
|-----------|----------------|
| Every 30 minutes | `*/30 * * * *` |
| Every hour | `0 * * * *` |
| Every 2 hours | `0 */2 * * *` |
| Every 6 hours | `0 */6 * * *` |
| Once daily (9 AM) | `0 9 * * *` |

### Change Search Query

Edit `backend/routers/scheduler.py`:
```python
query="personal finance OR money tips OR budgeting"
```

### Change Engagement Threshold

Edit `backend/routers/scheduler.py`:
```python
min_engagement=100  # Raise for higher quality, lower for more volume
```

---

## Troubleshooting

### Cron Not Running

**Check:**
1. Is the cron service actually calling the endpoint?
2. Check Railway logs for errors
3. Test manually with `curl -X POST .../scheduler/hourly-refresh`

### No New Data After Refresh

**Possible causes:**
1. **Twitter API rate limit** - Wait 15 minutes
2. **No qualifying posts** - Lower `min_engagement` threshold
3. **Query too narrow** - Broaden search terms

**Check rate limit:**
```bash
curl https://social-agent-hackathon-production.up.railway.app/api/v1/agent/db-status
```

### Duplicate Refreshes

The scheduler has a lock to prevent overlapping runs. If a refresh is already running, new requests will skip and return `"skipped": true`.

---

## Performance

- **API calls:** 1 Twitter API call per hour = 24/day (well under 180/15min limit)
- **Database writes:** ~25 rows per hour (negligible PostgreSQL usage)
- **Cost:** Free tier handles this easily

---

## Next Steps

1. **Set up cron** (choose Option 1 or 2)
2. **Test it:** Run manual refresh to verify
3. **Monitor:** Check hourly that new data appears
4. **Customize:** Adjust query/threshold if needed

---

## Quick Start Command

**Test everything right now:**

```bash
# Test manual refresh
curl -X POST https://social-agent-hackathon-production.up.railway.app/api/v1/scheduler/hourly-refresh

# Wait 3 seconds
sleep 3

# Check results
curl https://social-agent-hackathon-production.up.railway.app/api/v1/hubs/x/stats | python3 -m json.tool
```

**Then set up cron for hourly automation!**

---

**That's it! Your dashboard will now stay fresh automatically.** 🎉
