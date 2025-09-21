"""
Regression tests for transformer issues found in demo files.
These tests ensure specific syntax patterns that were problematic in Issues #134 & #135 continue to work.
"""

import pytest
from kinda.langs.python.transformer import transform_line


class TestDemoTransformerRegressions:
    """Test cases for transformer bugs found in demo files."""

    def test_inline_sometimes_true_issue_134(self):
        """Test that ~sometimes True is correctly transformed in inline contexts (Issue #134)."""
        # The specific pattern from statistical_testing_demo.py.knda line 12
        result = transform_line("assert_eventually(~sometimes True, timeout=3.0, confidence=0.95)")
        expected = ["assert_eventually(sometimes(True), timeout=3.0, confidence=0.95)"]
        assert result == expected

    def test_inline_rarely_true_issue_134(self):
        """Test that ~rarely True is correctly transformed in inline contexts (Issue #134)."""
        result = transform_line("assert_eventually(~rarely True, timeout=5.0)")
        expected = ["assert_eventually(rarely(True), timeout=5.0)"]
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
