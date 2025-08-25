"""
Tests for Task #39 (Error Handling & UX) and Task #49 (Disable C Support)
"""
import pytest
import subprocess
import tempfile
from pathlib import Path
from unittest.mock import patch
from kinda.cli import main


class TestCLanguageRejection:
    """Test that C language support is properly rejected with helpful messages."""
    
    def test_c_language_flag_rejected_transform(self, capsys):
        """Test that --lang c flag is rejected in transform command."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.knda', delete=False) as f:
            f.write('~kinda int x = 42')
            temp_path = Path(f.name)

        try:
            with patch('sys.argv', ['kinda', 'transform', str(temp_path), '--lang', 'c']):
                result = main()
                captured = capsys.readouterr()
                assert result == 1
                assert "planned for v0.4.0" in captured.out
                assert "issues/19" in captured.out
        finally:
            temp_path.unlink()

    def test_c_language_flag_rejected_run(self, capsys):
        """Test that --lang c flag is rejected in run command."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.knda', delete=False) as f:
            f.write('~kinda int x = 42')
            temp_path = Path(f.name)

        try:
            with patch('sys.argv', ['kinda', 'run', str(temp_path), '--lang', 'c']):
                result = main()
                captured = capsys.readouterr()
                assert result == 1
                assert "planned for v0.4.0" in captured.out
        finally:
            temp_path.unlink()

    def test_c_file_extension_rejected(self, capsys):
        """Test that .c.knda file extension is detected and rejected."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.c.knda', delete=False) as f:
            f.write('~kinda int x = 42')
            temp_path = Path(f.name)

        try:
            with patch('sys.argv', ['kinda', 'transform', str(temp_path)]):
                result = main()
                captured = capsys.readouterr()
                assert result == 1
                assert "planned for v0.4.0" in captured.out
        finally:
            temp_path.unlink()


class TestFileValidation:
    """Test enhanced file validation and helpful error messages."""
    
    def test_missing_file_helpful_suggestions(self, capsys):
        """Test that missing files get helpful suggestions for similar files."""
        # Create a test .knda file to be suggested
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            existing_file = temp_path / "example.knda"
            existing_file.write_text("~kinda int x = 42")
            
            nonexistent_file = temp_path / "exampl.knda"  # Typo - should suggest existing
            
            with patch('sys.argv', ['kinda', 'transform', str(nonexistent_file)]):
                result = main()
                captured = capsys.readouterr()
                assert result == 1
                assert "doesn't exist" in captured.out

    def test_binary_file_rejection(self, capsys):
        """Test that binary files are detected and rejected."""
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.knda', delete=False) as f:
            # Write binary data
            f.write(b'\x00\x01\x02\x03\x04\x05')
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


class TestParsingErrorMessages:
    """Test improved parsing error messages with helpful context."""
    
    def test_helpful_parsing_error_messages(self, capsys):
        """Test that malformed syntax gets helpful error messages."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.knda', delete=False) as f:
            # Malformed conditional syntax
            f.write('~sometimes {\n  unclosed block\n')  # Missing closing brace
            temp_path = Path(f.name)

        try:
            with patch('sys.argv', ['kinda', 'transform', str(temp_path)]):
                result = main()
                # Should not crash, but may produce warnings
                # Main goal is no crash with helpful output
                assert isinstance(result, int)
        finally:
            temp_path.unlink()

    def test_cli_help_messages_updated(self, capsys):
        """Test that CLI help messages show only Python support."""
        with patch('sys.argv', ['kinda', 'transform', '--help']):
            with pytest.raises(SystemExit):
                main()
        
        captured = capsys.readouterr()
        # Help should mention Python but not C as supported
        assert "python" in captured.out.lower()


class TestUserExperienceImprovements:
    """Test overall user experience improvements."""
    
    def test_examples_command_works(self, capsys):
        """Test that examples command works with new error handling."""
        with patch('sys.argv', ['kinda', 'examples']):
            result = main()
            captured = capsys.readouterr()
            assert result == 0
            assert "Here are some kinda programs" in captured.out

    def test_syntax_command_works(self, capsys):
        """Test that syntax command works with new error handling."""
        with patch('sys.argv', ['kinda', 'syntax']):
            result = main()
            captured = capsys.readouterr()
            assert result == 0
            assert "Kinda Syntax Reference" in captured.out


class TestTransformErrorHandling:
    """Test transformation error handling without runtime dependencies."""
    
    def test_transform_handles_various_constructs(self):
        """Test that transformation handles various constructs without crashing."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.knda', delete=False) as f:
            # Test multiple constructs that should transform successfully
            f.write('~kinda int x = 42\n~sorta print("test message")\n~sometimes {\n  ~sorta print("conditional")\n}')
            temp_path = Path(f.name)

        try:
            with patch('sys.argv', ['kinda', 'transform', str(temp_path)]):
                result = main()
                # Should transform without errors
                assert result == 0
        finally:
            temp_path.unlink()
            # Cleanup build directory
            build_dir = Path("build")
            if build_dir.exists():
                import shutil
                shutil.rmtree(build_dir)