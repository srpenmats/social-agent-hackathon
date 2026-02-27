# 🔍 DATABASE DIAGNOSTIC - Why Data Doesn't Show

## The Problem (ROOT CAUSE)

### Database Type: **SQLite** (Ephemeral)
**Location:** `backend/db/local.db`

**The Issue:**
Railway uses **ephemeral filesystem** - the SQLite database file gets **WIPED on every deploy/restart**.

```
Deploy/Restart → local.db deleted → All data lost → Shows empty
```

This is why:
1. ✅ Populate says "success" (writes to local.db)
2. ⏱️ Minutes/hours later: Railway restarts
3. ❌ local.db deleted
4. ❌ Frontend shows empty

---

## Proof

### Check Local Database (This Machine):
```bash
cd /home/ubuntu/.openclaw/workspace/social-agent-hackathon/backend
ls -lh db/local.db
# 116KB - HAS DATA
```

### Railway Database:
```bash
curl .../hubs/x/stats
# Returns zeros - EMPTY
```

**They're different databases!**

---

## Why SQLite is Wrong for Railway

| Issue | Impact |
|-------|--------|
| Ephemeral filesystem | Data lost on restart |
| No persistence | Every deploy = fresh DB |
| Not multi-container | Can't scale |
| File-based | Not accessible across instances |

**Railway needs:** PostgreSQL, MySQL, or hosted Supabase

---

## Solutions (Pick One)

### Option A: Use Railway PostgreSQL (Best - 10 min)

**What:** Add Railway PostgreSQL database, migrate code

**Steps:**
1. Railway Dashboard → Add PostgreSQL plugin
2. Update connection.py to use PostgreSQL
3. Run migrations
4. Persistent data ✅

**Time:** 10 minutes
**Cost:** Free tier available

---

### Option B: Use Supabase (Easiest - 5 min)

**What:** Point to hosted Supabase instance

**Steps:**
1. Get Supabase credentials (you may already have)
2. Set Railway env vars:
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
3. Code already supports it!

**Time:** 5 minutes  
**Cost:** Free tier

---

### Option C: External PostgreSQL (Flexible)

**What:** Use any PostgreSQL host (ElephantSQL, Neon, etc.)

**Steps:**
1. Create PostgreSQL database
2. Update connection string
3. Run migrations

---

### Option D: Keep SQLite + Mount Volume (Hacky)

**What:** Mount persistent volume in Railway

**Not recommended:** Railway doesn't officially support this well

---

## Quick Test to Prove It

Run this twice with 1 minute between:

```bash
# First run
curl -X POST .../populate/now
curl .../hubs/x/stats
# Shows data? ✅

# Wait 1 minute, Railway may restart

# Second run  
curl .../hubs/x/stats
# Shows empty? ❌ (if Railway restarted)
```

---

## What I Recommend

### Use Supabase (Immediate Fix)

**Do you have Supabase credentials?** If so:

1. Set these in Railway:
```bash
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJhbGc...
```

2. The code will automatically switch from SQLite to Supabase

3. Data persists ✅

---

## Check Current Setup

Let me verify what you have:

### Railway Environment Variables:
```bash
# Check these exist:
SUPABASE_URL
SUPABASE_KEY
DATABASE_URL
POSTGRES_URL
```

**If ANY of these exist,** we should use them instead of SQLite!

---

## The Fix (Step by Step)

### 1. Add Railway PostgreSQL (Recommended)

**In Railway Dashboard:**
1. Go to your project
2. Click "+ New" → Database → PostgreSQL
3. Copy the `DATABASE_URL` from variables
4. Restart service

### 2. Update Connection Code

I'll update `connection.py` to:
```python
# Check for DATABASE_URL first
if os.getenv("DATABASE_URL"):
    # Use PostgreSQL
else:
    # Fall back to SQLite (dev only)
```

### 3. Run Migrations

Create tables in PostgreSQL:
```bash
# Railway will auto-create tables on first run
```

### 4. Populate Data

```bash
curl -X POST .../populate/now
curl -X POST .../populate/engagements
```

**Data persists ✅**

---

## Immediate Action

**Tell me:**
1. Do you have Supabase credentials?
2. Should I add Railway PostgreSQL setup?
3. Do you want to check Railway dashboard for existing database?

**I can fix this in 5-10 minutes once we choose the database!**

---

## Summary

**Problem:** SQLite on ephemeral filesystem  
**Solution:** PostgreSQL or Supabase  
**Time:** 5-10 minutes  
**Result:** Persistent data that survives restarts

Let me know which option you prefer and I'll implement it now! 🚀
