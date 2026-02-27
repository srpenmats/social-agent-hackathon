# 📊 Overview Tab - Twitter Engagement Data

## What You Asked About

The **Overview tab** shows:
- Total Engagements
- Auto-Approval Rate  
- Pending Reviews
- Platform Health (TikTok, Instagram, X/Twitter)
- Engagement Timeline Chart

Currently it shows **all zeros** because the `engagements` table is empty.

---

## ✅ Solution (Ready at 5:35 UTC)

Run these TWO commands:

### 1. Populate Tweets (Already Done ✅)
```bash
curl -X POST https://social-agent-hackathon-production.up.railway.app/api/v1/populate/now
```

### 2. Populate Engagements (NEW)
```bash
curl -X POST https://social-agent-hackathon-production.up.railway.app/api/v1/populate/engagements
```

---

## What This Does

Creates **5 Twitter engagements** with full metrics:

| Metric | Range |
|--------|-------|
| **Likes** | 50-500 per engagement |
| **Replies** | 5-50 per engagement |
| **Impressions** | 1,000-10,000 per engagement |
| **Risk Score** | 10-30 (low-moderate) |
| **Status** | Posted |
| **Timestamps** | Last 48 hours |

---

## What You'll See in Overview Tab

### Top Stats:
```
📊 Total Engagements: 5
✅ Auto-Approval Rate: 0% (manually approved)
📋 Pending Reviews: 0
```

### Platform Health - X / Twitter:
```
🐦 X / Twitter
Status: ● Active (green)
Comments: 5
Avg Risk: 18%
```

### Engagement Timeline:
Chart showing activity over last 24 hours with data points.

---

## Complete Setup (Both Tabs)

```bash
# 1. Populate tweets (for X Hub)
curl -X POST .../populate/now

# 2. Populate engagements (for Overview)
curl -X POST .../populate/engagements

# 3. Verify Overview
curl .../dashboard/overview?timeframe=7d

# 4. Verify X Hub
curl .../hubs/x/stats
```

---

## Automated Script

```bash
cd /home/ubuntu/.openclaw/workspace/social-agent-hackathon
./populate-all.sh
```

This runs both populate commands and verifies the data.

---

## What Data Looks Like

### Sample Engagement:
```json
{
  "platform": "x",
  "video_id": 1,
  "comment_text": "Great insights! This is exactly what people need to hear about personal finance. 💰",
  "risk_score": 18,
  "posted_at": "2026-02-26T15:22:00Z",
  "status": "posted",
  "metrics": {
    "likes": 234,
    "replies": 23,
    "impressions": 4500
  }
}
```

---

## Timeline

| Task | Time | Status |
|------|------|--------|
| Populate tweets | 5:32 UTC | ✅ Done |
| Deploy engagements endpoint | ~2 min | ⏳ Deploying |
| Ready at | 5:35 UTC | ⏳ Soon |
| Run populate/engagements | 1 sec | ⏳ Ready soon |
| Refresh frontend | Instant | ⏳ Ready soon |

---

## Testing

### Check Overview Data:
```bash
curl https://social-agent-hackathon-production.up.railway.app/api/v1/dashboard/overview?timeframe=7d \
  | python3 -m json.tool
```

**Should show:**
- `"total_engagements": 5`
- `"active_platforms": 3`
- X/Twitter with 5 comments

### Check X Hub Data:
```bash
curl https://social-agent-hackathon-production.up.railway.app/api/v1/hubs/x/stats
```

**Should show:**
- `"replies": 5`
- `"keywords": 5+`
- Hashtags from tweets

---

## Frontend Result

### Overview Tab:
- ✅ Charts populated with activity
- ✅ X/Twitter shows 5 engagements
- ✅ Metrics visible
- ✅ Real timestamps

### X / Twitter Hub:
- ✅ 5 tweets visible
- ✅ Keyword streams populated
- ✅ Engagement counts

---

## At 5:35 UTC, Run:

```bash
curl -X POST https://social-agent-hackathon-production.up.railway.app/api/v1/populate/engagements
```

Then refresh your frontend Overview tab! 🎉
