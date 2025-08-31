# kinda/personality.py

"""
Kinda-Lang Personality and Chaos Control System

Provides configurable chaos levels through personality profiles that affect
fuzzy construct behavior, randomness, and error message tone.
"""

import random
from dataclasses import dataclass
from typing import Dict, Optional, Any, Tuple


@dataclass
class ChaosProfile:
    """Configuration for chaos levels in fuzzy constructs."""

    # Probability modifiers for conditional constructs
    sometimes_base: float = 0.5  # Base probability for ~sometimes
    maybe_base: float = 0.6  # Base probability for ~maybe
    probably_base: float = 0.7  # Base probability for ~probably
    rarely_base: float = 0.15  # Base probability for ~rarely
    sorta_print_base: float = 0.8  # Base probability for ~sorta print

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


# Pre-defined personality profiles based on user feedback requirements
PERSONALITY_PROFILES: Dict[str, ChaosProfile] = {
    "reliable": ChaosProfile(
        sometimes_base=0.95,  # Almost always execute
        maybe_base=0.95,  # Almost always execute
        probably_base=0.95,  # Almost always execute
        rarely_base=0.85,  # Reliable even when "rarely"
        sorta_print_base=0.95,  # Almost always print
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

    def __init__(self, mood: str = "playful"):
        self.mood = mood.lower()
        self.profile = PERSONALITY_PROFILES.get(self.mood, PERSONALITY_PROFILES["playful"])
        self.execution_count = 0
        self.instability_level = 0.0  # For cascade failures
        self.drift_accumulator = {}  # For time-based drift

    @classmethod
    def get_instance(cls) -> "PersonalityContext":
        """Get or create singleton personality context."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def set_mood(cls, mood: str) -> None:
        """Set the global mood/personality."""
        cls._instance = cls(mood)

    def get_chaos_probability(self, base_key: str, condition: Any = True) -> float:
        """Get chaos-adjusted probability for a construct."""
        base_prob = getattr(self.profile, f"{base_key}_base", 0.5)

        # Apply chaos amplifier - simpler approach
        # chaos_amplifier < 1.0 = more reliable (less chaos)
        # chaos_amplifier > 1.0 = more chaotic
        if self.profile.chaos_amplifier < 1.0:
            # More reliable: pull probabilities toward their "success" direction
            if base_prob >= 0.5:
                # High base prob -> make it higher (more reliable)
                adjusted = base_prob + (1.0 - base_prob) * (1.0 - self.profile.chaos_amplifier)
            else:
                # Low base prob -> make it lower (more predictably low)
                adjusted = base_prob * self.profile.chaos_amplifier
        else:
            # More chaotic: pull probabilities toward 0.5 (unpredictable)
            if base_prob > 0.5:
                adjusted = base_prob - (base_prob - 0.5) * (self.profile.chaos_amplifier - 1.0)
            else:
                adjusted = base_prob + (0.5 - base_prob) * (self.profile.chaos_amplifier - 1.0)

        # Apply cascade effects
        if self.instability_level > 0:
            cascade_impact = self.instability_level * self.profile.cascade_strength
            adjusted = adjusted * (1.0 - cascade_impact)

        # Ensure probability stays in valid range
        return max(0.0, min(1.0, adjusted))

    def get_fuzz_range(self, base_key: str = "int") -> Tuple[int, int]:
        """Get chaos-adjusted fuzz range."""
        base_range = getattr(self.profile, f"{base_key}_fuzz_range", (-1, 1))
        amplifier = self.profile.chaos_amplifier

        # Scale the range by chaos amplifier
        min_val, max_val = base_range
        scaled_min = int(min_val * amplifier)
        scaled_max = int(max_val * amplifier)

        return (scaled_min, scaled_max)

    def get_float_drift_range(self) -> Tuple[float, float]:
        """Get chaos-adjusted float drift range."""
        base_range = self.profile.float_drift_range
        amplifier = self.profile.chaos_amplifier

        # Scale the range by chaos amplifier
        min_val, max_val = base_range
        scaled_min = min_val * amplifier
        scaled_max = max_val * amplifier

        return (scaled_min, scaled_max)

    def get_ish_variance(self) -> float:
        """Get chaos-adjusted ish variance."""
        return self.profile.ish_variance * self.profile.chaos_amplifier

    def get_ish_tolerance(self) -> float:
        """Get chaos-adjusted ish tolerance."""
        return self.profile.ish_tolerance * self.profile.chaos_amplifier

    def get_bool_uncertainty(self) -> float:
        """Get personality-adjusted boolean uncertainty."""
        uncertainty = self.profile.bool_uncertainty * self.profile.chaos_amplifier

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

        # Apply chaos amplifier - make more/less extreme
        if self.profile.chaos_amplifier > 1.0:
            # More chaotic: push toward extremes
            factor = self.profile.chaos_amplifier - 1.0
            pos = pos * (1.0 + factor * 0.5)
            neg = neg * (1.0 + factor * 0.5)
            neutral = neutral * (1.0 - factor * 0.5)
        elif self.profile.chaos_amplifier < 1.0:
            # More reliable: balance toward neutral
            factor = 1.0 - self.profile.chaos_amplifier
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
    personality = get_personality()
    personality.update_instability(failed)
    personality.increment_execution()
