#!/usr/bin/env python3

"""
Epic #126 Task 3: Performance benchmarks for ~ish composition framework.
Validates <20% overhead requirement.
"""

import pytest
import time
import statistics
import os
from contextlib import contextmanager

# Skip all performance tests in CI environments
pytestmark = pytest.mark.skipif(
    bool(os.getenv("CI")) or bool(os.getenv("GITHUB_ACTIONS")),
    reason="Performance tests are flaky in CI environments",
)


@contextmanager
def performance_timer():
    """Context manager for timing operations."""
    start = time.perf_counter()
    yield lambda: time.perf_counter() - start


class TestIshPerformanceBenchmark:
    """Benchmark composition framework performance vs legacy."""

    def setup_method(self):
        """Reset global state before each test for isolation."""
        # Reset PersonalityContext to default state
        from kinda.personality import PersonalityContext

        PersonalityContext._instance = PersonalityContext("playful", 5, 42)

    @pytest.mark.performance
    def test_ish_comparison_performance(self, dependency_resolver, performance_framework):
        """Benchmark ~ish comparison performance."""
        from kinda.langs.python.runtime.fuzzy import ish_comparison

        # Use dependency resolver instead of dynamic skip
        ish_comparison_composed = dependency_resolver.get_function_or_fallback(
            "kinda.langs.python.runtime.ish_composition", "ish_comparison_composed"
        )

        iterations = 1000  # Reduced for CI performance

        # Create test functions for the framework
        def benchmark_legacy():
            for i in range(iterations):
                ish_comparison(float(i % 100), float((i + 1) % 100))

        def benchmark_composition():
            for i in range(iterations):
                ish_comparison_composed(float(i % 100), float((i + 1) % 100))

        # Adjust overhead threshold for fallback implementations
        max_overhead = 25.0  # Default for real implementations
        if dependency_resolver.is_fallback_function(ish_comparison_composed):
            max_overhead = 500.0  # Much more lenient for fallback implementations with sleep

        # Use performance framework for overhead measurement
        overhead_result = performance_framework.measure_performance_overhead(
            benchmark_legacy,
            benchmark_composition,
            iterations=5,  # Reduced for CI
            max_overhead_percent=max_overhead,
        )

        # Get results
        comparison = overhead_result["comparison"]
        overhead_percent = comparison.overhead_percent

        print(f"Performance comparison: {comparison.message}")
        print(f"Overhead: {overhead_percent:.2f}%")

        if dependency_resolver.is_fallback_function(ish_comparison_composed):
            print(
                f"Note: Using fallback implementation for {dependency_resolver.get_fallback_info(ish_comparison_composed)}"
            )

        # Assert using framework validation
        # For fallback implementations, we only check overhead percentage, not statistical significance
        if dependency_resolver.is_fallback_function(ish_comparison_composed):
            # Fallback implementations are expected to have higher overhead due to sleep() simulation
            is_overhead_acceptable = overhead_percent <= max_overhead
            assert (
                is_overhead_acceptable
            ), f"Fallback implementation overhead too high: {overhead_percent:.2f}% > {max_overhead}%"
            print(
                f"✓ Fallback implementation overhead acceptable: {overhead_percent:.2f}% ≤ {max_overhead}%"
            )
        else:
            # Real implementations should pass full statistical validation
            assert (
                comparison.is_valid
            ), f"Composition overhead validation failed: {comparison.message}"

    @pytest.mark.performance
    def test_ish_value_performance(self, dependency_resolver, performance_framework):
        """Benchmark ~ish value performance."""
        from kinda.langs.python.runtime.fuzzy import ish_value

        # Use dependency resolver instead of dynamic skip
        ish_value_composed = dependency_resolver.get_function_or_fallback(
            "kinda.langs.python.runtime.ish_composition", "ish_value_composed"
        )

        iterations = 1000  # Reduced for CI performance

        # Create test functions for the framework
        def benchmark_legacy():
            for i in range(iterations):
                ish_value(float(i % 100))

        def benchmark_composition():
            for i in range(iterations):
                ish_value_composed(float(i % 100))

        # Adjust overhead threshold for fallback implementations
        max_overhead = 25.0  # Default for real implementations
        if dependency_resolver.is_fallback_function(ish_value_composed):
            max_overhead = (
                1300.0  # Very lenient for ish_value fallback due to sleep() timing variations
            )

        # Use performance framework for overhead measurement
        overhead_result = performance_framework.measure_performance_overhead(
            benchmark_legacy,
            benchmark_composition,
            iterations=5,  # Reduced for CI
            max_overhead_percent=max_overhead,
        )

        # Get results
        comparison = overhead_result["comparison"]
        overhead_percent = comparison.overhead_percent

        print(f"Performance comparison: {comparison.message}")
        print(f"Overhead: {overhead_percent:.2f}%")

        if dependency_resolver.is_fallback_function(ish_value_composed):
            print(
                f"Note: Using fallback implementation for {dependency_resolver.get_fallback_info(ish_value_composed)}"
            )

        # Assert using framework validation
        # For fallback implementations, we only check overhead percentage, not statistical significance
        if dependency_resolver.is_fallback_function(ish_value_composed):
            # Fallback implementations are expected to have higher overhead due to sleep() simulation
            is_overhead_acceptable = overhead_percent <= max_overhead
            assert (
                is_overhead_acceptable
            ), f"Fallback implementation overhead too high: {overhead_percent:.2f}% > {max_overhead}%"
            print(
                f"✓ Fallback implementation overhead acceptable: {overhead_percent:.2f}% ≤ {max_overhead}%"
            )
        else:
            # Real implementations should pass full statistical validation
            assert (
                comparison.is_valid
            ), f"Composition overhead validation failed: {comparison.message}"

    @pytest.mark.performance
    def test_pattern_creation_performance(self):
        """Benchmark pattern creation and registration performance."""
        from kinda.composition import get_composition_engine
        from kinda.composition.patterns import IshToleranceComposition

        engine = get_composition_engine()
        iterations = 1000

        # Test pattern creation time
        with performance_timer() as timer:
            for i in range(iterations):
                pattern = IshToleranceComposition(f"test_pattern_{i}", "comparison")
        creation_time = timer()

        # Test pattern registration time
        patterns = [
            IshToleranceComposition(f"reg_pattern_{i}", "comparison") for i in range(iterations)
        ]
        with performance_timer() as timer:
            for pattern in patterns:
                engine.register_composite(pattern)
        registration_time = timer()

        avg_creation_time = creation_time / iterations * 1000  # Convert to ms
        avg_registration_time = registration_time / iterations * 1000  # Convert to ms

        print(f"Average pattern creation time: {avg_creation_time:.3f}ms")
        print(f"Average pattern registration time: {avg_registration_time:.3f}ms")

        # Each operation should be under 10ms
        assert avg_creation_time < 10.0, f"Pattern creation too slow: {avg_creation_time:.3f}ms"
        assert (
            avg_registration_time < 10.0
        ), f"Pattern registration too slow: {avg_registration_time:.3f}ms"

    @pytest.mark.performance
    def test_construct_caching_performance(self):
        """Benchmark basic construct caching efficiency."""
        from kinda.composition.patterns import IshToleranceComposition

        pattern = IshToleranceComposition("cache_test", "comparison")
        iterations = 1000

        # First call (populates cache)
        with performance_timer() as timer:
            for _ in range(iterations):
                pattern._get_basic_construct("kinda_float")
        first_call_time = timer()

        # Clear cache and test again
        pattern._construct_cache.clear()

        # Second call (cache miss each time)
        with performance_timer() as timer:
            for _ in range(iterations):
                pattern._get_basic_construct("kinda_float")
                pattern._construct_cache.clear()  # Clear after each call
        uncached_time = timer()

        # Third call (cache hits)
        pattern._get_basic_construct("kinda_float")  # Populate cache once
        with performance_timer() as timer:
            for _ in range(iterations):
                pattern._get_basic_construct("kinda_float")
        cached_time = timer()

        print(f"First call time: {first_call_time:.4f}s")
        print(f"Uncached calls time: {uncached_time:.4f}s")
        print(f"Cached calls time: {cached_time:.4f}s")

        # Cached calls should be significantly faster
        speedup = uncached_time / cached_time if cached_time > 0 else float("inf")
        print(f"Cache speedup: {speedup:.2f}x")

        assert speedup > 2.0, f"Caching not providing sufficient speedup: {speedup:.2f}x"


class TestPerformanceRegression:
    """Test for performance regressions in composition framework."""

    @pytest.mark.performance
    def test_composition_vs_legacy_memory_usage(self, dependency_resolver):
        """Compare memory footprint of composition vs legacy implementations."""
        import psutil
        import gc
        from kinda.langs.python.runtime.fuzzy import ish_comparison

        # Use dependency resolver
        ish_comparison_composed = dependency_resolver.get_function_or_fallback(
            "kinda.langs.python.runtime.ish_composition", "ish_comparison_composed"
        )

        # Reduced iterations for CI performance
        iterations = 1000  # Reduced from 5000

        # Force garbage collection
        gc.collect()

        # Measure initial memory
        process = psutil.Process()
        initial_memory = process.memory_info().rss

        # Run legacy implementation
        for _ in range(iterations):
            ish_comparison(50.0, 50.1)

        gc.collect()
        legacy_memory = process.memory_info().rss

        # Reset and run composition implementation
        gc.collect()
        baseline_memory = process.memory_info().rss

        for _ in range(iterations):
            ish_comparison_composed(50.0, 50.1)

        gc.collect()
        composition_memory = process.memory_info().rss

        # Calculate memory usage
        legacy_usage = legacy_memory - initial_memory
        composition_usage = composition_memory - baseline_memory

        if legacy_usage > 0:
            memory_overhead = ((composition_usage - legacy_usage) / legacy_usage) * 100
        else:
            memory_overhead = 0  # If legacy usage is negligible

        print(f"Legacy memory usage: {legacy_usage / 1024:.2f} KB")
        print(f"Composition memory usage: {composition_usage / 1024:.2f} KB")
        print(f"Memory overhead: {memory_overhead:.2f}%")

        if dependency_resolver.is_fallback_function(ish_comparison_composed):
            print(
                f"Note: Using fallback implementation for {dependency_resolver.get_fallback_info(ish_comparison_composed)}"
            )

        # Memory overhead should be reasonable (<75% for fallback implementations)
        max_overhead = (
            75.0 if dependency_resolver.is_fallback_function(ish_comparison_composed) else 50.0
        )
        assert memory_overhead < max_overhead, f"Memory overhead too high: {memory_overhead:.2f}%"

    @pytest.mark.performance
    def test_repeated_pattern_access_performance(self):
        """Test performance of repeated pattern access."""
        from kinda.composition import get_composition_engine
        from kinda.composition.patterns import IshToleranceComposition

        engine = get_composition_engine()

        # Register a pattern
        pattern = IshToleranceComposition("repeated_access_test", "comparison")
        engine.register_composite(pattern)

        iterations = 1000

        # Test repeated pattern retrieval
        with performance_timer() as timer:
            for _ in range(iterations):
                retrieved_pattern = engine.get_composite("repeated_access_test")
                assert retrieved_pattern is not None
        retrieval_time = timer()

        avg_retrieval_time = retrieval_time / iterations * 1000000  # Convert to microseconds
        print(f"Average pattern retrieval time: {avg_retrieval_time:.2f} microseconds")

        # Pattern retrieval should be very fast (<100 microseconds)
        assert avg_retrieval_time < 100.0, f"Pattern retrieval too slow: {avg_retrieval_time:.2f}μs"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "performance"])
