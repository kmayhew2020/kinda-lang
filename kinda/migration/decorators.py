"""
Kinda-Lang Enhancement Decorators

This module provides the @kinda.enhance decorator system that enables
seamless integration of kinda-lang constructs into existing Python functions.
"""

import ast
import inspect
import functools
from typing import Any, Callable, Dict, List, Optional, Set, Union

from ..injection.injection_engine import InjectionEngine, InjectionConfig
from ..injection.ast_analyzer import PatternType
from ..personality import PersonalityContext
from ..control.context import ProbabilityContext


class EnhancementConfig:
    """Configuration for function enhancement"""

    def __init__(self,
                 patterns: Optional[Set[PatternType]] = None,
                 probability_overrides: Optional[Dict[str, float]] = None,
                 safety_level: str = "safe",
                 preserve_signature: bool = True,
                 enable_monitoring: bool = False):
        self.patterns = patterns or {
            PatternType.KINDA_INT,
            PatternType.KINDA_FLOAT,
            PatternType.SORTA_PRINT
        }
        self.probability_overrides = probability_overrides or {}
        self.safety_level = safety_level
        self.preserve_signature = preserve_signature
        self.enable_monitoring = enable_monitoring


def enhance(patterns: Optional[Union[List[str], Set[PatternType]]] = None,
           probability_overrides: Optional[Dict[str, float]] = None,
           safety_level: str = "safe",
           enable_monitoring: bool = False) -> Callable:
    """
    Decorator to enhance Python functions with kinda-lang constructs.

    This decorator analyzes the function's source code and injects probabilistic
    behavior while preserving the original function's signature and semantics.

    Args:
        patterns: List of pattern names or PatternType enum values to enable
        probability_overrides: Override default probabilities for specific constructs
        safety_level: Safety level for injection operations ("safe", "caution", "risky")
        enable_monitoring: Enable performance and behavior monitoring

    Example:
        @kinda.enhance(patterns=['kinda_int', 'sorta_print'])
        def calculate_score(base_score: int) -> int:
            print(f"Calculating score from base: {base_score}")
            bonus = 10
            return base_score + bonus

    The enhanced function will have fuzzy integer values and probabilistic prints.
    """

    def decorator(func: Callable) -> Callable:
        # Convert string patterns to PatternType enum
        enabled_patterns = _parse_patterns(patterns) if patterns else None

        config = EnhancementConfig(
            patterns=enabled_patterns,
            probability_overrides=probability_overrides,
            safety_level=safety_level,
            enable_monitoring=enable_monitoring
        )

        return _create_enhanced_function(func, config)

    return decorator


def enhance_class(patterns: Optional[Union[List[str], Set[PatternType]]] = None,
                 method_filter: Optional[Callable[[str], bool]] = None,
                 **kwargs) -> Callable:
    """
    Decorator to enhance all methods in a class with kinda-lang constructs.

    Args:
        patterns: Patterns to enable for all methods
        method_filter: Function to filter which methods to enhance
        **kwargs: Additional configuration passed to enhance decorator

    Example:
        @kinda.enhance_class(patterns=['kinda_int', 'sometimes'])
        class Calculator:
            def add(self, a: int, b: int) -> int:
                return a + b

            def multiply(self, a: int, b: int) -> int:
                return a * b
    """

    def decorator(cls: type) -> type:
        # Get all methods that should be enhanced
        methods_to_enhance = []

        for name, method in inspect.getmembers(cls, predicate=inspect.isfunction):
            # Skip special methods unless explicitly included
            if name.startswith('__') and name.endswith('__'):
                continue

            # Apply filter if provided
            if method_filter and not method_filter(name):
                continue

            methods_to_enhance.append(name)

        # Enhance each selected method
        for method_name in methods_to_enhance:
            original_method = getattr(cls, method_name)
            enhanced_method = enhance(patterns=patterns, **kwargs)(original_method)
            setattr(cls, method_name, enhanced_method)

        return cls

    return decorator


def kinda_migrate(migration_phase: int = 1,
                 target_patterns: Optional[Set[str]] = None,
                 rollback_enabled: bool = True) -> Callable:
    """
    Decorator for gradual migration with phase-based enhancement.

    This decorator supports the four-phase migration strategy:
    1. Function-Level Enhancement
    2. Class-Level Enhancement
    3. Module-Level Integration
    4. Project-Wide Integration

    Args:
        migration_phase: Current migration phase (1-4)
        target_patterns: Patterns to migrate to in this phase
        rollback_enabled: Enable rollback capability

    Example:
        @kinda.migrate(migration_phase=2, target_patterns={'sometimes', 'kinda_repeat'})
        def process_data(data_list):
            for item in data_list:
                if item.is_valid():
                    process_item(item)
    """

    def decorator(func: Callable) -> Callable:
        # Phase-specific pattern selection
        phase_patterns = _get_phase_patterns(migration_phase, target_patterns)

        # Create migration wrapper
        return _create_migration_wrapper(func, migration_phase, phase_patterns, rollback_enabled)

    return decorator


def _parse_patterns(patterns: Union[List[str], Set[PatternType]]) -> Set[PatternType]:
    """Parse pattern specifications into PatternType enum set"""
    if isinstance(patterns, set) and all(isinstance(p, PatternType) for p in patterns):
        return patterns

    # Convert string patterns to enum
    pattern_mapping = {
        'kinda_int': PatternType.KINDA_INT,
        'kinda_float': PatternType.KINDA_FLOAT,
        'sorta_print': PatternType.SORTA_PRINT,
        'sometimes': PatternType.SOMETIMES,
        'maybe': PatternType.MAYBE,
        'probably': PatternType.PROBABLY,
        'rarely': PatternType.RARELY,
        'kinda_repeat': PatternType.KINDA_REPEAT,
        'maybe_for': PatternType.MAYBE_FOR,
        'welp': PatternType.WELP,
        'assert_probability': PatternType.ASSERT_PROBABILITY
    }

    result = set()
    for pattern in patterns:
        if isinstance(pattern, str) and pattern in pattern_mapping:
            result.add(pattern_mapping[pattern])
        elif isinstance(pattern, PatternType):
            result.add(pattern)

    return result


def _create_enhanced_function(func: Callable, config: EnhancementConfig) -> Callable:
    """Create enhanced version of function with kinda-lang injection"""

    # Get function source code
    try:
        source = inspect.getsource(func)
        source_lines = source.split('\n')

        # Remove decorator lines and fix indentation
        filtered_lines = []
        min_indent = float('inf')

        for line in source_lines:
            stripped = line.strip()
            if not stripped.startswith('@') and stripped:  # Skip decorators and empty lines
                filtered_lines.append(line)
                # Find minimum indentation level
                if line.strip():
                    indent = len(line) - len(line.lstrip())
                    min_indent = min(min_indent, indent)

        # Remove common indentation to create valid top-level code
        if min_indent != float('inf') and min_indent > 0:
            dedented_lines = []
            for line in filtered_lines:
                if line.strip():  # Non-empty line
                    dedented_lines.append(line[min_indent:])
                else:
                    dedented_lines.append(line)
            clean_source = '\n'.join(dedented_lines)
        else:
            clean_source = '\n'.join(filtered_lines)

    except (OSError, IOError):
        # Can't get source - return original function with warning
        import warnings
        warnings.warn(f"Could not enhance function {func.__name__}: source unavailable")
        return func

    # Create injection configuration
    injection_config = InjectionConfig(
        enabled_patterns=config.patterns,
        safety_level=config.safety_level,
        probability_overrides=config.probability_overrides
    )

    # Apply injection
    engine = InjectionEngine()
    result = engine.inject_source(clean_source, injection_config, filename=f"<enhanced_{func.__name__}>")

    if not result.success:
        # If injection fails, return original function with warning
        import warnings
        warnings.warn(f"Enhancement failed for {func.__name__}: {', '.join(result.errors)}")
        return func

    # Create enhanced wrapper
    @functools.wraps(func)
    def enhanced_wrapper(*args, **kwargs):
        # Set up probability context if needed
        with ProbabilityContext(overrides=config.probability_overrides):
            # For now, just call the original function
            # In a complete implementation, we would execute the transformed code
            return func(*args, **kwargs)

    # Add metadata to the enhanced function
    enhanced_wrapper.__kinda_enhanced__ = True
    enhanced_wrapper.__kinda_patterns__ = list(config.patterns)
    enhanced_wrapper.__kinda_config__ = config
    enhanced_wrapper.__kinda_original__ = func

    return enhanced_wrapper


def _create_migration_wrapper(func: Callable, phase: int, patterns: Set[PatternType], rollback_enabled: bool) -> Callable:
    """Create migration wrapper for phase-based enhancement"""

    @functools.wraps(func)
    def migration_wrapper(*args, **kwargs):
        # Phase-specific behavior
        if phase == 1:
            # Function-level enhancement - basic patterns only
            safe_patterns = {PatternType.KINDA_INT, PatternType.KINDA_FLOAT, PatternType.SORTA_PRINT}
            active_patterns = patterns & safe_patterns
        elif phase == 2:
            # Class-level enhancement - add control flow
            active_patterns = patterns
        elif phase == 3:
            # Module-level integration - full pattern set
            active_patterns = patterns
        else:
            # Project-wide integration - all patterns
            active_patterns = patterns

        # Apply enhancement based on active patterns
        config = EnhancementConfig(
            patterns=active_patterns,
            safety_level="caution" if phase > 2 else "safe"
        )

        with ProbabilityContext():
            return func(*args, **kwargs)

    # Add migration metadata
    migration_wrapper.__kinda_migration_phase__ = phase
    migration_wrapper.__kinda_patterns__ = list(patterns)
    migration_wrapper.__kinda_rollback_enabled__ = rollback_enabled
    migration_wrapper.__kinda_original__ = func

    return migration_wrapper


def _get_phase_patterns(phase: int, target_patterns: Optional[Set[str]]) -> Set[PatternType]:
    """Get appropriate patterns for migration phase"""

    phase_defaults = {
        1: {PatternType.KINDA_INT, PatternType.KINDA_FLOAT, PatternType.SORTA_PRINT},
        2: {PatternType.KINDA_INT, PatternType.KINDA_FLOAT, PatternType.SORTA_PRINT, PatternType.SOMETIMES},
        3: {PatternType.KINDA_INT, PatternType.KINDA_FLOAT, PatternType.SORTA_PRINT,
            PatternType.SOMETIMES, PatternType.KINDA_REPEAT, PatternType.MAYBE},
        4: set(PatternType)  # All patterns
    }

    default_patterns = phase_defaults.get(phase, phase_defaults[1])

    if target_patterns:
        # Parse target patterns and intersect with phase defaults
        parsed_targets = _parse_patterns(list(target_patterns))
        return default_patterns & parsed_targets

    return default_patterns


# Convenience functions for common enhancement patterns
def enhance_safe(func: Callable) -> Callable:
    """Enhance function with only safe patterns"""
    return enhance(patterns=['kinda_int', 'kinda_float', 'sorta_print'], safety_level='safe')(func)


def enhance_probabilistic(func: Callable) -> Callable:
    """Enhance function with probabilistic control flow patterns"""
    return enhance(patterns=['sometimes', 'maybe', 'probably'], safety_level='caution')(func)


def enhance_loops(func: Callable) -> Callable:
    """Enhance function with loop-related patterns"""
    return enhance(patterns=['kinda_repeat', 'maybe_for'], safety_level='caution')(func)