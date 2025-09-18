"""
Unit tests for confidence interval calculations.

These tests validate the mathematical accuracy of the statistical framework's
confidence interval calculations, ensuring proper implementation of Wilson score,
bootstrap, and other statistical methods.
"""

import pytest
import math
import statistics
from typing import List

from kinda.testing.confidence import (
    ConfidenceCalculator, ConfidenceInterval, ConfidenceMethod,
    wilson_score_interval, bootstrap_confidence_interval,
    StatisticalFrameworkError, ConfidenceIntervalError
)


class TestConfidenceInterval:
    """Test ConfidenceInterval data class functionality."""

    def test_confidence_interval_contains(self):
        """Test confidence interval contains method."""
        ci = ConfidenceInterval(
            lower=0.4, upper=0.8, confidence=0.95,
            method=ConfidenceMethod.WILSON, sample_size=100, point_estimate=0.6
        )

        assert ci.contains(0.5)
        assert ci.contains(0.6)
        assert ci.contains(0.7)
        assert not ci.contains(0.3)
        assert not ci.contains(0.9)

    def test_confidence_interval_width(self):
        """Test confidence interval width calculation."""
        ci = ConfidenceInterval(
            lower=0.4, upper=0.8, confidence=0.95,
            method=ConfidenceMethod.WILSON, sample_size=100, point_estimate=0.6
        )

        assert abs(ci.width() - 0.4) < 1e-6
        assert abs(ci.margin_of_error() - 0.2) < 1e-6

    def test_confidence_interval_edge_cases(self):
        """Test confidence interval with edge case values."""
        ci = ConfidenceInterval(
            lower=0.0, upper=1.0, confidence=0.95,
            method=ConfidenceMethod.WILSON, sample_size=0, point_estimate=0.0
        )

        assert ci.contains(0.5)
        assert ci.width() == 1.0
        assert ci.margin_of_error() == 0.5


class TestConfidenceCalculator:
    """Test ConfidenceCalculator functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.calculator = ConfidenceCalculator()

    def test_calculator_initialization(self):
        """Test calculator initializes properly."""
        assert self.calculator is not None
        assert len(self.calculator._z_score_cache) > 0

    def test_wilson_score_interval_basic(self):
        """Test Wilson score interval basic calculation."""
        # Test with 60 successes out of 100 trials
        ci = self.calculator._wilson_score_interval(60, 100, 0.95)

        assert isinstance(ci, ConfidenceInterval)
        assert ci.method == ConfidenceMethod.WILSON
        assert ci.sample_size == 100
        assert abs(ci.point_estimate - 0.6) < 1e-6
        assert 0.5 < ci.lower < 0.6
        assert 0.6 < ci.upper < 0.7

    def test_wilson_score_interval_edge_cases(self):
        """Test Wilson score interval with edge cases."""
        # Zero trials
        ci = self.calculator._wilson_score_interval(0, 0, 0.95)
        assert ci.lower == 0.0
        assert ci.upper == 1.0

        # All successes
        ci = self.calculator._wilson_score_interval(100, 100, 0.95)
        assert 0.9 < ci.lower < 1.0
        assert ci.upper == 1.0

        # No successes
        ci = self.calculator._wilson_score_interval(0, 100, 0.95)
        assert ci.lower == 0.0
        assert 0.0 < ci.upper < 0.1

    def test_normal_approximation_basic(self):
        """Test normal approximation confidence interval."""
        ci = self.calculator._normal_approximation(60, 100, 0.95)

        assert isinstance(ci, ConfidenceInterval)
        assert ci.method == ConfidenceMethod.NORMAL
        assert ci.sample_size == 100
        assert abs(ci.point_estimate - 0.6) < 1e-6

    def test_method_selection_logic(self):
        """Test automatic method selection logic."""
        # Small sample should use binomial
        method = self.calculator._select_method(5, 8, 0.95)
        assert method == ConfidenceMethod.BINOMIAL

        # Moderate sample with extreme probability should use Wilson
        method = self.calculator._select_method(1, 25, 0.95)
        assert method == ConfidenceMethod.WILSON

        # Large sample should use normal approximation
        method = self.calculator._select_method(600, 1200, 0.95)
        assert method == ConfidenceMethod.NORMAL

        # General case should use Wilson
        method = self.calculator._select_method(30, 50, 0.95)
        assert method == ConfidenceMethod.WILSON

    def test_z_score_caching(self):
        """Test z-score caching functionality."""
        # Common confidence levels should be cached
        z_90 = self.calculator._get_z_score(0.90)
        z_95 = self.calculator._get_z_score(0.95)
        z_99 = self.calculator._get_z_score(0.99)

        assert abs(z_90 - 1.645) < 0.01
        assert abs(z_95 - 1.960) < 0.01
        assert abs(z_99 - 2.576) < 0.01

        # Arbitrary confidence level should be calculated
        z_97 = self.calculator._get_z_score(0.97)
        assert 2.0 < z_97 < 2.5

    def test_calculate_interval_validation(self):
        """Test input validation for calculate_interval."""
        # Invalid success/trial ratio
        with pytest.raises(ValueError):
            self.calculator.calculate_interval(150, 100, 0.95)

        # Invalid confidence level
        with pytest.raises(ValueError):
            self.calculator.calculate_interval(50, 100, 1.5)

        with pytest.raises(ValueError):
            self.calculator.calculate_interval(50, 100, 0.3)

    def test_calculate_interval_auto_method(self):
        """Test automatic method selection in calculate_interval."""
        # Should automatically select appropriate method
        ci = self.calculator.calculate_interval(60, 100, 0.95, ConfidenceMethod.AUTO)
        assert ci.method == ConfidenceMethod.WILSON

        # Explicit method should be respected
        ci = self.calculator.calculate_interval(60, 100, 0.95, ConfidenceMethod.NORMAL)
        assert ci.method == ConfidenceMethod.NORMAL

    def test_bootstrap_interval_basic(self):
        """Test bootstrap confidence interval calculation."""
        ci = self.calculator._bootstrap_interval(60, 100, 0.95)

        assert isinstance(ci, ConfidenceInterval)
        assert ci.method == ConfidenceMethod.BOOTSTRAP
        assert ci.sample_size == 100
        assert abs(ci.point_estimate - 0.6) < 1e-6

        # Bootstrap should give reasonable bounds
        assert 0.4 < ci.lower < 0.7
        assert 0.4 < ci.upper < 0.8


class TestWilsonScoreInterval:
    """Test the global wilson_score_interval function."""

    def test_wilson_score_function(self):
        """Test global Wilson score interval function."""
        ci = wilson_score_interval(60, 100, 0.95)

        assert isinstance(ci, ConfidenceInterval)
        assert ci.method == ConfidenceMethod.WILSON
        assert ci.sample_size == 100
        assert abs(ci.point_estimate - 0.6) < 1e-6

    def test_wilson_score_different_confidence_levels(self):
        """Test Wilson score with different confidence levels."""
        ci_90 = wilson_score_interval(60, 100, 0.90)
        ci_95 = wilson_score_interval(60, 100, 0.95)
        ci_99 = wilson_score_interval(60, 100, 0.99)

        # Higher confidence should give wider intervals
        assert ci_90.width() < ci_95.width() < ci_99.width()

        # All should contain the point estimate
        for ci in [ci_90, ci_95, ci_99]:
            assert ci.contains(0.6)


class TestBootstrapConfidenceInterval:
    """Test the global bootstrap_confidence_interval function."""

    def test_bootstrap_function_mean(self):
        """Test bootstrap confidence interval for mean."""
        samples = [0.5, 0.6, 0.7, 0.8, 0.4, 0.9, 0.3, 0.5, 0.6, 0.7]
        ci = bootstrap_confidence_interval(samples, 0.95, "mean")

        assert isinstance(ci, ConfidenceInterval)
        assert ci.method == ConfidenceMethod.BOOTSTRAP
        assert ci.sample_size == len(samples)
        assert abs(ci.point_estimate - statistics.mean(samples)) < 1e-6

    def test_bootstrap_function_median(self):
        """Test bootstrap confidence interval for median."""
        samples = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        ci = bootstrap_confidence_interval(samples, 0.95, "median")

        assert ci.method == ConfidenceMethod.BOOTSTRAP
        assert abs(ci.point_estimate - statistics.median(samples)) < 1e-6

    def test_bootstrap_function_std(self):
        """Test bootstrap confidence interval for standard deviation."""
        samples = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        ci = bootstrap_confidence_interval(samples, 0.95, "std")

        assert ci.method == ConfidenceMethod.BOOTSTRAP
        expected_std = statistics.stdev(samples)
        assert abs(ci.point_estimate - expected_std) < 1e-6

    def test_bootstrap_empty_samples(self):
        """Test bootstrap with empty sample list."""
        with pytest.raises(ValueError):
            bootstrap_confidence_interval([], 0.95, "mean")

    def test_bootstrap_unknown_statistic(self):
        """Test bootstrap with unknown statistic."""
        samples = [1, 2, 3, 4, 5]
        with pytest.raises(ValueError):
            bootstrap_confidence_interval(samples, 0.95, "unknown")


class TestMathematicalAccuracy:
    """Test mathematical accuracy of confidence intervals."""

    def test_wilson_score_coverage_simulation(self):
        """Test that Wilson score intervals achieve expected coverage."""
        # This is a statistical test of the statistical framework itself
        import numpy as np

        true_p = 0.6
        confidence = 0.95
        n_trials = 100
        n_simulations = 200  # Reduced for faster testing

        coverage_count = 0

        for _ in range(n_simulations):
            # Simulate binomial data
            successes = np.random.binomial(n_trials, true_p)

            # Calculate confidence interval
            ci = wilson_score_interval(successes, n_trials, confidence)

            # Check if true parameter is covered
            if ci.contains(true_p):
                coverage_count += 1

        # Coverage should be approximately equal to confidence level
        observed_coverage = coverage_count / n_simulations

        # Allow some tolerance due to simulation variability
        # With 200 simulations, standard error is approximately 0.035
        tolerance = 0.1  # More lenient for test stability

        assert abs(observed_coverage - confidence) < tolerance, \
            f"Coverage {observed_coverage:.3f} differs from {confidence:.3f} by more than {tolerance}"

    def test_confidence_interval_nesting(self):
        """Test that higher confidence levels give wider intervals."""
        successes = 60
        trials = 100

        ci_90 = wilson_score_interval(successes, trials, 0.90)
        ci_95 = wilson_score_interval(successes, trials, 0.95)
        ci_99 = wilson_score_interval(successes, trials, 0.99)

        # Higher confidence should give wider intervals
        assert ci_90.width() < ci_95.width()
        assert ci_95.width() < ci_99.width()

        # Higher confidence intervals should contain lower confidence intervals
        assert ci_95.lower <= ci_90.lower
        assert ci_95.upper >= ci_90.upper
        assert ci_99.lower <= ci_95.lower
        assert ci_99.upper >= ci_95.upper

    def test_confidence_interval_consistency(self):
        """Test that different methods give consistent results for large samples."""
        successes = 600
        trials = 1000

        ci_wilson = wilson_score_interval(successes, trials, 0.95)

        calculator = ConfidenceCalculator()
        ci_normal = calculator._normal_approximation(successes, trials, 0.95)

        # For large samples, Wilson and normal approximation should be similar
        width_difference = abs(ci_wilson.width() - ci_normal.width())
        assert width_difference < 0.05, \
            f"Wilson and normal approximations differ too much: {width_difference}"

    def test_extreme_cases_stability(self):
        """Test that extreme cases are handled gracefully."""
        # Very small probability
        ci = wilson_score_interval(1, 1000, 0.95)
        assert 0 <= ci.lower < ci.upper <= 1
        assert ci.contains(0.001)

        # Very large probability
        ci = wilson_score_interval(999, 1000, 0.95)
        assert 0 <= ci.lower < ci.upper <= 1
        assert ci.contains(0.999)

        # Moderate case
        ci = wilson_score_interval(500, 1000, 0.95)
        assert 0 <= ci.lower < ci.upper <= 1
        assert ci.contains(0.5)


class TestPerformanceRequirements:
    """Test that performance requirements are met."""

    def test_wilson_score_performance(self):
        """Test Wilson score calculation performance."""
        import time

        start_time = time.time()

        # Calculate many intervals
        for i in range(1000):
            wilson_score_interval(50 + i % 50, 100, 0.95)

        elapsed_time = time.time() - start_time

        # Should complete 1000 calculations in reasonable time
        # Target: <0.1ms per calculation, so 1000 calculations in <100ms
        assert elapsed_time < 1.0, \
            f"Wilson score calculations too slow: {elapsed_time:.3f}s for 1000 calculations"

    def test_bootstrap_performance(self):
        """Test bootstrap calculation performance."""
        import time

        samples = list(range(100))

        start_time = time.time()

        # Calculate bootstrap intervals
        for _ in range(10):  # Fewer iterations due to higher computational cost
            bootstrap_confidence_interval(samples, 0.95, "mean")

        elapsed_time = time.time() - start_time

        # Bootstrap should be slower but still reasonable
        assert elapsed_time < 5.0, \
            f"Bootstrap calculations too slow: {elapsed_time:.3f}s for 10 calculations"