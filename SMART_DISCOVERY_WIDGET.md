# SMART DISCOVERY WIDGET - X/Twitter Hub

## Overview

New widget for X/Twitter Hub that lets users input keywords/context and get AI-powered post discovery with recommendation scores.

## User Flow

```
1. User opens X/Twitter Hub
2. Sees new "Smart Discovery" widget
3. Enters keywords (e.g., "OpenClaw security" or "AI agent vulnerabilities")
4. Sets min engagement threshold (default: 100 likes)
5. Clicks "Discover & Analyze"
6. GenClaw:
   - Searches Twitter API for matching posts
   - Analyzes each post for relevance
   - Scores recommendation potential (0-10)
   - Returns ranked results
7. User sees:
   - Top recommendations with scores
   - Persona recommendation (Observer/Advisor/Connector)
   - Risk level (Green/Yellow/Red)
   - Suggested angle
   - Reasoning for score
8. User can click to view post or add to queue
```

---

## API Endpoint

### POST `/api/v1/hubs/x/smart-discovery`

**Request:**
```json
{
  "query": "OpenClaw security nightmare",
  "min_engagement": 100,
  "max_results": 10
}
```

**Response:**
```json
{
  "query": "OpenClaw security nightmare",
  "found_posts": 15,
  "analyzed_posts": 12,
  "top_post": {
    "post_id": "2025336865130152240",
    "author": "chiefofautism",
    "text": "Andrej Karpathy just called OpenClaw a SECURITY nightmare...",
    "url": "https://twitter.com/...",
    "likes": 1629,
    "retweets": 119,
    "replies": 81,
    "relevance_score": 9.5,
    "engagement_potential": 8.7,
    "persona_recommendation": "Advisor",
    "risk_level": "Yellow",
    "angle_summary": "Validate security concerns with Gen research (15% malicious skills)",
    "recommendation_score": 9.2,
    "reasoning": "Relevance: 9.5/10 | Engagement: 8.7/10 | Risk: Yellow | High relevance to Agent Trust Hub | Strong engagement potential | Needs human review (high-profile)"
  },
  "recommendations": [...]
}
```

---

## Scoring Algorithm

### Relevance Score (0-10)

Keyword-based scoring:
- "openclaw": +3.0
- "ai agent": +2.5
- "autonomous": +2.0
- "security": +2.0
- "malicious": +2.5
- "skill"/"plugin": +1.5
- "vulnerability"/"threat": +2.0/+1.5
- "agentic": +2.0

Max: 10.0

### Engagement Potential (0-10)

Formula:
```
(likes / 200) * 3 +     // Up to 3 points
(retweets / 50) * 2 +   // Up to 2 points
(replies / 20) * 5      // Up to 5 points (discussion)
```

Max: 10.0

### Risk Level

- **Red**: Relevance < 3 (not worth engaging)
- **Yellow**: High-profile (>5K likes or mentions Karpathy/Musk/etc)
- **Green**: Safe to engage

### Recommendation Score (0-10)

Overall formula:
```
(relevance * 0.5) +      // 50% weight
(engagement * 0.3) +     // 30% weight
(risk_factor * 0.2)      // 20% weight

risk_factor:
  Green: 10
  Yellow: 6
  Red: 2
```

---

## Persona Recommendation

| Relevance | Persona | Reasoning |
|-----------|---------|-----------|
| 7-10 | **Advisor** | High relevance = security expertise needed |
| 4-6 | **Connector** | Medium relevance = solution mention fits |
| 0-3 | **Observer** | Low relevance = data sharing only |

---

## Angle Suggestions

Based on post content keywords:

| Keywords | Suggested Angle |
|----------|----------------|
| "openclaw" + "security" | Validate concerns with Gen research (15% malicious) |
| "ai agent" + "skill/plugin" | Mention Agent Trust Hub Scanner (free verification) |
| "autonomous" or "agentic" | Discuss OWASP LLM risks (supply chain, agency) |
| Generic | General security perspective with industry context |

---

## Data Storage

Top 5 recommendations are automatically stored in `discovered_videos` for tracking:
- Platform: "x"
- Engagement score: `recommendation_score * 10`
- Hashtags: Contains search query for tracking

---

## Frontend Integration

### Widget Location
X/Twitter Hub page, below "Keyword Streams" widget

### UI Components

**Input Section:**
```
┌─────────────────────────────────────────┐
│ Smart Discovery                         │
├─────────────────────────────────────────┤
│ Search Keywords:                        │
│ [                                     ] │
│                                         │
│ Min Engagement: [100  ] likes           │
│                                         │
│ [Discover & Analyze]                    │
└─────────────────────────────────────────┘
```

**Results Section:**
```
┌─────────────────────────────────────────┐
│ Recommendations (3 found)               │
├─────────────────────────────────────────┤
│ 🔥 9.2/10 - @chiefofautism (1.6K likes)│
│ "Andrej Karpathy called OpenClaw..."   │
│                                         │
│ Persona: Advisor | Risk: ⚠️ Yellow     │
│ Angle: Validate security concerns...    │
│                                         │
│ [View Post] [Add to Queue]              │
├─────────────────────────────────────────┤
│ 🔥 8.5/10 - @EasyClaw (219 likes)      │
│ ...                                     │
└─────────────────────────────────────────┘
```

---

## Example Usage

### Use Case 1: Breaking News Response
**Query:** "OpenClaw security"
**Result:** Finds Karpathy tweet (9.2/10), suggests Advisor persona, Yellow risk
**Action:** User sees high recommendation, clicks "Add to Queue" for human review

### Use Case 2: Daily Monitoring
**Query:** "AI agent marketplace"
**Result:** Finds 5 posts about skill stores (6-8/10 scores)
**Action:** GenClaw suggests Connector persona, links to Agent Trust Hub

### Use Case 3: Industry Trends
**Query:** "autonomous agent vulnerabilities"
**Result:** Discovers academic discussions, suggests Observer persona
**Action:** User sees moderate scores, decides to monitor but not engage immediately

---

## Benefits

1. **User Control**: Users define what to search for (not just pre-configured keywords)
2. **AI Analysis**: GenClaw does the hard work (relevance, scoring, persona)
3. **Actionable Insights**: Clear recommendation scores + reasoning
4. **Time Savings**: Filter 100+ posts down to top 3-5 worth reviewing
5. **Context Awareness**: Scoring considers Agent Trust Hub relevance specifically

---

## Next Steps

1. **Backend**: ✅ Endpoint created (`smart_discovery.py`)
2. **Integration**: ✅ Added to `main.py`
3. **Frontend**: Build React component for X Hub
4. **Testing**: Test with real Twitter API queries
5. **Refinement**: Tune scoring weights based on real results

---

## Technical Notes

**Dependencies:**
- `TwitterDiscoveryService` (already exists)
- Jen Context Engine concepts (relevance, persona, risk)
- PostgreSQL `discovered_videos` table

**Performance:**
- Twitter API: ~2-5 seconds for 10-25 posts
- Analysis: ~100ms per post
- Total: ~3-8 seconds for full discovery + analysis

**Rate Limits:**
- Twitter API: 180 requests/15 min
- Recommended: Cache queries for 5-10 minutes
- Add rate limiting if needed

---

## Files Created/Modified

**Created:**
- `backend/routers/smart_discovery.py` (new endpoint)

**Modified:**
- `backend/main.py` (added router)

**To Create:**
- Frontend component for X Hub
- Tests for scoring algorithm
- Documentation for users

---

**Status:** Backend complete, ready for frontend integration! 🚀
