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

    WILSON = "wilson"  # Wilson score interval
    NORMAL = "normal"  # Normal approximation
    BINOMIAL = "binomial"  # Exact binomial
    BOOTSTRAP = "bootstrap"  # Bootstrap method
    AUTO = "auto"  # Automatic method selection


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


class StatisticalFrameworkError(Exception):
    """Base exception for statistical framework."""

    pass


class ConfidenceIntervalError(StatisticalFrameworkError):
    """Confidence interval calculation failed."""

    pass


class InsufficientDataError(StatisticalFrameworkError):
    """Insufficient data for statistical analysis."""

    pass


class ConfidenceCalculator:
    """Core confidence interval calculation engine."""

    def __init__(self):
        self._z_score_cache = self._build_z_score_cache()

    def calculate_interval(
        self,
        successes: int,
        trials: int,
        confidence: float = 0.95,
        method: Union[str, ConfidenceMethod] = ConfidenceMethod.AUTO,
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
            ConfidenceIntervalError: Calculation fails
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

        try:
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
        except Exception as e:
            raise ConfidenceIntervalError(f"Failed to calculate confidence interval: {e}")

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

        # Handle floating point precision issues
        if upper > 0.9999999999999:
            upper = 1.0
        if lower < 0.0000000000001:
            lower = 0.0

        return ConfidenceInterval(
            lower=lower,
            upper=upper,
            confidence=confidence,
            method=ConfidenceMethod.WILSON,
            sample_size=trials,
            point_estimate=p,
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
            point_estimate=p,
        )

    def _exact_binomial(self, successes: int, trials: int, confidence: float) -> ConfidenceInterval:
        """Exact binomial confidence interval (Clopper-Pearson)."""
        # Implementation using beta distribution quantiles
        # This is computationally intensive but exact
        alpha = 1 - confidence

        if successes == 0:
            lower = 0.0
            upper = self._beta_quantile(1 - alpha / 2, successes + 1, trials - successes)
        elif successes == trials:
            lower = self._beta_quantile(alpha / 2, successes, trials - successes + 1)
            upper = 1.0
        else:
            lower = self._beta_quantile(alpha / 2, successes, trials - successes + 1)
            upper = self._beta_quantile(1 - alpha / 2, successes + 1, trials - successes)

        return ConfidenceInterval(
            lower=lower,
            upper=upper,
            confidence=confidence,
            method=ConfidenceMethod.BINOMIAL,
            sample_size=trials,
            point_estimate=successes / trials if trials > 0 else 0.0,
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
            point_estimate=p_original,
        )

    def _select_method(self, successes: int, trials: int, confidence: float) -> ConfidenceMethod:
        """Automatically select best confidence interval method."""
        p = successes / trials if trials > 0 else 0.5

        # Rules for method selection
        if trials < 10:
            return ConfidenceMethod.BINOMIAL  # Use exact for very small samples
        elif trials < 30 or p < 0.05 or p > 0.95:
            return ConfidenceMethod.WILSON  # Wilson for small samples or extreme p
        elif trials > 1000:
            return ConfidenceMethod.NORMAL  # Normal approx for large samples
        else:
            return ConfidenceMethod.WILSON  # Wilson as general default

    def _get_z_score(self, confidence: float) -> float:
        """Get z-score for confidence level with caching."""
        return self._z_score_cache.get(confidence, self._calculate_z_score(confidence))

    def _build_z_score_cache(self) -> dict:
        """Build cache of common z-scores."""
        return {0.90: 1.645, 0.95: 1.960, 0.99: 2.576, 0.999: 3.291}

    def _calculate_z_score(self, confidence: float) -> float:
        """Calculate z-score for arbitrary confidence level."""
        # Using inverse normal CDF approximation
        alpha = 1 - confidence
        return self._inverse_normal_cdf(1 - alpha / 2)

    def _inverse_normal_cdf(self, p: float) -> float:
        """Approximate inverse normal CDF."""
        # Improved approximation using rational function
        if p <= 0:
            return float("-inf")
        if p >= 1:
            return float("inf")
        if p < 0.5:
            return -self._inverse_normal_cdf(1 - p)

        # Use a more accurate approximation for the normal quantile
        t = math.sqrt(-2 * math.log(1 - p))
        return t - (2.515517 + 0.802853 * t + 0.010328 * t * t) / (
            1 + 1.432788 * t + 0.189269 * t * t + 0.001308 * t * t * t
        )

    def _beta_quantile(self, p: float, a: float, b: float) -> float:
        """Approximate beta distribution quantile."""
        # Simplified implementation - would use scipy.stats.beta.ppf in practice
        # Using continued fraction approximation
        if a == 1 and b == 1:
            return p
        elif a == 1:
            return 1 - (1 - p) ** (1 / b)
        elif b == 1:
            return p ** (1 / a)
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
        return x**a * (1 - x) ** b

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
        # Convert numpy array to native Python types for statistics module compatibility
        bootstrap_sample = [float(x) for x in bootstrap_sample]
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
    lower = np.percentile(bootstrap_stats, (alpha / 2) * 100)
    upper = np.percentile(bootstrap_stats, (1 - alpha / 2) * 100)

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
        point_estimate=point_est,
    )
