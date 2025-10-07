"""Pytest plugin for performance testing framework."""

import pytest
import time
from typing import Dict, List, Optional, Callable, Any
from pathlib import Path

from .environment import EnvironmentDetector, EnvironmentContext
from .thresholds import ThresholdManager
from .dependencies import DependencyResolver
from .statistics import StatisticalValidator


class PerformanceTestFramework:
    """Main framework for performance testing."""

    def __init__(self, cache_path: Optional[Path] = None):
        self.environment_detector = EnvironmentDetector()
        self.environment = self.environment_detector.get_environment_context()
        self.threshold_manager = ThresholdManager(cache_path)
        self.dependency_resolver = DependencyResolver()
        self.statistical_validator = StatisticalValidator()
        self._test_results: Dict[str, List[float]] = {}

    def run_performance_test(
        self,
        test_name: str,
        test_function: Callable,
        iterations: int = 100,
        threshold_factor: float = 1.2,
        statistical_method: str = "robust",
        warmup_iterations: int = 5,
    ) -> Dict[str, Any]:
        """Run performance test with statistical validation."""
        environment_key = self.environment_detector.get_environment_key()

        # Adjust iterations based on CI environment
        if self.environment.ci_environment.value != "local_dev":
            # Reduce iterations in CI for faster builds
            iterations = max(10, iterations // 5)
            warmup_iterations = max(1, warmup_iterations // 2)

        # Warmup runs to stabilize performance
        for _ in range(warmup_iterations):
            try:
                test_function()
            except Exception:
                # Skip failed warmup runs
                pass

        # Collect performance samples
        samples = []
        failed_runs = 0
        max_failures = iterations // 4  # Allow up to 25% failures

        for i in range(iterations):
            try:
                elapsed_time = self._measure_execution_time(test_function)
                samples.append(elapsed_time)
            except Exception as e:
                failed_runs += 1
                if failed_runs > max_failures:
                    raise RuntimeError(
                        f"Too many failed test runs ({failed_runs}/{iterations}): {e}"
                    )

        if not samples:
            raise RuntimeError("No successful test runs collected")

        # Remove outliers to improve stability
        cleaned_samples = self._remove_outliers(samples)
        if len(cleaned_samples) < len(samples) * 0.7:  # If we removed >30%, use original
            cleaned_samples = samples

        # Calculate adaptive thresholds
        lower_threshold, upper_threshold = self.threshold_manager.calculate_threshold(
            test_name, environment_key, cleaned_samples
        )

        # Apply environment-specific threshold adjustment
        adjusted_lower = lower_threshold * self.environment.performance_multiplier
        adjusted_upper = (
            upper_threshold * self.environment.performance_multiplier * threshold_factor
        )

        # Perform statistical validation
        validation_result = self.statistical_validator.validate_performance(
            cleaned_samples, adjusted_lower, adjusted_upper, statistical_method
        )

        # Update baseline for future tests
        self.threshold_manager.update_baseline(test_name, environment_key, cleaned_samples)

        # Store results for reporting
        self._test_results[test_name] = cleaned_samples

        return {
            "samples": cleaned_samples,
            "raw_samples": samples,
            "validation": validation_result,
            "thresholds": (adjusted_lower, adjusted_upper),
            "environment": environment_key,
            "iterations_completed": len(samples),
            "iterations_failed": failed_runs,
            "outliers_removed": len(samples) - len(cleaned_samples),
        }

    def measure_performance_overhead(
        self,
        baseline_function: Callable,
        test_function: Callable,
        iterations: int = 100,
        max_overhead_percent: float = 20.0,
    ) -> Dict[str, Any]:
        """Measure performance overhead between baseline and test function."""
        # Adjust iterations for CI
        if self.environment.ci_environment.value != "local_dev":
            iterations = max(5, iterations // 5)

        # Collect baseline samples
        baseline_samples = []
        for _ in range(iterations):
            try:
                elapsed_time = self._measure_execution_time(baseline_function)
                baseline_samples.append(elapsed_time)
            except Exception:
                # Skip failed runs
                pass

        # Collect test samples
        test_samples = []
        for _ in range(iterations):
            try:
                elapsed_time = self._measure_execution_time(test_function)
                test_samples.append(elapsed_time)
            except Exception:
                # Skip failed runs
                pass

        if not baseline_samples or not test_samples:
            raise RuntimeError("Failed to collect sufficient samples for overhead measurement")

        # Remove outliers
        cleaned_baseline = self._remove_outliers(baseline_samples)
        cleaned_test = self._remove_outliers(test_samples)

        # Perform comparison
        comparison_result = self.statistical_validator.compare_performance(
            cleaned_baseline, cleaned_test, max_overhead_percent
        )

        return {
            "baseline_samples": cleaned_baseline,
            "test_samples": cleaned_test,
            "comparison": comparison_result,
            "environment": self.environment_detector.get_environment_key(),
        }

    def _measure_execution_time(self, test_function: Callable) -> float:
        """Measure execution time of test function with high precision."""
        # Use highest precision timer available
        start_time = time.perf_counter()

        try:
            test_function()
        finally:
            end_time = time.perf_counter()

        return end_time - start_time

    def _remove_outliers(self, samples: List[float], method: str = "iqr") -> List[float]:
        """Remove outliers from samples to improve stability."""
        if len(samples) < 5:
            return samples  # Not enough data for outlier detection

        outliers, outlier_indices = self.statistical_validator.detect_outliers(samples, method)

        if not outlier_indices:
            return samples

        # Remove outliers
        cleaned_samples = [samples[i] for i in range(len(samples)) if i not in outlier_indices]

        # Don't remove too many samples
        if len(cleaned_samples) >= len(samples) * 0.5:
            return cleaned_samples
        else:
            return samples

    def get_test_results(self) -> Dict[str, List[float]]:
        """Get all test results collected during session."""
        return self._test_results.copy()

    def clear_test_results(self) -> None:
        """Clear collected test results."""
        self._test_results.clear()

    def get_environment_info(self) -> Dict[str, Any]:
        """Get environment information for debugging."""
        return {
            "ci_environment": self.environment.ci_environment.value,
            "platform_family": self.environment.platform_profile.platform_family,
            "cpu_cores": self.environment.platform_profile.cpu_cores,
            "memory_gb": self.environment.platform_profile.memory_gb,
            "virtualized": self.environment.platform_profile.virtualized,
            "performance_multiplier": self.environment.performance_multiplier,
            "resource_constraints": self.environment.resource_constraints,
        }


# Pytest plugin hooks and fixtures
def pytest_configure(config):
    """Configure pytest with performance testing markers."""
    config.addinivalue_line("markers", "performance: mark test as performance test")
    config.addinivalue_line("markers", "slow: mark test as slow running test")
    config.addinivalue_line(
        "markers", "ci_unstable: mark test as potentially unstable in CI environments"
    )
    # Statistical testing markers
    config.addinivalue_line("markers", "statistical: mark test for statistical validation")
    config.addinivalue_line("markers", "probabilistic: mark test for probabilistic behavior")
    config.addinivalue_line("markers", "binomial: mark test for binomial distribution testing")


def pytest_addoption(parser):
    """Add command line options for performance testing."""
    parser.addoption(
        "--performance-cache-dir",
        action="store",
        default=".performance-cache",
        help="Directory to store performance baselines",
    )
    parser.addoption(
        "--performance-report",
        action="store",
        default=None,
        help="File to write performance test report",
    )
    parser.addoption(
        "--performance-iterations",
        action="store",
        type=int,
        default=None,
        help="Override default number of iterations for performance tests",
    )


@pytest.fixture(scope="session")
def performance_framework(request, tmp_path_factory):
    """Provide performance testing framework."""
    # Get cache directory from command line option
    cache_dir = request.config.getoption("--performance-cache-dir")
    if cache_dir:
        cache_path = Path(cache_dir) / "baselines.json"
    else:
        cache_path = tmp_path_factory.mktemp("performance-cache") / "baselines.json"

    framework = PerformanceTestFramework(cache_path)

    # Store framework for cleanup
    request.session._performance_framework = framework

    return framework


@pytest.fixture(scope="session")
def dependency_resolver():
    """Provide dependency resolver for tests."""
    return DependencyResolver()


@pytest.fixture(scope="function")
def performance_test_config(request):
    """Provide performance test configuration."""
    # Get iterations from command line or test marker
    iterations = request.config.getoption("--performance-iterations")

    # Check if test has performance marker with custom config
    marker = request.node.get_closest_marker("performance")
    if marker and marker.kwargs:
        config = marker.kwargs
        if iterations is None:
            iterations = config.get("iterations", 100)
    else:
        iterations = iterations or 100

    return {
        "iterations": iterations,
        "warmup_iterations": max(1, iterations // 20),
        "threshold_factor": 1.2,
        "statistical_method": "robust",
    }


# Statistical Testing Fixtures
@pytest.fixture(scope="function")
def statistical_tester():
    """Provide statistical tester for test functions."""
    from .assertions import StatisticalTester

    return StatisticalTester()


@pytest.fixture(scope="function")
def distribution_tester():
    """Provide distribution tester for test functions."""
    from .distributions import DistributionTester

    return DistributionTester()


@pytest.fixture(scope="session")
def confidence_calculator():
    """Provide confidence interval calculator for test sessions."""
    from .confidence import ConfidenceCalculator

    return ConfidenceCalculator()


@pytest.fixture(scope="function")
def statistical_config(request):
    """Provide statistical test configuration."""
    # Get configuration from statistical marker if present
    marker = request.node.get_closest_marker("statistical")
    config = {}

    if marker and marker.kwargs:
        config = marker.kwargs

    # Default configuration with marker overrides
    return {
        "confidence": config.get("confidence", 0.95),
        "method": config.get("method", "wilson"),
        "tolerance": config.get("tolerance", None),
        "max_attempts": config.get("max_attempts", 100),
        "context": config.get("context", "statistical test validation"),
    }


def pytest_runtest_setup(item):
    """Setup for performance tests."""
    # Check if this is a performance test
    if item.get_closest_marker("performance"):
        # Could add performance-specific setup here
        pass


def pytest_runtest_teardown(item):
    """Teardown for performance tests."""
    # Check if this is a performance test
    if item.get_closest_marker("performance"):
        # Could add performance-specific cleanup here
        pass


def pytest_sessionfinish(session, exitstatus):
    """Generate performance report at end of session."""
    if hasattr(session, "_performance_framework"):
        framework = session._performance_framework

        # Get report file from command line option
        report_file = session.config.getoption("--performance-report")
        if report_file:
            _generate_performance_report(framework, report_file)


def _generate_performance_report(framework: PerformanceTestFramework, report_file: str):
    """Generate JSON performance report."""
    import json

    try:
        test_results = framework.get_test_results()
        environment_info = framework.get_environment_info()

        report = {
            "environment": environment_info,
            "test_results": {
                test_name: {
                    "samples": samples,
                    "median": __import__("statistics").median(samples),
                    "mean": __import__("statistics").mean(samples),
                    "std": __import__("statistics").stdev(samples) if len(samples) > 1 else 0,
                    "count": len(samples),
                }
                for test_name, samples in test_results.items()
            },
            "summary": {
                "total_tests": len(test_results),
                "total_samples": sum(len(samples) for samples in test_results.values()),
            },
        }

        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

    except Exception as e:
        print(f"Warning: Failed to generate performance report: {e}")


# Utility decorators for performance tests
def performance_test(
    iterations: int = 100,
    threshold_factor: float = 1.2,
    statistical_method: str = "robust",
    max_overhead_percent: Optional[float] = None,
):
    """Decorator for performance tests."""

    def decorator(test_func):
        # Add performance marker
        test_func = pytest.mark.performance(
            iterations=iterations,
            threshold_factor=threshold_factor,
            statistical_method=statistical_method,
            max_overhead_percent=max_overhead_percent,
        )(test_func)

        return test_func

    return decorator
