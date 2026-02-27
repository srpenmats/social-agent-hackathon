# Deploy Everything to Railway (Monorepo)

## Yes! You Can Host Frontend on Railway Too

Railway supports **both frontend and backend** in the same project. This simplifies deployment to a single platform.

## Benefits of All-Railway Setup

✅ **Single platform** - Everything in one place
✅ **One bill** - Railway only ($5/month total)
✅ **Easier management** - One dashboard
✅ **Simpler configuration** - No cross-platform env vars
✅ **Internal networking** - Frontend → Backend on private network (faster)

## How Railway Handles Frontend

Railway can serve your Vite frontend in two ways:

### Option 1: Static Site (Recommended)
Build the frontend and serve static files via Nginx or similar.

### Option 2: Vite Dev Server
Run `npm run dev` on Railway (not recommended for production).

---

## Deployment Steps: All on Railway

### Step 1: Create Railway Project

1. Go to: https://railway.app/new
2. Click **"Deploy from GitHub repo"**
3. Select: `vitoryago/social-agent-hackathon`

### Step 2: Railway Will Auto-Detect

Railway is smart and will detect:
- **Backend:** Python (FastAPI) - auto-detected from `requirements.txt`
- **Frontend:** Node.js (Vite) - auto-detected from `package.json`

It will create **two services** automatically:
1. `backend` service (Python)
2. `root` service (Node.js - the frontend)

### Step 3: Configure Backend Service

**Add PostgreSQL Database:**
1. Click **"+ New"** in your project
2. Select **"Database" → "PostgreSQL"**
3. Railway auto-connects it via `DATABASE_URL`

**Set Environment Variables:**
Go to backend service → Variables tab:

```bash
# Database (auto-filled by Railway)
DATABASE_URL=${DATABASE_URL}

# Supabase (or use Railway's PostgreSQL)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-key

# Auth
JWT_SECRET=your-random-secret-32-chars
ENCRYPTION_KEY=your-random-key-32-chars

# Twitter API
TWITTER_API_KEY=VSGzfKGVdY5DoTKlg2ihDR0D7
TWITTER_API_SECRET=H2BNlYINJKAHS7do4ZJo2Yd7VQpWDNWwmOtRo3PA4OQEJ2HMET
TWITTER_BEARER_TOKEN=AAAAAAAAAAAAAAAAAAAAAHnq7gEAAAAAQP%2B3ENHCj3Oxrt5Qq8OiXgQXyzw%3DSWCH80a84HXwRCsU1igJijJK3d4KiWh43r8GiziQ4YslxiGoGx
TWITTER_ACCESS_TOKEN=2024576960668860416-2f2HgAqVk781Bk47o5fO3ZtYDXbwCX
TWITTER_ACCESS_TOKEN_SECRET=aaExetMRH1Dc7HINSyPcCPaBe9C0PosWsXXIk0RAchxce

# LLM Provider (at least one)
ANTHROPIC_API_KEY=your-key
# OR
GEMINI_API_KEY=your-key

# Python Path
PYTHONPATH=/app

# CORS (will add frontend URL after deployment)
CORS_ORIGINS=http://localhost:3000
```

**Set Start Command:**
Settings → Deploy → Start Command:
```bash
cd /app && python -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

### Step 4: Configure Frontend Service

Go to the `root` service (Node.js) → Variables tab:

**Add Environment Variable:**
```bash
# Point to backend service (use Railway's internal URL)
VITE_API_URL=https://your-backend.up.railway.app
```

**Set Build & Start Commands:**

**Build Command:**
```bash
npm install && npm run build
```

**Start Command:**
```bash
npx serve -s dist -l $PORT
```

This builds the frontend and serves it as static files using `serve`.

### Step 5: Install `serve` Package

Add to `package.json` in the root:

```json
{
  "dependencies": {
    "serve": "^14.2.0",
    ...existing dependencies
  }
}
```

Or Railway will auto-install it if you use the start command above.

### Step 6: Deploy!

Railway will:
1. Build backend (Python)
2. Build frontend (npm install + npm run build)
3. Start both services

You'll get two URLs:
- **Frontend:** `https://social-agent-hackathon-frontend.up.railway.app`
- **Backend:** `https://social-agent-hackathon-backend.up.railway.app`

### Step 7: Update CORS

Go back to backend service → Variables:

Update `CORS_ORIGINS` to include the frontend URL:
```bash
CORS_ORIGINS=https://social-agent-hackathon-frontend.up.railway.app,http://localhost:3000
```

Railway will auto-redeploy the backend.

---

## Simpler Alternative: Monorepo Setup

Railway also supports monorepo configuration with a single `railway.json`:

Create `railway.json` in the root:

```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "numReplicas": 1,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

And create two separate Railway services pointing to different directories:
- Service 1: Root directory → Frontend
- Service 2: `backend/` directory → Backend

---

## Cost Comparison

### Vercel + Railway:
- Frontend (Vercel): Free
- Backend + DB (Railway): $5/mo
- **Total: $5/mo**

### All Railway:
- Frontend (Railway): $5/mo (or included in plan)
- Backend (Railway): $5/mo
- Database (Railway): Included
- **Total: $5/mo** (same price, but simpler)

**Note:** Railway's pricing is $5/month for the Hobby plan with $5 usage credit. As long as you stay under the free tier limits, it's effectively the same cost.

---

## Recommendation

### For Simplicity: ✅ **All Railway**
**Pros:**
- One platform
- Easier to manage
- Same cost ($5/mo)
- No cross-platform configuration

**Cons:**
- Slightly slower global CDN than Vercel
- Less optimized for static sites

### For Performance: ⚡ **Vercel + Railway**
**Pros:**
- Vercel has best-in-class CDN for frontends
- Faster global load times
- Free frontend hosting

**Cons:**
- Two platforms to manage
- More complex environment variable setup

---

## My Recommendation: Start with All Railway

Since you're already setting up Railway, **deploy everything there first**. It's simpler, and you can always move the frontend to Vercel later if you need the CDN performance boost.

---

## Quick Start: All Railway

1. **Create Railway project** from GitHub repo
2. **Add PostgreSQL** database
3. **Configure backend** environment variables
4. **Configure frontend** to point to backend
5. **Set start commands** for both services
6. **Deploy!**

**Time: ~20 minutes**
**Cost: $5/month**

---

**Want me to help you set this up on Railway instead of Vercel?**
