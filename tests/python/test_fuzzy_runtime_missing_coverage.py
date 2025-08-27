"""
Test coverage for missing functions in runtime/fuzzy.py
Focuses on: ish_comparison, ish_value (welp_fallback disabled)
Target: Cover lines 27-51, 57-76
"""

import pytest
import random
from unittest.mock import patch, MagicMock
from io import StringIO
import sys

# Import the functions we need to test (welp_fallback imported but tests disabled)
from kinda.langs.python.runtime.fuzzy import (
    ish_comparison, ish_value, welp_fallback, env
)


class TestIshComparison:
    """Test ish_comparison function with various inputs and edge cases."""
    
    def test_ish_comparison_numeric_within_tolerance(self):
        """Test ish_comparison with numeric values within tolerance."""
        # Test exact match
        result = ish_comparison(42, 42)
        assert result is True
        
        # Test within default tolerance (2)
        result = ish_comparison(42, 44)
        assert result is True
        
        result = ish_comparison(42, 40)
        assert result is True
        
        # Test at tolerance boundary
        result = ish_comparison(10, 12)
        assert result is True
        
        result = ish_comparison(10, 8)
        assert result is True
    
    def test_ish_comparison_numeric_outside_tolerance(self):
        """Test ish_comparison with numeric values outside tolerance."""
        # Test outside default tolerance (2)
        result = ish_comparison(42, 45)
        assert result is False
        
        result = ish_comparison(42, 39)
        assert result is False
        
        # Test with custom tolerance
        result = ish_comparison(10, 15, tolerance=3)
        assert result is False
        
        result = ish_comparison(10, 13, tolerance=3)
        assert result is True
    
    def test_ish_comparison_string_to_float_conversion(self):
        """Test ish_comparison with string that converts to float."""
        result = ish_comparison("42", 44)
        assert result is True
        
        result = ish_comparison(42, "40")
        assert result is True
        
        result = ish_comparison("10.5", "11.5")
        assert result is True
    
    def test_ish_comparison_left_value_conversion_error(self):
        """Test ish_comparison when left value can't be converted to numeric."""
        captured_output = StringIO()
        sys.stdout = captured_output
        
        with patch('random.choice', return_value=True):
            result = ish_comparison("not_a_number", 42)
            assert result is True
            
        output = captured_output.getvalue()
        assert "[?] ish comparison got weird left value: 'not_a_number'" in output
        assert "[tip] Expected a number but got str" in output
        
        sys.stdout = sys.__stdout__
    
    def test_ish_comparison_right_value_conversion_error(self):
        """Test ish_comparison when right value can't be converted to numeric."""
        captured_output = StringIO()
        sys.stdout = captured_output
        
        with patch('random.choice', return_value=False):
            result = ish_comparison(42, "not_a_number")
            assert result is False
            
        output = captured_output.getvalue()
        assert "[?] ish comparison got weird right value: 'not_a_number'" in output
        assert "[tip] Expected a number but got str" in output
        
        sys.stdout = sys.__stdout__
    
    def test_ish_comparison_both_values_conversion_error(self):
        """Test ish_comparison when both values can't be converted."""
        captured_output = StringIO()
        sys.stdout = captured_output
        
        with patch('random.choice', side_effect=[True, False]):
            # First call returns True for left error
            result1 = ish_comparison("left_bad", 42)
            assert result1 is True
            
            # Reset output
            captured_output.truncate(0)
            captured_output.seek(0)
            
            # Second call returns False for right error
            result2 = ish_comparison(42, "right_bad")
            assert result2 is False
            
        sys.stdout = sys.__stdout__
    
    def test_ish_comparison_exception_handling(self):
        """Test ish_comparison general exception handling."""
        captured_output = StringIO()
        sys.stdout = captured_output
        
        # Force an exception by patching abs to raise
        with patch('builtins.abs', side_effect=Exception("Math error")):
            with patch('random.choice', return_value=True):
                result = ish_comparison(10, 12)
                assert result is True
                
        output = captured_output.getvalue()
        assert "[shrug] Ish comparison kinda broke: Math error" in output
        assert "[tip] Flipping a coin instead" in output
        
        sys.stdout = sys.__stdout__
    
    def test_ish_comparison_with_none_values(self):
        """Test ish_comparison with None values."""
        captured_output = StringIO()
        sys.stdout = captured_output
        
        with patch('random.choice', return_value=True):
            result = ish_comparison(None, 42)
            assert result is True
            
        with patch('random.choice', return_value=False):
            result = ish_comparison(42, None)
            assert result is False
            
        sys.stdout = sys.__stdout__


class TestIshValue:
    """Test ish_value function with various inputs and edge cases."""
    
    def test_ish_value_with_integer(self):
        """Test ish_value with integer input."""
        with patch('random.uniform', return_value=1.0):
            result = ish_value(42)
            assert result == 43  # Should return integer since input was integer
            assert isinstance(result, int)
    
    def test_ish_value_with_float(self):
        """Test ish_value with float input."""
        with patch('random.uniform', return_value=1.5):
            result = ish_value(42.0)
            assert result == 43.5  # Should return float since input was float
            assert isinstance(result, float)
    
    def test_ish_value_with_custom_variance(self):
        """Test ish_value with custom variance."""
        with patch('random.uniform', return_value=3.0):
            result = ish_value(10, variance=5)
            assert result == 13
    
    def test_ish_value_with_negative_variance(self):
        """Test ish_value with negative variance (fuzzy decrease)."""
        with patch('random.uniform', return_value=-1.0):
            result = ish_value(42)
            assert result == 41
    
    def test_ish_value_string_to_float_conversion(self):
        """Test ish_value with string that converts to number."""
        with patch('random.uniform', return_value=0.5):
            result = ish_value("42.5")
            assert result == 43.0
    
    def test_ish_value_conversion_error(self):
        """Test ish_value when input can't be converted to numeric."""
        captured_output = StringIO()
        sys.stdout = captured_output
        
        with patch('random.uniform', return_value=1.5):
            result = ish_value("not_a_number", variance=3)
            assert result == 1.5  # Should return random value with variance
            
        output = captured_output.getvalue()
        assert "[?] ish value got something weird: 'not_a_number'" in output
        assert "[tip] Expected a number but got str" in output
        
        sys.stdout = sys.__stdout__
    
    def test_ish_value_with_list_input(self):
        """Test ish_value with list input (should trigger error path)."""
        captured_output = StringIO()
        sys.stdout = captured_output
        
        with patch('random.uniform', return_value=2.0):
            result = ish_value([1, 2, 3])
            assert result == 2.0
            
        output = captured_output.getvalue()
        assert "[?] ish value got something weird: [1, 2, 3]" in output
        assert "[tip] Expected a number but got list" in output
        
        sys.stdout = sys.__stdout__
    
    def test_ish_value_edge_cases(self):
        """Test ish_value with additional edge cases."""
        # Test with zero variance (should return original value)
        with patch('random.uniform', return_value=0.0):
            result = ish_value(42, variance=0)
            assert result == 42
            
        # Test with very small variance
        with patch('random.uniform', return_value=0.1):
            result = ish_value(100.0, variance=0.5)
            assert result == 100.1
    
    def test_ish_value_with_none_input(self):
        """Test ish_value with None input."""
        captured_output = StringIO()
        sys.stdout = captured_output
        
        with patch('random.uniform', return_value=-0.5):
            result = ish_value(None)
            assert result == -0.5
            
        output = captured_output.getvalue()
        assert "[?] ish value got something weird: None" in output
        assert "[tip] Expected a number but got NoneType" in output
        
        sys.stdout = sys.__stdout__


@pytest.mark.skip("welp construct is disabled - skipping welp_fallback tests")
class TestWelpFallback:
    """Test welp_fallback function - DISABLED (welp construct is disabled)."""
    
    def test_welp_fallback_with_direct_value(self):
        """Test welp_fallback with direct value (non-callable)."""
        result = welp_fallback(42, "fallback")
        assert result == 42
        
        result = welp_fallback("hello", "fallback") 
        assert result == "hello"
        
        result = welp_fallback([1, 2, 3], "fallback")
        assert result == [1, 2, 3]
    
    def test_welp_fallback_with_callable_success(self):
        """Test welp_fallback with successful callable execution."""
        def success_func():
            return "success"
            
        result = welp_fallback(success_func, "fallback")
        assert result == "success"
    
    def test_welp_fallback_with_callable_exception(self):
        """Test welp_fallback when callable raises exception."""
        captured_output = StringIO()
        sys.stdout = captured_output
        
        def failing_func():
            raise ValueError("Something went wrong")
            
        result = welp_fallback(failing_func, "fallback_value")
        assert result == "fallback_value"
        
        output = captured_output.getvalue()
        assert "[welp] Operation failed (ValueError: Something went wrong), using fallback: 'fallback_value'" in output
        
        sys.stdout = sys.__stdout__
    
    def test_welp_fallback_with_none_result(self):
        """Test welp_fallback when callable returns None."""
        captured_output = StringIO()
        sys.stdout = captured_output
        
        def none_func():
            return None
            
        result = welp_fallback(none_func, "used_fallback")
        assert result == "used_fallback"
        
        output = captured_output.getvalue()
        assert "[welp] Got None, using fallback: 'used_fallback'" in output
        
        sys.stdout = sys.__stdout__
    
    def test_welp_fallback_with_none_direct_value(self):
        """Test welp_fallback with None as direct value."""
        captured_output = StringIO()
        sys.stdout = captured_output
        
        result = welp_fallback(None, "fallback_for_none")
        assert result == "fallback_for_none"
        
        output = captured_output.getvalue()
        assert "[welp] Got None, using fallback: 'fallback_for_none'" in output
        
        sys.stdout = sys.__stdout__
    
    def test_welp_fallback_with_falsy_but_valid_values(self):
        """Test welp_fallback with falsy but valid values (0, False, empty string)."""
        # These should NOT trigger fallback since they're not None
        result = welp_fallback(0, "fallback")
        assert result == 0
        
        result = welp_fallback(False, "fallback")
        assert result is False
        
        result = welp_fallback("", "fallback")
        assert result == ""
        
        result = welp_fallback([], "fallback")
        assert result == []
    
    def test_welp_fallback_with_lambda(self):
        """Test welp_fallback with lambda function."""
        result = welp_fallback(lambda: "lambda_result", "fallback")
        assert result == "lambda_result"
        
        # Lambda that raises exception
        captured_output = StringIO()
        sys.stdout = captured_output
        
        result = welp_fallback(lambda: 1/0, "division_fallback")
        assert result == "division_fallback"
        
        output = captured_output.getvalue()
        assert "[welp] Operation failed (ZeroDivisionError:" in output
        
        sys.stdout = sys.__stdout__
    
    def test_welp_fallback_with_complex_callable(self):
        """Test welp_fallback with more complex callable scenarios."""
        class ComplexObject:
            def __call__(self):
                return {"complex": "result"}
                
        obj = ComplexObject()
        result = welp_fallback(obj, "fallback")
        assert result == {"complex": "result"}
        
        # Test with method
        class WithMethod:
            def get_value(self):
                return "method_result"
        
        instance = WithMethod()
        result = welp_fallback(instance.get_value, "method_fallback")
        assert result == "method_result"


class TestEnvironmentIntegration:
    """Test that new functions are properly added to the env dictionary."""
    
    def test_env_contains_new_functions(self):
        """Verify new fuzzy functions are in the environment dictionary."""
        assert "ish_comparison" in env
        assert env["ish_comparison"] == ish_comparison
        
        assert "ish_value" in env  
        assert env["ish_value"] == ish_value
        
        # welp_fallback exists in runtime but tests are disabled
        assert "welp_fallback" in env
        assert env["welp_fallback"] == welp_fallback