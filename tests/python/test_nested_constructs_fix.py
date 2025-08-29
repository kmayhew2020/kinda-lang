"""
Comprehensive tests for Issue #81: Nested constructs in function arguments
Tests that ~ish constructs with complex expressions are properly transformed
"""

import pytest
import tempfile
from pathlib import Path

from kinda.langs.python.transformer import transform_file


class TestNestedConstructsInArguments:
    """Test nested construct transformation in function arguments"""

    def test_simple_ish_comparison_in_conditional(self):
        """Test basic ~ish comparison in conditional argument"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".knda", delete=False) as f:
            f.write(
                """~kinda int value = 5
~sometimes (value ~ish 10) {
    ~sorta print("simple comparison")
}"""
            )
            temp_path = Path(f.name)

        try:
            result = transform_file(temp_path)

            assert "value = kinda_int(5)" in result
            assert "if sometimes(ish_comparison(value, 10)):" in result
            assert 'sorta_print("simple comparison")' in result

        finally:
            temp_path.unlink()

    def test_ish_comparison_with_arithmetic_expression(self):
        """Test ~ish comparison with arithmetic expressions"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".knda", delete=False) as f:
            f.write(
                """~kinda int a = 5
~kinda int b = 10
~sometimes (a ~ish b + 5 and b ~ish a * 2) {
    ~sorta print("arithmetic expressions")
}"""
            )
            temp_path = Path(f.name)

        try:
            result = transform_file(temp_path)

            # Should properly capture complex expressions
            assert "ish_comparison(a, b + 5)" in result
            assert "ish_comparison(b, a * 2)" in result
            assert "and" in result  # Should maintain logical operator

        finally:
            temp_path.unlink()

    def test_ish_comparison_with_parentheses(self):
        """Test ~ish comparison with parenthesized expressions"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".knda", delete=False) as f:
            f.write(
                """~kinda int x = 10
~kinda int y = 5
~sometimes (x ~ish (y + 3) or y ~ish (x - 2)) {
    ~sorta print("parenthesized expressions")
}"""
            )
            temp_path = Path(f.name)

        try:
            result = transform_file(temp_path)

            # Should handle parentheses correctly
            assert "ish_comparison(x, (y + 3))" in result
            assert "ish_comparison(y, (x - 2))" in result
            assert " or " in result  # Should maintain logical operator

        finally:
            temp_path.unlink()

    def test_multiple_ish_comparisons_with_logical_operators(self):
        """Test multiple ~ish comparisons connected by logical operators"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".knda", delete=False) as f:
            f.write(
                """~kinda int a = 1
~kinda int b = 2
~kinda int c = 3
~sometimes (a ~ish b and b ~ish c or a ~ish c) {
    ~sorta print("multiple comparisons")
}"""
            )
            temp_path = Path(f.name)

        try:
            result = transform_file(temp_path)

            # Each ~ish should be transformed independently
            assert "ish_comparison(a, b)" in result
            assert "ish_comparison(b, c)" in result
            assert "ish_comparison(a, c)" in result
            assert " and " in result
            assert " or " in result

        finally:
            temp_path.unlink()

    def test_nested_ish_in_maybe_conditional(self):
        """Test ~ish constructs in ~maybe conditionals"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".knda", delete=False) as f:
            f.write(
                """~kinda int score = 85
~maybe (score ~ish 100 - 10) {
    ~sorta print("close to perfect")
}"""
            )
            temp_path = Path(f.name)

        try:
            result = transform_file(temp_path)

            # Should transform both maybe and ish_comparison
            assert "if maybe(ish_comparison(score, 100 - 10)):" in result
            assert 'sorta_print("close to perfect")' in result

        finally:
            temp_path.unlink()

    def test_complex_expression_with_multiple_operators(self):
        """Test complex arithmetic expressions with multiple operators"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".knda", delete=False) as f:
            f.write(
                """~kinda int x = 10
~kinda int y = 5
~sometimes (x ~ish y * 2 + 3 - 1) {
    ~sorta print("complex arithmetic")
}"""
            )
            temp_path = Path(f.name)

        try:
            result = transform_file(temp_path)

            # Should capture the full expression
            assert "ish_comparison(x, y * 2 + 3 - 1)" in result

        finally:
            temp_path.unlink()

    def test_ish_comparison_mixed_with_regular_comparison(self):
        """Test ~ish comparison mixed with regular comparison operators"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".knda", delete=False) as f:
            f.write(
                """~kinda int value = 50
~sometimes (value > 30 and value ~ish 45 + 5) {
    ~sorta print("mixed comparisons")
}"""
            )
            temp_path = Path(f.name)

        try:
            result = transform_file(temp_path)

            # Should transform ~ish but leave regular comparison
            assert "value > 30" in result  # Regular comparison unchanged
            assert "ish_comparison(value, 45 + 5)" in result  # ~ish transformed

        finally:
            temp_path.unlink()

    def test_ish_value_still_works(self):
        """Test that ~ish values (not comparisons) still work"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".knda", delete=False) as f:
            f.write(
                """~sometimes (100~ish > 95) {
    ~sorta print("ish value test")
}"""
            )
            temp_path = Path(f.name)

        try:
            result = transform_file(temp_path)

            # Should transform ish_value, not ish_comparison
            assert "ish_value(100)" in result
            # Check that ish_comparison is not used in the logic (only imports)
            assert "ish_comparison(" not in result

        finally:
            temp_path.unlink()

    def test_whitespace_handling(self):
        """Test that various whitespace patterns work correctly"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".knda", delete=False) as f:
            f.write(
                """~kinda int val = 10
~sometimes (val~ish    20+5   and   val   ~ish   30) {
    ~sorta print("whitespace test")
}"""
            )
            temp_path = Path(f.name)

        try:
            result = transform_file(temp_path)

            # Should handle various whitespace patterns
            assert "ish_comparison(val, 20+5)" in result
            assert "ish_comparison(val, 30)" in result

        finally:
            temp_path.unlink()
