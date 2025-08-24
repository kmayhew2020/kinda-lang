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