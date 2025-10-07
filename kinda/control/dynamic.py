"""
Dynamic Probability Management for Kinda-Lang

Epic #127: Enhanced probability control - Dynamic adjustment of probabilities
based on runtime feedback, learning, and adaptive behavior.
"""

import threading
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Callable, Any, Tuple
from collections import defaultdict, deque

from .context import ProbabilityContext, ProbabilityProfile, ProbabilityMode


class RuleCondition(Enum):
    """Conditions for probability adjustment rules"""

    TIME_BASED = "time_based"
    CALL_COUNT = "call_count"
    SUCCESS_RATE = "success_rate"
    PERFORMANCE = "performance"
    ERROR_RATE = "error_rate"
    CUSTOM = "custom"


class AdjustmentType(Enum):
    """Types of probability adjustments"""

    ABSOLUTE = "absolute"  # Set to specific value
    RELATIVE = "relative"  # Add/subtract delta
    MULTIPLICATIVE = "multiplicative"  # Multiply by factor
    EXPONENTIAL = "exponential"  # Exponential decay/growth


@dataclass
class ProbabilityRule:
    """Rule for dynamic probability adjustment"""

    name: str
    construct_name: str
    condition: RuleCondition
    threshold: float
    adjustment_type: AdjustmentType
    adjustment_value: float
    min_probability: float = 0.0
    max_probability: float = 1.0
    enabled: bool = True
    description: str = ""

    def evaluate(self, metrics: Dict[str, Any]) -> bool:
        """Evaluate if rule condition is met"""
        if not self.enabled:
            return False

        if self.condition == RuleCondition.TIME_BASED:
            elapsed = metrics.get("elapsed_time", 0)
            return elapsed >= self.threshold

        elif self.condition == RuleCondition.CALL_COUNT:
            calls = metrics.get("call_count", 0)
            return calls >= self.threshold

        elif self.condition == RuleCondition.SUCCESS_RATE:
            success_rate = metrics.get("success_rate", 1.0)
            return success_rate <= self.threshold

        elif self.condition == RuleCondition.PERFORMANCE:
            performance = metrics.get("performance_score", 1.0)
            return performance <= self.threshold

        elif self.condition == RuleCondition.ERROR_RATE:
            error_rate = metrics.get("error_rate", 0.0)
            return error_rate >= self.threshold

        return False

    def apply_adjustment(self, current_probability: float) -> float:
        """Apply adjustment to current probability"""
        if self.adjustment_type == AdjustmentType.ABSOLUTE:
            new_prob = self.adjustment_value

        elif self.adjustment_type == AdjustmentType.RELATIVE:
            new_prob = current_probability + self.adjustment_value

        elif self.adjustment_type == AdjustmentType.MULTIPLICATIVE:
            new_prob = current_probability * self.adjustment_value

        elif self.adjustment_type == AdjustmentType.EXPONENTIAL:
            # Exponential adjustment based on distance from 0.5
            center_distance = abs(current_probability - 0.5)
            if current_probability > 0.5:
                new_prob = 0.5 + center_distance * self.adjustment_value
            else:
                new_prob = 0.5 - center_distance * self.adjustment_value

        else:
            new_prob = current_probability

        # Clamp to bounds
        return max(self.min_probability, min(self.max_probability, new_prob))


@dataclass
class PerformanceMetrics:
    """Performance and behavior metrics for a construct"""

    construct_name: str
    call_count: int = 0
    success_count: int = 0
    error_count: int = 0
    total_execution_time: float = 0.0
    last_call_time: Optional[float] = None
    probability_history: deque = field(default_factory=lambda: deque(maxlen=100))
    recent_adjustments: List[Tuple[float, str]] = field(default_factory=list)

    @property
    def success_rate(self) -> float:
        """Calculate success rate"""
        if self.call_count == 0:
            return 1.0
        return self.success_count / self.call_count

    @property
    def error_rate(self) -> float:
        """Calculate error rate"""
        if self.call_count == 0:
            return 0.0
        return self.error_count / self.call_count

    @property
    def average_execution_time(self) -> float:
        """Calculate average execution time"""
        if self.call_count == 0:
            return 0.0
        return self.total_execution_time / self.call_count

    def record_call(self, execution_time: float, success: bool, probability_used: float):
        """Record a construct call"""
        self.call_count += 1
        self.total_execution_time += execution_time
        self.last_call_time = time.time()

        if success:
            self.success_count += 1
        else:
            self.error_count += 1

        self.probability_history.append(probability_used)

    def get_metrics_dict(self, elapsed_time: float = 0.0) -> Dict[str, Any]:
        """Get metrics as dictionary for rule evaluation"""
        return {
            "call_count": self.call_count,
            "success_rate": self.success_rate,
            "error_rate": self.error_rate,
            "performance_score": 1.0 / (1.0 + self.average_execution_time),
            "elapsed_time": elapsed_time,
        }


class FeedbackCollector:
    """Collects feedback for probability adjustments"""

    def __init__(self):
        self.feedback_callbacks: List[Callable[[str, Dict[str, Any]], None]] = []

    def register_callback(self, callback: Callable[[str, Dict[str, Any]], None]):
        """Register a feedback callback"""
        self.feedback_callbacks.append(callback)

    def collect_feedback(self, construct_name: str, context: Dict[str, Any]):
        """Collect feedback from registered callbacks"""
        for callback in self.feedback_callbacks:
            try:
                callback(construct_name, context)
            except Exception:
                # Silent fail to avoid disrupting main execution
                pass


class DynamicProbabilityManager:
    """
    Manager for dynamic probability adjustments based on runtime feedback.

    This class provides adaptive probability control that can learn from
    execution patterns and adjust probabilities to optimize behavior.
    """

    def __init__(self):
        self.rules: List[ProbabilityRule] = []
        self.metrics: Dict[str, PerformanceMetrics] = {}
        self.start_time = time.time()
        self.enabled = True
        self.adjustment_history: List[Tuple[float, str, str, float, float]] = []
        self.feedback_collector = FeedbackCollector()
        self._lock = threading.Lock()

        # Initialize with some default rules
        self._initialize_default_rules()

    def _initialize_default_rules(self):
        """Initialize with sensible default rules"""

        # Reduce 'sometimes' probability if error rate is high
        self.add_rule(
            ProbabilityRule(
                name="sometimes_error_reduction",
                construct_name="sometimes",
                condition=RuleCondition.ERROR_RATE,
                threshold=0.1,  # 10% error rate
                adjustment_type=AdjustmentType.MULTIPLICATIVE,
                adjustment_value=0.8,  # Reduce by 20%
                description="Reduce 'sometimes' probability when error rate is high",
            )
        )

        # Increase 'rarely' probability if it's never triggering
        self.add_rule(
            ProbabilityRule(
                name="rarely_activation_boost",
                construct_name="rarely",
                condition=RuleCondition.CALL_COUNT,
                threshold=50,  # After 50 calls
                adjustment_type=AdjustmentType.RELATIVE,
                adjustment_value=0.1,  # Increase by 10%
                max_probability=0.5,  # Don't make it too common
                description="Boost 'rarely' probability if it's not triggering enough",
            )
        )

        # Performance-based adjustment for 'kinda_repeat'
        self.add_rule(
            ProbabilityRule(
                name="kinda_repeat_performance",
                construct_name="kinda_repeat",
                condition=RuleCondition.PERFORMANCE,
                threshold=0.5,  # Performance score below 0.5
                adjustment_type=AdjustmentType.MULTIPLICATIVE,
                adjustment_value=0.9,  # Slight reduction
                description="Reduce loop fuzziness if performance is poor",
            )
        )

    def add_rule(self, rule: ProbabilityRule):
        """Add a dynamic adjustment rule"""
        with self._lock:
            self.rules.append(rule)

    def remove_rule(self, rule_name: str) -> bool:
        """Remove a rule by name"""
        with self._lock:
            for i, rule in enumerate(self.rules):
                if rule.name == rule_name:
                    del self.rules[i]
                    return True
        return False

    def enable_rule(self, rule_name: str) -> bool:
        """Enable a rule"""
        with self._lock:
            for rule in self.rules:
                if rule.name == rule_name:
                    rule.enabled = True
                    return True
        return False

    def disable_rule(self, rule_name: str) -> bool:
        """Disable a rule"""
        with self._lock:
            for rule in self.rules:
                if rule.name == rule_name:
                    rule.enabled = False
                    return True
        return False

    def get_dynamic_probability(
        self, construct_name: str, base_probability: float, context: Optional[Dict[str, Any]] = None
    ) -> float:
        """
        Get dynamically adjusted probability for a construct.

        Args:
            construct_name: Name of the construct
            base_probability: Base probability before adjustments
            context: Additional context for decision making

        Returns:
            Adjusted probability value
        """
        if not self.enabled:
            return base_probability

        with self._lock:
            # Ensure metrics exist for this construct
            if construct_name not in self.metrics:
                self.metrics[construct_name] = PerformanceMetrics(construct_name)

            metrics = self.metrics[construct_name]
            elapsed_time = time.time() - self.start_time

            # Get current metrics for rule evaluation
            current_metrics = metrics.get_metrics_dict(elapsed_time)
            if context:
                current_metrics.update(context)

            # Apply rules
            adjusted_probability = base_probability
            applied_rules = []

            for rule in self.rules:
                if rule.construct_name == construct_name and rule.evaluate(current_metrics):
                    old_probability = adjusted_probability
                    adjusted_probability = rule.apply_adjustment(adjusted_probability)

                    # Record the adjustment
                    if old_probability != adjusted_probability:
                        applied_rules.append(rule.name)
                        self.adjustment_history.append(
                            (
                                time.time(),
                                rule.name,
                                construct_name,
                                old_probability,
                                adjusted_probability,
                            )
                        )

            # Record the probability in history
            metrics.probability_history.append(adjusted_probability)

            return adjusted_probability

    def record_construct_execution(
        self,
        construct_name: str,
        execution_time: float,
        success: bool,
        probability_used: float,
        context: Optional[Dict[str, Any]] = None,
    ):
        """
        Record the execution of a construct for learning.

        Args:
            construct_name: Name of the construct that executed
            execution_time: Time taken to execute
            success: Whether execution was successful
            probability_used: Probability value that was used
            context: Additional context about the execution
        """
        with self._lock:
            if construct_name not in self.metrics:
                self.metrics[construct_name] = PerformanceMetrics(construct_name)

            metrics = self.metrics[construct_name]
            metrics.record_call(execution_time, success, probability_used)

            # Collect feedback
            feedback_context = {
                "execution_time": execution_time,
                "success": success,
                "probability_used": probability_used,
                "metrics": metrics.get_metrics_dict(),
            }
            if context:
                feedback_context.update(context)

            self.feedback_collector.collect_feedback(construct_name, feedback_context)

    def get_construct_metrics(self, construct_name: str) -> Optional[PerformanceMetrics]:
        """Get performance metrics for a construct"""
        return self.metrics.get(construct_name)

    def get_all_metrics(self) -> Dict[str, PerformanceMetrics]:
        """Get all performance metrics"""
        return self.metrics.copy()

    def get_adjustment_history(
        self, construct_name: Optional[str] = None, limit: Optional[int] = None
    ) -> List[Tuple[float, str, str, float, float]]:
        """
        Get history of probability adjustments.

        Args:
            construct_name: Filter by construct name (None for all)
            limit: Limit number of results (None for all)

        Returns:
            List of (timestamp, rule_name, construct_name, old_prob, new_prob)
        """
        history = self.adjustment_history

        if construct_name:
            history = [h for h in history if h[2] == construct_name]

        if limit:
            history = history[-limit:]

        return history

    def create_adaptive_profile(
        self, base_profile: ProbabilityProfile, adaptation_strength: float = 0.1
    ) -> ProbabilityProfile:
        """
        Create an adaptive profile based on learned behavior.

        Args:
            base_profile: Base profile to adapt
            adaptation_strength: How much to weight learned adjustments (0.0-1.0)

        Returns:
            New adaptive profile
        """
        adapted_overrides = base_profile.construct_overrides.copy()

        for construct_name, metrics in self.metrics.items():
            if metrics.probability_history and construct_name in adapted_overrides:
                # Calculate average of recent probabilities
                recent_probs = list(metrics.probability_history)[-10:]  # Last 10 values
                if recent_probs:
                    learned_avg = sum(recent_probs) / len(recent_probs)
                    original = adapted_overrides[construct_name]

                    # Blend original with learned average
                    adapted_overrides[construct_name] = (
                        original * (1 - adaptation_strength) + learned_avg * adaptation_strength
                    )

        return ProbabilityProfile(
            name=f"{base_profile.name}_adapted",
            description=f"Adaptive version of {base_profile.name}",
            mode=base_profile.mode,
            construct_overrides=adapted_overrides,
            personality_config=base_profile.personality_config.copy(),
            seed=base_profile.seed,
        )

    def reset_metrics(self, construct_name: Optional[str] = None):
        """Reset metrics for a construct or all constructs"""
        with self._lock:
            if construct_name:
                if construct_name in self.metrics:
                    self.metrics[construct_name] = PerformanceMetrics(construct_name)
            else:
                self.metrics.clear()
                self.adjustment_history.clear()

    def get_summary_report(self) -> Dict[str, Any]:
        """Get a summary report of dynamic behavior"""
        with self._lock:
            total_calls = sum(m.call_count for m in self.metrics.values())
            total_adjustments = len(self.adjustment_history)

            construct_summaries = {}
            for name, metrics in self.metrics.items():
                construct_summaries[name] = {
                    "call_count": metrics.call_count,
                    "success_rate": metrics.success_rate,
                    "error_rate": metrics.error_rate,
                    "avg_execution_time": metrics.average_execution_time,
                    "current_probability": (
                        list(metrics.probability_history)[-1]
                        if metrics.probability_history
                        else None
                    ),
                }

            return {
                "total_constructs_tracked": len(self.metrics),
                "total_calls": total_calls,
                "total_adjustments": total_adjustments,
                "active_rules": len([r for r in self.rules if r.enabled]),
                "total_rules": len(self.rules),
                "uptime_seconds": time.time() - self.start_time,
                "construct_summaries": construct_summaries,
            }

    def export_learning_data(self) -> Dict[str, Any]:
        """Export learning data for analysis or persistence"""
        return {
            "metrics": {
                name: {
                    "call_count": m.call_count,
                    "success_count": m.success_count,
                    "error_count": m.error_count,
                    "total_execution_time": m.total_execution_time,
                    "probability_history": list(m.probability_history),
                }
                for name, m in self.metrics.items()
            },
            "adjustment_history": self.adjustment_history,
            "rules": [
                {
                    "name": r.name,
                    "construct_name": r.construct_name,
                    "condition": r.condition.value,
                    "threshold": r.threshold,
                    "adjustment_type": r.adjustment_type.value,
                    "adjustment_value": r.adjustment_value,
                    "enabled": r.enabled,
                }
                for r in self.rules
            ],
        }

    def import_learning_data(self, data: Dict[str, Any]):
        """Import previously exported learning data"""
        with self._lock:
            # Import metrics
            if "metrics" in data:
                for name, metric_data in data["metrics"].items():
                    metrics = PerformanceMetrics(name)
                    metrics.call_count = metric_data.get("call_count", 0)
                    metrics.success_count = metric_data.get("success_count", 0)
                    metrics.error_count = metric_data.get("error_count", 0)
                    metrics.total_execution_time = metric_data.get("total_execution_time", 0.0)

                    prob_history = metric_data.get("probability_history", [])
                    metrics.probability_history = deque(prob_history, maxlen=100)

                    self.metrics[name] = metrics

            # Import adjustment history
            if "adjustment_history" in data:
                self.adjustment_history = data["adjustment_history"]


# Global dynamic manager instance
_dynamic_manager: Optional[DynamicProbabilityManager] = None


def get_dynamic_manager() -> DynamicProbabilityManager:
    """Get the global dynamic probability manager"""
    global _dynamic_manager
    if _dynamic_manager is None:
        _dynamic_manager = DynamicProbabilityManager()
    return _dynamic_manager


def set_dynamic_manager(manager: DynamicProbabilityManager):
    """Set the global dynamic probability manager"""
    global _dynamic_manager
    _dynamic_manager = manager


# Integration with ProbabilityContext
class DynamicProbabilityContext(ProbabilityContext):
    """Extended probability context with dynamic adjustment support"""

    def __init__(self, *args, enable_dynamic: bool = True, **kwargs):
        super().__init__(*args, **kwargs)
        self.enable_dynamic = enable_dynamic
        self.dynamic_manager = get_dynamic_manager() if enable_dynamic else None

    def get_probability(self, construct_name: str, default: float = 0.5) -> float:
        """Get probability with dynamic adjustments"""
        # Get base probability from parent implementation
        base_probability = super().get_probability(construct_name, default)

        # Apply dynamic adjustments if enabled
        if self.enable_dynamic and self.dynamic_manager:
            return self.dynamic_manager.get_dynamic_probability(construct_name, base_probability)

        return base_probability
