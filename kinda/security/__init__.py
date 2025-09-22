# kinda/security/__init__.py

"""
Kinda-Lang Security Framework

This module provides comprehensive security controls for kinda-lang execution,
preventing malicious file access and code execution vulnerabilities.

Components:
- execution.py: Main secure execution engine
- sandbox.py: Python runtime restrictions and safe builtins
- filesystem.py: File access controls and path validation

Security Model:
- File system sandboxing: Restrict access to program directory only
- Import restrictions: Whitelist safe Python modules, block dangerous imports
- Resource limits: Memory and execution time controls
- Runtime security: Custom __builtins__ with safe functions only

Usage:
    from kinda.security.execution import SecureExecutionEngine

    engine = SecureExecutionEngine()
    result = engine.execute_file(program_path, security_level="safe")
"""

from .execution import SecureExecutionEngine, SecurityLevel, ExecutionResult
from .sandbox import PythonSandbox, SafeBuiltins
from .filesystem import FileSystemSandbox, FileAccessError

# Import backward compatibility functions from old security.py
import importlib.util
import os

# Load the old security.py file for backward compatibility
security_path = os.path.join(os.path.dirname(__file__), "..", "security.py")
if os.path.exists(security_path):
    spec = importlib.util.spec_from_file_location("old_security", security_path)
    old_security = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(old_security)

    # Make old functions available
    secure_condition_check = old_security.secure_condition_check
    is_condition_dangerous = old_security.is_condition_dangerous
    safe_bool_eval = old_security.safe_bool_eval
    normalize_for_security_check = old_security.normalize_for_security_check

    # Make old constants available
    DANGEROUS_PATTERNS = old_security.DANGEROUS_PATTERNS
    RANDOM_MANIPULATION_PATTERNS = old_security.RANDOM_MANIPULATION_PATTERNS
else:
    # Fallback functions if old security.py is not available
    def secure_condition_check(condition, construct_name):
        return True, bool(condition)

    def is_condition_dangerous(condition):
        return False, ""

    def safe_bool_eval(condition, timeout_seconds=1):
        return bool(condition)

    def normalize_for_security_check(text):
        return text.lower()

    # Fallback constants
    DANGEROUS_PATTERNS = ["__import__(", "exec(", "eval(", "open("]
    RANDOM_MANIPULATION_PATTERNS = ["random.seed", "random.random", "setattr"]

__all__ = [
    "SecureExecutionEngine",
    "SecurityLevel",
    "ExecutionResult",
    "PythonSandbox",
    "SafeBuiltins",
    "FileSystemSandbox",
    "FileAccessError",
    "secure_condition_check",
    "is_condition_dangerous",
    "safe_bool_eval",
    "normalize_for_security_check",
    "DANGEROUS_PATTERNS",
    "RANDOM_MANIPULATION_PATTERNS",
]
