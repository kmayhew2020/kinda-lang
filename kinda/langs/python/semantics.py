# kinda/core/semantics.py

from typing import Dict, Any, List
from kinda.personality import chaos_random, chaos_choice

env: Dict[str, Any] = {}


def evaluate(expr: str) -> Any:
    try:
        return eval(expr, {}, env)
    except:
        return None


def kinda_assign(var: str, expr: str) -> None:
    value = evaluate(expr)
    if value is not None:
        if isinstance(value, (int, float)):
            value += chaos_choice([-1, 0, 1])
        env[var] = value
        print(f"[assign] {var} ~= {value}")
    else:
        print(f"[assign] {var} skipped (evaluation failed)")


def sorta_print(expr: str) -> None:
    if chaos_random() < 0.8:
        try:
            print(f"[print] {eval(expr, {}, env)}")
        except:
            print(f"[print] Failed to evaluate: {expr}")


def run_sometimes_block(condition: str, block_lines: List[str]) -> None:
    if chaos_random() < 0.7:
        if evaluate(condition):
            for line in block_lines:
                # TODO: process_line function does not exist in kinda.interpreter.__main__
                # This needs to be implemented or replaced with proper line execution
                # from kinda.interpreter.__main__ import process_line  # type: ignore[attr-defined]
                # process_line(line.strip())
                print(f"[TODO] Would execute: {line.strip()}")
        else:
            print("[sometimes] condition false")
    else:
        print("[sometimes] skipped randomly")
