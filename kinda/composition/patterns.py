# kinda/composition/patterns.py

"""
Kinda-Lang Composition Patterns Library

Provides common composition patterns for building composite constructs
from basic probabilistic primitives.
"""

from typing import Any, Dict, List, Optional, Callable
from kinda.composition.framework import (
    CompositeConstruct,
    CompositionStrategy,
    CompositionConfig,
    CompositionEngine,
    PersonalityBridge,
)


class UnionComposition(CompositeConstruct):
    """Template for union-based compositions (like Task 1 sorta_print)."""

    def __init__(
        self, name: str, basic_constructs: List[str], bridge_config: Dict[str, float] = None
    ):
        config = CompositionConfig(
            strategy=CompositionStrategy.UNION, personality_bridges=bridge_config or {}
        )
        super().__init__(name, config)
        self.basic_constructs = basic_constructs

    def get_basic_constructs(self) -> List[str]:
        return self.basic_constructs

    def compose(self, *args, **kwargs) -> bool:
        """Execute union composition."""
        from kinda.composition.framework import get_composition_engine

        engine = get_composition_engine()

        # Get basic construct functions from global scope
        gates = []
        for construct_name in self.basic_constructs:
            gate_func = globals().get(construct_name)
            if gate_func is None:
                # Try importing from kinda runtime
                try:
                    from kinda.langs.python.runtime import fuzzy

                    gate_func = getattr(fuzzy, construct_name, None)
                except ImportError:
                    pass

            if gate_func is None:
                raise RuntimeError(f"Basic construct '{construct_name}' not available")
            gates.append(gate_func)

        # Execute union strategy
        base_result = engine._execute_union(gates, *args, **kwargs)

        # Apply personality bridge if configured
        return PersonalityBridge.apply_personality_bridge(
            base_result, self.name, self.config.personality_bridges
        )

    def get_target_probabilities(self) -> Dict[str, float]:
        """Calculate target probabilities for each personality."""
        from kinda.personality import get_personality, chaos_probability

        personality = get_personality()
        basic_probs = []

        for construct in self.basic_constructs:
            prob = chaos_probability(construct.replace("_base", ""))
            basic_probs.append(prob)

        composite_prob = PersonalityBridge.calculate_composite_probability(
            basic_probs, CompositionStrategy.UNION
        )

        return {personality.mood: composite_prob}


class ThresholdComposition(CompositeConstruct):
    """Pattern for threshold-based compositions."""

    def __init__(self, name: str, basic_constructs: List[str], threshold: float = 0.5):
        config = CompositionConfig(strategy=CompositionStrategy.WEIGHTED, personality_bridges={})
        super().__init__(name, config)
        self.basic_constructs = basic_constructs
        self.threshold = threshold

    def get_basic_constructs(self) -> List[str]:
        return self.basic_constructs

    def compose(self, *args, **kwargs) -> bool:
        """Execute threshold composition."""
        total_votes = 0
        positive_votes = 0

        for construct_name in self.basic_constructs:
            gate_func = globals().get(construct_name)
            if gate_func is None:
                # Try importing from kinda runtime
                try:
                    from kinda.langs.python.runtime import fuzzy

                    gate_func = getattr(fuzzy, construct_name, None)
                except ImportError:
                    pass

            if gate_func:
                try:
                    if gate_func(*args, **kwargs):
                        positive_votes += 1
                    total_votes += 1
                except Exception:
                    pass  # Skip failed constructs

        if total_votes == 0:
            return False

        vote_ratio = positive_votes / total_votes
        return vote_ratio >= self.threshold

    def get_target_probabilities(self) -> Dict[str, float]:
        """Calculate target probabilities for threshold composition."""
        from kinda.personality import get_personality, chaos_probability

        personality = get_personality()
        basic_probs = []

        for construct in self.basic_constructs:
            prob = chaos_probability(construct.replace("_base", ""))
            basic_probs.append(prob)

        # For threshold composition, estimate probability based on threshold
        avg_prob = sum(basic_probs) / len(basic_probs) if basic_probs else 0.5
        # Threshold probability is roughly the average probability
        # adjusted by how strict the threshold is
        threshold_prob = avg_prob * (1 - abs(self.threshold - 0.5))

        return {personality.mood: threshold_prob}


class ToleranceComposition(CompositeConstruct):
    """Pattern for tolerance-based compositions (for ~ish patterns)."""

    def __init__(self, name: str, base_construct: str, tolerance_func: str):
        config = CompositionConfig(strategy=CompositionStrategy.CONDITIONAL, personality_bridges={})
        super().__init__(name, config)
        self.base_construct = base_construct
        self.tolerance_func = tolerance_func

    def get_basic_constructs(self) -> List[str]:
        return [self.base_construct, self.tolerance_func]

    def compose(self, value_a: Any, value_b: Any, tolerance: float = None) -> bool:
        """Execute tolerance-based comparison composition."""
        from kinda.personality import chaos_tolerance

        # Get fuzzy value using base construct
        base_func = globals().get(self.base_construct)
        if base_func is None:
            # Try importing from kinda runtime
            try:
                from kinda.langs.python.runtime import fuzzy

                base_func = getattr(fuzzy, self.base_construct, None)
            except ImportError:
                pass

        if not base_func:
            raise RuntimeError(f"Base construct '{self.base_construct}' not available")

        # For tolerance composition, we compare fuzzy values
        try:
            fuzzy_a = float(base_func(value_a) if callable(base_func) else value_a)
            fuzzy_b = float(base_func(value_b) if callable(base_func) else value_b)
        except (TypeError, ValueError):
            # If conversion fails, fall back to direct comparison
            fuzzy_a = float(value_a) if isinstance(value_a, (int, float)) else 0.0
            fuzzy_b = float(value_b) if isinstance(value_b, (int, float)) else 0.0

        # Calculate tolerance-based comparison
        if tolerance is None:
            tolerance = chaos_tolerance()  # From personality system

        difference = abs(fuzzy_a - fuzzy_b)
        return difference <= tolerance

    def get_target_probabilities(self) -> Dict[str, float]:
        """Calculate target probabilities for tolerance composition."""
        from kinda.personality import get_personality

        personality = get_personality()

        # Tolerance compositions have variable probability based on input values
        # Return a reasonable default for the personality
        base_prob = {
            "reliable": 0.8,  # High precision, stricter tolerance
            "cautious": 0.7,  # Moderate tolerance
            "playful": 0.6,  # More relaxed tolerance
            "chaotic": 0.5,  # Very loose tolerance
        }.get(personality.mood, 0.65)

        return {personality.mood: base_prob}


class IshToleranceComposition(ToleranceComposition):
    """Enhanced tolerance composition specifically for ~ish patterns.

    Demonstrates how ~ish behavior emerges from composition of:
    - ~kinda_float (numerical fuzzing)
    - ~chaos_tolerance (personality-aware tolerance)
    - ~probably (probabilistic decision making)
    - ~sometimes (conditional execution)
    """

    def __init__(self, name: str, mode: str = "comparison"):
        """Initialize ish composition pattern.

        Args:
            name: Pattern name for registration
            mode: "comparison" for conditionals, "assignment" for variable modification
        """
        super().__init__(name, "kinda_float", "chaos_tolerance")
        self.mode = mode
        self._construct_cache = {}  # Cache basic construct functions

    def _get_basic_construct(self, construct_name: str) -> Callable:
        """Get basic construct function with caching."""
        if construct_name not in self._construct_cache:
            try:
                from kinda.langs.python.runtime import fuzzy

                self._construct_cache[construct_name] = getattr(fuzzy, construct_name)
            except ImportError:
                raise RuntimeError(f"Basic construct '{construct_name}' not available")
        return self._construct_cache[construct_name]

    def compose_comparison(self, left_val: Any, right_val: Any, tolerance: float = None) -> bool:
        """Compose ~ish comparison from basic constructs.

        Composition logic:
        1. Apply ~kinda_float to add uncertainty to difference calculation
        2. Use ~chaos_tolerance for personality-aware tolerance
        3. Apply ~probably to final boolean decision

        This shows how numerical fuzzing emerges from basic construct composition.
        """
        try:
            # Get basic construct functions
            kinda_float = self._get_basic_construct("kinda_float")
            probably = self._get_basic_construct("probably")

            # Convert inputs to numeric with error handling (preserve existing behavior)
            try:
                left_val = float(left_val)
                right_val = float(right_val)
            except (ValueError, TypeError) as e:
                from kinda.personality import update_chaos_state

                update_chaos_state(failed=True)
                return probably(False)  # Fallback behavior

            # Get tolerance using personality system if not provided
            if tolerance is None:
                from kinda.personality import chaos_tolerance

                tolerance = chaos_tolerance()

            # Apply composition: ~kinda_float adds uncertainty to calculation
            fuzzy_tolerance = kinda_float(tolerance)
            difference = kinda_float(abs(left_val - right_val))

            # Build ~ish behavior from basic constructs using ~probably
            base_result = difference <= fuzzy_tolerance
            return probably(base_result)

        except Exception as e:
            # Fallback to legacy implementation on any error
            from kinda.langs.python.runtime.fuzzy import ish_comparison

            return ish_comparison(left_val, right_val, tolerance)

    def compose_assignment(self, current_val: Any, target_val: Any = None) -> Any:
        """Compose ~ish variable modification from basic constructs.

        Composition logic:
        1. Use ~kinda_float for fuzzy variance calculation
        2. Apply ~sometimes for conditional adjustment behavior
        3. Demonstrate how variable modification emerges from simpler patterns
        """
        try:
            # Get basic construct functions
            kinda_float = self._get_basic_construct("kinda_float")
            sometimes = self._get_basic_construct("sometimes")

            # Convert to numeric with error handling
            try:
                current_val = float(current_val)
            except (ValueError, TypeError) as e:
                from kinda.personality import update_chaos_state

                update_chaos_state(failed=True)
                return kinda_float(0 if current_val is None else current_val)

            if target_val is None:
                # Standalone case: var~ish → create fuzzy value using composition
                from kinda.personality import chaos_variance

                variance_base = chaos_variance()
                fuzzy_variance = kinda_float(variance_base)
                result = current_val + fuzzy_variance
            else:
                # Assignment case: var ~ish target → show composition behavior
                try:
                    target_val = float(target_val)
                except (ValueError, TypeError):
                    from kinda.personality import update_chaos_state

                    update_chaos_state(failed=True)
                    return kinda_float(current_val)

                # Demonstrate how ~ish emerges from basic construct composition
                adjustment_factor = kinda_float(0.5)  # Fuzzy adjustment factor
                difference = kinda_float(target_val - current_val)

                # Use ~sometimes to show probabilistic decision making
                if sometimes(True):
                    # Adjust towards target using fuzzy factors
                    result = current_val + (difference * adjustment_factor)
                else:
                    # Apply direct fuzzy variance (fallback behavior)
                    from kinda.personality import chaos_variance

                    variance_base = chaos_variance()
                    fuzzy_variance = kinda_float(variance_base)
                    result = current_val + fuzzy_variance

            # Maintain type consistency
            if isinstance(current_val, int) and (target_val is None or isinstance(target_val, int)):
                return int(kinda_float(result))
            else:
                return kinda_float(result)

        except Exception as e:
            # Fallback to legacy implementation on any error
            from kinda.langs.python.runtime.fuzzy import ish_value

            return ish_value(current_val, target_val)

    def get_target_probabilities(self) -> Dict[str, float]:
        """Calculate target probabilities for ~ish patterns."""
        from kinda.personality import get_personality

        personality = get_personality()

        # ~ish patterns have personality-dependent behavior
        base_prob = {
            "reliable": 0.8,  # High precision, stricter tolerance
            "cautious": 0.75,  # Moderately strict tolerance
            "playful": 0.65,  # More relaxed tolerance
            "chaotic": 0.55,  # Very loose tolerance
        }.get(personality.mood, 0.7)

        return {personality.mood: base_prob}


class CompositionPatternFactory:
    """Factory for creating common composition patterns."""

    @staticmethod
    def create_union_pattern(
        name: str, basic_constructs: List[str], bridge_probabilities: Dict[str, float] = None
    ) -> UnionComposition:
        """Create a union composition pattern."""
        return UnionComposition(name, basic_constructs, bridge_probabilities)

    @staticmethod
    def create_threshold_pattern(
        name: str, basic_constructs: List[str], threshold: float = 0.5
    ) -> ThresholdComposition:
        """Create a threshold-based composition pattern."""
        return ThresholdComposition(name, basic_constructs, threshold)

    @staticmethod
    def create_tolerance_pattern(
        name: str, base_construct: str, tolerance_func: str = "kinda_float"
    ) -> ToleranceComposition:
        """Create a tolerance-based composition pattern."""
        return ToleranceComposition(name, base_construct, tolerance_func)

    @staticmethod
    def create_ish_comparison_pattern() -> IshToleranceComposition:
        """Create ~ish comparison composition pattern."""
        return IshToleranceComposition("ish_comparison_pattern", "comparison")

    @staticmethod
    def create_ish_assignment_pattern() -> IshToleranceComposition:
        """Create ~ish assignment composition pattern."""
        return IshToleranceComposition("ish_assignment_pattern", "assignment")

    @staticmethod
    def create_custom_pattern(
        name: str,
        strategy: CompositionStrategy,
        basic_constructs: List[str],
        config: CompositionConfig = None,
    ) -> CompositeConstruct:
        """Create a custom composition pattern."""
        if config is None:
            config = CompositionConfig(strategy=strategy)

        class CustomComposition(CompositeConstruct):
            def __init__(self):
                super().__init__(name, config)
                self.basic_constructs = basic_constructs

            def get_basic_constructs(self) -> List[str]:
                return self.basic_constructs

            def compose(self, *args, **kwargs) -> Any:
                from kinda.composition.framework import get_composition_engine

                engine = get_composition_engine()
                gates = []

                for construct_name in self.basic_constructs:
                    gate_func = globals().get(construct_name)
                    if gate_func is None:
                        # Try importing from kinda runtime
                        try:
                            from kinda.langs.python.runtime import fuzzy

                            gate_func = getattr(fuzzy, construct_name, None)
                        except ImportError:
                            pass

                    if gate_func is not None:
                        gates.append(gate_func)

                if not gates:
                    raise RuntimeError(f"No valid constructs found from {self.basic_constructs}")

                return engine._execute_strategy(strategy, gates, *args, **kwargs)

            def get_target_probabilities(self) -> Dict[str, float]:
                # Calculate based on basic construct probabilities
                from kinda.personality import get_personality, chaos_probability

                personality = get_personality()
                basic_probs = []
                for construct in self.basic_constructs:
                    prob = chaos_probability(construct.replace("_base", ""))
                    basic_probs.append(prob)

                composite_prob = PersonalityBridge.calculate_composite_probability(
                    basic_probs, strategy
                )

                return {personality.mood: composite_prob}

        return CustomComposition()


# Pre-defined composition patterns for common use cases


def create_sorta_pattern() -> UnionComposition:
    """Create the sorta pattern used in Task 1 (sometimes OR maybe)."""
    bridge_config = {
        "reliable": 0.0,  # No bridge needed for reliable
        "cautious": 0.0,  # No bridge needed for cautious
        "playful": 0.2,  # Bridge gap for playful personality
        "chaotic": 0.2,  # Bridge gap for chaotic personality
    }
    return CompositionPatternFactory.create_union_pattern(
        "sorta_composition", ["sometimes", "maybe"], bridge_config
    )


def create_ish_pattern() -> ToleranceComposition:
    """Create the ~ish tolerance pattern for Task 3."""
    return CompositionPatternFactory.create_tolerance_pattern(
        "ish_comparison", "kinda_float", "chaos_tolerance"
    )


def create_consensus_pattern(constructs: List[str], threshold: float = 0.6) -> ThresholdComposition:
    """Create a consensus pattern requiring majority agreement."""
    return CompositionPatternFactory.create_threshold_pattern(
        f"consensus_{len(constructs)}", constructs, threshold
    )


# Add to factory methods
def create_ish_comparison_pattern() -> IshToleranceComposition:
    """Create ~ish comparison composition pattern."""
    return IshToleranceComposition("ish_comparison_pattern", "comparison")


def create_ish_assignment_pattern() -> IshToleranceComposition:
    """Create ~ish assignment composition pattern."""
    return IshToleranceComposition("ish_assignment_pattern", "assignment")
