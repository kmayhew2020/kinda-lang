"""
High-level statistical assertion interface for kinda-lang testing.

This module provides user-friendly statistical assertion functions that
integrate with the confidence interval framework and pytest.
"""

from typing import Union, Optional, Dict, Any, Callable
from dataclasses import dataclass
import warnings

from .confidence import (
    ConfidenceCalculator,
    ConfidenceInterval,
    ConfidenceMethod,
    wilson_score_interval,
    bootstrap_confidence_interval,
    StatisticalFrameworkError,
)


class StatisticalValidationError(StatisticalFrameworkError, AssertionError):
    """Raised when statistical validation fails."""

    def __init__(
        self,
        observed: float,
        expected: float,
        confidence_interval: ConfidenceInterval,
        p_value: Optional[float] = None,
        context: Optional[str] = None,
    ):
        self.observed = observed
        self.expected = expected
        self.confidence_interval = confidence_interval
        self.p_value = p_value
        self.context = context

        # Create detailed error message
        message_parts = [
            f"Statistical validation failed",
            f"  Observed: {observed:.4f}",
            f"  Expected: {expected:.4f}",
            f"  {confidence_interval.confidence:.1%} CI: [{confidence_interval.lower:.4f}, {confidence_interval.upper:.4f}]",
            f"  Method: {confidence_interval.method.value}",
            f"  Sample size: {confidence_interval.sample_size}",
        ]

        if p_value is not None:
            message_parts.append(f"  p-value: {p_value:.4f}")

        if context:
            message_parts.insert(1, f"  Context: {context}")

        message = "\n" + "\n".join(message_parts)
        super().__init__(message)


@dataclass
class StatisticalConfig:
    """Configuration for statistical assertions."""

    default_confidence: float = 0.95
    default_method: str = "wilson"
    ci_environment_adjustment: float = 0.02  # More lenient in CI
    max_sample_size: int = 10000
    min_sample_size: int = 10


class StatisticalTester:
    """Main interface for statistical testing."""

    def __init__(self, config: Optional[StatisticalConfig] = None):
        self.config = config or StatisticalConfig()
        self.calculator = ConfidenceCalculator()
        self._is_ci_environment = self._detect_ci_environment()

    def statistical_assert(
        self,
        observed: Union[float, int],
        expected: float,
        n: int,
        confidence: Optional[float] = None,
        method: Optional[str] = None,
        tolerance: Optional[float] = None,
        context: Optional[str] = None,
    ) -> bool:
        """
        Statistically validate observed value against expected.

        Args:
            observed: Observed value (proportion or count)
            expected: Expected value/probability
            n: Sample size
            confidence: Confidence level (defaults to config)
            method: Statistical method (defaults to config)
            tolerance: Optional tolerance override
            context: Description for error messages

        Returns:
            True if validation passes

        Raises:
            StatisticalValidationError: If validation fails
        """
        # Apply defaults and CI adjustments
        confidence = confidence or self.config.default_confidence
        if self._is_ci_environment:
            confidence = max(0.9, confidence - self.config.ci_environment_adjustment)

        method = method or self.config.default_method

        # Convert observed to proportion if it's a count
        if isinstance(observed, int) and observed <= n:
            successes = observed
            proportion = observed / n
        else:
            proportion = float(observed)
            successes = int(proportion * n)

        # Calculate confidence interval
        ci = self.calculator.calculate_interval(successes, n, confidence, ConfidenceMethod(method))

        # Check if expected value falls within confidence interval
        if tolerance is not None:
            # Use tolerance-based validation
            is_valid = abs(proportion - expected) <= tolerance
        else:
            # Use confidence interval validation
            is_valid = ci.contains(expected)

        if not is_valid:
            # Calculate p-value for additional context
            p_value = self._calculate_p_value(successes, n, expected)
            raise StatisticalValidationError(proportion, expected, ci, p_value, context)

        return True

    def binomial_assert(
        self,
        successes: int,
        trials: int,
        expected_p: float,
        confidence: Optional[float] = None,
        two_tailed: bool = True,
        context: Optional[str] = None,
    ) -> bool:
        """
        Validate binomial proportion using confidence intervals.

        Args:
            successes: Number of successful trials
            trials: Total number of trials
            expected_p: Expected success probability
            confidence: Confidence level
            two_tailed: Whether to use two-tailed test
            context: Description for error messages

        Returns:
            True if validation passes
        """
        return self.statistical_assert(
            successes, expected_p, trials, confidence, method="wilson", context=context
        )

    def proportion_assert(
        self,
        count: int,
        total: int,
        expected_rate: float,
        confidence: Optional[float] = None,
        context: Optional[str] = None,
    ) -> bool:
        """
        Validate proportion using statistical testing.

        Args:
            count: Observed count
            total: Total possible count
            expected_rate: Expected proportion rate
            confidence: Confidence level
            context: Description for error messages

        Returns:
            True if validation passes
        """
        return self.binomial_assert(count, total, expected_rate, confidence, context=context)

    def eventually_assert(
        self,
        test_function: Callable[[], bool],
        expected_success_rate: float = 0.5,
        max_attempts: int = 100,
        confidence: Optional[float] = None,
        context: Optional[str] = None,
    ) -> bool:
        """
        Assert that test_function eventually succeeds with expected rate.

        Args:
            test_function: Function that returns True/False
            expected_success_rate: Expected success rate
            max_attempts: Maximum attempts to try
            confidence: Confidence level
            context: Description for error messages

        Returns:
            True if eventual success rate matches expectation
        """
        successes = 0
        attempts = 0

        while attempts < max_attempts:
            try:
                if test_function():
                    successes += 1
                attempts += 1
            except Exception:
                # Failed attempts don't count as successes
                attempts += 1

        return self.binomial_assert(
            successes,
            attempts,
            expected_success_rate,
            confidence,
            context=f"eventually_assert: {context}" if context else "eventually_assert",
        )

    def _calculate_p_value(self, successes: int, trials: int, expected_p: float) -> float:
        """Calculate two-tailed p-value for binomial test."""
        if trials == 0:
            return 1.0

        observed_p = successes / trials

        # Two-tailed test: calculate probability of observing this extreme or more extreme
        # This is a simplified calculation - would use scipy.stats.binom_test in practice

        from math import comb

        # Calculate exact binomial probabilities
        extreme_prob = 0.0

        for k in range(trials + 1):
            k_prob = comb(trials, k) * (expected_p**k) * ((1 - expected_p) ** (trials - k))
            k_p = k / trials

            # Include if as extreme or more extreme than observed
            if abs(k_p - expected_p) >= abs(observed_p - expected_p):
                extreme_prob += k_prob

        return min(1.0, extreme_prob)

    def _detect_ci_environment(self) -> bool:
        """Detect if running in CI environment."""
        import os

        ci_indicators = [
            "CI",
            "CONTINUOUS_INTEGRATION",
            "GITHUB_ACTIONS",
            "JENKINS_URL",
            "TRAVIS",
            "CIRCLECI",
        ]
        return any(os.environ.get(var) for var in ci_indicators)


# Global statistical tester instance
_default_tester = StatisticalTester()


def statistical_assert(
    observed: Union[float, int],
    expected: float,
    n: int,
    confidence: float = 0.95,
    method: str = "wilson",
    tolerance: Optional[float] = None,
    context: Optional[str] = None,
) -> bool:
    """Global statistical assertion function."""
    return _default_tester.statistical_assert(
        observed, expected, n, confidence, method, tolerance, context
    )


def binomial_assert(
    successes: int,
    trials: int,
    expected_p: float,
    confidence: float = 0.95,
    two_tailed: bool = True,
    context: Optional[str] = None,
) -> bool:
    """Global binomial assertion function."""
    return _default_tester.binomial_assert(
        successes, trials, expected_p, confidence, two_tailed, context
    )


def proportion_assert(
    count: int,
    total: int,
    expected_rate: float,
    confidence: float = 0.95,
    context: Optional[str] = None,
) -> bool:
    """Global proportion assertion function."""
    return _default_tester.proportion_assert(count, total, expected_rate, confidence, context)


def eventually_assert(
    test_function: Callable[[], bool],
    expected_success_rate: float = 0.5,
    max_attempts: int = 100,
    confidence: float = 0.95,
    context: Optional[str] = None,
) -> bool:
    """Global eventually assertion function."""
    return _default_tester.eventually_assert(
        test_function, expected_success_rate, max_attempts, confidence, context
    )
