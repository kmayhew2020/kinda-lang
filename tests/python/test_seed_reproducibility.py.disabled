#!/usr/bin/env python3
"""
Tests for seed functionality and reproducible chaos
Following both meta-programming philosophies:
1. "KINDA TESTS KINDA": Using existing constructs to test seed functionality
2. "KINDA BUILDS KINDA": Using kinda constructs in the test development process
"""

import unittest
import os
import sys
from pathlib import Path
from unittest.mock import patch

# Add the kinda package to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from kinda.personality import PersonalityContext, get_personality, get_seed_info
from kinda.personality import chaos_random, chaos_randint, chaos_uniform, chaos_choice
from kinda.langs.python.runtime.fuzzy import (
    kinda_int,
    kinda_float,
    kinda_bool,
    kinda_binary,
    sometimes,
    maybe,
    probably,
    rarely,
    sorta_print,
    ish_value,
    ish_comparison,
)


class TestSeedReproducibility(unittest.TestCase):
    """Test seed functionality for reproducible chaos"""

    def setUp(self):
        """Reset personality context before each test"""
        PersonalityContext._instance = None

    def tearDown(self):
        """Clean up after each test"""
        PersonalityContext._instance = None

    def test_seed_initialization_cli_arg(self):
        """Test seed initialization from CLI argument"""
        # Test with CLI seed value
        personality = PersonalityContext("playful", 5, seed=42)
        self.assertEqual(personality.seed, 42)
        self.assertIsNotNone(personality.rng)

        seed_info = personality.get_seed_info()
        self.assertEqual(seed_info["seed"], 42)
        self.assertTrue(seed_info["has_seed"])
        self.assertTrue(seed_info["reproducible"])

    def test_seed_initialization_no_seed(self):
        """Test initialization without seed (non-reproducible)"""
        personality = PersonalityContext("playful", 5, seed=None)
        self.assertIsNone(personality.seed)
        self.assertIsNotNone(personality.rng)  # Should still have RNG with None seed

        seed_info = personality.get_seed_info()
        self.assertIsNone(seed_info["seed"])
        self.assertFalse(seed_info["has_seed"])
        self.assertFalse(seed_info["reproducible"])

    def test_centralized_rng_reproducibility(self):
        """Test that centralized RNG produces identical sequences with same seed"""
        # First run with seed 123
        PersonalityContext._instance = PersonalityContext("playful", 5, seed=123)
        sequence1 = []
        for _ in range(10):
            sequence1.append(chaos_random())

        # Second run with same seed
        PersonalityContext._instance = PersonalityContext("playful", 5, seed=123)
        sequence2 = []
        for _ in range(10):
            sequence2.append(chaos_random())

        # Should be identical
        self.assertEqual(sequence1, sequence2)

    def test_centralized_rng_different_seeds(self):
        """Test that different seeds produce different sequences"""
        # First run with seed 123
        PersonalityContext._instance = PersonalityContext("playful", 5, seed=123)
        sequence1 = []
        for _ in range(10):
            sequence1.append(chaos_random())

        # Second run with seed 456
        PersonalityContext._instance = PersonalityContext("playful", 5, seed=456)
        sequence2 = []
        for _ in range(10):
            sequence2.append(chaos_random())

        # Should be different
        self.assertNotEqual(sequence1, sequence2)

    def test_kinda_int_reproducibility(self):
        """Test that ~kinda int produces identical results with same seed"""
        # First run with seed 42
        PersonalityContext._instance = PersonalityContext("playful", 5, seed=42)
        results1 = []
        for i in range(10):
            results1.append(kinda_int(i * 10))

        # Second run with same seed
        PersonalityContext._instance = PersonalityContext("playful", 5, seed=42)
        results2 = []
        for i in range(10):
            results2.append(kinda_int(i * 10))

        # Should be identical
        self.assertEqual(results1, results2)

    def test_kinda_float_reproducibility(self):
        """Test that ~kinda float produces identical results with same seed"""
        # First run with seed 99
        PersonalityContext._instance = PersonalityContext("playful", 5, seed=99)
        results1 = []
        for i in range(10):
            results1.append(kinda_float(i * 3.14))

        # Second run with same seed
        PersonalityContext._instance = PersonalityContext("playful", 5, seed=99)
        results2 = []
        for i in range(10):
            results2.append(kinda_float(i * 3.14))

        # Should be identical
        self.assertEqual(results1, results2)

    def test_sometimes_reproducibility(self):
        """Test that ~sometimes produces identical results with same seed"""
        # First run with seed 777
        PersonalityContext._instance = PersonalityContext("playful", 5, seed=777)
        results1 = []
        for i in range(20):
            results1.append(sometimes(True))  # Always true condition

        # Second run with same seed
        PersonalityContext._instance = PersonalityContext("playful", 5, seed=777)
        results2 = []
        for i in range(20):
            results2.append(sometimes(True))

        # Should be identical
        self.assertEqual(results1, results2)

    def test_maybe_reproducibility(self):
        """Test that ~maybe produces identical results with same seed"""
        # First run with seed 888
        PersonalityContext._instance = PersonalityContext("playful", 5, seed=888)
        results1 = []
        for i in range(20):
            results1.append(maybe(True))  # Always true condition

        # Second run with same seed
        PersonalityContext._instance = PersonalityContext("playful", 5, seed=888)
        results2 = []
        for i in range(20):
            results2.append(maybe(True))

        # Should be identical
        self.assertEqual(results1, results2)

    def test_kinda_binary_reproducibility(self):
        """Test that ~kinda binary produces identical results with same seed"""
        # First run with seed 333
        PersonalityContext._instance = PersonalityContext("playful", 5, seed=333)
        results1 = []
        for i in range(20):
            results1.append(kinda_binary())

        # Second run with same seed
        PersonalityContext._instance = PersonalityContext("playful", 5, seed=333)
        results2 = []
        for i in range(20):
            results2.append(kinda_binary())

        # Should be identical
        self.assertEqual(results1, results2)

    def test_ish_value_reproducibility(self):
        """Test that ~ish values produce identical results with same seed"""
        # First run with seed 111
        PersonalityContext._instance = PersonalityContext("playful", 5, seed=111)
        results1 = []
        for i in range(10):
            results1.append(ish_value(i * 5, variance=2.0))

        # Second run with same seed
        PersonalityContext._instance = PersonalityContext("playful", 5, seed=111)
        results2 = []
        for i in range(10):
            results2.append(ish_value(i * 5, variance=2.0))

        # Should be identical
        self.assertEqual(results1, results2)

    def test_mixed_constructs_reproducibility(self):
        """Test that mixed kinda constructs produce identical results with same seed"""
        # First run with seed 555
        PersonalityContext._instance = PersonalityContext("playful", 5, seed=555)
        results1 = []
        for i in range(5):
            results1.append(
                {
                    "int": kinda_int(i * 10),
                    "float": kinda_float(i * 2.5),
                    "binary": kinda_binary(),
                    "sometimes": sometimes(True),
                    "maybe": maybe(i > 2),
                    "ish": ish_value(i * 3, variance=1.0),
                }
            )

        # Second run with same seed
        PersonalityContext._instance = PersonalityContext("playful", 5, seed=555)
        results2 = []
        for i in range(5):
            results2.append(
                {
                    "int": kinda_int(i * 10),
                    "float": kinda_float(i * 2.5),
                    "binary": kinda_binary(),
                    "sometimes": sometimes(True),
                    "maybe": maybe(i > 2),
                    "ish": ish_value(i * 3, variance=1.0),
                }
            )

        # Should be identical
        self.assertEqual(results1, results2)

    def test_seed_with_different_moods(self):
        """Test that same seed works across different personality moods"""
        # Reliable mood with seed 1234
        PersonalityContext._instance = PersonalityContext("reliable", 5, seed=1234)
        reliable_results = []
        for i in range(5):
            reliable_results.append(kinda_int(10))

        # Chaotic mood with same seed
        PersonalityContext._instance = PersonalityContext("chaotic", 5, seed=1234)
        chaotic_results = []
        for i in range(5):
            chaotic_results.append(kinda_int(10))

        # Results should be deterministic within each mood but different between moods
        # (because personality affects the chaos multiplier and ranges)
        # The key is that each run with the same seed+mood should be identical

        # Test reliable mood reproducibility
        PersonalityContext._instance = PersonalityContext("reliable", 5, seed=1234)
        reliable_results2 = []
        for i in range(5):
            reliable_results2.append(kinda_int(10))
        self.assertEqual(reliable_results, reliable_results2)

        # Test chaotic mood reproducibility
        PersonalityContext._instance = PersonalityContext("chaotic", 5, seed=1234)
        chaotic_results2 = []
        for i in range(5):
            chaotic_results2.append(kinda_int(10))
        self.assertEqual(chaotic_results, chaotic_results2)

    def test_seed_with_different_chaos_levels(self):
        """Test that same seed works across different chaos levels"""
        # Low chaos (level 2) with seed 9999
        PersonalityContext._instance = PersonalityContext("playful", 2, seed=9999)
        low_chaos_results = []
        for i in range(5):
            low_chaos_results.append(kinda_float(5.0))

        # High chaos (level 8) with same seed
        PersonalityContext._instance = PersonalityContext("playful", 8, seed=9999)
        high_chaos_results = []
        for i in range(5):
            high_chaos_results.append(kinda_float(5.0))

        # Results should be deterministic within each chaos level
        # Test low chaos reproducibility
        PersonalityContext._instance = PersonalityContext("playful", 2, seed=9999)
        low_chaos_results2 = []
        for i in range(5):
            low_chaos_results2.append(kinda_float(5.0))
        self.assertEqual(low_chaos_results, low_chaos_results2)

        # Test high chaos reproducibility
        PersonalityContext._instance = PersonalityContext("playful", 8, seed=9999)
        high_chaos_results2 = []
        for i in range(5):
            high_chaos_results2.append(kinda_float(5.0))
        self.assertEqual(high_chaos_results, high_chaos_results2)

    def test_global_seed_info_function(self):
        """Test the global get_seed_info() convenience function"""
        PersonalityContext._instance = PersonalityContext("playful", 5, seed=12345)

        seed_info = get_seed_info()
        self.assertEqual(seed_info["seed"], 12345)
        self.assertTrue(seed_info["has_seed"])
        self.assertTrue(seed_info["reproducible"])

    def test_sorta_print_reproducibility_capture(self):
        """Test that sorta_print behavior is reproducible (capture output)"""
        # Note: This test captures print output to verify reproducibility
        from io import StringIO
        from contextlib import redirect_stdout

        # First run with seed 2468
        PersonalityContext._instance = PersonalityContext("playful", 5, seed=2468)
        output1 = StringIO()
        with redirect_stdout(output1):
            for i in range(5):
                sorta_print(f"Test message {i}")
        result1 = output1.getvalue()

        # Second run with same seed
        PersonalityContext._instance = PersonalityContext("playful", 5, seed=2468)
        output2 = StringIO()
        with redirect_stdout(output2):
            for i in range(5):
                sorta_print(f"Test message {i}")
        result2 = output2.getvalue()

        # Should be identical
        self.assertEqual(result1, result2)

    def test_kinda_tests_kinda_philosophy(self):
        """
        KINDA TESTS KINDA: Use existing kinda constructs to test seed functionality
        This test demonstrates the meta-programming philosophy by using kinda constructs
        in the testing process itself.
        """
        # Set up reproducible environment
        PersonalityContext._instance = PersonalityContext("playful", 5, seed=314159)

        # Use ~sometimes to decide which tests to run (but make it deterministic)
        test_cases = []

        # ~sometimes will be deterministic with the seed, so we can rely on it
        if sometimes(True):  # This will be deterministic
            test_cases.append("int_test")
        if maybe(True):  # This will also be deterministic
            test_cases.append("float_test")
        if probably(True):  # This too
            test_cases.append("binary_test")

        # The test cases selected should be consistent across runs
        # Reset and run again to verify
        PersonalityContext._instance = PersonalityContext("playful", 5, seed=314159)
        test_cases_repeat = []

        if sometimes(True):
            test_cases_repeat.append("int_test")
        if maybe(True):
            test_cases_repeat.append("float_test")
        if probably(True):
            test_cases_repeat.append("binary_test")

        # Should be identical (KINDA TESTS KINDA in action!)
        self.assertEqual(test_cases, test_cases_repeat)

        # Now run the actual tests based on what ~sometimes/~maybe/~probably decided
        results = {}
        PersonalityContext._instance = PersonalityContext("playful", 5, seed=314159)

        if "int_test" in test_cases:
            results["int"] = kinda_int(42)
        if "float_test" in test_cases:
            results["float"] = kinda_float(3.14)
        if "binary_test" in test_cases:
            results["binary"] = kinda_binary()

        # Verify reproducibility of the selected tests
        results_repeat = {}
        PersonalityContext._instance = PersonalityContext("playful", 5, seed=314159)

        # Skip the sometimes/maybe/probably checks since we know what was selected
        if "int_test" in test_cases:
            results_repeat["int"] = kinda_int(42)
        if "float_test" in test_cases:
            results_repeat["float"] = kinda_float(3.14)
        if "binary_test" in test_cases:
            results_repeat["binary"] = kinda_binary()

        self.assertEqual(results, results_repeat)

    def test_no_seed_non_reproducible(self):
        """Test that without a seed, results are non-reproducible"""
        # First run without seed
        PersonalityContext._instance = PersonalityContext("playful", 5, seed=None)
        results1 = []
        for i in range(10):
            results1.append(kinda_int(10))

        # Second run without seed
        PersonalityContext._instance = PersonalityContext("playful", 5, seed=None)
        results2 = []
        for i in range(10):
            results2.append(kinda_int(10))

        # Results should likely be different (though there's a tiny chance they could match)
        # We'll run multiple times to be statistically confident
        different_found = False
        for run in range(3):  # Try 3 times to find differences
            PersonalityContext._instance = PersonalityContext("playful", 5, seed=None)
            new_results = []
            for i in range(10):
                new_results.append(kinda_int(10))

            if new_results != results1:
                different_found = True
                break

        # With high probability, at least one run should be different
        self.assertTrue(
            different_found or len(set(results1)) > 1,
            "Non-seeded runs should produce variable results",
        )


if __name__ == "__main__":
    unittest.main()
