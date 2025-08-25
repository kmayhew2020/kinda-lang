"""
Comprehensive test suite for ~ish construct implementation.
Tests both ish_value (42~ish) and ish_comparison (score ~ish 100) patterns.
"""

import pytest
import random
import re
from unittest.mock import patch, MagicMock
from io import StringIO
import sys
from pathlib import Path
import tempfile

# Import test modules
from kinda.grammar.python.matchers import find_ish_constructs, match_python_construct
from kinda.langs.python.transformer import transform_line, _transform_ish_constructs
from kinda.langs.python.runtime.fuzzy import ish_value, ish_comparison


class TestIshMatching:
    """Test pattern matching for ~ish constructs."""
    
    def test_find_ish_value_patterns(self):
        """Test finding ish_value patterns in lines."""
        # Simple integer value
        constructs = find_ish_constructs("x = 42~ish")
        assert len(constructs) == 1
        assert constructs[0][0] == "ish_value"
        assert constructs[0][1].group(1) == "42"
        
        # Float value
        constructs = find_ish_constructs("y = 3.14~ish + 10")
        assert len(constructs) == 1
        assert constructs[0][0] == "ish_value"
        assert constructs[0][1].group(1) == "3.14"
        
        # Multiple values
        constructs = find_ish_constructs("result = 42~ish + 100~ish")
        assert len(constructs) == 2
        assert all(c[0] == "ish_value" for c in constructs)
        assert constructs[0][1].group(1) == "42"
        assert constructs[1][1].group(1) == "100"
    
    def test_find_ish_comparison_patterns(self):
        """Test finding ish_comparison patterns in lines."""
        # Simple comparison
        constructs = find_ish_constructs("if score ~ish 100:")
        assert len(constructs) == 1
        assert constructs[0][0] == "ish_comparison"
        assert constructs[0][1].group(1) == "score"
        assert constructs[0][1].group(2) == "100"
        
        # Variable comparison
        constructs = find_ish_constructs("while x ~ish target_value:")
        assert len(constructs) == 1
        assert constructs[0][0] == "ish_comparison"
        assert constructs[0][1].group(1) == "x"
        assert constructs[0][1].group(2) == "target_value"
    
    def test_no_ish_constructs(self):
        """Test lines without ~ish constructs."""
        constructs = find_ish_constructs("x = 42")
        assert len(constructs) == 0
        
        constructs = find_ish_constructs("if score == 100:")
        assert len(constructs) == 0
    
    def test_mixed_ish_constructs(self):
        """Test lines with both ish_value and ish_comparison."""
        # This should be parsed as a single nested construct: ish_comparison(score, ish_value(100))
        constructs = find_ish_constructs("if score ~ish 100~ish:")
        assert len(constructs) == 1
        assert constructs[0][0] == "ish_comparison_with_ish_value"
        assert constructs[0][1].group(1) == "score"
        assert constructs[0][1].group(2) == "100"


class TestIshTransformation:
    """Test transformation of ~ish constructs."""
    
    def test_transform_ish_value_simple(self):
        """Test transforming simple ish_value constructs."""
        result = _transform_ish_constructs("x = 42~ish")
        assert result == "x = ish_value(42)"
        
        result = _transform_ish_constructs("y = 3.14~ish")
        assert result == "y = ish_value(3.14)"
    
    def test_transform_ish_comparison_simple(self):
        """Test transforming simple ish_comparison constructs."""
        result = _transform_ish_constructs("if score ~ish 100:")
        assert result == "if ish_comparison(score, 100):"
        
        result = _transform_ish_constructs("while x ~ish target:")
        assert result == "while ish_comparison(x, target):"
    
    def test_transform_multiple_constructs(self):
        """Test transforming multiple ~ish constructs in one line."""
        result = _transform_ish_constructs("result = 42~ish + 100~ish")
        assert result == "result = ish_value(42) + ish_value(100)"
    
    def test_transform_mixed_constructs(self):
        """Test transforming mixed ish constructs."""
        result = _transform_ish_constructs("if score ~ish 100~ish:")
        # Should transform as nested construct
        assert result == "if ish_comparison(score, ish_value(100)):"
    
    def test_transform_line_integration(self):
        """Test transform_line integration with ish constructs."""
        result = transform_line("x = 42~ish")
        assert len(result) == 1
        assert result[0] == "x = ish_value(42)"
        
        result = transform_line("if score ~ish 100:")
        assert len(result) == 1
        assert result[0] == "if ish_comparison(score, 100):"
    
    def test_transform_preserves_other_content(self):
        """Test that transformation preserves non-ish content."""
        result = _transform_ish_constructs("x = 42~ish + y * 2")
        assert result == "x = ish_value(42) + y * 2"
        
        result = _transform_ish_constructs("if score ~ish 100 and valid:")
        assert result == "if ish_comparison(score, 100) and valid:"


class TestIshRuntimeBehavior:
    """Test runtime behavior of ish functions."""
    
    def test_ish_value_with_integer(self):
        """Test ish_value with integer inputs."""
        with patch('random.uniform', return_value=1.5):
            result = ish_value(42)
            assert result == 43  # int(42 + 1.5) = 43
            
        with patch('random.uniform', return_value=-0.8):
            result = ish_value(42)
            assert result == 41  # int(42 + (-0.8)) = 41
    
    def test_ish_value_with_float(self):
        """Test ish_value with float inputs."""
        with patch('random.uniform', return_value=1.2):
            result = ish_value(3.14)
            assert abs(result - 4.34) < 0.01  # 3.14 + 1.2 = 4.34
    
    def test_ish_value_default_variance(self):
        """Test ish_value uses ±2 variance by default."""
        # Mock random.uniform to check the variance parameter
        with patch('random.uniform') as mock_uniform:
            mock_uniform.return_value = 1.0
            ish_value(42)
            mock_uniform.assert_called_with(-2, 2)
    
    def test_ish_value_error_handling(self):
        """Test ish_value error handling with invalid inputs."""
        captured_output = StringIO()
        sys.stdout = captured_output
        
        with patch('random.uniform', return_value=1.0):
            result = ish_value("not_a_number")
            assert result == 1.0
            output = captured_output.getvalue()
            assert "[?] ish value got something weird" in output
            assert "[tip] Expected a number but got str" in output
            
        sys.stdout = sys.__stdout__
    
    def test_ish_comparison_within_tolerance(self):
        """Test ish_comparison when values are within tolerance."""
        assert ish_comparison(100, 100) is True  # Exact match
        assert ish_comparison(100, 102) is True  # Within ±2
        assert ish_comparison(100, 98) is True   # Within ±2
        assert ish_comparison(98, 100) is True   # Symmetric
    
    def test_ish_comparison_outside_tolerance(self):
        """Test ish_comparison when values are outside tolerance."""
        assert ish_comparison(100, 103) is False  # Outside ±2
        assert ish_comparison(100, 97) is False   # Outside ±2
        assert ish_comparison(95, 100) is False   # Outside ±2
    
    def test_ish_comparison_default_tolerance(self):
        """Test ish_comparison uses ±2 tolerance by default."""
        assert ish_comparison(50, 52) is True   # Exactly at boundary
        assert ish_comparison(50, 53) is False  # Just outside boundary
    
    def test_ish_comparison_with_floats(self):
        """Test ish_comparison with float values."""
        assert ish_comparison(3.14, 3.16) is True   # Within tolerance
        assert ish_comparison(3.14, 5.20) is False  # Outside tolerance
    
    def test_ish_comparison_error_handling(self):
        """Test ish_comparison error handling with invalid inputs."""
        captured_output = StringIO()
        sys.stdout = captured_output
        
        with patch('random.choice', return_value=True):
            result = ish_comparison("not_a_number", 100)
            assert result is True
            output = captured_output.getvalue()
            assert "[?] ish comparison got weird left value" in output
            
        sys.stdout = sys.__stdout__


class TestIshIntegration:
    """Test integration of ish constructs with other kinda constructs."""
    
    def test_ish_with_sorta_print(self):
        """Test ish constructs work with sorta_print."""
        from kinda.langs.python.transformer import transform_file
        
        # Create temporary file with mixed constructs
        with tempfile.NamedTemporaryFile(mode='w', suffix='.knda', delete=False) as f:
            f.write("~sorta print(42~ish)\n")
            f.write("if score ~ish 100~ish:\n")
            f.write("    ~sorta print('Match!')\n")
            temp_path = Path(f.name)
        
        try:
            result = transform_file(temp_path)
            assert "ish_value(42)" in result
            assert "ish_comparison(score, ish_value(100))" in result
            assert "sorta_print" in result
        finally:
            temp_path.unlink()
    
    def test_ish_with_conditional_blocks(self):
        """Test ish constructs work inside conditional blocks."""
        result = _transform_ish_constructs("    x = 42~ish  # Inside a block")
        assert result == "    x = ish_value(42)  # Inside a block"


class TestIshEdgeCases:
    """Test edge cases and error conditions for ish constructs."""
    
    def test_ish_value_edge_numbers(self):
        """Test ish_value with edge case numbers."""
        # Zero
        with patch('random.uniform', return_value=0.5):
            result = ish_value(0)
            assert result == 0  # int(0 + 0.5) = 0
        
        # Negative numbers
        with patch('random.uniform', return_value=-1.0):
            result = ish_value(-10)
            assert result == -11  # int(-10 + (-1.0)) = -11
    
    def test_ish_comparison_edge_values(self):
        """Test ish_comparison with edge case values."""
        # Boundary conditions
        assert ish_comparison(0, 2) is True    # Exactly at tolerance boundary
        assert ish_comparison(0, 2.1) is False # Just outside boundary
        
        # Negative numbers
        assert ish_comparison(-10, -12) is True   # Within tolerance
        assert ish_comparison(-10, -15) is False  # Outside tolerance
    
    def test_complex_expressions(self):
        """Test ish constructs in complex expressions."""
        result = _transform_ish_constructs("result = (42~ish * 2) if x ~ish target else 0")
        expected = "result = (ish_value(42) * 2) if ish_comparison(x, target) else 0"
        assert result == expected
    
    def test_whitespace_variations(self):
        """Test ish constructs with various whitespace patterns."""
        # No spaces
        result = _transform_ish_constructs("x=42~ish")
        assert result == "x=ish_value(42)"
        
        # Extra spaces around ~ish
        result = _transform_ish_constructs("if score  ~ish  100:")
        assert result == "if ish_comparison(score, 100):"
    
    def test_comments_preserved(self):
        """Test that comments are preserved during transformation."""
        result = _transform_ish_constructs("x = 42~ish  # This is fuzzy")
        assert result == "x = ish_value(42)  # This is fuzzy"
        
        result = _transform_ish_constructs("if score ~ish 100:  # Check if close")
        assert result == "if ish_comparison(score, 100):  # Check if close"


class TestIshUsedHelpersTracking:
    """Test that ish constructs are properly tracked in used_helpers."""
    
    def test_ish_value_adds_helper(self):
        """Test that using ish_value adds to used_helpers."""
        from kinda.langs.python.transformer import used_helpers
        
        # Clear helpers
        used_helpers.clear()
        
        # Transform ish_value
        _transform_ish_constructs("x = 42~ish")
        
        assert "ish_value" in used_helpers
    
    def test_ish_comparison_adds_helper(self):
        """Test that using ish_comparison adds to used_helpers."""
        from kinda.langs.python.transformer import used_helpers
        
        # Clear helpers
        used_helpers.clear()
        
        # Transform ish_comparison
        _transform_ish_constructs("if score ~ish 100:")
        
        assert "ish_comparison" in used_helpers
    
    def test_both_ish_helpers_tracked(self):
        """Test that both ish helpers are tracked when both are used."""
        from kinda.langs.python.transformer import used_helpers
        
        # Clear helpers
        used_helpers.clear()
        
        # Transform both constructs
        _transform_ish_constructs("if score ~ish 100~ish:")
        
        assert "ish_value" in used_helpers
        assert "ish_comparison" in used_helpers


if __name__ == "__main__":
    pytest.main([__file__])