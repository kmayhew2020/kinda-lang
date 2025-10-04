"""
Custom exceptions for the Kinda language compiler and runtime.
"""


class KindaError(Exception):
    """Base exception for all Kinda-related errors."""

    pass


class KindaSyntaxError(KindaError):
    """Raised when invalid Kinda syntax is encountered."""

    pass


class KindaSizeError(KindaError):
    """
    Raised when input exceeds parser safety limits.

    This exception is raised to prevent Denial of Service (DoS) attacks
    through maliciously large or complex input files. It enforces limits on:
    - File size
    - Line length
    - Parsing iterations
    - String literal size

    Attributes:
        message: Human-readable error message
        limit_type: Type of limit exceeded ('file_size', 'line_length',
                   'parse_iterations', 'string_size')
        current_value: The actual value that exceeded the limit
        max_value: The maximum allowed value
        context: Additional context (e.g., line number, file path)
    """

    def __init__(
        self, message: str, limit_type: str, current_value: int, max_value: int, context: str = ""
    ):
        super().__init__(message)
        self.limit_type = limit_type
        self.current_value = current_value
        self.max_value = max_value
        self.context = context

    def __str__(self) -> str:
        """Generate helpful error message with actionable suggestions."""
        base_msg = super().__str__()

        suggestions = {
            "file_size": "Consider splitting the file into smaller modules or increasing KINDA_MAX_FILE_SIZE.",
            "line_length": "Break this line into multiple lines or increase KINDA_MAX_LINE_LENGTH.",
            "parse_iterations": "The input may contain deeply nested constructs. Simplify the structure or increase KINDA_MAX_PARSE_ITERATIONS.",
            "string_size": "Break large string literals into smaller chunks or increase KINDA_MAX_STRING_SIZE.",
        }

        suggestion = suggestions.get(self.limit_type, "Check the input for malformed constructs.")

        details = f"\n  Limit type: {self.limit_type}"
        details += f"\n  Current value: {self.current_value:,}"
        details += f"\n  Maximum allowed: {self.max_value:,}"

        if self.context:
            details += f"\n  Context: {self.context}"

        details += f"\n  Suggestion: {suggestion}"

        return f"{base_msg}{details}"


class KindaRuntimeError(KindaError):
    """Raised when a runtime error occurs during execution."""

    pass


class KindaSecurityError(KindaError):
    """Raised when a security violation is detected."""

    pass
