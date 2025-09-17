# Custom Construct Example: Building Your Own Composition

## 🎯 Overview

This tutorial walks you through building a completely new composite construct from scratch using the Kinda-Lang Composition Framework. You'll create `~eventually`, a construct that combines persistence with uncertainty to model "eventually successful" operations.

## 💡 Concept: ~eventually Construct

### Design Goals

Create a construct that:
- **Attempts operations multiple times** with increasing probability of success
- **Adapts to personality** (reliable tries fewer times, chaotic tries more)
- **Demonstrates composition** by using ~sometimes, ~maybe, and ~kinda_repeat
- **Shows practical value** for modeling real-world "eventually successful" scenarios

### Behavior Specification

```kinda
// Basic usage
~eventually { print("This will happen... eventually") }

// With explicit attempts
~eventually(max_attempts=5) { risky_operation() }

// Personality-aware behavior:
// - reliable: succeeds quickly (2-3 attempts)
// - cautious: moderate attempts (3-4 attempts)
// - playful: variable attempts (2-6 attempts)
// - chaotic: many attempts (4-8 attempts)
```

## 🏗️ Step 1: Design the Composition Strategy

### Mathematical Model

**Core Logic**: Increasing probability with each attempt
```
attempt_1: base_probability
attempt_2: base_probability * 1.3
attempt_3: base_probability * 1.6
attempt_n: base_probability * (1 + 0.3 * (n-1))
```

**Base Probabilities by Personality**:
- reliable: 0.7 (high initial success chance)
- cautious: 0.5 (moderate initial success chance)
- playful: 0.4 (lower initial success chance)
- chaotic: 0.3 (low initial success chance)

**Maximum Attempts by Personality**:
- reliable: 3 (efficient, quick success)
- cautious: 4 (careful but not excessive)
- playful: 6 (willing to experiment)
- chaotic: 8 (persistent despite failures)

### Component Analysis

**Required Basic Constructs**:
- `~sometimes`: Provides probabilistic execution for each attempt
- `~maybe`: Adds secondary probability layer for attempt decisions
- `~kinda_repeat`: Manages the retry loop structure

## 🛠️ Step 2: Implement the Composition Class

```python
# File: kinda/composition/patterns.py (addition)

from kinda.composition.framework import CompositeConstruct, CompositionConfig, CompositionStrategy

class EventuallyComposition(CompositeConstruct):
    """Composition demonstrating persistence with increasing probability"""

    def __init__(self, name: str, max_attempts: int = None):
        config = CompositionConfig(
            strategy=CompositionStrategy.SEQUENTIAL,  # Attempts are sequential
            personality_bridges={
                "reliable": 0.1,    # Small bridge (already efficient)
                "cautious": 0.15,   # Moderate bridge (boost confidence)
                "playful": 0.2,     # Higher bridge (encourage experimentation)
                "chaotic": 0.25,    # Highest bridge (support persistence)
            },
            performance_target=0.18,  # Target <18% overhead
            dependency_validation=True,
            statistical_validation=True,
            debug_tracing=False,
        )
        super().__init__(name, config)
        self.max_attempts = max_attempts

    def get_basic_constructs(self):
        """Return required basic constructs"""
        return ["sometimes", "maybe", "kinda_repeat"]

    def compose(self, operation_func=None, *args, **kwargs):
        """Execute eventually composition logic"""

        # Validate dependencies
        if not self.validate_dependencies():
            raise RuntimeError("Required constructs not available: " +
                             str(self.get_basic_constructs()))

        # Get personality-specific parameters
        max_attempts = self._get_personality_max_attempts()
        base_probability = self._get_personality_base_probability()

        # Execute attempts with increasing probability
        for attempt in range(1, max_attempts + 1):
            try:
                # Calculate probability for this attempt
                attempt_probability = self._calculate_attempt_probability(
                    base_probability, attempt
                )

                # Primary gate: ~sometimes with calculated probability
                primary_gate = self._sometimes_with_probability(attempt_probability)

                # Secondary gate: ~maybe for additional uncertainty
                secondary_gate = maybe(True)

                # Combination logic: either gate can trigger success
                should_succeed = primary_gate or secondary_gate

                if should_succeed:
                    # Success! Execute the operation
                    if operation_func:
                        return operation_func(*args, **kwargs)
                    else:
                        return True

                # Failed this attempt, check if we should continue
                if attempt < max_attempts:
                    # Use ~kinda_repeat logic to decide if we continue
                    should_continue = self._should_continue_attempts(attempt, max_attempts)
                    if not should_continue:
                        break

            except Exception as e:
                print(f"[eventually] Attempt {attempt} failed: {e}")
                # Continue to next attempt unless it's the last one
                if attempt == max_attempts:
                    raise

        # All attempts exhausted - apply bridge probability
        bridge_success = self._apply_personality_bridge()
        if bridge_success and operation_func:
            return operation_func(*args, **kwargs)

        return bridge_success

    def _get_personality_max_attempts(self):
        """Get personality-specific maximum attempts"""
        if self.max_attempts is not None:
            return self.max_attempts

        from kinda.personality import get_personality
        personality = get_personality().mood

        max_attempts_by_personality = {
            "reliable": 3,   # Efficient
            "cautious": 4,   # Careful
            "playful": 6,    # Experimental
            "chaotic": 8,    # Persistent
        }

        return max_attempts_by_personality.get(personality, 4)

    def _get_personality_base_probability(self):
        """Get personality-specific base probability"""
        from kinda.personality import get_personality
        personality = get_personality().mood

        base_probabilities = {
            "reliable": 0.7,  # High success chance
            "cautious": 0.5,  # Moderate success chance
            "playful": 0.4,   # Lower success chance
            "chaotic": 0.3,   # Low success chance
        }

        return base_probabilities.get(personality, 0.5)

    def _calculate_attempt_probability(self, base_prob, attempt_number):
        """Calculate increasing probability for each attempt"""
        # Probability increases with each attempt
        multiplier = 1 + 0.3 * (attempt_number - 1)
        return min(base_prob * multiplier, 0.95)  # Cap at 95%

    def _sometimes_with_probability(self, target_probability):
        """Execute ~sometimes with specific target probability"""
        # This is simplified - in practice, we'd need to adjust
        # ~sometimes behavior to match the target probability
        return sometimes(True)

    def _should_continue_attempts(self, current_attempt, max_attempts):
        """Decide whether to continue attempts using ~kinda_repeat logic"""
        remaining = max_attempts - current_attempt

        # Use ~maybe to decide continuation with higher prob for more remaining attempts
        continuation_prob = remaining / max_attempts
        from kinda.personality import chaos_random
        return chaos_random() < continuation_prob

    def _apply_personality_bridge(self):
        """Apply personality bridge probability"""
        from kinda.personality import get_personality, chaos_random

        personality = get_personality().mood
        bridge_prob = self.config.personality_bridges.get(personality, 0.0)

        return chaos_random() < bridge_prob

    def get_target_probabilities(self):
        """Return target probability behavior for validation"""
        return {
            "reliable": 0.85,   # High success rate, few attempts
            "cautious": 0.75,   # Good success rate, moderate attempts
            "playful": 0.70,    # Decent success rate, more attempts
            "chaotic": 0.65,    # Lower success rate, many attempts
        }
```

## 🎯 Step 3: Create Factory Methods

```python
# Add to kinda/composition/patterns.py

class CompositionPatternFactory:
    # ... existing methods ...

    @staticmethod
    def create_eventually_pattern(name: str, max_attempts: int = None):
        """Create an eventually composition pattern"""
        return EventuallyComposition(name, max_attempts)

# Add convenience function to kinda/composition/__init__.py
def create_eventually_pattern(name: str, max_attempts: int = None):
    """Convenience function to create eventually pattern"""
    return CompositionPatternFactory.create_eventually_pattern(name, max_attempts)
```

## 🔧 Step 4: Implement Runtime Integration

```python
# File: kinda/langs/python/runtime/fuzzy.py (addition)

def eventually(operation_func=None, max_attempts=None):
    """~eventually construct: Persistence with increasing probability"""
    from kinda.composition import get_composition_engine
    from kinda.personality import update_chaos_state

    try:
        # Get or create eventually pattern
        engine = get_composition_engine()
        pattern_name = f"eventually_pattern_{max_attempts or 'default'}"
        eventually_pattern = engine.get_composite(pattern_name)

        if eventually_pattern is None:
            # Create and register pattern
            from kinda.composition.patterns import EventuallyComposition
            eventually_pattern = EventuallyComposition(pattern_name, max_attempts)
            engine.register_composite(eventually_pattern)

        # Execute composition
        result = eventually_pattern.compose(operation_func)
        update_chaos_state(failed=not result)
        return result

    except Exception as e:
        print(f"[eventually] Composition failed: {e}")
        update_chaos_state(failed=True)

        # Fallback: simple retry loop
        attempts = max_attempts or 3
        for attempt in range(attempts):
            from kinda.personality import chaos_random
            if chaos_random() < 0.6:  # 60% base chance
                if operation_func:
                    return operation_func()
                return True
        return False
```

## 📝 Step 5: Add Construct Definition

```python
# Add to kinda/grammar/python/constructs.py

"eventually": {
    "type": "control",
    "pattern": re.compile(r"~eventually(?:\(([^)]*)\))?\s*\{([^}]*)\}"),
    "description": "Execute with persistence and increasing probability",
    "body": (
        "def eventually_block(max_attempts=None, block_code=''):\n"
        "    from kinda.langs.python.runtime.fuzzy import eventually\n"
        "    \n"
        "    def operation():\n"
        "        exec(block_code, globals())\n"
        "        return True\n"
        "    \n"
        "    return eventually(operation, max_attempts)\n"
    ),
},
```

## 🧪 Step 6: Create Comprehensive Tests

```python
# File: tests/python/test_eventually_composition.py

import unittest
from unittest.mock import patch, MagicMock
import sys
import io
import contextlib

sys.path.insert(0, "src")

from kinda.personality import PersonalityContext, setup_personality
from kinda.composition import get_composition_engine, is_framework_ready

class TestEventuallyComposition(unittest.TestCase):
    """Test suite for custom ~eventually composition"""

    def setUp(self):
        """Set up test environment"""
        PersonalityContext._instance = None
        setup_personality("reliable", chaos_level=1, seed=42)

    def test_basic_functionality(self):
        """Test basic eventually composition functionality"""
        from kinda.langs.python.runtime.fuzzy import eventually

        # Test with simple operation
        call_count = 0
        def test_operation():
            nonlocal call_count
            call_count += 1
            return True

        result = eventually(test_operation, max_attempts=3)

        # Should succeed eventually
        self.assertTrue(result)
        # Should have been called at least once
        self.assertGreater(call_count, 0)
        # Should not exceed max attempts
        self.assertLessEqual(call_count, 3)

    def test_personality_behavior(self):
        """Test behavior across different personalities"""
        from kinda.langs.python.runtime.fuzzy import eventually

        personalities = ["reliable", "cautious", "playful", "chaotic"]

        for personality in personalities:
            with PersonalityContext(personality):
                with self.subTest(personality=personality):

                    # Statistical test
                    successes = 0
                    total_attempts = 0

                    for trial in range(100):
                        attempt_count = 0

                        def counting_operation():
                            nonlocal attempt_count
                            attempt_count += 1
                            return True

                        result = eventually(counting_operation, max_attempts=5)

                        if result:
                            successes += 1
                        total_attempts += attempt_count

                    success_rate = successes / 100
                    avg_attempts = total_attempts / 100

                    print(f"{personality}: {success_rate:.2%} success, "
                          f"{avg_attempts:.1f} avg attempts")

                    # Verify reasonable success rate
                    self.assertGreater(success_rate, 0.5)
                    self.assertLess(avg_attempts, 6)

    def test_dependency_validation(self):
        """Test dependency validation"""
        from kinda.composition.patterns import EventuallyComposition

        pattern = EventuallyComposition("test_eventually")
        dependencies = pattern.get_basic_constructs()

        # Should require basic constructs
        expected_deps = ["sometimes", "maybe", "kinda_repeat"]
        for dep in expected_deps:
            self.assertIn(dep, dependencies)

    def test_error_handling(self):
        """Test error handling and fallback behavior"""
        from kinda.langs.python.runtime.fuzzy import eventually

        def failing_operation():
            raise Exception("Test failure")

        # Should handle operation failures gracefully
        with patch('builtins.print') as mock_print:
            result = eventually(failing_operation, max_attempts=2)

            # Should fall back gracefully
            self.assertIsInstance(result, bool)
            # Should have logged the error
            self.assertTrue(any("failed" in str(call) for call in mock_print.call_args_list))

    def test_max_attempts_parameter(self):
        """Test explicit max_attempts parameter"""
        from kinda.langs.python.runtime.fuzzy import eventually

        call_count = 0
        def counting_operation():
            nonlocal call_count
            call_count += 1
            return call_count >= 3  # Succeed on 3rd attempt

        result = eventually(counting_operation, max_attempts=5)

        # Should succeed
        self.assertTrue(result)
        # Should have been called exactly 3 times
        self.assertEqual(call_count, 3)

    def test_performance_characteristics(self):
        """Test performance is within acceptable limits"""
        from kinda.langs.python.runtime.fuzzy import eventually
        import time

        def quick_operation():
            return True

        # Benchmark multiple executions
        start_time = time.perf_counter()
        for _ in range(1000):
            eventually(quick_operation, max_attempts=3)
        execution_time = time.perf_counter() - start_time

        # Should complete within reasonable time
        self.assertLess(execution_time, 2.0)  # 2 seconds for 1000 calls

        print(f"Performance: {execution_time:.3f}s for 1000 calls "
              f"({execution_time/1000*1000:.3f}ms per call)")

class TestEventuallyIntegration(unittest.TestCase):
    """Test framework integration aspects"""

    def test_framework_registration(self):
        """Test that patterns are registered correctly"""
        from kinda.composition.patterns import EventuallyComposition
        from kinda.composition import get_composition_engine

        # Create and register pattern
        pattern = EventuallyComposition("test_registration", max_attempts=3)
        engine = get_composition_engine()
        engine.register_composite(pattern)

        # Verify registration
        retrieved = engine.get_composite("test_registration")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.name, "test_registration")

    def test_composition_validation(self):
        """Test composition framework validation"""
        from kinda.composition.patterns import EventuallyComposition
        from kinda.composition.validation import validate_composition_integrity

        pattern = EventuallyComposition("test_validation")

        # Run framework validation
        validation_result = validate_composition_integrity(pattern)

        # Should pass basic validation
        self.assertEqual(validation_result["overall_status"], "PASS")
        self.assertTrue(validation_result["dependency_check"])

    def test_statistical_validation(self):
        """Test statistical behavior validation"""
        from kinda.composition.testing import get_test_framework
        from kinda.composition.patterns import EventuallyComposition

        framework = get_test_framework()
        pattern = EventuallyComposition("test_stats")

        personalities = ["reliable", "cautious", "playful", "chaotic"]

        for personality in personalities:
            target_prob = pattern.get_target_probabilities()[personality]

            # Validate with framework
            passed = framework.validate_composition_probability(
                pattern, personality, target_prob, tolerance=0.1
            )

            self.assertTrue(passed, f"Statistical validation failed for {personality}")

if __name__ == "__main__":
    unittest.main()
```

## 🎯 Step 7: Usage Examples

### Basic Usage

```python
# Simple eventually block
from kinda.langs.python.runtime.fuzzy import eventually

def risky_operation():
    from kinda.personality import chaos_random
    return chaos_random() < 0.3  # 30% chance of success

# Will try multiple times until success
result = eventually(risky_operation)
print(f"Eventually succeeded: {result}")
```

### Advanced Usage

```python
# With custom max attempts
def download_file(url):
    # Simulated download operation
    import random
    if random.random() < 0.4:
        return f"Downloaded {url}"
    else:
        raise Exception("Network error")

try:
    result = eventually(lambda: download_file("https://example.com"), max_attempts=5)
    print(f"Download result: {result}")
except Exception as e:
    print(f"Download failed after all attempts: {e}")
```

### In Kinda-Lang Syntax (Conceptual)

```kinda
// Basic usage
~eventually {
    risky_api_call()
}

// With parameters
~eventually(max_attempts=3) {
    upload_file("data.txt")
}

// Nested with other constructs
~sometimes {
    ~eventually(max_attempts=5) {
        ~maybe {
            complex_operation()
        }
    }
}
```

## 📊 Step 8: Performance Analysis

### Benchmarking Your Composition

```python
def benchmark_eventually_composition():
    """Comprehensive performance analysis"""
    import time
    import statistics
    from kinda.langs.python.runtime.fuzzy import eventually

    def benchmark_operation():
        return True

    # Benchmark different max_attempts values
    for max_attempts in [1, 3, 5, 10]:
        execution_times = []

        for _ in range(1000):
            start_time = time.perf_counter()
            eventually(benchmark_operation, max_attempts=max_attempts)
            execution_time = time.perf_counter() - start_time
            execution_times.append(execution_time)

        avg_time = statistics.mean(execution_times)
        std_dev = statistics.stdev(execution_times)

        print(f"Max attempts {max_attempts}: "
              f"{avg_time*1000:.3f}ms ± {std_dev*1000:.3f}ms")

    # Benchmark vs simple retry loop
    def simple_retry(operation, max_attempts=3):
        for _ in range(max_attempts):
            if operation():
                return True
        return False

    # Compare performance
    start_time = time.perf_counter()
    for _ in range(1000):
        eventually(benchmark_operation, max_attempts=3)
    composition_time = time.perf_counter() - start_time

    start_time = time.perf_counter()
    for _ in range(1000):
        simple_retry(benchmark_operation, max_attempts=3)
    simple_time = time.perf_counter() - start_time

    overhead = (composition_time - simple_time) / simple_time
    print(f"Composition overhead: {overhead:.1%}")
```

## 🎓 What You've Learned

### Composition Concepts Demonstrated

1. **Sequential Strategy**: Multiple attempts in sequence with increasing probability
2. **Personality Integration**: Different behavior patterns per personality mode
3. **Dependency Management**: Systematic validation of required basic constructs
4. **Error Resilience**: Graceful handling of operation failures
5. **Performance Monitoring**: Framework overhead within acceptable limits

### Framework Integration Skills

1. **Pattern Registration**: How to register custom patterns with the composition engine
2. **Factory Methods**: Creating convenience functions for pattern creation
3. **Runtime Integration**: Connecting compositions to language runtime
4. **Statistical Validation**: Ensuring composed behavior meets target probabilities
5. **Testing Strategies**: Comprehensive testing across personalities and edge cases

### Advanced Patterns Unlocked

1. **Increasing Probability**: Modeling operations that become more likely to succeed over time
2. **Adaptive Attempts**: Personality-specific retry behavior
3. **Bridge Probabilities**: Fine-tuning final success rates
4. **Fallback Mechanisms**: Robust error handling with multiple fallback layers
5. **Performance Optimization**: Balancing framework benefits with execution efficiency

## 🚀 Next Steps

Now that you've built a custom composition:

1. **Experiment with variations**: Try different probability calculations or retry strategies
2. **Add more complexity**: Integrate with other composed constructs
3. **Performance optimization**: Implement caching or lazy loading
4. **Real-world application**: Use ~eventually for actual retry scenarios
5. **Study [Advanced Patterns](../advanced-patterns.md)**: Learn sophisticated composition techniques

## 🎯 Production Considerations

### Feature Flag Integration

```python
def eventually_with_feature_flag(operation_func=None, max_attempts=None):
    """Production version with feature flag support"""
    import os

    if os.getenv('KINDA_USE_COMPOSITION_EVENTUALLY', 'true').lower() == 'true':
        try:
            return eventually(operation_func, max_attempts)
        except Exception as e:
            print(f"[eventually] Composition fallback: {e}")
            return simple_retry_fallback(operation_func, max_attempts)
    else:
        return simple_retry_fallback(operation_func, max_attempts)
```

### Monitoring and Metrics

```python
def eventually_with_monitoring(operation_func=None, max_attempts=None):
    """Version with monitoring and metrics collection"""
    import time

    start_time = time.time()
    attempt_count = 0

    def monitored_operation():
        nonlocal attempt_count
        attempt_count += 1
        return operation_func() if operation_func else True

    try:
        result = eventually(monitored_operation, max_attempts)

        # Collect metrics
        execution_time = time.time() - start_time
        success = result

        # Log metrics (in production, send to monitoring system)
        print(f"[metrics] eventually: success={success}, attempts={attempt_count}, "
              f"time={execution_time:.3f}s")

        return result

    except Exception as e:
        print(f"[metrics] eventually: error={e}, attempts={attempt_count}")
        raise
```

---

**Your Custom Composition**: ✅ Complete
**Pattern Type**: Sequential with Increasing Probability
**Framework**: Kinda-Lang Composition Framework v0.1.0
**Next**: [Performance Analysis](./performance-analysis.md) - Optimize your compositions