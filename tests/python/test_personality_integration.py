"""
Tests for personality/chaos integration system.

Ensures that different personality moods actually affect construct behavior.
"""

import pytest
import random
from pathlib import Path
from kinda.personality import (
    PersonalityContext,
    PERSONALITY_PROFILES,
    chaos_probability,
    chaos_fuzz_range,
    chaos_variance,
)
from kinda.cli import setup_personality


class TestPersonalityProfiles:
    """Test the personality profile system."""

    def test_personality_profiles_exist(self):
        """Ensure all expected personality profiles are defined."""
        expected_moods = {
            "reliable",
            "cautious",
            "playful",
            "chaotic",
            "professional",
            "friendly",
            "snarky",
        }
        assert set(PERSONALITY_PROFILES.keys()) == expected_moods

    def test_reliable_mood_settings(self):
        """Verify reliable mood has conservative settings."""
        profile = PERSONALITY_PROFILES["reliable"]

        # Reliable should have high success rates
        assert profile.sometimes_base >= 0.9
        assert profile.maybe_base >= 0.9
        assert profile.sorta_print_base >= 0.9

        # Minimal randomness
        assert profile.int_fuzz_range == (0, 0)
        assert profile.chaos_amplifier <= 0.5

    def test_chaotic_mood_settings(self):
        """Verify chaotic mood has extreme settings."""
        profile = PERSONALITY_PROFILES["chaotic"]

        # Chaotic should have lower success rates
        assert profile.sometimes_base <= 0.5
        assert profile.maybe_base <= 0.5

        # High randomness
        assert profile.int_fuzz_range[1] >= 3  # High fuzz range
        assert profile.chaos_amplifier >= 1.5
        assert profile.cascade_strength >= 0.3


class TestPersonalityContext:
    """Test the PersonalityContext singleton behavior."""

    def test_singleton_behavior(self):
        """Ensure PersonalityContext maintains singleton behavior."""
        ctx1 = PersonalityContext.get_instance()
        ctx2 = PersonalityContext.get_instance()
        assert ctx1 is ctx2

    def test_mood_setting(self):
        """Test setting different moods."""
        PersonalityContext.set_mood("reliable")
        ctx = PersonalityContext.get_instance()
        assert ctx.mood == "reliable"

        PersonalityContext.set_mood("chaotic")
        ctx = PersonalityContext.get_instance()
        assert ctx.mood == "chaotic"

    def test_chaos_probability_adjustment(self):
        """Test that different moods produce different probabilities."""
        # Test reliable mood
        PersonalityContext.set_mood("reliable")
        ctx = PersonalityContext.get_instance()
        reliable_prob = ctx.get_chaos_probability("sorta_print")

        # Test chaotic mood
        PersonalityContext.set_mood("chaotic")
        ctx = PersonalityContext.get_instance()
        chaotic_prob = ctx.get_chaos_probability("sorta_print")

        # Reliable should have higher print probability than chaotic
        assert reliable_prob > chaotic_prob

    def test_fuzz_range_adjustment(self):
        """Test that different moods produce different fuzz ranges."""
        # Test reliable mood (minimal fuzz)
        PersonalityContext.set_mood("reliable")
        ctx = PersonalityContext.get_instance()
        reliable_range = ctx.get_fuzz_range("int")

        # Test chaotic mood (high fuzz)
        PersonalityContext.set_mood("chaotic")
        ctx = PersonalityContext.get_instance()
        chaotic_range = ctx.get_fuzz_range("int")

        # Chaotic should have wider range than reliable
        chaotic_width = chaotic_range[1] - chaotic_range[0]
        reliable_width = reliable_range[1] - reliable_range[0]
        assert chaotic_width > reliable_width

    def test_instability_tracking(self):
        """Test that instability tracking works."""
        PersonalityContext.set_mood("playful")
        ctx = PersonalityContext.get_instance()
        ctx.instability_level = 0.0

        # Failed operation should increase instability
        ctx.update_instability(failed=True)
        assert ctx.instability_level > 0.0

        instability_after_failure = ctx.instability_level

        # Successful operation should decrease instability
        ctx.update_instability(failed=False)
        assert ctx.instability_level < instability_after_failure


class TestCLIIntegration:
    """Test CLI integration with personality system."""

    def test_setup_personality_with_valid_mood(self):
        """Test setup_personality with valid mood."""
        setup_personality("reliable")
        ctx = PersonalityContext.get_instance()
        assert ctx.mood == "reliable"

    def test_setup_personality_with_invalid_mood(self):
        """Test setup_personality handles invalid mood gracefully."""
        # This should default to 'playful' without crashing
        setup_personality("invalid_mood")
        ctx = PersonalityContext.get_instance()
        assert ctx.mood == "playful"  # Should fall back to default

    def test_setup_personality_with_none(self):
        """Test setup_personality with None defaults properly."""
        setup_personality(None)
        ctx = PersonalityContext.get_instance()
        assert ctx.mood == "playful"  # Should use default


class TestConstructIntegration:
    """Test that constructs properly use personality system."""

    def test_chaos_probability_function(self):
        """Test global chaos_probability function works."""
        PersonalityContext.set_mood("reliable")
        reliable_prob = chaos_probability("sorta_print")

        PersonalityContext.set_mood("chaotic")
        chaotic_prob = chaos_probability("sorta_print")

        assert reliable_prob != chaotic_prob
        assert 0.0 <= reliable_prob <= 1.0
        assert 0.0 <= chaotic_prob <= 1.0

    def test_chaos_fuzz_range_function(self):
        """Test global chaos_fuzz_range function works."""
        PersonalityContext.set_mood("reliable")
        reliable_range = chaos_fuzz_range("int")

        PersonalityContext.set_mood("chaotic")
        chaotic_range = chaos_fuzz_range("int")

        assert reliable_range != chaotic_range
        assert len(reliable_range) == 2
        assert len(chaotic_range) == 2

    def test_chaos_variance_function(self):
        """Test global chaos_variance function works."""
        PersonalityContext.set_mood("reliable")
        reliable_variance = chaos_variance()

        PersonalityContext.set_mood("chaotic")
        chaotic_variance = chaos_variance()

        assert reliable_variance != chaotic_variance
        assert chaotic_variance > reliable_variance


if __name__ == "__main__":
    pytest.main([__file__])
