"""
Comprehensive tests for the ~kinda bool construct.
Tests basic functionality, edge cases, personality integration, and fuzzy behavior.
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch
import random

from kinda.langs.python.transformer import transform_line, transform_file
from kinda.grammar.python.matchers import match_python_construct
from kinda.langs.python.runtime_gen import generate_runtime_helpers
from kinda.grammar.python.constructs import KindaPythonConstructs
from kinda.personality import PersonalityContext, PERSONALITY_PROFILES


class TestKindaBoolConstructParsing:
    """Test ~kinda bool construct parsing functionality"""

    def test_kinda_bool_basic_syntax(self):
        """Test basic ~kinda bool syntax parsing"""
        test_cases = [
            "~kinda bool flag = True;",
            "~kinda bool status ~= False;",
            "~kinda bool active = 1;",
            "~kinda bool enabled ~= 0;",
        ]
        
        for line in test_cases:
            construct_type, groups = match_python_construct(line)
            assert construct_type == "kinda_bool", f"Failed to parse: {line}"
            assert len(groups) == 2, f"Expected 2 groups, got {len(groups)} for: {line}"

    def test_kinda_bool_variable_names(self):
        """Test various variable naming patterns"""
        test_cases = [
            ("~kinda bool x = True;", "x", "True"),
            ("~kinda bool is_active = False;", "is_active", "False"),  
            ("~kinda bool flag123 ~= 1;", "flag123", "1"),
            ("~kinda bool _private = yes;", "_private", "yes"),
        ]
        
        for line, expected_var, expected_val in test_cases:
            construct_type, groups = match_python_construct(line)
            assert construct_type == "kinda_bool"
            var, val = groups
            assert var == expected_var, f"Expected var '{expected_var}', got '{var}'"
            assert val == expected_val, f"Expected val '{expected_val}', got '{val}'"

    def test_kinda_bool_various_values(self):
        """Test parsing with various boolean-like values"""
        test_cases = [
            "~kinda bool flag = True;",
            "~kinda bool flag = False;",
            "~kinda bool flag = 1;",
            "~kinda bool flag = 0;",
            "~kinda bool flag = 'yes';",
            "~kinda bool flag = 'no';",
            "~kinda bool flag = some_variable;",
            "~kinda bool flag = func_call();",
        ]
        
        for line in test_cases:
            construct_type, groups = match_python_construct(line)
            assert construct_type == "kinda_bool", f"Failed to parse: {line}"

    def test_kinda_bool_with_comments(self):
        """Test ~kinda bool with comments"""
        line = "~kinda bool flag = True; # This is a comment"
        construct_type, groups = match_python_construct(line)
        
        assert construct_type == "kinda_bool"
        var, val = groups
        assert var == "flag"
        assert val == "True"  # Comments should be stripped

    def test_kinda_bool_operators(self):
        """Test both = and ~= operators"""
        test_cases = [
            ("~kinda bool flag = True;", "flag", "True"),
            ("~kinda bool flag ~= True;", "flag", "True"),
            ("~kinda bool flag == True;", "flag", "True"),
            ("~kinda bool flag ~== True;", "flag", "True"),
        ]
        
        for line, expected_var, expected_val in test_cases:
            construct_type, groups = match_python_construct(line)
            assert construct_type == "kinda_bool"
            var, val = groups
            assert var == expected_var
            assert val == expected_val


class TestKindaBoolTransformation:
    """Test ~kinda bool transformation functionality"""

    def test_transform_basic_kinda_bool(self):
        """Test basic transformation of ~kinda bool"""
        line = "~kinda bool flag = True;"
        result = transform_line(line)
        
        assert len(result) == 1
        assert "flag = kinda_bool(True)" in result[0]

    def test_transform_kinda_bool_with_fuzzy_assign(self):
        """Test transformation with fuzzy assignment operator"""
        line = "~kinda bool active ~= False;"
        result = transform_line(line)
        
        assert len(result) == 1
        assert "active = kinda_bool(False)" in result[0]

    def test_transform_kinda_bool_various_values(self):
        """Test transformation with various value types"""
        test_cases = [
            ("~kinda bool flag = 1;", "flag = kinda_bool(1)"),
            ("~kinda bool status = 'yes';", "status = kinda_bool('yes')"),
            ("~kinda bool ready = some_var;", "ready = kinda_bool(some_var)"),
        ]
        
        for input_line, expected_output in test_cases:
            result = transform_line(input_line)
            assert len(result) == 1
            assert expected_output in result[0]

    def test_file_transformation_includes_helpers(self):
        """Test that file transformation includes kinda_bool helper"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.kinda', delete=False) as f:
            f.write("~kinda bool active = True;\n")
            f.write("~sorta print(active);\n")
            temp_file = f.name

        try:
            result = transform_file(temp_file)
            
            # Should import kinda_bool helper
            assert "kinda_bool" in result
            assert "active = kinda_bool(True)" in result
            
        finally:
            Path(temp_file).unlink()


class TestKindaBoolRuntime:
    """Test ~kinda bool runtime behavior"""

    def test_kinda_bool_function_exists(self):
        """Test that kinda_bool function is properly defined"""
        construct_info = KindaPythonConstructs["kinda_bool"]
        assert "def kinda_bool(" in construct_info["body"]

    def test_kinda_bool_with_boolean_values(self):
        """Test kinda_bool function with actual boolean values"""
        # Create namespace and execute function definition
        test_namespace = {}
        exec(KindaPythonConstructs["kinda_bool"]["body"], test_namespace)
        kinda_bool = test_namespace['kinda_bool']
        
        # Test with True
        with patch('random.random', return_value=0.9):  # No uncertainty flip
            with patch('kinda.personality.chaos_bool_uncertainty', return_value=0.1):
                result = kinda_bool(True)
                assert isinstance(result, bool)
        
        # Test with False  
        with patch('random.random', return_value=0.9):  # No uncertainty flip
            with patch('kinda.personality.chaos_bool_uncertainty', return_value=0.1):
                result = kinda_bool(False)
                assert isinstance(result, bool)

    def test_kinda_bool_with_integer_values(self):
        """Test kinda_bool with integer values"""
        test_namespace = {}
        exec(KindaPythonConstructs["kinda_bool"]["body"], test_namespace)
        kinda_bool = test_namespace['kinda_bool']
        
        # Test with 1 (truthy)
        with patch('random.random', return_value=0.9):  # No uncertainty flip
            with patch('kinda.personality.chaos_bool_uncertainty', return_value=0.1):
                result = kinda_bool(1)
                assert result is True
            
        # Test with 0 (falsy)
        with patch('random.random', return_value=0.9):  # No uncertainty flip
            with patch('kinda.personality.chaos_bool_uncertainty', return_value=0.1):
                result = kinda_bool(0)
                assert result is False

    def test_kinda_bool_with_string_values(self):
        """Test kinda_bool with various string values"""
        test_namespace = {}
        exec(KindaPythonConstructs["kinda_bool"]["body"], test_namespace)
        kinda_bool = test_namespace['kinda_bool']
        
        # Test truthy strings
        truthy_strings = ['true', 'TRUE', '1', 'yes', 'YES', 'on', 'y']
        for val in truthy_strings:
            with patch('random.random', return_value=0.9):  # No uncertainty flip
                with patch('kinda.personality.chaos_bool_uncertainty', return_value=0.1):
                    result = kinda_bool(val)
                    assert result is True, f"Expected True for '{val}'"
        
        # Test falsy strings  
        falsy_strings = ['false', 'FALSE', '0', 'no', 'NO', 'off', 'n']
        for val in falsy_strings:
            with patch('random.random', return_value=0.9):  # No uncertainty flip
                with patch('kinda.personality.chaos_bool_uncertainty', return_value=0.1):
                    result = kinda_bool(val)
                    assert result is False, f"Expected False for '{val}'"

    def test_kinda_bool_with_none(self):
        """Test kinda_bool with None value"""
        test_namespace = {}
        exec(KindaPythonConstructs["kinda_bool"]["body"], test_namespace)
        kinda_bool = test_namespace['kinda_bool']
        
        # With None, should return random boolean
        with patch('random.choice', return_value=True):
            with patch('kinda.personality.chaos_bool_uncertainty', return_value=0.1):
                result = kinda_bool(None)
                assert result is True
            
        with patch('random.choice', return_value=False):
            with patch('kinda.personality.chaos_bool_uncertainty', return_value=0.1):
                result = kinda_bool(None)
                assert result is False

    def test_kinda_bool_uncertainty_flip(self):
        """Test uncertainty causing boolean flip"""
        test_namespace = {}
        exec(KindaPythonConstructs["kinda_bool"]["body"], test_namespace)
        kinda_bool = test_namespace['kinda_bool']
        
        # High uncertainty should cause flip
        with patch('random.random', return_value=0.05):  # Triggers uncertainty
            with patch('kinda.personality.chaos_bool_uncertainty', return_value=0.1):
                result = kinda_bool(True)
                assert result is False  # Should be flipped
                
                result = kinda_bool(False)
                assert result is True  # Should be flipped

    def test_kinda_bool_error_handling(self):
        """Test error handling in kinda_bool"""
        test_namespace = {}
        exec(KindaPythonConstructs["kinda_bool"]["body"], test_namespace)
        kinda_bool = test_namespace['kinda_bool']
        
        # Test with problematic value that causes exception
        with patch('kinda.personality.chaos_bool_uncertainty', side_effect=Exception("Test error")):
            with patch('random.choice', return_value=True):
                result = kinda_bool("test")
                assert isinstance(result, bool)


class TestKindaBoolPersonalityIntegration:
    """Test personality system integration"""

    def setUp(self):
        """Set up clean personality state"""
        PersonalityContext._instance = None

    def tearDown(self):
        """Clean up personality state"""
        PersonalityContext._instance = None

    def test_reliable_personality_low_uncertainty(self):
        """Test reliable personality has low boolean uncertainty"""
        PersonalityContext.set_mood("reliable")
        personality = PersonalityContext.get_instance()
        
        uncertainty = personality.get_bool_uncertainty()
        assert uncertainty <= 0.05, f"Reliable personality should have low uncertainty, got {uncertainty}"

    def test_chaotic_personality_high_uncertainty(self):
        """Test chaotic personality has high boolean uncertainty"""
        PersonalityContext.set_mood("chaotic")
        personality = PersonalityContext.get_instance()
        
        uncertainty = personality.get_bool_uncertainty()
        assert uncertainty >= 0.2, f"Chaotic personality should have high uncertainty, got {uncertainty}"

    def test_uncertainty_with_instability(self):
        """Test that instability affects boolean uncertainty"""
        PersonalityContext.set_mood("playful")
        personality = PersonalityContext.get_instance()
        
        # Start with base uncertainty
        base_uncertainty = personality.get_bool_uncertainty()
        
        # Add instability 
        personality.instability_level = 0.5
        unstable_uncertainty = personality.get_bool_uncertainty()
        
        assert unstable_uncertainty > base_uncertainty, "Instability should increase uncertainty"

    def test_personality_profiles_have_bool_uncertainty(self):
        """Test that all personality profiles define bool_uncertainty"""
        for profile_name, profile in PERSONALITY_PROFILES.items():
            assert hasattr(profile, 'bool_uncertainty'), f"Profile '{profile_name}' missing bool_uncertainty"
            assert isinstance(profile.bool_uncertainty, (int, float)), f"Profile '{profile_name}' bool_uncertainty not numeric"
            assert 0.0 <= profile.bool_uncertainty <= 1.0, f"Profile '{profile_name}' bool_uncertainty out of range"


class TestKindaBoolIntegrationWithOtherConstructs:
    """Test integration with other kinda-lang constructs"""

    def test_kinda_bool_with_ish_comparison(self):
        """Test kinda bool works with ~ish comparisons"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.kinda', delete=False) as f:
            f.write("~kinda bool flag = True;\n")
            f.write("result = flag ~ish True;\n")
            temp_file = f.name

        try:
            result = transform_file(temp_file)
            assert "flag = kinda_bool(True)" in result
            assert "ish_comparison(" in result
        finally:
            Path(temp_file).unlink()

    def test_kinda_bool_with_conditional_constructs(self):
        """Test kinda bool with ~sometimes, ~maybe, ~probably"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.kinda', delete=False) as f:
            f.write("~kinda bool active = True;\n")
            f.write("~sometimes (active) {\n")
            f.write("    ~sorta print('active is true');\n")
            f.write("}\n")
            temp_file = f.name

        try:
            result = transform_file(temp_file)
            assert "active = kinda_bool(True)" in result
            assert "if sometimes(active):" in result
        finally:
            Path(temp_file).unlink()

    def test_kinda_bool_with_welp_fallback(self):
        """Test kinda bool with ~welp fallback"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.kinda', delete=False) as f:
            f.write("~kinda bool status = might_fail() ~welp False;\n")
            temp_file = f.name

        try:
            result = transform_file(temp_file)
            assert "kinda_bool(" in result
            assert "welp_fallback(" in result
        finally:
            Path(temp_file).unlink()


class TestKindaBoolEdgeCases:
    """Test edge cases and error scenarios"""

    def test_kinda_bool_with_empty_string(self):
        """Test kinda_bool with empty string"""
        test_namespace = {}
        exec(KindaPythonConstructs["kinda_bool"]["body"], test_namespace)
        kinda_bool = test_namespace['kinda_bool']
        
        # Empty string should be falsy
        with patch('random.random', return_value=0.9):  # No uncertainty flip
            with patch('kinda.personality.chaos_bool_uncertainty', return_value=0.1):
                result = kinda_bool("")
                assert result is False

    def test_kinda_bool_with_whitespace_strings(self):
        """Test kinda_bool with whitespace strings"""
        test_namespace = {}
        exec(KindaPythonConstructs["kinda_bool"]["body"], test_namespace)
        kinda_bool = test_namespace['kinda_bool']
        
        test_cases = [
            (" true ", True),
            (" FALSE ", False), 
            ("  yes  ", True),
            ("   no   ", False),
        ]
        
        for input_val, expected in test_cases:
            with patch('random.random', return_value=0.9):  # No uncertainty flip
                with patch('kinda.personality.chaos_bool_uncertainty', return_value=0.1):
                    result = kinda_bool(input_val)
                    assert result is expected, f"Expected {expected} for '{input_val}'"

    def test_kinda_bool_with_ambiguous_strings(self):
        """Test kinda_bool with ambiguous string values"""
        test_namespace = {}
        exec(KindaPythonConstructs["kinda_bool"]["body"], test_namespace)
        kinda_bool = test_namespace['kinda_bool']
        
        # Non-empty but ambiguous strings should be truthy (like standard Python)
        ambiguous_values = ["maybe", "kinda", "hello", "123abc"]
        
        for val in ambiguous_values:
            with patch('random.random', return_value=0.9):  # No uncertainty flip
                with patch('kinda.personality.chaos_bool_uncertainty', return_value=0.1):
                    result = kinda_bool(val)
                    assert result is True, f"Ambiguous string '{val}' should be truthy"

    def test_kinda_bool_with_numeric_edge_cases(self):
        """Test kinda_bool with edge case numeric values"""
        test_namespace = {}
        exec(KindaPythonConstructs["kinda_bool"]["body"], test_namespace)
        kinda_bool = test_namespace['kinda_bool']
        
        test_cases = [
            (-1, True),    # Negative numbers are truthy
            (0.0, False),  # Zero float is falsy
            (0.1, True),   # Small positive float is truthy
            (-0.1, True),  # Small negative float is truthy
        ]
        
        for input_val, expected in test_cases:
            with patch('random.random', return_value=0.9):  # No uncertainty flip
                with patch('kinda.personality.chaos_bool_uncertainty', return_value=0.1):
                    result = kinda_bool(input_val)
                    assert result is expected, f"Expected {expected} for {input_val}"

    def test_invalid_syntax_patterns(self):
        """Test patterns that should NOT match kinda_bool"""
        invalid_patterns = [
            "~kinda bool;",  # No variable or value
            "~kinda bool flag;",  # No assignment
            "kinda bool flag = True;",  # Missing ~
            "~kinda bool = True;",  # Missing variable name
            "~kinda boolean flag = True;",  # Wrong keyword
        ]
        
        for pattern in invalid_patterns:
            construct_type, groups = match_python_construct(pattern)
            assert construct_type != "kinda_bool", f"Should not match: {pattern}"

    def test_kinda_bool_uncertainty_bounds(self):
        """Test uncertainty is properly bounded"""
        from kinda.personality import PersonalityContext
        
        PersonalityContext._instance = None
        personality = PersonalityContext.get_instance()
        
        # Test maximum bounds
        personality.profile.bool_uncertainty = 2.0  # Way too high
        personality.profile.chaos_amplifier = 2.0
        uncertainty = personality.get_bool_uncertainty()
        assert uncertainty <= 0.5, f"Uncertainty should be capped at 0.5, got {uncertainty}"
        
        # Test minimum bounds
        personality.profile.bool_uncertainty = -0.5  # Negative
        uncertainty = personality.get_bool_uncertainty()
        assert uncertainty >= 0.0, f"Uncertainty should be non-negative, got {uncertainty}"


if __name__ == "__main__":
    pytest.main([__file__])