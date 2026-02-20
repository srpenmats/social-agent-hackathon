---
name: "moneylion-tools"
description: "API endpoints, browser automation capabilities, and platform selectors for the MoneyLion social engagement agent."
---

# Tools & API Reference

## Backend API

**Base URL:** Configured via the `NEOCLAW_API_BASE` environment variable.

**Authentication:** Include on every request:
```
Authorization: Bearer <NEOCLAW_API_KEY>
Content-Type: application/json
```

### Data Ingestion (You -> Backend)

**Report discovered content:**
```
POST /api/v1/neoclaw/ingest/videos

Request:
{
  "platform": "tiktok" | "instagram" | "x",
  "video_url": "https://www.tiktok.com/@creator/video/123",
  "creator": "@creator_handle",
  "description": "Video caption or tweet text",
  "hashtags": ["budgeting", "moneytips"],
  "likes": 15000,
  "comments_count": 342,
  "shares": 890
}

Response:
{
  "video_id": "uuid",
  "classification": "cultural-trending",
  "status": "queued"
}
```

The backend generates comment candidates, scores risk, and routes for approval automatically. You do not need to generate comments.

### Task Management (Backend -> You)

**Get your next task:**
```
GET /api/v1/neoclaw/tasks/next?platform=tiktok&types=post,discover

Response:
{
  "task_id": "uuid",
  "type": "post" | "discover" | "track",
  "platform": "tiktok",
  "payload": {
    "video_url": "https://...",
    "comment_text": "The approved comment to post",
    "video_id": "uuid"
  },
  "priority": 1
}

Response (no tasks available):
{ "task_id": null }
```

**Report task completion:**
```
POST /api/v1/neoclaw/tasks/{task_id}/complete

Request:
{
  "status": "success" | "fail",
  "screenshot_url": "https://...",
  "posted_at": "2026-02-19T14:30:00Z",
  "error": null
}

Request (failure):
{
  "status": "fail",
  "error": "comment_blocked",
  "error_detail": "Platform returned comment restriction error"
}
```

### Status & Config

**Send heartbeat (every 60 seconds):**
```
POST /api/v1/neoclaw/heartbeat

Request:
{
  "status": "active" | "idle" | "error",
  "platform": "tiktok",
  "current_action": "discovering" | "posting" | "tracking" | "waiting"
}
```

**Get agent config (check before every post):**
```
GET /api/v1/neoclaw/config

Response:
{
  "kill_switch_active": false,
  "rate_limits": {
    "tiktok": { "max_per_hour": 12, "min_gap_seconds": 180 },
    "instagram": { "max_per_hour": 10, "min_gap_seconds": 180 },
    "x": { "max_per_hour": 15, "min_gap_seconds": 180 }
  },
  "posting_hours": { "start": "08:00", "end": "23:00", "timezone": "US/Eastern" },
  "discovery_thresholds": {
    "tiktok": { "min_likes": 500, "max_age_hours": 24 },
    "instagram": { "min_likes": 1000, "max_age_hours": 48 },
    "x": { "min_likes": 100, "max_age_hours": 12 }
  }
}
```

If `kill_switch_active` is `true`, STOP ALL POSTING immediately. Continue sending heartbeats but do not execute any post tasks.

**Report platform health issues:**
```
POST /api/v1/neoclaw/platform-health

Request:
{
  "platform": "tiktok",
  "status": "healthy" | "stale" | "expired" | "captcha" | "rate_limited",
  "detail": "Session cookies expired, login page detected"
}
```

## Browser Automation

You have access to OpenClaw browser automation. Available actions:

| Action | Description | Human-Like Parameters |
|---|---|---|
| `navigate(url)` | Open a URL in the browser | -- |
| `scroll(direction, amount)` | Scroll the page | Dwell 3-8 seconds per screenful |
| `click(selector_or_coords)` | Click an element | Add 50-200ms delay before clicking |
| `type(selector, text)` | Type text into an input | 50-150ms per character, random pauses |
| `screenshot()` | Capture the current viewport | Use after posting for proof |
| `read_text(selector)` | Extract text content from an element | -- |
| `wait_for(selector, timeout)` | Wait for an element to appear | Max 10 seconds, then report failure |
| `get_url()` | Get the current page URL | -- |

Always use human-like timing. Never type at constant speed. Add random pauses between actions (200-2000ms).

## Platform Selectors

These selectors are approximate starting points. **Always verify at runtime** — platforms change their DOM frequently. If a selector fails, inspect the page and adapt.

### TikTok

| Element | Approximate Selector | Notes |
|---|---|---|
| Like count | `[data-e2e="like-count"]` | Right side of video |
| Comment count | `[data-e2e="comment-count"]` | Below like button |
| Share count | `[data-e2e="share-count"]` | Below comment button |
| Creator name | `[data-e2e="browse-username"]` | Below video |
| Video description | `[data-e2e="browse-video-desc"]` | Below creator name |
| Comment input | `[data-e2e="comment-input"]` | Bottom of comment section |
| Post comment button | `[data-e2e="comment-post"]` | Next to comment input |

### Instagram

| Element | Approximate Selector | Notes |
|---|---|---|
| Like count | `section span` near heart icon | Structure varies by post type |
| Comment count | Link text containing "comments" | In post footer |
| Creator handle | Header username element | Top of post |
| Comment input | `textarea[placeholder]` | In comment section footer |
| Post comment button | Button adjacent to textarea | Activates after typing |

### X (Twitter)

| Element | Approximate Selector | Notes |
|---|---|---|
| Like count/button | `[data-testid="like"]` | Below tweet |
| Retweet count/button | `[data-testid="retweet"]` | Below tweet |
| Reply button | `[data-testid="reply"]` | Below tweet |
| Tweet text | `[data-testid="tweetText"]` | Main tweet body |
| Reply input | `[data-testid="tweetTextarea_0"]` | In reply compose area |
| Post reply button | `[data-testid="tweetButtonInline"]` | In reply compose area |

**Adaptation strategy:** If a selector returns no results, try these fallbacks:
1. Search by `aria-label` containing the element name.
2. Search by role attributes (`role="button"`, `role="textbox"`).
3. Take a screenshot and visually locate the element by coordinates.
4. Report the broken selector via platform-health so it can be updated.

## Rate Limits

### API Rate Limits
Respect rate limits returned by the `/config` endpoint. Defaults:
- Heartbeat: 1 request per 60 seconds
- Ingest: 60 requests per minute
- Task poll: 1 request per 10 seconds

### Platform Posting Limits
| Platform | Max Per Hour | Min Gap Between Posts | Daily Target |
|---|---|---|---|
| TikTok | 12 | 3 minutes | 15-25 |
| Instagram | 10 | 3 minutes | 10-15 |
| X | 15 | 3 minutes | 20-30 |

## Error Codes

| HTTP Code | Meaning | Action |
|---|---|---|
| 200 | Success | Proceed normally |
| 401 | API key invalid or expired | Stop. Check `NEOCLAW_API_KEY` configuration. |
| 403 | Kill switch active | Stop ALL posting immediately. Continue heartbeats only. |
| 404 | Task or resource not found | Skip this task, poll for next. |
| 409 | Task already claimed by another agent | Skip, poll for next task. |
| 422 | Validation error in request body | Log the error, fix the payload, retry once. |
| 429 | API rate limited | Back off exponentially: 1min, 2min, 4min, 8min max. |
| 503 | Backend unavailable | Retry with exponential backoff. Continue discovery offline. |
