# kinda/personality.py

"""
Kinda-Lang Personality and Chaos Control System

Provides configurable chaos levels through personality profiles that affect
fuzzy construct behavior, randomness, and error message tone.

Advanced Performance Optimization (Epic #125 Task 3):
- Pre-computed probability caches
- Optimized random number generation
- Memory-efficient state management
"""

import random
import time
import weakref
from dataclasses import dataclass, field
from typing import Dict, Optional, Any, Tuple, List
from collections import deque, defaultdict
from enum import Enum


class ErrorHandlingMode(Enum):
    """Error handling modes for fuzzy construct failures (Issue #112)."""

    STRICT = "strict"  # Fail immediately on errors
    WARNING = "warning"  # Log errors and continue
    SILENT = "silent"  # Silently handle errors


@dataclass
class ErrorRecord:
    """Record of a fuzzy construct error."""

    construct_type: str  # Type of construct that errored
    error_message: str  # Error message
    context: str  # Additional context (e.g., input values)
    timestamp: float = field(default_factory=time.time)
    recovered: bool = True  # Whether error was recovered from


class ErrorTracker:
    """Centralized error collection for fuzzy constructs (Issue #112)."""

    def __init__(self, mode: ErrorHandlingMode = ErrorHandlingMode.WARNING) -> None:
        self.mode = mode
        self.errors: List[ErrorRecord] = []
        self.error_count_by_construct: Dict[str, int] = defaultdict(int)

    def record_error(
        self,
        construct_type: str,
        error_message: str,
        context: str = "",
        recovered: bool = True,
    ) -> None:
        """Record an error from a fuzzy construct."""
        error = ErrorRecord(
            construct_type=construct_type,
            error_message=error_message,
            context=context,
            recovered=recovered,
        )
        self.errors.append(error)
        self.error_count_by_construct[construct_type] += 1

        # Handle based on mode
        if self.mode == ErrorHandlingMode.STRICT and not recovered:
            raise RuntimeError(
                f"[STRICT MODE] {construct_type} error: {error_message} (context: {context})"
            )
        elif self.mode == ErrorHandlingMode.WARNING:
            print(f"[!] {construct_type} error: {error_message}")
            if context:
                print(f"    Context: {context}")

    def get_error_rate(self) -> float:
        """Calculate overall error handling rate (errors caught / errors that could occur)."""
        if not self.errors:
            return 1.0  # No errors = 100% success
        recovered_count = sum(1 for e in self.errors if e.recovered)
        return recovered_count / len(self.errors)

    def get_construct_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get error statistics by construct type."""
        stats = {}
        for construct_type in self.error_count_by_construct:
            construct_errors = [e for e in self.errors if e.construct_type == construct_type]
            recovered = sum(1 for e in construct_errors if e.recovered)
            stats[construct_type] = {
                "total_errors": len(construct_errors),
                "recovered": recovered,
                "failed": len(construct_errors) - recovered,
                "recovery_rate": recovered / len(construct_errors) if construct_errors else 1.0,
            }
        return stats

    def clear(self) -> None:
        """Clear all recorded errors."""
        self.errors.clear()
        self.error_count_by_construct.clear()

    def summary(self) -> str:
        """Get a summary of error tracking."""
        if not self.errors:
            return "No errors recorded"

        total = len(self.errors)
        recovered = sum(1 for e in self.errors if e.recovered)
        rate = self.get_error_rate()

        lines = [
            f"Error Handling Summary:",
            f"  Mode: {self.mode.value}",
            f"  Total errors: {total}",
            f"  Recovered: {recovered}",
            f"  Failed: {total - recovered}",
            f"  Recovery rate: {rate:.1%}",
        ]

        if self.error_count_by_construct:
            lines.append("  By construct:")
            for construct, count in sorted(
                self.error_count_by_construct.items(), key=lambda x: x[1], reverse=True
            ):
                lines.append(f"    - {construct}: {count} errors")

        return "\n".join(lines)


@dataclass
class ChaosProfile:
    """Configuration for chaos levels in fuzzy constructs."""

    # Probability modifiers for conditional constructs
    sometimes_base: float = 0.5  # Base probability for ~sometimes
    maybe_base: float = 0.6  # Base probability for ~maybe
    probably_base: float = 0.7  # Base probability for ~probably
    rarely_base: float = 0.15  # Base probability for ~rarely
    sorta_print_base: float = 0.8  # Base probability for ~sorta print

    # Loop construct continuation probabilities
    sometimes_while_base: float = 0.6  # Base probability for ~sometimes_while continuation
    maybe_for_base: float = 0.7  # Base probability for ~maybe_for item execution

    # Repetition construct variance settings
    kinda_repeat_variance: float = 0.1  # Standard deviation as fraction of n for ~kinda_repeat

    # Eventually until confidence thresholds
    eventually_until_confidence: float = 0.8  # Confidence threshold for termination

    # Variance modifiers for numeric constructs
    int_fuzz_range: Tuple[int, int] = (-1, 1)  # Range for kinda int fuzz
    float_drift_range: Tuple[float, float] = (-0.5, 0.5)  # Range for kinda float drift
    ish_variance: float = 2.0  # Variance for ~ish values
    ish_tolerance: float = 2.0  # Tolerance for ~ish comparisons

    # Boolean construct uncertainty
    bool_uncertainty: float = 0.1  # Probability of flipping boolean result

    # Binary construct probabilities
    binary_pos_prob: float = 0.4  # Probability of positive result
    binary_neg_prob: float = 0.4  # Probability of negative result
    binary_neutral_prob: float = 0.2  # Probability of neutral result

    # Chaos amplification factors
    chaos_amplifier: float = 1.0  # Multiplier for all randomness
    drift_rate: float = 0.0  # How quickly variables drift over time
    cascade_strength: float = 0.0  # How much operations affect each other

    # Error message personality
    error_snark_level: float = 0.5  # How snarky error messages are (0-1)


class ProbabilityCache:
    """
    Optimized probability cache for Epic #125 Task 3 performance requirements.
    Pre-computes and caches personality-specific probabilities to avoid
    repeated calculations in performance-critical scenarios.
    """

    def __init__(self, personality_context: Any) -> None:
        self.context = weakref.ref(personality_context)  # Avoid circular references
        self._cache: Dict[str, float] = {}
        self._cache_generation = 0
        self._build_cache()

    def _build_cache(self) -> None:
        """Pre-compute all commonly used probabilities."""
        ctx = self.context()
        if not ctx:
            return

        # Cache all construct probabilities with chaos adjustments
        constructs = [
            "sometimes",
            "maybe",
            "probably",
            "rarely",
            "sorta_print",
            "sometimes_while",
            "maybe_for",
        ]

        for construct in constructs:
            self._cache[construct] = ctx.get_chaos_probability(construct)

        # Cache chaos-adjusted ranges and variances
        self._cache["int_fuzz_range"] = ctx.get_fuzz_range("int")
        self._cache["float_drift_range"] = ctx.get_float_drift_range()
        self._cache["ish_variance"] = ctx.get_ish_variance()
        self._cache["ish_tolerance"] = ctx.get_ish_tolerance()
        self._cache["bool_uncertainty"] = ctx.get_bool_uncertainty()
        self._cache["binary_probs"] = ctx.get_binary_probabilities()

        # Cache repetition construct parameters
        self._cache["kinda_repeat_variance"] = (
            ctx.profile.kinda_repeat_variance * ctx.profile.chaos_amplifier * ctx.chaos_multiplier
        )
        self._cache["eventually_until_confidence"] = self._get_eventually_until_confidence(ctx)

    def _get_eventually_until_confidence(self, ctx: Any) -> float:
        """Calculate cached eventually_until confidence threshold."""
        base_confidence = float(ctx.profile.eventually_until_confidence)
        combined_amplifier = float(ctx.profile.chaos_amplifier * ctx.chaos_multiplier)
        if combined_amplifier > 1.0:
            factor = min(0.3, (combined_amplifier - 1.0) * 0.2)
            adjusted = base_confidence - factor
        else:
            factor = (1.0 - combined_amplifier) * 0.1
            adjusted = base_confidence + factor
        return float(max(0.5, min(0.99, adjusted)))

    def get_cached_probability(self, construct_name: str) -> Optional[float]:
        """Get cached probability or None if not cached."""
        return self._cache.get(construct_name)

    def get_cached_value(self, key: str) -> Optional[Any]:
        """Get any cached value by key."""
        return self._cache.get(key)

    def invalidate(self) -> None:
        """Invalidate cache when personality changes."""
        self._cache.clear()
        self._cache_generation += 1
        self._build_cache()


class MemoryOptimizedEventuallyUntil:
    """
    Memory-optimized eventually_until evaluator with circular buffer.
    Implements bounded memory usage for long-running loops per Epic #125 Task 3 requirements.
    """

    def __init__(self, confidence_threshold: float, max_history: int = 100):
        self.confidence_threshold = confidence_threshold
        self.evaluations: deque[bool] = deque(maxlen=max_history)  # Circular buffer
        self.min_samples = 3

    def add_evaluation(self, result: bool) -> bool:
        """
        Add evaluation and return whether loop should continue.
        Returns True to continue, False to terminate.
        """
        self.evaluations.append(bool(result))
        n = len(self.evaluations)

        if n < self.min_samples:
            return True  # Continue until we have enough data

        # Count recent consecutive successes
        consecutive_successes = 0
        for i in range(len(self.evaluations) - 1, -1, -1):
            if self.evaluations[i]:
                consecutive_successes += 1
            else:
                break

        # Check recent success rate (last 5-10 evaluations)
        recent_window = min(5, n)
        recent_evaluations = list(self.evaluations)[-recent_window:]
        recent_successes = sum(recent_evaluations)
        recent_success_rate = recent_successes / recent_window if recent_window > 0 else 0

        # Terminate if we have 2+ consecutive successes OR high recent success rate
        should_terminate = (consecutive_successes >= 2) or (recent_success_rate >= 0.8)
        return not should_terminate  # Continue while not terminated

    def get_stats(self) -> Dict[str, Any]:
        """Get evaluator statistics for debugging."""
        if not self.evaluations:
            return {"total": 0, "success_rate": 0.0}

        total = len(self.evaluations)
        successes = sum(self.evaluations)
        return {
            "total": total,
            "successes": successes,
            "success_rate": successes / total,
            "recent_5": list(self.evaluations)[-5:] if total >= 5 else list(self.evaluations),
        }


class OptimizedRandomState:
    """
    Fast random number generator optimized for personality-based chaos.
    Pre-generates random numbers in batches for improved performance.
    """

    def __init__(self, seed: Optional[int] = None, batch_size: int = 1000):
        self.rng = random.Random(seed)
        self.batch_size = batch_size
        self._float_batch: List[float] = []
        self._int_ranges: Dict[Tuple[int, int], List[int]] = defaultdict(list)

    def _refill_float_batch(self) -> None:
        """Pre-generate a batch of random floats."""
        self._float_batch = [self.rng.random() for _ in range(self.batch_size)]

    def _refill_int_batch(self, a: int, b: int) -> None:
        """Pre-generate a batch of random integers for a given range."""
        key = (a, b)
        self._int_ranges[key] = [self.rng.randint(a, b) for _ in range(self.batch_size)]

    def random(self) -> float:
        """Get next random float from batch."""
        if not self._float_batch:
            self._refill_float_batch()
        return self._float_batch.pop()

    def randint(self, a: int, b: int) -> int:
        """Get next random integer from batch."""
        key = (a, b)
        if not self._int_ranges[key]:
            self._refill_int_batch(a, b)
        return self._int_ranges[key].pop()

    def uniform(self, a: float, b: float) -> float:
        """Generate uniform random float."""
        return a + (b - a) * self.random()

    def choice(self, seq: Any) -> Any:
        """Choose random element from sequence."""
        if not seq:
            raise IndexError("Cannot choose from empty sequence")
        return seq[self.randint(0, len(seq) - 1)]

    def gauss(self, mu: float, sigma: float) -> float:
        """Generate Gaussian random number."""
        return self.rng.gauss(mu, sigma)

    def getstate(self) -> Tuple[Any, ...]:
        """Get RNG state."""
        return self.rng.getstate()

    def setstate(self, state: Any) -> None:
        """Set RNG state."""
        self.rng.setstate(state)


# Global eventually_until evaluator registry for memory optimization
_eventually_until_evaluators: Dict[str, MemoryOptimizedEventuallyUntil] = {}


def get_eventually_until_evaluator(context_id: str = "default") -> MemoryOptimizedEventuallyUntil:
    """Get or create a memory-optimized eventually_until evaluator."""
    from kinda.personality import get_personality

    if context_id not in _eventually_until_evaluators:
        confidence = get_personality().profile.eventually_until_confidence
        _eventually_until_evaluators[context_id] = MemoryOptimizedEventuallyUntil(confidence)

    return _eventually_until_evaluators[context_id]


def clear_eventually_until_evaluators() -> None:
    """Clear all evaluators (useful for testing)."""
    _eventually_until_evaluators.clear()


# Pre-defined personality profiles based on user feedback requirements
PERSONALITY_PROFILES: Dict[str, ChaosProfile] = {
    "professional": ChaosProfile(
        sometimes_base=0.85,  # Professional but still fuzzy
        maybe_base=0.8,  # High reliability
        probably_base=0.9,  # Very reliable
        rarely_base=0.1,  # Professional rarely
        sorta_print_base=0.9,  # Almost always print
        sometimes_while_base=0.8,  # 80% continuation probability
        maybe_for_base=0.85,  # 85% execution probability per item
        kinda_repeat_variance=0.15,  # ±15% variance
        eventually_until_confidence=0.85,  # 85% confidence threshold
        int_fuzz_range=(-1, 1),  # Minimal fuzz
        float_drift_range=(-0.1, 0.1),  # Minimal float drift
        ish_variance=1.0,  # Low variance
        ish_tolerance=1.5,  # Tight tolerance
        bool_uncertainty=0.05,  # Very low boolean uncertainty
        binary_pos_prob=0.6,  # Professional positive
        binary_neg_prob=0.2,  # Less negative
        binary_neutral_prob=0.2,  # Standard neutral
        chaos_amplifier=0.5,  # Low chaos
        drift_rate=0.01,  # Minimal drift
        cascade_strength=0.05,  # Minimal cascade
        error_snark_level=0.2,  # Professional error messages
    ),
    "friendly": ChaosProfile(
        sometimes_base=0.75,  # Friendly reliability
        maybe_base=0.7,  # Moderate reliability
        probably_base=0.8,  # Good reliability
        rarely_base=0.2,  # Friendly rarely
        sorta_print_base=0.85,  # Usually prints
        sometimes_while_base=0.7,  # 70% continuation probability
        maybe_for_base=0.8,  # 80% execution probability per item
        kinda_repeat_variance=0.25,  # ±25% variance
        eventually_until_confidence=0.75,  # 75% confidence threshold
        int_fuzz_range=(-1, 1),  # Standard fuzz
        float_drift_range=(-0.3, 0.3),  # Moderate float drift
        ish_variance=1.5,  # Moderate variance
        ish_tolerance=2.0,  # Standard tolerance
        bool_uncertainty=0.08,  # Low boolean uncertainty
        binary_pos_prob=0.5,  # Balanced positive
        binary_neg_prob=0.3,  # Less negative
        binary_neutral_prob=0.2,  # Standard neutral
        chaos_amplifier=0.8,  # Moderate chaos
        drift_rate=0.03,  # Slow drift
        cascade_strength=0.15,  # Some cascade
        error_snark_level=0.4,  # Friendly error messages
    ),
    "snarky": ChaosProfile(
        sometimes_base=0.6,  # Snarky unpredictability
        maybe_base=0.65,  # Moderate reliability
        probably_base=0.75,  # Still reliable but snarky
        rarely_base=0.1,  # Snarky rarely
        sorta_print_base=0.7,  # Sometimes skips printing
        sometimes_while_base=0.65,  # 65% continuation probability
        maybe_for_base=0.7,  # 70% execution probability per item
        kinda_repeat_variance=0.35,  # ±35% variance
        eventually_until_confidence=0.75,  # 75% confidence threshold
        int_fuzz_range=(-2, 2),  # More fuzz
        float_drift_range=(-0.8, 0.8),  # Higher float drift
        ish_variance=3.0,  # Higher variance
        ish_tolerance=3.0,  # Looser tolerance
        bool_uncertainty=0.15,  # Moderate boolean uncertainty
        binary_pos_prob=0.3,  # Less positive (snarky)
        binary_neg_prob=0.5,  # More negative (snarky)
        binary_neutral_prob=0.2,  # Standard neutral
        chaos_amplifier=1.2,  # Higher chaos
        drift_rate=0.07,  # Moderate drift
        cascade_strength=0.3,  # Moderate cascade
        error_snark_level=0.7,  # Snarky error messages
    ),
    "reliable": ChaosProfile(
        sometimes_base=0.95,  # Almost always execute
        maybe_base=0.95,  # Almost always execute
        probably_base=0.95,  # Almost always execute
        rarely_base=0.85,  # Reliable even when "rarely"
        sorta_print_base=0.95,  # Almost always print
        sometimes_while_base=0.90,  # 90% continuation probability per task spec
        maybe_for_base=0.95,  # 95% execution probability per item per task spec
        kinda_repeat_variance=0.10,  # ±10% variance per task spec
        eventually_until_confidence=0.95,  # 95% confidence threshold per task spec
        int_fuzz_range=(0, 0),  # No fuzz on integers
        float_drift_range=(0.0, 0.0),  # No drift on floats
        ish_variance=0.5,  # Minimal variance
        ish_tolerance=1.0,  # Tight tolerance
        bool_uncertainty=0.02,  # Very low boolean uncertainty
        binary_pos_prob=0.8,  # Highly positive
        binary_neg_prob=0.1,  # Rarely negative
        binary_neutral_prob=0.1,  # Rarely neutral
        chaos_amplifier=0.2,  # Very low chaos
        drift_rate=0.0,  # No drift
        cascade_strength=0.0,  # No cascade effects
        error_snark_level=0.1,  # Professional error messages
    ),
    "cautious": ChaosProfile(
        sometimes_base=0.7,  # Conservative execution
        maybe_base=0.75,  # Slightly more likely
        probably_base=0.8,  # Conservative but reliable
        rarely_base=0.25,  # Still cautious about rare events
        sorta_print_base=0.85,  # Usually prints
        sometimes_while_base=0.75,  # 75% continuation probability per task spec
        maybe_for_base=0.85,  # 85% execution probability per item per task spec
        kinda_repeat_variance=0.20,  # ±20% variance per task spec
        eventually_until_confidence=0.90,  # 90% confidence threshold per task spec
        int_fuzz_range=(-1, 1),  # Standard fuzz
        float_drift_range=(-0.2, 0.2),  # Minimal float drift
        ish_variance=1.5,  # Reduced variance
        ish_tolerance=1.5,  # Moderately tight tolerance
        bool_uncertainty=0.05,  # Low boolean uncertainty
        binary_pos_prob=0.5,  # Balanced positive
        binary_neg_prob=0.3,  # Less negative
        binary_neutral_prob=0.2,  # Standard neutral
        chaos_amplifier=0.6,  # Mild chaos
        drift_rate=0.01,  # Very slow drift
        cascade_strength=0.1,  # Minimal cascade
        error_snark_level=0.3,  # Gentle snark
    ),
    "playful": ChaosProfile(
        sometimes_base=0.5,  # Standard randomness
        maybe_base=0.6,  # Standard maybe
        probably_base=0.7,  # Standard probably (default)
        rarely_base=0.15,  # Standard rarely (default)
        sorta_print_base=0.8,  # Standard print rate
        sometimes_while_base=0.60,  # 60% continuation probability per task spec
        maybe_for_base=0.70,  # 70% execution probability per item per task spec
        kinda_repeat_variance=0.30,  # ±30% variance per task spec
        eventually_until_confidence=0.80,  # 80% confidence threshold per task spec
        int_fuzz_range=(-2, 2),  # More fuzz
        float_drift_range=(-0.5, 0.5),  # Standard float drift (default)
        ish_variance=2.5,  # Standard variance
        ish_tolerance=2.0,  # Standard tolerance
        bool_uncertainty=0.1,  # Standard boolean uncertainty (default)
        binary_pos_prob=0.4,  # Standard positive (default)
        binary_neg_prob=0.4,  # Standard negative (default)
        binary_neutral_prob=0.2,  # Standard neutral (default)
        chaos_amplifier=1.0,  # Normal chaos (default)
        drift_rate=0.05,  # Moderate drift
        cascade_strength=0.2,  # Some cascade effects
        error_snark_level=0.6,  # Moderate snark
    ),
    "chaotic": ChaosProfile(
        sometimes_base=0.3,  # More unpredictable
        maybe_base=0.4,  # Less reliable
        probably_base=0.5,  # Chaotic probably (reduced reliability)
        rarely_base=0.05,  # Almost never in chaotic mode
        sorta_print_base=0.6,  # Often skips printing
        sometimes_while_base=0.40,  # 40% continuation probability per task spec
        maybe_for_base=0.50,  # 50% execution probability per item per task spec
        kinda_repeat_variance=0.40,  # ±40% variance per task spec
        eventually_until_confidence=0.70,  # 70% confidence threshold per task spec
        int_fuzz_range=(-5, 5),  # High fuzz
        float_drift_range=(-2.0, 2.0),  # High float drift
        ish_variance=5.0,  # High variance
        ish_tolerance=4.0,  # Loose tolerance
        bool_uncertainty=0.25,  # High boolean uncertainty
        binary_pos_prob=0.2,  # Less positive (chaotic)
        binary_neg_prob=0.6,  # More negative (chaotic)
        binary_neutral_prob=0.2,  # Neutral stays same
        chaos_amplifier=1.8,  # Amplified chaos
        drift_rate=0.1,  # Fast drift
        cascade_strength=0.5,  # Strong cascade effects
        error_snark_level=0.9,  # Maximum snark
    ),
}


class PersonalityContext:
    """Global personality context for kinda-lang execution."""

    _instance: Optional["PersonalityContext"] = None

    def __init__(
        self,
        mood: str = "playful",
        chaos_level: int = 5,
        seed: Optional[int] = None,
        error_mode: ErrorHandlingMode = ErrorHandlingMode.WARNING,
    ):
        self.mood = mood.lower()
        self.profile = PERSONALITY_PROFILES.get(self.mood, PERSONALITY_PROFILES["playful"])
        self.chaos_level = chaos_level
        self.chaos_multiplier = self._calculate_chaos_multiplier(chaos_level)
        self.execution_count = 0
        self.instability_level = 0.0  # For cascade failures
        self.drift_accumulator: Dict[str, Dict[str, Any]] = {}  # For time-based drift

        # Performance optimizations (Epic #125 Task 3)
        self._probability_cache: Optional[ProbabilityCache] = None  # Lazy initialization
        self._optimized_rng = OptimizedRandomState(seed)  # Pre-generate batches of random numbers

        # Centralized random number generator for reproducibility (keeping for backward compatibility)
        self.seed = seed
        self.rng = random.Random(seed)  # Create seeded RNG instance

        # Error tracking (Issue #112)
        self.error_tracker = ErrorTracker(error_mode)

    @classmethod
    def get_instance(cls) -> "PersonalityContext":
        """Get or create singleton personality context."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _calculate_chaos_multiplier(self, chaos_level: int) -> float:
        """Calculate chaos multiplier from level (1-10 scale)."""
        # Chaos level 5 is baseline (1.0 multiplier)
        # Level 1-2: 0.2-0.6 (minimal chaos)
        # Level 3-4: 0.6-1.0 (low chaos)
        # Level 5-6: 1.0-1.4 (medium chaos) - DEFAULT
        # Level 7-8: 1.4-1.8 (high chaos)
        # Level 9-10: 1.8-2.2 (maximum chaos)

        if chaos_level <= 2:
            # Minimal chaos (very predictable)
            return 0.2 + (chaos_level - 1) * 0.2  # 0.2 to 0.4
        elif chaos_level <= 4:
            # Low chaos (slight unpredictability)
            return 0.4 + (chaos_level - 2) * 0.2  # 0.4 to 0.8
        elif chaos_level <= 6:
            # Medium chaos (balanced randomness) - DEFAULT
            return 0.8 + (chaos_level - 4) * 0.3  # 0.8 to 1.4
        elif chaos_level <= 8:
            # High chaos (significant randomness)
            return 1.4 + (chaos_level - 6) * 0.2  # 1.4 to 1.8
        else:
            # Maximum chaos (highly unpredictable)
            return 1.8 + (chaos_level - 8) * 0.2  # 1.8 to 2.2

    def _get_probability_cache(self) -> ProbabilityCache:
        """Get or create the probability cache for performance optimization."""
        if self._probability_cache is None:
            self._probability_cache = ProbabilityCache(self)
        return self._probability_cache

    def _invalidate_caches(self) -> None:
        """Invalidate all performance caches when personality changes."""
        if self._probability_cache is not None:
            self._probability_cache.invalidate()
        # Reset optimized RNG with new seed
        self._optimized_rng = OptimizedRandomState(self.seed)

    def get_cached_probability(self, construct_name: str) -> Optional[float]:
        """Get cached probability for performance optimization (Epic #125 Task 3)."""
        cache = self._get_probability_cache()
        return cache.get_cached_probability(construct_name)

    def get_optimized_random(self) -> float:
        """Get optimized random float for performance (Epic #125 Task 3)."""
        return self._optimized_rng.random()

    def get_optimized_randint(self, a: int, b: int) -> int:
        """Get optimized random integer for performance (Epic #125 Task 3)."""
        return self._optimized_rng.randint(a, b)

    def get_optimized_uniform(self, a: float, b: float) -> float:
        """Get optimized uniform random float for performance (Epic #125 Task 3)."""
        return self._optimized_rng.uniform(a, b)

    def get_optimized_choice(self, seq: Any) -> Any:
        """Get optimized random choice for performance (Epic #125 Task 3)."""
        return self._optimized_rng.choice(seq)

    def get_optimized_gauss(self, mu: float, sigma: float) -> float:
        """Get optimized Gaussian random number for performance (Epic #125 Task 3)."""
        return self._optimized_rng.gauss(mu, sigma)

    @classmethod
    def set_mood(cls, mood: str) -> None:
        """Set the global mood/personality."""
        current_chaos_level = cls._instance.chaos_level if cls._instance else 5
        current_seed = cls._instance.seed if cls._instance else None
        cls._instance = cls(mood, current_chaos_level, current_seed)
        # Clear performance optimization state when personality changes
        clear_eventually_until_evaluators()

    @classmethod
    def set_chaos_level(cls, chaos_level: int) -> None:
        """Set the global chaos level."""
        current_mood = cls._instance.mood if cls._instance else "playful"
        current_seed = cls._instance.seed if cls._instance else None
        cls._instance = cls(current_mood, chaos_level, current_seed)
        # Clear performance optimization state when personality changes
        clear_eventually_until_evaluators()

    @classmethod
    def set_seed(cls, seed: Optional[int]) -> None:
        """Set the global random seed."""
        current_mood = cls._instance.mood if cls._instance else "playful"
        current_chaos_level = cls._instance.chaos_level if cls._instance else 5
        cls._instance = cls(current_mood, current_chaos_level, seed)
        # Clear performance optimization state when personality changes
        clear_eventually_until_evaluators()

    def get_chaos_probability(self, base_key: str, condition: Any = True) -> float:
        """Get chaos-adjusted probability for a construct."""
        base_prob = getattr(self.profile, f"{base_key}_base", 0.5)

        # Combine personality profile chaos_amplifier with chaos_level multiplier
        combined_chaos_amplifier = self.profile.chaos_amplifier * self.chaos_multiplier

        # Apply chaos amplifier - simpler approach
        # combined_chaos_amplifier < 1.0 = more reliable (less chaos)
        # combined_chaos_amplifier > 1.0 = more chaotic
        if combined_chaos_amplifier < 1.0:
            # More reliable: pull probabilities toward their "success" direction
            if base_prob >= 0.5:
                # High base prob -> make it higher (more reliable)
                adjusted = base_prob + (1.0 - base_prob) * (1.0 - combined_chaos_amplifier)
            else:
                # Low base prob -> make it lower (more predictably low)
                adjusted = base_prob * combined_chaos_amplifier
        else:
            # More chaotic: pull probabilities toward 0.5 (unpredictable)
            if base_prob > 0.5:
                adjusted = base_prob - (base_prob - 0.5) * (combined_chaos_amplifier - 1.0)
            else:
                adjusted = base_prob + (0.5 - base_prob) * (combined_chaos_amplifier - 1.0)

        # Apply cascade effects
        if self.instability_level > 0:
            cascade_impact = self.instability_level * self.profile.cascade_strength
            adjusted = adjusted * (1.0 - cascade_impact)

        # Ensure probability stays in valid range
        return max(0.0, min(1.0, adjusted))

    def get_fuzz_range(self, base_key: str = "int") -> Tuple[int, int]:
        """Get chaos-adjusted fuzz range."""
        base_range = getattr(self.profile, f"{base_key}_fuzz_range", (-1, 1))
        combined_amplifier = self.profile.chaos_amplifier * self.chaos_multiplier

        # Scale the range by combined chaos amplifier
        min_val, max_val = base_range
        scaled_min = int(min_val * combined_amplifier)
        scaled_max = int(max_val * combined_amplifier)

        return (scaled_min, scaled_max)

    def get_float_drift_range(self) -> Tuple[float, float]:
        """Get chaos-adjusted float drift range."""
        base_range = self.profile.float_drift_range
        combined_amplifier = self.profile.chaos_amplifier * self.chaos_multiplier

        # Scale the range by combined chaos amplifier
        min_val, max_val = base_range
        scaled_min = min_val * combined_amplifier
        scaled_max = max_val * combined_amplifier

        return (scaled_min, scaled_max)

    def get_ish_variance(self) -> float:
        """Get chaos-adjusted ish variance."""
        combined_amplifier = self.profile.chaos_amplifier * self.chaos_multiplier
        return self.profile.ish_variance * combined_amplifier

    def get_ish_tolerance(self) -> float:
        """Get chaos-adjusted ish tolerance."""
        combined_amplifier = self.profile.chaos_amplifier * self.chaos_multiplier
        return self.profile.ish_tolerance * combined_amplifier

    def get_bool_uncertainty(self) -> float:
        """Get personality-adjusted boolean uncertainty."""
        combined_amplifier = self.profile.chaos_amplifier * self.chaos_multiplier
        uncertainty = self.profile.bool_uncertainty * combined_amplifier

        # Add instability effects
        if self.instability_level > 0.1:
            uncertainty += self.instability_level * 0.1

        # Keep uncertainty within reasonable bounds
        return max(0.0, min(0.5, uncertainty))

    def get_binary_probabilities(self) -> Tuple[float, float, float]:
        """Get personality-adjusted binary probabilities (pos, neg, neutral)."""
        # Apply chaos effects to make probabilities more or less predictable
        pos = self.profile.binary_pos_prob
        neg = self.profile.binary_neg_prob
        neutral = self.profile.binary_neutral_prob

        # Apply combined chaos amplifier - make more/less extreme
        combined_amplifier = self.profile.chaos_amplifier * self.chaos_multiplier
        if combined_amplifier > 1.0:
            # More chaotic: push toward extremes
            factor = combined_amplifier - 1.0
            pos = pos * (1.0 + factor * 0.5)
            neg = neg * (1.0 + factor * 0.5)
            neutral = neutral * (1.0 - factor * 0.5)
        elif combined_amplifier < 1.0:
            # More reliable: balance toward neutral
            factor = 1.0 - combined_amplifier
            pos = pos + (neutral - pos) * factor * 0.3
            neg = neg + (neutral - neg) * factor * 0.3

        # Normalize to ensure they add up to 1.0
        total = pos + neg + neutral
        if total > 0:
            pos /= total
            neg /= total
            neutral /= total

        return (pos, neg, neutral)

    def update_instability(self, failed: bool = False) -> None:
        """Update system instability for cascade effects."""
        if failed:
            self.instability_level += 0.1 * self.profile.cascade_strength
        else:
            # Stability slowly recovers
            self.instability_level *= 0.95

        # Keep instability in reasonable bounds
        self.instability_level = max(0.0, min(1.0, self.instability_level))

    def increment_execution(self) -> None:
        """Track execution count for time-based effects."""
        self.execution_count += 1

    def register_variable(self, var_name: str, initial_value: Any, var_type: str = "float") -> None:
        """Register a variable for time-based drift tracking."""
        current_time = time.time()
        self.drift_accumulator[var_name] = {
            "creation_time": current_time,
            "last_access_time": current_time,
            "access_count": 0,
            "initial_value": initial_value,
            "var_type": var_type,
            "accumulated_drift": 0.0,
        }

    def get_time_drift(self, var_name: str, current_value: Any) -> float:
        """Calculate time-based drift for a variable."""
        if var_name not in self.drift_accumulator:
            # Variable not registered yet, no drift
            return 0.0

        var_info = self.drift_accumulator[var_name]
        current_time = time.time()

        # Calculate age-based drift
        age_seconds = current_time - var_info["creation_time"]
        time_since_access = current_time - var_info["last_access_time"]

        # Update access tracking
        var_info["access_count"] += 1
        var_info["last_access_time"] = current_time

        # Base drift calculation:
        # - Older variables drift more
        # - More frequently accessed variables drift more
        # - Drift rate from personality profile controls speed
        base_drift_rate = self.profile.drift_rate
        if base_drift_rate <= 0:
            return 0.0

        # Age factor: logarithmic scaling to prevent explosive growth
        age_factor = min(1.0, age_seconds / 1000.0)  # Cap at 1000 seconds for max age effect

        # Usage factor: more accesses = more drift (but with diminishing returns)
        usage_factor = min(1.0, var_info["access_count"] / 100.0)  # Cap at 100 accesses

        # Time factor: recent activity causes more drift
        time_factor = max(
            0.1, min(1.0, 10.0 / (time_since_access + 1.0))
        )  # Recent access = more drift

        # Combined drift magnitude
        drift_magnitude = base_drift_rate * (age_factor + usage_factor + time_factor) / 3.0

        # Apply combined chaos amplifier
        combined_amplifier = self.profile.chaos_amplifier * self.chaos_multiplier
        drift_magnitude *= combined_amplifier

        # Generate actual drift value within reasonable bounds
        if isinstance(current_value, (int, float)):
            # Scale drift relative to value magnitude (but ensure minimum drift)
            value_magnitude = max(1.0, abs(float(current_value)))
            max_drift = max(0.01, drift_magnitude * value_magnitude * 0.1)
            drift = self.uniform(-max_drift, max_drift)  # Use seeded RNG
        else:
            # For non-numeric values, use small fixed drift
            drift = self.uniform(-0.1, 0.1) * drift_magnitude  # Use seeded RNG

        # Accumulate drift for this variable
        var_info["accumulated_drift"] += abs(drift)

        return drift

    def get_variable_age(self, var_name: str) -> float:
        """Get the age of a variable in seconds."""
        if var_name not in self.drift_accumulator:
            return 0.0
        creation_time = self.drift_accumulator[var_name]["creation_time"]
        if isinstance(creation_time, (int, float)):
            return float(time.time() - creation_time)
        return 0.0

    def get_variable_drift_stats(self, var_name: str) -> Dict[str, Any]:
        """Get drift statistics for a variable."""
        if var_name not in self.drift_accumulator:
            return {}

        var_info = self.drift_accumulator[var_name].copy()
        var_info["age_seconds"] = self.get_variable_age(var_name)
        return dict(var_info)

    # Centralized random number generation methods for reproducibility
    def random(self) -> float:
        """Get a random float in [0.0, 1.0) from seeded RNG."""
        return self.rng.random()

    def randint(self, a: int, b: int) -> int:
        """Get a random integer from seeded RNG."""
        return self.rng.randint(a, b)

    def uniform(self, a: float, b: float) -> float:
        """Get a uniform random float from seeded RNG."""
        return self.rng.uniform(a, b)

    def choice(self, seq: Any) -> Any:
        """Choose a random element from a sequence using seeded RNG."""
        return self.rng.choice(seq)

    def gauss(self, mu: float, sigma: float) -> float:
        """Get a Gaussian random number from seeded RNG."""
        return self.rng.gauss(mu, sigma)

    def get_seed_info(self) -> Dict[str, Any]:
        """Get information about the current seed configuration."""
        return {
            "seed": self.seed,
            "has_seed": self.seed is not None,
            "rng_state_type": str(type(self.rng.getstate())),
            "reproducible": self.seed is not None,
        }

    def reset_variable_drift(self, var_name: str) -> None:
        """Reset drift accumulation for a variable."""
        if var_name in self.drift_accumulator:
            var_info = self.drift_accumulator[var_name]
            var_info["accumulated_drift"] = 0.0
            var_info["access_count"] = 0
            var_info["creation_time"] = time.time()
            var_info["last_access_time"] = time.time()

    def get_error_message_style(self) -> str:
        """Get personality-appropriate error message style."""
        snark = self.profile.error_snark_level

        if snark < 0.3:
            return "professional"  # Minimal snark, helpful
        elif snark < 0.6:
            return "friendly"  # Light snark, approachable
        elif snark < 0.8:
            return "snarky"  # Moderate snark, personality
        else:
            return "chaotic"  # Maximum snark, chaos

    def chaos_random(self) -> float:
        """Get a random float in [0.0, 1.0) from personality-controlled seeded RNG (instance method)."""
        return self.random()


# Global convenience functions for use in constructs
def get_personality() -> PersonalityContext:
    """Get the current personality context."""
    return PersonalityContext.get_instance()


def chaos_probability(base_key: str, condition: Any = True) -> float:
    """Get personality-adjusted probability for a construct."""
    return get_personality().get_chaos_probability(base_key, condition)


def chaos_fuzz_range(base_key: str = "int") -> Tuple[int, int]:
    """Get personality-adjusted fuzz range."""
    return get_personality().get_fuzz_range(base_key)


def chaos_float_drift_range() -> Tuple[float, float]:
    """Get personality-adjusted float drift range."""
    return get_personality().get_float_drift_range()


def chaos_variance() -> float:
    """Get personality-adjusted ish variance."""
    return get_personality().get_ish_variance()


def chaos_tolerance() -> float:
    """Get personality-adjusted ish tolerance."""
    return get_personality().get_ish_tolerance()


def chaos_binary_probabilities() -> Tuple[float, float, float]:
    """Get personality-adjusted binary probabilities."""
    return get_personality().get_binary_probabilities()


def chaos_bool_uncertainty() -> float:
    """Get personality-adjusted boolean uncertainty."""
    return get_personality().get_bool_uncertainty()


def update_chaos_state(failed: bool = False) -> None:
    """Update chaos state tracking."""
    try:
        personality = get_personality()
        personality.update_instability(failed)
        personality.increment_execution()
    except Exception:
        # If chaos state update fails (e.g., personality system is broken), just continue
        # This prevents cascading exceptions in error handling paths
        pass


# Time-based drift convenience functions
def register_time_variable(var_name: str, initial_value: Any, var_type: str = "float") -> None:
    """Register a variable for time-based drift tracking."""
    return get_personality().register_variable(var_name, initial_value, var_type)


def get_time_drift(var_name: str, current_value: Any) -> float:
    """Get time-based drift for a variable."""
    return get_personality().get_time_drift(var_name, current_value)


def get_variable_age(var_name: str) -> float:
    """Get the age of a variable in seconds."""
    return get_personality().get_variable_age(var_name)


def get_variable_drift_stats(var_name: str) -> Dict[str, Any]:
    """Get drift statistics for a variable."""
    return get_personality().get_variable_drift_stats(var_name)


def reset_variable_drift(var_name: str) -> None:
    """Reset drift accumulation for a variable."""
    return get_personality().reset_variable_drift(var_name)


# Centralized random number generation functions for reproducible chaos
def chaos_random() -> float:
    """Get a random float in [0.0, 1.0) from personality-controlled seeded RNG."""
    return get_personality().random()


def chaos_randint(a: int, b: int) -> int:
    """Get a random integer from personality-controlled seeded RNG."""
    return get_personality().randint(a, b)


def chaos_uniform(a: float, b: float) -> float:
    """Get a uniform random float from personality-controlled seeded RNG."""
    return get_personality().uniform(a, b)


def chaos_choice(seq: Any) -> Any:
    """Choose a random element from a sequence using personality-controlled seeded RNG."""
    return get_personality().choice(seq)


def chaos_gauss(mu: float, sigma: float) -> float:
    """Get a Gaussian random number from personality-controlled seeded RNG."""
    return get_personality().gauss(mu, sigma)


def get_kinda_repeat_variance() -> float:
    """Get personality-adjusted variance for ~kinda_repeat constructs."""
    personality = get_personality()
    base_variance = personality.profile.kinda_repeat_variance
    # Apply chaos multiplier for additional variance scaling
    combined_amplifier = personality.profile.chaos_amplifier * personality.chaos_multiplier
    return base_variance * combined_amplifier


def get_eventually_until_confidence() -> float:
    """Get personality-adjusted confidence threshold for ~eventually_until constructs."""
    personality = get_personality()
    base_confidence = personality.profile.eventually_until_confidence
    # Apply chaos effects - more chaos means lower confidence thresholds
    combined_amplifier = personality.profile.chaos_amplifier * personality.chaos_multiplier
    if combined_amplifier > 1.0:
        # More chaotic: reduce confidence threshold (terminate earlier)
        factor = min(0.3, (combined_amplifier - 1.0) * 0.2)  # Cap reduction
        adjusted = base_confidence - factor
    else:
        # More reliable: increase confidence threshold (be more certain)
        factor = (1.0 - combined_amplifier) * 0.1
        adjusted = base_confidence + factor

    # Keep confidence in reasonable bounds
    return max(0.5, min(0.99, adjusted))


def get_seed_info() -> Dict[str, Any]:
    """Get information about the current seed configuration."""
    return get_personality().get_seed_info()


# Error tracking convenience functions (Issue #112)
def get_error_tracker() -> ErrorTracker:
    """Get the global error tracker."""
    return get_personality().error_tracker


def record_construct_error(
    construct_type: str, error_message: str, context: str = "", recovered: bool = True
) -> None:
    """Record an error from a fuzzy construct."""
    get_error_tracker().record_error(construct_type, error_message, context, recovered)
