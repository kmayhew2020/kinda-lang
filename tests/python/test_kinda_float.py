"""
Comprehensive tests for the ~kinda float construct.
Tests basic functionality, edge cases, personality integration, and fuzzy behavior.
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch
import random
import math

from kinda.langs.python.transformer import transform_line, transform_file
from kinda.grammar.python.matchers import match_python_construct
from kinda.langs.python.runtime_gen import generate_runtime_helpers
from kinda.grammar.python.constructs import KindaPythonConstructs
from kinda.personality import PersonalityContext, PERSONALITY_PROFILES


class TestKindaFloatConstructParsing:
    """Test ~kinda float construct parsing functionality"""

    def test_kinda_float_basic_syntax(self):
        """Test basic ~kinda float syntax parsing"""
        test_cases = [
            "~kinda float pi = 3.14159;",
            "~kinda float temp ~= 98.6;",
            "~kinda float rate = 2.5;",
            "~kinda float value ~= 0.0;",
        ]

        for line in test_cases:
            construct_type, groups = match_python_construct(line)
            assert construct_type == "kinda_float", f"Failed to parse: {line}"
            assert len(groups) == 2, f"Expected 2 groups, got {len(groups)} for: {line}"

    def test_kinda_float_variable_names(self):
        """Test various variable naming patterns"""
        test_cases = [
            ("~kinda float x = 1.5;", "x", "1.5"),
            ("~kinda float temperature = 72.3;", "temperature", "72.3"),
            ("~kinda float value123 ~= 99.99;", "value123", "99.99"),
            ("~kinda float _private = 0.001;", "_private", "0.001"),
        ]

        for line, expected_var, expected_val in test_cases:
            construct_type, groups = match_python_construct(line)
            assert construct_type == "kinda_float"
            var, val = groups
            assert var == expected_var, f"Expected var '{expected_var}', got '{var}'"
            assert val == expected_val, f"Expected val '{expected_val}', got '{val}'"

    def test_kinda_float_various_values(self):
        """Test parsing with various float-like values"""
        test_cases = [
            "~kinda float pi = 3.14159;",
            "~kinda float zero = 0.0;",
            "~kinda float negative = -5.5;",
            "~kinda float integer = 42;",
            "~kinda float scientific = 1.23e-4;",
            "~kinda float var_ref = some_variable;",
            "~kinda float func_result = calculate_value();",
        ]

        for line in test_cases:
            construct_type, groups = match_python_construct(line)
            assert construct_type == "kinda_float", f"Failed to parse: {line}"

    def test_kinda_float_with_comments(self):
        """Test ~kinda float with comments"""
        line = "~kinda float temperature = 98.6; # Body temperature"
        construct_type, groups = match_python_construct(line)

        assert construct_type == "kinda_float"
        var, val = groups
        assert var == "temperature"
        assert val == "98.6"  # Comments should be stripped

    def test_kinda_float_operators(self):
        """Test both = and ~= operators"""
        test_cases = [
            ("~kinda float rate = 2.5;", "rate", "2.5"),
            ("~kinda float rate ~= 2.5;", "rate", "2.5"),
            ("~kinda float rate == 2.5;", "rate", "2.5"),
            ("~kinda float rate ~== 2.5;", "rate", "2.5"),
        ]

        for line, expected_var, expected_val in test_cases:
            construct_type, groups = match_python_construct(line)
            assert construct_type == "kinda_float"
            var, val = groups
            assert var == expected_var
            assert val == expected_val

    def test_kinda_float_scientific_notation(self):
        """Test scientific notation parsing"""
        test_cases = [
            ("~kinda float small = 1.23e-4;", "small", "1.23e-4"),
            ("~kinda float large = 6.02e23;", "large", "6.02e23"),
            ("~kinda float negative = -9.8e1;", "negative", "-9.8e1"),
        ]

        for line, expected_var, expected_val in test_cases:
            construct_type, groups = match_python_construct(line)
            assert construct_type == "kinda_float"
            var, val = groups
            assert var == expected_var
            assert val == expected_val


class TestKindaFloatTransformation:
    """Test ~kinda float transformation functionality"""

    def test_transform_basic_kinda_float(self):
        """Test basic transformation of ~kinda float"""
        line = "~kinda float pi = 3.14159;"
        result = transform_line(line)

        assert len(result) == 1
        assert "pi = kinda_float(3.14159)" in result[0]

    def test_transform_kinda_float_with_fuzzy_assign(self):
        """Test transformation with fuzzy assignment operator"""
        line = "~kinda float temp ~= 98.6;"
        result = transform_line(line)

        assert len(result) == 1
        assert "temp = kinda_float(98.6)" in result[0]

    def test_transform_kinda_float_various_values(self):
        """Test transformation with various value types"""
        test_cases = [
            ("~kinda float x = 42;", "x = kinda_float(42)"),
            ("~kinda float y = 'string';", "y = kinda_float('string')"),
            ("~kinda float z = some_var;", "z = kinda_float(some_var)"),
            ("~kinda float scientific = 1.23e-4;", "scientific = kinda_float(1.23e-4)"),
        ]

        for input_line, expected_output in test_cases:
            result = transform_line(input_line)
            assert len(result) == 1
            assert expected_output in result[0]

    def test_file_transformation_includes_helpers(self):
        """Test that file transformation includes kinda_float helper"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".kinda", delete=False) as f:
            f.write("~kinda float rate = 2.5;\n")
            f.write("~sorta print(rate);\n")
            temp_file = f.name

        try:
            result = transform_file(temp_file)

            # Should import kinda_float helper
            assert "kinda_float" in result
            assert "rate = kinda_float(2.5)" in result

        finally:
            Path(temp_file).unlink()


class TestKindaFloatRuntime:
    """Test ~kinda float runtime behavior"""

    def test_kinda_float_function_exists(self):
        """Test that kinda_float function is properly defined"""
        construct_info = KindaPythonConstructs["kinda_float"]
        assert "def kinda_float(" in construct_info["body"]

    def test_kinda_float_with_float_values(self):
        """Test kinda_float function with actual float values"""
        # Create namespace and execute function definition
        test_namespace = {}
        exec(KindaPythonConstructs["kinda_float"]["body"], test_namespace)
        kinda_float = test_namespace["kinda_float"]

        # Test with positive float
        with patch("random.uniform", return_value=0.1):  # Small drift
            with patch("kinda.personality.chaos_float_drift_range", return_value=(-0.5, 0.5)):
                result = kinda_float(3.14)
                assert isinstance(result, float)
                assert abs(result - 3.14) <= 0.5  # Within drift range

        # Test with negative float
        with patch("random.uniform", return_value=-0.1):  # Small negative drift
            with patch("kinda.personality.chaos_float_drift_range", return_value=(-0.5, 0.5)):
                result = kinda_float(-2.5)
                assert isinstance(result, float)
                assert abs(result - (-2.5)) <= 0.5  # Within drift range

    def test_kinda_float_with_integer_values(self):
        """Test kinda_float with integer input values"""
        test_namespace = {}
        exec(KindaPythonConstructs["kinda_float"]["body"], test_namespace)
        kinda_float = test_namespace["kinda_float"]

        # Test with integer input
        with patch("random.uniform", return_value=0.2):  # Drift value
            with patch("kinda.personality.chaos_float_drift_range", return_value=(-0.5, 0.5)):
                result = kinda_float(42)
                assert isinstance(result, float)
                assert result == 42.2  # 42 + 0.2 drift

    def test_kinda_float_with_string_values(self):
        """Test kinda_float with string numeric values"""
        test_namespace = {}
        exec(KindaPythonConstructs["kinda_float"]["body"], test_namespace)
        kinda_float = test_namespace["kinda_float"]

        # Test with string representation of float
        with patch("random.uniform", return_value=0.0):  # No drift for easier testing
            with patch("kinda.personality.chaos_float_drift_range", return_value=(-0.5, 0.5)):
                result = kinda_float("3.14159")
                assert isinstance(result, float)
                assert result == 3.14159

        # Test with string representation of integer
        with patch("random.uniform", return_value=0.0):
            with patch("kinda.personality.chaos_float_drift_range", return_value=(-0.5, 0.5)):
                result = kinda_float("42")
                assert isinstance(result, float)
                assert result == 42.0

    def test_kinda_float_scientific_notation(self):
        """Test kinda_float with scientific notation"""
        test_namespace = {}
        exec(KindaPythonConstructs["kinda_float"]["body"], test_namespace)
        kinda_float = test_namespace["kinda_float"]

        # Test with scientific notation
        with patch("random.uniform", return_value=0.0):  # No drift for easier testing
            with patch("kinda.personality.chaos_float_drift_range", return_value=(-0.5, 0.5)):
                result = kinda_float(1.23e-4)
                assert isinstance(result, float)
                assert result == 1.23e-4

                result = kinda_float("6.02e23")
                assert isinstance(result, float)
                assert result == 6.02e23

    def test_kinda_float_with_invalid_string(self):
        """Test kinda_float with non-numeric string"""
        test_namespace = {}
        exec(KindaPythonConstructs["kinda_float"]["body"], test_namespace)
        kinda_float = test_namespace["kinda_float"]

        # Test with invalid string should return random float
        with patch("random.uniform", return_value=5.0):
            with patch("kinda.personality.chaos_float_drift_range", return_value=(-0.5, 0.5)):
                result = kinda_float("not_a_number")
                assert isinstance(result, float)
                assert result == 5.0

    def test_kinda_float_drift_application(self):
        """Test that drift is properly applied"""
        test_namespace = {}
        exec(KindaPythonConstructs["kinda_float"]["body"], test_namespace)
        kinda_float = test_namespace["kinda_float"]

        # Test positive drift
        with patch("random.uniform", return_value=0.3):
            with patch("kinda.personality.chaos_float_drift_range", return_value=(-0.5, 0.5)):
                result = kinda_float(10.0)
                assert result == 10.3

        # Test negative drift
        with patch("random.uniform", return_value=-0.2):
            with patch("kinda.personality.chaos_float_drift_range", return_value=(-0.5, 0.5)):
                result = kinda_float(10.0)
                assert result == 9.8

    def test_kinda_float_zero_handling(self):
        """Test kinda_float with zero values"""
        test_namespace = {}
        exec(KindaPythonConstructs["kinda_float"]["body"], test_namespace)
        kinda_float = test_namespace["kinda_float"]

        # Test with zero
        with patch("random.uniform", return_value=0.1):
            with patch("kinda.personality.chaos_float_drift_range", return_value=(-0.5, 0.5)):
                result = kinda_float(0.0)
                assert isinstance(result, float)
                assert result == 0.1

        # Test with negative zero
        with patch("random.uniform", return_value=-0.1):
            with patch("kinda.personality.chaos_float_drift_range", return_value=(-0.5, 0.5)):
                result = kinda_float(-0.0)
                assert isinstance(result, float)
                assert result == -0.1

    def test_kinda_float_error_handling(self):
        """Test error handling in kinda_float"""
        test_namespace = {}
        exec(KindaPythonConstructs["kinda_float"]["body"], test_namespace)
        kinda_float = test_namespace["kinda_float"]

        # Test with problematic value that causes exception
        with patch(
            "kinda.personality.chaos_float_drift_range", side_effect=Exception("Test error")
        ):
            with patch("random.uniform", return_value=5.0):
                result = kinda_float(3.14)
                assert isinstance(result, float)
                assert result == 5.0  # Should use fallback


class TestKindaFloatPersonalityIntegration:
    """Test personality system integration"""

    def setUp(self):
        """Set up clean personality state"""
        PersonalityContext._instance = None

    def tearDown(self):
        """Clean up personality state"""
        PersonalityContext._instance = None

    def test_reliable_personality_minimal_drift(self):
        """Test reliable personality has minimal float drift"""
        PersonalityContext.set_mood("reliable")
        personality = PersonalityContext.get_instance()

        drift_min, drift_max = personality.get_float_drift_range()
        assert (
            drift_min >= -0.1
        ), f"Reliable personality should have minimal drift, got min={drift_min}"
        assert (
            drift_max <= 0.1
        ), f"Reliable personality should have minimal drift, got max={drift_max}"

    def test_chaotic_personality_high_drift(self):
        """Test chaotic personality has high float drift"""
        PersonalityContext.set_mood("chaotic")
        personality = PersonalityContext.get_instance()

        drift_min, drift_max = personality.get_float_drift_range()
        assert drift_min <= -1.0, f"Chaotic personality should have high drift, got min={drift_min}"
        assert drift_max >= 1.0, f"Chaotic personality should have high drift, got max={drift_max}"

    def test_drift_with_instability(self):
        """Test that instability affects drift range through chaos amplifier"""
        PersonalityContext.set_mood("playful")
        personality = PersonalityContext.get_instance()

        # Start with base drift range
        base_min, base_max = personality.get_float_drift_range()

        # Add instability which affects chaos amplifier behavior
        personality.instability_level = 0.5
        # Note: instability affects probabilities, not directly drift ranges in current implementation
        # This tests that the system handles instability without crashing
        unstable_min, unstable_max = personality.get_float_drift_range()

        assert isinstance(unstable_min, float)
        assert isinstance(unstable_max, float)
        assert unstable_min < unstable_max

    def test_personality_profiles_have_float_drift_range(self):
        """Test that all personality profiles define float_drift_range"""
        for profile_name, profile in PERSONALITY_PROFILES.items():
            assert hasattr(
                profile, "float_drift_range"
            ), f"Profile '{profile_name}' missing float_drift_range"
            assert isinstance(
                profile.float_drift_range, tuple
            ), f"Profile '{profile_name}' float_drift_range not tuple"
            assert (
                len(profile.float_drift_range) == 2
            ), f"Profile '{profile_name}' float_drift_range not length 2"
            min_val, max_val = profile.float_drift_range
            assert isinstance(
                min_val, (int, float)
            ), f"Profile '{profile_name}' drift min not numeric"
            assert isinstance(
                max_val, (int, float)
            ), f"Profile '{profile_name}' drift max not numeric"
            assert (
                min_val <= max_val
            ), f"Profile '{profile_name}' drift range invalid: {profile.float_drift_range}"


class TestKindaFloatIntegrationWithOtherConstructs:
    """Test integration with other kinda-lang constructs"""

    def test_kinda_float_with_ish_comparison(self):
        """Test kinda float works with ~ish comparisons"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".kinda", delete=False) as f:
            f.write("~kinda float pi = 3.14159;\n")
            f.write("result = pi ~ish 3.14;\n")
            temp_file = f.name

        try:
            result = transform_file(temp_file)
            assert "pi = kinda_float(3.14159)" in result
            assert "ish_comparison(" in result
        finally:
            Path(temp_file).unlink()

    def test_kinda_float_with_conditional_constructs(self):
        """Test kinda float with ~sometimes, ~maybe, ~probably"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".kinda", delete=False) as f:
            f.write("~kinda float threshold = 0.5;\n")
            f.write("~sometimes (threshold > 0) {\n")
            f.write("    ~sorta print('threshold is positive');\n")
            f.write("}\n")
            temp_file = f.name

        try:
            result = transform_file(temp_file)
            assert "threshold = kinda_float(0.5)" in result
            assert "if sometimes(threshold > 0):" in result
        finally:
            Path(temp_file).unlink()

    def test_kinda_float_with_welp_fallback(self):
        """Test kinda float with ~welp fallback"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".kinda", delete=False) as f:
            f.write("~kinda float value = risky_calculation() ~welp 0.0;\n")
            temp_file = f.name

        try:
            result = transform_file(temp_file)
            assert "kinda_float(" in result
            assert "welp_fallback(" in result
        finally:
            Path(temp_file).unlink()

    def test_kinda_float_with_kinda_int_interaction(self):
        """Test kinda float interactions with kinda int"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".kinda", delete=False) as f:
            f.write("~kinda float rate = 2.5;\n")
            f.write("~kinda int count = 10;\n")
            f.write("total = rate * count;\n")
            f.write("~sorta print('total:', total);\n")
            temp_file = f.name

        try:
            result = transform_file(temp_file)
            assert "rate = kinda_float(2.5)" in result
            assert "count = kinda_int(10)" in result
            assert "total = rate * count" in result
        finally:
            Path(temp_file).unlink()


class TestKindaFloatEdgeCases:
    """Test edge cases and error scenarios"""

    def test_kinda_float_with_infinity(self):
        """Test kinda_float with infinity values"""
        test_namespace = {}
        exec(KindaPythonConstructs["kinda_float"]["body"], test_namespace)
        kinda_float = test_namespace["kinda_float"]

        # Test with positive infinity
        with patch("random.uniform", return_value=0.0):
            with patch("kinda.personality.chaos_float_drift_range", return_value=(-0.5, 0.5)):
                result = kinda_float(float("inf"))
                assert math.isinf(result)

        # Test with negative infinity
        with patch("random.uniform", return_value=0.0):
            with patch("kinda.personality.chaos_float_drift_range", return_value=(-0.5, 0.5)):
                result = kinda_float(float("-inf"))
                assert math.isinf(result)

    def test_kinda_float_with_nan(self):
        """Test kinda_float with NaN values"""
        test_namespace = {}
        exec(KindaPythonConstructs["kinda_float"]["body"], test_namespace)
        kinda_float = test_namespace["kinda_float"]

        # Test with NaN - should handle gracefully
        with patch("random.uniform", return_value=0.0):
            with patch("kinda.personality.chaos_float_drift_range", return_value=(-0.5, 0.5)):
                result = kinda_float(float("nan"))
                # NaN + anything is still NaN
                assert math.isnan(result)

    def test_kinda_float_very_large_numbers(self):
        """Test kinda_float with very large numbers"""
        test_namespace = {}
        exec(KindaPythonConstructs["kinda_float"]["body"], test_namespace)
        kinda_float = test_namespace["kinda_float"]

        # Test with very large number
        large_num = 1.23e100
        with patch("random.uniform", return_value=0.1):
            with patch("kinda.personality.chaos_float_drift_range", return_value=(-0.5, 0.5)):
                result = kinda_float(large_num)
                assert isinstance(result, float)
                assert abs(result - large_num) / large_num < 1e-99  # Relative error should be tiny

    def test_kinda_float_very_small_numbers(self):
        """Test kinda_float with very small numbers"""
        test_namespace = {}
        exec(KindaPythonConstructs["kinda_float"]["body"], test_namespace)
        kinda_float = test_namespace["kinda_float"]

        # Test with very small number
        small_num = 1.23e-100
        with patch("random.uniform", return_value=1e-101):
            with patch("kinda.personality.chaos_float_drift_range", return_value=(-1e-100, 1e-100)):
                result = kinda_float(small_num)
                assert isinstance(result, float)
                assert result > 0  # Should still be positive

    def test_kinda_float_precision_handling(self):
        """Test floating-point precision considerations"""
        test_namespace = {}
        exec(KindaPythonConstructs["kinda_float"]["body"], test_namespace)
        kinda_float = test_namespace["kinda_float"]

        # Test that we maintain reasonable precision
        precision_test_val = 0.1 + 0.2  # This is 0.30000000000000004 in Python
        with patch("random.uniform", return_value=0.0):  # No drift
            with patch("kinda.personality.chaos_float_drift_range", return_value=(-0.5, 0.5)):
                result = kinda_float(precision_test_val)
                assert isinstance(result, float)
                assert abs(result - precision_test_val) < 1e-10

    def test_invalid_syntax_patterns(self):
        """Test patterns that should NOT match kinda_float"""
        invalid_patterns = [
            "~kinda float;",  # No variable or value
            "~kinda float x;",  # No assignment
            "kinda float x = 3.14;",  # Missing ~
            "~kinda float = 3.14;",  # Missing variable name
            "~kinda double x = 3.14;",  # Wrong keyword
        ]

        for pattern in invalid_patterns:
            construct_type, groups = match_python_construct(pattern)
            assert construct_type != "kinda_float", f"Should not match: {pattern}"

    def test_kinda_float_bounds_checking(self):
        """Test drift bounds are properly applied"""
        from kinda.personality import PersonalityContext

        PersonalityContext._instance = None
        personality = PersonalityContext.get_instance()

        # Test maximum bounds
        # With default chaos_level=5, chaos_multiplier=1.1, so combined = 2.0 * 1.1 = 2.2
        personality.profile.float_drift_range = (-100.0, 100.0)
        personality.profile.chaos_amplifier = 2.0
        drift_min, drift_max = personality.get_float_drift_range()
        expected_min = -100.0 * 2.0 * 1.1  # -220.0
        expected_max = 100.0 * 2.0 * 1.1   # 220.0
        assert abs(drift_min - expected_min) < 1e-10, f"Expected {expected_min}, got {drift_min}"
        assert abs(drift_max - expected_max) < 1e-10, f"Expected {expected_max}, got {drift_max}"

        # Test minimum bounds (should be able to handle small ranges)
        # With chaos_level=5, chaos_multiplier=1.1, so combined = 0.1 * 1.1 = 0.11
        personality.profile.float_drift_range = (-0.001, 0.001)
        personality.profile.chaos_amplifier = 0.1
        drift_min, drift_max = personality.get_float_drift_range()
        expected_min = -0.001 * 0.1 * 1.1  # -0.00011
        expected_max = 0.001 * 0.1 * 1.1   # 0.00011
        assert abs(drift_min - expected_min) < 1e-10, f"Expected {expected_min}, got {drift_min}"
        assert abs(drift_max - expected_max) < 1e-10, f"Expected {expected_max}, got {drift_max}"


class TestKindaFloatMathematicalOperations:
    """Test kinda_float with various mathematical operations"""

    def test_kinda_float_arithmetic_operations(self):
        """Test arithmetic operations with kinda float values"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".kinda", delete=False) as f:
            f.write("~kinda float a = 3.5;\n")
            f.write("~kinda float b = 2.0;\n")
            f.write("sum_val = a + b;\n")
            f.write("diff_val = a - b;\n")
            f.write("prod_val = a * b;\n")
            f.write("quot_val = a / b;\n")
            f.write("~sorta print('Results:', sum_val, diff_val, prod_val, quot_val);\n")
            temp_file = f.name

        try:
            result = transform_file(temp_file)
            assert "a = kinda_float(3.5)" in result
            assert "b = kinda_float(2.0)" in result
            assert "sum_val = a + b" in result
            assert "diff_val = a - b" in result
            assert "prod_val = a * b" in result
            assert "quot_val = a / b" in result
        finally:
            Path(temp_file).unlink()

    def test_kinda_float_comparison_operations(self):
        """Test comparison operations with kinda float"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".kinda", delete=False) as f:
            f.write("~kinda float value = 5.0;\n")
            f.write("is_positive = value > 0;\n")
            f.write("is_equal = value == 5.0;\n")
            f.write("is_ish = value ~ish 5.0;\n")
            temp_file = f.name

        try:
            result = transform_file(temp_file)
            assert "value = kinda_float(5.0)" in result
            assert "is_positive = value > 0" in result
            assert "is_equal = value == 5.0" in result
            assert "ish_comparison(" in result
        finally:
            Path(temp_file).unlink()

    def test_kinda_float_mathematical_functions(self):
        """Test kinda float with mathematical functions"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".kinda", delete=False) as f:
            f.write("import math;\n")
            f.write("~kinda float angle = 1.57;\n")
            f.write("sin_val = math.sin(angle);\n")
            f.write("cos_val = math.cos(angle);\n")
            f.write("~sorta print('sin:', sin_val, 'cos:', cos_val);\n")
            temp_file = f.name

        try:
            result = transform_file(temp_file)
            assert "angle = kinda_float(1.57)" in result
            assert "sin_val = math.sin(angle)" in result
            assert "cos_val = math.cos(angle)" in result
        finally:
            Path(temp_file).unlink()


class TestKindaFloatSpecialValues:
    """Test kinda_float with special floating-point values"""

    def test_kinda_float_with_pi_approximation(self):
        """Test kinda_float with pi-like values"""
        test_namespace = {}
        exec(KindaPythonConstructs["kinda_float"]["body"], test_namespace)
        kinda_float = test_namespace["kinda_float"]

        pi_approx = 3.14159
        with patch("random.uniform", return_value=0.01):  # Small drift
            with patch("kinda.personality.chaos_float_drift_range", return_value=(-0.1, 0.1)):
                result = kinda_float(pi_approx)
                assert isinstance(result, float)
                assert abs(result - (pi_approx + 0.01)) < 1e-10

    def test_kinda_float_with_e_approximation(self):
        """Test kinda_float with e-like values"""
        test_namespace = {}
        exec(KindaPythonConstructs["kinda_float"]["body"], test_namespace)
        kinda_float = test_namespace["kinda_float"]

        e_approx = 2.71828
        with patch("random.uniform", return_value=-0.005):  # Small negative drift
            with patch("kinda.personality.chaos_float_drift_range", return_value=(-0.1, 0.1)):
                result = kinda_float(e_approx)
                assert isinstance(result, float)
                assert abs(result - (e_approx - 0.005)) < 1e-10

    def test_kinda_float_fractional_values(self):
        """Test kinda_float with common fractional values"""
        test_namespace = {}
        exec(KindaPythonConstructs["kinda_float"]["body"], test_namespace)
        kinda_float = test_namespace["kinda_float"]

        # Test 1/3
        one_third = 1.0 / 3.0
        with patch("random.uniform", return_value=0.0):  # No drift for precision test
            with patch("kinda.personality.chaos_float_drift_range", return_value=(-0.1, 0.1)):
                result = kinda_float(one_third)
                assert isinstance(result, float)
                assert abs(result - one_third) < 1e-15

        # Test 1/7
        one_seventh = 1.0 / 7.0
        with patch("random.uniform", return_value=0.0):  # No drift for precision test
            with patch("kinda.personality.chaos_float_drift_range", return_value=(-0.1, 0.1)):
                result = kinda_float(one_seventh)
                assert isinstance(result, float)
                assert abs(result - one_seventh) < 1e-15


class TestKindaFloatDriftBehavior:
    """Test specific drift behavior patterns"""

    def test_drift_maintains_sign_for_small_values(self):
        """Test that drift doesn't inappropriately flip signs for small values"""
        test_namespace = {}
        exec(KindaPythonConstructs["kinda_float"]["body"], test_namespace)
        kinda_float = test_namespace["kinda_float"]

        # Small positive value shouldn't become negative with reasonable drift
        with patch("random.uniform", return_value=0.1):  # Positive drift
            with patch("kinda.personality.chaos_float_drift_range", return_value=(-0.5, 0.5)):
                result = kinda_float(0.2)
                assert result > 0, f"Small positive value became negative: {result}"

    def test_drift_can_flip_signs_for_very_small_values(self):
        """Test that drift can flip signs for very small values (expected behavior)"""
        test_namespace = {}
        exec(KindaPythonConstructs["kinda_float"]["body"], test_namespace)
        kinda_float = test_namespace["kinda_float"]

        # Very small positive value can become negative with large enough drift
        with patch("random.uniform", return_value=-0.4):  # Large negative drift
            with patch("kinda.personality.chaos_float_drift_range", return_value=(-0.5, 0.5)):
                result = kinda_float(0.1)
                assert result < 0, f"Expected sign flip but got: {result}"

    def test_multiple_calls_produce_different_results(self):
        """Test that multiple calls with same input produce different results due to drift"""
        test_namespace = {}
        exec(KindaPythonConstructs["kinda_float"]["body"], test_namespace)
        kinda_float = test_namespace["kinda_float"]

        # Multiple calls should produce different results
        results = []
        for i in range(10):
            with patch("kinda.personality.chaos_float_drift_range", return_value=(-1.0, 1.0)):
                result = kinda_float(5.0)
                results.append(result)

        # Should have some variation (not all identical)
        unique_results = set(results)
        assert len(unique_results) > 1, f"All results were identical: {results}"

    def test_drift_range_scaling_with_chaos_amplifier(self):
        """Test that chaos amplifier properly scales drift range"""
        from kinda.personality import PersonalityContext

        PersonalityContext._instance = None
        personality = PersonalityContext.get_instance()

        # Test with amplifier = 2.0 (double the drift)
        # With default chaos_level=5, chaos_multiplier=1.1, so combined = 2.0 * 1.1 = 2.2
        personality.profile.float_drift_range = (-1.0, 1.0)
        personality.profile.chaos_amplifier = 2.0
        drift_min, drift_max = personality.get_float_drift_range()
        expected_min = -1.0 * 2.0 * 1.1  # -2.2
        expected_max = 1.0 * 2.0 * 1.1   # 2.2
        assert abs(drift_min - expected_min) < 1e-10, f"Expected {expected_min}, got {drift_min}"
        assert abs(drift_max - expected_max) < 1e-10, f"Expected {expected_max}, got {drift_max}"

        # Test with amplifier = 0.5 (half the drift)
        # With chaos_level=5, chaos_multiplier=1.1, so combined = 0.5 * 1.1 = 0.55
        personality.profile.chaos_amplifier = 0.5
        drift_min, drift_max = personality.get_float_drift_range()
        expected_min = -1.0 * 0.5 * 1.1  # -0.55
        expected_max = 1.0 * 0.5 * 1.1   # 0.55
        assert abs(drift_min - expected_min) < 1e-10, f"Expected {expected_min}, got {drift_min}"
        assert abs(drift_max - expected_max) < 1e-10, f"Expected {expected_max}, got {drift_max}"


if __name__ == "__main__":
    pytest.main([__file__])
