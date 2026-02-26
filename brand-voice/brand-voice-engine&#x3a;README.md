# MoneyLion Brand Voice Engine

The configuration layer for MoneyLion's AI-Powered Social Engagement Agent. This repo contains everything the agent needs to sound, think, and behave like MoneyLion across TikTok, Instagram, YouTube, and X.

---

## What This Is

An AI-powered engagement engine that operates in two modes:

1. **Cultural Engagement (Brand Awareness)** — Makes witty, human-sounding comments on viral posts. Participates in trending formats. Builds familiarity through repetition and humor. Feels like a real person, not marketing copy.

2. **Finance-Relevant Engagement (Conversion-Oriented)** — Engages on posts about budgeting, credit, loans, investing. Creates short-form educational but entertaining content. Turns product features into relatable social moments.

The voice feels culturally native and unscripted while operating within strict brand and compliance guardrails.

---

## Why This Exists

Paid media costs are rising. Organic engagement is under-leveraged. Financial services brands are perceived as transactional and impersonal. Duolingo proved that personality can outperform paid spend. MoneyLion can do the same in financial services — where the personality competition is far weaker.

**Strategic flywheel:** Engagement → Visibility → Followers → Organic Reach → Traffic → Conversions

---

## Repo Structure

```text
brand-voice-engine/
├── README.md                              # This file
│
├── voice/                                 # Voice & Brand Definition
│   ├── brand_voice.md                     # Core voice definition, persona, pillars
│   ├── brand_guidelines.md                # Rules, constraints, banned words, naming
│   └── voice_config.json                  # Machine-readable config for AI agent
│
├── content/                               # Content Generation
│   ├── content_engine.md                  # Pipeline architecture, signal detection, generation
│   ├── platform_playbooks.md              # Platform-specific guides (TikTok, IG, YT, X)
│   └── copywriting_reference.md           # Tone calibration, examples, scoring rubrics
│
└── guardrails/                            # Compliance & Safety
    └── compliance_rails.json              # Automated compliance rules for the agent
```

---

## File Descriptions

### `/voice/` — Voice & Brand Definition

| File | Purpose | Used By |
|---|---|---|
| `brand_voice.md` | **Foundation.** Defines who MoneyLion is, the Irreverent Maverick personality, four voice pillars (Live Richly, Share The Secret, Roar More, No Bull$hit), tone guardrails, and the social agent persona. | System prompt layer |
| `brand_guidelines.md` | **Rules.** Banned words, product naming rules (trademarks, acceptable/unacceptable variations), writing style rules, claim qualification requirements, social-specific rules, and the WIIFM principle. | Pre-publish validation |
| `voice_config.json` | **Machine-readable config.** All voice parameters, platform settings, scoring thresholds, and anti-spam rules in structured JSON for direct integration into the agent pipeline. | Agent runtime config |

### `/content/` — Content Generation

| File | Purpose | Used By |
|---|---|---|
| `content_engine.md` | **Pipeline backbone.** Signal detection sources, relevance scoring algorithm, content mode classification (Cultural vs Finance-Relevant), generation framework with templates, publishing strategy, and proactive content ideation calendar. | Orchestration layer |
| `platform_playbooks.md` | **Platform-specific guides.** Detailed voice calibration, engagement modes, example comments, and "what NOT to do" for TikTok, Instagram, YouTube, and X. Includes cross-platform calendar and velocity targets. | Platform selection logic |
| `copywriting_reference.md` | **Quality benchmark.** Tone calibration scales, do/don't pairs with explanations, scored example outputs by voice pillar, canonical headline references, content quality rubric, and A/B testing framework. | Few-shot prompting, evaluation |

### `/guardrails/` — Compliance & Safety

| File | Purpose | Used By |
|---|---|---|
| `compliance_rails.json` | **Automated guardrails.** Banned word lists (absolute + contextual), product naming validation, claim qualifier rules, social-specific rules with severity levels, content classification for auto-publish vs human review, sensitivity topics, and disclaimer triggers. | Pre-publish compliance check |

---

## How the Agent Uses These Files

```text
┌─────────────────────────────────────────────────┐
│                 SIGNAL DETECTED                  │
│         (trending topic, mention, etc.)          │
└─────────────────────┬───────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────┐
│            CONTENT ENGINE (content_engine.md)     │
│  1. Score signal relevance                       │
│  2. Classify mode (Cultural vs Finance)          │
│  3. Select voice pillar                          │
└─────────────────────┬───────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────┐
│          PLATFORM PLAYBOOK (platform_playbooks.md)│
│  Load platform-specific config                   │
│  (formality, humor level, length, emoji rules)   │
└─────────────────────┬───────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────┐
│           GENERATE CONTENT                       │
│  System prompt: brand_voice.md + voice_config.json│
│  Few-shot examples: copywriting_reference.md     │
│  Generate 3 candidates, rank, select best        │
└─────────────────────┬───────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────┐
│         COMPLIANCE CHECK (compliance_rails.json)  │
│  1. Banned words scan                            │
│  2. Product claim validation                     │
│  3. Financial advice check                       │
│  4. Sensitivity check                            │
│  5. Disclaimer trigger check                     │
└─────────────────────┬───────────────────────────┘
                      │
              ┌───────┴───────┐
              ▼               ▼
        ┌──────────┐   ┌──────────────┐
        │AUTO-PUBLISH│  │HUMAN REVIEW  │
        │(no product│   │(product      │
        │ mentions) │   │ mentions or  │
        └──────────┘   │ sensitive)   │
                        └──────────────┘
```

---

## Key Design Decisions

1. **Markdown for humans, JSON for machines.** The `.md` files are readable by humans (designers, marketers, legal) while `.json` files are directly consumable by the agent pipeline.

2. **Separation of voice from rules.** `brand_voice.md` defines *who we are*. `brand_guidelines.md` defines *what we can't do*. The agent needs both but they serve different purposes.

3. **Platform-specific calibration.** A TikTok comment shouldn't sound like a tweet. Each platform has its own voice settings, length limits, and engagement patterns.

4. **Compliance as a gatekeeper, not a bottleneck.** Most cultural engagement can auto-publish. Only product mentions and sensitive topics require human review. This keeps the agent fast while staying safe.

5. **Scored examples over rigid templates.** Rather than hard-coding response templates, we provide scored examples and a rubric. This gives the LLM flexibility while maintaining quality standards.

---

## Integration Notes

### System Prompt Construction

```python
system_prompt = f"""
{read_file('voice/brand_voice.md')}

## Platform: {platform}
{get_platform_section('content/platform_playbooks.md', platform)}

## Rules & Guardrails
{read_file('voice/brand_guidelines.md')}

## Examples (Few-Shot)
{get_examples('content/copywriting_reference.md', mode, pillar)}
"""
```

### Runtime Config Loading

```python
config = json.load(open('voice/voice_config.json'))
platform_config = config['platform_configs'][platform]
compliance = json.load(open('guardrails/compliance_rails.json'))
```

### Pre-Publish Validation

```python
def validate(content, compliance_rules):
    # 1. Check banned words
    for word in compliance_rules['banned_words']['absolute']:
        if word.lower() in content.lower():
            return REJECTED, f"Contains banned word: {word}"

    # 2. Check contextual bans
    for rule in compliance_rules['banned_words']['contextual']:
        if rule['word'].lower() in content.lower():
            return NEEDS_REVIEW, f"Contains contextual ban: {rule['word']}"

    # 3. Check product naming
    for misspelling in compliance_rules['product_naming']['misspellings_to_reject']:
        if misspelling in content:
            return REJECTED, f"Product misspelling: {misspelling}"

    # 4. Check sensitivity
    for topic in compliance_rules['sensitivity_topics']['do_not_engage']:
        if topic_detected(content, topic):
            return REJECTED, f"Sensitive topic: {topic}"

    return APPROVED, None
```

---

## Source Materials

This Brand Voice Engine was built from the following official MoneyLion documents:

- MoneyLion Verbal Identity Guide (Brand Personality, Voice, Tone)
- ML Consumer Product Overview & Messaging
- ML Marketing Disclosures (source of truth for disclaimers)
- MoneyLion Channel Spec Guidelines
- Instacash Product Marketing Guidelines
- RoarMoney Product Marketing Guidelines
- Personal Loans Product Marketing Guidelines
- Legal & Compliance Feedback (Instacash + RoarMoney)
- MoneyLion Brand Guidelines (colors, visual identity)

---

## Contributing

When updating these files:

1. **Voice changes** require Brand team sign-off
2. **Guideline changes** require Legal & Compliance review
3. **Compliance rule changes** require L&C approval before merge
4. **Platform playbook changes** can be updated by the social/growth team
5. **Content examples** should be refreshed quarterly with top-performing real examples

---

*Built for the MoneyLion AI Hackathon 2026*