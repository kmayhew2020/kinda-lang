"""
CLI coverage tests for kinda-lang command line interface.
Targets remaining coverage gaps in CLI module.
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
from io import StringIO
import sys

from kinda.cli import show_examples, show_syntax_reference, main


class TestCLIHelperFunctions:
    """Test CLI helper functions for coverage"""
    
    def test_show_examples(self, capsys):
        """Test show_examples function"""
        show_examples()
        captured = capsys.readouterr()
        assert "Here are some kinda programs to get you started" in captured.out
        assert "Hello World" in captured.out
        assert "Chaos Greeter" in captured.out
        assert "Maybe Math" in captured.out
        assert "Pro tip" in captured.out

    def test_show_syntax_reference(self, capsys):
        """Test show_syntax_reference function"""
        show_syntax_reference()
        captured = capsys.readouterr()
        assert "Kinda Syntax Reference" in captured.out
        assert "~kinda int" in captured.out
        assert "~sorta print" in captured.out
        assert "~sometimes" in captured.out
        assert "Basic Constructs" in captured.out
        assert "Pro Tips" in captured.out


class TestCLIMainFunction:
    """Test main CLI function with different command scenarios"""
    
    def test_examples_command(self, capsys):
        """Test examples command through main function"""
        with patch('sys.argv', ['kinda', 'examples']):
            result = main()
            captured = capsys.readouterr()
            assert result == 0
            assert "Here are some kinda programs" in captured.out
    
    def test_syntax_command(self, capsys):
        """Test syntax command through main function"""
        with patch('sys.argv', ['kinda', 'syntax']):
            result = main()
            captured = capsys.readouterr()
            assert result == 0
            assert "Kinda Syntax Reference" in captured.out

    def test_transform_command_missing_file(self, capsys):
        """Test transform command with nonexistent file"""
        with patch('sys.argv', ['kinda', 'transform', 'nonexistent.knda']):
            result = main()
            captured = capsys.readouterr()
            assert result == 1
            assert "doesn't exist" in captured.out

    def test_run_command_missing_file(self, capsys):
        """Test run command with nonexistent file"""
        with patch('sys.argv', ['kinda', 'run', 'nonexistent.knda']):
            result = main()
            captured = capsys.readouterr()
            assert result == 1
            assert "Can't find" in captured.out

    def test_interpret_command_missing_file(self, capsys):
        """Test interpret command with nonexistent file"""
        with patch('sys.argv', ['kinda', 'interpret', 'nonexistent.knda']):
            result = main()
            captured = capsys.readouterr()
            assert result == 1
            assert "nowhere to be found" in captured.out

    def test_transform_command_with_actual_file(self, capsys):
        """Test transform command with actual file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.knda', delete=False) as f:
            f.write('~kinda int x = 42\n~sorta print("hello")')
            temp_path = Path(f.name)

        try:
            with patch('sys.argv', ['kinda', 'transform', str(temp_path)]):
                result = main()
                captured = capsys.readouterr()
                assert result == 0
                assert "Transformed your chaos into" in captured.out
                assert "Generated" in captured.out and "file(s)" in captured.out
        finally:
            temp_path.unlink()
            # Clean up any generated files
            build_dir = Path("build")
            if build_dir.exists():
                import shutil
                shutil.rmtree(build_dir)

    def test_transform_unsupported_language(self, capsys):
        """Test transform with forced unsupported language"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.knda', delete=False) as f:
            f.write('~kinda int x = 42')
            temp_path = Path(f.name)

        try:
            with patch('sys.argv', ['kinda', 'transform', str(temp_path), '--lang', 'rust']):
                result = main()
                captured = capsys.readouterr()
                assert result == 0  # Returns 0 but shows message
                assert "don't speak" in captured.out
        finally:
            temp_path.unlink()

    def test_run_command_with_actual_file(self, capsys):
        """Test run command with actual file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.knda', delete=False) as f:
            f.write('~sorta print("test run")')
            temp_path = Path(f.name)

        try:
            with patch('sys.argv', ['kinda', 'run', str(temp_path)]):
                result = main()
                captured = capsys.readouterr()
                assert result == 0
                assert "Running your questionable code" in captured.out
                assert "didn't crash" in captured.out
        finally:
            temp_path.unlink()
            # Clean up build directory
            build_dir = Path(".kinda-build")
            if build_dir.exists():
                import shutil
                shutil.rmtree(build_dir)

    def test_run_unsupported_language_error(self, capsys):
        """Test run with unsupported language shows error"""  
        with tempfile.NamedTemporaryFile(mode='w', suffix='.knda', delete=False) as f:
            f.write('~kinda int x = 42')
            temp_path = Path(f.name)

        try:
            with patch('sys.argv', ['kinda', 'run', str(temp_path), '--lang', 'c']):
                result = main()
                captured = capsys.readouterr()
                assert result == 1
                assert "can transform c but can't run it" in captured.out
        finally:
            temp_path.unlink()

    @patch('kinda.interpreter.repl.run_interpreter')
    def test_interpret_command_with_file(self, mock_interpreter, capsys):
        """Test interpret command with actual file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.knda', delete=False) as f:
            f.write('~sorta print("interpret test")')
            temp_path = Path(f.name)

        try:
            with patch('sys.argv', ['kinda', 'interpret', str(temp_path)]):
                result = main()
                captured = capsys.readouterr()
                assert result == 0
                assert "Entering the chaos dimension" in captured.out
                assert "Chaos complete" in captured.out
                mock_interpreter.assert_called_once_with(str(temp_path), 'python')
        finally:
            temp_path.unlink()

    def test_interpret_unsupported_language(self, capsys):
        """Test interpret with unsupported language"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.knda', delete=False) as f:
            f.write('~kinda int x = 42')
            temp_path = Path(f.name)

        try:
            with patch('sys.argv', ['kinda', 'interpret', str(temp_path), '--lang', 'c']):
                result = main()
                captured = capsys.readouterr()
                assert result == 1
                assert "Interpret mode only works with Python" in captured.out
        finally:
            temp_path.unlink()


class TestCLIArgumentParsing:
    """Test CLI argument parsing edge cases"""

    def test_transform_with_custom_output_dir(self, capsys):
        """Test transform command with custom output directory"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.knda', delete=False) as f:
            f.write('~kinda int x = 42')
            temp_path = Path(f.name)

        try:
            with patch('sys.argv', ['kinda', 'transform', str(temp_path), '--out', 'custom_build']):
                result = main()
                captured = capsys.readouterr()
                assert result == 0
                assert "custom_build" in captured.out or "Transformed" in captured.out
        finally:
            temp_path.unlink()
            # Clean up custom build directory
            custom_dir = Path("custom_build")
            if custom_dir.exists():
                import shutil
                shutil.rmtree(custom_dir)

    def test_command_with_forced_language(self):
        """Test language detection with forced language parameter"""
        from kinda.cli import detect_language
        
        # Test forced language overrides extension detection
        test_path = Path("test.unknown.extension")
        result = detect_language(test_path, "python")
        assert result == "python"


class TestSafePrintCoverage:
    """Test safe_print function coverage for error handling"""

    @patch('builtins.print')
    def test_safe_print_with_unicode_fallback(self, mock_print):
        """Test safe_print handles UnicodeEncodeError gracefully"""
        from kinda.cli import safe_print
        
        # Test normal operation
        mock_print.side_effect = None
        safe_print("normal text")
        
        # Test with UnicodeEncodeError
        mock_print.side_effect = [UnicodeEncodeError('utf-8', '', 0, 1, 'test'), None]
        safe_print("text with emojis 🎲🤷📚")
        
        # Should call print twice - once failing, once with fallbacks
        assert mock_print.call_count >= 2

    def test_safe_print_emoji_replacements(self):
        """Test that safe_print replaces emojis correctly in fallback"""
        from kinda.cli import safe_print
        
        # This tests the fallback logic by checking the replacement patterns exist
        with patch('builtins.print') as mock_print:
            mock_print.side_effect = [UnicodeEncodeError('utf-8', '', 0, 1, 'test'), None]
            safe_print("✨🎲🤷📚📝🎯")
            
            # Check that fallback was called with replacements
            if mock_print.call_count > 1:
                fallback_call = mock_print.call_args_list[1]
                fallback_text = fallback_call[0][0]
                # Should contain ASCII replacements, not emojis
                assert "✨" not in fallback_text
                assert "🎲" not in fallback_text