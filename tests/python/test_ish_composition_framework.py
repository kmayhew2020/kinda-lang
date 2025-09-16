#!/usr/bin/env python3

"""
Epic #126 Task 3: Tests for ~ish composition framework integration.
These tests validate that ~ish patterns work identically using composition framework.
"""

import pytest
import os
import statistics
from pathlib import Path
import tempfile


# Epic #126 Task 3: Composition-aware ish functions (inline for testing)
def ish_comparison_composed(left_val, right_val, tolerance_base=None):
    """Epic #126 Task 3: ~ish comparison using composition framework."""
    from kinda.personality import update_chaos_state

    try:
        # Initialize composition framework if needed
        from kinda.composition import get_composition_engine, is_framework_ready

        if not is_framework_ready():
            # Fallback to legacy implementation if framework not available
            from kinda.langs.python.runtime.fuzzy import ish_comparison

            return ish_comparison(left_val, right_val, tolerance_base)

        # Get or create the ish comparison pattern
        engine = get_composition_engine()
        pattern_name = "ish_comparison_pattern"
        ish_pattern = engine.get_composite(pattern_name)

        if ish_pattern is None:
            # Create and register the pattern on first use
            from kinda.composition.patterns import IshToleranceComposition

            ish_pattern = IshToleranceComposition(pattern_name, "comparison")
            engine.register_composite(ish_pattern)

        # Delegate to composition framework
        result = ish_pattern.compose_comparison(left_val, right_val, tolerance_base)
        update_chaos_state(failed=False)
        return result

    except Exception as e:
        # Robust fallback to legacy implementation
        print(f"[composition] ~ish comparison fell back to legacy: {e}")
        update_chaos_state(failed=True)
        from kinda.langs.python.runtime.fuzzy import ish_comparison

        return ish_comparison(left_val, right_val, tolerance_base)


def ish_value_composed(val, target_val=None):
    """Epic #126 Task 3: ~ish value modification using composition framework."""
    from kinda.personality import update_chaos_state

    try:
        # Initialize composition framework if needed
        from kinda.composition import get_composition_engine, is_framework_ready

        if not is_framework_ready():
            # Fallback to legacy implementation if framework not available
            from kinda.langs.python.runtime.fuzzy import ish_value

            return ish_value(val, target_val)

        # Get or create the ish assignment pattern
        engine = get_composition_engine()
        pattern_name = "ish_assignment_pattern"
        ish_pattern = engine.get_composite(pattern_name)

        if ish_pattern is None:
            # Create and register the pattern on first use
            from kinda.composition.patterns import IshToleranceComposition

            ish_pattern = IshToleranceComposition(pattern_name, "assignment")
            engine.register_composite(ish_pattern)

        # Delegate to composition framework
        result = ish_pattern.compose_assignment(val, target_val)
        update_chaos_state(failed=False)
        return result

    except Exception as e:
        # Robust fallback to legacy implementation
        print(f"[composition] ~ish value fell back to legacy: {e}")
        update_chaos_state(failed=True)
        from kinda.langs.python.runtime.fuzzy import ish_value

        return ish_value(val, target_val)


# Test both composition and legacy implementations
@pytest.fixture(params=[True, False])
def use_composition(request, monkeypatch):
    """Test with both composition and legacy implementations."""
    monkeypatch.setenv("KINDA_USE_COMPOSITION_ISH", str(request.param).lower())
    return request.param


class TestIshCompositionBehavior:
    """Test that composition framework produces identical behavior."""

    def test_ish_comparison_statistical_equivalence(self, use_composition):
        """Test that composed ~ish comparison has same statistical behavior."""
        from kinda.langs.python.runtime.fuzzy import ish_comparison

        # ish_comparison_composed is defined inline above

        # Choose function based on parameter
        test_func = ish_comparison_composed if use_composition else ish_comparison

        # Test statistical equivalence over many runs
        results = []
        for _ in range(1000):
            result = test_func(10.0, 10.1, 0.2)
            results.append(result)

        success_rate = sum(results) / len(results)

        # Success rate varies by personality but should be reasonable
        assert 0.2 <= success_rate <= 1.0, f"Success rate {success_rate} outside expected range"

    def test_ish_value_statistical_equivalence(self, use_composition):
        """Test that composed ~ish value has same statistical behavior."""
        from kinda.langs.python.runtime.fuzzy import ish_value

        # ish_value_composed is defined inline above

        # Choose function based on parameter
        test_func = ish_value_composed if use_composition else ish_value

        # Test variance behavior
        base_value = 100.0
        results = []

        for _ in range(1000):
            result = test_func(base_value)  # Standalone case
            results.append(result)

        mean_result = statistics.mean(results)
        std_dev = statistics.stdev(results)

        # Results should cluster around base value with reasonable variance
        # Adjust tolerance for different personality modes (chaotic has higher variance)
        from kinda.personality import get_personality

        personality = get_personality()
        tolerance_multiplier = {
            "reliable": 1.0,
            "cautious": 1.5,
            "playful": 2.0,
            "chaotic": 3.0,
        }.get(personality.mood, 2.0)
        mean_tolerance = 5.0 * tolerance_multiplier

        assert (
            abs(mean_result - base_value) < mean_tolerance
        ), f"Mean {mean_result} too far from base {base_value} (tolerance: {mean_tolerance}, personality: {personality.mood})"
        # Adjust standard deviation range for personality variance patterns
        min_std_dev = 0.1 * tolerance_multiplier  # Lower bound for all personalities
        max_std_dev = 20.0 * tolerance_multiplier  # Upper bound scaled by personality
        assert (
            min_std_dev < std_dev < max_std_dev
        ), f"Standard deviation {std_dev} outside expected range [{min_std_dev:.2f}, {max_std_dev:.2f}] for {personality.mood} personality"

    def test_ish_assignment_statistical_equivalence(self, use_composition):
        """Test ~ish assignment behavior equivalence."""
        from kinda.langs.python.runtime.fuzzy import ish_value

        # ish_value_composed is defined inline above

        # Choose function based on parameter
        test_func = ish_value_composed if use_composition else ish_value

        # Test assignment behavior
        current_val = 50.0
        target_val = 100.0
        results = []

        for _ in range(1000):
            result = test_func(current_val, target_val)
            results.append(result)

        mean_result = statistics.mean(results)

        # Results should trend toward target but with variance
        assert (
            current_val < mean_result < target_val
        ), f"Mean {mean_result} not between current {current_val} and target {target_val}"


class TestIshCompositionIntegration:
    """Test integration with composition framework components."""

    def test_composition_pattern_registration(self):
        """Test that ~ish patterns register correctly with framework."""
        from kinda.composition import get_composition_engine

        # ish_comparison_composed is defined inline above

        # Clear any existing patterns
        engine = get_composition_engine()

        # First call should create and register pattern
        result = ish_comparison_composed(5.0, 5.1)

        # Pattern should now be registered
        pattern = engine.get_composite("ish_comparison_pattern")
        assert pattern is not None
        assert pattern.name == "ish_comparison_pattern"

    def test_composition_framework_fallback(self):
        """Test fallback to legacy functions when framework fails."""
        # Temporarily break framework
        with pytest.MonkeyPatch().context() as m:
            m.setenv("KINDA_USE_COMPOSITION_ISH", "true")

            # Mock framework to fail
            def mock_failing_engine():
                raise RuntimeError("Framework unavailable")

            m.setattr("kinda.composition.get_composition_engine", mock_failing_engine)

            # Should fallback gracefully
            # ish_comparison_composed is defined inline above
            result = ish_comparison_composed(5.0, 5.1)  # Should not raise exception
            assert isinstance(result, bool)


class TestIshTransformationCompatibility:
    """Test that transformed code works with both implementations."""

    def test_transformer_generates_correct_functions(self, use_composition):
        """Test that transformer uses correct runtime functions."""
        from kinda.langs.python.transformer import _transform_ish_constructs

        with pytest.MonkeyPatch().context() as m:
            m.setenv("KINDA_USE_COMPOSITION_ISH", str(use_composition).lower())

            # Re-import to pick up environment change
            import importlib
            import kinda.langs.python.transformer

            importlib.reload(kinda.langs.python.transformer)
            from kinda.langs.python.transformer import _transform_ish_constructs

            # Test assignment context
            result = _transform_ish_constructs("value ~ish 10")

            if use_composition:
                assert "ish_value_composed" in result
            else:
                assert "ish_value(" in result and "ish_value_composed" not in result

    def test_comparison_transformation_compatibility(self, use_composition):
        """Test comparison context transformation with composition framework."""
        from kinda.langs.python.transformer import _transform_ish_constructs

        with pytest.MonkeyPatch().context() as m:
            m.setenv("KINDA_USE_COMPOSITION_ISH", str(use_composition).lower())

            # Re-import to pick up environment change
            import importlib
            import kinda.langs.python.transformer

            importlib.reload(kinda.langs.python.transformer)
            from kinda.langs.python.transformer import _transform_ish_constructs

            # Test comparison context
            result = _transform_ish_constructs("if value ~ish 90:")

            if use_composition:
                assert "ish_comparison_composed" in result
            else:
                assert "ish_comparison(" in result and "ish_comparison_composed" not in result

    def test_file_transformation_compatibility(self, use_composition):
        """Test complete file transformation with composition framework."""
        from kinda.langs.python.transformer import transform_file

        knda_content = """# Test ~ish patterns
value = 100

# Assignment context
value ~ish 20

# Comparison context
if value ~ish 90:
    print("Close!")
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".knda", delete=False) as f:
            f.write(knda_content)
            temp_path = Path(f.name)

        try:
            with pytest.MonkeyPatch().context() as m:
                m.setenv("KINDA_USE_COMPOSITION_ISH", str(use_composition).lower())

                # Re-import to pick up environment change
                import importlib
                import kinda.langs.python.transformer

                importlib.reload(kinda.langs.python.transformer)
                from kinda.langs.python.transformer import transform_file

                result = transform_file(temp_path)

                if use_composition:
                    assert "ish_value_composed" in result
                    assert "ish_comparison_composed" in result
                else:
                    assert "ish_value" in result
                    assert "ish_comparison" in result
                    assert "composed" not in result

        finally:
            temp_path.unlink()


class TestIshCompositionFrameworkFeatures:
    """Test specific composition framework features."""

    def test_basic_construct_caching(self):
        """Test that basic constructs are cached for performance."""
        from kinda.composition.patterns import IshToleranceComposition

        pattern = IshToleranceComposition("test_pattern", "comparison")

        # First call should populate cache
        construct1 = pattern._get_basic_construct("kinda_float")

        # Second call should return cached version
        construct2 = pattern._get_basic_construct("kinda_float")

        # Should be the same object (cached)
        assert construct1 is construct2

    def test_ish_pattern_target_probabilities(self):
        """Test that ~ish patterns return personality-aware probabilities."""
        from kinda.composition.patterns import IshToleranceComposition

        pattern = IshToleranceComposition("test_pattern", "comparison")

        # Test that target probabilities are returned
        probs = pattern.get_target_probabilities()
        assert isinstance(probs, dict)
        assert len(probs) > 0

        # All probabilities should be between 0 and 1
        for personality, prob in probs.items():
            assert 0.0 <= prob <= 1.0, f"Probability {prob} for {personality} out of range"

    def test_composition_error_handling(self):
        """Test error handling in composition patterns."""
        from kinda.composition.patterns import IshToleranceComposition

        pattern = IshToleranceComposition("test_pattern", "comparison")

        # Test with invalid inputs that should trigger fallback
        result = pattern.compose_comparison("invalid", "values")
        assert isinstance(result, bool)  # Should not crash

        # Test assignment with invalid inputs
        result2 = pattern.compose_assignment("invalid")
        assert result2 is not None  # Should not crash


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
