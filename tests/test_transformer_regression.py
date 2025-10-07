"""
Regression tests for transformer issues found in demo files.
These tests ensure specific syntax patterns that were problematic in Issues #134 & #135 continue to work.
"""

import pytest
from kinda.langs.python.transformer import transform_line


class TestDemoTransformerRegressions:
    """Test cases for transformer bugs found in demo files."""

    def test_inline_sometimes_true_issue_134(self):
        """Test that ~sometimes True is correctly preserved in statistical assertions (Issue #134)."""
        # The specific pattern from statistical_testing_demo.py.knda line 12
        # Statistical assertions should preserve kinda syntax for proper statistical testing
        result = transform_line("assert_eventually(~sometimes True, timeout=3.0, confidence=0.95)")
        expected = ["assert_eventually(~sometimes True, timeout=3.0, confidence=0.95)"]
        assert result == expected

    def test_inline_rarely_true_issue_134(self):
        """Test that ~rarely True is correctly preserved in statistical assertions (Issue #134)."""
        # Statistical assertions should preserve kinda syntax for proper statistical testing
        result = transform_line("assert_eventually(~rarely True, timeout=5.0)")
        expected = ["assert_eventually(~rarely True, timeout=5.0)"]
        assert result == expected

    def test_inline_maybe_false_issue_134(self):
        """Test that ~maybe False is correctly transformed in inline contexts (Issue #134)."""
        result = transform_line("some_function(~maybe False)")
        expected = ["some_function(maybe(False))"]
        assert result == expected

    def test_kinda_mood_with_variable_issue_135(self):
        """Test that ~kinda mood {variable} is correctly transformed (Issue #135)."""
        # The specific pattern from 03_fuzzy_load_testing.knda line 68
        result = transform_line("~kinda mood {session_personality}")
        expected = ["kinda_mood(session_personality)"]
        assert result == expected

    def test_kinda_mood_with_literal_issue_135(self):
        """Test that ~kinda mood literal still works (Issue #135)."""
        result = transform_line("~kinda mood playful")
        expected = ["kinda_mood('playful')"]
        assert result == expected

    def test_maybe_for_with_tuple_unpacking_issue_135(self):
        """Test that ~maybe_for with tuple unpacking works (Issue #135)."""
        # The specific pattern from 03_fuzzy_load_testing.knda line 90
        result = transform_line("~maybe_for action_name, endpoint in user_actions:")
        expected = ["for action_name, endpoint in user_actions:"]
        assert result == expected

    def test_maybe_for_with_single_variable_issue_135(self):
        """Test that ~maybe_for with single variable still works (Issue #135)."""
        result = transform_line("~maybe_for item in items:")
        expected = ["for item in items:"]
        assert result == expected

    def test_single_line_conditional_blocks(self):
        """Test that single-line conditional blocks work correctly."""
        result = transform_line("~sometimes () { test_counter = test_counter + 1 }")
        expected = ["if sometimes(): test_counter = test_counter + 1"]
        assert result == expected

    def test_inline_constructs_skip_strings(self):
        """Test that inline transformations don't affect text inside strings."""
        result = transform_line('print("~sometimes eventually")')
        expected = ['print("~sometimes eventually")']
        assert result == expected

    def test_complex_welp_line_issue_134(self):
        """Test complex line with welp, assert_eventually, and sorta print (Issue #134)."""
        # The specific pattern from statistical_testing_demo.py.knda line 102
        line = '~assert_eventually (False, timeout=0.5, confidence=0.95) ~welp ~sorta print("Expected failure!")'
        result = transform_line(line)
        expected = [
            'welp_fallback(lambda: assert_eventually(False, timeout=0.5, confidence=0.95), sorta_print("Expected failure!"))'
        ]
        assert result == expected

    def test_nested_inline_constructs(self):
        """Test that nested inline constructs are handled correctly."""
        result = transform_line("func(~sometimes True, ~maybe False)")
        expected = ["func(sometimes(True), maybe(False))"]
        assert result == expected

    def test_inline_assert_eventually_basic(self):
        """Test basic inline ~assert_eventually transformation."""
        result = transform_line("~assert_eventually (condition, timeout=2.0)")
        expected = ["assert_eventually(condition, timeout=2.0)"]
        assert result == expected

    def test_inline_sorta_print_basic(self):
        """Test basic inline ~sorta print transformation."""
        result = transform_line('~sorta print("hello world")')
        expected = ['sorta_print("hello world")']
        assert result == expected


class TestIssue105WelpPrefixSyntax:
    """Regression tests for Issue #105: ~welp construct prefix syntax not transformed."""

    def test_welp_infix_syntax(self):
        """Test that infix syntax (expr ~welp fallback) works."""
        result = transform_line("result = risky_function() ~welp 42")
        expected = ["result = welp_fallback(lambda: risky_function(), 42)"]
        assert result == expected

    def test_welp_prefix_syntax(self):
        """Test that prefix syntax (~welp expr fallback) works (Issue #105)."""
        result = transform_line("result = ~welp risky_function() 42")
        expected = ["result = welp_fallback(lambda: risky_function(), 42)"]
        assert result == expected

    def test_welp_prefix_with_complex_expression(self):
        """Test prefix syntax with complex expressions."""
        result = transform_line("value = ~welp get_data(x, y) default_value")
        expected = ["value = welp_fallback(lambda: get_data(x, y), default_value)"]
        assert result == expected

    def test_welp_prefix_in_function_call(self):
        """Test prefix syntax as function argument."""
        result = transform_line("process(~welp fetch() None)")
        expected = ["process(welp_fallback(lambda: fetch(), None))"]
        assert result == expected


class TestIssue107NestedConditionalIndentation:
    """Regression tests for Issue #107: Invalid indentation in nested conditionals with else blocks."""

    def test_nested_conditionals_with_else_blocks(self):
        """Test that nested conditionals with else blocks generate correct indentation (Issue #107)."""
        from pathlib import Path
        from kinda.langs.python.transformer import transform_file
        import tempfile

        # Create test file with nested conditionals
        kinda_code = """~kinda int score = 85
~sometimes (score > 80) {
    ~maybe (score > 90) {
        ~sorta print("Excellent!")
    } {
        ~sorta print("Good!")
    }
} {
    ~rarely (score > 70) {
        ~sorta print("Okay")
    }
}
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py.knda", delete=False) as f:
            f.write(kinda_code)
            temp_path = Path(f.name)

        try:
            result = transform_file(temp_path)

            # Verify the code compiles without IndentationError
            compile(result, "<test>", "exec")

            # Verify specific indentation patterns
            lines = result.split("\n")

            # Find the inner if and inner else
            inner_if_line = next((i, l) for i, l in enumerate(lines) if "if maybe" in l)
            inner_else_line = next(
                (i, l) for i, l in enumerate(lines) if i > inner_if_line[0] and l.strip() == "else:"
            )

            # Extract indentation (count leading spaces)
            inner_if_indent = len(inner_if_line[1]) - len(inner_if_line[1].lstrip())
            inner_else_indent = len(inner_else_line[1]) - len(inner_else_line[1].lstrip())

            # Inner if and inner else should have same indentation
            assert (
                inner_if_indent == inner_else_indent
            ), f"Inner if at {inner_if_indent} spaces, but inner else at {inner_else_indent} spaces"
        finally:
            temp_path.unlink()

    def test_double_nested_conditionals(self):
        """Test deeply nested conditionals maintain correct indentation."""
        from pathlib import Path
        from kinda.langs.python.transformer import transform_file
        import tempfile

        kinda_code = """~sometimes (True) {
    ~maybe (True) {
        ~rarely (True) {
            ~sorta print("Deep!")
        } {
            ~sorta print("Not so deep")
        }
    } {
        ~sorta print("Middle")
    }
} {
    ~sorta print("Shallow")
}
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py.knda", delete=False) as f:
            f.write(kinda_code)
            temp_path = Path(f.name)

        try:
            result = transform_file(temp_path)
            # Should compile without IndentationError
            compile(result, "<test>", "exec")
        finally:
            temp_path.unlink()
