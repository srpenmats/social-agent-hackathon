# Twitter/X Frontend Hardening Design

**Date:** 2026-02-27
**Status:** Approved
**Scope:** Fix all production-breaking issues for Twitter/X features

## Problem Statement

The frontend deployed on Vercel cannot load Twitter data or interact with the backend on Railway. Multiple screens are broken due to hardcoded localhost URLs, incorrect environment variable patterns, and bypassed centralized API clients. The Dashboard is also affected due to failed API connections.

## Root Causes

1. **XHub.tsx:6** — hardcoded `http://localhost:8000/api/v1` used by 4 direct fetch calls (response queue, auto-refresh, review decisions)
2. **SmartDiscoveryWidget.tsx:36** — uses `process.env.NEXT_PUBLIC_API_BASE` (Node.js/Next.js pattern) instead of Vite's `import.meta.env`; works only because Railway URL is hardcoded as last fallback
3. **ReviewPostsWidget.tsx:26** — same `process.env` issue as SmartDiscoveryWidget
4. **CORS config** — defaults to `localhost:3000,localhost:5173`; Vercel domain not included unless `CORS_ORIGINS` env var is set on Railway
5. **Silent error handling** — `.catch(() => {})` blocks cause blank screens with no feedback

## Design

### Section 1: API URL Standardization

Export `BASE_URL` from `services/api.ts` so all files use one source of truth.

**Files to update:**
- `services/api.ts` — export `BASE_URL` constant
- `XHub.tsx` — replace hardcoded localhost with imported `BASE_URL`
- `SmartDiscoveryWidget.tsx` — replace `process.env` with imported `BASE_URL`
- `ReviewPostsWidget.tsx` — replace `process.env` with imported `BASE_URL`
- `AILearning.tsx` — replace local env var copy with imported `BASE_URL`

**Out of scope:** InstagramHub.tsx (not fixing Instagram for now)

### Section 2: Centralize API Calls

Add missing endpoints to `services/api.ts`:
- `JenAPI.getResponseQueue(limit)`
- `JenAPI.addReviewPosts(posts)`
- `JenAPI.getReviewPosts(status)`
- `JenAPI.approveDraft(postId)`
- `JenAPI.generateDraft(postId, persona)`
- `JenAPI.deletePost(postId)`
- `AgentAPI.autoRefresh()`
- `HubAPI.smartDiscovery(query, settings)`

Refactor these files to use centralized API client:
- `XHub.tsx` — replace raw fetch calls with API client methods
- `SmartDiscoveryWidget.tsx` — replace raw fetch with `HubAPI.smartDiscovery()` and `JenAPI.addReviewPosts()`
- `ReviewPostsWidget.tsx` — replace raw fetch with `JenAPI.*` methods

### Section 3: CORS Configuration

- Add Vercel production domain to default CORS origins in `backend/config.py`
- Document that `CORS_ORIGINS` env var on Railway should include the Vercel URL

### Section 4: Error Boundaries & Loading States

- Create a lightweight `ErrorBoundary` React component
- Create reusable `LoadingState` and `ErrorState` UI components
- Add error/loading states to: XHub, Overview, SmartDiscoveryWidget, ReviewPostsWidget
- Replace silent `.catch(() => {})` blocks with proper error state updates
- Add retry capability where appropriate

### Section 5: Deploy Uncommitted Features

- Commit all fixes plus new features (AILearning.tsx, feedback.py, feedback_loop.py)
- Commit modified files (App.tsx, Sidebar.tsx, backend changes)
- Trigger redeployment to Vercel and Railway

## Out of Scope

- InstagramHub.tsx fixes
- TikTokHub fixes
- Backend API endpoint bugs (if any)
- Twitter API credential rotation
- Database migration to Supabase
