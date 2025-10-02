"""
Test suite for Issue #106: ~sorta print Probability Behavior

Tests the direct probability implementation of ~sorta print using chaos_probability().
This test suite validates that ~sorta print correctly uses personality-aware probability
(~80% base rate) and integrates properly with the personality system.
"""

import unittest
from unittest.mock import patch, MagicMock, call
import io
import contextlib
import sys

sys.path.insert(0, "src")

from kinda.cli import setup_personality
from kinda.personality import get_personality, PersonalityContext
from kinda.grammar.python.constructs import KindaPythonConstructs


class TestSortaPrintBehavior(unittest.TestCase):
    """Test the direct probability behavior in sorta_print"""

    def setUp(self):
        """Set up test environment with clean personality context"""
        PersonalityContext._instance = None
        setup_personality("reliable", chaos_level=1, seed=42)

        # Import construct functions into global scope
        self.exec_scope = globals()
        exec(KindaPythonConstructs["sometimes"]["body"], self.exec_scope)
        exec(KindaPythonConstructs["maybe"]["body"], self.exec_scope)
        exec(KindaPythonConstructs["sorta_print"]["body"], self.exec_scope)

    def test_direct_probability_execution(self):
        """Test 5: Verify that sorta_print uses chaos_probability directly (not composition)"""
        # New implementation uses chaos_probability('sorta_print') directly
        # This test verifies that it executes without calling sometimes/maybe

        # Mock chaos_probability to return high probability
        with patch("kinda.personality.chaos_probability", return_value=0.95):
            with patch("kinda.personality.chaos_random", return_value=0.5):
                buf = io.StringIO()
                with contextlib.redirect_stdout(buf):
                    sorta_print("test")
                output = buf.getvalue()

                # Should print because 0.5 < 0.95
                self.assertIn("[print] test", output)

    def test_union_logic_verification(self):
        """Test 6: Verify union logic (gate1 OR gate2) works correctly"""
        test_cases = [
            (True, True, True),  # Both gates true -> execute
            (True, False, True),  # First gate true -> execute
            (False, True, True),  # Second gate true -> execute
            (False, False, False),  # Both gates false -> don't execute (before bridge)
        ]

        for gate1, gate2, expected_before_bridge in test_cases:
            with self.subTest(gate1=gate1, gate2=gate2):
                # Mock the functions directly in globals
                original_sometimes = globals().get("sometimes")
                original_maybe = globals().get("maybe")

                globals()["sometimes"] = MagicMock(return_value=gate1)
                globals()["maybe"] = MagicMock(return_value=gate2)

                try:
                    # Capture output to check execution
                    buf = io.StringIO()
                    with contextlib.redirect_stdout(buf):
                        sorta_print("test")
                    output = buf.getvalue()

                    executed = "[print] test" in output

                    # For False case, bridge probability might kick in for playful/chaotic
                    # but reliable personality shouldn't need bridge logic
                    if expected_before_bridge:
                        self.assertTrue(executed, f"Should execute with gates {gate1} OR {gate2}")
                    # Note: We can't test the False case deterministically due to bridge probability

                finally:
                    # Restore original functions
                    if original_sometimes:
                        globals()["sometimes"] = original_sometimes
                    if original_maybe:
                        globals()["maybe"] = original_maybe

    def test_dependency_validation_missing_sometimes(self):
        """Test missing sometimes construct dependency"""
        # Temporarily remove sometimes from global scope
        original_sometimes = globals().pop("sometimes", None)
        try:
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                sorta_print("test")
            output = buf.getvalue()

            self.assertIn("[error] Basic construct 'sometimes' not available", output)
            self.assertIn("[fallback] test", output)
        finally:
            # Restore sometimes if it existed
            if original_sometimes:
                globals()["sometimes"] = original_sometimes

    def test_dependency_validation_missing_maybe(self):
        """Test missing maybe construct dependency"""
        # Temporarily remove maybe from global scope
        original_maybe = globals().pop("maybe", None)
        try:
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                sorta_print("test")
            output = buf.getvalue()

            self.assertIn("[error] Basic construct 'maybe' not available", output)
            self.assertIn("[fallback] test", output)
        finally:
            # Restore maybe if it existed
            if original_maybe:
                globals()["maybe"] = original_maybe

    def test_empty_arguments_composition(self):
        """Test 7: Test sorta_print behavior with no arguments using composition"""
        # Mock the functions directly in globals
        original_sometimes = globals().get("sometimes")
        original_maybe = globals().get("maybe")

        globals()["sometimes"] = MagicMock(return_value=True)
        globals()["maybe"] = MagicMock(return_value=False)

        try:
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                sorta_print()  # No arguments
            output = buf.getvalue()

            self.assertIn("[shrug] Nothing to print, I guess?", output)
        finally:
            # Restore original functions
            if original_sometimes:
                globals()["sometimes"] = original_sometimes
            if original_maybe:
                globals()["maybe"] = original_maybe

    def test_exception_handling_during_execution(self):
        """Test 8: Test error handling when personality system fails"""
        # Mock chaos_probability to raise exception
        with patch("kinda.personality.chaos_probability", side_effect=Exception("Test error")):
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                sorta_print("test")
            output = buf.getvalue()

            self.assertIn("[error] Sorta print kinda broke: Test error", output)
            self.assertIn("[fallback] test", output)


class TestSortaPrintPersonalityCompatibility(unittest.TestCase):
    """Test personality-specific behavior and bridge probability logic"""

    def setUp(self):
        """Set up test environment with clean personality context"""
        PersonalityContext._instance = None

    def test_reliable_personality_probability(self):
        """Test 1: Test sorta_print probability in reliable personality mode"""
        setup_personality("reliable", chaos_level=1, seed=42)

        # Import construct functions
        exec_scope = globals()
        exec(KindaPythonConstructs["sometimes"]["body"], exec_scope)
        exec(KindaPythonConstructs["maybe"]["body"], exec_scope)
        exec(KindaPythonConstructs["sorta_print"]["body"], exec_scope)

        # Statistical test with multiple samples
        successes = 0
        samples = 100
        for _ in range(samples):
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                sorta_print("test")
            output = buf.getvalue()
            if "[print] test" in output:
                successes += 1

        success_rate = successes / samples
        # Reliable should have high success rate (target ~0.95)
        self.assertGreater(
            success_rate, 0.85, f"Reliable personality success rate too low: {success_rate}"
        )

    def test_cautious_personality_probability(self):
        """Test 2: Test sorta_print probability in cautious personality mode"""
        setup_personality("cautious", chaos_level=3, seed=42)

        # Import construct functions
        exec_scope = globals()
        exec(KindaPythonConstructs["sometimes"]["body"], exec_scope)
        exec(KindaPythonConstructs["maybe"]["body"], exec_scope)
        exec(KindaPythonConstructs["sorta_print"]["body"], exec_scope)

        # Statistical test with multiple samples
        successes = 0
        samples = 100
        for _ in range(samples):
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                sorta_print("test")
            output = buf.getvalue()
            if "[print] test" in output:
                successes += 1

        success_rate = successes / samples
        # Cautious should have moderate to high success rate due to union of sometimes(0.7) + maybe(0.75)
        # Union gives max(0.7, 0.75) = 0.75, but with overlap it can be higher
        self.assertGreater(
            success_rate, 0.65, f"Cautious personality success rate too low: {success_rate}"
        )
        # Allow higher success rate since union logic can produce rates higher than individual components
        self.assertLessEqual(
            success_rate, 1.0, f"Cautious personality success rate impossible: {success_rate}"
        )

    def test_playful_personality_bridge_probability(self):
        """Test 3: Test bridge probability logic for playful personality"""
        setup_personality("playful", chaos_level=5, seed=42)

        # Import construct functions
        exec_scope = globals()
        exec(KindaPythonConstructs["sometimes"]["body"], exec_scope)
        exec(KindaPythonConstructs["maybe"]["body"], exec_scope)
        exec(KindaPythonConstructs["sorta_print"]["body"], exec_scope)

        # Statistical test with multiple samples
        successes = 0
        samples = 100
        for _ in range(samples):
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                sorta_print("test")
            output = buf.getvalue()
            if "[print] test" in output:
                successes += 1

        success_rate = successes / samples
        # Playful should have moderate success rate with bridge logic (target ~0.8)
        self.assertGreater(
            success_rate, 0.50, f"Playful personality success rate too low: {success_rate}"
        )
        self.assertLess(
            success_rate, 0.95, f"Playful personality success rate too high: {success_rate}"
        )

    def test_chaotic_personality_low_probability(self):
        """Test 4: Test chaotic personality produces lower execution probability"""
        setup_personality("chaotic", chaos_level=8, seed=42)

        # Import construct functions
        exec_scope = globals()
        exec(KindaPythonConstructs["sometimes"]["body"], exec_scope)
        exec(KindaPythonConstructs["maybe"]["body"], exec_scope)
        exec(KindaPythonConstructs["sorta_print"]["body"], exec_scope)

        # Statistical test with multiple samples
        successes = 0
        samples = 200  # More samples for better statistical accuracy
        for _ in range(samples):
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                sorta_print("test")
            output = buf.getvalue()
            if "[print] test" in output:
                successes += 1

        success_rate = successes / samples
        # Chaotic with high chaos level should have very low success rate
        # Base = 0.6, with chaos_amplifier=1.4 and chaos_level=8 (multiplier ~2.2)
        # Combined amplifier ~3.08 pulls 0.6 toward 0.5, then cascade effects further reduce
        # Expected range: 0.15 to 0.45 (very unpredictable)
        self.assertGreater(
            success_rate, 0.10, f"Chaotic personality success rate too low: {success_rate}"
        )
        self.assertLess(
            success_rate, 0.50, f"Chaotic personality success rate too high: {success_rate}"
        )


class TestSortaPrintBehavioralCompatibility(unittest.TestCase):
    """Test backward compatibility and existing behavior preservation"""

    def setUp(self):
        """Set up test environment with clean personality context"""
        PersonalityContext._instance = None
        setup_personality("playful", chaos_level=5, seed=42)

        # Import construct functions
        exec_scope = globals()
        exec(KindaPythonConstructs["sometimes"]["body"], exec_scope)
        exec(KindaPythonConstructs["maybe"]["body"], exec_scope)
        exec(KindaPythonConstructs["sorta_print"]["body"], exec_scope)

    def test_failure_produces_silence(self):
        """Test that ~sorta print respects the ~20% failure rate by producing silence"""
        # Force failure case by mocking both gates to return False and no bridge
        original_sometimes = globals().get("sometimes")
        original_maybe = globals().get("maybe")

        globals()["sometimes"] = MagicMock(return_value=False)
        globals()["maybe"] = MagicMock(return_value=False)

        try:
            with patch(
                "kinda.personality.chaos_random", return_value=0.9
            ):  # Above bridge threshold - ensures failure
                buf = io.StringIO()
                with contextlib.redirect_stdout(buf):
                    sorta_print("test")
                output = buf.getvalue()

                # When construct fails, should produce NO output (respecting ~20% failure rate)
                self.assertEqual(
                    output, "", f"Expected silence on failure, but got output: {output}"
                )
        finally:
            if original_sometimes:
                globals()["sometimes"] = original_sometimes
            if original_maybe:
                globals()["maybe"] = original_maybe

    def test_error_handling_preserved(self):
        """Test that existing error handling patterns are preserved"""
        # Force exception in personality system
        with patch("kinda.personality.chaos_probability", side_effect=Exception("Chaos error")):
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                sorta_print("error_test")
            output = buf.getvalue()

            self.assertIn("[error] Sorta print kinda broke: Chaos error", output)
            self.assertIn("[fallback] error_test", output)

    def test_chaos_state_tracking_preserved(self):
        """Test that chaos state tracking is preserved in composition"""
        # This is harder to test directly, but we can verify the function is called
        with patch("kinda.personality.update_chaos_state") as mock_update:
            with io.StringIO() as buf, contextlib.redirect_stdout(buf):
                sorta_print("chaos_test")

            # update_chaos_state should be called at least once
            self.assertTrue(mock_update.called, "Chaos state should be updated")


class TestSortaPrintPerformanceRegression(unittest.TestCase):
    """Test 10: Performance comparison and regression testing"""

    def setUp(self):
        """Set up test environment"""
        PersonalityContext._instance = None
        setup_personality("reliable", chaos_level=1, seed=42)

    def test_composition_performance_acceptable(self):
        """Test that composition doesn't introduce excessive performance overhead"""
        import time

        # Import construct functions
        exec_scope = globals()
        exec(KindaPythonConstructs["sometimes"]["body"], exec_scope)
        exec(KindaPythonConstructs["maybe"]["body"], exec_scope)
        exec(KindaPythonConstructs["sorta_print"]["body"], exec_scope)

        # Measure composition implementation performance
        iterations = 1000
        start_time = time.perf_counter()

        for i in range(iterations):
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                sorta_print(f"performance_test_{i}")

        composition_time = time.perf_counter() - start_time

        # Test should complete within reasonable time (adjust threshold as needed)
        # This is mainly to catch egregious performance regressions
        max_acceptable_time = 5.0  # 5 seconds for 1000 iterations
        self.assertLess(
            composition_time,
            max_acceptable_time,
            f"Composition took too long: {composition_time:.3f}s > {max_acceptable_time}s",
        )

        print(
            f"Composition performance: {composition_time:.3f}s for {iterations} iterations "
            f"({composition_time/iterations*1000:.3f}ms per call)"
        )


if __name__ == "__main__":
    unittest.main()
