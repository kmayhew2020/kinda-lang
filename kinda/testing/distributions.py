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


class DistributionTestError(Exception):
    """Distribution test failed."""

    pass


class DistributionTester:
    """Statistical distribution testing engine."""

    def __init__(self):
        self._chi_square_cache = self._build_chi_square_cache()

    def chi_square_test(
        self, observed: Dict[str, int], expected: Dict[str, float], significance: float = 0.05
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
        expected_counts = {category: prob * total_observed for category, prob in expected.items()}

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
            message=message,
        )

    def kolmogorov_smirnov_test(
        self,
        sample1: List[float],
        sample2: Optional[List[float]] = None,
        expected_cdf: Optional[callable] = None,
        significance: float = 0.05,
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
        self, construct_samples: Dict[bool, int], expected_p: float, confidence: float = 0.95
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
            message=message,
        )

    def personality_distribution_test(
        self,
        construct_samples: Dict[str, int],
        personality_probabilities: Dict[str, float],
        significance: float = 0.05,
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
        return self.chi_square_test(construct_samples, personality_probabilities, significance)

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
            message=message,
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
            message=message,
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
                return df + 2 * math.sqrt(2 * df) + 2 / 3
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
            z = (math.pow(chi_square / df, 1.0 / 3.0) - (1 - h)) / math.sqrt(h)
            return 1 - self._normal_cdf(z)

    def _ks_critical_value(self, n1: int, n2: Optional[int], significance: float) -> float:
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
        return 2 * math.exp(-2 * lambda_val**2)

    def _binomial_test_p_value(self, successes: int, trials: int, expected_p: float) -> float:
        """Calculate binomial test p-value."""
        observed_p = successes / trials

        # Two-tailed test
        from math import comb

        extreme_prob = 0.0
        for k in range(trials + 1):
            k_prob = comb(trials, k) * (expected_p**k) * ((1 - expected_p) ** (trials - k))
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
    observed: Dict[str, int], expected: Dict[str, float], significance: float = 0.05
) -> DistributionTestResult:
    """Global chi-square test function."""
    return _default_tester.chi_square_test(observed, expected, significance)


def binomial_distribution_test(
    construct_samples: Dict[bool, int], expected_p: float, confidence: float = 0.95
) -> DistributionTestResult:
    """Global binomial distribution test function."""
    return _default_tester.binomial_distribution_test(construct_samples, expected_p, confidence)


def personality_distribution_test(
    construct_samples: Dict[str, int],
    personality_probabilities: Dict[str, float],
    significance: float = 0.05,
) -> DistributionTestResult:
    """Global personality distribution test function."""
    return _default_tester.personality_distribution_test(
        construct_samples, personality_probabilities, significance
    )
