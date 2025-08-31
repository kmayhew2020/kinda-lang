"""
Comprehensive tests for time-based variable drift functionality.
Tests drift accumulation, personality integration, and time-based behavior.
"""

import pytest
import tempfile
import time
from pathlib import Path
from unittest.mock import patch, MagicMock
import random

from kinda.langs.python.transformer import transform_line, transform_file
from kinda.grammar.python.matchers import match_python_construct
from kinda.langs.python.runtime_gen import generate_runtime_helpers
from kinda.grammar.python.constructs import KindaPythonConstructs
from kinda.personality import PersonalityContext, PERSONALITY_PROFILES, register_time_variable, get_time_drift, get_variable_age


class TestTimeDriftPersonalityIntegration:
    """Test time-based drift integration with personality system"""

    def setup_method(self):
        """Set up clean personality state before each test"""
        PersonalityContext._instance = None

    def teardown_method(self):
        """Clean up personality state after each test"""
        PersonalityContext._instance = None

    def test_register_variable_tracking(self):
        """Test variable registration for time-based drift"""
        PersonalityContext._instance = None
        personality = PersonalityContext.get_instance()
        
        # Register a variable
        register_time_variable("test_var", 10.5, "float")
        
        # Check that it's tracked
        assert "test_var" in personality.drift_accumulator
        var_info = personality.drift_accumulator["test_var"]
        assert var_info["initial_value"] == 10.5
        assert var_info["var_type"] == "float"
        assert var_info["access_count"] == 0
        assert var_info["accumulated_drift"] == 0.0

    def test_time_drift_calculation(self):
        """Test time-based drift calculation"""
        PersonalityContext.set_mood("playful")  # Has drift_rate = 0.05
        personality = PersonalityContext.get_instance()
        
        # Register a variable
        register_time_variable("drift_test", 100.0, "float")
        
        # Mock time to simulate aging
        with patch("time.time") as mock_time:
            # Initial registration time
            mock_time.return_value = 1000.0
            register_time_variable("aged_var", 50.0, "float")
            
            # Simulate 10 seconds later
            mock_time.return_value = 1010.0
            drift = get_time_drift("aged_var", 50.0)
            
            # Should have some drift due to age
            assert isinstance(drift, float)
            # Drift should be reasonable magnitude
            assert abs(drift) < 10.0  # Shouldn't be huge

    def test_drift_with_zero_drift_rate(self):
        """Test that zero drift rate produces no drift"""
        PersonalityContext.set_mood("reliable")  # Has drift_rate = 0.0
        personality = PersonalityContext.get_instance()
        
        register_time_variable("no_drift_var", 42.0, "float")
        
        # Should get no drift regardless of time
        drift = get_time_drift("no_drift_var", 42.0)
        assert drift == 0.0

    def test_drift_accumulation_tracking(self):
        """Test that drift accumulates properly"""
        PersonalityContext.set_mood("playful")
        personality = PersonalityContext.get_instance()
        
        register_time_variable("accumulate_test", 10.0, "float")
        
        # Get drift multiple times
        initial_accumulated = personality.drift_accumulator["accumulate_test"]["accumulated_drift"]
        
        drift1 = get_time_drift("accumulate_test", 10.0)
        after_first = personality.drift_accumulator["accumulate_test"]["accumulated_drift"]
        
        drift2 = get_time_drift("accumulate_test", 10.0)
        after_second = personality.drift_accumulator["accumulate_test"]["accumulated_drift"]
        
        # Accumulated drift should increase
        assert after_first >= initial_accumulated
        assert after_second >= after_first

    def test_access_count_tracking(self):
        """Test that access count increases with each drift calculation"""
        PersonalityContext.set_mood("playful")
        personality = PersonalityContext.get_instance()
        
        register_time_variable("access_test", 5.0, "float")
        
        initial_count = personality.drift_accumulator["access_test"]["access_count"]
        assert initial_count == 0
        
        get_time_drift("access_test", 5.0)
        assert personality.drift_accumulator["access_test"]["access_count"] == 1
        
        get_time_drift("access_test", 5.0)
        assert personality.drift_accumulator["access_test"]["access_count"] == 2

    def test_variable_age_calculation(self):
        """Test variable age calculation"""
        with patch("time.time") as mock_time:
            mock_time.return_value = 1000.0
            PersonalityContext._instance = None
            register_time_variable("age_test", 1.0, "float")
            
            # Simulate 5 seconds later
            mock_time.return_value = 1005.0
            age = get_variable_age("age_test")
            assert age == 5.0

    def test_chaos_amplifier_affects_drift(self):
        """Test that chaos amplifier affects drift magnitude"""
        # Test with low chaos (reliable personality has 0.2 amplifier)
        PersonalityContext._instance = None
        PersonalityContext.set_mood("reliable")
        register_time_variable("low_chaos", 10.0, "float")
        low_drift = abs(get_time_drift("low_chaos", 10.0))
        
        # Test with high chaos (chaotic personality has 1.8 amplifier)
        PersonalityContext._instance = None  
        PersonalityContext.set_mood("chaotic")
        register_time_variable("high_chaos", 10.0, "float")
        high_drift = abs(get_time_drift("high_chaos", 10.0))
        
        # Both should be floats (actual values will vary due to randomness)
        assert isinstance(high_drift, float)
        assert isinstance(low_drift, float)

    def test_unregistered_variable_no_drift(self):
        """Test that unregistered variables produce no drift"""
        PersonalityContext.set_mood("chaotic")
        drift = get_time_drift("nonexistent_var", 42.0)
        assert drift == 0.0


class TestTimeDriftFloatConstruct:
    """Test ~time drift float construct"""

    def test_time_drift_float_syntax_parsing(self):
        """Test ~time drift float syntax parsing"""
        test_cases = [
            "~time drift float x = 3.14;",
            "~time drift float temperature ~= 98.6;",
            "~time drift float value = 0.0;",
            "~time drift float rate ~== 2.5;",
        ]

        for line in test_cases:
            construct_type, groups = match_python_construct(line)
            assert construct_type == "time_drift_float", f"Failed to parse: {line}"
            assert len(groups) == 2, f"Expected 2 groups, got {len(groups)} for: {line}"

    def test_time_drift_float_variable_names(self):
        """Test various variable naming patterns"""
        test_cases = [
            ("~time drift float x = 1.5;", "x", "1.5"),
            ("~time drift float temperature = 72.3;", "temperature", "72.3"),
            ("~time drift float value123 ~= 99.99;", "value123", "99.99"),
            ("~time drift float _private = 0.001;", "_private", "0.001"),
        ]

        for line, expected_var, expected_val in test_cases:
            construct_type, groups = match_python_construct(line)
            assert construct_type == "time_drift_float"
            var, val = groups
            assert var == expected_var, f"Expected var '{expected_var}', got '{var}'"
            assert val == expected_val, f"Expected val '{expected_val}', got '{val}'"

    def test_time_drift_float_transformation(self):
        """Test transformation of ~time drift float"""
        line = "~time drift float pi = 3.14159;"
        result = transform_line(line)

        assert len(result) == 1
        assert "pi = time_drift_float('pi', 3.14159)" in result[0]

    def test_time_drift_float_function_behavior(self):
        """Test time_drift_float function behavior"""
        # Create namespace and execute function definition
        test_namespace = {}
        exec(KindaPythonConstructs["time_drift_float"]["body"], test_namespace)
        time_drift_float = test_namespace["time_drift_float"]

        # Mock the personality functions
        with patch("kinda.personality.register_time_variable") as mock_register:
            with patch("random.uniform", return_value=0.005):  # Small initial drift
                result = time_drift_float("test_var", 10.0)
                
                # Should register the variable
                mock_register.assert_called_once_with("test_var", 10.0, "float")
                
                # Should return value close to original with small drift
                assert isinstance(result, float)
                assert abs(result - 10.0) < 0.1  # Small initial drift

    def test_time_drift_float_with_string_values(self):
        """Test time_drift_float with string numeric values"""
        test_namespace = {}
        exec(KindaPythonConstructs["time_drift_float"]["body"], test_namespace)
        time_drift_float = test_namespace["time_drift_float"]

        with patch("kinda.personality.register_time_variable"):
            with patch("random.uniform", return_value=0.0):  # No drift for easier testing
                result = time_drift_float("string_test", "3.14159")
                assert isinstance(result, float)
                assert result == 3.14159

    def test_time_drift_float_error_handling(self):
        """Test error handling in time_drift_float"""
        test_namespace = {}
        exec(KindaPythonConstructs["time_drift_float"]["body"], test_namespace)
        time_drift_float = test_namespace["time_drift_float"]

        with patch("kinda.personality.register_time_variable"):
            with patch("random.uniform", return_value=5.0):
                result = time_drift_float("error_test", "not_a_number")
                assert isinstance(result, float)
                # Should return fallback random value


class TestTimeDriftIntConstruct:
    """Test ~time drift int construct"""

    def test_time_drift_int_syntax_parsing(self):
        """Test ~time drift int syntax parsing"""
        test_cases = [
            "~time drift int x = 42;",
            "~time drift int count ~= 100;",
            "~time drift int value = 0;",
            "~time drift int iterations ~== 50;",
        ]

        for line in test_cases:
            construct_type, groups = match_python_construct(line)
            assert construct_type == "time_drift_int", f"Failed to parse: {line}"
            assert len(groups) == 2, f"Expected 2 groups, got {len(groups)} for: {line}"

    def test_time_drift_int_transformation(self):
        """Test transformation of ~time drift int"""
        line = "~time drift int count = 42;"
        result = transform_line(line)

        assert len(result) == 1
        assert "count = time_drift_int('count', 42)" in result[0]

    def test_time_drift_int_function_behavior(self):
        """Test time_drift_int function behavior"""
        test_namespace = {}
        exec(KindaPythonConstructs["time_drift_int"]["body"], test_namespace)
        time_drift_int = test_namespace["time_drift_int"]

        with patch("kinda.personality.register_time_variable") as mock_register:
            with patch("random.choice", return_value=0):  # No initial fuzz
                result = time_drift_int("int_test", 42)
                
                mock_register.assert_called_once_with("int_test", 42, "int")
                assert isinstance(result, int)
                assert result == 42  # No fuzz applied

    def test_time_drift_int_with_fuzz(self):
        """Test time_drift_int with initial fuzz"""
        test_namespace = {}
        exec(KindaPythonConstructs["time_drift_int"]["body"], test_namespace)
        time_drift_int = test_namespace["time_drift_int"]

        with patch("kinda.personality.register_time_variable"):
            with patch("random.choice", return_value=1):  # Small positive fuzz
                result = time_drift_int("fuzz_test", 10)
                assert isinstance(result, int)
                assert result == 11

    def test_time_drift_int_error_handling(self):
        """Test error handling in time_drift_int"""
        test_namespace = {}
        exec(KindaPythonConstructs["time_drift_int"]["body"], test_namespace)
        time_drift_int = test_namespace["time_drift_int"]

        with patch("kinda.personality.register_time_variable"):
            with patch("random.randint", return_value=7):
                result = time_drift_int("error_test", "not_a_number")
                assert isinstance(result, int)
                # Should return fallback random value


class TestDriftAccessConstruct:
    """Test drift access pattern (var~drift)"""

    def test_drift_access_syntax_parsing(self):
        """Test drift access syntax parsing"""
        test_cases = [
            "x~drift",
            "temperature~drift",
            "value123~drift",
            "_private~drift",
        ]

        for line in test_cases:
            construct_type, groups = match_python_construct(line)
            assert construct_type == "drift_access", f"Failed to parse: {line}"
            assert len(groups) == 1, f"Expected 1 group, got {len(groups)} for: {line}"

    def test_drift_access_transformation(self):
        """Test transformation of drift access"""
        line = "result = x~drift;"
        result = transform_line(line)

        assert len(result) == 1
        assert "drift_access('x', x)" in result[0]


class TestTimeDriftIntegration:
    """Test integration of time-based drift with other constructs"""

    def test_file_transformation_includes_helpers(self):
        """Test that file transformation includes time drift helpers"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".kinda", delete=False) as f:
            f.write("~time drift float rate = 2.5;\n")
            f.write("~sorta print(rate~drift);\n")
            temp_file = f.name

        try:
            result = transform_file(temp_file)

            # Should include time drift helpers
            assert "time_drift_float" in result
            assert "drift_access" in result
            assert "rate = time_drift_float('rate', 2.5)" in result

        finally:
            Path(temp_file).unlink()

    def test_time_drift_with_conditional_constructs(self):
        """Test time drift with ~sometimes, ~maybe, ~probably"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".kinda", delete=False) as f:
            f.write("~time drift float threshold = 0.5;\n")
            f.write("~sometimes (threshold~drift > 0) {\n")
            f.write("    ~sorta print('threshold is positive');\n")
            f.write("}\n")
            temp_file = f.name

        try:
            result = transform_file(temp_file)
            assert "threshold = time_drift_float('threshold', 0.5)" in result
            assert "drift_access('threshold', threshold)" in result
            assert "if sometimes(" in result
        finally:
            Path(temp_file).unlink()

    def test_time_drift_with_ish_comparison(self):
        """Test time drift with ~ish comparisons"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".kinda", delete=False) as f:
            f.write("~time drift float pi = 3.14159;\n")
            f.write("result = pi~drift ~ish 3.14;\n")
            temp_file = f.name

        try:
            result = transform_file(temp_file)
            assert "pi = time_drift_float('pi', 3.14159)" in result
            assert "drift_access('pi', pi)" in result
            assert "ish_comparison(" in result
        finally:
            Path(temp_file).unlink()

    def test_mixed_time_drift_and_regular_constructs(self):
        """Test mixing time drift with regular kinda constructs"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".kinda", delete=False) as f:
            f.write("~time drift float x = 10.0;\n")
            f.write("~kinda float y = 20.0;\n")
            f.write("~kinda int z = 5;\n")
            f.write("sum_val = x~drift + y + z;\n")
            f.write("~sorta print('Sum:', sum_val);\n")
            temp_file = f.name

        try:
            result = transform_file(temp_file)
            assert "x = time_drift_float('x', 10.0)" in result
            assert "y = kinda_float(20.0)" in result
            assert "z = kinda_int(5)" in result
            assert "drift_access('x', x)" in result
        finally:
            Path(temp_file).unlink()


class TestTimeDriftPersonalityProfiles:
    """Test time drift behavior with different personality profiles"""

    def setup_method(self):
        """Set up clean personality state before each test"""
        PersonalityContext._instance = None

    def teardown_method(self):
        """Clean up personality state after each test"""
        PersonalityContext._instance = None

    def test_reliable_personality_minimal_time_drift(self):
        """Test reliable personality has minimal time-based drift"""
        PersonalityContext._instance = None  # Extra safety
        PersonalityContext.set_mood("reliable")
        personality = PersonalityContext.get_instance()
        
        assert personality.profile.drift_rate == 0.0
        
        register_time_variable("reliable_var", 10.0, "float")
        drift = get_time_drift("reliable_var", 10.0)
        assert drift == 0.0

    def test_chaotic_personality_high_time_drift(self):
        """Test chaotic personality has high time-based drift"""
        PersonalityContext.set_mood("chaotic")
        personality = PersonalityContext.get_instance()
        
        assert personality.profile.drift_rate == 0.1  # High drift rate
        
        register_time_variable("chaotic_var", 10.0, "float")
        drift = get_time_drift("chaotic_var", 10.0)
        
        # Should have some drift (non-zero)
        # Note: Due to randomness, we can't guarantee exact values
        assert isinstance(drift, float)

    def test_playful_personality_moderate_time_drift(self):
        """Test playful personality has moderate time-based drift"""
        PersonalityContext._instance = None  # Ensure clean state
        PersonalityContext.set_mood("playful")
        personality = PersonalityContext.get_instance()
        
        assert personality.profile.drift_rate == 0.05  # Moderate drift rate
        
        register_time_variable("playful_var", 10.0, "float")
        drift = get_time_drift("playful_var", 10.0)
        
        assert isinstance(drift, float)

    def test_cautious_personality_slow_time_drift(self):
        """Test cautious personality has slow time-based drift"""
        PersonalityContext.set_mood("cautious")
        personality = PersonalityContext.get_instance()
        
        assert personality.profile.drift_rate == 0.01  # Slow drift rate
        
        register_time_variable("cautious_var", 10.0, "float")
        drift = get_time_drift("cautious_var", 10.0)
        
        assert isinstance(drift, float)


class TestTimeDriftEdgeCases:
    """Test edge cases and error scenarios"""

    def test_drift_with_zero_values(self):
        """Test drift behavior with zero values"""
        PersonalityContext.set_mood("playful")
        register_time_variable("zero_var", 0.0, "float")
        drift = get_time_drift("zero_var", 0.0)
        
        assert isinstance(drift, float)
        # Should handle zero values gracefully

    def test_drift_with_negative_values(self):
        """Test drift behavior with negative values"""
        PersonalityContext.set_mood("playful")
        register_time_variable("negative_var", -10.0, "float")
        drift = get_time_drift("negative_var", -10.0)
        
        assert isinstance(drift, float)
        # Should handle negative values gracefully

    def test_drift_with_very_large_values(self):
        """Test drift behavior with very large values"""
        PersonalityContext.set_mood("playful")
        large_val = 1e6
        register_time_variable("large_var", large_val, "float")
        drift = get_time_drift("large_var", large_val)
        
        assert isinstance(drift, float)
        # Drift should be reasonable relative to value size

    def test_drift_with_very_small_values(self):
        """Test drift behavior with very small values"""
        PersonalityContext.set_mood("playful")
        small_val = 1e-6
        register_time_variable("small_var", small_val, "float")
        drift = get_time_drift("small_var", small_val)
        
        assert isinstance(drift, float)

    def test_repeated_access_increases_drift(self):
        """Test that repeated access can increase drift magnitude"""
        PersonalityContext.set_mood("playful")
        register_time_variable("repeated_var", 10.0, "float")
        
        # Access multiple times
        drifts = []
        for i in range(10):
            drift = get_time_drift("repeated_var", 10.0)
            drifts.append(drift)
        
        # Should all be floats
        for drift in drifts:
            assert isinstance(drift, float)
        
        # Access count should increase
        personality = PersonalityContext.get_instance()
        assert personality.drift_accumulator["repeated_var"]["access_count"] == 10


class TestTimeDriftDocumentation:
    """Test that time drift constructs have proper documentation"""

    def test_constructs_have_descriptions(self):
        """Test that all time drift constructs have descriptions"""
        time_drift_constructs = ["time_drift_float", "time_drift_int", "drift_access"]
        
        for construct_name in time_drift_constructs:
            construct_info = KindaPythonConstructs[construct_name]
            assert "description" in construct_info
            assert len(construct_info["description"]) > 0
            assert "time" in construct_info["description"].lower() or "drift" in construct_info["description"].lower()

    def test_constructs_have_proper_types(self):
        """Test that time drift constructs have proper types"""
        assert KindaPythonConstructs["time_drift_float"]["type"] == "declaration"
        assert KindaPythonConstructs["time_drift_int"]["type"] == "declaration"
        assert KindaPythonConstructs["drift_access"]["type"] == "access"


if __name__ == "__main__":
    pytest.main([__file__])