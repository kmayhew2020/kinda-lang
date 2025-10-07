# Statistical Testing Framework Architecture

## Document Information

- **Version**: 1.0
- **Date**: 2025-09-18
- **Architect**: Architect Agent
- **Issue**: #125 - Statistical Testing Framework
- **Priority**: Medium (Foundation Building)
- **Timeline**: 3 weeks for complete implementation

## Executive Summary

This document presents the comprehensive architecture for the Statistical Testing Framework, designed to replace ~35 test files using hardcoded probabilistic thresholds with scientifically rigorous confidence interval-based assertions. The framework provides professional-grade statistical validation for kinda-lang's probabilistic constructs while maintaining CI reliability and <1% performance overhead.

## System Overview

### Problem Statement

The current kinda-lang test suite contains ~35 test files with hardcoded probabilistic thresholds:
- `assert avg_rate > 0.2` (hardcoded 20% threshold)
- `assert convergence_rate >= 0.5` (hardcoded 50% threshold)
- `assert avg_accuracy >= 0.6` (hardcoded 60% threshold)
- `assert repeat_cv <= 0.25` (hardcoded variance threshold)

These hardcoded thresholds lack statistical rigor and create false positives/negatives due to natural probabilistic variance.

### Target Solution

Replace hardcoded assertions with statistically sound confidence interval validation:

```python
# Current (hardcoded)
assert success_rate >= 0.6  # May fail due to natural variance

# Future (statistical)
statistical_assert(success_rate, expected=0.6, confidence=0.95, n=sample_size)
```

## Architecture Design

### High-Level Component Architecture

```
kinda/testing/
├── statistics.py          (✅ exists - extend/enhance)
├── confidence.py           (NEW - confidence interval calculations)
├── assertions.py           (NEW - statistical assertion helpers)
├── distributions.py        (NEW - distribution testing utilities)
├── thresholds.py          (✅ exists - integrate with new components)
└── pytest_plugin.py      (✅ exists - extend for statistical assertions)
```

### Core Components

#### 1. Confidence Interval Engine (`confidence.py`)

**Purpose**: Provides mathematically sound confidence interval calculations.

**Key Functions**:
- `wilson_score_interval(successes, trials, confidence=0.95)` - Robust CI for proportions
- `bootstrap_confidence_interval(samples, confidence=0.95)` - Non-parametric CI for any statistic
- `binomial_confidence_interval(successes, trials, confidence=0.95)` - Exact binomial CI
- `normal_approximation_ci(mean, std, n, confidence=0.95)` - Normal approximation CI

**Mathematical Foundation**:
- **Wilson Score Intervals**: Robust for small samples and extreme probabilities
- **Bootstrap Methods**: Non-parametric, works with any statistic
- **Exact Binomial**: For precise binomial probability testing
- **Multiple Testing Correction**: Bonferroni and FDR correction methods

#### 2. Statistical Assertions (`assertions.py`)

**Purpose**: High-level statistical assertion interface for test authors.

**Key Functions**:
- `statistical_assert(observed, expected, n, confidence=0.95)` - General statistical validation
- `binomial_assert(successes, trials, expected_p, confidence=0.95)` - Binomial test validation
- `proportion_assert(count, total, expected_rate, confidence=0.95)` - Proportion testing
- `distribution_assert(observed_dist, expected_dist, method="chi_square")` - Distribution comparison

**Design Principles**:
- **Fail-Safe Defaults**: 95% confidence, robust methods
- **Clear Error Messages**: Statistical interpretation included
- **CI Compatibility**: Stable behavior across environments
- **Performance Optimized**: <1% overhead requirement

#### 3. Distribution Testing (`distributions.py`)

**Purpose**: Advanced statistical testing for probability distributions.

**Key Functions**:
- `chi_square_test(observed, expected, significance=0.05)` - Goodness-of-fit testing
- `kolmogorov_smirnov_test(sample1, sample2)` - Distribution comparison
- `anderson_darling_test(samples, distribution="normal")` - Normality testing
- `personality_distribution_test(construct_samples, personality_key)` - Kinda-specific testing

**Integration Points**:
- **Personality System**: Validates personality-adjusted probabilities
- **Construct Validation**: Tests ~maybe, ~sometimes, ~rarely behavior
- **Cross-Platform Stability**: Robust statistical methods for CI environments

#### 4. Enhanced Statistics Module (`statistics.py`)

**Current State**: Existing performance validation framework
**Enhancements**:
- Integration with confidence interval calculations
- Probabilistic construct validation methods
- Wilson score interval support
- Multiple testing correction

### System Integration Architecture

#### Integration with Existing Testing Framework

```
Existing Framework                Statistical Extensions
├── statistics.py            →   Enhanced with CI calculations
├── thresholds.py            →   Integrated with statistical thresholds
├── pytest_plugin.py        →   Extended with statistical fixtures
└── environment.py           →   Statistical environment detection

New Statistical Components
├── confidence.py            →   Core CI calculations
├── assertions.py            →   User-facing assertion API
└── distributions.py         →   Advanced distribution testing
```

#### Data Flow Architecture

```
Test Execution Flow:
1. Test runs probabilistic construct (e.g., ~maybe)
2. Collects samples (successes/failures)
3. Calls statistical_assert() with samples
4. Calculates confidence interval using Wilson score
5. Validates observed rate falls within CI
6. Returns pass/fail with statistical justification

CI Integration:
Environment Detection → Statistical Method Selection → CI Calculation → Validation
```

### API Design

#### Core Statistical Assertion API

```python
def statistical_assert(
    observed: Union[float, int],
    expected: float,
    n: int,
    confidence: float = 0.95,
    method: str = "wilson",
    tolerance: Optional[float] = None
) -> bool:
    """
    Statistically validate observed value against expected.

    Args:
        observed: Observed value (proportion or count)
        expected: Expected value/probability
        n: Sample size
        confidence: Confidence level (0.95 = 95%)
        method: Statistical method ("wilson", "binomial", "bootstrap")
        tolerance: Optional tolerance override

    Returns:
        True if observation falls within confidence interval

    Raises:
        StatisticalValidationError: If validation fails with details
    """
```

#### Binomial Testing API

```python
def binomial_assert(
    successes: int,
    trials: int,
    expected_p: float,
    confidence: float = 0.95,
    two_tailed: bool = True
) -> bool:
    """
    Validate binomial proportion using confidence intervals.

    Args:
        successes: Number of successful trials
        trials: Total number of trials
        expected_p: Expected success probability
        confidence: Confidence level
        two_tailed: Whether to use two-tailed test

    Returns:
        True if observed proportion within expected CI
    """
```

#### Distribution Testing API

```python
def distribution_assert(
    observed_distribution: Dict[str, int],
    expected_distribution: Dict[str, float],
    method: str = "chi_square",
    significance: float = 0.05
) -> bool:
    """
    Validate observed distribution matches expected.

    Args:
        observed_distribution: Observed counts by category
        expected_distribution: Expected probabilities by category
        method: Statistical test method
        significance: Significance level

    Returns:
        True if distributions match within significance level
    """
```

### Performance Considerations

#### Computational Optimization

**Wilson Score Calculation**:
- Pre-computed z-score lookup tables
- Vectorized operations for batch processing
- Caching for repeated confidence levels

**Bootstrap Methods**:
- Adaptive sample sizing (min 1000, max 10000)
- Early termination for stable estimates
- Memory-efficient streaming computation

**Performance Targets**:
- Statistical calculations: <1ms per assertion
- Wilson score intervals: <0.1ms per calculation
- Bootstrap confidence intervals: <10ms per calculation
- Total framework overhead: <1% of test execution time

#### Memory Management

**Sample Storage**:
- Streaming statistics for large samples
- Circular buffers for running calculations
- Lazy evaluation for expensive computations

**Caching Strategy**:
- Z-score lookup tables
- Precomputed confidence multipliers
- Memoized interval calculations

### Integration Patterns

#### Pytest Integration

**Custom Fixtures**:
```python
@pytest.fixture
def statistical_tester():
    """Provides statistical assertion capabilities."""
    return StatisticalTester(confidence=0.95, method="wilson")

def test_maybe_construct_probability(statistical_tester):
    """Test ~maybe construct using statistical validation."""
    successes = 0
    trials = 100

    for _ in range(trials):
        if maybe(True):  # ~maybe construct
            successes += 1

    # Statistical assertion instead of hardcoded threshold
    statistical_tester.binomial_assert(
        successes, trials, expected_p=0.6, confidence=0.95
    )
```

**Pytest Markers**:
```python
@pytest.mark.statistical(confidence=0.95, method="wilson")
def test_sometimes_construct():
    """Test marked for statistical validation."""
    pass

@pytest.mark.probabilistic(expected_p=0.7, trials=200)
def test_probably_construct():
    """Test with probabilistic behavior specification."""
    pass
```

#### Error Handling Strategy

**Statistical Validation Errors**:
```python
class StatisticalValidationError(AssertionError):
    """Raised when statistical validation fails."""

    def __init__(
        self,
        observed: float,
        expected: float,
        confidence_interval: Tuple[float, float],
        p_value: float,
        method: str
    ):
        self.observed = observed
        self.expected = expected
        self.confidence_interval = confidence_interval
        self.p_value = p_value
        self.method = method

        message = (
            f"Statistical validation failed:\n"
            f"  Observed: {observed:.3f}\n"
            f"  Expected: {expected:.3f}\n"
            f"  95% CI: [{confidence_interval[0]:.3f}, {confidence_interval[1]:.3f}]\n"
            f"  p-value: {p_value:.3f}\n"
            f"  Method: {method}"
        )
        super().__init__(message)
```

**Fallback Mechanisms**:
- Graceful degradation to simple thresholds in extreme cases
- Warning messages for unusual statistical conditions
- Automatic method selection based on sample characteristics

### Configuration System

#### Statistical Configuration

```python
class StatisticalConfig:
    """Configuration for statistical testing framework."""

    # Default confidence levels
    default_confidence: float = 0.95
    strict_confidence: float = 0.99
    lenient_confidence: float = 0.90

    # Method selection
    default_method: str = "wilson"
    small_sample_method: str = "binomial"  # n < 30
    large_sample_method: str = "normal"    # n > 1000

    # Performance limits
    max_bootstrap_samples: int = 10000
    min_bootstrap_samples: int = 1000
    sample_size_threshold: int = 30

    # CI environment adjustments
    ci_confidence_adjustment: float = 0.02  # Slightly more lenient in CI
    ci_timeout_multiplier: float = 2.0
```

#### Environment-Specific Adaptations

**CI Environment Detection**:
- GitHub Actions: Slightly more lenient thresholds
- Local Development: Standard thresholds
- Performance Testing: Stricter thresholds

**Platform Adjustments**:
- Windows: Adjusted for higher variance
- macOS: Standard configuration
- Linux: Optimized for CI stability

### Migration Strategy

#### Phase 1: Core Framework Implementation
1. Implement confidence interval calculations
2. Create statistical assertion API
3. Add pytest integration fixtures
4. Validate against existing performance tests

#### Phase 2: Test Migration
1. Identify all hardcoded threshold patterns
2. Convert high-priority test files
3. Validate statistical equivalence
4. Update CI configurations

#### Phase 3: Advanced Features
1. Distribution testing capabilities
2. Multiple testing correction
3. Advanced bootstrap methods
4. Performance optimization

### Quality Assurance

#### Testing the Statistical Framework

**Unit Tests**:
- Mathematical accuracy of confidence intervals
- API correctness and error handling
- Performance benchmarks
- Edge case handling

**Integration Tests**:
- End-to-end statistical validation workflows
- Pytest plugin integration
- CI environment compatibility
- Cross-platform stability

**Validation Tests**:
- Statistical power analysis
- False positive/negative rate validation
- Comparison with known statistical tools
- Real-world probabilistic construct testing

#### Success Metrics

**Statistical Rigor**:
- ✅ 95% confidence intervals mathematically correct
- ✅ Wilson score intervals for robust small-sample testing
- ✅ Multiple testing correction available
- ✅ Bootstrap methods for non-parametric statistics

**Performance Requirements**:
- ✅ <1% overhead for statistical calculations
- ✅ <1ms per assertion execution time
- ✅ Memory usage < 10MB for framework
- ✅ CI test execution time increase < 5%

**Developer Experience**:
- ✅ Clear, intuitive API for test authors
- ✅ Informative error messages with statistical context
- ✅ Seamless pytest integration
- ✅ Backward compatibility during migration

## Design Decisions and Rationale

### Choice of Wilson Score Intervals

**Decision**: Use Wilson score intervals as the default confidence interval method.

**Rationale**:
- More robust for small samples than normal approximation
- Better behavior at extreme probabilities (near 0 or 1)
- Widely accepted in statistical literature
- Good computational performance

**Alternatives Considered**:
- Normal approximation: Less robust for small samples
- Exact binomial: Too conservative, computationally expensive
- Clopper-Pearson: Too conservative for practical use

### Statistical vs. Practical Significance

**Decision**: Provide both statistical validation and practical tolerance checking.

**Rationale**:
- Statistical significance doesn't always mean practical importance
- Allow test authors to specify practical tolerance ranges
- Support both strict statistical testing and practical validation
- Maintain flexibility for different testing scenarios

### Bootstrap Implementation Strategy

**Decision**: Implement lightweight bootstrap with adaptive sample sizing.

**Rationale**:
- Non-parametric method works with any statistic
- Adaptive sizing balances accuracy with performance
- Memory-efficient streaming implementation
- Fallback to parametric methods when bootstrap fails

### Integration with Existing Framework

**Decision**: Extend existing testing framework rather than replace.

**Rationale**:
- Preserve investment in current performance testing infrastructure
- Maintain backward compatibility during migration
- Leverage existing environment detection and threshold management
- Minimize disruption to development workflow

## Risks and Mitigation

### Technical Risks

**Risk**: Statistical calculations impact performance
**Mitigation**:
- Aggressive optimization and caching
- Benchmark-driven performance tuning
- Fallback to simpler methods under load

**Risk**: CI environment variance affects statistical tests
**Mitigation**:
- Environment-specific confidence adjustments
- Robust statistical methods (Wilson score)
- Multiple validation approaches

**Risk**: Complex API adoption challenges
**Mitigation**:
- Clear documentation and examples
- Gradual migration strategy
- Training materials for test authors

### Project Risks

**Risk**: Migration timeline extends beyond 3 weeks
**Mitigation**:
- Prioritized implementation order
- Minimal viable product approach
- Parallel development of documentation

**Risk**: Statistical framework adds complexity
**Mitigation**:
- Simple default configurations
- Clear error messages
- Comprehensive testing of the framework itself

## Future Enhancements

### Advanced Statistical Methods
- Bayesian confidence intervals
- Sequential testing for early stopping
- Machine learning-based anomaly detection
- Advanced multiple testing correction

### Enhanced Integration
- Real-time statistical monitoring
- Statistical test result visualization
- Integration with external statistical tools
- Automated statistical report generation

### Performance Optimization
- GPU acceleration for large-scale testing
- Distributed statistical computation
- Advanced caching strategies
- Just-in-time compilation for hot paths

## Conclusion

The Statistical Testing Framework provides a mathematically sound foundation for validating kinda-lang's probabilistic behavior. By replacing hardcoded thresholds with confidence interval-based assertions, we achieve scientific rigor while maintaining practical usability and CI reliability.

The architecture balances statistical correctness with performance requirements, providing a robust foundation for current testing needs and future statistical enhancements. The framework design ensures smooth migration from existing hardcoded patterns while enabling advanced statistical validation capabilities.

---

**Next Steps**: Proceed to Implementation Specification (Week 1-2) for detailed technical specifications and coding requirements.