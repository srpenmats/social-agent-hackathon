# TWCLAW RAILWAY DEPLOYMENT

## What Was Built

**twclaw v1.0.0** - Twitter X API CLI tool for OpenClaw
- Location: `/home/ubuntu/twclaw/`
- Installed: `/usr/bin/twclaw` (globally)

## Railway Deployment Steps

### Option 1: Add to Dockerfile (Recommended)

Add to your Railway Dockerfile:

```dockerfile
# Install Node.js if not already present
RUN apt-get update && apt-get install -y nodejs npm

# Copy twclaw
COPY twclaw /app/twclaw
WORKDIR /app/twclaw
RUN npm install
RUN npm link

# Return to app directory
WORKDIR /app
```

### Option 2: Add to nixpacks.toml

```toml
[phases.setup]
nixPkgs = ["nodejs", "npm"]

[phases.install]
cmds = [
    "cd /tmp && git clone https://github.com/yourusername/twclaw.git",
    "cd /tmp/twclaw && npm install && npm link"
]
```

### Option 3: Post-install Script

Add to `package.json`:

```json
{
  "scripts": {
    "postinstall": "cd twclaw && npm install && npm link"
  }
}
```

## Required Environment Variables

Railway must have:
```
TWITTER_BEARER_TOKEN=<your-write-enabled-token>
```

## Testing After Deploy

```bash
# 1. Verify twclaw is available
railway run twclaw --help

# 2. Test authentication
railway run twclaw auth-check

# 3. Test search
railway run twclaw search "test" -n 3 --json

# 4. Test posting (careful!)
railway run twclaw tweet "Test from Railway"
```

## API Endpoints Now Available

```
POST /api/v1/jen/post-comment
  Body: {"tweet_id": "123", "comment_text": "Great post!"}
  Returns: {"success": true, "comment_url": "https://..."}

GET /api/v1/jen/verify-auth
  Returns: {"authenticated": true, "info": {...}}

GET /api/v1/jen/tweet-details/{tweet_id}
  Returns: Full tweet with ALL metrics
```

## What Changed in Backend

**backend/services/twitter_discovery.py**
- Now uses twclaw CLI instead of httpx
- Added: post_reply(), post_tweet(), get_tweet_details()
- Full metrics: quotes, bookmarks, impressions

**backend/routers/jen.py** (NEW)
- Comment posting endpoint
- Auth verification
- Tweet details retrieval

**backend/main.py**
- Registered jen router

## Next Steps

1. Push twclaw to GitHub repo
2. Add installation method to Railway
3. Deploy
4. Test endpoints
5. Update Smart Discovery frontend to show all metrics
6. Add "Post Comment" button to UI
