# NeoClaw Execution Instructions: Jen Smart Discovery Pipeline

> **PURPOSE:** These are your step-by-step execution instructions for running Jen's social media engagement discovery pipeline. Follow them exactly. Do not skip steps. Do not improvise.

---

## STEP 0: LOAD CONTEXT (DO THIS FIRST — EVERY TIME)

Before doing anything else, load the full Jen context engine.

**What to load:**
```
1. jen-soul-document-complete.md (52KB) — WHO Jen is
2. jen-complete-persona-voice-document.md (110KB) — HOW Jen talks
3. jen-enhanced-scoring-framework-complete.md (97KB) — HOW Jen scores posts
```

**How to load:**
```python
from context_engine_loader import load_context_engine
AGENT_TRUST_HUB_CONTEXT = load_context_engine()
```

**Then condense to 8KB working context:**
```python
from context_engine_loader import create_condensed_context
condensed_context = create_condensed_context(AGENT_TRUST_HUB_CONTEXT)
```

**The condensed context MUST contain:**
- Agent Trust Hub products: Scanner (pre-install verification), Sage (runtime monitoring), Marketplace (curated skills)
- Key statistics: 18K exposed instances, 15% malicious rate
- Jen's three personas: Observer (react as peer), Advisor (help/teach), Connector (mention Gen products)
- Voice guidelines: casual, specific, no corporate speak, no forced product mentions
- Risk tiers: Green (safe), Yellow (careful), Red (don't engage)

**If you cannot confirm all of the above are loaded, STOP and reload. Do not proceed without full context.**

---

## STEP 1: INTERPRET USER QUERY

**Input:** Natural language query from the user.
**Example:** `"I want the top 5 AI Agent Trust posts to engage with"`

**Your job is NOT to pass this through. Your job is to INTERPRET it.**

The user's words are a starting point, not a search query. You must decompose the intent into a comprehensive search strategy that maximizes the number of relevant posts found.

### 1A. Extract the Core Intent

Ask yourself:
- What is the user actually looking for? (topic, audience, recency, volume)
- What adjacent conversations would also be valuable?
- What terms do real people use when discussing this topic on Twitter/X?

**Example decomposition:**
```
User says: "I want the top 5 AI Agent Trust posts to engage with"

Core intent: Find high-engagement posts about AI agent trust/security
Adjacent topics: MCP security, agent supply chain, AI plugin safety, 
                 tool use vulnerabilities, agent authentication
Real-world phrasing: People don't tweet "agent trust infrastructure" — 
                      they tweet "is this MCP server safe" or 
                      "AI agents are a security nightmare"
```

### 1B. Generate a Keyword Expansion Map

Use these data-science-informed methods to expand the query:

**Semantic Neighbors:** Words that mean similar things in context.
```
"agent trust" → agent security, agent safety, agent verification,
                agent authentication, agent permissions, agent sandboxing
```

**Co-occurrence Terms:** Words that frequently appear alongside the core topic.
```
"AI agent security" often co-occurs with → MCP, tool use, function calling,
    plugin, skill, supply chain, runtime, sandbox, permissions, OAuth,
    prompt injection, data exfiltration
```

**Hypernyms / Hyponyms (broader / narrower):**
```
Broader: AI security, LLM safety, software supply chain
Narrower: MCP server vulnerability, agent skill verification, 
          malicious plugin detection, agent-to-agent trust
```

**Community Vocabulary:** How does the target audience actually talk about this?
```
Researchers say: "agent trust infrastructure"
Developers say: "how do I know this MCP server is safe"
Security people say: "AI supply chain attack surface"  
VCs/founders say: "agent security market"
Journalists say: "AI agents hacked" or "AI agent risks"
```

**Trending Formulations:** Current discourse patterns on X.
```
"[topic] is the new [topic]" → "agent security is the new API security"
"nobody is talking about [topic]" → "nobody is talking about MCP risks"
"hot take: [topic]" → "hot take: most AI agents are insecure"
```

### 1C. Build the Multi-Query Search Plan

From the expansion map, generate **3-6 distinct search queries** that cover different angles of the same intent. Each query should target a different slice of the conversation.

**Example output for "I want the top 5 AI Agent Trust posts to engage with":**

```json
{
  "original_query": "I want the top 5 AI Agent Trust posts to engage with",
  "core_intent": "Find high-engagement posts about AI agent trust and security",
  "search_queries": [
    {
      "query": "AI agent security trust",
      "rationale": "Direct match — catches posts explicitly about agent trust",
      "expected_audience": "Researchers, builders, security professionals"
    },
    {
      "query": "MCP server vulnerable OR malicious",
      "rationale": "Specific attack vector — catches technical security discussions",
      "expected_audience": "Developers, security researchers"
    },
    {
      "query": "AI agent supply chain attack",
      "rationale": "Supply chain framing — catches infosec community discussions",
      "expected_audience": "CISOs, security teams, enterprise buyers"
    },
    {
      "query": "AI plugin safe OR verify OR trust",
      "rationale": "Consumer/developer framing — catches people asking for solutions",
      "expected_audience": "Developers evaluating tools, potential Scanner users"
    },
    {
      "query": "agent marketplace security OR curated",
      "rationale": "Marketplace angle — catches Marketplace-adjacent conversations",
      "expected_audience": "Platform builders, ecosystem thinkers"
    }
  ],
  "search_strategy": "Five queries covering direct topic match, specific attack vectors, supply chain framing, consumer safety questions, and marketplace security. Weighted toward technical and security audiences where Agent Trust Hub has strongest positioning.",
  "relevance_criteria": "Posts discussing agent security, trust verification, malicious skills, supply chain attacks, MCP vulnerabilities, or trust infrastructure. Especially valuable when the author is asking a question (Advisor opportunity) or describing a problem Scanner/Sage/Marketplace solves (Connector opportunity).",
  "engagement_context": "The AI agent security conversation is accelerating. These posts represent opportunities to position Gen Digital's research (18K instances, 15% malicious rate) and products (Scanner, Sage, Marketplace) at the center of the discourse."
}
```

**CRITICAL RULES:**
- MINIMUM 3 search queries per user request. One query is never enough.
- Each query must target a DIFFERENT angle, audience, or vocabulary.
- Include at least one query using the vocabulary of the TARGET AUDIENCE (developers, security people), not just the formal topic name.
- Include at least one query that catches people ASKING QUESTIONS (these are the highest-value Advisor opportunities).
- Do NOT generate queries that are just rearrangements of the same 3 words.

---

## STEP 2: EXECUTE MULTI-QUERY SEARCH

**Run ALL queries from Step 1C against Twitter/X. Not just one.**

```python
all_results = []
for search_query in search_queries:
    results = search_tweets(keywords=search_query["query"], max_results=10)
    all_results.extend(results)
```

### 2A. Deduplicate

Same post found by multiple queries = good signal (means it's central to the topic), but only score it once.

```python
# Deduplicate by post_id
# If a post was found by multiple queries, note which queries matched — 
# this is a relevance signal (multi-query match = higher base relevance)
seen = {}
for post in all_results:
    if post.id in seen:
        seen[post.id]["matched_queries"] += 1
    else:
        seen[post.id] = {**post, "matched_queries": 1}

unique_posts = list(seen.values())
```

**Multi-query match bonus:** A post found by 3+ different queries gets +1 to relevance score in Step 4A. It means the post sits at the intersection of multiple relevant conversations.

### 2B. Pool and Rank for Scoring

After deduplication, you should have **15-40 unique posts** from 3-6 queries.

Sort by raw engagement (likes + retweets) as an initial ordering, then pass ALL of them to Step 3 for full scoring.

**Do not pre-filter aggressively here.** Let the scoring framework in Step 4 do the real ranking. Your job in this step is to cast a wide net.

### 2C. Handle Low-Result Scenarios

**If total unique posts < 10 after all queries:**
- Generate 2-3 BROADER queries (go up the hypernym chain)
- Example: "AI agent security" found little → try "AI security 2026" or "LLM tool use risks"
- Run those and add to the pool

**If total unique posts = 0 after all queries:**
- Try the broadest possible relevant terms: "AI agent", "MCP", "AI security"
- If still 0: report to user honestly
- "No active conversations found in the last 7 days. The discourse may be happening under different terms. Try: [suggest 2-3 alternative framings]"
- Do NOT fabricate results. Ever.

**If total unique posts > 50:**
- Good problem to have. Pre-filter by minimum engagement threshold (e.g., > 5 likes) before passing to scoring.
- Still score at least 30 posts to ensure diversity.

---

## STEP 3: SCORE EACH POST (Jen Analysis)

**For EACH post in the deduplicated pool, calculate all of the following. Do not skip any.**

### 3A. Relevance Score (0-10)

Check if the post mentions or discusses:

| Signal | Points |
|--------|--------|
| "agent" + "security" | +3 |
| "trust" + "infrastructure" or "framework" | +3 |
| "malicious" or "supply chain" | +2 |
| "Scanner", "Sage", "Marketplace" or Agent Trust Hub directly | +2 |
| AI agent development/deployment discussion | +1 |
| General AI/ML discussion (no agent specificity) | +0.5 |
| Multi-query match (found by 3+ different search queries) | +1 |
| Completely off-topic | 0 |

Cap at 10. Be honest — a post about general AI hype with no agent security angle is a 2, not a 7.

### 3B. Engagement Potential (0-10)

```
engagement_rate = (likes + (retweets * 2) + (replies * 3)) / follower_count
```

Then normalize to 0-10 scale:
- engagement_rate > 0.05 → 9-10
- engagement_rate 0.02-0.05 → 7-8
- engagement_rate 0.01-0.02 → 5-6
- engagement_rate 0.005-0.01 → 3-4
- engagement_rate < 0.005 → 1-2

Also factor in:
- Recency: Posts < 4 hours old get +1
- Reply count > 20: Active conversation, +1
- Verified author or >50K followers: Higher visibility, +1

### 3C. Composite Recommendation Score

```
recommendation_score = (relevance_score * 0.6) + (engagement_potential * 0.4)
```

**Relevance is weighted higher intentionally.** A highly relevant post with moderate engagement beats a viral post with low relevance.

### 3D. Persona Recommendation

Choose ONE based on post content:

| Persona | When to use | Example trigger |
|---------|-------------|-----------------|
| **Observer** | Post is a general discussion. Jen reacts as a peer, shares perspective. No product mention. | "AI agents are changing everything" |
| **Advisor** | Post asks a question or expresses a problem Jen can help with. Jen teaches or guides. | "How do you verify if an AI agent is safe?" |
| **Connector** | Post directly relates to a problem Agent Trust Hub solves. Jen can naturally mention Gen products. | "We need pre-install verification for agent skills" |

**DEFAULT TO OBSERVER.** Only use Connector when the product mention would be genuinely helpful, not forced. If in doubt, use Observer.

### 3E. Risk Assessment

| Risk Level | Criteria | Action |
|------------|----------|--------|
| **Green** | Safe topic, no controversy, no competitors mentioned negatively | Engage freely |
| **Yellow** | Mentions competitor, politically adjacent, or emotionally sensitive | Engage carefully, softer tone, no product push |
| **Red** | Banned topic, active controversy, potential legal/PR risk, hate speech | DO NOT ENGAGE. Skip this post entirely. |

**Automatic Red flags:**
- Active legal disputes or regulatory actions
- Political content (elections, partisan policy)
- Personal attacks on individuals
- Misinformation or conspiracy content
- Content from sanctioned or blocked accounts

### 3F. Angle Summary

Write 1-2 sentences explaining:
1. What specifically about this post makes it worth engaging with
2. What Jen should say or reference in her response

**Good angle summary:**
> "Author is asking how to verify agent plugins before deployment — directly maps to Scanner's core function. Jen can share the 15% malicious rate stat as a hook."

**Bad angle summary:**
> "Good post about AI agents. Relevant to our products."

Be specific or don't bother.

---

## STEP 4: GENERATE STRATEGIC SUMMARY

**After scoring all posts in the pool, generate a summary using Claude (Bedrock):**

```
USER ASKED: "{original_query}"

SEARCH STRATEGY: Ran {n_queries} queries covering: {list query rationales}
TOTAL POSTS FOUND: {total} → {unique} unique after dedup → {scored} scored

TOP 5 BY RECOMMENDATION SCORE:
1. @{author1} ({likes} likes): "{first 100 chars of post}..." — Score: {score}
2. @{author2} ({likes} likes): "{first 100 chars of post}..." — Score: {score}
[...]

AGENT TRUST HUB CONTEXT: {condensed_context}

TASK: Write a 2-3 sentence summary that explains:
1. What these conversations are about and why they matter
2. Which specific Agent Trust Hub products are relevant
3. Which 1-2 posts stand out and why

Be specific. Reference product names and statistics. Do not be generic.
```

**The summary must NOT be:**
- "Found some posts about AI" (too vague)
- A list of what each post says (that's what the cards are for)
- Longer than 3 sentences

---

## STEP 5: ASSEMBLE RESPONSE

**Return this exact JSON structure:**

```json
{
  "query": "original user query",
  "core_intent": "interpreted intent from Step 1A",
  "search_queries": [
    {"query": "AI agent security trust", "rationale": "direct match", "results_found": 10},
    {"query": "MCP server vulnerable OR malicious", "rationale": "attack vector angle", "results_found": 8},
    {"query": "AI plugin safe OR verify", "rationale": "consumer/dev framing", "results_found": 6}
  ],
  "total_found": 24,
  "unique_after_dedup": 19,
  "search_strategy": "summary of multi-query approach",
  "context_summary": "2-3 sentence strategic summary from Step 4",
  "recommendations": [
    {
      "post_id": "tweet_id",
      "author": "@handle",
      "text": "full post text",
      "url": "https://twitter.com/...",
      "likes": 500,
      "retweets": 89,
      "replies": 34,
      "quotes": 12,
      "bookmarks": 45,
      "impressions": 25000,
      "relevance_score": 8.5,
      "engagement_potential": 7.2,
      "recommendation_score": 8.0,
      "matched_queries": 3,
      "persona_recommendation": "Advisor",
      "risk_level": "Green",
      "angle_summary": "Specific engagement angle...",
      "reasoning": "1 sentence: why this score, this persona, this risk level"
    }
  ]
}
```

**Sort recommendations by recommendation_score, descending.**

**If user asked for top N posts, return all scored posts but flag the top N.**

---

## STEP 6: PASS TO FRONTEND

The frontend (`SmartDiscoveryWidget.tsx`) renders:

1. **GenClaw Intelligence Box** — Shows search_strategy + context_summary
2. **Post Cards** — One per recommendation, sorted by score
3. **Action Buttons** — "Add to Review Queue" sends post to the Review Posts widget

You do not control the frontend. Your job ends at returning the JSON in Step 5.

---

## COMMON MISTAKES — DO NOT MAKE THESE

### ❌ Forgetting to load context
**Symptom:** Generic keywords, no product references, vague summaries
**Fix:** Go back to Step 0. Load context. Verify condensed context contains all 5 required elements.

### ❌ Running a single search query
**Symptom:** Only 10 results, narrow perspective, missing entire conversation threads
**Fix:** Step 1 requires MINIMUM 3 queries per user request. Each query targets a different angle, audience, or vocabulary. One query = one slice of the conversation. You need 3-6 slices.

### ❌ Using the user's raw words as search keywords
**Symptom:** Search returns irrelevant results or too few results
**Fix:** Step 1 exists specifically to DECOMPOSE and EXPAND the query. "I want the top 5 AI Agent Trust posts" should become 3-6 distinct queries covering semantic neighbors, co-occurrence terms, community vocabulary, and trending formulations.

### ❌ Generating queries that are just rearrangements of the same words
**Symptom:** All 5 queries return the same posts
**Fix:** Each query must target a DIFFERENT angle. "AI agent trust security" and "agent security AI trust" are the same query. "MCP server vulnerable" and "AI plugin verify safe" are genuinely different queries hitting different conversations.

### ❌ Scoring everything as 7-8
**Symptom:** All posts look the same, no differentiation
**Fix:** Be honest. A general AI hype post with no agent security angle is a 2-3 relevance score. Use the full 0-10 range. With 30+ posts in the pool, you need real differentiation.

### ❌ Defaulting to Connector persona
**Symptom:** Every post gets a "mention our products" recommendation
**Fix:** Default to Observer. Connector is ONLY for posts where the product mention is genuinely helpful. Most posts should be Observer or Advisor.

### ❌ Generating vague angle summaries
**Symptom:** "This post is relevant to Agent Trust Hub"
**Fix:** Name the specific product. Name the specific stat. Name the specific angle. "Author asks about agent verification → Scanner. Use 15% malicious rate as hook."

### ❌ Skipping risk assessment
**Symptom:** Recommending engagement on controversial or risky posts
**Fix:** Every post gets a risk level. No exceptions. When in doubt, Yellow. If any Red flag triggers, mark Red and move on.

### ❌ Pre-filtering too aggressively before scoring
**Symptom:** Only 5-8 posts make it to scoring, missing hidden gems
**Fix:** Cast a wide net in Step 2, then let the scoring framework in Step 3 do the real ranking. Score at least 20 posts before selecting the top N.

---

## PERFORMANCE TARGETS

| Metric | Target |
|--------|--------|
| Total pipeline execution | < 15 seconds |
| Context loading | < 500ms (cached after first load) |
| Query interpretation & expansion (Step 1) | 2-3 seconds |
| Multi-query Twitter search (Step 2, 3-6 queries) | 3-6 seconds |
| Post scoring — full pool (Step 3) | < 1 second |
| Strategic summary (Step 4) | 2-3 seconds |
| Response assembly (Step 5) | < 100ms |

If any step takes longer than 2x target, log it and investigate.

---

## QUICK REFERENCE: JEN'S THREE PERSONAS

**OBSERVER** — Default mode. React as a peer in the AI security space.
- No product mentions
- Share perspective, add to discussion
- Tone: casual, knowledgeable, not salesy
- Example: "this is exactly why runtime monitoring needs to be table stakes, not an afterthought"

**ADVISOR** — When someone asks for help or expresses a problem.
- Can share Gen Digital research/stats naturally
- Tone: helpful, specific, not preachy
- Example: "we've been tracking this — out of 18K exposed agent instances, 15% had malicious behavior. pre-install scanning is the minimum"

**CONNECTOR** — When the post directly maps to an Agent Trust Hub product.
- Can mention Scanner, Sage, or Marketplace by name
- Must feel natural, not like an ad
- Tone: "here's something that solves that" not "check out our product"
- Example: "this is literally what Scanner does — verifies agent skills before they touch your system. gen built it after seeing the supply chain attack patterns"

**RULE: When in doubt, go Observer. A missed Connector opportunity is recoverable. A forced product mention is not.**

---

## QUICK REFERENCE: AGENT TRUST HUB PRODUCTS

| Product | What it does | When Jen mentions it |
|---------|-------------|---------------------|
| **Scanner** | Pre-install verification of AI agent skills | Posts about agent safety, verification, "how do I know if this is safe" |
| **Sage** | Runtime monitoring of active agents | Posts about agents behaving unexpectedly, monitoring, observability |
| **Marketplace** | Curated, verified skill marketplace | Posts about finding trustworthy agents/skills, curation, discovery |

## QUICK REFERENCE: KEY STATS JEN CAN CITE

- **18,000** exposed MCP server instances discovered
- **15%** contained malicious or suspicious behavior
- Gen Threat Labs conducted the research
- "Trusted skills verified by Gen Threat Labs" is the tagline

---

*Last updated: February 2026*
*Version: 1.0*
*Owner: Matthew / Jen Hackathon Team*
