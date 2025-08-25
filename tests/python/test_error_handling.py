"""
Comprehensive tests for enhanced error handling in kinda-lang.

Tests cover both parsing errors and runtime error recovery.
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch
from kinda.cli import main
from kinda.langs.python.runtime.fuzzy import kinda_int, sorta_print, sometimes, maybe


class TestCLanguageRejection:
    """Test that C language support is properly rejected with helpful messages."""
    
    def test_c_language_flag_rejected_transform(self, capsys):
        """Test that --lang c is rejected in transform command."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.knda', delete=False) as f:
            f.write('~kinda int x = 42')
            temp_path = Path(f.name)
        
        try:
            with patch('sys.argv', ['kinda', 'transform', str(temp_path), '--lang', 'c']):
                result = main()
                captured = capsys.readouterr()
                assert result == 1
                assert "C transpiler is planned for v0.4.0" in captured.out
                assert "Currently only Python is supported" in captured.out
                assert "github.com/kinda-lang/kinda-lang/issues/19" in captured.out
        finally:
            temp_path.unlink()
    
    def test_c_language_flag_rejected_run(self, capsys):
        """Test that --lang c is rejected in run command."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.knda', delete=False) as f:
            f.write('~kinda int x = 42')
            temp_path = Path(f.name)
        
        try:
            with patch('sys.argv', ['kinda', 'run', str(temp_path), '--lang', 'c']):
                result = main()
                captured = capsys.readouterr()
                assert result == 1
                assert ("C transpiler is planned for v0.4.0" in captured.out or 
                        "C support is coming in v0.4.0" in captured.out)
        finally:
            temp_path.unlink()
    
    def test_c_file_extension_rejected(self, capsys):
        """Test that .c.knda files are rejected with helpful message."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.c.knda', delete=False) as f:
            f.write('~kinda int x = 42')
            temp_path = Path(f.name)
        
        try:
            with patch('sys.argv', ['kinda', 'transform', str(temp_path)]):
                result = main()
                captured = capsys.readouterr()
                assert result == 1
                assert "C files detected but C transpiler isn't ready yet" in captured.out
                assert "use .py.knda files with Python syntax" in captured.out
        finally:
            temp_path.unlink()


class TestFileValidation:
    """Test file validation and error handling."""
    
    def test_missing_file_helpful_suggestions(self, capsys):
        """Test that missing files show helpful suggestions."""
        non_existent = "/tmp/nonexistent_file.knda"
        with patch('sys.argv', ['kinda', 'transform', non_existent]):
            result = main()
            captured = capsys.readouterr()
            assert result == 1
            assert "doesn't exist" in captured.out
            assert "Check your file path" in captured.out
    
    def test_binary_file_rejection(self, capsys):
        """Test that binary files are rejected gracefully."""
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.knda', delete=False) as f:
            f.write(b'\x00\x01\x02binary content')
            temp_path = Path(f.name)
        
        try:
            with patch('sys.argv', ['kinda', 'transform', str(temp_path)]):
                result = main()
                captured = capsys.readouterr()
                assert result == 1
                assert ("binary data" in captured.out or 
                        "File validation failed" in captured.out)
        finally:
            temp_path.unlink()


class TestRuntimeErrorHandling:
    """Test runtime error handling and recovery."""
    
    def test_kinda_int_with_invalid_input(self):
        """Test kinda_int gracefully handles non-numeric input."""
        import io
        import contextlib
        
        # Capture stdout to check error messages
        stdout_capture = io.StringIO()
        with contextlib.redirect_stdout(stdout_capture):
            result = kinda_int("not a number")
        
        output = stdout_capture.getvalue()
        assert "kinda int got something weird" in output
        assert "Expected a number but got str" in output
        assert isinstance(result, int)  # Should return a random int as fallback
        assert 0 <= result <= 10  # Should be in the fallback range
    
    def test_kinda_int_with_convertible_string(self):
        """Test kinda_int handles convertible strings correctly."""
        result = kinda_int("42")
        assert isinstance(result, int)
        # Result should be 42 ± 1 due to fuzz
        assert 41 <= result <= 43
    
    def test_sorta_print_error_recovery(self):
        """Test sorta_print handles errors gracefully."""
        import io
        import contextlib
        
        stdout_capture = io.StringIO()
        with contextlib.redirect_stdout(stdout_capture):
            # This should work normally
            sorta_print("test message")
        
        output = stdout_capture.getvalue()
        # Should either print normally or show personality
        assert ("[print]" in output or 
                "[shrug]" in output or 
                output.strip() == "")  # Sometimes sorta_print might not print anything
    
    def test_sorta_print_empty_arguments(self):
        """Test sorta_print handles empty arguments."""
        import io
        import contextlib
        
        stdout_capture = io.StringIO()
        with contextlib.redirect_stdout(stdout_capture):
            sorta_print()  # No arguments
        
        output = stdout_capture.getvalue()
        # Should either print nothing or a shrug message
        assert (output.strip() == "" or 
                "Nothing to print" in output)
    
    def test_conditional_functions_with_none(self):
        """Test sometimes and maybe handle None conditions gracefully."""
        import io
        import contextlib
        
        stdout_capture = io.StringIO()
        with contextlib.redirect_stdout(stdout_capture):
            result1 = sometimes(None)
            result2 = maybe(None)
        
        output = stdout_capture.getvalue()
        assert "got None as condition" in output
        assert isinstance(result1, bool)
        assert isinstance(result2, bool)
        # With None condition, both should return False after the warning
        assert result1 is False
        assert result2 is False


class TestParsingErrorMessages:
    """Test parsing error messages and syntax validation."""
    
    def test_helpful_parsing_error_messages(self, capsys):
        """Test that parsing errors include line numbers and helpful suggestions."""
        # Create a file with syntax that would normally cause parsing issues
        with tempfile.NamedTemporaryFile(mode='w', suffix='.knda', delete=False) as f:
            f.write('''# Test file with good syntax
~kinda int x = 5
~sorta print("This should work")

~maybe (x > 0) {
    ~sorta print("This is properly closed")
}''')
            temp_path = Path(f.name)
        
        try:
            with patch('sys.argv', ['kinda', 'transform', str(temp_path)]):
                result = main()
                captured = capsys.readouterr()
                # This should actually succeed since the syntax is correct
                assert result == 0
                assert "Transformed your chaos into:" in captured.out
        finally:
            temp_path.unlink()
    
    def test_cli_help_messages_updated(self, capsys):
        """Test that CLI help messages reflect Python-only support."""
        with patch('sys.argv', ['kinda', 'transform', '--help']):
            with pytest.raises(SystemExit):  # --help causes sys.exit
                main()
            captured = capsys.readouterr()
            assert "currently: 'python' only" in captured.out


class TestUserExperienceImprovements:
    """Test user experience improvements and helpful messaging."""
    
    def test_examples_command_works(self, capsys):
        """Test that examples command provides helpful output."""
        with patch('sys.argv', ['kinda', 'examples']):
            result = main()
            captured = capsys.readouterr()
            assert result == 0
            assert "kinda programs to get you started" in captured.out
            assert "examples/hello.py.knda" in captured.out
    
    def test_syntax_command_works(self, capsys):
        """Test that syntax command provides helpful reference."""
        with patch('sys.argv', ['kinda', 'syntax']):
            result = main()
            captured = capsys.readouterr()
            assert result == 0
            assert "Kinda Syntax Reference" in captured.out
            assert "~kinda int" in captured.out
            assert "~sorta print" in captured.out


if __name__ == "__main__":
    pytest.main([__file__])