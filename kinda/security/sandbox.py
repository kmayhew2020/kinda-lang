# kinda/security/sandbox.py

"""
Python Runtime Sandbox for Kinda-Lang Security

This module provides Python runtime restrictions and safe builtins to prevent
dangerous operations while maintaining kinda-lang functionality.

Key Features:
- Safe __builtins__ environment
- Import restrictions and whitelisting
- Runtime function monitoring
- Resource usage controls
"""

import sys
import builtins
import importlib
from typing import Dict, Set, Any, Optional, Callable
from pathlib import Path


class ImportError(Exception):
    """Raised when import is blocked by security policy"""

    pass


class SafeBuiltins:
    """
    Safe builtins environment for kinda-lang execution.

    Provides a restricted set of builtin functions that are safe for use,
    while blocking dangerous operations like eval, exec, open with system paths.
    """

    def __init__(self, filesystem_sandbox=None):
        self.filesystem_sandbox = filesystem_sandbox
        self._safe_builtins = self._create_safe_builtins()

    def _create_safe_builtins(self) -> Dict[str, Any]:
        """Create dictionary of safe builtin functions"""
        # Start with basic safe functions
        safe_functions = {
            # Type constructors
            "bool": bool,
            "int": int,
            "float": float,
            "str": str,
            "list": list,
            "tuple": tuple,
            "dict": dict,
            "set": set,
            "frozenset": frozenset,
            "bytes": bytes,
            "bytearray": bytearray,
            # Type checking
            "isinstance": isinstance,
            "issubclass": issubclass,
            "type": type,
            "hasattr": hasattr,
            "getattr": self._safe_getattr,
            "setattr": self._safe_setattr,
            "delattr": self._safe_delattr,
            # Iteration and sequences
            "len": len,
            "range": range,
            "enumerate": enumerate,
            "zip": zip,
            "reversed": reversed,
            "sorted": sorted,
            "filter": filter,
            "map": map,
            # Math functions
            "abs": abs,
            "max": max,
            "min": min,
            "sum": sum,
            "round": round,
            "divmod": divmod,
            "pow": pow,
            # String and representation
            "repr": repr,
            "ascii": ascii,
            "ord": ord,
            "chr": chr,
            "format": format,
            # Object operations
            "id": id,
            "hash": hash,
            # IO (restricted)
            "print": print,  # Standard print is usually safe
            "input": self._safe_input,
            "open": self._safe_open,
            # Iteration
            "iter": iter,
            "next": next,
            "all": all,
            "any": any,
            # Scope operations (restricted)
            "vars": self._safe_vars,
            "dir": self._safe_dir,
            "locals": self._safe_locals,
            "globals": self._safe_globals,
            # Exceptions
            "Exception": Exception,
            "ValueError": ValueError,
            "TypeError": TypeError,
            "AttributeError": AttributeError,
            "KeyError": KeyError,
            "IndexError": IndexError,
            "RuntimeError": RuntimeError,
            # Import (restricted)
            "__import__": self._safe_import,
            # Constants
            "True": True,
            "False": False,
            "None": None,
            "Ellipsis": Ellipsis,
            "NotImplemented": NotImplemented,
            # Utility
            "slice": slice,
            "property": property,
            "staticmethod": staticmethod,
            "classmethod": classmethod,
            "super": super,
        }

        return safe_functions

    def _safe_open(self, file, mode="r", **kwargs):
        """Safe file open with filesystem sandbox validation"""
        file_path = Path(file)

        # Validate file access if filesystem sandbox is available
        if self.filesystem_sandbox:
            try:
                self.filesystem_sandbox.validate_file_access(file_path)
            except Exception as e:
                raise PermissionError(f"File access denied by security policy: {e}")

        # Additional safety checks for mode
        safe_modes = {"r", "rb", "rt", "w", "wb", "wt", "a", "ab", "at", "x", "xb", "xt"}
        if mode not in safe_modes:
            raise ValueError(f"File mode '{mode}' not allowed")

        # Use builtin open with validated path
        return builtins.open(file, mode, **kwargs)

    def _safe_input(self, prompt=""):
        """Safe input function"""
        # Input is generally safe, but limit prompt length
        if len(str(prompt)) > 1000:
            raise ValueError("Input prompt too long")
        return builtins.input(prompt)

    def _safe_import(self, name, globals=None, locals=None, fromlist=(), level=0):
        """Safe import function with whitelist"""
        # Check if module is in allowed list
        if not self._is_module_allowed(name):
            raise ImportError(f"Module '{name}' is not allowed by security policy")

        try:
            return builtins.__import__(name, globals, locals, fromlist, level)
        except ImportError:
            # Re-raise import errors as-is
            raise
        except Exception as e:
            raise ImportError(f"Failed to import {name}: {e}")

    def _safe_getattr(self, obj, name, default=None):
        """Safe getattr with restrictions on dangerous attributes"""
        # Block access to potentially dangerous attributes
        dangerous_attrs = {
            "__globals__",
            "__code__",
            "__closure__",
            "__defaults__",
            "__dict__",
            "__class__",
            "__bases__",
            "__mro__",
            "__subclasses__",
            "func_globals",
            "func_code",
            "gi_frame",
            "cr_frame",
        }

        if name in dangerous_attrs:
            raise AttributeError(f"Access to attribute '{name}' is not allowed")

        if default is None:
            return builtins.getattr(obj, name)
        else:
            return builtins.getattr(obj, name, default)

    def _safe_setattr(self, obj, name, value):
        """Safe setattr with restrictions"""
        # Block modification of dangerous attributes
        dangerous_attrs = {
            "__globals__",
            "__code__",
            "__closure__",
            "__defaults__",
            "__dict__",
            "__class__",
            "__bases__",
        }

        if name in dangerous_attrs:
            raise AttributeError(f"Modification of attribute '{name}' is not allowed")

        return builtins.setattr(obj, name, value)

    def _safe_delattr(self, obj, name):
        """Safe delattr with restrictions"""
        # Block deletion of dangerous attributes
        dangerous_attrs = {
            "__globals__",
            "__code__",
            "__closure__",
            "__defaults__",
            "__dict__",
            "__class__",
        }

        if name in dangerous_attrs:
            raise AttributeError(f"Deletion of attribute '{name}' is not allowed")

        return builtins.delattr(obj, name)

    def _safe_vars(self, obj=None):
        """Safe vars function"""
        if obj is None:
            # Don't allow access to local variables without object
            raise RuntimeError("vars() without arguments is not allowed")
        return builtins.vars(obj)

    def _safe_dir(self, obj=None):
        """Safe dir function"""
        if obj is None:
            # Don't allow dir() without arguments (would show local scope)
            raise RuntimeError("dir() without arguments is not allowed")
        return builtins.dir(obj)

    def _safe_locals(self):
        """Safe locals function"""
        # Don't allow access to locals
        raise RuntimeError("locals() is not allowed")

    def _safe_globals(self):
        """Safe globals function"""
        # Don't allow access to globals
        raise RuntimeError("globals() is not allowed")

    def _is_module_allowed(self, module_name: str) -> bool:
        """Check if module is in whitelist"""
        # Whitelist of safe modules
        safe_modules = {
            # Standard library - data types
            "collections",
            "collections.abc",
            "array",
            "copy",
            "pprint",
            # Standard library - math and numbers
            "math",
            "cmath",
            "decimal",
            "fractions",
            "random",
            "statistics",
            # Standard library - strings and text
            "string",
            "re",
            "difflib",
            "textwrap",
            # Standard library - data formats
            "json",
            "csv",
            "configparser",
            # Standard library - dates and times
            "datetime",
            "time",
            "calendar",
            # Standard library - algorithms
            "itertools",
            "functools",
            "operator",
            # Kinda-lang specific modules
            "kinda",
            "kinda.personality",
            "kinda.security",
            # Limited I/O
            "io",
            "pathlib",
            # Testing (for test environments)
            "unittest",
            "pytest",
            # Type hints
            "typing",
        }

        # Check exact match first
        if module_name in safe_modules:
            return True

        # Check for submodules of allowed modules
        for safe_module in safe_modules:
            if module_name.startswith(safe_module + "."):
                return True

        # Special case for kinda submodules
        if module_name.startswith("kinda."):
            return True

        return False

    def get_safe_builtins(self) -> Dict[str, Any]:
        """Get the safe builtins dictionary"""
        return dict(self._safe_builtins)


class PythonSandbox:
    """
    Python runtime sandbox for secure execution.

    Manages the Python execution environment to prevent dangerous operations
    while allowing legitimate kinda-lang functionality.
    """

    def __init__(self):
        self.safe_builtins = SafeBuiltins()
        self.original_builtins = None
        self.blocked_modules: Set[str] = set()
        self.allowed_modules: Set[str] = set()
        self._initialize_module_restrictions()

    def _initialize_module_restrictions(self):
        """Initialize module import restrictions"""
        # Modules that are always blocked (os and sys are provided safely instead)
        self.blocked_modules.update(
            [
                "subprocess",
                "multiprocessing",
                "threading",
                "asyncio",
                "socket",
                "urllib",
                "http",
                "ftplib",
                "smtplib",
                "poplib",
                "imaplib",
                "telnetlib",
                "ctypes",
                "marshal",
                "pickle",
                "shelve",
                "dbm",
                "sqlite3",
                "importlib",
                "runpy",
                "types",
                "inspect",
                "gc",
                "weakref",
                "ast",
                "dis",
                "code",
                "codeop",
                "compileall",
            ]
        )

    def enter_sandbox(self, filesystem_sandbox=None):
        """
        Enter the sandbox environment.

        Args:
            filesystem_sandbox: Optional filesystem sandbox for file operations
        """
        # Store original builtins
        self.original_builtins = builtins.__dict__.copy()

        # Set up safe builtins
        if filesystem_sandbox:
            self.safe_builtins.filesystem_sandbox = filesystem_sandbox

        # Replace builtins with safe versions
        safe_builtins_dict = self.safe_builtins.get_safe_builtins()
        builtins.__dict__.clear()
        builtins.__dict__.update(safe_builtins_dict)

        # Monkey patch importlib if it's already loaded
        if "importlib" in sys.modules:
            original_import = sys.modules["importlib"].import_module
            sys.modules["importlib"].import_module = self._safe_importlib_import

    def exit_sandbox(self):
        """Exit the sandbox environment and restore original state"""
        if self.original_builtins:
            builtins.__dict__.clear()
            builtins.__dict__.update(self.original_builtins)
            self.original_builtins = None

    def _safe_importlib_import(self, name, package=None):
        """Safe importlib.import_module replacement"""
        if not self.safe_builtins._is_module_allowed(name):
            raise ImportError(f"Module '{name}' is not allowed by security policy")

        # Use original importlib functionality
        import importlib

        return importlib.import_module(name, package)

    def is_in_sandbox(self) -> bool:
        """Check if currently in sandbox mode"""
        return self.original_builtins is not None

    def add_allowed_module(self, module_name: str):
        """Add a module to the allowed list"""
        self.allowed_modules.add(module_name)

    def block_module(self, module_name: str):
        """Add a module to the blocked list"""
        self.blocked_modules.add(module_name)

    def validate_execution_environment(self) -> Dict[str, Any]:
        """
        Validate the current execution environment for security.

        Returns:
            Dictionary with validation results
        """
        validation: Dict[str, Any] = {
            "is_secure": True,
            "warnings": [],
            "violations": [],
        }

        # Check if dangerous modules are loaded
        dangerous_loaded = []
        for module_name in self.blocked_modules:
            if module_name in sys.modules:
                dangerous_loaded.append(module_name)

        if dangerous_loaded:
            validation["violations"].extend(
                [f"Dangerous module loaded: {module}" for module in dangerous_loaded]
            )
            validation["is_secure"] = False

        # Check builtins for dangerous functions
        current_builtins = set(builtins.__dict__.keys())
        dangerous_builtins = {"eval", "exec", "compile"}

        dangerous_in_builtins = current_builtins & dangerous_builtins
        if dangerous_in_builtins:
            validation["warnings"].extend(
                [f"Dangerous builtin available: {func}" for func in dangerous_in_builtins]
            )

        return validation
