"""
Test suite for enhanced error messages (Issue #113).

Tests all 9 error scenarios with improved error reporting:
1. Missing braces
2. Invalid operators
3. Unclosed strings
4. Malformed numbers
5. Mismatched parentheses
6. Invalid construct names
7. Wrong argument counts
8. Type mismatches
9. Nesting errors
"""

import pytest
from kinda.exceptions import (
    KindaSyntaxError,
    KindaParseError,
    SourcePosition,
    SourceSnippetExtractor,
    suggest_construct,
    VALID_CONSTRUCTS,
)


class TestSourcePosition:
    """Test SourcePosition class."""

    def test_basic_position(self):
        """Test basic position creation and formatting."""
        pos = SourcePosition(line=10, column=5)
        assert pos.line == 10
        assert pos.column == 5
        assert str(pos) == "line 10, column 5"

    def test_position_with_file(self):
        """Test position with file path."""
        pos = SourcePosition(line=15, column=8, file_path="test.py.knda")
        assert str(pos) == "test.py.knda:15:8"

    def test_position_range(self):
        """Test position range formatting."""
        pos = SourcePosition(line=10, column=5, end_line=12, end_column=10)
        assert pos.to_range_str() == "10:5-12:10"

        pos_with_file = SourcePosition(
            line=10, column=5, file_path="test.py.knda", end_line=12, end_column=10
        )
        assert pos_with_file.to_range_str() == "test.py.knda:10:5-12:10"

    def test_position_equality(self):
        """Test position equality comparison."""
        pos1 = SourcePosition(line=10, column=5)
        pos2 = SourcePosition(line=10, column=5)
        pos3 = SourcePosition(line=10, column=6)

        assert pos1 == pos2
        assert pos1 != pos3

    def test_position_ordering(self):
        """Test position less-than comparison."""
        pos1 = SourcePosition(line=10, column=5)
        pos2 = SourcePosition(line=10, column=6)
        pos3 = SourcePosition(line=11, column=0)

        assert pos1 < pos2
        assert pos1 < pos3
        assert pos2 < pos3


class TestSourceSnippetExtractor:
    """Test source code snippet extraction."""

    def setup_method(self):
        """Setup test source lines."""
        self.source_lines = [
            "~kinda int x = 5",
            "~sometimes {",
            "    print('hello')",
            "    ~maybe {",
            "        print('world')",
            "    }",
            "# Missing closing brace",
        ]

    def test_basic_extraction(self):
        """Test basic snippet extraction."""
        extractor = SourceSnippetExtractor(self.source_lines)
        pos = SourcePosition(line=3, column=0)
        snippet = extractor.extract(pos, context_lines=1)

        assert "2 " in snippet
        assert "3 →" in snippet
        assert "4 " in snippet
        assert "print('hello')" in snippet

    def test_extraction_with_column_highlight(self):
        """Test snippet with column highlight caret."""
        extractor = SourceSnippetExtractor(self.source_lines)
        pos = SourcePosition(line=3, column=10)
        snippet = extractor.extract(pos, context_lines=1, highlight_column=True)

        assert "3 →" in snippet
        assert "^" in snippet  # Caret under error column

    def test_extraction_at_file_start(self):
        """Test extraction at start of file."""
        extractor = SourceSnippetExtractor(self.source_lines)
        pos = SourcePosition(line=1, column=0)
        snippet = extractor.extract(pos, context_lines=3)

        assert "1 →" in snippet
        assert "~kinda int x = 5" in snippet

    def test_extraction_at_file_end(self):
        """Test extraction at end of file."""
        extractor = SourceSnippetExtractor(self.source_lines)
        pos = SourcePosition(line=7, column=0)
        snippet = extractor.extract(pos, context_lines=3)

        assert "7 →" in snippet
        assert "# Missing closing brace" in snippet

    def test_range_extraction_close_positions(self):
        """Test range extraction with close positions."""
        extractor = SourceSnippetExtractor(self.source_lines)
        start_pos = SourcePosition(line=2, column=0)
        end_pos = SourcePosition(line=4, column=0)

        snippet = extractor.extract_range(start_pos, end_pos, context_lines=1)

        # Should be single snippet covering both
        assert "2 →" in snippet
        assert "~sometimes {" in snippet

    def test_range_extraction_far_positions(self):
        """Test range extraction with distant positions."""
        # Add more lines to test far positions
        long_source = self.source_lines + [""] * 50 + ["end line"]
        extractor = SourceSnippetExtractor(long_source)

        start_pos = SourcePosition(line=2, column=0)
        end_pos = SourcePosition(line=58, column=0)

        snippet = extractor.extract_range(start_pos, end_pos, context_lines=1)

        # Should show separate snippets with separator
        assert "2 →" in snippet
        assert "58 →" in snippet
        assert "..." in snippet  # Separator

    def test_long_line_truncation(self):
        """Test truncation of long lines."""
        long_line = "x" * 100
        source = [long_line]
        extractor = SourceSnippetExtractor(source)

        pos = SourcePosition(line=1, column=0)
        snippet = extractor.extract(pos, max_line_width=50)

        # Line should be truncated
        assert "..." in snippet
        assert len(snippet.split("│")[1].strip()) <= 50


class TestScenario1_MissingBraces:
    """Test Scenario 1: Missing braces error messages."""

    def test_missing_closing_brace(self):
        """Test missing closing brace error."""
        source_lines = [
            "~sometimes {",
            "    print('hello')",
            "# Missing }",
        ]

        pos = SourcePosition(line=1, column=0)
        error = KindaSyntaxError(
            "missing_closing_brace",
            pos,
            source_lines=source_lines,
            construct_type="~sometimes",
            start_line=1,
            current_line=3,
        )

        error_msg = str(error)
        assert "Missing closing brace" in error_msg
        assert "~sometimes" in error_msg
        assert "line 1" in error_msg
        assert "[tip]" in error_msg

    def test_missing_opening_brace(self):
        """Test missing opening brace error."""
        source_lines = [
            "~sometimes",
            "    print('hello')",
            "}",
        ]

        pos = SourcePosition(line=1, column=0)
        error = KindaSyntaxError(
            "missing_opening_brace",
            pos,
            source_lines=source_lines,
            construct_type="~sometimes",
        )

        error_msg = str(error)
        assert "Expected opening brace" in error_msg
        assert "'{'" in error_msg or "{{" in error_msg


class TestScenario2_InvalidOperators:
    """Test Scenario 2: Invalid operator error messages."""

    def test_invalid_operator(self):
        """Test invalid operator error."""
        source_lines = [
            "~kinda int x = 5",
            "y ~~ x  # Invalid operator",
        ]

        pos = SourcePosition(line=2, column=2)
        error = KindaSyntaxError(
            "invalid_operator",
            pos,
            source_lines=source_lines,
            operator="~~",
        )

        error_msg = str(error)
        assert "Invalid operator" in error_msg
        assert "~~" in error_msg
        assert "Valid operators are:" in error_msg


class TestScenario3_UnclosedStrings:
    """Test Scenario 3: Unclosed string error messages."""

    def test_unclosed_string(self):
        """Test unclosed string literal error."""
        source_lines = [
            "~kinda int x = 5",
            "print('hello",
        ]

        pos = SourcePosition(line=2, column=6)
        error = KindaSyntaxError(
            "unclosed_string",
            pos,
            source_lines=source_lines,
            quote_type="'",
        )

        error_msg = str(error)
        assert "Unclosed string literal" in error_msg
        assert "line 2" in error_msg
        assert "[tip]" in error_msg

    def test_mismatched_quotes(self):
        """Test mismatched quote types."""
        source_lines = [
            "msg = \"hello'  # Mismatched quotes",
        ]

        pos = SourcePosition(line=1, column=6)
        error = KindaSyntaxError(
            "mismatched_quotes",
            pos,
            source_lines=source_lines,
            open_quote='"',
            close_quote="'",
        )

        error_msg = str(error)
        assert "Mismatched string quotes" in error_msg
        assert "Use matching quotes" in error_msg


class TestScenario4_MalformedNumbers:
    """Test Scenario 4: Malformed number error messages."""

    def test_malformed_number(self):
        """Test malformed number error."""
        source_lines = [
            "~kinda int x = 3.14.159  # Too many dots",
        ]

        pos = SourcePosition(line=1, column=15)
        error = KindaSyntaxError(
            "malformed_number",
            pos,
            source_lines=source_lines,
            value="3.14.159",
        )

        error_msg = str(error)
        assert "Malformed number" in error_msg
        assert "3.14.159" in error_msg
        assert "Valid number formats:" in error_msg

    def test_multiple_decimal_points(self):
        """Test multiple decimal points error."""
        source_lines = [
            "~kinda float pi = 3.1.4",
        ]

        pos = SourcePosition(line=1, column=18)
        error = KindaSyntaxError(
            "multiple_decimal_points",
            pos,
            source_lines=source_lines,
            corrected_value="3.14",
        )

        error_msg = str(error)
        assert "multiple decimal points" in error_msg
        assert "3.14" in error_msg


class TestScenario5_MismatchedParentheses:
    """Test Scenario 5: Mismatched parentheses error messages."""

    def test_unmatched_opening_paren(self):
        """Test unmatched opening parenthesis."""
        source_lines = [
            "~sometimes(condition",
        ]

        pos = SourcePosition(line=1, column=10)
        error = KindaSyntaxError(
            "unmatched_opening_paren",
            pos,
            source_lines=source_lines,
        )

        error_msg = str(error)
        assert "Unmatched opening parenthesis" in error_msg
        assert "Add closing ')'" in error_msg

    def test_unmatched_closing_paren(self):
        """Test unmatched closing parenthesis."""
        source_lines = [
            "print('hello'))",
        ]

        pos = SourcePosition(line=1, column=14)
        error = KindaSyntaxError(
            "unmatched_closing_paren",
            pos,
            source_lines=source_lines,
        )

        error_msg = str(error)
        assert "Unmatched closing parenthesis" in error_msg
        assert "Remove extra ')'" in error_msg

    def test_mismatched_brackets(self):
        """Test mismatched bracket types."""
        source_lines = [
            "data = [1, 2, 3)",
        ]

        pos = SourcePosition(line=1, column=15)
        error = KindaSyntaxError(
            "mismatched_brackets",
            pos,
            source_lines=source_lines,
            expected="]",
            actual=")",
        )

        error_msg = str(error)
        assert "Mismatched bracket" in error_msg
        assert "expected" in error_msg
        assert "]" in error_msg
        assert ")" in error_msg


class TestScenario6_InvalidConstructNames:
    """Test Scenario 6: Invalid construct name error messages with fuzzy matching."""

    def test_unknown_construct_with_suggestion(self):
        """Test unknown construct with fuzzy match suggestion."""
        source_lines = [
            "~sometymes {  # Typo: should be 'sometimes'",
        ]

        pos = SourcePosition(line=1, column=0)
        error = KindaSyntaxError(
            "unknown_construct",
            pos,
            source_lines=source_lines,
            construct_name="sometymes",
        )

        error_msg = str(error)
        assert "Unknown construct" in error_msg
        assert "~sometymes" in error_msg
        assert "Did you mean" in error_msg
        assert "~sometimes" in error_msg  # Fuzzy match suggestion

    def test_typo_in_construct(self):
        """Test construct typo with closest match."""
        source_lines = [
            "~probbly {  # Typo: should be 'probably'",
        ]

        pos = SourcePosition(line=1, column=0)

        # Get closest match
        from kinda.utils.fuzzy_match import find_closest_matches

        matches = find_closest_matches("probbly", VALID_CONSTRUCTS, max_results=1)
        closest_match = matches[0][0] if matches else "probably"
        distance = matches[0][1] if matches else 1

        error = KindaSyntaxError(
            "typo_in_construct",
            pos,
            source_lines=source_lines,
            construct_name="probbly",
            closest_match=closest_match,
            distance=distance,
        )

        error_msg = str(error)
        assert "Unrecognized construct" in error_msg
        assert "~probbly" in error_msg
        assert "Did you mean" in error_msg
        assert "~probably" in error_msg or f"~{closest_match}" in error_msg

    def test_suggest_construct_function(self):
        """Test suggest_construct helper function."""
        # Common typos
        assert suggest_construct("sometymes") is not None
        assert "~sometimes" in suggest_construct("sometymes")

        assert suggest_construct("probbly") is not None
        assert "~probably" in suggest_construct("probbly")

        # No close matches
        result = suggest_construct("completely_unknown_xyz")
        assert result is None


class TestScenario7_WrongArgumentCounts:
    """Test Scenario 7: Wrong argument count error messages."""

    def test_wrong_argument_count(self):
        """Test wrong number of arguments."""
        source_lines = [
            "~kinda int x = ~kinda_repeat(5, 10) {  # Too many args",
        ]

        pos = SourcePosition(line=1, column=19)
        error = KindaSyntaxError(
            "wrong_argument_count",
            pos,
            source_lines=source_lines,
            construct_type="~kinda_repeat",
            expected_count="1",
            actual_count="2",
            usage_example="~kinda_repeat(5) { ... }",
        )

        error_msg = str(error)
        assert "expects" in error_msg
        assert "argument" in error_msg
        assert "Usage:" in error_msg

    def test_missing_required_argument(self):
        """Test missing required argument."""
        source_lines = [
            "~kinda_repeat() {  # Missing count argument",
        ]

        pos = SourcePosition(line=1, column=0)
        error = KindaSyntaxError(
            "missing_required_argument",
            pos,
            source_lines=source_lines,
            construct_type="~kinda_repeat",
            arg_name="count",
            usage_example="~kinda_repeat(5) { ... }",
        )

        error_msg = str(error)
        assert "missing required argument" in error_msg
        assert "count" in error_msg
        assert "Usage:" in error_msg


class TestScenario8_TypeMismatches:
    """Test Scenario 8: Type mismatch error messages."""

    def test_type_mismatch(self):
        """Test type mismatch error."""
        source_lines = [
            "~kinda int x = 'not a number'  # Type mismatch",
        ]

        pos = SourcePosition(line=1, column=15)
        error = KindaSyntaxError(
            "type_mismatch",
            pos,
            source_lines=source_lines,
            expected_type="int",
            actual_type="str",
        )

        error_msg = str(error)
        assert "Type mismatch" in error_msg
        assert "expected" in error_msg
        assert "int" in error_msg
        assert "str" in error_msg

    def test_incompatible_types(self):
        """Test incompatible types in operation."""
        source_lines = [
            "result = 'hello' + 42  # Can't add str and int",
        ]

        pos = SourcePosition(line=1, column=9)
        error = KindaSyntaxError(
            "incompatible_types",
            pos,
            source_lines=source_lines,
            operation="addition",
            left_type="str",
            right_type="int",
            compatible_type="str or int",
        )

        error_msg = str(error)
        assert "Incompatible types" in error_msg
        assert "str" in error_msg
        assert "int" in error_msg


class TestScenario9_NestingErrors:
    """Test Scenario 9: Nesting error messages."""

    def test_excessive_nesting(self):
        """Test excessive nesting depth error."""
        source_lines = [
            "~sometimes {",
            "    " * 50 + "# Very deep nesting",
        ]

        pos = SourcePosition(line=2, column=0)
        error = KindaSyntaxError(
            "excessive_nesting",
            pos,
            source_lines=source_lines,
            current_depth=51,
            max_depth=50,
        )

        error_msg = str(error)
        assert "Nesting depth limit exceeded" in error_msg
        assert "51" in error_msg
        assert "50" in error_msg
        assert "KINDA_MAX_NESTING_DEPTH" in error_msg

    def test_inconsistent_nesting(self):
        """Test inconsistent indentation error."""
        source_lines = [
            "~sometimes {",
            "    print('hello')",
            "      print('world')  # Wrong indentation",
        ]

        pos = SourcePosition(line=3, column=0)
        error = KindaSyntaxError(
            "inconsistent_nesting",
            pos,
            source_lines=source_lines,
            expected_indent=4,
            actual_indent=6,
        )

        error_msg = str(error)
        assert "Inconsistent indentation" in error_msg
        assert "expected" in error_msg
        assert "4" in error_msg
        assert "6" in error_msg


class TestKindaParseErrorCompatibility:
    """Test backward compatibility of KindaParseError."""

    def test_legacy_parse_error_format(self):
        """Test legacy KindaParseError still works."""
        error = KindaParseError(
            message="Test error message",
            line_number=10,
            line_content="~kinda int x = 5",
            file_path="test.py.knda",
        )

        # Legacy attributes preserved
        assert error.line_number == 10
        assert error.line_content == "~kinda int x = 5"
        assert error.file_path == "test.py.knda"

        # Error message formatted
        error_msg = str(error)
        assert "line 10" in error_msg or "10:" in error_msg
        assert "Test error message" in error_msg

    def test_parse_error_without_file_path(self):
        """Test KindaParseError without file path."""
        error = KindaParseError(
            message="Parse error",
            line_number=5,
            line_content="bad syntax",
        )

        assert error.line_number == 5
        error_msg = str(error)
        assert "line 5" in error_msg

    def test_parse_error_with_source_lines(self):
        """Test KindaParseError with full source context."""
        source_lines = [
            "line 1",
            "line 2",
            "line 3 with error",
            "line 4",
        ]

        error = KindaParseError(
            message="Syntax error on line 3",
            line_number=3,
            line_content="line 3 with error",
            file_path="test.py.knda",
            source_lines=source_lines,
        )

        error_msg = str(error)
        assert "line 3" in error_msg or "3:" in error_msg
        assert "Syntax error" in error_msg
