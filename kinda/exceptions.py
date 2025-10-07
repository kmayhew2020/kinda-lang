"""
Custom exceptions for the Kinda language compiler and runtime.

This module provides enhanced error handling with:
- Precise line/column positioning (SourcePosition)
- Source code context extraction (SourceSnippetExtractor)
- Template-based error messages (ERROR_TEMPLATES)
- Fuzzy matching for typo suggestions
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from pathlib import Path

from kinda.utils.fuzzy_match import find_closest_matches, format_did_you_mean


# Valid construct names for fuzzy matching
VALID_CONSTRUCTS = [
    # Type declarations
    "kinda_int",
    "kinda_float",
    "kinda_bool",
    "kinda_binary",
    # Time-based drift
    "time_drift_float",
    "time_drift_int",
    # Conditionals
    "sometimes",
    "maybe",
    "probably",
    "rarely",
    # Loops
    "sometimes_while",
    "maybe_for",
    "kinda_repeat",
    "eventually_until",
    # Operators
    "ish",
    # Output
    "sorta_print",
    # Error handling
    "welp",
    # Statistical testing
    "assert_eventually",
    "assert_probability",
]

# Usage examples for error messages
CONSTRUCT_USAGE = {
    "kinda_int": "~kinda int x = 5",
    "kinda_float": "~kinda float pi = 3.14",
    "kinda_bool": "~kinda bool flag = True",
    "kinda_binary": "~kinda binary data = 0b1010",
    "sometimes": "~sometimes { ... } or ~sometimes(condition)",
    "maybe": "~maybe { ... } or ~maybe(condition)",
    "probably": "~probably { ... }",
    "rarely": "~rarely { ... }",
    "kinda_repeat": "~kinda_repeat(5) { ... }",
    "eventually_until": "~eventually_until condition { ... }",
    "sorta_print": "~sorta print('message')",
    "assert_eventually": "~assert_eventually(condition, timeout=5.0, confidence=0.95)",
    "assert_probability": "~assert_probability(lambda: event(), expected_prob=0.5, tolerance=0.1, samples=1000)",
}

# Error message templates with placeholders
ERROR_TEMPLATES = {
    # Scenario 1: Missing braces
    "missing_closing_brace": {
        "message": "Missing closing brace '}}' for {construct_type} block starting at line {start_line}",
        "suggestion": "Add '}}' after line {current_line} to close the {construct_type} block",
        "show_context": True,
        "context_lines": 5,
    },
    "missing_opening_brace": {
        "message": "Expected opening brace '{{' after {construct_type} at line {line}",
        "suggestion": "Add '{{' at the end of line {line} to start the block",
        "show_context": True,
        "context_lines": 3,
    },
    # Scenario 2: Invalid operators
    "invalid_operator": {
        "message": "Invalid operator '{operator}' at line {line}, column {column}",
        "suggestion": "Valid operators are: ~=, ==, !=, <, >, <=, >=, +, -, *, /, %",
        "show_context": True,
        "context_lines": 2,
    },
    # Scenario 3: Unclosed strings
    "unclosed_string": {
        "message": "Unclosed string literal starting at line {line}, column {column}",
        "suggestion": "Add closing {quote_type} before end of line",
        "show_context": True,
        "context_lines": 2,
        "highlight_column": True,
    },
    "mismatched_quotes": {
        "message": "Mismatched string quotes at line {line}: started with {open_quote}, ended with {close_quote}",
        "suggestion": "Use matching quotes: both single (') or both double (\")",
        "show_context": True,
        "context_lines": 2,
    },
    # Scenario 4: Malformed numbers
    "malformed_number": {
        "message": "Malformed number '{value}' at line {line}, column {column}",
        "suggestion": "Valid number formats: 42, 3.14, 0xFF (hex), 0b1010 (binary), 1.5e10 (scientific)",
        "show_context": True,
        "context_lines": 2,
        "highlight_column": True,
    },
    "multiple_decimal_points": {
        "message": "Number has multiple decimal points at line {line}, column {column}",
        "suggestion": "Use only one decimal point: {corrected_value}",
        "show_context": True,
        "context_lines": 2,
    },
    # Scenario 5: Mismatched parentheses
    "unmatched_opening_paren": {
        "message": "Unmatched opening parenthesis at line {line}, column {column}",
        "suggestion": "Add closing ')' or check for extra '(' at line {line}",
        "show_context": True,
        "context_lines": 3,
        "highlight_column": True,
    },
    "unmatched_closing_paren": {
        "message": "Unmatched closing parenthesis at line {line}, column {column}",
        "suggestion": "Remove extra ')' or add matching '(' earlier in the expression",
        "show_context": True,
        "context_lines": 3,
        "highlight_column": True,
    },
    "mismatched_brackets": {
        "message": "Mismatched bracket at line {line}, column {column}: expected '{expected}', got '{actual}'",
        "suggestion": "Check bracket pairing: (), [], {{}}",
        "show_context": True,
        "context_lines": 3,
    },
    # Scenario 6: Invalid construct names
    "unknown_construct": {
        "message": "Unknown construct '~{construct_name}' at line {line}, column {column}",
        "suggestion": "Did you mean: {suggestions}?",
        "show_context": True,
        "context_lines": 2,
        "use_fuzzy_matching": True,
    },
    "typo_in_construct": {
        "message": "Unrecognized construct '~{construct_name}' at line {line}",
        "suggestion": "Did you mean '~{closest_match}'? (Levenshtein distance: {distance})",
        "show_context": True,
        "context_lines": 2,
        "use_fuzzy_matching": True,
    },
    # Scenario 7: Wrong argument counts
    "wrong_argument_count": {
        "message": "{construct_type} expects {expected_count} argument(s), got {actual_count} at line {line}",
        "suggestion": "Usage: {usage_example}",
        "show_context": True,
        "context_lines": 3,
    },
    "missing_required_argument": {
        "message": "{construct_type} missing required argument '{arg_name}' at line {line}",
        "suggestion": "Usage: {usage_example}",
        "show_context": True,
        "context_lines": 2,
    },
    # Scenario 8: Type mismatches
    "type_mismatch": {
        "message": "Type mismatch at line {line}: expected {expected_type}, got {actual_type}",
        "suggestion": "Convert value to {expected_type} or use a different construct",
        "show_context": True,
        "context_lines": 2,
    },
    "incompatible_types": {
        "message": "Incompatible types for {operation} at line {line}: {left_type} and {right_type}",
        "suggestion": "Ensure both operands are {compatible_type}",
        "show_context": True,
        "context_lines": 2,
    },
    # Scenario 9: Nesting errors
    "excessive_nesting": {
        "message": "Nesting depth limit exceeded at line {line} ({current_depth}/{max_depth} levels)",
        "suggestion": "Refactor code to reduce nesting or increase KINDA_MAX_NESTING_DEPTH",
        "show_context": True,
        "context_lines": 5,
    },
    "inconsistent_nesting": {
        "message": "Inconsistent indentation at line {line}: expected {expected_indent} spaces, got {actual_indent}",
        "suggestion": "Align with previous block indentation",
        "show_context": True,
        "context_lines": 4,
    },
    # Generic error template for backward compatibility
    "generic_parse_error": {
        "message": "{message}",
        "suggestion": "",
        "show_context": True,
        "context_lines": 3,
    },
}


@dataclass
class SourcePosition:
    """
    Represents a position in source code with line and column information.

    Attributes:
        line: Line number (1-indexed)
        column: Column number (0-indexed for compatibility with Python AST)
        file_path: Path to the source file
        end_line: Optional end line for multi-line spans
        end_column: Optional end column for spans
    """

    line: int
    column: int
    file_path: Optional[str] = None
    end_line: Optional[int] = None
    end_column: Optional[int] = None

    def __str__(self) -> str:
        """Format as file:line:column (standard compiler format)"""
        if self.file_path:
            return f"{self.file_path}:{self.line}:{self.column}"
        return f"line {self.line}, column {self.column}"

    def to_range_str(self) -> str:
        """Format as file:line:col-line:col for spans"""
        if self.end_line and self.end_column:
            if self.file_path:
                return (
                    f"{self.file_path}:{self.line}:{self.column}-{self.end_line}:{self.end_column}"
                )
            return f"{self.line}:{self.column}-{self.end_line}:{self.end_column}"
        return str(self)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SourcePosition):
            return False
        return (
            self.line == other.line
            and self.column == other.column
            and self.file_path == other.file_path
        )

    def __lt__(self, other: object) -> bool:
        """Enable sorting by position"""
        if not isinstance(other, SourcePosition):
            return NotImplemented
        if self.line != other.line:
            return self.line < other.line
        return self.column < other.column


class SourceSnippetExtractor:
    """
    Extracts source code snippets with context for error messages.
    """

    def __init__(self, source_lines: List[str]):
        """
        Initialize with source code lines.

        Args:
            source_lines: List of source code lines (no line numbers)
        """
        self.source_lines = source_lines

    def extract(
        self,
        position: SourcePosition,
        context_lines: int = 3,
        highlight_column: bool = False,
        max_line_width: int = 80,
    ) -> str:
        """
        Extract source snippet with line numbers and context.

        Args:
            position: Source position to highlight
            context_lines: Number of lines before/after to show
            highlight_column: If True, add caret (^) under error column
            max_line_width: Truncate lines longer than this

        Returns:
            Formatted snippet string with line numbers
        """
        start_line = max(1, position.line - context_lines)
        end_line = min(len(self.source_lines), position.line + context_lines)

        # Calculate line number width for alignment
        line_num_width = len(str(end_line))

        snippet_lines = []
        for i in range(start_line - 1, end_line):  # -1 because source_lines is 0-indexed
            line_num = i + 1
            line_content = self.source_lines[i]

            # Truncate long lines
            if len(line_content) > max_line_width:
                line_content = line_content[: max_line_width - 3] + "..."

            # Highlight error line with marker
            marker = "→" if line_num == position.line else " "

            # Format: "  15 → │ code here"
            formatted = f"  {line_num:>{line_num_width}} {marker} │ {line_content}"
            snippet_lines.append(formatted)

            # Add column highlight caret if requested
            if highlight_column and line_num == position.line:
                # Calculate position of caret under error column
                prefix_len = line_num_width + 6  # "  NN → │ "
                caret_line = " " * (prefix_len + position.column) + "^"
                snippet_lines.append(caret_line)

        return "\n".join(snippet_lines)

    def extract_range(
        self,
        start_pos: SourcePosition,
        end_pos: SourcePosition,
        context_lines: int = 2,
    ) -> str:
        """
        Extract snippet highlighting a range (e.g., for unclosed blocks).

        Shows context around start and end positions with range markers.
        """
        # Show context around start
        start_snippet = self.extract(start_pos, context_lines=context_lines, highlight_column=True)

        # If end is far from start, show separate end context
        if end_pos.line - start_pos.line > context_lines * 2:
            end_snippet = self.extract(end_pos, context_lines=context_lines, highlight_column=True)
            separator = f"\n  ... ({end_pos.line - start_pos.line - 1} lines) ...\n"
            return start_snippet + separator + end_snippet
        else:
            # Positions are close, single snippet covers both
            return start_snippet


class ErrorContextManager:
    """
    Manages error context windows with smart truncation and formatting.
    """

    @staticmethod
    def format_context_window(
        snippet: str,
        position: SourcePosition,
        template_config: Dict[str, Any],
    ) -> str:
        """
        Format complete error context including snippet and metadata.

        Returns formatted string like:

        ```
        test.py.knda:15:8: Missing closing brace '}' for ~sometimes block

           10   │ ~sometimes {
           11   │     print("hello")
           12   │     ~maybe {
           13   │         print("world")
           14   │     }
           15 → │ # <- Missing } here
                        ^

        [tip] Add '}' after line 14 to close the ~sometimes block
        ```
        """
        parts = []

        # Header: file:line:col: message
        parts.append(f"{position}: {template_config['message']}")
        parts.append("")  # Blank line

        # Source snippet
        if template_config.get("show_context", False):
            parts.append(snippet)
            parts.append("")  # Blank line

        # Suggestion
        if "suggestion" in template_config and template_config["suggestion"]:
            parts.append(f"[tip] {template_config['suggestion']}")

        return "\n".join(parts)


def suggest_construct(typo: str) -> Optional[str]:
    """
    Suggest correct construct name for a typo.

    Args:
        typo: Mistyped construct name (without ~ prefix)

    Returns:
        Formatted "Did you mean?" suggestion or None
    """
    matches = find_closest_matches(typo, VALID_CONSTRUCTS, max_distance=3, max_results=3)

    if matches:
        return format_did_you_mean(matches)
    return None


class KindaError(Exception):
    """Base exception for all Kinda-related errors."""

    pass


class KindaSyntaxError(KindaError):
    """
    Enhanced syntax error with precise positioning, context, and suggestions.

    Attributes:
        template_key: Key from ERROR_TEMPLATES
        position: SourcePosition indicating error location
        template_args: Arguments to format error template
        source_lines: Optional source code lines for context extraction
    """

    def __init__(
        self,
        template_key: str,
        position: SourcePosition,
        source_lines: Optional[List[str]] = None,
        **template_args: Any,
    ):
        self.template_key = template_key
        self.position = position
        self.template_args = template_args
        self.source_lines = source_lines

        # Get template configuration
        if template_key not in ERROR_TEMPLATES:
            raise ValueError(f"Unknown error template: {template_key}")

        self.template_config = ERROR_TEMPLATES[template_key].copy()

        # Handle fuzzy matching FIRST if requested (before formatting)
        if self.template_config.get("use_fuzzy_matching", False):
            if "construct_name" in template_args:
                construct_name = str(template_args["construct_name"])
                fuzzy_suggestions = suggest_construct(construct_name)
                if fuzzy_suggestions:
                    template_args["suggestions"] = fuzzy_suggestions

        # Format message and suggestion
        message_template = str(self.template_config["message"])
        self.message = message_template.format(
            line=position.line, column=position.column, **template_args
        )

        suggestion_template = str(self.template_config.get("suggestion", ""))
        self.suggestion = suggestion_template
        if self.suggestion:
            self.suggestion = suggestion_template.format(
                line=position.line, column=position.column, **template_args
            )

        # Format complete error message
        super().__init__(self._format_error())

    def _format_error(self) -> str:
        """Format complete error message with context."""
        parts = []

        # Header: file:line:col: message
        parts.append(f"{self.position}: {self.message}")

        # Source snippet if available
        if self.source_lines and self.template_config.get("show_context", False):
            extractor = SourceSnippetExtractor(self.source_lines)
            context_lines_val = self.template_config.get("context_lines", 3)
            context_lines = context_lines_val if isinstance(context_lines_val, int) else 3
            highlight_column_val = self.template_config.get("highlight_column", False)
            highlight_column = (
                highlight_column_val if isinstance(highlight_column_val, bool) else False
            )
            snippet = extractor.extract(
                self.position,
                context_lines=context_lines,
                highlight_column=highlight_column,
            )
            parts.append("")  # Blank line
            parts.append(snippet)

        # Suggestion
        if self.suggestion:
            parts.append("")  # Blank line
            parts.append(f"[tip] {self.suggestion}")

        return "\n".join(parts)


class KindaParseError(KindaSyntaxError):
    """
    Parsing error with backward compatibility for existing code.

    Maintains compatibility with current KindaParseError usage while
    providing enhanced error messages when possible.
    """

    def __init__(
        self,
        message: str,
        line_number: int,
        line_content: str = "",
        file_path: Optional[str] = None,
        column: int = 0,
        source_lines: Optional[List[str]] = None,
    ):
        # Store legacy attributes for compatibility
        self.line_number = line_number
        self.line_content = line_content
        self.file_path = file_path

        # Create position from legacy parameters
        position = SourcePosition(
            line=line_number,
            column=column,
            file_path=file_path,
        )

        # If source_lines not provided, create from line_content
        if source_lines is None and line_content:
            source_lines = [line_content]

        # Use generic parse error template
        super().__init__(
            template_key="generic_parse_error",
            position=position,
            source_lines=source_lines,
            message=message,
        )


class KindaSizeError(KindaError):
    """
    Raised when input exceeds parser safety limits.

    This exception is raised to prevent Denial of Service (DoS) attacks
    through maliciously large or complex input files. It enforces limits on:
    - File size
    - Line length
    - Parsing iterations
    - String literal size

    Attributes:
        message: Human-readable error message
        limit_type: Type of limit exceeded ('file_size', 'line_length',
                   'parse_iterations', 'string_size')
        current_value: The actual value that exceeded the limit
        max_value: The maximum allowed value
        context: Additional context (e.g., line number, file path)
    """

    def __init__(
        self, message: str, limit_type: str, current_value: int, max_value: int, context: str = ""
    ):
        super().__init__(message)
        self.limit_type = limit_type
        self.current_value = current_value
        self.max_value = max_value
        self.context = context

    def __str__(self) -> str:
        """Generate helpful error message with actionable suggestions."""
        base_msg = super().__str__()

        suggestions = {
            "file_size": "Consider splitting the file into smaller modules or increasing KINDA_MAX_FILE_SIZE.",
            "line_length": "Break this line into multiple lines or increase KINDA_MAX_LINE_LENGTH.",
            "parse_iterations": "The input may contain deeply nested constructs. Simplify the structure or increase KINDA_MAX_PARSE_ITERATIONS.",
            "string_size": "Break large string literals into smaller chunks or increase KINDA_MAX_STRING_SIZE.",
        }

        suggestion = suggestions.get(self.limit_type, "Check the input for malformed constructs.")

        details = f"\n  Limit type: {self.limit_type}"
        details += f"\n  Current value: {self.current_value:,}"
        details += f"\n  Maximum allowed: {self.max_value:,}"

        if self.context:
            details += f"\n  Context: {self.context}"

        details += f"\n  Suggestion: {suggestion}"

        return f"{base_msg}{details}"


class KindaRuntimeError(KindaError):
    """Raised when a runtime error occurs during execution."""

    pass


class KindaSecurityError(KindaError):
    """Raised when a security violation is detected."""

    pass
