"""
Python AST Analysis Engine for Kinda-Lang Injection

This module provides comprehensive AST analysis capabilities for identifying
injection opportunities in Python code.
"""

import ast
import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import List, Optional, Dict, Any, Union

from ..security import secure_condition_check, is_condition_dangerous


class PatternType(Enum):
    """Types of injection patterns available"""
    KINDA_INT = "kinda_int"
    KINDA_FLOAT = "kinda_float"
    SORTA_PRINT = "sorta_print"
    SOMETIMES = "sometimes"
    MAYBE = "maybe"
    PROBABLY = "probably"
    RARELY = "rarely"
    KINDA_REPEAT = "kinda_repeat"
    MAYBE_FOR = "maybe_for"
    WELP = "welp"
    ASSERT_PROBABILITY = "assert_probability"


class SecurityLevel(Enum):
    """Security risk levels for injection operations"""
    SAFE = "safe"
    CAUTION = "caution"
    RISKY = "risky"
    DANGEROUS = "dangerous"


@dataclass
class CodeLocation:
    """Represents a location in source code"""
    line: int
    column: int
    end_line: Optional[int] = None
    end_column: Optional[int] = None

    def __str__(self) -> str:
        if self.end_line is not None:
            return f"line {self.line}-{self.end_line}, col {self.column}-{self.end_column}"
        return f"line {self.line}, col {self.column}"


@dataclass
class InjectionPoint:
    """Represents an injection opportunity in the code"""
    location: CodeLocation
    pattern_type: PatternType
    safety_level: SecurityLevel
    confidence: float
    node: ast.AST
    context: Dict[str, Any]

    def __str__(self) -> str:
        return f"{self.pattern_type.value} at {self.location} (confidence: {self.confidence:.2f})"


@dataclass
class ValidationResult:
    """Result of AST validation for injection compatibility"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    suggestions: List[str]


class InjectionVisitor(ast.NodeVisitor):
    """AST visitor to identify injection opportunities"""

    def __init__(self):
        self.injection_points: List[InjectionPoint] = []
        self.current_scope = []

    def visit_Assign(self, node: ast.Assign) -> None:
        """Visit assignment nodes to find variable injection opportunities"""
        for target in node.targets:
            if isinstance(target, ast.Name):
                # Check for integer assignments
                if isinstance(node.value, ast.Constant) and isinstance(node.value.value, int):
                    self._add_injection_point(
                        node, PatternType.KINDA_INT, SecurityLevel.SAFE, 0.9,
                        {"variable_name": target.id, "value": node.value.value}
                    )

                # Check for float assignments
                elif isinstance(node.value, ast.Constant) and isinstance(node.value.value, float):
                    self._add_injection_point(
                        node, PatternType.KINDA_FLOAT, SecurityLevel.SAFE, 0.9,
                        {"variable_name": target.id, "value": node.value.value}
                    )

        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        """Visit function calls to find print and other injection opportunities"""
        # Check for print statements
        if (isinstance(node.func, ast.Name) and node.func.id == 'print'):
            self._add_injection_point(
                node, PatternType.SORTA_PRINT, SecurityLevel.SAFE, 0.8,
                {"args": len(node.args), "has_kwargs": bool(node.keywords)}
            )

        self.generic_visit(node)

    def visit_If(self, node: ast.If) -> None:
        """Visit if statements for conditional injection opportunities"""
        # Check for simple conditions that could use sometimes/maybe
        if self._is_simple_condition(node.test):
            confidence = 0.7 if self._has_side_effects(node.body) else 0.9
            safety = SecurityLevel.CAUTION if self._has_side_effects(node.body) else SecurityLevel.SAFE

            self._add_injection_point(
                node, PatternType.SOMETIMES, safety, confidence,
                {"condition_type": type(node.test).__name__, "has_else": bool(node.orelse)}
            )

        self.generic_visit(node)

    def visit_For(self, node: ast.For) -> None:
        """Visit for loops for loop injection opportunities"""
        if isinstance(node.iter, ast.Call) and isinstance(node.iter.func, ast.Name):
            if node.iter.func.id == 'range':
                self._add_injection_point(
                    node, PatternType.KINDA_REPEAT, SecurityLevel.SAFE, 0.8,
                    {"range_args": len(node.iter.args), "has_else": bool(node.orelse)}
                )

        self.generic_visit(node)

    def visit_Assert(self, node: ast.Assert) -> None:
        """Visit assert statements for probabilistic assertion opportunities"""
        self._add_injection_point(
            node, PatternType.ASSERT_PROBABILITY, SecurityLevel.CAUTION, 0.6,
            {"has_msg": bool(node.msg)}
        )
        self.generic_visit(node)

    def _add_injection_point(self, node: ast.AST, pattern_type: PatternType,
                           safety_level: SecurityLevel, confidence: float,
                           context: Dict[str, Any]) -> None:
        """Add an injection point to the list"""
        location = CodeLocation(
            line=node.lineno,
            column=node.col_offset,
            end_line=getattr(node, 'end_lineno', None),
            end_column=getattr(node, 'end_col_offset', None)
        )

        injection_point = InjectionPoint(
            location=location,
            pattern_type=pattern_type,
            safety_level=safety_level,
            confidence=confidence,
            node=node,
            context=context
        )

        self.injection_points.append(injection_point)

    def _is_simple_condition(self, node: ast.AST) -> bool:
        """Check if a condition is simple enough for probabilistic execution"""
        # Simple conditions: comparisons, boolean operations, name references
        return isinstance(node, (ast.Compare, ast.BoolOp, ast.Name, ast.Constant))

    def _has_side_effects(self, nodes: List[ast.AST]) -> bool:
        """Check if a list of nodes has potential side effects"""
        for node in nodes:
            if isinstance(node, (ast.Call, ast.Assign, ast.AugAssign)):
                return True
        return False


class PythonASTAnalyzer:
    """Core AST analysis for Python injection"""

    def __init__(self):
        pass  # Security functions are now module-level imports

    def parse_file(self, file_path: Path) -> ast.AST:
        """Parse Python file into AST"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
            return ast.parse(source, filename=str(file_path))
        except (IOError, OSError) as e:
            raise ValueError(f"Could not read file {file_path}: {e}")
        except SyntaxError as e:
            raise ValueError(f"Syntax error in {file_path}: {e}")

    def parse_source(self, source: str, filename: str = '<string>') -> ast.AST:
        """Parse Python source code into AST"""
        try:
            return ast.parse(source, filename=filename)
        except SyntaxError as e:
            raise ValueError(f"Syntax error in {filename}: {e}")

    def find_injection_points(self, tree: ast.AST) -> List[InjectionPoint]:
        """Identify opportunities for injection"""
        visitor = InjectionVisitor()
        visitor.visit(tree)

        # Filter based on confidence and safety
        valid_points = []
        for point in visitor.injection_points:
            if point.confidence >= 0.5 and point.safety_level != SecurityLevel.DANGEROUS:
                valid_points.append(point)

        return sorted(valid_points, key=lambda p: p.confidence, reverse=True)

    def validate_syntax(self, tree: ast.AST) -> ValidationResult:
        """Validate AST for injection compatibility"""
        errors = []
        warnings = []
        suggestions = []

        # Basic AST validation
        try:
            # Ensure the tree is compilable
            compile(tree, '<ast>', 'exec')
        except Exception as e:
            errors.append(f"AST compilation failed: {e}")

        # Check for complex constructs that might interfere
        complexity_visitor = ComplexityChecker()
        complexity_visitor.visit(tree)

        if complexity_visitor.has_complex_decorators:
            warnings.append("Complex decorators found - injection may interfere")

        if complexity_visitor.has_metaclasses:
            warnings.append("Metaclasses found - injection may not work as expected")

        if complexity_visitor.nested_depth > 5:
            warnings.append("Deep nesting detected - consider simplifying before injection")

        # Add suggestions based on findings
        if complexity_visitor.simple_loops > 0:
            suggestions.append(f"Found {complexity_visitor.simple_loops} loops suitable for kinda_repeat")

        if complexity_visitor.simple_conditions > 0:
            suggestions.append(f"Found {complexity_visitor.simple_conditions} conditions suitable for sometimes/maybe")

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions
        )


class ComplexityChecker(ast.NodeVisitor):
    """Check AST complexity for injection suitability"""

    def __init__(self):
        self.has_complex_decorators = False
        self.has_metaclasses = False
        self.nested_depth = 0
        self.max_nested_depth = 0
        self.simple_loops = 0
        self.simple_conditions = 0

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        if len(node.decorator_list) > 2:
            self.has_complex_decorators = True
        self._enter_scope()
        self.generic_visit(node)
        self._exit_scope()

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        # Check for metaclasses
        for keyword in node.keywords:
            if keyword.arg == 'metaclass':
                self.has_metaclasses = True
        self._enter_scope()
        self.generic_visit(node)
        self._exit_scope()

    def visit_For(self, node: ast.For) -> None:
        if isinstance(node.iter, ast.Call) and isinstance(node.iter.func, ast.Name):
            if node.iter.func.id == 'range':
                self.simple_loops += 1
        self._enter_scope()
        self.generic_visit(node)
        self._exit_scope()

    def visit_If(self, node: ast.If) -> None:
        if isinstance(node.test, (ast.Compare, ast.Name, ast.Constant)):
            self.simple_conditions += 1
        self._enter_scope()
        self.generic_visit(node)
        self._exit_scope()

    def _enter_scope(self):
        self.nested_depth += 1
        self.max_nested_depth = max(self.max_nested_depth, self.nested_depth)

    def _exit_scope(self):
        self.nested_depth -= 1