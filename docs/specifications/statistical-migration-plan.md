# Statistical Testing Framework - Migration Plan

## Document Information

- **Version**: 1.0
- **Date**: 2025-09-18
- **Architect**: Architect Agent
- **Issue**: #125 - Statistical Testing Framework
- **Purpose**: Complete migration strategy from hardcoded thresholds to statistical assertions

## Migration Overview

This document provides a comprehensive plan for migrating ~35 test files from hardcoded probabilistic thresholds to scientifically rigorous statistical assertions using confidence intervals.

## Current State Analysis

### Hardcoded Threshold Inventory

**Total Files Identified**: 35 test files with numeric assertions
**Pattern Categories**:
1. **Probabilistic Rate Assertions**: `assert rate >= 0.6` (success rates)
2. **Range Bounds**: `assert 0.35 <= variance <= 0.45` (variance bounds)
3. **Performance Thresholds**: `assert time < 10.0` (timing constraints)
4. **Proportion Validation**: `assert count/total >= 0.7` (proportion tests)

### Priority Classification

#### High Priority Files (Critical Probabilistic Behavior)

**1. Core Probabilistic Constructs** (8 files)
- `tests/python/test_maybe_construct.py` - ~maybe (60% probability)
- `tests/python/test_sometimes_construct.py` - ~sometimes (70% probability)
- `tests/python/test_rarely_construct.py` - ~rarely (15% probability)
- `tests/python/test_probably_construct.py` - ~probably (70% probability)
- `tests/python/test_repetition_constructs.py` - repetition variance validation
- `tests/python/test_personality_integration.py` - personality-adjusted probabilities
- `tests/python/test_statistical_assertions.py` - existing statistical patterns
- `tests/python/test_kinda_bool_construct.py` - uncertainty measurements

**Hardcoded Patterns Found**:
```python
# Current problematic patterns
assert result == False  # Should not execute when random >= 0.6
assert chaotic_variance >= 0.35  # Should be around 0.4 or higher
assert reliable_confidence >= 0.90
assert repeat_cv <= 0.25  # Cautious should have moderate variance
assert profile.sometimes_base >= 0.9
assert uncertainty <= 0.5  # Uncertainty should be capped at 0.5
```

#### Medium Priority Files (Integration & Performance) (15 files)

**2. Documentation Examples** (3 files)
- `tests/documentation/test_probabilistic_control_flow_examples.py`
- `tests/documentation/test_integration_examples.py`
- `tests/test_cli.py`

**3. Performance & Timing Tests** (12 files)
- `tests/python/test_ish_performance_benchmark.py`
- `tests/python/test_time_drift.py`
- `tests/python/test_advanced_integration_optimization.py`
- `tests/python/test_fuzzy_runtime_comprehensive.py`
- `tests/python/test_repetition_personality.py`
- Plus 7 other performance-related files

#### Low Priority Files (Simple Numeric Bounds) (12 files)

**4. Simple Validation Tests**
- Version checks, installation tests, basic bounds validation
- Non-probabilistic numeric assertions that don't need statistical treatment

## Migration Strategy

### Phase 1: Framework Implementation (Week 1)
**Goal**: Implement core statistical framework components

**Tasks**:
1. ✅ Implement `kinda/testing/confidence.py`
2. ✅ Implement `kinda/testing/assertions.py`
3. ✅ Implement `kinda/testing/distributions.py`
4. ✅ Extend `kinda/testing/pytest_plugin.py` for statistical fixtures
5. ✅ Add comprehensive unit tests for mathematical accuracy

**Deliverables**:
- Working statistical assertion API
- Pytest integration fixtures
- Mathematical validation tests

### Phase 2: High Priority Migration (Week 2, Days 1-3)
**Goal**: Convert critical probabilistic construct tests

#### 2.1 Core Construct Tests Migration

**File: `tests/python/test_maybe_construct.py`**

*Current Pattern*:
```python
@patch("kinda.personality.chaos_random")
@patch("kinda.personality.chaos_probability")
def test_maybe_probability_no_execution(self, mock_chaos_prob, mock_random):
    mock_random.return_value = 0.7  # Should not execute
    mock_chaos_prob.return_value = 0.6  # Probability threshold

    result = maybe(True)
    assert result == False  # Should not execute when random >= 0.6
```

*Migrated Pattern*:
```python
def test_maybe_construct_probability(statistical_tester):
    """Test ~maybe construct using statistical validation."""
    successes = 0
    trials = 100

    for _ in range(trials):
        if maybe(True):  # ~maybe construct
            successes += 1

    # Statistical assertion instead of hardcoded threshold
    statistical_tester.binomial_assert(
        successes, trials, expected_p=0.6, confidence=0.95,
        context="~maybe construct probability validation"
    )
```

**File: `tests/python/test_repetition_constructs.py`**

*Current Pattern*:
```python
assert chaotic_variance >= 0.35  # Should be around 0.4 or higher
assert reliable_confidence >= 0.90
assert repeat_cv <= 0.25  # Cautious should have moderate variance
```

*Migrated Pattern*:
```python
def test_repetition_variance_distribution(statistical_tester):
    """Test repetition variance follows expected distribution."""
    variance_samples = []

    for _ in range(50):  # Multiple test runs
        repeat_counts = []
        for _ in range(20):  # Multiple repetitions per run
            count = kinda_repeat_count(5)  # Target 5 repetitions
            repeat_counts.append(count)

        variance = statistics.variance(repeat_counts)
        variance_samples.append(variance)

    # Statistical validation of variance distribution
    avg_variance = statistics.mean(variance_samples)

    # Use confidence interval instead of hardcoded bounds
    statistical_tester.statistical_assert(
        avg_variance, expected=0.4, n=len(variance_samples),
        confidence=0.95, tolerance=0.15,
        context="repetition variance validation"
    )
```

#### 2.2 Personality Integration Tests

**File: `tests/python/test_personality_integration.py`**

*Current Pattern*:
```python
assert profile.sometimes_base >= 0.9
assert profile.maybe_base >= 0.9
assert profile.chaos_amplifier <= 0.5
```

*Migrated Pattern*:
```python
def test_personality_probability_distribution(distribution_tester):
    """Test personality system produces expected probability distribution."""
    # Collect construct behavior under personality
    construct_samples = {"sometimes": 0, "maybe": 0, "rarely": 0}
    trials = 200

    for _ in range(trials):
        if sometimes(True):
            construct_samples["sometimes"] += 1
        if maybe(True):
            construct_samples["maybe"] += 1
        if rarely(True):
            construct_samples["rarely"] += 1

    # Get expected probabilities from personality system
    personality = get_personality()
    expected_probs = {
        "sometimes": personality.get_chaos_probability("sometimes"),
        "maybe": personality.get_chaos_probability("maybe"),
        "rarely": personality.get_chaos_probability("rarely")
    }

    # Statistical distribution validation
    result = distribution_tester.personality_distribution_test(
        construct_samples, expected_probs, significance=0.05
    )

    assert result.is_valid, result.message
```

### Phase 3: Medium Priority Migration (Week 2, Days 4-5)

#### 3.1 Documentation Example Tests

**File: `tests/documentation/test_integration_examples.py`**

*Current Pattern*:
```python
assert avg_rate > 0.2, f"Should process some records, got {avg_rate:.2%}"
assert convergence_rate >= 0.5, f"Should converge in most cases, got {convergence_rate:.2%}"
assert avg_accuracy >= 0.6, f"Should achieve reasonable accuracy, got {avg_accuracy:.3f}"
```

*Migrated Pattern*:
```python
def test_integration_example_statistical_behavior(statistical_tester):
    """Validate integration examples using statistical methods."""
    # Collect multiple runs of the integration example
    processing_rates = []
    convergence_results = []
    accuracy_scores = []

    for run in range(20):  # Multiple runs for statistical validity
        rate, converged, accuracy = run_integration_example()
        processing_rates.append(rate)
        convergence_results.append(1 if converged else 0)
        accuracy_scores.append(accuracy)

    # Statistical validation instead of hardcoded thresholds
    avg_rate = statistics.mean(processing_rates)
    statistical_tester.statistical_assert(
        avg_rate, expected=0.5, n=len(processing_rates),
        confidence=0.95, tolerance=0.3,
        context="integration processing rate"
    )

    # Convergence rate validation
    convergence_count = sum(convergence_results)
    statistical_tester.binomial_assert(
        convergence_count, len(convergence_results), expected_p=0.7,
        confidence=0.95, context="convergence rate validation"
    )

    # Accuracy distribution validation
    avg_accuracy = statistics.mean(accuracy_scores)
    statistical_tester.statistical_assert(
        avg_accuracy, expected=0.7, n=len(accuracy_scores),
        confidence=0.95, tolerance=0.1,
        context="accuracy distribution"
    )
```

#### 3.2 Performance Test Migration

**File: `tests/python/test_ish_performance_benchmark.py`**

*Current Pattern*:
```python
assert avg_creation_time < 10.0, f"Pattern creation too slow: {avg_creation_time:.3f}ms"
assert avg_retrieval_time < 100.0, f"Pattern retrieval too slow: {avg_retrieval_time:.2f}μs"
```

*Migrated Pattern*:
```python
def test_performance_statistical_validation(performance_framework):
    """Validate performance using statistical thresholds."""
    creation_times = []
    retrieval_times = []

    for _ in range(100):
        creation_time = measure_pattern_creation()
        retrieval_time = measure_pattern_retrieval()
        creation_times.append(creation_time)
        retrieval_times.append(retrieval_time)

    # Use performance framework's statistical validation
    creation_result = performance_framework.validate_performance(
        creation_times,
        lower_threshold=0.0,
        upper_threshold=15.0,  # More lenient statistical threshold
        method="robust",
        confidence_level=0.95
    )

    assert creation_result.is_valid, creation_result.message

    retrieval_result = performance_framework.validate_performance(
        retrieval_times,
        lower_threshold=0.0,
        upper_threshold=150.0,  # Statistical threshold with margin
        method="robust",
        confidence_level=0.95
    )

    assert retrieval_result.is_valid, retrieval_result.message
```

### Phase 4: Validation & Optimization (Week 2, Day 6-7)

#### 4.1 Migration Validation

**Validation Process**:
1. **A/B Testing**: Run both old and new tests in parallel
2. **Statistical Equivalence**: Verify new tests catch same issues as old tests
3. **CI Stability**: Ensure new tests are stable across CI environments
4. **Performance Impact**: Measure framework overhead

**Validation Script**:
```python
#!/usr/bin/env python3
"""
Migration validation script.
Compares old hardcoded tests with new statistical tests.
"""

def validate_migration(test_file_path):
    """Validate that migrated test maintains same detection capability."""

    # Run original test 100 times, record pass/fail
    original_results = []
    for _ in range(100):
        result = run_original_test(test_file_path)
        original_results.append(result)

    # Run statistical test 100 times, record pass/fail
    statistical_results = []
    for _ in range(100):
        result = run_statistical_test(test_file_path)
        statistical_results.append(result)

    # Compare false positive/negative rates
    original_pass_rate = sum(original_results) / len(original_results)
    statistical_pass_rate = sum(statistical_results) / len(statistical_results)

    # Should have similar pass rates (within statistical tolerance)
    rate_difference = abs(original_pass_rate - statistical_pass_rate)

    print(f"Original pass rate: {original_pass_rate:.3f}")
    print(f"Statistical pass rate: {statistical_pass_rate:.3f}")
    print(f"Rate difference: {rate_difference:.3f}")

    # Statistical test should be more stable (lower variance)
    original_variance = statistics.variance(original_results)
    statistical_variance = statistics.variance(statistical_results)

    print(f"Original variance: {original_variance:.3f}")
    print(f"Statistical variance: {statistical_variance:.3f}")

    # Assert improved stability
    assert statistical_variance <= original_variance * 1.2, \
        "Statistical test should be more stable"
```

## Conversion Examples

### Before/After Pattern Examples

#### Pattern 1: Simple Probability Assertion

**Before (Hardcoded)**:
```python
def test_sometimes_execution():
    successes = 0
    for _ in range(100):
        if sometimes(True):
            successes += 1

    success_rate = successes / 100
    assert success_rate >= 0.6  # Hardcoded threshold
```

**After (Statistical)**:
```python
def test_sometimes_execution(statistical_tester):
    successes = 0
    trials = 100

    for _ in range(trials):
        if sometimes(True):
            successes += 1

    # Statistical validation with confidence interval
    statistical_tester.binomial_assert(
        successes, trials, expected_p=0.7, confidence=0.95,
        context="~sometimes construct validation"
    )
```

#### Pattern 2: Variance/Range Validation

**Before (Hardcoded)**:
```python
def test_repetition_variance():
    variances = []
    for _ in range(20):
        counts = [kinda_repeat_count(5) for _ in range(10)]
        variance = statistics.variance(counts)
        variances.append(variance)

    avg_variance = statistics.mean(variances)
    assert 0.3 <= avg_variance <= 0.5  # Hardcoded range
```

**After (Statistical)**:
```python
def test_repetition_variance(statistical_tester):
    variances = []
    for _ in range(20):
        counts = [kinda_repeat_count(5) for _ in range(10)]
        variance = statistics.variance(counts)
        variances.append(variance)

    # Statistical validation of variance distribution
    avg_variance = statistics.mean(variances)
    statistical_tester.statistical_assert(
        avg_variance, expected=0.4, n=len(variances),
        confidence=0.95, tolerance=0.1,
        context="repetition variance distribution"
    )
```

#### Pattern 3: Performance Threshold

**Before (Hardcoded)**:
```python
def test_performance():
    times = []
    for _ in range(50):
        start = time.time()
        execute_function()
        times.append(time.time() - start)

    avg_time = statistics.mean(times)
    assert avg_time < 10.0  # Hardcoded performance threshold
```

**After (Statistical)**:
```python
def test_performance(performance_framework):
    times = []
    for _ in range(50):
        start = time.time()
        execute_function()
        times.append(time.time() - start)

    # Use performance framework's statistical validation
    result = performance_framework.validate_performance(
        times, lower_threshold=0.0, upper_threshold=12.0,
        method="robust", confidence_level=0.95
    )

    assert result.is_valid, f"Performance validation failed: {result.message}"
```

## Automated Migration Tools

### Migration Detection Script

```python
#!/usr/bin/env python3
"""
Automated tool to identify hardcoded threshold patterns.
"""

import ast
import re
from pathlib import Path
from typing import List, Dict, Tuple

class ThresholdPatternDetector(ast.NodeVisitor):
    """AST visitor to detect hardcoded threshold patterns."""

    def __init__(self):
        self.patterns = []
        self.current_function = None

    def visit_FunctionDef(self, node):
        """Track current function for context."""
        old_function = self.current_function
        self.current_function = node.name
        self.generic_visit(node)
        self.current_function = old_function

    def visit_Assert(self, node):
        """Detect assert statements with numeric comparisons."""
        if isinstance(node.test, ast.Compare):
            # Check for numeric literals in comparisons
            for comparator in node.test.comparators:
                if isinstance(comparator, ast.Constant) and isinstance(comparator.value, (int, float)):
                    pattern = {
                        'function': self.current_function,
                        'line': node.lineno,
                        'type': 'assert_comparison',
                        'value': comparator.value,
                        'operator': type(node.test.ops[0]).__name__,
                        'code': ast.unparse(node)
                    }
                    self.patterns.append(pattern)

        self.generic_visit(node)

def detect_migration_candidates(test_file_path: Path) -> List[Dict]:
    """Detect hardcoded patterns in test file."""
    try:
        with open(test_file_path, 'r') as f:
            source = f.read()

        tree = ast.parse(source)
        detector = ThresholdPatternDetector()
        detector.visit(tree)

        return detector.patterns
    except Exception as e:
        print(f"Error analyzing {test_file_path}: {e}")
        return []

def generate_migration_suggestions(patterns: List[Dict]) -> List[str]:
    """Generate migration suggestions for detected patterns."""
    suggestions = []

    for pattern in patterns:
        if pattern['type'] == 'assert_comparison':
            value = pattern['value']

            if 0.0 < value < 1.0:
                # Likely probability assertion
                suggestion = f"""
# Line {pattern['line']}: Convert probability assertion
# Old: {pattern['code']}
# New: statistical_tester.proportion_assert(observed_count, total_count, expected_p={value}, confidence=0.95)
"""
            elif value > 1.0:
                # Likely performance/count assertion
                suggestion = f"""
# Line {pattern['line']}: Convert performance/count assertion
# Old: {pattern['code']}
# New: statistical_tester.statistical_assert(observed_value, expected={value}, n=sample_size, tolerance=0.1)
"""
            else:
                suggestion = f"""
# Line {pattern['line']}: Review assertion
# {pattern['code']}
# Consider if this needs statistical treatment
"""

            suggestions.append(suggestion)

    return suggestions

def run_migration_analysis():
    """Run migration analysis on all test files."""
    test_dir = Path("tests")
    migration_report = []

    for test_file in test_dir.rglob("*.py"):
        patterns = detect_migration_candidates(test_file)
        if patterns:
            suggestions = generate_migration_suggestions(patterns)
            migration_report.append({
                'file': test_file,
                'patterns': patterns,
                'suggestions': suggestions
            })

    # Generate migration report
    with open("migration_analysis.md", "w") as f:
        f.write("# Hardcoded Threshold Migration Analysis\n\n")

        for report in migration_report:
            f.write(f"## {report['file']}\n\n")
            f.write(f"**Patterns Found**: {len(report['patterns'])}\n\n")

            for suggestion in report['suggestions']:
                f.write(suggestion + "\n")

            f.write("\n---\n\n")

if __name__ == "__main__":
    run_migration_analysis()
```

### Template Generation Tool

```python
#!/usr/bin/env python3
"""
Tool to generate statistical test templates from existing hardcoded tests.
"""

def generate_statistical_test_template(original_test_code: str) -> str:
    """Generate statistical test template from original code."""

    template = f'''
def {{test_name}}(statistical_tester):
    """Statistical version of original test."""
    # Collect samples through multiple test runs
    samples = []
    trials = 100  # Adjust based on test requirements

    for _ in range(trials):
        # Run original test logic here
        result = {{original_logic}}
        samples.append(result)

    # Statistical validation
    if isinstance(samples[0], bool):
        # Boolean results -> binomial test
        successes = sum(samples)
        statistical_tester.binomial_assert(
            successes, trials, expected_p={{expected_probability}},
            confidence=0.95, context="{{test_description}}"
        )
    else:
        # Numeric results -> statistical assert
        observed_value = statistics.mean(samples)
        statistical_tester.statistical_assert(
            observed_value, expected={{expected_value}}, n=len(samples),
            confidence=0.95, tolerance={{tolerance}},
            context="{{test_description}}"
        )

# Original test (commented out for reference):
# {original_test_code}
'''

    return template
```

## Testing Strategy

### Migration Testing Protocol

#### 1. Parallel Testing Phase

**Duration**: 1 week
**Process**:
- Run both old and new tests in CI
- Compare pass/fail rates
- Identify discrepancies
- Tune statistical parameters

#### 2. A/B Testing

**Methodology**:
- 50% of CI runs use old tests
- 50% of CI runs use new tests
- Monitor stability and detection capability
- Adjust confidence levels based on CI environment

#### 3. Gradual Rollout

**Week 1**: High priority files (8 files)
**Week 2**: Medium priority files (15 files)
**Week 3**: Low priority files (12 files)
**Week 4**: Full migration completion

### Quality Gates

#### Statistical Accuracy
- ✅ Confidence intervals mathematically correct
- ✅ Type I error rate ≤ 5%
- ✅ Statistical power ≥ 80%
- ✅ Cross-platform stability verified

#### Performance Requirements
- ✅ Framework overhead < 1%
- ✅ CI execution time increase < 5%
- ✅ Memory usage < 10MB additional
- ✅ Test reliability improved

#### Developer Experience
- ✅ Clear migration documentation
- ✅ Automated detection tools
- ✅ Template generation helpers
- ✅ Error messages provide statistical context

## Risk Mitigation

### Technical Risks

**Risk**: Statistical tests more complex than hardcoded thresholds
**Mitigation**:
- Provide simple default configurations
- Clear documentation with examples
- Automated migration tools

**Risk**: CI environment affects statistical stability
**Mitigation**:
- Environment-specific confidence adjustments
- Robust statistical methods (Wilson score)
- Fallback mechanisms

**Risk**: Migration introduces new test failures
**Mitigation**:
- Parallel testing during transition
- Conservative statistical parameters initially
- Gradual rollout with monitoring

### Project Risks

**Risk**: Migration timeline exceeds 2 weeks
**Mitigation**:
- Prioritized file migration order
- Automated tools to accelerate conversion
- Focus on high-impact files first

**Risk**: Team resistance to statistical complexity
**Mitigation**:
- Training materials and workshops
- Simple API with sensible defaults
- Clear benefits demonstration

## Success Metrics

### Quantitative Goals

**Test Reliability**:
- ❌ Reduce false positive rate by 50%
- ❌ Reduce false negative rate by 30%
- ❌ Increase cross-platform consistency to 95%

**Scientific Rigor**:
- ❌ All probabilistic assertions use confidence intervals
- ❌ Statistical significance properly calculated
- ❌ Multiple testing correction available

**Performance**:
- ❌ Statistical framework overhead < 1%
- ❌ Migration completion within 2 weeks
- ❌ CI stability maintained or improved

### Qualitative Goals

**Developer Experience**:
- Clear, understandable error messages
- Intuitive API for test authors
- Comprehensive documentation and examples
- Smooth migration path from existing patterns

**Long-term Benefits**:
- Foundation for advanced statistical features
- Academic credibility for research applications
- Regulatory compliance capability
- Professional-grade testing framework

## Implementation Schedule

### Week 1: Framework & High Priority Migration
**Days 1-2**: Core framework implementation
**Days 3-4**: High priority file migration (construct tests)
**Day 5**: Integration testing and validation

### Week 2: Medium Priority & Validation
**Days 1-2**: Medium priority file migration (documentation, performance)
**Days 3-4**: Migration validation and optimization
**Day 5**: Documentation and training materials

### Deliverables Timeline

**Week 1**:
- ✅ Statistical framework implemented
- ✅ 8 high priority files migrated
- ✅ Migration validation tools
- ✅ CI integration working

**Week 2**:
- ✅ 15 medium priority files migrated
- ✅ Low priority assessment completed
- ✅ Performance validation passed
- ✅ Documentation completed

**Final Outcome**:
- 23+ files migrated to statistical assertions
- <1% performance overhead achieved
- 95%+ CI stability maintained
- Professional-grade statistical testing framework operational

---

**Status**: Ready for implementation
**Dependencies**: Statistical framework completion (Week 1)
**Risk Level**: Medium (requires careful validation)
**Success Criteria**: Improved test reliability and scientific rigor