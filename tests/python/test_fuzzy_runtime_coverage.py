#!/usr/bin/env python3

import pytest
from unittest.mock import patch, MagicMock
import random
from kinda.langs.python.runtime.fuzzy import (
    fuzzy_assign, kinda_int, maybe, sometimes, sorta_print
)


class TestFuzzyAssignErrorHandling:
    """Test fuzzy_assign error handling - covers lines 18-21"""
    
    def test_fuzzy_assign_exception_during_processing(self):
        """Test fuzzy_assign when an exception occurs during processing"""
        # Mock random.randint to raise an exception the first time, then work normally
        call_count = 0
        def mock_randint(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:  # First call fails
                raise Exception("Random generator failed")
            return 5  # Subsequent calls return fixed value
        
        with patch('random.randint', side_effect=mock_randint):
            with patch('builtins.print') as mock_print:
                result = fuzzy_assign("test_var", 42)
                
                # Should print error messages and return fallback
                calls = [call.args[0] for call in mock_print.call_args_list]
                assert any("Fuzzy assignment kinda failed: Random generator failed" in call for call in calls)
                assert any("Returning a random number because why not?" in call for call in calls)
                
                # Should return a fallback value
                assert isinstance(result, int)
                assert result == 5


class TestKindaIntErrorHandling:
    """Test kinda_int error handling - covers lines 65-68"""
    
    def test_kinda_int_exception_during_processing(self):
        """Test kinda_int when an exception occurs during processing"""
        # Mock random.randint to raise an exception the first time, then work normally
        call_count = 0
        def mock_randint(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:  # First call fails
                raise Exception("Random error")
            return 5  # Subsequent calls return fixed value
        
        with patch('random.randint', side_effect=mock_randint):
            with patch('builtins.print') as mock_print:
                result = kinda_int(42)
                
                # Should print error messages
                calls = [call.args[0] for call in mock_print.call_args_list]
                assert any("Kinda int got kinda confused: Random error" in call for call in calls)
                assert any("Just picking a random number instead" in call for call in calls)
                
                # Should return a fallback value
                assert isinstance(result, int)
                assert result == 5


class TestMaybeErrorHandling:
    """Test maybe error handling - covers lines 79-82"""
    
    def test_maybe_exception_during_evaluation(self):
        """Test maybe when an exception occurs during evaluation"""
        # Create a condition that raises an exception when converted to bool
        class ProblematicCondition:
            def __bool__(self):
                raise ValueError("Condition evaluation failed")
        
        with patch('builtins.print') as mock_print:
            with patch('random.random', return_value=0.5):  # < 0.6, will evaluate condition
                with patch('random.choice', return_value=True) as mock_choice:
                    result = maybe(ProblematicCondition())
                
                    # Should print error messages
                    calls = [call.args[0] for call in mock_print.call_args_list]
                    assert any("Maybe couldn't decide:" in call for call in calls)
                    assert any("Condition evaluation failed" in call for call in calls)
                    assert any("Defaulting to random choice" in call for call in calls)
                    
                    # Should call random.choice as fallback
                    mock_choice.assert_called_once_with([True, False])
                    assert result is True  # from our mock


class TestSometimesErrorHandling:
    """Test sometimes error handling - covers lines 93-96"""
    
    def test_sometimes_exception_during_evaluation(self):
        """Test sometimes when an exception occurs during evaluation"""
        # Create a condition that raises an exception when evaluated as bool
        class ProblematicCondition:
            def __bool__(self):
                raise RuntimeError("Boolean conversion failed")
        
        with patch('builtins.print') as mock_print:
            with patch('random.random', return_value=0.3):  # < 0.5, will evaluate condition
                with patch('random.choice', return_value=False) as mock_choice:
                    result = sometimes(ProblematicCondition())
                    
                    # Should print error messages
                    calls = [call.args[0] for call in mock_print.call_args_list]
                    assert any("Sometimes got confused:" in call for call in calls)
                    assert any("Boolean conversion failed" in call for call in calls)
                    assert any("Flipping a coin instead" in call for call in calls)
                    
                    # Should call random.choice as fallback
                    mock_choice.assert_called_once_with([True, False])
                    assert result is False  # from our mock


class TestSortaPrintErrorHandling:
    """Test sorta_print error handling - covers lines 120-122"""
    
    def test_sorta_print_exception_during_printing(self):
        """Test sorta_print when an exception occurs during printing"""
        # Capture printed messages
        printed_messages = []
        
        def mock_print(*args, **kwargs):
            message = ' '.join(str(arg) for arg in args)
            printed_messages.append(message)
            # Fail on the specific print pattern to trigger exception handling
            if message.startswith('[print]'):
                raise IOError("Print operation failed")
        
        with patch('builtins.print', side_effect=mock_print):
            # Force the 80% path to trigger the exception  
            with patch('random.random', return_value=0.5):  # < 0.8, should print
                sorta_print("test message")
                
                # Should have captured the error and fallback messages
                output = ' '.join(printed_messages)
                assert "[error] Sorta print kinda broke:" in output
                assert "[fallback] test message" in output
    
    def test_sorta_print_no_args_shrug_response(self):
        """Test sorta_print with no args and shrug response"""
        # Test the path where no args are provided and random choice is to not print
        with patch('random.random', return_value=0.9), \
             patch('kinda.personality.chaos_probability', return_value=0.8):  # random > prob, should not print
            with patch('builtins.print') as mock_print:
                sorta_print()
                
                # Should not print anything when random > personality threshold and no args
                mock_print.assert_not_called()
    
    def test_sorta_print_no_args_with_shrug_message(self):
        """Test sorta_print with no args but shows shrug message"""
        # Test the path where no args are provided and random choice is to print shrug
        with patch('random.random', return_value=0.3), \
             patch('kinda.personality.chaos_probability', return_value=0.8):  # random < prob, should print shrug
            with patch('builtins.print') as mock_print:
                sorta_print()
                
                # Should print shrug message
                mock_print.assert_called_once_with('[shrug] Nothing to print, I guess?')


class TestFuzzyRuntimeIntegration:
    """Test integration and edge cases across fuzzy runtime functions"""
    
    def test_all_functions_handle_extreme_edge_cases(self):
        """Test all functions with extreme edge cases"""
        # Test with None values
        with patch('builtins.print'):
            assert isinstance(fuzzy_assign("var", None), int)
            assert isinstance(kinda_int(None), int) 
            assert isinstance(maybe(None), bool)
            assert isinstance(sometimes(None), bool)
            
            # Should not crash when called
            sorta_print(None)
    
    def test_random_seed_consistency(self):
        """Test that functions work with different random seeds"""
        seeds = [0, 42, 12345, 999999]
        
        for seed in seeds:
            random.seed(seed)
            
            # All functions should work regardless of random state
            with patch('builtins.print'):
                result1 = fuzzy_assign("test", 10)
                result2 = kinda_int(5)
                result3 = maybe(True)
                result4 = sometimes(True)
                
                assert isinstance(result1, int)
                assert isinstance(result2, int)
                assert isinstance(result3, bool)
                assert isinstance(result4, bool)
                
                sorta_print("test")  # Should not crash
    
    def test_functions_with_complex_data_types(self):
        """Test functions with complex data types that might cause issues"""
        complex_inputs = [
            float('inf'),
            float('-inf'),
            [],
            {},
            set(),
            object(),
        ]
        
        with patch('builtins.print'):
            for input_val in complex_inputs:
                # Should handle gracefully without crashing
                result1 = fuzzy_assign("var", input_val)
                result2 = kinda_int(input_val)
                result3 = maybe(input_val) 
                result4 = sometimes(input_val)
                
                assert isinstance(result1, int)
                assert isinstance(result2, int)
                assert isinstance(result3, bool)
                assert isinstance(result4, bool)
                
                sorta_print(input_val)  # Should not crash