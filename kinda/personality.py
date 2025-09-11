# kinda/personality.py

"""
Kinda-Lang Personality and Chaos Control System

Provides configurable chaos levels through personality profiles that affect
fuzzy construct behavior, randomness, and error message tone.
"""

import random
import time
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

    # Loop construct continuation probabilities
    sometimes_while_base: float = 0.6  # Base probability for ~sometimes_while continuation
    maybe_for_base: float = 0.7  # Base probability for ~maybe_for item execution

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
        sometimes_while_base=0.90,  # 90% continuation probability per task spec
        maybe_for_base=0.95,  # 95% execution probability per item per task spec
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

    def __init__(self, mood: str = "playful", chaos_level: int = 5, seed: Optional[int] = None):
        self.mood = mood.lower()
        self.profile = PERSONALITY_PROFILES.get(self.mood, PERSONALITY_PROFILES["playful"])
        self.chaos_level = chaos_level
        self.chaos_multiplier = self._calculate_chaos_multiplier(chaos_level)
        self.execution_count = 0
        self.instability_level = 0.0  # For cascade failures
        self.drift_accumulator = {}  # For time-based drift

        # Centralized random number generator for reproducibility
        self.seed = seed
        self.rng = random.Random(seed)  # Create seeded RNG instance

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

    @classmethod
    def set_mood(cls, mood: str) -> None:
        """Set the global mood/personality."""
        current_chaos_level = cls._instance.chaos_level if cls._instance else 5
        current_seed = cls._instance.seed if cls._instance else None
        cls._instance = cls(mood, current_chaos_level, current_seed)

    @classmethod
    def set_chaos_level(cls, chaos_level: int) -> None:
        """Set the global chaos level."""
        current_mood = cls._instance.mood if cls._instance else "playful"
        current_seed = cls._instance.seed if cls._instance else None
        cls._instance = cls(current_mood, chaos_level, current_seed)

    @classmethod
    def set_seed(cls, seed: Optional[int]) -> None:
        """Set the global random seed."""
        current_mood = cls._instance.mood if cls._instance else "playful"
        current_chaos_level = cls._instance.chaos_level if cls._instance else 5
        cls._instance = cls(current_mood, current_chaos_level, seed)

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
        return time.time() - self.drift_accumulator[var_name]["creation_time"]

    def get_variable_drift_stats(self, var_name: str) -> Dict[str, Any]:
        """Get drift statistics for a variable."""
        if var_name not in self.drift_accumulator:
            return {}

        var_info = self.drift_accumulator[var_name].copy()
        var_info["age_seconds"] = self.get_variable_age(var_name)
        return var_info

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

    def choice(self, seq):
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


def chaos_choice(seq):
    """Choose a random element from a sequence using personality-controlled seeded RNG."""
    return get_personality().choice(seq)


def chaos_gauss(mu: float, sigma: float) -> float:
    """Get a Gaussian random number from personality-controlled seeded RNG."""
    return get_personality().gauss(mu, sigma)


def get_seed_info() -> Dict[str, Any]:
    """Get information about the current seed configuration."""
    return get_personality().get_seed_info()
