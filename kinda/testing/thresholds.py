"""Statistical threshold management for performance tests."""

import json
import statistics
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class PerformanceBaseline:
    """Historical performance baseline data."""
    test_name: str
    environment_key: str
    median_time: float
    mad_time: float  # Median Absolute Deviation
    sample_count: int
    last_updated: str
    confidence_interval: Tuple[float, float]

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> 'PerformanceBaseline':
        """Create from dictionary for JSON deserialization."""
        return cls(**data)


class ThresholdManager:
    """Manages adaptive performance thresholds."""

    def __init__(self, cache_path: Optional[Path] = None):
        self.cache_path = cache_path or Path(".performance-cache/baselines.json")
        self.baselines: Dict[str, PerformanceBaseline] = {}
        self._load_baselines()

    def calculate_threshold(
        self,
        test_name: str,
        environment_key: str,
        current_samples: List[float],
        confidence_level: float = 0.95
    ) -> Tuple[float, float]:
        """Calculate adaptive threshold for test."""
        baseline = self.get_baseline(test_name, environment_key)

        if baseline is None:
            # No historical data - use current samples to establish baseline
            return self._calculate_initial_threshold(current_samples, confidence_level)

        # Use historical baseline with statistical adjustment
        return self._calculate_adaptive_threshold(baseline, current_samples, confidence_level)

    def update_baseline(
        self,
        test_name: str,
        environment_key: str,
        new_samples: List[float]
    ) -> None:
        """Update baseline with new performance data."""
        baseline_key = f"{test_name}:{environment_key}"

        if baseline_key in self.baselines:
            # Update existing baseline with exponential smoothing
            self._update_existing_baseline(baseline_key, new_samples)
        else:
            # Create new baseline
            self._create_new_baseline(test_name, environment_key, new_samples)

        self._save_baselines()

    def get_baseline(self, test_name: str, environment_key: str) -> Optional[PerformanceBaseline]:
        """Get baseline for specific test and environment."""
        baseline_key = f"{test_name}:{environment_key}"
        return self.baselines.get(baseline_key)

    def _calculate_initial_threshold(
        self,
        samples: List[float],
        confidence_level: float
    ) -> Tuple[float, float]:
        """Calculate initial threshold from current samples."""
        if not samples:
            return 0.0, float('inf')

        # Use robust statistics
        median = statistics.median(samples)
        mad = self._median_absolute_deviation(samples)

        # Calculate confidence interval using bootstrap method
        lower_bound, upper_bound = self._bootstrap_confidence_interval(
            samples, confidence_level
        )

        # For initial thresholds, use wider bounds for safety
        threshold_multiplier = self._get_threshold_multiplier(confidence_level)

        lower_threshold = max(0, lower_bound - mad * threshold_multiplier)
        upper_threshold = upper_bound + mad * threshold_multiplier * 2  # More lenient upper bound

        return lower_threshold, upper_threshold

    def _calculate_adaptive_threshold(
        self,
        baseline: PerformanceBaseline,
        current_samples: List[float],
        confidence_level: float
    ) -> Tuple[float, float]:
        """Calculate threshold using historical baseline and current performance."""
        if not current_samples:
            # Use baseline confidence interval if no current samples
            return baseline.confidence_interval

        # Use robust statistics (median + MAD) instead of mean + std
        current_median = statistics.median(current_samples)
        current_mad = self._median_absolute_deviation(current_samples)

        # Calculate adaptation factor based on current variability
        if baseline.mad_time > 0:
            adaptation_factor = min(2.0, max(0.5, current_mad / baseline.mad_time))
        else:
            adaptation_factor = 1.0

        # Calculate threshold using historical baseline with adaptation
        threshold_multiplier = self._get_threshold_multiplier(confidence_level)

        # Use exponential smoothing to blend baseline with current performance
        smoothing_factor = 0.3  # 30% weight to current, 70% to historical
        blended_median = (1 - smoothing_factor) * baseline.median_time + smoothing_factor * current_median
        blended_mad = (1 - smoothing_factor) * baseline.mad_time + smoothing_factor * current_mad

        lower_threshold = max(0, blended_median - blended_mad * threshold_multiplier * adaptation_factor)
        upper_threshold = blended_median + blended_mad * threshold_multiplier * adaptation_factor * 2

        return lower_threshold, upper_threshold

    def _update_existing_baseline(self, baseline_key: str, new_samples: List[float]) -> None:
        """Update existing baseline with exponential smoothing."""
        baseline = self.baselines[baseline_key]

        if not new_samples:
            return

        # Calculate statistics for new samples
        new_median = statistics.median(new_samples)
        new_mad = self._median_absolute_deviation(new_samples)
        new_confidence_interval = self._bootstrap_confidence_interval(new_samples, 0.95)

        # Exponential smoothing parameters
        alpha = 0.3  # Smoothing factor (30% weight to new data)

        # Update baseline with smoothed values
        updated_median = (1 - alpha) * baseline.median_time + alpha * new_median
        updated_mad = (1 - alpha) * baseline.mad_time + alpha * new_mad

        # Update confidence interval (blend endpoints)
        updated_ci = (
            (1 - alpha) * baseline.confidence_interval[0] + alpha * new_confidence_interval[0],
            (1 - alpha) * baseline.confidence_interval[1] + alpha * new_confidence_interval[1]
        )

        # Update baseline
        self.baselines[baseline_key] = PerformanceBaseline(
            test_name=baseline.test_name,
            environment_key=baseline.environment_key,
            median_time=updated_median,
            mad_time=updated_mad,
            sample_count=baseline.sample_count + len(new_samples),
            last_updated=datetime.now().isoformat(),
            confidence_interval=updated_ci
        )

    def _create_new_baseline(self, test_name: str, environment_key: str, samples: List[float]) -> None:
        """Create new baseline from samples."""
        if not samples:
            return

        baseline_key = f"{test_name}:{environment_key}"

        median = statistics.median(samples)
        mad = self._median_absolute_deviation(samples)
        confidence_interval = self._bootstrap_confidence_interval(samples, 0.95)

        self.baselines[baseline_key] = PerformanceBaseline(
            test_name=test_name,
            environment_key=environment_key,
            median_time=median,
            mad_time=mad,
            sample_count=len(samples),
            last_updated=datetime.now().isoformat(),
            confidence_interval=confidence_interval
        )

    def _median_absolute_deviation(self, samples: List[float]) -> float:
        """Calculate Median Absolute Deviation (MAD) - more robust than standard deviation."""
        if not samples:
            return 0.0

        median = statistics.median(samples)
        deviations = [abs(x - median) for x in samples]
        return statistics.median(deviations)

    def _bootstrap_confidence_interval(self, samples: List[float], confidence_level: float) -> Tuple[float, float]:
        """Calculate confidence interval using bootstrap method."""
        if len(samples) < 2:
            if samples:
                return samples[0], samples[0]
            return 0.0, 0.0

        try:
            # Simple bootstrap implementation
            bootstrap_medians = []
            n_bootstrap = min(1000, len(samples) * 10)  # Reasonable bootstrap size

            for _ in range(n_bootstrap):
                # Bootstrap resample
                bootstrap_sample = np.random.choice(samples, size=len(samples), replace=True)
                bootstrap_medians.append(statistics.median(bootstrap_sample))

            # Calculate percentiles for confidence interval
            alpha = 1 - confidence_level
            lower_percentile = (alpha / 2) * 100
            upper_percentile = (1 - alpha / 2) * 100

            lower_bound = np.percentile(bootstrap_medians, lower_percentile)
            upper_bound = np.percentile(bootstrap_medians, upper_percentile)

            return float(lower_bound), float(upper_bound)

        except Exception:
            # Fallback to simple percentile method
            sorted_samples = sorted(samples)
            lower_idx = max(0, int(len(samples) * 0.025))
            upper_idx = min(len(samples) - 1, int(len(samples) * 0.975))
            return sorted_samples[lower_idx], sorted_samples[upper_idx]

    def _get_threshold_multiplier(self, confidence_level: float) -> float:
        """Get threshold multiplier based on confidence level."""
        # Map confidence level to multiplier (similar to z-scores)
        multiplier_map = {
            0.90: 1.65,  # 90% confidence
            0.95: 1.96,  # 95% confidence
            0.99: 2.58,  # 99% confidence
        }

        # Find closest confidence level
        closest_level = min(multiplier_map.keys(), key=lambda x: abs(x - confidence_level))
        return multiplier_map[closest_level]

    def _load_baselines(self) -> None:
        """Load baselines from cache file."""
        try:
            if self.cache_path.exists():
                with open(self.cache_path, 'r') as f:
                    data = json.load(f)

                # Validate and load baselines
                for key, baseline_data in data.items():
                    try:
                        baseline = PerformanceBaseline.from_dict(baseline_data)
                        self.baselines[key] = baseline
                    except Exception as e:
                        # Skip invalid baseline entries
                        print(f"Warning: Failed to load baseline {key}: {e}")
                        continue

        except (FileNotFoundError, json.JSONDecodeError, Exception):
            # Start fresh if cache is corrupted or missing
            self.baselines = {}
            self._create_cache_directory()

    def _save_baselines(self) -> None:
        """Save baselines to cache file."""
        try:
            # Ensure cache directory exists
            self.cache_path.parent.mkdir(parents=True, exist_ok=True)

            # Convert baselines to serializable format
            data = {key: baseline.to_dict() for key, baseline in self.baselines.items()}

            # Write atomically (write to temp file, then rename)
            temp_path = self.cache_path.with_suffix('.tmp')
            with open(temp_path, 'w') as f:
                json.dump(data, f, indent=2)

            temp_path.rename(self.cache_path)

        except Exception as e:
            print(f"Warning: Failed to save performance baselines: {e}")

    def _create_cache_directory(self) -> None:
        """Create cache directory if it doesn't exist."""
        try:
            self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        except OSError:
            # Use current directory if cache directory can't be created
            self.cache_path = Path("baselines.json")

    def cleanup_old_baselines(self, retention_days: int = 30) -> None:
        """Remove baselines older than retention period."""
        cutoff_date = datetime.now()
        cutoff_date = cutoff_date.replace(day=cutoff_date.day - retention_days)
        cutoff_iso = cutoff_date.isoformat()

        keys_to_remove = []
        for key, baseline in self.baselines.items():
            if baseline.last_updated < cutoff_iso:
                keys_to_remove.append(key)

        for key in keys_to_remove:
            del self.baselines[key]

        if keys_to_remove:
            self._save_baselines()