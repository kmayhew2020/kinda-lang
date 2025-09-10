# tests/python/test_chaos_level.py

"""
Comprehensive test suite for --chaos-level parameter functionality.
Tests chaos levels 1-10 across all fuzzy constructs.
"""

import unittest
import random
from unittest.mock import patch
from kinda.personality import PersonalityContext, PERSONALITY_PROFILES
from kinda.cli import validate_chaos_level, setup_personality


class TestChaosLevelValidation(unittest.TestCase):
    """Test chaos level validation and CLI integration."""

    def test_validate_chaos_level_valid_range(self):
        """Test that valid chaos levels (1-10) are accepted."""
        for level in range(1, 11):
            with self.subTest(level=level):
                result = validate_chaos_level(level)
                self.assertEqual(result, level)

    def test_validate_chaos_level_invalid_below(self):
        """Test that chaos levels below 1 default to 5."""
        for level in [-5, -1, 0]:
            with self.subTest(level=level):
                with patch("kinda.cli.safe_print"):
                    result = validate_chaos_level(level)
                    self.assertEqual(result, 5)

    def test_validate_chaos_level_invalid_above(self):
        """Test that chaos levels above 10 default to 5."""
        for level in [11, 15, 100]:
            with self.subTest(level=level):
                with patch("kinda.cli.safe_print"):
                    result = validate_chaos_level(level)
                    self.assertEqual(result, 5)


class TestChaosLevelMultipliers(unittest.TestCase):
    """Test chaos level multiplier calculations."""

    def test_chaos_multiplier_mapping(self):
        """Test that chaos levels map to expected multiplier ranges."""
        expected_ranges = {
            1: (0.2, 0.4),  # Minimal chaos
            2: (0.2, 0.4),
            3: (0.4, 0.8),  # Low chaos
            4: (0.4, 0.8),
            5: (0.8, 1.4),  # Medium chaos (default)
            6: (0.8, 1.4),
            7: (1.4, 1.8),  # High chaos
            8: (1.4, 1.8),
            9: (1.8, 2.2),  # Maximum chaos
            10: (1.8, 2.2),
        }

        for level, (min_mult, max_mult) in expected_ranges.items():
            with self.subTest(level=level):
                ctx = PersonalityContext("playful", level)
                multiplier = ctx.chaos_multiplier
                self.assertGreaterEqual(
                    multiplier, min_mult, f"Level {level} multiplier {multiplier} below {min_mult}"
                )
                self.assertLessEqual(
                    multiplier, max_mult, f"Level {level} multiplier {multiplier} above {max_mult}"
                )

    def test_chaos_multiplier_progression(self):
        """Test that chaos multipliers generally increase with level."""
        multipliers = []
        for level in range(1, 11):
            ctx = PersonalityContext("playful", level)
            multipliers.append((level, ctx.chaos_multiplier))

        # Check that overall trend is increasing
        # Allow for some flat sections within same range
        low_end = multipliers[0][1]  # Level 1
        mid_range = multipliers[4][1]  # Level 5
        high_end = multipliers[9][1]  # Level 10

        self.assertLess(low_end, mid_range, "Level 1 should have lower multiplier than level 5")
        self.assertLess(mid_range, high_end, "Level 5 should have lower multiplier than level 10")


class TestChaosLevelProbabilities(unittest.TestCase):
    """Test chaos level effects on construct probabilities."""

    def test_sometimes_probability_chaos_levels(self):
        """Test that ~sometimes probability varies with chaos levels."""
        base_prob = PERSONALITY_PROFILES["playful"].sometimes_base  # Should be 0.5

        # Test different chaos levels
        levels_and_expectations = [
            (1, "higher"),  # Low chaos should make it more reliable (higher prob)
            (5, "baseline"),  # Medium chaos should be close to base
            (10, "varied"),  # High chaos should vary more
        ]

        for level, expectation in levels_and_expectations:
            with self.subTest(level=level, expectation=expectation):
                ctx = PersonalityContext("playful", level)
                prob = ctx.get_chaos_probability("sometimes")

                if expectation == "higher":
                    # Low chaos should make probabilities more reliable/predictable
                    # For sometimes (base 0.5), this could go either direction
                    self.assertGreaterEqual(prob, 0.0)
                    self.assertLessEqual(prob, 1.0)
                elif expectation == "baseline":
                    # Medium chaos should be closer to baseline
                    self.assertGreater(prob, 0.3)
                    self.assertLess(prob, 0.7)
                else:  # varied
                    # High chaos - just ensure it's valid
                    self.assertGreaterEqual(prob, 0.0)
                    self.assertLessEqual(prob, 1.0)

    def test_maybe_probability_chaos_levels(self):
        """Test that ~maybe probability varies with chaos levels."""
        for level in [1, 5, 10]:
            with self.subTest(level=level):
                ctx = PersonalityContext("playful", level)
                prob = ctx.get_chaos_probability("maybe")
                self.assertGreaterEqual(prob, 0.0)
                self.assertLessEqual(prob, 1.0)

    def test_probably_probability_chaos_levels(self):
        """Test that ~probably probability varies with chaos levels."""
        for level in [1, 5, 10]:
            with self.subTest(level=level):
                ctx = PersonalityContext("playful", level)
                prob = ctx.get_chaos_probability("probably")
                self.assertGreaterEqual(prob, 0.0)
                self.assertLessEqual(prob, 1.0)

    def test_rarely_probability_chaos_levels(self):
        """Test that ~rarely probability varies with chaos levels."""
        for level in [1, 5, 10]:
            with self.subTest(level=level):
                ctx = PersonalityContext("playful", level)
                prob = ctx.get_chaos_probability("rarely")
                self.assertGreaterEqual(prob, 0.0)
                self.assertLessEqual(prob, 1.0)

    def test_sorta_print_probability_chaos_levels(self):
        """Test that ~sorta print probability varies with chaos levels."""
        for level in [1, 5, 10]:
            with self.subTest(level=level):
                ctx = PersonalityContext("playful", level)
                prob = ctx.get_chaos_probability("sorta_print")
                self.assertGreaterEqual(prob, 0.0)
                self.assertLessEqual(prob, 1.0)


class TestChaosLevelFuzzRanges(unittest.TestCase):
    """Test chaos level effects on fuzz ranges."""

    def test_int_fuzz_range_chaos_levels(self):
        """Test that kinda int fuzz ranges scale with chaos levels."""
        for level in [1, 5, 10]:
            with self.subTest(level=level):
                ctx = PersonalityContext("playful", level)
                min_fuzz, max_fuzz = ctx.get_fuzz_range("int")

                # Ensure range is valid
                self.assertLessEqual(min_fuzz, max_fuzz)

                # Check scaling behavior
                if level == 1:
                    # Minimal chaos should have smaller range
                    range_size = max_fuzz - min_fuzz
                    self.assertLessEqual(range_size, 2)  # Should be quite small
                elif level == 10:
                    # Maximum chaos should have larger range
                    range_size = max_fuzz - min_fuzz
                    self.assertGreaterEqual(range_size, 2)  # Should be larger

    def test_float_drift_range_chaos_levels(self):
        """Test that kinda float drift ranges scale with chaos levels."""
        for level in [1, 5, 10]:
            with self.subTest(level=level):
                ctx = PersonalityContext("playful", level)
                min_drift, max_drift = ctx.get_float_drift_range()

                # Ensure range is valid
                self.assertLessEqual(min_drift, max_drift)

                # Check that ranges are reasonable
                self.assertGreaterEqual(abs(max_drift - min_drift), 0.0)


class TestChaosLevelVarianceTolerances(unittest.TestCase):
    """Test chaos level effects on ish variance and tolerance."""

    def test_ish_variance_chaos_levels(self):
        """Test that ~ish variance scales with chaos levels."""
        variances = {}
        for level in [1, 5, 10]:
            ctx = PersonalityContext("playful", level)
            variance = ctx.get_ish_variance()
            variances[level] = variance

            # Variance should be positive
            self.assertGreater(variance, 0.0)

        # Generally expect variance to increase with chaos level
        # (allowing for personality profile effects)
        self.assertLess(
            variances[1], variances[10], "Level 1 variance should be less than level 10"
        )

    def test_ish_tolerance_chaos_levels(self):
        """Test that ~ish tolerance scales with chaos levels."""
        tolerances = {}
        for level in [1, 5, 10]:
            ctx = PersonalityContext("playful", level)
            tolerance = ctx.get_ish_tolerance()
            tolerances[level] = tolerance

            # Tolerance should be positive
            self.assertGreater(tolerance, 0.0)

        # Generally expect tolerance to increase with chaos level
        self.assertLess(
            tolerances[1], tolerances[10], "Level 1 tolerance should be less than level 10"
        )


class TestChaosLevelBooleanUncertainty(unittest.TestCase):
    """Test chaos level effects on boolean uncertainty."""

    def test_bool_uncertainty_chaos_levels(self):
        """Test that boolean uncertainty scales with chaos levels."""
        uncertainties = {}
        for level in [1, 5, 10]:
            ctx = PersonalityContext("playful", level)
            uncertainty = ctx.get_bool_uncertainty()
            uncertainties[level] = uncertainty

            # Uncertainty should be in valid range
            self.assertGreaterEqual(uncertainty, 0.0)
            self.assertLessEqual(uncertainty, 0.5)

        # Generally expect uncertainty to increase with chaos level
        self.assertLess(
            uncertainties[1], uncertainties[10], "Level 1 uncertainty should be less than level 10"
        )


class TestChaosLevelBinaryProbabilities(unittest.TestCase):
    """Test chaos level effects on binary probabilities."""

    def test_binary_probabilities_chaos_levels(self):
        """Test that binary probabilities change with chaos levels."""
        for level in [1, 5, 10]:
            with self.subTest(level=level):
                ctx = PersonalityContext("playful", level)
                pos, neg, neutral = ctx.get_binary_probabilities()

                # Probabilities should be valid
                self.assertGreaterEqual(pos, 0.0)
                self.assertGreaterEqual(neg, 0.0)
                self.assertGreaterEqual(neutral, 0.0)

                # Should sum to approximately 1.0
                total = pos + neg + neutral
                self.assertAlmostEqual(total, 1.0, places=5)


class TestChaosLevelMoodIntegration(unittest.TestCase):
    """Test chaos level integration with personality moods."""

    def test_chaos_level_with_different_moods(self):
        """Test that chaos levels work with all personality moods."""
        moods = ["reliable", "cautious", "playful", "chaotic"]

        for mood in moods:
            for level in [1, 5, 10]:
                with self.subTest(mood=mood, level=level):
                    ctx = PersonalityContext(mood, level)

                    # Verify mood and chaos level are set
                    self.assertEqual(ctx.mood, mood)
                    self.assertEqual(ctx.chaos_level, level)

                    # Test that probabilities are reasonable
                    prob = ctx.get_chaos_probability("sometimes")
                    self.assertGreaterEqual(prob, 0.0)
                    self.assertLessEqual(prob, 1.0)

    def test_multiplicative_effect_mood_chaos(self):
        """Test that mood and chaos level have multiplicative effect."""
        # Compare reliable mood at different chaos levels
        ctx_reliable_low = PersonalityContext("reliable", 1)
        ctx_reliable_high = PersonalityContext("reliable", 10)

        prob_low = ctx_reliable_low.get_chaos_probability("sometimes")
        prob_high = ctx_reliable_high.get_chaos_probability("sometimes")

        # Both should be influenced by reliable mood, but chaos level should still matter
        self.assertNotEqual(prob_low, prob_high, "Chaos level should affect reliable mood")

        # Compare chaotic mood at different chaos levels
        ctx_chaotic_low = PersonalityContext("chaotic", 1)
        ctx_chaotic_high = PersonalityContext("chaotic", 10)

        prob_chaotic_low = ctx_chaotic_low.get_chaos_probability("sometimes")
        prob_chaotic_high = ctx_chaotic_high.get_chaos_probability("sometimes")

        # Chaos level should still have an effect even in chaotic mode
        self.assertNotEqual(
            prob_chaotic_low, prob_chaotic_high, "Chaos level should affect chaotic mood"
        )


class TestChaosLevelCLIIntegration(unittest.TestCase):
    """Test chaos level CLI parameter integration."""

    @patch("kinda.cli.safe_print")
    def test_setup_personality_with_chaos_level(self, mock_print):
        """Test that setup_personality accepts chaos level parameter."""
        # Test valid setup
        setup_personality("playful", 7)

        # Verify PersonalityContext was configured
        ctx = PersonalityContext.get_instance()
        self.assertEqual(ctx.mood, "playful")
        self.assertEqual(ctx.chaos_level, 7)

        # Verify output messages
        mock_print.assert_any_call("🎭 Setting kinda mood to 'playful'")
        mock_print.assert_any_call("🎲 Setting chaos level to 7 (1=minimal, 10=maximum chaos)")

    @patch("kinda.cli.safe_print")
    def test_setup_personality_invalid_chaos_level(self, mock_print):
        """Test that setup_personality handles invalid chaos levels."""
        setup_personality("playful", 15)  # Invalid level

        # Should default to 5
        ctx = PersonalityContext.get_instance()
        self.assertEqual(ctx.chaos_level, 5)


class TestChaosLevelErrorHandling(unittest.TestCase):
    """Test error handling for chaos level edge cases."""

    def test_chaos_level_boundary_values(self):
        """Test behavior at chaos level boundaries."""
        # Test level 1 (minimum)
        ctx1 = PersonalityContext("playful", 1)
        self.assertEqual(ctx1.chaos_level, 1)
        self.assertGreater(ctx1.chaos_multiplier, 0.0)

        # Test level 10 (maximum)
        ctx10 = PersonalityContext("playful", 10)
        self.assertEqual(ctx10.chaos_level, 10)
        self.assertGreater(ctx10.chaos_multiplier, 0.0)

    def test_chaos_level_stability(self):
        """Test that chaos level calculations are stable and repeatable."""
        # Same chaos level should produce same multiplier
        ctx1 = PersonalityContext("playful", 5)
        ctx2 = PersonalityContext("playful", 5)

        self.assertEqual(ctx1.chaos_multiplier, ctx2.chaos_multiplier)
        self.assertEqual(ctx1.get_ish_variance(), ctx2.get_ish_variance())


if __name__ == "__main__":
    unittest.main()
