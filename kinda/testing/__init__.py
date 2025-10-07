"""Performance testing framework for kinda-lang.

This module provides a comprehensive framework for statistical performance testing
that eliminates CI instability and provides robust validation for probabilistic
language constructs.
"""

from .environment import EnvironmentDetector, EnvironmentContext, CIEnvironment, PlatformProfile
from .thresholds import ThresholdManager, PerformanceBaseline
from .dependencies import DependencyResolver
from .statistics import StatisticalValidator
from .pytest_plugin import PerformanceTestFramework

# Statistical Testing Framework Components
from .confidence import (
    ConfidenceCalculator,
    ConfidenceInterval,
    ConfidenceMethod,
    wilson_score_interval,
    bootstrap_confidence_interval,
    StatisticalFrameworkError,
    ConfidenceIntervalError,
    InsufficientDataError,
)
from .assertions import (
    StatisticalTester,
    StatisticalValidationError,
    StatisticalConfig,
    statistical_assert,
    binomial_assert,
    proportion_assert,
    eventually_assert,
)
from .distributions import (
    DistributionTester,
    DistributionTestResult,
    DistributionTest,
    chi_square_test,
    binomial_distribution_test,
    personality_distribution_test,
)

__all__ = [
    # Performance Testing Framework
    "EnvironmentDetector",
    "EnvironmentContext",
    "CIEnvironment",
    "PlatformProfile",
    "ThresholdManager",
    "PerformanceBaseline",
    "DependencyResolver",
    "StatisticalValidator",
    "PerformanceTestFramework",
    # Statistical Testing Framework - Confidence Intervals
    "ConfidenceCalculator",
    "ConfidenceInterval",
    "ConfidenceMethod",
    "wilson_score_interval",
    "bootstrap_confidence_interval",
    "StatisticalFrameworkError",
    "ConfidenceIntervalError",
    "InsufficientDataError",
    # Statistical Testing Framework - Assertions
    "StatisticalTester",
    "StatisticalValidationError",
    "StatisticalConfig",
    "statistical_assert",
    "binomial_assert",
    "proportion_assert",
    "eventually_assert",
    # Statistical Testing Framework - Distributions
    "DistributionTester",
    "DistributionTestResult",
    "DistributionTest",
    "chi_square_test",
    "binomial_distribution_test",
    "personality_distribution_test",
]
