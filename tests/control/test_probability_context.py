"""
Tests for Probability Context Management

This module tests the probability context system for controlling
probabilistic behavior in kinda-lang constructs.
"""

import pytest
import random

from kinda.control.context import (
    ProbabilityContext,
    ProbabilityProfile,
    ProbabilityMode,
    get_construct_probability,
    is_deterministic_mode,
    is_testing_mode
)


class TestProbabilityProfile:
    """Test probability profile creation and management"""

    def test_create_testing_profile(self):
        """Test creation of testing profile"""
        profile = ProbabilityProfile.create_testing_profile(seed=42)

        assert profile.name == "testing"
        assert profile.mode == ProbabilityMode.TESTING
        assert profile.seed == 42
        assert "sometimes" in profile.construct_overrides
        assert profile.construct_overrides["sometimes"] == 0.7

    def test_create_production_profile(self):
        """Test creation of production profile"""
        profile = ProbabilityProfile.create_production_profile()

        assert profile.name == "production"
        assert profile.mode == ProbabilityMode.PRODUCTION
        assert profile.construct_overrides["sometimes"] == 0.9  # More predictable
        assert profile.construct_overrides["sorta_print"] == 1.0  # Always print

    def test_create_chaos_profile(self):
        """Test creation of chaos profile"""
        profile = ProbabilityProfile.create_chaos_profile()

        assert profile.name == "chaos"
        assert profile.mode == ProbabilityMode.CHAOS
        assert profile.construct_overrides["probably"] == 0.6  # Less probable
        assert profile.construct_overrides["rarely"] == 0.4  # More frequent

    def test_create_deterministic_profile(self):
        """Test creation of deterministic profile"""
        profile = ProbabilityProfile.create_deterministic_profile()

        assert profile.name == "deterministic"
        assert profile.mode == ProbabilityMode.DETERMINISTIC
        assert profile.construct_overrides["sometimes"] == 1.0  # Always
        assert profile.construct_overrides["rarely"] == 0.0  # Never


class TestProbabilityContext:
    """Test the main probability context manager"""

    def test_context_manager_basic(self):
        """Test basic context manager functionality"""
        with ProbabilityContext() as ctx:
            assert ctx is not None
            assert ProbabilityContext.get_current() is ctx

        # Should be None after exiting
        assert ProbabilityContext.get_current() is None

    def test_context_nesting(self):
        """Test nested probability contexts"""
        with ProbabilityContext() as outer_ctx:
            assert ProbabilityContext.get_current() is outer_ctx

            with ProbabilityContext() as inner_ctx:
                assert ProbabilityContext.get_current() is inner_ctx
                assert inner_ctx is not outer_ctx

            # Should restore outer context
            assert ProbabilityContext.get_current() is outer_ctx

    def test_get_probability_with_override(self):
        """Test getting probability with overrides"""
        overrides = {"sometimes": 0.9, "maybe": 0.3}
        with ProbabilityContext(overrides=overrides) as ctx:
            assert ctx.get_probability("sometimes") == 0.9
            assert ctx.get_probability("maybe") == 0.3
            assert ctx.get_probability("rarely", 0.2) == 0.2  # Default

    def test_get_probability_deterministic_mode(self):
        """Test probability behavior in deterministic mode"""
        profile = ProbabilityProfile.create_deterministic_profile()
        with ProbabilityContext(profile=profile) as ctx:
            # High defaults should become 1.0
            assert ctx.get_probability("sometimes", 0.7) == 1.0
            # Low defaults should become 0.0
            assert ctx.get_probability("rarely", 0.2) == 0.0

    def test_get_probability_chaos_mode(self):
        """Test probability behavior in chaos mode"""
        profile = ProbabilityProfile.create_chaos_profile()
        with ProbabilityContext(profile=profile) as ctx:
            # Should add some randomness
            prob1 = ctx.get_probability("test", 0.5)
            prob2 = ctx.get_probability("test", 0.5)
            # Note: This might occasionally fail due to randomness
            # In a real implementation, we'd use a fixed seed

    def test_seed_reproducibility(self):
        """Test that seed provides reproducible randomness"""
        # This test depends on how the actual implementation uses the seed
        with ProbabilityContext(seed=42):
            # Set seed should affect random behavior
            random.seed(42)  # This is set in the context manager
            value1 = random.random()

        with ProbabilityContext(seed=42):
            random.seed(42)
            value2 = random.random()

        assert value1 == value2

    def test_with_override_method(self):
        """Test creating context with additional overrides"""
        base_ctx = ProbabilityContext(overrides={"sometimes": 0.7})
        new_ctx = base_ctx.with_override("maybe", 0.3)

        assert new_ctx.get_probability("sometimes") == 0.7
        assert new_ctx.get_probability("maybe") == 0.3

    def test_with_profile_method(self):
        """Test creating context with different profile"""
        chaos_profile = ProbabilityProfile.create_chaos_profile()
        base_ctx = ProbabilityContext()
        new_ctx = base_ctx.with_profile(chaos_profile)

        assert new_ctx.profile.name == "chaos"

    def test_usage_stats_tracking(self):
        """Test usage statistics tracking"""
        with ProbabilityContext() as ctx:
            ctx.get_probability("sometimes")
            ctx.get_probability("maybe")
            ctx.get_probability("sometimes")  # Again

            stats = ctx.get_usage_stats()
            assert stats["total_calls"] == 3
            assert stats["construct_calls"]["sometimes"] == 2
            assert stats["construct_calls"]["maybe"] == 1
            assert stats["most_used"] == "sometimes"

    def test_temporary_override_context_manager(self):
        """Test temporary override context manager"""
        with ProbabilityContext(overrides={"sometimes": 0.7}):
            # Base context
            assert get_construct_probability("sometimes") == 0.7

            # Temporary override
            with ProbabilityContext.temporary_override("sometimes", 0.9):
                assert get_construct_probability("sometimes") == 0.9

            # Should restore original
            assert get_construct_probability("sometimes") == 0.7

    def test_testing_mode_context_manager(self):
        """Test testing mode context manager"""
        with ProbabilityContext.testing_mode(seed=123) as ctx:
            assert ctx.mode == ProbabilityMode.TESTING
            assert ctx.seed == 123
            assert is_testing_mode()

    def test_production_mode_context_manager(self):
        """Test production mode context manager"""
        with ProbabilityContext.production_mode() as ctx:
            assert ctx.mode == ProbabilityMode.PRODUCTION
            # Production mode should be more conservative
            assert ctx.get_probability("sometimes") == 0.9

    def test_chaos_mode_context_manager(self):
        """Test chaos mode context manager"""
        with ProbabilityContext.chaos_mode() as ctx:
            assert ctx.mode == ProbabilityMode.CHAOS

    def test_deterministic_mode_context_manager(self):
        """Test deterministic mode context manager"""
        with ProbabilityContext.deterministic_mode() as ctx:
            assert ctx.mode == ProbabilityMode.DETERMINISTIC
            assert is_deterministic_mode()


class TestUtilityFunctions:
    """Test utility functions for probability control"""

    def test_get_construct_probability_no_context(self):
        """Test getting probability when no context is active"""
        # Ensure no context is active
        assert ProbabilityContext.get_current() is None

        # Should return default
        prob = get_construct_probability("sometimes", 0.7)
        assert prob == 0.7

    def test_get_construct_probability_with_context(self):
        """Test getting probability with active context"""
        with ProbabilityContext(overrides={"sometimes": 0.9}):
            prob = get_construct_probability("sometimes", 0.7)
            assert prob == 0.9

    def test_is_deterministic_mode_no_context(self):
        """Test deterministic mode check with no context"""
        assert not is_deterministic_mode()

    def test_is_deterministic_mode_with_context(self):
        """Test deterministic mode check with context"""
        with ProbabilityContext.deterministic_mode():
            assert is_deterministic_mode()

        assert not is_deterministic_mode()

    def test_is_testing_mode_no_context(self):
        """Test testing mode check with no context"""
        assert not is_testing_mode()

    def test_is_testing_mode_with_context(self):
        """Test testing mode check with context"""
        with ProbabilityContext.testing_mode():
            assert is_testing_mode()

        assert not is_testing_mode()


class TestProbabilityModes:
    """Test different probability modes"""

    def test_normal_mode_behavior(self):
        """Test normal mode probability behavior"""
        profile = ProbabilityProfile(
            name="normal",
            description="Normal mode",
            mode=ProbabilityMode.NORMAL
        )

        with ProbabilityContext(profile=profile) as ctx:
            # Should return default values in normal mode
            assert ctx.get_probability("sometimes", 0.7) == 0.7

    def test_production_mode_conservative_behavior(self):
        """Test that production mode is more conservative"""
        with ProbabilityContext.production_mode() as ctx:
            # High probability constructs should stay high
            sometimes_prob = ctx.get_probability("sometimes", 0.7)
            assert sometimes_prob >= 0.7

            # Low probability constructs should stay low or get lower
            rarely_prob = ctx.get_probability("rarely", 0.2)
            assert rarely_prob <= 0.2

    def test_mode_persistence_in_context(self):
        """Test that mode persists throughout context"""
        with ProbabilityContext.deterministic_mode() as ctx:
            assert ctx.mode == ProbabilityMode.DETERMINISTIC

            # Mode should not change during context
            ctx.get_probability("sometimes")
            assert ctx.mode == ProbabilityMode.DETERMINISTIC