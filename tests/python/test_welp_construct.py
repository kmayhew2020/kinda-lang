#!/usr/bin/env python3

import pytest
from unittest.mock import patch
import tempfile
from pathlib import Path

# Import required functions for welp construct tests
from kinda.grammar.python.matchers import find_welp_constructs
from kinda.langs.python.transformer import transform_line, transform_file

# Import welp_fallback dynamically to handle runtime generation
try:
    from kinda.langs.python.runtime.fuzzy import welp_fallback
except ImportError:
    # Fallback for CI environments where runtime might not be generated yet
    def welp_fallback(primary_expr, fallback_value):
        """Fallback welp_fallback implementation for testing"""
        try:
            if callable(primary_expr):
                result = primary_expr()
            else:
                result = primary_expr
            return result if result is not None else fallback_value
        except Exception:
            return fallback_value

# Welp construct tests - now enabled!


class TestWelpMatching:
    """Test pattern matching for ~welp constructs."""
    
    def test_find_welp_patterns(self):
        """Test finding ~welp patterns."""
        patterns = find_welp_constructs("result = api_call() ~welp 'default'")
        assert len(patterns) == 1
        assert patterns[0][0] == "welp"  # construct type
        assert patterns[0][1].group() == "api_call() ~welp 'default'"  # matched pattern
        
    def test_find_welp_with_complex_expressions(self):
        """Test finding ~welp patterns with complex expressions."""  
        patterns = find_welp_constructs("value = get_data(url, timeout=10) ~welp None")
        assert len(patterns) == 1
        assert patterns[0][0] == "welp"  # construct type
        assert patterns[0][1].group() == "get_data(url, timeout=10) ~welp None"  # matched pattern
        
    def test_find_welp_with_variables(self):
        """Test finding ~welp patterns with variables."""
        patterns = find_welp_constructs("x = risky_operation ~welp fallback_value")
        assert len(patterns) == 1
        assert patterns[0][0] == "welp"  # construct type
        assert patterns[0][1].group() == "risky_operation ~welp fallback_value"  # matched pattern

    def test_skip_welp_in_strings(self):
        """Test that ~welp inside strings is ignored."""
        patterns = find_welp_constructs('print("Operation ~welp failed")')
        assert len(patterns) == 0  # Should not find any patterns in strings


class TestWelpTransformation:
    """Test transformation of ~welp constructs."""
    
    def test_transform_welp_simple(self):
        """Test transformation of simple ~welp expression."""
        result = transform_line("result = api_call() ~welp 'default'")
        assert isinstance(result, list)
        assert "welp_fallback(lambda: api_call(), 'default')" in result[0]
        
    def test_transform_welp_with_variable(self):
        """Test transformation of ~welp with variable fallback."""
        result = transform_line("data = get_data() ~welp backup_data")
        assert isinstance(result, list)
        assert "welp_fallback(lambda: get_data(), backup_data)" in result[0]
        
    def test_transform_welp_with_complex_expression(self):
        """Test transformation of ~welp with complex primary expression."""
        result = transform_line("value = calculate(x, y, z) * 2 ~welp 0")
        assert isinstance(result, list)
        assert "welp_fallback(lambda: calculate(x, y, z) * 2, 0)" in result[0]
        
    def test_transform_welp_with_function_call_fallback(self):
        """Test transformation of ~welp with function call as fallback."""
        result = transform_line("result = risky_op() ~welp get_default()")
        assert isinstance(result, list)
        assert "welp_fallback(lambda: risky_op(), get_default())" in result[0]


class TestWelpIntegration:
    """Test ~welp construct integration with existing features."""
    
    def test_welp_with_sorta_print(self):
        """Test ~welp working with ~sorta print."""
        result = transform_line("~sorta print(api_call() ~welp 'failed')")
        assert isinstance(result, list)
        # Should transform both ~sorta print AND ~welp
        assert "sorta_print" in result[0]
        assert "welp_fallback(lambda: api_call(), 'failed')" in result[0]
        
    def test_welp_with_ish_constructs(self):
        """Test ~welp with ~ish constructs."""
        result = transform_line("value = get_score() ~welp 50~ish")
        assert isinstance(result, list)
        assert "welp_fallback(lambda: get_score(), ish_value(50))" in result[0]
        
    def test_welp_in_assignment(self):
        """Test ~welp in variable assignments."""
        result = transform_line("score = calculate_score() ~welp 0")
        assert isinstance(result, list)
        assert "score = welp_fallback(lambda: calculate_score(), 0)" in result[0]
        
    def test_welp_in_expressions(self):
        """Test ~welp in complex expressions."""
        result = transform_line("total = (get_value() ~welp 10) + other_value")
        assert isinstance(result, list)
        assert "total = (welp_fallback(lambda: get_value(), 10)) + other_value" in result[0]
        
    def test_welp_with_indentation(self):
        """Test ~welp preserving indentation."""
        result = transform_line("    data = fetch_data() ~welp []")
        assert isinstance(result, list)
        # Should preserve indentation
        assert result[0].startswith("    ")
        assert "welp_fallback(lambda: fetch_data(), [])" in result[0]
        
    def test_welp_inside_strings_not_transformed(self):
        """Test that ~welp inside strings is NOT transformed."""
        result = transform_line('print("The operation ~welp failed")')
        assert isinstance(result, list)
        # The ~welp inside the string should remain literal
        assert "operation ~welp failed" in result[0]
        # Should NOT contain welp_fallback function call
        assert "welp_fallback" not in result[0]
        
    def test_welp_inside_f_strings_not_transformed(self):
        """Test that ~welp inside f-strings is NOT transformed."""
        result = transform_line('print(f"Result: {value} ~welp default")')
        assert isinstance(result, list)
        # The ~welp inside the f-string should remain literal
        assert "~welp default" in result[0]
        # Should NOT contain welp_fallback function call
        assert "welp_fallback" not in result[0]
        
    def test_multiple_welp_constructs(self):
        """Test multiple ~welp constructs on same line."""
        result = transform_line("x = op1() ~welp 'a', y = op2() ~welp 'b'")  
        assert isinstance(result, list)
        assert "welp_fallback(lambda: op1(), 'a')" in result[0]
        assert "welp_fallback(lambda: op2(), 'b')" in result[0]


class TestWelpFileTransformation:
    """Test complete file transformation with ~welp constructs."""
    
    def test_welp_in_simple_file(self):
        """Test file with ~welp constructs."""
        knda_content = """# Test welp construct
data = fetch_api_data() ~welp []
score = calculate() ~welp 0
print(f"Score: {score}")"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.knda', delete=False) as f:
            f.write(knda_content)
            temp_path = Path(f.name)
        
        try:
            result = transform_file(temp_path)
            
            # Check that welp_fallback is imported
            assert "from kinda.langs.python.runtime.fuzzy import" in result
            assert "welp_fallback" in result
            
            # Check proper transformation
            lines = result.split('\n')
            # Find the transformed lines
            transformed_lines = [line for line in lines if not line.startswith('from ')]
            combined = '\n'.join(transformed_lines)
            
            assert "welp_fallback(lambda: fetch_api_data(), [])" in combined
            assert "welp_fallback(lambda: calculate(), 0)" in combined
            assert 'print(f"Score: {score}")' in combined
            
        finally:
            temp_path.unlink()
            
    def test_welp_with_conditional_blocks(self):
        """Test ~welp with conditional constructs."""
        knda_content = """~sometimes():
    data = risky_operation() ~welp None
    if data ~welp False:
        print("Got data!")

result = final_check() ~welp "done\""""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.knda', delete=False) as f:
            f.write(knda_content)
            temp_path = Path(f.name)
        
        try:
            result = transform_file(temp_path)
            
            # Check imports
            assert "welp_fallback" in result
            assert "sometimes" in result
            
            # Check transformations
            lines = result.split('\n')
            combined = '\n'.join(lines)
            
            assert "if sometimes():" in combined
            assert "welp_fallback(lambda: risky_operation(), None)" in combined
            assert "welp_fallback(lambda: data, False)" in combined
            assert "welp_fallback(lambda: final_check(), \"done\")" in combined
            
        finally:
            temp_path.unlink()
            
    def test_welp_with_mixed_constructs(self):
        """Test file with mixed ~welp and other constructs."""
        knda_content = """# Mixed constructs test
~kinda int x ~= get_int() ~welp 42~ish
~sorta print("Value:", x ~welp 0)

~maybe():
    result = complex_calc() ~welp "failed"
    ~sorta print(result)"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.knda', delete=False) as f:
            f.write(knda_content)
            temp_path = Path(f.name)
        
        try:
            result = transform_file(temp_path)
            
            # Check imports - should include multiple helpers
            assert "welp_fallback" in result
            assert "kinda_int" in result
            assert "sorta_print" in result
            assert "ish_value" in result
            assert "maybe" in result
            
            # Check transformations
            lines = result.split('\n')
            combined = '\n'.join(lines)
            
            assert "kinda_int(welp_fallback(lambda: get_int(), ish_value(42)))" in combined
            assert "sorta_print(" in combined
            assert "welp_fallback(lambda: x, 0)" in combined
            assert "if maybe():" in combined
            assert "welp_fallback(lambda: complex_calc(), \"failed\")" in combined
            
        finally:
            temp_path.unlink()


class TestWelpEdgeCases:
    """Test edge cases for ~welp construct."""
    
    def test_welp_with_parentheses(self):
        """Test ~welp with parentheses in expressions."""
        result = transform_line("value = (a + b) ~welp (c + d)")
        assert isinstance(result, list)
        assert "welp_fallback(lambda: (a + b), (c + d))" in result[0]
        
    def test_welp_with_nested_function_calls(self):
        """Test ~welp with nested function calls."""
        result = transform_line("data = get_data(parse_url(config['url'])) ~welp get_default()")
        assert isinstance(result, list)
        assert "welp_fallback(lambda: get_data(parse_url(config['url'])), get_default())" in result[0]
        
    def test_welp_with_list_comprehension(self):
        """Test ~welp with list comprehensions."""
        result = transform_line("items = [process(x) for x in data] ~welp []")
        assert isinstance(result, list)
        assert "welp_fallback(lambda: [process(x) for x in data], [])" in result[0]
        
    def test_welp_with_dictionary_access(self):
        """Test ~welp with dictionary access."""
        result = transform_line("val = config['key']['subkey'] ~welp 'default'")
        assert isinstance(result, list)
        assert "welp_fallback(lambda: config['key']['subkey'], 'default')" in result[0]