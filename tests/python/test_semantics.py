"""
Comprehensive test suite for kinda/langs/python/semantics.py
Target: 95% coverage for semantic evaluation functions
"""

import pytest
import random
from unittest.mock import patch, MagicMock
from io import StringIO
import sys

# Import the semantics module
from kinda.langs.python import semantics


class TestEvaluate:
    """Test the evaluate function with various expressions."""
    
    def test_evaluate_simple_expression(self):
        """Test evaluating simple mathematical expressions."""
        # Set up environment with a variable
        semantics.env['x'] = 10
        
        result = semantics.evaluate("x + 5")
        assert result == 15
        
        result = semantics.evaluate("x * 2")
        assert result == 20
        
        result = semantics.evaluate("100 - x")
        assert result == 90
    
    def test_evaluate_with_empty_env(self):
        """Test evaluating with empty environment."""
        semantics.env.clear()
        
        result = semantics.evaluate("42")
        assert result == 42
        
        result = semantics.evaluate("1 + 2 + 3")
        assert result == 6
    
    def test_evaluate_invalid_expression(self):
        """Test evaluating invalid expressions returns None."""
        result = semantics.evaluate("undefined_variable")
        assert result is None
        
        result = semantics.evaluate("1 / 0")  # Division by zero
        assert result is None
        
        result = semantics.evaluate("invalid syntax !!!")
        assert result is None
    
    def test_evaluate_with_existing_env_variables(self):
        """Test that evaluate uses the env dictionary."""
        semantics.env['foo'] = "bar"
        semantics.env['num'] = 42
        
        result = semantics.evaluate("foo")
        assert result == "bar"
        
        result = semantics.evaluate("num + 8")
        assert result == 50
        
        # Clean up
        semantics.env.clear()


class TestKindaAssign:
    """Test the kinda_assign function."""
    
    def test_kinda_assign_integer(self):
        """Test kinda assignment with integer values."""
        captured_output = StringIO()
        sys.stdout = captured_output
        
        with patch('random.choice', return_value=1):
            semantics.kinda_assign('x', '42')
            assert semantics.env['x'] == 43
            output = captured_output.getvalue()
            assert "[assign] x ~= 43" in output
            
        sys.stdout = sys.__stdout__
        semantics.env.clear()
    
    def test_kinda_assign_float(self):
        """Test kinda assignment with float values."""
        captured_output = StringIO()
        sys.stdout = captured_output
        
        with patch('random.choice', return_value=-1):
            semantics.kinda_assign('y', '3.14')
            assert semantics.env['y'] == 2.14
            output = captured_output.getvalue()
            assert "[assign] y ~= 2.14" in output
            
        sys.stdout = sys.__stdout__
        semantics.env.clear()
    
    def test_kinda_assign_with_zero_fuzz(self):
        """Test kinda assignment with zero fuzz value."""
        captured_output = StringIO()
        sys.stdout = captured_output
        
        with patch('random.choice', return_value=0):
            semantics.kinda_assign('z', '100')
            assert semantics.env['z'] == 100
            output = captured_output.getvalue()
            assert "[assign] z ~= 100" in output
            
        sys.stdout = sys.__stdout__
        semantics.env.clear()
    
    def test_kinda_assign_non_numeric(self):
        """Test kinda assignment with non-numeric values."""
        captured_output = StringIO()
        sys.stdout = captured_output
        
        semantics.kinda_assign('name', '"John"')
        assert semantics.env['name'] == "John"
        output = captured_output.getvalue()
        assert "[assign] name ~= John" in output
        
        sys.stdout = sys.__stdout__
        semantics.env.clear()
    
    def test_kinda_assign_failed_evaluation(self):
        """Test kinda assignment when evaluation fails."""
        captured_output = StringIO()
        sys.stdout = captured_output
        
        semantics.kinda_assign('bad', 'undefined_variable')
        assert 'bad' not in semantics.env
        output = captured_output.getvalue()
        assert "[assign] bad skipped (evaluation failed)" in output
        
        sys.stdout = sys.__stdout__
        semantics.env.clear()
    
    def test_kinda_assign_expression(self):
        """Test kinda assignment with expressions."""
        captured_output = StringIO()
        sys.stdout = captured_output
        
        semantics.env['a'] = 10
        with patch('random.choice', return_value=1):
            semantics.kinda_assign('b', 'a * 2')
            assert semantics.env['b'] == 21  # (10 * 2) + 1
            output = captured_output.getvalue()
            assert "[assign] b ~= 21" in output
            
        sys.stdout = sys.__stdout__
        semantics.env.clear()


class TestSortaPrint:
    """Test the sorta_print function."""
    
    def test_sorta_print_success(self):
        """Test sorta_print when random allows printing."""
        captured_output = StringIO()
        sys.stdout = captured_output
        
        semantics.env['msg'] = "Hello World"
        
        with patch('random.random', return_value=0.5):  # Less than 0.8
            semantics.sorta_print('msg')
            output = captured_output.getvalue()
            assert "[print] Hello World" in output
            
        sys.stdout = sys.__stdout__
        semantics.env.clear()
    
    def test_sorta_print_skipped(self):
        """Test sorta_print when random prevents printing."""
        captured_output = StringIO()
        sys.stdout = captured_output
        
        semantics.env['msg'] = "Should not print"
        
        with patch('random.random', return_value=0.9):  # Greater than 0.8
            semantics.sorta_print('msg')
            output = captured_output.getvalue()
            assert output == ""  # Nothing printed
            
        sys.stdout = sys.__stdout__
        semantics.env.clear()
    
    def test_sorta_print_expression(self):
        """Test sorta_print with expressions."""
        captured_output = StringIO()
        sys.stdout = captured_output
        
        semantics.env['x'] = 5
        semantics.env['y'] = 10
        
        with patch('random.random', return_value=0.5):
            semantics.sorta_print('x + y')
            output = captured_output.getvalue()
            assert "[print] 15" in output
            
        sys.stdout = sys.__stdout__
        semantics.env.clear()
    
    def test_sorta_print_failed_evaluation(self):
        """Test sorta_print when evaluation fails."""
        captured_output = StringIO()
        sys.stdout = captured_output
        
        with patch('random.random', return_value=0.5):
            semantics.sorta_print('undefined_var')
            output = captured_output.getvalue()
            assert "[print] Failed to evaluate: undefined_var" in output
            
        sys.stdout = sys.__stdout__
        semantics.env.clear()
    
    def test_sorta_print_string_literal(self):
        """Test sorta_print with string literals."""
        captured_output = StringIO()
        sys.stdout = captured_output
        
        with patch('random.random', return_value=0.5):
            semantics.sorta_print('"Direct string"')
            output = captured_output.getvalue()
            assert "[print] Direct string" in output
            
        sys.stdout = sys.__stdout__


class TestRunSometimesBlock:
    """Test the run_sometimes_block function."""
    
    def test_run_sometimes_block_false_condition(self):
        """Test sometimes block doesn't execute when condition is false."""
        captured_output = StringIO()
        sys.stdout = captured_output
        
        # Mock evaluate to return False for the condition
        with patch('kinda.langs.python.semantics.evaluate', return_value=False):
            with patch('random.random', return_value=0.5):  # Less than 0.7
                block_lines = ['print("Should not run")']
                semantics.run_sometimes_block('x > 5', block_lines)
                
                output = captured_output.getvalue()
                assert "[sometimes] condition false" in output
            
        sys.stdout = sys.__stdout__
    
    def test_run_sometimes_block_randomly_skipped(self):
        """Test sometimes block skipped when random prevents execution."""
        captured_output = StringIO()
        sys.stdout = captured_output
        
        with patch('random.random', return_value=0.8):  # Greater than 0.7
            block_lines = ['print("Should not run")']
            semantics.run_sometimes_block('x > 5', block_lines)
            
            output = captured_output.getvalue()
            assert "[sometimes] skipped randomly" in output
            
        sys.stdout = sys.__stdout__
    
    def test_run_sometimes_block_invalid_condition(self):
        """Test sometimes block with invalid condition."""
        captured_output = StringIO()
        sys.stdout = captured_output
        
        # Mock evaluate to return None for invalid condition
        with patch('kinda.langs.python.semantics.evaluate', return_value=None):
            with patch('random.random', return_value=0.5):
                block_lines = ['print("test")']
                semantics.run_sometimes_block('undefined_var > 5', block_lines)
                
                output = captured_output.getvalue()
                assert "[sometimes] condition false" in output
            
        sys.stdout = sys.__stdout__