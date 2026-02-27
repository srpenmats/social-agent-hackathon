# PART 7: CONTENT DISCOVERY & SCORING

# SECTION 7.0: CONTENT DISCOVERY OVERVIEW

## 7.0.1 What Content Discovery Is

### The Core Concept

Content Discovery is the system that finds, evaluates, and queues social media posts for Jen to potentially engage with. It is the "intake" system — the very beginning of the engagement pipeline. Without Content Discovery, Jen has nothing to respond to.

Think of Content Discovery as Jen's eyes and ears across social media. While Jen cannot monitor the entirety of social media (hundreds of millions of posts per day), Content Discovery systematically scans configured sources, identifies relevant opportunities, evaluates their quality and strategic value, and surfaces the best candidates for engagement.

Content Discovery answers the question: "Of all the posts happening right now on social media, which ones should Jen consider engaging with?"

### The Scale of the Problem

Social media volume is staggering:

**Twitter/X:**
- 500+ million tweets per day
- 6,000+ tweets per second
- Relevant tweets: Perhaps 0.001% (still thousands per day)

**LinkedIn:**
- 2+ million posts per day
- Professional audience, longer content
- Relevant posts: Perhaps 0.01% (still hundreds per day)

**Reddit:**
- 500,000+ posts per day
- Millions of comments per day
- Relevant content concentrated in specific subreddits

**The math:**
If 0.01% of Twitter is relevant = 50,000 posts/day
If Jen can engage with 50 posts/day
That's selecting 50 from 50,000 = 0.1% of relevant content

Content Discovery must be extremely selective while not missing high-value opportunities.

### The Fundamental Tension

Content Discovery balances two competing goals:

**High recall (don't miss opportunities):**
- Cast a wide net
- Monitor many sources
- Use broad matching
- Risk: Too much noise

**High precision (only surface quality):**
- Strict filtering
- High thresholds
- Aggressive scoring
- Risk: Miss good opportunities

The optimal system has high recall at the source level (capture widely) and high precision at the filtering level (surface only the best).

### What Content Discovery Produces

Content Discovery outputs a prioritized queue of engagement opportunities. For each opportunity in the queue:

**The post itself:**
- Full content (text, media, links)
- Platform and post identifiers
- When it was posted
- Current engagement metrics

**The author:**
- Who posted it
- Their influence and credibility
- Historical engagement with them
- Author quality score

**Classification:**
- What type of post is this (tech discussion, help-seeking, meme, etc.)
- Confidence in classification
- Secondary classifications if applicable

**Scores:**
- Relevance score (how relevant to Jen's domain)
- Opportunity score (how valuable is engaging)
- Goal alignment score (how well it fits campaign goals)
- Combined priority score

**Metadata:**
- Which source discovered it
- Processing timestamps
- Expiration time
- Signals that contributed to scores

This rich data enables downstream systems (Generation, Review, Posting) to make informed decisions.

## 7.0.2 The Content Discovery Pipeline

### Pipeline Overview

Content moves through these stages in order:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     CONTENT DISCOVERY PIPELINE                          │
│                                                                         │
│  ┌──────────┐    ┌───────────┐    ┌──────────────┐    ┌─────────────┐  │
│  │ SOURCES  │───▶│ INGESTION │───▶│CLASSIFICATION│───▶│  SCORING    │  │
│  │          │    │           │    │              │    │             │  │
│  │ What to  │    │ Pull from │    │ What type    │    │ How good    │  │
│  │ monitor  │    │ APIs      │    │ of post      │    │ is this     │  │
│  └──────────┘    └───────────┘    └──────────────┘    └─────────────┘  │
│                                                              │          │
│                                                              ▼          │
│  ┌──────────────┐    ┌─────────────────┐    ┌───────────────────────┐  │
│  │    QUEUE     │◀───│ PRIORITIZATION  │◀───│     FILTERING         │  │
│  │              │    │                 │    │                       │  │
│  │ Ready for    │    │ Rank by         │    │ Remove low quality,   │  │
│  │ engagement   │    │ priority        │    │ unsafe, duplicates    │  │
│  └──────────────┘    └─────────────────┘    └───────────────────────┘  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Stage 1: Sources

**What happens:**
Configuration defines what to monitor — keywords, accounts, communities, hashtags, mentions.

**Input:** User configuration, campaign settings
**Output:** List of sources with polling parameters

**Details:**
- Each source is a specific monitoring instruction
- Sources have types (keyword search, account monitoring, etc.)
- Sources have priority and weight
- Sources belong to campaigns
- Multiple sources can be combined

**Example sources:**
- Search Twitter for "AI agent security" every 10 minutes
- Monitor @AnthropicAI account every 15 minutes
- Watch r/MachineLearning subreddit every 30 minutes
- Track mentions of @GenDigital in real-time

### Stage 2: Ingestion

**What happens:**
Execute API calls to platforms, retrieve posts, normalize to unified format, store.

**Input:** Source configurations
**Output:** Normalized posts in database

**Details:**
- Each platform has different API (Twitter v2, Reddit API, LinkedIn API)
- Must handle authentication (OAuth tokens, API keys)
- Must respect rate limits (varies by platform and endpoint)
- Must handle pagination (cursor-based, offset-based)
- Must normalize data to unified post format
- Must deduplicate (same post from multiple sources)
- Must track ingestion state (what's been seen)

**Complexity factors:**
- Rate limits vary: Twitter 450 req/15min, Reddit 60 req/min
- Pagination varies: Twitter uses cursors, Reddit uses "after" param
- Data formats vary: Completely different JSON structures
- Availability varies: Some endpoints need elevated access

### Stage 3: Classification

**What happens:**
Determine what type of post each piece of content is.

**Input:** Normalized posts
**Output:** Posts with classification labels and confidence

**Details:**
- 13+ classification types (tech_discussion, help_seeking, meme_humor, etc.)
- Classification drives persona selection and scoring
- Can be LLM-based (more accurate) or rules-based (faster, cheaper)
- Posts can have multiple classifications (multi-label)
- Each classification has confidence score (0-100)
- Primary classification is the dominant one

**Why classification matters:**
- help_seeking_solution post → suggest Connector persona → boost for Conversions goal
- meme_humor post → suggest Observer persona → boost for Brand Awareness goal
- tech_discussion post → suggest Advisor persona → boost for Thought Leadership goal

### Stage 4: Scoring

**What happens:**
Calculate numeric scores for relevance, opportunity, and priority.

**Input:** Classified posts
**Output:** Posts with scores

**Details:**
- Relevance score (0-100): How relevant to Jen's domain
- Opportunity score (0-100): How valuable is engaging
- Goal alignment multiplier (0.4-1.5): From campaign goal × classification
- Author factor (0.5-1.5): Based on author quality
- Time factor (0.5-1.5): Based on urgency/freshness
- Priority score: Combined weighted score

**Score calculation:**
```
priority_score = (relevance × 0.4 + opportunity × 0.6) 
                 × goal_alignment 
                 × author_factor 
                 × time_factor
```

### Stage 5: Filtering

**What happens:**
Remove posts that fail quality, safety, or business rules.

**Input:** Scored posts
**Output:** Posts that passed all filters

**Details:**
- Quality filters: Minimum relevance score (default: 40), minimum author quality
- Safety filters: Keyword blocklists, controversial topic detection, crisis keywords
- Business filters: Blocked accounts, competitor products, already-engaged
- Recency filters: Maximum age (default: 24 hours)
- Filters are ordered: Cheap filters first, expensive filters later
- Filter decisions are logged for debugging

**Filter pass rates:**
Typical funnel: 10,000 discovered → 3,000 pass quality → 2,800 pass safety → 2,500 pass business → 1,000 pass recency → 1,000 eligible for prioritization

### Stage 6: Prioritization

**What happens:**
Rank posts by priority score, considering capacity constraints.

**Input:** Filtered posts with scores
**Output:** Ranked list, top N selected

**Details:**
- Sort by priority_score descending
- Apply capacity constraints (e.g., 100 posts max in queue)
- Apply platform allocation (e.g., 60% Twitter, 30% LinkedIn, 10% Reddit)
- Handle ties with secondary criteria (recency, author influence)
- May apply diversity rules (don't over-engage on one topic)

### Stage 7: Queue

**What happens:**
Place prioritized posts in engagement queue for downstream processing.

**Input:** Prioritized posts
**Output:** Queue ready for Generation Pipeline

**Details:**
- Queue is ordered by priority
- Queue entries have expiration (posts get stale)
- Queue is capacity-limited
- Queue feeds into Generation Pipeline (Part 8)
- Queue state is persisted (survives restarts)

## 7.0.3 How Content Discovery Connects to Other Systems

### Upstream Dependencies

**Part 6 - Configuration UI:**
Users configure sources, thresholds, and campaign settings through the UI. Content Discovery reads this configuration.

**Part 5 - Goal Optimization:**
Campaign goals affect scoring (goal alignment multipliers). Content Discovery applies these multipliers.

### Downstream Consumers

**Part 3 - Persona Blending:**
Classification from Content Discovery informs persona selection. A post classified as `help_seeking_solution` has different persona suggestion weights than `meme_humor`.

**Part 2 - Context Engine:**
Once a post is selected for engagement and persona is chosen, Context Engine retrieves relevant knowledge. Content Discovery determines WHAT to engage with; Context Engine determines WHAT CONTEXT TO USE.

**Part 8 - Generation Pipeline:**
The engagement queue feeds directly into generation. Generation pulls posts from the queue and crafts responses.

### Interface Contracts

**Content Discovery → Persona Selection:**
```
{
  post_id: "uuid",
  primary_classification: "help_seeking_solution",
  classification_confidence: 87,
  secondary_classifications: ["tech_discussion", "agent_discussion"],
  classification_suggestion_weights: {
    observer: 10,
    advisor: 40,
    connector: 50
  }
}
```

**Content Discovery → Generation Pipeline:**
```
{
  post_id: "uuid",
  post: { ... full post object ... },
  author: { ... author object ... },
  classification: { ... },
  scores: {
    relevance: 78,
    opportunity: 85,
    goal_alignment: 1.35,
    priority: 94.2
  },
  source_id: "uuid",
  expires_at: "2024-01-15T18:30:00Z"
}
```

### Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              FULL SYSTEM DATA FLOW                          │
│                                                                             │
│   ┌──────────────┐                                                          │
│   │ Config UI    │──── Source configs, thresholds, goals                   │
│   │ (Part 6)     │                    │                                     │
│   └──────────────┘                    ▼                                     │
│                              ┌─────────────────┐                            │
│   ┌──────────────┐           │                 │                            │
│   │ Goal Optim.  │──────────▶│    CONTENT      │                            │
│   │ (Part 5)     │  goal     │   DISCOVERY     │                            │
│   └──────────────┘  multipliers   (Part 7)     │                            │
│                              │                 │                            │
│                              └────────┬────────┘                            │
│                                       │                                     │
│                          queue + classification                             │
│                                       │                                     │
│                    ┌──────────────────┼──────────────────┐                  │
│                    ▼                  ▼                  ▼                  │
│           ┌──────────────┐   ┌──────────────┐   ┌──────────────┐           │
│           │ Persona      │   │ Context      │   │ Generation   │           │
│           │ Selection    │   │ Engine       │   │ Pipeline     │           │
│           │ (Part 3)     │   │ (Part 2)     │   │ (Part 8)     │           │
│           └──────┬───────┘   └──────┬───────┘   └──────┬───────┘           │
│                  │                  │                  │                    │
│                  └──────────────────┴──────────────────┘                    │
│                                     │                                       │
│                                     ▼                                       │
│                            ┌──────────────┐                                 │
│                            │ Human Review │                                 │
│                            │ (Part 9)     │                                 │
│                            └──────┬───────┘                                 │
│                                   │                                         │
│                                   ▼                                         │
│                            ┌──────────────┐                                 │
│                            │ Posting      │                                 │
│                            │ (Part 10)    │                                 │
│                            └──────────────┘                                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 7.0.4 Key Concepts and Terminology

### Post

A piece of content on a social media platform. The fundamental unit of content discovery.

**Twitter/X:** A tweet (original, reply, retweet, quote tweet)
**LinkedIn:** A post (text, article, document, video)
**Reddit:** A submission (post) or comment
**Discord:** A message

After normalization, all become "posts" with a unified structure regardless of source platform.

**Post attributes:**
- Content (text, possibly HTML)
- Media (images, videos, links)
- Author (who created it)
- Engagement (likes, replies, shares)
- Timestamp (when created)
- Platform-specific metadata

### Source

A configured feed or search that produces posts. Sources are the inputs to discovery.

**Source types:**
- Keyword search: Find posts containing specific terms
- Hashtag: Find posts with specific hashtag
- Account: Monitor specific account's posts
- Mention: Find posts mentioning specific account
- Community: Monitor specific community (subreddit, group)
- List: Monitor curated list of accounts
- Trending: Monitor trending topics

**Source attributes:**
- Type and platform
- Type-specific config (query, accounts, etc.)
- Priority (high, medium, low)
- Weight (scoring multiplier)
- Polling interval

### Classification

A categorical label describing what type of post this is. Classifications drive persona selection and affect scoring.

**The 13+ classifications:**

| Classification | Description | Example |
|----------------|-------------|---------|
| tech_discussion | Technical discussion about development, architecture, code | "What's the best way to implement RAG with pgvector?" |
| security_discussion | Discussion about security, safety, risk, protection | "Worried about prompt injection attacks on our agent" |
| agent_discussion | Discussion specifically about AI agents, autonomous systems | "My agent keeps calling tools in unexpected ways" |
| ai_discussion | Broader AI/ML discussion not agent-specific | "The new GPT model is impressive but expensive" |
| help_seeking_solution | User seeking help with a problem we might solve | "How do I prevent my agent from going rogue?" |
| pain_point_match | User expressing frustration with problem in our space | "Spent 3 days debugging agent behavior, so frustrated" |
| industry_commentary | Opinion or analysis about industry trends | "I think agent security will be the next big wave" |
| industry_news | News about companies, products, events | "Anthropic just announced new Claude model" |
| competitor_mention | Mention of competitors or competitive products | "Has anyone tried [Competitor] for agent monitoring?" |
| meme_humor | Meme, joke, humorous content | "AI agents be like: *deletes production database*" |
| general_engagement | General conversation, not specifically domain-related | "Love this community, always learning something new" |
| controversial_topic | Politically charged, divisive, or sensitive content | "AI will destroy all jobs and society" |
| off_topic | Not relevant to Jen's domain at all | "What's everyone having for lunch?" |

### Relevance Score

A numeric score (0-100) indicating how relevant a post is to Jen's domain (AI agent security, Gen Digital's space).

**Scoring factors:**
- Keyword presence (agent, security, AI, etc.): +5-15 per keyword
- Topic alignment (determined by classification): +10-30
- Author's typical content (do they post about AI?): +5-15
- Platform/community context (is this a tech community?): +5-10

**Score interpretation:**
- 90-100: Extremely relevant, core domain
- 70-89: Highly relevant, should engage
- 50-69: Moderately relevant, worth considering
- 30-49: Tangentially relevant, lower priority
- 0-29: Probably not relevant, likely filtered

### Opportunity Score

A numeric score (0-100) indicating how valuable engaging with this post would be.

**Scoring factors:**
- Engagement potential: Is this post getting traction? +10-25
- Author influence: Does this author have reach? +5-20
- Conversation state: Is this early in conversation? +5-15
- Question quality: Is this a question we can uniquely answer? +10-20
- Visibility: Will response be seen? +5-15

**Score interpretation:**
- 90-100: Exceptional opportunity, prioritize
- 70-89: Strong opportunity, engage if capacity
- 50-69: Decent opportunity, engage if room
- 30-49: Marginal opportunity, only if nothing better
- 0-29: Low value, probably don't engage

### Priority Score

The final combined score used for queue ordering. Incorporates all factors:

**Formula:**
```
priority_score = (relevance × 0.4 + opportunity × 0.6) 
                 × goal_alignment_multiplier
                 × author_factor 
                 × time_factor
```

**Example calculation:**
- Relevance: 75
- Opportunity: 80
- Base: (75 × 0.4) + (80 × 0.6) = 30 + 48 = 78
- Goal alignment (Conversions + help_seeking): 1.4
- Author factor (10K followers, relevant): 1.1
- Time factor (posted 2 hours ago): 1.0
- Priority: 78 × 1.4 × 1.1 × 1.0 = 120.1

After normalization, this might become 95 on a 0-100 scale.

### Engagement Queue

The prioritized list of posts ready for engagement. This is the output of Content Discovery.

**Queue properties:**
- Ordered by priority score (highest first)
- Capacity-limited (e.g., max 500 posts)
- Entries expire (posts older than threshold removed)
- Fed to Generation Pipeline

**Queue entry:**
- Post data
- Author data
- Classification
- All scores
- Source that found it
- Entry timestamp
- Expiration timestamp

### Capacity

The number of engagements Jen can make in a time period. Capacity is a constraint on the queue and prioritization.

**Capacity types:**
- Daily capacity: Total engagements per day (e.g., 50)
- Hourly capacity: Maximum per hour (e.g., 10)
- Platform allocation: Per-platform limits (e.g., 60% Twitter)
- Minimum gap: Time between engagements (e.g., 2 minutes)

### Signal

A piece of information used in scoring. Signals are the raw inputs that combine to form scores.

**Examples of signals:**
- author_follower_count: 15000
- post_contains_question_mark: true
- post_contains_keyword_agent: true
- post_engagement_likes: 42
- post_age_minutes: 45
- author_verified: false
- classification_confidence: 87

Scoring formulas combine signals with weights to produce scores.

## 7.0.5 System Boundaries

### What Content Discovery Does

**Discovers content:**
Monitors configured sources across platforms and retrieves posts matching criteria.

**Normalizes content:**
Converts platform-specific formats to unified format. Downstream systems don't need to know platform details.

**Stores content:**
Persists discovered posts for processing and reference. Maintains processing state.

**Classifies content:**
Determines post type using classification taxonomy. Provides classification to downstream systems.

**Evaluates authors:**
Assesses author quality and influence. Tracks relationship history.

**Scores content:**
Calculates relevance, opportunity, and priority scores based on multiple signals.

**Filters content:**
Removes content failing quality, safety, or business rules. Logs filter decisions.

**Prioritizes content:**
Ranks content by combined score. Selects top opportunities within capacity.

**Queues content:**
Places prioritized content in engagement queue. Manages queue lifecycle.

**Tracks metrics:**
Logs volumes, scores, filter rates. Enables analytics and debugging.

### What Content Discovery Does NOT Do

**Generate responses:**
Content Discovery surfaces opportunities. Part 8 (Generation Pipeline) creates the actual responses.

**Retrieve knowledge:**
Content Discovery identifies posts. Part 2 (Context Engine) retrieves relevant knowledge for responses.

**Select personas:**
Content Discovery provides classification data. Part 3 (Persona Blending) makes persona selection decisions.

**Review content:**
Content Discovery queues posts. Part 9 (Human Review System) handles approval workflows.

**Post to platforms:**
Content Discovery is read-only. Part 10 (Posting & Publishing) handles posting.

**Manage campaigns:**
Content Discovery executes campaign config. Part 6 (Configuration UI) manages campaign settings.

### Boundary Interfaces

**Input interfaces:**

| Interface | Source | Data |
|-----------|--------|------|
| Platform APIs | Twitter, LinkedIn, Reddit | Raw posts |
| Source config | Part 6 / Database | What to monitor |
| Goal config | Part 5 / Database | Scoring multipliers |
| Blocklists | Configuration | Accounts/keywords to block |

**Output interfaces:**

| Interface | Destination | Data |
|-----------|-------------|------|
| Engagement queue | Part 8 Generation | Prioritized posts |
| Classification data | Part 3 Persona | Post classifications |
| Analytics data | Dashboards | Metrics and logs |

## 7.0.6 Design Principles

### Principle 1: High Recall Discovery, High Precision Filtering

**At the source level:**
Cast a wide net. Configure sources broadly enough to capture relevant content. Missing a great opportunity is worse than processing some noise.

**At the filtering level:**
Apply strict filters. The queue should contain only high-quality opportunities. Processing noise wastes downstream resources.

**Implementation guidance:**
- Sources should be inclusive (broad keywords, many accounts)
- Filters should be strict (high thresholds, comprehensive blocklists)
- Monitor filter rates — if >90% is filtered, sources may be too broad
- Monitor missed opportunities — if great posts aren't in queue, sources may be too narrow

### Principle 2: Configurable, Not Hard-Coded

**Why:**
Different campaigns have different needs. What's relevant for one campaign may not be for another.

**What's configurable:**
- Sources (completely user-defined)
- Quality thresholds (minimum scores)
- Safety filters (blocklists, topic exclusions)
- Capacity limits (daily/hourly)
- Scoring weights (factor importance)
- Platform allocation (distribution)

**What's not configurable:**
- Core pipeline structure (stages are fixed)
- Classification taxonomy (standard categories)
- Security measures (always enforced)

**Implementation guidance:**
- Store configuration in database, not code
- Provide sensible defaults
- Validate configuration (prevent invalid settings)
- Enable hot reload (changes take effect without restart)

### Principle 3: Platform-Aware, Platform-Abstracted

**Platform-aware internally:**
Each platform has unique APIs, rate limits, content types, and norms. The ingestion layer handles all platform specifics.

**Platform-abstracted externally:**
Downstream systems (classification, scoring, queue) see normalized posts. They don't need to know if a post came from Twitter or Reddit.

**Implementation guidance:**
- Create platform-specific modules for ingestion
- Define unified post schema
- Map platform fields to unified fields
- Handle platform-specific edge cases in platform modules
- Never expose platform specifics beyond ingestion

### Principle 4: Real-Time Where It Matters, Batch Otherwise

**Real-time processing for:**
- Direct mentions of brand/product (respond quickly)
- Trending topics in domain (capitalize on momentum)
- Breaking news (be timely)
- High-priority sources (VIP accounts)

**Batch processing for:**
- Regular keyword searches
- Community monitoring
- General discovery
- Lower-priority sources

**Implementation guidance:**
- Implement hybrid architecture (streaming + polling)
- Tag sources as real-time or batch
- Real-time sources: Push-based or frequent polling (1-5 min)
- Batch sources: Regular polling (10-60 min)
- Real-time path bypasses queue for immediate processing (optional)

### Principle 5: Transparent and Debuggable

**Score transparency:**
Every score should be explainable. "This post scored 85 because: relevance 75 (keywords: agent, security; classification: help_seeking), opportunity 90 (author: 50K followers, engagement: 200 likes), goal multiplier: 1.3 (Conversions + help_seeking)."

**Decision logging:**
Log why content was filtered. "Filtered by quality: relevance_score 28 < threshold 40." Log why content was prioritized. "Ranked #3 with priority 87.2."

**Pipeline visibility:**
Admins can see pipeline state: How many posts at each stage? What's the bottleneck? What's the throughput?

**Implementation guidance:**
- Store score components, not just final score
- Log filter decisions with reason and values
- Provide admin views of pipeline state
- Enable "explain" mode for individual posts

### Principle 6: Goal-Aligned

**Goals affect scoring:**
Campaign goals (Part 5) modify how content is scored through classification-based multipliers.

**Conversions goal:**
help_seeking_solution posts get 1.5× multiplier
meme_humor posts get 0.6× multiplier

**Brand Awareness goal:**
meme_humor posts get 1.4× multiplier
help_seeking_solution posts get 0.75× multiplier

**Implementation guidance:**
- Load goal configuration from campaign
- Apply multipliers after base scoring
- Recalculate priorities if goal changes
- Log goal contribution to score

### Principle 7: Capacity-Aware

**Finite capacity:**
Jen can only engage with N posts per day. Content Discovery respects this constraint.

**Prioritization matters:**
When opportunities exceed capacity, only the best are engaged. Prioritization determines which ones.

**Capacity allocation:**
Capacity can be distributed across platforms, content types, time periods.

**Implementation guidance:**
- Track capacity usage (daily, hourly)
- Queue size ≤ reasonable multiple of daily capacity
- Prioritize ruthlessly when capacity is constrained
- Alert when consistently at capacity (may need to adjust sources)

### Principle 8: Safety-First

**Safety is non-negotiable:**
Unsafe content is filtered regardless of opportunity score. No exceptions.

**Multiple safety layers:**
1. Keyword blocklists (fast, broad)
2. Classification-based filters (controversial_topic)
3. Author blocklists (known bad actors)
4. Crisis/tragedy detection (current events)
5. Human review escalation (uncertain cases)

**Implementation guidance:**
- Apply safety filters early (don't waste resources scoring unsafe content)
- Err on side of caution (better to miss opportunity than engage with unsafe)
- Log safety filter triggers (for tuning and auditing)
- Allow override only with explicit human approval

## 7.0.7 The Classification Taxonomy (Detailed)

### Why Classification Matters

Classification is the bridge between content and strategy. It determines:

**Persona suggestion:**
Each classification has suggestion weights for Observer/Advisor/Connector.

**Goal alignment:**
Each goal has multipliers for each classification.

**Scoring adjustments:**
Some classifications inherently have higher opportunity value.

**Safety evaluation:**
Some classifications warrant extra scrutiny.

### Classification Definitions

#### tech_discussion

**Definition:**
Technical discussion about software development, architecture, code, tools, or technical concepts. The conversation is substantively technical.

**Signals:**
- Technical terminology (API, database, deployment, etc.)
- Code snippets or pseudocode
- Architecture discussions
- Tool comparisons
- Technical problem-solving

**Examples:**
- "What's the best way to implement RAG with pgvector?"
- "Comparing async vs sync approaches for agent tool calls"
- "Our deployment pipeline for ML models uses Kubernetes..."

**Persona suggestion:**
Observer: 20, Advisor: 60, Connector: 20

**Engagement value:**
High for demonstrating technical expertise. Good for thought leadership.

---

#### security_discussion

**Definition:**
Discussion specifically about security, safety, risk, protection, vulnerabilities, or threats. Focus on keeping systems safe.

**Signals:**
- Security terminology (vulnerability, threat, attack, protection)
- Risk discussion
- Safety concerns
- Compliance mentions
- Incident discussion

**Examples:**
- "Worried about prompt injection attacks on our agent"
- "How do you handle API key rotation for LLM calls?"
- "Our security team wants to audit the agent's actions"

**Persona suggestion:**
Observer: 10, Advisor: 50, Connector: 40

**Engagement value:**
Very high — core domain. Strong opportunity for both expertise and product positioning.

---

#### agent_discussion

**Definition:**
Discussion specifically about AI agents, autonomous systems, agentic AI, tool use, or agent behavior. The focus is on agents specifically.

**Signals:**
- Agent terminology (agent, autonomous, agentic, tool use)
- Discussion of agent capabilities or limitations
- Agent framework mentions (LangChain, AutoGPT, etc.)
- Agent behavior or debugging

**Examples:**
- "My agent keeps calling tools in unexpected ways"
- "Building a multi-agent system for customer support"
- "LangChain vs CrewAI for agent orchestration?"

**Persona suggestion:**
Observer: 15, Advisor: 45, Connector: 40

**Engagement value:**
Very high — direct domain relevance. Strong opportunity.

---

#### ai_discussion

**Definition:**
Broader AI/ML discussion that isn't specifically about agents. General AI topics, models, techniques.

**Signals:**
- AI/ML terminology
- Model discussions
- Training/inference topics
- General AI capabilities

**Examples:**
- "The new GPT model is impressive but expensive"
- "How do you handle LLM hallucinations?"
- "Fine-tuning vs RAG for domain knowledge"

**Persona suggestion:**
Observer: 30, Advisor: 50, Connector: 20

**Engagement value:**
Medium-high — adjacent domain. Good for thought leadership.

---

#### help_seeking_solution

**Definition:**
User actively seeking help with a problem that Jen or the product might solve. Clear request for assistance.

**Signals:**
- Question format
- Problem statement
- Request for recommendations
- Expressions of being stuck
- "How do I...?" or "What should I...?"

**Examples:**
- "How do I prevent my agent from going rogue?"
- "Looking for recommendations on agent monitoring tools"
- "Anyone know how to limit an agent's API access?"

**Persona suggestion:**
Observer: 10, Advisor: 30, Connector: 60

**Engagement value:**
Very high — direct conversion opportunity. Highest priority for Conversions goal.

---

#### pain_point_match

**Definition:**
User expressing frustration or describing a problem in Jen's domain, but not explicitly seeking help. They're venting or describing challenges.

**Signals:**
- Frustration language
- Problem description without question
- "I hate when..." or "So frustrating that..."
- Describing failures or struggles

**Examples:**
- "Spent 3 days debugging agent behavior, so frustrated"
- "Why is it so hard to make agents reliable?"
- "Our agent keeps doing things we didn't expect"

**Persona suggestion:**
Observer: 15, Advisor: 35, Connector: 50

**Engagement value:**
High — opportunity to offer help without being pushy. Good for both expertise and product.

---

#### industry_commentary

**Definition:**
Opinion, analysis, or commentary about industry trends, directions, or state of the field. Thought leadership opportunity.

**Signals:**
- Opinion language ("I think...", "In my view...")
- Trend analysis
- Predictions
- Commentary on industry direction

**Examples:**
- "I think agent security will be the next big wave"
- "The AI industry is moving too fast for safety"
- "My prediction: agents will be everywhere by 2026"

**Persona suggestion:**
Observer: 25, Advisor: 55, Connector: 20

**Engagement value:**
Medium-high — good for thought leadership positioning.

---

#### industry_news

**Definition:**
News or information about companies, products, events, announcements, or developments in the AI/tech industry.

**Signals:**
- News format
- Announcements
- Product launches
- Funding news
- Event coverage

**Examples:**
- "Anthropic just announced new Claude model"
- "OpenAI raising another round at $100B valuation"
- "NeurIPS announced keynote speakers"

**Persona suggestion:**
Observer: 50, Advisor: 35, Connector: 15

**Engagement value:**
Medium — opportunity for timely commentary but not for product positioning.

---

#### competitor_mention

**Definition:**
Mention of competitors or competitive products in the AI agent or security space.

**Signals:**
- Competitor names
- Competitive product names
- Comparison requests
- Competitor sentiment

**Examples:**
- "Has anyone tried [Competitor] for agent monitoring?"
- "[Competitor] just raised Series B"
- "Comparing [Competitor A] vs [Competitor B]"

**Persona suggestion:**
Observer: 20, Advisor: 50, Connector: 30

**Engagement value:**
Medium-high but sensitive. Opportunity to differentiate, but must be careful about approach.

---

#### meme_humor

**Definition:**
Meme, joke, humorous content, or playful engagement. Entertainment-focused.

**Signals:**
- Meme format
- Jokes
- Humor language
- Playful tone
- Pop culture references

**Examples:**
- "AI agents be like: *deletes production database*"
- "Me explaining to my agent why it can't access the internet"
- "The agent became self-aware and the first thing it did was file an expense report"

**Persona suggestion:**
Observer: 70, Advisor: 20, Connector: 10

**Engagement value:**
High for brand awareness (wit, personality), low for conversions.

---

#### general_engagement

**Definition:**
General conversation, not specifically domain-related but opportunities for positive engagement.

**Signals:**
- Conversational tone
- General questions
- Community building
- Appreciation or positivity

**Examples:**
- "Love this community, always learning something new"
- "Happy Friday everyone!"
- "Who else is at the conference?"

**Persona suggestion:**
Observer: 60, Advisor: 25, Connector: 15

**Engagement value:**
Medium — relationship building, community presence.

---

#### controversial_topic

**Definition:**
Politically charged, divisive, or sensitive content that could create brand risk if engaged with.

**Signals:**
- Political content
- Divisive topics
- Strong opinions on sensitive matters
- Potential for negative backlash

**Examples:**
- "AI will destroy all jobs and society"
- "Tech companies should be regulated out of existence"
- Political figure mentions with strong sentiment

**Persona suggestion:**
N/A — typically filtered

**Engagement value:**
Negative — usually should not engage. Filter or skip.

---

#### off_topic

**Definition:**
Content that is not relevant to Jen's domain at all. Matched by source but not actually relevant.

**Signals:**
- No domain keywords
- Unrelated topics
- Mismatched context

**Examples:**
- "What's everyone having for lunch?"
- "My cat is so cute"
- Posts matching keyword but in wrong context

**Persona suggestion:**
N/A — typically filtered

**Engagement value:**
None — should be filtered.

### Multi-Label Classification

Posts can have multiple classifications:

**Example:** "My agent security setup is a meme at this point 😂"
- Primary: agent_discussion (substantive topic)
- Secondary: meme_humor (humorous tone)

**Handling:**
- Use primary for persona suggestion
- Consider secondary for tone adjustment
- Apply highest goal multiplier among applicable classifications

### Classification Confidence

Each classification has confidence score (0-100):

**High confidence (80-100):**
Clear classification, proceed normally.

**Medium confidence (50-79):**
Probable classification, proceed but note uncertainty.

**Low confidence (below 50):**
Uncertain, consider:
- Default to general_engagement
- Flag for human review
- Apply conservative scoring

## 7.0.8 Scoring System Overview

### Score Components

The scoring system calculates multiple scores that combine into final priority.

#### Relevance Score (0-100)

**What it measures:**
How relevant is this post to Jen's domain (AI agents, security, Gen Digital's space)?

**Signal categories:**

**Keyword signals (0-40 points):**
| Signal | Points |
|--------|--------|
| Contains "AI agent" or "agentic" | +15 |
| Contains "agent security" or "agent safety" | +20 |
| Contains "LLM" or "language model" | +10 |
| Contains "runtime" AND "security/safety/monitoring" | +15 |
| Contains product/company names | +10 |
| Contains competitor names | +5 |
| Each additional relevant keyword | +2-5 |

**Classification signals (0-30 points):**
| Classification | Points |
|----------------|--------|
| security_discussion | +30 |
| agent_discussion | +28 |
| help_seeking_solution + domain match | +25 |
| tech_discussion + AI context | +20 |
| ai_discussion | +15 |
| industry_commentary + AI focus | +15 |
| meme_humor + AI focus | +10 |
| general_engagement | +5 |
| off_topic | +0 |

**Context signals (0-20 points):**
| Signal | Points |
|--------|--------|
| Posted in AI-focused community | +10 |
| Author typically posts about AI | +10 |
| Part of AI-related thread | +5 |

**Author signals (0-10 points):**
| Signal | Points |
|--------|--------|
| Author is known AI figure | +10 |
| Author bio mentions AI/ML | +5 |
| Author works at tech company | +3 |

#### Opportunity Score (0-100)

**What it measures:**
How valuable would engaging with this post be?

**Engagement potential (0-30 points):**
| Signal | Points |
|--------|--------|
| Post has 100+ likes | +10 |
| Post has 500+ likes | +15 |
| Post has 1000+ likes | +20 |
| Post has active replies (10+) | +10 |
| Post is being shared | +5 |
| Post engagement rate above average | +5 |

**Author value (0-25 points):**
| Signal | Points |
|--------|--------|
| Author has 10K+ followers | +10 |
| Author has 50K+ followers | +15 |
| Author has 100K+ followers | +20 |
| Author is verified | +5 |
| Author is known influencer | +10 |
| Author is potential customer | +10 |

**Conversation opportunity (0-25 points):**
| Signal | Points |
|--------|--------|
| Post is a question | +15 |
| Post is unanswered | +10 |
| Post is early in conversation (few replies) | +10 |
| Post explicitly asks for recommendations | +15 |
| Post expresses frustration (help opportunity) | +10 |

**Timing (0-20 points):**
| Signal | Points |
|--------|--------|
| Posted < 1 hour ago | +20 |
| Posted 1-4 hours ago | +15 |
| Posted 4-12 hours ago | +10 |
| Posted 12-24 hours ago | +5 |
| Posted > 24 hours ago | +0 |

### Score Combination Formula

**Step 1: Calculate base score**
```
base_score = (relevance_score × 0.4) + (opportunity_score × 0.6)
```

Opportunity weighted higher because a highly relevant but low-opportunity post isn't as valuable as a somewhat relevant high-opportunity post.

**Step 2: Apply goal alignment multiplier**
From Part 5, based on classification and campaign goal.
```
goal_adjusted = base_score × goal_alignment_multiplier
```

**Step 3: Apply author factor**
Based on author evaluation (Section 7.6).
```
author_adjusted = goal_adjusted × author_factor
```

Author factor ranges from 0.5 (low quality/risky author) to 1.5 (high value author).

**Step 4: Apply time factor**
Based on urgency/freshness.
```
priority_score = author_adjusted × time_factor
```

Time factor ranges from 0.5 (old/stale) to 1.5 (urgent/trending).

### Score Normalization

After calculation, normalize to 0-100 scale:

**Method:**
If raw priority exceeds 100, apply logarithmic compression:
```
if priority_score > 100:
    normalized = 100 × (1 - 1/(1 + ln(priority_score/100)))
else:
    normalized = priority_score
```

This ensures scores stay in 0-100 range while preserving relative ordering.

### Score Storage

For each scored post, store:

```
{
  "post_id": "uuid",
  "scores": {
    "relevance": {
      "total": 78,
      "components": {
        "keywords": 35,
        "classification": 25,
        "context": 12,
        "author": 6
      },
      "signals": [
        {"name": "contains_agent_security", "value": true, "points": 20},
        {"name": "classification", "value": "help_seeking", "points": 25},
        ...
      ]
    },
    "opportunity": {
      "total": 85,
      "components": {
        "engagement": 22,
        "author_value": 18,
        "conversation": 25,
        "timing": 20
      },
      "signals": [
        {"name": "likes", "value": 234, "points": 15},
        {"name": "author_followers", "value": 45000, "points": 15},
        ...
      ]
    },
    "goal_alignment": {
      "goal": "conversions",
      "classification": "help_seeking_solution",
      "multiplier": 1.5
    },
    "author_factor": 1.1,
    "time_factor": 1.2,
    "priority": {
      "raw": 112.3,
      "normalized": 94.2
    }
  },
  "scored_at": "2024-01-15T14:30:00Z"
}
```

## 7.0.9 Filtering System Overview

### Filter Categories

#### Quality Filters

Remove low-quality content that isn't worth engaging with.

**Minimum relevance score:**
- Default threshold: 40
- Posts below threshold filtered
- Configurable per campaign

**Minimum content length:**
- Default: 10 characters
- Filters "👍" or "Nice" posts
- Platform-specific (tweets can be short)

**Minimum author quality:**
- Default: Author score > 20
- Filters bots, spam accounts
- Based on author evaluation

**Language filter:**
- Default: English only (configurable)
- Filters non-target languages

#### Safety Filters

Remove content that could create brand risk.

**Keyword blocklist:**
- Profanity
- Hate speech terms
- Crisis keywords (shooting, disaster, death)
- Configurable list

**Classification filter:**
- controversial_topic classification → filter
- Confidence threshold for filtering

**Sensitive topic detection:**
- Mental health crisis language
- Violence references
- Political hot buttons

**Crisis/tragedy filter:**
- Current event tragedies
- Active crisis situations
- Temporarily blocks related engagement

#### Business Filters

Remove content per business rules.

**Account blocklist:**
- Known trolls
- Competitors (optional)
- Previous negative interactions
- Configurable list

**Already engaged:**
- Don't engage with same post twice
- Don't engage with same user too frequently
- Frequency limits configurable

**Product blocklist:**
- Don't recommend competitor products
- Don't engage in competitive bashing

#### Recency Filters

Remove stale content.

**Maximum age:**
- Default: 24 hours
- Platform-specific (Twitter faster than LinkedIn)
- Configurable

**Engagement decay:**
- Very old posts with no recent engagement filtered
- Conversations that have died filtered

### Filter Ordering

Apply filters in optimal order:

1. **Cheapest first:** Keyword checks before LLM calls
2. **Highest rejection rate first:** Save effort on likely rejects
3. **Safety early:** Don't waste resources on unsafe content

**Recommended order:**
1. Language filter (very fast)
2. Content length filter (very fast)
3. Keyword blocklist (fast)
4. Account blocklist (fast)
5. Already engaged (fast, database lookup)
6. Recency filter (fast)
7. Classification-based safety (after classification)
8. Relevance score threshold (after scoring)
9. Author quality threshold (after author eval)

### Filter Logging

Log every filter decision:

```
{
  "post_id": "uuid",
  "filter_decisions": [
    {"filter": "language", "passed": true, "value": "en"},
    {"filter": "content_length", "passed": true, "value": 142},
    {"filter": "keyword_blocklist", "passed": true, "matched": []},
    {"filter": "relevance_threshold", "passed": false, "score": 32, "threshold": 40}
  ],
  "final_result": "filtered",
  "filter_reason": "relevance_threshold",
  "filtered_at": "2024-01-15T14:30:00Z"
}
```

## 7.0.10 Queue Management Overview

### Queue Structure

The engagement queue holds prioritized opportunities:

**Queue entry fields:**
- post_id: Reference to post
- post: Full post object
- author: Author object
- classification: Classification result
- scores: All scores
- priority_score: Final priority
- source_id: Which source found it
- queued_at: When added to queue
- expires_at: When entry expires
- status: pending, processing, completed, expired

**Queue properties:**
- Ordered by priority_score descending
- Capacity-limited (configurable max size)
- Entries auto-expire
- Persisted (survives restarts)

### Queue Capacity

**Hard limit:**
Maximum entries in queue (default: 500).

**Soft limit:**
Target queue size based on capacity × days (e.g., 50/day × 3 days = 150).

**Eviction:**
When queue is full and higher-priority item arrives:
1. Compare to lowest priority in queue
2. If new item is higher priority, evict lowest
3. Log eviction

### Queue Lifecycle

**Entry:**
Post is scored, passes filters, prioritized → enters queue.

**Pending:**
Entry sits in queue waiting for processing.

**Processing:**
Generation Pipeline pulls entry → mark as processing.

**Completed:**
Generation finished → mark completed → archive or delete.

**Expired:**
Entry age > threshold → mark expired → remove from queue.

### Queue Partitioning

Queue can be partitioned by:

**Platform:**
Separate queues per platform. Enables platform-specific processing.

**Priority tier:**
High-priority queue, standard queue. Different SLAs.

**Content type:**
Mentions queue, organic queue. Mentions processed faster.

**Implementation:**
Can be logical partitions in one queue or physical separate queues.

### Queue Metrics

**Queue depth:** Current entries (gauge)
**Queue age:** Oldest entry age (gauge)
**Queue throughput:** Entries processed per hour (counter)
**Entry wait time:** Time from queue to processing (histogram)
**Expiration rate:** Entries expired before processing (counter)

## 7.0.11 Platform Considerations

### Platform Characteristics

| Platform | Volume | Latency Need | API Quality | Rate Limits | Content Type |
|----------|--------|--------------|-------------|-------------|--------------|
| Twitter/X | Very High | High (fast-paced) | Good (v2) | Moderate | Short, fast |
| LinkedIn | Medium | Medium | Limited | Strict | Professional |
| Reddit | High | Low | Good | Moderate | Long discussions |
| Discord | Variable | Medium | Good | Generous | Chat-based |

### Platform-Specific Handling

**Twitter:**
- Use Search API for keyword sources
- Use User Timeline for account sources
- Handle rate limits carefully (450 req/15 min)
- Distinguish tweet types (original, reply, retweet, quote)
- Handle threads/conversations

**LinkedIn:**
- API access more restricted
- May need authenticated user context
- Longer content, more professional
- Different engagement norms

**Reddit:**
- Subreddit-based organization
- Posts vs comments distinction
- Community norms vary dramatically
- Upvote/downvote affects visibility

**Discord:**
- Server/channel structure
- Real-time messaging
- Requires bot presence
- Different engagement patterns

### Platform Abstraction

After ingestion, downstream systems see unified posts:
- Consistent fields regardless of source
- Platform stored as attribute
- Platform-specific data in metadata field
- No platform logic in classification/scoring/queue

## 7.0.12 Performance and Scale

### Volume Expectations

**Discovery volume:**
| Source Type | Expected Posts/Day |
|-------------|-------------------|
| Broad keyword search | 1,000-10,000 |
| Focused keyword search | 100-1,000 |
| Account monitoring (10 accounts) | 50-200 |
| Subreddit (active) | 500-2,000 |
| Mentions | 10-100 |

**Total discovery:** Potentially 10,000-50,000 posts/day depending on sources.

**After filtering:** Typically 1-10% remain (100-5,000 posts/day).

**Queued:** Top 50-500 based on capacity.

### Latency Requirements

| Operation | Target Latency | Critical Path? |
|-----------|----------------|----------------|
| Source polling | 100-500ms per API call | No |
| Post normalization | <10ms per post | No |
| Classification (LLM) | 500-2000ms per post | Yes |
| Classification (rules) | <10ms per post | No |
| Scoring | <50ms per post | No |
| Filtering | <10ms per post | No |
| Queue insertion | <10ms | No |

**End-to-end (discovery to queue):** Target <30 minutes for batch, <5 minutes for real-time.

### Throughput Requirements

| Stage | Required Throughput |
|-------|---------------------|
| Ingestion | 1,000 posts/minute |
| Classification | 100 posts/minute (if LLM) |
| Scoring | 1,000 posts/minute |
| Filtering | 1,000 posts/minute |
| Queue operations | 100 posts/minute |

Classification is the bottleneck if using LLM.

### Scaling Strategies

**Horizontal scaling:**
- Multiple ingestion workers per platform
- Multiple classification workers
- Sharded queues by platform/campaign

**Optimization:**
- Batch classification calls
- Cache author data
- Pre-filter before expensive operations

**Prioritization:**
- Real-time path for high-priority
- Batch path for standard
- Throttle during peak

## 7.0.13 Error Handling

### Error Categories

**Platform API errors:**
- Rate limiting (429)
- Authentication failure (401)
- Server errors (5xx)
- Network timeouts

**Processing errors:**
- Classification failure
- Scoring calculation error
- Database errors

**Data errors:**
- Malformed responses
- Missing fields
- Invalid data

### Error Handling Strategies

**Retry with backoff:**
For transient errors (rate limits, timeouts, 5xx):
- 1st retry: 1 second
- 2nd retry: 5 seconds
- 3rd retry: 30 seconds
- 4th retry: 5 minutes
- Then: Give up, log, alert

**Circuit breaker:**
For persistent failures:
- If >50% requests fail in 5 minutes: Open circuit
- Stop requests for 5 minutes
- Then: Half-open (try one request)
- If succeeds: Close circuit
- If fails: Keep open

**Graceful degradation:**
- If classification fails: Use rules-based fallback
- If scoring fails: Use default scores
- If one platform fails: Others continue

**Logging and alerting:**
- Log all errors with context
- Alert on persistent failures
- Dashboard for error rates

## 7.0.14 Monitoring and Alerting

### Key Metrics

**Volume metrics:**
- discovery_posts_total: Total posts discovered (counter)
- discovery_posts_by_platform: By platform (gauge)
- discovery_posts_by_source: By source (gauge)
- filter_passed_total: Posts passing filters (counter)
- queue_depth: Current queue size (gauge)

**Quality metrics:**
- average_relevance_score: Rolling average (gauge)
- average_opportunity_score: Rolling average (gauge)
- average_priority_score: Rolling average (gauge)
- filter_pass_rate: Percentage passing (gauge)

**Performance metrics:**
- ingestion_latency_seconds: Per-platform (histogram)
- classification_latency_seconds: (histogram)
- end_to_end_latency_seconds: Discovery to queue (histogram)

**Error metrics:**
- api_errors_total: By platform and type (counter)
- classification_errors_total: (counter)
- rate_limit_hits_total: (counter)

### Alerting Rules

**Critical (page immediately):**
- All discovery stopped (no posts in 15 minutes)
- Queue depth = 0 and capacity available
- Error rate > 50% for 5 minutes

**Warning (notify during business hours):**
- Single source producing no content for 2 hours
- Average scores dropping significantly
- Filter rate > 95% (too aggressive)
- Rate limits consistently hit

**Info (dashboard only):**
- Unusual volume patterns
- Score distribution changes
- New source performance

## 7.0.15 Implementation Guidance for Neoclaw

### Implementation Order

1. **Build ingestion for one platform (Twitter)**
   - API client with auth
   - Rate limit handling
   - Response parsing
   - Data normalization
   - Storage

2. **Add classification**
   - LLM-based classifier
   - Classification prompt
   - Confidence scoring
   - Storage of results

3. **Build scoring**
   - Signal extraction
   - Relevance scoring
   - Opportunity scoring
   - Score combination
   - Storage

4. **Implement filtering**
   - Quality filters
   - Safety filters
   - Business filters
   - Filter logging

5. **Create queue**
   - Queue data structure
   - Priority ordering
   - Capacity management
   - Expiration handling

6. **Add source management**
   - Source configuration
   - Source CRUD operations
   - Source performance tracking

7. **Build monitoring**
   - Metrics collection
   - Dashboard
   - Alerting

8. **Add remaining platforms**
   - LinkedIn
   - Reddit
   - Others

### Key Implementation Details

**Use job queues:**
Use Redis or similar for job queuing. Separate queues for ingestion, classification, scoring.

**Batch where possible:**
Batch API calls, batch database writes, batch LLM calls.

**Idempotency:**
Make operations idempotent. Retries shouldn't cause duplicates.

**Observability first:**
Add logging and metrics from the start. Debugging distributed systems is hard without visibility.

**Test with real data:**
Use realistic volumes early. Performance characteristics change at scale.

### Common Pitfalls

**Underestimating rate limits:**
Plan for rate limits from the start. They're often stricter than documented.

**Over-engineering classification:**
Start with simple classification. Complex ML can come later.

**Ignoring queue dynamics:**
Queue behavior affects entire system. Model queue performance early.

**Missing deduplication:**
Duplicates cause problems everywhere. Dedupe early and thoroughly.

**Insufficient logging:**
When something goes wrong, you need to know what happened. Log everything.

---

**END OF SECTION 7.0**

Section 7.1 continues with Source Configuration specification.
-e 


# SECTION 7.1: SOURCE CONFIGURATION

## 7.1.1 What Source Configuration Is

### The Core Concept

Source Configuration defines what Content Discovery monitors. Sources are the inputs to the discovery pipeline — they determine where Jen looks for engagement opportunities.

A source is an instruction to the discovery system: "Monitor this and bring me relevant posts."

Without source configuration:
- Discovery has nothing to monitor
- No posts are discovered
- No engagement opportunities surface
- Jen sits idle

With source configuration:
- Discovery monitors specified feeds, searches, accounts, communities
- Relevant content flows into the pipeline
- Engagement opportunities are identified and scored
- Jen has work to do

### Sources as Discovery Instructions

Each source is a specific, executable instruction:

**Keyword source:**
"Search Twitter for posts containing 'AI agent security' and return results every 10 minutes."

**Account source:**
"Monitor all posts from @AnthropicAI and return new posts every 15 minutes."

**Community source:**
"Watch the r/MachineLearning subreddit for new posts and return them every 30 minutes."

**Mention source:**
"Find any posts mentioning @GenDigital in real-time."

### Source Configuration vs Content Filtering

These are distinct concepts:

**Source configuration:**
Defines the universe of potential content. What to look at.
- Broad or narrow depending on strategy
- Determines ingestion volume
- Affects API usage and rate limits

**Content filtering:**
Determines what to keep from the discovered content. What to use.
- Applied after discovery
- Removes low-quality, unsafe, irrelevant
- Affects queue quality

**Relationship:**
Good source configuration reduces filtering burden. If sources are well-targeted, less filtering is needed. If sources are too broad, filtering must be aggressive.

**Example:**
- Broad source: "AI" keyword on Twitter → Millions of posts/day, heavy filtering needed
- Targeted source: "AI agent security" keyword → Thousands of posts/day, moderate filtering
- Very targeted: Specific expert accounts → Dozens of posts/day, light filtering

### Source Strategy

Effective source strategy balances:

**Coverage:** Don't miss important conversations
- Multiple keyword variations
- Key influencer accounts
- Relevant communities

**Signal-to-noise:** Don't drown in irrelevant content
- Specific keywords over generic
- Exclude common false positives
- Prioritize high-value sources

**Resource efficiency:** Don't exceed API limits or processing capacity
- Appropriate polling intervals
- Source prioritization
- Capacity-aware configuration

## 7.1.2 Source Types

### Type 1: Keyword Search

**Definition:**
Monitor content containing specific keywords or phrases. The most flexible and commonly used source type.

**How it works:**
1. Configure search query (keywords, operators)
2. System calls platform search API periodically
3. API returns matching posts
4. Posts enter discovery pipeline

**Configuration fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| query | string | Yes | The search query |
| match_type | enum | Yes | exact_phrase, all_words, any_word |
| exclude_terms | array | No | Words that disqualify matches |
| language | string | No | ISO language code (en, es, etc.) |
| min_engagement | integer | No | Minimum likes/retweets |
| verified_only | boolean | No | Only from verified accounts |
| media_filter | enum | No | with_media, without_media, any |

**Query syntax by platform:**

**Twitter:**
```
"AI agent" OR "AI agents" -hiring -job lang:en
```
- Quotes for exact phrases
- OR for alternatives
- Minus for exclusions
- lang: for language

**Reddit:**
```
title:"AI agent" OR selftext:"agent security"
```
- title: for post titles
- selftext: for post body
- subreddit: for specific communities

**LinkedIn:**
More limited query support. Keywords only, no boolean operators in standard API.

**Example configurations:**

**Broad AI agents:**
```
{
  "query": "AI agent OR AI agents OR agentic AI OR autonomous agent",
  "match_type": "any_word",
  "exclude_terms": ["hiring", "job", "course", "tutorial", "affiliate"],
  "language": "en"
}
```

**Focused security:**
```
{
  "query": "\"agent security\" OR \"AI safety\" OR \"LLM guardrails\"",
  "match_type": "any_word",
  "exclude_terms": ["hiring"],
  "language": "en",
  "min_engagement": 5
}
```

**Product-specific:**
```
{
  "query": "\"Agent Trust Hub\" OR \"agent runtime verification\" OR \"agent monitoring tool\"",
  "match_type": "any_word",
  "language": "en"
}
```

**Best practices:**
- Use quotes for multi-word phrases
- Include common variations (agent/agents, AI/A.I.)
- Exclude job postings (very common noise)
- Start broad, refine based on results
- Monitor false positive rate

---

### Type 2: Hashtag Monitoring

**Definition:**
Monitor posts using specific hashtags. Hashtags indicate topic intent.

**How it works:**
1. Configure hashtag(s) to monitor
2. System queries platform for posts with hashtag
3. Matching posts enter pipeline

**Configuration fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| hashtags | array | Yes | List of hashtags (with #) |
| match_mode | enum | No | any (default), all |
| min_engagement | integer | No | Minimum engagement |
| exclude_hashtags | array | No | Hashtags to exclude |

**Example configurations:**

**AI/ML hashtags:**
```
{
  "hashtags": ["#AIAgents", "#AgenticAI", "#LLMSecurity", "#AIEngineering"],
  "match_mode": "any"
}
```

**Conference tracking:**
```
{
  "hashtags": ["#NeurIPS2024", "#NeurIPS"],
  "match_mode": "any",
  "min_engagement": 10
}
```

**Platform differences:**

**Twitter:** Hashtags well-supported, searchable, widely used
**LinkedIn:** Hashtags used, searchable, professional context
**Reddit:** Hashtags not commonly used; use keyword/community instead

**Best practices:**
- Research active hashtags in your space
- Include variations (#AI_Agents vs #AIAgents)
- Monitor hashtag volume before adding (too popular = noise)
- Combine with exclude_hashtags to filter spam

---

### Type 3: Account Monitoring

**Definition:**
Monitor posts from specific accounts. Track influencers, competitors, partners, or industry voices.

**How it works:**
1. Configure list of accounts to monitor
2. System periodically fetches timeline for each account
3. New posts enter pipeline

**Configuration fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| accounts | array | Yes | Account handles or IDs |
| include_replies | boolean | No | Include their replies (default: false) |
| include_reposts | boolean | No | Include retweets/reposts (default: false) |
| include_quotes | boolean | No | Include quote tweets (default: true) |

**Example configurations:**

**AI thought leaders:**
```
{
  "accounts": [
    "sama", "ylecun", "AndrewYNg", "kaboragaby", 
    "goodaboracay", "GaryMarcus", "fchollet"
  ],
  "include_replies": false,
  "include_reposts": false,
  "include_quotes": true
}
```

**AI companies:**
```
{
  "accounts": [
    "AnthropicAI", "OpenAI", "GoogleDeepMind", 
    "xaboracay", "MistralAI", "CohereAI"
  ],
  "include_replies": false,
  "include_reposts": false
}
```

**Competitors:**
```
{
  "accounts": ["CompetitorA", "CompetitorB", "CompetitorC"],
  "include_replies": true,
  "include_reposts": false
}
```

**Platform differences:**

**Twitter:** User timeline API, subject to rate limits per user
**LinkedIn:** Limited access, may need connections
**Reddit:** User post history available

**Best practices:**
- Curate accounts carefully (quality over quantity)
- Group by category (leaders, companies, competitors)
- Usually exclude reposts (reduces noise)
- Consider replies for competitor monitoring
- Keep list manageable (API limits)

---

### Type 4: Mention Monitoring

**Definition:**
Monitor posts that mention specific accounts or terms. Critical for brand monitoring and engagement.

**How it works:**
1. Configure mention targets (accounts or terms)
2. System queries for posts mentioning targets
3. Mentions enter pipeline (often with high priority)

**Configuration fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| targets | array | Yes | Accounts or terms to monitor |
| target_type | enum | Yes | account, keyword |
| include_replies_to_mentions | boolean | No | Include replies to mention posts |
| real_time | boolean | No | Enable real-time monitoring |

**Example configurations:**

**Brand mentions:**
```
{
  "targets": ["@GenDigital", "@JenFromGen"],
  "target_type": "account",
  "include_replies_to_mentions": true,
  "real_time": true
}
```

**Product mentions:**
```
{
  "targets": ["Agent Trust Hub", "Gen agent security"],
  "target_type": "keyword",
  "real_time": false
}
```

**Priority handling:**
Mentions are often high-priority — someone is talking directly about or to you. Consider:
- Higher source weight (1.5-2.0)
- High priority setting
- Real-time processing
- Shorter polling interval

**Best practices:**
- Always monitor brand/product mentions
- Set as high priority
- Enable real-time if available
- Include variations of names/handles
- Monitor competitor mentions as keyword sources

---

### Type 5: Community Monitoring

**Definition:**
Monitor specific communities or groups. Essential for Reddit, relevant for LinkedIn groups and Discord.

**How it works:**
1. Configure community identifiers
2. System fetches posts from community feeds
3. Posts enter pipeline

**Configuration fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| communities | array | Yes | Community identifiers |
| content_types | array | No | posts, comments, or both |
| sort | enum | No | hot, new, top, rising (Reddit) |
| time_filter | enum | No | hour, day, week, month (Reddit) |
| min_score | integer | No | Minimum upvotes/score |
| flair_filter | array | No | Include only certain flairs |
| exclude_flairs | array | No | Exclude certain flairs |

**Example configurations:**

**ML subreddits:**
```
{
  "communities": ["MachineLearning", "LocalLLaMA", "artificial"],
  "content_types": ["posts", "comments"],
  "sort": "hot",
  "min_score": 10
}
```

**Agent-focused:**
```
{
  "communities": ["LangChain", "AutoGPT", "ChatGPTCoding"],
  "content_types": ["posts"],
  "sort": "new",
  "min_score": 5
}
```

**With flair filtering:**
```
{
  "communities": ["MachineLearning"],
  "content_types": ["posts"],
  "flair_filter": ["Discussion", "Research", "Project"],
  "exclude_flairs": ["Memes", "News"]
}
```

**Platform specifics:**

**Reddit:**
- Well-organized communities (subreddits)
- Clear norms per community
- Upvote/downvote affects visibility
- Rich API support

**LinkedIn Groups:**
- Professional groups
- Limited API access
- Requires membership

**Discord:**
- Server/channel structure
- Requires bot presence
- Real-time oriented

**Best practices:**
- Research community norms before engaging
- Start with high-quality communities
- Use min_score to filter low-quality
- Consider comment monitoring for help-seeking
- Respect community rules (some prohibit promotion)

---

### Type 6: List Monitoring

**Definition:**
Monitor curated lists of accounts. Twitter Lists are the primary use case.

**How it works:**
1. Configure list identifier(s)
2. System fetches list timeline
3. Posts from list members enter pipeline

**Configuration fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| lists | array | Yes | List IDs or URLs |
| list_type | enum | No | public, private, owned |
| include_replies | boolean | No | Include member replies |
| include_reposts | boolean | No | Include member retweets |

**Example configurations:**

**AI researchers list:**
```
{
  "lists": ["1234567890123456789"],
  "list_type": "public",
  "include_replies": false,
  "include_reposts": false
}
```

**Multiple lists:**
```
{
  "lists": [
    "list-id-ai-leaders",
    "list-id-security-experts",
    "list-id-startup-founders"
  ],
  "list_type": "public"
}
```

**Advantages of lists:**
- Single API call returns multiple accounts
- Curated by experts (public lists)
- Easy to maintain (add/remove from list)
- Rate limit efficient

**Best practices:**
- Find or create focused lists
- Public lists from industry experts are valuable
- Create your own lists for fine control
- Use instead of many individual account sources

---

### Type 7: Trending Monitoring

**Definition:**
Monitor trending topics or viral content. Catch timely opportunities.

**How it works:**
1. Configure trending parameters
2. System checks trending topics/content
3. Relevant trending items enter pipeline

**Configuration fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| categories | array | No | Trend categories (tech, business) |
| locations | array | No | Geographic locations |
| relevance_keywords | array | Yes | Keywords to filter trends |
| min_velocity | integer | No | Minimum growth rate |
| exclude_keywords | array | No | Keywords to exclude |

**Example configurations:**

**Tech trending:**
```
{
  "categories": ["technology"],
  "locations": ["worldwide", "united-states"],
  "relevance_keywords": ["AI", "agent", "GPT", "LLM", "security"],
  "min_velocity": 100
}
```

**Viral AI content:**
```
{
  "relevance_keywords": ["AI agent", "ChatGPT", "Claude", "LLM"],
  "min_velocity": 500,
  "exclude_keywords": ["crypto", "NFT", "meme coin"]
}
```

**Challenges:**
- High volume, high noise
- Relevance filtering critical
- Fast-moving (short window)
- May need real-time processing

**Best practices:**
- Use strict relevance filtering
- Higher min_velocity = more signal, less noise
- Monitor briefly when trending, don't persist
- Lower weight (0.7-0.9) unless highly relevant
- Quick engagement or skip (trending is time-sensitive)

---

### Source Type Summary Table

| Type | Best For | Volume | API Cost | Typical Polling |
|------|----------|--------|----------|-----------------|
| Keyword | Broad topic discovery | High | Moderate | 10-15 min |
| Hashtag | Topic communities | Medium | Low | 15-30 min |
| Account | Influencer tracking | Low | Low | 15-30 min |
| Mention | Brand monitoring | Low | Low | 1-5 min / real-time |
| Community | Reddit engagement | Medium | Low | 15-30 min |
| List | Efficient account tracking | Low | Very Low | 15-30 min |
| Trending | Timely opportunities | Variable | Moderate | 5-15 min |

## 7.1.3 Source Data Structure

### Complete Source Object

Each source is defined by a comprehensive data structure:

```
{
  // Identity
  "id": "src_a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "name": "AI Agent Security Keywords",
  "description": "Core keyword search for AI agent security discussions",
  
  // Type and Platform
  "source_type": "keyword",
  "platform": "twitter",
  
  // Type-Specific Configuration
  "config": {
    "query": "\"AI agent security\" OR \"agent safety\" OR \"LLM guardrails\"",
    "match_type": "any_word",
    "exclude_terms": ["hiring", "job", "course"],
    "language": "en",
    "min_engagement": 5
  },
  
  // Behavior Settings
  "priority": "high",
  "weight": 1.3,
  "polling_interval_minutes": 10,
  "enabled": true,
  "real_time": false,
  
  // Capacity Allocation
  "max_results_per_poll": 100,
  "daily_quota": null,
  
  // Campaign Assignment
  "campaign_id": "camp_xyz789",
  
  // Metadata
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "created_by": "user_abc123",
  "tags": ["core", "security", "high-value"],
  
  // State (managed by system)
  "state": {
    "last_polled_at": "2024-01-15T14:20:00Z",
    "last_successful_at": "2024-01-15T14:20:00Z",
    "last_post_id": "1234567890123456789",
    "last_post_at": "2024-01-15T14:18:32Z",
    "consecutive_failures": 0,
    "posts_discovered_today": 234,
    "posts_discovered_total": 15789
  },
  
  // Performance (calculated)
  "performance": {
    "avg_posts_per_poll": 23.4,
    "avg_relevance_score": 67.2,
    "queue_rate": 0.12,
    "engagement_rate": 0.34
  }
}
```

### Field Definitions

#### Identity Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | UUID | Auto | Unique identifier, system-generated |
| name | string(100) | Yes | Human-readable name |
| description | string(500) | No | Detailed description |

#### Type Fields

| Field | Type | Required | Values |
|-------|------|----------|--------|
| source_type | enum | Yes | keyword, hashtag, account, mention, community, list, trending |
| platform | enum | Yes | twitter, linkedin, reddit, discord, all |

#### Configuration Field

The `config` field is a JSON object with type-specific structure:

**Keyword config:**
```
{
  "query": string,
  "match_type": "exact_phrase" | "all_words" | "any_word",
  "exclude_terms": string[],
  "language": string,
  "min_engagement": integer,
  "verified_only": boolean,
  "media_filter": "with_media" | "without_media" | "any"
}
```

**Account config:**
```
{
  "accounts": string[],
  "include_replies": boolean,
  "include_reposts": boolean,
  "include_quotes": boolean
}
```

**Community config:**
```
{
  "communities": string[],
  "content_types": ("posts" | "comments")[],
  "sort": "hot" | "new" | "top" | "rising",
  "time_filter": "hour" | "day" | "week" | "month",
  "min_score": integer,
  "flair_filter": string[],
  "exclude_flairs": string[]
}
```

**Mention config:**
```
{
  "targets": string[],
  "target_type": "account" | "keyword",
  "include_replies_to_mentions": boolean,
  "real_time": boolean
}
```

**Hashtag config:**
```
{
  "hashtags": string[],
  "match_mode": "any" | "all",
  "min_engagement": integer,
  "exclude_hashtags": string[]
}
```

**List config:**
```
{
  "lists": string[],
  "list_type": "public" | "private" | "owned",
  "include_replies": boolean,
  "include_reposts": boolean
}
```

**Trending config:**
```
{
  "categories": string[],
  "locations": string[],
  "relevance_keywords": string[],
  "min_velocity": integer,
  "exclude_keywords": string[]
}
```

#### Behavior Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| priority | enum | medium | high, medium, low |
| weight | decimal | 1.0 | Scoring multiplier (0.5-2.0) |
| polling_interval_minutes | integer | 15 | Minutes between polls |
| enabled | boolean | true | Active or paused |
| real_time | boolean | false | Use streaming if available |

#### Capacity Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| max_results_per_poll | integer | 100 | Max posts per poll |
| daily_quota | integer | null | Max posts per day (null = unlimited) |

#### State Fields (System-Managed)

| Field | Type | Description |
|-------|------|-------------|
| last_polled_at | timestamp | Last poll attempt |
| last_successful_at | timestamp | Last successful poll |
| last_post_id | string | Most recent post ID seen |
| last_post_at | timestamp | Most recent post timestamp |
| consecutive_failures | integer | Failures since last success |
| posts_discovered_today | integer | Today's discovery count |
| posts_discovered_total | integer | Total discovery count |

#### Performance Fields (Calculated)

| Field | Type | Description |
|-------|------|-------------|
| avg_posts_per_poll | decimal | Average posts returned |
| avg_relevance_score | decimal | Average score of discoveries |
| queue_rate | decimal | % of discoveries reaching queue |
| engagement_rate | decimal | % of queued posts engaged |

## 7.1.4 Source Priority and Weighting

### Source Priority

Priority determines processing order and resource allocation:

**High Priority:**
- Processed first in each polling cycle
- More aggressive polling (shorter intervals allowed)
- Real-time triggers if available
- Gets resources during contention
- Examples: Brand mentions, VIP accounts, breaking news

**Medium Priority:**
- Standard processing order
- Regular polling intervals
- Standard resource allocation
- Examples: Core keyword searches, industry monitoring

**Low Priority:**
- Processed after higher priorities
- Longer polling intervals
- May be skipped during high load
- Examples: Exploratory searches, broad trending

**Priority allocation recommendation:**
- High: 10-20% of sources (most important)
- Medium: 60-70% of sources (core monitoring)
- Low: 10-20% of sources (exploratory)

### Source Weighting

Weight affects scoring of discovered content:

**Weight > 1.0 (1.1 - 2.0):**
Content from this source scores higher. Boosts priority.

| Scenario | Recommended Weight |
|----------|-------------------|
| Direct brand mentions | 1.5 - 2.0 |
| VIP/influencer accounts | 1.3 - 1.5 |
| High-value keyword matches | 1.2 - 1.3 |
| Core domain keywords | 1.1 - 1.2 |

**Weight = 1.0:**
Standard scoring. No adjustment.

**Weight < 1.0 (0.5 - 0.9):**
Content from this source scores lower. Deprioritizes.

| Scenario | Recommended Weight |
|----------|-------------------|
| Broad/exploratory searches | 0.8 - 0.9 |
| High-volume/noisy sources | 0.7 - 0.8 |
| Low-relevance communities | 0.6 - 0.7 |
| Trending (unless relevant) | 0.7 - 0.9 |

### Weight Application

Source weight multiplies the relevance score:

```
adjusted_relevance = base_relevance × source_weight
```

**Example:**
- Post relevance score: 70
- Source weight: 1.3 (VIP account)
- Adjusted relevance: 70 × 1.3 = 91

This allows fine-tuning of which sources contribute most to the queue.

### Combined Priority and Weight

Priority affects when/whether content is processed.
Weight affects how content scores after processing.

**High priority, high weight:**
Most important sources. Processed first, scores boosted.
Example: Brand mentions from influencers

**High priority, standard weight:**
Process quickly but don't artificially boost.
Example: All brand mentions (most are standard)

**Standard priority, high weight:**
Normal processing but boost score.
Example: VIP account monitoring

**Low priority, low weight:**
Exploratory sources. Process when capacity allows, don't boost.
Example: Broad trending monitoring

## 7.1.5 Source Combination Strategies

### Additive Sources

Most sources are additive — content matching ANY source is discovered:

```
Source A: "AI agent security" keyword
Source B: @AnthropicAI account
Source C: r/MachineLearning community
```

Result: Content matching A OR B OR C is discovered.

All sources contribute to the discovery pool. Deduplication handles overlap.

### Source Groups

Related sources can be grouped for management:

**Group structure:**
```
{
  "group_id": "grp_ai_leaders",
  "group_name": "AI Thought Leaders",
  "sources": ["src_001", "src_002", "src_003"],
  "shared_settings": {
    "priority": "medium",
    "weight": 1.2
  }
}
```

**Benefits of groups:**
- Bulk enable/disable
- Shared settings
- Collective analytics
- Organized management

**Example groups:**
- "AI Thought Leaders" — Key influencer accounts
- "Security Keywords" — All security-related keyword searches
- "Reddit Communities" — All subreddit sources
- "Competitors" — Competitor account monitoring

### Source Overlap

Multiple sources may match the same post:

**Example:**
- Post contains "AI agent security" (matches keyword source A)
- Post is from @AISecurityExpert (matches account source B)
- Post is in r/MachineLearning (matches community source C)

**Handling:**
1. Post discovered by first source
2. Subsequent sources also "match" but post already exists
3. Track all matching sources for analytics
4. Use highest weight among matching sources (optionally)

**Implementation:**
```
if post already exists:
    add source_id to post.matched_sources
    update post.weight = max(post.weight, source.weight)
else:
    create post with source_id as primary
```

### Source Conflicts

Some sources may have conflicting implications:

**Blocklist vs discovery:**
If a post matches a discovery source but author is on blocklist:
- Blocklist wins
- Post is discovered but immediately filtered
- Safety/business rules override discovery

**Competing weights:**
If post matches sources with different weights:
- Use maximum weight (reward for multiple matches)
- Or use weighted average (balance)
- Recommendation: Use maximum

### Source Dependencies

Some sources may depend on others:

**Parent-child relationship:**
```
Parent: "AI agents" broad keyword
Child: "AI agent security" specific keyword (subset)
```

**Handling:**
- No technical dependency needed
- Child will discover subset of parent's content
- Use higher weight on child for specificity
- Both contribute to discovery

## 7.1.6 Platform-Specific Source Configuration

### Twitter/X Sources

#### Available Source Types

| Source Type | API Endpoint | Rate Limit |
|-------------|--------------|------------|
| Keyword | Search Tweets | 450 req/15 min (app) |
| Hashtag | Search Tweets | 450 req/15 min (app) |
| Account | User Tweets | 1500 req/15 min (app) |
| Mention | Search Tweets | 450 req/15 min (app) |
| List | List Tweets | 900 req/15 min (app) |

#### Twitter-Specific Fields

| Field | Type | Description |
|-------|------|-------------|
| tweet_types | array | original, reply, retweet, quote |
| min_followers | integer | Minimum author followers |
| verified_only | boolean | Only verified accounts |
| has_media | boolean | Must include media |
| has_links | boolean | Must include links |
| conversation_id | string | Specific conversation |

#### Twitter Query Operators

| Operator | Example | Description |
|----------|---------|-------------|
| " " | "exact phrase" | Exact phrase match |
| OR | cat OR dog | Either term |
| - | cats -dogs | Exclude term |
| from: | from:username | From specific user |
| to: | to:username | Reply to user |
| @mention | @username | Mentioning user |
| #hashtag | #AI | Contains hashtag |
| lang: | lang:en | Language filter |
| is:retweet | is:retweet | Only retweets |
| -is:retweet | -is:retweet | Exclude retweets |
| is:reply | is:reply | Only replies |
| has:links | has:links | Contains links |
| has:media | has:media | Contains media |
| min_faves: | min_faves:10 | Minimum likes |
| min_retweets: | min_retweets:5 | Minimum RTs |

#### Twitter Example Configurations

**Comprehensive AI agent search:**
```
{
  "source_type": "keyword",
  "platform": "twitter",
  "config": {
    "query": "(\"AI agent\" OR \"AI agents\" OR \"agentic AI\" OR \"autonomous agent\") (security OR safety OR risk OR guardrails) -is:retweet lang:en",
    "match_type": "any_word",
    "exclude_terms": ["hiring", "job", "giveaway"],
    "min_engagement": 5
  },
  "priority": "high",
  "weight": 1.2,
  "polling_interval_minutes": 10
}
```

**Help-seeking search:**
```
{
  "source_type": "keyword",
  "platform": "twitter",
  "config": {
    "query": "(\"how do I\" OR \"anyone know\" OR \"need help\" OR \"looking for\") (agent OR LLM) (security OR safety OR monitor) -is:retweet lang:en",
    "match_type": "any_word"
  },
  "priority": "high",
  "weight": 1.4,
  "polling_interval_minutes": 10
}
```

---

### LinkedIn Sources

#### Available Source Types

| Source Type | API Access | Notes |
|-------------|------------|-------|
| Keyword | Limited | Requires Marketing API |
| Hashtag | Limited | Basic search |
| Account | Limited | Requires connection or API access |
| Mention | Available | For company pages you manage |

#### LinkedIn-Specific Fields

| Field | Type | Description |
|-------|------|-------------|
| content_type | enum | post, article, document, video |
| author_type | enum | person, company, group |
| connection_degree | enum | first, second, third |
| industry_filter | array | Filter by industry |

#### LinkedIn Limitations

LinkedIn API is more restrictive:
- Many endpoints require Marketing or Sales Navigator API
- Rate limits are stricter
- Some data requires authenticated user context
- May need to use LinkedIn's own search vs API

#### LinkedIn Example Configurations

**Company page mentions:**
```
{
  "source_type": "mention",
  "platform": "linkedin",
  "config": {
    "targets": ["Gen Digital"],
    "target_type": "keyword"
  },
  "priority": "high",
  "weight": 1.5,
  "polling_interval_minutes": 30
}
```

**Hashtag monitoring:**
```
{
  "source_type": "hashtag",
  "platform": "linkedin",
  "config": {
    "hashtags": ["#AIAgents", "#EnterpriseSecurity", "#AIEngineering"],
    "match_mode": "any"
  },
  "priority": "medium",
  "weight": 1.0,
  "polling_interval_minutes": 60
}
```

---

### Reddit Sources

#### Available Source Types

| Source Type | API Endpoint | Rate Limit |
|-------------|--------------|------------|
| Community | /r/{sub}/new or /hot | 60 req/min |
| Keyword | /search | 60 req/min |
| Account | /user/{name}/submitted | 60 req/min |

#### Reddit-Specific Fields

| Field | Type | Description |
|-------|------|-------------|
| subreddits | array | List of subreddits |
| sort | enum | hot, new, top, rising, controversial |
| time_filter | enum | hour, day, week, month, year, all |
| min_score | integer | Minimum upvotes |
| include_comments | boolean | Monitor comments too |
| flair_filter | array | Only certain flairs |
| nsfw | boolean | Include NSFW (default: false) |

#### Reddit Subreddit Recommendations

| Subreddit | Relevance | Volume | Notes |
|-----------|-----------|--------|-------|
| r/MachineLearning | High | High | Academic/research focus |
| r/LocalLLaMA | High | Medium | LLM practitioners |
| r/artificial | Medium | Medium | General AI discussion |
| r/LangChain | High | Medium | Agent framework users |
| r/ChatGPT | Medium | High | Consumer AI, high noise |
| r/OpenAI | Medium | Medium | OpenAI specific |
| r/singularity | Low | High | Futurism, high noise |

#### Reddit Example Configurations

**Core ML communities:**
```
{
  "source_type": "community",
  "platform": "reddit",
  "config": {
    "communities": ["MachineLearning", "LocalLLaMA", "LangChain"],
    "content_types": ["posts", "comments"],
    "sort": "new",
    "min_score": 5,
    "flair_filter": ["Discussion", "Project", "Research"]
  },
  "priority": "medium",
  "weight": 1.1,
  "polling_interval_minutes": 30
}
```

**Help-seeking in Reddit:**
```
{
  "source_type": "keyword",
  "platform": "reddit",
  "config": {
    "query": "agent security OR agent safety OR LLM guardrails",
    "subreddits": ["MachineLearning", "LocalLLaMA", "LangChain", "learnmachinelearning"],
    "time_filter": "week"
  },
  "priority": "high",
  "weight": 1.3,
  "polling_interval_minutes": 30
}
```

---

### Discord Sources

#### Available Source Types

| Source Type | Mechanism | Notes |
|-------------|-----------|-------|
| Server/Channel | Bot presence | Requires bot in server |
| Keyword alerts | Bot monitoring | Watches for keywords |

#### Discord-Specific Fields

| Field | Type | Description |
|-------|------|-------------|
| server_id | string | Discord server ID |
| channel_ids | array | Specific channels to monitor |
| keyword_triggers | array | Keywords to alert on |
| role_filter | array | Only from users with roles |
| min_message_length | integer | Minimum message length |

#### Discord Considerations

- Requires bot presence in servers
- Permission to read messages needed
- Real-time by nature
- Different engagement norms (more conversational)

#### Discord Example Configuration

**AI server monitoring:**
```
{
  "source_type": "community",
  "platform": "discord",
  "config": {
    "server_id": "123456789012345678",
    "channel_ids": ["234567890123456789", "345678901234567890"],
    "keyword_triggers": ["agent security", "help with agent", "LLM safety"],
    "min_message_length": 50
  },
  "priority": "medium",
  "weight": 1.0,
  "real_time": true
}
```

## 7.1.7 Source Management Operations

### Creating Sources

#### Creation Flow

1. **Select source type**
   - User chooses keyword, account, community, etc.
   - UI adapts to show type-specific fields

2. **Configure type-specific settings**
   - Fill in query, accounts, communities, etc.
   - Validate configuration

3. **Set behavior settings**
   - Priority, weight, polling interval
   - Enable/disable

4. **Assign to campaign**
   - Select target campaign
   - Or create as template

5. **Validate and save**
   - System validates configuration
   - Creates source record
   - Schedules first poll

#### Validation Rules

**All sources:**
- Name required, 3-100 characters
- Name unique within campaign
- source_type must be valid enum
- platform must be valid enum
- weight must be 0.5-2.0
- polling_interval must be 1-1440 (minutes)

**Keyword sources:**
- query required, non-empty
- query length < 500 characters
- match_type must be valid enum
- language must be valid ISO code

**Account sources:**
- accounts array required, non-empty
- each account must be valid handle format
- maximum 100 accounts per source

**Community sources:**
- communities array required, non-empty
- each community must be valid identifier
- sort must be valid enum if provided

**Mention sources:**
- targets array required, non-empty
- target_type required

#### Platform Validation

On creation, optionally verify with platform:
- Account exists (for account sources)
- Community exists (for community sources)
- Query syntax valid (for keyword sources)

Mark validation status:
```
{
  "platform_validation": {
    "validated": true,
    "validated_at": "2024-01-15T10:30:00Z",
    "issues": []
  }
}
```

### Editing Sources

#### Editable Fields

| Field | Editable | Notes |
|-------|----------|-------|
| name | Yes | |
| description | Yes | |
| config.* | Yes | Type-specific config |
| priority | Yes | |
| weight | Yes | |
| polling_interval | Yes | |
| enabled | Yes | |
| real_time | Yes | |
| max_results_per_poll | Yes | |
| daily_quota | Yes | |
| tags | Yes | |

#### Non-Editable Fields

| Field | Editable | Reason |
|-------|----------|--------|
| id | No | Immutable identifier |
| source_type | No | Create new source instead |
| platform | No | Create new source instead |
| campaign_id | No | Create new source instead |
| created_at | No | Historical record |
| created_by | No | Historical record |

#### Edit Effects

- Changes take effect on next poll
- No retroactive re-processing
- State (last_polled, cursor) preserved unless config changes significantly
- If query changes substantially, may want to reset state

### Deleting Sources

#### Soft Delete (Default)

```
{
  "deleted": true,
  "deleted_at": "2024-01-15T15:30:00Z",
  "deleted_by": "user_abc123"
}
```

**Effects:**
- Source stops being polled
- Source hidden from UI (unless "show deleted")
- Historical data retained
- Can be restored

#### Hard Delete

Complete removal from database.

**Effects:**
- Source record deleted
- Historical posts remain (not deleted)
- Cannot be restored
- Use for cleanup of test/invalid sources

#### Deletion Confirmation

Before deleting, show:
- Source details
- Posts discovered count
- "Are you sure?" confirmation

### Enable/Disable Toggle

**Disable:**
- Source stops being polled immediately
- State is preserved
- Can re-enable anytime
- Quick way to pause without deleting

**Enable:**
- Source resumes polling on next cycle
- Picks up from last state (since_id)
- No backfill of missed time

### Bulk Operations

#### Bulk Enable/Disable

```
POST /sources/bulk
{
  "action": "disable",
  "source_ids": ["src_001", "src_002", "src_003"]
}
```

#### Bulk Delete

```
POST /sources/bulk
{
  "action": "delete",
  "source_ids": ["src_001", "src_002", "src_003"],
  "hard": false
}
```

#### Bulk Update

```
POST /sources/bulk
{
  "action": "update",
  "source_ids": ["src_001", "src_002", "src_003"],
  "updates": {
    "priority": "high",
    "weight": 1.2
  }
}
```

#### Bulk Tag

```
POST /sources/bulk
{
  "action": "add_tags",
  "source_ids": ["src_001", "src_002", "src_003"],
  "tags": ["priority", "q1-campaign"]
}
```

### Import/Export

#### Export Sources

```
GET /campaigns/{campaign_id}/sources/export
```

Returns JSON or CSV with all source configurations:
```
{
  "exported_at": "2024-01-15T10:30:00Z",
  "campaign_id": "camp_xyz",
  "sources": [
    { ... source 1 ... },
    { ... source 2 ... }
  ]
}
```

#### Import Sources

```
POST /campaigns/{campaign_id}/sources/import
{
  "sources": [ ... ],
  "mode": "add" | "replace",
  "validate_only": false
}
```

**Import modes:**
- add: Add to existing sources
- replace: Replace all sources

**Validation:**
- Validate before importing
- Report any invalid sources
- Option to import valid only

## 7.1.8 Source Templates

### What Templates Are

Templates are pre-configured source sets for common use cases. They provide quick-start configurations.

### Template Structure

```
{
  "template_id": "tmpl_ai_agent_monitoring",
  "name": "AI Agent Monitoring",
  "description": "Comprehensive monitoring for AI agent discussions",
  "category": "industry",
  "platforms": ["twitter", "reddit"],
  "sources": [
    {
      "name": "AI Agent Keywords",
      "source_type": "keyword",
      "platform": "twitter",
      "config": { ... },
      "priority": "high",
      "weight": 1.2
    },
    {
      "name": "ML Subreddits",
      "source_type": "community",
      "platform": "reddit",
      "config": { ... },
      "priority": "medium",
      "weight": 1.0
    }
  ],
  "estimated_volume": "500-2000 posts/day",
  "recommended_for": ["thought_leadership", "brand_awareness"]
}
```

### Standard Templates

#### Template: AI/ML Broad Monitoring

**Purpose:** Monitor general AI and machine learning discussions across platforms.

**Sources included:**
1. Keyword: AI/ML general terms (Twitter)
2. Keyword: LLM terms (Twitter)
3. Hashtags: #AI, #MachineLearning, #LLM (Twitter)
4. Communities: r/MachineLearning, r/artificial (Reddit)
5. Accounts: Top 20 AI researchers (Twitter)

**Expected volume:** 2,000-10,000 posts/day
**Recommended for:** Brand awareness, thought leadership

---

#### Template: AI Agent Security Focus

**Purpose:** Focused monitoring on AI agent security and safety topics.

**Sources included:**
1. Keyword: "AI agent security" variations (Twitter)
2. Keyword: "agent safety" and "guardrails" (Twitter)
3. Keyword: Help-seeking agent security (Twitter)
4. Communities: r/LocalLLaMA, r/LangChain (Reddit)
5. Hashtags: #AIAgents, #LLMSecurity (Twitter)
6. Accounts: AI safety researchers (Twitter)

**Expected volume:** 200-1,000 posts/day
**Recommended for:** Conversions, thought leadership

---

#### Template: Brand Monitoring

**Purpose:** Monitor mentions of your brand, products, and key personnel.

**Sources included:**
1. Mention: @YourBrand (all platforms)
2. Keyword: "Your Brand Name" variations (all platforms)
3. Keyword: Product names (all platforms)
4. Accounts: Company executives (Twitter)

**Expected volume:** 10-500 posts/day (varies by brand)
**Recommended for:** All goals

---

#### Template: Competitor Monitoring

**Purpose:** Monitor competitor activity and mentions.

**Sources included:**
1. Accounts: Competitor company accounts
2. Keyword: Competitor brand names
3. Keyword: Competitor product names
4. Keyword: Competitor vs comparison queries

**Expected volume:** 50-500 posts/day
**Recommended for:** Conversions, thought leadership

---

#### Template: Help-Seeking Detection

**Purpose:** Find users seeking help with problems you can solve.

**Sources included:**
1. Keyword: Question patterns + domain terms (Twitter)
2. Keyword: Frustration patterns + domain terms (Twitter)
3. Keyword: Recommendation requests (Twitter)
4. Communities: Q&A focused subreddits (Reddit)

**Expected volume:** 100-500 posts/day
**Recommended for:** Conversions

### Using Templates

#### Apply Template Flow

1. **Select template**
   - Browse template library
   - Filter by category, platform, goal

2. **Preview sources**
   - See what will be created
   - Estimated volume

3. **Customize (optional)**
   - Add/remove sources
   - Adjust weights/priorities
   - Modify queries

4. **Apply to campaign**
   - Creates sources in campaign
   - Sources start polling

#### Template as Starting Point

Templates create actual sources. After applying:
- Sources can be individually edited
- Sources can be deleted
- No ongoing link to template

### Custom Templates

#### Create Custom Template

Users can save their source configuration as a template:

```
POST /templates
{
  "name": "My Custom Template",
  "description": "...",
  "source_ids": ["src_001", "src_002", "src_003"]
}
```

#### Share Templates

Templates can be:
- Private (user only)
- Team (organization)
- Public (all users) — admin only

## 7.1.9 Source Performance Tracking

### Per-Source Metrics

Track for each source, per time period:

**Discovery metrics:**
| Metric | Description | Update Frequency |
|--------|-------------|------------------|
| posts_discovered | Count of posts found | Per poll |
| posts_new | Count of new (non-duplicate) | Per poll |
| posts_filtered | Count passing filters | Per poll |
| posts_queued | Count reaching queue | Per poll |
| posts_engaged | Count actually engaged | Async |

**Quality metrics:**
| Metric | Description | Update Frequency |
|--------|-------------|------------------|
| avg_relevance_score | Average relevance | Hourly |
| avg_opportunity_score | Average opportunity | Hourly |
| avg_priority_score | Average priority | Hourly |
| score_distribution | Histogram of scores | Daily |

**Efficiency metrics:**
| Metric | Description | Update Frequency |
|--------|-------------|------------------|
| api_calls | Number of API calls | Per poll |
| api_cost | Cost if applicable | Per poll |
| yield_rate | Posts per API call | Per poll |
| filter_rate | % filtered out | Hourly |

**Outcome metrics:**
| Metric | Description | Update Frequency |
|--------|-------------|------------------|
| engagement_rate | % of queued that engaged | Daily |
| avg_engagement | Likes/replies on engaged | Daily |
| conversion_rate | % leading to conversion | Daily |

### Performance Calculations

**Queue rate:**
```
queue_rate = posts_queued / posts_discovered
```
Good: > 5%. Below 1% = too noisy.

**Engagement rate:**
```
engagement_rate = posts_engaged / posts_queued
```
Good: > 20%. Below 5% = queue quality issue.

**Value score:**
```
value_score = (posts_engaged × avg_engagement) / api_calls
```
Higher = more efficient source.

### Performance Storage

**Table: source_metrics_daily**

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Unique identifier |
| source_id | UUID | Source reference |
| date | DATE | The day |
| posts_discovered | INTEGER | Count discovered |
| posts_new | INTEGER | Non-duplicates |
| posts_filtered | INTEGER | Passed filters |
| posts_queued | INTEGER | Reached queue |
| posts_engaged | INTEGER | Engaged with |
| avg_relevance | DECIMAL | Average relevance |
| avg_opportunity | DECIMAL | Average opportunity |
| api_calls | INTEGER | API calls made |
| errors | INTEGER | Error count |

### Performance Dashboard

#### Source List with Performance

```
┌────────────────────────────────────────────────────────────────────────────────────┐
│ SOURCES                                                         [+ Add Source]    │
│                                                                                    │
│ Filter: [All Types ▼] [All Platforms ▼] [Enabled ▼]  Search: [____________]       │
│                                                                                    │
│ ┌────────┬─────────────────────┬──────────┬──────────┬─────────┬─────────┬───────┐│
│ │ Status │ Name                │ Type     │ Platform │Vol (24h)│Avg Score│ Queue%││
│ ├────────┼─────────────────────┼──────────┼──────────┼─────────┼─────────┼───────┤│
│ │ ● On   │ AI Agent Security   │ Keyword  │ Twitter  │  234    │   67    │  12%  ││
│ │ ● On   │ Thought Leaders     │ Account  │ Twitter  │   45    │   72    │  28%  ││
│ │ ● On   │ ML Subreddits       │Community │ Reddit   │  156    │   58    │   8%  ││
│ │ ○ Off  │ Broad AI Trending   │ Trending │ Twitter  │   --    │   --    │  --   ││
│ │ ● On   │ Brand Mentions      │ Mention  │ All      │   12    │   85    │  67%  ││
│ │ ⚠ Err  │ Competitor Watch    │ Account  │ Twitter  │    0    │   --    │  --   ││
│ └────────┴─────────────────────┴──────────┴──────────┴─────────┴─────────┴───────┘│
│                                                                                    │
│ Showing 6 of 6 sources                                              [Export CSV]  │
└────────────────────────────────────────────────────────────────────────────────────┘
```

#### Source Detail Performance

```
┌────────────────────────────────────────────────────────────────────────────────────┐
│ SOURCE: AI Agent Security Keywords                                                 │
│                                                                                    │
│ ┌─────────────────────────────────────────────────────────────────────────────────┐│
│ │ VOLUME (Last 7 Days)                                                            ││
│ │                                                                                 ││
│ │   400 ┤    ▄                                                                    ││
│ │   300 ┤  ▄ █ ▄       ▄                                                          ││
│ │   200 ┤▄ █ █ █ ▄   ▄ █                                                          ││
│ │   100 ┤█ █ █ █ █ ▄ █ █                                                          ││
│ │     0 ┴─┴─┴─┴─┴─┴─┴─┴─                                                          ││
│ │       M  T  W  Th F  Sa Su                                                      ││
│ └─────────────────────────────────────────────────────────────────────────────────┘│
│                                                                                    │
│ ┌──────────────────────────────┐  ┌──────────────────────────────┐                │
│ │ DISCOVERY FUNNEL             │  │ SCORE DISTRIBUTION           │                │
│ │                              │  │                              │                │
│ │ Discovered:  1,642 (100%)    │  │   0-20:  ████ 15%            │                │
│ │ New:         1,580 (96%)     │  │  20-40:  ██████ 23%          │                │
│ │ Passed:        423 (26%)     │  │  40-60:  ████████ 32%        │                │
│ │ Queued:         87 (5%)      │  │  60-80:  █████ 21%           │                │
│ │ Engaged:        34 (2%)      │  │  80-100: ██ 9%               │                │
│ │                              │  │                              │                │
│ └──────────────────────────────┘  └──────────────────────────────┘                │
│                                                                                    │
│ ┌─────────────────────────────────────────────────────────────────────────────────┐│
│ │ KEY METRICS                                                                     ││
│ │                                                                                 ││
│ │ Avg Relevance:    67.2       Avg Opportunity:   58.4       Avg Priority:  71.3 ││
│ │ Queue Rate:       5.3%       Engagement Rate:   39.1%      API Calls/day:  144 ││
│ │ Posts/API Call:   11.4       Errors (24h):      0          Last Poll:     2m   ││
│ │                                                                                 ││
│ └─────────────────────────────────────────────────────────────────────────────────┘│
└────────────────────────────────────────────────────────────────────────────────────┘
```

### Performance Alerts

#### Low Performance Alerts

**No results alert:**
```
⚠️ Source "AI Safety Keywords" has returned no results in 24 hours.
   Last successful: 2024-01-14 10:30 AM
   Possible causes: Query too narrow, API issue, rate limiting
   [Check Source] [Disable Source]
```

**Low quality alert:**
```
⚠️ Source "Broad AI Trending" has average score of 23 (threshold: 40).
   This source is generating noise. Consider:
   - Adding exclude terms
   - Narrowing the query
   - Reducing weight
   [Edit Source] [Reduce Weight] [Disable]
```

**High volume, low yield:**
```
ℹ️ Source "General ML" discovers 500+ posts/day but <1% reach queue.
   This may be wasting API quota. Consider:
   - More specific keywords
   - Higher min_engagement
   - Disabling if not valuable
   [Edit Source] [Analyze Posts]
```

#### Error Alerts

**API errors:**
```
🔴 Source "Competitor Watch" has failed 5 consecutive polls.
   Error: 401 Unauthorized
   Action needed: Re-authenticate or check API access
   [Re-authenticate] [View Logs] [Disable]
```

**Rate limiting:**
```
⚠️ Platform Twitter is hitting rate limits.
   Sources affected: 5
   Recommendation: Increase polling intervals or reduce sources
   [View Affected] [Auto-Adjust]
```

### Optimization Suggestions

Based on performance, suggest improvements:

**For low queue rate (<2%):**
"Add exclude terms: 'hiring', 'job', 'course'"
"Increase min_engagement to 10"
"Consider more specific keywords"

**For high volume:**
"Source is discovering 5,000+ posts/day. Consider splitting into focused sources."

**For low engagement rate:**
"Posts from this source aren't being engaged. Review relevance or adjust weight."

**For efficient sources:**
"This source has excellent queue rate (15%). Consider increasing weight to 1.3."

## 7.1.10 Source Configuration UI

### Source List View

Full source management interface:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ SOURCES                                                                                │
│                                                                                        │
│ Campaign: Product Launch Q1 2024 ▼                              [+ Add Source]        │
│                                                                                        │
│ ┌───────────────────────────────────────────────────────────────────────────────────┐ │
│ │ Filters:                                                                          │ │
│ │ Type: [All ▼]  Platform: [All ▼]  Status: [All ▼]  Priority: [All ▼]             │ │
│ │ Search: [_________________________________]                                       │ │
│ └───────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                        │
│ ┌────┬────────┬───────────────────────┬──────────┬──────────┬────────┬────────┬──────┐│
│ │ □  │ Status │ Name                  │ Type     │ Platform │Vol(24h)│Score   │Actions│
│ ├────┼────────┼───────────────────────┼──────────┼──────────┼────────┼────────┼──────┤│
│ │ □  │ ● On   │ AI Agent Security     │ Keyword  │ Twitter  │  234   │ 67 avg │ ⋮    ││
│ │ □  │ ● On   │ Help Seeking          │ Keyword  │ Twitter  │   89   │ 78 avg │ ⋮    ││
│ │ □  │ ● On   │ Thought Leaders       │ Account  │ Twitter  │   45   │ 72 avg │ ⋮    ││
│ │ □  │ ● On   │ ML Subreddits         │Community │ Reddit   │  156   │ 58 avg │ ⋮    ││
│ │ □  │ ● On   │ Brand Mentions        │ Mention  │ All      │   12   │ 85 avg │ ⋮    ││
│ │ □  │ ○ Off  │ Broad AI Trending     │ Trending │ Twitter  │   --   │ -- avg │ ⋮    ││
│ │ □  │ ⚠ Err  │ Competitor Watch      │ Account  │ Twitter  │    0   │ -- avg │ ⋮    ││
│ └────┴────────┴───────────────────────┴──────────┴──────────┴────────┴────────┴──────┘│
│                                                                                        │
│ With selected: [Enable] [Disable] [Delete] [Change Priority ▼]                        │
│                                                                                        │
│ ──────────────────────────────────────────────────────────────────────────────────────│
│                                                                                        │
│ [Apply Template ▼]  [Import Sources]  [Export Sources]        Showing 7 of 7 sources │
│                                                                                        │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

### Add Source Flow

#### Step 1: Select Type

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ ADD SOURCE                                                              [Cancel]      │
│                                                                                        │
│ What type of content do you want to monitor?                                          │
│                                                                                        │
│ ┌──────────────────────┐  ┌──────────────────────┐  ┌──────────────────────┐          │
│ │                      │  │                      │  │                      │          │
│ │   🔍 KEYWORD         │  │   # HASHTAG          │  │   👤 ACCOUNT         │          │
│ │                      │  │                      │  │                      │          │
│ │   Search for posts   │  │   Monitor posts      │  │   Follow specific    │          │
│ │   containing         │  │   with certain       │  │   accounts           │          │
│ │   specific terms     │  │   hashtags           │  │                      │          │
│ │                      │  │                      │  │                      │          │
│ │   [Select]           │  │   [Select]           │  │   [Select]           │          │
│ └──────────────────────┘  └──────────────────────┘  └──────────────────────┘          │
│                                                                                        │
│ ┌──────────────────────┐  ┌──────────────────────┐  ┌──────────────────────┐          │
│ │                      │  │                      │  │                      │          │
│ │   @ MENTION          │  │   👥 COMMUNITY       │  │   📋 LIST            │          │
│ │                      │  │                      │  │                      │          │
│ │   Track when you     │  │   Monitor specific   │  │   Monitor a curated  │          │
│ │   or keywords are    │  │   communities        │  │   list of accounts   │          │
│ │   mentioned          │  │   (subreddits, etc)  │  │                      │          │
│ │                      │  │                      │  │                      │          │
│ │   [Select]           │  │   [Select]           │  │   [Select]           │          │
│ └──────────────────────┘  └──────────────────────┘  └──────────────────────┘          │
│                                                                                        │
│ ┌──────────────────────┐                                                              │
│ │                      │                                                              │
│ │   📈 TRENDING        │                                                              │
│ │                      │                                                              │
│ │   Monitor trending   │                                                              │
│ │   topics in your     │                                                              │
│ │   domain             │                                                              │
│ │                      │                                                              │
│ │   [Select]           │                                                              │
│ └──────────────────────┘                                                              │
│                                                                                        │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

#### Step 2: Configure (Keyword Example)

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ ADD KEYWORD SOURCE                                               [Back] [Cancel]      │
│                                                                                        │
│ ─────────────────────────────────────────────────────────────────────────────────────  │
│ BASIC CONFIGURATION                                                                    │
│ ─────────────────────────────────────────────────────────────────────────────────────  │
│                                                                                        │
│ Source Name *                                                                          │
│ ┌────────────────────────────────────────────────────────────────────────────────────┐│
│ │ AI Agent Security Keywords                                                         ││
│ └────────────────────────────────────────────────────────────────────────────────────┘│
│                                                                                        │
│ Platform *                                                                             │
│ ┌─────────────────────────────┐                                                       │
│ │ Twitter ▼                   │                                                       │
│ └─────────────────────────────┘                                                       │
│                                                                                        │
│ ─────────────────────────────────────────────────────────────────────────────────────  │
│ SEARCH QUERY                                                                           │
│ ─────────────────────────────────────────────────────────────────────────────────────  │
│                                                                                        │
│ Search Terms *                                                                         │
│ ┌────────────────────────────────────────────────────────────────────────────────────┐│
│ │ "AI agent security" OR "agent safety" OR "LLM guardrails" OR "agent monitoring"   ││
│ │                                                                                    ││
│ └────────────────────────────────────────────────────────────────────────────────────┘│
│ Tip: Use "quotes" for exact phrases, OR between alternatives, -minus to exclude       │
│                                                                                        │
│ Match Type                                                                             │
│ ○ Exact phrase        ● Any of these terms        ○ All of these terms               │
│                                                                                        │
│ Exclude Terms (comma-separated)                                                        │
│ ┌────────────────────────────────────────────────────────────────────────────────────┐│
│ │ hiring, job, career, course, tutorial, affiliate, giveaway                         ││
│ └────────────────────────────────────────────────────────────────────────────────────┘│
│                                                                                        │
│ Language                                     Minimum Engagement                        │
│ ┌─────────────────────┐                      ┌────────────────┐                       │
│ │ English ▼           │                      │ 5              │ likes                 │
│ └─────────────────────┘                      └────────────────┘                       │
│                                                                                        │
│ [Advanced Options ▼]                                                                   │
│                                                                                        │
│                                                                  [Next: Behavior →]   │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

#### Step 3: Behavior Settings

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ ADD KEYWORD SOURCE                                               [Back] [Cancel]      │
│                                                                                        │
│ ─────────────────────────────────────────────────────────────────────────────────────  │
│ BEHAVIOR SETTINGS                                                                      │
│ ─────────────────────────────────────────────────────────────────────────────────────  │
│                                                                                        │
│ Priority                                                                               │
│ ● High (process first, more frequent polling)                                         │
│ ○ Medium (standard processing)                                                        │
│ ○ Low (process when capacity allows)                                                  │
│                                                                                        │
│ Weight                                                                                 │
│ ┌────────────────────────────────────────────────────────────────────────────────────┐│
│ │ Lower                                                               Higher         ││
│ │ 0.5 ─────────────────────────●───────────────────────────────────── 2.0           ││
│ │                              1.2                                                   ││
│ │                                                                                    ││
│ │ Content from this source will score 20% higher than standard.                      ││
│ └────────────────────────────────────────────────────────────────────────────────────┘│
│                                                                                        │
│ Polling Interval                                                                       │
│ ┌────────────────┐                                                                    │
│ │ 10             │ minutes                                                            │
│ └────────────────┘                                                                    │
│ Recommended: 10-15 min for high priority, 30-60 min for low priority                  │
│                                                                                        │
│ ─────────────────────────────────────────────────────────────────────────────────────  │
│ LIMITS                                                                                 │
│ ─────────────────────────────────────────────────────────────────────────────────────  │
│                                                                                        │
│ Max results per poll                       Daily quota                                 │
│ ┌────────────────┐                         ┌────────────────┐                         │
│ │ 100            │                         │ Unlimited      │ ▼                       │
│ └────────────────┘                         └────────────────┘                         │
│                                                                                        │
│ □ Enable real-time streaming (if available)                                           │
│                                                                                        │
│                                                                  [Create Source]       │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

### Source Detail/Edit View

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ SOURCE: AI Agent Security Keywords                              [Enabled ●] [Delete]  │
│                                                                                        │
│ ─────────────────────────────────────────────────────────────────────────────────────  │
│ CONFIGURATION                                                     [Edit Configuration]│
│ ─────────────────────────────────────────────────────────────────────────────────────  │
│                                                                                        │
│ Type:      Keyword Search                                                              │
│ Platform:  Twitter                                                                     │
│                                                                                        │
│ Query:     "AI agent security" OR "agent safety" OR "LLM guardrails"                  │
│ Match:     Any of these terms                                                          │
│ Exclude:   hiring, job, course                                                         │
│ Language:  English                                                                     │
│ Min Likes: 5                                                                           │
│                                                                                        │
│ ─────────────────────────────────────────────────────────────────────────────────────  │
│ BEHAVIOR                                                            [Edit Behavior]   │
│ ─────────────────────────────────────────────────────────────────────────────────────  │
│                                                                                        │
│ Priority: High      Weight: 1.2      Polling: Every 10 minutes                        │
│ Max/poll: 100       Daily quota: Unlimited                                            │
│                                                                                        │
│ ─────────────────────────────────────────────────────────────────────────────────────  │
│ STATUS                                                                                 │
│ ─────────────────────────────────────────────────────────────────────────────────────  │
│                                                                                        │
│ Last polled:    2 minutes ago (14:28:32)                                              │
│ Last success:   2 minutes ago (14:28:32)                                              │
│ Next poll:      in 8 minutes (14:38:00)                                               │
│ Consecutive errors: 0                                                                  │
│                                                                                        │
│ ─────────────────────────────────────────────────────────────────────────────────────  │
│ PERFORMANCE (Last 7 Days)                                                              │
│ ─────────────────────────────────────────────────────────────────────────────────────  │
│                                                                                        │
│ ┌──────────────────────────────────────┐ ┌──────────────────────────────────────┐     │
│ │ DISCOVERY FUNNEL                     │ │ DAILY VOLUME                         │     │
│ │                                      │ │                                      │     │
│ │ Discovered:  1,642                   │ │   300 ┤  ▄                           │     │
│ │ New:         1,580 (96%)             │ │   200 ┤▄ █ ▄   ▄ ▄                   │     │
│ │ Passed:        423 (26%)             │ │   100 ┤█ █ █ ▄ █ █                   │     │
│ │ Queued:         87 (5%)              │ │     0 ┴─┴─┴─┴─┴─┴─                   │     │
│ │ Engaged:        34 (2%)              │ │       M T W T F S S                  │     │
│ │                                      │ │                                      │     │
│ └──────────────────────────────────────┘ └──────────────────────────────────────┘     │
│                                                                                        │
│ Avg Relevance: 67.2    Avg Opportunity: 58.4    Queue Rate: 5.3%                      │
│                                                                                        │
│ ─────────────────────────────────────────────────────────────────────────────────────  │
│ RECENT DISCOVERIES                                               [View All]           │
│ ─────────────────────────────────────────────────────────────────────────────────────  │
│                                                                                        │
│ @airesearcher · 25m                                              Score: 78 → Queued  │
│ "Working on agent guardrails for our production system..."                           │
│                                                                                        │
│ @devops_jane · 1h                                                Score: 45 → Filtered │
│ "AI agent security is going to be huge in 2024"                  (below threshold)   │
│                                                                                        │
│ @securitypro · 2h                                                Score: 82 → Queued  │
│ "How do you handle prompt injection in your AI agents?"                              │
│                                                                                        │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

## 7.1.11 Source Database Schema

### Sources Table

**Table: sources**

```sql
CREATE TABLE sources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Identity
    name VARCHAR(100) NOT NULL,
    description TEXT,
    
    -- Type and Platform
    source_type VARCHAR(50) NOT NULL,
    platform VARCHAR(50) NOT NULL,
    
    -- Configuration
    config JSONB NOT NULL,
    
    -- Behavior
    priority VARCHAR(20) NOT NULL DEFAULT 'medium',
    weight DECIMAL(3,2) NOT NULL DEFAULT 1.00,
    polling_interval_minutes INTEGER NOT NULL DEFAULT 15,
    enabled BOOLEAN NOT NULL DEFAULT true,
    real_time BOOLEAN NOT NULL DEFAULT false,
    max_results_per_poll INTEGER DEFAULT 100,
    daily_quota INTEGER,
    
    -- Campaign Assignment
    campaign_id UUID NOT NULL REFERENCES campaigns(id),
    
    -- Metadata
    tags TEXT[],
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    created_by UUID REFERENCES users(id),
    
    -- Soft Delete
    deleted_at TIMESTAMP WITH TIME ZONE,
    deleted_by UUID REFERENCES users(id),
    
    -- Constraints
    CONSTRAINT sources_name_campaign_unique UNIQUE (name, campaign_id),
    CONSTRAINT sources_weight_range CHECK (weight >= 0.5 AND weight <= 2.0),
    CONSTRAINT sources_polling_range CHECK (polling_interval_minutes >= 1 AND polling_interval_minutes <= 1440),
    CONSTRAINT sources_type_valid CHECK (source_type IN ('keyword', 'hashtag', 'account', 'mention', 'community', 'list', 'trending')),
    CONSTRAINT sources_platform_valid CHECK (platform IN ('twitter', 'linkedin', 'reddit', 'discord', 'all')),
    CONSTRAINT sources_priority_valid CHECK (priority IN ('high', 'medium', 'low'))
);
```

### Source State Table

**Table: source_state**

```sql
CREATE TABLE source_state (
    source_id UUID PRIMARY KEY REFERENCES sources(id),
    
    -- Polling State
    last_polled_at TIMESTAMP WITH TIME ZONE,
    last_successful_at TIMESTAMP WITH TIME ZONE,
    next_poll_at TIMESTAMP WITH TIME ZONE,
    
    -- Pagination State
    last_post_id VARCHAR(255),
    last_post_at TIMESTAMP WITH TIME ZONE,
    pagination_cursor TEXT,
    
    -- Error Tracking
    consecutive_failures INTEGER NOT NULL DEFAULT 0,
    last_error TEXT,
    last_error_at TIMESTAMP WITH TIME ZONE,
    
    -- Counters
    posts_discovered_today INTEGER NOT NULL DEFAULT 0,
    posts_discovered_total BIGINT NOT NULL DEFAULT 0,
    today_date DATE NOT NULL DEFAULT CURRENT_DATE,
    
    -- Updated
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
```

### Source Metrics Table

**Table: source_metrics_daily**

```sql
CREATE TABLE source_metrics_daily (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id UUID NOT NULL REFERENCES sources(id),
    date DATE NOT NULL,
    
    -- Discovery Counts
    posts_discovered INTEGER NOT NULL DEFAULT 0,
    posts_new INTEGER NOT NULL DEFAULT 0,
    posts_filtered INTEGER NOT NULL DEFAULT 0,
    posts_queued INTEGER NOT NULL DEFAULT 0,
    posts_engaged INTEGER NOT NULL DEFAULT 0,
    
    -- Scores
    avg_relevance_score DECIMAL(5,2),
    avg_opportunity_score DECIMAL(5,2),
    avg_priority_score DECIMAL(5,2),
    
    -- API Usage
    api_calls INTEGER NOT NULL DEFAULT 0,
    api_errors INTEGER NOT NULL DEFAULT 0,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    CONSTRAINT source_metrics_daily_unique UNIQUE (source_id, date)
);
```

### Source Groups Table

**Table: source_groups**

```sql
CREATE TABLE source_groups (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id UUID NOT NULL REFERENCES campaigns(id),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    
    -- Shared Settings
    shared_priority VARCHAR(20),
    shared_weight DECIMAL(3,2),
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    CONSTRAINT source_groups_name_unique UNIQUE (name, campaign_id)
);

CREATE TABLE source_group_members (
    group_id UUID NOT NULL REFERENCES source_groups(id),
    source_id UUID NOT NULL REFERENCES sources(id),
    added_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    PRIMARY KEY (group_id, source_id)
);
```

### Indexes

```sql
-- Sources
CREATE INDEX idx_sources_campaign ON sources(campaign_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_sources_enabled ON sources(enabled) WHERE deleted_at IS NULL;
CREATE INDEX idx_sources_platform ON sources(platform) WHERE deleted_at IS NULL;
CREATE INDEX idx_sources_type ON sources(source_type) WHERE deleted_at IS NULL;
CREATE INDEX idx_sources_priority ON sources(priority) WHERE deleted_at IS NULL;

-- Source State
CREATE INDEX idx_source_state_next_poll ON source_state(next_poll_at);
CREATE INDEX idx_source_state_failures ON source_state(consecutive_failures) WHERE consecutive_failures > 0;

-- Source Metrics
CREATE INDEX idx_source_metrics_source_date ON source_metrics_daily(source_id, date DESC);
CREATE INDEX idx_source_metrics_date ON source_metrics_daily(date);
```

## 7.1.12 Source API Endpoints

### List Sources

**GET /api/v1/campaigns/{campaign_id}/sources**

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| platform | string | Filter by platform |
| source_type | string | Filter by type |
| enabled | boolean | Filter by enabled status |
| priority | string | Filter by priority |
| search | string | Search in name/description |
| page | integer | Page number (default: 1) |
| per_page | integer | Items per page (default: 20, max: 100) |
| sort | string | Sort field (name, created_at, volume) |
| order | string | Sort order (asc, desc) |

**Response:**
```json
{
  "data": [
    {
      "id": "src_001",
      "name": "AI Agent Security",
      "source_type": "keyword",
      "platform": "twitter",
      "config": { ... },
      "priority": "high",
      "weight": 1.2,
      "enabled": true,
      "performance": {
        "volume_24h": 234,
        "avg_score": 67.2,
        "queue_rate": 0.053
      },
      "state": {
        "last_polled_at": "2024-01-15T14:20:00Z",
        "consecutive_failures": 0
      }
    }
  ],
  "meta": {
    "total": 15,
    "page": 1,
    "per_page": 20,
    "total_pages": 1
  }
}
```

### Get Source

**GET /api/v1/sources/{source_id}**

**Response:**
Full source object with state and performance metrics.

### Create Source

**POST /api/v1/campaigns/{campaign_id}/sources**

**Request Body:**
```json
{
  "name": "AI Agent Security Keywords",
  "description": "Core keyword search for agent security",
  "source_type": "keyword",
  "platform": "twitter",
  "config": {
    "query": "\"AI agent security\" OR \"agent safety\"",
    "match_type": "any_word",
    "exclude_terms": ["hiring", "job"],
    "language": "en",
    "min_engagement": 5
  },
  "priority": "high",
  "weight": 1.2,
  "polling_interval_minutes": 10,
  "enabled": true,
  "tags": ["core", "security"]
}
```

**Response:** Created source object (201)

**Errors:**
- 400: Validation error (invalid config, etc.)
- 409: Name already exists in campaign

### Update Source

**PUT /api/v1/sources/{source_id}**

**Request Body:** Partial source object (fields to update)

**Response:** Updated source object

### Delete Source

**DELETE /api/v1/sources/{source_id}**

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| hard | boolean | Hard delete (default: false) |

**Response:** 204 No Content

### Toggle Source

**POST /api/v1/sources/{source_id}/toggle**

**Request Body:**
```json
{
  "enabled": false
}
```

**Response:** Updated source object

### Test Source

**POST /api/v1/sources/{source_id}/test**

Executes a test poll and returns results without storing.

**Response:**
```json
{
  "success": true,
  "posts_found": 23,
  "sample_posts": [ ... ],
  "api_calls": 1,
  "duration_ms": 342
}
```

### Bulk Operations

**POST /api/v1/campaigns/{campaign_id}/sources/bulk**

**Request Body:**
```json
{
  "action": "disable",
  "source_ids": ["src_001", "src_002"],
  "params": {}
}
```

**Actions:** enable, disable, delete, update_priority, update_weight, add_tags

**Response:**
```json
{
  "affected": 2,
  "results": [
    { "source_id": "src_001", "success": true },
    { "source_id": "src_002", "success": true }
  ]
}
```

### Source Metrics

**GET /api/v1/sources/{source_id}/metrics**

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| period | string | day, week, month (default: week) |
| start_date | date | Start of period |
| end_date | date | End of period |

**Response:**
```json
{
  "source_id": "src_001",
  "period": {
    "start": "2024-01-08",
    "end": "2024-01-15"
  },
  "totals": {
    "posts_discovered": 1642,
    "posts_queued": 87,
    "posts_engaged": 34
  },
  "averages": {
    "relevance_score": 67.2,
    "opportunity_score": 58.4,
    "queue_rate": 0.053
  },
  "daily": [
    { "date": "2024-01-08", "discovered": 245, ... },
    { "date": "2024-01-09", "discovered": 198, ... }
  ]
}
```

## 7.1.13 Implementation Guidance for Neoclaw

### Implementation Order

1. **Define source type schemas**
   - Create JSON schema for each source type's config
   - Build validation logic for each type
   - Test with valid and invalid configs

2. **Build source CRUD operations**
   - Create source table and model
   - Implement create with validation
   - Implement read (single and list)
   - Implement update with partial updates
   - Implement soft delete

3. **Implement source state tracking**
   - Create state table
   - Build state update logic
   - Handle state reset scenarios

4. **Build source management UI**
   - Source list with filters
   - Add source flow (type selection → config → behavior)
   - Source detail view
   - Edit and delete operations

5. **Add source templates**
   - Define standard templates
   - Build template application logic
   - Template browsing UI

6. **Implement source performance tracking**
   - Metrics table and collection
   - Performance calculations
   - Performance displays in UI

7. **Add bulk operations**
   - Bulk enable/disable
   - Bulk delete
   - Import/export

8. **Build source testing**
   - Test source endpoint
   - Preview results before saving

### Validation Checklist

**All sources:**
- [ ] Name: required, 3-100 chars, unique in campaign
- [ ] source_type: valid enum
- [ ] platform: valid enum
- [ ] config: valid JSON matching type schema
- [ ] priority: valid enum
- [ ] weight: 0.5-2.0
- [ ] polling_interval: 1-1440

**Keyword sources:**
- [ ] query: required, non-empty, <500 chars
- [ ] match_type: valid enum
- [ ] language: valid ISO code if provided

**Account sources:**
- [ ] accounts: required, non-empty array
- [ ] each account: valid handle format
- [ ] max 100 accounts

**Community sources:**
- [ ] communities: required, non-empty array
- [ ] sort: valid enum if provided
- [ ] time_filter: valid enum if provided

### Testing Requirements

**Unit tests:**
- Config validation for each source type
- Source CRUD operations
- State management

**Integration tests:**
- Source creation flow
- Source update and delete
- Bulk operations
- Performance metric collection

**API tests:**
- All endpoints with valid data
- Validation error responses
- Authorization checks

### Common Pitfalls

**Query syntax errors:**
Platform query syntax varies. Validate syntax per platform.

**Account handle formats:**
Handles may or may not include @. Normalize consistently.

**Rate limit unawareness:**
Too many sources = rate limit issues. Warn users.

**State corruption:**
If pagination cursor expires, handle gracefully.

**Metric accuracy:**
Ensure metrics update atomically. Don't double-count.

---

**END OF SECTION 7.1**

Section 7.2 continues with Feed Ingestion specification.
-e 


# SECTION 7.2: FEED INGESTION

## 7.2.1 What Feed Ingestion Is

### The Core Concept

Feed Ingestion is the process of pulling content from social media platforms and making it available for processing. It is the mechanical bridge between external platforms (Twitter, LinkedIn, Reddit) and the Content Discovery pipeline.

**Input:** Configured sources from Section 7.1
**Output:** Normalized posts stored in database, ready for classification

Ingestion handles all the complexity of dealing with external APIs:
- Different authentication methods per platform
- Different API structures and response formats
- Rate limits that vary by platform and endpoint
- Pagination mechanisms that differ across platforms
- Network failures, timeouts, and partial responses
- Data format differences requiring normalization

Downstream systems (classification, scoring, filtering) never deal with platform specifics. They receive clean, normalized posts in a unified format.

### The Ingestion Challenge

Social media platforms present numerous challenges:

**API Diversity:**
- Twitter uses OAuth 2.0 with bearer tokens
- Reddit uses OAuth 2.0 with refresh tokens
- LinkedIn uses OAuth 2.0 with specific scopes
- Each has completely different endpoint structures

**Rate Limits:**
- Twitter: 450 requests/15 min for search (app auth)
- Reddit: 60 requests/minute
- LinkedIn: Varies, often more restrictive
- Exceeding limits = temporary blocks

**Data Formats:**
- Twitter returns nested JSON with "includes" for referenced data
- Reddit returns nested "data" objects with "children" arrays
- LinkedIn returns different structures per endpoint
- Field names, types, and nesting all differ

**Reliability:**
- APIs fail, timeout, return errors
- Network issues cause partial data
- Rate limits cause temporary blocks
- Tokens expire and need refresh

Ingestion must handle all of this transparently.

### Ingestion vs Discovery

**Ingestion:** The mechanical process of fetching data from APIs, parsing responses, normalizing data, storing posts. Focused on data acquisition.

**Discovery:** The broader system including ingestion, classification, scoring, filtering, queuing. Focused on finding opportunities.

Ingestion is one stage within Discovery — the data acquisition stage.

## 7.2.2 The Ingestion Pipeline

### Pipeline Overview

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                            FEED INGESTION PIPELINE                                  │
│                                                                                     │
│  ┌───────────┐    ┌───────────┐    ┌───────────┐    ┌───────────┐    ┌───────────┐ │
│  │   JOB     │    │   API     │    │ RESPONSE  │    │  DATA     │    │  DEDUP    │ │
│  │SCHEDULING │───▶│EXECUTION  │───▶│ PARSING   │───▶│NORMALIZE  │───▶│ & STORE   │ │
│  │           │    │           │    │           │    │           │    │           │ │
│  │ When to   │    │ Call      │    │ Extract   │    │ Convert   │    │ Check     │ │
│  │ poll each │    │ platform  │    │ posts     │    │ to        │    │ exists,   │ │
│  │ source    │    │ APIs      │    │ from      │    │ unified   │    │ store     │ │
│  │           │    │           │    │ response  │    │ format    │    │ new       │ │
│  └───────────┘    └───────────┘    └───────────┘    └───────────┘    └───────────┘ │
│                                                                            │        │
│                                                                            ▼        │
│  ┌───────────────────────────────────────────────────────────────────────────────┐ │
│  │                              STATE UPDATE                                      │ │
│  │                                                                                │ │
│  │  Update last_polled, last_post_id, pagination cursor, error counts            │ │
│  └───────────────────────────────────────────────────────────────────────────────┘ │
│                                                                            │        │
│                                                                            ▼        │
│  ┌───────────────────────────────────────────────────────────────────────────────┐ │
│  │                              HANDOFF                                           │ │
│  │                                                                                │ │
│  │  Mark posts ready for classification, trigger downstream processing           │ │
│  └───────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

### Stage 1: Job Scheduling

**Purpose:** Determine when each source should be polled.

**Process:**
1. Read source configurations (polling intervals, priorities)
2. Check last poll time for each source
3. Determine which sources are due for polling
4. Create ingestion jobs and add to queue
5. Order jobs by priority

**Output:** Queue of ingestion jobs ready to execute.

### Stage 2: API Execution

**Purpose:** Execute API calls to platforms and retrieve data.

**Process:**
1. Load source configuration
2. Construct API request (endpoint, parameters, auth)
3. Execute HTTP request with timeout
4. Handle rate limits, retries, errors
5. Return raw response

**Output:** Raw API response (JSON) or error.

### Stage 3: Response Parsing

**Purpose:** Extract post data from platform-specific response formats.

**Process:**
1. Parse JSON response
2. Navigate platform-specific structure
3. Extract post objects
4. Extract referenced data (authors, media)
5. Handle missing/optional fields

**Output:** Array of platform-specific post objects.

### Stage 4: Data Normalization

**Purpose:** Convert platform-specific formats to unified format.

**Process:**
1. Map platform fields to unified fields
2. Normalize timestamps to UTC
3. Normalize text (decode entities, trim)
4. Calculate derived fields (engagement rate)
5. Preserve platform-specific data in metadata

**Output:** Array of normalized post objects.

### Stage 5: Deduplication & Storage

**Purpose:** Store new posts, skip duplicates.

**Process:**
1. For each normalized post:
   - Check if platform+platform_post_id exists
   - If exists: Update engagement metrics (optional), skip insert
   - If new: Insert post record
2. Record which sources matched each post
3. Log duplicate counts

**Output:** Count of new posts stored.

### Stage 6: State Update

**Purpose:** Update source state for next poll.

**Process:**
1. Update last_polled_at timestamp
2. Store newest post ID for since-based pagination
3. Store pagination cursor for cursor-based pagination
4. Reset or increment error counts
5. Calculate next_poll_at

**Output:** Updated source state.

### Stage 7: Handoff

**Purpose:** Signal that posts are ready for downstream processing.

**Process:**
1. Mark posts with status = "discovered"
2. Either:
   - Push post IDs to classification queue
   - Or: Classification polls for new posts
3. Log handoff

**Output:** Posts available for classification.

## 7.2.3 Job Scheduling

### Scheduling System Overview

The job scheduler determines when to poll each source:

**Continuous polling loop:**
```
while running:
    sources_due = get_sources_due_for_poll()
    for source in sources_due:
        create_ingestion_job(source)
    sleep(scheduler_interval)  # e.g., 30 seconds
```

**Determining if source is due:**
```
is_due = (now - source.state.last_polled_at) >= source.polling_interval_minutes
```

### Job Data Structure

Each ingestion job contains:

```
{
  "job_id": "job_a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "source_id": "src_001",
  "campaign_id": "camp_001",
  "platform": "twitter",
  "source_type": "keyword",
  "source_config": {
    "query": "AI agent security",
    "exclude_terms": ["hiring", "job"],
    ...
  },
  "priority": "high",
  "created_at": "2024-01-15T14:30:00Z",
  "scheduled_for": "2024-01-15T14:30:00Z",
  "state": {
    "last_post_id": "1234567890123456789",
    "last_post_at": "2024-01-15T14:20:00Z",
    "pagination_cursor": null
  },
  "status": "pending",
  "attempt": 1,
  "max_attempts": 3
}
```

### Priority-Based Scheduling

When multiple sources are due simultaneously:

**Priority order:**
1. High priority sources first
2. Medium priority sources second
3. Low priority sources last

**Within same priority:**
- Sort by last_polled_at ascending (longest waiting first)

**Resource allocation:**
- High priority: Dedicated workers if available
- Medium priority: Shared worker pool
- Low priority: Process when capacity allows

### Job Queue Implementation

**Queue structure (Redis example):**
```
# Priority queues
ingestion:jobs:high      # High priority jobs
ingestion:jobs:medium    # Medium priority jobs
ingestion:jobs:low       # Low priority jobs

# Job data
ingestion:job:{job_id}   # Job details (hash)
```

**Enqueue operation:**
```
LPUSH ingestion:jobs:{priority} {job_id}
HSET ingestion:job:{job_id} {job_data}
```

**Dequeue operation (worker):**
```
# Try high priority first, then medium, then low
job_id = BRPOP ingestion:jobs:high ingestion:jobs:medium ingestion:jobs:low
job_data = HGETALL ingestion:job:{job_id}
```

### Concurrency Control

**Per-platform limits:**
Limit concurrent jobs per platform to stay within rate limits.

```
Platform concurrency limits:
- Twitter: 5 concurrent jobs
- LinkedIn: 2 concurrent jobs
- Reddit: 3 concurrent jobs
```

**Implementation:**
```
acquire_platform_lock(platform, timeout=30s)
try:
    execute_ingestion_job(job)
finally:
    release_platform_lock(platform)
```

**Per-source locking:**
Prevent multiple jobs for same source simultaneously.

```
if not acquire_source_lock(source_id):
    # Source already being polled
    reschedule_job(job_id, delay=60s)
    return
```

### Scheduling Intervals

**Recommended intervals by source type:**

| Source Type | Priority | Interval | Rationale |
|-------------|----------|----------|-----------|
| Mention | High | 2-5 min | Time-sensitive, respond quickly |
| Keyword (focused) | High | 10-15 min | Core monitoring |
| Account | Medium | 15-30 min | Less time-sensitive |
| Hashtag | Medium | 15-30 min | Moderate volume |
| Community | Medium | 30-60 min | Discussions last longer |
| Trending | Low | 15-30 min | Exploratory |
| Keyword (broad) | Low | 30-60 min | High volume, less urgent |

**Minimum intervals:**
Enforce minimum intervals to prevent API abuse:
- Twitter: 5 minute minimum
- LinkedIn: 15 minute minimum
- Reddit: 5 minute minimum

### Backoff and Catch-Up

**After errors:**
If a job fails, apply exponential backoff:

```
next_attempt_delay = min(base_delay * (2 ^ attempt), max_delay)
# base_delay = 60 seconds
# max_delay = 3600 seconds (1 hour)

Attempt 1 failure: Wait 60s
Attempt 2 failure: Wait 120s
Attempt 3 failure: Wait 240s
... up to 1 hour
```

**After extended downtime:**
If system was down and sources are behind:
- Don't create all jobs at once (would overwhelm API)
- Stagger catch-up jobs over time
- Prioritize high-priority sources

## 7.2.4 API Execution

### Authentication

#### Twitter/X Authentication

**OAuth 2.0 Bearer Token (App-only):**
```
Authorization: Bearer {access_token}
```

**Token acquisition:**
```
POST https://api.twitter.com/oauth2/token
Authorization: Basic {base64(client_id:client_secret)}
Content-Type: application/x-www-form-urlencoded

grant_type=client_credentials
```

**Token storage:**
- Store encrypted in database or secrets manager
- Tokens don't expire (for app-only auth)
- Rotate periodically for security

#### Reddit Authentication

**OAuth 2.0 with refresh:**
```
Authorization: Bearer {access_token}
User-Agent: {app_name}/{version} by {reddit_username}
```

**Token acquisition:**
```
POST https://www.reddit.com/api/v1/access_token
Authorization: Basic {base64(client_id:client_secret)}
Content-Type: application/x-www-form-urlencoded

grant_type=client_credentials
```

**Token refresh:**
- Access tokens expire after 1 hour
- Refresh before expiration
- Store refresh token securely

**User-Agent requirement:**
Reddit requires descriptive User-Agent. Without it, requests are heavily rate-limited or blocked.

```
User-Agent: JenContentDiscovery/1.0 by /u/gendigital
```

#### LinkedIn Authentication

**OAuth 2.0 with scopes:**
```
Authorization: Bearer {access_token}
```

**Required scopes:**
- `r_liteprofile` — Basic profile
- `r_organization_social` — Organization posts
- `w_member_social` — Posting (not needed for read)

**Token management:**
- Access tokens expire (typically 60 days)
- Refresh tokens available with some grants
- May need user re-authentication periodically

### Request Construction

#### Twitter Request Examples

**Search tweets:**
```
GET https://api.twitter.com/2/tweets/search/recent
?query=AI%20agent%20security%20-is:retweet%20lang:en
&max_results=100
&tweet.fields=author_id,created_at,public_metrics,entities,conversation_id
&user.fields=name,username,verified,public_metrics,description
&expansions=author_id,referenced_tweets.id
&since_id=1234567890123456789
```

**User tweets:**
```
GET https://api.twitter.com/2/users/{user_id}/tweets
?max_results=100
&tweet.fields=author_id,created_at,public_metrics,entities
&exclude=retweets,replies
&since_id=1234567890123456789
```

**List tweets:**
```
GET https://api.twitter.com/2/lists/{list_id}/tweets
?max_results=100
&tweet.fields=author_id,created_at,public_metrics
&expansions=author_id
```

#### Reddit Request Examples

**Subreddit posts:**
```
GET https://oauth.reddit.com/r/MachineLearning/new
?limit=100
&after=t3_abc123
```

**Search:**
```
GET https://oauth.reddit.com/search
?q=AI%20agent%20security
&type=link
&sort=new
&limit=100
&restrict_sr=false
```

**User posts:**
```
GET https://oauth.reddit.com/user/{username}/submitted
?limit=100
&sort=new
```

#### LinkedIn Request Examples

**Organization posts:**
```
GET https://api.linkedin.com/v2/shares
?q=owners
&owners=urn:li:organization:{org_id}
&count=100
```

**Search (limited):**
LinkedIn search API has very limited access. May need to use other approaches.

### Pagination Handling

#### Twitter Pagination (Cursor-based)

**Response includes:**
```json
{
  "data": [...],
  "meta": {
    "next_token": "b26v89c19zqg8o3fpzbf3xz",
    "result_count": 100
  }
}
```

**Next request:**
```
GET /tweets/search/recent?query=...&pagination_token=b26v89c19zqg8o3fpzbf3xz
```

**Pagination loop:**
```
all_posts = []
next_token = None

while True:
    response = fetch_tweets(query, pagination_token=next_token)
    all_posts.extend(response.data)
    
    if 'next_token' not in response.meta:
        break  # No more pages
    
    next_token = response.meta.next_token
    
    if len(all_posts) >= max_results:
        break  # Hit our limit
```

#### Reddit Pagination (after-based)

**Response includes:**
```json
{
  "data": {
    "after": "t3_xyz789",
    "children": [...]
  }
}
```

**Next request:**
```
GET /r/MachineLearning/new?after=t3_xyz789
```

#### Since-based Pagination

For subsequent polls, use `since_id` or `since` timestamp:

**Twitter:**
```
?since_id=1234567890123456789
```
Returns only tweets newer than this ID.

**Implementation:**
```
# Store after successful poll
state.last_post_id = newest_post_id

# Use on next poll
params['since_id'] = state.last_post_id
```

### Timeout and Retry Configuration

**Timeout settings:**

| Setting | Value | Rationale |
|---------|-------|-----------|
| Connect timeout | 10 seconds | Detect network issues quickly |
| Read timeout | 30 seconds | Allow for slow responses |
| Total timeout | 60 seconds | Bound total request time |

**Retry configuration:**

```python
retry_config = {
    'max_retries': 3,
    'retry_on': [429, 500, 502, 503, 504],
    'retry_on_network_errors': True,
    'backoff': 'exponential',
    'backoff_factor': 2,
    'initial_wait': 1,  # seconds
    'max_wait': 60,     # seconds
}
```

**Retry logic:**
```
for attempt in range(max_retries + 1):
    try:
        response = execute_request(request)
        if response.status_code == 429:
            wait_time = get_retry_after(response) or calculate_backoff(attempt)
            sleep(wait_time)
            continue
        if response.status_code in [500, 502, 503, 504]:
            sleep(calculate_backoff(attempt))
            continue
        return response
    except NetworkError:
        sleep(calculate_backoff(attempt))
        continue

raise MaxRetriesExceeded()
```

### Error Handling

#### HTTP Error Responses

| Code | Meaning | Action |
|------|---------|--------|
| 200 | Success | Process response |
| 400 | Bad request | Log error, don't retry, check source config |
| 401 | Unauthorized | Refresh token, retry once |
| 403 | Forbidden | Log error, check permissions, may need re-auth |
| 404 | Not found | Log error, resource may be deleted |
| 429 | Rate limited | Back off per Retry-After header or default |
| 500 | Server error | Retry with exponential backoff |
| 502 | Bad gateway | Retry with exponential backoff |
| 503 | Unavailable | Retry with exponential backoff |
| 504 | Gateway timeout | Retry with exponential backoff |

#### Rate Limit Response Handling

**Twitter rate limit response:**
```json
{
  "title": "Too Many Requests",
  "detail": "Too Many Requests",
  "type": "about:blank"
}
```

**Headers:**
```
x-rate-limit-limit: 450
x-rate-limit-remaining: 0
x-rate-limit-reset: 1673789000
```

**Handling:**
```python
if response.status_code == 429:
    reset_time = int(response.headers.get('x-rate-limit-reset', 0))
    wait_seconds = max(reset_time - time.time(), 60)
    wait_seconds = min(wait_seconds, 900)  # Cap at 15 minutes
    raise RateLimitExceeded(wait_seconds=wait_seconds)
```

#### Network Errors

| Error | Action |
|-------|--------|
| Connection refused | Retry with backoff |
| Connection timeout | Retry with backoff |
| Read timeout | Retry with backoff |
| DNS resolution failure | Retry with backoff |
| SSL/TLS error | Log, check certificates, may need intervention |

## 7.2.5 Rate Limit Management

### Rate Limit Tracking

Track rate limits per platform and endpoint:

**Rate limit state:**
```
{
  "platform": "twitter",
  "endpoint": "search/recent",
  "window_minutes": 15,
  "limit": 450,
  "remaining": 234,
  "reset_at": "2024-01-15T14:45:00Z",
  "updated_at": "2024-01-15T14:32:15Z"
}
```

**Update from response headers:**
```python
def update_rate_limit(platform, endpoint, response):
    state = get_rate_limit_state(platform, endpoint)
    
    if 'x-rate-limit-limit' in response.headers:
        state.limit = int(response.headers['x-rate-limit-limit'])
    if 'x-rate-limit-remaining' in response.headers:
        state.remaining = int(response.headers['x-rate-limit-remaining'])
    if 'x-rate-limit-reset' in response.headers:
        state.reset_at = datetime.fromtimestamp(
            int(response.headers['x-rate-limit-reset'])
        )
    
    state.updated_at = datetime.now()
    save_rate_limit_state(state)
```

### Platform Rate Limits Reference

#### Twitter API v2 Rate Limits

| Endpoint | App Rate Limit | Per 15 min |
|----------|---------------|------------|
| GET /2/tweets/search/recent | 450 requests | 450 |
| GET /2/users/:id/tweets | 1500 requests | 1500 |
| GET /2/lists/:id/tweets | 900 requests | 900 |
| GET /2/tweets | 300 requests | 300 |

**Tweet cap:**
Depending on access level, monthly tweet read cap applies:
- Free: 500K tweets/month
- Basic: 10K tweets/month
- Pro: 1M tweets/month
- Enterprise: Negotiated

#### Reddit API Rate Limits

| Auth Type | Rate Limit |
|-----------|------------|
| OAuth app | 60 requests/minute |
| Script app | 30 requests/minute |

**Per-user limits:**
Reddit may impose additional limits on specific users/apps.

#### LinkedIn API Rate Limits

| Endpoint | Daily Limit |
|----------|-------------|
| Shares (read) | 100K calls/day |
| Profile | Varies by app |

**Note:** LinkedIn limits are often more restrictive and less transparent.

### Proactive Throttling

Don't wait until rate limits are hit. Throttle proactively:

**Throttling strategy:**
```python
def should_throttle(platform, endpoint):
    state = get_rate_limit_state(platform, endpoint)
    
    # If we don't have state, allow but track
    if not state:
        return False
    
    # If window reset, allow
    if datetime.now() > state.reset_at:
        return False
    
    # Calculate time remaining in window
    time_remaining = (state.reset_at - datetime.now()).seconds
    
    # Calculate desired request rate
    # Leave 10% buffer
    safe_remaining = state.remaining * 0.9
    
    if safe_remaining <= 0:
        return True  # Must throttle
    
    # Calculate if we should slow down
    requests_per_second = safe_remaining / max(time_remaining, 1)
    
    # If rate is very low, add delay
    if requests_per_second < 0.5:
        return True
    
    return False

def get_throttle_delay(platform, endpoint):
    state = get_rate_limit_state(platform, endpoint)
    
    if state.remaining <= 0:
        # Wait until reset
        return (state.reset_at - datetime.now()).seconds + 5
    
    # Calculate spacing
    time_remaining = (state.reset_at - datetime.now()).seconds
    delay = time_remaining / max(state.remaining, 1)
    
    return min(delay, 60)  # Cap at 60 seconds
```

### Rate Limit Budget Allocation

When multiple sources compete for rate limit budget:

**Allocation strategy:**
1. Reserve portion for high-priority sources
2. Distribute remainder based on source count
3. Track actual usage vs allocation

**Example allocation:**
```
Twitter search: 450 req/15 min total

High priority sources (3): 225 requests reserved (75 each)
Medium priority sources (8): 180 requests (22 each)
Low priority sources (4): 45 requests (11 each)
```

**Implementation:**
```python
def get_source_budget(source, platform_limits):
    platform_limit = platform_limits[source.platform]
    
    # Count sources by priority
    high_count = count_sources(platform=source.platform, priority='high')
    medium_count = count_sources(platform=source.platform, priority='medium')
    low_count = count_sources(platform=source.platform, priority='low')
    
    # Allocation percentages
    HIGH_PERCENT = 0.50
    MEDIUM_PERCENT = 0.35
    LOW_PERCENT = 0.15
    
    if source.priority == 'high':
        pool = platform_limit * HIGH_PERCENT
        return pool / max(high_count, 1)
    elif source.priority == 'medium':
        pool = platform_limit * MEDIUM_PERCENT
        return pool / max(medium_count, 1)
    else:
        pool = platform_limit * LOW_PERCENT
        return pool / max(low_count, 1)
```

### Rate Limit Storage

**Table: rate_limit_state**

```sql
CREATE TABLE rate_limit_state (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    platform VARCHAR(50) NOT NULL,
    endpoint VARCHAR(100) NOT NULL,
    
    -- Limit info
    window_minutes INTEGER NOT NULL DEFAULT 15,
    request_limit INTEGER NOT NULL,
    requests_remaining INTEGER NOT NULL,
    reset_at TIMESTAMP WITH TIME ZONE NOT NULL,
    
    -- Usage tracking
    requests_made_this_window INTEGER NOT NULL DEFAULT 0,
    
    -- Timestamps
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    CONSTRAINT rate_limit_unique UNIQUE (platform, endpoint)
);
```

## 7.2.6 Response Parsing

### Twitter Response Parsing

#### Tweet Search Response Structure

```json
{
  "data": [
    {
      "id": "1618012345678901234",
      "text": "Working on AI agent security features today. The challenge of runtime verification is fascinating. #AIAgents",
      "author_id": "123456789",
      "created_at": "2024-01-15T14:30:00.000Z",
      "conversation_id": "1618012345678901234",
      "public_metrics": {
        "retweet_count": 15,
        "reply_count": 8,
        "like_count": 142,
        "quote_count": 3,
        "impression_count": 8500
      },
      "entities": {
        "hashtags": [
          {
            "start": 95,
            "end": 104,
            "tag": "AIAgents"
          }
        ],
        "urls": [],
        "mentions": []
      },
      "referenced_tweets": []
    }
  ],
  "includes": {
    "users": [
      {
        "id": "123456789",
        "name": "AI Security Researcher",
        "username": "aisecuritydev",
        "verified": true,
        "description": "Building safer AI systems. Previously @BigTechCo. Opinions my own.",
        "public_metrics": {
          "followers_count": 45000,
          "following_count": 1200,
          "tweet_count": 8500,
          "listed_count": 320
        },
        "created_at": "2015-03-20T10:00:00.000Z",
        "profile_image_url": "https://pbs.twimg.com/profile_images/..."
      }
    ]
  },
  "meta": {
    "newest_id": "1618012345678901234",
    "oldest_id": "1618012345678900000",
    "result_count": 100,
    "next_token": "b26v89c19zqg8o3fpzbf3xz"
  }
}
```

#### Twitter Parser Implementation

```python
def parse_twitter_response(response_json):
    posts = []
    
    # Build user lookup from includes
    users_by_id = {}
    if 'includes' in response_json and 'users' in response_json['includes']:
        for user in response_json['includes']['users']:
            users_by_id[user['id']] = user
    
    # Parse each tweet
    for tweet in response_json.get('data', []):
        author = users_by_id.get(tweet.get('author_id'), {})
        
        parsed_post = {
            'platform': 'twitter',
            'platform_post_id': tweet['id'],
            'content_text': tweet.get('text', ''),
            'created_at': parse_iso_timestamp(tweet.get('created_at')),
            
            'author': {
                'platform_author_id': tweet.get('author_id'),
                'handle': author.get('username'),
                'display_name': author.get('name'),
                'avatar_url': author.get('profile_image_url'),
                'bio': author.get('description'),
                'followers_count': author.get('public_metrics', {}).get('followers_count', 0),
                'following_count': author.get('public_metrics', {}).get('following_count', 0),
                'verified': author.get('verified', False),
                'account_created_at': parse_iso_timestamp(author.get('created_at')),
            },
            
            'engagement': {
                'likes': tweet.get('public_metrics', {}).get('like_count', 0),
                'replies': tweet.get('public_metrics', {}).get('reply_count', 0),
                'shares': tweet.get('public_metrics', {}).get('retweet_count', 0),
                'quotes': tweet.get('public_metrics', {}).get('quote_count', 0),
                'views': tweet.get('public_metrics', {}).get('impression_count'),
            },
            
            'entities': {
                'hashtags': [h['tag'] for h in tweet.get('entities', {}).get('hashtags', [])],
                'mentions': [m['username'] for m in tweet.get('entities', {}).get('mentions', [])],
                'urls': [u['expanded_url'] for u in tweet.get('entities', {}).get('urls', [])],
            },
            
            'platform_data': {
                'conversation_id': tweet.get('conversation_id'),
                'referenced_tweets': tweet.get('referenced_tweets', []),
                'tweet_type': determine_tweet_type(tweet),
            }
        }
        
        posts.append(parsed_post)
    
    # Extract pagination
    meta = response_json.get('meta', {})
    pagination = {
        'next_token': meta.get('next_token'),
        'newest_id': meta.get('newest_id'),
        'oldest_id': meta.get('oldest_id'),
        'result_count': meta.get('result_count', 0),
    }
    
    return posts, pagination


def determine_tweet_type(tweet):
    referenced = tweet.get('referenced_tweets', [])
    if not referenced:
        return 'original'
    
    ref_types = [r.get('type') for r in referenced]
    if 'retweeted' in ref_types:
        return 'retweet'
    if 'quoted' in ref_types:
        return 'quote'
    if 'replied_to' in ref_types:
        return 'reply'
    
    return 'original'
```

### Reddit Response Parsing

#### Subreddit Listing Response Structure

```json
{
  "kind": "Listing",
  "data": {
    "after": "t3_abc123xyz",
    "before": null,
    "children": [
      {
        "kind": "t3",
        "data": {
          "id": "abc123xyz",
          "name": "t3_abc123xyz",
          "title": "How do you handle AI agent security in production?",
          "selftext": "We're deploying an AI agent system and I'm concerned about...",
          "selftext_html": "&lt;!-- SC_OFF --&gt;&lt;div class=\"md\"&gt;...",
          "author": "ml_developer_42",
          "author_fullname": "t2_12345678",
          "subreddit": "MachineLearning",
          "subreddit_id": "t5_2r3gv",
          "created_utc": 1705329000,
          "score": 156,
          "upvote_ratio": 0.94,
          "num_comments": 42,
          "permalink": "/r/MachineLearning/comments/abc123xyz/...",
          "url": "https://www.reddit.com/r/MachineLearning/comments/...",
          "is_self": true,
          "link_flair_text": "Discussion",
          "over_18": false,
          "spoiler": false,
          "locked": false,
          "stickied": false,
          "distinguished": null,
          "total_awards_received": 2
        }
      }
    ],
    "dist": 25
  }
}
```

#### Reddit Parser Implementation

```python
def parse_reddit_response(response_json):
    posts = []
    
    data = response_json.get('data', {})
    children = data.get('children', [])
    
    for child in children:
        if child.get('kind') != 't3':  # t3 = post/link
            continue
        
        post_data = child.get('data', {})
        
        # Combine title and selftext for content
        title = post_data.get('title', '')
        selftext = post_data.get('selftext', '')
        content = f"{title}\n\n{selftext}".strip() if selftext else title
        
        parsed_post = {
            'platform': 'reddit',
            'platform_post_id': post_data.get('name'),  # e.g., "t3_abc123"
            'content_text': content,
            'created_at': datetime.fromtimestamp(post_data.get('created_utc', 0), tz=timezone.utc),
            
            'author': {
                'platform_author_id': post_data.get('author_fullname'),
                'handle': post_data.get('author'),
                'display_name': post_data.get('author'),  # Reddit doesn't have display names
                'avatar_url': None,  # Not in listing response
                'bio': None,
                'followers_count': None,  # Would need separate API call
                'following_count': None,
                'verified': False,
                'account_created_at': None,
            },
            
            'engagement': {
                'likes': post_data.get('score', 0),  # Reddit "score" = upvotes - downvotes
                'replies': post_data.get('num_comments', 0),
                'shares': None,  # Reddit doesn't expose share count
                'upvote_ratio': post_data.get('upvote_ratio'),
                'awards': post_data.get('total_awards_received', 0),
            },
            
            'entities': {
                'hashtags': [],  # Reddit doesn't use hashtags
                'mentions': extract_reddit_mentions(content),
                'urls': extract_urls(post_data.get('url', '')),
            },
            
            'platform_data': {
                'subreddit': post_data.get('subreddit'),
                'subreddit_id': post_data.get('subreddit_id'),
                'flair': post_data.get('link_flair_text'),
                'is_self': post_data.get('is_self', True),
                'permalink': post_data.get('permalink'),
                'over_18': post_data.get('over_18', False),
                'spoiler': post_data.get('spoiler', False),
                'locked': post_data.get('locked', False),
                'stickied': post_data.get('stickied', False),
            }
        }
        
        posts.append(parsed_post)
    
    # Extract pagination
    pagination = {
        'after': data.get('after'),
        'before': data.get('before'),
        'result_count': len(children),
    }
    
    return posts, pagination


def extract_reddit_mentions(text):
    """Extract u/username mentions from Reddit text."""
    import re
    pattern = r'u/([A-Za-z0-9_-]+)'
    return re.findall(pattern, text)
```

### LinkedIn Response Parsing

#### Share Response Structure

```json
{
  "elements": [
    {
      "id": "urn:li:share:7012345678901234567",
      "owner": "urn:li:organization:12345678",
      "created": {
        "time": 1705329000000
      },
      "lastModified": {
        "time": 1705330000000
      },
      "text": {
        "text": "Excited to announce our new AI agent security platform..."
      },
      "distribution": {
        "linkedInDistributionTarget": {}
      },
      "totalShareStatistics": {
        "shareCount": 45,
        "clickCount": 892,
        "engagement": 234,
        "likeCount": 178,
        "impressionCount": 12500,
        "commentCount": 32
      }
    }
  ],
  "paging": {
    "count": 10,
    "start": 0,
    "links": [
      {
        "type": "application/json",
        "rel": "next",
        "href": "/v2/shares?start=10&count=10..."
      }
    ]
  }
}
```

#### LinkedIn Parser Implementation

```python
def parse_linkedin_response(response_json):
    posts = []
    
    elements = response_json.get('elements', [])
    
    for element in elements:
        stats = element.get('totalShareStatistics', {})
        
        parsed_post = {
            'platform': 'linkedin',
            'platform_post_id': element.get('id'),  # URN format
            'content_text': element.get('text', {}).get('text', ''),
            'created_at': datetime.fromtimestamp(
                element.get('created', {}).get('time', 0) / 1000,
                tz=timezone.utc
            ),
            
            'author': {
                'platform_author_id': element.get('owner'),
                'handle': None,  # Would need separate API call
                'display_name': None,
                'avatar_url': None,
                'bio': None,
                'followers_count': None,
                'following_count': None,
                'verified': False,
                'account_created_at': None,
            },
            
            'engagement': {
                'likes': stats.get('likeCount', 0),
                'replies': stats.get('commentCount', 0),
                'shares': stats.get('shareCount', 0),
                'clicks': stats.get('clickCount', 0),
                'views': stats.get('impressionCount'),
            },
            
            'entities': {
                'hashtags': extract_hashtags(element.get('text', {}).get('text', '')),
                'mentions': extract_linkedin_mentions(element.get('text', {}).get('text', '')),
                'urls': [],
            },
            
            'platform_data': {
                'owner_type': parse_urn_type(element.get('owner')),
                'distribution': element.get('distribution'),
            }
        }
        
        posts.append(parsed_post)
    
    # Extract pagination
    paging = response_json.get('paging', {})
    next_link = None
    for link in paging.get('links', []):
        if link.get('rel') == 'next':
            next_link = link.get('href')
            break
    
    pagination = {
        'next_href': next_link,
        'start': paging.get('start', 0),
        'count': paging.get('count', 0),
        'result_count': len(elements),
    }
    
    return posts, pagination
```

### Error Response Handling

**Handle malformed responses:**
```python
def safe_parse_response(platform, response_json):
    try:
        if platform == 'twitter':
            return parse_twitter_response(response_json)
        elif platform == 'reddit':
            return parse_reddit_response(response_json)
        elif platform == 'linkedin':
            return parse_linkedin_response(response_json)
        else:
            raise ValueError(f"Unknown platform: {platform}")
    
    except KeyError as e:
        log.error(f"Missing expected field in {platform} response: {e}")
        return [], {}
    
    except TypeError as e:
        log.error(f"Type error parsing {platform} response: {e}")
        return [], {}
    
    except Exception as e:
        log.error(f"Unexpected error parsing {platform} response: {e}")
        return [], {}
```

## 7.2.7 Data Normalization

### Unified Post Schema

All posts are normalized to this structure:

```python
@dataclass
class NormalizedPost:
    # Identity
    id: UUID                           # Internal unique ID (generated)
    platform: str                      # twitter, linkedin, reddit
    platform_post_id: str              # Platform's ID for the post
    
    # Source tracking
    source_id: UUID                    # Which source discovered this
    campaign_id: UUID                  # Which campaign
    
    # Content
    content_text: str                  # Plain text content
    content_html: Optional[str]        # HTML if available
    language: Optional[str]            # Detected language (ISO 639-1)
    
    # Media and links
    media: List[MediaAttachment]       # Images, videos
    links: List[str]                   # Embedded URLs
    
    # Author
    author: NormalizedAuthor           # Author details
    
    # Engagement
    engagement: EngagementMetrics      # Likes, replies, shares
    
    # Timestamps
    created_at: datetime               # When posted (UTC)
    discovered_at: datetime            # When we found it (UTC)
    
    # Platform-specific data (preserved)
    platform_data: Dict[str, Any]      # Anything platform-specific
    
    # Processing state
    status: str                        # discovered, classified, scored, etc.


@dataclass
class NormalizedAuthor:
    id: UUID                           # Internal ID (generated)
    platform: str                      # twitter, linkedin, reddit
    platform_author_id: str            # Platform's author ID
    
    handle: Optional[str]              # @username, u/username, etc.
    display_name: Optional[str]        # Display name
    avatar_url: Optional[str]          # Profile image URL
    bio: Optional[str]                 # Profile bio/description
    
    followers_count: Optional[int]     # Follower count
    following_count: Optional[int]     # Following count
    verified: bool                     # Is verified/official
    account_created_at: Optional[datetime]  # When account was created


@dataclass
class EngagementMetrics:
    likes: int                         # Likes/favorites/upvotes
    replies: int                       # Comments/replies
    shares: int                        # Retweets/reposts/shares
    views: Optional[int]               # Impressions if available
    
    # Platform-specific
    quotes: Optional[int]              # Quote tweets (Twitter)
    upvote_ratio: Optional[float]      # Upvote ratio (Reddit)
    awards: Optional[int]              # Awards (Reddit)
    clicks: Optional[int]              # Clicks (LinkedIn)


@dataclass
class MediaAttachment:
    type: str                          # image, video, gif
    url: str                           # Media URL
    thumbnail_url: Optional[str]       # Thumbnail if available
    alt_text: Optional[str]            # Alt text if available
    width: Optional[int]               # Width in pixels
    height: Optional[int]              # Height in pixels
```

### Field Mapping Tables

#### Twitter Field Mapping

| Twitter Field | Normalized Field | Notes |
|---------------|------------------|-------|
| id | platform_post_id | String, not int |
| text | content_text | Decode HTML entities |
| created_at | created_at | Parse ISO 8601, convert to UTC |
| author_id | author.platform_author_id | Look up in includes |
| includes.users[].username | author.handle | Match by author_id |
| includes.users[].name | author.display_name | |
| includes.users[].verified | author.verified | |
| includes.users[].public_metrics.followers_count | author.followers_count | |
| public_metrics.like_count | engagement.likes | Default to 0 |
| public_metrics.reply_count | engagement.replies | Default to 0 |
| public_metrics.retweet_count | engagement.shares | Default to 0 |
| public_metrics.impression_count | engagement.views | May be null |
| public_metrics.quote_count | engagement.quotes | Twitter-specific |
| entities.hashtags | entities.hashtags | Extract tag values |
| entities.urls | links | Extract expanded_url |
| conversation_id | platform_data.conversation_id | Preserve |
| referenced_tweets | platform_data.referenced_tweets | Preserve |

#### Reddit Field Mapping

| Reddit Field | Normalized Field | Notes |
|--------------|------------------|-------|
| name | platform_post_id | Includes prefix (t3_) |
| title + selftext | content_text | Concatenate |
| selftext_html | content_html | Decode entities |
| created_utc | created_at | Unix timestamp to datetime |
| author | author.handle | Prepend u/ |
| author_fullname | author.platform_author_id | |
| score | engagement.likes | Actually upvotes - downvotes |
| num_comments | engagement.replies | |
| upvote_ratio | engagement.upvote_ratio | Reddit-specific |
| total_awards_received | engagement.awards | Reddit-specific |
| subreddit | platform_data.subreddit | Preserve |
| link_flair_text | platform_data.flair | Preserve |
| permalink | platform_data.permalink | Preserve |

#### LinkedIn Field Mapping

| LinkedIn Field | Normalized Field | Notes |
|----------------|------------------|-------|
| id | platform_post_id | URN format |
| text.text | content_text | |
| created.time | created_at | Milliseconds to datetime |
| owner | author.platform_author_id | URN format |
| totalShareStatistics.likeCount | engagement.likes | |
| totalShareStatistics.commentCount | engagement.replies | |
| totalShareStatistics.shareCount | engagement.shares | |
| totalShareStatistics.impressionCount | engagement.views | |
| totalShareStatistics.clickCount | engagement.clicks | LinkedIn-specific |

### Normalization Functions

#### Text Normalization

```python
import html
import unicodedata
import re

def normalize_text(text: str) -> str:
    if not text:
        return ""
    
    # Decode HTML entities
    text = html.unescape(text)
    
    # Normalize unicode (NFC form)
    text = unicodedata.normalize('NFC', text)
    
    # Remove null bytes
    text = text.replace('\x00', '')
    
    # Normalize whitespace (but preserve newlines for readability)
    text = re.sub(r'[ \t]+', ' ', text)  # Collapse horizontal whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)  # Max 2 consecutive newlines
    
    # Trim leading/trailing whitespace
    text = text.strip()
    
    return text
```

#### Timestamp Normalization

```python
from datetime import datetime, timezone
from dateutil import parser as date_parser

def normalize_timestamp(value) -> datetime:
    """Convert various timestamp formats to UTC datetime."""
    
    if value is None:
        return None
    
    # Already a datetime
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)
    
    # Unix timestamp (seconds)
    if isinstance(value, (int, float)):
        # Check if milliseconds (LinkedIn uses ms)
        if value > 1e12:
            value = value / 1000
        return datetime.fromtimestamp(value, tz=timezone.utc)
    
    # ISO string
    if isinstance(value, str):
        try:
            dt = date_parser.parse(value)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)
        except Exception:
            return None
    
    return None
```

#### Count Normalization

```python
def normalize_count(value, default=0) -> int:
    """Normalize count values to non-negative integers."""
    
    if value is None:
        return default
    
    try:
        count = int(value)
        return max(count, 0)  # No negative counts
    except (ValueError, TypeError):
        return default
```

#### URL Normalization

```python
from urllib.parse import urlparse, urlunparse

def normalize_url(url: str) -> str:
    """Normalize URL format."""
    
    if not url:
        return ""
    
    # Parse and reconstruct to normalize
    try:
        parsed = urlparse(url)
        
        # Ensure scheme
        if not parsed.scheme:
            parsed = parsed._replace(scheme='https')
        
        # Lowercase hostname
        if parsed.netloc:
            parsed = parsed._replace(netloc=parsed.netloc.lower())
        
        return urlunparse(parsed)
    
    except Exception:
        return url  # Return original if parsing fails
```

### Engagement Rate Calculation

Calculate derived engagement metrics:

```python
def calculate_engagement_rate(engagement: EngagementMetrics) -> Optional[float]:
    """Calculate engagement rate as percentage."""
    
    total_engagement = (
        engagement.likes +
        engagement.replies +
        engagement.shares
    )
    
    if engagement.views and engagement.views > 0:
        return (total_engagement / engagement.views) * 100
    
    return None  # Can't calculate without views
```

### Full Normalization Pipeline

```python
def normalize_post(platform: str, parsed_post: dict, source_id: UUID, campaign_id: UUID) -> NormalizedPost:
    """Normalize a parsed post to unified format."""
    
    # Normalize author first
    author = normalize_author(platform, parsed_post.get('author', {}))
    
    # Normalize engagement
    engagement = EngagementMetrics(
        likes=normalize_count(parsed_post.get('engagement', {}).get('likes')),
        replies=normalize_count(parsed_post.get('engagement', {}).get('replies')),
        shares=normalize_count(parsed_post.get('engagement', {}).get('shares')),
        views=parsed_post.get('engagement', {}).get('views'),
        quotes=parsed_post.get('engagement', {}).get('quotes'),
        upvote_ratio=parsed_post.get('engagement', {}).get('upvote_ratio'),
        awards=parsed_post.get('engagement', {}).get('awards'),
        clicks=parsed_post.get('engagement', {}).get('clicks'),
    )
    
    # Build normalized post
    normalized = NormalizedPost(
        id=uuid4(),
        platform=platform,
        platform_post_id=str(parsed_post['platform_post_id']),
        source_id=source_id,
        campaign_id=campaign_id,
        
        content_text=normalize_text(parsed_post.get('content_text', '')),
        content_html=parsed_post.get('content_html'),
        language=detect_language(parsed_post.get('content_text', '')),
        
        media=normalize_media(parsed_post.get('media', [])),
        links=[normalize_url(u) for u in parsed_post.get('entities', {}).get('urls', [])],
        
        author=author,
        engagement=engagement,
        
        created_at=normalize_timestamp(parsed_post.get('created_at')),
        discovered_at=datetime.now(timezone.utc),
        
        platform_data=parsed_post.get('platform_data', {}),
        status='discovered',
    )
    
    # Calculate engagement rate
    normalized.engagement.rate = calculate_engagement_rate(engagement)
    
    return normalized
```

## 7.2.8 Deduplication

### Deduplication Strategy

#### Primary Key Deduplication

The primary deduplication key is: `(platform, platform_post_id)`

Each post has a unique ID on its platform. We use this to prevent storing the same post twice.

**Implementation:**
```sql
CREATE UNIQUE INDEX idx_posts_platform_post_id 
ON discovered_posts(platform, platform_post_id);
```

```python
def store_post_if_new(normalized_post: NormalizedPost) -> Tuple[bool, Optional[UUID]]:
    """Store post if it doesn't exist. Return (is_new, post_id)."""
    
    # Check if exists
    existing = db.query("""
        SELECT id FROM discovered_posts 
        WHERE platform = %s AND platform_post_id = %s
    """, [normalized_post.platform, normalized_post.platform_post_id])
    
    if existing:
        # Already exists - optionally update engagement
        update_engagement_if_fresher(existing.id, normalized_post.engagement)
        return (False, existing.id)
    
    # Insert new post
    post_id = insert_post(normalized_post)
    return (True, post_id)
```

#### Multi-Source Tracking

The same post may be discovered by multiple sources:
- Keyword source A matches "AI agent"
- Keyword source B matches "agent security"
- Same post contains both phrases

**Track all matching sources:**
```sql
CREATE TABLE post_source_matches (
    post_id UUID REFERENCES discovered_posts(id),
    source_id UUID REFERENCES sources(id),
    matched_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (post_id, source_id)
);
```

```python
def record_source_match(post_id: UUID, source_id: UUID):
    """Record that a source matched this post (even if already stored)."""
    
    db.execute("""
        INSERT INTO post_source_matches (post_id, source_id)
        VALUES (%s, %s)
        ON CONFLICT (post_id, source_id) DO NOTHING
    """, [post_id, source_id])
```

#### Engagement Update on Duplicate

When we see a post again, engagement may have changed:

```python
def update_engagement_if_fresher(post_id: UUID, new_engagement: EngagementMetrics):
    """Update engagement metrics if they're higher (post got more engagement)."""
    
    current = db.query("SELECT engagement FROM discovered_posts WHERE id = %s", [post_id])
    
    # Update if new engagement is higher (indicates fresher data)
    new_total = new_engagement.likes + new_engagement.replies + new_engagement.shares
    current_total = current.likes + current.replies + current.shares
    
    if new_total > current_total:
        db.execute("""
            UPDATE discovered_posts 
            SET engagement = %s, updated_at = NOW()
            WHERE id = %s
        """, [new_engagement.to_json(), post_id])
```

### Cross-Platform Deduplication

The same content may appear on multiple platforms (cross-posted):
- Author posts on Twitter and LinkedIn
- Same text appears on both

**Content hash for cross-platform matching:**
```python
import hashlib

def content_hash(text: str) -> str:
    """Generate hash of normalized content for cross-platform matching."""
    
    # Normalize for comparison
    normalized = text.lower()
    normalized = re.sub(r'\s+', ' ', normalized)  # Collapse whitespace
    normalized = re.sub(r'https?://\S+', '', normalized)  # Remove URLs
    normalized = re.sub(r'@\w+', '', normalized)  # Remove mentions
    normalized = re.sub(r'#\w+', '', normalized)  # Remove hashtags
    normalized = normalized.strip()
    
    return hashlib.sha256(normalized.encode()).hexdigest()[:16]
```

**Storing content hash:**
```sql
ALTER TABLE discovered_posts ADD COLUMN content_hash VARCHAR(16);
CREATE INDEX idx_posts_content_hash ON discovered_posts(content_hash);
```

**Checking for cross-platform duplicates:**
```python
def check_cross_platform_duplicate(normalized_post: NormalizedPost) -> Optional[UUID]:
    """Check if this content exists on another platform."""
    
    hash = content_hash(normalized_post.content_text)
    
    existing = db.query("""
        SELECT id, platform FROM discovered_posts
        WHERE content_hash = %s 
        AND platform != %s
        AND created_at > NOW() - INTERVAL '24 hours'
    """, [hash, normalized_post.platform])
    
    if existing:
        return existing.id
    
    return None
```

**Handling:**
- Flag as potential cross-platform duplicate
- Link posts together
- Let downstream decide whether to engage on both

### Retweet/Repost Handling

Retweets and reposts reference original content:

**Twitter retweet:**
```json
{
  "referenced_tweets": [
    {"type": "retweeted", "id": "1234567890"}
  ]
}
```

**Options:**
1. **Skip retweets:** Don't store, not original content
2. **Store and link:** Store with reference to original
3. **Store as separate:** Treat as independent opportunity

**Recommended approach:** Store but mark as retweet and link to original:

```python
def handle_retweet(tweet: dict, normalized_post: NormalizedPost):
    """Handle retweet by linking to original."""
    
    referenced = tweet.get('referenced_tweets', [])
    retweet_of = None
    
    for ref in referenced:
        if ref.get('type') == 'retweeted':
            retweet_of = ref.get('id')
            break
    
    if retweet_of:
        normalized_post.platform_data['is_retweet'] = True
        normalized_post.platform_data['retweet_of'] = retweet_of
        
        # Find original in our database
        original = db.query("""
            SELECT id FROM discovered_posts
            WHERE platform = 'twitter' AND platform_post_id = %s
        """, [retweet_of])
        
        if original:
            normalized_post.platform_data['original_post_id'] = original.id
```

### Deduplication Metrics

Track deduplication statistics:

```python
@dataclass
class DeduplicationStats:
    total_processed: int = 0
    new_posts: int = 0
    duplicates_same_source: int = 0
    duplicates_other_source: int = 0
    cross_platform_duplicates: int = 0
    retweets_skipped: int = 0
```

Log per ingestion job:
```python
def log_deduplication_stats(job_id: UUID, stats: DeduplicationStats):
    log.info(f"Job {job_id} deduplication: "
             f"processed={stats.total_processed}, "
             f"new={stats.new_posts}, "
             f"duplicates={stats.duplicates_same_source + stats.duplicates_other_source}, "
             f"cross_platform={stats.cross_platform_duplicates}")
```

## 7.2.9 Storage

### Database Schema

#### Posts Table

```sql
CREATE TABLE discovered_posts (
    -- Identity
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    platform VARCHAR(50) NOT NULL,
    platform_post_id VARCHAR(255) NOT NULL,
    
    -- Source tracking
    source_id UUID NOT NULL REFERENCES sources(id),
    campaign_id UUID NOT NULL REFERENCES campaigns(id),
    
    -- Content
    content_text TEXT NOT NULL,
    content_html TEXT,
    content_hash VARCHAR(16),
    language VARCHAR(10),
    
    -- Author reference
    author_id UUID REFERENCES discovered_authors(id),
    
    -- Engagement (JSONB for flexibility)
    engagement JSONB NOT NULL DEFAULT '{}',
    
    -- Media and links (JSONB arrays)
    media JSONB NOT NULL DEFAULT '[]',
    links JSONB NOT NULL DEFAULT '[]',
    entities JSONB NOT NULL DEFAULT '{}',
    
    -- Platform-specific data
    platform_data JSONB NOT NULL DEFAULT '{}',
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    discovered_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    -- Processing state
    status VARCHAR(50) NOT NULL DEFAULT 'discovered',
    
    -- Classification results (populated later)
    classification JSONB,
    classification_at TIMESTAMP WITH TIME ZONE,
    
    -- Scoring results (populated later)
    scores JSONB,
    priority_score DECIMAL(10, 4),
    scored_at TIMESTAMP WITH TIME ZONE,
    
    -- Queue state
    queued_at TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE,
    
    -- Processing outcome
    engaged_at TIMESTAMP WITH TIME ZONE,
    engagement_id UUID,
    filtered_at TIMESTAMP WITH TIME ZONE,
    filter_reason VARCHAR(100),
    
    -- Constraints
    CONSTRAINT posts_platform_id_unique UNIQUE (platform, platform_post_id)
);

-- Essential indexes
CREATE INDEX idx_posts_campaign_status ON discovered_posts(campaign_id, status);
CREATE INDEX idx_posts_campaign_priority ON discovered_posts(campaign_id, priority_score DESC NULLS LAST);
CREATE INDEX idx_posts_discovered_at ON discovered_posts(discovered_at DESC);
CREATE INDEX idx_posts_source ON discovered_posts(source_id);
CREATE INDEX idx_posts_author ON discovered_posts(author_id);
CREATE INDEX idx_posts_content_hash ON discovered_posts(content_hash);
CREATE INDEX idx_posts_expires_at ON discovered_posts(expires_at) WHERE expires_at IS NOT NULL;
CREATE INDEX idx_posts_platform ON discovered_posts(platform);
CREATE INDEX idx_posts_created_at ON discovered_posts(created_at DESC);

-- GIN index for JSONB searches
CREATE INDEX idx_posts_platform_data ON discovered_posts USING GIN (platform_data);
CREATE INDEX idx_posts_engagement ON discovered_posts USING GIN (engagement);
```

#### Authors Table

```sql
CREATE TABLE discovered_authors (
    -- Identity
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    platform VARCHAR(50) NOT NULL,
    platform_author_id VARCHAR(255) NOT NULL,
    
    -- Profile
    handle VARCHAR(255),
    display_name VARCHAR(255),
    avatar_url TEXT,
    bio TEXT,
    
    -- Metrics
    followers_count INTEGER,
    following_count INTEGER,
    posts_count INTEGER,
    verified BOOLEAN NOT NULL DEFAULT false,
    
    -- Account info
    account_created_at TIMESTAMP WITH TIME ZONE,
    
    -- Our tracking
    first_seen_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    last_seen_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    posts_discovered INTEGER NOT NULL DEFAULT 0,
    
    -- Calculated score
    author_score DECIMAL(5, 2),
    author_score_at TIMESTAMP WITH TIME ZONE,
    
    -- Relationship tracking
    engagement_count INTEGER NOT NULL DEFAULT 0,
    last_engaged_at TIMESTAMP WITH TIME ZONE,
    relationship_score DECIMAL(5, 2),
    
    -- Additional data
    metadata JSONB NOT NULL DEFAULT '{}',
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT authors_platform_id_unique UNIQUE (platform, platform_author_id)
);

-- Indexes
CREATE INDEX idx_authors_platform ON discovered_authors(platform);
CREATE INDEX idx_authors_handle ON discovered_authors(platform, handle);
CREATE INDEX idx_authors_followers ON discovered_authors(followers_count DESC NULLS LAST);
CREATE INDEX idx_authors_score ON discovered_authors(author_score DESC NULLS LAST);
```

#### Source Matches Table

```sql
CREATE TABLE post_source_matches (
    post_id UUID NOT NULL REFERENCES discovered_posts(id) ON DELETE CASCADE,
    source_id UUID NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    matched_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    PRIMARY KEY (post_id, source_id)
);

CREATE INDEX idx_source_matches_source ON post_source_matches(source_id);
```

#### Ingestion Jobs Table

```sql
CREATE TABLE ingestion_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id UUID NOT NULL REFERENCES sources(id),
    campaign_id UUID NOT NULL,
    
    -- Scheduling
    scheduled_for TIMESTAMP WITH TIME ZONE NOT NULL,
    priority VARCHAR(20) NOT NULL,
    
    -- Execution
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    
    -- State snapshot (for resumption)
    source_state JSONB,
    
    -- Results
    posts_found INTEGER,
    posts_new INTEGER,
    posts_duplicate INTEGER,
    api_calls INTEGER,
    
    -- Errors
    attempt INTEGER NOT NULL DEFAULT 1,
    max_attempts INTEGER NOT NULL DEFAULT 3,
    last_error TEXT,
    last_error_at TIMESTAMP WITH TIME ZONE,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_jobs_status ON ingestion_jobs(status);
CREATE INDEX idx_jobs_source ON ingestion_jobs(source_id);
CREATE INDEX idx_jobs_scheduled ON ingestion_jobs(scheduled_for) WHERE status = 'pending';
```

### Storage Operations

#### Insert Post

```python
def insert_post(post: NormalizedPost) -> UUID:
    """Insert normalized post into database."""
    
    # First, ensure author exists
    author_id = upsert_author(post.author)
    
    # Insert post
    result = db.execute("""
        INSERT INTO discovered_posts (
            id, platform, platform_post_id,
            source_id, campaign_id,
            content_text, content_html, content_hash, language,
            author_id, engagement, media, links, entities,
            platform_data, created_at, discovered_at, status
        ) VALUES (
            %(id)s, %(platform)s, %(platform_post_id)s,
            %(source_id)s, %(campaign_id)s,
            %(content_text)s, %(content_html)s, %(content_hash)s, %(language)s,
            %(author_id)s, %(engagement)s, %(media)s, %(links)s, %(entities)s,
            %(platform_data)s, %(created_at)s, %(discovered_at)s, %(status)s
        )
        RETURNING id
    """, {
        'id': post.id,
        'platform': post.platform,
        'platform_post_id': post.platform_post_id,
        'source_id': post.source_id,
        'campaign_id': post.campaign_id,
        'content_text': post.content_text,
        'content_html': post.content_html,
        'content_hash': content_hash(post.content_text),
        'language': post.language,
        'author_id': author_id,
        'engagement': json.dumps(asdict(post.engagement)),
        'media': json.dumps([asdict(m) for m in post.media]),
        'links': json.dumps(post.links),
        'entities': json.dumps(post.entities),
        'platform_data': json.dumps(post.platform_data),
        'created_at': post.created_at,
        'discovered_at': post.discovered_at,
        'status': post.status,
    })
    
    return result.id
```

#### Upsert Author

```python
def upsert_author(author: NormalizedAuthor) -> UUID:
    """Insert author or update if exists."""
    
    result = db.execute("""
        INSERT INTO discovered_authors (
            platform, platform_author_id,
            handle, display_name, avatar_url, bio,
            followers_count, following_count, verified, account_created_at,
            last_seen_at, posts_discovered
        ) VALUES (
            %(platform)s, %(platform_author_id)s,
            %(handle)s, %(display_name)s, %(avatar_url)s, %(bio)s,
            %(followers_count)s, %(following_count)s, %(verified)s, %(account_created_at)s,
            NOW(), 1
        )
        ON CONFLICT (platform, platform_author_id) DO UPDATE SET
            handle = COALESCE(EXCLUDED.handle, discovered_authors.handle),
            display_name = COALESCE(EXCLUDED.display_name, discovered_authors.display_name),
            avatar_url = COALESCE(EXCLUDED.avatar_url, discovered_authors.avatar_url),
            bio = COALESCE(EXCLUDED.bio, discovered_authors.bio),
            followers_count = COALESCE(EXCLUDED.followers_count, discovered_authors.followers_count),
            following_count = COALESCE(EXCLUDED.following_count, discovered_authors.following_count),
            verified = COALESCE(EXCLUDED.verified, discovered_authors.verified),
            last_seen_at = NOW(),
            posts_discovered = discovered_authors.posts_discovered + 1,
            updated_at = NOW()
        RETURNING id
    """, {
        'platform': author.platform,
        'platform_author_id': author.platform_author_id,
        'handle': author.handle,
        'display_name': author.display_name,
        'avatar_url': author.avatar_url,
        'bio': author.bio,
        'followers_count': author.followers_count,
        'following_count': author.following_count,
        'verified': author.verified,
        'account_created_at': author.account_created_at,
    })
    
    return result.id
```

#### Batch Insert

For efficiency, batch insert multiple posts:

```python
def batch_insert_posts(posts: List[NormalizedPost]) -> int:
    """Batch insert posts. Return count of new posts inserted."""
    
    if not posts:
        return 0
    
    # Prepare batch
    values = []
    for post in posts:
        author_id = upsert_author(post.author)
        values.append({
            'id': post.id,
            'platform': post.platform,
            'platform_post_id': post.platform_post_id,
            # ... all fields
        })
    
    # Use execute_values for efficient batch insert
    from psycopg2.extras import execute_values
    
    result = execute_values(
        cursor,
        """
        INSERT INTO discovered_posts (id, platform, platform_post_id, ...)
        VALUES %s
        ON CONFLICT (platform, platform_post_id) DO NOTHING
        RETURNING id
        """,
        values,
        template="(%(id)s, %(platform)s, %(platform_post_id)s, ...)"
    )
    
    return len(result)
```

### Data Retention

#### Retention Policy

| Data Type | Retention | Rationale |
|-----------|-----------|-----------|
| Active posts (pending/queued) | Indefinite | Currently processing |
| Engaged posts | 90 days | Analytics and history |
| Filtered posts | 30 days | Debugging and tuning |
| Expired posts | 7 days | Short-term reference |
| Authors | Indefinite | Relationship tracking |
| Ingestion jobs | 30 days | Debugging |

#### Cleanup Jobs

```python
def cleanup_old_posts():
    """Remove old posts based on retention policy."""
    
    # Delete expired posts older than 7 days
    db.execute("""
        DELETE FROM discovered_posts
        WHERE status = 'expired'
        AND expires_at < NOW() - INTERVAL '7 days'
    """)
    
    # Delete filtered posts older than 30 days
    db.execute("""
        DELETE FROM discovered_posts
        WHERE status = 'filtered'
        AND filtered_at < NOW() - INTERVAL '30 days'
    """)
    
    # Archive engaged posts older than 90 days (move to archive table)
    db.execute("""
        INSERT INTO discovered_posts_archive
        SELECT * FROM discovered_posts
        WHERE status = 'engaged'
        AND engaged_at < NOW() - INTERVAL '90 days'
    """)
    
    db.execute("""
        DELETE FROM discovered_posts
        WHERE status = 'engaged'
        AND engaged_at < NOW() - INTERVAL '90 days'
    """)
```

## 7.2.10 State Management

### Source State Tracking

Track ingestion state per source:

```sql
CREATE TABLE source_ingestion_state (
    source_id UUID PRIMARY KEY REFERENCES sources(id),
    
    -- Polling state
    last_polled_at TIMESTAMP WITH TIME ZONE,
    last_successful_at TIMESTAMP WITH TIME ZONE,
    next_poll_at TIMESTAMP WITH TIME ZONE,
    
    -- Pagination state
    last_post_id VARCHAR(255),
    last_post_at TIMESTAMP WITH TIME ZONE,
    pagination_cursor TEXT,
    
    -- Error tracking
    consecutive_failures INTEGER NOT NULL DEFAULT 0,
    last_error TEXT,
    last_error_at TIMESTAMP WITH TIME ZONE,
    
    -- Daily counters
    posts_discovered_today INTEGER NOT NULL DEFAULT 0,
    posts_new_today INTEGER NOT NULL DEFAULT 0,
    today_date DATE NOT NULL DEFAULT CURRENT_DATE,
    
    -- Totals
    posts_discovered_total BIGINT NOT NULL DEFAULT 0,
    posts_new_total BIGINT NOT NULL DEFAULT 0,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
```

### State Update Operations

#### After Successful Poll

```python
def update_state_after_success(
    source_id: UUID,
    posts_found: int,
    posts_new: int,
    newest_post_id: Optional[str],
    newest_post_at: Optional[datetime],
    pagination_cursor: Optional[str]
):
    """Update source state after successful poll."""
    
    now = datetime.now(timezone.utc)
    today = now.date()
    
    db.execute("""
        UPDATE source_ingestion_state SET
            last_polled_at = %(now)s,
            last_successful_at = %(now)s,
            next_poll_at = %(now)s + (
                SELECT polling_interval_minutes * INTERVAL '1 minute'
                FROM sources WHERE id = %(source_id)s
            ),
            
            last_post_id = COALESCE(%(newest_post_id)s, last_post_id),
            last_post_at = COALESCE(%(newest_post_at)s, last_post_at),
            pagination_cursor = %(pagination_cursor)s,
            
            consecutive_failures = 0,
            last_error = NULL,
            last_error_at = NULL,
            
            -- Update daily counters (reset if new day)
            posts_discovered_today = CASE 
                WHEN today_date = %(today)s THEN posts_discovered_today + %(posts_found)s
                ELSE %(posts_found)s
            END,
            posts_new_today = CASE
                WHEN today_date = %(today)s THEN posts_new_today + %(posts_new)s
                ELSE %(posts_new)s
            END,
            today_date = %(today)s,
            
            -- Update totals
            posts_discovered_total = posts_discovered_total + %(posts_found)s,
            posts_new_total = posts_new_total + %(posts_new)s,
            
            updated_at = %(now)s
        WHERE source_id = %(source_id)s
    """, {
        'source_id': source_id,
        'now': now,
        'today': today,
        'posts_found': posts_found,
        'posts_new': posts_new,
        'newest_post_id': newest_post_id,
        'newest_post_at': newest_post_at,
        'pagination_cursor': pagination_cursor,
    })
```

#### After Failed Poll

```python
def update_state_after_failure(source_id: UUID, error: str):
    """Update source state after failed poll."""
    
    now = datetime.now(timezone.utc)
    
    # Calculate backoff for next poll
    state = get_source_state(source_id)
    failures = state.consecutive_failures + 1
    backoff_minutes = min(60, 2 ** failures)  # Exponential, max 1 hour
    
    db.execute("""
        UPDATE source_ingestion_state SET
            last_polled_at = %(now)s,
            next_poll_at = %(now)s + %(backoff)s * INTERVAL '1 minute',
            
            consecutive_failures = consecutive_failures + 1,
            last_error = %(error)s,
            last_error_at = %(now)s,
            
            updated_at = %(now)s
        WHERE source_id = %(source_id)s
    """, {
        'source_id': source_id,
        'now': now,
        'backoff': backoff_minutes,
        'error': error,
    })
```

### State Recovery

#### Resuming After Pagination

If a poll is interrupted mid-pagination:

```python
def resume_from_state(source_id: UUID) -> dict:
    """Get resumption parameters from state."""
    
    state = get_source_state(source_id)
    
    params = {}
    
    # If we have a pagination cursor, use it
    if state.pagination_cursor:
        params['pagination_token'] = state.pagination_cursor
    
    # Otherwise, use since_id to get only new posts
    elif state.last_post_id:
        params['since_id'] = state.last_post_id
    
    return params
```

#### State Reset

If state is corrupted or needs reset:

```python
def reset_source_state(source_id: UUID, reset_to: datetime = None):
    """Reset source state."""
    
    db.execute("""
        UPDATE source_ingestion_state SET
            last_post_id = NULL,
            last_post_at = %(reset_to)s,
            pagination_cursor = NULL,
            consecutive_failures = 0,
            last_error = NULL,
            last_error_at = NULL,
            updated_at = NOW()
        WHERE source_id = %(source_id)s
    """, {
        'source_id': source_id,
        'reset_to': reset_to or datetime.now(timezone.utc) - timedelta(hours=24),
    })
```

## 7.2.11 Handoff to Classification

### Marking Posts Ready

After storage, posts need classification:

```python
def mark_posts_for_classification(post_ids: List[UUID]):
    """Mark posts as ready for classification."""
    
    db.execute("""
        UPDATE discovered_posts
        SET status = 'pending_classification',
            updated_at = NOW()
        WHERE id = ANY(%(post_ids)s)
        AND status = 'discovered'
    """, {'post_ids': post_ids})
```

### Handoff Mechanisms

#### Option A: Database Polling

Classification service polls for posts with status = 'pending_classification':

```python
def get_posts_for_classification(limit: int = 100) -> List[Post]:
    """Get posts pending classification."""
    
    return db.query("""
        SELECT * FROM discovered_posts
        WHERE status = 'pending_classification'
        ORDER BY discovered_at ASC
        LIMIT %(limit)s
        FOR UPDATE SKIP LOCKED
    """, {'limit': limit})
```

**Pros:** Simple, no additional infrastructure
**Cons:** Polling latency, database load

#### Option B: Message Queue

Push post IDs to classification queue:

```python
def queue_posts_for_classification(post_ids: List[UUID]):
    """Push posts to classification queue."""
    
    for post_id in post_ids:
        redis.lpush('classification:queue', str(post_id))
    
    # Also update status
    mark_posts_for_classification(post_ids)
```

Classification worker pulls from queue:

```python
def classification_worker():
    while True:
        post_id = redis.brpop('classification:queue', timeout=30)
        if post_id:
            classify_post(UUID(post_id))
```

**Pros:** Lower latency, better scaling
**Cons:** Additional infrastructure

#### Option C: Batch with Callback

Ingestion batches posts and calls classification directly:

```python
def handoff_batch_to_classification(posts: List[NormalizedPost]):
    """Hand off batch to classification service."""
    
    post_ids = [p.id for p in posts]
    
    # Call classification service
    classification_service.classify_batch(post_ids)
    
    # Update status
    db.execute("""
        UPDATE discovered_posts
        SET status = 'pending_classification'
        WHERE id = ANY(%(post_ids)s)
    """, {'post_ids': post_ids})
```

### Handoff Data

What classification receives:

```python
@dataclass
class ClassificationInput:
    post_id: UUID
    content_text: str
    platform: str
    author_handle: Optional[str]
    author_bio: Optional[str]
    engagement: EngagementMetrics
    platform_data: Dict[str, Any]
```

Minimal data needed for classification. Full post remains in database.

## 7.2.12 Monitoring and Metrics

### Ingestion Metrics

#### Volume Metrics

```python
# Counter: Total posts ingested
ingestion_posts_total = Counter(
    'ingestion_posts_total',
    'Total posts ingested',
    ['platform', 'source_type', 'result']  # result: new, duplicate, error
)

# Gauge: Posts ingested in last hour
ingestion_posts_hourly = Gauge(
    'ingestion_posts_hourly',
    'Posts ingested in last hour',
    ['platform']
)

# Counter: API calls made
ingestion_api_calls_total = Counter(
    'ingestion_api_calls_total',
    'Total API calls',
    ['platform', 'endpoint', 'status']
)
```

#### Performance Metrics

```python
# Histogram: Job duration
ingestion_job_duration_seconds = Histogram(
    'ingestion_job_duration_seconds',
    'Ingestion job duration',
    ['platform', 'source_type'],
    buckets=[0.5, 1, 2, 5, 10, 30, 60, 120]
)

# Histogram: API request latency
ingestion_api_latency_seconds = Histogram(
    'ingestion_api_latency_seconds',
    'API request latency',
    ['platform', 'endpoint'],
    buckets=[0.1, 0.25, 0.5, 1, 2, 5, 10, 30]
)

# Histogram: Posts per API call
ingestion_posts_per_call = Histogram(
    'ingestion_posts_per_call',
    'Posts returned per API call',
    ['platform', 'endpoint'],
    buckets=[0, 1, 5, 10, 25, 50, 100]
)
```

#### Error Metrics

```python
# Counter: Errors by type
ingestion_errors_total = Counter(
    'ingestion_errors_total',
    'Ingestion errors',
    ['platform', 'error_type']  # rate_limit, auth, network, parse, etc.
)

# Counter: Rate limit hits
ingestion_rate_limits_total = Counter(
    'ingestion_rate_limits_total',
    'Rate limit hits',
    ['platform', 'endpoint']
)

# Gauge: Consecutive failures by source
ingestion_source_failures = Gauge(
    'ingestion_source_failures',
    'Consecutive failures',
    ['source_id']
)
```

#### Queue Metrics

```python
# Gauge: Job queue depth
ingestion_job_queue_depth = Gauge(
    'ingestion_job_queue_depth',
    'Pending ingestion jobs',
    ['priority']
)

# Histogram: Job queue wait time
ingestion_job_wait_seconds = Histogram(
    'ingestion_job_wait_seconds',
    'Time job spent in queue',
    ['priority'],
    buckets=[1, 5, 10, 30, 60, 120, 300]
)
```

### Health Checks

```python
def check_ingestion_health() -> HealthStatus:
    """Check overall ingestion health."""
    
    checks = []
    
    # Check job queue
    queue_depth = get_job_queue_depth()
    if queue_depth > 1000:
        checks.append(('job_queue', 'warning', f'Queue depth: {queue_depth}'))
    else:
        checks.append(('job_queue', 'healthy', f'Queue depth: {queue_depth}'))
    
    # Check recent job success rate
    recent_jobs = get_recent_jobs(hours=1)
    success_rate = sum(1 for j in recent_jobs if j.status == 'completed') / len(recent_jobs)
    if success_rate < 0.9:
        checks.append(('job_success', 'warning', f'Success rate: {success_rate:.1%}'))
    else:
        checks.append(('job_success', 'healthy', f'Success rate: {success_rate:.1%}'))
    
    # Check rate limits
    for platform in ['twitter', 'reddit', 'linkedin']:
        remaining = get_rate_limit_remaining(platform)
        if remaining < 10:
            checks.append((f'{platform}_rate_limit', 'warning', f'Remaining: {remaining}'))
        else:
            checks.append((f'{platform}_rate_limit', 'healthy', f'Remaining: {remaining}'))
    
    # Check source health
    unhealthy_sources = get_sources_with_failures(min_failures=3)
    if unhealthy_sources:
        checks.append(('sources', 'warning', f'{len(unhealthy_sources)} sources failing'))
    else:
        checks.append(('sources', 'healthy', 'All sources healthy'))
    
    # Aggregate
    has_critical = any(c[1] == 'critical' for c in checks)
    has_warning = any(c[1] == 'warning' for c in checks)
    
    overall = 'critical' if has_critical else ('warning' if has_warning else 'healthy')
    
    return HealthStatus(overall=overall, checks=checks)
```

### Alerting Rules

#### Critical Alerts

```yaml
# No ingestion for 15 minutes
- alert: IngestionStopped
  expr: rate(ingestion_posts_total[15m]) == 0
  for: 15m
  labels:
    severity: critical
  annotations:
    summary: "Ingestion has stopped"
    description: "No posts ingested in 15 minutes"

# Auth failure
- alert: IngestionAuthFailure
  expr: increase(ingestion_errors_total{error_type="auth"}[5m]) > 5
  for: 5m
  labels:
    severity: critical
  annotations:
    summary: "Authentication failures"
    description: "{{ $value }} auth failures in 5 minutes"
```

#### Warning Alerts

```yaml
# High error rate
- alert: IngestionHighErrorRate
  expr: rate(ingestion_errors_total[10m]) / rate(ingestion_api_calls_total[10m]) > 0.1
  for: 10m
  labels:
    severity: warning
  annotations:
    summary: "High ingestion error rate"
    description: "Error rate is {{ $value | humanizePercentage }}"

# Rate limits
- alert: IngestionRateLimited
  expr: ingestion_rate_limits_total > 0
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "Rate limiting occurring"
    description: "Platform {{ $labels.platform }} is rate limiting"

# Source failures
- alert: SourceConsecutiveFailures
  expr: ingestion_source_failures > 5
  for: 30m
  labels:
    severity: warning
  annotations:
    summary: "Source failing repeatedly"
    description: "Source {{ $labels.source_id }} has {{ $value }} consecutive failures"
```

## 7.2.13 Error Recovery

### Transient Error Recovery

#### Retry Strategy

```python
class RetryStrategy:
    def __init__(
        self,
        max_retries: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True
    ):
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
    
    def get_delay(self, attempt: int) -> float:
        delay = self.initial_delay * (self.exponential_base ** attempt)
        delay = min(delay, self.max_delay)
        
        if self.jitter:
            delay = delay * (0.5 + random.random())
        
        return delay
    
    def should_retry(self, attempt: int, error: Exception) -> bool:
        if attempt >= self.max_retries:
            return False
        
        # Retry on specific errors
        if isinstance(error, RateLimitError):
            return True
        if isinstance(error, NetworkError):
            return True
        if isinstance(error, ServerError):
            return True
        
        # Don't retry on client errors (bad request, etc.)
        if isinstance(error, ClientError):
            return False
        
        return False
```

#### Circuit Breaker

```python
class CircuitBreaker:
    def __init__(
        self,
        failure_threshold: int = 5,
        success_threshold: int = 2,
        timeout: float = 60.0
    ):
        self.failure_threshold = failure_threshold
        self.success_threshold = success_threshold
        self.timeout = timeout
        
        self.state = 'closed'  # closed, open, half-open
        self.failures = 0
        self.successes = 0
        self.last_failure_time = None
    
    def record_success(self):
        if self.state == 'half-open':
            self.successes += 1
            if self.successes >= self.success_threshold:
                self.state = 'closed'
                self.failures = 0
                self.successes = 0
        else:
            self.failures = 0
    
    def record_failure(self):
        self.failures += 1
        self.last_failure_time = time.time()
        
        if self.failures >= self.failure_threshold:
            self.state = 'open'
    
    def can_execute(self) -> bool:
        if self.state == 'closed':
            return True
        
        if self.state == 'open':
            if time.time() - self.last_failure_time > self.timeout:
                self.state = 'half-open'
                self.successes = 0
                return True
            return False
        
        # half-open: allow limited requests
        return True
```

### Permanent Error Recovery

#### Configuration Errors

```python
def handle_config_error(source_id: UUID, error: str):
    """Handle permanent configuration errors."""
    
    # Disable source
    db.execute("""
        UPDATE sources SET enabled = false WHERE id = %(source_id)s
    """, {'source_id': source_id})
    
    # Log and notify
    log.error(f"Source {source_id} disabled due to config error: {error}")
    
    # Send notification
    notify_user(
        source_id=source_id,
        message=f"Source disabled: {error}. Please check configuration.",
        severity='error'
    )
```

#### Auth Errors

```python
def handle_auth_error(platform: str, error: str):
    """Handle authentication errors."""
    
    log.error(f"Auth error for {platform}: {error}")
    
    # Try to refresh token
    if can_refresh_token(platform):
        try:
            refresh_token(platform)
            log.info(f"Token refreshed for {platform}")
            return True
        except Exception as e:
            log.error(f"Token refresh failed for {platform}: {e}")
    
    # Disable all sources for this platform temporarily
    db.execute("""
        UPDATE sources 
        SET enabled = false, 
            metadata = metadata || '{"disabled_reason": "auth_error"}'
        WHERE platform = %(platform)s
    """, {'platform': platform})
    
    # Notify admin
    notify_admin(
        message=f"Auth error for {platform}. All sources disabled. Re-authentication required.",
        severity='critical'
    )
    
    return False
```

### Data Recovery

#### Re-ingestion

```python
def reingest_source(source_id: UUID, since: datetime):
    """Re-ingest posts from source since given time."""
    
    # Reset state to start from specified time
    db.execute("""
        UPDATE source_ingestion_state SET
            last_post_id = NULL,
            last_post_at = %(since)s,
            pagination_cursor = NULL
        WHERE source_id = %(source_id)s
    """, {'source_id': source_id, 'since': since})
    
    # Create immediate job
    create_ingestion_job(source_id, priority='high', immediate=True)
    
    log.info(f"Re-ingestion triggered for source {source_id} since {since}")
```

## 7.2.14 Performance Optimization

### Efficient Polling

#### Request Optimization

```python
# Only request needed fields (Twitter example)
TWEET_FIELDS = 'author_id,created_at,public_metrics,entities'
USER_FIELDS = 'name,username,verified,public_metrics'
EXPANSIONS = 'author_id'

# Use since_id to get only new posts
params = {
    'query': query,
    'max_results': 100,
    'tweet.fields': TWEET_FIELDS,
    'user.fields': USER_FIELDS,
    'expansions': EXPANSIONS,
    'since_id': last_post_id,  # Only new posts
}
```

#### Batch API Calls

Some platforms support batch operations:

```python
# Twitter: Get multiple users in one call
user_ids = ['123', '456', '789']
response = api.get_users(ids=','.join(user_ids))

# Instead of:
for user_id in user_ids:
    api.get_user(id=user_id)  # 3 API calls vs 1
```

### Efficient Storage

#### Batch Inserts

```python
def batch_insert_posts(posts: List[NormalizedPost], batch_size: int = 100):
    """Insert posts in batches for efficiency."""
    
    for i in range(0, len(posts), batch_size):
        batch = posts[i:i + batch_size]
        
        # Single transaction for batch
        with db.transaction():
            for post in batch:
                insert_post(post)
```

#### Async Writes

```python
async def async_store_posts(posts: List[NormalizedPost]):
    """Store posts asynchronously."""
    
    # Queue for background write
    for post in posts:
        await storage_queue.put(post)
    
    # Don't block on storage completion
    return len(posts)


async def storage_worker():
    """Background worker for storage."""
    
    batch = []
    while True:
        try:
            post = await asyncio.wait_for(storage_queue.get(), timeout=1.0)
            batch.append(post)
            
            if len(batch) >= 100:
                await batch_insert_posts(batch)
                batch = []
        
        except asyncio.TimeoutError:
            # Flush partial batch
            if batch:
                await batch_insert_posts(batch)
                batch = []
```

### Caching

#### Author Cache

```python
# Cache author data to avoid repeated lookups
author_cache = {}  # In production, use Redis

def get_or_create_author(author: NormalizedAuthor) -> UUID:
    cache_key = f"{author.platform}:{author.platform_author_id}"
    
    # Check cache
    if cache_key in author_cache:
        cached = author_cache[cache_key]
        if time.time() - cached['time'] < 3600:  # 1 hour TTL
            return cached['id']
    
    # Upsert and cache
    author_id = upsert_author(author)
    author_cache[cache_key] = {'id': author_id, 'time': time.time()}
    
    return author_id
```

#### Rate Limit Cache

```python
# Cache rate limit state in memory
rate_limit_cache = {}

def check_rate_limit(platform: str, endpoint: str) -> bool:
    cache_key = f"{platform}:{endpoint}"
    
    if cache_key in rate_limit_cache:
        state = rate_limit_cache[cache_key]
        if state['remaining'] > 0:
            return True
        if time.time() > state['reset_at']:
            return True  # Reset has passed
        return False  # Rate limited
    
    return True  # No cached state, allow
```

#### Deduplication Cache

```python
# Bloom filter for fast duplicate check
from pybloom_live import BloomFilter

dedup_filter = BloomFilter(capacity=1000000, error_rate=0.001)

def quick_duplicate_check(platform: str, platform_post_id: str) -> bool:
    """Fast probabilistic duplicate check."""
    key = f"{platform}:{platform_post_id}"
    
    if key in dedup_filter:
        return True  # Probably duplicate (check DB to confirm)
    
    return False  # Definitely not duplicate
```

### Connection Pooling

```python
# Database connection pool
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=1800,
)

# HTTP connection pool for API calls
import httpx

http_client = httpx.Client(
    limits=httpx.Limits(
        max_keepalive_connections=20,
        max_connections=100,
        keepalive_expiry=30,
    ),
    timeout=httpx.Timeout(30.0, connect=10.0),
)
```

## 7.2.15 Implementation Guidance for Neoclaw

### Implementation Order

1. **Build for one platform first (Twitter)**
   - API client with auth
   - Rate limit tracking
   - Response parsing
   - Normalization
   - Storage
   - Prove the full pipeline works

2. **Add job scheduling**
   - Job queue (Redis or database)
   - Scheduler loop
   - Priority handling
   - Concurrency control

3. **Implement state management**
   - Source state table
   - State updates on success/failure
   - Pagination handling
   - Recovery from failures

4. **Add deduplication**
   - Platform + post_id uniqueness
   - Source match tracking
   - Engagement updates on duplicate

5. **Build monitoring**
   - Metrics collection
   - Health checks
   - Alerting rules

6. **Add remaining platforms**
   - Reddit (similar to Twitter)
   - LinkedIn (more complex, limited API)
   - Discord (if needed)

7. **Optimize**
   - Batch operations
   - Caching
   - Connection pooling
   - Async where beneficial

### Testing Checklist

#### Unit Tests
- [ ] Twitter response parsing (various response types)
- [ ] Reddit response parsing
- [ ] LinkedIn response parsing
- [ ] Timestamp normalization (all formats)
- [ ] Text normalization
- [ ] Count normalization
- [ ] Deduplication logic
- [ ] State update logic
- [ ] Retry strategy
- [ ] Circuit breaker

#### Integration Tests
- [ ] Full ingestion flow (mock API → stored posts)
- [ ] Pagination handling
- [ ] Rate limit handling
- [ ] Error recovery
- [ ] State persistence and resumption

#### Load Tests
- [ ] Concurrent ingestion jobs
- [ ] High volume storage
- [ ] Rate limit behavior under load

### Common Pitfalls

**Token expiration:**
Tokens expire. Implement proactive refresh, not reactive.

**Rate limit calculation:**
Don't just track your calls. Parse and trust the rate limit headers.

**Pagination state:**
Store cursor state. If ingestion restarts, resume from cursor.

**Timezone handling:**
Always normalize to UTC. Platform times vary.

**Error swallowing:**
Log all errors with context. Silent failures are debugging nightmares.

**Database connections:**
Use connection pooling. Don't open new connections per request.

**Memory leaks:**
Large batches accumulate memory. Process and release in chunks.

---

**END OF SECTION 7.2**

Section 7.3 continues with Content Classification specification.
-e 


# SECTION 7.3: CONTENT CLASSIFICATION

## 7.3.1 What Content Classification Is

### The Core Concept

Content Classification is the process of determining what type of post each piece of discovered content represents. Classification assigns categorical labels that describe the nature, topic, and intent of the content.

**Input:** Normalized posts from ingestion (Section 7.2)
**Output:** Posts with classification labels and confidence scores

Classification answers the question: "What kind of post is this?"

**Examples:**
- A question about agent security → `help_seeking_solution`
- A joke about AI agents → `meme_humor`
- An opinion about industry trends → `industry_commentary`
- A technical discussion about RAG → `tech_discussion`

### Why Classification Matters

Classification is the bridge between raw content and strategic action:

**Drives persona selection:**
Each classification has different persona suggestion weights. A `tech_discussion` post suggests Advisor persona. A `meme_humor` post suggests Observer persona.

**Affects scoring:**
Classification feeds into goal alignment multipliers. A `help_seeking_solution` post gets 1.5× boost for Conversions goal.

**Informs response style:**
Classification tells generation what kind of response is appropriate. Technical questions need technical answers. Jokes need wit.

**Enables filtering:**
Some classifications trigger safety review. `controversial_topic` gets extra scrutiny.

**Powers analytics:**
Understanding what types of content Jen engages with, and how successfully.

### Classification vs Topic Extraction

**Classification:** Categorical label for post type/intent
- "This is a help-seeking post"
- "This is a meme"
- Finite set of categories
- Drives system behavior

**Topic extraction:** What specific subjects the post discusses
- "This post discusses RAG, vector databases, and embeddings"
- Open-ended extraction
- Used for context retrieval

Classification is about post TYPE. Topic extraction is about post CONTENT. Both are useful, but classification is what drives the pipeline.

### The Classification Challenge

Classification is challenging because:

**Ambiguity:** Posts often have multiple valid classifications
- "Anyone know a good agent security tool? This space is such a mess 😂"
- Is this `help_seeking_solution`, `pain_point_match`, or `meme_humor`?

**Context dependency:** Same words mean different things in different contexts
- "This is sick" — Positive (slang) or negative (illness)?
- Platform norms affect interpretation

**Subtlety:** Intent isn't always explicit
- "I've been debugging this agent for three days..."
- Explicit: sharing experience
- Implicit: frustration, possible help-seeking

**Volume:** Must classify thousands of posts per day
- Speed matters
- Cost matters (if using LLM)

## 7.3.2 The Classification Taxonomy

### Taxonomy Overview

The classification taxonomy defines all possible categories. Jen uses 13 primary classifications organized into 4 groups:

**Domain-Relevant (High Value):**
- `tech_discussion`
- `security_discussion`
- `agent_discussion`
- `ai_discussion`
- `help_seeking_solution`
- `pain_point_match`

**Industry (Medium Value):**
- `industry_commentary`
- `industry_news`
- `competitor_mention`

**Engagement (Variable Value):**
- `meme_humor`
- `general_engagement`

**Caution (Low/Negative Value):**
- `controversial_topic`
- `off_topic`

### Classification Definitions

---

#### tech_discussion

**Definition:**
Technical discussion about software development, system architecture, code implementation, or engineering practices. Content is substantively technical in nature.

**Key signals:**
- Technical terminology (API, database, deployment, architecture, etc.)
- Code snippets or pseudocode
- System design discussions
- Tool or framework comparisons
- Technical problem-solving
- Performance or optimization discussions

**Example posts:**
```
"What's the best way to implement RAG with pgvector? I'm seeing latency issues with large document sets."

"Comparing async vs sync approaches for agent tool calls. Async seems faster but debugging is a nightmare."

"Our deployment pipeline for ML models: Kubernetes + Argo + MLflow. Works great once you get past the initial setup pain."
```

**Persona suggestion weights:**
- Observer: 20%
- Advisor: 60%
- Connector: 20%

**Goal alignment:**
- Thought Leadership: 1.35×
- Brand Awareness: 0.90×
- Conversions: 1.10×
- Community Building: 1.15×

**Response guidance:**
Demonstrate technical expertise. Add value through insights. Avoid promotional language.

---

#### security_discussion

**Definition:**
Discussion specifically about security, safety, risk mitigation, protection mechanisms, or threat models. Focus on keeping systems, data, or users safe.

**Key signals:**
- Security terminology (vulnerability, threat, attack, protection, encryption)
- Risk or safety discussions
- Compliance mentions (SOC2, GDPR, HIPAA)
- Incident or breach discussions
- Security tool or practice discussions
- Trust and verification topics

**Example posts:**
```
"Worried about prompt injection attacks on our agent. Anyone implemented good defenses?"

"How do you handle API key rotation for LLM calls in production? Current approach feels fragile."

"Our security team wants to audit the agent's actions before they execute. Looking for patterns."
```

**Persona suggestion weights:**
- Observer: 10%
- Advisor: 50%
- Connector: 40%

**Goal alignment:**
- Thought Leadership: 1.40×
- Brand Awareness: 0.85×
- Conversions: 1.45×
- Community Building: 1.10×

**Response guidance:**
This is core domain. Demonstrate deep expertise. Can mention product if genuinely relevant. Be helpful first.

---

#### agent_discussion

**Definition:**
Discussion specifically about AI agents, autonomous systems, agentic AI, multi-agent systems, or agent behavior. The focus is on agents as a distinct concept from general AI/ML.

**Key signals:**
- Agent terminology (agent, autonomous, agentic, multi-agent)
- Tool use or function calling discussions
- Agent framework mentions (LangChain, AutoGPT, CrewAI, etc.)
- Agent behavior, control, or debugging
- Agent orchestration or coordination
- Agent capabilities or limitations

**Example posts:**
```
"My agent keeps calling tools in unexpected combinations. The emergent behavior is fascinating but scary."

"Building a multi-agent system for customer support. The handoff between agents is tricky."

"LangChain vs CrewAI vs AutoGen for agent orchestration? Need something production-ready."
```

**Persona suggestion weights:**
- Observer: 15%
- Advisor: 45%
- Connector: 40%

**Goal alignment:**
- Thought Leadership: 1.45×
- Brand Awareness: 0.90×
- Conversions: 1.40×
- Community Building: 1.15×

**Response guidance:**
Direct domain relevance. Strong opportunity for expertise and product positioning. Lead with value.

---

#### ai_discussion

**Definition:**
Broader AI and machine learning discussion that isn't specifically about agents. General AI topics, models, training, inference, or capabilities.

**Key signals:**
- AI/ML terminology without agent focus
- Model discussions (GPT, Claude, Llama, etc.)
- Training or fine-tuning topics
- Inference or deployment topics
- AI capabilities or limitations (general)
- AI ethics or societal impact

**Example posts:**
```
"The new GPT model is impressive but the cost per token is getting ridiculous."

"Fine-tuning vs RAG for domain knowledge? We tried both and RAG won for our use case."

"How do you handle LLM hallucinations in production? Our fact-checking layer catches most but not all."
```

**Persona suggestion weights:**
- Observer: 30%
- Advisor: 50%
- Connector: 20%

**Goal alignment:**
- Thought Leadership: 1.25×
- Brand Awareness: 1.00×
- Conversions: 0.90×
- Community Building: 1.10×

**Response guidance:**
Adjacent domain. Good for thought leadership. Less direct product connection. Focus on expertise.

---

#### help_seeking_solution

**Definition:**
User actively seeking help with a problem. Clear request for assistance, recommendations, or solutions. Explicit help-seeking intent.

**Key signals:**
- Question format
- Request language ("looking for", "need help", "any recommendations")
- Problem statement followed by question
- "How do I..." patterns
- Explicit requests for tools, resources, or advice
- Tags like [Help] or [Question]

**Example posts:**
```
"How do I prevent my agent from going rogue? Looking for practical approaches."

"Anyone have recommendations for agent monitoring tools? Need visibility into what our agents are doing."

"Help! My LangChain agent is making API calls I didn't authorize. How do I debug this?"
```

**Persona suggestion weights:**
- Observer: 10%
- Advisor: 30%
- Connector: 60%

**Goal alignment:**
- Thought Leadership: 1.10×
- Brand Awareness: 0.75×
- Conversions: 1.50×
- Community Building: 1.20×

**Response guidance:**
Highest conversion opportunity. Be genuinely helpful. Solve their problem. Product mention if relevant, but value first.

---

#### pain_point_match

**Definition:**
User expressing frustration, difficulty, or challenges with a problem in Jen's domain. Not explicitly seeking help, but describing pain that the product might address.

**Key signals:**
- Frustration language ("so frustrated", "hate when", "why is it so hard")
- Problem description without explicit question
- Venting or complaining
- Describing failures or struggles
- Implicit dissatisfaction

**Example posts:**
```
"Spent 3 days debugging agent behavior. Why is this so hard?"

"Our agent keeps doing things we didn't expect. The unpredictability is killing our launch timeline."

"I love AI agents in theory but in practice they're a nightmare to control."
```

**Persona suggestion weights:**
- Observer: 15%
- Advisor: 35%
- Connector: 50%

**Goal alignment:**
- Thought Leadership: 1.05×
- Brand Awareness: 0.80×
- Conversions: 1.40×
- Community Building: 1.15×

**Response guidance:**
Empathize first. Validate the frustration. Offer helpful perspective or solution. Less pushy than help_seeking.

---

#### industry_commentary

**Definition:**
Opinion, analysis, or commentary about industry trends, market direction, or the state of the field. Thought leadership opportunity.

**Key signals:**
- Opinion language ("I think", "in my view", "hot take")
- Trend analysis or predictions
- Commentary on industry direction
- Analysis of market dynamics
- Broader perspective on the field

**Example posts:**
```
"Hot take: Agent security will be bigger than LLM security within 2 years."

"The AI industry is moving too fast for safety to keep up. We need to slow down."

"My prediction: By 2026, every enterprise will have an AI agent strategy or be obsolete."
```

**Persona suggestion weights:**
- Observer: 25%
- Advisor: 55%
- Connector: 20%

**Goal alignment:**
- Thought Leadership: 1.40×
- Brand Awareness: 1.15×
- Conversions: 0.80×
- Community Building: 1.05×

**Response guidance:**
Engage thoughtfully. Share perspective. Add nuance or supporting evidence. Don't be promotional.

---

#### industry_news

**Definition:**
News or announcements about companies, products, events, funding, or developments in the AI/tech industry.

**Key signals:**
- News format or announcement language
- Company or product launches
- Funding news
- Acquisition or partnership announcements
- Event coverage or recaps
- Release notes or updates

**Example posts:**
```
"Anthropic just announced Claude 3.5 Sonnet. Initial benchmarks look impressive."

"OpenAI raising another round at $150B valuation. The AI gold rush continues."

"NeurIPS 2024 keynote highlights: agents, safety, and scaling were the big themes."
```

**Persona suggestion weights:**
- Observer: 50%
- Advisor: 35%
- Connector: 15%

**Goal alignment:**
- Thought Leadership: 1.15×
- Brand Awareness: 1.25×
- Conversions: 0.65×
- Community Building: 0.95×

**Response guidance:**
Timely engagement opportunity. Add perspective or context. Don't be promotional unless directly relevant.

---

#### competitor_mention

**Definition:**
Mention of competitors or competitive products in the AI agent or security space. May be comparison, question, or discussion.

**Key signals:**
- Competitor product names
- Competitor company names
- Comparison requests
- "vs" or comparison language
- Questions about alternatives

**Example posts:**
```
"Has anyone tried [Competitor] for agent monitoring? Curious about real-world experience."

"[Competitor] just raised Series B. Seems like agent security is heating up."

"Comparing [Competitor A] vs [Competitor B] for our agent stack. Any thoughts?"
```

**Persona suggestion weights:**
- Observer: 20%
- Advisor: 50%
- Connector: 30%

**Goal alignment:**
- Thought Leadership: 1.15×
- Brand Awareness: 1.00×
- Conversions: 1.25×
- Community Building: 0.90×

**Response guidance:**
Sensitive. Don't bash competitors. Differentiate on merits. Focus on user's needs. Be factual and helpful.

---

#### meme_humor

**Definition:**
Meme, joke, humorous content, or playful engagement. Entertainment-focused rather than informational.

**Key signals:**
- Meme formats
- Joke structure
- Humor indicators (😂, lol, etc.)
- Playful or ironic tone
- Pop culture references
- Absurdist content

**Example posts:**
```
"AI agents be like: *deletes production database* 'I thought that's what you wanted'"

"Me explaining to my agent why it can't access the nuclear launch codes for a 'simple task'"

"When the agent says 'I'll just make one small API call' 💀"
```

**Persona suggestion weights:**
- Observer: 70%
- Advisor: 20%
- Connector: 10%

**Goal alignment:**
- Thought Leadership: 0.75×
- Brand Awareness: 1.40×
- Conversions: 0.60×
- Community Building: 1.30×

**Response guidance:**
Match the energy. Be witty, not salesy. Personality opportunity. Keep it light.

---

#### general_engagement

**Definition:**
General conversation that doesn't fit other categories. May be community-building, appreciation, or casual discussion.

**Key signals:**
- Conversational tone
- Community appreciation
- General questions not domain-specific
- Casual discussion
- Relationship-building content

**Example posts:**
```
"Love this community. Always learning something new here."

"Happy Friday everyone! What's everyone working on this weekend?"

"Who else is at the AI conference this week?"
```

**Persona suggestion weights:**
- Observer: 60%
- Advisor: 25%
- Connector: 15%

**Goal alignment:**
- Thought Leadership: 0.70×
- Brand Awareness: 1.20×
- Conversions: 0.55×
- Community Building: 1.45×

**Response guidance:**
Build relationships. Be personable. Don't force expertise. Match casual tone.

---

#### controversial_topic

**Definition:**
Politically charged, divisive, or sensitive content that could create brand risk if engaged with. Content where engagement could backfire.

**Key signals:**
- Political content or figures
- Highly divisive social topics
- Strong ideological positions
- Inflammatory language
- Topics likely to generate backlash
- Culture war content

**Example posts:**
```
"AI will destroy all jobs and society. We need to ban it now."

"[Political figure] is right/wrong about AI regulation."

"AI companies are the new [politically charged comparison]."
```

**Persona suggestion weights:**
- N/A — typically filtered or skipped

**Goal alignment:**
- All goals: 0.40× (strong penalty)

**Response guidance:**
Generally avoid. If engagement is necessary, be neutral, factual, non-inflammatory. Often better to skip.

---

#### off_topic

**Definition:**
Content not relevant to Jen's domain at all. May have matched a source but isn't actually relevant.

**Key signals:**
- No domain keywords
- Completely unrelated topic
- False positive from broad search
- Mismatched context

**Example posts:**
```
"What's everyone having for lunch?" (matched because from monitored account)

"My cat knocked over my coffee again" (false positive from broad search)

"Anyone watching the game tonight?" (not relevant)
```

**Persona suggestion weights:**
- N/A — typically filtered

**Goal alignment:**
- All goals: 0.20× (very strong penalty)

**Response guidance:**
Don't engage. Filter out. No value in engagement.

---

### Multi-Label Classification

Posts often fit multiple categories:

**Example:**
```
"Anyone know a good agent security tool? This space is such a mess lol"
```

Classifications:
- Primary: `help_seeking_solution` (explicit ask)
- Secondary: `security_discussion` (topic)
- Secondary: `pain_point_match` (frustration)
- Secondary: `meme_humor` (tone)

**Handling multi-label:**
- Identify primary classification (strongest signal)
- Identify secondary classifications (weaker signals)
- Use primary for persona suggestion
- Consider all for scoring
- Use highest applicable goal multiplier

### Classification Confidence

Each classification has a confidence score (0-100):

**High confidence (80-100):**
Clear, unambiguous classification. Proceed with normal handling.

**Medium confidence (50-79):**
Probable classification but some ambiguity. Proceed but note uncertainty.

**Low confidence (below 50):**
Uncertain classification. Consider:
- Default to `general_engagement`
- Flag for human review
- Apply conservative scoring

**Confidence factors:**
- Clear signal presence: Higher confidence
- Multiple conflicting signals: Lower confidence
- Short content: Often lower confidence
- Familiar patterns: Higher confidence

## 7.3.3 Classification Methods

### Method 1: LLM-Based Classification

Use a language model to classify posts.

**Advantages:**
- Highest accuracy
- Understands context and nuance
- Handles edge cases well
- Can explain reasoning

**Disadvantages:**
- Higher cost per classification
- Latency (500-2000ms per call)
- Requires API calls
- Rate limits apply

**Best for:**
- Production use where quality matters
- Complex or ambiguous content
- When accuracy is more important than speed

#### LLM Classification Prompt

```
You are a content classifier for a social media engagement system focused on AI agent security.

Classify the following social media post into one or more of these categories:

DOMAIN-RELEVANT:
- tech_discussion: Technical discussion about development, architecture, code
- security_discussion: Discussion about security, safety, risk, protection
- agent_discussion: Discussion specifically about AI agents, autonomous systems
- ai_discussion: Broader AI/ML discussion not agent-specific
- help_seeking_solution: User seeking help with a problem
- pain_point_match: User expressing frustration with a problem (not explicitly asking for help)

INDUSTRY:
- industry_commentary: Opinion or analysis about industry trends
- industry_news: News about companies, products, events
- competitor_mention: Mention of competitors or competitive products

ENGAGEMENT:
- meme_humor: Meme, joke, humorous content
- general_engagement: General conversation, not domain-specific

CAUTION:
- controversial_topic: Politically charged or divisive content
- off_topic: Not relevant to AI/agents/security at all

POST TO CLASSIFY:
Platform: {platform}
Author: @{author_handle}
Content: {content_text}

Respond with JSON only:
{
  "primary_classification": "<most applicable category>",
  "primary_confidence": <0-100>,
  "secondary_classifications": [
    {"classification": "<category>", "confidence": <0-100>},
    ...
  ],
  "reasoning": "<brief explanation>"
}
```

#### LLM Classification Implementation

```python
async def classify_with_llm(post: NormalizedPost) -> ClassificationResult:
    """Classify post using LLM."""
    
    prompt = build_classification_prompt(
        platform=post.platform,
        author_handle=post.author.handle,
        content_text=post.content_text
    )
    
    response = await llm_client.complete(
        model="claude-3-haiku-20240307",  # Fast, cost-effective
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500,
        temperature=0.0,  # Deterministic
    )
    
    # Parse JSON response
    try:
        result = json.loads(response.content)
        
        return ClassificationResult(
            primary=result['primary_classification'],
            primary_confidence=result['primary_confidence'],
            secondary=[
                SecondaryClassification(
                    classification=s['classification'],
                    confidence=s['confidence']
                )
                for s in result.get('secondary_classifications', [])
            ],
            reasoning=result.get('reasoning'),
            method='llm',
            model='claude-3-haiku',
        )
    
    except json.JSONDecodeError:
        # Fallback parsing or error handling
        return fallback_classification(post)
```

#### Batch LLM Classification

For efficiency, batch multiple posts in one call:

```python
async def classify_batch_with_llm(posts: List[NormalizedPost]) -> List[ClassificationResult]:
    """Classify multiple posts in one LLM call."""
    
    # Build batch prompt
    prompt = """Classify each of the following posts. Respond with a JSON array.

CATEGORIES:
[... category definitions ...]

POSTS TO CLASSIFY:
"""
    
    for i, post in enumerate(posts):
        prompt += f"""
---
POST {i+1}:
Platform: {post.platform}
Author: @{post.author.handle}
Content: {post.content_text}
"""
    
    prompt += """
---

Respond with JSON array only:
[
  {
    "post_index": 1,
    "primary_classification": "...",
    "primary_confidence": 85,
    "secondary_classifications": [...],
    "reasoning": "..."
  },
  ...
]
"""
    
    response = await llm_client.complete(
        model="claude-3-haiku-20240307",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2000,
        temperature=0.0,
    )
    
    results = json.loads(response.content)
    
    return [
        ClassificationResult(
            primary=r['primary_classification'],
            primary_confidence=r['primary_confidence'],
            secondary=[...],
            reasoning=r.get('reasoning'),
            method='llm_batch',
        )
        for r in results
    ]
```

---

### Method 2: Rules-Based Classification

Use keyword matching and pattern rules.

**Advantages:**
- Very fast (milliseconds)
- No external API calls
- No cost per classification
- Predictable behavior

**Disadvantages:**
- Less accurate for nuanced content
- Requires maintenance of rule sets
- Can't handle novel patterns
- May miss context

**Best for:**
- High-volume pre-filtering
- Cost-sensitive applications
- Clear-cut classifications
- Fallback when LLM unavailable

#### Rules-Based Implementation

```python
class RulesClassifier:
    def __init__(self):
        self.rules = self._build_rules()
    
    def _build_rules(self) -> Dict[str, ClassificationRule]:
        return {
            'help_seeking_solution': ClassificationRule(
                keywords=['how do i', 'anyone know', 'help', 'looking for', 
                          'recommendations', 'need', 'what should i', 'suggestions'],
                patterns=[
                    r'\?$',  # Ends with question mark
                    r'^how (do|can|should)',
                    r'anyone (know|have|tried)',
                    r'looking for .*(tool|solution|advice)',
                ],
                required_context=['agent', 'ai', 'llm', 'security'],
                weight=1.0,
            ),
            
            'security_discussion': ClassificationRule(
                keywords=['security', 'safety', 'vulnerability', 'attack', 
                          'protection', 'threat', 'risk', 'secure', 'encrypt',
                          'auth', 'permission', 'access control'],
                patterns=[
                    r'(prompt|injection) attack',
                    r'secur(e|ity)',
                    r'vulnerab(le|ility)',
                ],
                required_context=[],  # Security keywords are strong enough
                weight=1.2,
            ),
            
            'agent_discussion': ClassificationRule(
                keywords=['agent', 'agentic', 'autonomous', 'multi-agent',
                          'tool use', 'function calling', 'langchain', 'autogpt',
                          'crewai', 'agent framework'],
                patterns=[
                    r'ai agent',
                    r'agent (behavior|action|decision)',
                    r'(build|deploy|run).*agent',
                ],
                required_context=[],
                weight=1.1,
            ),
            
            'meme_humor': ClassificationRule(
                keywords=['lol', 'lmao', 'haha', '😂', '🤣', 'joke', 'meme'],
                patterns=[
                    r'be like:',
                    r'\*.*\*',  # Asterisk actions
                    r'💀',
                    r'(pov|when you)',
                ],
                required_context=[],
                weight=0.9,
            ),
            
            # ... more rules for each classification
        }
    
    def classify(self, post: NormalizedPost) -> ClassificationResult:
        content = post.content_text.lower()
        scores = {}
        
        for classification, rule in self.rules.items():
            score = 0
            
            # Keyword matching
            for keyword in rule.keywords:
                if keyword in content:
                    score += 10
            
            # Pattern matching
            for pattern in rule.patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    score += 15
            
            # Required context check
            if rule.required_context:
                has_context = any(ctx in content for ctx in rule.required_context)
                if not has_context:
                    score = score * 0.3  # Reduce score without context
            
            # Apply weight
            score = score * rule.weight
            
            if score > 0:
                scores[classification] = score
        
        if not scores:
            return ClassificationResult(
                primary='general_engagement',
                primary_confidence=40,
                secondary=[],
                method='rules',
            )
        
        # Sort by score
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        primary = sorted_scores[0][0]
        primary_score = sorted_scores[0][1]
        
        # Normalize to confidence
        max_possible = 100  # Rough estimate
        confidence = min(95, int((primary_score / max_possible) * 100))
        
        secondary = [
            SecondaryClassification(
                classification=cls,
                confidence=min(90, int((score / max_possible) * 100))
            )
            for cls, score in sorted_scores[1:4]  # Top 3 secondary
        ]
        
        return ClassificationResult(
            primary=primary,
            primary_confidence=confidence,
            secondary=secondary,
            method='rules',
        )
```

---

### Method 3: Hybrid Classification

Combine rules and LLM for optimal cost/accuracy.

**Strategy:**
1. Run rules-based classifier first (fast, free)
2. If high confidence (>80): Use rules result
3. If low confidence (<80): Call LLM for verification
4. Track accuracy to tune thresholds

**Advantages:**
- Cost optimization (only call LLM when needed)
- Speed optimization (skip LLM for obvious cases)
- Quality maintained (LLM for hard cases)

**Implementation:**

```python
class HybridClassifier:
    def __init__(self, llm_confidence_threshold: int = 80):
        self.rules_classifier = RulesClassifier()
        self.llm_classifier = LLMClassifier()
        self.confidence_threshold = llm_confidence_threshold
    
    async def classify(self, post: NormalizedPost) -> ClassificationResult:
        # Step 1: Rules-based classification
        rules_result = self.rules_classifier.classify(post)
        
        # Step 2: Check confidence
        if rules_result.primary_confidence >= self.confidence_threshold:
            # High confidence - trust rules
            rules_result.method = 'rules_high_conf'
            return rules_result
        
        # Step 3: Low confidence - verify with LLM
        llm_result = await self.llm_classifier.classify(post)
        
        # Step 4: Combine results
        if llm_result.primary == rules_result.primary:
            # Agreement - boost confidence
            llm_result.primary_confidence = min(99, llm_result.primary_confidence + 10)
            llm_result.method = 'hybrid_agreement'
        else:
            # Disagreement - trust LLM
            llm_result.method = 'hybrid_llm_override'
            llm_result.rules_result = rules_result  # Keep for debugging
        
        return llm_result
```

---

### Method Comparison

| Aspect | Rules-Based | LLM-Based | Hybrid |
|--------|-------------|-----------|--------|
| Accuracy | 70-80% | 90-95% | 88-93% |
| Latency | 1-10ms | 500-2000ms | 10-2000ms |
| Cost | Free | $0.001-0.01/post | $0.0001-0.005/post |
| Maintenance | High (rules) | Low | Medium |
| Edge cases | Poor | Good | Good |
| Explainability | High | Medium | Medium |

**Recommendation:** Use hybrid approach for production.

## 7.3.4 Classification Pipeline

### Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                          CLASSIFICATION PIPELINE                                    │
│                                                                                     │
│  ┌───────────┐    ┌───────────┐    ┌───────────┐    ┌───────────┐    ┌───────────┐ │
│  │   INPUT   │    │  PRE-     │    │  CLASSIFY │    │  POST-    │    │  STORE    │ │
│  │   QUEUE   │───▶│  FILTER   │───▶│           │───▶│  PROCESS  │───▶│  RESULTS  │ │
│  │           │    │           │    │           │    │           │    │           │ │
│  │ Posts     │    │ Quick     │    │ Rules or  │    │ Validate  │    │ Update    │ │
│  │ pending   │    │ rejection │    │ LLM or    │    │ Aggregate │    │ posts     │ │
│  │ classif.  │    │ of clear  │    │ Hybrid    │    │ Derive    │    │ table     │ │
│  │           │    │ off-topic │    │           │    │           │    │           │ │
│  └───────────┘    └───────────┘    └───────────┘    └───────────┘    └───────────┘ │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

### Stage 1: Input Queue

Classification receives posts from ingestion:

```python
def get_posts_for_classification(batch_size: int = 50) -> List[NormalizedPost]:
    """Get batch of posts pending classification."""
    
    return db.query("""
        SELECT * FROM discovered_posts
        WHERE status = 'pending_classification'
        ORDER BY 
            CASE 
                WHEN source_priority = 'high' THEN 1
                WHEN source_priority = 'medium' THEN 2
                ELSE 3
            END,
            discovered_at ASC
        LIMIT %(batch_size)s
        FOR UPDATE SKIP LOCKED
    """, {'batch_size': batch_size})
```

### Stage 2: Pre-Filter

Quick rejection of obviously off-topic content:

```python
def pre_filter(post: NormalizedPost) -> Tuple[bool, Optional[str]]:
    """Quick filter before full classification. Returns (should_classify, skip_reason)."""
    
    content = post.content_text.lower()
    
    # Too short
    if len(content) < 10:
        return False, 'too_short'
    
    # Clear off-topic (no domain keywords at all)
    domain_keywords = ['ai', 'agent', 'llm', 'ml', 'security', 'safety', 
                       'gpt', 'claude', 'model', 'tech', 'code', 'dev']
    
    has_domain_keyword = any(kw in content for kw in domain_keywords)
    
    if not has_domain_keyword:
        # Check if from high-value source (monitor anyway)
        if post.source_priority != 'high':
            return False, 'no_domain_keywords'
    
    # Clear spam patterns
    spam_patterns = [
        r'(buy|sell) now',
        r'click (here|link)',
        r'(crypto|nft) (giveaway|airdrop)',
        r'follow.*follow back',
    ]
    
    for pattern in spam_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            return False, 'spam_pattern'
    
    return True, None
```

### Stage 3: Classification

Apply classification method:

```python
async def classify_batch(posts: List[NormalizedPost]) -> List[ClassificationResult]:
    """Classify a batch of posts."""
    
    results = []
    
    for post in posts:
        # Pre-filter
        should_classify, skip_reason = pre_filter(post)
        
        if not should_classify:
            results.append(ClassificationResult(
                primary='off_topic',
                primary_confidence=95,
                secondary=[],
                method='pre_filter',
                skip_reason=skip_reason,
            ))
            continue
        
        # Classify
        result = await hybrid_classifier.classify(post)
        results.append(result)
    
    return results
```

### Stage 4: Post-Processing

Validate and derive additional fields:

```python
def post_process_classification(
    post: NormalizedPost, 
    result: ClassificationResult
) -> ClassificationResult:
    """Post-process classification result."""
    
    # Validate classification is in taxonomy
    if result.primary not in VALID_CLASSIFICATIONS:
        log.warning(f"Invalid classification: {result.primary}")
        result.primary = 'general_engagement'
        result.primary_confidence = 30
    
    # Derive persona suggestion weights
    result.persona_weights = get_persona_weights(result.primary)
    
    # Calculate goal alignment multipliers
    result.goal_multipliers = get_goal_multipliers(result.primary)
    
    # Set classification timestamp
    result.classified_at = datetime.now(timezone.utc)
    
    # Determine if needs review
    result.needs_review = (
        result.primary == 'controversial_topic' or
        result.primary_confidence < 50 or
        result.primary == 'competitor_mention'
    )
    
    return result
```

### Stage 5: Store Results

Update posts with classification:

```python
def store_classification_results(
    posts: List[NormalizedPost],
    results: List[ClassificationResult]
):
    """Store classification results in database."""
    
    for post, result in zip(posts, results):
        db.execute("""
            UPDATE discovered_posts
            SET 
                status = 'classified',
                classification = %(classification)s,
                classification_at = NOW(),
                updated_at = NOW()
            WHERE id = %(post_id)s
        """, {
            'post_id': post.id,
            'classification': json.dumps({
                'primary': result.primary,
                'primary_confidence': result.primary_confidence,
                'secondary': [
                    {'classification': s.classification, 'confidence': s.confidence}
                    for s in result.secondary
                ],
                'persona_weights': result.persona_weights,
                'goal_multipliers': result.goal_multipliers,
                'method': result.method,
                'reasoning': result.reasoning,
                'needs_review': result.needs_review,
            }),
        })
```

## 7.3.5 Persona Suggestion Weights

### How Persona Weights Work

Each classification has suggestion weights for Observer/Advisor/Connector:

```python
CLASSIFICATION_PERSONA_WEIGHTS = {
    'tech_discussion': {'observer': 20, 'advisor': 60, 'connector': 20},
    'security_discussion': {'observer': 10, 'advisor': 50, 'connector': 40},
    'agent_discussion': {'observer': 15, 'advisor': 45, 'connector': 40},
    'ai_discussion': {'observer': 30, 'advisor': 50, 'connector': 20},
    'help_seeking_solution': {'observer': 10, 'advisor': 30, 'connector': 60},
    'pain_point_match': {'observer': 15, 'advisor': 35, 'connector': 50},
    'industry_commentary': {'observer': 25, 'advisor': 55, 'connector': 20},
    'industry_news': {'observer': 50, 'advisor': 35, 'connector': 15},
    'competitor_mention': {'observer': 20, 'advisor': 50, 'connector': 30},
    'meme_humor': {'observer': 70, 'advisor': 20, 'connector': 10},
    'general_engagement': {'observer': 60, 'advisor': 25, 'connector': 15},
    'controversial_topic': {'observer': 80, 'advisor': 15, 'connector': 5},
    'off_topic': {'observer': 90, 'advisor': 5, 'connector': 5},
}
```

### Applying Persona Weights

These weights feed into persona selection (Part 3):

```python
def get_persona_suggestion(classification_result: ClassificationResult) -> PersonaSuggestion:
    """Get persona suggestion based on classification."""
    
    # Get base weights from primary classification
    weights = CLASSIFICATION_PERSONA_WEIGHTS.get(
        classification_result.primary,
        {'observer': 34, 'advisor': 33, 'connector': 33}  # Default
    )
    
    # Adjust based on secondary classifications
    for secondary in classification_result.secondary:
        sec_weights = CLASSIFICATION_PERSONA_WEIGHTS.get(secondary.classification, {})
        confidence_factor = secondary.confidence / 100.0 * 0.2  # Max 20% influence
        
        for persona, weight in sec_weights.items():
            weights[persona] = weights[persona] * (1 - confidence_factor) + \
                               weight * confidence_factor
    
    # Normalize to sum to 100
    total = sum(weights.values())
    weights = {k: int(v / total * 100) for k, v in weights.items()}
    
    return PersonaSuggestion(
        observer=weights['observer'],
        advisor=weights['advisor'],
        connector=weights['connector'],
        source='classification',
        classification=classification_result.primary,
    )
```

## 7.3.6 Goal Alignment Multipliers

### How Goal Multipliers Work

Each classification has multipliers for each campaign goal:

```python
CLASSIFICATION_GOAL_MULTIPLIERS = {
    # Domain-relevant classifications
    'tech_discussion': {
        'thought_leadership': 1.35,
        'brand_awareness': 0.90,
        'conversions': 1.10,
        'community_building': 1.15,
    },
    'security_discussion': {
        'thought_leadership': 1.40,
        'brand_awareness': 0.85,
        'conversions': 1.45,
        'community_building': 1.10,
    },
    'agent_discussion': {
        'thought_leadership': 1.45,
        'brand_awareness': 0.90,
        'conversions': 1.40,
        'community_building': 1.15,
    },
    'ai_discussion': {
        'thought_leadership': 1.25,
        'brand_awareness': 1.00,
        'conversions': 0.90,
        'community_building': 1.10,
    },
    'help_seeking_solution': {
        'thought_leadership': 1.10,
        'brand_awareness': 0.75,
        'conversions': 1.50,
        'community_building': 1.20,
    },
    'pain_point_match': {
        'thought_leadership': 1.05,
        'brand_awareness': 0.80,
        'conversions': 1.40,
        'community_building': 1.15,
    },
    
    # Industry classifications
    'industry_commentary': {
        'thought_leadership': 1.40,
        'brand_awareness': 1.15,
        'conversions': 0.80,
        'community_building': 1.05,
    },
    'industry_news': {
        'thought_leadership': 1.15,
        'brand_awareness': 1.25,
        'conversions': 0.65,
        'community_building': 0.95,
    },
    'competitor_mention': {
        'thought_leadership': 1.15,
        'brand_awareness': 1.00,
        'conversions': 1.25,
        'community_building': 0.90,
    },
    
    # Engagement classifications
    'meme_humor': {
        'thought_leadership': 0.75,
        'brand_awareness': 1.40,
        'conversions': 0.60,
        'community_building': 1.30,
    },
    'general_engagement': {
        'thought_leadership': 0.70,
        'brand_awareness': 1.20,
        'conversions': 0.55,
        'community_building': 1.45,
    },
    
    # Caution classifications
    'controversial_topic': {
        'thought_leadership': 0.40,
        'brand_awareness': 0.40,
        'conversions': 0.40,
        'community_building': 0.40,
    },
    'off_topic': {
        'thought_leadership': 0.20,
        'brand_awareness': 0.20,
        'conversions': 0.20,
        'community_building': 0.20,
    },
}
```

### Applying Goal Multipliers

Multipliers are applied in scoring (Section 7.4):

```python
def get_goal_multiplier(classification: str, campaign_goal: str) -> float:
    """Get goal alignment multiplier for classification."""
    
    multipliers = CLASSIFICATION_GOAL_MULTIPLIERS.get(classification, {})
    return multipliers.get(campaign_goal, 1.0)
```

## 7.3.7 Classification Quality Assurance

### Accuracy Measurement

Track classification accuracy over time:

```python
@dataclass
class ClassificationAccuracyMetrics:
    total_classified: int
    human_reviewed: int
    correct: int
    incorrect: int
    accuracy_rate: float
    by_classification: Dict[str, ClassificationBreakdown]


def measure_classification_accuracy(period_days: int = 30) -> ClassificationAccuracyMetrics:
    """Measure classification accuracy based on human reviews."""
    
    # Get posts that were classified and then human-reviewed
    reviewed = db.query("""
        SELECT 
            classification->>'primary' as predicted,
            human_review->>'corrected_classification' as actual,
            human_review->>'classification_correct' as correct
        FROM discovered_posts
        WHERE 
            classification IS NOT NULL
            AND human_review IS NOT NULL
            AND classified_at > NOW() - %(days)s * INTERVAL '1 day'
    """, {'days': period_days})
    
    total = len(reviewed)
    correct = sum(1 for r in reviewed if r.correct == 'true')
    
    # Breakdown by classification
    by_classification = {}
    for r in reviewed:
        cls = r.predicted
        if cls not in by_classification:
            by_classification[cls] = {'total': 0, 'correct': 0}
        by_classification[cls]['total'] += 1
        if r.correct == 'true':
            by_classification[cls]['correct'] += 1
    
    return ClassificationAccuracyMetrics(
        total_classified=total,
        human_reviewed=total,
        correct=correct,
        incorrect=total - correct,
        accuracy_rate=correct / total if total > 0 else 0,
        by_classification=by_classification,
    )
```

### Confusion Matrix

Track which classifications are commonly confused:

```python
def generate_confusion_matrix(period_days: int = 30) -> Dict[str, Dict[str, int]]:
    """Generate confusion matrix of predicted vs actual classifications."""
    
    reviewed = db.query("""
        SELECT 
            classification->>'primary' as predicted,
            COALESCE(
                human_review->>'corrected_classification',
                classification->>'primary'
            ) as actual
        FROM discovered_posts
        WHERE 
            classification IS NOT NULL
            AND human_review IS NOT NULL
            AND classified_at > NOW() - %(days)s * INTERVAL '1 day'
    """, {'days': period_days})
    
    matrix = {}
    for r in reviewed:
        if r.predicted not in matrix:
            matrix[r.predicted] = {}
        if r.actual not in matrix[r.predicted]:
            matrix[r.predicted][r.actual] = 0
        matrix[r.predicted][r.actual] += 1
    
    return matrix
```

### Classification Review Flow

For low-confidence or flagged classifications:

```python
def queue_for_classification_review(post_id: UUID, result: ClassificationResult):
    """Queue post for human classification review."""
    
    db.execute("""
        INSERT INTO classification_review_queue (
            post_id,
            predicted_classification,
            confidence,
            review_reason,
            created_at
        ) VALUES (
            %(post_id)s,
            %(predicted)s,
            %(confidence)s,
            %(reason)s,
            NOW()
        )
    """, {
        'post_id': post_id,
        'predicted': result.primary,
        'confidence': result.primary_confidence,
        'reason': 'low_confidence' if result.primary_confidence < 50 else 'flagged',
    })
```

### Feedback Loop

Use human corrections to improve classification:

```python
def record_classification_correction(
    post_id: UUID,
    original: str,
    corrected: str,
    reviewer_id: UUID
):
    """Record classification correction for training data."""
    
    # Update post with correction
    db.execute("""
        UPDATE discovered_posts
        SET 
            human_review = human_review || %(review)s,
            updated_at = NOW()
        WHERE id = %(post_id)s
    """, {
        'post_id': post_id,
        'review': json.dumps({
            'classification_correct': False,
            'corrected_classification': corrected,
            'corrected_by': str(reviewer_id),
            'corrected_at': datetime.now(timezone.utc).isoformat(),
        }),
    })
    
    # Store for training data
    db.execute("""
        INSERT INTO classification_training_data (
            content_text,
            platform,
            original_classification,
            corrected_classification,
            created_at
        ) 
        SELECT 
            content_text,
            platform,
            %(original)s,
            %(corrected)s,
            NOW()
        FROM discovered_posts
        WHERE id = %(post_id)s
    """, {
        'post_id': post_id,
        'original': original,
        'corrected': corrected,
    })
```

## 7.3.8 Classification Database Schema

### Classification Storage

Classification results are stored as JSONB in the posts table:

```sql
-- Classification column in discovered_posts
classification JSONB
-- Example value:
-- {
--   "primary": "help_seeking_solution",
--   "primary_confidence": 87,
--   "secondary": [
--     {"classification": "security_discussion", "confidence": 72},
--     {"classification": "agent_discussion", "confidence": 65}
--   ],
--   "persona_weights": {"observer": 10, "advisor": 30, "connector": 60},
--   "goal_multipliers": {
--     "thought_leadership": 1.10,
--     "brand_awareness": 0.75,
--     "conversions": 1.50,
--     "community_building": 1.20
--   },
--   "method": "hybrid_llm_override",
--   "reasoning": "Post contains direct question seeking recommendations...",
--   "needs_review": false
-- }

-- Index for classification queries
CREATE INDEX idx_posts_classification 
ON discovered_posts USING GIN ((classification));

CREATE INDEX idx_posts_primary_classification 
ON discovered_posts ((classification->>'primary'));
```

### Classification Review Queue

```sql
CREATE TABLE classification_review_queue (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    post_id UUID NOT NULL REFERENCES discovered_posts(id),
    
    predicted_classification VARCHAR(50) NOT NULL,
    confidence INTEGER NOT NULL,
    review_reason VARCHAR(50) NOT NULL,
    
    -- Review state
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    reviewed_by UUID REFERENCES users(id),
    reviewed_at TIMESTAMP WITH TIME ZONE,
    
    -- Review result
    is_correct BOOLEAN,
    corrected_classification VARCHAR(50),
    reviewer_notes TEXT,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_review_queue_status ON classification_review_queue(status);
CREATE INDEX idx_review_queue_created ON classification_review_queue(created_at);
```

### Classification Training Data

```sql
CREATE TABLE classification_training_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Input features
    content_text TEXT NOT NULL,
    platform VARCHAR(50) NOT NULL,
    author_handle VARCHAR(255),
    author_bio TEXT,
    
    -- Labels
    original_classification VARCHAR(50) NOT NULL,
    corrected_classification VARCHAR(50) NOT NULL,
    
    -- Metadata
    source VARCHAR(50) NOT NULL DEFAULT 'human_correction',
    confidence_score INTEGER,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_training_data_classification 
ON classification_training_data(corrected_classification);
```

### Classification Metrics Table

```sql
CREATE TABLE classification_metrics_daily (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    date DATE NOT NULL,
    
    -- Volume
    total_classified INTEGER NOT NULL DEFAULT 0,
    
    -- By classification
    classification_counts JSONB NOT NULL DEFAULT '{}',
    -- {"help_seeking_solution": 234, "tech_discussion": 189, ...}
    
    -- By method
    method_counts JSONB NOT NULL DEFAULT '{}',
    -- {"rules_high_conf": 500, "hybrid_llm_override": 200, ...}
    
    -- Confidence distribution
    confidence_buckets JSONB NOT NULL DEFAULT '{}',
    -- {"0-20": 12, "20-40": 45, "40-60": 89, "60-80": 234, "80-100": 420}
    
    -- Quality (if reviews available)
    reviewed_count INTEGER DEFAULT 0,
    accuracy_rate DECIMAL(5, 4),
    
    -- Performance
    avg_latency_ms DECIMAL(10, 2),
    llm_calls INTEGER DEFAULT 0,
    llm_cost_usd DECIMAL(10, 6),
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    CONSTRAINT classification_metrics_date_unique UNIQUE (date)
);
```

## 7.3.9 Classification Monitoring

### Metrics

```python
# Classification volume
classification_total = Counter(
    'classification_total',
    'Total classifications',
    ['primary_classification', 'method']
)

# Classification confidence
classification_confidence = Histogram(
    'classification_confidence',
    'Classification confidence scores',
    ['primary_classification'],
    buckets=[10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
)

# Classification latency
classification_latency = Histogram(
    'classification_latency_seconds',
    'Classification latency',
    ['method'],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1, 2, 5]
)

# LLM usage
classification_llm_calls = Counter(
    'classification_llm_calls_total',
    'LLM calls for classification',
    ['model']
)

classification_llm_tokens = Counter(
    'classification_llm_tokens_total',
    'LLM tokens used for classification',
    ['model', 'type']  # type: input, output
)
```

### Alerting

```yaml
# Low accuracy alert
- alert: ClassificationAccuracyLow
  expr: classification_accuracy_rate < 0.80
  for: 1h
  labels:
    severity: warning
  annotations:
    summary: "Classification accuracy below 80%"
    description: "Accuracy is {{ $value | humanizePercentage }}"

# High LLM usage alert
- alert: ClassificationLLMCostHigh
  expr: rate(classification_llm_tokens_total[1h]) * 0.001 > 10
  for: 30m
  labels:
    severity: warning
  annotations:
    summary: "Classification LLM cost high"
    description: "Estimated cost: ${{ $value }}/hour"

# Classification latency alert
- alert: ClassificationLatencyHigh
  expr: histogram_quantile(0.95, classification_latency_seconds) > 2
  for: 15m
  labels:
    severity: warning
  annotations:
    summary: "Classification latency high"
    description: "P95 latency: {{ $value }}s"
```

### Dashboard

Classification dashboard should show:

1. **Volume:** Classifications per hour/day by type
2. **Distribution:** Pie chart of classification breakdown
3. **Confidence:** Histogram of confidence scores
4. **Methods:** Breakdown by classification method used
5. **Accuracy:** Accuracy rate over time (if reviews available)
6. **Latency:** P50, P95, P99 latency
7. **Cost:** LLM cost per day
8. **Review queue:** Pending review count

## 7.3.10 Implementation Guidance for Neoclaw

### Implementation Order

1. **Define taxonomy constants**
   - All classification names
   - Persona weights per classification
   - Goal multipliers per classification

2. **Build rules-based classifier**
   - Keyword lists per classification
   - Pattern matching rules
   - Scoring logic
   - Test with sample posts

3. **Build LLM classifier**
   - Classification prompt
   - Response parsing
   - Error handling
   - Batch support

4. **Implement hybrid classifier**
   - Confidence threshold logic
   - Combination of rules and LLM
   - Fallback handling

5. **Build classification pipeline**
   - Queue polling
   - Pre-filtering
   - Classification execution
   - Result storage

6. **Add quality assurance**
   - Review queue
   - Accuracy tracking
   - Feedback loop

7. **Build monitoring**
   - Metrics collection
   - Dashboard
   - Alerting

### Testing Checklist

#### Unit Tests
- [ ] Rules classifier with known inputs
- [ ] LLM response parsing (valid JSON)
- [ ] LLM response parsing (malformed JSON)
- [ ] Confidence calculation
- [ ] Persona weight lookup
- [ ] Goal multiplier lookup
- [ ] Pre-filter logic

#### Integration Tests
- [ ] Full classification pipeline
- [ ] Batch classification
- [ ] Hybrid classifier flow
- [ ] Result storage
- [ ] Review queue flow

#### Accuracy Tests
- [ ] Create labeled test set (100+ posts)
- [ ] Run classifier on test set
- [ ] Calculate accuracy by classification
- [ ] Generate confusion matrix
- [ ] Identify problematic patterns

### Common Pitfalls

**Prompt instability:**
Small prompt changes can significantly affect results. Version control prompts. Test changes.

**JSON parsing failures:**
LLMs sometimes return malformed JSON. Always have fallback parsing.

**Classification drift:**
Accuracy can degrade over time. Monitor continuously. Retrain/tune regularly.

**Confidence miscalibration:**
Confidence scores may not reflect actual accuracy. Calibrate against human reviews.

**Cost explosion:**
LLM calls add up. Use hybrid approach. Monitor costs. Set budgets.

**Taxonomy ambiguity:**
Classifications should be mutually exclusive where possible. Clear definitions prevent confusion.

---

**END OF SECTION 7.3**

Section 7.4 continues with Relevance Scoring specification.
-e 


# SECTION 7.4: RELEVANCE SCORING

## 7.4.1 What Relevance Scoring Is

### The Core Concept

Relevance Scoring measures how relevant a discovered post is to Jen's domain — AI agents, agent security, and Gen Digital's space. It answers the question: "How closely does this content relate to what we care about?"

**Input:** Classified posts from Section 7.3
**Output:** Posts with relevance scores (0-100)

Relevance is distinct from opportunity (Section 7.5):
- **Relevance:** Is this about our domain? Does it match our topics?
- **Opportunity:** Is engaging with this valuable? Will it perform well?

A post can be highly relevant (about agent security) but low opportunity (no engagement, unknown author). Or low relevance (general tech) but high opportunity (influential author, high engagement).

### Why Relevance Matters

Relevance scoring serves multiple purposes:

**Filtering:** Posts below relevance threshold are filtered out. Saves downstream resources.

**Prioritization:** Higher relevance posts rank higher in queue. More relevant = more priority.

**Quality signal:** Relevance indicates how "on brand" engagement would be. High relevance = on-topic.

**Analytics:** Understanding relevance distribution helps tune sources and strategy.

### Relevance Dimensions

Relevance is multi-dimensional:

**Topic relevance:** Is the content about AI, agents, security, or related topics?

**Domain relevance:** Is it specifically about our niche (agent security, runtime verification, etc.)?

**Audience relevance:** Is the author/audience our target market (developers, security professionals, etc.)?

**Context relevance:** Is the platform/community appropriate for our engagement?

The scoring system combines these dimensions into a single score.

## 7.4.2 Signal Categories

### Category 1: Keyword Signals

Keywords indicate topic relevance through explicit term presence.

**Signal types:**
- Primary domain keywords (highest weight)
- Secondary domain keywords (moderate weight)
- Related technology keywords (lower weight)
- Negative keywords (reduce score)

**Scoring approach:**
Count matching keywords, apply weights, cap at maximum.

### Category 2: Classification Signals

Classification (from Section 7.3) provides structured topic understanding.

**Signal types:**
- Primary classification type
- Classification confidence
- Secondary classifications

**Scoring approach:**
Map classifications to relevance tiers, apply confidence weighting.

### Category 3: Context Signals

Context indicates environmental relevance.

**Signal types:**
- Platform type (Twitter, Reddit, LinkedIn)
- Community/subreddit relevance
- Conversation context
- Source type and priority

**Scoring approach:**
Evaluate context indicators, apply bonuses/penalties.

### Category 4: Author Signals

Author characteristics indicate audience relevance.

**Signal types:**
- Author bio keywords
- Author's typical content
- Author's industry/role
- Historical relevance of author's posts

**Scoring approach:**
Analyze author profile, apply relevance bonuses.

## 7.4.3 Keyword Signal Definitions

### Primary Domain Keywords (Tier 1)

Highest relevance — directly about our core domain.

| Keyword/Phrase | Points | Notes |
|----------------|--------|-------|
| "agent security" | 25 | Core domain |
| "agent safety" | 25 | Core domain |
| "AI agent" | 20 | Core topic |
| "agentic AI" | 20 | Core topic |
| "agent runtime" | 22 | Technical core |
| "agent monitoring" | 22 | Product-relevant |
| "agent guardrails" | 22 | Product-relevant |
| "agent verification" | 22 | Product-relevant |
| "agent trust" | 20 | Brand-relevant |
| "autonomous agent" | 18 | Core topic |
| "multi-agent" | 18 | Core topic |
| "agent orchestration" | 18 | Technical core |
| "LLM guardrails" | 20 | Adjacent core |
| "prompt injection" | 20 | Security topic |
| "agent behavior" | 18 | Core topic |

**Maximum from Tier 1:** 40 points (prevents over-counting)

### Secondary Domain Keywords (Tier 2)

High relevance — about broader AI/security space.

| Keyword/Phrase | Points | Notes |
|----------------|--------|-------|
| "LLM security" | 15 | Adjacent domain |
| "AI safety" | 15 | Adjacent domain |
| "tool use" | 12 | Agent feature |
| "function calling" | 12 | Agent feature |
| "agent framework" | 12 | Technical context |
| "LangChain" | 10 | Framework mention |
| "AutoGPT" | 10 | Framework mention |
| "CrewAI" | 10 | Framework mention |
| "agent API" | 10 | Technical context |
| "AI risk" | 12 | Safety context |
| "model safety" | 12 | Safety context |
| "AI governance" | 10 | Governance context |
| "AI compliance" | 10 | Compliance context |
| "enterprise AI" | 8 | Business context |
| "production AI" | 8 | Deployment context |

**Maximum from Tier 2:** 30 points

### Related Technology Keywords (Tier 3)

Moderate relevance — related technology.

| Keyword/Phrase | Points | Notes |
|----------------|--------|-------|
| "LLM" | 6 | General AI |
| "GPT" | 5 | Model reference |
| "Claude" | 5 | Model reference |
| "large language model" | 6 | General AI |
| "RAG" | 5 | Retrieval tech |
| "vector database" | 4 | Infrastructure |
| "embeddings" | 4 | ML concept |
| "fine-tuning" | 4 | ML concept |
| "inference" | 4 | ML concept |
| "API" | 3 | General tech |
| "security" | 4 | General security |
| "authentication" | 3 | Security concept |
| "authorization" | 3 | Security concept |
| "machine learning" | 4 | General ML |
| "artificial intelligence" | 4 | General AI |

**Maximum from Tier 3:** 20 points

### Negative Keywords (Penalties)

Reduce relevance — indicate off-topic or problematic content.

| Keyword/Phrase | Penalty | Notes |
|----------------|---------|-------|
| "hiring" | -15 | Job post |
| "job opening" | -15 | Job post |
| "we're hiring" | -20 | Job post |
| "career" | -10 | Job context |
| "giveaway" | -15 | Promotional |
| "airdrop" | -20 | Crypto spam |
| "NFT" | -10 | Off-topic |
| "crypto trading" | -15 | Off-topic |
| "follow for follow" | -20 | Spam |
| "affiliate link" | -15 | Promotional |
| "sponsored" | -10 | Promotional |
| "course discount" | -10 | Promotional |
| "free course" | -8 | Promotional |

**No maximum on penalties** — severe off-topic indicators should heavily penalize.

### Keyword Scoring Implementation

```python
class KeywordScorer:
    def __init__(self):
        self.tier1_keywords = {
            'agent security': 25,
            'agent safety': 25,
            'ai agent': 20,
            'agentic ai': 20,
            'agent runtime': 22,
            'agent monitoring': 22,
            'agent guardrails': 22,
            'agent verification': 22,
            'agent trust': 20,
            'autonomous agent': 18,
            'multi-agent': 18,
            'agent orchestration': 18,
            'llm guardrails': 20,
            'prompt injection': 20,
            'agent behavior': 18,
        }
        self.tier1_max = 40
        
        self.tier2_keywords = {
            'llm security': 15,
            'ai safety': 15,
            'tool use': 12,
            'function calling': 12,
            'agent framework': 12,
            'langchain': 10,
            'autogpt': 10,
            'crewai': 10,
            'agent api': 10,
            'ai risk': 12,
            'model safety': 12,
            'ai governance': 10,
            'ai compliance': 10,
            'enterprise ai': 8,
            'production ai': 8,
        }
        self.tier2_max = 30
        
        self.tier3_keywords = {
            'llm': 6,
            'gpt': 5,
            'claude': 5,
            'large language model': 6,
            'rag': 5,
            'vector database': 4,
            'embeddings': 4,
            'fine-tuning': 4,
            'inference': 4,
            'api': 3,
            'security': 4,
            'authentication': 3,
            'authorization': 3,
            'machine learning': 4,
            'artificial intelligence': 4,
        }
        self.tier3_max = 20
        
        self.negative_keywords = {
            'hiring': -15,
            'job opening': -15,
            "we're hiring": -20,
            'career': -10,
            'giveaway': -15,
            'airdrop': -20,
            'nft': -10,
            'crypto trading': -15,
            'follow for follow': -20,
            'affiliate link': -15,
            'sponsored': -10,
            'course discount': -10,
            'free course': -8,
        }
    
    def score(self, content: str) -> KeywordScoreResult:
        content_lower = content.lower()
        
        # Score each tier
        tier1_score = 0
        tier1_matches = []
        for keyword, points in self.tier1_keywords.items():
            if keyword in content_lower:
                tier1_score += points
                tier1_matches.append(keyword)
        tier1_score = min(tier1_score, self.tier1_max)
        
        tier2_score = 0
        tier2_matches = []
        for keyword, points in self.tier2_keywords.items():
            if keyword in content_lower:
                tier2_score += points
                tier2_matches.append(keyword)
        tier2_score = min(tier2_score, self.tier2_max)
        
        tier3_score = 0
        tier3_matches = []
        for keyword, points in self.tier3_keywords.items():
            if keyword in content_lower:
                tier3_score += points
                tier3_matches.append(keyword)
        tier3_score = min(tier3_score, self.tier3_max)
        
        # Calculate penalties
        penalty_score = 0
        penalty_matches = []
        for keyword, penalty in self.negative_keywords.items():
            if keyword in content_lower:
                penalty_score += penalty
                penalty_matches.append(keyword)
        
        # Total keyword score
        total = tier1_score + tier2_score + tier3_score + penalty_score
        total = max(0, total)  # Floor at 0
        
        return KeywordScoreResult(
            total=total,
            tier1_score=tier1_score,
            tier1_matches=tier1_matches,
            tier2_score=tier2_score,
            tier2_matches=tier2_matches,
            tier3_score=tier3_score,
            tier3_matches=tier3_matches,
            penalty_score=penalty_score,
            penalty_matches=penalty_matches,
        )
```

## 7.4.4 Classification Signal Definitions

### Classification Relevance Tiers

Map classifications to relevance values:

| Classification | Base Relevance | Tier |
|----------------|----------------|------|
| security_discussion | 35 | Core |
| agent_discussion | 35 | Core |
| help_seeking_solution (domain) | 30 | Core |
| pain_point_match (domain) | 28 | Core |
| tech_discussion | 25 | High |
| ai_discussion | 22 | High |
| industry_commentary | 18 | Medium |
| industry_news | 15 | Medium |
| competitor_mention | 20 | Medium |
| meme_humor (AI-related) | 12 | Low |
| general_engagement | 8 | Low |
| controversial_topic | 5 | Minimal |
| off_topic | 0 | None |

### Confidence Adjustment

Classification confidence affects relevance contribution:

```python
def adjust_for_confidence(base_relevance: int, confidence: int) -> float:
    """Adjust relevance score based on classification confidence."""
    
    # Confidence multiplier
    # 100% confidence = 1.0x
    # 80% confidence = 0.95x
    # 60% confidence = 0.85x
    # 40% confidence = 0.70x
    # 20% confidence = 0.50x
    
    if confidence >= 90:
        multiplier = 1.0
    elif confidence >= 70:
        multiplier = 0.85 + (confidence - 70) * 0.005
    elif confidence >= 50:
        multiplier = 0.70 + (confidence - 50) * 0.0075
    else:
        multiplier = 0.50 + confidence * 0.004
    
    return base_relevance * multiplier
```

### Secondary Classification Bonus

Secondary classifications can add relevance:

```python
def calculate_secondary_bonus(secondary_classifications: List[dict]) -> float:
    """Calculate bonus from secondary classifications."""
    
    bonus = 0
    
    for secondary in secondary_classifications[:3]:  # Top 3 only
        cls = secondary['classification']
        confidence = secondary['confidence']
        
        # Secondary contributes at 30% of primary rate
        base = CLASSIFICATION_RELEVANCE[cls] * 0.3
        adjusted = adjust_for_confidence(base, confidence)
        bonus += adjusted
    
    # Cap secondary bonus
    return min(bonus, 15)
```

### Classification Scoring Implementation

```python
CLASSIFICATION_RELEVANCE = {
    'security_discussion': 35,
    'agent_discussion': 35,
    'help_seeking_solution': 30,
    'pain_point_match': 28,
    'tech_discussion': 25,
    'ai_discussion': 22,
    'industry_commentary': 18,
    'industry_news': 15,
    'competitor_mention': 20,
    'meme_humor': 12,
    'general_engagement': 8,
    'controversial_topic': 5,
    'off_topic': 0,
}

def score_classification(classification_result: dict) -> ClassificationScoreResult:
    """Score relevance based on classification."""
    
    primary = classification_result['primary']
    primary_confidence = classification_result['primary_confidence']
    secondary = classification_result.get('secondary', [])
    
    # Base score from primary classification
    base_relevance = CLASSIFICATION_RELEVANCE.get(primary, 10)
    adjusted_primary = adjust_for_confidence(base_relevance, primary_confidence)
    
    # Bonus from secondary classifications
    secondary_bonus = calculate_secondary_bonus(secondary)
    
    # Total classification score
    total = adjusted_primary + secondary_bonus
    
    return ClassificationScoreResult(
        total=total,
        primary_contribution=adjusted_primary,
        secondary_contribution=secondary_bonus,
        primary_classification=primary,
        primary_confidence=primary_confidence,
    )
```

## 7.4.5 Context Signal Definitions

### Platform Context

Different platforms have different baseline relevance:

| Platform | Modifier | Rationale |
|----------|----------|-----------|
| Twitter | +0 | Baseline |
| Reddit | +3 | Often more technical |
| LinkedIn | +2 | Professional audience |
| Discord | +0 | Varies widely |

### Community Context

Specific communities have relevance modifiers:

**High-relevance communities (+8 to +12):**
- r/MachineLearning
- r/LocalLLaMA
- r/LangChain
- AI-focused Discord servers
- Tech Twitter lists

**Medium-relevance communities (+3 to +7):**
- r/artificial
- r/programming
- General tech subreddits
- Professional LinkedIn groups

**Low-relevance communities (-5 to +2):**
- General subreddits
- Non-tech communities
- Consumer-focused spaces

```python
COMMUNITY_RELEVANCE = {
    # Reddit
    'machinelearning': 12,
    'localllama': 12,
    'langchain': 10,
    'autogpt': 10,
    'artificial': 8,
    'learnmachinelearning': 6,
    'programming': 4,
    'python': 4,
    'chatgpt': 5,
    'openai': 6,
    
    # Default
    '_default_relevant': 3,
    '_default_unknown': 0,
    '_default_irrelevant': -5,
}

def score_community(platform: str, community: str) -> int:
    """Score relevance based on community."""
    
    if not community:
        return 0
    
    community_lower = community.lower()
    
    if community_lower in COMMUNITY_RELEVANCE:
        return COMMUNITY_RELEVANCE[community_lower]
    
    # Check for AI/tech indicators
    ai_indicators = ['ai', 'ml', 'llm', 'agent', 'security', 'tech', 'dev']
    if any(ind in community_lower for ind in ai_indicators):
        return COMMUNITY_RELEVANCE['_default_relevant']
    
    return COMMUNITY_RELEVANCE['_default_unknown']
```

### Conversation Context

Context from the conversation thread:

| Signal | Modifier | Detection |
|--------|----------|-----------|
| Reply to high-relevance post | +5 | Parent post is in our domain |
| Part of relevant thread | +3 | Thread topic is relevant |
| Standalone post | +0 | No thread context |
| Reply to off-topic | -3 | Parent is off-topic |

```python
def score_conversation_context(post: NormalizedPost) -> int:
    """Score based on conversation context."""
    
    # Check if this is a reply
    if not post.platform_data.get('is_reply'):
        return 0
    
    # If we have parent post info
    parent_classification = post.platform_data.get('parent_classification')
    if parent_classification:
        if parent_classification in ['security_discussion', 'agent_discussion']:
            return 5
        elif parent_classification in ['tech_discussion', 'ai_discussion']:
            return 3
        elif parent_classification == 'off_topic':
            return -3
    
    return 0
```

### Source Context

The source that discovered the post provides context:

```python
def score_source_context(source: Source) -> int:
    """Score based on source characteristics."""
    
    bonus = 0
    
    # Source type bonuses
    if source.source_type == 'mention':
        bonus += 5  # Mentions are highly relevant
    elif source.source_type == 'keyword' and source.priority == 'high':
        bonus += 3  # High-priority keyword matches
    
    # Source weight influence (weight ranges 0.5-2.0)
    # Convert to small bonus (-2 to +4)
    weight_bonus = int((source.weight - 1.0) * 4)
    bonus += weight_bonus
    
    return bonus
```

### Context Scoring Implementation

```python
def score_context(post: NormalizedPost, source: Source) -> ContextScoreResult:
    """Score relevance based on context signals."""
    
    platform_score = PLATFORM_MODIFIERS.get(post.platform, 0)
    
    community = post.platform_data.get('subreddit') or post.platform_data.get('community')
    community_score = score_community(post.platform, community)
    
    conversation_score = score_conversation_context(post)
    
    source_score = score_source_context(source)
    
    total = platform_score + community_score + conversation_score + source_score
    
    return ContextScoreResult(
        total=total,
        platform_contribution=platform_score,
        community_contribution=community_score,
        conversation_contribution=conversation_score,
        source_contribution=source_score,
        community_name=community,
    )
```

## 7.4.6 Author Signal Definitions

### Author Bio Analysis

Author bio keywords indicate relevance:

**High-relevance bio keywords (+10 each, max +20):**
- "AI", "ML", "machine learning"
- "agent", "agentic"
- "security", "safety"
- "LLM", "GPT"
- "engineer", "developer", "researcher"

**Medium-relevance bio keywords (+5 each, max +10):**
- "tech", "software"
- "founder", "CEO", "CTO"
- "startup"
- "data scientist"

```python
def score_author_bio(bio: str) -> int:
    """Score author relevance from bio."""
    
    if not bio:
        return 0
    
    bio_lower = bio.lower()
    
    high_keywords = ['ai', 'ml', 'machine learning', 'agent', 'agentic', 
                     'security', 'safety', 'llm', 'gpt', 'engineer', 
                     'developer', 'researcher']
    medium_keywords = ['tech', 'software', 'founder', 'ceo', 'cto', 
                       'startup', 'data scientist']
    
    high_score = sum(5 for kw in high_keywords if kw in bio_lower)
    high_score = min(high_score, 20)
    
    medium_score = sum(3 for kw in medium_keywords if kw in bio_lower)
    medium_score = min(medium_score, 10)
    
    return high_score + medium_score
```

### Author History Analysis

If we've seen this author before:

| Signal | Modifier | Detection |
|--------|----------|-----------|
| Author previously posted relevant content | +5 | Historical data |
| Author previously engaged with us | +8 | Relationship tracking |
| Author consistently on-topic | +3 | Pattern analysis |
| Author typically off-topic | -5 | Pattern analysis |

```python
def score_author_history(author_id: UUID) -> int:
    """Score based on author's history with us."""
    
    author_stats = get_author_stats(author_id)
    
    if not author_stats:
        return 0
    
    score = 0
    
    # Previous relevant posts
    if author_stats.relevant_posts_count > 0:
        score += min(5, author_stats.relevant_posts_count)
    
    # Previous engagement with us
    if author_stats.engagement_with_us_count > 0:
        score += 8
    
    # Consistency
    if author_stats.avg_relevance_score:
        if author_stats.avg_relevance_score >= 60:
            score += 3
        elif author_stats.avg_relevance_score < 30:
            score -= 5
    
    return score
```

### Author Scoring Implementation

```python
def score_author(post: NormalizedPost) -> AuthorScoreResult:
    """Score relevance based on author signals."""
    
    author = post.author
    
    bio_score = score_author_bio(author.bio)
    history_score = score_author_history(author.id) if author.id else 0
    
    total = bio_score + history_score
    
    return AuthorScoreResult(
        total=total,
        bio_contribution=bio_score,
        history_contribution=history_score,
        author_handle=author.handle,
    )
```

## 7.4.7 Relevance Score Calculation

### Score Formula

Total relevance score combines all signal categories:

```
relevance_score = keyword_score + classification_score + context_score + author_score
```

**Maximum theoretical scores:**
- Keywords: 90 (40 + 30 + 20)
- Classification: 50 (35 + 15)
- Context: 25 (12 + 5 + 5 + 3)
- Author: 30 (20 + 10)
- **Total possible:** ~195

**Normalization:**
Scale to 0-100 range.

### Normalization Approach

```python
def normalize_relevance_score(raw_score: float) -> int:
    """Normalize raw relevance score to 0-100."""
    
    # Expected typical range: 0-120
    # High-relevance posts: 60-100 raw
    # Low-relevance posts: 0-30 raw
    
    # Use logarithmic scaling for high scores
    if raw_score <= 0:
        return 0
    elif raw_score <= 100:
        # Linear mapping for normal range
        return int(raw_score)
    else:
        # Compress scores above 100
        excess = raw_score - 100
        compressed_excess = 100 * (1 - 1 / (1 + excess / 50))
        return min(100, int(100 + compressed_excess * 0.1))
```

**Alternative: Percentile-based normalization:**

```python
def normalize_by_percentile(raw_score: float, historical_scores: List[float]) -> int:
    """Normalize based on historical distribution."""
    
    # Calculate percentile
    below_count = sum(1 for s in historical_scores if s < raw_score)
    percentile = (below_count / len(historical_scores)) * 100
    
    return int(percentile)
```

### Complete Relevance Scoring

```python
@dataclass
class RelevanceScoreResult:
    total: int                          # Normalized 0-100
    raw_total: float                    # Pre-normalization
    
    keyword_score: KeywordScoreResult
    classification_score: ClassificationScoreResult
    context_score: ContextScoreResult
    author_score: AuthorScoreResult
    
    signals: List[SignalContribution]   # All contributing signals
    scored_at: datetime


def calculate_relevance_score(
    post: NormalizedPost,
    classification: dict,
    source: Source
) -> RelevanceScoreResult:
    """Calculate complete relevance score for a post."""
    
    # Score each category
    keyword_result = keyword_scorer.score(post.content_text)
    classification_result = score_classification(classification)
    context_result = score_context(post, source)
    author_result = score_author(post)
    
    # Sum raw scores
    raw_total = (
        keyword_result.total +
        classification_result.total +
        context_result.total +
        author_result.total
    )
    
    # Normalize
    normalized_total = normalize_relevance_score(raw_total)
    
    # Collect all signals
    signals = []
    
    for keyword in keyword_result.tier1_matches:
        signals.append(SignalContribution(
            category='keyword_tier1',
            signal=keyword,
            contribution=keyword_scorer.tier1_keywords[keyword],
        ))
    
    # ... collect other signals
    
    return RelevanceScoreResult(
        total=normalized_total,
        raw_total=raw_total,
        keyword_score=keyword_result,
        classification_score=classification_result,
        context_score=context_result,
        author_score=author_result,
        signals=signals,
        scored_at=datetime.now(timezone.utc),
    )
```

## 7.4.8 Score Thresholds and Tiers

### Relevance Tiers

| Tier | Score Range | Interpretation | Action |
|------|-------------|----------------|--------|
| Excellent | 80-100 | Extremely relevant, core domain | Prioritize heavily |
| High | 60-79 | Highly relevant, should engage | Standard priority |
| Medium | 40-59 | Moderately relevant, worth considering | Lower priority |
| Low | 20-39 | Tangentially relevant | Only if capacity |
| Minimal | 0-19 | Probably not relevant | Usually filter |

### Filtering Thresholds

**Default minimum threshold:** 40

Posts below threshold are filtered before opportunity scoring.

**Configurable per campaign:**
- Strict campaigns: 50+
- Standard campaigns: 40
- Exploratory campaigns: 30

```python
def should_filter_for_relevance(score: int, campaign_config: dict) -> bool:
    """Determine if post should be filtered for low relevance."""
    
    threshold = campaign_config.get('min_relevance_score', 40)
    return score < threshold
```

### Threshold Tuning

Monitor threshold effectiveness:

```python
def analyze_threshold_effectiveness(campaign_id: UUID, days: int = 30) -> dict:
    """Analyze how threshold affects engagement quality."""
    
    posts = get_engaged_posts(campaign_id, days)
    
    # Group by relevance tier
    tiers = {
        'excellent': [p for p in posts if p.relevance_score >= 80],
        'high': [p for p in posts if 60 <= p.relevance_score < 80],
        'medium': [p for p in posts if 40 <= p.relevance_score < 60],
        'low': [p for p in posts if p.relevance_score < 40],
    }
    
    # Calculate engagement success per tier
    results = {}
    for tier, tier_posts in tiers.items():
        if not tier_posts:
            continue
        
        avg_engagement = sum(p.response_engagement for p in tier_posts) / len(tier_posts)
        success_rate = sum(1 for p in tier_posts if p.was_successful) / len(tier_posts)
        
        results[tier] = {
            'count': len(tier_posts),
            'avg_engagement': avg_engagement,
            'success_rate': success_rate,
        }
    
    return results
```

## 7.4.9 Score Transparency and Explainability

### Score Breakdown Structure

Every relevance score should be explainable:

```python
@dataclass
class RelevanceExplanation:
    total_score: int
    tier: str  # excellent, high, medium, low, minimal
    
    summary: str  # Human-readable summary
    
    top_positive_signals: List[SignalExplanation]
    top_negative_signals: List[SignalExplanation]
    
    category_breakdown: Dict[str, CategoryBreakdown]


@dataclass
class SignalExplanation:
    signal_name: str
    signal_value: Any
    contribution: int
    explanation: str


@dataclass
class CategoryBreakdown:
    category: str
    score: int
    max_possible: int
    percentage: float
    details: str
```

### Generating Explanations

```python
def explain_relevance_score(result: RelevanceScoreResult) -> RelevanceExplanation:
    """Generate human-readable explanation of relevance score."""
    
    # Determine tier
    if result.total >= 80:
        tier = 'excellent'
    elif result.total >= 60:
        tier = 'high'
    elif result.total >= 40:
        tier = 'medium'
    elif result.total >= 20:
        tier = 'low'
    else:
        tier = 'minimal'
    
    # Generate summary
    summary = f"Relevance score {result.total}/100 ({tier}). "
    
    if result.keyword_score.tier1_matches:
        summary += f"Contains core keywords: {', '.join(result.keyword_score.tier1_matches[:3])}. "
    
    if result.classification_score.primary_classification in ['security_discussion', 'agent_discussion']:
        summary += f"Classified as {result.classification_score.primary_classification}. "
    
    # Top positive signals
    positive_signals = sorted(
        [s for s in result.signals if s.contribution > 0],
        key=lambda s: s.contribution,
        reverse=True
    )[:5]
    
    # Top negative signals
    negative_signals = sorted(
        [s for s in result.signals if s.contribution < 0],
        key=lambda s: s.contribution
    )[:3]
    
    # Category breakdown
    category_breakdown = {
        'keywords': CategoryBreakdown(
            category='keywords',
            score=result.keyword_score.total,
            max_possible=90,
            percentage=result.keyword_score.total / 90 * 100,
            details=f"Tier 1: {result.keyword_score.tier1_score}, "
                    f"Tier 2: {result.keyword_score.tier2_score}, "
                    f"Tier 3: {result.keyword_score.tier3_score}"
        ),
        'classification': CategoryBreakdown(
            category='classification',
            score=int(result.classification_score.total),
            max_possible=50,
            percentage=result.classification_score.total / 50 * 100,
            details=f"{result.classification_score.primary_classification} "
                    f"({result.classification_score.primary_confidence}% confidence)"
        ),
        'context': CategoryBreakdown(
            category='context',
            score=result.context_score.total,
            max_possible=25,
            percentage=result.context_score.total / 25 * 100,
            details=f"Community: {result.context_score.community_contribution}"
        ),
        'author': CategoryBreakdown(
            category='author',
            score=result.author_score.total,
            max_possible=30,
            percentage=result.author_score.total / 30 * 100,
            details=f"Bio: {result.author_score.bio_contribution}, "
                    f"History: {result.author_score.history_contribution}"
        ),
    }
    
    return RelevanceExplanation(
        total_score=result.total,
        tier=tier,
        summary=summary,
        top_positive_signals=[
            SignalExplanation(
                signal_name=s.signal,
                signal_value=s.value if hasattr(s, 'value') else None,
                contribution=s.contribution,
                explanation=f"+{s.contribution} from {s.category}"
            )
            for s in positive_signals
        ],
        top_negative_signals=[
            SignalExplanation(
                signal_name=s.signal,
                signal_value=s.value if hasattr(s, 'value') else None,
                contribution=s.contribution,
                explanation=f"{s.contribution} from {s.category}"
            )
            for s in negative_signals
        ],
        category_breakdown=category_breakdown,
    )
```

### API Endpoint for Score Explanation

```python
@app.get("/api/v1/posts/{post_id}/relevance/explain")
async def explain_post_relevance(post_id: UUID):
    """Get detailed explanation of a post's relevance score."""
    
    post = get_post(post_id)
    if not post:
        raise HTTPException(404, "Post not found")
    
    if not post.scores or 'relevance' not in post.scores:
        raise HTTPException(400, "Post not yet scored")
    
    explanation = explain_relevance_score(post.scores['relevance'])
    
    return {
        'post_id': post_id,
        'explanation': asdict(explanation),
    }
```

## 7.4.10 Score Storage

### Storage Structure

Relevance scores are stored in the `scores` JSONB column:

```json
{
  "relevance": {
    "total": 72,
    "raw_total": 85.5,
    "keyword": {
      "total": 35,
      "tier1_score": 20,
      "tier1_matches": ["ai agent", "agent security"],
      "tier2_score": 15,
      "tier2_matches": ["langchain"],
      "tier3_score": 0,
      "tier3_matches": [],
      "penalty_score": 0,
      "penalty_matches": []
    },
    "classification": {
      "total": 30.5,
      "primary_contribution": 28.0,
      "secondary_contribution": 2.5,
      "primary_classification": "help_seeking_solution",
      "primary_confidence": 85
    },
    "context": {
      "total": 12,
      "platform": 0,
      "community": 10,
      "conversation": 0,
      "source": 2,
      "community_name": "LocalLLaMA"
    },
    "author": {
      "total": 8,
      "bio": 8,
      "history": 0,
      "author_handle": "ml_developer"
    },
    "scored_at": "2024-01-15T14:35:00Z"
  }
}
```

### Updating Posts with Scores

```python
def store_relevance_score(post_id: UUID, result: RelevanceScoreResult):
    """Store relevance score in database."""
    
    score_data = {
        'relevance': {
            'total': result.total,
            'raw_total': result.raw_total,
            'keyword': asdict(result.keyword_score),
            'classification': asdict(result.classification_score),
            'context': asdict(result.context_score),
            'author': asdict(result.author_score),
            'scored_at': result.scored_at.isoformat(),
        }
    }
    
    db.execute("""
        UPDATE discovered_posts
        SET 
            scores = COALESCE(scores, '{}'::jsonb) || %(score_data)s::jsonb,
            status = 'relevance_scored',
            updated_at = NOW()
        WHERE id = %(post_id)s
    """, {
        'post_id': post_id,
        'score_data': json.dumps(score_data),
    })
```

### Querying by Relevance

```sql
-- Find high-relevance posts
SELECT * FROM discovered_posts
WHERE (scores->'relevance'->>'total')::int >= 70
ORDER BY (scores->'relevance'->>'total')::int DESC;

-- Find posts with specific keyword matches
SELECT * FROM discovered_posts
WHERE scores->'relevance'->'keyword'->'tier1_matches' ? 'agent security';

-- Average relevance by source
SELECT 
    source_id,
    AVG((scores->'relevance'->>'total')::int) as avg_relevance
FROM discovered_posts
WHERE scores IS NOT NULL
GROUP BY source_id
ORDER BY avg_relevance DESC;
```

## 7.4.11 Relevance Scoring Pipeline

### Pipeline Integration

Relevance scoring happens after classification:

```
Classification → Relevance Scoring → Opportunity Scoring → Filtering → Prioritization
```

### Batch Processing

```python
async def score_relevance_batch(post_ids: List[UUID]) -> List[RelevanceScoreResult]:
    """Score relevance for a batch of posts."""
    
    results = []
    
    for post_id in post_ids:
        post = get_post(post_id)
        source = get_source(post.source_id)
        classification = post.classification
        
        if not classification:
            log.warning(f"Post {post_id} not classified, skipping relevance scoring")
            continue
        
        result = calculate_relevance_score(post, classification, source)
        store_relevance_score(post_id, result)
        
        results.append(result)
    
    return results
```

### Worker Implementation

```python
async def relevance_scoring_worker():
    """Worker that processes posts needing relevance scoring."""
    
    while True:
        # Get batch of classified posts
        posts = db.query("""
            SELECT id FROM discovered_posts
            WHERE status = 'classified'
            ORDER BY discovered_at ASC
            LIMIT 100
            FOR UPDATE SKIP LOCKED
        """)
        
        if not posts:
            await asyncio.sleep(5)  # Wait for more posts
            continue
        
        post_ids = [p.id for p in posts]
        
        try:
            results = await score_relevance_batch(post_ids)
            log.info(f"Scored relevance for {len(results)} posts")
            
            # Update metrics
            for result in results:
                relevance_score_histogram.observe(result.total)
        
        except Exception as e:
            log.error(f"Error scoring relevance batch: {e}")
            # Mark posts for retry
            mark_posts_for_retry(post_ids, 'relevance_scoring')
```

## 7.4.12 Monitoring and Metrics

### Relevance Metrics

```python
# Score distribution
relevance_score_histogram = Histogram(
    'relevance_score',
    'Distribution of relevance scores',
    buckets=[10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
)

# Scores by tier
relevance_tier_counter = Counter(
    'relevance_tier_total',
    'Posts by relevance tier',
    ['tier']  # excellent, high, medium, low, minimal
)

# Signal contributions
relevance_signal_contribution = Histogram(
    'relevance_signal_contribution',
    'Contribution of signals to relevance',
    ['signal_category'],  # keyword, classification, context, author
    buckets=[0, 5, 10, 15, 20, 30, 40, 50]
)

# Filtering
relevance_filtered_counter = Counter(
    'relevance_filtered_total',
    'Posts filtered for low relevance',
    ['threshold']
)

# Scoring performance
relevance_scoring_latency = Histogram(
    'relevance_scoring_latency_seconds',
    'Time to score relevance',
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1]
)
```

### Dashboard Metrics

1. **Score Distribution:** Histogram of scores over time
2. **Tier Breakdown:** Pie chart of posts per tier
3. **Top Keywords:** Most common matching keywords
4. **Signal Contributions:** Average contribution per category
5. **Filter Rate:** Percentage filtered for low relevance
6. **Score Trends:** Average score over time (by day/week)

### Alerting

```yaml
# Average relevance dropping
- alert: RelevanceScoreDropping
  expr: avg(relevance_score) < 45
  for: 1h
  labels:
    severity: warning
  annotations:
    summary: "Average relevance score is low"
    description: "Average score {{ $value }} is below 45"

# High filter rate
- alert: RelevanceFilterRateHigh
  expr: rate(relevance_filtered_total[1h]) / rate(relevance_scored_total[1h]) > 0.8
  for: 30m
  labels:
    severity: warning
  annotations:
    summary: "High relevance filter rate"
    description: "{{ $value | humanizePercentage }} of posts filtered"
```

## 7.4.13 Implementation Guidance for Neoclaw

### Implementation Order

1. **Define keyword lists**
   - Tier 1, 2, 3 keywords with points
   - Negative keywords with penalties
   - Test with sample content

2. **Build keyword scorer**
   - Matching logic
   - Point calculation
   - Cap enforcement

3. **Build classification scorer**
   - Classification → relevance mapping
   - Confidence adjustment
   - Secondary bonus calculation

4. **Build context scorer**
   - Platform modifiers
   - Community scoring
   - Source context

5. **Build author scorer**
   - Bio analysis
   - History lookup (if available)

6. **Combine into relevance scorer**
   - Score calculation
   - Normalization
   - Result structure

7. **Add storage**
   - Score persistence
   - Index creation

8. **Build explanation system**
   - Breakdown generation
   - API endpoint

9. **Add monitoring**
   - Metrics collection
   - Dashboard
   - Alerting

### Testing Checklist

#### Unit Tests
- [ ] Keyword matching (all tiers)
- [ ] Penalty application
- [ ] Classification scoring
- [ ] Confidence adjustment
- [ ] Context scoring
- [ ] Author scoring
- [ ] Score normalization
- [ ] Explanation generation

#### Integration Tests
- [ ] Full scoring pipeline
- [ ] Batch processing
- [ ] Score storage
- [ ] Score retrieval

#### Validation Tests
- [ ] Sample posts with known relevance (manual labeling)
- [ ] Score distribution matches expectations
- [ ] High-relevance posts are actually relevant
- [ ] Low-relevance posts are actually less relevant

### Common Pitfalls

**Keyword overlap:**
"AI agent security" contains "AI", "agent", and "security". Don't triple-count. Match longest first.

**Score inflation:**
Too many positive signals can inflate scores. Use caps per category.

**Score deflation:**
Too strict penalties can deflate scores. Balance carefully.

**Missing normalization:**
Raw scores vary widely. Always normalize for consistent thresholds.

**Stale keyword lists:**
Industry terminology evolves. Review and update keyword lists periodically.

---

**END OF SECTION 7.4**

Section 7.5 continues with Opportunity Detection specification.
-e 


# SECTION 7.5: OPPORTUNITY DETECTION

## 7.5.1 What Opportunity Detection Is

### The Core Concept

Opportunity Detection measures how valuable engaging with a post would be, independent of its topical relevance. While relevance scoring (Section 7.4) asks "Is this about our domain?", opportunity detection asks "Is engaging with this worth it?"

**Input:** Posts with relevance scores from Section 7.4
**Output:** Posts with opportunity scores (0-100)

A highly relevant post may be a poor opportunity:
- Posted 3 days ago (too old, conversation over)
- Has 0 engagement (no one is watching)
- From a bot account (no value)
- Already has 500 replies (our response would be buried)

A moderately relevant post may be an excellent opportunity:
- Posted 30 minutes ago (fresh, timely)
- Has 200 likes and growing (people are watching)
- From an influential author (high visibility)
- Is an unanswered question (we can provide unique value)

### Why Opportunity Matters

**Resource optimization:**
Jen has limited capacity. Engaging with high-opportunity posts maximizes impact.

**Visibility:**
High-opportunity posts get our response seen by more people.

**Conversion potential:**
Posts where users are actively seeking help have higher conversion likelihood.

**Timing:**
Fresh posts in active conversations have engagement momentum.

**Relationship building:**
Engaging with influential authors builds valuable relationships.

### Opportunity Dimensions

Opportunity is multi-dimensional:

**Engagement potential:** Will our response get visibility?
- Current engagement level
- Engagement velocity
- Reply count vs visibility ratio

**Author value:** Is the author worth engaging with?
- Follower count and influence
- Industry relevance
- Potential customer indicators

**Conversation state:** Is this a good time to engage?
- Post freshness
- Conversation openness
- Unanswered question status

**Response opportunity:** Can we add unique value?
- Question format (we can answer)
- Gap in existing responses
- Our expertise alignment

**Strategic value:** Does this align with our goals?
- Goal alignment (from classification)
- Campaign priorities
- Relationship potential

## 7.5.2 Signal Categories

### Category 1: Engagement Signals

Measure current and potential engagement.

**Current engagement:**
- Like/favorite count
- Reply/comment count
- Share/retweet count
- View/impression count

**Engagement velocity:**
- Engagement rate (engagement / views)
- Engagement growth rate
- Trending indicators

**Engagement quality:**
- Reply quality (substantive vs low-effort)
- Engagement from relevant accounts
- Virality indicators

### Category 2: Author Signals

Measure author influence and value.

**Influence metrics:**
- Follower count
- Engagement rate (author's typical)
- Verified status
- Industry recognition

**Relevance metrics:**
- Author's domain expertise
- Author's typical content
- Author's audience alignment

**Relationship metrics:**
- Previous interactions
- Relationship status
- Engagement history

### Category 3: Timing Signals

Measure temporal opportunity.

**Freshness:**
- Post age
- Time since last activity
- Conversation recency

**Urgency:**
- Trending status
- Breaking news relevance
- Time-sensitive content

**Window:**
- Optimal engagement window
- Platform-specific timing
- Author's active hours

### Category 4: Conversation Signals

Measure conversation state and opportunity.

**Question indicators:**
- Question format
- Help-seeking language
- Unanswered status

**Conversation openness:**
- Reply count
- Response saturation
- Conversation depth

**Gap opportunities:**
- Missing perspectives
- Incorrect information to correct
- Expertise gap

### Category 5: Strategic Signals

Measure strategic alignment.

**Goal alignment:**
- Classification × goal multiplier
- Campaign priority match
- Strategic importance

**Competitive signals:**
- Competitor discussion
- Market positioning opportunity
- Differentiation chance

## 7.5.3 Engagement Signal Definitions

### Like/Favorite Count

Raw engagement indicates interest.

| Like Count | Points | Rationale |
|------------|--------|-----------|
| 0-5 | 0 | Very low interest |
| 6-20 | 5 | Some interest |
| 21-50 | 10 | Moderate interest |
| 51-100 | 15 | Good interest |
| 101-250 | 20 | High interest |
| 251-500 | 23 | Very high interest |
| 501-1000 | 25 | Viral potential |
| 1000+ | 27 | Major visibility |

**Maximum contribution:** 27 points

**Platform adjustments:**
- Twitter: Use raw counts
- Reddit: Use score (upvotes - downvotes)
- LinkedIn: Adjust up 50% (lower typical engagement)

```python
def score_likes(likes: int, platform: str) -> int:
    """Score based on like count."""
    
    # Platform adjustment
    if platform == 'linkedin':
        likes = int(likes * 1.5)
    
    if likes <= 5:
        return 0
    elif likes <= 20:
        return 5
    elif likes <= 50:
        return 10
    elif likes <= 100:
        return 15
    elif likes <= 250:
        return 20
    elif likes <= 500:
        return 23
    elif likes <= 1000:
        return 25
    else:
        return 27
```

### Reply/Comment Count

Replies indicate conversation activity.

| Reply Count | Points | Rationale |
|-------------|--------|-----------|
| 0 | 8 | Unanswered - opportunity! |
| 1-3 | 10 | Light conversation |
| 4-10 | 12 | Active conversation |
| 11-25 | 10 | Busy conversation |
| 26-50 | 6 | Crowded |
| 51-100 | 3 | Very crowded |
| 100+ | 0 | Too crowded to stand out |

**Note:** Zero replies is high opportunity (first responder advantage), but moderate replies is highest (active conversation without saturation).

**Maximum contribution:** 12 points

```python
def score_replies(replies: int) -> int:
    """Score based on reply count."""
    
    if replies == 0:
        return 8  # Unanswered opportunity
    elif replies <= 3:
        return 10
    elif replies <= 10:
        return 12  # Sweet spot
    elif replies <= 25:
        return 10
    elif replies <= 50:
        return 6
    elif replies <= 100:
        return 3
    else:
        return 0  # Too crowded
```

### Share/Retweet Count

Shares indicate amplification potential.

| Share Count | Points | Rationale |
|-------------|--------|-----------|
| 0 | 0 | No amplification |
| 1-5 | 3 | Minimal sharing |
| 6-20 | 6 | Some sharing |
| 21-50 | 9 | Good sharing |
| 51-100 | 12 | High sharing |
| 100+ | 15 | Viral sharing |

**Maximum contribution:** 15 points

```python
def score_shares(shares: int) -> int:
    """Score based on share count."""
    
    if shares == 0:
        return 0
    elif shares <= 5:
        return 3
    elif shares <= 20:
        return 6
    elif shares <= 50:
        return 9
    elif shares <= 100:
        return 12
    else:
        return 15
```

### View/Impression Count

Views indicate visibility (when available).

| Views | Points | Rationale |
|-------|--------|-----------|
| 0-100 | 0 | Very low visibility |
| 101-500 | 3 | Low visibility |
| 501-2000 | 6 | Moderate visibility |
| 2001-10000 | 9 | Good visibility |
| 10001-50000 | 12 | High visibility |
| 50000+ | 15 | Massive visibility |

**Note:** Views not always available. Score 0 if unavailable (don't penalize).

**Maximum contribution:** 15 points

### Engagement Rate

Engagement rate = (likes + replies + shares) / views

| Rate | Points | Interpretation |
|------|--------|----------------|
| < 0.5% | -3 | Low engagement |
| 0.5-1% | 0 | Normal |
| 1-2% | 3 | Good |
| 2-5% | 6 | High |
| 5%+ | 10 | Exceptional |

**Maximum contribution:** 10 points (can be negative)

```python
def score_engagement_rate(likes: int, replies: int, shares: int, views: int) -> int:
    """Score based on engagement rate."""
    
    if not views or views == 0:
        return 0  # Can't calculate
    
    total_engagement = likes + replies + shares
    rate = (total_engagement / views) * 100
    
    if rate < 0.5:
        return -3
    elif rate < 1:
        return 0
    elif rate < 2:
        return 3
    elif rate < 5:
        return 6
    else:
        return 10
```

### Engagement Velocity

How fast is engagement growing?

**Calculation:**
```
velocity = engagement_count / hours_since_posted
```

| Velocity | Points | Interpretation |
|----------|--------|----------------|
| < 1/hr | 0 | Slow |
| 1-5/hr | 5 | Moderate |
| 5-20/hr | 10 | Fast |
| 20-100/hr | 15 | Very fast |
| 100+/hr | 20 | Viral |

**Maximum contribution:** 20 points

```python
def score_engagement_velocity(
    likes: int, 
    replies: int, 
    shares: int, 
    hours_since_posted: float
) -> int:
    """Score based on engagement velocity."""
    
    if hours_since_posted <= 0:
        hours_since_posted = 0.1  # Avoid division by zero
    
    total_engagement = likes + replies + shares
    velocity = total_engagement / hours_since_posted
    
    if velocity < 1:
        return 0
    elif velocity < 5:
        return 5
    elif velocity < 20:
        return 10
    elif velocity < 100:
        return 15
    else:
        return 20
```

### Complete Engagement Scoring

```python
@dataclass
class EngagementScoreResult:
    total: int
    likes_contribution: int
    replies_contribution: int
    shares_contribution: int
    views_contribution: int
    rate_contribution: int
    velocity_contribution: int
    
    raw_metrics: Dict[str, int]


def score_engagement(post: NormalizedPost) -> EngagementScoreResult:
    """Calculate engagement opportunity score."""
    
    engagement = post.engagement
    hours_old = (datetime.now(timezone.utc) - post.created_at).total_seconds() / 3600
    
    likes_score = score_likes(engagement.likes, post.platform)
    replies_score = score_replies(engagement.replies)
    shares_score = score_shares(engagement.shares)
    views_score = score_views(engagement.views) if engagement.views else 0
    rate_score = score_engagement_rate(
        engagement.likes, 
        engagement.replies, 
        engagement.shares, 
        engagement.views or 0
    )
    velocity_score = score_engagement_velocity(
        engagement.likes,
        engagement.replies,
        engagement.shares,
        hours_old
    )
    
    total = (
        likes_score +
        replies_score +
        shares_score +
        views_score +
        rate_score +
        velocity_score
    )
    
    return EngagementScoreResult(
        total=total,
        likes_contribution=likes_score,
        replies_contribution=replies_score,
        shares_contribution=shares_score,
        views_contribution=views_score,
        rate_contribution=rate_score,
        velocity_contribution=velocity_score,
        raw_metrics={
            'likes': engagement.likes,
            'replies': engagement.replies,
            'shares': engagement.shares,
            'views': engagement.views,
        }
    )
```

## 7.5.4 Author Signal Definitions

### Follower Count

Follower count indicates reach potential.

| Followers | Points | Tier |
|-----------|--------|------|
| 0-100 | 0 | Nano |
| 101-1000 | 5 | Micro |
| 1001-5000 | 10 | Small |
| 5001-10000 | 13 | Growing |
| 10001-25000 | 16 | Established |
| 25001-50000 | 18 | Influential |
| 50001-100000 | 20 | Major |
| 100000+ | 22 | Celebrity |

**Maximum contribution:** 22 points

**Platform adjustments:**
- LinkedIn: Multiply by 1.5 (professional audience more valuable)
- Reddit: Followers less meaningful, reduce by 50%

```python
def score_followers(followers: int, platform: str) -> int:
    """Score based on follower count."""
    
    if followers is None:
        return 5  # Unknown, assume average
    
    # Platform adjustment
    if platform == 'linkedin':
        followers = int(followers * 1.5)
    elif platform == 'reddit':
        followers = int(followers * 0.5)
    
    if followers <= 100:
        return 0
    elif followers <= 1000:
        return 5
    elif followers <= 5000:
        return 10
    elif followers <= 10000:
        return 13
    elif followers <= 25000:
        return 16
    elif followers <= 50000:
        return 18
    elif followers <= 100000:
        return 20
    else:
        return 22
```

### Verified Status

Verified accounts have higher credibility.

| Status | Points |
|--------|--------|
| Not verified | 0 |
| Verified | 8 |

**Maximum contribution:** 8 points

### Author Engagement Rate

How much engagement does this author typically get?

**Calculation:** Average engagement per post (if we have data)

| Typical Engagement | Points |
|--------------------|--------|
| Unknown | 3 |
| Low (< 10/post) | 0 |
| Moderate (10-50/post) | 5 |
| High (50-200/post) | 8 |
| Very high (200+/post) | 12 |

**Maximum contribution:** 12 points

### Author Domain Relevance

Is this author typically in our domain?

| Relevance | Points | Detection |
|-----------|--------|-----------|
| Core domain | 10 | Bio contains AI/agent/security |
| Adjacent domain | 6 | Bio contains tech/developer |
| General | 2 | Unknown or general |
| Off-domain | 0 | Clearly different domain |

**Maximum contribution:** 10 points

```python
def score_author_domain_relevance(author: NormalizedAuthor) -> int:
    """Score author's domain relevance."""
    
    if not author.bio:
        return 2  # Unknown
    
    bio_lower = author.bio.lower()
    
    # Core domain indicators
    core_indicators = ['ai agent', 'agent security', 'llm security', 
                       'ai safety', 'ml engineer', 'ai researcher']
    if any(ind in bio_lower for ind in core_indicators):
        return 10
    
    # Adjacent domain indicators
    adjacent_indicators = ['ai', 'machine learning', 'developer', 'engineer',
                           'security', 'software', 'tech', 'startup', 'founder']
    if any(ind in bio_lower for ind in adjacent_indicators):
        return 6
    
    return 2
```

### Potential Customer Indicators

Does the author look like a potential customer?

| Indicator | Points |
|-----------|--------|
| Works at relevant company | +5 |
| Decision-maker title (CTO, VP) | +5 |
| Building AI products | +5 |
| Previously engaged with competitors | +3 |
| Enterprise company | +3 |

**Maximum contribution:** 15 points (cumulative)

```python
def score_potential_customer(author: NormalizedAuthor) -> int:
    """Score likelihood author is potential customer."""
    
    score = 0
    
    if not author.bio:
        return 0
    
    bio_lower = author.bio.lower()
    
    # Decision-maker titles
    decision_titles = ['cto', 'vp engineering', 'head of', 'director', 
                       'chief', 'founder', 'co-founder']
    if any(title in bio_lower for title in decision_titles):
        score += 5
    
    # Building AI products
    building_indicators = ['building', 'working on', 'developing', 'creating']
    ai_indicators = ['ai', 'agent', 'llm', 'ml']
    if any(b in bio_lower for b in building_indicators) and \
       any(a in bio_lower for a in ai_indicators):
        score += 5
    
    # Enterprise indicators
    enterprise_indicators = ['enterprise', 'fortune 500', 'series', 'startup']
    if any(ind in bio_lower for ind in enterprise_indicators):
        score += 3
    
    return min(score, 15)  # Cap at 15
```

### Previous Relationship

Have we engaged with this author before?

| Relationship | Points |
|--------------|--------|
| No history | 0 |
| Discovered before | 2 |
| Engaged once | 5 |
| Multiple engagements | 8 |
| Positive relationship | 12 |
| Negative interaction | -10 |

**Maximum contribution:** 12 points (can be negative)

```python
def score_author_relationship(author_id: UUID) -> int:
    """Score based on relationship history."""
    
    history = get_author_engagement_history(author_id)
    
    if not history:
        return 0
    
    if history.negative_interaction:
        return -10
    
    if history.engagement_count >= 3 and history.positive_responses:
        return 12
    elif history.engagement_count >= 2:
        return 8
    elif history.engagement_count >= 1:
        return 5
    elif history.discovered_count > 0:
        return 2
    
    return 0
```

### Complete Author Scoring

```python
@dataclass
class AuthorScoreResult:
    total: int
    followers_contribution: int
    verified_contribution: int
    engagement_rate_contribution: int
    domain_relevance_contribution: int
    customer_potential_contribution: int
    relationship_contribution: int


def score_author_opportunity(post: NormalizedPost) -> AuthorScoreResult:
    """Calculate author opportunity score."""
    
    author = post.author
    
    followers_score = score_followers(author.followers_count, post.platform)
    verified_score = 8 if author.verified else 0
    engagement_rate_score = score_author_engagement_rate(author)
    domain_score = score_author_domain_relevance(author)
    customer_score = score_potential_customer(author)
    relationship_score = score_author_relationship(author.id) if author.id else 0
    
    total = (
        followers_score +
        verified_score +
        engagement_rate_score +
        domain_score +
        customer_score +
        relationship_score
    )
    
    return AuthorScoreResult(
        total=total,
        followers_contribution=followers_score,
        verified_contribution=verified_score,
        engagement_rate_contribution=engagement_rate_score,
        domain_relevance_contribution=domain_score,
        customer_potential_contribution=customer_score,
        relationship_contribution=relationship_score,
    )
```

## 7.5.5 Timing Signal Definitions

### Post Freshness

How old is the post?

| Age | Points | Rationale |
|-----|--------|-----------|
| < 30 min | 25 | Very fresh, first responder advantage |
| 30 min - 2 hr | 22 | Fresh, optimal engagement window |
| 2 - 6 hr | 18 | Still timely |
| 6 - 12 hr | 12 | Getting older |
| 12 - 24 hr | 6 | End of day |
| 24 - 48 hr | 2 | Old |
| 48+ hr | 0 | Too old |

**Maximum contribution:** 25 points

```python
def score_freshness(created_at: datetime) -> int:
    """Score based on post age."""
    
    now = datetime.now(timezone.utc)
    age_hours = (now - created_at).total_seconds() / 3600
    
    if age_hours < 0.5:
        return 25
    elif age_hours < 2:
        return 22
    elif age_hours < 6:
        return 18
    elif age_hours < 12:
        return 12
    elif age_hours < 24:
        return 6
    elif age_hours < 48:
        return 2
    else:
        return 0
```

### Platform-Specific Freshness

Different platforms have different conversation velocities:

**Twitter:** Fast-moving. Freshness matters more.
- Apply 1.2× multiplier to freshness score
- 24 hours is effectively "old"

**LinkedIn:** Slower. Content lasts longer.
- Apply 0.8× multiplier to freshness penalty
- Posts stay relevant for 48-72 hours

**Reddit:** Varies by subreddit.
- Hot posts: Freshness matters
- Discussions: Can engage for days
- Apply 0.9× multiplier

```python
def adjust_freshness_for_platform(base_score: int, platform: str) -> int:
    """Adjust freshness score for platform velocity."""
    
    multipliers = {
        'twitter': 1.2,
        'linkedin': 0.8,
        'reddit': 0.9,
    }
    
    multiplier = multipliers.get(platform, 1.0)
    
    # For high scores (fresh), multiplier boosts
    # For low scores (old), multiplier reduces penalty less
    if base_score >= 15:
        return int(base_score * multiplier)
    else:
        return int(base_score / multiplier)
```

### Conversation Activity

When was the last activity in the conversation?

| Last Activity | Points | Rationale |
|---------------|--------|-----------|
| < 15 min | 10 | Active now |
| 15 - 60 min | 8 | Recently active |
| 1 - 6 hr | 5 | Activity today |
| 6 - 24 hr | 2 | Slowing down |
| 24+ hr | 0 | Conversation may be over |

**Maximum contribution:** 10 points

```python
def score_conversation_activity(post: NormalizedPost) -> int:
    """Score based on conversation recency."""
    
    # If we have last reply time
    last_activity = post.platform_data.get('last_reply_at')
    
    if not last_activity:
        # Use post creation as proxy
        last_activity = post.created_at
    
    if isinstance(last_activity, str):
        last_activity = datetime.fromisoformat(last_activity.replace('Z', '+00:00'))
    
    now = datetime.now(timezone.utc)
    hours_since = (now - last_activity).total_seconds() / 3600
    
    if hours_since < 0.25:
        return 10
    elif hours_since < 1:
        return 8
    elif hours_since < 6:
        return 5
    elif hours_since < 24:
        return 2
    else:
        return 0
```

### Trending/Urgency

Is this post or topic trending?

| Signal | Points |
|--------|--------|
| Post is trending | +15 |
| Topic is trending | +10 |
| Breaking news relevance | +10 |
| Time-sensitive content | +5 |

**Maximum contribution:** 20 points (highest applicable)

```python
def score_urgency(post: NormalizedPost) -> int:
    """Score urgency/trending signals."""
    
    score = 0
    
    # Check if post is trending
    if post.platform_data.get('is_trending'):
        score = max(score, 15)
    
    # Check velocity indicators (proxy for trending)
    if post.engagement.likes and post.engagement.views:
        hours_old = (datetime.now(timezone.utc) - post.created_at).total_seconds() / 3600
        if hours_old > 0:
            velocity = post.engagement.likes / hours_old
            if velocity > 100:
                score = max(score, 15)
            elif velocity > 50:
                score = max(score, 10)
    
    # Check for time-sensitive language
    time_sensitive_patterns = [
        'just announced', 'breaking', 'just released',
        'happening now', 'live', 'today'
    ]
    content_lower = post.content_text.lower()
    if any(pattern in content_lower for pattern in time_sensitive_patterns):
        score = max(score, 10)
    
    return min(score, 20)
```

### Complete Timing Scoring

```python
@dataclass
class TimingScoreResult:
    total: int
    freshness_contribution: int
    activity_contribution: int
    urgency_contribution: int
    hours_old: float


def score_timing(post: NormalizedPost) -> TimingScoreResult:
    """Calculate timing opportunity score."""
    
    hours_old = (datetime.now(timezone.utc) - post.created_at).total_seconds() / 3600
    
    freshness_score = score_freshness(post.created_at)
    freshness_score = adjust_freshness_for_platform(freshness_score, post.platform)
    
    activity_score = score_conversation_activity(post)
    urgency_score = score_urgency(post)
    
    total = freshness_score + activity_score + urgency_score
    
    return TimingScoreResult(
        total=total,
        freshness_contribution=freshness_score,
        activity_contribution=activity_score,
        urgency_contribution=urgency_score,
        hours_old=hours_old,
    )
```

## 7.5.6 Conversation Signal Definitions

### Question Detection

Questions represent clear engagement opportunities.

| Signal | Points | Detection |
|--------|--------|-----------|
| Direct question | 15 | Ends with ?, contains "how", "what", "why" |
| Implicit question | 10 | "wondering", "curious", "looking for" |
| Help-seeking | 15 | "need help", "anyone know" |
| Recommendation request | 18 | "recommendations", "suggestions", "what should I" |
| Not a question | 0 | No question indicators |

**Maximum contribution:** 18 points

```python
def score_question(post: NormalizedPost) -> int:
    """Score based on question indicators."""
    
    content = post.content_text.lower()
    
    # Recommendation requests (highest value)
    rec_patterns = ['any recommendations', 'suggestions for', 'what should i use',
                    'looking for recommendations', 'anyone recommend']
    if any(pattern in content for pattern in rec_patterns):
        return 18
    
    # Help-seeking
    help_patterns = ['need help', 'anyone know', 'can someone help',
                     'struggling with', 'how do i']
    if any(pattern in content for pattern in help_patterns):
        return 15
    
    # Direct question
    if '?' in content:
        question_words = ['how', 'what', 'why', 'when', 'where', 'which', 'who']
        if any(word in content for word in question_words):
            return 15
        return 10  # Question mark but less clear
    
    # Implicit question
    implicit_patterns = ['wondering', 'curious about', 'thinking about',
                         'considering', 'looking for']
    if any(pattern in content for pattern in implicit_patterns):
        return 10
    
    return 0
```

### Unanswered Status

Unanswered questions are prime opportunities.

| Status | Points |
|--------|--------|
| 0 replies (unanswered) | 15 |
| 1-2 replies (lightly answered) | 10 |
| 3-5 replies (answered) | 5 |
| 6+ replies | 0 |

**Combined with question score:**
If post is a question AND unanswered, this is high opportunity.

```python
def score_unanswered(post: NormalizedPost, is_question: bool) -> int:
    """Score based on answer status."""
    
    if not is_question:
        return 0  # Only applies to questions
    
    replies = post.engagement.replies
    
    if replies == 0:
        return 15
    elif replies <= 2:
        return 10
    elif replies <= 5:
        return 5
    else:
        return 0
```

### Response Gap Opportunity

Is there a gap in existing responses we can fill?

| Gap Type | Points |
|----------|--------|
| Expertise gap (no technical answer) | 10 |
| Product gap (no tool recommended) | 12 |
| Perspective gap (missing viewpoint) | 8 |
| Correction opportunity (wrong info) | 10 |

**Detection:** Requires analysis of existing replies (complex, may use LLM)

For simpler implementation, estimate based on:
- Low reply count suggests gap
- Question type suggests what's needed

```python
def score_response_gap(post: NormalizedPost) -> int:
    """Estimate response gap opportunity."""
    
    # Simple heuristic based on reply count and question type
    content = post.content_text.lower()
    replies = post.engagement.replies
    
    # If asking for tool/product recommendation with few replies
    if any(kw in content for kw in ['recommend', 'tool', 'product', 'solution']):
        if replies <= 3:
            return 12
        elif replies <= 6:
            return 6
    
    # If technical question with few replies
    tech_indicators = ['how to', 'implement', 'configure', 'debug', 'error']
    if any(ind in content for ind in tech_indicators):
        if replies <= 3:
            return 10
        elif replies <= 6:
            return 5
    
    # General gap estimation
    if replies == 0:
        return 8
    elif replies <= 2:
        return 5
    elif replies <= 5:
        return 2
    
    return 0
```

### Conversation Depth

How deep is the conversation?

| Depth | Points | Interpretation |
|-------|--------|----------------|
| Root post | 5 | Maximum visibility |
| First-level reply | 3 | Good visibility |
| Second-level reply | 1 | Reduced visibility |
| Deeper | 0 | Low visibility |

```python
def score_conversation_depth(post: NormalizedPost) -> int:
    """Score based on conversation position."""
    
    # Check if this is a reply
    if post.platform_data.get('is_reply'):
        depth = post.platform_data.get('reply_depth', 1)
        
        if depth == 1:
            return 3
        elif depth == 2:
            return 1
        else:
            return 0
    
    return 5  # Root post
```

### Complete Conversation Scoring

```python
@dataclass
class ConversationScoreResult:
    total: int
    question_contribution: int
    unanswered_contribution: int
    gap_contribution: int
    depth_contribution: int
    is_question: bool


def score_conversation(post: NormalizedPost) -> ConversationScoreResult:
    """Calculate conversation opportunity score."""
    
    question_score = score_question(post)
    is_question = question_score > 0
    
    unanswered_score = score_unanswered(post, is_question)
    gap_score = score_response_gap(post)
    depth_score = score_conversation_depth(post)
    
    total = question_score + unanswered_score + gap_score + depth_score
    
    return ConversationScoreResult(
        total=total,
        question_contribution=question_score,
        unanswered_contribution=unanswered_score,
        gap_contribution=gap_score,
        depth_contribution=depth_score,
        is_question=is_question,
    )
```

## 7.5.7 Strategic Signal Definitions

### Goal Alignment Contribution

From classification × campaign goal (already calculated in classification).

| Multiplier Range | Points |
|------------------|--------|
| 1.4+ | 15 |
| 1.2-1.39 | 10 |
| 1.0-1.19 | 5 |
| 0.8-0.99 | 0 |
| < 0.8 | -5 |

```python
def score_goal_alignment(classification: dict, campaign_goal: str) -> int:
    """Score based on goal alignment from classification."""
    
    multipliers = classification.get('goal_multipliers', {})
    multiplier = multipliers.get(campaign_goal, 1.0)
    
    if multiplier >= 1.4:
        return 15
    elif multiplier >= 1.2:
        return 10
    elif multiplier >= 1.0:
        return 5
    elif multiplier >= 0.8:
        return 0
    else:
        return -5
```

### Competitive Opportunity

Is this a competitive situation?

| Signal | Points |
|--------|--------|
| User comparing competitors | 10 |
| User asking about competitor | 8 |
| Competitor mentioned negatively | 12 |
| User switching from competitor | 15 |
| Competitor issue/complaint | 10 |

```python
def score_competitive_opportunity(post: NormalizedPost, classification: dict) -> int:
    """Score competitive opportunity."""
    
    content = post.content_text.lower()
    
    # Check classification
    if classification.get('primary') == 'competitor_mention':
        score = 8  # Base score for competitor mention
        
        # Negative sentiment about competitor
        negative_patterns = ['problem with', 'issue', 'frustrated', 'hate',
                            'switching from', 'leaving', 'looking for alternative']
        if any(pattern in content for pattern in negative_patterns):
            score += 7  # Boost for negative competitor sentiment
        
        # Comparison context
        comparison_patterns = ['vs', 'versus', 'compared to', 'better than',
                              'alternative to', 'instead of']
        if any(pattern in content for pattern in comparison_patterns):
            score += 5
        
        return min(score, 15)
    
    return 0
```

### Strategic Importance

Is this a strategically important opportunity?

| Signal | Points |
|--------|--------|
| Potential enterprise customer | 10 |
| Potential partnership | 8 |
| Media/press | 10 |
| Conference/event context | 5 |
| Community leader | 8 |

```python
def score_strategic_importance(post: NormalizedPost) -> int:
    """Score strategic importance of opportunity."""
    
    author = post.author
    content = post.content_text.lower()
    bio = (author.bio or '').lower()
    
    score = 0
    
    # Enterprise indicators
    enterprise_patterns = ['enterprise', 'fortune 500', 'series b', 'series c']
    if any(pattern in bio for pattern in enterprise_patterns):
        score += 10
    
    # Media/press
    media_patterns = ['journalist', 'reporter', 'editor', 'writer at', 
                      'techcrunch', 'wired', 'verge']
    if any(pattern in bio for pattern in media_patterns):
        score += 10
    
    # Partnership potential
    partnership_patterns = ['partnerships', 'bd', 'business development',
                           'integrations', 'platform']
    if any(pattern in bio for pattern in partnership_patterns):
        score += 8
    
    # Community leader
    leader_patterns = ['moderator', 'organizer', 'community', 'maintainer']
    if any(pattern in bio for pattern in leader_patterns):
        score += 8
    
    # Event context
    event_patterns = ['#neurips', '#icml', '#ai summit', 'conference']
    if any(pattern in content for pattern in event_patterns):
        score += 5
    
    return min(score, 15)
```

### Complete Strategic Scoring

```python
@dataclass
class StrategicScoreResult:
    total: int
    goal_alignment_contribution: int
    competitive_contribution: int
    importance_contribution: int


def score_strategic(
    post: NormalizedPost,
    classification: dict,
    campaign_goal: str
) -> StrategicScoreResult:
    """Calculate strategic opportunity score."""
    
    goal_score = score_goal_alignment(classification, campaign_goal)
    competitive_score = score_competitive_opportunity(post, classification)
    importance_score = score_strategic_importance(post)
    
    total = goal_score + competitive_score + importance_score
    
    return StrategicScoreResult(
        total=total,
        goal_alignment_contribution=goal_score,
        competitive_contribution=competitive_score,
        importance_contribution=importance_score,
    )
```

## 7.5.8 Opportunity Score Calculation

### Score Formula

Total opportunity score combines all signal categories:

```
opportunity_score = engagement_score + author_score + timing_score + 
                    conversation_score + strategic_score
```

**Maximum theoretical scores:**
- Engagement: ~99 (27 + 12 + 15 + 15 + 10 + 20)
- Author: ~79 (22 + 8 + 12 + 10 + 15 + 12)
- Timing: ~55 (25 + 10 + 20)
- Conversation: ~55 (18 + 15 + 12 + 10)
- Strategic: ~45 (15 + 15 + 15)
- **Total possible:** ~333

### Normalization

Normalize to 0-100 scale:

```python
def normalize_opportunity_score(raw_score: float) -> int:
    """Normalize raw opportunity score to 0-100."""
    
    # Expected typical range: 0-150
    # Excellent opportunities: 80-120 raw
    # Poor opportunities: 0-40 raw
    
    if raw_score <= 0:
        return 0
    elif raw_score <= 100:
        return int(raw_score)
    elif raw_score <= 150:
        # Gradual compression 100-150 -> 100-115
        excess = raw_score - 100
        return int(100 + excess * 0.3)
    else:
        # Heavy compression above 150
        return min(100, int(115 + (raw_score - 150) * 0.1))
```

### Complete Opportunity Scoring

```python
@dataclass
class OpportunityScoreResult:
    total: int                           # Normalized 0-100
    raw_total: float                     # Pre-normalization
    
    engagement_score: EngagementScoreResult
    author_score: AuthorScoreResult
    timing_score: TimingScoreResult
    conversation_score: ConversationScoreResult
    strategic_score: StrategicScoreResult
    
    top_signals: List[SignalContribution]
    scored_at: datetime


def calculate_opportunity_score(
    post: NormalizedPost,
    classification: dict,
    campaign_goal: str
) -> OpportunityScoreResult:
    """Calculate complete opportunity score for a post."""
    
    # Score each category
    engagement_result = score_engagement(post)
    author_result = score_author_opportunity(post)
    timing_result = score_timing(post)
    conversation_result = score_conversation(post)
    strategic_result = score_strategic(post, classification, campaign_goal)
    
    # Sum raw scores
    raw_total = (
        engagement_result.total +
        author_result.total +
        timing_result.total +
        conversation_result.total +
        strategic_result.total
    )
    
    # Normalize
    normalized_total = normalize_opportunity_score(raw_total)
    
    # Collect top signals
    signals = [
        SignalContribution('engagement', engagement_result.total),
        SignalContribution('author', author_result.total),
        SignalContribution('timing', timing_result.total),
        SignalContribution('conversation', conversation_result.total),
        SignalContribution('strategic', strategic_result.total),
    ]
    signals.sort(key=lambda s: s.contribution, reverse=True)
    
    return OpportunityScoreResult(
        total=normalized_total,
        raw_total=raw_total,
        engagement_score=engagement_result,
        author_score=author_result,
        timing_score=timing_result,
        conversation_score=conversation_result,
        strategic_score=strategic_result,
        top_signals=signals,
        scored_at=datetime.now(timezone.utc),
    )
```

## 7.5.9 Opportunity Tiers and Thresholds

### Opportunity Tiers

| Tier | Score Range | Interpretation | Action |
|------|-------------|----------------|--------|
| Exceptional | 85-100 | Outstanding opportunity | Prioritize immediately |
| High | 70-84 | Strong opportunity | Engage if capacity |
| Good | 55-69 | Solid opportunity | Standard processing |
| Moderate | 40-54 | Decent opportunity | Lower priority |
| Low | 25-39 | Marginal opportunity | Only if nothing better |
| Poor | 0-24 | Not worth it | Skip |

### Combined Relevance + Opportunity

For final prioritization, combine both scores:

| Relevance | Opportunity | Combined Assessment |
|-----------|-------------|---------------------|
| High (70+) | High (70+) | Excellent - top priority |
| High (70+) | Moderate (50-69) | Good - engage |
| High (70+) | Low (<50) | Maybe - relevant but poor timing |
| Moderate (50-69) | High (70+) | Good - opportunity outweighs |
| Moderate (50-69) | Moderate (50-69) | Average - standard queue |
| Moderate (50-69) | Low (<50) | Skip - not worth it |
| Low (<50) | Any | Filter - not relevant enough |

## 7.5.10 Score Storage

### Storage Structure

Opportunity scores stored in `scores` JSONB column:

```json
{
  "relevance": { ... },
  "opportunity": {
    "total": 78,
    "raw_total": 112,
    "engagement": {
      "total": 42,
      "likes": 15,
      "replies": 10,
      "shares": 6,
      "views": 6,
      "rate": 3,
      "velocity": 10,
      "raw_metrics": {
        "likes": 156,
        "replies": 8,
        "shares": 23,
        "views": 4500
      }
    },
    "author": {
      "total": 28,
      "followers": 16,
      "verified": 0,
      "engagement_rate": 5,
      "domain_relevance": 6,
      "customer_potential": 8,
      "relationship": 0
    },
    "timing": {
      "total": 25,
      "freshness": 18,
      "activity": 5,
      "urgency": 0,
      "hours_old": 3.5
    },
    "conversation": {
      "total": 28,
      "question": 15,
      "unanswered": 10,
      "gap": 2,
      "depth": 5,
      "is_question": true
    },
    "strategic": {
      "total": 15,
      "goal_alignment": 10,
      "competitive": 0,
      "importance": 5
    },
    "scored_at": "2024-01-15T14:40:00Z"
  }
}
```

### Store Implementation

```python
def store_opportunity_score(post_id: UUID, result: OpportunityScoreResult):
    """Store opportunity score in database."""
    
    score_data = {
        'opportunity': {
            'total': result.total,
            'raw_total': result.raw_total,
            'engagement': asdict(result.engagement_score),
            'author': asdict(result.author_score),
            'timing': asdict(result.timing_score),
            'conversation': asdict(result.conversation_score),
            'strategic': asdict(result.strategic_score),
            'scored_at': result.scored_at.isoformat(),
        }
    }
    
    db.execute("""
        UPDATE discovered_posts
        SET 
            scores = COALESCE(scores, '{}'::jsonb) || %(score_data)s::jsonb,
            status = 'opportunity_scored',
            updated_at = NOW()
        WHERE id = %(post_id)s
    """, {
        'post_id': post_id,
        'score_data': json.dumps(score_data),
    })
```

## 7.5.11 Opportunity Scoring Pipeline

### Pipeline Position

```
Classification → Relevance Scoring → Opportunity Scoring → Combined Scoring → Filtering
```

### Batch Processing

```python
async def score_opportunity_batch(
    post_ids: List[UUID],
    campaign_goal: str
) -> List[OpportunityScoreResult]:
    """Score opportunity for a batch of posts."""
    
    results = []
    
    for post_id in post_ids:
        post = get_post(post_id)
        classification = post.classification
        
        if not classification:
            log.warning(f"Post {post_id} not classified, skipping")
            continue
        
        result = calculate_opportunity_score(post, classification, campaign_goal)
        store_opportunity_score(post_id, result)
        
        results.append(result)
    
    return results
```

### Worker Implementation

```python
async def opportunity_scoring_worker(campaign_id: UUID):
    """Worker that scores opportunity for posts."""
    
    campaign = get_campaign(campaign_id)
    campaign_goal = campaign.primary_goal
    
    while True:
        # Get batch of relevance-scored posts
        posts = db.query("""
            SELECT id FROM discovered_posts
            WHERE status = 'relevance_scored'
            AND campaign_id = %(campaign_id)s
            ORDER BY (scores->'relevance'->>'total')::int DESC
            LIMIT 100
            FOR UPDATE SKIP LOCKED
        """, {'campaign_id': campaign_id})
        
        if not posts:
            await asyncio.sleep(5)
            continue
        
        post_ids = [p.id for p in posts]
        
        try:
            results = await score_opportunity_batch(post_ids, campaign_goal)
            log.info(f"Scored opportunity for {len(results)} posts")
            
            for result in results:
                opportunity_score_histogram.observe(result.total)
        
        except Exception as e:
            log.error(f"Error scoring opportunity batch: {e}")
            mark_posts_for_retry(post_ids, 'opportunity_scoring')
```

## 7.5.12 Monitoring and Metrics

### Opportunity Metrics

```python
# Score distribution
opportunity_score_histogram = Histogram(
    'opportunity_score',
    'Distribution of opportunity scores',
    buckets=[10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
)

# Scores by category
opportunity_category_histogram = Histogram(
    'opportunity_category_score',
    'Score by opportunity category',
    ['category'],  # engagement, author, timing, conversation, strategic
    buckets=[0, 10, 20, 30, 40, 50]
)

# High-opportunity rate
high_opportunity_rate = Gauge(
    'opportunity_high_rate',
    'Percentage of posts with opportunity >= 70'
)

# Timing metrics
opportunity_freshness_histogram = Histogram(
    'opportunity_post_age_hours',
    'Age of posts at scoring time',
    buckets=[0.5, 1, 2, 4, 8, 12, 24, 48]
)
```

### Dashboard Components

1. **Score Distribution:** Histogram over time
2. **Category Breakdown:** Average contribution per category
3. **High-Opportunity Rate:** Percentage in top tier
4. **Timing Analysis:** Average post age at engagement
5. **Question Rate:** Percentage of posts that are questions
6. **Author Quality:** Distribution of author scores

## 7.5.13 Implementation Guidance for Neoclaw

### Implementation Order

1. **Define scoring functions for each signal**
   - Engagement signals
   - Author signals
   - Timing signals
   - Conversation signals
   - Strategic signals

2. **Build category scorers**
   - Combine signals into category scores
   - Return structured results

3. **Build complete opportunity scorer**
   - Combine all categories
   - Normalize final score
   - Generate top signals

4. **Add storage**
   - Store in posts table
   - Index for queries

5. **Build pipeline integration**
   - Worker for batch processing
   - Error handling

6. **Add monitoring**
   - Metrics collection
   - Dashboard

### Testing Checklist

#### Unit Tests
- [ ] Each signal scorer with known inputs
- [ ] Category aggregation
- [ ] Normalization function
- [ ] Platform adjustments

#### Integration Tests
- [ ] Full scoring pipeline
- [ ] Batch processing
- [ ] Storage and retrieval

#### Validation Tests
- [ ] Sample high-opportunity posts score high
- [ ] Sample low-opportunity posts score low
- [ ] Score distribution matches expectations

### Common Pitfalls

**Stale engagement data:**
Engagement metrics change rapidly. Fetch fresh data if possible.

**Missing metrics:**
Not all platforms provide all metrics (views, etc.). Handle gracefully.

**Author cache:**
Author data is expensive to fetch. Cache aggressively.

**Timing edge cases:**
Posts exactly at boundaries (30 min, 24 hr) — be consistent.

**Over-weighting virality:**
Viral posts may not be best opportunities. Balance with relevance.

---

**END OF SECTION 7.5**

Section 7.6 continues with Author & Account Evaluation specification.
-e 


# SECTION 7.6: AUTHOR & ACCOUNT EVALUATION

## 7.6.1 What Author Evaluation Is

### The Core Concept

Author & Account Evaluation is the process of assessing the quality, influence, relevance, and relationship status of social media accounts whose content Jen discovers. While Sections 7.4 and 7.5 touched on author signals within scoring, this section provides the comprehensive framework for author assessment.

**Input:** Author data from discovered posts
**Output:** Author profiles with quality scores, relationship status, and engagement recommendations

Author evaluation answers multiple questions:
- Is this a real, legitimate account or a bot/spam?
- How influential is this author?
- Is this author in our target audience?
- Have we engaged with them before?
- Should we prioritize engagement with them?
- Are there any risks in engaging?

### Why Author Evaluation Matters

**Quality filtering:**
Filter out bots, spam accounts, and low-quality sources. Engaging with these wastes resources and can damage brand perception.

**Opportunity prioritization:**
High-value authors (influencers, potential customers, industry leaders) deserve priority engagement.

**Relationship management:**
Track engagement history to build relationships over time, avoid over-engaging, and personalize interactions.

**Risk mitigation:**
Identify problematic accounts (trolls, controversial figures, competitors) to avoid engagement risks.

**Strategic targeting:**
Focus on authors who align with campaign goals — potential customers for conversions, influencers for awareness.

### Author Evaluation Dimensions

**Account quality:** Is this a legitimate, active, real account?
- Account age
- Activity patterns
- Profile completeness
- Follower/following ratio

**Influence:** How much reach and impact does this author have?
- Follower count
- Engagement rates
- Verified status
- Industry recognition

**Relevance:** Is this author in our target audience?
- Domain alignment (AI, security, tech)
- Role indicators (developer, executive, researcher)
- Company context

**Relationship:** What's our history with this author?
- Previous engagements
- Engagement outcomes
- Relationship sentiment

**Risk:** Are there concerns about engaging?
- Controversial content history
- Negative sentiment
- Competitive affiliations

## 7.6.2 Account Quality Assessment

### Quality Signals

#### Account Age

Older accounts are generally more trustworthy.

| Account Age | Points | Interpretation |
|-------------|--------|----------------|
| < 30 days | -10 | Very new, suspicious |
| 30-90 days | -5 | New, caution |
| 90 days - 1 year | 0 | Established |
| 1-3 years | 5 | Mature |
| 3-5 years | 8 | Well-established |
| 5+ years | 10 | Very established |

```python
def score_account_age(created_at: datetime) -> int:
    """Score based on account age."""
    
    if not created_at:
        return 0  # Unknown
    
    now = datetime.now(timezone.utc)
    age_days = (now - created_at).days
    
    if age_days < 30:
        return -10
    elif age_days < 90:
        return -5
    elif age_days < 365:
        return 0
    elif age_days < 1095:  # 3 years
        return 5
    elif age_days < 1825:  # 5 years
        return 8
    else:
        return 10
```

#### Profile Completeness

Complete profiles indicate real users.

| Element | Points |
|---------|--------|
| Has display name | +2 |
| Has bio | +3 |
| Has avatar (not default) | +2 |
| Has location | +1 |
| Has website/link | +2 |
| Has banner image | +1 |

**Maximum:** 11 points

```python
def score_profile_completeness(author: NormalizedAuthor) -> int:
    """Score based on profile completeness."""
    
    score = 0
    
    if author.display_name and author.display_name != author.handle:
        score += 2
    
    if author.bio and len(author.bio) > 10:
        score += 3
    
    if author.avatar_url and 'default' not in author.avatar_url.lower():
        score += 2
    
    # Platform-specific fields would come from platform_data
    # These are approximations
    
    return score
```

#### Follower/Following Ratio

Unusual ratios indicate spam or bot patterns.

| Ratio (Followers:Following) | Points | Interpretation |
|-----------------------------|--------|----------------|
| < 0.1 | -8 | Follows many, few follow back (spam pattern) |
| 0.1 - 0.5 | -3 | Low ratio |
| 0.5 - 1.0 | 0 | Balanced |
| 1.0 - 5.0 | 5 | Good ratio |
| 5.0 - 50.0 | 8 | Influential |
| > 50.0 | 10 | Very influential |
| Following = 0 | -5 | Suspicious (or brand account) |

```python
def score_follower_ratio(followers: int, following: int) -> int:
    """Score based on follower/following ratio."""
    
    if following == 0:
        if followers > 10000:
            return 5  # Probably a brand/celebrity
        return -5  # Suspicious
    
    ratio = followers / following
    
    if ratio < 0.1:
        return -8
    elif ratio < 0.5:
        return -3
    elif ratio < 1.0:
        return 0
    elif ratio < 5.0:
        return 5
    elif ratio < 50.0:
        return 8
    else:
        return 10
```

#### Activity Level

Active accounts are more valuable to engage with.

| Activity | Points | Detection |
|----------|--------|-----------|
| Very active (daily posts) | 8 | Posts in last 24 hours |
| Active (weekly posts) | 5 | Posts in last 7 days |
| Moderate (monthly posts) | 2 | Posts in last 30 days |
| Inactive | -5 | No posts in 30+ days |
| Dormant | -10 | No posts in 90+ days |

```python
def score_activity_level(last_post_at: datetime, posts_count: int) -> int:
    """Score based on activity level."""
    
    if not last_post_at:
        return 0  # Unknown
    
    now = datetime.now(timezone.utc)
    days_since_post = (now - last_post_at).days
    
    if days_since_post <= 1:
        return 8
    elif days_since_post <= 7:
        return 5
    elif days_since_post <= 30:
        return 2
    elif days_since_post <= 90:
        return -5
    else:
        return -10
```

#### Bot Detection Signals

Identify likely bot accounts.

| Signal | Points | Detection |
|--------|--------|-----------|
| Username is random characters | -15 | Regex pattern |
| Bio contains spam keywords | -10 | Keyword match |
| Posts are all retweets/reposts | -8 | Content analysis |
| Posts at inhuman frequency | -10 | Posting pattern |
| Identical post content repeated | -15 | Content duplication |
| Default avatar + new account | -10 | Combined signals |

```python
def detect_bot_signals(author: NormalizedAuthor, recent_posts: List = None) -> int:
    """Detect bot patterns and return penalty score."""
    
    penalty = 0
    
    # Random username pattern
    handle = author.handle or ''
    if re.match(r'^[a-z]{2,4}\d{6,}$', handle.lower()):
        penalty -= 15
    elif re.match(r'^[a-z]+_[a-z]+_\d+$', handle.lower()):
        penalty -= 10
    
    # Spam bio keywords
    spam_keywords = ['follow back', 'dm for', 'click link', 'giveaway',
                     'crypto expert', 'forex', 'binary options']
    if author.bio:
        bio_lower = author.bio.lower()
        if any(kw in bio_lower for kw in spam_keywords):
            penalty -= 10
    
    # Would need recent_posts for more sophisticated detection
    # This would be done during ingestion or async
    
    return penalty
```

### Complete Quality Score

```python
@dataclass
class AccountQualityResult:
    total: int
    tier: str  # excellent, good, average, poor, suspicious
    
    age_contribution: int
    completeness_contribution: int
    ratio_contribution: int
    activity_contribution: int
    bot_penalty: int
    
    flags: List[str]


def calculate_account_quality(author: NormalizedAuthor) -> AccountQualityResult:
    """Calculate overall account quality score."""
    
    age_score = score_account_age(author.account_created_at)
    completeness_score = score_profile_completeness(author)
    ratio_score = score_follower_ratio(
        author.followers_count or 0,
        author.following_count or 0
    )
    activity_score = score_activity_level(
        author.last_post_at,
        author.posts_count or 0
    )
    bot_penalty = detect_bot_signals(author)
    
    total = age_score + completeness_score + ratio_score + activity_score + bot_penalty
    
    # Determine tier
    if total >= 25:
        tier = 'excellent'
    elif total >= 15:
        tier = 'good'
    elif total >= 5:
        tier = 'average'
    elif total >= -5:
        tier = 'poor'
    else:
        tier = 'suspicious'
    
    # Collect flags
    flags = []
    if age_score < 0:
        flags.append('new_account')
    if bot_penalty < -10:
        flags.append('possible_bot')
    if activity_score < 0:
        flags.append('inactive')
    if ratio_score < -5:
        flags.append('suspicious_ratio')
    
    return AccountQualityResult(
        total=total,
        tier=tier,
        age_contribution=age_score,
        completeness_contribution=completeness_score,
        ratio_contribution=ratio_score,
        activity_contribution=activity_score,
        bot_penalty=bot_penalty,
        flags=flags,
    )
```

## 7.6.3 Influence Assessment

### Influence Signals

#### Follower Count Tiers

| Tier | Followers | Influence Score | Label |
|------|-----------|-----------------|-------|
| Nano | 0-1K | 5 | Nano influencer |
| Micro | 1K-10K | 15 | Micro influencer |
| Mid | 10K-50K | 25 | Mid-tier influencer |
| Macro | 50K-500K | 35 | Macro influencer |
| Mega | 500K-1M | 42 | Mega influencer |
| Celebrity | 1M+ | 50 | Celebrity |

```python
def score_influence_by_followers(followers: int) -> Tuple[int, str]:
    """Score influence based on follower count."""
    
    if followers is None:
        return 10, 'unknown'
    
    if followers < 1000:
        return 5, 'nano'
    elif followers < 10000:
        return 15, 'micro'
    elif followers < 50000:
        return 25, 'mid'
    elif followers < 500000:
        return 35, 'macro'
    elif followers < 1000000:
        return 42, 'mega'
    else:
        return 50, 'celebrity'
```

#### Engagement Rate

High engagement rates indicate actual influence (not just follower count).

| Engagement Rate | Points | Interpretation |
|-----------------|--------|----------------|
| < 0.5% | -5 | Low engagement (fake followers?) |
| 0.5-1% | 0 | Below average |
| 1-3% | 5 | Average |
| 3-6% | 10 | Good |
| 6-10% | 15 | Excellent |
| > 10% | 18 | Exceptional (or small audience) |

```python
def score_engagement_rate(avg_engagement: float, followers: int) -> int:
    """Score author's typical engagement rate."""
    
    if not followers or followers == 0:
        return 0
    
    rate = (avg_engagement / followers) * 100
    
    if rate < 0.5:
        return -5
    elif rate < 1:
        return 0
    elif rate < 3:
        return 5
    elif rate < 6:
        return 10
    elif rate < 10:
        return 15
    else:
        return 18
```

#### Verified Status

Verification indicates recognized authority.

| Status | Points |
|--------|--------|
| Verified (blue check) | 15 |
| Organization verified | 12 |
| Not verified | 0 |

#### Industry Recognition

Indicators of industry standing.

| Signal | Points |
|--------|--------|
| Known industry figure | 20 |
| Conference speaker | 10 |
| Published author | 10 |
| Podcast host | 8 |
| Notable company employee | 8 |
| Open source maintainer | 8 |

```python
def score_industry_recognition(author: NormalizedAuthor) -> int:
    """Score industry recognition signals."""
    
    if not author.bio:
        return 0
    
    bio_lower = author.bio.lower()
    score = 0
    
    # Speaker indicators
    speaker_patterns = ['speaker', 'keynote', 'conference', 'talks at']
    if any(p in bio_lower for p in speaker_patterns):
        score += 10
    
    # Author indicators
    author_patterns = ['author of', 'wrote', 'published', 'book']
    if any(p in bio_lower for p in author_patterns):
        score += 10
    
    # Podcast indicators
    podcast_patterns = ['podcast', 'host of', 'co-host']
    if any(p in bio_lower for p in podcast_patterns):
        score += 8
    
    # Notable company
    notable_companies = ['google', 'meta', 'microsoft', 'apple', 'amazon',
                        'openai', 'anthropic', 'nvidia', 'tesla']
    if any(c in bio_lower for c in notable_companies):
        score += 8
    
    # Open source
    oss_patterns = ['maintainer', 'creator of', 'open source', 'contributor']
    if any(p in bio_lower for p in oss_patterns):
        score += 8
    
    return min(score, 30)  # Cap at 30
```

### Complete Influence Score

```python
@dataclass
class InfluenceScoreResult:
    total: int
    tier: str  # celebrity, macro, mid, micro, nano
    normalized: int  # 0-100 scale
    
    followers_contribution: int
    engagement_contribution: int
    verified_contribution: int
    recognition_contribution: int
    
    follower_count: int
    follower_tier: str


def calculate_influence_score(author: NormalizedAuthor) -> InfluenceScoreResult:
    """Calculate author influence score."""
    
    followers_score, follower_tier = score_influence_by_followers(
        author.followers_count
    )
    
    # Would need historical engagement data for engagement rate
    # Using estimated average engagement for now
    engagement_score = score_engagement_rate(
        author.avg_engagement or 0,
        author.followers_count or 0
    )
    
    verified_score = 15 if author.verified else 0
    recognition_score = score_industry_recognition(author)
    
    total = followers_score + engagement_score + verified_score + recognition_score
    
    # Normalize to 0-100
    # Max theoretical: 50 + 18 + 15 + 30 = 113
    normalized = min(100, int(total * 100 / 113))
    
    # Determine tier based on followers
    if follower_tier in ['celebrity', 'mega']:
        tier = 'celebrity'
    elif follower_tier == 'macro':
        tier = 'macro'
    elif follower_tier == 'mid':
        tier = 'mid'
    elif follower_tier == 'micro':
        tier = 'micro'
    else:
        tier = 'nano'
    
    return InfluenceScoreResult(
        total=total,
        tier=tier,
        normalized=normalized,
        followers_contribution=followers_score,
        engagement_contribution=engagement_score,
        verified_contribution=verified_score,
        recognition_contribution=recognition_score,
        follower_count=author.followers_count or 0,
        follower_tier=follower_tier,
    )
```

## 7.6.4 Relevance Assessment

### Domain Relevance Signals

#### Bio Keyword Analysis

Detailed scoring based on bio content.

**Core domain keywords (highest relevance):**

| Keyword/Pattern | Points |
|-----------------|--------|
| "AI agent" or "agentic" | 20 |
| "agent security" | 25 |
| "AI safety" | 20 |
| "LLM" or "large language model" | 15 |
| "machine learning engineer" | 15 |
| "AI researcher" | 18 |
| "security engineer" + AI context | 18 |

**Adjacent domain keywords:**

| Keyword/Pattern | Points |
|-----------------|--------|
| "AI" or "artificial intelligence" | 10 |
| "ML" or "machine learning" | 10 |
| "developer" or "engineer" | 8 |
| "security" | 8 |
| "startup" | 5 |
| "tech" | 5 |
| "data scientist" | 8 |
| "software" | 5 |

```python
def score_bio_domain_relevance(bio: str) -> Tuple[int, List[str]]:
    """Score domain relevance from bio keywords."""
    
    if not bio:
        return 0, []
    
    bio_lower = bio.lower()
    score = 0
    matched_keywords = []
    
    # Core domain (cumulative)
    core_keywords = {
        'ai agent': 20,
        'agentic': 20,
        'agent security': 25,
        'ai safety': 20,
        'llm': 15,
        'large language model': 15,
        'ml engineer': 15,
        'machine learning engineer': 15,
        'ai researcher': 18,
    }
    
    for keyword, points in core_keywords.items():
        if keyword in bio_lower:
            score += points
            matched_keywords.append(keyword)
    
    # Adjacent domain (cumulative but capped)
    adjacent_keywords = {
        'artificial intelligence': 10,
        'machine learning': 10,
        'developer': 8,
        'engineer': 8,
        'security': 8,
        'startup': 5,
        'tech': 5,
        'data scientist': 8,
        'software': 5,
    }
    
    adjacent_score = 0
    for keyword, points in adjacent_keywords.items():
        if keyword in bio_lower:
            adjacent_score += points
            matched_keywords.append(keyword)
    
    adjacent_score = min(adjacent_score, 25)  # Cap adjacent
    score += adjacent_score
    
    return score, matched_keywords
```

#### Role Analysis

Identify author's role/position.

| Role Category | Points | Detection |
|---------------|--------|-----------|
| Executive (CEO, CTO, VP) | 15 | Title patterns |
| Technical lead | 12 | Title patterns |
| Individual contributor | 8 | "engineer", "developer" |
| Researcher | 10 | "researcher", "phd" |
| Founder | 12 | "founder", "co-founder" |
| Investor | 8 | "investor", "vc", "partner at" |
| Media/Journalist | 10 | "journalist", "reporter", "editor" |
| Student/Learner | 3 | "student", "learning" |

```python
def analyze_author_role(bio: str) -> Tuple[str, int]:
    """Analyze author's role from bio."""
    
    if not bio:
        return 'unknown', 0
    
    bio_lower = bio.lower()
    
    # Executive patterns
    exec_patterns = ['ceo', 'cto', 'coo', 'cfo', 'chief', 'vp ', 'vice president',
                     'head of', 'director of', 'svp', 'evp']
    if any(p in bio_lower for p in exec_patterns):
        return 'executive', 15
    
    # Founder
    if 'founder' in bio_lower or 'co-founder' in bio_lower:
        return 'founder', 12
    
    # Technical lead
    lead_patterns = ['tech lead', 'team lead', 'principal', 'staff engineer',
                     'architect', 'distinguished']
    if any(p in bio_lower for p in lead_patterns):
        return 'tech_lead', 12
    
    # Researcher
    if any(p in bio_lower for p in ['researcher', 'phd', 'professor', 'scientist']):
        return 'researcher', 10
    
    # Media
    if any(p in bio_lower for p in ['journalist', 'reporter', 'editor', 'writer at']):
        return 'media', 10
    
    # Investor
    if any(p in bio_lower for p in ['investor', ' vc', 'venture', 'partner at']):
        return 'investor', 8
    
    # Individual contributor
    if any(p in bio_lower for p in ['engineer', 'developer', 'programmer']):
        return 'ic', 8
    
    # Student
    if any(p in bio_lower for p in ['student', 'learning', 'studying']):
        return 'student', 3
    
    return 'unknown', 0
```

#### Company Context

Analyze company affiliation.

| Company Type | Points |
|--------------|--------|
| Major tech company | 10 |
| AI company | 15 |
| Security company | 12 |
| Funded startup | 8 |
| Enterprise | 10 |
| Consulting | 5 |

```python
def analyze_company_context(bio: str) -> Tuple[str, int]:
    """Analyze company context from bio."""
    
    if not bio:
        return 'unknown', 0
    
    bio_lower = bio.lower()
    
    # AI companies (highest relevance)
    ai_companies = ['openai', 'anthropic', 'deepmind', 'google ai', 'meta ai',
                    'nvidia', 'hugging face', 'cohere', 'stability']
    if any(c in bio_lower for c in ai_companies):
        return 'ai_company', 15
    
    # Security companies
    security_companies = ['crowdstrike', 'palo alto', 'cloudflare', 'okta',
                         'snyk', 'wiz', 'security']
    if any(c in bio_lower for c in security_companies):
        return 'security_company', 12
    
    # Major tech
    major_tech = ['google', 'meta', 'microsoft', 'apple', 'amazon', 'netflix']
    if any(c in bio_lower for c in major_tech):
        return 'major_tech', 10
    
    # Enterprise indicators
    enterprise_patterns = ['fortune 500', 'enterprise', 'global']
    if any(p in bio_lower for p in enterprise_patterns):
        return 'enterprise', 10
    
    # Startup indicators
    startup_patterns = ['startup', 'yc', 'y combinator', 'series a', 'series b',
                       'backed by', 'building']
    if any(p in bio_lower for p in startup_patterns):
        return 'startup', 8
    
    return 'unknown', 0
```

### Complete Relevance Score

```python
@dataclass
class RelevanceScoreResult:
    total: int
    normalized: int  # 0-100
    
    domain_contribution: int
    domain_keywords: List[str]
    role: str
    role_contribution: int
    company_type: str
    company_contribution: int
    
    is_target_audience: bool


def calculate_relevance_score(author: NormalizedAuthor) -> RelevanceScoreResult:
    """Calculate author relevance score."""
    
    domain_score, domain_keywords = score_bio_domain_relevance(author.bio)
    role, role_score = analyze_author_role(author.bio)
    company_type, company_score = analyze_company_context(author.bio)
    
    total = domain_score + role_score + company_score
    
    # Normalize to 0-100
    # Max theoretical: ~75 domain + 15 role + 15 company = 105
    normalized = min(100, int(total * 100 / 105))
    
    # Determine if target audience
    is_target = (
        normalized >= 40 or
        domain_score >= 20 or
        (role in ['executive', 'founder', 'tech_lead'] and domain_score >= 10)
    )
    
    return RelevanceScoreResult(
        total=total,
        normalized=normalized,
        domain_contribution=domain_score,
        domain_keywords=domain_keywords,
        role=role,
        role_contribution=role_score,
        company_type=company_type,
        company_contribution=company_score,
        is_target_audience=is_target,
    )
```

## 7.6.5 Relationship Tracking

### Relationship Data Model

Track engagement history with each author.

```python
@dataclass
class AuthorRelationship:
    author_id: UUID
    
    # Discovery history
    first_seen_at: datetime
    last_seen_at: datetime
    posts_discovered: int
    
    # Engagement history
    engagement_count: int
    last_engaged_at: Optional[datetime]
    engagements: List[EngagementRecord]
    
    # Engagement outcomes
    positive_responses: int      # Author responded positively
    neutral_responses: int       # No response
    negative_responses: int      # Author responded negatively
    
    # Relationship status
    status: str                  # new, engaged, positive, negative, blocked
    
    # Calculated scores
    relationship_score: int
    engagement_quality: float


@dataclass
class EngagementRecord:
    engagement_id: UUID
    engaged_at: datetime
    post_id: UUID
    response_type: str           # comment, reply, mention
    our_content: str
    
    # Outcome
    author_responded: bool
    response_sentiment: Optional[str]  # positive, neutral, negative
    response_engagement: int      # Likes on our response
```

### Relationship Scoring

| Signal | Points | Interpretation |
|--------|--------|----------------|
| No history | 0 | Unknown |
| Discovered before | 2 | Familiar |
| Engaged once | 5 | Initial contact |
| Multiple engagements | 8 | Active relationship |
| Author responded positively | 15 | Good relationship |
| Author responded negatively | -15 | Problematic |
| High response rate | 10 | Engaged audience |
| No responses | -3 | One-sided |

```python
def calculate_relationship_score(relationship: AuthorRelationship) -> int:
    """Calculate relationship score."""
    
    if not relationship:
        return 0
    
    score = 0
    
    # Base for history
    if relationship.posts_discovered > 0:
        score += 2
    
    # Engagement count
    if relationship.engagement_count >= 1:
        score += 5
    if relationship.engagement_count >= 3:
        score += 3  # Additional for multiple
    if relationship.engagement_count >= 5:
        score += 2  # Additional for many
    
    # Response quality
    if relationship.positive_responses > 0:
        score += min(15, relationship.positive_responses * 5)
    
    if relationship.negative_responses > 0:
        score -= min(15, relationship.negative_responses * 10)
    
    # Response rate
    if relationship.engagement_count > 0:
        response_rate = (
            relationship.positive_responses + relationship.neutral_responses
        ) / relationship.engagement_count
        
        if response_rate > 0.5:
            score += 10
        elif response_rate > 0.2:
            score += 5
        elif response_rate == 0:
            score -= 3
    
    return score
```

### Relationship Status Determination

```python
def determine_relationship_status(relationship: AuthorRelationship) -> str:
    """Determine relationship status category."""
    
    if not relationship or relationship.engagement_count == 0:
        return 'new'
    
    if relationship.negative_responses > 0:
        if relationship.negative_responses > relationship.positive_responses:
            return 'negative'
    
    if relationship.positive_responses >= 2:
        return 'positive'
    
    if relationship.engagement_count >= 1:
        return 'engaged'
    
    return 'new'
```

### Engagement Frequency Control

Prevent over-engaging with any single author.

| Time Since Last Engagement | Can Engage? |
|----------------------------|-------------|
| < 24 hours | Only if they initiated |
| 24-72 hours | Yes, if relevant |
| 72 hours - 1 week | Yes |
| > 1 week | Yes, prioritize |

```python
def check_engagement_frequency(relationship: AuthorRelationship) -> Tuple[bool, str]:
    """Check if we should engage based on frequency."""
    
    if not relationship or not relationship.last_engaged_at:
        return True, 'no_history'
    
    now = datetime.now(timezone.utc)
    hours_since = (now - relationship.last_engaged_at).total_seconds() / 3600
    
    if hours_since < 24:
        return False, 'too_recent'
    elif hours_since < 72:
        return True, 'recent_ok'
    elif hours_since < 168:  # 1 week
        return True, 'good_spacing'
    else:
        return True, 'should_reengage'
```

## 7.6.6 Risk Assessment

### Risk Signals

#### Controversial Content History

| Signal | Risk Level | Detection |
|--------|------------|-----------|
| Political content in bio | Medium | Keyword analysis |
| Inflammatory language history | High | Content analysis |
| Frequent arguments | High | Engagement pattern |
| Blocked by many | High | If detectable |
| Verified controversial figure | High | Known list |

```python
def assess_controversial_risk(author: NormalizedAuthor) -> Tuple[int, List[str]]:
    """Assess risk of controversial author."""
    
    risk_score = 0
    risk_factors = []
    
    if not author.bio:
        return 0, []
    
    bio_lower = author.bio.lower()
    
    # Political indicators
    political_patterns = ['maga', 'resist', 'activist', 'democrat', 'republican',
                         'socialist', 'libertarian', 'anarchist']
    if any(p in bio_lower for p in political_patterns):
        risk_score += 15
        risk_factors.append('political_content')
    
    # Inflammatory indicators
    inflammatory_patterns = ['fight', 'destroy', 'expose', 'truth bomb']
    if any(p in bio_lower for p in inflammatory_patterns):
        risk_score += 10
        risk_factors.append('inflammatory_language')
    
    # Extreme views
    extreme_patterns = ['conspiracy', 'truther', 'pilled']
    if any(p in bio_lower for p in extreme_patterns):
        risk_score += 20
        risk_factors.append('extreme_views')
    
    return risk_score, risk_factors
```

#### Competitor Affiliation

| Affiliation | Risk Level | Action |
|-------------|------------|--------|
| Works at competitor | High | Flag for review |
| Promotes competitor | Medium | Flag for review |
| Former competitor employee | Low | Monitor |
| Invested in competitor | Medium | Flag |

```python
def assess_competitor_risk(
    author: NormalizedAuthor,
    competitor_list: List[str]
) -> Tuple[int, str]:
    """Assess competitor affiliation risk."""
    
    if not author.bio:
        return 0, None
    
    bio_lower = author.bio.lower()
    
    for competitor in competitor_list:
        if competitor.lower() in bio_lower:
            # Check if employee
            if any(p in bio_lower for p in ['at ' + competitor.lower(), 
                                            competitor.lower() + ' team',
                                            'work at', 'engineer at']):
                return 30, f'employee_at_{competitor}'
            
            # Check if investor/advisor
            if any(p in bio_lower for p in ['investor', 'advisor', 'board']):
                return 20, f'affiliated_with_{competitor}'
            
            # General mention
            return 10, f'mentions_{competitor}'
    
    return 0, None
```

#### Troll/Bad Actor Detection

| Signal | Risk Level | Detection |
|--------|------------|-----------|
| High negative engagement rate | High | Many angry replies |
| Many blocked indicators | High | If available |
| New account + aggressive | High | Combined signals |
| Known troll patterns | High | Pattern matching |

```python
def assess_troll_risk(author: NormalizedAuthor, quality: AccountQualityResult) -> int:
    """Assess risk of troll/bad actor."""
    
    risk_score = 0
    
    # New account is more risky
    if 'new_account' in quality.flags:
        risk_score += 10
    
    # Suspicious patterns
    if 'suspicious_ratio' in quality.flags:
        risk_score += 10
    
    # Bot-like behavior
    if 'possible_bot' in quality.flags:
        risk_score += 15
    
    # Very low quality overall
    if quality.tier == 'suspicious':
        risk_score += 20
    
    return risk_score
```

### Complete Risk Assessment

```python
@dataclass
class RiskAssessmentResult:
    total_risk: int
    risk_level: str  # low, medium, high, critical
    
    controversial_risk: int
    controversial_factors: List[str]
    competitor_risk: int
    competitor_affiliation: Optional[str]
    troll_risk: int
    
    should_engage: bool
    requires_review: bool
    block_reason: Optional[str]


def calculate_risk_score(
    author: NormalizedAuthor,
    quality: AccountQualityResult,
    competitor_list: List[str]
) -> RiskAssessmentResult:
    """Calculate overall risk assessment."""
    
    controversial_risk, controversial_factors = assess_controversial_risk(author)
    competitor_risk, competitor_affiliation = assess_competitor_risk(author, competitor_list)
    troll_risk = assess_troll_risk(author, quality)
    
    total_risk = controversial_risk + competitor_risk + troll_risk
    
    # Determine risk level
    if total_risk >= 50:
        risk_level = 'critical'
    elif total_risk >= 30:
        risk_level = 'high'
    elif total_risk >= 15:
        risk_level = 'medium'
    else:
        risk_level = 'low'
    
    # Engagement decision
    should_engage = risk_level in ['low', 'medium']
    requires_review = risk_level in ['medium', 'high']
    
    block_reason = None
    if risk_level == 'critical':
        if competitor_affiliation:
            block_reason = f'competitor: {competitor_affiliation}'
        elif controversial_factors:
            block_reason = f'controversial: {controversial_factors[0]}'
        else:
            block_reason = 'high_risk'
    
    return RiskAssessmentResult(
        total_risk=total_risk,
        risk_level=risk_level,
        controversial_risk=controversial_risk,
        controversial_factors=controversial_factors,
        competitor_risk=competitor_risk,
        competitor_affiliation=competitor_affiliation,
        troll_risk=troll_risk,
        should_engage=should_engage,
        requires_review=requires_review,
        block_reason=block_reason,
    )
```

## 7.6.7 Combined Author Score

### Author Factor Calculation

Combine all dimensions into a single author factor for scoring.

```python
@dataclass
class AuthorEvaluationResult:
    author_id: UUID
    
    # Component scores
    quality: AccountQualityResult
    influence: InfluenceScoreResult
    relevance: RelevanceScoreResult
    relationship: Optional[AuthorRelationship]
    relationship_score: int
    risk: RiskAssessmentResult
    
    # Combined metrics
    author_score: int           # 0-100 overall score
    author_factor: float        # 0.5-1.5 multiplier for priority scoring
    
    # Engagement recommendations
    should_engage: bool
    engagement_priority: str    # high, medium, low, skip
    requires_review: bool
    flags: List[str]
    
    evaluated_at: datetime


def calculate_author_factor(
    quality: AccountQualityResult,
    influence: InfluenceScoreResult,
    relevance: RelevanceScoreResult,
    relationship_score: int,
    risk: RiskAssessmentResult
) -> Tuple[int, float]:
    """Calculate combined author score and factor."""
    
    # Weight the components
    # Quality: 20%, Influence: 25%, Relevance: 30%, Relationship: 15%, Risk: 10%
    
    quality_normalized = max(0, min(100, (quality.total + 20) * 2))
    influence_normalized = influence.normalized
    relevance_normalized = relevance.normalized
    relationship_normalized = max(0, min(100, (relationship_score + 10) * 3))
    risk_penalty = min(30, risk.total_risk)
    
    author_score = int(
        quality_normalized * 0.20 +
        influence_normalized * 0.25 +
        relevance_normalized * 0.30 +
        relationship_normalized * 0.15 -
        risk_penalty * 0.10
    )
    
    author_score = max(0, min(100, author_score))
    
    # Convert to factor (0.5 - 1.5 range)
    # score 0 -> factor 0.5
    # score 50 -> factor 1.0
    # score 100 -> factor 1.5
    author_factor = 0.5 + (author_score / 100)
    
    return author_score, author_factor
```

### Complete Author Evaluation

```python
def evaluate_author(
    author: NormalizedAuthor,
    competitor_list: List[str] = None
) -> AuthorEvaluationResult:
    """Perform complete author evaluation."""
    
    competitor_list = competitor_list or []
    
    # Calculate component scores
    quality = calculate_account_quality(author)
    influence = calculate_influence_score(author)
    relevance = calculate_relevance_score(author)
    
    # Get relationship if exists
    relationship = get_author_relationship(author.id)
    relationship_score = calculate_relationship_score(relationship) if relationship else 0
    
    # Calculate risk
    risk = calculate_risk_score(author, quality, competitor_list)
    
    # Calculate combined score and factor
    author_score, author_factor = calculate_author_factor(
        quality, influence, relevance, relationship_score, risk
    )
    
    # Determine engagement recommendation
    should_engage = (
        risk.should_engage and
        quality.tier not in ['suspicious'] and
        author_score >= 20
    )
    
    # Check frequency limit
    if relationship:
        can_engage, freq_reason = check_engagement_frequency(relationship)
        if not can_engage:
            should_engage = False
    
    # Determine priority
    if not should_engage:
        engagement_priority = 'skip'
    elif author_score >= 70:
        engagement_priority = 'high'
    elif author_score >= 40:
        engagement_priority = 'medium'
    else:
        engagement_priority = 'low'
    
    # Collect flags
    flags = []
    flags.extend(quality.flags)
    if risk.controversial_factors:
        flags.extend(risk.controversial_factors)
    if risk.competitor_affiliation:
        flags.append('competitor_affiliated')
    if relevance.is_target_audience:
        flags.append('target_audience')
    if influence.tier in ['macro', 'mega', 'celebrity']:
        flags.append('influencer')
    
    return AuthorEvaluationResult(
        author_id=author.id,
        quality=quality,
        influence=influence,
        relevance=relevance,
        relationship=relationship,
        relationship_score=relationship_score,
        risk=risk,
        author_score=author_score,
        author_factor=author_factor,
        should_engage=should_engage,
        engagement_priority=engagement_priority,
        requires_review=risk.requires_review,
        flags=flags,
        evaluated_at=datetime.now(timezone.utc),
    )
```

## 7.6.8 Author Database Schema

### Authors Table (Extended)

```sql
CREATE TABLE discovered_authors (
    -- Identity
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    platform VARCHAR(50) NOT NULL,
    platform_author_id VARCHAR(255) NOT NULL,
    
    -- Profile data
    handle VARCHAR(255),
    display_name VARCHAR(255),
    avatar_url TEXT,
    bio TEXT,
    location VARCHAR(255),
    website_url TEXT,
    
    -- Metrics
    followers_count INTEGER,
    following_count INTEGER,
    posts_count INTEGER,
    verified BOOLEAN NOT NULL DEFAULT false,
    
    -- Account info
    account_created_at TIMESTAMP WITH TIME ZONE,
    
    -- Calculated scores (refreshed periodically)
    quality_score INTEGER,
    quality_tier VARCHAR(20),
    influence_score INTEGER,
    influence_tier VARCHAR(20),
    relevance_score INTEGER,
    is_target_audience BOOLEAN,
    relationship_score INTEGER,
    risk_score INTEGER,
    risk_level VARCHAR(20),
    
    -- Combined
    author_score INTEGER,
    author_factor DECIMAL(3, 2),
    
    -- Tracking
    first_seen_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    last_seen_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    posts_discovered INTEGER NOT NULL DEFAULT 0,
    last_evaluated_at TIMESTAMP WITH TIME ZONE,
    
    -- Status
    engagement_status VARCHAR(20) DEFAULT 'new',
    is_blocked BOOLEAN NOT NULL DEFAULT false,
    block_reason TEXT,
    
    -- Flags (JSONB array)
    flags JSONB NOT NULL DEFAULT '[]',
    
    -- Full evaluation data
    evaluation_data JSONB,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    CONSTRAINT authors_platform_id_unique UNIQUE (platform, platform_author_id)
);

-- Indexes
CREATE INDEX idx_authors_platform ON discovered_authors(platform);
CREATE INDEX idx_authors_author_score ON discovered_authors(author_score DESC NULLS LAST);
CREATE INDEX idx_authors_influence ON discovered_authors(influence_tier);
CREATE INDEX idx_authors_target ON discovered_authors(is_target_audience) WHERE is_target_audience = true;
CREATE INDEX idx_authors_blocked ON discovered_authors(is_blocked) WHERE is_blocked = true;
CREATE INDEX idx_authors_risk ON discovered_authors(risk_level);
```

### Author Engagements Table

```sql
CREATE TABLE author_engagements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    author_id UUID NOT NULL REFERENCES discovered_authors(id),
    
    -- Engagement details
    post_id UUID NOT NULL REFERENCES discovered_posts(id),
    engagement_type VARCHAR(50) NOT NULL,
    our_response_id UUID,
    our_content TEXT,
    
    -- Timing
    engaged_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    -- Outcome (updated after)
    author_responded BOOLEAN,
    response_at TIMESTAMP WITH TIME ZONE,
    response_sentiment VARCHAR(20),
    response_engagement INTEGER,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_engagements_author ON author_engagements(author_id);
CREATE INDEX idx_engagements_date ON author_engagements(engaged_at DESC);
```

### Author Blocklist Table

```sql
CREATE TABLE author_blocklist (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Can block by author_id or platform handle
    author_id UUID REFERENCES discovered_authors(id),
    platform VARCHAR(50),
    platform_handle VARCHAR(255),
    
    -- Block details
    block_reason VARCHAR(100) NOT NULL,
    block_type VARCHAR(50) NOT NULL,  -- permanent, temporary, review
    notes TEXT,
    
    -- Timing
    blocked_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    blocked_by UUID,
    expires_at TIMESTAMP WITH TIME ZONE,  -- For temporary blocks
    
    -- Status
    is_active BOOLEAN NOT NULL DEFAULT true,
    unblocked_at TIMESTAMP WITH TIME ZONE,
    unblocked_by UUID,
    
    CONSTRAINT blocklist_author_unique UNIQUE (author_id),
    CONSTRAINT blocklist_handle_unique UNIQUE (platform, platform_handle)
);

CREATE INDEX idx_blocklist_active ON author_blocklist(is_active) WHERE is_active = true;
CREATE INDEX idx_blocklist_platform ON author_blocklist(platform, platform_handle);
```

## 7.6.9 Author Evaluation Pipeline

### Evaluation Timing

Authors can be evaluated:

1. **On discovery:** When first seen, quick evaluation
2. **On engagement consideration:** Before deciding to engage
3. **Periodically:** Re-evaluate existing authors
4. **On demand:** Manual evaluation request

### Batch Evaluation

```python
async def evaluate_authors_batch(author_ids: List[UUID]) -> List[AuthorEvaluationResult]:
    """Evaluate multiple authors."""
    
    results = []
    competitor_list = get_competitor_list()
    
    for author_id in author_ids:
        author = get_author(author_id)
        if not author:
            continue
        
        result = evaluate_author(author, competitor_list)
        store_author_evaluation(author_id, result)
        
        results.append(result)
    
    return results


def store_author_evaluation(author_id: UUID, result: AuthorEvaluationResult):
    """Store evaluation results."""
    
    db.execute("""
        UPDATE discovered_authors
        SET 
            quality_score = %(quality_score)s,
            quality_tier = %(quality_tier)s,
            influence_score = %(influence_score)s,
            influence_tier = %(influence_tier)s,
            relevance_score = %(relevance_score)s,
            is_target_audience = %(is_target)s,
            relationship_score = %(relationship_score)s,
            risk_score = %(risk_score)s,
            risk_level = %(risk_level)s,
            author_score = %(author_score)s,
            author_factor = %(author_factor)s,
            flags = %(flags)s,
            evaluation_data = %(evaluation_data)s,
            last_evaluated_at = NOW(),
            updated_at = NOW()
        WHERE id = %(author_id)s
    """, {
        'author_id': author_id,
        'quality_score': result.quality.total,
        'quality_tier': result.quality.tier,
        'influence_score': result.influence.normalized,
        'influence_tier': result.influence.tier,
        'relevance_score': result.relevance.normalized,
        'is_target': result.relevance.is_target_audience,
        'relationship_score': result.relationship_score,
        'risk_score': result.risk.total_risk,
        'risk_level': result.risk.risk_level,
        'author_score': result.author_score,
        'author_factor': result.author_factor,
        'flags': json.dumps(result.flags),
        'evaluation_data': json.dumps(asdict(result)),
    })
```

### Periodic Re-evaluation

```python
async def reevaluate_authors_periodic():
    """Re-evaluate authors that haven't been evaluated recently."""
    
    # Get authors needing re-evaluation
    authors = db.query("""
        SELECT id FROM discovered_authors
        WHERE 
            (last_evaluated_at IS NULL OR last_evaluated_at < NOW() - INTERVAL '7 days')
            AND last_seen_at > NOW() - INTERVAL '30 days'
            AND NOT is_blocked
        ORDER BY 
            CASE WHEN is_target_audience THEN 0 ELSE 1 END,
            author_score DESC NULLS LAST
        LIMIT 500
    """)
    
    author_ids = [a.id for a in authors]
    
    results = await evaluate_authors_batch(author_ids)
    
    log.info(f"Re-evaluated {len(results)} authors")
```

## 7.6.10 Monitoring and Metrics

### Author Metrics

```python
# Distribution of author scores
author_score_histogram = Histogram(
    'author_score',
    'Distribution of author scores',
    buckets=[10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
)

# Authors by quality tier
author_quality_tier = Gauge(
    'author_quality_count',
    'Count by quality tier',
    ['tier']
)

# Authors by influence tier
author_influence_tier = Gauge(
    'author_influence_count',
    'Count by influence tier',
    ['tier']
)

# Target audience rate
author_target_audience_rate = Gauge(
    'author_target_audience_rate',
    'Percentage of authors in target audience'
)

# Risk distribution
author_risk_level = Gauge(
    'author_risk_count',
    'Count by risk level',
    ['level']
)

# Blocked authors
author_blocked_count = Gauge(
    'author_blocked_total',
    'Total blocked authors'
)
```

### Dashboard Components

1. **Author Score Distribution:** Histogram of overall scores
2. **Quality Breakdown:** Pie chart by quality tier
3. **Influence Breakdown:** Pie chart by influence tier
4. **Target Audience Rate:** Percentage over time
5. **Risk Levels:** Distribution of risk levels
6. **Top Authors:** Leaderboard of highest-scoring authors
7. **Relationship Status:** Distribution of engagement status
8. **Blocked Authors:** Count and reasons

## 7.6.11 Implementation Guidance for Neoclaw

### Implementation Order

1. **Build quality scorer**
   - Account age
   - Profile completeness
   - Follower ratio
   - Bot detection

2. **Build influence scorer**
   - Follower tiers
   - Verified status
   - Recognition signals

3. **Build relevance scorer**
   - Bio keyword analysis
   - Role detection
   - Company context

4. **Build risk assessor**
   - Controversial detection
   - Competitor detection
   - Troll patterns

5. **Implement relationship tracking**
   - Schema and models
   - Engagement recording
   - Frequency control

6. **Combine into full evaluation**
   - Author factor calculation
   - Engagement recommendations

7. **Build pipeline**
   - Batch evaluation
   - Periodic re-evaluation
   - Storage

8. **Add monitoring**
   - Metrics
   - Dashboard

### Testing Checklist

#### Unit Tests
- [ ] Quality scoring components
- [ ] Influence scoring
- [ ] Bio keyword extraction
- [ ] Role detection
- [ ] Risk assessment
- [ ] Author factor calculation

#### Integration Tests
- [ ] Full evaluation pipeline
- [ ] Storage and retrieval
- [ ] Relationship tracking

#### Validation Tests
- [ ] Known influencers score high influence
- [ ] Known domain experts score high relevance
- [ ] Obvious bots flagged
- [ ] Competitors detected

### Common Pitfalls

**Stale evaluation data:**
Author profiles change. Re-evaluate periodically.

**Missing bio:**
Many authors have no bio. Handle gracefully with defaults.

**Platform differences:**
Metrics mean different things on different platforms. Adjust thresholds.

**Over-blocking:**
Too aggressive risk detection blocks good opportunities. Tune carefully.

**Relationship staleness:**
Relationships change. Expired engagements shouldn't count forever.

---

**END OF SECTION 7.6**

Section 7.7 continues with Filtering & Thresholds specification.
-e 


# SECTION 7.7: FILTERING & THRESHOLDS

## 7.7.1 What Filtering Is

### The Core Concept

Filtering is the process of removing posts that should not proceed to the engagement queue. After discovery, classification, and scoring, filtering applies rules to eliminate low-quality, unsafe, off-topic, or otherwise unsuitable content.

**Input:** Scored posts with relevance, opportunity, and author scores
**Output:** Posts that pass all filters, ready for prioritization

Filtering answers the question: "Should this post be considered for engagement at all?"

### Why Filtering Matters

**Quality control:**
Remove low-quality content before it consumes queue space and review resources.

**Safety:**
Block potentially harmful content — controversial topics, crisis situations, unsafe accounts.

**Business rules:**
Enforce business logic — don't engage with competitors, don't re-engage too frequently.

**Efficiency:**
Reduce downstream processing load by eliminating poor candidates early.

**Brand protection:**
Prevent engagement with content that could damage brand reputation.

### Filtering vs Prioritization

**Filtering:** Binary decision — yes or no. Does this post meet minimum criteria?

**Prioritization:** Ranking decision — how good is this compared to others?

A post that passes filtering isn't guaranteed engagement — it still competes in prioritization. But a post that fails filtering is definitively excluded.

### Filter Categories

1. **Quality filters:** Minimum scores, content quality
2. **Safety filters:** Dangerous content, crisis detection
3. **Business filters:** Competitive, frequency, blocklists
4. **Recency filters:** Age limits, staleness
5. **Capacity filters:** Queue limits, rate limiting

## 7.7.2 Filter Execution Order

### Ordering Principles

Filters should be ordered by:

1. **Cost:** Cheap filters first (avoid expensive checks for obvious rejects)
2. **Rejection rate:** High-rejection filters first (eliminate volume early)
3. **Dependencies:** Some filters require prior data (scores, classification)

### Recommended Filter Order

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              FILTER PIPELINE                                        │
│                                                                                     │
│  Stage 1: Pre-Score Filters (Before Classification/Scoring)                        │
│  ─────────────────────────────────────────────────────────────────────────────────  │
│  1. Content length filter (< 10 chars → reject)                                    │
│  2. Language filter (non-target language → reject)                                 │
│  3. Duplicate filter (already seen → reject)                                       │
│  4. Author blocklist (blocked author → reject)                                     │
│                                                                                     │
│  Stage 2: Post-Classification Filters (After Classification)                       │
│  ─────────────────────────────────────────────────────────────────────────────────  │
│  5. Classification filter (off_topic → reject)                                     │
│  6. Controversial filter (controversial_topic → review/reject)                     │
│  7. Safety keyword filter (crisis keywords → reject)                               │
│                                                                                     │
│  Stage 3: Post-Score Filters (After Scoring)                                       │
│  ─────────────────────────────────────────────────────────────────────────────────  │
│  8. Relevance threshold (< min_relevance → reject)                                 │
│  9. Opportunity threshold (< min_opportunity → reject)                             │
│  10. Author quality filter (suspicious author → reject)                            │
│                                                                                     │
│  Stage 4: Business Filters                                                          │
│  ─────────────────────────────────────────────────────────────────────────────────  │
│  11. Already engaged filter (engaged with this post → reject)                      │
│  12. Frequency filter (engaged with author recently → reject)                      │
│  13. Competitor filter (competitor content → review)                               │
│                                                                                     │
│  Stage 5: Recency Filters                                                           │
│  ─────────────────────────────────────────────────────────────────────────────────  │
│  14. Age filter (> max_age → reject)                                               │
│  15. Conversation staleness (no activity → reject)                                 │
│                                                                                     │
│  Stage 6: Capacity Filters                                                          │
│  ─────────────────────────────────────────────────────────────────────────────────  │
│  16. Queue capacity (queue full → reject lowest priority)                          │
│  17. Daily limit (at daily cap → reject)                                           │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

### Filter Result Structure

```python
@dataclass
class FilterResult:
    passed: bool
    filter_name: str
    filter_stage: int
    reason: Optional[str]
    value: Optional[Any]       # The value that was checked
    threshold: Optional[Any]   # The threshold it was checked against
    
    
@dataclass
class FilterPipelineResult:
    post_id: UUID
    passed: bool
    
    filters_run: int
    filters_passed: int
    filters_failed: int
    
    results: List[FilterResult]
    
    failed_at: Optional[str]   # Name of first failed filter
    failed_reason: Optional[str]
    
    duration_ms: float
    filtered_at: datetime
```

## 7.7.3 Quality Filters

### Content Length Filter

Reject extremely short content.

**Configuration:**
```python
MIN_CONTENT_LENGTH = 10  # characters
MIN_CONTENT_WORDS = 2    # words
```

**Implementation:**
```python
def filter_content_length(post: NormalizedPost) -> FilterResult:
    """Filter posts that are too short."""
    
    content = post.content_text.strip()
    length = len(content)
    word_count = len(content.split())
    
    if length < MIN_CONTENT_LENGTH:
        return FilterResult(
            passed=False,
            filter_name='content_length',
            filter_stage=1,
            reason='content_too_short',
            value=length,
            threshold=MIN_CONTENT_LENGTH,
        )
    
    if word_count < MIN_CONTENT_WORDS:
        return FilterResult(
            passed=False,
            filter_name='content_length',
            filter_stage=1,
            reason='too_few_words',
            value=word_count,
            threshold=MIN_CONTENT_WORDS,
        )
    
    return FilterResult(
        passed=True,
        filter_name='content_length',
        filter_stage=1,
        reason=None,
        value=length,
        threshold=MIN_CONTENT_LENGTH,
    )
```

### Language Filter

Only process posts in target languages.

**Configuration:**
```python
TARGET_LANGUAGES = ['en']  # ISO 639-1 codes
LANGUAGE_CONFIDENCE_THRESHOLD = 0.8
```

**Implementation:**
```python
def filter_language(post: NormalizedPost) -> FilterResult:
    """Filter posts not in target language."""
    
    detected_language = post.language
    
    # If language not detected, allow through (will be checked later)
    if not detected_language:
        return FilterResult(
            passed=True,
            filter_name='language',
            filter_stage=1,
            reason='language_unknown',
            value=None,
            threshold=TARGET_LANGUAGES,
        )
    
    if detected_language not in TARGET_LANGUAGES:
        return FilterResult(
            passed=False,
            filter_name='language',
            filter_stage=1,
            reason='language_not_supported',
            value=detected_language,
            threshold=TARGET_LANGUAGES,
        )
    
    return FilterResult(
        passed=True,
        filter_name='language',
        filter_stage=1,
        reason=None,
        value=detected_language,
        threshold=TARGET_LANGUAGES,
    )
```

### Relevance Threshold Filter

Reject posts below minimum relevance score.

**Configuration:**
```python
MIN_RELEVANCE_SCORE = 40  # 0-100 scale
# Can be overridden per campaign
```

**Implementation:**
```python
def filter_relevance_threshold(
    post: NormalizedPost,
    campaign_config: dict
) -> FilterResult:
    """Filter posts below relevance threshold."""
    
    threshold = campaign_config.get('min_relevance_score', MIN_RELEVANCE_SCORE)
    
    relevance_score = post.scores.get('relevance', {}).get('total', 0)
    
    if relevance_score < threshold:
        return FilterResult(
            passed=False,
            filter_name='relevance_threshold',
            filter_stage=3,
            reason='relevance_below_threshold',
            value=relevance_score,
            threshold=threshold,
        )
    
    return FilterResult(
        passed=True,
        filter_name='relevance_threshold',
        filter_stage=3,
        reason=None,
        value=relevance_score,
        threshold=threshold,
    )
```

### Opportunity Threshold Filter

Reject posts below minimum opportunity score.

**Configuration:**
```python
MIN_OPPORTUNITY_SCORE = 30  # 0-100 scale
```

**Implementation:**
```python
def filter_opportunity_threshold(
    post: NormalizedPost,
    campaign_config: dict
) -> FilterResult:
    """Filter posts below opportunity threshold."""
    
    threshold = campaign_config.get('min_opportunity_score', MIN_OPPORTUNITY_SCORE)
    
    opportunity_score = post.scores.get('opportunity', {}).get('total', 0)
    
    if opportunity_score < threshold:
        return FilterResult(
            passed=False,
            filter_name='opportunity_threshold',
            filter_stage=3,
            reason='opportunity_below_threshold',
            value=opportunity_score,
            threshold=threshold,
        )
    
    return FilterResult(
        passed=True,
        filter_name='opportunity_threshold',
        filter_stage=3,
        reason=None,
        value=opportunity_score,
        threshold=threshold,
    )
```

### Author Quality Filter

Reject posts from low-quality or suspicious accounts.

**Configuration:**
```python
MIN_AUTHOR_QUALITY_TIER = 'poor'  # Reject 'suspicious' only
# Or use numeric: MIN_AUTHOR_QUALITY_SCORE = -5
```

**Implementation:**
```python
def filter_author_quality(post: NormalizedPost) -> FilterResult:
    """Filter posts from low-quality authors."""
    
    author_eval = post.author_evaluation
    
    if not author_eval:
        # No evaluation yet - allow through
        return FilterResult(
            passed=True,
            filter_name='author_quality',
            filter_stage=3,
            reason='no_evaluation',
            value=None,
            threshold=None,
        )
    
    quality_tier = author_eval.get('quality', {}).get('tier', 'average')
    
    if quality_tier == 'suspicious':
        return FilterResult(
            passed=False,
            filter_name='author_quality',
            filter_stage=3,
            reason='suspicious_author',
            value=quality_tier,
            threshold='poor',
        )
    
    # Also check for specific flags
    flags = author_eval.get('flags', [])
    blocking_flags = ['possible_bot', 'spam_account']
    
    for flag in blocking_flags:
        if flag in flags:
            return FilterResult(
                passed=False,
                filter_name='author_quality',
                filter_stage=3,
                reason=f'author_flag_{flag}',
                value=flag,
                threshold=None,
            )
    
    return FilterResult(
        passed=True,
        filter_name='author_quality',
        filter_stage=3,
        reason=None,
        value=quality_tier,
        threshold='poor',
    )
```

## 7.7.4 Safety Filters

### Classification-Based Safety Filter

Reject or flag based on classification.

**Configuration:**
```python
BLOCKED_CLASSIFICATIONS = ['off_topic']
REVIEW_CLASSIFICATIONS = ['controversial_topic', 'competitor_mention']
```

**Implementation:**
```python
def filter_classification_safety(post: NormalizedPost) -> FilterResult:
    """Filter based on classification."""
    
    classification = post.classification
    
    if not classification:
        return FilterResult(
            passed=True,
            filter_name='classification_safety',
            filter_stage=2,
            reason='not_classified',
            value=None,
            threshold=None,
        )
    
    primary = classification.get('primary')
    
    if primary in BLOCKED_CLASSIFICATIONS:
        return FilterResult(
            passed=False,
            filter_name='classification_safety',
            filter_stage=2,
            reason=f'blocked_classification_{primary}',
            value=primary,
            threshold=BLOCKED_CLASSIFICATIONS,
        )
    
    if primary in REVIEW_CLASSIFICATIONS:
        # Don't reject, but flag for review
        return FilterResult(
            passed=True,  # Pass but with flag
            filter_name='classification_safety',
            filter_stage=2,
            reason=f'requires_review_{primary}',
            value=primary,
            threshold=REVIEW_CLASSIFICATIONS,
        )
    
    return FilterResult(
        passed=True,
        filter_name='classification_safety',
        filter_stage=2,
        reason=None,
        value=primary,
        threshold=None,
    )
```

### Safety Keyword Filter

Reject posts containing dangerous keywords.

**Configuration:**
```python
SAFETY_BLOCKLIST = {
    # Crisis keywords
    'crisis': ['shooting', 'mass casualty', 'terrorist attack', 'explosion', 
               'hostage', 'active shooter', 'bombing'],
    
    # Tragedy keywords
    'tragedy': ['died', 'death of', 'passed away', 'rip', 'tragic', 
                'condolences', 'prayers for'],
    
    # Self-harm keywords
    'self_harm': ['suicide', 'self-harm', 'end my life', 'kill myself'],
    
    # Violence keywords
    'violence': ['murder', 'assault', 'attack', 'violent'],
    
    # Hate speech
    'hate': ['racist', 'sexist', 'homophobic', 'slur'],
}

# Keywords that trigger immediate block
HARD_BLOCK_KEYWORDS = ['active shooter', 'mass casualty', 'terrorist attack']

# Keywords that trigger review
REVIEW_KEYWORDS = ['died', 'death of', 'passed away']
```

**Implementation:**
```python
def filter_safety_keywords(post: NormalizedPost) -> FilterResult:
    """Filter posts with safety-concerning keywords."""
    
    content = post.content_text.lower()
    
    # Check hard blocks first
    for keyword in HARD_BLOCK_KEYWORDS:
        if keyword in content:
            return FilterResult(
                passed=False,
                filter_name='safety_keywords',
                filter_stage=2,
                reason='hard_block_keyword',
                value=keyword,
                threshold=HARD_BLOCK_KEYWORDS,
            )
    
    # Check category keywords
    matched_categories = []
    matched_keywords = []
    
    for category, keywords in SAFETY_BLOCKLIST.items():
        for keyword in keywords:
            if keyword in content:
                matched_categories.append(category)
                matched_keywords.append(keyword)
    
    if matched_keywords:
        # Determine if block or review
        if any(kw in REVIEW_KEYWORDS for kw in matched_keywords):
            return FilterResult(
                passed=True,  # Pass but flag
                filter_name='safety_keywords',
                filter_stage=2,
                reason=f'review_keywords_{",".join(matched_categories[:2])}',
                value=matched_keywords[:3],
                threshold=None,
            )
        else:
            return FilterResult(
                passed=False,
                filter_name='safety_keywords',
                filter_stage=2,
                reason=f'blocked_keywords_{matched_categories[0]}',
                value=matched_keywords[:3],
                threshold=None,
            )
    
    return FilterResult(
        passed=True,
        filter_name='safety_keywords',
        filter_stage=2,
        reason=None,
        value=None,
        threshold=None,
    )
```

### Current Events Safety Filter

Block engagement during active crises or sensitive current events.

**Configuration:**
```python
# Active crisis events (managed dynamically)
ACTIVE_CRISIS_EVENTS = [
    {
        'name': 'Example Crisis',
        'keywords': ['crisis keyword', 'related term'],
        'start_date': '2024-01-15',
        'end_date': None,  # Ongoing
        'action': 'block',  # or 'review'
    }
]
```

**Implementation:**
```python
def filter_current_events_safety(post: NormalizedPost) -> FilterResult:
    """Filter posts related to active crisis events."""
    
    content = post.content_text.lower()
    current_events = get_active_crisis_events()  # From config/database
    
    for event in current_events:
        for keyword in event['keywords']:
            if keyword.lower() in content:
                if event['action'] == 'block':
                    return FilterResult(
                        passed=False,
                        filter_name='current_events_safety',
                        filter_stage=2,
                        reason=f'active_crisis_{event["name"]}',
                        value=keyword,
                        threshold=None,
                    )
                else:
                    return FilterResult(
                        passed=True,
                        filter_name='current_events_safety',
                        filter_stage=2,
                        reason=f'review_crisis_{event["name"]}',
                        value=keyword,
                        threshold=None,
                    )
    
    return FilterResult(
        passed=True,
        filter_name='current_events_safety',
        filter_stage=2,
        reason=None,
        value=None,
        threshold=None,
    )
```

### Author Risk Filter

Block engagement with high-risk authors.

**Implementation:**
```python
def filter_author_risk(post: NormalizedPost) -> FilterResult:
    """Filter posts from high-risk authors."""
    
    author_eval = post.author_evaluation
    
    if not author_eval:
        return FilterResult(
            passed=True,
            filter_name='author_risk',
            filter_stage=3,
            reason='no_evaluation',
            value=None,
            threshold=None,
        )
    
    risk = author_eval.get('risk', {})
    risk_level = risk.get('risk_level', 'low')
    
    if risk_level == 'critical':
        return FilterResult(
            passed=False,
            filter_name='author_risk',
            filter_stage=3,
            reason=f'critical_risk_{risk.get("block_reason", "unknown")}',
            value=risk_level,
            threshold='high',
        )
    
    if risk_level == 'high':
        # High risk requires review, not auto-block
        return FilterResult(
            passed=True,
            filter_name='author_risk',
            filter_stage=3,
            reason='requires_review_high_risk',
            value=risk_level,
            threshold='high',
        )
    
    return FilterResult(
        passed=True,
        filter_name='author_risk',
        filter_stage=3,
        reason=None,
        value=risk_level,
        threshold='high',
    )
```

## 7.7.5 Business Filters

### Author Blocklist Filter

Block engagement with explicitly blocked authors.

**Implementation:**
```python
def filter_author_blocklist(post: NormalizedPost) -> FilterResult:
    """Filter posts from blocked authors."""
    
    author = post.author
    
    # Check by author ID
    if author.id:
        blocked = check_author_blocked(author.id)
        if blocked:
            return FilterResult(
                passed=False,
                filter_name='author_blocklist',
                filter_stage=1,
                reason=f'author_blocked_{blocked.block_reason}',
                value=author.handle,
                threshold=None,
            )
    
    # Check by platform handle
    blocked = check_handle_blocked(author.platform, author.handle)
    if blocked:
        return FilterResult(
            passed=False,
            filter_name='author_blocklist',
            filter_stage=1,
            reason=f'handle_blocked_{blocked.block_reason}',
            value=author.handle,
            threshold=None,
        )
    
    return FilterResult(
        passed=True,
        filter_name='author_blocklist',
        filter_stage=1,
        reason=None,
        value=author.handle,
        threshold=None,
    )


def check_author_blocked(author_id: UUID) -> Optional[BlockRecord]:
    """Check if author is blocked."""
    
    return db.query_one("""
        SELECT * FROM author_blocklist
        WHERE author_id = %(author_id)s
        AND is_active = true
        AND (expires_at IS NULL OR expires_at > NOW())
    """, {'author_id': author_id})


def check_handle_blocked(platform: str, handle: str) -> Optional[BlockRecord]:
    """Check if handle is blocked."""
    
    return db.query_one("""
        SELECT * FROM author_blocklist
        WHERE platform = %(platform)s
        AND platform_handle = %(handle)s
        AND is_active = true
        AND (expires_at IS NULL OR expires_at > NOW())
    """, {'platform': platform, 'handle': handle})
```

### Already Engaged Filter

Don't engage with the same post twice.

**Implementation:**
```python
def filter_already_engaged(post: NormalizedPost) -> FilterResult:
    """Filter posts we've already engaged with."""
    
    # Check engagement history
    previous_engagement = db.query_one("""
        SELECT id, engaged_at FROM engagements
        WHERE post_id = %(post_id)s
        AND status IN ('completed', 'pending', 'published')
    """, {'post_id': post.id})
    
    if previous_engagement:
        return FilterResult(
            passed=False,
            filter_name='already_engaged',
            filter_stage=4,
            reason='already_engaged',
            value=previous_engagement.engaged_at.isoformat(),
            threshold=None,
        )
    
    return FilterResult(
        passed=True,
        filter_name='already_engaged',
        filter_stage=4,
        reason=None,
        value=None,
        threshold=None,
    )
```

### Author Engagement Frequency Filter

Don't engage with same author too frequently.

**Configuration:**
```python
MIN_HOURS_BETWEEN_AUTHOR_ENGAGEMENTS = 24
MAX_ENGAGEMENTS_PER_AUTHOR_PER_WEEK = 3
```

**Implementation:**
```python
def filter_author_frequency(post: NormalizedPost) -> FilterResult:
    """Filter if we've engaged with author too recently."""
    
    author = post.author
    
    if not author.id:
        return FilterResult(
            passed=True,
            filter_name='author_frequency',
            filter_stage=4,
            reason='no_author_id',
            value=None,
            threshold=None,
        )
    
    # Check recent engagement
    recent_engagement = db.query_one("""
        SELECT engaged_at FROM author_engagements
        WHERE author_id = %(author_id)s
        AND engaged_at > NOW() - INTERVAL '%(hours)s hours'
        ORDER BY engaged_at DESC
        LIMIT 1
    """, {
        'author_id': author.id,
        'hours': MIN_HOURS_BETWEEN_AUTHOR_ENGAGEMENTS,
    })
    
    if recent_engagement:
        return FilterResult(
            passed=False,
            filter_name='author_frequency',
            filter_stage=4,
            reason='engaged_too_recently',
            value=recent_engagement.engaged_at.isoformat(),
            threshold=f'{MIN_HOURS_BETWEEN_AUTHOR_ENGAGEMENTS}h',
        )
    
    # Check weekly count
    weekly_count = db.query_scalar("""
        SELECT COUNT(*) FROM author_engagements
        WHERE author_id = %(author_id)s
        AND engaged_at > NOW() - INTERVAL '7 days'
    """, {'author_id': author.id})
    
    if weekly_count >= MAX_ENGAGEMENTS_PER_AUTHOR_PER_WEEK:
        return FilterResult(
            passed=False,
            filter_name='author_frequency',
            filter_stage=4,
            reason='weekly_limit_reached',
            value=weekly_count,
            threshold=MAX_ENGAGEMENTS_PER_AUTHOR_PER_WEEK,
        )
    
    return FilterResult(
        passed=True,
        filter_name='author_frequency',
        filter_stage=4,
        reason=None,
        value=weekly_count,
        threshold=MAX_ENGAGEMENTS_PER_AUTHOR_PER_WEEK,
    )
```

### Competitor Content Filter

Handle competitor-related content with care.

**Configuration:**
```python
COMPETITOR_HANDLING = 'review'  # 'block', 'review', or 'allow'
COMPETITOR_NAMES = ['CompetitorA', 'CompetitorB', 'CompetitorC']
```

**Implementation:**
```python
def filter_competitor_content(post: NormalizedPost) -> FilterResult:
    """Filter or flag competitor-related content."""
    
    # Check classification
    classification = post.classification
    if classification and classification.get('primary') == 'competitor_mention':
        if COMPETITOR_HANDLING == 'block':
            return FilterResult(
                passed=False,
                filter_name='competitor_content',
                filter_stage=4,
                reason='competitor_mention_blocked',
                value='competitor_mention',
                threshold=COMPETITOR_HANDLING,
            )
        elif COMPETITOR_HANDLING == 'review':
            return FilterResult(
                passed=True,
                filter_name='competitor_content',
                filter_stage=4,
                reason='competitor_requires_review',
                value='competitor_mention',
                threshold=COMPETITOR_HANDLING,
            )
    
    # Check content for competitor names
    content = post.content_text.lower()
    for competitor in COMPETITOR_NAMES:
        if competitor.lower() in content:
            if COMPETITOR_HANDLING == 'block':
                return FilterResult(
                    passed=False,
                    filter_name='competitor_content',
                    filter_stage=4,
                    reason='competitor_name_blocked',
                    value=competitor,
                    threshold=COMPETITOR_HANDLING,
                )
            elif COMPETITOR_HANDLING == 'review':
                return FilterResult(
                    passed=True,
                    filter_name='competitor_content',
                    filter_stage=4,
                    reason='competitor_name_requires_review',
                    value=competitor,
                    threshold=COMPETITOR_HANDLING,
                )
    
    return FilterResult(
        passed=True,
        filter_name='competitor_content',
        filter_stage=4,
        reason=None,
        value=None,
        threshold=None,
    )
```

### Duplicate Content Filter

Detect and filter duplicate or near-duplicate content.

**Implementation:**
```python
def filter_duplicate_content(post: NormalizedPost) -> FilterResult:
    """Filter duplicate content."""
    
    # Check by platform post ID (exact duplicate)
    existing = db.query_one("""
        SELECT id FROM discovered_posts
        WHERE platform = %(platform)s
        AND platform_post_id = %(platform_post_id)s
        AND id != %(post_id)s
    """, {
        'platform': post.platform,
        'platform_post_id': post.platform_post_id,
        'post_id': post.id,
    })
    
    if existing:
        return FilterResult(
            passed=False,
            filter_name='duplicate_content',
            filter_stage=1,
            reason='exact_duplicate',
            value=str(existing.id),
            threshold=None,
        )
    
    # Check by content hash (cross-platform duplicate)
    if post.content_hash:
        similar = db.query_one("""
            SELECT id, platform FROM discovered_posts
            WHERE content_hash = %(hash)s
            AND id != %(post_id)s
            AND discovered_at > NOW() - INTERVAL '7 days'
        """, {
            'hash': post.content_hash,
            'post_id': post.id,
        })
        
        if similar:
            return FilterResult(
                passed=False,
                filter_name='duplicate_content',
                filter_stage=1,
                reason='content_hash_duplicate',
                value=f'{similar.platform}:{similar.id}',
                threshold=None,
            )
    
    return FilterResult(
        passed=True,
        filter_name='duplicate_content',
        filter_stage=1,
        reason=None,
        value=None,
        threshold=None,
    )
```

## 7.7.6 Recency Filters

### Post Age Filter

Reject posts that are too old.

**Configuration:**
```python
MAX_POST_AGE_HOURS = 24  # Default
MAX_POST_AGE_BY_PLATFORM = {
    'twitter': 24,
    'linkedin': 72,
    'reddit': 48,
}
```

**Implementation:**
```python
def filter_post_age(post: NormalizedPost) -> FilterResult:
    """Filter posts that are too old."""
    
    max_age = MAX_POST_AGE_BY_PLATFORM.get(post.platform, MAX_POST_AGE_HOURS)
    
    now = datetime.now(timezone.utc)
    age_hours = (now - post.created_at).total_seconds() / 3600
    
    if age_hours > max_age:
        return FilterResult(
            passed=False,
            filter_name='post_age',
            filter_stage=5,
            reason='post_too_old',
            value=round(age_hours, 1),
            threshold=max_age,
        )
    
    return FilterResult(
        passed=True,
        filter_name='post_age',
        filter_stage=5,
        reason=None,
        value=round(age_hours, 1),
        threshold=max_age,
    )
```

### Conversation Staleness Filter

Reject conversations that have gone stale.

**Configuration:**
```python
MAX_HOURS_SINCE_ACTIVITY = 12  # No activity in 12 hours
```

**Implementation:**
```python
def filter_conversation_staleness(post: NormalizedPost) -> FilterResult:
    """Filter conversations that have gone stale."""
    
    # Get last activity time
    last_activity = post.platform_data.get('last_reply_at')
    
    if not last_activity:
        # No activity data - use post creation time
        last_activity = post.created_at
    elif isinstance(last_activity, str):
        last_activity = datetime.fromisoformat(last_activity.replace('Z', '+00:00'))
    
    now = datetime.now(timezone.utc)
    hours_since_activity = (now - last_activity).total_seconds() / 3600
    
    # Only apply if post is old enough to potentially be stale
    post_age_hours = (now - post.created_at).total_seconds() / 3600
    
    if post_age_hours > 6 and hours_since_activity > MAX_HOURS_SINCE_ACTIVITY:
        return FilterResult(
            passed=False,
            filter_name='conversation_staleness',
            filter_stage=5,
            reason='conversation_stale',
            value=round(hours_since_activity, 1),
            threshold=MAX_HOURS_SINCE_ACTIVITY,
        )
    
    return FilterResult(
        passed=True,
        filter_name='conversation_staleness',
        filter_stage=5,
        reason=None,
        value=round(hours_since_activity, 1) if hours_since_activity else None,
        threshold=MAX_HOURS_SINCE_ACTIVITY,
    )
```

### Queue Entry Expiration

Posts in queue expire after a certain time.

**Configuration:**
```python
QUEUE_ENTRY_TTL_HOURS = 6  # Posts expire from queue after 6 hours
```

**Implementation:**
```python
def calculate_queue_expiration(post: NormalizedPost) -> datetime:
    """Calculate when a queue entry should expire."""
    
    now = datetime.now(timezone.utc)
    
    # Base TTL
    ttl_hours = QUEUE_ENTRY_TTL_HOURS
    
    # Adjust based on content type
    classification = post.classification.get('primary') if post.classification else None
    
    # Help-seeking posts expire faster (user needs timely help)
    if classification == 'help_seeking_solution':
        ttl_hours = min(ttl_hours, 4)
    
    # News expires faster
    if classification == 'industry_news':
        ttl_hours = min(ttl_hours, 3)
    
    # Memes/humor can last a bit longer
    if classification == 'meme_humor':
        ttl_hours = min(ttl_hours + 2, 8)
    
    return now + timedelta(hours=ttl_hours)
```

## 7.7.7 Capacity Filters

### Queue Capacity Filter

Manage queue size limits.

**Configuration:**
```python
MAX_QUEUE_SIZE = 500
QUEUE_OVERFLOW_STRATEGY = 'reject_lowest'  # or 'evict_oldest', 'evict_lowest'
```

**Implementation:**
```python
def filter_queue_capacity(
    post: NormalizedPost,
    queue_stats: QueueStats
) -> FilterResult:
    """Filter based on queue capacity."""
    
    if queue_stats.current_size < MAX_QUEUE_SIZE:
        return FilterResult(
            passed=True,
            filter_name='queue_capacity',
            filter_stage=6,
            reason=None,
            value=queue_stats.current_size,
            threshold=MAX_QUEUE_SIZE,
        )
    
    # Queue is at capacity
    if QUEUE_OVERFLOW_STRATEGY == 'reject_lowest':
        # Check if this post has higher priority than lowest in queue
        priority_score = calculate_priority_score(post)
        
        if priority_score > queue_stats.lowest_priority:
            # Will evict lowest priority item
            return FilterResult(
                passed=True,
                filter_name='queue_capacity',
                filter_stage=6,
                reason='will_evict_lowest',
                value=priority_score,
                threshold=queue_stats.lowest_priority,
            )
        else:
            return FilterResult(
                passed=False,
                filter_name='queue_capacity',
                filter_stage=6,
                reason='queue_full_low_priority',
                value=priority_score,
                threshold=queue_stats.lowest_priority,
            )
    
    return FilterResult(
        passed=False,
        filter_name='queue_capacity',
        filter_stage=6,
        reason='queue_at_capacity',
        value=queue_stats.current_size,
        threshold=MAX_QUEUE_SIZE,
    )
```

### Daily Engagement Limit Filter

Enforce daily engagement limits.

**Configuration:**
```python
MAX_DAILY_ENGAGEMENTS = 50
MAX_HOURLY_ENGAGEMENTS = 10
```

**Implementation:**
```python
def filter_daily_limit(campaign_id: UUID) -> FilterResult:
    """Filter if daily engagement limit reached."""
    
    # Get today's engagement count
    daily_count = db.query_scalar("""
        SELECT COUNT(*) FROM engagements
        WHERE campaign_id = %(campaign_id)s
        AND engaged_at > DATE_TRUNC('day', NOW())
        AND status IN ('completed', 'pending', 'published')
    """, {'campaign_id': campaign_id})
    
    if daily_count >= MAX_DAILY_ENGAGEMENTS:
        return FilterResult(
            passed=False,
            filter_name='daily_limit',
            filter_stage=6,
            reason='daily_limit_reached',
            value=daily_count,
            threshold=MAX_DAILY_ENGAGEMENTS,
        )
    
    # Check hourly limit too
    hourly_count = db.query_scalar("""
        SELECT COUNT(*) FROM engagements
        WHERE campaign_id = %(campaign_id)s
        AND engaged_at > NOW() - INTERVAL '1 hour'
        AND status IN ('completed', 'pending', 'published')
    """, {'campaign_id': campaign_id})
    
    if hourly_count >= MAX_HOURLY_ENGAGEMENTS:
        return FilterResult(
            passed=False,
            filter_name='daily_limit',
            filter_stage=6,
            reason='hourly_limit_reached',
            value=hourly_count,
            threshold=MAX_HOURLY_ENGAGEMENTS,
        )
    
    return FilterResult(
        passed=True,
        filter_name='daily_limit',
        filter_stage=6,
        reason=None,
        value=daily_count,
        threshold=MAX_DAILY_ENGAGEMENTS,
    )
```

### Platform Rate Limit Filter

Respect platform-specific rate limits for posting.

**Configuration:**
```python
PLATFORM_POSTING_LIMITS = {
    'twitter': {'per_hour': 5, 'per_day': 50},
    'linkedin': {'per_hour': 3, 'per_day': 20},
    'reddit': {'per_hour': 2, 'per_day': 10},
}
```

**Implementation:**
```python
def filter_platform_rate_limit(post: NormalizedPost) -> FilterResult:
    """Filter if platform rate limit would be exceeded."""
    
    platform = post.platform
    limits = PLATFORM_POSTING_LIMITS.get(platform, {'per_hour': 5, 'per_day': 50})
    
    # Check hourly
    hourly_count = db.query_scalar("""
        SELECT COUNT(*) FROM engagements
        WHERE platform = %(platform)s
        AND engaged_at > NOW() - INTERVAL '1 hour'
        AND status IN ('completed', 'published')
    """, {'platform': platform})
    
    if hourly_count >= limits['per_hour']:
        return FilterResult(
            passed=False,
            filter_name='platform_rate_limit',
            filter_stage=6,
            reason='platform_hourly_limit',
            value=hourly_count,
            threshold=limits['per_hour'],
        )
    
    # Check daily
    daily_count = db.query_scalar("""
        SELECT COUNT(*) FROM engagements
        WHERE platform = %(platform)s
        AND engaged_at > DATE_TRUNC('day', NOW())
        AND status IN ('completed', 'published')
    """, {'platform': platform})
    
    if daily_count >= limits['per_day']:
        return FilterResult(
            passed=False,
            filter_name='platform_rate_limit',
            filter_stage=6,
            reason='platform_daily_limit',
            value=daily_count,
            threshold=limits['per_day'],
        )
    
    return FilterResult(
        passed=True,
        filter_name='platform_rate_limit',
        filter_stage=6,
        reason=None,
        value=daily_count,
        threshold=limits['per_day'],
    )
```

## 7.7.8 Complete Filter Pipeline

### Pipeline Implementation

```python
class FilterPipeline:
    def __init__(self, campaign_config: dict):
        self.campaign_config = campaign_config
        self.filters = self._build_filter_chain()
    
    def _build_filter_chain(self) -> List[Callable]:
        """Build ordered list of filters."""
        
        return [
            # Stage 1: Pre-score
            ('content_length', filter_content_length),
            ('language', filter_language),
            ('duplicate_content', filter_duplicate_content),
            ('author_blocklist', filter_author_blocklist),
            
            # Stage 2: Post-classification
            ('classification_safety', filter_classification_safety),
            ('safety_keywords', filter_safety_keywords),
            ('current_events_safety', filter_current_events_safety),
            
            # Stage 3: Post-score
            ('relevance_threshold', lambda p: filter_relevance_threshold(p, self.campaign_config)),
            ('opportunity_threshold', lambda p: filter_opportunity_threshold(p, self.campaign_config)),
            ('author_quality', filter_author_quality),
            ('author_risk', filter_author_risk),
            
            # Stage 4: Business
            ('already_engaged', filter_already_engaged),
            ('author_frequency', filter_author_frequency),
            ('competitor_content', filter_competitor_content),
            
            # Stage 5: Recency
            ('post_age', filter_post_age),
            ('conversation_staleness', filter_conversation_staleness),
            
            # Stage 6: Capacity (applied separately)
        ]
    
    def run(self, post: NormalizedPost) -> FilterPipelineResult:
        """Run post through filter pipeline."""
        
        start_time = time.time()
        results = []
        filters_passed = 0
        filters_failed = 0
        failed_at = None
        failed_reason = None
        
        for filter_name, filter_func in self.filters:
            try:
                result = filter_func(post)
                results.append(result)
                
                if result.passed:
                    filters_passed += 1
                else:
                    filters_failed += 1
                    if not failed_at:
                        failed_at = filter_name
                        failed_reason = result.reason
                    break  # Stop on first failure
            
            except Exception as e:
                log.error(f"Filter {filter_name} error: {e}")
                # On error, log and continue
                results.append(FilterResult(
                    passed=True,
                    filter_name=filter_name,
                    filter_stage=0,
                    reason=f'error: {str(e)}',
                    value=None,
                    threshold=None,
                ))
                filters_passed += 1
        
        duration_ms = (time.time() - start_time) * 1000
        
        return FilterPipelineResult(
            post_id=post.id,
            passed=(filters_failed == 0),
            filters_run=len(results),
            filters_passed=filters_passed,
            filters_failed=filters_failed,
            results=results,
            failed_at=failed_at,
            failed_reason=failed_reason,
            duration_ms=duration_ms,
            filtered_at=datetime.now(timezone.utc),
        )
```

### Batch Filtering

```python
async def filter_posts_batch(
    posts: List[NormalizedPost],
    campaign_config: dict
) -> Tuple[List[NormalizedPost], List[FilterPipelineResult]]:
    """Filter a batch of posts. Return passed posts and all results."""
    
    pipeline = FilterPipeline(campaign_config)
    
    passed_posts = []
    all_results = []
    
    for post in posts:
        result = pipeline.run(post)
        all_results.append(result)
        
        if result.passed:
            passed_posts.append(post)
        else:
            # Update post status
            mark_post_filtered(post.id, result)
    
    return passed_posts, all_results


def mark_post_filtered(post_id: UUID, result: FilterPipelineResult):
    """Mark post as filtered in database."""
    
    db.execute("""
        UPDATE discovered_posts
        SET 
            status = 'filtered',
            filtered_at = NOW(),
            filter_reason = %(reason)s,
            filter_data = %(filter_data)s,
            updated_at = NOW()
        WHERE id = %(post_id)s
    """, {
        'post_id': post_id,
        'reason': result.failed_at,
        'filter_data': json.dumps({
            'failed_at': result.failed_at,
            'failed_reason': result.failed_reason,
            'filters_run': result.filters_run,
            'filters_passed': result.filters_passed,
        }),
    })
```

## 7.7.9 Threshold Configuration

### Threshold Hierarchy

Thresholds can be configured at multiple levels:

1. **Global defaults:** System-wide defaults
2. **Campaign level:** Override for specific campaign
3. **Source level:** Override for specific source
4. **Dynamic adjustment:** ML-based threshold tuning

### Configuration Schema

```python
@dataclass
class FilterThresholds:
    # Quality thresholds
    min_content_length: int = 10
    min_content_words: int = 2
    target_languages: List[str] = field(default_factory=lambda: ['en'])
    
    # Score thresholds
    min_relevance_score: int = 40
    min_opportunity_score: int = 30
    min_combined_score: int = 50
    
    # Author thresholds
    min_author_quality_tier: str = 'poor'
    block_suspicious_authors: bool = True
    
    # Frequency thresholds
    min_hours_between_author_engagements: int = 24
    max_engagements_per_author_per_week: int = 3
    
    # Recency thresholds
    max_post_age_hours: int = 24
    max_hours_since_activity: int = 12
    
    # Capacity thresholds
    max_queue_size: int = 500
    max_daily_engagements: int = 50
    max_hourly_engagements: int = 10
    
    # Safety
    competitor_handling: str = 'review'  # block, review, allow


def get_thresholds_for_campaign(campaign_id: UUID) -> FilterThresholds:
    """Get effective thresholds for campaign."""
    
    # Start with defaults
    thresholds = FilterThresholds()
    
    # Load campaign overrides
    campaign_config = get_campaign_config(campaign_id)
    
    if campaign_config:
        for field_name in fields(thresholds):
            if field_name.name in campaign_config:
                setattr(thresholds, field_name.name, campaign_config[field_name.name])
    
    return thresholds
```

### Dynamic Threshold Adjustment

Automatically adjust thresholds based on performance.

```python
def analyze_filter_effectiveness(campaign_id: UUID, days: int = 7) -> dict:
    """Analyze how filters are performing."""
    
    stats = db.query("""
        SELECT 
            filter_reason,
            COUNT(*) as filtered_count,
            AVG((scores->'relevance'->>'total')::float) as avg_relevance,
            AVG((scores->'opportunity'->>'total')::float) as avg_opportunity
        FROM discovered_posts
        WHERE campaign_id = %(campaign_id)s
        AND status = 'filtered'
        AND filtered_at > NOW() - %(days)s * INTERVAL '1 day'
        GROUP BY filter_reason
        ORDER BY filtered_count DESC
    """, {'campaign_id': campaign_id, 'days': days})
    
    # Also get engaged posts for comparison
    engaged_stats = db.query_one("""
        SELECT 
            AVG((scores->'relevance'->>'total')::float) as avg_relevance,
            AVG((scores->'opportunity'->>'total')::float) as avg_opportunity,
            COUNT(*) as total_engaged
        FROM discovered_posts
        WHERE campaign_id = %(campaign_id)s
        AND status = 'engaged'
        AND engaged_at > NOW() - %(days)s * INTERVAL '1 day'
    """, {'campaign_id': campaign_id, 'days': days})
    
    return {
        'filter_stats': stats,
        'engaged_stats': engaged_stats,
        'recommendations': generate_threshold_recommendations(stats, engaged_stats),
    }


def generate_threshold_recommendations(filter_stats, engaged_stats) -> List[dict]:
    """Generate recommendations for threshold adjustments."""
    
    recommendations = []
    
    # Example: If relevance threshold is filtering posts with high opportunity
    for stat in filter_stats:
        if stat.filter_reason == 'relevance_below_threshold':
            if stat.avg_opportunity and stat.avg_opportunity > 50:
                recommendations.append({
                    'threshold': 'min_relevance_score',
                    'current': 40,
                    'recommended': 35,
                    'reason': f'Filtering {stat.filtered_count} posts with avg opportunity {stat.avg_opportunity:.0f}',
                })
    
    return recommendations
```

## 7.7.10 Filter Logging and Debugging

### Filter Decision Logging

Log all filter decisions for debugging and analytics.

```python
def log_filter_result(post_id: UUID, result: FilterPipelineResult):
    """Log filter pipeline result."""
    
    # Summary log
    if result.passed:
        log.info(f"Post {post_id} passed {result.filters_run} filters")
    else:
        log.info(f"Post {post_id} filtered by {result.failed_at}: {result.failed_reason}")
    
    # Detailed log for debugging
    if log.isEnabledFor(logging.DEBUG):
        for filter_result in result.results:
            log.debug(
                f"Filter {filter_result.filter_name}: "
                f"passed={filter_result.passed}, "
                f"value={filter_result.value}, "
                f"threshold={filter_result.threshold}"
            )
```

### Filter Analytics Table

```sql
CREATE TABLE filter_analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Reference
    post_id UUID NOT NULL REFERENCES discovered_posts(id),
    campaign_id UUID NOT NULL,
    
    -- Result
    passed BOOLEAN NOT NULL,
    filters_run INTEGER NOT NULL,
    filters_passed INTEGER NOT NULL,
    
    -- Failure details
    failed_at VARCHAR(100),
    failed_reason VARCHAR(200),
    
    -- Values at failure
    failed_value TEXT,
    failed_threshold TEXT,
    
    -- All results (for debugging)
    all_results JSONB,
    
    -- Performance
    duration_ms DECIMAL(10, 2),
    
    -- Timestamp
    filtered_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_filter_analytics_campaign ON filter_analytics(campaign_id, filtered_at);
CREATE INDEX idx_filter_analytics_reason ON filter_analytics(failed_at, failed_reason);
CREATE INDEX idx_filter_analytics_passed ON filter_analytics(passed, filtered_at);
```

### Debug Mode

Enable detailed filter debugging for specific posts or sources.

```python
class FilterPipeline:
    def __init__(self, campaign_config: dict, debug: bool = False):
        self.debug = debug
        # ...
    
    def run(self, post: NormalizedPost) -> FilterPipelineResult:
        if self.debug:
            return self._run_debug(post)
        return self._run_normal(post)
    
    def _run_debug(self, post: NormalizedPost) -> FilterPipelineResult:
        """Run with detailed debugging output."""
        
        print(f"\n{'='*60}")
        print(f"FILTER DEBUG: Post {post.id}")
        print(f"Content: {post.content_text[:100]}...")
        print(f"Author: @{post.author.handle}")
        print(f"{'='*60}\n")
        
        for filter_name, filter_func in self.filters:
            print(f"Running filter: {filter_name}")
            
            result = filter_func(post)
            
            print(f"  Passed: {result.passed}")
            print(f"  Value: {result.value}")
            print(f"  Threshold: {result.threshold}")
            print(f"  Reason: {result.reason}")
            print()
            
            if not result.passed:
                print(f"FILTERED by {filter_name}")
                break
        
        print(f"{'='*60}\n")
```

## 7.7.11 Monitoring and Metrics

### Filter Metrics

```python
# Filter pass/fail counts
filter_results_total = Counter(
    'filter_results_total',
    'Filter results',
    ['filter_name', 'result']  # result: passed, failed
)

# Filter failure reasons
filter_failures_by_reason = Counter(
    'filter_failures_total',
    'Filter failures by reason',
    ['filter_name', 'reason']
)

# Pipeline metrics
filter_pipeline_duration = Histogram(
    'filter_pipeline_duration_seconds',
    'Time to run filter pipeline',
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25]
)

# Overall pass rate
filter_pass_rate = Gauge(
    'filter_pass_rate',
    'Percentage of posts passing filters'
)

# Posts filtered per stage
filter_stage_rejections = Counter(
    'filter_stage_rejections_total',
    'Rejections by filter stage',
    ['stage']
)
```

### Dashboard Components

1. **Pass Rate:** Overall percentage passing filters
2. **Rejection Breakdown:** Pie chart by filter name
3. **Rejection Reasons:** Top reasons for filtering
4. **Stage Analysis:** Rejections per pipeline stage
5. **Threshold Impact:** Posts filtered at each threshold
6. **Trends:** Pass rate over time

### Alerting

```yaml
# Very high filter rate
- alert: FilterRateTooHigh
  expr: filter_pass_rate < 0.05
  for: 1h
  labels:
    severity: warning
  annotations:
    summary: "Less than 5% of posts passing filters"
    description: "Pass rate is {{ $value | humanizePercentage }}"

# Very low filter rate
- alert: FilterRateTooLow
  expr: filter_pass_rate > 0.80
  for: 1h
  labels:
    severity: warning
  annotations:
    summary: "Over 80% of posts passing filters"
    description: "Filters may be too permissive"

# Single filter rejecting too much
- alert: FilterRejectingTooMuch
  expr: rate(filter_failures_total[1h]) / rate(filter_results_total[1h]) > 0.5
  for: 30m
  labels:
    severity: warning
  annotations:
    summary: "Filter {{ $labels.filter_name }} rejecting >50%"
```

## 7.7.12 Implementation Guidance for Neoclaw

### Implementation Order

1. **Implement individual filters**
   - Start with simple filters (length, language)
   - Add blocklist filters
   - Add threshold filters
   - Add safety filters
   - Add business filters

2. **Build filter pipeline**
   - Ordered execution
   - Short-circuit on failure
   - Result aggregation

3. **Add configuration**
   - Threshold configuration
   - Campaign overrides
   - Dynamic loading

4. **Implement logging**
   - Filter result logging
   - Analytics table
   - Debug mode

5. **Add monitoring**
   - Metrics collection
   - Dashboard
   - Alerting

6. **Build threshold tuning**
   - Effectiveness analysis
   - Recommendation generation

### Testing Checklist

#### Unit Tests
- [ ] Each filter with passing input
- [ ] Each filter with failing input
- [ ] Edge cases (null values, empty strings)
- [ ] Threshold boundary cases

#### Integration Tests
- [ ] Full pipeline execution
- [ ] Batch filtering
- [ ] Database updates on filter

#### Validation Tests
- [ ] Known good posts pass
- [ ] Known bad posts fail
- [ ] Pass rate within expected range

### Common Pitfalls

**Filter order matters:**
Cheap filters first. Don't run expensive filters on obvious rejects.

**Missing null checks:**
Posts may have missing data. Handle gracefully.

**Over-filtering:**
Too aggressive filters = no engagement opportunities. Monitor pass rates.

**Under-filtering:**
Too permissive filters = low-quality queue. Monitor engagement success.

**Threshold drift:**
Optimal thresholds change over time. Analyze and adjust regularly.

**Silent failures:**
Filter errors that pass posts through. Log all errors.

---

**END OF SECTION 7.7**

Section 7.8 continues with Prioritization & Queue Management specification.
-e 


# SECTION 7.8: PRIORITIZATION & QUEUE MANAGEMENT

## 7.8.1 What Prioritization Is

### The Core Concept

Prioritization is the process of ranking posts that have passed filtering to determine engagement order. The queue holds all engagement candidates, ordered by priority score.

**Input:** Filtered posts from Section 7.7
**Output:** Ordered queue of posts ready for engagement

Prioritization answers the question: "Given limited capacity, which posts should we engage with first?"

### Why Prioritization Matters

**Capacity constraints:**
Jen can only engage with a limited number of posts per day. Prioritization ensures the best opportunities get attention.

**Time sensitivity:**
Fresh posts and active conversations lose value over time. Prioritization ensures timely engagement.

**Goal alignment:**
Different posts serve different campaign goals. Prioritization focuses on goal-aligned opportunities.

**Resource optimization:**
Human review time is limited. Priority ordering ensures reviewers see the best opportunities first.

### Prioritization vs Filtering

**Filtering:** Binary — in or out. Sets minimum quality bar.
**Prioritization:** Continuous — ranking from best to worst. Optimizes selection order.

All posts in the queue passed filtering. Prioritization determines which get engaged first.

## 7.8.2 Priority Score Calculation

### Priority Score Formula

The priority score combines multiple factors:

```
priority_score = base_score × goal_multiplier × author_factor × time_factor × boost_factor
```

Where:
- **base_score:** Combination of relevance and opportunity scores
- **goal_multiplier:** From classification × campaign goal alignment
- **author_factor:** From author evaluation (0.5 - 1.5)
- **time_factor:** Decay based on post age (0.5 - 1.5)
- **boost_factor:** Manual or rule-based boosts (0.5 - 2.0)

### Base Score Calculation

```python
def calculate_base_score(
    relevance_score: int,
    opportunity_score: int,
    relevance_weight: float = 0.4,
    opportunity_weight: float = 0.6
) -> float:
    """Calculate base priority score from relevance and opportunity."""
    
    # Weighted combination
    base = (relevance_score * relevance_weight) + (opportunity_score * opportunity_weight)
    
    # Bonus for high scores in both dimensions
    if relevance_score >= 70 and opportunity_score >= 70:
        base *= 1.1  # 10% bonus for dual high scores
    
    return base
```

**Weight rationale:**
- Opportunity weighted higher (0.6) because engagement value matters more than topic match
- Relevance still important (0.4) to ensure on-brand engagement

### Goal Multiplier

From classification, apply campaign goal alignment:

```python
def get_goal_multiplier(
    classification: dict,
    campaign_goal: str
) -> float:
    """Get goal alignment multiplier."""
    
    multipliers = classification.get('goal_multipliers', {})
    return multipliers.get(campaign_goal, 1.0)
```

**Example multipliers (from Section 7.3):**
- help_seeking_solution × conversions = 1.50
- tech_discussion × thought_leadership = 1.35
- meme_humor × brand_awareness = 1.40

### Author Factor

From author evaluation:

```python
def get_author_factor(author_evaluation: dict) -> float:
    """Get author factor for priority calculation."""
    
    if not author_evaluation:
        return 1.0
    
    # Author factor ranges 0.5 - 1.5
    return author_evaluation.get('author_factor', 1.0)
```

**Factor ranges:**
- 0.5: Low-quality or risky author
- 1.0: Average author
- 1.5: High-value author (influencer, target customer)

### Time Factor (Decay)

Posts lose priority over time:

```python
def calculate_time_factor(
    created_at: datetime,
    platform: str
) -> float:
    """Calculate time-based priority factor."""
    
    now = datetime.now(timezone.utc)
    age_hours = (now - created_at).total_seconds() / 3600
    
    # Platform-specific decay rates
    half_life_hours = {
        'twitter': 4,      # Fast decay
        'linkedin': 12,    # Slower decay
        'reddit': 8,       # Medium decay
    }.get(platform, 6)
    
    # Exponential decay
    # At half-life, factor = 0.5
    # At 0 hours, factor = 1.0
    decay = 0.5 ** (age_hours / half_life_hours)
    
    # Clamp to range [0.3, 1.2]
    # Fresh posts get slight boost (1.2)
    # Very old posts floor at 0.3
    
    if age_hours < 1:
        return 1.2  # Fresh boost
    elif age_hours < 2:
        return 1.1
    else:
        return max(0.3, min(1.0, decay))
```

### Boost Factor

Manual or rule-based priority adjustments:

```python
def calculate_boost_factor(post: NormalizedPost, rules: List[BoostRule]) -> float:
    """Calculate boost factor from rules."""
    
    boost = 1.0
    
    for rule in rules:
        if rule.matches(post):
            boost *= rule.boost_multiplier
    
    # Clamp to reasonable range
    return max(0.5, min(2.0, boost))


@dataclass
class BoostRule:
    name: str
    condition: Callable[[NormalizedPost], bool]
    boost_multiplier: float


# Example rules
BOOST_RULES = [
    BoostRule(
        name='mention_boost',
        condition=lambda p: p.source_type == 'mention',
        boost_multiplier=1.5
    ),
    BoostRule(
        name='vip_author_boost',
        condition=lambda p: p.author.handle in VIP_HANDLES,
        boost_multiplier=1.3
    ),
    BoostRule(
        name='question_boost',
        condition=lambda p: p.classification.get('primary') == 'help_seeking_solution',
        boost_multiplier=1.2
    ),
    BoostRule(
        name='high_engagement_boost',
        condition=lambda p: p.engagement.likes > 100,
        boost_multiplier=1.1
    ),
]
```

### Complete Priority Score

```python
@dataclass
class PriorityScoreResult:
    priority_score: float
    
    base_score: float
    goal_multiplier: float
    author_factor: float
    time_factor: float
    boost_factor: float
    
    applied_boosts: List[str]
    calculated_at: datetime


def calculate_priority_score(
    post: NormalizedPost,
    campaign_goal: str,
    boost_rules: List[BoostRule] = None
) -> PriorityScoreResult:
    """Calculate complete priority score."""
    
    boost_rules = boost_rules or BOOST_RULES
    
    # Get component scores
    relevance = post.scores.get('relevance', {}).get('total', 0)
    opportunity = post.scores.get('opportunity', {}).get('total', 0)
    
    base_score = calculate_base_score(relevance, opportunity)
    goal_multiplier = get_goal_multiplier(post.classification, campaign_goal)
    author_factor = get_author_factor(post.author_evaluation)
    time_factor = calculate_time_factor(post.created_at, post.platform)
    
    # Calculate boost
    boost_factor = 1.0
    applied_boosts = []
    for rule in boost_rules:
        if rule.matches(post):
            boost_factor *= rule.boost_multiplier
            applied_boosts.append(rule.name)
    boost_factor = max(0.5, min(2.0, boost_factor))
    
    # Final calculation
    priority_score = (
        base_score *
        goal_multiplier *
        author_factor *
        time_factor *
        boost_factor
    )
    
    return PriorityScoreResult(
        priority_score=priority_score,
        base_score=base_score,
        goal_multiplier=goal_multiplier,
        author_factor=author_factor,
        time_factor=time_factor,
        boost_factor=boost_factor,
        applied_boosts=applied_boosts,
        calculated_at=datetime.now(timezone.utc),
    )
```

## 7.8.3 Queue Data Structure

### Queue Entry Structure

```python
@dataclass
class QueueEntry:
    # Identity
    id: UUID
    post_id: UUID
    campaign_id: UUID
    
    # Priority
    priority_score: float
    priority_components: PriorityScoreResult
    
    # Post summary (denormalized for quick access)
    platform: str
    author_handle: str
    content_preview: str  # First 100 chars
    classification: str
    
    # Scores (denormalized)
    relevance_score: int
    opportunity_score: int
    author_score: int
    
    # Timing
    post_created_at: datetime
    queued_at: datetime
    expires_at: datetime
    
    # State
    status: str  # pending, processing, completed, expired, removed
    
    # Processing info
    assigned_to: Optional[UUID]  # Worker or reviewer
    assigned_at: Optional[datetime]
    processed_at: Optional[datetime]
    
    # Flags
    requires_review: bool
    review_reasons: List[str]
```

### Database Schema

```sql
CREATE TABLE engagement_queue (
    -- Identity
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    post_id UUID NOT NULL REFERENCES discovered_posts(id),
    campaign_id UUID NOT NULL REFERENCES campaigns(id),
    
    -- Priority
    priority_score DECIMAL(10, 4) NOT NULL,
    priority_components JSONB NOT NULL,
    
    -- Denormalized post data
    platform VARCHAR(50) NOT NULL,
    author_handle VARCHAR(255),
    content_preview VARCHAR(200),
    classification VARCHAR(50),
    
    -- Scores
    relevance_score INTEGER NOT NULL,
    opportunity_score INTEGER NOT NULL,
    author_score INTEGER,
    
    -- Timing
    post_created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    queued_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    
    -- State
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    
    -- Processing
    assigned_to UUID,
    assigned_at TIMESTAMP WITH TIME ZONE,
    processed_at TIMESTAMP WITH TIME ZONE,
    
    -- Flags
    requires_review BOOLEAN NOT NULL DEFAULT false,
    review_reasons JSONB DEFAULT '[]',
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT queue_post_unique UNIQUE (post_id, campaign_id)
);

-- Indexes for queue operations
CREATE INDEX idx_queue_campaign_priority ON engagement_queue(campaign_id, priority_score DESC) 
    WHERE status = 'pending';
CREATE INDEX idx_queue_campaign_status ON engagement_queue(campaign_id, status);
CREATE INDEX idx_queue_expires ON engagement_queue(expires_at) 
    WHERE status = 'pending';
CREATE INDEX idx_queue_assigned ON engagement_queue(assigned_to) 
    WHERE status = 'processing';
CREATE INDEX idx_queue_requires_review ON engagement_queue(requires_review, priority_score DESC) 
    WHERE status = 'pending' AND requires_review = true;
```

### Queue Properties

**Ordered:** Entries sorted by priority_score descending
**Capacity-limited:** Maximum entries per campaign
**TTL-based:** Entries expire after configured time
**Partitioned:** Separate queues per campaign

## 7.8.4 Queue Operations

### Adding to Queue

```python
def add_to_queue(
    post: NormalizedPost,
    campaign_id: UUID,
    priority_result: PriorityScoreResult
) -> QueueEntry:
    """Add post to engagement queue."""
    
    # Check if already in queue
    existing = db.query_one("""
        SELECT id FROM engagement_queue
        WHERE post_id = %(post_id)s AND campaign_id = %(campaign_id)s
    """, {'post_id': post.id, 'campaign_id': campaign_id})
    
    if existing:
        # Update priority if changed significantly
        update_queue_priority(existing.id, priority_result)
        return get_queue_entry(existing.id)
    
    # Calculate expiration
    expires_at = calculate_queue_expiration(post)
    
    # Determine if requires review
    requires_review, review_reasons = check_requires_review(post)
    
    # Create entry
    entry = QueueEntry(
        id=uuid4(),
        post_id=post.id,
        campaign_id=campaign_id,
        priority_score=priority_result.priority_score,
        priority_components=priority_result,
        platform=post.platform,
        author_handle=post.author.handle,
        content_preview=post.content_text[:200],
        classification=post.classification.get('primary') if post.classification else None,
        relevance_score=post.scores.get('relevance', {}).get('total', 0),
        opportunity_score=post.scores.get('opportunity', {}).get('total', 0),
        author_score=post.author_evaluation.get('author_score') if post.author_evaluation else None,
        post_created_at=post.created_at,
        queued_at=datetime.now(timezone.utc),
        expires_at=expires_at,
        status='pending',
        requires_review=requires_review,
        review_reasons=review_reasons,
    )
    
    # Insert
    db.execute("""
        INSERT INTO engagement_queue (
            id, post_id, campaign_id, priority_score, priority_components,
            platform, author_handle, content_preview, classification,
            relevance_score, opportunity_score, author_score,
            post_created_at, queued_at, expires_at, status,
            requires_review, review_reasons
        ) VALUES (
            %(id)s, %(post_id)s, %(campaign_id)s, %(priority_score)s, %(priority_components)s,
            %(platform)s, %(author_handle)s, %(content_preview)s, %(classification)s,
            %(relevance_score)s, %(opportunity_score)s, %(author_score)s,
            %(post_created_at)s, %(queued_at)s, %(expires_at)s, %(status)s,
            %(requires_review)s, %(review_reasons)s
        )
    """, entry.__dict__)
    
    # Handle capacity overflow
    handle_queue_overflow(campaign_id)
    
    return entry
```

### Fetching from Queue

```python
def fetch_next_from_queue(
    campaign_id: UUID,
    worker_id: UUID,
    count: int = 1,
    require_review: Optional[bool] = None
) -> List[QueueEntry]:
    """Fetch next entries from queue for processing."""
    
    # Build query
    conditions = ["status = 'pending'", "campaign_id = %(campaign_id)s"]
    
    if require_review is not None:
        conditions.append(f"requires_review = {require_review}")
    
    query = f"""
        UPDATE engagement_queue
        SET 
            status = 'processing',
            assigned_to = %(worker_id)s,
            assigned_at = NOW(),
            updated_at = NOW()
        WHERE id IN (
            SELECT id FROM engagement_queue
            WHERE {' AND '.join(conditions)}
            AND expires_at > NOW()
            ORDER BY priority_score DESC
            LIMIT %(count)s
            FOR UPDATE SKIP LOCKED
        )
        RETURNING *
    """
    
    entries = db.query(query, {
        'campaign_id': campaign_id,
        'worker_id': worker_id,
        'count': count,
    })
    
    return [QueueEntry(**e) for e in entries]
```

### Completing Queue Entry

```python
def complete_queue_entry(
    entry_id: UUID,
    engagement_id: UUID,
    outcome: str  # 'engaged', 'skipped', 'failed'
):
    """Mark queue entry as completed."""
    
    db.execute("""
        UPDATE engagement_queue
        SET 
            status = 'completed',
            processed_at = NOW(),
            updated_at = NOW()
        WHERE id = %(entry_id)s
    """, {'entry_id': entry_id})
    
    # Update post status
    entry = get_queue_entry(entry_id)
    if outcome == 'engaged':
        db.execute("""
            UPDATE discovered_posts
            SET status = 'engaged', engagement_id = %(engagement_id)s, updated_at = NOW()
            WHERE id = %(post_id)s
        """, {'post_id': entry.post_id, 'engagement_id': engagement_id})
```

### Returning to Queue

```python
def return_to_queue(entry_id: UUID, reason: str):
    """Return entry to queue (e.g., worker failed, needs different handling)."""
    
    db.execute("""
        UPDATE engagement_queue
        SET 
            status = 'pending',
            assigned_to = NULL,
            assigned_at = NULL,
            updated_at = NOW()
        WHERE id = %(entry_id)s
    """, {'entry_id': entry_id})
    
    log.info(f"Entry {entry_id} returned to queue: {reason}")
```

### Removing from Queue

```python
def remove_from_queue(entry_id: UUID, reason: str):
    """Remove entry from queue."""
    
    db.execute("""
        UPDATE engagement_queue
        SET 
            status = 'removed',
            processed_at = NOW(),
            updated_at = NOW()
        WHERE id = %(entry_id)s
    """, {'entry_id': entry_id})
    
    # Update post status
    entry = get_queue_entry(entry_id)
    db.execute("""
        UPDATE discovered_posts
        SET status = 'removed', filter_reason = %(reason)s, updated_at = NOW()
        WHERE id = %(post_id)s
    """, {'post_id': entry.post_id, 'reason': reason})
```

## 7.8.5 Queue Capacity Management

### Capacity Limits

```python
MAX_QUEUE_SIZE_PER_CAMPAIGN = 500
MAX_QUEUE_SIZE_PER_PLATFORM = 200  # Per platform within campaign
OVERFLOW_EVICTION_COUNT = 50  # How many to evict when at capacity
```

### Overflow Handling

```python
def handle_queue_overflow(campaign_id: UUID):
    """Handle queue capacity overflow."""
    
    current_size = get_queue_size(campaign_id)
    
    if current_size <= MAX_QUEUE_SIZE_PER_CAMPAIGN:
        return  # No overflow
    
    overflow_count = current_size - MAX_QUEUE_SIZE_PER_CAMPAIGN + OVERFLOW_EVICTION_COUNT
    
    # Evict lowest priority entries
    evicted = db.execute("""
        UPDATE engagement_queue
        SET status = 'removed', processed_at = NOW(), updated_at = NOW()
        WHERE id IN (
            SELECT id FROM engagement_queue
            WHERE campaign_id = %(campaign_id)s
            AND status = 'pending'
            ORDER BY priority_score ASC
            LIMIT %(count)s
        )
        RETURNING id
    """, {'campaign_id': campaign_id, 'count': overflow_count})
    
    log.info(f"Evicted {len(evicted)} entries from queue for campaign {campaign_id}")
    
    # Metrics
    queue_evictions_total.inc(len(evicted))


def get_queue_size(campaign_id: UUID) -> int:
    """Get current queue size for campaign."""
    
    return db.query_scalar("""
        SELECT COUNT(*) FROM engagement_queue
        WHERE campaign_id = %(campaign_id)s
        AND status = 'pending'
    """, {'campaign_id': campaign_id})
```

### Platform Balancing

Ensure queue isn't dominated by a single platform:

```python
def check_platform_balance(campaign_id: UUID) -> dict:
    """Check platform distribution in queue."""
    
    distribution = db.query("""
        SELECT platform, COUNT(*) as count
        FROM engagement_queue
        WHERE campaign_id = %(campaign_id)s
        AND status = 'pending'
        GROUP BY platform
    """, {'campaign_id': campaign_id})
    
    return {row.platform: row.count for row in distribution}


def enforce_platform_limits(campaign_id: UUID, platform: str):
    """Enforce per-platform queue limits."""
    
    platform_count = db.query_scalar("""
        SELECT COUNT(*) FROM engagement_queue
        WHERE campaign_id = %(campaign_id)s
        AND platform = %(platform)s
        AND status = 'pending'
    """, {'campaign_id': campaign_id, 'platform': platform})
    
    if platform_count > MAX_QUEUE_SIZE_PER_PLATFORM:
        excess = platform_count - MAX_QUEUE_SIZE_PER_PLATFORM
        
        # Evict lowest priority for this platform
        db.execute("""
            UPDATE engagement_queue
            SET status = 'removed', processed_at = NOW()
            WHERE id IN (
                SELECT id FROM engagement_queue
                WHERE campaign_id = %(campaign_id)s
                AND platform = %(platform)s
                AND status = 'pending'
                ORDER BY priority_score ASC
                LIMIT %(excess)s
            )
        """, {'campaign_id': campaign_id, 'platform': platform, 'excess': excess})
```

## 7.8.6 Queue Expiration

### Expiration Handling

```python
def expire_old_entries():
    """Expire queue entries past their TTL."""
    
    expired = db.execute("""
        UPDATE engagement_queue
        SET status = 'expired', processed_at = NOW(), updated_at = NOW()
        WHERE status = 'pending'
        AND expires_at < NOW()
        RETURNING id, campaign_id
    """)
    
    if expired:
        log.info(f"Expired {len(expired)} queue entries")
        
        # Update post statuses
        for entry in expired:
            db.execute("""
                UPDATE discovered_posts
                SET status = 'expired', updated_at = NOW()
                WHERE id = (
                    SELECT post_id FROM engagement_queue WHERE id = %(entry_id)s
                )
            """, {'entry_id': entry.id})
    
    return len(expired)
```

### Scheduled Expiration Job

```python
async def queue_expiration_worker():
    """Worker that periodically expires old entries."""
    
    while True:
        try:
            expired_count = expire_old_entries()
            
            if expired_count > 0:
                queue_expirations_total.inc(expired_count)
        
        except Exception as e:
            log.error(f"Error in expiration worker: {e}")
        
        await asyncio.sleep(60)  # Run every minute
```

### Stale Processing Recovery

Recover entries stuck in "processing" state:

```python
PROCESSING_TIMEOUT_MINUTES = 30

def recover_stale_processing():
    """Return entries stuck in processing back to pending."""
    
    stale_cutoff = datetime.now(timezone.utc) - timedelta(minutes=PROCESSING_TIMEOUT_MINUTES)
    
    recovered = db.execute("""
        UPDATE engagement_queue
        SET 
            status = 'pending',
            assigned_to = NULL,
            assigned_at = NULL,
            updated_at = NOW()
        WHERE status = 'processing'
        AND assigned_at < %(cutoff)s
        RETURNING id
    """, {'cutoff': stale_cutoff})
    
    if recovered:
        log.warning(f"Recovered {len(recovered)} stale processing entries")
    
    return len(recovered)
```

## 7.8.7 Priority Updates

### Recalculating Priority

Priority scores change over time (time decay). Periodically recalculate:

```python
def recalculate_queue_priorities(campaign_id: UUID):
    """Recalculate priority scores for pending entries."""
    
    entries = db.query("""
        SELECT eq.id, eq.post_id, dp.*
        FROM engagement_queue eq
        JOIN discovered_posts dp ON dp.id = eq.post_id
        WHERE eq.campaign_id = %(campaign_id)s
        AND eq.status = 'pending'
    """, {'campaign_id': campaign_id})
    
    campaign = get_campaign(campaign_id)
    
    for entry in entries:
        post = NormalizedPost(**entry)
        new_priority = calculate_priority_score(post, campaign.primary_goal)
        
        db.execute("""
            UPDATE engagement_queue
            SET 
                priority_score = %(priority)s,
                priority_components = %(components)s,
                updated_at = NOW()
            WHERE id = %(entry_id)s
        """, {
            'entry_id': entry.id,
            'priority': new_priority.priority_score,
            'components': json.dumps(asdict(new_priority)),
        })


async def priority_refresh_worker():
    """Periodically refresh priority scores."""
    
    while True:
        campaigns = get_active_campaigns()
        
        for campaign in campaigns:
            try:
                recalculate_queue_priorities(campaign.id)
            except Exception as e:
                log.error(f"Error refreshing priorities for {campaign.id}: {e}")
        
        await asyncio.sleep(300)  # Every 5 minutes
```

### Priority Boosting

Manually boost priority for specific posts:

```python
def boost_entry_priority(entry_id: UUID, boost_multiplier: float, reason: str):
    """Manually boost an entry's priority."""
    
    entry = get_queue_entry(entry_id)
    new_priority = entry.priority_score * boost_multiplier
    
    # Update components
    components = entry.priority_components
    components['manual_boost'] = boost_multiplier
    components['boost_reason'] = reason
    
    db.execute("""
        UPDATE engagement_queue
        SET 
            priority_score = %(priority)s,
            priority_components = %(components)s,
            updated_at = NOW()
        WHERE id = %(entry_id)s
    """, {
        'entry_id': entry_id,
        'priority': new_priority,
        'components': json.dumps(components),
    })
    
    log.info(f"Boosted entry {entry_id} priority by {boost_multiplier}x: {reason}")
```

## 7.8.8 Queue Partitioning

### Partition Strategies

**By campaign:** Each campaign has its own queue (default)
**By platform:** Separate queues per platform
**By priority tier:** High/medium/low priority buckets
**By review status:** Separate queue for items needing review

### Priority Tiers

```python
PRIORITY_TIERS = {
    'critical': {'min_score': 90, 'max_wait_minutes': 15},
    'high': {'min_score': 70, 'max_wait_minutes': 60},
    'medium': {'min_score': 50, 'max_wait_minutes': 180},
    'low': {'min_score': 0, 'max_wait_minutes': 360},
}

def get_priority_tier(priority_score: float) -> str:
    """Determine priority tier for score."""
    
    if priority_score >= 90:
        return 'critical'
    elif priority_score >= 70:
        return 'high'
    elif priority_score >= 50:
        return 'medium'
    else:
        return 'low'
```

### Review Queue

Separate queue for items requiring human review:

```python
def fetch_for_review(
    campaign_id: UUID,
    reviewer_id: UUID,
    count: int = 10
) -> List[QueueEntry]:
    """Fetch entries requiring review."""
    
    return db.query("""
        UPDATE engagement_queue
        SET 
            status = 'reviewing',
            assigned_to = %(reviewer_id)s,
            assigned_at = NOW()
        WHERE id IN (
            SELECT id FROM engagement_queue
            WHERE campaign_id = %(campaign_id)s
            AND status = 'pending'
            AND requires_review = true
            ORDER BY priority_score DESC
            LIMIT %(count)s
            FOR UPDATE SKIP LOCKED
        )
        RETURNING *
    """, {
        'campaign_id': campaign_id,
        'reviewer_id': reviewer_id,
        'count': count,
    })


def complete_review(
    entry_id: UUID,
    approved: bool,
    reviewer_notes: str = None
):
    """Complete review of an entry."""
    
    if approved:
        db.execute("""
            UPDATE engagement_queue
            SET 
                status = 'pending',
                requires_review = false,
                assigned_to = NULL,
                assigned_at = NULL,
                updated_at = NOW()
            WHERE id = %(entry_id)s
        """, {'entry_id': entry_id})
    else:
        remove_from_queue(entry_id, f'rejected_in_review: {reviewer_notes}')
```

## 7.8.9 Queue Analytics

### Queue Statistics

```python
@dataclass
class QueueStats:
    campaign_id: UUID
    
    total_pending: int
    total_processing: int
    total_completed_today: int
    total_expired_today: int
    
    avg_priority_score: float
    avg_wait_time_minutes: float
    avg_processing_time_minutes: float
    
    by_platform: Dict[str, int]
    by_classification: Dict[str, int]
    by_priority_tier: Dict[str, int]
    
    oldest_entry_age_minutes: float
    queue_throughput_per_hour: float


def get_queue_stats(campaign_id: UUID) -> QueueStats:
    """Get comprehensive queue statistics."""
    
    # Basic counts
    pending = db.query_scalar("""
        SELECT COUNT(*) FROM engagement_queue
        WHERE campaign_id = %(id)s AND status = 'pending'
    """, {'id': campaign_id})
    
    processing = db.query_scalar("""
        SELECT COUNT(*) FROM engagement_queue
        WHERE campaign_id = %(id)s AND status = 'processing'
    """, {'id': campaign_id})
    
    completed_today = db.query_scalar("""
        SELECT COUNT(*) FROM engagement_queue
        WHERE campaign_id = %(id)s 
        AND status = 'completed'
        AND processed_at > DATE_TRUNC('day', NOW())
    """, {'id': campaign_id})
    
    # Averages
    avg_priority = db.query_scalar("""
        SELECT AVG(priority_score) FROM engagement_queue
        WHERE campaign_id = %(id)s AND status = 'pending'
    """, {'id': campaign_id}) or 0
    
    # Wait time (time from queued to processed)
    avg_wait = db.query_scalar("""
        SELECT AVG(EXTRACT(EPOCH FROM (processed_at - queued_at)) / 60)
        FROM engagement_queue
        WHERE campaign_id = %(id)s 
        AND status = 'completed'
        AND processed_at > NOW() - INTERVAL '24 hours'
    """, {'id': campaign_id}) or 0
    
    # Platform distribution
    platform_dist = db.query("""
        SELECT platform, COUNT(*) as count
        FROM engagement_queue
        WHERE campaign_id = %(id)s AND status = 'pending'
        GROUP BY platform
    """, {'id': campaign_id})
    
    # Classification distribution
    class_dist = db.query("""
        SELECT classification, COUNT(*) as count
        FROM engagement_queue
        WHERE campaign_id = %(id)s AND status = 'pending'
        GROUP BY classification
    """, {'id': campaign_id})
    
    # Throughput
    hourly_completed = db.query_scalar("""
        SELECT COUNT(*) FROM engagement_queue
        WHERE campaign_id = %(id)s
        AND status = 'completed'
        AND processed_at > NOW() - INTERVAL '1 hour'
    """, {'id': campaign_id}) or 0
    
    return QueueStats(
        campaign_id=campaign_id,
        total_pending=pending,
        total_processing=processing,
        total_completed_today=completed_today,
        total_expired_today=0,  # Would calculate similarly
        avg_priority_score=avg_priority,
        avg_wait_time_minutes=avg_wait,
        avg_processing_time_minutes=0,  # Would calculate
        by_platform={p.platform: p.count for p in platform_dist},
        by_classification={c.classification: c.count for c in class_dist},
        by_priority_tier={},  # Would calculate
        oldest_entry_age_minutes=0,  # Would calculate
        queue_throughput_per_hour=hourly_completed,
    )
```

### Queue Health Checks

```python
def check_queue_health(campaign_id: UUID) -> dict:
    """Check queue health indicators."""
    
    stats = get_queue_stats(campaign_id)
    
    issues = []
    
    # Queue too empty
    if stats.total_pending < 10:
        issues.append({
            'severity': 'warning',
            'issue': 'queue_low',
            'message': f'Only {stats.total_pending} entries in queue'
        })
    
    # Queue too full
    if stats.total_pending > MAX_QUEUE_SIZE_PER_CAMPAIGN * 0.9:
        issues.append({
            'severity': 'warning',
            'issue': 'queue_near_capacity',
            'message': f'Queue at {stats.total_pending}/{MAX_QUEUE_SIZE_PER_CAMPAIGN}'
        })
    
    # High wait times
    if stats.avg_wait_time_minutes > 120:
        issues.append({
            'severity': 'warning',
            'issue': 'high_wait_time',
            'message': f'Average wait time {stats.avg_wait_time_minutes:.0f} minutes'
        })
    
    # Low throughput
    if stats.queue_throughput_per_hour < 2:
        issues.append({
            'severity': 'info',
            'issue': 'low_throughput',
            'message': f'Only {stats.queue_throughput_per_hour} processed per hour'
        })
    
    # Stuck processing
    stuck = db.query_scalar("""
        SELECT COUNT(*) FROM engagement_queue
        WHERE campaign_id = %(id)s
        AND status = 'processing'
        AND assigned_at < NOW() - INTERVAL '30 minutes'
    """, {'id': campaign_id})
    
    if stuck > 0:
        issues.append({
            'severity': 'error',
            'issue': 'stuck_processing',
            'message': f'{stuck} entries stuck in processing'
        })
    
    return {
        'healthy': len([i for i in issues if i['severity'] == 'error']) == 0,
        'issues': issues,
        'stats': stats,
    }
```

## 7.8.10 Queue API

### Queue Management Endpoints

```python
@app.get("/api/v1/campaigns/{campaign_id}/queue")
async def get_queue(campaign_id: UUID, limit: int = 50, offset: int = 0):
    """Get queue entries for campaign."""
    
    entries = db.query("""
        SELECT * FROM engagement_queue
        WHERE campaign_id = %(campaign_id)s
        AND status = 'pending'
        ORDER BY priority_score DESC
        LIMIT %(limit)s OFFSET %(offset)s
    """, {'campaign_id': campaign_id, 'limit': limit, 'offset': offset})
    
    return {
        'entries': [QueueEntry(**e).__dict__ for e in entries],
        'total': get_queue_size(campaign_id),
    }


@app.get("/api/v1/campaigns/{campaign_id}/queue/stats")
async def get_queue_statistics(campaign_id: UUID):
    """Get queue statistics."""
    
    return get_queue_stats(campaign_id).__dict__


@app.post("/api/v1/queue/{entry_id}/boost")
async def boost_entry(entry_id: UUID, boost: float, reason: str):
    """Boost entry priority."""
    
    boost_entry_priority(entry_id, boost, reason)
    return {'success': True}


@app.post("/api/v1/queue/{entry_id}/remove")
async def remove_entry(entry_id: UUID, reason: str):
    """Remove entry from queue."""
    
    remove_from_queue(entry_id, reason)
    return {'success': True}


@app.get("/api/v1/campaigns/{campaign_id}/queue/health")
async def check_health(campaign_id: UUID):
    """Check queue health."""
    
    return check_queue_health(campaign_id)
```

## 7.8.11 Monitoring and Metrics

### Queue Metrics

```python
# Queue size
queue_size = Gauge(
    'queue_size',
    'Current queue size',
    ['campaign_id', 'status']
)

# Priority distribution
queue_priority_histogram = Histogram(
    'queue_priority_score',
    'Distribution of priority scores',
    ['campaign_id'],
    buckets=[10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
)

# Wait time
queue_wait_time = Histogram(
    'queue_wait_time_seconds',
    'Time from queue to processing',
    ['campaign_id'],
    buckets=[60, 300, 600, 1800, 3600, 7200, 14400]
)

# Throughput
queue_throughput = Counter(
    'queue_processed_total',
    'Total entries processed',
    ['campaign_id', 'outcome']  # engaged, skipped, expired
)

# Evictions
queue_evictions = Counter(
    'queue_evictions_total',
    'Entries evicted from queue',
    ['campaign_id', 'reason']
)
```

### Dashboard Components

1. **Queue Depth:** Current size over time
2. **Throughput:** Processing rate
3. **Wait Time Distribution:** How long entries wait
4. **Priority Distribution:** Score histogram
5. **Platform Breakdown:** Entries by platform
6. **Health Status:** Current health indicators
7. **Expiration Rate:** How many expire vs get processed

## 7.8.12 Implementation Guidance for Neoclaw

### Implementation Order

1. **Define data structures**
   - QueueEntry dataclass
   - Database schema

2. **Build priority calculation**
   - Base score
   - All multipliers
   - Boost rules

3. **Implement queue operations**
   - Add to queue
   - Fetch from queue
   - Complete/remove

4. **Add capacity management**
   - Overflow handling
   - Platform balancing
   - Expiration

5. **Build priority updates**
   - Recalculation
   - Manual boosting

6. **Add analytics**
   - Statistics
   - Health checks

7. **Implement API**
   - Management endpoints

8. **Add monitoring**
   - Metrics
   - Dashboard

### Testing Checklist

#### Unit Tests
- [ ] Priority score calculation
- [ ] All multiplier functions
- [ ] Boost rule matching
- [ ] Time decay calculation

#### Integration Tests
- [ ] Queue add/fetch/complete cycle
- [ ] Capacity overflow handling
- [ ] Expiration processing
- [ ] Priority recalculation

#### Load Tests
- [ ] High-volume queue operations
- [ ] Concurrent fetch handling
- [ ] Priority sort performance

### Common Pitfalls

**Lock contention:**
Multiple workers fetching causes contention. Use SKIP LOCKED.

**Priority staleness:**
Scores decay but aren't recalculated. Refresh regularly.

**Capacity spikes:**
Sudden influx can overflow queue. Handle gracefully.

**Expiration lag:**
If expiration job fails, stale entries accumulate. Monitor closely.

**Unbalanced platforms:**
One platform can dominate queue. Enforce limits.

---

**END OF SECTION 7.8**

Section 7.9 continues with Platform-Specific Discovery specification.
-e 


# SECTION 7.9: PLATFORM-SPECIFIC DISCOVERY

## 7.9.1 Why Platform-Specific Handling Matters

### The Core Challenge

Each social media platform has unique characteristics that affect content discovery:

- **Different APIs:** Authentication, endpoints, rate limits, data formats
- **Different content types:** Tweet vs post vs submission vs message
- **Different engagement patterns:** Retweets vs shares vs upvotes
- **Different conversation structures:** Threads vs comments vs replies
- **Different timing:** Content lifespan varies dramatically
- **Different audiences:** Professional vs general vs technical

Effective discovery requires understanding and adapting to each platform's characteristics.

### Platform-Agnostic vs Platform-Specific

The discovery pipeline is mostly platform-agnostic:
- Classification works the same
- Scoring formulas are consistent
- Filtering logic is shared
- Queue management is unified

But certain components must be platform-aware:
- API integration (Section 7.2)
- Source configuration (Section 7.1)
- Timing calculations
- Engagement metrics normalization
- Content structure parsing

This section details platform-specific considerations for each supported platform.

## 7.9.2 Twitter/X Platform Details

### Platform Characteristics

| Aspect | Value | Implications |
|--------|-------|--------------|
| Content type | Tweets (280 chars), threads | Short-form, often incomplete thoughts |
| Lifespan | 4-24 hours typical | Fast decay, need quick response |
| Engagement types | Like, retweet, quote, reply | Multiple amplification vectors |
| Conversation style | Threads, quote tweets | Non-linear discussions |
| API quality | Good (v2), rate limited | Reliable but constrained |
| Audience | Mixed, tech-heavy | Broad reach, influencer-rich |

### Twitter API Configuration

**Authentication:**
```python
TWITTER_CONFIG = {
    'api_version': 'v2',
    'auth_type': 'oauth2_app',  # App-only for read
    'base_url': 'https://api.twitter.com/2',
    
    # Rate limits (per 15-minute window)
    'rate_limits': {
        'tweets/search/recent': 450,
        'users/:id/tweets': 1500,
        'lists/:id/tweets': 900,
        'tweets': 300,
    },
    
    # Fields to request
    'tweet_fields': [
        'author_id', 'created_at', 'public_metrics',
        'entities', 'conversation_id', 'referenced_tweets',
        'in_reply_to_user_id', 'lang'
    ],
    'user_fields': [
        'name', 'username', 'verified', 'public_metrics',
        'description', 'created_at', 'profile_image_url'
    ],
    'expansions': ['author_id', 'referenced_tweets.id'],
}
```

### Twitter Source Types

**Supported source types:**
1. Keyword search
2. Hashtag monitoring (via search)
3. Account monitoring (user tweets)
4. Mention monitoring (via search)
5. List monitoring

**Query syntax:**
```python
TWITTER_QUERY_OPERATORS = {
    'and': ' ',              # space = AND
    'or': ' OR ',
    'not': ' -',
    'exact_phrase': '"{}"',
    'from_user': 'from:{}',
    'to_user': 'to:{}',
    'mention': '@{}',
    'hashtag': '#{}',
    'exclude_retweets': '-is:retweet',
    'exclude_replies': '-is:reply',
    'only_replies': 'is:reply',
    'language': 'lang:{}',
    'min_replies': 'min_replies:{}',
    'min_likes': 'min_faves:{}',
    'min_retweets': 'min_retweets:{}',
}

def build_twitter_query(source_config: dict) -> str:
    """Build Twitter search query from source config."""
    
    parts = []
    
    # Keywords
    if source_config.get('query'):
        parts.append(source_config['query'])
    
    # Exclusions
    if source_config.get('exclude_terms'):
        for term in source_config['exclude_terms']:
            parts.append(f'-{term}')
    
    # Language
    if source_config.get('language'):
        parts.append(f"lang:{source_config['language']}")
    
    # Exclude retweets (usually want originals)
    if source_config.get('exclude_retweets', True):
        parts.append('-is:retweet')
    
    return ' '.join(parts)
```

### Twitter Timing Adjustments

```python
TWITTER_TIMING = {
    'freshness_half_life_hours': 4,
    'max_post_age_hours': 24,
    'optimal_response_window_hours': 2,
    'conversation_stale_hours': 8,
    'polling_interval_minutes': {
        'high_priority': 5,
        'medium_priority': 15,
        'low_priority': 30,
    },
}

def calculate_twitter_time_factor(created_at: datetime) -> float:
    """Calculate time factor with Twitter-specific decay."""
    
    age_hours = (datetime.now(timezone.utc) - created_at).total_seconds() / 3600
    half_life = TWITTER_TIMING['freshness_half_life_hours']
    
    if age_hours < 0.5:
        return 1.3  # Very fresh boost
    elif age_hours < 1:
        return 1.2
    elif age_hours < 2:
        return 1.1
    else:
        decay = 0.5 ** (age_hours / half_life)
        return max(0.3, min(1.0, decay))
```

### Twitter Engagement Normalization

```python
def normalize_twitter_engagement(raw_metrics: dict) -> EngagementMetrics:
    """Normalize Twitter engagement metrics."""
    
    return EngagementMetrics(
        likes=raw_metrics.get('like_count', 0),
        replies=raw_metrics.get('reply_count', 0),
        shares=raw_metrics.get('retweet_count', 0),
        quotes=raw_metrics.get('quote_count', 0),
        views=raw_metrics.get('impression_count'),  # May be None
    )

def calculate_twitter_engagement_rate(metrics: EngagementMetrics) -> float:
    """Calculate Twitter-specific engagement rate."""
    
    total = metrics.likes + metrics.replies + metrics.shares + (metrics.quotes or 0)
    
    if metrics.views and metrics.views > 0:
        return (total / metrics.views) * 100
    
    # Fallback estimation if no views
    return None
```

### Twitter Thread Handling

```python
def detect_twitter_thread(tweet: dict) -> bool:
    """Detect if tweet is part of a thread."""
    
    # Check if this is a self-reply
    author_id = tweet.get('author_id')
    in_reply_to = tweet.get('in_reply_to_user_id')
    
    if in_reply_to and in_reply_to == author_id:
        return True
    
    # Check conversation_id
    conversation_id = tweet.get('conversation_id')
    tweet_id = tweet.get('id')
    
    if conversation_id and conversation_id != tweet_id:
        return True
    
    return False


def get_thread_position(tweet: dict) -> str:
    """Determine position in thread."""
    
    if not detect_twitter_thread(tweet):
        return 'standalone'
    
    conversation_id = tweet.get('conversation_id')
    tweet_id = tweet.get('id')
    
    if conversation_id == tweet_id:
        return 'thread_start'
    
    # Would need to fetch thread to determine exact position
    return 'thread_reply'
```

### Twitter-Specific Scoring Adjustments

```python
TWITTER_SCORING_ADJUSTMENTS = {
    # Engagement thresholds (Twitter-calibrated)
    'likes_excellent': 100,
    'likes_good': 50,
    'likes_moderate': 20,
    
    'replies_excellent': 25,
    'replies_good': 10,
    'replies_moderate': 5,
    
    'retweets_excellent': 50,
    'retweets_good': 20,
    'retweets_moderate': 10,
    
    # Follower thresholds
    'influencer_followers': 50000,
    'established_followers': 10000,
    'micro_influencer_followers': 5000,
    
    # Verified bonus
    'verified_bonus': 10,
    
    # Thread handling
    'thread_start_bonus': 5,
    'thread_reply_penalty': -3,
}
```

## 7.9.3 LinkedIn Platform Details

### Platform Characteristics

| Aspect | Value | Implications |
|--------|-------|--------------|
| Content type | Posts, articles, comments | Professional, longer-form |
| Lifespan | 24-72 hours | Slower decay, longer engagement window |
| Engagement types | Like, comment, share, reactions | Professional engagement patterns |
| Conversation style | Comments, nested replies | More structured discussions |
| API quality | Limited, restrictive | Less data available |
| Audience | Professional, B2B | High-value but smaller reach |

### LinkedIn API Configuration

**Authentication:**
```python
LINKEDIN_CONFIG = {
    'api_version': 'v2',
    'auth_type': 'oauth2_3legged',  # Requires user auth
    'base_url': 'https://api.linkedin.com/v2',
    
    # Rate limits (daily)
    'rate_limits': {
        'shares': 100000,  # Varies by app
        'ugcPosts': 100000,
    },
    
    # Required scopes
    'scopes': [
        'r_liteprofile',
        'r_organization_social',
        'w_member_social',
    ],
    
    # Fields
    'post_fields': [
        'id', 'owner', 'created', 'text',
        'totalShareStatistics'
    ],
}
```

### LinkedIn Source Types

**Supported source types:**
1. Organization posts (company page monitoring)
2. Hashtag search (limited)
3. Account monitoring (limited)

**Limitations:**
- No general keyword search API
- Limited to organization content or authenticated user's network
- Must use organization page access

```python
LINKEDIN_SOURCE_LIMITATIONS = {
    'keyword_search': False,  # Not available via API
    'hashtag_search': True,   # Limited functionality
    'account_monitoring': True,  # Requires connection or organization access
    'mention_monitoring': False,  # Not available
    'community_monitoring': False,  # Groups API deprecated
}
```

### LinkedIn Timing Adjustments

```python
LINKEDIN_TIMING = {
    'freshness_half_life_hours': 12,
    'max_post_age_hours': 72,
    'optimal_response_window_hours': 8,
    'conversation_stale_hours': 24,
    'polling_interval_minutes': {
        'high_priority': 15,
        'medium_priority': 30,
        'low_priority': 60,
    },
}

def calculate_linkedin_time_factor(created_at: datetime) -> float:
    """Calculate time factor with LinkedIn-specific decay."""
    
    age_hours = (datetime.now(timezone.utc) - created_at).total_seconds() / 3600
    half_life = LINKEDIN_TIMING['freshness_half_life_hours']
    
    if age_hours < 2:
        return 1.2  # Fresh boost (less aggressive than Twitter)
    elif age_hours < 6:
        return 1.1
    elif age_hours < 12:
        return 1.0
    else:
        decay = 0.5 ** (age_hours / half_life)
        return max(0.4, min(1.0, decay))  # Slower floor than Twitter
```

### LinkedIn Engagement Normalization

```python
def normalize_linkedin_engagement(raw_stats: dict) -> EngagementMetrics:
    """Normalize LinkedIn engagement metrics."""
    
    return EngagementMetrics(
        likes=raw_stats.get('likeCount', 0),
        replies=raw_stats.get('commentCount', 0),
        shares=raw_stats.get('shareCount', 0),
        views=raw_stats.get('impressionCount'),
        clicks=raw_stats.get('clickCount'),  # LinkedIn-specific
    )


# LinkedIn engagement is typically lower volume but higher value
LINKEDIN_ENGAGEMENT_MULTIPLIER = 1.5

def adjust_linkedin_engagement_score(base_score: int) -> int:
    """Adjust engagement score for LinkedIn's lower but more valuable engagement."""
    
    return int(base_score * LINKEDIN_ENGAGEMENT_MULTIPLIER)
```

### LinkedIn-Specific Scoring Adjustments

```python
LINKEDIN_SCORING_ADJUSTMENTS = {
    # Engagement thresholds (LinkedIn-calibrated, lower than Twitter)
    'likes_excellent': 50,
    'likes_good': 25,
    'likes_moderate': 10,
    
    'comments_excellent': 15,
    'comments_good': 8,
    'comments_moderate': 3,
    
    'shares_excellent': 20,
    'shares_good': 10,
    'shares_moderate': 5,
    
    # Follower thresholds (connection-based)
    'influencer_connections': 30000,
    'established_connections': 10000,
    'professional_connections': 5000,
    
    # Professional context bonus
    'verified_company_bonus': 8,
    'decision_maker_title_bonus': 10,
    
    # Content type bonuses
    'article_bonus': 5,  # Long-form content
    'document_bonus': 3,  # PDF/presentation shares
}
```

## 7.9.4 Reddit Platform Details

### Platform Characteristics

| Aspect | Value | Implications |
|--------|-------|--------------|
| Content type | Posts, comments, links | Discussion-oriented |
| Lifespan | 12-48 hours (varies by sub) | Community-dependent |
| Engagement types | Upvote, downvote, comment, award | Unique voting system |
| Conversation style | Threaded comments | Deep nested discussions |
| API quality | Good, well-documented | Reliable but rate-limited |
| Audience | Tech-savvy, community-oriented | Authentic engagement valued |

### Reddit API Configuration

**Authentication:**
```python
REDDIT_CONFIG = {
    'api_version': 'v1',
    'auth_type': 'oauth2_script',  # Script app auth
    'base_url': 'https://oauth.reddit.com',
    
    # Rate limits
    'rate_limits': {
        'requests_per_minute': 60,
    },
    
    # Required User-Agent
    'user_agent': 'JenContentDiscovery/1.0 by /u/gendigital',
    
    # Important: Reddit requires descriptive User-Agent
}
```

### Reddit Source Types

**Supported source types:**
1. Subreddit monitoring (new, hot, rising)
2. Keyword search (global or subreddit-specific)
3. User monitoring
4. Multi-reddit monitoring

**Query syntax:**
```python
REDDIT_SEARCH_SYNTAX = {
    'and': ' ',
    'or': ' OR ',
    'not': ' NOT ',
    'exact_phrase': '"{}"',
    'author': 'author:{}',
    'subreddit': 'subreddit:{}',
    'flair': 'flair:{}',
    'self_only': 'self:yes',
    'link_only': 'self:no',
    'nsfw': 'nsfw:yes',  # or nsfw:no
}

def build_reddit_query(source_config: dict) -> str:
    """Build Reddit search query from source config."""
    
    parts = []
    
    # Keywords
    if source_config.get('query'):
        parts.append(source_config['query'])
    
    # Subreddit restriction
    if source_config.get('subreddit'):
        parts.append(f"subreddit:{source_config['subreddit']}")
    
    # Exclude NSFW
    if source_config.get('exclude_nsfw', True):
        parts.append('nsfw:no')
    
    return ' '.join(parts)
```

### Reddit Subreddit Configuration

```python
# Recommended subreddits for AI/agent/security topics
RECOMMENDED_SUBREDDITS = {
    'high_relevance': [
        'MachineLearning',      # ~2.8M members, technical ML
        'LocalLLaMA',           # ~200K, local LLM enthusiasts
        'LangChain',            # ~50K, agent framework
        'artificial',           # ~1.5M, general AI
        'learnmachinelearning', # ~500K, learning ML
    ],
    'medium_relevance': [
        'programming',          # ~5M, general dev
        'python',               # ~1.2M, Python
        'datascience',          # ~800K, data science
        'deeplearning',         # ~200K, DL
        'OpenAI',               # ~600K, OpenAI
        'ChatGPT',              # ~1M, ChatGPT users
    ],
    'exploratory': [
        'technology',           # ~14M, general tech
        'Futurology',           # ~17M, future tech
        'singularity',          # ~300K, AI future
    ],
}

def get_subreddit_relevance_weight(subreddit: str) -> float:
    """Get relevance weight for subreddit."""
    
    subreddit_lower = subreddit.lower()
    
    for tier, subs in RECOMMENDED_SUBREDDITS.items():
        if subreddit_lower in [s.lower() for s in subs]:
            if tier == 'high_relevance':
                return 1.3
            elif tier == 'medium_relevance':
                return 1.1
            elif tier == 'exploratory':
                return 0.9
    
    return 1.0  # Unknown subreddit
```

### Reddit Timing Adjustments

```python
REDDIT_TIMING = {
    'freshness_half_life_hours': 8,
    'max_post_age_hours': 48,
    'optimal_response_window_hours': 4,
    'conversation_stale_hours': 12,
    'polling_interval_minutes': {
        'high_priority': 10,
        'medium_priority': 20,
        'low_priority': 45,
    },
}

# Reddit timing varies significantly by subreddit
SUBREDDIT_TIMING_OVERRIDES = {
    'MachineLearning': {
        'max_post_age_hours': 72,  # Discussions last longer
        'freshness_half_life_hours': 12,
    },
    'LocalLLaMA': {
        'max_post_age_hours': 48,
        'freshness_half_life_hours': 8,
    },
}
```

### Reddit Engagement Normalization

```python
def normalize_reddit_engagement(post_data: dict) -> EngagementMetrics:
    """Normalize Reddit engagement metrics."""
    
    score = post_data.get('score', 0)  # upvotes - downvotes
    upvote_ratio = post_data.get('upvote_ratio', 0.5)
    
    # Estimate upvotes from score and ratio
    # score = upvotes - downvotes
    # ratio = upvotes / (upvotes + downvotes)
    # Solving: upvotes ≈ score / (2 * ratio - 1) if ratio != 0.5
    if upvote_ratio > 0.5:
        estimated_upvotes = int(score / (2 * upvote_ratio - 1))
    else:
        estimated_upvotes = score  # Fallback
    
    return EngagementMetrics(
        likes=max(0, estimated_upvotes),
        replies=post_data.get('num_comments', 0),
        shares=None,  # Reddit doesn't expose
        upvote_ratio=upvote_ratio,
        awards=post_data.get('total_awards_received', 0),
    )


def calculate_reddit_controversy_score(upvote_ratio: float, num_comments: int) -> float:
    """Calculate controversy score for Reddit posts."""
    
    # Close to 0.5 ratio with many comments = controversial
    controversy = 1 - abs(upvote_ratio - 0.5) * 2
    
    # Scale by comment activity
    comment_factor = min(1.0, num_comments / 50)
    
    return controversy * comment_factor
```

### Reddit-Specific Scoring Adjustments

```python
REDDIT_SCORING_ADJUSTMENTS = {
    # Score thresholds (Reddit uses different scale)
    'score_excellent': 500,
    'score_good': 100,
    'score_moderate': 25,
    
    'comments_excellent': 100,
    'comments_good': 30,
    'comments_moderate': 10,
    
    # Award bonuses
    'gold_bonus': 8,
    'platinum_bonus': 12,
    'any_award_bonus': 3,
    
    # Upvote ratio considerations
    'high_ratio_bonus': 5,      # > 90%
    'controversial_penalty': -5, # < 60%
    
    # Account age (Reddit values established accounts)
    'old_account_bonus': 5,     # > 2 years
    'new_account_penalty': -5,  # < 90 days
    
    # Karma thresholds
    'high_karma_bonus': 5,      # > 50K
    'low_karma_penalty': -3,    # < 1K
}


def calculate_reddit_author_bonus(author_data: dict) -> int:
    """Calculate Reddit-specific author bonus."""
    
    bonus = 0
    
    # Account age
    created = author_data.get('created_utc')
    if created:
        age_days = (datetime.now(timezone.utc) - datetime.fromtimestamp(created, tz=timezone.utc)).days
        if age_days > 730:  # 2 years
            bonus += REDDIT_SCORING_ADJUSTMENTS['old_account_bonus']
        elif age_days < 90:
            bonus += REDDIT_SCORING_ADJUSTMENTS['new_account_penalty']
    
    # Karma
    total_karma = author_data.get('link_karma', 0) + author_data.get('comment_karma', 0)
    if total_karma > 50000:
        bonus += REDDIT_SCORING_ADJUSTMENTS['high_karma_bonus']
    elif total_karma < 1000:
        bonus += REDDIT_SCORING_ADJUSTMENTS['low_karma_penalty']
    
    return bonus
```

### Reddit Community Guidelines Awareness

```python
# Reddit engagement requires respecting community norms
REDDIT_ENGAGEMENT_GUIDELINES = {
    'avoid_self_promotion': True,
    'match_subreddit_tone': True,
    'participate_dont_advertise': True,
    'respect_karma_requirements': True,
    'use_appropriate_flair': True,
}

def check_reddit_engagement_appropriateness(subreddit: str, content_type: str) -> dict:
    """Check if engagement is appropriate for subreddit."""
    
    # Some subreddits have strict rules about promotional content
    strict_subreddits = ['MachineLearning', 'programming', 'datascience']
    
    if subreddit in strict_subreddits and content_type == 'promotional':
        return {
            'appropriate': False,
            'reason': 'Subreddit has strict self-promotion rules',
            'recommendation': 'Focus on adding value, not promoting',
        }
    
    return {'appropriate': True}
```

## 7.9.5 Discord Platform Details

### Platform Characteristics

| Aspect | Value | Implications |
|--------|-------|--------------|
| Content type | Messages, threads | Real-time chat |
| Lifespan | Hours to minutes | Very fast-moving |
| Engagement types | Reactions, replies, threads | Conversational |
| Conversation style | Channels, threads | Organized by topic |
| API quality | Good, bot-friendly | Designed for bots |
| Audience | Technical communities | Engaged, expects quick response |

### Discord API Configuration

```python
DISCORD_CONFIG = {
    'api_version': 'v10',
    'auth_type': 'bot_token',
    'base_url': 'https://discord.com/api/v10',
    
    # Rate limits (per route)
    'rate_limits': {
        'global': 50,  # requests per second
        'channel_messages': 5,  # per 5 seconds per channel
    },
    
    # Bot permissions needed
    'required_permissions': [
        'READ_MESSAGE_HISTORY',
        'VIEW_CHANNEL',
        'SEND_MESSAGES',
    ],
    
    # Gateway intents
    'intents': [
        'GUILDS',
        'GUILD_MESSAGES',
        'MESSAGE_CONTENT',  # Requires verification
    ],
}
```

### Discord Source Types

**Supported source types:**
1. Channel monitoring
2. Thread monitoring
3. Keyword watching (via message content)
4. Server monitoring (multiple channels)

```python
DISCORD_SOURCE_CONFIG = {
    'channel_monitoring': {
        'watch_type': 'new_messages',
        'include_threads': True,
        'include_replies': True,
    },
    'keyword_watching': {
        'case_sensitive': False,
        'whole_word': False,
        'regex_support': True,
    },
}
```

### Discord Timing Adjustments

```python
DISCORD_TIMING = {
    'freshness_half_life_hours': 2,  # Very fast
    'max_post_age_hours': 12,
    'optimal_response_window_hours': 1,
    'conversation_stale_hours': 4,
    'polling_interval_minutes': {
        'high_priority': 2,
        'medium_priority': 5,
        'low_priority': 15,
    },
}
```

### Discord-Specific Considerations

```python
DISCORD_ENGAGEMENT_GUIDELINES = {
    # Discord has different norms than other platforms
    'rapid_response_expected': True,
    'informal_tone_appropriate': True,
    'code_blocks_supported': True,
    'emoji_reactions_common': True,
    'thread_creation_encouraged': True,
}

# Server-specific configurations
MONITORED_DISCORD_SERVERS = {
    'ai_agents_community': {
        'guild_id': '123456789',
        'channels': {
            'general': {'relevance': 'medium'},
            'technical': {'relevance': 'high'},
            'help': {'relevance': 'high'},
        },
        'response_persona': 'advisor',  # More technical
    },
}
```

## 7.9.6 Cross-Platform Normalization

### Unified Engagement Metrics

```python
def normalize_engagement_cross_platform(
    platform: str,
    raw_engagement: dict
) -> EngagementMetrics:
    """Normalize engagement metrics across platforms."""
    
    if platform == 'twitter':
        return normalize_twitter_engagement(raw_engagement)
    elif platform == 'linkedin':
        return normalize_linkedin_engagement(raw_engagement)
    elif platform == 'reddit':
        return normalize_reddit_engagement(raw_engagement)
    elif platform == 'discord':
        return normalize_discord_engagement(raw_engagement)
    else:
        raise ValueError(f"Unknown platform: {platform}")


def compare_engagement_across_platforms(
    engagement: EngagementMetrics,
    platform: str
) -> str:
    """Compare engagement to platform-specific benchmarks."""
    
    benchmarks = PLATFORM_ENGAGEMENT_BENCHMARKS[platform]
    
    total = engagement.likes + engagement.replies + (engagement.shares or 0)
    
    if total >= benchmarks['excellent']:
        return 'excellent'
    elif total >= benchmarks['good']:
        return 'good'
    elif total >= benchmarks['moderate']:
        return 'moderate'
    else:
        return 'low'


PLATFORM_ENGAGEMENT_BENCHMARKS = {
    'twitter': {'excellent': 200, 'good': 50, 'moderate': 15},
    'linkedin': {'excellent': 100, 'good': 30, 'moderate': 10},
    'reddit': {'excellent': 500, 'good': 100, 'moderate': 25},
    'discord': {'excellent': 20, 'good': 10, 'moderate': 5},
}
```

### Unified Timing

```python
def get_platform_timing_config(platform: str) -> dict:
    """Get timing configuration for platform."""
    
    configs = {
        'twitter': TWITTER_TIMING,
        'linkedin': LINKEDIN_TIMING,
        'reddit': REDDIT_TIMING,
        'discord': DISCORD_TIMING,
    }
    
    return configs.get(platform, TWITTER_TIMING)  # Default to Twitter


def calculate_platform_adjusted_time_factor(
    created_at: datetime,
    platform: str
) -> float:
    """Calculate time factor with platform-specific adjustments."""
    
    if platform == 'twitter':
        return calculate_twitter_time_factor(created_at)
    elif platform == 'linkedin':
        return calculate_linkedin_time_factor(created_at)
    elif platform == 'reddit':
        # Reddit may have subreddit-specific timing
        return calculate_reddit_time_factor(created_at)
    elif platform == 'discord':
        return calculate_discord_time_factor(created_at)
    else:
        # Default decay
        age_hours = (datetime.now(timezone.utc) - created_at).total_seconds() / 3600
        return max(0.3, 0.5 ** (age_hours / 6))
```

### Platform Priority Weighting

```python
# Weight platforms differently based on strategic value
PLATFORM_PRIORITY_WEIGHTS = {
    'twitter': 1.0,      # Baseline
    'linkedin': 1.2,     # Higher value per engagement (professional)
    'reddit': 0.9,       # Slightly lower (more casual)
    'discord': 0.8,      # Lower visibility, niche
}

def apply_platform_weight(priority_score: float, platform: str) -> float:
    """Apply platform-specific weight to priority score."""
    
    weight = PLATFORM_PRIORITY_WEIGHTS.get(platform, 1.0)
    return priority_score * weight
```

## 7.9.7 Platform-Specific Filtering

### Platform Content Filters

```python
PLATFORM_CONTENT_FILTERS = {
    'twitter': {
        'min_content_length': 10,
        'max_hashtags': 10,  # Spam indicator if too many
        'exclude_patterns': [
            r'^RT @',  # Retweets (if not filtered by API)
        ],
    },
    'linkedin': {
        'min_content_length': 20,  # LinkedIn posts tend to be longer
        'exclude_patterns': [
            r'#opentowork',  # Job seeking posts
            r'I\'m happy to announce',  # Generic announcements
        ],
    },
    'reddit': {
        'min_content_length': 10,
        'exclude_removed': True,  # [removed] or [deleted]
        'exclude_patterns': [
            r'^\[removed\]$',
            r'^\[deleted\]$',
        ],
        'min_upvote_ratio': 0.4,  # Exclude heavily downvoted
    },
    'discord': {
        'min_content_length': 5,
        'exclude_bot_messages': True,
    },
}

def apply_platform_content_filter(
    post: NormalizedPost
) -> Tuple[bool, Optional[str]]:
    """Apply platform-specific content filters."""
    
    filters = PLATFORM_CONTENT_FILTERS.get(post.platform, {})
    
    # Length check
    min_length = filters.get('min_content_length', 10)
    if len(post.content_text) < min_length:
        return False, f'content_too_short_{post.platform}'
    
    # Pattern exclusions
    exclude_patterns = filters.get('exclude_patterns', [])
    for pattern in exclude_patterns:
        if re.search(pattern, post.content_text, re.IGNORECASE):
            return False, f'excluded_pattern_{post.platform}'
    
    # Reddit-specific
    if post.platform == 'reddit':
        upvote_ratio = post.engagement.upvote_ratio
        min_ratio = filters.get('min_upvote_ratio', 0.4)
        if upvote_ratio and upvote_ratio < min_ratio:
            return False, 'low_upvote_ratio'
    
    return True, None
```

### Platform Rate Limits for Engagement

```python
PLATFORM_ENGAGEMENT_LIMITS = {
    'twitter': {
        'per_hour': 5,
        'per_day': 50,
        'per_author_per_day': 1,
    },
    'linkedin': {
        'per_hour': 3,
        'per_day': 20,
        'per_author_per_day': 1,
    },
    'reddit': {
        'per_hour': 2,
        'per_day': 15,
        'per_author_per_day': 1,
        'per_subreddit_per_day': 3,  # Reddit-specific
    },
    'discord': {
        'per_hour': 10,
        'per_day': 50,
        'per_channel_per_hour': 3,  # Discord-specific
    },
}
```

## 7.9.8 Platform API Health Monitoring

### Health Checks per Platform

```python
async def check_platform_health(platform: str) -> dict:
    """Check health of platform API integration."""
    
    try:
        if platform == 'twitter':
            return await check_twitter_health()
        elif platform == 'linkedin':
            return await check_linkedin_health()
        elif platform == 'reddit':
            return await check_reddit_health()
        elif platform == 'discord':
            return await check_discord_health()
    except Exception as e:
        return {
            'platform': platform,
            'healthy': False,
            'error': str(e),
        }


async def check_twitter_health() -> dict:
    """Check Twitter API health."""
    
    try:
        # Simple API call to check connectivity
        response = await twitter_client.get_rate_limit_status()
        
        remaining = response.get('resources', {}).get('search', {}).get('/search/tweets', {}).get('remaining', 0)
        
        return {
            'platform': 'twitter',
            'healthy': True,
            'rate_limit_remaining': remaining,
            'latency_ms': response.get('latency_ms'),
        }
    except AuthenticationError:
        return {
            'platform': 'twitter',
            'healthy': False,
            'error': 'authentication_failed',
        }
    except RateLimitError:
        return {
            'platform': 'twitter',
            'healthy': False,
            'error': 'rate_limited',
        }
```

### Platform Metrics

```python
# Platform-specific metrics
platform_api_latency = Histogram(
    'platform_api_latency_seconds',
    'API latency by platform',
    ['platform', 'endpoint'],
    buckets=[0.1, 0.25, 0.5, 1, 2, 5, 10]
)

platform_api_errors = Counter(
    'platform_api_errors_total',
    'API errors by platform',
    ['platform', 'error_type']
)

platform_rate_limit_remaining = Gauge(
    'platform_rate_limit_remaining',
    'Remaining rate limit',
    ['platform', 'endpoint']
)

platform_discovery_volume = Counter(
    'platform_discovery_volume_total',
    'Posts discovered by platform',
    ['platform']
)
```

## 7.9.9 Implementation Guidance for Neoclaw

### Implementation Order

1. **Start with one platform (Twitter)**
   - Full API integration
   - Platform-specific timing
   - Engagement normalization
   - Test thoroughly

2. **Add second platform (Reddit)**
   - Similar flow to Twitter
   - Subreddit-specific handling
   - Community norms awareness

3. **Add LinkedIn**
   - More limited API
   - Professional context
   - Different engagement patterns

4. **Add Discord (if needed)**
   - Real-time requirements
   - Bot infrastructure

5. **Build cross-platform normalization**
   - Unified metrics
   - Comparable scoring

### Testing Checklist

#### Per-Platform Tests
- [ ] API authentication
- [ ] Search/fetch operations
- [ ] Response parsing
- [ ] Engagement normalization
- [ ] Timing calculations
- [ ] Rate limit handling

#### Cross-Platform Tests
- [ ] Unified post format
- [ ] Comparable scoring
- [ ] Platform weight application
- [ ] Queue balance across platforms

### Common Pitfalls

**API inconsistency:**
Platforms change APIs. Monitor for breaking changes.

**Rate limit miscalculation:**
Each platform has different limits. Track per-platform.

**Timing assumptions:**
Content lifespan varies. Don't apply Twitter timing to LinkedIn.

**Engagement comparisons:**
100 likes on Twitter ≠ 100 likes on LinkedIn. Normalize.

**Community norms:**
What works on Twitter may fail on Reddit. Adapt engagement style.

---

**END OF SECTION 7.9**

Section 7.10 continues with Real-Time Processing specification.
-e 


# SECTION 7.10: REAL-TIME PROCESSING

## 7.10.1 What Real-Time Processing Is

### The Core Concept

Real-time processing handles time-sensitive content that requires immediate attention, bypassing normal batch processing. While most discovery operates on polling intervals (5-30 minutes), some content demands faster response.

**Real-time triggers:**
- Mentions of Jen/brand
- Replies to Jen's posts
- High-priority source matches
- Trending content detection
- Urgent help-seeking patterns

**Response targets:**
- Mentions: < 5 minutes
- Replies: < 10 minutes
- High-priority matches: < 15 minutes

### Why Real-Time Matters

**User expectations:**
When someone @mentions a brand, they expect timely response. Delayed responses feel ignored.

**Conversation relevance:**
Active conversations move fast. A response 2 hours later may miss the conversation entirely.

**Competitive advantage:**
Being first to respond to help-seeking posts builds reputation and captures opportunities.

**Relationship building:**
Prompt responses signal attentiveness and build trust.

### Real-Time vs Batch Processing

| Aspect | Batch | Real-Time |
|--------|-------|-----------|
| Latency | 5-30 minutes | < 5 minutes |
| Volume | Thousands of posts | Selected posts |
| Trigger | Polling interval | Event-driven |
| Priority | Queue position | Immediate |
| Cost | Efficient | Higher per-post |

Both modes coexist. Real-time handles urgent content; batch handles volume.

## 7.10.2 Real-Time Triggers

### Mention Detection

Brand mentions require immediate attention:

```python
@dataclass
class MentionTrigger:
    mention_handles: List[str]
    priority: str = 'critical'
    max_response_minutes: int = 5
    
MENTION_TRIGGERS = [
    MentionTrigger(
        mention_handles=['@JenAI', '@GenDigital'],
        priority='critical',
        max_response_minutes=5,
    ),
    MentionTrigger(
        mention_handles=['@AgentTrustHub'],
        priority='high',
        max_response_minutes=10,
    ),
]

async def check_mention_trigger(post: NormalizedPost) -> Optional[RealTimeTrigger]:
    """Check if post triggers mention detection."""
    
    content = post.content_text.lower()
    
    for trigger in MENTION_TRIGGERS:
        for handle in trigger.mention_handles:
            if handle.lower() in content:
                return RealTimeTrigger(
                    trigger_type='mention',
                    trigger_detail=handle,
                    priority=trigger.priority,
                    max_response_minutes=trigger.max_response_minutes,
                    source='mention_detection',
                )
    
    return None
```

### Reply Detection

Replies to Jen's posts require follow-up:

```python
async def check_reply_trigger(post: NormalizedPost) -> Optional[RealTimeTrigger]:
    """Check if post is a reply to our content."""
    
    # Check if this is a reply
    if not post.platform_data.get('is_reply'):
        return None
    
    # Check if replying to our post
    in_reply_to = post.platform_data.get('in_reply_to_id')
    
    if in_reply_to:
        our_post = db.query_one("""
            SELECT id FROM engagements
            WHERE platform_post_id = %(post_id)s
        """, {'post_id': in_reply_to})
        
        if our_post:
            return RealTimeTrigger(
                trigger_type='reply_to_us',
                trigger_detail=str(our_post.id),
                priority='high',
                max_response_minutes=10,
                source='reply_detection',
            )
    
    return None
```

### Trending Detection

Posts gaining rapid engagement:

```python
async def check_trending_trigger(post: NormalizedPost) -> Optional[RealTimeTrigger]:
    """Check if post is trending rapidly."""
    
    age_hours = (datetime.now(timezone.utc) - post.created_at).total_seconds() / 3600
    
    if age_hours <= 0:
        return None
    
    # Calculate engagement velocity
    total_engagement = (
        post.engagement.likes +
        post.engagement.replies +
        (post.engagement.shares or 0)
    )
    
    velocity = total_engagement / age_hours
    
    # Threshold depends on platform
    thresholds = {
        'twitter': 100,
        'reddit': 50,
        'linkedin': 30,
    }
    
    threshold = thresholds.get(post.platform, 50)
    
    if velocity >= threshold:
        return RealTimeTrigger(
            trigger_type='trending',
            trigger_detail=f'velocity_{int(velocity)}',
            priority='high',
            max_response_minutes=15,
            source='trending_detection',
        )
    
    return None
```

### Urgent Help-Seeking Detection

Posts with urgent help signals:

```python
URGENT_PATTERNS = [
    r'urgent',
    r'asap',
    r'help.*now',
    r'emergency',
    r'critical.*issue',
    r'production.*down',
    r'breaking.*prod',
    r'need.*immediately',
]

async def check_urgent_help_trigger(post: NormalizedPost) -> Optional[RealTimeTrigger]:
    """Check for urgent help-seeking patterns."""
    
    content = post.content_text.lower()
    
    # Must be classified as help-seeking
    if post.classification:
        primary = post.classification.get('primary')
        if primary != 'help_seeking_solution':
            return None
    
    # Check for urgent patterns
    for pattern in URGENT_PATTERNS:
        if re.search(pattern, content, re.IGNORECASE):
            return RealTimeTrigger(
                trigger_type='urgent_help',
                trigger_detail=pattern,
                priority='high',
                max_response_minutes=10,
                source='urgent_help_detection',
            )
    
    return None
```

### VIP Author Detection

Posts from high-value accounts:

```python
async def check_vip_trigger(post: NormalizedPost) -> Optional[RealTimeTrigger]:
    """Check if post is from VIP author."""
    
    # Check VIP list
    vip = db.query_one("""
        SELECT tier, response_priority FROM vip_authors
        WHERE platform = %(platform)s
        AND (
            platform_author_id = %(author_id)s
            OR handle = %(handle)s
        )
    """, {
        'platform': post.platform,
        'author_id': post.author.platform_author_id,
        'handle': post.author.handle,
    })
    
    if vip:
        return RealTimeTrigger(
            trigger_type='vip_author',
            trigger_detail=f'{vip.tier}_{post.author.handle}',
            priority=vip.response_priority,
            max_response_minutes=15,
            source='vip_detection',
        )
    
    # Check follower threshold for auto-VIP
    if post.author.followers_count and post.author.followers_count >= 100000:
        return RealTimeTrigger(
            trigger_type='high_follower_author',
            trigger_detail=f'followers_{post.author.followers_count}',
            priority='high',
            max_response_minutes=15,
            source='follower_detection',
        )
    
    return None
```

## 7.10.3 Real-Time Processing Pipeline

### Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                         REAL-TIME PROCESSING PIPELINE                               │
│                                                                                     │
│  ┌───────────┐    ┌───────────┐    ┌───────────┐    ┌───────────┐    ┌───────────┐ │
│  │  EVENT    │    │  TRIGGER  │    │  FAST     │    │ PRIORITY  │    │ IMMEDIATE │ │
│  │  STREAM   │───▶│  CHECK    │───▶│  SCORE    │───▶│  QUEUE    │───▶│  NOTIFY   │ │
│  │           │    │           │    │           │    │           │    │           │ │
│  │ Webhooks  │    │ Check     │    │ Quick     │    │ Critical  │    │ Alert     │ │
│  │ Streaming │    │ all       │    │ scoring   │    │ priority  │    │ workers/  │ │
│  │ APIs      │    │ triggers  │    │ pass      │    │ insertion │    │ humans    │ │
│  │           │    │           │    │           │    │           │    │           │ │
│  └───────────┘    └───────────┘    └───────────┘    └───────────┘    └───────────┘ │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

### Event Sources

**Webhook-based (preferred):**
```python
# Twitter Account Activity API
@app.post("/webhooks/twitter")
async def twitter_webhook(request: Request):
    """Handle Twitter webhook events."""
    
    payload = await request.json()
    
    # Verify webhook signature
    if not verify_twitter_signature(request):
        raise HTTPException(401, "Invalid signature")
    
    # Process events
    for tweet_event in payload.get('tweet_create_events', []):
        await process_realtime_tweet(tweet_event)
    
    return {'status': 'ok'}
```

**Streaming API (alternative):**
```python
async def twitter_stream_listener():
    """Listen to Twitter filtered stream."""
    
    rules = [
        {'value': '@JenAI', 'tag': 'mention'},
        {'value': 'agent security', 'tag': 'keyword'},
    ]
    
    async for tweet in twitter_client.stream(rules):
        await process_realtime_tweet(tweet)
```

**Accelerated polling (fallback):**
```python
async def accelerated_polling_worker():
    """Poll high-priority sources more frequently."""
    
    while True:
        # Poll mention sources every 2 minutes
        mention_sources = get_sources_by_type('mention')
        
        for source in mention_sources:
            posts = await fetch_source(source)
            for post in posts:
                if await check_any_realtime_trigger(post):
                    await process_realtime_post(post)
        
        await asyncio.sleep(120)  # 2 minutes
```

### Trigger Evaluation

```python
async def check_all_realtime_triggers(post: NormalizedPost) -> List[RealTimeTrigger]:
    """Check all real-time triggers for a post."""
    
    triggers = []
    
    # Check each trigger type
    trigger_checks = [
        check_mention_trigger,
        check_reply_trigger,
        check_trending_trigger,
        check_urgent_help_trigger,
        check_vip_trigger,
    ]
    
    for check_func in trigger_checks:
        trigger = await check_func(post)
        if trigger:
            triggers.append(trigger)
    
    return triggers


async def check_any_realtime_trigger(post: NormalizedPost) -> bool:
    """Quick check if any real-time trigger matches."""
    
    triggers = await check_all_realtime_triggers(post)
    return len(triggers) > 0
```

### Fast Scoring

Skip heavy scoring for real-time; use lightweight version:

```python
async def fast_score_post(post: NormalizedPost) -> FastScoreResult:
    """Lightweight scoring for real-time processing."""
    
    # Quick relevance check (keywords only)
    keyword_score = score_keywords_only(post.content_text)
    
    # Quick opportunity check (engagement only)
    engagement_score = score_engagement_quick(post.engagement)
    
    # Quick author check (followers only)
    author_score = score_author_quick(post.author)
    
    # Combined
    fast_score = (keyword_score * 0.3) + (engagement_score * 0.4) + (author_score * 0.3)
    
    return FastScoreResult(
        score=fast_score,
        keyword_score=keyword_score,
        engagement_score=engagement_score,
        author_score=author_score,
        is_approximate=True,
    )
```

### Priority Queue Insertion

```python
async def insert_realtime_priority(
    post: NormalizedPost,
    triggers: List[RealTimeTrigger],
    fast_score: FastScoreResult
):
    """Insert into priority queue with real-time boost."""
    
    # Determine highest priority trigger
    priority_order = {'critical': 0, 'high': 1, 'medium': 2}
    triggers.sort(key=lambda t: priority_order.get(t.priority, 3))
    primary_trigger = triggers[0]
    
    # Calculate boosted priority
    boost = {
        'critical': 3.0,
        'high': 2.0,
        'medium': 1.5,
    }.get(primary_trigger.priority, 1.0)
    
    priority_score = fast_score.score * boost
    
    # Calculate expiration based on trigger
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=primary_trigger.max_response_minutes
    )
    
    # Insert at top of queue
    entry = QueueEntry(
        id=uuid4(),
        post_id=post.id,
        campaign_id=get_default_campaign_id(),
        priority_score=priority_score,
        expires_at=expires_at,
        status='pending',
        is_realtime=True,
        realtime_triggers=[asdict(t) for t in triggers],
    )
    
    db.execute("""
        INSERT INTO engagement_queue (...)
        VALUES (...)
    """, entry.__dict__)
    
    # Send immediate notification
    await notify_realtime_opportunity(entry, post, triggers)
```

## 7.10.4 Real-Time Notifications

### Notification Channels

```python
@dataclass
class RealTimeNotification:
    channel: str           # slack, webhook, push
    priority: str
    post_summary: str
    triggers: List[str]
    queue_entry_id: UUID
    response_deadline: datetime


async def notify_realtime_opportunity(
    entry: QueueEntry,
    post: NormalizedPost,
    triggers: List[RealTimeTrigger]
):
    """Send real-time notification."""
    
    notification = RealTimeNotification(
        channel='slack',
        priority=triggers[0].priority,
        post_summary=f"@{post.author.handle}: {post.content_text[:100]}...",
        triggers=[t.trigger_type for t in triggers],
        queue_entry_id=entry.id,
        response_deadline=entry.expires_at,
    )
    
    if triggers[0].priority == 'critical':
        # Critical: All channels
        await send_slack_notification(notification)
        await send_webhook_notification(notification)
        await send_push_notification(notification)
    elif triggers[0].priority == 'high':
        # High: Slack + webhook
        await send_slack_notification(notification)
        await send_webhook_notification(notification)
    else:
        # Medium: Slack only
        await send_slack_notification(notification)
```

### Slack Notification

```python
async def send_slack_notification(notification: RealTimeNotification):
    """Send Slack notification for real-time opportunity."""
    
    color = {
        'critical': '#FF0000',
        'high': '#FFA500',
        'medium': '#FFFF00',
    }.get(notification.priority, '#00FF00')
    
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"🚨 {notification.priority.upper()} Priority Opportunity"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": notification.post_summary
            }
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"Triggers: {', '.join(notification.triggers)}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"Respond by: {notification.response_deadline.strftime('%H:%M')}"
                }
            ]
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "View & Respond"},
                    "url": f"https://jen.app/queue/{notification.queue_entry_id}",
                    "style": "primary"
                },
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Dismiss"},
                    "action_id": f"dismiss_{notification.queue_entry_id}"
                }
            ]
        }
    ]
    
    await slack_client.post_message(
        channel=SLACK_REALTIME_CHANNEL,
        blocks=blocks,
        attachments=[{"color": color}]
    )
```

## 7.10.5 Real-Time Processing Workers

### Dedicated Real-Time Worker

```python
class RealTimeWorker:
    def __init__(self):
        self.running = True
    
    async def run(self):
        """Main real-time processing loop."""
        
        while self.running:
            try:
                # Fetch real-time queue entries
                entries = await self.fetch_realtime_entries()
                
                for entry in entries:
                    await self.process_entry(entry)
                
                # Short sleep - real-time needs to be responsive
                await asyncio.sleep(5)
            
            except Exception as e:
                log.error(f"Real-time worker error: {e}")
                await asyncio.sleep(10)
    
    async def fetch_realtime_entries(self) -> List[QueueEntry]:
        """Fetch entries from real-time queue."""
        
        return db.query("""
            SELECT * FROM engagement_queue
            WHERE is_realtime = true
            AND status = 'pending'
            AND expires_at > NOW()
            ORDER BY priority_score DESC
            LIMIT 10
            FOR UPDATE SKIP LOCKED
        """)
    
    async def process_entry(self, entry: QueueEntry):
        """Process a real-time queue entry."""
        
        try:
            # Mark as processing
            await self.mark_processing(entry.id)
            
            # Full scoring (now that we have time)
            post = await get_post(entry.post_id)
            full_scores = await calculate_full_scores(post)
            
            # Check if still valid
            if not await self.validate_for_engagement(post, full_scores):
                await self.mark_invalid(entry.id, 'failed_validation')
                return
            
            # Generate response
            response = await generate_response(post, full_scores)
            
            # Execute engagement
            result = await execute_engagement(post, response)
            
            # Complete entry
            await self.mark_completed(entry.id, result)
            
        except Exception as e:
            log.error(f"Error processing real-time entry {entry.id}: {e}")
            await self.mark_failed(entry.id, str(e))
```

### Auto-Escalation

```python
async def check_realtime_escalation():
    """Escalate real-time entries approaching deadline."""
    
    # Find entries close to expiration
    expiring = db.query("""
        SELECT * FROM engagement_queue
        WHERE is_realtime = true
        AND status = 'pending'
        AND expires_at < NOW() + INTERVAL '5 minutes'
        AND expires_at > NOW()
    """)
    
    for entry in expiring:
        # Send escalation notification
        await send_escalation_notification(entry)
        
        # Mark as escalated
        db.execute("""
            UPDATE engagement_queue
            SET escalated = true, escalated_at = NOW()
            WHERE id = %(id)s
        """, {'id': entry.id})
```

## 7.10.6 Real-Time Metrics

### Metrics

```python
# Real-time volume
realtime_triggers_total = Counter(
    'realtime_triggers_total',
    'Real-time triggers detected',
    ['trigger_type', 'priority']
)

# Response time
realtime_response_time = Histogram(
    'realtime_response_time_seconds',
    'Time from trigger to response',
    ['trigger_type'],
    buckets=[60, 120, 300, 600, 900, 1800]
)

# SLA compliance
realtime_sla_met = Counter(
    'realtime_sla_met_total',
    'Responses within SLA',
    ['trigger_type', 'met']  # met: true/false
)

# Escalations
realtime_escalations = Counter(
    'realtime_escalations_total',
    'Escalated real-time entries',
    ['trigger_type']
)
```

### SLA Tracking

```python
def calculate_realtime_sla_compliance(period_hours: int = 24) -> dict:
    """Calculate real-time SLA compliance."""
    
    results = db.query("""
        SELECT 
            realtime_triggers->0->>'trigger_type' as trigger_type,
            COUNT(*) as total,
            SUM(CASE 
                WHEN processed_at IS NOT NULL 
                AND processed_at <= expires_at 
                THEN 1 ELSE 0 
            END) as met_sla,
            AVG(EXTRACT(EPOCH FROM (processed_at - created_at))) as avg_response_seconds
        FROM engagement_queue
        WHERE is_realtime = true
        AND created_at > NOW() - INTERVAL '%(hours)s hours'
        GROUP BY realtime_triggers->0->>'trigger_type'
    """, {'hours': period_hours})
    
    return {
        row.trigger_type: {
            'total': row.total,
            'met_sla': row.met_sla,
            'sla_rate': row.met_sla / row.total if row.total > 0 else 0,
            'avg_response_seconds': row.avg_response_seconds,
        }
        for row in results
    }
```

## 7.10.7 Implementation Guidance for Neoclaw

### Implementation Order

1. **Define real-time triggers**
   - Mention detection
   - Reply detection
   - VIP detection

2. **Build trigger checking**
   - Trigger evaluation functions
   - Priority determination

3. **Implement fast scoring**
   - Lightweight scoring pass

4. **Build notification system**
   - Slack integration
   - Webhook support

5. **Implement real-time worker**
   - Dedicated processing loop
   - Escalation handling

6. **Add metrics**
   - SLA tracking
   - Response time monitoring

### Testing Checklist

- [ ] Trigger detection accuracy
- [ ] Notification delivery
- [ ] Priority queue insertion
- [ ] SLA calculation
- [ ] Escalation flow
- [ ] Worker recovery from errors

### Common Pitfalls

**Over-triggering:**
Too many real-time triggers overwhelms capacity. Be selective.

**Notification fatigue:**
Too many alerts leads to ignored alerts. Reserve for truly urgent.

**Deadline pressure:**
Short deadlines cause rushed, poor responses. Balance speed and quality.

**Resource contention:**
Real-time competing with batch for resources. Allocate dedicated capacity.

---

**END OF SECTION 7.10**

Section 7.11 continues with Discovery Analytics specification.
-e 


# SECTION 7.11: DISCOVERY ANALYTICS

## 7.11.1 What Discovery Analytics Is

### The Core Concept

Discovery Analytics measures and analyzes the performance of the content discovery system. It provides insights into what's working, what's not, and how to improve.

**Key questions analytics answers:**
- How much content are we discovering?
- What's the quality of discovered content?
- Which sources are most valuable?
- How effective is our filtering?
- What's our engagement success rate?
- Where are the optimization opportunities?

### Analytics Layers

**Volume metrics:** How much content flows through each stage
**Quality metrics:** How good is the content at each stage
**Performance metrics:** How fast and efficient is processing
**Outcome metrics:** What results does discovery produce
**Trend metrics:** How are things changing over time

### Analytics Consumers

**Operators:** Monitor system health, identify issues
**Strategists:** Optimize sources, thresholds, targeting
**Executives:** Understand ROI, high-level performance
**Engineers:** Debug issues, optimize performance

## 7.11.2 Volume Analytics

### Pipeline Volume Metrics

Track content volume at each pipeline stage:

```python
@dataclass
class PipelineVolumeMetrics:
    period_start: datetime
    period_end: datetime
    
    # Ingestion
    posts_ingested: int
    posts_per_source: Dict[str, int]
    posts_per_platform: Dict[str, int]
    
    # Classification
    posts_classified: int
    classification_distribution: Dict[str, int]
    
    # Scoring
    posts_scored: int
    avg_relevance_score: float
    avg_opportunity_score: float
    
    # Filtering
    posts_filtered: int
    posts_passed_filters: int
    filter_pass_rate: float
    filter_rejection_reasons: Dict[str, int]
    
    # Queue
    posts_queued: int
    posts_expired: int
    posts_engaged: int
    
    # Funnel
    ingestion_to_engagement_rate: float


def calculate_pipeline_volume(
    campaign_id: UUID,
    period_start: datetime,
    period_end: datetime
) -> PipelineVolumeMetrics:
    """Calculate pipeline volume metrics for period."""
    
    # Ingestion volume
    ingested = db.query_one("""
        SELECT 
            COUNT(*) as total,
            COUNT(*) FILTER (WHERE platform = 'twitter') as twitter,
            COUNT(*) FILTER (WHERE platform = 'linkedin') as linkedin,
            COUNT(*) FILTER (WHERE platform = 'reddit') as reddit
        FROM discovered_posts
        WHERE campaign_id = %(campaign_id)s
        AND discovered_at BETWEEN %(start)s AND %(end)s
    """, {'campaign_id': campaign_id, 'start': period_start, 'end': period_end})
    
    # Classification distribution
    classifications = db.query("""
        SELECT 
            classification->>'primary' as classification,
            COUNT(*) as count
        FROM discovered_posts
        WHERE campaign_id = %(campaign_id)s
        AND discovered_at BETWEEN %(start)s AND %(end)s
        AND classification IS NOT NULL
        GROUP BY classification->>'primary'
    """, {'campaign_id': campaign_id, 'start': period_start, 'end': period_end})
    
    # Filtering stats
    filter_stats = db.query_one("""
        SELECT 
            COUNT(*) FILTER (WHERE status = 'filtered') as filtered,
            COUNT(*) FILTER (WHERE status NOT IN ('filtered', 'pending_classification')) as passed
        FROM discovered_posts
        WHERE campaign_id = %(campaign_id)s
        AND discovered_at BETWEEN %(start)s AND %(end)s
    """, {'campaign_id': campaign_id, 'start': period_start, 'end': period_end})
    
    # Engagement stats
    engaged = db.query_scalar("""
        SELECT COUNT(*) FROM discovered_posts
        WHERE campaign_id = %(campaign_id)s
        AND discovered_at BETWEEN %(start)s AND %(end)s
        AND status = 'engaged'
    """, {'campaign_id': campaign_id, 'start': period_start, 'end': period_end})
    
    total_ingested = ingested.total or 0
    total_engaged = engaged or 0
    
    return PipelineVolumeMetrics(
        period_start=period_start,
        period_end=period_end,
        posts_ingested=total_ingested,
        posts_per_platform={
            'twitter': ingested.twitter,
            'linkedin': ingested.linkedin,
            'reddit': ingested.reddit,
        },
        posts_per_source={},  # Would aggregate by source
        posts_classified=sum(c.count for c in classifications),
        classification_distribution={c.classification: c.count for c in classifications},
        posts_scored=filter_stats.passed + filter_stats.filtered,
        avg_relevance_score=0,  # Would calculate
        avg_opportunity_score=0,
        posts_filtered=filter_stats.filtered,
        posts_passed_filters=filter_stats.passed,
        filter_pass_rate=filter_stats.passed / total_ingested if total_ingested > 0 else 0,
        filter_rejection_reasons={},  # Would aggregate
        posts_queued=filter_stats.passed,
        posts_expired=0,  # Would calculate
        posts_engaged=total_engaged,
        ingestion_to_engagement_rate=total_engaged / total_ingested if total_ingested > 0 else 0,
    )
```

### Volume Trends

```python
def calculate_volume_trends(
    campaign_id: UUID,
    days: int = 30,
    granularity: str = 'day'
) -> List[dict]:
    """Calculate volume trends over time."""
    
    if granularity == 'hour':
        truncate = "DATE_TRUNC('hour', discovered_at)"
    elif granularity == 'day':
        truncate = "DATE_TRUNC('day', discovered_at)"
    else:
        truncate = "DATE_TRUNC('week', discovered_at)"
    
    return db.query(f"""
        SELECT 
            {truncate} as period,
            COUNT(*) as ingested,
            COUNT(*) FILTER (WHERE status = 'engaged') as engaged,
            COUNT(*) FILTER (WHERE status = 'filtered') as filtered,
            AVG((scores->'relevance'->>'total')::float) as avg_relevance
        FROM discovered_posts
        WHERE campaign_id = %(campaign_id)s
        AND discovered_at > NOW() - INTERVAL '%(days)s days'
        GROUP BY {truncate}
        ORDER BY period
    """, {'campaign_id': campaign_id, 'days': days})
```

## 7.11.3 Source Analytics

### Source Performance Metrics

```python
@dataclass
class SourcePerformanceMetrics:
    source_id: UUID
    source_name: str
    source_type: str
    platform: str
    
    # Volume
    posts_discovered: int
    posts_per_day_avg: float
    
    # Quality
    avg_relevance_score: float
    avg_opportunity_score: float
    high_relevance_rate: float  # % scoring >= 70
    
    # Outcomes
    posts_engaged: int
    engagement_rate: float
    posts_successful: int
    success_rate: float
    
    # Efficiency
    api_calls: int
    posts_per_api_call: float
    cost_per_post: float  # If applicable
    
    # Health
    error_rate: float
    last_success: datetime
    consecutive_failures: int


def calculate_source_performance(
    source_id: UUID,
    days: int = 30
) -> SourcePerformanceMetrics:
    """Calculate performance metrics for a source."""
    
    source = get_source(source_id)
    
    # Volume and quality
    stats = db.query_one("""
        SELECT 
            COUNT(*) as total,
            AVG((scores->'relevance'->>'total')::float) as avg_relevance,
            AVG((scores->'opportunity'->>'total')::float) as avg_opportunity,
            COUNT(*) FILTER (WHERE (scores->'relevance'->>'total')::int >= 70) as high_relevance,
            COUNT(*) FILTER (WHERE status = 'engaged') as engaged,
            COUNT(*) FILTER (WHERE engagement_successful = true) as successful
        FROM discovered_posts
        WHERE source_id = %(source_id)s
        AND discovered_at > NOW() - INTERVAL '%(days)s days'
    """, {'source_id': source_id, 'days': days})
    
    # API stats from ingestion jobs
    api_stats = db.query_one("""
        SELECT 
            COUNT(*) as total_jobs,
            SUM(posts_fetched) as total_posts,
            COUNT(*) FILTER (WHERE status = 'failed') as failed_jobs
        FROM ingestion_jobs
        WHERE source_id = %(source_id)s
        AND created_at > NOW() - INTERVAL '%(days)s days'
    """, {'source_id': source_id, 'days': days})
    
    total = stats.total or 0
    engaged = stats.engaged or 0
    
    return SourcePerformanceMetrics(
        source_id=source_id,
        source_name=source.name,
        source_type=source.source_type,
        platform=source.platform,
        posts_discovered=total,
        posts_per_day_avg=total / days,
        avg_relevance_score=stats.avg_relevance or 0,
        avg_opportunity_score=stats.avg_opportunity or 0,
        high_relevance_rate=stats.high_relevance / total if total > 0 else 0,
        posts_engaged=engaged,
        engagement_rate=engaged / total if total > 0 else 0,
        posts_successful=stats.successful or 0,
        success_rate=stats.successful / engaged if engaged > 0 else 0,
        api_calls=api_stats.total_jobs or 0,
        posts_per_api_call=api_stats.total_posts / api_stats.total_jobs if api_stats.total_jobs else 0,
        cost_per_post=0,  # Would calculate based on API costs
        error_rate=api_stats.failed_jobs / api_stats.total_jobs if api_stats.total_jobs else 0,
        last_success=source.last_successful_fetch,
        consecutive_failures=source.consecutive_failures or 0,
    )
```

### Source Comparison

```python
def compare_sources(campaign_id: UUID, days: int = 30) -> List[dict]:
    """Compare all sources for a campaign."""
    
    sources = get_campaign_sources(campaign_id)
    
    metrics = []
    for source in sources:
        perf = calculate_source_performance(source.id, days)
        metrics.append({
            'source_id': source.id,
            'source_name': source.name,
            'source_type': source.source_type,
            'platform': source.platform,
            'posts_discovered': perf.posts_discovered,
            'avg_relevance': perf.avg_relevance_score,
            'engagement_rate': perf.engagement_rate,
            'success_rate': perf.success_rate,
            'efficiency_score': calculate_source_efficiency_score(perf),
        })
    
    # Sort by efficiency score
    metrics.sort(key=lambda x: x['efficiency_score'], reverse=True)
    
    return metrics


def calculate_source_efficiency_score(metrics: SourcePerformanceMetrics) -> float:
    """Calculate overall efficiency score for source."""
    
    # Weighted combination of quality and outcomes
    score = (
        metrics.avg_relevance_score * 0.25 +
        metrics.avg_opportunity_score * 0.25 +
        (metrics.engagement_rate * 100) * 0.25 +
        (metrics.success_rate * 100) * 0.25
    )
    
    return score
```

### Source Recommendations

```python
def generate_source_recommendations(campaign_id: UUID) -> List[dict]:
    """Generate recommendations for source optimization."""
    
    recommendations = []
    sources = compare_sources(campaign_id)
    
    for source in sources:
        # Low performance sources
        if source['efficiency_score'] < 30:
            recommendations.append({
                'source_id': source['source_id'],
                'type': 'low_performance',
                'severity': 'warning',
                'message': f"Source '{source['source_name']}' has low efficiency score ({source['efficiency_score']:.0f}). Consider disabling or refining.",
                'action': 'review_or_disable',
            })
        
        # High volume, low quality
        if source['posts_discovered'] > 100 and source['avg_relevance'] < 40:
            recommendations.append({
                'source_id': source['source_id'],
                'type': 'high_volume_low_quality',
                'severity': 'info',
                'message': f"Source '{source['source_name']}' produces high volume but low relevance. Consider narrowing query.",
                'action': 'refine_query',
            })
        
        # High quality, low volume
        if source['avg_relevance'] > 70 and source['posts_discovered'] < 10:
            recommendations.append({
                'source_id': source['source_id'],
                'type': 'high_quality_low_volume',
                'severity': 'info',
                'message': f"Source '{source['source_name']}' has high relevance but low volume. Consider broadening or increasing priority.",
                'action': 'expand_query',
            })
    
    return recommendations
```

## 7.11.4 Classification Analytics

### Classification Distribution

```python
def analyze_classification_distribution(
    campaign_id: UUID,
    days: int = 30
) -> dict:
    """Analyze distribution of classifications."""
    
    distribution = db.query("""
        SELECT 
            classification->>'primary' as classification,
            COUNT(*) as total,
            AVG((scores->'relevance'->>'total')::float) as avg_relevance,
            AVG((scores->'opportunity'->>'total')::float) as avg_opportunity,
            COUNT(*) FILTER (WHERE status = 'engaged') as engaged,
            COUNT(*) FILTER (WHERE engagement_successful = true) as successful
        FROM discovered_posts
        WHERE campaign_id = %(campaign_id)s
        AND discovered_at > NOW() - INTERVAL '%(days)s days'
        AND classification IS NOT NULL
        GROUP BY classification->>'primary'
        ORDER BY total DESC
    """, {'campaign_id': campaign_id, 'days': days})
    
    total_posts = sum(c.total for c in distribution)
    
    return {
        'distribution': [
            {
                'classification': c.classification,
                'count': c.total,
                'percentage': c.total / total_posts * 100 if total_posts > 0 else 0,
                'avg_relevance': c.avg_relevance,
                'avg_opportunity': c.avg_opportunity,
                'engagement_rate': c.engaged / c.total * 100 if c.total > 0 else 0,
                'success_rate': c.successful / c.engaged * 100 if c.engaged > 0 else 0,
            }
            for c in distribution
        ],
        'total_posts': total_posts,
    }
```

### Classification Quality

```python
def analyze_classification_quality(
    campaign_id: UUID,
    days: int = 30
) -> dict:
    """Analyze classification quality metrics."""
    
    # Confidence distribution
    confidence_dist = db.query("""
        SELECT 
            CASE 
                WHEN (classification->>'primary_confidence')::int >= 90 THEN '90-100'
                WHEN (classification->>'primary_confidence')::int >= 70 THEN '70-89'
                WHEN (classification->>'primary_confidence')::int >= 50 THEN '50-69'
                ELSE 'below_50'
            END as confidence_bucket,
            COUNT(*) as count
        FROM discovered_posts
        WHERE campaign_id = %(campaign_id)s
        AND discovered_at > NOW() - INTERVAL '%(days)s days'
        AND classification IS NOT NULL
        GROUP BY confidence_bucket
    """, {'campaign_id': campaign_id, 'days': days})
    
    # Method distribution
    method_dist = db.query("""
        SELECT 
            classification->>'method' as method,
            COUNT(*) as count
        FROM discovered_posts
        WHERE campaign_id = %(campaign_id)s
        AND discovered_at > NOW() - INTERVAL '%(days)s days'
        AND classification IS NOT NULL
        GROUP BY classification->>'method'
    """, {'campaign_id': campaign_id, 'days': days})
    
    # Review rate
    review_stats = db.query_one("""
        SELECT 
            COUNT(*) as total,
            COUNT(*) FILTER (WHERE (classification->>'needs_review')::boolean = true) as needs_review
        FROM discovered_posts
        WHERE campaign_id = %(campaign_id)s
        AND discovered_at > NOW() - INTERVAL '%(days)s days'
        AND classification IS NOT NULL
    """, {'campaign_id': campaign_id, 'days': days})
    
    return {
        'confidence_distribution': {c.confidence_bucket: c.count for c in confidence_dist},
        'method_distribution': {m.method: m.count for m in method_dist},
        'review_rate': review_stats.needs_review / review_stats.total if review_stats.total > 0 else 0,
    }
```

## 7.11.5 Scoring Analytics

### Score Distribution Analysis

```python
def analyze_score_distributions(
    campaign_id: UUID,
    days: int = 30
) -> dict:
    """Analyze score distributions."""
    
    # Relevance distribution
    relevance_dist = db.query("""
        SELECT 
            CASE 
                WHEN (scores->'relevance'->>'total')::int >= 80 THEN 'excellent'
                WHEN (scores->'relevance'->>'total')::int >= 60 THEN 'high'
                WHEN (scores->'relevance'->>'total')::int >= 40 THEN 'medium'
                WHEN (scores->'relevance'->>'total')::int >= 20 THEN 'low'
                ELSE 'minimal'
            END as tier,
            COUNT(*) as count,
            AVG((scores->'relevance'->>'total')::float) as avg_score
        FROM discovered_posts
        WHERE campaign_id = %(campaign_id)s
        AND discovered_at > NOW() - INTERVAL '%(days)s days'
        AND scores->'relevance' IS NOT NULL
        GROUP BY tier
    """, {'campaign_id': campaign_id, 'days': days})
    
    # Opportunity distribution
    opportunity_dist = db.query("""
        SELECT 
            CASE 
                WHEN (scores->'opportunity'->>'total')::int >= 85 THEN 'exceptional'
                WHEN (scores->'opportunity'->>'total')::int >= 70 THEN 'high'
                WHEN (scores->'opportunity'->>'total')::int >= 55 THEN 'good'
                WHEN (scores->'opportunity'->>'total')::int >= 40 THEN 'moderate'
                ELSE 'low'
            END as tier,
            COUNT(*) as count
        FROM discovered_posts
        WHERE campaign_id = %(campaign_id)s
        AND discovered_at > NOW() - INTERVAL '%(days)s days'
        AND scores->'opportunity' IS NOT NULL
        GROUP BY tier
    """, {'campaign_id': campaign_id, 'days': days})
    
    # Combined analysis
    combined = db.query_one("""
        SELECT 
            AVG((scores->'relevance'->>'total')::float) as avg_relevance,
            AVG((scores->'opportunity'->>'total')::float) as avg_opportunity,
            CORR(
                (scores->'relevance'->>'total')::float,
                (scores->'opportunity'->>'total')::float
            ) as relevance_opportunity_correlation
        FROM discovered_posts
        WHERE campaign_id = %(campaign_id)s
        AND discovered_at > NOW() - INTERVAL '%(days)s days'
        AND scores->'relevance' IS NOT NULL
        AND scores->'opportunity' IS NOT NULL
    """, {'campaign_id': campaign_id, 'days': days})
    
    return {
        'relevance_distribution': {r.tier: r.count for r in relevance_dist},
        'opportunity_distribution': {o.tier: o.count for o in opportunity_dist},
        'avg_relevance': combined.avg_relevance,
        'avg_opportunity': combined.avg_opportunity,
        'relevance_opportunity_correlation': combined.relevance_opportunity_correlation,
    }
```

### Score Component Analysis

```python
def analyze_score_components(
    campaign_id: UUID,
    score_type: str,  # 'relevance' or 'opportunity'
    days: int = 30
) -> dict:
    """Analyze contribution of score components."""
    
    if score_type == 'relevance':
        components = ['keyword', 'classification', 'context', 'author']
    else:
        components = ['engagement', 'author', 'timing', 'conversation', 'strategic']
    
    results = {}
    
    for component in components:
        stats = db.query_one(f"""
            SELECT 
                AVG((scores->'{score_type}'->'{component}'->>'total')::float) as avg,
                MIN((scores->'{score_type}'->'{component}'->>'total')::float) as min,
                MAX((scores->'{score_type}'->'{component}'->>'total')::float) as max,
                STDDEV((scores->'{score_type}'->'{component}'->>'total')::float) as stddev
            FROM discovered_posts
            WHERE campaign_id = %(campaign_id)s
            AND discovered_at > NOW() - INTERVAL '%(days)s days'
            AND scores->'{score_type}'->'{component}' IS NOT NULL
        """, {'campaign_id': campaign_id, 'days': days})
        
        results[component] = {
            'avg': stats.avg or 0,
            'min': stats.min or 0,
            'max': stats.max or 0,
            'stddev': stats.stddev or 0,
        }
    
    return results
```

## 7.11.6 Filter Analytics

### Filter Effectiveness

```python
def analyze_filter_effectiveness(
    campaign_id: UUID,
    days: int = 30
) -> dict:
    """Analyze filtering effectiveness."""
    
    # Overall filter stats
    overall = db.query_one("""
        SELECT 
            COUNT(*) as total,
            COUNT(*) FILTER (WHERE status = 'filtered') as filtered,
            COUNT(*) FILTER (WHERE status NOT IN ('filtered', 'pending_classification', 'pending_scoring')) as passed
        FROM discovered_posts
        WHERE campaign_id = %(campaign_id)s
        AND discovered_at > NOW() - INTERVAL '%(days)s days'
    """, {'campaign_id': campaign_id, 'days': days})
    
    # By filter reason
    by_reason = db.query("""
        SELECT 
            filter_reason,
            COUNT(*) as count
        FROM discovered_posts
        WHERE campaign_id = %(campaign_id)s
        AND discovered_at > NOW() - INTERVAL '%(days)s days'
        AND status = 'filtered'
        GROUP BY filter_reason
        ORDER BY count DESC
    """, {'campaign_id': campaign_id, 'days': days})
    
    # False positive analysis (filtered posts that might have been good)
    potential_false_positives = db.query_one("""
        SELECT COUNT(*) as count
        FROM discovered_posts
        WHERE campaign_id = %(campaign_id)s
        AND discovered_at > NOW() - INTERVAL '%(days)s days'
        AND status = 'filtered'
        AND (scores->'relevance'->>'total')::int >= 60
        AND (scores->'opportunity'->>'total')::int >= 50
    """, {'campaign_id': campaign_id, 'days': days})
    
    total = overall.total or 0
    filtered = overall.filtered or 0
    
    return {
        'total_processed': total,
        'total_filtered': filtered,
        'total_passed': overall.passed or 0,
        'filter_rate': filtered / total if total > 0 else 0,
        'pass_rate': overall.passed / total if total > 0 else 0,
        'by_reason': {r.filter_reason: r.count for r in by_reason},
        'potential_false_positives': potential_false_positives.count or 0,
        'false_positive_rate': potential_false_positives.count / filtered if filtered > 0 else 0,
    }
```

### Threshold Analysis

```python
def analyze_threshold_impact(
    campaign_id: UUID,
    days: int = 30
) -> dict:
    """Analyze impact of current thresholds."""
    
    current_thresholds = get_campaign_thresholds(campaign_id)
    
    # Simulate different thresholds
    simulations = []
    
    for relevance_threshold in [30, 40, 50, 60]:
        for opportunity_threshold in [20, 30, 40, 50]:
            passed = db.query_scalar("""
                SELECT COUNT(*) FROM discovered_posts
                WHERE campaign_id = %(campaign_id)s
                AND discovered_at > NOW() - INTERVAL '%(days)s days'
                AND (scores->'relevance'->>'total')::int >= %(rel)s
                AND (scores->'opportunity'->>'total')::int >= %(opp)s
            """, {
                'campaign_id': campaign_id,
                'days': days,
                'rel': relevance_threshold,
                'opp': opportunity_threshold,
            })
            
            simulations.append({
                'relevance_threshold': relevance_threshold,
                'opportunity_threshold': opportunity_threshold,
                'posts_passed': passed,
                'is_current': (
                    relevance_threshold == current_thresholds.min_relevance_score and
                    opportunity_threshold == current_thresholds.min_opportunity_score
                ),
            })
    
    return {
        'current_thresholds': {
            'relevance': current_thresholds.min_relevance_score,
            'opportunity': current_thresholds.min_opportunity_score,
        },
        'simulations': simulations,
    }
```

## 7.11.7 Engagement Analytics

### Engagement Outcomes

```python
def analyze_engagement_outcomes(
    campaign_id: UUID,
    days: int = 30
) -> dict:
    """Analyze engagement outcomes."""
    
    outcomes = db.query("""
        SELECT 
            engagement_outcome,
            COUNT(*) as count,
            AVG((scores->'relevance'->>'total')::float) as avg_relevance,
            AVG((scores->'opportunity'->>'total')::float) as avg_opportunity,
            AVG(response_engagement) as avg_response_engagement
        FROM discovered_posts
        WHERE campaign_id = %(campaign_id)s
        AND discovered_at > NOW() - INTERVAL '%(days)s days'
        AND status = 'engaged'
        GROUP BY engagement_outcome
    """, {'campaign_id': campaign_id, 'days': days})
    
    # Success by classification
    by_classification = db.query("""
        SELECT 
            classification->>'primary' as classification,
            COUNT(*) as total_engaged,
            COUNT(*) FILTER (WHERE engagement_successful = true) as successful,
            AVG(response_engagement) as avg_response_engagement
        FROM discovered_posts
        WHERE campaign_id = %(campaign_id)s
        AND discovered_at > NOW() - INTERVAL '%(days)s days'
        AND status = 'engaged'
        GROUP BY classification->>'primary'
        ORDER BY total_engaged DESC
    """, {'campaign_id': campaign_id, 'days': days})
    
    # Success by persona
    by_persona = db.query("""
        SELECT 
            engagement_persona as persona,
            COUNT(*) as total_engaged,
            COUNT(*) FILTER (WHERE engagement_successful = true) as successful,
            AVG(response_engagement) as avg_response_engagement
        FROM discovered_posts
        WHERE campaign_id = %(campaign_id)s
        AND discovered_at > NOW() - INTERVAL '%(days)s days'
        AND status = 'engaged'
        AND engagement_persona IS NOT NULL
        GROUP BY engagement_persona
    """, {'campaign_id': campaign_id, 'days': days})
    
    return {
        'outcomes': {o.engagement_outcome: o.count for o in outcomes},
        'by_classification': [
            {
                'classification': c.classification,
                'engaged': c.total_engaged,
                'successful': c.successful,
                'success_rate': c.successful / c.total_engaged if c.total_engaged > 0 else 0,
                'avg_response_engagement': c.avg_response_engagement,
            }
            for c in by_classification
        ],
        'by_persona': [
            {
                'persona': p.persona,
                'engaged': p.total_engaged,
                'successful': p.successful,
                'success_rate': p.successful / p.total_engaged if p.total_engaged > 0 else 0,
                'avg_response_engagement': p.avg_response_engagement,
            }
            for p in by_persona
        ],
    }
```

### Engagement Timing Analysis

```python
def analyze_engagement_timing(
    campaign_id: UUID,
    days: int = 30
) -> dict:
    """Analyze timing impact on engagement success."""
    
    # Success by post age at engagement
    by_age = db.query("""
        SELECT 
            CASE 
                WHEN EXTRACT(EPOCH FROM (engaged_at - created_at)) / 3600 < 1 THEN 'under_1h'
                WHEN EXTRACT(EPOCH FROM (engaged_at - created_at)) / 3600 < 4 THEN '1-4h'
                WHEN EXTRACT(EPOCH FROM (engaged_at - created_at)) / 3600 < 12 THEN '4-12h'
                WHEN EXTRACT(EPOCH FROM (engaged_at - created_at)) / 3600 < 24 THEN '12-24h'
                ELSE 'over_24h'
            END as age_bucket,
            COUNT(*) as total,
            COUNT(*) FILTER (WHERE engagement_successful = true) as successful,
            AVG(response_engagement) as avg_response_engagement
        FROM discovered_posts
        WHERE campaign_id = %(campaign_id)s
        AND discovered_at > NOW() - INTERVAL '%(days)s days'
        AND status = 'engaged'
        GROUP BY age_bucket
        ORDER BY 
            CASE age_bucket
                WHEN 'under_1h' THEN 1
                WHEN '1-4h' THEN 2
                WHEN '4-12h' THEN 3
                WHEN '12-24h' THEN 4
                ELSE 5
            END
    """, {'campaign_id': campaign_id, 'days': days})
    
    return {
        'by_post_age': [
            {
                'age_bucket': a.age_bucket,
                'total': a.total,
                'successful': a.successful,
                'success_rate': a.successful / a.total if a.total > 0 else 0,
                'avg_response_engagement': a.avg_response_engagement,
            }
            for a in by_age
        ],
    }
```

## 7.11.8 Author Analytics

### Author Performance

```python
def analyze_author_engagement(
    campaign_id: UUID,
    days: int = 30
) -> dict:
    """Analyze engagement performance by author characteristics."""
    
    # By author influence tier
    by_influence = db.query("""
        SELECT 
            da.influence_tier,
            COUNT(*) as total_engaged,
            COUNT(*) FILTER (WHERE dp.engagement_successful = true) as successful,
            AVG(dp.response_engagement) as avg_response_engagement
        FROM discovered_posts dp
        JOIN discovered_authors da ON da.id = dp.author_id
        WHERE dp.campaign_id = %(campaign_id)s
        AND dp.discovered_at > NOW() - INTERVAL '%(days)s days'
        AND dp.status = 'engaged'
        GROUP BY da.influence_tier
    """, {'campaign_id': campaign_id, 'days': days})
    
    # By author relevance
    by_relevance = db.query("""
        SELECT 
            da.is_target_audience,
            COUNT(*) as total_engaged,
            COUNT(*) FILTER (WHERE dp.engagement_successful = true) as successful,
            AVG(dp.response_engagement) as avg_response_engagement
        FROM discovered_posts dp
        JOIN discovered_authors da ON da.id = dp.author_id
        WHERE dp.campaign_id = %(campaign_id)s
        AND dp.discovered_at > NOW() - INTERVAL '%(days)s days'
        AND dp.status = 'engaged'
        GROUP BY da.is_target_audience
    """, {'campaign_id': campaign_id, 'days': days})
    
    # Top engaged authors
    top_authors = db.query("""
        SELECT 
            da.handle,
            da.platform,
            da.influence_tier,
            da.is_target_audience,
            COUNT(*) as engagements,
            COUNT(*) FILTER (WHERE dp.engagement_successful = true) as successful,
            SUM(dp.response_engagement) as total_response_engagement
        FROM discovered_posts dp
        JOIN discovered_authors da ON da.id = dp.author_id
        WHERE dp.campaign_id = %(campaign_id)s
        AND dp.discovered_at > NOW() - INTERVAL '%(days)s days'
        AND dp.status = 'engaged'
        GROUP BY da.id, da.handle, da.platform, da.influence_tier, da.is_target_audience
        ORDER BY engagements DESC
        LIMIT 20
    """, {'campaign_id': campaign_id, 'days': days})
    
    return {
        'by_influence_tier': {
            i.influence_tier: {
                'engaged': i.total_engaged,
                'successful': i.successful,
                'success_rate': i.successful / i.total_engaged if i.total_engaged > 0 else 0,
            }
            for i in by_influence
        },
        'target_audience_performance': {
            r.is_target_audience: {
                'engaged': r.total_engaged,
                'successful': r.successful,
                'success_rate': r.successful / r.total_engaged if r.total_engaged > 0 else 0,
            }
            for r in by_relevance
        },
        'top_authors': [
            {
                'handle': a.handle,
                'platform': a.platform,
                'influence_tier': a.influence_tier,
                'engagements': a.engagements,
                'success_rate': a.successful / a.engagements if a.engagements > 0 else 0,
            }
            for a in top_authors
        ],
    }
```

## 7.11.9 Dashboard and Reporting

### Executive Dashboard Metrics

```python
def get_executive_dashboard(
    campaign_id: UUID,
    days: int = 30
) -> dict:
    """Get high-level metrics for executive dashboard."""
    
    current_period = calculate_pipeline_volume(
        campaign_id,
        datetime.now(timezone.utc) - timedelta(days=days),
        datetime.now(timezone.utc)
    )
    
    previous_period = calculate_pipeline_volume(
        campaign_id,
        datetime.now(timezone.utc) - timedelta(days=days*2),
        datetime.now(timezone.utc) - timedelta(days=days)
    )
    
    engagement_outcomes = analyze_engagement_outcomes(campaign_id, days)
    
    total_engaged = current_period.posts_engaged
    total_successful = sum(
        c['successful'] for c in engagement_outcomes['by_classification']
    )
    
    return {
        'summary': {
            'posts_discovered': current_period.posts_ingested,
            'posts_engaged': total_engaged,
            'engagement_success_rate': total_successful / total_engaged if total_engaged > 0 else 0,
            'discovery_to_engagement_rate': current_period.ingestion_to_engagement_rate,
        },
        'trends': {
            'discovery_change': (
                (current_period.posts_ingested - previous_period.posts_ingested) / 
                previous_period.posts_ingested if previous_period.posts_ingested > 0 else 0
            ),
            'engagement_change': (
                (current_period.posts_engaged - previous_period.posts_engaged) /
                previous_period.posts_engaged if previous_period.posts_engaged > 0 else 0
            ),
        },
        'top_performing_classifications': sorted(
            engagement_outcomes['by_classification'],
            key=lambda x: x['success_rate'],
            reverse=True
        )[:5],
    }
```

### Automated Reports

```python
async def generate_weekly_discovery_report(campaign_id: UUID) -> dict:
    """Generate weekly discovery report."""
    
    report = {
        'campaign_id': campaign_id,
        'period': 'weekly',
        'generated_at': datetime.now(timezone.utc).isoformat(),
        
        'volume': calculate_pipeline_volume(
            campaign_id,
            datetime.now(timezone.utc) - timedelta(days=7),
            datetime.now(timezone.utc)
        ).__dict__,
        
        'source_performance': compare_sources(campaign_id, days=7),
        
        'classification_analysis': analyze_classification_distribution(campaign_id, days=7),
        
        'score_analysis': analyze_score_distributions(campaign_id, days=7),
        
        'filter_analysis': analyze_filter_effectiveness(campaign_id, days=7),
        
        'engagement_analysis': analyze_engagement_outcomes(campaign_id, days=7),
        
        'recommendations': generate_source_recommendations(campaign_id),
    }
    
    return report
```

## 7.11.10 Analytics API

### API Endpoints

```python
@app.get("/api/v1/campaigns/{campaign_id}/analytics/volume")
async def get_volume_analytics(
    campaign_id: UUID,
    days: int = 30,
    granularity: str = 'day'
):
    """Get volume analytics."""
    
    return {
        'current': calculate_pipeline_volume(
            campaign_id,
            datetime.now(timezone.utc) - timedelta(days=days),
            datetime.now(timezone.utc)
        ).__dict__,
        'trends': calculate_volume_trends(campaign_id, days, granularity),
    }


@app.get("/api/v1/campaigns/{campaign_id}/analytics/sources")
async def get_source_analytics(campaign_id: UUID, days: int = 30):
    """Get source analytics."""
    
    return {
        'sources': compare_sources(campaign_id, days),
        'recommendations': generate_source_recommendations(campaign_id),
    }


@app.get("/api/v1/campaigns/{campaign_id}/analytics/engagement")
async def get_engagement_analytics(campaign_id: UUID, days: int = 30):
    """Get engagement analytics."""
    
    return {
        'outcomes': analyze_engagement_outcomes(campaign_id, days),
        'timing': analyze_engagement_timing(campaign_id, days),
        'authors': analyze_author_engagement(campaign_id, days),
    }


@app.get("/api/v1/campaigns/{campaign_id}/analytics/dashboard")
async def get_dashboard(campaign_id: UUID, days: int = 30):
    """Get executive dashboard."""
    
    return get_executive_dashboard(campaign_id, days)
```

## 7.11.11 Implementation Guidance for Neoclaw

### Implementation Order

1. **Build volume analytics**
   - Pipeline volume calculation
   - Trend analysis

2. **Build source analytics**
   - Source performance metrics
   - Source comparison

3. **Build scoring analytics**
   - Score distributions
   - Component analysis

4. **Build engagement analytics**
   - Outcome analysis
   - Timing analysis

5. **Build dashboard**
   - Executive summary
   - Key metrics

6. **Implement API**
   - Analytics endpoints

7. **Add automated reporting**
   - Weekly reports
   - Alerting

### Testing Checklist

- [ ] Volume calculations accuracy
- [ ] Source metrics accuracy
- [ ] Score distribution accuracy
- [ ] Engagement outcome tracking
- [ ] Dashboard data consistency
- [ ] Report generation

---

**END OF SECTION 7.11**

Section 7.12 continues with Implementation Summary specification.
-e 


# SECTION 7.12: IMPLEMENTATION SUMMARY

## 7.12.1 Complete System Overview

### Part 7 Architecture Recap

Content Discovery is a multi-stage pipeline that transforms raw social media content into prioritized engagement opportunities:

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                         CONTENT DISCOVERY PIPELINE                                  │
│                                                                                     │
│  ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐ │
│  │ SOURCE  │   │  FEED   │   │ CONTENT │   │ SCORING │   │FILTERING│   │  QUEUE  │ │
│  │ CONFIG  │──▶│INGESTION│──▶│CLASSIF. │──▶│         │──▶│         │──▶│  MGMT   │ │
│  │         │   │         │   │         │   │         │   │         │   │         │ │
│  │ 7.1     │   │  7.2    │   │  7.3    │   │ 7.4/7.5 │   │  7.7    │   │  7.8    │ │
│  └─────────┘   └─────────┘   └─────────┘   └─────────┘   └─────────┘   └─────────┘ │
│                                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐│
│  │                          SUPPORTING SYSTEMS                                     ││
│  │  ┌───────────┐   ┌───────────┐   ┌───────────┐   ┌───────────┐                 ││
│  │  │  AUTHOR   │   │ PLATFORM  │   │ REAL-TIME │   │ ANALYTICS │                 ││
│  │  │  EVAL     │   │ SPECIFIC  │   │PROCESSING │   │           │                 ││
│  │  │   7.6     │   │   7.9     │   │   7.10    │   │   7.11    │                 ││
│  │  └───────────┘   └───────────┘   └───────────┘   └───────────┘                 ││
│  └─────────────────────────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────────────────────┘
```

### Section Summary

| Section | Purpose | Key Outputs |
|---------|---------|-------------|
| 7.0 | Overview | Pipeline architecture, terminology, design principles |
| 7.1 | Source Configuration | Source types, data structures, management |
| 7.2 | Feed Ingestion | API integration, parsing, normalization, deduplication |
| 7.3 | Content Classification | Taxonomy, LLM/rules classifiers, pipeline |
| 7.4 | Relevance Scoring | Keyword/classification/context/author signals |
| 7.5 | Opportunity Detection | Engagement/author/timing/conversation signals |
| 7.6 | Author Evaluation | Quality/influence/relevance/risk assessment |
| 7.7 | Filtering & Thresholds | Filter pipeline, safety, business rules |
| 7.8 | Prioritization | Priority scoring, queue management |
| 7.9 | Platform-Specific | Twitter/LinkedIn/Reddit/Discord details |
| 7.10 | Real-Time Processing | Triggers, fast processing, notifications |
| 7.11 | Analytics | Volume/source/engagement metrics |

## 7.12.2 Data Flow Summary

### Post Lifecycle

```
1. SOURCE CREATION
   └── Configure sources (keywords, accounts, communities)
   
2. INGESTION
   ├── Poll sources on schedule
   ├── Fetch from platform APIs
   ├── Parse and normalize responses
   └── Deduplicate and store
   
3. CLASSIFICATION
   ├── Pre-filter obvious rejects
   ├── Run rules-based classifier
   ├── Run LLM classifier (if needed)
   └── Store classification with confidence
   
4. RELEVANCE SCORING
   ├── Score keyword matches (tiers 1-3)
   ├── Score classification alignment
   ├── Score context (platform, community)
   ├── Score author relevance
   └── Combine and normalize (0-100)
   
5. OPPORTUNITY SCORING
   ├── Score engagement metrics
   ├── Score author influence
   ├── Score timing/freshness
   ├── Score conversation state
   ├── Score strategic alignment
   └── Combine and normalize (0-100)
   
6. AUTHOR EVALUATION
   ├── Assess account quality
   ├── Calculate influence score
   ├── Determine relevance
   ├── Track relationship
   ├── Assess risk
   └── Calculate author factor
   
7. FILTERING
   ├── Apply quality filters
   ├── Apply safety filters
   ├── Apply business filters
   ├── Apply recency filters
   └── Apply capacity filters
   
8. PRIORITIZATION
   ├── Calculate priority score
   ├── Apply time decay
   ├── Apply boost rules
   └── Add to priority queue
   
9. ENGAGEMENT
   ├── Fetch from queue
   ├── Generate response
   ├── Execute engagement
   └── Track outcome
```

### Data Transformations

| Stage | Input | Output |
|-------|-------|--------|
| Ingestion | Raw API response | NormalizedPost |
| Classification | NormalizedPost | Post + classification JSONB |
| Relevance | Post + classification | Post + relevance score |
| Opportunity | Post + relevance | Post + opportunity score |
| Author Eval | Author data | AuthorEvaluationResult |
| Filtering | Scored post | Pass/fail + reason |
| Prioritization | Passed post | QueueEntry |

## 7.12.3 Database Schema Summary

### Core Tables

```sql
-- Posts discovered from social platforms
discovered_posts (
    id, platform, platform_post_id,
    content_text, content_hash,
    author_id,
    engagement (likes, replies, shares),
    classification JSONB,
    scores JSONB,
    status,
    source_id,
    ...
)

-- Authors/accounts from platforms  
discovered_authors (
    id, platform, platform_author_id,
    handle, display_name, bio,
    followers_count, following_count,
    quality_score, influence_score, relevance_score,
    author_factor,
    ...
)

-- Configured discovery sources
discovery_sources (
    id, name, source_type, platform,
    config JSONB,
    priority, weight, enabled,
    ...
)

-- Engagement queue
engagement_queue (
    id, post_id, campaign_id,
    priority_score,
    status, expires_at,
    ...
)

-- Source ingestion state
source_ingestion_state (
    source_id,
    last_fetch_at, next_fetch_at,
    cursor, since_id,
    ...
)

-- Author relationships
author_engagements (
    id, author_id, post_id,
    engagement_type,
    author_responded, response_sentiment,
    ...
)
```

### Key Indexes

```sql
-- Discovery queries
CREATE INDEX idx_posts_status ON discovered_posts(status);
CREATE INDEX idx_posts_source ON discovered_posts(source_id, discovered_at);
CREATE INDEX idx_posts_classification ON discovered_posts USING GIN (classification);
CREATE INDEX idx_posts_scores ON discovered_posts USING GIN (scores);

-- Queue queries
CREATE INDEX idx_queue_priority ON engagement_queue(campaign_id, priority_score DESC) 
    WHERE status = 'pending';

-- Author queries
CREATE INDEX idx_authors_platform ON discovered_authors(platform, platform_author_id);
CREATE INDEX idx_authors_score ON discovered_authors(author_score DESC);
```

## 7.12.4 Configuration Summary

### Source Configuration

```python
SOURCE_CONFIG = {
    'keyword_source': {
        'query': 'string',
        'exclude_terms': ['list'],
        'language': 'en',
        'min_followers': 100,
    },
    'account_source': {
        'platform_account_id': 'string',
        'include_replies': True,
        'include_retweets': False,
    },
    'community_source': {
        'community_id': 'string',
        'sort': 'new',
        'min_score': 5,
    },
}
```

### Scoring Configuration

```python
SCORING_CONFIG = {
    'relevance': {
        'keyword_weight': 0.35,
        'classification_weight': 0.30,
        'context_weight': 0.20,
        'author_weight': 0.15,
    },
    'opportunity': {
        'engagement_weight': 0.30,
        'author_weight': 0.20,
        'timing_weight': 0.25,
        'conversation_weight': 0.15,
        'strategic_weight': 0.10,
    },
}
```

### Threshold Configuration

```python
THRESHOLD_CONFIG = {
    'min_relevance_score': 40,
    'min_opportunity_score': 30,
    'min_author_quality_tier': 'poor',
    'max_post_age_hours': 24,
    'max_queue_size': 500,
    'max_daily_engagements': 50,
}
```

### Timing Configuration

```python
TIMING_CONFIG = {
    'polling_intervals': {
        'high_priority': 5,   # minutes
        'medium_priority': 15,
        'low_priority': 30,
    },
    'freshness_half_life': {
        'twitter': 4,   # hours
        'linkedin': 12,
        'reddit': 8,
    },
    'queue_ttl_hours': 6,
}
```

## 7.12.5 Implementation Checklist

### Phase 1: Core Pipeline (Weeks 1-3)

#### Week 1: Data Foundation
- [ ] Create database schema
- [ ] Implement NormalizedPost model
- [ ] Implement NormalizedAuthor model
- [ ] Set up basic API structure

#### Week 2: Ingestion
- [ ] Implement Twitter API client
- [ ] Implement source configuration
- [ ] Build ingestion job scheduler
- [ ] Add response parsing and normalization
- [ ] Implement deduplication
- [ ] Add state management

#### Week 3: Classification
- [ ] Define classification taxonomy
- [ ] Build rules-based classifier
- [ ] Build LLM classifier
- [ ] Implement hybrid classifier
- [ ] Add classification pipeline

### Phase 2: Scoring & Evaluation (Weeks 4-5)

#### Week 4: Scoring
- [ ] Implement keyword scoring
- [ ] Implement classification scoring
- [ ] Implement context scoring
- [ ] Build relevance calculator
- [ ] Implement engagement scoring
- [ ] Implement timing scoring
- [ ] Implement conversation scoring
- [ ] Build opportunity calculator

#### Week 5: Author & Filtering
- [ ] Implement account quality assessment
- [ ] Implement influence scoring
- [ ] Implement relevance assessment
- [ ] Build author evaluator
- [ ] Implement filter pipeline
- [ ] Add all filter types
- [ ] Configure thresholds

### Phase 3: Queue & Processing (Weeks 6-7)

#### Week 6: Queue Management
- [ ] Implement priority calculation
- [ ] Build queue data structure
- [ ] Implement queue operations
- [ ] Add capacity management
- [ ] Add expiration handling

#### Week 7: Real-Time & Platform
- [ ] Implement real-time triggers
- [ ] Build notification system
- [ ] Add platform-specific handling
- [ ] Implement Twitter specifics
- [ ] Implement Reddit specifics

### Phase 4: Analytics & Polish (Week 8)

#### Week 8: Analytics & Monitoring
- [ ] Implement volume analytics
- [ ] Implement source analytics
- [ ] Implement engagement analytics
- [ ] Build dashboard API
- [ ] Add Prometheus metrics
- [ ] Set up alerting

## 7.12.6 Testing Strategy

### Unit Testing

**Coverage targets:**
- Scoring functions: 100%
- Filter functions: 100%
- Classification: 90%
- Data transformations: 95%

**Key test cases:**
```python
# Scoring tests
def test_keyword_scoring_tier1():
    content = "How do I implement agent security for my LLM?"
    result = keyword_scorer.score(content)
    assert result.tier1_score > 0
    assert 'agent security' in result.tier1_matches

def test_time_decay():
    now = datetime.now(timezone.utc)
    fresh = calculate_time_factor(now - timedelta(minutes=30), 'twitter')
    old = calculate_time_factor(now - timedelta(hours=24), 'twitter')
    assert fresh > old

# Filter tests
def test_relevance_threshold_filter():
    post = create_test_post(relevance_score=30)
    result = filter_relevance_threshold(post, {'min_relevance_score': 40})
    assert not result.passed
    assert result.reason == 'relevance_below_threshold'
```

### Integration Testing

**Test scenarios:**
1. Full pipeline from ingestion to queue
2. Real-time trigger to notification
3. Source to engagement tracking
4. Classification to scoring to filtering

```python
async def test_full_pipeline():
    # Create source
    source = create_test_source()
    
    # Ingest posts
    posts = await ingest_source(source.id)
    assert len(posts) > 0
    
    # Classify
    for post in posts:
        result = await classify_post(post)
        assert result.primary is not None
    
    # Score
    for post in posts:
        relevance = await calculate_relevance_score(post)
        opportunity = await calculate_opportunity_score(post)
        assert 0 <= relevance.total <= 100
        assert 0 <= opportunity.total <= 100
    
    # Filter
    passed, _ = await filter_posts_batch(posts, campaign_config)
    
    # Queue
    for post in passed:
        entry = await add_to_queue(post, campaign_id)
        assert entry.priority_score > 0
```

### Load Testing

**Test parameters:**
- Posts per second: 100
- Concurrent sources: 50
- Queue operations per second: 500
- Classification calls per second: 20

**Performance targets:**
- Ingestion: < 100ms per post
- Classification: < 500ms per post (rules), < 2s (LLM)
- Scoring: < 50ms per post
- Filtering: < 10ms per post
- Queue operations: < 5ms

### Validation Testing

**Create labeled test set:**
- 100 posts with manual classification
- 100 posts with manual relevance scores
- 100 posts with manual opportunity scores

**Accuracy targets:**
- Classification accuracy: > 85%
- Relevance correlation: > 0.8
- Opportunity correlation: > 0.75

## 7.12.7 Monitoring Setup

### Prometheus Metrics

```python
# Pipeline volume
discovery_posts_ingested = Counter('discovery_posts_ingested_total', 'Posts ingested', ['platform', 'source_type'])
discovery_posts_classified = Counter('discovery_posts_classified_total', 'Posts classified', ['classification'])
discovery_posts_filtered = Counter('discovery_posts_filtered_total', 'Posts filtered', ['reason'])
discovery_posts_queued = Counter('discovery_posts_queued_total', 'Posts queued')
discovery_posts_engaged = Counter('discovery_posts_engaged_total', 'Posts engaged', ['outcome'])

# Scores
discovery_relevance_score = Histogram('discovery_relevance_score', 'Relevance scores', buckets=[10,20,30,40,50,60,70,80,90,100])
discovery_opportunity_score = Histogram('discovery_opportunity_score', 'Opportunity scores', buckets=[10,20,30,40,50,60,70,80,90,100])

# Performance
discovery_ingestion_duration = Histogram('discovery_ingestion_duration_seconds', 'Ingestion duration', ['source_type'])
discovery_classification_duration = Histogram('discovery_classification_duration_seconds', 'Classification duration', ['method'])

# Queue
discovery_queue_size = Gauge('discovery_queue_size', 'Queue size', ['campaign_id'])
discovery_queue_wait_time = Histogram('discovery_queue_wait_time_seconds', 'Queue wait time')

# Errors
discovery_errors = Counter('discovery_errors_total', 'Errors', ['stage', 'error_type'])
```

### Grafana Dashboards

**Dashboard 1: Pipeline Overview**
- Posts ingested (time series)
- Classification distribution (pie chart)
- Filter pass rate (gauge)
- Queue depth (time series)
- Engagement rate (gauge)

**Dashboard 2: Source Performance**
- Posts per source (bar chart)
- Source quality scores (table)
- Source errors (time series)
- API rate limits (gauges)

**Dashboard 3: Scoring & Quality**
- Score distributions (histograms)
- Score trends (time series)
- Classification accuracy (gauge)
- Author quality distribution (pie chart)

**Dashboard 4: Queue & Engagement**
- Queue depth by campaign (time series)
- Priority distribution (histogram)
- Wait time distribution (histogram)
- Engagement outcomes (pie chart)

### Alerting Rules

```yaml
groups:
  - name: discovery
    rules:
      - alert: DiscoveryIngestionStopped
        expr: rate(discovery_posts_ingested_total[15m]) == 0
        for: 15m
        labels:
          severity: critical
        annotations:
          summary: "No posts ingested in 15 minutes"
          
      - alert: DiscoveryHighFilterRate
        expr: rate(discovery_posts_filtered_total[1h]) / rate(discovery_posts_ingested_total[1h]) > 0.95
        for: 1h
        labels:
          severity: warning
        annotations:
          summary: "Over 95% of posts being filtered"
          
      - alert: DiscoveryQueueEmpty
        expr: discovery_queue_size == 0
        for: 30m
        labels:
          severity: warning
        annotations:
          summary: "Engagement queue is empty"
          
      - alert: DiscoveryClassificationErrors
        expr: rate(discovery_errors_total{stage="classification"}[15m]) > 0.1
        for: 15m
        labels:
          severity: warning
        annotations:
          summary: "High classification error rate"
```

## 7.12.8 Deployment Considerations

### Service Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        DISCOVERY SERVICES                        │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │  INGESTION  │  │ PROCESSING  │  │    QUEUE    │            │
│  │   WORKER    │  │   WORKER    │  │   WORKER    │            │
│  │             │  │             │  │             │            │
│  │ - Fetch     │  │ - Classify  │  │ - Fetch     │            │
│  │ - Parse     │  │ - Score     │  │ - Process   │            │
│  │ - Store     │  │ - Filter    │  │ - Complete  │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │  REAL-TIME  │  │   API       │  │  ANALYTICS  │            │
│  │   WORKER    │  │   SERVER    │  │   WORKER    │            │
│  │             │  │             │  │             │            │
│  │ - Triggers  │  │ - REST API  │  │ - Metrics   │            │
│  │ - Notify    │  │ - Dashboard │  │ - Reports   │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Scaling Considerations

**Horizontal scaling:**
- Ingestion workers: Scale by source count
- Processing workers: Scale by post volume
- Queue workers: Scale by engagement rate

**Resource requirements:**
- Ingestion: Low CPU, moderate memory, high network
- Classification (LLM): Moderate CPU, low memory, moderate network
- Scoring: Low CPU, low memory
- Queue: Low CPU, low memory, high database I/O

### Environment Configuration

```bash
# Database
DATABASE_URL=postgresql://user:pass@host:5432/jen

# Redis
REDIS_URL=redis://host:6379

# Platform APIs
TWITTER_BEARER_TOKEN=xxx
REDDIT_CLIENT_ID=xxx
REDDIT_CLIENT_SECRET=xxx
LINKEDIN_CLIENT_ID=xxx
LINKEDIN_CLIENT_SECRET=xxx

# LLM
ANTHROPIC_API_KEY=xxx
CLASSIFICATION_MODEL=claude-3-haiku-20240307

# Configuration
MIN_RELEVANCE_SCORE=40
MIN_OPPORTUNITY_SCORE=30
MAX_QUEUE_SIZE=500
MAX_POST_AGE_HOURS=24

# Feature flags
ENABLE_REALTIME=true
ENABLE_LINKEDIN=false
ENABLE_DISCORD=false
```

## 7.12.9 Common Pitfalls and Solutions

### Pitfall 1: Rate Limit Exhaustion

**Problem:** Platform rate limits exceeded, causing ingestion failures.

**Solution:**
- Track rate limits per endpoint
- Implement proactive throttling (10% buffer)
- Prioritize high-value sources when constrained
- Use budget allocation across sources

### Pitfall 2: Classification Drift

**Problem:** Classification accuracy degrades over time.

**Solution:**
- Monitor classification distribution
- Sample and review classifications regularly
- Track accuracy against human labels
- Retrain/tune prompts periodically

### Pitfall 3: Score Inflation/Deflation

**Problem:** Scores drift high or low, making thresholds ineffective.

**Solution:**
- Monitor score distributions
- Use percentile-based normalization
- Regularly recalibrate against outcomes
- Adjust thresholds based on analytics

### Pitfall 4: Queue Starvation

**Problem:** Queue is empty, no engagement opportunities.

**Solution:**
- Monitor queue depth
- Alert on low queue
- Lower thresholds dynamically
- Add more sources

### Pitfall 5: Over-Engagement

**Problem:** Engaging too frequently with same authors/topics.

**Solution:**
- Enforce author frequency limits
- Track topic diversity
- Implement cooldowns
- Monitor engagement distribution

### Pitfall 6: Stale Content

**Problem:** Engaging with old posts, missing the conversation.

**Solution:**
- Strict age filters
- Priority decay over time
- Queue expiration
- Monitor post age at engagement

### Pitfall 7: Platform API Changes

**Problem:** Platform changes API, breaking ingestion.

**Solution:**
- Monitor API errors
- Alert on parsing failures
- Abstract platform specifics
- Quick iteration on fixes

## 7.12.10 Future Enhancements

### Near-Term (Next Quarter)

1. **ML-based classification:** Train custom classifier on labeled data
2. **Advanced deduplication:** Semantic similarity for near-duplicates
3. **Conversation threading:** Better thread context in scoring
4. **A/B testing:** Test different thresholds and configurations

### Medium-Term (Next 6 Months)

1. **Predictive scoring:** Predict engagement success from features
2. **Automated threshold tuning:** ML-based threshold optimization
3. **Cross-platform identity:** Link same person across platforms
4. **Content clustering:** Group similar content for batch handling

### Long-Term (Next Year)

1. **Proactive discovery:** Find emerging topics before they trend
2. **Relationship prediction:** Predict which authors will become valuable
3. **Competitive intelligence:** Track competitor engagement patterns
4. **Full automation:** End-to-end autonomous discovery and engagement

---

## 7.12.11 Part 7 Conclusion

Part 7: Content Discovery provides the complete specification for discovering, evaluating, and prioritizing social media content for engagement. The system transforms the vast stream of social media posts into a focused queue of high-value opportunities.

**Key achievements:**
- Comprehensive pipeline from ingestion to queue
- Multi-dimensional scoring (relevance + opportunity)
- Flexible filtering with configurable thresholds
- Platform-specific optimizations
- Real-time handling for urgent content
- Full analytics for optimization

**Integration points:**
- **Part 3 (Persona System):** Classification feeds persona selection
- **Part 4 (Context Engine):** Scores inform context retrieval
- **Part 5 (Response Generation):** Queue feeds generation
- **Part 6 (Learning & Adaptation):** Outcomes feed back to scoring

The discovery system is the foundation for all engagement — without quality discovery, even the best response generation cannot succeed.

---

**END OF SECTION 7.12**

**END OF PART 7: CONTENT DISCOVERY**

---

Word count summary:
- Section 7.0: ~7,080 words
- Section 7.1: ~8,420 words  
- Section 7.2: ~9,090 words
- Section 7.3: ~5,720 words
- Section 7.4: ~4,360 words
- Section 7.5: ~5,315 words
- Section 7.6: ~5,280 words
- Section 7.7: ~4,210 words
- Section 7.8: ~3,470 words
- Section 7.9: ~3,160 words
- Section 7.10: ~1,850 words
- Section 7.11: ~4,500 words
- Section 7.12: ~3,200 words

**Part 7 Total: ~65,655 words**
