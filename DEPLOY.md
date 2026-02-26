# Railway Deployment Guide

## Quick Deploy to Railway (15 minutes)

Railway is the easiest way to deploy this full-stack app. Here's the step-by-step:

### Prerequisites
- GitHub account
- Railway account (sign up at railway.app - free to start)
- This codebase pushed to a GitHub repo

### Step 1: Push to GitHub (If Not Already There)

```bash
cd /home/ubuntu/.openclaw/workspace/social-agent-hackathon

# Initialize git if needed
git init
git add .
git commit -m "Initial commit - Social Agent Pro"

# Create a new repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/social-agent-pro.git
git push -u origin main
```

### Step 2: Deploy Backend + Database

1. **Go to Railway:** https://railway.app
2. **Click "New Project"**
3. **Select "Deploy from GitHub repo"**
4. **Choose your `social-agent-pro` repo**
5. **Railway will auto-detect it's a Python app**

6. **Add PostgreSQL:**
   - Click "+ New" in your project
   - Select "Database → PostgreSQL"
   - Railway will automatically provision it

7. **Configure Environment Variables:**
   Click on the backend service → Variables tab:

   ```bash
   # Database (auto-filled by Railway when you add PostgreSQL)
   DATABASE_URL=${DATABASE_URL}
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_ANON_KEY=your-anon-key
   SUPABASE_SERVICE_ROLE_KEY=your-service-key

   # Auth
   JWT_SECRET=generate-a-random-secret-here
   ENCRYPTION_KEY=generate-32-char-key-here

   # LLM Provider (add at least one)
   ANTHROPIC_API_KEY=your-key
   # OR
   GEMINI_API_KEY=your-key
   # OR
   OPENAI_API_KEY=your-key

   # Twitter (when ready)
   TWITTER_CLIENT_ID=your-client-id
   TWITTER_CLIENT_SECRET=your-client-secret

   # Python path
   PYTHONPATH=/app

   # CORS (add your frontend URL after deploying frontend)
   CORS_ORIGINS=https://your-frontend.vercel.app,http://localhost:3000
   ```

8. **Set Start Command:**
   Settings → Build & Deploy → Start Command:
   ```bash
   uvicorn backend.main:app --host 0.0.0.0 --port ${PORT}
   ```

9. **Deploy!**
   - Railway will build and deploy automatically
   - Get your backend URL: `https://your-backend.railway.app`

### Step 3: Deploy Frontend to Vercel

1. **Go to Vercel:** https://vercel.com
2. **Click "New Project"**
3. **Import your GitHub repo**
4. **Configure:**
   - Framework Preset: Vite
   - Root Directory: `./` (leave as is)
   - Build Command: `npm run build`
   - Output Directory: `dist`

5. **Add Environment Variable:**
   ```bash
   VITE_API_URL=https://your-backend.railway.app
   ```

6. **Deploy!**
   - Vercel will build and deploy
   - Get your frontend URL: `https://your-app.vercel.app`

### Step 4: Update CORS

1. Go back to Railway → Backend service → Variables
2. Update `CORS_ORIGINS` to include your Vercel URL:
   ```bash
   CORS_ORIGINS=https://your-app.vercel.app,http://localhost:3000
   ```
3. Railway will auto-redeploy

### Step 5: Run Database Migrations (If Needed)

If using Supabase or need to set up tables:

1. Railway → Backend service → Terminal
2. Run migration scripts:
   ```bash
   python backend/scripts/init_db.py
   ```

### Step 6: Test!

1. Visit `https://your-app.vercel.app`
2. You should see the dashboard
3. Test login/features

## Alternative: Deploy Everything to Railway

If you prefer to keep everything in one place:

1. **Create monorepo structure** (Railway can handle it)
2. **Add Nixpacks config** or Railway will auto-detect
3. **Deploy frontend as static site on Railway**

## Cost Estimate

### Railway (Backend + Database)
- **Hobby Plan:** $5/month (includes $5 credit)
- **Database:** Included in hobby plan
- **Bandwidth:** 100GB included

### Vercel (Frontend)
- **Hobby Plan:** Free (100GB bandwidth)
- **Pro Plan:** $20/month (more bandwidth, faster builds)

**Total for hobby/dev:** ~$5/month
**Total for production:** ~$25/month

## Troubleshooting

### Backend won't start
- Check logs in Railway → Backend service → Deployments → Logs
- Verify all required env variables are set
- Check `PYTHONPATH` is set to `/app`

### Frontend can't reach backend
- Verify `VITE_API_URL` is correct
- Check CORS_ORIGINS includes your Vercel URL
- Test backend health: `curl https://your-backend.railway.app/api/v1/health`

### Database connection errors
- Make sure PostgreSQL service is running
- Verify `DATABASE_URL` is set
- Check Supabase credentials if using Supabase

### Rate limiting / performance issues
- Upgrade Railway plan for more resources
- Add caching layer (Redis)
- Optimize database queries

## Generating Secrets

```bash
# Generate JWT_SECRET
openssl rand -hex 32

# Generate ENCRYPTION_KEY (32 chars)
openssl rand -base64 32 | head -c 32
```

## Post-Deployment Checklist

- [ ] Backend health check passes
- [ ] Frontend loads correctly
- [ ] Login works
- [ ] Twitter connection works (if credentials added)
- [ ] RAG system retrieves context
- [ ] Comments generate properly
- [ ] Review workflow functions
- [ ] No CORS errors in browser console

---

**Need help?** Drop questions in the repo issues or check Railway/Vercel docs.
