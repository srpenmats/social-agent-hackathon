# 🐱 CashKitty Command Hub - Connect to Real Twitter Metrics

## Quick Answer: 3 Steps to See Real Data

```bash
# Step 1: Wait for Railway deployment (~2 min from now)
sleep 120

# Step 2: Discover real tweets
curl -X POST https://social-agent-hackathon-production.up.railway.app/api/v1/discovery/twitter/search \
  -H "Content-Type: application/json" \
  -d '{"query": "personal finance OR budgeting OR saving money", "max_results": 20}'

# Step 3: Sync to Hub
curl -X POST https://social-agent-hackathon-production.up.railway.app/api/v1/discovery/sync-to-hub

# Done! Refresh your X Hub in the browser
```

---

## 🎯 Current Status

✅ **Frontend**: Deployed and ready
✅ **Backend**: Live on Railway  
✅ **TWITTER_BEARER_TOKEN**: Set in environment
✅ **SQLite fix**: Deploying now (~2 minutes)
✅ **Discovery API**: Ready to use

---

## 📊 What CashKitty Command Hub Shows

Your X/Twitter Hub displays:

### 1. Stats Cards (Top Row)
- **Mentions Replied**: Count of your actual replies
- **Keywords Triggered**: Number of relevant tweets found
- **Avg Sentiment**: Calculated from engagement
- **API Quota**: Twitter API rate limit status

### 2. Keyword Streams (Left Panel)
- Real hashtags from discovered tweets
- Sample tweet text
- Engagement volume (likes on original tweets)
- "Monitor" status for each keyword

### 3. High-Risk Drafts (Right Panel)
- AI-generated comment candidates
- Original tweet context
- Risk score (0-100)
- Approve/Reject/Edit buttons

---

## 🔄 Complete Workflow

### Discover → Generate → Review → Post

```bash
# 1. DISCOVER: Find relevant tweets
curl -X POST https://social-agent-hackathon-production.up.railway.app/api/v1/discovery/twitter/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "personal finance OR money tips OR budgeting",
    "max_results": 20
  }'

# Response shows found tweets
# {"success": true, "found": 20, "stored": 20, "tweets": [...]}

# 2. GENERATE: Create AI comment candidates
# (Get tweet ID from step 1 response)
curl -X POST https://social-agent-hackathon-production.up.railway.app/api/v1/discovery/generate-comment \
  -H "Content-Type: application/json" \
  -d '{
    "post_id": "2027242068272111899",
    "tweet_text": "Simple financial tip: track your spending",
    "author_username": "finance_expert",
    "num_candidates": 3,
    "tone": "casual"
  }'

# Response shows generated comments
# {"success": true, "candidates_generated": 3, "candidates": [...]}

# 3. SYNC: Make visible in Hub
curl -X POST https://social-agent-hackathon-production.up.railway.app/api/v1/discovery/sync-to-hub

# Response confirms sync
# {"success": true, "synced_count": 20}

# 4. REVIEW: Open X Hub in browser → See drafts → Approve/Reject

# 5. POST: (Future feature - post approved comments to Twitter)
```

---

## 🎨 Example Queries for CashKitty

### Personal Finance Content
```bash
curl -X POST https://social-agent-hackathon-production.up.railway.app/api/v1/discovery/twitter/search \
  -H "Content-Type: application/json" \
  -d '{"query": "personal finance OR budgeting OR financial literacy", "max_results": 20}'
```

### Money Tips & Advice
```bash
curl -X POST https://social-agent-hackathon-production.up.railway.app/api/v1/discovery/twitter/search \
  -H "Content-Type: application/json" \
  -d '{"query": "money tips OR saving money OR broke OR paycheck", "max_results": 20}'
```

### Student Finance
```bash
curl -X POST https://social-agent-hackathon-production.up.railway.app/api/v1/discovery/twitter/search \
  -H "Content-Type: application/json" \
  -d '{"query": "student loans OR college debt OR financial aid", "max_results": 20}'
```

### Credit & Banking
```bash
curl -X POST https://social-agent-hackathon-production.up.railway.app/api/v1/discovery/twitter/search \
  -H "Content-Type: application/json" \
  -d '{"query": "credit score OR banking OR credit card tips", "max_results": 20}'
```

---

## 🤖 Comment Tone Options

CashKitty can respond in different tones:

### Casual (Default - Cash Kitty Voice)
```json
{
  "tone": "casual",
  "example": "ngl this is the financial literacy content we need more of. the kitty approves 🐱"
}
```

### Professional
```json
{
  "tone": "professional",
  "example": "Great insights on financial management. This aligns with evidence-based approaches to personal finance."
}
```

### Humorous
```json
{
  "tone": "humorous",
  "example": "My savings account just woke up and said 'finally, someone gets it' 😹"
}
```

### Technical
```json
{
  "tone": "technical",
  "example": "This budget optimization approach shows strong correlation with improved savings rates across multiple income brackets."
}
```

---

## 📈 Real Metrics You'll See

### Discovered Tweet Example:
```json
{
  "id": "2027242068272111899",
  "text": "Simple financial knowledge tip: It's small decisions that determine your financial future",
  "author_username": "mabele2003",
  "author_name": "Financial Expert",
  "likes": 1250,
  "retweets": 380,
  "replies": 67,
  "url": "https://twitter.com/mabele2003/status/..."
}
```

### Generated Comment Example:
```json
{
  "text": "the small decisions matter. but the big ones like rent, student loans, healthcare - those eat up everything before you get to the 'small' stuff",
  "risk_score": 25,
  "confidence": 0.85,
  "classification": "financial-education"
}
```

---

## 🎯 Testing Right Now (Step by Step)

### Test 1: Health Check
```bash
curl https://social-agent-hackathon-production.up.railway.app/api/v1/health
# Expected: {"status":"ok"}
```

### Test 2: Wait for Deployment
```bash
# Railway is deploying the SQLite fix now
# Wait ~2 minutes from 5:08 UTC = ready at ~5:10 UTC
sleep 120
```

### Test 3: Discover Financial Tweets
```bash
curl -X POST https://social-agent-hackathon-production.up.railway.app/api/v1/discovery/twitter/search \
  -H "Content-Type: application/json" \
  -d '{"query": "money tips OR personal finance", "max_results": 15}'
```

### Test 4: Check Discovered Posts
```bash
curl https://social-agent-hackathon-production.up.railway.app/api/v1/discovery/twitter/posts?limit=5
```

### Test 5: Sync to Hub
```bash
curl -X POST https://social-agent-hackathon-production.up.railway.app/api/v1/discovery/sync-to-hub
```

### Test 6: View Hub Stats
```bash
curl https://social-agent-hackathon-production.up.railway.app/api/v1/hubs/x/stats
# Should show keywords, drafts, etc.
```

---

## 🖥️ Frontend: Opening CashKitty Command Hub

1. **Navigate to your frontend URL**
   - Vercel: `https://your-app.vercel.app`
   - Or wherever your frontend is deployed

2. **Click "X / Twitter Hub" in sidebar**

3. **Click "Refresh" button** (after running discovery + sync)

4. **You'll see:**
   - Real stats from Twitter
   - Keyword streams with #finance, #money, etc.
   - Pending drafts ready for review
   - Clickable tweet URLs

---

## ⚙️ Frontend Refresh Button (Optional Enhancement)

To make the Refresh button automatically trigger discovery:

Edit `screens/XHub.tsx`:

```typescript
const handleRefresh = async () => {
  setRefreshing(true);
  try {
    // Discover financial tweets
    await fetch(`${API_BASE}/discovery/twitter/search`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query: "personal finance OR money tips OR budgeting",
        max_results: 20
      })
    });
    
    // Wait for completion
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    // Sync to Hub
    await fetch(`${API_BASE}/discovery/sync-to-hub`, { method: 'POST' });
    
    // Reload data
    await fetchData();
  } catch (e) {
    console.error('Refresh failed:', e);
  }
  setRefreshing(false);
};
```

---

## 🚨 Troubleshooting

### "Discovery failed" error
→ Railway still deploying, wait 2 more minutes

### No tweets found
→ Try broader query: `"money OR finance OR budget"`

### Data doesn't appear in Hub
→ Make sure you ran the sync-to-hub endpoint

### Refresh button does nothing
→ Check browser console for API errors
→ Verify Railway URL is correct in frontend

---

## ⏱️ Timeline

| Task | Time | Status |
|------|------|--------|
| SQLite fix deployed | ~2 min | ⏳ Deploying |
| Discover tweets | 3 sec | ⏳ Ready soon |
| Sync to Hub | 1 sec | ⏳ Ready soon |
| See in browser | Instant | ⏳ Ready soon |
| **Total** | **~2-3 min** | **Almost there!** |

---

## ✅ Success Checklist

After running the commands above, you should have:

- [ ] 15-20 real tweets discovered
- [ ] Tweets visible in discovered_posts table
- [ ] Keyword streams populated (#finance, #money, #budget)
- [ ] Stats cards showing real numbers
- [ ] Clickable tweet URLs
- [ ] Real engagement metrics (likes, retweets, replies)

---

## 🎉 What You'll See (Screenshot Description)

```
┌──────────────────────────────────────────────────────────┐
│ Cash Kitty Command Hub                     [🔄 Refresh]  │
├──────────────────────────────────────────────────────────┤
│ 📊 Stats                                                 │
│ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐    │
│ │    15    │ │    20    │ │   82%    │ │   95%    │    │
│ │ Replies  │ │ Keywords │ │Sentiment │ │  Quota   │    │
│ └──────────┘ └──────────┘ └──────────┘ └──────────┘    │
├──────────────────────────────────────────────────────────┤
│ Keyword Streams          │ High-Risk Drafts (3)         │
│ ┌──────────────────────┐ │ ┌──────────────────────────┐ │
│ │ #personalfinance     │ │ │ Replying to @user1       │ │
│ │ "track your spending"│ │ │ "ngl this is the...      │ │
│ │ 🔥 Volume: 1,250     │ │ │ Risk: 18                 │ │
│ └──────────────────────┘ │ │ [Approve][Reject][Edit]  │ │
│ ┌──────────────────────┐ │ └──────────────────────────┘ │
│ │ #budgeting           │ │ ┌──────────────────────────┐ │
│ │ "save more money..."  │ │ │ Replying to @user2       │ │
│ │ 🔥 Volume: 890       │ │ │ "ok but why is...        │ │
│ └──────────────────────┘ │ │ Risk: 12                 │ │
│                          │ │ [Approve][Reject][Edit]  │ │
│                          │ └──────────────────────────┘ │
└──────────────────────────┴──────────────────────────────┘
```

---

**🚀 You're ready! In ~2 minutes (at 5:10 UTC), run the discover + sync commands and see real Twitter data in CashKitty Command Hub!**
