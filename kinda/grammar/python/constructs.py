# kinda/grammar/constructs.py

import re

KindaPythonConstructs = {
    "kinda_int": {
        "type": "declaration",
        "pattern": re.compile(r'kinda int (\w+)\s*~=\s*(.+)'),
        "description": "Fuzzy integer declaration with noise",
        "body": (
            "def kinda_int(val):\n"
            "    fuzz = random.randint(-1, 1)\n"
            "    return val + fuzz"
        ),
    },
    "sorta_print": {
        "type": "print",
        "pattern": re.compile(r'sorta print\((.+)\)'),
        "description": "Print with ~70% probability",
        "body": (
            "def sorta_print(*args):\n"
            "    if random.random() < 0.8:\n"
            "        print('[print]', *args)\n"
            "    else:\n"
            "        print('[shrug]', *args)"
        ),
    },
    "sometimes": {
        "type": "conditional",
        "pattern": re.compile(r'sometimes: ?(.*)'),
        "description": "Fuzzy conditional trigger (50% chance)",
        "body": (
            "def sometimes():\n"
            "    return random.random() < 0.5"
        ),
    },
    "fuzzy_reassign": {
    "type": "reassignment",
    "pattern": re.compile(r'(\w+)\s*~=\s*(.+?);?$'),
    "description": "Fuzzy reassignment to an existing variable",
    "body": "# (not needed for now — handled in interpreter)",
    },
}
