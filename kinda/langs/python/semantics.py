# kinda/core/semantics.py

from kinda.personality import chaos_random, chaos_choice

env = {}


def evaluate(expr):
    try:
        return eval(expr, {}, env)
    except:
        return None


def kinda_assign(var, expr):
    value = evaluate(expr)
    if value is not None:
        if isinstance(value, (int, float)):
            value += chaos_choice([-1, 0, 1])
        env[var] = value
        print(f"[assign] {var} ~= {value}")
    else:
        print(f"[assign] {var} skipped (evaluation failed)")


def sorta_print(expr):
    if chaos_random() < 0.8:
        try:
            print(f"[print] {eval(expr, {}, env)}")
        except:
            print(f"[print] Failed to evaluate: {expr}")


def run_sometimes_block(condition, block_lines):
    if chaos_random() < 0.7:
        if evaluate(condition):
            for line in block_lines:
                from kinda.interpreter.__main__ import process_line

                process_line(line.strip())
        else:
            print("[sometimes] condition false")
    else:
        print("[sometimes] skipped randomly")
