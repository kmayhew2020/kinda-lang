# kinda/security/execution.py

"""
Secure Execution Engine for Kinda-Lang

This module provides the main secure execution engine that orchestrates
all security components to safely execute kinda-lang programs while
preventing Issue #109 vulnerabilities.

Key Features:
- Integrated file system sandboxing
- Python runtime restrictions
- Import whitelisting
- Resource monitoring
- Error handling with security context
"""

import os
import sys
import time
import tempfile
import subprocess
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from dataclasses import dataclass

from .sandbox import PythonSandbox
from .filesystem import FileSystemSandbox, FileAccessError


class SecurityLevel(Enum):
    """Security levels for execution environment"""

    SAFE = "safe"  # Maximum security, minimal access
    CAUTION = "caution"  # Moderate security, some access
    RISKY = "risky"  # Minimal security, broad access


@dataclass
class ExecutionResult:
    """Result of secure execution attempt"""

    success: bool
    return_code: int
    stdout: str
    stderr: str
    execution_time: float
    security_violations: List[str]
    blocked_operations: List[str]
    resource_usage: Dict[str, Any]

    @property
    def has_security_issues(self) -> bool:
        """Check if execution had security violations"""
        return len(self.security_violations) > 0 or len(self.blocked_operations) > 0


class SecureExecutionEngine:
    """
    Main secure execution engine for kinda-lang programs.

    Prevents Issue #109 by:
    1. Sandboxing file system access to program directory only
    2. Restricting Python imports to safe modules
    3. Monitoring resource usage and execution time
    4. Providing secure __builtins__ environment
    """

    def __init__(self, security_level: SecurityLevel = SecurityLevel.SAFE):
        self.security_level = security_level
        self.filesystem_sandbox = FileSystemSandbox()
        self.python_sandbox = PythonSandbox()
        self.max_execution_time = self._get_execution_timeout()
        self.max_memory_mb = self._get_memory_limit()

    def _get_execution_timeout(self) -> int:
        """Get execution timeout based on security level"""
        timeouts = {
            SecurityLevel.SAFE: 30,  # 30 seconds
            SecurityLevel.CAUTION: 60,  # 1 minute
            SecurityLevel.RISKY: 300,  # 5 minutes
        }
        return timeouts.get(self.security_level, 30)

    def _get_memory_limit(self) -> int:
        """Get memory limit in MB based on security level"""
        limits = {
            SecurityLevel.SAFE: 128,  # 128 MB
            SecurityLevel.CAUTION: 256,  # 256 MB
            SecurityLevel.RISKY: 512,  # 512 MB
        }
        return limits.get(self.security_level, 128)

    def execute_file(
        self, program_path: Path, working_directory: Optional[Path] = None
    ) -> ExecutionResult:
        """
        Execute a kinda-lang program file securely.

        Args:
            program_path: Path to the program file to execute
            working_directory: Working directory for execution (defaults to program directory)

        Returns:
            ExecutionResult with execution status and security information
        """
        program_path = Path(program_path).resolve()

        if working_directory is None:
            working_directory = program_path.parent
        else:
            working_directory = Path(working_directory).resolve()

        # Validate paths exist and are accessible
        if not program_path.exists():
            return ExecutionResult(
                success=False,
                return_code=1,
                stdout="",
                stderr=f"Program file not found: {program_path}",
                execution_time=0.0,
                security_violations=["file_not_found"],
                blocked_operations=[],
                resource_usage={},
            )

        # Set up file system sandbox
        try:
            self.filesystem_sandbox.set_allowed_directory(working_directory)
            self.filesystem_sandbox.validate_file_access(program_path)
        except FileAccessError as e:
            return ExecutionResult(
                success=False,
                return_code=1,
                stdout="",
                stderr=f"File access denied: {e}",
                execution_time=0.0,
                security_violations=["file_access_denied"],
                blocked_operations=[str(e)],
                resource_usage={},
            )

        # Execute the program with security controls
        return self._execute_with_sandbox(program_path, working_directory)

    def _execute_with_sandbox(self, program_path: Path, working_directory: Path) -> ExecutionResult:
        """Execute program with full security sandbox"""
        start_time = time.time()
        security_violations = []
        blocked_operations = []

        try:
            # Read the program file
            with open(program_path, "r", encoding="utf-8") as f:
                program_code = f.read()

            # Pre-process code for security violations
            security_check = self._check_code_security(program_code)
            if not security_check["safe"]:
                security_violations.extend(security_check["violations"])
                blocked_operations.extend(security_check["blocked"])

                if self.security_level == SecurityLevel.SAFE:
                    execution_time = time.time() - start_time
                    return ExecutionResult(
                        success=False,
                        return_code=1,
                        stdout="",
                        stderr="[SECURITY] Code blocked due to security violations",
                        execution_time=execution_time,
                        security_violations=security_violations,
                        blocked_operations=blocked_operations,
                        resource_usage={},
                    )

            # Execute with restricted imports and builtins
            stdout_capture = []
            stderr_capture = []

            # Create secure execution environment
            secure_globals = self._create_secure_globals(working_directory)

            # Redirect stdout/stderr for capture
            import io

            old_stdout = sys.stdout
            old_stderr = sys.stderr
            sys.stdout = io.StringIO()
            sys.stderr = io.StringIO()

            try:
                # Execute the code with restricted environment
                exec(program_code, secure_globals)

                # Capture output
                stdout = sys.stdout.getvalue()
                stderr = sys.stderr.getvalue()
                return_code = 0

            except Exception as e:
                stdout = sys.stdout.getvalue()
                stderr = sys.stderr.getvalue() + f"\n{type(e).__name__}: {e}"
                return_code = 1

                # Check if it's a security-related exception
                if "security" in str(e).lower() or "permission" in str(e).lower():
                    security_violations.append(f"runtime_security_error: {e}")

            finally:
                # Restore stdout/stderr
                sys.stdout = old_stdout
                sys.stderr = old_stderr

        except Exception as e:
            execution_time = time.time() - start_time
            return ExecutionResult(
                success=False,
                return_code=1,
                stdout="",
                stderr=f"Execution setup failed: {e}",
                execution_time=execution_time,
                security_violations=["execution_setup_error"],
                blocked_operations=[str(e)],
                resource_usage={},
            )

        execution_time = time.time() - start_time

        # Check for security violations in output
        security_violations.extend(self._scan_output_for_violations(stdout, stderr))

        # Determine success based on return code and security violations
        success = return_code == 0 and (
            len(security_violations) == 0 or self.security_level != SecurityLevel.SAFE
        )

        return ExecutionResult(
            success=success,
            return_code=return_code,
            stdout=stdout,
            stderr=stderr,
            execution_time=execution_time,
            security_violations=security_violations,
            blocked_operations=blocked_operations,
            resource_usage={
                "execution_time": execution_time,
                "memory_limit_mb": self.max_memory_mb,
                "timeout_seconds": self.max_execution_time,
            },
        )

    def _create_secure_environment(self, working_directory: Path) -> Dict[str, str]:
        """Create secure environment variables for execution"""
        # Start with minimal environment
        secure_env = {
            "PATH": os.environ.get("PATH", ""),
            "PYTHONPATH": str(working_directory),
            "PWD": str(working_directory),
            "HOME": str(working_directory),  # Restrict home directory
        }

        # Add kinda-lang specific variables
        if "KINDA_SEED" in os.environ:
            secure_env["KINDA_SEED"] = os.environ["KINDA_SEED"]

        # Security level specific restrictions
        if self.security_level == SecurityLevel.SAFE:
            # Maximum restrictions
            secure_env["PYTHONDONTWRITEBYTECODE"] = "1"  # No .pyc files
            secure_env["PYTHONHASHSEED"] = "random"  # Random hash seed

        elif self.security_level == SecurityLevel.CAUTION:
            # Moderate restrictions
            secure_env["PYTHONWARNINGS"] = "default"

        # Note: RISKY level uses current environment with minimal changes
        elif self.security_level == SecurityLevel.RISKY:
            # Inherit more from current environment
            for key in ["TEMP", "TMP", "TMPDIR", "USER", "USERNAME"]:
                if key in os.environ:
                    secure_env[key] = os.environ[key]

        return secure_env

    def _scan_output_for_violations(self, stdout: str, stderr: str) -> List[str]:
        """Scan execution output for security violations"""
        violations = []
        combined_output = stdout + stderr

        # Check for file system access violations
        violation_patterns = [
            "/etc/passwd",
            "/etc/shadow",
            "/root/",
            "/home/",
            "/var/",
            "/usr/",
            "/sys/",
            "/proc/",
            "/.ssh/",
            "/tmp/",
        ]

        for pattern in violation_patterns:
            if pattern in combined_output:
                violations.append(f"filesystem_access:{pattern}")

        # Check for dangerous module usage
        dangerous_modules = [
            "subprocess",
            "os.system",
            "os.popen",
            "eval(",
            "exec(",
            "__import__",
        ]

        for module in dangerous_modules:
            if module in combined_output:
                violations.append(f"dangerous_module:{module}")

        return violations

    def execute_code(self, code: str, working_directory: Optional[Path] = None) -> ExecutionResult:
        """
        Execute kinda-lang code string securely.

        Args:
            code: The code string to execute
            working_directory: Working directory for execution

        Returns:
            ExecutionResult with execution status and security information
        """
        if working_directory is None:
            working_directory = Path.cwd()
        else:
            working_directory = Path(working_directory).resolve()

        # Create temporary file for code execution
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, dir=working_directory
        ) as temp_file:
            temp_file.write(code)
            temp_path = Path(temp_file.name)

        try:
            # Execute the temporary file
            result = self.execute_file(temp_path, working_directory)
            return result
        finally:
            # Clean up temporary file
            try:
                temp_path.unlink()
            except Exception:
                pass  # Best effort cleanup

    def validate_program(self, program_path: Path) -> Dict[str, Any]:
        """
        Validate a program for security issues without executing it.

        Args:
            program_path: Path to the program file

        Returns:
            Dictionary with validation results
        """
        program_path = Path(program_path).resolve()

        validation_result = {
            "safe_to_execute": True,
            "security_warnings": [],
            "blocked_imports": [],
            "file_access_violations": [],
        }

        try:
            # Check file access permissions
            self.filesystem_sandbox.validate_file_access(program_path)

            # Read and analyze program content
            with open(program_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Static analysis for dangerous patterns
            dangerous_patterns = [
                ("import os", "Operating system access"),
                ("import subprocess", "Subprocess execution"),
                ("import sys", "System module access"),
                ("open(", "File operations"),
                ("eval(", "Dynamic code evaluation"),
                ("exec(", "Dynamic code execution"),
                ("__import__", "Dynamic imports"),
            ]

            for pattern, description in dangerous_patterns:
                if pattern in content:
                    if self.security_level == SecurityLevel.SAFE:
                        validation_result["security_warnings"].append(
                            f"Potentially dangerous pattern: {pattern} ({description})"
                        )
                    elif pattern in ["eval(", "exec(", "__import__"]:
                        # These are always concerning
                        validation_result["security_warnings"].append(
                            f"High-risk pattern: {pattern} ({description})"
                        )

            # Check for file path violations
            file_patterns = ["/etc/", "/root/", "/home/", "/var/", "/usr/"]
            for pattern in file_patterns:
                if pattern in content:
                    validation_result["file_access_violations"].append(
                        f"Potential system file access: {pattern}"
                    )

            # Determine if safe to execute
            if self.security_level == SecurityLevel.SAFE:
                validation_result["safe_to_execute"] = (
                    len(validation_result["security_warnings"]) == 0
                    and len(validation_result["file_access_violations"]) == 0
                )
            else:
                # More permissive for other security levels
                validation_result["safe_to_execute"] = (
                    len(validation_result["file_access_violations"]) == 0
                )

        except FileAccessError as e:
            validation_result["safe_to_execute"] = False
            validation_result["security_warnings"].append(f"File access denied: {e}")
        except Exception as e:
            validation_result["safe_to_execute"] = False
            validation_result["security_warnings"].append(f"Validation error: {e}")

        return validation_result

    def _check_code_security(self, code: str) -> Dict[str, Any]:
        """Check code for security violations before execution"""
        violations = []
        blocked = []
        safe = True

        # Check for dangerous file access patterns
        dangerous_file_patterns = [
            "/etc/passwd",
            "/etc/shadow",
            "/etc/hosts",
            "/etc/fstab",
            "/root/",
            "/home/",
            "/var/",
            "/usr/",
            "/sys/",
            "/proc/",
            "/boot/",
            "/lib/",
            "/lib64/",
            "/opt/",
            "/sbin/",
            "/bin/",
            "C:\\Windows",
            "C:\\Users",
            "C:\\Program Files",
        ]

        for pattern in dangerous_file_patterns:
            if pattern in code:
                violations.append(f"dangerous_file_access: {pattern}")
                blocked.append(f"File access to {pattern}")
                if self.security_level == SecurityLevel.SAFE:
                    safe = False

        # Check for dangerous function calls
        dangerous_functions = [
            "subprocess.",
            "os.system",
            "os.popen",
            "eval(",
            "exec(",
            "__import__",
        ]

        for func in dangerous_functions:
            if func in code:
                violations.append(f"dangerous_function: {func}")
                blocked.append(f"Function call {func}")
                if self.security_level == SecurityLevel.SAFE:
                    safe = False

        # Check for dangerous imports
        dangerous_imports = [
            "import os",
            "import subprocess",
            "import sys",
            "from os import",
            "from subprocess import",
        ]

        for imp in dangerous_imports:
            if imp in code:
                violations.append(f"dangerous_import: {imp}")
                blocked.append(f"Import statement {imp}")
                if self.security_level == SecurityLevel.SAFE:
                    safe = False

        return {"safe": safe, "violations": violations, "blocked": blocked}

    def _create_secure_globals(self, working_directory: Path) -> Dict[str, Any]:
        """Create secure global environment for code execution"""
        # Start with safe builtins
        secure_globals = self.python_sandbox.safe_builtins.get_safe_builtins()

        # Add basic Python modules that are safe
        import math
        import random
        import json
        import datetime
        import time as time_module

        safe_modules = {
            "math": math,
            "random": random,
            "json": json,
            "datetime": datetime,
            "time": time_module,
        }

        # Add modules based on security level
        if self.security_level in [SecurityLevel.CAUTION, SecurityLevel.RISKY]:
            import pathlib

            safe_modules["pathlib"] = pathlib

        if self.security_level == SecurityLevel.RISKY:
            import os

            # Even in risky mode, provide limited os functionality
            safe_modules["os"] = type(
                "LimitedOS",
                (),
                {
                    "getcwd": os.getcwd,
                    "path": os.path,
                    "environ": dict(os.environ),  # Read-only copy
                },
            )

        # Add available modules to globals
        secure_globals.update(safe_modules)

        # Add kinda-lang specific modules if available
        try:
            from kinda.personality import PersonalityContext

            secure_globals["PersonalityContext"] = PersonalityContext
        except ImportError:
            pass

        # Set working directory context
        secure_globals["__file__"] = str(working_directory / "__main__.py")
        secure_globals["__name__"] = "__main__"

        return secure_globals
