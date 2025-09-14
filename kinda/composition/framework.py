# kinda/composition/framework.py

"""
Kinda-Lang Composition Framework

Core framework providing infrastructure for creating composite constructs
built from basic probabilistic primitives.
"""

import time
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Callable, Union
from dataclasses import dataclass
from enum import Enum


class CompositionStrategy(Enum):
    """Strategy patterns for construct composition."""
    UNION = "union"              # gate1 OR gate2 (like Task 1 sorta)
    INTERSECTION = "intersection" # gate1 AND gate2
    SEQUENTIAL = "sequential"     # gate1 then gate2 if gate1 succeeds
    WEIGHTED = "weighted"         # Weighted combination of results
    CONDITIONAL = "conditional"   # Execute gate2 based on gate1 result


@dataclass
class CompositionConfig:
    """Configuration for construct composition."""
    strategy: CompositionStrategy
    personality_bridges: Dict[str, float]  # Bridge probabilities per personality
    performance_target: float = 0.20      # Max 20% overhead
    dependency_validation: bool = True
    statistical_validation: bool = True
    debug_tracing: bool = False


class CompositeConstruct(ABC):
    """Base class for all composite constructs built from basic constructs."""

    def __init__(self, name: str, config: CompositionConfig):
        self.name = name
        self.config = config
        self.dependencies = []
        self.composition_history = []
        self.performance_metrics = {}

    @abstractmethod
    def get_basic_constructs(self) -> List[str]:
        """Return list of basic construct names this composite depends on."""
        pass

    @abstractmethod
    def compose(self, *args, **kwargs) -> Any:
        """Execute the composition logic."""
        pass

    @abstractmethod
    def get_target_probabilities(self) -> Dict[str, float]:
        """Return target probability behavior for each personality."""
        pass

    def validate_dependencies(self) -> bool:
        """Validate that all required basic constructs are available."""
        from kinda.composition.validation import validate_construct_dependencies
        return validate_construct_dependencies(self.get_basic_constructs())

    def execute_with_tracing(self, *args, **kwargs) -> Any:
        """Execute composition with optional debug tracing."""
        if self.config.debug_tracing:
            return self._execute_traced(*args, **kwargs)
        return self.compose(*args, **kwargs)

    def _execute_traced(self, *args, **kwargs) -> Any:
        """Execute with debug tracing enabled."""
        from kinda.personality import get_personality

        trace_data = {
            'construct': self.name,
            'inputs': args,
            'personality': get_personality().mood,
            'timestamp': time.time()
        }

        result = self.compose(*args, **kwargs)

        trace_data['result'] = result
        trace_data['duration'] = time.time() - trace_data['timestamp']
        self.composition_history.append(trace_data)

        return result


class PerformanceMonitor:
    """Monitors and reports performance metrics for compositions."""

    def __init__(self):
        self.execution_times = {}
        self.memory_usage = {}
        self.error_rates = {}

    def record_execution(self, construct_name: str,
                        execution_time: float, success: bool):
        """Record execution metrics."""

        if construct_name not in self.execution_times:
            self.execution_times[construct_name] = []
            self.error_rates[construct_name] = {'total': 0, 'errors': 0}

        self.execution_times[construct_name].append(execution_time)
        self.error_rates[construct_name]['total'] += 1

        if not success:
            self.error_rates[construct_name]['errors'] += 1

    def get_performance_report(self, construct_name: str) -> Dict[str, Any]:
        """Get performance report for a construct."""

        if construct_name not in self.execution_times:
            return {}

        times = self.execution_times[construct_name]
        errors = self.error_rates[construct_name]

        return {
            'construct': construct_name,
            'total_executions': len(times),
            'avg_time': sum(times) / len(times),
            'min_time': min(times),
            'max_time': max(times),
            'error_rate': errors['errors'] / errors['total'] if errors['total'] > 0 else 0.0
        }


class CompositionEngine:
    """Core engine for executing construct compositions."""

    def __init__(self):
        self.construct_registry = {}
        self.dependency_graph = {}
        self.performance_monitor = PerformanceMonitor()

    def register_composite(self, construct: CompositeConstruct):
        """Register a composite construct with dependency tracking."""
        self.construct_registry[construct.name] = construct
        self._update_dependency_graph(construct)

    def _update_dependency_graph(self, construct: CompositeConstruct):
        """Update dependency graph with new construct."""
        self.dependency_graph[construct.name] = construct.get_basic_constructs()

    def execute_composition(self, construct_name: str,
                          strategy: CompositionStrategy,
                          gates: List[Callable],
                          *args, **kwargs) -> Any:
        """Execute a composition using specified strategy."""

        # Performance monitoring
        start_time = time.perf_counter()

        try:
            result = self._execute_strategy(strategy, gates, *args, **kwargs)

            # Record performance metrics
            execution_time = time.perf_counter() - start_time
            self.performance_monitor.record_execution(
                construct_name, execution_time, True
            )

            return result

        except Exception as e:
            execution_time = time.perf_counter() - start_time
            self.performance_monitor.record_execution(
                construct_name, execution_time, False
            )
            raise

    def _execute_strategy(self, strategy: CompositionStrategy,
                         gates: List[Callable], *args, **kwargs) -> Any:
        """Execute specific composition strategy."""

        if strategy == CompositionStrategy.UNION:
            return self._execute_union(gates, *args, **kwargs)
        elif strategy == CompositionStrategy.INTERSECTION:
            return self._execute_intersection(gates, *args, **kwargs)
        elif strategy == CompositionStrategy.SEQUENTIAL:
            return self._execute_sequential(gates, *args, **kwargs)
        elif strategy == CompositionStrategy.WEIGHTED:
            return self._execute_weighted(gates, *args, **kwargs)
        elif strategy == CompositionStrategy.CONDITIONAL:
            return self._execute_conditional(gates, *args, **kwargs)
        else:
            raise ValueError(f"Unknown composition strategy: {strategy}")

    def _execute_union(self, gates: List[Callable], *args, **kwargs) -> bool:
        """Execute union composition (OR logic)."""
        results = []
        for gate in gates:
            try:
                result = gate(*args, **kwargs)
                results.append(result)
                if result:  # Short-circuit on first True
                    return True
            except Exception:
                results.append(False)
        return any(results)

    def _execute_intersection(self, gates: List[Callable], *args, **kwargs) -> bool:
        """Execute intersection composition (AND logic)."""
        for gate in gates:
            try:
                result = gate(*args, **kwargs)
                if not result:  # Short-circuit on first False
                    return False
            except Exception:
                return False
        return True

    def _execute_sequential(self, gates: List[Callable], *args, **kwargs) -> Any:
        """Execute sequential composition (gate1 then gate2 if gate1 succeeds)."""
        for gate in gates:
            result = gate(*args, **kwargs)
            if not result:
                return result
        return result  # Return last successful result

    def _execute_weighted(self, gates: List[Callable],
                         weights: List[float] = None, *args, **kwargs) -> float:
        """Execute weighted composition."""
        if weights is None:
            weights = [1.0] * len(gates)

        if len(gates) != len(weights):
            raise ValueError("Gates and weights must have same length")

        total_weight = 0.0
        weighted_sum = 0.0

        for gate, weight in zip(gates, weights):
            try:
                result = float(gate(*args, **kwargs))
                weighted_sum += result * weight
                total_weight += weight
            except Exception:
                # Skip failed gates
                pass

        return weighted_sum / total_weight if total_weight > 0 else 0.0

    def _execute_conditional(self, gates: List[Callable], *args, **kwargs) -> Any:
        """Execute conditional composition."""
        if len(gates) < 2:
            raise ValueError("Conditional composition requires at least 2 gates")

        condition_result = gates[0](*args, **kwargs)

        if condition_result:
            return gates[1](*args, **kwargs)
        elif len(gates) > 2:
            return gates[2](*args, **kwargs)  # Optional else clause
        else:
            return False


class PersonalityBridge:
    """Handles personality-aware adjustments for composite constructs."""

    @staticmethod
    def apply_personality_bridge(base_result: bool,
                               construct_name: str,
                               bridge_config: Dict[str, float]) -> bool:
        """Apply personality-specific bridge probability adjustments."""
        from kinda.personality import get_personality, chaos_random

        if base_result:
            return base_result  # No adjustment needed for success

        personality = get_personality()
        bridge_prob = bridge_config.get(personality.mood, 0.0)

        if bridge_prob > 0 and chaos_random() < bridge_prob:
            return True

        return base_result

    @staticmethod
    def calculate_composite_probability(basic_probs: List[float],
                                      strategy: CompositionStrategy) -> float:
        """Calculate expected probability for composite construct."""
        if strategy == CompositionStrategy.UNION:
            # P(A ∪ B) = P(A) + P(B) - P(A ∩ B)
            # Simplified as max for independent events
            return max(basic_probs)
        elif strategy == CompositionStrategy.INTERSECTION:
            # P(A ∩ B) = P(A) × P(B) for independent events
            result = 1.0
            for prob in basic_probs:
                result *= prob
            return result
        elif strategy == CompositionStrategy.WEIGHTED:
            # Weighted average
            return sum(basic_probs) / len(basic_probs)
        else:
            return sum(basic_probs) / len(basic_probs)  # Default average


# Global composition engine instance
composition_engine = None


def get_composition_engine() -> CompositionEngine:
    """Get the global composition engine instance."""
    global composition_engine
    if composition_engine is None:
        composition_engine = CompositionEngine()
    return composition_engine