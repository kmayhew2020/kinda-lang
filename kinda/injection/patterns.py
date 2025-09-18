"""
Pattern Library for Python Injection

This module defines the available patterns for injecting kinda-lang constructs
into Python code, with their detection logic and transformation rules.
"""

import ast
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional, Any

from .ast_analyzer import PatternType, SecurityLevel


@dataclass
class PatternInfo:
    """Information about an injection pattern"""

    name: str
    pattern_type: PatternType
    description: str
    default_probability: float
    security_level: SecurityLevel
    complexity: str  # basic, intermediate, advanced
    prerequisites: List[str]
    examples: List[str]


class InjectionPattern(ABC):
    """Base class for all injection patterns"""

    def __init__(self, pattern_info: PatternInfo):
        self.info = pattern_info

    @abstractmethod
    def detect(self, node: ast.AST) -> bool:
        """Detect if this pattern can be applied to the given AST node"""
        pass

    @abstractmethod
    def validate_safety(self, node: ast.AST) -> bool:
        """Validate that applying this pattern to the node is safe"""
        pass

    @abstractmethod
    def estimate_impact(self, node: ast.AST) -> float:
        """Estimate the performance impact of applying this pattern (percentage)"""
        pass

    def get_prerequisites(self) -> List[str]:
        """Get list of required imports or setup for this pattern"""
        return self.info.prerequisites

    def get_examples(self) -> List[str]:
        """Get example usage patterns"""
        return self.info.examples


class KindaIntPattern(InjectionPattern):
    """Pattern for injecting kinda_int behavior into integer assignments"""

    def __init__(self):
        super().__init__(
            PatternInfo(
                name="Kinda Integer",
                pattern_type=PatternType.KINDA_INT,
                description="Adds fuzzy noise to integer values",
                default_probability=1.0,  # Always fuzzy when applied
                security_level=SecurityLevel.SAFE,
                complexity="basic",
                prerequisites=["kinda.kinda_int"],
                examples=[
                    "x = 42  # becomes x = kinda.kinda_int(42)",
                    "count = 10  # becomes count = kinda.kinda_int(10)",
                ],
            )
        )

    def detect(self, node: ast.AST) -> bool:
        """Detect integer assignment patterns"""
        if isinstance(node, ast.Assign):
            # Single target assignment of integer constant
            if (
                len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name)
                and isinstance(node.value, ast.Constant)
                and isinstance(node.value.value, int)
            ):
                return True
        return False

    def validate_safety(self, node: ast.AST) -> bool:
        """Integer assignments are generally safe for injection"""
        if isinstance(node, ast.Assign):
            target = node.targets[0]
            # Avoid system/reserved variables
            reserved_names = {"__file__", "__name__", "__package__", "__version__"}
            if isinstance(target, ast.Name) and target.id in reserved_names:
                return False
        return True

    def estimate_impact(self, node: ast.AST) -> float:
        """Minimal performance impact for integer fuzzing"""
        return 1.5  # 1.5% overhead


class KindaFloatPattern(InjectionPattern):
    """Pattern for injecting kinda_float behavior into float assignments"""

    def __init__(self):
        super().__init__(
            PatternInfo(
                name="Kinda Float",
                pattern_type=PatternType.KINDA_FLOAT,
                description="Adds fuzzy variance to floating-point values",
                default_probability=1.0,
                security_level=SecurityLevel.SAFE,
                complexity="basic",
                prerequisites=["kinda.kinda_float"],
                examples=[
                    "pi = 3.14159  # becomes pi = kinda.kinda_float(3.14159)",
                    "ratio = 0.618  # becomes ratio = kinda.kinda_float(0.618)",
                ],
            )
        )

    def detect(self, node: ast.AST) -> bool:
        """Detect float assignment patterns"""
        if isinstance(node, ast.Assign):
            if (
                len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name)
                and isinstance(node.value, ast.Constant)
                and isinstance(node.value.value, float)
            ):
                return True
        return False

    def validate_safety(self, node: ast.AST) -> bool:
        """Float assignments are generally safe, but check for critical values"""
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant):
            value = node.value.value
            # Avoid critical system values
            if abs(value) < 1e-10 or abs(value) > 1e10:
                return False
        return True

    def estimate_impact(self, node: ast.AST) -> float:
        """Minimal performance impact for float fuzzing"""
        return 1.8  # 1.8% overhead


class SortaPrintPattern(InjectionPattern):
    """Pattern for making print statements probabilistic"""

    def __init__(self):
        super().__init__(
            PatternInfo(
                name="Sorta Print",
                pattern_type=PatternType.SORTA_PRINT,
                description="Makes print statements execute probabilistically",
                default_probability=0.8,  # 80% chance of printing
                security_level=SecurityLevel.SAFE,
                complexity="basic",
                prerequisites=["kinda.sorta_print"],
                examples=[
                    'print("Hello")  # becomes kinda.sorta_print("Hello")',
                    'print(f"Value: {x}")  # becomes kinda.sorta_print(f"Value: {x}")',
                ],
            )
        )

    def detect(self, node: ast.AST) -> bool:
        """Detect print function calls"""
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id == "print":
                return True
        return False

    def validate_safety(self, node: ast.AST) -> bool:
        """Print statements are safe to make probabilistic"""
        # Could add checks for critical logging or debug prints
        return True

    def estimate_impact(self, node: ast.AST) -> float:
        """Very minimal impact for print statements"""
        return 0.5  # 0.5% overhead


class SometimesPattern(InjectionPattern):
    """Pattern for making conditional statements probabilistic"""

    def __init__(self):
        super().__init__(
            PatternInfo(
                name="Sometimes",
                pattern_type=PatternType.SOMETIMES,
                description="Makes conditional execution probabilistic",
                default_probability=0.7,  # 70% execution chance
                security_level=SecurityLevel.CAUTION,
                complexity="intermediate",
                prerequisites=["kinda.sometimes"],
                examples=[
                    "if condition:  # becomes kinda.sometimes(lambda: ...)",
                    "if x > 0:  # becomes probabilistic execution",
                ],
            )
        )

    def detect(self, node: ast.AST) -> bool:
        """Detect if statements suitable for sometimes injection"""
        if isinstance(node, ast.If):
            # Simple conditions are good candidates
            return self._is_simple_condition(node.test)
        return False

    def validate_safety(self, node: ast.AST) -> bool:
        """Check if if-statement is safe for probabilistic execution"""
        if isinstance(node, ast.If):
            # Avoid if statements with critical operations
            return not self._has_critical_operations(node.body)
        return False

    def estimate_impact(self, node: ast.AST) -> float:
        """Moderate impact for conditional probability"""
        return 3.0  # 3% overhead

    def _is_simple_condition(self, node: ast.AST) -> bool:
        """Check if condition is simple enough for probabilistic execution"""
        return isinstance(node, (ast.Compare, ast.BoolOp, ast.Name, ast.Constant))

    def _has_critical_operations(self, body: List[ast.AST]) -> bool:
        """Check if body contains critical operations"""
        for stmt in body:
            if isinstance(stmt, (ast.Return, ast.Raise, ast.Break, ast.Continue)):
                return True
            # Check for file operations, network calls, etc.
            if isinstance(stmt, ast.Call):
                if hasattr(stmt.func, "attr"):
                    attr = stmt.func.attr
                    if attr in {"write", "read", "open", "close", "send", "recv"}:
                        return True
        return False


class KindaRepeatPattern(InjectionPattern):
    """Pattern for making loops fuzzy with kinda_repeat"""

    def __init__(self):
        super().__init__(
            PatternInfo(
                name="Kinda Repeat",
                pattern_type=PatternType.KINDA_REPEAT,
                description="Makes loop iterations fuzzy and probabilistic",
                default_probability=1.0,  # Always apply when detected
                security_level=SecurityLevel.CAUTION,
                complexity="intermediate",
                prerequisites=["kinda.kinda_repeat"],
                examples=[
                    "for i in range(10):  # becomes kinda.kinda_repeat(10, ...)",
                    "for _ in range(5):  # becomes fuzzy iteration count",
                ],
            )
        )

    def detect(self, node: ast.AST) -> bool:
        """Detect for loops with range() suitable for kinda_repeat"""
        if isinstance(node, ast.For):
            if (
                isinstance(node.iter, ast.Call)
                and isinstance(node.iter.func, ast.Name)
                and node.iter.func.id == "range"
            ):
                return True
        return False

    def validate_safety(self, node: ast.AST) -> bool:
        """Check if loop is safe for fuzzy iteration"""
        if isinstance(node, ast.For):
            # Avoid loops with critical side effects
            return not self._has_critical_loop_operations(node.body)
        return False

    def estimate_impact(self, node: ast.AST) -> float:
        """Moderate to high impact for loop fuzzing"""
        return 5.0  # 5% overhead

    def _has_critical_loop_operations(self, body: List[ast.AST]) -> bool:
        """Check if loop body has critical operations"""
        for stmt in body:
            if isinstance(stmt, (ast.Return, ast.Raise, ast.Break, ast.Continue)):
                return True
            # Check for file operations in loops
            if isinstance(stmt, ast.Call):
                if hasattr(stmt.func, "attr"):
                    attr = stmt.func.attr
                    if attr in {"write", "append", "insert", "delete"}:
                        return True
        return False


class PatternLibrary:
    """Registry and manager for all injection patterns"""

    def __init__(self):
        self.patterns: Dict[PatternType, InjectionPattern] = {}
        self._initialize_patterns()

    def _initialize_patterns(self):
        """Initialize all available patterns"""
        patterns = [
            KindaIntPattern(),
            KindaFloatPattern(),
            SortaPrintPattern(),
            SometimesPattern(),
            KindaRepeatPattern(),
        ]

        for pattern in patterns:
            self.patterns[pattern.info.pattern_type] = pattern

    def get_pattern(self, pattern_type: PatternType) -> Optional[InjectionPattern]:
        """Get a specific pattern by type"""
        return self.patterns.get(pattern_type)

    def get_all_patterns(self) -> List[InjectionPattern]:
        """Get all available patterns"""
        return list(self.patterns.values())

    def get_patterns_by_complexity(self, complexity: str) -> List[InjectionPattern]:
        """Get patterns by complexity level"""
        return [p for p in self.patterns.values() if p.info.complexity == complexity]

    def get_patterns_by_security_level(
        self, security_level: SecurityLevel
    ) -> List[InjectionPattern]:
        """Get patterns by security level"""
        return [p for p in self.patterns.values() if p.info.security_level == security_level]

    def validate_pattern_compatibility(self, patterns: List[PatternType]) -> Dict[str, Any]:
        """Check compatibility between multiple patterns"""
        results = {"compatible": True, "conflicts": [], "warnings": []}

        # Check for known conflicts
        if PatternType.KINDA_INT in patterns and PatternType.KINDA_FLOAT in patterns:
            results["warnings"].append(
                "Both kinda_int and kinda_float enabled - ensure type consistency"
            )

        if PatternType.SOMETIMES in patterns and PatternType.KINDA_REPEAT in patterns:
            results["warnings"].append(
                "Sometimes and kinda_repeat together may create complex probability interactions"
            )

        return results

    def estimate_total_impact(self, pattern_counts: Dict[PatternType, int]) -> float:
        """Estimate total performance impact of multiple patterns"""
        total_impact = 0.0

        for pattern_type, count in pattern_counts.items():
            pattern = self.get_pattern(pattern_type)
            if pattern:
                # Simple approximation - real implementation would be more sophisticated
                base_impact = 2.0  # Base impact per pattern
                total_impact += base_impact * count

        # Apply diminishing returns for multiple patterns
        if total_impact > 10.0:
            total_impact = 10.0 + (total_impact - 10.0) * 0.5

        return min(total_impact, 50.0)  # Cap at 50% overhead
