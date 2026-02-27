# Quick Vercel Deployment Guide

## ✅ Step-by-Step: Deploy Frontend to Vercel

### 1. Go to Vercel
Visit: https://vercel.com/dashboard

### 2. Import Project
1. Click **"Add New..."** → **"Project"**
2. Select **"Import Git Repository"**
3. Choose: `vitoryago/social-agent-hackathon`
4. Click **"Import"**

### 3. Configure Build Settings

Vercel should auto-detect Vite. Verify these settings:

- **Framework Preset:** Vite
- **Root Directory:** `./` (leave as root)
- **Build Command:** `npm run build`
- **Output Directory:** `dist`
- **Install Command:** `npm install`

### 4. Add Environment Variable

Click **"Environment Variables"** and add:

**Key:** `VITE_API_URL`

**Value:** (Choose one option below)

**Option A: Use the temporary tunnel backend**
```
https://advert-trips-granted-zones.trycloudflare.com
```

**Option B: Deploy backend to Railway first** (recommended)
```
https://your-backend.railway.app
```
(See Step 5 below for Railway deployment)

### 5. Deploy!
Click **"Deploy"**

Vercel will build and deploy your frontend in ~2 minutes.

You'll get a URL like: `https://social-agent-hackathon-xyz.vercel.app`

---

## 🚂 Deploy Backend to Railway (Optional but Recommended)

If you want a permanent backend (instead of the temporary tunnel):

### 1. Go to Railway
Visit: https://railway.app/new

### 2. Create New Project
1. Click **"Deploy from GitHub repo"**
2. Select: `vitoryago/social-agent-hackathon`
3. Railway will auto-detect Python

### 3. Add PostgreSQL Database
1. In your project, click **"+ New"**
2. Select **"Database"** → **"PostgreSQL"**
3. Railway will provision it and auto-connect

### 4. Configure Environment Variables

Go to your backend service → **Variables** tab.

Add these (copy from `backend/.env.example`):

```bash
# Database (auto-filled by Railway)
DATABASE_URL=${DATABASE_URL}

# Or use Supabase
SUPABASE_URL=your-supabase-url
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-key

# Auth (generate new ones for production!)
JWT_SECRET=your-random-secret-32-chars
ENCRYPTION_KEY=your-random-key-32-chars

# Twitter API
TWITTER_API_KEY=VSGzfKGVdY5DoTKlg2ihDR0D7
TWITTER_API_SECRET=H2BNlYINJKAHS7do4ZJo2Yd7VQpWDNWwmOtRo3PA4OQEJ2HMET
TWITTER_BEARER_TOKEN=AAAAAAAAAAAAAAAAAAAAAHnq7gEAAAAAQP%2B3ENHCj3Oxrt5Qq8OiXgQXyzw%3DSWCH80a84HXwRCsU1igJijJK3d4KiWh43r8GiziQ4YslxiGoGx
TWITTER_ACCESS_TOKEN=2024576960668860416-2f2HgAqVk781Bk47o5fO3ZtYDXbwCX
TWITTER_ACCESS_TOKEN_SECRET=aaExetMRH1Dc7HINSyPcCPaBe9C0PosWsXXIk0RAchxce

# LLM Provider (add at least one)
ANTHROPIC_API_KEY=your-key-here
# OR
GEMINI_API_KEY=your-key-here

# Python Path
PYTHONPATH=/app

# CORS (add your Vercel URL after deploying frontend)
CORS_ORIGINS=https://your-app.vercel.app,http://localhost:3000
```

### 5. Set Start Command

Go to **Settings** → **Deploy** → **Start Command**:

```bash
cd /app && python -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

### 6. Deploy!

Railway will build and deploy automatically.

You'll get a URL like: `https://social-agent-hackathon-production.up.railway.app`

### 7. Update Vercel Frontend

Go back to Vercel → Your project → **Settings** → **Environment Variables**

Update `VITE_API_URL` to your Railway backend URL.

Redeploy frontend (Vercel → Deployments → click ⋯ → "Redeploy")

### 8. Update Railway CORS

Go to Railway → Backend service → **Variables**

Update `CORS_ORIGINS` to include your Vercel URL:
```
CORS_ORIGINS=https://your-app.vercel.app,http://localhost:3000
```

Railway will auto-redeploy.

---

## ✅ Done!

Your app is now live with permanent URLs!

- **Frontend:** `https://your-app.vercel.app`
- **Backend:** `https://your-backend.railway.app`

---

## 🔐 Generate Secrets

For production JWT_SECRET and ENCRYPTION_KEY:

```bash
# JWT_SECRET
openssl rand -hex 32

# ENCRYPTION_KEY (exactly 32 chars)
openssl rand -base64 32 | head -c 32
```

---

## 💰 Cost

- **Vercel:** Free (hobby plan)
- **Railway:** $5/month (includes PostgreSQL)
- **Total:** $5/month

---

## 🐛 Troubleshooting

### Frontend can't connect to backend
- Check `VITE_API_URL` in Vercel env vars
- Verify backend CORS includes Vercel URL
- Test backend health: `https://your-backend.railway.app/api/v1/health`

### Backend won't start on Railway
- Check deployment logs (Railway → Deployments → Logs)
- Verify all required env variables are set
- Check `PYTHONPATH` is `/app`

### Database connection errors
- Make sure PostgreSQL addon is added in Railway
- Or verify Supabase credentials if using Supabase
- Check `DATABASE_URL` or `SUPABASE_URL` is set

---

**Questions?** Check the logs or drop a message!
