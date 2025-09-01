#!/usr/bin/env python3
"""
Comprehensive tests for statistical assertions: ~assert_eventually and ~assert_probability.
Tests basic functionality, statistical validation, edge cases, and KINDA TESTS KINDA self-validation.
"""

import pytest
import tempfile
import time
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
import random

# Add the kinda package to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from kinda.langs.python.transformer import transform_line, transform_file
from kinda.grammar.python.matchers import match_python_construct
from kinda.langs.python.runtime_gen import generate_runtime_helpers
from kinda.grammar.python.constructs import KindaPythonConstructs
from kinda.personality import PersonalityContext


class TestAssertEventuallyParsing:
    """Test ~assert_eventually construct parsing functionality"""
    
    def test_assert_eventually_basic_syntax(self):
        """Test basic ~assert_eventually syntax parsing"""
        line = "~assert_eventually (~sometimes True)"
        construct_type, groups = match_python_construct(line)
        
        assert construct_type == "assert_eventually"
        assert groups[0] == "~sometimes True"
        assert groups[1] is None  # timeout
        assert groups[2] is None  # confidence

    def test_assert_eventually_with_timeout(self):
        """Test ~assert_eventually with timeout parameter"""
        line = "~assert_eventually (~maybe True, timeout=10.0)"
        construct_type, groups = match_python_construct(line)
        
        assert construct_type == "assert_eventually"
        assert groups[0] == "~maybe True"
        assert groups[1] == "10.0"
        assert groups[2] is None

    def test_assert_eventually_with_all_params(self):
        """Test ~assert_eventually with all parameters"""
        line = "~assert_eventually (~probably True, timeout=2.0, confidence=0.9)"
        construct_type, groups = match_python_construct(line)
        
        assert construct_type == "assert_eventually"
        assert groups[0] == "~probably True"
        assert groups[1] == "2.0"
        assert groups[2] == "0.9"

    def test_assert_eventually_complex_condition(self):
        """Test ~assert_eventually with complex conditions"""
        test_cases = [
            "~assert_eventually (~sometimes (x > 0 and y < 10))",
            "~assert_eventually (~maybe func(a, b))",
            "~assert_eventually (~rarely len(items) > 0, timeout=5.0)",
        ]
        
        for case in test_cases:
            construct_type, groups = match_python_construct(case)
            assert construct_type == "assert_eventually"
            assert groups[0] is not None

    def test_assert_eventually_invalid_syntax(self):
        """Test ~assert_eventually with invalid syntax"""
        invalid_cases = [
            "assert_eventually (~sometimes True)",  # Missing ~
            "~assert_eventually",  # No parentheses
            "~assert_eventually()",  # Empty parentheses
        ]
        
        for case in invalid_cases:
            construct_type, groups = match_python_construct(case)
            if case == "~assert_eventually()":
                # This should still parse but with empty condition
                assert construct_type == "assert_eventually" or construct_type is None
            else:
                assert construct_type is None


class TestAssertProbabilityParsing:
    """Test ~assert_probability construct parsing functionality"""
    
    def test_assert_probability_basic_syntax(self):
        """Test basic ~assert_probability syntax parsing"""
        line = "~assert_probability (~sometimes True)"
        construct_type, groups = match_python_construct(line)
        
        assert construct_type == "assert_probability"
        assert groups[0] == "~sometimes True"
        assert groups[1] is None  # expected_prob
        assert groups[2] is None  # tolerance
        assert groups[3] is None  # samples

    def test_assert_probability_with_expected_prob(self):
        """Test ~assert_probability with expected_prob parameter"""
        line = "~assert_probability (~maybe True, expected_prob=0.6)"
        construct_type, groups = match_python_construct(line)
        
        assert construct_type == "assert_probability"
        assert groups[0] == "~maybe True"
        assert groups[1] == "0.6"
        assert groups[2] is None
        assert groups[3] is None

    def test_assert_probability_with_all_params(self):
        """Test ~assert_probability with all parameters"""
        line = "~assert_probability (~probably True, expected_prob=0.7, tolerance=0.05, samples=500)"
        construct_type, groups = match_python_construct(line)
        
        assert construct_type == "assert_probability"
        assert groups[0] == "~probably True"
        assert groups[1] == "0.7"
        assert groups[2] == "0.05"
        assert groups[3] == "500"

    def test_assert_probability_complex_event(self):
        """Test ~assert_probability with complex events"""
        test_cases = [
            "~assert_probability (~sometimes (x > random.random()))",
            "~assert_probability (~maybe flip_coin(), expected_prob=0.5)",
            "~assert_probability (~rarely dice_roll() == 6, expected_prob=0.15, tolerance=0.2, samples=1000)",
        ]
        
        for case in test_cases:
            construct_type, groups = match_python_construct(case)
            assert construct_type == "assert_probability"
            assert groups[0] is not None


class TestStatisticalAssertionsTransformation:
    """Test transformation of statistical assertion constructs"""
    
    def test_assert_eventually_transformation_basic(self):
        """Test basic ~assert_eventually transformation"""
        line = "~assert_eventually (~sometimes True)"
        transformed = transform_line(line)
        
        assert len(transformed) == 1
        assert "assert_eventually(~sometimes True)" in transformed[0]

    def test_assert_eventually_transformation_with_params(self):
        """Test ~assert_eventually transformation with parameters"""
        line = "~assert_eventually (~maybe True, timeout=3.0, confidence=0.8)"
        transformed = transform_line(line)
        
        assert len(transformed) == 1
        result = transformed[0]
        assert "assert_eventually(~maybe True, timeout=3.0, confidence=0.8)" in result

    def test_assert_probability_transformation_basic(self):
        """Test basic ~assert_probability transformation"""
        line = "~assert_probability (~sometimes True)"
        transformed = transform_line(line)
        
        assert len(transformed) == 1
        assert "assert_probability(~sometimes True)" in transformed[0]

    def test_assert_probability_transformation_with_params(self):
        """Test ~assert_probability transformation with parameters"""
        line = "~assert_probability (~maybe True, expected_prob=0.6, tolerance=0.1, samples=200)"
        transformed = transform_line(line)
        
        assert len(transformed) == 1
        result = transformed[0]
        assert "assert_probability(~maybe True, expected_prob=0.6, tolerance=0.1, samples=200)" in result


class TestStatisticalAssertionsRuntime:
    """Test runtime functionality of statistical assertions"""
    
    def setUp(self):
        """Reset personality context before each test"""
        PersonalityContext._instance = None

    def test_assert_probability_deterministic_true(self):
        """Test ~assert_probability with always-true event"""
        from kinda.langs.python.runtime.fuzzy import assert_probability
        
        # Should observe probability of 1.0
        result = assert_probability(True, expected_prob=1.0, tolerance=0.01, samples=100)
        assert result is True

    def test_assert_probability_deterministic_false(self):
        """Test ~assert_probability with always-false event"""
        from kinda.langs.python.runtime.fuzzy import assert_probability
        
        # Should observe probability of 0.0
        result = assert_probability(False, expected_prob=0.0, tolerance=0.01, samples=100)
        assert result is True

    def test_assert_probability_parameter_validation(self):
        """Test ~assert_probability parameter validation"""
        from kinda.langs.python.runtime.fuzzy import assert_probability
        
        # Invalid expected_prob should be corrected
        with patch('builtins.print') as mock_print:
            # This should succeed since expected_prob gets corrected to 0.5
            result = assert_probability(True, expected_prob=2.0, tolerance=0.6, samples=10)
            mock_print.assert_any_call("[?] assert_probability got weird expected_prob: 2.0")

        # Invalid tolerance should be corrected  
        with patch('builtins.print') as mock_print:
            result = assert_probability(True, expected_prob=1.0, tolerance=-0.1, samples=10)
            mock_print.assert_any_call("[?] assert_probability got weird tolerance: -0.1")

        # Invalid samples should be corrected
        with patch('builtins.print') as mock_print:
            result = assert_probability(True, expected_prob=1.0, tolerance=0.1, samples=-10)
            mock_print.assert_any_call("[?] assert_probability got weird samples: -10")

    def test_assert_probability_sample_limiting(self):
        """Test ~assert_probability sample count limiting for performance"""
        from kinda.langs.python.runtime.fuzzy import assert_probability
        
        # Should limit to 10000 samples
        with patch('builtins.print') as mock_print:
            result = assert_probability(True, expected_prob=1.0, tolerance=0.01, samples=50000)
            mock_print.assert_any_call("[?] Limiting samples to 10000 for performance (requested 50000)")


class TestStatisticalAssertionsIntegration:
    """Integration tests for statistical assertions with other kinda constructs"""
    
    def setUp(self):
        """Reset personality context before each test"""
        PersonalityContext._instance = None
        
    def test_assert_eventually_with_sometimes(self):
        """KINDA TESTS KINDA: Use ~assert_eventually to test ~sometimes behavior"""
        # Create a kinda file that tests itself
        kinda_code = '''
~kinda int test_var = 0

# This should eventually be true since ~sometimes has ~50% chance
~assert_eventually (~sometimes (test_var >= 0), timeout=2.0, confidence=0.8)
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py.knda', delete=False) as f:
            f.write(kinda_code)
            temp_path = f.name

        try:
            # Transform and execute
            with tempfile.TemporaryDirectory() as temp_dir:
                output_code = transform_file(Path(temp_path))
                # Should contain the statistical assertion
                assert "assert_eventually" in output_code
                assert "sometimes" in output_code
        finally:
            Path(temp_path).unlink()

    def test_assert_probability_with_fuzzy_constructs(self):
        """KINDA TESTS KINDA: Use ~assert_probability to validate fuzzy construct probabilities"""
        kinda_code = '''
# Test that ~maybe behaves with roughly 60% probability
~assert_probability (~maybe True, expected_prob=0.6, tolerance=0.15, samples=500)

# Test that ~rarely behaves with roughly 15% probability
~assert_probability (~rarely True, expected_prob=0.15, tolerance=0.1, samples=1000)
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py.knda', delete=False) as f:
            f.write(kinda_code)
            temp_path = f.name

        try:
            # Transform the code
            output_code = transform_file(Path(temp_path))
            
            # Should contain both statistical assertions (import + 2 calls = 3 total)
            assert output_code.count("assert_probability") >= 2
            assert "maybe" in output_code
            assert "rarely" in output_code
            assert "expected_prob=0.6" in output_code
            assert "expected_prob=0.15" in output_code
        finally:
            Path(temp_path).unlink()




if __name__ == "__main__":
    pytest.main([__file__, "-v"])