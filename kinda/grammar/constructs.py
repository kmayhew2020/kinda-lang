# kinda/core/constructs.py

KindaConstructs = {
    "kinda int": {
        "type": "declaration",
        "pattern": r'kinda int (\w+)\s*=\s*(.+);',
        "description": "Fuzzy integer declaration with noise",
    },
    "~=": {
        "type": "assignment",
        "pattern": r'(\w+)\s*~=\s*(.+);',
        "description": "Fuzzy reassignment",
    },
    "sorta print": {
        "type": "print",
        "pattern": r'sorta print\((.+)\);',
        "description": "80% chance to print",
    },
    "sometimes": {
        "type": "conditional",
        "pattern": r'sometimes\s*\((.+)\)\s*{',
        "description": "Fuzzy conditional block",
    },
}
