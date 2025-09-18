# Epic #127: Enhanced Probability Control - Technical Specification

**Strategic Goal**: Fine-grained probabilistic behavior control for native Python integration
**Philosophy**: "Predictable unpredictability" - Users control chaos while preserving kinda spirit
**Integration**: Seamless bridge between Python's determinism and kinda's probabilistic nature

## 🎯 Enhanced Probability Control Overview

### Core Concepts

1. **Context-Aware Probability**: Different probability profiles for different execution contexts
2. **Dynamic Probability Adjustment**: Real-time probability tuning based on runtime conditions
3. **Construct-Specific Control**: Individual probability control for each kinda construct
4. **Python-Native API**: Pythonic interfaces for probability management
5. **Reproducible Chaos**: Seed-based deterministic randomness for testing and debugging

### Probability Control Architecture

```
Python Application Context
    ↓
Probability Controller (kinda.control)
    ↓
┌─────────────────┬─────────────────┬─────────────────┐
│   Context       │   Construct     │   Dynamic       │
│   Manager       │   Controller    │   Adjuster      │
└─────────────────┴─────────────────┴─────────────────┘
    ↓                    ↓                    ↓
Personality Bridge  →  Runtime Bridge  ←  Feedback Loop
    ↓                    ↓                    ↓
Kinda Runtime System (existing)
```

## 🔧 Python-Native Probability API

### Context Management System
```python
# kinda/control/context.py

import kinda
from contextlib import contextmanager
from typing import Dict, Optional, Any, Callable

class ProbabilityContext:
    """Context manager for controlling kinda construct probabilities."""

    def __init__(self,
                 chaos_level: int = 5,
                 personality: str = 'playful',
                 seed: Optional[int] = None,
                 construct_overrides: Optional[Dict[str, float]] = None,
                 dynamic_adjustment: bool = False):
        self.chaos_level = chaos_level
        self.personality = personality
        self.seed = seed
        self.construct_overrides = construct_overrides or {}
        self.dynamic_adjustment = dynamic_adjustment
        self._previous_context = None

    def __enter__(self):
        # Store previous context for nesting support
        self._previous_context = kinda.get_current_context()
        kinda.set_context(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Restore previous context
        kinda.set_context(self._previous_context)

# Usage examples
@contextmanager
def testing_context():
    """Predictable context for unit testing."""
    with kinda.ProbabilityContext(chaos_level=1, personality='reliable', seed=12345):
        yield

@contextmanager
def production_context():
    """Balanced chaos for production environments."""
    with kinda.ProbabilityContext(chaos_level=5, personality='cautious'):
        yield

@contextmanager
def stress_testing_context():
    """High chaos for stress testing."""
    with kinda.ProbabilityContext(chaos_level=10, personality='chaotic'):
        yield
```

### Construct-Specific Control
```python
# kinda/control/constructs.py

class ConstructController:
    """Fine-grained control over individual kinda constructs."""

    def __init__(self):
        self._construct_configs = {}
        self._global_modifiers = {}

    def configure(self, construct: str, **options):
        """Configure specific construct behavior.

        Args:
            construct: Name of kinda construct ('sometimes', 'sorta_print', etc.)
            probability: Override base probability (0.0-1.0)
            personality_scaling: Whether construct respects personality (default: True)
            chaos_scaling: Whether construct respects chaos level (default: True)
            custom_behavior: Custom behavior function
        """
        self._construct_configs[construct] = ConstructConfig(**options)

    def get_probability(self, construct: str, base_probability: float) -> float:
        """Get actual probability for construct considering all modifiers."""
        config = self._construct_configs.get(construct)
        if not config:
            return self._apply_global_modifiers(base_probability)

        # Apply construct-specific overrides
        probability = config.probability if config.probability is not None else base_probability

        # Apply personality scaling if enabled
        if config.personality_scaling:
            personality = kinda.get_current_personality()
            probability *= personality.get_scaling_factor(construct)

        # Apply chaos level scaling if enabled
        if config.chaos_scaling:
            chaos_level = kinda.get_current_chaos_level()
            probability *= chaos_level / 5.0  # Normalize around default level 5

        return max(0.0, min(1.0, probability))

# Usage examples
construct_controller = kinda.ConstructController()

# Make ~sometimes more conservative in this context
construct_controller.configure('sometimes', probability=0.3)

# Disable personality scaling for critical constructs
construct_controller.configure('assert_eventually', personality_scaling=False)

# Add custom behavior for specific construct
def custom_sorta_behavior(*args, **kwargs):
    # Custom logic for sorta_print
    if len(args[0]) > 100:  # Long messages always print
        return True
    return kinda.default_sorta_behavior(*args, **kwargs)

construct_controller.configure('sorta_print', custom_behavior=custom_sorta_behavior)
```

### Dynamic Probability Adjustment
```python
# kinda/control/dynamic.py

class DynamicProbabilityAdjuster:
    """Dynamically adjusts probabilities based on runtime conditions."""

    def __init__(self):
        self._adjustment_rules = []
        self._feedback_system = FeedbackSystem()

    def add_rule(self, rule: AdjustmentRule):
        """Add dynamic adjustment rule."""
        self._adjustment_rules.append(rule)

    def adjust_probability(self, construct: str, base_probability: float,
                         context: Dict[str, Any]) -> float:
        """Apply dynamic adjustments to probability."""
        adjusted_probability = base_probability

        for rule in self._adjustment_rules:
            if rule.applies_to(construct, context):
                adjustment = rule.calculate_adjustment(context)
                adjusted_probability *= adjustment

        # Apply feedback-based learning
        feedback_adjustment = self._feedback_system.get_adjustment(construct, context)
        adjusted_probability *= feedback_adjustment

        return max(0.0, min(1.0, adjusted_probability))

# Example adjustment rules
class TimeBasedAdjustment(AdjustmentRule):
    """Adjust probability based on time of day."""

    def applies_to(self, construct: str, context: Dict[str, Any]) -> bool:
        return 'timestamp' in context

    def calculate_adjustment(self, context: Dict[str, Any]) -> float:
        import datetime
        hour = datetime.datetime.fromtimestamp(context['timestamp']).hour

        # Lower probability during business hours for ~sometimes
        if 9 <= hour <= 17:
            return 0.8
        return 1.0

class PerformanceBasedAdjustment(AdjustmentRule):
    """Adjust probability based on system performance."""

    def calculate_adjustment(self, context: Dict[str, Any]) -> float:
        cpu_usage = context.get('cpu_usage', 0.5)

        # Reduce chaos when system is under load
        if cpu_usage > 0.8:
            return 0.6
        elif cpu_usage > 0.6:
            return 0.8
        return 1.0
```

### Probability Profiles System
```python
# kinda/control/profiles.py

class ProbabilityProfile:
    """Predefined probability configurations for common scenarios."""

    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config

    def apply(self) -> ProbabilityContext:
        """Create context with this profile's configuration."""
        return ProbabilityContext(**self.config)

# Built-in profiles
PROBABILITY_PROFILES = {
    'testing': ProbabilityProfile('testing', {
        'chaos_level': 1,
        'personality': 'reliable',
        'seed': 42,
        'construct_overrides': {
            'sometimes': 0.1,  # Rarely execute for predictable tests
            'sorta_print': 1.0  # Always print for test visibility
        }
    }),

    'development': ProbabilityProfile('development', {
        'chaos_level': 3,
        'personality': 'playful',
        'construct_overrides': {
            'sorta_print': 0.9,  # More verbose for debugging
        }
    }),

    'production': ProbabilityProfile('production', {
        'chaos_level': 5,
        'personality': 'cautious',
        'dynamic_adjustment': True,
        'construct_overrides': {
            'sorta_print': 0.3,  # Less noise in production logs
        }
    }),

    'chaos_testing': ProbabilityProfile('chaos_testing', {
        'chaos_level': 10,
        'personality': 'chaotic',
        'dynamic_adjustment': True
    }),

    'demo': ProbabilityProfile('demo', {
        'chaos_level': 7,
        'personality': 'playful',
        'construct_overrides': {
            'sometimes': 0.8,    # Make demos more exciting
            'sorta_print': 0.95  # Show most outputs for demo
        }
    })
}

# Usage
with kinda.profiles['testing']:
    run_unit_tests()

with kinda.profiles['production']:
    handle_api_request()
```

## 🎛️ Advanced Probability Control Features

### Conditional Probability Control
```python
# kinda/control/conditional.py

class ConditionalProbabilityController:
    """Control probabilities based on runtime conditions."""

    def __init__(self):
        self._conditions = []

    def add_condition(self, condition: Callable[[Dict], bool],
                     probability_adjustments: Dict[str, float]):
        """Add conditional probability adjustment.

        Args:
            condition: Function that returns True when condition is met
            probability_adjustments: Dict of construct -> probability multiplier
        """
        self._conditions.append((condition, probability_adjustments))

    def get_conditional_probability(self, construct: str, base_probability: float,
                                  context: Dict[str, Any]) -> float:
        """Get probability adjusted for current conditions."""
        probability = base_probability

        for condition, adjustments in self._conditions:
            if condition(context):
                adjustment = adjustments.get(construct, 1.0)
                probability *= adjustment

        return max(0.0, min(1.0, probability))

# Example usage
controller = ConditionalProbabilityController()

# Reduce chaos during database transactions
controller.add_condition(
    condition=lambda ctx: ctx.get('in_transaction', False),
    probability_adjustments={
        'sometimes': 0.2,
        'maybe': 0.4,
        'kinda_int': 0.1  # Be more precise with fuzzy integers
    }
)

# Increase verbosity when debugging
controller.add_condition(
    condition=lambda ctx: ctx.get('debug_mode', False),
    probability_adjustments={
        'sorta_print': 1.5  # Increase print probability when debugging
    }
)
```

### Probability Learning System
```python
# kinda/control/learning.py

class ProbabilityLearningSystem:
    """Learn optimal probabilities based on user feedback and outcomes."""

    def __init__(self):
        self._outcome_history = []
        self._user_feedback = {}
        self._learned_adjustments = {}

    def record_outcome(self, construct: str, probability_used: float,
                      outcome: str, context: Dict[str, Any]):
        """Record outcome of probabilistic construct execution."""
        self._outcome_history.append(OutcomeRecord(
            construct=construct,
            probability=probability_used,
            outcome=outcome,
            context=context,
            timestamp=time.time()
        ))

        # Trigger learning update
        self._update_learned_adjustments(construct)

    def record_user_feedback(self, construct: str, feedback: UserFeedback):
        """Record user feedback about construct behavior."""
        if construct not in self._user_feedback:
            self._user_feedback[construct] = []
        self._user_feedback[construct].append(feedback)

    def get_learned_probability(self, construct: str, base_probability: float,
                               context: Dict[str, Any]) -> float:
        """Get probability adjusted based on learned behavior."""
        adjustment = self._learned_adjustments.get(construct, 1.0)
        return max(0.0, min(1.0, base_probability * adjustment))

    def _update_learned_adjustments(self, construct: str):
        """Update learned adjustments based on historical outcomes."""
        recent_outcomes = [
            record for record in self._outcome_history[-100:]  # Last 100 outcomes
            if record.construct == construct
        ]

        if len(recent_outcomes) < 10:  # Not enough data
            return

        # Simple learning algorithm - adjust based on success rate
        success_rate = sum(1 for r in recent_outcomes if r.outcome == 'success') / len(recent_outcomes)

        if success_rate < 0.3:  # Too many failures
            self._learned_adjustments[construct] = 0.8  # Reduce probability
        elif success_rate > 0.8:  # Very successful
            self._learned_adjustments[construct] = 1.2  # Increase probability
        else:
            self._learned_adjustments[construct] = 1.0  # Keep current
```

## 🔄 Integration with Existing Personality System

### Personality Bridge
```python
# kinda/control/personality_bridge.py

class PersonalityBridge:
    """Bridge between new probability control system and existing personality system."""

    def __init__(self):
        self.personality_system = kinda.personality.PersonalityContext()

    def integrate_with_context(self, prob_context: ProbabilityContext):
        """Integrate probability context with existing personality system."""
        # Update personality system with new context
        self.personality_system.set_chaos_level(prob_context.chaos_level)
        self.personality_system.set_mood(prob_context.personality)

        if prob_context.seed is not None:
            self.personality_system.set_seed(prob_context.seed)

    def get_personality_scaling(self, construct: str, personality: str) -> float:
        """Get personality-based scaling factor for construct."""
        # Use existing personality profiles from kinda.personality
        personality_profile = PERSONALITY_PROFILES.get(personality, PERSONALITY_PROFILES['playful'])
        return personality_profile.get_construct_scaling(construct)

    def bridge_construct_call(self, construct: str, *args, **kwargs):
        """Bridge construct call through probability control system."""
        context = kinda.get_current_context()

        # Calculate final probability
        base_prob = self.personality_system.get_base_probability(construct)
        controlled_prob = context.get_controlled_probability(construct, base_prob)

        # Execute construct with controlled probability
        return self.personality_system.execute_construct(construct, controlled_prob, *args, **kwargs)
```

### Backward Compatibility
```python
# kinda/control/compatibility.py

class BackwardCompatibilityLayer:
    """Ensures new probability control doesn't break existing kinda code."""

    def __init__(self):
        self.legacy_mode = os.getenv('KINDA_LEGACY_MODE', 'false').lower() == 'true'

    def wrap_legacy_construct(self, construct_func):
        """Wrap legacy construct function with new probability control."""
        def wrapped(*args, **kwargs):
            if self.legacy_mode:
                # Use original behavior
                return construct_func(*args, **kwargs)
            else:
                # Use new probability control system
                context = kinda.get_current_context()
                if context:
                    return context.execute_construct(construct_func.__name__, construct_func, *args, **kwargs)
                else:
                    return construct_func(*args, **kwargs)

        return wrapped

    def migrate_legacy_code(self, source_code: str) -> str:
        """Migrate legacy kinda code to use new probability control."""
        # Pattern matching and replacement for common usage patterns
        patterns = [
            (r'kinda\.set_chaos_level\((\d+)\)', r'kinda.ProbabilityContext(chaos_level=\1)'),
            (r'kinda\.set_personality\(["\'](\w+)["\']\)', r'kinda.ProbabilityContext(personality="\1")'),
        ]

        migrated_code = source_code
        for pattern, replacement in patterns:
            migrated_code = re.sub(pattern, replacement, migrated_code)

        return migrated_code
```

## 📊 Monitoring and Observability

### Probability Monitoring System
```python
# kinda/control/monitoring.py

class ProbabilityMonitor:
    """Monitor and analyze probability behavior in applications."""

    def __init__(self):
        self.execution_log = []
        self.probability_stats = {}
        self.performance_metrics = {}

    def log_execution(self, construct: str, probability_used: float,
                     executed: bool, execution_time: float):
        """Log construct execution for analysis."""
        log_entry = ExecutionLogEntry(
            construct=construct,
            probability=probability_used,
            executed=executed,
            execution_time=execution_time,
            timestamp=time.time()
        )
        self.execution_log.append(log_entry)

        # Update statistics
        self._update_stats(log_entry)

    def get_probability_report(self, construct: str = None) -> ProbabilityReport:
        """Generate probability behavior report."""
        if construct:
            entries = [e for e in self.execution_log if e.construct == construct]
        else:
            entries = self.execution_log

        return ProbabilityReport(
            total_executions=len(entries),
            execution_rate=self._calculate_execution_rate(entries),
            average_probability=self._calculate_average_probability(entries),
            probability_distribution=self._calculate_distribution(entries),
            performance_impact=self._calculate_performance_impact(entries)
        )

    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get data for probability control dashboard."""
        return {
            'construct_usage': self._get_construct_usage_stats(),
            'probability_trends': self._get_probability_trends(),
            'performance_metrics': self._get_performance_metrics(),
            'context_statistics': self._get_context_stats()
        }

# Dashboard integration
@app.route('/kinda/dashboard')
def probability_dashboard():
    monitor = kinda.get_global_monitor()
    data = monitor.get_dashboard_data()
    return render_template('probability_dashboard.html', data=data)
```

### Debug and Visualization Tools
```python
# kinda/control/debugging.py

class ProbabilityDebugger:
    """Debug probability control behavior."""

    def __init__(self):
        self.trace_mode = False
        self.breakpoints = set()

    def enable_trace(self):
        """Enable probability execution tracing."""
        self.trace_mode = True

    def add_breakpoint(self, construct: str):
        """Add breakpoint for specific construct."""
        self.breakpoints.add(construct)

    def trace_construct_execution(self, construct: str, probability: float, context: Dict):
        """Trace construct execution with detailed information."""
        if self.trace_mode or construct in self.breakpoints:
            print(f"""
╭─ Kinda Probability Trace ─╮
│ Construct: {construct:<15} │
│ Probability: {probability:.3f}       │
│ Context: {str(context)[:20]:<20} │
│ Will Execute: {probability > random()}  │
╰────────────────────────────╯
            """)

            if construct in self.breakpoints:
                import pdb; pdb.set_trace()

# Visualization utilities
def visualize_probability_distribution(construct: str, samples: int = 1000):
    """Visualize probability distribution for a construct."""
    import matplotlib.pyplot as plt

    probabilities = []
    for _ in range(samples):
        prob = kinda.calculate_construct_probability(construct)
        probabilities.append(prob)

    plt.hist(probabilities, bins=50, alpha=0.7)
    plt.title(f'Probability Distribution for {construct}')
    plt.xlabel('Probability')
    plt.ylabel('Frequency')
    plt.show()
```

## 🧪 Testing Enhanced Probability Control

### Test Framework Integration
```python
# kinda/control/testing.py

class ProbabilityTestFramework:
    """Testing framework for probability-controlled code."""

    def __init__(self):
        self.test_contexts = {}

    def create_test_context(self, name: str, **config) -> ProbabilityContext:
        """Create named test context with specific configuration."""
        context = ProbabilityContext(**config)
        self.test_contexts[name] = context
        return context

    def assert_probability_behavior(self, construct: str, expected_prob: float,
                                  tolerance: float = 0.1, samples: int = 1000):
        """Assert that construct behaves with expected probability."""
        successes = 0
        for _ in range(samples):
            if kinda.execute_construct_test(construct):
                successes += 1

        actual_prob = successes / samples
        assert abs(actual_prob - expected_prob) <= tolerance, \
            f"Expected {expected_prob}, got {actual_prob} for {construct}"

    def assert_context_isolation(self, context1: ProbabilityContext,
                                context2: ProbabilityContext):
        """Assert that contexts don't interfere with each other."""
        with context1:
            prob1 = kinda.calculate_construct_probability('sometimes')

        with context2:
            prob2 = kinda.calculate_construct_probability('sometimes')

        # Verify contexts produce different probabilities
        assert prob1 != prob2, "Contexts should produce different probabilities"

# Pytest integration
@pytest.fixture
def predictable_context():
    """Pytest fixture for predictable kinda behavior."""
    return kinda.ProbabilityContext(chaos_level=1, personality='reliable', seed=42)

@pytest.fixture
def chaotic_context():
    """Pytest fixture for chaotic kinda behavior."""
    return kinda.ProbabilityContext(chaos_level=10, personality='chaotic')

def test_probability_control(predictable_context):
    """Test that probability control works as expected."""
    with predictable_context:
        # Test should be predictable with this context
        assert kinda.sometimes(True) == expected_predictable_result
```

## 📋 Quality Gates for Probability Control

### API Quality Gates
- [ ] ✅ Context managers work correctly with nested contexts
- [ ] ✅ Construct-specific overrides function as expected
- [ ] ✅ Dynamic adjustment rules apply correctly
- [ ] ✅ Probability profiles provide expected behavior

### Integration Quality Gates
- [ ] ✅ Backward compatibility with existing kinda code maintained
- [ ] ✅ Personality system integration preserves existing behavior
- [ ] ✅ Performance impact < 10% vs existing personality system
- [ ] ✅ Thread safety for concurrent probability contexts

### User Experience Quality Gates
- [ ] ✅ Python-native API feels intuitive to Python developers
- [ ] ✅ Documentation provides clear usage examples
- [ ] ✅ Error messages are helpful and actionable
- [ ] ✅ Debug tools provide useful insights

### Testing Quality Gates
- [ ] ✅ Test framework enables reliable testing of probabilistic code
- [ ] ✅ Monitoring system provides actionable insights
- [ ] ✅ Visualization tools help understand probability behavior
- [ ] ✅ All probability control features have comprehensive tests

## 🔮 Advanced Features for Future Releases

### Machine Learning Integration (Future)
```python
# Future: ML-based probability optimization
class MLProbabilityOptimizer:
    """Use machine learning to optimize probabilities based on outcomes."""

    def __init__(self):
        self.model = None

    def train_on_historical_data(self, historical_outcomes: List[OutcomeRecord]):
        """Train ML model on historical construct outcomes."""
        pass

    def predict_optimal_probability(self, construct: str, context: Dict) -> float:
        """Predict optimal probability for current context."""
        pass
```

### Distributed Probability Control (Future)
```python
# Future: Distributed systems probability coordination
class DistributedProbabilityController:
    """Coordinate probabilities across distributed system components."""

    def __init__(self, node_id: str):
        self.node_id = node_id
        self.cluster_coordinator = None

    def sync_probabilities(self, other_nodes: List[str]):
        """Synchronize probability states across nodes."""
        pass
```

---

**Status**: Enhanced Probability Control Specification Complete
**Python Integration**: Native API ready for seamless integration
**Next Phase**: Final architectural validation and implementation handoff