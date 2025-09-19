# Best Practices & Troubleshooting

## 🎯 Overview

This guide provides proven patterns, common pitfalls, troubleshooting techniques, and best practices for effective use of the Kinda-Lang Composition Framework. It's based on real-world experience from Epic #126 implementations and production deployments.

## ✅ Composition Design Best Practices

### 1. Start Simple, Evolve Gradually

**Good Pattern:**
```python
# Start with basic union composition
class SimpleComposition(CompositeConstruct):
    def compose(self, *args, **kwargs):
        return sometimes(True) or maybe(True)

# Evolve to more sophisticated patterns
class EvolutionComposition(CompositeConstruct):
    def compose(self, *args, **kwargs):
        basic_result = sometimes(True) or maybe(True)
        if not basic_result:
            return self._apply_bridge_probability()
        return basic_result
```

**Anti-Pattern:**
```python
# Don't start with overly complex compositions
class OverComplexComposition(CompositeConstruct):
    def compose(self, *args, **kwargs):
        # 15 lines of complex logic, multiple strategies,
        # machine learning, external APIs, etc.
        # Too complex for initial implementation
        pass
```

### 2. Maintain Clear Dependency Hierarchies

**Good Practice: Dependency Layers**
```python
# Layer 1: Basic constructs (no dependencies)
basic_constructs = ["sometimes", "maybe", "rarely"]

# Layer 2: Simple compositions (depend only on Layer 1)
simple_compositions = ["sorta_pattern", "ish_pattern"]

# Layer 3: Complex compositions (depend on Layer 1 + 2)
complex_compositions = ["eventually_pattern", "consensus_pattern"]
```

**Avoid: Circular Dependencies**
```python
# Bad: Circular dependency
class PatternA(CompositeConstruct):
    def get_basic_constructs(self):
        return ["pattern_b"]  # Depends on Pattern B

class PatternB(CompositeConstruct):
    def get_basic_constructs(self):
        return ["pattern_a"]  # Depends on Pattern A (circular!)
```

### 3. Design for Testability

**Good: Testable Composition**
```python
class TestableComposition(CompositeConstruct):
    def __init__(self, name: str, config: CompositionConfig):
        super().__init__(name, config)
        self.execution_count = 0
        self.last_result = None

    def compose(self, *args, **kwargs):
        self.execution_count += 1

        # Clear, predictable logic
        gate1 = sometimes(True)
        gate2 = maybe(True)
        result = gate1 or gate2

        self.last_result = result
        return result

    def get_debug_info(self):
        """Provide debug information for testing"""
        return {
            'execution_count': self.execution_count,
            'last_result': self.last_result,
            'dependencies': self.get_basic_constructs()
        }
```

### 4. Implement Robust Error Handling

**Comprehensive Error Handling Pattern:**
```python
class RobustComposition(CompositeConstruct):
    def compose(self, *args, **kwargs):
        try:
            # Validate dependencies first
            if not self.validate_dependencies():
                return self._dependency_fallback(*args, **kwargs)

            # Validate arguments
            if not self._validate_arguments(*args, **kwargs):
                return self._argument_fallback(*args, **kwargs)

            # Execute main composition logic
            return self._execute_composition(*args, **kwargs)

        except Exception as e:
            # Log error with context
            self._log_composition_error(e, *args, **kwargs)

            # Attempt graceful degradation
            return self._error_fallback(e, *args, **kwargs)

    def _dependency_fallback(self, *args, **kwargs):
        """Fallback when dependencies unavailable"""
        print(f"[{self.name}] Dependencies unavailable, using simple fallback")
        from kinda.personality import chaos_random
        return chaos_random() < 0.5

    def _argument_fallback(self, *args, **kwargs):
        """Fallback when arguments invalid"""
        print(f"[{self.name}] Invalid arguments, using default behavior")
        return True

    def _error_fallback(self, error: Exception, *args, **kwargs):
        """Final fallback for unexpected errors"""
        print(f"[{self.name}] Unexpected error: {error}")
        # Return safe default
        return False

    def _validate_arguments(self, *args, **kwargs) -> bool:
        """Validate composition arguments"""
        # Add specific validation logic for your composition
        return True

    def _log_composition_error(self, error: Exception, *args, **kwargs):
        """Log composition errors with context"""
        context = {
            'composition': self.name,
            'error': str(error),
            'args': str(args),
            'kwargs': str(kwargs)
        }
        print(f"[error] Composition failed: {context}")
```

## ⚡ Performance Best Practices

### 1. Optimize Pattern Registration

**Efficient Pattern Management:**
```python
class OptimizedPatternManager:
    """Efficient pattern management for production use"""

    def __init__(self):
        self._pattern_cache = {}
        self._lazy_loaders = {}
        self.cache_stats = {'hits': 0, 'misses': 0}

    def register_lazy_pattern(self, name: str, factory: Callable):
        """Register pattern with lazy loading"""
        self._lazy_loaders[name] = factory

    def get_pattern(self, name: str):
        """Get pattern with caching and lazy loading"""
        if name in self._pattern_cache:
            self.cache_stats['hits'] += 1
            return self._pattern_cache[name]

        self.cache_stats['misses'] += 1

        if name in self._lazy_loaders:
            pattern = self._lazy_loaders[name]()
            self._pattern_cache[name] = pattern
            return pattern

        raise ValueError(f"Pattern {name} not found")

    def get_cache_efficiency(self) -> float:
        """Get cache hit rate"""
        total = self.cache_stats['hits'] + self.cache_stats['misses']
        return self.cache_stats['hits'] / total if total > 0 else 0.0

# Usage
manager = OptimizedPatternManager()

# Register patterns lazily
manager.register_lazy_pattern(
    "expensive_pattern",
    lambda: ExpensiveComposition("expensive_pattern")
)

# Patterns only created when first accessed
pattern = manager.get_pattern("expensive_pattern")
```

### 2. Implement Smart Caching

**Result Caching Strategy:**
```python
from functools import lru_cache
import hashlib

class CachedComposition(CompositeConstruct):
    """Composition with intelligent result caching"""

    def __init__(self, name: str, config: CompositionConfig):
        super().__init__(name, config)
        self._cache_size = 1000
        self._cache_hits = 0
        self._cache_misses = 0

    def compose(self, *args, **kwargs):
        """Execute with caching for deterministic cases"""

        # Check if this execution can be cached
        if self._is_cacheable(*args, **kwargs):
            cache_key = self._generate_cache_key(*args, **kwargs)
            cached_result = self._get_cached_result(cache_key)

            if cached_result is not None:
                self._cache_hits += 1
                return cached_result

        # Execute composition
        result = self._execute_composition(*args, **kwargs)

        # Cache result if appropriate
        if self._is_cacheable(*args, **kwargs):
            cache_key = self._generate_cache_key(*args, **kwargs)
            self._cache_result(cache_key, result)
            self._cache_misses += 1

        return result

    def _is_cacheable(self, *args, **kwargs) -> bool:
        """Determine if execution can be cached"""
        # Don't cache if personality affects randomness significantly
        from kinda.personality import get_personality
        personality = get_personality().mood

        # Only cache for reliable personality (most deterministic)
        return personality == "reliable"

    def _generate_cache_key(self, *args, **kwargs) -> str:
        """Generate cache key for arguments"""
        key_data = f"{args}:{sorted(kwargs.items())}"
        return hashlib.md5(key_data.encode()).hexdigest()

    @lru_cache(maxsize=1000)
    def _get_cached_result(self, cache_key: str):
        """Get cached result (using LRU cache)"""
        return None  # Cache miss

    def _cache_result(self, cache_key: str, result):
        """Cache execution result"""
        # Implementation would store in actual cache
        pass

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get caching statistics"""
        total = self._cache_hits + self._cache_misses
        hit_rate = self._cache_hits / total if total > 0 else 0.0

        return {
            'hit_rate': hit_rate,
            'hits': self._cache_hits,
            'misses': self._cache_misses,
            'total': total
        }
```

### 3. Monitor Performance Continuously

**Production Performance Monitoring:**
```python
import time
from collections import deque

class PerformanceMonitor:
    """Continuous performance monitoring for compositions"""

    def __init__(self, window_size: int = 1000):
        self.execution_times = deque(maxlen=window_size)
        self.error_counts = {}
        self.slow_operations = deque(maxlen=100)
        self.performance_alerts = []

    def record_execution(self, composition_name: str, execution_time: float,
                        success: bool, args_count: int = 0):
        """Record execution metrics"""

        self.execution_times.append(execution_time)

        # Track errors
        if not success:
            self.error_counts[composition_name] = self.error_counts.get(composition_name, 0) + 1

        # Track slow operations
        if execution_time > 0.001:  # 1ms threshold
            self.slow_operations.append({
                'composition': composition_name,
                'time': execution_time,
                'args_count': args_count,
                'timestamp': time.time()
            })

        # Check for performance alerts
        self._check_performance_alerts(composition_name, execution_time)

    def _check_performance_alerts(self, composition_name: str, execution_time: float):
        """Check for performance issues and generate alerts"""

        # Alert on slow execution
        if execution_time > 0.005:  # 5ms threshold
            alert = f"Slow execution: {composition_name} took {execution_time*1000:.2f}ms"
            self.performance_alerts.append(alert)

        # Alert on high error rate
        total_executions = len(self.execution_times)
        error_count = self.error_counts.get(composition_name, 0)

        if total_executions > 100 and error_count / total_executions > 0.05:  # 5% error rate
            alert = f"High error rate: {composition_name} has {error_count}/{total_executions} errors"
            self.performance_alerts.append(alert)

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get current performance summary"""
        if not self.execution_times:
            return {"error": "No performance data available"}

        import statistics

        return {
            'mean_time': statistics.mean(self.execution_times),
            'median_time': statistics.median(self.execution_times),
            'max_time': max(self.execution_times),
            'min_time': min(self.execution_times),
            'total_executions': len(self.execution_times),
            'slow_operations_count': len(self.slow_operations),
            'error_counts': self.error_counts.copy(),
            'recent_alerts': self.performance_alerts[-5:]  # Last 5 alerts
        }

# Global monitor instance
_performance_monitor = PerformanceMonitor()

def get_performance_monitor() -> PerformanceMonitor:
    """Get global performance monitor"""
    return _performance_monitor

# Decorator for automatic monitoring
def monitor_composition(func):
    """Decorator to automatically monitor composition performance"""
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        success = False

        try:
            result = func(*args, **kwargs)
            success = True
            return result
        except Exception as e:
            raise
        finally:
            execution_time = time.perf_counter() - start_time
            monitor = get_performance_monitor()
            monitor.record_execution(
                func.__name__, execution_time, success, len(args)
            )

    return wrapper

# Usage
@monitor_composition
def my_composition_function(*args, **kwargs):
    # Your composition logic
    pass
```

## 🧪 Testing Best Practices

### 1. Comprehensive Test Strategies

**Multi-Layer Testing Approach:**
```python
class ComprehensiveCompositionTest(unittest.TestCase):
    """Comprehensive testing strategy for compositions"""

    def setUp(self):
        """Set up test environment"""
        PersonalityContext._instance = None
        self.composition = MyComposition("test_composition")

    def test_basic_functionality(self):
        """Layer 1: Basic functionality testing"""
        # Test basic execution
        result = self.composition.compose(True)
        self.assertIsInstance(result, bool)

    def test_dependency_validation(self):
        """Layer 2: Dependency testing"""
        # Test dependency validation
        self.assertTrue(self.composition.validate_dependencies())

        # Test with missing dependencies
        with patch_missing_construct("sometimes"):
            self.assertFalse(self.composition.validate_dependencies())

    def test_personality_consistency(self):
        """Layer 3: Personality behavior testing"""
        personalities = ["reliable", "cautious", "playful", "chaotic"]

        for personality in personalities:
            with PersonalityContext(personality):
                with self.subTest(personality=personality):
                    results = [self.composition.compose(True) for _ in range(100)]
                    success_rate = sum(results) / len(results)

                    # Verify reasonable behavior for personality
                    if personality == "reliable":
                        self.assertGreater(success_rate, 0.7)
                    elif personality == "chaotic":
                        self.assertLess(success_rate, 0.8)

    def test_statistical_behavior(self):
        """Layer 4: Statistical validation"""
        from kinda.composition.testing import CompositionAssertion

        # Test across multiple personalities
        for personality in ["reliable", "cautious", "playful", "chaotic"]:
            with PersonalityContext(personality):
                results = [self.composition.compose(True) for _ in range(1000)]
                target_probs = self.composition.get_target_probabilities()
                expected = target_probs.get(personality, 0.5)

                success_rate = sum(results) / len(results)
                self.assertAlmostEqual(success_rate, expected, delta=0.1)

    def test_performance_characteristics(self):
        """Layer 5: Performance testing"""
        import time

        # Benchmark execution time
        start_time = time.perf_counter()
        for _ in range(1000):
            self.composition.compose(True)
        execution_time = time.perf_counter() - start_time

        # Should complete within reasonable time
        self.assertLess(execution_time, 1.0)  # 1 second for 1000 calls

        avg_time = execution_time / 1000
        print(f"Average execution time: {avg_time*1000:.3f}ms")

    def test_error_handling(self):
        """Layer 6: Error handling testing"""
        # Test with invalid arguments
        try:
            result = self.composition.compose(None)
            self.assertIsInstance(result, bool)  # Should handle gracefully
        except Exception as e:
            self.assertIsInstance(e, (ValueError, RuntimeError))

        # Test with component failures
        with patch_component_failure("sometimes"):
            result = self.composition.compose(True)
            # Should either succeed or fail gracefully
            self.assertIsInstance(result, bool)

    def test_integration_with_framework(self):
        """Layer 7: Framework integration testing"""
        from kinda.composition import get_composition_engine

        engine = get_composition_engine()
        engine.register_composite(self.composition)

        # Test retrieval
        retrieved = engine.get_composite(self.composition.name)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.name, self.composition.name)
```

### 2. Statistical Testing Patterns

**Robust Statistical Validation:**
```python
def validate_composition_statistics(composition: CompositeConstruct,
                                  trials: int = 5000,
                                  confidence_level: float = 0.95):
    """Robust statistical validation of composition behavior"""

    from scipy import stats
    import numpy as np

    personalities = ["reliable", "cautious", "playful", "chaotic"]
    results = {}

    for personality in personalities:
        with PersonalityContext(personality):
            # Collect results
            outcomes = [composition.compose(True) for _ in range(trials)]
            success_rate = sum(outcomes) / len(outcomes)

            # Get expected probability
            target_probs = composition.get_target_probabilities()
            expected_prob = target_probs.get(personality, 0.5)

            # Calculate confidence interval
            successes = sum(outcomes)
            ci_lower, ci_upper = stats.binom.interval(
                confidence_level, trials, expected_prob
            )

            ci_lower_rate = ci_lower / trials
            ci_upper_rate = ci_upper / trials

            # Statistical tests
            is_within_ci = ci_lower_rate <= success_rate <= ci_upper_rate

            # Chi-square goodness of fit test
            expected_successes = trials * expected_prob
            expected_failures = trials * (1 - expected_prob)
            observed_successes = successes
            observed_failures = trials - successes

            chi2_stat, p_value = stats.chisquare(
                [observed_successes, observed_failures],
                [expected_successes, expected_failures]
            )

            results[personality] = {
                'success_rate': success_rate,
                'expected_rate': expected_prob,
                'within_confidence_interval': is_within_ci,
                'confidence_interval': (ci_lower_rate, ci_upper_rate),
                'chi2_p_value': p_value,
                'statistically_valid': p_value > 0.05,  # Fail to reject null hypothesis
                'sample_size': trials
            }

    return results

# Usage
stats_results = validate_composition_statistics(my_composition)
for personality, stats in stats_results.items():
    if stats['statistically_valid']:
        print(f"✅ {personality}: Statistically valid behavior")
    else:
        print(f"❌ {personality}: Statistical validation failed")
```

## 🚨 Common Pitfalls and Solutions

### 1. Pitfall: Over-Caching Non-Deterministic Results

**Problem:**
```python
# Bad: Caching probabilistic results
@lru_cache(maxsize=1000)
def bad_cached_composition(*args):
    return sometimes(True) or maybe(True)  # Result varies each call!
```

**Solution:**
```python
# Good: Only cache deterministic components
class SmartCachedComposition(CompositeConstruct):
    @lru_cache(maxsize=1000)
    def _get_target_probability(self, personality: str):
        """Cache only deterministic calculations"""
        return self.get_target_probabilities()[personality]

    def compose(self, *args, **kwargs):
        """Don't cache the probabilistic execution"""
        return sometimes(True) or maybe(True)
```

### 2. Pitfall: Ignoring Personality Context

**Problem:**
```python
# Bad: Ignoring personality in composition
def personality_blind_composition():
    # Always uses same logic regardless of personality
    return sometimes(True) and maybe(True)
```

**Solution:**
```python
# Good: Personality-aware composition
def personality_aware_composition():
    from kinda.personality import get_personality

    personality = get_personality().mood

    if personality == "reliable":
        # Conservative: require both
        return sometimes(True) and maybe(True)
    elif personality == "chaotic":
        # Adventurous: either one
        return sometimes(True) or maybe(True) or rarely(True)
    else:
        # Balanced: standard union
        return sometimes(True) or maybe(True)
```

### 3. Pitfall: Inadequate Error Handling

**Problem:**
```python
# Bad: No error handling
def fragile_composition():
    gate1 = sometimes(True)  # Could fail if 'sometimes' not available
    gate2 = maybe(True)      # Could fail if 'maybe' not available
    return gate1 or gate2    # Could fail with AttributeError
```

**Solution:**
```python
# Good: Comprehensive error handling
def robust_composition():
    try:
        # Validate dependencies
        if 'sometimes' not in globals():
            raise RuntimeError("'sometimes' construct not available")
        if 'maybe' not in globals():
            raise RuntimeError("'maybe' construct not available")

        gate1 = sometimes(True)
        gate2 = maybe(True)
        return gate1 or gate2

    except Exception as e:
        print(f"[composition] Error: {e}")
        # Fallback to simple random choice
        from kinda.personality import chaos_random
        return chaos_random() < 0.5
```

### 4. Pitfall: Performance Regression

**Problem:**
```python
# Bad: No performance consideration
def slow_composition():
    results = []
    for i in range(1000):  # Unnecessary loop
        results.append(sometimes(True))
    return any(results)
```

**Solution:**
```python
# Good: Performance-optimized
def fast_composition():
    # Simple, direct logic
    return sometimes(True) or maybe(True)

# Even better: With monitoring
@monitor_composition
def monitored_composition():
    return sometimes(True) or maybe(True)
```

## 🔧 Troubleshooting Guide

### 1. Dependency Issues

**Problem: "Required construct not available"**

**Diagnosis:**
```python
def diagnose_dependency_issues(composition: CompositeConstruct):
    """Diagnose composition dependency problems"""

    required = composition.get_basic_constructs()
    available = []
    missing = []

    for construct in required:
        if construct in globals():
            available.append(construct)
        else:
            missing.append(construct)

    print(f"Required constructs: {required}")
    print(f"Available: {available}")
    print(f"Missing: {missing}")

    return missing

# Usage
missing_deps = diagnose_dependency_issues(my_composition)
if missing_deps:
    print(f"Install missing constructs: {missing_deps}")
```

**Solutions:**
1. Ensure all required constructs are imported
2. Check construct initialization order
3. Implement graceful fallbacks

### 2. Statistical Behavior Issues

**Problem: "Composition behavior doesn't match expected probabilities"**

**Diagnosis:**
```python
def diagnose_statistical_issues(composition: CompositeConstruct, trials: int = 1000):
    """Diagnose statistical behavior problems"""

    from kinda.personality import PersonalityContext
    import statistics

    for personality in ["reliable", "cautious", "playful", "chaotic"]:
        with PersonalityContext(personality):
            results = [composition.compose(True) for _ in range(trials)]
            success_rate = sum(results) / len(results)

            target_probs = composition.get_target_probabilities()
            expected = target_probs.get(personality, 0.5)

            difference = abs(success_rate - expected)

            print(f"{personality}:")
            print(f"  Expected: {expected:.3f}")
            print(f"  Actual: {success_rate:.3f}")
            print(f"  Difference: {difference:.3f}")
            print(f"  Status: {'✅ OK' if difference < 0.1 else '❌ ISSUE'}")
```

**Solutions:**
1. Check bridge probability configuration
2. Verify component construct behavior
3. Increase sample size for testing
4. Review composition logic

### 3. Performance Issues

**Problem: "Composition is too slow"**

**Diagnosis:**
```python
import time
import cProfile

def diagnose_performance_issues(composition: CompositeConstruct):
    """Diagnose composition performance problems"""

    # Profile composition execution
    def profile_execution():
        for _ in range(1000):
            composition.compose(True)

    # Run profiler
    profiler = cProfile.Profile()
    start_time = time.perf_counter()

    profiler.enable()
    profile_execution()
    profiler.disable()

    end_time = time.perf_counter()

    # Print timing results
    total_time = end_time - start_time
    avg_time = total_time / 1000

    print(f"Total time: {total_time:.3f}s")
    print(f"Average per call: {avg_time*1000:.3f}ms")
    print(f"Calls per second: {1/avg_time:.0f}")

    # Print profiler statistics
    profiler.print_stats(sort='cumulative')
```

**Solutions:**
1. Implement pattern caching
2. Optimize component lookup
3. Reduce unnecessary calculations
4. Use lazy loading for expensive operations

### 4. Integration Issues

**Problem: "Composition doesn't work with framework"**

**Diagnosis:**
```python
def diagnose_integration_issues():
    """Diagnose framework integration problems"""

    from kinda.composition import (
        is_framework_ready,
        get_composition_engine,
        validate_framework_installation
    )

    print("Framework Diagnosis:")
    print(f"  Framework ready: {is_framework_ready()}")

    try:
        engine = get_composition_engine()
        patterns = engine.list_composites()
        print(f"  Available patterns: {len(patterns)}")
        print(f"  Pattern names: {patterns}")
    except Exception as e:
        print(f"  Engine error: {e}")

    # Full validation
    validation = validate_framework_installation()
    print(f"  Validation result: {validation}")

    return validation
```

## 📋 Production Deployment Checklist

### Pre-Deployment Validation

- [ ] **All compositions pass statistical validation** (±5% tolerance)
- [ ] **Performance targets met** (<20% overhead vs direct implementation)
- [ ] **Error handling tested** (dependency failures, argument errors)
- [ ] **Framework integration validated** (patterns registered correctly)
- [ ] **Cross-personality testing complete** (all 4 personality modes)
- [ ] **Fallback mechanisms tested** (graceful degradation works)
- [ ] **Documentation updated** (API changes, new patterns)

### Performance Monitoring Setup

- [ ] **Performance monitoring enabled** (execution time tracking)
- [ ] **Error rate monitoring configured** (failure tracking)
- [ ] **Cache efficiency monitoring** (hit rate tracking)
- [ ] **Alert thresholds set** (slow execution, high error rate)
- [ ] **Dashboards configured** (real-time performance visibility)

### Operational Readiness

- [ ] **Feature flags configured** (ability to disable compositions)
- [ ] **Rollback procedures documented** (how to revert to legacy)
- [ ] **Support team trained** (troubleshooting procedures)
- [ ] **Monitoring alerts tested** (alert delivery works)
- [ ] **Performance baselines established** (pre-deployment metrics)

## 🎯 Quick Reference

### Common Commands

```bash
# Validate framework installation
python -c "from kinda.composition import validate_framework_installation; print(validate_framework_installation())"

# Check available patterns
python -c "from kinda.composition import get_composition_engine; print(get_composition_engine().list_composites())"

# Run composition tests
pytest tests/python/test_*composition* -v

# Performance benchmark
python -m kinda.composition.benchmarks
```

### Emergency Procedures

**If compositions fail in production:**

1. **Immediate**: Set feature flag `KINDA_USE_COMPOSITION=false`
2. **Validate**: Check that fallback to legacy implementations works
3. **Investigate**: Review error logs and performance metrics
4. **Fix**: Address root cause and re-enable gradually

**Common emergency scenarios:**
- High error rate → Check dependency availability
- Slow performance → Check for cache misses or complex logic
- Statistical anomalies → Verify personality context and bridge probabilities

---

**Best Practices**: ✅ Production-Tested Guidelines
**Troubleshooting**: 🔧 Real-World Solutions
**Ready for Production**: 🚀 Deployment-Ready Framework

This concludes the comprehensive documentation for the Kinda-Lang Composition Framework, demonstrating how "Kinda builds Kinda" through systematic, transparent, and maintainable construct composition.