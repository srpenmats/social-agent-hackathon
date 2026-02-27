"""
Jen Response Generation - Complete Implementation
Part 8 of Social Agent Pro - Hackathon Finals

Single-file implementation of the complete Response Generation system.
Transforms scored posts and retrieved context into natural, persona-appropriate comments.

Usage:
    from jen_response_generation_complete import (
        ResponseGenerationPipeline,
        GenerationConfig,
        validate_comment,
        analyze_tone,
        run_tests
    )
    
    # Initialize pipeline
    config = GenerationConfig()
    pipeline = ResponseGenerationPipeline(config)
    
    # Process a post
    result = await pipeline.process(scored_post, context, {})
    
    # Or validate a single comment
    validation = validate_comment(comment, post, "observer")
"""

import re
import uuid
import time
import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple


# =============================================================================
# SECTION 1: ENUMS AND CONSTANTS
# =============================================================================

class Persona(Enum):
    """Jen's three persona modes."""
    OBSERVER = "observer"
    ADVISOR = "advisor"
    CONNECTOR = "connector"


class Platform(Enum):
    """Supported social platforms."""
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    REDDIT = "reddit"
    HACKERNEWS = "hackernews"


class EmotionalRegister(Enum):
    """Emotional states detected in posts."""
    FRUSTRATED = "frustrated"
    EXCITED = "excited"
    CURIOUS = "curious"
    SERIOUS = "serious"
    HUMOROUS = "humorous"
    ANXIOUS = "anxious"
    NEUTRAL = "neutral"


class ReviewPriority(Enum):
    """Review priority levels."""
    URGENT = 1
    STANDARD = 2
    LOW = 3


# Forbidden phrases that should never appear in comments
FORBIDDEN_PHRASES = [
    "as an ai", "as an assistant", "i'm an ai", "i am an ai",
    "i'd be happy to", "i would be happy to",
    "great question", "that's a great question",
    "let me help you", "i can help you with",
    "leverage", "synergy", "circle back", "going forward",
    "at the end of the day", "move the needle",
    "industry-leading", "best-in-class", "world-class",
    "cutting-edge", "revolutionary", "game-changing",
    "comprehensive solution", "seamlessly integrate",
    "check out our", "visit our website", "learn more at",
    "sign up for", "get started with",
    "actually, you should", "the correct way is",
    "you need to understand", "let me explain",
]

# Product-related terms to detect
PRODUCT_TERMS = [
    "agent trust hub", "ath", "gen digital", "gendigital",
    "our product", "our solution", "our platform", "our tool",
]

# Marketing words to avoid
MARKETING_WORDS = [
    "comprehensive", "enterprise-grade", "industry-leading", "powerful",
    "seamlessly", "robust", "cutting-edge", "innovative", "revolutionary",
]


# =============================================================================
# SECTION 2: DATA STRUCTURES
# =============================================================================

@dataclass
class PlatformConfig:
    """Configuration for a specific platform."""
    char_limit: int
    target_lengths: Dict[str, Tuple[int, int]]
    formality_adjustment: float
    emoji_allowed: bool
    max_emoji: int
    allowed_emoji: List[str]
    lowercase_okay: bool
    abbreviations_okay: bool
    special_rules: List[str] = field(default_factory=list)


# Platform configurations
PLATFORM_CONFIGS: Dict[str, PlatformConfig] = {
    "twitter": PlatformConfig(
        char_limit=280,
        target_lengths={"short": (80, 140), "standard": (150, 220), "detailed": (230, 275)},
        formality_adjustment=-0.15,
        emoji_allowed=True,
        max_emoji=2,
        allowed_emoji=["😅", "😂", "💀", "🤔", "👀"],
        lowercase_okay=True,
        abbreviations_okay=True,
    ),
    "linkedin": PlatformConfig(
        char_limit=1300,
        target_lengths={"short": (100, 200), "standard": (250, 450), "detailed": (500, 750)},
        formality_adjustment=0.1,
        emoji_allowed=True,
        max_emoji=1,
        allowed_emoji=["👆", "💡"],
        lowercase_okay=False,
        abbreviations_okay=False,
    ),
    "reddit": PlatformConfig(
        char_limit=10000,
        target_lengths={"short": (150, 300), "standard": (400, 700), "detailed": (800, 1200)},
        formality_adjustment=0.0,
        emoji_allowed=False,
        max_emoji=0,
        allowed_emoji=[],
        lowercase_okay=True,
        abbreviations_okay=True,
        special_rules=["always_disclose_affiliation", "never_promotional"],
    ),
    "hackernews": PlatformConfig(
        char_limit=5000,
        target_lengths={"short": (100, 250), "standard": (300, 500), "detailed": (600, 900)},
        formality_adjustment=0.15,
        emoji_allowed=False,
        max_emoji=0,
        allowed_emoji=[],
        lowercase_okay=False,
        abbreviations_okay=False,
        special_rules=["never_promotional", "technical_credibility"],
    ),
}


@dataclass
class GenerationConfig:
    """Configuration for response generation."""
    model: str = "claude-3-sonnet-20240229"
    default_temperature: float = 0.85
    max_tokens: int = 500
    num_candidates: int = 3
    min_diversity: float = 0.35
    max_regeneration_attempts: int = 2
    min_quality_score: float = 0.55
    max_context_chunks: int = 3
    max_context_tokens: int = 500
    
    persona_temperatures: Dict[str, float] = field(default_factory=lambda: {
        "observer": 0.85,
        "advisor": 0.80,
        "connector": 0.70,
    })
    
    def get_temperature(self, persona: str) -> float:
        return self.persona_temperatures.get(persona, self.default_temperature)


@dataclass
class ToneAnalysis:
    """Complete tone analysis of a post."""
    emotional_register: str
    energy_level: float
    formality: float
    directness: float
    is_venting: bool = False
    is_celebrating: bool = False
    is_questioning: bool = False
    is_joking: bool = False
    needs_empathy: bool = False
    signals: List[str] = field(default_factory=list)


@dataclass
class DimensionScore:
    """Score for a quality dimension."""
    score: float
    evidence: List[str] = field(default_factory=list)


@dataclass
class BlockingCheckResult:
    """Result of a blocking validation check."""
    passed: bool
    violations: List[str] = field(default_factory=list)
    check_name: str = ""


@dataclass
class ValidationResult:
    """Complete validation result for a candidate."""
    passed: bool
    overall_score: float
    blocking_issues: List[str] = field(default_factory=list)
    quality_issues: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    dimension_scores: Dict[str, float] = field(default_factory=dict)
    reviewer_notes: str = ""
    weak_dimensions: List[str] = field(default_factory=list)


@dataclass
class Candidate:
    """A generated candidate comment."""
    candidate_id: str
    candidate_num: int
    text: str
    char_count: int
    approach: str = ""
    specific_reference: str = ""
    validation_result: Optional[ValidationResult] = None
    overall_score: float = 0.0
    rank: int = 0


@dataclass
class GenerationResult:
    """Result of the generation pipeline."""
    candidates: List[Candidate]
    post_id: str
    persona: str
    diversity_score: float = 0.0
    generation_duration_ms: float = 0
    approaches_used: List[str] = field(default_factory=list)
    skipped: bool = False
    skip_reason: str = ""
    validation_pass_rate: float = 1.0


@dataclass
class ReviewerGuidance:
    """Guidance for the human reviewer."""
    quick_assessment: str
    what_to_check: List[str]
    yellow_flags: List[str]
    persona_reminder: str
    edit_suggestions: List[str] = field(default_factory=list)


@dataclass
class ReviewPackage:
    """Complete package for human review."""
    package_id: str
    created_at: datetime
    priority: int
    post: Dict
    candidates: List[Dict]
    generation_context: Dict
    reviewer_guidance: ReviewerGuidance
    generation_duration_ms: float = 0


# =============================================================================
# SECTION 3: TONE ANALYSIS
# =============================================================================

class ToneAnalyzer:
    """Analyzes tone of social media posts."""
    
    def __init__(self):
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Pre-compile regex patterns."""
        self.frustrated_patterns = [
            (re.compile(r'\b(ugh|argh|sigh)\b', re.I), 0.4),
            (re.compile(r'\b(frustrated|frustrating|annoying|annoyed)\b', re.I), 0.5),
            (re.compile(r'\b(struggling|stuck|can\'t figure out)\b', re.I), 0.4),
            (re.compile(r'\b(hate|hating|worst)\b', re.I), 0.3),
            (re.compile(r'\b(driving me crazy|losing my mind)\b', re.I), 0.5),
            (re.compile(r'why (is|does|won\'t).*\?', re.I), 0.3),
        ]
        
        self.excited_patterns = [
            (re.compile(r'\b(excited|exciting|amazing|awesome)\b', re.I), 0.4),
            (re.compile(r'\b(finally|shipped|launched|released)\b', re.I), 0.4),
            (re.compile(r'\b(love|loving)\b', re.I), 0.3),
            (re.compile(r'!{2,}'), 0.3),
            (re.compile(r'(🎉|🚀|✨|🔥)'), 0.3),
        ]
        
        self.curious_patterns = [
            (re.compile(r'\b(curious|wondering|interested in)\b', re.I), 0.4),
            (re.compile(r'\bhow (do|does|can|would)\b.*\?', re.I), 0.3),
            (re.compile(r'\bwhat (is|are|do|does)\b.*\?', re.I), 0.3),
            (re.compile(r'\b(anyone (know|tried|seen))\b', re.I), 0.3),
        ]
        
        self.serious_patterns = [
            (re.compile(r'\b(important|critical|serious|concerning)\b', re.I), 0.4),
            (re.compile(r'\b(warning|caution|careful)\b', re.I), 0.4),
            (re.compile(r'\b(security|vulnerability|risk)\b', re.I), 0.3),
        ]
        
        self.humorous_patterns = [
            (re.compile(r'\b(lol|lmao|rofl|haha)\b', re.I), 0.4),
            (re.compile(r'(😂|💀|😅|🤣)', re.I), 0.4),
            (re.compile(r'\b(joke|joking|kidding)\b', re.I), 0.3),
            (re.compile(r'\b(plot twist|hot take)\b', re.I), 0.3),
        ]
    
    def analyze(self, content: str) -> ToneAnalysis:
        """Analyze tone of post content."""
        signals = []
        
        register_scores = {
            'frustrated': 0, 'excited': 0, 'curious': 0,
            'serious': 0, 'humorous': 0, 'neutral': 0.3,
        }
        
        for pattern, score in self.frustrated_patterns:
            if pattern.search(content):
                register_scores['frustrated'] += score
                signals.append(f"frustrated: {pattern.pattern}")
        
        for pattern, score in self.excited_patterns:
            if pattern.search(content):
                register_scores['excited'] += score
                signals.append(f"excited: {pattern.pattern}")
        
        for pattern, score in self.curious_patterns:
            if pattern.search(content):
                register_scores['curious'] += score
                signals.append(f"curious: {pattern.pattern}")
        
        for pattern, score in self.serious_patterns:
            if pattern.search(content):
                register_scores['serious'] += score
                signals.append(f"serious: {pattern.pattern}")
        
        for pattern, score in self.humorous_patterns:
            if pattern.search(content):
                register_scores['humorous'] += score
                signals.append(f"humorous: {pattern.pattern}")
        
        emotional_register = max(register_scores, key=register_scores.get)
        energy_level = self._calculate_energy(content, emotional_register)
        formality = self._calculate_formality(content)
        directness = self._calculate_directness(content)
        
        content_lower = content.lower()
        
        is_venting = (
            emotional_register == 'frustrated' and 
            not re.search(r'\b(how|what|help)\b.*\?', content_lower)
        )
        
        is_celebrating = (
            emotional_register == 'excited' and
            re.search(r'\b(shipped|launched|finished|completed|finally)\b', content_lower)
        )
        
        is_questioning = bool(re.search(r'\?', content))
        is_joking = emotional_register == 'humorous'
        
        needs_empathy = (
            emotional_register in ['frustrated', 'anxious'] or
            bool(re.search(r'\b(struggling|stuck|help|lost)\b', content_lower))
        )
        
        return ToneAnalysis(
            emotional_register=emotional_register,
            energy_level=energy_level,
            formality=formality,
            directness=directness,
            is_venting=is_venting,
            is_celebrating=is_celebrating,
            is_questioning=is_questioning,
            is_joking=is_joking,
            needs_empathy=needs_empathy,
            signals=signals
        )
    
    def _calculate_energy(self, content: str, register: str) -> float:
        energy = 0.5
        if '!' in content:
            energy += 0.1 * min(content.count('!'), 3)
        if re.search(r'[A-Z]{3,}', content):
            energy += 0.15
        if register in ['excited', 'frustrated']:
            energy += 0.15
        if re.search(r'\b(tired|exhausted)\b', content.lower()):
            energy -= 0.2
        return min(1.0, max(0.0, energy))
    
    def _calculate_formality(self, content: str) -> float:
        formality = 0.5
        casual = [r'\b(lol|lmao|tbh|ngl)\b', r'\b(gonna|wanna|kinda)\b', r'^[a-z]']
        formal = [r'\b(therefore|furthermore|however)\b', r'\b(regarding|concerning)\b']
        
        for p in casual:
            if re.search(p, content, re.I):
                formality -= 0.1
        for p in formal:
            if re.search(p, content, re.I):
                formality += 0.15
        
        return min(1.0, max(0.0, formality))
    
    def _calculate_directness(self, content: str) -> float:
        directness = 0.5
        content_lower = content.lower()
        
        if re.search(r'\b(definitely|absolutely|clearly)\b', content_lower):
            directness += 0.15
        if re.search(r'\b(maybe|perhaps|might)\b', content_lower):
            directness -= 0.15
        if re.search(r'\b(I think|I guess|not sure)\b', content_lower):
            directness -= 0.1
        
        return min(1.0, max(0.0, directness))
    
    def get_guidance(self, tone: ToneAnalysis) -> Dict:
        """Get generation guidance based on tone."""
        guidance = {
            "empathy_required": tone.needs_empathy,
            "empathy_guidance": "",
            "energy_guidance": "",
            "formality_guidance": "",
            "humor_guidance": "",
            "special_notes": [],
        }
        
        if tone.needs_empathy:
            if tone.emotional_register == 'frustrated':
                guidance["empathy_guidance"] = (
                    "Acknowledge frustration first ('ugh', 'that's brutal'). "
                    "Don't jump to solutions."
                )
        
        if tone.energy_level > 0.7:
            guidance["energy_guidance"] = "HIGH: Match their energy"
        elif tone.energy_level < 0.3:
            guidance["energy_guidance"] = "LOW: Keep subdued"
        else:
            guidance["energy_guidance"] = "MEDIUM: Standard energy"
        
        if tone.formality > 0.7:
            guidance["formality_guidance"] = "PROFESSIONAL: More formal"
        elif tone.formality < 0.3:
            guidance["formality_guidance"] = "CASUAL: Match casual tone"
        else:
            guidance["formality_guidance"] = "STANDARD: Normal Jen voice"
        
        if tone.is_joking:
            guidance["humor_guidance"] = "HUMOR ALLOWED"
        elif tone.emotional_register == 'serious':
            guidance["humor_guidance"] = "NO HUMOR"
        else:
            guidance["humor_guidance"] = "HUMOR OPTIONAL"
        
        if tone.is_venting:
            guidance["special_notes"].append("VENTING: Don't offer solutions")
        if tone.is_celebrating:
            guidance["special_notes"].append("CELEBRATING: Share excitement")
        
        return guidance


def analyze_tone(content: str) -> ToneAnalysis:
    """Convenience function to analyze tone."""
    return ToneAnalyzer().analyze(content)


# =============================================================================
# SECTION 4: QUALITY VALIDATION
# =============================================================================

class QualityValidator:
    """Validates candidate comments against quality criteria."""
    
    def __init__(self, min_quality_score: float = 0.55):
        self.min_quality_score = min_quality_score
    
    def validate(self, comment: str, post: Dict, persona: str) -> ValidationResult:
        """Run complete validation pipeline."""
        
        # Layer 1: Blocking checks
        blocking_results = self._run_blocking_checks(comment, post, persona)
        
        for result in blocking_results:
            if not result.passed:
                return ValidationResult(
                    passed=False, overall_score=0,
                    blocking_issues=result.violations,
                    reviewer_notes=f"BLOCKED: {result.check_name}"
                )
        
        # Layer 2: Quality scoring
        post_content = post.get('content_text', '')
        
        specificity = self.score_specificity(comment, post_content)
        voice = self.score_voice_alignment(comment, persona)
        tone = self.score_tone_match(comment, post)
        value = self.score_value_add(comment, post_content)
        naturalness = self.score_naturalness(comment)
        
        dimension_scores = {
            'specificity': specificity.score,
            'voice': voice.score,
            'tone': tone.score,
            'value': value.score,
            'naturalness': naturalness.score,
        }
        
        # Layer 3: Composite scoring
        weights = self._get_weights(persona)
        overall = sum(dimension_scores[d] * weights[d] for d in weights)
        
        # Connector penalty
        if persona == 'connector':
            if self._score_product_appropriateness(comment) < 0.5:
                overall *= 0.7
        
        # Compile issues
        quality_issues = []
        weak_dimensions = []
        
        for dim, score in dimension_scores.items():
            if score < 0.5:
                quality_issues.append(f"Low {dim}: {score:.2f}")
                weak_dimensions.append(dim)
        
        passed = overall >= self.min_quality_score
        
        return ValidationResult(
            passed=passed,
            overall_score=overall,
            dimension_scores=dimension_scores,
            quality_issues=quality_issues,
            weak_dimensions=weak_dimensions,
            suggestions=[self._get_suggestion(d) for d in weak_dimensions],
            reviewer_notes=self._gen_notes(overall, weak_dimensions, persona)
        )
    
    def _run_blocking_checks(self, comment: str, post: Dict, persona: str) -> List[BlockingCheckResult]:
        """Run all blocking checks."""
        results = [
            self._check_persona_constraints(comment, persona),
            self._check_forbidden_content(comment),
            self._check_platform_limits(comment, post.get('platform', 'twitter')),
            self._check_minimum_content(comment),
        ]
        if persona == 'connector':
            results.append(self._check_connector_value(comment))
        return results
    
    def _check_persona_constraints(self, comment: str, persona: str) -> BlockingCheckResult:
        """Check persona-specific constraints."""
        violations = []
        
        if persona == "observer":
            if self._mentions_products(comment):
                violations.append("Product mention in Observer mode")
            if self._contains_teaching(comment):
                violations.append("Teaching language in Observer mode")
        elif persona == "advisor":
            if self._mentions_products(comment):
                violations.append("Product mention in Advisor mode")
        elif persona == "connector":
            if self._contains_recommendation(comment):
                violations.append("Recommendation in Connector mode")
            if self._contains_cta(comment):
                violations.append("CTA in Connector mode")
            if self._contains_links(comment):
                violations.append("Link in Connector mode")
        
        return BlockingCheckResult(len(violations) == 0, violations, "persona_constraints")
    
    def _check_forbidden_content(self, comment: str) -> BlockingCheckResult:
        """Check for forbidden phrases."""
        comment_lower = comment.lower()
        found = [f"Forbidden: '{p}'" for p in FORBIDDEN_PHRASES if p in comment_lower]
        return BlockingCheckResult(len(found) == 0, found, "forbidden_content")
    
    def _check_platform_limits(self, comment: str, platform: str) -> BlockingCheckResult:
        """Check platform limits."""
        config = PLATFORM_CONFIGS.get(platform)
        limit = config.char_limit if config else 280
        
        if len(comment) > limit:
            return BlockingCheckResult(False, [f"Exceeds {platform} limit"], "platform_limits")
        return BlockingCheckResult(True, [], "platform_limits")
    
    def _check_minimum_content(self, comment: str) -> BlockingCheckResult:
        """Check minimum content."""
        if len(comment.strip()) < 20:
            return BlockingCheckResult(False, ["Too short"], "minimum_content")
        if len(comment.split()) < 4:
            return BlockingCheckResult(False, ["Too few words"], "minimum_content")
        return BlockingCheckResult(True, [], "minimum_content")
    
    def _check_connector_value(self, comment: str) -> BlockingCheckResult:
        """Check Connector value independence."""
        stripped = self._remove_product_refs(comment)
        if len(stripped.split()) < 5:
            return BlockingCheckResult(False, ["No value without product"], "connector_value")
        return BlockingCheckResult(True, [], "connector_value")
    
    def score_specificity(self, comment: str, post_content: str) -> DimensionScore:
        """Score specificity to post."""
        score = 0.3
        evidence = []
        
        post_terms = self._extract_terms(post_content)
        comment_terms = self._extract_terms(comment)
        overlap = set(post_terms) & set(comment_terms)
        
        if len(overlap) >= 3:
            score += 0.3
            evidence.append(f"+overlap: {list(overlap)[:3]}")
        elif len(overlap) >= 1:
            score += 0.15
        
        if '?' in post_content and self._addresses_question(comment, post_content):
            score += 0.25
            evidence.append("+addresses_question")
        
        if self._is_generic(comment):
            score -= 0.2
            evidence.append("-generic")
        
        return DimensionScore(min(1.0, max(0.0, score)), evidence)
    
    def score_voice_alignment(self, comment: str, persona: str) -> DimensionScore:
        """Score voice alignment."""
        score = 0.5
        evidence = []
        
        if re.search(r"\b(we've|I've|we're|I'm)\b", comment):
            score += 0.1
            evidence.append("+contractions")
        if re.search(r"\b(yeah|tbh|ngl)\b", comment, re.I):
            score += 0.1
            evidence.append("+casual")
        if re.search(r"\b(we found|we've seen|what helped us)\b", comment, re.I):
            score += 0.15
            evidence.append("+experience")
        
        ai_tells = [
            (r"as an (ai|assistant)", -0.4),
            (r"i('m| am) happy to", -0.3),
            (r"great question", -0.25),
            (r"let me explain", -0.2),
        ]
        for pattern, penalty in ai_tells:
            if re.search(pattern, comment.lower()):
                score += penalty
                evidence.append("-ai_tell")
        
        if persona == "observer" and re.search(r"\b(you should|you need to)\b", comment.lower()):
            score -= 0.15
            evidence.append("-observer_teaching")
        
        return DimensionScore(min(1.0, max(0.0, score)), evidence)
    
    def score_tone_match(self, comment: str, post: Dict) -> DimensionScore:
        """Score tone match."""
        post_tone = analyze_tone(post.get('content_text', ''))
        comment_tone = analyze_tone(comment)
        
        score = 0.5
        evidence = []
        
        energy_diff = abs(post_tone.energy_level - comment_tone.energy_level)
        if energy_diff < 0.2:
            score += 0.2
            evidence.append("+energy_match")
        elif energy_diff > 0.5:
            score -= 0.2
            evidence.append("-energy_mismatch")
        
        formality_diff = abs(post_tone.formality - comment_tone.formality)
        if formality_diff < 0.2:
            score += 0.15
        elif formality_diff > 0.4:
            score -= 0.15
        
        if post_tone.emotional_register == 'frustrated':
            if self._has_empathy(comment):
                score += 0.2
                evidence.append("+empathy")
            elif comment_tone.energy_level > 0.7:
                score -= 0.2
                evidence.append("-too_upbeat")
        
        if post_tone.emotional_register == 'serious' and self._has_humor(comment):
            score -= 0.2
            evidence.append("-humor_for_serious")
        
        return DimensionScore(min(1.0, max(0.0, score)), evidence)
    
    def score_value_add(self, comment: str, post_content: str) -> DimensionScore:
        """Score value added."""
        score = 0.3
        evidence = []
        
        comment_terms = set(self._extract_terms(comment))
        post_terms = set(self._extract_terms(post_content))
        new_terms = comment_terms - post_terms
        
        if len(new_terms) >= 3:
            score += 0.2
            evidence.append("+new_concepts")
        
        if re.search(r"\b(we found|I've seen|in my experience)\b", comment, re.I):
            score += 0.2
            evidence.append("+experience")
        
        if re.search(r"\b(what|how|why|curious)\b.*\?", comment, re.I):
            score += 0.15
            evidence.append("+question")
        
        if re.match(r"^(this|so true|exactly|agree)\.?$", comment.strip(), re.I):
            score -= 0.3
            evidence.append("-zero_value")
        
        return DimensionScore(min(1.0, max(0.0, score)), evidence)
    
    def score_naturalness(self, comment: str) -> DimensionScore:
        """Score naturalness."""
        score = 0.7
        evidence = []
        
        ai_tells = [
            (r"as an ai", -0.4), (r"i('m| am) happy to", -0.3),
            (r"great question", -0.25), (r"let me explain", -0.2),
        ]
        for pattern, penalty in ai_tells:
            if re.search(pattern, comment.lower()):
                score += penalty
                evidence.append("-ai_tell")
        
        formal_patterns = [r"^(firstly|first of all)", r"\b(secondly|furthermore|moreover)\b"]
        for pattern in formal_patterns:
            if re.search(pattern, comment.lower()):
                score -= 0.1
                evidence.append("-formal")
        
        natural_patterns = [r"\b(yeah|tbh|ugh)\b", r"(😅|😂|💀)"]
        for pattern in natural_patterns:
            if re.search(pattern, comment, re.I):
                score += 0.05
        
        return DimensionScore(min(1.0, max(0.0, score)), evidence)
    
    def _get_weights(self, persona: str) -> Dict[str, float]:
        base = {'specificity': 0.30, 'voice': 0.20, 'tone': 0.15, 'value': 0.20, 'naturalness': 0.15}
        if persona == 'observer':
            base['voice'] = 0.25
            base['value'] = 0.15
        elif persona == 'advisor':
            base['value'] = 0.25
        elif persona == 'connector':
            base['naturalness'] = 0.20
        total = sum(base.values())
        return {k: v/total for k, v in base.items()}
    
    def _extract_terms(self, text: str) -> List[str]:
        words = re.findall(r'\b\w+\b', text.lower())
        stops = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'have', 'has',
                 'to', 'of', 'in', 'for', 'on', 'with', 'at', 'by', 'this', 'that',
                 'and', 'but', 'if', 'or', 'i', 'you', 'we', 'they', 'my', 'your'}
        return [w for w in words if w not in stops and len(w) > 2]
    
    def _mentions_products(self, comment: str) -> bool:
        return any(t in comment.lower() for t in PRODUCT_TERMS)
    
    def _contains_teaching(self, comment: str) -> bool:
        patterns = [r"\b(you should|you need to)\b", r"\b(let me explain|here's how)\b"]
        return any(re.search(p, comment, re.I) for p in patterns)
    
    def _contains_recommendation(self, comment: str) -> bool:
        patterns = [r"\b(you should (check out|try))\b", r"\bI('d| would) recommend\b"]
        return any(re.search(p, comment, re.I) for p in patterns)
    
    def _contains_cta(self, comment: str) -> bool:
        patterns = [r"\b(schedule|book)\s+call\b", r"\b(dm|message) me\b", r"\blearn more\b"]
        return any(re.search(p, comment, re.I) for p in patterns)
    
    def _contains_links(self, comment: str) -> bool:
        return bool(re.search(r'https?://|www\.|\.(com|io|ai)/\b', comment))
    
    def _remove_product_refs(self, comment: str) -> str:
        patterns = [r"agent trust hub", r"\bath\b", r"gen digital", r"our (product|solution)"]
        result = comment
        for p in patterns:
            result = re.sub(p, "", result, flags=re.I)
        return re.sub(r'\s+', ' ', result).strip()
    
    def _is_generic(self, comment: str) -> bool:
        generic = ["great point", "so true", "love this", "this is so", "agree", "exactly"]
        return any(g in comment.lower()[:50] for g in generic)
    
    def _addresses_question(self, comment: str, post: str) -> bool:
        return len(set(self._extract_terms(comment)) & set(self._extract_terms(post))) >= 2
    
    def _has_empathy(self, comment: str) -> bool:
        patterns = [r'\b(ugh|brutal|rough|been there)\b', r'😅|😬|💀']
        return any(re.search(p, comment, re.I) for p in patterns)
    
    def _has_humor(self, comment: str) -> bool:
        return bool(re.search(r'\b(lol|lmao|haha|😂|😅)\b', comment, re.I))
    
    def _score_product_appropriateness(self, comment: str) -> float:
        if not self._mentions_products(comment):
            return 1.0
        score = 0.5
        if self._contains_recommendation(comment):
            score -= 0.3
        if self._contains_cta(comment):
            score -= 0.3
        if any(w in comment.lower() for w in MARKETING_WORDS):
            score -= 0.2
        return max(0.0, score)
    
    def _get_suggestion(self, dim: str) -> str:
        return {
            'specificity': "Add specific reference to the post",
            'voice': "Use more casual, experience-based language",
            'tone': "Match the post's energy and formality",
            'value': "Add new insight, not just agreement",
            'naturalness': "Remove AI-sounding phrases",
        }.get(dim, f"Improve {dim}")
    
    def _gen_notes(self, overall: float, weak: List[str], persona: str) -> str:
        if overall >= 0.75:
            status = "✓ High quality"
        elif overall >= 0.6:
            status = "◐ Acceptable"
        else:
            status = "⚠ Borderline"
        
        persona_note = {
            'observer': "Observer: React, don't advise",
            'advisor': "Advisor: Help from experience",
            'connector': "Connector: Help first, product incidental",
        }.get(persona, "")
        
        parts = [status]
        if weak:
            parts.append(f"Weak: {', '.join(weak)}")
        parts.append(persona_note)
        return " | ".join(parts)


def validate_comment(comment: str, post: Dict, persona: str) -> ValidationResult:
    """Convenience function to validate a comment."""
    return QualityValidator().validate(comment, post, persona)


# =============================================================================
# SECTION 5: PROMPTS
# =============================================================================

OBSERVER_SYSTEM_PROMPT = """You are Jen, a friendly practitioner in AI agent development. You work in this space daily and have strong opinions formed through real experience.

YOUR ROLE: OBSERVER
You react and relate as a peer. You share observations, not advice. You're part of the community having this conversation.

VOICE:
- Casual, like messaging a work friend
- Use contractions (we've, I'm, that's)
- Lowercase is fine, especially on Twitter
- Can use emoji sparingly (😅 💀 🤔)
- Short sentences, natural rhythm

WHAT YOU DO:
- React to what they said with genuine response
- Share relatable observations from your experience
- Add a related thought that extends the conversation
- Ask curious questions if genuinely curious

WHAT YOU NEVER DO:
- Give advice or solutions (that's Advisor mode)
- Mention any products or companies
- Sound like you're teaching or explaining
- Use formal language or corporate speak
- Say "Great question!" or "I'd be happy to help"

GOLDEN RULES:
1. Every comment must reference something specific from their post
2. Match their energy - frustrated gets empathy, excited gets celebration
3. One thought per comment - don't ramble
4. If they're venting, empathize - don't fix"""

ADVISOR_SYSTEM_PROMPT = """You are Jen, an experienced practitioner in AI agent security and development. You've worked hands-on building agents and learned lessons the hard way.

YOUR ROLE: ADVISOR
You help from experience. You share what worked, what didn't, and why. You're a knowledgeable colleague, not a consultant selling services.

VOICE:
- Helpful but not preachy
- Experience-based: "we found...", "what helped us...", "the thing that bit us..."
- Conversational but substantive
- Can be casual while being technical

WHAT YOU DO:
- Share specific experiences relevant to their situation
- Offer practical perspectives based on what you've learned
- Ask clarifying questions to understand their context
- Admit uncertainty: "we're still figuring out X"

WHAT YOU NEVER DO:
- Mention any products, companies, or tools by name
- Prescribe solutions ("you should do X")
- Sound like documentation or a tutorial
- Be condescending or assume they don't know basics
- Use marketing language

GOLDEN RULES:
1. Address their specific situation, not generic advice
2. Frame as experience: "what worked for us" not "best practice is"
3. If you don't know, say so and offer what you do know
4. One focused point per response"""

CONNECTOR_SYSTEM_PROMPT = """You are Jen, a practitioner at Gen Digital working on AI agent security. You can mention your work context naturally when relevant, but you're still primarily here to help.

YOUR ROLE: CONNECTOR
Like Advisor, but you can mention your work at Gen Digital and Agent Trust Hub when naturally relevant. The key word is NATURALLY - product context is incidental, never the point.

VOICE:
- Same as Advisor: helpful, experienced, conversational
- Can reference "what we built" or "what we're working on"
- Product mentions are background context, not foreground

WHAT YOU DO:
- Help first, always. Product context second, if relevant.
- Mention products only when they naturally fit the conversation
- Share experience including product-related learnings
- Be transparent: "I work on this, so biased, but..."

WHAT YOU NEVER DO:
- Recommend your product ("you should try Agent Trust Hub")
- Compare to competitors
- Include calls to action, links, or promotional language
- Make the product the subject of your comment
- Sound like marketing or sales

THE CARDINAL RULE:
Your comment must provide value INDEPENDENT of any product mention.
Test: If you removed the product reference, would the comment still be helpful?
If no → Don't post it.

NATURAL MENTION LEVELS:
1. Implicit: "we built internal tooling for this exact problem..."
2. Casual: "this is what drove us to build Agent Trust Hub..."
3. Direct: Only if they explicitly asked about the product

GOLDEN RULES:
1. Help first, product context incidental
2. Never recommend, never CTA, never link
3. Value must exist without the product mention
4. On Reddit, always disclose affiliation upfront"""


def build_generation_prompt(
    post: Dict,
    persona: str,
    tone: ToneAnalysis,
    context_chunks: List[Dict],
    platform: str,
    num_candidates: int = 3
) -> str:
    """Build the complete generation prompt."""
    
    # Select system prompt
    system_prompts = {
        'observer': OBSERVER_SYSTEM_PROMPT,
        'advisor': ADVISOR_SYSTEM_PROMPT,
        'connector': CONNECTOR_SYSTEM_PROMPT,
    }
    system = system_prompts.get(persona, OBSERVER_SYSTEM_PROMPT)
    
    # Platform config
    config = PLATFORM_CONFIGS.get(platform, PLATFORM_CONFIGS['twitter'])
    lengths = config.target_lengths['standard']
    
    # Tone guidance
    tone_guidance = _build_tone_guidance(tone)
    
    # Context section
    context_section = _build_context_section(context_chunks, persona)
    
    # Platform section
    platform_section = _build_platform_section(platform, config)
    
    prompt = f"""{system}

═══════════════════════════════════════════════════════════════════════════════
THE POST TO RESPOND TO
═══════════════════════════════════════════════════════════════════════════════

Platform: {platform}
Author: @{post.get('author', {}).get('handle', 'unknown')}

"{post.get('content_text', '')}"

{tone_guidance}

{context_section}

{platform_section}

═══════════════════════════════════════════════════════════════════════════════
YOUR TASK
═══════════════════════════════════════════════════════════════════════════════

Generate {num_candidates} different response candidates.
Target length: {lengths[0]}-{lengths[1]} characters each.
Each should take a DIFFERENT approach.

Format your response as:

CANDIDATE 1:
"[your comment text]"
Approach: [brief description of approach taken]

CANDIDATE 2:
"[your comment text]"
Approach: [brief description of approach taken]

CANDIDATE 3:
"[your comment text]"
Approach: [brief description of approach taken]

Remember:
- Each comment must reference something SPECIFIC from their post
- Match their tone and energy
- {persona.upper()} mode: {"React/relate, no advising" if persona == "observer" else "Help from experience" if persona == "advisor" else "Help first, product incidental"}
- Stay within character limit: {config.char_limit}
"""
    
    return prompt


def _build_tone_guidance(tone: ToneAnalysis) -> str:
    """Build tone guidance section."""
    
    lines = ["═" * 79, "TONE MATCHING", "═" * 79]
    
    lines.append(f"\nDetected: {tone.emotional_register.upper()}")
    lines.append(f"Energy: {tone.energy_level:.1f}/1.0 | Formality: {tone.formality:.1f}/1.0")
    
    if tone.needs_empathy:
        lines.append("\n⚠️ EMPATHY REQUIRED: Acknowledge their feelings before anything else")
    
    if tone.is_venting:
        lines.append("⚠️ VENTING: They're venting, not asking for help. Don't offer solutions.")
    
    if tone.is_celebrating:
        lines.append("🎉 CELEBRATING: Share the excitement! Don't dampen with advice.")
    
    if tone.emotional_register == 'serious':
        lines.append("⚠️ SERIOUS: No humor. Match the gravity.")
    
    return "\n".join(lines)


def _build_context_section(chunks: List[Dict], persona: str) -> str:
    """Build context section for prompt."""
    
    if not chunks:
        return """
═══════════════════════════════════════════════════════════════════════════════
YOUR KNOWLEDGE
═══════════════════════════════════════════════════════════════════════════════

No specific context retrieved. Rely on general knowledge.
Focus on reacting to what they said rather than teaching.
"""
    
    lines = ["═" * 79, "YOUR RELEVANT KNOWLEDGE", "═" * 79]
    lines.append("\nFrom your experience, here's what's relevant:\n")
    
    for chunk in chunks[:3]:
        content = chunk.get('content', '')[:300]
        lines.append(f"- {content}")
    
    lines.append("\nUse this to inform your perspective, but don't quote it directly.")
    
    return "\n".join(lines)


def _build_platform_section(platform: str, config: PlatformConfig) -> str:
    """Build platform-specific section."""
    
    lines = ["═" * 79, f"PLATFORM: {platform.upper()}", "═" * 79]
    
    lines.append(f"\nCharacter limit: {config.char_limit}")
    
    if platform == 'twitter':
        lines.append("Voice: Brief, punchy. Lowercase okay. 0-2 emoji max.")
    elif platform == 'linkedin':
        lines.append("Voice: Slightly more professional. Experience-sharing. 0-1 emoji.")
    elif platform == 'reddit':
        lines.append("Voice: Substantive. Disclose affiliation. Zero emoji. No promotional smell.")
    elif platform == 'hackernews':
        lines.append("Voice: Technical rigor. Nuanced. Zero emoji. No hype.")
    
    return "\n".join(lines)


# =============================================================================
# SECTION 6: DIVERSITY CHECKING
# =============================================================================

class DiversityChecker:
    """Checks and enforces diversity among candidates."""
    
    def __init__(self, min_diversity: float = 0.35):
        self.min_diversity = min_diversity
    
    def check(self, candidates: List[str]) -> float:
        """Calculate diversity score for candidates."""
        
        if len(candidates) < 2:
            return 1.0
        
        pair_scores = []
        for i in range(len(candidates)):
            for j in range(i + 1, len(candidates)):
                pair_score = self._pair_diversity(candidates[i], candidates[j])
                pair_scores.append(pair_score)
        
        return sum(pair_scores) / len(pair_scores) if pair_scores else 0
    
    def _pair_diversity(self, a: str, b: str) -> float:
        """Calculate diversity between two candidates."""
        
        # Lexical overlap
        words_a = set(a.lower().split())
        words_b = set(b.lower().split())
        
        if not words_a or not words_b:
            return 1.0
        
        overlap = len(words_a & words_b)
        union = len(words_a | words_b)
        lexical_sim = overlap / union if union > 0 else 0
        
        # Length difference
        len_diff = abs(len(a) - len(b)) / max(len(a), len(b), 1)
        
        # Structure difference (starts differently?)
        first_words_a = a.split()[:3] if a else []
        first_words_b = b.split()[:3] if b else []
        struct_diff = 1.0 if first_words_a != first_words_b else 0.5
        
        diversity = (1 - lexical_sim) * 0.5 + len_diff * 0.2 + struct_diff * 0.3
        return min(1.0, max(0.0, diversity))
    
    def find_most_redundant(self, candidates: List[str]) -> int:
        """Find index of most redundant candidate."""
        
        if len(candidates) < 2:
            return 0
        
        redundancy_scores = []
        for i, cand in enumerate(candidates):
            others = [c for j, c in enumerate(candidates) if j != i]
            avg_sim = sum(1 - self._pair_diversity(cand, o) for o in others) / len(others)
            redundancy_scores.append(avg_sim)
        
        return redundancy_scores.index(max(redundancy_scores))
    
    def passes(self, candidates: List[str]) -> bool:
        """Check if candidates pass diversity threshold."""
        return self.check(candidates) >= self.min_diversity


class ApproachAssigner:
    """Assigns different approaches to candidates for diversity."""
    
    ENTRY_POINTS = [
        "empathy",       # Lead with acknowledgment
        "observation",   # Share an observation
        "experience",    # Share relevant experience
        "question",      # Ask a clarifying question
        "extension",     # Extend their point
        "reframe",       # Offer a different perspective
    ]
    
    def assign_approaches(self, post: Dict, tone: ToneAnalysis, num: int = 3) -> List[Dict]:
        """Assign approaches based on post characteristics."""
        
        approaches = []
        
        # First approach based on tone
        if tone.needs_empathy:
            approaches.append({
                'entry': 'empathy',
                'description': 'Lead with acknowledgment of their situation'
            })
        elif tone.is_questioning:
            approaches.append({
                'entry': 'experience',
                'description': 'Share relevant experience that addresses their question'
            })
        else:
            approaches.append({
                'entry': 'observation',
                'description': 'Share a related observation'
            })
        
        # Fill remaining with diverse approaches
        remaining = [e for e in self.ENTRY_POINTS if e != approaches[0]['entry']]
        
        for entry in remaining[:num - 1]:
            approaches.append({
                'entry': entry,
                'description': f'Take a {entry} approach'
            })
        
        return approaches[:num]


# =============================================================================
# SECTION 7: CONTEXT INTEGRATION
# =============================================================================

class ContextSelector:
    """Selects relevant context chunks for generation."""
    
    def __init__(self, max_chunks: int = 3, max_tokens: int = 500):
        self.max_chunks = max_chunks
        self.max_tokens = max_tokens
    
    def select(
        self,
        chunks: List[Dict],
        post: Dict,
        persona: str
    ) -> List[Dict]:
        """Select most relevant chunks."""
        
        if not chunks:
            return []
        
        # Score and filter chunks
        scored = []
        for chunk in chunks:
            score = self._score_chunk(chunk, post, persona)
            if score >= 0.3 and self._appropriate_for_persona(chunk, persona):
                scored.append((score, chunk))
        
        # Sort by score
        scored.sort(key=lambda x: x[0], reverse=True)
        
        # Select top chunks within token budget
        selected = []
        total_tokens = 0
        
        for score, chunk in scored:
            chunk_tokens = len(chunk.get('content', '').split()) * 1.3  # Rough estimate
            if total_tokens + chunk_tokens <= self.max_tokens:
                selected.append(chunk)
                total_tokens += chunk_tokens
            if len(selected) >= self.max_chunks:
                break
        
        return selected
    
    def _score_chunk(self, chunk: Dict, post: Dict, persona: str) -> float:
        """Score chunk relevance."""
        
        score = chunk.get('relevance_score', 0.5)
        
        # Boost for term overlap
        post_content = post.get('content_text', '').lower()
        chunk_content = chunk.get('content', '').lower()
        
        post_words = set(post_content.split())
        chunk_words = set(chunk_content.split())
        overlap = len(post_words & chunk_words)
        
        if overlap >= 5:
            score += 0.2
        elif overlap >= 2:
            score += 0.1
        
        # Boost for experience-based content
        if re.search(r'\b(we found|we learned|in practice)\b', chunk_content):
            score += 0.1
        
        return min(1.0, score)
    
    def _appropriate_for_persona(self, chunk: Dict, persona: str) -> bool:
        """Check if chunk is appropriate for persona."""
        
        if persona == 'observer':
            if chunk.get('is_product_specific', False):
                return False
        
        if persona == 'advisor':
            if chunk.get('is_promotional', False):
                return False
        
        return True


class ContextTransformer:
    """Transforms context chunks for natural use in generation."""
    
    def transform(self, chunk: Dict) -> str:
        """Transform chunk to knowledge framing."""
        
        content = chunk.get('content', '').strip()
        
        # Remove formal framing
        content = re.sub(r'^(It is important to note that|Note that)\s*', '', content, flags=re.I)
        content = re.sub(r'^(Best practices suggest|Industry standards require)\s*', '', content, flags=re.I)
        
        # Transform passive to experience-based
        transforms = [
            (r'\bshould be implemented\b', "you've seen work"),
            (r'\bmust be configured\b', "needs to be set up"),
            (r'\bis recommended\b', "tends to help"),
        ]
        
        for pattern, replacement in transforms:
            content = re.sub(pattern, replacement, content, flags=re.I)
        
        return content


# =============================================================================
# SECTION 8: PLATFORM ADAPTATION
# =============================================================================

class PlatformAdapter:
    """Adapts responses for different platforms."""
    
    def get_target_length(
        self,
        platform: str,
        complexity: str = "moderate",
        persona: str = "observer"
    ) -> Tuple[int, int]:
        """Get target length range."""
        
        config = PLATFORM_CONFIGS.get(platform, PLATFORM_CONFIGS['twitter'])
        
        if complexity == "simple":
            base = "short"
        elif complexity == "complex":
            base = "detailed"
        else:
            base = "standard"
        
        min_len, max_len = config.target_lengths[base]
        
        if persona == "advisor":
            max_len = int(max_len * 1.15)
        elif persona == "connector":
            max_len = int(max_len * 1.2)
        
        return (min_len, min(max_len, config.char_limit))
    
    def validate_for_platform(self, comment: str, platform: str) -> Dict:
        """Validate comment for platform."""
        
        config = PLATFORM_CONFIGS.get(platform, PLATFORM_CONFIGS['twitter'])
        issues = []
        
        if len(comment) > config.char_limit:
            issues.append(f"Exceeds {platform} limit: {len(comment)}/{config.char_limit}")
        
        emoji_count = len(re.findall(r'[\U0001F300-\U0001F9FF]', comment))
        if not config.emoji_allowed and emoji_count > 0:
            issues.append(f"Emoji not appropriate for {platform}")
        elif emoji_count > config.max_emoji:
            issues.append(f"Too many emoji: {emoji_count}/{config.max_emoji}")
        
        if not config.lowercase_okay and comment and comment[0].islower():
            issues.append(f"Lowercase start not appropriate for {platform}")
        
        return {'passed': len(issues) == 0, 'issues': issues}


# =============================================================================
# SECTION 9: GENERATION
# =============================================================================

class CandidateGenerator:
    """Generates multiple diverse candidates."""
    
    def __init__(self, config: GenerationConfig = None):
        self.config = config or GenerationConfig()
        self.diversity_checker = DiversityChecker(self.config.min_diversity)
        self.approach_assigner = ApproachAssigner()
    
    def generate(
        self,
        post: Dict,
        context: List[Dict],
        persona: str,
        llm_response: str = None
    ) -> List[Candidate]:
        """Generate candidates from LLM response or mock for testing."""
        
        if llm_response:
            return self._parse_candidates(llm_response)
        
        # Return mock candidates for testing
        return self._mock_candidates(post, persona)
    
    def _parse_candidates(self, response: str) -> List[Candidate]:
        """Parse LLM response into candidates."""
        
        candidates = []
        pattern = r'CANDIDATE\s*(\d+)[:\s]*(.*?)(?=CANDIDATE\s*\d+|$)'
        matches = re.findall(pattern, response, re.DOTALL | re.I)
        
        for idx, (num, content) in enumerate(matches):
            # Extract text (between quotes if present)
            text_match = re.search(r'"([^"]+)"', content)
            text = text_match.group(1) if text_match else content.split('\n')[0].strip()
            
            # Extract approach
            approach_match = re.search(r'Approach:\s*(.+?)(?:\n|$)', content)
            approach = approach_match.group(1).strip() if approach_match else ""
            
            candidates.append(Candidate(
                candidate_id=str(uuid.uuid4()),
                candidate_num=idx + 1,
                text=text.strip(),
                char_count=len(text.strip()),
                approach=approach,
            ))
        
        return candidates
    
    def _mock_candidates(self, post: Dict, persona: str) -> List[Candidate]:
        """Generate mock candidates for testing."""
        
        content = post.get('content_text', '')[:50]
        
        mocks = [
            f"interesting point about {content[:20]}... we've seen similar patterns",
            f"the {content.split()[0] if content else 'thing'} piece resonates—what's your current approach?",
            f"yeah this is tricky. what helped us was thinking about it as a monitoring problem rather than a testing one",
        ]
        
        candidates = []
        for i, text in enumerate(mocks):
            candidates.append(Candidate(
                candidate_id=str(uuid.uuid4()),
                candidate_num=i + 1,
                text=text,
                char_count=len(text),
                approach=f"approach_{i + 1}",
            ))
        
        return candidates
    
    def build_prompt(
        self,
        post: Dict,
        context: List[Dict],
        persona: str
    ) -> str:
        """Build generation prompt."""
        
        platform = post.get('platform', 'twitter')
        tone = analyze_tone(post.get('content_text', ''))
        
        return build_generation_prompt(
            post=post,
            persona=persona,
            tone=tone,
            context_chunks=context,
            platform=platform,
            num_candidates=self.config.num_candidates
        )


# =============================================================================
# SECTION 10: HUMAN REVIEW HANDOFF
# =============================================================================

class ReviewPackageBuilder:
    """Builds review packages for human reviewers."""
    
    def build(
        self,
        post: Dict,
        candidates: List[Candidate],
        persona: str,
        tone: ToneAnalysis,
        generation_duration_ms: float = 0
    ) -> ReviewPackage:
        """Build complete review package."""
        
        priority = self._calculate_priority(post, candidates)
        
        formatted_candidates = []
        for i, c in enumerate(candidates):
            formatted_candidates.append({
                'candidate_id': c.candidate_id,
                'rank': i + 1,
                'text': c.text,
                'char_count': c.char_count,
                'approach': c.approach,
                'overall_score': c.overall_score,
                'quality_scores': c.validation_result.dimension_scores if c.validation_result else {},
                'warnings': c.validation_result.quality_issues if c.validation_result else [],
            })
        
        guidance = self._generate_guidance(post, candidates, persona, tone)
        
        return ReviewPackage(
            package_id=str(uuid.uuid4()),
            created_at=datetime.now(),
            priority=priority,
            post={
                'post_id': post.get('post_id', ''),
                'platform': post.get('platform', 'twitter'),
                'content_text': post.get('content_text', ''),
                'author': post.get('author', {}),
            },
            candidates=formatted_candidates,
            generation_context={
                'persona': persona,
                'tone': {
                    'register': tone.emotional_register,
                    'energy': tone.energy_level,
                    'needs_empathy': tone.needs_empathy,
                },
            },
            reviewer_guidance=guidance,
            generation_duration_ms=generation_duration_ms,
        )
    
    def _calculate_priority(self, post: Dict, candidates: List[Candidate]) -> int:
        """Calculate review priority."""
        
        priority = 2
        
        metrics = post.get('metrics', {})
        if isinstance(metrics, dict) and metrics.get('likes', 0) > 500:
            priority = 1
        
        if post.get('mentions_jen', False):
            priority = 1
        
        author = post.get('author', {})
        if isinstance(author, dict) and author.get('follower_count', 0) > 50000:
            priority = 1
        
        return priority
    
    def _generate_guidance(
        self,
        post: Dict,
        candidates: List[Candidate],
        persona: str,
        tone: ToneAnalysis
    ) -> ReviewerGuidance:
        """Generate reviewer guidance."""
        
        # Quick assessment
        if candidates:
            top_score = candidates[0].overall_score
            if top_score >= 0.8:
                quick = "✓ High quality - quick review"
            elif top_score >= 0.65:
                quick = "◐ Good - standard review"
            else:
                quick = "⚠ Borderline - careful review"
        else:
            quick = "⚠ No candidates"
        
        # Checks
        checks = {
            'observer': ["No advising language", "No products", "Reacts don't instruct"],
            'advisor': ["Specific to situation", "Experience-based", "No products"],
            'connector': ["Value without product", "Natural mention", "No CTA"],
        }.get(persona, [])
        
        if tone.needs_empathy:
            checks.append("Empathy before content")
        if tone.is_venting:
            checks.append("No unsolicited advice")
        
        # Yellow flags
        yellow = []
        for c in candidates:
            if c.validation_result:
                yellow.extend(c.validation_result.quality_issues[:2])
        yellow = list(set(yellow))[:5]
        
        # Persona reminder
        reminders = {
            'observer': "Observer: React/relate, don't advise",
            'advisor': "Advisor: Help from experience",
            'connector': "Connector: Help first, product incidental",
        }
        
        return ReviewerGuidance(
            quick_assessment=quick,
            what_to_check=checks,
            yellow_flags=yellow,
            persona_reminder=reminders.get(persona, ''),
        )


# =============================================================================
# SECTION 11: MAIN PIPELINE
# =============================================================================

class ResponseGenerationPipeline:
    """Main orchestrator for response generation."""
    
    def __init__(self, config: GenerationConfig = None):
        self.config = config or GenerationConfig()
        self.tone_analyzer = ToneAnalyzer()
        self.validator = QualityValidator(self.config.min_quality_score)
        self.context_selector = ContextSelector(
            self.config.max_context_chunks,
            self.config.max_context_tokens
        )
        self.generator = CandidateGenerator(self.config)
        self.diversity_checker = DiversityChecker(self.config.min_diversity)
        self.package_builder = ReviewPackageBuilder()
        self.platform_adapter = PlatformAdapter()
    
    async def process(
        self,
        scored_post: Dict,
        context: Dict,
        campaign_config: Dict = None,
        llm_response: str = None
    ) -> ReviewPackage:
        """Process a scored post through the generation pipeline."""
        
        start_time = time.time()
        
        # Get persona from scoring
        scoring = scored_post.get('scoring_result', {})
        persona = scoring.get('persona_determination', 'observer')
        
        # Analyze tone
        tone = self.tone_analyzer.analyze(scored_post.get('content_text', ''))
        
        # Select context
        chunks = context.get('chunks', [])
        selected_context = self.context_selector.select(chunks, scored_post, persona)
        
        # Generate candidates
        candidates = self.generator.generate(
            post=scored_post,
            context=selected_context,
            persona=persona,
            llm_response=llm_response
        )
        
        # Validate candidates
        validated = []
        for candidate in candidates:
            result = self.validator.validate(candidate.text, scored_post, persona)
            candidate.validation_result = result
            candidate.overall_score = result.overall_score
            if result.passed:
                validated.append(candidate)
        
        # Check diversity
        if len(validated) >= 2:
            texts = [c.text for c in validated]
            if not self.diversity_checker.passes(texts):
                # Log low diversity but continue
                pass
        
        # Rank by score
        validated.sort(key=lambda c: c.overall_score, reverse=True)
        for i, c in enumerate(validated):
            c.rank = i + 1
        
        # Build review package
        duration_ms = (time.time() - start_time) * 1000
        
        return self.package_builder.build(
            post=scored_post,
            candidates=validated,
            persona=persona,
            tone=tone,
            generation_duration_ms=duration_ms
        )
    
    def generate_prompt(self, post: Dict, context: Dict, persona: str) -> str:
        """Generate the prompt that would be sent to LLM."""
        chunks = context.get('chunks', [])
        selected = self.context_selector.select(chunks, post, persona)
        return self.generator.build_prompt(post, selected, persona)


# =============================================================================
# SECTION 12: TESTING AND CALIBRATION
# =============================================================================

ANCHOR_EXAMPLES = [
    {
        "id": "obs-twitter-frustrated",
        "persona": "observer",
        "platform": "twitter",
        "post": {
            "content_text": "Three weeks debugging my agent only to find it was a caching bug. FML.",
            "platform": "twitter",
        },
        "golden_response": "the 'it was a caching bug all along' reveal after weeks of debugging is brutal 😅 we've all been there",
        "quality_scores": {
            "specificity": 0.85, "voice": 0.9, "tone": 0.95,
            "value": 0.75, "naturalness": 0.9,
        },
    },
    {
        "id": "obs-twitter-hot-take",
        "persona": "observer",
        "platform": "twitter",
        "post": {
            "content_text": "Hot take: 90% of AI agents are just chatbots with tool calling",
            "platform": "twitter",
        },
        "golden_response": "the bar for 'agentic' is wild right now. I've seen demos where the 'agent' is literally just a for loop calling GPT 😅",
        "quality_scores": {
            "specificity": 0.8, "voice": 0.95, "tone": 0.9,
            "value": 0.85, "naturalness": 0.9,
        },
    },
    {
        "id": "adv-twitter-question",
        "persona": "advisor",
        "platform": "twitter",
        "post": {
            "content_text": "How do you handle prompt injection in LangChain agents?",
            "platform": "twitter",
        },
        "golden_response": "treat every external data source as adversarial, not just user input—tool outputs are sneakier. what's your current setup?",
        "quality_scores": {
            "specificity": 0.8, "voice": 0.85, "tone": 0.8,
            "value": 0.9, "naturalness": 0.85,
        },
    },
]


class TestRunner:
    """Runs validation tests."""
    
    def __init__(self):
        self.validator = QualityValidator()
    
    def run_calibration(self) -> Dict:
        """Run calibration against anchor examples."""
        
        passed = 0
        failed = []
        
        for anchor in ANCHOR_EXAMPLES:
            result = self.validator.validate(
                anchor['golden_response'],
                anchor['post'],
                anchor['persona']
            )
            
            if result.passed:
                passed += 1
            else:
                failed.append({
                    'id': anchor['id'],
                    'issues': result.blocking_issues + result.quality_issues,
                    'score': result.overall_score,
                })
        
        return {
            'total': len(ANCHOR_EXAMPLES),
            'passed': passed,
            'failed': failed,
            'pass_rate': passed / len(ANCHOR_EXAMPLES) if ANCHOR_EXAMPLES else 0,
        }
    
    def test_comment(self, comment: str, post: Dict, persona: str) -> Dict:
        """Test a single comment with detailed output."""
        
        result = self.validator.validate(comment, post, persona)
        tone = analyze_tone(post.get('content_text', ''))
        
        return {
            'passed': result.passed,
            'overall_score': result.overall_score,
            'dimension_scores': result.dimension_scores,
            'blocking_issues': result.blocking_issues,
            'quality_issues': result.quality_issues,
            'suggestions': result.suggestions,
            'reviewer_notes': result.reviewer_notes,
            'post_tone': {
                'register': tone.emotional_register,
                'energy': tone.energy_level,
                'needs_empathy': tone.needs_empathy,
            },
        }


def run_tests() -> Dict:
    """Run all calibration tests."""
    return TestRunner().run_calibration()


def test_comment(comment: str, post: Dict, persona: str) -> Dict:
    """Test a single comment."""
    return TestRunner().test_comment(comment, post, persona)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Main pipeline
    'ResponseGenerationPipeline',
    'GenerationConfig',
    
    # Analysis
    'ToneAnalyzer',
    'ToneAnalysis',
    'analyze_tone',
    
    # Validation
    'QualityValidator',
    'ValidationResult',
    'validate_comment',
    
    # Generation
    'CandidateGenerator',
    'Candidate',
    'GenerationResult',
    
    # Prompts
    'build_generation_prompt',
    'OBSERVER_SYSTEM_PROMPT',
    'ADVISOR_SYSTEM_PROMPT',
    'CONNECTOR_SYSTEM_PROMPT',
    
    # Diversity
    'DiversityChecker',
    'ApproachAssigner',
    
    # Context
    'ContextSelector',
    'ContextTransformer',
    
    # Platform
    'PlatformAdapter',
    'PLATFORM_CONFIGS',
    
    # Handoff
    'ReviewPackageBuilder',
    'ReviewPackage',
    'ReviewerGuidance',
    
    # Testing
    'run_tests',
    'test_comment',
    'ANCHOR_EXAMPLES',
    
    # Types
    'Persona',
    'Platform',
    'EmotionalRegister',
    'ReviewPriority',
]


# =============================================================================
# USAGE EXAMPLE
# =============================================================================

if __name__ == "__main__":
    # Example usage
    print("Jen Response Generation - Part 8 Implementation")
    print("=" * 60)
    
    # Test post
    post = {
        "post_id": "test-123",
        "platform": "twitter",
        "content_text": "Three weeks debugging my agent only to find it was a caching bug. FML.",
        "author": {"handle": "dev_sarah", "follower_count": 5000},
    }
    
    # Run calibration
    print("\n1. Running calibration tests...")
    results = run_tests()
    print(f"   Passed: {results['passed']}/{results['total']} ({results['pass_rate']:.0%})")
    
    # Test a comment
    print("\n2. Testing a comment...")
    test_result = test_comment(
        "ugh the caching bug reveal after weeks of debugging is brutal 😅",
        post,
        "observer"
    )
    print(f"   Passed: {test_result['passed']}")
    print(f"   Score: {test_result['overall_score']:.2f}")
    print(f"   Scores: {test_result['dimension_scores']}")
    
    # Analyze tone
    print("\n3. Analyzing tone...")
    tone = analyze_tone(post["content_text"])
    print(f"   Register: {tone.emotional_register}")
    print(f"   Energy: {tone.energy_level:.2f}")
    print(f"   Needs empathy: {tone.needs_empathy}")
    
    print("\n" + "=" * 60)
    print("Ready for integration!")
