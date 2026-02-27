#!/usr/bin/env python3
"""
JEN ENHANCED SCORING - COMPLETE IMPLEMENTATION
===============================================

Four-dimension scoring framework for the Jen social engagement agent.

Dimensions:
1. Risk Level (-3, -1, 0) - Safety and sensitivity
2. Engagement Potential (0-3) - Opportunity size
3. Jen Angle Strength (0-3) - Can we say something specific?
4. Persona Clarity (0-2) - Which persona should engage?

Key features:
- Hard termination on Risk -3 (Red-tier) or Angle 0 (Golden Rule)
- Yellow-tier override forces human review
- Detailed score rationales for calibration
- Complete evaluation metadata

Usage:
    from jen_enhanced_scoring_complete import score_post, ScoringConfig
    
    result = score_post(post_data)
    print(f"Score: {result.composite_score}, Outcome: {result.outcome}")
"""

from __future__ import annotations

import logging
import re
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID, uuid4


# =============================================================================
# ENUMS
# =============================================================================

class RiskTier(str, Enum):
    GREEN = "green"
    YELLOW = "yellow"
    RED = "red"


class Outcome(str, Enum):
    ENGAGE_IMMEDIATELY = "engage_immediately"
    ENGAGE_STANDARD = "engage_standard"
    PASS = "pass"
    DO_NOT_ENGAGE = "do_not_engage"
    RED_TIER = "red_tier"


class RoutingQueue(str, Enum):
    PRIORITY_REVIEW = "priority_review"
    STANDARD_REVIEW = "standard_review"
    YELLOW_TIER = "yellow_tier"
    PASSED_LOG = "passed_log"
    DO_NOT_ENGAGE_LOG = "do_not_engage_log"
    RED_TIER_LOG = "red_tier_log"


class Persona(str, Enum):
    OBSERVER = "observer"
    ADVISOR = "advisor"
    CONNECTOR = "connector"


class PersonaConfidence(str, Enum):
    HIGH = "high"
    MODERATE = "moderate"
    NONE = "none"


class TimingPhase(str, Enum):
    PHASE_1 = "phase_1"
    PHASE_2 = "phase_2"
    PHASE_3 = "phase_3"
    EXPIRED = "expired"


# =============================================================================
# DATACLASSES
# =============================================================================

@dataclass
class RiskLevelResult:
    score: int
    tier: RiskTier
    score_rationale: str
    inputs_used: List[str]
    red_flags: List[str] = field(default_factory=list)
    yellow_flags: List[str] = field(default_factory=list)
    termination_triggered: bool = False
    evaluation_duration_ms: float = 0.0


@dataclass
class EngagementPotentialResult:
    score: int
    score_rationale: str
    inputs_used: List[str]
    timing_phase: TimingPhase
    velocity_ratio: Optional[float] = None
    phase_drift_detected: bool = False
    original_phase: Optional[TimingPhase] = None
    amplifying_signals: List[str] = field(default_factory=list)
    evaluation_duration_ms: float = 0.0


@dataclass
class JenAngleStrengthResult:
    score: int
    score_rationale: str
    inputs_used: List[str]
    termination_triggered: bool = False
    angle_description: Optional[str] = None
    expertise_area_match: Optional[str] = None
    top_comment_check: Optional[Dict[str, Any]] = None
    golden_rule_passed: bool = True
    evaluation_duration_ms: float = 0.0


@dataclass
class PersonaClarityResult:
    score: int
    score_rationale: str
    inputs_used: List[str]
    persona_determination: Optional[Persona] = None
    persona_confidence: PersonaConfidence = PersonaConfidence.NONE
    yellow_flag_applied: bool = False
    signals_detected: Dict[str, List[str]] = field(default_factory=dict)
    evaluation_duration_ms: float = 0.0


@dataclass
class DimensionScores:
    risk_level: int
    engagement_potential: int
    jen_angle_strength: int
    persona_clarity: int


@dataclass
class TerminationFlags:
    red_tier_terminated: bool = False
    zero_angle_terminated: bool = False
    yellow_tier_override: bool = False


@dataclass
class ScoringConfig:
    connector_enabled: bool = True
    connector_blend_weight: float = 0.1
    timing_windows: Dict[str, Dict[str, int]] = field(default_factory=lambda: {
        "twitter": {"phase_1": 4, "phase_2": 12, "phase_3": 24, "max": 24},
        "linkedin": {"phase_1": 12, "phase_2": 48, "phase_3": 72, "max": 72},
        "reddit": {"phase_1": 6, "phase_2": 24, "phase_3": 48, "max": 48},
        "hackernews": {"phase_1": 4, "phase_2": 12, "phase_3": 24, "max": 24},
        "discord": {"phase_1": 2, "phase_2": 6, "phase_3": 12, "max": 12},
    })
    high_priority_authors: List[str] = field(default_factory=list)


@dataclass
class ScoringResult:
    post_id: UUID
    scored_at: datetime
    scoring_duration_ms: float
    composite_score: Optional[float]
    outcome: Outcome
    tier: RiskTier
    routing_queue: RoutingQueue
    priority: int
    persona_determination: Optional[Persona]
    persona_confidence: PersonaConfidence
    dimension_scores: DimensionScores
    risk_level_evaluation: RiskLevelResult
    engagement_potential_evaluation: EngagementPotentialResult
    jen_angle_strength_evaluation: Optional[JenAngleStrengthResult]
    persona_clarity_evaluation: Optional[PersonaClarityResult]
    termination_flags: TerminationFlags
    yellow_tier_reasons: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "post_id": str(self.post_id),
            "scored_at": self.scored_at.isoformat(),
            "composite_score": self.composite_score,
            "outcome": self.outcome.value,
            "tier": self.tier.value,
            "routing_queue": self.routing_queue.value,
            "priority": self.priority,
            "persona_determination": self.persona_determination.value if self.persona_determination else None,
            "dimension_scores": {
                "risk_level": self.dimension_scores.risk_level,
                "engagement_potential": self.dimension_scores.engagement_potential,
                "jen_angle_strength": self.dimension_scores.jen_angle_strength,
                "persona_clarity": self.dimension_scores.persona_clarity,
            },
        }


# =============================================================================
# RISK LEVEL EVALUATOR
# =============================================================================

RED_PATTERNS = {
    "death_actual": [r"\b(rip|rest in peace)\b.*\b(died|passed away)\b"],
    "mental_health_crisis": [r"\b(suicidal|self[- ]harm)\b"],
    "active_news_event": [r"\b(breaking|happening now)\b"],
    "gen_digital_negative": [r"\b(gen digital|agent trust hub)\b.*\b(sucks|terrible|failed)\b"],
}

YELLOW_PATTERNS = {
    "health_illness_content": [r"\b(cancer|hospital|surgery)\b"],
    "security_incident_discussion": [r"\b(breach|cve|vulnerability)\b"],
    "named_company_negative": [r"\b(openai|anthropic)\b.*\b(terrible|broken)\b"],
}

METAPHORICAL_INDICATORS = ["production", "server", "deployment", "code", "app", "database"]


class RiskLevelEvaluator:
    def __init__(self):
        self.red_patterns = {k: [re.compile(p, re.I) for p in v] for k, v in RED_PATTERNS.items()}
        self.yellow_patterns = {k: [re.compile(p, re.I) for p in v] for k, v in YELLOW_PATTERNS.items()}
    
    def evaluate(self, post: Dict[str, Any]) -> RiskLevelResult:
        start = time.time()
        content = post.get("content_text", "")
        content_lower = content.lower()
        
        # Check Red-tier
        red_flags = []
        for cond, patterns in self.red_patterns.items():
            for p in patterns:
                if p.search(content):
                    if cond == "death_actual" and self._is_metaphorical(content_lower):
                        continue
                    red_flags.append(cond)
                    break
        
        if self._is_gen_digital_negative(post):
            red_flags.append("gen_digital_negative")
        
        if red_flags:
            return RiskLevelResult(
                score=-3, tier=RiskTier.RED,
                score_rationale=f"Red-tier: {red_flags}. TERMINATED.",
                inputs_used=["content_text"], red_flags=red_flags,
                termination_triggered=True,
                evaluation_duration_ms=(time.time() - start) * 1000
            )
        
        # Check Yellow-tier
        yellow_flags = []
        for cond, patterns in self.yellow_patterns.items():
            for p in patterns:
                if p.search(content):
                    yellow_flags.append(cond)
                    break
        
        if yellow_flags:
            return RiskLevelResult(
                score=-1, tier=RiskTier.YELLOW,
                score_rationale=f"Yellow-tier: {yellow_flags}. Human review required.",
                inputs_used=["content_text"], yellow_flags=yellow_flags,
                termination_triggered=False,
                evaluation_duration_ms=(time.time() - start) * 1000
            )
        
        return RiskLevelResult(
            score=0, tier=RiskTier.GREEN,
            score_rationale="Green-tier: No risk signals.",
            inputs_used=["content_text"],
            evaluation_duration_ms=(time.time() - start) * 1000
        )
    
    def _is_metaphorical(self, text: str) -> bool:
        return sum(1 for i in METAPHORICAL_INDICATORS if i in text) >= 2
    
    def _is_gen_digital_negative(self, post: Dict) -> bool:
        text = post.get("content_text", "").lower()
        mentions = ["gen digital", "agent trust hub"]
        negatives = ["sucks", "terrible", "failed", "broken"]
        return any(m in text for m in mentions) and any(n in text for n in negatives)


# =============================================================================
# ENGAGEMENT POTENTIAL EVALUATOR
# =============================================================================

DEFAULT_WINDOWS = {
    "twitter": {"phase_1": 4, "phase_2": 12, "phase_3": 24, "max": 24},
    "linkedin": {"phase_1": 12, "phase_2": 48, "phase_3": 72, "max": 72},
    "reddit": {"phase_1": 6, "phase_2": 24, "phase_3": 48, "max": 48},
}


class EngagementPotentialEvaluator:
    def __init__(self, config: ScoringConfig = None):
        self.config = config or ScoringConfig()
        self.windows = self.config.timing_windows or DEFAULT_WINDOWS
    
    def evaluate(self, post: Dict[str, Any]) -> EngagementPotentialResult:
        start = time.time()
        platform = post.get("platform", "twitter").lower()
        created_at = post.get("created_at")
        metrics = post.get("metrics", {})
        author = post.get("author", {})
        comments = post.get("top_existing_comments", [])
        
        phase, age = self._calc_phase(created_at, platform)
        
        if phase == TimingPhase.EXPIRED:
            return EngagementPotentialResult(
                score=0, timing_phase=phase,
                score_rationale=f"Expired ({age:.1f}h old)",
                inputs_used=["created_at"],
                evaluation_duration_ms=(time.time() - start) * 1000
            )
        
        if not metrics.get("metrics_available", True):
            return EngagementPotentialResult(
                score=0, timing_phase=phase,
                score_rationale="No metrics available",
                inputs_used=["metrics"],
                evaluation_duration_ms=(time.time() - start) * 1000
            )
        
        velocity = self._calc_velocity(metrics, age, platform)
        signals = self._check_signals(post, author, comments)
        
        # Score calculation
        if phase == TimingPhase.PHASE_1 and velocity >= 2.0 and len(comments) >= 3 and signals:
            score, rationale = 3, f"Score 3: Phase 1, velocity {velocity:.1f}, signals: {signals}"
        elif phase == TimingPhase.PHASE_1 and velocity >= 1.0:
            score, rationale = 2, f"Score 2: Phase 1, velocity {velocity:.1f}"
        elif phase == TimingPhase.PHASE_2 and velocity >= 2.0 and signals:
            score, rationale = 2, f"Score 2: Phase 2, velocity {velocity:.1f}, signals: {signals}"
        elif velocity >= 1.0:
            score, rationale = 1, f"Score 1: {phase.value}, velocity {velocity:.1f}"
        else:
            score, rationale = 0, f"Score 0: velocity {velocity:.1f} below threshold"
        
        return EngagementPotentialResult(
            score=score, timing_phase=phase, velocity_ratio=velocity,
            score_rationale=rationale, inputs_used=["metrics", "created_at"],
            amplifying_signals=signals,
            evaluation_duration_ms=(time.time() - start) * 1000
        )
    
    def _calc_phase(self, created_at, platform: str) -> Tuple[TimingPhase, float]:
        if not created_at:
            return TimingPhase.PHASE_2, 12.0
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)
        age = (datetime.now(timezone.utc) - created_at).total_seconds() / 3600
        w = self.windows.get(platform, DEFAULT_WINDOWS["twitter"])
        if age <= w["phase_1"]: return TimingPhase.PHASE_1, age
        if age <= w["phase_2"]: return TimingPhase.PHASE_2, age
        if age <= w["phase_3"]: return TimingPhase.PHASE_3, age
        return TimingPhase.EXPIRED, age
    
    def _calc_velocity(self, metrics: Dict, age: float, platform: str) -> float:
        likes = metrics.get("likes", 0) or 0
        replies = metrics.get("replies", 0) or metrics.get("comments", 0) or 0
        shares = metrics.get("shares", 0) or 0
        actual = likes + replies * 2 + shares * 1.5
        expected = {"twitter": 10, "linkedin": 5, "reddit": 15}.get(platform, 10) * max(age, 0.5)
        return actual / expected if expected > 0 else 0
    
    def _check_signals(self, post: Dict, author: Dict, comments: List) -> List[str]:
        signals = []
        if author.get("verified"): signals.append("verified")
        if (author.get("follower_count") or 0) >= 50000: signals.append("high_followers")
        if len(comments) >= 3: signals.append("active_comments")
        return signals


# =============================================================================
# JEN ANGLE STRENGTH EVALUATOR
# =============================================================================

EXPERTISE_AREAS = {
    "agent_runtime_security": ["runtime", "monitoring", "verification"],
    "tool_use_authorization": ["tool use", "tool calling", "permissions"],
    "prompt_injection_defense": ["prompt injection", "jailbreak"],
}

TIER_1_KEYWORDS = ["agent security", "runtime verification", "prompt injection"]
TIER_2_KEYWORDS = ["langchain security", "llm security", "guardrails"]


class JenAngleStrengthEvaluator:
    def __init__(self, config: ScoringConfig = None):
        self.config = config or ScoringConfig()
    
    def evaluate(self, post: Dict[str, Any]) -> JenAngleStrengthResult:
        start = time.time()
        content = post.get("content_text", "")
        content_lower = content.lower()
        keywords = post.get("keyword_matches", [])
        classification = post.get("classification", "")
        
        # Check for zero conditions
        if self._is_gen_digital_negative(content_lower):
            return JenAngleStrengthResult(
                score=0, termination_triggered=True, golden_rule_passed=False,
                score_rationale="Score 0: Gen Digital negative. TERMINATED.",
                inputs_used=["content_text"],
                evaluation_duration_ms=(time.time() - start) * 1000
            )
        
        if self._is_generic(content_lower) and not keywords:
            return JenAngleStrengthResult(
                score=0, termination_triggered=True, golden_rule_passed=False,
                score_rationale="Score 0: Generic content, no angle. TERMINATED.",
                inputs_used=["content_text"],
                evaluation_duration_ms=(time.time() - start) * 1000
            )
        
        # Find expertise match
        expertise = self._find_expertise(content_lower, keywords)
        has_question = "?" in content and any(k in content_lower for k in ["how", "what", "why", "help"])
        has_specifics = bool(re.search(r'\d+\s*(agents?|apis?|calls?)', content, re.I))
        
        # Calculate score
        score = 0
        factors = []
        
        if expertise:
            score = 2
            factors.append(f"expertise: {expertise}")
        
        if has_question:
            score = max(score, 2)
            factors.append("actionable question")
        
        if has_specifics:
            score = min(score + 1, 3)
            factors.append("specific details")
        
        if any(k.lower() in content_lower for k in TIER_1_KEYWORDS):
            score = max(score, 2)
            factors.append("Tier 1 keyword")
        
        if classification in ["technical_question", "help_seeking"]:
            score = max(score, 2)
            factors.append(f"classification: {classification}")
        
        if score == 0:
            return JenAngleStrengthResult(
                score=0, termination_triggered=True, golden_rule_passed=False,
                score_rationale="Score 0: No specific angle found. TERMINATED.",
                inputs_used=["content_text", "classification"],
                evaluation_duration_ms=(time.time() - start) * 1000
            )
        
        return JenAngleStrengthResult(
            score=score, termination_triggered=False, golden_rule_passed=True,
            score_rationale=f"Score {score}: {'; '.join(factors)}",
            inputs_used=["content_text", "keyword_matches", "classification"],
            expertise_area_match=expertise,
            evaluation_duration_ms=(time.time() - start) * 1000
        )
    
    def _is_gen_digital_negative(self, text: str) -> bool:
        mentions = ["gen digital", "agent trust hub"]
        negatives = ["sucks", "terrible", "failed", "hate"]
        return any(m in text for m in mentions) and any(n in text for n in negatives)
    
    def _is_generic(self, text: str) -> bool:
        generic = ["ai is", "the future", "amazing", "game changer"]
        return sum(1 for g in generic if g in text) >= 2
    
    def _find_expertise(self, text: str, keywords: List[str]) -> Optional[str]:
        for area, terms in EXPERTISE_AREAS.items():
            if any(t in text for t in terms):
                return area
        return None


# =============================================================================
# PERSONA CLARITY EVALUATOR
# =============================================================================

ADVISOR_SIGNALS = [r"how (do|can|should)", r"help|advice|struggling", r"\?$"]
OBSERVER_SIGNALS = [r"just (shipped|launched)", r"my (thoughts|take)"]
CONNECTOR_SIGNALS = [r"looking for.*(tool|solution)", r"evaluating"]


class PersonaClarityEvaluator:
    def __init__(self, config: ScoringConfig = None):
        self.config = config or ScoringConfig()
        self.advisor_patterns = [re.compile(p, re.I) for p in ADVISOR_SIGNALS]
        self.observer_patterns = [re.compile(p, re.I) for p in OBSERVER_SIGNALS]
        self.connector_patterns = [re.compile(p, re.I) for p in CONNECTOR_SIGNALS]
    
    def evaluate(self, post: Dict[str, Any]) -> PersonaClarityResult:
        start = time.time()
        content = post.get("content_text", "")
        classification = post.get("classification", "")
        
        advisor = sum(1 for p in self.advisor_patterns if p.search(content))
        observer = sum(1 for p in self.observer_patterns if p.search(content))
        connector = sum(1 for p in self.connector_patterns if p.search(content)) if self.config.connector_enabled else 0
        
        # Classification boost
        if classification in ["technical_question", "help_seeking"]:
            advisor += 2
        elif classification in ["news_announcement", "industry_commentary"]:
            observer += 2
        
        # Determine persona
        signals = {"advisor": advisor, "observer": observer, "connector": connector}
        max_sig = max(signals.values())
        
        if max_sig == 0:
            persona, conf, score = Persona.OBSERVER, PersonaConfidence.MODERATE, 1
        elif advisor == max_sig and advisor >= 2:
            persona, conf, score = Persona.ADVISOR, PersonaConfidence.HIGH, 2
        elif observer == max_sig and observer >= 2:
            persona, conf, score = Persona.OBSERVER, PersonaConfidence.HIGH, 2
        elif connector == max_sig and connector >= 2:
            persona, conf, score = Persona.CONNECTOR, PersonaConfidence.HIGH, 2
        elif max_sig >= 1:
            winning = max(signals.items(), key=lambda x: x[1])
            persona = Persona[winning[0].upper()]
            conf, score = PersonaConfidence.MODERATE, 1
        else:
            persona, conf, score = None, PersonaConfidence.NONE, 0
        
        return PersonaClarityResult(
            score=score, persona_determination=persona, persona_confidence=conf,
            score_rationale=f"Score {score}: {persona.value if persona else 'undetermined'} ({conf.value})",
            inputs_used=["content_text", "classification"],
            signals_detected=signals,
            yellow_flag_applied=(score == 0),
            evaluation_duration_ms=(time.time() - start) * 1000
        )


# =============================================================================
# COMPOSITE CALCULATOR & TIER CLASSIFIER
# =============================================================================

class CompositeScoreCalculator:
    def calculate(self, risk: RiskLevelResult, engagement: EngagementPotentialResult,
                  angle: Optional[JenAngleStrengthResult], persona: Optional[PersonaClarityResult]):
        
        flags = TerminationFlags()
        
        if risk.termination_triggered:
            flags.red_tier_terminated = True
            return {
                "composite_score": None,
                "outcome": Outcome.RED_TIER,
                "dimension_scores": DimensionScores(risk.score, 0, 0, 0),
                "termination_flags": flags,
                "yellow_tier_flag": False,
                "persona": None,
                "persona_confidence": PersonaConfidence.NONE,
            }
        
        if angle and angle.termination_triggered:
            flags.zero_angle_terminated = True
            return {
                "composite_score": 0,
                "outcome": Outcome.DO_NOT_ENGAGE,
                "dimension_scores": DimensionScores(risk.score, engagement.score, 0, 0),
                "termination_flags": flags,
                "yellow_tier_flag": False,
                "persona": None,
                "persona_confidence": PersonaConfidence.NONE,
            }
        
        composite = risk.score + engagement.score + (angle.score if angle else 0) + (persona.score if persona else 0)
        
        if composite >= 7: outcome = Outcome.ENGAGE_IMMEDIATELY
        elif composite >= 5: outcome = Outcome.ENGAGE_STANDARD
        elif composite >= 3: outcome = Outcome.PASS
        else: outcome = Outcome.DO_NOT_ENGAGE
        
        yellow = risk.tier == RiskTier.YELLOW or (persona and persona.yellow_flag_applied)
        if yellow: flags.yellow_tier_override = True
        
        return {
            "composite_score": composite,
            "outcome": outcome,
            "dimension_scores": DimensionScores(
                risk.score, engagement.score,
                angle.score if angle else 0,
                persona.score if persona else 0
            ),
            "termination_flags": flags,
            "yellow_tier_flag": yellow,
            "persona": persona.persona_determination if persona else None,
            "persona_confidence": persona.persona_confidence if persona else PersonaConfidence.NONE,
        }


class TierClassifier:
    def classify(self, calc_result: Dict, timing_phase: TimingPhase):
        flags = calc_result["termination_flags"]
        
        if flags.red_tier_terminated:
            return {"tier": RiskTier.RED, "queue": RoutingQueue.RED_TIER_LOG, "priority": 5}
        
        if calc_result["yellow_tier_flag"]:
            priority = {TimingPhase.PHASE_1: 1, TimingPhase.PHASE_2: 2}.get(timing_phase, 3)
            return {"tier": RiskTier.YELLOW, "queue": RoutingQueue.YELLOW_TIER, "priority": priority}
        
        outcome = calc_result["outcome"]
        queue_map = {
            Outcome.ENGAGE_IMMEDIATELY: RoutingQueue.PRIORITY_REVIEW,
            Outcome.ENGAGE_STANDARD: RoutingQueue.STANDARD_REVIEW,
            Outcome.PASS: RoutingQueue.PASSED_LOG,
            Outcome.DO_NOT_ENGAGE: RoutingQueue.DO_NOT_ENGAGE_LOG,
        }
        priority = {TimingPhase.PHASE_1: 1, TimingPhase.PHASE_2: 2}.get(timing_phase, 3)
        
        return {"tier": RiskTier.GREEN, "queue": queue_map.get(outcome, RoutingQueue.DO_NOT_ENGAGE_LOG), "priority": priority}


# =============================================================================
# EVALUATION ENGINE
# =============================================================================

class EvaluationEngine:
    def __init__(self, config: ScoringConfig = None):
        self.config = config or ScoringConfig()
        self.risk = RiskLevelEvaluator()
        self.engagement = EngagementPotentialEvaluator(self.config)
        self.angle = JenAngleStrengthEvaluator(self.config)
        self.persona = PersonaClarityEvaluator(self.config)
        self.calculator = CompositeScoreCalculator()
        self.classifier = TierClassifier()
    
    def evaluate(self, post: Dict[str, Any]) -> ScoringResult:
        start = time.time()
        post_id = UUID(post.get("id", str(uuid4()))) if isinstance(post.get("id"), str) else uuid4()
        
        # Step 1: Risk
        risk_result = self.risk.evaluate(post)
        if risk_result.termination_triggered:
            return self._terminated_result(post_id, start, risk_result, "red")
        
        # Step 2: Engagement
        engagement_result = self.engagement.evaluate(post)
        
        # Step 3: Angle
        angle_result = self.angle.evaluate(post)
        if angle_result.termination_triggered:
            return self._terminated_result(post_id, start, risk_result, "angle", engagement_result, angle_result)
        
        # Step 4: Persona
        persona_result = self.persona.evaluate(post)
        
        # Step 5: Calculate
        calc = self.calculator.calculate(risk_result, engagement_result, angle_result, persona_result)
        
        # Step 6: Classify
        tier_result = self.classifier.classify(calc, engagement_result.timing_phase)
        
        return ScoringResult(
            post_id=post_id, scored_at=datetime.now(timezone.utc),
            scoring_duration_ms=(time.time() - start) * 1000,
            composite_score=calc["composite_score"], outcome=calc["outcome"],
            tier=tier_result["tier"], routing_queue=tier_result["queue"],
            priority=tier_result["priority"],
            persona_determination=calc["persona"],
            persona_confidence=calc["persona_confidence"],
            dimension_scores=calc["dimension_scores"],
            risk_level_evaluation=risk_result,
            engagement_potential_evaluation=engagement_result,
            jen_angle_strength_evaluation=angle_result,
            persona_clarity_evaluation=persona_result,
            termination_flags=calc["termination_flags"]
        )
    
    def _terminated_result(self, post_id, start, risk, term_type, engagement=None, angle=None):
        if term_type == "red":
            return ScoringResult(
                post_id=post_id, scored_at=datetime.now(timezone.utc),
                scoring_duration_ms=(time.time() - start) * 1000,
                composite_score=None, outcome=Outcome.RED_TIER,
                tier=RiskTier.RED, routing_queue=RoutingQueue.RED_TIER_LOG, priority=5,
                persona_determination=None, persona_confidence=PersonaConfidence.NONE,
                dimension_scores=DimensionScores(risk.score, 0, 0, 0),
                risk_level_evaluation=risk,
                engagement_potential_evaluation=EngagementPotentialResult(0, "N/A", [], TimingPhase.PHASE_2),
                jen_angle_strength_evaluation=None, persona_clarity_evaluation=None,
                termination_flags=TerminationFlags(red_tier_terminated=True)
            )
        else:
            return ScoringResult(
                post_id=post_id, scored_at=datetime.now(timezone.utc),
                scoring_duration_ms=(time.time() - start) * 1000,
                composite_score=0, outcome=Outcome.DO_NOT_ENGAGE,
                tier=RiskTier.GREEN, routing_queue=RoutingQueue.DO_NOT_ENGAGE_LOG, priority=5,
                persona_determination=None, persona_confidence=PersonaConfidence.NONE,
                dimension_scores=DimensionScores(risk.score, engagement.score if engagement else 0, 0, 0),
                risk_level_evaluation=risk,
                engagement_potential_evaluation=engagement or EngagementPotentialResult(0, "N/A", [], TimingPhase.PHASE_2),
                jen_angle_strength_evaluation=angle, persona_clarity_evaluation=None,
                termination_flags=TerminationFlags(zero_angle_terminated=True)
            )


# =============================================================================
# CONVENIENCE FUNCTION
# =============================================================================

def score_post(post: Dict[str, Any], config: ScoringConfig = None) -> ScoringResult:
    """Score a single post through the four-dimension framework."""
    engine = EvaluationEngine(config)
    return engine.evaluate(post)


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    # Example usage
    example_post = {
        "id": str(uuid4()),
        "content_text": "How do I implement runtime verification for my LangChain agent? We have 15 different API tools.",
        "created_at": datetime.now(timezone.utc) - timedelta(hours=2),
        "platform": "twitter",
        "author": {"handle": "devuser", "follower_count": 5000, "verified": False},
        "metrics": {"likes": 50, "replies": 10, "shares": 5, "metrics_available": True},
        "classification": "technical_question",
        "keyword_matches": ["langchain", "runtime verification"],
        "keyword_tier": 1,
        "top_existing_comments": [{"text": "Great question!", "likes": 5}],
        "hashtags": ["#ai", "#security"],
    }
    
    result = score_post(example_post)
    
    print(f"\n{'='*60}")
    print("JEN ENHANCED SCORING - EXAMPLE OUTPUT")
    print(f"{'='*60}")
    print(f"Post ID: {result.post_id}")
    print(f"Composite Score: {result.composite_score}")
    print(f"Outcome: {result.outcome.value}")
    print(f"Tier: {result.tier.value}")
    print(f"Routing Queue: {result.routing_queue.value}")
    print(f"Priority: {result.priority}")
    print(f"Persona: {result.persona_determination.value if result.persona_determination else 'None'}")
    print(f"\nDimension Scores:")
    print(f"  Risk Level: {result.dimension_scores.risk_level}")
    print(f"  Engagement: {result.dimension_scores.engagement_potential}")
    print(f"  Angle:      {result.dimension_scores.jen_angle_strength}")
    print(f"  Persona:    {result.dimension_scores.persona_clarity}")
    print(f"\nDuration: {result.scoring_duration_ms:.2f}ms")
