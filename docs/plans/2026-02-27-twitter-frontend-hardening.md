# Twitter/X Frontend Hardening Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Fix all production-breaking API URL issues, centralize API calls, fix CORS, add error boundaries, and deploy — so the Twitter/X features work on Vercel + Railway.

**Architecture:** Export `BASE_URL` from the existing centralized `services/api.ts` and wire all screens/widgets to use it (or the `apiFetch` helper directly). Add missing Jen/Agent endpoints to the API client. Fix backend CORS. Add lightweight error/loading UI. Commit and deploy.

**Tech Stack:** React 19 + Vite, FastAPI (Python), Tailwind CSS, Vercel + Railway

---

## Task 1: Export BASE_URL and apiFetch from services/api.ts

**Files:**
- Modify: `services/api.ts:3,17`

**Step 1: Add exports to services/api.ts**

Change line 3 from:
```typescript
const BASE_URL = (typeof import.meta !== 'undefined' && import.meta.env?.VITE_API_URL) || 'http://localhost:8000/api/v1';
```
to:
```typescript
export const BASE_URL = (typeof import.meta !== 'undefined' && import.meta.env?.VITE_API_URL) || 'http://localhost:8000/api/v1';
```

Also export the `apiFetch` helper — change line 17 from:
```typescript
async function apiFetch<T>(endpoint: string, options?: RequestInit): Promise<T> {
```
to:
```typescript
export async function apiFetch<T>(endpoint: string, options?: RequestInit): Promise<T> {
```

**Step 2: Verify build still compiles**

Run: `cd /Users/vitor.carvalho/social-agent-hackathon && npx vite build 2>&1 | tail -5`
Expected: Build succeeds (existing consumers unaffected by adding `export`)

**Step 3: Commit**

```bash
git add services/api.ts
git commit -m "refactor: export BASE_URL and apiFetch from api.ts"
```

---

## Task 2: Add missing Jen, Agent, and Hub endpoints to services/api.ts

**Files:**
- Modify: `services/api.ts` (append after line 114, before CommentsAPI)

**Step 1: Add JenAPI and AgentAPI to services/api.ts**

Insert after the `HubAPI` block (after line 114):

```typescript
// --- Jen (Review Posts) ---

export const JenAPI = {
  getResponseQueue: (limit = 10) =>
    apiFetch<{ posts: any[] }>(`/jen/response-queue?limit=${limit}`),

  getReviewPosts: (status: string = 'pending') =>
    apiFetch<{ posts: any[] }>(`/jen/review-posts?status=${status}`),

  addReviewPost: (post: any) =>
    apiFetch<any>('/jen/review-posts', {
      method: 'POST',
      body: JSON.stringify(post),
    }),

  saveDraft: (postId: string, comment: string) =>
    apiFetch<any>(`/jen/review-posts/${postId}/draft`, {
      method: 'PUT',
      body: JSON.stringify({ comment }),
    }),

  approvePost: (postId: string, comment: string) =>
    apiFetch<any>(`/jen/review-posts/${postId}/approve`, {
      method: 'POST',
      body: JSON.stringify({ comment }),
    }),

  deletePost: (postId: string) =>
    apiFetch<any>(`/jen/review-posts/${postId}`, {
      method: 'DELETE',
    }),
};

// --- Agent ---

export const AgentAPI = {
  autoRefresh: () =>
    apiFetch<any>('/agent/auto-refresh', { method: 'POST' }),
};
```

Also add `smartDiscovery` to the existing `HubAPI` block — change lines 111-114 from:
```typescript
export const HubAPI = {
  getStats: (platform: string) =>
    apiFetch<any>(`/hubs/${platform}/stats`),
};
```
to:
```typescript
export const HubAPI = {
  getStats: (platform: string) =>
    apiFetch<any>(`/hubs/${platform}/stats`),

  smartDiscovery: (query: string, maxResults = 10) =>
    apiFetch<any>(`/hubs/x/smart-discovery`, {
      method: 'POST',
      body: JSON.stringify({ query, max_results: maxResults }),
    }),
};
```

**Step 2: Verify build**

Run: `cd /Users/vitor.carvalho/social-agent-hackathon && npx vite build 2>&1 | tail -5`
Expected: Build succeeds

**Step 3: Commit**

```bash
git add services/api.ts
git commit -m "feat: add JenAPI, AgentAPI, and HubAPI.smartDiscovery endpoints"
```

---

## Task 3: Fix XHub.tsx — replace hardcoded localhost with centralized API

**Files:**
- Modify: `screens/XHub.tsx`

**Step 1: Replace the entire XHub API layer**

Remove lines 1-26 (the hardcoded API_BASE and decideDraft function) and replace with:

```typescript
import React, { useState, useEffect, useCallback } from 'react';
import { HubAPI, JenAPI, AgentAPI, ReviewAPI, ApiError } from '../services/api';
import SmartDiscoveryWidget from '../components/SmartDiscoveryWidget';
import ReviewPostsWidget from '../components/ReviewPostsWidget';
```

Then update the `fetchData` function (lines 35-51) to use `JenAPI`:

```typescript
  const fetchData = useCallback(async () => {
    try {
      const result = await HubAPI.getStats('x');

      // Also fetch response queue
      const responseQueue = await JenAPI.getResponseQueue(10);

      // Merge response queue into data.drafts for display
      result.drafts = responseQueue.posts || [];

      setData(result);
      setError(null);
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : 'Failed to load X data.');
    }
  }, []);
```

Update `handleRefresh` (lines 57-70) to use `AgentAPI`:

```typescript
  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      await AgentAPI.autoRefresh();
    } catch (e) {
      console.warn('Refresh request failed, reloading cached data:', e);
    }
    await fetchData();
    setRefreshing(false);
  };
```

Update `handleApprove` and `handleReject` to use `ReviewAPI.decide()` instead of the removed `decideDraft`:

```typescript
  const handleApprove = async (item: any) => {
    try {
      await ReviewAPI.decide(String(item.id), 'approve');
      setData((prev: any) => ({
        ...prev,
        drafts: prev.drafts.filter((d: any) => d.id !== item.id),
      }));
    } catch (e) {
      console.error('Failed to approve draft:', e);
    }
  };

  const handleReject = async (item: any) => {
    try {
      await ReviewAPI.decide(String(item.id), 'reject');
      setData((prev: any) => ({
        ...prev,
        drafts: prev.drafts.filter((d: any) => d.id !== item.id),
      }));
    } catch (e) {
      console.error('Failed to reject draft:', e);
    }
  };
```

Update `handleSaveEdit` similarly:

```typescript
  const handleSaveEdit = async (item: any) => {
    try {
      await ReviewAPI.decide(String(item.id), 'approve', editText);
      setData((prev: any) => ({
        ...prev,
        drafts: prev.drafts.filter((d: any) => d.id !== item.id),
      }));
      setEditingId(null);
      setEditText('');
    } catch (e) {
      console.error('Failed to save edited draft:', e);
    }
  };
```

**Step 2: Verify build**

Run: `cd /Users/vitor.carvalho/social-agent-hackathon && npx vite build 2>&1 | tail -5`
Expected: Build succeeds

**Step 3: Commit**

```bash
git add screens/XHub.tsx
git commit -m "fix: replace hardcoded localhost with centralized API in XHub"
```

---

## Task 4: Fix SmartDiscoveryWidget.tsx — use centralized API

**Files:**
- Modify: `components/SmartDiscoveryWidget.tsx`

**Step 1: Replace the API layer**

Change line 36 from:
```typescript
const API_BASE = process.env.NEXT_PUBLIC_API_BASE || process.env.REACT_APP_API_BASE || 'https://social-agent-hackathon-production.up.railway.app/api/v1';
```
to:
```typescript
import { HubAPI, JenAPI } from '../services/api';
```

(Add this import at the top of the file, after the React import on line 1.)

Then remove the old `API_BASE` line entirely.

Update `handleDiscover` (lines 45-76) to use `HubAPI.smartDiscovery`:

```typescript
  const handleDiscover = async () => {
    if (!query.trim()) {
      setError('Please enter a description of what you\'re looking for');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const data: SmartDiscoveryResponse = await HubAPI.smartDiscovery(query.trim(), 10);
      setResults(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to discover posts');
      setResults(null);
    } finally {
      setLoading(false);
    }
  };
```

Update `handleAddToQueue` (lines 97-122) to use `JenAPI.addReviewPost`:

```typescript
  const handleAddToQueue = async (post: PostAnalysis) => {
    setAddingToQueue(post.post_id);
    try {
      await JenAPI.addReviewPost(post);

      // Trigger custom event to refresh Review Posts widget
      window.dispatchEvent(new CustomEvent('review-queue-updated'));

      // Show success message (brief)
      setTimeout(() => {
        setAddingToQueue(null);
      }, 1000);
    } catch (error) {
      console.error('Failed to add to queue:', error);
      setError('Failed to add to review queue. Please try again.');
      setAddingToQueue(null);
    }
  };
```

**Step 2: Verify build**

Run: `cd /Users/vitor.carvalho/social-agent-hackathon && npx vite build 2>&1 | tail -5`
Expected: Build succeeds

**Step 3: Commit**

```bash
git add components/SmartDiscoveryWidget.tsx
git commit -m "fix: replace process.env with centralized API in SmartDiscoveryWidget"
```

---

## Task 5: Fix ReviewPostsWidget.tsx — use centralized API

**Files:**
- Modify: `components/ReviewPostsWidget.tsx`

**Step 1: Replace the API layer**

Add import at the top (after line 1):
```typescript
import { JenAPI } from '../services/api';
```

Remove line 26 (the `API_BASE` declaration).

Update `loadReviewPosts` (lines 52-63):
```typescript
  const loadReviewPosts = async () => {
    setLoading(true);
    try {
      const data = await JenAPI.getReviewPosts(filter);
      setPosts(data.posts || []);
    } catch (error) {
      console.error('Failed to load review posts:', error);
    } finally {
      setLoading(false);
    }
  };
```

Update `handleSaveDraft` (lines 70-82):
```typescript
  const handleSaveDraft = async (postId: string) => {
    try {
      await JenAPI.saveDraft(postId, editComment);
      setEditingId(null);
      loadReviewPosts();
    } catch (error) {
      console.error('Failed to save draft:', error);
    }
  };
```

Update `handleApprove` (lines 84-97):
```typescript
  const handleApprove = async (postId: string, comment: string) => {
    if (!confirm('Approve this comment for posting?')) return;

    try {
      await JenAPI.approvePost(postId, comment);
      loadReviewPosts();
    } catch (error) {
      console.error('Failed to approve:', error);
    }
  };
```

Update `handleRemove` (lines 99-110):
```typescript
  const handleRemove = async (postId: string) => {
    if (!confirm('Remove this post from review queue?')) return;

    try {
      await JenAPI.deletePost(postId);
      loadReviewPosts();
    } catch (error) {
      console.error('Failed to remove:', error);
    }
  };
```

**Step 2: Verify build**

Run: `cd /Users/vitor.carvalho/social-agent-hackathon && npx vite build 2>&1 | tail -5`
Expected: Build succeeds

**Step 3: Commit**

```bash
git add components/ReviewPostsWidget.tsx
git commit -m "fix: replace process.env with centralized API in ReviewPostsWidget"
```

---

## Task 6: Fix AILearning.tsx — use centralized apiFetch

**Files:**
- Modify: `screens/AILearning.tsx`

**Step 1: Replace the local API layer**

Remove lines 5-18 (the local `API_BASE` and `apiFetchLocal` function).

Change line 3 from:
```typescript
import { ApiError } from '../services/api';
```
to:
```typescript
import { apiFetch, ApiError } from '../services/api';
```

Then update the `useEffect` (lines 58-74) to use the imported `apiFetch` instead of `apiFetchLocal`:

```typescript
  useEffect(() => {
    Promise.all([
      apiFetch<FeedbackStats>('/feedback/stats'),
      apiFetch<{ trend: TrendPoint[] }>('/feedback/accuracy-trend'),
      apiFetch<{ approved: FeedbackExample[]; denied: FeedbackExample[] }>('/feedback/examples'),
    ])
      .then(([statsData, trendData, examplesData]) => {
        setStats(statsData);
        setTrend(trendData.trend || []);
        setExamples(examplesData);
        setLoading(false);
      })
      .catch((err) => {
        setError(err instanceof ApiError ? err.detail : 'Unable to load AI Learning data.');
        setLoading(false);
      });
  }, []);
```

**Step 2: Verify build**

Run: `cd /Users/vitor.carvalho/social-agent-hackathon && npx vite build 2>&1 | tail -5`
Expected: Build succeeds

**Step 3: Commit**

```bash
git add screens/AILearning.tsx
git commit -m "fix: use centralized apiFetch in AILearning screen"
```

---

## Task 7: Fix CORS — add Vercel domain to backend defaults

**Files:**
- Modify: `backend/config.py:53`

**Step 1: Update default CORS origins**

Change line 53 from:
```python
    cors_origins: str = "http://localhost:3000,http://localhost:5173"
```
to:
```python
    cors_origins: str = "http://localhost:3000,http://localhost:5173,https://social-agent-hackathon.vercel.app"
```

Note: If the actual Vercel domain is different, adjust accordingly. The `CORS_ORIGINS` env var on Railway should still be set to include the exact production domain.

**Step 2: Commit**

```bash
git add backend/config.py
git commit -m "fix: add Vercel production domain to default CORS origins"
```

---

## Task 8: Add lightweight error/loading UI improvements to Overview

**Files:**
- Modify: `screens/Overview.tsx:31-41`

**Step 1: Replace silent catch blocks with meaningful defaults**

Change lines 31-42 from:
```typescript
  useEffect(() => {
    ExecutionAPI.getStatus()
      .then((status) => {
        setSystemStatus(status);
        setKillSwitch(status.kill_switch_enabled ?? false);
      })
      .catch(() => {});

    ConnectionsAPI.getConnections()
      .then(setConnections)
      .catch(() => {});
  }, []);
```
to:
```typescript
  useEffect(() => {
    ExecutionAPI.getStatus()
      .then((status) => {
        setSystemStatus(status);
        setKillSwitch(status.kill_switch_enabled ?? false);
      })
      .catch((err) => {
        console.warn('System status unavailable:', err);
        setSystemStatus({ uptime: 'N/A', discovery_latency_ms: null, queue_depth: null, api_health: 'N/A' });
      });

    ConnectionsAPI.getConnections()
      .then(setConnections)
      .catch((err) => {
        console.warn('Connections unavailable:', err);
        setConnections([]);
      });
  }, []);
```

**Step 2: Verify build**

Run: `cd /Users/vitor.carvalho/social-agent-hackathon && npx vite build 2>&1 | tail -5`
Expected: Build succeeds

**Step 3: Commit**

```bash
git add screens/Overview.tsx
git commit -m "fix: replace silent catch blocks with fallback defaults in Overview"
```

---

## Task 9: Commit all uncommitted changes and verify full build

**Files:**
- All modified/untracked files: `App.tsx`, `components/Sidebar.tsx`, `backend/main.py`, `backend/db/sqlite_store.py`, `backend/services/ai/rag.py`, `backend/routers/feedback.py`, `backend/services/ai/feedback_loop.py`

**Step 1: Review uncommitted changes**

Run: `git status && git diff --stat`

**Step 2: Stage and commit new features**

```bash
git add backend/routers/feedback.py backend/services/ai/feedback_loop.py screens/AILearning.tsx
git commit -m "feat: add AI Learning screen with feedback loop backend"
```

**Step 3: Stage and commit remaining modified files**

```bash
git add App.tsx components/Sidebar.tsx backend/main.py backend/db/sqlite_store.py backend/services/ai/rag.py package-lock.json
git commit -m "chore: sync uncommitted changes for deployment"
```

**Step 4: Final build verification**

Run: `cd /Users/vitor.carvalho/social-agent-hackathon && npx vite build 2>&1 | tail -10`
Expected: Build succeeds with no errors

**Step 5: Push to trigger deployment**

```bash
git push origin main
```

This triggers automatic deployment on both Vercel (frontend) and Railway (backend).

---

## Task 10: Verify production deployment

**Step 1: Wait for deployments to complete**

Check Vercel: visit the Vercel dashboard or run `vercel ls` if CLI is configured.
Check Railway: visit Railway dashboard.

**Step 2: Smoke test critical flows**

1. Open the Vercel URL in browser
2. Navigate to XHub (X/Twitter page) — verify stats load, no spinning forever
3. Try Smart Discovery — enter a query, verify posts appear
4. Try adding a post to review queue
5. Navigate to Overview dashboard — verify metrics load
6. Navigate to AI Learning — verify stats/charts load
7. Check browser DevTools Network tab — no `localhost:8000` requests should appear

**Step 3: If CORS errors appear**

Set `CORS_ORIGINS` env var on Railway to include the exact Vercel domain:
```
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,https://social-agent-hackathon.vercel.app
```
Then redeploy Railway.
