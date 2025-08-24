# kinda/grammar/python/matchers_py.py

import re
from kinda.grammar.python.constructs import KindaPythonConstructs

def match_python_construct(line: str):
    # Clean matching - no debug spam
    for key, data in KindaPythonConstructs.items():
        if key == "sorta_print":
            # Special handling for sorta_print to handle balanced parentheses
            # More robust pattern matching to handle various whitespace scenarios
            stripped = line.strip()
            
            # Match ~sorta followed by one or more whitespace, then print
            sorta_match = re.match(r'^~sorta\s+print\s*\(', stripped)
            if sorta_match:
                # Find the opening parenthesis after the matched pattern
                start_idx = line.find('(')
                if start_idx != -1:
                    # Find the matching closing parenthesis with string-aware parsing
                    paren_count = 0
                    end_idx = start_idx
                    in_string = False
                    string_char = None
                    escaped = False
                    
                    for i in range(start_idx, len(line)):
                        char = line[i]
                        
                        if escaped:
                            escaped = False
                            continue
                            
                        if char == '\\' and in_string:
                            escaped = True
                            continue
                            
                        if not in_string:
                            if char in ['"', "'"]:
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
                            if char == string_char and not escaped:
                                in_string = False
                                string_char = None
                    
                    if paren_count == 0 and not in_string:  # Found matching parenthesis and not in unclosed string
                        content = line[start_idx + 1:end_idx]
                        return "sorta_print", (content,)
                    elif in_string:
                        # Handle unclosed string gracefully - still try to parse what we have
                        # This allows for partial parsing and better error reporting
                        content = line[start_idx + 1:]
                        return "sorta_print", (content,)
        else:
            pattern = data["pattern"]
            match = pattern.match(line)
            if match:
                return key, match.groups()

    return None, None