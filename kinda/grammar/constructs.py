# kinda/grammar/constructs.py

KindaConstructs = {
    "kinda int": {
        "type": "declaration",
        "pattern": r'kinda int (\w+)\s*=\s*(.+);',
        "description": "Fuzzy integer declaration with noise",
        "runtime": {
            "python": (
                "def kinda_int(name, value):\n"
                "    import random\n"
                "    noisy = value + random.randint(-2, 2)\n"
                "    globals()[name] = noisy\n"
                "    print(f\"[assign] {name} ~= {noisy}\")\n"
                "    return noisy"
            )
        }
    },
    "~=": {
        "type": "assignment",
        "pattern": r'(\w+)\s*~=\s*(.+);',
        "description": "Fuzzy reassignment",
        "runtime": {
            "python": "def fuzzy_assign(name, value):\n    import random\n    noisy = value + random.randint(-2, 2)\n    globals()[name] = noisy\n    print(f\"[assign] {name} ~= {noisy}\")"
        }
    },
        "sorta print": {
        "type": "print",
        "pattern": r'sorta print\((.+)\);',
        "description": "80% chance to print",
        "runtime": {
            "python": "def sorta_print(*args):\n    import random\n    if random.random() < 0.8:\n        print('[print]', *args)"
        }
    },
    "sometimes": {
        "type": "conditional",
        "pattern": r'sometimes\s*\((.+)\)\s*{',
        "description": "Fuzzy conditional block",
        "runtime": {
            "python": (
                "def sometimes(condition):\n"
                "    import random\n"
                "    return condition and random.random() < 0.5"
            )
        }
    }
}
