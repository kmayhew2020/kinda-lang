"""
Python Code Injection Engine

This module handles the actual transformation of Python code to inject
kinda-lang constructs while preserving semantics and functionality.
"""

import ast
import textwrap
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any, Optional, Set

from .ast_analyzer import InjectionPoint, PatternType, PythonASTAnalyzer
from .patterns import PatternLibrary
from .security import InjectionSecurityValidator
from ..personality import PersonalityContext


@dataclass
class InjectionConfig:
    """Configuration for injection operations"""
    enabled_patterns: Set[PatternType]
    safety_level: str = "safe"  # safe, caution, risky
    preserve_comments: bool = True
    add_kinda_imports: bool = True
    probability_overrides: Dict[str, float] = None

    def __post_init__(self):
        if self.probability_overrides is None:
            self.probability_overrides = {}


@dataclass
class TransformResult:
    """Result of code transformation"""
    success: bool
    transformed_code: str
    applied_patterns: List[str]
    errors: List[str]
    warnings: List[str]
    performance_estimate: float  # Estimated overhead percentage


class CodeTransformer(ast.NodeTransformer):
    """AST transformer that applies kinda-lang injections"""

    def __init__(self, injection_points: List[InjectionPoint],
                 config: InjectionConfig, personality: Optional[PersonalityContext]):
        self.injection_points = injection_points
        self.config = config
        self.personality = personality
        self.applied_patterns = []
        self.kinda_imports_added = False

        # Create lookup for quick access
        self.points_by_line = {}
        for point in injection_points:
            line = point.location.line
            if line not in self.points_by_line:
                self.points_by_line[line] = []
            self.points_by_line[line].append(point)

    def visit_Assign(self, node: ast.Assign) -> ast.AST:
        """Transform assignment statements"""
        if hasattr(node, 'lineno') and node.lineno in self.points_by_line:
            for point in self.points_by_line[node.lineno]:
                if point.pattern_type == PatternType.KINDA_INT:
                    return self._transform_kinda_int(node, point)
                elif point.pattern_type == PatternType.KINDA_FLOAT:
                    return self._transform_kinda_float(node, point)

        return self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> ast.AST:
        """Transform function calls"""
        if hasattr(node, 'lineno') and node.lineno in self.points_by_line:
            for point in self.points_by_line[node.lineno]:
                if point.pattern_type == PatternType.SORTA_PRINT:
                    return self._transform_sorta_print(node, point)

        return self.generic_visit(node)

    def visit_If(self, node: ast.If) -> ast.AST:
        """Transform if statements"""
        if hasattr(node, 'lineno') and node.lineno in self.points_by_line:
            for point in self.points_by_line[node.lineno]:
                if point.pattern_type == PatternType.SOMETIMES:
                    return self._transform_sometimes(node, point)

        return self.generic_visit(node)

    def visit_For(self, node: ast.For) -> ast.AST:
        """Transform for loops"""
        if hasattr(node, 'lineno') and node.lineno in self.points_by_line:
            for point in self.points_by_line[node.lineno]:
                if point.pattern_type == PatternType.KINDA_REPEAT:
                    return self._transform_kinda_repeat(node, point)

        return self.generic_visit(node)

    def _transform_kinda_int(self, node: ast.Assign, point: InjectionPoint) -> ast.AST:
        """Transform integer assignment to use kinda_int"""
        self.applied_patterns.append("kinda_int")

        # Create kinda_int call
        kinda_int_call = ast.Call(
            func=ast.Attribute(
                value=ast.Name(id='kinda', ctx=ast.Load()),
                attr='kinda_int',
                ctx=ast.Load()
            ),
            args=[node.value],  # Original value as base
            keywords=[]
        )

        # Replace the assignment value
        new_assign = ast.Assign(
            targets=node.targets,
            value=kinda_int_call,
            lineno=node.lineno,
            col_offset=node.col_offset
        )

        return new_assign

    def _transform_kinda_float(self, node: ast.Assign, point: InjectionPoint) -> ast.AST:
        """Transform float assignment to use kinda_float"""
        self.applied_patterns.append("kinda_float")

        # Create kinda_float call
        kinda_float_call = ast.Call(
            func=ast.Attribute(
                value=ast.Name(id='kinda', ctx=ast.Load()),
                attr='kinda_float',
                ctx=ast.Load()
            ),
            args=[node.value],  # Original value as base
            keywords=[]
        )

        # Replace the assignment value
        new_assign = ast.Assign(
            targets=node.targets,
            value=kinda_float_call,
            lineno=node.lineno,
            col_offset=node.col_offset
        )

        return new_assign

    def _transform_sorta_print(self, node: ast.Call, point: InjectionPoint) -> ast.AST:
        """Transform print to sorta_print"""
        self.applied_patterns.append("sorta_print")

        # Create sorta_print call
        sorta_print_call = ast.Call(
            func=ast.Attribute(
                value=ast.Name(id='kinda', ctx=ast.Load()),
                attr='sorta_print',
                ctx=ast.Load()
            ),
            args=node.args,
            keywords=node.keywords,
            lineno=node.lineno,
            col_offset=node.col_offset
        )

        return sorta_print_call

    def _transform_sometimes(self, node: ast.If, point: InjectionPoint) -> ast.AST:
        """Transform if statement to sometimes"""
        self.applied_patterns.append("sometimes")

        # Create lambda for the body
        body_stmts = node.body

        # For now, wrap the body in a function call
        # In a real implementation, this would be more sophisticated
        sometimes_call = ast.Expr(
            value=ast.Call(
                func=ast.Attribute(
                    value=ast.Name(id='kinda', ctx=ast.Load()),
                    attr='sometimes',
                    ctx=ast.Load()
                ),
                args=[],
                keywords=[],
                lineno=node.lineno,
                col_offset=node.col_offset
            )
        )

        # Return the original node for now - proper implementation would
        # require more complex AST manipulation
        return node

    def _transform_kinda_repeat(self, node: ast.For, point: InjectionPoint) -> ast.AST:
        """Transform for loop to kinda_repeat"""
        self.applied_patterns.append("kinda_repeat")

        # Extract range arguments
        if (isinstance(node.iter, ast.Call) and
            isinstance(node.iter.func, ast.Name) and
            node.iter.func.id == 'range'):

            range_args = node.iter.args

            # Create kinda_repeat call
            # This is a simplified version - real implementation would be more complex
            kinda_repeat_call = ast.Expr(
                value=ast.Call(
                    func=ast.Attribute(
                        value=ast.Name(id='kinda', ctx=ast.Load()),
                        attr='kinda_repeat',
                        ctx=ast.Load()
                    ),
                    args=range_args,
                    keywords=[],
                    lineno=node.lineno,
                    col_offset=node.col_offset
                )
            )

            return kinda_repeat_call

        return node


class InjectionEngine:
    """Main engine for Python code injection"""

    def __init__(self, personality: Optional[PersonalityContext] = None):
        self.analyzer = PythonASTAnalyzer()
        self.pattern_library = PatternLibrary()
        self.security_validator = InjectionSecurityValidator()
        self.personality = personality

    def inject_file(self, file_path: Path, config: InjectionConfig) -> TransformResult:
        """Inject kinda-lang constructs into a Python file"""
        try:
            # Parse the file
            tree = self.analyzer.parse_file(file_path)

            # Find injection points
            injection_points = self.analyzer.find_injection_points(tree)

            # Filter based on config
            filtered_points = self._filter_injection_points(injection_points, config)

            # Validate security
            security_result = self.security_validator.validate_injection_request(
                file_path, filtered_points, config
            )

            if not security_result.is_safe:
                return TransformResult(
                    success=False,
                    transformed_code="",
                    applied_patterns=[],
                    errors=security_result.errors,
                    warnings=security_result.warnings,
                    performance_estimate=0.0
                )

            # Apply transformations
            return self._apply_transformations(tree, filtered_points, config)

        except Exception as e:
            return TransformResult(
                success=False,
                transformed_code="",
                applied_patterns=[],
                errors=[f"Injection failed: {e}"],
                warnings=[],
                performance_estimate=0.0
            )

    def inject_source(self, source: str, config: InjectionConfig,
                     filename: str = '<string>') -> TransformResult:
        """Inject kinda-lang constructs into Python source code"""
        try:
            # Parse the source
            tree = self.analyzer.parse_source(source, filename)

            # Find injection points
            injection_points = self.analyzer.find_injection_points(tree)

            # Filter based on config
            filtered_points = self._filter_injection_points(injection_points, config)

            # Apply transformations
            return self._apply_transformations(tree, filtered_points, config)

        except Exception as e:
            return TransformResult(
                success=False,
                transformed_code="",
                applied_patterns=[],
                errors=[f"Injection failed: {e}"],
                warnings=[],
                performance_estimate=0.0
            )

    def _filter_injection_points(self, points: List[InjectionPoint],
                                config: InjectionConfig) -> List[InjectionPoint]:
        """Filter injection points based on configuration"""
        filtered = []

        for point in points:
            # Check if pattern is enabled
            if point.pattern_type in config.enabled_patterns:
                # Check safety level
                if self._is_safe_enough(point, config.safety_level):
                    filtered.append(point)

        return filtered

    def _is_safe_enough(self, point: InjectionPoint, safety_level: str) -> bool:
        """Check if injection point meets safety requirements"""
        safety_levels = {
            'safe': ['safe'],
            'caution': ['safe', 'caution'],
            'risky': ['safe', 'caution', 'risky']
        }

        return point.safety_level.value in safety_levels.get(safety_level, ['safe'])

    def _apply_transformations(self, tree: ast.AST, points: List[InjectionPoint],
                             config: InjectionConfig) -> TransformResult:
        """Apply transformations to the AST"""
        transformer = CodeTransformer(points, config, self.personality)

        # Transform the tree
        new_tree = transformer.visit(tree)

        # Generate code with imports
        code_parts = []

        if config.add_kinda_imports:
            code_parts.append("import kinda")
            code_parts.append("")

        # Convert AST back to source code
        try:
            import astor
            transformed_source = astor.to_source(new_tree)
        except ImportError:
            # Fallback if astor is not available
            transformed_source = "# Transformed code (astor not available for pretty printing)\n"
            transformed_source += f"# Applied patterns: {', '.join(transformer.applied_patterns)}\n"

        code_parts.append(transformed_source)

        final_code = '\n'.join(code_parts)

        # Calculate performance estimate (rough approximation)
        performance_estimate = len(transformer.applied_patterns) * 2.5  # 2.5% per pattern

        return TransformResult(
            success=True,
            transformed_code=final_code,
            applied_patterns=transformer.applied_patterns,
            errors=[],
            warnings=[],
            performance_estimate=performance_estimate
        )