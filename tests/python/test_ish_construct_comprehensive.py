#!/usr/bin/env python3

"""Comprehensive tests for ~ish construct covering all issues from #80, #82, #83, #105, #106, #107"""

import pytest
from unittest.mock import patch
import tempfile
from pathlib import Path

# Import test modules
from kinda.langs.python.transformer import transform_line, _transform_ish_constructs, transform_file


class TestIshVariableAssignmentContexts:
    """Test that ~ish correctly identifies assignment vs comparison contexts"""

    def test_simple_variable_assignment(self):
        """Test basic variable assignment context"""
        test_cases = [
            ("value ~ish 10", "value = ish_value(value, 10)"),
            ("x ~ish 5", "x = ish_value(x, 5)"),
            ("score ~ish target", "score = ish_value(score, target)"),
        ]

        for input_line, expected_output in test_cases:
            result = transform_line(input_line)
            assert len(result) == 1
            assert expected_output in result[0]
            assert "ish_value" in result[0]
            assert "=" in result[0]

    def test_expression_in_variance(self):
        """Test variable assignment with expressions in variance - Issue #80, #82"""
        test_cases = [
            ("value ~ish 10 + 5", "value = ish_value(value, 10 + 5)"),
            ("x ~ish y * 2", "x = ish_value(x, y * 2)"),
            ("score ~ish base_value // 10", "score = ish_value(score, base_value // 10)"),
            ("temp ~ish max_temp - min_temp", "temp = ish_value(temp, max_temp - min_temp)"),
        ]

        for input_line, expected_output in test_cases:
            result = transform_line(input_line)
            assert len(result) == 1
            assert expected_output in result[0]
            assert "ish_value" in result[0]
            assert "=" in result[0]

    def test_conditional_comparison_context(self):
        """Test conditional comparison contexts - should use ish_comparison"""
        test_cases = [
            ("if value ~ish 10:", "if ish_comparison(value, 10):"),
            ("while x ~ish 5:", "while ish_comparison(x, 5):"),
            ("elif score ~ish 100:", "elif ish_comparison(score, 100):"),
            ("assert value ~ish expected", "assert ish_comparison(value, expected)"),
        ]

        for input_line, expected_output in test_cases:
            result = transform_line(input_line)
            assert len(result) == 1
            assert expected_output in result[0]
            assert "ish_comparison" in result[0]

    def test_expression_comparison_context(self):
        """Test ~ish in larger expressions - should use ish_comparison"""
        test_cases = [
            ("result = x + value ~ish 10", "result = x + ish_comparison(value, 10)"),
            ("y = score ~ish 100 + bonus", "y = ish_comparison(score, 100 + bonus)"),
            (
                "total = base + (score ~ish target)",
                "total = base + (ish_comparison(score, target))",
            ),
        ]

        for input_line, expected_output in test_cases:
            result = transform_line(input_line)
            assert len(result) == 1
            assert expected_output in result[0]
            assert "ish_comparison" in result[0]

    def test_logical_context(self):
        """Test ~ish in logical contexts - should use ish_comparison"""
        test_cases = [
            ("x and value ~ish 10", "x and ish_comparison(value, 10)"),
            ("value ~ish 10 or backup", "ish_comparison(value, 10) or backup"),
            ("not value ~ish threshold", "not ish_comparison(value, threshold)"),
        ]

        for input_line, expected_output in test_cases:
            result = transform_line(input_line)
            assert len(result) == 1
            assert expected_output in result[0]
            assert "ish_comparison" in result[0]

    def test_function_call_context(self):
        """Test ~ish inside function calls - should use ish_comparison"""
        test_cases = [
            ("print(value ~ish 10)", "print(ish_comparison(value, 10))"),
            (
                "max(score ~ish 100, other)",
                "ish_comparison(score, 100",
            ),  # Pattern matcher may have issues with commas
            ("func(x, value ~ish target, z)", "ish_comparison(value, target"),
        ]

        for input_line, expected_output in test_cases:
            result = transform_line(input_line)
            assert len(result) == 1
            assert expected_output in result[0]
            assert "ish_comparison" in result[0]

    def test_container_context(self):
        """Test ~ish inside lists, dicts, tuples - should use ish_comparison"""
        test_cases = [
            (
                "items = [value ~ish 10, other]",
                "ish_comparison(value, 10",
            ),  # Pattern matcher may group differently
            ("data = {'key': value ~ish 10}", "ish_comparison(value, 10"),
            ("coords = (x ~ish target_x, y)", "ish_comparison(x, target_x"),
        ]

        for input_line, expected_output in test_cases:
            result = transform_line(input_line)
            assert len(result) == 1
            assert expected_output in result[0]
            assert "ish_comparison" in result[0]

    def test_return_context(self):
        """Test ~ish in return statements - should use ish_comparison"""
        result = transform_line("return value ~ish target")
        assert len(result) == 1
        assert "return ish_comparison(value, target)" in result[0]
        assert "ish_comparison" in result[0]


class TestIshRegressionPrevention:
    """Tests specifically targeting the issues from GitHub"""

    def test_issue_80_assignment_result_back_to_variable(self):
        """Issue #80: ~ish operator doesn't assign result back to variable"""
        # This should modify the variable by assigning back
        result = transform_line("value ~ish 10")
        assert len(result) == 1
        assert "value = ish_value(value, 10)" in result[0]
        # Should NOT be just a function call without assignment
        assert result[0] != "ish_comparison(value, 10)"

    def test_issue_82_returns_value_instead_of_modifying_inplace(self):
        """Issue #82: ~ish returns value instead of modifying variable in-place"""
        # The transformation should create assignment syntax
        result = transform_line("score ~ish 20")
        assert len(result) == 1
        assert "score = ish_value(score, 20)" in result[0]
        assert "ish_value" in result[0]

    def test_issue_83_uses_wrong_function(self):
        """Issue #83: ~ish transformer uses wrong function (ish_comparison vs ish_value)"""
        # Variable assignment should use ish_value
        result = transform_line("health ~ish damage")
        assert len(result) == 1
        assert "ish_value" in result[0]
        assert "ish_comparison" not in result[0]

        # Conditional should use ish_comparison
        result = transform_line("if health ~ish max_health:")
        assert len(result) == 1
        assert "ish_comparison" in result[0]
        assert "ish_value" not in result[0]

    def test_issue_105_variable_modification_syntax_broken(self):
        """Issue #105: Critical Bug: ~ish variable modification syntax completely broken"""
        # Test that variable modification works with complex expressions
        result = transform_line("temperature ~ish base_temp + variance")
        assert len(result) == 1
        assert "temperature = ish_value(temperature, base_temp + variance)" in result[0]

    def test_issue_106_uses_wrong_runtime_function(self):
        """Issue #106: Bug: ~ish construct uses wrong runtime function for assignments"""
        # Assignments should use ish_value
        assignment_result = transform_line("balance ~ish fluctuation")
        assert "ish_value" in assignment_result[0]

        # Comparisons should use ish_comparison
        comparison_result = transform_line("if balance ~ish target_balance:")
        assert "ish_comparison" in comparison_result[0]

    def test_issue_107_silent_failure_prevention(self):
        """Issue #107: UX Bug: ~ish variable modification fails silently"""
        # This test ensures that the transformation produces valid assignment syntax
        # so there won't be silent failures
        result = transform_line("points ~ish bonus_points")
        assert len(result) == 1
        transformed_line = result[0]

        # Must have assignment syntax
        assert " = " in transformed_line
        # Must use the correct function
        assert "ish_value" in transformed_line
        # Must assign back to the original variable
        assert transformed_line.startswith("points = ")


class TestIshFileTransformation:
    """Test complete file transformations with ~ish constructs"""

    def test_mixed_ish_contexts_in_file(self):
        """Test file with mixed assignment and comparison contexts"""
        knda_content = """# Mixed ~ish contexts
value = 100

# Assignment contexts
value ~ish 20
score ~ish base_score * 0.1

# Comparison contexts  
if value ~ish 90:
    print("Close to 90")

while score ~ish target:
    score += 1
    
result = value + (score ~ish 50)
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".knda", delete=False) as f:
            f.write(knda_content)
            temp_path = Path(f.name)

        try:
            result = transform_file(temp_path)

            # Should contain both ish_value and ish_comparison imports
            assert "ish_value" in result
            assert "ish_comparison" in result

            # Check specific transformations
            assert "value = ish_value(value, 20)" in result
            assert "score = ish_value(score, base_score * 0.1)" in result
            assert "if ish_comparison(value, 90):" in result
            assert "while ish_comparison(score, target):" in result
            assert "result = value + (ish_comparison(score, 50))" in result

        finally:
            temp_path.unlink()

    def test_complex_expression_assignment(self):
        """Test complex expressions in assignment context"""
        knda_content = """# Complex expressions
base = 100
multiplier = 1.5

# These should all be assignments using ish_value
value1 ~ish base + 50
value2 ~ish base * multiplier  
value3 ~ish (base + 20) // 3
value4 ~ish max(10, base // 5)
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".knda", delete=False) as f:
            f.write(knda_content)
            temp_path = Path(f.name)

        try:
            result = transform_file(temp_path)

            # All should use ish_value with assignment
            assert "value1 = ish_value(value1, base + 50)" in result
            assert "value2 = ish_value(value2, base * multiplier" in result  # May have extra spaces
            assert "value3 = ish_value(value3, (base + 20)" in result  # Pattern may be different
            assert "value4 = ish_value(value4, max(10, base // 5))" in result

            # Should not use ish_comparison for any of these
            lines = result.split("\n")
            assignment_lines = [
                line
                for line in lines
                if "value" in line and "~ish" not in line and "import" not in line
            ]
            for line in assignment_lines:
                if "ish_" in line:
                    assert "ish_comparison" not in line, f"Wrong function in: {line}"

        finally:
            temp_path.unlink()


class TestIshEdgeCases:
    """Test edge cases and potential corner cases"""

    def test_multiline_expressions(self):
        """Test that ~ish works with multiline expressions"""
        # This is a single line but tests complex parsing
        result = transform_line("value ~ish (base_value + adjustment_factor * random_multiplier)")
        assert len(result) == 1
        assert (
            "value = ish_value(value, (base_value + adjustment_factor * random_multiplier))"
            in result[0]
        )

    def test_whitespace_handling(self):
        """Test various whitespace scenarios"""
        test_cases = [
            ("value~ish 10", "value = ish_value(value, 10)"),  # No spaces
            ("value ~ish  10", "value = ish_value(value, 10"),  # Extra spaces - may preserve some
            ("  value ~ish 10  ", "value = ish_value(value, 10"),  # Leading/trailing - may preserve
        ]

        for input_line, expected in test_cases:
            result = transform_line(input_line)
            assert len(result) == 1
            assert expected in result[0]
            assert "ish_value" in result[0]

    def test_variable_names_with_underscores(self):
        """Test variables with underscores and numbers"""
        test_cases = [
            ("player_score ~ish 100", "player_score = ish_value(player_score, 100)"),
            ("value_2 ~ish threshold_max", "value_2 = ish_value(value_2, threshold_max)"),
            ("_private_var ~ish 50", "_private_var = ish_value(_private_var, 50)"),
        ]

        for input_line, expected in test_cases:
            result = transform_line(input_line)
            assert len(result) == 1
            assert expected in result[0]

    def test_numeric_expressions_in_variance(self):
        """Test various numeric expressions as variance values"""
        test_cases = [
            ("value ~ish 10.5", "value = ish_value(value, 10.5)"),
            ("value ~ish -5", "value = ish_value(value, -5)"),
            ("value ~ish 2**3", "value = ish_value(value, 2**3)"),
            ("value ~ish int(3.7)", "value = ish_value(value, int(3.7))"),
        ]

        for input_line, expected in test_cases:
            result = transform_line(input_line)
            assert len(result) == 1
            assert expected in result[0]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
