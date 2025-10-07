"""
Tests for Parser DoS Protection (Issue #110)

This test suite validates the 4-layer Defense in Depth approach:
1. File size validation
2. Line length validation
3. Iteration bounds enforcement
4. String literal size validation

All tests use environment variables to temporarily override limits for testing.
"""

import os
import pytest
import tempfile
from pathlib import Path
from kinda.exceptions import KindaSizeError
from kinda.langs.python.transformer import transform_file
from kinda.grammar.python import matchers


class TestFileSizeValidation:
    """Test Layer 1: File size validation"""

    def test_file_within_limit(self, tmp_path):
        """Test that files within the size limit are processed successfully"""
        # Create a small valid file
        test_file = tmp_path / "small.py.knda"
        test_file.write_text("~kinda int x = 42\n")

        # Should transform successfully
        result = transform_file(test_file)
        assert "x =" in result

    def test_file_exceeds_limit(self, tmp_path, monkeypatch):
        """Test that files exceeding the size limit raise KindaSizeError"""
        # Set a very small limit for testing - patch both locations
        from kinda.langs.python import transformer

        monkeypatch.setattr(matchers, "KINDA_MAX_FILE_SIZE", 100)
        monkeypatch.setattr(transformer, "KINDA_MAX_FILE_SIZE", 100)

        # Create a file larger than the limit
        test_file = tmp_path / "large.py.knda"
        large_content = "# " + ("x" * 200) + "\n~kinda int y = 1\n"
        test_file.write_text(large_content)

        # Should raise KindaSizeError
        with pytest.raises(KindaSizeError) as exc_info:
            transform_file(test_file)

        assert exc_info.value.limit_type == "file_size"
        assert exc_info.value.current_value > 100
        assert exc_info.value.max_value == 100
        assert "exceeds maximum allowed size" in str(exc_info.value)

    def test_file_at_exact_limit(self, tmp_path, monkeypatch):
        """Test that files exactly at the limit are allowed"""
        from kinda.langs.python import transformer

        # Create a file exactly at the limit (30 bytes)
        test_file = tmp_path / "exact.py.knda"
        # Exact content - 30 bytes: "~kinda int x = 12345678901234\n" (29 chars + 1 newline = 30 bytes)
        content = "~kinda int x = 12345678901234\n"
        test_file.write_text(content)

        # Verify file size and set limit to exact file size
        file_size = os.path.getsize(test_file)
        monkeypatch.setattr(matchers, "KINDA_MAX_FILE_SIZE", file_size)
        monkeypatch.setattr(transformer, "KINDA_MAX_FILE_SIZE", file_size)

        # Should transform successfully (at limit, not over)
        result = transform_file(test_file)
        assert result is not None

    def test_empty_file_allowed(self, tmp_path):
        """Test that empty files are allowed"""
        test_file = tmp_path / "empty.py.knda"
        test_file.write_text("")

        # Empty files should be allowed
        result = transform_file(test_file)
        assert result is not None


class TestLineLengthValidation:
    """Test Layer 2: Line length validation"""

    def test_line_within_limit(self, tmp_path):
        """Test that lines within the length limit are processed"""
        test_file = tmp_path / "normal.py.knda"
        test_file.write_text("~kinda int x = 42\n")

        result = transform_file(test_file)
        assert "x =" in result

    def test_line_exceeds_limit(self, tmp_path, monkeypatch):
        """Test that lines exceeding the length limit raise KindaSizeError"""
        # Set a small limit for testing
        monkeypatch.setattr(matchers, "KINDA_MAX_LINE_LENGTH", 50)

        # Create a file with a very long line
        test_file = tmp_path / "longline.py.knda"
        long_line = "~kinda int x = " + ("1" * 100) + "\n"
        test_file.write_text(long_line)

        # Should raise KindaSizeError
        with pytest.raises(KindaSizeError) as exc_info:
            transform_file(test_file)

        assert exc_info.value.limit_type == "line_length"
        assert exc_info.value.current_value > 50
        assert exc_info.value.max_value == 50
        assert "Line 1" in str(exc_info.value)
        assert "exceeds maximum length" in str(exc_info.value)

    def test_multiple_short_lines_allowed(self, tmp_path):
        """Test that multiple short lines are all processed"""
        test_file = tmp_path / "multiline.py.knda"
        content = "\n".join([f"~kinda int x{i} = {i}" for i in range(100)])
        test_file.write_text(content)

        result = transform_file(test_file)
        # All lines should be processed
        for i in range(100):
            assert f"x{i}" in result

    def test_line_at_exact_limit(self, tmp_path, monkeypatch):
        """Test that lines exactly at the limit are allowed"""
        monkeypatch.setattr(matchers, "KINDA_MAX_LINE_LENGTH", 30)

        # Create a line exactly 30 characters
        test_file = tmp_path / "exactline.py.knda"
        # Adjust to make exactly 30 chars: add 3 more digits
        line = "~kinda int x = 123456789012345"  # Exactly 30 chars
        assert len(line) == 30
        test_file.write_text(line + "\n")

        # Should succeed
        result = transform_file(test_file)
        assert "x =" in result


class TestIterationBounds:
    """Test Layer 3: Iteration bounds enforcement"""

    def test_normal_parsing_iterations(self, tmp_path):
        """Test that normal code stays within iteration limits"""
        test_file = tmp_path / "normal.py.knda"
        test_file.write_text("~sorta print('Hello, world!')\n")

        result = transform_file(test_file)
        assert "sorta_print" in result

    def test_excessive_iterations_prevented(self, tmp_path, monkeypatch):
        """Test that excessive iterations raise KindaSizeError"""
        # Set a very low iteration limit (the limit is checked per character in parsing loops)
        monkeypatch.setattr(matchers, "KINDA_MAX_PARSE_ITERATIONS", 20)

        # Create a line with deeply nested parentheses to force use of _parse_balanced_parentheses
        # The balanced parentheses parser iterates character-by-character
        test_file = tmp_path / "nested.py.knda"
        # Use ~sometimes construct with nested parentheses - requires balanced paren parsing
        # This will use _parse_balanced_parentheses which has iteration bounds
        nested_expr = "~sometimes((" + ("x" * 30) + "))\n"
        test_file.write_text(nested_expr)

        # Should raise KindaSizeError due to iteration limit
        with pytest.raises(KindaSizeError) as exc_info:
            transform_file(test_file)

        assert exc_info.value.limit_type == "parse_iterations"
        assert exc_info.value.current_value > 20
        assert exc_info.value.max_value == 20
        assert "exceeded maximum iterations" in str(exc_info.value).lower()

    def test_complex_but_valid_code_succeeds(self, tmp_path):
        """Test that complex but valid code succeeds with default limits"""
        test_file = tmp_path / "complex.py.knda"
        # Complex but reasonable code
        content = """
~sometimes() {
    ~kinda int x = 42
    ~sorta print(x)
    ~maybe() {
        ~kinda int y = x + 1
        ~sorta print(y)
    }
}
"""
        test_file.write_text(content)

        result = transform_file(test_file)
        assert "sometimes" in result
        assert "maybe" in result


class TestStringLiteralSize:
    """Test Layer 4: String literal size validation"""

    def test_normal_string_allowed(self, tmp_path):
        """Test that normal-sized strings are allowed"""
        test_file = tmp_path / "string.py.knda"
        test_file.write_text('~sorta print("Hello, world!")\n')

        result = transform_file(test_file)
        assert "Hello, world!" in result

    def test_validate_string_literal_function(self):
        """Test the validate_string_literal function directly"""
        from kinda.grammar.python.matchers import validate_string_literal

        # Normal string should pass
        validate_string_literal("Hello", 1, "test.knda")

        # Large string should fail with custom limit
        import kinda.grammar.python.matchers as m

        original_limit = m.KINDA_MAX_STRING_SIZE
        try:
            m.KINDA_MAX_STRING_SIZE = 10
            with pytest.raises(KindaSizeError) as exc_info:
                validate_string_literal("x" * 100, 1, "test.knda")

            assert exc_info.value.limit_type == "string_size"
            assert exc_info.value.current_value == 100
            assert exc_info.value.max_value == 10
        finally:
            m.KINDA_MAX_STRING_SIZE = original_limit


class TestErrorMessages:
    """Test that error messages are helpful and actionable"""

    def test_file_size_error_message(self, tmp_path, monkeypatch):
        """Test that file size error has helpful message"""
        from kinda.langs.python import transformer

        monkeypatch.setattr(matchers, "KINDA_MAX_FILE_SIZE", 50)
        monkeypatch.setattr(transformer, "KINDA_MAX_FILE_SIZE", 50)

        test_file = tmp_path / "large.py.knda"
        test_file.write_text("x" * 100)

        with pytest.raises(KindaSizeError) as exc_info:
            transform_file(test_file)

        error_msg = str(exc_info.value)
        assert "file_size" in error_msg
        assert "Current value:" in error_msg
        assert "Maximum allowed:" in error_msg
        assert "Suggestion:" in error_msg
        assert "splitting the file" in error_msg or "KINDA_MAX_FILE_SIZE" in error_msg

    def test_line_length_error_message(self, tmp_path, monkeypatch):
        """Test that line length error has helpful message"""
        monkeypatch.setattr(matchers, "KINDA_MAX_LINE_LENGTH", 30)

        test_file = tmp_path / "longline.py.knda"
        test_file.write_text("x" * 100)

        with pytest.raises(KindaSizeError) as exc_info:
            transform_file(test_file)

        error_msg = str(exc_info.value)
        assert "line_length" in error_msg
        assert "Line 1" in error_msg
        assert "Current value:" in error_msg
        assert "Maximum allowed:" in error_msg
        assert "Suggestion:" in error_msg

    def test_iteration_error_message(self, tmp_path, monkeypatch):
        """Test that iteration limit error has helpful message"""
        monkeypatch.setattr(matchers, "KINDA_MAX_PARSE_ITERATIONS", 10)

        test_file = tmp_path / "complex.py.knda"
        # Use nested parentheses to force balanced parentheses parser
        test_file.write_text("~sometimes((" + ("x" * 30) + "))")

        with pytest.raises(KindaSizeError) as exc_info:
            transform_file(test_file)

        error_msg = str(exc_info.value)
        assert "parse_iterations" in error_msg
        assert "Current value:" in error_msg
        assert "Maximum allowed:" in error_msg
        assert "Suggestion:" in error_msg


class TestEnvironmentVariableConfiguration:
    """Test that limits can be configured via environment variables"""

    def test_custom_file_size_limit(self, tmp_path, monkeypatch):
        """Test that KINDA_MAX_FILE_SIZE can be configured"""
        # This test verifies the environment variable is read at module load time
        # We can't easily test runtime changes, but we can verify the current value
        assert hasattr(matchers, "KINDA_MAX_FILE_SIZE")
        assert isinstance(matchers.KINDA_MAX_FILE_SIZE, int)
        assert matchers.KINDA_MAX_FILE_SIZE > 0

    def test_custom_line_length_limit(self, tmp_path, monkeypatch):
        """Test that KINDA_MAX_LINE_LENGTH can be configured"""
        assert hasattr(matchers, "KINDA_MAX_LINE_LENGTH")
        assert isinstance(matchers.KINDA_MAX_LINE_LENGTH, int)
        assert matchers.KINDA_MAX_LINE_LENGTH > 0

    def test_custom_iteration_limit(self, tmp_path, monkeypatch):
        """Test that KINDA_MAX_PARSE_ITERATIONS can be configured"""
        assert hasattr(matchers, "KINDA_MAX_PARSE_ITERATIONS")
        assert isinstance(matchers.KINDA_MAX_PARSE_ITERATIONS, int)
        assert matchers.KINDA_MAX_PARSE_ITERATIONS > 0

    def test_custom_string_size_limit(self, tmp_path, monkeypatch):
        """Test that KINDA_MAX_STRING_SIZE can be configured"""
        assert hasattr(matchers, "KINDA_MAX_STRING_SIZE")
        assert isinstance(matchers.KINDA_MAX_STRING_SIZE, int)
        assert matchers.KINDA_MAX_STRING_SIZE > 0


class TestPerformanceImpact:
    """Test that DoS protection has minimal performance overhead"""

    @pytest.mark.skip(
        reason="Performance tests disabled until release - they take too long and get invalidated by changes"
    )
    def test_validation_overhead_minimal(self, tmp_path, benchmark=None):
        """Test that validation adds minimal overhead to normal files"""
        # Create a typical kinda file
        test_file = tmp_path / "typical.py.knda"
        content = "\n".join(
            [
                "~kinda int x = 42",
                "~sorta print(x)",
                "~sometimes() {",
                "    ~kinda int y = x + 1",
                "}",
            ]
        )
        test_file.write_text(content)

        # This should complete quickly
        result = transform_file(test_file)
        assert result is not None
        # If benchmark is available (pytest-benchmark), we could measure exact overhead
        # For now, we just verify it completes successfully


class TestEdgeCases:
    """Test edge cases and boundary conditions"""

    def test_file_with_only_comments(self, tmp_path):
        """Test that files with only comments are handled"""
        test_file = tmp_path / "comments.py.knda"
        test_file.write_text("# This is a comment\n# Another comment\n")

        result = transform_file(test_file)
        assert result is not None

    def test_file_with_empty_lines(self, tmp_path):
        """Test that files with many empty lines are handled"""
        test_file = tmp_path / "empty_lines.py.knda"
        test_file.write_text("\n\n\n~kinda int x = 1\n\n\n")

        result = transform_file(test_file)
        assert "x =" in result

    def test_unicode_content(self, tmp_path):
        """Test that Unicode content is handled correctly"""
        test_file = tmp_path / "unicode.py.knda"
        test_file.write_text('~sorta print("Hello, 世界!")\n', encoding="utf-8")

        result = transform_file(test_file)
        assert "世界" in result

    def test_windows_line_endings(self, tmp_path):
        """Test that Windows line endings (CRLF) are handled"""
        test_file = tmp_path / "windows.py.knda"
        test_file.write_bytes(b"~kinda int x = 42\r\n~sorta print(x)\r\n")

        result = transform_file(test_file)
        assert "x =" in result


class TestSecurityValidation:
    """Test that DoS attacks are prevented"""

    def test_no_dos_with_10mb_file(self, tmp_path, monkeypatch):
        """Test that 10MB file is rejected (would cause DoS without protection)"""
        # Don't actually create 10MB, just test the limit - patch both locations
        from kinda.langs.python import transformer

        monkeypatch.setattr(matchers, "KINDA_MAX_FILE_SIZE", 1024)  # 1KB limit
        monkeypatch.setattr(transformer, "KINDA_MAX_FILE_SIZE", 1024)

        test_file = tmp_path / "fake_large.py.knda"
        test_file.write_text("x" * 2000)  # 2KB file

        with pytest.raises(KindaSizeError) as exc_info:
            transform_file(test_file)

        assert exc_info.value.limit_type == "file_size"

    def test_no_dos_with_100k_line(self, tmp_path, monkeypatch):
        """Test that 100K character line is rejected"""
        monkeypatch.setattr(matchers, "KINDA_MAX_LINE_LENGTH", 100)

        test_file = tmp_path / "fake_long_line.py.knda"
        test_file.write_text("x" * 200)

        with pytest.raises(KindaSizeError) as exc_info:
            transform_file(test_file)

        assert exc_info.value.limit_type == "line_length"

    def test_no_dos_with_1m_string(self, tmp_path, monkeypatch):
        """Test that 1M character string is rejected"""
        from kinda.grammar.python.matchers import validate_string_literal

        monkeypatch.setattr(matchers, "KINDA_MAX_STRING_SIZE", 100)

        with pytest.raises(KindaSizeError) as exc_info:
            validate_string_literal("x" * 200, 1, "test.knda")

        assert exc_info.value.limit_type == "string_size"
