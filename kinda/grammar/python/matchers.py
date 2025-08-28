# kinda/grammar/python/matchers.py

import re
from kinda.grammar.python.constructs import KindaPythonConstructs

# Compiled regex patterns for performance optimization
_SORTA_PRINT_PATTERN = re.compile(r'^\s*~sorta\s+print\s*\(')
_ISH_VALUE_PATTERN = re.compile(r'\b(\d+(?:\.\d+)?)\s*~ish')
_ISH_VARIABLE_VALUE_PATTERN = re.compile(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*~ish(?!\s+\w)')
_ISH_COMPARISON_PATTERN = re.compile(r'(\w+)\s*~ish\s+([-+]?[\d.]+|[\w]+)')
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
    if start_idx >= len(line) or line[start_idx] != '(':
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
            
        if char == '\\' and in_string:
            escaped = True
            continue
            
        if not in_string:
            if char in '"\'':
                in_string = True
                string_char = char
            elif char == '(':
                paren_count += 1
            elif char == ')':
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
        content = line[start_idx + 1:end_idx]
        return content
    else:
        # Graceful handling of unclosed strings/parentheses
        # Return partial content for better error context
        content = line[start_idx + 1:]
        return content


def _parse_balanced_parentheses(line: str, start_pos: int) -> tuple:
    """
    Parse balanced parentheses starting from start_pos.
    Returns (content, is_balanced) - content inside parentheses and whether they were balanced.
    """
    if start_pos >= len(line) or line[start_pos] != '(':
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
            
        if char == '\\' and in_string:
            escaped = True
            continue
            
        if not in_string:
            if char in '"\'':
                in_string = True
                string_char = char
            elif char == '(':
                paren_count += 1
            elif char == ')':
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
        content = line[start_pos + 1:end_pos]
        return content, True
    else:
        # Unbalanced parentheses
        content = line[start_pos + 1:]
        return content, False


def _parse_conditional_arguments(line: str, construct_name: str):
    """
    Parse conditional constructs (~maybe, ~sometimes) with balanced parentheses support.
    Maintains compatibility with existing behavior and tests.
    """
    import re
    
    # Maintain original behavior: NO leading whitespace allowed (consistent with tests)
    pattern = re.compile(f'^~{construct_name}\\s*\\(')
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


def match_python_construct(line: str):
    """
    Enhanced Python construct matcher with robust parsing for all constructs.
    """
    # Clean matching - no debug spam
    for key, data in KindaPythonConstructs.items():
        if key == "sorta_print":
            # Use enhanced sorta_print parsing
            content = _parse_sorta_print_arguments(line)
            if content is not None:
                return "sorta_print", (content,)
        elif key in ["maybe", "sometimes"]:
            # Use enhanced conditional parsing with balanced parentheses
            content = _parse_conditional_arguments(line, key)
            if content is not None:
                return key, (content,)
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
            
        if char == '\\' and in_string:
            escaped = True
            continue
            
        if not in_string:
            if char in '"\'':
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
    
    # Find variable ish_value patterns (e.g., "player_level~ish")
    for match in _ISH_VARIABLE_VALUE_PATTERN.finditer(line):
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
            constructs.append(("ish_comparison_with_ish_value", match, comparison_start, value_end_pos))
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
        pos = line.find('~welp', start)
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
                
            if char == '\\' and in_string:
                escaped = True
                continue
                
            if not in_string:
                if char in '"\'':
                    in_string = True
                    string_char = char
                elif char == ')':
                    paren_depth += 1
                elif char == '(':
                    paren_depth -= 1
                    if paren_depth < 0:
                        # Found unmatched opening paren - this is the start boundary
                        actual_start = i + 1
                        break
                elif char == ']':
                    bracket_depth += 1
                elif char == '[':
                    bracket_depth -= 1
                    if bracket_depth < 0:
                        # Found unmatched opening bracket - this is the start boundary
                        actual_start = i + 1
                        break
                elif char == '}':
                    brace_depth += 1
                elif char == '{':
                    brace_depth -= 1
                    if brace_depth < 0:
                        # Found unmatched opening brace - this is the start boundary
                        actual_start = i + 1
                        break
                elif (char in '=,;:' and 
                      paren_depth == 0 and bracket_depth == 0 and brace_depth == 0):
                    # Found delimiter at same level - this is the start boundary
                    actual_start = i + 1
                    break
                elif (char.isspace() and 
                      paren_depth == 0 and bracket_depth == 0 and brace_depth == 0):
                    # Check if this whitespace is after a Python keyword
                    # that shouldn't be part of the expression (only at top level)
                    word_start = i + 1
                    while word_start < len(line) and line[word_start].isspace():
                        word_start += 1
                    
                    # Look backwards to see if we have a keyword before this space
                    word_end = i
                    while word_end > 0 and not line[word_end - 1].isspace() and line[word_end - 1].isalnum():
                        word_end -= 1
                    
                    if word_end < i:
                        keyword = line[word_end:i]
                        if keyword in ['if', 'elif', 'while', 'for', 'return', 'yield', 'assert', 'del']:
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
        if 'print(' in expr_before:
            # Look further back to see if there's ~sorta
            check_start = max(0, expr_start - 10)
            prefix = line[check_start:expr_start].strip()
            if prefix.endswith('~sorta'):
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
                
            if char == '\\' and in_string:
                escaped = True
                continue
                
            if not in_string:
                if char in '"\'':
                    in_string = True
                    string_char = char
                elif char == '(':
                    paren_depth += 1
                elif char == ')':
                    paren_depth -= 1
                    if paren_depth < 0:
                        fallback_end = i
                        break
                elif char == '[':
                    bracket_depth += 1
                elif char == ']':
                    bracket_depth -= 1
                elif char == '{':
                    brace_depth += 1
                elif char == '}':
                    brace_depth -= 1
                elif char in ',:;' and paren_depth == 0 and bracket_depth == 0 and brace_depth == 0:
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