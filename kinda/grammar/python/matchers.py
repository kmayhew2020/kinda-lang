# kinda/grammar/python/matchers.py

import os
import re
from typing import Optional, Tuple, Any, List
from kinda.grammar.python.constructs import KindaPythonConstructs
from kinda.exceptions import KindaSizeError

# Parser DoS Protection Limits (Issue #110)
# These limits prevent malicious input from causing Denial of Service attacks
# All limits are configurable via environment variables

# Maximum file size in bytes (default: 1MB)
KINDA_MAX_FILE_SIZE = int(os.getenv("KINDA_MAX_FILE_SIZE", str(1024 * 1024)))

# Maximum line length in characters (default: 10,000)
KINDA_MAX_LINE_LENGTH = int(os.getenv("KINDA_MAX_LINE_LENGTH", "10000"))

# Maximum parsing iterations to prevent infinite loops (default: 50,000)
KINDA_MAX_PARSE_ITERATIONS = int(os.getenv("KINDA_MAX_PARSE_ITERATIONS", "50000"))

# Maximum string literal size in characters (default: 5,000)
KINDA_MAX_STRING_SIZE = int(os.getenv("KINDA_MAX_STRING_SIZE", "5000"))

# Compiled regex patterns for performance optimization
_SORTA_PRINT_PATTERN = re.compile(r"^\s*~sorta\s+print\s*\(")
_ISH_VALUE_PATTERN = re.compile(r"\b(\d+(?:\.\d+)?)\s*~ish")
_ISH_VALUE_FUNC_PATTERN = re.compile(r"\bish_value\s*\(\s*([^)]+)\s*\)")
_ISH_COMPARISON_PATTERN = re.compile(
    r"([a-zA-Z_][a-zA-Z0-9_]*)\s*~ish\s+([^~]+?)(?=\s+(?:and|or)|~|\)|\]|$|#|;|:)"
)
_WELP_PATTERN = re.compile(r'([^~"\']*)\s*~welp\s+([^\n]+)')
_STRING_DELIMITERS = re.compile(r'["\']{1,3}')


def validate_line_length(line: str, line_number: int, file_path: str = "unknown") -> None:
    """
    Validate that a line does not exceed the maximum allowed length.

    Args:
        line: The line to validate
        line_number: Line number in the source file (1-indexed)
        file_path: Path to the source file for error reporting

    Raises:
        KindaSizeError: If line exceeds KINDA_MAX_LINE_LENGTH
    """
    line_len = len(line)
    if line_len > KINDA_MAX_LINE_LENGTH:
        raise KindaSizeError(
            f"Line {line_number} in {file_path} exceeds maximum length",
            limit_type="line_length",
            current_value=line_len,
            max_value=KINDA_MAX_LINE_LENGTH,
            context=f"Line {line_number} in {file_path}",
        )


def validate_string_literal(
    string_content: str, line_number: int, file_path: str = "unknown"
) -> None:
    """
    Validate that a string literal does not exceed the maximum allowed size.

    Args:
        string_content: The string literal content (without quotes)
        line_number: Line number in the source file (1-indexed)
        file_path: Path to the source file for error reporting

    Raises:
        KindaSizeError: If string literal exceeds KINDA_MAX_STRING_SIZE
    """
    string_len = len(string_content)
    if string_len > KINDA_MAX_STRING_SIZE:
        raise KindaSizeError(
            f"String literal on line {line_number} in {file_path} exceeds maximum size",
            limit_type="string_size",
            current_value=string_len,
            max_value=KINDA_MAX_STRING_SIZE,
            context=f"Line {line_number} in {file_path}",
        )


def _parse_sorta_print_arguments(line: str) -> Optional[str]:
    """
    Robust parsing of ~sorta print arguments with string-aware parentheses matching.
    Handles nested function calls, complex expressions, and string literals.
    """
    # Use pre-compiled pattern for better performance
    match = _SORTA_PRINT_PATTERN.match(line)
    if not match:
        return None

    # Find the opening parenthesis
    start_idx = match.end() - 1  # -1 to include the opening paren
    if start_idx >= len(line) or line[start_idx] != "(":
        return None

    # String-aware parentheses parsing with iteration bounds
    paren_count = 0
    in_string = False
    string_char = None
    escaped = False
    end_idx = start_idx
    iterations = 0

    for i in range(start_idx, len(line)):
        # DoS protection: Check iteration bounds
        iterations += 1
        if iterations > KINDA_MAX_PARSE_ITERATIONS:
            raise KindaSizeError(
                f"Parsing exceeded maximum iterations while processing ~sorta print",
                limit_type="parse_iterations",
                current_value=iterations,
                max_value=KINDA_MAX_PARSE_ITERATIONS,
                context="~sorta print argument parsing",
            )

        char = line[i]

        if escaped:
            escaped = False
            continue

        if char == "\\" and in_string:
            escaped = True
            continue

        if not in_string:
            if char in "\"'":
                in_string = True
                string_char = char
            elif char == "(":
                paren_count += 1
            elif char == ")":
                paren_count -= 1
                if paren_count == 0:
                    end_idx = i
                    break
        else:
            # We're inside a string
            if char == string_char:
                in_string = False
                string_char = None

    if paren_count == 0:  # Found matching parenthesis
        content = line[start_idx + 1 : end_idx]
        return content
    else:
        # Graceful handling of unclosed strings/parentheses
        # Return partial content for better error context
        content = line[start_idx + 1 :]
        return content


def _parse_balanced_parentheses(line: str, start_pos: int) -> Tuple[Optional[str], bool]:
    """
    Parse balanced parentheses starting from start_pos.
    Returns (content, is_balanced) - content inside parentheses and whether they were balanced.
    """
    if start_pos >= len(line) or line[start_pos] != "(":
        return None, False

    paren_count = 0
    in_string = False
    string_char = None
    escaped = False
    end_pos = start_pos
    iterations = 0

    for i in range(start_pos, len(line)):
        # DoS protection: Check iteration bounds
        iterations += 1
        if iterations > KINDA_MAX_PARSE_ITERATIONS:
            raise KindaSizeError(
                f"Parsing exceeded maximum iterations while balancing parentheses",
                limit_type="parse_iterations",
                current_value=iterations,
                max_value=KINDA_MAX_PARSE_ITERATIONS,
                context="balanced parentheses parsing",
            )

        char = line[i]

        if escaped:
            escaped = False
            continue

        if char == "\\" and in_string:
            escaped = True
            continue

        if not in_string:
            if char in "\"'":
                in_string = True
                string_char = char
            elif char == "(":
                paren_count += 1
            elif char == ")":
                paren_count -= 1
                if paren_count == 0:
                    end_pos = i
                    break
        else:
            # We're inside a string
            if char == string_char:
                in_string = False
                string_char = None

    if paren_count == 0:  # Found matching parenthesis
        content = line[start_pos + 1 : end_pos]
        return content, True
    else:
        # Unbalanced parentheses
        content = line[start_pos + 1 :]
        return content, False


def _parse_conditional_arguments(line: str, construct_name: str) -> Optional[Tuple[str]]:
    """
    Parse conditional constructs (~maybe, ~sometimes) with balanced parentheses support.
    Maintains compatibility with existing behavior and tests.
    """
    import re

    # Maintain original behavior: NO leading whitespace allowed (consistent with tests)
    pattern = re.compile(f"^~{construct_name}\\s*\\(")
    match = pattern.match(line)
    if not match:
        return None

    # Find the opening parenthesis
    start_idx = match.end() - 1  # -1 to include the opening paren
    content, is_balanced = _parse_balanced_parentheses(line, start_idx)

    # Only return content if parentheses are properly balanced
    # This maintains original error handling for invalid syntax
    if content is not None and is_balanced:
        return (content,)

    return None


def _parse_statistical_arguments(line: str, construct_name: str) -> Optional[Tuple[str, ...]]:
    """
    Parse statistical assertion constructs with complex parameter parsing.
    Supports named parameters like timeout=5.0, confidence=0.95, etc.
    """
    import re

    # Match the construct pattern
    pattern = re.compile(f"^~{construct_name}\\s*\\(")
    match = pattern.match(line)
    if not match:
        return None

    # Find the opening parenthesis
    start_idx = match.end() - 1  # -1 to include the opening paren
    content, is_balanced = _parse_balanced_parentheses(line, start_idx)

    # Only return content if parentheses are properly balanced
    if content is not None and is_balanced:
        # Parse the complex arguments and return the original result
        if construct_name == "assert_eventually":
            result = _parse_assert_eventually_args(content)
            if result is not None:
                # Return original tuple - mypy should accept this due to type covariance
                return result  # type: ignore[return-value]
        elif construct_name == "assert_probability":
            prob_result = _parse_assert_probability_args(content)
            if prob_result is not None:
                # Return original tuple - mypy should accept this due to type covariance
                return prob_result  # type: ignore[return-value]

    return None


def _parse_loop_arguments(line: str, construct_name: str) -> Optional[Tuple[str]]:
    """
    Parse loop constructs with complex expression parsing.
    Handles nested parentheses in expressions like kinda_repeat(int(7.8))
    """
    import re

    # Match the construct pattern
    if construct_name == "kinda_repeat":
        pattern = re.compile(f"^~{construct_name}\\s*\\(")
    elif construct_name == "eventually_until":
        # eventually_until doesn't use parentheses, it uses condition directly
        # Handle it differently - find condition up to colon
        colon_pos = line.find(":")
        if colon_pos == -1:
            return None
        prefix = f"~{construct_name}\\s+"
        if not re.match(prefix, line):
            return None
        # Extract condition between construct name and colon
        match = re.match(prefix, line)
        if match:
            condition_start = match.end()
            condition = line[condition_start:colon_pos].strip()
            return (condition,) if condition else None
        return None
    else:
        return None

    # For kinda_repeat, parse the parentheses
    match = pattern.match(line)
    if not match:
        return None

    # Find the opening parenthesis
    start_idx = match.end() - 1  # -1 to include the opening paren
    content, is_balanced = _parse_balanced_parentheses(line, start_idx)

    # Only return content if parentheses are properly balanced and line ends with colon
    if content is not None and is_balanced:
        # Check if line ends with colon (with possible whitespace)
        remaining = line[
            match.end() - 1 + len(content) + 2 :
        ].strip()  # +2 for opening and closing parens
        if remaining.startswith(":"):
            return (content.strip(),)

    return None


def _parse_assert_eventually_args(
    content: str,
) -> Optional[Tuple[str, Optional[str], Optional[str]]]:
    """Parse assert_eventually arguments: condition, timeout=5.0, confidence=0.95"""
    import re

    # Split on commas that aren't inside parentheses, quotes, etc.
    args = _split_function_arguments(content)

    if not args:
        return None

    # First argument is always the condition
    condition = args[0].strip()

    # Parse optional named parameters
    timeout = None
    confidence = None

    for arg in args[1:]:
        arg = arg.strip()
        if "=" in arg:
            key, value = arg.split("=", 1)
            key = key.strip()
            value = value.strip()

            if key == "timeout":
                timeout = value
            elif key == "confidence":
                confidence = value

    return (condition, timeout, confidence)


def _parse_assert_probability_args(
    content: str,
) -> Optional[Tuple[str, Optional[str], Optional[str], Optional[str]]]:
    """Parse assert_probability arguments: event, expected_prob=0.5, tolerance=0.1, samples=1000"""
    import re

    # Split on commas that aren't inside parentheses, quotes, etc.
    args = _split_function_arguments(content)

    if not args:
        return None

    # First argument is always the event condition
    event = args[0].strip()

    # Parse optional named parameters
    expected_prob = None
    tolerance = None
    samples = None

    for arg in args[1:]:
        arg = arg.strip()
        if "=" in arg:
            key, value = arg.split("=", 1)
            key = key.strip()
            value = value.strip()

            if key == "expected_prob":
                expected_prob = value
            elif key == "tolerance":
                tolerance = value
            elif key == "samples":
                samples = value

    return (event, expected_prob, tolerance, samples)


def _split_function_arguments(content: str) -> List[str]:
    """Split function arguments on commas, respecting nested parentheses and strings."""
    args = []
    current_arg = []
    paren_depth = 0
    in_string = False
    string_char = None
    escaped = False
    iterations = 0

    for char in content:
        # DoS protection: Check iteration bounds
        iterations += 1
        if iterations > KINDA_MAX_PARSE_ITERATIONS:
            raise KindaSizeError(
                f"Parsing exceeded maximum iterations while splitting function arguments",
                limit_type="parse_iterations",
                current_value=iterations,
                max_value=KINDA_MAX_PARSE_ITERATIONS,
                context="function argument splitting",
            )

        if escaped:
            current_arg.append(char)
            escaped = False
            continue

        if char == "\\" and in_string:
            current_arg.append(char)
            escaped = True
            continue

        if not in_string:
            if char in "\"'":
                in_string = True
                string_char = char
                current_arg.append(char)
            elif char == "(":
                paren_depth += 1
                current_arg.append(char)
            elif char == ")":
                paren_depth -= 1
                current_arg.append(char)
            elif char == "," and paren_depth == 0:
                # Split here
                args.append("".join(current_arg))
                current_arg = []
            else:
                current_arg.append(char)
        else:
            # We're inside a string
            current_arg.append(char)
            if char == string_char:
                in_string = False
                string_char = None

    # Add the last argument
    if current_arg:
        args.append("".join(current_arg))

    return [arg.strip() for arg in args if arg.strip()]


def match_python_construct(line: str) -> Tuple[Optional[str], Optional[Any]]:
    """
    Enhanced Python construct matcher with robust parsing for all constructs.
    """
    # Clean matching - no debug spam
    # Check loop constructs first to avoid conflicts with conditional constructs
    for key in ["sometimes_while", "maybe_for", "kinda_repeat", "eventually_until"]:
        if key in KindaPythonConstructs:
            # Use enhanced parsing for kinda_repeat and eventually_until
            if key in ["kinda_repeat", "eventually_until"]:
                content = _parse_loop_arguments(line, key)
                if content is not None:
                    return key, content
            else:
                # Use original pattern matching for sometimes_while and maybe_for
                data = KindaPythonConstructs[key]
                pattern = data["pattern"]
                match = pattern.match(line.strip())
                if match:
                    return key, match.groups()

    # Then check other constructs
    for key, data in KindaPythonConstructs.items():
        # Skip loop constructs as they were already checked
        if key in ["sometimes_while", "maybe_for", "kinda_repeat", "eventually_until"]:
            continue
        elif key == "sorta_print":
            # Use enhanced sorta_print parsing
            content_str = _parse_sorta_print_arguments(line)
            if content_str is not None:
                return "sorta_print", (content_str,)
        elif key in ["maybe", "sometimes", "probably", "rarely"]:
            # Use enhanced conditional parsing with balanced parentheses
            content = _parse_conditional_arguments(line, key)
            if content is not None:
                return key, content
        elif key in ["assert_eventually", "assert_probability"]:
            # Use enhanced parsing for statistical assertions with balanced parentheses
            stat_content = _parse_statistical_arguments(line, key)
            if stat_content is not None:
                return key, stat_content
        else:
            if isinstance(data, dict) and "pattern" in data:
                pattern = data["pattern"]
                if hasattr(pattern, "match"):
                    match = pattern.match(line)
                    if match:
                        return key, match.groups()

    return None, None


def _find_expression_end(line: str, start_pos: int) -> int:
    """
    Find the end position of an expression starting at start_pos.
    Respects parentheses, brackets, strings, and stops at delimiters like comma, semicolon, etc.
    """
    paren_depth = 0
    bracket_depth = 0
    brace_depth = 0
    in_string = False
    string_char = None
    escaped = False
    pos = start_pos

    while pos < len(line):
        char = line[pos]

        if escaped:
            escaped = False
            pos += 1
            continue

        if char == "\\" and in_string:
            escaped = True
            pos += 1
            continue

        if not in_string:
            if char in "\"'":
                in_string = True
                string_char = char
            elif char == "(":
                paren_depth += 1
            elif char == ")":
                paren_depth -= 1
                if paren_depth < 0:
                    return pos
            elif char == "[":
                bracket_depth += 1
            elif char == "]":
                bracket_depth -= 1
            elif char == "{":
                brace_depth += 1
            elif char == "}":
                brace_depth -= 1
            elif char in ",:;#" and paren_depth == 0 and bracket_depth == 0 and brace_depth == 0:
                return pos
        else:
            if char == string_char:
                in_string = False
                string_char = None

        pos += 1

    return pos


def _is_inside_string_literal(line: str, position: int) -> bool:
    """Check if a position is inside a string literal (single or double quoted)."""
    # Early return for common cases
    if position >= len(line) or position < 0:
        return False

    # Quick check: if no quotes before position, not in string
    line_before_pos = line[:position]
    if not ('"' in line_before_pos or "'" in line_before_pos):
        return False

    in_string = False
    string_char = None
    escaped = False

    # Only iterate up to position for efficiency
    for i in range(position):
        char = line[i]

        if escaped:
            escaped = False
            continue

        if char == "\\" and in_string:
            escaped = True
            continue

        if not in_string:
            if char in "\"'":
                in_string = True
                string_char = char
        else:
            # We're inside a string
            if char == string_char:
                in_string = False
                string_char = None

    return in_string


def find_ish_constructs(line: str) -> List[Tuple[str, Any, int, int]]:
    """
    Find all ~ish constructs in a line for inline transformation.
    Returns a list of (construct_type, match_object, start_pos, end_pos).
    Only finds constructs that are NOT inside string literals.
    """
    constructs = []

    # Strategy: find all individual ~ish tokens and classify them based on context

    # Find all ish_value function calls (e.g., "ish_value(5)") - using pre-compiled pattern
    for match in _ISH_VALUE_FUNC_PATTERN.finditer(line):
        # Skip if inside string literal
        if _is_inside_string_literal(line, match.start()):
            continue
        constructs.append(("ish_value", match, match.start(), match.end()))

    # Find all ish_value patterns (e.g., "42~ish") - using pre-compiled pattern
    for match in _ISH_VALUE_PATTERN.finditer(line):
        # Skip if inside string literal
        if _is_inside_string_literal(line, match.start()):
            continue
        constructs.append(("ish_value", match, match.start(), match.end()))

    # Find ish_comparison patterns (e.g., "score ~ish 100") - using pre-compiled pattern
    # Look for variable followed by ~ish followed by a number (but don't overlap with ish_value)
    for match in _ISH_COMPARISON_PATTERN.finditer(line):
        # Skip if inside string literal
        if _is_inside_string_literal(line, match.start()):
            continue

        # Check if the right side is a number that was already captured as ish_value
        right_val = match.group(2)
        comparison_start = match.start()
        comparison_end = match.end()

        # Find if there's an ish_value that overlaps with the right side
        overlapping_value = None
        for i, (ctype, cmatch, cstart, cend) in enumerate(constructs):
            if ctype == "ish_value" and cstart < comparison_end and cend > comparison_start:
                overlapping_value = (i, ctype, cmatch, cstart, cend)
                break

        if overlapping_value:
            # Remove the overlapping ish_value and create nested structure
            constructs.pop(overlapping_value[0])
            # The comparison should include the full range including the trailing ~ish
            value_end_pos = overlapping_value[4]  # End position of the ish_value
            constructs.append(
                ("ish_comparison_with_ish_value", match, comparison_start, value_end_pos)
            )
        else:
            constructs.append(("ish_comparison", match, comparison_start, comparison_end))

    # Sort by position to handle transformations correctly
    constructs.sort(key=lambda x: x[2])

    return constructs


class _WelpMatch:
    """Match object for ~welp constructs (both prefix and infix syntax)."""

    def __init__(self, full_match: str, primary: str, fallback: str, start: int, end: int) -> None:
        self.full_match = full_match
        self.primary = primary
        self.fallback = fallback
        self.start_pos = start
        self.end_pos = end

    def group(self, n: int = 0) -> str:
        if n == 0:
            return self.full_match
        elif n == 1:
            return self.primary
        elif n == 2:
            return self.fallback
        else:
            raise IndexError("No such group")

    def start(self) -> int:
        return self.start_pos

    def end(self) -> int:
        return self.end_pos


def _transform_probabilistic_syntax(expression: str) -> str:
    """
    Helper function to transform ~construct syntax to function() syntax WITHOUT adding lambdas.
    This is used internally by transform_nested_constructs.

    CRITICAL BUG FIX (Issue #96 Bug 1): Now truly recursive - handles ALL nested constructs
    including those in conditional expressions, parenthesized expressions, and complex nesting.
    """
    import re

    transformed = expression
    probabilistic_constructs = ["sometimes", "maybe", "probably", "rarely"]

    # Process each type of construct
    for construct in probabilistic_constructs:
        # Pattern for ~construct(expr) - has explicit parentheses
        pattern_with_parens = re.compile(rf"~{construct}\s*\(")

        while True:
            match = pattern_with_parens.search(transformed)
            if not match:
                break

            # Find balanced parentheses
            start_paren = match.end() - 1
            content, is_balanced = _parse_balanced_parentheses(transformed, start_paren)

            if not is_balanced or content is None:
                break  # Stop if we can't parse balanced parens

            # Recursively transform the content (but don't add lambda)
            transformed_content = _transform_probabilistic_syntax(content)

            # Replace the matched construct
            end_paren = start_paren + len(content) + 2  # +2 for the parens
            replacement = f"{construct}({transformed_content})"
            transformed = transformed[: match.start()] + replacement + transformed[end_paren:]

        # Pattern for ~construct expr - no explicit parentheses around condition
        # FIX: Improved to handle complex expressions properly
        pattern_no_parens = re.compile(rf"~{construct}\s+(?!\()")

        while True:
            match = pattern_no_parens.search(transformed)
            if not match:
                break

            # Find the end of the argument expression
            # Need to handle Python expressions: literals, identifiers, if-else, operators, etc.
            condition_start = match.end()
            condition_end = _find_probabilistic_expression_end(transformed, condition_start)

            condition = transformed[condition_start:condition_end].strip()

            # Don't process empty conditions
            if not condition:
                break

            # Recursively transform the condition (but don't add lambda)
            transformed_condition = _transform_probabilistic_syntax(condition)

            # Replace the matched construct
            replacement = f"{construct}({transformed_condition})"
            transformed = transformed[: match.start()] + replacement + transformed[condition_end:]

    return transformed


def _find_probabilistic_expression_end(line: str, start_pos: int) -> int:
    """
    Find the end of a probabilistic expression argument.
    Handles Python expressions including:
    - Simple values: True, False, 42, 3.14, "string"
    - Conditionals: x if condition else y
    - Operators: x + y, x == y, etc.
    - Nested parentheses: (expr)
    - Function calls: func(args)

    Stops at:
    - Comma (at same depth)
    - Closing paren/bracket/brace (at outer depth)
    - Semicolon, hash (comment)
    - End of line
    """
    paren_depth = 0
    bracket_depth = 0
    brace_depth = 0
    in_string = False
    string_char = None
    escaped = False
    pos = start_pos

    # Track if we've seen 'if' to handle conditional expressions
    saw_if = False
    saw_else = False

    while pos < len(line):
        char = line[pos]

        if escaped:
            escaped = False
            pos += 1
            continue

        if char == "\\" and in_string:
            escaped = True
            pos += 1
            continue

        if not in_string:
            # Check for string delimiters
            if char in "\"'":
                in_string = True
                string_char = char
            # Track nesting depth
            elif char == "(":
                paren_depth += 1
            elif char == ")":
                paren_depth -= 1
                if paren_depth < 0:
                    return pos  # Hit closing paren at outer level
            elif char == "[":
                bracket_depth += 1
            elif char == "]":
                bracket_depth -= 1
                if bracket_depth < 0:
                    return pos  # Hit closing bracket at outer level
            elif char == "{":
                brace_depth += 1
            elif char == "}":
                brace_depth -= 1
                if brace_depth < 0:
                    return pos  # Hit closing brace at outer level
            # Stop conditions at same depth
            elif paren_depth == 0 and bracket_depth == 0 and brace_depth == 0:
                if char in ",;#":
                    return pos
                # Check for Python keywords that indicate expression boundaries
                # Extract word at current position
                if char.isalpha() or char == "_":
                    word_end = pos
                    while word_end < len(line) and (
                        line[word_end].isalnum() or line[word_end] == "_"
                    ):
                        word_end += 1
                    word = line[pos:word_end]

                    # Handle 'if' and 'else' keywords in conditional expressions
                    if word == "if":
                        saw_if = True
                        pos = word_end
                        continue
                    elif word == "else":
                        if saw_if:
                            # This is part of a conditional expression, keep going
                            saw_else = True
                            pos = word_end
                            continue
                        else:
                            # This might be a statement-level else, stop here
                            return pos
                    # Other keywords that end expressions
                    elif word in ["and", "or", "not", "is", "in"]:
                        # These are operators, keep going
                        pos = word_end
                        continue
                    elif word in [
                        "for",
                        "while",
                        "with",
                        "try",
                        "except",
                        "finally",
                        "class",
                        "def",
                        "return",
                        "yield",
                        "raise",
                        "import",
                        "from",
                        "as",
                        "lambda",
                    ]:
                        # These indicate statement boundaries or lambda (which we treat specially)
                        if word == "lambda":
                            # Lambda is complex, for now treat as expression continuation
                            pos = word_end
                            continue
                        else:
                            return pos
        else:
            # We're inside a string
            if char == string_char:
                in_string = False
                string_char = None

        pos += 1

    return pos


def transform_nested_constructs(expression: str) -> str:
    """
    Transform nested probabilistic constructs into lambdas for use in function arguments.

    This function detects probabilistic constructs (~sometimes, ~maybe, etc.) in expressions
    and wraps them in lambdas so they can be evaluated repeatedly.

    Example:
        "~sometimes True" -> "lambda: sometimes(True)"
        "~maybe x > 5" -> "lambda: maybe(x > 5)"
        "~sometimes (meta_result == ~sometimes True)" -> "lambda: sometimes(meta_result == sometimes(True))"

    Args:
        expression: The expression to transform

    Returns:
        Transformed expression with nested constructs wrapped in lambda if needed
    """
    # Strip whitespace
    expression = expression.strip()

    # Check if expression contains any probabilistic constructs
    probabilistic_constructs = ["sometimes", "maybe", "probably", "rarely"]
    has_probabilistic = any(f"~{c}" in expression for c in probabilistic_constructs)

    if not has_probabilistic:
        return expression

    # First, transform all the tilde syntax to function call syntax
    transformed = _transform_probabilistic_syntax(expression)

    # Then wrap the ENTIRE expression in a lambda (only once, at the top level)
    return f"lambda: {transformed}"


def find_welp_constructs(line: str) -> List[Tuple[str, Any, int, int]]:
    """
    Find all ~welp constructs in a line for inline transformation.
    Returns a list of (construct_type, match_object, start_pos, end_pos).
    Only finds constructs that are NOT inside string literals.

    Supports two syntaxes:
    1. Infix: expr ~welp fallback
    2. Prefix: ~welp expr fallback
    """
    constructs = []

    # First, check for prefix syntax (~welp expr fallback)
    # This must be done before infix syntax to avoid conflicts
    prefix_pattern = re.compile(r"~welp\s+")
    for prefix_match in prefix_pattern.finditer(line):
        prefix_pos = prefix_match.start()

        # Skip if inside string literal
        if _is_inside_string_literal(line, prefix_pos):
            continue

        # Check if this is at the start of a line/statement (after =, :, etc.)
        # to distinguish from infix usage
        is_prefix = False
        if prefix_pos == 0:
            is_prefix = True
        else:
            # Check characters before ~welp
            before = line[:prefix_pos].rstrip()
            if not before or before[-1] in "=,:;({[":
                is_prefix = True

        if not is_prefix:
            continue  # This is likely infix syntax, skip

        # Find the expression and fallback after ~welp
        remainder = line[prefix_match.end() :]

        # Parse the expression and fallback
        # Expression ends at the last space before fallback value
        # We need to find where expr ends and fallback begins
        # Split on spaces, but respect parentheses
        paren_depth = 0
        bracket_depth = 0
        in_string = False
        string_char = None
        escaped = False
        expr_end = -1

        for i, char in enumerate(remainder):
            if escaped:
                escaped = False
                continue

            if char == "\\" and in_string:
                escaped = True
                continue

            if not in_string:
                if char in "\"'":
                    in_string = True
                    string_char = char
                elif char == "(":
                    paren_depth += 1
                elif char == ")":
                    paren_depth -= 1
                elif char == "[":
                    bracket_depth += 1
                elif char == "]":
                    bracket_depth -= 1
                elif char.isspace() and paren_depth == 0 and bracket_depth == 0:
                    # Found potential split point
                    # Check if there's content after this space
                    if i + 1 < len(remainder) and not remainder[i + 1].isspace():
                        expr_end = i
            else:
                if char == string_char:
                    in_string = False
                    string_char = None

        if expr_end == -1:
            continue  # Couldn't find split point

        primary_expr = remainder[:expr_end].strip()
        fallback_value = remainder[expr_end:].strip()

        # Find actual end position (end of fallback, respecting delimiters)
        fallback_end_pos = _find_expression_end(line, prefix_match.end() + expr_end)
        fallback_value = line[prefix_match.end() + expr_end : fallback_end_pos].strip()

        if not primary_expr or not fallback_value:
            continue

        # Create match object for prefix syntax
        full_match = line[prefix_pos:fallback_end_pos]
        match_obj = _WelpMatch(
            full_match, primary_expr, fallback_value, prefix_pos, fallback_end_pos
        )
        constructs.append(("welp", match_obj, prefix_pos, fallback_end_pos))

    # Keep track of already-processed positions to avoid duplicates
    processed_positions = set()
    for _, _, start, end in constructs:
        for pos in range(start, end):
            processed_positions.add(pos)

    # Find all ~welp occurrences for infix syntax (expr ~welp fallback)
    welp_positions = []
    start = 0
    while True:
        pos = line.find("~welp", start)
        if pos == -1:
            break
        welp_positions.append(pos)
        start = pos + 1

    for welp_pos in welp_positions:
        # Skip if already processed as prefix syntax
        if welp_pos in processed_positions:
            continue

        # Skip if inside string literal
        if _is_inside_string_literal(line, welp_pos):
            continue

        # Find the expression before ~welp
        # Work backwards to find the start of the expression
        expr_start = welp_pos - 1

        # Skip whitespace before ~welp
        while expr_start >= 0 and line[expr_start].isspace():
            expr_start -= 1

        if expr_start < 0:
            continue

        # Find the actual start of the expression by looking for balanced parentheses/brackets
        # and assignment operators or delimiters
        paren_depth = 0
        bracket_depth = 0
        brace_depth = 0
        in_string = False
        string_char = None
        escaped = False

        # Scan backwards to find the start of the expression
        actual_start = expr_start
        for i in range(expr_start, -1, -1):
            char = line[i]

            if escaped:
                escaped = False
                continue

            if char == "\\" and in_string:
                escaped = True
                continue

            if not in_string:
                if char in "\"'":
                    in_string = True
                    string_char = char
                elif char == ")":
                    paren_depth += 1
                elif char == "(":
                    paren_depth -= 1
                    if paren_depth < 0:
                        # Found unmatched opening paren - this is the start boundary
                        actual_start = i + 1
                        break
                elif char == "]":
                    bracket_depth += 1
                elif char == "[":
                    bracket_depth -= 1
                    if bracket_depth < 0:
                        # Found unmatched opening bracket - this is the start boundary
                        actual_start = i + 1
                        break
                elif char == "}":
                    brace_depth += 1
                elif char == "{":
                    brace_depth -= 1
                    if brace_depth < 0:
                        # Found unmatched opening brace - this is the start boundary
                        actual_start = i + 1
                        break
                elif (
                    char in "=,;:" and paren_depth == 0 and bracket_depth == 0 and brace_depth == 0
                ):
                    # Found delimiter at same level - this is the start boundary
                    actual_start = i + 1
                    break
                elif (
                    char.isspace() and paren_depth == 0 and bracket_depth == 0 and brace_depth == 0
                ):
                    # Check if this whitespace is after a Python keyword
                    # that shouldn't be part of the expression (only at top level)
                    word_start = i + 1
                    while word_start < len(line) and line[word_start].isspace():
                        word_start += 1

                    # Look backwards to see if we have a keyword before this space
                    word_end = i
                    while (
                        word_end > 0
                        and not line[word_end - 1].isspace()
                        and line[word_end - 1].isalnum()
                    ):
                        word_end -= 1

                    if word_end < i:
                        keyword = line[word_end:i]
                        if keyword in [
                            "if",
                            "elif",
                            "while",
                            "for",
                            "return",
                            "yield",
                            "assert",
                            "del",
                        ]:
                            # Found keyword boundary - this is the start
                            actual_start = word_start
                            break
            else:
                if char == string_char:
                    in_string = False
                    string_char = None

            actual_start = i

        expr_start = actual_start

        # Skip leading whitespace
        while expr_start < welp_pos and line[expr_start].isspace():
            expr_start += 1

        # Extract the expression before ~welp
        expr_before = line[expr_start:welp_pos].strip()

        # Skip empty expressions
        if not expr_before:
            continue

        # Check if this is part of a ~sorta print construct
        if "print(" in expr_before:
            # Look further back to see if there's ~sorta
            check_start = max(0, expr_start - 10)
            prefix = line[check_start:expr_start].strip()
            if prefix.endswith("~sorta"):
                continue

        # Find the fallback value after ~welp
        fallback_start = welp_pos + 5  # Skip past '~welp'

        # Skip whitespace after ~welp
        while fallback_start < len(line) and line[fallback_start].isspace():
            fallback_start += 1

        if fallback_start >= len(line):
            continue

        # Find the end of the fallback expression
        # It ends at comma, closing paren/bracket/brace, or end of line
        fallback_end = fallback_start
        paren_depth = 0
        bracket_depth = 0
        brace_depth = 0
        in_string = False
        string_char = None
        escaped = False

        for i in range(fallback_start, len(line)):
            char = line[i]

            if escaped:
                escaped = False
                continue

            if char == "\\" and in_string:
                escaped = True
                continue

            if not in_string:
                if char in "\"'":
                    in_string = True
                    string_char = char
                elif char == "(":
                    paren_depth += 1
                elif char == ")":
                    paren_depth -= 1
                    if paren_depth < 0:
                        fallback_end = i
                        break
                elif char == "[":
                    bracket_depth += 1
                elif char == "]":
                    bracket_depth -= 1
                elif char == "{":
                    brace_depth += 1
                elif char == "}":
                    brace_depth -= 1
                elif (
                    char in ",:;#" and paren_depth == 0 and bracket_depth == 0 and brace_depth == 0
                ):
                    fallback_end = i
                    break
            else:
                if char == string_char:
                    in_string = False
                    string_char = None

            fallback_end = i + 1

        fallback_value = line[fallback_start:fallback_end].strip()

        if not fallback_value:
            continue

        # Create a match object for infix syntax
        full_match = line[expr_start:fallback_end]
        match_obj = _WelpMatch(full_match, expr_before, fallback_value, expr_start, fallback_end)

        constructs.append(("welp", match_obj, expr_start, fallback_end))

    return constructs
