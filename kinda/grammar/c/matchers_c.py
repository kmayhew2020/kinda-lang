# kinda/grammar/c/matchers_c.py

import re
from .constructs_c import KindaCConstructs

def match_c_construct(line):
    """Match C kinda-lang constructs in the given line."""
    for key, meta in KindaCConstructs.items():
        match = meta["pattern"].match(line.strip())
        if match:
            return key, match.groups()
    return None, None
