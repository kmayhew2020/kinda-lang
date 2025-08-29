#!/usr/bin/env python3

import pytest
from unittest.mock import patch
import tempfile
from pathlib import Path

# Import test modules
from kinda.grammar.python.matchers import find_ish_constructs, match_python_construct
from kinda.langs.python.transformer import transform_line, _transform_ish_constructs, transform_file


class TestIshMatching:
    """Test pattern matching for ~ish constructs."""

    def test_find_ish_value_patterns(self):
        """Test finding ~ish value patterns."""
        patterns = find_ish_constructs("x = 42~ish")
        assert len(patterns) == 1
        assert patterns[0][0] == "ish_value"  # construct type
        assert patterns[0][1].group() == "42~ish"  # matched pattern

    def test_find_ish_comparison_patterns(self):
        """Test finding ~ish comparison patterns."""
        patterns = find_ish_constructs("if score ~ish 100:")
        assert len(patterns) == 1
        assert patterns[0][0] == "ish_comparison"  # construct type
        assert patterns[0][1].group() == "score ~ish 100"  # matched pattern


class TestIshTransformation:
    """Test transformation of ~ish constructs."""

    def test_transform_ish_value(self):
        """Test transformation of ~ish values."""
        result = transform_line("x = 42~ish")
        assert isinstance(result, list)
        assert "ish_value(42)" in result[0]

    def test_transform_ish_comparison(self):
        """Test transformation of ~ish comparisons."""
        result = transform_line("if score ~ish 100:")
        assert isinstance(result, list)
        assert "ish_comparison(score, 100)" in result[0]


class TestIshIntegration:
    """Test ~ish construct integration with existing features."""

    def test_ish_with_other_constructs(self):
        """Test ~ish working with other kinda constructs."""
        result = transform_line("~sorta print(42~ish)")
        assert isinstance(result, list)
        # Should transform both ~sorta print AND ~ish
        assert "sorta_print" in result[0]
        assert "ish_value(42)" in result[0]

    def test_ish_in_expressions(self):
        """Test ~ish in complex expressions."""
        result = transform_line("result = x + 42~ish - y")
        assert isinstance(result, list)
        assert "ish_value(42)" in result[0]

    def test_mixed_constructs_same_line(self):
        """Test mixed ~ish and main constructs on same line."""
        result = transform_line("    ~sorta print('value:', 42~ish)")
        assert isinstance(result, list)
        assert "sorta_print" in result[0]
        assert "ish_value(42)" in result[0]
        # Should preserve indentation
        assert result[0].startswith("    ")

    def test_ish_inside_f_strings(self):
        """Test that ~ish inside f-strings is NOT transformed."""
        result = transform_line('print(f"Score {score} is ~ish equal to {target}")')
        assert isinstance(result, list)
        # The ~ish inside the f-string should remain literal
        assert "is ~ish equal to" in result[0]
        # Should NOT contain ish_comparison function call
        assert "ish_comparison" not in result[0]

    def test_ish_inside_regular_strings(self):
        """Test that ~ish inside regular strings is NOT transformed."""
        result = transform_line('print("Value is 42~ish")')
        assert isinstance(result, list)
        # The ~ish inside the string should remain literal
        assert "42~ish" in result[0]
        # Should NOT contain ish_value function call
        assert "ish_value" not in result[0]

    def test_ish_comparison_with_ish_value(self):
        """Test complex nested ish constructs."""
        result = transform_line("if score ~ish 100~ish:")
        assert isinstance(result, list)
        # Should transform to nested function calls
        assert "ish_comparison(score, ish_value(100))" in result[0]

    def test_multiple_ish_constructs(self):
        """Test multiple ~ish constructs on same line."""
        result = transform_line("result = 42~ish + score ~ish 100")
        assert isinstance(result, list)
        assert "ish_value(42)" in result[0]
        assert "ish_comparison(score, 100)" in result[0]


class TestIshFileTransformation:
    """Test complete file transformation with ~ish constructs."""

    def test_python_style_indented_blocks(self):
        """Test ~sometimes with Python-style indented blocks."""
        knda_content = """~sometimes():
    ~sorta print("hello", 42~ish)
    x = 100~ish

print("done")"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".knda", delete=False) as f:
            f.write(knda_content)
            temp_path = Path(f.name)

        try:
            result = transform_file(temp_path)

            # Check that sorta_print is imported
            assert "from kinda.langs.python.runtime.fuzzy import" in result
            assert "sorta_print" in result
            assert "ish_value" in result
            assert "sometimes" in result

            # Check proper transformation
            lines = result.split("\n")
            # Find the transformed lines
            transformed_lines = [line for line in lines if not line.startswith("from ")]
            combined = "\n".join(transformed_lines)

            assert "if sometimes():" in combined
            assert "sorta_print(" in combined
            assert "ish_value(42)" in combined
            assert "ish_value(100)" in combined
            assert 'print("done")' in combined

        finally:
            temp_path.unlink()

    def test_mixed_constructs_in_file(self):
        """Test file with mixed ~ish and other constructs."""
        knda_content = """# Test mixed constructs
score = 98
if score ~ish 100:
    print(f"Score {score} is ~ish equal to 100")
    ~sorta print("Close enough!", 42~ish)

result = 50~ish"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".knda", delete=False) as f:
            f.write(knda_content)
            temp_path = Path(f.name)

        try:
            result = transform_file(temp_path)

            # Check imports
            assert "ish_comparison" in result
            assert "ish_value" in result
            assert "sorta_print" in result

            # Check transformations
            assert "ish_comparison(score, 100)" in result
            assert "is ~ish equal to 100" in result  # f-string preserved
            assert "sorta_print(" in result
            assert "ish_value(42)" in result
            assert "ish_value(50)" in result

        finally:
            temp_path.unlink()

    def test_string_literal_preservation(self):
        """Test that ~ish in strings is preserved."""
        knda_content = """print("This 42~ish should not transform")
print(f"Score ~ish comparison should stay")
x = 42~ish  # This should transform"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".knda", delete=False) as f:
            f.write(knda_content)
            temp_path = Path(f.name)

        try:
            result = transform_file(temp_path)

            # The string literals should be preserved
            assert '"This 42~ish should not transform"' in result
            assert '"Score ~ish comparison should stay"' in result
            # But the actual construct should be transformed
            assert "ish_value(42)" in result

        finally:
            temp_path.unlink()
