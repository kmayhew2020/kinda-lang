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
    
    # Find all occurrences of ~welp that are not in strings
    welp_positions = []
    for match in re.finditer(r'~welp\b', line):
        if not _is_inside_string_literal(line, match.start()):
            welp_positions.append(match.start())
    
    # Process each welp construct
    for welp_start in welp_positions:
        # Find the primary expression by working backwards with proper balance
        primary_start = _find_balanced_expr_start(line, welp_start - 1)
        primary_expr = line[primary_start:welp_start].strip()
        
        # Find the fallback expression by working forwards
        fallback_start = welp_start + 5  # len("~welp")
        while fallback_start < len(line) and line[fallback_start].isspace():
            fallback_start += 1
        fallback_end = _find_balanced_expr_end(line, fallback_start)
        fallback_expr = line[fallback_start:fallback_end].strip()
        
        if primary_expr and fallback_expr:
            # Create a custom match-like object
            class TrimmedMatch:
                def __init__(self, text, group1, group2):
                    self.text = text
                    self.group1 = group1
                    self.group2 = group2
                def group(self, n=0):
                    if n == 0:
                        return self.text
                    elif n == 1:
                        return self.group1
                    elif n == 2:
                        return self.group2
                    return None
            
            match_text = f"{primary_expr} ~welp {fallback_expr}"
            trimmed_match = TrimmedMatch(match_text, primary_expr, fallback_expr)
            constructs.append(("welp", trimmed_match, primary_start, fallback_end))
    
    return constructs


def _find_balanced_expr_start(line: str, pos: int) -> int:
    """Find the start of an expression by working backwards with balanced delimiters."""
    # Skip whitespace
    while pos >= 0 and line[pos].isspace():
        pos -= 1
    
    if pos < 0:
        return 0
    
    # Track balance - start balanced (we're looking for the expression start)
    paren_count = 0
    bracket_count = 0
    brace_count = 0
    
    while pos >= 0:
        char = line[pos]
        
        if _is_inside_string_literal(line, pos):
            pos -= 1
            continue
            
        if char in ')]}':
            if char == ')':
                paren_count += 1
            elif char == ']':
                bracket_count += 1
            elif char == '}':
                brace_count += 1
        elif char in '([{':
            if char == '(':
                paren_count -= 1
                # If we're now unbalanced (more opens than closes), stop here
                if paren_count < 0:
                    return pos + 1  # Expression starts after the opening paren
            elif char == '[':
                bracket_count -= 1
                if bracket_count < 0:
                    return pos + 1
            elif char == '{':
                brace_count -= 1
                if brace_count < 0:
                    return pos + 1
        elif paren_count == 0 and bracket_count == 0 and brace_count == 0:
            # At top level - stop at major delimiters
            if char in '=,;':
                return pos + 1
            # Check if we're at the end of a Python keyword
            elif char.isspace() and pos > 0:
                # Look backwards to see if we just passed a keyword
                word_end = pos
                word_start = pos - 1
                while word_start >= 0 and (line[word_start].isalnum() or line[word_start] == '_'):
                    word_start -= 1
                word_start += 1
                if word_start < word_end:
                    word = line[word_start:word_end]
                    if word in ['if', 'elif', 'else', 'for', 'while', 'try', 'except', 'finally', 'with', 'def', 'class', 'return', 'yield', 'raise', 'import', 'from']:
                        # Stop after the keyword (include the space)
                        return word_end
                
        pos -= 1
    
    return 0


def _find_balanced_expr_end(line: str, pos: int) -> int:
    """Find the end of an expression by working forwards with balanced delimiters."""
    paren_count = 0
    bracket_count = 0
    brace_count = 0
    length = len(line)
    
    while pos < length:
        char = line[pos]
        
        if _is_inside_string_literal(line, pos):
            pos += 1
            continue
            
        if char in '([{':
            if char == '(':
                paren_count += 1
            elif char == '[':
                bracket_count += 1
            elif char == '{':
                brace_count += 1
        elif char in ')]}':
            if char == ')':
                paren_count -= 1
                if paren_count < 0:
                    return pos
            elif char == ']':
                bracket_count -= 1
                if bracket_count < 0:
                    return pos
            elif char == '}':
                brace_count -= 1
                if brace_count < 0:
                    return pos
        elif paren_count == 0 and bracket_count == 0 and brace_count == 0:
            # At top level - stop at delimiters
            if char in ',;)]}:':
                return pos
                
        pos += 1
    
    return length


def _skip_whitespace(line: str, pos: int) -> int:
    """Skip whitespace characters starting from position."""
    while pos < len(line) and line[pos].isspace():
        pos += 1
    return pos