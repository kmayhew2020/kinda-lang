"""Statistical validation framework for performance tests."""

import statistics
import numpy as np
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
from enum import Enum


class ValidationMethod(Enum):
    """Statistical validation methods."""
    ROBUST = "robust"  # Median + MAD based
    BOOTSTRAP = "bootstrap"  # Bootstrap confidence intervals
    PERCENTILE = "percentile"  # Percentile-based validation
    SIMPLE = "simple"  # Simple mean + std (fallback)


@dataclass
class ValidationResult:
    """Result of statistical validation."""
    is_valid: bool
    message: str
    p_value: Optional[float]
    confidence_level: float
    method_used: ValidationMethod
    statistics: Dict[str, float]


@dataclass
class ComparisonResult:
    """Result of performance comparison between two sets."""
    is_valid: bool
    message: str
    overhead_percent: float
    significance_test: Optional[str]
    p_value: Optional[float]
    effect_size: Optional[float]


class StatisticalValidator:
    """Provides statistical validation for performance tests."""

    def __init__(self):
        self._validation_cache: Dict[str, ValidationResult] = {}

    def validate_performance(
        self,
        samples: List[float],
        lower_threshold: float,
        upper_threshold: float,
        method: str = "robust",
        confidence_level: float = 0.95
    ) -> ValidationResult:
        """Validate performance samples against thresholds."""
        if not samples:
            return ValidationResult(
                is_valid=False,
                message="No samples provided for validation",
                p_value=None,
                confidence_level=confidence_level,
                method_used=ValidationMethod.SIMPLE,
                statistics={}
            )

        # Convert method string to enum
        try:
            validation_method = ValidationMethod(method.lower())
        except ValueError:
            validation_method = ValidationMethod.ROBUST

        # Calculate basic statistics
        stats = self._calculate_basic_statistics(samples)

        # Perform validation based on method
        if validation_method == ValidationMethod.ROBUST:
            result = self._validate_robust(samples, lower_threshold, upper_threshold, confidence_level, stats)
        elif validation_method == ValidationMethod.BOOTSTRAP:
            result = self._validate_bootstrap(samples, lower_threshold, upper_threshold, confidence_level, stats)
        elif validation_method == ValidationMethod.PERCENTILE:
            result = self._validate_percentile(samples, lower_threshold, upper_threshold, confidence_level, stats)
        else:  # SIMPLE
            result = self._validate_simple(samples, lower_threshold, upper_threshold, confidence_level, stats)

        return result

    def compare_performance(
        self,
        baseline_samples: List[float],
        comparison_samples: List[float],
        max_overhead_percent: float = 20.0,
        significance_level: float = 0.05
    ) -> ComparisonResult:
        """Compare performance between two sample sets."""
        if not baseline_samples or not comparison_samples:
            return ComparisonResult(
                is_valid=False,
                message="Insufficient samples for comparison",
                overhead_percent=float('inf'),
                significance_test=None,
                p_value=None,
                effect_size=None
            )

        # Calculate medians for overhead calculation
        baseline_median = statistics.median(baseline_samples)
        comparison_median = statistics.median(comparison_samples)

        # Calculate overhead percentage
        if baseline_median > 0:
            overhead_percent = ((comparison_median - baseline_median) / baseline_median) * 100
        else:
            overhead_percent = 0.0

        # Perform statistical significance test
        p_value, test_name = self._perform_significance_test(baseline_samples, comparison_samples)

        # Calculate effect size (Cohen's d equivalent for medians)
        effect_size = self._calculate_effect_size(baseline_samples, comparison_samples)

        # Determine if comparison is valid
        is_valid = (
            overhead_percent <= max_overhead_percent and
            (p_value is None or p_value >= significance_level)  # No significant increase
        )

        # Create informative message
        if is_valid:
            message = f"Performance comparison valid: {overhead_percent:.2f}% overhead (≤{max_overhead_percent}%)"
        else:
            reasons = []
            if overhead_percent > max_overhead_percent:
                reasons.append(f"overhead {overhead_percent:.2f}% > {max_overhead_percent}%")
            if p_value and p_value < significance_level:
                reasons.append(f"significant performance degradation (p={p_value:.3f})")
            message = f"Performance comparison failed: {', '.join(reasons)}"

        return ComparisonResult(
            is_valid=is_valid,
            message=message,
            overhead_percent=overhead_percent,
            significance_test=test_name,
            p_value=p_value,
            effect_size=effect_size
        )

    def detect_outliers(self, samples: List[float], method: str = "iqr") -> Tuple[List[float], List[int]]:
        """Detect and return outliers in samples."""
        if len(samples) < 3:
            return [], []

        if method.lower() == "iqr":
            return self._detect_outliers_iqr(samples)
        elif method.lower() == "mad":
            return self._detect_outliers_mad(samples)
        elif method.lower() == "zscore":
            return self._detect_outliers_zscore(samples)
        else:
            return self._detect_outliers_iqr(samples)  # Default

    def _calculate_basic_statistics(self, samples: List[float]) -> Dict[str, float]:
        """Calculate basic statistics for samples."""
        if not samples:
            return {}

        return {
            'mean': statistics.mean(samples),
            'median': statistics.median(samples),
            'std': statistics.stdev(samples) if len(samples) > 1 else 0.0,
            'mad': self._median_absolute_deviation(samples),
            'min': min(samples),
            'max': max(samples),
            'count': len(samples),
            'q25': np.percentile(samples, 25),
            'q75': np.percentile(samples, 75),
        }

    def _validate_robust(
        self,
        samples: List[float],
        lower_threshold: float,
        upper_threshold: float,
        confidence_level: float,
        stats: Dict[str, float]
    ) -> ValidationResult:
        """Validate using robust statistics (median + MAD)."""
        median = stats['median']
        mad = stats['mad']

        # Use MAD-based confidence interval
        # MAD * 1.4826 approximates standard deviation for normal data
        mad_multiplier = 1.4826
        confidence_multiplier = self._get_confidence_multiplier(confidence_level)

        # Calculate robust confidence interval
        margin_of_error = mad * mad_multiplier * confidence_multiplier / np.sqrt(len(samples))
        ci_lower = median - margin_of_error
        ci_upper = median + margin_of_error

        # Check if confidence interval is within thresholds
        is_valid = ci_lower >= lower_threshold and ci_upper <= upper_threshold

        # Calculate approximate p-value (how far outside thresholds)
        if not is_valid:
            if ci_lower < lower_threshold:
                z_score = (lower_threshold - ci_lower) / (mad * mad_multiplier)
            else:  # ci_upper > upper_threshold
                z_score = (ci_upper - upper_threshold) / (mad * mad_multiplier)
            p_value = 2 * (1 - self._normal_cdf(abs(z_score)))
        else:
            p_value = 1.0  # Well within thresholds

        message = (
            f"Robust validation: median={median:.4f}, "
            f"CI=[{ci_lower:.4f}, {ci_upper:.4f}], "
            f"thresholds=[{lower_threshold:.4f}, {upper_threshold:.4f}]"
        )

        return ValidationResult(
            is_valid=is_valid,
            message=message,
            p_value=p_value,
            confidence_level=confidence_level,
            method_used=ValidationMethod.ROBUST,
            statistics={**stats, 'ci_lower': ci_lower, 'ci_upper': ci_upper}
        )

    def _validate_bootstrap(
        self,
        samples: List[float],
        lower_threshold: float,
        upper_threshold: float,
        confidence_level: float,
        stats: Dict[str, float]
    ) -> ValidationResult:
        """Validate using bootstrap confidence intervals."""
        try:
            # Perform bootstrap resampling
            n_bootstrap = min(1000, len(samples) * 50)
            bootstrap_medians = []

            for _ in range(n_bootstrap):
                bootstrap_sample = np.random.choice(samples, size=len(samples), replace=True)
                bootstrap_medians.append(statistics.median(bootstrap_sample))

            # Calculate percentiles for confidence interval
            alpha = 1 - confidence_level
            lower_percentile = (alpha / 2) * 100
            upper_percentile = (1 - alpha / 2) * 100

            ci_lower = np.percentile(bootstrap_medians, lower_percentile)
            ci_upper = np.percentile(bootstrap_medians, upper_percentile)

            # Check if confidence interval is within thresholds
            is_valid = ci_lower >= lower_threshold and ci_upper <= upper_threshold

            # Estimate p-value from bootstrap distribution
            outside_count = sum(1 for m in bootstrap_medians if m < lower_threshold or m > upper_threshold)
            p_value = outside_count / len(bootstrap_medians)

            message = (
                f"Bootstrap validation: median={stats['median']:.4f}, "
                f"bootstrap CI=[{ci_lower:.4f}, {ci_upper:.4f}], "
                f"thresholds=[{lower_threshold:.4f}, {upper_threshold:.4f}]"
            )

            return ValidationResult(
                is_valid=is_valid,
                message=message,
                p_value=p_value,
                confidence_level=confidence_level,
                method_used=ValidationMethod.BOOTSTRAP,
                statistics={**stats, 'ci_lower': ci_lower, 'ci_upper': ci_upper, 'bootstrap_samples': n_bootstrap}
            )

        except Exception:
            # Fall back to robust method if bootstrap fails
            return self._validate_robust(samples, lower_threshold, upper_threshold, confidence_level, stats)

    def _validate_percentile(
        self,
        samples: List[float],
        lower_threshold: float,
        upper_threshold: float,
        confidence_level: float,
        stats: Dict[str, float]
    ) -> ValidationResult:
        """Validate using percentile-based thresholds."""
        # Calculate percentiles that correspond to confidence level
        alpha = 1 - confidence_level
        lower_percentile = (alpha / 2) * 100
        upper_percentile = (1 - alpha / 2) * 100

        ci_lower = np.percentile(samples, lower_percentile)
        ci_upper = np.percentile(samples, upper_percentile)

        # Check if percentile range is within thresholds
        is_valid = ci_lower >= lower_threshold and ci_upper <= upper_threshold

        # Calculate proportion of samples outside thresholds
        outside_count = sum(1 for s in samples if s < lower_threshold or s > upper_threshold)
        p_value = outside_count / len(samples)

        message = (
            f"Percentile validation: {lower_percentile:.1f}%-{upper_percentile:.1f}% range="
            f"[{ci_lower:.4f}, {ci_upper:.4f}], thresholds=[{lower_threshold:.4f}, {upper_threshold:.4f}]"
        )

        return ValidationResult(
            is_valid=is_valid,
            message=message,
            p_value=p_value,
            confidence_level=confidence_level,
            method_used=ValidationMethod.PERCENTILE,
            statistics={**stats, 'ci_lower': ci_lower, 'ci_upper': ci_upper}
        )

    def _validate_simple(
        self,
        samples: List[float],
        lower_threshold: float,
        upper_threshold: float,
        confidence_level: float,
        stats: Dict[str, float]
    ) -> ValidationResult:
        """Simple validation using mean and standard deviation."""
        mean = stats['mean']
        std = stats['std']

        # Calculate confidence interval using t-distribution approximation
        confidence_multiplier = self._get_confidence_multiplier(confidence_level)
        margin_of_error = confidence_multiplier * std / np.sqrt(len(samples))

        ci_lower = mean - margin_of_error
        ci_upper = mean + margin_of_error

        # Check if confidence interval is within thresholds
        is_valid = ci_lower >= lower_threshold and ci_upper <= upper_threshold

        # Simple p-value calculation
        if not is_valid:
            if ci_lower < lower_threshold:
                z_score = (lower_threshold - ci_lower) / (std / np.sqrt(len(samples)))
            else:
                z_score = (ci_upper - upper_threshold) / (std / np.sqrt(len(samples)))
            p_value = 2 * (1 - self._normal_cdf(abs(z_score)))
        else:
            p_value = 1.0

        message = (
            f"Simple validation: mean={mean:.4f}±{margin_of_error:.4f}, "
            f"thresholds=[{lower_threshold:.4f}, {upper_threshold:.4f}]"
        )

        return ValidationResult(
            is_valid=is_valid,
            message=message,
            p_value=p_value,
            confidence_level=confidence_level,
            method_used=ValidationMethod.SIMPLE,
            statistics={**stats, 'ci_lower': ci_lower, 'ci_upper': ci_upper, 'margin_of_error': margin_of_error}
        )

    def _perform_significance_test(self, baseline: List[float], comparison: List[float]) -> Tuple[Optional[float], str]:
        """Perform appropriate significance test."""
        try:
            from scipy import stats
            # Use Mann-Whitney U test (non-parametric)
            statistic, p_value = stats.mannwhitneyu(
                baseline, comparison, alternative='less'  # Test if baseline < comparison (degradation)
            )
            return p_value, "Mann-Whitney U"
        except ImportError:
            # Fallback to simple t-test approximation
            try:
                baseline_mean = statistics.mean(baseline)
                comparison_mean = statistics.mean(comparison)
                baseline_std = statistics.stdev(baseline) if len(baseline) > 1 else 0
                comparison_std = statistics.stdev(comparison) if len(comparison) > 1 else 0

                # Pooled standard error
                n1, n2 = len(baseline), len(comparison)
                pooled_se = np.sqrt((baseline_std**2 / n1) + (comparison_std**2 / n2))

                if pooled_se > 0:
                    t_stat = (comparison_mean - baseline_mean) / pooled_se
                    # Approximate p-value (one-tailed)
                    p_value = 1 - self._normal_cdf(t_stat)
                    return p_value, "Approximate t-test"
                else:
                    return None, "No variance"
            except Exception:
                return None, "No test"

    def _calculate_effect_size(self, baseline: List[float], comparison: List[float]) -> Optional[float]:
        """Calculate effect size (Cohen's d equivalent for robust statistics)."""
        try:
            baseline_median = statistics.median(baseline)
            comparison_median = statistics.median(comparison)

            # Use MAD instead of standard deviation for robustness
            baseline_mad = self._median_absolute_deviation(baseline)
            comparison_mad = self._median_absolute_deviation(comparison)

            # Pooled MAD
            pooled_mad = np.sqrt((baseline_mad**2 + comparison_mad**2) / 2)

            if pooled_mad > 0:
                effect_size = (comparison_median - baseline_median) / pooled_mad
                return effect_size
            else:
                return 0.0
        except Exception:
            return None

    def _median_absolute_deviation(self, samples: List[float]) -> float:
        """Calculate Median Absolute Deviation."""
        if not samples:
            return 0.0
        median = statistics.median(samples)
        deviations = [abs(x - median) for x in samples]
        return statistics.median(deviations)

    def _get_confidence_multiplier(self, confidence_level: float) -> float:
        """Get multiplier for confidence interval calculation."""
        multiplier_map = {
            0.90: 1.645,
            0.95: 1.96,
            0.99: 2.576,
        }
        closest_level = min(multiplier_map.keys(), key=lambda x: abs(x - confidence_level))
        return multiplier_map[closest_level]

    def _normal_cdf(self, z: float) -> float:
        """Approximate normal CDF using error function approximation."""
        # Simple approximation for normal CDF
        return 0.5 * (1 + np.tanh(z * np.sqrt(2 / np.pi)))

    def _detect_outliers_iqr(self, samples: List[float]) -> Tuple[List[float], List[int]]:
        """Detect outliers using IQR method."""
        q1 = np.percentile(samples, 25)
        q3 = np.percentile(samples, 75)
        iqr = q3 - q1

        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr

        outliers = []
        outlier_indices = []

        for i, sample in enumerate(samples):
            if sample < lower_bound or sample > upper_bound:
                outliers.append(sample)
                outlier_indices.append(i)

        return outliers, outlier_indices

    def _detect_outliers_mad(self, samples: List[float]) -> Tuple[List[float], List[int]]:
        """Detect outliers using MAD method."""
        median = statistics.median(samples)
        mad = self._median_absolute_deviation(samples)

        # Modified Z-score threshold (typically 3.5)
        threshold = 3.5
        mad_multiplier = 1.4826  # Consistency constant

        outliers = []
        outlier_indices = []

        for i, sample in enumerate(samples):
            modified_z_score = 0.6745 * (sample - median) / (mad * mad_multiplier) if mad > 0 else 0
            if abs(modified_z_score) > threshold:
                outliers.append(sample)
                outlier_indices.append(i)

        return outliers, outlier_indices

    def _detect_outliers_zscore(self, samples: List[float]) -> Tuple[List[float], List[int]]:
        """Detect outliers using Z-score method."""
        mean = statistics.mean(samples)
        std = statistics.stdev(samples) if len(samples) > 1 else 0

        threshold = 2.5
        outliers = []
        outlier_indices = []

        if std > 0:
            for i, sample in enumerate(samples):
                z_score = abs(sample - mean) / std
                if z_score > threshold:
                    outliers.append(sample)
                    outlier_indices.append(i)

        return outliers, outlier_indices