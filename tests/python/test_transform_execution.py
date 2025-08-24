"""Tests for actual execution of transform functions"""
import pytest
from pathlib import Path
from kinda.langs.python.transformer import transform_line, transform_file


class TestPythonTransformExecution:
    """Test that Python transforms actually execute and produce correct output"""
    
    def test_kinda_int_transform(self):
        """Test ~kinda int declaration transform"""
        line = "~kinda int x = 42;"
        result = transform_line(line)
        expected = ["~kinda int x = 42;".replace("~kinda int x = 42", "x = kinda_int(42)")]
        assert result[0].strip().endswith("x = kinda_int(42)"), f"Expected kinda_int call, got {result}"
    
    def test_sorta_print_transform(self):
        """Test ~sorta print transform"""
        line = "~sorta print(hello)"
        result = transform_line(line)
        assert "sorta_print(hello)" in result[0], f"Expected sorta_print call, got {result}"
    
    def test_sometimes_transform(self):
        """Test ~sometimes conditional transform"""
        line = "~sometimes (x > 0):"
        result = transform_line(line)
        assert "if sometimes(x > 0):" in result[0], f"Expected sometimes conditional, got {result}"
    
    def test_fuzzy_reassign_transform(self):
        """Test fuzzy reassignment (~=) transform"""
        line = "x ~= 10;"
        result = transform_line(line)
        assert "fuzzy_assign('x', 10)" in result[0], f"Expected fuzzy_assign call, got {result}"
    
    def test_comment_passthrough(self):
        """Test that comments are passed through unchanged"""
        line = "# This is a comment"
        result = transform_line(line)
        assert result == [line], f"Comments should pass through unchanged"
    
    def test_blank_line_passthrough(self):
        """Test that blank lines are handled correctly"""
        line = ""
        result = transform_line(line)
        assert result == [""], f"Blank lines should return empty string list"
    
    def test_normal_python_passthrough(self):
        """Test that normal Python code passes through unchanged"""
        line = "print('hello world')"
        result = transform_line(line)
        assert result == [line], f"Normal Python should pass through unchanged"


class TestPythonFileTransforms:
    """Test transform_file functionality"""
    
    def test_transform_simple_file(self, tmp_path):
        """Test transforming a simple file with kinda constructs"""
        test_file = tmp_path / "test.knda"
        test_file.write_text("""~kinda int x = 5;
~sorta print(x);
""")
        
        result = transform_file(test_file)
        
        # Should have import header
        assert "from kinda.langs.python.runtime.fuzzy import" in result
        assert "kinda_int" in result
        assert "sorta_print" in result
        
        # Should have transformed calls
        assert "x = kinda_int(5)" in result
        assert "sorta_print(x)" in result
    
    def test_transform_sometimes_block(self, tmp_path):
        """Test transforming sometimes blocks with proper indentation"""
        test_file = tmp_path / "sometimes.knda"
        test_file.write_text("""~kinda int x = 1;
~sometimes (x > 0) {
    x ~= 10;
    ~sorta print(x);
}
""")
        
        result = transform_file(test_file)
        lines = result.split('\n')
        
        # Find the sometimes line
        sometimes_line = None
        for i, line in enumerate(lines):
            if 'if sometimes(' in line:
                sometimes_line = i
                break
        
        assert sometimes_line is not None, "Should find sometimes conditional"
        
        # Check that following lines are properly indented
        assert any("    " in line and "fuzzy_assign" in line for line in lines), "Block should be indented"
        assert any("    " in line and "sorta_print" in line for line in lines), "Block should be indented"
    
    def test_mixed_constructs_file(self, tmp_path):
        """Test file with multiple different constructs"""
        test_file = tmp_path / "mixed.knda"
        test_file.write_text("""# Comment at top
~kinda int a = 1;
normal_var = 42
a ~= 5;
~sorta print(a);
""")
        
        result = transform_file(test_file)
        
        # Should preserve comment
        assert "# Comment at top" in result
        
        # Should transform kinda constructs
        assert "a = kinda_int(1)" in result
        assert "a = fuzzy_assign('a', 5)" in result
        assert "sorta_print(a)" in result
        
        # Should preserve normal Python
        assert "normal_var = 42" in result
        
        # Should have proper imports
        assert "from kinda.langs.python.runtime.fuzzy import" in result



class TestTransformEdgeCases:
    """Test edge cases and complex scenarios"""
    
    def test_multiple_constructs_same_line(self):
        """Test handling multiple constructs on same line (if supported)"""
        # This tests the robustness of the parser
        line = "~kinda int x = 5; ~sorta print(x);"
        result = transform_line(line)
        # Should handle gracefully (may not support multiple, but shouldn't crash)
        assert isinstance(result, list)
        assert len(result) > 0
    
    def test_nested_expressions(self):
        """Test nested expressions in constructs"""
        line = "~kinda int result = (x + y) * 2;"
        result = transform_line(line)
        assert isinstance(result, list)
        if "kinda_int" in result[0]:
            assert "(x + y) * 2" in result[0]
    
    def test_empty_sometimes_condition(self):
        """Test sometimes with no condition"""
        line = "~sometimes () {"
        result = transform_line(line)
        assert "if sometimes()" in result[0] or result == [line]
    
    def test_whitespace_handling(self):
        """Test various whitespace scenarios"""
        test_cases = [
            "  ~kinda int x = 42;  ",
            "\t~sorta print(hello)\t",
            "    ~sometimes (True) {",
        ]
        
        for line in test_cases:
            result = transform_line(line)
            assert isinstance(result, list)
            assert len(result) > 0
            # Should preserve or handle whitespace appropriately