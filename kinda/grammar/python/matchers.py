# kinda/grammar/python/matchers_py.py

from kinda.grammar.python.constructs import KindaPythonConstructs

def match_python_construct(line: str):
    # Clean matching - no debug spam
    for key, data in KindaPythonConstructs.items():
        pattern = data["pattern"]
        match = pattern.match(line)
        if match:
            return key, match.groups()

    return None, None