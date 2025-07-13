# kinda/interpreter/__main__.py

import sys
import random
from kinda.grammar.matchers import match_construct
from kinda.grammar.semantics import kinda_assign, sorta_print, run_sometimes_block
from kinda.grammar.constructs import KindaConstructs

def process_line(line):
    line = line.strip()
    if not line or line.startswith("//"):
        return

    key, groups = match_construct(line)

    if key == "kinda int":
        var, expr = groups
        kinda_assign(var, expr)

    elif key == "~=":
        var, expr = groups
        kinda_assign(var, expr)

    elif key == "sorta print":
        (expr,) = groups
        sorta_print(expr)

    else:
        print(f"[warn] Unrecognized line: {line}")

def run_kinda_file(path):
    with open(path, 'r') as f:
        lines = f.readlines()

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("sometimes"):
            from re import match
            cond_match = match(KindaConstructs["sometimes"]["pattern"], line)
            if cond_match:
                condition = cond_match.group(1)
                block = []
                i += 1
                while i < len(lines) and not lines[i].strip().startswith("}"):
                    block.append(lines[i])
                    i += 1
                run_sometimes_block(condition, block)
        else:
            process_line(line)
        i += 1

if __name__ == "__main__":
    test_mode = False
    if "--test" in sys.argv:
        random.seed(42)
        test_mode = True
        sys.argv.remove("--test")

    if len(sys.argv) != 2:
        print("Usage: python -m kinda.interpreter [--test] <file.knda>")
    else:
        run_kinda_file(sys.argv[1])
