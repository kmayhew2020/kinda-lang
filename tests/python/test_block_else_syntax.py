"""
Comprehensive tests for Issue #79: Block else syntax transformation
Tests the } { else syntax in kinda conditional blocks
"""

import pytest
import tempfile
from pathlib import Path

from kinda.langs.python.transformer import transform_file


class TestBlockElseSyntax:
    """Test block else syntax transformation"""

    def test_sometimes_with_else_block(self):
        """Test ~sometimes with } { else syntax"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".knda", delete=False) as f:
            f.write(
                """~sometimes (True) {
    ~sorta print("if block")
} {
    ~sorta print("else block")
}"""
            )
            temp_path = Path(f.name)

        try:
            result = transform_file(temp_path)

            # Should generate proper Python else syntax
            assert "if sometimes(True):" in result
            assert 'sorta_print("if block")' in result
            assert "else:" in result
            assert 'sorta_print("else block")' in result

            # Should not contain orphaned braces
            assert "} {" not in result

        finally:
            temp_path.unlink()

    def test_maybe_with_else_block(self):
        """Test ~maybe with } { else syntax"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".knda", delete=False) as f:
            f.write(
                """~maybe (condition) {
    ~kinda int x = 10
} {
    x = 5
}"""
            )
            temp_path = Path(f.name)

        try:
            result = transform_file(temp_path)

            # Should generate proper Python else syntax
            assert "if maybe(condition):" in result
            assert "x = kinda_int(10)" in result
            assert "else:" in result
            assert "x = 5" in result

        finally:
            temp_path.unlink()

    def test_nested_conditionals_with_else(self):
        """Test nested conditionals with else blocks"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".knda", delete=False) as f:
            f.write(
                """~sometimes (outer) {
    ~maybe (inner) {
        ~sorta print("nested if")
    } {
        ~sorta print("nested else")
    }
} {
    ~sorta print("outer else")
}"""
            )
            temp_path = Path(f.name)

        try:
            result = transform_file(temp_path)

            # Should handle nested else blocks correctly
            assert "if sometimes(outer):" in result
            assert "if maybe(inner):" in result
            assert 'sorta_print("nested if")' in result
            assert 'sorta_print("nested else")' in result
            assert 'sorta_print("outer else")' in result
            assert result.count("else:") == 2

        finally:
            temp_path.unlink()

    def test_else_with_indented_content(self):
        """Test else block with proper indentation"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".knda", delete=False) as f:
            f.write(
                """~sometimes (check) {
    if True:
        ~sorta print("nested python")
} {
    for i in range(3):
        ~sorta print("loop in else")
}"""
            )
            temp_path = Path(f.name)

        try:
            result = transform_file(temp_path)

            # Should maintain proper indentation in else block
            lines = result.split("\n")
            else_line_idx = next(i for i, line in enumerate(lines) if "else:" in line)

            # Check indentation is correct
            assert lines[else_line_idx].startswith("else:")
            assert "for i in range(3):" in result

        finally:
            temp_path.unlink()

    def test_conditional_without_else_still_works(self):
        """Test that conditionals without else blocks still work"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".knda", delete=False) as f:
            f.write(
                """~sometimes (True) {
    ~sorta print("only if block")
}"""
            )
            temp_path = Path(f.name)

        try:
            result = transform_file(temp_path)

            # Should work normally without else
            assert "if sometimes(True):" in result
            assert 'sorta_print("only if block")' in result
            assert "else:" not in result

        finally:
            temp_path.unlink()

    def test_empty_else_block(self):
        """Test else block with no content"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".knda", delete=False) as f:
            f.write(
                """~sometimes (True) {
    ~sorta print("if block")
} {
}"""
            )
            temp_path = Path(f.name)

        try:
            result = transform_file(temp_path)

            # Should handle empty else block
            assert "if sometimes(True):" in result
            assert "else:" in result

        finally:
            temp_path.unlink()
