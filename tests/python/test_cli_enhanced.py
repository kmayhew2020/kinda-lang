"""
Enhanced CLI tests to improve coverage to 95% target.
Focuses on untested functions and edge cases in kinda/cli.py
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
from io import StringIO
import sys

from kinda.cli import (
    safe_read_file, validate_knda_file, detect_language,
    get_transformer, safe_print, main
)


class TestSafeReadFile:
    """Test safe_read_file function with various scenarios."""
    
    def test_safe_read_file_normal(self):
        """Test reading a normal text file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.knda', delete=False) as f:
            f.write("~kinda int x = 42\n~sorta print(x)")
            temp_path = Path(f.name)
        
        try:
            content = safe_read_file(temp_path)
            assert "~kinda int x = 42" in content
            assert "~sorta print(x)" in content
        finally:
            temp_path.unlink()
    
    def test_safe_read_file_empty(self, capsys):
        """Test reading an empty file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.knda', delete=False) as f:
            temp_path = Path(f.name)
        
        try:
            content = safe_read_file(temp_path)
            assert content == ""
            captured = capsys.readouterr()
            assert "appears to be empty" in captured.out
        finally:
            temp_path.unlink()
    
    def test_safe_read_file_permission_error(self):
        """Test handling permission errors."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.knda', delete=False) as f:
            f.write("test content")
            temp_path = Path(f.name)
        
        try:
            # Make file unreadable (Unix only)
            if os.name != 'nt':
                os.chmod(temp_path, 0o000)
                with pytest.raises(PermissionError):
                    safe_read_file(temp_path)
                os.chmod(temp_path, 0o644)  # Restore permissions for cleanup
        finally:
            if temp_path.exists():
                os.chmod(temp_path, 0o644)  # Ensure we can delete it
                temp_path.unlink()
    
    def test_safe_read_file_unicode_decode_error(self, capsys):
        """Test handling files with encoding issues."""
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.knda', delete=False) as f:
            # Write invalid UTF-8 bytes
            f.write(b'\xff\xfe~kinda int x = 42')
            temp_path = Path(f.name)
        
        try:
            content = safe_read_file(temp_path)
            # Should handle the encoding issue and return something
            assert content is not None
        finally:
            temp_path.unlink()
    
    def test_safe_read_file_with_different_encodings(self, capsys):
        """Test file reading with different encodings."""
        # Test UTF-8 BOM
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.knda', delete=False) as f:
            f.write(b'\xef\xbb\xbf~kinda int x = 42')
            temp_path = Path(f.name)
        
        try:
            content = safe_read_file(temp_path)
            assert "~kinda int" in content
        finally:
            temp_path.unlink()
    
    def test_safe_read_file_os_error(self):
        """Test handling OSError when reading file."""
        with patch('builtins.open', side_effect=OSError("Disk error")):
            with pytest.raises(OSError):
                safe_read_file(Path("test.knda"))


class TestValidateKndaFile:
    """Test validate_knda_file function."""
    
    def test_validate_directory(self):
        """Test that directories are considered valid."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = validate_knda_file(Path(temp_dir))
            assert result is True
    
    def test_validate_normal_file(self):
        """Test validating a normal .knda file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.knda', delete=False) as f:
            f.write("~kinda int x = 42")
            temp_path = Path(f.name)
        
        try:
            result = validate_knda_file(temp_path)
            assert result is True
        finally:
            temp_path.unlink()
    
    def test_validate_large_file(self, capsys):
        """Test validation warns about large files."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.knda', delete=False) as f:
            # Write >1MB of content
            f.write("x" * 1_100_000)
            temp_path = Path(f.name)
        
        try:
            result = validate_knda_file(temp_path)
            assert result is True  # Still valid, just warns
            captured = capsys.readouterr()
            assert "pretty huge" in captured.out
            assert "performance issues" in captured.out
        finally:
            temp_path.unlink()
    
    def test_validate_binary_file(self, capsys):
        """Test validation rejects binary files."""
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.knda', delete=False) as f:
            f.write(b'\x00\x01\x02\x03binary data')
            temp_path = Path(f.name)
        
        try:
            result = validate_knda_file(temp_path)
            assert result is False
            captured = capsys.readouterr()
            assert "binary data" in captured.out
            assert "not gonna work" in captured.out
        finally:
            temp_path.unlink()
    
    def test_validate_file_read_exception(self):
        """Test validation handles exceptions."""
        with patch('kinda.cli.safe_read_file', side_effect=Exception("Read error")):
            result = validate_knda_file(Path("test.knda"))
            assert result is False


class TestDetectLanguage:
    """Test language detection function."""
    
    def test_detect_python_extension(self):
        """Test detecting Python from file extension."""
        assert detect_language(Path("test.py.knda"), None) == "python"
        assert detect_language(Path("test.py"), None) == "python"
    
    def test_detect_c_extension(self, capsys):
        """Test detecting C from file extension raises error."""
        with pytest.raises(ValueError, match="C files not yet supported"):
            detect_language(Path("test.c.knda"), None)
        
        with pytest.raises(ValueError, match="C files not yet supported"):
            detect_language(Path("test.c"), None)
    
    def test_detect_unknown_extension(self):
        """Test unknown extension defaults to Python."""
        assert detect_language(Path("test.unknown.knda"), None) == "python"
        assert detect_language(Path("test.txt"), None) == "python"
    
    def test_detect_with_forced_python(self):
        """Test forced Python language."""
        assert detect_language(Path("test.c.knda"), "python") == "python"
        assert detect_language(Path("test.unknown"), "python") == "python"
    
    def test_detect_with_forced_c(self, capsys):
        """Test forced C language raises error."""
        with pytest.raises(ValueError, match="C language not yet supported"):
            detect_language(Path("test.py.knda"), "c")
        
        captured = capsys.readouterr()
        assert "C transpiler is planned for v0.4.0" in captured.out


class TestGetTransformer:
    """Test transformer getter function."""
    
    def test_get_python_transformer(self):
        """Test getting Python transformer."""
        transformer = get_transformer("python")
        assert transformer is not None
        assert hasattr(transformer, 'transform')
    
    def test_get_c_transformer(self, capsys):
        """Test C transformer is disabled."""
        transformer = get_transformer("c")
        assert transformer is None
        captured = capsys.readouterr()
        assert "C support is coming in v0.4.0" in captured.out
    
    def test_get_unsupported_language(self):
        """Test unsupported languages raise ValueError."""
        with pytest.raises(ValueError, match="Unsupported language: java"):
            get_transformer("java")
        
        with pytest.raises(ValueError, match="Unsupported language: javascript"):
            get_transformer("javascript")


class TestMainFunctionEdgeCases:
    """Test main function with various edge cases."""
    
    def test_main_no_arguments(self, capsys):
        """Test main with no arguments shows error."""
        with pytest.raises(SystemExit):
            main([])
    
    def test_main_help_flag(self, capsys):
        """Test --help flag."""
        with patch('sys.argv', ['kinda', '--help']):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0
            captured = capsys.readouterr()
            assert "usage:" in captured.out.lower()
    
    def test_main_invalid_arguments(self, capsys):
        """Test invalid arguments."""
        with pytest.raises(SystemExit):
            main(['--invalid-flag'])
    
    def test_main_unknown_command(self, capsys):
        """Test unknown command."""
        with patch('sys.argv', ['kinda', 'unknown_command']):
            with pytest.raises(SystemExit):
                main()
            captured = capsys.readouterr()
            assert "invalid choice" in captured.err or "error" in captured.err.lower()
    
    def test_main_transform_binary_file(self, capsys):
        """Test transform with binary file gets rejected."""
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.knda', delete=False) as f:
            f.write(b'\x00\x01\x02\x03binary')
            temp_path = Path(f.name)
        
        try:
            with patch('sys.argv', ['kinda', 'transform', str(temp_path)]):
                result = main()
                assert result == 1
                captured = capsys.readouterr()
                assert "binary data" in captured.out or "not gonna work" in captured.out
        finally:
            temp_path.unlink()
    
    def test_main_run_with_valid_file(self, capsys):
        """Test run command with valid file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.knda', delete=False) as f:
            f.write('~sorta print("test")')
            temp_path = Path(f.name)
        
        try:
            result = main(['run', str(temp_path)])
            captured = capsys.readouterr()
            assert result == 0
        finally:
            temp_path.unlink()
            # Clean up
            if Path(".kinda-build").exists():
                import shutil
                shutil.rmtree(".kinda-build")


class TestSafePrintEdgeCases:
    """Test safe_print function edge cases."""
    
    def test_safe_print_various_emojis(self):
        """Test safe_print handles various emoji types."""
        from kinda.cli import safe_print
        
        # Test different emoji categories
        test_strings = [
            "🎲 Dice emoji",
            "✨ Sparkles emoji",
            "📚 Book emoji",
            "🔍 Magnifying glass",
            "💥 Explosion",
            "🚫 Prohibited",
            "⚠️ Warning",
            "😰 Anxious face"
        ]
        
        for test_str in test_strings:
            with patch('builtins.print') as mock_print:
                # First call might fail with UnicodeEncodeError
                mock_print.side_effect = [
                    UnicodeEncodeError('ascii', test_str, 0, 1, 'ordinal not in range'),
                    None
                ]
                safe_print(test_str)
                # Should have called print twice (once failed, once succeeded)
                assert mock_print.call_count == 2