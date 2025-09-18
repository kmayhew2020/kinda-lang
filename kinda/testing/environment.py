"""Environment detection and adaptation for performance testing."""

import os
import platform
import psutil
import time
from dataclasses import dataclass
from typing import Dict, Optional, Tuple
from enum import Enum


class CIEnvironment(Enum):
    """Supported CI environment types."""
    GITHUB_ACTIONS = "github_actions"
    GITLAB_CI = "gitlab_ci"
    LOCAL_DEV = "local_dev"
    UNKNOWN = "unknown"


@dataclass
class PlatformProfile:
    """Platform capability profile for performance normalization."""
    cpu_cores: int
    memory_gb: float
    platform_family: str  # 'linux', 'darwin', 'windows'
    virtualized: bool
    baseline_factor: float  # Performance multiplier vs reference platform


@dataclass
class EnvironmentContext:
    """Complete environment context for test execution."""
    ci_environment: CIEnvironment
    platform_profile: PlatformProfile
    resource_constraints: Dict[str, float]
    performance_multiplier: float


class EnvironmentDetector:
    """Detects and profiles execution environment."""

    def __init__(self):
        self._cache: Optional[EnvironmentContext] = None

    def detect_ci_environment(self) -> CIEnvironment:
        """Detect CI environment from environment variables."""
        if os.getenv('GITHUB_ACTIONS'):
            return CIEnvironment.GITHUB_ACTIONS
        elif os.getenv('GITLAB_CI'):
            return CIEnvironment.GITLAB_CI
        elif any(ci_var in os.environ for ci_var in ['CI', 'CONTINUOUS_INTEGRATION']):
            return CIEnvironment.UNKNOWN
        else:
            return CIEnvironment.LOCAL_DEV

    def profile_platform(self) -> PlatformProfile:
        """Profile platform capabilities."""
        cpu_cores = psutil.cpu_count(logical=True)
        memory_gb = psutil.virtual_memory().total / (1024**3)
        platform_family = platform.system().lower()

        # Detect virtualization (heuristic-based)
        virtualized = self._detect_virtualization()

        # Calculate baseline factor based on known CI performance characteristics
        baseline_factor = self._calculate_baseline_factor(
            cpu_cores, memory_gb, platform_family, virtualized
        )

        return PlatformProfile(
            cpu_cores=cpu_cores,
            memory_gb=memory_gb,
            platform_family=platform_family,
            virtualized=virtualized,
            baseline_factor=baseline_factor
        )

    def get_environment_context(self) -> EnvironmentContext:
        """Get complete environment context with caching."""
        if self._cache is not None:
            return self._cache

        ci_env = self.detect_ci_environment()
        platform = self.profile_platform()
        constraints = self._measure_resource_constraints()

        # Calculate performance multiplier based on environment
        multiplier = self._calculate_performance_multiplier(ci_env, platform, constraints)

        self._cache = EnvironmentContext(
            ci_environment=ci_env,
            platform_profile=platform,
            resource_constraints=constraints,
            performance_multiplier=multiplier
        )

        return self._cache

    def _detect_virtualization(self) -> bool:
        """Detect if running in virtualized environment."""
        # Check for common virtualization indicators
        try:
            # Check for container indicators
            if os.path.exists('/.dockerenv'):
                return True

            # Check for hypervisor indicators in /proc/cpuinfo
            if os.path.exists('/proc/cpuinfo'):
                with open('/proc/cpuinfo', 'r') as f:
                    cpuinfo = f.read().lower()
                    if any(indicator in cpuinfo for indicator in ['vmware', 'virtualbox', 'kvm', 'xen']):
                        return True

            # Check for GitHub Actions runner
            if os.getenv('RUNNER_OS'):
                return True

            # Default to assuming virtualization in CI
            ci_env = self.detect_ci_environment()
            return ci_env != CIEnvironment.LOCAL_DEV

        except (OSError, IOError):
            # If we can't determine, assume virtualized for safety
            return True

    def _calculate_baseline_factor(self, cpu_cores: int, memory_gb: float,
                                 platform_family: str, virtualized: bool) -> float:
        """Calculate platform baseline performance factor."""
        # Start with neutral baseline
        factor = 1.0

        # Platform adjustments based on typical performance characteristics
        if platform_family == 'darwin':
            factor *= 0.9  # macOS typically 10% slower in CI
        elif platform_family == 'windows':
            factor *= 0.8  # Windows typically 20% slower in CI

        # Virtualization penalty
        if virtualized:
            factor *= 0.7  # Virtualized environments typically 30% slower

        # CPU core adjustment
        if cpu_cores < 2:
            factor *= 0.5  # Single core significantly slower
        elif cpu_cores >= 8:
            factor *= 1.2  # High core count machines typically faster

        # Memory adjustment
        if memory_gb < 4:
            factor *= 0.8  # Low memory can impact performance
        elif memory_gb >= 16:
            factor *= 1.1  # High memory typically better performance

        return factor

    def _measure_resource_constraints(self) -> Dict[str, float]:
        """Measure current resource constraints."""
        try:
            # Sample resource usage over brief period
            cpu_measurements = []
            memory_measurements = []

            for _ in range(3):
                cpu_measurements.append(psutil.cpu_percent(interval=0.1))
                memory_measurements.append(psutil.virtual_memory().percent)

            return {
                'cpu_load': sum(cpu_measurements) / len(cpu_measurements) / 100.0,
                'memory_pressure': sum(memory_measurements) / len(memory_measurements) / 100.0,
                'io_wait': self._get_io_wait(),
                'load_average': self._get_load_average()
            }
        except Exception:
            # Return neutral values if measurement fails
            return {
                'cpu_load': 0.5,
                'memory_pressure': 0.5,
                'io_wait': 0.1,
                'load_average': 1.0
            }

    def _get_io_wait(self) -> float:
        """Get I/O wait percentage (Linux only)."""
        try:
            if platform.system().lower() == 'linux':
                # Try to get I/O wait from /proc/stat
                with open('/proc/stat', 'r') as f:
                    line = f.readline()
                    if line.startswith('cpu '):
                        fields = line.split()
                        if len(fields) >= 6:
                            # cpu user nice system idle iowait
                            idle = int(fields[4])
                            iowait = int(fields[5]) if len(fields) > 5 else 0
                            total = sum(int(x) for x in fields[1:8])
                            return iowait / total if total > 0 else 0.0
            return 0.1  # Default for non-Linux systems
        except (OSError, IOError, ValueError):
            return 0.1

    def _get_load_average(self) -> float:
        """Get system load average."""
        try:
            if hasattr(os, 'getloadavg'):
                # Unix-like systems
                return os.getloadavg()[0]  # 1-minute load average
            else:
                # Windows or other systems - estimate from CPU count
                return psutil.cpu_count() * 0.5
        except (OSError, AttributeError):
            return 1.0

    def _calculate_performance_multiplier(self, ci_env: CIEnvironment,
                                        platform: PlatformProfile,
                                        constraints: Dict[str, float]) -> float:
        """Calculate overall performance multiplier for thresholds."""
        # Start with platform baseline
        multiplier = platform.baseline_factor

        # CI environment adjustments
        if ci_env == CIEnvironment.GITHUB_ACTIONS:
            multiplier *= 0.6  # GitHub Actions quite variable
        elif ci_env == CIEnvironment.UNKNOWN:
            multiplier *= 0.7  # Unknown CI - be conservative
        elif ci_env == CIEnvironment.LOCAL_DEV:
            multiplier *= 1.2  # Local dev typically more consistent

        # Resource constraint adjustments
        cpu_factor = max(0.3, 1.0 - constraints['cpu_load'] * 0.5)
        memory_factor = max(0.5, 1.0 - constraints['memory_pressure'] * 0.3)
        io_factor = max(0.7, 1.0 - constraints['io_wait'] * 2.0)

        multiplier *= cpu_factor * memory_factor * io_factor

        # Ensure minimum performance multiplier for safety
        return max(0.1, multiplier)

    def get_environment_key(self) -> str:
        """Get unique key for current environment for caching."""
        context = self.get_environment_context()
        return f"{context.ci_environment.value}_{context.platform_profile.platform_family}_{context.platform_profile.virtualized}"