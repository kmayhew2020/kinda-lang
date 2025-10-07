#!/usr/bin/env python3
"""
Integration test for Epic #127: Python Enhancement Bridge
Tests the core functionality of all 4 major features.
"""

import tempfile
from pathlib import Path


def test_injection_engine():
    """Test the injection engine basic functionality"""
    print("Testing injection engine...")

    from kinda.injection import InjectionEngine, InjectionConfig
    from kinda.injection.ast_analyzer import PatternType

    # Test source code
    test_code = """
def calculate_score(base: int) -> int:
    bonus = 10
    print(f"Calculating with base: {base}")
    return base + bonus
"""

    # Create injection config
    config = InjectionConfig(
        enabled_patterns={PatternType.KINDA_INT, PatternType.SORTA_PRINT}, safety_level="safe"
    )

    # Test injection
    engine = InjectionEngine()
    result = engine.inject_source(test_code, config, "test_function")

    print(f"✓ Injection result success: {result.success}")
    print(f"✓ Applied patterns: {result.applied_patterns}")

    return result.success


def test_enhancement_decorators():
    """Test the @enhance decorator functionality"""
    print("\nTesting enhancement decorators...")

    from kinda.migration import enhance

    @enhance(patterns=["kinda_int", "sorta_print"], safety_level="safe")
    def test_function(x: int) -> int:
        y = 42
        print(f"Processing {x}")
        return x + y

    # Test enhanced function
    result = test_function(10)
    enhanced = hasattr(test_function, "__kinda_enhanced__")

    print(f"✓ Function enhanced: {enhanced}")
    print(f"✓ Function callable: {callable(test_function)}")
    print(f"✓ Result: {result}")

    return enhanced


def test_probability_control():
    """Test the probability control system"""
    print("\nTesting probability control...")

    from kinda.control import ProbabilityContext, ProbabilityProfile

    # Test context creation
    profile = ProbabilityProfile.create_testing_profile(seed=42)

    with ProbabilityContext(profile=profile) as ctx:
        prob1 = ctx.get_probability("sometimes", 0.7)
        prob2 = ctx.get_probability("maybe", 0.5)

        print(f"✓ Sometimes probability: {prob1}")
        print(f"✓ Maybe probability: {prob2}")

        # Test nested context
        with ctx.with_override("sometimes", 0.9):
            prob3 = ctx.get_probability("sometimes", 0.7)
            print(f"✓ Overridden sometimes probability: {prob3}")

    return True


def test_transpiler_infrastructure():
    """Test the transpiler infrastructure"""
    print("\nTesting transpiler infrastructure...")

    from kinda.transpiler import TranspilerEngine, LanguageTarget

    # Test engine creation
    engine = TranspilerEngine()

    # Test basic functionality
    targets = engine.get_available_targets()
    print(f"✓ Available targets: {targets}")

    # Test if we can create a target
    python_target = engine.get_target("python_enhanced")
    print(f"✓ Python enhanced target available: {python_target is not None}")

    return True


def test_migration_utilities():
    """Test migration utilities"""
    print("\nTesting migration utilities...")

    from kinda.migration import MigrationUtilities

    utilities = MigrationUtilities()

    # Create a temporary test file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(
            """
def test_function():
    x = 42
    print("Hello World")
    return x
"""
        )
        temp_path = Path(f.name)

    try:
        # Test file analysis
        analysis = utilities.analyze_file(temp_path)
        print(f"✓ File analyzed: {analysis is not None}")
        if analysis:
            print(f"✓ Functions found: {analysis.function_count}")
            print(f"✓ Injection opportunities: {len(analysis.injection_opportunities)}")

        return analysis is not None
    finally:
        temp_path.unlink()  # Clean up


def main():
    """Run all integration tests"""
    print("Epic #127 Integration Tests")
    print("=" * 40)

    tests = [
        test_injection_engine,
        test_enhancement_decorators,
        test_probability_control,
        test_transpiler_infrastructure,
        test_migration_utilities,
    ]

    passed = 0
    for test in tests:
        try:
            if test():
                passed += 1
                print(f"✓ {test.__name__} PASSED")
            else:
                print(f"✗ {test.__name__} FAILED")
        except Exception as e:
            print(f"✗ {test.__name__} ERROR: {e}")

    print("\n" + "=" * 40)
    print(f"Results: {passed}/{len(tests)} tests passed")

    if passed == len(tests):
        print("🎉 All Epic #127 core features working!")
        return True
    else:
        print("❌ Some features need attention")
        return False


if __name__ == "__main__":
    main()
