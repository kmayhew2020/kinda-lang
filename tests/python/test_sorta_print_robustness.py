"""
Comprehensive tests for ~sorta print parsing robustness improvements.

Tests specific edge cases and malformed inputs to ensure the parser
handles them gracefully and robustly.
"""

import pytest
from kinda.grammar.python.matchers import match_python_construct
from kinda.langs.python.transformer import transform_line


class TestSortaPrintParsingRobustness:
    """Test improved robustness of sorta print parsing"""

    def test_whitespace_variations_comprehensive(self):
        """Test comprehensive whitespace handling"""
        test_cases = [
            # Basic variations
            ('~sorta print("hello")', True, '"hello"'),
            ('~sorta  print("hello")', True, '"hello"'),  # double space
            ('~sorta   print("hello")', True, '"hello"'),  # triple space
            ('~sorta\tprint("hello")', True, '"hello"'),  # tab
            ('~sorta \t print("hello")', True, '"hello"'),  # mixed space/tab
            
            # Leading/trailing whitespace
            ('   ~sorta print("hello")', True, '"hello"'),
            ('~sorta print("hello")   ', True, '"hello"'),
            ('\t~sorta print("hello")\t', True, '"hello"'),
            
            # Spaces around parentheses
            ('~sorta print ( "hello" )', True, ' "hello" '),
            ('~sorta print(  "hello"  )', True, '  "hello"  '),
            ('~sorta print\t(\t"hello"\t)', True, '\t"hello"\t'),
        ]
        
        for line, should_match, expected_content in test_cases:
            construct_type, groups = match_python_construct(line)
            
            if should_match:
                assert construct_type == "sorta_print", f"Failed to match: {repr(line)}"
                assert groups[0] == expected_content, f"Wrong content for {repr(line)}: got {repr(groups[0])}, expected {repr(expected_content)}"
            else:
                assert construct_type != "sorta_print", f"Should not match: {repr(line)}"

    def test_string_literal_edge_cases(self):
        """Test complex string literal scenarios"""
        test_cases = [
            # Escaped quotes
            ('~sorta print("escaped \\"quote\\"")', True, '"escaped \\"quote\\""'),
            ("~sorta print('escaped \\'quote\\'')", True, "'escaped \\'quote\\''"),
            
            # Mixed quotes
            ('~sorta print("mix \'quotes\'")', True, '"mix \'quotes\'"'),
            ("~sorta print('mix \"quotes\"')", True, "'mix \"quotes\"'"),
            
            # Parentheses in strings
            ('~sorta print("text (with parens)")', True, '"text (with parens)"'),
            ('~sorta print("nested ((parens))")', True, '"nested ((parens))"'),
            
            # Special characters
            ('~sorta print("unicode: 🎲 🤷 ✨")', True, '"unicode: 🎲 🤷 ✨"'),
            ('~sorta print("newline\\ncharacter")', True, '"newline\\ncharacter"'),
            ('~sorta print("tab\\tcharacter")', True, '"tab\\tcharacter"'),
        ]
        
        for line, should_match, expected_content in test_cases:
            construct_type, groups = match_python_construct(line)
            
            if should_match:
                assert construct_type == "sorta_print", f"Failed to match: {repr(line)}"
                assert groups[0] == expected_content, f"Wrong content for {repr(line)}: got {repr(groups[0])}, expected {repr(expected_content)}"
            else:
                assert construct_type != "sorta_print", f"Should not match: {repr(line)}"

    def test_nested_parentheses_robustness(self):
        """Test complex nested parentheses scenarios"""
        test_cases = [
            # Function calls with parens
            ('~sorta print(func(a, b))', True, 'func(a, b)'),
            ('~sorta print(func(other(1, 2), 3))', True, 'func(other(1, 2), 3)'),
            
            # Lists and tuples
            ('~sorta print([1, 2, 3])', True, '[1, 2, 3]'),
            ('~sorta print((a, b, c))', True, '(a, b, c)'),
            
            # Complex expressions
            ('~sorta print((a + b) * (c - d))', True, '(a + b) * (c - d)'),
            ('~sorta print({"key": func(x)})', True, '{"key": func(x)}'),
            
            # Deep nesting
            ('~sorta print(func(sub(deep(nest()))))', True, 'func(sub(deep(nest())))'),
        ]
        
        for line, should_match, expected_content in test_cases:
            construct_type, groups = match_python_construct(line)
            
            if should_match:
                assert construct_type == "sorta_print", f"Failed to match: {repr(line)}"
                assert groups[0] == expected_content, f"Wrong content for {repr(line)}: got {repr(groups[0])}, expected {repr(expected_content)}"

    def test_malformed_input_graceful_handling(self):
        """Test graceful handling of malformed inputs"""
        malformed_cases = [
            # Missing parentheses
            ('~sorta print', False),
            ('~sorta print)', False),
            ('~sorta print hello', False),
            
            # Invalid syntax
            ('~sortaprint("hello")', False),  # No space after tilde
            ('~~sorta print("hello")', False),  # Double tilde
            ('~sorta print print("hello")', False),  # Double print
            
            # Unclosed parentheses - these should not match
            ('~sorta print(unclosed', False),
            ('~sorta print(a, b,', False),
        ]
        
        for line, should_match in malformed_cases:
            construct_type, groups = match_python_construct(line)
            
            if should_match:
                assert construct_type == "sorta_print", f"Should match gracefully: {repr(line)}"
                assert groups is not None, f"Should have content: {repr(line)}"
            else:
                assert construct_type != "sorta_print", f"Should not match: {repr(line)}"
    
    def test_unclosed_string_graceful_handling(self):
        """Test graceful handling of unclosed strings"""
        unclosed_string_cases = [
            # Unclosed strings - these should still parse for better error handling
            ('~sorta print("unclosed', True, '"unclosed'),
            ("~sorta print('unclosed", True, "'unclosed"),
            ('~sorta print("partially closed", "unclosed', True, '"partially closed", "unclosed'),
        ]
        
        for line, should_match, expected_content in unclosed_string_cases:
            construct_type, groups = match_python_construct(line)
            
            if should_match:
                assert construct_type == "sorta_print", f"Should match gracefully: {repr(line)}"
                assert groups is not None and groups[0] == expected_content, f"Should have expected content: {repr(line)}"

    def test_complex_python_expressions(self):
        """Test with complex Python expressions as arguments"""
        test_cases = [
            # Comprehensions
            ('~sorta print([i for i in range(10)])', True),
            ('~sorta print({k: v for k, v in items.items()})', True),
            ('~sorta print((x for x in data if x > 0))', True),
            
            # Lambda expressions
            ('~sorta print(lambda x: x * 2)', True),
            ('~sorta print(lambda: "hello")', True),
            ('~sorta print(map(lambda x: x + 1, data))', True),
            
            # Conditional expressions
            ('~sorta print(a if condition else b)', True),
            ('~sorta print("positive" if x > 0 else "negative")', True),
            
            # Multiple complex arguments
            ('~sorta print(func(a, b), [1, 2, 3], {"key": value})', True),
        ]
        
        for line, should_match in test_cases:
            construct_type, groups = match_python_construct(line)
            
            if should_match:
                assert construct_type == "sorta_print", f"Failed to match: {repr(line)}"
                assert groups is not None and groups[0], f"Should have content: {repr(line)}"

    def test_transformation_robustness(self):
        """Test that improved parsing works with transformation"""
        test_cases = [
            '~sorta  print("hello")',  # multiple spaces
            '~sorta print ( "world" )',  # spaces around parens
            '~sorta print("string with (parens)")',  # parens in string
            '~sorta print(func(a, b), "text")',  # complex expression
        ]
        
        for line in test_cases:
            # Should transform without errors
            result = transform_line(line)
            
            assert len(result) == 1, f"Should produce one line: {repr(line)}"
            assert "sorta_print(" in result[0], f"Should contain sorta_print call: {repr(line)}"

    def test_backward_compatibility(self):
        """Test that improvements maintain backward compatibility"""
        # These are the original test cases that should still work
        original_cases = [
            '~sorta print("hello")',
            '~sorta print("hello", "world")',
            '~sorta print(variable)',
            '~sorta print(func(1, 2, 3))',
            '~sorta print()',
        ]
        
        for line in original_cases:
            construct_type, groups = match_python_construct(line)
            assert construct_type == "sorta_print", f"Backward compatibility broken for: {repr(line)}"
            assert groups is not None, f"Should have groups: {repr(line)}"

    def test_performance_with_long_lines(self):
        """Test parser performance with very long lines"""
        # Create a very long sorta print line
        long_args = ", ".join([f'"arg{i}"' for i in range(100)])
        long_line = f"~sorta print({long_args})"
        
        construct_type, groups = match_python_construct(long_line)
        
        assert construct_type == "sorta_print"
        assert groups[0] == long_args
        
        # Should also transform properly
        result = transform_line(long_line)
        assert len(result) == 1
        assert "sorta_print(" in result[0]