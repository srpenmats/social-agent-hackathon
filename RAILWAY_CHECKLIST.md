# Railway Backend - Environment Variables Checklist

Copy this list and verify each one is set in Railway:

## Required Variables (11 total):

1. DATABASE_URL = ${{Postgres.DATABASE_URL}}
2. JWT_SECRET = social-agent-jwt-d4e8f9a2b5c7e1f3a6d8c9b4e7f2a5c8d1e4f7a9b2c5e8f1a4d7
3. ENCRYPTION_KEY = social-agent-enc-Kx9mP2nQ5tR8vY
4. TWITTER_API_KEY = VSGzfKGVdY5DoTKlg2ihDR0D7
5. TWITTER_API_SECRET = H2BNlYINJKAHS7do4ZJo2Yd7VQpWDNWwmOtRo3PA4OQEJ2HMET
6. TWITTER_BEARER_TOKEN = AAAAAAAAAAAAAAAAAAAAAHnq7gEAAAAAQP%2B3ENHCj3Oxrt5Qq8OiXgQXyzw%3DSWCH80a84HXwRCsU1igJijJK3d4KiWh43r8GiziQ4YslxiGoGx
7. TWITTER_ACCESS_TOKEN = 2024576960668860416-2f2HgAqVk781Bk47o5fO3ZtYDXbwCX
8. TWITTER_ACCESS_TOKEN_SECRET = aaExetMRH1Dc7HINSyPcCPaBe9C0PosWsXXIk0RAchxce
9. PYTHONPATH = /app
10. CORS_ORIGINS = https://social-agent-hackathon.vercel.app,http://localhost:3000
11. NEOCLAW_API_KEY = neoclaw-api-key-d4e8f9a2b5c7e1f3a6d8c9b4e7f2a5c8d1e4f7a9b2c5e8

## Also Check:

### Start Command (Settings → Deploy → Custom Start Command):
```
cd /app && python -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

### PostgreSQL Service:
- Is there a "Postgres" service in your Railway project?
- Is it running (green checkmark)?

---

## Common Issues:

### Missing SUPABASE variables cause errors?
The code falls back to SQLite if Supabase is not configured, but it needs placeholder values.

Add these if missing:
- SUPABASE_URL = https://placeholder.supabase.co
- SUPABASE_ANON_KEY = placeholder

### PYTHONPATH not set?
Without this, Python can't find the backend module.

Must be: /app

### Wrong start command?
Must include: cd /app && python -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT
