# Vercel Import - Step-by-Step with Screenshots Guide

## Step 1: Log into Vercel

Go to: **https://vercel.com/login**

Log in with your account (GitHub, GitLab, or Bitbucket)

---

## Step 2: Go to Dashboard

After logging in, you'll be at: **https://vercel.com/dashboard**

---

## Step 3: Start New Project

Click the **"Add New..."** button (top right)

Then select **"Project"** from the dropdown

---

## Step 4: Import Git Repository

You'll see a screen titled **"Import Git Repository"**

### Option A: If You See the Repo Listed
- Look for `vitoryago/social-agent-hackathon` in the list
- Click **"Import"** next to it

### Option B: If You Don't See the Repo
1. Click **"Adjust GitHub App Permissions"** or **"Add GitHub Account"**
2. Authorize Vercel to access your GitHub account
3. Select the repositories you want to give Vercel access to
4. Include: `vitoryago/social-agent-hackathon`
5. Save permissions
6. Return to Vercel - the repo should now appear
7. Click **"Import"**

---

## Step 5: Configure Project

You'll see the **"Configure Project"** screen.

### Framework Preset
Should auto-detect: **Vite** ✅

If not, select it from the dropdown.

### Root Directory
Leave as: **`./`** (the root)

### Build Settings (Should be pre-filled)
- **Build Command:** `npm run build`
- **Output Directory:** `dist`
- **Install Command:** `npm install`

✅ These should be correct by default for Vite.

---

## Step 6: Environment Variables

**IMPORTANT:** Add this environment variable:

1. Expand **"Environment Variables"** section
2. Click **"Add"**
3. Enter:
   - **Key:** `VITE_API_URL`
   - **Value:** Choose one:

**Option A: Use temporary tunnel (quick test)**
```
https://advert-trips-granted-zones.trycloudflare.com
```

**Option B: Deploy backend to Railway first (recommended for production)**
```
https://your-backend.railway.app
```
(Replace with your actual Railway URL after deploying backend)

**Option C: Use localhost (only for local development)**
```
http://localhost:8000
```

4. Click **"Add"**

---

## Step 7: Deploy!

Click the big **"Deploy"** button at the bottom.

Vercel will now:
1. Clone the repository
2. Install dependencies (`npm install`)
3. Build the project (`npm run build`)
4. Deploy to their CDN

This takes about **1-3 minutes**.

---

## Step 8: Wait for Deployment

You'll see a build log showing progress:
```
Cloning repository...
Installing dependencies...
Building...
Deploying...
```

When complete, you'll see:
```
🎉 Deployed to production

Visit: https://social-agent-hackathon-xyz.vercel.app
```

---

## Step 9: Visit Your Site!

Click the **"Visit"** button or the deployment URL.

Your Social Agent Pro UI should load! 🎉

---

## Troubleshooting

### "Repository not found"
**Solution:** Go to GitHub → Settings → Applications → Vercel → Grant access to the repo

### "Build failed"
**Solution:** Check the build logs. Common issues:
- Missing dependencies (usually auto-fixed on retry)
- TypeScript errors (check the logs)
- Environment variable issues

### "Site loads but can't connect to backend"
**Solution:** 
- Check `VITE_API_URL` is set correctly
- Verify backend is running
- Check browser console for CORS errors

### "404 on routes"
**Solution:** Vercel needs a rewrite rule. Add `vercel.json`:
```json
{
  "rewrites": [
    { "source": "/(.*)", "destination": "/" }
  ]
}
```

---

## After Deployment

### Get Your URL
Format: `https://social-agent-hackathon-[random].vercel.app`

### Update Backend CORS
If using Railway backend, add your Vercel URL to CORS:
```
CORS_ORIGINS=https://your-app.vercel.app,http://localhost:3000
```

### Redeploy (if needed)
- Go to Deployments tab
- Click ⋯ menu on latest deployment
- Select "Redeploy"

### Add Custom Domain (Optional)
- Go to Settings → Domains
- Add your custom domain
- Follow DNS setup instructions

---

## Quick Access Links

- **Vercel Dashboard:** https://vercel.com/dashboard
- **Import New Project:** https://vercel.com/new
- **Your Deployments:** https://vercel.com/dashboard (shows all your projects)

---

**Need help?** Just tell me which step you're stuck on!
