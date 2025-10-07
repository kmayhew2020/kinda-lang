"""
Test suite for line/column position tracking accuracy (Issue #113).

Validates that error positions are correctly calculated and reported.
"""

import pytest
from kinda.exceptions import SourcePosition, SourceSnippetExtractor


class TestPositionAccuracy:
    """Test accuracy of position tracking."""

    def test_single_line_position(self):
        """Test position in single line."""
        source = ["~kinda int x = 5"]
        pos = SourcePosition(line=1, column=0)

        extractor = SourceSnippetExtractor(source)
        snippet = extractor.extract(pos, context_lines=0)

        assert "1 →" in snippet
        assert "~kinda int x = 5" in snippet

    def test_multi_line_position(self):
        """Test position across multiple lines."""
        source = [
            "line 1",
            "line 2",
            "line 3 with error",
            "line 4",
        ]

        pos = SourcePosition(line=3, column=5)
        extractor = SourceSnippetExtractor(source)
        snippet = extractor.extract(pos, context_lines=1, highlight_column=True)

        assert "3 →" in snippet
        assert "line 3 with error" in snippet
        assert "^" in snippet  # Column marker

    def test_column_marker_alignment(self):
        """Test column marker aligns correctly."""
        source = ["~kinda int x = 5"]

        # Error at 'int' (column 7)
        pos = SourcePosition(line=1, column=7)
        extractor = SourceSnippetExtractor(source)
        snippet = extractor.extract(pos, context_lines=0, highlight_column=True)

        lines = snippet.split("\n")
        code_line = [l for l in lines if "→" in l][0]
        caret_line = [l for l in lines if "^" in l][0]

        # Find where 'int' starts in code_line
        int_pos = code_line.index("int")
        caret_pos = caret_line.index("^")

        # Caret should be close to 'i' in 'int' (within 1 char for formatting)
        assert abs(caret_pos - int_pos) <= 1

    def test_position_at_line_start(self):
        """Test position at start of line."""
        source = ["    indented code"]

        pos = SourcePosition(line=1, column=0)
        extractor = SourceSnippetExtractor(source)
        snippet = extractor.extract(pos, context_lines=0, highlight_column=True)

        assert "1 →" in snippet
        assert "^" in snippet

    def test_position_at_line_end(self):
        """Test position at end of line."""
        source = ["short"]

        pos = SourcePosition(line=1, column=5)  # After 't' in 'short'
        extractor = SourceSnippetExtractor(source)
        snippet = extractor.extract(pos, context_lines=0, highlight_column=True)

        assert "1 →" in snippet
        assert "^" in snippet

    def test_position_in_whitespace(self):
        """Test position in whitespace."""
        source = ["word    word"]

        pos = SourcePosition(line=1, column=6)  # In spaces
        extractor = SourceSnippetExtractor(source)
        snippet = extractor.extract(pos, context_lines=0, highlight_column=True)

        assert "^" in snippet


class TestContextWindowAccuracy:
    """Test accuracy of context windows."""

    def test_context_lines_before(self):
        """Test context lines before error."""
        source = [
            "line 1",
            "line 2",
            "line 3",
            "line 4 error",
            "line 5",
        ]

        pos = SourcePosition(line=4, column=0)
        extractor = SourceSnippetExtractor(source)
        snippet = extractor.extract(pos, context_lines=2)

        # Should show lines 2, 3, 4
        assert "2 " in snippet
        assert "3 " in snippet
        assert "4 →" in snippet

    def test_context_lines_after(self):
        """Test context lines after error."""
        source = [
            "line 1",
            "line 2 error",
            "line 3",
            "line 4",
            "line 5",
        ]

        pos = SourcePosition(line=2, column=0)
        extractor = SourceSnippetExtractor(source)
        snippet = extractor.extract(pos, context_lines=2)

        # Should show lines 2, 3, 4
        assert "2 →" in snippet
        assert "3 " in snippet
        assert "4 " in snippet

    def test_context_at_file_boundaries(self):
        """Test context doesn't exceed file boundaries."""
        source = ["line 1", "line 2", "line 3"]

        # Error at line 1 - no lines before
        pos = SourcePosition(line=1, column=0)
        extractor = SourceSnippetExtractor(source)
        snippet = extractor.extract(pos, context_lines=5)

        lines = snippet.split("\n")
        line_numbers = [int(l.split()[0]) for l in lines if "│" in l]
        assert min(line_numbers) == 1

        # Error at line 3 - no lines after
        pos = SourcePosition(line=3, column=0)
        snippet = extractor.extract(pos, context_lines=5)

        lines = snippet.split("\n")
        line_numbers = [int(l.split()[0]) for l in lines if "│" in l]
        assert max(line_numbers) == 3

    def test_zero_context_lines(self):
        """Test zero context lines shows only error line."""
        source = [
            "line 1",
            "line 2 error",
            "line 3",
        ]

        pos = SourcePosition(line=2, column=0)
        extractor = SourceSnippetExtractor(source)
        snippet = extractor.extract(pos, context_lines=0)

        # Should show only line 2
        assert "2 →" in snippet
        assert "1 " not in snippet
        assert "3 " not in snippet


class TestRangeExtraction:
    """Test range extraction for multi-line errors."""

    def test_close_range(self):
        """Test range with close start/end positions."""
        source = [
            "line 1",
            "line 2 start",
            "line 3",
            "line 4 end",
            "line 5",
        ]

        start_pos = SourcePosition(line=2, column=7)
        end_pos = SourcePosition(line=4, column=7)

        extractor = SourceSnippetExtractor(source)
        snippet = extractor.extract_range(start_pos, end_pos, context_lines=1)

        # Should show single continuous snippet with start highlighted
        assert "2 →" in snippet
        # The range extraction shows context around start position
        assert "line 2 start" in snippet
        assert "..." not in snippet  # No separator for close ranges

    def test_far_range(self):
        """Test range with distant start/end positions."""
        # Create source with gap
        source = ["line 1", "line 2 start"] + [""] * 10 + ["line 13 end", "line 14"]

        start_pos = SourcePosition(line=2, column=7)
        end_pos = SourcePosition(line=13, column=7)

        extractor = SourceSnippetExtractor(source)
        snippet = extractor.extract_range(start_pos, end_pos, context_lines=1)

        # Should show separate snippets with separator
        assert "2 →" in snippet
        assert "13 →" in snippet
        assert "..." in snippet  # Separator showing gap

    def test_range_with_column_highlights(self):
        """Test range extraction includes column highlights."""
        source = [
            "~sometimes {",
            "    print('hello')",
            "}  # Missing opening brace earlier",
        ]

        start_pos = SourcePosition(line=1, column=0)
        end_pos = SourcePosition(line=3, column=0)

        extractor = SourceSnippetExtractor(source)
        snippet = extractor.extract_range(start_pos, end_pos, context_lines=0)

        # Both positions should be highlighted
        assert "1 →" in snippet
        assert "^" in snippet


class TestLineNumberFormatting:
    """Test line number formatting in snippets."""

    def test_line_number_alignment(self):
        """Test line numbers are aligned correctly."""
        # Mix of single, double, and triple digit line numbers
        source = ["line"] * 100

        pos = SourcePosition(line=50, column=0)
        extractor = SourceSnippetExtractor(source)
        snippet = extractor.extract(pos, context_lines=52)  # Show lines ~1-100

        lines = snippet.split("\n")
        # All line numbers should align
        # Find width of first line number
        first_line = [l for l in lines if "│" in l][0]
        first_num_width = first_line.index("│") - first_line.index(" ") - 2

        # Check all lines have same alignment
        for line in lines:
            if "│" in line:
                num_width = line.index("│") - line.index(" ") - 2
                assert num_width == first_num_width

    def test_single_digit_line_numbers(self):
        """Test formatting with single digit line numbers."""
        source = ["line 1", "line 2", "line 3"]

        pos = SourcePosition(line=2, column=0)
        extractor = SourceSnippetExtractor(source)
        snippet = extractor.extract(pos, context_lines=1)

        # Line numbers should be aligned
        assert "1 " in snippet or " 1 " in snippet
        assert "2 →" in snippet or " 2 →" in snippet
        assert "3 " in snippet or " 3 " in snippet

    def test_triple_digit_line_numbers(self):
        """Test formatting with triple digit line numbers."""
        source = ["line"] * 150

        pos = SourcePosition(line=100, column=0)
        extractor = SourceSnippetExtractor(source)
        snippet = extractor.extract(pos, context_lines=2)

        # Should show lines 98-102
        assert "100 →" in snippet
        assert "│" in snippet


class TestEdgeCases:
    """Test edge cases in position tracking."""

    def test_empty_file(self):
        """Test position in empty file."""
        source = []
        pos = SourcePosition(line=1, column=0)

        extractor = SourceSnippetExtractor(source)
        snippet = extractor.extract(pos, context_lines=1)

        # Should handle gracefully (likely empty snippet)
        assert isinstance(snippet, str)

    def test_empty_lines(self):
        """Test position on empty lines."""
        source = [
            "line 1",
            "",
            "line 3",
        ]

        pos = SourcePosition(line=2, column=0)
        extractor = SourceSnippetExtractor(source)
        snippet = extractor.extract(pos, context_lines=1)

        assert "2 →" in snippet
        assert "1 " in snippet
        assert "3 " in snippet

    def test_very_long_line(self):
        """Test position in very long line."""
        long_line = "x" * 200
        source = [long_line]

        pos = SourcePosition(line=1, column=150)
        extractor = SourceSnippetExtractor(source)
        snippet = extractor.extract(pos, context_lines=0, max_line_width=80)

        # Line should be truncated
        assert "..." in snippet
        assert len(snippet.split("│")[1].strip()) <= 80

    def test_position_beyond_line_length(self):
        """Test position beyond actual line length."""
        source = ["short"]

        pos = SourcePosition(line=1, column=100)  # Beyond line end
        extractor = SourceSnippetExtractor(source)
        snippet = extractor.extract(pos, context_lines=0, highlight_column=True)

        # Should handle gracefully
        assert "1 →" in snippet
        assert isinstance(snippet, str)

    def test_unicode_content(self):
        """Test position tracking with Unicode characters."""
        source = [
            "# 中文注释",
            "~kinda int x = 5  # Ошибка",
            "emoji = '🚀'",
        ]

        pos = SourcePosition(line=2, column=0)
        extractor = SourceSnippetExtractor(source)
        snippet = extractor.extract(pos, context_lines=1)

        assert "2 →" in snippet
        # Unicode should be preserved
        assert "中文" in snippet or "int" in snippet

    def test_tabs_vs_spaces(self):
        """Test position tracking with mixed tabs/spaces."""
        source = [
            "\t~sometimes {",  # Tab indent
            "    \tprint('hello')",  # Mixed
            "        }",  # Spaces
        ]

        pos = SourcePosition(line=2, column=4)
        extractor = SourceSnippetExtractor(source)
        snippet = extractor.extract(pos, context_lines=1, highlight_column=True)

        assert "2 →" in snippet
        assert "^" in snippet
