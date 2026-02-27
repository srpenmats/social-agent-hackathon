# Social Agent Pro → Production Plan
**Target:** Agent Trust Hub / Gen
**Timeline:** 2 days
**Focus:** Twitter monitoring for AI Agent Security conversations

---

## Current State Assessment

### ✅ What's Already Built (MoneyLion Base)
- **Full-stack architecture:**
  - Backend: Python/FastAPI with Supabase + pgvector
  - Frontend: React/Vite TypeScript
  - Twitter API v2 integration (OAuth + rate limiting)
  - Instagram, TikTok support (not needed now)

- **AI Services:**
  - RAG system (embeddings + retrieval)
  - Brand voice engine
  - Comment generator
  - Compliance/risk scoring
  - Voice drift detection

- **Infrastructure:**
  - Dashboard, review, settings APIs
  - Neoclaw integration
  - Multi-platform support

### ⚠️ Gaps to Address

1. **Brand Voice Context** — Currently MoneyLion-specific
   - Need Agent Trust Hub positioning
   - Gen product docs
   - AI agent security expertise

2. **RAG Retrieval** — Needs refinement for relevance
   - Must reference actual Gen offerings
   - Context-aware comment generation

3. **Production Deployment** — Not yet deployed
   - Need hosting strategy
   - Environment configuration
   - Live demo access

4. **Twitter Search Queries** — Need to define monitoring keywords
   - "AI agent security"
   - "agent trust"
   - Related terms

---

## 2-Day Implementation Plan

### Day 1: Core Adaptation (Today)

**Morning (4-6 hours):**
1. ✅ Clone repo (DONE)
2. **Replace brand voice context** (2 hours)
   - Awaiting Agent Trust Hub docs from aGENt
   - Create Gen-specific brand voice files
   - Update compliance rails if needed

3. **Configure Twitter monitoring** (2 hours)
   - Define search queries
   - Set up Twitter API credentials
   - Test discovery service

4. **Test RAG locally** (2 hours)
   - Verify embeddings generation
   - Test context retrieval
   - Ensure comments reference Gen appropriately

**Evening (4 hours):**
5. **Connect frontend ↔ backend** (2 hours)
   - Fix any API integration issues
   - Test dashboard flow

6. **Local end-to-end test** (2 hours)
   - Monitor → Discover → Generate → Review
   - Verify comment quality

### Day 2: Production Deployment

**Morning (4 hours):**
7. **Deployment setup** (3 hours)
   - Railway or Render for backend + DB
   - Vercel for frontend
   - Environment variables
   - Database migration

8. **Live testing** (1 hour)
   - End-to-end flow on production
   - Fix any deployment issues

**Afternoon (4 hours):**
9. **Polish & refinement** (2 hours)
   - UI improvements
   - Error handling
   - Loading states

10. **Documentation** (1 hour)
    - How to use
    - How to deploy updates
    - API reference

11. **Final demo prep** (1 hour)
    - Create demo account
    - Pre-populate with real data
    - Prepare walkthrough

---

## Immediate Next Steps

**Waiting on aGENt:**
1. **Agent Trust Hub context docs:**
   - Product positioning
   - Key messaging
   - What problems you solve
   - Target audience
   - Tone/voice guidelines

2. **Twitter API credentials** (if not already set up)
   - Bearer token or OAuth app credentials

3. **Deployment preferences:**
   - Railway? Render? Other?
   - Budget constraints?

**I can start now:**
- Set up local development environment
- Review/optimize RAG code
- Prepare deployment configs
- Design Gen-specific brand voice structure

---

## Questions for aGENt

1. **Brand voice:** How should Gen sound on Twitter?
   - Professional expert?
   - Conversational educator?
   - Technical but accessible?

2. **Engagement strategy:**
   - Only reply to direct questions?
   - Join broader conversations?
   - Proactive thought leadership?

3. **Risk tolerance:**
   - Conservative (only high-confidence matches)?
   - Moderate (broader relevance)?
   - Aggressive (maximize visibility)?

4. **Search scope:**
   - AI agent security (narrow)
   - AI agents broadly (medium)
   - AI/ML general + security topics (wide)

---

Ready to proceed as soon as you provide the context docs!
