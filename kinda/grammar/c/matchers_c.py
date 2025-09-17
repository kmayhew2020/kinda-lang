# kinda/grammar/c/matchers_c.py

import re
from typing import Optional, Tuple, Any
from .constructs_c import KindaCConstructs


def match_c_construct(line: str) -> Tuple[Optional[str], Optional[Tuple[Any, ...]]]:
    """Match C kinda-lang constructs in the given line."""
    for key, meta in KindaCConstructs.items():
        pattern = meta["pattern"]
        if hasattr(pattern, "match"):
            match = pattern.match(line.strip())
            if match:
                return key, match.groups()
    return None, None
