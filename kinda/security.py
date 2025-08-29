# kinda/security.py

"""
Security protections for kinda-lang constructs

This module provides security utilities to protect against:
1. Code injection vulnerabilities
2. Deterministic subversion (random manipulation)
3. Resource exhaustion attacks

Security features include:
- Case-insensitive pattern matching to prevent bypass attempts
- Extended random manipulation detection including import statements
- Timeout protection for slow conditions (Unix systems)
- Comprehensive dangerous pattern detection
"""

import signal
from typing import Any, List, Tuple

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
    "vars(",  # Issue #8: vars() without parentheses bypass
    "dir()",
    "dir(",  # Issue #9: dir() without parentheses bypass
    "getattr(",  # Issue #10: getattr() method bypass
]

# Patterns that could manipulate random number generation
RANDOM_MANIPULATION_PATTERNS = [
    "random.seed",
    "random.random",
    "setattr",
    "from random import",
    "import random",
    "getattr(",  # Issue #11: getattr() random manipulation
    "__dict__",  # Issue #13: Direct __dict__ access bypass
]


def is_condition_dangerous(condition: Any) -> Tuple[bool, str]:
    """
    Check if a condition contains dangerous patterns.
    Uses case-insensitive matching to prevent bypasses.

    Returns:
        tuple: (is_dangerous, reason)
    """
    condition_str = str(condition).lower()  # Convert to lowercase for case-insensitive matching

    # Check for dangerous code injection patterns
    for pattern in DANGEROUS_PATTERNS:
        if pattern.lower() in condition_str:
            return True, f"dangerous pattern detected: {pattern}"

    # Check for random manipulation attempts with special handling for import statements
    for pattern in RANDOM_MANIPULATION_PATTERNS:
        pattern_lower = pattern.lower()
        if pattern_lower == "import random":
            # More precise matching for "import random" to avoid false positives
            # Issue #12: Improved regex handling for whitespace-obfuscated imports
            import re

            # Match "import random" with flexible whitespace and case insensitive
            if re.search(r"\bimport\s+random\b", condition_str, re.IGNORECASE):
                return True, f"random manipulation attempt: {pattern}"
        elif pattern_lower == "from random import":
            # Issue #12: Improved regex for "from random import" with flexible whitespace
            import re

            # Match "from random import" with flexible whitespace and case insensitive
            if re.search(r"\bfrom\s+random\s+import\b", condition_str, re.IGNORECASE):
                return True, f"random manipulation attempt: {pattern}"
        else:
            if pattern_lower in condition_str:
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

    # Check if SIGALRM is available (Unix-only)
    if hasattr(signal, "SIGALRM"):

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
    else:
        # Windows or other systems without SIGALRM - just evaluate directly
        # This is less secure but maintains compatibility
        result = bool(condition)
        return result


def secure_condition_check(condition: Any, construct_name: str) -> Tuple[bool, bool]:
    """
    Perform a secure check of a condition with all protections.
    Uses case-insensitive pattern matching to prevent bypasses.

    Args:
        condition: The condition to check
        construct_name: Name of the construct (for error messages)

    Returns:
        tuple: (should_proceed, condition_result)
               should_proceed: False if security blocked
               condition_result: The boolean result if allowed
    """
    condition_str = str(condition).lower()  # Case-insensitive matching

    # Check for dangerous code injection patterns first
    for pattern in DANGEROUS_PATTERNS:
        if pattern.lower() in condition_str:
            print(f"[security] {construct_name} blocked dangerous condition - nice try though")
            return False, False

    # Check for random manipulation patterns separately with special handling for import statements
    for pattern in RANDOM_MANIPULATION_PATTERNS:
        pattern_lower = pattern.lower()
        if pattern_lower == "import random":
            # More precise matching for "import random" to avoid false positives
            # Issue #12: Improved regex handling for whitespace-obfuscated imports
            import re

            # Match "import random" with flexible whitespace and case insensitive
            if re.search(r"\bimport\s+random\b", condition_str, re.IGNORECASE):
                print(
                    f"[security] {construct_name} won't let you break the chaos - that's not kinda"
                )
                return False, False
        elif pattern_lower == "from random import":
            # Issue #12: Improved regex for "from random import" with flexible whitespace
            import re

            # Match "from random import" with flexible whitespace and case insensitive
            if re.search(r"\bfrom\s+random\s+import\b", condition_str, re.IGNORECASE):
                print(
                    f"[security] {construct_name} won't let you break the chaos - that's not kinda"
                )
                return False, False
        else:
            if pattern_lower in condition_str:
                print(
                    f"[security] {construct_name} won't let you break the chaos - that's not kinda"
                )
                return False, False

    # Safely evaluate the condition with timeout
    try:
        condition_result = safe_bool_eval(condition)
        return True, condition_result
    except TimeoutError:
        print(f"[security] {construct_name} blocked slow condition evaluation - keeping it snappy")
        return False, False
