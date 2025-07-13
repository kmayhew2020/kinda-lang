# kinda/core/matchers.py

import re
from .constructs import KindaConstructs

def match_construct(line):
    for key, meta in KindaConstructs.items():
        match = re.match(meta["pattern"], line)
        if match:
            return key, match.groups()
    return None, None
