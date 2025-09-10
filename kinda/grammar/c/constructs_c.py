# kinda/grammar/c/constructs_c.py

import re

KindaCConstructs = {
    "kinda_int": {
        "type": "declaration",
        "pattern": re.compile(r"kinda int (\w+)\s*=\s*(.+?);"),
        "description": "Fuzzy integer declaration with noise",
    },
    "kinda_int_decl": {
        "type": "declaration",
        "pattern": re.compile(r"(\w+):\s*kinda int\s*=\s*(.+?);"),
        "description": "Fuzzy integer declaration with type annotation",
    },
    "sorta_print": {
        "type": "print",
        "pattern": re.compile(r"sorta print\s*\((.*)\)\s*;?"),
        "description": "Print with ~80% probability",
    },
    "sometimes": {
        "type": "conditional",
        "pattern": re.compile(r"sometimes\s*\(([^)]*)\)\s*\{"),
        "description": "Fuzzy conditional trigger (50% chance)",
    },
    "maybe": {
        "type": "conditional",
        "pattern": re.compile(r"maybe\s*\(([^)]*)\)\s*\{"),
        "description": "Fuzzy conditional trigger (60% chance)",
    },
    "fuzzy_reassign": {
        "type": "reassignment",
        "pattern": re.compile(r"(\w+)\s*~=\s*(.+?);"),
        "description": "Fuzzy reassignment to an existing variable",
    },
    "kinda_binary": {
        "type": "declaration",
        "pattern": re.compile(r"kinda\s+binary\s+(\w+)(?:\s*~\s*probabilities\s*\(([^)]+)\))?;?"),
        "description": "Three-state binary: positive (1), negative (-1), or neutral (0)",
    },
}
