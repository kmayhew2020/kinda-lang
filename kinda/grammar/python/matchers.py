# kinda/grammar/python/matchers_py.py

from kinda.grammar.python.constructs import KindaPythonConstructs

def match_python_construct(line: str):
    print(f"[debug] Matching line: {line!r}")  # ✅ Add this debug print

    for key, data in KindaPythonConstructs.items():
        pattern = data["pattern"]
        match = pattern.match(line)
        if match:
            print(f"[debug] Matched construct: {key}")  # ✅ Add this too
            return key, match.groups()

    return None, None