# kinda/grammar/python/matchers.py

import re
from kinda.grammar.python.constructs import KindaPythonConstructs


def _parse_sorta_print_arguments(line: str):
    """
    Robust parsing of ~sorta print arguments with string-aware parentheses matching.
    Handles nested function calls, complex expressions, and string literals.
    """
    import re
    
    # Flexible regex to handle whitespace variations
    sorta_pattern = re.compile(r'^\s*~sorta\s+print\s*\(')
    match = sorta_pattern.match(line)
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


def match_python_construct(line: str):
    """
    Enhanced Python construct matcher with robust ~sorta print parsing.
    """
    # Clean matching - no debug spam
    for key, data in KindaPythonConstructs.items():
        if key == "sorta_print":
            # Use enhanced sorta_print parsing
            content = _parse_sorta_print_arguments(line)
            if content is not None:
                return "sorta_print", (content,)
        else:
            pattern = data["pattern"]
            match = pattern.match(line)
            if match:
                return key, match.groups()

    return None, None


def _is_inside_string_literal(line: str, position: int) -> bool:
    """Check if a position is inside a string literal (single or double quoted)."""
    in_string = False
    string_char = None
    escaped = False
    
    for i, char in enumerate(line):
        if i >= position:
            return in_string
            
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
    
    # Find all ish_value patterns (e.g., "42~ish")
    ish_value_pattern = re.compile(r'(\d+(?:\.\d+)?)~ish')
    for match in ish_value_pattern.finditer(line):
        # Skip if inside string literal
        if _is_inside_string_literal(line, match.start()):
            continue
        constructs.append(("ish_value", match, match.start(), match.end()))
    
    # Find ish_comparison patterns (e.g., "score ~ish 100")
    # Look for variable followed by ~ish followed by a number (but don't overlap with ish_value)
    ish_comparison_pattern = re.compile(r'(\w+)\s*~ish\s+(\w+)')
    for match in ish_comparison_pattern.finditer(line):
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
    
    # Find welp patterns (e.g., "api_call() ~welp default_value")
    welp_pattern = re.compile(r'(.+)\s*~welp\s*(.+)')
    for match in welp_pattern.finditer(line):
        # Skip if inside string literal
        if _is_inside_string_literal(line, match.start()):
            continue
        constructs.append(("welp", match, match.start(), match.end()))
    
    return constructs