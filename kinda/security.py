# kinda/security.py

"""
Security protections for kinda-lang constructs

This module provides security utilities to protect against:
1. Code injection vulnerabilities
2. Deterministic subversion (random manipulation)
3. Resource exhaustion attacks
"""

import signal
from typing import Any, List

# Dangerous patterns that could enable code injection
DANGEROUS_PATTERNS = [
    "__import__(",
    "exec(",
    "eval(",
    "open(",
    "subprocess",
    "compile(",
    "globals()",
    "locals()",
    "vars()",
    "dir()",
]

# Patterns that could manipulate random number generation
RANDOM_MANIPULATION_PATTERNS = ["random.seed", "random.random", "setattr"]


def is_condition_dangerous(condition: Any) -> tuple[bool, str]:
    """
    Check if a condition contains dangerous patterns.

    Returns:
        tuple: (is_dangerous, reason)
    """
    condition_str = str(condition)

    # Check for dangerous code injection patterns
    for pattern in DANGEROUS_PATTERNS:
        if pattern in condition_str:
            return True, f"dangerous pattern detected: {pattern}"

    # Check for random manipulation attempts
    for pattern in RANDOM_MANIPULATION_PATTERNS:
        if pattern in condition_str:
            return True, f"random manipulation attempt: {pattern}"

    return False, ""


def safe_bool_eval(condition: Any, timeout_seconds: int = 1) -> bool:
    """
    Safely evaluate a condition as boolean with timeout protection.

    Args:
        condition: The condition to evaluate
        timeout_seconds: Maximum time to allow for evaluation

    Returns:
        bool: The boolean value of the condition

    Raises:
        TimeoutError: If evaluation takes too long
    """

    def timeout_handler(signum, frame):
        raise TimeoutError("Condition evaluation timed out")

    # Set up timeout protection
    old_handler = signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout_seconds)

    try:
        result = bool(condition)
        return result
    finally:
        # Always restore the original handler and cancel the alarm
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old_handler)


def secure_condition_check(condition: Any, construct_name: str) -> tuple[bool, bool]:
    """
    Perform a secure check of a condition with all protections.

    Args:
        condition: The condition to check
        construct_name: Name of the construct (for error messages)

    Returns:
        tuple: (should_proceed, condition_result)
               should_proceed: False if security blocked
               condition_result: The boolean result if allowed
    """
    condition_str = str(condition)

    # Check for dangerous code injection patterns first
    for pattern in DANGEROUS_PATTERNS:
        if pattern in condition_str:
            print(f"[security] {construct_name} blocked dangerous condition - nice try though")
            return False, False

    # Check for random manipulation patterns separately
    for pattern in RANDOM_MANIPULATION_PATTERNS:
        if pattern in condition_str:
            print(f"[security] {construct_name} won't let you break the chaos - that's not kinda")
            return False, False

    # Safely evaluate the condition with timeout
    try:
        condition_result = safe_bool_eval(condition)
        return True, condition_result
    except TimeoutError:
        print(f"[security] {construct_name} blocked slow condition evaluation - keeping it snappy")
        return False, False
