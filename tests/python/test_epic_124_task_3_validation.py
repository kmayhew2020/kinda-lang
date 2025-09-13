"""
Epic #124 Task 3 Validation: ~ish Patterns Implementation using ~kinda float + tolerance
Simple validation tests to confirm Task 3 composition requirements are met.
"""

import pytest
from kinda.grammar.python.constructs import KindaPythonConstructs
from kinda.langs.python.transformer import transform_line


class TestEpic124Task3Validation:
    """Validate Epic #124 Task 3 composition implementation."""

    def test_ish_comparison_contains_composition_pattern(self):
        """Test that ish_comparison implementation contains composition elements."""
        # Get the construct definition
        ish_comparison = KindaPythonConstructs["ish_comparison"]

        # Should be documented as Epic #124 Task 3
        assert "Epic #124 Task 3" in ish_comparison["description"]

        # Implementation body should use composition
        body = ish_comparison["body"]

        # Should use ~kinda float for fuzzy tolerance and difference
        assert "kinda_float(tolerance_base)" in body
        assert "kinda_float(abs(left_val - right_val))" in body

        # Should use ~probably for probabilistic result
        assert "probably(base_result)" in body

        # Should use composed fallbacks
        assert "probably(False)" in body  # Error fallback
        assert "maybe(False)" in body  # Exception fallback

    def test_ish_value_contains_composition_pattern(self):
        """Test that ish_value implementation contains composition elements."""
        # Get the construct definition
        ish_value = KindaPythonConstructs["ish_value"]

        # Should be documented as Epic #124 Task 3
        assert "Epic #124 Task 3" in ish_value["description"]

        # Implementation body should use composition
        body = ish_value["body"]

        # Should use ~kinda float for fuzzy adjustments
        assert "kinda_float(0.5)" in body  # adjustment factor
        assert "kinda_float(target_val - val)" in body  # difference

        # Should use ~sometimes for conditional logic
        assert "if sometimes(True):" in body

        # Should use fuzzy fallbacks
        assert "kinda_float(" in body  # Multiple fuzzy operations

    def test_transformation_still_works_correctly(self):
        """Test that transformation works correctly with composed implementation."""
        # Test ish_comparison in conditional
        result = transform_line("if value ~ish 10:")
        assert "if ish_comparison(value, 10):" in result[0]

        # Test ish_value in assignment
        result = transform_line("value ~ish 100")
        assert "value = ish_value(value, 100)" in result[0]

    def test_composition_documentation_clear(self):
        """Test that composition is clearly documented in the implementations."""
        ish_comparison = KindaPythonConstructs["ish_comparison"]
        ish_value = KindaPythonConstructs["ish_value"]

        # Both should reference the task
        assert "Epic #124 Task 3" in ish_comparison["description"]
        assert "Epic #124 Task 3" in ish_value["description"]

        # Should show composition approach
        assert "~kinda float + tolerance" in ish_comparison["description"]
        assert "~kinda float + variance" in ish_value["description"]

        # Implementation should show clear composition
        comp_body = ish_comparison["body"]
        val_body = ish_value["body"]

        # Should explain the composition approach in comments
        assert "Use ~kinda float to add uncertainty to tolerance" in comp_body
        assert "Build ~ish behavior from basic constructs" in comp_body
        assert "Show how ~ish variable modification emerges from simpler constructs" in val_body

    def test_composed_implementations_functional_equivalence(self):
        """Test that composed implementations maintain functional equivalence."""
        # These test cases should all still work the same way
        test_cases = [
            ("value ~ish 10", "ish_value"),
            ("if x ~ish 5:", "ish_comparison"),
            ("result = a ~ish b", "ish_comparison"),
            ("score ~ish target + bonus", "ish_value"),
        ]

        for input_code, expected_function in test_cases:
            result = transform_line(input_code)
            assert len(result) == 1
            assert f"{expected_function}(" in result[0]
