# kinda/grammar/python/matchers_py.py

from kinda.grammar.python.constructs_py import KindaPythonConstructs

def match_python_construct(line: str):
    for key, data in KindaPythonConstructs.items():
        pattern = data["pattern"]
        match = pattern.match(line)
        if match:
            return key, match.groups()
    return None, None
