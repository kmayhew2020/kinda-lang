# Statistical Testing Framework - Implementation Specification

## Document Information

- **Version**: 1.0
- **Date**: 2025-09-18
- **Architect**: Architect Agent
- **Issue**: #125 - Statistical Testing Framework
- **Purpose**: Detailed implementation specifications for Coder Agent

## Implementation Overview

This specification provides complete technical details for implementing the Statistical Testing Framework, including function signatures, data structures, algorithms, error handling, and integration requirements.

## Module Implementation Specifications

### 1. Core Confidence Interval Module (`kinda/testing/confidence.py`)

#### Module Structure

```python
"""
Confidence interval calculations for statistical testing framework.

This module provides mathematically sound confidence interval calculations
for various statistical scenarios in probabilistic programming testing.
"""

import math
import statistics
from typing import Tuple, List, Optional, Union
from dataclasses import dataclass
from enum import Enum
import numpy as np


class ConfidenceMethod(Enum):
    """Available confidence interval calculation methods."""
    WILSON = "wilson"           # Wilson score interval
    NORMAL = "normal"           # Normal approximation
    BINOMIAL = "binomial"       # Exact binomial
    BOOTSTRAP = "bootstrap"     # Bootstrap method
    AUTO = "auto"              # Automatic method selection


@dataclass
class ConfidenceInterval:
    """Represents a confidence interval with metadata."""
    lower: float
    upper: float
    confidence: float
    method: ConfidenceMethod
    sample_size: int
    point_estimate: float

    def contains(self, value: float) -> bool:
        """Check if value falls within confidence interval."""
        return self.lower <= value <= self.upper

    def width(self) -> float:
        """Calculate confidence interval width."""
        return self.upper - self.lower

    def margin_of_error(self) -> float:
        """Calculate margin of error (half-width)."""
        return self.width() / 2.0


class ConfidenceCalculator:
    """Core confidence interval calculation engine."""

    def __init__(self):
        self._z_score_cache = self._build_z_score_cache()

    def calculate_interval(
        self,
        successes: int,
        trials: int,
        confidence: float = 0.95,
        method: Union[str, ConfidenceMethod] = ConfidenceMethod.AUTO
    ) -> ConfidenceInterval:
        """
        Calculate confidence interval for binomial proportion.

        Args:
            successes: Number of successful trials
            trials: Total number of trials
            confidence: Confidence level (0.0 to 1.0)
            method: Calculation method to use

        Returns:
            ConfidenceInterval object with bounds and metadata

        Raises:
            ValueError: Invalid input parameters
            StatisticalError: Calculation fails
        """
        # Validation
        if not 0 <= successes <= trials:
            raise ValueError(f"Invalid successes/trials: {successes}/{trials}")
        if not 0.5 <= confidence <= 0.999:
            raise ValueError(f"Confidence must be 0.5-0.999, got {confidence}")

        # Method selection
        if isinstance(method, str):
            method = ConfidenceMethod(method)

        if method == ConfidenceMethod.AUTO:
            method = self._select_method(successes, trials, confidence)

        # Calculate based on method
        if method == ConfidenceMethod.WILSON:
            return self._wilson_score_interval(successes, trials, confidence)
        elif method == ConfidenceMethod.NORMAL:
            return self._normal_approximation(successes, trials, confidence)
        elif method == ConfidenceMethod.BINOMIAL:
            return self._exact_binomial(successes, trials, confidence)
        elif method == ConfidenceMethod.BOOTSTRAP:
            return self._bootstrap_interval(successes, trials, confidence)
        else:
            raise ValueError(f"Unknown method: {method}")

    def _wilson_score_interval(
        self, successes: int, trials: int, confidence: float
    ) -> ConfidenceInterval:
        """
        Calculate Wilson score confidence interval.

        More robust than normal approximation for small samples and extreme probabilities.
        Formula: (p + z²/2n ± z√(p(1-p)/n + z²/4n²)) / (1 + z²/n)
        """
        if trials == 0:
            return ConfidenceInterval(0.0, 1.0, confidence, ConfidenceMethod.WILSON, 0, 0.0)

        p = successes / trials
        z = self._get_z_score(confidence)

        # Wilson score calculation
        n = trials
        z_squared = z * z

        center = (p + z_squared / (2 * n)) / (1 + z_squared / n)
        margin = z * math.sqrt((p * (1 - p) + z_squared / (4 * n)) / n) / (1 + z_squared / n)

        lower = max(0.0, center - margin)
        upper = min(1.0, center + margin)

        return ConfidenceInterval(
            lower=lower,
            upper=upper,
            confidence=confidence,
            method=ConfidenceMethod.WILSON,
            sample_size=trials,
            point_estimate=p
        )

    def _normal_approximation(
        self, successes: int, trials: int, confidence: float
    ) -> ConfidenceInterval:
        """Normal approximation confidence interval."""
        if trials == 0:
            return ConfidenceInterval(0.0, 1.0, confidence, ConfidenceMethod.NORMAL, 0, 0.0)

        p = successes / trials
        z = self._get_z_score(confidence)

        # Standard error
        se = math.sqrt(p * (1 - p) / trials)
        margin = z * se

        lower = max(0.0, p - margin)
        upper = min(1.0, p + margin)

        return ConfidenceInterval(
            lower=lower,
            upper=upper,
            confidence=confidence,
            method=ConfidenceMethod.NORMAL,
            sample_size=trials,
            point_estimate=p
        )

    def _exact_binomial(
        self, successes: int, trials: int, confidence: float
    ) -> ConfidenceInterval:
        """Exact binomial confidence interval (Clopper-Pearson)."""
        # Implementation using beta distribution quantiles
        # This is computationally intensive but exact
        alpha = 1 - confidence

        if successes == 0:
            lower = 0.0
            upper = self._beta_quantile(1 - alpha/2, successes + 1, trials - successes)
        elif successes == trials:
            lower = self._beta_quantile(alpha/2, successes, trials - successes + 1)
            upper = 1.0
        else:
            lower = self._beta_quantile(alpha/2, successes, trials - successes + 1)
            upper = self._beta_quantile(1 - alpha/2, successes + 1, trials - successes)

        return ConfidenceInterval(
            lower=lower,
            upper=upper,
            confidence=confidence,
            method=ConfidenceMethod.BINOMIAL,
            sample_size=trials,
            point_estimate=successes / trials if trials > 0 else 0.0
        )

    def _bootstrap_interval(
        self, successes: int, trials: int, confidence: float
    ) -> ConfidenceInterval:
        """Bootstrap confidence interval."""
        if trials == 0:
            return ConfidenceInterval(0.0, 1.0, confidence, ConfidenceMethod.BOOTSTRAP, 0, 0.0)

        # Generate bootstrap samples
        n_bootstrap = min(10000, max(1000, trials * 10))
        bootstrap_proportions = []

        p_original = successes / trials

        for _ in range(n_bootstrap):
            # Bootstrap resample
            bootstrap_successes = np.random.binomial(trials, p_original)
            bootstrap_p = bootstrap_successes / trials
            bootstrap_proportions.append(bootstrap_p)

        # Calculate percentiles
        alpha = 1 - confidence
        lower_percentile = (alpha / 2) * 100
        upper_percentile = (1 - alpha / 2) * 100

        lower = np.percentile(bootstrap_proportions, lower_percentile)
        upper = np.percentile(bootstrap_proportions, upper_percentile)

        return ConfidenceInterval(
            lower=lower,
            upper=upper,
            confidence=confidence,
            method=ConfidenceMethod.BOOTSTRAP,
            sample_size=trials,
            point_estimate=p_original
        )

    def _select_method(
        self, successes: int, trials: int, confidence: float
    ) -> ConfidenceMethod:
        """Automatically select best confidence interval method."""
        p = successes / trials if trials > 0 else 0.5

        # Rules for method selection
        if trials < 10:
            return ConfidenceMethod.BINOMIAL  # Use exact for very small samples
        elif trials < 30 or p < 0.05 or p > 0.95:
            return ConfidenceMethod.WILSON    # Wilson for small samples or extreme p
        elif trials > 1000:
            return ConfidenceMethod.NORMAL    # Normal approx for large samples
        else:
            return ConfidenceMethod.WILSON    # Wilson as general default

    def _get_z_score(self, confidence: float) -> float:
        """Get z-score for confidence level with caching."""
        return self._z_score_cache.get(confidence, self._calculate_z_score(confidence))

    def _build_z_score_cache(self) -> dict:
        """Build cache of common z-scores."""
        return {
            0.90: 1.645,
            0.95: 1.960,
            0.99: 2.576,
            0.999: 3.291
        }

    def _calculate_z_score(self, confidence: float) -> float:
        """Calculate z-score for arbitrary confidence level."""
        # Using inverse normal CDF approximation
        alpha = 1 - confidence
        return self._inverse_normal_cdf(1 - alpha/2)

    def _inverse_normal_cdf(self, p: float) -> float:
        """Approximate inverse normal CDF."""
        # Beasley-Springer-Moro algorithm approximation
        if p < 0.5:
            return -self._inverse_normal_cdf(1 - p)

        p = p - 0.5
        r = p * p
        return p * (2.515517 + 0.802853 * r + 0.010328 * r * r) / \
               (1 + 1.432788 * r + 0.189269 * r * r + 0.001308 * r * r * r)

    def _beta_quantile(self, p: float, a: float, b: float) -> float:
        """Approximate beta distribution quantile."""
        # Simplified implementation - would use scipy.stats.beta.ppf in practice
        # Using continued fraction approximation
        if a == 1 and b == 1:
            return p
        elif a == 1:
            return 1 - (1 - p) ** (1/b)
        elif b == 1:
            return p ** (1/a)
        else:
            # Newton-Raphson approximation for general case
            x = a / (a + b)  # Initial guess
            for _ in range(10):  # Limited iterations
                fx = self._incomplete_beta(x, a, b) - p
                if abs(fx) < 1e-6:
                    break
                dfx = self._beta_pdf(x, a, b)
                if dfx != 0:
                    x = x - fx / dfx
                x = max(0.001, min(0.999, x))  # Keep in bounds
            return x

    def _incomplete_beta(self, x: float, a: float, b: float) -> float:
        """Simplified incomplete beta function."""
        # Approximation - would use scipy.special.betainc in practice
        if x <= 0:
            return 0.0
        if x >= 1:
            return 1.0
        # Simplified approximation
        return x ** a * (1 - x) ** b

    def _beta_pdf(self, x: float, a: float, b: float) -> float:
        """Beta distribution PDF."""
        if x <= 0 or x >= 1:
            return 0.0
        return x ** (a - 1) * (1 - x) ** (b - 1)


# Global calculator instance
_calculator = ConfidenceCalculator()


def wilson_score_interval(
    successes: int, trials: int, confidence: float = 0.95
) -> ConfidenceInterval:
    """Calculate Wilson score confidence interval."""
    return _calculator.calculate_interval(successes, trials, confidence, ConfidenceMethod.WILSON)


def bootstrap_confidence_interval(
    samples: List[float], confidence: float = 0.95, statistic: str = "mean"
) -> ConfidenceInterval:
    """Calculate bootstrap confidence interval for arbitrary statistic."""
    if not samples:
        raise ValueError("Empty sample list")

    n_bootstrap = min(10000, max(1000, len(samples) * 10))
    bootstrap_stats = []

    for _ in range(n_bootstrap):
        bootstrap_sample = np.random.choice(samples, size=len(samples), replace=True)
        if statistic == "mean":
            stat = statistics.mean(bootstrap_sample)
        elif statistic == "median":
            stat = statistics.median(bootstrap_sample)
        elif statistic == "std":
            stat = statistics.stdev(bootstrap_sample) if len(bootstrap_sample) > 1 else 0
        else:
            raise ValueError(f"Unknown statistic: {statistic}")
        bootstrap_stats.append(stat)

    alpha = 1 - confidence
    lower = np.percentile(bootstrap_stats, (alpha/2) * 100)
    upper = np.percentile(bootstrap_stats, (1 - alpha/2) * 100)

    if statistic == "mean":
        point_est = statistics.mean(samples)
    elif statistic == "median":
        point_est = statistics.median(samples)
    elif statistic == "std":
        point_est = statistics.stdev(samples) if len(samples) > 1 else 0

    return ConfidenceInterval(
        lower=lower,
        upper=upper,
        confidence=confidence,
        method=ConfidenceMethod.BOOTSTRAP,
        sample_size=len(samples),
        point_estimate=point_est
    )
```

### 2. Statistical Assertions Module (`kinda/testing/assertions.py`)

#### Module Structure

```python
"""
High-level statistical assertion interface for kinda-lang testing.

This module provides user-friendly statistical assertion functions that
integrate with the confidence interval framework and pytest.
"""

from typing import Union, Optional, Dict, Any, Callable
from dataclasses import dataclass
import warnings

from .confidence import (
    ConfidenceCalculator, ConfidenceInterval, ConfidenceMethod,
    wilson_score_interval, bootstrap_confidence_interval
)


class StatisticalValidationError(AssertionError):
    """Raised when statistical validation fails."""

    def __init__(
        self,
        observed: float,
        expected: float,
        confidence_interval: ConfidenceInterval,
        p_value: Optional[float] = None,
        context: Optional[str] = None
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
            f"  Sample size: {confidence_interval.sample_size}"
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
        context: Optional[str] = None
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
        ci = self.calculator.calculate_interval(
            successes, n, confidence, ConfidenceMethod(method)
        )

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
            raise StatisticalValidationError(
                proportion, expected, ci, p_value, context
            )

        return True

    def binomial_assert(
        self,
        successes: int,
        trials: int,
        expected_p: float,
        confidence: Optional[float] = None,
        two_tailed: bool = True,
        context: Optional[str] = None
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
            successes, expected_p, trials, confidence,
            method="wilson", context=context
        )

    def proportion_assert(
        self,
        count: int,
        total: int,
        expected_rate: float,
        confidence: Optional[float] = None,
        context: Optional[str] = None
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
        return self.binomial_assert(
            count, total, expected_rate, confidence, context=context
        )

    def eventually_assert(
        self,
        test_function: Callable[[], bool],
        expected_success_rate: float = 0.5,
        max_attempts: int = 100,
        confidence: Optional[float] = None,
        context: Optional[str] = None
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
            successes, attempts, expected_success_rate, confidence,
            context=f"eventually_assert: {context}" if context else "eventually_assert"
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
            k_prob = comb(trials, k) * (expected_p ** k) * ((1 - expected_p) ** (trials - k))
            k_p = k / trials

            # Include if as extreme or more extreme than observed
            if abs(k_p - expected_p) >= abs(observed_p - expected_p):
                extreme_prob += k_prob

        return min(1.0, extreme_prob)

    def _detect_ci_environment(self) -> bool:
        """Detect if running in CI environment."""
        import os
        ci_indicators = [
            'CI', 'CONTINUOUS_INTEGRATION', 'GITHUB_ACTIONS',
            'JENKINS_URL', 'TRAVIS', 'CIRCLECI'
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
    context: Optional[str] = None
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
    context: Optional[str] = None
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
    context: Optional[str] = None
) -> bool:
    """Global proportion assertion function."""
    return _default_tester.proportion_assert(
        count, total, expected_rate, confidence, context
    )


def eventually_assert(
    test_function: Callable[[], bool],
    expected_success_rate: float = 0.5,
    max_attempts: int = 100,
    confidence: float = 0.95,
    context: Optional[str] = None
) -> bool:
    """Global eventually assertion function."""
    return _default_tester.eventually_assert(
        test_function, expected_success_rate, max_attempts, confidence, context
    )
```

### 3. Distribution Testing Module (`kinda/testing/distributions.py`)

#### Module Structure

```python
"""
Advanced distribution testing for kinda-lang probabilistic constructs.

This module provides statistical tests for validating probability distributions
and comparing observed vs expected behavior in probabilistic systems.
"""

from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
from enum import Enum
import math
import statistics

from .confidence import ConfidenceInterval
from .assertions import StatisticalValidationError


class DistributionTest(Enum):
    """Available distribution testing methods."""
    CHI_SQUARE = "chi_square"
    KOLMOGOROV_SMIRNOV = "kolmogorov_smirnov"
    ANDERSON_DARLING = "anderson_darling"
    BINOMIAL = "binomial"


@dataclass
class DistributionTestResult:
    """Result of distribution testing."""
    test_statistic: float
    p_value: float
    degrees_of_freedom: Optional[int]
    critical_value: float
    is_valid: bool
    method: DistributionTest
    sample_size: int
    message: str


class DistributionTester:
    """Statistical distribution testing engine."""

    def __init__(self):
        self._chi_square_cache = self._build_chi_square_cache()

    def chi_square_test(
        self,
        observed: Dict[str, int],
        expected: Dict[str, float],
        significance: float = 0.05
    ) -> DistributionTestResult:
        """
        Perform chi-square goodness-of-fit test.

        Args:
            observed: Observed counts by category
            expected: Expected probabilities by category
            significance: Significance level

        Returns:
            DistributionTestResult with test outcome
        """
        # Validate inputs
        if not observed or not expected:
            raise ValueError("Observed and expected must be non-empty")

        if set(observed.keys()) != set(expected.keys()):
            raise ValueError("Observed and expected must have same categories")

        # Calculate total observations
        total_observed = sum(observed.values())

        # Calculate expected counts
        expected_counts = {
            category: prob * total_observed
            for category, prob in expected.items()
        }

        # Check minimum expected count requirement
        min_expected = min(expected_counts.values())
        if min_expected < 5:
            # Warn about low expected counts
            import warnings
            warnings.warn(
                f"Chi-square test with low expected count ({min_expected:.1f}). "
                "Results may be unreliable."
            )

        # Calculate chi-square statistic
        chi_square = 0.0
        for category in observed.keys():
            obs = observed[category]
            exp = expected_counts[category]
            if exp > 0:
                chi_square += (obs - exp) ** 2 / exp

        # Degrees of freedom
        df = len(observed) - 1

        # Get critical value
        critical_value = self._get_chi_square_critical(df, significance)

        # Calculate p-value (approximation)
        p_value = self._chi_square_p_value(chi_square, df)

        # Determine if test passes
        is_valid = chi_square <= critical_value

        message = (
            f"Chi-square test: χ² = {chi_square:.3f}, "
            f"critical = {critical_value:.3f}, "
            f"p = {p_value:.3f}, "
            f"df = {df}"
        )

        return DistributionTestResult(
            test_statistic=chi_square,
            p_value=p_value,
            degrees_of_freedom=df,
            critical_value=critical_value,
            is_valid=is_valid,
            method=DistributionTest.CHI_SQUARE,
            sample_size=total_observed,
            message=message
        )

    def kolmogorov_smirnov_test(
        self,
        sample1: List[float],
        sample2: Optional[List[float]] = None,
        expected_cdf: Optional[callable] = None,
        significance: float = 0.05
    ) -> DistributionTestResult:
        """
        Perform Kolmogorov-Smirnov test.

        Args:
            sample1: First sample
            sample2: Second sample (for two-sample test)
            expected_cdf: Expected CDF function (for one-sample test)
            significance: Significance level

        Returns:
            DistributionTestResult with test outcome
        """
        if sample2 is not None:
            # Two-sample KS test
            return self._ks_two_sample(sample1, sample2, significance)
        elif expected_cdf is not None:
            # One-sample KS test
            return self._ks_one_sample(sample1, expected_cdf, significance)
        else:
            raise ValueError("Must provide either sample2 or expected_cdf")

    def binomial_distribution_test(
        self,
        construct_samples: Dict[bool, int],
        expected_p: float,
        confidence: float = 0.95
    ) -> DistributionTestResult:
        """
        Test if construct behavior matches binomial distribution.

        Args:
            construct_samples: {True: success_count, False: failure_count}
            expected_p: Expected success probability
            confidence: Confidence level

        Returns:
            DistributionTestResult with test outcome
        """
        successes = construct_samples.get(True, 0)
        failures = construct_samples.get(False, 0)
        total = successes + failures

        if total == 0:
            raise ValueError("No samples provided")

        # Use Wilson score interval for binomial test
        from .confidence import wilson_score_interval
        ci = wilson_score_interval(successes, total, confidence)

        # Test if expected probability falls within confidence interval
        is_valid = ci.contains(expected_p)
        observed_p = successes / total

        # Calculate binomial test p-value
        p_value = self._binomial_test_p_value(successes, total, expected_p)

        message = (
            f"Binomial test: observed p = {observed_p:.3f}, "
            f"expected p = {expected_p:.3f}, "
            f"CI = [{ci.lower:.3f}, {ci.upper:.3f}], "
            f"p = {p_value:.3f}"
        )

        return DistributionTestResult(
            test_statistic=observed_p,
            p_value=p_value,
            degrees_of_freedom=None,
            critical_value=expected_p,
            is_valid=is_valid,
            method=DistributionTest.BINOMIAL,
            sample_size=total,
            message=message
        )

    def personality_distribution_test(
        self,
        construct_samples: Dict[str, int],
        personality_probabilities: Dict[str, float],
        significance: float = 0.05
    ) -> DistributionTestResult:
        """
        Test if construct behavior matches personality-adjusted distribution.

        Args:
            construct_samples: Observed counts by construct type
            personality_probabilities: Expected probabilities by construct type
            significance: Significance level

        Returns:
            DistributionTestResult with test outcome
        """
        return self.chi_square_test(
            construct_samples, personality_probabilities, significance
        )

    def _ks_two_sample(
        self, sample1: List[float], sample2: List[float], significance: float
    ) -> DistributionTestResult:
        """Two-sample Kolmogorov-Smirnov test."""
        if not sample1 or not sample2:
            raise ValueError("Both samples must be non-empty")

        # Sort samples
        sorted1 = sorted(sample1)
        sorted2 = sorted(sample2)

        # Calculate empirical CDFs and find maximum difference
        max_diff = 0.0

        # Get all unique values
        all_values = sorted(set(sorted1 + sorted2))

        for value in all_values:
            cdf1 = sum(1 for x in sorted1 if x <= value) / len(sorted1)
            cdf2 = sum(1 for x in sorted2 if x <= value) / len(sorted2)
            diff = abs(cdf1 - cdf2)
            max_diff = max(max_diff, diff)

        # Calculate critical value
        n1, n2 = len(sorted1), len(sorted2)
        critical_value = self._ks_critical_value(n1, n2, significance)

        is_valid = max_diff <= critical_value

        # Approximate p-value
        p_value = self._ks_p_value(max_diff, n1, n2)

        message = (
            f"KS two-sample test: D = {max_diff:.3f}, "
            f"critical = {critical_value:.3f}, "
            f"p ≈ {p_value:.3f}"
        )

        return DistributionTestResult(
            test_statistic=max_diff,
            p_value=p_value,
            degrees_of_freedom=None,
            critical_value=critical_value,
            is_valid=is_valid,
            method=DistributionTest.KOLMOGOROV_SMIRNOV,
            sample_size=n1 + n2,
            message=message
        )

    def _ks_one_sample(
        self, sample: List[float], expected_cdf: callable, significance: float
    ) -> DistributionTestResult:
        """One-sample Kolmogorov-Smirnov test."""
        if not sample:
            raise ValueError("Sample must be non-empty")

        sorted_sample = sorted(sample)
        n = len(sorted_sample)
        max_diff = 0.0

        for i, value in enumerate(sorted_sample):
            empirical_cdf = (i + 1) / n
            expected_cdf_value = expected_cdf(value)
            diff = abs(empirical_cdf - expected_cdf_value)
            max_diff = max(max_diff, diff)

        critical_value = self._ks_critical_value(n, None, significance)
        is_valid = max_diff <= critical_value

        p_value = self._ks_p_value(max_diff, n, None)

        message = (
            f"KS one-sample test: D = {max_diff:.3f}, "
            f"critical = {critical_value:.3f}, "
            f"p ≈ {p_value:.3f}"
        )

        return DistributionTestResult(
            test_statistic=max_diff,
            p_value=p_value,
            degrees_of_freedom=None,
            critical_value=critical_value,
            is_valid=is_valid,
            method=DistributionTest.KOLMOGOROV_SMIRNOV,
            sample_size=n,
            message=message
        )

    def _get_chi_square_critical(self, df: int, significance: float) -> float:
        """Get chi-square critical value."""
        key = (df, significance)
        if key in self._chi_square_cache:
            return self._chi_square_cache[key]

        # Simplified approximation for missing values
        if significance == 0.05:
            if df == 1:
                return 3.841
            elif df == 2:
                return 5.991
            elif df == 3:
                return 7.815
            else:
                # Approximation: χ²(df, 0.05) ≈ df + 2√(2df) + 2/3
                return df + 2 * math.sqrt(2 * df) + 2/3
        else:
            # Very rough approximation
            return df + 2 * math.sqrt(2 * df)

    def _chi_square_p_value(self, chi_square: float, df: int) -> float:
        """Approximate chi-square p-value."""
        # Simplified approximation - would use scipy.stats.chi2.sf in practice
        if df == 1:
            # For df=1, use normal approximation
            z = math.sqrt(chi_square)
            return 2 * (1 - self._normal_cdf(z))
        else:
            # Rough approximation using Wilson-Hilferty transformation
            h = 2.0 / (9.0 * df)
            z = (math.pow(chi_square / df, 1.0/3.0) - (1 - h)) / math.sqrt(h)
            return 1 - self._normal_cdf(z)

    def _ks_critical_value(
        self, n1: int, n2: Optional[int], significance: float
    ) -> float:
        """Calculate Kolmogorov-Smirnov critical value."""
        if n2 is None:
            # One-sample test
            return math.sqrt(-0.5 * math.log(significance / 2)) / math.sqrt(n1)
        else:
            # Two-sample test
            return math.sqrt(-0.5 * math.log(significance / 2)) * math.sqrt((n1 + n2) / (n1 * n2))

    def _ks_p_value(self, d_statistic: float, n1: int, n2: Optional[int]) -> float:
        """Approximate Kolmogorov-Smirnov p-value."""
        if n2 is None:
            # One-sample
            lambda_val = d_statistic * math.sqrt(n1)
        else:
            # Two-sample
            lambda_val = d_statistic * math.sqrt(n1 * n2 / (n1 + n2))

        # Smirnov's asymptotic formula approximation
        return 2 * math.exp(-2 * lambda_val ** 2)

    def _binomial_test_p_value(self, successes: int, trials: int, expected_p: float) -> float:
        """Calculate binomial test p-value."""
        observed_p = successes / trials

        # Two-tailed test
        from math import comb

        extreme_prob = 0.0
        for k in range(trials + 1):
            k_prob = comb(trials, k) * (expected_p ** k) * ((1 - expected_p) ** (trials - k))
            k_p = k / trials

            if abs(k_p - expected_p) >= abs(observed_p - expected_p):
                extreme_prob += k_prob

        return min(1.0, extreme_prob)

    def _normal_cdf(self, z: float) -> float:
        """Approximate normal CDF."""
        # Using error function approximation
        return 0.5 * (1 + math.tanh(z * math.sqrt(2 / math.pi)))

    def _build_chi_square_cache(self) -> Dict[Tuple[int, float], float]:
        """Build cache of common chi-square critical values."""
        return {
            (1, 0.05): 3.841,
            (2, 0.05): 5.991,
            (3, 0.05): 7.815,
            (4, 0.05): 9.488,
            (5, 0.05): 11.071,
            (1, 0.01): 6.635,
            (2, 0.01): 9.210,
            (3, 0.01): 11.345,
            (4, 0.01): 13.277,
            (5, 0.01): 15.086,
        }


# Global distribution tester instance
_default_tester = DistributionTester()


def chi_square_test(
    observed: Dict[str, int],
    expected: Dict[str, float],
    significance: float = 0.05
) -> DistributionTestResult:
    """Global chi-square test function."""
    return _default_tester.chi_square_test(observed, expected, significance)


def binomial_distribution_test(
    construct_samples: Dict[bool, int],
    expected_p: float,
    confidence: float = 0.95
) -> DistributionTestResult:
    """Global binomial distribution test function."""
    return _default_tester.binomial_distribution_test(construct_samples, expected_p, confidence)


def personality_distribution_test(
    construct_samples: Dict[str, int],
    personality_probabilities: Dict[str, float],
    significance: float = 0.05
) -> DistributionTestResult:
    """Global personality distribution test function."""
    return _default_tester.personality_distribution_test(
        construct_samples, personality_probabilities, significance
    )
```

## Error Handling Strategy

### Exception Hierarchy

```python
class StatisticalFrameworkError(Exception):
    """Base exception for statistical framework."""
    pass

class StatisticalValidationError(StatisticalFrameworkError, AssertionError):
    """Statistical validation failed."""
    pass

class ConfidenceIntervalError(StatisticalFrameworkError):
    """Confidence interval calculation failed."""
    pass

class DistributionTestError(StatisticalFrameworkError):
    """Distribution test failed."""
    pass

class InsufficientDataError(StatisticalFrameworkError):
    """Insufficient data for statistical analysis."""
    pass
```

### Error Handling Patterns

```python
def robust_statistical_assert(*args, **kwargs):
    """Statistical assert with fallback mechanisms."""
    try:
        return statistical_assert(*args, **kwargs)
    except InsufficientDataError:
        # Fall back to simple threshold check
        warnings.warn("Insufficient data for statistical test, using simple threshold")
        return simple_threshold_check(*args, **kwargs)
    except ConfidenceIntervalError:
        # Fall back to different CI method
        kwargs['method'] = 'normal'
        return statistical_assert(*args, **kwargs)
```

## Configuration System

### Environment-Specific Configurations

```python
class EnvironmentConfig:
    """Environment-specific statistical configurations."""

    @classmethod
    def for_ci(cls):
        """Configuration optimized for CI environments."""
        return StatisticalConfig(
            default_confidence=0.93,  # Slightly more lenient
            default_method="wilson",
            ci_environment_adjustment=0.02,
            max_sample_size=5000,  # Reduced for faster CI
            min_sample_size=20
        )

    @classmethod
    def for_development(cls):
        """Configuration for local development."""
        return StatisticalConfig(
            default_confidence=0.95,
            default_method="wilson",
            ci_environment_adjustment=0.0,
            max_sample_size=10000,
            min_sample_size=10
        )

    @classmethod
    def for_performance_testing(cls):
        """Configuration for performance testing."""
        return StatisticalConfig(
            default_confidence=0.99,  # Stricter for performance
            default_method="bootstrap",
            ci_environment_adjustment=0.0,
            max_sample_size=50000,
            min_sample_size=100
        )
```

## Integration Requirements

### Pytest Plugin Extensions

```python
# In kinda/testing/pytest_plugin.py

class StatisticalTestingPlugin:
    """Pytest plugin for statistical testing."""

    def pytest_configure(self, config):
        """Configure statistical testing markers."""
        config.addinivalue_line(
            "markers", "statistical: mark test for statistical validation"
        )
        config.addinivalue_line(
            "markers", "probabilistic: mark test for probabilistic behavior"
        )

    @pytest.fixture
    def statistical_tester(self):
        """Provide statistical tester fixture."""
        return StatisticalTester()

    @pytest.fixture
    def distribution_tester(self):
        """Provide distribution tester fixture."""
        return DistributionTester()
```

### Runtime Helpers Integration

```python
# Integration with existing runtime helpers

from kinda.testing.assertions import statistical_assert, binomial_assert

def enhanced_maybe(condition, expected_probability=0.6):
    """Enhanced ~maybe with optional statistical validation."""
    result = maybe(condition)

    # Optional: collect samples for statistical validation
    if hasattr(enhanced_maybe, '_samples'):
        enhanced_maybe._samples.append(result)

    return result

# Add statistical validation helper
enhanced_maybe._samples = []

def validate_maybe_behavior(expected_p=0.6, confidence=0.95):
    """Validate collected ~maybe samples."""
    samples = enhanced_maybe._samples
    successes = sum(samples)
    trials = len(samples)

    return binomial_assert(successes, trials, expected_p, confidence)
```

## Performance Optimization

### Computational Optimizations

```python
class OptimizedConfidenceCalculator(ConfidenceCalculator):
    """Performance-optimized confidence calculator."""

    def __init__(self):
        super().__init__()
        self._interval_cache = {}
        self._cache_hits = 0
        self._cache_misses = 0

    def calculate_interval(self, successes, trials, confidence, method):
        """Calculate with caching."""
        cache_key = (successes, trials, confidence, method)

        if cache_key in self._interval_cache:
            self._cache_hits += 1
            return self._interval_cache[cache_key]

        result = super().calculate_interval(successes, trials, confidence, method)

        # Cache result if cache isn't too large
        if len(self._interval_cache) < 10000:
            self._interval_cache[cache_key] = result

        self._cache_misses += 1
        return result
```

### Memory Management

```python
class StreamingStatisticalTester(StatisticalTester):
    """Memory-efficient statistical tester for large samples."""

    def streaming_binomial_assert(
        self, sample_stream, expected_p, confidence=0.95
    ):
        """Process samples in streaming fashion."""
        successes = 0
        trials = 0

        for sample in sample_stream:
            if sample:
                successes += 1
            trials += 1

            # Periodic validation for early detection
            if trials % 1000 == 0:
                # Calculate confidence interval with current data
                ci = self.calculator.calculate_interval(
                    successes, trials, confidence
                )

                # Early exit if clearly failing
                if not ci.contains(expected_p) and trials > 5000:
                    raise StatisticalValidationError(
                        successes/trials, expected_p, ci,
                        context="Early termination due to clear failure"
                    )

        # Final validation
        return self.binomial_assert(successes, trials, expected_p, confidence)
```

## Validation Requirements

### Framework Self-Testing

```python
class FrameworkValidator:
    """Validates the statistical framework itself."""

    def test_confidence_interval_accuracy(self):
        """Test that confidence intervals have correct coverage."""
        true_p = 0.6
        confidence = 0.95
        coverage_count = 0
        trials = 1000

        for _ in range(trials):
            # Simulate binomial samples
            n = 100
            successes = np.random.binomial(n, true_p)

            # Calculate confidence interval
            ci = wilson_score_interval(successes, n, confidence)

            # Check if true parameter is covered
            if ci.contains(true_p):
                coverage_count += 1

        # Coverage should be approximately equal to confidence level
        observed_coverage = coverage_count / trials
        assert abs(observed_coverage - confidence) < 0.05, \
            f"Coverage {observed_coverage:.3f} differs from {confidence:.3f}"

    def test_type_i_error_rate(self):
        """Test that Type I error rate matches significance level."""
        significance = 0.05
        true_p = 0.5
        error_count = 0
        trials = 1000

        for _ in range(trials):
            # Generate data under null hypothesis
            n = 100
            successes = np.random.binomial(n, true_p)

            try:
                binomial_assert(successes, n, true_p + 0.1, confidence=0.95)
            except StatisticalValidationError:
                error_count += 1

        # Error rate should be approximately equal to significance level
        observed_error_rate = error_count / trials
        assert abs(observed_error_rate - significance) < 0.02, \
            f"Error rate {observed_error_rate:.3f} differs from {significance:.3f}"
```

## Documentation Requirements

### API Documentation

- Complete docstrings for all public functions
- Mathematical formulas in documentation
- Usage examples for each assertion type
- Error handling documentation
- Performance characteristics documentation

### Migration Guides

- Step-by-step conversion examples
- Before/after code comparisons
- Common pitfalls and solutions
- Performance impact analysis
- Testing strategy recommendations

## Implementation Timeline

### Week 1: Core Implementation
- Implement confidence.py module
- Implement assertions.py module
- Basic pytest integration
- Unit tests for mathematical accuracy

### Week 2: Advanced Features
- Implement distributions.py module
- Enhanced pytest plugin
- Performance optimizations
- Integration testing

### Week 3: Finalization
- Documentation completion
- Migration tooling
- Performance validation
- Final testing and optimization

## Success Criteria

### Mathematical Accuracy
- ✅ Wilson score intervals mathematically correct
- ✅ Bootstrap methods statistically sound
- ✅ Distribution tests properly implemented
- ✅ Multiple testing correction available

### Performance Targets
- ✅ <1ms per assertion execution
- ✅ <1% framework overhead
- ✅ Memory usage <10MB
- ✅ CI execution time increase <5%

### Integration Quality
- ✅ Seamless pytest integration
- ✅ Clear error messages
- ✅ Backward compatibility
- ✅ Comprehensive documentation

---

**Status**: Ready for Coder Agent implementation
**Dependencies**: None (extends existing framework)
**Risk Level**: Low (well-defined mathematical foundation)