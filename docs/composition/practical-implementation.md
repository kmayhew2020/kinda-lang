# Practical Implementation Guide

## 🚀 Getting Started with Construct Composition

This guide provides hands-on instruction for using the Kinda-Lang Composition Framework to build your own composite constructs. You'll learn by examining real implementations and building working examples.

## 📋 Prerequisites

Before starting, ensure you have:

- **Kinda-Lang development environment** set up
- **Composition framework** installed and functional
- **Basic understanding** of Kinda-Lang constructs (~sometimes, ~maybe, etc.)
- **Python development experience** (for framework integration)

### Quick Framework Validation

```python
# Test that the composition framework is ready
from kinda.composition import is_framework_ready, validate_framework_installation

# Check framework status
if is_framework_ready():
    print("✅ Composition framework ready!")
else:
    print("❌ Framework needs initialization")

# Run full validation
validation_results = validate_framework_installation()
print(f"Framework validation: {validation_results}")
```

## 🎯 Tutorial 1: Understanding Existing Compositions

### Step 1: Examining ~sorta Composition (Epic #126 Task 1)

The `~sorta print` construct demonstrates union composition - combining multiple probabilistic gates with OR logic.

**Original Implementation (Monolithic)**:
```python
def sorta_print(*args):
    from kinda.personality import chaos_probability
    if chaos_probability('sorta_print'):  # Single probability check
        print(f"[print] {' '.join(map(str, args))}")
    else:
        # Shrug responses
        pass
```

**Composition Implementation**:
```python
def sorta_print(*args):
    """Epic #126 Task 1: Composition-based implementation"""
    try:
        # Gate 1: ~sometimes check
        gate1 = sometimes(True)

        # Gate 2: ~maybe check
        gate2 = maybe(True)

        # Union logic: Execute if either gate succeeds
        should_execute = gate1 or gate2

        if should_execute:
            print(f"[print] {' '.join(map(str, args))}")
        else:
            # Bridge probability for personality adjustment
            if bridge_probability():
                print(f"[print] {' '.join(map(str, args))}")
            else:
                shrug_response(args)

    except Exception as e:
        # Fallback to legacy implementation
        print(f"[error] Sorta print kinda broke: {e}")
        print(f"[fallback] {' '.join(map(str, args))}")
```

**Key Insights**:
- **Transparency**: You can see exactly how ~sorta emerges from ~sometimes + ~maybe
- **Flexibility**: Modify individual components to affect overall behavior
- **Reliability**: Graceful fallback ensures backward compatibility

### Step 2: Examining ~ish Composition (Epic #126 Task 3)

The `~ish` construct demonstrates tolerance composition - using fuzzy values for approximate comparisons.

**Composition Implementation**:
```python
def ish_comparison_composed(left_val, right_val, tolerance_base=None):
    """Epic #126 Task 3: ~ish comparison using composition framework"""
    try:
        # Get composition engine
        from kinda.composition import get_composition_engine
        engine = get_composition_engine()

        # Get or create ish pattern
        ish_pattern = engine.get_composite("ish_comparison_pattern")
        if ish_pattern is None:
            # Create tolerance composition on first use
            from kinda.composition.patterns import IshToleranceComposition
            ish_pattern = IshToleranceComposition("ish_comparison_pattern", "comparison")
            engine.register_composite(ish_pattern)

        # Delegate to composition framework
        return ish_pattern.compose_comparison(left_val, right_val, tolerance_base)

    except Exception as e:
        # Robust fallback to legacy implementation
        from kinda.langs.python.runtime.fuzzy import ish_comparison
        return ish_comparison(left_val, right_val, tolerance_base)
```

**Key Insights**:
- **Lazy Loading**: Patterns created on first use for efficiency
- **Framework Integration**: Seamless integration with composition engine
- **Error Resilience**: Automatic fallback to legacy implementation

## 🛠️ Tutorial 2: Building Your First Composition

### Step 1: Design Your Composition

Let's create a custom construct called `~kinda_sure` that requires 2 out of 3 basic constructs to succeed.

**Design Requirements**:
- **Components**: ~sometimes, ~maybe, ~rarely
- **Strategy**: Threshold composition (≥2 successes required)
- **Behavior**: Higher confidence than individual constructs
- **Personality-aware**: Different thresholds per personality

### Step 2: Implement the Pattern Class

```python
# Create: kinda/composition/patterns.py addition
from kinda.composition.framework import CompositeConstruct, CompositionConfig, CompositionStrategy

class KindaSureComposition(CompositeConstruct):
    """Custom threshold composition requiring 2/3 construct agreement."""

    def __init__(self, name: str, threshold: int = 2):
        config = CompositionConfig(
            strategy=CompositionStrategy.THRESHOLD,
            personality_bridges={
                "reliable": 0.0,    # High confidence personalities need no bridge
                "cautious": 0.1,    # Slight bridge for caution
                "playful": 0.15,    # Moderate bridge for playfulness
                "chaotic": 0.2,     # Higher bridge for chaos
            },
            performance_target=0.15,  # Target <15% overhead
            dependency_validation=True,
            statistical_validation=True,
        )
        super().__init__(name, config)
        self.threshold = threshold

    def get_basic_constructs(self):
        """Return required basic constructs."""
        return ["sometimes", "maybe", "rarely"]

    def compose(self, condition=True):
        """Execute threshold composition logic."""
        # Validate dependencies first
        if not self.validate_dependencies():
            raise RuntimeError("Required basic constructs not available")

        # Execute component constructs
        results = []
        try:
            # Import basic constructs from global scope
            results.append(sometimes(condition))
            results.append(maybe(condition))
            results.append(rarely(condition))
        except Exception as e:
            raise RuntimeError(f"Component execution failed: {e}")

        # Threshold logic: Count successes
        successes = sum(1 for result in results if result)
        base_result = successes >= self.threshold

        # Apply personality bridge if needed
        if not base_result:
            from kinda.personality import get_personality, chaos_random
            personality = get_personality().mood
            bridge_prob = self.config.personality_bridges.get(personality, 0.0)

            if bridge_prob > 0 and chaos_random() < bridge_prob:
                return True

        return base_result

    def get_target_probabilities(self):
        """Return target probabilities for each personality."""
        # These would be calculated based on component probabilities
        # and threshold requirements
        return {
            "reliable": 0.85,   # High confidence
            "cautious": 0.75,   # Moderate confidence
            "playful": 0.65,    # Balanced confidence
            "chaotic": 0.55,    # Lower confidence
        }
```

### Step 3: Register and Use Your Composition

```python
# Register the new pattern with the composition framework
from kinda.composition import get_composition_engine

def register_kinda_sure_pattern():
    """Register the kinda_sure composition pattern."""
    engine = get_composition_engine()

    # Create and register the pattern
    kinda_sure_pattern = KindaSureComposition("kinda_sure_pattern", threshold=2)
    engine.register_composite(kinda_sure_pattern)

    return kinda_sure_pattern

# Use in your construct definition
def kinda_sure(condition=True):
    """~kinda_sure construct: Requires 2/3 basic construct agreement."""
    try:
        engine = get_composition_engine()
        pattern = engine.get_composite("kinda_sure_pattern")

        if pattern is None:
            pattern = register_kinda_sure_pattern()

        return pattern.compose(condition)

    except Exception as e:
        # Fallback: Use majority vote of basic constructs
        from kinda.personality import chaos_random
        results = [
            chaos_random() < 0.7,  # sometimes-like probability
            chaos_random() < 0.5,  # maybe-like probability
            chaos_random() < 0.2,  # rarely-like probability
        ]
        return sum(results) >= 2
```

### Step 4: Test Your Composition

```python
# Test the new composition
def test_kinda_sure_composition():
    """Test our custom composition."""
    from kinda.personality import PersonalityContext

    # Test across different personalities
    personalities = ["reliable", "cautious", "playful", "chaotic"]

    for personality in personalities:
        with PersonalityContext(personality):
            # Statistical test
            successes = 0
            trials = 1000

            for _ in range(trials):
                if kinda_sure(True):
                    successes += 1

            success_rate = successes / trials
            print(f"{personality}: {success_rate:.2%} success rate")

            # Verify it's within expected range for personality
            pattern = get_composition_engine().get_composite("kinda_sure_pattern")
            expected = pattern.get_target_probabilities()[personality]
            tolerance = 0.05

            assert abs(success_rate - expected) < tolerance, \
                f"{personality}: Expected {expected:.2%}, got {success_rate:.2%}"

# Run the test
test_kinda_sure_composition()
```

## 🏗️ Tutorial 3: Framework-Integrated Compositions

### Step 1: Using CompositionPatternFactory

For common patterns, use the built-in factory methods:

```python
from kinda.composition import CompositionPatternFactory, get_composition_engine

def create_quick_union_composition():
    """Create a union composition using the factory."""

    # Define bridge probabilities
    bridge_config = {
        "reliable": 0.0,
        "cautious": 0.05,
        "playful": 0.15,
        "chaotic": 0.20,
    }

    # Create union pattern (OR logic)
    union_pattern = CompositionPatternFactory.create_union_pattern(
        name="quick_union",
        constructs=["sometimes", "maybe"],
        bridge_probs=bridge_config
    )

    # Register with engine
    engine = get_composition_engine()
    engine.register_composite(union_pattern)

    return union_pattern

def create_quick_threshold_composition():
    """Create a threshold composition using the factory."""

    # Create threshold pattern (2/3 agreement)
    threshold_pattern = CompositionPatternFactory.create_threshold_pattern(
        name="quick_threshold",
        constructs=["sometimes", "maybe", "rarely"],
        threshold=2
    )

    # Register with engine
    engine = get_composition_engine()
    engine.register_composite(threshold_pattern)

    return threshold_pattern

def create_quick_tolerance_composition():
    """Create a tolerance composition using the factory."""

    # Create tolerance pattern (like ~ish)
    tolerance_pattern = CompositionPatternFactory.create_tolerance_pattern(
        name="quick_tolerance",
        base_construct="comparison",
        tolerance_func="kinda_float"
    )

    # Register with engine
    engine = get_composition_engine()
    engine.register_composite(tolerance_pattern)

    return tolerance_pattern
```

### Step 2: Framework Integration Best Practices

**1. Dependency Validation**
```python
def robust_composition(self):
    """Always validate dependencies before execution."""
    if not self.validate_dependencies():
        # Log the issue
        missing = [name for name in self.get_basic_constructs()
                  if not construct_available(name)]
        print(f"[composition] Missing constructs: {missing}")

        # Return sensible fallback
        return self.fallback_behavior()

    # Proceed with normal composition
    return self.compose()
```

**2. Performance Monitoring**
```python
def monitored_composition(self):
    """Monitor performance during composition."""
    import time

    start_time = time.perf_counter()
    result = self.compose()
    execution_time = time.perf_counter() - start_time

    # Track performance metrics
    self.performance_metrics[time.time()] = execution_time

    # Alert if performance target exceeded
    if execution_time > self.config.performance_target:
        print(f"[performance] Composition {self.name} exceeded target: "
              f"{execution_time:.3f}s > {self.config.performance_target:.3f}s")

    return result
```

**3. Statistical Validation**
```python
def validate_composition_statistics():
    """Validate that composition behaves as expected."""
    from kinda.composition.testing import get_test_framework

    framework = get_test_framework()

    # Test composition across personalities
    personalities = ["reliable", "cautious", "playful", "chaotic"]

    for personality in personalities:
        # Get expected probability for this personality
        expected_prob = my_composition.get_target_probabilities()[personality]

        # Validate with framework
        passed = framework.validate_composition_probability(
            my_composition,
            personality,
            expected_prob,
            tolerance=0.05
        )

        assert passed, f"Composition failed validation for {personality}"
```

## 🔧 Tutorial 4: Advanced Integration Patterns

### Step 1: Multi-Level Composition

Build compositions that use other compositions as components:

```python
class MetaComposition(CompositeConstruct):
    """Composition that uses other compositions as components."""

    def get_basic_constructs(self):
        # This composition depends on other compositions!
        return ["sorta_pattern", "ish_pattern", "kinda_sure_pattern"]

    def compose(self, *args, **kwargs):
        """Execute meta-composition logic."""
        engine = get_composition_engine()

        # Get component compositions
        sorta = engine.get_composite("sorta_pattern")
        ish = engine.get_composite("ish_pattern")
        kinda_sure = engine.get_composite("kinda_sure_pattern")

        # Combine their results
        results = [
            sorta.compose(True),
            ish.compose_comparison(args[0], args[1]) if len(args) >= 2 else False,
            kinda_sure.compose(True),
        ]

        # Meta-logic: Require majority agreement
        return sum(results) >= 2
```

### Step 2: Context-Aware Composition

Create compositions that adapt behavior based on usage context:

```python
class ContextAwareComposition(CompositeConstruct):
    """Composition that adapts behavior based on context."""

    def compose(self, *args, context=None, **kwargs):
        """Execute context-aware composition."""

        # Adapt strategy based on context
        if context == "critical":
            # Use higher threshold for critical operations
            return self._execute_critical_mode(*args, **kwargs)
        elif context == "experimental":
            # Use more chaotic behavior for experiments
            return self._execute_experimental_mode(*args, **kwargs)
        else:
            # Default behavior
            return self._execute_default_mode(*args, **kwargs)

    def _execute_critical_mode(self, *args, **kwargs):
        """Conservative composition for critical operations."""
        # Require all basic constructs to succeed
        results = [sometimes(True), maybe(True)]
        return all(results)

    def _execute_experimental_mode(self, *args, **kwargs):
        """Chaotic composition for experimental operations."""
        # Any single construct success is enough
        results = [sometimes(True), maybe(True), rarely(True)]
        return any(results)

    def _execute_default_mode(self, *args, **kwargs):
        """Standard union composition."""
        gate1 = sometimes(True)
        gate2 = maybe(True)
        return gate1 or gate2
```

## ⚡ Performance Optimization

### Caching and Lazy Loading

```python
class OptimizedComposition(CompositeConstruct):
    """Composition with performance optimizations."""

    def __init__(self, name, config):
        super().__init__(name, config)
        self._component_cache = {}
        self._result_cache = {}

    def compose(self, *args, **kwargs):
        """Execute optimized composition with caching."""

        # Check result cache first
        cache_key = (args, tuple(sorted(kwargs.items())))
        if cache_key in self._result_cache:
            return self._result_cache[cache_key]

        # Execute composition
        result = self._execute_composition(*args, **kwargs)

        # Cache result (with size limit)
        if len(self._result_cache) < 1000:
            self._result_cache[cache_key] = result

        return result

    def get_cached_component(self, component_name):
        """Get component with caching."""
        if component_name not in self._component_cache:
            self._component_cache[component_name] = self._load_component(component_name)

        return self._component_cache[component_name]
```

## 🧪 Testing Your Compositions

### Comprehensive Test Suite Template

```python
import unittest
from kinda.personality import PersonalityContext
from kinda.composition.testing import get_test_framework

class TestMyComposition(unittest.TestCase):
    """Test suite for custom composition."""

    def setUp(self):
        """Set up test environment."""
        self.test_framework = get_test_framework()
        self.composition = MyComposition("test_composition")

    def test_basic_functionality(self):
        """Test basic composition functionality."""
        # Test that it returns boolean
        result = self.composition.compose(True)
        self.assertIsInstance(result, bool)

    def test_dependency_validation(self):
        """Test dependency validation."""
        dependencies = self.composition.get_basic_constructs()
        self.assertTrue(self.composition.validate_dependencies())
        self.assertGreater(len(dependencies), 0)

    def test_personality_behavior(self):
        """Test behavior across all personalities."""
        personalities = ["reliable", "cautious", "playful", "chaotic"]

        for personality in personalities:
            with PersonalityContext(personality):
                with self.subTest(personality=personality):
                    # Statistical test
                    successes = sum(self.composition.compose(True) for _ in range(100))
                    success_rate = successes / 100

                    # Should be reasonable probability
                    self.assertGreater(success_rate, 0.1)
                    self.assertLess(success_rate, 0.99)

    def test_performance(self):
        """Test performance characteristics."""
        import time

        start_time = time.perf_counter()
        for _ in range(1000):
            self.composition.compose(True)
        execution_time = time.perf_counter() - start_time

        # Should complete within reasonable time
        self.assertLess(execution_time, 1.0)  # 1 second for 1000 calls

    def test_error_handling(self):
        """Test error handling and fallback behavior."""
        # Test with invalid arguments
        try:
            result = self.composition.compose(None)
            # Should either succeed or raise appropriate exception
            self.assertIsInstance(result, bool)
        except Exception as e:
            # If it raises exception, should be meaningful
            self.assertIsInstance(e, (ValueError, RuntimeError))
```

## 📝 Next Steps

Once you've mastered the basics:

1. **Study [Working Examples](./examples/)** - See real implementations in action
2. **Explore [Advanced Patterns](./advanced-patterns.md)** - Learn sophisticated composition techniques
3. **Review [API Reference](./api-reference.md)** - Master the complete framework API
4. **Check [Best Practices](./best-practices.md)** - Avoid common pitfalls

## 🎯 Quick Reference

### Essential Framework Classes

- **`CompositeConstruct`**: Base class for all compositions
- **`CompositionConfig`**: Configuration for composition behavior
- **`CompositionEngine`**: Central registry and execution engine
- **`CompositionPatternFactory`**: Factory for common patterns

### Essential Functions

- **`get_composition_engine()`**: Get the global composition engine
- **`is_framework_ready()`**: Check if framework is initialized
- **`validate_framework_installation()`**: Run full framework validation

### Common Patterns

- **Union**: `gate1 or gate2` (like ~sorta)
- **Intersection**: `gate1 and gate2` (strict requirements)
- **Threshold**: `count(successes) >= threshold` (consensus)
- **Tolerance**: `fuzzy_comparison(a, b, tolerance)` (like ~ish)

---

**Next**: [Working Examples](./examples/) - See compositions in action with complete implementations.