"""
Comprehensive tests for ~sorta print parsing robustness improvements.
Tests Task #37 requirements: nested expressions, string literals, and error handling.
"""

import pytest
from kinda.grammar.python.matchers import match_python_construct


class TestSortaPrintWhitespaceRobustness:
    """Test ~sorta print with various whitespace patterns"""

    def test_multiple_spaces_between_sorta_and_print(self):
        """Test ~sorta print with multiple spaces"""
        line = '~sorta  print("hello")'
        construct_type, groups = match_python_construct(line)
        
        assert construct_type == "sorta_print"
        assert groups[0] == '"hello"'

    def test_leading_whitespace(self):
        """Test ~sorta print with leading whitespace"""
        line = '   ~sorta print("hello")'
        construct_type, groups = match_python_construct(line)
        
        assert construct_type == "sorta_print"
        assert groups[0] == '"hello"'

    def test_spaces_around_parentheses(self):
        """Test ~sorta print with spaces around parentheses"""
        line = '~sorta print ( "hello" )'
        construct_type, groups = match_python_construct(line)
        
        assert construct_type == "sorta_print"
        assert groups[0] == ' "hello" '


class TestSortaPrintStringLiterals:
    """Test ~sorta print with complex string literals"""

    def test_string_with_parentheses(self):
        """Test strings containing parentheses"""
        line = '~sorta print("text (with parens)", "more (nested) text")'
        construct_type, groups = match_python_construct(line)
        
        assert construct_type == "sorta_print"
        assert groups[0] == '"text (with parens)", "more (nested) text"'

    def test_single_quoted_strings(self):
        """Test single-quoted strings"""
        line = "~sorta print('single quotes', 'with (parens)')"
        construct_type, groups = match_python_construct(line)
        
        assert construct_type == "sorta_print"
        assert groups[0] == "'single quotes', 'with (parens)'"

    def test_mixed_quote_types(self):
        """Test mixed single and double quotes"""
        line = '''~sorta print("double", 'single', "with (parens)")'''
        construct_type, groups = match_python_construct(line)
        
        assert construct_type == "sorta_print"
        assert groups[0] == '''"double", 'single', "with (parens)"'''

    def test_escaped_quotes(self):
        """Test strings with escaped quotes - simpler case"""
        line = r'~sorta print("escaped \"quote\"")'
        construct_type, groups = match_python_construct(line)
        
        assert construct_type == "sorta_print"
        assert groups[0] == r'"escaped \"quote\""'


class TestSortaPrintNestedExpressions:
    """Test ~sorta print with complex nested expressions"""

    def test_nested_function_calls(self):
        """Test nested function calls"""
        line = '~sorta print(func(a, b), other_func(1, 2, 3))'
        construct_type, groups = match_python_construct(line)
        
        assert construct_type == "sorta_print"
        assert groups[0] == "func(a, b), other_func(1, 2, 3)"

    def test_deeply_nested_functions(self):
        """Test deeply nested function calls"""
        line = '~sorta print(outer(middle(inner(x, y)), z))'
        construct_type, groups = match_python_construct(line)
        
        assert construct_type == "sorta_print"
        assert groups[0] == "outer(middle(inner(x, y)), z)"

    def test_list_and_dict_literals(self):
        """Test list and dictionary literals"""
        line = '~sorta print([1, 2, 3], {"key": "value"}, (a, b, c))'
        construct_type, groups = match_python_construct(line)
        
        assert construct_type == "sorta_print"
        assert groups[0] == '[1, 2, 3], {"key": "value"}, (a, b, c)'

    def test_complex_expressions(self):
        """Test complex Python expressions"""
        test_cases = [
            '~sorta print(x if y else z)',
            '~sorta print([i for i in range(10)])',
            '~sorta print(lambda x: x + 1)',
            '~sorta print({"key": value for key, value in items})'
        ]
        
        for line in test_cases:
            construct_type, groups = match_python_construct(line)
            assert construct_type == "sorta_print", f"Failed for: {line}"
            assert groups is not None


class TestSortaPrintErrorHandling:
    """Test graceful handling of malformed input"""

    def test_unclosed_parentheses(self):
        """Test handling of unclosed parentheses"""
        line = '~sorta print("hello"'
        construct_type, groups = match_python_construct(line)
        
        # Should still parse and return partial content
        assert construct_type == "sorta_print"
        assert groups[0] == '"hello"'

    def test_unclosed_string(self):
        """Test handling of unclosed strings"""
        line = '~sorta print("unclosed string'
        construct_type, groups = match_python_construct(line)
        
        # Should still parse and return partial content
        assert construct_type == "sorta_print"
        assert groups[0] == '"unclosed string'

    def test_empty_arguments(self):
        """Test empty arguments"""
        line = '~sorta print()'
        construct_type, groups = match_python_construct(line)
        
        assert construct_type == "sorta_print"
        assert groups[0] == ""

    def test_malformed_construct_name(self):
        """Test malformed construct names"""
        malformed_lines = [
            "~sorta_print('wrong syntax')",
            "~sortaprint('no space')",
            "~sorta  print_extra('too much')"
        ]
        
        for line in malformed_lines:
            construct_type, groups = match_python_construct(line)
            # Should not match sorta_print
            assert construct_type != "sorta_print" or construct_type is None


class TestSortaPrintPerformance:
    """Test parsing performance with complex input"""

    def test_very_long_line(self):
        """Test parsing performance with very long lines"""
        # Create a line with many nested function calls
        nested_calls = "func(" * 50 + "x" + ")" * 50
        line = f'~sorta print({nested_calls})'
        
        construct_type, groups = match_python_construct(line)
        
        assert construct_type == "sorta_print"
        assert groups[0] == nested_calls

    def test_many_string_arguments(self):
        """Test parsing many string arguments"""
        args = ', '.join([f'"arg{i}"' for i in range(100)])
        line = f'~sorta print({args})'
        
        construct_type, groups = match_python_construct(line)
        
        assert construct_type == "sorta_print"
        assert groups[0] == args


class TestBackwardCompatibility:
    """Ensure all existing functionality still works"""

    def test_simple_cases_still_work(self):
        """Test that simple existing cases still work"""
        simple_cases = [
            '~sorta print("hello")',
            '~sorta print(x, y, z)',
            '~sorta print(42)',
            '~sorta print("hello", world)'
        ]
        
        for line in simple_cases:
            construct_type, groups = match_python_construct(line)
            assert construct_type == "sorta_print", f"Failed for: {line}"
            assert groups is not None

    def test_edge_cases_from_existing_tests(self):
        """Test edge cases that were in existing test suite"""
        line = '~sorta print(func(a, b), other_func(1, 2, 3))'
        construct_type, groups = match_python_construct(line)
        
        assert construct_type == "sorta_print"
        assert groups[0] == "func(a, b), other_func(1, 2, 3)"