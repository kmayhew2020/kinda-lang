"""
Tests for Python AST Analyzer

This module tests the AST analysis capabilities for identifying
injection opportunities in Python code.
"""

import ast
import pytest
from pathlib import Path

from kinda.injection.ast_analyzer import (
    PythonASTAnalyzer,
    InjectionPoint,
    PatternType,
    SecurityLevel,
    CodeLocation,
    ValidationResult,
    InjectionVisitor,
    ComplexityChecker
)


class TestPythonASTAnalyzer:
    """Test the main AST analyzer"""

    def setup_method(self):
        """Set up test fixtures"""
        self.analyzer = PythonASTAnalyzer()

    def test_parse_source_simple_code(self):
        """Test parsing simple Python source code"""
        source = """
x = 42
print("Hello")
"""
        tree = self.analyzer.parse_source(source)
        assert isinstance(tree, ast.AST)

    def test_parse_source_syntax_error(self):
        """Test handling of syntax errors"""
        source = "x = 42 +"  # Incomplete expression
        with pytest.raises(ValueError, match="Syntax error"):
            self.analyzer.parse_source(source)

    def test_find_injection_points_integer_assignment(self):
        """Test detection of integer assignment patterns"""
        source = """
x = 42
y = 3.14
z = "hello"
"""
        tree = self.analyzer.parse_source(source)
        points = self.analyzer.find_injection_points(tree)

        # Should find kinda_int and kinda_float opportunities
        pattern_types = [point.pattern_type for point in points]
        assert PatternType.KINDA_INT in pattern_types
        assert PatternType.KINDA_FLOAT in pattern_types

        # Should not find string patterns
        assert all(p.pattern_type != PatternType.SORTA_PRINT for p in points)

    def test_find_injection_points_print_statements(self):
        """Test detection of print statement patterns"""
        source = """
print("Hello world")
print(f"Value: {x}")
"""
        tree = self.analyzer.parse_source(source)
        points = self.analyzer.find_injection_points(tree)

        # Should find sorta_print opportunities
        pattern_types = [point.pattern_type for point in points]
        assert PatternType.SORTA_PRINT in pattern_types

        # Check that we found 2 print statements
        print_points = [p for p in points if p.pattern_type == PatternType.SORTA_PRINT]
        assert len(print_points) == 2

    def test_find_injection_points_if_statements(self):
        """Test detection of if statement patterns"""
        source = """
if x > 0:
    print("positive")

if condition:
    do_something()
"""
        tree = self.analyzer.parse_source(source)
        points = self.analyzer.find_injection_points(tree)

        # Should find sometimes opportunities
        pattern_types = [point.pattern_type for point in points]
        assert PatternType.SOMETIMES in pattern_types

    def test_find_injection_points_for_loops(self):
        """Test detection of for loop patterns"""
        source = """
for i in range(10):
    process(i)

for item in items:
    handle(item)
"""
        tree = self.analyzer.parse_source(source)
        points = self.analyzer.find_injection_points(tree)

        # Should find kinda_repeat opportunities for range loops
        pattern_types = [point.pattern_type for point in points]
        assert PatternType.KINDA_REPEAT in pattern_types

        # Should only find one kinda_repeat (the range loop)
        repeat_points = [p for p in points if p.pattern_type == PatternType.KINDA_REPEAT]
        assert len(repeat_points) == 1

    def test_validate_syntax_valid_code(self):
        """Test syntax validation for valid code"""
        source = """
def hello():
    return "world"
"""
        tree = self.analyzer.parse_source(source)
        result = self.analyzer.validate_syntax(tree)

        assert result.is_valid
        assert len(result.errors) == 0

    def test_validate_syntax_suggestions(self):
        """Test that validation provides helpful suggestions"""
        source = """
for i in range(5):
    print(f"Item {i}")

if x > 0:
    process(x)
"""
        tree = self.analyzer.parse_source(source)
        result = self.analyzer.validate_syntax(tree)

        assert result.is_valid
        assert len(result.suggestions) > 0

        # Should suggest loop and condition enhancements
        suggestions_text = ' '.join(result.suggestions)
        assert 'loops' in suggestions_text.lower()
        assert 'conditions' in suggestions_text.lower()


class TestInjectionVisitor:
    """Test the AST visitor for injection point detection"""

    def setup_method(self):
        """Set up test fixtures"""
        self.visitor = InjectionVisitor()

    def test_visit_assign_integer(self):
        """Test visiting integer assignments"""
        source = "x = 42"
        tree = ast.parse(source)
        self.visitor.visit(tree)

        points = self.visitor.injection_points
        assert len(points) == 1
        assert points[0].pattern_type == PatternType.KINDA_INT
        assert points[0].safety_level == SecurityLevel.SAFE
        assert points[0].confidence == 0.9

    def test_visit_assign_float(self):
        """Test visiting float assignments"""
        source = "pi = 3.14159"
        tree = ast.parse(source)
        self.visitor.visit(tree)

        points = self.visitor.injection_points
        assert len(points) == 1
        assert points[0].pattern_type == PatternType.KINDA_FLOAT
        assert points[0].context['value'] == 3.14159

    def test_visit_call_print(self):
        """Test visiting print calls"""
        source = 'print("hello")'
        tree = ast.parse(source)
        self.visitor.visit(tree)

        points = self.visitor.injection_points
        assert len(points) == 1
        assert points[0].pattern_type == PatternType.SORTA_PRINT
        assert points[0].context['args'] == 1

    def test_visit_if_simple(self):
        """Test visiting simple if statements"""
        source = """
if x > 0:
    print("positive")
"""
        tree = ast.parse(source)
        self.visitor.visit(tree)

        points = self.visitor.injection_points
        sometimes_points = [p for p in points if p.pattern_type == PatternType.SOMETIMES]
        assert len(sometimes_points) == 1

    def test_visit_for_range(self):
        """Test visiting for loops with range"""
        source = """
for i in range(10):
    process(i)
"""
        tree = ast.parse(source)
        self.visitor.visit(tree)

        points = self.visitor.injection_points
        repeat_points = [p for p in points if p.pattern_type == PatternType.KINDA_REPEAT]
        assert len(repeat_points) == 1
        assert repeat_points[0].context['range_args'] == 1

    def test_visit_assert_statement(self):
        """Test visiting assert statements"""
        source = "assert x > 0"
        tree = ast.parse(source)
        self.visitor.visit(tree)

        points = self.visitor.injection_points
        assert_points = [p for p in points if p.pattern_type == PatternType.ASSERT_PROBABILITY]
        assert len(assert_points) == 1


class TestComplexityChecker:
    """Test the complexity analysis visitor"""

    def test_simple_function(self):
        """Test complexity analysis of simple function"""
        source = """
def hello():
    return "world"
"""
        tree = ast.parse(source)
        checker = ComplexityChecker()
        checker.visit(tree)

        assert not checker.has_complex_decorators
        assert not checker.has_metaclasses
        assert checker.max_nested_depth == 1

    def test_complex_decorators(self):
        """Test detection of complex decorators"""
        source = """
@decorator1
@decorator2
@decorator3
def complex_function():
    pass
"""
        tree = ast.parse(source)
        checker = ComplexityChecker()
        checker.visit(tree)

        assert checker.has_complex_decorators

    def test_metaclass_detection(self):
        """Test detection of metaclasses"""
        source = """
class MyClass(metaclass=MyMeta):
    pass
"""
        tree = ast.parse(source)
        checker = ComplexityChecker()
        checker.visit(tree)

        assert checker.has_metaclasses

    def test_nested_depth_calculation(self):
        """Test nested depth calculation"""
        source = """
def outer():
    def inner():
        for i in range(10):
            if i > 5:
                pass
"""
        tree = ast.parse(source)
        checker = ComplexityChecker()
        checker.visit(tree)

        assert checker.max_nested_depth >= 4

    def test_simple_loop_counting(self):
        """Test counting of simple loops"""
        source = """
for i in range(10):
    pass

for j in range(5):
    pass

for item in items:
    pass
"""
        tree = ast.parse(source)
        checker = ComplexityChecker()
        checker.visit(tree)

        assert checker.simple_loops == 2  # Only range loops count

    def test_simple_condition_counting(self):
        """Test counting of simple conditions"""
        source = """
if x > 0:
    pass

if condition:
    pass

if complex_function() and other_condition():
    pass
"""
        tree = ast.parse(source)
        checker = ComplexityChecker()
        checker.visit(tree)

        assert checker.simple_conditions >= 2


class TestCodeLocation:
    """Test the CodeLocation dataclass"""

    def test_single_line_location(self):
        """Test single line location"""
        loc = CodeLocation(line=42, column=10)
        assert str(loc) == "line 42, col 10"

    def test_multi_line_location(self):
        """Test multi-line location"""
        loc = CodeLocation(line=42, column=10, end_line=44, end_column=20)
        assert str(loc) == "line 42-44, col 10-20"


class TestInjectionPoint:
    """Test the InjectionPoint dataclass"""

    def test_injection_point_string_representation(self):
        """Test string representation of injection point"""
        location = CodeLocation(line=42, column=10)
        point = InjectionPoint(
            location=location,
            pattern_type=PatternType.KINDA_INT,
            safety_level=SecurityLevel.SAFE,
            confidence=0.9,
            node=ast.Assign(),
            context={}
        )

        str_repr = str(point)
        assert "kinda_int" in str_repr
        assert "line 42" in str_repr
        assert "0.90" in str_repr