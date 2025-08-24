# kinda/grammar/python/matchers_py.py

from kinda.grammar.python.constructs import KindaPythonConstructs

def match_python_construct(line: str):
    # Clean matching - no debug spam
    for key, data in KindaPythonConstructs.items():
        if key == "sorta_print":
            # Special handling for sorta_print to handle balanced parentheses
            if line.strip().startswith('~sorta print'):
                # Find the opening parenthesis
                start_idx = line.find('(')
                if start_idx != -1:
                    # Find the matching closing parenthesis
                    paren_count = 0
                    end_idx = start_idx
                    for i in range(start_idx, len(line)):
                        if line[i] == '(':
                            paren_count += 1
                        elif line[i] == ')':
                            paren_count -= 1
                            if paren_count == 0:
                                end_idx = i
                                break
                    
                    if paren_count == 0:  # Found matching parenthesis
                        content = line[start_idx + 1:end_idx]
                        return "sorta_print", (content,)
        else:
            pattern = data["pattern"]
            match = pattern.match(line)
            if match:
                return key, match.groups()

    return None, None