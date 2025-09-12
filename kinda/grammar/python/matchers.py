# kinda/grammar/python/matchers.py

import re
from kinda.grammar.python.constructs import KindaPythonConstructs

# Compiled regex patterns for performance optimization
_SORTA_PRINT_PATTERN = re.compile(r"^\s*~sorta\s+print\s*\(")
_ISH_VALUE_PATTERN = re.compile(r"\b(\d+(?:\.\d+)?)\s*~ish")
_ISH_COMPARISON_PATTERN = re.compile(
    r"([a-zA-Z_][a-zA-Z0-9_]*)\s*~ish\s+([^~]+?)(?=\s+(?:and|or)|~|\)|\]|$|#|;|:)"
)
_WELP_PATTERN = re.compile(r'([^~"\']*)\s*~welp\s+([^\n]+)')
_STRING_DELIMITERS = re.compile(r'["\']{1,3}')


def _parse_sorta_print_arguments(line: str):
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

    # String-aware parentheses parsing
    paren_count = 0
    in_string = False
    string_char = None
    escaped = False
    end_idx = start_idx

    for i in range(start_idx, len(line)):
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


def _parse_balanced_parentheses(line: str, start_pos: int) -> tuple:
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

    for i in range(start_pos, len(line)):
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


def _parse_conditional_arguments(line: str, construct_name: str):
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
        return content

    return None


def _parse_statistical_arguments(line: str, construct_name: str):
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
        # Parse the complex arguments
        if construct_name == "assert_eventually":
            return _parse_assert_eventually_args(content)
        elif construct_name == "assert_probability":
            return _parse_assert_probability_args(content)

    return None


def _parse_assert_eventually_args(content: str):
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


def _parse_assert_probability_args(content: str):
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


def _split_function_arguments(content: str):
    """Split function arguments on commas, respecting nested parentheses and strings."""
    args = []
    current_arg = []
    paren_depth = 0
    in_string = False
    string_char = None
    escaped = False

    for char in content:
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


def match_python_construct(line: str):
    """
    Enhanced Python construct matcher with robust parsing for all constructs.
    """
    # Clean matching - no debug spam
    # Check loop constructs first to avoid conflicts with conditional constructs
    for key in ["sometimes_while", "maybe_for"]:
        if key in KindaPythonConstructs:
            data = KindaPythonConstructs[key]
            pattern = data["pattern"]
            match = pattern.match(line.strip())
            if match:
                return key, match.groups()

    # Then check other constructs
    for key, data in KindaPythonConstructs.items():
        # Skip loop constructs as they were already checked
        if key in ["sometimes_while", "maybe_for"]:
            continue
        elif key == "sorta_print":
            # Use enhanced sorta_print parsing
            content = _parse_sorta_print_arguments(line)
            if content is not None:
                return "sorta_print", (content,)
        elif key in ["maybe", "sometimes", "probably", "rarely"]:
            # Use enhanced conditional parsing with balanced parentheses
            content = _parse_conditional_arguments(line, key)
            if content is not None:
                return key, (content,)
        elif key in ["assert_eventually", "assert_probability"]:
            # Use enhanced parsing for statistical assertions with balanced parentheses
            content = _parse_statistical_arguments(line, key)
            if content is not None:
                return key, content
        else:
            pattern = data["pattern"]
            match = pattern.match(line)
            if match:
                return key, match.groups()

    return None, None


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


def find_ish_constructs(line: str):
    """
    Find all ~ish constructs in a line for inline transformation.
    Returns a list of (construct_type, match_object, start_pos, end_pos).
    Only finds constructs that are NOT inside string literals.
    """
    constructs = []

    # Strategy: find all individual ~ish tokens and classify them based on context

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


def find_welp_constructs(line: str):
    """
    Find all ~welp constructs in a line for inline transformation.
    Returns a list of (construct_type, match_object, start_pos, end_pos).
    Only finds constructs that are NOT inside string literals.
    """
    constructs = []

    # Find all ~welp occurrences in the line
    welp_positions = []
    start = 0
    while True:
        pos = line.find("~welp", start)
        if pos == -1:
            break
        welp_positions.append(pos)
        start = pos + 1

    for welp_pos in welp_positions:
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
                elif char in ",:;" and paren_depth == 0 and bracket_depth == 0 and brace_depth == 0:
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

        # Create a synthetic match object that mimics the old regex match
        class WelpMatch:
            def __init__(self, full_match, primary_expr, fallback_val, start, end):
                self.full_match = full_match
                self.primary_expr = primary_expr
                self.fallback_val = fallback_val
                self.start_pos = start
                self.end_pos = end

            def group(self, n=0):
                if n == 0:
                    return self.full_match
                elif n == 1:
                    return self.primary_expr
                elif n == 2:
                    return self.fallback_val
                else:
                    raise IndexError("No such group")

            def start(self):
                return self.start_pos

            def end(self):
                return self.end_pos

        full_match = line[expr_start:fallback_end]
        match_obj = WelpMatch(full_match, expr_before, fallback_value, expr_start, fallback_end)

        constructs.append(("welp", match_obj, expr_start, fallback_end))

    return constructs
