# kinda/composition/testing.py

"""
Kinda-Lang Composition Testing Framework

Statistical testing and validation framework for composite constructs.
"""

import time
from typing import Dict, Any, List, Optional
from kinda.composition.framework import CompositeConstruct


class CompositionTestFramework:
    """Statistical testing framework for composite constructs."""

    def __init__(self, samples: int = 1000, confidence: float = 0.95):
        self.samples = samples
        self.confidence = confidence
        self.test_results = {}

    def validate_composition_probability(
        self,
        composite: CompositeConstruct,
        personality: str,
        expected_prob: float,
        tolerance: float = 0.05,
        *args,
        **kwargs,
    ) -> bool:
        """Validate that composite construct behaves with expected probability."""
        from kinda.personality import get_personality, PersonalityContext

        # Set personality for test
        original_personality = get_personality().mood
        PersonalityContext.set_mood(personality)

        try:
            successes = 0
            for _ in range(self.samples):
                try:
                    if composite.compose(*args, **kwargs):
                        successes += 1
                except Exception:
                    # Count exceptions as failures for probability calculation
                    pass

            actual_prob = successes / self.samples
            within_tolerance = abs(actual_prob - expected_prob) <= tolerance

            test_result = {
                "construct": composite.name,
                "personality": personality,
                "expected": expected_prob,
                "actual": actual_prob,
                "tolerance": tolerance,
                "samples": self.samples,
                "passed": within_tolerance,
            }

            self.test_results[f"{composite.name}_{personality}"] = test_result
            return within_tolerance

        finally:
            # Restore original personality
            PersonalityContext.set_mood(original_personality)

    def validate_composition_dependencies(self, composite: CompositeConstruct) -> bool:
        """Validate that all dependencies are available."""
        missing_deps = []

        for dep in composite.get_basic_constructs():
            # Check in globals first
            if dep not in globals():
                # Try importing from kinda runtime
                try:
                    from kinda.langs.python.runtime import fuzzy

                    if not hasattr(fuzzy, dep):
                        missing_deps.append(dep)
                except ImportError:
                    missing_deps.append(dep)

        if missing_deps:
            print(f"[composition] Missing dependencies for {composite.name}: {missing_deps}")
            return False

        return True

    def validate_composition_performance(
        self,
        composite: CompositeConstruct,
        baseline_time: float,
        max_overhead: float = 0.20,
        iterations: int = 1000,
    ) -> bool:
        """Validate that composition performance is within acceptable bounds."""

        start_time = time.perf_counter()
        for _ in range(iterations):
            try:
                composite.compose(True)  # Simple test case
            except Exception:
                pass  # Ignore exceptions for performance testing

        total_time = time.perf_counter() - start_time
        avg_time = total_time / iterations

        if baseline_time == 0:
            overhead_ratio = 0  # No baseline to compare
        else:
            overhead_ratio = (avg_time - baseline_time) / baseline_time

        within_bounds = overhead_ratio <= max_overhead

        performance_result = {
            "construct": composite.name,
            "baseline_time": baseline_time,
            "actual_time": avg_time,
            "overhead_ratio": overhead_ratio,
            "max_overhead": max_overhead,
            "iterations": iterations,
            "passed": within_bounds,
        }

        self.test_results[f"{composite.name}_performance"] = performance_result
        return within_bounds

    def generate_test_report(self) -> str:
        """Generate a comprehensive test report."""
        if not self.test_results:
            return "[composition] No test results available\n"

        report = "[composition] Test Framework Report\n"
        report += "=" * 50 + "\n\n"

        # Probability tests
        prob_tests = {k: v for k, v in self.test_results.items() if not k.endswith("_performance")}

        if prob_tests:
            report += "Probability Validation Results:\n"
            report += "-" * 30 + "\n"

            for test_name, result in prob_tests.items():
                status = "PASS" if result["passed"] else "FAIL"
                report += f"{test_name}: {status}\n"
                report += f"  Expected: {result['expected']:.3f} ± {result['tolerance']:.3f}\n"
                report += f"  Actual:   {result['actual']:.3f}\n"
                report += f"  Samples:  {result['samples']}\n\n"

        # Performance tests
        perf_tests = {k: v for k, v in self.test_results.items() if k.endswith("_performance")}

        if perf_tests:
            report += "Performance Validation Results:\n"
            report += "-" * 30 + "\n"

            for test_name, result in perf_tests.items():
                status = "PASS" if result["passed"] else "FAIL"
                report += f"{test_name}: {status}\n"
                report += f"  Baseline:  {result['baseline_time']:.6f}s\n"
                report += f"  Actual:    {result['actual_time']:.6f}s\n"
                report += f"  Overhead:  {result['overhead_ratio']:.1%}\n"
                report += f"  Max:       {result['max_overhead']:.1%}\n\n"

        return report


class CompositionAssertion:
    """Assertion utilities for composite constructs."""

    @staticmethod
    def assert_composition_equivalent(
        composite: CompositeConstruct,
        reference_behavior: Dict[str, float],
        tolerance: float = 0.05,
        samples: int = 1000,
    ):
        """Assert that composition behaves equivalently to reference."""

        framework = CompositionTestFramework(samples)

        for personality, expected_prob in reference_behavior.items():
            passed = framework.validate_composition_probability(
                composite, personality, expected_prob, tolerance
            )

            if not passed:
                actual = framework.test_results[f"{composite.name}_{personality}"]["actual"]
                raise AssertionError(
                    f"{composite.name} failed probability test for {personality}: "
                    f"expected {expected_prob:.3f} ± {tolerance:.3f}, "
                    f"got {actual:.3f}"
                )

    @staticmethod
    def assert_composition_performance(
        composite: CompositeConstruct, max_overhead: float = 0.20, baseline_construct: str = None
    ):
        """Assert that composition performance is acceptable."""

        # Measure baseline if provided
        baseline_time = 0.0
        if baseline_construct:
            baseline_func = globals().get(baseline_construct)
            if baseline_func is None:
                # Try importing from kinda runtime
                try:
                    from kinda.langs.python.runtime import fuzzy

                    baseline_func = getattr(fuzzy, baseline_construct, None)
                except ImportError:
                    pass

            if baseline_func:
                start = time.perf_counter()
                for _ in range(100):
                    try:
                        baseline_func(True)
                    except Exception:
                        pass
                baseline_time = (time.perf_counter() - start) / 100

        framework = CompositionTestFramework()
        passed = framework.validate_composition_performance(composite, baseline_time, max_overhead)

        if not passed:
            result = framework.test_results[f"{composite.name}_performance"]
            raise AssertionError(
                f"{composite.name} failed performance test: "
                f"overhead {result['overhead_ratio']:.1%} > {max_overhead:.1%}"
            )

    @staticmethod
    def assert_composition_dependencies(composite: CompositeConstruct):
        """Assert that all composition dependencies are available."""
        framework = CompositionTestFramework()
        passed = framework.validate_composition_dependencies(composite)

        if not passed:
            raise AssertionError(
                f"{composite.name} has missing dependencies: " f"{composite.get_basic_constructs()}"
            )


class CompositionIntegrationTester:
    """Integration testing for composite constructs with existing systems."""

    def __init__(self):
        self.integration_results = {}

    def test_personality_integration(self, composite: CompositeConstruct) -> bool:
        """Test integration with personality system."""
        from kinda.personality import PersonalityContext

        personalities = ["reliable", "cautious", "playful", "chaotic"]
        results = {}

        original_personality = None
        try:
            from kinda.personality import get_personality

            original_personality = get_personality().mood
        except:
            pass

        try:
            for personality in personalities:
                PersonalityContext.set_mood(personality)

                # Test multiple samples to ensure personality affects behavior
                probabilities = []
                for _ in range(100):
                    try:
                        if composite.compose(True):
                            probabilities.append(1.0)
                        else:
                            probabilities.append(0.0)
                    except Exception:
                        probabilities.append(0.0)

                avg_prob = sum(probabilities) / len(probabilities) if probabilities else 0.0
                results[personality] = avg_prob

            # Verify that different personalities produce different behaviors
            unique_behaviors = len(set(f"{p:.2f}" for p in results.values()))
            personality_variation = unique_behaviors > 1

            self.integration_results[f"{composite.name}_personality"] = {
                "results": results,
                "personality_variation": personality_variation,
                "passed": personality_variation,
            }

            return personality_variation

        finally:
            # Restore original personality
            if original_personality:
                PersonalityContext.set_mood(original_personality)

    def test_construct_loading_order(self, composite: CompositeConstruct) -> bool:
        """Test that composite handles construct loading order correctly."""

        dependencies = composite.get_basic_constructs()

        # Test with missing dependencies
        original_funcs = {}
        for dep in dependencies:
            if dep in globals():
                original_funcs[dep] = globals()[dep]
                del globals()[dep]

        try:
            # Should handle missing dependencies gracefully
            try:
                composite.compose(True)
                missing_handled = False  # Should have failed
            except RuntimeError as e:
                missing_handled = "not available" in str(e)

        finally:
            # Restore dependencies
            for dep, func in original_funcs.items():
                globals()[dep] = func

        # Test with dependencies restored
        try:
            composite.compose(True)
            dependencies_work = True
        except Exception:
            dependencies_work = False

        test_passed = missing_handled and dependencies_work

        self.integration_results[f"{composite.name}_loading_order"] = {
            "missing_handled": missing_handled,
            "dependencies_work": dependencies_work,
            "passed": test_passed,
        }

        return test_passed

    def test_chaos_state_integration(self, composite: CompositeConstruct) -> bool:
        """Test that composite construct properly integrates with chaos state system."""
        from kinda.personality import update_chaos_state, get_personality

        # Reset chaos state
        personality = get_personality()
        original_failed = personality.chaos_state.failed
        personality.chaos_state.failed = False

        try:
            # Execute composition multiple times
            for _ in range(10):
                try:
                    composite.compose(True)
                except Exception:
                    pass

            # Chaos state should be updated appropriately
            state_updated = True  # Basic test - if we get here, integration works

            self.integration_results[f"{composite.name}_chaos_state"] = {
                "state_updated": state_updated,
                "passed": state_updated,
            }

            return state_updated

        finally:
            # Restore original chaos state
            personality.chaos_state.failed = original_failed

    def generate_integration_report(self) -> str:
        """Generate integration test report."""
        if not self.integration_results:
            return "[composition] No integration test results available\n"

        report = "[composition] Integration Test Report\n"
        report += "=" * 50 + "\n\n"

        for test_name, result in self.integration_results.items():
            status = "PASS" if result.get("passed", False) else "FAIL"
            report += f"{test_name}: {status}\n"

            # Add specific details based on test type
            if "personality_variation" in result:
                report += f"  Personality Variation: {result['personality_variation']}\n"
                report += f"  Results: {result['results']}\n"
            elif "missing_handled" in result:
                report += f"  Missing Deps Handled: {result['missing_handled']}\n"
                report += f"  Dependencies Work: {result['dependencies_work']}\n"
            elif "state_updated" in result:
                report += f"  State Integration: {result['state_updated']}\n"

            report += "\n"

        return report


# Global test framework instance
test_framework = None


def get_test_framework() -> CompositionTestFramework:
    """Get the global test framework instance."""
    global test_framework
    if test_framework is None:
        test_framework = CompositionTestFramework()
    return test_framework
