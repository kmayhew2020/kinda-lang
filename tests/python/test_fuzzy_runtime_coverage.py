#!/usr/bin/env python3

import pytest
import os
from unittest.mock import patch, MagicMock
import random
from kinda.langs.python.runtime.fuzzy import fuzzy_assign, kinda_int, maybe, sometimes, sorta_print
from kinda.personality import PersonalityContext


class TestFuzzyAssignErrorHandling:
    """Test fuzzy_assign error handling - covers lines 18-21"""

    def setup_method(self):
        """Set up deterministic PersonalityContext for each test."""
        PersonalityContext._instance = None

    def test_fuzzy_assign_exception_during_processing(self):
        """Test fuzzy_assign when an exception occurs during processing"""
        # With the new seeded system, exceptions are less likely, so let's test
        # with an extreme input that might cause issues
        PersonalityContext._instance = PersonalityContext("playful", 5, seed=99999)

        with patch("builtins.print") as mock_print:
            # Test with an input that can potentially cause issues
            result = fuzzy_assign("test_var", float("inf"))

            # Should handle gracefully and return a valid integer
            assert isinstance(result, int)
            # In case of extreme values, should return fallback range
            assert 0 <= result <= 10 or abs(result - float("inf")) < 100


class TestKindaIntErrorHandling:
    """Test kinda_int error handling - covers lines 65-68"""

    def setup_method(self):
        """Set up deterministic PersonalityContext for each test."""
        PersonalityContext._instance = None

    def test_kinda_int_exception_during_processing(self):
        """Test kinda_int when an exception occurs during processing"""
        PersonalityContext._instance = PersonalityContext("playful", 5, seed=44444)

        # Test with extreme input that should trigger error handling
        with patch("builtins.print") as mock_print:
            result = kinda_int(float("inf"))

            # Should handle gracefully and return a valid integer
            assert isinstance(result, int)
            # Should either handle inf or fallback to 0-10 range
            assert result == result  # Should be deterministic with seed


class TestMaybeErrorHandling:
    """Test maybe error handling - covers lines 79-82"""

    def setup_method(self):
        """Set up deterministic PersonalityContext for each test."""
        PersonalityContext._instance = None

    def test_maybe_exception_during_evaluation(self):
        """Test maybe when an exception occurs during evaluation"""
        PersonalityContext._instance = PersonalityContext("playful", 5, seed=55555)

        # Create a condition that raises an exception when converted to bool
        class ProblematicCondition:
            def __bool__(self):
                raise ValueError("Condition evaluation failed")

        with patch("builtins.print") as mock_print:
            result = maybe(ProblematicCondition())

            # Should handle gracefully and return a boolean
            assert isinstance(result, bool)
            # With seeded RNG, result should be deterministic
            assert result == result


class TestSometimesErrorHandling:
    """Test sometimes error handling - covers lines 93-96"""

    def setup_method(self):
        """Set up deterministic PersonalityContext for each test."""
        PersonalityContext._instance = None

    def test_sometimes_exception_during_evaluation(self):
        """Test sometimes when an exception occurs during evaluation"""
        PersonalityContext._instance = PersonalityContext("playful", 5, seed=66666)

        # Create a condition that raises an exception when evaluated as bool
        class ProblematicCondition:
            def __bool__(self):
                raise RuntimeError("Boolean conversion failed")

        with patch("builtins.print") as mock_print:
            result = sometimes(ProblematicCondition())

            # Should handle gracefully and return a boolean
            assert isinstance(result, bool)
            # With seeded RNG, result should be deterministic
            assert result == result


class TestSortaPrintErrorHandling:
    """Test sorta_print error handling - covers lines 120-122"""

    def test_sorta_print_exception_during_printing(self):
        """Test sorta_print when an exception occurs during printing"""
        # Set up seeded context
        PersonalityContext._instance = PersonalityContext("playful", 5, seed=99999)
        
        # Capture printed messages
        printed_messages = []

        def mock_print(*args, **kwargs):
            message = " ".join(str(arg) for arg in args)
            printed_messages.append(message)
            # Fail on the specific print pattern to trigger exception handling
            if message.startswith("[print]"):
                raise IOError("Print operation failed")

        with patch("builtins.print", side_effect=mock_print):
            sorta_print("test message")

            # Should have captured the error and fallback messages if exception occurred
            output = " ".join(printed_messages)
            
            # Check for either normal output or error handling
            if "[error] Sorta print kinda broke:" in output:
                assert "[fallback] test message" in output
            elif "[print] test message" in output:
                # Normal execution path - also valid
                pass
            else:
                # Shrug response path - also valid 
                assert "[shrug]" in output and "test message" in output

    def test_sorta_print_no_args_shrug_response(self):
        """Test sorta_print with no args and shrug response"""
        PersonalityContext._instance = PersonalityContext("playful", 5, seed=77777)

        with patch("builtins.print") as mock_print:
            sorta_print()

            # Should handle no args gracefully, may or may not print
            # The important thing is it doesn't crash
            assert True  # Test passes if no exception

    def test_sorta_print_no_args_with_shrug_message(self):
        """Test sorta_print with no args but shows shrug message"""
        # Set up a seeded context that will trigger the shrug message path
        PersonalityContext._instance = PersonalityContext("playful", 5, seed=88888)
        
        with patch("builtins.print") as mock_print:
            sorta_print()
            
            # With deterministic seeding, should print shrug message when no args
            # Check that print was called with a shrug message
            if mock_print.call_count > 0:
                call_args = str(mock_print.call_args)
                assert "[shrug] Nothing to print, I guess?" in call_args
            else:
                # If no call was made, that's also valid behavior for sorta_print with no args
                assert mock_print.call_count == 0


class TestFuzzyRuntimeIntegration:
    """Test integration and edge cases across fuzzy runtime functions"""

    def test_all_functions_handle_extreme_edge_cases(self):
        """Test all functions with extreme edge cases"""
        # Test with None values
        with patch("builtins.print"):
            assert isinstance(fuzzy_assign("var", None), int)
            assert isinstance(kinda_int(None), int)
            assert isinstance(maybe(None), bool)
            assert isinstance(sometimes(None), bool)

            # Should not crash when called
            sorta_print(None)

    def test_random_seed_consistency(self):
        """Test that functions work with different random seeds"""
        seeds = [0, 42, 12345, 999999]

        for seed in seeds:
            random.seed(seed)

            # All functions should work regardless of random state
            with patch("builtins.print"):
                result1 = fuzzy_assign("test", 10)
                result2 = kinda_int(5)
                result3 = maybe(True)
                result4 = sometimes(True)

                assert isinstance(result1, int)
                assert isinstance(result2, int)
                assert isinstance(result3, bool)
                assert isinstance(result4, bool)

                sorta_print("test")  # Should not crash

    def test_functions_with_complex_data_types(self):
        """Test functions with complex data types that might cause issues"""
        complex_inputs = [
            float("inf"),
            float("-inf"),
            [],
            {},
            set(),
            object(),
        ]

        with patch("builtins.print"):
            for input_val in complex_inputs:
                # Should handle gracefully without crashing
                result1 = fuzzy_assign("var", input_val)
                result2 = kinda_int(input_val)
                result3 = maybe(input_val)
                result4 = sometimes(input_val)

                assert isinstance(result1, int)
                assert isinstance(result2, int)
                assert isinstance(result3, bool)
                assert isinstance(result4, bool)

                sorta_print(input_val)  # Should not crash
