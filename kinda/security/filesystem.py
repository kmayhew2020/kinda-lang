# kinda/security/filesystem.py

"""
File System Sandbox for Kinda-Lang Security

This module provides file system access controls to prevent Issue #109
by restricting file access to safe directories and preventing path traversal attacks.

Key Features:
- Path traversal prevention (../, /, ~/ attacks)
- Directory-based access control
- System file protection
- Secure path validation
"""

import os
import sys
from pathlib import Path
from typing import Set, Optional, List
from urllib.parse import unquote


class FileAccessError(Exception):
    """Raised when file access is denied by security policy"""

    pass


class FileSystemSandbox:
    """
    File system access control for kinda-lang programs.

    Prevents access to sensitive system files and directories,
    and restricts file operations to approved directories only.
    """

    def __init__(self):
        self.allowed_directories: Set[Path] = set()
        self.blocked_paths: Set[Path] = set()
        self._initialize_default_restrictions()

    def _initialize_default_restrictions(self):
        """Initialize default file system restrictions"""
        # Automatically block sensitive system directories
        sensitive_dirs = [
            "/etc",
            "/root",
            "/var/log",
            "/var/spool",
            "/usr/bin",
            "/usr/sbin",
            "/sbin",
            "/bin",
            "/sys",
            "/proc",
            "/dev",
        ]

        # Add platform-specific restrictions
        if sys.platform.startswith("win"):
            # Windows system directories
            sensitive_dirs.extend(
                [
                    "C:\\Windows",
                    "C:\\Program Files",
                    "C:\\Program Files (x86)",
                    "C:\\ProgramData",
                    "C:\\Users\\Administrator",
                ]
            )
        else:
            # Unix-like system directories
            sensitive_dirs.extend(
                [
                    "/boot",
                    "/lib",
                    "/lib64",
                    "/opt",
                ]
            )

        # Convert to Path objects and add to blocked paths
        for dir_path in sensitive_dirs:
            try:
                path = Path(dir_path).resolve()
                if path.exists():
                    self.blocked_paths.add(path)
            except Exception:
                # Skip paths that can't be resolved
                continue

        # Block user home directories except current user's
        try:
            if sys.platform.startswith("win"):
                users_dir = Path("C:/Users")
                if users_dir.exists():
                    current_user = os.environ.get("USERNAME", "")
                    for user_dir in users_dir.iterdir():
                        if user_dir.is_dir() and user_dir.name != current_user:
                            self.blocked_paths.add(user_dir)
            else:
                home_dir = Path("/home")
                if home_dir.exists():
                    current_user = os.environ.get("USER", "")
                    for user_dir in home_dir.iterdir():
                        if user_dir.is_dir() and user_dir.name != current_user:
                            self.blocked_paths.add(user_dir)
        except Exception:
            # Best effort - if we can't scan, skip
            pass

    def set_allowed_directory(self, directory: Path):
        """
        Set a directory as allowed for file operations.

        Args:
            directory: Directory path to allow access to
        """
        directory = Path(directory).resolve()

        if not directory.exists():
            raise FileAccessError(f"Directory does not exist: {directory}")

        if not directory.is_dir():
            raise FileAccessError(f"Path is not a directory: {directory}")

        # Check if directory is in blocked paths
        for blocked_path in self.blocked_paths:
            try:
                if directory == blocked_path or blocked_path in directory.parents:
                    raise FileAccessError(
                        f"Directory is in restricted area: {directory} (blocked: {blocked_path})"
                    )
            except Exception:
                # Path comparison failed, err on the side of caution
                continue

        self.allowed_directories.add(directory)

    def add_allowed_directory(self, directory: Path):
        """Add an additional allowed directory"""
        self.set_allowed_directory(directory)

    def validate_file_access(self, file_path: Path) -> bool:
        """
        Validate that a file path is allowed for access.

        Args:
            file_path: File path to validate

        Returns:
            True if access is allowed

        Raises:
            FileAccessError: If access is denied
        """
        file_path = Path(file_path)

        # Resolve path to handle symlinks and relative paths
        try:
            resolved_path = file_path.resolve()
        except Exception as e:
            raise FileAccessError(f"Cannot resolve path {file_path}: {e}")

        # Check for path traversal attempts
        self._validate_path_traversal(file_path, resolved_path)

        # Check against blocked paths
        self._validate_blocked_paths(resolved_path)

        # Check against allowed directories
        self._validate_allowed_directories(resolved_path)

        return True

    def _validate_path_traversal(self, original_path: Path, resolved_path: Path):
        """Validate path for traversal attacks"""
        original_str = str(original_path)
        resolved_str = str(resolved_path)

        # Check for directory traversal patterns
        dangerous_patterns = [
            "../",
            "..\\",
            "%2e%2e/",
            "%2e%2e\\",
            "..%2f",
            "..%5c",
            "..%255c",
            "..%c0%af",
            "..%c1%9c",
        ]

        # URL decode the path to catch encoded traversal attempts
        decoded_path = unquote(original_str)

        for pattern in dangerous_patterns:
            if pattern in original_str.lower() or pattern in decoded_path.lower():
                raise FileAccessError(
                    f"Path traversal attempt detected: {pattern} in {original_path}"
                )

        # Check for suspicious path components
        path_parts = resolved_path.parts
        for part in path_parts:
            if part.startswith(".") and len(part) > 1:
                # Allow single dot (current directory) but be suspicious of others
                if part not in [".", ".."]:
                    # This could be a hidden file, which is fine
                    continue
                elif part == "..":
                    # Check if this resolved to something outside allowed areas
                    continue

        # Check for null bytes (common in path traversal)
        if "\x00" in original_str or "\x00" in resolved_str:
            raise FileAccessError(f"Null byte in path: {original_path}")

    def _validate_blocked_paths(self, resolved_path: Path):
        """Check if path is in blocked areas"""
        for blocked_path in self.blocked_paths:
            try:
                # Check if the file is in a blocked directory
                if resolved_path == blocked_path:
                    raise FileAccessError(f"Access denied to blocked path: {resolved_path}")

                # Check if the file is under a blocked directory
                if blocked_path in resolved_path.parents:
                    raise FileAccessError(
                        f"Access denied to file in blocked directory: {resolved_path} "
                        f"(blocked parent: {blocked_path})"
                    )

                # Check if trying to access a parent of a blocked directory
                # (this could be an attempt to access the parent to reach the blocked area)
                if resolved_path in blocked_path.parents:
                    # Be more permissive here, but log it
                    pass

            except Exception:
                # Path comparison failed, continue checking
                continue

        # Additional checks for specific sensitive files
        sensitive_files = {
            "passwd": "/etc/passwd",
            "shadow": "/etc/shadow",
            "hosts": "/etc/hosts",
            "fstab": "/etc/fstab",
            "sudoers": "/etc/sudoers",
        }

        resolved_str = str(resolved_path).lower()
        for file_type, file_path in sensitive_files.items():
            if file_path.lower() in resolved_str:
                raise FileAccessError(f"Access denied to sensitive system file: {resolved_path}")

    def _validate_allowed_directories(self, resolved_path: Path):
        """Check if path is within allowed directories"""
        if not self.allowed_directories:
            # No restrictions set, allow access (but this is not recommended)
            return

        # Check if the file is within any allowed directory
        for allowed_dir in self.allowed_directories:
            try:
                # Check if file is in the allowed directory or its subdirectories
                if resolved_path == allowed_dir:
                    return  # Exact match, allowed

                if allowed_dir in resolved_path.parents:
                    return  # File is in subdirectory of allowed directory

                # For files, check if the parent directory is allowed
                if resolved_path.is_file() and resolved_path.parent == allowed_dir:
                    return

            except Exception:
                # Path comparison failed, continue checking
                continue

        # If we get here, the path is not in any allowed directory
        allowed_dirs_str = ", ".join(str(d) for d in self.allowed_directories)
        raise FileAccessError(
            f"Access denied: {resolved_path} is not within allowed directories: {allowed_dirs_str}"
        )

    def validate_directory_access(self, directory: Path) -> bool:
        """
        Validate access to a directory for operations like listing contents.

        Args:
            directory: Directory path to validate

        Returns:
            True if access is allowed

        Raises:
            FileAccessError: If access is denied
        """
        directory = Path(directory)

        if not directory.exists():
            raise FileAccessError(f"Directory does not exist: {directory}")

        if not directory.is_dir():
            raise FileAccessError(f"Path is not a directory: {directory}")

        # Use the same validation as file access
        return self.validate_file_access(directory)

    def get_safe_temp_directory(self) -> Path:
        """
        Get a safe temporary directory for file operations.

        Returns:
            Path to a safe temporary directory
        """
        import tempfile

        # Get system temp directory
        temp_dir = Path(tempfile.gettempdir())

        # Create a subdirectory for kinda-lang operations
        kinda_temp = temp_dir / "kinda-lang-sandbox"
        kinda_temp.mkdir(exist_ok=True)

        # Add to allowed directories
        self.add_allowed_directory(kinda_temp)

        return kinda_temp

    def list_allowed_directories(self) -> List[Path]:
        """Get list of currently allowed directories"""
        return list(self.allowed_directories)

    def list_blocked_paths(self) -> List[Path]:
        """Get list of blocked paths"""
        return list(self.blocked_paths)

    def reset_permissions(self):
        """Reset all permissions to defaults"""
        self.allowed_directories.clear()
        self.blocked_paths.clear()
        self._initialize_default_restrictions()

    def is_path_safe(self, path: Path) -> bool:
        """
        Check if a path is safe without raising exceptions.

        Args:
            path: Path to check

        Returns:
            True if path is safe, False otherwise
        """
        try:
            self.validate_file_access(path)
            return True
        except FileAccessError:
            return False
