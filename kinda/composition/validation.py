# kinda/composition/validation.py

"""
Kinda-Lang Composition Validation System

Provides dependency validation and performance monitoring for composite constructs.
"""

import time
from typing import List, Dict, Any, Set, Optional
from kinda.composition.framework import CompositeConstruct


class DependencyValidator:
    """Validates construct dependencies and loading order."""

    def __init__(self):
        self.dependency_graph = {}
        self.validation_cache = {}

    def register_dependencies(self, construct_name: str, deps: List[str]):
        """Register dependencies for a construct."""
        self.dependency_graph[construct_name] = deps

    def validate_construct_dependencies(self, construct_names: List[str]) -> bool:
        """Validate that all required constructs are available."""

        cache_key = tuple(sorted(construct_names))
        if cache_key in self.validation_cache:
            return self.validation_cache[cache_key]

        missing = []
        for construct in construct_names:
            # Check in globals first
            if construct not in globals():
                # Try importing from kinda runtime
                available = False
                try:
                    from kinda.langs.python.runtime import fuzzy

                    if hasattr(fuzzy, construct):
                        available = True
                except ImportError:
                    pass

                # Try checking in kinda.personality for basic constructs
                if not available:
                    try:
                        from kinda.personality import chaos_probability

                        # If we can get a probability for it, the construct exists
                        chaos_probability(construct)
                        available = True
                    except Exception:
                        pass

                if not available:
                    missing.append(construct)

        is_valid = len(missing) == 0
        self.validation_cache[cache_key] = is_valid

        if not is_valid:
            print(f"[validation] Missing required constructs: {missing}")

        return is_valid

    def get_dependency_chain(self, construct_name: str) -> List[str]:
        """Get full dependency chain for a construct."""

        chain = []
        to_visit = [construct_name]
        visited = set()

        while to_visit:
            current = to_visit.pop(0)
            if current in visited:
                continue

            visited.add(current)
            chain.append(current)

            if current in self.dependency_graph:
                for dep in self.dependency_graph[current]:
                    if dep not in visited:
                        to_visit.append(dep)

        return chain[1:]  # Exclude the construct itself

    def detect_circular_dependencies(self) -> List[str]:
        """Detect circular dependencies in construct graph."""

        def visit(node, path, visited):
            if node in path:
                # Found circular dependency
                cycle_start = path.index(node)
                return path[cycle_start:] + [node]

            if node in visited:
                return None

            visited.add(node)
            path.append(node)

            for dep in self.dependency_graph.get(node, []):
                cycle = visit(dep, path[:], visited)
                if cycle:
                    return cycle

            return None

        visited = set()
        for construct in self.dependency_graph:
            if construct not in visited:
                cycle = visit(construct, [], visited)
                if cycle:
                    return cycle

        return []

    def validate_loading_order(self, constructs: List[str]) -> bool:
        """Validate that constructs are loaded in proper dependency order."""

        # Build reverse dependency map
        dependents = {}
        for construct, deps in self.dependency_graph.items():
            for dep in deps:
                if dep not in dependents:
                    dependents[dep] = []
                dependents[dep].append(construct)

        # Check that all dependencies appear before their dependents
        seen = set()
        for construct in constructs:
            # Check if all dependencies of this construct have been seen
            deps = self.dependency_graph.get(construct, [])
            missing_deps = [dep for dep in deps if dep not in seen]

            if missing_deps:
                print(f"[validation] {construct} loaded before dependencies: {missing_deps}")
                return False

            seen.add(construct)

        return True


class PerformanceValidator:
    """Validates performance characteristics of compositions."""

    def __init__(self):
        self.performance_baselines = {}
        self.overhead_measurements = {}

    def establish_baseline(self, construct_name: str, iterations: int = 1000) -> float:
        """Establish performance baseline for a basic construct."""

        if construct_name in self.performance_baselines:
            return self.performance_baselines[construct_name]

        construct_func = globals().get(construct_name)
        if construct_func is None:
            # Try importing from kinda runtime
            try:
                from kinda.langs.python.runtime import fuzzy

                construct_func = getattr(fuzzy, construct_name, None)
            except ImportError:
                pass

        if not construct_func:
            return 0.0

        start_time = time.perf_counter()

        for _ in range(iterations):
            try:
                construct_func(True)
            except Exception:
                pass  # Ignore errors for baseline measurement

        total_time = time.perf_counter() - start_time
        baseline = total_time / iterations

        self.performance_baselines[construct_name] = baseline
        return baseline

    def measure_composition_overhead(
        self, composite: CompositeConstruct, iterations: int = 1000
    ) -> float:
        """Measure overhead of composition vs basic constructs."""

        # Measure composite performance
        start_time = time.perf_counter()

        for _ in range(iterations):
            try:
                composite.compose(True)
            except Exception:
                pass

        composite_time = (time.perf_counter() - start_time) / iterations

        # Calculate baseline time from dependencies
        total_baseline = 0.0
        for dep in composite.get_basic_constructs():
            baseline = self.establish_baseline(dep)
            total_baseline += baseline

        if total_baseline > 0:
            overhead_ratio = (composite_time - total_baseline) / total_baseline
        else:
            overhead_ratio = 0.0

        self.overhead_measurements[composite.name] = {
            "composite_time": composite_time,
            "baseline_time": total_baseline,
            "overhead_ratio": overhead_ratio,
        }

        return overhead_ratio

    def validate_performance_target(
        self, composite: CompositeConstruct, max_overhead: float = 0.20
    ) -> bool:
        """Validate that composition meets performance targets."""

        overhead = self.measure_composition_overhead(composite)
        meets_target = overhead <= max_overhead

        if not meets_target:
            print(
                f"[performance] {composite.name} overhead {overhead:.1%} "
                f"exceeds target {max_overhead:.1%}"
            )

        return meets_target

    def benchmark_against_existing(
        self, composite: CompositeConstruct, comparison_construct: str = None
    ) -> Dict[str, Any]:
        """Benchmark composite against existing construct performance."""

        # Measure composite performance
        composite_perf = self._measure_construct_performance(composite.compose, iterations=1000)

        results = {"composite_performance": composite_perf, "composite_name": composite.name}

        if comparison_construct:
            # Try to find the comparison construct
            comparison_func = globals().get(comparison_construct)
            if comparison_func is None:
                try:
                    from kinda.langs.python.runtime import fuzzy

                    comparison_func = getattr(fuzzy, comparison_construct, None)
                except ImportError:
                    pass

            if comparison_func:
                comparison_perf = self._measure_construct_performance(
                    comparison_func, iterations=1000
                )
                results["comparison_performance"] = comparison_perf
                results["comparison_name"] = comparison_construct

                if comparison_perf > 0:
                    results["relative_performance"] = composite_perf / comparison_perf
                    results["performance_ratio"] = f"{results['relative_performance']:.2f}x"

        # Compare with basic construct baselines
        baseline_perfs = []
        for dep in composite.get_basic_constructs():
            dep_perf = self.establish_baseline(dep, iterations=100)  # Smaller sample for comparison
            if dep_perf > 0:
                baseline_perfs.append(dep_perf)

        if baseline_perfs:
            total_baseline = sum(baseline_perfs)
            results["baseline_performance"] = total_baseline
            results["overhead_ratio"] = (composite_perf - total_baseline) / total_baseline
            results["meets_target"] = results["overhead_ratio"] <= 0.20

        return results

    def _measure_construct_performance(self, func: callable, iterations: int = 1000) -> float:
        """Measure performance of a single construct function."""
        start_time = time.perf_counter()

        for _ in range(iterations):
            try:
                func(True)
            except Exception:
                pass  # Ignore errors during performance measurement

        total_time = time.perf_counter() - start_time
        return total_time / iterations

    def generate_performance_report(self) -> str:
        """Generate comprehensive performance report."""
        if not self.overhead_measurements:
            return "[performance] No performance measurements available\n"

        report = "[performance] Performance Validation Report\n"
        report += "=" * 50 + "\n\n"

        report += "Composition Overhead Analysis:\n"
        report += "-" * 30 + "\n"

        for construct_name, measurements in self.overhead_measurements.items():
            report += f"{construct_name}:\n"
            report += f"  Composite Time:  {measurements['composite_time']:.6f}s\n"
            report += f"  Baseline Time:   {measurements['baseline_time']:.6f}s\n"
            report += f"  Overhead Ratio:  {measurements['overhead_ratio']:.1%}\n"

            if measurements["overhead_ratio"] <= 0.20:
                report += f"  Status:          PASS (within 20% target)\n"
            else:
                report += f"  Status:          FAIL (exceeds 20% target)\n"

            report += "\n"

        if self.performance_baselines:
            report += "Basic Construct Baselines:\n"
            report += "-" * 30 + "\n"

            for construct, baseline in self.performance_baselines.items():
                report += f"{construct}: {baseline:.6f}s\n"

        return report


# Global instances for framework use
dependency_validator = DependencyValidator()
performance_validator = PerformanceValidator()


def validate_construct_dependencies(construct_names: List[str]) -> bool:
    """Convenience function for dependency validation."""
    return dependency_validator.validate_construct_dependencies(construct_names)


def validate_performance_target(composite: CompositeConstruct, max_overhead: float = 0.20) -> bool:
    """Convenience function for performance validation."""
    return performance_validator.validate_performance_target(composite, max_overhead)


def register_construct_dependencies(construct_name: str, dependencies: List[str]):
    """Register dependencies for a construct in the global validator."""
    dependency_validator.register_dependencies(construct_name, dependencies)


def establish_performance_baseline(construct_name: str, iterations: int = 1000) -> float:
    """Establish performance baseline for a construct."""
    return performance_validator.establish_baseline(construct_name, iterations)


def validate_composition_integrity(composite: CompositeConstruct) -> Dict[str, Any]:
    """Comprehensive validation of composition integrity."""

    results = {
        "construct_name": composite.name,
        "validation_timestamp": time.time(),
        "tests_passed": 0,
        "tests_total": 0,
        "issues": [],
    }

    # Test 1: Dependency validation
    results["tests_total"] += 1
    deps_valid = validate_construct_dependencies(composite.get_basic_constructs())
    results["dependency_validation"] = deps_valid
    if deps_valid:
        results["tests_passed"] += 1
    else:
        results["issues"].append("Missing or unavailable dependencies")

    # Test 2: Performance validation
    results["tests_total"] += 1
    perf_valid = validate_performance_target(composite)
    results["performance_validation"] = perf_valid
    if perf_valid:
        results["tests_passed"] += 1
    else:
        results["issues"].append("Performance overhead exceeds 20% target")

    # Test 3: Circular dependency detection
    results["tests_total"] += 1
    register_construct_dependencies(composite.name, composite.get_basic_constructs())
    circular_deps = dependency_validator.detect_circular_dependencies()
    results["circular_dependencies"] = circular_deps
    if not circular_deps:
        results["tests_passed"] += 1
    else:
        results["issues"].append(f"Circular dependencies detected: {circular_deps}")

    # Test 4: Basic execution test
    results["tests_total"] += 1
    try:
        # Try a simple execution to ensure basic functionality works
        composite.compose(True)
        results["execution_test"] = True
        results["tests_passed"] += 1
    except Exception as e:
        results["execution_test"] = False
        results["issues"].append(f"Basic execution failed: {str(e)}")

    # Calculate overall health score
    results["health_score"] = results["tests_passed"] / results["tests_total"]
    results["overall_status"] = "PASS" if results["health_score"] >= 0.75 else "FAIL"

    return results
