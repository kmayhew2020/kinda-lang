# kinda/composition/__init__.py

"""
Kinda-Lang Composition Framework

Provides infrastructure for creating, testing, and validating composite constructs
built from basic probabilistic primitives.

This framework enables the "Kinda builds Kinda" philosophy by providing
systematic tools for construct composition, statistical validation, and
performance monitoring.
"""

from typing import List, Dict, Any

# Core framework components
from .framework import (
    CompositeConstruct,
    CompositionStrategy,
    CompositionConfig,
    CompositionEngine,
    PersonalityBridge,
    PerformanceMonitor,
    get_composition_engine
)

# Composition patterns
from .patterns import (
    UnionComposition,
    ThresholdComposition,
    ToleranceComposition,
    CompositionPatternFactory,
    create_sorta_pattern,
    create_ish_pattern,
    create_consensus_pattern
)

# Testing framework
from .testing import (
    CompositionTestFramework,
    CompositionAssertion,
    CompositionIntegrationTester,
    get_test_framework
)

# Validation system
from .validation import (
    DependencyValidator,
    PerformanceValidator,
    validate_construct_dependencies,
    validate_performance_target,
    register_construct_dependencies,
    establish_performance_baseline,
    validate_composition_integrity,
    dependency_validator,
    performance_validator
)

__version__ = "0.1.0"
__all__ = [
    # Core framework
    'CompositeConstruct',
    'CompositionStrategy',
    'CompositionConfig',
    'CompositionEngine',
    'PersonalityBridge',
    'PerformanceMonitor',
    'get_composition_engine',

    # Patterns
    'UnionComposition',
    'ThresholdComposition',
    'ToleranceComposition',
    'CompositionPatternFactory',
    'create_sorta_pattern',
    'create_ish_pattern',
    'create_consensus_pattern',

    # Testing
    'CompositionTestFramework',
    'CompositionAssertion',
    'CompositionIntegrationTester',
    'get_test_framework',

    # Validation
    'DependencyValidator',
    'PerformanceValidator',
    'validate_construct_dependencies',
    'validate_performance_target',
    'register_construct_dependencies',
    'establish_performance_baseline',
    'validate_composition_integrity',
    'dependency_validator',
    'performance_validator'
]


def initialize_framework():
    """Initialize the composition framework with default configuration."""

    # Get global instances
    composition_engine = get_composition_engine()
    test_framework = get_test_framework()

    print("[composition] Framework initialized successfully")
    return composition_engine, test_framework


def get_framework_info():
    """Get information about the composition framework."""
    return {
        'name': 'Kinda-Lang Composition Framework',
        'version': __version__,
        'description': 'Infrastructure for systematic construct composition',
        'components': [
            'Core Framework (CompositeConstruct, CompositionEngine)',
            'Pattern Library (UnionComposition, ThresholdComposition, etc.)',
            'Testing Framework (Statistical validation, integration testing)',
            'Validation System (Dependencies, performance monitoring)'
        ],
        'capabilities': [
            'Union/Intersection/Sequential/Weighted/Conditional composition strategies',
            'Personality-aware bridge probability adjustments',
            'Statistical validation with configurable tolerance',
            'Performance monitoring with 20% overhead target',
            'Dependency validation and circular dependency detection',
            'Integration testing with existing personality system'
        ]
    }


def create_composition_example():
    """Create an example composition for demonstration purposes."""

    # Example: Create a union composition similar to Task 1's sorta_print
    bridge_config = {
        'reliable': 0.0,    # No bridge needed for reliable
        'cautious': 0.0,    # No bridge needed for cautious
        'playful': 0.2,     # Bridge gap for playful personality
        'chaotic': 0.2      # Bridge gap for chaotic personality
    }

    example_composition = CompositionPatternFactory.create_union_pattern(
        "example_sorta", ["sometimes", "maybe"], bridge_config
    )

    # Register with the framework
    engine = get_composition_engine()
    engine.register_composite(example_composition)

    return example_composition


def validate_framework_installation():
    """Validate that the framework is properly installed and functional."""

    validation_results = {
        'framework_initialized': False,
        'imports_successful': False,
        'example_creation': False,
        'validation_system': False,
        'overall_status': False
    }

    try:
        # Test framework initialization
        engine, framework = initialize_framework()
        validation_results['framework_initialized'] = True

        # Test imports
        assert CompositeConstruct is not None
        assert CompositionEngine is not None
        assert CompositionTestFramework is not None
        validation_results['imports_successful'] = True

        # Test example creation
        example = create_composition_example()
        validation_results['example_creation'] = True

        # Test validation system
        integrity_check = validate_composition_integrity(example)
        validation_results['validation_system'] = integrity_check['overall_status'] == 'PASS'

        # Overall status
        validation_results['overall_status'] = all([
            validation_results['framework_initialized'],
            validation_results['imports_successful'],
            validation_results['example_creation']
        ])

    except Exception as e:
        validation_results['error'] = str(e)

    return validation_results


# Auto-initialize framework on import
try:
    composition_engine, test_framework = initialize_framework()
    _FRAMEWORK_INITIALIZED = True
except Exception as e:
    _FRAMEWORK_INITIALIZED = False
    print(f"[composition] Warning: Framework initialization failed: {e}")


def is_framework_ready():
    """Check if the framework is ready for use."""
    return _FRAMEWORK_INITIALIZED


# Provide convenient shortcuts for common operations
def quick_union_composition(name: str, constructs: List[str],
                          bridge_probs: dict = None) -> UnionComposition:
    """Quickly create and register a union composition."""
    composition = CompositionPatternFactory.create_union_pattern(
        name, constructs, bridge_probs
    )
    get_composition_engine().register_composite(composition)
    return composition


def quick_threshold_composition(name: str, constructs: List[str],
                              threshold: float = 0.5) -> ThresholdComposition:
    """Quickly create and register a threshold composition."""
    composition = CompositionPatternFactory.create_threshold_pattern(
        name, constructs, threshold
    )
    get_composition_engine().register_composite(composition)
    return composition


def quick_tolerance_composition(name: str, base_construct: str,
                              tolerance_func: str = "kinda_float") -> ToleranceComposition:
    """Quickly create and register a tolerance composition."""
    composition = CompositionPatternFactory.create_tolerance_pattern(
        name, base_construct, tolerance_func
    )
    get_composition_engine().register_composite(composition)
    return composition


def test_composition(composite: CompositeConstruct,
                   personalities: List[str] = None,
                   tolerance: float = 0.05) -> bool:
    """Quickly test a composition across personalities."""
    if personalities is None:
        personalities = ['reliable', 'cautious', 'playful', 'chaotic']

    framework = get_test_framework()

    for personality in personalities:
        target_probs = composite.get_target_probabilities()
        expected_prob = target_probs.get(personality, 0.5)

        passed = framework.validate_composition_probability(
            composite, personality, expected_prob, tolerance
        )

        if not passed:
            return False

    return True


# Framework status information
FRAMEWORK_STATUS = {
    'initialized': _FRAMEWORK_INITIALIZED,
    'version': __version__,
    'components_loaded': len(__all__),
    'ready_for_task_3': True  # Framework is ready for ~ish pattern implementation
}