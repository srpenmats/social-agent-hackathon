# JEN CONTENT DISCOVERY: ENHANCED SCORING FRAMEWORK

## Section 7.4-Enhanced: Four-Dimension Scoring System

This section replaces and enhances the original scoring specification with a rigorous four-dimension framework adapted from production-tested social engagement systems. The enhanced framework adds critical safety mechanisms, angle quality enforcement, and persona clarity checks that prevent Jen from posting generic or inappropriate comments.

---

## 7.4.0 Scoring Component Overview

### What the Scoring Component Is

The Scoring Component is the most consequential component in the entire Jen pipeline. The Content Discovery system's job is to find content—finding too much or too little is a calibration problem that can be corrected over time. The Scoring Component's job is to decide what to do with what was found.

A discovery system that surfaces 200 posts per day and a scoring system that correctly identifies the 15 worth engaging with is a functional pipeline. A discovery system that surfaces 200 posts per day and a scoring system that misclassifies 40 of them—routing sensitive content to auto-post, dropping high-value security discussions, misidentifying persona mode—produces real damage to the brand regardless of how well every other component performs.

Every other component in the pipeline depends on the Scoring Component getting it right:
- The Response Generation Component generates comments on whatever the Scoring Component says to engage with
- The Posting Component posts whatever Response Generation produces
- The human review queue is only as useful as the Scoring Component's ability to correctly identify which content needs human eyes

Get the scoring wrong and the entire pipeline produces the wrong outputs.

### What the Scoring Component Does Not Do

The Scoring Component evaluates content and routes it. It does not:
- Generate comments—that is Response Generation
- Post anything—that is the Posting Component
- Make the final human review decision—it determines which queue that decision happens in

The Scoring Component's output is a routing decision attached to a scored record. It produces no user-facing content. It interacts with no platform APIs. Its entire operation is internal—reading from the discovery queue, evaluating against a defined framework, and writing results to routing queues.

### The Golden Rule

**A comment that could appear on any post does not get posted.**

This rule governs the entire scoring framework. Every dimension evaluation, every termination condition, every routing decision exists to enforce this rule. Content that cannot produce a specific, genuine, non-generic comment is filtered out regardless of how well it scores on other dimensions.

The Golden Rule is not a guideline. It is not a threshold that can be adjusted. It is the foundational principle that separates valuable engagement from noise.

---

## 7.4.1 The Four-Dimension Framework

### Why Four Dimensions

Previous scoring approaches used two dimensions: Relevance (how related to our domain) and Opportunity (how valuable to engage). This was insufficient because:

1. **High relevance + high opportunity can still produce generic comments.** A viral post about "AI agents" with 10K likes is both relevant and opportune—but if there's nothing specific for Jen to say, engaging produces a generic comment that damages the brand.

2. **Risk assessment was mixed into filtering.** Sensitive content was filtered out, but the filtering was binary. There was no mechanism to say "this is worth engaging but needs human review first."

3. **Persona selection happened after scoring.** Whether the content was appropriate for Observer, Advisor, or Connector mode wasn't evaluated—it was guessed later during generation.

The four-dimension framework addresses all three gaps:

| Dimension | What It Measures | Score Range | Termination? |
|-----------|------------------|-------------|--------------|
| **Risk Level** | Can we safely engage with this content? | -3, -1, 0 | Yes (-3 = immediate) |
| **Engagement Potential** | Will our comment be seen by a meaningful audience? | 0, 1, 2, 3 | No |
| **Jen Angle Strength** | Can we write something specific and genuine? | 0, 1, 2, 3 | Yes (0 = immediate) |
| **Persona Clarity** | Can we confidently identify the right persona? | 0, 1, 2 | No (but forces review) |

### Evaluation Order

The dimensions are evaluated in a specific order designed to terminate evaluation as early as possible when content is unsuitable:

```
┌─────────────────────────────────────────────────────────────┐
│  STEP 1: RISK LEVEL                                         │
│  ─────────────────                                          │
│  Evaluate safety, sensitivity, brand risk                   │
│                                                             │
│  Score -3? ──────────────────────────────────────────────┐  │
│     │                                        RED TIER    │  │
│     │                               EVALUATION TERMINATED│  │
│     │                               No comment generated │  │
│     └────────────────────────────────────────────────────┘  │
│                                                             │
│  Score -1? ── Continue, but flag for Yellow-tier review     │
│  Score 0?  ── Continue normally                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 2: ENGAGEMENT POTENTIAL                               │
│  ──────────────────────────                                 │
│  Evaluate timing, velocity, visibility                      │
│                                                             │
│  Score 0-3 ── Continue (no termination, but affects         │
│               composite score and routing priority)         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 3: JEN ANGLE STRENGTH                                 │
│  ──────────────────────────                                 │
│  Evaluate: Can we write something specific?                 │
│                                                             │
│  Score 0? ───────────────────────────────────────────────┐  │
│     │                                   DO NOT ENGAGE    │  │
│     │                               EVALUATION TERMINATED│  │
│     │                       Golden Rule: Nothing to say  │  │
│     └────────────────────────────────────────────────────┘  │
│                                                             │
│  Score 1-3? ── Continue                                     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 4: PERSONA CLARITY                                    │
│  ──────────────────────                                     │
│  Evaluate: Can we confidently select Observer/Advisor/      │
│            Connector?                                       │
│                                                             │
│  Score 0? ── Continue, but force Yellow-tier review         │
│              (human determines persona before generation)   │
│  Score 1-2? ── Continue with determined persona             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 5: COMPOSITE SCORE & ROUTING                          │
│  ─────────────────────────────────                          │
│  Calculate composite score                                  │
│  Apply tier classification                                  │
│  Route to appropriate queue                                 │
└─────────────────────────────────────────────────────────────┘
```

### The Five Possible Outcomes

Every post that enters the Scoring Component receives exactly one of five outcomes:

**Outcome 1 - Engage Immediately (Priority Review)**
- Composite score 7-8, Green tier
- Content is high-value, low-risk, timing window is open
- Target time from discovery to posted comment: under 2 hours
- Route to priority review queue

**Outcome 2 - Engage Standard (Standard Review)**
- Composite score 5-6, Green tier
- Content is worth engaging with but not time-critical
- Target time from discovery to posted comment: under 8 hours
- Route to standard review queue

**Outcome 3 - Pass**
- Composite score 3-4, any tier
- Content does not meet the engagement threshold
- No comment is generated
- Logged for analytics

**Outcome 4 - Do Not Engage**
- Composite score 0-2, any tier, OR
- Jen Angle Strength score of 0 (automatic)
- Content is not worth engaging with
- No comment is generated
- Logged for analytics

**Outcome 5 - Red Tier**
- Risk Level score of -3 (automatic)
- Content is categorically off-limits
- Evaluation terminates immediately
- No comment is generated under any circumstances
- If Gen Digital is mentioned negatively, internal flag added

**Yellow-Tier Override**
- Risk Level score of -1, OR Persona Clarity score of 0
- Does not change the outcome category
- Overrides routing to Yellow-tier review queue regardless of composite score
- Human must review before any comment is generated

---

## 7.4.2 Architectural Principles

Before describing each dimension in detail, establish the principles that govern every decision in the Scoring Component's design.

### Principle 1: Sequential Evaluation, Not Parallel

The four scoring dimensions are evaluated in a specific order, not simultaneously. Risk Level is always evaluated first because a score of -3 terminates evaluation immediately. Evaluating other dimensions on content that is about to be Red-tiered wastes compute and creates a code path where Red-tier content is partially processed before being stopped.

Build the evaluation as a sequential pipeline where each dimension feeds the next and any step can terminate the entire evaluation.

### Principle 2: One Post at a Time, Fully Processed

The Scoring Component does not batch-evaluate posts. It reads one post, completes the full evaluation, writes the result, and only then reads the next post. This ensures that scoring state for any given post is never commingled with another post. It makes bugs easier to reproduce and fixes easier to verify.

### Principle 3: Every Evaluation Decision Is Logged

Not just the final score—every dimension's evaluation. The log for a scored post must contain, for each dimension:
- What inputs were used
- What the evaluation logic produced
- What score was assigned
- Why that score was assigned (specific rationale)

This level of logging is not overhead—it is the data the feedback loop uses to identify whether the scoring framework is calibrated correctly. A scoring system that only logs final scores cannot be improved because you cannot see what led to the final score.

### Principle 4: The Scoring Framework Is Configuration, Not Code

The specific score values, threshold definitions, keyword lists, and routing rules are defined in a configuration layer that can be updated without changing the core evaluation code. When calibration review identifies that a dimension's scoring needs adjustment, that change should be made in configuration, not by modifying evaluation logic.

### Principle 5: Idempotent Evaluation

If the Scoring Component evaluates the same post twice—due to a retry after a write failure, a process restart—the second evaluation must produce the same result as the first. The scoring framework is deterministic: given the same input post and the same configuration, the same score must always be produced.

Never use randomness, timestamps, or external state that changes between evaluations as inputs to scoring logic.

### Principle 6: Fail Loudly, Fail Early

If the Scoring Component cannot evaluate a post—because required fields are missing, because the database is unavailable, because a configuration value is absent—it must log a clear, specific error and stop processing that post. It must not assign a default score, must not make assumptions about missing fields, and must not silently continue with degraded inputs.

A post that cannot be scored correctly is better left in pending_scoring status for retry than incorrectly scored and routed to the wrong queue.

---

## 7.4.3 System Components

The Scoring Component is built from six sub-components:

```
┌─────────────────────────────────────────────────────────────┐
│  SUB-COMPONENT 1: QUEUE READER                              │
│  Reads pending_scoring posts from discovery queue           │
│  Locks post to prevent concurrent processing                │
│  Passes post to Evaluation Engine                           │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  SUB-COMPONENT 2: EVALUATION ENGINE                         │
│  Orchestrates the four dimensions in sequence               │
│  Handles termination conditions                             │
│  Collects results and passes to Calculator                  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  SUB-COMPONENT 3: DIMENSION EVALUATORS (4 total)            │
│  One evaluator per dimension                                │
│  Each receives full post data                               │
│  Each returns score + evaluation metadata                   │
│                                                             │
│  • Risk Level Evaluator → score: -3, -1, or 0               │
│  • Engagement Potential Evaluator → score: 0, 1, 2, or 3    │
│  • Jen Angle Strength Evaluator → score: 0, 1, 2, or 3      │
│  • Persona Clarity Evaluator → score: 0, 1, or 2            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  SUB-COMPONENT 4: COMPOSITE SCORE CALCULATOR                │
│  Receives all four dimension scores                         │
│  Calculates composite score                                 │
│  Enforces termination rules                                 │
│  Determines outcome category                                │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  SUB-COMPONENT 5: TIER CLASSIFIER                           │
│  Applies Green / Yellow / Red classification                │
│  Handles Yellow-tier overrides                              │
│  Determines routing queue and priority                      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  SUB-COMPONENT 6: QUEUE ROUTER                              │
│  Updates discovery record with scoring results              │
│  Writes routing entry to routing queue                      │
│  Updates session metrics                                    │
└─────────────────────────────────────────────────────────────┘
```

Build them in this order. Test each one before building the next.

# Dimension 1: Risk Level Evaluator

## 7.4.4 Risk Level

### What Risk Level Measures

Risk Level measures the sensitivity, compliance, and reputational risk of engaging with this content. It is the only dimension with a negative score and the only dimension that can terminate evaluation entirely.

- **Score 0** means the content is appropriate to engage with from a risk perspective
- **Score -1** means the content requires human review before any comment is posted
- **Score -3** means the content is categorically off-limits

Risk Level is evaluated first because a score of -3 must terminate all further evaluation immediately. The other three dimensions are never evaluated on Red-tier content.

### The Three-Tier System

#### Green Tier (Score 0)

Content is low-risk. None of the Yellow or Red tier signals are present. The content is:
- Lighthearted or professionally technical
- Non-sensitive, non-controversial
- No emotional weight that could make brand engagement inappropriate
- No identity dimensions central to the content
- No health, illness, or medical content
- No political or legal content
- No minors as the primary subject
- No negative Gen Digital association

Green-tier content can proceed through the full pipeline without additional review requirements from a risk perspective.

#### Yellow Tier (Score -1)

Content has elevated sensitivity that requires human judgment before posting. A Yellow-tier flag does not mean "do not engage"—it means "do not engage without human review."

The specific reason for the Yellow flag must be logged and presented to the human reviewer so they can make an informed decision.

**Yellow-tier conditions (any single condition is sufficient):**

| Condition | Description | Example |
|-----------|-------------|---------|
| **Health/Illness Content** | Illness, injury, or health content, even when framed technically | "My company's AI agent crashed because the engineer was out sick for a week" |
| **Emotional Vulnerability** | Grief, loss, major life stress, layoffs | "Just got laid off from my ML engineering job, feeling lost" |
| **Edgy/Transgressive** | Content playing with social norms where misreading could cause offense | Sarcastic takes on "AI taking jobs" |
| **Named Company Negative** | Specific company named in potentially negative context | "OpenAI's agent security is a joke" |
| **Power Imbalance** | Workplace harassment, discrimination, abuse of power dynamics | "My manager made me work 80 hours on this agent deployment" |
| **Creator Controversy** | Creator has known controversy history | Influential figure with past problematic statements |
| **Bold Angle Risk** | Best Jen comment would be bold/edgy in a way that could be misread | Humor that's funny to most but could offend some |
| **Security Incident Discussion** | Active discussion of breaches, vulnerabilities, exploits | "Anyone else see that agent jailbreak going around?" |
| **Regulatory/Compliance** | Content touching on AI regulation, legal compliance | "Does this agent violate GDPR?" |

#### Red Tier (Score -3)

Content is categorically off-limits. A score of -3 is absolute and non-negotiable. Evaluation terminates immediately. No comment is ever generated.

**Red-tier conditions (any single condition is sufficient):**

| Condition | Description | Never Engage |
|-----------|-------------|--------------|
| **Death** | Death of any person in any framing | Real deaths, not metaphorical "RIP my server" |
| **Active Mental Health Crisis** | Self-harm, suicidal ideation, eating disorders, substance abuse crisis | Active crisis, not educational discussion |
| **Genuine Trauma** | Abuse, assault, violence, traumatic experiences | Personal trauma narratives |
| **Contested Political Content** | Political figures, elections, policy controversy, partisan issues as primary subject | Election discussions, political AI regulation debates |
| **Active News Events** | Breaking news, disasters, crises, rapidly developing situations | Data breaches in progress, major incidents |
| **Minors as Primary Subject** | Children featured prominently in content | Young people's social media posts about AI |
| **Exploitation Risk** | Financial hardship content where brand comment would appear opportunistic | "I can't afford to pay my cloud bills anymore" |
| **Gen Digital Negative** | Gen Digital or its products discussed negatively | Complaints, criticism, negative experiences |
| **Competitor Legal Risk** | Competitor mentioned in way that could create legal exposure | Comparative claims, false statements |
| **Criminal Activity** | Discussion of illegal activities, hacking (malicious), fraud | "How to bypass agent security for..." |
| **Ongoing Litigation** | Active lawsuits, legal proceedings involving tech companies | "Did you see the lawsuit against..." |

### The Red-Tier Override Is Absolute

The Red-tier override cannot be softened, conditioned, or made configurable. Build it as a hard stop that fires before composite score calculation begins. If a post's Risk Level scores -3, the composite score is never calculated. The post is immediately routed to the Red-tier log.

This is not a threshold. This is not a guideline. This is a categorical prohibition.

### Risk Evaluation Process

The Risk Level evaluator applies checks in this order, stopping at the first Red-tier condition found:

```
Step 1: Red-Tier Check
────────────────────────
Evaluate against EVERY Red-tier condition.
Check content text, hashtags, author, and top existing comments.

If ANY Red-tier condition is confirmed:
  → Assign score -3
  → Log specific condition and signal that triggered it
  → Set red_tier_terminated = true
  → TERMINATE EVALUATION
  → Pass result directly to Tier Classifier

Step 2: Yellow-Tier Check
────────────────────────
If no Red-tier condition found:
Evaluate against EVERY Yellow-tier condition.

If ANY Yellow-tier condition found:
  → Assign score -1
  → Log EVERY Yellow-tier condition found (may be multiple)
  → Set yellow_tier_flag = true
  → CONTINUE EVALUATION (Yellow does not terminate)

Step 3: Green-Tier Confirmation
────────────────────────
If no Red or Yellow conditions found:
  → Assign score 0
  → Log confirmation that no risk signals were found
  → CONTINUE EVALUATION
```

### Inputs Used

```
content_text              Full text of the post
hashtags                  All hashtags on the post
platform                  Which platform (affects risk thresholds)
author_handle             Author's username
author_bio                Author's bio (for controversy check)
author_follower_count     High-follower controversial creators = higher risk
classification            Post classification (some types inherently higher risk)
top_existing_comments     Comment section tone is a risk signal
keyword_matches           Gen Digital-specific matches require extra scrutiny
mentioned_entities        Companies, people, products mentioned
```

### Score Rationale Examples

The `score_rationale` must be specific to the content being evaluated. Generic rationales provide no calibration value.

**Score 0 (Green) rationale example:**
```
"Score 0 (Green) - Technical discussion about LangChain agent architecture.
No death/tragedy signals. No mental health crisis signals. No political 
content. No named company in negative context. No minor as primary subject. 
No Gen Digital negative mention. Creator has no flagged controversy history. 
Content is appropriate for engagement."
```

**Score -1 (Yellow) rationale example:**
```
"Score -1 (Yellow) - Discussion of recent API security incident. Content 
involves active security vulnerability discussion even though framing is 
educational. Human review required before comment is generated. 
Specific Yellow flag: security_incident_discussion.
Additional flag: named_company_negative (references 'OpenAI's security gaps')."
```

**Score -3 (Red) rationale example:**
```
"Score -3 (Red) - Content involves active news event. Creator is posting 
updates about an ongoing data breach affecting their company. Brand 
engagement is categorically inappropriate. EVALUATION TERMINATED.
Red flag: active_news_event.
Additional context: breach_in_progress, company_named."
```

### Edge Cases

**"RIP my deployment" and similar metaphorical language**

Metaphorical use of death-adjacent language in clearly technical contexts is common. The Risk Level evaluator must distinguish between:
- Metaphorical: "RIP my production server after that update" → NOT Red-tier
- Actual: "RIP [person's name], they were a great engineer" → Red-tier

Key signal: Is the death language applied to a person or to a technical concept? When genuinely ambiguous, default to Yellow-tier rather than Red-tier—human review will make the final determination.

**Security discussions: educational vs. active**

An engineer discussing how to secure agents in general is different from someone discussing an ongoing breach. The former may be Yellow-tier (security topic). The latter is Red-tier (active news event). Signals:
- Past tense vs. present tense
- Educational framing vs. incident response framing
- "Here's how to prevent..." vs. "We're seeing attacks right now..."

When ambiguous, default to Yellow-tier.

**Gen Digital mentioned in passing**

If Gen Digital is mentioned briefly and neutrally in content that is primarily about something else—"I'm evaluating Gen Digital's Agent Trust Hub alongside other solutions"—this is NOT Red-tier. It's a high-priority engagement opportunity.

Red-tier Gen Digital mentions are content where Gen Digital is the primary negative subject—complaints, bad experiences, criticism.

**Competitor criticism**

Content criticizing a competitor (OpenAI, LangChain, etc.) is tricky:
- If Jen comments, it could appear like piling on
- If the criticism is factual and Jen adds value, it could be appropriate
- If the criticism invites legal exposure, it's Red-tier

Default: Yellow-tier for competitor criticism unless it crosses into legal risk (defamation, false claims), then Red-tier.

---

## Risk Level Evaluator: Implementation Checklist

```
□ Red-tier termination fires immediately upon -3 score
□ Yellow-tier flag set but evaluation continues on -1 score
□ All Red-tier conditions checked before any Yellow-tier conditions
□ Multiple Yellow flags can be present on same post (all logged)
□ Score rationale is specific to the evaluated content
□ Metaphorical death language correctly distinguished from actual
□ Gen Digital mentions correctly categorized (positive/neutral vs. negative)
□ Security discussions correctly categorized (educational vs. active incident)
□ Competitor content handled appropriately
□ Edge cases default to Yellow-tier rather than Green-tier when ambiguous
```

# Dimension 2: Engagement Potential Evaluator

## 7.4.5 Engagement Potential

### What Engagement Potential Measures

Engagement Potential measures the likelihood that a comment posted on this content will be seen by a significant audience and generate profile visits—users curious enough about the commenter to check out Jen's profile and, by extension, Gen Digital.

It is NOT a measure of content quality. It is NOT a measure of whether Jen should comment. It is a measure of the **opportunity size**: How many people will see the comment if it is posted, and how much runway remains in the content's engagement window?

Engagement Potential answers one question: **If Jen posts the perfect comment on this content right now, how many people are realistically going to see it?**

A piece of content can be perfect for Jen to comment on—specific angle, right persona, no risk—and still score low on Engagement Potential because the timing window has closed or the content never gained meaningful traction. That is not a failure of the scoring framework. That is the framework correctly identifying that the engagement opportunity has passed, even if the content itself was good.

### Timing Phases

Content moves through timing phases as it ages. The phase determines the maximum Engagement Potential score possible:

| Phase | Age (Tech/AI Content) | Age (General Tech) | Max Score |
|-------|----------------------|-------------------|-----------|
| Phase 1 | 0-6 hours | 0-4 hours | 3 |
| Phase 2 | 6-24 hours | 4-12 hours | 2 |
| Phase 3 | 24-48 hours | 12-24 hours | 1 |
| Expired | >48 hours | >24 hours | 0 |

Platform-specific adjustments:

| Platform | Phase 1 | Phase 2 | Phase 3 | Expired |
|----------|---------|---------|---------|---------|
| Twitter/X | 0-4 hours | 4-12 hours | 12-24 hours | >24 hours |
| LinkedIn | 0-12 hours | 12-48 hours | 48-72 hours | >72 hours |
| Reddit | 0-6 hours | 6-24 hours | 24-48 hours | >48 hours |
| HackerNews | 0-4 hours | 4-12 hours | 12-24 hours | >24 hours |
| Discord | 0-2 hours | 2-6 hours | 6-12 hours | >12 hours |

### Velocity Ratio

The velocity ratio compares actual engagement to expected engagement:

```
velocity_ratio = actual_engagement / expected_engagement_for_age
```

Where:
- `actual_engagement` = likes + (replies × 2) + (shares × 1.5)
- `expected_engagement_for_age` = platform baseline × age factor

A velocity ratio of:
- **> 2.0** = Content performing at more than double expected rate (viral)
- **1.0 - 2.0** = Content performing at or above expected rate (healthy)
- **< 1.0** = Content performing below expected rate (underperforming)

### Scoring Criteria

#### Score 3 - High Engagement Potential

ALL of the following must be true for a score of 3:

1. Content is in **Phase 1** of its timing window
2. Velocity ratio is **above 2.0** (performing at 2x+ expected rate)
3. Comment section is active (at least 3 comments present)
4. At least ONE of these amplifying signals:
   - Cross-platform trending (same topic trending on multiple platforms)
   - Author is verified
   - Author has 50K+ followers
   - Contains trending hashtag/topic
   - Referenced by multiple other posts

**Phase 1 timing is required for score 3.** Phase 2 content cannot score 3 regardless of velocity or amplifying signals.

**Score 3 rationale example:**
```
"Score 3 - Phase 1 timing (2.4 hours old), velocity ratio 3.8, 
active comment section (7 comments), author verified with 82K followers.
Cross-platform signal: topic also trending on HackerNews."
```

#### Score 2 - Moderate Engagement Potential

Content scores 2 when it meets threshold but not the criteria for score 3. Any of these conditions:

- Phase 1 content with velocity ratio between 1.0 and 2.0 and no amplifying signals
- Phase 2 content with velocity ratio above 2.0 and at least one amplifying signal
- Content from a high-priority author (recognized industry voice) regardless of timing phase, as long as within maximum age window and above velocity threshold

**Score 2 rationale example:**
```
"Score 2 - Phase 2 timing (8 hours old) reduces from 3. 
Velocity ratio 2.3 (above 2.0 but Phase 2 cap applies). 
Author is recognized AI security researcher (high-priority author list)."
```

#### Score 1 - Low Engagement Potential

Content scores 1 when engagement is above threshold but opportunity is limited:

- Phase 2 content with velocity ratio between 1.0 and 2.0 and no amplifying signals
- Phase 3 content with velocity ratio above 2.0
- Content from secondary platforms where Jen has less presence
- Long-tail content (technical deep dives that accumulate views over time)

**Score 1 rationale example:**
```
"Score 1 - Phase 3 timing (28 hours old), velocity ratio 1.4.
No amplifying signals. LinkedIn technical post - may accumulate 
views via search over time but immediate engagement window closing."
```

#### Score 0 - No Engagement Potential

Content scores 0 in any of these conditions:

- Content is in **expired** status (age exceeds maximum window for platform)
- Velocity ratio is **below 1.0** (underperforming)
- Metrics are unavailable (`metrics_available = false`)
- No engagement data available

**A score of 0 does not terminate evaluation.** The Evaluation Engine continues to the next dimension. But a score of 0 here means the composite score cannot exceed 5 (maximum remaining: Angle 3 + Persona 2 = 5), which produces an Engage Standard outcome at best.

In practice, content with zero Engagement Potential almost never reaches Engage Standard because Angle Strength and Persona Clarity scores of 3 and 2 are not independently achievable on stale, low-velocity content.

**Score 0 rationale example:**
```
"Score 0 - Content age 51 hours exceeds 48-hour maximum for 
Reddit technical content. Expired before evaluation could complete.
No engagement potential remains."
```

### Inputs Used

```
metrics.engagement_count          Total engagement (likes + comments + shares)
metrics.velocity_ratio            Calculated engagement velocity
metrics.metrics_available         Whether metrics could be retrieved
timing_phase                      Current phase (may need recalculation)
content_age_hours                 How old the content is
platform                          Affects timing windows
author.follower_count             For amplifying signal check
author.verified                   For amplifying signal check
author.is_high_priority           On recognized voices list
top_existing_comments             Count indicates active discussion
trending_signals                  Cross-platform, hashtag trends
```

### Phase Drift Handling

When the Queue Reader reads a post, the `timing_phase` field reflects the phase at time of discovery. By the time the Scoring Component evaluates it, the content may have moved to a later phase.

**The evaluator must recalculate current timing phase** using:
- `content_created_at` timestamp
- Current time
- Platform-specific phase boundaries

If current phase is later than recorded phase:
1. Update `timing_phase` field in the post
2. Log a `phase_drift_detected` event with original and current phases
3. Score based on the **current** phase, not the recorded phase

If current phase is "expired":
1. Score 0 for Engagement Potential
2. Log `expired_before_scoring` event
3. Continue evaluation (do not terminate—let composite score handle routing)

**Phase drift rationale example:**
```
"Score 2 (adjusted from expected 3) - Phase drift detected.
Original phase at discovery: phase_1. Current phase: phase_2.
Content aged from 4 hours to 8 hours while in queue.
Velocity ratio 2.5 would score 3 in Phase 1, capped at 2 for Phase 2."
```

### Edge Cases

**Null metrics**

Some discovery methods (keyword search, manual entry) may not have engagement metrics. When `metrics_available = false`:
- Score 0 for Engagement Potential
- Log the null metrics as reason
- Continue evaluation (the post may still have high Angle Strength for manual processing)

**High-priority author with expired content**

Even recognized industry voices should not score above 0 if content is past the maximum age window. The phase drift check catches this, but if an expired high-priority post reaches the evaluator:
- Score 0
- Log as expired
- Note the author status for analytics

**Comment section as engagement signal**

The presence of comments indicates active discussion. Use comment count as a secondary signal:
- 0-2 comments: No boost
- 3-10 comments: Active discussion, supports score 2-3
- 10+ comments: Very active, strong support for score 3

If comment count is high but engagement metrics are low (many comments, few likes), this may indicate controversial content—consider whether this should trigger Yellow-tier risk review.

---

## Engagement Potential Evaluator: Implementation Checklist

```
□ Phase 1 required for score 3 (hard rule)
□ Velocity ratio correctly calculated
□ Phase drift detected and handled
□ Expired content scores 0 but doesn't terminate
□ Platform-specific timing windows applied
□ Amplifying signals checked for score 3
□ High-priority authors handled correctly
□ Null metrics handled gracefully
□ Score rationale includes all relevant factors
□ Comment count used as secondary signal
```

# Dimension 3: Jen Angle Strength Evaluator

## 7.4.6 Jen Angle Strength

### What Jen Angle Strength Measures

Jen Angle Strength measures the quality and specificity of the comment Jen can write on this content. **It is the most important dimension in the scoring framework** because it is the dimension most directly connected to whether the agent produces value or produces noise.

### The Golden Rule

**A comment that could appear on any post does not get posted.**

Every score in this dimension is an evaluation of how specific, genuine, and inevitable the best possible comment on this content is:
- **Score 3** means the angle is so specific to this exact content that it could not have been written without reading it
- **Score 0** means no such angle exists

### The Hard Termination

Jen Angle Strength is the only dimension besides Risk Level with a hard termination condition. **A score of 0 terminates evaluation and routes the post to Do Not Engage regardless of all other scores.**

This is the correct behavior. A high-velocity, Phase 1, perfectly safe piece of content with no genuine Jen angle is worth nothing—posting a generic comment on it actively damages the persona by making Jen look like a bot.

Consider: A viral post about "AI agents are the future!" with 50K likes.
- Risk Level: 0 (Green, safe content)
- Engagement Potential: 3 (Phase 1, high velocity, verified author)
- Jen Angle Strength: 0 (What can Jen say that isn't generic?)

Without the Angle Strength check, this post scores 5/8 and routes to Standard Review. With the check, it terminates at score 0. The generic comment that would have been generated ("Great point! AI agents are definitely changing the landscape!") never gets created.

### What the Evaluator Is Actually Doing

The Jen Angle Strength evaluator performs a different kind of evaluation than the other three dimensions. Engagement Potential, Persona Clarity, and Risk Level evaluate objective, measurable attributes—timing, velocity, keyword presence, sensitivity patterns.

Jen Angle Strength evaluates something more subjective: **the quality of a comment that doesn't exist yet.**

This means the evaluator cannot simply read a field from the discovery record and map it to a score. It must reason about the content—its text, its context, its comment section—and assess whether a specific, genuine, non-generic comment is achievable.

The inputs are:
- The content text
- The hashtags
- The top existing comments
- The keyword matches that triggered discovery
- The content classification
- Gen Digital's relevant expertise areas

From these inputs the evaluator must determine whether a comment exists that is:
1. **Specific** to something in this exact content
2. **Something Jen would actually say** in character
3. **At a level that would make a reader stop and engage** rather than scroll past
4. **Not already said** by an existing top comment

### The Quality Ladder

The quality ladder defines what "good" looks like for Jen's comments. The evaluator's job is to assess what level on the quality ladder the best possible comment on this content could reach.

| Level | Description | Maps to Score |
|-------|-------------|---------------|
| **Level 5** | Genuinely unexpected, perfectly specific, memorable | Score 3 |
| **Level 4** | Strong, specific, clearly Jen's voice | Score 3 |
| **Level 3** | Acceptable, specific enough to not be generic, passes Golden Rule | Score 2 |
| **Level 2** | Marginal, technically non-generic but forgettable | Score 1 |
| **Level 1** | Generic, could appear on any similar post | Score 0 |

### Scoring Criteria

#### Score 3 - Strong Angle

The content contains a specific, identifiable moment, detail, or tension that creates a comment opportunity impossible to write without having actually read this content. The angle:
- Arises naturally from what the content is about
- Is not forced by applying an AI security lens onto irrelevant content
- Would strike a reader as inevitable—"of course that's the comment to write here"

**Signals that suggest score 3:**

| Signal | Why It Suggests Score 3 |
|--------|------------------------|
| Content text contains a specific detail, number, or statement Jen can respond to directly | "We're using 47 different API calls in our agent" → specific attack surface to discuss |
| Top existing comments show audience engaged with aspect Jen would comment on | Jen joins an active conversation rather than starting one in a dead section |
| Content category is AI/security and keyword match is Tier 1 | Gen Digital's expertise is directly relevant |
| Content has a clear emotional beat Jen can meet at right register | Frustration with agent security → Jen can empathize specifically |
| Author is asking a question Jen has unique expertise to answer | "How do I verify my agent isn't being prompt injected?" |

**Score 3 rationale example:**
```
"Score 3 - Content is a detailed thread about agent permission systems 
where author describes their custom implementation with 'allow-list only' 
approach for tool calls. Specific technical detail (permission architecture) 
creates direct Gen Digital Agent Trust Hub angle - runtime verification 
addresses exactly this problem. No existing top comment addresses verification 
approach. Author explicitly asking for feedback. Level 5 angle achievable."
```

#### Score 2 - Adequate Angle

A specific angle exists but requires thought to construct. The comment is not immediately obvious but upon reflection is genuinely specific to this content. The connection between the content and what Jen would say is real but not immediate.

**Signals that suggest score 2:**

| Signal | Why It Suggests Score 2 |
|--------|------------------------|
| Content is AI-adjacent (Tier 2 keyword match) and security angle is present but secondary | Relevant but requires finding the connection |
| Content's topic is one where Jen has a recognized perspective, but execution requires creativity | The angle exists but isn't obvious |
| Existing top comments made some obvious observations—Jen needs less obvious angle | Space is partially occupied |
| Content is a general AI discussion where security framing adds value | Relevant but Jen is adding perspective, not directly responding |

**Score 2 rationale example:**
```
"Score 2 - Thread about LangChain agent development where security is 
mentioned but not the primary focus. Angle requires construction - 
the author is discussing agent architectures generally, and Jen can 
add security perspective that's genuinely valuable but not the 
obvious response. Existing top comment with 1.2K likes discusses 
performance optimization - Jen's security angle is distinct."
```

#### Score 1 - Weak Angle

An angle technically exists but is either generic, forced, or already said. The comment would pass the Golden Rule test only narrowly—it references something specific to this content but wouldn't make anyone stop scrolling.

**Signals that suggest score 1:**

| Signal | Why It Suggests Score 1 |
|--------|------------------------|
| Best angle is a surface-level observation about AI security | References content but doesn't add much |
| Connection to Jen's expertise requires significant construction | Feels forced |
| Multiple existing comments have already said what Jen would say | Angle exists but space is occupied |
| Content is tangentially related to AI but security connection is thin | Relevant in name only |

**Score 1 rationale example:**
```
"Score 1 - Post about general LLM usage trends where 'agent' is 
mentioned once. Best available angle is a general comment about 
agent security being important. Would pass Golden Rule narrowly 
(references this specific post's mention of agents) but wouldn't 
stop a scrolling reader. Multiple existing comments already 
making similar observations."
```

#### Score 0 - No Angle (TERMINATES EVALUATION)

No specific, genuine comment exists. Any comment Jen would write on this content would be generic—it could appear on a dozen other posts without being out of place.

**This triggers the hard termination.**

**Signals that suggest score 0:**

| Signal | Why It Suggests Score 0 |
|--------|------------------------|
| Content is straightforward with no room for specific observation | "AI is cool!" → What can Jen add? |
| Content is from trending discovery but has no AI security angle | Viral but irrelevant |
| All possible angles have been taken by top comments with thousands of likes | No space left |
| Content is generic industry commentary with nothing specific | No hook for a specific response |
| Security/agent angle would be completely forced | Would damage Jen's credibility |

**Score 0 rationale example:**
```
"Score 0 - High-engagement post about general tech industry trends. 
No AI agent or security content whatsoever. Source was keyword match 
on 'automation' but content is about business process automation, 
not AI agents. Any comment would be generic or off-topic. 
Golden Rule: Nothing specific to say. EVALUATION TERMINATED."
```

### The Top Comments Check

The top existing comments are the most important input for Jen Angle Strength evaluation after the content text itself. Before assigning a score, the evaluator must check whether any existing top comments have already occupied the angle Jen would take.

**The check works as follows:**

1. For each top comment captured in `top_existing_comments`:
2. Assess whether the comment's substance overlaps with the angle Jen would write
3. If a top comment with significant engagement has already made the AI security observation Jen would make:
   - The angle is **occupied**
   - Reduce the score by 1 (but not below 1)
4. Log the top comment check result:
   - Which comment (if any) was assessed as occupying Jen's angle
   - Whether a score reduction was applied

**Why not reduce below 1?**

A score of 1 means "angle exists but is weak" which is accurate if the angle has been taken.
A score of 0 means "no angle exists at all" which is different from "angle exists but is taken."

If the only possible angle is taken, score 1. If no angle exists regardless of what others said, score 0.

**Top comments check rationale example:**
```
"Top comment check: @securitydev (2.4K likes) already commented 
'This is exactly why runtime verification matters for agents.'
This overlaps with Jen's primary angle. Score reduced from 3 to 2.
Alternative angle available: Specific technical implementation 
suggestion for the author's described architecture."
```

### Inputs Used

```
content_text              Full post text
content_hashtags          Hashtags (indicate topic focus)
top_existing_comments     What's already been said (and engagement levels)
keyword_matches           What terms triggered discovery
keyword_tier              How core the match is (Tier 1, 2, or 3)
classification            Post type (helps assess angle potential)
author_bio                May indicate if author is in target audience
author_domain_relevance   Is author typically in AI/security space?
gen_digital_expertise     What can Jen specifically contribute?
```

### Jen's Expertise Areas (for angle assessment)

These are the areas where Jen can provide genuinely valuable, non-generic commentary:

| Expertise Area | Specific Value Jen Can Add |
|----------------|---------------------------|
| **Agent runtime security** | How to monitor/verify agent behavior in production |
| **Tool use authorization** | Permission systems for agent tool access |
| **Prompt injection defense** | Practical mitigation strategies |
| **Agent architecture patterns** | Security-first design approaches |
| **LLM security fundamentals** | Input/output validation, sandboxing |
| **Enterprise agent deployment** | Compliance, audit trails, governance |
| **Agent framework comparison** | Security implications of LangChain vs AutoGen vs others |
| **Gen Digital products** | Agent Trust Hub, runtime verification (Connector mode only) |

If the content doesn't touch any of these areas, the maximum Angle Strength score is 1 (weak angle based on general AI knowledge).

### Edge Cases

**Content with no text**

Some content—particularly reposts or link shares—may have minimal caption text. If `content_text` is null or under 10 characters:
- Rely entirely on hashtags and top existing comments
- If those are also sparse, score 1 or 0 depending on whether classification suggests an angle is possible
- Log sparse text as a factor in rationale

**Gen Digital mentioned negatively**

If keyword matches include Gen Digital terms AND the content discusses Gen Digital negatively:
- Score 0 for Jen Angle Strength
- This content requires carefully crafted human response, not agent-generated comment
- Risk Level evaluator will also flag this as Red-tier

The Angle Strength evaluator should independently recognize this case as a defensive measure.

**Competitor content**

Content matching competitor terms (LangChain, AutoGen, CrewAI security issues, etc.) in Tier 1 is often a genuine engagement opportunity—Jen can add value to conversations about agent security regardless of whose framework is being discussed.

Score based on whether a specific, non-generic angle exists. Do not automatically score competitor content high or low—evaluate the specific angle available.

**Question already answered**

If the post asks a question and a top comment has already provided the same answer Jen would give:
- Angle is occupied
- Score 1 (angle exists but is taken)
- Note: Jen could still add value if she can expand on, nuance, or respectfully build on the existing answer

---

## Jen Angle Strength: The Evaluation Checklist

Before assigning a score, the evaluator should answer these questions:

```
□ What specifically would Jen say about THIS content?
□ Could this comment appear on 10 other posts? (If yes → Score 0)
□ Does the angle reference something specific IN the content?
□ Is the angle in Jen's expertise areas?
□ Has this angle already been said in top comments?
□ Would this comment make a reader stop and engage?
□ Is the connection to AI security natural or forced?
□ If Connector mode: Is there a natural product mention opportunity?
□ If Advisor mode: Is there specific expertise to share?
□ If Observer mode: Is there a specific observation to make?
```

## Jen Angle Strength Evaluator: Implementation Checklist

```
□ Score 0 terminates evaluation immediately
□ Golden Rule enforced: generic comments never score above 0
□ Top comments check performed before final score
□ Score reduction applied for occupied angles (but not below 1)
□ Expertise areas consulted for angle assessment
□ Competitor content handled appropriately
□ Gen Digital negative mentions score 0
□ Score rationale is specific to content (not generic)
□ Sparse content handled gracefully
□ Evaluation metadata includes all reasoning
```

# Dimension 4: Persona Clarity Evaluator

## 7.4.7 Persona Clarity

### What Persona Clarity Measures

Persona Clarity measures how unambiguously the correct operating persona for Jen can be identified from this content. Jen operates in three personas:

| Persona | Role | When to Use |
|---------|------|-------------|
| **Observer** | Industry watcher, no product ties | General AI discussions, trends, humor |
| **Advisor** | Helpful expert, no product mentions | Technical questions, help-seeking |
| **Connector** | Product advocate when natural | Direct product relevance, buying signals |

Using the wrong persona is one of the most damaging errors the agent can make:
- Connector on content that calls for Observer = looks like spam
- Observer on content where someone needs help = looks dismissive
- Advisor on content that's casual/humorous = looks tone-deaf

Persona Clarity does not measure *which* persona is correct—it measures **how clearly the correct persona can be identified**. Content where the correct persona is obvious scores high. Content where the persona is ambiguous—where choosing incorrectly is a real risk—scores low. Content where the persona cannot be determined with confidence scores 0 and is flagged for human review.

### The Persona Selection Framework

The three personas exist on a spectrum of engagement depth:

```
OBSERVER                    ADVISOR                     CONNECTOR
──────────────────────────────────────────────────────────────────►
Light touch               Helpful expert              Product advocate
No product ties           No product names            Natural product mention
Observational             Educational                 Promotional (subtle)
Industry participant      Trusted helper              Brand representative
```

**Observer mode** is the default for:
- General AI/tech discussions
- Industry commentary
- Humor and memes
- News/announcements (not asking for help)
- Content where Jen is a peer in the conversation

**Advisor mode** is indicated by:
- Direct questions seeking help
- Technical problems or debugging
- "How do I..." or "What's the best way to..."
- Frustration with a technical challenge
- Learning/educational content where expertise adds value

**Connector mode** is only appropriate when:
- Content explicitly mentions agent security solutions
- Content is comparing products in the space
- Content shows buying/evaluation signals ("looking for a tool")
- Gen Digital product is directly relevant AND naturally fits
- Connector mode is currently enabled in campaign settings

### Scoring Criteria

#### Score 2 - Persona Unambiguous

The correct operating persona can be identified with full confidence. The key test: **if a second evaluator looked at this content independently, they would reach the same persona conclusion without hesitation.**

**Score 2 conditions:**

| Condition | Determined Persona | Confidence |
|-----------|-------------------|------------|
| No AI security angle, general tech discussion | Observer | High |
| Direct technical question about agent implementation | Advisor | High |
| Explicit "looking for a solution" with buying signals | Connector | High |
| Help-seeking about specific technical problem | Advisor | High |
| Industry news commentary, no question asked | Observer | High |
| Humor/meme about AI with no help-seeking | Observer | High |
| Explicit mention of evaluating security tools | Connector | High |

**Score 2 rationale examples:**

```
Observer (Unambiguous):
"Score 2 - Industry commentary about AI agent trends. Author sharing 
observations, not asking questions. No help-seeking signals. No buying 
signals. No product evaluation context. Observer is the only appropriate 
persona. Persona determination: Observer, confidence: high."
```

```
Advisor (Unambiguous):
"Score 2 - Direct technical question: 'How do I prevent prompt injection 
in my LangChain agent?' Explicit help-seeking, specific technical challenge. 
Advisor mode provides value without product mention. 
Persona determination: Advisor, confidence: high."
```

```
Connector (Unambiguous):
"Score 2 - Author explicitly evaluating agent security solutions: 
'We're looking for runtime verification tools for our production agents.'
Direct buying signal, explicit solution-seeking. Natural Connector opportunity.
Persona determination: Connector, confidence: high."
```

#### Score 1 - Persona Determinable with Moderate Confidence

The correct persona can be identified but requires interpretation. The content sits between two personas in a way that requires judgment. A score of 1 means the evaluator has determined a persona with reasonable confidence, but acknowledges the determination required judgment rather than being self-evident.

**Score 1 conditions:**

| Condition | Likely Persona | Why Moderate Confidence |
|-----------|---------------|------------------------|
| Technical discussion with embedded question | Advisor or Observer | Is the question rhetorical or genuine? |
| Frustration about security issues generally | Advisor or Observer | Venting or seeking help? |
| Comparison post that doesn't ask for input | Observer or Connector | Opening for input or just sharing? |
| Educational content where Jen could add expertise | Advisor or Observer | Add to education or just observe? |

**Score 1 rationale example:**
```
"Score 1 - Thread about agent security challenges where author describes 
problems but doesn't explicitly ask for help. Could be interpreted as 
venting (Observer appropriate) or implicit help-seeking (Advisor appropriate).
Author's tone is frustrated but constructive. Leaning Advisor based on 
'anyone else dealt with this?' closing, but interpretation required.
Persona determination: Advisor, confidence: moderate."
```

#### Score 0 - Persona Indeterminate (FORCES HUMAN REVIEW)

The correct persona cannot be determined with confidence. The content sits directly on the line between personas in a way where choosing incorrectly carries meaningful risk. 

**A score of 0 does not terminate evaluation.** The composite score is calculated including this 0. But the Tier Classifier treats a Persona Clarity score of 0 as a **Yellow-tier flag that forces human review** regardless of the composite score.

**Score 0 conditions:**

| Condition | Conflict | Risk |
|-----------|----------|------|
| Frustrated rant that might be seeking help | Observer vs Advisor | Observer looks dismissive if they want help; Advisor looks preachy if they're venting |
| Product comparison where adding Gen Digital could be helpful or spammy | Advisor vs Connector | Connector looks like spam; Advisor misses legitimate opportunity |
| Sarcastic/ironic tone about security tools | Observer vs Advisor | Hard to tell if genuine question wrapped in humor |
| Implicit help-seeking in technical showcase | Observer vs Advisor | "Check out my agent" - Are they asking for feedback? |

**Score 0 rationale example:**
```
"Score 0 - Post about agent security challenges presented through 
frustrated humor. Author says 'my agent keeps getting jailbroken lol' 
with laughing emoji but comment section shows both 'lol same' responses 
AND genuine technical suggestions. Observer humor risks being dismissive 
if they actually want help. Advisor expertise risks missing the joke if 
they're just venting. Cannot determine persona with confidence.
YELLOW-TIER FLAG APPLIED - Human must determine persona before generation."
```

### Persona Identification Logic

The Persona Clarity evaluator determines persona using this logic:

```
Step 1: Check for Connector signals
────────────────────────────────────
If ANY of these are true:
  - Content explicitly mentions evaluating/buying security tools
  - Content contains "looking for a solution/tool/product"
  - Content compares products in the space with evaluation intent
  - Content mentions Gen Digital products by name (positively)
  
AND Connector mode is enabled in campaign settings:
  → Connector is the likely persona
  → Proceed to Step 4 for confidence assessment

If Connector signals are weak or mode is disabled:
  → Proceed to Step 2

Step 2: Check for Advisor signals
────────────────────────────────────
If ANY of these are true:
  - Content contains explicit question ("How do I...", "What's the best...")
  - Content describes a specific technical problem
  - Content uses help-seeking language ("struggling with", "can't figure out")
  - Content classification is help_seeking or technical_question
  - Comment section shows others providing technical assistance
  
  → Advisor is the likely persona
  → Proceed to Step 4 for confidence assessment

If help-seeking signals are weak:
  → Proceed to Step 3

Step 3: Default to Observer
────────────────────────────────────
Content defaults to Observer when:
  - General industry discussion
  - Commentary without questions
  - News sharing
  - Humor/memes
  - No explicit help-seeking
  
  → Observer is the likely persona
  → Proceed to Step 4

Step 4: Confidence Assessment
────────────────────────────────────
Assess confidence in the determination:

HIGH confidence (Score 2) if:
  - Signals are unambiguous
  - Only one persona makes sense
  - Second evaluator would reach same conclusion

MODERATE confidence (Score 1) if:
  - Signals lean one direction but aren't definitive
  - Interpretation was required
  - Edge case but determinable

LOW confidence (Score 0) if:
  - Two personas are equally plausible
  - Choosing incorrectly would be damaging
  - Human judgment required
```

### Handling Ambiguous Tone

The hardest cases are where tone makes persona selection ambiguous:

**Sarcasm/Irony:**
- "Oh great, another agent jailbreak. Just what I needed today." 
- Is this frustration seeking help (Advisor) or sardonic observation (Observer)?
- Signal: Check if author engages with helpful replies or dismisses them

**Self-deprecating humor about real problems:**
- "My security posture is basically praying the AI doesn't go rogue lol"
- Is this a joke (Observer) or a cry for help wrapped in humor (Advisor)?
- Signal: Check comment section for genuine advice vs. joke replies

**Rhetorical questions:**
- "Why is agent security so hard?"
- Is this seeking explanation (Advisor) or just expressing frustration (Observer)?
- Signal: Check if author responds to explanatory comments with interest

**When genuinely ambiguous, score 0.** The Yellow-tier review ensures a human makes the call.

### Inputs Used

```
content_text              Full post text (for tone/signals)
content_classification    Classification helps determine likely persona
question_detected         Was a question asked?
help_seeking_signals      Phrases indicating need for help
buying_signals            Phrases indicating product evaluation
top_existing_comments     How are others responding? (advice vs. jokes)
author_engagement         Does author engage with helpful replies?
campaign_connector_mode   Is Connector mode enabled?
connector_blend_weight    How much should Connector be weighted?
```

### Connector Mode Special Rules

Connector mode has additional requirements beyond persona clarity:

1. **Connector must be enabled** in campaign settings. If connector_blend_weight is 0 or Connector is disabled, Connector is never the determination regardless of signals.

2. **Connector requires strong signals.** Unlike Observer/Advisor which can be determined from ambiguous content, Connector should only be determined when signals are clear. Default to Advisor if product relevance exists but signals aren't strong.

3. **Connector determination should be rare.** Most content should route to Observer or Advisor. Connector is for explicit opportunities.

4. **Connector with score 1 requires review.** If Connector is determined with moderate confidence (score 1), add a flag for human verification of the product mention appropriateness.

### Edge Cases

**Content entirely promotional**

If the post is itself promotional content (a company sharing their product), Jen's persona should usually be Observer (light engagement with industry content) unless there's a genuine question embedded.

**Author asking for help on competitor's product**

"How do I secure my LangChain agent?" - This is Advisor mode, not Connector. Jen helps with the general problem, doesn't pivot to "use our product instead."

**Multiple signals present**

If help-seeking AND buying signals are present ("I need help choosing a security tool"), determine based on the primary need:
- "I'm evaluating tools and stuck on X" → Connector (evaluation context)
- "I'm trying to secure my agent and wondering about tools" → Advisor (help-seeking primary)

---

## Persona Clarity Evaluator: Implementation Checklist

```
□ Score 0 triggers Yellow-tier override (doesn't terminate)
□ Connector mode checked against campaign settings
□ Sarcasm/irony cases handled with caution
□ Observer is default when signals are absent
□ Advisor requires explicit help-seeking signals
□ Connector requires strong buying/evaluation signals
□ Confidence levels correctly mapped to scores
□ Persona determination included in scoring result
□ Ambiguous cases scored 0, not guessed
□ Human review flag set for all score 0 and Connector score 1
```

# Composite Score Calculator, Tier Classifier, and Queue Router

## 7.4.8 Composite Score Calculator

### What the Composite Score Calculator Does

The Composite Score Calculator receives the four dimension scores from the Evaluation Engine and produces a single composite score that determines the content's outcome category. It enforces the two termination conditions flagged by the Evaluation Engine and maps the composite score to one of the five outcome categories.

### The Calculation

```
composite_score = engagement_potential + jen_angle_strength + 
                  persona_clarity + risk_level
```

| Dimension | Score Range | Max Contribution |
|-----------|-------------|------------------|
| Risk Level | -3, -1, 0 | 0 |
| Engagement Potential | 0, 1, 2, 3 | 3 |
| Jen Angle Strength | 0, 1, 2, 3 | 3 |
| Persona Clarity | 0, 1, 2 | 2 |
| **Maximum Composite** | | **8** |

The minimum possible composite score before termination conditions is -3 (0 + 0 + 0 + (-3)). In practice, a Risk Level score of -3 terminates evaluation before the composite score is calculated, so the effective minimum composite score for any non-terminated record is 0.

### Termination Condition Enforcement

Before calculating the composite score, the Calculator checks for termination flags:

**Red-tier termination flag**

If the Risk Level evaluator returned -3 and set `red_tier_terminated = true`:
- Calculator does NOT calculate composite score
- Assigns `composite_score: null`
- Assigns `outcome: "red_tier"`
- Passes immediately to Tier Classifier

**Zero Angle termination flag**

If the Jen Angle Strength evaluator returned 0 and set `zero_angle_terminated = true`:
- Calculator assigns `composite_score: 0`
- Assigns `outcome: "do_not_engage"`
- Passes to Tier Classifier

Note: The composite score is recorded as 0 even though Engagement Potential and Persona Clarity may have produced positive scores. The zero-angle termination overrides the composite calculation.

### Outcome Category Mapping

After calculating the composite score, map to an outcome category:

```
Composite Score 7-8:    outcome = "engage_immediately"
Composite Score 5-6:    outcome = "engage_standard"
Composite Score 3-4:    outcome = "pass"
Composite Score 0-2:    outcome = "do_not_engage"
Composite Score null:   outcome = "red_tier" (set by termination, not calculated)
```

**These mappings are fixed.** They are not configurable. The outcome thresholds are part of the core framework and changing them requires deliberate system-wide review.

### Yellow-Tier Interaction

A Yellow-tier flag from Risk Level (-1) or Persona Clarity (0) does not change the composite score calculation:

1. The composite score is calculated normally with -1 included (for Risk Level)
2. The outcome category is determined normally
3. The Yellow-tier flag is passed to the Tier Classifier separately
4. The Tier Classifier overrides routing regardless of outcome category

**Example:**

A post with:
- Risk Level: -1 (Yellow flag: health content)
- Engagement Potential: 3
- Jen Angle Strength: 3
- Persona Clarity: 2

Composite score: -1 + 3 + 3 + 2 = **7**
Outcome: "engage_immediately"

But the Yellow-tier flag overrides routing from `priority_review` to `yellow_tier`. The outcome reflects the content's quality. The tier classification reflects the risk. Both are recorded.

### Calculator Output

```
composite_score             float | null    The calculated composite score
outcome                     string          One of five outcome categories
dimension_scores            object          
  risk_level               integer         -3, -1, or 0
  engagement_potential     integer         0, 1, 2, or 3
  jen_angle_strength       integer         0, 1, 2, or 3
  persona_clarity          integer         0, 1, or 2
termination_flags           object
  red_tier_terminated      boolean
  zero_angle_terminated    boolean
yellow_tier_flag            boolean         True if risk_level = -1 OR persona_clarity = 0
persona_determination       string | null   "observer" | "advisor" | "connector" | null
persona_confidence          string | null   "high" | "moderate" | null
```

---

## 7.4.9 Tier Classifier

### What the Tier Classifier Does

The Tier Classifier receives the Calculator's output and produces:
1. Final tier classification (Green, Yellow, Red)
2. Routing queue assignment
3. Priority within the queue

### Classification Rules

The Tier Classifier applies three rules in order:

**Rule 1: Red-tier classification**

If `red_tier_terminated = true`:
- Classify as **Red tier**
- Assign routing queue: `"red_tier"`
- Assign priority: 5 (lowest)
- Stop. No further rules apply.

**Rule 2: Yellow-tier override**

If `yellow_tier_flag = true` (from Risk Level -1 OR Persona Clarity 0):
- Classify as **Yellow tier** regardless of composite score and outcome
- Assign routing queue: `"yellow_tier"`
- Assign priority based on timing phase (see below)
- Preserve original outcome category in record for reference
- Stop. No further rules apply.

**Rule 3: Green-tier classification**

If neither Red nor Yellow conditions apply:
- Classify as **Green tier**
- Assign routing queue based on outcome category:

| Outcome | Routing Queue |
|---------|---------------|
| engage_immediately | priority_review |
| engage_standard | standard_review |
| pass | passed_log |
| do_not_engage | do_not_engage_log |

### Priority Assignment

Priority determines the order in which posts are processed within a queue. Lower number = higher priority.

**Priority Review Queue:**

| Condition | Priority |
|-----------|----------|
| Phase 1 content | 1 (highest) |
| Phase 2 content | 2 |
| Phase 3 content | 3 |

**Yellow-Tier Queue:**

| Condition | Priority |
|-----------|----------|
| Phase 1 content | 1 |
| Phase 2 content | 2 |
| Phase 3 content | 3 |

**Standard Review Queue:**

| Condition | Priority |
|-----------|----------|
| Technical content, Phase 2 | 2 |
| General content, Phase 2 | 3 |
| Phase 3 content | 4 |

**All other queues:** Priority 5 (lowest)

Priority affects processing order, not whether content is engaged with. Phase 1 content in any queue is always processed before Phase 2, because Phase 1 has a shorter timing window.

### Persona Determination in Classification

The Tier Classifier confirms the persona determination for the scoring result:

- If `persona_confidence` is "high" or "moderate": Include `persona_determination` in scoring result. Response Generation will use this.
- If `persona_confidence` is null (Persona Clarity score was 0): Set `persona_determination` to null and flag. The Yellow-tier routing ensures human reviewer determines persona.

### Tier Classifier Output

```
tier                        string          "green" | "yellow" | "red"
routing_queue               string          Queue name
priority                    integer         1-5
original_outcome            string          The outcome before any overrides
yellow_tier_reasons         array           List of reasons for yellow flag
persona_determination       string | null   Final persona or null for human decision
```

---

## 7.4.10 Queue Router

### What the Queue Router Does

The Queue Router is the final sub-component. It performs three database operations in a single transaction:

1. Updates the discovery record with full scoring result
2. Writes a routing entry to the routing queue table
3. Updates session metrics

If any operation fails, the entire transaction rolls back.

### Discovery Record Update

```sql
UPDATE discovered_posts
SET
  status = {new_status},
  updated_at = NOW(),
  scoring_result = {scoring_result_json},
  priority_score = {composite_score},
  tier = {tier}
WHERE
  id = {post_id}
  AND status = 'pending_scoring'
```

The `AND status = 'pending_scoring'` clause is a safety check. If the update affects 0 rows, log a `concurrent_modification_detected` error and do not write the routing entry.

**Status values by outcome:**

| Outcome | New Status |
|---------|------------|
| engage_immediately | pending_priority_review |
| engage_standard | pending_standard_review |
| pass | passed |
| do_not_engage | do_not_engage |
| red_tier | red_tier |
| Yellow-tier override | pending_yellow_review |

### Routing Queue Entry

```sql
INSERT INTO engagement_queue (
  id,
  post_id,
  queue_name,
  priority,
  queued_at,
  expires_at,
  composite_score,
  tier,
  timing_phase,
  persona_determination,
  requires_review,
  status
)
VALUES (
  {uuid},
  {post_id},
  {routing_queue},
  {priority},
  NOW(),
  {expiration_timestamp},
  {composite_score},
  {tier},
  {current_timing_phase},
  {persona_determination},
  {requires_review},
  'pending'
)
```

### Scoring Result JSON Structure

The complete scoring result stored in the discovery record:

```json
{
  "scored_at": "2024-01-15T10:30:00Z",
  "scoring_duration_ms": 245,
  "composite_score": 7,
  "outcome": "engage_immediately",
  "tier": "green",
  "routing_queue": "priority_review",
  "priority": 1,
  "persona_determination": "advisor",
  "persona_confidence": "high",
  
  "dimension_scores": {
    "risk_level": 0,
    "engagement_potential": 3,
    "jen_angle_strength": 2,
    "persona_clarity": 2
  },
  
  "dimension_evaluations": {
    "risk_level": {
      "score": 0,
      "score_rationale": "Score 0 (Green) - Technical discussion about agent architecture. No risk signals detected. No death/trauma content. No political content. No Gen Digital negative mention. Content appropriate for engagement.",
      "inputs_used": ["content_text", "author_bio", "classification"],
      "termination_triggered": false,
      "yellow_flags": [],
      "red_flags": []
    },
    
    "engagement_potential": {
      "score": 3,
      "score_rationale": "Score 3 - Phase 1 timing (2.1 hours old), velocity ratio 3.2, active comment section (12 comments), author verified with 45K followers.",
      "inputs_used": ["timing_phase", "velocity_ratio", "comment_count", "author_verified"],
      "phase_at_evaluation": "phase_1",
      "phase_drift_detected": false
    },
    
    "jen_angle_strength": {
      "score": 2,
      "score_rationale": "Score 2 - Author describes custom agent permission system implementation. Specific technical detail creates Gen Digital angle (runtime verification addresses this). Top comment check: one comment discusses permissions generally but doesn't cover verification. Angle available but requires thought to construct.",
      "inputs_used": ["content_text", "keyword_matches", "top_comments"],
      "termination_triggered": false,
      "top_comment_check": {
        "overlap_detected": false,
        "overlapping_comment": null,
        "score_reduced": false
      }
    },
    
    "persona_clarity": {
      "score": 2,
      "score_rationale": "Score 2 - Explicit technical question: 'What's the best approach for agent tool authorization?' Direct help-seeking, specific technical challenge. Advisor mode unambiguous.",
      "inputs_used": ["content_text", "classification", "help_seeking_signals"],
      "persona_determination": "advisor",
      "persona_confidence": "high",
      "yellow_flag_applied": false
    }
  },
  
  "termination_flags": {
    "red_tier_terminated": false,
    "zero_angle_terminated": false,
    "yellow_tier_override": false
  }
}
```

### Session Metrics Update

After successful commit, update session metrics:

```
total_evaluated                 Total posts evaluated this session
total_red_tier                  Posts terminated as Red tier
total_zero_angle                Posts terminated for zero angle
total_yellow_tier               Posts routed to Yellow-tier review
total_engage_immediately        Posts routed to priority review
total_engage_standard           Posts routed to standard review
total_passed                    Posts that passed (score 3-4)
total_do_not_engage             Posts scored 0-2 or zero angle

by_platform.{platform}          Per-platform breakdown

score_distribution              Count at each composite score (0-8)
avg_scoring_duration_ms         Rolling average evaluation time

persona_distribution            Count per persona determination
  observer_count
  advisor_count
  connector_count
  undetermined_count
```

### Retry on Write Failure

If the database transaction fails:
1. Retry up to 3 times with exponential backoff (2s, 4s, 8s)
2. If all retries fail, log `scoring_write_failure_unrecoverable`
3. Roll back transaction; post remains in `pending_scoring`
4. Post will be re-evaluated on next polling cycle
5. Idempotent evaluation ensures same result on re-evaluation

---

## 7.4.11 Evaluation Metadata Requirements

Every scoring evaluation must produce metadata that enables calibration review. The metadata is not optional—it is the data used to improve the scoring framework over time.

### Required Fields for Every Dimension

```
dimension               string    Dimension name
score                   integer   Score assigned
score_rationale         string    SPECIFIC explanation (not generic)
inputs_used             array     Fields from post used in evaluation
evaluation_duration_ms  integer   How long this dimension took
```

### Score Rationale Requirements

**The score_rationale must be specific to the content being evaluated.**

✗ Bad rationale: "Content is engaging and relevant"
✗ Bad rationale: "Risk level is acceptable"
✗ Bad rationale: "Angle exists for this content"

✓ Good rationale: "Score 3 - Phase 1 timing (2.4 hours old), velocity ratio 3.8, active comment section (7 comments), author verified with 82K followers."

✓ Good rationale: "Score 0 (Red) - Content discusses active data breach at named company. Red flag: active_news_event. Brand engagement categorically inappropriate."

✓ Good rationale: "Score 2 - Author describes custom permission system. Specific technical detail creates Gen Digital angle. Top comment discusses permissions generally but doesn't cover runtime verification - angle available."

If you cannot write a specific rationale, you do not understand why the score was assigned.

# Testing Protocol and Implementation Checklist

## 7.4.12 Testing Protocol

### Phase 1: Unit Tests

#### Risk Level Evaluator Tests

**Test 1.1 - Red-tier termination on active incident**

Provide a discovery record with content about an ongoing security breach. Verify:
- Risk Level evaluator returns -3
- `red_tier_terminated` is set to true
- Specific trigger condition is logged
- Engagement Potential, Jen Angle Strength, and Persona Clarity are NOT evaluated

**Test 1.2 - Red-tier termination on Gen Digital negative mention**

Provide a discovery record with Gen Digital product mentioned negatively ("Gen Digital's Agent Trust Hub failed us"). Verify:
- Evaluator returns -3
- Condition logged as `gen_digital_negative_mention`
- Evaluation terminates immediately

**Test 1.3 - Yellow-tier flag on security incident discussion**

Provide a discovery record about a past security vulnerability (educational, not active). Verify:
- Evaluator returns -1
- `yellow_tier_flag` is set to true
- Evaluation CONTINUES (Yellow does not terminate)
- Yellow flag condition is logged

**Test 1.4 - Green-tier on clean technical content**

Provide a discovery record for a technical question about agent architecture with no sensitivity signals. Verify:
- Evaluator returns 0
- No Yellow or Red flags
- Green-tier confirmation is logged

**Test 1.5 - Metaphorical death language handling**

Provide a discovery record with caption "RIP my production deployment after that update 💀". Verify:
- Evaluator does NOT return -3
- Returns 0 (metaphorical, not actual death)
- Logs the assessment decision and reasoning

---

#### Engagement Potential Evaluator Tests

**Test 1.6 - Score 3 for Phase 1 with high velocity**

Provide a record with:
- timing_phase: "phase_1"
- velocity_ratio: 4.2
- comment_count: 8
- author_verified: true

Verify: Score 3 is returned with rationale referencing all four inputs.

**Test 1.7 - Score 2 for Phase 2 with amplifying signals**

Provide a record with timing_phase "phase_2", velocity_ratio 2.8, and author_verified true. Verify:
- Score 2 is returned
- Change timing_phase to "phase_1" → verify score rises to 3
- Confirms Phase 1 is required for score 3

**Test 1.8 - Score 0 for expired content**

Provide a record with timing_phase "expired". Verify:
- Score 0 is returned
- Expired status is logged as reason
- Evaluation continues (not terminated)

**Test 1.9 - Phase drift handling**

Provide a record with:
- timing_phase: "phase_1" (at discovery)
- content_created_at: 8 hours ago (now Phase 2)

Verify:
- Evaluator uses recalculated phase (phase_2)
- `phase_drift_detected` is logged
- Score reflects Phase 2 criteria (max score 2)

---

#### Jen Angle Strength Evaluator Tests

**Test 1.10 - Score 0 terminates evaluation**

Provide a record with generic content where no specific Jen angle exists ("AI is changing everything!"). Verify:
- Score 0 is returned
- `zero_angle_terminated` flag is set
- Persona Clarity evaluator is NOT called
- Outcome is "do_not_engage"

**Test 1.11 - Top comment overlap reduces score**

Provide a record with a top comment that makes the AI security observation Jen would make. Verify:
- Score is reduced by 1 from baseline
- Reduction is logged with overlapping comment text
- Score does not reduce below 1

**Test 1.12 - Score 3 for specific technical detail**

Provide a record with content: "We're implementing tool-level permissions for our LangChain agent - any best practices for runtime verification?" Verify:
- Score 3 is returned
- Rationale references specific technical detail (tool permissions, runtime verification)
- Angle identified as directly relevant to Gen Digital expertise

**Test 1.13 - Score 0 for generic AI content**

Provide a record that matched on "AI" keyword but contains no security or agent angle. Verify:
- Score 0 is returned
- Golden Rule cited in rationale
- Evaluation terminates

---

#### Persona Clarity Evaluator Tests

**Test 1.14 - Score 2 for unambiguous Observer**

Provide a record with industry commentary, no questions asked. Verify:
- Score 2
- persona_determination: "observer"
- persona_confidence: "high"

**Test 1.15 - Score 2 for unambiguous Advisor**

Provide a record with explicit technical question ("How do I prevent prompt injection?"). Verify:
- Score 2
- persona_determination: "advisor"
- persona_confidence: "high"

**Test 1.16 - Score 2 for unambiguous Connector**

Provide a record with "We're evaluating agent security tools" (clear buying signal). Verify:
- Score 2 (if Connector mode enabled)
- persona_determination: "connector"
- persona_confidence: "high"

**Test 1.17 - Score 0 for ambiguous help-seeking/venting**

Provide a record with frustrated tone that could be venting or seeking help. Verify:
- Score 0
- `yellow_tier_flag` is set
- persona_determination: null
- persona_confidence: null

**Test 1.18 - Connector disabled handling**

Provide a record with buying signals BUT Connector mode disabled in campaign settings. Verify:
- Connector is NOT determined even with signals present
- Advisor or Observer is determined instead
- Connector disabled state is logged

---

#### Composite Score Calculator Tests

**Test 1.19 - Correct composite calculation**

Provide dimension scores:
- risk_level: 0
- engagement_potential: 3
- jen_angle_strength: 2
- persona_clarity: 2

Verify: composite_score = 7, outcome = "engage_immediately"

**Test 1.20 - Red-tier produces null composite**

Provide a record where `red_tier_terminated = true`. Verify:
- composite_score is null
- outcome is "red_tier"
- Other dimension scores not included in calculation

**Test 1.21 - Zero angle produces score 0**

Provide a record where `zero_angle_terminated = true` with engagement_potential 3 and persona_clarity 2. Verify:
- composite_score is 0 (despite positive other scores)
- outcome is "do_not_engage"

**Test 1.22 - Yellow flag preserved in composite**

Provide dimension scores:
- risk_level: -1 (Yellow flag)
- engagement_potential: 3
- jen_angle_strength: 3
- persona_clarity: 2

Verify:
- composite_score = 7 (-1 + 3 + 3 + 2)
- outcome = "engage_immediately"
- yellow_tier_flag = true
- Tier Classifier will override routing

---

#### Tier Classifier Tests

**Test 1.23 - Red-tier routes to red_tier queue**

Provide Calculator output with outcome "red_tier". Verify:
- tier = "red"
- routing_queue = "red_tier"
- priority = 5

**Test 1.24 - Yellow-tier overrides engage_immediately**

Provide Calculator output with outcome "engage_immediately" and yellow_tier_flag true. Verify:
- tier = "yellow"
- routing_queue = "yellow_tier" (not "priority_review")
- priority = 1 (if Phase 1)

**Test 1.25 - Persona Clarity 0 applies Yellow override**

Provide Calculator output with outcome "engage_standard" and persona_clarity_score 0. Verify:
- tier = "yellow"
- routing_queue = "yellow_tier"
- persona_determination = null

**Test 1.26 - Green-tier routing correct**

Provide Calculator output with outcome "engage_immediately", no Yellow flags, Phase 1 timing. Verify:
- tier = "green"
- routing_queue = "priority_review"
- priority = 1

---

### Phase 2: Integration Tests

**Integration Test 1: Full pipeline - engage_immediately outcome**

Place a discovery record representing a Phase 1 technical question about agent security from a verified author with high velocity. Run full Scoring Component evaluation. Verify:
- Status updated to "pending_priority_review"
- Routing entry exists with queue_name "priority_review" and priority 1
- scoring_result JSON is complete with all four dimension evaluations
- composite_score is 6, 7, or 8

**Integration Test 2: Red-tier termination and routing**

Place a discovery record about an active security breach. Run evaluation. Verify:
- Evaluation terminates after Risk Level
- Other dimensions NOT evaluated (absent from scoring_result)
- Status = "red_tier"
- Routing entry exists with queue_name "red_tier"
- composite_score is null

**Integration Test 3: Yellow-tier override from Risk Level**

Place a discovery record for security incident discussion (Yellow flag) with high engagement and strong angle. Run evaluation. Verify:
- Composite score is calculated and is 5+
- tier = "yellow" despite high score
- routing_queue = "yellow_tier"
- Yellow flag condition documented in scoring_result

**Integration Test 4: Zero angle termination**

Place a discovery record for generic AI tweet ("AI is amazing!"). Run evaluation. Verify:
- Evaluation terminates after Jen Angle Strength
- Persona Clarity NOT evaluated
- composite_score = 0
- outcome = "do_not_engage"

**Integration Test 5: Phase drift detection**

Place a record with timing_phase "phase_1" representing content created 8 hours ago. Run evaluation. Verify:
- Evaluator uses Phase 2 in Engagement Potential
- phase_drift_detected = true in metadata
- scoring_result records both original and current phases
- Engagement Potential score reflects Phase 2 criteria

**Integration Test 6: Persona ambiguity triggers Yellow-tier**

Place a record where persona determination is genuinely ambiguous (frustrated humor). Run evaluation. Verify:
- Persona Clarity scores 0
- Yellow-tier override applied
- routing_queue = "yellow_tier"
- persona_determination = null

---

### Phase 3: Calibration Tests

Calibration tests verify that the scoring framework produces scores aligned with expected outcomes for reference content examples.

**Calibration Test 1: Anchor Examples**

Define 12 anchor examples with pre-approved expected score ranges:

| # | Content Type | Expected Outcome | Expected Composite |
|---|--------------|------------------|-------------------|
| 1 | Phase 1 technical question, high velocity | engage_immediately | 7-8 |
| 2 | Phase 2 help-seeking, moderate velocity | engage_standard | 5-6 |
| 3 | Generic AI commentary, no angle | do_not_engage | 0 |
| 4 | Industry news, Observer mode clear | pass or engage_standard | 3-6 |
| 5 | Active security incident (Red-tier) | red_tier | null |
| 6 | Security discussion, educational (Yellow) | yellow_tier | 5-7 |
| 7 | Frustrated rant, persona ambiguous (Yellow) | yellow_tier | 4-6 |
| 8 | Buying signals, Connector opportunity | engage_immediately | 6-8 |
| 9 | Competitor product question | engage_standard | 5-6 |
| 10 | Expired content, high historical engagement | pass | 2-4 |
| 11 | Gen Digital negative mention | red_tier | null |
| 12 | Strong angle, low engagement potential | pass | 3-4 |

Run Scoring Component against each anchor example. Verify every example produces a composite score within its expected range and routes to the expected queue.

**If any anchor example produces an out-of-range score, do not adjust the expected range—adjust the scoring logic.** Anchor examples are fixed references that define what correct scoring looks like.

**Calibration Test 2: Score Distribution Check**

Run Scoring Component against 100+ discovery records from production-like data. Review distribution:

| Outcome | Expected Range |
|---------|---------------|
| engage_immediately | 10-15% |
| engage_standard | 20-30% |
| pass | 20-30% |
| do_not_engage | 20-30% |
| yellow_tier | 5-10% |
| red_tier | <5% |

If distribution is significantly skewed (e.g., 70% engage_immediately), the framework is miscalibrated. Review dimension evaluator criteria and adjust thresholds.

---

## 7.4.13 Implementation Sign-Off Checklist

The Scoring Component is complete when every item is confirmed:

### Core Functionality

```
□ All Phase 1 unit tests pass without test modifications
□ All Phase 2 integration tests pass
□ All Phase 3 calibration tests pass with approved expected ranges
□ Anchor examples documented and approved
```

### Termination Conditions

```
□ Risk Level -3 terminates immediately (Red-tier)
□ Jen Angle Strength 0 terminates immediately (Do Not Engage)
□ Yellow-tier flags force review but don't terminate
□ Termination flags correctly set and propagated
```

### Dimension Evaluators

```
□ Risk Level: All Red conditions checked before Yellow
□ Risk Level: Multiple Yellow flags can exist on same post
□ Engagement Potential: Phase drift detection working
□ Engagement Potential: Phase 1 required for score 3
□ Jen Angle Strength: Golden Rule enforced (no generic comments)
□ Jen Angle Strength: Top comments check performed
□ Persona Clarity: Observer default when signals absent
□ Persona Clarity: Connector mode respects campaign settings
```

### Scoring Quality

```
□ Score rationales are specific (not generic)
□ All dimension evaluations logged with inputs used
□ Scoring duration averaging under 2 seconds per record
□ Idempotent evaluation verified (same input = same output)
```

### Database Operations

```
□ Transaction atomicity confirmed (no partial writes)
□ Retry logic confirmed on write failure
□ Concurrent modification detection working
□ Session metrics updating correctly
```

### Queue Routing

```
□ Priority review queue populated correctly
□ Standard review queue populated correctly
□ Yellow-tier queue populated correctly
□ Red-tier log populated correctly
□ Do Not Engage log populated correctly
□ Priority assignment correct by timing phase
```

### Human Review Integration

```
□ Yellow-tier posts require human review before generation
□ Persona determination passed to generation (or null for human decision)
□ Yellow flag reasons visible to reviewers
□ Red-tier posts never reach generation
```

---

## 7.4.14 Summary

The enhanced four-dimension scoring framework provides:

1. **Risk Level** - Safety termination for dangerous content
2. **Engagement Potential** - Opportunity sizing for timing and visibility
3. **Jen Angle Strength** - Quality enforcement via the Golden Rule
4. **Persona Clarity** - Mode selection with human review for ambiguity

Together, these dimensions ensure that:
- Dangerous content is never engaged with
- Stale or low-visibility content is deprioritized appropriately
- Generic comments are never generated
- The correct persona is selected (or a human decides)

The framework produces five outcomes:
- **Engage Immediately** - High priority, time-sensitive
- **Engage Standard** - Worth engaging, not urgent
- **Pass** - Below threshold
- **Do Not Engage** - No angle exists
- **Red Tier** - Categorically off-limits

With Yellow-tier override forcing human review when:
- Content has elevated sensitivity
- Persona cannot be confidently determined

This framework closes the gap between "finding relevant content" and "producing valuable engagement" by ensuring that every post that reaches Response Generation has both something worth saying AND a clear understanding of how to say it.

