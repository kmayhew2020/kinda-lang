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

__all__ = [
    "EnvironmentDetector",
    "EnvironmentContext",
    "CIEnvironment",
    "PlatformProfile",
    "ThresholdManager",
    "PerformanceBaseline",
    "DependencyResolver",
    "StatisticalValidator",
    "PerformanceTestFramework",
]