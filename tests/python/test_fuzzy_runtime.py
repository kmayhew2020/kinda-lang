"""
Comprehensive test suite for kinda/langs/python/runtime/fuzzy.py
Target: 95% coverage for all fuzzy runtime functions
"""

import pytest
import random
from unittest.mock import patch, MagicMock
from io import StringIO
import sys

# Import the fuzzy runtime module - generate it if it doesn't exist
try:
    from kinda.langs.python.runtime.fuzzy import (
        fuzzy_assign, kinda_binary, kinda_int, maybe, sometimes, sorta_print, env
    )
except ImportError:
    # Generate the runtime module if it doesn't exist
    from pathlib import Path
    import tempfile
    from kinda.langs.python import transformer
    
    # Create a minimal .knda file to trigger runtime generation
    with tempfile.NamedTemporaryFile(mode='w', suffix='.knda', delete=False) as f:
        f.write("~kinda int x = 42\n~kinda binary y\n~sorta print('test')\n~maybe (True) { }\n~sometimes (True) { }")
        temp_path = Path(f.name)
    
    try:
        # Transform to generate runtime
        transformer.transform_file(temp_path, out_dir=Path("build"))
    finally:
        temp_path.unlink()
    
    # Now import should work
    from kinda.langs.python.runtime.fuzzy import (
        fuzzy_assign, kinda_binary, kinda_int, maybe, sometimes, sorta_print, env
    )


class TestFuzzyAssign:
    """Test fuzzy_assign function with various inputs and edge cases."""
    
    def test_fuzzy_assign_with_integer(self):
        """Test fuzzy assignment with integer values."""
        with patch('random.randint', return_value=1):
            result = fuzzy_assign('x', 42)
            assert result == 43
            
        with patch('random.randint', return_value=-1):
            result = fuzzy_assign('x', 42)
            assert result == 41
            
        with patch('random.randint', return_value=0):
            result = fuzzy_assign('x', 42)
            assert result == 42
    
    def test_fuzzy_assign_with_float(self):
        """Test fuzzy assignment with float values."""
        with patch('random.randint', return_value=1):
            result = fuzzy_assign('x', 42.5)
            assert result == 43
            
    def test_fuzzy_assign_with_string_number(self):
        """Test fuzzy assignment with string that can be converted to number."""
        captured_output = StringIO()
        sys.stdout = captured_output
        
        with patch('random.randint', return_value=1):
            result = fuzzy_assign('x', "42")
            assert result == 43
            
        sys.stdout = sys.__stdout__
    
    def test_fuzzy_assign_with_invalid_string(self):
        """Test fuzzy assignment with non-numeric string."""
        captured_output = StringIO()
        sys.stdout = captured_output
        
        with patch('random.randint', return_value=5):
            result = fuzzy_assign('x', "not_a_number")
            assert result == 5
            output = captured_output.getvalue()
            assert "[?] fuzzy assignment got something weird" in output
            assert "[tip] Expected a number but got str" in output
            
        sys.stdout = sys.__stdout__
    
    def test_fuzzy_assign_with_none(self):
        """Test fuzzy assignment with None value."""
        captured_output = StringIO()
        sys.stdout = captured_output
        
        with patch('random.randint', return_value=7):
            result = fuzzy_assign('x', None)
            assert result == 7
            output = captured_output.getvalue()
            assert "[?] fuzzy assignment got something weird" in output
            
        sys.stdout = sys.__stdout__
    
    def test_fuzzy_assign_with_exception(self):
        """Test fuzzy assignment exception handling."""
        captured_output = StringIO()
        sys.stdout = captured_output
        
        # Test with list which can't be converted to float
        with patch('random.randint', return_value=3):
            result = fuzzy_assign('x', [1, 2, 3])
            assert result == 3
            output = captured_output.getvalue()
            assert "[?] fuzzy assignment got something weird" in output
            assert "[tip] Expected a number but got list" in output
            
        sys.stdout = sys.__stdout__


class TestKindaBinary:
    """Test kinda_binary function with various probability configurations."""
    
    def test_kinda_binary_default_probabilities(self):
        """Test kinda_binary with default probabilities."""
        # Test positive outcome
        with patch('random.random', return_value=0.2):
            result = kinda_binary()
            assert result == 1
            
        # Test negative outcome
        with patch('random.random', return_value=0.5):
            result = kinda_binary()
            assert result == -1
            
        # Test neutral outcome
        with patch('random.random', return_value=0.9):
            result = kinda_binary()
            assert result == 0
    
    def test_kinda_binary_custom_probabilities(self):
        """Test kinda_binary with custom probabilities."""
        # High positive probability
        with patch('random.random', return_value=0.3):
            result = kinda_binary(pos_prob=0.8, neg_prob=0.1, neutral_prob=0.1)
            assert result == 1
            
        # High negative probability
        with patch('random.random', return_value=0.3):
            result = kinda_binary(pos_prob=0.1, neg_prob=0.8, neutral_prob=0.1)
            assert result == -1
    
    def test_kinda_binary_invalid_probabilities(self):
        """Test kinda_binary with probabilities that don't sum to 1."""
        captured_output = StringIO()
        sys.stdout = captured_output
        
        with patch('random.random', return_value=0.3):
            result = kinda_binary(pos_prob=0.5, neg_prob=0.3, neutral_prob=0.1)
            assert result in [1, -1, 0]
            output = captured_output.getvalue()
            assert "[?] Binary probabilities don't add up to 1.0" in output
            assert "[tip] Normalizing" in output
            
        sys.stdout = sys.__stdout__
    
    def test_kinda_binary_exception_handling(self):
        """Test kinda_binary exception handling."""
        captured_output = StringIO()
        sys.stdout = captured_output
        
        # Force an exception by patching random.random to raise
        with patch('random.random', side_effect=Exception("Random failed")):
            with patch('random.choice', return_value=0):
                result = kinda_binary()
                assert result == 0
                output = captured_output.getvalue()
                assert "[shrug] Binary choice kinda broke" in output
                assert "[tip] Defaulting to random choice" in output
                
        sys.stdout = sys.__stdout__


class TestKindaInt:
    """Test kinda_int function with various inputs."""
    
    def test_kinda_int_with_integer(self):
        """Test kinda_int with integer input."""
        with patch('random.randint', return_value=1):
            result = kinda_int(42)
            assert result == 43
            
    def test_kinda_int_with_float(self):
        """Test kinda_int with float input."""
        with patch('random.randint', return_value=-1):
            result = kinda_int(42.7)
            assert result == 41
            
    def test_kinda_int_with_string_number(self):
        """Test kinda_int with numeric string."""
        captured_output = StringIO()
        sys.stdout = captured_output
        
        with patch('random.randint', return_value=0):
            result = kinda_int("100")
            assert result == 100
            
        sys.stdout = sys.__stdout__
    
    def test_kinda_int_with_invalid_input(self):
        """Test kinda_int with invalid input."""
        captured_output = StringIO()
        sys.stdout = captured_output
        
        with patch('random.randint', return_value=8):
            result = kinda_int("not_a_number")
            assert result == 8
            output = captured_output.getvalue()
            assert "[?] kinda int got something weird" in output
            assert "[tip] Expected a number but got str" in output
            
        sys.stdout = sys.__stdout__
    
    def test_kinda_int_with_exception(self):
        """Test kinda_int exception handling."""
        captured_output = StringIO()
        sys.stdout = captured_output
        
        # Test with object that raises exception
        class BadNumber:
            def __float__(self):
                raise ValueError("Cannot convert")
        
        with patch('random.randint', return_value=4):
            result = kinda_int(BadNumber())
            assert result == 4
            output = captured_output.getvalue()
            assert "[?] kinda int got something weird" in output
            
        sys.stdout = sys.__stdout__


class TestMaybe:
    """Test maybe function with various conditions."""
    
    def test_maybe_true_condition(self):
        """Test maybe with True condition."""
        # Should return True 60% of the time when condition is True
        with patch('random.random', return_value=0.5):
            result = maybe(True)
            assert result is True
            
        with patch('random.random', return_value=0.7):
            result = maybe(True)
            assert result is False
    
    def test_maybe_false_condition(self):
        """Test maybe with False condition."""
        # Should always return False when condition is False
        with patch('random.random', return_value=0.1):
            result = maybe(False)
            assert result is False
            
    def test_maybe_none_condition(self):
        """Test maybe with None condition."""
        captured_output = StringIO()
        sys.stdout = captured_output
        
        result = maybe(None)
        assert result is False
        output = captured_output.getvalue()
        assert "[?] Maybe got None as condition" in output
        
        sys.stdout = sys.__stdout__
    
    def test_maybe_exception_handling(self):
        """Test maybe with truthy/falsy conditions."""
        # Maybe should work with any truthy/falsy value
        with patch('random.random', return_value=0.5):
            assert maybe(1) is True
            assert maybe(0) is False
            assert maybe("") is False
            assert maybe("text") is True
            assert maybe([]) is False
            assert maybe([1, 2]) is True


class TestSometimes:
    """Test sometimes function with various conditions."""
    
    def test_sometimes_true_condition(self):
        """Test sometimes with True condition."""
        # Should return True 50% of the time when condition is True
        with patch('random.random', return_value=0.3):
            result = sometimes(True)
            assert result is True
            
        with patch('random.random', return_value=0.7):
            result = sometimes(True)
            assert result is False
    
    def test_sometimes_false_condition(self):
        """Test sometimes with False condition."""
        # Should always return False when condition is False
        with patch('random.random', return_value=0.1):
            result = sometimes(False)
            assert result is False
            
    def test_sometimes_none_condition(self):
        """Test sometimes with None condition."""
        captured_output = StringIO()
        sys.stdout = captured_output
        
        result = sometimes(None)
        assert result is False
        output = captured_output.getvalue()
        assert "[?] Sometimes got None as condition" in output
        
        sys.stdout = sys.__stdout__
    
    def test_sometimes_exception_handling(self):
        """Test sometimes with truthy/falsy conditions."""
        # Sometimes should work with any truthy/falsy value
        with patch('random.random', return_value=0.3):
            assert sometimes(1) is True
            assert sometimes(0) is False
            assert sometimes("") is False
            assert sometimes("text") is True
            assert sometimes([]) is False
            assert sometimes([1, 2]) is True


class TestSortaPrint:
    """Test sorta_print function with various inputs."""
    
    def test_sorta_print_with_args(self):
        """Test sorta_print with normal arguments."""
        captured_output = StringIO()
        sys.stdout = captured_output
        
        # Test when it prints (80% chance)
        with patch('random.random', return_value=0.5):
            sorta_print("Hello", "World")
            output = captured_output.getvalue()
            assert "[print] Hello World" in output
            
        sys.stdout = sys.__stdout__
    
    def test_sorta_print_shrug_response(self):
        """Test sorta_print shrug responses (20% chance)."""
        captured_output = StringIO()
        sys.stdout = captured_output
        
        # Test when it shrugs (20% chance)
        with patch('random.random', return_value=0.9):
            with patch('random.choice', return_value='[shrug] Meh...'):
                sorta_print("Hello")
                output = captured_output.getvalue()
                assert "[shrug] Meh... Hello" in output
                
        sys.stdout = sys.__stdout__
    
    def test_sorta_print_no_args(self):
        """Test sorta_print with no arguments."""
        captured_output = StringIO()
        sys.stdout = captured_output
        
        with patch('random.random', return_value=0.3):
            sorta_print()
            output = captured_output.getvalue()
            assert "[shrug] Nothing to print, I guess?" in output
            
        sys.stdout = sys.__stdout__
    
    def test_sorta_print_no_args_no_output(self):
        """Test sorta_print with no arguments when random > 0.5."""
        captured_output = StringIO()
        sys.stdout = captured_output
        
        with patch('random.random', return_value=0.7):
            sorta_print()
            output = captured_output.getvalue()
            assert output == ""
            
        sys.stdout = sys.__stdout__
    
    def test_sorta_print_with_various_types(self):
        """Test sorta_print with various data types."""
        captured_output = StringIO()
        sys.stdout = captured_output
        
        with patch('random.random', return_value=0.5):
            # Test with different types
            sorta_print(42)
            sorta_print(3.14)
            sorta_print([1, 2, 3])
            sorta_print({"key": "value"})
            sorta_print(None)
            
            output = captured_output.getvalue()
            assert "[print] 42" in output
            assert "[print] 3.14" in output
            assert "[print] [1, 2, 3]" in output
            assert "[print] {'key': 'value'}" in output
            assert "[print] None" in output
            
        sys.stdout = sys.__stdout__
    
    def test_sorta_print_various_shrug_responses(self):
        """Test that various shrug responses work."""
        shrug_responses = [
            '[shrug] Not feeling it right now',
            '[shrug] Maybe later?',
            '[shrug] *waves hand dismissively*',
            '[shrug] Kinda busy'
        ]
        
        for response in shrug_responses:
            captured_output = StringIO()
            sys.stdout = captured_output
            
            with patch('random.random', return_value=0.9):
                with patch('random.choice', return_value=response):
                    sorta_print("test")
                    output = captured_output.getvalue()
                    assert response in output
                    assert "test" in output
                    
            sys.stdout = sys.__stdout__


class TestEnvironmentDict:
    """Test that all functions are properly added to the env dictionary."""
    
    def test_env_contains_all_functions(self):
        """Verify all fuzzy functions are in the environment dictionary."""
        assert "fuzzy_assign" in env
        assert env["fuzzy_assign"] == fuzzy_assign
        
        assert "kinda_binary" in env
        assert env["kinda_binary"] == kinda_binary
        
        assert "kinda_int" in env
        assert env["kinda_int"] == kinda_int
        
        assert "maybe" in env
        assert env["maybe"] == maybe
        
        assert "sometimes" in env
        assert env["sometimes"] == sometimes
        
        assert "sorta_print" in env
        assert env["sorta_print"] == sorta_print