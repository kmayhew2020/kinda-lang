"""
Probability Context Management

This module provides context managers for controlling probability behavior
in kinda-lang constructs with Python-native APIs.
"""

import threading
from contextlib import contextmanager
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, Optional, Generator, Callable, List
from contextvars import ContextVar

from ..personality import PersonalityContext as PersonalityManager


class ProbabilityMode(Enum):
    """Probability execution modes"""

    NORMAL = "normal"  # Standard probabilistic behavior
    DETERMINISTIC = "deterministic"  # Disable all randomness
    CHAOS = "chaos"  # Maximum randomness
    TESTING = "testing"  # Reproducible randomness with seed
    PRODUCTION = "production"  # Conservative probabilities


@dataclass
class ProbabilityProfile:
    """Predefined probability configuration profiles"""

    name: str
    description: str
    mode: ProbabilityMode
    construct_overrides: Dict[str, float] = field(default_factory=dict)
    personality_config: Dict[str, Any] = field(default_factory=dict)
    seed: Optional[int] = None

    @classmethod
    def create_testing_profile(cls, seed: int = 42) -> "ProbabilityProfile":
        """Create a testing profile with reproducible randomness"""
        return cls(
            name="testing",
            description="Reproducible randomness for testing",
            mode=ProbabilityMode.TESTING,
            construct_overrides={
                "sometimes": 0.7,
                "maybe": 0.5,
                "probably": 0.8,
                "rarely": 0.2,
                "sorta_print": 0.8,
            },
            seed=seed,
        )

    @classmethod
    def create_production_profile(cls) -> "ProbabilityProfile":
        """Create a conservative production profile"""
        return cls(
            name="production",
            description="Conservative probabilities for production",
            mode=ProbabilityMode.PRODUCTION,
            construct_overrides={
                "sometimes": 0.9,  # More predictable
                "maybe": 0.7,  # Less random
                "probably": 0.95,  # Very likely
                "rarely": 0.1,  # Very rare
                "sorta_print": 1.0,  # Always print in production
            },
        )

    @classmethod
    def create_chaos_profile(cls) -> "ProbabilityProfile":
        """Create maximum chaos profile"""
        return cls(
            name="chaos",
            description="Maximum randomness and unpredictability",
            mode=ProbabilityMode.CHAOS,
            construct_overrides={
                "sometimes": 0.5,
                "maybe": 0.5,
                "probably": 0.6,  # Less probable than expected
                "rarely": 0.4,  # More frequent than expected
                "sorta_print": 0.3,  # Mostly silent
            },
        )

    @classmethod
    def create_deterministic_profile(cls) -> "ProbabilityProfile":
        """Create deterministic profile (no randomness)"""
        return cls(
            name="deterministic",
            description="Deterministic execution, no randomness",
            mode=ProbabilityMode.DETERMINISTIC,
            construct_overrides={
                "sometimes": 1.0,  # Always execute
                "maybe": 1.0,
                "probably": 1.0,
                "rarely": 0.0,  # Never execute
                "sorta_print": 1.0,
            },
        )


# Context variable for thread-local probability context
_probability_context: ContextVar[Optional["ProbabilityContext"]] = ContextVar(
    "probability_context", default=None
)


class ProbabilityContext:
    """
    Context manager for controlling probability behavior in kinda-lang constructs.

    This provides a Python-native API for managing probabilistic behavior,
    enabling fine-grained control over randomness and chaos in kinda-lang programs.
    """

    def __init__(
        self,
        profile: Optional[ProbabilityProfile] = None,
        overrides: Optional[Dict[str, float]] = None,
        seed: Optional[int] = None,
        mode: Optional[ProbabilityMode] = None,
        personality: Optional[str] = None,
    ):
        """
        Initialize probability context.

        Args:
            profile: Predefined probability profile
            overrides: Override probabilities for specific constructs
            seed: Random seed for reproducible behavior
            mode: Execution mode override
            personality: Personality to use ('reliable', 'chaotic', etc.)
        """
        self.profile = profile or ProbabilityProfile.create_testing_profile()
        self.overrides = overrides or {}
        self.seed = seed or self.profile.seed
        self.mode = mode or self.profile.mode
        self.personality = personality

        # Merge overrides with profile overrides
        self.effective_overrides = {**self.profile.construct_overrides, **self.overrides}

        # Track nested contexts
        self._parent_context: Optional["ProbabilityContext"] = None

        # Performance monitoring
        self.construct_calls: Dict[str, int] = {}
        self.total_calls: int = 0

        # Integration with personality system
        self.personality_manager: Optional[PersonalityManager] = None

    def __enter__(self) -> "ProbabilityContext":
        """Enter the probability context"""
        # Store parent context for nesting support
        self._parent_context = _probability_context.get()

        # Set this as the current context
        _probability_context.set(self)

        # Set random seed if specified
        if self.seed is not None:
            import random

            random.seed(self.seed)

        # Initialize personality manager if specified
        if self.personality:
            self.personality_manager = PersonalityManager()
            # Set personality would be called here in complete implementation

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the probability context"""
        # Restore parent context
        _probability_context.set(self._parent_context)

    def get_probability(self, construct_name: str, default: float = 0.5) -> float:
        """
        Get effective probability for a construct.

        Args:
            construct_name: Name of the construct ('sometimes', 'maybe', etc.)
            default: Default probability if not overridden

        Returns:
            Effective probability value between 0.0 and 1.0
        """
        # Track usage
        self.construct_calls[construct_name] = self.construct_calls.get(construct_name, 0) + 1
        self.total_calls += 1

        # Check for override
        if construct_name in self.effective_overrides:
            return self.effective_overrides[construct_name]

        # Apply mode-specific adjustments
        if self.mode == ProbabilityMode.DETERMINISTIC:
            return 1.0 if default > 0.5 else 0.0
        elif self.mode == ProbabilityMode.CHAOS:
            # Add some chaos to the default
            import random

            chaos_factor = random.uniform(-0.2, 0.2)
            return max(0.0, min(1.0, default + chaos_factor))
        elif self.mode == ProbabilityMode.PRODUCTION:
            # More conservative (closer to extremes)
            return 0.9 if default > 0.5 else 0.1

        return default

    def with_override(self, construct_name: str, probability: float) -> "ProbabilityContext":
        """
        Create a new context with an additional override.

        Args:
            construct_name: Name of construct to override
            probability: New probability value

        Returns:
            New ProbabilityContext with the override applied
        """
        new_overrides = {**self.overrides, construct_name: probability}
        return ProbabilityContext(
            profile=self.profile,
            overrides=new_overrides,
            seed=self.seed,
            mode=self.mode,
            personality=self.personality,
        )

    def with_profile(self, profile: ProbabilityProfile) -> "ProbabilityContext":
        """
        Create a new context with a different profile.

        Args:
            profile: New profile to use

        Returns:
            New ProbabilityContext with the profile applied
        """
        return ProbabilityContext(
            profile=profile,
            overrides=self.overrides,  # Keep current overrides
            seed=self.seed,
            mode=self.mode,
            personality=self.personality,
        )

    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics for this context"""
        return {
            "total_calls": self.total_calls,
            "construct_calls": self.construct_calls.copy(),
            "most_used": (
                max(self.construct_calls, key=self.construct_calls.get)
                if self.construct_calls
                else None
            ),
            "profile_name": self.profile.name,
            "mode": self.mode.value,
            "seed": self.seed,
        }

    @staticmethod
    def get_current() -> Optional["ProbabilityContext"]:
        """Get the current probability context"""
        return _probability_context.get()

    @staticmethod
    @contextmanager
    def temporary_override(construct_name: str, probability: float) -> Generator[None, None, None]:
        """
        Temporarily override a construct's probability.

        Args:
            construct_name: Name of construct to override
            probability: Temporary probability value
        """
        current = ProbabilityContext.get_current()
        if current:
            with current.with_override(construct_name, probability):
                yield
        else:
            # No current context, create a temporary one
            with ProbabilityContext(overrides={construct_name: probability}):
                yield

    @staticmethod
    @contextmanager
    def testing_mode(seed: int = 42) -> Generator["ProbabilityContext", None, None]:
        """
        Context manager for testing mode with reproducible randomness.

        Args:
            seed: Random seed for reproducibility
        """
        profile = ProbabilityProfile.create_testing_profile(seed)
        with ProbabilityContext(profile=profile) as ctx:
            yield ctx

    @staticmethod
    @contextmanager
    def production_mode() -> Generator["ProbabilityContext", None, None]:
        """Context manager for production mode with conservative probabilities"""
        profile = ProbabilityProfile.create_production_profile()
        with ProbabilityContext(profile=profile) as ctx:
            yield ctx

    @staticmethod
    @contextmanager
    def chaos_mode() -> Generator["ProbabilityContext", None, None]:
        """Context manager for maximum chaos mode"""
        profile = ProbabilityProfile.create_chaos_profile()
        with ProbabilityContext(profile=profile) as ctx:
            yield ctx

    @staticmethod
    @contextmanager
    def deterministic_mode() -> Generator["ProbabilityContext", None, None]:
        """Context manager for deterministic mode (no randomness)"""
        profile = ProbabilityProfile.create_deterministic_profile()
        with ProbabilityContext(profile=profile) as ctx:
            yield ctx


# Utility functions for getting probabilities from current context
def get_construct_probability(construct_name: str, default: float = 0.5) -> float:
    """
    Get probability for a construct from current context.

    Args:
        construct_name: Name of the construct
        default: Default probability if no context is active

    Returns:
        Effective probability value
    """
    current_context = ProbabilityContext.get_current()
    if current_context:
        return current_context.get_probability(construct_name, default)
    return default


def is_deterministic_mode() -> bool:
    """Check if current context is in deterministic mode"""
    current_context = ProbabilityContext.get_current()
    return current_context and current_context.mode == ProbabilityMode.DETERMINISTIC


def is_testing_mode() -> bool:
    """Check if current context is in testing mode"""
    current_context = ProbabilityContext.get_current()
    return current_context and current_context.mode == ProbabilityMode.TESTING
