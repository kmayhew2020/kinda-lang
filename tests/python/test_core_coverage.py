"""
Core coverage tests for kinda-lang constructs.
Focuses on testing the main functionality and covering gaps in coverage.
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch

from kinda.langs.python.transformer import transform_line, transform_file
from kinda.grammar.python.matchers import match_python_construct
from kinda.langs.python.runtime_gen import generate_runtime


class TestSortaPrintParsing:
    """Test ~sorta print parsing functionality"""

    def test_nested_function_calls(self):
        """Test ~sorta print with nested function calls"""
        line = '~sorta print(func(a, b), other_func(1, 2, 3))'
        construct_type, groups = match_python_construct(line)
        
        assert construct_type == "sorta_print"
        assert groups[0] == "func(a, b), other_func(1, 2, 3)"

    def test_string_literals_with_parentheses(self):
        """Test ~sorta print with strings containing parentheses"""
        line = '~sorta print("text (with parens)", "more (nested) text")'
        construct_type, groups = match_python_construct(line)
        
        assert construct_type == "sorta_print"
        assert groups[0] == '"text (with parens)", "more (nested) text"'

    def test_complex_expressions(self):
        """Test ~sorta print with complex Python expressions"""
        test_cases = [
            '~sorta print(x if y else z)',
            '~sorta print([i for i in range(10)])',
            '~sorta print({"key": value for key, value in items})',
        ]
        
        for line in test_cases:
            construct_type, groups = match_python_construct(line)
            assert construct_type == "sorta_print", f"Failed for: {line}"
            assert groups is not None

    def test_empty_print_arguments(self):
        """Test ~sorta print with empty parentheses"""
        line = '~sorta print()'
        construct_type, groups = match_python_construct(line)
        
        assert construct_type == "sorta_print"
        assert groups[0] == ""


class TestTransformLineCore:
    """Test core transform_line functionality"""

    def test_comment_preservation(self):
        """Test that comments are preserved"""
        comment_line = "# This is a comment"
        result = transform_line(comment_line)
        assert result == [comment_line]

    def test_normal_python_passthrough(self):
        """Test normal Python passes through unchanged"""
        python_line = "x = 42"
        result = transform_line(python_line)
        assert result == [python_line]

    def test_kinda_int_transformation(self):
        """Test ~kinda int transformations"""
        line = "~kinda int x = 42"
        result = transform_line(line)
        
        assert len(result) == 1
        assert "kinda_int(42)" in result[0]

    def test_sorta_print_transformation(self):
        """Test ~sorta print transformations"""
        line = '~sorta print("hello world")'
        result = transform_line(line)
        
        assert len(result) == 1
        assert "sorta_print" in result[0]
        assert '"hello world"' in result[0]

    def test_fuzzy_assignment_transformation(self):
        """Test x ~= value transformations"""
        line = "x ~= 100"
        result = transform_line(line)
        
        assert len(result) == 1
        assert "fuzzy_assign" in result[0]


class TestRuntimeGeneration:
    """Test runtime generation functionality"""

    def test_basic_runtime_generation(self):
        """Test basic runtime generation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            generate_runtime(temp_path)
            
            runtime_file = temp_path / "fuzzy.py"
            assert runtime_file.exists()
            
            result = runtime_file.read_text()
            assert "import random" in result
            assert "env = {}" in result

    def test_runtime_includes_constructs(self):
        """Test runtime includes expected constructs"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            generate_runtime(temp_path)
            
            runtime_file = temp_path / "fuzzy.py"
            result = runtime_file.read_text()
            
            # Should include core constructs
            assert "sorta_print" in result or "def sorta_print" in result
            assert "sometimes" in result or "def sometimes" in result


class TestCLIFunctionsCoverage:
    """Test CLI functions for coverage"""

    def test_safe_print_normal_case(self):
        """Test safe_print with normal text"""
        from kinda.cli import safe_print
        
        # Should not raise exception with normal text
        safe_print("Hello world")

    @patch('builtins.print')
    def test_safe_print_fallback(self, mock_print):
        """Test safe_print fallback for Unicode errors"""
        from kinda.cli import safe_print
        
        # Test normal case first
        mock_print.reset_mock()
        mock_print.side_effect = None
        safe_print("normal text")
        mock_print.assert_called_once_with("normal text")
        
        # Test fallback case with proper UnicodeEncodeError
        mock_print.reset_mock()
        mock_print.side_effect = [UnicodeEncodeError('utf-8', '', 0, 1, 'test'), None]
        
        safe_print("text with emoji 🎲")
        
        # Should call print twice: once failing, once with fallback
        assert mock_print.call_count == 2

    def test_detect_language(self):
        """Test language detection logic"""
        from kinda.cli import detect_language
        from pathlib import Path
        
        # Test forced language
        assert detect_language(Path("test.py"), "python") == "python"
        
        # Test .py.knda extension
        assert detect_language(Path("test.py.knda"), None) == "python"
        
        # Test .py extension  
        assert detect_language(Path("test.py"), None) == "python"
        
        # Test default
        assert detect_language(Path("test.unknown"), None) == "python"

    def test_get_transformer(self):
        """Test transformer retrieval"""
        from kinda.cli import get_transformer
        
        transformer = get_transformer("python")
        assert transformer is not None
        
        # Test unsupported language
        with pytest.raises(ValueError):
            get_transformer("unsupported")


class TestFileTransformation:
    """Test file-level transformation"""

    def test_transform_mixed_content(self):
        """Test transforming file with mixed Python and kinda content"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.knda', delete=False) as f:
            f.write("""# Mixed content file
import math

def regular_function():
    return 42

~kinda int kinda_var = 10
~sorta print("Mixed content")

result = regular_function()
""")
            temp_path = Path(f.name)

        try:
            result = transform_file(temp_path)
            
            # Should preserve Python and transform kinda
            assert "import math" in result
            assert "def regular_function" in result
            assert "kinda_int(10)" in result
            assert "sorta_print" in result
            
        finally:
            temp_path.unlink()


class TestErrorRecovery:
    """Test error recovery and graceful degradation"""

    def test_partial_construct_matching(self):
        """Test handling of partially matching constructs"""
        partial_lines = [
            "~sorta",  # Incomplete
            "~kinda int",  # Missing assignment
            "x ~=",  # Missing value
        ]
        
        for line in partial_lines:
            result = transform_line(line)
            # Should return the original line if can't transform
            assert result == [line]

    def test_mixed_valid_invalid_constructs(self):
        """Test file with mix of valid and invalid constructs"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.knda', delete=False) as f:
            f.write("""~kinda int good_var = 42
~sorta print(broken_syntax
~kinda int another_good = 100
~sorta print("this should work")
""")
            temp_path = Path(f.name)

        try:
            result = transform_file(temp_path)
            
            # Should process valid constructs, leave invalid unchanged
            assert "kinda_int(42)" in result
            assert "kinda_int(100)" in result
            assert 'sorta_print("this should work")' in result
            # Invalid lines should pass through
            assert "~sorta print(broken_syntax" in result
            
        finally:
            temp_path.unlink()


class TestUnicodeHandling:
    """Test Unicode handling in constructs"""

    def test_unicode_in_constructs(self):
        """Test constructs with Unicode characters"""
        unicode_lines = [
            '~sorta print("Hello 世界")',
            '~sorta print("Café ☕")', 
        ]
        
        for line in unicode_lines:
            # Should handle Unicode without crashing
            result = transform_line(line)
            assert result is not None
            assert len(result) >= 1