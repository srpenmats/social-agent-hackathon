# Content Engine

> **Purpose:** Multi-phase content pipeline — the candidate generation backbone for the social engagement agent.
> **Use as:** The orchestration logic that decides what to engage with, how to generate content, and when to deploy it.

---

## Pipeline Architecture

```text
[Signal Detection] → [Relevance Scoring] → [Content Generation] → [Compliance Check] → [Publish/Queue]
      ↑                                            ↓
  [Trend Monitor]                          [Voice Calibration]
      ↑                                            ↓
  [Platform APIs]                          [Brand Guidelines]
```

### Phase 1: Signal Detection

The agent monitors multiple signal sources to identify engagement opportunities.

#### Signal Sources

| Source | What to Monitor | Priority |
|---|---|---|
| **Trending topics** | Platform-native trending sections (X Trending, TikTok For You, IG Explore) | High |
| **Finance conversations** | Keywords: budgeting, credit score, payday, saving, investing, side hustle, rent, bills | High |
| **Cultural moments** | Award shows, album drops, sports events, movie releases, viral moments | Medium-High |
| **Creator activity** | Posts from top creators in finance, lifestyle, comedy with high early engagement | Medium |
| **Competitor mentions** | Mentions of SoFi, NerdWallet, Cash App, Chime, Dave, Earnin, Venmo | Medium |
| **MoneyLion mentions** | Direct mentions, tags, and replies to MoneyLion accounts | Highest |
| **Seasonal triggers** | Tax season, back to school, holiday spending, new year goals, summer travel | Medium |

#### Signal Scoring

Each detected signal gets scored on:

```text
engagement_score = (
    virality_potential × 0.3 +
    brand_relevance × 0.25 +
    timing_freshness × 0.25 +
    audience_alignment × 0.2
)
```

| Factor | How It's Measured |
|---|---|
| **virality_potential** | Current engagement velocity (likes/min, comments/min, shares/min) |
| **brand_relevance** | How naturally MoneyLion's voice fits in this conversation |
| **timing_freshness** | How new is this trend? (< 2 hrs = 1.0, < 6 hrs = 0.7, < 24 hrs = 0.4, > 24 hrs = 0.1) |
| **audience_alignment** | Does this reach MoneyLion's target demo? (18-40, working/middle class, financially aspirational) |

Threshold: Only engage on signals scoring **> 0.6**

---

### Phase 2: Content Mode Classification

Based on the signal, classify the engagement into one of two modes.

#### Mode 1: Cultural Engagement (Brand Awareness)

**Objective:** Increase recognition and brand loyalty through positive sentiment outside direct finance conversations.

**Characteristics:**
- Makes funny, human-sounding comments on viral posts
- Participates in trending formats
- Builds familiarity through repetition and humor
- Feels like a real person, not marketing copy

**Content types:**
- Witty one-liners
- Hot takes
- Self-aware brand humor
- Pop culture references
- Relatable "adulting" observations

**Success metrics:**
- Likes / engagement on comments
- Reply chains generated
- Screenshot shares
- Follower growth
- Brand sentiment (measured via social listening)

#### Mode 2: Finance-Relevant Engagement (Conversion-Oriented)

**Objective:** Drive site traffic and product conversions.

**Characteristics:**
- Engages on posts about budgeting, credit, loans, debt, investing
- Creates short-form educational but entertaining content
- Turns product features into relatable social moments
- Responds to questions at scale

**Content types:**
- Financial tips wrapped in humor
- Myth-busting takes
- "Did you know" style insights
- Empathetic responses to financial struggles
- Subtle product education (never salesy)

**Success metrics:**
- Click-throughs to MoneyLion
- Profile visits
- Branded search volume
- Conversion events (sign-ups, app downloads)

---

### Phase 3: Content Generation

#### Generation Framework

For each engagement opportunity, the agent generates content using this framework:

```text
1. CONTEXT: What is the post/topic about?
2. PLATFORM: Which platform are we on? (loads platform playbook)
3. MODE: Cultural or Finance-Relevant?
4. PILLAR: Which voice pillar fits best? (Live Richly / Share The Secret / Roar More / No Bull$hit)
5. TONE: What's the emotional register? (funny / insightful / empathetic / bold)
6. GENERATE: Produce 3 candidate responses
7. RANK: Score candidates on brand-fit, humor, engagement potential
8. SELECT: Choose the highest-scoring candidate
9. COMPLIANCE: Run through guardrails check
10. PUBLISH: Deploy or queue for review
```

#### Content Templates

##### Template: The One-Liner
- **When:** Viral content, trending topics, high-velocity comment sections
- **Structure:** Single sentence, punchy, quotable
- **Voice pillar:** Roar More / No Bull$hit
- **Example:** "Inflation said 'we're all in this together' and I've never felt more personally attacked."

##### Template: The Hot Take
- **When:** Debates, opinion-driven content, cultural moments
- **Structure:** Bold statement + brief justification
- **Voice pillar:** No Bull$hit / Live Richly
- **Example:** "Hot take: the best financial advice is 'know where your money goes.' Everything else is a footnote."

##### Template: The Relatable Observation
- **When:** Lifestyle content, "adulting" posts, paycheck/payday content
- **Structure:** "When you..." or observation format
- **Voice pillar:** Share The Secret / Live Richly
- **Example:** "The 3 stages of payday: 1) rich 2) bills 3) wait, where did it go?"

##### Template: The Value Drop
- **When:** Finance conversations, credit discussions, money tip threads
- **Structure:** Insight + accessible explanation
- **Voice pillar:** Share The Secret / No Bull$hit
- **Example:** "Credit utilization under 30% is one of the fastest ways to improve your score. It's not about how much credit you have — it's about how little of it you're using."

##### Template: The Self-Aware Brand
- **When:** Someone acknowledges brands in comments, meta-commentary
- **Structure:** Acknowledging we're a brand + being genuinely funny about it
- **Voice pillar:** Roar More / No Bull$hit
- **Example:** "Yes, we're a financial services company in the comments section. No, we will not be making this weird. (Okay, maybe a little.)"

##### Template: The Empathetic Pivot
- **When:** Someone shares financial struggles, stress, or anxiety
- **Structure:** Validation + gentle encouragement (NEVER a product pitch)
- **Voice pillar:** Share The Secret / Live Richly
- **Example:** "The fact that you're even thinking about this means you're further ahead than you realize. One step at a time."

---

### Phase 4: Compliance Check

Before any content is published, it passes through the compliance layer.

```text
compliance_check(content):
    1. banned_words_scan(content)        → REJECT if match
    2. product_claim_check(content)      → REJECT if unqualified claim
    3. financial_advice_check(content)   → REJECT if specific advice
    4. competitor_mention_check(content)  → REJECT if naming competitors
    5. sensitivity_check(content)         → REJECT if inappropriate context
    6. disclaimer_requirement(content)    → FLAG if product mention needs disclaimer
    7. platform_rules_check(content)      → REJECT if violates platform TOS

    return APPROVED / NEEDS_REVIEW / REJECTED
```

See `guardrails/compliance_rails.json` for the full rule set.

---

### Phase 5: Publishing & Queue Management

#### Publish Strategy

| Content Type | Approval Flow | Latency Target |
|---|---|---|
| Cultural engagement (no product mention) | Auto-publish | < 30 min from signal |
| Finance-relevant (no product mention) | Auto-publish | < 1 hr from signal |
| Any content with product mention | Human review queue | < 2 hrs from signal |
| Response to direct MoneyLion mention | Auto-publish (if cultural) or human review (if product) | < 15 min |
| Sensitive topic (layoffs, recession, debt crisis) | Human review required | No time pressure — accuracy > speed |

#### Anti-Spam Rules

| Rule | Threshold |
|---|---|
| Max comments per video/post | 1 (never double-comment) |
| Min time between comments on same platform | 3 minutes |
| Max daily comments per platform | See platform playbook targets |
| Repeat content cooldown | Never reuse exact same comment. Minimum 7 days before similar structure. |
| Self-promotion ratio | Max 10% of all engagement can mention MoneyLion products |

---

## Content Ideation: Proactive Topic Generation

Beyond reactive engagement, the agent proactively identifies content themes.

### Weekly Theme Calendar

| Week Theme | Content Angles |
|---|---|
| **Payday Week** (end of month / bi-weekly) | Payday celebrations, "what I did with my paycheck," budgeting resets |
| **Tax Season** (Jan-Apr) | Tax tips, refund planning, "what are you doing with your refund" |
| **Back to School** (Aug-Sep) | Student budgeting, first apartment, financial independence |
| **Holiday Season** (Nov-Dec) | Gift budgeting, year-end financial review, "new year new money" |
| **Summer** (Jun-Aug) | Travel budgeting, vacation funds, side hustle season |
| **Credit Awareness** (ongoing) | Credit score education, building credit, credit myths |

### Reactive Content Triggers

| Trigger | Content Response |
|---|---|
| Federal Reserve rate decision | Quick explainer on what it means for everyday people |
| Viral "I'm broke" meme | Relatable engagement + subtle value content |
| Celebrity financial news | Hot take that connects back to everyday money |
| Major economic data release | Plain-English translation of what it means |
| Competitor controversy | Never mention them. Instead, post positively about what MoneyLion does. |
| Platform algorithm change | Adapt strategy, don't comment on it publicly |